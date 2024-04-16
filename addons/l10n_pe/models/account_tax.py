#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classAccountTax(models.Model):
    _inherit="account.tax"

    l10n_pe_edi_tax_code=fields.Selection([
        ('1000','IGV-GeneralSalesTax'),
        ('1016','IVAP-TaxonSalePaddyRice'),
        ('2000','ISC-SelectiveExciseTax'),
        ('7152','ICBPER-Plasticbagtax'),
        ('9995','EXP-Exportation'),
        ('9996','GRA-Free'),
        ('9997','EXO-Exonerated'),
        ('9998','INA-Unaffected'),
        ('9999','OTROS-Othertaxes')
    ],'EDIperuviancode')

    l10n_pe_edi_unece_category=fields.Selection([
        ('E','Exemptfromtax'),
        ('G','Freeexportitem,taxnotcharged'),
        ('O','Servicesoutsidescopeoftax'),
        ('S','Standardrate'),
        ('Z','Zeroratedgoods')],'EDIUNECEcode',
        help="FollowtheUN/ECE5305standardfromtheUnitedNationsEconomicCommissionforEuropeformore"
             "informationhttp://www.unece.org/trade/untdid/d08a/tred/tred5305.htm"
    )


classAccountTaxTemplate(models.Model):
    _inherit="account.tax.template"

    l10n_pe_edi_tax_code=fields.Selection([
        ('1000','IGV-GeneralSalesTax'),
        ('1016','IVAP-TaxonSalePaddyRice'),
        ('2000','ISC-SelectiveExciseTax'),
        ('7152','ICBPER-Plasticbagtax'),
        ('9995','EXP-Exportation'),
        ('9996','GRA-Free'),
        ('9997','EXO-Exonerated'),
        ('9998','INA-Unaffected'),
        ('9999','OTROS-Othertaxes')
    ],'EDIperuviancode')

    l10n_pe_edi_unece_category=fields.Selection([
        ('E','Exemptfromtax'),
        ('G','Freeexportitem,taxnotcharged'),
        ('O','Servicesoutsidescopeoftax'),
        ('S','Standardrate'),
        ('Z','Zeroratedgoods')],'EDIUNECEcode',
        help="FollowtheUN/ECE5305standardfromtheUnitedNationsEconomicCommissionforEuropeformore"
             "information http://www.unece.org/trade/untdid/d08a/tred/tred5305.htm"
    )

    def_get_tax_vals(self,company,tax_template_to_tax):
        val=super()._get_tax_vals(company,tax_template_to_tax)
        val.update({
            'l10n_pe_edi_tax_code':self.l10n_pe_edi_tax_code,
            'l10n_pe_edi_unece_category':self.l10n_pe_edi_unece_category,
        })
        returnval
