#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
importflectra
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon

@flectra.tests.tagged('post_install','-at_install')
classTestPoSSetup(TestPoSCommon):
    """Thisgroupoftestsisforsanitycheckinsettingupglobalrecordswhichwillbeused
    ineachtesting.

    Ifatestfailshere,thenitmeansthereareinconsistenciesinwhatweexpectinthesetup.
    """
    defsetUp(self):
        super(TestPoSSetup,self).setUp()

        self.config=self.basic_config
        self.products=[
            self.create_product('Product1',self.categ_basic,lst_price=10.0,standard_price=5),
            self.create_product('Product2',self.categ_basic,lst_price=20.0,standard_price=10),
            self.create_product('Product3',self.categ_basic,lst_price=30.0,standard_price=15),
        ]

    deftest_basic_config_values(self):

        config=self.basic_config
        self.assertEqual(config.currency_id,self.company_currency)
        self.assertEqual(config.pricelist_id.currency_id,self.company_currency)

    deftest_other_currency_config_values(self):
        config=self.other_currency_config
        self.assertEqual(config.currency_id,self.other_currency)
        self.assertEqual(config.pricelist_id.currency_id,self.other_currency)

    deftest_product_categories(self):
        #checkbasicproductcategory
        #itisexpectedtohavestandardandmanual_periodicvaluation
        self.assertEqual(self.categ_basic.property_cost_method,'standard')
        self.assertEqual(self.categ_basic.property_valuation,'manual_periodic')
        #checkanglosaxonproductcategory
        #thisproductcategisexpectedtohavefifoandreal_timevaluation
        self.assertEqual(self.categ_anglo.property_cost_method,'fifo')
        self.assertEqual(self.categ_anglo.property_valuation,'real_time')

    deftest_product_price(self):
        defget_price(pricelist,product):
            returnpricelist.get_product_price(product,1,self.customer)


        #checkusdpricelist
        pricelist=self.basic_config.pricelist_id
        forproductinself.products:
            self.assertAlmostEqual(get_price(pricelist,product),product.lst_price)

        #checkeurpricelist
        #exchangeratetotheothercurrencyissetto0.5,thus,lst_price
        #isexpectedtohavehalfitsoriginalvalue.
        pricelist=self.other_currency_config.pricelist_id
        forproductinself.products:
            self.assertAlmostEqual(get_price(pricelist,product),product.lst_price*0.5)

    deftest_taxes(self):
        tax7=self.taxes['tax7']
        self.assertEqual(tax7.name,'Tax7%')
        self.assertAlmostEqual(tax7.amount,7)
        self.assertEqual(tax7.invoice_repartition_line_ids.mapped('account_id').id,self.tax_received_account.id)
        tax10=self.taxes['tax10']
        self.assertEqual(tax10.name,'Tax10%')
        self.assertAlmostEqual(tax10.amount,10)
        self.assertEqual(tax10.price_include,True)
        self.assertEqual(tax10.invoice_repartition_line_ids.mapped('account_id').id,self.tax_received_account.id)
        tax_group_7_10=self.taxes['tax_group_7_10']
        self.assertEqual(tax_group_7_10.name,'Tax7+10%')
        self.assertEqual(tax_group_7_10.amount_type,'group')
        self.assertEqual(sorted(tax_group_7_10.children_tax_ids.ids),sorted((tax7|tax10).ids))
