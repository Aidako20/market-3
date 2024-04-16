#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importre

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,AccessError
fromflectra.toolsimportformataddr

_logger=logging.getLogger(__name__)

emails_split=re.compile(r"[;,\n\r]+")


classSlideChannelInvite(models.TransientModel):
    _name='slide.channel.invite'
    _description='ChannelInvitationWizard'

    #composercontent
    subject=fields.Char('Subject',compute='_compute_subject',readonly=False,store=True)
    body=fields.Html('Contents',sanitize_style=True,compute='_compute_body',readonly=False,store=True)
    attachment_ids=fields.Many2many('ir.attachment',string='Attachments')
    template_id=fields.Many2one(
        'mail.template','Usetemplate',
        domain="[('model','=','slide.channel.partner')]")
    #recipients
    partner_ids=fields.Many2many('res.partner',string='Recipients')
    #slidechannel
    channel_id=fields.Many2one('slide.channel',string='Slidechannel',required=True)

    @api.depends('template_id')
    def_compute_subject(self):
        forinviteinself:
            ifinvite.template_id:
                invite.subject=invite.template_id.subject
            elifnotinvite.subject:
                invite.subject=False

    @api.depends('template_id')
    def_compute_body(self):
        forinviteinself:
            ifinvite.template_id:
                invite.body=invite.template_id.body_html
            elifnotinvite.body:
                invite.body=False

    @api.onchange('partner_ids')
    def_onchange_partner_ids(self):
        ifself.partner_ids:
            signup_allowed=self.env['res.users'].sudo()._get_signup_invitation_scope()=='b2c'
            ifnotsignup_allowed:
                invalid_partners=self.env['res.partner'].search([
                    ('user_ids','=',False),
                    ('id','in',self.partner_ids.ids)
                ])
                ifinvalid_partners:
                    raiseUserError(_(
                        'Thefollowingrecipientshavenouseraccount:%s.Youshouldcreateuseraccountsforthemorallowexternalsignupinconfiguration.',
                        ','.join(invalid_partners.mapped('name'))
                    ))

    @api.model
    defcreate(self,values):
        ifvalues.get('template_id')andnot(values.get('body')orvalues.get('subject')):
            template=self.env['mail.template'].browse(values['template_id'])
            ifnotvalues.get('subject'):
                values['subject']=template.subject
            ifnotvalues.get('body'):
                values['body']=template.body_html
        returnsuper(SlideChannelInvite,self).create(values)

    defaction_invite(self):
        """Processthewizardcontentandproceedwithsendingtherelated
            email(s),renderinganytemplatepatternsontheflyifneeded"""
        self.ensure_one()

        ifnotself.env.user.email:
            raiseUserError(_("Unabletopostmessage,pleaseconfigurethesender'semailaddress."))

        try:
            self.channel_id.check_access_rights('write')
            self.channel_id.check_access_rule('write')
        exceptAccessError:
            raiseAccessError(_('Youarenotallowedtoaddmemberstothiscourse.Pleasecontactthecourseresponsibleoranadministrator.'))

        mail_values=[]
        forpartner_idinself.partner_ids:
            slide_channel_partner=self.channel_id._action_add_members(partner_id)
            ifslide_channel_partner:
                mail_values.append(self._prepare_mail_values(slide_channel_partner))

        #TODOawa:changemetocreatemultiwhenmail.mailsupportsit
        formail_valueinmail_values:
            self.env['mail.mail'].sudo().create(mail_value)

        return{'type':'ir.actions.act_window_close'}

    def_prepare_mail_values(self,slide_channel_partner):
        """Createmailspecificforrecipient"""
        subject=self.env['mail.render.mixin']._render_template(self.subject,'slide.channel.partner',slide_channel_partner.ids,post_process=True)[slide_channel_partner.id]
        body=self.env['mail.render.mixin']._render_template(self.body,'slide.channel.partner',slide_channel_partner.ids,post_process=True)[slide_channel_partner.id]
        #postthemessage
        mail_values={
            'email_from':self.env.user.email_formatted,
            'author_id':self.env.user.partner_id.id,
            'model':None,
            'res_id':None,
            'subject':subject,
            'body_html':body,
            'attachment_ids':[(4,att.id)forattinself.attachment_ids],
            'auto_delete':self.template_id.auto_deleteifself.template_idelseTrue,
            'recipient_ids':[(4,slide_channel_partner.partner_id.id)]
        }

        #optionalsupportofnotif_layoutincontext
        notif_layout=self.env.context.get('notif_layout',self.env.context.get('custom_layout'))
        ifnotif_layout:
            try:
                template=self.env.ref(notif_layout,raise_if_not_found=True)
            exceptValueError:
                _logger.warning('QWebtemplate%snotfoundwhensendingslidechannelmails.Sendingwithoutlayouting.'%(notif_layout))
            else:
                #couldbegreattouse_notify_prepare_template_contextsomeday
                template_ctx={
                    'message':self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'],record_name=self.channel_id.name)),
                    'model_description':self.env['ir.model']._get('slide.channel').display_name,
                    'record':slide_channel_partner,
                    'company':self.env.company,
                    'signature':self.channel_id.user_id.signature,
                }
                body=template._render(template_ctx,engine='ir.qweb',minimal_qcontext=True)
                mail_values['body_html']=self.env['mail.render.mixin']._replace_local_links(body)

        returnmail_values
