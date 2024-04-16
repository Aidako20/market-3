#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.event.tests.commonimportTestEventCommon
fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.addons.sms.tests.commonimportSMSCase


classTestSMSSchedule(TestEventCommon,SMSCase):

    @classmethod
    defsetUpClass(cls):
        super(TestSMSSchedule,cls).setUpClass()

        cls.sms_template_sub=cls.env['sms.template'].create({
            'name':'Testsubscription',
            'model_id':cls.env.ref('event.model_event_registration').id,
            'body':'${object.event_id.organizer_id.name}registrationconfirmation.',
            'lang':'${object.partner_id.lang}'
        })
        cls.sms_template_rem=cls.env['sms.template'].create({
            'name':'Testreminder',
            'model_id':cls.env.ref('event.model_event_registration').id,
            'body':'${object.event_id.organizer_id.name}reminder',
            'lang':'${object.partner_id.lang}'
        })

        cls.event_0.write({
            'event_mail_ids':[
                (0,0,{ #rightatsubscription
                    'interval_unit':'now',
                    'interval_type':'after_sub',
                    'notification_type':'sms',
                    'sms_template_id':cls.sms_template_sub.id}),
                (0,0,{ #3daysbeforeevent
                    'interval_nbr':3,
                    'interval_unit':'days',
                    'interval_type':'before_event',
                    'notification_type':'sms',
                    'sms_template_id':cls.sms_template_rem.id}),
            ]
        })

    deftest_sms_schedule(self):
        withself.mockSMSGateway():
            self._create_registrations(self.event_0,3)

        #checksubscriptionscheduler
        schedulers=self.env['event.mail'].search([('event_id','=',self.event_0.id),('interval_type','=','after_sub')])
        self.assertEqual(len(schedulers),1)
        self.assertEqual(schedulers.scheduled_date,self.event_0.create_date,'event:incorrectscheduleddateforcheckingcontroller')

        #verifythatsubscriptionschedulerwasauto-executedaftereachregistration
        self.assertEqual(len(schedulers.mail_registration_ids),3)
        self.assertTrue(all(m.mail_sentisTrueforminschedulers.mail_registration_ids))
        self.assertEqual(schedulers.mapped('mail_registration_ids.registration_id'),self.event_0.registration_ids)
        sanitized_numbers=[]
        forregistrationinself.event_0.registration_ids:
            reg_sanitized_number=phone_validation.phone_format(registration.phone,'BE','32',force_format='E164')
            sanitized_numbers.append(reg_sanitized_number)
            self.assertSMSOutgoing(
                self.env['res.partner'],reg_sanitized_number,
                content='%sregistrationconfirmation.'%self.event_0.organizer_id.name)

        #clearnotificationqueuetoavoidconflictswhencheckingnextnotifications
        self.env['mail.notification'].search([('sms_number','in',sanitized_numbers)]).unlink()
        self.env['sms.sms'].search([('number','in',sanitized_numbers)]).unlink()

        #checkbeforeeventscheduler
        schedulers=self.env['event.mail'].search([('event_id','=',self.event_0.id),('interval_type','=','before_event')])
        self.assertEqual(len(schedulers),1,'event:wrongschedulercreation')
        self.assertEqual(schedulers[0].scheduled_date,self.event_0.date_begin+relativedelta(days=-3))

        #executeeventreminderschedulerexplicitly
        withself.mockSMSGateway():
            schedulers.execute()

        #verifythatsubscriptionschedulerwasauto-executedaftereachregistration
        forregistrationinself.event_0.registration_ids:
            reg_sanitized_number=phone_validation.phone_format(registration.phone,'BE','32',force_format='E164')
            self.assertSMSOutgoing(
                self.env['res.partner'],reg_sanitized_number,
                content='%sreminder'%self.event_0.organizer_id.name)
