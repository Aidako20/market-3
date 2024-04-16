#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classResPartner(models.Model):
    _inherit='res.partner'

    l10n_in_shipping_gstin=fields.Char("ShippingGSTIN")

    @api.constrains('l10n_in_shipping_gstin')
    def_check_l10n_in_shipping_gstin(self):
        check_vat_in=self.env['res.partner'].check_vat_in
        wrong_shipping_gstin_partner=self.filtered(lambdap:p.l10n_in_shipping_gstinandnotcheck_vat_in(p.l10n_in_shipping_gstin))
        ifwrong_shipping_gstin_partner:
            raiseValidationError(_("TheshippingGSTINnumber[%s]doesnotseemtobevalid")%(",".join(p.l10n_in_shipping_gstinforpinwrong_shipping_gstin_partner)))
