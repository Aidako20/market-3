#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classAccountJournal(models.Model):

    _inherit='account.journal'

    invoice_reference_model=fields.Selection(selection_add=[
        ('fi','FinnishStandardReference'),
        ('fi_rf','FinnishCreditorReference(RF)'),
    ],ondelete={'fi':lambdarecs:recs.write({'invoice_reference_model':'flectra'}),
                 'fi_rf':lambdarecs:recs.write({'invoice_reference_model':'flectra'})})
