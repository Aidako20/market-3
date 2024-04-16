#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
importmath
fromdatetimeimportdatetime,time,timedelta
fromdateutil.relativedeltaimportrelativedelta
fromdateutil.rruleimportrrule,DAILY,WEEKLY
fromfunctoolsimportpartial
fromitertoolsimportchain
frompytzimporttimezone,utc

fromflectraimportapi,fields,models,_
fromflectra.addons.base.models.res_partnerimport_tz_get
fromflectra.exceptionsimportValidationError,UserError
fromflectra.osvimportexpression
fromflectra.tools.float_utilsimportfloat_round

fromflectra.toolsimportdate_utils,float_utils
from.resource_mixinimporttimezone_datetime

#Defaulthourperdayvalue.Theoneshould
#onlybeusedwhentheonefromthecalendar
#isnotavailable.
HOURS_PER_DAY=8
#Thiswillgenerate16thofdays
ROUNDING_FACTOR=16


defmake_aware(dt):
    """Return``dt``withanexplicittimezone,togetherwithafunctionto
        convertadatetimetothesame(naiveoraware)timezoneas``dt``.
    """
    ifdt.tzinfo:
        returndt,lambdaval:val.astimezone(dt.tzinfo)
    else:
        returndt.replace(tzinfo=utc),lambdaval:val.astimezone(utc).replace(tzinfo=None)


defstring_to_datetime(value):
    """ConvertthegivenstringvaluetoadatetimeinUTC."""
    returnutc.localize(fields.Datetime.from_string(value))


defdatetime_to_string(dt):
    """Convertthegivendatetime(convertedinUTC)toastringvalue."""
    returnfields.Datetime.to_string(dt.astimezone(utc))


deffloat_to_time(hours):
    """Convertanumberofhoursintoatimeobject."""
    ifhours==24.0:
        returntime.max
    fractional,integral=math.modf(hours)
    returntime(int(integral),int(float_round(60*fractional,precision_digits=0)),0)


def_boundaries(intervals,opening,closing):
    """Iterateontheboundariesofintervals."""
    forstart,stop,recsinintervals:
        ifstart<stop:
            yield(start,opening,recs)
            yield(stop,closing,recs)


classIntervals(object):
    """Collectionofordereddisjointintervalswithsomeassociatedrecords.
        Eachintervalisatriple``(start,stop,records)``,where``records``
        isarecordset.
    """
    def__init__(self,intervals=()):
        self._items=[]
        ifintervals:
            #normalizetherepresentationofintervals
            append=self._items.append
            starts=[]
            recses=[]
            forvalue,flag,recsinsorted(_boundaries(intervals,'start','stop')):
                ifflag=='start':
                    starts.append(value)
                    recses.append(recs)
                else:
                    start=starts.pop()
                    ifnotstarts:
                        append((start,value,recses[0].union(*recses)))
                        recses.clear()

    def__bool__(self):
        returnbool(self._items)

    def__len__(self):
        returnlen(self._items)

    def__iter__(self):
        returniter(self._items)

    def__reversed__(self):
        returnreversed(self._items)

    def__or__(self,other):
        """Returntheunionoftwosetsofintervals."""
        returnIntervals(chain(self._items,other._items))

    def__and__(self,other):
        """Returntheintersectionoftwosetsofintervals."""
        returnself._merge(other,False)

    def__sub__(self,other):
        """Returnthedifferenceoftwosetsofintervals."""
        returnself._merge(other,True)

    def_merge(self,other,difference):
        """Returnthedifferenceorintersectionoftwosetsofintervals."""
        result=Intervals()
        append=result._items.append

        #using'self'and'other'belowforcesnormalization
        bounds1=_boundaries(self,'start','stop')
        bounds2=_boundaries(other,'switch','switch')

        start=None                   #setbystart/stop
        recs1=None                   #setbystart
        enabled=difference           #changedbyswitch
        forvalue,flag,recsinsorted(chain(bounds1,bounds2)):
            ifflag=='start':
                start=value
                recs1=recs
            elifflag=='stop':
                ifenabledandstart<value:
                    append((start,value,recs1))
                start=None
            else:
                ifnotenabledandstartisnotNone:
                    start=value
                ifenabledandstartisnotNoneandstart<value:
                    append((start,value,recs1))
                enabled=notenabled

        returnresult


classResourceCalendar(models.Model):
    """Calendarmodelforaresource.Ithas

     -attendance_ids:listofresource.calendar.attendancethatareaworking
                       intervalinagivenweekday.
     -leave_ids:listofleaveslinkedtothiscalendar.Aleavecanbegeneral
                  orlinkedtoaspecificresource,dependingonitsresource_id.

    Allmethodsinthisclassuseintervals.Anintervalisatupleholding
    (begin_datetime,end_datetime).Alistofintervalsisthereforealistof
    tuples,holdingseveralintervalsofworkorleaves."""
    _name="resource.calendar"
    _description="ResourceWorkingTime"

    @api.model
    defdefault_get(self,fields):
        res=super(ResourceCalendar,self).default_get(fields)
        ifnotres.get('name')andres.get('company_id'):
            res['name']=_('WorkingHoursof%s',self.env['res.company'].browse(res['company_id']).name)
        if'attendance_ids'infieldsandnotres.get('attendance_ids'):
            company_id=res.get('company_id',self.env.company.id)
            company=self.env['res.company'].browse(company_id)
            company_attendance_ids=company.resource_calendar_id.attendance_ids
            ifcompany_attendance_ids:
                res['attendance_ids']=[
                    (0,0,{
                        'name':attendance.name,
                        'dayofweek':attendance.dayofweek,
                        'hour_from':attendance.hour_from,
                        'hour_to':attendance.hour_to,
                        'day_period':attendance.day_period,
                    })
                    forattendanceincompany_attendance_ids
                ]
            else:
                res['attendance_ids']=[
                    (0,0,{'name':_('MondayMorning'),'dayofweek':'0','hour_from':8,'hour_to':12,'day_period':'morning'}),
                    (0,0,{'name':_('MondayAfternoon'),'dayofweek':'0','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                    (0,0,{'name':_('TuesdayMorning'),'dayofweek':'1','hour_from':8,'hour_to':12,'day_period':'morning'}),
                    (0,0,{'name':_('TuesdayAfternoon'),'dayofweek':'1','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                    (0,0,{'name':_('WednesdayMorning'),'dayofweek':'2','hour_from':8,'hour_to':12,'day_period':'morning'}),
                    (0,0,{'name':_('WednesdayAfternoon'),'dayofweek':'2','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                    (0,0,{'name':_('ThursdayMorning'),'dayofweek':'3','hour_from':8,'hour_to':12,'day_period':'morning'}),
                    (0,0,{'name':_('ThursdayAfternoon'),'dayofweek':'3','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                    (0,0,{'name':_('FridayMorning'),'dayofweek':'4','hour_from':8,'hour_to':12,'day_period':'morning'}),
                    (0,0,{'name':_('FridayAfternoon'),'dayofweek':'4','hour_from':13,'hour_to':17,'day_period':'afternoon'})
                ]
        returnres

    name=fields.Char(required=True)
    active=fields.Boolean("Active",default=True,
                            help="Iftheactivefieldissettofalse,itwillallowyoutohidetheWorkingTimewithoutremovingit.")
    company_id=fields.Many2one(
        'res.company','Company',
        default=lambdaself:self.env.company)
    attendance_ids=fields.One2many(
        'resource.calendar.attendance','calendar_id','WorkingTime',
        compute='_compute_attendance_ids',store=True,readonly=False,copy=True)
    leave_ids=fields.One2many(
        'resource.calendar.leaves','calendar_id','TimeOff')
    global_leave_ids=fields.One2many(
        'resource.calendar.leaves','calendar_id','GlobalTimeOff',
        compute='_compute_global_leave_ids',store=True,readonly=False,
        domain=[('resource_id','=',False)],copy=True,
    )
    hours_per_day=fields.Float("AverageHourperDay",default=HOURS_PER_DAY,
                                 help="Averagehoursperdayaresourceissupposedtoworkwiththiscalendar.")
    tz=fields.Selection(
        _tz_get,string='Timezone',required=True,
        default=lambdaself:self._context.get('tz')orself.env.user.tzor'UTC',
        help="Thisfieldisusedinordertodefineinwhichtimezonetheresourceswillwork.")
    two_weeks_calendar=fields.Boolean(string="Calendarin2weeksmode")
    two_weeks_explanation=fields.Char('Explanation',compute="_compute_two_weeks_explanation")

    @api.depends('company_id')
    def_compute_attendance_ids(self):
        forcalendarinself.filtered(lambdac:notc._originorc._origin.company_id!=c.company_id):
            company_calendar=calendar.company_id.resource_calendar_id
            calendar.write({
                'two_weeks_calendar':company_calendar.two_weeks_calendar,
                'hours_per_day':company_calendar.hours_per_day,
                'tz':company_calendar.tz,
                'attendance_ids':[(5,0,0)]+[
                    (0,0,attendance._copy_attendance_vals())forattendanceincompany_calendar.attendance_idsifnotattendance.resource_id]
            })

    @api.depends('company_id')
    def_compute_global_leave_ids(self):
        forcalendarinself.filtered(lambdac:notc._originorc._origin.company_id!=c.company_id):
            calendar.write({
                'global_leave_ids':[(5,0,0)]+[
                    (0,0,leave._copy_leave_vals())forleaveincalendar.company_id.resource_calendar_id.global_leave_ids]
            })

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        ifdefaultisNone:
            default={}
        ifnotdefault.get('name'):
            default.update(name=_('%s(copy)')%(self.name))
        returnsuper(ResourceCalendar,self).copy(default)

    @api.constrains('attendance_ids')
    def_check_attendance_ids(self):
        forresourceinself:
            if(resource.two_weeks_calendarand
                    resource.attendance_ids.filtered(lambdaa:a.display_type=='line_section')and
                    notresource.attendance_ids.sorted('sequence')[0].display_type):
                raiseValidationError(_("Inacalendarwith2weeksmode,allperiodsneedtobeinthesections."))

    @api.depends('two_weeks_calendar')
    def_compute_two_weeks_explanation(self):
        today=fields.Date.today()
        week_type=_("odd")ifint(math.floor((today.toordinal()-1)/7)%2)else_("even")
        first_day=date_utils.start_of(today,'week')
        last_day=date_utils.end_of(today,'week')
        self.two_weeks_explanation="Thisweek(from%sto%s)isan%sweek."%(first_day,last_day,week_type)

    def_get_global_attendances(self):
        returnself.attendance_ids.filtered(lambdaattendance:
            notattendance.date_fromandnotattendance.date_to
            andnotattendance.resource_idandnotattendance.display_type)

    def_compute_hours_per_day(self,attendances):
        ifnotattendances:
            return0

        hour_count=0.0
        forattendanceinattendances:
            hour_count+=attendance.hour_to-attendance.hour_from

        ifself.two_weeks_calendar:
            number_of_days=len(set(attendances.filtered(lambdacal:cal.week_type=='1').mapped('dayofweek')))
            number_of_days+=len(set(attendances.filtered(lambdacal:cal.week_type=='0').mapped('dayofweek')))
        else:
            number_of_days=len(set(attendances.mapped('dayofweek')))

        returnfloat_round(hour_count/float(number_of_days),precision_digits=2)

    @api.onchange('attendance_ids','two_weeks_calendar')
    def_onchange_hours_per_day(self):
        attendances=self._get_global_attendances()
        self.hours_per_day=self._compute_hours_per_day(attendances)

    defswitch_calendar_type(self):
        ifself==self.env.company.resource_calendar_id:
            raiseUserError(_('Impossibletoswitchcalendartypeforthedefaultcompanyschedule.'))

        ifnotself.two_weeks_calendar:
            self.attendance_ids.unlink()
            self.attendance_ids=[
                (0,0,{
                    'name':'Evenweek',
                    'dayofweek':'0',
                    'sequence':'0',
                    'hour_from':0,
                    'day_period':'morning',
                    'week_type':'0',
                    'hour_to':0,
                    'display_type':
                    'line_section'}),
                (0,0,{
                    'name':'Oddweek',
                    'dayofweek':'0',
                    'sequence':'25',
                    'hour_from':0,
                    'day_period':
                    'morning',
                    'week_type':'1',
                    'hour_to':0,
                    'display_type':'line_section'}),
            ]

            self.two_weeks_calendar=True
            default_attendance=self.default_get('attendance_ids')['attendance_ids']
            foridx,attinenumerate(default_attendance):
                att[2]["week_type"]='0'
                att[2]["sequence"]=idx+1
            self.attendance_ids=default_attendance
            foridx,attinenumerate(default_attendance):
                att[2]["week_type"]='1'
                att[2]["sequence"]=idx+26
            self.attendance_ids=default_attendance
        else:
            self.two_weeks_calendar=False
            self.attendance_ids.unlink()
            self.attendance_ids=self.default_get('attendance_ids')['attendance_ids']
        self._onchange_hours_per_day()

    @api.onchange('attendance_ids')
    def_onchange_attendance_ids(self):
        ifnotself.two_weeks_calendar:
            return

        even_week_seq=self.attendance_ids.filtered(lambdaatt:att.display_type=='line_section'andatt.week_type=='0')
        odd_week_seq=self.attendance_ids.filtered(lambdaatt:att.display_type=='line_section'andatt.week_type=='1')
        iflen(even_week_seq)!=1orlen(odd_week_seq)!=1:
            raiseValidationError(_("Youcan'tdeletesectionbetweenweeks."))

        even_week_seq=even_week_seq.sequence
        odd_week_seq=odd_week_seq.sequence

        forlineinself.attendance_ids.filtered(lambdaatt:att.display_typeisFalse):
            ifeven_week_seq>odd_week_seq:
                line.week_type='1'ifeven_week_seq>line.sequenceelse'0'
            else:
                line.week_type='0'ifodd_week_seq>line.sequenceelse'1'

    def_check_overlap(self,attendance_ids):
        """attendance_idscorrespondtoattendanceofaweek,
            willcheckforeachdayofweekthattherearenosuperimpose."""
        result=[]
        forattendanceinattendance_ids.filtered(lambdaatt:notatt.date_fromandnotatt.date_to):
            #0.000001isaddedtoeachstarthourtoavoidtodetecttwocontiguousintervalsassuperimposing.
            #IndeedIntervalsfunctionwilljoin2intervalswiththestartandstophourcorresponding.
            result.append((int(attendance.dayofweek)*24+attendance.hour_from+0.000001,int(attendance.dayofweek)*24+attendance.hour_to,attendance))

        iflen(Intervals(result))!=len(result):
            raiseValidationError(_("Attendancescan'toverlap."))

    @api.constrains('attendance_ids')
    def_check_attendance(self):
        #Avoidsuperimposeinattendance
        forcalendarinself:
            attendance_ids=calendar.attendance_ids.filtered(lambdaattendance:notattendance.resource_idandattendance.display_typeisFalse)
            ifcalendar.two_weeks_calendar:
                calendar._check_overlap(attendance_ids.filtered(lambdaattendance:attendance.week_type=='0'))
                calendar._check_overlap(attendance_ids.filtered(lambdaattendance:attendance.week_type=='1'))
            else:
                calendar._check_overlap(attendance_ids)

    #--------------------------------------------------
    #ComputationAPI
    #--------------------------------------------------
    #YTITODO:Removemeinmaster
    def_attendance_intervals(self,start_dt,end_dt,resource=None,domain=None,tz=None):
        ifresourceisNone:
            resource=self.env['resource.resource']
        returnself._attendance_intervals_batch(
            start_dt,end_dt,resources=resource,domain=domain,tz=tz
        )[resource.id]

    def_attendance_intervals_batch(self,start_dt,end_dt,resources=None,domain=None,tz=None):
        """Returntheattendanceintervalsinthegivendatetimerange.
            Thereturnedintervalsareexpressedinspecifiedtzorintheresource'stimezone.
        """
        self.ensure_one()
        resources=self.env['resource.resource']ifnotresourceselseresources
        assertstart_dt.tzinfoandend_dt.tzinfo
        self.ensure_one()
        combine=datetime.combine

        resources_list=list(resources)+[self.env['resource.resource']]
        resource_ids=[r.idforrinresources_list]
        domain=domainifdomainisnotNoneelse[]
        domain=expression.AND([domain,[
            ('calendar_id','=',self.id),
            ('resource_id','in',resource_ids),
            ('display_type','=',False),
        ]])

        #foreachattendancespec,generatetheintervalsinthedaterange
        cache_dates=defaultdict(dict)
        cache_deltas=defaultdict(dict)
        result=defaultdict(list)
        forattendanceinself.env['resource.calendar.attendance'].search(domain):
            forresourceinresources_list:
                #expressalldatesandtimesinspecifiedtzorintheresource'stimezone
                tz=tziftzelsetimezone((resourceorself).tz)
                if(tz,start_dt)incache_dates:
                    start=cache_dates[(tz,start_dt)]
                else:
                    start=start_dt.astimezone(tz)
                    cache_dates[(tz,start_dt)]=start
                if(tz,end_dt)incache_dates:
                    end=cache_dates[(tz,end_dt)]
                else:
                    end=end_dt.astimezone(tz)
                    cache_dates[(tz,end_dt)]=end

                start=start.date()
                ifattendance.date_from:
                    start=max(start,attendance.date_from)
                until=end.date()
                ifattendance.date_to:
                    until=min(until,attendance.date_to)
                ifattendance.week_type:
                    start_week_type=int(math.floor((start.toordinal()-1)/7)%2)
                    ifstart_week_type!=int(attendance.week_type):
                        #startmustbetheweekoftheattendance
                        #ifit'snotthecase,wemustremoveoneweek
                        start=start+relativedelta(weeks=-1)
                weekday=int(attendance.dayofweek)

                ifself.two_weeks_calendarandattendance.week_type:
                    days=rrule(WEEKLY,start,interval=2,until=until,byweekday=weekday)
                else:
                    days=rrule(DAILY,start,until=until,byweekday=weekday)

                fordayindays:
                    #Weneedtoexcludeincorrectdaysaccordingtore-definedstartpreviously
                    #withweeks=-1(Note:untiliscorrectlyhandled)
                    if(self.two_weeks_calendarandattendance.date_fromandattendance.date_from>day.date()):
                        continue
                    #attendancehoursareinterpretedintheresource'stimezone
                    hour_from=attendance.hour_from
                    if(tz,day,hour_from)incache_deltas:
                        dt0=cache_deltas[(tz,day,hour_from)]
                    else:
                        dt0=tz.localize(combine(day,float_to_time(hour_from)))
                        cache_deltas[(tz,day,hour_from)]=dt0

                    hour_to=attendance.hour_to
                    if(tz,day,hour_to)incache_deltas:
                        dt1=cache_deltas[(tz,day,hour_to)]
                    else:
                        dt1=tz.localize(combine(day,float_to_time(hour_to)))
                        cache_deltas[(tz,day,hour_to)]=dt1
                    result[resource.id].append((max(cache_dates[(tz,start_dt)],dt0),min(cache_dates[(tz,end_dt)],dt1),attendance))
        return{r.id:Intervals(result[r.id])forrinresources_list}

    def_leave_intervals(self,start_dt,end_dt,resource=None,domain=None,tz=None):
        ifresourceisNone:
            resource=self.env['resource.resource']
        returnself._leave_intervals_batch(
            start_dt,end_dt,resources=resource,domain=domain,tz=tz
        )[resource.id]

    def_leave_intervals_batch(self,start_dt,end_dt,resources=None,domain=None,tz=None):
        """Returntheleaveintervalsinthegivendatetimerange.
            Thereturnedintervalsareexpressedinspecifiedtzorinthecalendar'stimezone.
        """
        resources=self.env['resource.resource']ifnotresourceselseresources
        assertstart_dt.tzinfoandend_dt.tzinfo
        self.ensure_one()

        #forthecomputation,expressalldatetimesinUTC
        resources_list=list(resources)+[self.env['resource.resource']]
        resource_ids=[r.idforrinresources_list]
        ifdomainisNone:
            domain=[('time_type','=','leave')]
        domain=domain+[
            ('calendar_id','=',self.id),
            ('resource_id','in',resource_ids),
            ('date_from','<=',datetime_to_string(end_dt)),
            ('date_to','>=',datetime_to_string(start_dt)),
        ]

        #retrieveleaveintervalsin(start_dt,end_dt)
        result=defaultdict(lambda:[])
        tz_dates={}
        forleaveinself.env['resource.calendar.leaves'].search(domain):
            forresourceinresources_list:
                ifleave.resource_id.idnotin[False,resource.id]:
                    continue
                tz=tziftzelsetimezone((resourceorself).tz)
                if(tz,start_dt)intz_dates:
                    start=tz_dates[(tz,start_dt)]
                else:
                    start=start_dt.astimezone(tz)
                    tz_dates[(tz,start_dt)]=start
                if(tz,end_dt)intz_dates:
                    end=tz_dates[(tz,end_dt)]
                else:
                    end=end_dt.astimezone(tz)
                    tz_dates[(tz,end_dt)]=end
                dt0=string_to_datetime(leave.date_from).astimezone(tz)
                dt1=string_to_datetime(leave.date_to).astimezone(tz)
                result[resource.id].append((max(start,dt0),min(end,dt1),leave))

        return{r.id:Intervals(result[r.id])forrinresources_list}

    #YTITODO:Removemeinmaster
    def_work_intervals(self,start_dt,end_dt,resource=None,domain=None,tz=None):
        ifresourceisNone:
            resource=self.env['resource.resource']
        returnself._work_intervals_batch(
            start_dt,end_dt,resources=resource,domain=domain,tz=tz
        )[resource.id]

    def_work_intervals_batch(self,start_dt,end_dt,resources=None,domain=None,tz=None):
        """Returntheeffectiveworkintervalsbetweenthegivendatetimes."""
        ifnotresources:
            resources=self.env['resource.resource']
            resources_list=[resources]
        else:
            resources_list=list(resources)

        attendance_intervals=self._attendance_intervals_batch(start_dt,end_dt,resources,tz=tz)
        leave_intervals=self._leave_intervals_batch(start_dt,end_dt,resources,domain,tz=tz)
        return{
            r.id:(attendance_intervals[r.id]-leave_intervals[r.id])forrinresources_list
        }

    def_unavailable_intervals(self,start_dt,end_dt,resource=None,domain=None,tz=None):
        ifresourceisNone:
            resource=self.env['resource.resource']
        returnself._unavailable_intervals_batch(
            start_dt,end_dt,resources=resource,domain=domain,tz=tz
        )[resource.id]

    def_unavailable_intervals_batch(self,start_dt,end_dt,resources=None,domain=None,tz=None):
        """Returntheunavailableintervalsbetweenthegivendatetimes."""
        ifnotresources:
            resources=self.env['resource.resource']
            resources_list=[resources]
        else:
            resources_list=list(resources)

        resources_work_intervals=self._work_intervals_batch(start_dt,end_dt,resources,domain,tz)
        result={}
        forresourceinresources_list:
            work_intervals=[(start,stop)forstart,stop,metainresources_work_intervals[resource.id]]
            #start+flatten(intervals)+end
            work_intervals=[start_dt]+list(chain.from_iterable(work_intervals))+[end_dt]
            #putitbacktoUTC
            work_intervals=list(map(lambdadt:dt.astimezone(utc),work_intervals))
            #pickgroupsoftwo
            work_intervals=list(zip(work_intervals[0::2],work_intervals[1::2]))
            result[resource.id]=work_intervals
        returnresult

    #--------------------------------------------------
    #PrivateMethods/Helpers
    #--------------------------------------------------

    def_get_days_data(self,intervals,day_total):
        """
        helperfunctiontocomputedurationof`intervals`
        expressedindaysandhours.
        `day_total`isadict{date:n_hours}withthenumberofhoursforeachday.
        """
        day_hours=defaultdict(float)
        forstart,stop,metainintervals:
            day_hours[start.date()]+=(stop-start).total_seconds()/3600

        #computenumberofdaysasquarters
        days=sum(
            float_utils.round(ROUNDING_FACTOR*day_hours[day]/day_total[day])/ROUNDING_FACTORifday_total[day]else0
            fordayinday_hours
        )
        return{
            'days':days,
            'hours':sum(day_hours.values()),
        }

    #YTITODO:Removemeinmaster
    def_get_day_total(self,from_datetime,to_datetime,resource=None):
        ifresourceisNone:
            resource=self.env['resource.resource']
        returnself._get_resources_day_total(from_datetime,to_datetime,resources=resource)[resource.id]

    def_get_resources_day_total(self,from_datetime,to_datetime,resources=None):
        """
        @returndictwithhoursofattendanceineachdaybetween`from_datetime`and`to_datetime`
        """
        self.ensure_one()
        resources=self.env['resource.resource']ifnotresourceselseresources
        resources_list=list(resources)+[self.env['resource.resource']]
        #totalhoursperday: retrieveattendanceswithoneextradaymargin,
        #inordertocomputethetotalhoursonthefirstandlastdays
        from_full=from_datetime-timedelta(days=1)
        to_full=to_datetime+timedelta(days=1)
        intervals=self._attendance_intervals_batch(from_full,to_full,resources=resources)

        result=defaultdict(lambda:defaultdict(float))
        forresourceinresources_list:
            day_total=result[resource.id]
            forstart,stop,metainintervals[resource.id]:
                day_total[start.date()]+=(stop-start).total_seconds()/3600
        returnresult

    def_get_closest_work_time(self,dt,match_end=False,resource=None,search_range=None):
        """Returntheclosestworkintervalboundarywithinthesearchrange.
        Consideronlystartsofintervalsunless`match_end`isTrue.Itwillthenonlyconsider
        endsofintervals.
        :paramdt:referencedatetime
        :parammatch_end:wethertosearchforthebeginingofanintervalortheend.
        :paramsearch_range:timeintervalconsidered.Defaultstotheentiredayof`dt`
        :rtype:datetime|None
        """
        definterval_dt(interval):
            returninterval[1ifmatch_endelse0]

        tz=resource.tzifresourceelseself.tz
        ifresourceisNone:
            resource=self.env['resource.resource']

        ifnotdt.tzinfoorsearch_rangeandnot(search_range[0].tzinfoandsearch_range[1].tzinfo):
            raiseValueError('Provideddatetimesneedstobetimezoned')

        dt=dt.astimezone(timezone(tz))

        ifnotsearch_range:
            range_start=dt+relativedelta(hour=0,minute=0,second=0)
            range_end=dt+relativedelta(days=1,hour=0,minute=0,second=0)
        else:
            range_start,range_end=search_range

        ifnotrange_start<=dt<=range_end:
            returnNone
        work_intervals=sorted(
            self._work_intervals_batch(range_start,range_end,resource)[resource.id],
            key=lambdai:abs(interval_dt(i)-dt),
        )
        returninterval_dt(work_intervals[0])ifwork_intervalselseNone

    #--------------------------------------------------
    #ExternalAPI
    #--------------------------------------------------

    defget_work_hours_count(self,start_dt,end_dt,compute_leaves=True,domain=None):
        """
            `compute_leaves`controlswhetherornotthismethodistakinginto
            accountthegloballeaves.

            `domain`controlsthewayleavesarerecognized.
            Nonemeansdefaultvalue('time_type','=','leave')

            Countsthenumberofworkhoursbetweentwodatetimes.
        """
        self.ensure_one()
        #SettimezoneinUTCifnotimezoneisexplicitlygiven
        ifnotstart_dt.tzinfo:
            start_dt=start_dt.replace(tzinfo=utc)
        ifnotend_dt.tzinfo:
            end_dt=end_dt.replace(tzinfo=utc)

        ifcompute_leaves:
            intervals=self._work_intervals_batch(start_dt,end_dt,domain=domain)[False]
        else:
            intervals=self._attendance_intervals_batch(start_dt,end_dt)[False]

        returnsum(
            (stop-start).total_seconds()/3600
            forstart,stop,metainintervals
        )

    defget_work_duration_data(self,from_datetime,to_datetime,compute_leaves=True,domain=None):
        """
            Gettheworkingduration(indaysandhours)foragivenperiod,only
            basedonthecurrentcalendar.Thismethoddoesnotuseresourceto
            computeit.

            `domain`isusedinordertorecognisetheleavestotake,
            Nonemeansdefaultvalue('time_type','=','leave')

            Returnsadict{'days':n,'hours':h}containingthe
            quantityofworkingtimeexpressedasdaysandashours.
        """
        #naivedatetimesaremadeexplicitinUTC
        from_datetime,dummy=make_aware(from_datetime)
        to_datetime,dummy=make_aware(to_datetime)

        day_total=self._get_resources_day_total(from_datetime,to_datetime)[False]

        #actualhoursperday
        ifcompute_leaves:
            intervals=self._work_intervals_batch(from_datetime,to_datetime,domain=domain)[False]
        else:
            intervals=self._attendance_intervals_batch(from_datetime,to_datetime)[False]

        returnself._get_days_data(intervals,day_total)

    defplan_hours(self,hours,day_dt,compute_leaves=False,domain=None,resource=None):
        """
        `compute_leaves`controlswhetherornotthismethodistakinginto
        accountthegloballeaves.

        `domain`controlsthewayleavesarerecognized.
        Nonemeansdefaultvalue('time_type','=','leave')

        Returndatetimeafterhavingplannedhours
        """
        day_dt,revert=make_aware(day_dt)

        #whichmethodtouseforretrievingintervals
        ifcompute_leaves:
            get_intervals=partial(self._work_intervals,domain=domain,resource=resource)
        else:
            get_intervals=self._attendance_intervals

        ifhours>=0:
            delta=timedelta(days=14)
            forninrange(100):
                dt=day_dt+delta*n
                forstart,stop,metainget_intervals(dt,dt+delta):
                    interval_hours=(stop-start).total_seconds()/3600
                    ifhours<=interval_hours:
                        returnrevert(start+timedelta(hours=hours))
                    hours-=interval_hours
            returnFalse
        else:
            hours=abs(hours)
            delta=timedelta(days=14)
            forninrange(100):
                dt=day_dt-delta*n
                forstart,stop,metainreversed(get_intervals(dt-delta,dt)):
                    interval_hours=(stop-start).total_seconds()/3600
                    ifhours<=interval_hours:
                        returnrevert(stop-timedelta(hours=hours))
                    hours-=interval_hours
            returnFalse

    defplan_days(self,days,day_dt,compute_leaves=False,domain=None):
        """
        `compute_leaves`controlswhetherornotthismethodistakinginto
        accountthegloballeaves.

        `domain`controlsthewayleavesarerecognized.
        Nonemeansdefaultvalue('time_type','=','leave')

        Returnsthedatetimeofadaysscheduling.
        """
        day_dt,revert=make_aware(day_dt)

        #whichmethodtouseforretrievingintervals
        ifcompute_leaves:
            get_intervals=partial(self._work_intervals,domain=domain)
        else:
            get_intervals=self._attendance_intervals

        ifdays>0:
            found=set()
            delta=timedelta(days=14)
            forninrange(100):
                dt=day_dt+delta*n
                forstart,stop,metainget_intervals(dt,dt+delta):
                    found.add(start.date())
                    iflen(found)==days:
                        returnrevert(stop)
            returnFalse

        elifdays<0:
            days=abs(days)
            found=set()
            delta=timedelta(days=14)
            forninrange(100):
                dt=day_dt-delta*n
                forstart,stop,metainreversed(get_intervals(dt-delta,dt)):
                    found.add(start.date())
                    iflen(found)==days:
                        returnrevert(start)
            returnFalse

        else:
            returnrevert(day_dt)

    def_get_max_number_of_hours(self,start,end):
        self.ensure_one()
        ifnotself.attendance_ids:
            return0
        mapped_data=defaultdict(lambda:0)
        forattendanceinself.attendance_ids.filtered(lambdaa:(nota.date_fromornota.date_to)or(a.date_from<=end.date()anda.date_to>=start.date())):
            mapped_data[(attendance.week_type,attendance.dayofweek)]+=attendance.hour_to-attendance.hour_from
        returnmax(mapped_data.values())


classResourceCalendarAttendance(models.Model):
    _name="resource.calendar.attendance"
    _description="WorkDetail"
    _order='week_type,dayofweek,hour_from'

    name=fields.Char(required=True)
    dayofweek=fields.Selection([
        ('0','Monday'),
        ('1','Tuesday'),
        ('2','Wednesday'),
        ('3','Thursday'),
        ('4','Friday'),
        ('5','Saturday'),
        ('6','Sunday')
        ],'DayofWeek',required=True,index=True,default='0')
    date_from=fields.Date(string='StartingDate')
    date_to=fields.Date(string='EndDate')
    hour_from=fields.Float(string='Workfrom',required=True,index=True,
        help="StartandEndtimeofworking.\n"
             "Aspecificvalueof24:00isinterpretedas23:59:59.999999.")
    hour_to=fields.Float(string='Workto',required=True)
    calendar_id=fields.Many2one("resource.calendar",string="Resource'sCalendar",required=True,ondelete='cascade')
    day_period=fields.Selection([('morning','Morning'),('afternoon','Afternoon')],required=True,default='morning')
    resource_id=fields.Many2one('resource.resource','Resource')
    week_type=fields.Selection([
        ('1','Oddweek'),
        ('0','Evenweek')
        ],'WeekEven/Odd',default=False)
    two_weeks_calendar=fields.Boolean("Calendarin2weeksmode",related='calendar_id.two_weeks_calendar')
    display_type=fields.Selection([
        ('line_section',"Section")],default=False,help="TechnicalfieldforUXpurpose.")
    sequence=fields.Integer(default=10,
        help="Givesthesequenceofthislinewhendisplayingtheresourcecalendar.")

    @api.onchange('hour_from','hour_to')
    def_onchange_hours(self):
        #avoidnegativeoraftermidnight
        self.hour_from=min(self.hour_from,23.99)
        self.hour_from=max(self.hour_from,0.0)
        self.hour_to=min(self.hour_to,23.99)
        self.hour_to=max(self.hour_to,0.0)

        #avoidwrongorder
        self.hour_to=max(self.hour_to,self.hour_from)

    def_copy_attendance_vals(self):
        self.ensure_one()
        return{
            'name':self.name,
            'dayofweek':self.dayofweek,
            'date_from':self.date_from,
            'date_to':self.date_to,
            'hour_from':self.hour_from,
            'hour_to':self.hour_to,
            'day_period':self.day_period,
            'week_type':self.week_type,
            'display_type':self.display_type,
            'sequence':self.sequence,
        }

classResourceResource(models.Model):
    _name="resource.resource"
    _description="Resources"

    @api.model
    defdefault_get(self,fields):
        res=super(ResourceResource,self).default_get(fields)
        ifnotres.get('calendar_id')andres.get('company_id'):
            company=self.env['res.company'].browse(res['company_id'])
            res['calendar_id']=company.resource_calendar_id.id
        returnres

    name=fields.Char(required=True)
    active=fields.Boolean(
        'Active',default=True,
        help="IftheactivefieldissettoFalse,itwillallowyoutohidetheresourcerecordwithoutremovingit.")
    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company)
    resource_type=fields.Selection([
        ('user','Human'),
        ('material','Material')],string='ResourceType',
        default='user',required=True)
    user_id=fields.Many2one('res.users',string='User',help='Relatedusernamefortheresourcetomanageitsaccess.')
    time_efficiency=fields.Float(
        'EfficiencyFactor',default=100,required=True,
        help="Thisfieldisusedtocalculatetheexpecteddurationofaworkorderatthisworkcenter.Forexample,ifaworkordertakesonehourandtheefficiencyfactoris100%,thentheexpecteddurationwillbeonehour.Iftheefficiencyfactoris200%,howevertheexpecteddurationwillbe30minutes.")
    calendar_id=fields.Many2one(
        "resource.calendar",string='WorkingTime',
        default=lambdaself:self.env.company.resource_calendar_id,
        required=True,
        help="Definethescheduleofresource")
    tz=fields.Selection(
        _tz_get,string='Timezone',required=True,
        default=lambdaself:self._context.get('tz')orself.env.user.tzor'UTC',
        help="Thisfieldisusedinordertodefineinwhichtimezonetheresourceswillwork.")

    _sql_constraints=[
        ('check_time_efficiency','CHECK(time_efficiency>0)','Timeefficiencymustbestrictlypositive'),
    ]

    @api.constrains('time_efficiency')
    def_check_time_efficiency(self):
        forrecordinself:
            ifrecord.time_efficiency==0:
                raiseValidationError(_('Theefficiencyfactorcannotbeequalto0.'))

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            ifvalues.get('company_id')andnotvalues.get('calendar_id'):
                values['calendar_id']=self.env['res.company'].browse(values['company_id']).resource_calendar_id.id
            ifnotvalues.get('tz'):
                #retrievetimezoneonuserorcalendar
                tz=(self.env['res.users'].browse(values.get('user_id')).tzor
                      self.env['resource.calendar'].browse(values.get('calendar_id')).tz)
                iftz:
                    values['tz']=tz
        returnsuper(ResourceResource,self).create(vals_list)

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        ifdefaultisNone:
            default={}
        ifnotdefault.get('name'):
            default.update(name=_('%s(copy)')%(self.name))
        returnsuper(ResourceResource,self).copy(default)

    @api.onchange('company_id')
    def_onchange_company_id(self):
        ifself.company_id:
            self.calendar_id=self.company_id.resource_calendar_id.id

    @api.onchange('user_id')
    def_onchange_user_id(self):
        ifself.user_id:
            self.tz=self.user_id.tz

    def_get_work_interval(self,start,end):
        #Deprecatedmethod.Use`_adjust_to_calendar`instead
        returnself._adjust_to_calendar(start,end)

    def_adjust_to_calendar(self,start,end):
        """Adjustthegivenstartandenddatetimestotheclosesteffectivehoursencoded
        intheresourcecalendar.Onlyattendancesinthesamedayas`start`and`end`are
        considered(respectively).Ifnoattendanceisfoundduringthatday,theclosesthour
        isNone.
        e.g.simplifiedexample:
             giventwoattendances:8am-1pmand2pm-5pm,givenstart=9amandend=6pm
             resource._adjust_to_calendar(start,end)
             >>>{resource:(8am,5pm)}
        :return:Closestmatchingstartandendofworkingperiodsforeachresource
        :rtype:dict(resource,tuple(datetime|None,datetime|None))
        """
        start,revert_start_tz=make_aware(start)
        end,revert_end_tz=make_aware(end)
        result={}
        forresourceinself:
            calendar_start=resource.calendar_id._get_closest_work_time(start,resource=resource)
            search_range=None
            tz=timezone(resource.tz)
            ifcalendar_startandstart.astimezone(tz).date()==end.astimezone(tz).date():
                end=end.astimezone(tz)
                #Makesuretoonlysearchendafterstart
                search_range=(
                    start,
                    end+relativedelta(days=1,hour=0,minute=0,second=0),
                )
            calendar_end=resource.calendar_id._get_closest_work_time(end,match_end=True,resource=resource,search_range=search_range)
            result[resource]=(
                calendar_startandrevert_start_tz(calendar_start),
                calendar_endandrevert_end_tz(calendar_end),
            )
        returnresult


    def_get_unavailable_intervals(self,start,end):
        """Computetheintervalsduringwhichemployeeisunavailablewithhourgranularitybetweenstartandend
            Note:thismethodisusedinenterprise(forecastandplanning)

        """
        start_datetime=timezone_datetime(start)
        end_datetime=timezone_datetime(end)
        resource_mapping={}
        calendar_mapping=defaultdict(lambda:self.env['resource.resource'])
        forresourceinself:
            calendar_mapping[resource.calendar_id]|=resource

        forcalendar,resourcesincalendar_mapping.items():
            resources_unavailable_intervals=calendar._unavailable_intervals_batch(start_datetime,end_datetime,resources,tz=timezone(calendar.tz))
            resource_mapping.update(resources_unavailable_intervals)
        returnresource_mapping


classResourceCalendarLeaves(models.Model):
    _name="resource.calendar.leaves"
    _description="ResourceTimeOffDetail"
    _order="date_from"

    name=fields.Char('Reason')
    company_id=fields.Many2one(
        'res.company',related='calendar_id.company_id',string="Company",
        readonly=True,store=True)
    calendar_id=fields.Many2one('resource.calendar','WorkingHours',index=True)
    date_from=fields.Datetime('StartDate',required=True)
    date_to=fields.Datetime('EndDate',required=True)
    resource_id=fields.Many2one(
        "resource.resource",'Resource',index=True,
        help="Ifempty,thisisagenerictimeoffforthecompany.Ifaresourceisset,thetimeoffisonlyforthisresource")
    time_type=fields.Selection([('leave','TimeOff'),('other','Other')],default='leave',
                                 help="Whetherthisshouldbecomputedasatimeofforasworktime(eg:formation)")

    @api.constrains('date_from','date_to')
    defcheck_dates(self):
        ifself.filtered(lambdaleave:leave.date_from>leave.date_to):
            raiseValidationError(_('Thestartdateofthetimeoffmustbeearlierthantheenddate.'))

    @api.onchange('resource_id')
    defonchange_resource(self):
        ifself.resource_id:
            self.calendar_id=self.resource_id.calendar_id

    def_copy_leave_vals(self):
        self.ensure_one()
        return{
            'name':self.name,
            'date_from':self.date_from,
            'date_to':self.date_to,
            'time_type':self.time_type,
        }
