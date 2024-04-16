#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectra.addons.test_mass_mailing.testsimportcommon
fromflectra.tests.commonimportusers
fromflectra.addons.mass_mailing.models.mail_threadimportBLACKLIST_MAX_BOUNCED_LIMIT


classTestAutoBlacklist(common.TestMassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestAutoBlacklist,cls).setUpClass()
        cls.target_rec=cls._create_mailing_test_records()[0]
        cls.mailing_bl.write({'mailing_domain':[('id','in',cls.target_rec.ids)]})

    @users('user_marketing')
    deftest_mailing_bounce_w_auto_bl(self):
        self._test_mailing_bounce_w_auto_bl(None)

    @users('user_marketing')
    deftest_mailing_bounce_w_auto_bl_partner(self):
        bounced_partner=self.env['res.partner'].sudo().create({
            'name':'BouncedPartner',
            'email':self.target_rec.email_from,
            'message_bounce':BLACKLIST_MAX_BOUNCED_LIMIT,
        })
        self._test_mailing_bounce_w_auto_bl({'bounced_partner':bounced_partner})

    @users('user_marketing')
    deftest_mailing_bounce_w_auto_bl_partner_duplicates(self):
        bounced_partners=self.env['res.partner'].sudo().create({
            'name':'BouncedPartner1',
            'email':self.target_rec.email_from,
            'message_bounce':BLACKLIST_MAX_BOUNCED_LIMIT,
        })|self.env['res.partner'].sudo().create({
            'name':'BouncedPartner2',
            'email':self.target_rec.email_from,
            'message_bounce':BLACKLIST_MAX_BOUNCED_LIMIT,
        })
        self._test_mailing_bounce_w_auto_bl({'bounced_partner':bounced_partners})

    def_test_mailing_bounce_w_auto_bl(self,bounce_base_values):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)
        target=self.env['mailing.test.blacklist'].browse(self.target_rec.ids)

        #createbouncedhistoryof4statistics
        foridxinrange(4):
            new_mailing=mailing.copy()
            self._create_bounce_trace(new_mailing,target,dt=datetime.datetime.now()-datetime.timedelta(weeks=idx+2))
            self.gateway_mail_bounce(new_mailing,target,bounce_base_values)

        #massmailrecord:ok,notblacklistedyet
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'email':'test.record.00@test.example.com'}],
            mailing,target,
            check_mail=True
        )

        #callbounced
        self.gateway_mail_bounce(mailing,target,bounce_base_values)

        #checkblacklist
        blacklist_record=self.env['mail.blacklist'].sudo().search([('email','=',target.email_normalized)])
        self.assertEqual(len(blacklist_record),1)
        self.assertTrue(target.is_blacklisted)

        #massmailrecord:ko,blacklisted
        new_mailing=mailing.copy()
        new_mailing.write({'mailing_domain':[('id','in',target.ids)]})
        new_mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            new_mailing._process_mass_mailing_queue()
        self.assertMailTraces(
            [{'email':'test.record.00@test.example.com','state':'ignored','failure_type':False}],
            new_mailing,target,check_mail=True
        )
