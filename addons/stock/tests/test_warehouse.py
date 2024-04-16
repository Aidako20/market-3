#-*-coding:utf-8-*-

fromflectra.addons.stock.tests.common2importTestStockCommon
fromflectra.testsimportForm
fromflectra.exceptionsimportAccessError
fromflectra.toolsimportmute_logger


classTestWarehouse(TestStockCommon):

    defsetUp(self):
        super(TestWarehouse,self).setUp()
        self.partner=self.env['res.partner'].create({'name':'DecoAddict'})

    deftest_inventory_product(self):
        self.product_1.type='product'
        product_1_quant=self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_1.id,
            'inventory_quantity':50.0,
            'location_id':self.warehouse_1.lot_stock_id.id,
        })
        inventory=self.env['stock.inventory'].with_user(self.user_stock_manager).create({
            'name':'Startingforproduct_1',
            'location_ids':[(4,self.warehouse_1.lot_stock_id.id)],
            'product_ids':[(4,self.product_1.id)],
        })
        inventory.action_start()
        #Asdoneincommon.py,thereisalreadyaninventorylineexisting
        self.assertEqual(len(inventory.line_ids),1)
        self.assertEqual(inventory.line_ids.theoretical_qty,50.0)
        self.assertEqual(inventory.line_ids.product_id,self.product_1)
        self.assertEqual(inventory.line_ids.product_uom_id,self.product_1.uom_id)

        #Updatetheline,setto35
        inventory.line_ids.write({'product_qty':35.0})
        inventory.action_validate()

        #Checkrelatedmoveandquants
        self.assertIn(inventory.name,inventory.move_ids.name)
        self.assertEqual(inventory.move_ids.product_qty,15.0)
        self.assertEqual(inventory.move_ids.location_id,self.warehouse_1.lot_stock_id)
        self.assertEqual(inventory.move_ids.location_dest_id,self.product_1.property_stock_inventory) #Inventoryloss
        self.assertEqual(inventory.move_ids.state,'done')
        quants=self.env['stock.quant']._gather(self.product_1,self.product_1.property_stock_inventory)
        self.assertEqual(len(quants),1) #Onequantcreatedforinventoryloss

        #Checkquantityofproductinvariouslocations:current,itsparent,brotherandother
        self.assertEqual(self.env['stock.quant']._gather(self.product_1,self.warehouse_1.lot_stock_id).quantity,35.0)
        self.assertEqual(self.env['stock.quant']._gather(self.product_1,self.warehouse_1.lot_stock_id.location_id).quantity,35.0)
        self.assertEqual(self.env['stock.quant']._gather(self.product_1,self.warehouse_1.view_location_id).quantity,35.0)

        self.assertEqual(self.env['stock.quant']._gather(self.product_1,self.warehouse_1.wh_input_stock_loc_id).quantity,0.0)
        self.assertEqual(self.env['stock.quant']._gather(self.product_1,self.env.ref('stock.stock_location_stock')).quantity,0.0)

    deftest_inventory_wizard_as_manager(self):
        """Usingthe"UpdateQuantity"wizardasstockmanager.
        """
        self.product_1.type='product'
        InventoryWizard=self.env['stock.change.product.qty'].with_user(self.user_stock_manager)
        inventory_wizard=InventoryWizard.create({
            'product_id':self.product_1.id,
            'product_tmpl_id':self.product_1.product_tmpl_id.id,
            'new_quantity':50.0,
        })
        inventory_wizard.change_product_qty()
        #Checkquantitywasupdated
        self.assertEqual(self.product_1.virtual_available,50.0)
        self.assertEqual(self.product_1.qty_available,50.0)

        #Checkassociatedquants:2quantsfortheproductandthequantity(1instock,1ininventoryadjustment)
        quant=self.env['stock.quant'].search([('id','notin',self.existing_quants.ids)])
        self.assertEqual(len(quant),2)

    deftest_inventory_wizard_as_user(self):
        """Usingthe"UpdateQuantity"wizardasstockuser.
        """
        self.product_1.type='product'
        InventoryWizard=self.env['stock.change.product.qty'].with_user(self.user_stock_user)
        inventory_wizard=InventoryWizard.create({
            'product_id':self.product_1.id,
            'product_tmpl_id':self.product_1.product_tmpl_id.id,
            'new_quantity':50.0,
        })
        #Userhasnorightonquant,mustraiseanAccessError
        withself.assertRaises(AccessError):
            inventory_wizard.change_product_qty()
        #Checkquantitywasn'tupdated
        self.assertEqual(self.product_1.virtual_available,0.0)
        self.assertEqual(self.product_1.qty_available,0.0)

        #Checkassociatedquants:0quantexpected
        quant=self.env['stock.quant'].search([('id','notin',self.existing_quants.ids)])
        self.assertEqual(len(quant),0)

    deftest_basic_move(self):
        product=self.product_3.with_user(self.user_stock_manager)
        product.type='product'
        picking_out=self.env['stock.picking'].create({
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':self.warehouse_1.lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
        })
        customer_move=self.env['stock.move'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':5,
            'product_uom':product.uom_id.id,
            'picking_id':picking_out.id,
            'location_id':self.warehouse_1.lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
        })
        #simulatecreate+onchange
        #testmovevalues
        self.assertEqual(customer_move.product_uom,product.uom_id)
        self.assertEqual(customer_move.location_id,self.warehouse_1.lot_stock_id)
        self.assertEqual(customer_move.location_dest_id,self.env.ref('stock.stock_location_customers'))

        #confirmmove,checkquantityonhandandvirtuallyavailable,withoutlocationcontext
        customer_move._action_confirm()
        self.assertEqual(product.qty_available,0.0)
        self.assertEqual(product.virtual_available,-5.0)

        customer_move.quantity_done=5
        customer_move._action_done()
        self.assertEqual(product.qty_available,-5.0)

        #compensatenegativequantsbyreceivingproductsfromsupplier
        receive_move=self._create_move(product,self.env.ref('stock.stock_location_suppliers'),self.warehouse_1.lot_stock_id,product_uom_qty=15)

        receive_move._action_confirm()
        receive_move.quantity_done=15
        receive_move._action_done()

        product._compute_quantities()
        self.assertEqual(product.qty_available,10.0)
        self.assertEqual(product.virtual_available,10.0)

        #newmovetowardscustomer
        customer_move_2=self._create_move(product,self.warehouse_1.lot_stock_id,self.env.ref('stock.stock_location_customers'),product_uom_qty=2)

        customer_move_2._action_confirm()
        product._compute_quantities()
        self.assertEqual(product.qty_available,10.0)
        self.assertEqual(product.virtual_available,8.0)

        customer_move_2.quantity_done=2.0
        customer_move_2._action_done()
        product._compute_quantities()
        self.assertEqual(product.qty_available,8.0)

    deftest_inventory_adjustment_and_negative_quants_1(self):
        """Makesurenegativequantsfromreturnsgetwipedoutwithaninventoryadjustment"""
        productA=self.env['product.product'].create({'name':'ProductA','type':'product'})
        stock_location=self.env.ref('stock.stock_location_stock')
        customer_location=self.env.ref('stock.stock_location_customers')

        #Createapickingoutandforceavailability
        picking_out=self.env['stock.picking'].create({
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
        })
        self.env['stock.move'].create({
            'name':productA.name,
            'product_id':productA.id,
            'product_uom_qty':1,
            'product_uom':productA.uom_id.id,
            'picking_id':picking_out.id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
        })
        picking_out.action_confirm()
        picking_out.move_lines.quantity_done=1
        picking_out._action_done()

        quant=self.env['stock.quant'].search([('product_id','=',productA.id),('location_id','=',stock_location.id)])
        self.assertEqual(len(quant),1)
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_out.ids,active_id=picking_out.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=1.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.action_assign()
        return_pick.move_lines.quantity_done=1
        return_pick._action_done()

        quant=self.env['stock.quant'].search([('product_id','=',productA.id),('location_id','=',stock_location.id)])
        self.assertEqual(sum(quant.mapped('quantity')),0)

    deftest_inventory_adjustment_and_negative_quants_2(self):
        """Makesurenegativequantsgetwipedoutwithaninventoryadjustment"""
        productA=self.env['product.product'].create({'name':'ProductA','type':'product'})
        stock_location=self.env.ref('stock.stock_location_stock')
        customer_location=self.env.ref('stock.stock_location_customers')
        location_loss=productA.property_stock_inventory

        #Createapickingoutandforceavailability
        picking_out=self.env['stock.picking'].create({
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
        })
        self.env['stock.move'].create({
            'name':productA.name,
            'product_id':productA.id,
            'product_uom_qty':1,
            'product_uom':productA.uom_id.id,
            'picking_id':picking_out.id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
        })
        picking_out.action_confirm()
        picking_out.move_lines.quantity_done=1
        picking_out._action_done()

        #Makeaninventoryadjustmenttosetthequantityto0
        inventory=self.env['stock.inventory'].create({
            'name':'Startingforproduct_1',
            'location_ids':[(4,stock_location.id)],
            'product_ids':[(4,productA.id)],
        })
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids),1,"Wronginventorylinesgenerated.")
        self.assertEqual(inventory.line_ids.theoretical_qty,-1,"Theoreticalquantityshouldbe-1.")
        inventory.line_ids.product_qty=0 #Putthequantitybackto0
        inventory.action_validate()

        #Theinventoryadjustmentshouldhavecreatedone
        self.assertEqual(len(inventory.move_ids),1)
        quantity=inventory.move_ids.mapped('product_qty')
        self.assertEqual(quantity,[1],"Movescreatedwithwrongquantity.")
        location_ids=inventory.move_ids.mapped('location_id').ids
        self.assertEqual(set(location_ids),{location_loss.id})

        #Thereshouldbenoquantinthestocklocation
        quants=self.env['stock.quant'].search([('product_id','=',productA.id),('location_id','=',stock_location.id)])
        self.assertEqual(sum(quants.mapped('quantity')),0)

        #Thereshouldbeonequantintheinventorylosslocation
        quant=self.env['stock.quant'].search([('product_id','=',productA.id),('location_id','=',location_loss.id)])
        self.assertEqual(len(quant),1)

    deftest_resupply_route(self):
        """Simulatearesupplychainbetweenwarehouses.
        Stock->transit->Dist.->transit->Shop->Customer
        CreatethemovefromShoptoCustomerandensurethatallthepull
        rulesaretriggeredinordertocompletethemovechaintoStock.
        """
        warehouse_stock=self.env['stock.warehouse'].create({
            'name':'Stock.',
            'code':'STK',
        })

        distribution_partner=self.env['res.partner'].create({'name':'DistributionCenter'})
        warehouse_distribution=self.env['stock.warehouse'].create({
            'name':'Dist.',
            'code':'DIST',
            'resupply_wh_ids':[(6,0,[warehouse_stock.id])],
            'partner_id':distribution_partner.id,
        })

        warehouse_shop=self.env['stock.warehouse'].create({
            'name':'Shop',
            'code':'SHOP',
            'resupply_wh_ids':[(6,0,[warehouse_distribution.id])]
        })

        route_stock_to_dist=warehouse_distribution.resupply_route_ids
        route_dist_to_shop=warehouse_shop.resupply_route_ids

        #Changetheprocure_methodonthepullrulesbetweendistandshop
        #warehouses.Sincemtoandresupplyroutesarebothonproductitwill
        #selectonerandomlybetweenthemandifitselecttheresupplyitis
        #'maketostock'anditwillnotcreatethepickingbetweenstockand
        #distwarehouses.
        route_dist_to_shop.rule_ids.write({'procure_method':'make_to_order'})

        product=self.env['product.product'].create({
            'name':'Fakir',
            'type':'product',
            'route_ids':[(4,route_id)forroute_idin[route_stock_to_dist.id,route_dist_to_shop.id,self.env.ref('stock.route_warehouse0_mto').id]],
        })

        picking_out=self.env['stock.picking'].create({
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':warehouse_shop.lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
        })
        self.env['stock.move'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':1,
            'product_uom':product.uom_id.id,
            'picking_id':picking_out.id,
            'location_id':warehouse_shop.lot_stock_id.id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'warehouse_id':warehouse_shop.id,
            'procure_method':'make_to_order',
        })
        picking_out.action_confirm()

        moves=self.env['stock.move'].search([('product_id','=',product.id)])
        #Shop/Stock->Customer
        #Transit->Shop/Stock
        #Dist/Stock->Transit
        #Transit->Dist/Stock
        #Stock/Stock->Transit
        self.assertEqual(len(moves),5,'Invalidmovesnumber.')
        self.assertTrue(self.env['stock.move'].search([('location_id','=',warehouse_stock.lot_stock_id.id)]))
        self.assertTrue(self.env['stock.move'].search([('location_dest_id','=',warehouse_distribution.lot_stock_id.id)]))
        self.assertTrue(self.env['stock.move'].search([('location_id','=',warehouse_distribution.lot_stock_id.id)]))
        self.assertTrue(self.env['stock.move'].search([('location_dest_id','=',warehouse_shop.lot_stock_id.id)]))
        self.assertTrue(self.env['stock.move'].search([('location_id','=',warehouse_shop.lot_stock_id.id)]))

        self.assertTrue(self.env['stock.picking'].search([('location_id','=',self.env.company.internal_transit_location_id.id),('partner_id','=',distribution_partner.id)]))
        self.assertTrue(self.env['stock.picking'].search([('location_dest_id','=',self.env.company.internal_transit_location_id.id),('partner_id','=',distribution_partner.id)]))

    deftest_mutiple_resupply_warehouse(self):
        """Simulatethefollowingsituation:
        -2shopswithstockareresupplyby2distinctwarehouses
        -ShopNamurisresupplybythewarehousestockNamur
        -ShopWavreisresupplybythewarehousestockWavre
        -Simulate2movesforthesameproductbutindifferentshop.
        Thistestensurethatthemovearesuppliedbythecorrectdistribution
        warehouse.
        """
        customer_location=self.env.ref('stock.stock_location_customers')

        warehouse_distribution_wavre=self.env['stock.warehouse'].create({
            'name':'StockWavre.',
            'code':'WV',
        })

        warehouse_shop_wavre=self.env['stock.warehouse'].create({
            'name':'ShopWavre',
            'code':'SHWV',
            'resupply_wh_ids':[(6,0,[warehouse_distribution_wavre.id])]
        })

        warehouse_distribution_namur=self.env['stock.warehouse'].create({
            'name':'StockNamur.',
            'code':'NM',
        })

        warehouse_shop_namur=self.env['stock.warehouse'].create({
            'name':'ShopNamur',
            'code':'SHNM',
            'resupply_wh_ids':[(6,0,[warehouse_distribution_namur.id])]
        })

        route_shop_namur=warehouse_shop_namur.resupply_route_ids
        route_shop_wavre=warehouse_shop_wavre.resupply_route_ids
        #Theproductcontainsthe2resupplyroutes.
        product=self.env['product.product'].create({
            'name':'Fakir',
            'type':'product',
            'route_ids':[(4,route_id)forroute_idin[route_shop_namur.id,route_shop_wavre.id,self.env.ref('stock.route_warehouse0_mto').id]],
        })

        #Add1quantineachdistributionwarehouse.
        self.env['stock.quant']._update_available_quantity(product,warehouse_distribution_wavre.lot_stock_id,1.0)
        self.env['stock.quant']._update_available_quantity(product,warehouse_distribution_namur.lot_stock_id,1.0)

        #CreatethemovefortheshopNamur.Shouldcreatearesupplyfrom
        #distributionwarehouseNamur.
        picking_out_namur=self.env['stock.picking'].create({
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':warehouse_shop_namur.lot_stock_id.id,
            'location_dest_id':customer_location.id,
        })
        self.env['stock.move'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':1,
            'product_uom':product.uom_id.id,
            'picking_id':picking_out_namur.id,
            'location_id':warehouse_shop_namur.lot_stock_id.id,
            'location_dest_id':customer_location.id,
            'warehouse_id':warehouse_shop_namur.id,
            'procure_method':'make_to_order',
        })
        picking_out_namur.action_confirm()

        #Validatethepicking
        #Dist.warehouseNamur->transitLocation->ShopNamur
        picking_stock_transit=self.env['stock.picking'].search([('location_id','=',warehouse_distribution_namur.lot_stock_id.id)])
        self.assertTrue(picking_stock_transit)
        picking_stock_transit.action_assign()
        picking_stock_transit.move_lines[0].quantity_done=1.0
        picking_stock_transit._action_done()

        picking_transit_shop_namur=self.env['stock.picking'].search([('location_dest_id','=',warehouse_shop_namur.lot_stock_id.id)])
        self.assertTrue(picking_transit_shop_namur)
        picking_transit_shop_namur.action_assign()
        picking_transit_shop_namur.move_lines[0].quantity_done=1.0
        picking_transit_shop_namur._action_done()

        picking_out_namur.action_assign()
        picking_out_namur.move_lines[0].quantity_done=1.0
        picking_out_namur._action_done()

        #Checkthatthecorrectquantityhasbeenprovidedtocustomer
        self.assertEqual(self.env['stock.quant']._gather(product,customer_location).quantity,1)
        #Ensuretherestillnoquantsindistributionwarehouse
        self.assertEqual(sum(self.env['stock.quant']._gather(product,warehouse_distribution_namur.lot_stock_id).mapped('quantity')),0)

        #CreatethemovefortheshopWavre.Shouldcreatearesupplyfrom
        #distributionwarehouseWavre.
        picking_out_wavre=self.env['stock.picking'].create({
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':warehouse_shop_wavre.lot_stock_id.id,
            'location_dest_id':customer_location.id,
        })
        self.env['stock.move'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':1,
            'product_uom':product.uom_id.id,
            'picking_id':picking_out_wavre.id,
            'location_id':warehouse_shop_wavre.lot_stock_id.id,
            'location_dest_id':customer_location.id,
            'warehouse_id':warehouse_shop_wavre.id,
            'procure_method':'make_to_order',
        })
        picking_out_wavre.action_confirm()

        #Validatethepicking
        #Dist.warehouseWavre->transitLocation->ShopWavre
        picking_stock_transit=self.env['stock.picking'].search([('location_id','=',warehouse_distribution_wavre.lot_stock_id.id)])
        self.assertTrue(picking_stock_transit)
        picking_stock_transit.action_assign()
        picking_stock_transit.move_lines[0].quantity_done=1.0
        picking_stock_transit._action_done()

        picking_transit_shop_wavre=self.env['stock.picking'].search([('location_dest_id','=',warehouse_shop_wavre.lot_stock_id.id)])
        self.assertTrue(picking_transit_shop_wavre)
        picking_transit_shop_wavre.action_assign()
        picking_transit_shop_wavre.move_lines[0].quantity_done=1.0
        picking_transit_shop_wavre._action_done()

        picking_out_wavre.action_assign()
        picking_out_wavre.move_lines[0].quantity_done=1.0
        picking_out_wavre._action_done()

        #Checkthatthecorrectquantityhasbeenprovidedtocustomer
        self.assertEqual(self.env['stock.quant']._gather(product,customer_location).quantity,2)
        #Ensuretherestillnoquantsindistributionwarehouse
        self.assertEqual(sum(self.env['stock.quant']._gather(product,warehouse_distribution_wavre.lot_stock_id).mapped('quantity')),0)

    deftest_noleak(self):
        #non-regressiontesttoavoidcompany_idleakingtootherwarehouses(seeblame)
        partner=self.env['res.partner'].create({'name':'Chicagopartner'})
        company=self.env['res.company'].create({
            'name':'MyCompany(Chicago)1',
            'currency_id':self.ref('base.USD')
        })
        self.env['stock.warehouse'].create({
            'name':'ChicagoWarehouse2',
            'company_id':company.id,
            'code':'Chic2',
            'partner_id':partner.id
        })
        wh=self.env["stock.warehouse"].search([])

        assertlen(set(wh.mapped("company_id.id")))>1

        companies_before=wh.mapped(lambdaw:(w.id,w.company_id))
        #writingonanyfieldshouldchangethecompanyofwarehouses
        wh.write({"name":"whatever"})
        companies_after=wh.mapped(lambdaw:(w.id,w.company_id))

        self.assertEqual(companies_after,companies_before)

    deftest_toggle_active_warehouse_1(self):
        """Basictestthatcreateawarehousewithclassicconfiguration.
        Archiveitandcheckthatlocations,pickingtypes,routes,rulesare
        correcltyactiveorarchive.
        """
        wh=Form(self.env['stock.warehouse'])
        wh.name="TheatticofWilly"
        wh.code="WIL"
        warehouse=wh.save()

        custom_location=Form(self.env['stock.location'])
        custom_location.name="ATrunk"
        custom_location.location_id=warehouse.lot_stock_id
        custom_location=custom_location.save()

        #Archivewarehouse
        warehouse.toggle_active()
        #Globalrule
        self.assertFalse(warehouse.mto_pull_id.active)

        #Route
        self.assertFalse(warehouse.reception_route_id.active)
        self.assertFalse(warehouse.delivery_route_id.active)

        #Location
        self.assertFalse(warehouse.lot_stock_id.active)
        self.assertFalse(warehouse.wh_input_stock_loc_id.active)
        self.assertFalse(warehouse.wh_qc_stock_loc_id.active)
        self.assertFalse(warehouse.wh_output_stock_loc_id.active)
        self.assertFalse(warehouse.wh_pack_stock_loc_id.active)
        self.assertFalse(custom_location.active)

        #PickingType
        self.assertFalse(warehouse.in_type_id.active)
        self.assertFalse(warehouse.in_type_id.show_operations)
        self.assertFalse(warehouse.out_type_id.active)
        self.assertFalse(warehouse.int_type_id.active)
        self.assertFalse(warehouse.pick_type_id.active)
        self.assertFalse(warehouse.pack_type_id.active)

        #Activewarehouse
        warehouse.toggle_active()
        #Globalrule
        self.assertTrue(warehouse.mto_pull_id.active)

        #Route
        self.assertTrue(warehouse.reception_route_id.active)
        self.assertTrue(warehouse.delivery_route_id.active)

        #Location
        self.assertTrue(warehouse.lot_stock_id.active)
        self.assertFalse(warehouse.wh_input_stock_loc_id.active)
        self.assertFalse(warehouse.wh_qc_stock_loc_id.active)
        self.assertFalse(warehouse.wh_output_stock_loc_id.active)
        self.assertFalse(warehouse.wh_pack_stock_loc_id.active)
        self.assertTrue(custom_location.active)

        #PickingType
        self.assertTrue(warehouse.in_type_id.active)
        self.assertFalse(warehouse.in_type_id.show_operations)
        self.assertTrue(warehouse.out_type_id.active)
        self.assertTrue(warehouse.int_type_id.active)
        self.assertFalse(warehouse.pick_type_id.active)
        self.assertFalse(warehouse.pack_type_id.active)

    deftest_toggle_active_warehouse_2(self):
        wh=Form(self.env['stock.warehouse'])
        wh.name="TheatticofWilly"
        wh.code="WIL"
        wh.reception_steps="two_steps"
        wh.delivery_steps="pick_pack_ship"
        warehouse=wh.save()

        warehouse.resupply_wh_ids=[(6,0,[self.warehouse_1.id])]

        custom_location=Form(self.env['stock.location'])
        custom_location.name="ATrunk"
        custom_location.location_id=warehouse.lot_stock_id
        custom_location=custom_location.save()

        #Addawarehouseontheroute.
        warehouse.reception_route_id.write({
            'warehouse_ids':[(4,self.warehouse_1.id)]
        })

        route=Form(self.env['stock.location.route'])
        route.name="Stair"
        route=route.save()

        route.warehouse_ids=[(6,0,[warehouse.id,self.warehouse_1.id])]

        #Prearchivealocationandaroute
        warehouse.delivery_route_id.toggle_active()
        warehouse.wh_pack_stock_loc_id.toggle_active()

        #Archivewarehouse
        warehouse.toggle_active()
        #Globalrule
        self.assertFalse(warehouse.mto_pull_id.active)

        #Route
        self.assertTrue(warehouse.reception_route_id.active)
        self.assertFalse(warehouse.delivery_route_id.active)
        self.assertTrue(route.active)

        #Location
        self.assertFalse(warehouse.lot_stock_id.active)
        self.assertFalse(warehouse.wh_input_stock_loc_id.active)
        self.assertFalse(warehouse.wh_qc_stock_loc_id.active)
        self.assertFalse(warehouse.wh_output_stock_loc_id.active)
        self.assertFalse(warehouse.wh_pack_stock_loc_id.active)
        self.assertFalse(custom_location.active)

        #PickingType
        self.assertFalse(warehouse.in_type_id.active)
        self.assertFalse(warehouse.out_type_id.active)
        self.assertFalse(warehouse.int_type_id.active)
        self.assertFalse(warehouse.pick_type_id.active)
        self.assertFalse(warehouse.pack_type_id.active)

        #Activewarehouse
        warehouse.toggle_active()
        #Globalrule
        self.assertTrue(warehouse.mto_pull_id.active)

        #Route
        self.assertTrue(warehouse.reception_route_id.active)
        self.assertTrue(warehouse.delivery_route_id.active)

        #Location
        self.assertTrue(warehouse.lot_stock_id.active)
        self.assertTrue(warehouse.wh_input_stock_loc_id.active)
        self.assertFalse(warehouse.wh_qc_stock_loc_id.active)
        self.assertTrue(warehouse.wh_output_stock_loc_id.active)
        self.assertTrue(warehouse.wh_pack_stock_loc_id.active)
        self.assertTrue(custom_location.active)

        #PickingType
        self.assertTrue(warehouse.in_type_id.active)
        self.assertTrue(warehouse.out_type_id.active)
        self.assertTrue(warehouse.int_type_id.active)
        self.assertTrue(warehouse.pick_type_id.active)
        self.assertTrue(warehouse.pack_type_id.active)

    deftest_edit_warehouse_1(self):
        wh=Form(self.env['stock.warehouse'])
        wh.name="Chicago"
        wh.code="chic"
        warehouse=wh.save()
        self.assertEqual(warehouse.int_type_id.barcode,'CHIC-INTERNAL')
        self.assertEqual(warehouse.int_type_id.sequence_id.prefix,'chic/INT/')

        wh=Form(warehouse)
        wh.code='CH'
        wh.save()
        self.assertEqual(warehouse.int_type_id.barcode,'CH-INTERNAL')
        self.assertEqual(warehouse.int_type_id.sequence_id.prefix,'CH/INT/')
