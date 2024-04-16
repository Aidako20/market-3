#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#Copyright(c)2005-2006AxelorSARL.(http://www.axelor.com)

importlogging

fromdatetimeimportdatetime,time
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models
fromflectra.addons.resource.models.resourceimportHOURS_PER_DAY
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.tools.translateimport_
fromflectra.tools.float_utilsimportfloat_round
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)


classHolidaysAllocation(models.Model):
    """AllocationRequestsAccessspecifications:similartoleaverequests"""
    _name="hr.leave.allocation"
    _description="TimeOffAllocation"
    _order="create_datedesc"
    _inherit=['mail.thread','mail.activity.mixin']
    _mail_post_access='read'

    def_default_holiday_status_id(self):
        ifself.user_has_groups('hr_holidays.group_hr_holidays_user'):
            domain=[('valid','=',True)]
        else:
            domain=[('valid','=',True),('allocation_type','=','fixed_allocation')]
        returnself.env['hr.leave.type'].search(domain,limit=1)

    def_holiday_status_id_domain(self):
        ifself.user_has_groups('hr_holidays.group_hr_holidays_manager'):
            return[('valid','=',True),('allocation_type','!=','no')]
        return[('valid','=',True),('allocation_type','=','fixed_allocation')]

    name=fields.Char('Description',compute='_compute_description',inverse='_inverse_description',search='_search_description',compute_sudo=False)
    private_name=fields.Char('AllocationDescription',groups='hr_holidays.group_hr_holidays_user')
    state=fields.Selection([
        ('draft','ToSubmit'),
        ('cancel','Cancelled'),
        ('confirm','ToApprove'),
        ('refuse','Refused'),
        ('validate1','SecondApproval'),
        ('validate','Approved')
        ],string='Status',readonly=True,tracking=True,copy=False,default='confirm',
        help="Thestatusissetto'ToSubmit',whenanallocationrequestiscreated."+
        "\nThestatusis'ToApprove',whenanallocationrequestisconfirmedbyuser."+
        "\nThestatusis'Refused',whenanallocationrequestisrefusedbymanager."+
        "\nThestatusis'Approved',whenanallocationrequestisapprovedbymanager.")
    date_from=fields.Datetime(
        'StartDate',readonly=True,index=True,copy=False,default=fields.Date.context_today,
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]},tracking=True)
    date_to=fields.Datetime(
        'EndDate',compute='_compute_from_holiday_status_id',store=True,readonly=False,copy=False,tracking=True,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    holiday_status_id=fields.Many2one(
        "hr.leave.type",compute='_compute_from_employee_id',store=True,string="TimeOffType",required=True,readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]},
        domain=_holiday_status_id_domain)
    employee_id=fields.Many2one(
        'hr.employee',compute='_compute_from_holiday_type',store=True,string='Employee',index=True,readonly=False,ondelete="restrict",tracking=True,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    manager_id=fields.Many2one('hr.employee',compute='_compute_from_employee_id',store=True,string='Manager')
    notes=fields.Text('Reasons',readonly=True,states={'draft':[('readonly',False)],'confirm':[('readonly',False)]})
    #duration
    number_of_days=fields.Float(
        'NumberofDays',compute='_compute_from_holiday_status_id',store=True,readonly=False,tracking=True,default=1,
        help='Durationindays.Referencefieldtousewhennecessary.')
    number_of_days_display=fields.Float(
        'Duration(days)',compute='_compute_number_of_days_display',
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]},
        help="IfAccrualAllocation:Numberofdaysallocatedinadditiontotheonesyouwillgetviatheaccrual'system.")
    number_of_hours_display=fields.Float(
        'Duration(hours)',compute='_compute_number_of_hours_display',
        help="IfAccrualAllocation:Numberofhoursallocatedinadditiontotheonesyouwillgetviatheaccrual'system.")
    duration_display=fields.Char('Allocated(Days/Hours)',compute='_compute_duration_display',
        help="Fieldallowingtoseetheallocationdurationindaysorhoursdependingonthetype_request_unit")
    #details
    parent_id=fields.Many2one('hr.leave.allocation',string='Parent')
    linked_request_ids=fields.One2many('hr.leave.allocation','parent_id',string='LinkedRequests')
    first_approver_id=fields.Many2one(
        'hr.employee',string='FirstApproval',readonly=True,copy=False,
        help='Thisareaisautomaticallyfilledbytheuserwhovalidatestheallocation')
    second_approver_id=fields.Many2one(
        'hr.employee',string='SecondApproval',readonly=True,copy=False,
        help='Thisareaisautomaticallyfilledbytheuserwhovalidatestheallocationwithsecondlevel(Ifallocationtypeneedsecondvalidation)')
    validation_type=fields.Selection(string='ValidationType',related='holiday_status_id.allocation_validation_type',readonly=True)
    can_reset=fields.Boolean('Canreset',compute='_compute_can_reset')
    can_approve=fields.Boolean('CanApprove',compute='_compute_can_approve')
    type_request_unit=fields.Selection(related='holiday_status_id.request_unit',readonly=True)
    #mode
    holiday_type=fields.Selection([
        ('employee','ByEmployee'),
        ('company','ByCompany'),
        ('department','ByDepartment'),
        ('category','ByEmployeeTag')],
        string='AllocationMode',readonly=True,required=True,default='employee',
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]},
        help="Allowtocreaterequestsinbatchs:\n-ByEmployee:foraspecificemployee"
             "\n-ByCompany:allemployeesofthespecifiedcompany"
             "\n-ByDepartment:allemployeesofthespecifieddepartment"
             "\n-ByEmployeeTag:allemployeesofthespecificemployeegroupcategory")
    mode_company_id=fields.Many2one(
        'res.company',compute='_compute_from_holiday_type',store=True,string='CompanyMode',readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    department_id=fields.Many2one(
        'hr.department',compute='_compute_department_id',store=True,string='Department',
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]})
    category_id=fields.Many2one(
        'hr.employee.category',compute='_compute_from_holiday_type',store=True,string='EmployeeTag',readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    #accrualconfiguration
    allocation_type=fields.Selection(
        [
            ('regular','RegularAllocation'),
            ('accrual','AccrualAllocation')
        ],string="AllocationType",default="regular",required=True,readonly=True,
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]})
    accrual_limit=fields.Integer('Balancelimit',default=0,help="Maximumofallocationforaccrual;0meansnomaximum.")
    number_per_interval=fields.Float("Numberofunitperinterval",compute='_compute_from_holiday_status_id',store=True,readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    interval_number=fields.Integer("Numberofunitbetweentwointervals",compute='_compute_from_holiday_status_id',store=True,readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    unit_per_interval=fields.Selection([
        ('hours','Hours'),
        ('days','Days')
        ],compute='_compute_from_holiday_status_id',store=True,string="Unitoftimeaddedateachinterval",readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    interval_unit=fields.Selection([
        ('days','Days'),
        ('weeks','Weeks'),
        ('months','Months'),
        ('years','Years')
        ],compute='_compute_from_holiday_status_id',store=True,string="Unitoftimebetweentwointervals",readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    nextcall=fields.Date("Dateofthenextaccrualallocation",default=False,readonly=True)
    max_leaves=fields.Float(compute='_compute_leaves')
    leaves_taken=fields.Float(compute='_compute_leaves')

    _sql_constraints=[
        ('type_value',
         "CHECK((holiday_type='employee'ANDemployee_idISNOTNULL)or"
         "(holiday_type='category'ANDcategory_idISNOTNULL)or"
         "(holiday_type='department'ANDdepartment_idISNOTNULL)or"
         "(holiday_type='company'ANDmode_company_idISNOTNULL))",
         "Theemployee,department,companyoremployeecategoryofthisrequestismissing.Pleasemakesurethatyouruserloginislinkedtoanemployee."),
        ('duration_check',"CHECK(number_of_days>=0)","Thenumberofdaysmustbegreaterthan0."),
        ('number_per_interval_check',"CHECK(number_per_interval>0)","Thenumberperintervalshouldbegreaterthan0"),
        ('interval_number_check',"CHECK(interval_number>0)","Theintervalnumbershouldbegreaterthan0"),
    ]

    @api.model
    def_update_accrual(self):
        """
            Methodcalledbythecrontaskinordertoincrementthenumber_of_dayswhen
            necessary.
        """
        today=fields.Date.from_string(fields.Date.today())

        holidays=self.search([('allocation_type','=','accrual'),('employee_id.active','=',True),('state','=','validate'),('holiday_type','=','employee'),
                                '|',('date_to','=',False),('date_to','>',fields.Datetime.now()),
                                '|',('nextcall','=',False),('nextcall','<=',today)])

        forholidayinholidays:
            values={}

            delta=relativedelta(days=0)

            ifholiday.interval_unit=='days':
                delta=relativedelta(days=holiday.interval_number)
            ifholiday.interval_unit=='weeks':
                delta=relativedelta(weeks=holiday.interval_number)
            ifholiday.interval_unit=='months':
                delta=relativedelta(months=holiday.interval_number)
            ifholiday.interval_unit=='years':
                delta=relativedelta(years=holiday.interval_number)

            ifholiday.nextcall:
                values['nextcall']=holiday.nextcall+delta
            else:
                values['nextcall']=holiday.date_from
                whilevalues['nextcall']<=datetime.combine(today,time(0,0,0)):
                    values['nextcall']+=delta

            period_start=datetime.combine(today,time(0,0,0))-delta
            period_end=datetime.combine(today,time(0,0,0))

            #Wehavetocheckwhentheemployeehasbeencreated
            #inordertonotallocatehim/hertoomuchleaves
            start_date=holiday.employee_id._get_date_start_work()
            #Ifemployeeiscreatedaftertheperiod,wecancelthecomputation
            ifperiod_end<=start_dateorperiod_end<holiday.date_from:
                holiday.write(values)
                continue

            #Ifemployeecreatedduringtheperiod,takingthedateatwhichhehasbeencreated
            ifperiod_start<=start_date:
                period_start=start_date

            employee=holiday.employee_id
            worked=employee._get_work_days_data_batch(
                period_start,period_end,
                domain=[('holiday_id.holiday_status_id.unpaid','=',True),('time_type','=','leave')]
            )[employee.id]['days']
            left=employee._get_leave_days_data_batch(
                period_start,period_end,
                domain=[('holiday_id.holiday_status_id.unpaid','=',True),('time_type','=','leave')]
            )[employee.id]['days']
            prorata=worked/(left+worked)ifworkedelse0

            days_to_give=holiday.number_per_interval
            ifholiday.unit_per_interval=='hours':
                #Asweencodeeverythingindaysinthedatabaseweneedtoconvert
                #thenumberofhoursintodaysforthisweusethe
                #meannumberofhourssetontheemployee'scalendar
                days_to_give=days_to_give/(employee.resource_calendar_id.hours_per_dayorHOURS_PER_DAY)

            values['number_of_days']=holiday.number_of_days+days_to_give*prorata
            ifholiday.accrual_limit>0:
                values['number_of_days']=min(values['number_of_days'],holiday.accrual_limit)

            holiday.write(values)

    @api.depends_context('uid')
    def_compute_description(self):
        self.check_access_rights('read')
        self.check_access_rule('read')

        is_officer=self.env.user.has_group('hr_holidays.group_hr_holidays_user')

        forallocationinself:
            ifis_officerorallocation.employee_id.user_id==self.env.userorallocation.manager_id==self.env.user:
                allocation.name=allocation.sudo().private_name
            else:
                allocation.name='*****'

    def_inverse_description(self):
        is_officer=self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        forallocationinself:
            ifis_officerorallocation.employee_id.user_id==self.env.userorallocation.manager_id==self.env.user:
                allocation.sudo().private_name=allocation.name

    def_search_description(self,operator,value):
        is_officer=self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        domain=[('private_name',operator,value)]

        ifnotis_officer:
            domain=expression.AND([domain,[('employee_id.user_id','=',self.env.user.id)]])

        allocations=self.sudo().search(domain)
        return[('id','in',allocations.ids)]

    @api.depends('employee_id','holiday_status_id')
    def_compute_leaves(self):
        forallocationinself:
            leave_type=allocation.holiday_status_id.with_context(employee_id=allocation.employee_id.id)
            allocation.max_leaves=leave_type.max_leaves
            allocation.leaves_taken=leave_type.leaves_taken

    @api.depends('number_of_days')
    def_compute_number_of_days_display(self):
        forallocationinself:
            allocation.number_of_days_display=allocation.number_of_days

    @api.depends('number_of_days','employee_id')
    def_compute_number_of_hours_display(self):
        forallocationinself:
            ifallocation.parent_idandallocation.parent_id.type_request_unit=="hour":
                allocation.number_of_hours_display=allocation.number_of_days*HOURS_PER_DAY
            elifallocation.number_of_days:
                allocation.number_of_hours_display=allocation.number_of_days*(allocation.employee_id.sudo().resource_id.calendar_id.hours_per_dayorHOURS_PER_DAY)
            else:
                allocation.number_of_hours_display=0.0

    @api.depends('number_of_hours_display','number_of_days_display')
    def_compute_duration_display(self):
        forallocationinself:
            allocation.duration_display='%g%s'%(
                (float_round(allocation.number_of_hours_display,precision_digits=2)
                ifallocation.type_request_unit=='hour'
                elsefloat_round(allocation.number_of_days_display,precision_digits=2)),
                _('hours')ifallocation.type_request_unit=='hour'else_('days'))

    @api.depends('state','employee_id','department_id')
    def_compute_can_reset(self):
        forallocationinself:
            try:
                allocation._check_approval_update('draft')
            except(AccessError,UserError):
                allocation.can_reset=False
            else:
                allocation.can_reset=True

    @api.depends('state','employee_id','department_id')
    def_compute_can_approve(self):
        forallocationinself:
            try:
                ifallocation.state=='confirm'andallocation.holiday_status_id.allocation_type=="fixed_allocation"andallocation.validation_type=='both':
                    allocation._check_approval_update('validate1')
                else:
                    allocation._check_approval_update('validate')
            except(AccessError,UserError):
                allocation.can_approve=False
            else:
                allocation.can_approve=True

    @api.depends('holiday_type')
    def_compute_from_holiday_type(self):
        forallocationinself:
            ifallocation.holiday_type=='employee':
                ifnotallocation.employee_id:
                    allocation.employee_id=self.env.user.employee_id
                allocation.mode_company_id=False
                allocation.category_id=False
            ifallocation.holiday_type=='company':
                allocation.employee_id=False
                ifnotallocation.mode_company_id:
                    allocation.mode_company_id=self.env.company
                allocation.category_id=False
            elifallocation.holiday_type=='department':
                allocation.employee_id=False
                allocation.mode_company_id=False
                allocation.category_id=False
            elifallocation.holiday_type=='category':
                allocation.employee_id=False
                allocation.mode_company_id=False
            elifnotallocation.employee_idandnotallocation._origin.employee_id:
                allocation.employee_id=self.env.context.get('default_employee_id')orself.env.user.employee_id

    @api.depends('holiday_type','employee_id')
    def_compute_department_id(self):
        forallocationinself:
            ifallocation.holiday_type=='employee':
                allocation.department_id=allocation.employee_id.department_id
            elifallocation.holiday_type=='department':
                ifnotallocation.department_id:
                    allocation.department_id=self.env.user.employee_id.department_id
            elifallocation.holiday_type=='category':
                allocation.department_id=False

    @api.depends('employee_id')
    def_compute_from_employee_id(self):
        default_holiday_status_id=self._default_holiday_status_id()
        forholidayinself:
            holiday.manager_id=holiday.employee_idandholiday.employee_id.parent_id
            ifholiday.employee_id.user_id!=self.env.userandholiday._origin.employee_id!=holiday.employee_id:
                holiday.holiday_status_id=False
            elifnotholiday.holiday_status_idandnotholiday._origin.holiday_status_id:
                holiday.holiday_status_id=default_holiday_status_id

    @api.depends('holiday_status_id','allocation_type','number_of_hours_display','number_of_days_display')
    def_compute_from_holiday_status_id(self):
        forallocationinself:
            allocation.number_of_days=allocation.number_of_days_display
            ifallocation.type_request_unit=='hour':
                allocation.number_of_days=allocation.number_of_hours_display/(allocation.employee_id.sudo().resource_calendar_id.hours_per_dayorHOURS_PER_DAY)

            #setdefaultvalues
            ifnotallocation.interval_numberandnotallocation._origin.interval_number:
                allocation.interval_number=1
            ifnotallocation.number_per_intervalandnotallocation._origin.number_per_interval:
                allocation.number_per_interval=1
            ifnotallocation.unit_per_intervalandnotallocation._origin.unit_per_interval:
                allocation.unit_per_interval='hours'
            ifnotallocation.interval_unitandnotallocation._origin.interval_unit:
                allocation.interval_unit='weeks'

            ifallocation.holiday_status_id.validity_stopandallocation.date_to:
                new_date_to=datetime.combine(allocation.holiday_status_id.validity_stop,time.max)
                ifnew_date_to<allocation.date_to:
                    allocation.date_to=new_date_to

            ifallocation.allocation_type=='accrual':
                ifallocation.holiday_status_id.request_unit=='hour':
                    allocation.unit_per_interval='hours'
                else:
                    allocation.unit_per_interval='days'
            else:
                allocation.interval_number=1
                allocation.interval_unit='weeks'
                allocation.number_per_interval=1
                allocation.unit_per_interval='hours'

    ####################################################
    #ORMOverridesmethods
    ####################################################

    defname_get(self):
        res=[]
        forallocationinself:
            ifallocation.holiday_type=='company':
                target=allocation.mode_company_id.name
            elifallocation.holiday_type=='department':
                target=allocation.department_id.name
            elifallocation.holiday_type=='category':
                target=allocation.category_id.name
            else:
                target=allocation.employee_id.sudo().name

            res.append(
                (allocation.id,
                 _("Allocationof%(allocation_name)s:%(duration).2f%(duration_type)sto%(person)s",
                   allocation_name=allocation.holiday_status_id.sudo().name,
                   duration=allocation.number_of_hours_displayifallocation.type_request_unit=='hour'elseallocation.number_of_days,
                   duration_type='hours'ifallocation.type_request_unit=='hour'else'days',
                   person=target
                ))
            )
        returnres

    defadd_follower(self,employee_id):
        employee=self.env['hr.employee'].browse(employee_id)
        ifemployee.user_id:
            self.message_subscribe(partner_ids=employee.user_id.partner_id.ids)

    @api.constrains('holiday_status_id')
    def_check_leave_type_validity(self):
        forallocationinself:
            ifallocation.holiday_status_id.validity_stop:
                vstop=allocation.holiday_status_id.validity_stop
                today=fields.Date.today()

                ifvstop<today:
                    raiseValidationError(_(
                        'Youcanallocate%(allocation_type)sonlybefore%(date)s.',
                        allocation_type=allocation.holiday_status_id.display_name,
                        date=allocation.holiday_status_id.validity_stop
                    ))

    @api.model
    defcreate(self,values):
        """Overridetoavoidautomaticloggingofcreation"""
        employee_id=values.get('employee_id',False)
        ifnotvalues.get('department_id'):
            values.update({'department_id':self.env['hr.employee'].browse(employee_id).department_id.id})
        holiday=super(HolidaysAllocation,self.with_context(mail_create_nosubscribe=True)).create(values)
        holiday.add_follower(employee_id)
        ifholiday.validation_type=='hr':
            holiday.message_subscribe(partner_ids=(holiday.employee_id.parent_id.user_id.partner_id|holiday.employee_id.leave_manager_id.partner_id).ids)
        ifnotself._context.get('import_file'):
            holiday.activity_update()
        returnholiday

    defwrite(self,values):
        employee_id=values.get('employee_id',False)
        ifvalues.get('state'):
            self._check_approval_update(values['state'])
        result=super(HolidaysAllocation,self).write(values)
        self.add_follower(employee_id)
        returnresult

    defunlink(self):
        state_description_values={elem[0]:elem[1]foreleminself._fields['state']._description_selection(self.env)}
        forholidayinself.filtered(lambdaholiday:holiday.statenotin['draft','cancel','confirm']):
            raiseUserError(_('Youcannotdeleteanallocationrequestwhichisin%sstate.')%(state_description_values.get(holiday.state),))
        returnsuper(HolidaysAllocation,self).unlink()

    def_get_mail_redirect_suggested_company(self):
        returnself.holiday_status_id.company_id

    ####################################################
    #Businessmethods
    ####################################################

    def_prepare_holiday_values(self,employee):
        self.ensure_one()
        values={
            'name':self.name,
            'holiday_type':'employee',
            'holiday_status_id':self.holiday_status_id.id,
            'notes':self.notes,
            'number_of_days':self.number_of_days,
            'parent_id':self.id,
            'employee_id':employee.id,
            'allocation_type':self.allocation_type,
            'date_from':self.date_from,
            'date_to':self.date_to,
            'interval_unit':self.interval_unit,
            'interval_number':self.interval_number,
            'number_per_interval':self.number_per_interval,
            'unit_per_interval':self.unit_per_interval,
        }
        returnvalues

    defaction_draft(self):
        ifany(holiday.statenotin['confirm','refuse']forholidayinself):
            raiseUserError(_('Allocationrequeststatemustbe"Refused"or"ToApprove"inordertoberesettoDraft.'))
        self.write({
            'state':'draft',
            'first_approver_id':False,
            'second_approver_id':False,
        })
        linked_requests=self.mapped('linked_request_ids')
        iflinked_requests:
            linked_requests.action_draft()
            linked_requests.unlink()
        self.activity_update()
        returnTrue

    defaction_confirm(self):
        ifself.filtered(lambdaholiday:holiday.state!='draft'):
            raiseUserError(_('AllocationrequestmustbeinDraftstate("ToSubmit")inordertoconfirmit.'))
        res=self.write({'state':'confirm'})
        self.activity_update()
        returnres

    defaction_approve(self):
        #ifvalidation_type=='both':thismethodisthefirstapprovalapproval
        #ifvalidation_type!='both':thismethodcallsaction_validate()below
        ifany(holiday.state!='confirm'forholidayinself):
            raiseUserError(_('Allocationrequestmustbeconfirmed("ToApprove")inordertoapproveit.'))

        current_employee=self.env.user.employee_id

        self.filtered(lambdahol:hol.validation_type=='both').write({'state':'validate1','first_approver_id':current_employee.id})
        self.filtered(lambdahol:nothol.validation_type=='both').action_validate()
        self.activity_update()

    defaction_validate(self):
        current_employee=self.env.user.employee_id
        forholidayinself:
            ifholiday.statenotin['confirm','validate1']:
                raiseUserError(_('Allocationrequestmustbeconfirmedinordertoapproveit.'))

            holiday.write({'state':'validate'})
            ifholiday.validation_type=='both':
                holiday.write({'second_approver_id':current_employee.id})
            else:
                holiday.write({'first_approver_id':current_employee.id})

            holiday._action_validate_create_childs()
        self.activity_update()
        returnTrue

    def_action_validate_create_childs(self):
        childs=self.env['hr.leave.allocation']
        ifself.state=='validate'andself.holiday_typein['category','department','company']:
            ifself.holiday_type=='category':
                employees=self.category_id.employee_ids
            elifself.holiday_type=='department':
                employees=self.department_id.member_ids
            else:
                employees=self.env['hr.employee'].search([('company_id','=',self.mode_company_id.id)])

            foremployeeinemployees:
                childs+=self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))
            #TODOisitnecessarytointerleavethecalls?
            childs.action_approve()
            ifchildsandself.validation_type=='both':
                childs.action_validate()
        returnchilds

    defaction_refuse(self):
        current_employee=self.env.user.employee_id
        ifany(holiday.statenotin['confirm','validate','validate1']forholidayinself):
            raiseUserError(_('Allocationrequestmustbeconfirmedorvalidatedinordertorefuseit.'))

        validated_holidays=self.filtered(lambdahol:hol.state=='validate1')
        validated_holidays.write({'state':'refuse','first_approver_id':current_employee.id})
        (self-validated_holidays).write({'state':'refuse','second_approver_id':current_employee.id})
        #Ifacategorythatcreatedseveralholidays,cancelallrelated
        linked_requests=self.mapped('linked_request_ids')
        iflinked_requests:
            linked_requests.action_refuse()
        self.activity_update()
        returnTrue

    def_check_approval_update(self,state):
        """Checkiftargetstateisachievable."""
        ifself.env.is_superuser():
            return
        current_employee=self.env.user.employee_id
        ifnotcurrent_employee:
            return
        is_officer=self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager=self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        forholidayinself:
            val_type=holiday.holiday_status_id.sudo().allocation_validation_type
            ifstate=='confirm':
                continue

            ifstate=='draft':
                ifholiday.employee_id!=current_employeeandnotis_manager:
                    raiseUserError(_('OnlyatimeoffManagercanresetotherpeopleallocation.'))
                continue

            ifnotis_officerandself.env.user!=holiday.employee_id.leave_manager_id:
                raiseUserError(_('OnlyatimeoffOfficer/ResponsibleorManagercanapproveorrefusetimeoffrequests.'))

            ifis_officerorself.env.user==holiday.employee_id.leave_manager_id:
                #useir.rulebasedfirstaccesscheck:department,members,...(seesecurity.xml)
                holiday.check_access_rule('write')

            ifholiday.employee_id==current_employeeandnotis_manager:
                raiseUserError(_('OnlyatimeoffManagercanapproveitsownrequests.'))

            if(state=='validate1'andval_type=='both')or(state=='validate'andval_type=='manager'):
                ifself.env.user==holiday.employee_id.leave_manager_idandself.env.user!=holiday.employee_id.user_id:
                    continue
                manager=holiday.employee_id.parent_idorholiday.employee_id.department_id.manager_id
                if(manager!=current_employee)andnotis_manager:
                    raiseUserError(_('Youmustbeeither%s\'smanagerortimeoffmanagertoapprovethistimeoff')%(holiday.employee_id.name))

            ifstate=='validate'andval_type=='both':
                ifnotis_officer:
                    raiseUserError(_('OnlyaTimeoffApprovercanapplythesecondapprovalonallocationrequests.'))

    #------------------------------------------------------------
    #Activitymethods
    #------------------------------------------------------------

    def_get_responsible_for_approval(self):
        self.ensure_one()
        responsible=self.env.user

        ifself.validation_type=='manager'or(self.validation_type=='both'andself.state=='confirm'):
            ifself.employee_id.leave_manager_id:
                responsible=self.employee_id.leave_manager_id
            elifself.employee_id.parent_id.user_id:
                responsible=self.employee_id.parent_id.user_id
        elifself.validation_type=='hr'or(self.validation_type=='both'andself.state=='validate1'):
            ifself.holiday_status_id.responsible_id:
                responsible=self.holiday_status_id.responsible_id

        returnresponsible

    defactivity_update(self):
        to_clean,to_do=self.env['hr.leave.allocation'],self.env['hr.leave.allocation']
        forallocationinself:
            note=_(
                'NewAllocationRequestcreatedby%(user)s:%(count)sDaysof%(allocation_type)s',
                user=allocation.create_uid.name,
                count=allocation.number_of_days,
                allocation_type=allocation.holiday_status_id.name
            )
            ifallocation.state=='draft':
                to_clean|=allocation
            elifallocation.state=='confirm':
                allocation.activity_schedule(
                    'hr_holidays.mail_act_leave_allocation_approval',
                    note=note,
                    user_id=allocation.sudo()._get_responsible_for_approval().idorself.env.user.id)
            elifallocation.state=='validate1':
                allocation.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval'])
                allocation.activity_schedule(
                    'hr_holidays.mail_act_leave_allocation_second_approval',
                    note=note,
                    user_id=allocation.sudo()._get_responsible_for_approval().idorself.env.user.id)
            elifallocation.state=='validate':
                to_do|=allocation
            elifallocation.state=='refuse':
                to_clean|=allocation
        ifto_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_allocation_approval','hr_holidays.mail_act_leave_allocation_second_approval'])
        ifto_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval','hr_holidays.mail_act_leave_allocation_second_approval'])

    ####################################################
    #Messagingmethods
    ####################################################

    def_track_subtype(self,init_values):
        if'state'ininit_valuesandself.state=='validate':
            allocation_notif_subtype_id=self.holiday_status_id.allocation_notif_subtype_id
            returnallocation_notif_subtype_idorself.env.ref('hr_holidays.mt_leave_allocation')
        returnsuper(HolidaysAllocation,self)._track_subtype(init_values)

    def_notify_get_groups(self,msg_vals=None):
        """HandleHRusersandofficersrecipientsthatcanvalidateorrefuseholidays
        directlyfromemail."""
        groups=super(HolidaysAllocation,self)._notify_get_groups(msg_vals=msg_vals)
        local_msg_vals=dict(msg_valsor{})

        self.ensure_one()
        hr_actions=[]
        ifself.state=='confirm':
            app_action=self._notify_get_action_link('controller',controller='/allocation/validate',**local_msg_vals)
            hr_actions+=[{'url':app_action,'title':_('Approve')}]
        ifself.statein['confirm','validate','validate1']:
            ref_action=self._notify_get_action_link('controller',controller='/allocation/refuse',**local_msg_vals)
            hr_actions+=[{'url':ref_action,'title':_('Refuse')}]

        holiday_user_group_id=self.env.ref('hr_holidays.group_hr_holidays_user').id
        new_group=(
            'group_hr_holidays_user',lambdapdata:pdata['type']=='user'andholiday_user_group_idinpdata['groups'],{
                'actions':hr_actions,
            })

        return[new_group]+groups

    defmessage_subscribe(self,partner_ids=None,channel_ids=None,subtype_ids=None):
        #duetorecordrulecannotallowtoaddfollowerandmentiononvalidatedleavesosubscribethroughsudo
        ifself.statein['validate','validate1']:
            self.check_access_rights('read')
            self.check_access_rule('read')
            returnsuper(HolidaysAllocation,self.sudo()).message_subscribe(partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=subtype_ids)
        returnsuper(HolidaysAllocation,self).message_subscribe(partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=subtype_ids)
