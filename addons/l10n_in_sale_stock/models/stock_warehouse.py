#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classStock(models.Model):
    _inherit='stock.warehouse'

    l10n_in_sale_journal_id=fields.Many2one('account.journal',string="SaleJournal")
