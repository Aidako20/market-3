#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classAccountMove(models.Model):
    _inherit='account.move'

    narration=fields.Text(translate=True)

    def_get_name_invoice_report(self):
        self.ensure_one()
        ifself.company_id.country_id.code=='SA':
            return'l10n_gcc_invoice.arabic_english_invoice'
        returnsuper()._get_name_invoice_report()


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    l10n_gcc_invoice_tax_amount=fields.Float(string='TaxAmount',compute='_compute_tax_amount',digits='ProductPrice')

    @api.depends('price_subtotal','price_total')
    def_compute_tax_amount(self):
        forrecordinself:
            record.l10n_gcc_invoice_tax_amount=record.price_total-record.price_subtotal
