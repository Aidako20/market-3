#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,timedelta

fromflectraimportfields
fromflectra.testsimportForm
fromflectra.addons.mrp.tests.commonimportTestMrpCommon
fromflectra.exceptionsimportUserError
fromflectra.toolsimportmute_logger


classTestProcurement(TestMrpCommon):

    deftest_procurement(self):
        """Thistestcasewhencreateproductionordercheckprocurementiscreate"""
        #UpdateBOM
        self.bom_3.bom_line_ids.filtered(lambdax:x.product_id==self.product_5).unlink()
        self.bom_1.bom_line_ids.filtered(lambdax:x.product_id==self.product_1).unlink()
        #Updateroute
        self.warehouse=self.env.ref('stock.warehouse0')
        self.warehouse.mto_pull_id.route_id.active=True
        route_manufacture=self.warehouse.manufacture_pull_id.route_id.id
        route_mto=self.warehouse.mto_pull_id.route_id.id
        self.product_4.write({'route_ids':[(6,0,[route_manufacture,route_mto])]})

        #Createproductionorder
        #-------------------------
        #Product6Unit24
        #   Product48Dozen
        #   Product212Unit
        #-----------------------

        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=self.bom_3
        production_form.product_qty=24
        production_form.product_uom_id=self.product_6.uom_id
        production_product_6=production_form.save()
        production_product_6.action_confirm()
        production_product_6.action_assign()

        #checkproductionstateisConfirmed
        self.assertEqual(production_product_6.state,'confirmed')

        #Checkprocurementforproduct4createdornot.
        #Checkitcreatedapurchaseorder

        move_raw_product4=production_product_6.move_raw_ids.filtered(lambdax:x.product_id==self.product_4)
        produce_product_4=self.env['mrp.production'].search([('product_id','=',self.product_4.id),
                                                               ('move_dest_ids','=',move_raw_product4[0].id)])
        #produceproduct
        self.assertEqual(produce_product_4.reservation_state,'confirmed',"Consumematerialnotavailable")

        #Createproductionorder
        #-------------------------
        #Product4 96Unit
        #   Product248Unit
        #---------------------
        #UpdateInventory
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_2.id,
            'inventory_quantity':48,
            'location_id':self.warehouse.lot_stock_id.id,
        })
        produce_product_4.action_assign()
        self.assertEqual(produce_product_4.product_qty,8,"Wrongquantityoffinishproduct.")
        self.assertEqual(produce_product_4.product_uom_id,self.uom_dozen,"Wrongquantityoffinishproduct.")
        self.assertEqual(produce_product_4.reservation_state,'assigned',"Consumematerialnotavailable")

        #produceproduct4
        #---------------

        mo_form=Form(produce_product_4)
        mo_form.qty_producing=produce_product_4.product_qty
        produce_product_4=mo_form.save()
        #CheckprocurementandProductionstateforproduct4.
        produce_product_4.button_mark_done()
        self.assertEqual(produce_product_4.state,'done','Productionordershouldbeinstatedone')

        #Produceproduct6
        #------------------

        #UpdateInventory
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_2.id,
            'inventory_quantity':12,
            'location_id':self.warehouse.lot_stock_id.id,
        })
        production_product_6.action_assign()

        #------------------------------------

        self.assertEqual(production_product_6.reservation_state,'assigned',"Consumematerialnotavailable")
        mo_form=Form(production_product_6)
        mo_form.qty_producing=production_product_6.product_qty
        production_product_6=mo_form.save()
        #CheckprocurementandProductionstateforproduct6.
        production_product_6.button_mark_done()
        self.assertEqual(production_product_6.state,'done','Productionordershouldbeinstatedone')
        self.assertEqual(self.product_6.qty_available,24,'Wrongquantityavailableoffinishedproduct.')

    deftest_procurement_2(self):
        """Checkthatamanufacturingordercreatetherightprocurementswhentherouteareseton
        aparentcategoryofaproduct"""
        #findachildcategoryid
        all_categ_id=self.env['product.category'].search([('parent_id','=',None)],limit=1)
        child_categ_id=self.env['product.category'].search([('parent_id','=',all_categ_id.id)],limit=1)

        #settheproductof`self.bom_1`tothischildcategory
        forbom_line_idinself.bom_1.bom_line_ids:
            #checkthatnoroutesaredefinedontheproduct
            self.assertEqual(len(bom_line_id.product_id.route_ids),0)
            #setthecategoryoftheproducttoachildcategory
            bom_line_id.product_id.categ_id=child_categ_id

        #settheMTOroutetotheparentcategory(all)
        self.warehouse=self.env.ref('stock.warehouse0')
        mto_route=self.warehouse.mto_pull_id.route_id
        mto_route.active=True
        mto_route.product_categ_selectable=True
        all_categ_id.write({'route_ids':[(6,0,[mto_route.id])]})

        #createMO,butcheckitraiseserrorascomponentsareinmaketoorderandnoteveryonehas
        withself.assertRaises(UserError):
            production_form=Form(self.env['mrp.production'])
            production_form.product_id=self.product_4
            production_form.product_uom_id=self.product_4.uom_id
            production_form.product_qty=1
            production_product_4=production_form.save()
            production_product_4.action_confirm()

    deftest_procurement_4(self):
        warehouse=self.env['stock.warehouse'].search([],limit=1)
        product_A=self.env['product.product'].create({
            'name':'productA',
            'type':'product',
            'route_ids':[(4,self.ref('mrp.route_warehouse0_manufacture'))]
        })
        product_B=self.env['product.product'].create({
            'name':'productB',
            'type':'product',
            'route_ids':[(4,self.ref('mrp.route_warehouse0_manufacture'))]
        })
        product_C=self.env['product.product'].create({
            'name':'productC',
            'type':'product',
        })
        product_route=self.env['stock.location.route'].create({
            'name':'Stock->outputroute',
            'product_selectable':True,
            'rule_ids':[(0,0,{
                'name':'Stock->outputrule',
                'action':'pull',
                'picking_type_id':self.ref('stock.picking_type_internal'),
                'location_src_id':self.ref('stock.stock_location_stock'),
                'location_id':self.ref('stock.stock_location_output'),
            })],
        })

        #Setthisrouteon`product.product_product_3`
        product_C.write({
            'route_ids':[(4,product_route.id)]
        })

        bom_A=self.env['mrp.bom'].create({
            'product_id':product_A.id,
            'product_tmpl_id':product_A.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':product_B.id,'product_qty':2.0})
            ]})

        self.env['stock.warehouse.orderpoint'].create({
            'name':'ARR',
            'location_id':warehouse.lot_stock_id.id,
            'product_id':product_A.id,
            'product_min_qty':10,
            'product_max_qty':100,
        })

        bom_B=self.env['mrp.bom'].create({
            'product_id':product_B.id,
            'product_tmpl_id':product_B.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':product_C.id,'product_qty':1.0})
            ]})

        self.env['stock.warehouse.orderpoint'].create({
            'name':'BRR',
            'location_id':warehouse.lot_stock_id.id,
            'product_id':product_B.id,
            'product_min_qty':20,
            'product_max_qty':200,
        })

        self.env['stock.warehouse.orderpoint'].create({
            'name':'CRR',
            'location_id':warehouse.lot_stock_id.id,
            'product_id':product_C.id,
            'product_min_qty':20,
            'product_max_qty':200,
        })

        withmute_logger('flectra.addons.stock.models.procurement'):
            self.env['procurement.group'].run_scheduler()

        production_A=self.env['mrp.production'].search([
            ('product_id','=',product_A.id),
            ('state','=','confirmed')
        ])
        self.assertEqual(production_A.product_uom_qty,100,"100unitsofAshouldbescheduledforproduction")
        production_B=self.env['mrp.production'].search([
            ('product_id','=',product_B.id),
            ('state','=','confirmed')
        ])
        self.assertEqual(sum(production_B.mapped('product_uom_qty')),400,"400unitsofBshouldbescheduledforproduction")

    deftest_procurement_3(self):
        warehouse=self.env['stock.warehouse'].search([],limit=1)
        warehouse.write({'reception_steps':'three_steps'})
        warehouse.mto_pull_id.route_id.active=True
        self.env['stock.location']._parent_store_compute()
        warehouse.reception_route_id.rule_ids.filtered(
            lambdap:p.location_src_id==warehouse.wh_input_stock_loc_idand
            p.location_id==warehouse.wh_qc_stock_loc_id).write({
                'procure_method':'make_to_stock'
            })

        finished_product=self.env['product.product'].create({
            'name':'FinishedProduct',
            'type':'product',
        })
        component=self.env['product.product'].create({
            'name':'Component',
            'type':'product',
            'route_ids':[(4,warehouse.mto_pull_id.route_id.id)]
        })
        self.env['stock.quant']._update_available_quantity(component,warehouse.wh_input_stock_loc_id,100)
        bom=self.env['mrp.bom'].create({
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':component.id,'product_qty':1.0})
            ]})
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finished_product
        mo_form.bom_id=bom
        mo_form.product_qty=5
        mo_form.product_uom_id=finished_product.uom_id
        mo_form.location_src_id=warehouse.lot_stock_id
        mo=mo_form.save()
        mo.action_confirm()
        pickings=self.env['stock.picking'].search([('product_id','=',component.id)])
        self.assertEqual(len(pickings),2.0)
        picking_input_to_qc=pickings.filtered(lambdap:p.location_id==warehouse.wh_input_stock_loc_id)
        picking_qc_to_stock=pickings-picking_input_to_qc
        self.assertTrue(picking_input_to_qc)
        self.assertTrue(picking_qc_to_stock)
        picking_input_to_qc.action_assign()
        self.assertEqual(picking_input_to_qc.state,'assigned')
        picking_input_to_qc.move_line_ids.write({'qty_done':5.0})
        picking_input_to_qc._action_done()
        picking_qc_to_stock.action_assign()
        self.assertEqual(picking_qc_to_stock.state,'assigned')
        picking_qc_to_stock.move_line_ids.write({'qty_done':3.0})
        picking_qc_to_stock.with_context(skip_backorder=True,picking_ids_not_to_backorder=picking_qc_to_stock.ids).button_validate()
        self.assertEqual(picking_qc_to_stock.state,'done')
        mo.action_assign()
        self.assertEqual(mo.move_raw_ids.reserved_availability,3.0)
        produce_form=Form(mo)
        produce_form.qty_producing=3.0
        mo=produce_form.save()
        self.assertEqual(mo.move_raw_ids.quantity_done,3.0)
        picking_qc_to_stock.move_line_ids.qty_done=5.0
        self.assertEqual(mo.move_raw_ids.reserved_availability,5.0)
        self.assertEqual(mo.move_raw_ids.quantity_done,3.0)

    deftest_link_date_mo_moves(self):
        """Checklinkofsheduledateformanufaturingwithdatestockmove."""

        #createaproductwithmanufactureroute
        product_1=self.env['product.product'].create({
            'name':'AAA',
            'route_ids':[(4,self.ref('mrp.route_warehouse0_manufacture'))]
        })

        component_1=self.env['product.product'].create({
            'name':'component',
        })

        self.env['mrp.bom'].create({
            'product_id':product_1.id,
            'product_tmpl_id':product_1.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':component_1.id,'product_qty':1}),
            ]})

        #createamoveforproduct_1fromstocktooutputandreservetotriggerthe
        #rule
        move_dest=self.env['stock.move'].create({
            'name':'move_orig',
            'product_id':product_1.id,
            'product_uom':self.ref('uom.product_uom_unit'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'product_uom_qty':10,
            'procure_method':'make_to_order'
        })

        move_dest._action_confirm()
        mo=self.env['mrp.production'].search([
            ('product_id','=',product_1.id),
            ('state','=','confirmed')
        ])

        self.assertAlmostEqual(mo.move_finished_ids.date,mo.move_raw_ids.date+timedelta(hours=1),delta=timedelta(seconds=1))

        self.assertEqual(len(mo),1,'themanufactureorderisnotcreated')

        mo_form=Form(mo)
        self.assertEqual(mo_form.product_qty,10,'thequantitytoproduceisnotgoodrelativetothemove')

        mo=mo_form.save()

        #Confirmingmocreatefinishedmove
        move_orig=self.env['stock.move'].search([
            ('move_dest_ids','in',move_dest.ids)
        ],limit=1)

        self.assertEqual(len(move_orig),1,'themoveorigisnotcreated')
        self.assertEqual(move_orig.product_qty,10,'thequantitytoproduceisnotgoodrelativetothemove')

        new_sheduled_date=fields.Datetime.to_datetime(mo.date_planned_start)+timedelta(days=5)
        mo_form=Form(mo)
        mo_form.date_planned_start=new_sheduled_date
        mo=mo_form.save()

        self.assertAlmostEqual(mo.move_raw_ids.date,mo.date_planned_start,delta=timedelta(seconds=1))
        self.assertAlmostEqual(mo.move_finished_ids.date,mo.date_planned_finished,delta=timedelta(seconds=1))

    deftest_finished_move_cancellation(self):
        """Checkstateoffinishedmoveoncancellationofrawmoves."""
        product_bottle=self.env['product.product'].create({
            'name':'PlasticBottle',
            'route_ids':[(4,self.ref('mrp.route_warehouse0_manufacture'))]
        })

        component_mold=self.env['product.product'].create({
            'name':'PlasticMold',
        })

        self.env['mrp.bom'].create({
            'product_id':product_bottle.id,
            'product_tmpl_id':product_bottle.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':component_mold.id,'product_qty':1}),
            ]})

        move_dest=self.env['stock.move'].create({
            'name':'move_bottle',
            'product_id':product_bottle.id,
            'product_uom':self.ref('uom.product_uom_unit'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'product_uom_qty':10,
            'procure_method':'make_to_order',
        })

        move_dest._action_confirm()
        mo=self.env['mrp.production'].search([
            ('product_id','=',product_bottle.id),
            ('state','=','confirmed')
        ])
        mo.move_raw_ids[0]._action_cancel()
        self.assertEqual(mo.state,'cancel','Manufacturingordershouldbecancelled.')
        self.assertEqual(mo.move_finished_ids[0].state,'cancel','Finishedmoveshouldbecancelledifmoiscancelled.')
        self.assertEqual(mo.move_dest_ids[0].state,'waiting','DestinationmoveshouldnotbecancelledifprapogationcancelisFalseonmanufacturingrule.')

    deftest_procurement_with_empty_bom(self):
        """EnsurethataprocurementrequestusingaproductwithanemptyBoM
        willcreateaMOindraftstatethatcouldbecompletedafterwards.
        """
        self.warehouse=self.env.ref('stock.warehouse0')
        route_manufacture=self.warehouse.manufacture_pull_id.route_id.id
        route_mto=self.warehouse.mto_pull_id.route_id.id
        product=self.env['product.product'].create({
            'name':'Clafoutis',
            'route_ids':[(6,0,[route_manufacture,route_mto])]
        })
        self.env['mrp.bom'].create({
            'product_id':product.id,
            'product_tmpl_id':product.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
        })
        move_dest=self.env['stock.move'].create({
            'name':'CustomerMTOMove',
            'product_id':product.id,
            'product_uom':self.ref('uom.product_uom_unit'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'product_uom_qty':10,
            'procure_method':'make_to_order',
        })
        move_dest._action_confirm()

        production=self.env['mrp.production'].search([('product_id','=',product.id)])
        self.assertTrue(production)
        self.assertFalse(production.move_raw_ids)
        self.assertEqual(production.state,'draft')

        comp1=self.env['product.product'].create({
            'name':'egg',
        })
        move_values=production._get_move_raw_values(comp1,40.0,self.env.ref('uom.product_uom_unit'))
        self.env['stock.move'].create(move_values)

        production.action_confirm()
        produce_form=Form(production)
        produce_form.qty_producing=production.product_qty
        production=produce_form.save()
        production.button_mark_done()

        move_dest._action_assign()
        self.assertEqual(move_dest.reserved_availability,10.0)

    deftest_auto_assign(self):
        """Whenautoreorderingruleexists,checkforwhen:
        1.Thereisnotenoughofamanufacturedproducttoassign(reservefor)apicking=>auto-create1stMO
        2.ThereisnotenoughofamanufacturedcomponenttoassignthecreatedMO=>auto-create2ndMO
        3.Addanextramanufacturedcomponent(notinstock)to1stMO=>auto-create3rdMO
        4.When2ndMOiscompleted=>auto-assignto1stMO
        5.When1stMOiscompleted=>auto-assigntopicking"""

        self.warehouse=self.env.ref('stock.warehouse0')
        route_manufacture=self.warehouse.manufacture_pull_id.route_id

        product_1=self.env['product.product'].create({
            'name':'Cake',
            'type':'product',
            'route_ids':[(6,0,[route_manufacture.id])]
        })
        product_2=self.env['product.product'].create({
            'name':'CakeMix',
            'type':'product',
            'route_ids':[(6,0,[route_manufacture.id])]
        })
        product_3=self.env['product.product'].create({
            'name':'Flour',
            'type':'consu',
        })

        self.env['mrp.bom'].create({
            'product_id':product_1.id,
            'product_tmpl_id':product_1.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1,
            'consumption':'flexible',
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':product_2.id,'product_qty':1}),
            ]})

        self.env['mrp.bom'].create({
            'product_id':product_2.id,
            'product_tmpl_id':product_2.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':product_3.id,'product_qty':1}),
            ]})

        #extramanufacturedcomponentaddedto1stMOafteritisalreadyconfirmed
        product_4=self.env['product.product'].create({
            'name':'FlavorEnchancer',
            'type':'product',
            'route_ids':[(6,0,[route_manufacture.id])]
        })
        product_5=self.env['product.product'].create({
            'name':'MSG',
            'type':'consu',
        })

        self.env['mrp.bom'].create({
            'product_id':product_4.id,
            'product_tmpl_id':product_4.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':product_5.id,'product_qty':1}),
            ]})

        #setupautoorderpoints(reorderingrules)
        self.env['stock.warehouse.orderpoint'].create({
            'name':'CakeRR',
            'location_id':self.warehouse.lot_stock_id.id,
            'product_id':product_1.id,
            'product_min_qty':0,
            'product_max_qty':5,
        })

        self.env['stock.warehouse.orderpoint'].create({
            'name':'CakeMixRR',
            'location_id':self.warehouse.lot_stock_id.id,
            'product_id':product_2.id,
            'product_min_qty':0,
            'product_max_qty':5,
        })

        self.env['stock.warehouse.orderpoint'].create({
            'name':'FlavorEnchancerRR',
            'location_id':self.warehouse.lot_stock_id.id,
            'product_id':product_4.id,
            'product_min_qty':0,
            'product_max_qty':5,
        })

        #createpickingoutputtotriggercreatingMOforreorderingproduct_1
        pick_output=self.env['stock.picking'].create({
            'name':'CakeDeliveryOrder',
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.warehouse.lot_stock_id.id,
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'move_lines':[(0,0,{
                'name':'/',
                'product_id':product_1.id,
                'product_uom':product_1.uom_id.id,
                'product_uom_qty':10.00,
                'procure_method':'make_to_stock',
            })],
        })
        pick_output.action_confirm() #shouldtriggerorderpointtocreateandconfirm1stMO
        pick_output.action_assign()

        mo=self.env['mrp.production'].search([
            ('product_id','=',product_1.id),
            ('state','=','confirmed')
        ])

        self.assertEqual(len(mo),1,"Manufactureorderwasnotautomaticallycreated")
        mo.action_assign()
        self.assertEqual(mo.move_raw_ids.reserved_availability,0,"Nocomponentsshouldbereservedyet")
        self.assertEqual(mo.product_qty,15,"Quantitytoproduceshouldbepickingdemand+reorderingrulemaxqty")

        #2ndMOforproduct_2shouldhavebeencreatedandconfirmedwhen1stMOforproduct_1wasconfirmed
        mo2=self.env['mrp.production'].search([
            ('product_id','=',product_2.id),
            ('state','=','confirmed')
        ])

        self.assertEqual(len(mo2),1,'Secondmanufactureorderwasnotcreated')
        self.assertEqual(mo2.product_qty,20,"QuantitytoproduceshouldbeMO's'toconsume'qty+reorderingrulemaxqty")
        mo2_form=Form(mo2)
        mo2_form.qty_producing=20
        mo2=mo2_form.save()
        mo2.button_mark_done()

        self.assertEqual(mo.move_raw_ids.reserved_availability,15,"Componentsshouldhavebeenauto-reserved")

        #addnewcomponentto1stMO
        mo_form=Form(mo)
        withmo_form.move_raw_ids.new()asline:
            line.product_id=product_4
            line.product_uom_qty=1
        mo_form.save() #shouldtriggerorderpointtocreateandconfirm3rdMO

        mo3=self.env['mrp.production'].search([
            ('product_id','=',product_4.id),
            ('state','=','confirmed')
        ])

        self.assertEqual(len(mo3),1,'Thirdmanufactureorderforaddedcomponentwasnotcreated')
        self.assertEqual(mo3.product_qty,6,"Quantitytoproduceshouldbe1+reorderingrulemaxqty")

        mo_form=Form(mo)
        mo.move_raw_ids.quantity_done=15
        mo_form.qty_producing=15
        mo=mo_form.save()
        mo.button_mark_done()

        self.assertEqual(pick_output.move_ids_without_package.reserved_availability,10,"Completedproductsshouldhavebeenauto-reservedinpicking")

    deftest_rr_with_dependance_between_bom(self):
        self.warehouse=self.env.ref('stock.warehouse0')
        route_mto=self.warehouse.mto_pull_id.route_id
        route_mto.active=True
        route_manufacture=self.warehouse.manufacture_pull_id.route_id
        product_1=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'route_ids':[(6,0,[route_manufacture.id])]
        })
        product_2=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'route_ids':[(6,0,[route_manufacture.id,route_mto.id])]
        })
        product_3=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'route_ids':[(6,0,[route_manufacture.id])]
        })
        product_4=self.env['product.product'].create({
            'name':'ProductC',
            'type':'consu',
        })

        op1=self.env['stock.warehouse.orderpoint'].create({
            'name':'ProductA',
            'location_id':self.warehouse.lot_stock_id.id,
            'product_id':product_1.id,
            'product_min_qty':1,
            'product_max_qty':20,
        })

        op2=self.env['stock.warehouse.orderpoint'].create({
            'name':'ProductB',
            'location_id':self.warehouse.lot_stock_id.id,
            'product_id':product_3.id,
            'product_min_qty':5,
            'product_max_qty':50,
        })

        self.env['mrp.bom'].create({
            'product_id':product_1.id,
            'product_tmpl_id':product_1.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1,
            'consumption':'flexible',
            'type':'normal',
            'bom_line_ids':[(0,0,{'product_id':product_2.id,'product_qty':1})]
        })

        self.env['mrp.bom'].create({
            'product_id':product_2.id,
            'product_tmpl_id':product_2.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1,
            'consumption':'flexible',
            'type':'normal',
            'bom_line_ids':[(0,0,{'product_id':product_3.id,'product_qty':1})]
        })

        self.env['mrp.bom'].create({
            'product_id':product_3.id,
            'product_tmpl_id':product_3.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1,
            'consumption':'flexible',
            'type':'normal',
            'bom_line_ids':[(0,0,{'product_id':product_4.id,'product_qty':1})]
        })

        (op1|op2)._procure_orderpoint_confirm()
        mo1=self.env['mrp.production'].search([('product_id','=',product_1.id)])
        mo3=self.env['mrp.production'].search([('product_id','=',product_3.id)])

        self.assertEqual(len(mo1),1)
        self.assertEqual(len(mo3),1)
        self.assertEqual(mo1.product_qty,20)
        self.assertEqual(mo3.product_qty,50)

    deftest_several_boms_same_finished_product(self):
        """
        SupposeaproductwithtwoBoMs,eachonebasedonadifferentoperationtype
        Thistestensuresthat,whenrunningthescheduler,thegeneratedMOsarebased
        onthecorrectBoMs
        """
        warehouse=self.env.ref('stock.warehouse0')

        stock_location01=warehouse.lot_stock_id
        stock_location02=stock_location01.copy()

        manu_operation01=warehouse.manu_type_id
        manu_operation02=manu_operation01.copy()
        withForm(manu_operation02)asform:
            form.name='Manufacturing02'
            form.sequence_code='MO2'
            form.default_location_dest_id=stock_location02

        manu_rule01=warehouse.manufacture_pull_id
        manu_route=manu_rule01.route_id
        manu_rule02=manu_rule01.copy()
        withForm(manu_rule02)asform:
            form.picking_type_id=manu_operation02
        manu_route.rule_ids=[(6,0,(manu_rule01+manu_rule02).ids)]

        compo01,compo02,finished=self.env['product.product'].create([{
            'name':'compo01',
            'type':'consu',
        },{
            'name':'compo02',
            'type':'consu',
        },{
            'name':'finished',
            'type':'product',
            'route_ids':[(6,0,manu_route.ids)],
        }])

        bom01_form=Form(self.env['mrp.bom'])
        bom01_form.product_tmpl_id=finished.product_tmpl_id
        bom01_form.code='01'
        bom01_form.picking_type_id=manu_operation01
        withbom01_form.bom_line_ids.new()asline:
            line.product_id=compo01
        bom01=bom01_form.save()

        bom02_form=Form(self.env['mrp.bom'])
        bom02_form.product_tmpl_id=finished.product_tmpl_id
        bom02_form.code='02'
        bom02_form.picking_type_id=manu_operation02
        withbom02_form.bom_line_ids.new()asline:
            line.product_id=compo02
        bom02=bom02_form.save()

        self.env['stock.warehouse.orderpoint'].create([{
            'warehouse_id':warehouse.id,
            'location_id':stock_location01.id,
            'product_id':finished.id,
            'product_min_qty':1,
            'product_max_qty':1,
        },{
            'warehouse_id':warehouse.id,
            'location_id':stock_location02.id,
            'product_id':finished.id,
            'product_min_qty':2,
            'product_max_qty':2,
        }])

        self.env['procurement.group'].run_scheduler()

        mos=self.env['mrp.production'].search([('product_id','=',finished.id)],order='origin')
        self.assertRecordValues(mos,[
            {'product_qty':1,'bom_id':bom01.id,'picking_type_id':manu_operation01.id,'location_dest_id':stock_location01.id},
            {'product_qty':2,'bom_id':bom02.id,'picking_type_id':manu_operation02.id,'location_dest_id':stock_location02.id},
        ])
