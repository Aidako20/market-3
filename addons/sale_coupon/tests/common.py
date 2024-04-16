#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale.tests.test_sale_product_attribute_value_configimportTestSaleProductAttributeValueCommon


classTestSaleCouponCommon(TestSaleProductAttributeValueCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestSaleCouponCommon,cls).setUpClass()

        #setcurrencytonotrelyondemodataandavoidpossibleracecondition
        cls.currency_ratio=1.0
        pricelist=cls.env.ref('product.list0')
        pricelist.currency_id=cls._setup_currency(cls.currency_ratio)

        #Setalltheexistingprogramstoactive=Falsetoavoidinterference
        cls.env['coupon.program'].search([]).write({'active':False})

        #createpartnerforsaleorder.
        cls.steve=cls.env['res.partner'].create({
            'name':'SteveBucknor',
            'email':'steve.bucknor@example.com',
        })

        cls.empty_order=cls.env['sale.order'].create({
            'partner_id':cls.steve.id
        })

        cls.uom_unit=cls.env.ref('uom.product_uom_unit')

        #Taxes
        cls.tax_15pc_excl=cls.env['account.tax'].create({
            'name':"Tax15%",
            'amount_type':'percent',
            'amount':15,
            'type_tax_use':'sale',
        })

        cls.tax_10pc_incl=cls.env['account.tax'].create({
            'name':"10%Taxincl",
            'amount_type':'percent',
            'amount':10,
            'price_include':True,
        })

        cls.tax_10pc_base_incl=cls.env['account.tax'].create({
            'name':"10%Taxinclbaseamount",
            'amount_type':'percent',
            'amount':10,
            'price_include':True,
            'include_base_amount':True,
        })

        cls.tax_10pc_excl=cls.env['account.tax'].create({
            'name':"10%Taxexcl",
            'amount_type':'percent',
            'amount':10,
            'price_include':False,
        })

        cls.tax_20pc_excl=cls.env['account.tax'].create({
            'name':"20%Taxexcl",
            'amount_type':'percent',
            'amount':20,
            'price_include':False,
        })

        #products
        cls.product_A=cls.env['product.product'].create({
            'name':'ProductA',
            'list_price':100,
            'sale_ok':True,
            'taxes_id':[(6,0,[cls.tax_15pc_excl.id])],
        })

        cls.product_B=cls.env['product.product'].create({
            'name':'ProductB',
            'list_price':5,
            'sale_ok':True,
            'taxes_id':[(6,0,[cls.tax_15pc_excl.id])],
        })

        cls.product_C=cls.env['product.product'].create({
            'name':'ProductC',
            'list_price':100,
            'sale_ok':True,
            'taxes_id':[(6,0,[])],

        })

        #ImmediateProgramByA+B:getBfree
        #NoConditions
        cls.immediate_promotion_program=cls.env['coupon.program'].create({
            'name':'BuyA+1B,1Barefree',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'reward_product_id':cls.product_B.id,
            'rule_products_domain':"[('id','in',[%s])]"%(cls.product_A.id),
            'active':True,
        })

        cls.code_promotion_program=cls.env['coupon.program'].create({
            'name':'Buy1A+Entercode,1Aisfree',
            'promo_code_usage':'code_needed',
            'reward_type':'product',
            'reward_product_id':cls.product_A.id,
            'rule_products_domain':"[('id','in',[%s])]"%(cls.product_A.id),
            'active':True,
        })

        cls.code_promotion_program_with_discount=cls.env['coupon.program'].create({
            'name':'Buy1C+Entercode,10percentdiscountonC',
            'promo_code_usage':'code_needed',
            'reward_type':'discount',
            'discount_type':'percentage',
            'discount_percentage':10,
            'rule_products_domain':"[('id','in',[%s])]"%(cls.product_C.id),
            'active':True,
            'discount_apply_on':'on_order',
        })
