#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.urlsimporturl_parse,url_decode

fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.tests.commonimporttagged,HttpCase,users
fromflectra.toolsimportmute_logger


@tagged('mail_thread')
classTestChatterTweaks(TestMailCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestChatterTweaks,cls).setUpClass()
        cls.test_record=cls.env['mail.test.simple'].with_context(cls._test_context).create({'name':'Test','email_from':'ignasse@example.com'})

    deftest_post_no_subscribe_author(self):
        original=self.test_record.message_follower_ids
        self.test_record.with_user(self.user_employee).with_context({'mail_create_nosubscribe':True}).message_post(
            body='TestBody',message_type='comment',subtype_xmlid='mail.mt_comment')
        self.assertEqual(self.test_record.message_follower_ids.mapped('partner_id'),original.mapped('partner_id'))
        self.assertEqual(self.test_record.message_follower_ids.mapped('channel_id'),original.mapped('channel_id'))

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_no_subscribe_recipients(self):
        original=self.test_record.message_follower_ids
        self.test_record.with_user(self.user_employee).with_context({'mail_create_nosubscribe':True}).message_post(
            body='TestBody',message_type='comment',subtype_xmlid='mail.mt_comment',partner_ids=[self.partner_1.id,self.partner_2.id])
        self.assertEqual(self.test_record.message_follower_ids.mapped('partner_id'),original.mapped('partner_id'))
        self.assertEqual(self.test_record.message_follower_ids.mapped('channel_id'),original.mapped('channel_id'))

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_post_subscribe_recipients(self):
        original=self.test_record.message_follower_ids
        self.test_record.with_user(self.user_employee).with_context({'mail_create_nosubscribe':True,'mail_post_autofollow':True}).message_post(
            body='TestBody',message_type='comment',subtype_xmlid='mail.mt_comment',partner_ids=[self.partner_1.id,self.partner_2.id])
        self.assertEqual(self.test_record.message_follower_ids.mapped('partner_id'),original.mapped('partner_id')|self.partner_1|self.partner_2)
        self.assertEqual(self.test_record.message_follower_ids.mapped('channel_id'),original.mapped('channel_id'))

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_chatter_context_cleaning(self):
        """Testdefaultkeysarenotpropagatedtomessagecreationasitmay
        inducewrongvaluesforsomefields,likeparent_id."""
        parent=self.env['res.partner'].create({'name':'Parent'})
        partner=self.env['res.partner'].with_context(default_parent_id=parent.id).create({'name':'Contact'})
        self.assertFalse(partner.message_ids[-1].parent_id)

    deftest_chatter_mail_create_nolog(self):
        """Testdisableofautomaticchattermessageatcreate"""
        rec=self.env['mail.test.simple'].with_user(self.user_employee).with_context({'mail_create_nolog':True}).create({'name':'Test'})
        self.flush_tracking()
        self.assertEqual(rec.message_ids,self.env['mail.message'])

        rec=self.env['mail.test.simple'].with_user(self.user_employee).with_context({'mail_create_nolog':False}).create({'name':'Test'})
        self.flush_tracking()
        self.assertEqual(len(rec.message_ids),1)

    deftest_chatter_mail_notrack(self):
        """Testdisableofautomaticvaluetrackingatcreateandwrite"""
        rec=self.env['mail.test.track'].with_user(self.user_employee).create({'name':'Test','user_id':self.user_employee.id})
        self.flush_tracking()
        self.assertEqual(len(rec.message_ids),1,
                         "Acreationmessagewithouttrackingvaluesshouldhavebeenposted")
        self.assertEqual(len(rec.message_ids.sudo().tracking_value_ids),0,
                         "Acreationmessagewithouttrackingvaluesshouldhavebeenposted")

        rec.with_context({'mail_notrack':True}).write({'user_id':self.user_admin.id})
        self.flush_tracking()
        self.assertEqual(len(rec.message_ids),1,
                         "Nonewmessageshouldhavebeenpostedwithmail_notrackkey")

        rec.with_context({'mail_notrack':False}).write({'user_id':self.user_employee.id})
        self.flush_tracking()
        self.assertEqual(len(rec.message_ids),2,
                         "Atrackingmessageshouldhavebeenposted")
        self.assertEqual(len(rec.message_ids.sudo().mapped('tracking_value_ids')),1,
                         "Newtrackingmessageshouldhavetrackingvalues")

    deftest_chatter_tracking_disable(self):
        """Testdisableofallchatterfeaturesatcreateandwrite"""
        rec=self.env['mail.test.track'].with_user(self.user_employee).with_context({'tracking_disable':True}).create({'name':'Test','user_id':self.user_employee.id})
        self.flush_tracking()
        self.assertEqual(rec.sudo().message_ids,self.env['mail.message'])
        self.assertEqual(rec.sudo().mapped('message_ids.tracking_value_ids'),self.env['mail.tracking.value'])

        rec.write({'user_id':self.user_admin.id})
        self.flush_tracking()
        self.assertEqual(rec.sudo().mapped('message_ids.tracking_value_ids'),self.env['mail.tracking.value'])

        rec.with_context({'tracking_disable':False}).write({'user_id':self.user_employee.id})
        self.flush_tracking()
        self.assertEqual(len(rec.sudo().mapped('message_ids.tracking_value_ids')),1)

        rec=self.env['mail.test.track'].with_user(self.user_employee).with_context({'tracking_disable':False}).create({'name':'Test','user_id':self.user_employee.id})
        self.flush_tracking()
        self.assertEqual(len(rec.sudo().message_ids),1,
                         "Creationmessagewithouttrackingvaluesshouldhavebeenposted")
        self.assertEqual(len(rec.sudo().mapped('message_ids.tracking_value_ids')),0,
                         "Creationmessagewithouttrackingvaluesshouldhavebeenposted")

    deftest_cache_invalidation(self):
        """Testthatcreatingamail-threadrecorddoesnotinvalidatethewholecache."""
        #makeanewrecordincache
        record=self.env['res.partner'].new({'name':'BraveNewPartner'})
        self.assertTrue(record.name)

        #creatingamail-threadrecordshouldnotinvalidatethewholecache
        self.env['res.partner'].create({'name':'ActualPartner'})
        self.assertTrue(record.name)


classTestDiscuss(TestMailCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestDiscuss,cls).setUpClass()
        cls.test_record=cls.env['mail.test.simple'].with_context(cls._test_context).create({'name':'Test','email_from':'ignasse@example.com'})

    deftest_set_message_done_user(self):
        withself.assertSinglePostNotifications([{'partner':self.partner_employee,'type':'inbox'}],message_info={'content':'Test'}):
            message=self.test_record.message_post(
                body='Test',message_type='comment',subtype_xmlid='mail.mt_comment',
                partner_ids=[self.user_employee.partner_id.id])
        message.with_user(self.user_employee).set_message_done()
        self.assertMailNotifications(message,[{'notif':[{'partner':self.partner_employee,'type':'inbox','is_read':True}]}])
        #TDETODO:itseemsbusnotificationscouldbechecked

    deftest_set_star(self):
        msg=self.test_record.with_user(self.user_admin).message_post(body='MyBody',subject='1')
        msg_emp=self.env['mail.message'].with_user(self.user_employee).browse(msg.id)

        #Adminsetasstarred
        msg.toggle_message_starred()
        self.assertTrue(msg.starred)

        #Employeesetasstarred
        msg_emp.toggle_message_starred()
        self.assertTrue(msg_emp.starred)

        #Do:Adminunstarsmsg
        msg.toggle_message_starred()
        self.assertFalse(msg.starred)
        self.assertTrue(msg_emp.starred)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_cc_recipient_suggestion(self):
        record=self.env['mail.test.cc'].create({'email_cc':'cc1@example.com,cc2@example.com,cc3<cc3@example.com>'})
        suggestions=record._message_get_suggested_recipients()[record.id]
        self.assertEqual(sorted(suggestions),[
            (False,'"cc3"<cc3@example.com>','CCEmail'),
            (False,'cc1@example.com','CCEmail'),
            (False,'cc2@example.com','CCEmail'),
        ],'ccshouldbeinsuggestions')

    deftest_inbox_message_fetch_needaction(self):
        user1=self.env['res.users'].create({'login':'user1','name':'User1'})
        user1.notification_type='inbox'
        user2=self.env['res.users'].create({'login':'user2','name':'User2'})
        user2.notification_type='inbox'
        message1=self.test_record.with_user(self.user_admin).message_post(body='Message1',partner_ids=[user1.partner_id.id,user2.partner_id.id])
        message2=self.test_record.with_user(self.user_admin).message_post(body='Message2',partner_ids=[user1.partner_id.id,user2.partner_id.id])

        #bothnotifiedusersshouldhavethe2messagesinInboxinitially
        messages=self.env['mail.message'].with_user(user1).message_fetch(domain=[['needaction','=',True]])
        self.assertEqual(len(messages),2)
        messages=self.env['mail.message'].with_user(user2).message_fetch(domain=[['needaction','=',True]])
        self.assertEqual(len(messages),2)

        #firstuserismarkingonemessageasdone:theothermessageisstillInbox,whiletheotheruserstillhasthe2messagesinInbox
        message1.with_user(user1).set_message_done()
        messages=self.env['mail.message'].with_user(user1).message_fetch(domain=[['needaction','=',True]])
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].get('id'),message2.id)
        messages=self.env['mail.message'].with_user(user2).message_fetch(domain=[['needaction','=',True]])
        self.assertEqual(len(messages),2)

    deftest_notification_has_error_filter(self):
        """Ensuremessage_has_errorfilterisonlyreturningthreadsforwhich
        thecurrentuserisauthorofafailedmessage."""
        message=self.test_record.with_user(self.user_admin).message_post(
            body='Test',message_type='comment',subtype_xmlid='mail.mt_comment',
            partner_ids=[self.user_employee.partner_id.id]
        )
        self.assertFalse(message.has_error)
        withself.mock_mail_gateway(sim_error='connect_smtp_notfound'):
            self.user_admin.notification_type='email'
            message2=self.test_record.with_user(self.user_employee).message_post(
                body='Test',message_type='comment',subtype_xmlid='mail.mt_comment',
                partner_ids=[self.user_admin.partner_id.id]
            )
            self.assertTrue(message2.has_error)
        #employeeisauthorofmessagewhichhasafailure
        threads_employee=self.test_record.with_user(self.user_employee).search([('message_has_error','=',True)])
        self.assertEqual(len(threads_employee),1)
        #adminisalsoauthorofamessage,butitdoesn'thaveafailure
        #andthefailurefromemployee'smessageshouldnotbetakenintoaccountforadmin
        threads_admin=self.test_record.with_user(self.user_admin).search([('message_has_error','=',True)])
        self.assertEqual(len(threads_admin),0)

    @users("employee")
    deftest_unlink_notification_message(self):
        channel=self.env['mail.channel'].create({'name':'testChannel'})
        channel.message_notify(
            body='test',
            message_type='user_notification',
            partner_ids=[self.partner_2.id],
            author_id=2
        )

        channel_message=self.env['mail.message'].sudo().search([('model','=','mail.channel'),('res_id','in',channel.ids)])
        self.assertEqual(len(channel_message),1,"Testmessageshouldhavebeenposted")

        channel.unlink()
        remaining_message=channel_message.exists()
        self.assertEqual(len(remaining_message),0,"Testmessageshouldhavebeendeleted")


@tagged('-at_install','post_install')
classTestMultiCompany(HttpCase):

    deftest_redirect_to_records(self):

        self.company_A=self.env['res.company'].create({
            'name':'CompanyA',
            'user_ids':[(4,self.ref('base.user_admin'))],
        })

        self.company_B=self.env['res.company'].create({
            'name':'CompanyB',
        })

        self.multi_company_record=self.env['mail.test.multi.company'].create({
            'name':'MultiCompanyRecord',
            'company_id':self.company_A.id,
        })

        #TestCase0
        #Notlogged,redirecttoweb/login
        response=self.url_open('/mail/view?model=%s&res_id=%s'%(
            self.multi_company_record._name,
            self.multi_company_record.id),timeout=15)

        path=url_parse(response.url).path
        self.assertEqual(path,'/web/login')

        self.authenticate('admin','admin')

        #TestCase1
        #Loggedintocompany1,tryaccessingrecordincompanyA
        #_redirect_to_recordshouldaddcompanyAinallowed_company_ids
        response=self.url_open('/mail/view?model=%s&res_id=%s'%(
            self.multi_company_record._name,
            self.multi_company_record.id),timeout=15)

        self.assertEqual(response.status_code,200)

        fragment=url_parse(response.url).fragment
        cids=url_decode(fragment)['cids']

        self.assertEqual(cids,'1,%s'%(self.company_A.id))

        #TestCase2
        #Loggedintocompany1,tryaccessingrecordincompanyB
        #_redirect_to_recordshouldredirecttomessagingastheuser
        #doesn'thaveanyaccessforthiscompany
        self.multi_company_record.company_id=self.company_B

        response=self.url_open('/mail/view?model=%s&res_id=%s'%(
            self.multi_company_record._name,
            self.multi_company_record.id),timeout=15)

        self.assertEqual(response.status_code,200)

        fragment=url_parse(response.url).fragment
        action=url_decode(fragment)['action']

        self.assertEqual(action,'mail.action_discuss')
