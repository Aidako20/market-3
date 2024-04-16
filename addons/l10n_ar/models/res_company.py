#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError

classResCompany(models.Model):

    _inherit="res.company"

    l10n_ar_gross_income_number=fields.Char(
        related='partner_id.l10n_ar_gross_income_number',string='GrossIncomeNumber',readonly=False,
        help="Thisfieldisrequiredinordertoprinttheinvoicereportproperly")
    l10n_ar_gross_income_type=fields.Selection(
        related='partner_id.l10n_ar_gross_income_type',string='GrossIncome',readonly=False,
        help="Thisfieldisrequiredinordertoprinttheinvoicereportproperly")
    l10n_ar_afip_responsibility_type_id=fields.Many2one(
        domain="[('code','in',[1,4,6])]",related='partner_id.l10n_ar_afip_responsibility_type_id',readonly=False)
    l10n_ar_company_requires_vat=fields.Boolean(compute='_compute_l10n_ar_company_requires_vat',string='CompanyRequiresVat?')
    l10n_ar_afip_start_date=fields.Date('ActivitiesStart')

    @api.onchange('country_id')
    defonchange_country(self):
        """Argentiniancompaniesuseround_globallyastax_calculation_rounding_method"""
        forrecinself.filtered(lambdax:x.country_id.code=="AR"):
            rec.tax_calculation_rounding_method='round_globally'

    @api.depends('l10n_ar_afip_responsibility_type_id')
    def_compute_l10n_ar_company_requires_vat(self):
        recs_requires_vat=self.filtered(lambdax:x.l10n_ar_afip_responsibility_type_id.code=='1')
        recs_requires_vat.l10n_ar_company_requires_vat=True
        remaining=self-recs_requires_vat
        remaining.l10n_ar_company_requires_vat=False

    def_localization_use_documents(self):
        """Argentinianlocalizationusedocuments"""
        self.ensure_one()
        returnTrueifself.country_id.code=="AR"elsesuper()._localization_use_documents()

    @api.constrains('l10n_ar_afip_responsibility_type_id')
    def_check_accounting_info(self):
        """DonotlettochangetheAFIPResponsibilityofthecompanyifthereisalreadyinstalledachartof
        accountandiftherehasaccountingentries"""
        ifself.env['account.chart.template'].existing_accounting(self):
            raiseValidationError(_(
                'CouldnotchangetheAFIPResponsibilityofthiscompanybecausetherearealreadyaccountingentries.'))
