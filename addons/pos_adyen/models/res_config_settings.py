#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    adyen_account_id=fields.Many2one(string='AdyenAccount',related='company_id.adyen_account_id')

    defcreate_adyen_account(self):
        returnself.env['adyen.account'].action_create_redirect()
