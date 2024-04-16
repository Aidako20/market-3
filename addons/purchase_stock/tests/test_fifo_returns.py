#-*-coding:utf-8-*-

importtime

fromflectra.testsimporttagged,Form
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon


@tagged('-at_install','post_install')
classTestFifoReturns(ValuationReconciliationTestCommon):

    deftest_fifo_returns(self):
        """TesttocreateproductandpurchaseordertotesttheFIFOreturnsoftheproduct"""
        res_partner_3=self.env['res.partner'].create({
            'name':'GeminiPartner',
        })

        #Setaproductasusingfifoprice
        product_fiforet_icecream=self.env['product.product'].create({
            'default_code':'FIFORET',
            'name':'FIFOIceCream',
            'type':'product',
            'categ_id':self.stock_account_product_categ.id,
            'standard_price':0.0,
            'uom_id':self.env.ref('uom.product_uom_kgm').id,
            'uom_po_id':self.env.ref('uom.product_uom_kgm').id,
            'description':'FIFOIceCream',
        })

        #IcreateadraftPurchaseOrderforfirstinmovefor10kgat50euro
        purchase_order_1=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':'FIFOIceCream',
                'product_id':product_fiforet_icecream.id,
                'product_qty':10.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':50.0,
                'date_planned':time.strftime('%Y-%m-%d'),
            })],
        })

        #CreateadraftPurchaseOrderforsecondshipmentfor30kgat80€/kg
        purchase_order_2=self.env['purchase.order'].create({
            'partner_id':res_partner_3.id,
            'order_line':[(0,0,{
                'name':'FIFOIceCream',
                'product_id':product_fiforet_icecream.id,
                'product_qty':30.0,
                'product_uom':self.env.ref('uom.product_uom_kgm').id,
                'price_unit':80.0,
                'date_planned':time.strftime('%Y-%m-%d'),
            })],
        })

        #Confirmthefirstpurchaseorder
        purchase_order_1.button_confirm()

        #Processthereceptionofpurchaseorder1
        picking=purchase_order_1.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkthestandardpriceoftheproduct(fifoicecream)
        self.assertAlmostEqual(product_fiforet_icecream.standard_price,50)

        #Confirmthesecondpurchaseorder
        purchase_order_2.button_confirm()
        picking=purchase_order_2.picking_ids[0]
        res=picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Returnthegoodsofpurchaseorder2
        picking=purchase_order_2.picking_ids[0]
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids,active_id=picking.ids[0],
            active_model='stock.picking'))
        return_pick_wiz=stock_return_picking_form.save()
        return_picking_id,dummy=return_pick_wiz.with_context(active_id=picking.id)._create_returns()

        #Importanttopassthroughconfirmationandassignation
        return_picking=self.env['stock.picking'].browse(return_picking_id)
        return_picking.action_confirm()
        return_picking.move_lines[0].quantity_done=return_picking.move_lines[0].product_uom_qty
        return_picking._action_done()

        # Afterthereturnonly10ofthesecondpurchaseordershouldstillbeinstockasitappliesfifoonthereturntoo
        self.assertEqual(product_fiforet_icecream.qty_available,10.0,'Qtyavailableshouldbe10.0')
        self.assertEqual(product_fiforet_icecream.value_svl,800.0,'Stockvalueshouldbe800')
