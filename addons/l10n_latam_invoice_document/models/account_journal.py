#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError

classAccountJournal(models.Model):

    _inherit="account.journal"

    l10n_latam_use_documents=fields.Boolean(
        'UseDocuments?',help="Ifactive:willbeusingforlegalinvoicing(invoices,debit/creditnotes)."
        "Ifnotsetmeansthatwillbeusedtoregisteraccountingentriesnotrelatedtoinvoicinglegaldocuments."
        "ForExample:Receipts,TaxPayments,Registerjournalentries")
    l10n_latam_company_use_documents=fields.Boolean(compute='_compute_l10n_latam_company_use_documents')

    @api.depends('company_id')
    def_compute_l10n_latam_company_use_documents(self):
        forrecinself:
            rec.l10n_latam_company_use_documents=rec.company_id._localization_use_documents()

    @api.onchange('company_id','type')
    def_onchange_company(self):
        self.l10n_latam_use_documents=self.typein['sale','purchase']and\
            self.l10n_latam_company_use_documents

    @api.constrains('l10n_latam_use_documents')
    defcheck_use_document(self):
        forrecinself:
            ifrec.env['account.move'].search([('journal_id','=',rec.id),('posted_before','=',True)],limit=1):
                raiseValidationError(_(
                    'Youcannotmodifythefield"UseDocuments?"iftherearevalidatedinvoicesinthisjournal!'))

    @api.onchange('type','l10n_latam_use_documents')
    def_onchange_type(self):
        res=super()._onchange_type()
        ifself.l10n_latam_use_documents:
            self.refund_sequence=False
        returnres
