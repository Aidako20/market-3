#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.addons.mrp.tests.commonimportTestMrpCommon


classTestMultistepManufacturingWarehouse(TestMrpCommon):

    defsetUp(self):
        super(TestMultistepManufacturingWarehouse,self).setUp()
        #Createwarehouse
        self.customer_location=self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_customers')
        warehouse_form=Form(self.env['stock.warehouse'])
        warehouse_form.name='TestWarehouse'
        warehouse_form.code='TWH'
        self.warehouse=warehouse_form.save()

        self.uom_unit=self.env.ref('uom.product_uom_unit')

        #Createmanufacturedproduct
        product_form=Form(self.env['product.product'])
        product_form.name='Stick'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        product_form.type='product'
        product_form.route_ids.clear()
        product_form.route_ids.add(self.warehouse.manufacture_pull_id.route_id)
        product_form.route_ids.add(self.warehouse.mto_pull_id.route_id)
        self.finished_product=product_form.save()

        #Createrawproductformanufacturedproduct
        product_form=Form(self.env['product.product'])
        product_form.name='RawStick'
        product_form.type='product'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        self.raw_product=product_form.save()

        #Createbomformanufacturedproduct
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.finished_product
        bom_product_form.product_tmpl_id=self.finished_product.product_tmpl_id
        bom_product_form.product_qty=1.0
        bom_product_form.type='normal'
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.raw_product
            bom_line.product_qty=2.0

        self.bom=bom_product_form.save()

    def_check_location_and_routes(self):
        #Checkmanufacturingpullrule.
        self.assertTrue(self.warehouse.manufacture_pull_id)
        self.assertTrue(self.warehouse.manufacture_pull_id.active,self.warehouse.manufacture_to_resupply)
        self.assertTrue(self.warehouse.manufacture_pull_id.route_id)
        #Checknewroutescreatedornot.
        self.assertTrue(self.warehouse.pbm_route_id)
        #Checklocationshouldbecreatedandlinkedtowarehouse.
        self.assertTrue(self.warehouse.pbm_loc_id)
        self.assertEqual(self.warehouse.pbm_loc_id.active,self.warehouse.manufacture_steps!='mrp_one_step',"Inputlocationmustbede-activeforsinglesteponly.")
        self.assertTrue(self.warehouse.manu_type_id.active)

    deftest_00_create_warehouse(self):
        """Warehousetestingfordirectmanufacturing"""
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='mrp_one_step'
        self._check_location_and_routes()
        #Checklocationsofexistingpullrule
        self.assertFalse(self.warehouse.pbm_route_id.rule_ids,'onlytheupdateofglobalmanufacturerouteshouldhappen.')
        self.assertEqual(self.warehouse.manufacture_pull_id.location_id.id,self.warehouse.lot_stock_id.id)

    deftest_01_warehouse_twostep_manufacturing(self):
        """Warehousetestingforpickingbeforemanufacturing"""
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm'
        self._check_location_and_routes()
        self.assertEqual(len(self.warehouse.pbm_route_id.rule_ids),2)
        self.assertEqual(self.warehouse.manufacture_pull_id.location_id.id,self.warehouse.lot_stock_id.id)

    deftest_02_warehouse_twostep_manufacturing(self):
        """Warehousetestingforpickingansstoreaftermanufacturing"""
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'
        self._check_location_and_routes()
        self.assertEqual(len(self.warehouse.pbm_route_id.rule_ids),3)
        self.assertEqual(self.warehouse.manufacture_pull_id.location_id.id,self.warehouse.sam_loc_id.id)

    deftest_manufacturing_3_steps(self):
        """TestMO/pickingbeforemanufacturing/pickingaftermanufacturing
        componentsandmove_orig/move_dest.Ensurethateverythingiscreated
        correctly.
        """
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'

        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.finished_product
        production_form.picking_type_id=self.warehouse.manu_type_id
        production=production_form.save()
        production.action_confirm()

        move_raw_ids=production.move_raw_ids
        self.assertEqual(len(move_raw_ids),1)
        self.assertEqual(move_raw_ids.product_id,self.raw_product)
        self.assertEqual(move_raw_ids.picking_type_id,self.warehouse.manu_type_id)
        pbm_move=move_raw_ids.move_orig_ids
        self.assertEqual(len(pbm_move),1)
        self.assertEqual(pbm_move.location_id,self.warehouse.lot_stock_id)
        self.assertEqual(pbm_move.location_dest_id,self.warehouse.pbm_loc_id)
        self.assertEqual(pbm_move.picking_type_id,self.warehouse.pbm_type_id)
        self.assertFalse(pbm_move.move_orig_ids)

        move_finished_ids=production.move_finished_ids
        self.assertEqual(len(move_finished_ids),1)
        self.assertEqual(move_finished_ids.product_id,self.finished_product)
        self.assertEqual(move_finished_ids.picking_type_id,self.warehouse.manu_type_id)
        sam_move=move_finished_ids.move_dest_ids
        self.assertEqual(len(sam_move),1)
        self.assertEqual(sam_move.location_id,self.warehouse.sam_loc_id)
        self.assertEqual(sam_move.location_dest_id,self.warehouse.lot_stock_id)
        self.assertEqual(sam_move.picking_type_id,self.warehouse.sam_type_id)
        self.assertFalse(sam_move.move_dest_ids)

    deftest_manufacturing_flow(self):
        """Simulateapickpackshipdeliverycombinedwithapickingbefore
        manufacturingandstoreaftermanufacturing.AlsoensurethattheMOand
        themovestostockarecreatedwiththegenericpullrules.
        Inordertotriggertherulewecreateapickingtothecustomerwith
        the'maketoorder'procuremethod
        """
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'
            warehouse.delivery_steps='pick_pack_ship'
        self.warehouse.flush()
        self.env.ref('stock.route_warehouse0_mto').active=True
        self.env['stock.quant']._update_available_quantity(self.raw_product,self.warehouse.lot_stock_id,4.0)
        picking_customer=self.env['stock.picking'].create({
            'location_id':self.warehouse.wh_output_stock_loc_id.id,
            'location_dest_id':self.customer_location,
            'partner_id':self.env['ir.model.data'].xmlid_to_res_id('base.res_partner_4'),
            'picking_type_id':self.warehouse.out_type_id.id,
        })
        self.env['stock.move'].create({
            'name':self.finished_product.name,
            'product_id':self.finished_product.id,
            'product_uom_qty':2,
            'product_uom':self.uom_unit.id,
            'picking_id':picking_customer.id,
            'location_id':self.warehouse.wh_output_stock_loc_id.id,
            'location_dest_id':self.customer_location,
            'procure_method':'make_to_order',
            'origin':'SOURCEDOCUMENT',
            'state':'draft',
        })
        picking_customer.action_confirm()
        production_order=self.env['mrp.production'].search([('product_id','=',self.finished_product.id)])
        self.assertTrue(production_order)
        self.assertEqual(production_order.origin,'SOURCEDOCUMENT','TheMOoriginshouldbetheSOname')
        self.assertNotEqual(production_order.name,'SOURCEDOCUMENT','TheMOnameshouldnotbetheoriginofthemove')

        picking_stock_preprod=self.env['stock.move'].search([
            ('product_id','=',self.raw_product.id),
            ('location_id','=',self.warehouse.lot_stock_id.id),
            ('location_dest_id','=',self.warehouse.pbm_loc_id.id),
            ('picking_type_id','=',self.warehouse.pbm_type_id.id)
        ]).picking_id
        picking_stock_postprod=self.env['stock.move'].search([
            ('product_id','=',self.finished_product.id),
            ('location_id','=',self.warehouse.sam_loc_id.id),
            ('location_dest_id','=',self.warehouse.lot_stock_id.id),
            ('picking_type_id','=',self.warehouse.sam_type_id.id)
        ]).picking_id

        self.assertTrue(picking_stock_preprod)
        self.assertTrue(picking_stock_postprod)
        self.assertEqual(picking_stock_preprod.state,'confirmed')
        self.assertEqual(picking_stock_postprod.state,'waiting')
        self.assertEqual(picking_stock_preprod.origin,production_order.name,'Thepre-prodoriginshouldbetheMOname')
        self.assertEqual(picking_stock_postprod.origin,'SOURCEDOCUMENT','Thepost-prodoriginshouldbetheSOname')

        picking_stock_preprod.action_assign()
        picking_stock_preprod.move_line_ids.qty_done=4
        picking_stock_preprod._action_done()

        self.assertFalse(sum(self.env['stock.quant']._gather(self.raw_product,self.warehouse.lot_stock_id).mapped('quantity')))
        self.assertTrue(self.env['stock.quant']._gather(self.raw_product,self.warehouse.pbm_loc_id))

        production_order.action_assign()
        self.assertEqual(production_order.reservation_state,'assigned')
        self.assertEqual(picking_stock_postprod.state,'waiting')

        produce_form=Form(production_order)
        produce_form.qty_producing=production_order.product_qty
        production_order=produce_form.save()
        production_order.button_mark_done()

        self.assertFalse(sum(self.env['stock.quant']._gather(self.raw_product,self.warehouse.pbm_loc_id).mapped('quantity')))

        self.assertEqual(picking_stock_postprod.state,'assigned')

        picking_stock_pick=self.env['stock.move'].search([
            ('product_id','=',self.finished_product.id),
            ('location_id','=',self.warehouse.lot_stock_id.id),
            ('location_dest_id','=',self.warehouse.wh_pack_stock_loc_id.id),
            ('picking_type_id','=',self.warehouse.pick_type_id.id)
        ]).picking_id
        self.assertEqual(picking_stock_pick.move_lines.move_orig_ids.picking_id,picking_stock_postprod)

    deftest_cancel_propagation(self):
        """Testcancellingmovesina'pickingbefore
        manufacturing'and'storeaftermanufacturing'process.Thepropagationof
        canceldependsonthedefaultvaluesoneachruleofthechain.
        """
        self.warehouse.manufacture_steps='pbm_sam'
        self.warehouse.flush()
        self.env['stock.quant']._update_available_quantity(self.raw_product,self.warehouse.lot_stock_id,4.0)
        picking_customer=self.env['stock.picking'].create({
            'location_id':self.warehouse.lot_stock_id.id,
            'location_dest_id':self.customer_location,
            'partner_id':self.env['ir.model.data'].xmlid_to_res_id('base.res_partner_4'),
            'picking_type_id':self.warehouse.out_type_id.id,
        })
        self.env['stock.move'].create({
            'name':self.finished_product.name,
            'product_id':self.finished_product.id,
            'product_uom_qty':2,
            'picking_id':picking_customer.id,
            'product_uom':self.uom_unit.id,
            'location_id':self.warehouse.lot_stock_id.id,
            'location_dest_id':self.customer_location,
            'procure_method':'make_to_order',
        })
        picking_customer.action_confirm()
        production_order=self.env['mrp.production'].search([('product_id','=',self.finished_product.id)])
        self.assertTrue(production_order)

        move_stock_preprod=self.env['stock.move'].search([
            ('product_id','=',self.raw_product.id),
            ('location_id','=',self.warehouse.lot_stock_id.id),
            ('location_dest_id','=',self.warehouse.pbm_loc_id.id),
            ('picking_type_id','=',self.warehouse.pbm_type_id.id)
        ])
        move_stock_postprod=self.env['stock.move'].search([
            ('product_id','=',self.finished_product.id),
            ('location_id','=',self.warehouse.sam_loc_id.id),
            ('location_dest_id','=',self.warehouse.lot_stock_id.id),
            ('picking_type_id','=',self.warehouse.sam_type_id.id)
        ])

        self.assertTrue(move_stock_preprod)
        self.assertTrue(move_stock_postprod)
        self.assertEqual(move_stock_preprod.state,'confirmed')
        self.assertEqual(move_stock_postprod.state,'waiting')

        move_stock_preprod._action_cancel()
        self.assertEqual(production_order.state,'confirmed')
        production_order.action_cancel()
        self.assertTrue(move_stock_postprod.state,'cancel')

    deftest_no_initial_demand(self):
        """TestMO/pickingbeforemanufacturing/pickingaftermanufacturing
        componentsandmove_orig/move_dest.Ensurethateverythingiscreated
        correctly.
        """
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.finished_product
        production_form.picking_type_id=self.warehouse.manu_type_id
        production=production_form.save()
        production.move_raw_ids.product_uom_qty=0
        production.action_confirm()
        production.action_assign()
        self.assertFalse(production.move_raw_ids.move_orig_ids)
        self.assertEqual(production.state,'confirmed')
        self.assertEqual(production.reservation_state,'assigned')

    deftest_manufacturing_3_steps_flexible(self):
        """TestMO/pickingbeforemanufacturing/pickingaftermanufacturing
        componentsandmove_orig/move_dest.Ensurethatadditionalmovesareput
        inpickingbeforemanufacturingtoo.
        """
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'
        bom=self.env['mrp.bom'].search([
            ('product_id','=',self.finished_product.id)
        ])
        new_product=self.env['product.product'].create({
            'name':'Newproduct',
            'type':'product',
        })
        bom.consumption='flexible'
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.finished_product
        production_form.picking_type_id=self.warehouse.manu_type_id
        production=production_form.save()

        production.action_confirm()

        production_form=Form(production)
        withproduction_form.move_raw_ids.new()asmove:
            move.product_id=new_product
            move.product_uom_qty=2
        production=production_form.save()
        move_raw_ids=production.move_raw_ids
        self.assertEqual(len(move_raw_ids),2)
        pbm_move=move_raw_ids.move_orig_ids
        self.assertEqual(len(pbm_move),2)
        self.assertTrue(new_productinpbm_move.product_id)

    deftest_manufacturing_complex_product_3_steps(self):
        """TestMO/pickingaftermanufacturingacomplexproductwhichuses
        manufacturedcomponents.Ensurethateverythingiscreatedandpicked
        correctly.
        """

        self.warehouse.mto_pull_id.route_id.active=True
        #Creatingcomplexproductwhichtriggeranothermanifacture

        product_form=Form(self.env['product.product'])
        product_form.name='Arrow'
        product_form.type='product'
        product_form.route_ids.clear()
        product_form.route_ids.add(self.warehouse.manufacture_pull_id.route_id)
        product_form.route_ids.add(self.warehouse.mto_pull_id.route_id)
        self.complex_product=product_form.save()

        ##Createrawproductformanufacturedproduct
        product_form=Form(self.env['product.product'])
        product_form.name='RawIron'
        product_form.type='product'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        self.raw_product_2=product_form.save()

        withForm(self.finished_product)asfinished_product:
            finished_product.route_ids.clear()
            finished_product.route_ids.add(self.warehouse.manufacture_pull_id.route_id)
            finished_product.route_ids.add(self.warehouse.mto_pull_id.route_id)

        ##Createbomformanufacturedproduct
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.complex_product
        bom_product_form.product_tmpl_id=self.complex_product.product_tmpl_id
        withbom_product_form.bom_line_ids.new()asline:
            line.product_id=self.finished_product
            line.product_qty=1.0
        withbom_product_form.bom_line_ids.new()asline:
            line.product_id=self.raw_product_2
            line.product_qty=1.0

        self.complex_bom=bom_product_form.save()

        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'

        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.complex_product
        production_form.picking_type_id=self.warehouse.manu_type_id
        production=production_form.save()
        production.action_confirm()

        move_raw_ids=production.move_raw_ids
        self.assertEqual(len(move_raw_ids),2)
        sfp_move_raw_id,raw_move_raw_id=move_raw_ids
        self.assertEqual(sfp_move_raw_id.product_id,self.finished_product)
        self.assertEqual(raw_move_raw_id.product_id,self.raw_product_2)

        formove_raw_idinmove_raw_ids:
            self.assertEqual(move_raw_id.picking_type_id,self.warehouse.manu_type_id)

            pbm_move=move_raw_id.move_orig_ids
            self.assertEqual(len(pbm_move),1)
            self.assertEqual(pbm_move.location_id,self.warehouse.lot_stock_id)
            self.assertEqual(pbm_move.location_dest_id,self.warehouse.pbm_loc_id)
            self.assertEqual(pbm_move.picking_type_id,self.warehouse.pbm_type_id)

        #Checkmovelocations
        move_finished_ids=production.move_finished_ids
        self.assertEqual(len(move_finished_ids),1)
        self.assertEqual(move_finished_ids.product_id,self.complex_product)
        self.assertEqual(move_finished_ids.picking_type_id,self.warehouse.manu_type_id)
        sam_move=move_finished_ids.move_dest_ids
        self.assertEqual(len(sam_move),1)
        self.assertEqual(sam_move.location_id,self.warehouse.sam_loc_id)
        self.assertEqual(sam_move.location_dest_id,self.warehouse.lot_stock_id)
        self.assertEqual(sam_move.picking_type_id,self.warehouse.sam_type_id)
        self.assertFalse(sam_move.move_dest_ids)

        subproduction=self.env['mrp.production'].browse(production.id+1)
        subproduction.invalidate_cache(fnames=['picking_ids'],ids=subproduction.ids)
        sfp_pickings=subproduction.picking_ids.sorted('id')

        #SFPProduction:2pickings,1group
        self.assertEqual(len(sfp_pickings),2)
        self.assertEqual(sfp_pickings.mapped('group_id'),subproduction.procurement_group_id)

        ##MoveRawStick-Stock->Preprocessing
        picking=sfp_pickings[0]
        self.assertEqual(len(picking.move_lines),1)
        picking.move_lines[0].product_id=self.raw_product

        ##MoveSFP-PostProcessing->Stock
        picking=sfp_pickings[1]
        self.assertEqual(len(picking.move_lines),1)
        picking.move_lines[0].product_id=self.finished_product

        #Mainproduction2pickings,1group
        pickings=production.picking_ids.sorted('id')
        self.assertEqual(len(pickings),2)
        self.assertEqual(pickings.mapped('group_id'),production.procurement_group_id)

        ##Move2componentsStock->Preprocessing
        picking=pickings[0]
        self.assertEqual(len(picking.move_lines),2)
        picking.move_lines[0].product_id=self.finished_product
        picking.move_lines[1].product_id=self.raw_product_2

        ##MoveFPPostProcessing->Stock
        picking=pickings[1]
        self.assertEqual(len(picking.move_lines),1)
        picking.product_id=self.complex_product

        #MOsarecorrectlylinkedtoeachother
        self.assertEqual(production.mrp_production_child_count,1)
        self.assertEqual(production.mrp_production_source_count,0)
        self.assertEqual(subproduction.mrp_production_child_count,0)
        self.assertEqual(subproduction.mrp_production_source_count,1)
        child_action=production.action_view_mrp_production_childs()
        source_action=subproduction.action_view_mrp_production_sources()
        self.assertEqual(child_action.get('res_id'),subproduction.id)
        self.assertEqual(source_action.get('res_id'),production.id)

    deftest_3_steps_and_byproduct(self):
        """SupposeawarehousewithManufactureoptionsetto'3setps'andaproductP01withareorderingrule.
        SupposeP01hasaBoMandthisBoMmentionsthatwhensomeP01areproduced,someP02areproducedtoo.
        ThistestensuresthatwhenaMOisgeneratedthankstothereorderingrule,2pickingsarealso
        generated:
            -Onetobringthecomponents
            -AnothertoreturntheP01andP02produced
        """
        warehouse=self.warehouse
        warehouse.manufacture_steps='pbm_sam'
        warehouse_stock_location=warehouse.lot_stock_id
        pre_production_location=warehouse.pbm_loc_id
        post_production_location=warehouse.sam_loc_id

        one_unit_uom=self.env['ir.model.data'].xmlid_to_object('uom.product_uom_unit')
        [two_units_uom,four_units_uom]=self.env['uom.uom'].create([{
            'name':'x%s'%i,
            'category_id':self.ref('uom.product_uom_categ_unit'),
            'uom_type':'bigger',
            'factor_inv':i,
        }foriin[2,4]])

        finished_product=self.env['product.product'].create({
            'name':'SuperProduct',
            'route_ids':[(4,self.ref('mrp.route_warehouse0_manufacture'))],
            'type':'product',
        })
        secondary_product=self.env['product.product'].create({
            'name':'Secondary',
            'type':'product',
        })
        component=self.env['product.product'].create({
            'name':'Component',
            'type':'consu',
        })

        bom=self.env['mrp.bom'].create({
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':two_units_uom.id,
            'bom_line_ids':[(0,0,{
                'product_id':component.id,
                'product_qty':1,
                'product_uom_id':one_unit_uom.id,
            })],
            'byproduct_ids':[(0,0,{
                'product_id':secondary_product.id,
                'product_qty':1,
                'product_uom_id':four_units_uom.id,
            })],
        })

        orderpoint=self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id':warehouse.id,
            'location_id':warehouse_stock_location.id,
            'product_id':finished_product.id,
            'product_min_qty':2,
            'product_max_qty':2,
        })

        self.env['procurement.group'].run_scheduler()
        mo=self.env['mrp.production'].search([('product_id','=',finished_product.id)])
        pickings=mo.picking_ids
        self.assertEqual(len(pickings),2)

        preprod_picking=pickings[0]ifpickings[0].location_id==warehouse_stock_locationelsepickings[1]
        self.assertEqual(preprod_picking.location_id,warehouse_stock_location)
        self.assertEqual(preprod_picking.location_dest_id,pre_production_location)

        postprod_picking=pickings-preprod_picking
        self.assertEqual(postprod_picking.location_id,post_production_location)
        self.assertEqual(postprod_picking.location_dest_id,warehouse_stock_location)

        postprod_SML=postprod_picking.move_lines
        self.assertEqual(len(postprod_SML),2)
        self.assertEqual(postprod_SML.location_id,post_production_location)
        self.assertEqual(postprod_SML.location_dest_id,warehouse_stock_location)

        finished_product_SML=postprod_SML[0]ifpostprod_SML[0].product_id==finished_productelsepostprod_SML[1]
        secondary_product_SML=postprod_SML-finished_product_SML
        self.assertEqual(finished_product_SML.product_uom.id,one_unit_uom.id)
        self.assertEqual(finished_product_SML.product_uom_qty,2)
        self.assertEqual(secondary_product_SML.product_uom.id,four_units_uom.id)
        self.assertEqual(secondary_product_SML.product_uom_qty,1)

    deftest_2_steps_and_additional_moves(self):
        """Supposea2-stepsconfiguration.IfauseraddsaproducttoanexistingdraftMOandthen
        confirmsit,theassociatedpickingshouldincludesthisnewproduct"""
        self.warehouse.manufacture_steps='pbm'

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=self.bom.product_id
        mo_form.picking_type_id=self.warehouse.manu_type_id
        mo=mo_form.save()

        component_move=mo.move_raw_ids[0]
        mo.with_context(default_raw_material_production_id=mo.id).move_raw_ids=[
            [0,0,{
                'location_id':component_move.location_id.id,
                'location_dest_id':component_move.location_dest_id.id,
                'picking_type_id':component_move.picking_type_id.id,
                'product_id':self.product_2.id,
                'name':self.product_2.display_name,
                'product_uom_qty':1,
                'product_uom':self.product_2.uom_id.id,
                'warehouse_id':component_move.warehouse_id.id,
                'raw_material_production_id':mo.id,
            }]
        ]

        mo.action_confirm()

        self.assertEqual(self.bom.bom_line_ids.product_id+self.product_2,mo.picking_ids.move_lines.product_id)

    deftest_manufacturing_3_steps_trigger_reordering_rules(self):
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'

        withForm(self.raw_product)asp:
            p.route_ids.clear()
            p.route_ids.add(self.warehouse.manufacture_pull_id.route_id)

        #CreateanadditionalBoMforcomponent
        product_form=Form(self.env['product.product'])
        product_form.name='Wood'
        product_form.type='product'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        self.wood_product=product_form.save()

        #Createbomformanufacturedproduct
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.raw_product
        bom_product_form.product_tmpl_id=self.raw_product.product_tmpl_id
        bom_product_form.product_qty=1.0
        bom_product_form.type='normal'
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.wood_product
            bom_line.product_qty=1.0

        bom_product_form.save()

        self.env['stock.quant']._update_available_quantity(
            self.finished_product,self.warehouse.lot_stock_id,-1.0)

        rr_form=Form(self.env['stock.warehouse.orderpoint'])
        rr_form.product_id=self.wood_product
        rr_form.location_id=self.warehouse.lot_stock_id
        rr_form.save()

        rr_form=Form(self.env['stock.warehouse.orderpoint'])
        rr_form.product_id=self.finished_product
        rr_form.location_id=self.warehouse.lot_stock_id
        rr_finish=rr_form.save()

        rr_form=Form(self.env['stock.warehouse.orderpoint'])
        rr_form.product_id=self.raw_product
        rr_form.location_id=self.warehouse.lot_stock_id
        rr_form.save()

        self.env['procurement.group'].run_scheduler()

        pickings_component=self.env['stock.picking'].search(
            [('product_id','=',self.wood_product.id)])
        self.assertTrue(pickings_component)
        self.assertTrue(rr_finish.nameinpickings_component.origin)

    deftest_manufacturing_bom_from_reordering_rules(self):
        """
            CheckthatthemanufacturingorderiscreatedwiththeBoMsetinthereordingrule:
                -Createaproductwith2billofmaterials,
                -Createanorderpointforthisproductspecifyingthe2ndBoMthatmustbeused,
                -CheckthattheMOhasbeencreatedwiththe2ndBoM
        """
        manufacturing_route=self.env['stock.rule'].search([
            ('action','=','manufacture')]).route_id
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm_sam'
        finished_product=self.env['product.product'].create({
            'name':'Product',
            'type':'product',
            'route_ids':manufacturing_route,
        })
        self.env['mrp.bom'].create({
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':finished_product.uom_id.id,
            'type':'normal',
        })
        bom_2=self.env['mrp.bom'].create({
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':finished_product.uom_id.id,
            'type':'normal',
        })
        self.env['stock.warehouse.orderpoint'].create({
            'name':'OrderpointforP1',
            'product_id':self.finished_product.id,
            'product_min_qty':1,
            'product_max_qty':1,
            'route_id':manufacturing_route.id,
            'bom_id':bom_2.id,
        })
        self.env['procurement.group'].run_scheduler()
        mo=self.env['mrp.production'].search([('product_id','=',self.finished_product.id)])
        self.assertEqual(len(mo),1)
        self.assertEqual(mo.product_qty,1.0)
        self.assertEqual(mo.bom_id,bom_2)
