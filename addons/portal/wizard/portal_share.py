#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models,_


classPortalShare(models.TransientModel):
    _name='portal.share'
    _description='PortalSharing'

    @api.model
    defdefault_get(self,fields):
        result=super(PortalShare,self).default_get(fields)
        result['res_model']=self._context.get('active_model',False)
        result['res_id']=self._context.get('active_id',False)
        ifresult['res_model']andresult['res_id']:
            record=self.env[result['res_model']].browse(result['res_id'])
            result['share_link']=record.get_base_url()+record._get_share_url(redirect=True)
        returnresult

    res_model=fields.Char('RelatedDocumentModel',required=True)
    res_id=fields.Integer('RelatedDocumentID',required=True)
    partner_ids=fields.Many2many('res.partner',string="Recipients",required=True)
    note=fields.Text(help="Addextracontenttodisplayintheemail")
    share_link=fields.Char(string="Link",compute='_compute_share_link')
    access_warning=fields.Text("Accesswarning",compute="_compute_access_warning")

    @api.depends('res_model','res_id')
    def_compute_share_link(self):
        forrecinself:
            rec.share_link=False
            ifrec.res_model:
                res_model=self.env[rec.res_model]
                ifisinstance(res_model,self.pool['portal.mixin'])andrec.res_id:
                    record=res_model.browse(rec.res_id)
                    rec.share_link=record.get_base_url()+record._get_share_url(redirect=True)

    @api.depends('res_model','res_id')
    def_compute_access_warning(self):
        forrecinself:
            rec.access_warning=False
            ifrec.res_model:
                res_model=self.env[rec.res_model]
                ifisinstance(res_model,self.pool['portal.mixin'])andrec.res_id:
                    record=res_model.browse(rec.res_id)
                    rec.access_warning=record.access_warning

    defaction_send_mail(self):
        active_record=self.env[self.res_model].browse(self.res_id)
        note=self.env.ref('mail.mt_note')
        signup_enabled=self.env['ir.config_parameter'].sudo().get_param('auth_signup.invitation_scope')=='b2c'

        ifhasattr(active_record,'access_token')andactive_record.access_tokenornotsignup_enabled:
            partner_ids=self.partner_ids
        else:
            partner_ids=self.partner_ids.filtered(lambdax:x.user_ids)
        #ifpartneralreadyuserorrecordhasaccesstokensendcommonlinkinbatchtoalluser
        forpartnerinself.partner_ids:
            share_link=active_record.get_base_url()+active_record._get_share_url(redirect=True,pid=partner.id)
            saved_lang=self.env.lang
            self=self.with_context(lang=partner.lang)
            template=self.env.ref('portal.portal_share_template',False)
            active_record.with_context(mail_post_autofollow=True).message_post_with_view(template,
                values={'partner':partner,'note':self.note,'record':active_record,
                        'share_link':share_link},
                subject=_("Youareinvitedtoaccess%s",active_record.display_name),
                subtype_id=note.id,
                email_layout_xmlid='mail.mail_notification_light',
                partner_ids=[(6,0,partner.ids)])
            self=self.with_context(lang=saved_lang)
        #whenpartnernotusersendindividualmailwithsignuptoken
        forpartnerinself.partner_ids-partner_ids:
            # preparepartnerforsignupandsendsingupurlwithredirecturl
            partner.signup_get_auth_param()
            share_link=partner._get_signup_url_for_action(action='/mail/view',res_id=self.res_id,model=self.model)[partner.id]
            saved_lang=self.env.lang
            self=self.with_context(lang=partner.lang)
            template=self.env.ref('portal.portal_share_template',False)
            active_record.with_context(mail_post_autofollow=True).message_post_with_view(template,
                values={'partner':partner,'note':self.note,'record':active_record,
                        'share_link':share_link},
                subject=_("Youareinvitedtoaccess%s",active_record.display_name),
                subtype_id=note.id,
                email_layout_xmlid='mail.mail_notification_light',
                partner_ids=[(6,0,partner.ids)])
            self=self.with_context(lang=saved_lang)
        return{'type':'ir.actions.act_window_close'}
