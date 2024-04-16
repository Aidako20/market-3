#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.addons.base_iban.models.res_partner_bankimportnormalize_iban,pretty_iban,validate_iban
fromflectra.addons.base.models.res_bankimportsanitize_account_number
fromflectra.exceptionsimportValidationError

classResPartnerBank(models.Model):
    _inherit='res.partner.bank'

    l10n_ch_qr_iban=fields.Char(string='QR-IBAN',help="PuttheQR-IBANhereforyourownbankaccounts. Thatway,youcan"
                                                         "stillusethemainIBANintheAccountNumberwhileyouwillseethe"
                                                         "QR-IBANforthebarcode. ")

    def_validate_qr_iban(self,qr_iban):
        #Checkfirstifit'savalidIBAN.
        validate_iban(qr_iban)
        #Wesanitizefirstsothat_check_qr_iban_range()canextractcorrectIIDfromIBANtovalidateit.
        sanitized_qr_iban=sanitize_account_number(qr_iban)
        #Now,checkifit'svalidQR-IBAN(basedonitsIID).
        ifnotself._check_qr_iban_range(sanitized_qr_iban):
            raiseValidationError(_("QR-IBAN'%s'isinvalid.")%qr_iban)
        returnTrue

    @api.model
    defcreate(self,vals):
        ifvals.get('l10n_ch_qr_iban'):
            self._validate_qr_iban(vals['l10n_ch_qr_iban'])
            vals['l10n_ch_qr_iban']=pretty_iban(normalize_iban(vals['l10n_ch_qr_iban']))
        returnsuper().create(vals)

    defwrite(self,vals):
        ifvals.get('l10n_ch_qr_iban'):
            self._validate_qr_iban(vals['l10n_ch_qr_iban'])
            vals['l10n_ch_qr_iban']=pretty_iban(normalize_iban(vals['l10n_ch_qr_iban']))
        returnsuper().write(vals)

    def_is_qr_iban(self):
        returnsuper(ResPartnerBank,self)._is_qr_iban()orself.l10n_ch_qr_iban

    def_l10n_ch_get_qr_vals(self,amount,currency,debtor_partner,free_communication,structured_communication):
        qr_vals=super()._l10n_ch_get_qr_vals(amount,currency,debtor_partner,free_communication,structured_communication)
        #IfthereisaQRIBANweuseitforthebarcodeinsteadoftheaccountnumber
        ifself.l10n_ch_qr_iban:
            qr_vals[3]=sanitize_account_number(self.l10n_ch_qr_iban)
        returnqr_vals
