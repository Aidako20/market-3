#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression
importmath


classSaleOrder(models.Model):
    _inherit='sale.order'

    timesheet_ids=fields.Many2many('account.analytic.line',compute='_compute_timesheet_ids',string='Timesheetactivitiesassociatedtothissale')
    timesheet_count=fields.Float(string='Timesheetactivities',compute='_compute_timesheet_ids',groups="hr_timesheet.group_hr_timesheet_user")

    #overridedomain
    project_id=fields.Many2one(domain="['|',('bill_type','=','customer_task'),('pricing_type','=','fixed_rate'),('analytic_account_id','!=',False),('company_id','=',company_id)]")
    timesheet_encode_uom_id=fields.Many2one('uom.uom',related='company_id.timesheet_encode_uom_id')
    timesheet_total_duration=fields.Integer("TimesheetTotalDuration",compute='_compute_timesheet_total_duration',help="Totalrecordedduration,expressedintheencodingUoM,androundedtotheunit")

    @api.depends('analytic_account_id.line_ids')
    def_compute_timesheet_ids(self):
        fororderinself:
            iforder.analytic_account_id:
                order.timesheet_ids=self.env['account.analytic.line'].search(
                    [('so_line','in',order.order_line.ids),
                        ('amount','<=',0.0),
                        ('project_id','!=',False)])
            else:
                order.timesheet_ids=[]
            order.timesheet_count=len(order.timesheet_ids)

    @api.depends('timesheet_ids','company_id.timesheet_encode_uom_id')
    def_compute_timesheet_total_duration(self):
        forsale_orderinself:
            timesheets=sale_order.timesheet_idsifself.user_has_groups('hr_timesheet.group_hr_timesheet_approver')elsesale_order.timesheet_ids.filtered(lambdat:t.user_id.id==self.env.uid)
            total_time=0.0
            fortimesheetintimesheets.filtered(lambdat:nott.non_allow_billable):
                #Timesheetsmaybestoredinadifferentunitofmeasure,sofirstweconvertallofthemtothereferenceunit
                total_time+=timesheet.unit_amount*timesheet.product_uom_id.factor_inv
            #Nowconverttotheproperunitofmeasure
            total_time*=sale_order.timesheet_encode_uom_id.factor
            sale_order.timesheet_total_duration=total_time

    defaction_view_project_ids(self):
        self.ensure_one()
        #redirecttoformorkanbanview
        billable_projects=self.project_ids.filtered(lambdaproject:project.sale_line_id)
        iflen(billable_projects)==1andself.env.user.has_group('project.group_project_manager'):
            action=billable_projects[0].action_view_timesheet_plan()
        else:
            action=super().action_view_project_ids()
        returnaction

    defaction_view_timesheet(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("sale_timesheet.timesheet_action_from_sales_order")
        action['context']={
            'search_default_billable_timesheet':True
        } #erasedefaultfilters
        ifself.timesheet_count>0:
            action['domain']=[('so_line','in',self.order_line.ids),('project_id','!=',False)]
        else:
            action={'type':'ir.actions.act_window_close'}
        returnaction

    def_create_invoices(self,grouped=False,final=False,date=None):
        """Linktimesheetstothecreatedinvoices.Dateintervalisinjectedinthe
        contextinsale_make_invoice_advance_invwizard.
        """
        moves=super()._create_invoices(grouped=grouped,final=final,date=date)
        moves._link_timesheets_to_invoice(self.env.context.get("timesheet_start_date"),self.env.context.get("timesheet_end_date"))
        returnmoves


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    qty_delivered_method=fields.Selection(selection_add=[('timesheet','Timesheets')])
    analytic_line_ids=fields.One2many(domain=[('project_id','=',False)]) #onlyanalyticlines,nottimesheets(sincethisfielddetermineifSOlinecamefromexpense)
    remaining_hours_available=fields.Boolean(compute='_compute_remaining_hours_available')
    remaining_hours=fields.Float('RemainingHoursonSO',compute='_compute_remaining_hours')

    defname_get(self):
        res=super(SaleOrderLine,self).name_get()
        ifself.env.context.get('with_remaining_hours'):
            names=dict(res)
            result=[]
            uom_hour=self.env.ref('uom.product_uom_hour')
            uom_day=self.env.ref('uom.product_uom_day')
            forlineinself:
                name=names.get(line.id)
                ifline.remaining_hours_available:
                    company=self.env.company
                    encoding_uom=company.timesheet_encode_uom_id
                    remaining_time=''
                    ifencoding_uom==uom_hour:
                        hours,minutes=divmod(abs(line.remaining_hours)*60,60)
                        round_minutes=minutes/30
                        minutes=math.ceil(round_minutes)ifline.remaining_hours>=0elsemath.floor(round_minutes)
                        ifminutes>1:
                            minutes=0
                            hours+=1
                        else:
                            minutes=minutes*30
                        remaining_time='({sign}{hours:02.0f}:{minutes:02.0f})'.format(
                            sign='-'ifline.remaining_hours<0else'',
                            hours=hours,
                            minutes=minutes)
                    elifencoding_uom==uom_day:
                        remaining_days=company.project_time_mode_id._compute_quantity(line.remaining_hours,encoding_uom,round=False)
                        remaining_time='({qty:.02f}{unit})'.format(
                            qty=remaining_days,
                            unit=_('days')ifabs(remaining_days)>1else_('day')
                        )
                    name='{name}{remaining_time}'.format(
                        name=name,
                        remaining_time=remaining_time
                    )
                result.append((line.id,name))
            returnresult
        returnres

    @api.depends('product_id.service_policy')
    def_compute_remaining_hours_available(self):
        uom_hour=self.env.ref('uom.product_uom_hour')
        forlineinself:
            is_ordered_timesheet=line.product_id.service_policy=='ordered_timesheet'
            is_time_product=line.product_uom.category_id==uom_hour.category_id
            line.remaining_hours_available=is_ordered_timesheetandis_time_product

    @api.depends('qty_delivered','product_uom_qty','analytic_line_ids')
    def_compute_remaining_hours(self):
        uom_hour=self.env.ref('uom.product_uom_hour')
        forlineinself:
            remaining_hours=None
            ifline.remaining_hours_available:
                qty_left=line.product_uom_qty-line.qty_delivered
                remaining_hours=line.product_uom._compute_quantity(qty_left,uom_hour)
            line.remaining_hours=remaining_hours

    @api.depends('product_id')
    def_compute_qty_delivered_method(self):
        """SaleTimesheetmodulecomputedeliveredqtyforproduct[('type','in',['service']),('service_type','=','timesheet')]"""
        super(SaleOrderLine,self)._compute_qty_delivered_method()
        forlineinself:
            ifnotline.is_expenseandline.product_id.type=='service'andline.product_id.service_type=='timesheet':
                line.qty_delivered_method='timesheet'

    @api.depends('analytic_line_ids.project_id','analytic_line_ids.non_allow_billable','project_id.pricing_type','project_id.bill_type')
    def_compute_qty_delivered(self):
        super(SaleOrderLine,self)._compute_qty_delivered()

        lines_by_timesheet=self.filtered(lambdasol:sol.qty_delivered_method=='timesheet')
        domain=lines_by_timesheet._timesheet_compute_delivered_quantity_domain()
        mapping=lines_by_timesheet.sudo()._get_delivered_quantity_by_analytic(domain)
        forlineinlines_by_timesheet:
            line.qty_delivered=mapping.get(line.idorline._origin.id,0.0)

    def_timesheet_compute_delivered_quantity_domain(self):
        """Hookforvalidatedtimesheetinaddionnalmodule"""
        return[('project_id','!=',False),('non_allow_billable','=',False)]

    ###########################################
    #Service:Projectandtaskgeneration
    ###########################################

    def_convert_qty_company_hours(self,dest_company):
        company_time_uom_id=dest_company.project_time_mode_id
        ifself.product_uom.id!=company_time_uom_id.idandself.product_uom.category_id.id==company_time_uom_id.category_id.id:
            planned_hours=self.product_uom._compute_quantity(self.product_uom_qty,company_time_uom_id)
        else:
            planned_hours=self.product_uom_qty
        returnplanned_hours

    def_timesheet_create_project(self):
        project=super()._timesheet_create_project()
        project.write({'allow_timesheets':True})
        returnproject

    def_timesheet_create_project_prepare_values(self):
        """Generateprojectvalues"""
        values=super()._timesheet_create_project_prepare_values()
        values['allow_billable']=True
        values['bill_type']='customer_project'
        values['pricing_type']='fixed_rate'
        returnvalues

    def_recompute_qty_to_invoice(self,start_date,end_date):
        """Recomputetheqty_to_invoicefieldforproductcontainingtimesheets

            Searchtheexistedtimesheetsbetweenthegivenperiodinparameter.
            Retrievetheunit_amountofthistimesheetandthenrecompute
            theqty_to_invoiceforeachcurrentproduct.

            :paramstart_date:thestartdateoftheperiod
            :paramend_date:theenddateoftheperiod
        """
        lines_by_timesheet=self.filtered(lambdasol:sol.product_idandsol.product_id._is_delivered_timesheet())
        domain=lines_by_timesheet._timesheet_compute_delivered_quantity_domain()
        refund_account_moves=self.order_id.invoice_ids.filtered(lambdaam:am.state=='posted'andam.move_type=='out_refund').reversed_entry_id
        timesheet_domain=[
            '|',
            ('timesheet_invoice_id','=',False),
            ('timesheet_invoice_id.state','=','cancel')]
        ifrefund_account_moves:
            credited_timesheet_domain=[('timesheet_invoice_id.state','=','posted'),('timesheet_invoice_id','in',refund_account_moves.ids)]
            timesheet_domain=expression.OR([timesheet_domain,credited_timesheet_domain])
        domain=expression.AND([domain,timesheet_domain])
        ifstart_date:
            domain=expression.AND([domain,[('date','>=',start_date)]])
        ifend_date:
            domain=expression.AND([domain,[('date','<=',end_date)]])
        mapping=lines_by_timesheet.sudo()._get_delivered_quantity_by_analytic(domain)

        forlineinlines_by_timesheet:
            line.qty_to_invoice=mapping.get(line.id,0.0)
