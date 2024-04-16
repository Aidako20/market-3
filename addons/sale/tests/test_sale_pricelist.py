#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

from.commonimportTestSaleCommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportForm


@tagged('post_install','-at_install')
classTestSaleOrder(TestSaleCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        Pricelist=cls.env['product.pricelist']
        PricelistItem=cls.env['product.pricelist.item']
        SaleOrder=cls.env['sale.order'].with_context(tracking_disable=True)
        SaleOrderLine=cls.env['sale.order.line'].with_context(tracking_disable=True)

        #Createaproductcategory
        cls.product_category_1=cls.env['product.category'].create({
            'name':'ProductCategoryforpricelist',
        })
        #Createapricelistwithdiscountpolicy:percentageonservices,fixedpriceforproduct_order
        cls.pricelist_discount_incl=Pricelist.create({
            'name':'PricelistA',
            'discount_policy':'with_discount',
            'company_id':cls.company_data['company'].id,
        })
        PricelistItem.create({
            'pricelist_id':cls.pricelist_discount_incl.id,
            'applied_on':'1_product',
            'product_tmpl_id':cls.company_data['product_service_order'].product_tmpl_id.id,
            'compute_price':'percentage',
            'percent_price':10
        })
        PricelistItem.create({
            'pricelist_id':cls.pricelist_discount_incl.id,
            'applied_on':'1_product',
            'product_tmpl_id':cls.company_data['product_service_delivery'].product_tmpl_id.id,
            'compute_price':'percentage',
            'percent_price':20,
        })
        cls.pricelist_discount_incl_item3=PricelistItem.create({
            'pricelist_id':cls.pricelist_discount_incl.id,
            'applied_on':'1_product',
            'product_tmpl_id':cls.company_data['product_order_no'].product_tmpl_id.id,
            'compute_price':'fixed',
            'fixed_price':211,
        })

        #Createapricelistwithoutdiscountpolicy:formulaforproduct_category_1category,percentageforservice_order
        cls.pricelist_discount_excl=Pricelist.create({
            'name':'PricelistB',
            'discount_policy':'without_discount',
            'company_id':cls.company_data['company'].id,
        })
        PricelistItem.create({
            'pricelist_id':cls.pricelist_discount_excl.id,
            'applied_on':'2_product_category',
            'categ_id':cls.product_category_1.id,
            'compute_price':'formula',
            'base':'standard_price',
            'price_discount':10,
        })
        PricelistItem.create({
            'pricelist_id':cls.pricelist_discount_excl.id,
            'applied_on':'1_product',
            'product_tmpl_id':cls.company_data['product_service_order'].product_tmpl_id.id,
            'compute_price':'percentage',
            'percent_price':20,
        })

        #Createapricelistwithoutdiscountpolicy:percentageonallproducts
        cls.pricelist_discount_excl_global=cls.env['product.pricelist'].create({
            'name':'PricelistC',
            'discount_policy':'without_discount',
            'company_id':cls.env.company.id,
            'item_ids':[(0,0,{
                'applied_on':'3_global',
                'compute_price':'percentage',
                'percent_price':54,
            })],
        })

        #createagenericSaleOrderwithallclassicalproductsandemptypricelist
        cls.sale_order=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })
        cls.sol_product_order=SaleOrderLine.create({
            'name':cls.company_data['product_order_no'].name,
            'product_id':cls.company_data['product_order_no'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_order_no'].uom_id.id,
            'price_unit':cls.company_data['product_order_no'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_serv_deliver=SaleOrderLine.create({
            'name':cls.company_data['product_service_delivery'].name,
            'product_id':cls.company_data['product_service_delivery'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_service_delivery'].uom_id.id,
            'price_unit':cls.company_data['product_service_delivery'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_serv_order=SaleOrderLine.create({
            'name':cls.company_data['product_service_order'].name,
            'product_id':cls.company_data['product_service_order'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_service_order'].uom_id.id,
            'price_unit':cls.company_data['product_service_order'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_prod_deliver=SaleOrderLine.create({
            'name':cls.company_data['product_delivery_no'].name,
            'product_id':cls.company_data['product_delivery_no'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_delivery_no'].uom_id.id,
            'price_unit':cls.company_data['product_delivery_no'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })

    deftest_sale_with_pricelist_discount_included(self):
        """TestSOwiththepricelistandcheckunitpriceappearedonitslines"""
        #Changethepricelist
        self.sale_order.write({'pricelist_id':self.pricelist_discount_incl.id})
        #Triggeronchangetoresetdiscount,unitprice,subtotal,...
        forlineinself.sale_order.order_line:
            line.product_id_change()
            line._onchange_discount()
        #CheckthatpricelistoftheSOhasbeenappliedonthesaleorderlinesornot
        forlineinself.sale_order.order_line:
            ifline.product_id==self.company_data['product_order_no']:
                self.assertEqual(line.price_unit,self.pricelist_discount_incl_item3.fixed_price,'Priceofproduct_ordershouldbe%sappliedontheorderline'%(self.pricelist_discount_incl_item3.fixed_price,))
            else: #onlyservices(service_orderandservice_deliver)
                foriteminself.sale_order.pricelist_id.item_ids.filtered(lambdal:l.product_tmpl_id==line.product_id.product_tmpl_id):
                    price=item.percent_price
                    self.assertEqual(price,(line.product_id.list_price-line.price_unit)/line.product_id.list_price*100,'PricelistoftheSOshouldbeappliedonanorderline%s'%(line.product_id.name,))

    deftest_sale_with_pricelist_discount_excluded(self):
        """TestSOwiththepricelist'discountdisplayed'andcheckdiscountandunitpriceappearedonitslines"""
        #Addgroup'DiscountonLines'totheuser
        self.env.user.write({'groups_id':[(4,self.env.ref('product.group_discount_per_so_line').id)]})

        #Setproductcategoryonconsumableproducts(forthepricelistitemapplyingonthiscategory)
        self.company_data['product_order_no'].write({'categ_id':self.product_category_1.id})
        self.company_data['product_delivery_no'].write({'categ_id':self.product_category_1.id})

        #Changethepricelist
        self.sale_order.write({'pricelist_id':self.pricelist_discount_excl.id})
        #Triggeronchangetoresetdiscount,unitprice,subtotal,...
        forlineinself.sale_order.order_line:
            line.product_id_change()
            line._onchange_discount()

        #CheckpricelistoftheSOapplyornotonorderlineswherepricelistcontainsformulathatadd15%onthecostprice
        forlineinself.sale_order.order_line:
            ifline.product_id.categ_idinself.sale_order.pricelist_id.item_ids.mapped('categ_id'): #reductionpercategory(consummableonly)
                foriteminself.sale_order.pricelist_id.item_ids.filtered(lambdal:l.categ_id==line.product_id.categ_id):
                    self.assertEqual(line.discount,item.price_discount,"Discountshouldbedisplayedonorderline%ssinceitscategorygetsomediscount"%(line.name,))
                self.assertEqual(line.price_unit,line.product_id.standard_price,"Priceunitshouldbethecostpriceforproduct%s"%(line.name,))
            else:
                ifline.product_id==self.company_data['product_service_order']: #reductionforthisproduct
                    self.assertEqual(line.discount,20.0,"Discountforproduct%sshouldbe20percentwithpricelist%s"%(line.name,self.pricelist_discount_excl.name))
                    self.assertEqual(line.price_unit,line.product_id.list_price,'Unitpriceoforderlineshouldbeasalepriceasthepricelistnotappliedontheothercategory\'sproduct')
                else: #nodiscountfortherest
                    self.assertEqual(line.discount,0.0,'PricelistofSOshouldnotbeappliedonanorderline')
                    self.assertEqual(line.price_unit,line.product_id.list_price,'Unitpriceoforderlineshouldbeasalepriceasthepricelistnotappliedontheothercategory\'sproduct')

    deftest_sale_change_of_pricelists_excluded_value_discount(self):
        """TestSOwiththepricelist'discountdisplayed'andcheckdisplayedpercentagevalueaftermultiplechangesofpricelist"""
        self.env.user.write({'groups_id':[(4,self.env.ref('product.group_discount_per_so_line').id)]})

        #Createaproductwithaverylowprice
        amazing_product=self.env['product.product'].create({
            'name':'AmazingProduct',
            'lst_price':0.03,
        })

        #createasimpleSaleOrderwithauniqueline
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
            'order_line':[(0,0,{
                'name':amazing_product.name,
                'product_id':amazing_product.id,
                'product_uom_qty':1,
                'product_uom':amazing_product.uom_id.id,
                'price_unit':0.03,
                'tax_id':False,
            })],
        })

        #Changethepricelist
        sale_order.write({'pricelist_id':self.pricelist_discount_excl_global.id})
        #UpdatePrices
        sale_order.update_prices()

        #Checkthatthediscountdisplayedisthecorrectone
        self.assertEqual(
            sale_order.order_line.discount,54,
            "Wrongdiscountcomputedforspecifiedproduct&pricelist"
        )
        #Additionaltocheckforoverallconsistency
        self.assertEqual(
            sale_order.order_line.price_unit,0.03,
            "Wrongunitpricecomputedforspecifiedproduct&pricelist"
        )
        self.assertEqual(
            sale_order.order_line.price_subtotal,0.01,
            "Wrongsubtotalpricecomputedforspecifiedproduct&pricelist"
        )
        self.assertFalse(
            sale_order.order_line.tax_id,
            "Wrongtaxappliedforspecifiedproduct&pricelist"
        )

    deftest_sale_change_of_pricelists_excluded_value_discount_on_tax_included_price_mapped_to_tax_excluded_price(self):
        self.env.user.write({'groups_id':[(4,self.env.ref('product.group_discount_per_so_line').id)]})

        #settingupthetaxes:
        tax_a=self.tax_sale_a.copy()
        tax_b=self.tax_sale_a.copy()
        tax_a.price_include=True
        tax_b.amount=6

        #settingupfiscalposition:
        fiscal_pos=self.fiscal_pos_a.copy()
        fiscal_pos.auto_apply=True
        country=self.env["res.country"].search([('name','=','Belgium')],limit=1)
        fiscal_pos.country_id=country
        fiscal_pos.tax_ids=[
            (0,None,
             {
                 'tax_src_id':tax_a.id,
                 'tax_dest_id':tax_b.id
             })
        ]

        #settinguppartner:
        self.partner_a.country_id=country

        #creatingproduct:

        my_product=self.env['product.product'].create({
            'name':'myProduct',
            'lst_price':115,
            'taxes_id':[tax_a.id]
        })

        #creatingSO

        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
            'order_line':[(0,0,{
                'name':my_product.name,
                'product_id':my_product.id,
                'product_uom_qty':1,
                'product_uom':my_product.uom_id.id,
            })],
        })

        #Applyfiscalposition

        sale_order.fiscal_position_id=fiscal_pos.id
        #Changethepricelist
        sale_order.write({'pricelist_id':self.pricelist_discount_excl_global.id})
        #UpdatePrices
        sale_order.update_prices()


        #Checkthatthediscountdisplayedisthecorrectone
        self.assertEqual(
            sale_order.order_line.discount,54,
            "Wrongdiscountcomputedforspecifiedproduct&pricelist"
        )
        #Additionaltocheckforoverallconsistency
        self.assertEqual(
            sale_order.order_line.price_unit,100,
            "Wrongunitpricecomputedforspecifiedproduct&pricelist"
        )
        self.assertEqual(
            sale_order.order_line.price_subtotal,46,
            "Wrongsubtotalpricecomputedforspecifiedproduct&pricelist"
        )
        self.assertEqual(
            sale_order.order_line.tax_id.id,tax_b.id,
            "Wrongtaxappliedforspecifiedproduct&pricelist"
        )

    deftest_sale_with_pricelist_discount_excluded_2(self):
        """TestSOwiththepricelist'discountdisplayed'andcheckdiscountandunitpriceappearedonitslines
        Whenproductareaddedafterpricelistandtheonchangeshouldbetriggerautomatically.
        """
        #Addgroup'DiscountonLines'totheuser
        self.env.user.write({'groups_id':[(4,self.env.ref('product.group_discount_per_so_line').id)]})

        product_order=self.company_data['product_order_no']
        service_order=self.company_data['product_service_order']

        #Setproductcategoryonconsumableproducts(forthepricelistitemapplyingonthiscategory)
        product_order.write({'categ_id':self.product_category_1.id})

        #RemovecurrentSOlines
        self.sale_order.write({'order_line':[(5,)]})

        #Changethepricelist
        self.sale_order.write({'pricelist_id':self.pricelist_discount_excl.id})
        self.env['sale.order.line'].create({
            'order_id':self.sale_order.id,
            'name':'Dummy1',
            'product_id':1,
        })

        withForm(self.sale_order)asso_form:
            sol_form=so_form.order_line.edit(0)
            sol_form.product_id=service_order

            self.assertEqual(sol_form.product_id,service_order)
            self.assertEqual(sol_form.price_unit,service_order.list_price,
                             "Unitpriceoforderlineshouldbeasalepriceasthepricelistnotappliedontheothercategory\'sproduct")
            self.assertEqual(sol_form.discount,20,
                             "Discountshouldbedisplayedonorderlinesincetheproductgetsomediscount")

            sol_form.product_id=product_order
            self.assertEqual(sol_form.product_id,product_order)
            self.assertEqual(sol_form.price_unit,product_order.standard_price,
                             "Priceunitshouldbethecostpriceforproduct")
            self.assertEqual(sol_form.discount,10,
                             "Discountshouldbedisplayedonorderlinesinceitscategorygetsomediscount")
