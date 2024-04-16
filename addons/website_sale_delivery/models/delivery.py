#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classDeliveryCarrier(models.Model):
    _name='delivery.carrier'
    _inherit=['delivery.carrier','website.published.multi.mixin']

    website_description=fields.Text(related='product_id.description_sale',string='DescriptionforOnlineQuotations',readonly=False)
