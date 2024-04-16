#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    @api.model
    def_redirect_to_iap_account(self):
        return{
            'type':'ir.actions.act_url',
            'url':self.env['iap.account'].get_account_url(),
        }
