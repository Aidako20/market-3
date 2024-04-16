#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError
importpytz
fromdatetimeimportdatetime,date
fromdateutil.relativedeltaimportrelativedelta

fromflectra.tests.commonimportSavepointCase


classTestRecurrentEvents(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestRecurrentEvents,cls).setUpClass()
        lang=cls.env['res.lang']._lang_get(cls.env.user.lang)
        lang.week_start='1' #Monday

    defassertEventDates(self,events,dates):
        events=events.sorted('start')
        self.assertEqual(len(events),len(dates),"Wrongnumberofeventsintherecurrence")
        self.assertTrue(all(events.mapped('active')),"Alleventsshouldbeactive")
        forevent,datesinzip(events,dates):
            start,stop=dates
            self.assertEqual(event.start,start)
            self.assertEqual(event.stop,stop)


classTestCreateRecurrentEvents(TestRecurrentEvents):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.event=cls.env['calendar.event'].create({
            'name':'RecurrentEvent',
            'start':datetime(2019,10,21,8,0),
            'stop':datetime(2019,10,23,18,0),
            'recurrency':True,
        })

    deftest_weekly_count(self):
        """Everyweek,onTuesdays,for3occurences"""
        detached_events=self.event._apply_recurrence_values({
            'rrule_type':'weekly',
            'tu':True,
            'interval':1,
            'count':3,
            'event_tz':'UTC',
        })
        self.assertEqual(detached_events,self.event,"Itshouldbedetachedfromtherecurrence")
        self.assertFalse(self.event.recurrence_id,"Itshouldbedetachedfromtherecurrence")
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEqual(len(events),3,"Itshouldhave3eventsintherecurrence")
        self.assertEventDates(events,[
            (datetime(2019,10,22,8,0),datetime(2019,10,24,18,0)),
            (datetime(2019,10,29,8,0),datetime(2019,10,31,18,0)),
            (datetime(2019,11,5,8,0),datetime(2019,11,7,18,0)),
        ])

    deftest_weekly_interval_2(self):
        self.event._apply_recurrence_values({
            'interval':2,
            'rrule_type':'weekly',
            'tu':True,
            'count':2,
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEventDates(events,[
            (datetime(2019,10,22,8,0),datetime(2019,10,24,18,0)),
            (datetime(2019,11,5,8,0),datetime(2019,11,7,18,0)),
        ])

    deftest_weekly_interval_2_week_start_sunday(self):
        lang=self.env['res.lang']._lang_get(self.env.user.lang)
        lang.week_start='7' #Sunday

        self.event._apply_recurrence_values({
            'interval':2,
            'rrule_type':'weekly',
            'tu':True,
            'count':2,
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEventDates(events,[
            (datetime(2019,10,22,8,0),datetime(2019,10,24,18,0)),
            (datetime(2019,11,5,8,0),datetime(2019,11,7,18,0)),
        ])
        lang.week_start='1' #Monday

    deftest_weekly_until(self):
        self.event._apply_recurrence_values({
            'rrule_type':'weekly',
            'tu':True,
            'interval':2,
            'end_type':'end_date',
            'until':datetime(2019,11,15),
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEqual(len(events),2,"Itshouldhave2eventsintherecurrence")
        self.assertEventDates(events,[
            (datetime(2019,10,22,8,0),datetime(2019,10,24,18,0)),
            (datetime(2019,11,5,8,0),datetime(2019,11,7,18,0)),
        ])

    deftest_monthly_count_by_date(self):
        self.event._apply_recurrence_values({
            'rrule_type':'monthly',
            'interval':2,
            'month_by':'date',
            'day':27,
            'end_type':'count',
            'count':3,
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEqual(len(events),3,"Itshouldhave3eventsintherecurrence")
        self.assertEventDates(events,[
            (datetime(2019,10,27,8,0),datetime(2019,10,29,18,0)),
            (datetime(2019,12,27,8,0),datetime(2019,12,29,18,0)),
            (datetime(2020,2,27,8,0),datetime(2020,2,29,18,0)),
        ])

    deftest_monthly_count_by_date_31(self):
        self.event._apply_recurrence_values({
            'rrule_type':'monthly',
            'interval':1,
            'month_by':'date',
            'day':31,
            'end_type':'count',
            'count':3,
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEqual(len(events),3,"Itshouldhave3eventsintherecurrence")
        self.assertEventDates(events,[
            (datetime(2019,10,31,8,0),datetime(2019,11,2,18,0)),
            #Missing31thinNovember
            (datetime(2019,12,31,8,0),datetime(2020,1,2,18,0)),
            (datetime(2020,1,31,8,0),datetime(2020,2,2,18,0)),
        ])

    deftest_monthly_until_by_day(self):
        """Every2months,onthethirdTuesday,until27thMarch2020"""
        self.event.start=datetime(2019,10,1,8,0)
        self.event.stop=datetime(2019,10,3,18,0)
        self.event._apply_recurrence_values({
            'rrule_type':'monthly',
            'interval':2,
            'month_by':'day',
            'byday':'3',
            'weekday':'TU',
            'end_type':'end_date',
            'until':date(2020,3,27),
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEqual(len(events),3,"Itshouldhave3eventsintherecurrence")
        self.assertEventDates(events,[
            (datetime(2019,10,15,8,0),datetime(2019,10,17,18,0)),
            (datetime(2019,12,17,8,0),datetime(2019,12,19,18,0)),
            (datetime(2020,2,18,8,0),datetime(2020,2,20,18,0)),
        ])

    deftest_monthly_until_by_day_last(self):
        """Every2months,onthelastWednesday,until15thJanuary2020"""
        self.event._apply_recurrence_values({
            'interval':2,
            'rrule_type':'monthly',
            'month_by':'day',
            'weekday':'WE',
            'byday':'-1',
            'end_type':'end_date',
            'until':date(2020,1,15),
            'event_tz':'UTC',
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        events=recurrence.calendar_event_ids
        self.assertEqual(len(events),2,"Itshouldhave3eventsintherecurrence")
        self.assertEventDates(events,[
            (datetime(2019,10,30,8,0),datetime(2019,11,1,18,0)),
            (datetime(2019,12,25,8,0),datetime(2019,12,27,18,0)),
        ])

    deftest_yearly_count(self):
        self.event._apply_recurrence_values({
            'interval':2,
            'rrule_type':'yearly',
            'count':2,
            'event_tz':'UTC',
        })
        events=self.event.recurrence_id.calendar_event_ids
        self.assertEqual(len(events),2,"Itshouldhave3eventsintherecurrence")
        self.assertEventDates(events,[
            (self.event.start,self.event.stop),
            (self.event.start+relativedelta(years=2),self.event.stop+relativedelta(years=2)),
        ])

    deftest_dst_timezone(self):
        """Testhoursstaysthesame,regardlessofDSTchanges"""
        self.event.start=datetime(2002,10,28,10,0)
        self.event.stop=datetime(2002,10,28,12,0)
        self.event._apply_recurrence_values({
            'interval':2,
            'rrule_type':'weekly',
            'mo':True,
            'count':'2',
            'event_tz':'US/Eastern', #DSTchangeon2002/10/27
        })
        recurrence=self.env['calendar.recurrence'].search([('base_event_id','=',self.event.id)])
        self.assertEventDates(recurrence.calendar_event_ids,[
            (datetime(2002,10,28,10,0),datetime(2002,10,28,12,0)),
            (datetime(2002,11,11,10,0),datetime(2002,11,11,12,0)),
        ])

    deftest_ambiguous_dst_time_winter(self):
        """Testhoursstaysthesame,regardlessofDSTchanges"""
        eastern=pytz.timezone('US/Eastern')
        dt=eastern.localize(datetime(2002,10,20,1,30,00)).astimezone(pytz.utc).replace(tzinfo=None)
        #Nextoccurencehappensat1:30amon27thOct2002whichhappenedtwiceintheUS/Eastern
        #timezonewhentheclockswhereputbackattheendofDaylightSavingTime
        self.event.start=dt
        self.event.stop=dt+relativedelta(hours=1)
        self.event._apply_recurrence_values({
            'interval':1,
            'rrule_type':'weekly',
            'su':True,
            'count':'2',
            'event_tz':'US/Eastern' #DSTchangeon2002/4/7
        })
        events=self.event.recurrence_id.calendar_event_ids
        self.assertEqual(events.mapped('duration'),[1,1])
        self.assertEventDates(events,[
            (datetime(2002,10,20,5,30),datetime(2002,10,20,6,30)),
            (datetime(2002,10,27,6,30),datetime(2002,10,27,7,30)),
        ])

    deftest_ambiguous_dst_time_spring(self):
        """Testhoursstaysthesame,regardlessofDSTchanges"""
        eastern=pytz.timezone('US/Eastern')
        dt=eastern.localize(datetime(2002,3,31,2,30,00)).astimezone(pytz.utc).replace(tzinfo=None)
        #Nextoccurencehappens2:30amon7thApril2002whichneverhappenedatallinthe
        #US/Easterntimezone,astheclockswhereputforwardat2:00amskippingtheentirehour
        self.event.start=dt
        self.event.stop=dt+relativedelta(hours=1)
        self.event._apply_recurrence_values({
            'interval':1,
            'rrule_type':'weekly',
            'su':True,
            'count':'2',
            'event_tz':'US/Eastern' #DSTchangeon2002/4/7
        })
        events=self.event.recurrence_id.calendar_event_ids
        self.assertEqual(events.mapped('duration'),[1,1])
        #Theeventbeginsat"thesametime"(i.e.2h30aftermidnight),butthatday,2h30aftermidnighthappenstobeat3:30am
        self.assertEventDates(events,[
            (datetime(2002,3,31,7,30),datetime(2002,3,31,8,30)),
            (datetime(2002,4,7,7,30),datetime(2002,4,7,8,30)),
        ])

    deftest_ambiguous_full_day(self):
        """Testdatestaysthesame,regardlessofDSTchanges"""
        self.event.write({
            'start':datetime(2020,3,23,0,0),
            'stop':datetime(2020,3,23,23,59),
        })
        self.event.allday=True
        self.event._apply_recurrence_values({
            'interval':1,
            'rrule_type':'weekly',
            'mo':True,
            'count':2,
            'event_tz':'Europe/Brussels' #DSTchangeon2020/3/23
        })
        events=self.event.recurrence_id.calendar_event_ids
        self.assertEventDates(events,[
            (datetime(2020,3,23,0,0),datetime(2020,3,23,23,59)),
            (datetime(2020,3,30,0,0),datetime(2020,3,30,23,59)),
        ])


classTestUpdateRecurrentEvents(TestRecurrentEvents):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        event=cls.env['calendar.event'].create({
            'name':'RecurrentEvent',
            'start':datetime(2019,10,22,1,0),
            'stop':datetime(2019,10,24,18,0),
            'recurrency':True,
            'rrule_type':'weekly',
            'tu':True,
            'interval':1,
            'count':3,
            'event_tz':'Etc/GMT-4',
        })
        cls.recurrence=event.recurrence_id
        cls.events=event.recurrence_id.calendar_event_ids.sorted('start')

    deftest_shift_future(self):
        event=self.events[1]
        self.events[1].write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(days=4),
            'stop':event.stop+relativedelta(days=5),
        })
        self.assertEqual(self.recurrence.end_type,'end_date')
        self.assertEqual(self.recurrence.until,date(2019,10,27))
        self.assertEventDates(self.recurrence.calendar_event_ids,[
            (datetime(2019,10,22,1,0),datetime(2019,10,24,18,0)),
        ])
        new_recurrence=event.recurrence_id
        self.assertNotEqual(self.recurrence,new_recurrence)
        self.assertEqual(new_recurrence.count,2)
        self.assertEqual(new_recurrence.dtstart,datetime(2019,11,2,1,0))
        self.assertFalse(new_recurrence.tu)
        self.assertTrue(new_recurrence.sa)
        self.assertEventDates(new_recurrence.calendar_event_ids,[
            (datetime(2019,11,2,1,0),datetime(2019,11,5,18,0)),
            (datetime(2019,11,9,1,0),datetime(2019,11,12,18,0)),
        ])

    deftest_shift_future_first(self):
        event=self.events[0]
        self.events[0].write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(days=4),
            'stop':event.stop+relativedelta(days=5),
        })
        new_recurrence=event.recurrence_id
        self.assertFalse(self.recurrence.exists())
        self.assertEqual(new_recurrence.count,3)
        self.assertEqual(new_recurrence.dtstart,datetime(2019,10,26,1,0))
        self.assertFalse(new_recurrence.tu)
        self.assertTrue(new_recurrence.sa)
        self.assertEventDates(new_recurrence.calendar_event_ids,[
            (datetime(2019,10,26,1,0),datetime(2019,10,29,18,0)),
            (datetime(2019,11,2,1,0),datetime(2019,11,5,18,0)),
            (datetime(2019,11,9,1,0),datetime(2019,11,12,18,0)),
        ])

    deftest_shift_reapply(self):
        event=self.events[2]
        self.events[2].write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(days=4),
            'stop':event.stop+relativedelta(days=5),
        })
        #re-Applyingthefirstrecurrenceshouldbeidempotent
        self.recurrence._apply_recurrence()
        self.assertEventDates(self.recurrence.calendar_event_ids,[
            (datetime(2019,10,22,1,0),datetime(2019,10,24,18,0)),
            (datetime(2019,10,29,1,0),datetime(2019,10,31,18,0)),
        ])

    deftest_shift_all(self):
        event=self.events[1]
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start+relativedelta(days=4),
                'stop':event.stop+relativedelta(days=5),
            })

    deftest_change_week_day_rrule(self):
        recurrence=self.events.recurrence_id
        recurrence.rrule='FREQ=WEEKLY;COUNT=3;BYDAY=WE'#fromTUtoWE
        self.assertFalse(self.recurrence.tu)
        self.assertTrue(self.recurrence.we)

    deftest_shift_all_base_inactive(self):
        self.recurrence.base_event_id.active=False
        event=self.events[1]
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start+relativedelta(days=4),
                'stop':event.stop+relativedelta(days=5),
            })

    deftest_shift_all_with_outlier(self):
        outlier=self.events[1]
        outlier.write({
            'recurrence_update':'self_only',
            'start':datetime(2019,9,26,1,0), #Thursday
            'stop':datetime(2019,9,26,18,0),
        })
        event=self.events[0]
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start+relativedelta(days=4),
                'stop':event.stop+relativedelta(days=5),
            })

    deftest_update_recurrence_future(self):
        event=self.events[1]
        event.write({
            'recurrence_update':'future_events',
            'fr':True, #recurrenceisnowTuesdayANDFriday
            'count':4,
        })
        self.assertEventDates(self.recurrence.calendar_event_ids,[
            (datetime(2019,10,22,1,0),datetime(2019,10,24,18,0)), #Tu
        ])

        self.assertEventDates(event.recurrence_id.calendar_event_ids,[
            (datetime(2019,10,29,1,0),datetime(2019,10,31,18,0)), #Tu
            (datetime(2019,11,1,1,0),datetime(2019,11,3,18,0)),   #Fr
            (datetime(2019,11,5,1,0),datetime(2019,11,7,18,0)),   #Tu
            (datetime(2019,11,8,1,0),datetime(2019,11,10,18,0)),  #Fr
        ])

        events=event.recurrence_id.calendar_event_ids.sorted('start')
        self.assertEqual(events[0],self.events[1],"EventsonTuesdaysshouldnothavechanged")
        self.assertEqual(events[2],self.events[2],"EventsonTuesdaysshouldnothavechanged")
        self.assertNotEqual(events.recurrence_id,self.recurrence,"Eventsshouldnolongerbelinkedtotheoriginalrecurrence")
        self.assertEqual(events.recurrence_id.count,4,"Thenewrecurrenceshouldhave4")
        self.assertTrue(event.recurrence_id.tu)
        self.assertTrue(event.recurrence_id.fr)

    deftest_update_recurrence_all(self):
        withself.assertRaises(UserError):
            self.events[1].write({
                'recurrence_update':'all_events',
                'mo':True, #recurrenceisnowTuesdayANDMonday
            })

    deftest_shift_single(self):
        event=self.events[1]
        event.write({
            'recurrence_update':'self_only',
            'name':"Updatedevent",
            'start':event.start-relativedelta(hours=2)
        })
        self.events[0].write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(hours=4),
            'stop':event.stop+relativedelta(hours=5),
        })

    deftest_break_recurrence_future(self):
        event=self.events[1]
        event.write({
            'recurrence_update':'future_events',
            'recurrency':False,
        })
        self.assertFalse(event.recurrence_id)
        self.assertTrue(self.events[0].active)
        self.assertTrue(self.events[1].active)
        self.assertFalse(self.events[2].exists())
        self.assertEqual(self.recurrence.until,date(2019,10,27))
        self.assertEqual(self.recurrence.end_type,'end_date')
        self.assertEventDates(self.recurrence.calendar_event_ids,[
            (datetime(2019,10,22,1,0),datetime(2019,10,24,18,0)),
        ])

    deftest_break_recurrence_all(self):
        event=self.events[1]
        event.write({
            'recurrence_update':'all_events',
            'recurrency':False,
            'count':0, #Inpractice,JSframeworksendsupdatedrecurrencyfields,sincetheyhavebeenrecomputed,triggeredbythe`recurrency`change
        })
        self.assertFalse(self.events[0].exists())
        self.assertTrue(event.active)
        self.assertFalse(self.events[2].exists())
        self.assertFalse(event.recurrence_id)
        self.assertFalse(self.recurrence.exists())

    deftest_all_day_shift(self):
        recurrence=self.env['calendar.event'].create({
            'name':'RecurrentEvent',
            'start_date':datetime(2019,10,22),
            'stop_date':datetime(2019,10,24),
            'recurrency':True,
            'rrule_type':'weekly',
            'tu':True,
            'interval':1,
            'count':3,
            'event_tz':'Etc/GMT-4',
            'allday':True,
        }).recurrence_id
        events=recurrence.calendar_event_ids.sorted('start')
        event=events[1]
        event.write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(days=4),
            'stop':event.stop+relativedelta(days=5),
        })
        self.assertEqual(recurrence.end_type,'end_date')
        self.assertEqual(recurrence.until,date(2019,10,27))
        self.assertEventDates(recurrence.calendar_event_ids,[
            (datetime(2019,10,22,8,0),datetime(2019,10,24,18,0)),
        ])
        new_recurrence=event.recurrence_id
        self.assertNotEqual(recurrence,new_recurrence)
        self.assertEqual(new_recurrence.count,2)
        self.assertEqual(new_recurrence.dtstart,datetime(2019,11,2,8,0))
        self.assertFalse(new_recurrence.tu)
        self.assertTrue(new_recurrence.sa)
        self.assertEventDates(new_recurrence.calendar_event_ids,[
            (datetime(2019,11,2,8,0),datetime(2019,11,5,18,0)),
            (datetime(2019,11,9,8,0),datetime(2019,11,12,18,0)),
        ])

    #TODOtestfollowers,andalarmsarecopied


classTestUpdateMultiDayWeeklyRecurrentEvents(TestRecurrentEvents):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        event=cls.env['calendar.event'].create({
            'name':'RecurrentEvent',
            'start':datetime(2019,10,22,1,0),
            'stop':datetime(2019,10,24,18,0),
            'recurrency':True,
            'rrule_type':'weekly',
            'tu':True,
            'fr':True,
            'interval':1,
            'count':3,
            'event_tz':'Etc/GMT-4',
        })
        cls.recurrence=event.recurrence_id
        cls.events=event.recurrence_id.calendar_event_ids.sorted('start')
        #Tuesdaydatetime(2019,10,22,1,0)
        #Fridaydatetime(2019,10,25,1,0)
        #Tuesdaydatetime(2019,10,29,1,0)

    deftest_shift_all_multiple_weekdays(self):
        event=self.events[0] #Tuesday
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start+relativedelta(days=2),
                'stop':event.stop+relativedelta(days=2),
            })

    deftest_shift_all_multiple_weekdays_duration(self):
        event=self.events[0] #Tuesday
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start+relativedelta(days=2),
                'stop':event.stop+relativedelta(days=3),
            })

    deftest_shift_future_multiple_weekdays(self):
        event=self.events[1] #Friday
        event.write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(days=3),
            'stop':event.stop+relativedelta(days=3),
        })
        self.assertTrue(self.recurrence.fr)
        self.assertTrue(self.recurrence.tu)
        self.assertTrue(event.recurrence_id.tu)
        self.assertTrue(event.recurrence_id.mo)
        self.assertFalse(event.recurrence_id.fr)
        self.assertEqual(event.recurrence_id.count,2)


classTestUpdateMonthlyByDay(TestRecurrentEvents):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        event=cls.env['calendar.event'].create({
            'name':'RecurrentEvent',
            'start':datetime(2019,10,15,1,0),
            'stop':datetime(2019,10,16,18,0),
            'recurrency':True,
            'rrule_type':'monthly',
            'interval':1,
            'count':3,
            'month_by':'day',
            'weekday':'TU',
            'byday':'3',
            'event_tz':'Etc/GMT-4',
        })
        cls.recurrence=event.recurrence_id
        cls.events=event.recurrence_id.calendar_event_ids.sorted('start')
        #datetime(2019,10,15,1,0)
        #datetime(2019,11,19,1,0)
        #datetime(2019,12,17,1,0)

    deftest_shift_all(self):
        event=self.events[1]
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start-relativedelta(days=5),
                'stop':event.stop-relativedelta(days=4),
            })


classTestUpdateMonthlyByDate(TestRecurrentEvents):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        event=cls.env['calendar.event'].create({
            'name':'RecurrentEvent',
            'start':datetime(2019,10,22,1,0),
            'stop':datetime(2019,10,24,18,0),
            'recurrency':True,
            'rrule_type':'monthly',
            'interval':1,
            'count':3,
            'month_by':'date',
            'day':22,
            'event_tz':'Etc/GMT-4',
        })
        cls.recurrence=event.recurrence_id
        cls.events=event.recurrence_id.calendar_event_ids.sorted('start')
        #datetime(2019,10,22,1,0)
        #datetime(2019,11,22,1,0)
        #datetime(2019,12,22,1,0)

    deftest_shift_future(self):
        event=self.events[1]
        event.write({
            'recurrence_update':'future_events',
            'start':event.start+relativedelta(days=4),
            'stop':event.stop+relativedelta(days=5),
        })
        self.assertEventDates(self.recurrence.calendar_event_ids,[
            (datetime(2019,10,22,1,0),datetime(2019,10,24,18,0)),
        ])
        self.assertEventDates(event.recurrence_id.calendar_event_ids,[
            (datetime(2019,11,26,1,0),datetime(2019,11,29,18,0)),
            (datetime(2019,12,26,1,0),datetime(2019,12,29,18,0)),
        ])

    deftest_shift_all(self):
        event=self.events[1]
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'start':event.start+relativedelta(days=4),
                'stop':event.stop+relativedelta(days=5),
            })

    deftest_update_all(self):
        event=self.events[1]
        withself.assertRaises(UserError):
            event.write({
                'recurrence_update':'all_events',
                'day':25,
            })
