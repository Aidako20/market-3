#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    company_lunch_minimum_threshold=fields.Float(string="MaximumAllowedOverdraft",readonly=False,related='company_id.lunch_minimum_threshold')
