#-*-coding:utf-8-*-
importbabel.dates
fromdateutil.relativedeltaimportrelativedelta
importitertools
importjson

fromflectraimportfields,_,models
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_round
fromflectra.tools.miscimportget_lang

fromflectra.addons.web.controllers.mainimportclean_action
fromdatetimeimportdate

DEFAULT_MONTH_RANGE=3


classProject(models.Model):
    _inherit='project.project'


    def_qweb_prepare_qcontext(self,view_id,domain):
        values=super()._qweb_prepare_qcontext(view_id,domain)

        projects=self.search(domain)
        values.update(projects._plan_prepare_values())
        values['actions']=projects._plan_prepare_actions(values)

        returnvalues

    def_plan_get_employee_ids(self):
        aal_employee_ids=self.env['account.analytic.line'].read_group([('project_id','in',self.ids),('employee_id','!=',False)],['employee_id'],['employee_id'])
        employee_ids=list(map(lambdax:x['employee_id'][0],aal_employee_ids))
        returnemployee_ids

    def_plan_prepare_values(self):
        currency=self.env.company.currency_id
        uom_hour=self.env.ref('uom.product_uom_hour')
        company_uom=self.env.company.timesheet_encode_uom_id
        is_uom_day=company_uom==self.env.ref('uom.product_uom_day')
        hour_rounding=uom_hour.rounding
        billable_types=['non_billable','non_billable_project','billable_time','non_billable_timesheet','billable_fixed']

        values={
            'projects':self,
            'currency':currency,
            'timesheet_domain':[('project_id','in',self.ids)],
            'profitability_domain':[('project_id','in',self.ids)],
            'stat_buttons':self._plan_get_stat_button(),
            'is_uom_day':is_uom_day,
        }

        #
        #Hours,RatesandProfitability
        #
        dashboard_values={
            'time':dict.fromkeys(billable_types+['total'],0.0),
            'rates':dict.fromkeys(billable_types+['total'],0.0),
            'profit':{
                'invoiced':0.0,
                'to_invoice':0.0,
                'cost':0.0,
                'total':0.0,
            }
        }

        #hoursfromnon-invoicedtimesheetsthatarelinkedtocanceledso
        canceled_hours_domain=[('project_id','in',self.ids),('timesheet_invoice_type','!=',False),('so_line.state','=','cancel')]
        total_canceled_hours=sum(self.env['account.analytic.line'].search(canceled_hours_domain).mapped('unit_amount'))
        canceled_hours=float_round(total_canceled_hours,precision_rounding=hour_rounding)
        ifis_uom_day:
            #converttimefromhourstodays
            canceled_hours=round(uom_hour._compute_quantity(canceled_hours,company_uom,raise_if_failure=False),2)
        dashboard_values['time']['canceled']=canceled_hours
        dashboard_values['time']['total']+=canceled_hours

        #hours(fromtimesheet)andrates(bybillabletype)
        dashboard_domain=[('project_id','in',self.ids),('timesheet_invoice_type','!=',False),'|',('so_line','=',False),('so_line.state','!=','cancel')] #forcebillabletype
        dashboard_data=self.env['account.analytic.line'].read_group(dashboard_domain,['unit_amount','timesheet_invoice_type'],['timesheet_invoice_type'])
        dashboard_total_hours=sum([data['unit_amount']fordataindashboard_data])+total_canceled_hours
        fordataindashboard_data:
            billable_type=data['timesheet_invoice_type']
            amount=float_round(data.get('unit_amount'),precision_rounding=hour_rounding)
            ifis_uom_day:
                #converttimefromhourstodays
                amount=round(uom_hour._compute_quantity(amount,company_uom,raise_if_failure=False),2)
            dashboard_values['time'][billable_type]=amount
            dashboard_values['time']['total']+=amount
            #rates
            rate=round(data.get('unit_amount')/dashboard_total_hours*100,2)ifdashboard_total_hourselse0.0
            dashboard_values['rates'][billable_type]=rate
            dashboard_values['rates']['total']+=rate
        dashboard_values['time']['total']=round(dashboard_values['time']['total'],2)

        #ratesfromnon-invoicedtimesheetsthatarelinkedtocanceledso
        dashboard_values['rates']['canceled']=float_round(100*total_canceled_hours/(dashboard_total_hoursor1),precision_rounding=hour_rounding)
        
        #profitability,usingprofitabilitySQLreport
        field_map={
            'amount_untaxed_invoiced':'invoiced',
            'amount_untaxed_to_invoice':'to_invoice',
            'timesheet_cost':'cost',
            'expense_cost':'expense_cost',
            'expense_amount_untaxed_invoiced':'expense_amount_untaxed_invoiced',
            'expense_amount_untaxed_to_invoice':'expense_amount_untaxed_to_invoice',
            'other_revenues':'other_revenues'
        }
        profit=dict.fromkeys(list(field_map.values())+['other_revenues','total'],0.0)
        profitability_raw_data=self.env['project.profitability.report'].read_group([('project_id','in',self.ids)],['project_id']+list(field_map),['project_id'])  
        fordatainprofitability_raw_data:
            company_id=self.env['project.project'].browse(data.get('project_id')[0]).company_id
            from_currency=company_id.currency_id
            forfieldinfield_map:
                value=data.get(field,0.0)
                iffrom_currency!=currency:
                    value=from_currency._convert(value,currency,company_id,date.today())
                profit[field_map[field]]+=value              
        profit['total']=sum([profit[item]foriteminprofit.keys()])
        dashboard_values['profit']=profit

        values['dashboard']=dashboard_values

        #
        #TimeRepartition(peremployeeperbillabletypes)
        #
        employee_ids=self._plan_get_employee_ids()
        employee_ids=list(set(employee_ids))
        #Retrievetheemployeesforwhichthecurrentusercanseetheirstimesheets
        employee_domain=expression.AND([[('company_id','in',self.env.companies.ids)],self.env['account.analytic.line']._domain_employee_id()])
        employees=self.env['hr.employee'].sudo().browse(employee_ids).filtered_domain(employee_domain)
        repartition_domain=[('project_id','in',self.ids),('employee_id','!=',False),('timesheet_invoice_type','!=',False)] #forcebillabletype
        #repartitiondata,withouttimesheetoncancelledso
        repartition_data=self.env['account.analytic.line'].read_group(repartition_domain+['|',('so_line','=',False),('so_line.state','!=','cancel')],['employee_id','timesheet_invoice_type','unit_amount'],['employee_id','timesheet_invoice_type'],lazy=False)
        #readtimesheetoncancelledso
        cancelled_so_timesheet=self.env['account.analytic.line'].read_group(repartition_domain+[('so_line.state','=','cancel')],['employee_id','unit_amount'],['employee_id'],lazy=False)
        repartition_data+=[{**canceled,'timesheet_invoice_type':'canceled'}forcanceledincancelled_so_timesheet]

        #setrepartitionpertypeperemployee
        repartition_employee={}
        foremployeeinemployees:
            repartition_employee[employee.id]=dict(
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
        fordatainrepartition_data:
            employee_id=data['employee_id'][0]
            repartition_employee.setdefault(employee_id,dict(
                employee_id=data['employee_id'][0],
                employee_name=data['employee_id'][1],
                non_billable_project=0.0,
                non_billable=0.0,
                billable_time=0.0,
                non_billable_timesheet=0.0,
                billable_fixed=0.0,
                canceled=0.0,
                total=0.0,
            ))[data['timesheet_invoice_type']]=float_round(data.get('unit_amount',0.0),precision_rounding=hour_rounding)
            repartition_employee[employee_id]['__domain_'+data['timesheet_invoice_type']]=data['__domain']
        #computetotal
        foremployee_id,valsinrepartition_employee.items():
            repartition_employee[employee_id]['total']=sum([vals[inv_type]forinv_typein[*billable_types,'canceled']])
            ifis_uom_day:
                #convertalltimesfromhourstodays
                fortime_typein['non_billable_project','non_billable','billable_time','non_billable_timesheet','billable_fixed','canceled','total']:
                    ifrepartition_employee[employee_id][time_type]:
                        repartition_employee[employee_id][time_type]=round(uom_hour._compute_quantity(repartition_employee[employee_id][time_type],company_uom,raise_if_failure=False),2)
        hours_per_employee=[repartition_employee[employee_id]['total']foremployee_idinrepartition_employee]
        values['repartition_employee_max']=(max(hours_per_employee)ifhours_per_employeeelse1)or1
        values['repartition_employee']=repartition_employee

        #
        #TablegroupedbySO/SOL/Employees
        #
        timesheet_forecast_table_rows=self._table_get_line_values(employees)
        iftimesheet_forecast_table_rows:
            values['timesheet_forecast_table']=timesheet_forecast_table_rows
        returnvalues

    def_table_get_line_values(self,employees=None):
        """returntheheaderandtherowsinformationsofthetable"""
        ifnotself:
            returnFalse

        uom_hour=self.env.ref('uom.product_uom_hour')
        company_uom=self.env.company.timesheet_encode_uom_id
        is_uom_day=company_uomandcompany_uom==self.env.ref('uom.product_uom_day')

        #buildSQLqueryandfetchrawdata
        query,query_params=self._table_rows_sql_query()
        self.env.cr.execute(query,query_params)
        raw_data=self.env.cr.dictfetchall()
        rows_employee=self._table_rows_get_employee_lines(raw_data)
        default_row_vals=self._table_row_default()

        empty_line_ids,empty_order_ids=self._table_get_empty_so_lines()

        #extractrowlabels
        sale_line_ids=set()
        sale_order_ids=set()
        forkey_tuple,rowinrows_employee.items():
            ifrow[0]['sale_line_id']:
                sale_line_ids.add(row[0]['sale_line_id'])
            ifrow[0]['sale_order_id']:
                sale_order_ids.add(row[0]['sale_order_id'])

        sale_orders=self.env['sale.order'].sudo().browse(sale_order_ids|empty_order_ids)
        sale_order_lines=self.env['sale.order.line'].sudo().browse(sale_line_ids|empty_line_ids)
        map_so_names={so.id:so.nameforsoinsale_orders}
        map_so_cancel={so.id:so.state=='cancel'forsoinsale_orders}
        map_sol={sol.id:solforsolinsale_order_lines}
        map_sol_names={sol.id:sol.name.split('\n')[0]ifsol.nameelse_('NoSalesOrderLine')forsolinsale_order_lines}
        map_sol_so={sol.id:sol.order_id.idforsolinsale_order_lines}

        rows_sale_line={} #(so,sol)->[INFO,before,M1,M2,M3,Done,M3,M4,M5,After,Forecasted]
        forsale_line_idinempty_line_ids: #addserviceSOlinehavingnotimesheet
            sale_line_row_key=(map_sol_so.get(sale_line_id),sale_line_id)
            sale_line=map_sol.get(sale_line_id)
            is_milestone=sale_line.product_id.invoice_policy=='delivery'andsale_line.product_id.service_type=='manual'ifsale_lineelseFalse
            rows_sale_line[sale_line_row_key]=[{'label':map_sol_names.get(sale_line_id,_('NoSalesOrderLine')),'res_id':sale_line_id,'res_model':'sale.order.line','type':'sale_order_line','is_milestone':is_milestone}]+default_row_vals[:]
            ifnotis_milestone:
                rows_sale_line[sale_line_row_key][-2]=sale_line.product_uom._compute_quantity(sale_line.product_uom_qty,uom_hour,raise_if_failure=False)ifsale_lineelse0.0

        rows_sale_line_all_data={}
        ifnotemployees:
            employees=self.env['hr.employee'].sudo().search(self.env['account.analytic.line']._domain_employee_id())
        forrow_key,row_employeeinrows_employee.items():
            sale_order_id,sale_line_id,employee_id=row_key
            #salelinerow
            sale_line_row_key=(sale_order_id,sale_line_id)
            ifsale_line_row_keynotinrows_sale_line:
                sale_line=map_sol.get(sale_line_id,self.env['sale.order.line'])
                is_milestone=sale_line.product_id.invoice_policy=='delivery'andsale_line.product_id.service_type=='manual'ifsale_lineelseFalse
                rows_sale_line[sale_line_row_key]=[{'label':map_sol_names.get(sale_line.id)ifsale_lineelse_('NoSalesOrderLine'),'res_id':sale_line_id,'res_model':'sale.order.line','type':'sale_order_line','is_milestone':is_milestone}]+default_row_vals[:] #INFO,before,M1,M2,M3,Done,M3,M4,M5,After,Forecasted
                ifnotis_milestone:
                    rows_sale_line[sale_line_row_key][-2]=sale_line.product_uom._compute_quantity(sale_line.product_uom_qty,uom_hour,raise_if_failure=False)ifsale_lineelse0.0

            ifsale_line_row_keynotinrows_sale_line_all_data:
                rows_sale_line_all_data[sale_line_row_key]=[0]*len(row_employee)
            forindexinrange(1,len(row_employee)):
                ifemployee_idinemployees.ids:
                    rows_sale_line[sale_line_row_key][index]+=row_employee[index]
                rows_sale_line_all_data[sale_line_row_key][index]+=row_employee[index]
            ifnotrows_sale_line[sale_line_row_key][0].get('is_milestone'):
                rows_sale_line[sale_line_row_key][-1]=rows_sale_line[sale_line_row_key][-2]-rows_sale_line_all_data[sale_line_row_key][5]
            else:
                rows_sale_line[sale_line_row_key][-1]=0

        rows_sale_order={} #so->[INFO,before,M1,M2,M3,Done,M3,M4,M5,After,Forecasted]
        forrow_key,row_sale_lineinrows_sale_line.items():
            sale_order_id=row_key[0]
            #saleorderrow
            ifsale_order_idnotinrows_sale_order:
                rows_sale_order[sale_order_id]=[{'label':map_so_names.get(sale_order_id,_('NoSalesOrder')),'canceled':map_so_cancel.get(sale_order_id,False),'res_id':sale_order_id,'res_model':'sale.order','type':'sale_order'}]+default_row_vals[:] #INFO,before,M1,M2,M3,Done,M3,M4,M5,After,Forecasted

            forindexinrange(1,len(row_sale_line)):
                rows_sale_order[sale_order_id][index]+=row_sale_line[index]

        #grouprowsSO,SOLandtheirrelatedemployeerows.
        timesheet_forecast_table_rows=[]
        forsale_order_id,sale_order_rowinrows_sale_order.items():
            timesheet_forecast_table_rows.append(sale_order_row)
            forsale_line_row_key,sale_line_rowinrows_sale_line.items():
                ifsale_order_id==sale_line_row_key[0]:
                    sale_order_row[0]['has_children']=True
                    timesheet_forecast_table_rows.append(sale_line_row)
                    foremployee_row_key,employee_rowinrows_employee.items():
                        ifsale_order_id==employee_row_key[0]andsale_line_row_key[1]==employee_row_key[1]andemployee_row_key[2]inemployees.ids:
                            sale_line_row[0]['has_children']=True
                            timesheet_forecast_table_rows.append(employee_row)

        ifis_uom_day:
            #convertallvaluesfromhourstodays
            forrowintimesheet_forecast_table_rows:
                forindexinrange(1,len(row)):
                    row[index]=round(uom_hour._compute_quantity(row[index],company_uom,raise_if_failure=False),2)
        #completetabledata
        return{
            'header':self._table_header(),
            'rows':timesheet_forecast_table_rows
        }
    def_table_header(self):
        initial_date=fields.Date.from_string(fields.Date.today())
        ts_months=sorted([fields.Date.to_string(initial_date-relativedelta(months=i,day=1))foriinrange(0,DEFAULT_MONTH_RANGE)]) #M1,M2,M3

        def_to_short_month_name(date):
            month_index=fields.Date.from_string(date).month
            returnbabel.dates.get_month_names('abbreviated',locale=get_lang(self.env).code)[month_index]

        header_names=[_('SalesOrder'),_('Before')]+[_to_short_month_name(date)fordateints_months]+[_('Total'),_('Sold'),_('Remaining')]

        result=[]
        fornameinheader_names:
            result.append({
                'label':name,
                'tooltip':'',
            })
        #addtooltipforreminaing
        result[-1]['tooltip']=_('Whatisstilltodeliverbasedonsoldhoursandhoursalreadydone.Equalstosoldhours-donehours.')
        returnresult

    def_table_row_default(self):
        lenght=len(self._table_header())
        return[0.0]*(lenght-1) #before,M1,M2,M3,Done,Sold,Remaining

    def_table_rows_sql_query(self):
        initial_date=fields.Date.from_string(fields.Date.today())
        ts_months=sorted([fields.Date.to_string(initial_date-relativedelta(months=i,day=1))foriinrange(0,DEFAULT_MONTH_RANGE)]) #M1,M2,M3
        #buildquery
        query="""
            SELECT
                'timesheet'AStype,
                date_trunc('month',date)::dateASmonth_date,
                E.idASemployee_id,
                S.order_idASsale_order_id,
                A.so_lineASsale_line_id,
                SUM(A.unit_amount)ASnumber_hours
            FROMaccount_analytic_lineA
                JOINhr_employeeEONE.id=A.employee_id
                LEFTJOINsale_order_lineSONS.id=A.so_line
            WHEREA.project_idISNOTNULL
                ANDA.project_idIN%s
                ANDA.date<%s
            GROUPBYdate_trunc('month',date)::date,S.order_id,A.so_line,E.id
        """

        last_ts_month=fields.Date.to_string(fields.Date.from_string(ts_months[-1])+relativedelta(months=1))
        query_params=(tuple(self.ids),last_ts_month)
        returnquery,query_params

    def_table_rows_get_employee_lines(self,data_from_db):
        initial_date=fields.Date.today()
        ts_months=sorted([initial_date-relativedelta(months=i,day=1)foriinrange(0,DEFAULT_MONTH_RANGE)]) #M1,M2,M3
        default_row_vals=self._table_row_default()

        #extractemployeenames
        employee_ids=set()
        fordataindata_from_db:
            employee_ids.add(data['employee_id'])
        map_empl_names={empl.id:empl.nameforemplinself.env['hr.employee'].sudo().browse(employee_ids)}

        #extractrowsdataforemployee,solandsorows
        rows_employee={} #(so,sol,employee)->[INFO,before,M1,M2,M3,Done,M3,M4,M5,After,Forecasted]
        fordataindata_from_db:
            sale_line_id=data['sale_line_id']
            sale_order_id=data['sale_order_id']
            #employeerow
            row_key=(data['sale_order_id'],sale_line_id,data['employee_id'])
            ifrow_keynotinrows_employee:
                meta_vals={
                    'label':map_empl_names.get(row_key[2]),
                    'sale_line_id':sale_line_id,
                    'sale_order_id':sale_order_id,
                    'res_id':row_key[2],
                    'res_model':'hr.employee',
                    'type':'hr_employee'
                }
                rows_employee[row_key]=[meta_vals]+default_row_vals[:] #INFO,before,M1,M2,M3,Done,M3,M4,M5,After,Forecasted

            index=False
            ifdata['type']=='timesheet':
                ifdata['month_date']ints_months:
                    index=ts_months.index(data['month_date'])+2
                elifdata['month_date']<ts_months[0]:
                    index=1
                rows_employee[row_key][index]+=data['number_hours']
                rows_employee[row_key][5]+=data['number_hours']
        returnrows_employee

    def_table_get_empty_so_lines(self):
        """gettheSaleOrderLineshavingnotimesheetbuthavinggeneratedataskoraproject"""
        so_lines=self.sudo().mapped('sale_line_id.order_id.order_line').filtered(lambdasol:sol.is_serviceandnotsol.is_expenseandnotsol.is_downpayment)
        #includetheserviceSOlineofSOsharingthesameproject
        sale_order=self.env['sale.order'].search([('project_id','in',self.ids)])
        returnset(so_lines.ids)|set(sale_order.mapped('order_line').filtered(lambdasol:sol.is_serviceandnotsol.is_expense).ids),set(so_lines.mapped('order_id').ids)|set(sale_order.ids)

    #--------------------------------------------------
    #Actions:Statbuttons,...
    #--------------------------------------------------

    def_plan_prepare_actions(self,values):
        actions=[]
        iflen(self)==1:
            task_order_line_ids=[]
            #retrieveallthesaleorderlinethatwewillneedlaterbelow
            ifself.env.user.has_group('sales_team.group_sale_salesman')orself.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
                task_order_line_ids=self.env['project.task'].read_group([('project_id','=',self.id),('sale_line_id','!=',False)],['sale_line_id'],['sale_line_id'])
                task_order_line_ids=[ol['sale_line_id'][0]forolintask_order_line_ids]

            ifself.env.user.has_group('sales_team.group_sale_salesman'):
                ifself.bill_type=='customer_project'andself.allow_billableandnotself.sale_order_id:
                    actions.append({
                        'label':_("CreateaSalesOrder"),
                        'type':'action',
                        'action_id':'sale_timesheet.project_project_action_multi_create_sale_order',
                        'context':json.dumps({'active_id':self.id,'active_model':'project.project'}),
                    })
            ifself.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
                to_invoice_amount=values['dashboard']['profit'].get('to_invoice',False) #planprojectonlytakesservicesSOlinewithtimesheetintoaccount

                sale_order_ids=self.env['sale.order.line'].read_group([('id','in',task_order_line_ids)],['order_id'],['order_id'])
                sale_order_ids=[s['order_id'][0]forsinsale_order_ids]
                sale_order_ids=self.env['sale.order'].search_read([('id','in',sale_order_ids),('invoice_status','=','toinvoice')],['id'])
                sale_order_ids=list(map(lambdax:x['id'],sale_order_ids))

                ifto_invoice_amountandsale_order_ids:
                    iflen(sale_order_ids)==1:
                        actions.append({
                            'label':_("CreateInvoice"),
                            'type':'action',
                            'action_id':'sale.action_view_sale_advance_payment_inv',
                            'context':json.dumps({'active_ids':sale_order_ids,'active_model':'project.project'}),
                        })
                    else:
                        actions.append({
                            'label':_("CreateInvoice"),
                            'type':'action',
                            'action_id':'sale_timesheet.project_project_action_multi_create_invoice',
                            'context':json.dumps({'active_id':self.id,'active_model':'project.project'}),
                        })
        returnactions

    def_plan_get_stat_button(self):
        stat_buttons=[]
        num_projects=len(self)
        ifnum_projects==1:
            action_data=_to_action_data('project.project',res_id=self.id,
                                          views=[[self.env.ref('project.edit_project').id,'form']])
        else:
            action_data=_to_action_data(action=self.env.ref('project.open_view_project_all_config'),
                                          domain=[('id','in',self.ids)])

        stat_buttons.append({
            'name':_('Project')ifnum_projects==1else_('Projects'),
            'count':num_projects,
            'icon':'fafa-puzzle-piece',
            'action':action_data
        })

        #ifonlyoneproject,additinthecontextasdefaultvalue
        tasks_domain=[('project_id','in',self.ids)]
        tasks_context=self.env.context.copy()
        tasks_context.pop('search_default_name',False)
        late_tasks_domain=[('project_id','in',self.ids),('date_deadline','<',fields.Date.to_string(fields.Date.today())),('date_end','=',False)]
        overtime_tasks_domain=[('project_id','in',self.ids),('overtime','>',0),('planned_hours','>',0)]

        iflen(self)==1:
            tasks_context={**tasks_context,'default_project_id':self.id}
        eliflen(self):
            task_projects_ids=self.env['project.task'].read_group([('project_id','in',self.ids)],['project_id'],['project_id'])
            task_projects_ids=[p['project_id'][0]forpintask_projects_ids]
            iflen(task_projects_ids)==1:
                tasks_context={**tasks_context,'default_project_id':task_projects_ids[0]}

        stat_buttons.append({
            'name':_('Tasks'),
            'count':sum(self.mapped('task_count')),
            'icon':'fafa-tasks',
            'action':_to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=tasks_domain,
                context=tasks_context
            )
        })
        stat_buttons.append({
            'name':[_("Tasks"),_("Late")],
            'count':self.env['project.task'].search_count(late_tasks_domain),
            'icon':'fafa-tasks',
            'action':_to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=late_tasks_domain,
                context=tasks_context,
            ),
        })
        stat_buttons.append({
            'name':[_("Tasks"),_("inOvertime")],
            'count':self.env['project.task'].search_count(overtime_tasks_domain),
            'icon':'fafa-tasks',
            'action':_to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=overtime_tasks_domain,
                context=tasks_context,
            ),
        })

        ifself.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            #readallthesaleorderslinkedtotheprojects'tasks
            task_so_ids=self.env['project.task'].search_read([
                ('project_id','in',self.ids),('sale_order_id','!=',False)
            ],['sale_order_id'])
            task_so_ids=[o['sale_order_id'][0]forointask_so_ids]

            sale_orders=self.mapped('sale_line_id.order_id')|self.env['sale.order'].browse(task_so_ids)
            ifsale_orders:
                stat_buttons.append({
                    'name':_('SalesOrders'),
                    'count':len(sale_orders),
                    'icon':'fafa-dollar',
                    'action':_to_action_data(
                        action=self.env.ref('sale.action_orders'),
                        domain=[('id','in',sale_orders.ids)],
                        context={'create':False,'edit':False,'delete':False}
                    )
                })

                invoice_ids=self.env['sale.order'].search_read([('id','in',sale_orders.ids)],['invoice_ids'])
                invoice_ids=list(itertools.chain(*[i['invoice_ids']foriininvoice_ids]))
                invoice_ids=self.env['account.move'].search_read([('id','in',invoice_ids),('move_type','=','out_invoice')],['id'])
                invoice_ids=list(map(lambdax:x['id'],invoice_ids))

                ifinvoice_ids:
                    stat_buttons.append({
                        'name':_('Invoices'),
                        'count':len(invoice_ids),
                        'icon':'fafa-pencil-square-o',
                        'action':_to_action_data(
                            action=self.env.ref('account.action_move_out_invoice_type'),
                            domain=[('id','in',invoice_ids),('move_type','=','out_invoice')],
                            context={'create':False,'delete':False}
                        )
                    })

        ts_tree=self.env.ref('hr_timesheet.hr_timesheet_line_tree')
        ts_form=self.env.ref('hr_timesheet.hr_timesheet_line_form')
        ifself.env.company.timesheet_encode_uom_id==self.env.ref('uom.product_uom_day'):
            timesheet_label=[_('Days'),_('Recorded')]
        else:
            timesheet_label=[_('Hours'),_('Recorded')]

        stat_buttons.append({
            'name':timesheet_label,
            'count':sum(self.mapped('total_timesheet_time')),
            'icon':'fafa-calendar',
            'action':_to_action_data(
                'account.analytic.line',
                domain=[('project_id','in',self.ids)],
                views=[(ts_tree.id,'list'),(ts_form.id,'form')],
            )
        })

        returnstat_buttons


def_to_action_data(model=None,*,action=None,views=None,res_id=None,domain=None,context=None):
    #passineitheractionor(model,views)
    ifaction:
        assertmodelisNoneandviewsisNone
        act={
            field:value
            forfield,valueinaction.sudo().read()[0].items()
            iffieldinaction._get_readable_fields()
        }
        act=clean_action(act,env=action.env)
        model=act['res_model']
        views=act['views']
    #FIXME:search-view-id,possiblyhelp?
    descr={
        'data-model':model,
        'data-views':json.dumps(views),
    }
    ifcontextisnotNone:#otherwisecopyaction's?
        descr['data-context']=json.dumps(context)
    ifres_id:
        descr['data-res-id']=res_id
    elifdomain:
        descr['data-domain']=json.dumps(domain)
    returndescr
