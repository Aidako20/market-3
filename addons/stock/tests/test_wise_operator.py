#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestWiseOperator(TransactionCase):

    deftest_wise_operator(self):

        #Createanewstorableproduct
        product_wise=self.env['product.product'].create({
            'name':'WiseUnit',
            'type':'product',
            'categ_id':self.ref('product.product_category_1'),
            'uom_id':self.ref('uom.product_uom_unit'),
            'uom_po_id':self.ref('uom.product_uom_unit'),
        })

        self.partner=self.env['res.partner'].create({'name':'DecoAddict'})

        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        self.shelf2=self.env['stock.location'].create({
            'name':'Shelf2',
            'barcode':1231985,
            'location_id':warehouse.lot_stock_id.id
        })
        self.shelf1=self.env['stock.location'].create({
            'name':'Shelf1',
            'barcode':1231892,
            'location_id':warehouse.lot_stock_id.id
        })

        self.partner2=self.env['res.partner'].create({'name':'ReadyMat'})

        #Createanincomingpickingforthisproductof10PCEfromsupplierstostock
        vals={
            'name':'Incomingpicking(wiseunit)',
            'partner_id':self.partner.id,
            'picking_type_id':self.ref('stock.picking_type_in'),
            'location_id':self.ref('stock.stock_location_suppliers'),
            'location_dest_id':self.ref('stock.stock_location_stock'),
            'move_lines':[(0,0,{
                'name':'/',
                'product_id':product_wise.id,
                'product_uom':product_wise.uom_id.id,
                'product_uom_qty':10.00,
                'location_id':self.ref('stock.stock_location_suppliers'),
                'location_dest_id':self.ref('stock.stock_location_stock'),
            })],
        }
        pick1_wise=self.env['stock.picking'].create(vals)
        pick1_wise.onchange_picking_type()
        pick1_wise.move_lines.onchange_product_id()

        #Confirmandassignpickingandpreparepartial
        pick1_wise.action_confirm()
        pick1_wise.action_assign()

        #Put4piecesinshelf1and6piecesinshelf2
        package1=self.env['stock.quant.package'].create({'name':'Pack1'})
        pick1_wise.move_line_ids[0].write({
            'result_package_id':package1.id,
            'qty_done':4,
            'location_dest_id':self.shelf1.id
        })
        new_pack1=self.env['stock.move.line'].create({
            'product_id':product_wise.id,
            'product_uom_id':self.ref('uom.product_uom_unit'),
            'picking_id':pick1_wise.id,
            'qty_done':6.0,
            'location_id':self.ref('stock.stock_location_suppliers'),
            'location_dest_id':self.shelf2.id
        })

        #Transferthereceipt
        pick1_wise._action_done()

        #Checkthesystemcreated3quants
        records=self.env['stock.quant'].search([('product_id','=',product_wise.id)])
        self.assertEqual(len(records.ids),3,"Thenumberofquantscreatedisnotcorrect")

        #Makeadeliveryorderof5piecestothecustomer
        vals={
            'name':'outgoingpicking1(wiseunit)',
            'partner_id':self.partner2.id,
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'move_lines':[(0,0,{
                'name':'/',
                'product_id':product_wise.id,
                'product_uom':product_wise.uom_id.id,
                'product_uom_qty':5.0,
                'location_id':self.ref('stock.stock_location_stock'),
                'location_dest_id':self.ref('stock.stock_location_customers'),
            })],
        }
        delivery_order_wise1=self.env['stock.picking'].create(vals)
        delivery_order_wise1.onchange_picking_type()
        delivery_order_wise1.move_lines.onchange_product_id()

        #Assignandconfirm
        delivery_order_wise1.action_confirm()
        delivery_order_wise1.action_assign()
        self.assertEqual(delivery_order_wise1.state,'assigned')

        #Makeadeliveryorderof5piecestothecustomer
        vals={
            'name':'outgoingpicking2(wiseunit)',
            'partner_id':self.partner2.id,
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'move_lines':[(0,0,{
                'name':'/',
                'product_id':product_wise.id,
                'product_uom':product_wise.uom_id.id,
                'product_uom_qty':5.0,
                'location_id':self.ref('stock.stock_location_stock'),
                'location_dest_id':self.ref('stock.stock_location_customers'),
            })],
        }
        delivery_order_wise2=self.env['stock.picking'].create(vals)
        delivery_order_wise2.onchange_picking_type()
        delivery_order_wise2.move_lines.onchange_product_id()

        #Assignandconfirm
        delivery_order_wise2.action_confirm()
        delivery_order_wise2.action_assign()
        self.assertEqual(delivery_order_wise2.state,'assigned')

        #TheoperatorisawiseguyanddecidestodotheoppositeofwhatFlectraproposes.
        #Heusestheproductsreservedonpicking1onpicking2andviceversa
        move1=delivery_order_wise1.move_lines[0]
        move2=delivery_order_wise2.move_lines[0]
        pack_ids1=delivery_order_wise1.move_line_ids
        pack_ids2=delivery_order_wise2.move_line_ids

        self.assertEqual(pack_ids1.location_id.id,self.shelf2.id)
        self.assertEqual(set(pack_ids2.mapped('location_id.id')),set([
            self.shelf1.id,
            self.shelf2.id]))

        #putthemovelinesfromdelivery_order_wise2intodelivery_order_wise1
        forpack_id2inpack_ids2:
            new_pack_id1=pack_id2.copy(default={'picking_id':delivery_order_wise1.id,'move_id':move1.id})
            new_pack_id1.qty_done=pack_id2.product_qty

        new_move_lines=delivery_order_wise1.move_line_ids.filtered(lambdap:p.qty_done)
        self.assertEqual(sum(new_move_lines.mapped('product_qty')),0)
        self.assertEqual(sum(new_move_lines.mapped('qty_done')),5)
        self.assertEqual(set(new_move_lines.mapped('location_id.id')),set([
            self.shelf1.id,
            self.shelf2.id]))

        #putthemovelinefromdelivery_order_wise1intodelivery_order_wise2
        new_pack_id2=pack_ids1.copy(default={'picking_id':delivery_order_wise2.id,'move_id':move2.id})
        new_pack_id2.qty_done=pack_ids1.product_qty

        new_move_lines=delivery_order_wise2.move_line_ids.filtered(lambdap:p.qty_done)
        self.assertEqual(len(new_move_lines),1)
        self.assertEqual(sum(new_move_lines.mapped('product_qty')),0)
        self.assertEqual(sum(new_move_lines.mapped('qty_done')),5)
        self.assertEqual(new_move_lines.location_id.id,self.shelf2.id)

        #Processthispicking
        delivery_order_wise1._action_done()

        #Checktherewasnonegativequantcreatedbythispicking

        records=self.env['stock.quant'].search([
            ('product_id','=',product_wise.id),
            ('quantity','<',0.0),
            ('location_id.id','=',self.ref('stock.stock_location_stock'))])
        self.assertEqual(len(records.ids),0,'Thisshouldnothavecreatedanegativequant')

        #Checktheotherdeliveryorderhaschangeditsstatebacktoready
        self.assertEqual(delivery_order_wise2.state,'assigned',"Deliveryorder2shouldbebackinreadystate")

        #Processthesecondpicking
        delivery_order_wise2._action_done()

        #CheckallquantsareinCustomersandtherearenonegativequantsanymore
        records=self.env['stock.quant'].search([
            ('product_id','=',product_wise.id),
            ('location_id','!=',self.ref('stock.stock_location_suppliers'))])
        self.assertTrue(all([x.location_id.id==self.ref('stock.stock_location_customers')andx.quantity>0.0or
                             x.location_id.id!=self.ref('stock.stock_location_customers')andx.quantity==0.0forxinrecords]),
                        "Negativequantorwronglocationdetected")
