#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importre
importwerkzeug

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)

emails_split=re.compile(r"[;,\n\r]+")


classSurveyInvite(models.TransientModel):
    _name='survey.invite'
    _description='SurveyInvitationWizard'

    @api.model
    def_get_default_from(self):
        ifself.env.user.email:
            returnself.env.user.email_formatted
        raiseUserError(_("Unabletopostmessage,pleaseconfigurethesender'semailaddress."))

    @api.model
    def_get_default_author(self):
        returnself.env.user.partner_id

    #composercontent
    subject=fields.Char('Subject',compute='_compute_subject',readonly=False,store=True)
    body=fields.Html('Contents',sanitize_style=True,compute='_compute_body',readonly=False,store=True)
    attachment_ids=fields.Many2many(
        'ir.attachment','survey_mail_compose_message_ir_attachments_rel','wizard_id','attachment_id',
        string='Attachments')
    template_id=fields.Many2one(
        'mail.template','Usetemplate',index=True,
        domain="[('model','=','survey.user_input')]")
    #origin
    email_from=fields.Char('From',default=_get_default_from,help="Emailaddressofthesender.")
    author_id=fields.Many2one(
        'res.partner','Author',index=True,
        ondelete='setnull',default=_get_default_author,
        help="Authorofthemessage.")
    #recipients
    partner_ids=fields.Many2many(
        'res.partner','survey_invite_partner_ids','invite_id','partner_id',string='Recipients',
        domain="""[
            '|',(survey_users_can_signup,'=',1),
            '|',(notsurvey_users_login_required,'=',1),
                 ('user_ids','!=',False),
        ]"""
    )
    existing_partner_ids=fields.Many2many(
        'res.partner',compute='_compute_existing_partner_ids',readonly=True,store=False)
    emails=fields.Text(string='Additionalemails',help="Thislistofemailsofrecipientswillnotbeconvertedincontacts.\
        Emailsmustbeseparatedbycommas,semicolonsornewline.")
    existing_emails=fields.Text(
        'Existingemails',compute='_compute_existing_emails',
        readonly=True,store=False)
    existing_mode=fields.Selection([
        ('new','Newinvite'),('resend','Resendinvite')],
        string='Handleexisting',default='resend',required=True)
    existing_text=fields.Text('ResendComment',compute='_compute_existing_text',readonly=True,store=False)
    #technicalinfo
    mail_server_id=fields.Many2one('ir.mail_server','Outgoingmailserver')
    #survey
    survey_id=fields.Many2one('survey.survey',string='Survey',required=True)
    survey_start_url=fields.Char('SurveyURL',compute='_compute_survey_start_url')
    survey_access_mode=fields.Selection(related="survey_id.access_mode",readonly=True)
    survey_users_login_required=fields.Boolean(related="survey_id.users_login_required",readonly=True)
    survey_users_can_signup=fields.Boolean(related='survey_id.users_can_signup')
    deadline=fields.Datetime(string="Answerdeadline")

    @api.depends('partner_ids','survey_id')
    def_compute_existing_partner_ids(self):
        self.existing_partner_ids=list(set(self.survey_id.user_input_ids.partner_id.ids)&set(self.partner_ids.ids))

    @api.depends('emails','survey_id')
    def_compute_existing_emails(self):
        emails=list(set(emails_split.split(self.emailsor"")))
        existing_emails=self.survey_id.mapped('user_input_ids.email')
        self.existing_emails='\n'.join(emailforemailinemailsifemailinexisting_emails)

    @api.depends('existing_partner_ids','existing_emails')
    def_compute_existing_text(self):
        existing_text=False
        ifself.existing_partner_ids:
            existing_text='%s:%s.'%(
                _('Thefollowingcustomershavealreadyreceivedaninvite'),
                ','.join(self.mapped('existing_partner_ids.name'))
            )
        ifself.existing_emails:
            existing_text='%s\n'%existing_textifexisting_textelse''
            existing_text+='%s:%s.'%(
                _('Thefollowingemailshavealreadyreceivedaninvite'),
                self.existing_emails
            )

        self.existing_text=existing_text

    @api.depends('survey_id.access_token')
    def_compute_survey_start_url(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        forinviteinself:
            invite.survey_start_url=werkzeug.urls.url_join(base_url,invite.survey_id.get_start_url())ifinvite.survey_idelseFalse

    @api.onchange('emails')
    def_onchange_emails(self):
        ifself.emailsand(self.survey_users_login_requiredandnotself.survey_id.users_can_signup):
            raiseUserError(_('Thissurveydoesnotallowexternalpeopletoparticipate.Youshouldcreateuseraccountsorupdatesurveyaccessmodeaccordingly.'))
        ifnotself.emails:
            return
        valid,error=[],[]
        emails=list(set(emails_split.split(self.emailsor"")))
        foremailinemails:
            email_check=tools.email_split_and_format(email)
            ifnotemail_check:
                error.append(email)
            else:
                valid.extend(email_check)
        iferror:
            raiseUserError(_("Someemailsyoujustenteredareincorrect:%s")%(','.join(error)))
        self.emails='\n'.join(valid)

    @api.onchange('partner_ids')
    def_onchange_partner_ids(self):
        ifself.survey_users_login_requiredandself.partner_ids:
            ifnotself.survey_id.users_can_signup:
                invalid_partners=self.env['res.partner'].search([
                    ('user_ids','=',False),
                    ('id','in',self.partner_ids.ids)
                ])
                ifinvalid_partners:
                    raiseUserError(_(
                        'Thefollowingrecipientshavenouseraccount:%s.Youshouldcreateuseraccountsforthemorallowexternalsignupinconfiguration.',
                        ','.join(invalid_partners.mapped('name'))
                    ))

    @api.depends('template_id','partner_ids')
    def_compute_subject(self):
        forinviteinself:
            langs=set(invite.partner_ids.mapped('lang'))-{False}
            iflen(langs)==1:
                invite=invite.with_context(lang=langs.pop())
            ifinvite.template_id:
                invite.subject=invite.template_id.subject
            elifnotinvite.subject:
                invite.subject=False

    @api.depends('template_id','partner_ids')
    def_compute_body(self):
        forinviteinself:
            langs=set(invite.partner_ids.mapped('lang'))-{False}
            iflen(langs)==1:
                invite=invite.with_context(lang=langs.pop())
            ifinvite.template_id:
                invite.body=invite.template_id.body_html
            elifnotinvite.body:
                invite.body=False

    @api.model
    defcreate(self,values):
        ifvalues.get('template_id')andnot(values.get('body')orvalues.get('subject')):
            template=self.env['mail.template'].browse(values['template_id'])
            ifnotvalues.get('subject'):
                values['subject']=template.subject
            ifnotvalues.get('body'):
                values['body']=template.body_html
        returnsuper(SurveyInvite,self).create(values)

    #------------------------------------------------------
    #Wizardvalidationandsend
    #------------------------------------------------------

    def_prepare_answers(self,partners,emails):
        answers=self.env['survey.user_input']
        existing_answers=self.env['survey.user_input'].search([
            '&',('survey_id','=',self.survey_id.id),
            '|',
            ('partner_id','in',partners.ids),
            ('email','in',emails)
        ])
        partners_done=self.env['res.partner']
        emails_done=[]
        ifexisting_answers:
            ifself.existing_mode=='resend':
                partners_done=existing_answers.mapped('partner_id')
                emails_done=existing_answers.mapped('email')

                #onlyaddthelastanswerforeachuserofeachtype(partner_id&email)
                #tohaveonlyonemailsentperuser
                forpartner_doneinpartners_done:
                    answers|=next(existing_answerforexisting_answerin
                        existing_answers.sorted(lambdaanswer:answer.create_date,reverse=True)
                        ifexisting_answer.partner_id==partner_done)

                foremail_doneinemails_done:
                    answers|=next(existing_answerforexisting_answerin
                        existing_answers.sorted(lambdaanswer:answer.create_date,reverse=True)
                        ifexisting_answer.email==email_done)

        fornew_partnerinpartners-partners_done:
            answers|=self.survey_id._create_answer(partner=new_partner,check_attempts=False,**self._get_answers_values())
        fornew_emailin[emailforemailinemailsifemailnotinemails_done]:
            answers|=self.survey_id._create_answer(email=new_email,check_attempts=False,**self._get_answers_values())

        returnanswers

    def_get_answers_values(self):
        return{
            'deadline':self.deadline,
        }

    def_send_mail(self,answer):
        """Createmailspecificforrecipientcontainingnotablyitsaccesstoken"""
        subject=self.env['mail.render.mixin'].with_context(safe=True)._render_template(self.subject,'survey.user_input',answer.ids,post_process=True)[answer.id]
        body=self.env['mail.render.mixin']._render_template(self.body,'survey.user_input',answer.ids,post_process=True)[answer.id]
        #postthemessage
        mail_values={
            'email_from':self.email_from,
            'author_id':self.author_id.id,
            'model':None,
            'res_id':None,
            'subject':subject,
            'body_html':body,
            'attachment_ids':[(4,att.id)forattinself.attachment_ids],
            'auto_delete':True,
        }
        ifanswer.partner_id:
            mail_values['recipient_ids']=[(4,answer.partner_id.id)]
        else:
            mail_values['email_to']=answer.email

        #optionalsupportofnotif_layoutincontext
        notif_layout=self.env.context.get('notif_layout',self.env.context.get('custom_layout'))
        ifnotif_layout:
            try:
                template=self.env.ref(notif_layout,raise_if_not_found=True)
            exceptValueError:
                _logger.warning('QWebtemplate%snotfoundwhensendingsurveymails.Sendingwithoutlayouting.'%(notif_layout))
            else:
                template_ctx={
                    'message':self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'],record_name=self.survey_id.title)),
                    'model_description':self.env['ir.model']._get('survey.survey').display_name,
                    'company':self.env.company,
                }
                body=template._render(template_ctx,engine='ir.qweb',minimal_qcontext=True)
                mail_values['body_html']=self.env['mail.render.mixin']._replace_local_links(body)

        returnself.env['mail.mail'].sudo().create(mail_values)

    defaction_invite(self):
        """Processthewizardcontentandproceedwithsendingtherelated
            email(s),renderinganytemplatepatternsontheflyifneeded"""
        self.ensure_one()
        Partner=self.env['res.partner']

        #computepartnersandemails,trytofindpartnersforgivenemails
        valid_partners=self.partner_ids
        langs=set(valid_partners.mapped('lang'))-{False}
        iflen(langs)==1:
            self=self.with_context(lang=langs.pop())
        valid_emails=[]
        foremailinemails_split.split(self.emailsor''):
            partner=False
            email_normalized=tools.email_normalize(email)
            ifemail_normalized:
                limit=Noneifself.survey_users_login_requiredelse1
                partner=Partner.search([('email_normalized','=',email_normalized)],limit=limit)
            ifpartner:
                valid_partners|=partner
            else:
                email_formatted=tools.email_split_and_format(email)
                ifemail_formatted:
                    valid_emails.extend(email_formatted)

        ifnotvalid_partnersandnotvalid_emails:
            raiseUserError(_("Pleaseenteratleastonevalidrecipient."))

        answers=self._prepare_answers(valid_partners,valid_emails)
        foranswerinanswers:
            self._send_mail(answer)

        return{'type':'ir.actions.act_window_close'}
