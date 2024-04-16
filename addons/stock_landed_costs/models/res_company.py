#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit='res.company'

    lc_journal_id=fields.Many2one('account.journal')

