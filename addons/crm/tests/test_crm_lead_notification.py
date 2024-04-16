#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittestimportskip

fromflectra.addons.crm.tests.commonimportTestCrmCommon
fromflectra.testsimporttagged,users
fromflectra.toolsimportmute_logger


@tagged('mail_thread','mail_gateway')
classNewLeadNotification(TestCrmCommon):

    @users('user_sales_manager')
    @skip('Waituntiltest_predictive_lead_scoringissueisfixed')
    deftest_lead_message_get_suggested_recipient(self):
        """Test'_message_get_suggested_recipients'anditsoverrideinlead."""
        lead_format,lead_multi,lead_from,lead_partner=self.env['crm.lead'].create([
            {
                'email_from':'"NewCustomer"<new.customer.format@test.example.com>',
                'name':'TestSuggestion(email_fromwithformat)',
                'partner_name':'FormatName',
                'user_id':self.user_sales_leads.id,
            },{
                'email_from':'new.customer.multi.1@test.example.com,new.customer.2@test.example.com',
                'name':'TestSuggestion(email_frommulti)',
                'partner_name':'MultiName',
                'user_id':self.user_sales_leads.id,
            },{
                'email_from':'new.customer.simple@test.example.com',
                'name':'TestSuggestion(email_from)',
                'partner_name':'StdName',
                'user_id':self.user_sales_leads.id,
            },{
                'name':'TestSuggestion(partner_id)',
                'partner_id':self.contact_1.id,
                'user_id':self.user_sales_leads.id,
            }
        ])
        forlead,expected_suggestedinzip(
            lead_format+lead_multi+lead_from+lead_partner,
            [(False,'"NewCustomer"<new.customer.format@test.example.com>','CustomerEmail'),
             (False,'"MultiName"<new.customer.multi.1@test.example.com,new.customer.2@test.example.com>','CustomerEmail'),
             (False,'"StdName"<new.customer.simple@test.example.com>','CustomerEmail'),
             (self.contact_1.id,'"PhilipJFry"<philip.j.fry@test.example.com>','Customer'),
            ]
        ):
            withself.subTest(lead=lead,email_from=lead.email_from):
                res=lead._message_get_suggested_recipients()[lead.id]
                self.assertEqual(len(res),1)
                self.assertEqual(res[0],expected_suggested)

    deftest_new_lead_notification(self):
        """Testnewlycreateleadslikefromthewebsite.Peopleandchannels
        subscribedtotheSalesTeamshoudbenotified."""
        #subscribeapartnerandachanneltotheSalesTeamwithnewleadsubtype
        channel_listen=self.env['mail.channel'].create({'name':'Listener'})
        sales_team_1=self.env['crm.team'].create({
            'name':'TestSalesTeam',
            'alias_name':'test_sales_team',
        })

        subtype=self.env.ref("crm.mt_salesteam_lead")
        sales_team_1.message_subscribe(partner_ids=[self.user_sales_manager.partner_id.id],channel_ids=[channel_listen.id],subtype_ids=[subtype.id])

        #Imitatewhathappensinthecontrollerwhensomebodycreatesanew
        #leadfromthewebsiteform
        lead=self.env["crm.lead"].with_context(mail_create_nosubscribe=True).sudo().create({
            "contact_name":"Somebody",
            "description":"Somequestion",
            "email_from":"somemail@example.com",
            "name":"Somesubject",
            "partner_name":"Somecompany",
            "team_id":sales_team_1.id,
            "phone":"+0000000000"
        })
        #partnerandchannelshouldbeautosubscribed
        self.assertIn(self.user_sales_manager.partner_id,lead.message_partner_ids)
        self.assertIn(channel_listen,lead.message_channel_ids)

        msg=lead.message_ids[0]
        self.assertIn(self.user_sales_manager.partner_id,msg.notified_partner_ids)
        self.assertIn(channel_listen,msg.channel_ids)

        #Theusershouldhaveanewunreadmessage
        lead_user=lead.with_user(self.user_sales_manager)
        self.assertTrue(lead_user.message_needaction)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_new_lead_from_email_multicompany(self):
        company0=self.env.company
        company1=self.env['res.company'].create({'name':'new_company'})

        self.env.user.write({
            'company_ids':[(4,company0.id,False),(4,company1.id,False)],
        })

        crm_team_model=self.env['ir.model'].search([('model','=','crm.team')])
        crm_lead_model=self.env['ir.model'].search([('model','=','crm.lead')])
        self.env["ir.config_parameter"].sudo().set_param("mail.catchall.domain",'aqualung.com')

        crm_team0=self.env['crm.team'].create({
            'name':'crmteam0',
            'company_id':company0.id,
        })
        crm_team1=self.env['crm.team'].create({
            'name':'crmteam1',
            'company_id':company1.id,
        })

        mail_alias0=self.env['mail.alias'].create({
            'alias_name':'sale_team_0',
            'alias_model_id':crm_lead_model.id,
            'alias_parent_model_id':crm_team_model.id,
            'alias_parent_thread_id':crm_team0.id,
            'alias_defaults':"{'type':'opportunity','team_id':%s}"%crm_team0.id,
        })
        mail_alias1=self.env['mail.alias'].create({
            'alias_name':'sale_team_1',
            'alias_model_id':crm_lead_model.id,
            'alias_parent_model_id':crm_team_model.id,
            'alias_parent_thread_id':crm_team1.id,
            'alias_defaults':"{'type':'opportunity','team_id':%s}"%crm_team1.id,
        })

        crm_team0.write({'alias_id':mail_alias0.id})
        crm_team1.write({'alias_id':mail_alias1.id})

        new_message0="""MIME-Version:1.0
Date:Thu,27Dec201816:27:45+0100
Message-ID:<blablabla0>
Subject:saleteam0incompany0
From: Aclient<client_a@someprovider.com>
To:sale_team_0@aqualung.com
Content-Type:multipart/alternative;boundary="000000000000a47519057e029630"

--000000000000a47519057e029630
Content-Type:text/plain;charset="UTF-8"


--000000000000a47519057e029630
Content-Type:text/html;charset="UTF-8"
Content-Transfer-Encoding:quoted-printable

<div>Agoodmessage</div>

--000000000000a47519057e029630--
"""

        new_message1="""MIME-Version:1.0
Date:Thu,27Dec201816:27:45+0100
Message-ID:<blablabla1>
Subject:saleteam1incompany1
From: Bclient<client_b@someprovider.com>
To:sale_team_1@aqualung.com
Content-Type:multipart/alternative;boundary="000000000000a47519057e029630"

--000000000000a47519057e029630
Content-Type:text/plain;charset="UTF-8"


--000000000000a47519057e029630
Content-Type:text/html;charset="UTF-8"
Content-Transfer-Encoding:quoted-printable

<div>Agoodmessagebis</div>

--000000000000a47519057e029630--
"""
        crm_lead0_id=self.env['mail.thread'].message_process('crm.lead',new_message0)
        crm_lead1_id=self.env['mail.thread'].message_process('crm.lead',new_message1)

        crm_lead0=self.env['crm.lead'].browse(crm_lead0_id)
        crm_lead1=self.env['crm.lead'].browse(crm_lead1_id)

        self.assertEqual(crm_lead0.team_id,crm_team0)
        self.assertEqual(crm_lead1.team_id,crm_team1)

        self.assertEqual(crm_lead0.company_id,company0)
        self.assertEqual(crm_lead1.company_id,company1)
