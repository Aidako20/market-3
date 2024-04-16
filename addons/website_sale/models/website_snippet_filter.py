#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classWebsiteSnippetFilter(models.Model):
    _inherit='website.snippet.filter'

    @api.model
    def_get_website_currency(self):
        pricelist=self.env['website'].get_current_website().get_current_pricelist()
        returnpricelist.currency_id
