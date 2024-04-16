#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classServiceTaxRate(models.Model):
    _name="l10n_eu_service.service_tax_rate"
    _description="EUServiceTaxRate"

    country_id=fields.Many2one('res.country',string='Country')
    rate=fields.Float(string="VATRate")
