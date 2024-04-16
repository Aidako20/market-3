#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromunittest.mockimportpatch

fromflectra.addons.test_mail.data.test_mail_dataimportMAIL_TEMPLATE_PLAINTEXT
fromflectra.addons.test_mail.models.test_mail_modelsimportMailTestSimple
fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.apiimportcall_kw
fromflectra.exceptionsimportAccessError
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger,formataddr
fromflectra.tests.commonimportusers


@tagged('mail_post')
classTestMessagePost(TestMailCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestMessagePost,cls).setUpClass()
        cls._create_portal_user()
        cls.test_record=cls.env['mail.test.simple'].with_context(cls._test_context).create({'name':'Test','email_from':'ignasse@example.com'})
        cls._reset_mail_context(cls.test_record)
        cls.user_admin.write({'notification_type':'email'})

    #Thismethodshouldberuninsideapost_installclasstoensurethatall
    #message_postoverridesaretested.
    deftest_message_post_return(self):
        test_channel=self.env['mail.channel'].create({
            'name':'Test',
        })
        #Usecall_kwasshortcuttosimulateaRPCcall.
        messageId=call_kw(self.env['mail.channel'],'message_post',[test_channel.id],{'body':'test'})
        self.assertTrue(isinstance(messageId,int))

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_notify_mail_add_signature(self):
        test_track=self.env['mail.test.track'].with_context(self._test_context).with_user(self.user_employee).create({
            'name':'Test',
            'email_from':'ignasse@example.com'
        })
        test_track.user_id=self.env.user

        signature=self.env.user.signature

        template=self.env.ref('mail.mail_notification_paynow',raise_if_not_found=True).sudo()
        self.assertIn("record.user_id.sudo().signature",template.arch)

        withself.mock_mail_gateway():
            test_track.message_post(body="Testbody",mail_auto_delete=False,add_sign=True,partner_ids=[self.partner_1.id,self.partner_2.id],email_layout_xmlid="mail.mail_notification_paynow")
        found_mail=self._new_mails
        self.assertIn(signature,found_mail.body_html)
        self.assertEqual(found_mail.body_html.count(signature),1)

        withself.mock_mail_gateway():
            test_track.message_post(body="Testbody",mail_auto_delete=False,add_sign=False,partner_ids=[self.partner_1.id,self.partner_2.id],email_layout_xmlid="mail.mail_notification_paynow")
        found_mail=self._new_mails
        self.assertNotIn(signature,found_mail.body_html)
        self.assertEqual(found_mail.body_html.count(signature),0)

    @users('employee')
    deftest_notify_prepare_template_context_company_value(self):
        """Verifythatthetemplatecontextcompanyvalueisright
        afterswitchingtheenvcompanyorifacompany_idisset
        onmailrecord.
        """
        current_user=self.env.user
        main_company=current_user.company_id
        other_company=self.env['res.company'].with_user(self.user_admin).create({'name':'CompanyB'})
        current_user.sudo().write({'company_ids':[(4,other_company.id)]})
        test_record=self.env['mail.test.multi.company'].with_user(self.user_admin).create({
            'name':'MultiCompanyRecord',
            'company_id':False,
        })

        #self.env.company.id=MainCompany   AND   test_record.company_id=False
        self.assertEqual(self.env.company.id,main_company.id)
        self.assertEqual(test_record.company_id.id,False)
        template_values=test_record._notify_prepare_template_context(test_record.message_ids,{})
        self.assertEqual(template_values.get('company').id,self.env.company.id)

        #self.env.company.id=OtherCompany   AND   test_record.company_id=False
        current_user.company_id=other_company
        test_record=self.env['mail.test.multi.company'].browse(test_record.id)
        self.assertEqual(self.env.company.id,other_company.id)
        self.assertEqual(test_record.company_id.id,False)
        template_values=test_record._notify_prepare_template_context(test_record.message_ids,{})
        self.assertEqual(template_values.get('company').id,self.env.company.id)

        #self.env.company.id=OtherCompany   AND   test_record.company_id=MainCompany
        test_record.company_id=main_company
        test_record=self.env['mail.test.multi.company'].browse(test_record.id)
        self.assertEqual(self.env.company.id,other_company.id)
        self.assertEqual(test_record.company_id.id,main_company.id)
        template_values=test_record._notify_prepare_template_context(test_record.message_ids,{})
        self.assertEqual(template_values.get('company').id,main_company.id)

    deftest_notify_recipients_internals(self):
        pdata=self._generate_notify_recipients(self.partner_1|self.partner_employee)
        msg_vals={
            'body':'Messagebody',
            'model':self.test_record._name,
            'res_id':self.test_record.id,
            'subject':'Messagesubject',
        }
        link_vals={
            'token':'token_val',
            'access_token':'access_token_val',
            'auth_signup_token':'auth_signup_token_val',
            'auth_login':'auth_login_val',
        }
        notify_msg_vals=dict(msg_vals,**link_vals)
        classify_res=self.env[self.test_record._name]._notify_classify_recipients(pdata,'MyCustomModelName',msg_vals=notify_msg_vals)
        #findbackinformationforeachrecipients
        partner_info=next(itemforiteminclassify_resifitem['recipients']==self.partner_1.ids)
        emp_info=next(itemforiteminclassify_resifitem['recipients']==self.partner_employee.ids)

        #partner:noaccessbutton
        self.assertFalse(partner_info['has_button_access'])

        #employee:accessbuttonandlink
        self.assertTrue(emp_info['has_button_access'])
        forparam,valueinlink_vals.items():
            self.assertIn('%s=%s'%(param,value),emp_info['button_access']['url'])
        self.assertIn('model=%s'%self.test_record._name,emp_info['button_access']['url'])
        self.assertIn('res_id=%s'%self.test_record.id,emp_info['button_access']['url'])
        self.assertNotIn('body',emp_info['button_access']['url'])
        self.assertNotIn('subject',emp_info['button_access']['url'])

        #testwhennotifyingonnon-records(e.g.MailThread._message_notify())
        formodel,res_idin((self.test_record._name,False),
                              (self.test_record._name,0), #browse(0)doesnotreturnavalidrecordset
                              (False,self.test_record.id),
                              (False,False),
                              ('mail.thread',False),
                              ('mail.thread',self.test_record.id)):
            msg_vals.update({
                'model':model,
                'res_id':res_id,
            })
            #notethatmsg_valswinsoverrecordonwhichmethodiscalled
            notify_msg_vals=dict(msg_vals,**link_vals)
            classify_res=self.test_record._notify_classify_recipients(
                pdata,'Test',msg_vals=notify_msg_vals)
            #findbackinformationforpartner
            partner_info=next(itemforiteminclassify_resifitem['recipients']==self.partner_1.ids)
            emp_info=next(itemforiteminclassify_resifitem['recipients']==self.partner_employee.ids)
            #checkthereisnoaccessbutton
            self.assertFalse(partner_info['has_button_access'])
            self.assertFalse(emp_info['has_button_access'])

            #testonfalsyrecords(Falsemodelcannotbebrowsed,skipped)
            ifmodel:
                record_falsy=self.env[model].browse(res_id)
                classify_res=record_falsy._notify_classify_recipients(
                    pdata,'Test',msg_vals=notify_msg_vals)
                #findbackinformationforpartner
                partner_info=next(itemforiteminclassify_resifitem['recipients']==self.partner_1.ids)
                emp_info=next(itemforiteminclassify_resifitem['recipients']==self.partner_employee.ids)
                #checkthereisnoaccessbutton
                self.assertFalse(partner_info['has_button_access'])
                self.assertFalse(emp_info['has_button_access'])

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_needaction(self):
        (self.user_employee|self.user_admin).write({'notification_type':'inbox'})
        withself.assertSinglePostNotifications([{'partner':self.partner_employee,'type':'inbox'}],{'content':'Body'}):
            self.test_record.message_post(
                body='Body',message_type='comment',subtype_xmlid='mail.mt_comment',
                partner_ids=[self.user_employee.partner_id.id])

        self.test_record.message_subscribe([self.partner_1.id])
        withself.assertSinglePostNotifications([
                {'partner':self.partner_employee,'type':'inbox'},
                {'partner':self.partner_1,'type':'email'}],{'content':'NewBody'}):
            self.test_record.message_post(
                body='NewBody',message_type='comment',subtype_xmlid='mail.mt_comment',
                partner_ids=[self.user_employee.partner_id.id])

        withself.assertSinglePostNotifications([
                {'partner':self.partner_1,'type':'email'},
                {'partner':self.partner_portal,'type':'email'}],{'content':'ToPortal'}):
            self.test_record.message_post(
                body='ToPortal',message_type='comment',subtype_xmlid='mail.mt_comment',
                partner_ids=[self.partner_portal.id])

    deftest_post_inactive_follower(self):
        #Insomecaseflectrabotisfollowerofarecord.
        #Evenifitshouldn'tbethecase,wewanttobesurethatflectrabotisnotnotified
        (self.user_employee|self.user_admin).write({'notification_type':'inbox'})
        self.test_record._message_subscribe(self.user_employee.partner_id.ids)
        withself.assertSinglePostNotifications([{'partner':self.partner_employee,'type':'inbox'}],{'content':'Test'}):
            self.test_record.message_post(
                body='Test',message_type='comment',subtype_xmlid='mail.mt_comment')

        self.user_employee.active=False
        #atthispoint,partnerisstillactiveandwouldreceiveanemailnotification
        self.user_employee.partner_id._write({'active':False})
        withself.assertPostNotifications([{'content':'Test','notif':[]}]):
            self.test_record.message_post(
                body='Test',message_type='comment',subtype_xmlid='mail.mt_comment')

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.tests')
    deftest_post_notifications(self):
        _body,_subject='<p>TestBody</p>','TestSubject'

        #subscribesecondemployeetothegrouptotestnotifications
        self.test_record.message_subscribe(partner_ids=[self.user_admin.partner_id.id])

        withself.assertSinglePostNotifications(
                [{'partner':self.partner_1,'type':'email'},
                 {'partner':self.partner_2,'type':'email'},
                 {'partner':self.partner_admin,'type':'email'}],
                {'content':_body},
                mail_unlink_sent=True):
            msg=self.test_record.with_user(self.user_employee).message_post(
                body=_body,subject=_subject,
                message_type='comment',subtype_xmlid='mail.mt_comment',
                partner_ids=[self.partner_1.id,self.partner_2.id]
            )

        #messagecontent
        self.assertEqual(msg.subject,_subject)
        self.assertEqual(msg.body,_body)
        self.assertEqual(msg.partner_ids,self.partner_1|self.partner_2)
        self.assertEqual(msg.notified_partner_ids,self.user_admin.partner_id|self.partner_1|self.partner_2)
        self.assertEqual(msg.channel_ids,self.env['mail.channel'])

        #notificationsemailsshouldhavebeendeleted
        self.assertFalse(self.env['mail.mail'].sudo().search([('mail_message_id','=',msg.id)]),
                         'message_post:mail.mailnotificationsshouldhavebeenauto-deleted')

        #notified_partner_idsshouldbeemptyaftercopyingthemessage
        copy=msg.copy()
        self.assertFalse(copy.notified_partner_ids)

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.tests')
    deftest_post_notifications_email_field(self):
        """Testvariouscombinationsofcornercase/notstandardfillingof
        emailfields:multiemail,formattedemails,..."""
        partner_emails=[
            'valid.lelitre@agrolait.com,valid.lelitre.cc@agrolait.com', #multiemail
            '"ValidLelitre"<valid.lelitre@agrolait.com>', #emailcontainsformattedemail
            'wrong', #wrong
            False,'','', #falsy
        ]
        expected_tos=[
            #Sendsmulti-emails
            [f'"{self.partner_1.name}"<valid.lelitre@agrolait.com>',
             f'"{self.partner_1.name}"<valid.lelitre.cc@agrolait.com>',],
            #Avoiddoubleencapsulation
            [f'"{self.partner_1.name}"<valid.lelitre@agrolait.com>',],
            #sent"normally":formatsemailbasedonwrong/falsyemail
            [f'"{self.partner_1.name}"<@wrong>',],
            [f'"{self.partner_1.name}"<@False>',],
            [f'"{self.partner_1.name}"<@False>',],
            [f'"{self.partner_1.name}"<@>',],
        ]

        forpartner_email,expected_toinzip(partner_emails,expected_tos):
            withself.subTest(partner_email=partner_email,expected_to=expected_to):
                self.partner_1.write({'email':partner_email})
                withself.mock_mail_gateway():
                    self.test_record.with_user(self.user_employee).message_post(
                        body='Testmultiemail',
                        message_type='comment',
                        partner_ids=[self.partner_1.id],
                        subject='Exoticemail',
                        subtype_xmlid='mt_comment',
                    )

                self.assertSentEmail(
                    self.user_employee.partner_id,
                    [self.partner_1],
                    email_to=expected_to,
                )

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_post_notifications_emails_tweak(self):
        pass
        #weshouldcheck_notification_groupsbehavior,foremailsandbuttons

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_notifications_keep_emails(self):
        self.test_record.message_subscribe(partner_ids=[self.user_admin.partner_id.id])

        msg=self.test_record.with_user(self.user_employee).message_post(
            body='Test',subject='Test',
            message_type='comment',subtype_xmlid='mail.mt_comment',
            partner_ids=[self.partner_1.id,self.partner_2.id],
            mail_auto_delete=False
        )

        #notificationsemailsshouldnothavebeendeleted:oneforcustomers,oneforuser
        self.assertEqual(len(self.env['mail.mail'].sudo().search([('mail_message_id','=',msg.id)])),2)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_attachments(self):
        _attachments=[
            ('List1',b'Myfirstattachment'),
            ('List2',b'Mysecondattachment')
        ]
        _attach_1=self.env['ir.attachment'].with_user(self.user_employee).create({
            'name':'Attach1',
            'datas':'bWlncmF0aW9uIHRlc3Q=',
            'res_model':'mail.compose.message','res_id':0})
        _attach_2=self.env['ir.attachment'].with_user(self.user_employee).create({
            'name':'Attach2',
            'datas':'bWlncmF0aW9uIHRlc3Q=',
            'res_model':'mail.compose.message','res_id':0})

        withself.mock_mail_gateway():
            msg=self.test_record.with_user(self.user_employee).message_post(
                body='Test',subject='Test',
                message_type='comment',subtype_xmlid='mail.mt_comment',
                attachment_ids=[_attach_1.id,_attach_2.id],
                partner_ids=[self.partner_1.id],
                attachments=_attachments,
            )

        #messageattachments
        self.assertEqual(len(msg.attachment_ids),4)
        self.assertEqual(set(msg.attachment_ids.mapped('res_model')),set([self.test_record._name]))
        self.assertEqual(set(msg.attachment_ids.mapped('res_id')),set([self.test_record.id]))
        self.assertEqual(set([base64.b64decode(x)forxinmsg.attachment_ids.mapped('datas')]),
                         set([b'migrationtest',_attachments[0][1],_attachments[1][1]]))
        self.assertTrue(set([_attach_1.id,_attach_2.id]).issubset(msg.attachment_ids.ids),
                        'message_post:mail.messageattachmentsduplicated')

        #notificationemailattachments
        self.assertSentEmail(self.user_employee.partner_id,[self.partner_1])
        #self.assertEqual(len(self._mails),1)
        self.assertEqual(len(self._mails[0]['attachments']),4)
        self.assertIn(('List1',b'Myfirstattachment','application/octet-stream'),self._mails[0]['attachments'])
        self.assertIn(('List2',b'Mysecondattachment','application/octet-stream'),self._mails[0]['attachments'])
        self.assertIn(('Attach1',b'migrationtest','application/octet-stream'), self._mails[0]['attachments'])
        self.assertIn(('Attach2',b'migrationtest','application/octet-stream'),self._mails[0]['attachments'])

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_answer(self):
        withself.mock_mail_gateway():
            parent_msg=self.test_record.with_user(self.user_employee).message_post(
                body='<p>Test</p>',
                message_type='comment',
                subject='TestSubject',
                subtype_xmlid='mail.mt_comment',
            )

        self.assertEqual(parent_msg.partner_ids,self.env['res.partner'])
        self.assertNotSentEmail()

        #postafirstreply
        withself.assertPostNotifications([{'content':'<p>TestAnswer</p>','notif':[{'partner':self.partner_1,'type':'email'}]}]):
            msg=self.test_record.with_user(self.user_employee).message_post(
                body='<p>TestAnswer</p>',
                message_type='comment',
                subject='Welcome',
                subtype_xmlid='mail.mt_comment',
                parent_id=parent_msg.id,
                partner_ids=[self.partner_1.id],
            )

        self.assertEqual(msg.parent_id.id,parent_msg.id)
        self.assertEqual(msg.partner_ids,self.partner_1)
        self.assertEqual(parent_msg.partner_ids,self.env['res.partner'])

        #checknotificationemails:references
        self.assertSentEmail(
            self.user_employee.partner_id,
            [self.partner_1],
            references_content='openerp-%d-mail.test.simple'%self.test_record.id,
            #referencesshouldbesortedfromtheoldesttothenewest
            references='%s%s'%(parent_msg.message_id,msg.message_id),
        )

        #postareplytothereply:checkparentisthefirstone
        withself.mock_mail_gateway():
            new_msg=self.test_record.with_user(self.user_employee).message_post(
                body='<p>TestAnswerBis</p>',
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                parent_id=msg.id,
                partner_ids=[self.partner_2.id],
            )

        self.assertEqual(new_msg.parent_id.id,parent_msg.id,'message_post:flattenerror')
        self.assertEqual(new_msg.partner_ids,self.partner_2)
        self.assertSentEmail(
            self.user_employee.partner_id,
            [self.partner_2],
            body_content='<p>TestAnswerBis</p>',
            reply_to=msg.reply_to,
            subject='Re:%s'%self.test_record.name,
            references_content='openerp-%d-mail.test.simple'%self.test_record.id,
            references='%s%s'%(parent_msg.message_id,new_msg.message_id),
        )

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.tests')
    deftest_post_email_with_multiline_subject(self):
        _body,_body_alt,_subject='<p>TestBody</p>','TestBody','1stline\n2ndline'
        msg=self.test_record.with_user(self.user_employee).message_post(
            body=_body,subject=_subject,
            message_type='comment',subtype_xmlid='mail.mt_comment',
            partner_ids=[self.partner_1.id,self.partner_2.id]
        )
        self.assertEqual(msg.subject,'1stline2ndline')

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_portal_ok(self):
        self.test_record.message_subscribe((self.partner_1|self.user_employee.partner_id).ids)

        withself.assertPostNotifications([{'content':'<p>Test</p>','notif':[
            {'partner':self.partner_employee,'type':'inbox'},
            {'partner':self.partner_1,'type':'email'}]}
        ]),patch.object(MailTestSimple,'check_access_rights',return_value=True):
            new_msg=self.test_record.with_user(self.user_portal).message_post(
                body='<p>Test</p>',subject='Subject',
                message_type='comment',subtype_xmlid='mail.mt_comment')

        self.assertEqual(new_msg.sudo().notified_partner_ids,(self.partner_1|self.user_employee.partner_id))

    deftest_post_portal_crash(self):
        withself.assertRaises(AccessError):
            self.test_record.with_user(self.user_portal).message_post(
                body='<p>Test</p>',subject='Subject',
                message_type='comment',subtype_xmlid='mail.mt_comment')

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.addons.mail.models.mail_thread')
    deftest_post_internal(self):
        self.test_record.message_subscribe([self.user_admin.partner_id.id])
        msg=self.test_record.with_user(self.user_employee).message_post(
            body='MyBody',subject='MySubject',
            message_type='comment',subtype_xmlid='mail.mt_note')
        self.assertEqual(msg.partner_ids,self.env['res.partner'])
        self.assertEqual(msg.notified_partner_ids,self.env['res.partner'])

        self.format_and_process(
            MAIL_TEMPLATE_PLAINTEXT,self.user_admin.email,'not_my_businesss@example.com',
            msg_id='<1198923581.41972151344608186800.JavaMail.diff1@agrolait.com>',
            extra='In-Reply-To:\r\n\t%s\n'%msg.message_id,
            target_model='mail.test.simple')
        reply=self.test_record.message_ids-msg
        self.assertTrue(reply)
        self.assertEqual(reply.subtype_id,self.env.ref('mail.mt_note'))
        self.assertEqual(reply.notified_partner_ids,self.user_employee.partner_id)
        self.assertEqual(reply.parent_id,msg)

    deftest_post_log(self):
        new_note=self.test_record.with_user(self.user_employee)._message_log(
            body='<p>Labrador</p>',
        )

        self.assertEqual(new_note.subtype_id,self.env.ref('mail.mt_note'))
        self.assertEqual(new_note.body,'<p>Labrador</p>')
        self.assertEqual(new_note.author_id,self.user_employee.partner_id)
        self.assertEqual(new_note.email_from,formataddr((self.user_employee.name,self.user_employee.email)))
        self.assertEqual(new_note.notified_partner_ids,self.env['res.partner'])

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_notify(self):
        self.user_employee.write({'notification_type':'inbox'})

        withself.mock_mail_gateway():
            new_notification=self.test_record.message_notify(
                subject='Thisshouldbeasubject',
                body='<p>Youhavereceivedanotification</p>',
                partner_ids=[self.partner_1.id,self.partner_admin.id,self.user_employee.partner_id.id],
            )

        self.assertEqual(new_notification.subtype_id,self.env.ref('mail.mt_note'))
        self.assertEqual(new_notification.message_type,'user_notification')
        self.assertEqual(new_notification.body,'<p>Youhavereceivedanotification</p>')
        self.assertEqual(new_notification.author_id,self.env.user.partner_id)
        self.assertEqual(new_notification.email_from,formataddr((self.env.user.name,self.env.user.email)))
        self.assertEqual(new_notification.notified_partner_ids,self.partner_1|self.user_employee.partner_id|self.partner_admin)
        self.assertNotIn(new_notification,self.test_record.message_ids)

        admin_mails=[xforxinself._mailsifself.partner_admin.nameinx.get('email_to')[0]]
        self.assertEqual(len(admin_mails),1,'Thereshouldbeexactlyoneemailsenttoadmin')
        admin_mail=admin_mails[0].get('body')
        admin_access_link=admin_mail[admin_mail.index('model='):admin_mail.index('/>')-1]if'model='inadmin_mailelseNone
  
        self.assertIsNotNone(admin_access_link,'Theemailsenttoadminshouldcontainanaccesslink')
        self.assertIn('model=%s'%self.test_record._name,admin_access_link,'Theaccesslinkshouldcontainavalidmodelargument')
        self.assertIn('res_id=%d'%self.test_record.id,admin_access_link,'Theaccesslinkshouldcontainavalidres_idargument')

        partner_mails=[xforxinself._mailsifself.partner_1.nameinx.get('email_to')[0]]
        self.assertEqual(len(partner_mails),1,'Thereshouldbeexactlyoneemailsenttopartner')
        partner_mail=partner_mails[0].get('body')
        self.assertNotIn('/mail/view?model=',partner_mail,'Theemailsenttoadminshouldnotcontainanaccesslink')
        #todoxdoaddtestmessage_notifyonthreadwithfollowersandstuff

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_post_w_template(self):
        test_record=self.env['mail.test.simple'].with_context(self._test_context).create({'name':'Test','email_from':'ignasse@example.com'})
        self.user_employee.write({
            'groups_id':[(4,self.env.ref('base.group_partner_manager').id)],
        })
        _attachments=[{
            'name':'first.txt',
            'datas':base64.b64encode(b'Myfirstattachment'),
            'res_model':'res.partner',
            'res_id':self.user_admin.partner_id.id
        },{
            'name':'second.txt',
            'datas':base64.b64encode(b'Mysecondattachment'),
            'res_model':'res.partner',
            'res_id':self.user_admin.partner_id.id
        }]
        email_1='test1@example.com'
        email_2='test2@example.com'
        email_3=self.partner_1.email
        self._create_template('mail.test.simple',{
            'attachment_ids':[(0,0,_attachments[0]),(0,0,_attachments[1])],
            'partner_to':'%s,%s'%(self.partner_2.id,self.user_admin.partner_id.id),
            'email_to':'%s,%s'%(email_1,email_2),
            'email_cc':'%s'%email_3,
        })
        #adminshouldreceiveemails
        self.user_admin.write({'notification_type':'email'})
        #Forcetheattachmentsofthetemplatetobeinthenaturalorder.
        self.email_template.invalidate_cache(['attachment_ids'],ids=self.email_template.ids)

        withself.mock_mail_gateway():
            test_record.with_user(self.user_employee).message_post_with_template(self.email_template.id,composition_mode='comment')

        new_partners=self.env['res.partner'].search([('email','in',[email_1,email_2])])
        forrin[self.partner_1,self.partner_2,new_partners[0],new_partners[1],self.partner_admin]:
            self.assertSentEmail(
                self.user_employee.partner_id,
                [r],
                subject='About%s'%test_record.name,
                body_content=test_record.name,
                attachments=[('first.txt',b'Myfirstattachment','text/plain'),('second.txt',b'Mysecondattachment','text/plain')])
