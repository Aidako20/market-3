#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


#YTIPLEASESPLITME
classProject(models.Model):
    _inherit='project.project'

    @api.model
    defdefault_get(self,fields):
        """Pre-filltimesheetproductas"Time"dataproductwhencreatingnewprojectallowingbillabletasksbydefault."""
        result=super(Project,self).default_get(fields)
        if'timesheet_product_id'infieldsandresult.get('allow_billable')andresult.get('allow_timesheets')andnotresult.get('timesheet_product_id'):
            default_product=self.env.ref('sale_timesheet.time_product',False)
            ifdefault_product:
                result['timesheet_product_id']=default_product.id
        returnresult

    def_default_timesheet_product_id(self):
        returnself.env.ref('sale_timesheet.time_product',False)

    bill_type=fields.Selection([
        ('customer_task','Differentcustomers'),
        ('customer_project','Auniquecustomer')
    ],string="InvoiceTasksto",default="customer_task",
        help='Whenbillingtasksindividually,aSalesOrderwillbecreatedfromeachtask.Itisperfectifyouwouldliketobilldifferentservicestodifferentcustomersatdifferentrates.\nWhenbillingthewholeproject,aSalesOrderwillbecreatedfromtheprojectinstead.Thisoptionisbetterifyouwouldliketobillallthetasksofagivenprojecttoaspecificcustomereitheratafixedrate,oratanemployeerate.')
    pricing_type=fields.Selection([
        ('fixed_rate','Projectrate'),
        ('employee_rate','Employeerate')
    ],string="Pricing",default="fixed_rate",
        help='Thefixedrateisperfectifyoubillaserviceatafixedrateperhourordayworkedregardlessoftheemployeewhoperformedit.Theemployeerateispreferableifyouremployeesdeliverthesameserviceatadifferentrate.Forinstance,juniorandseniorconsultantswoulddeliverthesameservice(=consultancy),butatadifferentratebecauseoftheirlevelofseniority.')
    sale_line_employee_ids=fields.One2many('project.sale.line.employee.map','project_id',"Saleline/Employeemap",copy=False,
        help="Employee/SaleOrderItemMapping:\nDefinestowhichsalesorderitemanemployee'stimesheetentrywillbelinked."
        "Byextension,itdefinestherateatwhichanemployee'stimeontheprojectisbilled.")
    allow_billable=fields.Boolean("Billable",help="Invoiceyourtimeandmaterialfromtasks.")
    display_create_order=fields.Boolean(compute='_compute_display_create_order')
    timesheet_product_id=fields.Many2one(
        'product.product',string='TimesheetProduct',
        domain="""[
            ('type','=','service'),
            ('invoice_policy','=','delivery'),
            ('service_type','=','timesheet'),
            '|',('company_id','=',False),('company_id','=',company_id)]""",
        help='SelectaServiceproductwithwhichyouwouldliketobillyourtimespentontasks.',
        compute="_compute_timesheet_product_id",store=True,readonly=False,
        default=_default_timesheet_product_id)
    warning_employee_rate=fields.Boolean(compute='_compute_warning_employee_rate')

    _sql_constraints=[
        ('timesheet_product_required_if_billable_and_time',"""
            CHECK(
                (allow_billable='t'ANDallow_timesheets='t'ANDtimesheet_product_idISNOTNULL)
                OR(allow_billableISNOTTRUE)
                OR(allow_timesheetsISNOTTRUE)
                OR(allow_billableISNULL)
                OR(allow_timesheetsISNULL)
            )""",'Thetimesheetproductisrequiredwhenthetaskcanbebilledandtimesheetsareallowed.'),

    ]

    @api.depends('allow_billable','sale_order_id','partner_id','bill_type')
    def_compute_display_create_order(self):
        forprojectinself:
            show=True
            ifnotproject.partner_idorproject.bill_type!='customer_project'ornotproject.allow_billableorproject.sale_order_id:
                show=False
            project.display_create_order=show

    @api.depends('allow_timesheets','allow_billable')
    def_compute_timesheet_product_id(self):
        default_product=self.env.ref('sale_timesheet.time_product',False)
        forprojectinself:
            ifnotproject.allow_timesheetsornotproject.allow_billable:
                project.timesheet_product_id=False
            elifnotproject.timesheet_product_id:
                project.timesheet_product_id=default_product

    @api.depends('pricing_type','allow_timesheets','allow_billable','sale_line_employee_ids','sale_line_employee_ids.employee_id','bill_type')
    def_compute_warning_employee_rate(self):
        projects=self.filtered(lambdap:p.allow_billableandp.allow_timesheetsandp.bill_type=='customer_project'andp.pricing_type=='employee_rate')
        tasks=projects.task_ids.filtered(lambdat:nott.non_allow_billable)
        employees=self.env['account.analytic.line'].read_group([('task_id','in',tasks.ids),('non_allow_billable','=',False)],['employee_id','project_id'],['employee_id','project_id'],lazy=False)
        dict_project_employee=defaultdict(list)
        forlineinemployees:
            dict_project_employee[line['project_id'][0]]+=[line['employee_id'][0]]ifline['employee_id']else[]
        forprojectinprojects:
            project.warning_employee_rate=any(xnotinproject.sale_line_employee_ids.employee_id.idsforxindict_project_employee[project.id])

        (self-projects).warning_employee_rate=False

    @api.constrains('sale_line_id','pricing_type')
    def_check_sale_line_type(self):
        forprojectinself:
            ifproject.pricing_type=='fixed_rate':
                ifproject.sale_line_idandnotproject.sale_line_id.is_service:
                    raiseValidationError(_("AbillableprojectshouldbelinkedtoaSalesOrderItemhavingaServiceproduct."))
                ifproject.sale_line_idandproject.sale_line_id.is_expense:
                    raiseValidationError(_("AbillableprojectshouldbelinkedtoaSalesOrderItemthatdoesnotcomefromanexpenseoravendorbill."))

    @api.onchange('allow_billable')
    def_onchange_allow_billable(self):
        ifself.task_ids._get_timesheet()andself.allow_timesheetsandnotself.allow_billable:
            message=_("AlltimesheethoursthatarenotyetinvoicedwillberemovedfromSalesOrderonsave.Discardtoavoidthechange.")
            return{'warning':{
                'title':_("Warning"),
                'message':message
            }}

    defwrite(self,values):
        res=super(Project,self).write(values)
        if'allow_billable'invaluesandnotvalues.get('allow_billable'):
            self.task_ids._get_timesheet().write({
                'so_line':False,
            })
        returnres

    def_get_not_billed_timesheets(self):
        returnself.sudo(False).mapped('timesheet_ids').filtered(
            lambdat:nott.timesheet_invoice_idort.timesheet_invoice_id.state=='cancel')

    def_update_timesheets_sale_line_id(self):
        forprojectinself.filtered(lambdap:p.allow_billableandp.allow_timesheets):
            timesheet_ids=project._get_not_billed_timesheets()
            ifnottimesheet_ids:
                continue
            foremployee_idinproject.sale_line_employee_ids.filtered(lambdal:l.project_id==project).employee_id:
                sale_line_id=project.sale_line_employee_ids.filtered(lambdal:l.project_id==projectandl.employee_id==employee_id).sale_line_id
                timesheet_ids.filtered(lambdat:t.employee_id==employee_id).sudo().so_line=sale_line_id

    defaction_view_timesheet(self):
        self.ensure_one()
        ifself.allow_timesheets:
            returnself.action_view_timesheet_plan()
        return{
            'type':'ir.actions.act_window',
            'name':_('Timesheetsof%s',self.name),
            'domain':[('project_id','!=',False)],
            'res_model':'account.analytic.line',
            'view_id':False,
            'view_mode':'tree,form',
            'help':_("""
                <pclass="o_view_nocontent_smiling_face">
                    Recordtimesheets
                </p><p>
                    Youcanregisterandtrackyourworkingshoursbyprojectevery
                    day.Everytimespentonaprojectwillbecomeacostandcanbere-invoicedto
                    customersifrequired.
                </p>
            """),
            'limit':80,
            'context':{
                'default_project_id':self.id,
                'search_default_project_id':[self.id]
            }
        }

    defaction_view_timesheet_plan(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale_timesheet.project_timesheet_action_client_timesheet_plan")
        action['params']={
            'project_ids':self.ids,
        }
        action['context']={
            'active_id':self.id,
            'active_ids':self.ids,
            'search_default_name':self.name,
        }
        returnaction

    defaction_make_billable(self):
        return{
            "name":_("CreateSalesOrder"),
            "type":'ir.actions.act_window',
            "res_model":'project.create.sale.order',
            "views":[[False,"form"]],
            "target":'new',
            "context":{
                'active_id':self.id,
                'active_model':'project.project',
                'default_product_id':self.timesheet_product_id.id,
            },
        }


classProjectTask(models.Model):
    _inherit="project.task"

    @api.model
    defdefault_get(self,fields):
        result=super(ProjectTask,self).default_get(fields)

        ifnotresult.get('timesheet_product_id',False)and'project_id'inresult:
            project=self.env['project.project'].browse(result['project_id'])
            ifproject.bill_type!='customer_project'orproject.pricing_type!='employee_rate':
                result['timesheet_product_id']=project.timesheet_product_id.id
        returnresult

    #overridesale_order_idandmakeitcomputedstoredfieldinsteadofregularfield.
    sale_order_id=fields.Many2one(compute='_compute_sale_order_id',store=True,readonly=False,
    domain="['|','|',('partner_id','=',partner_id),('partner_id','child_of',commercial_partner_id),('partner_id','parent_of',partner_id)]")
    #contentinrelatedparameterofthefielddefinitionisremovedtomanuallydefinethecomputeandthesearchmethod.
    project_sale_order_id=fields.Many2one(compute='_compute_project_sale_order_id',search='_search_project_sale_order_id',related=None)
    analytic_account_id=fields.Many2one('account.analytic.account',related='sale_order_id.analytic_account_id')
    bill_type=fields.Selection(related="project_id.bill_type")
    pricing_type=fields.Selection(related="project_id.pricing_type")
    is_project_map_empty=fields.Boolean("IsProjectmapempty",compute='_compute_is_project_map_empty')
    has_multi_sol=fields.Boolean(compute='_compute_has_multi_sol',compute_sudo=True)
    allow_billable=fields.Boolean(related="project_id.allow_billable")
    display_create_order=fields.Boolean(compute='_compute_display_create_order')
    timesheet_product_id=fields.Many2one(
        'product.product',string='Service',
        domain="""[
            ('type','=','service'),
            ('invoice_policy','=','delivery'),
            ('service_type','=','timesheet'),
            '|',('company_id','=',False),('company_id','=',company_id)]""",
        help='SelectaServiceproductwithwhichyouwouldliketobillyourtimespentonthistask.')

    #TODO:[XBO]removemeinmaster
    non_allow_billable=fields.Boolean("Non-Billable",help="Yourtimesheetslinkedtothistaskwillnotbebilled.")
    remaining_hours_so=fields.Float('RemainingHoursonSO',compute='_compute_remaining_hours_so',compute_sudo=True)
    remaining_hours_available=fields.Boolean(related="sale_line_id.remaining_hours_available")

    @api.depends('sale_line_id','timesheet_ids','timesheet_ids.unit_amount')
    def_compute_remaining_hours_so(self):
        #TODOThisisnotyetperfectlyworkingastimesheet.so_linesticktoitsoldvaluealthoughchanged
        #     inthetaskFromView.
        timesheets=self.timesheet_ids.filtered(lambdat:t.task_id.sale_line_idin(t.so_line,t._origin.so_line)andt.so_line.remaining_hours_available)

        mapped_remaining_hours={task._origin.id:task.sale_line_idandtask.sale_line_id.remaining_hoursor0.0fortaskinself}
        uom_hour=self.env.ref('uom.product_uom_hour')
        fortimesheetintimesheets:
            delta=0
            iftimesheet._origin.so_line==timesheet.task_id.sale_line_id:
                delta+=timesheet._origin.unit_amount
            iftimesheet.so_line==timesheet.task_id.sale_line_id:
                delta-=timesheet.unit_amount
            ifdelta:
                mapped_remaining_hours[timesheet.task_id._origin.id]+=timesheet.product_uom_id._compute_quantity(delta,uom_hour)

        fortaskinself:
            task.remaining_hours_so=mapped_remaining_hours[task._origin.id]

    @api.depends(
        'allow_billable','allow_timesheets','sale_order_id')
    def_compute_display_create_order(self):
        fortaskinself:
            show=True
            ifnottask.allow_billableornottask.allow_timesheetsor\
                (task.bill_type!='customer_task'andnottask.timesheet_product_id)or(nottask.partner_idandtask.bill_type!='customer_task')or\
                task.sale_order_idor(task.bill_type!='customer_task'andtask.pricing_type!='employee_rate'):
                show=False
            task.display_create_order=show

    @api.onchange('sale_line_id')
    def_onchange_sale_line_id(self):
        #TODO:removemeinmaster
        return

    @api.onchange('project_id')
    def_onchange_project_id(self):
        #TODO:removemeinmaster
        return

    @api.depends('analytic_account_id.active')
    def_compute_analytic_account_active(self):
        super()._compute_analytic_account_active()
        fortaskinself:
            task.analytic_account_active=task.analytic_account_activeortask.analytic_account_id.active

    @api.depends('project_id.bill_type','project_id.sale_order_id')
    def_compute_project_sale_order_id(self):
        fortaskinself:
            iftask.bill_type!='customer_task':
                task.project_sale_order_id=task.project_id.sale_order_id
            else:
                task.project_sale_order_id=False

    @api.depends('sale_line_id','project_id','allow_billable','non_allow_billable')
    def_compute_sale_order_id(self):
        fortaskinself:
            ifnottask.allow_billableortask.non_allow_billable:
                task.sale_order_id=False
            eliftask.allow_billable:
                iftask.sale_line_id:
                    task.sale_order_id=task.sale_line_id.sudo().order_id
                eliftask.project_id.sale_order_id:
                    task.sale_order_id=task.project_id.sale_order_id
                iftask.sale_order_idandnottask.partner_id:
                    task.partner_id=task.sale_order_id.partner_id

    @api.depends('commercial_partner_id','sale_line_id.order_partner_id.commercial_partner_id','parent_id.sale_line_id','project_id.sale_line_id','allow_billable')
    def_compute_sale_line(self):
        billable_tasks=self.filtered('allow_billable')
        super(ProjectTask,billable_tasks)._compute_sale_line()
        fortaskinbillable_tasks.filtered(lambdat:nott.sale_line_id):
            task.sale_line_id=task._get_last_sol_of_customer()

    @api.depends('project_id.sale_line_employee_ids')
    def_compute_is_project_map_empty(self):
        fortaskinself:
            task.is_project_map_empty=notbool(task.sudo().project_id.sale_line_employee_ids)

    @api.depends('timesheet_ids')
    def_compute_has_multi_sol(self):
        fortaskinself:
            task.has_multi_sol=task.timesheet_idsandtask.timesheet_ids.so_line!=task.sale_line_id

    @api.onchange('project_id')
    def_onchange_project(self):
        ifself.project_idandself.project_id.bill_type=='customer_project':
            ifnotself.partner_id:
                self.partner_id=self.project_id.partner_id
            ifnotself.sale_line_id:
                self.sale_line_id=self.project_id.sale_line_id

    def_search_project_sale_order_id(self,operator,value):
        return[('bill_type','!=','customer_task'),('project_id.sale_order_id',operator,value)]

    defwrite(self,values):
        res=super(ProjectTask,self).write(values)
        #Doneaftersupertoavoidconstraintsonfieldrecomputation
        ifvalues.get('project_id'):
            project_dest=self.env['project.project'].browse(values['project_id'])
            ifproject_dest.bill_type=='customer_project'andproject_dest.pricing_type=='employee_rate':
                self.write({'sale_line_id':False})
        if'non_allow_billable'invaluesandself.filtered('allow_timesheets').sudo().timesheet_ids:
            timesheet_ids=self.filtered('allow_timesheets').timesheet_ids.filtered(
                lambdat:(nott.timesheet_invoice_idort.timesheet_invoice_id.state=='cancel')
            )
            ifvalues['non_allow_billable']:
                timesheet_ids.write({'so_line':False})
                self.sale_line_id=False
            else:
                #Wewriteprojectontimesheetlinestocall_timesheet_preprocess.ThisfunctionwillsetcorrecttheSOL
                forprojectintimesheet_ids.project_id:
                    current_timesheet_ids=timesheet_ids.filtered(lambdat:t.project_id==project)
                    current_timesheet_ids.task_id.update({'sale_line_id':project.sale_line_id.id})
                    foremployeeincurrent_timesheet_ids.employee_id:
                        current_timesheet_ids.filtered(lambdat:t.employee_id==employee).write({'project_id':project.id})

        returnres

    def_get_last_sol_of_customer(self):
        #GetthelastSOLmadeforthecustomerinthecurrenttaskwhereweneedtocompute
        self.ensure_one()
        ifnotself.commercial_partner_idornotself.allow_billable:
            returnFalse
        domain=[('company_id','=',self.company_id.id),('is_service','=',True),('order_partner_id','child_of',self.commercial_partner_id.id),('is_expense','=',False),('state','in',['sale','done'])]
        ifself.project_id.bill_type=='customer_project'andself.project_sale_order_id:
            domain.append(('order_id','=?',self.project_sale_order_id.id))
        sale_lines=self.env['sale.order.line'].search(domain)
        forlineinsale_lines:
            ifline.remaining_hours_availableandline.remaining_hours>0:
                returnline
        returnFalse

    defaction_make_billable(self):
        return{
            "name":_("CreateSalesOrder"),
            "type":'ir.actions.act_window',
            "res_model":'project.task.create.sale.order',
            "views":[[False,"form"]],
            "target":'new',
            "context":{
                'active_id':self.id,
                'active_model':'project.task',
                'form_view_initial_mode':'edit',
                'default_product_id':self.timesheet_product_id.idorself.project_id.timesheet_product_id.id,
            },
        }

    def_get_timesheet(self):
        #returnnotinvoicedtimesheetandtimesheetwithoutso_lineorso_linelinkedtotask
        timesheet_ids=super(ProjectTask,self)._get_timesheet()
        returntimesheet_ids.filtered(lambdat:(nott.timesheet_invoice_idort.timesheet_invoice_id.state=='cancel')and(nott.so_lineort.so_line==t.task_id._origin.sale_line_id))

    def_get_action_view_so_ids(self):
        returnlist(set((self.sale_order_id+self.timesheet_ids.so_line.order_id).ids))

classProjectTaskRecurrence(models.Model):
    _inherit='project.task.recurrence'

    @api.model
    def_get_recurring_fields(self):
        return['analytic_account_id']+super(ProjectTaskRecurrence,self)._get_recurring_fields()
