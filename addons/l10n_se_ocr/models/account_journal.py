#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError


classAccountJournal(models.Model):
    _inherit='account.journal'

    invoice_reference_model=fields.Selection(selection_add=[('se_ocr2','SwedenOCRLevel1&2'),('se_ocr3','SwedenOCRLevel3'),('se_ocr4','SwedenOCRLevel4')],ondelete={'se_ocr2':'setdefault','se_ocr3':'setdefault','se_ocr4':'setdefault'})
    l10n_se_invoice_ocr_length=fields.Integer(string='OCRNumberLength',help="TotallengthofOCRReferenceNumberincludingchecksum.",default=6)

    @api.constrains('l10n_se_invoice_ocr_length')
    def_check_l10n_se_invoice_ocr_length(self):
        ifself.l10n_se_invoice_ocr_length<6:
            returnValidationError(_('OCRReferenceNumberlengthneedtobegreaterthan5.Pleasecorrectsettingsunderinvoicejournalsettings.'))
