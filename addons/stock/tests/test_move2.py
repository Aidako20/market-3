#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectra.addons.stock.tests.commonimportTestStockCommon
fromflectra.exceptionsimportUserError

fromflectra.testsimportForm
fromflectra.toolsimportfloat_is_zero,float_compare

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

classTestPickShip(TestStockCommon):
    defcreate_pick_ship(self):
        picking_client=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })

        dest=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_client.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'state':'waiting',
            'procure_method':'make_to_order',
        })

        picking_pick=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'picking_type_id':self.picking_type_out,
        })

        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_pick.id,
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'move_dest_ids':[(4,dest.id)],
            'state':'confirmed',
        })
        returnpicking_pick,picking_client

    defcreate_pick_pack_ship(self):
        picking_ship=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })

        ship=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_ship.id,
            'location_id':self.output_location,
            'location_dest_id':self.customer_location,
        })

        picking_pack=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'picking_type_id':self.picking_type_out,
        })

        pack=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_pack.id,
            'location_id':self.pack_location,
            'location_dest_id':self.output_location,
            'move_dest_ids':[(4,ship.id)],
        })

        picking_pick=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'picking_type_id':self.picking_type_out,
        })

        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_pick.id,
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'move_dest_ids':[(4,pack.id)],
            'state':'confirmed',
        })
        returnpicking_pick,picking_pack,picking_ship

    deftest_unreserve_only_required_quantity(self):
        product_unreserve=self.env['product.product'].create({
            'name':'productunreserve',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(product_unreserve,stock_location,4.0)
        quants=self.env['stock.quant']._gather(product_unreserve,stock_location,strict=True)
        self.assertEqual(quants[0].reserved_quantity,0)
        move=self.MoveObj.create({
            'name':product_unreserve.name,
            'product_id':product_unreserve.id,
            'product_uom_qty':3,
            'product_uom':product_unreserve.uom_id.id,
            'state':'confirmed',
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        move._action_assign()
        self.assertEqual(quants[0].reserved_quantity,3)
        move_2=self.MoveObj.create({
            'name':product_unreserve.name,
            'product_id':product_unreserve.id,
            'product_uom_qty':2,
            'quantity_done':2,
            'product_uom':product_unreserve.uom_id.id,
            'state':'confirmed',
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        move_2._action_assign()
        move_2._action_done()
        quants=self.env['stock.quant']._gather(product_unreserve,stock_location,strict=True)
        self.assertEqual(quants[0].reserved_quantity,2)


    deftest_mto_moves(self):
        """
            10instock,dopick->shipandcheckshipisassignedwhenpickisdone,thenbackorderofship
        """
        picking_pick,picking_client=self.create_pick_ship()
        location=self.env['stock.location'].browse(self.stock_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.productA,location,10.0)
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()

        self.assertEqual(picking_client.state,'assigned','Thestateoftheclientshouldbeassigned')

        #Nowpartiallytransfertheship
        picking_client.move_lines[0].move_line_ids[0].qty_done=5
        picking_client._action_done() #nonewinordertocreatebackorder

        backorder=self.env['stock.picking'].search([('backorder_id','=',picking_client.id)])
        self.assertEqual(backorder.state,'assigned','Backordershouldbestarted')

    deftest_mto_moves_transfer(self):
        """
            10instock,5inpack. Makesureitdoesnotassignthe5piecesinpack
        """
        picking_pick,picking_client=self.create_pick_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0)
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,5.0)

        self.assertEqual(len(self.env['stock.quant']._gather(self.productA,stock_location)),1.0)
        self.assertEqual(len(self.env['stock.quant']._gather(self.productA,pack_location)),1.0)

        (picking_pick+picking_client).action_assign()

        move_pick=picking_pick.move_lines
        move_cust=picking_client.move_lines
        self.assertEqual(move_pick.state,'assigned')
        self.assertEqual(picking_pick.state,'assigned')
        self.assertEqual(move_cust.state,'waiting')
        self.assertEqual(picking_client.state,'waiting','Thepickingshouldnotassignwhatitdoesnothave')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),5.0)

        move_pick.move_line_ids[0].qty_done=10.0
        picking_pick._action_done()

        self.assertEqual(move_pick.state,'done')
        self.assertEqual(picking_pick.state,'done')
        self.assertEqual(move_cust.state,'assigned')
        self.assertEqual(picking_client.state,'assigned','Thepickingshouldnotassignwhatitdoesnothave')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),5.0)
        self.assertEqual(sum(self.env['stock.quant']._gather(self.productA,stock_location).mapped('quantity')),0.0)
        self.assertEqual(len(self.env['stock.quant']._gather(self.productA,pack_location)),1.0)

    deftest_mto_moves_return(self):
        picking_pick,picking_client=self.create_pick_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0)

        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()
        self.assertEqual(picking_pick.state,'done')
        self.assertEqual(picking_client.state,'assigned')

        #returnapartofwhatwe'vedone
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_pick.ids,active_id=picking_pick.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=2.0 #Returnonly2
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done=2.0
        return_pick._action_done()
        #theclientpickingshouldnotbeassignedanymore,aswereturnedpartiallywhatwetook
        self.assertEqual(picking_client.state,'confirmed')

    deftest_mto_moves_extra_qty(self):
        """EnsurethatamoveinMTOwillsupportanextraquantity.Theextra
        moveshouldbecreatedinMTSandshouldnotbemergedintheinitial
        moveifit'sinMTO.Itshouldalsoavoidtotriggertherules.
        """
        picking_pick,picking_client=self.create_pick_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.productA.write({'route_ids':[(4,self.env.ref('stock.route_warehouse0_mto').id)]})
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0)
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=15.0
        picking_pick._action_done()
        self.assertEqual(picking_pick.state,'done')
        self.assertEqual(picking_client.state,'assigned')

        picking_client.move_lines[0].move_line_ids[0].qty_done=15.0
        picking_client.move_lines._action_done()
        self.assertEqual(len(picking_client.move_lines),2)
        move_lines=picking_client.move_lines.sorted()
        self.assertEqual(move_lines.mapped('procure_method'),['make_to_order','make_to_stock'])
        self.assertEqual(move_lines.mapped('product_uom_qty'),[10.0,5.0])

    deftest_mto_moves_return_extra(self):
        picking_pick,picking_client=self.create_pick_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0)

        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()
        self.assertEqual(picking_pick.state,'done')
        self.assertEqual(picking_client.state,'assigned')

        #returnmorethanwe'vedone
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_pick.ids,active_id=picking_pick.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=12.0#Return2extra
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        #Verifytheextramovehasbeenmergedwiththeoriginalmove
        self.assertAlmostEqual(return_pick.move_lines.product_uom_qty,12.0)
        self.assertAlmostEqual(return_pick.move_lines.quantity_done,0.0)
        self.assertAlmostEqual(return_pick.move_lines.reserved_availability,10.0)

    deftest_mto_resupply_cancel_ship(self):
        """Thistestsimulatesapickpackshipwitharesupplyroute
        set.Pickandpackarevalidated,shipiscancelled.Thistest
        ensurethatnewpickingarenotcreatedfromthecancelled
        shipaftertheschedulertask.Thesupplyrouteisonlysetin
        ordertomaketheschedulerrunwithoutmistakes(nonext
        activity).
        """
        picking_pick,picking_pack,picking_ship=self.create_pick_pack_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse_1.write({'delivery_steps':'pick_pack_ship'})
        warehouse_2=self.env['stock.warehouse'].create({
            'name':'SmallWarehouse',
            'code':'SWH'
        })
        warehouse_1.write({
            'resupply_wh_ids':[(6,0,[warehouse_2.id])]
        })
        resupply_route=self.env['stock.location.route'].search([('supplier_wh_id','=',warehouse_2.id),('supplied_wh_id','=',warehouse_1.id)])
        self.assertTrue(resupply_route)
        self.productA.write({'route_ids':[(4,resupply_route.id),(4,self.env.ref('stock.route_warehouse0_mto').id)]})

        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0)

        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()

        picking_pack.action_assign()
        picking_pack.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pack._action_done()

        picking_ship.action_cancel()
        picking_ship.move_lines.write({'procure_method':'make_to_order'})

        self.env['procurement.group'].run_scheduler()
        next_activity=self.env['mail.activity'].search([('res_model','=','product.template'),('res_id','=',self.productA.product_tmpl_id.id)])
        self.assertEqual(picking_ship.state,'cancel')
        self.assertFalse(next_activity,'Ifanextactivityhasbeencreatedifmeansthatschedulerfailed\
        andtheendofthistestdonothavesense.')
        self.assertEqual(len(picking_ship.move_lines.mapped('move_orig_ids')),0,
        'Schedulershouldnotcreatepickingpackandpicksinceshiphasbeenmanuallycancelled.')

    deftest_no_backorder_1(self):
        """Checkthebehaviorofdoinglessthanaskedinthepickingpickandchosingnotto
        createabackorder.Inthisbehavior,thesecondpickingshouldobviouslyonlybeableto
        reservewhatwasbrought,butitsinitialdemandshouldstaythesameandthesystemwill
        asktheuserwillhavetoconsideragainifhewantstocreateabackorderornot.
        """
        picking_pick,picking_client=self.create_pick_ship()
        location=self.env['stock.location'].browse(self.stock_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.productA,location,10.0)
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=5.0

        #createabackorder
        picking_pick._action_done()
        picking_pick_backorder=self.env['stock.picking'].search([('backorder_id','=',picking_pick.id)])
        self.assertEqual(picking_pick_backorder.state,'assigned')
        self.assertEqual(picking_pick_backorder.move_lines.product_qty,5.0)

        self.assertEqual(picking_client.state,'assigned')

        #cancelthebackorder
        picking_pick_backorder.action_cancel()
        self.assertEqual(picking_client.state,'assigned')

    deftest_edit_done_chained_move(self):
        """Let’ssaytwomovesarechained:thefirstisdoneandthesecondisassigned.
        Editingthemovelineofthefirstmoveshouldimpactthereservationofthesecondone.
        """
        picking_pick,picking_client=self.create_pick_ship()
        location=self.env['stock.location'].browse(self.stock_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.productA,location,10.0)
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()

        self.assertEqual(picking_pick.state,'done','Thestateofthepickshouldbedone')
        self.assertEqual(picking_client.state,'assigned','Thestateoftheclientshouldbeassigned')
        self.assertEqual(picking_pick.move_lines.quantity_done,10.0,'Wrongquantity_doneforpickmove')
        self.assertEqual(picking_client.move_lines.product_qty,10.0,'Wronginitialdemandforclientmove')
        self.assertEqual(picking_client.move_lines.reserved_availability,10.0,'Wrongquantityalreadyreservedforclientmove')

        picking_pick.move_lines[0].move_line_ids[0].qty_done=5.0
        self.assertEqual(picking_pick.state,'done','Thestateofthepickshouldbedone')
        self.assertEqual(picking_client.state,'assigned','Thestateoftheclientshouldbepartiallyavailable')
        self.assertEqual(picking_pick.move_lines.quantity_done,5.0,'Wrongquantity_doneforpickmove')
        self.assertEqual(picking_client.move_lines.product_qty,10.0,'Wronginitialdemandforclientmove')
        self.assertEqual(picking_client.move_lines.reserved_availability,5.0,'Wrongquantityalreadyreservedforclientmove')

        #Checkifrunaction_assigndoesnotcrash
        picking_client.action_assign()

    deftest_edit_done_chained_move_with_lot(self):
        """Let’ssaytwomovesarechained:thefirstisdoneandthesecondisassigned.
        Editingthelotonthemovelineofthefirstmoveshouldimpactthereservationofthesecondone.
        """
        self.productA.tracking='lot'
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        picking_pick,picking_client=self.create_pick_ship()
        location=self.env['stock.location'].browse(self.stock_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.productA,location,10.0)
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].write({
            'qty_done':10.0,
            'lot_id':lot1.id,
        })
        picking_pick._action_done()

        self.assertEqual(picking_pick.state,'done','Thestateofthepickshouldbedone')
        self.assertEqual(picking_client.state,'assigned','Thestateoftheclientshouldbeassigned')
        self.assertEqual(picking_pick.move_lines.quantity_done,10.0,'Wrongquantity_doneforpickmove')
        self.assertEqual(picking_client.move_lines.product_qty,10.0,'Wronginitialdemandforclientmove')
        self.assertEqual(picking_client.move_lines.move_line_ids.lot_id,lot1,'Wronglotforclientmoveline')
        self.assertEqual(picking_client.move_lines.reserved_availability,10.0,'Wrongquantityalreadyreservedforclientmove')

        picking_pick.move_lines[0].move_line_ids[0].lot_id=lot2.id
        self.assertEqual(picking_pick.state,'done','Thestateofthepickshouldbedone')
        self.assertEqual(picking_client.state,'assigned','Thestateoftheclientshouldbepartiallyavailable')
        self.assertEqual(picking_pick.move_lines.quantity_done,10.0,'Wrongquantity_doneforpickmove')
        self.assertEqual(picking_client.move_lines.product_qty,10.0,'Wronginitialdemandforclientmove')
        self.assertEqual(picking_client.move_lines.move_line_ids.lot_id,lot2,'Wronglotforclientmoveline')
        self.assertEqual(picking_client.move_lines.reserved_availability,10.0,'Wrongquantityalreadyreservedforclientmove')

        #Checkifrunaction_assigndoesnotcrash
        picking_client.action_assign()

    deftest_chained_move_with_uom(self):
        """Createpickshipwithadifferentuomthantheonceusedforquant.
        Checkthatreservedquantityandflowworkcorrectly.
        """
        picking_client=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        dest=self.MoveObj.create({
            'name':self.gB.name,
            'product_id':self.gB.id,
            'product_uom_qty':5,
            'product_uom':self.uom_kg.id,
            'picking_id':picking_client.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'state':'waiting',
        })

        picking_pick=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'picking_type_id':self.picking_type_out,
        })

        self.MoveObj.create({
            'name':self.gB.name,
            'product_id':self.gB.id,
            'product_uom_qty':5,
            'product_uom':self.uom_kg.id,
            'picking_id':picking_pick.id,
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'move_dest_ids':[(4,dest.id)],
            'state':'confirmed',
        })
        location=self.env['stock.location'].browse(self.stock_location)
        pack_location=self.env['stock.location'].browse(self.pack_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.gB,location,10000.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.gB,pack_location),0.0)
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=5.0
        picking_pick._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.gB,location),5000.0)
        self.assertEqual(self.env['stock.quant']._gather(self.gB,pack_location).quantity,5000.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.gB,pack_location),0.0)
        self.assertEqual(picking_client.state,'assigned')
        self.assertEqual(picking_client.move_lines.reserved_availability,5.0)

    deftest_pick_ship_return(self):
        """Createpickandship.Bringitotthecustomerandthenreturn
        ittostock.Thistestcheckthestateandthequantityaftereachmovein
        ordertoensurethatitiscorrect.
        """
        picking_pick,picking_ship=self.create_pick_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        pack_location=self.env['stock.location'].browse(self.pack_location)
        customer_location=self.env['stock.location'].browse(self.customer_location)
        self.productA.tracking='lot'
        lot=self.env['stock.production.lot'].create({
            'product_id':self.productA.id,
            'name':'123456789',
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0,lot_id=lot)

        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()
        self.assertEqual(picking_pick.state,'done')
        self.assertEqual(picking_ship.state,'assigned')

        picking_ship.action_assign()
        picking_ship.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_ship._action_done()

        customer_quantity=self.env['stock.quant']._get_available_quantity(self.productA,customer_location,lot_id=lot)
        self.assertEqual(customer_quantity,10,'Itshouldbeoneproductincustomer')

        """Firstwecreatethereturnpickingforpickpinking.
        Sincewedonothavecreatedthereturnbetweencustomerand
        output.Thisreturnshouldnotbeavailableandshouldonlyhave
        pickingpickasoriginmove.
        """
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_pick.ids,active_id=picking_pick.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=10.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick_picking=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        self.assertEqual(return_pick_picking.state,'waiting')

        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_ship.ids,active_id=picking_ship.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=10.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_ship_picking=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        self.assertEqual(return_ship_picking.state,'assigned','Returnshippickingshouldautomaticallybeassigned')
        """Wecreatedthereturnforshippicking.Theorigin/destination
        linkbetweenreturnmovesshouldhavebeencreatedduringreturncreation.
        """
        self.assertTrue(return_ship_picking.move_linesinreturn_pick_picking.move_lines.mapped('move_orig_ids'),
                        'Thepickreturnpicking\'smovesshouldhavetheshipreturnpicking\'smovesasorigin')

        self.assertTrue(return_pick_picking.move_linesinreturn_ship_picking.move_lines.mapped('move_dest_ids'),
                        'Theshipreturnpicking\'smovesshouldhavethepickreturnpicking\'smovesasdestination')

        return_ship_picking.move_lines[0].move_line_ids[0].write({
            'qty_done':10.0,
            'lot_id':lot.id,
        })
        return_ship_picking._action_done()
        self.assertEqual(return_ship_picking.state,'done')
        self.assertEqual(return_pick_picking.state,'assigned')

        customer_quantity=self.env['stock.quant']._get_available_quantity(self.productA,customer_location,lot_id=lot)
        self.assertEqual(customer_quantity,0,'Itshouldbeoneproductincustomer')

        pack_quantity=self.env['stock.quant']._get_available_quantity(self.productA,pack_location,lot_id=lot)
        self.assertEqual(pack_quantity,0,'Itshouldbeoneproductinpacklocationbutisreserved')

        #Shouldusepreviousmovelot.
        return_pick_picking.move_lines[0].move_line_ids[0].qty_done=10.0
        return_pick_picking._action_done()
        self.assertEqual(return_pick_picking.state,'done')

        stock_quantity=self.env['stock.quant']._get_available_quantity(self.productA,stock_location,lot_id=lot)
        self.assertEqual(stock_quantity,10,'Theproductisnotbackinstock')

    deftest_pick_pack_ship_return(self):
        """Thistestdoapickpackshipdeliverytocustomerandthen
        returnittostock.Onceeverythingisdone,thistestwillcheck
        ifallthelinkorgini/destinationbetweenmovesarecorrect.
        """
        picking_pick,picking_pack,picking_ship=self.create_pick_pack_ship()
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.productA.tracking='serial'
        lot=self.env['stock.production.lot'].create({
            'product_id':self.productA.id,
            'name':'123456789',
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,1.0,lot_id=lot)

        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=1.0
        picking_pick._action_done()

        picking_pack.action_assign()
        picking_pack.move_lines[0].move_line_ids[0].qty_done=1.0
        picking_pack._action_done()

        picking_ship.action_assign()
        picking_ship.move_lines[0].move_line_ids[0].qty_done=1.0
        picking_ship._action_done()

        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_ship.ids,active_id=picking_ship.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=1.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_ship_picking=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        return_ship_picking.move_lines[0].move_line_ids[0].write({
            'qty_done':1.0,
            'lot_id':lot.id,
        })
        return_ship_picking._action_done()

        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_pack.ids,active_id=picking_pack.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=1.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pack_picking=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        return_pack_picking.move_lines[0].move_line_ids[0].qty_done=1.0
        return_pack_picking._action_done()

        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_pick.ids,active_id=picking_pick.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=1.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick_picking=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        return_pick_picking.move_lines[0].move_line_ids[0].qty_done=1.0
        return_pick_picking._action_done()

        #Nowthateverythingisreturnedwewillcheckifthereturnmovesarecorrectlylinkedbetweenthem.
        #+--------------------------------------------------------------------------------------------------------+
        #|        --picking_pick(1)-->      --picking_pack(2)-->        --picking_ship(3)-->
        #|Stock                         Pack                        Output                         Customer
        #|        <---returnpick(6)--     <---returnpack(5)--         <---returnship(4)--
        #+--------------------------------------------------------------------------------------------------------+
        #Recapsoffinallink(MO=move_orig_ids,MD=move_dest_ids)
        #picking_pick(1):MO=(),MD=(2,6)
        #picking_pack(2):MO=(1),MD=(3,5)
        #pickingship(3):MO=(2),MD=(4)
        #returnship(4):MO=(3),MD=(5)
        #returnpack(5):MO=(2,4),MD=(6)
        #returnpick(6):MO=(1,5),MD=()

        self.assertEqual(len(picking_pick.move_lines.move_orig_ids),0,'Pickingpickshouldnothaveoriginmoves')
        self.assertEqual(set(picking_pick.move_lines.move_dest_ids.ids),set((picking_pack.move_lines|return_pick_picking.move_lines).ids))

        self.assertEqual(set(picking_pack.move_lines.move_orig_ids.ids),set(picking_pick.move_lines.ids))
        self.assertEqual(set(picking_pack.move_lines.move_dest_ids.ids),set((picking_ship.move_lines|return_pack_picking.move_lines).ids))

        self.assertEqual(set(picking_ship.move_lines.move_orig_ids.ids),set(picking_pack.move_lines.ids))
        self.assertEqual(set(picking_ship.move_lines.move_dest_ids.ids),set(return_ship_picking.move_lines.ids))

        self.assertEqual(set(return_ship_picking.move_lines.move_orig_ids.ids),set(picking_ship.move_lines.ids))
        self.assertEqual(set(return_ship_picking.move_lines.move_dest_ids.ids),set(return_pack_picking.move_lines.ids))

        self.assertEqual(set(return_pack_picking.move_lines.move_orig_ids.ids),set((picking_pack.move_lines|return_ship_picking.move_lines).ids))
        self.assertEqual(set(return_pack_picking.move_lines.move_dest_ids.ids),set(return_pick_picking.move_lines.ids))

        self.assertEqual(set(return_pick_picking.move_lines.move_orig_ids.ids),set((picking_pick.move_lines|return_pack_picking.move_lines).ids))
        self.assertEqual(len(return_pick_picking.move_lines.move_dest_ids),0)

    deftest_merge_move_mto_mts(self):
        """Create2movesofthesameproductinthesamepickingwith
        onein'MTO'andtheotheronein'MTS'.Themovesshouldn'tbemerged
        """
        picking_pick,picking_client=self.create_pick_ship()

        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':3,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_client.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'origin':'MPS',
            'procure_method':'make_to_stock',
        })
        picking_client.action_confirm()
        self.assertEqual(len(picking_client.move_lines),2,'Movesshouldnotbemerged')

    deftest_mto_cancel_move_line(self):
        """Createapickshipsituation.Thenprocessthepickpicking
        withabackorder.Thentrytounlinkthemovelinecreatedon
        theshipandcheckifthepickingandmovestateareupdated.
        Thenvalidatethebackorderandunlinktheshipmovelinesin
        ordertocheckagainifthepickingandstateareupdated.
        """
        picking_pick,picking_client=self.create_pick_ship()
        location=self.env['stock.location'].browse(self.stock_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.productA,location,10.0)
        picking_pick.move_lines.quantity_done=5.0
        backorder_wizard_values=picking_pick.button_validate()
        backorder_wizard=self.env[(backorder_wizard_values.get('res_model'))].browse(backorder_wizard_values.get('res_id')).with_context(backorder_wizard_values['context'])
        backorder_wizard.process()

        self.assertTrue(picking_client.move_line_ids,'Amovelineshouldbecreated.')
        self.assertEqual(picking_client.move_line_ids.product_uom_qty,5,'Themovelineshouldhave5unitreserved.')

        #Directlydeletethemovelinesonthepicking.(Useshowdetailoperationonpickingtype)
        #Shoulddothesamebehaviorthanunreserve
        picking_client.move_line_ids.unlink()

        self.assertEqual(picking_client.move_lines.state,'waiting','Themovestateshouldbewaitingsincenothingisreservedandanotheroriginmovestillinprogess.')
        self.assertEqual(picking_client.state,'waiting','Thepickingstateshouldnotbereadyanymore.')

        picking_client.action_assign()

        back_order=self.env['stock.picking'].search([('backorder_id','=',picking_pick.id)])
        back_order.move_lines.quantity_done=5
        back_order.button_validate()

        self.assertEqual(picking_client.move_lines.reserved_availability,10,'Thetotalquantityshouldbereservedsinceeverythingisavailable.')
        picking_client.move_line_ids.unlink()

        self.assertEqual(picking_client.move_lines.state,'confirmed','Themoveshouldbeconfirmedsincealltheoriginmovesareprocessed.')
        self.assertEqual(picking_client.state,'confirmed','Thepickingshouldbeconfirmedsinceallthemovesareconfirmed.')

    deftest_unreserve(self):
        picking_pick,picking_client=self.create_pick_ship()

        self.assertEqual(picking_pick.state,'confirmed')
        picking_pick.do_unreserve()
        self.assertEqual(picking_pick.state,'confirmed')
        location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,location,10.0)
        picking_pick.action_assign()
        self.assertEqual(picking_pick.state,'assigned')
        picking_pick.do_unreserve()
        self.assertEqual(picking_pick.state,'confirmed')

        self.assertEqual(picking_client.state,'waiting')
        picking_client.do_unreserve()
        self.assertEqual(picking_client.state,'waiting')

    deftest_return_location(self):
        """Inapickshipscenario,sendtwoitemstothecustomer,thenreturnoneintheship
        locationandoneinareturnlocationthatislocatedinanotherwarehouse.
        """
        pick_location=self.env['stock.location'].browse(self.stock_location)
        pick_location.return_location=True

        return_warehouse=self.env['stock.warehouse'].create({'name':'returnwarehouse','code':'rw'})
        return_location=self.env['stock.location'].create({
            'name':'returninternal',
            'usage':'internal',
            'location_id':return_warehouse.view_location_id.id
        })

        self.env['stock.quant']._update_available_quantity(self.productA,pick_location,10.0)
        picking_pick,picking_client=self.create_pick_ship()

        #sendtheitemstothecustomer
        picking_pick.action_assign()
        picking_pick.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick._action_done()
        picking_client.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_client._action_done()

        #returnhalfinthepicklocation
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_client.ids,active_id=picking_client.ids[0],
            active_model='stock.picking'))
        return1=stock_return_picking_form.save()
        return1.product_return_moves.quantity=5.0
        return1.location_id=pick_location.id
        return_to_pick_picking_action=return1.create_returns()

        return_to_pick_picking=self.env['stock.picking'].browse(return_to_pick_picking_action['res_id'])
        return_to_pick_picking.move_lines[0].move_line_ids[0].qty_done=5.0
        return_to_pick_picking._action_done()

        #returntheremainigproductsinthereturnwarehouse
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking_client.ids,active_id=picking_client.ids[0],
            active_model='stock.picking'))
        return2=stock_return_picking_form.save()
        return2.product_return_moves.quantity=5.0
        return2.location_id=return_location.id
        return_to_return_picking_action=return2.create_returns()

        return_to_return_picking=self.env['stock.picking'].browse(return_to_return_picking_action['res_id'])
        return_to_return_picking.move_lines[0].move_line_ids[0].qty_done=5.0
        return_to_return_picking._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pick_location),5.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,return_location),5.0)
        self.assertEqual(len(self.env['stock.quant'].search([('product_id','=',self.productA.id),('quantity','!=',0)])),2)


classTestSinglePicking(TestStockCommon):
    deftest_backorder_1(self):
        """Checkthegoodbehaviorofcreatingabackorderforanavailablestockmove.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        #makesomestock
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,2)

        #assign
        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)

        #validwithbackordercreation
        delivery_order.move_lines[0].move_line_ids[0].qty_done=1
        delivery_order._action_done()
        self.assertNotEqual(delivery_order.date_done,False)

        backorder=self.env['stock.picking'].search([('backorder_id','=',delivery_order.id)])
        self.assertEqual(backorder.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)

    deftest_backorder_2(self):
        """Checkthegoodbehaviorofcreatingabackorderforapartiallyavailablestockmove.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        #makesomestock
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,1)

        #assigntopartiallyavailable
        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)

        #validwithbackordercreation
        delivery_order.move_lines[0].move_line_ids[0].qty_done=1
        delivery_order._action_done()
        self.assertNotEqual(delivery_order.date_done,False)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)

        backorder=self.env['stock.picking'].search([('backorder_id','=',delivery_order.id)])
        self.assertEqual(backorder.state,'confirmed')

    deftest_backorder_3(self):
        """Checkthegoodbehaviorofcreatingabackorderforanavailablemoveonapickingwith
        twoavailablemoves.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productB.id,
            'product_uom_qty':2,
            'product_uom':self.productB.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        #makesomestock
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,2)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,2)

        #assigntopartiallyavailable
        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')

        delivery_order.move_lines[0].move_line_ids[0].qty_done=2
        delivery_order._action_done()

        backorder=self.env['stock.picking'].search([('backorder_id','=',delivery_order.id)])
        self.assertEqual(backorder.state,'confirmed')

    deftest_backorder_4(self):
        """Checkthegoodbehaviorifnobackorderarecreated
        forapickingwithamissingproduct.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productB.id,
            'product_uom_qty':2,
            'product_uom':self.productB.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        #Updateavailablequantitiesforeachproducts
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,2)
        self.env['stock.quant']._update_available_quantity(self.productB,pack_location,2)

        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')

        #Processonlyoneproductwithoutcreatingabackorder
        delivery_order.move_lines[0].move_line_ids[0].qty_done=2
        res_dict=delivery_order.button_validate()
        backorder_wizard=Form(self.env['stock.backorder.confirmation'].with_context(res_dict['context'])).save()
        backorder_wizard.process_cancel_backorder()

        #Nobackordershouldbecreatedandthemovecorrespondingtothemissingproductshouldbecancelled
        backorder=self.env['stock.picking'].search([('backorder_id','=',delivery_order.id)])
        self.assertFalse(backorder)
        self.assertEqual(delivery_order.state,'done')
        self.assertEqual(delivery_order.move_lines[1].state,'cancel')

    deftest_assign_deadline(self):
        """Checkifsimilaritemswithshorterdeadlineareprioritized.
        """
        delivery_order=self.PickingObj.create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':"move1",
            'product_id':self.productA.id,
            'product_uom_qty':4,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'date_deadline':datetime.now()+relativedelta(days=1)
        })
        self.MoveObj.create({
            'name':"move2",
            'product_id':self.productA.id,
            'product_uom_qty':4,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'date_deadline':datetime.now()+relativedelta(days=2)
        })

        #makesomestock
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.StockQuantObj._update_available_quantity(self.productA,pack_location,2)

        #assigntopartiallyavailable
        delivery_order.action_confirm()
        delivery_order.action_assign()
        reservedMove1=sum([x.reserved_availabilityforxindelivery_order.move_linesifx.name=="move1"])
        reservedMove2=sum([x.reserved_availabilityforxindelivery_order.move_linesifx.name=="move2"])

        self.assertEqual(reservedMove1,2,"Earlierdeadlineshouldhavereservedquantity")
        self.assertEqual(reservedMove2,0,"Laterdeadlineshouldnothavereservedquantity")

        delivery_order.move_lines[0].move_line_ids[0].qty_done=2
        delivery_order._action_done()

        #addnewstock
        self.StockQuantObj._update_available_quantity(self.productA,pack_location,2)

        #assignnewstocktobackorder
        backorder=delivery_order.backorder_ids
        backorder.action_assign()

        reservedMove1=sum([x.reserved_availabilityforxinbackorder.move_linesifx.name=="move1"])
        reservedMove2=sum([x.reserved_availabilityforxinbackorder.move_linesifx.name=="move2"])

        self.assertEqual(reservedMove1,2,"Earlierdeadlineshouldhavereservedquantity")
        self.assertEqual(reservedMove2,0,"Laterdeadlineshouldnothavereservedquantity")

    deftest_extra_move_1(self):
        """Checkthegoodbehaviorofcreatinganextramoveinadeliveryorder.Thisusecase
        simulatesthedeliveryof2itemwhiletheinitialstockmovehadtomove1andthere's
        only1instock.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        #makesomestock
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),1.0)

        #assigntoavailable
        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)

        #validwithbackordercreation
        delivery_order.move_lines[0].move_line_ids[0].qty_done=2
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)
        delivery_order._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location,allow_negative=True),-1.0)

        self.assertEqual(move1.product_qty,2.0)
        self.assertEqual(move1.quantity_done,2.0)
        self.assertEqual(move1.reserved_availability,0.0)
        self.assertEqual(move1.move_line_ids.product_qty,0.0) #changereservationto0fordonemove
        self.assertEqual(sum(move1.move_line_ids.mapped('qty_done')),2.0)
        self.assertEqual(move1.state,'done')

    deftest_extra_move_2(self):
        """Checkthegoodbehaviorofcreatinganextramoveinadeliveryorder.Thisusecase
        simulatesthedeliveryof3itemwhiletheinitialstockmovehadtomove1andthere's
        only1instock.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        #makesomestock
        pack_location=self.env['stock.location'].browse(self.pack_location)
        self.env['stock.quant']._update_available_quantity(self.productA,pack_location,1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),1.0)

        #assigntoavailable
        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)

        #validwithbackordercreation
        delivery_order.move_lines[0].move_line_ids[0].qty_done=3
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)
        delivery_order._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location,allow_negative=True),-2.0)

        self.assertEqual(move1.product_qty,3.0)
        self.assertEqual(move1.quantity_done,3.0)
        self.assertEqual(move1.reserved_availability,0.0)
        self.assertEqual(move1.move_line_ids.product_qty,0.0) #changereservationto0fordonemove
        self.assertEqual(sum(move1.move_line_ids.mapped('qty_done')),3.0)
        self.assertEqual(move1.state,'done')

    deftest_extra_move_3(self):
        """Checkthegoodbehaviorofcreatinganextramoveinareceipt.Thisusecasesimulates
         thereceiptof2itemwhiletheinitialstockmovehadtomove1.
        """
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)

        #assigntoavailable
        receipt.action_confirm()
        receipt.action_assign()
        self.assertEqual(receipt.state,'assigned')

        #validwithbackordercreation
        receipt.move_lines[0].move_line_ids[0].qty_done=2
        receipt._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,stock_location),2.0)

        self.assertEqual(move1.product_qty,2.0)
        self.assertEqual(move1.quantity_done,2.0)
        self.assertEqual(move1.reserved_availability,0.0)
        self.assertEqual(move1.move_line_ids.product_qty,0.0) #changereservationto0fordonemove
        self.assertEqual(sum(move1.move_line_ids.mapped('qty_done')),2.0)
        self.assertEqual(move1.state,'done')

    deftest_extra_move_4(self):
        """Createapickingwithsimilarmoves(createdafter
        confirmation).Actiondoneshouldpropagatealltheextra
        quantityandonlymergeextramovesintheiroriginalmoves.
        """
        delivery=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':5,
            'quantity_done':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,5)
        delivery.action_confirm()
        delivery.action_assign()

        delivery.write({
            'move_lines':[(0,0,{
                'name':self.productA.name,
                'product_id':self.productA.id,
                'product_uom_qty':0,
                'quantity_done':10,
                'state':'assigned',
                'product_uom':self.productA.uom_id.id,
                'picking_id':delivery.id,
                'location_id':self.stock_location,
                'location_dest_id':self.customer_location,
            })]
        })
        delivery._action_done()
        self.assertEqual(len(delivery.move_lines),2,'Moveshouldnotbemergedtogether')
        formoveindelivery.move_lines:
            self.assertEqual(move.quantity_done,move.product_uom_qty,'Initialdemandshouldbeequalstoquantitydone')

    deftest_extra_move_5(self):
        """Createapickingamovethatisproblematicwith
        rounding(5.95-5.5=0.4500000000000002).Ensurethat
        initialdemandiscorrctaferaction_doneandbackoder
        arenotcreated.
        """
        delivery=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        product=self.kgB
        self.MoveObj.create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':5.5,
            'quantity_done':5.95,
            'product_uom':product.uom_id.id,
            'picking_id':delivery.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(product,stock_location,5.5)
        delivery.action_confirm()
        delivery.action_assign()
        delivery._action_done()
        self.assertEqual(delivery.move_lines.product_uom_qty,5.95,'Moveinitialdemandshouldbe5.95')

        back_order=self.env['stock.picking'].search([('backorder_id','=',delivery.id)])
        self.assertFalse(back_order,'Thereshouldbenobackorder')

    deftest_recheck_availability_1(self):
        """Checkthegoodbehaviorofcheckavailability.IcreateaDOfor2unitwith
        onlyoneinstock.Afterthefirstcheckavailability,Ishouldhave1reserved
        productwithonemoveline.Afteraddingasecondunitinstockandrecheckavailability.
        TheDOshouldhave2reservedunit,beinavailablestateandhaveonlyonemoveline.
        """
        self.env['stock.quant']._update_available_quantity(self.productA,self.env['stock.location'].browse(self.stock_location),1.0)
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        #CheckState
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'partially_available')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.product_qty,1)

        inventory=self.env['stock.inventory'].create({
            'name':'removeproduct1',
            'location_ids':[(4,self.stock_location)],
            'product_ids':[(4,self.productA.id)],
        })
        inventory.action_start()
        inventory.line_ids.product_qty=2
        inventory.action_validate()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'assigned')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,2.0)
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.product_qty,2)

    deftest_recheck_availability_2(self):
        """Samecheckthantest_recheck_availability_1butwithlotthistime.
        Ifthenewproducthasthesamelotthatalreadyreservedone,themovelines
        reservedquantityshouldbeupdated.
        Otherwiseanewmovelineswiththenewlotshouldbeadded.
        """
        self.productA.tracking='lot'
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,1.0,lot_id=lot1)
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        #CheckState
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'partially_available')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.product_qty,1)

        inventory=self.env['stock.inventory'].create({
            'name':'removeproduct1',
            'location_ids':[(4,self.stock_location)],
            'product_ids':[(4,self.productA.id)],
        })
        inventory.action_start()
        inventory.line_ids.prod_lot_id=lot1
        inventory.line_ids.product_qty=2
        inventory.action_validate()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'assigned')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,2.0)
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.lot_id.id,lot1.id)
        self.assertEqual(move1.move_line_ids.product_qty,2)

    deftest_recheck_availability_3(self):
        """Samecheckthantest_recheck_availability_2butwithdifferentlots.
        """
        self.productA.tracking='lot'
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,1.0,lot_id=lot1)
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        #CheckState
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'partially_available')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.product_qty,1)

        inventory=self.env['stock.inventory'].create({
            'name':'removeproduct1',
            'location_ids':[(4,self.stock_location)],
            'product_ids':[(4,self.productA.id)],
        })
        inventory.action_start()
        self.env['stock.inventory.line'].create({
            'inventory_id':inventory.id,
            'location_id':inventory.location_ids[0].id,
            'prod_lot_id':lot2.id,
            'product_id':self.productA.id,
            'product_qty':1,
        })
        inventory.action_validate()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'assigned')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,2.0)
        self.assertEqual(len(move1.move_line_ids),2)
        move_lines=move1.move_line_ids.sorted()
        self.assertEqual(move_lines[0].lot_id.id,lot1.id)
        self.assertEqual(move_lines[1].lot_id.id,lot2.id)

    deftest_recheck_availability_4(self):
        """Samecheckthantest_recheck_availability_2butwithserialnumberthistime.
        Serialnumberreservationshouldalwayscreateanewmoveline.
        """
        self.productA.tracking='serial'
        serial1=self.env['stock.production.lot'].create({
            'name':'serial1',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        serial2=self.env['stock.production.lot'].create({
            'name':'serial2',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,1.0,lot_id=serial1)
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        #CheckState
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'partially_available')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.product_qty,1)

        inventory=self.env['stock.inventory'].create({
            'name':'removeproduct1',
            'location_ids':[(4,self.stock_location)],
            'product_ids':[(4,self.productA.id)],
        })
        inventory.action_start()
        self.env['stock.inventory.line'].create({
            'inventory_id':inventory.id,
            'location_id':inventory.location_ids[0].id,
            'prod_lot_id':serial2.id,
            'product_id':self.productA.id,
            'product_qty':1,
        })
        inventory.action_validate()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(move1.state,'assigned')

        #Checkreservedquantity
        self.assertEqual(move1.reserved_availability,2.0)
        self.assertEqual(len(move1.move_line_ids),2)
        move_lines=move1.move_line_ids.sorted()
        self.assertEqual(move_lines[0].lot_id.id,serial1.id)
        self.assertEqual(move_lines[1].lot_id.id,serial2.id)

    deftest_use_create_lot_use_existing_lot_1(self):
        """Checkthebehaviorofapickingwhen`use_create_lot`and`use_existing_lot`are
        settoFalseandthere'samoveforatrackedproduct.
        """
        self.env['stock.picking.type']\
            .browse(self.picking_type_out)\
            .write({
                'use_create_lots':False,
                'use_existing_lots':False,
            })
        self.productA.tracking='lot'

        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'picking_type_id':self.picking_type_out,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        delivery_order.action_confirm()
        delivery_order.move_lines.quantity_done=2
        #donotsetalot_idorlot_name,itshouldwork
        delivery_order._action_done()

    deftest_use_create_lot_use_existing_lot_2(self):
        """Checkthebehaviorofapickingwhen`use_create_lot`and`use_existing_lot`are
        settoTrueandthere'samoveforatrackedproduct.
        """
        self.env['stock.picking.type']\
            .browse(self.picking_type_out)\
            .write({
                'use_create_lots':True,
                'use_existing_lots':True,
            })
        self.productA.tracking='lot'

        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'picking_type_id':self.picking_type_out,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        delivery_order.action_confirm()
        delivery_order.move_lines.quantity_done=2
        move_line=delivery_order.move_lines.move_line_ids

        #notlot_nameset,shouldraise
        withself.assertRaises(UserError):
            delivery_order._action_done()

        #enteranewlotname,shouldwork
        move_line.lot_name='newlot'
        delivery_order._action_done()

    deftest_use_create_lot_use_existing_lot_3(self):
        """Checkthebehaviorofapickingwhen`use_create_lot`issettoTrueand
        `use_existing_lot`issettoFalseandthere'samoveforatrackedproduct.
        """
        self.env['stock.picking.type']\
            .browse(self.picking_type_out)\
            .write({
                'use_create_lots':True,
                'use_existing_lots':False,
            })
        self.productA.tracking='lot'

        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'picking_type_id':self.picking_type_out,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        delivery_order.action_confirm()
        delivery_order.move_lines.quantity_done=2
        move_line=delivery_order.move_lines.move_line_ids

        #notlot_nameset,shouldraise
        withself.assertRaises(UserError):
            delivery_order._action_done()

        #enteranewlotname,shouldwork
        move_line.lot_name='newlot'
        delivery_order._action_done()

    deftest_use_create_lot_use_existing_lot_4(self):
        """Checkthebehaviorofapickingwhen`use_create_lot`issettoFalseand
        `use_existing_lot`issettoTrueandthere'samoveforatrackedproduct.
        """
        self.env['stock.picking.type']\
            .browse(self.picking_type_out)\
            .write({
                'use_create_lots':False,
                'use_existing_lots':True,
            })
        self.productA.tracking='lot'

        delivery_order=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':2,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'picking_type_id':self.picking_type_out,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
        })

        delivery_order.action_confirm()
        delivery_order.move_lines.quantity_done=2
        move_line=delivery_order.move_lines.move_line_ids

        #notlot_nameset,shouldraise
        withself.assertRaises(UserError):
            delivery_order._action_done()

        #creatingalotfromtheviewshouldraise
        withself.assertRaises(UserError):
            self.env['stock.production.lot']\
                .with_context(active_picking_id=delivery_order.id)\
                .create({
                    'name':'lot1',
                    'product_id':self.productA.id,
                    'company_id':self.env.company.id,
                })

        #enteranexistinglot_id,shouldwork
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.productA.id,
            'company_id':self.env.company.id,
        })
        move_line.lot_id=lot1
        delivery_order._action_done()

    deftest_merge_moves_1(self):
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':3,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':5,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        self.MoveObj.create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':5,
            'product_uom':self.productB.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        receipt.action_confirm()
        self.assertEqual(len(receipt.move_lines),2,'Moveswerenotmerged')
        self.assertEqual(receipt.move_lines.filtered(lambdam:m.product_id==self.productA).product_uom_qty,9,'Mergedquantityisnotcorrect')
        self.assertEqual(receipt.move_lines.filtered(lambdam:m.product_id==self.productB).product_uom_qty,5,'MergeshouldnotimpactproductBreservedquantity')

    deftest_merge_moves_2(self):
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':3,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'origin':'MPS'
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':5,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'origin':'PO0001'
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':3,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'origin':'MPS'
        })
        receipt.action_confirm()
        self.assertEqual(len(receipt.move_lines),1,'Moveswerenotmerged')
        self.assertEqual(receipt.move_lines.origin.count('MPS'),1,'Originnotmergedtogetherorduplicated')
        self.assertEqual(receipt.move_lines.origin.count('PO0001'),1,'Originnotmergedtogetherorduplicated')

    deftest_merge_moves_3(self):
        """Create2moveswithoutinitial_demandandalreadya
        quantitydone.Checkthatwestillhaveonly2movesafter
        validation.
        """
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        move_1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':0,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'origin':'MPS'
        })
        move_2=self.MoveObj.create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':0,
            'product_uom':self.productB.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'origin':'PO0001'
        })
        move_1.quantity_done=5
        move_2.quantity_done=5
        receipt.button_validate()
        self.assertEqual(len(receipt.move_lines),2,'Moveswerenotmerged')

    deftest_merge_chained_moves(self):
        """Imaginemultiplestepdelivery.Twodifferentreceiptpickingforthesameproductshouldonlygenerate
        1pickingfrominputtoQCandanotherfromQCtostock.Thelinkattheendshouldfollowthisscheme.
        Movereceipt1\
                        MoveInput->QC-MoveQC->Stock
        Movereceipt2/
        """
        warehouse=self.env['stock.warehouse'].create({
            'name':'TESTWAREHOUSE',
            'code':'TEST1',
            'reception_steps':'three_steps',
        })
        receipt1=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':warehouse.wh_input_stock_loc_id.id,
            'picking_type_id':warehouse.in_type_id.id,
        })
        move_receipt_1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':5,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt1.id,
            'location_id':self.supplier_location,
            'location_dest_id':warehouse.wh_input_stock_loc_id.id,
        })
        receipt2=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':warehouse.wh_input_stock_loc_id.id,
            'picking_type_id':warehouse.in_type_id.id,
        })
        move_receipt_2=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':3,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt2.id,
            'location_id':self.supplier_location,
            'location_dest_id':warehouse.wh_input_stock_loc_id.id,
        })
        receipt1.action_confirm()
        receipt2.action_confirm()

        #Checkfollowingmovehasbeencreatedandgroupedinonepicking.
        self.assertTrue(move_receipt_1.move_dest_ids,'Nomovecreatedfrompushrules')
        self.assertTrue(move_receipt_2.move_dest_ids,'Nomovecreatedfrompushrules')
        self.assertEqual(move_receipt_1.move_dest_ids.picking_id,move_receipt_2.move_dest_ids.picking_id,'Destinationmovesshouldbeinthesamepicking')

        #Checklinkforinputmovearecorrect.
        input_move=move_receipt_2.move_dest_ids
        self.assertEqual(len(input_move.move_dest_ids),1)
        self.assertEqual(set(input_move.move_orig_ids.ids),set((move_receipt_2|move_receipt_1).ids),
                         'MovefrominputtoQCshouldbemergedandhavethetworeceiptmovesasorigin.')
        self.assertEqual(move_receipt_1.move_dest_ids,input_move)
        self.assertEqual(move_receipt_2.move_dest_ids,input_move)

        #Checklinkforqualitycheckmovearealsocorrect.
        qc_move=input_move.move_dest_ids
        self.assertEqual(len(qc_move),1)
        self.assertTrue(qc_move.move_orig_ids==input_move,'MovebetweenQCandstockshouldonlyhavetheinputmoveasorigin')

    deftest_empty_moves_validation_1(self):
        """Usebuttonvalidateonapickingthatcontainsonlymoves
        withoutinitialdemandandwithoutquantitydoneshouldbe
        impossibleandraiseausererror.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':0,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        self.MoveObj.create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':0,
            'product_uom':self.productB.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        withself.assertRaises(UserError):
            delivery_order.button_validate()

    deftest_empty_moves_validation_2(self):
        """Usebuttonvalidateonapickingthatcontainsonlymoves
        withoutinitialdemandbutatleastonewithaquantitydone
        shouldprocessthemovewithquantitydoneandcancelthe
        other.
        """
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        move_a=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':0,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        move_b=self.MoveObj.create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':0,
            'product_uom':self.productB.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        move_a.quantity_done=1
        delivery_order.button_validate()

        self.assertEqual(move_a.state,'done')
        self.assertEqual(move_b.state,'cancel')
        back_order=self.env['stock.picking'].search([('backorder_id','=',delivery_order.id)])
        self.assertFalse(back_order,'Thereshouldbenobackorder')

    deftest_unlink_move_1(self):
        picking=Form(self.env['stock.picking'])
        ptout=self.env['stock.picking.type'].browse(self.picking_type_out)
        picking.picking_type_id=ptout
        withpicking.move_ids_without_package.new()asmove:
            move.product_id=self.productA
            move.product_uom_qty=10
        picking=picking.save()
        self.assertEqual(picking.immediate_transfer,False)
        self.assertEqual(picking.state,'draft')

        picking=Form(picking)
        picking.move_ids_without_package.remove(0)
        picking=picking.save()
        self.assertEqual(len(picking.move_ids_without_package),0)

    deftest_additional_move_1(self):
        """Onaplannedtrasfer,addastockmovewhenthepickingisalreadyready.Checkthat
        thecheckavailabilitybuttonappearsandwork.
        """
        #MakesomestockforproductAandproductB.
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        move_1=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        move_2=self.MoveObj.create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':10,
            'product_uom':self.productB.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        receipt.action_confirm()
        move_1.quantity_done=10
        move_2.quantity_done=10
        receipt.button_validate()
        self.assertEqual(self.productA.qty_available,10)
        self.assertEqual(self.productB.qty_available,10)

        #Createadeliveryfor1productA,reserve,checkthepickingisready
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
            'move_type':'one',
        })
        move_3=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':delivery_order.id,
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
        })
        delivery_order.action_confirm()
        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')

        #AddaunitofproductB,thecheck_availabilitybuttonshouldappear.
        delivery_order=Form(delivery_order)
        withdelivery_order.move_ids_without_package.new()asmove:
            move.product_id=self.productB
            move.product_uom_qty=10
        delivery_order=delivery_order.save()

        #Theautocoformran,thepickingshoudbeconfirmedandreservable.
        self.assertEqual(delivery_order.state,'confirmed')
        self.assertEqual(delivery_order.show_mark_as_todo,False)
        self.assertEqual(delivery_order.show_check_availability,True)

        delivery_order.action_assign()
        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(delivery_order.show_check_availability,False)
        self.assertEqual(delivery_order.show_mark_as_todo,False)

        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.assertEqual(self.env['stock.quant']._gather(self.productA,stock_location).reserved_quantity,10.0)
        self.assertEqual(self.env['stock.quant']._gather(self.productB,stock_location).reserved_quantity,10.0)

    deftest_additional_move_2(self):
        """Onanimmediatetrasfer,addastockmovewhenthepickingisalreadyready.Checkthat
        thecheckavailabilitybuttondoestnotappear.
        """
        #Createadeliveryfor1productA,checkthepickingisready
        delivery_order=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
            'immediate_transfer':True,
            'move_ids_without_package':[(0,0,{
                'name':self.productA.name,
                'product_id':self.productA.id,
                'product_uom':self.productA.uom_id.id,
                'location_id':self.stock_location,
                'location_dest_id':self.customer_location,
                'quantity_done':5,
            })],
        })
        self.assertEqual(delivery_order.state,'assigned')

        #AddaunitofproductB,thecheck_availabilitybuttonshouldnotappear.
        delivery_order=Form(delivery_order)
        withdelivery_order.move_ids_without_package.new()asmove:
            move.product_id=self.productB
        delivery_order=delivery_order.save()

        self.assertEqual(delivery_order.state,'assigned')
        self.assertEqual(delivery_order.show_check_availability,False)
        self.assertEqual(delivery_order.show_mark_as_todo,False)

    deftest_owner_1(self):
        """Makeareceipt,setanownerandvalidate"""
        owner1=self.env['res.partner'].create({'name':'owner'})
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        move1=self.env['stock.move'].create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':receipt.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
        })
        receipt.action_confirm()
        receipt=Form(receipt)
        receipt.owner_id=owner1
        receipt=receipt.save()
        wiz=receipt.button_validate()
        wiz=Form(self.env['stock.immediate.transfer'].with_context(wiz['context'])).save()
        wiz.process()

        supplier_location=self.env['stock.location'].browse(self.supplier_location)
        stock_location=self.env['stock.location'].browse(self.stock_location)
        supplier_quant=self.env['stock.quant']._gather(self.productA,supplier_location)
        stock_quant=self.env['stock.quant']._gather(self.productA,stock_location)

        self.assertEqual(supplier_quant.owner_id,owner1)
        self.assertEqual(supplier_quant.quantity,-1)
        self.assertEqual(stock_quant.owner_id,owner1)
        self.assertEqual(stock_quant.quantity,1)

    deftest_putaway_for_picking_sml(self):
        """Checkspicking'smovelineswilltakeinaccounttheputawayrules
        todefinethe`location_dest_id`.
        """
        partner=self.env['res.partner'].create({'name':'Partner'})
        supplier_location=self.env['stock.location'].browse(self.supplier_location)
        stock_location=self.env['stock.location'].create({
            'name':'test-stock',
            'usage':'internal',
        })
        shelf_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':stock_location.id,
        })

        #Weneedtoactivatemulti-locationstouseputawayrules.
        grp_multi_loc=self.env.ref('stock.group_stock_multi_locations')
        self.env.user.write({'groups_id':[(4,grp_multi_loc.id)]})
        putaway_product=self.env['stock.putaway.rule'].create({
            'product_id':self.productA.id,
            'location_in_id':stock_location.id,
            'location_out_id':shelf_location.id,
        })
        #Changesconfigofreceipttypetoallowtoeditmovelinesdirectly.
        picking_type=self.env['stock.picking.type'].browse(self.picking_type_in)
        picking_type.show_operations=True

        receipt_form=Form(self.env['stock.picking'].with_context(
            force_detailed_view=True
        ),view='stock.view_picking_form')
        receipt_form.partner_id=partner
        receipt_form.picking_type_id=picking_type
        receipt_form.location_id=supplier_location
        receipt_form.location_dest_id=stock_location
        receipt=receipt_form.save()
        withreceipt_form.move_line_nosuggest_ids.new()asmove_line:
            move_line.product_id=self.productA

        receipt=receipt_form.save()
        #Checksreceipthasstillitsdestinationlocationandchecksitsmove
        #linetooktheonefromtheputawayrule.
        self.assertEqual(receipt.location_dest_id.id,stock_location.id)
        self.assertEqual(receipt.move_line_ids.location_dest_id.id,shelf_location.id)

    deftest_cancel_plan_transfer(self):
        """Testcancelingplantransfer"""
        #Createpickingwithstockmove.
        picking=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
            'move_lines':[(0,0,{
                'name':self.productA.name,
                'product_id':self.productA.id,
                'product_uom_qty':10,
                'product_uom':self.productA.uom_id.id,
                'location_id':self.pack_location,
                'location_dest_id':self.customer_location,
            })]
        })
        #Confirmtheoutgoingpicking,stateshouldbechanged.
        picking.action_confirm()
        self.assertEqual(picking.state,'confirmed',"Pickingshouldbeinaconfirmedstate.")

        #Pickinginaconfirmedstateandtrytocancelit.
        picking.action_cancel()
        self.assertEqual(picking.state,'cancel',"Pickingshouldbeinacancelstate.")

    deftest_immediate_transfer(self):
        """TestpickingshouldbeinreadystateifimmediatetransferandSMLiscreatedviaview+
            Testpickingcancelationwithimmediatetransferanddonequantity"""
        #createpickingwithstockmoveline
        picking=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
            'immediate_transfer':True,
            'move_line_ids':[(0,0,{
                'product_id':self.productA.id,
                'qty_done':10,
                'product_uom_id':self.productA.uom_id.id,
                'location_id':self.pack_location,
                'location_dest_id':self.customer_location,
            })]
        })

        self.assertEqual(picking.state,'assigned',"Pickingshouldnotbeinadraftstate.")
        self.assertEqual(len(picking.move_lines),1,"Pickingshouldhavestockmove.")
        picking.action_cancel()
        self.assertEqual(picking.move_lines.state,'cancel',"Stockmoveshouldbeinacancelstate.")
        self.assertEqual(picking.state,'cancel',"Pickingshouldbeinacancelstate.")


classTestStockUOM(TestStockCommon):
    defsetUp(self):
        super(TestStockUOM,self).setUp()
        dp=self.env.ref('product.decimal_product_uom')
        dp.digits=7

    deftest_pickings_transfer_with_different_uom_and_back_orders(self):
        """Pickingtransferwithdiffrentunitofmeassure."""
        #weightcategory
        categ_test=self.env['uom.category'].create({'name':'Biggerthantons'})

        T_LBS=self.env['uom.uom'].create({
            'name':'T-LBS',
            'category_id':categ_test.id,
            'uom_type':'reference',
            'rounding':0.01
        })
        T_GT=self.env['uom.uom'].create({
            'name':'T-GT',
            'category_id':categ_test.id,
            'uom_type':'bigger',
            'rounding':0.0000001,
            'factor_inv':2240.00,
        })
        T_TEST=self.env['product.product'].create({
            'name':'T_TEST',
            'type':'product',
            'uom_id':T_LBS.id,
            'uom_po_id':T_LBS.id,
            'tracking':'lot',
        })

        picking_in=self.env['stock.picking'].create({
            'picking_type_id':self.picking_type_in,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location
        })
        move=self.env['stock.move'].create({
            'name':'Firstmovewith60GT',
            'product_id':T_TEST.id,
            'product_uom_qty':60,
            'product_uom':T_GT.id,
            'picking_id':picking_in.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location
        })
        picking_in.action_confirm()

        self.assertEqual(move.product_uom_qty,60.00,'WrongT_GTquantity')
        self.assertEqual(move.product_qty,134400.00,'WrongT_LBSquantity')

        lot=self.env['stock.production.lot'].create({'name':'LotTEST','product_id':T_TEST.id,'company_id':self.env.company.id,})
        self.env['stock.move.line'].create({
            'move_id':move.id,
            'product_id':T_TEST.id,
            'product_uom_id':T_LBS.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'qty_done':42760.00,
            'lot_id':lot.id,
        })

        picking_in._action_done()
        back_order_in=self.env['stock.picking'].search([('backorder_id','=',picking_in.id)])

        self.assertEqual(len(back_order_in),1.00,'Thereshouldbeonebackordercreated')
        self.assertEqual(back_order_in.move_lines.product_qty,91640.00,'Thereshouldbeonebackordercreated')

    deftest_move_product_with_different_uom(self):
        """Productdefinedingwith0.01rounding
        DecimalAccuracy(DA)3digits.
        Quantityonhand:149.88g
        Pickingof1kg
        kghas0.0001rounding
        Duetoconversions,wemayendupreserving150g
        (morethanthequantityinstock),wecheckthat
        wereservelessthanthequantityinstock
        """
        precision=self.env.ref('product.decimal_product_uom')
        precision.digits=3
        precision_digits=precision.digits

        self.uom_kg.rounding=0.0001
        self.uom_gm.rounding=0.01

        product_G=self.env['product.product'].create({
            'name':'ProductG',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'uom_id':self.uom_gm.id,
            'uom_po_id':self.uom_gm.id,
        })

        stock_location=self.env['stock.location'].browse(self.stock_location)
        self.env['stock.quant']._update_available_quantity(product_G,stock_location,149.88)
        self.assertEqual(len(product_G.stock_quant_ids),1,'Onequantshouldexistfortheproduct.')
        quant=product_G.stock_quant_ids

        #transfer1kgofproduct_G
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })

        move=self.env['stock.move'].create({
            'name':'test_reserve_product_G',
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_id':picking.id,
            'product_id':product_G.id,
            'product_uom':self.uom_kg.id,
            'product_uom_qty':1,
        })

        self.assertEqual(move.product_uom.id,self.uom_kg.id)
        self.assertEqual(move.product_uom_qty,1.0)

        picking.action_confirm()
        picking.action_assign()

        self.assertEqual(product_G.uom_id.rounding,0.01)
        self.assertEqual(move.product_uom.rounding,0.0001)

        self.assertEqual(len(picking.move_line_ids),1,'Onemovelineshouldexistforthepicking.')
        move_line=picking.move_line_ids
        #checkthatwedonotreservemore(inthesameUOM)thanthequantityinstock
        self.assertEqual(float_compare(move_line.product_qty,quant.quantity,precision_digits=precision_digits),-1,"Wedonotreservemore(inthesameUOM)thanthequantityinstock")
        #checkthatwereservethesamequantityinthemlandthequant
        self.assertTrue(float_is_zero(move_line.product_qty-quant.reserved_quantity,precision_digits=precision_digits))

    deftest_update_product_move_line_with_different_uom(self):
        """Checkthatwhenthemovelineandcorresponding
        producthavedifferentUOMwithpossiblyconflicting
        precisions,wedonotreservemorethanthequantity
        instock.Similarinitialconfigurationas
        test_move_product_with_different_uom.
        """
        precision=self.env.ref('product.decimal_product_uom')
        precision.digits=3
        precision_digits=precision.digits

        self.uom_kg.rounding=0.0001
        self.uom_gm.rounding=0.01

        product_LtDA=self.env['product.product'].create({
            'name':'ProductLessthanDA',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'uom_id':self.uom_gm.id,
            'uom_po_id':self.uom_gm.id,
        })

        product_GtDA=self.env['product.product'].create({
            'name':'ProductGreaterthanDA',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'uom_id':self.uom_gm.id,
            'uom_po_id':self.uom_gm.id,
        })

        stock_location=self.env['stock.location'].browse(self.stock_location)

        #quantityinhandconvertedtokgisnotmoreprecisethantheDA
        self.env['stock.quant']._update_available_quantity(product_LtDA,stock_location,149)
        #quantityinhandconvertedtokgismoreprecisethantheDA
        self.env['stock.quant']._update_available_quantity(product_GtDA,stock_location,149.88)

        self.assertEqual(len(product_LtDA.stock_quant_ids),1,'Onequantshouldexistfortheproduct.')
        self.assertEqual(len(product_GtDA.stock_quant_ids),1,'Onequantshouldexistfortheproduct.')
        quant_LtDA=product_LtDA.stock_quant_ids
        quant_GtDA=product_GtDA.stock_quant_ids

        #create2movesof1kg
        move_LtDA=self.env['stock.move'].create({
            'name':'test_reserve_product_LtDA',
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'product_id':product_LtDA.id,
            'product_uom':self.uom_kg.id,
            'product_uom_qty':1,
        })

        move_GtDA=self.env['stock.move'].create({
            'name':'test_reserve_product_GtDA',
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'product_id':product_GtDA.id,
            'product_uom':self.uom_kg.id,
            'product_uom_qty':1,
        })

        self.assertEqual(move_LtDA.state,'draft')
        self.assertEqual(move_GtDA.state,'draft')
        move_LtDA._action_confirm()
        move_GtDA._action_confirm()
        self.assertEqual(move_LtDA.state,'confirmed')
        self.assertEqual(move_GtDA.state,'confirmed')
        #checkavailability,lessthaninitialdemand
        move_LtDA._action_assign()
        move_GtDA._action_assign()
        self.assertEqual(move_LtDA.state,'partially_available')
        self.assertEqual(move_GtDA.state,'partially_available')
        #theinitialdemandis1kg
        self.assertEqual(move_LtDA.product_uom.id,self.uom_kg.id)
        self.assertEqual(move_GtDA.product_uom.id,self.uom_kg.id)
        self.assertEqual(move_LtDA.product_uom_qty,1.0)
        self.assertEqual(move_GtDA.product_uom_qty,1.0)
        #onemovelineiscreated
        self.assertEqual(len(move_LtDA.move_line_ids),1)
        self.assertEqual(len(move_GtDA.move_line_ids),1)

        #increasequantityby0.14988kg(moreprecisethanDA)
        self.env['stock.quant']._update_available_quantity(product_LtDA,stock_location,149.88)
        self.env['stock.quant']._update_available_quantity(product_GtDA,stock_location,149.88)

        #_update_reserved_quantityiscalledonamoveonlyin_action_assign
        move_LtDA._action_assign()
        move_GtDA._action_assign()

        #asthemovelineforLtDAanditscorrespondingquantcanbe
        #indifferentUOMs,anewmovelinecanbecreated
        #from_update_reserved_quantity
        move_lines_LtDA=self.env["stock.move.line"].search([
            ('product_id','=',quant_LtDA.product_id.id),
            ('location_id','=',quant_LtDA.location_id.id),
            ('lot_id','=',quant_LtDA.lot_id.id),
            ('package_id','=',quant_LtDA.package_id.id),
            ('owner_id','=',quant_LtDA.owner_id.id),
            ('product_qty','!=',0)
        ])
        reserved_on_move_lines_LtDA=sum(move_lines_LtDA.mapped('product_qty'))

        move_lines_GtDA=self.env["stock.move.line"].search([
            ('product_id','=',quant_GtDA.product_id.id),
            ('location_id','=',quant_GtDA.location_id.id),
            ('lot_id','=',quant_GtDA.lot_id.id),
            ('package_id','=',quant_GtDA.package_id.id),
            ('owner_id','=',quant_GtDA.owner_id.id),
            ('product_qty','!=',0)
        ])
        reserved_on_move_lines_GtDA=sum(move_lines_GtDA.mapped('product_qty'))

        #checkthatwedonotreservemore(inthesameUOM)thanthequantityinstock
        self.assertEqual(float_compare(reserved_on_move_lines_LtDA,quant_LtDA.quantity,precision_digits=precision_digits),-1,"Wedonotreservemore(inthesameUOM)thanthequantityinstock")
        self.assertEqual(float_compare(reserved_on_move_lines_GtDA,quant_GtDA.quantity,precision_digits=precision_digits),-1,"Wedonotreservemore(inthesameUOM)thanthequantityinstock")

        #checkthatwereservethesamequantityinthemlandthequant
        self.assertTrue(float_is_zero(reserved_on_move_lines_LtDA-quant_LtDA.reserved_quantity,precision_digits=precision_digits))
        self.assertTrue(float_is_zero(reserved_on_move_lines_GtDA-quant_GtDA.reserved_quantity,precision_digits=precision_digits))


classTestRoutes(TestStockCommon):
    defsetUp(self):
        super(TestRoutes,self).setUp()
        self.product1=self.env['product.product'].create({
            'name':'producta',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        self.uom_unit=self.env.ref('uom.product_uom_unit')
        self.partner=self.env['res.partner'].create({'name':'Partner'})

    def_enable_pick_ship(self):
        self.wh=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)

        #createandgetbackthepickshiproute
        self.wh.write({'delivery_steps':'pick_ship'})
        self.pick_ship_route=self.wh.route_ids.filtered(lambdar:'(pick+ship)'inr.name)

    deftest_pick_ship_1(self):
        """Enablethepickshiproute,forceaprocurementgrouponthe
        pick.Whenasecondmoveisadded,makesurethe`partner_id`and
        `origin`fieldsareerased.
        """
        self._enable_pick_ship()

        #createaprocurementgroupandsetinonthepickstockrule
        procurement_group0=self.env['procurement.group'].create({})
        pick_rule=self.pick_ship_route.rule_ids.filtered(lambdarule:'Stock→Output'inrule.name)
        push_rule=self.pick_ship_route.rule_ids-pick_rule
        pick_rule.write({
            'group_propagation_option':'fixed',
            'group_id':procurement_group0.id,
        })

        ship_location=pick_rule.location_id
        customer_location=push_rule.location_id
        partners=self.env['res.partner'].search([],limit=2)
        partner0=partners[0]
        partner1=partners[1]
        procurement_group1=self.env['procurement.group'].create({'partner_id':partner0.id})
        procurement_group2=self.env['procurement.group'].create({'partner_id':partner1.id})

        move1=self.env['stock.move'].create({
            'name':'firstoutmove',
            'procure_method':'make_to_order',
            'location_id':ship_location.id,
            'location_dest_id':customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'warehouse_id':self.wh.id,
            'group_id':procurement_group1.id,
            'origin':'origin1',
        })

        move2=self.env['stock.move'].create({
            'name':'secondoutmove',
            'procure_method':'make_to_order',
            'location_id':ship_location.id,
            'location_dest_id':customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'warehouse_id':self.wh.id,
            'group_id':procurement_group2.id,
            'origin':'origin2',
        })

        #firstoutmove,the"pick"pickingshouldhaveapartnerandanorigin
        move1._action_confirm()
        picking_pick=move1.move_orig_ids.picking_id
        self.assertEqual(picking_pick.partner_id.id,procurement_group1.partner_id.id)
        self.assertEqual(picking_pick.origin,move1.group_id.name)

        #secondoutmove,the"pick"pickingshouldhavelostitspartnerandorigin
        move2._action_confirm()
        self.assertEqual(picking_pick.partner_id.id,False)
        self.assertEqual(picking_pick.origin,False)

    deftest_replenish_pick_ship_1(self):
        """Creates2warehousesandmakeareplenishusingonewarehouse
        toressuplytheotherone,Thencheckifthequantityandtheproductarematching
        """
        self.product_uom_qty=42

        warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse_2=self.env['stock.warehouse'].create({
            'name':'SmallWarehouse',
            'code':'SWH'
        })
        warehouse_1.write({
            'resupply_wh_ids':[(6,0,[warehouse_2.id])]
        })
        resupply_route=self.env['stock.location.route'].search([('supplier_wh_id','=',warehouse_2.id),('supplied_wh_id','=',warehouse_1.id)])
        self.assertTrue(resupply_route,"Ressuplyroutenotfound")
        self.product1.write({'route_ids':[(4,resupply_route.id),(4,self.env.ref('stock.route_warehouse0_mto').id)]})
        self.wh=warehouse_1

        replenish_wizard=self.env['product.replenish'].create({
            'product_id':self.product1.id,
            'product_tmpl_id':self.product1.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'quantity':self.product_uom_qty,
            'warehouse_id':self.wh.id,
        })

        replenish_wizard.launch_replenishment()
        last_picking_id=self.env['stock.picking'].search([('origin','=','ManualReplenishment')])[-1]
        self.assertTrue(last_picking_id,'Pickingnotfound')
        move_line=last_picking_id.move_lines.search([('product_id','=',self.product1.id)])
        self.assertTrue(move_line,'Theproductisnotinthepicking')
        self.assertEqual(move_line[0].product_uom_qty,self.product_uom_qty,'Quantitiesdoesnotmatch')
        self.assertEqual(move_line[1].product_uom_qty,self.product_uom_qty,'Quantitiesdoesnotmatch')

    deftest_push_rule_on_move_1(self):
        """Createaroutewithapushrule,forceitonamove,checkthatitisapplied.
        """
        self._enable_pick_ship()
        stock_location=self.env.ref('stock.stock_location_stock')

        push_location=self.env['stock.location'].create({
            'location_id':stock_location.location_id.id,
            'name':'pushlocation',
        })

        #TODO:maybeaddanewtypeonthe"applicableon"fields?
        route=self.env['stock.location.route'].create({
            'name':'newroute',
            'rule_ids':[(0,False,{
                'name':'createamovetopushlocation',
                'location_src_id':stock_location.id,
                'location_id':push_location.id,
                'company_id':self.env.company.id,
                'action':'push',
                'auto':'manual',
                'picking_type_id':self.env.ref('stock.picking_type_in').id,
            })],
        })
        move1=self.env['stock.move'].create({
            'name':'movewitharoute',
            'location_id':stock_location.id,
            'location_dest_id':stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'route_ids':[(4,route.id)]
        })
        move1._action_confirm()

        pushed_move=move1.move_dest_ids
        self.assertEqual(pushed_move.location_dest_id.id,push_location.id)

    deftest_location_dest_update(self):
        """Checkthelocationdestofastockmovechangedbyapushrule
        withautofieldsettotransparentisdonecorrectly.Thestock_move
        iscreatewiththemovelinedirectlytopassintoaction_confirm()via
        action_done()."""
        self.wh=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        new_loc=self.env['stock.location'].create({
            'name':'New_location',
            'usage':'internal',
            'location_id':self.env.ref('stock.stock_location_locations').id,
        })
        picking_type=self.env['stock.picking.type'].create({
            'name':'new_picking_type',
            'code':'internal',
            'sequence_code':'NPT',
            'default_location_src_id':self.env.ref('stock.stock_location_stock').id,
            'default_location_dest_id':new_loc.id,
            'warehouse_id':self.wh.id,
        })
        route=self.env['stock.location.route'].create({
            'name':'newroute',
            'rule_ids':[(0,False,{
                'name':'createamovetopushlocation',
                'location_src_id':self.env.ref('stock.stock_location_stock').id,
                'location_id':new_loc.id,
                'company_id':self.env.company.id,
                'action':'push',
                'auto':'transparent',
                'picking_type_id':picking_type.id,
            })],
        })
        product=self.env['product.product'].create({
            'name':'new_product',
            'type':'product',
            'route_ids':[(4,route.id)]
        })
        move1=self.env['stock.move'].create({
            'name':'movewitharoute',
            'location_id':self.supplier_location,
            'location_dest_id':self.env.ref('stock.stock_location_stock').id,
            'product_id':product.id,
            'product_uom_qty':1.0,
            'product_uom':self.uom_unit.id,
            'move_line_ids':[(0,0,{
                'product_id':product.id,
                'product_uom_id':self.uom_unit.id,
                'location_id':self.supplier_location,
                'location_dest_id':self.env.ref('stock.stock_location_stock').id,
                'qty_done':1.00,
            })],
        })
        move1._action_done()
        self.assertEqual(move1.location_dest_id,new_loc)
        positive_quant=product.stock_quant_ids.filtered(lambdaq:q.quantity>0)
        self.assertEqual(positive_quant.location_id,new_loc)

    deftest_mtso_mto(self):
        """Runaprocurementfor5productswhenthereareonly4instockthen
        checkthatMTOisappliedonthemoveswhentheruleissetto'mts_else_mto'
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse.delivery_steps='pick_pack_ship'
        partner_demo_customer=self.partner
        final_location=partner_demo_customer.property_stock_customer
        product_a=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })

        self.env['stock.quant']._update_available_quantity(product_a,warehouse.wh_output_stock_loc_id,4.0)

        #Wesetquantitiesinthestocklocationtoavoidwarnings
        #triggeredby'_onchange_product_id_check_availability'
        self.env['stock.quant']._update_available_quantity(product_a,warehouse.lot_stock_id,4.0)

        #Wealteroneruleandwesetitto'mts_else_mto'
        values={'warehouse_id':warehouse}
        rule=self.env['procurement.group']._get_rule(product_a,final_location,values)
        rule.procure_method='mts_else_mto'

        pg=self.env['procurement.group'].create({'name':'Test-pg-mtso-mto'})

        self.env['procurement.group'].run([
            pg.Procurement(
                product_a,
                5.0,
                product_a.uom_id,
                final_location,
                'test_mtso_mto',
                'test_mtso_mto',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg
                }
            )
        ])

        qty_available=self.env['stock.quant']._get_available_quantity(product_a,warehouse.wh_output_stock_loc_id)

        #3pickingsshouldbecreated.
        picking_ids=self.env['stock.picking'].search([('group_id','=',pg.id)])
        self.assertEqual(len(picking_ids),3)
        forpickinginpicking_ids:
            #OnlythepickingfromStocktoPackshouldbeMTS
            ifpicking.location_id==warehouse.lot_stock_id:
                self.assertEqual(picking.move_lines.procure_method,'make_to_stock')
            else:
                self.assertEqual(picking.move_lines.procure_method,'make_to_order')

            self.assertEqual(len(picking.move_lines),1)
            self.assertEqual(picking.move_lines.product_uom_qty,5,'ThequantityofthemoveshouldbethesameasontheSO')
        self.assertEqual(qty_available,4,'The4productsshouldstillbeavailable')

    deftest_mtso_mts(self):
        """Runaprocurementfor4productswhenthereare4instockthen
        checkthatMTSisappliedonthemoveswhentheruleissetto'mts_else_mto'
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse.delivery_steps='pick_pack_ship'
        partner_demo_customer=self.partner
        final_location=partner_demo_customer.property_stock_customer
        product_a=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })

        self.env['stock.quant']._update_available_quantity(product_a,warehouse.wh_output_stock_loc_id,4.0)

        #Wealteroneruleandwesetitto'mts_else_mto'
        values={'warehouse_id':warehouse}
        rule=self.env['procurement.group']._get_rule(product_a,final_location,values)
        rule.procure_method='mts_else_mto'

        pg=self.env['procurement.group'].create({'name':'Test-pg-mtso-mts'})

        self.env['procurement.group'].run([
            pg.Procurement(
                product_a,
                4.0,
                product_a.uom_id,
                final_location,
                'test_mtso_mts',
                'test_mtso_mts',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg
                }
            )
        ])

        #ApickingshouldbecreatedwithitsmovehavingMTSasprocuremethod.
        picking_ids=self.env['stock.picking'].search([('group_id','=',pg.id)])
        self.assertEqual(len(picking_ids),1)
        picking=picking_ids
        self.assertEqual(picking.move_lines.procure_method,'make_to_stock')
        self.assertEqual(len(picking.move_lines),1)
        self.assertEqual(picking.move_lines.product_uom_qty,4)

    deftest_mtso_multi_pg(self):
        """Run3procurementsfor2productsatthesametimeswhenthereare4instockthen
        checkthatMTSisappliedonthemoveswhentheruleissetto'mts_else_mto'
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse.delivery_steps='pick_pack_ship'
        partner_demo_customer=self.partner
        final_location=partner_demo_customer.property_stock_customer
        product_a=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })

        self.env['stock.quant']._update_available_quantity(product_a,warehouse.wh_output_stock_loc_id,4.0)

        #Wealteroneruleandwesetitto'mts_else_mto'
        values={'warehouse_id':warehouse}
        rule=self.env['procurement.group']._get_rule(product_a,final_location,values)
        rule.procure_method='mts_else_mto'

        pg1=self.env['procurement.group'].create({'name':'Test-pg-mtso-mts-1'})
        pg2=self.env['procurement.group'].create({'name':'Test-pg-mtso-mts-2'})
        pg3=self.env['procurement.group'].create({'name':'Test-pg-mtso-mts-3'})

        self.env['procurement.group'].run([
            pg1.Procurement(
                product_a,
                2.0,
                product_a.uom_id,
                final_location,
                'test_mtso_mts_1',
                'test_mtso_mts_1',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg1
                }
            ),
            pg2.Procurement(
                product_a,
                2.0,
                product_a.uom_id,
                final_location,
                'test_mtso_mts_2',
                'test_mtso_mts_2',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg2
                }
            ),
            pg3.Procurement(
                product_a,
                2.0,
                product_a.uom_id,
                final_location,
                'test_mtso_mts_3',
                'test_mtso_mts_3',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg3
                }
            )
        ])

        pickings_pg1=self.env['stock.picking'].search([('group_id','=',pg1.id)])
        pickings_pg2=self.env['stock.picking'].search([('group_id','=',pg2.id)])
        pickings_pg3=self.env['stock.picking'].search([('group_id','=',pg3.id)])

        #The2firstprocurementsshouldhavecreateonly1pickingsinceenoughquantities
        #areleftinthedeliverylocation
        self.assertEqual(len(pickings_pg1),1)
        self.assertEqual(len(pickings_pg2),1)
        self.assertEqual(pickings_pg1.move_lines.procure_method,'make_to_stock')
        self.assertEqual(pickings_pg2.move_lines.procure_method,'make_to_stock')

        #Thelastoneshouldhave3pickingsasthere'snothingleftinthedeliverylocation
        self.assertEqual(len(pickings_pg3),3)
        forpickinginpickings_pg3:
            #OnlythepickingfromStocktoPackshouldbeMTS
            ifpicking.location_id==warehouse.lot_stock_id:
                self.assertEqual(picking.move_lines.procure_method,'make_to_stock')
            else:
                self.assertEqual(picking.move_lines.procure_method,'make_to_order')

            #Allthemovesshouldbeshouldhavethesamequantityasitisoneachprocurements
            self.assertEqual(len(picking.move_lines),1)
            self.assertEqual(picking.move_lines.product_uom_qty,2)

    deftest_mtso_mto_adjust_01(self):
        """Run'_adjust_procure_method'forproductsA&B:
        -ProductAhas5.0available
        -ProductBhas3.0available
        Stockmoves(SM)arecreatedfor4.0units
        After'_adjust_procure_method':
        -SMforAis'make_to_stock'
        -SMforBis'make_to_order'
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        final_location=self.partner.property_stock_customer
        product_A=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })
        product_B=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
        })

        #Wealteroneruleandwesetitto'mts_else_mto'
        rule=self.env['procurement.group']._get_rule(product_A,final_location,{'warehouse_id':warehouse})
        rule.procure_method='mts_else_mto'

        self.env['stock.quant']._update_available_quantity(product_A,warehouse.lot_stock_id,5.0)
        self.env['stock.quant']._update_available_quantity(product_B,warehouse.lot_stock_id,3.0)

        move_tmpl={
            'name':'Product',
            'product_uom':self.uom_unit.id,
            'product_uom_qty':4.0,
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.partner.property_stock_customer.id,
            'warehouse_id':warehouse.id,
        }
        move_A_vals=dict(move_tmpl)
        move_A_vals.update({
            'product_id':product_A.id,
        })
        move_A=self.env['stock.move'].create(move_A_vals)
        move_B_vals=dict(move_tmpl)
        move_B_vals.update({
            'product_id':product_B.id,
        })
        move_B=self.env['stock.move'].create(move_B_vals)
        moves=move_A+move_B

        self.assertEqual(move_A.procure_method,'make_to_stock','MoveAshouldbe"make_to_stock"')
        self.assertEqual(move_B.procure_method,'make_to_stock','MoveAshouldbe"make_to_order"')
        moves._adjust_procure_method()
        self.assertEqual(move_A.procure_method,'make_to_stock','MoveAshouldbe"make_to_stock"')
        self.assertEqual(move_B.procure_method,'make_to_order','MoveAshouldbe"make_to_order"')

    deftest_mtso_mto_adjust_02(self):
        """Run'_adjust_procure_method'forproductsA&B:
        -ProductAhas5.0available
        -ProductBhas3.0available
        Stockmoves(SM)arecreatedfor2.0+2.0units
        After'_adjust_procure_method':
        -SMforAis'make_to_stock'
        -SMforBis'make_to_stock'and'make_to_order'
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        final_location=self.partner.property_stock_customer
        product_A=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })
        product_B=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
        })

        #Wealteroneruleandwesetitto'mts_else_mto'
        rule=self.env['procurement.group']._get_rule(product_A,final_location,{'warehouse_id':warehouse})
        rule.procure_method='mts_else_mto'

        self.env['stock.quant']._update_available_quantity(product_A,warehouse.lot_stock_id,5.0)
        self.env['stock.quant']._update_available_quantity(product_B,warehouse.lot_stock_id,3.0)

        move_tmpl={
            'name':'Product',
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.partner.property_stock_customer.id,
            'warehouse_id':warehouse.id,
        }
        move_A1_vals=dict(move_tmpl)
        move_A1_vals.update({
            'product_id':product_A.id,
        })
        move_A1=self.env['stock.move'].create(move_A1_vals)
        move_A2_vals=dict(move_tmpl)
        move_A2_vals.update({
            'product_id':product_A.id,
        })
        move_A2=self.env['stock.move'].create(move_A2_vals)
        move_B1_vals=dict(move_tmpl)
        move_B1_vals.update({
            'product_id':product_B.id,
        })
        move_B1=self.env['stock.move'].create(move_B1_vals)
        move_B2_vals=dict(move_tmpl)
        move_B2_vals.update({
            'product_id':product_B.id,
        })
        move_B2=self.env['stock.move'].create(move_B2_vals)
        moves=move_A1+move_A2+move_B1+move_B2

        self.assertEqual(move_A1.procure_method,'make_to_stock','MoveA1shouldbe"make_to_stock"')
        self.assertEqual(move_A2.procure_method,'make_to_stock','MoveA2shouldbe"make_to_stock"')
        self.assertEqual(move_B1.procure_method,'make_to_stock','MoveB1shouldbe"make_to_stock"')
        self.assertEqual(move_B2.procure_method,'make_to_stock','MoveB2shouldbe"make_to_stock"')
        moves._adjust_procure_method()
        self.assertEqual(move_A1.procure_method,'make_to_stock','MoveA1shouldbe"make_to_stock"')
        self.assertEqual(move_A2.procure_method,'make_to_stock','MoveA2shouldbe"make_to_stock"')
        self.assertEqual(move_B1.procure_method,'make_to_stock','MoveB1shouldbe"make_to_stock"')
        self.assertEqual(move_B2.procure_method,'make_to_order','MoveB2shouldbe"make_to_order"')

    deftest_mtso_mto_adjust_03(self):
        """Run'_adjust_procure_method'forproductsAwith4.0available
        2Stockmoves(SM)arecreated:
        -SM1for5.0Units
        -SM2for3.0Units
        SM1isconfirmed,so'virtual_available'is-1.0.
        SM1shouldbecome'make_to_order'
        SM2shouldremain'make_to_stock'
        """
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        final_location=self.partner.property_stock_customer
        product_A=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })

        #Wealteroneruleandwesetitto'mts_else_mto'
        rule=self.env['procurement.group']._get_rule(product_A,final_location,{'warehouse_id':warehouse})
        rule.procure_method='mts_else_mto'

        self.env['stock.quant']._update_available_quantity(product_A,warehouse.lot_stock_id,4.0)

        move_tmpl={
            'name':'Product',
            'product_id':product_A.id,
            'product_uom':self.uom_unit.id,
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.partner.property_stock_customer.id,
            'warehouse_id':warehouse.id,
        }
        move_A1_vals=dict(move_tmpl)
        move_A1_vals.update({
            'product_uom_qty':5.0,
        })
        move_A1=self.env['stock.move'].create(move_A1_vals)
        move_A2_vals=dict(move_tmpl)
        move_A2_vals.update({
            'product_uom_qty':3.0,
        })
        move_A2=self.env['stock.move'].create(move_A2_vals)
        moves=move_A1+move_A2

        self.assertEqual(move_A1.procure_method,'make_to_stock','MoveA1shouldbe"make_to_stock"')
        self.assertEqual(move_A2.procure_method,'make_to_stock','MoveA2shouldbe"make_to_stock"')
        move_A1._action_confirm()
        moves._adjust_procure_method()
        self.assertEqual(move_A1.procure_method,'make_to_order','MoveAshouldbe"make_to_stock"')
        self.assertEqual(move_A2.procure_method,'make_to_stock','MoveAshouldbe"make_to_order"')

    deftest_delay_alert_3(self):
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        warehouse.delivery_steps='pick_pack_ship'
        partner_demo_customer=self.partner
        final_location=partner_demo_customer.property_stock_customer
        product_a=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })
        pg=self.env['procurement.group'].create({'name':'Test-delay_alert_3'})
        self.env['procurement.group'].run([
            pg.Procurement(
                product_a,
                4.0,
                product_a.uom_id,
                final_location,
                'delay',
                'delay',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg
                }
            ),
        ])
        ship,pack,pick=self.env['stock.move'].search([('product_id', '=',product_a.id)])

        #bydefaulttheyallthesame`date`
        self.assertEqual(set((ship+pack+pick).mapped('date')),{pick.date})

        #pick-pack-ship
        ship.date+=timedelta(days=2)
        pack.date+=timedelta(days=1)
        self.assertFalse(pick.delay_alert_date)
        self.assertFalse(pack.delay_alert_date)
        self.assertFalse(ship.delay_alert_date)

        #movethepackaftertheship
        #pick-ship-pack
        pack.date+=timedelta(days=2)
        self.assertFalse(pick.delay_alert_date)
        self.assertFalse(pack.delay_alert_date)
        self.assertTrue(ship.delay_alert_date)
        self.assertAlmostEqual(ship.delay_alert_date,pack.date)

        #restorethepackbeforetheship
        #pick-pack-ship
        pack.date-=timedelta(days=2)
        self.assertFalse(pick.delay_alert_date)
        self.assertFalse(pack.delay_alert_date)
        self.assertFalse(ship.delay_alert_date)

        #movethepickafterthepack
        #pack-ship-pick
        pick.date+=timedelta(days=3)
        self.assertFalse(pick.delay_alert_date)
        self.assertTrue(pack.delay_alert_date)
        self.assertFalse(ship.delay_alert_date)
        self.assertAlmostEqual(pack.delay_alert_date,pick.date)

        #movetheshipbeforethepack
        #ship-pack-pick
        ship.date-=timedelta(days=2)
        self.assertFalse(pick.delay_alert_date)
        self.assertTrue(pack.delay_alert_date)
        self.assertTrue(ship.delay_alert_date)
        self.assertAlmostEqual(pack.delay_alert_date,pick.date)
        self.assertAlmostEqual(ship.delay_alert_date,pack.date)

        #movethepackattheend
        #ship-pick-pack
        pack.date=pick.date+timedelta(days=2)
        self.assertFalse(pick.delay_alert_date)
        self.assertFalse(pack.delay_alert_date)
        self.assertTrue(ship.delay_alert_date)
        self.assertAlmostEqual(ship.delay_alert_date,pack.date)

        #fixtheship
        ship.date=pack.date+timedelta(days=2)
        self.assertFalse(pick.delay_alert_date)
        self.assertFalse(pack.delay_alert_date)
        self.assertFalse(ship.delay_alert_date)


classTestAutoAssign(TestStockCommon):
    defcreate_pick_ship(self):
        picking_client=self.env['stock.picking'].create({
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })

        dest=self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_client.id,
            'location_id':self.pack_location,
            'location_dest_id':self.customer_location,
            'state':'waiting',
            'procure_method':'make_to_order',
        })

        picking_pick=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'picking_type_id':self.picking_type_out,
        })

        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_pick.id,
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'move_dest_ids':[(4,dest.id)],
            'state':'confirmed',
        })
        returnpicking_pick,picking_client

    deftest_auto_assign_0(self):
        """CreateaoutgoingMTSmovewithoutenoughproductsinstock,then
        validateaincomingmovetocheckiftheoutgoingmoveisautomatically
        assigned.
        """
        pack_location=self.env['stock.location'].browse(self.pack_location)
        stock_location=self.env['stock.location'].browse(self.stock_location)

        #createcustomerpickingandmove
        customer_picking=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'picking_type_id':self.picking_type_out,
        })
        customer_move=self.env['stock.move'].create({
            'name':'customermove',
            'location_id':self.stock_location,
            'location_dest_id':self.customer_location,
            'product_id':self.productA.id,
            'product_uom':self.productA.uom_id.id,
            'product_uom_qty':10.0,
            'picking_id':customer_picking.id,
            'picking_type_id':self.picking_type_out,
        })
        customer_picking.action_confirm()
        customer_picking.action_assign()
        self.assertEqual(customer_move.state,'confirmed')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,stock_location),0)

        #createsupplierpickingandmove
        supplier_picking=self.env['stock.picking'].create({
            'location_id':self.customer_location,
            'location_dest_id':self.stock_location,
            'picking_type_id':self.picking_type_in,
        })
        supplier_move=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.customer_location,
            'location_dest_id':self.stock_location,
            'product_id':self.productA.id,
            'product_uom':self.productA.uom_id.id,
            'product_uom_qty':10.0,
            'picking_id':supplier_picking.id,
        })
        customer_picking.action_confirm()
        customer_picking.action_assign()
        supplier_move.quantity_done=10
        supplier_picking._action_done()

        #customermoveshouldbeautomaticallyassignedandnomoreavailableproductinstock
        self.assertEqual(customer_move.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,stock_location),0)

    deftest_auto_assign_1(self):
        """CreateaoutgoingMTOmovewithoutenoughproducts,thenvalidatea
        movetomakeitavailabletocheckiftheoutgoingmoveisnot
        automaticallyassigned.
        """
        picking_pick,picking_client=self.create_pick_ship()
        pack_location=self.env['stock.location'].browse(self.pack_location)
        stock_location=self.env['stock.location'].browse(self.stock_location)

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.productA,stock_location,10.0)

        #createanothermovetomakeproductavailableinpack_location
        picking_pick_2=self.env['stock.picking'].create({
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'picking_type_id':self.picking_type_out,
        })
        self.MoveObj.create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_pick_2.id,
            'location_id':self.stock_location,
            'location_dest_id':self.pack_location,
            'state':'confirmed',
        })
        picking_pick_2.action_assign()
        picking_pick_2.move_lines[0].move_line_ids[0].qty_done=10.0
        picking_pick_2._action_done()

        self.assertEqual(picking_client.state,'waiting',"MTOmovescan'tbeautomaticallyassigned.")
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.productA,pack_location),10.0)

    deftest_serial_lot_ids(self):
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.customer_location=self.env.ref('stock.stock_location_customers')
        self.supplier_location=self.env.ref('stock.stock_location_suppliers')
        self.uom_unit=self.env.ref('uom.product_uom_unit')
        self.product_serial=self.env['product.product'].create({
            'name':'PSerial',
            'type':'product',
            'tracking':'serial',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        move=self.env['stock.move'].create({
            'name':'TestReceive',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.assertEqual(move.state,'draft')
        lot1=self.env['stock.production.lot'].create({
            'name':'serial1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'serial2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot3=self.env['stock.production.lot'].create({
            'name':'serial3',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        move.lot_ids=[(4,lot1.id)]
        move.lot_ids=[(4,lot2.id)]
        move.lot_ids=[(4,lot3.id)]
        self.assertEqual(move.quantity_done,3.0)
        move.lot_ids=[(3,lot2.id)]
        self.assertEqual(move.quantity_done,2.0)

        self.uom_dozen=self.env.ref('uom.product_uom_dozen')
        move=self.env['stock.move'].create({
            'name':'TestReceiveDozen',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_dozen.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move.lot_ids=[(4,lot1.id)]
        move.lot_ids=[(4,lot2.id)]
        move.lot_ids=[(4,lot3.id)]
        self.assertEqual(move.quantity_done,3.0/12.0)

    deftest_update_description(self):
        """Createanemptypicking.Addsamoveonproduct1,selectthepickingtype,add
        againamoveonproduct1.Confirmthepicking.Thetwostockmovesshouldbemerged."""
        product1=self.env['product.product'].create({
            'name':'product',
            'type':'product',
        })
        picking_form=Form(self.env['stock.picking'])
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product1
            move.product_uom_qty=10
            move.location_id=self.env.ref('stock.stock_location_suppliers')
            move.location_dest_id=self.env.ref('stock.stock_location_stock')
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=product1
            move.product_uom_qty=15

        picking=picking_form.save()
        picking.action_confirm()

        self.assertEqual(len(picking.move_lines),1)
        self.assertEqual(picking.move_lines.product_uom_qty,25)
