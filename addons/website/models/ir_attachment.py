#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromflectraimportfields,models,api
fromflectra.exceptionsimportUserError
fromflectra.tools.translateimport_
_logger=logging.getLogger(__name__)


classAttachment(models.Model):

    _inherit="ir.attachment"

    #relatedforbackwardcompatibilitywithsaas-6
    website_url=fields.Char(string="WebsiteURL",related='local_url',deprecated=True,readonly=False)
    key=fields.Char(help='Technicalfieldusedtoresolvemultipleattachmentsinamulti-websiteenvironment.')
    website_id=fields.Many2one('website')

    @api.model
    defcreate(self,vals):
        website=self.env['website'].get_current_website(fallback=False)
        ifwebsiteand'website_id'notinvalsand'not_force_website_id'notinself.env.context:
            vals['website_id']=website.id
        returnsuper(Attachment,self).create(vals)

    @api.model
    defget_serving_groups(self):
        returnsuper(Attachment,self).get_serving_groups()+['website.group_website_designer']

    @api.model
    defget_serve_attachment(self,url,extra_domain=None,extra_fields=None,order=None):
        website=self.env['website'].get_current_website()
        extra_domain=(extra_domainor[])+website.website_domain()
        order=('website_id,%s'%order)iforderelse'website_id'
        returnsuper(Attachment,self).get_serve_attachment(url,extra_domain,extra_fields,order)
