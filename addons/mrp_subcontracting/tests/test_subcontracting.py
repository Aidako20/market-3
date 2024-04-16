#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.tests.commonimportTransactionCase
fromflectra.addons.mrp_subcontracting.tests.commonimportTestMrpSubcontractingCommon

fromflectra.testsimporttagged
fromdateutil.relativedeltaimportrelativedelta


@tagged('post_install','-at_install')
classTestSubcontractingBasic(TransactionCase):
    deftest_subcontracting_location_1(self):
        """Checksthecreationandpresenceofthesubcontractinglocation."""
        self.assertTrue(self.env.company.subcontracting_location_id)
        self.assertTrue(self.env.company.subcontracting_location_id.active)
        company2=self.env['res.company'].create({'name':'TestCompany'})
        self.assertTrue(company2.subcontracting_location_id)
        self.assertTrue(self.env.company.subcontracting_location_id!=company2.subcontracting_location_id)


classTestSubcontractingFlows(TestMrpSubcontractingCommon):
    deftest_flow_1(self):
        """Don'ttickanyrouteonthecomponentsandtriggerthecreationofthesubcontracting
        manufacturingorderthroughareceiptpicking.Createareorderingruleinthe
        subcontractinglocationsforacomponentandruntheschedulertoresupply.Checksifthe
        resupplyingactuallyworks
        """
        #ChecksubcontractingpickingType
        self.assertTrue(all(self.env['stock.warehouse'].search([]).with_context(active_test=False).mapped('subcontracting_type_id.use_create_components_lots')))
        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        #Nothingshouldbetracked
        self.assertTrue(all(m.product_uom_qty==m.reserved_availabilityforminpicking_receipt.move_lines))
        self.assertEqual(picking_receipt.state,'assigned')
        self.assertFalse(picking_receipt.display_action_record_components)

        #Checkthecreatedmanufacturingorder
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertEqual(len(mo),1)
        self.assertEqual(len(mo.picking_ids),0)
        wh=picking_receipt.picking_type_id.warehouse_id
        self.assertEqual(mo.picking_type_id,wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        #CreateaRR
        pg1=self.env['procurement.group'].create({})
        self.env['stock.warehouse.orderpoint'].create({
            'name':'xxx',
            'product_id':self.comp1.id,
            'product_min_qty':0,
            'product_max_qty':0,
            'location_id':self.env.user.company_id.subcontracting_location_id.id,
            'group_id':pg1.id,
        })

        #Runtheschedulerandcheckthecreatedpicking
        self.env['procurement.group'].run_scheduler()
        picking=self.env['stock.picking'].search([('group_id','=',pg1.id)])
        self.assertEqual(len(picking),1)
        self.assertEqual(picking.picking_type_id,wh.out_type_id)
        picking_receipt.move_lines.quantity_done=1
        picking_receipt.button_validate()
        self.assertEqual(mo.state,'done')

        #Availablequantitiesshouldbenegativeatthesubcontractinglocationforeachcomponents
        avail_qty_comp1=self.env['stock.quant']._get_available_quantity(self.comp1,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_comp2=self.env['stock.quant']._get_available_quantity(self.comp2,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_finished=self.env['stock.quant']._get_available_quantity(self.finished,wh.lot_stock_id)
        self.assertEqual(avail_qty_comp1,-1)
        self.assertEqual(avail_qty_comp2,-1)
        self.assertEqual(avail_qty_finished,1)

        #Ensurereturnstosubcontractorlocation
        return_form=Form(self.env['stock.return.picking'].with_context(active_id=picking_receipt.id,active_model='stock.picking'))
        return_wizard=return_form.save()
        return_picking_id,pick_type_id=return_wizard._create_returns()
        return_picking=self.env['stock.picking'].browse(return_picking_id)
        self.assertEqual(len(return_picking),1)
        self.assertEqual(return_picking.move_lines.location_dest_id,self.subcontractor_partner1.property_stock_subcontractor)

    deftest_flow_2(self):
        """Tick"ResupplySubcontractoronOrder"onthecomponentsandtriggerthecreationof
        thesubcontractingmanufacturingorderthroughareceiptpicking.Checksiftheresupplying
        actuallyworks.Alsosetadifferentsubcontractinglocationonthepartner.
        """
        #Tick"resupplysubconractoronorder"
        resupply_sub_on_order_route=self.env['stock.location.route'].search([('name','=','ResupplySubcontractoronOrder')])
        (self.comp1+self.comp2).write({'route_ids':[(4,resupply_sub_on_order_route.id,None)]})
        #Createadifferentsubcontractlocation
        partner_subcontract_location=self.env['stock.location'].create({
            'name':'Specificpartnerlocation',
            'location_id':self.env.ref('stock.stock_location_locations_partner').id,
            'usage':'internal',
            'company_id':self.env.company.id,
        })
        self.subcontractor_partner1.property_stock_subcontractor=partner_subcontract_location.id
        resupply_rule=resupply_sub_on_order_route.rule_ids.filtered(lambdal:
            l.location_id==self.comp1.property_stock_productionand
            l.location_src_id==self.env.company.subcontracting_location_id)
        resupply_rule.copy({'location_src_id':partner_subcontract_location.id})
        resupply_warehouse_rule=self.warehouse.route_ids.rule_ids.filtered(lambdal:
            l.location_id==self.env.company.subcontracting_location_idand
            l.location_src_id==self.warehouse.lot_stock_id)
        resupply_warehouse_rule.copy({'location_id':partner_subcontract_location.id})
        #Addamanufacturingleadtimetocheckthattheresupplydeliveryiscorrectlyplanned2days
        #beforethesubcontractingreceipt
        self.finished.produce_delay=2

        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        #Nothingshouldbetracked
        self.assertFalse(picking_receipt.display_action_record_components)

        #Pickingsshoulddirectlybecreated
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertEqual(len(mo.picking_ids),1)
        self.assertEqual(mo.state,'confirmed')
        self.assertEqual(len(mo.picking_ids.move_lines),2)

        picking=mo.picking_ids
        wh=picking.picking_type_id.warehouse_id

        #Thepickingshouldbeadeliveryorder
        self.assertEqual(picking.picking_type_id,wh.out_type_id)
        #Thedateplannedshouldbecorrect
        self.assertEqual(picking_receipt.scheduled_date,picking.scheduled_date+relativedelta(days=self.finished.produce_delay))

        self.assertEqual(mo.picking_type_id,wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        #Nomanufacturingorderfor`self.comp2`
        comp2mo=self.env['mrp.production'].search([('bom_id','=',self.comp2_bom.id)])
        self.assertEqual(len(comp2mo),0)

        picking_receipt.move_lines.quantity_done=1
        picking_receipt.button_validate()
        self.assertEqual(mo.state,'done')

        #Availablequantitiesshouldbenegativeatthesubcontractinglocationforeachcomponents
        avail_qty_comp1=self.env['stock.quant']._get_available_quantity(self.comp1,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_comp2=self.env['stock.quant']._get_available_quantity(self.comp2,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_finished=self.env['stock.quant']._get_available_quantity(self.finished,wh.lot_stock_id)
        self.assertEqual(avail_qty_comp1,-1)
        self.assertEqual(avail_qty_comp2,-1)
        self.assertEqual(avail_qty_finished,1)

        avail_qty_comp1_in_global_location=self.env['stock.quant']._get_available_quantity(self.comp1,self.env.company.subcontracting_location_id,allow_negative=True)
        avail_qty_comp2_in_global_location=self.env['stock.quant']._get_available_quantity(self.comp2,self.env.company.subcontracting_location_id,allow_negative=True)
        self.assertEqual(avail_qty_comp1_in_global_location,0.0)
        self.assertEqual(avail_qty_comp2_in_global_location,0.0)

    deftest_flow_3(self):
        """Tick"ResupplySubcontractoronOrder"and"MTO"onthecomponentsandtriggerthe
        creationofthesubcontractingmanufacturingorderthroughareceiptpicking.Checksifthe
        resupplyingactuallyworks.Oneofthecomponenthasalso"manufacture"setandaBOM
        linked.ChecksthatanMOiscreatedforthisone.
        """
        #Tick"resupplysubconractoronorder"
        resupply_sub_on_order_route=self.env['stock.location.route'].search([('name','=','ResupplySubcontractoronOrder')])
        (self.comp1+self.comp2).write({'route_ids':[(4,resupply_sub_on_order_route.id,None)]})

        #Tick"manufacture"andMTOonself.comp2
        mto_route=self.env.ref('stock.route_warehouse0_mto')
        mto_route.active=True
        manufacture_route=self.env['stock.location.route'].search([('name','=','Manufacture')])
        self.comp2.write({'route_ids':[(4,manufacture_route.id,None)]})
        self.comp2.write({'route_ids':[(4,mto_route.id,None)]})

        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        #Nothingshouldbetracked
        self.assertFalse(picking_receipt.display_action_record_components)

        #Pickingsshoulddirectlybecreated
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertEqual(mo.state,'confirmed')

        picking_delivery=mo.picking_ids
        self.assertEqual(len(picking_delivery),1)
        self.assertEqual(len(picking_delivery.move_lines),2)
        self.assertEqual(picking_delivery.origin,picking_receipt.name)
        self.assertEqual(picking_delivery.partner_id,picking_receipt.partner_id)

        #Thepickingshouldbeadeliveryorder
        wh=picking_receipt.picking_type_id.warehouse_id
        self.assertEqual(mo.picking_ids.picking_type_id,wh.out_type_id)

        self.assertEqual(mo.picking_type_id,wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        #Aswellasamanufacturingorderfor`self.comp2`
        comp2mo=self.env['mrp.production'].search([('bom_id','=',self.comp2_bom.id)])
        self.assertEqual(len(comp2mo),1)
        picking_receipt.move_lines.quantity_done=1
        picking_receipt.button_validate()
        self.assertEqual(mo.state,'done')

        #Availablequantitiesshouldbenegativeatthesubcontractinglocationforeachcomponents
        avail_qty_comp1=self.env['stock.quant']._get_available_quantity(self.comp1,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_comp2=self.env['stock.quant']._get_available_quantity(self.comp2,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_finished=self.env['stock.quant']._get_available_quantity(self.finished,wh.lot_stock_id)
        self.assertEqual(avail_qty_comp1,-1)
        self.assertEqual(avail_qty_comp2,-1)
        self.assertEqual(avail_qty_finished,1)

    deftest_flow_4(self):
        """Tick"Manufacture"and"MTO"onthecomponentsandtriggerthe
        creationofthesubcontractingmanufacturingorderthroughareceipt
        picking.ChecksthatthedeliveryandMOforitscomponentsare
        automaticallycreated.
        """
        #Tick"manufacture"andMTOonself.comp2
        mto_route=self.env.ref('stock.route_warehouse0_mto')
        mto_route.active=True
        manufacture_route=self.env['stock.location.route'].search([('name','=','Manufacture')])
        self.comp2.write({'route_ids':[(4,manufacture_route.id,None)]})
        self.comp2.write({'route_ids':[(4,mto_route.id,None)]})

        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=self.comp2
        orderpoint_form.product_min_qty=0.0
        orderpoint_form.product_max_qty=10.0
        orderpoint_form.location_id=self.env.company.subcontracting_location_id
        orderpoint=orderpoint_form.save()

        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        warehouse=picking_receipt.picking_type_id.warehouse_id

        #Pickingsshoulddirectlybecreated
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertEqual(mo.state,'confirmed')

        picking_delivery=mo.picking_ids
        self.assertFalse(picking_delivery)

        picking_delivery=self.env['stock.picking'].search([('origin','ilike','%'+picking_receipt.name+'%')])
        self.assertFalse(picking_delivery)

        move=self.env['stock.move'].search([
            ('product_id','=',self.comp2.id),
            ('location_id','=',warehouse.lot_stock_id.id),
            ('location_dest_id','=',self.env.company.subcontracting_location_id.id)
        ])
        self.assertTrue(move)
        picking_delivery=move.picking_id
        self.assertTrue(picking_delivery)
        self.assertEqual(move.product_uom_qty,11.0)

        #Aswellasamanufacturingorderfor`self.comp2`
        comp2mo=self.env['mrp.production'].search([('bom_id','=',self.comp2_bom.id)])
        self.assertEqual(len(comp2mo),1)

    deftest_flow_5(self):
        """CheckthatthecorrectBoMischosenaccordinglytothepartner
        """
        #Wecreateasecondpartneroftypesubcontractor
        main_partner_2=self.env['res.partner'].create({'name':'main_partner'})
        subcontractor_partner2=self.env['res.partner'].create({
            'name':'subcontractor_partner',
            'parent_id':main_partner_2.id,
            'company_id':self.env.ref('base.main_company').id
        })

        #WecreateadifferentBoMforthesameproduct
        comp3=self.env['product.product'].create({
            'name':'Component1',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        bom_form=Form(self.env['mrp.bom'])
        bom_form.type='subcontract'
        bom_form.product_tmpl_id=self.finished.product_tmpl_id
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.comp1
            bom_line.product_qty=1
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=comp3
            bom_line.product_qty=1
        bom2=bom_form.save()

        #WeassignthesecondBoMtothenewpartner
        self.bom.write({'subcontractor_ids':[(4,self.subcontractor_partner1.id,None)]})
        bom2.write({'subcontractor_ids':[(4,subcontractor_partner2.id,None)]})

        #Createareceiptpickingfromthesubcontractor1
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt1=picking_form.save()
        picking_receipt1.action_confirm()

        #Createareceiptpickingfromthesubcontractor2
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=subcontractor_partner2
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt2=picking_form.save()
        picking_receipt2.action_confirm()

        mo_pick1=picking_receipt1.move_lines.mapped('move_orig_ids.production_id')
        mo_pick2=picking_receipt2.move_lines.mapped('move_orig_ids.production_id')
        self.assertEqual(len(mo_pick1),1)
        self.assertEqual(len(mo_pick2),1)
        self.assertEqual(mo_pick1.bom_id,self.bom)
        self.assertEqual(mo_pick2.bom_id,bom2)

    deftest_flow_6(self):
        """Extraquantityonthemove.
        """
        #Wecreateasecondpartneroftypesubcontractor
        main_partner_2=self.env['res.partner'].create({'name':'main_partner'})
        subcontractor_partner2=self.env['res.partner'].create({
            'name':'subcontractor_partner',
            'parent_id':main_partner_2.id,
            'company_id':self.env.ref('base.main_company').id,
        })
        self.env.cache.invalidate()

        #WecreateadifferentBoMforthesameproduct
        comp3=self.env['product.product'].create({
            'name':'Component3',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        bom_form=Form(self.env['mrp.bom'])
        bom_form.type='subcontract'
        bom_form.product_tmpl_id=self.finished.product_tmpl_id
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.comp1
            bom_line.product_qty=1
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=comp3
            bom_line.product_qty=2
        bom2=bom_form.save()

        #WeassignthesecondBoMtothenewpartner
        self.bom.write({'subcontractor_ids':[(4,self.subcontractor_partner1.id,None)]})
        bom2.write({'subcontractor_ids':[(4,subcontractor_partner2.id,None)]})

        #Createareceiptpickingfromthesubcontractor1
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=subcontractor_partner2
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        picking_receipt.move_lines.quantity_done=3.0
        picking_receipt._action_done()
        mo=picking_receipt._get_subcontracted_productions()
        move_comp1=mo.move_raw_ids.filtered(lambdam:m.product_id==self.comp1)
        move_comp3=mo.move_raw_ids.filtered(lambdam:m.product_id==comp3)
        self.assertEqual(sum(move_comp1.mapped('product_uom_qty')),3.0)
        self.assertEqual(sum(move_comp3.mapped('product_uom_qty')),6.0)
        self.assertEqual(sum(move_comp1.mapped('quantity_done')),3.0)
        self.assertEqual(sum(move_comp3.mapped('quantity_done')),6.0)
        move_finished=mo.move_finished_ids
        self.assertEqual(sum(move_finished.mapped('product_uom_qty')),3.0)
        self.assertEqual(sum(move_finished.mapped('quantity_done')),3.0)

    deftest_flow_8(self):
        resupply_sub_on_order_route=self.env['stock.location.route'].search([('name','=','ResupplySubcontractoronOrder')])
        (self.comp1+self.comp2).write({'route_ids':[(4,resupply_sub_on_order_route.id,None)]})

        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=5
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        picking_receipt.move_lines.quantity_done=3
        backorder_wiz=picking_receipt.button_validate()
        backorder_wiz=Form(self.env[backorder_wiz['res_model']].with_context(backorder_wiz['context'])).save()
        backorder_wiz.process()

        backorder=self.env['stock.picking'].search([('backorder_id','=',picking_receipt.id)])
        self.assertTrue(backorder)
        self.assertEqual(backorder.move_lines.product_uom_qty,2)
        mo_done=backorder.move_lines.move_orig_ids.production_id.filtered(lambdap:p.state=='done')
        backorder_mo=backorder.move_lines.move_orig_ids.production_id.filtered(lambdap:p.state!='done')
        self.assertTrue(mo_done)
        self.assertEqual(mo_done.qty_produced,3)
        self.assertEqual(mo_done.product_uom_qty,3)
        self.assertTrue(backorder_mo)
        self.assertEqual(backorder_mo.product_uom_qty,2)
        self.assertEqual(backorder_mo.qty_produced,0)
        backorder.move_lines.quantity_done=2
        backorder._action_done()
        self.assertTrue(picking_receipt.move_lines.move_orig_ids.production_id.state=='done')

    deftest_flow_9(self):
        """Ensurethatcancelthesubcontractmoveswillalsodeletethe
        componentsneedforthesubcontractor.
        """
        resupply_sub_on_order_route=self.env['stock.location.route'].search([
            ('name','=','ResupplySubcontractoronOrder')
        ])
        (self.comp1+self.comp2).write({
            'route_ids':[(4,resupply_sub_on_order_route.id)]
        })

        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=5
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        picking_delivery=self.env['stock.move'].search([
            ('product_id','in',(self.comp1|self.comp2).ids)
        ]).picking_id
        self.assertTrue(picking_delivery)
        self.assertEqual(picking_delivery.state,'confirmed')
        self.assertEqual(self.comp1.virtual_available,-5)
        self.assertEqual(self.comp2.virtual_available,-5)
        #action_cancelisnotcallonthepickinginorder
        #totestbehaviorfromothersourcethanpicking(e.g.puchase).
        picking_receipt.move_lines._action_cancel()
        self.assertEqual(picking_delivery.state,'cancel')
        self.assertEqual(self.comp1.virtual_available,0.0)
        self.assertEqual(self.comp1.virtual_available,0.0)

    deftest_flow_10(self):
        """Receiptsfromachildrencontactofasubcontractorareproperly
        handled.
        """
        #Createachildrencontact
        subcontractor_contact=self.env['res.partner'].create({
            'name':'Testchildrensubcontractorcontact',
            'parent_id':self.subcontractor_partner1.id,
        })
        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=subcontractor_contact
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()
        #Checkthatamanufacturingorderiscreated
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertEqual(len(mo),1)

    deftest_mo_name(self):
        receipt_form=Form(self.env['stock.picking'])
        receipt_form.picking_type_id=self.env.ref('stock.picking_type_in')
        receipt_form.partner_id=self.subcontractor_partner1
        withreceipt_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished
            move.product_uom_qty=1
        receipt=receipt_form.save()
        receipt.action_confirm()

        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])

        display_name=mo.display_name
        self.assertIn(receipt.name,display_name,"Ifsubcontracted,thenameofaMOshouldcontaintheassociatedreceiptname")
        self.assertIn(mo.name,display_name)

        forkey_searchin[mo.name,receipt.name]:
            res=mo.name_search(key_search)
            self.assertTrue(res,'Whenlookingfor"%s",itshouldfindsomething'%key_search)
            self.assertEqual(res[0][0],mo.id,'Whenlookingfor"%s",itshouldfindtheMOprocessedabove'%key_search)


classTestSubcontractingTracking(TransactionCase):
    defsetUp(self):
        super(TestSubcontractingTracking,self).setUp()
        #1:Createasubcontractingpartner
        main_company_1=self.env['res.partner'].create({'name':'main_partner'})
        self.subcontractor_partner1=self.env['res.partner'].create({
            'name':'Subcontractor1',
            'parent_id':main_company_1.id,
            'company_id':self.env.ref('base.main_company').id
        })

        #2.CreateaBOMofsubcontractingtype
        #2.1.Comp1hastrackingbylot
        self.comp1_sn=self.env['product.product'].create({
            'name':'Component1',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'tracking':'serial'
        })
        self.comp2=self.env['product.product'].create({
            'name':'Component2',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        #2.2.Finishedprodcuthastrackingbyserialnumber
        self.finished_product=self.env['product.product'].create({
            'name':'finished',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'tracking':'lot'
        })
        bom_form=Form(self.env['mrp.bom'])
        bom_form.type='subcontract'
        bom_form.subcontractor_ids.add(self.subcontractor_partner1)
        bom_form.product_tmpl_id=self.finished_product.product_tmpl_id
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.comp1_sn
            bom_line.product_qty=1
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.comp2
            bom_line.product_qty=1
        self.bom_tracked=bom_form.save()

    deftest_flow_tracked_1(self):
        """Thistestmimicstest_flow_1butwithaBoMthathastrackingincludedinit.
        """
        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished_product
            move.product_uom_qty=1
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        #Weshouldbeabletocallthe'record_components'button
        self.assertTrue(picking_receipt.display_action_record_components)

        #Checkthecreatedmanufacturingorder
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom_tracked.id)])
        self.assertEqual(len(mo),1)
        self.assertEqual(len(mo.picking_ids),0)
        wh=picking_receipt.picking_type_id.warehouse_id
        self.assertEqual(mo.picking_type_id,wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        #CreateaRR
        pg1=self.env['procurement.group'].create({})
        self.env['stock.warehouse.orderpoint'].create({
            'name':'xxx',
            'product_id':self.comp1_sn.id,
            'product_min_qty':0,
            'product_max_qty':0,
            'location_id':self.env.user.company_id.subcontracting_location_id.id,
            'group_id':pg1.id,
        })

        #Runtheschedulerandcheckthecreatedpicking
        self.env['procurement.group'].run_scheduler()
        picking=self.env['stock.picking'].search([('group_id','=',pg1.id)])
        self.assertEqual(len(picking),1)
        self.assertEqual(picking.picking_type_id,wh.out_type_id)

        lot_id=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.finished_product.id,
            'company_id':self.env.company.id,
        })
        serial_id=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.comp1_sn.id,
            'company_id':self.env.company.id,
        })

        action=picking_receipt.action_record_components()
        mo=self.env['mrp.production'].browse(action['res_id'])
        mo_form=Form(mo.with_context(**action['context']),view=action['view_id'])
        mo_form.qty_producing=1
        mo_form.lot_producing_id=lot_id
        withmo_form.move_line_raw_ids.edit(0)asml:
            ml.lot_id=serial_id
        mo=mo_form.save()
        mo.subcontracting_record_component()

        #Weshouldnotbeabletocallthe'record_components'button
        self.assertFalse(picking_receipt.display_action_record_components)

        picking_receipt.button_validate()
        self.assertEqual(mo.state,'done')

        #Availablequantitiesshouldbenegativeatthesubcontractinglocationforeachcomponents
        avail_qty_comp1=self.env['stock.quant']._get_available_quantity(self.comp1_sn,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_comp2=self.env['stock.quant']._get_available_quantity(self.comp2,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_finished=self.env['stock.quant']._get_available_quantity(self.finished_product,wh.lot_stock_id)
        self.assertEqual(avail_qty_comp1,-1)
        self.assertEqual(avail_qty_comp2,-1)
        self.assertEqual(avail_qty_finished,1)

    deftest_flow_tracked_only_finished(self):
        """Testwhenonlythefinishedproductistracked"""
        self.finished_product.tracking="serial"
        self.comp1_sn.tracking="none"
        nb_finished_product=3
        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished_product
            move.product_uom_qty=nb_finished_product
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        #Weshouldn'tbeabletocallthe'record_components'button
        self.assertFalse(picking_receipt.display_action_record_components)

        wh=picking_receipt.picking_type_id.warehouse_id
        lot_names_finished=[f"subtracked_{i}"foriinrange(nb_finished_product)]

        move_details=Form(picking_receipt.move_lines,view='stock.view_stock_move_nosuggest_operations')
        forlot_nameinlot_names_finished:
            withmove_details.move_line_nosuggest_ids.new()asml:
                ml.qty_done=1
                ml.lot_name=lot_name
        move_details.save()

        picking_receipt.button_validate()
        #Checkthecreatedmanufacturingorder
        #Shouldhaveonemobyserialnumber
        mos=picking_receipt.move_lines.move_orig_ids.production_id
        self.assertEqual(len(mos),nb_finished_product)
        self.assertEqual(mos.mapped("state"),["done"]*nb_finished_product)
        self.assertEqual(mos.picking_type_id,wh.subcontracting_type_id)
        self.assertFalse(mos.picking_type_id.active)
        self.assertEqual(set(mos.lot_producing_id.mapped("name")),set(lot_names_finished))

        #Availablequantitiesshouldbenegativeatthesubcontractinglocationforeachcomponents
        avail_qty_comp1=self.env['stock.quant']._get_available_quantity(self.comp1_sn,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_comp2=self.env['stock.quant']._get_available_quantity(self.comp2,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_finished=self.env['stock.quant']._get_available_quantity(self.finished_product,wh.lot_stock_id)
        self.assertEqual(avail_qty_comp1,-nb_finished_product)
        self.assertEqual(avail_qty_comp2,-nb_finished_product)
        self.assertEqual(avail_qty_finished,nb_finished_product)

    deftest_flow_tracked_backorder(self):
        """Thistestusestracked(serialandlot)componentandtracked(serial)finishedproduct"""
        todo_nb=4
        self.comp2.tracking='lot'
        self.finished_product.tracking='serial'

        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.finished_product
            move.product_uom_qty=todo_nb
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        #Weshouldbeabletocallthe'record_components'button
        self.assertTrue(picking_receipt.display_action_record_components)

        #Checkthecreatedmanufacturingorder
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom_tracked.id)])
        self.assertEqual(len(mo),1)
        self.assertEqual(len(mo.picking_ids),0)
        wh=picking_receipt.picking_type_id.warehouse_id
        self.assertEqual(mo.picking_type_id,wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        lot_comp2=self.env['stock.production.lot'].create({
            'name':'lot_comp2',
            'product_id':self.comp2.id,
            'company_id':self.env.company.id,
        })
        serials_finished=[]
        serials_comp1=[]
        foriinrange(todo_nb):
            serials_finished.append(self.env['stock.production.lot'].create({
                'name':'serial_fin_%s'%i,
                'product_id':self.finished_product.id,
                'company_id':self.env.company.id,
            }))
            serials_comp1.append(self.env['stock.production.lot'].create({
                'name':'serials_comp1_%s'%i,
                'product_id':self.comp1_sn.id,
                'company_id':self.env.company.id,
            }))

        foriinrange(todo_nb):
            action=picking_receipt.action_record_components()
            mo=self.env['mrp.production'].browse(action['res_id'])
            mo_form=Form(mo.with_context(**action['context']),view=action['view_id'])
            mo_form.lot_producing_id=serials_finished[i]
            withmo_form.move_line_raw_ids.edit(0)asml:
                self.assertEqual(ml.product_id,self.comp1_sn)
                ml.lot_id=serials_comp1[i]
            withmo_form.move_line_raw_ids.edit(1)asml:
                self.assertEqual(ml.product_id,self.comp2)
                ml.lot_id=lot_comp2
            mo=mo_form.save()
            mo.subcontracting_record_component()

        #Weshouldnotbeabletocallthe'record_components'button
        self.assertFalse(picking_receipt.display_action_record_components)

        picking_receipt.button_validate()
        self.assertEqual(mo.state,'done')
        self.assertEqual(mo.procurement_group_id.mrp_production_ids.mapped("state"),['done']*todo_nb)
        self.assertEqual(len(mo.procurement_group_id.mrp_production_ids),todo_nb)
        self.assertEqual(mo.procurement_group_id.mrp_production_ids.mapped("qty_produced"),[1]*todo_nb)

        #Availablequantitiesshouldbenegativeatthesubcontractinglocationforeachcomponents
        avail_qty_comp1=self.env['stock.quant']._get_available_quantity(self.comp1_sn,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_comp2=self.env['stock.quant']._get_available_quantity(self.comp2,self.subcontractor_partner1.property_stock_subcontractor,allow_negative=True)
        avail_qty_finished=self.env['stock.quant']._get_available_quantity(self.finished_product,wh.lot_stock_id)
        self.assertEqual(avail_qty_comp1,-todo_nb)
        self.assertEqual(avail_qty_comp2,-todo_nb)
        self.assertEqual(avail_qty_finished,todo_nb)

    deftest_flow_tracked_backorder02(self):
        """Bothcomponentandfinishedproductaretrackedbylot."""
        todo_nb=4
        resupply_sub_on_order_route=self.env['stock.location.route'].search([('name','=','ResupplySubcontractoronOrder')])
        finished_product,component=self.env['product.product'].create([{
            'name':'SuperProduct',
            'type':'product',
            'tracking':'lot',
        },{
            'name':'Component',
            'type':'product',
            'tracking':'lot',
            'route_ids':[(4,resupply_sub_on_order_route.id)],
        }])

        bom_form=Form(self.env['mrp.bom'])
        bom_form.type='subcontract'
        bom_form.subcontractor_ids.add(self.subcontractor_partner1)
        bom_form.product_tmpl_id=finished_product.product_tmpl_id
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=component
            bom_line.product_qty=1
        bom=bom_form.save()

        finished_lot,component_lot=self.env['stock.production.lot'].create([{
            'name':'lot_%s'%product.name,
            'product_id':product.id,
            'company_id':self.env.company.id,
        }forproductin[finished_product,component]])

        self.env['stock.quant']._update_available_quantity(component,self.env.ref('stock.stock_location_stock'),todo_nb,lot_id=component_lot)

        #Createareceiptpickingfromthesubcontractor
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        picking_form.partner_id=self.subcontractor_partner1
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=finished_product
            move.product_uom_qty=todo_nb
        picking_receipt=picking_form.save()
        picking_receipt.action_confirm()

        mo=self.env['mrp.production'].search([('bom_id','=',bom.id)])

        #Processthedeliveryofthecomponents
        compo_picking=mo.picking_ids
        compo_picking.action_assign()
        wizard_data=compo_picking.button_validate()
        wizard=Form(self.env[wizard_data['res_model']].with_context(wizard_data['context'])).save()
        wizard.process()

        forqtyin[3,1]:
            #Recordthereceiptionof<qty>finishedproducts
            picking_receipt=self.env['stock.picking'].search([('partner_id','=',self.subcontractor_partner1.id),('state','!=','done')])
            action=picking_receipt.action_record_components()
            mo=self.env['mrp.production'].browse(action['res_id'])
            mo_form=Form(mo.with_context(**action['context']),view=action['view_id'])
            mo_form.qty_producing=qty
            mo_form.lot_producing_id=finished_lot
            withmo_form.move_line_raw_ids.edit(0)asml:
                ml.lot_id=component_lot
            mo=mo_form.save()
            mo.subcontracting_record_component()

            #Validatethepickingandcreateabackorder
            wizard_data=picking_receipt.button_validate()
            ifqty==3:
                wizard=Form(self.env[wizard_data['res_model']].with_context(wizard_data['context'])).save()
                wizard.process()

            self.assertEqual(picking_receipt.state,'done')


@tagged('post_install','-at_install')
classTestSubcontractingPurchaseFlows(TransactionCase):

    defsetUp(self):
        super().setUp()
        #todo15.0:movein`mrp_subcontracting_purchase`
        if'purchase.order'notinself.env:
            self.skipTest('`purchase`isnotinstalled')

        self.subcontractor=self.env['res.partner'].create({'name':'SuperSubcontractor'})

        self.finished,self.compo=self.env['product.product'].create([{
            'name':'SuperProduct',
            'type':'product',
        },{
            'name':'Component',
            'type':'consu',
        }])

        self.bom=self.env['mrp.bom'].create({
            'product_tmpl_id':self.finished.product_tmpl_id.id,
            'type':'subcontract',
            'subcontractor_ids':[(6,0,self.subcontractor.ids)],
            'bom_line_ids':[(0,0,{
                'product_id':self.compo.id,
                'product_qty':1,
            })],
        })

    deftest_purchase_and_return01(self):
        """
        Theuserbuys10xasubcontractedproductP.Hereceivesthe10
        productsandthendoesareturnwith3xP.Thetestensuresthatthe
        finalreceivedquantityiscorrectlycomputed
        """
        po=self.env['purchase.order'].create({
            'partner_id':self.subcontractor.id,
            'order_line':[(0,0,{
                'name':self.finished.name,
                'product_id':self.finished.id,
                'product_uom_qty':10,
                'product_uom':self.finished.uom_id.id,
                'price_unit':1,
            })],
        })
        po.button_confirm()

        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertTrue(mo)

        receipt=po.picking_ids
        receipt.move_lines.quantity_done=10
        receipt.button_validate()

        return_form=Form(self.env['stock.return.picking'].with_context(active_id=receipt.id,active_model='stock.picking'))
        withreturn_form.product_return_moves.edit(0)asline:
            line.quantity=3
            line.to_refund=True
        return_wizard=return_form.save()
        return_id,_=return_wizard._create_returns()

        return_picking=self.env['stock.picking'].browse(return_id)
        return_picking.move_lines.quantity_done=3
        return_picking.button_validate()

        self.assertEqual(self.finished.qty_available,7.0)
        self.assertEqual(po.order_line.qty_received,7.0)

    deftest_purchase_and_return02(self):
        """
        Theuserbuys10xasubcontractedproductP.Hereceivesthe10
        productsandthendoesareturnwith3xP(withtheflagto_refund
        disabledandthesubcontractinglocationasreturnlocation).Thetest
        ensuresthatthefinalreceivedquantityiscorrectlycomputed
        """
        grp_multi_loc=self.env.ref('stock.group_stock_multi_locations')
        self.env.user.write({'groups_id':[(4,grp_multi_loc.id)]})

        po=self.env['purchase.order'].create({
            'partner_id':self.subcontractor.id,
            'order_line':[(0,0,{
                'name':self.finished.name,
                'product_id':self.finished.id,
                'product_uom_qty':10,
                'product_uom':self.finished.uom_id.id,
                'price_unit':1,
            })],
        })
        po.button_confirm()

        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertTrue(mo)

        receipt=po.picking_ids
        receipt.move_lines.quantity_done=10
        receipt.button_validate()

        return_form=Form(self.env['stock.return.picking'].with_context(active_id=receipt.id,active_model='stock.picking'))
        return_form.location_id=self.env.company.subcontracting_location_id
        withreturn_form.product_return_moves.edit(0)asline:
            line.quantity=3
            line.to_refund=False
        return_wizard=return_form.save()
        return_id,_=return_wizard._create_returns()

        return_picking=self.env['stock.picking'].browse(return_id)
        return_picking.move_lines.quantity_done=3
        return_picking.button_validate()

        self.assertEqual(self.finished.qty_available,7.0)
        self.assertEqual(po.order_line.qty_received,10.0)
