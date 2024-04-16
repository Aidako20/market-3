#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError,ValidationError

fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression


classAccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    def_default_sale_line_domain(self):
        domain=super(AccountAnalyticLine,self)._default_sale_line_domain()
        returnexpression.OR([domain,[('qty_delivered_method','=','timesheet')]])

    timesheet_invoice_type=fields.Selection([
        ('billable_time','BilledonTimesheets'),
        ('billable_fixed','BilledataFixedprice'),
        ('non_billable','NonBillableTasks'),
        ('non_billable_timesheet','NonBillableTimesheet'),
        ('non_billable_project','Notaskfound')],string="BillableType",compute='_compute_timesheet_invoice_type',compute_sudo=True,store=True,readonly=True)
    timesheet_invoice_id=fields.Many2one('account.move',string="Invoice",readonly=True,copy=False,help="Invoicecreatedfromthetimesheet")
    non_allow_billable=fields.Boolean("Non-Billable",help="Yourtimesheetwillnotbebilled.")
    so_line=fields.Many2one(compute="_compute_so_line",store=True,readonly=False)

    #TODO:[XBO]Sincethetask_idisnotrequiredinthismodel, thenitshouldmoreefficienttodependstobill_typeandpricing_typeofproject(Seeinmaster)
    @api.depends('so_line.product_id','project_id','task_id','non_allow_billable','task_id.bill_type','task_id.pricing_type','task_id.non_allow_billable')
    def_compute_timesheet_invoice_type(self):
        non_allowed_billable=self.filtered('non_allow_billable')
        non_allowed_billable.timesheet_invoice_type='non_billable_timesheet'
        non_allowed_billable_task=(self-non_allowed_billable).filtered(lambdat:t.task_id.bill_type=='customer_project'andt.task_id.pricing_type=='employee_rate'andt.task_id.non_allow_billable)
        non_allowed_billable_task.timesheet_invoice_type='non_billable'

        fortimesheetinself-non_allowed_billable-non_allowed_billable_task:
            iftimesheet.project_id: #AALwillbesettoFalse
                invoice_type='non_billable_project'ifnottimesheet.task_idelse'non_billable'
                iftimesheet.task_idandtimesheet.so_line.product_id.type=='service':
                    iftimesheet.so_line.product_id.invoice_policy=='delivery':
                        iftimesheet.so_line.product_id.service_type=='timesheet':
                            invoice_type='billable_time'
                        else:
                            invoice_type='billable_fixed'
                    eliftimesheet.so_line.product_id.invoice_policy=='order':
                        invoice_type='billable_fixed'
                timesheet.timesheet_invoice_type=invoice_type
            else:
                timesheet.timesheet_invoice_type=False

    @api.onchange('employee_id')
    def_onchange_task_id_employee_id(self):
        ifself.project_idandself.task_id.allow_billable: #timesheetonly
            ifself.task_id.bill_type=='customer_task'orself.task_id.pricing_type=='fixed_rate':
                self.so_line=self.task_id.sale_line_id
            elifself.task_id.pricing_type=='employee_rate':
                self.so_line=self._timesheet_determine_sale_line(self.task_id,self.employee_id,self.project_id)
            else:
                self.so_line=False

    @api.depends('task_id.sale_line_id','project_id.sale_line_id','employee_id','project_id.allow_billable')
    def_compute_so_line(self):
        fortimesheetinself._get_not_billed(): #Getonlythetimesheetsarenotyetinvoiced
            timesheet.so_line=timesheet.project_id.allow_billableandtimesheet._timesheet_determine_sale_line(timesheet.task_id,timesheet.employee_id,timesheet.project_id)
    
    @api.depends('timesheet_invoice_id.state')
    def_compute_partner_id(self):
        super(AccountAnalyticLine,self._get_not_billed())._compute_partner_id()

    def_get_not_billed(self):
        returnself.filtered(lambdat:nott.timesheet_invoice_idort.timesheet_invoice_id.state=='cancel')

    def_check_timesheet_can_be_billed(self):
        returnself.so_lineinself.project_id.mapped('sale_line_employee_ids.sale_line_id')|self.task_id.sale_line_id|self.project_id.sale_line_id

    @api.constrains('so_line','project_id')
    def_check_sale_line_in_project_map(self):
        ifnotall(t._check_timesheet_can_be_billed()fortinself._get_not_billed().filtered(lambdat:t.project_idandt.so_line)):
            raiseValidationError(_("Thistimesheetlinecannotbebilled:thereisnoSaleOrderItemdefinedonthetask,norontheproject.Pleasedefineonetosaveyourtimesheetline."))

    defwrite(self,values):
        #preventtoupdateinvoicedtimesheetsifonelineisoftypedelivery
        self._check_can_write(values)
        result=super(AccountAnalyticLine,self).write(values)
        returnresult

    def_check_can_write(self,values):
        ifself.sudo().filtered(lambdaaal:aal.so_line.product_id.invoice_policy=="delivery")andself.filtered(lambdat:t.timesheet_invoice_idandt.timesheet_invoice_id.state!='cancel'):
            ifany(field_nameinvaluesforfield_namein['unit_amount','employee_id','project_id','task_id','so_line','amount','date']):
                raiseUserError(_('Youcannotmodifyalreadyinvoicedtimesheets(linkedtoaSalesorderitemsinvoicedonTimeandmaterial).'))

    @api.model
    def_timesheet_preprocess(self,values):
        ifvalues.get('task_id')andnotvalues.get('account_id'):
            task=self.env['project.task'].browse(values.get('task_id'))
            iftask.analytic_account_id:
                values['account_id']=task.analytic_account_id.id
                values['company_id']=task.analytic_account_id.company_id.idortask.company_id.id
        values=super(AccountAnalyticLine,self)._timesheet_preprocess(values)
        returnvalues

    @api.model
    def_timesheet_determine_sale_line(self,task,employee,project):
        """DeducetheSOlineassociatedtothetimesheetline:
            1/timesheetontaskrate:thesolinewillbetheonefromthetask
            2/timesheetonemployeeratetask:findtheSOlineinthemapoftheproject(evenforsubtask),orfallbackontheSOlineofthetask,orfallback
                ontheoneontheproject
        """
        ifnottask:
            ifproject.bill_type=='customer_project'andproject.pricing_type=='employee_rate':
                map_entry=self.env['project.sale.line.employee.map'].search([('project_id','=',project.id),('employee_id','=',employee.id)])
                ifmap_entry:
                    returnmap_entry.sale_line_id
            ifproject.sale_line_id:
                returnproject.sale_line_id
        iftask.allow_billableandtask.sale_line_id:
            iftask.bill_type=='customer_task':
                returntask.sale_line_id
            iftask.pricing_type=='fixed_rate':
                returntask.sale_line_id
            eliftask.pricing_type=='employee_rate'andnottask.non_allow_billable:
                map_entry=project.sale_line_employee_ids.filtered(lambdamap_entry:map_entry.employee_id==employee)
                ifmap_entry:
                    returnmap_entry.sale_line_id
                iftask.sale_line_idorproject.sale_line_id:
                    returntask.sale_line_idorproject.sale_line_id
        returnself.env['sale.order.line']

    def_timesheet_get_portal_domain(self):
        """Onlythetimesheetswithaproductinvoicedondeliveredquantityareconcerned.
            sinceinorderedquantity,thetimesheetquantityisnotinvoiced,
            thusthereisnomeaningofshowinginvoicewithorderedquantity.
        """
        domain=super(AccountAnalyticLine,self)._timesheet_get_portal_domain()
        returnexpression.AND([domain,[('timesheet_invoice_type','in',['billable_time','non_billable','billable_fixed'])]])

    @api.model
    def_timesheet_get_sale_domain(self,order_lines_ids,invoice_ids):
        ifnotinvoice_ids:
            return[('so_line','in',order_lines_ids.ids)]

        return[
            '|',
            '&',
            ('timesheet_invoice_id','in',invoice_ids.ids),
            #TODO:Master:Checkifnon_billableshouldberemoved?
            ('timesheet_invoice_type','in',['billable_time','non_billable']),
            '&',
            ('timesheet_invoice_type','=','billable_fixed'),
            ('so_line','in',order_lines_ids.ids)
        ]

    def_get_timesheets_to_merge(self):
        res=super(AccountAnalyticLine,self)._get_timesheets_to_merge()
        returnres.filtered(lambdal:notl.timesheet_invoice_idorl.timesheet_invoice_id.state!='posted')

    defunlink(self):
        ifany(line.timesheet_invoice_idandline.timesheet_invoice_id.state=='posted'forlineinself):
            raiseUserError(_('Youcannotremoveatimesheetthathasalreadybeeninvoiced.'))
        returnsuper(AccountAnalyticLine,self).unlink()
