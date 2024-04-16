#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classL10nLatamDocumentType(models.Model):

    _inherit='l10n_latam.document.type'

    internal_type=fields.Selection(
        selection_add=[
            ('invoice','Invoices'),
            ('invoice_in','PurchaseInvoices'),
            ('debit_note','DebitNotes'),
            ('credit_note','CreditNotes'),
            ('receipt_invoice','ReceiptInvoice')])

    def_format_document_number(self,document_number):
        """MakevalidationofImportDispatchNumber
          *makingvalidationsonthedocument_number.Ifitiswrongitshouldraiseanexception
          *formatthedocument_numberagainstapatternandreturnit
        """
        self.ensure_one()
        ifself.country_id.code!="CL":
            returnsuper()._format_document_number(document_number)

        ifnotdocument_number:
            returnFalse

        returndocument_number.zfill(6)

    def_filter_taxes_included(self,taxes):
        """InChileweincludetaxesdependingondocumenttype"""
        self.ensure_one()
        ifself.country_id.code=="CL"andself.codein['39','41','110','111','112','34']:
            returntaxes.filtered(lambdax:x.l10n_cl_sii_code==14)
        returnsuper()._filter_taxes_included(taxes)
