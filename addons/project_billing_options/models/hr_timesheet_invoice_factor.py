# coding: utf-8
# Part of Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models, fields, api
from flectra.osv import expression
from flectra.tools import float_round
from dateutil.relativedelta import relativedelta

DEFAULT_MONTH_RANGE = 3


class HrTimesheetInvoiceFactor(models.Model):
    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"

    name = fields.Char('Name', translate=True)
    factor = fields.Float(string='Invoicable Factor',
                          required=True, help="Invoicable in percentage")


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = "Account Analytic Line"

    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor',
                                    string="Invoicable(%)")
    calculated_hours_invoice = fields.Float(string="Calculated Hours",
                                            compute_sudo=True, store=True,
                                            compute="_compute_calculated_hours")

    @api.depends('unit_amount', 'invoicable_id')
    def _compute_calculated_hours(self):
        for rec in self:
            if rec.invoicable_id.factor != 0.0:
                calculated_hours = (rec.unit_amount * rec.invoicable_id.factor / 100)
                rec.update({
                    'calculated_hours_invoice': calculated_hours,
                })
            else:
                for a in rec:
                    a.calculated_hours_invoice = a.unit_amount


class Project(models.Model):
    _inherit = 'project.project'
    _description = "Project Project"

    def _plan_prepare_values(self):
        currency = self.env.company.currency_id
        uom_hour = self.env.ref('uom.product_uom_hour')
        company_uom = self.env.company.timesheet_encode_uom_id
        is_uom_day = company_uom == self.env.ref('uom.product_uom_day')
        hour_rounding = uom_hour.rounding
        billable_types = ['non_billable', 'non_billable_project',
                          'billable_time', 'non_billable_timesheet',
                          'billable_fixed']

        values = {
            'projects': self,
            'currency': currency,
            'timesheet_domain': [('project_id', 'in', self.ids)],
            'profitability_domain': [('project_id', 'in', self.ids)],
            'stat_buttons': self._plan_get_stat_button(),
            'is_uom_day': is_uom_day,
        }

        #
        # Hours, Rates and Profitability
        #
        dashboard_values = {
            'time': dict.fromkeys(billable_types + ['total'], 0.0),
            'rates': dict.fromkeys(billable_types + ['total'], 0.0),
            'profit': {
                'invoiced': 0.0,
                'to_invoice': 0.0,
                'cost': 0.0,
                'total': 0.0,
            }
        }
        canceled_hours_domain = [('project_id', 'in', self.ids),
                                 ('timesheet_invoice_type', '!=', False),
                                 ('so_line.state', '=', 'cancel')]
        total_canceled_hours = sum(
            self.env['account.analytic.line'].search(
                canceled_hours_domain).mapped('calculated_hours_invoice'))
        canceled_hours = float_round(total_canceled_hours,
                                     precision_rounding=hour_rounding)
        if is_uom_day:
            # convert time from hours to days
            canceled_hours = round(uom_hour._compute_quantity(
                canceled_hours, company_uom, raise_if_failure=False), 2)
        dashboard_values['time']['canceled'] = canceled_hours
        dashboard_values['time']['total'] += canceled_hours

        dashboard_domain = [('project_id', 'in', self.ids),
                            ('timesheet_invoice_type', '!=', False),
                            ('calculated_hours_invoice', '!=', False),
                            '|', ('so_line', '=', False),
                            ('so_line.state', '!=', 'cancel')]  # force billable type
        dashboard_data = self.env['account.analytic.line'].read_group(
            dashboard_domain,
            ['calculated_hours_invoice', 'timesheet_invoice_type'],
            ['timesheet_invoice_type'])
        dashboard_total_hours = sum(
            [data['calculated_hours_invoice']
             for data in dashboard_data]) + total_canceled_hours
        for data in dashboard_data:
            billable_type = data['timesheet_invoice_type']
            amount = float_round(data.get('calculated_hours_invoice'),
                                 precision_rounding=hour_rounding)
            if is_uom_day:
                # convert time from hours to days
                amount = round(
                    uom_hour._compute_quantity(
                        amount, company_uom, raise_if_failure=False), 2)
            dashboard_values['time'][billable_type] = amount
            dashboard_values['time']['total'] += amount
            # rates
            rate = round(
                data.get('calculated_hours_invoice') / dashboard_total_hours * 100,
                2) if dashboard_total_hours else 0.0
            dashboard_values['rates'][billable_type] = rate
            dashboard_values['rates']['total'] += rate
        dashboard_values['time']['total'] = round(dashboard_values['time']['total'], 2)

        # rates from non-invoiced timesheets that are linked to canceled so
        dashboard_values['rates']['canceled'] = float_round(
            100 * total_canceled_hours / (dashboard_total_hours or 1),
            precision_rounding=hour_rounding)

        other_revenues = self.env['account.analytic.line'].read_group([
            ('account_id', 'in', self.analytic_account_id.ids),
            ('amount', '>=', 0),
            ('project_id', '=', False)], ['amount'], [])[0].get('amount', 0)

        # profitability, using profitability SQL report
        profit = dict.fromkeys(
            ['invoiced', 'to_invoice', 'cost', 'expense_cost',
             'expense_amount_untaxed_invoiced', 'total'], 0.0)
        profitability_raw_data = self.env['project.profitability.report'].read_group(
            [('project_id', 'in', self.ids)],
            ['project_id',
             'amount_untaxed_to_invoice',
             'amount_untaxed_invoiced',
             'timesheet_cost', 'expense_cost',
             'expense_amount_untaxed_invoiced'],
            ['project_id'])
        for data in profitability_raw_data:
            profit['invoiced'] += data.get('amount_untaxed_invoiced', 0.0)
            profit['to_invoice'] += data.get('amount_untaxed_to_invoice', 0.0)
            profit['cost'] += data.get('timesheet_cost', 0.0)
            profit['expense_cost'] += data.get('expense_cost', 0.0)
            profit['expense_amount_untaxed_invoiced'] += data.get(
                'expense_amount_untaxed_invoiced', 0.0)
        profit['other_revenues'] = other_revenues - data.get(
            'amount_untaxed_invoiced', 0.0) if other_revenues else 0.0
        profit['total'] = sum([profit[item] for item in profit.keys()])
        dashboard_values['profit'] = profit

        values['dashboard'] = dashboard_values

        #
        # Time Repartition (per employee per billable types)
        #
        employee_ids = self._plan_get_employee_ids()
        employee_ids = list(set(employee_ids))
        # Retrieve the employees for which the current user can see theirs timesheets
        employee_domain = expression.AND(
            [[('company_id', 'in', self.env.companies.ids)],
             self.env['account.analytic.line']._domain_employee_id()])
        employees = self.env['hr.employee'].sudo().browse(
            employee_ids).filtered_domain(employee_domain)
        repartition_domain = [('project_id', 'in', self.ids),
                              ('employee_id', '!=', False),
                              ('timesheet_invoice_type', '!=', False)]
        # force billable type
        # repartition data, without timesheet on cancelled so
        repartition_data = self.env['account.analytic.line'].read_group(
            repartition_domain + ['|', ('so_line', '=', False),
                                  ('so_line.state', '!=', 'cancel')],
            ['employee_id', 'timesheet_invoice_type', 'calculated_hours_invoice'],
            ['employee_id', 'timesheet_invoice_type'],
            lazy=False)
        # read timesheet on cancelled so
        cancelled_so_timesheet = self.env['account.analytic.line'].read_group(
            repartition_domain + [('so_line.state', '=', 'cancel')],
            ['employee_id', 'calculated_hours_invoice'],
            ['employee_id'],
            lazy=False)
        repartition_data += [{**canceled, 'timesheet_invoice_type': 'canceled'}
                             for canceled in cancelled_so_timesheet]

        # set repartition per type per employee
        repartition_employee = {}
        for employee in employees:
            repartition_employee[employee.id] = dict(
                employee_id=employee.id,
                employee_name=employee.name,
                non_billable_project=0.0,
                non_billable=0.0,
                billable_time=0.0,
                non_billable_timesheet=0.0,
                billable_fixed=0.0,
                canceled=0.0,
                total=0.0,
            )
        for data in repartition_data:
            employee_id = data['employee_id'][0]
            repartition_employee.setdefault(employee_id, dict(
                employee_id=data['employee_id'][0],
                employee_name=data['employee_id'][1],
                non_billable_project=0.0,
                non_billable=0.0,
                billable_time=0.0,
                non_billable_timesheet=0.0,
                billable_fixed=0.0,
                canceled=0.0,
                total=0.0,
            ))[data['timesheet_invoice_type']] = float_round(
                data.get('calculated_hours_invoice', 0.0),
                precision_rounding=hour_rounding)
            repartition_employee[employee_id]['__domain_' + data[
                'timesheet_invoice_type']] = data['__domain']
        # compute total
        for employee_id, vals in repartition_employee.items():
            repartition_employee[employee_id]['total'] = sum(
                [vals[inv_type] for inv_type in [*billable_types, 'canceled']])

            if is_uom_day:
                # convert all times from hours to days
                for time_type in ['non_billable_project',
                                  'non_billable', 'billable_time',
                                  'non_billable_timesheet',
                                  'billable_fixed',
                                  'canceled',
                                  'total']:

                    if repartition_employee[employee_id][time_type]:
                        repartition_employee[employee_id][time_type] = round(
                            uom_hour._compute_quantity(
                                repartition_employee[employee_id][time_type],
                                company_uom,
                                raise_if_failure=False), 2)
        hours_per_employee = [repartition_employee[employee_id]['total']
                              for employee_id in repartition_employee]
        values['repartition_employee_max'] = (max(hours_per_employee)
                                              if hours_per_employee else 1) or 1
        values['repartition_employee'] = repartition_employee

        #
        # Table grouped by SO / SOL / Employees
        #
        timesheet_forecast_table_rows = self._table_get_line_values(employees)
        if timesheet_forecast_table_rows:
            values['timesheet_forecast_table'] = timesheet_forecast_table_rows
        return values

    def _table_rows_sql_query(self):
        initial_date = fields.Date.from_string(fields.Date.today())
        ts_months = sorted(
            [fields.Date.to_string(initial_date - relativedelta(months=i, day=1))
             for i in range(0, DEFAULT_MONTH_RANGE)])  # M1, M2, M3
        # build query
        query = """
            SELECT
                'timesheet' AS type,
                date_trunc('month', date)::date AS month_date,
                E.id AS employee_id,
                S.order_id AS sale_order_id,
                A.so_line AS sale_line_id,
                SUM(A.calculated_hours_invoice) AS number_hours
            FROM account_analytic_line A
                JOIN hr_employee E ON E.id = A.employee_id
                LEFT JOIN sale_order_line S ON S.id = A.so_line
            WHERE A.project_id IS NOT NULL
                AND A.project_id IN %s
                AND A.date < %s
            GROUP BY date_trunc('month', date)::date, S.order_id, A.so_line, E.id
        """

        last_ts_month = fields.Date.to_string(
            fields.Date.from_string(ts_months[-1]) + relativedelta(months=1))
        query_params = (tuple(self.ids), last_ts_month)
        return query, query_params
