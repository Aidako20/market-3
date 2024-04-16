#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mail_full.tests.commonimportTestMailFullCommon,TestRecipients


classTestSMSWizards(TestMailFullCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestSMSWizards,cls).setUpClass()
        cls.test_record=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
            'name':'Test',
            'customer_id':cls.partner_1.id,
        })
        cls.test_record=cls._reset_mail_context(cls.test_record)
        cls.msg=cls.test_record.message_post(body='TESTBODY',author_id=cls.partner_employee.id)
        cls.notif_p1=cls.env['mail.notification'].create({
            'mail_message_id':cls.msg.id,
            'res_partner_id':cls.partner_1.id,
            'sms_number':cls.partner_1.mobile,
            'notification_type':'sms',
            'notification_status':'exception',
            'failure_type':'sms_number_format',
        })
        cls.notif_p2=cls.env['mail.notification'].create({
            'mail_message_id':cls.msg.id,
            'res_partner_id':cls.partner_2.id,
            'sms_number':cls.partner_2.mobile,
            'notification_type':'sms',
            'notification_status':'exception',
            'failure_type':'sms_credit',
        })

    deftest_sms_resend(self):
        self._reset_bus()

        withself.with_user('employee'):
            wizard=self.env['sms.resend'].with_context(default_mail_message_id=self.msg.id).create({})
            wizard.write({'recipient_ids':[(1,r.id,{'resend':True})forrinwizard.recipient_ids]})
            withself.mockSMSGateway():
                wizard.action_resend()

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'sent'},
            {'partner':self.partner_2,'state':'sent'}
        ],'TESTBODY',self.msg,check_sms=True)
        self.assertMessageBusNotifications(self.msg)

    deftest_sms_resend_update_number(self):
        self._reset_bus()

        withself.with_user('employee'):
            wizard=self.env['sms.resend'].with_context(default_mail_message_id=self.msg.id).create({})
            wizard.write({'recipient_ids':[(1,r.id,{'resend':True,'sms_number':self.random_numbers[idx]})foridx,rinenumerate(wizard.recipient_ids.sorted())]})
            withself.mockSMSGateway():
                wizard.action_resend()

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'sent','number':self.random_numbers_san[0]},
            {'partner':self.partner_2,'state':'sent','number':self.random_numbers_san[1]}
        ],'TESTBODY',self.msg,check_sms=True)
        self.assertMessageBusNotifications(self.msg)

    deftest_sms_resend_cancel(self):
        self._reset_bus()

        withself.with_user('employee'):
            wizard=self.env['sms.resend'].with_context(default_mail_message_id=self.msg.id).create({})
            withself.mockSMSGateway():
                wizard.action_cancel()

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'canceled','number':self.notif_p1.sms_number,'failure_type':'sms_number_format'},
            {'partner':self.partner_2,'state':'canceled','number':self.notif_p2.sms_number,'failure_type':'sms_credit'}
        ],'TESTBODY',self.msg,check_sms=False)
        self.assertMessageBusNotifications(self.msg)

    deftest_sms_resend_internals(self):
        self._reset_bus()
        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'exception','number':self.notif_p1.sms_number,'failure_type':'sms_number_format'},
            {'partner':self.partner_2,'state':'exception','number':self.notif_p2.sms_number,'failure_type':'sms_credit'}
        ],'TESTBODY',self.msg,check_sms=False)

        withself.with_user('employee'):
            wizard=self.env['sms.resend'].with_context(default_mail_message_id=self.msg.id).create({})
            self.assertTrue(wizard.has_insufficient_credit)
            self.assertEqual(set(wizard.mapped('recipient_ids.partner_name')),set((self.partner_1|self.partner_2).mapped('display_name')))
            wizard.write({'recipient_ids':[(1,r.id,{'resend':True})forrinwizard.recipient_ids]})
            withself.mockSMSGateway():
                wizard.action_resend()

    deftest_sms_resend_w_cancel(self):
        self._reset_bus()

        withself.with_user('employee'):
            wizard=self.env['sms.resend'].with_context(default_mail_message_id=self.msg.id).create({})
            wizard.write({'recipient_ids':[(1,r.id,{'resend':Trueifr.partner_id==self.partner_1elseFalse})forrinwizard.recipient_ids]})
            withself.mockSMSGateway():
                wizard.action_resend()

        self.assertSMSNotification([{'partner':self.partner_1,'state':'sent'}],'TESTBODY',self.msg,check_sms=True)
        self.assertSMSNotification([{'partner':self.partner_2,'state':'canceled','number':self.notif_p2.sms_number,'failure_type':'sms_credit'}],'TESTBODY',self.msg,check_sms=False)
        self.assertMessageBusNotifications(self.msg)

    deftest_sms_cancel(self):
        self._reset_bus()

        withself.mockSMSGateway(),self.with_user('employee'):
            wizard=self.env['sms.cancel'].with_context(default_model=self.msg.model).create({})
            wizard.action_cancel()

            self.assertEqual((self.notif_p1|self.notif_p2).mapped('notification_status'),['canceled','canceled'])

        self.assertMessageBusNotifications(self.msg)
