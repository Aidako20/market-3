#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectra.addons.mass_mailing.tests.commonimportMassMailCommon
fromflectra.tests.commonimportusers,Form,tagged
fromflectra.toolsimportformataddr,mute_logger


@tagged('mass_mailing')
classTestMassMailValues(MassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassMailValues,cls).setUpClass()
        cls._create_mailing_list()

    @users('user_marketing')
    deftest_mailing_body_responsive(self):
        """Testingmailmailingresponsivemailbody"""
        recipient=self.env['res.partner'].create({
            'name':'MassMailPartner',
            'email':'Customer<test.customer@example.com>',
        })
        mailing=self.env['mailing.mailing'].create({
            'name':'Test',
            'subject':'Test',
            'state':'draft',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
        })

        composer=self.env['mail.compose.message'].with_user(self.user_marketing).with_context({
            'default_composition_mode':'mass_mail',
            'default_model':'res.partner',
            'default_res_id':recipient.id,
        }).create({
            'subject':'MassMailResponsive',
            'body':'IamResponsivebody',
            'mass_mailing_id':mailing.id
        })

        mail_values=composer.get_mail_values([recipient.id])
        body_html=str(mail_values[recipient.id]['body_html'])

        self.assertIn('<!DOCTYPEhtml>',body_html)
        self.assertIn('<head>',body_html)
        self.assertIn('viewport',body_html)
        self.assertIn('@media',body_html)
        self.assertIn('IamResponsivebody',body_html)

    @users('user_marketing')
    deftest_mailing_computed_fields(self):
        #Createonres.partner,withdefaultvaluesforcomputedfields
        mailing=self.env['mailing.mailing'].create({
            'name':'TestMailing',
            'subject':'Test',
            'mailing_type':'mail',
            'body_html':'<p>Hello${object.name}</p>',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
        })
        self.assertEqual(mailing.user_id,self.user_marketing)
        self.assertEqual(mailing.medium_id,self.env.ref('utm.utm_medium_email'))
        self.assertEqual(mailing.mailing_model_name,'res.partner')
        self.assertEqual(mailing.mailing_model_real,'res.partner')
        self.assertEqual(mailing.reply_to_mode,'email')
        self.assertEqual(mailing.reply_to,self.user_marketing.email_formatted)
        #defaultforpartner:removeblacklisted
        self.assertEqual(literal_eval(mailing.mailing_domain),[('is_blacklisted','=',False)])
        #updatedomain
        mailing.write({
            'mailing_domain':[('email','ilike','test.example.com')]
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[('email','ilike','test.example.com')])

        #resetmailingmodel->resetdomain;setreply_to->keepit
        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mailing.list').id,
            'reply_to':self.email_reply_to,
        })
        self.assertEqual(mailing.mailing_model_name,'mailing.list')
        self.assertEqual(mailing.mailing_model_real,'mailing.contact')
        self.assertEqual(mailing.reply_to_mode,'email')
        self.assertEqual(mailing.reply_to,self.email_reply_to)
        #defaultformailinglist:dependsuponcontact_list_ids
        self.assertEqual(literal_eval(mailing.mailing_domain),[])
        mailing.write({
            'contact_list_ids':[(4,self.mailing_list_1.id),(4,self.mailing_list_2.id)]
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[('list_ids','in',(self.mailing_list_1|self.mailing_list_2).ids)])

        #resetmailingmodel->resetdomainandreplytomode
        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mail.channel').id,
        })
        self.assertEqual(mailing.mailing_model_name,'mail.channel')
        self.assertEqual(mailing.mailing_model_real,'mail.channel')
        self.assertEqual(mailing.reply_to_mode,'thread')
        self.assertFalse(mailing.reply_to)

    @users('user_marketing')
    deftest_mailing_computed_fields_default(self):
        mailing=self.env['mailing.mailing'].with_context(
            default_mailing_domain=repr([('email','ilike','test.example.com')])
        ).create({
            'name':'TestMailing',
            'subject':'Test',
            'mailing_type':'mail',
            'body_html':'<p>Hello${object.name}</p>',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[('email','ilike','test.example.com')])

    @users('user_marketing')
    deftest_mailing_computed_fields_form(self):
        mailing_form=Form(self.env['mailing.mailing'].with_context(
            default_mailing_domain="[('email','ilike','test.example.com')]",
            default_mailing_model_id=self.env['ir.model']._get('res.partner').id,
        ))
        self.assertEqual(
            literal_eval(mailing_form.mailing_domain),
            [('email','ilike','test.example.com')],
        )
        self.assertEqual(mailing_form.mailing_model_real,'res.partner')


@tagged('mass_mailing')
classTestMassMailFeatures(MassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassMailFeatures,cls).setUpClass()
        cls._create_mailing_list()

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_channel_blacklisted_recipients(self):
        """Postingamessageonachannelshouldsendoneemailtoallrecipients,excepttheblacklistedones"""
        def_join_channel(channel,partners):
            forpartnerinpartners:
                channel.write({'channel_last_seen_partner_ids':[(0,0,{'partner_id':partner.id})]})
            channel.invalidate_cache()

        test_channel=self.env['mail.channel'].create({
            'name':'Test',
            'description':'Description',
            'alias_name':'test',
            'public':'public',
            'email_send':True,
        })
        test_partner=self.env['res.partner'].create({
            'name':'TestPartner',
            'email':'test@example.com',
        })

        blacklisted_partner=self.env['res.partner'].create({
            'name':'BlacklistedPartner',
            'email':'test@black.list',
        })

        #SetBlacklist
        self.env['mail.blacklist'].create({
            'email':'test@black.list',
        })

        _join_channel(test_channel,test_partner)
        _join_channel(test_channel,blacklisted_partner)
        withself.mock_mail_gateway():
            test_channel.message_post(body="Test",message_type='comment',subtype_xmlid='mail.mt_comment')

        self.assertEqual(len(self._mails),1,'Numberofmailincorrect.Shouldbeequalto1.')
        foremailinself._mails:
            self.assertEqual(
                set(email['email_to']),
                set([formataddr((test_partner.name,test_partner.email))]),
                'email_toincorrect.Shouldbeequalto"%s"'%(
                    formataddr((test_partner.name,test_partner.email))))

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_deletion(self):
        """Testdeletioninvarioususecase,dependingonreply-to"""
        #1-Keeparchivesandreply-tosetto'answer=newthread'
        mailing=self.env['mailing.mailing'].create({
            'name':'TestSource',
            'subject':'TestDeletion',
            'body_html':"<div>Hello{object.name}</div>",
            'mailing_model_id':self.env['ir.model']._get('mailing.list').id,
            'contact_list_ids':[(6,0,self.mailing_list_1.ids)],
            'keep_archives':True,
            'reply_to_mode':'email',
            'reply_to':self.email_reply_to,
        })
        self.assertEqual(self.mailing_list_1.contact_ids.message_ids,self.env['mail.message'])

        withself.mock_mail_gateway(mail_unlink_sent=True):
            mailing.action_send_mail()

        self.assertEqual(len(self._mails),3)
        self.assertEqual(len(self._new_mails.exists()),3)
        self.assertEqual(len(self.mailing_list_1.contact_ids.message_ids),3)

        #2-Keeparchivesandreply-tosetto'answer=updatethread'
        self.mailing_list_1.contact_ids.message_ids.unlink()
        mailing=mailing.copy()
        mailing.write({
            'reply_to_mode':'thread',
        })
        self.assertEqual(self.mailing_list_1.contact_ids.message_ids,self.env['mail.message'])

        withself.mock_mail_gateway(mail_unlink_sent=True):
            mailing.action_send_mail()

        self.assertEqual(len(self._mails),3)
        self.assertEqual(len(self._new_mails.exists()),3)
        self.assertEqual(len(self.mailing_list_1.contact_ids.message_ids),3)

        #3-Removearchivesandreply-tosetto'answer=newthread'
        self.mailing_list_1.contact_ids.message_ids.unlink()
        mailing=mailing.copy()
        mailing.write({
            'keep_archives':False,
            'reply_to_mode':'email',
            'reply_to':self.email_reply_to,
        })
        self.assertEqual(self.mailing_list_1.contact_ids.message_ids,self.env['mail.message'])

        withself.mock_mail_gateway(mail_unlink_sent=True):
            mailing.action_send_mail()

        self.assertEqual(len(self._mails),3)
        self.assertEqual(len(self._new_mails.exists()),0)
        self.assertEqual(self.mailing_list_1.contact_ids.message_ids,self.env['mail.message'])

        #4-Removearchivesandreply-tosetto'answer=updatethread'
        #Implykeepingmail.messageforgatewayreply)
        self.mailing_list_1.contact_ids.message_ids.unlink()
        mailing=mailing.copy()
        mailing.write({
            'keep_archives':False,
            'reply_to_mode':'thread',
        })
        self.assertEqual(self.mailing_list_1.contact_ids.message_ids,self.env['mail.message'])

        withself.mock_mail_gateway(mail_unlink_sent=True):
            mailing.action_send_mail()

        self.assertEqual(len(self._mails),3)
        self.assertEqual(len(self._new_mails.exists()),0)
        self.assertEqual(len(self.mailing_list_1.contact_ids.message_ids),3)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_on_res_partner(self):
        """Testmailingonres.partnermodel:ensuredefaultrecipientsare
        correctlycomputed"""
        partner_a=self.env['res.partner'].create({
            'name':'testemail1',
            'email':'test1@example.com',
        })
        partner_b=self.env['res.partner'].create({
            'name':'testemail2',
            'email':'test2@example.com',
        })
        self.env['mail.blacklist'].create({'email':'Test2@example.com',})

        mailing=self.env['mailing.mailing'].create({
            'name':'One',
            'subject':'One',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
            'mailing_domain':[('id','in',(partner_a|partner_b).ids)],
            'body_html':'Thisismassmailmarketingdemo'
        })
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'partner':partner_a},
             {'partner':partner_b,'state':'ignored','failure_type':False}],
            mailing,partner_a+partner_b,check_mail=True
        )

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_shortener(self):
        mailing=self.env['mailing.mailing'].create({
            'name':'TestSource',
            'subject':'TestShortener',
            'body_html':"""<div>
Hi,
%seturl="www.flectrahq.com"
%sethttpurl="https://www.flectra.eu"
Website0:<aid="url0"href="https://www.flectra.tz/my/${object.name}">https://www.flectra.tz/my/${object.name}</a>
Website1:<aid="url1"href="https://www.flectra.be">https://www.flectra.be</a>
Website2:<aid="url2"href="https://${url}">https://${url}</a>
Website3:<aid="url3"href="${httpurl}">${httpurl}</a>
External1:<aid="url4"href="https://www.example.com/foo/bar?baz=qux">Youpie</a>
Email:<aid="url5"href="mailto:test@flectrahq.com">test@flectrahq.com</a></div>""",
            'mailing_model_id':self.env['ir.model']._get('mailing.list').id,
            'reply_to_mode':'email',
            'reply_to':self.email_reply_to,
            'contact_list_ids':[(6,0,self.mailing_list_1.ids)],
            'keep_archives':True,
        })

        mailing.action_put_in_queue()

        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'email':'fleurus@example.com'},
             {'email':'gorramts@example.com'},
             {'email':'ybrant@example.com'}],
            mailing,self.mailing_list_1.contact_ids,check_mail=True
        )

        forcontactinself.mailing_list_1.contact_ids:
            new_mail=self._find_mail_mail_wrecord(contact)
            forlink_infoin[('url0','https://www.flectra.tz/my/%s'%contact.name,True),
                              ('url1','https://www.flectra.be',True),
                              ('url2','https://www.flectrahq.com',True),
                              ('url3','https://www.flectra.eu',True),
                              ('url4','https://www.example.com/foo/bar?baz=qux',True),
                              ('url5','mailto:test@flectrahq.com',False)]:
                #TDEFIXME:whygoingtomailmessageid?mail.body_htmlseemstofail,check
                link_params={'utm_medium':'Email','utm_source':mailing.name}
                iflink_info[0]=='url4':
                    link_params['baz']='qux'
                self.assertLinkShortenedHtml(
                    new_mail.mail_message_id.body,
                    link_info,
                    link_params=link_params,
                )
