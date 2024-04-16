#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimporttagged,Form

importtime


@tagged('-at_install','post_install')
classTestAveragePrice(ValuationReconciliationTestCommon):

    deftest_00_average_price(self):
        """Testcaseforaveragepricecomputation"""

        res_partner_3=self.env['res.partner'].create({
            'name':'GeminiPartner',
        })

        #Setaproductasusingaverageprice.
        product_cable_management_box=self.env['product.product'].create({
            'default_code':'AVG',
            'name':'AverageIceCream',
            'type':'product',
            'categ_id':self.stock_account_product_categ.id,
            'list_price':100.0,
            'standard_price':60.0,
            'uom_id':self.env.ref('uom.product_uom_kgm').id,
            'uom_po_id':self.env.ref('uom.product_uom_kgm').id,
            'supplier_taxes_id':[],
            'description':'FIFOIceCream',
        })
        product_cable_management_box.categ_id.property_cost_method='average'

        #IcreateadraftPurchaseOrderforfirstincomingshipmentfor10piecesat60€
        purchase_order_1=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':'AverageIceCream',
                'product_id':product_cable_management_box.id,
                'product_qty':10.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':60.0,
                'date_planned':time.strftime('%Y-%m-%d'),
            })]
        })

        #Confirmthefirstpurchaseorder
        purchase_order_1.button_confirm()

        #Checkthe"Approved"statusofpurchaseorder1
        self.assertEqual(purchase_order_1.state,'purchase',"Wrongstateofpurchaseorder!")

        #Processthereceptionofpurchaseorder1
        picking=purchase_order_1.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checktheaverage_priceoftheproduct(averageicecream).
        self.assertEqual(product_cable_management_box.qty_available,10.0,'Wrongquantityinstockafterfirstreception')
        self.assertEqual(product_cable_management_box.standard_price,60.0,'Standardpriceshouldbethepriceofthefirstreception!')

        #IcreateadraftPurchaseOrderforsecondincomingshipmentfor30piecesat80€
        purchase_order_2=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_cable_management_box.id,
                'product_qty':30.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':80.0,
                'date_planned':time.strftime('%Y-%m-%d'),
            })]
        })

        #Confirmthesecondpurchaseorder
        purchase_order_2.button_confirm()
        #Processthereceptionofpurchaseorder2
        picking=purchase_order_2.picking_ids[0]
        res=picking.button_validate()
        Form(self.env['stock.immediate.transfer'].with_context(res['context'])).save().process()

        #Checkthestandardprice
        self.assertEqual(product_cable_management_box.standard_price,75.0,'Aftersecondreception,weshouldhaveanaveragepriceof75.0ontheproduct')

        #Createpickingtosendsomegoods
        outgoing_shipment=self.env['stock.picking'].create({
            'picking_type_id':self.company_data['default_warehouse'].out_type_id.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'move_lines':[(0,0,{
                'name':'outgoing_shipment_avg_move',
                'product_id':product_cable_management_box.id,
                'product_uom_qty':20.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'location_id': self.company_data['default_warehouse'].lot_stock_id.id,
                'location_dest_id':self.env.ref('stock.stock_location_customers').id})]
            })

        #Assignthisoutgoingshipmentandprocessthedelivery
        outgoing_shipment.action_assign()
        res=outgoing_shipment.button_validate()
        Form(self.env['stock.immediate.transfer'].with_context(res['context'])).save().process()

        #Checktheaverageprice(60*10+30*80)/40=75.0€didnotchange
        self.assertEqual(product_cable_management_box.standard_price,75.0,'Averagepriceshouldnothavechangedwithoutgoingpicking!')
        self.assertEqual(product_cable_management_box.qty_available,20.0,'Pieceswerenotpickedcorrectlyasthequantityonhandiswrong')

        #Makeanewpurchaseorderwith500gAverageIceCreamatapriceof0.2€/g
        purchase_order_3=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':product_cable_management_box.name,
                'product_id':product_cable_management_box.id,
                'product_qty':500.0,
                'product_uom':self.ref('uom.product_uom_gram'),
                'price_unit':0.2,
                'date_planned':time.strftime('%Y-%m-%d'),
            })]
        })

        #Confirmthefirstpurchaseorder
        purchase_order_3.button_confirm()
        #Processthereceptionofpurchaseorder3ingrams

        picking=purchase_order_3.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkpriceis(75.0*20+200*0.5)/20.5=78.04878€
        self.assertEqual(product_cable_management_box.qty_available,20.5,'Receptionofpurchaseorderingramsleadstowrongquantityinstock')
        self.assertEqual(round(product_cable_management_box.standard_price,2),78.05,
            'StandardpriceasaveragepriceofthirdreceptionwithotherUoMincorrect!Got%sinsteadof78.05'%(round(product_cable_management_box.standard_price,2)))
