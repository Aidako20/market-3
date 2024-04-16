#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    lc_journal_id=fields.Many2one('account.journal',string='DefaultJournal',related='company_id.lc_journal_id',readonly=False)

