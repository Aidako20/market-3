#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#Copyright(c)2005-2006AxelorSARL.(http://www.axelor.com)

importdatetime
importlogging

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models
fromflectra.exceptionsimportValidationError
fromflectra.osvimportexpression
fromflectra.tools.translateimport_
fromflectra.tools.float_utilsimportfloat_round

_logger=logging.getLogger(__name__)


classHolidaysType(models.Model):
    _name="hr.leave.type"
    _description="TimeOffType"

    @api.model
    def_model_sorting_key(self,leave_type):
        remaining=leave_type.virtual_remaining_leaves>0
        taken=leave_type.leaves_taken>0
        returnleave_type.allocation_type=='fixed'andremaining,leave_type.allocation_type=='fixed_allocation'andremaining,taken

    name=fields.Char('TimeOffType',required=True,translate=True)
    code=fields.Char('Code')
    sequence=fields.Integer(default=100,
                              help='Thetypewiththesmallestsequenceisthedefaultvalueintimeoffrequest')
    create_calendar_meeting=fields.Boolean(string="DisplayTimeOffinCalendar",default=True)
    color_name=fields.Selection([
        ('red','Red'),
        ('blue','Blue'),
        ('lightgreen','LightGreen'),
        ('lightblue','LightBlue'),
        ('lightyellow','LightYellow'),
        ('magenta','Magenta'),
        ('lightcyan','LightCyan'),
        ('black','Black'),
        ('lightpink','LightPink'),
        ('brown','Brown'),
        ('violet','Violet'),
        ('lightcoral','LightCoral'),
        ('lightsalmon','LightSalmon'),
        ('lavender','Lavender'),
        ('wheat','Wheat'),
        ('ivory','Ivory')],string='ColorinReport',required=True,default='red',
        help='ThiscolorwillbeusedinthetimeoffsummarylocatedinReporting>TimeoffbyDepartment.')
    active=fields.Boolean('Active',default=True,
                            help="Iftheactivefieldissettofalse,itwillallowyoutohidethetimeofftypewithoutremovingit.")
    max_leaves=fields.Float(compute='_compute_leaves',string='MaximumAllowed',search='_search_max_leaves',
                              help='Thisvalueisgivenbythesumofalltimeoffrequestswithapositivevalue.')
    leaves_taken=fields.Float(
        compute='_compute_leaves',string='TimeoffAlreadyTaken',
        help='Thisvalueisgivenbythesumofalltimeoffrequestswithanegativevalue.')
    remaining_leaves=fields.Float(
        compute='_compute_leaves',string='RemainingTimeOff',
        help='MaximumTimeOffAllowed-TimeOffAlreadyTaken')
    virtual_remaining_leaves=fields.Float(
        compute='_compute_leaves',search='_search_virtual_remaining_leaves',string='VirtualRemainingTimeOff',
        help='MaximumTimeOffAllowed-TimeOffAlreadyTaken-TimeOffWaitingApproval')
    virtual_leaves_taken=fields.Float(
        compute='_compute_leaves',string='VirtualTimeOffAlreadyTaken',
        help='Sumofvalidatedandnonvalidatedtimeoffrequests.')
    group_days_allocation=fields.Float(
        compute='_compute_group_days_allocation',string='DaysAllocated')
    group_days_leave=fields.Float(
        compute='_compute_group_days_leave',string='GroupTimeOff')
    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company)
    responsible_id=fields.Many2one('res.users','Responsible',
        domain=lambdaself:[('groups_id','in',self.env.ref('hr_holidays.group_hr_holidays_user').id)],
        help="Thisuserwillberesponsibleforapprovingthistypeoftimeoff."
        "Thisisonlyusedwhenvalidationis'ByTimeOffOfficer'or'ByEmployee'sManagerandTimeOffOfficer'",)
    leave_validation_type=fields.Selection([
        ('no_validation','NoValidation'),
        ('hr','ByTimeOffOfficer'),
        ('manager',"ByEmployee'sManager"),
        ('both',"ByEmployee'sManagerandTimeOffOfficer")],default='hr',string='LeaveValidation')
    allocation_validation_type=fields.Selection([
        ('hr','ByTimeOffOfficer'),
        ('manager',"ByEmployee'sManager"),
        ('both',"ByEmployee'sManagerandTimeOffOfficer")],default='manager',string='AllocationValidation')
    allocation_type=fields.Selection([
        ('no','NoLimit'),
        ('fixed_allocation','AllowEmployeesRequests'),
        ('fixed','SetbyTimeOffOfficer')],
        default='no',string='Mode',
        help='\tNoLimit:noallocationbydefault,userscanfreelyrequesttimeoff;'
             '\tAllowEmployeesRequests:allocatedbyHRanduserscanrequesttimeoffandallocations;'
             '\tSetbyTimeOffOfficer:allocatedbyHRandcannotbebypassed;userscanrequesttimeoff;')
    validity_start=fields.Date("From",
                                 help='Addingvaliditytotypesoftimeoffsothatitcannotbeselectedoutsidethistimeperiod')
    validity_stop=fields.Date("To")
    valid=fields.Boolean(compute='_compute_valid',search='_search_valid',help='Thisindicatesifitisstillpossibletousethistypeofleave')
    time_type=fields.Selection([('leave','TimeOff'),('other','Other')],default='leave',string="KindofLeave",
                                 help="Whetherthisshouldbecomputedasaholidayorasworktime(eg:formation)")
    request_unit=fields.Selection([
        ('day','Day'),('half_day','HalfDay'),('hour','Hours')],
        default='day',string='TakeTimeOffin',required=True)
    unpaid=fields.Boolean('IsUnpaid',default=False)
    leave_notif_subtype_id=fields.Many2one('mail.message.subtype',string='TimeOffNotificationSubtype',default=lambdaself:self.env.ref('hr_holidays.mt_leave',raise_if_not_found=False))
    allocation_notif_subtype_id=fields.Many2one('mail.message.subtype',string='AllocationNotificationSubtype',default=lambdaself:self.env.ref('hr_holidays.mt_leave_allocation',raise_if_not_found=False))

    @api.constrains('validity_start','validity_stop')
    def_check_validity_dates(self):
        forleave_typeinself:
            ifleave_type.validity_startandleave_type.validity_stopand\
               leave_type.validity_start>leave_type.validity_stop:
                raiseValidationError(_("Endofvalidityperiodshouldbegreaterthanstartofvalidityperiod"))

    @api.depends('validity_start','validity_stop')
    def_compute_valid(self):
        dt=self._context.get('default_date_from')orfields.Date.context_today(self)

        forholiday_typeinself:
            ifholiday_type.validity_startandholiday_type.validity_stop:
                holiday_type.valid=((dt<holiday_type.validity_stop)and(dt>holiday_type.validity_start))
            elifholiday_type.validity_startand(dt>holiday_type.validity_start):
                holiday_type.valid=False
            else:
                holiday_type.valid=True

    def_search_valid(self,operator,value):
        dt=self._context.get('default_date_from',False)

        ifnotdt:
            return[]
        signs=['>=','<=']ifoperator=='='else['<=','>=']

        return['|',('validity_stop',operator,False),'&',
                ('validity_stop',signs[0]ifvalueelsesigns[1],dt),
                ('validity_start',signs[1]ifvalueelsesigns[0],dt)]

    def_search_max_leaves(self,operator,value):
        value=float(value)
        employee_id=self._get_contextual_employee_id()
        leaves=defaultdict(int)

        ifemployee_id:
            allocations=self.env['hr.leave.allocation'].search([
                ('employee_id','=',employee_id),
                ('state','=','validate')
            ])
            forallocationinallocations:
                leaves[allocation.holiday_status_id.id]+=allocation.number_of_days
        valid_leave=[]
        forleaveinleaves:
            ifoperator=='>':
                ifleaves[leave]>value:
                    valid_leave.append(leave)
            elifoperator=='<':
                ifleaves[leave]<value:
                    valid_leave.append(leave)
            elifoperator=='=':
                ifleaves[leave]==value:
                    valid_leave.append(leave)
            elifoperator=='!=':
                ifleaves[leave]!=value:
                    valid_leave.append(leave)

        return[('id','in',valid_leave)]

    def_search_virtual_remaining_leaves(self,operator,value):
        value=float(value)
        leave_types=self.env['hr.leave.type'].search([])
        valid_leave_types=self.env['hr.leave.type']

        forleave_typeinleave_types:
            ifleave_type.allocation_type!='no':
                ifoperator=='>'andleave_type.virtual_remaining_leaves>value:
                    valid_leave_types|=leave_type
                elifoperator=='<'andleave_type.virtual_remaining_leaves<value:
                    valid_leave_types|=leave_type
                elifoperator=='>='andleave_type.virtual_remaining_leaves>=value:
                    valid_leave_types|=leave_type
                elifoperator=='<='andleave_type.virtual_remaining_leaves<=value:
                    valid_leave_types|=leave_type
                elifoperator=='='andleave_type.virtual_remaining_leaves==value:
                    valid_leave_types|=leave_type
                elifoperator=='!='andleave_type.virtual_remaining_leaves!=value:
                    valid_leave_types|=leave_type
            else:
                valid_leave_types|=leave_type

        return[('id','in',valid_leave_types.ids)]

    #YTITODO:Removemeinmaster
    defget_days(self,employee_id):
        returnself.get_employees_days([employee_id])[employee_id]

    defget_employees_days(self,employee_ids):
        result={
            employee_id:{
                leave_type.id:{
                    'max_leaves':0,
                    'leaves_taken':0,
                    'remaining_leaves':0,
                    'virtual_remaining_leaves':0,
                    'virtual_leaves_taken':0,
                }forleave_typeinself
            }foremployee_idinemployee_ids
        }

        requests=self.env['hr.leave'].search([
            ('employee_id','in',employee_ids),
            ('state','in',['confirm','validate1','validate']),
            ('holiday_status_id','in',self.ids)
        ])

        allocations=self.env['hr.leave.allocation'].search([
            ('employee_id','in',employee_ids),
            ('state','in',['confirm','validate1','validate']),
            ('holiday_status_id','in',self.ids)
        ])

        forrequestinrequests:
            status_dict=result[request.employee_id.id][request.holiday_status_id.id]
            status_dict['virtual_remaining_leaves']-=(request.number_of_hours_display
                                                    ifrequest.leave_type_request_unit=='hour'
                                                    elserequest.number_of_days)
            status_dict['virtual_leaves_taken']+=(request.number_of_hours_display
                                                ifrequest.leave_type_request_unit=='hour'
                                                elserequest.number_of_days)
            ifrequest.state=='validate':
                status_dict['leaves_taken']+=(request.number_of_hours_display
                                            ifrequest.leave_type_request_unit=='hour'
                                            elserequest.number_of_days)
                status_dict['remaining_leaves']-=(request.number_of_hours_display
                                                ifrequest.leave_type_request_unit=='hour'
                                                elserequest.number_of_days)

        forallocationinallocations.sudo():
            status_dict=result[allocation.employee_id.id][allocation.holiday_status_id.id]
            ifallocation.state=='validate':
                #note:addonlyvalidatedallocationevenforthevirtual
                #count;otherwisependingthenrefusedallocationallow
                #theemployeetocreatemoreleavesthanpossible
                status_dict['virtual_remaining_leaves']+=(allocation.number_of_hours_display
                                                          ifallocation.type_request_unit=='hour'
                                                          elseallocation.number_of_days)
                status_dict['max_leaves']+=(allocation.number_of_hours_display
                                            ifallocation.type_request_unit=='hour'
                                            elseallocation.number_of_days)
                status_dict['remaining_leaves']+=(allocation.number_of_hours_display
                                                  ifallocation.type_request_unit=='hour'
                                                  elseallocation.number_of_days)
        returnresult

    @api.model
    defget_days_all_request(self):
        leave_types=sorted(self.search([]).filtered(lambdax:x.virtual_remaining_leavesorx.max_leaves),key=self._model_sorting_key,reverse=True)
        return[(lt.name,{
                    'remaining_leaves':('%.2f'%lt.remaining_leaves).rstrip('0').rstrip('.'),
                    'virtual_remaining_leaves':('%.2f'%lt.virtual_remaining_leaves).rstrip('0').rstrip('.'),
                    'max_leaves':('%.2f'%lt.max_leaves).rstrip('0').rstrip('.'),
                    'leaves_taken':('%.2f'%lt.leaves_taken).rstrip('0').rstrip('.'),
                    'virtual_leaves_taken':('%.2f'%lt.virtual_leaves_taken).rstrip('0').rstrip('.'),
                    'request_unit':lt.request_unit,
                },lt.allocation_type,lt.validity_stop)
            forltinleave_types]

    def_get_contextual_employee_id(self):
        if'employee_id'inself._context:
            employee_id=self._context['employee_id']
        elif'default_employee_id'inself._context:
            employee_id=self._context['default_employee_id']
        else:
            employee_id=self.env.user.employee_id.id
        returnemployee_id

    @api.depends_context('employee_id','default_employee_id')
    def_compute_leaves(self):
        data_days={}
        employee_id=self._get_contextual_employee_id()

        ifemployee_id:
            data_days=self.get_employees_days([employee_id])[employee_id]

        forholiday_statusinself:
            result=data_days.get(holiday_status.id,{})
            holiday_status.max_leaves=result.get('max_leaves',0)
            holiday_status.leaves_taken=result.get('leaves_taken',0)
            holiday_status.remaining_leaves=result.get('remaining_leaves',0)
            holiday_status.virtual_remaining_leaves=result.get('virtual_remaining_leaves',0)
            holiday_status.virtual_leaves_taken=result.get('virtual_leaves_taken',0)

    def_compute_group_days_allocation(self):
        domain=[
            ('holiday_status_id','in',self.ids),
            ('holiday_type','!=','employee'),
            ('state','=','validate'),
        ]
        domain2=[
            '|',
            ('date_from','>=',fields.Datetime.to_string(datetime.datetime.now().replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0))),
            ('date_from','=',False),
        ]
        grouped_res=self.env['hr.leave.allocation'].read_group(
            expression.AND([domain,domain2]),
            ['holiday_status_id','number_of_days'],
            ['holiday_status_id'],
        )
        grouped_dict=dict((data['holiday_status_id'][0],data['number_of_days'])fordataingrouped_res)
        forallocationinself:
            allocation.group_days_allocation=grouped_dict.get(allocation.id,0)

    def_compute_group_days_leave(self):
        grouped_res=self.env['hr.leave'].read_group(
            [('holiday_status_id','in',self.ids),('holiday_type','=','employee'),('state','=','validate'),
             ('date_from','>=',fields.Datetime.to_string(datetime.datetime.now().replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)))],
            ['holiday_status_id'],
            ['holiday_status_id'],
        )
        grouped_dict=dict((data['holiday_status_id'][0],data['holiday_status_id_count'])fordataingrouped_res)
        forallocationinself:
            allocation.group_days_leave=grouped_dict.get(allocation.id,0)

    defname_get(self):
        ifnotself._context.get('employee_id'):
            #leavecountsisbasedonemployee_id,wouldbeinaccurateifnotbasedoncorrectemployee
            returnsuper(HolidaysType,self).name_get()
        res=[]
        forrecordinself:
            name=record.name
            ifrecord.allocation_type!='no':
                name="%(name)s(%(count)s)"%{
                    'name':name,
                    'count':_('%gremainingoutof%g')%(
                        float_round(record.virtual_remaining_leaves,precision_digits=2)or0.0,
                        float_round(record.max_leaves,precision_digits=2)or0.0,
                    )+(_('hours')ifrecord.request_unit=='hour'else_('days'))
                }
            res.append((record.id,name))
        returnres

    @api.model
    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        """Override_searchtoordertheresults,accordingtosomeemployee.
        Theorderisthefollowing

         -allocationfixedfirst,thenallowingallocation,thenfreeallocation
         -virtualremainingleaves(higherthebetter,sousingreverseonsorted)

        Thisoverrideisnecessarybecausethosefieldsarenotstoredanddepends
        onanemployee_idgivenincontext.Thissortwillbedonewhenthere
        isanemployee_idincontextandthatnootherorderhasbeengiven
        tothemethod.
        """
        employee_id=self._get_contextual_employee_id()
        post_sort=(notcountandnotorderandemployee_id)
        leave_ids=super(HolidaysType,self)._search(args,offset=offset,limit=(Noneifpost_sortelselimit),order=order,count=count,access_rights_uid=access_rights_uid)
        leaves=self.browse(leave_ids)
        ifpost_sort:
            returnleaves.sorted(key=self._model_sorting_key,reverse=True).ids[:limitorNone]
        returnleave_ids

    defaction_see_days_allocated(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("hr_holidays.hr_leave_allocation_action_all")
        domain=[
            ('holiday_status_id','in',self.ids),
            ('holiday_type','!=','employee'),
        ]
        domain2=[
            '|',
            ('date_from','>=',fields.Datetime.to_string(datetime.datetime.now().replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0))),
            ('date_from','=',False),
        ]
        action['domain']=expression.AND([domain,domain2])
        action['context']={
            'default_holiday_type':'department',
            'default_holiday_status_id':self.ids[0],
        }
        returnaction

    defaction_see_group_leaves(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("hr_holidays.hr_leave_action_action_approve_department")
        action['domain']=[
            ('holiday_status_id','=',self.ids[0]),
            ('date_from','>=',fields.Datetime.to_string(datetime.datetime.now().replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)))
        ]
        action['context']={
            'default_holiday_status_id':self.ids[0],
        }
        returnaction
