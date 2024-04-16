#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,time
importpytz

fromdateutilimportrrule
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError

fromflectra.addons.base.models.res_partnerimport_tz_get


MAX_RECURRENT_EVENT=720

SELECT_FREQ_TO_RRULE={
    'daily':rrule.DAILY,
    'weekly':rrule.WEEKLY,
    'monthly':rrule.MONTHLY,
    'yearly':rrule.YEARLY,
}

RRULE_FREQ_TO_SELECT={
    rrule.DAILY:'daily',
    rrule.WEEKLY:'weekly',
    rrule.MONTHLY:'monthly',
    rrule.YEARLY:'yearly',
}

RRULE_WEEKDAY_TO_FIELD={
    rrule.MO.weekday:'mo',
    rrule.TU.weekday:'tu',
    rrule.WE.weekday:'we',
    rrule.TH.weekday:'th',
    rrule.FR.weekday:'fr',
    rrule.SA.weekday:'sa',
    rrule.SU.weekday:'su',
}

RRULE_TYPE_SELECTION=[
    ('daily','Days'),
    ('weekly','Weeks'),
    ('monthly','Months'),
    ('yearly','Years'),
]

END_TYPE_SELECTION=[
    ('count','Numberofrepetitions'),
    ('end_date','Enddate'),
    ('forever','Forever'),
]

MONTH_BY_SELECTION=[
    ('date','Dateofmonth'),
    ('day','Dayofmonth'),
]

WEEKDAY_SELECTION=[
    ('MO','Monday'),
    ('TU','Tuesday'),
    ('WE','Wednesday'),
    ('TH','Thursday'),
    ('FR','Friday'),
    ('SA','Saturday'),
    ('SU','Sunday'),
]

BYDAY_SELECTION=[
    ('1','First'),
    ('2','Second'),
    ('3','Third'),
    ('4','Fourth'),
    ('-1','Last'),
]

deffreq_to_select(rrule_freq):
    returnRRULE_FREQ_TO_SELECT[rrule_freq]


deffreq_to_rrule(freq):
    returnSELECT_FREQ_TO_RRULE[freq]


defweekday_to_field(weekday_index):
    returnRRULE_WEEKDAY_TO_FIELD.get(weekday_index)


classRecurrenceRule(models.Model):
    _name='calendar.recurrence'
    _description='EventRecurrenceRule'

    name=fields.Char(compute='_compute_name',store=True)
    base_event_id=fields.Many2one(
        'calendar.event',ondelete='setnull',copy=False) #store=False?
    calendar_event_ids=fields.One2many('calendar.event','recurrence_id')
    event_tz=fields.Selection(
        _tz_get,string='Timezone',
        default=lambdaself:self.env.context.get('tz')orself.env.user.tz)
    rrule=fields.Char(compute='_compute_rrule',inverse='_inverse_rrule',store=True)
    dtstart=fields.Datetime(compute='_compute_dtstart')
    rrule_type=fields.Selection(RRULE_TYPE_SELECTION,default='weekly')
    end_type=fields.Selection(END_TYPE_SELECTION,default='count')
    interval=fields.Integer(default=1)
    count=fields.Integer(default=1)
    mo=fields.Boolean()
    tu=fields.Boolean()
    we=fields.Boolean()
    th=fields.Boolean()
    fr=fields.Boolean()
    sa=fields.Boolean()
    su=fields.Boolean()
    month_by=fields.Selection(MONTH_BY_SELECTION,default='date')
    day=fields.Integer(default=1)
    weekday=fields.Selection(WEEKDAY_SELECTION,string='Weekday')
    byday=fields.Selection(BYDAY_SELECTION,string='Byday')
    until=fields.Date('RepeatUntil')

    _sql_constraints=[
        ('month_day',
         "CHECK(rrule_type!='monthly'"
                "ORmonth_by!='day'"
                "ORday>=1ANDday<=31"
                "ORweekdayin%sANDbydayin%s)"
                %(tuple(wd[0]forwdinWEEKDAY_SELECTION),tuple(bd[0]forbdinBYDAY_SELECTION)),
         "Thedaymustbebetween1and31"),
    ]

    @api.depends('rrule')
    def_compute_name(self):
        forrecurrenceinself:
            period=dict(RRULE_TYPE_SELECTION)[recurrence.rrule_type]
            every=_("Every%(count)s%(period)s",count=recurrence.interval,period=period)

            ifrecurrence.end_type=='count':
                end=_("for%sevents",recurrence.count)
            elifrecurrence.end_type=='end_date':
                end=_("until%s",recurrence.until)
            else:
                end=''

            ifrecurrence.rrule_type=='weekly':
                weekdays=recurrence._get_week_days()
                #ConvertWeekdayobject
                weekdays=[str(w)forwinweekdays]
                day_strings=[d[1]fordinWEEKDAY_SELECTIONifd[0]inweekdays]
                on=_("on%s")%",".join([day_nameforday_nameinday_strings])
            elifrecurrence.rrule_type=='monthly':
                ifrecurrence.month_by=='day':
                    position_label=dict(BYDAY_SELECTION)[recurrence.byday]
                    weekday_label=dict(WEEKDAY_SELECTION)[recurrence.weekday]
                    on=_("onthe%(position)s%(weekday)s",position=position_label,weekday=weekday_label)
                else:
                    on=_("day%s",recurrence.day)
            else:
                on=''
            recurrence.name=','.join(filter(lambdas:s,[every,on,end]))

    @api.depends('calendar_event_ids.start')
    def_compute_dtstart(self):
        groups=self.env['calendar.event'].read_group([('recurrence_id','in',self.ids)],['start:min'],['recurrence_id'])
        start_mapping={
            group['recurrence_id'][0]:group['start']
            forgroupingroups
        }
        forrecurrenceinself:
            recurrence.dtstart=start_mapping.get(recurrence.id)

    @api.depends(
        'byday','until','rrule_type','month_by','interval','count','end_type',
        'mo','tu','we','th','fr','sa','su','day','weekday')
    def_compute_rrule(self):
        forrecurrenceinself:
            recurrence.rrule=recurrence._rrule_serialize()

    def_inverse_rrule(self):
        forrecurrenceinself:
            ifrecurrence.rrule:
                values=self._rrule_parse(recurrence.rrule,recurrence.dtstart)
                recurrence.write(values)

    def_reconcile_events(self,ranges):
        """
        :paramranges:iterableoftuples(datetime_start,datetime_stop)
        :return:tuple(eventsoftherecurrencealreadyinsyncwithranges,
                 andrangesnotcoveredbyanyevents)
        """
        ranges=set(ranges)

        synced_events=self.calendar_event_ids.filtered(lambdae:e._range()inranges)

        existing_ranges=set(event._range()foreventinsynced_events)
        ranges_to_create=(event_rangeforevent_rangeinrangesifevent_rangenotinexisting_ranges)
        returnsynced_events,ranges_to_create

    def_select_new_base_event(self):
        """
        whenthebaseeventisnomoreavailable(archived,deleted,etc.),anewoneshouldbeselected
        """
        forrecurrenceinself:
            recurrence.base_event_id=recurrence._get_first_event()

    def_apply_recurrence(self,specific_values_creation=None,no_send_edit=False):
        """Createmissingeventsintherecurrenceanddetacheventswhichnolonger
        followtherecurrencerules.
        :return:detachedevents
        """
        event_vals=[]
        keep=self.env['calendar.event']
        ifspecific_values_creationisNone:
            specific_values_creation={}

        forrecurrenceinself.filtered('base_event_id'):
            self.calendar_event_ids|=recurrence.base_event_id
            event=recurrence.base_event_idorrecurrence._get_first_event(include_outliers=False)
            duration=event.stop-event.start
            ifspecific_values_creation:
                ranges=set([(x[1],x[2])forxinspecific_values_creationifx[0]==recurrence.id])
            else:
                ranges=recurrence._range_calculation(event,duration)

            events_to_keep,ranges=recurrence._reconcile_events(ranges)
            keep|=events_to_keep
            [base_values]=event.copy_data()
            values=[]
            forstart,stopinranges:
                value=dict(base_values,start=start,stop=stop,recurrence_id=recurrence.id,follow_recurrence=True)
                if(recurrence.id,start,stop)inspecific_values_creation:
                    value.update(specific_values_creation[(recurrence.id,start,stop)])
                values+=[value]
            event_vals+=values

        events=self.calendar_event_ids-keep
        detached_events=self._detach_events(events)
        self.env['calendar.event'].with_context(no_mail_to_attendees=True,mail_create_nolog=True).create(event_vals)
        returndetached_events

    def_split_from(self,event,recurrence_values=None):
        """Stopsthecurrentrecurrenceatthegiveneventandcreatesanewonestarting
        withtheevent.
        :paramevent:startingpointofthenewrecurrence
        :paramrecurrence_values:valuesappliedtothenewrecurrence
        :return:newrecurrence
        """
        ifrecurrence_valuesisNone:
            recurrence_values={}
        event.ensure_one()
        ifnotself:
            return
        [values]=self.copy_data()
        detached_events=self._stop_at(event)

        count=recurrence_values.get('count',0)orlen(detached_events)
        returnself.create({
            **values,
            **recurrence_values,
            'base_event_id':event.id,
            'calendar_event_ids':[(6,0,detached_events.ids)],
            'count':max(count,1),
        })

    def_stop_at(self,event):
        """Stopstherecurrenceatthegivenevent.Detachtheeventandallfollowing
        eventsfromtherecurrence.

        :return:detachedeventsfromtherecurrence
        """
        self.ensure_one()
        events=self._get_events_from(event.start)
        detached_events=self._detach_events(events)
        ifnotself.calendar_event_ids:
            self.with_context(archive_on_error=True).unlink()
            returndetached_events

        ifevent.allday:
            until=self._get_start_of_period(event.start_date)
        else:
            until_datetime=self._get_start_of_period(event.start)
            until_timezoned=pytz.utc.localize(until_datetime).astimezone(self._get_timezone())
            until=until_timezoned.date()
        self.write({
            'end_type':'end_date',
            'until':until-relativedelta(days=1),
        })
        returndetached_events

    @api.model
    def_detach_events(self,events):
        events.write({
            'recurrence_id':False,
            'recurrency':False,
        })
        returnevents

    def_write_events(self,values,dtstart=None):
        """
        Writevaluesoneventsintherecurrence.
        :paramvalues:eventvalues
        :paramdstart:ifprovided,onlywriteeventsstartingfromthispointintime
        """
        events=self._get_events_from(dtstart)ifdtstartelseself.calendar_event_ids
        returnevents.with_context(no_mail_to_attendees=True,dont_notify=True).write(dict(values,recurrence_update='self_only'))

    def_rrule_serialize(self):
        """
        ComputerulestringaccordingtovaluetypeRECURofiCalendar
        :return:stringcontainingrecurringrule(emptyifnorule)
        """
        ifself.interval<=0:
            raiseUserError(_('Theintervalcannotbenegative.'))
        ifself.end_type=='count'andself.count<=0:
            raiseUserError(_('Thenumberofrepetitionscannotbenegative.'))

        returnstr(self._get_rrule())ifself.rrule_typeelse''

    @api.model
    def_rrule_parse(self,rule_str,date_start):
        #LULTODOcleanthismess
        data={}
        day_list=['mo','tu','we','th','fr','sa','su']

        if'Z'inrule_stranddate_startandnotdate_start.tzinfo:
            date_start=pytz.utc.localize(date_start)
        rule=rrule.rrulestr(rule_str,dtstart=date_start)

        data['rrule_type']=freq_to_select(rule._freq)
        data['count']=rule._count
        data['interval']=rule._interval
        data['until']=rule._until
        #Repeatweekly
        ifrule._byweekday:
            forweekdayinday_list:
                data[weekday]=False #reset
            forweekday_indexinrule._byweekday:
                weekday=rrule.weekday(weekday_index)
                data[weekday_to_field(weekday.weekday)]=True
                data['rrule_type']='weekly'

        #Repeatmonthlybynweekday((weekday,weeknumber),)
        ifrule._bynweekday:
            data['weekday']=day_list[list(rule._bynweekday)[0][0]].upper()
            data['byday']=str(list(rule._bynweekday)[0][1])
            data['month_by']='day'
            data['rrule_type']='monthly'

        ifrule._bymonthday:
            data['day']=list(rule._bymonthday)[0]
            data['month_by']='date'
            data['rrule_type']='monthly'

        #Repeatyearlybutforflectrait'smonthly,takesameinformationasmonthlybutintervalis12times
        ifrule._bymonth:
            data['interval']*=12

        ifdata.get('until'):
            data['end_type']='end_date'
        elifdata.get('count'):
            data['end_type']='count'
        else:
            data['end_type']='forever'
        returndata

    def_get_lang_week_start(self):
        lang=self.env['res.lang']._lang_get(self.env.user.lang)
        week_start=int(lang.week_start) #lang.week_startrangesfrom'1'to'7'
        returnrrule.weekday(week_start-1)#rruleexpectsanintfrom0to6

    def_get_start_of_period(self,dt):
        ifself.rrule_type=='weekly':
            week_start=self._get_lang_week_start()
            start=dt+relativedelta(weekday=week_start(-1))
        elifself.rrule_type=='monthly':
            start=dt+relativedelta(day=1)
        else:
            start=dt
        returnstart

    def_get_first_event(self,include_outliers=False):
        ifnotself.calendar_event_ids:
            returnself.env['calendar.event']
        events=self.calendar_event_ids.sorted('start')
        ifnotinclude_outliers:
            events-=self._get_outliers()
        returnevents[:1]

    def_get_outliers(self):
        synced_events=self.env['calendar.event']
        forrecurrenceinself:
            ifrecurrence.calendar_event_ids:
                start=min(recurrence.calendar_event_ids.mapped('start'))
                starts=set(recurrence._get_occurrences(start))
                synced_events|=recurrence.calendar_event_ids.filtered(lambdae:e.startinstarts)
        returnself.calendar_event_ids-synced_events

    def_range_calculation(self,event,duration):
        """Calculatetherangeofrecurrencewhenapplyingtherecurrence
        Thefollowingissuesaretakenintoaccount:
            startofperiodissometimesinthepast(weeklyormonthlyrule).
            Wecaneasilyfiltertheserangevaluesbutthenthecountvaluemaybewrong...
            Inthatcase,wejustincreasethecountvalue,recomputetherangesanddismisstheuselessvalues
        """
        self.ensure_one()
        original_count=self.end_type=='count'andself.count
        ranges=set(self._get_ranges(event.start,duration))
        future_events=set((x,y)forx,yinrangesifx.date()>=event.start.date()andy.date()>=event.start.date())
        iforiginal_countandlen(future_events)<original_count:
            #Risecountnumberbecausesomepastvalueswillbedismissed.
            self.count=(2*original_count)-len(future_events)
            ranges=set(self._get_ranges(event.start,duration))
            #Wesetbacktheoccurrencenumbertoitsoriginalvalue
            self.count=original_count
        #Removerangesofeventsoccurringinthepast
        ranges=set((x,y)forx,yinrangesifx.date()>=event.start.date()andy.date()>=event.start.date())
        returnranges


    def_get_ranges(self,start,event_duration):
        starts=self._get_occurrences(start)
        return((start,start+event_duration)forstartinstarts)

    def_get_timezone(self):
        returnpytz.timezone(self.event_tzorself.env.context.get('tz')or'UTC')

    def_get_occurrences(self,dtstart):
        """
        Getocurrencesoftherrule
        :paramdtstart:startoftherecurrence
        :return:iterableofdatetimes
        """
        self.ensure_one()
        dtstart=self._get_start_of_period(dtstart)
        ifself._is_allday():
            returnself._get_rrule(dtstart=dtstart)

        timezone=self._get_timezone()
        #Localizethestartingdatetimetoavoidmissingthefirstoccurrence
        dtstart=pytz.utc.localize(dtstart).astimezone(timezone)
        #dtstartisgivenasanaivedatetime,butitactuallyrepresentsatimezoneddatetime
        #(rrulepackageexpectsanaivedatetime)
        occurences=self._get_rrule(dtstart=dtstart.replace(tzinfo=None))

        #SpecialtimezoningisneededtohandleDST(DaylightSavingTime)changes.
        #Giventhefollowingrecurrence:
        #  -monthly
        #  -1stofeachmonth
        #  -timezoneUS/Eastern(UTC−05:00)
        #  -at6amUS/Eastern=11amUTC
        #  -from2019/02/01to2019/05/01.
        #Thenaivewaywouldbetostore:
        #2019/02/0111:00-2019/03/0111:00-2019/04/0111:00-2019/05/0111:00(UTC)
        #
        #ButaDSTchangeoccurson2019/03/10inUS/Easterntimezone.US/EasternisnowUTC−04:00.
        #Fromthispointintime,11am(UTC)isactuallyconvertedto7am(US/Eastern)insteadoftheexpected6am!
        #Whatshouldbestoredis:
        #2019/02/0111:00-2019/03/0111:00-2019/04/0110:00-2019/05/0110:00(UTC)
        #                                                 *****             *****
        return(timezone.localize(occurrence,is_dst=False).astimezone(pytz.utc).replace(tzinfo=None)foroccurrenceinoccurences)

    def_get_events_from(self,dtstart):
        returnself.env['calendar.event'].search([
            ('id','in',self.calendar_event_ids.ids),
            ('start','>=',dtstart)
        ])

    def_get_week_days(self):
        """
        :return:tupleofrruleweekdaysforthisrecurrence.
        """
        returntuple(
            rrule.weekday(weekday_index)
            forweekday_index,weekdayin{
                rrule.MO.weekday:self.mo,
                rrule.TU.weekday:self.tu,
                rrule.WE.weekday:self.we,
                rrule.TH.weekday:self.th,
                rrule.FR.weekday:self.fr,
                rrule.SA.weekday:self.sa,
                rrule.SU.weekday:self.su,
            }.items()ifweekday
        )

    def_is_allday(self):
        """Returnswhetheramajorityofeventsarealldayornot(theremightbesomeoutlierevents)
        """
        score=sum(1ife.alldayelse-1foreinself.calendar_event_ids)
        returnscore>=0

    def_get_rrule(self,dtstart=None):
        self.ensure_one()
        freq=self.rrule_type
        rrule_params=dict(
            dtstart=dtstart,
            interval=self.interval,
        )
        iffreq=='monthly'andself.month_by=='date': #e.g.every15thofthemonth
            rrule_params['bymonthday']=self.day
        eliffreq=='monthly'andself.month_by=='day': #e.g.every2ndMondayinthemonth
            rrule_params['byweekday']=getattr(rrule,self.weekday)(int(self.byday)) #e.g.MO(+2)forthesecondMondayofthemonth
        eliffreq=='weekly':
            weekdays=self._get_week_days()
            ifnotweekdays:
                raiseUserError(_("Youhavetochooseatleastonedayintheweek"))
            rrule_params['byweekday']=weekdays
            rrule_params['wkst']=self._get_lang_week_start()

        ifself.end_type=='count': #e.g.stopafterXoccurence
            rrule_params['count']=min(self.count,MAX_RECURRENT_EVENT)
        elifself.end_type=='forever':
            rrule_params['count']=MAX_RECURRENT_EVENT
        elifself.end_type=='end_date': #e.g.stopafter12/10/2020
            rrule_params['until']=datetime.combine(self.until,time.max)
        returnrrule.rrule(
            freq_to_rrule(freq),**rrule_params
        )
