#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.toolsimportmute_logger


classTestMailTemplate(TestMailCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestMailTemplate,cls).setUpClass()
        cls.test_record=cls.env['mail.test.simple'].with_context(cls._test_context).create({'name':'Test','email_from':'ignasse@example.com'})

        cls.user_employee.write({
            'groups_id':[(4,cls.env.ref('base.group_partner_manager').id)],
        })

        cls._attachments=[{
            'name':'first.txt',
            'datas':base64.b64encode(b'Myfirstattachment'),
            'res_model':'res.partner',
            'res_id':cls.user_admin.partner_id.id
        },{
            'name':'second.txt',
            'datas':base64.b64encode(b'Mysecondattachment'),
            'res_model':'res.partner',
            'res_id':cls.user_admin.partner_id.id
        }]

        cls.email_1='test1@example.com'
        cls.email_2='test2@example.com'
        cls.email_3=cls.partner_1.email
        cls._create_template('mail.test.simple',{
            'attachment_ids':[(0,0,cls._attachments[0]),(0,0,cls._attachments[1])],
            'partner_to':'%s,%s'%(cls.partner_2.id,cls.user_admin.partner_id.id),
            'email_to':'%s,%s'%(cls.email_1,cls.email_2),
            'email_cc':'%s'%cls.email_3,
        })

        #adminshouldreceiveemails
        cls.user_admin.write({'notification_type':'email'})
        #Forcetheattachmentsofthetemplatetobeinthenaturalorder.
        cls.email_template.invalidate_cache(['attachment_ids'],ids=cls.email_template.ids)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_template_send_email(self):
        mail_id=self.email_template.send_mail(self.test_record.id)
        mail=self.env['mail.mail'].sudo().browse(mail_id)
        self.assertEqual(mail.subject,'About%s'%self.test_record.name)
        self.assertEqual(mail.email_to,self.email_template.email_to)
        self.assertEqual(mail.email_cc,self.email_template.email_cc)
        self.assertEqual(mail.recipient_ids,self.partner_2|self.user_admin.partner_id)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_template_translation(self):
        self.env['res.lang']._activate_lang('es_ES')
        self.env.ref('base.module_base')._update_translations(['es_ES'])

        partner=self.env['res.partner'].create({'name':"test",'lang':'es_ES'})
        email_template=self.env['mail.template'].create({
            'name':'TestTemplate',
            'subject':'EnglishSubject',
            'body_html':'<p>EnglishBody</p>',
            'model_id':self.env['ir.model']._get(partner._name).id,
            'lang':'${object.lang}'
        })
        #MakesureSpanishtranslationshavenotbeenaltered
        description_translations=self.env['ir.translation'].search([('module','=','base'),('src','=',partner._description),('lang','=','es_ES')])
        description_translations.update({'value':'Spanishdescription'})

        self.env['ir.translation'].create({
            'type':'model',
            'name':'mail.template,subject',
            'module':'mail',
            'lang':'es_ES',
            'res_id':email_template.id,
            'value':'SpanishSubject',
            'state':'translated',
        })
        self.env['ir.translation'].create({
            'type':'model',
            'name':'mail.template,body_html',
            'module':'mail',
            'lang':'es_ES',
            'res_id':email_template.id,
            'value':'<p>SpanishBody</p>',
            'state':'translated',
        })
        view=self.env['ir.ui.view'].create({
            'name':'test_layout',
            'key':'test_layout',
            'type':'qweb',
            'arch_db':'<body><tt-raw="message.body"/>EnglishLayout<tt-esc="model_description"/></body>'
        })
        self.env['ir.model.data'].create({
            'name':'test_layout',
            'module':'test_mail',
            'model':'ir.ui.view',
            'res_id':view.id
        })
        self.env['ir.translation'].create({
            'type':'model_terms',
            'name':'ir.ui.view,arch_db',
            'module':'test_mail',
            'lang':'es_ES',
            'res_id':view.id,
            'src':'EnglishLayout',
            'value':'SpanishLayout',
            'state':'translated',
        })

        mail_id=email_template.send_mail(partner.id,notif_layout='test_mail.test_layout')
        mail=self.env['mail.mail'].sudo().browse(mail_id)
        self.assertEqual(mail.subject,'SpanishSubject')
        self.assertEqual(mail.body_html,'<body><p>SpanishBody</p>SpanishLayoutSpanishdescription</body>')

    deftest_template_add_context_action(self):
        self.email_template.create_action()

        #checktemplateact_windowhasbeenupdated
        self.assertTrue(bool(self.email_template.ref_ir_act_window))

        #checkthoserecords
        action=self.email_template.ref_ir_act_window
        self.assertEqual(action.name,'SendMail(%s)'%self.email_template.name)
        self.assertEqual(action.binding_model_id.model,'mail.test.simple')

    #deftest_template_scheduled_date(self):
    #    fromunittest.mockimportpatch

    #    self.email_template_in_2_days=self.email_template.copy()

    #    withpatch('flectra.addons.mail.tests.test_mail_template.datetime',wraps=datetime)asmock_datetime:
    #        mock_datetime.now.return_value=datetime(2017,11,15,11,30,28)
    #        mock_datetime.side_effect=lambda*args,**kw:datetime(*args,**kw)

    #        self.email_template_in_2_days.write({
    #            'scheduled_date':"${(datetime.datetime.now()+relativedelta(days=2)).strftime('%s')}"%DEFAULT_SERVER_DATETIME_FORMAT,
    #        })

    #        mail_now_id=self.email_template.send_mail(self.test_record.id)
    #        mail_in_2_days_id=self.email_template_in_2_days.send_mail(self.test_record.id)

    #        mail_now=self.env['mail.mail'].browse(mail_now_id)
    #        mail_in_2_days=self.env['mail.mail'].browse(mail_in_2_days_id)

    #        #mailpreparation
    #        self.assertEqual(mail_now.exists()|mail_in_2_days.exists(),mail_now|mail_in_2_days)
    #        self.assertEqual(bool(mail_now.scheduled_date),False)
    #        self.assertEqual(mail_now.state,'outgoing')
    #        self.assertEqual(mail_in_2_days.state,'outgoing')
    #        scheduled_date=datetime.strptime(mail_in_2_days.scheduled_date,DEFAULT_SERVER_DATETIME_FORMAT)
    #        date_in_2_days=datetime.now()+timedelta(days=2)
    #        self.assertEqual(scheduled_date,date_in_2_days)
    #        #self.assertEqual(scheduled_date.month,date_in_2_days.month)
    #        #self.assertEqual(scheduled_date.year,date_in_2_days.year)

    #        #Launchthescheduleronthefirstmail,itshouldbereportedinself.mails
    #        #andthemail_mailisnowdeleted
    #        self.env['mail.mail'].process_email_queue()
    #        self.assertEqual(mail_now.exists()|mail_in_2_days.exists(),mail_in_2_days)

    #        #Launchthescheduleronthefirstmail,it'sstillin'outgoing'state
    #        self.env['mail.mail'].process_email_queue(ids=[mail_in_2_days.id])
    #        self.assertEqual(mail_in_2_days.state,'outgoing')
    #        self.assertEqual(mail_now.exists()|mail_in_2_days.exists(),mail_in_2_days)
