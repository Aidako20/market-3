#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta
fromfreezegunimportfreeze_time

fromflectra.addons.event.tests.commonimportTestEventCommon
fromflectra.addons.mail.tests.commonimportMockEmail
fromflectra.toolsimportformataddr,mute_logger


classTestMailSchedule(TestEventCommon,MockEmail):

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_event_mail_schedule(self):
        """Testmailschedulingforevents"""
        event_cron_id=self.env.ref('event.event_mail_scheduler')

        #deactivateotherschedulerstoavoidmessingwithcrons
        self.env['event.mail'].search([]).unlink()

        #freezesomedatetimes,andensuremorethan1D+1Hbeforeeventstarts
        #toeasetime-basedschedulercheck
        now=datetime(2021,3,20,14,30,15)
        event_date_begin=datetime(2021,3,22,8,0,0)
        event_date_end=datetime(2021,3,24,18,0,0)

        withfreeze_time(now):
            test_event=self.env['event.event'].with_user(self.user_eventmanager).create({
                'name':'TestEventMail',
                'auto_confirm':True,
                'date_begin':event_date_begin,
                'date_end':event_date_end,
                'event_mail_ids':[
                    (0,0,{ #rightatsubscription
                        'interval_unit':'now',
                        'interval_type':'after_sub',
                        'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_subscription')}),
                    (0,0,{ #onedayaftersubscription
                        'interval_nbr':1,
                        'interval_unit':'hours',
                        'interval_type':'after_sub',
                        'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_subscription')}),
                    (0,0,{ #1daysbeforeevent
                        'interval_nbr':1,
                        'interval_unit':'days',
                        'interval_type':'before_event',
                        'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')}),
                    (0,0,{ #immediatelyafterevent
                        'interval_nbr':1,
                        'interval_unit':'hours',
                        'interval_type':'after_event',
                        'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')}),
                ]
            })

        #checksubscriptionscheduler
        after_sub_scheduler=self.env['event.mail'].search([('event_id','=',test_event.id),('interval_type','=','after_sub'),('interval_unit','=','now')])
        self.assertEqual(len(after_sub_scheduler),1,'event:wrongschedulercreation')
        self.assertEqual(after_sub_scheduler.scheduled_date,test_event.create_date)
        self.assertTrue(after_sub_scheduler.done)
        after_sub_scheduler_2=self.env['event.mail'].search([('event_id','=',test_event.id),('interval_type','=','after_sub'),('interval_unit','=','hours')])
        self.assertEqual(len(after_sub_scheduler_2),1,'event:wrongschedulercreation')
        self.assertEqual(after_sub_scheduler_2.scheduled_date,test_event.create_date+relativedelta(hours=1))
        self.assertTrue(after_sub_scheduler_2.done)
        #checkbeforeeventscheduler
        event_prev_scheduler=self.env['event.mail'].search([('event_id','=',test_event.id),('interval_type','=','before_event')])
        self.assertEqual(len(event_prev_scheduler),1,'event:wrongschedulercreation')
        self.assertEqual(event_prev_scheduler.scheduled_date,event_date_begin+relativedelta(days=-1))
        self.assertFalse(event_prev_scheduler.done)
        #checkaftereventscheduler
        event_next_scheduler=self.env['event.mail'].search([('event_id','=',test_event.id),('interval_type','=','after_event')])
        self.assertEqual(len(event_next_scheduler),1,'event:wrongschedulercreation')
        self.assertEqual(event_next_scheduler.scheduled_date,event_date_end+relativedelta(hours=1))
        self.assertFalse(event_next_scheduler.done)

        #createsomeregistrations
        withfreeze_time(now),self.mock_mail_gateway():
            reg1=self.env['event.registration'].with_user(self.user_eventuser).create({
                'event_id':test_event.id,
                'name':'Reg1',
                'email':'reg1@example.com',
            })
            reg2=self.env['event.registration'].with_user(self.user_eventuser).create({
                'event_id':test_event.id,
                'name':'Reg2',
                'email':'reg2@example.com',
            })

        #REGISTRATIONS/PRESCHEDULERS
        #--------------------------------------------------

        #checkregistrationstate
        self.assertTrue(all(reg.state=='open'forreginreg1+reg2),'Registrations:shouldbeauto-confirmed')
        self.assertTrue(all(reg.date_open==nowforreginreg1+reg2),'Registrations:shouldhaveopendatesettoconfirmdate')

        #verifythatsubscriptionschedulerwasauto-executedaftereachregistration
        self.assertEqual(len(after_sub_scheduler.mail_registration_ids),2,'event:shouldhave2scheduledcommunication(1/registration)')
        formail_registrationinafter_sub_scheduler.mail_registration_ids:
            self.assertEqual(mail_registration.scheduled_date,now)
            self.assertTrue(mail_registration.mail_sent,'event:registrationmailshouldbesentatregistrationcreation')
        self.assertTrue(after_sub_scheduler.done,'event:allsubscriptionmailsshouldhavebeensent')

        #checkemailseffectivelysent
        self.assertEqual(len(self._new_mails),2,'event:shouldhave2scheduledemails(1/registration)')
        self.assertMailMailWEmails(
            [formataddr((reg1.name,reg1.email)),formataddr((reg2.name,reg2.email))],
            'outgoing',
            content=None,
            fields_values={'subject':'Yourregistrationat%s'%test_event.name,
                           'email_from':self.user_eventmanager.company_id.email_formatted,
                          })

        #sameforsecondscheduler:scheduledbutnotsent
        self.assertEqual(len(after_sub_scheduler_2.mail_registration_ids),2,'event:shouldhave2scheduledcommunication(1/registration)')
        formail_registrationinafter_sub_scheduler_2.mail_registration_ids:
            self.assertEqual(mail_registration.scheduled_date,now+relativedelta(hours=1))
            self.assertFalse(mail_registration.mail_sent,'event:registrationmailshouldbescheduled,notsent')
        self.assertFalse(after_sub_scheduler_2.done,'event:allsubscriptionmailsshouldbescheduled,notsent')

        #executeeventreminderschedulerexplicitly,beforescheduleddate->shouldnotdoanything
        withfreeze_time(now),self.mock_mail_gateway():
            after_sub_scheduler_2.execute()
        self.assertFalse(any(mail_reg.mail_sentformail_reginafter_sub_scheduler_2.mail_registration_ids))
        self.assertFalse(after_sub_scheduler_2.done)
        self.assertEqual(len(self._new_mails),0,'event:shouldnotsendmailsbeforescheduleddate')

        #executeeventreminderschedulerexplicitly,rightatscheduleddate->shouldsentmails
        now_registration=now+relativedelta(hours=1)
        withfreeze_time(now_registration),self.mock_mail_gateway():
            after_sub_scheduler_2.execute()

        #verifythatsubscriptionschedulerwasauto-executedaftereachregistration
        self.assertEqual(len(after_sub_scheduler_2.mail_registration_ids),2,'event:shouldhave2scheduledcommunication(1/registration)')
        self.assertTrue(all(mail_reg.mail_sentformail_reginafter_sub_scheduler_2.mail_registration_ids))
        #FIXME:fieldnotupdated
        #self.assertTrue(after_sub_scheduler_2.done,'event:allsubscriptionmailsshouldhavebeensent')

        #checkemailseffectivelysent
        self.assertEqual(len(self._new_mails),2,'event:shouldhave2scheduledemails(1/registration)')
        self.assertMailMailWEmails(
            [formataddr((reg1.name,reg1.email)),formataddr((reg2.name,reg2.email))],
            'outgoing',
            content=None,
            fields_values={'subject':'Yourregistrationat%s'%test_event.name,
                           'email_from':self.user_eventmanager.company_id.email_formatted,
                          })

        #PRESCHEDULERS(MOVEFORWARDINTIME)
        #--------------------------------------------------

        self.assertFalse(event_prev_scheduler.mail_sent)
        self.assertFalse(event_prev_scheduler.done)

        #executeeventreminderschedulerexplicitly,beforescheduleddate->shouldnotdoanything
        now_start=event_date_begin+relativedelta(hours=-25)
        withfreeze_time(now_start),self.mock_mail_gateway():
            event_prev_scheduler.execute()

        self.assertFalse(event_prev_scheduler.mail_sent)
        self.assertFalse(event_prev_scheduler.done)
        self.assertEqual(len(self._new_mails),0)

        #executecrontorunschedulers
        now_start=event_date_begin+relativedelta(hours=-23)
        withfreeze_time(now_start),self.mock_mail_gateway():
            event_cron_id.method_direct_trigger()

        #checkthatschedulerisfinished
        self.assertTrue(event_prev_scheduler.mail_sent,'event:reminderschedulershouldhaverun')
        self.assertTrue(event_prev_scheduler.done,'event:reminderschedulershouldhaverun')

        #checkemailseffectivelysent
        self.assertEqual(len(self._new_mails),2,'event:shouldhavescheduled2mails(1/registration)')
        self.assertMailMailWEmails(
            [formataddr((reg1.name,reg1.email)),formataddr((reg2.name,reg2.email))],
            'outgoing',
            content=None,
            fields_values={'subject':'%s:tomorrow'%test_event.name,
                           'email_from':self.user_eventmanager.company_id.email_formatted,
                          })

        #NEWREGISTRATIONEFFECTONSCHEDULERS
        #--------------------------------------------------

        test_event.write({'auto_confirm':False})
        withfreeze_time(now_start),self.mock_mail_gateway():
            reg3=self.env['event.registration'].with_user(self.user_eventuser).create({
                'event_id':test_event.id,
                'name':'Reg3',
                'email':'reg3@example.com',
            })

        #nomoreseats
        self.assertEqual(reg3.state,'draft')

        #schedulersstateuntouched
        self.assertTrue(event_prev_scheduler.mail_sent)
        self.assertTrue(event_prev_scheduler.mail_sent)
        self.assertFalse(event_next_scheduler.mail_sent)
        self.assertFalse(event_next_scheduler.done)
        self.assertFalse(after_sub_scheduler.done,'event:schedulerregistrationsshouldbelowerthaneffectiveregistrations')
        self.assertFalse(after_sub_scheduler_2.done,'event:schedulerregistrationsshouldbelowerthaneffectiveregistrations')

        #confirmregistration->shouldtriggerregistrationschedulers
        #NOTE:currentlyallschedulersarebasedondate_openwhichequalscreate_date
        #meaningseveralcommunicationsmaybesentinthetimetime
        withfreeze_time(now_start+relativedelta(hours=1)),self.mock_mail_gateway():
            reg3.action_confirm()

       #verifythatsubscriptionschedulerwasauto-executedafternewregistrationconfirmed
        self.assertEqual(len(after_sub_scheduler.mail_registration_ids),3,'event:shouldhave3scheduledcommunication(1/registration)')
        new_mail_reg=after_sub_scheduler.mail_registration_ids.filtered(lambdamail_reg:mail_reg.registration_id==reg3)
        self.assertEqual(new_mail_reg.scheduled_date,now_start)
        self.assertTrue(new_mail_reg.mail_sent,'event:registrationmailshouldbesentatregistrationcreation')
        self.assertTrue(after_sub_scheduler.done,'event:allsubscriptionmailsshouldhavebeensent')

       #verifythatsubscriptionschedulerwasauto-executedafternewregistrationconfirmed
        self.assertEqual(len(after_sub_scheduler_2.mail_registration_ids),3,'event:shouldhave3scheduledcommunication(1/registration)')
        new_mail_reg=after_sub_scheduler_2.mail_registration_ids.filtered(lambdamail_reg:mail_reg.registration_id==reg3)
        self.assertEqual(new_mail_reg.scheduled_date,now_start+relativedelta(hours=1))
        self.assertTrue(new_mail_reg.mail_sent,'event:registrationmailshouldbesentatregistrationcreation')
        self.assertTrue(after_sub_scheduler_2.done,'event:allsubscriptionmailsshouldhavebeensent')

        #checkemailseffectivelysent
        self.assertEqual(len(self._new_mails),2,'event:shouldhave1scheduledemails(newregistrationonly)')
        #manualcheckbecause2identicalmailsaresentandmailtoolsdonotsupportiteasily
        formailinself._new_mails:
            self.assertEqual(mail.email_from,self.user_eventmanager.company_id.email_formatted)
            self.assertEqual(mail.subject,'Yourregistrationat%s'%test_event.name)
            self.assertEqual(mail.state,'outgoing')
            self.assertEqual(mail.email_to,formataddr((reg3.name,reg3.email)))

        #POSTSCHEDULERS(MOVEFORWARDINTIME)
        #--------------------------------------------------

        self.assertFalse(event_next_scheduler.mail_sent)
        self.assertFalse(event_next_scheduler.done)

        #executeeventreminderschedulerexplicitlyafteritsscheduledate
        new_end=event_date_end+relativedelta(hours=2)
        withfreeze_time(new_end),self.mock_mail_gateway():
            event_cron_id.method_direct_trigger()

        #checkthatschedulerisfinished
        self.assertTrue(event_next_scheduler.mail_sent,'event:reminderschedulershouldshouldhaverun')
        self.assertTrue(event_next_scheduler.done,'event:reminderschedulershouldhaverun')

        #checkemailseffectivelysent
        self.assertEqual(len(self._new_mails),3,'event:shouldhavescheduled3mails,oneforeachregistration')
        self.assertMailMailWEmails(
            [formataddr((reg1.name,reg1.email)),formataddr((reg2.name,reg2.email)),formataddr((reg3.name,reg3.email))],
            'outgoing',
            content=None,
            fields_values={'subject':'%s:today'%test_event.name,
                           'email_from':self.user_eventmanager.company_id.email_formatted,
                          })

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_archived_event_mail_schedule(self):
        """Testmailschedulingforarchivedevents"""
        event_cron_id=self.env.ref('event.event_mail_scheduler')

        #deactivateotherschedulerstoavoidmessingwithcrons
        self.env['event.mail'].search([]).unlink()

        #freezesomedatetimes,andensuremorethan1D+1Hbeforeeventstarts
        #toeasetime-basedschedulercheck
        now=datetime(2023,7,24,14,30,15)
        event_date_begin=datetime(2023,7,26,8,0,0)
        event_date_end=datetime(2023,7,28,18,0,0)

        withfreeze_time(now):
            test_event=self.env['event.event'].with_user(self.user_eventmanager).create({
                'name':'TestEventMail',
                'auto_confirm':True,
                'date_begin':event_date_begin,
                'date_end':event_date_end,
                'event_mail_ids':[
                    (0,0,{ #rightatsubscription
                        'interval_unit':'now',
                        'interval_type':'after_sub',
                        'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_subscription')}),
                    (0,0,{ #3hoursbeforeevent
                        'interval_nbr':3,
                        'interval_unit':'hours',
                        'interval_type':'before_event',
                        'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')})
                ]
            })

        #checkeventscheduler
        scheduler=self.env['event.mail'].search([('event_id','=',test_event.id)])
        self.assertEqual(len(scheduler),2,'event:wrongschedulercreation')

        event_prev_scheduler=self.env['event.mail'].search([('event_id','=',test_event.id),('interval_type','=','before_event')])

        withfreeze_time(now),self.mock_mail_gateway():
            self.env['event.registration'].with_user(self.user_eventuser).create({
                'event_id':test_event.id,
                'name':'Reg1',
                'email':'reg1@example.com',
            })
            self.env['event.registration'].with_user(self.user_eventuser).create({
                'event_id':test_event.id,
                'name':'Reg2',
                'email':'reg2@example.com',
            })
        #checkemailseffectivelysent
        self.assertEqual(len(self._new_mails),2,'event:shouldhave2scheduledemails(1/registration)')

        #ArchivetheEvent
        test_event.action_archive()

        #executecrontorunschedulers
        now_start=event_date_begin+relativedelta(hours=-3)
        withfreeze_time(now_start),self.mock_mail_gateway():
            event_cron_id.method_direct_trigger()

        #checkthatschedulerisnotexecuted
        self.assertFalse(event_prev_scheduler.mail_sent,'event:reminderschedulershouldnotrun')
        self.assertFalse(event_prev_scheduler.done,'event:reminderschedulershouldnotrun')
