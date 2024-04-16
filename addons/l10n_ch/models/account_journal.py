#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api

fromflectra.exceptionsimportValidationError

fromflectra.addons.base_iban.models.res_partner_bankimportvalidate_iban
fromflectra.addons.base.models.res_bankimportsanitize_account_number


classAccountJournal(models.Model):
    _inherit='account.journal'

    #creationofbankjournalsbygivingtheaccountnumber,allowcraetionofthe
    l10n_ch_postal=fields.Char('ClientNumber',related='bank_account_id.l10n_ch_postal',readonly=False)
    invoice_reference_model=fields.Selection(selection_add=[
        ('ch','Switzerland')
    ],ondelete={'ch':lambdarecs:recs.write({'invoice_reference_model':'flectra'})})

    @api.model
    defcreate(self,vals):
        rslt=super(AccountJournal,self).create(vals)

        #Thecalltosuper()createstherelatedbank_account_idfield
        if'l10n_ch_postal'invals:
            rslt.l10n_ch_postal=vals['l10n_ch_postal']
        returnrslt

    defwrite(self,vals):
        rslt=super(AccountJournal,self).write(vals)

        #Thecalltosuper()createstherelatedbank_account_idfieldifnecessary
        if'l10n_ch_postal'invals:
            forrecordinself.filtered('bank_account_id'):
                record.bank_account_id.l10n_ch_postal=vals['l10n_ch_postal']
        returnrslt

    @api.onchange('bank_acc_number')
    def_onchange_set_l10n_ch_postal(self):
        try:
            validate_iban(self.bank_acc_number)
            is_iban=True
        exceptValidationError:
            is_iban=False

        ifis_iban:
            self.l10n_ch_postal=self.env['res.partner.bank']._retrieve_l10n_ch_postal(sanitize_account_number(self.bank_acc_number))
        else:
            self.l10n_ch_postal=self.bank_acc_number
