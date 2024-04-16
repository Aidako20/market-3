#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mail_full.tests.commonimportTestMailFullCommon,TestRecipients


classTestServerAction(TestMailFullCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestServerAction,cls).setUpClass()
        cls.test_record=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
            'name':'Test',
            'customer_id':cls.partner_1.id,
        })
        cls.test_record_2=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
            'name':'TestRecord2',
            'customer_id':False,
            'phone_nbr':cls.test_numbers[0],
        })

        cls.sms_template=cls._create_sms_template('mail.test.sms')
        cls.action=cls.env['ir.actions.server'].create({
            'name':'TestSMSAction',
            'model_id':cls.env['ir.model']._get('mail.test.sms').id,
            'state':'sms',
            'sms_template_id':cls.sms_template.id,
            'groups_id':cls.env.ref('base.group_user'),
        })

    deftest_action_sms(self):
        context={
            'active_model':'mail.test.sms',
            'active_ids':(self.test_record|self.test_record_2).ids,
        }

        withself.with_user('employee'),self.mockSMSGateway():
            self.action.with_user(self.env.user).with_context(**context).run()

        self.assertSMSOutgoing(self.test_record.customer_id,None,content='Dear%sthisisanSMS.'%self.test_record.display_name)
        self.assertSMSOutgoing(self.env['res.partner'],self.test_numbers_san[0],content='Dear%sthisisanSMS.'%self.test_record_2.display_name)

    deftest_action_sms_single(self):
        context={
            'active_model':'mail.test.sms',
            'active_id':self.test_record.id,
        }

        withself.with_user('employee'),self.mockSMSGateway():
            self.action.with_user(self.env.user).with_context(**context).run()
        self.assertSMSOutgoing(self.test_record.customer_id,None,content='Dear%sthisisanSMS.'%self.test_record.display_name)

    deftest_action_sms_w_log(self):
        self.action.sms_mass_keep_log=True
        context={
            'active_model':'mail.test.sms',
            'active_ids':(self.test_record|self.test_record_2).ids,
        }

        withself.with_user('employee'),self.mockSMSGateway():
            self.action.with_user(self.env.user).with_context(**context).run()

        self.assertSMSOutgoing(self.test_record.customer_id,None,content='Dear%sthisisanSMS.'%self.test_record.display_name)
        self.assertSMSLogged(self.test_record,'Dear%sthisisanSMS.'%self.test_record.display_name)

        self.assertSMSOutgoing(self.env['res.partner'],self.test_numbers_san[0],content='Dear%sthisisanSMS.'%self.test_record_2.display_name)
        self.assertSMSLogged(self.test_record_2,'Dear%sthisisanSMS.'%self.test_record_2.display_name)
