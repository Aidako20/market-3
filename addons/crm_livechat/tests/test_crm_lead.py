#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.crm.tests.commonimportTestCrmCommon
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.tests.commonimportusers


classTestLivechatLead(TestCrmCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestLivechatLead,cls).setUpClass()

        cls.user_anonymous=mail_new_test_user(
            cls.env,login='user_anonymous',
            name='AnonymousWebsite',email=False,
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='base.group_public',
        )
        cls.user_portal=mail_new_test_user(
            cls.env,login='user_portal',
            name='PaulettePortal',email='user_portal@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='base.group_portal',
        )

    @users('user_sales_leads')
    deftest_crm_lead_creation_guest(self):
        """Testcustomersetonlead:notifpublic,guestifnotpublic"""
        #public:shouldnotbesetascustomer
        channel=self.env['mail.channel'].create({
            'name':'ChatwithVisitor',
            'channel_partner_ids':[(4,self.user_anonymous.partner_id.id)]
        })
        lead=channel._convert_visitor_to_lead(self.env.user.partner_id,channel.channel_last_seen_partner_ids,'/leadTestLeadcommand')

        self.assertEqual(
            channel.channel_last_seen_partner_ids.partner_id,
            self.user_sales_leads.partner_id|self.user_anonymous.partner_id
        )
        self.assertEqual(lead.name,'TestLeadcommand')
        self.assertEqual(lead.partner_id,self.env['res.partner'])

        #publicuser:shouldnotbesetascustomer
        #'base.public_user'isarchivedbydefault
        self.assertFalse(self.env.ref('base.public_user').active)

        channel=self.env['mail.channel'].create({
            'name':'ChatwithVisitor',
            'channel_partner_ids':[(4,self.env.ref('base.public_partner').id)]
        })
        lead=channel._convert_visitor_to_lead(self.env.user.partner_id,channel.channel_last_seen_partner_ids,'/leadTestLeadcommand')

        self.assertEqual(
            channel.channel_last_seen_partner_ids.partner_id,
            self.user_sales_leads.partner_id|self.env.ref('base.public_partner')
        )
        self.assertEqual(lead.name,'TestLeadcommand')
        self.assertEqual(lead.partner_id,self.env['res.partner'])

        #public+someoneelse:nocustomer(ashewasanonymous)
        channel.write({
            'channel_partner_ids':[(4,self.user_sales_manager.partner_id.id)]
        })
        lead=channel._convert_visitor_to_lead(self.env.user.partner_id,channel.channel_last_seen_partner_ids,'/leadTestLeadcommand')
        self.assertEqual(lead.partner_id,self.env['res.partner'])

        #portal:shouldbesetascustomer
        channel=self.env['mail.channel'].create({
            'name':'ChatwithVisitor',
            'channel_partner_ids':[(4,self.user_portal.partner_id.id)]
        })
        lead=channel._convert_visitor_to_lead(self.env.user.partner_id,channel.channel_last_seen_partner_ids,'/leadTestLeadcommand')

        self.assertEqual(
            channel.channel_last_seen_partner_ids.partner_id,
            self.user_sales_leads.partner_id|self.user_portal.partner_id
        )
        self.assertEqual(lead.partner_id,self.user_portal.partner_id)

        #anotheroperatorinvited:internalusershouldnotbecustomerifportalispresent
        channel.write({
            'channel_partner_ids':[(4,self.user_sales_manager.partner_id.id)]
        })
        lead=channel._convert_visitor_to_lead(self.env.user.partner_id,channel.channel_last_seen_partner_ids,'/leadTestLeadcommand')

        self.assertEqual(
            channel.channel_last_seen_partner_ids.partner_id,
            self.user_sales_leads.partner_id|self.user_portal.partner_id|self.user_sales_manager.partner_id
        )
        self.assertEqual(lead.partner_id,self.user_portal.partner_id)
