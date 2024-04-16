#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.tests.commonimportTransactionCase,users,warmup
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


@tagged('mail_performance','post_install','-at_install')
classTestMassMailPerformanceBase(TransactionCase):

    defsetUp(self):
        super(TestMassMailPerformanceBase,self).setUp()

        self.user_employee=mail_new_test_user(
            self.env,login='emp',
            groups='base.group_user',
            name='ErnestEmployee',notification_type='inbox')

        self.user_marketing=mail_new_test_user(
            self.env,login='marketing',
            groups='base.group_user,mass_mailing.group_mass_mailing_user',
            name='MartialMarketing',signature='--\nMartial')

        #setupmailgateway
        self.alias_domain='example.com'
        self.alias_catchall='catchall.test'
        self.alias_bounce='bounce.test'
        self.default_from='notifications'
        self.env['ir.config_parameter'].set_param('mail.bounce.alias',self.alias_bounce)
        self.env['ir.config_parameter'].set_param('mail.catchall.domain',self.alias_domain)
        self.env['ir.config_parameter'].set_param('mail.catchall.alias',self.alias_catchall)
        self.env['ir.config_parameter'].set_param('mail.default.from',self.default_from)

        #patchregistrytosimulateareadyenvironment
        self.patch(self.env.registry,'ready',True)


@tagged('mail_performance','post_install','-at_install')
classTestMassMailPerformance(TestMassMailPerformanceBase):

    defsetUp(self):
        super(TestMassMailPerformance,self).setUp()
        values=[{
            'name':'Recipient%s'%x,
            'email_from':'Recipient<rec.%s@example.com>'%x,
        }forxinrange(0,50)]
        self.mm_recs=self.env['mailing.performance'].create(values)

    @users('__system__','marketing')
    @warmup
    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink','flectra.tests')
    deftest_send_mailing(self):
        mailing=self.env['mailing.mailing'].create({
            'name':'Test',
            'subject':'Test',
            'body_html':'<p>Hello<arole="button"href="https://www.example.com/foo/bar?baz=qux">quux</a><arole="button"href="/unsubscribe_from_list">Unsubscribe</a></p>',
            'reply_to_mode':'email',
            'mailing_model_id':self.ref('test_mass_mailing.model_mailing_performance'),
            'mailing_domain':[('id','in',self.mm_recs.ids)],
        })

        #runbotneeds+52comparedtolocal
        withself.assertQueryCount(__system__=1718,marketing=1720): #tmm1666/1668
            mailing.action_send_mail()

        self.assertEqual(mailing.sent,50)
        self.assertEqual(mailing.delivered,50)


@tagged('mail_performance','post_install','-at_install')
classTestMassMailBlPerformance(TestMassMailPerformanceBase):

    defsetUp(self):
        """Inthissetupweprepare20blacklistentries.Wethereforeadd
        20recipientscomparedtofirsttestinordertohavecomparableresults."""
        super(TestMassMailBlPerformance,self).setUp()
        values=[{
            'name':'Recipient%s'%x,
            'email_from':'Recipient<rec.%s@example.com>'%x,
        }forxinrange(0,62)]
        self.mm_recs=self.env['mailing.performance.blacklist'].create(values)

        forxinrange(1,13):
            self.env['mail.blacklist'].create({
                'email':'rec.%s@example.com'%(x*5)
            })
        self.env['mailing.performance.blacklist'].flush()

    @users('__system__','marketing')
    @warmup
    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink','flectra.tests')
    deftest_send_mailing_w_bl(self):
        mailing=self.env['mailing.mailing'].create({
            'name':'Test',
            'subject':'Test',
            'body_html':'<p>Hello<arole="button"href="https://www.example.com/foo/bar?baz=qux">quux</a><arole="button"href="/unsubscribe_from_list">Unsubscribe</a></p>',
            'reply_to_mode':'email',
            'mailing_model_id':self.ref('test_mass_mailing.model_mailing_performance_blacklist'),
            'mailing_domain':[('id','in',self.mm_recs.ids)],
        })

        #runbotneeds+64comparedtolocal(sometimes+1forsystem)
        withself.assertQueryCount(__system__=1997,marketing=1998): #tmm1932/1934-com+ent1996/1998
            mailing.action_send_mail()

        self.assertEqual(mailing.sent,50)
        self.assertEqual(mailing.delivered,50)
