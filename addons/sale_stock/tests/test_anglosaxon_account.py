#-*-coding:utf-8-*-
fromflectra.addons.sale_stock.tests.test_anglo_saxon_valuation_reconciliationimportTestValuationReconciliation
fromflectra.testsimporttagged

@tagged('post_install','-at_install')
classTestAngloSaxonAccounting(TestValuationReconciliation):

    deftest_cogs_should_use_price_from_the_right_company(self):
        """
        ReproducetheflowofcreatinganinvoicefromasaleorderwithcompanyA
        andpostingtheinvoicewithbothcompaniesselectedandcompanyBasthemain.
        """
        company_a_data=self.company_data
        company_b_data=self.company_data_2
        companies_with_b_first=company_b_data['company']+company_a_data['company']
        product=self.test_product_delivery

        #setdifferentcostpriceforthesameproductinthe2companies
        company_a_standard_price=20.0
        product.with_company(company_a_data['company']).standard_price=company_a_standard_price
        company_b_standard_price=10.0
        product.with_company(company_b_data['company']).standard_price=company_b_standard_price

        #createsaleorderwithcompanyAindraft(bydefault,self.env.user.company_idiscompanyA)
        company_a_order=self._create_sale(product,'2021-01-01')
        company_a_invoice=self._create_invoice_for_so(company_a_order,product,'2021-01-10')

        #PosttheinvoicefromcompanyAwithcompanyB
        company_a_invoice.with_context(allowed_company_ids=companies_with_b_first.ids).action_post()

        #checkcostusedforanglo_saxon_lineisfromcompanyA
        anglo_saxon_lines=company_a_invoice.line_ids.filtered('is_anglo_saxon_line')
        self.assertRecordValues(anglo_saxon_lines,[
            {'debit':0.0,'credit':company_a_standard_price},
            {'debit':company_a_standard_price,'credit':0.0},
        ])
