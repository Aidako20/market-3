#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classAccountInvoiceReport(models.Model):

    _inherit='account.invoice.report'

    l10n_ar_state_id=fields.Many2one('res.country.state','State',readonly=True)
    date=fields.Date(readonly=True,string="AccountingDate")

    _depends={
        'account.move':['partner_id','date'],
        'res.partner':['state_id'],
    }

    def_select(self):
        returnsuper()._select()+",contact_partner.state_idasl10n_ar_state_id,move.date"

    def_from(self):
        returnsuper()._from()+"LEFTJOINres_partnercontact_partnerONcontact_partner.id=move.partner_id"
