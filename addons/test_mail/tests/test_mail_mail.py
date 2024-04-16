#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importpsycopg2

fromflectraimportapi,tools
fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.testsimportcommon,tagged
fromflectra.toolsimportmute_logger


@tagged('mail_mail')
classTestMailMail(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailMail,cls).setUpClass()
        cls._init_mail_gateway()

        cls.test_record=cls.env['mail.test.gateway'].with_context(cls._test_context).create({
            'name':'Test',
            'email_from':'ignasse@example.com',
        }).with_context({})

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_mail_notify_from_mail_mail(self):
        #Dueotpost-commithooks,storesendemailsineverystep
        mail=self.env['mail.mail'].sudo().create({
            'body_html':'<p>Test</p>',
            'email_to':'test@example.com',
            'partner_ids':[(4,self.user_employee.partner_id.id)]
        })
        withself.mock_mail_gateway():
            mail.send()
        self.assertSentEmail(mail.env.user.partner_id,['test@example.com'])
        self.assertEqual(len(self._mails),1)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_mail_return_path(self):
        #mailwithoutthread-enabledrecord
        base_values={
            'body_html':'<p>Test</p>',
            'email_to':'test@example.com',
        }

        mail=self.env['mail.mail'].create(base_values)
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(self._mails[0]['headers']['Return-Path'],'%s+%d@%s'%(self.alias_bounce,mail.id,self.alias_domain))

        #mailonthread-enabledrecord
        mail=self.env['mail.mail'].create(dict(base_values,**{
            'model':self.test_record._name,
            'res_id':self.test_record.id,
        }))
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(self._mails[0]['headers']['Return-Path'],'%s+%d-%s-%s@%s'%(self.alias_bounce,mail.id,self.test_record._name,self.test_record.id,self.alias_domain))

        #forcestaticaddressingonbouncealias
        self.env['ir.config_parameter'].set_param('mail.bounce.alias.static',True)

        #mailwithoutthread-enabledrecord
        mail=self.env['mail.mail'].create(base_values)
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(self._mails[0]['headers']['Return-Path'],'%s@%s'%(self.alias_bounce,self.alias_domain))

        #mailonthread-enabledrecord
        mail=self.env['mail.mail'].create(dict(base_values,**{
            'model':self.test_record._name,
            'res_id':self.test_record.id,
        }))
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(self._mails[0]['headers']['Return-Path'],'%s@%s'%(self.alias_bounce,self.alias_domain))

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_mail_values_email_formatted(self):
        """Testoutgoingemailvalues,withformatting"""
        customer=self.env['res.partner'].create({
            'name':'TonyCustomer',
            'email':'"FormattedEmails"<tony.customer@test.example.com>',
        })
        mail=self.env['mail.mail'].create({
            'body_html':'<p>Test</p>',
            'email_cc':'"Ignasse,lePoilu"<test.cc.1@test.example.com>',
            'email_to':'"Raoul,leGrand"<test.email.1@test.example.com>,"Micheline,l\'immense"<test.email.2@test.example.com>',
            'recipient_ids':[(4,self.user_employee.partner_id.id),(4,customer.id)]
        })
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(len(self._mails),3,'Mail:sent3emails:1foremail_to,1/recipient')
        self.assertEqual(
            sorted(sorted(_mail['email_to'])for_mailinself._mails),
            sorted([sorted(['"Raoul,leGrand"<test.email.1@test.example.com>','"Micheline,l\'immense"<test.email.2@test.example.com>']),
                    [tools.formataddr((self.user_employee.name,self.user_employee.email_normalized))],
                    [tools.formataddr(("TonyCustomer",'tony.customer@test.example.com'))]
                   ]),
            'Mail:formattingissuesshouldhavebeenremovedasmuchaspossible'
        )
        #Currentlybroken:CCareaddedtoALLemails(spammy)
        self.assertEqual(
            [_mail['email_cc']for_mailinself._mails],
            [['test.cc.1@test.example.com']]*3,
            'Mail:currentlyalwaysremovingformattinginemail_cc'
        )

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_mail_values_email_multi(self):
        """Testoutgoingemailvalues,withemailfieldholdingmultiemails"""
        #Multi
        customer=self.env['res.partner'].create({
            'name':'TonyCustomer',
            'email':'tony.customer@test.example.com,norbert.customer@test.example.com',
        })
        mail=self.env['mail.mail'].create({
            'body_html':'<p>Test</p>',
            'email_cc':'test.cc.1@test.example.com,test.cc.2@test.example.com',
            'email_to':'test.email.1@test.example.com,test.email.2@test.example.com',
            'recipient_ids':[(4,self.user_employee.partner_id.id),(4,customer.id)]
        })
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(len(self._mails),3,'Mail:sent3emails:1foremail_to,1/recipient')
        self.assertEqual(
            sorted(sorted(_mail['email_to'])for_mailinself._mails),
            sorted([sorted(['test.email.1@test.example.com','test.email.2@test.example.com']),
                    [tools.formataddr((self.user_employee.name,self.user_employee.email_normalized))],
                    sorted([tools.formataddr(("TonyCustomer",'tony.customer@test.example.com')),
                            tools.formataddr(("TonyCustomer",'norbert.customer@test.example.com'))]),
                   ]),
            'Mail:formattingissuesshouldhavebeenremovedasmuchaspossible(multiemailsinasingleaddressaremanaged'
            'likeseparateemailswhensendingwithrecipient_ids'
        )
        #Currentlybroken:CCareaddedtoALLemails(spammy)
        self.assertEqual(
            [_mail['email_cc']for_mailinself._mails],
            [['test.cc.1@test.example.com','test.cc.2@test.example.com']]*3,
        )

        #Multi+formatting
        customer=self.env['res.partner'].create({
            'name':'TonyCustomer',
            'email':'tony.customer@test.example.com,"NorbertCustomer"<norbert.customer@test.example.com>',
        })
        mail=self.env['mail.mail'].create({
            'body_html':'<p>Test</p>',
            'email_cc':'test.cc.1@test.example.com,test.cc.2@test.example.com',
            'email_to':'test.email.1@test.example.com,test.email.2@test.example.com',
            'recipient_ids':[(4,self.user_employee.partner_id.id),(4,customer.id)]
        })
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(len(self._mails),3,'Mail:sent3emails:1foremail_to,1/recipient')
        self.assertEqual(
            sorted(sorted(_mail['email_to'])for_mailinself._mails),
            sorted([sorted(['test.email.1@test.example.com','test.email.2@test.example.com']),
                    [tools.formataddr((self.user_employee.name,self.user_employee.email_normalized))],
                    sorted([tools.formataddr(("TonyCustomer",'tony.customer@test.example.com')),
                            tools.formataddr(("TonyCustomer",'norbert.customer@test.example.com'))]),
                   ]),
            'Mail:formattingissuesshouldhavebeenremovedasmuchaspossible(multiemailsinasingleaddressaremanaged'
            'likeseparateemailswhensendingwithrecipient_ids(andpartnernameisalwaysusedasnamepart)'
        )
        #Currentlybroken:CCareaddedtoALLemails(spammy)
        self.assertEqual(
            [_mail['email_cc']for_mailinself._mails],
            [['test.cc.1@test.example.com','test.cc.2@test.example.com']]*3,
        )

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_mail_values_unicode(self):
        """Unicodeshouldbefine."""
        mail=self.env['mail.mail'].create({
            'body_html':'<p>Test</p>',
            'email_cc':'test.😊.cc@example.com',
            'email_to':'test.😊@example.com',
        })
        withself.mock_mail_gateway():
            mail.send()
        self.assertEqual(len(self._mails),1)
        self.assertEqual(self._mails[0]['email_cc'],['test.😊.cc@example.com'])
        self.assertEqual(self._mails[0]['email_to'],['test.😊@example.com'])


@tagged('mail_mail')
classTestMailMailRace(common.TransactionCase):

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_bounce_during_send(self):
        self.partner=self.env['res.partner'].create({
            'name':'ErnestPartner',
        })
        #weneedtosimulateamailsentbythecrontask,firstcreatemail,messageandnotificationbyhand
        mail=self.env['mail.mail'].sudo().create({
            'body_html':'<p>Test</p>',
            'notification':True,
            'state':'outgoing',
            'recipient_ids':[(4,self.partner.id)]
        })
        message=self.env['mail.message'].create({
            'subject':'S',
            'body':'B',
            'subtype_id':self.ref('mail.mt_comment'),
            'notification_ids':[(0,0,{
                'res_partner_id':self.partner.id,
                'mail_id':mail.id,
                'notification_type':'email',
                'is_read':True,
                'notification_status':'ready',
            })],
        })
        notif=self.env['mail.notification'].search([('res_partner_id','=',self.partner.id)])
        #weneedtocommittransactionorcrwillkeepthelockonnotif
        self.cr.commit()

        #patchsend_emailinordertocreateaconcurentupdateandcheckthenotifisalreadylockedby_send()
        this=self #codinginjavascriptruinnedmylife
        bounce_deferred=[]
        @api.model
        defsend_email(self,message,*args,**kwargs):
            withthis.registry.cursor()ascr,mute_logger('flectra.sql_db'):
                try:
                    #tryroaquirelock(nowait)onnotification(shouldfail)
                    cr.execute("SELECTnotification_statusFROMmail_message_res_partner_needaction_relWHEREid=%sFORUPDATENOWAIT",[notif.id])
                exceptpsycopg2.OperationalError:
                    #recordalreadylockedbysend,allgood
                    bounce_deferred.append(True)
                else:
                    #thisshouldtriggerpsycopg2.extensions.TransactionRollbackErrorinsend().
                    #Onlyheretosimulatetheinitialusecase
                    #Iftherecordislock,thislinewouldcreateadeadlocksinceweareinthesamethread
                    #Inpractice,theupdatewillwaittheendofthesend()transactionandsetthenotifasbounce,asexpeced
                    cr.execute("UPDATEmail_message_res_partner_needaction_relSETnotification_status='bounce'WHEREid=%s",[notif.id])
            returnmessage['Message-Id']
        self.env['ir.mail_server']._patch_method('send_email',send_email)

        mail.send()

        self.assertTrue(bounce_deferred,"Thebounceshouldhavebeendeferred")
        self.assertEqual(notif.notification_status,'sent')

        #somecleaningsincewecommitedthecr
        self.env['ir.mail_server']._revert_method('send_email')

        notif.unlink()
        message.unlink()
        mail.unlink()
        self.partner.unlink()
        self.env.cr.commit()
