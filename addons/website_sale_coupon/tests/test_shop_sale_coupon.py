#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimporttimedelta

fromflectraimportfields
fromflectra.testsimportHttpCase,tagged,TransactionCase
fromflectra.addons.sale.tests.test_sale_product_attribute_value_configimportTestSaleProductAttributeValueCommon


@tagged('post_install','-at_install')
classTestUi(TestSaleProductAttributeValueCommon,HttpCase):

    @classmethod
    defsetUpClass(cls):
        super(TestUi,cls).setUpClass()
        #setcurrencytonotrelyondemodataandavoidpossibleracecondition
        cls.currency_ratio=1.0
        pricelist=cls.env.ref('product.list0')
        new_currency=cls._setup_currency(cls.currency_ratio)
        pricelist.currency_id=new_currency
        pricelist.flush()


    deftest_01_admin_shop_sale_coupon_tour(self):
        #preenable"Show#found"optiontoavoidracecondition...
        public_category=self.env['product.public.category'].create({'name':'PublicCategory'})

        large_cabinet=self.env['product.product'].create({
            'name':'SmallCabinet',
            'list_price':320.0,
            'type':'consu',
            'is_published':True,
            'sale_ok':True,
            'public_categ_ids':[(4,public_category.id)],
            'taxes_id':False,
        })

        free_large_cabinet=self.env['product.product'].create({
            'name':'FreeProduct-SmallCabinet',
            'type':'service',
            'taxes_id':False,
            'supplier_taxes_id':False,
            'sale_ok':False,
            'purchase_ok':False,
            'invoice_policy':'order',
            'default_code':'FREELARGECABINET',
            'categ_id':self.env.ref('product.product_category_all').id,
            'taxes_id':False,
        })

        ten_percent=self.env['product.product'].create({
            'name':'10.0%discountontotalamount',
            'type':'service',
            'taxes_id':False,
            'supplier_taxes_id':False,
            'sale_ok':False,
            'purchase_ok':False,
            'invoice_policy':'order',
            'default_code':'10PERCENTDISC',
            'categ_id':self.env.ref('product.product_category_all').id,
            'taxes_id':False,
        })

        self.env['coupon.program'].create({
            'name':"Buy3SmallCabinets,getoneforfree",
            'promo_code_usage':'no_code_needed',
            'discount_apply_on':'on_order',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':large_cabinet.id,
            'rule_min_quantity':3,
            'rule_products_domain':"[['name','ilike','SmallCabinet']]",
            'discount_line_product_id':free_large_cabinet.id
        })

        self.env['coupon.program'].create({
            'name':"Codefor10%onorders",
            'promo_code_usage':'code_needed',
            'promo_code':'testcode',
            'discount_apply_on':'on_order',
            'discount_type':'percentage',
            'discount_percentage':10.0,
            'program_type':'promotion_program',
            'discount_line_product_id':ten_percent.id
        })

        self.env.ref("website_sale.search_count_box").write({"active":True})
        self.start_tour("/",'shop_sale_coupon',login="admin")


@tagged('post_install','-at_install')
classTestWebsiteSaleCoupon(TransactionCase):

    defsetUp(self):
        super(TestWebsiteSaleCoupon,self).setUp()
        program=self.env['coupon.program'].create({
            'name':'10%TESTDiscount',
            'promo_code_usage':'code_needed',
            'discount_apply_on':'on_order',
            'discount_type':'percentage',
            'discount_percentage':10.0,
            'program_type':'coupon_program',
        })

        self.env['coupon.generate.wizard'].with_context(active_id=program.id).create({}).generate_coupon()
        self.coupon=program.coupon_ids[0]

        self.steve=self.env['res.partner'].create({
            'name':'SteveBucknor',
            'email':'steve.bucknor@example.com',
        })
        self.empty_order=self.env['sale.order'].create({
            'partner_id':self.steve.id
        })

    deftest_01_gc_coupon(self):
        #1.Simulateafrontendorder(website,product)
        order=self.empty_order
        order.website_id=self.env['website'].browse(1)
        self.env['sale.order.line'].create({
            'product_id':self.env['product.product'].create({
                'name':'ProductA',
                'list_price':100,
                'sale_ok':True,
            }).id,
            'name':'ProductA',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        #2.Applythecoupon
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':self.coupon.code
        }).process_coupon()
        order.recompute_coupon_lines()

        self.assertEqual(len(order.applied_coupon_ids),1,"Thecouponshould'vebeenappliedontheorder")
        self.assertEqual(self.coupon,order.applied_coupon_ids)
        self.assertEqual(self.coupon.state,'used')

        #3.Testrecentorder->Shouldnotberemoved
        order._gc_abandoned_coupons()

        self.assertEqual(len(order.applied_coupon_ids),1,"Thecouponshouldn'thavebeenremovedfromtheordernomorethan4days")
        self.assertEqual(self.coupon.state,'used',"Shouldnothavebeenchanged")

        #4.TestordernotolderthanICPvalidity->Shouldnotberemoved
        ICP=self.env['ir.config_parameter']
        icp_validity=ICP.create({'key':'website_sale_coupon.abandonned_coupon_validity','value':5})
        order.flush()
        query="""UPDATE%sSETwrite_date=%%sWHEREid=%%s"""%(order._table,)
        self.env.cr.execute(query,(fields.Datetime.to_string(fields.datetime.now()-timedelta(days=4,hours=2)),order.id))
        order._gc_abandoned_coupons()

        self.assertEqual(len(order.applied_coupon_ids),1,"Thecouponshouldn'thavebeenremovedfromtheordertheorderis4daysoldbuticpvalidityis5days")
        self.assertEqual(self.coupon.state,'used',"Shouldnothavebeenchanged(2)")

        #5.TestorderwithnoICPandolderthen4defaultdays->Shouldberemoved
        icp_validity.unlink()
        order._gc_abandoned_coupons()

        self.assertEqual(len(order.applied_coupon_ids),0,"Thecouponshould'vebeenremovedfromtheorderasmorethan4days")
        self.assertEqual(self.coupon.state,'new',"Shouldhavebeenreset.")
