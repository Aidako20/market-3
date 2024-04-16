#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

from.importcommon
fromflectra.exceptionsimportUserError
fromflectra.testsimportForm


classTestWarehouse(common.TestMrpCommon):
    defsetUp(self):
        super(TestWarehouse,self).setUp()

        unit=self.env.ref("uom.product_uom_unit")
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.depot_location=self.env['stock.location'].create({
            'name':'Depot',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env["stock.putaway.rule"].create({
            "location_in_id":self.stock_location.id,
            "location_out_id":self.depot_location.id,
            'category_id':self.env.ref('product.product_category_all').id,
        })
        mrp_workcenter=self.env['mrp.workcenter'].create({
            'name':'AssemblyLine1',
            'resource_calendar_id':self.env.ref('resource.resource_calendar_std').id,
        })
        inventory=self.env['stock.inventory'].create({
            'name':'Initialinventory',
            'line_ids':[(0,0,{
                'product_id':self.graphics_card.id,
                'product_uom_id':self.graphics_card.uom_id.id,
                'product_qty':16.0,
                'location_id':self.stock_location_14.id,
            })]
        })
        inventory.action_start()
        inventory.action_validate()

        self.bom_laptop=self.env['mrp.bom'].create({
            'product_tmpl_id':self.laptop.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':unit.id,
            'consumption':'flexible',
            'bom_line_ids':[(0,0,{
                'product_id':self.graphics_card.id,
                'product_qty':1,
                'product_uom_id':unit.id
            })],
            'operation_ids':[
                (0,0,{'name':'CuttingMachine','workcenter_id':self.workcenter_1.id,'time_cycle':12,'sequence':1}),
            ],
        })

    defnew_mo_laptop(self):
        form=Form(self.env['mrp.production'])
        form.product_id=self.laptop
        form.product_qty=1
        form.bom_id=self.bom_laptop
        p=form.save()
        p.action_confirm()
        p.action_assign()
        returnp

    deftest_manufacturing_route(self):
        warehouse_1_stock_manager=self.warehouse_1.with_user(self.user_stock_manager)
        manu_rule=self.env['stock.rule'].search([
            ('action','=','manufacture'),
            ('warehouse_id','=',self.warehouse_1.id)])
        self.assertEqual(self.warehouse_1.manufacture_pull_id,manu_rule)
        manu_route=manu_rule.route_id
        self.assertIn(manu_route,warehouse_1_stock_manager._get_all_routes())
        warehouse_1_stock_manager.write({
            'manufacture_to_resupply':False
        })
        self.assertFalse(self.warehouse_1.manufacture_pull_id.active)
        self.assertFalse(self.warehouse_1.manu_type_id.active)
        self.assertNotIn(manu_route,warehouse_1_stock_manager._get_all_routes())
        warehouse_1_stock_manager.write({
            'manufacture_to_resupply':True
        })
        manu_rule=self.env['stock.rule'].search([
            ('action','=','manufacture'),
            ('warehouse_id','=',self.warehouse_1.id)])
        self.assertEqual(self.warehouse_1.manufacture_pull_id,manu_rule)
        self.assertTrue(self.warehouse_1.manu_type_id.active)
        self.assertIn(manu_route,warehouse_1_stock_manager._get_all_routes())

    deftest_manufacturing_scrap(self):
        """
            Testingtodoascrapofconsumedmaterial.
        """

        #Updatedemoproducts
        (self.product_4|self.product_2).write({
            'tracking':'lot',
        })

        #UpdateBillOfMaterialtoremoveproductwithphantombom.
        self.bom_3.bom_line_ids.filtered(lambdax:x.product_id==self.product_5).unlink()

        #CreateInventoryAdjustmentForStickandStoneToolswithlot.
        lot_product_4=self.env['stock.production.lot'].create({
            'name':'0000000000001',
            'product_id':self.product_4.id,
            'company_id':self.env.company.id,
        })
        lot_product_2=self.env['stock.production.lot'].create({
            'name':'0000000000002',
            'product_id':self.product_2.id,
            'company_id':self.env.company.id,
        })

        stock_inv_product_4=self.env['stock.inventory'].create({
            'name':'StockInventoryforStick',
            'product_ids':[(4,self.product_4.id)],
            'line_ids':[
                (0,0,{'product_id':self.product_4.id,'product_uom_id':self.product_4.uom_id.id,'product_qty':8,'prod_lot_id':lot_product_4.id,'location_id':self.stock_location_14.id}),
            ]})

        stock_inv_product_2=self.env['stock.inventory'].create({
            'name':'StockInventoryforStoneTools',
            'product_ids':[(4,self.product_2.id)],
            'line_ids':[
                (0,0,{'product_id':self.product_2.id,'product_uom_id':self.product_2.uom_id.id,'product_qty':12,'prod_lot_id':lot_product_2.id,'location_id':self.stock_location_14.id})
            ]})
        (stock_inv_product_4|stock_inv_product_2)._action_start()
        stock_inv_product_2.action_validate()
        stock_inv_product_4.action_validate()

        #CreateManufacturingorder.
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=self.bom_3
        production_form.product_qty=12
        production_form.product_uom_id=self.product_6.uom_id
        production_3=production_form.save()
        production_3.action_confirm()
        production_3.action_assign()

        #CheckManufacturingorder'savailability.
        self.assertEqual(production_3.reservation_state,'assigned',"Productionorder'savailabilityshouldbeAvailable.")

        location_id=production_3.move_raw_ids.filtered(lambdax:x.statenotin('done','cancel'))andproduction_3.location_src_id.idorproduction_3.location_dest_id.id,

        #ScrapProductWoodwithoutlottocheckassertraise?.
        scrap_id=self.env['stock.scrap'].with_context(active_model='mrp.production',active_id=production_3.id).create({'product_id':self.product_2.id,'scrap_qty':1.0,'product_uom_id':self.product_2.uom_id.id,'location_id':location_id,'production_id':production_3.id})
        withself.assertRaises(UserError):
            scrap_id.do_scrap()

        #ScrapProductWoodwithlot.
        self.env['stock.scrap'].with_context(active_model='mrp.production',active_id=production_3.id).create({'product_id':self.product_2.id,'scrap_qty':1.0,'product_uom_id':self.product_2.uom_id.id,'location_id':location_id,'lot_id':lot_product_2.id,'production_id':production_3.id})

        #Checkscrapmoveiscreatedforthisproductionorder.
        #TODO:shouldcheckwithscrapobjectslinkinbetween

#       scrap_move=production_3.move_raw_ids.filtered(lambdax:x.product_id==self.product_2andx.scrapped)
#       self.assertTrue(scrap_move,"Therearenoanyscrapmovecreatedforproductionorder.")

    deftest_putaway_after_manufacturing_3(self):
        """Thistestchecksatrackedmanufacturedproductwillgotolocation
        definedinputawaystrategywhentheproductionisrecordedwith
        product.producewizard.
        """
        self.laptop.tracking='serial'
        mo_laptop=self.new_mo_laptop()
        serial=self.env['stock.production.lot'].create({'product_id':self.laptop.id,'company_id':self.env.company.id})

        mo_form=Form(mo_laptop)
        mo_form.qty_producing=1
        mo_form.lot_producing_id=serial
        mo_laptop=mo_form.save()
        mo_laptop.button_mark_done()

        #Wecheckifthelaptopgointhedepotandnotinthestock
        move=mo_laptop.move_finished_ids
        location_dest=move.move_line_ids.location_dest_id
        self.assertEqual(location_dest.id,self.depot_location.id)
        self.assertNotEqual(location_dest.id,self.stock_location.id)

classTestKitPicking(common.TestMrpCommon):
    defsetUp(self):
        super(TestKitPicking,self).setUp()

        defcreate_product(name):
            p=Form(self.env['product.product'])
            p.name=name
            p.type='product'
            returnp.save()

        #Createakit'kit_parent':
        #---------------------------
        #
        #kit_parent--|-kit_2x2--|-component_dx1
        #             |            |-kit_1x2-------|-component_a  x2
        #             |                               |-component_b  x1
        #             |                               |-component_c  x3
        #             |
        #             |-kit_3x1--|-component_fx1
        #             |            |-component_gx2
        #             |
        #             |-component_ex1
        #Creatingallcomponents
        component_a=create_product('CompA')
        component_b=create_product('CompB')
        component_c=create_product('CompC')
        component_d=create_product('CompD')
        component_e=create_product('CompE')
        component_f=create_product('CompF')
        component_g=create_product('CompG')
        #Creatingallkits
        kit_1=create_product('Kit1')
        kit_2=create_product('Kit2')
        kit_3=create_product('kit3')
        self.kit_parent=create_product('KitParent')
        #Linkingthekitsandthecomponentsviasome'phantom'BoMs
        bom_kit_1=self.env['mrp.bom'].create({
            'product_tmpl_id':kit_1.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})
        BomLine=self.env['mrp.bom.line']
        BomLine.create({
            'product_id':component_a.id,
            'product_qty':2.0,
            'bom_id':bom_kit_1.id})
        BomLine.create({
            'product_id':component_b.id,
            'product_qty':1.0,
            'bom_id':bom_kit_1.id})
        BomLine.create({
            'product_id':component_c.id,
            'product_qty':3.0,
            'bom_id':bom_kit_1.id})
        bom_kit_2=self.env['mrp.bom'].create({
            'product_tmpl_id':kit_2.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})
        BomLine.create({
            'product_id':component_d.id,
            'product_qty':1.0,
            'bom_id':bom_kit_2.id})
        BomLine.create({
            'product_id':kit_1.id,
            'product_qty':2.0,
            'bom_id':bom_kit_2.id})
        bom_kit_parent=self.env['mrp.bom'].create({
            'product_tmpl_id':self.kit_parent.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})
        BomLine.create({
            'product_id':component_e.id,
            'product_qty':1.0,
            'bom_id':bom_kit_parent.id})
        BomLine.create({
            'product_id':kit_2.id,
            'product_qty':2.0,
            'bom_id':bom_kit_parent.id})
        bom_kit_3=self.env['mrp.bom'].create({
            'product_tmpl_id':kit_3.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})
        BomLine.create({
            'product_id':component_f.id,
            'product_qty':1.0,
            'bom_id':bom_kit_3.id})
        BomLine.create({
            'product_id':component_g.id,
            'product_qty':2.0,
            'bom_id':bom_kit_3.id})
        BomLine.create({
            'product_id':kit_3.id,
            'product_qty':1.0,
            'bom_id':bom_kit_parent.id})

        #Wecreatean'immediatetransfer'receiptforx3kit_parent
        self.test_partner=self.env['res.partner'].create({
            'name':'NotthatGuyagain',
        })
        self.test_supplier=self.env['stock.location'].create({
            'name':'supplier',
            'usage':'supplier',
            'location_id':self.env.ref('stock.stock_location_stock').id,
        })

        self.expected_quantities={
            component_a:24,
            component_b:12,
            component_c:36,
            component_d:6,
            component_e:3,
            component_f:3,
            component_g:6
        }

    deftest_kit_immediate_transfer(self):
        """Makesureakitissplitinthecorrectsquantity_donebycomponentsincaseofan
        immediatetransfer.
        """
        picking=self.env['stock.picking'].create({
            'location_id':self.test_supplier.id,
            'location_dest_id':self.warehouse_1.wh_input_stock_loc_id.id,
            'partner_id':self.test_partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'immediate_transfer':True
        })
        move_receipt_1=self.env['stock.move'].create({
            'name':self.kit_parent.name,
            'product_id':self.kit_parent.id,
            'quantity_done':3,
            'product_uom':self.kit_parent.uom_id.id,
            'picking_id':picking.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'location_id': self.test_supplier.id,
            'location_dest_id':self.warehouse_1.wh_input_stock_loc_id.id,
        })
        picking.button_validate()

        #Wecheckthatthepickinghasthecorrectquantitiesafteritsmoveweresplitted.
        self.assertEqual(len(picking.move_lines),7)
        formove_lineinpicking.move_lines:
            self.assertEqual(move_line.quantity_done,self.expected_quantities[move_line.product_id])

    deftest_kit_planned_transfer(self):
        """Makesureakitissplitinthecorrectsproduct_qtybycomponentsincaseofa
        plannedtransfer.
        """
        picking=self.env['stock.picking'].create({
            'location_id':self.test_supplier.id,
            'location_dest_id':self.warehouse_1.wh_input_stock_loc_id.id,
            'partner_id':self.test_partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'immediate_transfer':False,
        })
        move_receipt_1=self.env['stock.move'].create({
            'name':self.kit_parent.name,
            'product_id':self.kit_parent.id,
            'product_uom_qty':3,
            'product_uom':self.kit_parent.uom_id.id,
            'picking_id':picking.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'location_id': self.test_supplier.id,
            'location_dest_id':self.warehouse_1.wh_input_stock_loc_id.id,
        })
        picking.action_confirm()

        #Wecheckthatthepickinghasthecorrectquantitiesafteritsmoveweresplitted.
        self.assertEqual(len(picking.move_lines),7)
        formove_lineinpicking.move_lines:
            self.assertEqual(move_line.product_qty,self.expected_quantities[move_line.product_id])

    deftest_add_sml_with_kit_to_confirmed_picking(self):
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        customer_location=self.env.ref('stock.stock_location_customers')
        stock_location=warehouse.lot_stock_id
        in_type=warehouse.in_type_id

        self.bom_4.type='phantom'
        kit=self.bom_4.product_id
        compo=self.bom_4.bom_line_ids.product_id
        product=self.env['product.product'].create({'name':'SuperProduct','type':'product'})

        receipt=self.env['stock.picking'].create({
            'picking_type_id':in_type.id,
            'location_id':customer_location.id,
            'location_dest_id':stock_location.id,
            'move_lines':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':1,
                'product_uom':product.uom_id.id,
                'location_id':customer_location.id,
                'location_dest_id':stock_location.id,
            })]
        })
        receipt.action_confirm()

        receipt.move_line_ids.qty_done=1
        receipt.move_line_ids=[(0,0,{
            'product_id':kit.id,
            'qty_done':1,
            'product_uom_id':kit.uom_id.id,
            'location_id':customer_location.id,
            'location_dest_id':stock_location.id,
        })]

        receipt.button_validate()

        self.assertEqual(receipt.state,'done')
        self.assertRecordValues(receipt.move_lines,[
            {'product_id':product.id,'quantity_done':1,'state':'done'},
            {'product_id':compo.id,'quantity_done':1,'state':'done'},
        ])
