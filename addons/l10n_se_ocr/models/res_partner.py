#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_
fromstdnumimportluhn


classResPartner(models.Model):
    _inherit='res.partner'

    l10n_se_check_vendor_ocr=fields.Boolean(string='CheckVendorOCR',help='ThisVendorusesOCRNumberontheirVendorBills.')
    l10n_se_default_vendor_payment_ref=fields.Char(string='DefaultVendorPaymentRef',help='Ifset,thevendorusesthesameDefaultPaymentReferenceorOCRNumberonalltheirVendorBills.')

    @api.onchange('l10n_se_default_vendor_payment_ref')
    defonchange_l10n_se_default_vendor_payment_ref(self):
        ifnotself.l10n_se_default_vendor_payment_ref==""andself.l10n_se_check_vendor_ocr:
            reference=self.l10n_se_default_vendor_payment_ref
            try:
                luhn.validate(reference)
            except:
                return{'warning':{'title':_('Warning'),'message':_('DefaultvendorOCRnumberisn\'tavalidOCRnumber.')}}
