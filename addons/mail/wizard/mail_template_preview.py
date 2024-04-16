#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.exceptionsimportUserError


classMailTemplatePreview(models.TransientModel):
    _name='mail.template.preview'
    _description='EmailTemplatePreview'
    _MAIL_TEMPLATE_FIELDS=['subject','body_html','email_from','email_to',
                             'email_cc','reply_to','scheduled_date','attachment_ids']

    @api.model
    def_selection_target_model(self):
        return[(model.model,model.name)formodelinself.env['ir.model'].search([])]

    @api.model
    def_selection_languages(self):
        returnself.env['res.lang'].get_installed()

    @api.model
    defdefault_get(self,fields):
        result=super(MailTemplatePreview,self).default_get(fields)
        ifnotresult.get('mail_template_id')or'resource_ref'notinfields:
            returnresult
        mail_template=self.env['mail.template'].browse(result['mail_template_id'])
        res=self.env[mail_template.model_id.model].search([],limit=1)
        ifres:
            result['resource_ref']='%s,%s'%(mail_template.model_id.model,res.id)
        returnresult

    mail_template_id=fields.Many2one('mail.template',string='RelatedMailTemplate',required=True)
    model_id=fields.Many2one('ir.model',string='Targetedmodel',related="mail_template_id.model_id")
    resource_ref=fields.Reference(string='Record',selection='_selection_target_model')
    lang=fields.Selection(_selection_languages,string='TemplatePreviewLanguage')
    no_record=fields.Boolean('NoRecord',compute='_compute_no_record')
    error_msg=fields.Char('ErrorMessage',readonly=True)
    #Fieldssamethanthemail.templatemodel,computedwithresource_refandlang
    subject=fields.Char('Subject',compute='_compute_mail_template_fields')
    email_from=fields.Char('From',compute='_compute_mail_template_fields',help="Senderaddress")
    email_to=fields.Char('To',compute='_compute_mail_template_fields',
                           help="Comma-separatedrecipientaddresses")
    email_cc=fields.Char('Cc',compute='_compute_mail_template_fields',help="Carboncopyrecipients")
    reply_to=fields.Char('Reply-To',compute='_compute_mail_template_fields',help="Preferredresponseaddress")
    scheduled_date=fields.Char('ScheduledDate',compute='_compute_mail_template_fields',
                                 help="Thequeuemanagerwillsendtheemailafterthedate")
    body_html=fields.Html('Body',compute='_compute_mail_template_fields',sanitize=False)
    attachment_ids=fields.Many2many('ir.attachment','Attachments',compute='_compute_mail_template_fields')
    #Extrafieldsinfogeneratedbygenerate_email
    partner_ids=fields.Many2many('res.partner',string='Recipients',compute='_compute_mail_template_fields')

    @api.depends('model_id')
    def_compute_no_record(self):
        forpreviewinself:
            preview.no_record=(self.env[preview.model_id.model].search_count([])==0)ifpreview.model_idelseTrue

    @api.depends('lang','resource_ref')
    def_compute_mail_template_fields(self):
        """Previewthemailtemplate(body,subject,...)dependingofthelanguageand
        therecordreference,morepreciselytherecordidforthedefinedmodelofthemailtemplate.
        Ifnorecordidisselectable/set,thejinjaplaceholderswon'tbereplaceinthedisplayinformation."""
        copy_depends_values={'lang':self.lang}
        mail_template=self.mail_template_id.with_context(lang=self.lang)
        try:
            ifnotself.resource_ref:
                self._set_mail_attributes()
            else:
                copy_depends_values['resource_ref']='%s,%s'%(self.resource_ref._name,self.resource_ref.id)
                mail_values=mail_template.with_context(template_preview_lang=self.lang).generate_email(
                    self.resource_ref.id,self._MAIL_TEMPLATE_FIELDS+['partner_to'])
                self._set_mail_attributes(values=mail_values)
            self.error_msg=False
        exceptUserErrorasuser_error:
            self._set_mail_attributes()
            self.error_msg=user_error.args[0]
        finally:
            #Avoidtobechangebyainvalidate_cachecall(ingenerate_mail),e.g.Quotation/Orderreport
            forkey,valueincopy_depends_values.items():
                self[key]=value

    def_set_mail_attributes(self,values=None):
        forfieldinself._MAIL_TEMPLATE_FIELDS:
            field_value=values.get(field,False)ifvalueselseself.mail_template_id[field]
            self[field]=field_value
        self.partner_ids=values.get('partner_ids',False)ifvalueselseFalse
