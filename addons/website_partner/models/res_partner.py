#-*-coding:utf-8-*-

fromflectraimportapi,fields,models
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.tools.translateimporthtml_translate


classWebsiteResPartner(models.Model):
    _name='res.partner'
    _inherit=['res.partner','website.seo.metadata']

    website_description=fields.Html('WebsitePartnerFullDescription',strip_style=True,translate=html_translate)
    website_short_description=fields.Text('WebsitePartnerShortDescription',translate=True)

    def_compute_website_url(self):
        super(WebsiteResPartner,self)._compute_website_url()
        forpartnerinself:
            partner.website_url="/partners/%s"%slug(partner)
