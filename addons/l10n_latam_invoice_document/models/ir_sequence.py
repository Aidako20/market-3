#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classIrSequence(models.Model):

    _inherit='ir.sequence'

    l10n_latam_document_type_id=fields.Many2one('l10n_latam.document.type','DocumentType')#stillneededforl10n_cluntilnextsaas
