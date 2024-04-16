#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classResCountry(models.Model):
    _inherit='res.country'

    defget_website_sale_countries(self,mode='billing'):
        returnself.sudo().search([])

    defget_website_sale_states(self,mode='billing'):
        returnself.sudo().state_ids
