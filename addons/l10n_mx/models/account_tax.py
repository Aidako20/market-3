#coding:utf-8
fromflectraimportmodels,fields


classAccountTaxTemplate(models.Model):
    _inherit='account.tax.template'

    l10n_mx_tax_type=fields.Selection(
        selection=[
            ('Tasa',"Tasa"),
            ('Cuota',"Cuota"),
            ('Exento',"Exento"),
        ],
        string="FactorType",
        default='Tasa',
        help="TheCFDIversion3.3havetheattribute'TipoFactor'inthetaxlines.Initisindicatedthefactor"
             "typethatisappliedtothebaseofthetax.")

    def_get_tax_vals(self,company,tax_template_to_tax):
        #OVERRIDE
        res=super()._get_tax_vals(company,tax_template_to_tax)
        res['l10n_mx_tax_type']=self.l10n_mx_tax_type
        returnres


classAccountTax(models.Model):
    _inherit='account.tax'

    l10n_mx_tax_type=fields.Selection(
        selection=[
            ('Tasa',"Tasa"),
            ('Cuota',"Cuota"),
            ('Exento',"Exento"),
        ],
        string="FactorType",
        default='Tasa',
        help="TheCFDIversion3.3havetheattribute'TipoFactor'inthetaxlines.Initisindicatedthefactor"
             "typethatisappliedtothebaseofthetax.")
