#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta
importmath
fromitertoolsimportrepeat

importbabel.dates
importlogging
importpytz

fromflectraimportapi,fields,models
fromflectraimporttools
fromflectra.addons.base.models.res_partnerimport_tz_get
fromflectra.addons.calendar.models.calendar_attendeeimportAttendee
fromflectra.addons.calendar.models.calendar_recurrenceimport(
    weekday_to_field,
    RRULE_TYPE_SELECTION,
    END_TYPE_SELECTION,
    MONTH_BY_SELECTION,
    WEEKDAY_SELECTION,
    BYDAY_SELECTION
)
fromflectra.tools.translateimport_
fromflectra.tools.miscimportget_lang
fromflectra.toolsimportpycompat
fromflectra.exceptionsimportUserError,ValidationError,AccessError

_logger=logging.getLogger(__name__)

SORT_ALIASES={
    'start':'sort_start',
    'start_date':'sort_start',
}

defget_weekday_occurence(date):
    """
    :returns:ocurrence

    >>>get_weekday_occurence(date(2019,12,17))
    3 #thirdTuesdayofthemonth

    >>>get_weekday_occurence(date(2019,12,25))
    -1 #lastFridayofthemonth
    """
    occurence_in_month=math.ceil(date.day/7)
    ifoccurence_in_monthin{4,5}: #fourthorfifthweekonthemonth->last
        return-1
    returnoccurence_in_month


classMeeting(models.Model):
    _name='calendar.event'
    _description="CalendarEvent"
    _order="startdesc"
    _inherit=["mail.thread"]

    @api.model
    defdefault_get(self,fields):
        #superdefault_model='crm.lead'foreasieruseinaddons
        ifself.env.context.get('default_res_model')andnotself.env.context.get('default_res_model_id'):
            self=self.with_context(
                default_res_model_id=self.env['ir.model'].sudo().search([
                    ('model','=',self.env.context['default_res_model'])
                ],limit=1).id
            )

        defaults=super(Meeting,self).default_get(fields)

        #supportactive_model/active_idasreplacementofdefault_*ifnotalreadygiven
        if'res_model_id'notindefaultsand'res_model_id'infieldsand\
                self.env.context.get('active_model')andself.env.context['active_model']!='calendar.event':
            defaults['res_model_id']=self.env['ir.model'].sudo().search([('model','=',self.env.context['active_model'])],limit=1).id
            defaults['res_model']=self.env.context.get('active_model')
        if'res_id'notindefaultsand'res_id'infieldsand\
                defaults.get('res_model_id')andself.env.context.get('active_id'):
            defaults['res_id']=self.env.context['active_id']

        returndefaults

    @api.model
    def_default_partners(self):
        """Whenactive_modelisres.partner,thecurrentpartnersshouldbeattendees"""
        partners=self.env.user.partner_id
        active_id=self._context.get('active_id')
        ifself._context.get('active_model')=='res.partner'andactive_id:
            ifactive_idnotinpartners.ids:
                partners|=self.env['res.partner'].browse(active_id)
        returnpartners

    def_find_my_attendee(self):
        """Returnthefirstattendeewheretheuserconnectedhasbeeninvited
            fromallthemeeting_idsinparameters.
        """
        self.ensure_one()
        forattendeeinself.attendee_ids:
            ifself.env.user.partner_id==attendee.partner_id:
                returnattendee
        returnFalse

    @api.model
    def_get_date_formats(self):
        """getcurrentdateandtimeformat,accordingtothecontextlang
            :return:atuplewith(formatdate,formattime)
        """
        lang=get_lang(self.env)
        return(lang.date_format,lang.time_format)

    @api.model
    def_get_recurrent_fields(self):
        return{'byday','until','rrule_type','month_by','event_tz','rrule',
                'interval','count','end_type','mo','tu','we','th','fr','sa',
                'su','day','weekday'}

    @api.model
    def_get_time_fields(self):
        return{'start','stop','start_date','stop_date'}

    @api.model
    def_get_custom_fields(self):
        all_fields=self.fields_get(attributes=['manual'])
        return{fnameforfnameinall_fieldsifall_fields[fname]['manual']}

    @api.model
    def_get_public_fields(self):
        returnself._get_recurrent_fields()|self._get_time_fields()|self._get_custom_fields()|{
            'id','active','allday',
            'duration','user_id','interval',
            'count','rrule','recurrence_id','show_as','privacy'}

    @api.model
    def_get_display_time(self,start,stop,zduration,zallday):
        """Returndateandtime(fromtofrom)basedondurationwithtimezoneinstring.Eg:
                1)ifuseradddurationfor2hours,return:August-23-2013at(04-30To06-30)(Europe/Brussels)
                2)ifeventallday,return:AllDay,July-31-2013
        """
        timezone=self._context.get('tz')orself.env.user.partner_id.tzor'UTC'

        #getdate/timeformataccordingtocontext
        format_date,format_time=self._get_date_formats()

        #convertdateandtimeintousertimezone
        self_tz=self.with_context(tz=timezone)
        date=fields.Datetime.context_timestamp(self_tz,fields.Datetime.from_string(start))
        date_deadline=fields.Datetime.context_timestamp(self_tz,fields.Datetime.from_string(stop))

        #convertintostringthedateandtime,usinguserformats
        to_text=pycompat.to_text
        date_str=to_text(date.strftime(format_date))
        time_str=to_text(date.strftime(format_time))

        ifzallday:
            display_time=_("AllDay,%(day)s",day=date_str)
        elifzduration<24:
            duration=date+timedelta(minutes=round(zduration*60))
            duration_time=to_text(duration.strftime(format_time))
            display_time=_(
                u"%(day)sat(%(start)sTo%(end)s)(%(timezone)s)",
                day=date_str,
                start=time_str,
                end=duration_time,
                timezone=timezone,
            )
        else:
            dd_date=to_text(date_deadline.strftime(format_date))
            dd_time=to_text(date_deadline.strftime(format_time))
            display_time=_(
                u"%(date_start)sat%(time_start)sTo\n%(date_end)sat%(time_end)s(%(timezone)s)",
                date_start=date_str,
                time_start=time_str,
                date_end=dd_date,
                time_end=dd_time,
                timezone=timezone,
            )
        returndisplay_time

    def_get_duration(self,start,stop):
        """Getthedurationvaluebetweenthe2givendates."""
        ifnotstartornotstop:
            return0
        duration=(stop-start).total_seconds()/3600
        returnround(duration,2)

    def_compute_is_highlighted(self):
        ifself.env.context.get('active_model')=='res.partner':
            partner_id=self.env.context.get('active_id')
            foreventinself:
                ifevent.partner_ids.filtered(lambdas:s.id==partner_id):
                    event.is_highlighted=True
                else:
                    event.is_highlighted=False
        else:
            foreventinself:
                event.is_highlighted=False

    name=fields.Char('MeetingSubject',required=True)

    attendee_status=fields.Selection(
        Attendee.STATE_SELECTION,string='AttendeeStatus',compute='_compute_attendee')
    display_time=fields.Char('EventTime',compute='_compute_display_time')
    start=fields.Datetime(
        'Start',required=True,tracking=True,default=fields.Date.today,
        help="Startdateofanevent,withouttimeforfulldaysevents")
    stop=fields.Datetime(
        'Stop',required=True,tracking=True,default=lambdaself:fields.Datetime.today()+timedelta(hours=1),
        compute='_compute_stop',readonly=False,store=True,
        help="Stopdateofanevent,withouttimeforfulldaysevents")

    allday=fields.Boolean('AllDay',default=False)
    start_date=fields.Date(
        'StartDate',store=True,tracking=True,
        compute='_compute_dates',inverse='_inverse_dates')
    stop_date=fields.Date(
        'EndDate',store=True,tracking=True,
        compute='_compute_dates',inverse='_inverse_dates')
    duration=fields.Float('Duration',compute='_compute_duration',store=True,readonly=False)
    description=fields.Text('Description')
    privacy=fields.Selection(
        [('public','Everyone'),
         ('private','Onlyme'),
         ('confidential','Onlyinternalusers')],
        'Privacy',default='public',required=True)
    location=fields.Char('Location',tracking=True,help="LocationofEvent")
    show_as=fields.Selection(
        [('free','Free'),
         ('busy','Busy')],'ShowTimeas',default='busy',required=True)

    #linkeddocument
    #LULTODOusefields.Reference?
    res_id=fields.Integer('DocumentID')
    res_model_id=fields.Many2one('ir.model','DocumentModel',ondelete='cascade')
    res_model=fields.Char(
        'DocumentModelName',related='res_model_id.model',readonly=True,store=True)
    activity_ids=fields.One2many('mail.activity','calendar_event_id',string='Activities')

    #redifinemessage_idstoremoveautojointoavoidsearchtocrashinget_recurrent_ids
    message_ids=fields.One2many(auto_join=False)

    user_id=fields.Many2one('res.users','Responsible',default=lambdaself:self.env.user)
    partner_id=fields.Many2one(
        'res.partner',string='ResponsibleContact',related='user_id.partner_id',readonly=True)
    active=fields.Boolean(
        'Active',default=True,
        help="Iftheactivefieldissettofalse,itwillallowyoutohidetheeventalarminformationwithoutremovingit.")
    categ_ids=fields.Many2many(
        'calendar.event.type','meeting_category_rel','event_id','type_id','Tags')
    attendee_ids=fields.One2many(
        'calendar.attendee','event_id','Participant')
    partner_ids=fields.Many2many(
        'res.partner','calendar_event_res_partner_rel',
        string='Attendees',default=_default_partners)
    alarm_ids=fields.Many2many(
        'calendar.alarm','calendar_alarm_calendar_event_rel',
        string='Reminders',ondelete="restrict")
    is_highlighted=fields.Boolean(
        compute='_compute_is_highlighted',string='IstheEventHighlighted')

    #RECURRENCEFIELD
    recurrency=fields.Boolean('Recurrent',help="RecurrentEvent")
    recurrence_id=fields.Many2one(
        'calendar.recurrence',string="RecurrenceRule",index=True)
    follow_recurrence=fields.Boolean(default=False)#Indicatesifaneventfollowstherecurrence,i.e.isnotanexception
    recurrence_update=fields.Selection([
        ('self_only',"Thisevent"),
        ('future_events',"Thisandfollowingevents"),
        ('all_events',"Allevents"),
    ],store=False,copy=False,default='self_only',
       help="Choosewhattodowithothereventsintherecurrence.UpdatingAllEventsisnotallowedwhendatesortimeismodified")

    #Thosefieldarepseudo-relatedfieldsofrecurrence_id.
    #Theycan'tbe"real"relatedfieldsbecauseitshouldworkatrecordcreation
    #whenrecurrence_idisnotcreatedyet.
    #Ifsomeofthesefieldsaresetandrecurrence_iddoesnotexists,
    #a`calendar.recurrence.rule`willbedynamicallycreated.
    rrule=fields.Char('RecurrentRule',compute='_compute_recurrence',readonly=False)
    rrule_type=fields.Selection(RRULE_TYPE_SELECTION,string='Recurrence',
                                  help="Lettheeventautomaticallyrepeatatthatinterval",
                                  compute='_compute_recurrence',readonly=False)
    event_tz=fields.Selection(
        _tz_get,string='Timezone',compute='_compute_recurrence',readonly=False)
    end_type=fields.Selection(
        END_TYPE_SELECTION,string='RecurrenceTermination',
        compute='_compute_recurrence',readonly=False)
    interval=fields.Integer(
        string='RepeatEvery',compute='_compute_recurrence',readonly=False,
        help="Repeatevery(Days/Week/Month/Year)")
    count=fields.Integer(
        string='Repeat',help="Repeatxtimes",compute='_compute_recurrence',readonly=False)
    mo=fields.Boolean('Mon',compute='_compute_recurrence',readonly=False)
    tu=fields.Boolean('Tue',compute='_compute_recurrence',readonly=False)
    we=fields.Boolean('Wed',compute='_compute_recurrence',readonly=False)
    th=fields.Boolean('Thu',compute='_compute_recurrence',readonly=False)
    fr=fields.Boolean('Fri',compute='_compute_recurrence',readonly=False)
    sa=fields.Boolean('Sat',compute='_compute_recurrence',readonly=False)
    su=fields.Boolean('Sun',compute='_compute_recurrence',readonly=False)
    month_by=fields.Selection(
        MONTH_BY_SELECTION,string='Option',compute='_compute_recurrence',readonly=False)
    day=fields.Integer('Dateofmonth',compute='_compute_recurrence',readonly=False)
    weekday=fields.Selection(WEEKDAY_SELECTION,compute='_compute_recurrence',readonly=False)
    byday=fields.Selection(BYDAY_SELECTION,compute='_compute_recurrence',readonly=False)
    until=fields.Date(compute='_compute_recurrence',readonly=False)

    def_compute_attendee(self):
        formeetinginself:
            attendee=meeting._find_my_attendee()
            meeting.attendee_status=attendee.stateifattendeeelse'needsAction'

    def_compute_display_time(self):
        formeetinginself:
            meeting.display_time=self._get_display_time(meeting.start,meeting.stop,meeting.duration,meeting.allday)

    @api.depends('allday','start','stop')
    def_compute_dates(self):
        """Adaptthevalueofstart_date(time)/stop_date(time)
            accordingtostart/stopfieldsandallday.Also,compute
            thedurationfornotalldaymeeting;otherwisethe
            durationissettozero,sincethemeetinglastalltheday.
        """
        formeetinginself:
            ifmeeting.alldayandmeeting.startandmeeting.stop:
                meeting.start_date=meeting.start.date()
                meeting.stop_date=meeting.stop.date()
            else:
                meeting.start_date=False
                meeting.stop_date=False

    @api.depends('stop','start')
    def_compute_duration(self):
        foreventinself.with_context(dont_notify=True):
            event.duration=self._get_duration(event.start,event.stop)

    @api.depends('start','duration')
    def_compute_stop(self):
        #stopanddurationfieldsbothdependsonthestartfield.
        #Buttheyalsodependsoneachother.
        #Whenstartisupdated,wewanttoupdatethestopdatetimebasedon
        #the*current*duration.Inotherwords,wewant:changestart=>keepthedurationfixedand
        #recomputestopaccordingly.
        #However,whilecomputingstop,durationismarkedtoberecomputed.Calling`event.duration`wouldtrigger
        #itsrecomputation.Toavoidthiswemanuallymarkthefieldascomputed.
        duration_field=self._fields['duration']
        self.env.remove_to_compute(duration_field,self)
        foreventinself:
            #Roundtheduration(inhours)totheminutetoavoidweirdsituationswheretheevent
            #stopsat4:19:59,laterdisplayedas4:19.
            event.stop=event.startandevent.start+timedelta(minutes=round((event.durationor1.0)*60))
            ifevent.allday:
                event.stop-=timedelta(seconds=1)

    def_inverse_dates(self):
        """Thismethodisusedtosetthestartandstopvaluesofalldayevents.
            Thecalendarviewneedsdate_startanddate_stopvaluestodisplaycorrectlythealldayeventsacross
            severaldays.Astheusereditthe{start,stop}_datefieldswhenalldayistrue,
            thisinversemethodisneededtoupdatethe start/stopvalueandhavearelevantcalendarview.
        """
        formeetinginself:
            ifmeeting.allday:

                #Conventionbreak:
                #stopandstartareNOTinUTCinalldayevent
                #inthiscase,theyactuallyrepresentadate
                #becausefullcalendarjustdropstimesforfulldayevents.
                #i.e.Christmasison25/12foreveryone
                #evenifpeopledon'tcelebrateitsimultaneously
                enddate=fields.Datetime.from_string(meeting.stop_date)
                enddate=enddate.replace(hour=18)

                startdate=fields.Datetime.from_string(meeting.start_date)
                startdate=startdate.replace(hour=8) #Set8AM

                meeting.write({
                    'start':startdate.replace(tzinfo=None),
                    'stop':enddate.replace(tzinfo=None)
                })

    @api.constrains('start','stop','start_date','stop_date')
    def_check_closing_date(self):
        formeetinginself:
            ifnotmeeting.alldayandmeeting.startandmeeting.stopandmeeting.stop<meeting.start:
                raiseValidationError(
                    _('Theendingdateandtimecannotbeearlierthanthestartingdateandtime.')+'\n'+
                    _("Meeting'%(name)s'starts'%(start_datetime)s'andends'%(end_datetime)s'",
                      name=meeting.name,
                      start_datetime=meeting.start,
                      end_datetime=meeting.stop
                    )
                )
            ifmeeting.alldayandmeeting.start_dateandmeeting.stop_dateandmeeting.stop_date<meeting.start_date:
                raiseValidationError(
                    _('Theendingdatecannotbeearlierthanthestartingdate.')+'\n'+
                    _("Meeting'%(name)s'starts'%(start_datetime)s'andends'%(end_datetime)s'",
                      name=meeting.name,
                      start_datetime=meeting.start,
                      end_datetime=meeting.stop
                    )
                )

    ####################################################
    #CalendarBusiness,Reccurency,...
    ####################################################

    @api.depends('recurrence_id','recurrency')
    def_compute_recurrence(self):
        recurrence_fields=self._get_recurrent_fields()
        false_values={field:Falseforfieldinrecurrence_fields} #computesneedtosetavalue
        defaults=self.env['calendar.recurrence'].default_get(recurrence_fields)
        default_rrule_values=self.recurrence_id.default_get(recurrence_fields)
        foreventinself:
            ifevent.recurrency:
                event.update(defaults) #defaultrecurrencevaluesareneededtocorrectlycomputetherecurrenceparams
                event_values=event._get_recurrence_params()
                rrule_values={
                    field:event.recurrence_id[field]
                    forfieldinrecurrence_fields
                    ifevent.recurrence_id[field]
                }
                rrule_values=rrule_valuesordefault_rrule_values
                event.update({**false_values,**event_values,**rrule_values})
            else:
                event.update(false_values)

    def_get_ics_file(self):
        """ReturnsiCalendarfilefortheeventinvitation.
            :returnsadictof.icsfilecontentforeachmeeting
        """
        result={}

        defics_datetime(idate,allday=False):
            ifidate:
                ifallday:
                    returnidate
                returnidate.replace(tzinfo=pytz.timezone('UTC'))
            returnFalse

        try:
            #FIXME:whyisn'tthisinCalDAV?
            importvobject
        exceptImportError:
            _logger.warning("The`vobject`Pythonmoduleisnotinstalled,soiCalfilegenerationisunavailable.Pleaseinstallthe`vobject`Pythonmodule")
            returnresult

        formeetinginself:
            cal=vobject.iCalendar()
            event=cal.add('vevent')

            ifnotmeeting.startornotmeeting.stop:
                raiseUserError(_("Firstyouhavetospecifythedateoftheinvitation."))
            event.add('created').value=ics_datetime(fields.Datetime.now())
            event.add('dtstart').value=ics_datetime(meeting.start,meeting.allday)
            event.add('dtend').value=ics_datetime(meeting.stop,meeting.allday)
            event.add('summary').value=meeting.name
            ifmeeting.description:
                event.add('description').value=meeting.description
            ifmeeting.location:
                event.add('location').value=meeting.location
            ifmeeting.rrule:
                event.add('rrule').value=meeting.rrule

            ifmeeting.alarm_ids:
                foralarminmeeting.alarm_ids:
                    valarm=event.add('valarm')
                    interval=alarm.interval
                    duration=alarm.duration
                    trigger=valarm.add('TRIGGER')
                    trigger.params['related']=["START"]
                    ifinterval=='days':
                        delta=timedelta(days=duration)
                    elifinterval=='hours':
                        delta=timedelta(hours=duration)
                    elifinterval=='minutes':
                        delta=timedelta(minutes=duration)
                    trigger.value=delta
                    valarm.add('DESCRIPTION').value=alarm.nameoru'Flectra'
            forattendeeinmeeting.attendee_ids:
                attendee_add=event.add('attendee')
                attendee_add.value=u'MAILTO:'+(attendee.emailoru'')
            event.add('organizer').value=u'MAILTO:'+(meeting.user_id.emailoru'')
            result[meeting.id]=cal.serialize().encode('utf-8')

        returnresult

    def_attendees_values(self,partner_commands):
        """
        :parampartner_commands:ORMcommandsforpartner_idfield(0and1commandsnotsupported)
        :return:associatedattendee_idsORMcommands
        """
        attendee_commands=[]

        removed_partner_ids=[]
        added_partner_ids=[]
        forcommandinpartner_commands:
            op=command[0]
            ifopin(2,3): #Removepartner
                removed_partner_ids+=[command[1]]
            elifop==6: #Replaceall
                removed_partner_ids+=set(self.attendee_ids.mapped('partner_id').ids)-set(command[2]) #Don'trecreateattendeeifpartneralreadyattendtheevent
                added_partner_ids+=set(command[2])-set(self.attendee_ids.mapped('partner_id').ids)
            elifop==4:
                added_partner_ids+=[command[1]]ifcommand[1]notinself.attendee_ids.mapped('partner_id').idselse[]
            #commands0and1notsupported

        attendees_to_unlink=self.env['calendar.attendee'].search([
            ('event_id','in',self.ids),
            ('partner_id','in',removed_partner_ids),
        ])ifselfelseself.env['calendar.attendee']
        attendee_commands+=[[2,attendee.id]forattendeeinattendees_to_unlink] #Removesanddelete

        attendee_commands+=[
            [0,0,dict(partner_id=partner_id)]
            forpartner_idinadded_partner_ids
        ]
        returnattendee_commands

    defget_interval(self,interval,tz=None):
        """Formatandlocalizesomedatestobeusedinemailtemplates
            :paramstringinterval:Among'day','month','dayname'and'time'indicatingthedesiredformatting
            :paramstringtz:Timezoneindicator(optional)
            :returnunicode:Formatteddateortime(asunicodestring,topreventjinja2crash)
        """
        self.ensure_one()
        date=fields.Datetime.from_string(self.start)
        result=''

        iftz:
            timezone=pytz.timezone(tzor'UTC')
            date=date.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

        ifinterval=='day':
            #Daynumber(1-31)
            result=str(date.day)

        elifinterval=='month':
            #Localizedmonthnameandyear
            result=babel.dates.format_date(date=date,format='MMMMy',locale=get_lang(self.env).code)

        elifinterval=='dayname':
            #Localizeddayname
            result=babel.dates.format_date(date=date,format='EEEE',locale=get_lang(self.env).code)

        elifinterval=='time':
            #Localizedtime
            #FIXME:formatsarespecificallyencodedtobytes,maybeusebabel?
            dummy,format_time=self._get_date_formats()
            result=tools.ustr(date.strftime(format_time+"%Z"))

        returnresult

    defget_display_time_tz(self,tz=False):
        """getthedisplay_timeofthemeeting,forcingthetimezone.Thismethodiscalledfromemailtemplate,tonotusesudo()."""
        self.ensure_one()
        iftz:
            self=self.with_context(tz=tz)
        returnself._get_display_time(self.start,self.stop,self.duration,self.allday)

    defaction_open_calendar_event(self):
        ifself.res_modelandself.res_id:
            returnself.env[self.res_model].browse(self.res_id).get_formview_action()
        returnFalse

    defaction_sendmail(self):
        email=self.env.user.email
        ifemail:
            formeetinginself:
                meeting.attendee_ids._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')
        returnTrue

    def_apply_recurrence_values(self,values,future=True):
        """Applythenewrecurrencerulesin`values`.Createarecurrenceifitdoesnotexist
        andcreateallmissingeventsaccordingtotherrule.
        Ifthechangesareappliedtofuture
        eventsonly,anewrecurrenceiscreatedwiththeupdatedrrule.

        :paramvalues:newrecurrencevaluestoapply
        :paramfuture:rrulevaluesareappliedtofutureeventsonlyifTrue.
                       Rrulechangesareappliedtoalleventsintherecurrenceotherwise.
                       (ignoredifnorecurrenceexistsyet).
        :return:eventsdetachedfromtherecurrence
        """
        ifnotvalues:
            returnself.browse()
        recurrence_vals=[]
        to_update=self.env['calendar.recurrence']
        foreventinself:
            ifnotevent.recurrence_id:
                recurrence_vals+=[dict(values,base_event_id=event.id,calendar_event_ids=[(4,event.id)])]
            eliffuture:
                to_update|=event.recurrence_id._split_from(event,values)
        self.write({'recurrency':True,'follow_recurrence':True})
        to_update|=self.env['calendar.recurrence'].create(recurrence_vals)
        returnto_update._apply_recurrence()

    def_get_recurrence_params(self):
        ifnotself:
            return{}
        event_date=self._get_start_date()
        weekday_field_name=weekday_to_field(event_date.weekday())
        return{
            weekday_field_name:True,
            'weekday':weekday_field_name.upper(),
            'byday':str(get_weekday_occurence(event_date)),
            'day':event_date.day,
        }

    def_get_start_date(self):
        """Returntheeventstartingdateintheevent'stimezone.
        Ifnostartingtimeisassigned(yet),returntodayasdefault
        :return:date
        """
        ifnotself.start:
            returnfields.Date.today()
        ifself.recurrencyandself.event_tz:
            tz=pytz.timezone(self.event_tz)
            returnpytz.utc.localize(self.start).astimezone(tz).date()
        returnself.start.date()

    def_split_recurrence(self,time_values):
        """Applytimechangestoeventsandupdatetherecurrenceaccordingly.

        :return:detachedevents
        """
        self.ensure_one()
        ifnottime_values:
            returnself.browse()
        ifself.follow_recurrenceandself.recurrency:
            previous_week_day_field=weekday_to_field(self._get_start_date().weekday())
        else:
            #Whenwetrytochangerecurrencevaluesofaneventnotfollowingtherecurrence,wegettheparametersfrom
            #thebase_event
            previous_week_day_field=weekday_to_field(self.recurrence_id.base_event_id._get_start_date().weekday())
        self.write(time_values)
        returnself._apply_recurrence_values({
            previous_week_day_field:False,
            **self._get_recurrence_params(),
        },future=True)

    def_break_recurrence(self,future=True):
        """Breakstheevent'srecurrence.
        Stoptherecurrenceatthecurrenteventif`future`isTrue,leavingpasteventsintherecurrence.
        If`future`isFalse,alleventsintherecurrencearedetachedandtherecurrenceitselfisunlinked.
        :return:detachedeventsexcludingthecurrentevents
        """
        recurrences_to_unlink=self.env['calendar.recurrence']
        detached_events=self.env['calendar.event']
        foreventinself:
            recurrence=event.recurrence_id
            iffuture:
                detached_events|=recurrence._stop_at(event)
            else:
                detached_events|=recurrence.calendar_event_ids
                recurrence.calendar_event_ids.recurrence_id=False
                recurrences_to_unlink|=recurrence
        recurrences_to_unlink.with_context(archive_on_error=True).unlink()
        returndetached_events-self

    defwrite(self,values):
        detached_events=self.env['calendar.event']
        recurrence_update_setting=values.pop('recurrence_update',None)
        update_recurrence=recurrence_update_settingin('all_events','future_events')andlen(self)==1
        break_recurrence=values.get('recurrency')isFalse

        update_alarms=False
        update_time=False
        if'partner_ids'invalues:
            values['attendee_ids']=self._attendees_values(values['partner_ids'])
            update_alarms=True

        time_fields=self.env['calendar.event']._get_time_fields()
        ifany(values.get(key)forkeyintime_fields)or'alarm_ids'invalues:
            update_alarms=True
            update_time=True

        if(notrecurrence_update_settingorrecurrence_update_setting=='self_only'andlen(self)==1)and'follow_recurrence'notinvalues:
            ifany({field:values.get(field)forfieldintime_fieldsiffieldinvalues}):
                values['follow_recurrence']=False

        previous_attendees=self.attendee_ids

        recurrence_values={field:values.pop(field)forfieldinself._get_recurrent_fields()iffieldinvalues}
        ifupdate_recurrence:
            ifbreak_recurrence:
                #Updatethisevent
                detached_events|=self._break_recurrence(future=recurrence_update_setting=='future_events')
            else:
                update_start=self.startifrecurrence_update_setting=='future_events'elseNone
                time_values={field:values.pop(field)forfieldintime_fieldsiffieldinvalues}
                ifnotupdate_startand(time_valuesorrecurrence_values):
                    raiseUserError(_("UpdatingAllEventsisnotallowedwhendatesortimeismodified.Youcanonlyupdateoneparticulareventandfollowingevents."))
                detached_events|=self._split_recurrence(time_values)
                self.recurrence_id._write_events(values,dtstart=update_start)
        else:
            super().write(values)
            self._sync_activities(fields=values.keys())

        #Wereapplyrecurrenceforfutureeventsandwhenweaddarruleand'recurrency'==Trueontheevent
        ifrecurrence_update_settingnotin['self_only','all_events']andnotbreak_recurrence:
            detached_events|=self._apply_recurrence_values(recurrence_values,future=recurrence_update_setting=='future_events')

        (detached_events&self).active=False
        (detached_events-self).with_context(archive_on_error=True).unlink()

        #Notifyattendeesifthereisanalarmonthemodifiedevent,oriftherewasanalarm
        #thathasjustbeenremoved,asitmighthavechangedtheirnexteventnotification
        ifnotself.env.context.get('dont_notify')andupdate_alarms:
            self.env['calendar.alarm_manager']._notify_next_alarm(self.partner_ids.ids)
        attendee_update_events=self.filtered(lambdaev:ev.user_id!=self.env.user)
        ifupdate_timeandattendee_update_events:
            #Anotheruserupdatetheeventtimefields.Itshouldnotbeautoacceptedfortheorganizer.
            #Thispreventweirdbehaviorwhenausermodifiedfutureeventstimefieldsand
            #thebaseeventofarecurrenceisacceptedbytheorganizerbutnotthefollowingevents
            attendee_update_events.attendee_ids.filtered(lambdaatt:self.user_id.partner_id==att.partner_id).write({'state':'needsAction'})

        current_attendees=self.filtered('active').attendee_ids
        if'partner_ids'invalues:
            (current_attendees-previous_attendees)._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')
        ifnotself.env.context.get('is_calendar_event_new')and'start'invalues:
            start_date=fields.Datetime.to_datetime(values.get('start'))
            #Onlynotifyonfutureevents
            ifstart_dateandstart_date>=fields.Datetime.now():
                (current_attendees&previous_attendees)._send_mail_to_attendees('calendar.calendar_template_meeting_changedate',ignore_recurrence=notupdate_recurrence)

        returnTrue

    @api.model_create_multi
    defcreate(self,vals_list):
        #Preventsendingupdatenotificationwhen_inverse_datesiscalled
        self=self.with_context(is_calendar_event_new=True)

        vals_list=[ #Elsebugwithquick_createwhenwearefilteronanotheruser
            dict(vals,user_id=self.env.user.id)ifnot'user_id'invalselsevals
            forvalsinvals_list
        ]

        defaults=self.default_get(['activity_ids','res_model_id','res_id','user_id','res_model','partner_ids'])
        meeting_activity_type=self.env['mail.activity.type'].search([('category','=','meeting')],limit=1)
        #getlistofmodelsidsandfilteroutNonevaluesdirectly
        model_ids=list(filter(None,{values.get('res_model_id',defaults.get('res_model_id'))forvaluesinvals_list}))
        model_name=defaults.get('res_model')
        valid_activity_model_ids=model_nameandself.env[model_name].sudo().browse(model_ids).filtered(lambdam:'activity_ids'inm).idsor[]
        ifmeeting_activity_typeandnotdefaults.get('activity_ids'):
            forvaluesinvals_list:
                #createdfromcalendar:trytocreateanactivityontherelatedrecord
                ifvalues.get('activity_ids'):
                    continue
                res_model_id=values.get('res_model_id',defaults.get('res_model_id'))
                values['res_id']=res_id=values.get('res_id')ordefaults.get('res_id')
                user_id=values.get('user_id',defaults.get('user_id'))
                ifnotres_model_idornotres_id:
                    continue
                ifres_model_idnotinvalid_activity_model_ids:
                    continue
                activity_vals={
                    'res_model_id':res_model_id,
                    'res_id':res_id,
                    'activity_type_id':meeting_activity_type.id,
                }
                ifuser_id:
                    activity_vals['user_id']=user_id
                values['activity_ids']=[(0,0,activity_vals)]

        #Addcommandstocreateattendeesfrompartners(ifpresent)ifnoattendeecommand
        #isalreadygiven(comingfromGoogleeventforexample).
        #Automaticallyaddthecurrentpartnerwhencreatinganeventifthereisnone(happenswhenwequickcreateanevent)
        vals_list=[
            dict(vals,attendee_ids=self._attendees_values(vals['partner_ids']))
            if'partner_ids'invalsandnotvals.get('attendee_ids')
            elsevals
            forvalsinvals_list
        ]
        recurrence_fields=self._get_recurrent_fields()
        recurring_vals=[valsforvalsinvals_listifvals.get('recurrency')]
        other_vals=[valsforvalsinvals_listifnotvals.get('recurrency')]
        events=super().create(other_vals)

        forvalsinrecurring_vals:
            vals['follow_recurrence']=True
        recurring_events=super().create(recurring_vals)
        events+=recurring_events

        forevent,valsinzip(recurring_events,recurring_vals):
            recurrence_values={field:vals.pop(field)forfieldinrecurrence_fieldsiffieldinvals}
            ifvals.get('recurrency'):
                detached_events=event._apply_recurrence_values(recurrence_values)
                detached_events.active=False

        events.filtered(lambdaevent:event.start>fields.Datetime.now()).attendee_ids._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')
        events._sync_activities(fields={fforvalsinvals_listforfinvals.keys()})
        ifnotself.env.context.get('dont_notify'):
            foreventinevents:
                iflen(event.alarm_ids)>0:
                    self.env['calendar.alarm_manager']._notify_next_alarm(event.partner_ids.ids)

        returnevents.with_context(is_calendar_event_new=False)

    def_compute_field_value(self,field):
        iffield.compute_sudo:
            returnsuper(Meeting,self.with_context(prefetch_fields=False))._compute_field_value(field)
        returnsuper()._compute_field_value(field)

    def_read(self,fields):
        ifself.env.is_system():
            super()._read(fields)
            return

        fields=set(fields)
        private_fields=fields-self._get_public_fields()
        ifnotprivate_fields:
            super()._read(fields)
            return

        super()._read(fields|{'privacy','user_id','partner_ids'})
        current_partner_id=self.env.user.partner_id
        others_private_events=self.filtered(
            lambdae:e.privacy=='private'\
                  ande.user_id!=self.env.user\
                  andcurrent_partner_idnotine.partner_ids
        )
        ifnotothers_private_events:
            return

        forfield_nameinprivate_fields:
            field=self._fields[field_name]
            replacement=field.convert_to_cache(
                _('Busy')iffield_name=='name'elseFalse,
                others_private_events)
            self.env.cache.update(others_private_events,field,repeat(replacement))

    defname_get(self):
        """Hideprivateevents'nameforeventswhichdon'tbelongtothecurrentuser
        """
        hidden=self.filtered(
            lambdaevt:
                evt.privacy=='private'and
                evt.user_id.id!=self.env.uidand
                self.env.user.partner_idnotinevt.partner_ids
        )

        shown=self-hidden
        shown_names=super(Meeting,shown).name_get()
        obfuscated_names=[(eid,_('Busy'))foreidinhidden.ids]
        returnshown_names+obfuscated_names
    
    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        groupby=[groupby]ifisinstance(groupby,str)elsegroupby
        grouped_fields=set(group_field.split(':')[0]forgroup_fieldingroupby)
        private_fields=grouped_fields-self._get_public_fields()
        ifnotself.env.suandprivate_fields:
            raiseAccessError(_(
                "Groupingby%sisnotallowed.",
                ','.join([self._fields[field_name].stringforfield_nameinprivate_fields])
            ))
        returnsuper(Meeting,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

    defunlink(self):
        #Getconcernedattendeestonotifythemifthereisanalarmontheunlinkedevents,
        #asitmighthavechangedtheirnexteventnotification
        events=self.filtered_domain([('alarm_ids','!=',False)])
        partner_ids=events.mapped('partner_ids').ids

        #don'tforgettoupdaterecurrencesiftherearesomebaseeventsinthesettounlink,
        #butafterhavingremovedtheevents;-)
        recurrences=self.env["calendar.recurrence"].search([
            ('base_event_id.id','in',[e.idforeinself])
        ])

        result=super().unlink()

        ifrecurrences:
            recurrences._select_new_base_event()

        #Notifytheconcernedattendees(mustbedoneafterremovingtheevents)
        self.env['calendar.alarm_manager']._notify_next_alarm(partner_ids)
        returnresult

    def_range(self):
        self.ensure_one()
        return(self.start,self.stop)

    def_sync_activities(self,fields):
        #updateactivities
        foreventinself:
            ifevent.activity_ids:
                activity_values={}
                if'name'infields:
                    activity_values['summary']=event.name
                if'description'infields:
                    activity_values['note']=event.descriptionandtools.plaintext2html(event.description)
                if'start'infields:
                    #self.startisadatetimeUTC*onlywhentheeventisnotallday*
                    #activty.date_deadlineisadate(NoTZ,butshouldrepresentthedayinwhichtheuser'sTZis)
                    #See72254129dbaeae58d0a2055cba4e4a82cde495b7forthesameissue,butelsewhere
                    deadline=event.start
                    user_tz=self.env.context.get('tz')
                    ifuser_tzandnotevent.allday:
                        deadline=pytz.UTC.localize(deadline)
                        deadline=deadline.astimezone(pytz.timezone(user_tz))
                    activity_values['date_deadline']=deadline.date()
                if'user_id'infields:
                    activity_values['user_id']=event.user_id.id
                ifactivity_values.keys():
                    event.activity_ids.write(activity_values)

    defchange_attendee_status(self,status):
        attendee=self.attendee_ids.filtered(lambdax:x.partner_id==self.env.user.partner_id)
        ifstatus=='accepted':
            returnattendee.do_accept()
        ifstatus=='declined':
            returnattendee.do_decline()
        returnattendee.do_tentative()
