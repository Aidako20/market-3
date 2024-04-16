#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.addons.test_mail_full.tests.commonimportTestMailFullCommon
fromflectraimportexceptions
fromflectra.testsimporttagged
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger


@tagged('mass_mailing')
classTestMassSMSCommon(TestMailFullCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassSMSCommon,cls).setUpClass()
        cls._test_body='MassSMSinyourface'

        records=cls.env['mail.test.sms']
        partners=cls.env['res.partner']
        country_be_id=cls.env.ref('base.be').id,
        country_us_id=cls.env.ref('base.us').id,

        forxinrange(10):
            partners+=cls.env['res.partner'].with_context(**cls._test_context).create({
                'name':'Partner_%s'%(x),
                'email':'_test_partner_%s@example.com'%(x),
                'country_id':country_be_id,
                'mobile':'045600%s%s99'%(x,x)
            })
            records+=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
                'name':'MassSMSTest_%s'%(x),
                'customer_id':partners[x].id,
                'phone_nbr':'045600%s%s44'%(x,x)
            })
        cls.records=cls._reset_mail_context(records)
        cls.records_numbers=[phone_validation.phone_format(r.phone_nbr,'BE','32',force_format='E164')forrincls.records]
        cls.partners=partners

        cls.sms_template=cls.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':cls.env['ir.model']._get('mail.test.sms').id,
            'body':'Dear${object.display_name}thisisamassSMS.',
        })

        cls.partner_numbers=[
            phone_validation.phone_format(partner.mobile,partner.country_id.code,partner.country_id.phone_code,force_format='E164')
            forpartnerinpartners
        ]

        cls.mailing=cls.env['mailing.mailing'].with_user(cls.user_marketing).create({
            'name':'XmasSpam',
            'subject':'XmasSpam',
            'mailing_model_id':cls.env['ir.model']._get('mail.test.sms').id,
            'mailing_type':'sms',
            'mailing_domain':'%s'%repr([('name','ilike','MassSMSTest')]),
            'sms_template_id':cls.sms_template.id,
            'sms_allow_unsubscribe':False,
        })


@tagged('mass_mailing')
classTestMassSMSInternals(TestMassSMSCommon):

    @users('user_marketing')
    deftest_mass_sms_domain(self):
        mailing=self.env['mailing.mailing'].create({
            'name':'XmasSpam',
            'subject':'XmasSpam',
            'mailing_model_id':self.env['ir.model']._get('mail.test.sms').id,
            'mailing_type':'sms',
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[])

        mailing=self.env['mailing.mailing'].create({
            'name':'XmasSpam',
            'subject':'XmasSpam',
            'mailing_model_id':self.env['ir.model']._get('mail.test.sms.bl').id,
            'mailing_type':'sms',
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[('phone_sanitized_blacklisted','=',False)])

    @users('user_marketing')
    deftest_mass_sms_internals(self):
        withself.with_user('user_marketing'):
            mailing=self.env['mailing.mailing'].create({
                'name':'XmasSpam',
                'subject':'XmasSpam',
                'mailing_model_id':self.env['ir.model']._get('mail.test.sms').id,
                'mailing_type':'sms',
                'mailing_domain':'%s'%repr([('name','ilike','MassSMSTest')]),
                'sms_template_id':self.sms_template.id,
                'sms_allow_unsubscribe':False,
            })

            self.assertEqual(mailing.mailing_model_real,'mail.test.sms')
            self.assertEqual(mailing.medium_id,self.env.ref('mass_mailing_sms.utm_medium_sms'))
            self.assertEqual(mailing.body_plaintext,self.sms_template.body)

            remaining_res_ids=mailing._get_remaining_recipients()
            self.assertEqual(set(remaining_res_ids),set(self.records.ids))

            withself.mockSMSGateway():
                mailing.action_send_sms()

        self.assertSMSTraces(
            [{'partner':record.customer_id,
              'number':self.records_numbers[i],
              'content':'Dear%sthisisamassSMS.'%record.display_name
             }fori,recordinenumerate(self.records)],
            mailing,self.records,
        )

    deftest_mass_sms_internals_errors(self):
        #samecustomer,specificdifferentnumberonrecord->shouldbevalid
        new_record_1=self.env['mail.test.sms'].create({
            'name':'MassSMSTest_nr1',
            'customer_id':self.partners[0].id,
            'phone_nbr':'0456999999',
        })
        void_record=self.env['mail.test.sms'].create({
            'name':'MassSMSTest_void',
            'customer_id':False,
            'phone_nbr':'',
        })
        falsy_record_1=self.env['mail.test.sms'].create({
            'name':'MassSMSTest_falsy_1',
            'customer_id':False,
            'phone_nbr':'abcd',
        })
        falsy_record_2=self.env['mail.test.sms'].create({
            'name':'MassSMSTest_falsy_2',
            'customer_id':False,
            'phone_nbr':'04561122',
        })
        bl_record_1=self.env['mail.test.sms'].create({
            'name':'MassSMSTest_bl_1',
            'customer_id':False,
            'phone_nbr':'0456110011',
        })
        self.env['phone.blacklist'].create({'number':'0456110011'})
        #newcustomer,numberalreadyonrecord->shouldbeignored
        country_be_id=self.env.ref('base.be').id
        nr2_partner=self.env['res.partner'].create({
            'name':'Partner_nr2',
            'country_id':country_be_id,
            'mobile':'0456449999',
        })
        new_record_2=self.env['mail.test.sms'].create({
            'name':'MassSMSTest_nr2',
            'customer_id':nr2_partner.id,
            'phone_nbr':self.records[0].phone_nbr,
        })
        records_numbers=self.records_numbers+['+32456999999']

        withself.with_user('user_marketing'):
            withself.mockSMSGateway():
                self.mailing.action_send_sms()

        self.assertSMSTraces(
            [{'partner':record.customer_id,'number':records_numbers[i],
              'content':'Dear%sthisisamassSMS.'%record.display_name}
             fori,recordinenumerate(self.records|new_record_1)],
            self.mailing,self.records|new_record_1,
        )
        #duplicates
        self.assertSMSTraces(
            [{'partner':new_record_2.customer_id,'number':self.records_numbers[0],
              'content':'Dear%sthisisamassSMS.'%new_record_2.display_name,'state':'ignored',
              'failure_type':'sms_duplicate'}],
            self.mailing,new_record_2,
        )
        #blacklist
        self.assertSMSTraces(
            [{'partner':self.env['res.partner'],'number':phone_validation.phone_format(bl_record_1.phone_nbr,'BE','32',force_format='E164'),
              'content':'Dear%sthisisamassSMS.'%bl_record_1.display_name,'state':'ignored',
              'failure_type':'sms_blacklist'}],
            self.mailing,bl_record_1,
        )
        #missingnumber
        self.assertSMSTraces(
            [{'partner':self.env['res.partner'],'number':False,
              'content':'Dear%sthisisamassSMS.'%void_record.display_name,'state':'exception',
              'failure_type':'sms_number_missing'}],
            self.mailing,void_record,
        )
        #wrongvalues
        self.assertSMSTraces(
            [{'partner':self.env['res.partner'],'number':record.phone_nbr,
              'content':'Dear%sthisisamassSMS.'%record.display_name,'state':'bounced',
              'failure_type':'sms_number_format'}
             forrecordinfalsy_record_1+falsy_record_2],
            self.mailing,falsy_record_1+falsy_record_2,
        )

    deftest_mass_sms_internals_done_ids(self):
        withself.with_user('user_marketing'):
            withself.mockSMSGateway():
                self.mailing.action_send_sms(res_ids=self.records[:5].ids)

        traces=self.env['mailing.trace'].search([('mass_mailing_id','in',self.mailing.ids)])
        self.assertEqual(len(traces),5)
        #newtracesgenerated
        self.assertSMSTraces(
            [{'partner':record.customer_id,'number':self.records_numbers[i],
              'content':'Dear%sthisisamassSMS.'%record.display_name}
             fori,recordinenumerate(self.records[:5])],
            self.mailing,self.records[:5],
        )

        withself.with_user('user_marketing'):
            withself.mockSMSGateway():
                self.mailing.action_send_sms(res_ids=self.records.ids)

        #deleteoldtraces(fortestingpurpose:easecheckbydeletingoldones)
        traces.unlink()
        #newfailedtracesgeneratedforduplicates
        self.assertSMSTraces(
            [{'partner':record.customer_id,'number':self.records_numbers[i],
              'content':'Dear%sthisisamassSMS.'%record.display_name,'state':'ignored',
              'failure_type':'sms_duplicate'}
             fori,recordinenumerate(self.records[:5])],
            self.mailing,self.records[:5],
        )
        #newtracesgenerated
        self.assertSMSTraces(
            [{'partner':record.customer_id,'number':self.records_numbers[i+5],
              'content':'Dear%sthisisamassSMS.'%record.display_name}
             fori,recordinenumerate(self.records[5:])],
            self.mailing,self.records[5:],
        )

    @mute_logger('flectra.addons.mail.models.mail_render_mixin')
    deftest_mass_sms_test_button(self):
        mailing=self.env['mailing.mailing'].create({
            'name':'TestButton',
            'subject':'Subject${object.name}',
            'preview':'Preview${object.name}',
            'state':'draft',
            'mailing_type':'sms',
            'body_plaintext':'Hello${object.name}',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
        })
        mailing_test=self.env['mailing.sms.test'].with_user(self.user_marketing).create({
            'numbers':'+32456001122',
            'mailing_id':mailing.id,
        })

        withself.with_user('user_marketing'):
            withself.mockSMSGateway():
                mailing_test.action_send_sms()

        #Testifbadjinjainthebodyraisesanerror
        mailing.write({
            'body_plaintext':'Hello${object.name_id.id}',
        })

        withself.with_user('user_marketing'):
            withself.mock_mail_gateway(),self.assertRaises(Exception):
                mailing_test.action_send_sms()


@tagged('mass_mailing','mass_mailing_sms')
classTestMassSMS(TestMassSMSCommon):

    @users('user_marketing')
    deftest_mass_sms_links(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing.ids)
        mailing.write({
            'body_plaintext':'Dear${object.display_name}thisisamassSMSwithtwolinkshttp://www.flectrahq.com/smstestandhttp://www.flectrahq.com/smstest/${object.name}',
            'sms_template_id':False,
            'sms_force_send':True,
            'sms_allow_unsubscribe':True,
        })

        withself.mockSMSGateway():
            mailing.action_send_sms()

        self.assertSMSTraces(
            [{'partner':record.customer_id,
              'number':self.records_numbers[i],
              'state':'sent',
              'content':'Dear%sthisisamassSMSwithtwolinks'%record.display_name
             }fori,recordinenumerate(self.records)],
            mailing,self.records,
            sms_links_info=[[
                ('http://www.flectrahq.com/smstest',True,{}),
                ('http://www.flectrahq.com/smstest/%s'%record.name,True,{}),
                #unsubscribeisnotshortenedandparsedatsending
                ('unsubscribe',False,{}),
            ]forrecordinself.records],
        )

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mass_sms_partner_only(self):
        """ChecksendingSMSmarketingonmodelshavingonlyapartner_idfields
        setisworking."""
        mailing=self.env['mailing.mailing'].browse(self.mailing_sms.ids)
        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mail.test.sms.partner').id,
        })

        records=self.env['mail.test.sms.partner'].create([
            {'name':'SMSTeston%s'%partner.name,
             'customer_id':partner.id,
            }forpartnerinself.partners
        ])

        withself.mockSMSGateway():
            mailing.action_send_sms()

        self.assertEqual(len(mailing.mailing_trace_ids),10)
        self.assertSMSTraces(
            [{'partner':record.customer_id,
              'number':record.customer_id.phone_sanitized,
              'state':'sent',
              'content':'Dear%sthisisamassSMSwithtwolinks'%record.display_name
             }forrecordinrecords],
            mailing,records,
            sms_links_info=[[
                ('http://www.flectrahq.com/smstest',True,{}),
                ('http://www.flectrahq.com/smstest/%s'%record.id,True,{}),
                #unsubscribeisnotshortenedandparsedatsending
                ('unsubscribe',False,{}),
            ]forrecordinrecords],
        )

        #addanewrecord,send->sentlistshouldnotresendtraces
        new_record=self.env['mail.test.sms.partner'].create([
            {'name':'DuplicateSMSon%s'%self.partners[0].name,
             'customer_id':self.partners[0].id,
            }
        ])
        withself.mockSMSGateway():
            mailing.action_send_sms()

        self.assertEqual(len(mailing.mailing_trace_ids),11)
        self.assertSMSTraces(
            [{'partner':new_record.customer_id,
              'number':new_record.customer_id.phone_sanitized,
              'state':'sent',
              'content':'Dear%sthisisamassSMSwithtwolinks'%new_record.display_name
             }],
            mailing,new_record,
            sms_links_info=[[
                ('http://www.flectrahq.com/smstest',True,{}),
                ('http://www.flectrahq.com/smstest/%s'%new_record.id,True,{}),
                #unsubscribeisnotshortenedandparsedatsending
                ('unsubscribe',False,{}),
            ]],
        )

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mass_sms_partner_only_m2m(self):
        """ChecksendingSMSmarketingonmodelshavingonlyam2mtopartners
        iscurrentlynotsuppored."""
        mailing=self.env['mailing.mailing'].browse(self.mailing_sms.ids)
        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mail.test.sms.partner.2many').id,
        })

        records=self.env['mail.test.sms.partner.2many'].create([
            {'name':'SMSTeston%s'%partner.name,
             'customer_ids':[(4,partner.id)],
            }forpartnerinself.partners
        ])

        withself.assertRaises(exceptions.UserError),self.mockSMSGateway():
            mailing.action_send_sms()


    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mass_sms_w_opt_out(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_sms.ids)
        recipients=self._create_mailing_sms_test_records(model='mail.test.sms.bl.optout',count=5)

        #optoutrecords0and1
        (recipients[0]|recipients[1]).write({'opt_out':True})
        #blacklistrecords4
        #TDEFIXME:sudoshouldnotbenecessary
        self.env['phone.blacklist'].sudo().create({'number':recipients[4].phone_nbr})

        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mail.test.sms.bl.optout'),
            'mailing_domain':[('id','in',recipients.ids)],
        })

        withself.mockSMSGateway():
            mailing.action_send_sms()

        self.assertSMSTraces(
            [{'number':'+32456000000','state':'ignored','failure_type':'sms_blacklist'}, #TDEFIXME:shouldbeopt_out
             {'number':'+32456000101','state':'ignored','failure_type':'sms_blacklist'}, #TDEFIXME:shouldbeopt_out
             {'number':'+32456000202','state':'sent'},
             {'number':'+32456000303','state':'sent'},
             {'number':'+32456000404','state':'ignored','failure_type':'sms_blacklist'}],
            mailing,recipients
        )
        self.assertEqual(mailing.ignored,3)
