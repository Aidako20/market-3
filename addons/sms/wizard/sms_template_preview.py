#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSMSTemplatePreview(models.TransientModel):
    _name="sms.template.preview"
    _description="SMSTemplatePreview"

    @api.model
    def_selection_target_model(self):
        models=self.env['ir.model'].search([])
        return[(model.model,model.name)formodelinmodels]

    @api.model
    def_selection_languages(self):
        returnself.env['res.lang'].get_installed()

    @api.model
    defdefault_get(self,fields):
        result=super(SMSTemplatePreview,self).default_get(fields)
        sms_template_id=self.env.context.get('default_sms_template_id')
        ifnotsms_template_idor'resource_ref'notinfields:
            returnresult
        sms_template=self.env['sms.template'].browse(sms_template_id)
        res=self.env[sms_template.model_id.model].search([],limit=1)
        ifres:
            result['resource_ref']='%s,%s'%(sms_template.model_id.model,res.id)
        returnresult

    sms_template_id=fields.Many2one('sms.template',required=True,ondelete='cascade')
    lang=fields.Selection(_selection_languages,string='TemplatePreviewLanguage')
    model_id=fields.Many2one('ir.model',related="sms_template_id.model_id")
    body=fields.Char('Body',compute='_compute_sms_template_fields')
    resource_ref=fields.Reference(string='Recordreference',selection='_selection_target_model')
    no_record=fields.Boolean('NoRecord',compute='_compute_no_record')

    @api.depends('model_id')
    def_compute_no_record(self):
        forpreviewinself:
            preview.no_record=(self.env[preview.model_id.model].search_count([])==0)ifpreview.model_idelseTrue

    @api.depends('lang','resource_ref')
    def_compute_sms_template_fields(self):
        forwizardinself:
            ifwizard.sms_template_idandwizard.resource_ref:
                wizard.body=wizard.sms_template_id._render_field('body',[wizard.resource_ref.id],set_lang=wizard.lang)[wizard.resource_ref.id]
            else:
                wizard.body=wizard.sms_template_id.body
