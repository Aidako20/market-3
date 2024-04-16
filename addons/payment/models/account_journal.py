#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportValidationError


classAccountJournal(models.Model):
    _inherit='account.journal'

    @api.constrains('type')
    def_check_journal_type_change(self):
        acquirer_incompatible_journals=self.filtered(lambdaj:j.typenotin('bank','cash'))
        ifacquirer_incompatible_journalsandself.env['payment.acquirer'].search_count([('journal_id','in',acquirer_incompatible_journals.ids)]):
            raiseValidationError(_("Anacquirerisusingthisjournal.Onlybankandcashtypesareallowed."))
