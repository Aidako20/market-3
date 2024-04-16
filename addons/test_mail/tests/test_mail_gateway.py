#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importsocket

fromunittest.mockimportDEFAULT
fromunittest.mockimportpatch

fromflectraimportexceptions
fromflectra.addons.mail.models.mail_threadimportMailThread
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.test_mail.dataimporttest_mail_data
fromflectra.addons.test_mail.data.test_mail_dataimportMAIL_TEMPLATE
fromflectra.addons.test_mail.models.test_mail_modelsimportMailTestGateway
fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportusers
fromflectra.toolsimportemail_split_and_format,formataddr,mute_logger


@tagged('mail_gateway')
classTestEmailParsing(TestMailCommon):

    deftest_message_parse_and_replace_binary_octetstream(self):
        """IncomingemailcontainingawrongContent-TypeasdescribedinRFC2046/section-3"""
        received_mail=self.from_string(test_mail_data.MAIL_MULTIPART_BINARY_OCTET_STREAM)
        withself.assertLogs('flectra.addons.mail.models.mail_thread',level="WARNING")ascapture:
            extracted_mail=self.env['mail.thread']._message_parse_extract_payload(received_mail)

        self.assertEqual(len(extracted_mail['attachments']),1)
        attachment=extracted_mail['attachments'][0]
        self.assertEqual(attachment.fname,'hello_world.dat')
        self.assertEqual(attachment.content,b'Helloworld\n')
        self.assertEqual(capture.output,[
            ("WARNING:flectra.addons.mail.models.mail_thread:Messagecontaininganunexpected"
             "Content-Type'binary/octet-stream',assuming'application/octet-stream'"),
        ])

    deftest_message_parse_body(self):
        #testpureplaintext
        plaintext=self.format(test_mail_data.MAIL_TEMPLATE_PLAINTEXT,email_from='"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>')
        res=self.env['mail.thread'].message_parse(self.from_string(plaintext))
        self.assertIn('Pleasecallmeassoonaspossiblethisafternoon!',res['body'])

        #testpurehtml
        html=self.format(test_mail_data.MAIL_TEMPLATE_HTML,email_from='"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>')
        res=self.env['mail.thread'].message_parse(self.from_string(html))
        self.assertIn('<p>Pleasecallmeassoonaspossiblethisafternoon!</p>',res['body'])
        self.assertNotIn('<!DOCTYPE',res['body'])

        #testmultipart/textandhtml->htmlhaspriority
        multipart=self.format(MAIL_TEMPLATE,email_from='"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>')
        res=self.env['mail.thread'].message_parse(self.from_string(multipart))
        self.assertIn('<p>Pleasecallmeassoonaspossiblethisafternoon!</p>',res['body'])

        #testmultipart/mixed
        res=self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_MULTIPART_MIXED))
        self.assertNotIn(
            'Shouldcreateamultipart/mixed:fromgmail,*bold*,withattachment',res['body'],
            'message_parse:textversionshouldnotbeinbodyafterparsingmultipart/mixed')
        self.assertIn(
            '<divdir="ltr">Shouldcreateamultipart/mixed:fromgmail,<b>bold</b>,withattachment.<brclear="all"><div><br></div>',res['body'],
            'message_parse:htmlversionshouldbeinbodyafterparsingmultipart/mixed')

        res=self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_MULTIPART_MIXED_TWO))
        self.assertNotIn('Firstandsecondpart',res['body'],
                         'message_parse:textversionshouldnotbeinbodyafterparsingmultipart/mixed')
        self.assertIn('Firstpart',res['body'],
                      'message_parse:firstpartofthehtmlversionshouldbeinbodyafterparsingmultipart/mixed')
        self.assertIn('Secondpart',res['body'],
                      'message_parse:secondpartofthehtmlversionshouldbeinbodyafterparsingmultipart/mixed')

        res=self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_SINGLE_BINARY))
        self.assertEqual(res['body'],'')
        self.assertEqual(res['attachments'][0][0],'thetruth.pdf')

        res=self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_MULTIPART_WEIRD_FILENAME))
        self.assertEqual(res['attachments'][0][0],'62_@;,][)=.(ÇÀÉ.txt')

    deftest_message_parse_bugs(self):
        """Variouscornercasesormessageparsing"""
        #messagewithoutFinal-Recipient
        self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_NO_FINAL_RECIPIENT))

        #messagewithemptybody(includingonlyvoidcharacters)
        res=self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_NO_BODY))
        self.assertEqual(res['body'],'\n\n','Gatewayshouldnotcrashwithvoidcontent')

    deftest_message_parse_eml(self):
        #Testthattheparsingofmailwithembeddedemailsaseml(msg)whichgeneratesemptyattachments,canbeprocessed.
        mail=self.format(test_mail_data.MAIL_EML_ATTACHMENT,email_from='"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>',to='generic@test.com')
        self.env['mail.thread'].message_parse(self.from_string(mail))

    deftest_message_parse_eml_bounce_headers(self):
        #TestText/RFC822-HeadersMIMEcontent-type
        msg_id='<861878175823148.1577183525.736005783081055-openerp-19177-account.invoice@mycompany.example.com>'
        mail=self.format(
            test_mail_data.MAIL_EML_ATTACHMENT_BOUNCE_HEADERS,
            email_from='MAILER-DAEMON@example.com(MailDeliverySystem)',
            to='test_bounce+82240-account.invoice-19177@mycompany.example.com',
            #msg_idgoestotheattachment'sMessage-Idheader
            msg_id=msg_id,
        )
        res=self.env['mail.thread'].message_parse(self.from_string(mail))

        self.assertEqual(res['bounced_msg_id'],[msg_id],"Message-IdisnotextractedfromText/RFC822-Headersattachment")

    deftest_message_parse_extract_bounce_rfc822_headers_qp(self):
        #IncomingbounceforunexistingOutlookaddress
        #bouncebacksometimeswithaContent-Type`text/rfc822-headers`
        #andContent-Type-Encoding`quoted-printable`
        partner=self.env['res.partner'].create({
            'name':'MitchelleAdmine',
            'email':'rdesfrdgtfdrfesd@outlook.com'
        })
        message=self.env['mail.message'].create({
            'message_id':'<368396033905967.1673346177.695352554321289-openerp-11-sale.order@eupp00>'
        })
        incoming_bounce=self.format(
            test_mail_data.MAIL_BOUNCE_QP_RFC822_HEADERS,
            email_from='MAILER-DAEMON@mailserver.flectrahq.com(MailDeliverySystem)',
            email_to='bounce@xxx.flectrahq.com',
            delivered_to='bounce@xxx.flectrahq.com'
        )

        msg_dict={}
        msg=self.env['mail.thread']._message_parse_extract_bounce(self.from_string(incoming_bounce),msg_dict)
        self.assertEqual(msg['bounced_email'],partner.email,"Thesenderemailshouldbecorrectlyparsed")
        self.assertEqual(msg['bounced_partner'],partner,"Apartnerwiththisemailshouldexist")
        self.assertEqual(msg['bounced_msg_id'][0],message.message_id,"Thesendermessage-idshouldcorrectlyparsed")
        self.assertEqual(msg['bounced_message'],message,"Anexistingmessagewiththismessage_idshouldexist")

    deftest_message_parse_plaintext(self):
        """Incomingemailinplaintextshouldbestoredashtml"""
        mail=self.format(test_mail_data.MAIL_TEMPLATE_PLAINTEXT,email_from='"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>',to='generic@test.com')
        res=self.env['mail.thread'].message_parse(self.from_string(mail))
        self.assertIn('<pre>\nPleasecallmeassoonaspossiblethisafternoon!\n\n--\nSylvie\n</pre>',res['body'])

    deftest_message_parse_xhtml(self):
        #TestthattheparsingofXHTMLmailsdoesnotfail
        self.env['mail.thread'].message_parse(self.from_string(test_mail_data.MAIL_XHTML))

@tagged('mail_gateway')
classTestMailAlias(TestMailCommon):

    @users('employee')
    deftest_alias_creation(self):
        record=self.env['mail.test.container'].create({
            'name':'TestRecord',
            'alias_name':'alias.test',
            'alias_contact':'followers',
        })
        self.assertEqual(record.alias_id.alias_model_id,self.env['ir.model']._get('mail.test.container'))
        self.assertEqual(record.alias_id.alias_force_thread_id,record.id)
        self.assertEqual(record.alias_id.alias_parent_model_id,self.env['ir.model']._get('mail.test.container'))
        self.assertEqual(record.alias_id.alias_parent_thread_id,record.id)
        self.assertEqual(record.alias_id.alias_name,'alias.test')
        self.assertEqual(record.alias_id.alias_contact,'followers')

        record.write({
            'alias_name':'better.alias.test',
            'alias_defaults':"{'default_name':'defaults'}"
        })
        self.assertEqual(record.alias_id.alias_name,'better.alias.test')
        self.assertEqual(record.alias_id.alias_defaults,"{'default_name':'defaults'}")

        withself.assertRaises(exceptions.AccessError):
            record.write({
                'alias_force_thread_id':0,
            })

        withself.assertRaises(exceptions.AccessError):
            record.write({
                'alias_model_id':self.env['ir.model']._get('mail.test.gateway').id,
            })

        withself.assertRaises(exceptions.ValidationError):
            record.write({'alias_defaults':"{'custom_field':brokendict"})

    deftest_alias_domain_allowed_validation(self):
        """Checkthevalidationof`mail.catchall.domain.allowed`systemparameter"""
        forvaluein[',',',,',',,']:
            withself.assertRaises(exceptions.ValidationError,
                 msg="Thevalue'%s'shouldnotbeallowed"%value):
                self.env['ir.config_parameter'].set_param('mail.catchall.domain.allowed',value)

        forvalue,expectedin[
            ('',False),
            ('hello.com','hello.com'),
            ('hello.com,,','hello.com'),
            ('hello.com,bonjour.com','hello.com,bonjour.com'),
            ('hello.COM,BONJOUR.com','hello.com,bonjour.com'),
        ]:
            self.env['ir.config_parameter'].set_param('mail.catchall.domain.allowed',value)
            self.assertEqual(self.env['ir.config_parameter'].get_param('mail.catchall.domain.allowed'),expected)

    deftest_alias_setup(self):
        alias=self.env['mail.alias'].create({
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_name':'b4r+_#_R3wl$$',
        })
        self.assertEqual(alias.alias_name,'b4r+_-_r3wl-','Disallowedcharsshouldbereplacedbyhyphens')

        withself.assertRaises(exceptions.ValidationError):
            alias.write({'alias_defaults':"{'custom_field':brokendict"})

    deftest_alias_name_unique(self):
        alias_model_id=self.env['ir.model']._get('mail.test.gateway').id
        catchall_alias=self.env['ir.config_parameter'].sudo().get_param('mail.catchall.alias')
        bounce_alias=self.env['ir.config_parameter'].sudo().get_param('mail.bounce.alias')

        #testyoucannotcreatealiasesmatchingbounce/catchall
        withself.assertRaises(exceptions.UserError),self.cr.savepoint():
            self.env['mail.alias'].create({'alias_model_id':alias_model_id,'alias_name':catchall_alias})
        withself.assertRaises(exceptions.UserError),self.cr.savepoint():
            self.env['mail.alias'].create({'alias_model_id':alias_model_id,'alias_name':bounce_alias})

        new_mail_alias=self.env['mail.alias'].create({
            'alias_model_id':alias_model_id,
            'alias_name':'unused.test.alias'
        })

        #testthatre-usingcatchallandbouncealiasraisesUserError
        withself.assertRaises(exceptions.UserError),self.cr.savepoint():
            new_mail_alias.write({
                'alias_name':catchall_alias
            })
        withself.assertRaises(exceptions.UserError),self.cr.savepoint():
            new_mail_alias.write({
                'alias_name':bounce_alias
            })

        new_mail_alias.write({'alias_name':'another.unused.test.alias'})

        #testthatduplicatinganaliasshouldhaveblankname
        copy_new_mail_alias=new_mail_alias.copy()
        self.assertFalse(copy_new_mail_alias.alias_name)

        #cannotsetcatchall/bouncetousedalias
        withself.assertRaises(exceptions.UserError),self.cr.savepoint():
            self.env['ir.config_parameter'].sudo().set_param('mail.catchall.alias',new_mail_alias.alias_name)
        withself.assertRaises(exceptions.UserError),self.cr.savepoint():
            self.env['ir.config_parameter'].sudo().set_param('mail.bounce.alias',new_mail_alias.alias_name)

    deftest_alias_mixin_copy(self):
        user_demo=self.env.ref('base.user_demo')
        self.assertFalse(user_demo.has_group('base.group_system'),'DemouserisnotsupposedtohaveAdministratoraccess')
        self._test_alias_mixin_copy(user_demo,'alias.test1',False)
        self._test_alias_mixin_copy(user_demo,'alias.test2','<p>WhatIsDeadMayNeverDie</p>')

    def_test_alias_mixin_copy(self,user,alias_name,alias_bounced_content):
        record=self.env['mail.test.container'].with_user(user).with_context(lang='en_US').create({
            'name':'TestRecord',
            'alias_name':alias_name,
            'alias_contact':'followers',
            'alias_bounced_content':alias_bounced_content,
        })
        self.assertEqual(record.alias_bounced_content,alias_bounced_content)
        record_copy=record.copy()
        self.assertEqual(record_copy.alias_bounced_content,alias_bounced_content)


@tagged('mail_gateway')
classTestMailgateway(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailgateway,cls).setUpClass()
        cls.test_model=cls.env['ir.model']._get('mail.test.gateway')
        cls.email_from='"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>'

        cls.test_record=cls.env['mail.test.gateway'].with_context(cls._test_context).create({
            'name':'Test',
            'email_from':'ignasse@example.com',
        }).with_context({})

        cls.partner_1=cls.env['res.partner'].with_context(cls._test_context).create({
            'name':'ValidLelitre',
            'email':'valid.lelitre@agrolait.com',
        })
        #groups@..willcausethecreationofnewmail.test.gateway
        cls.alias=cls.env['mail.alias'].create({
            'alias_name':'groups',
            'alias_user_id':False,
            'alias_model_id':cls.test_model.id,
            'alias_contact':'everyone'})

        #Setafirstmessageonpublicgrouptotestupdateandhierarchy
        cls.fake_email=cls._create_gateway_message(cls.test_record,'123456')

        cls._init_mail_gateway()

    @classmethod
    def_create_gateway_message(cls,record,msg_id_prefix,**values):
        msg_values={
            'author_id':cls.partner_1.id,
            'email_from':cls.partner_1.email_formatted,
            'body':'<p>Genericbody</p>',
            'message_id':f'<{msg_id_prefix}-openerp-{record.id}-{record._name}@{socket.gethostname()}>',
            'message_type':'email',
            'model':record._name,
            'res_id':record.id,
            'subject':'GenericMessage',
            'subtype_id':cls.env.ref('mail.mt_comment').id,
        }
        msg_values.update(**values)
        returncls.env['mail.message'].create(msg_values)

    #--------------------------------------------------
    #Baselow-leveltests
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_basic(self):
        """Testdetailsofcreatedmessagegoingthroughmailgateway"""
        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='Specific')

        #Test:onegroupcreatedbymailgatewayadministratorasuser_idisnotset
        self.assertEqual(len(record),1,'message_process:anewmail.testshouldhavebeencreated')
        res=record.get_metadata()[0].get('create_uid')or[None]
        self.assertEqual(res[0],self.env.uid)

        #Test:onemessagethatistheincomingemail
        self.assertEqual(len(record.message_ids),1)
        msg=record.message_ids[0]
        self.assertEqual(msg.subject,'Specific')
        self.assertIn('Pleasecallmeassoonaspossiblethisafternoon!',msg.body)
        self.assertEqual(msg.message_type,'email')
        self.assertEqual(msg.subtype_id,self.env.ref('mail.mt_comment'))

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_cid(self):
        origin_message_parse_extract_payload=MailThread._message_parse_extract_payload

        def_message_parse_extract_payload(this,*args,**kwargs):
            res=origin_message_parse_extract_payload(this,*args,**kwargs)
            self.assertTrue(isinstance(res['body'],str),'Bodyfromextractedpayloadshouldstillbeastring.')
            returnres

        withpatch.object(MailThread,'_message_parse_extract_payload',_message_parse_extract_payload):
            record=self.format_and_process(test_mail_data.MAIL_MULTIPART_IMAGE,self.email_from,'groups@test.com')

        message=record.message_ids[0]
        forattachmentinmessage.attachment_ids:
            self.assertIn('/web/image/%s'%attachment.id,message.body)
        self.assertEqual(
            set(message.attachment_ids.mapped('name')),
            set(['rosaçée.gif','verte!µ.gif','orangée.gif']))

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_followers(self):
        """Incomingemail:recognizedauthornotarchivedandnotflectrabot:addedasfollower"""
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@test.com')

        self.assertEqual(record.message_ids[0].author_id,self.partner_1,
                         'message_process:recognizedemail->author_id')
        self.assertEqual(record.message_ids[0].email_from,self.partner_1.email_formatted)
        self.assertEqual(record.message_follower_ids.partner_id,self.partner_1,
                         'message_process:recognizedemail->addedasfollower')
        self.assertEqual(record.message_partner_ids,self.partner_1,
                         'message_process:recognizedemail->addedasfollower')

        #justanemail->nofollower
        withself.mock_mail_gateway():
            record2=self.format_and_process(
                MAIL_TEMPLATE,self.email_from,'groups@test.com',
                subject='AnotherEmail')

        self.assertEqual(record2.message_ids[0].author_id,self.env['res.partner'])
        self.assertEqual(record2.message_ids[0].email_from,self.email_from)
        self.assertEqual(record2.message_follower_ids.partner_id,self.env['res.partner'],
                         'message_process:unrecognizedemail->nofollower')
        self.assertEqual(record2.message_partner_ids,self.env['res.partner'],
                         'message_process:unrecognizedemail->nofollower')

        #archivedpartner->nofollower
        self.partner_1.active=False
        self.partner_1.flush()
        withself.mock_mail_gateway():
            record3=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@test.com',
                subject='YetAnotherEmail')

        self.assertEqual(record3.message_ids[0].author_id,self.env['res.partner'])
        self.assertEqual(record3.message_ids[0].email_from,self.partner_1.email_formatted)
        self.assertEqual(record3.message_follower_ids.partner_id,self.env['res.partner'],
                         'message_process:unrecognizedemail->nofollower')
        self.assertEqual(record3.message_partner_ids,self.env['res.partner'],
                         'message_process:unrecognizedemail->nofollower')


        #partner_root->neveragain
        flectrabot=self.env.ref('base.partner_root')
        flectrabot.active=True
        flectrabot.email='flectrabot@example.com'
        withself.mock_mail_gateway():
            record4=self.format_and_process(
                MAIL_TEMPLATE,flectrabot.email_formatted,'groups@test.com',
                subject='FlectrabotAutomaticAnswer')

        self.assertEqual(record4.message_ids[0].author_id,flectrabot)
        self.assertEqual(record4.message_ids[0].email_from,flectrabot.email_formatted)
        self.assertEqual(record4.message_follower_ids.partner_id,self.env['res.partner'],
                         'message_process:unrecognizedemail->nofollower')
        self.assertEqual(record4.message_partner_ids,self.env['res.partner'],
                         'message_process:unrecognizedemail->nofollower')

    #--------------------------------------------------
    #Authorrecognition
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_email_email_from(self):
        """Incomingemail:notrecognizedauthor:email_from,noauthor_id,nofollowers"""
        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com')
        self.assertFalse(record.message_ids[0].author_id,'message_process:unrecognizedemail->noauthor_id')
        self.assertEqual(record.message_ids[0].email_from,self.email_from)
        self.assertEqual(len(record.message_partner_ids),0,
                         'message_process:newlycreategroupshouldnothaveanyfollower')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_email_author(self):
        """Incomingemail:recognizedauthor:email_from,author_id,addedasfollower"""
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@test.com',subject='Test1')

        self.assertEqual(record.message_ids[0].author_id,self.partner_1,
                         'message_process:recognizedemail->author_id')
        self.assertEqual(record.message_ids[0].email_from,self.partner_1.email_formatted)
        self.assertNotSentEmail() #Nonotification/bounceshouldbesent

        #Emailrecognizedifpartnerhasaformattedemail
        self.partner_1.write({'email':'"ValidLelitre"<%s>'%self.partner_1.email})
        record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email,'groups@test.com',subject='Test2')

        self.assertEqual(record.message_ids[0].author_id,self.partner_1,
                         'message_process:recognizedemail->author_id')
        self.assertEqual(record.message_ids[0].email_from,self.partner_1.email)
        self.assertNotSentEmail() #Nonotification/bounceshouldbesent

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_email_author_multiemail(self):
        """Incomingemail:recognizedauthor:checkmulti/formattedemailinfield"""
        test_email='valid.lelitre@agrolait.com'
        #Emailnotrecognizedifpartnerhasamulti-email(source=formattedemail)
        self.partner_1.write({'email':f'{test_email},"ValidLelitre"<another.email@test.example.com>'})
        withself.mock_mail_gateway():
            record=self.format_and_process(
                MAIL_TEMPLATE,f'"ValidLelitre"<{test_email}>','groups@test.com',subject='Test3')

        self.assertEqual(record.message_ids[0].author_id,self.partner_1,
                         'message_process:foundauthorbasedonfirstfoundemailnormalized,evenwithmultiemails')
        self.assertEqual(record.message_ids[0].email_from,f'"ValidLelitre"<{test_email}>')
        self.assertNotSentEmail() #Nonotification/bounceshouldbesent

        #Emailnotrecognizedifpartnerhasamulti-email(source=stdemail)
        withself.mock_mail_gateway():
            record=self.format_and_process(
                MAIL_TEMPLATE,test_email,'groups@test.com',subject='Test4')

        self.assertEqual(record.message_ids[0].author_id,self.partner_1,
                         'message_process:foundauthorbasedonfirstfoundemailnormalized,evenwithmultiemails')
        self.assertEqual(record.message_ids[0].email_from,test_email)
        self.assertNotSentEmail() #Nonotification/bounceshouldbesent

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_email_partner_find(self):
        """Findingthepartnerbasedonemail,basedonpartner/user/follower"""
        self.alias.write({'alias_force_thread_id':self.test_record.id})
        from_1=self.env['res.partner'].create({'name':'BriceDenisse','email':'from.test@example.com'})

        self.format_and_process(MAIL_TEMPLATE,from_1.email_formatted,'groups@test.com')
        self.assertEqual(self.test_record.message_ids[0].author_id,from_1)
        self.test_record.message_unsubscribe([from_1.id])

        from_2=mail_new_test_user(self.env,login='B',groups='base.group_user',name='UserDenisse',email='from.test@example.com')

        self.format_and_process(MAIL_TEMPLATE,from_1.email_formatted,'groups@test.com')
        self.assertEqual(self.test_record.message_ids[0].author_id,from_2.partner_id)
        self.test_record.message_unsubscribe([from_2.partner_id.id])

        from_3=self.env['res.partner'].create({'name':'FOllowerDenisse','email':'from.test@example.com'})
        self.test_record.message_subscribe([from_3.id])

        self.format_and_process(MAIL_TEMPLATE,from_1.email_formatted,'groups@test.com')
        self.assertEqual(self.test_record.message_ids[0].author_id,from_3)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_email_author_exclude_alias(self):
        """Donotsetaliasasauthortoavoidincludingaliasesindiscussions"""
        from_1=self.env['res.partner'].create({'name':'BriceDenisse','email':'from.test@test.com'})
        self.env['mail.alias'].create({
            'alias_name':'from.test',
            'alias_model_id':self.env['ir.model']._get('mail.test.gateway').id
        })

        record=self.format_and_process(MAIL_TEMPLATE,from_1.email_formatted,'groups@test.com')
        self.assertFalse(record.message_ids[0].author_id)
        self.assertEqual(record.message_ids[0].email_from,from_1.email_formatted)

    #--------------------------------------------------
    #Aliasconfiguration
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_alias_config_bounced_content(self):
        """Custombouncedmessageforthealias=>Receivedthiscustommessage"""
        self.alias.write({
            'alias_contact':'partners',
            'alias_bounced_content':'<p>WhatIsDeadMayNeverDie</p>'
        })

        #Test:custombouncedcontent
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='ShouldBounce')
        self.assertFalse(record,'message_process:shouldhavebounced')
        self.assertSentEmail('"MAILER-DAEMON"<bounce.test@test.com>',['whatever-2a840@postmaster.twitter.com'],body_content='<p>WhatIsDeadMayNeverDie</p>')

        self.alias.write({
            'alias_contact':'partners',
            'alias_bounced_content':'<p></br></p>'
        })

        #Test:with"empty"bouncedcontent(simulateview,puttingalways'<p></br></p>'inhtmlfield)
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='ShouldBounce')
        self.assertFalse(record,'message_process:shouldhavebounced')
        #Checkifdefault(hardcoded)valueisinthemailcontent
        self.assertSentEmail('"MAILER-DAEMON"<bounce.test@test.com>',['whatever-2a840@postmaster.twitter.com'],body_content='Thefollowingemailsentto')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_message_process_alias_config_bounced_to(self):
        """Checkbouncemessagecontainsthebouncingalias,notageneric"to""""
        self.alias.write({'alias_contact':'partners'})
        bounce_message_with_alias="Thefollowingemailsentto%scannotbeacceptedbecausethisisaprivateemailaddress."%self.alias.display_name.lower()

        #BounceisTo
        withself.mock_mail_gateway():
            self.format_and_process(
                MAIL_TEMPLATE,self.email_from,'groups@example.com',
                cc='other@gmail.com',subject='ShouldBounce')
        self.assertIn(bounce_message_with_alias,self._mails[0].get('body'))

        #BounceisCC
        withself.mock_mail_gateway():
            self.format_and_process(
                MAIL_TEMPLATE,self.email_from,'other@gmail.com',
                cc='groups@example.com',subject='ShouldBounce')
        self.assertIn(bounce_message_with_alias,self._mails[0].get('body'))

        #BounceispartofTo
        withself.mock_mail_gateway():
            self.format_and_process(
                MAIL_TEMPLATE,self.email_from,'other@gmail.com,groups@example.com',
                subject='ShouldBounce')
        self.assertIn(bounce_message_with_alias,self._mails[0].get('body'))

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_defaults(self):
        """Testaliasdefaultsandinnervalues"""
        self.alias.write({
            'alias_user_id':self.user_employee.id,
            'alias_defaults':"{'custom_field':'defaults_custom'}"
        })

        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='Specific')
        self.assertEqual(len(record),1)
        res=record.get_metadata()[0].get('create_uid')or[None]
        self.assertEqual(res[0],self.user_employee.id)
        self.assertEqual(record.name,'Specific')
        self.assertEqual(record.custom_field,'defaults_custom')

        self.alias.write({'alias_defaults':'""'})
        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='Specific2')
        self.assertEqual(len(record),1)
        res=record.get_metadata()[0].get('create_uid')or[None]
        self.assertEqual(res[0],self.user_employee.id)
        self.assertEqual(record.name,'Specific2')
        self.assertFalse(record.custom_field)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_user_id(self):
        """Testaliasownership"""
        self.alias.write({'alias_user_id':self.user_employee.id})

        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com')
        self.assertEqual(len(record),1)
        res=record.get_metadata()[0].get('create_uid')or[None]
        self.assertEqual(res[0],self.user_employee.id)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_everyone(self):
        """Incomingemail:everyone:newrecord+message_new"""
        self.alias.write({'alias_contact':'everyone'})

        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='Specific')
        self.assertEqual(len(record),1)
        self.assertEqual(len(record.message_ids),1)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_alias_partners_bounce(self):
        """IncomingemailfromanunknownpartneronaPartnersonlyalias->bounce+testbounceemail"""
        self.alias.write({'alias_contact':'partners'})

        #Test:nogroupcreated,emailbounced
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='ShouldBounce')
        self.assertFalse(record)
        self.assertSentEmail('"MAILER-DAEMON"<bounce.test@test.com>',['whatever-2a840@postmaster.twitter.com'],subject='Re:ShouldBounce')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_alias_followers_bounce(self):
        """Incomingemailfromunknownpartner/notfollowerpartneronaFollowersonlyalias->bounce"""
        self.alias.write({
            'alias_contact':'followers',
            'alias_parent_model_id':self.env['ir.model']._get('mail.test.gateway').id,
            'alias_parent_thread_id':self.test_record.id,
        })

        #Test:unknownonfollowersalias->bounce
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='ShouldBounce')
        self.assertFalse(record,'message_process:shouldhavebounced')
        self.assertSentEmail('"MAILER-DAEMON"<bounce.test@test.com>',['whatever-2a840@postmaster.twitter.com'],subject='Re:ShouldBounce')

        #Test:partneronfollowersalias->bounce
        self._init_mail_mock()
        withself.mock_mail_gateway():
            record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@test.com',subject='ShouldBounce')
        self.assertFalse(record,'message_process:shouldhavebounced')
        self.assertSentEmail('"MAILER-DAEMON"<bounce.test@test.com>',['whatever-2a840@postmaster.twitter.com'],subject='Re:ShouldBounce')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_partner(self):
        """IncomingemailfromaknownpartneronaPartnersalias->ok(+testonalias.user_id)"""
        self.alias.write({'alias_contact':'partners'})
        record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@test.com')

        #Test:onegroupcreatedbyaliasuser
        self.assertEqual(len(record),1)
        self.assertEqual(len(record.message_ids),1)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_followers(self):
        """IncomingemailfromaparentdocumentfolloweronaFollowersonlyalias->ok"""
        self.alias.write({
            'alias_contact':'followers',
            'alias_parent_model_id':self.env['ir.model']._get('mail.test.gateway').id,
            'alias_parent_thread_id':self.test_record.id,
        })
        self.test_record.message_subscribe(partner_ids=[self.partner_1.id])
        record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@test.com')

        #Test:onegroupcreatedbyRaoul(orSylviemaybe,ifweimplementit)
        self.assertEqual(len(record),1)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_alias_followers_multiemail(self):
        """IncomingemailfromaparentdocumentfolloweronaFollowersonly
        aliasdependsonemail_from/partnerrecognition,tobetestedwhen
        dealingwithmultiemails/formattedemails."""
        self.alias.write({
            'alias_contact':'followers',
            'alias_parent_model_id':self.env['ir.model']._get('mail.test.gateway').id,
            'alias_parent_thread_id':self.test_record.id,
        })
        self.test_record.message_subscribe(partner_ids=[self.partner_1.id])
        email_from=formataddr(("AnotherName",self.partner_1.email_normalized))

        forpartner_email,passedin[
            (formataddr((self.partner_1.name,self.partner_1.email_normalized)),True),
            (f'{self.partner_1.email_normalized},"MultiEmail"<multi.email@test.example.com>',True),
            (f'"MultiEmail"<multi.email@test.example.com>,{self.partner_1.email_normalized}',False),
        ]:
            withself.subTest(partner_email=partner_email):
                self.partner_1.write({'email':partner_email})
                record=self.format_and_process(
                    MAIL_TEMPLATE,email_from,'groups@test.com',
                    subject=f'Testfor{partner_email}')

                ifpassed:
                    self.assertEqual(len(record),1)
                    self.assertEqual(record.email_from,email_from)
                    self.assertEqual(record.message_partner_ids,self.partner_1)
                #multiemailsnotrecognized(nonormalizedemail,recognition)
                else:
                    self.assertEqual(len(record),0,
                                     'Aliascheck(FIXME):multi-emailsbadsupportforrecognition')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_alias_update(self):
        """Incomingemailupdatediscussion+notificationemail"""
        self.alias.write({'alias_force_thread_id':self.test_record.id})

        self.test_record.message_subscribe(partner_ids=[self.partner_1.id])
        withself.mock_mail_gateway():
            record=self.format_and_process(
                MAIL_TEMPLATE,self.email_from,'groups@test.com>',
                msg_id='<1198923581.41972151344608186799.JavaMail.diff1@agrolait.com>',subject='Re:cats')

        #Test:nonewgroup+newmessage
        self.assertFalse(record,'message_process:aliasupdateshouldnotcreatenewrecords')
        self.assertEqual(len(self.test_record.message_ids),2)
        #Test:sentemails:1(Sylviecopyoftheincomingemail)
        self.assertSentEmail(self.email_from,[self.partner_1],subject='Re:cats')

    #--------------------------------------------------
    #Creatorrecognition
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_create_uid_crash(self):
        def_employee_crash(*args,**kwargs):
            """Ifemployeeistestemployee,considerhehasnoaccessondocument"""
            recordset=args[0]
            ifrecordset.env.uid==self.user_employee.idandnotrecordset.env.su:
                ifkwargs.get('raise_exception',True):
                    raiseexceptions.AccessError('HophophopErnest,pleasestepback.')
                returnFalse
            returnDEFAULT

        withpatch.object(MailTestGateway,'check_access_rights',autospec=True,side_effect=_employee_crash):
            record=self.format_and_process(MAIL_TEMPLATE,self.user_employee.email_formatted,'groups@test.com',subject='NoEmployeeAllowed')
        self.assertEqual(record.create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].subject,'NoEmployeeAllowed')
        self.assertEqual(record.message_ids[0].create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].author_id,self.user_employee.partner_id)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_create_uid_email(self):
        record=self.format_and_process(MAIL_TEMPLATE,self.user_employee.email_formatted,'groups@test.com',subject='EmailFound')
        self.assertEqual(record.create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].subject,'EmailFound')
        self.assertEqual(record.message_ids[0].create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].author_id,self.user_employee.partner_id)

        record=self.format_and_process(MAIL_TEMPLATE,'Anothername<%s>'%self.user_employee.email,'groups@test.com',subject='EmailOtherName')
        self.assertEqual(record.create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].subject,'EmailOtherName')
        self.assertEqual(record.message_ids[0].create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].author_id,self.user_employee.partner_id)

        record=self.format_and_process(MAIL_TEMPLATE,self.user_employee.email_normalized,'groups@test.com',subject='EmailSimpleEmail')
        self.assertEqual(record.create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].subject,'EmailSimpleEmail')
        self.assertEqual(record.message_ids[0].create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].author_id,self.user_employee.partner_id)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_create_uid_email_follower(self):
        self.alias.write({
            'alias_parent_model_id':self.test_model.id,
            'alias_parent_thread_id':self.test_record.id,
        })
        follower_user=mail_new_test_user(self.env,login='better',groups='base.group_user',name='ErnestFollower',email=self.user_employee.email)
        self.test_record.message_subscribe(follower_user.partner_id.ids)

        record=self.format_and_process(MAIL_TEMPLATE,self.user_employee.email_formatted,'groups@test.com',subject='FollowerWinner')
        self.assertEqual(record.create_uid,follower_user)
        self.assertEqual(record.message_ids[0].subject,'FollowerWinner')
        self.assertEqual(record.message_ids[0].create_uid,follower_user)
        self.assertEqual(record.message_ids[0].author_id,follower_user.partner_id)

        #nameorderwin
        self.test_record.message_unsubscribe(follower_user.partner_id.ids)
        self.test_record.flush()
        record=self.format_and_process(MAIL_TEMPLATE,self.user_employee.email_formatted,'groups@test.com',subject='FirstFoundWinner')
        self.assertEqual(record.create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].subject,'FirstFoundWinner')
        self.assertEqual(record.message_ids[0].create_uid,self.user_employee)
        self.assertEqual(record.message_ids[0].author_id,self.user_employee.partner_id)

    #--------------------------------------------------
    #Aliasroutingmanagement
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_alias_no_domain(self):
        """Incomingemail:writetoaliasevenifnodomainset:consideredasvalidalias"""
        self.env['ir.config_parameter'].set_param('mail.catchall.domain','')

        new_record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,'groups@another.domain.com',subject='TestSubject')
        #Test:onegroupcreated
        self.assertEqual(len(new_record),1,'message_process:anewmail.test.simpleshouldhavebeencreated')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_alias_forward_bypass_reply_first(self):
        """Incomingemail:writetotwo"newthread"alias,oneasareply,onebeinganothermodel->considerasaforward"""
        self.assertEqual(len(self.test_record.message_ids),1)

        #test@..willcausethecreationofnewmail.test
        new_alias_2=self.env['mail.alias'].create({
            'alias_name':'test',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })
        new_rec=self.format_and_process(
            MAIL_TEMPLATE,self.partner_1.email_formatted,
            '%s@%s,%s@%s'%(new_alias_2.alias_name,self.alias_domain,self.alias.alias_name,self.alias_domain),
            subject='TestSubject',
            extra='In-Reply-To:\r\n\t%s\n'%self.fake_email.message_id,
            target_model=new_alias_2.alias_model_id.model
        )
        #Forwardcreatedanewrecordinmail.test
        self.assertEqual(len(new_rec),1,'message_process:anewmail.testshouldhavebeencreated')
        self.assertEqual(new_rec._name,new_alias_2.alias_model_id.model)
        #Nonewpostontest_record,nonewrecordinmail.test.simpleeither
        self.assertEqual(len(self.test_record.message_ids),1,'message_process:shouldnotpostonrepliedrecordasforwardshouldbypassit')
        new_simple=self.env['mail.test.simple'].search([('name','=','TestSubject')])
        self.assertEqual(len(new_simple),0,'message_process:anewmail.testshouldnothavebeencreated')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_alias_forward_bypass_reply_second(self):
        """Incomingemail:writetotwo"newthread"alias,oneasareply,onebeinganothermodel->considerasaforward"""
        self.assertEqual(len(self.test_record.message_ids),1)

        #test@..willcausethecreationofnewmail.test
        new_alias_2=self.env['mail.alias'].create({
            'alias_name':'test',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })
        new_rec=self.format_and_process(
            MAIL_TEMPLATE,self.partner_1.email_formatted,
            '%s@%s,%s@%s'%(self.alias.alias_name,self.alias_domain,new_alias_2.alias_name,self.alias_domain),
            subject='TestSubject',
            extra='In-Reply-To:\r\n\t%s\n'%self.fake_email.message_id,
            target_model=new_alias_2.alias_model_id.model
        )
        #Forwardcreatedanewrecordinmail.test
        self.assertEqual(len(new_rec),1,'message_process:anewmail.testshouldhavebeencreated')
        self.assertEqual(new_rec._name,new_alias_2.alias_model_id.model)
        #Nonewpostontest_record,nonewrecordinmail.test.simpleeither
        self.assertEqual(len(self.test_record.message_ids),1,'message_process:shouldnotpostonrepliedrecordasforwardshouldbypassit')
        new_simple=self.env['mail.test.simple'].search([('name','=','TestSubject')])
        self.assertEqual(len(new_simple),0,'message_process:anewmail.testshouldnothavebeencreated')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_alias_forward_bypass_update_alias(self):
        """Incomingemail:writetoone"update",one"newthread"alias,oneasareply,onebeinganothermodel->considerasaforward"""
        self.assertEqual(len(self.test_record.message_ids),1)
        self.alias.write({
            'alias_force_thread_id':self.test_record.id,
        })

        #test@..willcausethecreationofnewmail.test
        new_alias_2=self.env['mail.alias'].create({
            'alias_name':'test',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })
        new_rec=self.format_and_process(
            MAIL_TEMPLATE,self.partner_1.email_formatted,
            '%s@%s,%s@%s'%(new_alias_2.alias_name,self.alias_domain,self.alias.alias_name,self.alias_domain),
            subject='TestSubject',
            extra='In-Reply-To:\r\n\t%s\n'%self.fake_email.message_id,
            target_model=new_alias_2.alias_model_id.model
        )
        #Forwardcreatedanewrecordinmail.test
        self.assertEqual(len(new_rec),1,'message_process:anewmail.testshouldhavebeencreated')
        self.assertEqual(new_rec._name,new_alias_2.alias_model_id.model)
        #Nonewpostontest_record,nonewrecordinmail.test.simpleeither
        self.assertEqual(len(self.test_record.message_ids),1,'message_process:shouldnotpostonrepliedrecordasforwardshouldbypassit')
        #Nonewrecordonfirstaliasmodel
        new_simple=self.env['mail.test.gateway'].search([('name','=','TestSubject')])
        self.assertEqual(len(new_simple),0,'message_process:anewmail.testshouldnothavebeencreated')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_alias_multiple_new(self):
        """Incomingemail:writetotwoaliasescreatingrecords:bothshouldbeactivated"""
        #test@..willcausethecreationofnewmail.test
        new_alias_2=self.env['mail.alias'].create({
            'alias_name':'test',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })
        new_rec=self.format_and_process(
            MAIL_TEMPLATE,self.partner_1.email_formatted,
            '%s@%s,%s@%s'%(self.alias.alias_name,self.alias_domain,new_alias_2.alias_name,self.alias_domain),
            subject='TestSubject',
            target_model=new_alias_2.alias_model_id.model
        )
        #Newrecordinbothmail.test(new_alias_2)andmail.test.simple(self.alias)
        self.assertEqual(len(new_rec),1,'message_process:anewmail.testshouldhavebeencreated')
        self.assertEqual(new_rec._name,new_alias_2.alias_model_id.model)
        new_simple=self.env['mail.test.gateway'].search([('name','=','TestSubject')])
        self.assertEqual(len(new_simple),1,'message_process:anewmail.testshouldhavebeencreated')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_alias_with_allowed_domains(self):
        """Incomingemail:checkthatifdomainsaresetinthe
        optionalsystemparameter`mail.catchall.domain.allowed`,
        onlyincomingemailsfromthesedomainswillgeneraterecords."""

        MailTestGatewayModel=self.env['mail.test.gateway']
        MailTestContainerModel=self.env['mail.test.container']

        allowed_domain='hello.com'
        not_allowed_domain='bonjour.com'

        #test@..willcausethecreationofnewmail.test
        new_alias_2=self.env['mail.alias'].create({
            'alias_name':'test',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })

        forsubject,gateway_created,container_created,alias2_domain,sys_paramin[
            #Testwith'mail.catchall.domain.allowed'notsetinsystemparameters
            #andwithadomainnotallowed
            ('TestSubject1',True,True,not_allowed_domain,""),
            #Testwith'mail.catchall.domain.allowed'setinsystemparameters
            #andwithadomainnotallowed
            ('TestSubject2',True,False,not_allowed_domain,allowed_domain),
            #Testwith'mail.catchall.domain.allowed'setinsystemparameters
            #andwithadomainallowed
            ('TestSubject3',True,True,allowed_domain,allowed_domain),
        ]:
            withself.subTest(subject=subject,gateway_created=gateway_created,
                              container_created=container_created,alias2_domain=alias2_domain,
                              sys_param=sys_param):
                self.env['ir.config_parameter'].set_param('mail.catchall.domain.allowed',sys_param)

                email_to='%s@%s,%s@%s'%(
                    self.alias.alias_name,self.alias_domain,
                    new_alias_2.alias_name,alias2_domain,
                )

                self.format_and_process(
                    MAIL_TEMPLATE,self.partner_1.email_formatted,email_to,
                    subject=subject,
                    target_model=self.alias.alias_model_id.model
                )

                res_alias_1=MailTestGatewayModel.search([('name','=',subject)])
                res_alias_2=MailTestContainerModel.search([('name','=',subject)])
                self.assertEqual(
                    bool(res_alias_1),gateway_created,
                    'message_process(%s):anewmail.test.gateway%shavebeencreated'%
                        (subject,'should'ifgateway_createdelse"shouldnot")
                )
                self.assertEqual(
                    bool(res_alias_2),container_created,
                    'message_process(%s):anewmail.test.container%shavebeencreated'%
                        (subject,'should'ifcontainer_createdelse"shouldnot")
                )

    #--------------------------------------------------
    #EmailManagement
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_bounce(self):
        """Incomingemail:bounce usingbouncealias:norecordcreation"""
        withself.mock_mail_gateway():
            new_recs=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s+%s-%s-%s@%s'%(
                    self.alias_bounce,self.fake_email.id,
                    self.fake_email.model,self.fake_email.res_id,
                    self.alias_domain
                ),
                subject='Shouldbounce',
            )
        self.assertFalse(new_recs)
        self.assertNotSentEmail()

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_bounce_if_static_but_still_has_plus_addressing(self):
        """Incomingemail:bounceusingbouncealiaswithoutplusaddressing:keepoldbehavior."""
        self.env['ir.config_parameter'].set_param('mail.bounce.alias.static',True)
        withself.mock_mail_gateway():
            new_recs=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s+%s-%s-%s@%s'%(
                    self.alias_bounce,self.fake_email.id,
                    self.fake_email.model,self.fake_email.res_id,
                    self.alias_domain
                ),
                subject='Shouldbounce',
            )
        self.assertFalse(new_recs)
        self.assertEqual(len(self._mails),0,'message_process:incomingbounceproducesnomails')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_bounce_if_static_without_plus_addressing(self):
        """Incomingemail:bounceusingbouncealiaswithoutplusaddressing:bounceit."""
        self.env['ir.config_parameter'].set_param('mail.bounce.alias.static',True)
        withself.mock_mail_gateway():
            new_recs=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s@%s'%(self.alias_bounce,self.alias_domain),
                subject='Shouldbounce',
            )
        self.assertFalse(new_recs)
        self.assertEqual(len(self._mails),0,'message_process:incomingbounceproducesnomails')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_no_bounce_if_not_static_without_plus_addressing(self):
        """Incomingemail:bounceusingbouncealiaswithoutplusaddressing:raiseas
        consideringasadirectwritetobouncealias->invalid"""
        self.env['ir.config_parameter'].set_param('mail.bounce.alias.static',False)
        withself.assertRaises(ValueError):
            self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s@%s'%(self.alias_bounce,self.alias_domain),
                subject="Shouldfailbecauseitisnotabounceandthere'snoalias",
            )

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_bounce_other_recipients(self):
        """Incomingemail:bounceprocessing:bounceshouldbecomputedevenifnotfirstrecipient"""
        withself.mock_mail_gateway():
            new_recs=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s@%s,%s+%s-%s-%s@%s'%(
                    self.alias.alias_name,self.alias_domain,
                    self.alias_bounce,self.fake_email.id,
                    self.fake_email.model,self.fake_email.res_id,
                    self.alias_domain
                ),
                subject='Shouldbounce',
            )
        self.assertFalse(new_recs)
        self.assertNotSentEmail()

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_message_route_write_to_catchall(self):
        """Writingdirectlytocatchallshouldbounce"""
        #Test:nogroupcreated,emailbounced
        withself.mock_mail_gateway():
            record=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '"MySuperCatchall"<%s@%s>'%(self.alias_catchall,self.alias_domain),
                subject='ShouldBounce')
        self.assertFalse(record)
        self.assertSentEmail('"MAILER-DAEMON"<bounce.test@test.com>',['whatever-2a840@postmaster.twitter.com'],subject='Re:ShouldBounce')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_write_to_catchall_other_recipients_first(self):
        """Writingdirectlytocatchallandavalidaliasshouldtakealias"""
        #Test:nogroupcreated,emailbounced
        withself.mock_mail_gateway():
            record=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s@%s,%s@%s'%(self.alias_catchall,self.alias_domain,self.alias.alias_name,self.alias_domain),
                subject='CatchallNotBlocking'
            )
        #Test:onegroupcreated
        self.assertEqual(len(record),1,'message_process:anewmail.testshouldhavebeencreated')
        #Nobounceemail
        self.assertNotSentEmail()

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_route_write_to_catchall_other_recipients_second(self):
        """Writingdirectlytocatchallandavalidaliasshouldtakealias"""
        #Test:nogroupcreated,emailbounced
        withself.mock_mail_gateway():
            record=self.format_and_process(
                MAIL_TEMPLATE,self.partner_1.email_formatted,
                '%s@%s,%s@%s'%(self.alias.alias_name,self.alias_domain,self.alias_catchall,self.alias_domain),
                subject='CatchallNotBlocking'
            )
        #Test:onegroupcreated
        self.assertEqual(len(record),1,'message_process:anewmail.testshouldhavebeencreated')
        #Nobounceemail
        self.assertNotSentEmail()

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_alias(self):
        """Writingtobouncealiasisconsideredasabounceevenifnotmultipart/reportbouncestructure"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

        bounced_mail_id=4442
        bounce_email_to='%s+%s-%s-%s@%s'%('bounce.test',bounced_mail_id,self.test_record._name,self.test_record.id,'test.com')
        record=self.format_and_process(MAIL_TEMPLATE,self.partner_1.email_formatted,bounce_email_to,subject='UndeliveredMailReturnedtoSender')
        self.assertFalse(record)
        #Noinformationfoundinbounceemail->notpossibletodoanythingexceptavoidingemail
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_from_mailer_demon(self):
        """MAILER_DAEMONemailsareconsideredasbounce"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

        record=self.format_and_process(MAIL_TEMPLATE,'MAILER-DAEMON@example.com','groups@test.com',subject='UndeliveredMailReturnedtoSender')
        self.assertFalse(record)
        #Noinformationfoundinbounceemail->notpossibletodoanythingexceptavoidingemail
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_multipart_alias(self):
        """Multipart/reportbouncecorrectlymakerelatedpartnerbounce"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

        bounced_mail_id=4442
        bounce_email_to='%s+%s-%s-%s@%s'%('bounce.test',bounced_mail_id,self.test_record._name,self.test_record.id,'test.com')
        record=self.format_and_process(test_mail_data.MAIL_BOUNCE,self.partner_1.email_formatted,bounce_email_to,subject='UndeliveredMailReturnedtoSender')
        self.assertFalse(record)
        #Missinginreplytomessage_id->cannotfindoriginalrecord
        self.assertEqual(self.partner_1.message_bounce,1)
        self.assertEqual(self.test_record.message_bounce,0)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_multipart_alias_reply(self):
        """Multipart/reportbouncecorrectlymakerelatedpartnerandrecordfoundinbounceemailbounce"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

        bounced_mail_id=4442
        bounce_email_to='%s+%s-%s-%s@%s'%('bounce.test',bounced_mail_id,self.test_record._name,self.test_record.id,'test.com')
        extra=self.fake_email.message_id
        record=self.format_and_process(test_mail_data.MAIL_BOUNCE,self.partner_1.email_formatted,bounce_email_to,subject='UndeliveredMailReturnedtoSender',extra=extra)
        self.assertFalse(record)
        self.assertEqual(self.partner_1.message_bounce,1)
        self.assertEqual(self.test_record.message_bounce,1)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_multipart_alias_whatever_from(self):
        """Multipart/reportbouncecorrectlymakerelatedrecordfoundinbounceemailbounce"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

        bounced_mail_id=4442
        bounce_email_to='%s+%s-%s-%s@%s'%('bounce.test',bounced_mail_id,self.test_record._name,self.test_record.id,'test.com')
        extra=self.fake_email.message_id
        record=self.format_and_process(test_mail_data.MAIL_BOUNCE,'Whatever<what@ever.com>',bounce_email_to,subject='UndeliveredMailReturnedtoSender',extra=extra)
        self.assertFalse(record)
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,1)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_multipart_whatever_to_and_from(self):
        """Multipart/reportbouncecorrectlymakerelatedrecordfoundinbounceemailbounce"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,0)

        extra=self.fake_email.message_id
        record=self.format_and_process(test_mail_data.MAIL_BOUNCE,'Whatever<what@ever.com>','groups@test.com',subject='UndeliveredMailReturnedtoSender',extra=extra)
        self.assertFalse(record)
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(self.test_record.message_bounce,1)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_records_channel(self):
        """Testblacklistallowtomulti-bounceandautoupdateofmail.channel"""
        other_record=self.env['mail.test.gateway'].create({
            'email_from':'Anothername<%s>'%self.partner_1.email
        })
        yet_other_record=self.env['mail.test.gateway'].create({
            'email_from':'YetAnothername<%s>'%self.partner_1.email.upper()
        })
        test_channel=self.env['mail.channel'].create({
            'name':'Test',
            'channel_last_seen_partner_ids':[(0,0,{'partner_id':self.partner_1.id})],
        })
        self.fake_email.write({
            'model':'mail.channel',
            'res_id':test_channel.id,
        })
        self.assertIn(self.partner_1,test_channel.channel_partner_ids)
        self.assertEqual(self.partner_1.message_bounce,0)
        self.assertEqual(other_record.message_bounce,0)
        self.assertEqual(yet_other_record.message_bounce,0)

        extra=self.fake_email.message_id
        foriinrange(10):
            record=self.format_and_process(test_mail_data.MAIL_BOUNCE,'Athirdname<%s>'%self.partner_1.email,'groups@test.com',subject='UndeliveredMailReturnedtoSender',extra=extra)
            self.assertFalse(record)
        self.assertEqual(self.partner_1.message_bounce,10)
        self.assertEqual(self.test_record.message_bounce,0)
        self.assertEqual(other_record.message_bounce,10)
        self.assertEqual(yet_other_record.message_bounce,10)
        self.assertNotIn(self.partner_1,test_channel.channel_partner_ids)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_bounce_records_partner(self):
        """Testblacklist+bounceon``res.partner``model"""
        self.assertEqual(self.partner_1.message_bounce,0)
        self.fake_email.write({
            'model':'res.partner',
            'res_id':self.partner_1.id,
        })

        extra=self.fake_email.message_id
        record=self.format_and_process(test_mail_data.MAIL_BOUNCE,self.partner_1.email_formatted,'groups@test.com',subject='UndeliveredMailReturnedtoSender',extra=extra)
        self.assertFalse(record)
        self.assertEqual(self.partner_1.message_bounce,1)
        self.assertEqual(self.test_record.message_bounce,0)

    #--------------------------------------------------
    #Threadformation
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_in_reply_to(self):
        """Incomingemailusingin-rely-toshouldgointotherightdestinationevenwithawrongdestination"""
        init_msg_count=len(self.test_record.message_ids)
        self.format_and_process(
            MAIL_TEMPLATE,'valid.other@gmail.com','erroneous@test.com>',
            subject='Re:news',extra='In-Reply-To:\r\n\t%s\n'%self.fake_email.message_id)

        self.assertEqual(len(self.test_record.message_ids),init_msg_count+1)
        self.assertEqual(self.fake_email.child_ids,self.test_record.message_ids[0])

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_references(self):
        """Incomingemailusingreferencesshouldgointotherightdestinationevenwithawrongdestination"""
        init_msg_count=len(self.test_record.message_ids)
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'erroneous@test.com',
            extra='References:<2233@a.com>\r\n\t<3edss_dsa@b.com>%s'%self.fake_email.message_id)

        self.assertEqual(len(self.test_record.message_ids),init_msg_count+1)
        self.assertEqual(self.fake_email.child_ids,self.test_record.message_ids[0])

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_references_multi_parent(self):
        """Incomingemailwithmultiplereferences """
        reply1=self._create_gateway_message(
            self.test_record,'reply1',parent_id=self.fake_email.id,
        )
        reply2=self._create_gateway_message(
            self.test_record,'reply2',parent_id=self.fake_email.id,
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
        )
        reply1_1=self._create_gateway_message(
            self.test_record,'reply1_1',parent_id=reply1.id,
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
        )
        reply2_1=self._create_gateway_message(
            self.test_record,'reply2_1',parent_id=reply2.id,
        )

        #replytoreply1usingmultiplereferences
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'groups@test.com',
            subject='Replytoreply1',
            extra=f'References:{reply1.message_id}{self.fake_email.message_id}'
        )
        new_msg=self.test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,self.fake_email,'Mail:flatteningattachtooriginalmessage')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_comment'),'Mail:replytoacommentshouldbeacomment')

        #orderingshouldnotimpact
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'groups@test.com',
            subject='Replytoreply1(orderissue)',
            extra=f'References:{self.fake_email.message_id}{reply1.message_id}'
        )
        new_msg=self.test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,self.fake_email,'Mail:flatteningattachtooriginalmessage')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_comment'),'Mail:replytoacommentshouldbeacomment')

        #historywithlastonebeinganote
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'groups@test.com',
            subject='Replytoreply1_1',
            extra=f'References:{reply1_1.message_id}{self.fake_email.message_id}'
        )
        new_msg=self.test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,self.fake_email,'Mail:flatteningattachtooriginalmessage')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_note'),'Mail:replytoanoteshouldbeanote')

        #messeduphistory(twochildbranches):gatewayinitialparentisnewestone
        #(thenmaychangewithflatteningwhenpostingonrecord)
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'groups@test.com',
            subject='Replytoreply2_1(withnoise)',
            extra=f'References:{reply1_1.message_id}{reply2_1.message_id}'
        )
        new_msg=self.test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,self.fake_email,'Mail:flatteningattachtooriginalmessage')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_comment'),'Mail:parentshouldbeacomment(beforeflattening)')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_references_multi_parent_notflat(self):
        """Incomingemailwithmultiplereferenceswith``_mail_flat_thread``
        beingFalse(mail.group/mail.channelbehaviorlike)."""
        test_record=self.env['mail.test.gateway.groups'].create({
            'alias_name':'test.gateway',
            'name':'Test',
            'email_from':'ignasse@example.com',
        })

        #Setafirstmessageonpublicgrouptotestupdateandhierarchy
        first_msg=self._create_gateway_message(test_record,'first_msg')
        reply1=self._create_gateway_message(
            test_record,'reply1',parent_id=first_msg.id,
        )
        reply2=self._create_gateway_message(
            test_record,'reply2',parent_id=first_msg.id,
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
        )
        reply1_1=self._create_gateway_message(
            test_record,'reply1_1',parent_id=reply1.id,
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
        )
        reply2_1=self._create_gateway_message(
            test_record,'reply2_1',parent_id=reply2.id,
        )

        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.gateway@test.com',
            subject='Replytoreply1',
            extra=f'References:{reply1.message_id}'
        )
        new_msg=test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,first_msg,'Mail:pseudonoflattening:gettinguponelevel(reply1parent)')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_comment'),'Mail:parentshouldbeacomment')

        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.gateway@test.com',
            subject='Replytoreply1_1(withnoise)',
            extra=f'References:{reply1_1.message_id}{reply1.message_id}{reply1.message_id}'
        )
        new_msg=test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,reply1,'Mail:pseudonoflattening:gettinguponelevel(reply1_1parent)')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_note'),'Mail:replytoanoteshouldbeanote')

        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.gateway@test.com',
            subject='Replytoreply2_1(withnoise)',
            extra=f'References:{reply2_1.message_id}{reply1_1.message_id}'
        )
        new_msg=test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,reply2,'Mail:pseudonoflattening:gettinguponelevel(reply2_1parent')
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_comment'),'Mail:parentshouldbeacomment')

        #noreferences:newdiscussionthreadstarted
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.gateway@test.com',
            subject='Newthread',
            extra='References:'
        )
        new_thread=test_record.message_ids[0]
        self.assertFalse(new_thread.parent_id,'Mail:pseudonoflattening:noparentmeansnewthread')
        self.assertEqual(new_thread.subject,'Newthread')
        self.assertEqual(new_thread.subtype_id,self.env.ref('mail.mt_comment'),'Mail:parentshouldbeacomment')

        #mixedupreferences:newermessagewins
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.gateway@test.com',
            subject='Newthread',
            extra=f'References:{new_thread.message_id}{reply1_1.message_id}'
        )
        new_msg=test_record.message_ids[0]
        self.assertEqual(new_msg.parent_id,new_thread)
        self.assertEqual(new_msg.subtype_id,self.env.ref('mail.mt_comment'),'Mail:parentshouldbeacomment')

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_references_external(self):
        """Incomingemailbeingareplytoanexternalemailprocessedbyflectrashouldupdatethreadaccordingly"""
        new_message_id='<ThisIsTooMuchFake.MonsterEmail.789@agrolait.com>'
        self.fake_email.write({
            'message_id':new_message_id
        })
        init_msg_count=len(self.test_record.message_ids)
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'erroneous@test.com',
            extra='References:<2233@a.com>\r\n\t<3edss_dsa@b.com>%s'%self.fake_email.message_id)

        self.assertEqual(len(self.test_record.message_ids),init_msg_count+1)
        self.assertEqual(self.fake_email.child_ids,self.test_record.message_ids[0])

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_references_external_buggy_message_id(self):
        """
        Incomingemailbeingareplytoanexternalemailprocessedby
        flectrashouldupdatethreadaccordingly.Specialcasewhenthe
        externalmailservicewronglyfoldsthemessage_idonseveral
        lines.
        """
        new_message_id='<ThisIsTooMuchFake.MonsterEmail.789@agrolait.com>'
        buggy_message_id=new_message_id.replace('MonsterEmail','Monster\r\n Email')
        self.fake_email.write({
            'message_id':new_message_id
        })
        init_msg_count=len(self.test_record.message_ids)
        self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'erroneous@test.com',
            extra='References:<2233@a.com>\r\n\t<3edss_dsa@b.com>%s'%buggy_message_id)

        self.assertEqual(len(self.test_record.message_ids),init_msg_count+1)
        self.assertEqual(self.fake_email.child_ids,self.test_record.message_ids[0])

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_references_forward(self):
        """Incomingemailusingreferencesbutwithaliasforwardshouldnotgointoreferencesdestination"""
        self.env['mail.alias'].create({
            'alias_name':'test.alias',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })
        init_msg_count=len(self.test_record.message_ids)
        res_test=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.alias@test.com',
            subject='MyDearForward',extra='References:<2233@a.com>\r\n\t<3edss_dsa@b.com>%s'%self.fake_email.message_id,
            target_model='mail.test.container')

        self.assertEqual(len(self.test_record.message_ids),init_msg_count)
        self.assertEqual(len(self.fake_email.child_ids),0)
        self.assertEqual(res_test.name,'MyDearForward')
        self.assertEqual(len(res_test.message_ids),1)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_references_forward_same_model(self):
        """Incomingemailusingreferencesbutwithaliasforwardonsamemodelshouldbeconsideredasareply"""
        self.env['mail.alias'].create({
            'alias_name':'test.alias',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.gateway').id,
            'alias_contact':'everyone',
        })
        init_msg_count=len(self.test_record.message_ids)
        res_test=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'test.alias@test.com',
            subject='MyDearForward',extra='References:<2233@a.com>\r\n\t<3edss_dsa@b.com>%s'%self.fake_email.message_id,
            target_model='mail.test.container')

        self.assertEqual(len(self.test_record.message_ids),init_msg_count+1)
        self.assertEqual(len(self.fake_email.child_ids),1)
        self.assertFalse(res_test)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_references_forward_cc(self):
        """IncomingemailusingreferencesbutwithaliasforwardinCCshouldbeconsideredasarepy(To>Cc)"""
        self.env['mail.alias'].create({
            'alias_name':'test.alias',
            'alias_user_id':False,
            'alias_model_id':self.env['ir.model']._get('mail.test.container').id,
            'alias_contact':'everyone',
        })
        init_msg_count=len(self.test_record.message_ids)
        res_test=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'catchall.test@test.com',cc='test.alias@test.com',
            subject='MyDearForward',extra='References:<2233@a.com>\r\n\t<3edss_dsa@b.com>%s'%self.fake_email.message_id,
            target_model='mail.test.container')

        self.assertEqual(len(self.test_record.message_ids),init_msg_count+1)
        self.assertEqual(len(self.fake_email.child_ids),1)
        self.assertFalse(res_test)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_message_process_reply_to_new_thread(self):
        """Testrepliesnotbeingconsideredasrepliesbutusedestinationinformationinstead(aka,masspost+specificreplytousingaliases)"""
        first_record=self.env['mail.test.simple'].with_user(self.user_employee).create({'name':'RepliestoRecord'})
        record_msg=first_record.message_post(
            subject='Discussion',
            no_auto_thread=False,
            subtype_xmlid='mail.mt_comment',
        )
        self.assertEqual(record_msg.reply_to,formataddr(('%s%s'%(self.user_employee.company_id.name,first_record.name),'%s@%s'%('catchall.test','test.com'))))
        mail_msg=first_record.message_post(
            subject='RepliestoRecord',
            reply_to='groups@test.com',
            no_auto_thread=True,
            subtype_xmlid='mail.mt_comment',
        )
        self.assertEqual(mail_msg.reply_to,'groups@test.com')

        #replytomailbutshouldbeconsideredasanewmailforalias
        msgID='<this.is.duplicate.test@iron.sky>'
        res_test=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,record_msg.reply_to,cc='',
            subject='Re:RepliestoRecord',extra='In-Reply-To:%s'%record_msg.message_id,
            msg_id=msgID,target_model='mail.test.simple')
        incoming_msg=self.env['mail.message'].search([('message_id','=',msgID)])
        self.assertFalse(res_test)
        self.assertEqual(incoming_msg.model,'mail.test.simple')
        self.assertEqual(incoming_msg.parent_id,first_record.message_ids[-1])
        self.assertTrue(incoming_msg.res_id==first_record.id)

        #replytomailbutshouldbeconsideredasanewmailforalias
        msgID='<this.is.for.testing@iron.sky>'
        res_test=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,mail_msg.reply_to,cc='',
            subject='Re:RepliestoRecord',extra='In-Reply-To:%s'%mail_msg.message_id,
            msg_id=msgID,target_model='mail.test.gateway')
        incoming_msg=self.env['mail.message'].search([('message_id','=',msgID)])
        self.assertEqual(len(res_test),1)
        self.assertEqual(res_test.name,'Re:RepliestoRecord')
        self.assertEqual(incoming_msg.model,'mail.test.gateway')
        self.assertFalse(incoming_msg.parent_id)
        self.assertTrue(incoming_msg.res_id==res_test.id)

    #--------------------------------------------------
    #Gateway/Recordsynchronization
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_gateway_values_base64_image(self):
        """Newrecordwithmailthatcontainsbase64inlineimage."""
        target_model="mail.test.field.type"
        alias=self.env["mail.alias"].create({
            "alias_name":"base64-lover",
            "alias_model_id":self.env["ir.model"]._get(target_model).id,
            "alias_defaults":"{}",
            "alias_contact":"everyone",
        })
        record=self.format_and_process(
            test_mail_data.MAIL_TEMPLATE_EXTRA_HTML,self.email_from,
            '%s@%s'%(alias.alias_name,self.alias_catchall),
            subject='base64imagetoalias',
            target_model=target_model,
            extra_html='<imgsrc="data:image/png;base64,iV/+OkI=">',
        )
        self.assertEqual(record.type,"first")
        self.assertEqual(len(record.message_ids[0].attachment_ids),1)
        self.assertEqual(record.message_ids[0].attachment_ids[0].name,"image0")
        self.assertEqual(record.message_ids[0].attachment_ids[0].type,"binary")

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_gateway_values_base64_image_walias(self):
        """Newrecordwithmailthatcontainsbase64inlineimage+defaultvalues
        comingfromalias."""
        target_model="mail.test.field.type"
        alias=self.env["mail.alias"].create({
            "alias_name":"base64-lover",
            "alias_model_id":self.env["ir.model"]._get(target_model).id,
            "alias_defaults":"{'type':'second'}",
            "alias_contact":"everyone",
        })
        record=self.format_and_process(
            test_mail_data.MAIL_TEMPLATE_EXTRA_HTML,self.email_from,
            '%s@%s'%(alias.alias_name,self.alias_catchall),
            subject='base64imagetoalias',
            target_model=target_model,
            extra_html='<imgsrc="data:image/png;base64,iV/+OkI=">',
        )
        self.assertEqual(record.type,"second")
        self.assertEqual(len(record.message_ids[0].attachment_ids),1)
        self.assertEqual(record.message_ids[0].attachment_ids[0].name,"image0")
        self.assertEqual(record.message_ids[0].attachment_ids[0].type,"binary")

    #--------------------------------------------------
    #Threadformation:mailgatewaycornercases
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_extra_model_res_id(self):
        """Incomingemailwithrefholdingmodel/res_idbutthatdoesnotmatchanymessageinthethread:mustraisesinceOpenERPsaas-3"""
        self.assertRaises(ValueError,
                          self.format_and_process,MAIL_TEMPLATE,
                          self.partner_1.email_formatted,'noone@test.com',subject='spam',
                          extra='In-Reply-To:<12321321-openerp-%d-mail.test.gateway@%s>'%(self.test_record.id,socket.gethostname()))

        #when6.1messagesarepresent,compatmodeisavailable
        #Flectra10update:compatmodehasbeenremovedandshouldnotworkanymore
        self.fake_email.write({'message_id':False})
        #Do:compatmodeacceptspartial-matchingemails
        self.assertRaises(
            ValueError,
            self.format_and_process,MAIL_TEMPLATE,
            self.partner_1.email_formatted,'noone@test.com>',subject='spam',
            extra='In-Reply-To:<12321321-openerp-%d-mail.test.gateway@%s>'%(self.test_record.id,socket.gethostname()))

        #Testcreatedmessages
        self.assertEqual(len(self.test_record.message_ids),1)
        self.assertEqual(len(self.test_record.message_ids[0].child_ids),0)

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_duplicate(self):
        """Duplicateemails(samemessage_id)arenotprocessed"""
        self.alias.write({'alias_force_thread_id':self.test_record.id,})

        #Postabasemessage
        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='Re:supercats',msg_id='<123?456.diff1@agrolait.com>')
        self.assertFalse(record)
        self.assertEqual(len(self.test_record.message_ids),2)

        #Do:duetosomeissue,sameemailgoesbackintothemailgateway
        record=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'groups@test.com',subject='Re:news',
            msg_id='<123?456.diff1@agrolait.com>',extra='In-Reply-To:<1198923581.41972151344608186799.JavaMail.diff1@agrolait.com>\n')
        self.assertFalse(record)
        self.assertEqual(len(self.test_record.message_ids),2)

        #Test:message_idisstillunique
        no_of_msg=self.env['mail.message'].search_count([('message_id','ilike','<123?456.diff1@agrolait.com>')])
        self.assertEqual(no_of_msg,1,
                         'message_process:messagewithalreadyexistingmessage_idshouldnothavebeenduplicated')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_crash_wrong_model(self):
        """Incomingemailwithmodelthatdoesnotacceptsincomingemailsmustraise"""
        self.assertRaises(ValueError,
                          self.format_and_process,
                          MAIL_TEMPLATE,self.email_from,'noone@test.com',
                          subject='spam',extra='',model='res.country')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_crash_no_data(self):
        """Incomingemailwithoutmodelandwithoutaliasmustraise"""
        self.assertRaises(ValueError,
                          self.format_and_process,
                          MAIL_TEMPLATE,self.email_from,'noone@test.com',
                          subject='spam',extra='')

    @mute_logger('flectra.addons.mail.models.mail_thread','flectra.models')
    deftest_message_process_fallback(self):
        """Incomingemailwithmodelthatacceptingincomingemailsasfallback"""
        record=self.format_and_process(
            MAIL_TEMPLATE,self.email_from,'noone@test.com',
            subject='Spammy',extra='',model='mail.test.gateway')
        self.assertEqual(len(record),1)
        self.assertEqual(record.name,'Spammy')
        self.assertEqual(record._name,'mail.test.gateway')

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_file_encoding(self):
        """Incomingemailwithfileencoding"""
        file_content='HelloWorld'
        forencodingin['','UTF-8','UTF-16LE','UTF-32BE']:
            file_content_b64=base64.b64encode(file_content.encode(encodingor'utf-8')).decode()
            record=self.format_and_process(test_mail_data.MAIL_FILE_ENCODING,
                self.email_from,'groups@test.com',
                subject='TestCharset%s'%encodingor'Unset',
                charset=';charset="%s"'%encodingifencodingelse'',
                content=file_content_b64
            )
            attachment=record.message_ids.attachment_ids
            self.assertEqual(file_content,attachment.raw.decode(encodingor'utf-8'))
            ifencodingnotin['','UTF-8']:
                self.assertNotEqual(file_content,attachment.raw.decode('utf-8'))

    #--------------------------------------------------
    #Cornercases/Bugsduringmessageprocess
    #--------------------------------------------------

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_process_file_encoding_ascii(self):
        """Incomingemailcontaininganxmlattachmentwithunknowncharacters(�)butanASCIIcharsetshouldnot
        raiseanException.UTF-8isusedasasafefallback.
        """
        record=self.format_and_process(test_mail_data.MAIL_MULTIPART_INVALID_ENCODING,self.email_from,'groups@test.com')

        self.assertEqual(record.message_main_attachment_id.name,'bis3_with_error_encoding_address.xml')
        #NB:thexmlreceivedbyemailcontainsb"Chauss\xef\xbf\xbd\xef\xbf\xbde"with"\xef\xbf\xbd"beingthe
        #replacementcharacter�inUTF-8.
        #Whencalling`_message_parse_extract_payload`,`part.get_content()`willbecalledontheattachmentpartof
        #theemail,triggeringthedecodingofthebase64attachment,sob"Chauss\xef\xbf\xbd\xef\xbf\xbde"is
        #firstretrieved.Then,`get_text_content`in`email`triestodecodethisusingthecharsetoftheemail
        #part,i.e:`content.decode('us-ascii',errors='replace')`.SotheerrorsarereplacedusingtheUnicode
        #replacementmarkerandthestring"Chauss������e"isusedtocreatetheattachment.
        #Thisexplainsthemultiple"�"intheattachment.
        self.assertIn("Chauss������edeBruxelles",record.message_main_attachment_id.raw.decode())

    deftest_message_process_file_omitted_charset(self):
        """ForincomingemailcontaininganxmlattachmentwithomittedcharsetandcontaininganUTF8payloadwe
        shouldparsetheattachmentusingUTF-8.
        """
        record=self.format_and_process(test_mail_data.MAIL_MULTIPART_OMITTED_CHARSET,self.email_from,'groups@test.com')
        self.assertEqual(record.message_main_attachment_id.name,'bis3.xml')
        self.assertEqual("<Invoice>ChausséedeBruxelles</Invoice>",record.message_main_attachment_id.raw.decode())

@tagged('mail_gateway','mail_thread')
classTestMailThreadCC(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailThreadCC,cls).setUpClass()

        cls.email_from='SylvieLelitre<test.sylvie.lelitre@agrolait.com>'
        cls.alias=cls.env['mail.alias'].create({
            'alias_name':'cc_record',
            'alias_user_id':False,
            'alias_model_id':cls.env['ir.model']._get('mail.test.cc').id,
            'alias_contact':'everyone'})

        cls._init_mail_gateway()

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_cc_new(self):
        record=self.format_and_process(MAIL_TEMPLATE,self.email_from,'cc_record@test.com',
                                         cc='cc1@example.com,cc2@example.com',target_model='mail.test.cc')
        cc=email_split_and_format(record.email_cc)
        self.assertEqual(sorted(cc),['cc1@example.com','cc2@example.com'])

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_cc_update_with_old(self):
        record=self.env['mail.test.cc'].create({'email_cc':'cc1<cc1@example.com>,cc2@example.com'})
        self.alias.write({'alias_force_thread_id':record.id})

        self.format_and_process(MAIL_TEMPLATE,self.email_from,'cc_record@test.com',
                                cc='cc2<cc2@example.com>,cc3@example.com',target_model='mail.test.cc')
        cc=email_split_and_format(record.email_cc)
        self.assertEqual(sorted(cc),['"cc1"<cc1@example.com>','cc2@example.com','cc3@example.com'],'newccshouldhavebeenaddedonrecord(unique)')

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_message_cc_update_no_old(self):
        record=self.env['mail.test.cc'].create({})
        self.alias.write({'alias_force_thread_id':record.id})

        self.format_and_process(MAIL_TEMPLATE,self.email_from,'cc_record@test.com',
                                cc='cc2<cc2@example.com>,cc3@example.com',target_model='mail.test.cc')
        cc=email_split_and_format(record.email_cc)
        self.assertEqual(sorted(cc),['"cc2"<cc2@example.com>','cc3@example.com'],'newccshouldhavebeenaddedonrecord(unique)')
