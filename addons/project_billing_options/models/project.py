# coding: utf-8
# Part of Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models, fields, api, _
from flectra.osv import expression
from flectra.addons.web.controllers.main import clean_action
import json
import itertools


class Task(models.Model):
    _inherit = 'project.task'
    _description = "Project Task"

    timesheet_invoice_type = fields.Selection([
        ('billable_time', 'Billed on Timesheets'),
        ('billable_fixed', 'Billed at a Fixed price'),
        ('non_billable', 'Non Billable Tasks'),
        ('non_billable_timesheet', 'Non Billable Timesheet'),
        ('non_billable_project', 'No task found')],
        string="Billable Type")
    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor',
                                    string="Invoicable(%)")
    total_computed_hours = fields.Float(compute="_compute_total_calculated_hours",
                                        help="Time spent on this task,"
                                             " excluding its sub-tasks.")

    @api.onchange('project_id')
    def _compute_timesheet_invoice_type(self):

        values = {
            'timesheet_invoice_type': self.project_id.timesheet_invoice_type,
            'invoicable_id': self.project_id.invoicable_id,
        }
        self.update(values)


    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_calculated_hours(self):
        for task in self:
            task.total_computed_hours = round(sum(
                task.timesheet_ids.mapped('calculated_hours_invoice')), 2)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = "Account Analytic Line"

    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor', string="Invoicable",
                                    readonly=False)
    timesheet_invoice_type = fields.Selection([
        ('billable_time', 'Billed on Timesheets'),
        ('billable_fixed', 'Billed at a Fixed price'),
        ('non_billable', 'Non Billable Tasks'),
        ('non_billable_timesheet', 'Non Billable Timesheet'),
        ('non_billable_project', 'No task found')],
        string="Billable Type", compute=False)
    task_id = fields.Many2one(
        'project.task', 'Task', compute='_compute_task_id',
        store=True, readonly=False, index=True,
        domain="[('company_id', '=', company_id),"
               " ('project_id.allow_timesheets', '=', True),"
               " ('project_id', '=?', project_id)]")

    @api.onchange('task_id')
    def _onchange_timesheet_ids(self):
        values = {
            'timesheet_invoice_type': self.task_id.timesheet_invoice_type,
            'invoicable_id': self.task_id.invoicable_id,
        }
        self.update(values)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order'
    _description = 'Sales Order'

    @api.depends('timesheet_ids', 'company_id.timesheet_encode_uom_id')
    def _compute_timesheet_total_duration(self):
        for sale_order in self:
            timesheets = sale_order.timesheet_ids if self.user_has_groups(
                'hr_timesheet.group_hr_timesheet_approver') \
                else sale_order.timesheet_ids.filtered(
                lambda t: t.user_id.id == self.env.uid)
            total_time = 0.0
            for timesheet in timesheets.filtered(lambda t: not t.non_allow_billable):
                # Timesheets may be stored in a different unit of measure,
                # so first we convert all of them to the reference unit
                total_time += timesheet.calculated_hours_invoice * timesheet. \
                    product_uom_id.factor_inv
            # Now convert to the proper unit of measure
            total_time *= sale_order.timesheet_encode_uom_id.factor
            sale_order.timesheet_total_duration = total_time


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        """ Compute and write the delivered quantity of current SO lines,
         based on their related
            analytic lines.
            :param additional_domain: domain to restrict AAL to include in computation
             (required since timesheet is an AAL with a project ...)
        """
        result = {}

        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group analytic lines by product uom and so line
        domain = expression.AND([[('so_line', 'in', self.ids)], additional_domain])
        data = self.env['account.analytic.line'].read_group(
            domain,
            ['so_line', 'calculated_hours_invoice', 'product_uom_id'],
            ['product_uom_id', 'so_line'], lazy=False
        )

        # convert uom and sum all unit_amount of analytic
        # lines to get the delivered qty of SO lines
        # browse so lines and product uoms here to make them share the same prefetch
        lines = self.browse([item['so_line'][0] for item in data])
        lines_map = {line.id: line for line in lines}
        product_uom_ids = [item['product_uom_id'][0]
                           for item in data if item['product_uom_id']]
        product_uom_map = {uom.id: uom
                           for uom in self.env['uom.uom'].browse(product_uom_ids)}

        for item in data:
            if not item['product_uom_id']:
                continue
            so_line_id = item['so_line'][0]
            so_line = lines_map[so_line_id]
            result.setdefault(so_line_id, 0.0)
            uom = product_uom_map.get(item['product_uom_id'][0])

            if so_line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(item['calculated_hours_invoice'],
                                            so_line.product_uom)
                qty = (float(qty))

            else:
                qty = item['calculated_hours_invoice']
            result[so_line_id] += qty

        return result


class Project(models.Model):
    _inherit = 'project.project'
    _description = "Project of Project"

    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor',
                                    string="Invoicable(%)")
    timesheet_invoice_type = fields.Selection([
        ('billable_time', 'Billed on Timesheets'),
        ('billable_fixed', 'Billed at a Fixed price'),
        ('non_billable', 'Non Billable Tasks'),
        ('non_billable_timesheet', 'Non Billable Timesheet'),
        ('non_billable_project', 'No task found')],
        string="Billable Type")
    total_calculated_timesheet_time = fields.Integer(
        compute='_compute_calculated_timesheet_time',
        help="Total number of time (in the proper UoM) recorded in the project,"
             " rounded to the unit.")

    @api.depends('timesheet_ids')
    def _compute_calculated_timesheet_time(self):
        total_time = 0.0

        for project in self:
            # total_time = 0.0
            for timesheet in project.timesheet_ids:
                # Timesheets may be stored in a different unit of measure, so first
                # we convert all of them to the reference unit
                total_time += timesheet.calculated_hours_invoice * timesheet. \
                    product_uom_id.factor_inv
            # Now convert to the proper unit of measure set in the settings
            total_time *= project.timesheet_encode_uom_id.factor
            project.total_calculated_timesheet_time = int(round(total_time))

    def _plan_get_stat_button(self):
        stat_buttons = []
        num_projects = len(self)
        if num_projects == 1:
            action_data = _to_action_data(
                'project.project', res_id=self.id,
                views=[[self.env.ref('project.edit_project').id, 'form']])
        else:
            action_data = _to_action_data(
                action=self.env.ref('project.open_view_project_all_config').sudo(),
                domain=[('id', 'in', self.ids)])

        stat_buttons.append({
            'name': _('Project') if num_projects == 1 else _('Projects'),
            'count': num_projects,
            'icon': 'fa fa-puzzle-piece',
            'action': action_data
        })

        # if only one project, add it in the context as default value
        tasks_domain = [('project_id', 'in', self.ids)]
        tasks_context = self.env.context.copy()
        tasks_context.pop('search_default_name', False)
        late_tasks_domain = [('project_id', 'in', self.ids),
                             ('date_deadline', '<',
                              fields.Date.to_string(fields.Date.today())),
                             ('date_end', '=', False)]
        overtime_tasks_domain = [('project_id', 'in', self.ids),
                                 ('overtime', '>', 0),
                                 ('planned_hours', '>', 0)]

        if len(self) == 1:
            tasks_context = {**tasks_context, 'default_project_id': self.id}
        elif len(self):
            task_projects_ids = self.env['project.task'].read_group(
                [('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
            task_projects_ids = [p['project_id'][0] for p in task_projects_ids]
            if len(task_projects_ids) == 1:
                tasks_context = {**tasks_context,
                                 'default_project_id': task_projects_ids[0]}

        stat_buttons.append({
            'name': _('Tasks'),
            'count': sum(self.mapped('task_count')),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task').sudo(),
                domain=tasks_domain,
                context=tasks_context
            )
        })
        stat_buttons.append({
            'name': [_("Tasks"), _("Late")],
            'count': self.env['project.task'].search_count(late_tasks_domain),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task').sudo(),
                domain=late_tasks_domain,
                context=tasks_context,
            ),
        })
        stat_buttons.append({
            'name': [_("Tasks"), _("in Overtime")],
            'count': self.env['project.task'].search_count(overtime_tasks_domain),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task').sudo(),
                domain=overtime_tasks_domain,
                context=tasks_context,
            ),
        })

        if self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            # read all the sale orders linked to the projects' tasks
            task_so_ids = self.env['project.task'].search_read([
                ('project_id', 'in', self.ids), ('sale_order_id', '!=', False)
            ], ['sale_order_id'])
            task_so_ids = [o['sale_order_id'][0] for o in task_so_ids]

            sale_orders = self.mapped(
                'sale_line_id.order_id') | self.env['sale.order'].browse(task_so_ids)
            if sale_orders:
                stat_buttons.append({
                    'name': _('Sales Orders'),
                    'count': len(sale_orders),
                    'icon': 'fa fa-dollar',
                    'action': _to_action_data(
                        action=self.env.ref('sale.action_orders').sudo(),
                        domain=[('id', 'in', sale_orders.ids)],
                        context={'create': False, 'edit': False, 'delete': False}
                    )
                })

                invoice_ids = self.env['sale.order'].search_read(
                    [('id', 'in', sale_orders.ids)], ['invoice_ids'])
                invoice_ids = list(
                    itertools.chain(*[i['invoice_ids'] for i in invoice_ids]))
                invoice_ids = self.env['account.move'].search_read(
                    [('id', 'in', invoice_ids),
                     ('move_type', '=', 'out_invoice')],
                    ['id'])
                invoice_ids = list(map(lambda x: x['id'], invoice_ids))

                if invoice_ids:
                    stat_buttons.append({
                        'name': _('Invoices'),
                        'count': len(invoice_ids),
                        'icon': 'fa fa-pencil-square-o',
                        'action': _to_action_data(
                            action=self.env.ref(
                                'account.action_move_out_invoice_type').sudo(),
                            domain=[('id', 'in', invoice_ids),
                                    ('move_type', '=', 'out_invoice')],
                            context={'create': False, 'delete': False}
                        )
                    })

        ts_tree = self.env.ref('hr_timesheet.hr_timesheet_line_tree')
        ts_form = self.env.ref('hr_timesheet.hr_timesheet_line_form')
        if self.env.company.timesheet_encode_uom_id == self.env.ref(
                'uom.product_uom_day'):
            timesheet_label = [_('Days'), _('Recorded')]
        else:
            timesheet_label = [_('Hours'), _('Recorded')]

        stat_buttons.append({
            'name': timesheet_label,
            'count': sum(self.mapped('total_timesheet_time')),
            'icon': 'fa fa-calendar',
            'action': _to_action_data(
                'account.analytic.line',
                domain=[('project_id', 'in', self.ids)],
                views=[(ts_tree.id, 'list'), (ts_form.id, 'form')],
            )
        })

        if self.env.company.timesheet_encode_uom_id == self.env.ref(
                'uom.product_uom_day'):
            timesheet_labels = [_('Calculated'), _('Days')]
        else:
            timesheet_labels = [_('Calculated'), _('Hours')]

        stat_buttons.append({
            'name': timesheet_labels,
            'count': sum(self.mapped('total_calculated_timesheet_time')),
            'icon': 'fa fa-calendar',
            'action': _to_action_data(
                'account.analytic.line',
                domain=[('project_id', 'in', self.ids)],
                views=[(ts_tree.id, 'list'), (ts_form.id, 'form')],
            )
        })

        return stat_buttons


def _to_action_data(model=None,
                    *, action=None, views=None, res_id=None, domain=None, context=None):
    # pass in either action or (model, views)
    if action:
        assert model is None and views is None
        act = clean_action(action.read()[0], env=action.env)
        model = act['res_model']
        views = act['views']
    # FIXME: search-view-id, possibly help?
    descr = {
        'data-model': model,
        'data-views': json.dumps(views),
    }
    if context is not None:  # otherwise copy action's?
        descr['data-context'] = json.dumps(context)
    if res_id:
        descr['data-res-id'] = res_id
    elif domain:
        descr['data-domain'] = json.dumps(domain)
    return descr
