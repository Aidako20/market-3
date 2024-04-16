#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,tools
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimporttagged,common,Form


@tagged('-at_install','post_install')
classTestLifoPrice(ValuationReconciliationTestCommon):

    deftest_lifoprice(self):

        #SetproductcategoryremovalstrategyasLIFO
        product_category_001=self.env['product.category'].create({
            'name':'LifoCategory',
            'removal_strategy_id':self.env.ref('stock.removal_lifo').id,
            'property_valuation':'real_time',
            'property_cost_method':'fifo',
        })
        res_partner_3=self.env['res.partner'].create({'name':'MyTestPartner'})
        self.company_data['default_warehouse'].out_type_id.show_operations=False

        #Setaproductasusinglifoprice
        product_form=Form(self.env['product.product'])
        product_form.default_code='LIFO'
        product_form.name='LIFOIceCream'
        product_form.type='product'
        product_form.categ_id=product_category_001
        product_form.lst_price=100.0
        product_form.uom_id=self.env.ref('uom.product_uom_kgm')
        product_form.uom_po_id=self.env.ref('uom.product_uom_kgm')
        #thesearenotavailable(visible)ineitherproductorvariant
        #forviews,apparentlyfromtheUIyoucanonlysettheproduct
        #category(orhand-assigntheproperty_*versionwhichseems...)
        #product_form.categ_id.valuation='real_time'
        #product_form.categ_id.property_cost_method='fifo'
        product_form.categ_id.property_stock_account_input_categ_id=self.company_data['default_account_stock_in']
        product_form.categ_id.property_stock_account_output_categ_id=self.company_data['default_account_stock_out']
        product_lifo_icecream=product_form.save()

        product_lifo_icecream.standard_price=70.0

        #IcreateadraftPurchaseOrderforfirstinmovefor10piecesat60euro
        order_form=Form(self.env['purchase.order'])
        order_form.partner_id=res_partner_3
        withorder_form.order_line.new()asline:
            line.product_id=product_lifo_icecream
            line.product_qty=10.0
            line.price_unit=60.0
        purchase_order_lifo1=order_form.save()

        #IcreateadraftPurchaseOrderforsecondshipmentfor30piecesat80euro
        order2_form=Form(self.env['purchase.order'])
        order2_form.partner_id=res_partner_3
        withorder2_form.order_line.new()asline:
            line.product_id=product_lifo_icecream
            line.product_qty=30.0
            line.price_unit=80.0
        purchase_order_lifo2=order2_form.save()

        #Iconfirmthefirstpurchaseorder
        purchase_order_lifo1.button_confirm()

        #Icheckthe"Approved"statusofpurchaseorder1
        self.assertEqual(purchase_order_lifo1.state,'purchase')

        #Processthereceiptofpurchaseorder1
        purchase_order_lifo1.picking_ids[0].move_lines.quantity_done=purchase_order_lifo1.picking_ids[0].move_lines.product_qty
        purchase_order_lifo1.picking_ids[0].button_validate()

        #Iconfirmthesecondpurchaseorder
        purchase_order_lifo2.button_confirm()

        #Processthereceiptofpurchaseorder2
        purchase_order_lifo2.picking_ids[0].move_lines.quantity_done=purchase_order_lifo2.picking_ids[0].move_lines.product_qty
        purchase_order_lifo2.picking_ids[0].button_validate()

        #Letussendsomegoods
        self.company_data['default_warehouse'].out_type_id.show_operations=False
        out_form=Form(self.env['stock.picking'])
        out_form.picking_type_id=self.company_data['default_warehouse'].out_type_id
        out_form.immediate_transfer=True
        without_form.move_ids_without_package.new()asmove:
            move.product_id=product_lifo_icecream
            move.quantity_done=20.0
            move.date=fields.Datetime.now()
        outgoing_lifo_shipment=out_form.save()

        #Iassignthisoutgoingshipment
        outgoing_lifo_shipment.action_assign()

        #Processthedeliveryoftheoutgoingshipment
        outgoing_lifo_shipment.button_validate()

        #Checkifthemovevaluecorrectlyreflectsthefifocostingmethod
        self.assertEqual(outgoing_lifo_shipment.move_lines.stock_valuation_layer_ids.value,-1400.0,'Stockmovevalueshouldhavebeen1400euro')
