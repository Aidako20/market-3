#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetimeasdt
fromdatetimeimporttimedeltaastd
fromfreezegunimportfreeze_time

fromflectraimportSUPERUSER_ID
fromflectra.testsimportForm
fromflectra.tests.commonimportSavepointCase
fromflectra.exceptionsimportUserError


@freeze_time("2021-01-1409:12:15")
classTestReorderingRule(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super(TestReorderingRule,cls).setUpClass()
        cls.partner=cls.env['res.partner'].create({
            'name':'Smith'
        })

        #createproductandsetthevendor
        product_form=Form(cls.env['product.product'])
        product_form.name='ProductA'
        product_form.type='product'
        product_form.description='InternalNotes'
        withproduct_form.seller_ids.new()asseller:
            seller.name=cls.partner
        product_form.route_ids.add(cls.env.ref('purchase_stock.route_warehouse0_buy'))
        cls.product_01=product_form.save()

    deftest_reordering_rule_1(self):
        """
            -Receiveproductsin2steps
            -Theproducthasareorderingrule
            -Onthepogenerated,thesourcedocumentshouldbethenameofthereorderingrule
            -IncreasethequantityontheRFQ,theextraquantityshouldfollowthepushrules
            -IncreasethequantityonthePO,theextraquantityshouldfollowthepushrules
            -Thereshouldbeonemovesupplier->inputandtwomovesinput->stock
        """
        warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse_1.write({'reception_steps':'two_steps'})
        warehouse_2=self.env['stock.warehouse'].create({'name':'WH2','code':'WH2','company_id':self.env.company.id,'partner_id':self.env.company.partner_id.id,'reception_steps':'one_step'})
        
        #createreorderingrule
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id=warehouse_1
        orderpoint_form.location_id=warehouse_1.lot_stock_id
        orderpoint_form.product_id=self.product_01
        orderpoint_form.product_min_qty=0.000
        orderpoint_form.product_max_qty=0.000
        order_point=orderpoint_form.save()
        #CreateDeliveryOrderof10product
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=self.partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.product_01
            move.product_uom_qty=10.0
        customer_picking=picking_form.save()
        #pickingconfirm
        customer_picking.action_confirm()
        #Runscheduler
        self.env['procurement.group'].run_scheduler()

        #Checkpurchaseordercreatedornot
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.partner.id)])
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')
        
        #Checkthepickingtypeonthepurchaseorder
        purchase_order.picking_type_id=warehouse_2.in_type_id
        withself.assertRaises(UserError):
            purchase_order.button_confirm()
        purchase_order.picking_type_id=warehouse_1.in_type_id

        #Onthepogenerated,thesourcedocumentshouldbethenameofthereorderingrule
        self.assertEqual(order_point.name,purchase_order.origin,'Sourcedocumentonpurchaseordershouldbethenameofthereorderingrule.')
        self.assertEqual(purchase_order.order_line.product_qty,10)
        self.assertEqual(purchase_order.order_line.name,'ProductA')

        #IncreasethequantityontheRFQbeforeconfirmingit
        purchase_order.order_line.product_qty=12
        purchase_order.button_confirm()

        self.assertEqual(purchase_order.picking_ids.move_lines.filtered(lambdam:m.product_id==self.product_01).product_qty,12)
        next_picking=purchase_order.picking_ids.move_lines.move_dest_ids.picking_id
        self.assertEqual(len(next_picking),2)
        self.assertEqual(next_picking[0].move_lines.filtered(lambdam:m.product_id==self.product_01).product_qty,10)
        self.assertEqual(next_picking[1].move_lines.filtered(lambdam:m.product_id==self.product_01).product_qty,2)

        #IncreasethequantityonthePO
        purchase_order.order_line.product_qty=15
        self.assertEqual(purchase_order.picking_ids.move_lines.product_qty,15)
        self.assertEqual(next_picking[0].move_lines.filtered(lambdam:m.product_id==self.product_01).product_qty,10)
        self.assertEqual(next_picking[1].move_lines.filtered(lambdam:m.product_id==self.product_01).product_qty,5)

    deftest_reordering_rule_2(self):
        """
            -Receiveproductsin1steps
            -Theproducthastworeorderingrules,eachoneapplyinginasublocation
            -Processingthepurchaseordershouldfulfillthetwosublocations
            -IncreasethequantityontheRFQforoneofthePOL,theextraquantitywillgoto
              theoriginalsublocsincewedon'tknowwheretopushit(nomovedest)
            -IncreasethequantityonthePO,theextraquantityshouldfollowthepushrulesand
              thusgotostock
        """
        warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        subloc_1=self.env['stock.location'].create({'name':'subloc_1','location_id':warehouse_1.lot_stock_id.id})
        subloc_2=self.env['stock.location'].create({'name':'subloc_2','location_id':warehouse_1.lot_stock_id.id})

        #createreorderingrules
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id=warehouse_1
        orderpoint_form.location_id=subloc_1
        orderpoint_form.product_id=self.product_01
        orderpoint_form.product_min_qty=0.000
        orderpoint_form.product_max_qty=0.000
        order_point_1=orderpoint_form.save()
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id=warehouse_1
        orderpoint_form.location_id=subloc_2
        orderpoint_form.product_id=self.product_01
        orderpoint_form.product_min_qty=0.000
        orderpoint_form.product_max_qty=0.000
        order_point_2=orderpoint_form.save()

        #CreateDeliveryOrderof10product
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=self.partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.product_01
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.product_01
            move.product_uom_qty=10.0
        customer_picking=picking_form.save()
        customer_picking.move_lines[0].location_id=subloc_1.id
        customer_picking.move_lines[1].location_id=subloc_2.id

        #pickingconfirm
        customer_picking.action_confirm()
        self.assertEqual(self.product_01.with_context(location=subloc_1.id).virtual_available,-10)
        self.assertEqual(self.product_01.with_context(location=subloc_2.id).virtual_available,-10)

        #Runscheduler
        self.env['procurement.group'].run_scheduler()

        #Checkpurchaseordercreatedornot
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.partner.id)])
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')
        self.assertEqual(len(purchase_order.order_line),2,'Notenoughpurchaseorderlinescreated.')

        #incrementtheqtyofthefirstpoline
        purchase_order.order_line.filtered(lambdapol:pol.orderpoint_id==order_point_1).product_qty=15
        purchase_order.button_confirm()
        self.assertEqual(self.product_01.with_context(location=subloc_1.id).virtual_available,5)
        self.assertEqual(self.product_01.with_context(location=subloc_2.id).virtual_available,0)

        #incrementtheqtyofthesecondpoline
        purchase_order.order_line.filtered(lambdapol:pol.orderpoint_id==order_point_2).with_context(debug=True).product_qty=15
        self.assertEqual(self.product_01.with_context(location=subloc_1.id).virtual_available,5)
        self.assertEqual(self.product_01.with_context(location=subloc_2.id).virtual_available,0)
        self.assertEqual(self.product_01.with_context(location=warehouse_1.lot_stock_id.id).virtual_available,10) #5onthemainloc,5onsubloc_1

        self.assertEqual(purchase_order.picking_ids.move_lines[-1].product_qty,5)
        self.assertEqual(purchase_order.picking_ids.move_lines[-1].location_dest_id,warehouse_1.lot_stock_id)

    deftest_reordering_rule_3(self):
        """
            triggerareorderingrulewitharoutetoalocationwithoutwarehouse
        """
        warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)

        outside_loc=self.env['stock.location'].create({
            'name':'outside',
            'usage':'internal',
            'location_id':self.env.ref('stock.stock_location_locations').id,
        })
        route=self.env['stock.location.route'].create({
            'name':'resupplyoutside',
            'rule_ids':[
                (0,False,{
                    'name':'Buy',
                    'location_id':warehouse_1.lot_stock_id.id,
                    'company_id':self.env.company.id,
                    'action':'buy',
                    'sequence':2,
                    'procure_method':'make_to_stock',
                    'picking_type_id':self.env.ref('stock.picking_type_in').id,
                }),
                (0,False,{
                    'name':'ressuplyfromstock',
                    'location_src_id':warehouse_1.lot_stock_id.id,
                    'location_id':outside_loc.id,
                    'company_id':self.env.company.id,
                    'action':'pull',
                    'procure_method':'mts_else_mto',
                    'sequence':1,
                    'picking_type_id':self.env.ref('stock.picking_type_out').id,
                }),
            ],
        })
        vendor1=self.env['res.partner'].create({'name':'AAA','email':'from.test@example.com'})
        supplier_info1=self.env['product.supplierinfo'].create({
            'name':vendor1.id,
            'price':50,
        })
        product=self.env['product.product'].create({
            'name':'product_rr_3',
            'type':'product',
            'route_ids':[(4,route.id)],
            'seller_ids':[(6,0,[supplier_info1.id])],
        })

        #createreorderingrules
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'].with_user(2))
        orderpoint_form.warehouse_id=warehouse_1
        orderpoint_form.location_id=outside_loc
        orderpoint_form.product_id=product
        orderpoint_form.product_min_qty=0.000
        orderpoint_form.product_max_qty=0.000
        order_point_1=orderpoint_form.save()
        order_point_1.route_id=route
        order_point_1.trigger='manual'

        #Createmoveoutof10product
        move=self.env['stock.move'].create({
            'name':'moveout',
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':10,
            'location_id':outside_loc.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move._action_confirm()

        #Forecastontheorderpointshouldbe-10
        self.assertEqual(order_point_1.qty_forecast,-10)

        order_point_1.action_replenish()

        #Checkpurchaseordercreatedornot
        purchase_order=self.env['purchase.order.line'].search([('product_id','=',product.id)]).order_id
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')
        self.assertEqual(len(purchase_order.order_line),1,'Notenoughpurchaseorderlinescreated.')
        purchase_order.button_confirm()

    deftest_reordering_rule_4(self):
        """WhenupdatingaPOgeneratedbythescheduler,iftheuserdecreasesthequantityandthenconfirmsthePO,
        thepickingquantityshouldbetheupdatedone
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse.write({'reception_steps':'three_steps'})

        self.env['stock.warehouse.orderpoint'].search([]).unlink()
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id=warehouse
        orderpoint_form.location_id=warehouse.lot_stock_id
        orderpoint_form.product_id=self.product_01
        orderpoint_form.product_min_qty=1
        orderpoint_form.product_max_qty=100
        orderpoint_form.save()

        self.env['procurement.group'].run_scheduler()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.partner.id)])
        purchase_order.order_line.product_qty=80
        purchase_order.button_confirm()

        move=purchase_order.picking_ids.move_lines
        forqty,transfer_namein[(80,"Vendor->Input"),(100,"Input->Quality"),(100,"Quality->Stock")]:
            self.assertEqual(move.product_qty,qty,"Incorrectqtyfortrasfer%s"%transfer_name)
            move=move.move_dest_ids
        self.assertFalse(move)

    deftest_reordering_rule_5(self):
        """
        AproductPwthRR0-0-1.
        Confirmadeliverywith1xP->POcreatedforit.
        Confirmaseconddelivery,with1xPagain:
        -ThePOshouldbeupdated
        -TheqtytoorderoftheRRshouldbezero
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        stock_location=warehouse.lot_stock_id
        out_type=warehouse.out_type_id
        customer_location=self.env.ref('stock.stock_location_customers')

        rr=self.env['stock.warehouse.orderpoint'].create({
            'location_id':stock_location.id,
            'product_id':self.product_01.id,
            'product_min_qty':0,
            'product_max_qty':0,
            'qty_multiple':1,
        })

        delivery=self.env['stock.picking'].create({
            'picking_type_id':out_type.id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'move_lines':[(0,0,{
                'name':self.product_01.name,
                'product_id':self.product_01.id,
                'product_uom_qty':1,
                'product_uom':self.product_01.uom_id.id,
                'location_id':stock_location.id,
                'location_dest_id':customer_location.id,
            })]
        })
        delivery.action_confirm()

        pol=self.env['purchase.order.line'].search([('product_id','=',self.product_01.id)])
        self.assertEqual(pol.product_qty,1.0)
        self.assertEqual(rr.qty_to_order,0.0)

        delivery=self.env['stock.picking'].create({
            'picking_type_id':out_type.id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'move_lines':[(0,0,{
                'name':self.product_01.name,
                'product_id':self.product_01.id,
                'product_uom_qty':1,
                'product_uom':self.product_01.uom_id.id,
                'location_id':stock_location.id,
                'location_dest_id':customer_location.id,
            })]
        })
        delivery.action_confirm()

        self.assertEqual(pol.product_qty,2.0)
        self.assertEqual(rr.qty_to_order,0.0)

    deftest_replenish_report_1(self):
        """Teststheautogenerationofmanualorderpoints.

        Openingmultipletimesthereportshouldnotduplicatethegeneratedorderpoints.
        MTOproductsshouldnottriggerthecreationofgeneratedorderpoints
        """
        partner=self.env['res.partner'].create({
            'name':'Tintin'
        })
        route_buy=self.env.ref('purchase_stock.route_warehouse0_buy')
        route_mto=self.env.ref('stock.route_warehouse0_mto')

        product_form=Form(self.env['product.product'])
        product_form.name='SimpleProduct'
        product_form.type='product'
        withproduct_form.seller_ids.new()ass:
            s.name=partner
        product=product_form.save()

        product_form=Form(self.env['product.product'])
        product_form.name='ProductBUY+MTO'
        product_form.type='product'
        product_form.route_ids.add(route_buy)
        product_form.route_ids.add(route_mto)
        withproduct_form.seller_ids.new()ass:
            s.name=partner
        product_buy_mto=product_form.save()

        #CreateDeliveryOrderof20productand10buy+MTO
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product_buy_mto
            move.product_uom_qty=10.0
        customer_picking=picking_form.save()
        customer_picking.move_lines.filtered(lambdam:m.product_id==product_buy_mto).procure_method='make_to_order'
        customer_picking.action_confirm()
        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()
        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()

        orderpoint_product=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product.id)])
        orderpoint_product_mto_buy=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product_buy_mto.id)])
        self.assertFalse(orderpoint_product_mto_buy)
        self.assertEqual(len(orderpoint_product),1.0)
        self.assertEqual(orderpoint_product.qty_to_order,20.0)
        self.assertEqual(orderpoint_product.trigger,'manual')
        self.assertEqual(orderpoint_product.create_uid.id,SUPERUSER_ID)

        orderpoint_product.action_replenish()
        po=self.env['purchase.order'].search([('partner_id','=',partner.id)])
        self.assertTrue(po)
        self.assertEqual(len(po.order_line),2.0)
        po_line_product_mto=po.order_line.filtered(lambdal:l.product_id==product_buy_mto)
        po_line_product=po.order_line.filtered(lambdal:l.product_id==product)
        self.assertEqual(po_line_product_mto.product_uom_qty,10.0)
        self.assertEqual(po_line_product.product_uom_qty,20.0)

        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()
        orderpoint_product=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product.id)])
        orderpoint_product_mto_buy=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product_buy_mto.id)])
        self.assertFalse(orderpoint_product)
        self.assertFalse(orderpoint_product_mto_buy)

        #CreateDeliveryOrderof10productand10buy+MTO
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product_buy_mto
            move.product_uom_qty=10.0
        customer_picking=picking_form.save()
        customer_picking.move_lines.filtered(lambdam:m.product_id==product_buy_mto).procure_method='make_to_order'
        customer_picking.action_confirm()
        self.env['stock.warehouse.orderpoint'].flush()

        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()
        orderpoint_product=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product.id)])
        orderpoint_product_mto_buy=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product_buy_mto.id)])
        self.assertFalse(orderpoint_product_mto_buy)
        self.assertEqual(len(orderpoint_product),1.0)
        self.assertEqual(orderpoint_product.qty_to_order,10.0)
        self.assertEqual(orderpoint_product.trigger,'manual')
        self.assertEqual(orderpoint_product.create_uid.id,SUPERUSER_ID)

    deftest_replenish_report_2(self):
        """Samethen`test_replenish_report_1`butwithtwostepsreceiptenabled"""
        partner=self.env['res.partner'].create({
            'name':'Tintin'
        })
        forwhinself.env['stock.warehouse'].search([]):
            wh.write({'reception_steps':'two_steps'})
        route_buy=self.env.ref('purchase_stock.route_warehouse0_buy')
        route_mto=self.env.ref('stock.route_warehouse0_mto')

        product_form=Form(self.env['product.product'])
        product_form.name='SimpleProduct'
        product_form.type='product'
        withproduct_form.seller_ids.new()ass:
            s.name=partner
        product=product_form.save()

        product_form=Form(self.env['product.product'])
        product_form.name='ProductBUY+MTO'
        product_form.type='product'
        product_form.route_ids.add(route_buy)
        product_form.route_ids.add(route_mto)
        withproduct_form.seller_ids.new()ass:
            s.name=partner
        product_buy_mto=product_form.save()

        #CreateDeliveryOrderof20productand10buy+MTO
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product_buy_mto
            move.product_uom_qty=10.0
        customer_picking=picking_form.save()
        customer_picking.move_lines.filtered(lambdam:m.product_id==product_buy_mto).procure_method='make_to_order'
        customer_picking.action_confirm()
        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()
        orderpoint_product=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product.id)])
        orderpoint_product_mto_buy=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product_buy_mto.id)])
        self.assertFalse(orderpoint_product_mto_buy)
        self.assertEqual(len(orderpoint_product),1.0)
        self.assertEqual(orderpoint_product.qty_to_order,20.0)
        self.assertEqual(orderpoint_product.trigger,'manual')
        self.assertEqual(orderpoint_product.create_uid.id,SUPERUSER_ID)

        orderpoint_product.action_replenish()
        po=self.env['purchase.order'].search([('partner_id','=',partner.id)])
        self.assertTrue(po)
        self.assertEqual(len(po.order_line),2.0)
        po_line_product_mto=po.order_line.filtered(lambdal:l.product_id==product_buy_mto)
        po_line_product=po.order_line.filtered(lambdal:l.product_id==product)
        self.assertEqual(po_line_product_mto.product_uom_qty,10.0)
        self.assertEqual(po_line_product.product_uom_qty,20.0)

        self.env['stock.warehouse.orderpoint'].flush()
        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()
        orderpoint_product=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product.id)])
        orderpoint_product_mto_buy=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product_buy_mto.id)])
        self.assertFalse(orderpoint_product)
        self.assertFalse(orderpoint_product_mto_buy)

        #CreateDeliveryOrderof10productand10buy+MTO
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product
            move.product_uom_qty=10.0
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product_buy_mto
            move.product_uom_qty=10.0
        customer_picking=picking_form.save()
        customer_picking.move_lines.filtered(lambdam:m.product_id==product_buy_mto).procure_method='make_to_order'
        customer_picking.action_confirm()
        self.env['stock.warehouse.orderpoint'].flush()

        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()
        orderpoint_product=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product.id)])
        orderpoint_product_mto_buy=self.env['stock.warehouse.orderpoint'].search(
            [('product_id','=',product_buy_mto.id)])
        self.assertFalse(orderpoint_product_mto_buy)
        self.assertEqual(len(orderpoint_product),1.0)
        self.assertEqual(orderpoint_product.qty_to_order,10.0)
        self.assertEqual(orderpoint_product.trigger,'manual')
        self.assertEqual(orderpoint_product.create_uid.id,SUPERUSER_ID)

    deftest_procure_not_default_partner(self):
        """Defineaproductwith2vendors.Firstruna"standard"procurement,
        defaultvendorshouldbeused.Then,callaprocurementwith
        `partner_id`specifiedinvalues,thespecifiedvendorshouldbe
        used."""
        purchase_route=self.env.ref("purchase_stock.route_warehouse0_buy")
        uom_unit=self.env.ref("uom.product_uom_unit")
        warehouse=self.env['stock.warehouse'].search(
            [('company_id','=',self.env.company.id)],limit=1)
        product=self.env["product.product"].create({
            "name":"productTEST",
            "standard_price":100.0,
            "type":"product",
            "uom_id":uom_unit.id,
            "default_code":"A",
            "route_ids":[(6,0,purchase_route.ids)],
        })
        default_vendor=self.env["res.partner"].create({
            "name":"SupplierA",
        })
        secondary_vendor=self.env["res.partner"].create({
            "name":"SupplierB",
        })
        self.env["product.supplierinfo"].create({
            "name":default_vendor.id,
            "product_tmpl_id":product.product_tmpl_id.id,
            "delay":7,
        })
        self.env["product.supplierinfo"].create({
            "name":secondary_vendor.id,
            "product_tmpl_id":product.product_tmpl_id.id,
            "delay":10,
        })

        #Teststandardprocurement.
        po_line=self.env["purchase.order.line"].search(
            [("product_id","=",product.id)])
        self.assertFalse(po_line)
        self.env["procurement.group"].run(
            [self.env["procurement.group"].Procurement(
                product,100,uom_unit,
                warehouse.lot_stock_id,"Testdefaultvendor","/",
                self.env.company,
                {
                    "warehouse_id":warehouse,
                    "date_planned":dt.today()+td(days=15),
                    "rule_id":warehouse.buy_pull_id,
                    "group_id":False,
                    "route_ids":[],
                }
            )])
        po_line=self.env["purchase.order.line"].search(
            [("product_id","=",product.id)])
        self.assertTrue(po_line)
        self.assertEqual(po_line.partner_id,default_vendor)
        po_line.order_id.button_cancel()
        po_line.order_id.unlink()

        #nowforcethevendor:
        po_line=self.env["purchase.order.line"].search(
            [("product_id","=",product.id)])
        self.assertFalse(po_line)
        self.env["procurement.group"].run(
            [self.env["procurement.group"].Procurement(
                product,100,uom_unit,
                warehouse.lot_stock_id,"Testdefaultvendor","/",
                self.env.company,
                {
                    "warehouse_id":warehouse,
                    "date_planned":dt.today()+td(days=15),
                    "rule_id":warehouse.buy_pull_id,
                    "group_id":False,
                    "route_ids":[],
                    "supplierinfo_name":secondary_vendor,
                }
            )])
        po_line=self.env["purchase.order.line"].search(
            [("product_id","=",product.id)])
        self.assertTrue(po_line)
        self.assertEqual(po_line.partner_id,secondary_vendor)

    deftest_procure_multi_lingual(self):
        """
        DefineaproductwithdescriptioninEnglishandFrench.
        Runaprocurementspecifyingagroup_idwithapartner(customer)
        setupwithFrenchaslanguage. VerifythatthePOisgenerated
        usingthedefault(English)language.
        """
        purchase_route=self.env.ref("purchase_stock.route_warehouse0_buy")
        #createanewwarehousetomakesureitgetsthemts/mtorule
        warehouse=self.env['stock.warehouse'].create({
            "name":"testwarehouse",
            "active":True,
            'reception_steps':'one_step',
            'delivery_steps':'ship_only',
            'code':'TEST'
        })
        customer_loc,_=warehouse._get_partner_locations()
        mto_rule=self.env['stock.rule'].search(
            [('warehouse_id','=',warehouse.id),
             ('procure_method','=','mts_else_mto'),
             ('location_id','=',customer_loc.id)
            ]
        )
        route_mto=self.env["stock.location.route"].create({
            "name":"MTO",
            "active":True,
            "sequence":3,
            "product_selectable":True,
            "rule_ids":[(6,0,[
                mto_rule.id
            ])]
        })
        uom_unit=self.env.ref("uom.product_uom_unit")
        product=self.env["product.product"].create({
            "name":"productTEST",
            "standard_price":100.0,
            "type":"product",
            "uom_id":uom_unit.id,
            "default_code":"A",
            "route_ids":[(6,0,[
                route_mto.id,
                purchase_route.id,
            ])],
        })
        self.env['res.lang']._activate_lang('fr_FR')
        self.env['ir.translation']._set_ids('product.template,name','model','fr_FR',product.product_tmpl_id.ids,'produitenfrançais')
        self.env['ir.translation']._set_ids('product.product,name','model','fr_FR',product.ids,'produitenfrançais')
        default_vendor=self.env["res.partner"].create({
            "name":"SupplierA",
        })
        self.env["product.supplierinfo"].create({
            "name":default_vendor.id,
            "product_tmpl_id":product.product_tmpl_id.id,
            "delay":7,
        })
        customer=self.env["res.partner"].create({
            "name":"Customer",
            "lang":"fr_FR"
        })
        proc_group=self.env["procurement.group"].create({
            "partner_id":customer.id
        })
        procurement=self.env["procurement.group"].Procurement(
                product,100,uom_unit,
                customer.property_stock_customer,
                "Testdefaultvendor",
                "/",
                self.env.company,
                {
                    "warehouse_id":warehouse,
                    "date_planned":dt.today()+td(days=15),
                    "group_id":proc_group,
                    "route_ids":[],
                }
            )
        self.env.cache.invalidate()

        self.env["procurement.group"].run([procurement])

        po_line=self.env["purchase.order.line"].search(
            [("product_id","=",product.id)])
        self.assertTrue(po_line)
        self.assertEqual("[A]productTEST",po_line.name)

    deftest_multi_locations_and_reordering_rule(self):
        """
        Supposetwoorderpointsforthesameproduct,eachonetoadifferentlocation
        Iftheusertriggerseachorderpointseparately,itshouldstillproducetwo
        differentpurchaseorderlines(oneforeachorderpoint)
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        stock_location=warehouse.lot_stock_id
        sub_location=self.env['stock.location'].create({'name':'subloc_1','location_id':stock_location.id})

        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id=warehouse
        orderpoint_form.location_id=stock_location
        orderpoint_form.product_id=self.product_01
        orderpoint_form.product_min_qty=1
        orderpoint_form.product_max_qty=1
        stock_op=orderpoint_form.save()

        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id=warehouse
        orderpoint_form.location_id=sub_location
        orderpoint_form.product_id=self.product_01
        orderpoint_form.product_min_qty=2
        orderpoint_form.product_max_qty=2
        sub_op=orderpoint_form.save()

        stock_op.action_replenish()
        sub_op.action_replenish()

        po=self.env['purchase.order'].search([('partner_id','=',self.partner.id)])
        self.assertRecordValues(po.order_line,[
            {'product_id':self.product_01.id,'product_qty':1.0,'orderpoint_id':stock_op.id},
            {'product_id':self.product_01.id,'product_qty':2.0,'orderpoint_id':sub_op.id},
        ])

        po.button_confirm()
        picking=po.picking_ids
        action=picking.button_validate()
        wizard=Form(self.env[(action.get('res_model'))].with_context(action['context'])).save()
        wizard.process()

        self.assertRecordValues(picking.move_line_ids,[
            {'product_id':self.product_01.id,'qty_done':1.0,'state':'done','location_dest_id':stock_location.id},
            {'product_id':self.product_01.id,'qty_done':2.0,'state':'done','location_dest_id':sub_location.id},
        ])

    deftest_change_of_scheduled_date(self):
        """
        Ausercreatesadelivery,anorderpointiscreated.Itsforecast
        quantitybecomes-1andthequantitytoorderis1.Thentheuser
        postponesthescheduleddateofthedelivery.Thequantitiesofthe
        orderpointshouldberesettozero.
        """
        delivery_form=Form(self.env['stock.picking'])
        delivery_form.partner_id=self.partner
        delivery_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withdelivery_form.move_ids_without_package.new()asmove:
            move.product_id=self.product_01
            move.product_uom_qty=1
        delivery=delivery_form.save()
        delivery.action_confirm()

        self.env['report.stock.quantity'].flush()
        self.env['stock.warehouse.orderpoint']._get_orderpoint_action()

        orderpoint=self.env['stock.warehouse.orderpoint'].search([('product_id','=',self.product_01.id)])
        self.assertRecordValues(orderpoint,[
            {'qty_forecast':-1,'qty_to_order':1},
        ])

        delivery.scheduled_date+=td(days=7)
        orderpoint.invalidate_cache(fnames=['qty_forecast','qty_to_order'],ids=orderpoint.ids)

        self.assertRecordValues(orderpoint,[
            {'qty_forecast':0,'qty_to_order':0},
        ])

    deftest_add_line_to_existing_draft_po(self):
        """
        Daystopurchase=10
        TwoproductsP1,P2fromthesamesupplier
        Severalusecases,eachtimeweruntheRRonebyone.Then,according
        tothedatesandtheconfiguration,itshouldusetheexistingPOornot
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)

        self.env.company.days_to_purchase=10
        expected_order_date=dt.combine(dt.today()+td(days=10),dt.min.time())
        expected_delivery_date=expected_order_date+td(days=1.0)
        expected_delivery_date=expected_delivery_date.replace(hour=12,minute=0,second=0)

        product_02=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'product',
            'seller_ids':[(0,0,{'name':self.partner.id})],
        })

        op_01,op_02=self.env['stock.warehouse.orderpoint'].create([{
            'warehouse_id':warehouse.id,
            'location_id':warehouse.lot_stock_id.id,
            'product_id':p.id,
            'product_min_qty':1,
            'product_max_qty':0,
        }forpin[self.product_01,product_02]])

        op_01.action_replenish()
        po01=self.env['purchase.order'].search([],order='iddesc',limit=1)
        self.assertEqual(po01.date_order,expected_order_date)

        op_02.action_replenish()
        self.assertEqual(po01.date_order,expected_order_date)
        self.assertRecordValues(po01.order_line,[
            {'product_id':self.product_01.id,'date_planned':expected_delivery_date},
            {'product_id':product_02.id,'date_planned':expected_delivery_date},
        ])

        #Resetandtryanotherflow
        po01.button_cancel()
        op_01.action_replenish()
        po02=self.env['purchase.order'].search([],order='iddesc',limit=1)
        self.assertNotEqual(po02,po01)

        withfreeze_time(dt.today()+td(days=1)):
            op_02.invalidate_cache(fnames=['lead_days_date'],ids=op_02.ids)
            op_02.action_replenish()
            self.assertEqual(po02.date_order,expected_order_date)
            self.assertRecordValues(po02.order_line,[
                {'product_id':self.product_01.id,'date_planned':expected_delivery_date},
                {'product_id':product_02.id,'date_planned':expected_delivery_date},
            ])

        #RestrictthemergewithPOsthathavetheirorderdeadlinein[today-2days,today+2days]
        self.env['ir.config_parameter'].set_param('purchase_stock.delta_days_merge','2')

        #ResetandtrywithasecondRRexecutedinthedatesrange(->shouldstillusetheexistingPO)
        po02.button_cancel()
        op_01.action_replenish()
        po03=self.env['purchase.order'].search([],order='iddesc',limit=1)
        self.assertNotEqual(po03,po02)

        withfreeze_time(dt.today()+td(days=2)):
            op_02.invalidate_cache(fnames=['lead_days_date'],ids=op_02.ids)
            op_02.action_replenish()
            self.assertEqual(po03.date_order,expected_order_date)
            self.assertRecordValues(po03.order_line,[
                {'product_id':self.product_01.id,'date_planned':expected_delivery_date},
                {'product_id':product_02.id,'date_planned':expected_delivery_date},
            ])

        #ResetandtrywithasecondRRexecutedafterthedatesrange(->shouldnotusetheexistingPO)
        po03.button_cancel()
        op_01.action_replenish()
        po04=self.env['purchase.order'].search([],order='iddesc',limit=1)
        self.assertNotEqual(po04,po03)

        withfreeze_time(dt.today()+td(days=3)):
            op_02.invalidate_cache(fnames=['lead_days_date'],ids=op_02.ids)
            op_02.action_replenish()
            self.assertEqual(po04.order_line.product_id,self.product_01,'Thereshouldbeonlyalineforproduct01')
            po05=self.env['purchase.order'].search([],order='iddesc',limit=1)
            self.assertNotEqual(po05,po04,'AnewPOshouldbegenerated')
            self.assertEqual(po05.order_line.product_id,product_02)
