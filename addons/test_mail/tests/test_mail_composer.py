#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromunittest.mockimportpatch

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.test_mail.models.test_mail_modelsimportMailTestTicket
fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.testsimporttagged
fromflectra.tests.commonimportusers,Form
fromflectra.toolsimportmute_logger,formataddr

@tagged('mail_composer')
classTestMailComposer(TestMailCommon,TestRecipients):
    """TestComposerinternals"""

    @classmethod
    defsetUpClass(cls):
        super(TestMailComposer,cls).setUpClass()
        cls._init_mail_gateway()

        #ensureemployeecancreatepartners,necessaryfortemplates
        cls.user_employee.write({
            'groups_id':[(4,cls.env.ref('base.group_partner_manager').id)],
        })

        cls.user_employee_2=mail_new_test_user(
            cls.env,login='employee2',groups='base.group_user',
            notification_type='email',email='eglantine@example.com',
            name='EglantineEmployee',signature='--\nEglantine')
        cls.partner_employee_2=cls.user_employee_2.partner_id

        cls.test_record=cls.env['mail.test.ticket'].with_context(cls._test_context).create({
            'name':'TestRecord',
            'customer_id':cls.partner_1.id,
            'user_id':cls.user_employee_2.id,
        })
        cls.test_records,cls.test_partners=cls._create_records_for_batch('mail.test.ticket',2)

        cls.test_report=cls.env['ir.actions.report'].create({
            'name':'TestReportonmailtestticket',
            'model':'mail.test.ticket',
            'report_type':'qweb-pdf',
            'report_name':'test_mail.mail_test_ticket_test_template',
        })
        cls.test_record_report=cls.test_report._render_qweb_pdf(cls.test_report.ids)

        cls.test_from='"JohnDoe"<john@example.com>'

        cls.mail_server=cls.env['ir.mail_server'].create({
            'name':'DummyTestServer',
            'smtp_host':'smtp.pizza.moc',
            'smtp_port':17,
            'smtp_encryption':'ssl',
            'sequence':666,
        })

        cls.template=cls.env['mail.template'].create({
            'name':'TestTemplate',
            'subject':'TemplateSubject${object.name}',
            'body_html':'<p>TemplateBody${object.name}</p>',
            'partner_to':'${object.customer_id.idifobject.customer_idelse""}',
            'email_to':'${(object.email_fromifnotobject.customer_idelse"")|safe}',
            'email_from':'${(object.user_id.email_formattedoruser.email_formatted)|safe}',
            'model_id':cls.env['ir.model']._get('mail.test.ticket').id,
            'mail_server_id':cls.mail_server.id,
            'auto_delete':True,
        })

    def_generate_attachments_data(self,count):
        return[{
            'name':'%02d.txt'%x,
            'datas':base64.b64encode(b'Att%02d'%x),
        }forxinrange(count)]

    def_get_web_context(self,records,add_web=True,**values):
        """Helpertogeneratecomposercontext.Willmaketestsabitless
        verbose.

        :paramadd_web:addwebcontext,generallymakingnoiseespeciallyin
          massmailmode(active_id/idsbothpresentincontext)
        """
        base_context={
            'default_model':records._name,
        }
        iflen(records)==1:
            base_context['default_composition_mode']='comment'
            base_context['default_res_id']=records.id
        else:
            base_context['default_composition_mode']='mass_mail'
            base_context['active_ids']=records.ids
        ifadd_web:
            base_context['active_model']=records._name
            base_context['active_id']=records[0].id
        ifvalues:
            base_context.update(**values)
        returnbase_context


@tagged('mail_composer')
classTestComposerForm(TestMailComposer):

    @users('employee')
    deftest_mail_composer_comment(self):
        composer_form=Form(self.env['mail.compose.message'].with_context(self._get_web_context(self.test_record,add_web=True)))
        self.assertEqual(
            composer_form.subject,'Re:%s'%self.test_record.name,
            'MailComposer:commentmodeshouldhavedefaultsubjectRe:record_name')
        #recordnamenotdisplayedcurrentlyinview
        #self.assertEqual(composer_form.record_name,self.test_record.name,'MailComposer:commentmodeshouldcomputerecordname')
        self.assertFalse(composer_form.no_auto_thread)
        self.assertEqual(composer_form.composition_mode,'comment')
        self.assertEqual(composer_form.model,self.test_record._name)

    @users('employee')
    deftest_mail_composer_comment_attachments(self):
        """Teststhatallattachmentsareaddedtothecomposer,staticattachments
        arenotduplicatedandwhilereportsarere-generated,andthatintermediary
        attachmentsaredropped."""
        attachment_data=self._generate_attachments_data(2)
        template_1=self.template.copy({
            'attachment_ids':[(0,0,a)forainattachment_data],
            'report_name':'TestReportfor${object.name}.html', #testcursorforceshtml
            'report_template':self.test_report.id,
        })
        template_1_attachments=template_1.attachment_ids
        self.assertEqual(len(template_1_attachments),2)
        template_2=self.template.copy({
            'attachment_ids':False,
            'report_template':self.test_report.id,
        })

        #beginswithoutattachments
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record,add_web=True,default_attachment_ids=[])
        ))
        self.assertEqual(len(composer_form.attachment_ids),0)

        #changetemplate:2static(attachment_ids)and1dynamic(report)
        composer_form.template_id=template_1
        self.assertEqual(len(composer_form.attachment_ids),3)
        report_attachments=[attforattincomposer_form.attachment_idsifattnotintemplate_1_attachments]
        self.assertEqual(len(report_attachments),1)
        tpl_attachments=composer_form.attachment_ids[:]-report_attachments[0]
        self.assertEqual(tpl_attachments,template_1_attachments)

        #changetemplate:0static(attachment_ids)and1dynamic(report)
        composer_form.template_id=template_2
        self.assertEqual(len(composer_form.attachment_ids),1)
        report_attachments=[attforattincomposer_form.attachment_idsifattnotintemplate_1_attachments]
        self.assertEqual(len(report_attachments),1)
        tpl_attachments=composer_form.attachment_ids[:]-report_attachments[0]
        self.assertEqual(tpl_attachments,self.env['ir.attachment'])

        #changebacktotemplate1
        composer_form.template_id=template_1
        self.assertEqual(len(composer_form.attachment_ids),3)
        report_attachments=[attforattincomposer_form.attachment_idsifattnotintemplate_1_attachments]
        self.assertEqual(len(report_attachments),1)
        tpl_attachments=composer_form.attachment_ids[:]-report_attachments[0]
        self.assertEqual(tpl_attachments,template_1_attachments)

        #resettemplate
        composer_form.template_id=self.env['mail.template']
        self.assertEqual(len(composer_form.attachment_ids),0)

    @users('employee')
    deftest_mail_composer_mass(self):
        composer_form=Form(self.env['mail.compose.message'].with_context(self._get_web_context(self.test_records,add_web=True)))
        self.assertFalse(composer_form.subject,'MailComposer:massmodeshouldhavevoiddefaultsubjectifnotemplate')
        #recordnamenotdisplayedcurrentlyinview
        #self.assertFalse(composer_form.record_name,'MailComposer:massmodeshouldhavevoidrecordname')
        self.assertFalse(composer_form.no_auto_thread)
        self.assertEqual(composer_form.composition_mode,'mass_mail')
        self.assertEqual(composer_form.model,self.test_records._name)

    @users('employee')
    deftest_mail_composer_mass_wtpl(self):
        ctx=self._get_web_context(self.test_records,add_web=True,default_template_id=self.template.id)
        composer_form=Form(self.env['mail.compose.message'].with_context(ctx))
        self.assertEqual(composer_form.subject,self.template.subject,
                         'MailComposer:massmodeshouldhavetemplaterawsubjectiftemplate')
        self.assertEqual(composer_form.body,self.template.body_html,
                         'MailComposer:massmodeshouldhavetemplaterawbodyiftemplate')
        #recordnamenotdisplayedcurrentlyinview
        #self.assertFalse(composer_form.record_name,'MailComposer:massmodeshouldhavevoidrecordname')
        self.assertFalse(composer_form.no_auto_thread)
        self.assertEqual(composer_form.composition_mode,'mass_mail')
        self.assertEqual(composer_form.model,self.test_records._name)


@tagged('mail_composer')
classTestComposerInternals(TestMailComposer):

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_attachments_comment(self):
        """Testattachmentsmanagementincommentmode."""
        attachment_data=self._generate_attachments_data(3)
        self.template.write({
            'attachment_ids':[(0,0,a)forainattachment_data],
            'report_name':'TestReportfor${object.name}.html', #testcursorforceshtml
            'report_template':self.test_report.id,
        })
        attachs=self.env['ir.attachment'].search([('name','in',[a['name']forainattachment_data])])
        self.assertEqual(len(attachs),3)

        composer=self.env['mail.compose.message'].with_context({
            'default_composition_mode':'comment',
            'default_model':self.test_record._name,
            'default_res_id':self.test_record.id,
            'default_template_id':self.template.id,
        }).create({
            'body':'<p>TestBody</p>',
        })
        #currentlyonchangenecessary
        composer.onchange_template_id_wrapper()

        #valuescomingfromtemplate
        self.assertEqual(len(composer.attachment_ids),4)
        forattachinattachs:
            self.assertIn(attach,composer.attachment_ids)
        generated=composer.attachment_ids-attachs
        self.assertEqual(len(generated),1,'MailComposer:shouldhave1additionalattachmentforreport')
        self.assertEqual(generated.name,'TestReportfor%s.html'%self.test_record.name)
        self.assertEqual(generated.res_model,'mail.compose.message')
        self.assertEqual(generated.res_id,0)

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_author(self):
        """Testauthor_id/email_fromsynchronization,inbothcommentandmassmail
        modes."""
        forcomposition_modein['comment','mass_mail']:
            ifcomposition_mode=='comment':
                ctx=self._get_web_context(self.test_record,add_web=False)
            else:
                ctx=self._get_web_context(self.test_records,add_web=False)
            composer=self.env['mail.compose.message'].with_context(ctx).create({
                'body':'<p>TestBody</p>',
            })

            #defaultvaluesarecurrentuser
            self.assertEqual(composer.author_id,self.env.user.partner_id)
            self.assertEqual(composer.email_from,self.env.user.email_formatted)

            #authorvaluesresetemail(FIXME:currentlynotsynchronized)
            composer.write({'author_id':self.partner_1})
            self.assertEqual(composer.author_id,self.partner_1)
            self.assertEqual(composer.email_from,self.env.user.email_formatted)
            #self.assertEqual(composer.email_from,self.partner_1.email_formatted)

            #changingtemplateshouldupdateitsemail_from
            composer.write({'template_id':self.template.id,'author_id':self.env.user.partner_id})
            #currentlyonchangenecessary
            composer.onchange_template_id_wrapper()
            self.assertEqual(composer.author_id,self.env.user.partner_id,
                             'MailComposer:shouldtakevaluegivenbyuser')
            ifcomposition_mode=='comment':
                self.assertEqual(composer.email_from,self.test_record.user_id.email_formatted,
                                 'MailComposer:shouldtakeemail_fromrenderedfromtemplate')
            else:
                self.assertEqual(composer.email_from,self.template.email_from,
                                 'MailComposer:shouldtakeemail_fromrawfromtemplate')

            #manualvaluesarekeptovertemplatevalues
            composer.write({'email_from':self.test_from})
            self.assertEqual(composer.author_id,self.env.user.partner_id)
            self.assertEqual(composer.email_from,self.test_from)

    @users('employee')
    deftest_mail_composer_content(self):
        """Testcontentmanagement(subject,body,server)inbothcommentand
        massmailingmode.Templateupdateisalsotested."""
        forcomposition_modein['comment','mass_mail']:
            ifcomposition_mode=='comment':
                ctx=self._get_web_context(self.test_record,add_web=False)
            else:
                ctx=self._get_web_context(self.test_records,add_web=False)

            #1.checkwithouttemplate+templateupdate
            composer=self.env['mail.compose.message'].with_context(ctx).create({
                'subject':'Myamazingsubject',
                'body':'<p>TestBody</p>',
            })

            #creationvaluesaretaken
            self.assertEqual(composer.subject,'Myamazingsubject')
            self.assertEqual(composer.body,'<p>TestBody</p>')
            self.assertEqual(composer.mail_server_id.id,False)

            #changingtemplateshouldupdateitscontent
            composer.write({'template_id':self.template.id})
            #currentlyonchangenecessary
            composer.onchange_template_id_wrapper()

            #valuescomefromtemplate
            ifcomposition_mode=='comment':
                self.assertEqual(composer.subject,'TemplateSubject%s'%self.test_record.name)
                self.assertEqual(composer.body,'<p>TemplateBody%s</p>'%self.test_record.name)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)
            else:
                self.assertEqual(composer.subject,self.template.subject)
                self.assertEqual(composer.body,self.template.body_html)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)

            #manualvaluesiskeptovertemplate
            composer.write({'subject':'Backtomyamazingsubject'})
            self.assertEqual(composer.subject,'Backtomyamazingsubject')

            #resettemplateshouldresetvalues
            composer.write({'template_id':False})
            #currentlyonchangenecessary
            composer.onchange_template_id_wrapper()

            #valuesarereset
            ifcomposition_mode=='comment':
                self.assertEqual(composer.subject,'Re:%s'%self.test_record.name)
                self.assertEqual(composer.body,'')
                #TDEFIXME:serveridiskept,notsurewhy
                #self.assertFalse(composer.mail_server_id.id)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)
            else:
                #valuesareresetTDEFIXME:strangeforsubject
                self.assertEqual(composer.subject,'Backtomyamazingsubject')
                self.assertEqual(composer.body,'')
                #TDEFIXME:serveridiskept,notsurewhy
                #self.assertFalse(composer.mail_server_id.id)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)

            #2.checkwithdefault
            ctx['default_template_id']=self.template.id
            composer=self.env['mail.compose.message'].with_context(ctx).create({
                'template_id':self.template.id,
            })
            #currentlyonchangenecessary
            composer.onchange_template_id_wrapper()

            #valuescomefromtemplate
            ifcomposition_mode=='comment':
                self.assertEqual(composer.subject,'TemplateSubject%s'%self.test_record.name)
                self.assertEqual(composer.body,'<p>TemplateBody%s</p>'%self.test_record.name)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)
            else:
                self.assertEqual(composer.subject,self.template.subject)
                self.assertEqual(composer.body,self.template.body_html)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)

            #3.checkatcreate
            ctx.pop('default_template_id')
            composer=self.env['mail.compose.message'].with_context(ctx).create({
                'template_id':self.template.id,
            })
            #currentlyonchangenecessary
            composer.onchange_template_id_wrapper()

            #valuescomefromtemplate
            ifcomposition_mode=='comment':
                self.assertEqual(composer.subject,'TemplateSubject%s'%self.test_record.name)
                self.assertEqual(composer.body,'<p>TemplateBody%s</p>'%self.test_record.name)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)
            else:
                self.assertEqual(composer.subject,self.template.subject)
                self.assertEqual(composer.body,self.template.body_html)
                self.assertEqual(composer.mail_server_id,self.template.mail_server_id)

            #4.template+userinput
            ctx['default_template_id']=self.template.id
            composer=self.env['mail.compose.message'].with_context(ctx).create({
                'subject':'Myamazingsubject',
                'body':'<p>TestBody</p>',
                'mail_server_id':False,
            })

            #creationvaluesaretaken
            self.assertEqual(composer.subject,'Myamazingsubject')
            self.assertEqual(composer.body,'<p>TestBody</p>')
            self.assertEqual(composer.mail_server_id.id,False)

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink','flectra.tests')
    deftest_mail_composer_parent(self):
        """Testspecificmanagementincommentmodewhenhavingparent_idset:
        record_name,subject,parent'spartners."""
        parent=self.test_record.message_post(body='Test',partner_ids=(self.partner_1+self.partner_2).ids)

        composer=self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record,add_web=False,default_parent_id=parent.id)
        ).create({
            'body':'<p>TestBody</p>',
        })

        #creationvaluestakenfromparent
        self.assertEqual(composer.subject,'Re:%s'%self.test_record.name)
        self.assertEqual(composer.body,'<p>TestBody</p>')
        self.assertEqual(composer.partner_ids,self.partner_1+self.partner_2)

    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink','flectra.tests')
    deftest_mail_composer_rights_portal(self):
        portal_user=self._create_portal_user()

        withpatch.object(MailTestTicket,'check_access_rights',return_value=True):
            self.env['mail.compose.message'].with_user(portal_user).with_context(
                self._get_web_context(self.test_record)
            ).create({
                'subject':'Subject',
                'body':'<p>Bodytext</p>',
                'partner_ids':[]
            }).send_mail()

            self.assertEqual(self.test_record.message_ids[0].body,'<p>Bodytext</p>')
            self.assertEqual(self.test_record.message_ids[0].author_id,portal_user.partner_id)

            self.env['mail.compose.message'].with_user(portal_user).with_context({
                'default_composition_mode':'comment',
                'default_parent_id':self.test_record.message_ids.ids[0],
            }).create({
                'subject':'Subject',
                'body':'<p>Bodytext2</p>'
            }).send_mail()

            self.assertEqual(self.test_record.message_ids[0].body,'<p>Bodytext2</p>')
            self.assertEqual(self.test_record.message_ids[0].author_id,portal_user.partner_id)

    @users('employee')
    deftest_mail_composer_save_template(self):
        self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record,add_web=False)
        ).create({
            'subject':'TemplateSubject',
            'body':'<p>TemplateBody</p>',
        }).save_as_template()

        #Test:email_templatesubject,body_html,model
        template=self.env['mail.template'].search([
            ('model','=',self.test_record._name),
            ('subject','=','TemplateSubject')
        ],limit=1)
        self.assertEqual(template.name,"%s:%s"%(self.env['ir.model']._get(self.test_record._name).name,'TemplateSubject'))
        self.assertEqual(template.body_html,'<p>TemplateBody</p>','email_templateincorrectbody_html')


@tagged('mail_composer')
classTestComposerResultsComment(TestMailComposer):
    """Testglobaloutputofcomposerusedincommentmode.Testnotably
    notificationandemailsgeneratedduringthisprocess."""

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink','flectra.tests')
    deftest_mail_composer_notifications_delete(self):
        """Notificationsarecorrectlydeletedoncesent"""
        composer=self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record)
        ).create({
            'body':'<p>TestBody</p>',
            'partner_ids':[(4,self.partner_1.id),(4,self.partner_2.id)]
        })
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #notifications
        message=self.test_record.message_ids[0]
        self.assertEqual(message.notified_partner_ids,self.partner_employee_2+self.partner_1+self.partner_2)

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated2mail.mail(1forusers,1forcustomers)')
        self.assertEqual(len(self._mails),3,'Shouldhavesentanemaileachrecipient')
        self.assertEqual(self._new_mails.exists(),self.env['mail.mail'],'Shouldhavedeletedmail.mailrecords')

        #ensure``mail_auto_delete``contextkeyallowtooverridethisbehavior
        composer=self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record),
            mail_auto_delete=False,
        ).create({
            'body':'<p>TestBody</p>',
            'partner_ids':[(4,self.partner_1.id),(4,self.partner_2.id)]
        })
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #notifications
        message=self.test_record.message_ids[0]
        self.assertEqual(message.notified_partner_ids,self.partner_employee_2+self.partner_1+self.partner_2)

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated2mail.mail(1forusers,1forcustomers)')
        self.assertEqual(len(self._mails),3,'Shouldhavesentanemaileachrecipient')
        self.assertEqual(len(self._new_mails.exists()),2,'Shouldnothavedeletedmail.mailrecords')

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail','flectra.models.unlink','flectra.tests')
    deftest_mail_composer_recipients(self):
        """Testpartner_idsgiventocomposeraregiventothefinalmessage."""
        composer=self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record)
        ).create({
            'body':'<p>TestBody</p>',
            'partner_ids':[(4,self.partner_1.id),(4,self.partner_2.id)]
        })
        composer.send_mail()

        message=self.test_record.message_ids[0]
        self.assertEqual(message.body,'<p>TestBody</p>')
        self.assertEqual(message.author_id,self.user_employee.partner_id)
        self.assertEqual(message.subject,'Re:%s'%self.test_record.name)
        self.assertEqual(message.subtype_id,self.env.ref('mail.mt_comment'))
        self.assertEqual(message.partner_ids,self.partner_1|self.partner_2)

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_complete(self):
        """Testapostingprocessusingacomplextemplate,holdingseveral
        additionalrecipientsandattachments.

        Thistestsnotifies:2newemail_to(+1duplicated),1email_cc,
        test_recordfollowersandpartner_adminaddedinpartner_to."""
        attachment_data=self._generate_attachments_data(2)
        email_to_1='test.to.1@test.example.com'
        email_to_2='test.to.2@test.example.com'
        email_to_3='test.to.1@test.example.com' #duplicate:shouldnotsenttwicetheemail
        email_cc_1='test.cc.1@test.example.com'
        self.template.write({
            'auto_delete':False, #keepsentemailstocheckcontent
            'attachment_ids':[(0,0,a)forainattachment_data],
            'email_to':'%s,%s,%s'%(email_to_1,email_to_2,email_to_3),
            'email_cc':email_cc_1,
            'partner_to':'%s,${object.customer_id.idifobject.customer_idelse""}'%self.partner_admin.id,
            'report_name':'TestReportfor${object.name}', #testcursorforceshtml
            'report_template':self.test_report.id,
        })
        attachs=self.env['ir.attachment'].search([('name','in',[a['name']forainattachment_data])])
        self.assertEqual(len(attachs),2)

        #ensureinitialdata
        self.assertEqual(self.test_record.user_id,self.user_employee_2)
        self.assertEqual(self.test_record.message_partner_ids,self.partner_employee_2)

        #openacomposerandrunitincommentmode
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_record,add_web=True,
                                  default_template_id=self.template.id)
        ))
        composer=composer_form.save()
        self.assertFalse(composer.no_auto_thread,'Mail:thread-enabledmodelsshoulduseautothreadbydefault')
        withself.mock_mail_gateway(mail_unlink_sent=False),self.mock_mail_app():
            composer.send_mail()

        #checknewpartnershavebeencreatedbasedonemailsgiven
        new_partners=self.env['res.partner'].search([
            ('email','in',[email_to_1,email_to_2,email_to_3,email_cc_1])
        ])
        self.assertEqual(len(new_partners),3)
        self.assertEqual(set(new_partners.mapped('email')),
                         set(['test.to.1@test.example.com','test.to.2@test.example.com','test.cc.1@test.example.com'])
                        )

        #globaloutgoing:onemail.mail(allcustomerrecipients,thenallemployeerecipients)
        #and5emails,and1inboxnotification(admin)
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mail')
        self.assertEqual(len(self._mails),5,'Shouldhavesent5emails,oneperrecipient')

        #templateissentonlytopartners(email_toaretransformed)
        message=self.test_record.message_ids[0]
        self.assertMailMail(self.partner_employee_2,'sent',
                            mail_message=message,
                            author=self.partner_employee, #author!=email_from(templatesetsonlyemail_from)
                            email_values={
                                'body_content':'TemplateBody%s'%self.test_record.name,
                                'email_from':self.test_record.user_id.email_formatted, #setbytemplate
                                'subject':'TemplateSubject%s'%self.test_record.name,
                                'attachments_info':[
                                    {'name':'00.txt','raw':b'Att00','type':'text/plain'},
                                    {'name':'01.txt','raw':b'Att01','type':'text/plain'},
                                    {'name':'TestReportfor%s.html'%self.test_record.name,'type':'text/plain'},
                                ]
                            },
                            fields_values={},
                           )
        self.assertMailMail(self.test_record.customer_id+new_partners,'sent',
                            mail_message=message,
                            author=self.partner_employee, #author!=email_from(templatesetsonlyemail_from)
                            email_values={
                                'body_content':'TemplateBody%s'%self.test_record.name,
                                'email_from':self.test_record.user_id.email_formatted, #setbytemplate
                                'subject':'TemplateSubject%s'%self.test_record.name,
                                'attachments_info':[
                                    {'name':'00.txt','raw':b'Att00','type':'text/plain'},
                                    {'name':'01.txt','raw':b'Att01','type':'text/plain'},
                                    {'name':'TestReportfor%s.html'%self.test_record.name,'type':'text/plain'},
                                ]
                            },
                            fields_values={},
                           )

        #messageispostedandnotifiedadmin
        self.assertEqual(message.subtype_id,self.env.ref('mail.mt_comment'))
        self.assertNotified(message,[{'partner':self.partner_admin,'is_read':False,'type':'inbox'}])
        #attachmentsarecopiedonmessageandlinkedtodocument
        self.assertEqual(
            set(message.attachment_ids.mapped('name')),
            set(['00.txt','01.txt','TestReportfor%s.html'%self.test_record.name])
        )
        self.assertEqual(set(message.attachment_ids.mapped('res_model')),set([self.test_record._name]))
        self.assertEqual(set(message.attachment_ids.mapped('res_id')),set(self.test_record.ids))
        self.assertTrue(all(attachnotinmessage.attachment_idsforattachinattachs),'Shouldhavecopiedattachments')

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_recipients_email_fields(self):
        """Testvariouscombinationsofcornercase/notstandardfillingof
        emailfields:multiemail,formattedemails,...ontemplate,usedto
        postamessageusingthecomposer."""
        existing_partners=self.env['res.partner'].search([])
        partner_format_tofind,partner_multi_tofind=self.env['res.partner'].create([
            {
                'email':'"FindMeFormat"<find.me.format@test.example.com>',
                'name':'FindMeFormat',
            },{
                'email':'find.me.multi.1@test.example.com,"FindMeMulti"<find.me.multi.2@test.example.com>',
                'name':'FindMeMulti',
            }
        ])
        email_ccs=['"Raoul"<test.cc.1@example.com>','"Raoulette"<test.cc.2@example.com>','test.cc.2.2@example.com>','invalid',' ']
        email_tos=['"Micheline,l\'Immense"<test.to.1@example.com>','test.to.2@example.com','wrong',' ']

        self.template.write({
            'email_cc':','.join(email_ccs),
            'email_from':'${user.email_formatted|safe}',
            'email_to':','.join(email_tos+(partner_format_tofind+partner_multi_tofind).mapped('email')),
            'partner_to':f'{self.partner_1.id},{self.partner_2.id},0,test',
        })
        self.user_employee.write({'email':'email.from.1@test.example.com,email.from.2@test.example.com'})
        self.partner_1.write({'email':'"ValidFormatted"<valid.lelitre@agrolait.com>'})
        self.partner_2.write({'email':'valid.other.1@agrolait.com,valid.other.cc@agrolait.com'})
        #ensurevaluesusedafterwardsfortesting
        self.assertEqual(
            self.partner_employee.email_formatted,
            '"ErnestEmployee"<email.from.1@test.example.com,email.from.2@test.example.com>',
            'Formatting:wrongformattingduetomulti-email')
        self.assertEqual(
            self.partner_1.email_formatted,
            '"ValidLelitre"<valid.lelitre@agrolait.com>',
            'Formatting:avoidwrongdoubleencapsulation')
        self.assertEqual(
            self.partner_2.email_formatted,
            '"ValidPoilvache"<valid.other.1@agrolait.com,valid.other.cc@agrolait.com>',
            'Formatting:wrongformattingduetomulti-email')

        #instantiatecomposer,postmessage
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(
                self.test_record,
                add_web=True,
                default_template_id=self.template.id,
            )
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=False),self.mock_mail_app():
            composer.send_mail()

        #findpartnerscreatedduringsending(asemailsaretransformedintopartners)
        #FIXME:currentlyemailfindingbasedonformatted/multiemailsdoes
        #notwork
        new_partners=self.env['res.partner'].search([]).search([('id','notin',existing_partners.ids)])
        self.assertEqual(len(new_partners),8,
                         'Mail(FIXME):multiplepartnercreationduetoformatted/multiemails:1extrapartners')
        self.assertIn(partner_format_tofind,new_partners)
        self.assertIn(partner_multi_tofind,new_partners)
        self.assertEqual(
            sorted(new_partners.mapped('email')),
            sorted(['"FindMeFormat"<find.me.format@test.example.com>',
                    'find.me.multi.1@test.example.com,"FindMeMulti"<find.me.multi.2@test.example.com>',
                    'find.me.multi.2@test.example.com',
                    'test.cc.1@example.com','test.cc.2@example.com','test.cc.2.2@example.com',
                    'test.to.1@example.com','test.to.2@example.com']),
            'Mail:createdpartnersforvalidemails(wrong/invalidnottakenintoaccount)+didnotfindcornercases(FIXME)'
        )
        self.assertEqual(
            sorted(new_partners.mapped('email_formatted')),
            sorted(['"FindMeFormat"<find.me.format@test.example.com>',
                    '"FindMeMulti"<find.me.multi.1@test.example.com,find.me.multi.2@test.example.com>',
                    '"find.me.multi.2@test.example.com"<find.me.multi.2@test.example.com>',
                    '"test.cc.1@example.com"<test.cc.1@example.com>',
                    '"test.cc.2@example.com"<test.cc.2@example.com>',
                    '"test.cc.2.2@example.com"<test.cc.2.2@example.com>',
                    '"test.to.1@example.com"<test.to.1@example.com>',
                    '"test.to.2@example.com"<test.to.2@example.com>']),
        )
        self.assertEqual(
            sorted(new_partners.mapped('name')),
            sorted(['FindMeFormat',
                    'FindMeMulti',
                    'find.me.multi.2@test.example.com',
                    'test.cc.1@example.com','test.to.1@example.com','test.to.2@example.com',
                    'test.cc.2@example.com','test.cc.2.2@example.com']),
            'Mail:currentlysettingname=email,nottakingintoaccountformattedemails'
        )

        #globaloutgoing:twomail.mail(allcustomerrecipients,thenallemployeerecipients)
        #and11emails,and1inboxnotification(admin)
        #FIXMEtemplateissentonlytopartners(email_toaretransformed)->
        #  wrong/weirdemails(seeemail_formattedofpartners)iskept
        #FIXME:morepartnerscreatedthanrealemails(seeabove)->dueto
        #  transformationfromemail->partnerintemplate'generate_recipients'
        #  therearemorepartnersthanemailtonotify;
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated2mail.mail')
        self.assertEqual(
            len(self._mails),len(new_partners)+3,
            f'Shouldhavesent{len(new_partners)+3}emails,one/recipient({len(new_partners)}mailedpartners+partner_1+partner_2+partner_employee)')
        self.assertMailMail(
            self.partner_employee_2,'sent',
            author=self.partner_employee,
            email_values={
                'body_content':f'TemplateBody{self.test_record.name}',
                #singleemaileventifemailfieldismulti-email
                'email_from':formataddr((self.user_employee.name,'email.from.1@test.example.com')),
                'subject':f'TemplateSubject{self.test_record.name}',
            },
            fields_values={
                #currentlyholdingmulti-email'email_from'
                'email_from':formataddr((self.user_employee.name,'email.from.1@test.example.com,email.from.2@test.example.com')),
            },
            mail_message=self.test_record.message_ids[0],
        )
        self.assertMailMail(
            self.partner_1+self.partner_2+new_partners,'sent',
            author=self.partner_employee,
            email_to_recipients=[
                [self.partner_1.email_formatted],
                [f'"{self.partner_2.name}"<valid.other.1@agrolait.com>',f'"{self.partner_2.name}"<valid.other.cc@agrolait.com>'],
            ]+[[new_partners[0]['email_formatted']],
                 ['"FindMeMulti"<find.me.multi.1@test.example.com>','"FindMeMulti"<find.me.multi.2@test.example.com>']
            ]+[[email]foremailinnew_partners[2:].mapped('email_formatted')],
            email_values={
                'body_content':f'TemplateBody{self.test_record.name}',
                #singleemaileventifemailfieldismulti-email
                'email_from':formataddr((self.user_employee.name,'email.from.1@test.example.com')),
                'subject':f'TemplateSubject{self.test_record.name}',
            },
            fields_values={
                #currentlyholdingmulti-email'email_from'
                'email_from':formataddr((self.user_employee.name,'email.from.1@test.example.com,email.from.2@test.example.com')),
            },
            mail_message=self.test_record.message_ids[0],
        )


@tagged('mail_composer')
classTestComposerResultsMass(TestMailComposer):

    @classmethod
    defsetUpClass(cls):
        super(TestComposerResultsMass,cls).setUpClass()
        #ensureemployeecancreatepartners,necessaryfortemplates
        cls.user_employee.write({
            'groups_id':[(4,cls.env.ref('base.group_partner_manager').id)],
        })

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl(self):
        self.template.auto_delete=False #keepsentemailstocheckcontent
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id)
        ))
        composer=composer_form.save()
        self.assertFalse(composer.no_auto_thread,'Mail:thread-enabledmodelsshoulduseautothreadbydefault')
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),2,'Shouldhavesent1emailperrecord')

        forrecordinself.test_records:
            #messagecopyiskept
            message=record.message_ids[0]

            #templateissentdirectlyusingcustomerfield,meaningwehaverecipients
            self.assertMailMail(record.customer_id,'sent',
                                mail_message=message,
                                author=self.partner_employee)

            #messagecontent
            self.assertEqual(message.subject,'TemplateSubject%s'%record.name)
            self.assertEqual(message.body,'<p>TemplateBody%s</p>'%record.name)
            self.assertEqual(message.author_id,self.user_employee.partner_id)
            #post-relatedfieldsarevoid
            self.assertEqual(message.subtype_id,self.env['mail.message.subtype'])
            self.assertEqual(message.partner_ids,self.env['res.partner'])

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_complete(self):
        """Testacomposerinmassmodewithaquitecompletetemplate,containing
        notablyemail-basedrecipientsandattachments."""
        attachment_data=self._generate_attachments_data(2)
        email_to_1='test.to.1@test.example.com'
        email_to_2='test.to.2@test.example.com'
        email_to_3='test.to.1@test.example.com' #duplicate:shouldnotsenttwicetheemail
        email_cc_1='test.cc.1@test.example.com'
        self.template.write({
            'auto_delete':False, #keepsentemailstocheckcontent
            'attachment_ids':[(0,0,a)forainattachment_data],
            'email_to':'%s,%s,%s'%(email_to_1,email_to_2,email_to_3),
            'email_cc':email_cc_1,
            'partner_to':'%s,${object.customer_id.idifobject.customer_idelse""}'%self.partner_admin.id,
            'report_name':'TestReportfor${object.name}', #testcursorforceshtml
            'report_template':self.test_report.id,
        })
        attachs=self.env['ir.attachment'].search([('name','in',[a['name']forainattachment_data])])
        self.assertEqual(len(attachs),2)

        #ensureinitialdata
        self.assertEqual(self.test_records.user_id,self.env['res.users'])
        self.assertEqual(self.test_records.message_partner_ids,self.env['res.partner'])

        #launchcomposerinmassmode
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id)
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            composer.send_mail()

        new_partners=self.env['res.partner'].search([
            ('email','in',[email_to_1,email_to_2,email_to_3,email_cc_1])
        ])
        self.assertEqual(len(new_partners),3)

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),10,'Shouldhavesent5emailsperrecord')

        forrecordinself.test_records:
            #templateissentonlytopartners(email_toaretransformed)
            self.assertMailMail(record.customer_id+new_partners+self.partner_admin,
                                'sent',
                                author=self.partner_employee,
                                email_values={
                                    'attachments_info':[
                                        {'name':'00.txt','raw':b'Att00','type':'text/plain'},
                                        {'name':'01.txt','raw':b'Att01','type':'text/plain'},
                                        {'name':'TestReportfor%s.html'%record.name,'type':'text/plain'},
                                    ],
                                    'body_content':'TemplateBody%s'%record.name,
                                    'email_from':self.partner_employee.email_formatted,
                                    'reply_to':formataddr((
                                        f'{self.env.user.company_id.name}{record.name}',
                                        f'{self.alias_catchall}@{self.alias_domain}'
                                    )),
                                    'subject':'TemplateSubject%s'%record.name,
                                },
                                fields_values={
                                    'email_from':self.partner_employee.email_formatted,
                                    'reply_to':formataddr((
                                        f'{self.env.user.company_id.name}{record.name}',
                                        f'{self.alias_catchall}@{self.alias_domain}'
                                    )),
                                },
                                mail_message=record.message_ids[0], #messagecopyiskept
                               )

        #testwithoutcatchallfillingreply-to
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id)
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=True):
            #removealiassothat_notify_get_reply_towillreturnthedefaultvalueinsteadofalias
            self.env['ir.config_parameter'].sudo().set_param("mail.catchall.domain",None)
            composer.send_mail()

        forrecordinself.test_records:
            #templateissentonlytopartners(email_toaretransformed)
            self.assertMailMail(record.customer_id+new_partners+self.partner_admin,
                                'sent',
                                mail_message=record.message_ids[0],
                                author=self.partner_employee,
                                email_values={
                                    'email_from':self.partner_employee.email_formatted,
                                    'reply_to':self.partner_employee.email_formatted,
                                },
                                fields_values={
                                    'email_from':self.partner_employee.email_formatted,
                                    'reply_to':self.partner_employee.email_formatted,
                                },
                               )

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_delete(self):
        self.template.auto_delete=True
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id)
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),2,'Shouldhavesent1emailperrecord')
        self.assertEqual(self._new_mails.exists(),self.env['mail.mail'],'Shouldhavedeletedmail.mailrecords')

        forrecordinself.test_records:
            #messagecopyiskept
            message=record.message_ids[0]

            #templateissentdirectlyusingcustomerfield
            self.assertSentEmail(self.partner_employee,record.customer_id)

            #messagecontent
            self.assertEqual(message.subject,'TemplateSubject%s'%record.name)
            self.assertEqual(message.body,'<p>TemplateBody%s</p>'%record.name)
            self.assertEqual(message.author_id,self.user_employee.partner_id)
            #post-relatedfieldsarevoid
            self.assertEqual(message.subtype_id,self.env['mail.message.subtype'])
            self.assertEqual(message.partner_ids,self.env['res.partner'])

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_delete_notif(self):
        self.template.auto_delete=True
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id,
                                  default_auto_delete_message=True)
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),2,'Shouldhavesent1emailperrecord')
        self.assertEqual(self._new_mails.exists(),self.env['mail.mail'],'Shouldhavedeletedmail.mailrecords')

        forrecordinself.test_records:
            #messagecopyisunlinked
            self.assertEqual(record.message_ids,self.env['mail.message'],'Shouldhavedeletedmail.messagerecords')

            #templateissentdirectlyusingcustomerfield
            self.assertSentEmail(self.partner_employee,record.customer_id)

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_no_auto_thread(self):
        """Testnoautothreadbehavior,notablywithreply-to."""
        #launchcomposerinmassmode
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id)
        ))
        composer_form.no_auto_thread=True
        composer_form.reply_to="${('\"'+object.name+'\"<%s>'%'dynamic.reply.to@test.com')|safe}"
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            composer.send_mail()

        forrecordinself.test_records:
            self.assertMailMail(record.customer_id,
                                'sent',
                                mail_message=record.message_ids[0],
                                author=self.partner_employee,
                                email_values={
                                    'body_content':'TemplateBody%s'%record.name,
                                    'email_from':self.partner_employee.email_formatted,
                                    'reply_to':formataddr((
                                        f'{record.name}',
                                        'dynamic.reply.to@test.com'
                                    )),
                                    'subject':'TemplateSubject%s'%record.name,
                                },
                                fields_values={
                                    'email_from':self.partner_employee.email_formatted,
                                    'reply_to':formataddr((
                                        f'{record.name}',
                                        'dynamic.reply.to@test.com'
                                    )),
                                },
                               )

    @users('employee')
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_recipients(self):
        """Testvariouscombinationsofrecipients:active_domain,active_id,
        active_ids,...toensurefallbackbehaviorareworking."""
        #1:active_domain
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id,
                                  active_ids=[],
                                  default_use_active_domain=True,
                                  default_active_domain=[('id','in',self.test_records.ids)])
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),2,'Shouldhavesent1emailperrecord')

        forrecordinself.test_records:
            #templateissentdirectlyusingcustomerfield
            self.assertSentEmail(self.partner_employee,record.customer_id)

        #2:active_domainnottakenintoaccountifuse_active_domainisFalse
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id,
                                  default_use_active_domain=False,
                                  default_active_domain=[('id','in',-1)])
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=True):
            composer.send_mail()

        #globaloutgoing
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),2,'Shouldhavesent1emailperrecord')

        #3:fallbackonactive_idifnotactive_ids
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(self.test_records,add_web=True,
                                  default_template_id=self.template.id,
                                  active_ids=[])
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            composer.send_mail()

        #globaloutgoing
        self.assertEqual(len(self._new_mails),1,'Shouldhavecreated1mail.mailperrecord')
        self.assertEqual(len(self._mails),1,'Shouldhavesent1emailperrecord')

        #3:voidisvoid
        composer_form=Form(self.env['mail.compose.message'].with_context(
            default_model='mail.test.ticket',
            default_template_id=self.template.id
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=False),self.assertRaises(ValueError):
            composer.send_mail()

    @users('employee')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_wtpl_recipients_email_fields(self):
        """Testvariouscombinationsofcornercase/notstandardfillingof
        emailfields:multiemail,formattedemails,..."""
        existing_partners=self.env['res.partner'].search([])
        partner_format_tofind,partner_multi_tofind=self.env['res.partner'].create([
            {
                'email':'"FindMeFormat"<find.me.format@test.example.com>',
                'name':'FindMeFormat',
            },{
                'email':'find.me.multi.1@test.example.com,"FindMeMulti"<find.me.multi.2@test.example.com>',
                'name':'FindMeMulti',
            }
        ])
        email_ccs=['"Raoul"<test.cc.1@example.com>','"Raoulette"<test.cc.2@example.com>','test.cc.2.2@example.com>','invalid',' ']
        email_tos=['"Micheline,l\'Immense"<test.to.1@example.com>','test.to.2@example.com','wrong',' ']

        self.template.write({
            'email_cc':','.join(email_ccs),
            'email_from':'${user.email_formatted|safe}',
            'email_to':','.join(email_tos+(partner_format_tofind+partner_multi_tofind).mapped('email')),
            'partner_to':f'{self.partner_1.id},{self.partner_2.id},0,test',
        })
        self.user_employee.write({'email':'email.from.1@test.example.com,email.from.2@test.example.com'})
        self.partner_1.write({'email':'"ValidFormatted"<valid.lelitre@agrolait.com>'})
        self.partner_2.write({'email':'valid.other.1@agrolait.com,valid.other.cc@agrolait.com'})
        #ensurevaluesusedafterwardsfortesting
        self.assertEqual(
            self.partner_employee.email_formatted,
            '"ErnestEmployee"<email.from.1@test.example.com,email.from.2@test.example.com>',
            'Formatting:wrongformattingduetomulti-email')
        self.assertEqual(
            self.partner_1.email_formatted,
            '"ValidLelitre"<valid.lelitre@agrolait.com>',
            'Formatting:avoidwrongdoubleencapsulation')
        self.assertEqual(
            self.partner_2.email_formatted,
            '"ValidPoilvache"<valid.other.1@agrolait.com,valid.other.cc@agrolait.com>',
            'Formatting:wrongformattingduetomulti-email')

        #instantiatecomposer,sendmailing
        composer_form=Form(self.env['mail.compose.message'].with_context(
            self._get_web_context(
                self.test_records,
                add_web=True,
                default_template_id=self.template.id,
            )
        ))
        composer=composer_form.save()
        withself.mock_mail_gateway(mail_unlink_sent=False),self.mock_mail_app():
            composer.send_mail()

        #findpartnerscreatedduringsending(asemailsaretransformedintopartners)
        #FIXME:currentlyemailfindingbasedonformatted/multiemailsdoes
        #notwork
        new_partners=self.env['res.partner'].search([]).search([('id','notin',existing_partners.ids)])
        self.assertEqual(len(new_partners),8,
                         'Mail(FIXME):didnotfindexistingpartnersforformatted/multiemails:1extrapartners')
        self.assertIn(partner_format_tofind,new_partners)
        self.assertIn(partner_multi_tofind,new_partners)
        self.assertEqual(
            sorted(new_partners.mapped('email')),
            sorted(['"FindMeFormat"<find.me.format@test.example.com>',
                    'find.me.multi.1@test.example.com,"FindMeMulti"<find.me.multi.2@test.example.com>',
                    'find.me.multi.2@test.example.com',
                    'test.cc.1@example.com','test.cc.2@example.com','test.cc.2.2@example.com',
                    'test.to.1@example.com','test.to.2@example.com']),
            'Mail:createdpartnersforvalidemails(wrong/invalidnottakenintoaccount)+didnotfindcornercases(FIXME)'
        )
        self.assertEqual(
            sorted(new_partners.mapped('email_formatted')),
            sorted(['"FindMeFormat"<find.me.format@test.example.com>',
                    '"FindMeMulti"<find.me.multi.1@test.example.com,find.me.multi.2@test.example.com>',
                    '"find.me.multi.2@test.example.com"<find.me.multi.2@test.example.com>',
                    '"test.cc.1@example.com"<test.cc.1@example.com>',
                    '"test.cc.2@example.com"<test.cc.2@example.com>',
                    '"test.cc.2.2@example.com"<test.cc.2.2@example.com>',
                    '"test.to.1@example.com"<test.to.1@example.com>',
                    '"test.to.2@example.com"<test.to.2@example.com>']),
        )
        self.assertEqual(
            sorted(new_partners.mapped('name')),
            sorted(['FindMeFormat',
                    'FindMeMulti',
                    'find.me.multi.2@test.example.com',
                    'test.cc.1@example.com','test.to.1@example.com','test.to.2@example.com',
                    'test.cc.2@example.com','test.cc.2.2@example.com']),
            'Mail:currentlysettingname=email,nottakingintoaccountformattedemails'
        )

        #globaloutgoing:onemail.mail(allcustomerrecipients),*2records
        #  Notethatemployeeisnotmailedherecomparedto'comment'modeashe
        #  isnotinthetemplaterecipients,onlyafollower
        #FIXMEtemplateissentonlytopartners(email_toaretransformed)->
        #  wrong/weirdemails(seeemail_formattedofpartners)iskept
        #FIXME:morepartnerscreatedthanrealemails(seeabove)->dueto
        #  transformationfromemail->partnerintemplate'generate_recipients'
        #  therearemorepartnersthanemailtonotify;
        self.assertEqual(len(self._new_mails),2,'Shouldhavecreated2mail.mail')
        self.assertEqual(
            len(self._mails),(len(new_partners)+2)*2,
            f'Shouldhavesent{(len(new_partners)+2)*2}emails,one/recipient({len(new_partners)}mailedpartners+partner_1+partner_2)*2records')
        forrecordinself.test_records:
            self.assertMailMail(
                self.partner_1+self.partner_2+new_partners,
                'sent',
                author=self.partner_employee,
                email_to_recipients=[
                    [self.partner_1.email_formatted],
                    [f'"{self.partner_2.name}"<valid.other.1@agrolait.com>',f'"{self.partner_2.name}"<valid.other.cc@agrolait.com>'],
                ]+[[new_partners[0]['email_formatted']],
                     ['"FindMeMulti"<find.me.multi.1@test.example.com>','"FindMeMulti"<find.me.multi.2@test.example.com>']
                ]+[[email]foremailinnew_partners[2:].mapped('email_formatted')],
                email_values={
                    'body_content':f'TemplateBody{record.name}',
                    #singleemaileventifemailfieldismulti-email
                    'email_from':formataddr((self.user_employee.name,'email.from.1@test.example.com')),
                    'reply_to':formataddr((
                        f'{self.env.user.company_id.name}{record.name}',
                        f'{self.alias_catchall}@{self.alias_domain}'
                    )),
                    'subject':f'TemplateSubject{record.name}',
                },
                fields_values={
                    #currentlyholdingmulti-email'email_from'
                    'email_from':self.partner_employee.email_formatted,
                    'reply_to':formataddr((
                        f'{self.env.user.company_id.name}{record.name}',
                        f'{self.alias_catchall}@{self.alias_domain}'
                    )),
                },
                mail_message=record.message_ids[0], #messagecopyiskept
            )
