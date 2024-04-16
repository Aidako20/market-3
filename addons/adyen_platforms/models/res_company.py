#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit="res.company"

    adyen_account_id=fields.Many2one('adyen.account',string='AdyenAccount',readonly=True)
