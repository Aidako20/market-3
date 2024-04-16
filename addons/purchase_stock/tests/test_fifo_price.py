#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimporttagged,Form

importtime


@tagged('-at_install','post_install')
classTestFifoPrice(ValuationReconciliationTestCommon):

    deftest_00_test_fifo(self):
        """Testproductcostpricewithfiforemovalstrategy."""

        res_partner_3=self.env['res.partner'].create({
            'name':'GeminiPartner',
        })

        #Setaproductasusingfifoprice
        product_cable_management_box=self.env['product.product'].create({
            'default_code':'FIFO',
            'name':'FIFOIceCream',
            'type':'product',
            'categ_id':self.stock_account_product_categ.id,
            'list_price':100.0,
            'standard_price':70.0,
            'uom_id':self.env.ref('uom.product_uom_kgm').id,
            'uom_po_id':self.env.ref('uom.product_uom_kgm').id,
            'supplier_taxes_id':[],
            'description':'FIFOIceCream',
        })

        #IcreateadraftPurchaseOrderforfirstinmovefor10kgat50euro
        purchase_order_1=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':'FIFOIceCream',
                'product_id':product_cable_management_box.id,
                'product_qty':10.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':50.0,
                'date_planned':time.strftime('%Y-%m-%d')})],
        })

        #Confirmthefirstpurchaseorder
        purchase_order_1.button_confirm()

        #Checkthe"Purchase"statusofpurchaseorder1
        self.assertEqual(purchase_order_1.state,'purchase')

        #Processthereceptionofpurchaseorder1andsetdate
        picking=purchase_order_1.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkthestandardpriceoftheproduct(fifoicecream),thatshouldhavechanged
        #becausetheunitcostofthepurchaseorderis50
        self.assertAlmostEqual(product_cable_management_box.standard_price,50.0)
        self.assertEqual(product_cable_management_box.value_svl,500.0,'Wrongstockvalue')

        #IcreateadraftPurchaseOrderforsecondshipmentfor30kgat80euro
        purchase_order_2=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':'FIFOIceCream',
                'product_id':product_cable_management_box.id,
                'product_qty':30.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':80.0,
                'date_planned':time.strftime('%Y-%m-%d')})],
            })

        #Confirmthesecondpurchaseorder
        purchase_order_2.button_confirm()

        #Processthereceptionofpurchaseorder2
        picking=purchase_order_2.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkthestandardpriceoftheproduct,thatshouldhavenotchangedbecausewe
        #stillhaveicecreaminstock
        self.assertEqual(product_cable_management_box.standard_price,50.0,'Standardpriceasfifopriceofsecondreceptionincorrect!')
        self.assertEqual(product_cable_management_box.value_svl,2900.0,'Stockvaluationshouldbe2900')

        #Letussendsomegoods
        outgoing_shipment=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_cable_management_box.id,
                'product_uom_qty':20.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'picking_type_id':self.company_data['default_warehouse'].out_type_id.id})]
            })

        #Iassignthisoutgoingshipment
        outgoing_shipment.action_assign()

        #Processthedeliveryoftheoutgoingshipment
        res=outgoing_shipment.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkstockvaluebecame1600.
        self.assertEqual(product_cable_management_box.value_svl,1600.0,'Stockvaluationshouldbe1600')

        #Doadeliveryofanextra500g(deliveryorder)
        outgoing_shipment_uom=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_cable_management_box.id,
                'product_uom_qty':500.0,
                'product_uom':self.env.ref('uom.product_uom_gram').id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'picking_type_id':self.company_data['default_warehouse'].out_type_id.id})]
            })

        #Iassignthisoutgoingshipment
        outgoing_shipment_uom.action_assign()

        #Processthedeliveryoftheoutgoingshipment
        res=outgoing_shipment_uom.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkstockvaluationandqtyinstock
        self.assertEqual(product_cable_management_box.value_svl,1560.0,'Stockvaluationshouldbe1560')
        self.assertEqual(product_cable_management_box.qty_available,19.5,'Shouldstillhave19.5instock')

        #WewilltemporarilychangethecurrencyrateonthesixthofJunetohavethesameresultsallyear
        NewUSD=self.env['res.currency'].create({
            'name':'new_usd',
            'symbol':'$²',
            'rate_ids':[(0,0,{'rate':1.2834,'name':time.strftime('%Y-%m-%d')})],
        })

        #CreatePOfor30000gat0.150$/gand10kgat150$/kg
        purchase_order_usd=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'currency_id':NewUSD.id,
            'order_line':[(0,0,{
                    'name':'FIFOIceCream',
                    'product_id':product_cable_management_box.id,
                    'product_qty':30,
                    'product_uom':self.env.ref('uom.product_uom_kgm').id,
                    'price_unit':0.150,
                    'date_planned':time.strftime('%Y-%m-%d')}),
                (0,0,{
                    'name':product_cable_management_box.name,
                    'product_id':product_cable_management_box.id,
                    'product_qty':10.0,
                    'product_uom':self.env.ref('uom.product_uom_kgm').id,
                    'price_unit':150.0,
                    'date_planned':time.strftime('%Y-%m-%d')})]
                })

        #ConfirmthepurchaseorderinUSD
        purchase_order_usd.button_confirm()
        #ProcessthereceptionofpurchaseorderwithUSD
        picking=purchase_order_usd.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Createdeliveryorderof49.5kg
        outgoing_shipment_cur=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_cable_management_box.id,
                'product_uom_qty':49.5,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'picking_type_id':self.company_data['default_warehouse'].out_type_id.id})]
        })

        #Iassignthisoutgoingshipment
        outgoing_shipment_cur.action_assign()

        #Processthedeliveryoftheoutgoingshipment
        res=outgoing_shipment_cur.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Doadeliveryofanextra10kg
        outgoing_shipment_ret=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_cable_management_box.id,
                'product_uom_qty':10,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'picking_type_id':self.company_data['default_warehouse'].out_type_id.id})]
            })

        #Iassignthisoutgoingshipment
        outgoing_shipment_ret.action_assign()
        res=outgoing_shipment_ret.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkroundedpriceis150.0/1.2834
        self.assertEqual(round(product_cable_management_box.qty_available),0.0,'Wrongquantityinstockafterfirstreception.')

        #Letuscreatesomeoutstogetnegativestockforanewproductusingthesameconfig
        product_fifo_negative=self.env['product.product'].create({
            'default_code':'NEG',
            'name':'FIFONegative',
            'type':'product',
            'categ_id':self.stock_account_product_categ.id,
            'list_price':100.0,
            'standard_price':70.0,
            'uom_id':self.env.ref('uom.product_uom_kgm').id,
            'uom_po_id':self.env.ref('uom.product_uom_kgm').id,
            'supplier_taxes_id':[],
            'description':'FIFOIceCream',
        })

        #Createoutpicking.createdeliveryorderof100kg.
        outgoing_shipment_neg=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':product_fifo_negative.name,
                'product_id':product_fifo_negative.id,
                'product_uom_qty':100,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'picking_type_id':self.company_data['default_warehouse'].out_type_id.id})]
        })

        #Processthedeliveryofthefirstoutgoingshipment
        outgoing_shipment_neg.action_confirm()
        outgoing_shipment_neg.move_lines[0].quantity_done=100.0
        outgoing_shipment_neg._action_done()

        #Checkqtyavailable=-100
        self.assertEqual(product_fifo_negative.qty_available,-100,'Stockqtyshouldbe-100')

        #Thebehavioroffifo/lifoisnotgaranteeifthequantsarecreatedatthesamesecond,sojustwaitonesecond
        time.sleep(1)

        #Letcreateanotheroutshipmentof400kg
        outgoing_shipment_neg2=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':product_fifo_negative.name,
                'product_id':product_fifo_negative.id,
                'product_uom_qty':400,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'picking_type_id':self.company_data['default_warehouse'].out_type_id.id})]
        })

        #Processthedeliveryoftheoutgoingshipments
        outgoing_shipment_neg2.action_confirm()
        outgoing_shipment_neg2.move_lines[0].quantity_done=400.0
        outgoing_shipment_neg2._action_done()

        #Checkqtyavailable=-500
        self.assertEqual(product_fifo_negative.qty_available,-500,'Stockqtyshouldbe-500')

        #Receivepurchaseorderwith50kgIceCreamat50€/kg
        purchase_order_neg=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':'FIFOIceCream',
                'product_id':product_fifo_negative.id,
                'product_qty':50.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':50.0,
                'date_planned':time.strftime('%Y-%m-%d')})],
        })

        #Iconfirmthefirstpurchaseorder
        purchase_order_neg.button_confirm()

        #Processthereceptionofpurchaseorderneg
        picking=purchase_order_neg.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Receivepurchaseorderwith600kgFIFOIceCreamat80euro/kg
        purchase_order_neg2=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_fifo_negative.id,
                'product_qty':600.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':80.0,
                'date_planned':time.strftime('%Y-%m-%d')})],
        })

        #Iconfirmthesecondnegativepurchaseorder
        purchase_order_neg2.button_confirm()

        #Processthereceptionofpurchaseorderneg2
        picking=purchase_order_neg2.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        original_out_move=outgoing_shipment_neg.move_lines[0]
        self.assertEqual(original_out_move.product_id.value_svl, 12000.0,'Valueofthemoveshouldbe12000')
        self.assertEqual(original_out_move.product_id.qty_available,150.0,'Qtyavailableshouldbe150')

    deftest_01_test_fifo(self):
        """"Thistestensuresthatunitpricekeepsitsdecimalprecision"""

        unit_price_precision=self.env['ir.model.data'].xmlid_to_object('product.decimal_price')
        unit_price_precision.digits=3

        tax=self.env["account.tax"].create({
            "name":"DummyTax",
            "amount":"0.00",
            "type_tax_use":"purchase",
        })

        super_product=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'product',
            'categ_id':self.stock_account_product_categ.id,
            'standard_price':0.035,
        })
        self.assertEqual(super_product.cost_method,'fifo')
        self.assertEqual(super_product.valuation,'real_time')

        purchase_order=self.env['purchase.order'].create({
            'partner_id':self.env.ref('base.res_partner_3').id,
            'order_line':[(0,0,{
                'name':super_product.name,
                'product_id':super_product.id,
                'product_qty':1000,
                'product_uom':super_product.uom_id.id,
                'price_unit':super_product.standard_price,
                'date_planned':time.strftime('%Y-%m-%d'),
                'taxes_id':[(4,tax.id)],
            })],
        })

        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state,'purchase')

        picking=purchase_order.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        self.assertEqual(super_product.standard_price,0.035)
        self.assertEqual(super_product.value_svl,35.0)
        self.assertEqual(picking.move_lines.price_unit,0.035)
