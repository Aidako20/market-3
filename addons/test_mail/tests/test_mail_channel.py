#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimporttagged,Form
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.exceptionsimportAccessError,ValidationError,UserError
fromflectra.toolsimportmute_logger,formataddr


@tagged('mail_channel')
classTestChannelAccessRights(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestChannelAccessRights,cls).setUpClass()
        Channel=cls.env['mail.channel'].with_context(cls._test_context)

        cls.user_public=mail_new_test_user(cls.env,login='bert',groups='base.group_public',name='BertTartignole')
        cls.user_portal=mail_new_test_user(cls.env,login='chell',groups='base.group_portal',name='ChellGladys')

        #Pigs:basegroupfortests
        cls.group_pigs=Channel.create({
            'name':'Pigs',
            'public':'groups',
            'group_public_id':cls.env.ref('base.group_user').id})
        #Jobs:publicgroup
        cls.group_public=Channel.create({
            'name':'Jobs',
            'description':'NotFalse',
            'public':'public'})
        #Private:privategroup
        cls.group_private=Channel.create({
            'name':'Private',
            'public':'private'})

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_access_rights_public(self):
        #Readpublicgroup->ok
        self.group_public.with_user(self.user_public).read()

        #ReadPigs->ko,restrictedtoemployees
        withself.assertRaises(AccessError):
            self.group_pigs.with_user(self.user_public).read()

        #Readaprivategroupwhenbeingamember:ok
        self.group_private.write({'channel_partner_ids':[(4,self.user_public.partner_id.id)]})
        self.group_private.with_user(self.user_public).read()

        #Creategroup:ko,noaccessrights
        withself.assertRaises(AccessError):
            self.env['mail.channel'].with_user(self.user_public).create({'name':'Test'})

        #Updategroup:ko,noaccessrights
        withself.assertRaises(AccessError):
            self.group_public.with_user(self.user_public).write({'name':'Broutouschnouk'})

        #Unlinkgroup:ko,noaccessrights
        withself.assertRaises(AccessError):
            self.group_public.with_user(self.user_public).unlink()

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models','flectra.models.unlink')
    deftest_access_rights_groups(self):
        #Employeereademployee-basedgroup:ok
        self.group_pigs.with_user(self.user_employee).read()

        #Employeecancreateagroup
        self.env['mail.channel'].with_user(self.user_employee).create({'name':'Test'})

        #Employeeupdateemployee-basedgroup:ok
        self.group_pigs.with_user(self.user_employee).write({'name':'modified'})

        #Employeeunlinkemployee-basedgroup:ok
        self.group_pigs.with_user(self.user_employee).unlink()

        #Employeecannotreadaprivategroup
        withself.assertRaises(AccessError):
            self.group_private.with_user(self.user_employee).read()

        #Employeecannotwriteonprivate
        withself.assertRaises(AccessError):
            self.group_private.with_user(self.user_employee).write({'name':'re-modified'})

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_access_rights_followers_ko(self):
        #self.group_private.namehasbeenputinthecacheduringthesetupassudo
        #Itmustthereforeberemovedfromthecacheinothertovalidatethefactuser_portalcan'treadit.
        self.group_private.invalidate_cache(['name'])
        withself.assertRaises(AccessError):
            self.group_private.with_user(self.user_portal).name

    deftest_access_rights_followers_portal(self):
        #Do:ChellisaddedintoPigsmembersandbrowseit->okformessages,koforpartners(noreadpermission)
        self.group_private.write({'channel_partner_ids':[(4,self.user_portal.partner_id.id)]})
        chell_pigs=self.group_private.with_user(self.user_portal)
        trigger_read=chell_pigs.name
        formessageinchell_pigs.message_ids:
            trigger_read=message.subject

        withself.assertRaises(AccessError):
            chell_pigs.message_partner_ids

        forpartnerinself.group_private.message_partner_ids:
            ifpartner.id==self.user_portal.partner_id.id:
                #Chellcanreadherownpartnerrecord
                continue
            withself.assertRaises(AccessError):
                trigger_read=partner.with_user(self.user_portal).name


@tagged('mail_channel')
classTestChannelFeatures(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestChannelFeatures,cls).setUpClass()
        cls.test_channel=cls.env['mail.channel'].with_context(cls._test_context).create({
            'name':'Test',
            'description':'Description',
            'alias_name':'test',
            'public':'public',
        })
        cls.test_partner=cls.env['res.partner'].with_context(cls._test_context).create({
            'name':'TestPartner',
            'email':'test@example.com',
        })

    def_join_channel(self,channel,partners):
        forpartnerinpartners:
            channel.write({'channel_last_seen_partner_ids':[(0,0,{'partner_id':partner.id})]})
        channel.invalidate_cache()

    def_leave_channel(self,channel,partners):
        forpartnerinpartners:
            channel._action_unfollow(partner)

    deftest_channel_listeners(self):
        self.assertEqual(self.test_channel.message_channel_ids,self.test_channel)
        self.assertEqual(self.test_channel.message_partner_ids,self.env['res.partner'])
        self.assertEqual(self.test_channel.channel_partner_ids,self.env['res.partner'])

        self._join_channel(self.test_channel,self.test_partner)
        self.assertEqual(self.test_channel.message_channel_ids,self.test_channel)
        self.assertEqual(self.test_channel.message_partner_ids,self.env['res.partner'])
        self.assertEqual(self.test_channel.channel_partner_ids,self.test_partner)

        self._leave_channel(self.test_channel,self.test_partner)
        self.assertEqual(self.test_channel.message_channel_ids,self.test_channel)
        self.assertEqual(self.test_channel.message_partner_ids,self.env['res.partner'])
        self.assertEqual(self.test_channel.channel_partner_ids,self.env['res.partner'])

    deftest_channel_post_nofollow(self):
        self.test_channel.message_post(body='Test',message_type='comment',subtype_xmlid='mail.mt_comment')
        self.assertEqual(self.test_channel.message_channel_ids,self.test_channel)
        self.assertEqual(self.test_channel.message_partner_ids,self.env['res.partner'])

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_channel_mailing_list_recipients(self):
        """Postingamessageonamailinglistshouldsendoneemailtoallrecipients"""
        self.env['ir.config_parameter'].set_param('mail.catchall.domain','schlouby.fr')
        self.test_channel.write({'email_send':True})
        self.user_employee.write({'notification_type':'email'})

        #Subscribeanuserwithoutemail.Weshouldn'ttrytosendemailtothem.
        nomail=self.env['res.users'].create({
            "login":"nomail",
            "name":"NoMail",
            "email":False,
            "notification_type":"email",
        })
        self._join_channel(self.test_channel,self.user_employee.partner_id|self.test_partner|nomail.partner_id)
        withself.mock_mail_gateway():
            self.test_channel.message_post(body="Test",message_type='comment',subtype_xmlid='mail.mt_comment')
        self.assertSentEmail(self.test_channel.env.user.partner_id,[self.partner_employee,self.test_partner])

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_channel_chat_recipients(self):
        """Postingamessageonachatshouldnotsendemails"""
        self.env['ir.config_parameter'].set_param('mail.catchall.domain','schlouby.fr')
        self.test_channel.write({'email_send':False})
        self._join_channel(self.test_channel,self.user_employee.partner_id|self.test_partner)
        withself.mock_mail_gateway():
            self.test_channel.message_post(body="Test",message_type='comment',subtype_xmlid='mail.mt_comment')
        self.assertNotSentEmail()
        self.assertEqual(len(self._mails),0)

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_channel_classic_recipients(self):
        """Postingamessageonaclassicchannelshouldworklikeclassicpost"""
        self.test_channel.write({'alias_name':False})
        self.test_channel.message_subscribe([self.user_employee.partner_id.id,self.test_partner.id])
        withself.mock_mail_gateway():
            self.test_channel.message_post(body="Test",message_type='comment',subtype_xmlid='mail.mt_comment')
        self.assertSentEmail(self.test_channel.env.user.partner_id,[self.test_partner])

    deftest_channel_creation(self):
        """Auserthatcreateaprivatechannelshouldbeabletoreadit."""
        channel_form=Form(self.env['mail.channel'].with_user(self.user_employee))
        channel_form.name='Testprivatechannel'
        channel_form.public='private'
        channel=channel_form.save()
        self.assertEqual(channel.name,'Testprivatechannel','Mustbeabletoreadthecreatedchannel')

    deftest_channel_get(self):
        current_user=self.env['res.users'].create({
            "login":"adam",
            "name":"Jonas",
        })
        current_user=current_user.with_user(current_user)
        current_partner=current_user.partner_id
        other_partner=self.test_partner

        #`channel_get`shouldreturnanewchannelthefirsttimeapartnerisgiven
        initial_channel_info=current_user.env['mail.channel'].channel_get(partners_to=other_partner.ids)
        self.assertEqual(set(p['id']forpininitial_channel_info['members']),{current_partner.id,other_partner.id})

        #`channel_get`shouldreturntheexistingchanneleverytimethesamepartnerisgiven
        same_channel_info=current_user.env['mail.channel'].channel_get(partners_to=other_partner.ids)
        self.assertEqual(same_channel_info['id'],initial_channel_info['id'])

        #`channel_get`shouldreturntheexistingchannelwhenthecurrentpartnerisgiventogetherwiththeotherpartner
        together_channel_info=current_user.env['mail.channel'].channel_get(partners_to=(current_partner+other_partner).ids)
        self.assertEqual(together_channel_info['id'],initial_channel_info['id'])

        #`channel_get`shouldreturnanewchannelthefirsttimejustthecurrentpartnerisgiven,
        #evenifachannelcontainingthecurrentpartnertogetherwithotherpartnersalreadyexists
        solo_channel_info=current_user.env['mail.channel'].channel_get(partners_to=current_partner.ids)
        self.assertNotEqual(solo_channel_info['id'],initial_channel_info['id'])
        self.assertEqual(set(p['id']forpinsolo_channel_info['members']),{current_partner.id})

        #`channel_get`shouldreturntheexistingchanneleverytimethecurrentpartnerisgiven
        same_solo_channel_info=current_user.env['mail.channel'].channel_get(partners_to=current_partner.ids)
        self.assertEqual(same_solo_channel_info['id'],solo_channel_info['id'])

    deftest_channel_seen(self):
        """
        Incaseofconcurrentchannel_seenRPC,ensuretheoldestcallhasnoeffect.
        """
        self.test_channel.write({'channel_type':'chat'})
        self.test_channel.action_follow()
        msg_1=self._add_messages(self.test_channel,'Body1',author=self.user_employee.partner_id,
            channel_ids=[self.test_channel.id])
        msg_2=self._add_messages(self.test_channel,'Body2',author=self.user_employee.partner_id,
            channel_ids=[self.test_channel.id])
        ChannelAsUser=self.test_channel.with_user(self.user_employee).browse(self.test_channel.id)

        self.test_channel.channel_seen(msg_2.id)
        self.assertEqual(
            ChannelAsUser.channel_info()[0]['seen_partners_info'][0]['seen_message_id'],
            msg_2.id,
            "Lastmessageidshouldhavebeenupdated"
        )

        self.test_channel.channel_seen(msg_1.id)
        self.assertEqual(
            ChannelAsUser.channel_info()[0]['seen_partners_info'][0]['seen_message_id'],
            msg_2.id,
            "Lastmessageidshouldstaythesameaftermarkchannelasseenwithanoldermessage"
        )

    @mute_logger('flectra.models.unlink')
    deftest_channel_auto_unsubscribe_archived_or_deleted_users(self):
        """Archiving/deletingausershouldautomaticallyunsubscriberelatedpartnerfromprivatechannels"""
        test_channel_private=self.env['mail.channel'].with_context(self._test_context).create({
            'name':'Windencaves',
            'description':'Channeltotravelthroughtime',
            'public':'private',
        })
        test_channel_group=self.env['mail.channel'].with_context(self._test_context).create({
            'name':'SicMundus',
            'public':'groups',
            'group_public_id':self.env.ref('base.group_user').id})

        test_user=self.env['res.users'].create({
            "login":"adam",
            "name":"Jonas",
        })
        test_partner=test_user.partner_id
        test_chat=self.env['mail.channel'].with_context(self._test_context).create({
            'name':'test',
            'channel_type':'chat',
            'public':'private',
            'channel_partner_ids':[(4,self.user_employee.partner_id.id),(4,test_partner.id)],
        })

        self._join_channel(self.test_channel,self.user_employee.partner_id|test_partner)
        self._join_channel(test_channel_private,self.user_employee.partner_id|test_partner)
        self._join_channel(test_channel_group,self.user_employee.partner_id|test_partner)

        #Unsubscribearchiveduserfromtheprivatechannels,butnotfrompublicchannelsandnotfromchat
        self.user_employee.active=False
        self.assertEqual(test_channel_private.channel_partner_ids,test_partner)
        self.assertEqual(test_channel_group.channel_partner_ids,test_partner)
        self.assertEqual(self.test_channel.channel_partner_ids,self.user_employee.partner_id|test_partner)
        self.assertEqual(test_chat.channel_partner_ids,self.user_employee.partner_id|test_partner)

        #Unsubscribedeleteduserfromtheprivatechannels,butnotfrompublicchannelsandnotfromchat
        test_user.unlink()
        self.assertEqual(test_channel_private.channel_partner_ids,self.env['res.partner'])
        self.assertEqual(test_channel_group.channel_partner_ids,self.env['res.partner'])
        self.assertEqual(self.test_channel.channel_partner_ids,self.user_employee.partner_id|test_partner)
        self.assertEqual(test_chat.channel_partner_ids,self.user_employee.partner_id|test_partner)

    deftest_channel_unfollow_should_also_unsubscribe_the_partner(self):
        self.test_channel.message_subscribe(self.test_partner.ids)
        self.test_channel._action_unfollow(self.test_partner)

        self.assertFalse(self.test_channel.message_partner_ids)

    deftest_channel_unfollow_should_not_post_message_if_the_partner_has_been_removed(self):
        '''
        Whenapartnerleavesachannel,thesystemwillhelppostamessageunder
        thatpartner'snameinthechanneltonotifyothersif`email_sent`isset`False`.
        Themessageshouldonlybepostedwhenthepartnerisstillamemberofthechannel
        beforemethod`_action_unfollow()`iscalled.
        Ifthepartnerhasbeenremovedearlier,nomoremessageswillbeposted
        evenif`_action_unfollow()`iscalledagain.
        '''
        self.test_channel.write({'email_send':False})
        self._join_channel(self.test_channel,self.test_partner)
        self.test_channel.message_subscribe(self.partner_employee.ids)

        #amessageshouldbepostedtonotifyotherswhenapartnerisabouttoleave
        withself.assertSinglePostNotifications([{'partner':self.partner_employee,'type':'inbox'}],{
            'message_type':'notification',
            'subtype':'mail.mt_comment',
        }):
            self.test_channel._action_unfollow(self.test_partner)

        #nomoremessagesshouldbepostedifthepartnerhasbeenremovedbefore.
        withself.assertNoNotifications():
            self.test_channel._action_unfollow(self.test_partner)

    deftest_multi_company_chat(self):
        company_A=self.env['res.company'].create({'name':'CompanyA'})
        company_B=self.env['res.company'].create({'name':'CompanyB'})
        test_user_1=self.env['res.users'].create({
            'login':'user1',
            'name':'MyFirstNewUser',
            'company_ids':[(6,0,company_A.ids)],
            'company_id':company_A.id
        })
        test_user_2=self.env['res.users'].create({
            'login':'user2',
            'name':'MySecondNewUser',
            'company_ids':[(6,0,company_B.ids)],
            'company_id':company_B.id
        })
        initial_channel_info=self.env['mail.channel'].with_user(test_user_1).with_context(allowed_company_ids=company_A.ids).channel_get(test_user_2.partner_id.ids)
        self.assertTrue(initial_channel_info,'shouldbeabletochatwithmulticompanyuser')

    deftest_multi_company_message_post_notifications(self):
        company_1=self.company_admin
        company_2=self.env['res.company'].create({'name':'Company2'})

        #Company1andnotification_type=="inbox"
        user_1=self.user_employee

        #Company1andnotification_type=="email"
        user_2=self.user_admin
        user_2.notification_type='email'

        user_3=mail_new_test_user(
            self.env,login='user3',email='user3@example.com',groups='base.group_user',
            company_id=company_2.id,company_ids=[(6,0,company_2.ids)],
            name='user3',notification_type='inbox')

        user_4=mail_new_test_user(
            self.env,login='user4',email='user4@example.com',groups='base.group_user',
            company_id=company_2.id,company_ids=[(6,0,company_2.ids)],
            name='user4',notification_type='email')

        partner_without_user=self.env['res.partner'].create({
            'name':'Partner',
            'email':'partner_test_123@example.com',
        })
        mail_channel=self.env['mail.channel'].with_user(user_1).create({
            'name':'Channel',
            'channel_partner_ids':[
                (4,user_1.partner_id.id),
                (4,user_2.partner_id.id),
                (4,user_3.partner_id.id),
                (4,user_4.partner_id.id),
                (4,partner_without_user.id),
            ],
            'email_send':True,
        })

        mail_channel.invalidate_cache()
        (user_1|user_2|user_3|user_4).invalidate_cache()

        withself.mock_mail_gateway():
            mail_channel.with_user(user_1).with_company(company_1).message_post(
                body='Testbodymessage1337',
                channel_ids=mail_channel.ids,
            )

        self.assertSentEmail(user_1.partner_id,[user_2.partner_id])
        self.assertSentEmail(user_1.partner_id,[user_4.partner_id])
        self.assertEqual(len(self._mails),3,'Shouldhavesendonly3emailstouser2,user4andthepartner')

        self.assertBusNotifications([(self.cr.dbname,'mail.channel',mail_channel.id)])

        #Shouldnotcreatemailnotificationsforuser1&3
        self.assertFalse(self.env['mail.notification'].search([('res_partner_id','=',user_1.partner_id.id)]))
        self.assertFalse(self.env['mail.notification'].search([('res_partner_id','=',user_3.partner_id.id)]))

        #Shouldcreatemailnotificationsforuser2&4
        self.assertTrue(self.env['mail.notification'].search([('res_partner_id','=',user_2.partner_id.id)]))
        self.assertTrue(self.env['mail.notification'].search([('res_partner_id','=',user_4.partner_id.id)]))

        #Checkthatwedidnotsenda"channel_seen"notifications
        #fortheuserswhichreceivethenotificationsbyemail
        notification_seen_user_2=self.env['bus.bus'].search([('create_uid','=',user_2.id)])
        self.assertFalse(notification_seen_user_2,'Shouldnothavesentanotificationasuser2')
        notification_seen_user_4=self.env['bus.bus'].search([('create_uid','=',user_4.id)])
        self.assertFalse(notification_seen_user_4,'Shouldnothavesentanotificationasuser4')


@tagged('moderation','mail_channel')
classTestChannelModeration(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestChannelModeration,cls).setUpClass()

        cls.channel_1=cls.env['mail.channel'].create({
            'name':'Moderation_1',
            'email_send':True,
            'moderation':True,
            'channel_partner_ids':[(4,cls.partner_employee.id)],
            'moderator_ids':[(4,cls.user_employee.id)],
        })

        #ensureinitialdata
        cls.user_employee_2=mail_new_test_user(
            cls.env,login='employee2',groups='base.group_user',company_id=cls.company_admin.id,
            name='EnguerrandEmployee2',notification_type='inbox',signature='--\nEnguerrand'
        )
        cls.partner_employee_2=cls.user_employee_2.partner_id

        cls.user_portal=cls._create_portal_user()

    deftest_moderator_consistency(self):
        #moderatorsshouldbechannelmembers
        withself.assertRaises(ValidationError):
            self.channel_1.write({'moderator_ids':[(4,self.user_admin.id)]})

        #member->moderatoror
        self.channel_1.write({'channel_partner_ids':[(4,self.partner_admin.id)]})
        self.channel_1.write({'moderator_ids':[(4,self.user_admin.id)]})

        #member->moderatorkoifnoemail
        self.channel_1.write({'moderator_ids':[(3,self.partner_admin.id)]})
        self.user_admin.write({'email':False})
        withself.assertRaises(ValidationError):
            self.channel_1.write({'moderator_ids':[(4,self.user_admin.id)]})

    deftest_moderation_consistency(self):
        #moderationenabledchannelsarerestrictedtomailinglists
        withself.assertRaises(ValidationError):
            self.channel_1.write({'email_send':False})

        #moderationenabledchannelsshouldalwayshavemoderators
        withself.assertRaises(ValidationError):
            self.channel_1.write({'moderator_ids':[(5,0)]})

    deftest_moderation_count(self):
        self.assertEqual(self.channel_1.moderation_count,0)
        self.channel_1.write({'moderation_ids':[
            (0,0,{'email':'test0@example.com','status':'allow'}),
            (0,0,{'email':'test1@example.com','status':'ban'})
        ]})
        self.assertEqual(self.channel_1.moderation_count,2)

    @mute_logger('flectra.addons.mail.models.mail_channel','flectra.models.unlink')
    deftest_send_guidelines(self):
        self.channel_1.write({'channel_partner_ids':[(4,self.partner_portal.id),(4,self.partner_admin.id)]})
        self.channel_1._update_moderation_email([self.partner_admin.email],'ban')
        withself.mock_mail_gateway():
            self.channel_1.with_user(self.user_employee).send_guidelines()
        formailinself._new_mails:
            self.assertEqual(mail.author_id,self.partner_employee)
            self.assertEqual(mail.subject,'Guidelinesofchannel%s'%self.channel_1.name)
            self.assertEqual(mail.state,'outgoing')
            self.assertEqual(mail.email_from,self.user_employee.company_id.catchall_formatted)
        self.assertEqual(self._new_mails.mapped('recipient_ids'),self.partner_employee|self.partner_portal)

    deftest_send_guidelines_crash(self):
        self.channel_1.write({
            'channel_partner_ids':[(4,self.partner_admin.id)],
            'moderator_ids':[(4,self.user_admin.id),(3,self.user_employee.id)]
        })
        withself.assertRaises(UserError):
            self.channel_1.with_user(self.user_employee).send_guidelines()

    deftest_update_moderation_email(self):
        self.channel_1.write({'moderation_ids':[
            (0,0,{'email':'test0@example.com','status':'allow'}),
            (0,0,{'email':'test1@example.com','status':'ban'})
        ]})
        self.channel_1._update_moderation_email(['test0@example.com','test3@example.com'],'ban')
        self.assertEqual(len(self.channel_1.moderation_ids),3)
        self.assertTrue(all(status=='ban'forstatusinself.channel_1.moderation_ids.mapped('status')))

    deftest_moderation_reset(self):
        self.channel_2=self.env['mail.channel'].create({
            'name':'Moderation_1',
            'email_send':True,
            'moderation':True,
            'channel_partner_ids':[(4,self.partner_employee.id)],
            'moderator_ids':[(4,self.user_employee.id)],
        })

        self.msg_c1_1=self._add_messages(self.channel_1,'Body11',author=self.partner_admin,moderation_status='accepted')
        self.msg_c1_2=self._add_messages(self.channel_1,'Body12',author=self.partner_admin,moderation_status='pending_moderation')
        self.msg_c2_1=self._add_messages(self.channel_2,'Body21',author=self.partner_admin,moderation_status='pending_moderation')

        self.assertEqual(self.env['mail.message'].search_count([
            ('moderation_status','=','pending_moderation'),
            ('model','=','mail.channel'),('res_id','=',self.channel_1.id)
        ]),1)
        self.channel_1.write({'moderation':False})
        self.assertEqual(self.env['mail.message'].search_count([
            ('moderation_status','=','pending_moderation'),
            ('model','=','mail.channel'),('res_id','=',self.channel_1.id)
        ]),0)
        self.assertEqual(self.env['mail.message'].search_count([
            ('moderation_status','=','pending_moderation'),
            ('model','=','mail.channel'),('res_id','=',self.channel_2.id)
        ]),1)
        self.channel_2.write({'moderation':False})
        self.assertEqual(self.env['mail.message'].search_count([
            ('moderation_status','=','pending_moderation'),
            ('model','=','mail.channel'),('res_id','=',self.channel_2.id)
        ]),0)

    @mute_logger('flectra.models.unlink')
    deftest_message_post(self):
        email1='test0@example.com'
        email2='test1@example.com'

        self.channel_1._update_moderation_email([email1],'ban')
        self.channel_1._update_moderation_email([email2],'allow')

        msg_admin=self.channel_1.message_post(message_type='email',subtype_xmlid='mail.mt_comment',author_id=self.partner_admin.id)
        msg_moderator=self.channel_1.message_post(message_type='comment',subtype_xmlid='mail.mt_comment',author_id=self.partner_employee.id)
        msg_email1=self.channel_1.message_post(message_type='comment',subtype_xmlid='mail.mt_comment',email_from=formataddr(("MyName",email1)))
        msg_email2=self.channel_1.message_post(message_type='email',subtype_xmlid='mail.mt_comment',email_from=email2)
        msg_notif=self.channel_1.message_post()

        messages=self.env['mail.message'].search([('model','=','mail.channel'),('res_id','=',self.channel_1.id)])
        pending_messages=messages.filtered(lambdam:m.moderation_status=='pending_moderation')
        accepted_messages=messages.filtered(lambdam:m.moderation_status=='accepted')

        self.assertFalse(msg_email1)
        self.assertEqual(msg_admin,pending_messages)
        self.assertEqual(accepted_messages,msg_moderator|msg_email2|msg_notif)
        self.assertFalse(msg_admin.channel_ids)
        self.assertEqual(msg_email2.channel_ids,self.channel_1)

    deftest_user_is_moderator(self):
        self.assertTrue(self.user_employee.is_moderator)
        self.assertFalse(self.user_employee_2.is_moderator)
        self.channel_1.write({
            'channel_partner_ids':[(4,self.partner_employee_2.id)],
            'moderator_ids':[(4,self.user_employee_2.id)],
        })
        self.assertTrue(self.user_employee_2.is_moderator)

    deftest_user_moderation_counter(self):
        self._add_messages(self.channel_1,'B',moderation_status='pending_moderation',author=self.partner_employee_2)
        self._add_messages(self.channel_1,'B',moderation_status='accepted',author=self.partner_employee_2)
        self._add_messages(self.channel_1,'B',moderation_status='accepted',author=self.partner_employee)
        self._add_messages(self.channel_1,'B',moderation_status='pending_moderation',author=self.partner_employee)
        self._add_messages(self.channel_1,'B',moderation_status='accepted',author=self.partner_employee)

        self.assertEqual(self.user_employee.moderation_counter,2)
        self.assertEqual(self.user_employee_2.moderation_counter,0)

        self.channel_1.write({
            'channel_partner_ids':[(4,self.partner_employee_2.id)],
            'moderator_ids':[(4,self.user_employee_2.id)]
        })
        self.assertEqual(self.user_employee.moderation_counter,2)
        self.assertEqual(self.user_employee_2.moderation_counter,0)
