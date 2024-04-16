#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mail_full.tests.commonimportTestMailFullCommon,TestRecipients


classTestSMSPost(TestMailFullCommon,TestRecipients):
    """TODO

      *addtestsfornewmail.messageandmail.threadfields;
    """

    @classmethod
    defsetUpClass(cls):
        super(TestSMSPost,cls).setUpClass()
        cls._test_body='VOIDCONTENT'

        cls.test_record=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
            'name':'Test',
            'customer_id':cls.partner_1.id,
            'mobile_nbr':cls.test_numbers[0],
            'phone_nbr':cls.test_numbers[1],
        })
        cls.test_record=cls._reset_mail_context(cls.test_record)

    deftest_message_sms_internals_body(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms('<p>MegaSMS<br/>Topmoumoutte</p>',partner_ids=self.partner_1.ids)

        self.assertEqual(messages.body,'<p>MegaSMS<br>Topmoumoutte</p>')
        self.assertEqual(messages.subtype_id,self.env.ref('mail.mt_note'))
        self.assertSMSNotification([{'partner':self.partner_1}],'MegaSMS\nTopmoumoutte',messages)

    deftest_message_sms_internals_check_existing(self):
        withself.with_user('employee'),self.mockSMSGateway(sim_error='wrong_number_format'):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=self.partner_1.ids)

        self.assertSMSNotification([{'partner':self.partner_1,'state':'exception','failure_type':'sms_number_format'}],self._test_body,messages)

        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            test_record._notify_record_by_sms(messages,{'partners':[{'id':self.partner_1.id,'notif':'sms'}]},check_existing=True)
        self.assertSMSNotification([{'partner':self.partner_1}],self._test_body,messages)

    deftest_message_sms_internals_sms_numbers(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=self.partner_1.ids,sms_numbers=self.random_numbers)

        self.assertSMSNotification([{'partner':self.partner_1},{'number':self.random_numbers_san[0]},{'number':self.random_numbers_san[1]}],self._test_body,messages)

    deftest_message_sms_internals_subtype(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms('<p>MegaSMS<br/>Topmoumoutte</p>',subtype_id=self.env.ref('mail.mt_comment').id,partner_ids=self.partner_1.ids)

        self.assertEqual(messages.body,'<p>MegaSMS<br>Topmoumoutte</p>')
        self.assertEqual(messages.subtype_id,self.env.ref('mail.mt_comment'))
        self.assertSMSNotification([{'partner':self.partner_1}],'MegaSMS\nTopmoumoutte',messages)

    deftest_message_sms_internals_pid_to_number(self):
        pid_to_number={
            self.partner_1.id:self.random_numbers[0],
            self.partner_2.id:self.random_numbers[1],
        }
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2).ids,sms_pid_to_number=pid_to_number)

        self.assertSMSNotification([
            {'partner':self.partner_1,'number':self.random_numbers_san[0]},
            {'partner':self.partner_2,'number':self.random_numbers_san[1]}],
            self._test_body,messages)

    deftest_message_sms_model_partner(self):
        withself.with_user('employee'),self.mockSMSGateway():
            messages=self.partner_1._message_sms(self._test_body)
            messages|=self.partner_2._message_sms(self._test_body)
        self.assertSMSNotification([{'partner':self.partner_1},{'partner':self.partner_2}],self._test_body,messages)

    deftest_message_sms_model_partner_fallback(self):
        self.partner_1.write({'mobile':False,'phone':self.random_numbers[0]})

        withself.mockSMSGateway():
            messages=self.partner_1._message_sms(self._test_body)
            messages|=self.partner_2._message_sms(self._test_body)

        self.assertSMSNotification([{'partner':self.partner_1,'number':self.random_numbers_san[0]},{'partner':self.partner_2}],self._test_body,messages)

    deftest_message_sms_model_w_partner_only(self):
        withself.with_user('employee'):
            record=self.env['mail.test.sms.partner'].create({'customer_id':self.partner_1.id})

            withself.mockSMSGateway():
                messages=record._message_sms(self._test_body)

        self.assertSMSNotification([{'partner':self.partner_1}],self._test_body,messages)

    deftest_message_sms_model_w_partner_only_void(self):
        withself.with_user('employee'):
            record=self.env['mail.test.sms.partner'].create({'customer_id':False})

            withself.mockSMSGateway():
                messages=record._message_sms(self._test_body)

        #shouldnotcrashbuthaveafailednotification
        self.assertSMSNotification([{'partner':self.env['res.partner'],'number':False,'state':'exception','failure_type':'sms_number_missing'}],self._test_body,messages)

    deftest_message_sms_model_w_partner_m2m_only(self):
        withself.with_user('employee'):
            record=self.env['mail.test.sms.partner.2many'].create({'customer_ids':[(4,self.partner_1.id)]})

            withself.mockSMSGateway():
                messages=record._message_sms(self._test_body)

        self.assertSMSNotification([{'partner':self.partner_1}],self._test_body,messages)

        #TDE:shouldtakefirstfoundoneaccordingtopartnerordering
        withself.with_user('employee'):
            record=self.env['mail.test.sms.partner.2many'].create({'customer_ids':[(4,self.partner_1.id),(4,self.partner_2.id)]})

            withself.mockSMSGateway():
                messages=record._message_sms(self._test_body)

        self.assertSMSNotification([{'partner':self.partner_2}],self._test_body,messages)

    deftest_message_sms_on_field_w_partner(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,number_field='mobile_nbr')

        self.assertSMSNotification([{'partner':self.partner_1,'number':self.test_record.mobile_nbr}],self._test_body,messages)

    deftest_message_sms_on_field_wo_partner(self):
        self.test_record.write({'customer_id':False})

        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,number_field='mobile_nbr')

        self.assertSMSNotification([{'number':self.test_record.mobile_nbr}],self._test_body,messages)

    deftest_message_sms_on_field_wo_partner_wo_value(self):
        """Testrecordwithoutapartnerandwithoutphonevalues."""
        self.test_record.write({
            'customer_id':False,
            'phone_nbr':False,
            'mobile_nbr':False,
        })

        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body)

        #shouldnotcrashbuthaveafailednotification
        self.assertSMSNotification([{'partner':self.env['res.partner'],'number':False,'state':'exception','failure_type':'sms_number_missing'}],self._test_body,messages)

    deftest_message_sms_on_field_wo_partner_default_field(self):
        self.test_record.write({'customer_id':False})

        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body)

        self.assertSMSNotification([{'number':self.test_numbers_san[1]}],self._test_body,messages)

    deftest_message_sms_on_field_wo_partner_default_field_2(self):
        self.test_record.write({'customer_id':False,'phone_nbr':False})

        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body)

        self.assertSMSNotification([{'number':self.test_numbers_san[0]}],self._test_body,messages)

    deftest_message_sms_on_numbers(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,sms_numbers=self.random_numbers_san)
        self.assertSMSNotification([{'number':self.random_numbers_san[0]},{'number':self.random_numbers_san[1]}],self._test_body,messages)

    deftest_message_sms_on_numbers_sanitization(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,sms_numbers=self.random_numbers)
        self.assertSMSNotification([{'number':self.random_numbers_san[0]},{'number':self.random_numbers_san[1]}],self._test_body,messages)

    deftest_message_sms_on_partner_ids(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2).ids)

        self.assertSMSNotification([{'partner':self.partner_1},{'partner':self.partner_2}],self._test_body,messages)

    deftest_message_sms_on_partner_ids_default(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body)

        self.assertSMSNotification([{'partner':self.test_record.customer_id,'number':self.test_numbers_san[1]}],self._test_body,messages)

    deftest_message_sms_on_partner_ids_w_numbers(self):
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=self.partner_1.ids,sms_numbers=self.random_numbers[:1])

        self.assertSMSNotification([{'partner':self.partner_1},{'number':self.random_numbers_san[0]}],self._test_body,messages)

    deftest_message_sms_with_template(self):
        sms_template=self.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':self.env['ir.model']._get('mail.test.sms').id,
            'body':'Dear${object.display_name}thisisanSMS.',
        })

        withself.with_user('employee'):
            withself.mockSMSGateway():
                test_record=self.env['mail.test.sms'].browse(self.test_record.id)
                messages=test_record._message_sms_with_template(template=sms_template)

        self.assertSMSNotification([{'partner':self.partner_1,'number':self.test_numbers_san[1]}],'Dear%sthisisanSMS.'%self.test_record.display_name,messages)

    deftest_message_sms_with_template_fallback(self):
        withself.with_user('employee'):
            withself.mockSMSGateway():
                test_record=self.env['mail.test.sms'].browse(self.test_record.id)
                messages=test_record._message_sms_with_template(template_xmlid='test_mail_full.this_should_not_exists',template_fallback='Fallbackfor${object.id}')

        self.assertSMSNotification([{'partner':self.partner_1,'number':self.test_numbers_san[1]}],'Fallbackfor%s'%self.test_record.id,messages)

    deftest_message_sms_with_template_xmlid(self):
        sms_template=self.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':self.env['ir.model']._get('mail.test.sms').id,
            'body':'Dear${object.display_name}thisisanSMS.',
        })
        self.env['ir.model.data'].create({
            'name':'this_should_exists',
            'module':'test_mail_full',
            'model':sms_template._name,
            'res_id':sms_template.id,
        })

        withself.with_user('employee'):
            withself.mockSMSGateway():
                test_record=self.env['mail.test.sms'].browse(self.test_record.id)
                messages=test_record._message_sms_with_template(template_xmlid='test_mail_full.this_should_exists')

        self.assertSMSNotification([{'partner':self.partner_1,'number':self.test_numbers_san[1]}],'Dear%sthisisanSMS.'%self.test_record.display_name,messages)


classTestSMSPostException(TestMailFullCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestSMSPostException,cls).setUpClass()
        cls._test_body='VOIDCONTENT'

        cls.test_record=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
            'name':'Test',
            'customer_id':cls.partner_1.id,
        })
        cls.test_record=cls._reset_mail_context(cls.test_record)
        cls.partner_3=cls.env['res.partner'].with_context({
            'mail_create_nolog':True,
            'mail_create_nosubscribe':True,
            'mail_notrack':True,
            'no_reset_password':True,
        }).create({
            'name':'ErnestineLoubine',
            'email':'ernestine.loubine@agrolait.com',
            'country_id':cls.env.ref('base.be').id,
            'mobile':'0475556644',
        })

    deftest_message_sms_w_numbers_invalid(self):
        random_numbers=self.random_numbers+['6988754']
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,sms_numbers=random_numbers)

        #invalidnumbersarestillgiventoIAPcurrentlyastheyare
        self.assertSMSNotification([{'number':self.random_numbers_san[0]},{'number':self.random_numbers_san[1]},{'number':random_numbers[2]}],self._test_body,messages)

    deftest_message_sms_w_partners_nocountry(self):
        self.test_record.customer_id.write({
            'mobile':self.random_numbers[0],
            'phone':self.random_numbers[1],
            'country_id':False,
        })
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=self.test_record.customer_id.ids)

        self.assertSMSNotification([{'partner':self.test_record.customer_id}],self._test_body,messages)

    deftest_message_sms_w_partners_falsy(self):
        #TDEFIXME:currentlysenttoIAP
        self.test_record.customer_id.write({
            'mobile':'youpie',
            'phone':'youpla',
        })
        withself.with_user('employee'),self.mockSMSGateway():
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=self.test_record.customer_id.ids)

        #self.assertSMSNotification({self.test_record.customer_id:{}},{},self._test_body,messages)

    deftest_message_sms_w_numbers_sanitization_duplicate(self):
        pass
        #TDEFIXME:notsure
        #random_numbers=self.random_numbers+[self.random_numbers[1]]
        #random_numbers_san=self.random_numbers_san+[self.random_numbers_san[1]]
        #withself.with_user('employee'),self.mockSMSGateway():
        #    messages=self.test_record._message_sms(self._test_body,sms_numbers=random_numbers)
        #self.assertSMSNotification({},{random_numbers_san[0]:{},random_numbers_san[1]:{},random_numbers_san[2]:{}},self._test_body,messages)

    deftest_message_sms_crash_credit(self):
        withself.with_user('employee'),self.mockSMSGateway(sim_error='credit'):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'exception','failure_type':'sms_credit'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_credit'},
        ],self._test_body,messages)

    deftest_message_sms_crash_credit_single(self):
        withself.with_user('employee'),self.mockSMSGateway(nbr_t_error={self.partner_2.phone_get_sanitized_number():'credit'}):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2|self.partner_3).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'sent'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_credit'},
            {'partner':self.partner_3,'state':'sent'},
        ],self._test_body,messages)

    deftest_message_sms_crash_server_crash(self):
        withself.with_user('employee'),self.mockSMSGateway(sim_error='jsonrpc_exception'):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2|self.partner_3).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'exception','failure_type':'sms_server'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_server'},
            {'partner':self.partner_3,'state':'exception','failure_type':'sms_server'},
        ],self._test_body,messages)

    deftest_message_sms_crash_unregistered(self):
        withself.with_user('employee'),self.mockSMSGateway(sim_error='unregistered'):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'exception','failure_type':'sms_acc'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_acc'},
        ],self._test_body,messages)

    deftest_message_sms_crash_unregistered_single(self):
        withself.with_user('employee'),self.mockSMSGateway(nbr_t_error={self.partner_2.phone_get_sanitized_number():'unregistered'}):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2|self.partner_3).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'sent'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_acc'},
            {'partner':self.partner_3,'state':'sent'},
        ],self._test_body,messages)

    deftest_message_sms_crash_wrong_number(self):
        withself.with_user('employee'),self.mockSMSGateway(sim_error='wrong_number_format'):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'exception','failure_type':'sms_number_format'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_number_format'},
        ],self._test_body,messages)

    deftest_message_sms_crash_wrong_number_single(self):
        withself.with_user('employee'),self.mockSMSGateway(nbr_t_error={self.partner_2.phone_get_sanitized_number():'wrong_number_format'}):
            test_record=self.env['mail.test.sms'].browse(self.test_record.id)
            messages=test_record._message_sms(self._test_body,partner_ids=(self.partner_1|self.partner_2|self.partner_3).ids)

        self.assertSMSNotification([
            {'partner':self.partner_1,'state':'sent'},
            {'partner':self.partner_2,'state':'exception','failure_type':'sms_number_format'},
            {'partner':self.partner_3,'state':'sent'},
        ],self._test_body,messages)


classTestSMSApi(TestMailFullCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestSMSApi,cls).setUpClass()
        cls._test_body='ZizisseanSMS.'

        cls._create_records_for_batch('mail.test.sms',3)
        cls.sms_template=cls._create_sms_template('mail.test.sms')

    deftest_message_schedule_sms(self):
        withself.with_user('employee'):
            withself.mockSMSGateway():
                self.env['mail.test.sms'].browse(self.records.ids)._message_sms_schedule_mass(body=self._test_body,mass_keep_log=False)

        forrecordinself.records:
            self.assertSMSOutgoing(record.customer_id,None,content=self._test_body)

    deftest_message_schedule_sms_w_log(self):
        withself.with_user('employee'):
            withself.mockSMSGateway():
                self.env['mail.test.sms'].browse(self.records.ids)._message_sms_schedule_mass(body=self._test_body,mass_keep_log=True)

        forrecordinself.records:
            self.assertSMSOutgoing(record.customer_id,None,content=self._test_body)
            self.assertSMSLogged(record,self._test_body)

    deftest_message_schedule_sms_w_template(self):
        withself.with_user('employee'):
            withself.mockSMSGateway():
                self.env['mail.test.sms'].browse(self.records.ids)._message_sms_schedule_mass(template=self.sms_template,mass_keep_log=False)

        forrecordinself.records:
            self.assertSMSOutgoing(record.customer_id,None,content='Dear%sthisisanSMS.'%record.display_name)

    deftest_message_schedule_sms_w_template_and_log(self):
        withself.with_user('employee'):
            withself.mockSMSGateway():
                self.env['mail.test.sms'].browse(self.records.ids)._message_sms_schedule_mass(template=self.sms_template,mass_keep_log=True)

        forrecordinself.records:
            self.assertSMSOutgoing(record.customer_id,None,content='Dear%sthisisanSMS.'%record.display_name)
            self.assertSMSLogged(record,'Dear%sthisisanSMS.'%record.display_name)
