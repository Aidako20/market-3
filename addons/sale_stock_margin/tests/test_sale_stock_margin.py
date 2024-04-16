#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields

fromflectra.tests.commonimportForm
fromflectra.addons.stock_account.tests.test_stockvaluationlayerimportTestStockValuationCommon


classTestSaleStockMargin(TestStockValuationCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestSaleStockMargin,cls).setUpClass()
        cls.pricelist=cls.env['product.pricelist'].create({'name':'SimplePricelist'})
        cls.env['res.currency.rate'].search([]).unlink()

    #########
    #UTILS#
    #########

    def_create_sale_order(self):
        returnself.env['sale.order'].create({
            'name':'Saleorder',
            'partner_id':self.env.ref('base.partner_admin').id,
            'partner_invoice_id':self.env.ref('base.partner_admin').id,
            'pricelist_id':self.pricelist.id,
        })

    def_create_sale_order_line(self,sale_order,product,quantity,price_unit=0):
        returnself.env['sale.order.line'].create({
            'name':'Saleorder',
            'order_id':sale_order.id,
            'price_unit':price_unit,
            'product_id':product.id,
            'product_uom_qty':quantity,
            'product_uom':self.env.ref('uom.product_uom_unit').id,
        })

    def_create_product(self):
        product_template=self.env['product.template'].create({
            'name':'Superproduct',
            'type':'product',
        })
        product_template.categ_id.property_cost_method='fifo'
        returnproduct_template.product_variant_ids

    #########
    #TESTS#
    #########

    deftest_sale_stock_margin_1(self):
        sale_order=self._create_sale_order()
        product=self._create_product()

        self._make_in_move(product,2,35)
        self._make_out_move(product,1)

        order_line=self._create_sale_order_line(sale_order,product,1,50)
        sale_order.action_confirm()

        self.assertEqual(order_line.purchase_price,35)
        self.assertEqual(sale_order.margin,15)

        sale_order.picking_ids.move_lines.quantity_done=1
        sale_order.picking_ids.button_validate()

        self.assertEqual(order_line.purchase_price,35)
        self.assertEqual(order_line.margin,15)
        self.assertEqual(sale_order.margin,15)

    deftest_sale_stock_margin_2(self):
        sale_order=self._create_sale_order()
        product=self._create_product()

        self._make_in_move(product,2,32)
        self._make_in_move(product,5,17)
        self._make_out_move(product,1)

        order_line=self._create_sale_order_line(sale_order,product,2,50)
        sale_order.action_confirm()

        self.assertEqual(order_line.purchase_price,32)
        self.assertAlmostEqual(sale_order.margin,36)

        sale_order.picking_ids.move_lines.quantity_done=2
        sale_order.picking_ids.button_validate()

        self.assertAlmostEqual(order_line.purchase_price,24.5)
        self.assertAlmostEqual(order_line.margin,51)
        self.assertAlmostEqual(sale_order.margin,51)

    deftest_sale_stock_margin_3(self):
        sale_order=self._create_sale_order()
        product=self._create_product()

        self._make_in_move(product,2,10)
        self._make_out_move(product,1)

        order_line=self._create_sale_order_line(sale_order,product,2,20)
        sale_order.action_confirm()

        self.assertEqual(order_line.purchase_price,10)
        self.assertAlmostEqual(sale_order.margin,20)

        sale_order.picking_ids.move_lines.quantity_done=1
        sale_order.picking_ids.button_validate()

        self.assertAlmostEqual(order_line.purchase_price,10)
        self.assertAlmostEqual(order_line.margin,20)
        self.assertAlmostEqual(sale_order.margin,20)

    deftest_sale_stock_margin_4(self):
        sale_order=self._create_sale_order()
        product=self._create_product()

        self._make_in_move(product,2,10)
        self._make_in_move(product,1,20)
        self._make_out_move(product,1)

        order_line=self._create_sale_order_line(sale_order,product,2,20)
        sale_order.action_confirm()

        self.assertEqual(order_line.purchase_price,10)
        self.assertAlmostEqual(sale_order.margin,20)

        sale_order.picking_ids.move_lines.quantity_done=1
        res=sale_order.picking_ids.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        self.assertAlmostEqual(order_line.purchase_price,15)
        self.assertAlmostEqual(order_line.margin,10)
        self.assertAlmostEqual(sale_order.margin,10)

    deftest_sale_stock_margin_5(self):
        sale_order=self._create_sale_order()
        product_1=self._create_product()
        product_2=self._create_product()

        self._make_in_move(product_1,2,35)
        self._make_in_move(product_1,1,51)
        self._make_out_move(product_1,1)

        self._make_in_move(product_2,2,17)
        self._make_in_move(product_2,1,11)
        self._make_out_move(product_2,1)

        order_line_1=self._create_sale_order_line(sale_order,product_1,2,60)
        order_line_2=self._create_sale_order_line(sale_order,product_2,4,20)
        sale_order.action_confirm()

        self.assertAlmostEqual(order_line_1.purchase_price,35)
        self.assertAlmostEqual(order_line_2.purchase_price,17)
        self.assertAlmostEqual(order_line_1.margin,25*2)
        self.assertAlmostEqual(order_line_2.margin,3*4)
        self.assertAlmostEqual(sale_order.margin,62)

        sale_order.picking_ids.move_lines[0].quantity_done=2
        sale_order.picking_ids.move_lines[1].quantity_done=3

        res=sale_order.picking_ids.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        self.assertAlmostEqual(order_line_1.purchase_price,43)      #(35+51)/2
        self.assertAlmostEqual(order_line_2.purchase_price,12.5)    #(17+11+11+11)/4
        self.assertAlmostEqual(order_line_1.margin,34)              #(60-43)*2
        self.assertAlmostEqual(order_line_2.margin,30)              #(20-12.5)*4
        self.assertAlmostEqual(sale_order.margin,64)

    deftest_sale_stock_margin_6(self):
        """Testthatthepurchasepricedoesn'tchangewhenthereisaserviceproductintheSO"""
        service=self.env['product.product'].create({
            'name':'Service',
            'type':'service',
            'list_price':100.0,
            'standard_price':50.0})
        self.product1.list_price=80.0
        self.product1.standard_price=40.0
        sale_order=self._create_sale_order()
        order_line_1=self._create_sale_order_line(sale_order,service,1,100)
        order_line_2=self._create_sale_order_line(sale_order,self.product1,1,80)

        self.assertEqual(order_line_1.purchase_price,50,"Salesorderlinecostshouldbe50.00")
        self.assertEqual(order_line_2.purchase_price,40,"Salesorderlinecostshouldbe40.00")

        self.assertEqual(order_line_1.margin,50,"Salesorderlineprofitshouldbe50.00")
        self.assertEqual(order_line_2.margin,40,"Salesorderlineprofitshouldbe40.00")
        self.assertEqual(sale_order.margin,90,"Salesorderprofitshouldbe90.00")

        #Changethepurchasepriceoftheserviceproduct.
        order_line_1.purchase_price=100.0
        self.assertEqual(order_line_1.purchase_price,100,"Salesorderlinecostshouldbe100.00")

        #Confirmthesalesorder.
        sale_order.action_confirm()

        self.assertEqual(order_line_1.purchase_price,100,"Salesorderlinecostshouldbe100.00")
        self.assertEqual(order_line_2.purchase_price,40,"Salesorderlinecostshouldbe40.00")

    deftest_so_and_multicurrency(self):
        ResCurrencyRate=self.env['res.currency.rate']
        company_currency=self.env.company.currency_id
        other_currency=self.env.ref('base.EUR')ifcompany_currency==self.env.ref('base.USD')elseself.env.ref('base.USD')

        date=fields.Date.today()
        ResCurrencyRate.create({'currency_id':company_currency.id,'rate':1,'name':date})
        other_currency_rate=ResCurrencyRate.search([('name','=',date),('currency_id','=',other_currency.id)])
        ifother_currency_rate:
            other_currency_rate.rate=2
        else:
            ResCurrencyRate.create({'currency_id':other_currency.id,'rate':2,'name':date})

        so=self._create_sale_order()
        so.pricelist_id=self.env['product.pricelist'].create({
            'name':'SuperPricelist',
            'currency_id':other_currency.id,
        })

        product=self._create_product()
        product.standard_price=100
        product.list_price=200

        so_form=Form(so)
        withso_form.order_line.new()asline:
            line.product_id=product
        so=so_form.save()
        so_line=so.order_line

        self.assertEqual(so_line.purchase_price,200)
        self.assertEqual(so_line.price_unit,400)
        so.action_confirm()
        self.assertEqual(so_line.purchase_price,200)
        self.assertEqual(so_line.price_unit,400)

    deftest_so_and_multicompany(self):
        """Inamulticompanyenvironnement,whentheuserisoncompanyC01andconfirmsaSOthat
        belongstoasecondcompanyC02,thistestensuresthatthecomputationswillbebasedon
        C02'sdata"""
        main_company=self.env['res.company']._get_main_company()
        main_company_currency=main_company.currency_id
        new_company_currency=self.env.ref('base.EUR')ifmain_company_currency==self.env.ref('base.USD')elseself.env.ref('base.USD')

        date=fields.Date.today()
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create([
            {'currency_id':main_company_currency.id,'rate':1,'name':date,'company_id':False},
            {'currency_id':new_company_currency.id,'rate':3,'name':date,'company_id':False},
        ])

        new_company=self.env['res.company'].create({
            'name':'SuperCompany',
            'currency_id':new_company_currency.id,
        })
        self.env.user.company_id=new_company.id

        self.pricelist.currency_id=new_company_currency.id

        product=self._create_product()

        incoming_picking_type=self.env['stock.picking.type'].search([('company_id','=',new_company.id),('code','=','incoming')])
        production_location=self.env['stock.location'].search([('company_id','=',new_company.id),('usage','=','production')])

        picking=self.env['stock.picking'].create({
            'picking_type_id':incoming_picking_type.id,
            'location_id':production_location.id,
            'location_dest_id':incoming_picking_type.default_location_dest_id.id,
        })
        self.env['stock.move'].create({
            'name':'IncomingProduct',
            'product_id':product.id,
            'location_id':production_location.id,
            'location_dest_id':incoming_picking_type.default_location_dest_id.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':100,
            'picking_type_id':incoming_picking_type.id,
            'picking_id':picking.id,
        })
        picking.action_confirm()
        res_dict=picking.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process()

        self.pricelist.currency_id=new_company_currency.id
        partner=self.env['res.partner'].create({'name':'SuperPartner'})
        so=self.env['sale.order'].create({
            'name':'Saleorder',
            'partner_id':partner.id,
            'partner_invoice_id':partner.id,
            'pricelist_id':self.pricelist.id,
        })
        sol=self._create_sale_order_line(so,product,1,price_unit=200)

        self.env.user.company_id=main_company.id
        so.action_confirm()

        self.assertEqual(sol.purchase_price,100)
        self.assertEqual(sol.margin,100)
