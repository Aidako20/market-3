#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sms.testsimportcommonassms_common
fromflectra.addons.test_mail.tests.test_performanceimportBaseMailPerformance
fromflectra.tests.commonimportusers,warmup
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


@tagged('mail_performance','post_install','-at_install')
classTestSMSPerformance(BaseMailPerformance,sms_common.SMSCase):

    defsetUp(self):
        super(TestSMSPerformance,self).setUp()
        self.user_employee.write({
            'login':'employee',
            'country_id':self.env.ref('base.be').id,
        })
        self.admin=self.env.user

        self.customer=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'TestCustomer',
            'email':'test@example.com',
            'mobile':'0456123456',
            'country_id':self.env.ref('base.be').id,
        })
        self.test_record=self.env['mail.test.sms'].with_context(self._quick_create_ctx).create({
            'name':'Test',
            'customer_id':self.customer.id,
            'phone_nbr':'0456999999',
        })

        #preparerecipientstotestformorerealisticworkload
        Partners=self.env['res.partner'].with_context(self._quick_create_ctx)
        self.partners=self.env['res.partner']
        forxinrange(0,10):
            self.partners|=Partners.create({
                'name':'Test%s'%x,
                'email':'test%s@example.com'%x,
                'mobile':'0456%s%s0000'%(x,x),
                'country_id':self.env.ref('base.be').id,
            })

        self._init_mail_gateway()

        #patchregistrytosimulateareadyenvironment
        self.patch(self.env.registry,'ready',True)

    @mute_logger('flectra.addons.sms.models.sms_sms')
    @users('employee')
    @warmup
    deftest_message_sms_record_1_partner(self):
        record=self.test_record.with_user(self.env.user)
        pids=self.customer.ids
        withself.mockSMSGateway(sms_allow_unlink=True),self.assertQueryCount(employee=25): #test_mail_enterprise:25
            messages=record._message_sms(
                body='PerformanceTest',
                partner_ids=pids,
            )

        self.assertEqual(record.message_ids[0].body,'<p>PerformanceTest</p>')
        self.assertSMSNotification([{'partner':self.customer}],'PerformanceTest',messages,sent_unlink=True)

    @mute_logger('flectra.addons.sms.models.sms_sms')
    @users('employee')
    @warmup
    deftest_message_sms_record_10_partners(self):
        record=self.test_record.with_user(self.env.user)
        pids=self.partners.ids
        withself.mockSMSGateway(sms_allow_unlink=True),self.assertQueryCount(employee=43):
            messages=record._message_sms(
                body='PerformanceTest',
                partner_ids=pids,
            )

        self.assertEqual(record.message_ids[0].body,'<p>PerformanceTest</p>')
        self.assertSMSNotification([{'partner':partner}forpartnerinself.partners],'PerformanceTest',messages,sent_unlink=True)

    @mute_logger('flectra.addons.sms.models.sms_sms')
    @users('employee')
    @warmup
    deftest_message_sms_record_default(self):
        record=self.test_record.with_user(self.env.user)
        withself.mockSMSGateway(sms_allow_unlink=True),self.assertQueryCount(employee=27):
            messages=record._message_sms(
                body='PerformanceTest',
            )

        self.assertEqual(record.message_ids[0].body,'<p>PerformanceTest</p>')
        self.assertSMSNotification([{'partner':self.customer}],'PerformanceTest',messages,sent_unlink=True)


@tagged('mail_performance','post_install','-at_install')
classTestSMSMassPerformance(BaseMailPerformance,sms_common.MockSMS):

    defsetUp(self):
        super(TestSMSMassPerformance,self).setUp()
        be_country_id=self.env.ref('base.be').id,
        self.user_employee.write({
            'login':'employee',
            'country_id':be_country_id,
        })
        self.admin=self.env.user
        self.admin.write({
            'country_id':be_country_id,
        })

        self._test_body='MASSSMS'

        records=self.env['mail.test.sms']
        partners=self.env['res.partner']
        forxinrange(50):
            partners+=self.env['res.partner'].with_context(**self._quick_create_ctx).create({
                'name':'Partner_%s'%(x),
                'email':'_test_partner_%s@example.com'%(x),
                'country_id':be_country_id,
                'mobile':'047500%02d%02d'%(x,x)
            })
            records+=self.env['mail.test.sms'].with_context(**self._quick_create_ctx).create({
                'name':'Test_%s'%(x),
                'customer_id':partners[x].id,
            })
        self.partners=partners
        self.records=records

        self.sms_template=self.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':self.env['ir.model']._get('mail.test.sms').id,
            'body':'Dear${object.display_name}thisisanSMS.',
        })

    @mute_logger('flectra.addons.sms.models.sms_sms')
    @users('employee')
    @warmup
    deftest_composer_mass_active_domain(self):
        composer=self.env['sms.composer'].with_context(
            default_composition_mode='mass',
            default_res_model='mail.test.sms',
            default_use_active_domain=True,
            active_domain=[('id','in',self.records.ids)],
        ).create({
            'body':self._test_body,
            'mass_keep_log':False,
        })

        withself.mockSMSGateway(sms_allow_unlink=True),self.assertQueryCount(employee=106):
            composer.action_send_sms()

    @mute_logger('flectra.addons.sms.models.sms_sms')
    @users('employee')
    @warmup
    deftest_composer_mass_active_domain_w_log(self):
        composer=self.env['sms.composer'].with_context(
            default_composition_mode='mass',
            default_res_model='mail.test.sms',
            default_use_active_domain=True,
            active_domain=[('id','in',self.records.ids)],
        ).create({
            'body':self._test_body,
            'mass_keep_log':True,
        })

        withself.mockSMSGateway(sms_allow_unlink=True),self.assertQueryCount(employee=157):
            composer.action_send_sms()
