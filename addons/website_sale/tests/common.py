fromflectra.tests.commonimportTransactionCase

classTestWebsiteSaleCommon(TransactionCase):

    defsetUp(self):
        super(TestWebsiteSaleCommon,self).setUp()
        #Resetcountryandfiscalcountry,sothatfieldsaddedbylocalizationsare
        #hiddenandnon-required.
        #Alsoremovedefaulttaxesfromthecompanyanditsaccounts,toavoidinconsistencies
        #withemptyfiscalcountry.
        self.env.company.write({
            'country_id':None,#Alsoresetsaccount_fiscal_country_id
            'account_sale_tax_id':None,
            'account_purchase_tax_id':None,
        })
        account_with_taxes=self.env['account.account'].search([('tax_ids','!=',False),('company_id','=',self.env.company.id)])
        account_with_taxes.write({
            'tax_ids':[(5,0,0)],
        })
        #Updatewebsitepricelisttoensurecurrencyissameasenv.company
        website=self.env['website'].get_current_website()
        pricelist=website.get_current_pricelist()
        pricelist.write({'currency_id':self.env.company.currency_id.id})
