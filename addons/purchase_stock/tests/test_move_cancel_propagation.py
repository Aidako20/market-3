#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimporttagged
from.commonimportPurchaseTestCommon


classTestMoveCancelPropagation(PurchaseTestCommon):

    defsetUp(self):
        super(TestMoveCancelPropagation,self).setUp()
        self.customer=self.env['res.partner'].create({'name':'abc'})
        self.group=self.env['procurement.group'].create({'partner_id':self.customer.id,'name':'NewGroup'})
        self.warehouse=self.env.ref('stock.warehouse0')
        cust_location=self.env.ref('stock.stock_location_customers')
        seller=self.env['product.supplierinfo'].create({
            'name':self.customer.id,
            'price':100.0,
        })
        product=self.env['product.product'].create({
            'name':'Geyser',
            'type':'product',
            'route_ids':[(4,self.route_mto),(4,self.route_buy)],
            'seller_ids':[(6,0,[seller.id])],
        })
        self.picking_out=self.env['stock.picking'].create({
            'location_id':self.warehouse.out_type_id.default_location_src_id.id,
            'location_dest_id':cust_location.id,
            'partner_id':self.customer.id,
            'group_id':self.group.id,
            'picking_type_id':self.ref('stock.picking_type_out'),
        })
        self.move=self.env['stock.move'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':10,
            'product_uom':product.uom_id.id,
            'picking_id':self.picking_out.id,
            'group_id':self.group.id,
            'location_id':self.warehouse.out_type_id.default_location_src_id.id,
            'location_dest_id':cust_location.id,
            'procure_method':'make_to_order',
        })

    deftest_01_cancel_draft_purchase_order_one_steps(self):
        """CheckthepickingandmovesstatusrelatedPO,Whencancelingpurchaseorder
            Ex.
                1)Setonestepsofreceiptionanddeliveryonthewarehouse.
                2)CreateDeliveryorderwithmtomoveandconfirmtheorder,relatedRFQshouldbegenerated.
                3)Cancel'draft'purchaseordershouldnotcancel<Delivery>
        """
        self.warehouse.write({'delivery_steps':'ship_only','reception_steps':'one_step'})
        self.picking_out.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.move.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.picking_out.action_confirm()

        #FindPOrelatedtopicking.
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.customer.id)])

        #Poshouldbecreaterelatedpicking.
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        #CheckstatusofPurchaseOrder
        self.assertEqual(purchase_order.state,'draft',"Purchaseordershouldbein'draft'state.")

        #CancelPurchaseorder.
        purchase_order.button_cancel()

        #Checkthestatusofpickingaftercancelingpo.
        self.assertNotEqual(self.picking_out.state,'cancel')

    deftest_02_cancel_confirm_purchase_order_one_steps(self):
        """Checkthepickingandmovesstatusrelatedpurchaseorder,Whencancelingpurchaseorder
            afterconfirming.
            Ex.
                1)Setonestepsofreceiptionanddeliveryonthewarehouse.
                2)CreateDeliveryorderwithmtomoveandconfirmtheorder,relatedRFQshouldbegenerated.
                3)Cancel'confirmed'purchaseorder,shouldcancelreleted<Receiption>
                  butitshouldnotcancel<Delivery>order.
        """
        self.warehouse.write({'delivery_steps':'ship_only','reception_steps':'one_step'})
        self.picking_out.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.move.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.picking_out.action_confirm()

        #FindPOrelatedtopicking.
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.customer.id)])
        #Poshouldbecreaterelatedpicking.
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        #CheckstatusofPurchaseOrder
        self.assertEqual(purchase_order.state,'draft',"Purchaseordershouldbein'draft'state.")
        purchase_order.button_confirm()
        picking_in=purchase_order.picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.in_type_id)
        #CancelPurchaseorder.
        purchase_order.button_cancel()

        #Checkthestatusofpickingaftercancelingpo.
        self.assertEqual(picking_in.state,'cancel')
        self.assertNotEqual(self.picking_out.state,'cancel')

    deftest_03_cancel_draft_purchase_order_two_steps(self):
        """CheckthepickingandmovesstatusrelatedPO,Whencancelingpurchaseorder
            in'draft'state.
            Ex.
                1)Settwostepsofreceiptionanddeliveryonthewarehouse.
                2)CreateDeliveryorderwithmtomoveandconfirmtheorder,relatedRFQshouldbegenerated.
                3)Cancel'draft'purchaseordershouldcancel<InputtoStock>
                  butitshouldnotcancel<PICK,Delivery>
        """
        self.warehouse.write({'delivery_steps':'pick_ship','reception_steps':'two_steps'})
        self.picking_out.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.move.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.picking_out.action_confirm()

        #Findpurchaseorderrelatedtopicking.
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.customer.id)])
        #Purchaseordershouldbecreatedforpicking.
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        picking_ids=self.env['stock.picking'].search([('group_id','=',self.group.id)])

        internal=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.int_type_idandr.group_id.id==self.group.id)
        pick=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.pick_type_idandr.group_id.id==self.group.id)

        #CheckstatusofPurchaseOrder
        self.assertEqual(purchase_order.state,'draft',"Purchaseordershouldbein'draft'state.")
        #CancelPurchaseorder.
        purchase_order.button_cancel()

        #Checkthestatusofpickingaftercancelingpo.
        forresininternal:
            self.assertEqual(res.state,'cancel')
        self.assertNotEqual(pick.state,'cancel')
        self.assertNotEqual(self.picking_out.state,'cancel')

    deftest_04_cancel_confirm_purchase_order_two_steps(self):
        """CheckthepickingandmovesstatusrelatedPO,Whencancelingpurchaseorder
            Ex.
                1)Set2stepsofreceiptionanddeliveryonthewarehouse.
                2)CreateDeliveryorderwithmtomoveandconfirmtheorder,relatedRFQshouldbegenerated.
                3)Cancel'comfirm'purchaseordershouldcancelreleted<ReceiptionPickingIN,INT>
                  not<PICK,SHIP>
        """
        self.warehouse.write({'delivery_steps':'pick_ship','reception_steps':'two_steps'})
        self.picking_out.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.move.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.picking_out.action_confirm()

        #FindPOrelatedtopicking.
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.customer.id)])
        #Poshouldbecreaterelatedpicking.
        self.assertTrue(purchase_order,'purchaseorderiscreated.')

        picking_ids=self.env['stock.picking'].search([('group_id','=',self.group.id)])

        internal=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.int_type_id)
        pick=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.pick_type_id)

        #CheckstatusofPurchaseOrder
        self.assertEqual(purchase_order.state,'draft',"Purchaseordershouldbein'draft'state.")

        purchase_order.button_confirm()
        picking_in=purchase_order.picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.in_type_id)
        #CancelPurchaseorder.
        purchase_order.button_cancel()

        #Checkthestatusofpickingaftercancelingpo.
        self.assertEqual(picking_in.state,'cancel')
        forresininternal:
            self.assertEqual(res.state,'cancel')
        self.assertNotEqual(pick.state,'cancel')
        self.assertNotEqual(self.picking_out.state,'cancel')

    deftest_05_cancel_draft_purchase_order_three_steps(self):
        """CheckthepickingandmovesstatusrelatedPO,Whencancelingpurchaseorder
            Ex.
                1)Set3stepsofreceiptionanddeliveryonthewarehouse.
                2)CreateDeliveryorderwithmtomoveandconfirmtheorder,relatedRFQshouldbegenerated.
                3)Cancel'draft'purchaseordershouldcancelreleted<ReceiptionPicking IN>
                  not<PICK,PACK,SHIP>
        """
        self.warehouse.write({'delivery_steps':'pick_pack_ship','reception_steps':'three_steps'})
        self.picking_out.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.move.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.picking_out.action_confirm()

        #FindPOrelatedtopicking.
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.customer.id)])
        #Poshouldbecreaterelatedpicking.
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        picking_ids=self.env['stock.picking'].search([('group_id','=',self.group.id)])

        internal=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.int_type_id)
        pick=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.pick_type_id)
        pack=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.pack_type_id)

        #CheckstatusofPurchaseOrder
        self.assertEqual(purchase_order.state,'draft',"Purchaseordershouldbein'draft'state.")
        #CancelPurchaseorder.
        purchase_order.button_cancel()

        #Checkthestatusofpickingaftercancelingpo.
        forresininternal:
            self.assertEqual(res.state,'cancel')
        self.assertNotEqual(pick.state,'cancel')
        self.assertNotEqual(pack.state,'cancel')
        self.assertNotEqual(self.picking_out.state,'cancel')

    deftest_06_cancel_confirm_purchase_order_three_steps(self):
        """CheckthepickingandmovesstatusrelatedPO,Whencancelingpurchaseorder
            Ex.
                1)Set3stepsofreceiptionanddeliveryonthewarehouse.
                2)CreateDeliveryorderwithmtomoveandconfirmtheorder,relatedRFQshouldbegenerated.
                3)Cancel'comfirm'purchaseordershouldcancelreleted<ReceiptionPickingIN,INT>
                  not<PICK,PACK,SHIP>
        """
        self.warehouse.write({'delivery_steps':'pick_pack_ship','reception_steps':'three_steps'})
        self.picking_out.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.move.write({'location_id':self.warehouse.out_type_id.default_location_src_id.id})
        self.picking_out.action_confirm()

        #FindPOrelatedtopicking.
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.customer.id)])
        #Poshouldbecreaterelatedpicking.
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        picking_ids=self.env['stock.picking'].search([('group_id','=',self.group.id)])

        internal=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.int_type_id)
        pick=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.pick_type_id)
        pack=picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.pack_type_id)

        #CheckstatusofPurchaseOrder
        self.assertEqual(purchase_order.state,'draft',"Purchaseordershouldbein'draft'state.")

        purchase_order.button_confirm()
        picking_in=purchase_order.picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse.in_type_id)
        #CancelPurchaseorder.
        purchase_order.button_cancel()

        #Checkthestatusofpickingaftercancelingpo.
        self.assertEqual(picking_in.state,'cancel')
        forresininternal:
            self.assertEqual(res.state,'cancel')
        self.assertNotEqual(pick.state,'cancel')
        self.assertNotEqual(pack.state,'cancel')
        self.assertNotEqual(self.picking_out.state,'cancel')

    deftest_cancel_move_lines_operation(self):
        """Checkfordoneandcancelledmoves.EnsurethattheRFQcancellation
        willnotimpactthedeliverystateifit'salreadycancelled.
        """
        stock_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_stock')
        customer_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_customers')
        picking_type_out=self.env['ir.model.data'].xmlid_to_object('stock.picking_type_out')

        partner=self.env['res.partner'].create({
            'name':'Steve'
        })
        seller=self.env['product.supplierinfo'].create({
            'name':partner.id,
            'price':10.0,
        })
        product_car=self.env['product.product'].create({
            'name':'Car',
            'type':'product',
            'route_ids':[(4,self.ref('stock.route_warehouse0_mto')),(4,self.ref('purchase_stock.route_warehouse0_buy'))],
            'seller_ids':[(6,0,[seller.id])],
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        customer_picking=self.env['stock.picking'].create({
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':picking_type_out.id,
        })
        customer_move=self.env['stock.move'].create({
            'name':'moveout',
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'product_id':product_car.id,
            'product_uom':product_car.uom_id.id,
            'product_uom_qty':10.0,
            'procure_method':'make_to_order',
            'picking_id':customer_picking.id,
        })
        customer_move._action_confirm()
        purchase_order=self.env['purchase.order'].search([('partner_id','=',partner.id)])
        customer_move._action_cancel()
        self.assertEqual(customer_move.state,'cancel','Moveshouldbecancelled')
        purchase_order.button_cancel()
        self.assertEqual(customer_move.state,'cancel','Stateofcancelledanddonemovesshouldnotchange.')
