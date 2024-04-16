#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
fromunittest.mockimportpatch

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.addons.test_mail.models.test_mail_modelsimportMailTestSimple
fromflectra.exceptionsimportAccessError
fromflectra.toolsimportmute_logger,formataddr
fromflectra.testsimporttagged,users


@tagged('mail_message')
classTestMessageValues(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMessageValues,cls).setUpClass()

        cls._init_mail_gateway()
        cls.alias_record=cls.env['mail.test.container'].with_context(cls._test_context).create({
            'name':'Pigs',
            'alias_name':'pigs',
            'alias_contact':'followers',
        })
        cls.Message=cls.env['mail.message'].with_user(cls.user_employee)

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_format(self):
        record1=self.env['mail.test.simple'].create({'name':'Test1'})
        message=self.env['mail.message'].create([{
            'model':'mail.test.simple',
            'res_id':record1.id,
        }])
        res=message.message_format()
        self.assertEqual(res[0].get('record_name'),'Test1')

        record1.write({"name":"Test2"})
        res=message.message_format()
        self.assertEqual(res[0].get('record_name'),'Test2')

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_format_access(self):
        """
        Userthatdoesn'thaveaccesstoarecordshouldstillbeabletofetch
        therecord_nameinsidemessage_format.
        """
        company_2=self.env['res.company'].create({'name':'SecondTestCompany'})
        record1=self.env['mail.test.multi.company'].create({
            'name':'Test1',
            'company_id':company_2.id,
        })
        message=record1.message_post(body='',partner_ids=[self.user_employee.partner_id.id])
        #WeneedtoflushandinvalidatetheORMcachesincetherecord_name
        #isalreadycachedfromthecreation.Otherwiseitwillleakinside
        #message_format.
        message.flush()
        message.invalidate_cache()
        res=message.with_user(self.user_employee).message_format()
        self.assertEqual(res[0].get('record_name'),'Test1')

    deftest_mail_message_values_body_base64_image(self):
        msg=self.env['mail.message'].with_user(self.user_employee).create({
            'body':'taratata<imgsrc="data:image/png;base64,iV/+OkI="width="2"><imgsrc="data:image/png;base64,iV/+OkI="width="2">',
        })
        self.assertEqual(len(msg.attachment_ids),1)
        self.assertEqual(
            msg.body,
            '<p>taratata<imgsrc="/web/image/{attachment.id}?access_token={attachment.access_token}"alt="image0"width="2">'
            '<imgsrc="/web/image/{attachment.id}?access_token={attachment.access_token}"alt="image0"width="2"></p>'.format(attachment=msg.attachment_ids[0])
        )

    @mute_logger('flectra.models.unlink')
    @users('employee')
    deftest_mail_message_values_fromto_long_name(self):
        """Longheadersmaybreakinpythonifabove78charsasfoldingisnot
        donecorrectly(see``_notify_get_reply_to_formatted_email``docstring
        +commitlinkedtothistest)."""
        #namewouldmakeitblowup:keeponlyemail
        test_record=self.env['mail.test.container'].browse(self.alias_record.ids)
        test_record.write({
            'name':'SuperLongNameThatPeopleMayEnter"Evenwithaninternalquotingofstuff"'
        })
        msg=self.env['mail.message'].create({
            'model':test_record._name,
            'res_id':test_record.id
        })
        reply_to_email=f"{test_record.alias_name}@{self.alias_domain}"
        self.assertEqual(msg.reply_to,reply_to_email,
                         'Reply-To:useonlyemailwhenformataddr>78chars')

        #name+company_namewouldmakeitblowup:keeprecord_nameinformatting
        test_record.write({'name':'Namethatwouldbemorethan78withcompanyname'})
        msg=self.env['mail.message'].create({
            'model':test_record._name,
            'res_id':test_record.id
        })
        self.assertEqual(msg.reply_to,formataddr((test_record.name,reply_to_email)),
                         'Reply-To:userecordnameasnameinformatifrecordname+company>78chars')

        #norecord_name:keepcompany_nameinformattingifok
        test_record.write({'name':''})
        msg=self.env['mail.message'].create({
            'model':test_record._name,
            'res_id':test_record.id
        })
        self.assertEqual(msg.reply_to,formataddr((self.env.user.company_id.name,reply_to_email)),
                         'Reply-To:usecompanyasnameinformatwhennorecordnameandstill<78chars')

        #norecord_nameandcompany_namemakeitblowup:keeponlyemail
        self.env.user.company_id.write({'name':'SuperLongNameThatPeopleMayEnter"Evenwithaninternalquotingofstuff"'})
        msg=self.env['mail.message'].create({
            'model':test_record._name,
            'res_id':test_record.id
        })
        self.assertEqual(msg.reply_to,reply_to_email,
                         'Reply-To:useonlyemailwhenformataddr>78chars')

        #whatevertherecordandcompanynames,emailistoolong:keeponlyemail
        test_record.write({
            'alias_name':'Waaaaytoolongaliasnamethatshouldmakeanyreply-toblowthe78characterslimit',
            'name':'Short',
        })
        self.env.user.company_id.write({'name':'Comp'})
        sanitized_alias_name='waaaay-too-long-alias-name-that-should-make-any-reply-to-blow-the-78-characters-limit'
        msg=self.env['mail.message'].create({
            'model':test_record._name,
            'res_id':test_record.id
        })
        self.assertEqual(msg.reply_to,f"{sanitized_alias_name}@{self.alias_domain}",
                         'Reply-To:evenalongemailisokasonlyformataddrisproblematic')

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_values_fromto_no_document_values(self):
        msg=self.Message.create({
            'reply_to':'test.reply@example.com',
            'email_from':'test.from@example.com',
        })
        self.assertIn('-private',msg.message_id.split('@')[0],'mail_message:message_idforavoidmessageshouldbea"private"one')
        self.assertEqual(msg.reply_to,'test.reply@example.com')
        self.assertEqual(msg.email_from,'test.from@example.com')

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_values_fromto_no_document(self):
        msg=self.Message.create({})
        self.assertIn('-private',msg.message_id.split('@')[0],'mail_message:message_idforavoidmessageshouldbea"private"one')
        reply_to_name=self.env.user.company_id.name
        reply_to_email='%s@%s'%(self.alias_catchall,self.alias_domain)
        self.assertEqual(msg.reply_to,formataddr((reply_to_name,reply_to_email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

        #noaliasdomain->author
        self.env['ir.config_parameter'].search([('key','=','mail.catchall.domain')]).unlink()

        msg=self.Message.create({})
        self.assertIn('-private',msg.message_id.split('@')[0],'mail_message:message_idforavoidmessageshouldbea"private"one')
        self.assertEqual(msg.reply_to,formataddr((self.user_employee.name,self.user_employee.email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

        #noaliascatchall,noalias->author
        self.env['ir.config_parameter'].set_param('mail.catchall.domain',self.alias_domain)
        self.env['ir.config_parameter'].search([('key','=','mail.catchall.alias')]).unlink()

        msg=self.Message.create({})
        self.assertIn('-private',msg.message_id.split('@')[0],'mail_message:message_idforavoidmessageshouldbea"private"one')
        self.assertEqual(msg.reply_to,formataddr((self.user_employee.name,self.user_employee.email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_values_fromto_document_alias(self):
        msg=self.Message.create({
            'model':'mail.test.container',
            'res_id':self.alias_record.id
        })
        self.assertIn('-openerp-%d-mail.test'%self.alias_record.id,msg.message_id.split('@')[0])
        reply_to_name='%s%s'%(self.env.user.company_id.name,self.alias_record.name)
        reply_to_email='%s@%s'%(self.alias_record.alias_name,self.alias_domain)
        self.assertEqual(msg.reply_to,formataddr((reply_to_name,reply_to_email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

        #noaliasdomain->author
        self.env['ir.config_parameter'].search([('key','=','mail.catchall.domain')]).unlink()

        msg=self.Message.create({
            'model':'mail.test.container',
            'res_id':self.alias_record.id
        })
        self.assertIn('-openerp-%d-mail.test'%self.alias_record.id,msg.message_id.split('@')[0])
        self.assertEqual(msg.reply_to,formataddr((self.user_employee.name,self.user_employee.email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

        #nocatchall->don'tcare,alias
        self.env['ir.config_parameter'].set_param('mail.catchall.domain',self.alias_domain)
        self.env['ir.config_parameter'].search([('key','=','mail.catchall.alias')]).unlink()

        msg=self.Message.create({
            'model':'mail.test.container',
            'res_id':self.alias_record.id
        })
        self.assertIn('-openerp-%d-mail.test'%self.alias_record.id,msg.message_id.split('@')[0])
        reply_to_name='%s%s'%(self.env.company.name,self.alias_record.name)
        reply_to_email='%s@%s'%(self.alias_record.alias_name,self.alias_domain)
        self.assertEqual(msg.reply_to,formataddr((reply_to_name,reply_to_email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_values_fromto_document_no_alias(self):
        test_record=self.env['mail.test.simple'].create({'name':'Test','email_from':'ignasse@example.com'})

        msg=self.Message.create({
            'model':'mail.test.simple',
            'res_id':test_record.id
        })
        self.assertIn('-openerp-%d-mail.test.simple'%test_record.id,msg.message_id.split('@')[0])
        reply_to_name='%s%s'%(self.env.user.company_id.name,test_record.name)
        reply_to_email='%s@%s'%(self.alias_catchall,self.alias_domain)
        self.assertEqual(msg.reply_to,formataddr((reply_to_name,reply_to_email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_values_fromto_document_manual_alias(self):
        test_record=self.env['mail.test.simple'].create({'name':'Test','email_from':'ignasse@example.com'})
        alias=self.env['mail.alias'].create({
            'alias_name':'MegaLias',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.simple').id,
            'alias_parent_model_id':self.env['ir.model']._get('mail.test.simple').id,
            'alias_parent_thread_id':test_record.id,
        })

        msg=self.Message.create({
            'model':'mail.test.simple',
            'res_id':test_record.id
        })

        self.assertIn('-openerp-%d-mail.test.simple'%test_record.id,msg.message_id.split('@')[0])
        reply_to_name='%s%s'%(self.env.user.company_id.name,test_record.name)
        reply_to_email='%s@%s'%(alias.alias_name,self.alias_domain)
        self.assertEqual(msg.reply_to,formataddr((reply_to_name,reply_to_email)))
        self.assertEqual(msg.email_from,formataddr((self.user_employee.name,self.user_employee.email)))

    deftest_mail_message_values_fromto_no_auto_thread(self):
        msg=self.Message.create({
            'model':'mail.test.container',
            'res_id':self.alias_record.id,
            'no_auto_thread':True,
        })
        self.assertIn('reply_to',msg.message_id.split('@')[0])
        self.assertNotIn('mail.test.container',msg.message_id.split('@')[0])
        self.assertNotIn('-%d-'%self.alias_record.id,msg.message_id.split('@')[0])


@tagged('mail_message')
classTestMessageAccess(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMessageAccess,cls).setUpClass()

        cls.user_public=mail_new_test_user(cls.env,login='bert',groups='base.group_public',name='BertTartignole')
        cls.user_portal=mail_new_test_user(cls.env,login='chell',groups='base.group_portal',name='ChellGladys')

        Channel=cls.env['mail.channel'].with_context(cls._test_context)
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
        #Private:privategtroup
        cls.group_private=Channel.create({
            'name':'Private',
            'public':'private'})
        cls.message=cls.env['mail.message'].create({
            'body':'MyBody',
            'model':'mail.channel',
            'res_id':cls.group_private.id,
        })

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_message_access_search(self):
        #Data:variousauthor_ids,partner_ids,documents
        msg1=self.env['mail.message'].create({
            'subject':'_ZTest','body':'A','subtype_id':self.ref('mail.mt_comment')})
        msg2=self.env['mail.message'].create({
            'subject':'_ZTest','body':'A+B','subtype_id':self.ref('mail.mt_comment'),
            'partner_ids':[(6,0,[self.user_public.partner_id.id])]})
        msg3=self.env['mail.message'].create({
            'subject':'_ZTest','body':'APigs','subtype_id':False,
            'model':'mail.channel','res_id':self.group_pigs.id})
        msg4=self.env['mail.message'].create({
            'subject':'_ZTest','body':'A+PPigs','subtype_id':self.ref('mail.mt_comment'),
            'model':'mail.channel','res_id':self.group_pigs.id,
            'partner_ids':[(6,0,[self.user_public.partner_id.id])]})
        msg5=self.env['mail.message'].create({
            'subject':'_ZTest','body':'A+EPigs','subtype_id':self.ref('mail.mt_comment'),
            'model':'mail.channel','res_id':self.group_pigs.id,
            'partner_ids':[(6,0,[self.user_employee.partner_id.id])]})
        msg6=self.env['mail.message'].create({
            'subject':'_ZTest','body':'ABirds','subtype_id':self.ref('mail.mt_comment'),
            'model':'mail.channel','res_id':self.group_private.id})
        msg7=self.env['mail.message'].with_user(self.user_employee).create({
            'subject':'_ZTest','body':'B','subtype_id':self.ref('mail.mt_comment')})
        msg8=self.env['mail.message'].with_user(self.user_employee).create({
            'subject':'_ZTest','body':'B+E','subtype_id':self.ref('mail.mt_comment'),
            'partner_ids':[(6,0,[self.user_employee.partner_id.id])]})

        #Test:Public:2messages(recipient)
        messages=self.env['mail.message'].with_user(self.user_public).search([('subject','like','_ZTest')])
        self.assertEqual(messages,msg2|msg4)

        #Test:Employee:3messagesonPigsRaoulcanread(employeecanreadgroupwithdefaultvalues)
        messages=self.env['mail.message'].with_user(self.user_employee).search([('subject','like','_ZTest'),('body','ilike','A')])
        self.assertEqual(messages,msg3|msg4|msg5)

        #Test:Raoul:3messagesonPigsRaoulcanread(employeecanreadgroupwithdefaultvalues),0onBirds(privategroup)+2messagesasauthor
        messages=self.env['mail.message'].with_user(self.user_employee).search([('subject','like','_ZTest')])
        self.assertEqual(messages,msg3|msg4|msg5|msg7|msg8)

        #Test:Admin:allmessages
        messages=self.env['mail.message'].search([('subject','like','_ZTest')])
        self.assertEqual(messages,msg1|msg2|msg3|msg4|msg5|msg6|msg7|msg8)

        #Test:Portal:0(noaccesstogroups,notrecipient)
        messages=self.env['mail.message'].with_user(self.user_portal).search([('subject','like','_ZTest')])
        self.assertFalse(messages)

        #Test:Portal:2messages(publicgroupwithasubtype)
        self.group_pigs.write({'public':'public'})
        messages=self.env['mail.message'].with_user(self.user_portal).search([('subject','like','_ZTest')])
        self.assertEqual(messages,msg4|msg5)

    #--------------------------------------------------
    #READ
    #--------------------------------------------------

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_mail_message_access_read_crash(self):
        withself.assertRaises(AccessError):
            self.message.with_user(self.user_employee).read()

    @mute_logger('flectra.models')
    deftest_mail_message_access_read_crash_portal(self):
        withself.assertRaises(AccessError):
            self.message.with_user(self.user_portal).read(['body','message_type','subtype_id'])

    deftest_mail_message_access_read_ok_portal(self):
        self.message.write({'subtype_id':self.ref('mail.mt_comment'),'res_id':self.group_public.id})
        self.message.with_user(self.user_portal).read(['body','message_type','subtype_id'])

    deftest_mail_message_access_read_notification(self):
        attachment=self.env['ir.attachment'].create({
            'datas':base64.b64encode(b'Myattachment'),
            'name':'doc.txt',
            'res_model':self.message._name,
            'res_id':self.message.id})
        #attachtheattachmenttothemessage
        self.message.write({'attachment_ids':[(4,attachment.id)]})
        self.message.write({'partner_ids':[(4,self.user_employee.partner_id.id)]})
        self.message.with_user(self.user_employee).read()
        #Test:Berthasaccesstoattachment,okbecausehecanreadmessage
        attachment.with_user(self.user_employee).read(['name','datas'])

    deftest_mail_message_access_read_author(self):
        self.message.write({'author_id':self.user_employee.partner_id.id})
        self.message.with_user(self.user_employee).read()

    deftest_mail_message_access_read_doc(self):
        self.message.write({'model':'mail.channel','res_id':self.group_public.id})
        #Test:Bertreadsthemessage,okbecauselinkedtoadocheisallowedtoread
        self.message.with_user(self.user_employee).read()

    deftest_mail_message_access_read_crash_moderation(self):
        #withself.assertRaises(AccessError):
        self.message.write({'model':'mail.channel','res_id':self.group_public.id,'moderation_status':'pending_moderation'})
        #Test:Bertreadsthemessage,okbecauselinkedtoadocheisallowedtoread
        self.message.with_user(self.user_employee).read()

    #--------------------------------------------------
    #CREATE
    #--------------------------------------------------

    @mute_logger('flectra.addons.base.models.ir_model')
    deftest_mail_message_access_create_crash_public(self):
        #Do:BertcreatesamessageonPigs->ko,nocreationrights
        withself.assertRaises(AccessError):
            self.env['mail.message'].with_user(self.user_public).create({'model':'mail.channel','res_id':self.group_pigs.id,'body':'Test'})

        #Do:BertcreateamessageonJobs->ko,nocreationrights
        withself.assertRaises(AccessError):
            self.env['mail.message'].with_user(self.user_public).create({'model':'mail.channel','res_id':self.group_public.id,'body':'Test'})

    @mute_logger('flectra.models')
    deftest_mail_message_access_create_crash(self):
        #Do:Bertcreateaprivatemessage->ko,nocreationrights
        withself.assertRaises(AccessError):
            self.env['mail.message'].with_user(self.user_employee).create({'model':'mail.channel','res_id':self.group_private.id,'body':'Test'})

    @mute_logger('flectra.models')
    deftest_mail_message_access_create_doc(self):
        Message=self.env['mail.message'].with_user(self.user_employee)
        #Do:RaoulcreatesamessageonJobs->ok,writeaccesstotherelateddocument
        Message.create({'model':'mail.channel','res_id':self.group_public.id,'body':'Test'})
        #Do:RaoulcreatesamessageonPriv->ko,nowriteaccesstotherelateddocument
        withself.assertRaises(AccessError):
            Message.create({'model':'mail.channel','res_id':self.group_private.id,'body':'Test'})

    deftest_mail_message_access_create_private(self):
        self.env['mail.message'].with_user(self.user_employee).create({'body':'Test'})

    deftest_mail_message_access_create_reply(self):
        #TDEFIXME:shoulditreallywork?notsure-catchallmakescrash(aka,postwillcrashalso)
        self.env['ir.config_parameter'].set_param('mail.catchall.domain',False)
        self.message.write({'partner_ids':[(4,self.user_employee.partner_id.id)]})
        self.env['mail.message'].with_user(self.user_employee).create({'model':'mail.channel','res_id':self.group_private.id,'body':'Test','parent_id':self.message.id})

    deftest_mail_message_access_create_wo_parent_access(self):
        """Purposeistotestpostingamessageonarecordwhosefirstmessage/parent
        isnotaccessiblebycurrentuser."""
        test_record=self.env['mail.test.simple'].with_context(self._test_context).create({'name':'Test','email_from':'ignasse@example.com'})
        partner_1=self.env['res.partner'].create({
            'name':'JitendraPrajapati(jpr-flectra)',
            'email':'jpr@flectrahq.com',
        })
        test_record.message_subscribe((partner_1|self.user_admin.partner_id).ids)

        message=test_record.message_post(
            body='<p>ThisisFirstMessage</p>',subject='Subject',
            message_type='comment',subtype_xmlid='mail.mt_note')
        #portaluserhavenorightstoreadthemessage
        withself.assertRaises(AccessError):
            message.with_user(self.user_portal).read(['subject,body'])

        withpatch.object(MailTestSimple,'check_access_rights',return_value=True):
            withself.assertRaises(AccessError):
                message.with_user(self.user_portal).read(['subject,body'])

            #parentmessageisaccessibletoreferencesnotificationmailvalues
            #for_notifymethodandportaluserhavenorightstosendthemessageforthismodel
            new_msg=test_record.with_user(self.user_portal).message_post(
                body='<p>ThisisSecondMessage</p>',
                subject='Subject',
                parent_id=message.id,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                mail_auto_delete=False)

        new_mail=self.env['mail.mail'].sudo().search([
            ('mail_message_id','=',new_msg.id),
            ('references','=',f'{message.message_id}{new_msg.message_id}'),
        ])

        self.assertTrue(new_mail)
        self.assertEqual(new_msg.parent_id,message)

    #--------------------------------------------------
    #WRITE
    #--------------------------------------------------

    deftest_mail_message_access_write_moderation(self):
        """Onlymoderatorscanmodifypendingmessages"""
        self.group_public.write({
            'email_send':True,
            'moderation':True,
            'channel_partner_ids':[(4,self.partner_employee.id)],
            'moderator_ids':[(4,self.user_employee.id)],
        })
        self.message.write({'model':'mail.channel','res_id':self.group_public.id,'moderation_status':'pending_moderation'})
        self.message.with_user(self.user_employee).write({'moderation_status':'accepted'})

    deftest_mail_message_access_write_crash_moderation(self):
        self.message.write({'model':'mail.channel','res_id':self.group_public.id,'moderation_status':'pending_moderation'})
        withself.assertRaises(AccessError):
            self.message.with_user(self.user_employee).write({'moderation_status':'accepted'})

    @mute_logger('openerp.addons.mail.models.mail_mail')
    deftest_mark_all_as_read(self):
        self.user_employee.notification_type='inbox'
        emp_partner=self.user_employee.partner_id.with_user(self.user_employee)

        group_private=self.env['mail.channel'].with_context({
            'mail_create_nolog':True,
            'mail_create_nosubscribe':True,
            'mail_channel_noautofollow':True,
        }).create({
            'name':'Private',
            'description':'PrivateJamesR.',
            'public':'private',
            'alias_name':'private',
            'alias_contact':'followers'}
        ).with_context({'mail_create_nosubscribe':False})

        #markallasreadclearneedactions
        msg1=group_private.message_post(body='Test',message_type='comment',subtype_xmlid='mail.mt_comment',partner_ids=[emp_partner.id])
        self._reset_bus()
        emp_partner.env['mail.message'].mark_all_as_read(domain=[])
        self.assertBusNotifications([(self.cr.dbname,'res.partner',emp_partner.id)],[{'type':'mark_as_read','message_ids':[msg1.id],'needaction_inbox_counter':0}])
        na_count=emp_partner.get_needaction_count()
        self.assertEqual(na_count,0,"markallasreadshouldconcludeallneedactions")

        #markallasreadalsoclearinaccessibleneedactions
        msg2=group_private.message_post(body='Zest',message_type='comment',subtype_xmlid='mail.mt_comment',partner_ids=[emp_partner.id])
        needaction_accessible=len(emp_partner.env['mail.message'].search([['needaction','=',True]]))
        self.assertEqual(needaction_accessible,1,"anewmessagetoapartnerisreadabletothatpartner")

        msg2.sudo().partner_ids=self.env['res.partner']
        emp_partner.env['mail.message'].search([['needaction','=',True]])
        needaction_length=len(emp_partner.env['mail.message'].search([['needaction','=',True]]))
        self.assertEqual(needaction_length,1,"messageshouldstillbereadablewhennotified")

        na_count=emp_partner.get_needaction_count()
        self.assertEqual(na_count,1,"messagenotaccessibleiscurrentlystillcounted")

        self._reset_bus()
        emp_partner.env['mail.message'].mark_all_as_read(domain=[])
        self.assertBusNotifications([(self.cr.dbname,'res.partner',emp_partner.id)],[{'type':'mark_as_read','message_ids':[msg2.id],'needaction_inbox_counter':0}])
        na_count=emp_partner.get_needaction_count()
        self.assertEqual(na_count,0,"markallreadshouldconcludeallneedactionseveninacessibleones")

    @mute_logger('openerp.addons.mail.models.mail_mail')
    deftest_mark_all_as_read_share(self):
        self.user_portal.notification_type='inbox'
        portal_partner=self.user_portal.partner_id.with_user(self.user_portal)

        #markallasreadclearneedactions
        self.group_pigs.message_post(body='Test',message_type='comment',subtype_xmlid='mail.mt_comment',partner_ids=[portal_partner.id])
        portal_partner.env['mail.message'].mark_all_as_read(domain=[])
        na_count=portal_partner.get_needaction_count()
        self.assertEqual(na_count,0,"markallasreadshouldconcludeallneedactions")

        #markallasreadalsoclearinaccessibleneedactions
        new_msg=self.group_pigs.message_post(body='Zest',message_type='comment',subtype_xmlid='mail.mt_comment',partner_ids=[portal_partner.id])
        needaction_accessible=len(portal_partner.env['mail.message'].search([['needaction','=',True]]))
        self.assertEqual(needaction_accessible,1,"anewmessagetoapartnerisreadabletothatpartner")

        new_msg.sudo().partner_ids=self.env['res.partner']
        needaction_length=len(portal_partner.env['mail.message'].search([['needaction','=',True]]))
        self.assertEqual(needaction_length,1,"messageshouldstillbereadablewhennotified")

        na_count=portal_partner.get_needaction_count()
        self.assertEqual(na_count,1,"messagenotaccessibleiscurrentlystillcounted")

        portal_partner.env['mail.message'].mark_all_as_read(domain=[])
        na_count=portal_partner.get_needaction_count()
        self.assertEqual(na_count,0,"markallreadshouldconcludeallneedactionseveninacessibleones")


@tagged('moderation')
classTestMessageModeration(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMessageModeration,cls).setUpClass()

        cls.channel_1=cls.env['mail.channel'].create({
            'name':'Moderation_1',
            'email_send':True,
            'moderation':True
        })
        cls.user_employee.write({'moderation_channel_ids':[(6,0,[cls.channel_1.id])]})
        cls.user_portal=cls._create_portal_user()

        #Apendingmoderationmessageneedstohavefieldchannel_idsempty.Moderators
        #needtobeabletonotifyapendingmoderationmessage(inachanneltheymoderate).
        cls.msg_c1_admin1=cls._add_messages(cls.channel_1,'Body11',author=cls.partner_admin,moderation_status='pending_moderation')
        cls.msg_c1_admin2=cls._add_messages(cls.channel_1,'Body12',author=cls.partner_admin,moderation_status='pending_moderation')
        cls.msg_c1_portal=cls._add_messages(cls.channel_1,'Body21',author=cls.partner_portal,moderation_status='pending_moderation')

    @mute_logger('flectra.models.unlink')
    deftest_moderate_accept(self):
        self._reset_bus()
        self.assertFalse(self.msg_c1_admin1.channel_ids|self.msg_c1_admin2.channel_ids|self.msg_c1_portal.channel_ids)

        self.msg_c1_admin1.with_user(self.user_employee)._moderate('accept')
        self.assertEqual(self.msg_c1_admin1.channel_ids,self.channel_1)
        self.assertEqual(self.msg_c1_admin1.moderation_status,'accepted')
        self.assertEqual(self.msg_c1_admin2.moderation_status,'pending_moderation')
        self.assertBusNotifications([(self.cr.dbname,'mail.channel',self.channel_1.id)])

    @mute_logger('flectra.models.unlink')
    deftest_moderate_allow(self):
        self._reset_bus()

        self.msg_c1_admin1.with_user(self.user_employee)._moderate('allow')
        self.assertEqual(self.msg_c1_admin1.channel_ids,self.channel_1)
        self.assertEqual(self.msg_c1_admin2.channel_ids,self.channel_1)
        self.assertEqual(self.msg_c1_admin1.moderation_status,'accepted')
        self.assertEqual(self.msg_c1_admin2.moderation_status,'accepted')
        self.assertBusNotifications([
            (self.cr.dbname,'mail.channel',self.channel_1.id),
            (self.cr.dbname,'mail.channel',self.channel_1.id)])

    @mute_logger('flectra.models.unlink')
    deftest_moderate_reject(self):
        withself.mock_mail_gateway():
            (self.msg_c1_admin1|self.msg_c1_portal).with_user(self.user_employee)._moderate_send_reject_email('Title','Messagetoauthor')
            self.assertEqual(len(self._new_mails),2)
        formailinself._new_mails:
            self.assertEqual(mail.author_id,self.partner_employee)
            self.assertEqual(mail.subject,'Title')
            self.assertEqual(mail.state,'outgoing')
        self.assertEqual(
            set(self._new_mails.mapped('email_to')),
            set([self.msg_c1_admin1.email_from,self.msg_c1_portal.email_from])
        )
        self.assertEqual(
            set(self._new_mails.mapped('body_html')),
            set(['<div>Messagetoauthor</div>\n%s\n'%self.msg_c1_admin1.body,'<div>Messagetoauthor</div>\n%s\n'%self.msg_c1_portal.body])
        ) #TDEnote:\nareaddedbyappendcontenttohtml,becausewhynot

    @mute_logger('flectra.models.unlink')
    deftest_moderate_discard(self):
        self._reset_bus()
        id1,id2,id3=self.msg_c1_admin1.id,self.msg_c1_admin2.id,self.msg_c1_portal.id #saveidsbecauseunlinkwilldiscardthem
        (self.msg_c1_admin1|self.msg_c1_admin2|self.msg_c1_portal).with_user(self.user_employee)._moderate_discard()

        self.assertBusNotifications(
            [(self.cr.dbname,'res.partner',self.partner_admin.id),
             (self.cr.dbname,'res.partner',self.partner_employee.id),
             (self.cr.dbname,'res.partner',self.partner_portal.id)],
            [{'type':'deletion','message_ids':[id1,id2]}, #authorof2messages
             {'type':'deletion','message_ids':[id1,id2,id3]}, #moderator
             {'type':'deletion','message_ids':[id3]}] #authorof1message
        )

    @mute_logger('flectra.models.unlink')
    deftest_notify_moderators(self):
        #creatependingmessagesinanotherchanneltohavetwonotificationtopush
        channel_2=self.env['mail.channel'].create({
            'name':'Moderation_1',
            'email_send':True,
            'moderation':True
        })
        self.user_admin.write({'moderation_channel_ids':[(6,0,[channel_2.id])]})
        self.msg_c2_portal=self._add_messages(channel_2,'Body31',author=self.partner_portal,moderation_status='pending_moderation')

        #onenotificationforeachmoderator:employee(channel1),admin(channel2)
        withself.assertPostNotifications([{
            'content':'Hello%s'%self.partner_employee.name,
            'message_type':'user_notification','subtype':'mail.mt_note',
            'notif':[{
                'partner':self.partner_employee,
                'type':'inbox'}]
        },{
            'content':'Hello%s'%self.partner_admin.name,
            'message_type':'user_notification','subtype':'mail.mt_note',
            'notif':[{
                'partner':self.partner_admin,
                'type':'inbox'}]
        }]):
            self.env['mail.message']._notify_moderators()
