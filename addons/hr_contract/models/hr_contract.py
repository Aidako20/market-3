#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importthreading

fromdatetimeimportdate
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError

fromflectra.osvimportexpression

importlogging
_logger=logging.getLogger(__name__)


classContract(models.Model):
    _name='hr.contract'
    _description='Contract'
    _inherit=['mail.thread','mail.activity.mixin']

    name=fields.Char('ContractReference',required=True)
    active=fields.Boolean(default=True)
    structure_type_id=fields.Many2one('hr.payroll.structure.type',string="SalaryStructureType")
    employee_id=fields.Many2one('hr.employee',string='Employee',tracking=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    department_id=fields.Many2one('hr.department',compute='_compute_employee_contract',store=True,readonly=False,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",string="Department")
    job_id=fields.Many2one('hr.job',compute='_compute_employee_contract',store=True,readonly=False,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",string='JobPosition')
    date_start=fields.Date('StartDate',required=True,default=fields.Date.today,tracking=True,
        help="Startdateofthecontract.")
    date_end=fields.Date('EndDate',tracking=True,
        help="Enddateofthecontract(ifit'safixed-termcontract).")
    trial_date_end=fields.Date('EndofTrialPeriod',
        help="Enddateofthetrialperiod(ifthereisone).")
    resource_calendar_id=fields.Many2one(
        'resource.calendar','WorkingSchedule',compute='_compute_employee_contract',store=True,readonly=False,
        default=lambdaself:self.env.company.resource_calendar_id.id,copy=False,index=True,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    wage=fields.Monetary('Wage',required=True,tracking=True,help="Employee'smonthlygrosswage.")
    notes=fields.Text('Notes')
    state=fields.Selection([
        ('draft','New'),
        ('open','Running'),
        ('close','Expired'),
        ('cancel','Cancelled')
    ],string='Status',group_expand='_expand_states',copy=False,
       tracking=True,help='Statusofthecontract',default='draft')
    company_id=fields.Many2one('res.company',compute='_compute_employee_contract',store=True,readonly=False,
        default=lambdaself:self.env.company,required=True)
    company_country_id=fields.Many2one('res.country',string="Companycountry",related='company_id.country_id',readonly=True)

    """
        kanban_state:
            *draft+green="Incoming"state(willbesetasOpenoncethecontracthasstarted)
            *open+red="Pending"state(willbesetasClosedoncethecontracthasended)
            *red=Showsawarningontheemployeeskanbanview
    """
    kanban_state=fields.Selection([
        ('normal','Grey'),
        ('done','Green'),
        ('blocked','Red')
    ],string='KanbanState',default='normal',tracking=True,copy=False)
    currency_id=fields.Many2one(string="Currency",related='company_id.currency_id',readonly=True)
    permit_no=fields.Char('WorkPermitNo',related="employee_id.permit_no",readonly=False)
    visa_no=fields.Char('VisaNo',related="employee_id.visa_no",readonly=False)
    visa_expire=fields.Date('VisaExpireDate',related="employee_id.visa_expire",readonly=False)
    hr_responsible_id=fields.Many2one('res.users','HRResponsible',tracking=True,
        help='Personresponsibleforvalidatingtheemployee\'scontracts.')
    calendar_mismatch=fields.Boolean(compute='_compute_calendar_mismatch')
    first_contract_date=fields.Date(related='employee_id.first_contract_date')

    @api.depends('employee_id.resource_calendar_id','resource_calendar_id')
    def_compute_calendar_mismatch(self):
        forcontractinself:
            contract.calendar_mismatch=contract.resource_calendar_id!=contract.employee_id.resource_calendar_id

    def_expand_states(self,states,domain,order):
        return[keyforkey,valinself._fields['state'].selection]

    @api.depends('employee_id')
    def_compute_employee_contract(self):
        forcontractinself.filtered('employee_id'):
            contract.job_id=contract.employee_id.job_id
            contract.department_id=contract.employee_id.department_id
            contract.resource_calendar_id=contract.employee_id.resource_calendar_id
            contract.company_id=contract.employee_id.company_id

    @api.onchange('company_id')
    def_onchange_company_id(self):
        ifself.company_id:
            structure_types=self.env['hr.payroll.structure.type'].search([
                '|',
                ('country_id','=',self.company_id.country_id.id),
                ('country_id','=',False)])
            ifstructure_types:
                self.structure_type_id=structure_types[0]
            elifself.structure_type_idnotinstructure_types:
                self.structure_type_id=False

    @api.onchange('structure_type_id')
    def_onchange_structure_type_id(self):
        ifself.structure_type_id.default_resource_calendar_id:
            self.resource_calendar_id=self.structure_type_id.default_resource_calendar_id

    @api.constrains('employee_id','state','kanban_state','date_start','date_end')
    def_check_current_contract(self):
        """Twocontractsinstate[incoming|open|close]cannotoverlap"""
        forcontractinself.filtered(lambdac:(c.statenotin['draft','cancel']orc.state=='draft'andc.kanban_state=='done')andc.employee_id):
            domain=[
                ('id','!=',contract.id),
                ('employee_id','=',contract.employee_id.id),
                ('company_id','=',contract.company_id.id),
                '|',
                    ('state','in',['open','close']),
                    '&',
                        ('state','=','draft'),
                        ('kanban_state','=','done')#replacesincoming
            ]

            ifnotcontract.date_end:
                start_domain=[]
                end_domain=['|',('date_end','>=',contract.date_start),('date_end','=',False)]
            else:
                start_domain=[('date_start','<=',contract.date_end)]
                end_domain=['|',('date_end','>',contract.date_start),('date_end','=',False)]

            domain=expression.AND([domain,start_domain,end_domain])
            ifself.search_count(domain):
                raiseValidationError(_('Anemployeecanonlyhaveonecontractatthesametime.(ExcludingDraftandCancelledcontracts)'))

    @api.constrains('date_start','date_end')
    def_check_dates(self):
        ifself.filtered(lambdac:c.date_endandc.date_start>c.date_end):
            raiseValidationError(_('Contractstartdatemustbeearlierthancontractenddate.'))

    @api.model
    defupdate_state(self):
        from_cron='from_cron'inself.env.context
        contracts=self.search([
            ('state','=','open'),('kanban_state','!=','blocked'),
            '|',
            '&',
            ('date_end','<=',fields.Date.to_string(date.today()+relativedelta(days=7))),
            ('date_end','>=',fields.Date.to_string(date.today()+relativedelta(days=1))),
            '&',
            ('visa_expire','<=',fields.Date.to_string(date.today()+relativedelta(days=60))),
            ('visa_expire','>=',fields.Date.to_string(date.today()+relativedelta(days=1))),
        ])

        forcontractincontracts:
            contract.activity_schedule(
                'mail.mail_activity_data_todo',contract.date_end,
                _("Thecontractof%sisabouttoexpire.",contract.employee_id.name),
                user_id=contract.hr_responsible_id.idorself.env.uid)

        ifcontracts:
            contracts._safe_write_for_cron({'kanban_state':'blocked'},from_cron)

        contracts_to_close=self.search([
            ('state','=','open'),
            '|',
            ('date_end','<=',fields.Date.to_string(date.today())),
            ('visa_expire','<=',fields.Date.to_string(date.today())),
        ])

        ifcontracts_to_close:
            contracts_to_close._safe_write_for_cron({'state':'close'},from_cron)

        contracts_to_open=self.search([('state','=','draft'),('kanban_state','=','done'),('date_start','<=',fields.Date.to_string(date.today())),])

        ifcontracts_to_open:
            contracts_to_open._safe_write_for_cron({'state':'open'},from_cron)

        contract_ids=self.search([('date_end','=',False),('state','=','close'),('employee_id','!=',False)])
        #Ensureallclosedcontractfollowedbyanewcontracthaveaenddate.
        #Ifclosedcontracthasnocloseddate,theworkentrieswillbegeneratedforanunlimitedperiod.
        forcontractincontract_ids:
            next_contract=self.search([
                ('employee_id','=',contract.employee_id.id),
                ('state','notin',['cancel','draft']),
                ('date_start','>',contract.date_start)
            ],order="date_startasc",limit=1)
            ifnext_contract:
                contract._safe_write_for_cron({'date_end':next_contract.date_start-relativedelta(days=1)},from_cron)
                continue
            next_contract=self.search([
                ('employee_id','=',contract.employee_id.id),
                ('date_start','>',contract.date_start)
            ],order="date_startasc",limit=1)
            ifnext_contract:
                contract._safe_write_for_cron({'date_end':next_contract.date_start-relativedelta(days=1)},from_cron)

        returnTrue

    def_safe_write_for_cron(self,vals,from_cron=False):
        iffrom_cron:
            auto_commit=notgetattr(threading.current_thread(),'testing',False)
            forcontractinself:
                try:
                    withself.env.cr.savepoint():
                        contract.write(vals)
                exceptValidationErrorase:
                    _logger.warning(e)
                else:
                    ifauto_commit:
                        self.env.cr.commit()
        else:
            self.write(vals)

    def_assign_open_contract(self):
        forcontractinself:
            contract.employee_id.sudo().write({'contract_id':contract.id})

    def_get_contract_wage(self):
        self.ensure_one()
        returnself[self._get_contract_wage_field()]

    def_get_contract_wage_field(self):
        self.ensure_one()
        return'wage'

    defwrite(self,vals):
        res=super(Contract,self).write(vals)
        ifvals.get('state')=='open':
            self._assign_open_contract()
        ifvals.get('state')=='close':
            forcontractinself.filtered(lambdac:notc.date_end):
                contract.date_end=max(date.today(),contract.date_start)

        calendar=vals.get('resource_calendar_id')
        ifcalendar:
            self.filtered(lambdac:c.state=='open'or(c.state=='draft'andc.kanban_state=='done')).mapped('employee_id').write({'resource_calendar_id':calendar})

        if'state'invalsand'kanban_state'notinvals:
            self.write({'kanban_state':'normal'})

        returnres

    @api.model
    defcreate(self,vals):
        contracts=super(Contract,self).create(vals)
        ifvals.get('state')=='open':
            contracts._assign_open_contract()
        open_contracts=contracts.filtered(lambdac:c.state=='open'orc.state=='draft'andc.kanban_state=='done')
        #synccontractcalendar->calendaremployee
        forcontractinopen_contracts.filtered(lambdac:c.employee_idandc.resource_calendar_id):
            contract.employee_id.resource_calendar_id=contract.resource_calendar_id
        returncontracts

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'state'ininit_valuesandself.state=='open'and'kanban_state'ininit_valuesandself.kanban_state=='blocked':
            returnself.env.ref('hr_contract.mt_contract_pending')
        elif'state'ininit_valuesandself.state=='close':
            returnself.env.ref('hr_contract.mt_contract_close')
        returnsuper(Contract,self)._track_subtype(init_values)
