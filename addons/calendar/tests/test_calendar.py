#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importdatetime

fromdatetimeimportdatetime,timedelta,time

fromflectraimportfields
fromflectra.testsimportForm
fromflectra.addons.base.tests.commonimportSavepointCaseWithUserDemo
importpytz
importre


classTestCalendar(SavepointCaseWithUserDemo):

    defsetUp(self):
        super(TestCalendar,self).setUp()

        self.CalendarEvent=self.env['calendar.event']
        #InOrdertotestcalendar,IwillfirstcreateOneSimpleEventwithrealdata
        self.event_tech_presentation=self.CalendarEvent.create({
            'privacy':'private',
            'start':'2011-04-3016:00:00',
            'stop':'2011-04-3018:30:00',
            'description':'TheTechnicalPresentationwillcoverfollowingtopics:\n*CreatingFlectraclass\n*Views\n*Wizards\n*Workflows',
            'duration':2.5,
            'location':'FlectraS.A.',
            'name':'TechnicalPresentation'
        })

    deftest_event_order(self):
        """checktheorderingofeventswhensearching"""
        defcreate_event(name,date):
            returnself.CalendarEvent.create({
                'name':name,
                'start':date+'12:00:00',
                'stop':date+'14:00:00',
            })
        foo1=create_event('foo','2011-04-01')
        foo2=create_event('foo','2011-06-01')
        bar1=create_event('bar','2011-05-01')
        bar2=create_event('bar','2011-06-01')
        domain=[('id','in',(foo1+foo2+bar1+bar2).ids)]

        #sortthembynameonly
        events=self.CalendarEvent.search(domain,order='name')
        self.assertEqual(events.mapped('name'),['bar','bar','foo','foo'])
        events=self.CalendarEvent.search(domain,order='namedesc')
        self.assertEqual(events.mapped('name'),['foo','foo','bar','bar'])

        #sortthembystartdateonly
        events=self.CalendarEvent.search(domain,order='start')
        self.assertEqual(events.mapped('start'),(foo1+bar1+foo2+bar2).mapped('start'))
        events=self.CalendarEvent.search(domain,order='startdesc')
        self.assertEqual(events.mapped('start'),(foo2+bar2+bar1+foo1).mapped('start'))

        #sortthembynamethenstartdate
        events=self.CalendarEvent.search(domain,order='nameasc,startasc')
        self.assertEqual(list(events),[bar1,bar2,foo1,foo2])
        events=self.CalendarEvent.search(domain,order='nameasc,startdesc')
        self.assertEqual(list(events),[bar2,bar1,foo2,foo1])
        events=self.CalendarEvent.search(domain,order='namedesc,startasc')
        self.assertEqual(list(events),[foo1,foo2,bar1,bar2])
        events=self.CalendarEvent.search(domain,order='namedesc,startdesc')
        self.assertEqual(list(events),[foo2,foo1,bar2,bar1])

        #sortthembystartdatethenname
        events=self.CalendarEvent.search(domain,order='startasc,nameasc')
        self.assertEqual(list(events),[foo1,bar1,bar2,foo2])
        events=self.CalendarEvent.search(domain,order='startasc,namedesc')
        self.assertEqual(list(events),[foo1,bar1,foo2,bar2])
        events=self.CalendarEvent.search(domain,order='startdesc,nameasc')
        self.assertEqual(list(events),[bar2,foo2,bar1,foo1])
        events=self.CalendarEvent.search(domain,order='startdesc,namedesc')
        self.assertEqual(list(events),[foo2,bar2,bar1,foo1])

    deftest_event_activity(self):
        #ensuremeetingactivitytypeexists
        meeting_act_type=self.env['mail.activity.type'].search([('category','=','meeting')],limit=1)
        ifnotmeeting_act_type:
            meeting_act_type=self.env['mail.activity.type'].create({
                'name':'MeetingTest',
                'category':'meeting',
            })

        #haveatestmodelinheritingfromactivities
        test_record=self.env['res.partner'].create({
            'name':'Test',
        })
        now=datetime.now()
        test_user=self.user_demo
        test_name,test_description,test_description2='Test-Meeting','Test-Description','NotTest'
        test_note,test_note2='<p>Test-Description</p>','<p>NotTest</p>'

        #createusingdefault_*keys
        test_event=self.env['calendar.event'].with_user(test_user).with_context(
            default_res_model=test_record._name,
            default_res_id=test_record.id,
        ).create({
            'name':test_name,
            'description':test_description,
            'start':fields.Datetime.to_string(now+timedelta(days=-1)),
            'stop':fields.Datetime.to_string(now+timedelta(hours=2)),
            'user_id':self.env.user.id,
        })
        self.assertEqual(test_event.res_model,test_record._name)
        self.assertEqual(test_event.res_id,test_record.id)
        self.assertEqual(len(test_record.activity_ids),1)
        self.assertEqual(test_record.activity_ids.summary,test_name)
        self.assertEqual(test_record.activity_ids.note,test_note)
        self.assertEqual(test_record.activity_ids.user_id,self.env.user)
        self.assertEqual(test_record.activity_ids.date_deadline,(now+timedelta(days=-1)).date())

        #updatingeventshouldupdateactivity
        test_event.write({
            'name':'%s2'%test_name,
            'description':test_description2,
            'start':fields.Datetime.to_string(now+timedelta(days=-2)),
            'user_id':test_user.id,
        })
        self.assertEqual(test_record.activity_ids.summary,'%s2'%test_name)
        self.assertEqual(test_record.activity_ids.note,test_note2)
        self.assertEqual(test_record.activity_ids.user_id,test_user)
        self.assertEqual(test_record.activity_ids.date_deadline,(now+timedelta(days=-2)).date())

        #updateeventwithadescriptionthathaveaspecialcharacterandanewline
        test_description3='Test&\nDescription'
        test_note3='<p>Test&amp;<br>Description</p>'
        test_event.write({
            'description':test_description3,
        })

        self.assertEqual(test_record.activity_ids.note,test_note3)

        #deletingmeetingshoulddeleteitsactivity
        test_record.activity_ids.unlink()
        self.assertEqual(self.env['calendar.event'],self.env['calendar.event'].search([('name','=',test_name)]))

        #createusingactive_modelkeys
        test_event=self.env['calendar.event'].with_user(self.user_demo).with_context(
            active_model=test_record._name,
            active_id=test_record.id,
        ).create({
            'name':test_name,
            'description':test_description,
            'start':now+timedelta(days=-1),
            'stop':now+timedelta(hours=2),
            'user_id':self.env.user.id,
        })
        self.assertEqual(test_event.res_model,test_record._name)
        self.assertEqual(test_event.res_id,test_record.id)
        self.assertEqual(len(test_record.activity_ids),1)

    deftest_event_allday(self):
        self.env.user.tz='Pacific/Honolulu'

        event=self.CalendarEvent.create({
            'name':'AllDay',
            'start':"2018-10-1600:00:00",
            'start_date':"2018-10-16",
            'stop':"2018-10-1800:00:00",
            'stop_date':"2018-10-18",
            'allday':True,
        })
        event.invalidate_cache()
        self.assertEqual(str(event.start),'2018-10-1608:00:00')
        self.assertEqual(str(event.stop),'2018-10-1818:00:00')

    deftest_recurring_around_dst(self):
        m=self.CalendarEvent.create({
            'name':"wheee",
            'start':'2018-10-2714:30:00',
            'allday':False,
            'rrule':u'FREQ=DAILY;INTERVAL=1;COUNT=4',
            'recurrency':True,
            'stop':'2018-10-2716:30:00',
            'event_tz':'Europe/Brussels',
        })

        start_recurring_dates=m.recurrence_id.calendar_event_ids.sorted('start').mapped('start')
        self.assertEqual(len(start_recurring_dates),4)

        fordinstart_recurring_dates:
            ifd.day<28: #DSTswitchhappensbetween2018-10-27and2018-10-28
                self.assertEqual(d.hour,14)
            else:
                self.assertEqual(d.hour,15)
            self.assertEqual(d.minute,30)

    deftest_recurring_ny(self):
        self.env.user.tz='US/Eastern'
        f=Form(self.CalendarEvent.with_context(tz='US/Eastern'))
        f.name='test'
        f.start='2022-07-0701:00:00' #ThisisinUTC.InNY,itcorrespondstothe6thofjulyat9pm.
        f.recurrency=True
        self.assertEqual(f.weekday,'WE')
        self.assertEqual(f.event_tz,'US/Eastern',"Thevalueshouldcorrespondtotheusertz")
        self.assertEqual(f.count,1,"Thedefaultvalueshouldbedisplayed")
        self.assertEqual(f.interval,1,"Thedefaultvalueshouldbedisplayed")
        self.assertEqual(f.month_by,"date","Thedefaultvalueshouldbedisplayed")
        self.assertEqual(f.end_type,"count","Thedefaultvalueshouldbedisplayed")
        self.assertEqual(f.rrule_type,"weekly","Thedefaultvalueshouldbedisplayed")

    deftest_event_activity_timezone(self):
        activty_type=self.env['mail.activity.type'].create({
            'name':'Meeting',
            'category':'meeting'
        })

        activity_id=self.env['mail.activity'].create({
            'summary':'Meetingwithpartner',
            'activity_type_id':activty_type.id,
            'res_model_id':self.env['ir.model'].search([('model','=','res.partner')],limit=1).id,
            'res_id':self.env['res.partner'].create({'name':'APartner'}).id,
        })

        calendar_event=self.env['calendar.event'].create({
            'name':'Meetingwithpartner',
            'activity_ids':[(6,False,activity_id.ids)],
            'start':'2018-11-1221:00:00',
            'stop':'2018-11-1300:00:00',
        })

        #CheckoutputinUTC
        self.assertEqual(str(activity_id.date_deadline),'2018-11-12')

        #Checkoutputintheuser'stz
        #writeontheeventtotriggersyncofactivities
        calendar_event.with_context({'tz':'Australia/Brisbane'}).write({
            'start':'2018-11-1221:00:00',
        })

        self.assertEqual(str(activity_id.date_deadline),'2018-11-13')

    deftest_event_allday_activity_timezone(self):
        #Coversusecaseofcommiteef4c3b48bcb4feac028bf640b545006dd0c9b91
        #Also,readthecommentinthecodeatcalendar.event._inverse_dates
        activty_type=self.env['mail.activity.type'].create({
            'name':'Meeting',
            'category':'meeting'
        })

        activity_id=self.env['mail.activity'].create({
            'summary':'Meetingwithpartner',
            'activity_type_id':activty_type.id,
            'res_model_id':self.env['ir.model'].search([('model','=','res.partner')],limit=1).id,
            'res_id':self.env['res.partner'].create({'name':'APartner'}).id,
        })

        calendar_event=self.env['calendar.event'].create({
            'name':'AllDay',
            'start':"2018-10-1600:00:00",
            'start_date':"2018-10-16",
            'stop':"2018-10-1800:00:00",
            'stop_date':"2018-10-18",
            'allday':True,
            'activity_ids':[(6,False,activity_id.ids)],
        })

        #CheckoutputinUTC
        self.assertEqual(str(activity_id.date_deadline),'2018-10-16')

        #Checkoutputintheuser'stz
        #writeontheeventtotriggersyncofactivities
        calendar_event.with_context({'tz':'Pacific/Honolulu'}).write({
            'start':'2018-10-1600:00:00',
            'start_date':'2018-10-16',
        })

        self.assertEqual(str(activity_id.date_deadline),'2018-10-16')

    deftest_event_creation_mail(self):
        """
        Checkthatmailaresenttotheattendeesoneventcreation
        Checkthatmailaresenttotheaddedattendeesoneventedit
        CheckthatmailareNOTsenttotheattendeeswhentheeventdateispast
        """

        def_test_one_mail_per_attendee(self,partners):
            #checkthateveryattendeereceivea(single)mailfortheevent
            forpartnerinpartners:
                mail=self.env['mail.message'].sudo().search([
                    ('notified_partner_ids','in',partner.id),
                    ])
                self.assertEqual(len(mail),1)

        partners=[
            self.env['res.partner'].create({'name':'testuser0','email':u'bob@example.com'}),
            self.env['res.partner'].create({'name':'testuser1','email':u'alice@example.com'}),
        ]
        partner_ids=[(6,False,[p.idforpinpartners]),]
        now=fields.Datetime.context_timestamp(partners[0],fields.Datetime.now())
        m=self.CalendarEvent.create({
            'name':"mailTest1",
            'allday':False,
            'rrule':u'FREQ=DAILY;INTERVAL=1;COUNT=5',
            'recurrency':True,
            'partner_ids':partner_ids,
            'start':fields.Datetime.to_string(now+timedelta(days=10)),
            'stop':fields.Datetime.to_string(now+timedelta(days=15)),
            })

        #everypartnershouldhave1mailsent
        _test_one_mail_per_attendee(self,partners)

        #addingmorepartnerstotheevent
        partners.extend([
            self.env['res.partner'].create({'name':'testuser2','email':u'marc@example.com'}),
            self.env['res.partner'].create({'name':'testuser3','email':u'carl@example.com'}),
            self.env['res.partner'].create({'name':'testuser4','email':u'alain@example.com'}),
            ])
        partner_ids=[(6,False,[p.idforpinpartners]),]
        m.write({
            'partner_ids':partner_ids,
            'recurrence_update':'all_events',
        })

        #moreemailshouldbesent
        _test_one_mail_per_attendee(self,partners)

        #createaneweventinthepast
        self.CalendarEvent.create({
            'name':"NOmailTest",
            'allday':False,
            'recurrency':False,
            'partner_ids':partner_ids,
            'start':fields.Datetime.to_string(now-timedelta(days=10)),
            'stop':fields.Datetime.to_string(now-timedelta(days=9)),
        })

        #nomoreemailshouldbesent
        _test_one_mail_per_attendee(self,partners)

    deftest_event_creation_sudo_other_company(self):
        """CheckAccessrightissuewhencreateeventwithsudo

            Createacompany,auserinthatcompany
            Createaneventforsomeoneelseinanothercompanyassudo
            Shouldnotfailedforaccesrightcheck
        """
        now=fields.Datetime.context_timestamp(self.partner_demo,fields.Datetime.now())

        web_company=self.env['res.company'].sudo().create({'name':"WebsiteCompany"})
        web_user=self.env['res.users'].with_company(web_company).sudo().create({
            'name':'webuser',
            'login':'web',
            'company_id':web_company.id
        })
        self.CalendarEvent.with_user(web_user).with_company(web_company).sudo().create({
            'name':"Test",
            'allday':False,
            'recurrency':False,
            'partner_ids':[(6,0,self.partner_demo.ids)],
            'alarm_ids':[(0,0,{
                'name':'Alarm',
                'alarm_type':'notification',
                'interval':'minutes',
                'duration':30,
            })],
            'user_id':self.user_demo.id,
            'start':fields.Datetime.to_string(now+timedelta(hours=5)),
            'stop':fields.Datetime.to_string(now+timedelta(hours=6)),
        })
