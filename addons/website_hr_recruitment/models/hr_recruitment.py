#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeugimporturls

fromflectraimport_,api,fields,models
fromflectra.tools.translateimporthtml_translate
fromflectra.exceptionsimportUserError


classRecruitmentSource(models.Model):
    _inherit='hr.recruitment.source'

    url=fields.Char(compute='_compute_url',string='UrlParameters')

    @api.depends('source_id','source_id.name','job_id')
    def_compute_url(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        forsourceinself:
            source.url=urls.url_join(base_url,"%s?%s"%(source.job_id.website_url,
                urls.url_encode({
                    'utm_campaign':self.env.ref('hr_recruitment.utm_campaign_job').name,
                    'utm_medium':self.env.ref('utm.utm_medium_website').name,
                    'utm_source':source.source_id.name
                })
            ))


classApplicant(models.Model):

    _inherit='hr.applicant'

    defwebsite_form_input_filter(self,request,values):
        if'partner_name'invalues:
            values.setdefault('name','%s\'sApplication'%values['partner_name'])
        ifvalues.get('job_id'):
            job=self.env['hr.job'].browse(values.get('job_id'))
            ifnotjob.sudo().website_published:
                raiseUserError(_("Youcannotapplyforthisjob."))
            stage=self.env['hr.recruitment.stage'].sudo().search([
                ('fold','=',False),
                '|',('job_ids','=',False),('job_ids','=',values['job_id']),
            ],order='sequenceasc',limit=1)
            ifstage:
                values['stage_id']=stage.id
        returnvalues


classJob(models.Model):

    _name='hr.job'
    _inherit=['hr.job','website.seo.metadata','website.published.multi.mixin']

    def_get_default_website_description(self):
        default_description=self.env["ir.model.data"].xmlid_to_object("website_hr_recruitment.default_website_description")
        return(default_description._render()ifdefault_descriptionelse"")

    website_description=fields.Html('Websitedescription',translate=html_translate,sanitize_attributes=False,default=_get_default_website_description,prefetch=False,sanitize_form=False)

    def_compute_website_url(self):
        super(Job,self)._compute_website_url()
        forjobinself:
            job.website_url="/jobs/detail/%s"%job.id

    defset_open(self):
        self.write({'website_published':False})
        returnsuper(Job,self).set_open()

    defget_backend_menu_id(self):
        returnself.env.ref('hr_recruitment.menu_hr_recruitment_root').id
