#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale.tests.commonimportTestSaleCommon
fromflectra.testsimportForm,tagged


@tagged('-at_install','post_install')
classTestSaleOrder(TestSaleCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        Pricelist=cls.env['product.pricelist']
        Product=cls.env['product.product']
        SaleOrder=cls.env['sale.order']
        SaleOrderTemplate=cls.env['sale.order.template']
        SaleOrderTemplateLine=cls.env['sale.order.template.line']
        SaleOrderTemplateOption=cls.env['sale.order.template.option']

        #somevariablestoeaseassertsintests
        cls.pub_product_price=100.0
        cls.pl_product_price=80.0
        cls.tpl_discount=10.0
        cls.pl_discount=(cls.pub_product_price-cls.pl_product_price)*100/cls.pub_product_price
        cls.merged_discount=100.0-(100.0-cls.pl_discount)*(100.0-cls.tpl_discount)/100.0

        cls.pub_option_price=200.0
        cls.pl_option_price=100.0
        cls.tpl_option_discount=20.0
        cls.pl_option_discount=(cls.pub_option_price-cls.pl_option_price)*100/cls.pub_option_price
        cls.merged_option_discount=100.0-(100.0-cls.pl_option_discount)*(100.0-cls.tpl_option_discount)/100.0

        #createsomeproducts
        cls.product_1=Product.create({
            'name':'Product1',
            'lst_price':cls.pub_product_price,
        })

        cls.optional_product=Product.create({
            'name':'Optionalproduct',
            'lst_price':cls.pub_option_price,
        })

        #createsomequotationtemplates
        cls.quotation_template_no_discount=SaleOrderTemplate.create({
            'name':'Aquotationtemplatewithoutdiscount'
        })

        SaleOrderTemplateLine.create({
            'name':'Product1',
            'sale_order_template_id':cls.quotation_template_no_discount.id,
            'product_id':cls.product_1.id,
            'product_uom_id':cls.product_1.uom_id.id
        })

        SaleOrderTemplateOption.create({
            'name':'Optionalproduct1',
            'sale_order_template_id':cls.quotation_template_no_discount.id,
            'product_id':cls.optional_product.id,
            'uom_id':cls.optional_product.uom_id.id
        })

        #createsomepricelists
        cls.discount_included_price_list=Pricelist.create({
            'name':'DiscountincludedPricelist',
            'discount_policy':'with_discount',
            'item_ids':[
                (0,0,{
                    'name':'Product1premiumprice',
                    'applied_on':'1_product',
                    'product_tmpl_id':cls.product_1.product_tmpl_id.id,
                    'compute_price':'fixed',
                    'fixed_price':cls.pl_product_price
                }),
                (0,0,{
                    'name':'Optionalproductpremiumprice',
                    'applied_on':'1_product',
                    'product_tmpl_id':cls.optional_product.product_tmpl_id.id,
                    'compute_price':'fixed',
                    'fixed_price':cls.pl_option_price
                })]
        })

        cls.discount_excluded_price_list=Pricelist.create({
            'name':'DiscountexcludedPricelist',
            'discount_policy':'without_discount',
            'item_ids':[
                (0,0,{
                    'name':'Product1premiumprice',
                    'applied_on':'1_product',
                    'product_tmpl_id':cls.product_1.product_tmpl_id.id,
                    'compute_price':'fixed',
                    'fixed_price':cls.pl_product_price
                }),
                (0,0,{
                    'name':'Optionalproductpremiumprice',
                    'applied_on':'1_product',
                    'product_tmpl_id':cls.optional_product.product_tmpl_id.id,
                    'compute_price':'fixed',
                    'fixed_price':cls.pl_option_price
                })]
        })

        #createsomesaleorders
        cls.sale_order=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })

        cls.sale_order_no_price_list=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })

    deftest_01_template_without_pricelist(self):
        """
        Thistestchecksthatwithoutanypricelist,thepublicprice
        oftheproductisusedinthesaleorderafterselectinga
        quotationtemplate.
        """
        #firstcase,withoutdiscountinthequotationtemplate
        self.sale_order_no_price_list.write({
            'sale_order_template_id':self.quotation_template_no_discount.id
        })
        self.sale_order_no_price_list.onchange_sale_order_template_id()

        self.assertEqual(
            len(self.sale_order_no_price_list.order_line),
            1,
            "Thesaleordershallcontainsthesamenumberofproductsas"
            "thequotationtemplate.")

        self.assertEqual(
            self.sale_order_no_price_list.order_line[0].product_id.id,
            self.product_1.id,
            "Thesaleordershallcontainsthesameproductsasthe"
            "quotationtemplate.")

        self.assertEqual(
            self.sale_order_no_price_list.order_line[0].price_unit,
            self.pub_product_price,
            "Withoutanypricelistanddiscount,thepublicpriceof"
            "theproductshallbeused.")

        self.assertEqual(
            len(self.sale_order_no_price_list.sale_order_option_ids),
            1,
            "Thesaleordershallcontainsthesamenumberofoptionalproductsas"
            "thequotationtemplate.")

        self.assertEqual(
            self.sale_order_no_price_list.sale_order_option_ids[0].product_id.id,
            self.optional_product.id,
            "Thesaleordershallcontainsthesameoptionalproductsasthe"
            "quotationtemplate.")

        self.assertEqual(
            self.sale_order_no_price_list.sale_order_option_ids[0].price_unit,
            self.pub_option_price,
            "Withoutanypricelistanddiscount,thepublicpriceof"
            "theoptionalproductshallbeused.")

        #addtheoptiontotheorder
        self.sale_order_no_price_list.sale_order_option_ids[0].button_add_to_order()

        self.assertEqual(
            len(self.sale_order_no_price_list.order_line),
            2,
            "Whenanoptionisadded,aneworderlineiscreated")

        self.assertEqual(
            self.sale_order_no_price_list.order_line[1].product_id.id,
            self.optional_product.id,
            "Thesaleordershallcontainsthesameproductsasthe"
            "quotationtemplate.")

        self.assertEqual(
            self.sale_order_no_price_list.order_line[1].price_unit,
            self.pub_option_price,
            "Withoutanypricelistanddiscount,thepublicpriceof"
            "theoptionalproductshallbeused.")

    deftest_02_template_with_discount_included_pricelist(self):
        """
        Thistestchecksthatwitha'discountincluded'pricelist,
        thepriceusedinthesaleorderiscomputedaccordingtothe
        pricelist.
        """

        #firstcase,withoutdiscountinthequotationtemplate
        self.sale_order.write({
            'pricelist_id':self.discount_included_price_list.id,
            'sale_order_template_id':self.quotation_template_no_discount.id
        })
        self.sale_order.onchange_sale_order_template_id()

        self.assertEqual(
            self.sale_order.order_line[0].price_unit,
            self.pl_product_price,
            "Ifapricelistisset,theproductpriceshallbecomputed"
            "accordingtoit.")

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].price_unit,
            self.pl_option_price,
            "Ifapricelistisset,theoptionalproductpriceshall"
            "becomputedaccordingtoit.")

        #addtheoptiontotheorder
        self.sale_order.sale_order_option_ids[0].button_add_to_order()

        self.assertEqual(
            self.sale_order.order_line[1].price_unit,
            self.pl_option_price,
            "Ifapricelistisset,theoptionalproductpriceshall"
            "becomputedaccordingtoit.")

    deftest_03_template_with_discount_excluded_pricelist(self):
        """
        Thistestchecksthatwitha'discountexcluded'pricelist,
        thepriceusedinthesaleorderistheproductpublicpriceand
        thediscountiscomputedaccordingtothepricelist.
        """

        self.sale_order.write({
            'pricelist_id':self.discount_excluded_price_list.id,
            'sale_order_template_id':self.quotation_template_no_discount.id
        })
        self.sale_order.onchange_sale_order_template_id()

        self.assertEqual(
            self.sale_order.order_line[0].price_unit,
            self.pub_product_price,
            "Ifapricelistissetwithoutdiscountincluded,theunit"
            "priceshallbethepublicproductprice.")

        self.assertEqual(
            self.sale_order.order_line[0].price_subtotal,
            self.pl_product_price,
            "Ifapricelistissetwithoutdiscountincluded,thesubtotal"
            "priceshallbethepricecomputedaccordingtothepricelist.")

        self.assertEqual(
            self.sale_order.order_line[0].discount,
            self.pl_discount,
            "Ifapricelistissetwithoutdiscountincluded,thediscount"
            "shallbecomputedaccordingtothepriceunitandthesubtotal."
            "price")

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].price_unit,
            self.pub_option_price,
            "Ifapricelistissetwithoutdiscountincluded,theunit"
            "priceshallbethepublicoptionalproductprice.")

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].discount,
            self.pl_option_discount,
            "Ifapricelistissetwithoutdiscountincluded,thediscount"
            "shallbecomputedaccordingtotheoptionalpriceunitand"
            "thesubtotalprice.")

        #addtheoptiontotheorder
        self.sale_order.sale_order_option_ids[0].button_add_to_order()

        self.assertEqual(
            self.sale_order.order_line[1].price_unit,
            self.pub_option_price,
            "Ifapricelistissetwithoutdiscountincluded,theunit"
            "priceshallbethepublicoptionalproductprice.")

        self.assertEqual(
            self.sale_order.order_line[1].price_subtotal,
            self.pl_option_price,
            "Ifapricelistissetwithoutdiscountincluded,thesubtotal"
            "priceshallbethepricecomputedaccordingtothepricelist.")

        self.assertEqual(
            self.sale_order.order_line[1].discount,
            self.pl_option_discount,
            "Ifapricelistissetwithoutdiscountincluded,thediscount"
            "shallbecomputedaccordingtothepriceunitandthesubtotal."
            "price")

    deftest_04_update_pricelist_option_line(self):
        """
        Thistestchecksthatoptionline'svaluesarecorrectly
        updatedafterapricelistupdate
        """

        #Necessaryfor_onchange_discount()check
        self.env.user.write({
            'groups_id':[(4,self.env.ref('product.group_discount_per_so_line').id)],
        })

        self.sale_order.write({
            'sale_order_template_id':self.quotation_template_no_discount.id
        })
        self.sale_order.onchange_sale_order_template_id()

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].price_unit,
            self.pub_option_price,
            "Ifnopricelistisset,theunitpriceshallbetheoption'sproductprice.")

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].discount,0,
            "Ifnopricelistisset,thediscountshouldbe0.")

        self.sale_order.write({
            'pricelist_id':self.discount_included_price_list.id,
        })
        self.sale_order.update_prices()

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].price_unit,
            self.pl_option_price,
            "Ifapricelistissetwithdiscountincluded,"
            "theunitpriceshallbetheoption'sproductdiscountedprice.")

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].discount,0,
            "Ifapricelistissetwithdiscountincluded,"
            "thediscountshouldbe0.")

        self.sale_order.write({
            'pricelist_id':self.discount_excluded_price_list.id,
        })
        self.sale_order.update_prices()

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].price_unit,
            self.pub_option_price,
            "Ifapricelistissetwithoutdiscountincluded,"
            "theunitpriceshallbetheoption'sproductsaleprice.")

        self.assertEqual(
            self.sale_order.sale_order_option_ids[0].discount,
            self.pl_option_discount,
            "Ifapricelistissetwithoutdiscountincluded,"
            "thediscountshouldbecorrectlycomputed.")

    deftest_option_creation(self):
        """Makesuretheproductuomisautomaticallyaddedtotheoptionwhentheproductisspecified"""
        order_form=Form(self.sale_order)
        withorder_form.sale_order_option_ids.new()asoption:
            option.product_id=self.product_1
            self.assertTrue(bool(option.uom_id))
