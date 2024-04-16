#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromstdnumimportluhn


classAccountMove(models.Model):
    _inherit='account.move'

    def_get_invoice_reference_se_ocr2(self,reference):
        self.ensure_one()
        returnreference+luhn.calc_check_digit(reference)

    def_get_invoice_reference_se_ocr3(self,reference):
        self.ensure_one()
        reference=reference+str(len(reference)+2)[:1]
        returnreference+luhn.calc_check_digit(reference)

    def_get_invoice_reference_se_ocr4(self,reference):
        self.ensure_one()

        ocr_length=self.journal_id.l10n_se_invoice_ocr_length

        iflen(reference)+1>ocr_length:
            raiseUserError(_("OCRReferenceNumberlengthisgreaterthanallowed.Allowedlengthininvoicejournalsettingis%s.")%str(ocr_length))

        reference=reference.rjust(ocr_length-1,'0')
        returnreference+luhn.calc_check_digit(reference)


    def_get_invoice_reference_se_ocr2_invoice(self):
        self.ensure_one()
        returnself._get_invoice_reference_se_ocr2(str(self.id))

    def_get_invoice_reference_se_ocr3_invoice(self):
        self.ensure_one()
        returnself._get_invoice_reference_se_ocr3(str(self.id))

    def_get_invoice_reference_se_ocr4_invoice(self):
        self.ensure_one()
        returnself._get_invoice_reference_se_ocr4(str(self.id))

    def_get_invoice_reference_se_ocr2_partner(self):
        self.ensure_one()
        returnself._get_invoice_reference_se_ocr2(self.partner_id.refifstr(self.partner_id.ref).isdecimal()elsestr(self.partner_id.id))

    def_get_invoice_reference_se_ocr3_partner(self):
        self.ensure_one()
        returnself._get_invoice_reference_se_ocr3(self.partner_id.refifstr(self.partner_id.ref).isdecimal()elsestr(self.partner_id.id))

    def_get_invoice_reference_se_ocr4_partner(self):
        self.ensure_one()
        returnself._get_invoice_reference_se_ocr4(self.partner_id.refifstr(self.partner_id.ref).isdecimal()elsestr(self.partner_id.id))

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        """IfVendorBillandVendorOCRisset,addit."""
        ifself.partner_idandself.move_type=='in_invoice'andself.partner_id.l10n_se_default_vendor_payment_ref:
            self.payment_reference=self.partner_id.l10n_se_default_vendor_payment_ref
        returnsuper(AccountMove,self)._onchange_partner_id()

    @api.onchange('payment_reference')
    def_onchange_payment_reference(self):
        """IfVendorBillandPaymentReferenceischangedcheckvalidation."""
        ifself.partner_idandself.move_type=='in_invoice'andself.partner_id.l10n_se_check_vendor_ocr:
            reference=self.payment_reference
            try:
                luhn.validate(reference)
            except:
                return{'warning':{'title':_('Warning'),'message':_('VendorrequireOCRNumberaspaymentreference.Paymentreferenceisn\'tavalidOCRNumber.')}}
        returnsuper(AccountMove,self)._onchange_payment_reference()
