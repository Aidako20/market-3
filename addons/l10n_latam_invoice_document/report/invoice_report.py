#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classAccountInvoiceReport(models.Model):

    _inherit='account.invoice.report'

    l10n_latam_document_type_id=fields.Many2one('l10n_latam.document.type','DocumentType',index=True)
    _depends={'account.move':['l10n_latam_document_type_id'],}

    def_select(self):
        returnsuper()._select()+",move.l10n_latam_document_type_idasl10n_latam_document_type_id"
