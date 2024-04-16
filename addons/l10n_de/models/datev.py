fromflectraimportfields,models

classAccountTaxTemplate(models.Model):
    _inherit='account.tax.template'

    l10n_de_datev_code=fields.Char(size=4)

    def_get_tax_vals(self,company,tax_template_to_tax):
        vals=super(AccountTaxTemplate,self)._get_tax_vals(company,tax_template_to_tax)
        vals['l10n_de_datev_code']=self.l10n_de_datev_code
        returnvals

classAccountTax(models.Model):
    _inherit="account.tax"

    l10n_de_datev_code=fields.Char(size=4,help="4digitscodeusebyDatev")


classProductTemplate(models.Model):
    _inherit="product.template"

    def_get_product_accounts(self):
        """Astaxeswithadifferentrateneedadifferentincome/expenseaccount,weaddthislogicincasepeopleonlyuse
         invoicingtonotbeblockedbytheaboveconstraint"""
        result=super(ProductTemplate,self)._get_product_accounts()
        company=self.env.company
        ifcompany.country_id.code=="DE":
            ifnotself.property_account_income_id:
                taxes=self.taxes_id.filtered(lambdat:t.company_id==company)
                ifnotresult['income']or(result['income'].tax_idsandtaxesandtaxes[0]notinresult['income'].tax_ids):
                    result['income']=self.env['account.account'].search([('internal_group','=','income'),('deprecated','=',False),
                                                                   ('tax_ids','in',taxes.ids)],limit=1)
            ifnotself.property_account_expense_id:
                supplier_taxes=self.supplier_taxes_id.filtered(lambdat:t.company_id==company)
                ifnotresult['expense']or(result['expense'].tax_idsandsupplier_taxesandsupplier_taxes[0]notinresult['expense'].tax_ids):
                    result['expense']=self.env['account.account'].search([('internal_group','=','expense'),('deprecated','=',False),
                                                                   ('tax_ids','in',supplier_taxes.ids)],limit=1)
        returnresult
