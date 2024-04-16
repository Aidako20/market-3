#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classAccountMove(models.Model):
    _inherit="account.move"

    def_l10n_in_get_shipping_partner(self):
        shipping_partner=super()._l10n_in_get_shipping_partner()
        returnself.partner_shipping_idorshipping_partner

    @api.model
    def_l10n_in_get_shipping_partner_gstin(self,shipping_partner):
        returnshipping_partner.l10n_in_shipping_gstin
