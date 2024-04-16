#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#Copyright(c)2005-2006AxelorSARL.(http://www.axelor.com)

importlogging
importmath

fromcollectionsimportdefaultdict,namedtuple

fromdatetimeimportdatetime,date,timedelta,time
fromdateutil.rruleimportrrule,DAILY
frompytzimporttimezone,UTC

fromflectraimportapi,fields,models,SUPERUSER_ID,tools
fromflectra.addons.base.models.res_partnerimport_tz_get
fromflectra.addons.resource.models.resourceimportfloat_to_time,HOURS_PER_DAY
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.toolsimportfloat_compare,format_date
fromflectra.tools.float_utilsimportfloat_round
fromflectra.tools.translateimport_
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)

#Usedtoagglomeratetheattendancesinordertofindthehour_fromandhour_to
#See_compute_date_from_to
DummyAttendance=namedtuple('DummyAttendance','hour_from,hour_to,dayofweek,day_period,week_type')

classHolidaysRequest(models.Model):
    """LeaveRequestsAccessspecifications

     -aregularemployee/user
      -canseeallleaves;
      -cannotseenamefieldofleavesbelongingtootheruserasitmaycontain
        privateinformationthatwedon'twanttosharetootherpeoplethan
        HRpeople;
      -canmodifyonlyitsownnotvalidatedleaves(exceptwritingonstateto
        bypassapproval);
      -candiscussonitsleaverequests;
      -canresetonlyitsownleaves;
      -cannotvalidateanyleaves;
     -anOfficer
      -canseeallleaves;
      -canvalidate"HR"singlevalidationleavesfrompeopleif
       -heistheemployeemanager;
       -heisthedepartmentmanager;
       -heismemberofthesamedepartment;
       -targetemployeehasnomanagerandnodepartmentmanager;
      -canvalidate"Manager"singlevalidationleavesfrompeopleif
       -heistheemployeemanager;
       -heisthedepartmentmanager;
       -targetemployeehasnomanagerandnodepartmentmanager;
      -canfirstvalidate"Both"doublevalidationleavesfrompeoplelike"HR"
        singlevalidation,movingtheleavestovalidate1state;
      -cannotvalidateitsownleaves;
      -canresetonlyitsownleaves;
      -canrefuseallleaves;
     -aManager
      -candoeverythinghewants

    Ontopofthatmulticompanyrulesapplybasedoncompanydefinedonthe
    leaverequestleavetype.
    """
    _name="hr.leave"
    _description="TimeOff"
    _order="date_fromdesc"
    _inherit=['mail.thread','mail.activity.mixin']
    _mail_post_access='read'

    @api.model
    defdefault_get(self,fields_list):
        defaults=super(HolidaysRequest,self).default_get(fields_list)
        defaults=self._default_get_request_parameters(defaults)

        if'holiday_status_id'infields_listandnotdefaults.get('holiday_status_id'):
            lt=self.env['hr.leave.type'].search([('valid','=',True)],limit=1)

            iflt:
                defaults['holiday_status_id']=lt.id
                defaults['request_unit_custom']=False

        if'state'infields_listandnotdefaults.get('state'):
            lt=self.env['hr.leave.type'].browse(defaults.get('holiday_status_id'))
            defaults['state']='confirm'

        now=fields.Datetime.now()
        if'date_from'notindefaults:
            defaults.update({'date_from':now})
        if'date_to'notindefaults:
            defaults.update({'date_to':now})
        returndefaults

    def_default_get_request_parameters(self,values):
        new_values=dict(values)
        global_from,global_to=False,False
        #TDEFIXME:consideramappingonseveraldaysthatisnotthestandard
        #calendarwidget7-19inuser'sTZissomecustominput
        ifvalues.get('date_from'):
            user_tz=self.env.user.tzor'UTC'
            localized_dt=timezone('UTC').localize(values['date_from']).astimezone(timezone(user_tz))
            global_from=localized_dt.time().hour==7andlocalized_dt.time().minute==0
            new_values['request_date_from']=localized_dt.date()
        ifvalues.get('date_to'):
            user_tz=self.env.user.tzor'UTC'
            localized_dt=timezone('UTC').localize(values['date_to']).astimezone(timezone(user_tz))
            global_to=localized_dt.time().hour==19andlocalized_dt.time().minute==0
            new_values['request_date_to']=localized_dt.date()
        ifglobal_fromandglobal_to:
            new_values['request_unit_custom']=True
        returnnew_values

    #description
    name=fields.Char('Description',compute='_compute_description',inverse='_inverse_description',search='_search_description',compute_sudo=False)
    private_name=fields.Char('TimeOffDescription',groups='hr_holidays.group_hr_holidays_user')
    state=fields.Selection([
        ('draft','ToSubmit'),
        ('cancel','Cancelled'), #YTIThisstateseemstobeunused.Toremove
        ('confirm','ToApprove'),
        ('refuse','Refused'),
        ('validate1','SecondApproval'),
        ('validate','Approved')
        ],string='Status',compute='_compute_state',store=True,tracking=True,copy=False,readonly=False,
        help="Thestatusissetto'ToSubmit',whenatimeoffrequestiscreated."+
        "\nThestatusis'ToApprove',whentimeoffrequestisconfirmedbyuser."+
        "\nThestatusis'Refused',whentimeoffrequestisrefusedbymanager."+
        "\nThestatusis'Approved',whentimeoffrequestisapprovedbymanager.")
    payslip_status=fields.Boolean('Reportedinlastpayslips',help='Greenthisbuttonwhenthetimeoffhasbeentakenintoaccountinthepayslip.',copy=False)
    report_note=fields.Text('HRComments',copy=False,groups="hr_holidays.group_hr_holidays_manager")
    user_id=fields.Many2one('res.users',string='User',related='employee_id.user_id',related_sudo=True,compute_sudo=True,store=True,default=lambdaself:self.env.uid,readonly=True)
    manager_id=fields.Many2one('hr.employee',compute='_compute_from_employee_id',store=True,readonly=False)
    #leavetypeconfiguration
    holiday_status_id=fields.Many2one(
        "hr.leave.type",compute='_compute_from_employee_id',store=True,string="TimeOffType",required=True,readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]},
        domain=[('valid','=',True)])
    validation_type=fields.Selection(string='ValidationType',related='holiday_status_id.leave_validation_type',readonly=False)
    #HRdata

    employee_id=fields.Many2one(
        'hr.employee',compute='_compute_from_holiday_type',store=True,string='Employee',index=True,readonly=False,ondelete="restrict",
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]},
        tracking=True)
    tz_mismatch=fields.Boolean(compute='_compute_tz_mismatch')
    tz=fields.Selection(_tz_get,compute='_compute_tz')
    department_id=fields.Many2one(
        'hr.department',compute='_compute_department_id',store=True,string='Department',readonly=False,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    notes=fields.Text('Reasons',readonly=True,states={'draft':[('readonly',False)],'confirm':[('readonly',False)]})
    #duration
    date_from=fields.Datetime(
        'StartDate',compute='_compute_date_from_to',store=True,readonly=False,index=True,copy=False,required=True,tracking=True,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    date_to=fields.Datetime(
        'EndDate',compute='_compute_date_from_to',store=True,readonly=False,copy=False,required=True,tracking=True,
        states={'cancel':[('readonly',True)],'refuse':[('readonly',True)],'validate1':[('readonly',True)],'validate':[('readonly',True)]})
    number_of_days=fields.Float(
        'Duration(Days)',compute='_compute_number_of_days',store=True,readonly=False,copy=False,tracking=True,
        help='Numberofdaysofthetimeoffrequest.Usedinthecalculation.Tomanuallycorrecttheduration,usethisfield.')
    number_of_days_display=fields.Float(
        'Durationindays',compute='_compute_number_of_days_display',readonly=True,
        help='Numberofdaysofthetimeoffrequestaccordingtoyourworkingschedule.Usedforinterface.')
    number_of_hours_display=fields.Float(
        'Durationinhours',compute='_compute_number_of_hours_display',readonly=True,
        help='Numberofhoursofthetimeoffrequestaccordingtoyourworkingschedule.Usedforinterface.')
    number_of_hours_text=fields.Char(compute='_compute_number_of_hours_text')
    duration_display=fields.Char('Requested(Days/Hours)',compute='_compute_duration_display',store=True,
        help="Fieldallowingtoseetheleaverequestdurationindaysorhoursdependingontheleave_type_request_unit")   #details
    #details
    meeting_id=fields.Many2one('calendar.event',string='Meeting',copy=False)
    parent_id=fields.Many2one('hr.leave',string='Parent',copy=False)
    linked_request_ids=fields.One2many('hr.leave','parent_id',string='LinkedRequests')
    holiday_type=fields.Selection([
        ('employee','ByEmployee'),
        ('company','ByCompany'),
        ('department','ByDepartment'),
        ('category','ByEmployeeTag')],
        string='AllocationMode',readonly=True,required=True,default='employee',
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]},
        help='ByEmployee:Allocation/RequestforindividualEmployee,ByEmployeeTag:Allocation/Requestforgroupofemployeesincategory')
    category_id=fields.Many2one(
        'hr.employee.category',compute='_compute_from_holiday_type',store=True,string='EmployeeTag',
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]},help='CategoryofEmployee')
    mode_company_id=fields.Many2one(
        'res.company',compute='_compute_from_holiday_type',store=True,string='CompanyMode',
        states={'draft':[('readonly',False)],'confirm':[('readonly',False)]})
    first_approver_id=fields.Many2one(
        'hr.employee',string='FirstApproval',readonly=True,copy=False,
        help='Thisareaisautomaticallyfilledbytheuserwhovalidatethetimeoff')
    second_approver_id=fields.Many2one(
        'hr.employee',string='SecondApproval',readonly=True,copy=False,
        help='Thisareaisautomaticallyfilledbytheuserwhovalidatethetimeoffwithsecondlevel(Iftimeofftypeneedsecondvalidation)')
    can_reset=fields.Boolean('Canreset',compute='_compute_can_reset')
    can_approve=fields.Boolean('CanApprove',compute='_compute_can_approve')

    #UXfields
    leave_type_request_unit=fields.Selection(related='holiday_status_id.request_unit',readonly=True)
    #Interfacefieldsusedwhennotusinghour-basedcomputation
    request_date_from=fields.Date('RequestStartDate')
    request_date_to=fields.Date('RequestEndDate')
    #Interfacefieldsusedwhenusinghour-basedcomputation
    request_hour_from=fields.Selection([
        ('0','12:00AM'),('0.5','12:30AM'),
        ('1','1:00AM'),('1.5','1:30AM'),
        ('2','2:00AM'),('2.5','2:30AM'),
        ('3','3:00AM'),('3.5','3:30AM'),
        ('4','4:00AM'),('4.5','4:30AM'),
        ('5','5:00AM'),('5.5','5:30AM'),
        ('6','6:00AM'),('6.5','6:30AM'),
        ('7','7:00AM'),('7.5','7:30AM'),
        ('8','8:00AM'),('8.5','8:30AM'),
        ('9','9:00AM'),('9.5','9:30AM'),
        ('10','10:00AM'),('10.5','10:30AM'),
        ('11','11:00AM'),('11.5','11:30AM'),
        ('12','12:00PM'),('12.5','12:30PM'),
        ('13','1:00PM'),('13.5','1:30PM'),
        ('14','2:00PM'),('14.5','2:30PM'),
        ('15','3:00PM'),('15.5','3:30PM'),
        ('16','4:00PM'),('16.5','4:30PM'),
        ('17','5:00PM'),('17.5','5:30PM'),
        ('18','6:00PM'),('18.5','6:30PM'),
        ('19','7:00PM'),('19.5','7:30PM'),
        ('20','8:00PM'),('20.5','8:30PM'),
        ('21','9:00PM'),('21.5','9:30PM'),
        ('22','10:00PM'),('22.5','10:30PM'),
        ('23','11:00PM'),('23.5','11:30PM')],string='Hourfrom')
    request_hour_to=fields.Selection([
        ('0','12:00AM'),('0.5','12:30AM'),
        ('1','1:00AM'),('1.5','1:30AM'),
        ('2','2:00AM'),('2.5','2:30AM'),
        ('3','3:00AM'),('3.5','3:30AM'),
        ('4','4:00AM'),('4.5','4:30AM'),
        ('5','5:00AM'),('5.5','5:30AM'),
        ('6','6:00AM'),('6.5','6:30AM'),
        ('7','7:00AM'),('7.5','7:30AM'),
        ('8','8:00AM'),('8.5','8:30AM'),
        ('9','9:00AM'),('9.5','9:30AM'),
        ('10','10:00AM'),('10.5','10:30AM'),
        ('11','11:00AM'),('11.5','11:30AM'),
        ('12','12:00PM'),('12.5','12:30PM'),
        ('13','1:00PM'),('13.5','1:30PM'),
        ('14','2:00PM'),('14.5','2:30PM'),
        ('15','3:00PM'),('15.5','3:30PM'),
        ('16','4:00PM'),('16.5','4:30PM'),
        ('17','5:00PM'),('17.5','5:30PM'),
        ('18','6:00PM'),('18.5','6:30PM'),
        ('19','7:00PM'),('19.5','7:30PM'),
        ('20','8:00PM'),('20.5','8:30PM'),
        ('21','9:00PM'),('21.5','9:30PM'),
        ('22','10:00PM'),('22.5','10:30PM'),
        ('23','11:00PM'),('23.5','11:30PM')],string='Hourto')
    #usedonlywhentheleaveistakeninhalfdays
    request_date_from_period=fields.Selection([
        ('am','Morning'),('pm','Afternoon')],
        string="DatePeriodStart",default='am')
    #requesttype
    request_unit_half=fields.Boolean('HalfDay',compute='_compute_request_unit_half',store=True,readonly=False)
    request_unit_hours=fields.Boolean('CustomHours',compute='_compute_request_unit_hours',store=True,readonly=False)
    request_unit_custom=fields.Boolean('Days-longcustomhours',compute='_compute_request_unit_custom',store=True,readonly=False)

    _sql_constraints=[
        ('type_value',
         "CHECK((holiday_type='employee'ANDemployee_idISNOTNULL)or"
         "(holiday_type='company'ANDmode_company_idISNOTNULL)or"
         "(holiday_type='category'ANDcategory_idISNOTNULL)or"
         "(holiday_type='department'ANDdepartment_idISNOTNULL))",
         "Theemployee,department,companyoremployeecategoryofthisrequestismissing.Pleasemakesurethatyouruserloginislinkedtoanemployee."),
        ('date_check2',"CHECK((date_from<=date_to))","Thestartdatemustbeanteriortotheenddate."),
        ('duration_check',"CHECK(number_of_days>=0)","Ifyouwanttochangethenumberofdaysyoushouldusethe'period'mode"),
    ]

    def_auto_init(self):
        res=super(HolidaysRequest,self)._auto_init()
        tools.create_index(self._cr,'hr_leave_date_to_date_from_index',
                           self._table,['date_to','date_from'])
        returnres

    @api.depends_context('uid')
    def_compute_description(self):
        self.check_access_rights('read')
        self.check_access_rule('read')

        is_officer=self.user_has_groups('hr_holidays.group_hr_holidays_user')

        forleaveinself:
            ifis_officerorleave.user_id==self.env.userorleave.employee_id.leave_manager_id==self.env.user:
                leave.name=leave.sudo().private_name
            else:
                leave.name='*****'

    def_inverse_description(self):
        is_officer=self.user_has_groups('hr_holidays.group_hr_holidays_user')

        forleaveinself:
            ifis_officerorleave.user_id==self.env.userorleave.employee_id.leave_manager_id==self.env.user:
                leave.sudo().private_name=leave.name

    def_search_description(self,operator,value):
        is_officer=self.user_has_groups('hr_holidays.group_hr_holidays_user')
        domain=[('private_name',operator,value)]

        ifnotis_officer:
            domain=expression.AND([domain,[('user_id','=',self.env.user.id)]])

        leaves=self.search(domain)
        return[('id','in',leaves.ids)]

    @api.depends('holiday_status_id')
    def_compute_state(self):
        forholidayinself:
            ifself.env.context.get('unlink')andholiday.state=='draft':
                #Otherwisetherecordindraftwithvalidation_typein(hr,manager,both)willbesettoconfirm
                #andasimpleinternaluserwillnotbeabletodeletehisowndraftrecord
                holiday.state='draft'
            else:
                holiday.state='confirm'ifholiday.validation_type!='no_validation'else'draft'

    @api.depends('request_date_from_period','request_hour_from','request_hour_to','request_date_from','request_date_to',
                'request_unit_half','request_unit_hours','request_unit_custom','employee_id')
    def_compute_date_from_to(self):
        forholidayinself:
            ifholiday.request_date_fromandholiday.request_date_toandholiday.request_date_from>holiday.request_date_to:
                holiday.request_date_to=holiday.request_date_from
            ifnotholiday.request_date_from:
                holiday.date_from=False
            elifnotholiday.request_unit_halfandnotholiday.request_unit_hoursandnotholiday.request_date_to:
                holiday.date_to=False
            else:
                ifholiday.request_unit_halforholiday.request_unit_hours:
                    holiday.request_date_to=holiday.request_date_from
                resource_calendar_id=holiday.employee_id.resource_calendar_idorself.env.company.resource_calendar_id
                domain=[('calendar_id','=',resource_calendar_id.id),('display_type','=',False)]
                attendances=self.env['resource.calendar.attendance'].read_group(domain,['ids:array_agg(id)','hour_from:min(hour_from)','hour_to:max(hour_to)','week_type','dayofweek','day_period'],['week_type','dayofweek','day_period'],lazy=False)

                #MustbesortedbydayofweekASCandday_periodDESC
                attendances=sorted([DummyAttendance(group['hour_from'],group['hour_to'],group['dayofweek'],group['day_period'],group['week_type'])forgroupinattendances],key=lambdaatt:(att.dayofweek,att.day_period!='morning'))

                default_value=DummyAttendance(0,0,0,'morning',False)

                ifresource_calendar_id.two_weeks_calendar:
                    #findweektypeofstart_date
                    start_week_type=int(math.floor((holiday.request_date_from.toordinal()-1)/7)%2)
                    attendance_actual_week=[attforattinattendancesifatt.week_typeisFalseorint(att.week_type)==start_week_type]
                    attendance_actual_next_week=[attforattinattendancesifatt.week_typeisFalseorint(att.week_type)!=start_week_type]
                    #First,adddaysofactualweekcomingafterdate_from
                    attendance_filtred=[attforattinattendance_actual_weekifint(att.dayofweek)>=holiday.request_date_from.weekday()]
                    #Second,adddaysoftheothertypeofweek
                    attendance_filtred+=list(attendance_actual_next_week)
                    #Third,adddaysofactualweek(toconsiderdaysthatwehaveremovefirstbecausetheycomingbeforedate_from)
                    attendance_filtred+=list(attendance_actual_week)

                    end_week_type=int(math.floor((holiday.request_date_to.toordinal()-1)/7)%2)
                    attendance_actual_week=[attforattinattendancesifatt.week_typeisFalseorint(att.week_type)==end_week_type]
                    attendance_actual_next_week=[attforattinattendancesifatt.week_typeisFalseorint(att.week_type)!=end_week_type]
                    attendance_filtred_reversed=list(reversed([attforattinattendance_actual_weekifint(att.dayofweek)<=holiday.request_date_to.weekday()]))
                    attendance_filtred_reversed+=list(reversed(attendance_actual_next_week))
                    attendance_filtred_reversed+=list(reversed(attendance_actual_week))

                    #findfirstattendancecomingafterfirst_day
                    attendance_from=attendance_filtred[0]
                    #findlastattendancecomingbeforelast_day
                    attendance_to=attendance_filtred_reversed[0]
                else:
                    #findfirstattendancecomingafterfirst_day
                    attendance_from=next((attforattinattendancesifint(att.dayofweek)>=holiday.request_date_from.weekday()),attendances[0]ifattendanceselsedefault_value)
                    #findlastattendancecomingbeforelast_day
                    attendance_to=next((attforattinreversed(attendances)ifint(att.dayofweek)<=holiday.request_date_to.weekday()),attendances[-1]ifattendanceselsedefault_value)

                compensated_request_date_from=holiday.request_date_from
                compensated_request_date_to=holiday.request_date_to

                ifholiday.request_unit_half:
                    ifholiday.request_date_from_period=='am':
                        hour_from=float_to_time(attendance_from.hour_from)
                        hour_to=float_to_time(attendance_from.hour_to)
                    else:
                        hour_from=float_to_time(attendance_to.hour_from)
                        hour_to=float_to_time(attendance_to.hour_to)
                elifholiday.request_unit_hours:
                    hour_from=float_to_time(float(holiday.request_hour_from))
                    hour_to=float_to_time(float(holiday.request_hour_to))
                elifholiday.request_unit_custom:
                    hour_from=holiday.date_from.time()
                    hour_to=holiday.date_to.time()
                    compensated_request_date_from=holiday._adjust_date_based_on_tz(holiday.request_date_from,hour_from)
                    compensated_request_date_to=holiday._adjust_date_based_on_tz(holiday.request_date_to,hour_to)
                else:
                    hour_from=float_to_time(attendance_from.hour_from)
                    hour_to=float_to_time(attendance_to.hour_to)

                holiday.date_from=timezone(holiday.tz).localize(datetime.combine(compensated_request_date_from,hour_from)).astimezone(UTC).replace(tzinfo=None)
                holiday.date_to=timezone(holiday.tz).localize(datetime.combine(compensated_request_date_to,hour_to)).astimezone(UTC).replace(tzinfo=None)

    @api.depends('holiday_status_id','request_unit_hours','request_unit_custom')
    def_compute_request_unit_half(self):
        forholidayinself:
            ifholiday.holiday_status_idorholiday.request_unit_hoursorholiday.request_unit_custom:
                holiday.request_unit_half=False

    @api.depends('holiday_status_id','request_unit_half','request_unit_custom')
    def_compute_request_unit_hours(self):
        forholidayinself:
            ifholiday.holiday_status_idorholiday.request_unit_halforholiday.request_unit_custom:
                holiday.request_unit_hours=False

    @api.depends('holiday_status_id','request_unit_half','request_unit_hours')
    def_compute_request_unit_custom(self):
        forholidayinself:
            ifholiday.holiday_status_idorholiday.request_unit_halforholiday.request_unit_hours:
                holiday.request_unit_custom=False

    @api.depends('holiday_type')
    def_compute_from_holiday_type(self):
        forholidayinself:
            ifholiday.holiday_type=='employee':
                ifnotholiday.employee_id:
                    holiday.employee_id=self.env.user.employee_id
                holiday.mode_company_id=False
                holiday.category_id=False
            elifholiday.holiday_type=='company':
                holiday.employee_id=False
                ifnotholiday.mode_company_id:
                    holiday.mode_company_id=self.env.company.id
                holiday.category_id=False
            elifholiday.holiday_type=='department':
                holiday.employee_id=False
                holiday.mode_company_id=False
                holiday.category_id=False
            elifholiday.holiday_type=='category':
                holiday.employee_id=False
                holiday.mode_company_id=False
            else:
                holiday.employee_id=self.env.context.get('default_employee_id')orself.env.user.employee_id

    @api.depends('employee_id')
    def_compute_from_employee_id(self):
        forholidayinself:
            holiday.manager_id=holiday.employee_id.parent_id.id
            ifholiday.employee_id.user_id!=self.env.userandself._origin.employee_id!=holiday.employee_id:
                holiday.holiday_status_id=False

    @api.depends('employee_id','holiday_type')
    def_compute_department_id(self):
        forholidayinself:
            ifholiday.employee_id:
                holiday.department_id=holiday.employee_id.department_id
            elifholiday.holiday_type=='department':
                ifnotholiday.department_id:
                    holiday.department_id=self.env.user.employee_id.department_id
            else:
                holiday.department_id=False

    @api.depends('date_from','date_to','employee_id')
    def_compute_number_of_days(self):
        forholidayinself:
            ifholiday.date_fromandholiday.date_to:
                holiday.number_of_days=holiday._get_number_of_days(holiday.date_from,holiday.date_to,holiday.employee_id.id)['days']
            else:
                holiday.number_of_days=0

    @api.depends('tz')
    @api.depends_context('uid')
    def_compute_tz_mismatch(self):
        forleaveinself:
            leave.tz_mismatch=leave.tz!=self.env.user.tz

    @api.depends('request_unit_custom','employee_id','holiday_type','department_id.company_id.resource_calendar_id.tz','mode_company_id.resource_calendar_id.tz')
    def_compute_tz(self):
        forleaveinself:
            tz=False
            ifleave.request_unit_custom:
                tz='UTC'#custom->alreadyinUTC
            elifleave.holiday_type=='employee':
                tz=leave.employee_id.tz
            elifleave.holiday_type=='department':
                tz=leave.department_id.company_id.resource_calendar_id.tz
            elifleave.holiday_type=='company':
                tz=leave.mode_company_id.resource_calendar_id.tz
            leave.tz=tzorself.env.company.resource_calendar_id.tzorself.env.user.tzor'UTC'

    @api.depends('number_of_days')
    def_compute_number_of_days_display(self):
        forholidayinself:
            holiday.number_of_days_display=holiday.number_of_days

    def_get_calendar(self):
        self.ensure_one()
        returnself.employee_id.resource_calendar_idorself.env.company.resource_calendar_id

    @api.depends('number_of_days')
    def_compute_number_of_hours_display(self):
        forholidayinself:
            calendar=holiday._get_calendar()
            ifholiday.date_fromandholiday.date_to:
                #Takeattendancesintoaccount,incasetheleavevalidated
                #Otherwise,thiswillresultintonumber_of_hours=0
                #andnumber_of_hours_display=0or(#day*calendar.hours_per_day),
                #whichcouldbewrongiftheemployeedoesn'tworkthesamenumber
                #hourseachday
                ifholiday.state=='validate':
                    start_dt=holiday.date_from
                    end_dt=holiday.date_to
                    ifnotstart_dt.tzinfo:
                        start_dt=start_dt.replace(tzinfo=UTC)
                    ifnotend_dt.tzinfo:
                        end_dt=end_dt.replace(tzinfo=UTC)
                    resource=holiday.employee_id.resource_id
                    intervals=calendar._attendance_intervals_batch(start_dt,end_dt,resource)[resource.id]\
                                -calendar._leave_intervals_batch(start_dt,end_dt,None)[False] #SubstractGlobalLeaves
                    number_of_hours=sum((stop-start).total_seconds()/3600forstart,stop,dummyinintervals)
                else:
                    number_of_hours=holiday._get_number_of_days(holiday.date_from,holiday.date_to,holiday.employee_id.id)['hours']
                holiday.number_of_hours_display=number_of_hoursor(holiday.number_of_days*(calendar.hours_per_dayorHOURS_PER_DAY))
            else:
                holiday.number_of_hours_display=0

    @api.depends('number_of_hours_display','number_of_days_display')
    def_compute_duration_display(self):
        forleaveinself:
            leave.duration_display='%g%s'%(
                (float_round(leave.number_of_hours_display,precision_digits=2)
                ifleave.leave_type_request_unit=='hour'
                elsefloat_round(leave.number_of_days_display,precision_digits=2)),
                _('hours')ifleave.leave_type_request_unit=='hour'else_('days'))

    @api.depends('number_of_hours_display')
    def_compute_number_of_hours_text(self):
        #YTINote:Allthisbecauseareadonlyfieldtakesallthewidthoneditmode...
        forleaveinself:
            leave.number_of_hours_text='%s%g%s%s'%(
                ''ifleave.request_unit_halforleave.request_unit_hourselse'(',
                float_round(leave.number_of_hours_display,precision_digits=2),
                _('Hours'),
                ''ifleave.request_unit_halforleave.request_unit_hourselse')')

    @api.depends('state','employee_id','department_id')
    def_compute_can_reset(self):
        forholidayinself:
            try:
                holiday._check_approval_update('draft')
            except(AccessError,UserError):
                holiday.can_reset=False
            else:
                holiday.can_reset=True

    @api.depends('state','employee_id','department_id')
    def_compute_can_approve(self):
        forholidayinself:
            try:
                ifholiday.state=='confirm'andholiday.validation_type=='both':
                    holiday._check_approval_update('validate1')
                else:
                    holiday._check_approval_update('validate')
            except(AccessError,UserError):
                holiday.can_approve=False
            else:
                holiday.can_approve=True

    @api.constrains('date_from','date_to','employee_id')
    def_check_date(self):
        ifself.env.context.get('leave_skip_date_check',False):
            return
        forholidayinself.filtered('employee_id'):
            domain=[
                ('date_from','<',holiday.date_to),
                ('date_to','>',holiday.date_from),
                ('employee_id','=',holiday.employee_id.id),
                ('id','!=',holiday.id),
                ('state','notin',['cancel','refuse']),
            ]
            nholidays=self.search_count(domain)
            ifnholidays:
                raiseValidationError(_('Youcannotset2timeoffthatoverlapsonthesamedayforthesameemployee.'))

    @api.constrains('state','number_of_days','holiday_status_id')
    def_check_holidays(self):
        mapped_days=self.mapped('holiday_status_id').get_employees_days(self.mapped('employee_id').ids)
        forholidayinself:
            ifholiday.holiday_type!='employee'ornotholiday.employee_idorholiday.holiday_status_id.allocation_type=='no':
                continue
            leave_days=mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            iffloat_compare(leave_days['remaining_leaves'],0,precision_digits=2)==-1orfloat_compare(leave_days['virtual_remaining_leaves'],0,precision_digits=2)==-1:
                raiseValidationError(_('Thenumberofremainingtimeoffisnotsufficientforthistimeofftype.\n'
                                        'Pleasealsocheckthetimeoffwaitingforvalidation.'))

    @api.constrains('date_from','date_to','employee_id')
    def_check_date_state(self):
        ifself.env.context.get('leave_skip_state_check'):
            return
        forholidayinself:
            ifholiday.statein['cancel','refuse','validate1','validate']:
                raiseValidationError(_("Thismodificationisnotallowedinthecurrentstate."))

    def_get_number_of_days(self,date_from,date_to,employee_id):
        """Returnsafloatequalstothetimedeltabetweentwodatesgivenasstring."""
        ifemployee_id:
            employee=self.env['hr.employee'].browse(employee_id)
            #Weforcethecompanyinthedomainaswearemorethanlikelyinacompute_sudo
            domain=[('company_id','in',self.env.company.ids+self.env.context.get('allowed_company_ids',[]))]
            result=employee._get_work_days_data_batch(date_from,date_to,domain=domain)[employee.id]
            ifself.request_unit_halfandresult['hours']>0:
                result['days']=0.5
            returnresult

        today_hours=self.env.company.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(),time.min),
            datetime.combine(date_from.date(),time.max),
            False)

        hours=self.env.company.resource_calendar_id.get_work_hours_count(date_from,date_to)
        days=hours/(today_hoursorHOURS_PER_DAY)ifnotself.request_unit_halfelse0.5
        return{'days':days,'hours':hours}

    def_adjust_date_based_on_tz(self,leave_date,hour):
        """request_date_{from,to}arelocaltotheuser'stzbuthour_{from,to}areinUTC.

        Insomecasestheyarecombined(assumingtheyareinthesametz)asadatetime.When
        thathappensit'spossibleweneedtoadjustoneofthedates.Thisfunctionadjustthe
        date,sothatitcanbepassedtodatetime().

        E.g.aleaveinUS/Pacificforoneday:
        -request_date_from:1stofJan
        -request_date_to:  1stofJan
        -hour_from:        15:00(7:00local)
        -hour_to:          03:00(19:00local)<--thishappensonthe2ndofJaninUTC
        """
        user_tz=timezone(self.env.user.tzifself.env.user.tzelse'UTC')
        request_date_to_utc=UTC.localize(datetime.combine(leave_date,hour)).astimezone(user_tz).replace(tzinfo=None)
        ifrequest_date_to_utc.date()<leave_date:
            returnleave_date+timedelta(days=1)
        elifrequest_date_to_utc.date()>leave_date:
            returnleave_date-timedelta(days=1)
        else:
            returnleave_date

    ####################################################
    #ORMOverridesmethods
    ####################################################

    defname_get(self):
        res=[]
        forleaveinself:
            ifself.env.context.get('short_name'):
                ifleave.leave_type_request_unit=='hour':
                    res.append((leave.id,_("%s:%.2fhours")%(leave.nameorleave.holiday_status_id.name,leave.number_of_hours_display)))
                else:
                    res.append((leave.id,_("%s:%.2fdays")%(leave.nameorleave.holiday_status_id.name,leave.number_of_days)))
            else:
                ifleave.holiday_type=='company':
                    target=leave.mode_company_id.name
                elifleave.holiday_type=='department':
                    target=leave.department_id.name
                elifleave.holiday_type=='category':
                    target=leave.category_id.name
                else:
                    target=leave.employee_id.name
                display_date=format_date(self.env,leave.date_from)
                ifleave.leave_type_request_unit=='hour':
                    ifself.env.context.get('hide_employee_name')and'employee_id'inself.env.context.get('group_by',[]):
                        res.append((
                            leave.id,
                            _("%(person)son%(leave_type)s:%(duration).2fhourson%(date)s",
                                person=target,
                                leave_type=leave.holiday_status_id.name,
                                duration=leave.number_of_hours_display,
                                date=display_date,
                            )
                        ))
                    else:
                        res.append((
                            leave.id,
                            _("%(person)son%(leave_type)s:%(duration).2fhourson%(date)s",
                                person=target,
                                leave_type=leave.holiday_status_id.name,
                                duration=leave.number_of_hours_display,
                                date=display_date,
                            )
                        ))
                else:
                    ifleave.number_of_days>1:
                        display_date+='⇨%s'%format_date(self.env,leave.date_to)
                    ifself.env.context.get('hide_employee_name')and'employee_id'inself.env.context.get('group_by',[]):
                        res.append((
                            leave.id,
                            _("%(leave_type)s:%(duration).2fdays(%(start)s)",
                                leave_type=leave.holiday_status_id.name,
                                duration=leave.number_of_days,
                                start=display_date,
                            )
                        ))
                    else:
                        res.append((
                            leave.id,
                            _("%(person)son%(leave_type)s:%(duration).2fdays(%(start)s)",
                                person=target,
                                leave_type=leave.holiday_status_id.name,
                                duration=leave.number_of_days,
                                start=display_date,
                            )
                        ))
        returnres

    defadd_follower(self,employee_id):
        employee=self.env['hr.employee'].browse(employee_id)
        ifemployee.user_id:
            self.message_subscribe(partner_ids=employee.user_id.partner_id.ids)

    @api.constrains('holiday_status_id','date_to','date_from')
    def_check_leave_type_validity(self):
        forleaveinself:
            vstart=leave.holiday_status_id.validity_start
            vstop=leave.holiday_status_id.validity_stop
            dfrom=leave.date_from
            dto=leave.date_to
            ifleave.holiday_status_id.validity_startandleave.holiday_status_id.validity_stop:
                ifdfromanddtoand(dfrom.date()<vstartordto.date()>vstop):
                    raiseValidationError(_(
                        '%(leave_type)sareonlyvalidbetween%(start)sand%(end)s',
                        leave_type=leave.holiday_status_id.display_name,
                        start=leave.holiday_status_id.validity_start,
                        end=leave.holiday_status_id.validity_stop
                    ))
            elifleave.holiday_status_id.validity_start:
                ifdfromand(dfrom.date()<vstart):
                    raiseValidationError(_(
                        '%(leave_type)sareonlyvalidstartingfrom%(date)s',
                        leave_type=leave.holiday_status_id.display_name,
                        date=leave.holiday_status_id.validity_start
                    ))
            elifleave.holiday_status_id.validity_stop:
                ifdtoand(dto.date()>vstop):
                    raiseValidationError(_(
                        '%(leave_type)sareonlyvaliduntil%(date)s',
                        leave_type=leave.holiday_status_id.display_name,
                        date=leave.holiday_status_id.validity_stop
                    ))

    def_check_double_validation_rules(self,employees,state):
        ifself.user_has_groups('hr_holidays.group_hr_holidays_manager'):
            return

        is_leave_user=self.user_has_groups('hr_holidays.group_hr_holidays_user')
        ifstate=='validate1':
            employees=employees.filtered(lambdaemployee:employee.leave_manager_id!=self.env.user)
            ifemployeesandnotis_leave_user:
                raiseAccessError(_('Youcannotfirstapproveatimeofffor%s,becauseyouarenothistimeoffmanager',employees[0].name))
        elifstate=='validate'andnotis_leave_user:
            #Isprobablyhandledviair.rule
            raiseAccessError(_('Youdon\'thavetherightstoapplysecondapprovalonatimeoffrequest'))

    @api.model_create_multi
    defcreate(self,vals_list):
        """Overridetoavoidautomaticloggingofcreation"""
        ifnotself._context.get('leave_fast_create'):
            leave_types=self.env['hr.leave.type'].browse([values.get('holiday_status_id')forvaluesinvals_listifvalues.get('holiday_status_id')])
            mapped_validation_type={leave_type.id:leave_type.leave_validation_typeforleave_typeinleave_types}

            forvaluesinvals_list:
                employee_id=values.get('employee_id',False)
                leave_type_id=values.get('holiday_status_id')
                #Handleautomaticdepartment_id
                ifnotvalues.get('department_id'):
                    values.update({'department_id':self.env['hr.employee'].browse(employee_id).department_id.id})

                #Handleno_validation
                ifmapped_validation_type[leave_type_id]=='no_validation':
                    values.update({'state':'confirm'})

                if'state'notinvalues:
                    #Tomimicthebehaviorofcompute_statethatwasalwaystriggered,asthefieldwasreadonly
                    values['state']='confirm'ifmapped_validation_type[leave_type_id]!='no_validation'else'draft'

                #Handledoublevalidation
                ifmapped_validation_type[leave_type_id]=='both':
                    self._check_double_validation_rules(employee_id,values.get('state',False))

        holidays=super(HolidaysRequest,self.with_context(mail_create_nosubscribe=True)).create(vals_list)

        forholidayinholidays:
            ifnotself._context.get('leave_fast_create'):
                #Everythingthatisdoneheremustbedoneusingsudobecausewemight
                #havedifferentcreateandwriterights
                #eg:holidays_usercancreatealeaverequestwithvalidation_type='manager'forsomeoneelse
                #buttheycanonlywriteonitiftheyareleave_manager_id
                holiday_sudo=holiday.sudo()
                holiday_sudo.add_follower(employee_id)
                ifholiday.validation_type=='manager':
                    holiday_sudo.message_subscribe(partner_ids=holiday.employee_id.leave_manager_id.partner_id.ids)
                ifholiday.validation_type=='no_validation':
                    #Automaticvalidationshouldbedoneinsudo,becauseusermightnothavetherightstodoitbyhimself
                    holiday_sudo.action_validate()
                    holiday_sudo.message_subscribe(partner_ids=[holiday._get_responsible_for_approval().partner_id.id])
                    holiday_sudo.message_post(body=_("Thetimeoffhasbeenautomaticallyapproved"),subtype_xmlid="mail.mt_comment")#MessagefromFlectraBot(sudo)
                elifnotself._context.get('import_file'):
                    holiday_sudo.activity_update()
        returnholidays

    defwrite(self,values):
        is_officer=self.env.user.has_group('hr_holidays.group_hr_holidays_user')orself.env.is_superuser()

        ifnotis_officerandvalues.keys()-{'message_main_attachment_id'}:
            ifany(hol.date_from.date()<fields.Date.today()andhol.employee_id.leave_manager_id!=self.env.userforholinself):
                raiseUserError(_('Youmusthavemanagerrightstomodify/validateatimeoffthatalreadybegun'))

        employee_id=values.get('employee_id',False)
        ifnotself.env.context.get('leave_fast_create'):
            ifvalues.get('state'):
                self._check_approval_update(values['state'])
                ifany(holiday.validation_type=='both'forholidayinself):
                    ifvalues.get('employee_id'):
                        employees=self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees=self.mapped('employee_id')
                    self._check_double_validation_rules(employees,values['state'])
            if'date_from'invalues:
                values['request_date_from']=values['date_from']
            if'date_to'invalues:
                values['request_date_to']=values['date_to']
        result=super(HolidaysRequest,self).write(values)
        ifnotself.env.context.get('leave_fast_create'):
            forholidayinself:
                ifemployee_id:
                    holiday.add_follower(employee_id)
        returnresult

    defunlink(self):
        error_message=_('Youcannotdeleteatimeoffwhichisin%sstate')
        state_description_values={elem[0]:elem[1]foreleminself._fields['state']._description_selection(self.env)}

        ifnotself.user_has_groups('hr_holidays.group_hr_holidays_user'):
            ifany(hol.state!='draft'forholinself):
                raiseUserError(error_message%state_description_values.get(self[:1].state))
        else:
            forholidayinself.filtered(lambdaholiday:holiday.statenotin['draft','cancel','confirm']):
                raiseUserError(error_message%(state_description_values.get(holiday.state),))
        returnsuper(HolidaysRequest,self.with_context(leave_skip_date_check=True,unlink=True)).unlink()

    defcopy_data(self,default=None):
        ifdefaultand'date_from'indefaultand'date_to'indefault:
            default['request_date_from']=default.get('date_from')
            default['request_date_to']=default.get('date_to')
            returnsuper().copy_data(default)
        elifself.statein{"cancel","refuse"}: #Nooverlapconstraintinthesecases
            returnsuper().copy_data(default)
        raiseUserError(_('Atimeoffcannotbeduplicated.'))

    def_get_mail_redirect_suggested_company(self):
        returnself.holiday_status_id.company_id

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        ifnotself.user_has_groups('hr_holidays.group_hr_holidays_user')and'private_name'ingroupby:
            raiseUserError(_('Suchgroupingisnotallowed.'))
        returnsuper(HolidaysRequest,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

    ####################################################
    #Businessmethods
    ####################################################

    def_prepare_resource_leave_vals_list(self):
        """Hookmethodforotherstoinjectdata
        """
        return[{
            'name':leave.name,
            'date_from':leave.date_from,
            'holiday_id':leave.id,
            'date_to':leave.date_to,
            'resource_id':leave.employee_id.resource_id.id,
            'calendar_id':leave.employee_id.resource_calendar_id.id,
            'time_type':leave.holiday_status_id.time_type,
            }forleaveinself]

    def_create_resource_leave(self):
        """Thismethodwillcreateentryinresourcecalendartimeoffobjectatthetimeofholidaysvalidated
        :returns:created`resource.calendar.leaves`
        """
        vals_list=self._prepare_resource_leave_vals_list()
        returnself.env['resource.calendar.leaves'].sudo().create(vals_list)

    def_remove_resource_leave(self):
        """Thismethodwillcreateentryinresourcecalendartimeoffobjectatthetimeofholidayscancel/removed"""
        returnself.env['resource.calendar.leaves'].search([('holiday_id','in',self.ids)]).unlink()

    def_validate_leave_request(self):
        """Validatetimeoffrequests(holiday_type='employee')
        bycreatingacalendareventandaresourcetimeoff."""
        holidays=self.filtered(lambdarequest:request.holiday_type=='employee')
        holidays._create_resource_leave()
        meeting_holidays=holidays.filtered(lambdal:l.holiday_status_id.create_calendar_meeting)
        meetings=self.env['calendar.event']
        ifmeeting_holidays:
            meeting_values_for_user_id=meeting_holidays._prepare_holidays_meeting_values()
            foruser_id,meeting_valuesinmeeting_values_for_user_id.items():
                meetings+=self.env['calendar.event'].with_user(user_idorself.env.uid).with_context(
                                allowed_company_ids=[],
                                no_mail_to_attendees=True,
                                active_model=self._name
                            ).create(meeting_values)
        Holiday=self.env['hr.leave']
        formeetinginmeetings:
            Holiday.browse(meeting.res_id).meeting_id=meeting

    def_prepare_holidays_meeting_values(self):
        result=defaultdict(list)
        company_calendar=self.env.company.resource_calendar_id
        forholidayinself:
            calendar=holiday.employee_id.resource_calendar_idorcompany_calendar
            user=holiday.user_id
            ifholiday.leave_type_request_unit=='hour':
                meeting_name=_("%sonTimeOff:%.2fhour(s)")%(holiday.employee_id.nameorholiday.category_id.name,holiday.number_of_hours_display)
            else:
                meeting_name=_("%sonTimeOff:%.2fday(s)")%(holiday.employee_id.nameorholiday.category_id.name,holiday.number_of_days)
            meeting_values={
                'name':meeting_name,
                'duration':holiday.number_of_days*(calendar.hours_per_dayorHOURS_PER_DAY),
                'description':holiday.notes,
                'user_id':user.id,
                'start':holiday.date_from,
                'stop':holiday.date_to,
                'allday':False,
                'privacy':'confidential',
                'event_tz':user.tz,
                'activity_ids':[(5,0,0)],
                'res_id':holiday.id,
            }
            #Addthepartner_id(ifexist)asanattendee
            ifuseranduser.partner_id:
                meeting_values['partner_ids']=[
                    (4,user.partner_id.id)]
            result[user.id].append(meeting_values)
        returnresult

    #YTITODO:Removemeinmaster
    def_prepare_holiday_values(self,employee):
        returnself._prepare_employees_holiday_values(employee)[0]

    def_prepare_employees_holiday_values(self,employees):
        self.ensure_one()
        work_days_data=employees._get_work_days_data_batch(self.date_from,self.date_to)
        return[{
            'name':self.name,
            'holiday_type':'employee',
            'holiday_status_id':self.holiday_status_id.id,
            'date_from':self.date_from,
            'date_to':self.date_to,
            'request_date_from':self.request_date_from,
            'request_date_to':self.request_date_to,
            'notes':self.notes,
            'number_of_days':work_days_data[employee.id]['days'],
            'parent_id':self.id,
            'employee_id':employee.id,
            'state':'validate',
        }foremployeeinemployeesifwork_days_data[employee.id]['days']]

    defaction_draft(self):
        ifany(holiday.statenotin['confirm','refuse']forholidayinself):
            raiseUserError(_('Timeoffrequeststatemustbe"Refused"or"ToApprove"inordertoberesettodraft.'))
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
            raiseUserError(_('TimeoffrequestmustbeinDraftstate("ToSubmit")inordertoconfirmit.'))
        self.write({'state':'confirm'})
        holidays=self.filtered(lambdaleave:leave.validation_type=='no_validation')
        ifholidays:
            #Automaticvalidationshouldbedoneinsudo,becauseusermightnothavetherightstodoitbyhimself
            holidays.sudo().action_validate()
        self.activity_update()
        returnTrue

    defaction_approve(self):
        #ifvalidation_type=='both':thismethodisthefirstapprovalapproval
        #ifvalidation_type!='both':thismethodcallsaction_validate()below
        ifany(holiday.state!='confirm'forholidayinself):
            raiseUserError(_('Timeoffrequestmustbeconfirmed("ToApprove")inordertoapproveit.'))

        current_employee=self.env.user.employee_id
        self.filtered(lambdahol:hol.validation_type=='both').write({'state':'validate1','first_approver_id':current_employee.id})


        #Postasecondmessage,moreverbosethanthetrackingmessage
        forholidayinself.filtered(lambdaholiday:holiday.employee_id.user_id):
            holiday.message_post(
                body=_(
                    'Your%(leave_type)splannedon%(date)shasbeenaccepted',
                    leave_type=holiday.holiday_status_id.display_name,
                    date=holiday.date_from
                ),
                partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambdahol:nothol.validation_type=='both').action_validate()
        ifnotself.env.context.get('leave_fast_create'):
            self.activity_update()
        returnTrue

    defaction_validate(self):
        current_employee=self.env.user.employee_id
        leaves=self.filtered(lambdal:l.employee_idandnotl.number_of_days)
        ifleaves:
            raiseValidationError(_('Thefollowingemployeesarenotsupposedtoworkduringthatperiod:\n%s')%','.join(leaves.mapped('employee_id.name')))

        ifany(holiday.statenotin['confirm','validate1']andholiday.validation_type!='no_validation'forholidayinself):
            raiseUserError(_('Timeoffrequestmustbeconfirmedinordertoapproveit.'))

        self.write({'state':'validate'})
        self.filtered(lambdaholiday:holiday.validation_type=='both').write({'second_approver_id':current_employee.id})
        self.filtered(lambdaholiday:holiday.validation_type!='both').write({'first_approver_id':current_employee.id})

        forholidayinself.filtered(lambdaholiday:holiday.holiday_type!='employee'):
            ifholiday.holiday_type=='category':
                employees=holiday.category_id.employee_ids
            elifholiday.holiday_type=='company':
                employees=self.env['hr.employee'].search([('company_id','=',holiday.mode_company_id.id)])
            else:
                employees=holiday.department_id.member_ids

            conflicting_leaves=self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True
            ).search([
                ('date_from','<=',holiday.date_to),
                ('date_to','>',holiday.date_from),
                ('state','notin',['cancel','refuse']),
                ('holiday_type','=','employee'),
                ('employee_id','in',employees.ids)])

            ifconflicting_leaves:
                #YTI:Morecomplexusecasescouldbemanagedinmaster
                ifholiday.leave_type_request_unit!='day'orany(l.leave_type_request_unit=='hour'forlinconflicting_leaves):
                    raiseValidationError(_('Youcannothave2timeoffthatoverlapsonthesameday.'))

                #keeptrackofconflictingleavesstatesbeforerefusal
                target_states={l.id:l.stateforlinconflicting_leaves}
                conflicting_leaves.action_refuse()
                split_leaves_vals=[]
                forconflicting_leaveinconflicting_leaves:
                    ifconflicting_leave.leave_type_request_unit=='half_day'andconflicting_leave.request_unit_half:
                        continue

                    #Leavesindays
                    ifconflicting_leave.date_from<holiday.date_from:
                        before_leave_vals=conflicting_leave.copy_data({
                            'date_from':conflicting_leave.date_from.date(),
                            'date_to':holiday.date_from.date()+timedelta(days=-1),
                            'state':target_states[conflicting_leave.id],
                        })[0]
                        before_leave=self.env['hr.leave'].new(before_leave_vals)
                        before_leave._compute_date_from_to()

                        #Couldhappenforpart-timecontract,thattimeoffisnotnecessary
                        #anymore.
                        #Imagineyouworkonmonday-wednesday-fridayonly.
                        #Youtakeatimeoffonfriday.
                        #Wecreateacompanytimeoffonfriday.
                        #Bylookingatthelastattendancebeforethecompanytimeoff
                        #startdatetocomputethedate_to,youwouldhaveadate_from>date_to.
                        #Justdon'tcreatetheleaveatthattime.That'sthereasonwhyweuse
                        #newinsteadofcreate.Astheleaveisnotactuallycreatedyet,thesql
                        #constraintdidn'tcheckdate_from<date_toyet.
                        ifbefore_leave.date_from<before_leave.date_to:
                            split_leaves_vals.append(before_leave._convert_to_write(before_leave._cache))
                    ifconflicting_leave.date_to>holiday.date_to:
                        after_leave_vals=conflicting_leave.copy_data({
                            'date_from':holiday.date_to.date()+timedelta(days=1),
                            'date_to':conflicting_leave.date_to.date(),
                            'state':target_states[conflicting_leave.id],
                        })[0]
                        after_leave=self.env['hr.leave'].new(after_leave_vals)
                        after_leave._compute_date_from_to()
                        #Couldhappenforpart-timecontract,thattimeoffisnotnecessary
                        #anymore.
                        ifafter_leave.date_from<after_leave.date_to:
                            split_leaves_vals.append(after_leave._convert_to_write(after_leave._cache))

                split_leaves=self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    leave_skip_state_check=True
                ).create(split_leaves_vals)

                split_leaves.filtered(lambdal:l.statein'validate')._validate_leave_request()

            values=holiday._prepare_employees_holiday_values(employees)
            leaves=self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
                leave_skip_state_check=True,
            ).create(values)

            leaves._validate_leave_request()

        employee_requests=self.filtered(lambdahol:hol.holiday_type=='employee')
        employee_requests._validate_leave_request()
        ifnotself.env.context.get('leave_fast_create'):
            employee_requests.filtered(lambdaholiday:holiday.validation_type!='no_validation').activity_update()
        returnTrue

    defaction_refuse(self):
        current_employee=self.env.user.employee_id
        ifany(holiday.statenotin['draft','confirm','validate','validate1']forholidayinself):
            raiseUserError(_('Timeoffrequestmustbeconfirmedorvalidatedinordertorefuseit.'))

        validated_holidays=self.filtered(lambdahol:hol.state=='validate1')
        validated_holidays.write({'state':'refuse','first_approver_id':current_employee.id})
        (self-validated_holidays).write({'state':'refuse','second_approver_id':current_employee.id})
        #Deletethemeeting
        self.mapped('meeting_id').write({'active':False})
        #Ifacategorythatcreatedseveralholidays,cancelallrelated
        linked_requests=self.mapped('linked_request_ids')
        iflinked_requests:
            linked_requests.action_refuse()

        #Postasecondmessage,moreverbosethanthetrackingmessage
        forholidayinself:
            ifholiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your%(leave_type)splannedon%(date)shasbeenrefused',leave_type=holiday.holiday_status_id.display_name,date=holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self._remove_resource_leave()
        self.activity_update()
        returnTrue

    def_check_approval_update(self,state):
        """Checkiftargetstateisachievable."""
        ifself.env.is_superuser():
            return

        current_employee=self.env.user.employee_id
        is_officer=self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager=self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        forholidayinself:
            val_type=holiday.validation_type

            ifnotis_managerandstate!='confirm':
                ifstate=='draft':
                    ifholiday.state=='refuse':
                        raiseUserError(_('OnlyaTimeOffManagercanresetarefusedleave.'))
                    ifholiday.date_fromandholiday.date_from.date()<=fields.Date.today():
                        raiseUserError(_('OnlyaTimeOffManagercanresetastartedleave.'))
                    ifholiday.employee_id!=current_employee:
                        raiseUserError(_('OnlyaTimeOffManagercanresetotherpeopleleaves.'))
                else:
                    ifval_type=='no_validation'andcurrent_employee==holiday.employee_id:
                        continue
                    #useir.rulebasedfirstaccesscheck:department,members,...(seesecurity.xml)
                    holiday.check_access_rule('write')

                    #Thishandlesstatesvalidate1validateandrefuse
                    ifholiday.employee_id==current_employee:
                        raiseUserError(_('OnlyaTimeOffManagercanapprove/refuseitsownrequests.'))

                    if(state=='validate1'andval_type=='both')or(state=='validate'andval_type=='manager')andholiday.holiday_type=='employee':
                        ifnotis_officerandself.env.user!=holiday.employee_id.leave_manager_id:
                            raiseUserError(_('Youmustbeeither%s\'smanagerorTimeoffManagertoapprovethisleave')%(holiday.employee_id.name))

                    ifnotis_officerand(state=='validate'andval_type=='hr')andholiday.holiday_type=='employee':
                        raiseUserError(_('YoumusteitherbeaTimeoffOfficerorTimeoffManagertoapprovethisleave'))

    #------------------------------------------------------------
    #Activitymethods
    #------------------------------------------------------------

    def_get_responsible_for_approval(self):
        self.ensure_one()

        responsible=self.env.user

        ifself.holiday_type!='employee':
            returnresponsible

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
        to_clean,to_do=self.env['hr.leave'],self.env['hr.leave']
        forholidayinself:
            start=UTC.localize(holiday.date_from).astimezone(timezone(holiday.employee_id.tzor'UTC'))
            end=UTC.localize(holiday.date_to).astimezone(timezone(holiday.employee_id.tzor'UTC'))
            note=_(
                'New%(leave_type)sRequestcreatedby%(user)sfrom%(start)sto%(end)s',
                leave_type=holiday.holiday_status_id.name,
                user=holiday.create_uid.name,
                start=start,
                end=end
            )
            ifholiday.state=='draft':
                to_clean|=holiday
            elifholiday.state=='confirm':
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().idorself.env.user.id)
            elifholiday.state=='validate1':
                holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_second_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().idorself.env.user.id)
            elifholiday.state=='validate':
                to_do|=holiday
            elifholiday.state=='refuse':
                to_clean|=holiday
        ifto_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_approval','hr_holidays.mail_act_leave_second_approval'])
        ifto_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_approval','hr_holidays.mail_act_leave_second_approval'])

    ####################################################
    #Messagingmethods
    ####################################################

    def_track_subtype(self,init_values):
        if'state'ininit_valuesandself.state=='validate':
            leave_notif_subtype=self.holiday_status_id.leave_notif_subtype_id
            returnleave_notif_subtypeorself.env.ref('hr_holidays.mt_leave')
        returnsuper(HolidaysRequest,self)._track_subtype(init_values)

    def_notify_get_groups(self,msg_vals=None):
        """HandleHRusersandofficersrecipientsthatcanvalidateorrefuseholidays
        directlyfromemail."""
        groups=super(HolidaysRequest,self)._notify_get_groups(msg_vals=msg_vals)
        local_msg_vals=dict(msg_valsor{})

        self.ensure_one()
        hr_actions=[]
        ifself.state=='confirm':
            app_action=self._notify_get_action_link('controller',controller='/leave/validate',**local_msg_vals)
            hr_actions+=[{'url':app_action,'title':_('Approve')}]
        ifself.statein['confirm','validate','validate1']:
            ref_action=self._notify_get_action_link('controller',controller='/leave/refuse',**local_msg_vals)
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
            returnsuper(HolidaysRequest,self.sudo()).message_subscribe(partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=subtype_ids)
        returnsuper(HolidaysRequest,self).message_subscribe(partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=subtype_ids)

    @api.model
    defget_unusual_days(self,date_from,date_to=None):
        #Checkingthecalendardirectlyallowstonotgreyouttheleavestaken
        #bytheemployee
        calendar=self.env.user.employee_id.resource_calendar_id
        ifnotcalendar:
            return{}
        dfrom=datetime.combine(fields.Date.from_string(date_from),time.min).replace(tzinfo=UTC)
        dto=datetime.combine(fields.Date.from_string(date_to),time.max).replace(tzinfo=UTC)

        works={d[0].date()fordincalendar._work_intervals_batch(dfrom,dto)[False]}
        return{fields.Date.to_string(day.date()):(day.date()notinworks)fordayinrrule(DAILY,dfrom,until=dto)}
