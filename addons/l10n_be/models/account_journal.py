#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classAccountJournal(models.Model):
    _inherit='account.journal'

    invoice_reference_model=fields.Selection(selection_add=[
        ('be','Belgium')
        ],ondelete={'be':lambdarecs:recs.write({'invoice_reference_model':'flectra'})})

