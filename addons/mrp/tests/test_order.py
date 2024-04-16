#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromdatetimeimportdatetime,timedelta
fromfreezegunimportfreeze_time

fromflectra.fieldsimportDatetimeasDt
fromflectra.exceptionsimportUserError
fromflectra.addons.mrp.tests.commonimportTestMrpCommon

classTestMrpOrder(TestMrpCommon):

    deftest_access_rights_manager(self):
        """ChecksanMRPmanagercancreate,confirmandcancelamanufacturingorder."""
        man_order_form=Form(self.env['mrp.production'].with_user(self.user_mrp_manager))
        man_order_form.product_id=self.product_4
        man_order_form.product_qty=5.0
        man_order_form.bom_id=self.bom_1
        man_order_form.location_src_id=self.location_1
        man_order_form.location_dest_id=self.warehouse_1.wh_output_stock_loc_id
        man_order=man_order_form.save()
        man_order.action_confirm()
        man_order.action_cancel()
        self.assertEqual(man_order.state,'cancel',"Productionordershouldbeincancelstate.")
        man_order.unlink()

    deftest_access_rights_user(self):
        """ChecksanMRPusercancreate,confirmandcancelamanufacturingorder."""
        man_order_form=Form(self.env['mrp.production'].with_user(self.user_mrp_user))
        man_order_form.product_id=self.product_4
        man_order_form.product_qty=5.0
        man_order_form.bom_id=self.bom_1
        man_order_form.location_src_id=self.location_1
        man_order_form.location_dest_id=self.warehouse_1.wh_output_stock_loc_id
        man_order=man_order_form.save()
        man_order.action_confirm()
        man_order.action_cancel()
        self.assertEqual(man_order.state,'cancel',"Productionordershouldbeincancelstate.")
        man_order.unlink()

    deftest_basic(self):
        """Checksabasicmanufacturingorder:norouting(thusnoworkorders),nolotand
        consumestrictlywhat'sneeded."""
        self.product_1.type='product'
        self.product_2.type='product'
        inventory=self.env['stock.inventory'].create({
            'name':'Initialinventory',
            'line_ids':[(0,0,{
                'product_id':self.product_1.id,
                'product_uom_id':self.product_1.uom_id.id,
                'product_qty':500,
                'location_id':self.warehouse_1.lot_stock_id.id
            }),(0,0,{
                'product_id':self.product_2.id,
                'product_uom_id':self.product_2.uom_id.id,
                'product_qty':500,
                'location_id':self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_start()
        inventory.action_validate()

        test_date_planned=Dt.now()-timedelta(days=1)
        test_quantity=3.0
        man_order_form=Form(self.env['mrp.production'].with_user(self.user_mrp_user))
        man_order_form.product_id=self.product_4
        man_order_form.bom_id=self.bom_1
        man_order_form.product_uom_id=self.product_4.uom_id
        man_order_form.product_qty=test_quantity
        man_order_form.date_planned_start=test_date_planned
        man_order_form.location_src_id=self.location_1
        man_order_form.location_dest_id=self.warehouse_1.wh_output_stock_loc_id
        man_order=man_order_form.save()

        self.assertEqual(man_order.state,'draft',"Productionordershouldbeindraftstate.")
        man_order.action_confirm()
        self.assertEqual(man_order.state,'confirmed',"Productionordershouldbeinconfirmedstate.")

        #checkproductionmove
        production_move=man_order.move_finished_ids
        self.assertAlmostEqual(production_move.date,test_date_planned+timedelta(hours=1),delta=timedelta(seconds=10))
        self.assertEqual(production_move.product_id,self.product_4)
        self.assertEqual(production_move.product_uom,man_order.product_uom_id)
        self.assertEqual(production_move.product_qty,man_order.product_qty)
        self.assertEqual(production_move.location_id,self.product_4.property_stock_production)
        self.assertEqual(production_move.location_dest_id,man_order.location_dest_id)

        #checkconsumptionmoves
        formoveinman_order.move_raw_ids:
            self.assertEqual(move.date,test_date_planned)
        first_move=man_order.move_raw_ids.filtered(lambdamove:move.product_id==self.product_2)
        self.assertEqual(first_move.product_qty,test_quantity/self.bom_1.product_qty*self.product_4.uom_id.factor_inv*2)
        first_move=man_order.move_raw_ids.filtered(lambdamove:move.product_id==self.product_1)
        self.assertEqual(first_move.product_qty,test_quantity/self.bom_1.product_qty*self.product_4.uom_id.factor_inv*4)

        #produceproduct
        mo_form=Form(man_order)
        mo_form.qty_producing=2.0
        man_order=mo_form.save()

        action=man_order.button_mark_done()
        self.assertEqual(man_order.state,'progress',"Productionordershouldbeopenabackorderwizard,thennotdoneyet.")

        quantity_issues=man_order._get_consumption_issues()
        action=man_order._action_generate_consumption_wizard(quantity_issues)
        backorder=Form(self.env['mrp.production.backorder'].with_context(**action['context']))
        backorder.save().action_close_mo()
        self.assertEqual(man_order.state,'done',"Productionordershouldbedone.")

        #checkthatcopyhandlesmovescorrectly
        mo_copy=man_order.copy()
        self.assertEqual(mo_copy.state,'draft',"Copiedproductionordershouldbedraft.")
        self.assertEqual(len(mo_copy.move_raw_ids),4,"Incorrectnumberofcomponentmoves[i.e.no0qtymovesshouldbecopied].")
        self.assertEqual(len(mo_copy.move_finished_ids),1,"Incorrectnumberofmovesforproductstoproduce[i.e.cancelledmovesshouldnotbecopied")
        self.assertEqual(mo_copy.move_finished_ids.product_uom_qty,2,"Incorrectqtyofproductstoproduce")

        #checkthatacancelledMOiscopiedcorrectly
        mo_copy.action_cancel()
        self.assertEqual(mo_copy.state,'cancel')
        mo_copy_2=mo_copy.copy()
        self.assertEqual(mo_copy_2.state,'draft',"Copiedproductionordershouldbedraft.")
        self.assertEqual(len(mo_copy_2.move_raw_ids),4,"Incorrectnumberofcomponentmoves.")
        self.assertEqual(len(mo_copy_2.move_finished_ids),1,"Incorrectnumberofmovesforproductstoproduce[i.e.copyingacancelledMOshouldcopyitscancelledmoves]")
        self.assertEqual(mo_copy_2.move_finished_ids.product_uom_qty,2,"Incorrectqtyofproductstoproduce")

    deftest_production_avialability(self):
        """Checkstheavailabilityofaproductionorderthroughmutliplecallsto`action_assign`.
        """
        self.bom_3.bom_line_ids.filtered(lambdax:x.product_id==self.product_5).unlink()
        self.bom_3.bom_line_ids.filtered(lambdax:x.product_id==self.product_4).unlink()
        self.bom_3.ready_to_produce='all_available'

        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=self.bom_3
        production_form.product_qty=5.0
        production_form.product_uom_id=self.product_6.uom_id
        production_2=production_form.save()

        production_2.action_confirm()
        production_2.action_assign()

        #checksubproductavailabilitystateiswaiting
        self.assertEqual(production_2.reservation_state,'confirmed','Productionordershouldbeavailabilityforwaitingstate')

        #UpdateInventory
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_2.id,
            'inventory_quantity':2.0,
            'location_id':self.stock_location_14.id
        })

        production_2.action_assign()
        #checksubproductavailabilitystateispartiallyavailable
        self.assertEqual(production_2.reservation_state,'confirmed','Productionordershouldbeavailabilityforpartiallyavailablestate')

        #UpdateInventory
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_2.id,
            'inventory_quantity':5.0,
            'location_id':self.stock_location_14.id
        })

        production_2.action_assign()
        #checksubproductavailabilitystateisassigned
        self.assertEqual(production_2.reservation_state,'assigned','Productionordershouldbeavailabilityforassignedstate')

    deftest_split_move_line(self):
        """Consumemorecomponentquantitythantheinitialdemand.
        Itshouldcreateextramoveandsharethequantitybetweenthetwostock
        moves"""
        mo,bom,p_final,p1,p2=self.generate_mo(qty_base_1=10,qty_final=1,qty_base_2=1)
        mo.action_assign()
        #checkis_quantity_done_editable
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=2
        details_operation_form.save()
        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=11
        details_operation_form.save()

        self.assertEqual(len(mo.move_raw_ids),2)
        self.assertEqual(len(mo.move_raw_ids.mapped('move_line_ids')),2)
        self.assertEqual(mo.move_raw_ids[0].move_line_ids.mapped('qty_done'),[2])
        self.assertEqual(mo.move_raw_ids[1].move_line_ids.mapped('qty_done'),[11])
        self.assertEqual(mo.move_raw_ids[0].quantity_done,2)
        self.assertEqual(mo.move_raw_ids[1].quantity_done,11)
        mo.button_mark_done()
        self.assertEqual(len(mo.move_raw_ids),4)
        self.assertEqual(len(mo.move_raw_ids.mapped('move_line_ids')),4)
        self.assertEqual(mo.move_raw_ids.mapped('quantity_done'),[1,10,1,1])
        self.assertEqual(mo.move_raw_ids.mapped('move_line_ids.qty_done'),[1,10,1,1])

    deftest_under_consumption(self):
        """Consumelesscomponentquantitythantheinitialdemand.
            Beforedone:
                p1,toconsume=1,consumed=0
                p2,toconsume=10,consumed=5
            Afterdone:
                p1,toconsume=1,consumed=0,state=cancel
                p2,toconsume=5,consumed=5,state=done
                p2,toconsume=5,consumed=0,state=cancel
        """
        mo,_bom,_p_final,_p1,_p2=self.generate_mo(qty_base_1=10,qty_final=1,qty_base_2=1)
        mo.action_assign()
        #checkis_quantity_done_editable
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=0
        details_operation_form.save()
        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=5
        details_operation_form.save()

        self.assertEqual(len(mo.move_raw_ids),2)
        self.assertEqual(len(mo.move_raw_ids.mapped('move_line_ids')),2)
        self.assertEqual(mo.move_raw_ids[0].move_line_ids.mapped('qty_done'),[0])
        self.assertEqual(mo.move_raw_ids[1].move_line_ids.mapped('qty_done'),[5])
        self.assertEqual(mo.move_raw_ids[0].quantity_done,0)
        self.assertEqual(mo.move_raw_ids[1].quantity_done,5)
        mo.button_mark_done()
        self.assertEqual(len(mo.move_raw_ids),3)
        self.assertEqual(len(mo.move_raw_ids.mapped('move_line_ids')),1)
        self.assertEqual(mo.move_raw_ids.mapped('quantity_done'),[0,5,0])
        self.assertEqual(mo.move_raw_ids.mapped('product_uom_qty'),[1,5,5])
        self.assertEqual(mo.move_raw_ids.mapped('state'),['cancel','done','cancel'])
        self.assertEqual(mo.move_raw_ids.mapped('move_line_ids.qty_done'),[5])

    deftest_update_quantity_1(self):
        """Build5finalproductswithdifferentconsumedlots,
        theneditthefinishedquantityandupdatetheManufacturing
        orderquantity.Thencheckiftheproducedquantitydonot
        changeanditispossibletoclosetheMO.
        """
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_base_1='lot')
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        lot_1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })
        lot_2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,10,lot_id=lot_1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,10,lot_id=lot_2)

        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()

        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=lot_1
            ml.qty_done=20
        details_operation_form.save()
        update_quantity_wizard=self.env['change.production.qty'].create({
            'mo_id':mo.id,
            'product_qty':4,
        })
        update_quantity_wizard.change_prod_qty()

        self.assertEqual(mo.move_raw_ids.filtered(lambdam:m.product_id==p1).quantity_done,20,'Updatetheproducequantityshouldnotimpactalreadyproducedquantity.')
        self.assertEqual(mo.move_finished_ids.product_uom_qty,4)
        mo.button_mark_done()

    deftest_update_quantity_2(self):
        """Build5finalproductswithdifferentconsumedlots,
        theneditthefinishedquantityandupdatetheManufacturing
        orderquantity.Thencheckiftheproducedquantitydonot
        changeanditispossibletoclosetheMO.
        """
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=3)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,20)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=2
        mo=mo_form.save()

        mo._post_inventory()

        update_quantity_wizard=self.env['change.production.qty'].create({
            'mo_id':mo.id,
            'product_qty':5,
        })
        update_quantity_wizard.change_prod_qty()
        mo_form=Form(mo)
        mo_form.qty_producing=5
        mo=mo_form.save()
        mo.button_mark_done()

        self.assertEqual(sum(mo.move_raw_ids.filtered(lambdam:m.product_id==p1).mapped('quantity_done')),20)
        self.assertEqual(sum(mo.move_finished_ids.mapped('quantity_done')),5)

    deftest_update_quantity_3(self):
        bom=self.env['mrp.bom'].create({
            'product_id':self.product_6.id,
            'product_tmpl_id':self.product_6.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':self.product_6.uom_id.id,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':self.product_2.id,'product_qty':2.03}),
                (0,0,{'product_id':self.product_8.id,'product_qty':4.16})
            ],
            'operation_ids':[
                (0,0,{'name':'GiftWrapMaching','workcenter_id':self.workcenter_1.id,'time_cycle':15,'sequence':1}),
            ]
        })
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=bom
        production_form.product_qty=1
        production_form.product_uom_id=self.product_6.uom_id
        production=production_form.save()
        self.assertEqual(production.workorder_ids.duration_expected,90)
        mo_form=Form(production)
        mo_form.product_qty=3
        production=mo_form.save()
        self.assertEqual(production.workorder_ids.duration_expected,165)

    deftest_update_quantity_4(self):
        bom=self.env['mrp.bom'].create({
            'product_id':self.product_6.id,
            'product_tmpl_id':self.product_6.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':self.product_6.uom_id.id,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':self.product_2.id,'product_qty':2.03}),
                (0,0,{'product_id':self.product_8.id,'product_qty':4.16})
            ],
        })
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=bom
        production_form.product_qty=1
        production_form.product_uom_id=self.product_6.uom_id
        production=production_form.save()
        production_form=Form(production)
        withproduction_form.workorder_ids.new()aswo:
            wo.name='OP1'
            wo.workcenter_id=self.workcenter_1
            wo.duration_expected=40
        production=production_form.save()
        self.assertEqual(production.workorder_ids.duration_expected,40)
        mo_form=Form(production)
        mo_form.product_qty=3
        production=mo_form.save()
        self.assertEqual(production.workorder_ids.duration_expected,90)

    deftest_qty_producing(self):
        """Qtyproducingshouldbetheqtyremaintoproduce,insteadof0"""
        bom=self.env['mrp.bom'].create({
            'product_id':self.product_6.id,
            'product_tmpl_id':self.product_6.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':self.product_6.uom_id.id,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':self.product_2.id,'product_qty':2.00}),
            ],
        })
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=bom
        production_form.product_qty=5
        production_form.product_uom_id=self.product_6.uom_id
        production=production_form.save()
        production_form=Form(production)
        withproduction_form.workorder_ids.new()aswo:
            wo.name='OP1'
            wo.workcenter_id=self.workcenter_1
            wo.duration_expected=40
        production=production_form.save()
        production.action_confirm()
        production.button_plan()

        wo=production.workorder_ids[0]
        wo.button_start()
        self.assertEqual(wo.qty_producing,5,"Wrongquantityissuggestedtoproduce.")

        #Simulatechangingtheqty_producinginthefrontend
        wo.qty_producing=4
        wo.button_pending()
        wo.button_start()
        self.assertEqual(wo.qty_producing,4,"Changingtheqty_producinginthefrontendisnotpersisted")

    deftest_update_quantity_5(self):
        bom=self.env['mrp.bom'].create({
            'product_id':self.product_6.id,
            'product_tmpl_id':self.product_6.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':self.product_6.uom_id.id,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':self.product_2.id,'product_qty':3}),
            ],
        })
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=bom
        production_form.product_qty=1
        production_form.product_uom_id=self.product_6.uom_id
        production=production_form.save()
        production.action_confirm()
        production.action_assign()
        production_form=Form(production)
        #changethequantityproducingandtheinitialdemand
        #inthesametransaction
        production_form.qty_producing=10
        withproduction_form.move_raw_ids.edit(0)asmove:
            move.product_uom_qty=2
        production=production_form.save()
        production.button_mark_done()

    deftest_update_plan_date(self):
        """EditingthescheduleddateafterplanningtheMOshouldunplantheMO,andadjustthedateonthestockmoves"""
        planned_date=datetime(2023,5,15,9,0)
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=self.product_4
        mo_form.bom_id=self.bom_1
        mo_form.product_qty=1
        mo_form.date_planned_start=planned_date
        mo=mo_form.save()
        self.assertEqual(mo.move_finished_ids[0].date,datetime(2023,5,15,10,0))
        mo.action_confirm()
        mo.button_plan()
        withForm(mo)asfrm:
            frm.date_planned_start=datetime(2024,5,15,9,0)
        self.assertEqual(mo.move_finished_ids[0].date,datetime(2024,5,15,10,0))

    deftest_rounding(self):
        """Checksweroundupwhenbringinggoodstoproduceandroundhalf-upwhenproducing.
        Thisimplementationallowstoimplementanefficiencynotion(seerev347f140fe63612ee05e).
        """
        self.product_6.uom_id.rounding=1.0
        bom_eff=self.env['mrp.bom'].create({
            'product_id':self.product_6.id,
            'product_tmpl_id':self.product_6.product_tmpl_id.id,
            'product_qty':1,
            'product_uom_id':self.product_6.uom_id.id,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':self.product_2.id,'product_qty':2.03}),
                (0,0,{'product_id':self.product_8.id,'product_qty':4.16})
            ]
        })
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_6
        production_form.bom_id=bom_eff
        production_form.product_qty=20
        production_form.product_uom_id=self.product_6.uom_id
        production=production_form.save()
        production.action_confirm()
        #Checktheproductionorderhastherightquantities
        self.assertEqual(production.move_raw_ids[0].product_qty,41,'Thequantityshouldberoundedup')
        self.assertEqual(production.move_raw_ids[1].product_qty,84,'Thequantityshouldberoundedup')

        #produceproduct
        mo_form=Form(production)
        mo_form.qty_producing=8
        production=mo_form.save()
        self.assertEqual(production.move_raw_ids[0].quantity_done,16,'Shouldusehalf-uproundingwhenproducing')
        self.assertEqual(production.move_raw_ids[1].quantity_done,34,'Shouldusehalf-uproundingwhenproducing')

    deftest_product_produce_1(self):
        """Checkstheproductionwizardcontainslinesevenforuntrackedproducts."""
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo()
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()

        #changethequantitydoneinoneline
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=1
        details_operation_form.save()

        #changethequantityproducing
        mo_form=Form(mo)
        mo_form.qty_producing=3

        #checkthanallquantitiesareupdatecorrectly
        self.assertEqual(mo_form.move_raw_ids._records[0]['product_uom_qty'],5,"Wrongquantitytoconsume")
        self.assertEqual(mo_form.move_raw_ids._records[0]['quantity_done'],3,"Wrongquantitydone")
        self.assertEqual(mo_form.move_raw_ids._records[1]['product_uom_qty'],20,"Wrongquantitytoconsume")
        self.assertEqual(mo_form.move_raw_ids._records[1]['quantity_done'],12,"Wrongquantitydone")

    deftest_product_produce_2(self):
        """Checksthat,foraBOMwhereoneofthecomponentsistrackedbyserialnumberandthe
        otherisnottracked,whencreatingamanufacturingorderfortwofinishedproductsand
        reserving,theproducewizardsproposesthecorrectslineswhenproducingoneatatime.
        """
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_base_1='serial',qty_base_1=1,qty_final=2)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        lot_p1_1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })
        lot_p1_2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,1,lot_id=lot_p1_1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,1,lot_id=lot_p1_2)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()

        self.assertEqual(len(mo.move_raw_ids.move_line_ids),3,'Youshouldhave3stockmovelines.Oneforeachserialtoconsumeandfortheuntrackedproduct.')
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()

        #gettheproposedlot
        details_operation_form=Form(mo.move_raw_ids.filtered(lambdamove:move.product_id==p1),view=self.env.ref('stock.view_stock_move_operations'))
        self.assertEqual(len(details_operation_form.move_line_ids),2)
        withdetails_operation_form.move_line_ids.edit(0)asml:
            consumed_lots=ml.lot_id
            ml.qty_done=1
        details_operation_form.save()

        remaining_lot=(lot_p1_1|lot_p1_2)-consumed_lots
        remaining_lot.ensure_one()
        action=mo.button_mark_done()
        backorder=Form(self.env['mrp.production.backorder'].with_context(**action['context']))
        backorder.save().action_backorder()

        #CheckMObackorder
        mo_backorder=mo.procurement_group_id.mrp_production_ids[-1]

        mo_form=Form(mo_backorder)
        mo_form.qty_producing=1
        mo_backorder=mo_form.save()
        details_operation_form=Form(mo_backorder.move_raw_ids.filtered(lambdamove:move.product_id==p1),view=self.env.ref('stock.view_stock_move_operations'))
        self.assertEqual(len(details_operation_form.move_line_ids),1)
        withdetails_operation_form.move_line_ids.edit(0)asml:
            self.assertEqual(ml.lot_id,remaining_lot)

    deftest_product_produce_3(self):
        """Checksthat,foraBOMwhereoneofthecomponentsistrackedbylotandtheotheris
        nottracked,whencreatingamanufacturingorderfor1finishedproductandreserving,the
        reservedlinesaredisplayed.Then,over-consumebycreatingnewline.
        """
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.stock_shelf_1=self.stock_location_components

        self.stock_shelf_2=self.stock_location_14
        mo,_,p_final,p1,p2=self.generate_mo(tracking_base_1='lot',qty_base_1=10,qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        first_lot_for_p1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })
        second_lot_for_p1=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })

        final_product_lot=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':p_final.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p1,self.stock_shelf_1,3,lot_id=first_lot_for_p1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_shelf_2,3,lot_id=first_lot_for_p1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,8,lot_id=second_lot_for_p1)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()
        mo_form=Form(mo)
        mo_form.qty_producing=1.0
        mo_form.lot_producing_id=final_product_lot
        mo=mo_form.save()
        #p2
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asline:
            line.qty_done=line.product_uom_qty
        withdetails_operation_form.move_line_ids.new()asline:
            line.qty_done=1
        details_operation_form.save()

        #p1
        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        foriinrange(len(details_operation_form.move_line_ids)):
            #reservationinshelf1:3lot1,shelf2:3lot1,stock:4lot2
            withdetails_operation_form.move_line_ids.edit(i)asline:
                line.qty_done=line.product_uom_qty
        withdetails_operation_form.move_line_ids.new()asline:
            line.qty_done=2
            line.lot_id=first_lot_for_p1
        withdetails_operation_form.move_line_ids.new()asline:
            line.qty_done=1
            line.lot_id=second_lot_for_p1
        details_operation_form.save()

        move_1=mo.move_raw_ids.filtered(lambdam:m.product_id==p1)
        #qty_done/product_uom_qtylot
        #3/3lot1shelf1
        #1/1lot1shelf2
        #2/2lot1shelf2
        #2/0lot1other
        #5/4lot2
        ml_to_shelf_1=move_1.move_line_ids.filtered(lambdaml:ml.lot_id==first_lot_for_p1andml.location_id==self.stock_shelf_1)
        ml_to_shelf_2=move_1.move_line_ids.filtered(lambdaml:ml.lot_id==first_lot_for_p1andml.location_id==self.stock_shelf_2)

        self.assertEqual(sum(ml_to_shelf_1.mapped('qty_done')),3.0,'3unitsshouldbetookfromshelf1asreserved.')
        self.assertEqual(sum(ml_to_shelf_2.mapped('qty_done')),3.0,'3unitsshouldbetookfromshelf2asreserved.')
        self.assertEqual(move_1.quantity_done,13,'Youshouldhaveusedthetemunits.')

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")

    deftest_product_produce_4(self):
        """Possibilitytoproducewithagivenrawmaterialinmultiplelocations."""
        #FIXMEsle:howisitpossibletoconsumebeforeproducingintheinterface?
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.stock_shelf_1=self.stock_location_components
        self.stock_shelf_2=self.stock_location_14
        mo,_,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=5)

        self.env['stock.quant']._update_available_quantity(p1,self.stock_shelf_1,2)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_shelf_2,3)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,1)

        mo.action_assign()
        ml_p1=mo.move_raw_ids.filtered(lambdax:x.product_id==p1).mapped('move_line_ids')
        ml_p2=mo.move_raw_ids.filtered(lambdax:x.product_id==p2).mapped('move_line_ids')
        self.assertEqual(len(ml_p1),2)
        self.assertEqual(len(ml_p2),1)

        #Addsomequantityalreadydonetoforceanextramovelinetobecreated
        ml_p1[0].qty_done=1.0

        #Producebaby!
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()

        m_p1=mo.move_raw_ids.filtered(lambdax:x.product_id==p1)
        ml_p1=m_p1.mapped('move_line_ids')
        self.assertEqual(len(ml_p1),2)
        self.assertEqual(sorted(ml_p1.mapped('qty_done')),[2.0,3.0],'Quantitydoneshouldbe1.0,2.0or3.0')
        self.assertEqual(m_p1.quantity_done,5.0,'Totalqtydoneshouldbe6.0')
        self.assertEqual(sum(ml_p1.mapped('product_uom_qty')),5.0,'Totalqtyreservedshouldbe5.0')

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")

    deftest_product_produce_6(self):
        """Plan5finishedproducts,reserveandproduce3.Postthecurrentproduction.
        Simulateanunlockandeditand,ontheopenedmoves,settheconsumedquantity
        to3.Now,trytoupdatethequantitytomo2to3.Itshouldfailsincethere
        areconsumedquantities.Unlockandedit,removetheconsumedquantitiesand
        updatethequantitytoproduceto3."""
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo()
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,20)

        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=3
        mo=mo_form.save()

        mo._post_inventory()
        self.assertEqual(len(mo.move_raw_ids),4)

        mo.move_raw_ids.filtered(lambdam:m.state!='done')[0].quantity_done=3

        update_quantity_wizard=self.env['change.production.qty'].create({
            'mo_id':mo.id,
            'product_qty':3,
        })

        mo.move_raw_ids.filtered(lambdam:m.state!='done')[0].quantity_done=0
        update_quantity_wizard.change_prod_qty()

        self.assertEqual(len(mo.move_raw_ids),4)

        mo.button_mark_done()
        self.assertTrue(all(sin['done','cancel']forsinmo.move_raw_ids.mapped('state')))
        self.assertEqual(sum(mo.move_raw_ids.mapped('move_line_ids.product_uom_qty')),0)

    deftest_consumption_strict_1(self):
        """CheckstheconstraintsofastrictBOMwithouttrackingwhenplayingaround
        quantitiestoconsume."""
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(consumption='strict',qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()

        mo_form=Form(mo)

        #tryaddinganotherlineforabomproducttoincreasethequantity
        mo_form.qty_producing=1
        withmo_form.move_raw_ids.new()asline:
            line.product_id=p1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[-1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=1
        details_operation_form.save()
        #Won'taccepttobedone,insteadreturnawizard
        mo.button_mark_done()
        self.assertEqual(mo.state,'to_close')
        consumption_issues=mo._get_consumption_issues()
        action=mo._action_generate_consumption_wizard(consumption_issues)
        warning=Form(self.env['mrp.consumption.warning'].with_context(**action['context']))
        warning=warning.save()

        self.assertEqual(len(warning.mrp_consumption_warning_line_ids),1)
        self.assertEqual(warning.mrp_consumption_warning_line_ids[0].product_consumed_qty_uom,5)
        self.assertEqual(warning.mrp_consumption_warning_line_ids[0].product_expected_qty_uom,4)
        #Forcethewarning(asamanager)
        warning.action_confirm()
        self.assertEqual(mo.state,'done')

    deftest_consumption_warning_1(self):
        """CheckstheconstraintsofastrictBOMwithouttrackingwhenplayingaround
        quantitiestoconsume."""
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(consumption='warning',qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()

        mo_form=Form(mo)

        #tryaddinganotherlineforabomproducttoincreasethequantity
        mo_form.qty_producing=1
        withmo_form.move_raw_ids.new()asline:
            line.product_id=p1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[-1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=1
        details_operation_form.save()

        #Won'taccepttobedone,insteadreturnawizard
        mo.button_mark_done()
        self.assertEqual(mo.state,'to_close')

        consumption_issues=mo._get_consumption_issues()
        action=mo._action_generate_consumption_wizard(consumption_issues)
        warning=Form(self.env['mrp.consumption.warning'].with_context(**action['context']))
        warning=warning.save()

        self.assertEqual(len(warning.mrp_consumption_warning_line_ids),1)
        self.assertEqual(warning.mrp_consumption_warning_line_ids[0].product_consumed_qty_uom,5)
        self.assertEqual(warning.mrp_consumption_warning_line_ids[0].product_expected_qty_uom,4)
        #Forcethewarning(asamanageroremployee)
        warning.action_confirm()
        self.assertEqual(mo.state,'done')

    deftest_consumption_flexible_1(self):
        """CheckstheconstraintsofastrictBOMwithouttrackingwhenplayingaround
        quantitiestoconsume."""
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(consumption='flexible',qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()

        mo_form=Form(mo)

        #tryaddinganotherlineforabomproducttoincreasethequantity
        mo_form.qty_producing=1
        withmo_form.move_raw_ids.new()asline:
            line.product_id=p1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[-1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=1
        details_operation_form.save()

        #Won'taccepttobedone,insteadreturnawizard
        mo.button_mark_done()
        self.assertEqual(mo.state,'done')

    deftest_consumption_flexible_2(self):
        """CheckstheconstraintsofastrictBOMonlyapplytotheproductoftheBoM."""
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(consumption='flexible',qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        add_product=self.env['product.product'].create({
            'name':'additional',
            'type':'product',
        })
        mo.action_assign()

        mo_form=Form(mo)

        #tryaddinganotherlineforabomproducttoincreasethequantity
        mo_form.qty_producing=1
        withmo_form.move_raw_ids.new()asline:
            line.product_id=p1
        withmo_form.move_raw_ids.new()asline:
            line.product_id=add_product
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[-1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=1
        details_operation_form.save()

        #Won'taccepttobedone,insteadreturnawizard
        mo.button_mark_done()
        self.assertEqual(mo.state,'done')

    deftest_product_produce_9(self):
        """Checkstheproductionwizardcontainslinesevenforuntrackedproducts."""
        serial=self.env['product.product'].create({
            'name':'S1',
            'tracking':'serial',
        })
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo()
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)

        mo.action_assign()
        mo_form=Form(mo)

        #changethequantitydoneinoneline
        withself.assertRaises(AssertionError):
            withmo_form.move_raw_ids.new()asmove:
                move.product_id=serial
                move.quantity_done=2
            mo_form.save()

    deftest_product_produce_10(self):
        """Producebyproductwithserial,lotandnottracked.
        byproduct1serial1.0
        byproduct2lot   2.0
        byproduct3none  1.0dozen
        Checkqtyproducingupdateandmovesfinishedvalues.
        """
        dozen=self.env.ref('uom.product_uom_dozen')
        self.byproduct1=self.env['product.product'].create({
            'name':'Byproduct1',
            'type':'product',
            'tracking':'serial'
        })
        self.serial_1=self.env['stock.production.lot'].create({
            'product_id':self.byproduct1.id,
            'name':'serial1',
            'company_id':self.env.company.id,
        })
        self.serial_2=self.env['stock.production.lot'].create({
            'product_id':self.byproduct1.id,
            'name':'serial2',
            'company_id':self.env.company.id,
        })

        self.byproduct2=self.env['product.product'].create({
            'name':'Byproduct2',
            'type':'product',
            'tracking':'lot',
        })
        self.lot_1=self.env['stock.production.lot'].create({
            'product_id':self.byproduct2.id,
            'name':'Lot1',
            'company_id':self.env.company.id,
        })
        self.lot_2=self.env['stock.production.lot'].create({
            'product_id':self.byproduct2.id,
            'name':'Lot2',
            'company_id':self.env.company.id,
        })

        self.byproduct3=self.env['product.product'].create({
            'name':'Byproduct3',
            'type':'product',
            'tracking':'none',
        })

        withForm(self.bom_1)asbom:
            bom.product_qty=1.0
            withbom.byproduct_ids.new()asbp:
                bp.product_id=self.byproduct1
                bp.product_qty=1.0
            withbom.byproduct_ids.new()asbp:
                bp.product_id=self.byproduct2
                bp.product_qty=2.0
            withbom.byproduct_ids.new()asbp:
                bp.product_id=self.byproduct3
                bp.product_qty=2.0
                bp.product_uom_id=dozen

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=self.product_4
        mo_form.bom_id=self.bom_1
        mo_form.product_qty=2
        mo=mo_form.save()

        mo.action_confirm()
        move_byproduct_1=mo.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct1)
        self.assertEqual(len(move_byproduct_1),1)
        self.assertEqual(move_byproduct_1.product_uom_qty,2.0)
        self.assertEqual(move_byproduct_1.quantity_done,0)
        self.assertEqual(len(move_byproduct_1.move_line_ids),0)

        move_byproduct_2=mo.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct2)
        self.assertEqual(len(move_byproduct_2),1)
        self.assertEqual(move_byproduct_2.product_uom_qty,4.0)
        self.assertEqual(move_byproduct_2.quantity_done,0)
        self.assertEqual(len(move_byproduct_2.move_line_ids),0)

        move_byproduct_3=mo.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct3)
        self.assertEqual(move_byproduct_3.product_uom_qty,4.0)
        self.assertEqual(move_byproduct_3.quantity_done,0)
        self.assertEqual(move_byproduct_3.product_uom,dozen)
        self.assertEqual(len(move_byproduct_3.move_line_ids),0)

        mo_form=Form(mo)
        mo_form.qty_producing=1.0
        mo=mo_form.save()
        move_byproduct_1=mo.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct1)
        self.assertEqual(len(move_byproduct_1),1)
        self.assertEqual(move_byproduct_1.product_uom_qty,2.0)
        self.assertEqual(move_byproduct_1.quantity_done,0)

        move_byproduct_2=mo.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct2)
        self.assertEqual(len(move_byproduct_2),1)
        self.assertEqual(move_byproduct_2.product_uom_qty,4.0)
        self.assertEqual(move_byproduct_2.quantity_done,0)

        move_byproduct_3=mo.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct3)
        self.assertEqual(move_byproduct_3.product_uom_qty,4.0)
        self.assertEqual(move_byproduct_3.quantity_done,2.0)
        self.assertEqual(move_byproduct_3.product_uom,dozen)

        details_operation_form=Form(move_byproduct_1,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=self.serial_1
            ml.qty_done=1
        details_operation_form.save()
        details_operation_form=Form(move_byproduct_2,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=self.lot_1
            ml.qty_done=2
        details_operation_form.save()
        action=mo.button_mark_done()
        backorder=Form(self.env['mrp.production.backorder'].with_context(**action['context']))
        backorder.save().action_backorder()
        mo2=mo.procurement_group_id.mrp_production_ids[-1]

        mo_form=Form(mo2)
        mo_form.qty_producing=1
        mo2=mo_form.save()

        move_byproduct_1=mo2.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct1)
        self.assertEqual(len(move_byproduct_1),1)
        self.assertEqual(move_byproduct_1.product_uom_qty,1.0)
        self.assertEqual(move_byproduct_1.quantity_done,0)

        move_byproduct_2=mo2.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct2)
        self.assertEqual(len(move_byproduct_2),1)
        self.assertEqual(move_byproduct_2.product_uom_qty,2.0)
        self.assertEqual(move_byproduct_2.quantity_done,0)

        move_byproduct_3=mo2.move_finished_ids.filtered(lambdal:l.product_id==self.byproduct3)
        self.assertEqual(move_byproduct_3.product_uom_qty,2.0)
        self.assertEqual(move_byproduct_3.quantity_done,2.0)
        self.assertEqual(move_byproduct_3.product_uom,dozen)

        details_operation_form=Form(move_byproduct_1,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=self.serial_2
            ml.qty_done=1
        details_operation_form.save()
        details_operation_form=Form(move_byproduct_2,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=self.lot_2
            ml.qty_done=2
        details_operation_form.save()
        details_operation_form=Form(move_byproduct_3,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=3
        details_operation_form.save()

        mo2.button_mark_done()
        move_lines_byproduct_1=(mo|mo2).move_finished_ids.filtered(lambdal:l.product_id==self.byproduct1).mapped('move_line_ids')
        move_lines_byproduct_2=(mo|mo2).move_finished_ids.filtered(lambdal:l.product_id==self.byproduct2).mapped('move_line_ids')
        move_lines_byproduct_3=(mo|mo2).move_finished_ids.filtered(lambdal:l.product_id==self.byproduct3).mapped('move_line_ids')
        self.assertEqual(move_lines_byproduct_1.filtered(lambdaml:ml.lot_id==self.serial_1).qty_done,1.0)
        self.assertEqual(move_lines_byproduct_1.filtered(lambdaml:ml.lot_id==self.serial_2).qty_done,1.0)
        self.assertEqual(move_lines_byproduct_2.filtered(lambdaml:ml.lot_id==self.lot_1).qty_done,2.0)
        self.assertEqual(move_lines_byproduct_2.filtered(lambdaml:ml.lot_id==self.lot_2).qty_done,2.0)
        self.assertEqual(sum(move_lines_byproduct_3.mapped('qty_done')),5.0)
        self.assertEqual(move_lines_byproduct_3.mapped('product_uom_id'),dozen)

    deftest_product_produce_11(self):
        """Checksthat,foraBOMwithtwocomponents,whencreatingamanufacturingorderforone
        finishedproductsandwithoutreserving,theproducewizardsproposesthecorrectslines
        evenifwechangethequantitytoproducemultipletimes.
        """
        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,4)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,1)

        mo.bom_id.consumption='flexible' #Becausewe'llover-consumewithaproductnotdefinedintheBOM
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=3
        self.assertEqual(sum([x['quantity_done']forxinmo_form.move_raw_ids._records]),15,'Updatetheproducequantityshouldchangethecomponentsquantity.')
        mo=mo_form.save()
        self.assertEqual(sum(mo.move_raw_ids.mapped('reserved_availability')),5,'Updatetheproducequantityshouldnotchangethecomponentsreservedquantity.')
        mo_form=Form(mo)
        mo_form.qty_producing=4
        self.assertEqual(sum([x['quantity_done']forxinmo_form.move_raw_ids._records]),20,'Updatetheproducequantityshouldchangethecomponentsquantity.')
        mo=mo_form.save()
        self.assertEqual(sum(mo.move_raw_ids.mapped('reserved_availability')),5,'Updatetheproducequantityshouldnotchangethecomponentsreservedquantity.')
        mo_form=Form(mo)
        mo_form.qty_producing=1
        self.assertEqual(sum([x['quantity_done']forxinmo_form.move_raw_ids._records]),5,'Updatetheproducequantityshouldchangethecomponentsquantity.')
        mo=mo_form.save()
        self.assertEqual(sum(mo.move_raw_ids.mapped('reserved_availability')),5,'Updatetheproducequantityshouldnotchangethecomponentsreservedquantity.')
        #tryaddinganotherproductthatdoesn'tbelongtotheBoM
        withmo_form.move_raw_ids.new()asmove:
            move.product_id=self.product_4
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[-1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=10
        details_operation_form.save()
        #Checkthatthisnewproductisnotupdatedbyqty_producing
        mo_form=Form(mo)
        mo_form.qty_producing=2
        formoveinmo_form.move_raw_ids._records:
            ifmove['product_id']==self.product_4.id:
                self.assertEqual(move['quantity_done'],10)
                break
        mo=mo_form.save()
        mo.button_mark_done()

    deftest_product_produce_duplicate_1(self):
        """produceafinishedproducttrackedbyserialnumber2timeswiththe
        sameSN.Checkthatanerrorisraisedthesecondtime"""
        mo1,bom,p_final,p1,p2=self.generate_mo(tracking_final='serial',qty_final=1,qty_base_1=1,)

        mo_form=Form(mo1)
        mo_form.qty_producing=1
        mo1=mo_form.save()
        mo1.action_generate_serial()
        sn=mo1.lot_producing_id
        mo1.button_mark_done()

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=p_final
        mo_form.bom_id=bom
        mo_form.product_qty=1
        mo2=mo_form.save()
        mo2.action_confirm()

        mo_form=Form(mo2)
        withself.assertLogs(level="WARNING"):
            mo_form.lot_producing_id=sn
        mo2=mo_form.save()
        withself.assertRaises(UserError):
            mo2.button_mark_done()

    deftest_product_produce_duplicate_2(self):
        """produceafinishedproductwithcomponenttrackedbyserialnumber2
        timeswiththesameSN.Checkthatanerrorisraisedthesecondtime"""
        mo1,bom,p_final,p1,p2=self.generate_mo(tracking_base_2='serial',qty_final=1,qty_base_1=1,)
        sn=self.env['stock.production.lot'].create({
            'name':'snusedtwice',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })
        mo_form=Form(mo1)
        mo_form.qty_producing=1
        mo1=mo_form.save()
        details_operation_form=Form(mo1.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=sn
        details_operation_form.save()
        mo1.button_mark_done()

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=p_final
        mo_form.bom_id=bom
        mo_form.product_qty=1
        mo2=mo_form.save()
        mo2.action_confirm()

        mo_form=Form(mo2)
        mo_form.qty_producing=1
        mo2=mo_form.save()
        details_operation_form=Form(mo2.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=sn
        details_operation_form.save()
        withself.assertRaises(UserError):
            mo2.button_mark_done()

    deftest_product_produce_duplicate_3(self):
        """produceafinishedproductwithby-producttrackedbyserialnumber2
        timeswiththesameSN.Checkthatanerrorisraisedthesecondtime"""
        finished_product=self.env['product.product'].create({'name':'finishedproduct'})
        byproduct=self.env['product.product'].create({'name':'byproduct','tracking':'serial'})
        component=self.env['product.product'].create({'name':'component'})
        bom=self.env['mrp.bom'].create({
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':finished_product.uom_id.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':component.id,'product_qty':1}),
            ],
            'byproduct_ids':[
                (0,0,{'product_id':byproduct.id,'product_qty':1,'product_uom_id':byproduct.uom_id.id})
            ]})
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finished_product
        mo_form.bom_id=bom
        mo_form.product_qty=1
        mo=mo_form.save()
        mo.action_confirm()

        sn=self.env['stock.production.lot'].create({
            'name':'snusedtwice',
            'product_id':byproduct.id,
            'company_id':self.env.company.id,
        })

        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        move_byproduct=mo.move_finished_ids.filtered(lambdam:m.product_id!=mo.product_id)
        details_operation_form=Form(move_byproduct,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=sn
        details_operation_form.save()
        mo.button_mark_done()

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finished_product
        mo_form.bom_id=bom
        mo_form.product_qty=1
        mo2=mo_form.save()
        mo2.action_confirm()

        mo_form=Form(mo2)
        mo_form.qty_producing=1
        mo2=mo_form.save()
        move_byproduct=mo2.move_finished_ids.filtered(lambdam:m.product_id!=mo.product_id)
        details_operation_form=Form(move_byproduct,view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=sn
        details_operation_form.save()
        withself.assertRaises(UserError):
            mo2.button_mark_done()

    deftest_product_produce_duplicate_4(self):
        """Consumingthesameserialnumbertwotimesshouldnotgiveanerrorif
        arepairorderofthefirstproductionhasbeenmadebeforethesecondone"""
        mo1,bom,p_final,p1,p2=self.generate_mo(tracking_base_2='serial',qty_final=1,qty_base_1=1,)
        sn=self.env['stock.production.lot'].create({
            'name':'snusedtwice',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })
        mo_form=Form(mo1)
        mo_form.qty_producing=1
        mo1=mo_form.save()
        details_operation_form=Form(mo1.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=sn
        details_operation_form.save()
        mo1.button_mark_done()

        unbuild_form=Form(self.env['mrp.unbuild'])
        unbuild_form.product_id=p_final
        unbuild_form.bom_id=bom
        unbuild_form.product_qty=1
        unbuild_form.mo_id=mo1
        unbuild_order=unbuild_form.save()
        unbuild_order.action_unbuild()

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=p_final
        mo_form.bom_id=bom
        mo_form.product_qty=1
        mo2=mo_form.save()
        mo2.action_confirm()

        mo_form=Form(mo2)
        mo_form.qty_producing=1
        mo2=mo_form.save()
        details_operation_form=Form(mo2.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=sn
        details_operation_form.save()
        mo2.button_mark_done()

    deftest_product_produce_12(self):
        """Checksthat,theproductionisrobustagainstdeletionoffinishedmove."""

        self.stock_location=self.env.ref('stock.stock_location_stock')
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=1)
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        #removethefinishedmovefromtheavailabletobeupdated
        mo.move_finished_ids._action_done()
        mo.button_mark_done()

    deftest_product_produce_13(self):
        """Checkthattheproductioncannotbecompletedwithoutanyconsumption."""
        product=self.env['product.product'].create({
            'name':'ProductnoBoM',
            'type':'product',
        })
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product
        mo=mo_form.save()
        move=self.env['stock.move'].create({
            'name':'mrp_move',
            'product_id':self.product_2.id,
            'product_uom':self.ref('uom.product_uom_unit'),
            'production_id':mo.id,
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'product_uom_qty':0,
            'quantity_done':0,
        })
        mo.move_raw_ids|=move
        mo.action_confirm()

        mo.qty_producing=1
        #can'tproducewithoutanyconsumption(i.e.componentsw/0consumed)
        withself.assertRaises(UserError):
            mo.button_mark_done()

        mo.move_raw_ids.quantity_done=1
        mo.button_mark_done()
        self.assertEqual(mo.state,'done')

    deftest_product_produce_uom(self):
        """Produceafinishedproducttrackedbyserialnumber.Setanother
        UoMonthebom.TheproducewizardshouldkeeptheUoMoftheproduct(unit)
        andquantity=1."""
        dozen=self.env.ref('uom.product_uom_dozen')
        unit=self.env.ref('uom.product_uom_unit')
        plastic_laminate=self.env['product.product'].create({
            'name':'PlasticLaminate',
            'type':'product',
            'uom_id':unit.id,
            'uom_po_id':unit.id,
            'tracking':'serial',
        })
        ply_veneer=self.env['product.product'].create({
            'name':'PlyVeneer',
            'type':'product',
            'uom_id':unit.id,
            'uom_po_id':unit.id,
        })
        bom=self.env['mrp.bom'].create({
            'product_tmpl_id':plastic_laminate.product_tmpl_id.id,
            'product_uom_id':unit.id,
            'sequence':1,
            'bom_line_ids':[(0,0,{
                'product_id':ply_veneer.id,
                'product_qty':1,
                'product_uom_id':unit.id,
                'sequence':1,
            })]
        })

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=plastic_laminate
        mo_form.bom_id=bom
        mo_form.product_uom_id=dozen
        mo_form.product_qty=1
        mo=mo_form.save()

        final_product_lot=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':plastic_laminate.id,
            'company_id':self.env.company.id,
        })

        mo.action_confirm()
        mo.action_assign()
        self.assertEqual(mo.move_raw_ids.product_qty,12,'12unitsshouldbereserved.')

        #produceproduct
        mo_form=Form(mo)
        mo_form.qty_producing=1/12.0
        mo_form.lot_producing_id=final_product_lot
        mo=mo_form.save()

        move_line_raw=mo.move_raw_ids.mapped('move_line_ids').filtered(lambdam:m.qty_done)
        self.assertEqual(move_line_raw.qty_done,1)
        self.assertEqual(move_line_raw.product_uom_id,unit,'Shouldbe1unitsincethetrackingisserial.')

        mo._post_inventory()
        move_line_finished=mo.move_finished_ids.mapped('move_line_ids').filtered(lambdam:m.qty_done)
        self.assertEqual(move_line_finished.qty_done,1)
        self.assertEqual(move_line_finished.product_uom_id,unit,'Shouldbe1unitsincethetrackingisserial.')

    deftest_product_type_service_1(self):
        #Createfinishedproduct
        finished_product=self.env['product.product'].create({
            'name':'Geyser',
            'type':'product',
        })

        #Createservicetypeproduct
        product_raw=self.env['product.product'].create({
            'name':'rawGeyser',
            'type':'service',
        })

        #Createbomforfinishproduct
        bom=self.env['mrp.bom'].create({
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[(5,0),(0,0,{'product_id':product_raw.id})]
        })

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finished_product
        mo_form.bom_id=bom
        mo_form.product_uom_id=self.env.ref('uom.product_uom_unit')
        mo_form.product_qty=1
        mo=mo_form.save()

        #CheckMoiscreatedornot
        self.assertTrue(mo,"Moiscreated")

    deftest_immediate_validate_1(self):
        """Inaproductionwithasingleavailablemoveraw,clickingonmarkasdonewithoutfillingany
        quantitiesshouldopenawizardaskingtoprocessallthereservation(so,thewholemove).
        """
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=1,qty_base_2=1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location_components,5.0)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location_components,5.0)
        mo.action_assign()
        res_dict=mo.button_mark_done()
        self.assertEqual(res_dict.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(mo.move_raw_ids.mapped('state'),['done','done'])
        self.assertEqual(mo.move_raw_ids.mapped('quantity_done'),[1,1])
        self.assertEqual(mo.move_finished_ids.state,'done')
        self.assertEqual(mo.move_finished_ids.quantity_done,1)

    deftest_immediate_validate_2(self):
        """Inaproductionwithasingleavailablemoveraw,clickingonmarkasdoneafterfillingquantity
        forastockmoveonlywilltriggeranerrorasqty_producingisleftto0."""
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=1,qty_base_2=1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location_components,5.0)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location_components,5.0)
        mo.action_assign()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=1
        details_operation_form.save()
        withself.assertRaises(UserError):
            res_dict=mo.button_mark_done()

    deftest_immediate_validate_3(self):
        """Inaproductionwithaserialnumbertrackedproduct.Checkthattheimmediateproductiononlycreates
        oneunitoffinishedproduct.Testwithreservation."""
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_final='serial',qty_final=2,qty_base_1=1,qty_base_2=1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location_components,5.0)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location_components,5.0)
        mo.action_assign()
        action=mo.button_mark_done()
        self.assertEqual(action.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        action=wizard.process()
        self.assertEqual(action.get('res_model'),'mrp.production.backorder')
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        action=wizard.action_backorder()
        self.assertEqual(mo.qty_producing,1)
        self.assertEqual(mo.move_raw_ids.mapped('quantity_done'),[1,1])
        self.assertEqual(len(mo.procurement_group_id.mrp_production_ids),2)
        mo_backorder=mo.procurement_group_id.mrp_production_ids[-1]
        self.assertEqual(mo_backorder.product_qty,1)
        self.assertEqual(mo_backorder.move_raw_ids.mapped('product_uom_qty'),[1,1])

    deftest_immediate_validate_4(self):
        """Inaproductionwithaserialnumbertrackedproduct.Checkthattheimmediateproductiononlycreates
        oneunitoffinishedproduct.Testwithoutreservation."""
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_final='serial',qty_final=2,qty_base_1=1,qty_base_2=1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location_components,5.0)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location_components,5.0)
        action=mo.button_mark_done()
        self.assertEqual(action.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        action=wizard.process()
        self.assertEqual(action.get('res_model'),'mrp.production.backorder')
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        action=wizard.action_backorder()
        self.assertEqual(mo.qty_producing,1)
        self.assertEqual(mo.move_raw_ids.mapped('quantity_done'),[1,1])
        self.assertEqual(len(mo.procurement_group_id.mrp_production_ids),2)
        mo_backorder=mo.procurement_group_id.mrp_production_ids[-1]
        self.assertEqual(mo_backorder.product_qty,1)
        self.assertEqual(mo_backorder.move_raw_ids.mapped('product_uom_qty'),[1,1])

    deftest_immediate_validate_5(self):
        """Validatethreeproductionsatonce."""
        mo1,bom,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=1,qty_base_2=1)
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location_components,5.0)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location_components,5.0)
        mo1.action_assign()
        mo2_form=Form(self.env['mrp.production'])
        mo2_form.product_id=p_final
        mo2_form.bom_id=bom
        mo2_form.product_qty=1
        mo2=mo2_form.save()
        mo2.action_confirm()
        mo2.action_assign()
        mo3_form=Form(self.env['mrp.production'])
        mo3_form.product_id=p_final
        mo3_form.bom_id=bom
        mo3_form.product_qty=1
        mo3=mo3_form.save()
        mo3.action_confirm()
        mo3.action_assign()
        mos=mo1|mo2|mo3
        res_dict=mos.button_mark_done()
        self.assertEqual(res_dict.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(mos.move_raw_ids.mapped('state'),['done']*6)
        self.assertEqual(mos.move_raw_ids.mapped('quantity_done'),[1]*6)
        self.assertEqual(mos.move_finished_ids.mapped('state'),['done']*3)
        self.assertEqual(mos.move_finished_ids.mapped('quantity_done'),[1]*3)

    deftest_immediate_validate_6(self):
        """Inaproductionforatrackedproduct,clickingonmarkasdonewithoutfillinganyquantitiesshould
        popuptheimmediatetransferwizard.Processingshouldchooseanewlotforthefinishedproduct."""
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=1,qty_base_2=1,tracking_final='lot')
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location_components,5.0)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location_components,5.0)
        mo.action_assign()
        res_dict=mo.button_mark_done()
        self.assertEqual(res_dict.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(mo.move_raw_ids.mapped('state'),['done']*2)
        self.assertEqual(mo.move_raw_ids.mapped('quantity_done'),[1]*2)
        self.assertEqual(mo.move_finished_ids.state,'done')
        self.assertEqual(mo.move_finished_ids.quantity_done,1)
        self.assertTrue(mo.move_finished_ids.move_line_ids.lot_id!=False)

    deftest_immediate_validate_uom(self):
        """Inaproductionwithadifferentuomthanthefinishedproductone,the
        immediateproductionwizardshouldfillthecorrectquantities."""
        p_final=self.env['product.product'].create({
            'name':'final',
            'type':'product',
        })
        component=self.env['product.product'].create({
            'name':'component',
            'type':'product',
        })
        bom=self.env['mrp.bom'].create({
            'product_id':p_final.id,
            'product_tmpl_id':p_final.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'consumption':'flexible',
            'bom_line_ids':[(0,0,{'product_id':component.id,'product_qty':1})]
        })
        self.env['stock.quant']._update_available_quantity(component,self.stock_location_components,25.0)
        mo_form=Form(self.env['mrp.production'])
        mo_form.bom_id=bom
        mo_form.product_uom_id=self.uom_dozen
        mo_form.product_qty=1
        mo=mo_form.save()
        mo.action_confirm()
        mo.action_assign()
        res_dict=mo.button_mark_done()
        self.assertEqual(res_dict.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(mo.move_raw_ids.state,'done')
        self.assertEqual(mo.move_raw_ids.quantity_done,12)
        self.assertEqual(mo.move_finished_ids.state,'done')
        self.assertEqual(mo.move_finished_ids.quantity_done,1)
        self.assertEqual(component.qty_available,13)

    deftest_immediate_validate_uom_2(self):
        """TheroundingprecisionofacomponentshouldbebasedontheUoMusedintheMOforthiscomponent,
        notontheproducedproduct'sUoMnorthedefaultUoMofthecomponent"""
        uom_units=self.env['ir.model.data'].xmlid_to_object('uom.product_uom_unit')
        uom_L=self.env['ir.model.data'].xmlid_to_object('uom.product_uom_litre')
        uom_cL=self.env['uom.uom'].create({
            'name':'cL',
            'category_id':uom_L.category_id.id,
            'uom_type':'smaller',
            'factor':100,
            'rounding':1,
        })
        uom_units.rounding=1
        uom_L.rounding=0.01

        product=self.env['product.product'].create({
            'name':'SuperProduct',
            'uom_id':uom_units.id,
        })
        consumable_component=self.env['product.product'].create({
            'name':'ConsumableComponent',
            'type':'consu',
            'uom_id':uom_cL.id,
            'uom_po_id':uom_cL.id,
        })
        storable_component=self.env['product.product'].create({
            'name':'StorableComponent',
            'type':'product',
            'uom_id':uom_cL.id,
            'uom_po_id':uom_cL.id,
        })
        self.env['stock.quant']._update_available_quantity(storable_component,self.env.ref('stock.stock_location_stock'),100)

        forcomponentin[consumable_component,storable_component]:
            bom=self.env['mrp.bom'].create({
                'product_tmpl_id':product.product_tmpl_id.id,
                'bom_line_ids':[(0,0,{
                    'product_id':component.id,
                    'product_qty':0.2,
                    'product_uom_id':uom_L.id,
                })],
            })

            mo_form=Form(self.env['mrp.production'])
            mo_form.bom_id=bom
            mo=mo_form.save()
            mo.action_confirm()
            action=mo.button_mark_done()
            self.assertEqual(action.get('res_model'),'mrp.immediate.production')
            wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
            action=wizard.process()

            self.assertEqual(mo.move_raw_ids.product_uom_qty,0.2)
            self.assertEqual(mo.move_raw_ids.quantity_done,0.2)

    deftest_copy(self):
        """Checkthatcopyingadoneproduction,createallthestockmoves"""
        mo,bom,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=1,qty_base_2=1)
        mo.action_confirm()
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        mo.button_mark_done()
        self.assertEqual(mo.state,'done')
        mo_copy=mo.copy()
        self.assertTrue(mo_copy.move_raw_ids)
        self.assertTrue(mo_copy.move_finished_ids)
        mo_copy.action_confirm()
        mo_form=Form(mo_copy)
        mo_form.qty_producing=1
        mo_copy=mo_form.save()
        mo_copy.button_mark_done()
        self.assertEqual(mo_copy.state,'done')

    deftest_product_produce_different_uom(self):
        """Checkthatforproductstrackedbylots,
        withcomponentproductUOMdifferentfromUOMusedintheBOM,
        wedonotcreateanewmovelineduetoextrareservedquantity
        causedbydecimalroundingconversions.
        """

        #theoveralldecimalaccuracyissetto3digits
        precision=self.env.ref('product.decimal_product_uom')
        precision.digits=3

        #defineLandml,Lhasrounding.001butmlhasrounding.01
        #whenproducinge.g.187.5ml,itwillberoundedto.188L
        categ_test=self.env['uom.category'].create({'name':'VolumeTest'})

        uom_L=self.env['uom.uom'].create({
            'name':'TestLiters',
            'category_id':categ_test.id,
            'uom_type':'reference',
            'rounding':0.001
        })

        uom_ml=self.env['uom.uom'].create({
            'name':'Testml',
            'category_id':categ_test.id,
            'uom_type':'smaller',
            'rounding':0.01,
            'factor_inv':0.001,
        })

        #createaproductcomponentandthefinalproductusingthecomponent
        product_comp=self.env['product.product'].create({
            'name':'ProductComponent',
            'type':'product',
            'tracking':'lot',
            'categ_id':self.env.ref('product.product_category_all').id,
            'uom_id':uom_L.id,
            'uom_po_id':uom_L.id,
        })

        product_final=self.env['product.product'].create({
            'name':'ProductFinal',
            'type':'product',
            'tracking':'lot',
            'categ_id':self.env.ref('product.product_category_all').id,
            'uom_id':uom_L.id,
            'uom_po_id':uom_L.id,
        })

        #theproductsaretrackedbylot,sowegothrough_generate_consumed_move_line
        lot_final=self.env['stock.production.lot'].create({
            'name':'LotFinal',
            'product_id':product_final.id,
            'company_id':self.env.company.id,
        })

        lot_comp=self.env['stock.production.lot'].create({
            'name':'LotComponent',
            'product_id':product_comp.id,
            'company_id':self.env.company.id,
        })

        #updatethequantityonhandforComponent,inalot
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.env['stock.quant']._update_available_quantity(product_comp,self.stock_location,1,lot_id=lot_comp)

        #createaBOMforFinal,usingComponent
        test_bom=self.env['mrp.bom'].create({
            'product_id':product_final.id,
            'product_tmpl_id':product_final.product_tmpl_id.id,
            'product_uom_id':uom_L.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[(0,0,{
                'product_id':product_comp.id,
                'product_qty':375.00,
                'product_uom_id':uom_ml.id
            })],
        })

        #createaMOforthisBOM
        mo_product_final_form=Form(self.env['mrp.production'])
        mo_product_final_form.product_id=product_final
        mo_product_final_form.product_uom_id=uom_L
        mo_product_final_form.bom_id=test_bom
        mo_product_final_form.product_qty=0.5
        mo_product_final_form=mo_product_final_form.save()

        mo_product_final_form.action_confirm()
        mo_product_final_form.action_assign()
        self.assertEqual(mo_product_final_form.reservation_state,'assigned')

        #produce
        res_dict=mo_product_final_form.button_mark_done()
        self.assertEqual(res_dict.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()

        #checkthatin_generate_consumed_move_line,
        #wedonotcreateanextramovelinebecause
        #ofaconversion187.5ml=0.188L
        #thuscreatinganextralinewith'product_uom_qty':0.5
        self.assertEqual(len(mo_product_final_form.move_raw_ids.move_line_ids),1,'OnemovelineshouldexistfortheMO.')

    deftest_multi_button_plan(self):
        """Testbatchmethods(confirm/validate)oftheMOwiththesamebom"""
        self.bom_2.type="normal" #avoidtogettheoperationofthekitbom

        mo_3=Form(self.env['mrp.production'])
        mo_3.bom_id=self.bom_3
        mo_3=mo_3.save()

        self.assertEqual(len(mo_3.workorder_ids),2)

        mo_3.button_plan()
        self.assertEqual(mo_3.state,'confirmed')
        self.assertEqual(mo_3.workorder_ids[0].state,'ready')

        mo_1=Form(self.env['mrp.production'])
        mo_1.bom_id=self.bom_3
        mo_1=mo_1.save()

        mo_2=Form(self.env['mrp.production'])
        mo_2.bom_id=self.bom_3
        mo_2=mo_2.save()

        self.assertEqual(mo_1.product_id,self.product_6)
        self.assertEqual(mo_2.product_id,self.product_6)
        self.assertEqual(len(self.bom_3.operation_ids),2)
        self.assertEqual(len(mo_1.workorder_ids),2)
        self.assertEqual(len(mo_2.workorder_ids),2)

        (mo_1|mo_2).button_plan() #Confirmandplaninthesame"request"
        self.assertEqual(mo_1.state,'confirmed')
        self.assertEqual(mo_2.state,'confirmed')
        self.assertEqual(mo_1.workorder_ids[0].state,'ready')
        self.assertEqual(mo_2.workorder_ids[0].state,'ready')

        #produce
        res_dict=(mo_1|mo_2).button_mark_done()
        self.assertEqual(res_dict.get('res_model'),'mrp.immediate.production')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(mo_1.state,'done')
        self.assertEqual(mo_2.state,'done')

    deftest_workcenter_timezone(self):
        #WorkcenterisbasedinBangkok
        #PossibleworkinghoursareMondaytoFriday,from8:00to12:00andfrom13:00to17:00(UTC+7)
        workcenter=self.workcenter_1
        workcenter.resource_calendar_id.tz='Asia/Bangkok'

        bom=self.env['mrp.bom'].create({
            'product_tmpl_id':self.product_1.product_tmpl_id.id,
            'bom_line_ids':[(0,0,{
                'product_id':self.product_2.id,
            })],
            'operation_ids':[(0,0,{
                'name':'SuperOperation01',
                'workcenter_id':workcenter.id,
            }),(0,0,{
                'name':'SuperOperation01',
                'workcenter_id':workcenter.id,
            })],
        })

        #NextMondayat6:00amUTC
        date_planned=(Dt.now()+timedelta(days=7-Dt.now().weekday())).replace(hour=6,minute=0,second=0)
        mo_form=Form(self.env['mrp.production'])
        mo_form.bom_id=bom
        mo_form.date_planned_start=date_planned
        mo=mo_form.save()

        mo.workorder_ids[0].duration_expected=240
        mo.workorder_ids[1].duration_expected=60

        mo.action_confirm()
        mo.button_plan()

        #Asia/BangkokisUTC+7andthestartdateisonMondayat06:00UTC(i.e.,13:00UTC+7).
        #So,inBangkok,thefirstworkorderusestheentireMondayafternoonslot13:00-17:00UTC+7(i.e.,06:00-10:00UTC)
        #ThesecondjobusesthebeginningoftheTuesdaymorningslot:08:00-09:00UTC+7(i.e.,01:00-02:00UTC)
        self.assertEqual(mo.workorder_ids[0].date_planned_start,date_planned)
        self.assertEqual(mo.workorder_ids[0].date_planned_finished,date_planned+timedelta(hours=4))
        tuesday=date_planned+timedelta(days=1)
        self.assertEqual(mo.workorder_ids[1].date_planned_start,tuesday.replace(hour=1))
        self.assertEqual(mo.workorder_ids[1].date_planned_finished,tuesday.replace(hour=2))

    deftest_backorder_with_underconsumption(self):
        """Checkthatthecomponentsofthebackorderhavethecorrectquantities
        whenthereisunderconsumptionintheinitialMO
        """
        mo,_,_,p1,p2=self.generate_mo(qty_final=20,qty_base_1=1,qty_base_2=1)
        mo.action_confirm()
        mo.qty_producing=10
        mo.move_raw_ids.filtered(lambdam:m.product_id==p1).quantity_done=5
        mo.move_raw_ids.filtered(lambdam:m.product_id==p2).quantity_done=10
        action=mo.button_mark_done()
        backorder=Form(self.env['mrp.production.backorder'].with_context(**action['context']))
        backorder.save().action_backorder()
        mo_backorder=mo.procurement_group_id.mrp_production_ids[-1]

        #CheckquantitiesoftheoriginalMO
        self.assertEqual(mo.product_uom_qty,10.0)
        self.assertEqual(mo.qty_produced,10.0)
        move_prod_1_done=mo.move_raw_ids.filtered(lambdam:m.product_id==p1andm.state=='done')
        self.assertEqual(sum(move_prod_1_done.mapped('quantity_done')),5)
        self.assertEqual(sum(move_prod_1_done.mapped('product_uom_qty')),5)
        move_prod_1_cancel=mo.move_raw_ids.filtered(lambdam:m.product_id==p1andm.state=='cancel')
        self.assertEqual(sum(move_prod_1_cancel.mapped('quantity_done')),0)
        self.assertEqual(sum(move_prod_1_cancel.mapped('product_uom_qty')),5)
        move_prod_2=mo.move_raw_ids.filtered(lambdam:m.product_id==p2)
        self.assertEqual(sum(move_prod_2.mapped('quantity_done')),10)
        self.assertEqual(sum(move_prod_2.mapped('product_uom_qty')),10)

        #CheckquantitiesofthebackorderMO
        self.assertEqual(mo_backorder.product_uom_qty,10.0)
        move_prod_1_bo=mo_backorder.move_raw_ids.filtered(lambdam:m.product_id==p1)
        move_prod_2_bo=mo_backorder.move_raw_ids.filtered(lambdam:m.product_id==p2)
        self.assertEqual(sum(move_prod_1_bo.mapped('product_uom_qty')),10.0)
        self.assertEqual(sum(move_prod_2_bo.mapped('product_uom_qty')),10.0)

    deftest_products_with_variants(self):
        """Checkforproductwithdifferentvariantswithsamebom"""
        product=self.env['product.template'].create({
            "attribute_line_ids":[
                [0,0,{"attribute_id":2,"value_ids":[[6,0,[3,4]]]}]
            ],
            "name":"Productwithvariants",
        })

        variant_1=product.product_variant_ids[0]
        variant_2=product.product_variant_ids[1]

        component=self.env['product.template'].create({
            "name":"Component",
        })

        self.env['mrp.bom'].create({
            'product_id':False,
            'product_tmpl_id':product.id,
            'bom_line_ids':[
                (0,0,{'product_id':component.product_variant_id.id,'product_qty':1})
            ]
        })

        #Firstbehaviortocheck,ischangingtheproduct(sameproductbutanothervariant)aftersavingtheMOafirsttime.
        mo_form_1=Form(self.env['mrp.production'])
        mo_form_1.product_id=variant_1
        mo_1=mo_form_1.save()
        mo_form_1=Form(self.env['mrp.production'].browse(mo_1.id))
        mo_form_1.product_id=variant_2
        mo_1=mo_form_1.save()
        mo_1.action_confirm()
        mo_1.action_assign()
        mo_form_1=Form(self.env['mrp.production'].browse(mo_1.id))
        mo_form_1.qty_producing=1
        mo_1=mo_form_1.save()
        mo_1.button_mark_done()

        move_lines_1=self.env['stock.move.line'].search([("reference","=",mo_1.name)])
        move_finished_ids_1=self.env['stock.move'].search([("production_id","=",mo_1.id)])
        self.assertEqual(len(move_lines_1),2,"Thereshouldonlybe2movelines:thecomponentlineandproducedproductline")
        self.assertEqual(len(move_finished_ids_1),1,"Thereshouldonlybe1producedproductforthisMO")
        self.assertEqual(move_finished_ids_1.product_id,variant_2,"Incorrectvariantproduced")

        #SecondbehaviorischangingtheproductbeforesavingtheMO
        mo_form_2=Form(self.env['mrp.production'])
        mo_form_2.product_id=variant_1
        mo_form_2.product_id=variant_2
        mo_2=mo_form_2.save()
        mo_2.action_confirm()
        mo_2.action_assign()
        mo_form_2=Form(self.env['mrp.production'].browse(mo_2.id))
        mo_form_2.qty_producing=1
        mo_2=mo_form_2.save()
        mo_2.button_mark_done()

        move_lines_2=self.env['stock.move.line'].search([("reference","=",mo_2.name)])
        move_finished_ids_2=self.env['stock.move'].search([("production_id","=",mo_2.id)])
        self.assertEqual(len(move_lines_2),2,"Thereshouldonlybe2movelines:thecomponentlineandproducedproductline")
        self.assertEqual(len(move_finished_ids_2),1,"Thereshouldonlybe1producedproductforthisMO")
        self.assertEqual(move_finished_ids_2.product_id,variant_2,"Incorrectvariantproduced")

        #ThirdbehaviorischangingtheproductbeforesavingtheMO,thenanothertimeafter
        mo_form_3=Form(self.env['mrp.production'])
        mo_form_3.product_id=variant_1
        mo_form_3.product_id=variant_2
        mo_3=mo_form_3.save()
        mo_form_3=Form(self.env['mrp.production'].browse(mo_3.id))
        mo_form_3.product_id=variant_1
        mo_3=mo_form_3.save()
        mo_3.action_confirm()
        mo_3.action_assign()
        mo_form_3=Form(self.env['mrp.production'].browse(mo_3.id))
        mo_form_3.qty_producing=1
        mo_3=mo_form_3.save()
        mo_3.button_mark_done()

        move_lines_3=self.env['stock.move.line'].search([("reference","=",mo_3.name)])
        move_finished_ids_3=self.env['stock.move'].search([("production_id","=",mo_3.id)])
        self.assertEqual(len(move_lines_3),2,"Thereshouldonlybe2movelines:thecomponentlineandproducedproductline")
        self.assertEqual(len(move_finished_ids_3),1,"Thereshouldonlybe1producedproductforthisMO")
        self.assertEqual(move_finished_ids_3.product_id,variant_1,"Incorrectvariantproduced")

    deftest_manufacturing_order_with_work_orders(self):
        """Testthebehaviorofamanufacturingorderwhenopeningtheworkorderrelatedtoit,
           aswellasthebehaviorwhenabackorderiscreated
           """
        #createafewworkcenters
        work_center_1=self.env['mrp.workcenter'].create({"name":"WC1"})
        work_center_2=self.env['mrp.workcenter'].create({"name":"WC2"})
        work_center_3=self.env['mrp.workcenter'].create({"name":"WC3"})

        #createaproduct,abomrelatedtoitwith3componentsand3operations
        product=self.env['product.template'].create({"name":"Product"})
        component_1=self.env['product.template'].create({"name":"Component1","type":"product"})
        component_2=self.env['product.template'].create({"name":"Component2","type":"product"})
        component_3=self.env['product.template'].create({"name":"Component3","type":"product"})

        self.env['stock.quant'].create({
            "product_id":component_1.product_variant_id.id,
            "location_id":8,
            "inventory_quantity":100
        })
        self.env['stock.quant'].create({
            "product_id":component_2.product_variant_id.id,
            "location_id":8,
            "inventory_quantity":100
        })
        self.env['stock.quant'].create({
            "product_id":component_3.product_variant_id.id,
            "location_id":8,
            "inventory_quantity":100
        })

        self.env['mrp.bom'].create({
            "product_tmpl_id":product.id,
            "product_id":False,
            "product_qty":1,
            "bom_line_ids":[
                [0,0,{"product_id":component_1.product_variant_id.id,"product_qty":1}],
                [0,0,{"product_id":component_2.product_variant_id.id,"product_qty":1}],
                [0,0,{"product_id":component_3.product_variant_id.id,"product_qty":1}]
            ],
            "operation_ids":[
                [0,0,{"name":"Operation1","workcenter_id":work_center_1.id}],
                [0,0,{"name":"Operation2","workcenter_id":work_center_2.id}],
                [0,0,{"name":"Operation3","workcenter_id":work_center_3.id}]
            ]
        })

        #createamanufacturingorderwith10producttoproduce
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product.product_variant_id
        mo_form.product_qty=10
        mo=mo_form.save()

        self.assertEqual(mo.state,'draft')
        mo.action_confirm()

        wo_1=mo.workorder_ids[0]
        wo_2=mo.workorder_ids[1]
        wo_3=mo.workorder_ids[2]
        self.assertEqual(mo.state,'confirmed')

        duration_expected=wo_1.duration_expected
        wo_1.button_start()
        self.assertEqual(mo.state,'progress')
        wo_1.button_finish()
        self.assertEqual(duration_expected,wo_1.duration_expected)

        duration_expected=wo_2.duration_expected
        wo_2.button_start()
        wo_2.qty_producing=8
        wo_2.button_finish()
        self.assertEqual(duration_expected,wo_2.duration_expected)

        duration_expected=wo_3.duration_expected
        wo_3.button_start()
        wo_3.qty_producing=8
        wo_3.button_finish()
        self.assertEqual(duration_expected,wo_3.duration_expected)

        self.assertEqual(mo.state,'to_close')
        mo.button_mark_done()

        bo=self.env['mrp.production.backorder'].create({
            "mrp_production_backorder_line_ids":[
                [0,0,{"mrp_production_id":mo.id,"to_backorder":True}]
            ]
        })
        bo.action_backorder()

        self.assertEqual(mo.state,'done')

        mo_2=self.env['mrp.production'].browse(mo.id+1)
        self.assertEqual(mo_2.state,'progress')
        wo_4,wo_5,wo_6=mo_2.workorder_ids
        self.assertEqual(wo_4.state,'cancel')

        wo_5.button_start()
        self.assertEqual(mo_2.state,'progress')
        wo_5.button_finish()

        wo_6.button_start()
        wo_6.button_finish()
        self.assertEqual(mo_2.state,'to_close')
        mo_2.button_mark_done()
        self.assertEqual(mo_2.state,'done')

    deftest_move_finished_onchanges(self):
        """Testthatmove_finished_ids(i.e.producedproducts)arestillcorrectevenafter
        multipleonchangeshavechangedthethemoves
        """

        product1=self.env['product.product'].create({
            'name':'OatmealCookie',
        })
        product2=self.env['product.product'].create({
            'name':'ChocolateChipCookie',
        })

        #=====product_idonchangechecks=====#
        #checkproduct_idonchangewithoutsaving
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product1
        mo_form.product_id=product2
        mo=mo_form.save()
        self.assertEqual(len(mo.move_finished_ids),1,'Wrongnumberoffinishedproductmovescreated')
        self.assertEqual(mo.move_finished_ids.product_id,product2,'Wrongproducttoproduceinfinishedproductmove')
        #checkproduct_idonchangeaftersaving
        mo_form=Form(self.env['mrp.production'].browse(mo.id))
        mo_form.product_id=product1
        mo=mo_form.save()
        self.assertEqual(len(mo.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo.move_finished_ids.product_id,product1,'Wrongproducttoproduceinfinishedproductmove')
        #checkproduct_idonchangewhenmo._origin.product_idisunchanged
        mo_form=Form(self.env['mrp.production'].browse(mo.id))
        mo_form.product_id=product2
        mo_form.product_id=product1
        mo=mo_form.save()
        self.assertEqual(len(mo.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo.move_finished_ids.product_id,product1,'Wrongproducttoproduceinfinishedproductmove')

        #=====product_qtyonchangechecks=====#
        #checkproduct_qtyonchangewithoutsaving
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product1
        mo_form.product_qty=5
        mo_form.product_qty=10
        mo2=mo_form.save()
        self.assertEqual(len(mo2.move_finished_ids),1,'Wrongnumberoffinishedproductmovescreated')
        self.assertEqual(mo2.move_finished_ids.product_qty,10,'Wrongqtytoproduceforthefinishedproductmove')

        #checkproduct_qtyonchangeaftersaving
        mo_form=Form(self.env['mrp.production'].browse(mo2.id))
        mo_form.product_qty=5
        mo2=mo_form.save()
        self.assertEqual(len(mo2.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo2.move_finished_ids.product_qty,5,'Wrongqtytoproduceforthefinishedproductmove')

        #checkproduct_qtyonchangewhenmo._origin.product_idisunchanged
        mo_form=Form(self.env['mrp.production'].browse(mo2.id))
        mo_form.product_qty=10
        mo_form.product_qty=5
        mo2=mo_form.save()
        self.assertEqual(len(mo2.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo2.move_finished_ids.product_qty,5,'Wrongqtytoproduceforthefinishedproductmove')

        #=====product_uom_idonchangechecks=====#
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product1
        mo_form.product_qty=1
        mo_form.product_uom_id=self.env['uom.uom'].browse(self.ref('uom.product_uom_dozen'))
        mo3=mo_form.save()
        self.assertEqual(len(mo3.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo3.move_finished_ids.product_qty,12,'Wrongqtytoproduceforthefinishedproductmove')

        #=====bom_idonchangechecks=====#
        component=self.env['product.product'].create({
            "name":"Sugar",
        })

        bom1=self.env['mrp.bom'].create({
            'product_id':False,
            'product_tmpl_id':product1.product_tmpl_id.id,
            'bom_line_ids':[
                (0,0,{'product_id':component.id,'product_qty':1})
            ]
        })

        bom2=self.env['mrp.bom'].create({
            'product_id':False,
            'product_tmpl_id':product1.product_tmpl_id.id,
            'bom_line_ids':[
                (0,0,{'product_id':component.id,'product_qty':10})
            ]
        })
        #checkbom_idonchangebeforeproductchange
        mo_form=Form(self.env['mrp.production'])
        mo_form.bom_id=bom1
        mo_form.bom_id=bom2
        mo_form.product_id=product2
        mo4=mo_form.save()
        self.assertFalse(mo4.bom_id,'BoMshouldhavebeenremoved')
        self.assertEqual(len(mo4.move_finished_ids),1,'Wrongnumberoffinishedproductmovescreated')
        self.assertEqual(mo4.move_finished_ids.product_id,product2,'Wrongproducttoproduceinfinishedproductmove')
        #checkbom_idonchangeafterproductchange
        mo_form=Form(self.env['mrp.production'].browse(mo4.id))
        mo_form.product_id=product1
        mo_form.bom_id=bom1
        mo_form.bom_id=bom2
        mo4=mo_form.save()
        self.assertEqual(len(mo4.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo4.move_finished_ids.product_id,product1,'Wrongproducttoproduceinfinishedproductmove')
        #checkproduct_idonchangewhenmo._origin.product_idisunchanged
        mo_form=Form(self.env['mrp.production'].browse(mo4.id))
        mo_form.bom_id=bom2
        mo_form.bom_id=bom1
        mo4=mo_form.save()
        self.assertEqual(len(mo4.move_finished_ids),1,'Wrongnumberoffinishproductmovescreated')
        self.assertEqual(mo4.move_finished_ids.product_id,product1,'Wrongproducttoproduceinfinishedproductmove')

    deftest_compute_tracked_time_1(self):
        """
        ChecksthattheDurationComputation(`time_mode`ofmrp.routing.workcenter)withvalue`auto`withBasedOn
        (`time_mode_batch`)setto1actuallycomputethetimebasedonthelast1operation,andnotmore.
        Createafirstproductionin15minutes(expectedshouldgofrom60to15
        Createasecondonein10minutes(expectedshouldNOTgofrom15to12.5,itshouldgofrom15to10)
        """
        #Firstproduction,thedefaultis60andthereis0productionsofthatoperation
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_4
        production=production_form.save()
        self.assertEqual(production.workorder_ids[0].duration_expected,60.0,"Defaultdurationis0+0+1*60.0")
        production.action_confirm()
        production.button_plan()
        #Productionplanned,timetostart,Iproduceallthe1product
        production_form.qty_producing=1
        withproduction_form.workorder_ids.edit(0)aswo:
            wo.duration=15#in15minutes
        production=production_form.save()
        production.button_mark_done()
        #Itissavedanddone,registeredinthedb.Therearenow1productionsofthatoperation

        #Sameproduction,let'sseewhattheduration_expectedis,lastprodwas15minutesfor1item
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_4
        production=production_form.save()
        self.assertEqual(production.workorder_ids[0].duration_expected,15.0,"Durationisnow0+0+1*15")
        production.action_confirm()
        production.button_plan()
        #Productionplanned,timetostart,Iproduceallthe1product
        production_form.qty_producing=1
        withproduction_form.workorder_ids.edit(0)aswo:
            wo.duration=10 #In10minutesthistime
        production=production_form.save()
        production.button_mark_done()
        #Itissavedanddone,registeredinthedb.Therearenow2productionsofthatoperation

        #Sameproduction,let'sseewhattheduration_expectedis,lastprodwas10minutesfor1item
        #Totalaveragetimewouldbe12.5butwecomputethedurationbasedonthelast1item
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_4
        production=production_form.save()
        self.assertNotEqual(production.workorder_ids[0].duration_expected,12.5,"Durationexpectedisbasedonthelast1production,notlast2")
        self.assertEqual(production.workorder_ids[0].duration_expected,10.0,"Durationisnow0+0+1*10")

    deftest_compute_tracked_time_2_under_capacity(self):
        """
        Testthatwhentrackingthe2lastproduction,ifwemakeonewithundercapacity,andonewithnormalcapacity,
        thetwoareequivalent(1donewithcapacity2in10mn=2donewithcapacity2in10mn)
        """
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_5
        production=production_form.save()
        production.action_confirm()
        production.button_plan()

        #Productionplanned,timetostart,Iproduceallthe1product
        production_form.qty_producing=1
        withproduction_form.workorder_ids.edit(0)aswo:
            wo.duration=10 #in10minutes
        production=production_form.save()
        production.button_mark_done()
        #Itissavedanddone,registeredinthedb.Therearenow1productionsofthatoperation

        #Sameproduction,let'sseewhattheduration_expectedis,lastprodwas10minutesfor1item
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_5
        production_form.product_qty=2 #Wewanttoproduce2items(thecapacity)now
        production=production_form.save()
        self.assertNotEqual(production.workorder_ids[0].duration_expected,20.0,"Wemade1itemwithcapacity2in10mn->so2itemsshouldn'tbedoublethat")
        self.assertEqual(production.workorder_ids[0].duration_expected,10.0,"Producing1or2itemswithcapacity2isthesameduration")
        production.action_confirm()
        production.button_plan()
        #Productionplanned,timetostart,Iproduceallthe2product
        production_form.qty_producing=2
        withproduction_form.workorder_ids.edit(0)aswo:
            wo.duration=10 #In10minutesthistime
        production=production_form.save()
        production.button_mark_done()
        #Itissavedanddone,registeredinthedb.Therearenow2productionsofthatoperationbuttheyhavethesameduration

        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_5
        production=production_form.save()
        self.assertNotEqual(production.workorder_ids[0].duration_expected,15,"Producing1or2in10mnwithcapacity2takethesameamountoftime:10mn")
        self.assertEqual(production.workorder_ids[0].duration_expected,10.0,"Durationisindeed(10+10)/2")

    deftest_capacity_duration_expected(self):
        """
        Testthatthedurationexpectediscorrectlycomputedwhendealingwithbeloworabovecapacity
        1->10mn
        2->10mn
        3->20mn
        4->20mn
        5->30mn
        ...
        """
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_6
        production=production_form.save()
        production.action_confirm()
        production.button_plan()

        #Productionplanned,timetostart,Iproduceallthe1product
        production_form.qty_producing=1
        withproduction_form.workorder_ids.edit(0)aswo:
            wo.duration=10 #in10minutes
        production=production_form.save()
        production.button_mark_done()

        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_6
        production=production_form.save()
        #production_form.product_qty=1[BYDEFAULT]
        self.assertEqual(production.workorder_ids[0].duration_expected,10.0,"Produce1withcapacity2,expectedis10mnforeachrun->10mn")
        production_form.product_qty=2
        production=production_form.save()
        self.assertEqual(production.workorder_ids[0].duration_expected,10.0,"Produce2withcapacity2,expectedis10mnforeachrun->10mn")

        production_form.product_qty=3
        production=production_form.save()
        self.assertEqual(production.workorder_ids[0].duration_expected,20.0,"Produce3withcapacity2,expectedis10mnforeachrun->20mn")

        production_form.product_qty=4
        production=production_form.save()
        self.assertEqual(production.workorder_ids[0].duration_expected,20.0,"Produce4withcapacity2,expectedis10mnforeachrun->20mn")

        production_form.product_qty=5
        production=production_form.save()
        self.assertEqual(production.workorder_ids[0].duration_expected,30.0,"Produce5withcapacity2,expectedis10mnforeachrun->30mn")

    deftest_planning_workorder(self):
        """
            Checkthatthefastestworkcenterisusedwhenplanningtheworkorder.

            -createtwoworkcenterswithsimilarproductioncapacity
                butthework_center_2withalongerstartandstoptime.

            1:/produce2units>work_center_1fasterbecause
                itdoesnotneedmuchtimetostartandtofinishtheproduction.

            2/-updatetheproductioncapacityofthework_center_2to4
                -produce4units>work_center_2fasterbecause
                itmustdoasinglecyclewhilethework_center_1havetodotwocycles.
        """
        workcenter_1=self.env['mrp.workcenter'].create({
            'name':'wc1',
            'capacity':2,
            'time_start':1,
            'time_stop':1,
            'time_efficiency':100,
        })

        workcenter_2=self.env['mrp.workcenter'].create({
            'name':'wc2',
            'capacity':2,
            'time_start':10,
            'time_stop':5,
            'time_efficiency':100,
            'alternative_workcenter_ids':[workcenter_1.id]
        })

        product_to_build=self.env['product.product'].create({
            'name':'finalproduct',
            'type':'product',
        })

        product_to_use=self.env['product.product'].create({
            'name':'component',
            'type':'product',
        })

        bom=self.env['mrp.bom'].create({
            'product_id':product_to_build.id,
            'product_tmpl_id':product_to_build.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'consumption':'flexible',
            'operation_ids':[
                (0,0,{'name':'Test','workcenter_id':workcenter_2.id,'time_cycle':60,'sequence':1}),
            ],
            'bom_line_ids':[
                (0,0,{'product_id':product_to_use.id,'product_qty':1}),
            ]})

        #MO_1
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product_to_build
        mo_form.bom_id=bom
        mo_form.product_qty=2
        mo=mo_form.save()
        mo.action_confirm()
        mo.button_plan()
        self.assertEqual(mo.workorder_ids[0].workcenter_id.id,workcenter_1.id,'workcenter_1isfasterthanworkcenter_2tomanufacture2units')
        #Unplanthemotopreventthefirstworkcenterfrombeingbusy
        mo.button_unplan()

        #Updatetheproductioncapcity
        workcenter_2.capacity=4

        #MO_2
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product_to_build
        mo_form.bom_id=bom
        mo_form.product_qty=4
        mo_2=mo_form.save()
        mo_2.action_confirm()
        mo_2.button_plan()
        self.assertEqual(mo_2.workorder_ids[0].workcenter_id.id,workcenter_2.id,'workcenter_2isfasterthanworkcenter_1tomanufacture4units')

    deftest_starting_wo_twice(self):
        """
            Checkthattheworkorderisstartedonlyoncewhenclickingthestartbuttonseveraltimes.
        """
        production_form=Form(self.env['mrp.production'])
        production_form.bom_id=self.bom_2
        production_form.product_qty=1
        production=production_form.save()
        production_form=Form(production)
        withproduction_form.workorder_ids.new()aswo:
            wo.name='OP1'
            wo.workcenter_id=self.workcenter_1
            wo.duration_expected=40
        production=production_form.save()
        production.action_confirm()
        production.button_plan()
        production.workorder_ids[0].button_start()
        production.workorder_ids[0].button_start()
        self.assertEqual(len(production.workorder_ids[0].time_ids.filtered(lambdat:t.date_startandnott.date_end)),1)

    @freeze_time('2022-06-2808:00')
    deftest_replan_workorders01(self):
        """
        CreatetwoMO,eachonewithoneWO.Setthesamescheduledstartdate
        toeachWOduringthecreationoftheMO.Awarningwillbedisplayed.
        ->TheuserreplansoneoftheWO:thewarningsshoulddisappearandthe
        WOshouldbepostponed.
        """
        mos=self.env['mrp.production']
        for_inrange(2):
            mo_form=Form(self.env['mrp.production'])
            mo_form.bom_id=self.bom_4
            withmo_form.workorder_ids.edit(0)aswo_line:
                wo_line.date_planned_start=Dt.now()
            mos+=mo_form.save()
        mos.action_confirm()

        mo_01,mo_02=mos
        wo_01=mo_01.workorder_ids
        wo_02=mo_02.workorder_ids

        self.assertTrue(wo_01.show_json_popover)
        self.assertTrue(wo_02.show_json_popover)

        wo_02.action_replan()

        self.assertFalse(wo_01.show_json_popover)
        self.assertFalse(wo_02.show_json_popover)
        self.assertEqual(wo_01.date_planned_finished,wo_02.date_planned_start)

    @freeze_time('2022-06-2808:00')
    deftest_replan_workorders02(self):
        """
        CreatetwoMO,eachonewithoneWO.Setthesamescheduledstartdate
        toeachWOafterthecreationoftheMO.Awarningwillbedisplayed.
        ->TheuserreplansoneoftheWO:thewarningsshoulddisappearandthe
        WOshouldbepostponed.
        """
        mos=self.env['mrp.production']
        for_inrange(2):
            mo_form=Form(self.env['mrp.production'])
            mo_form.bom_id=self.bom_4
            mos+=mo_form.save()
        mos.action_confirm()
        mo_01,mo_02=mos

        formoinmos:
            withForm(mo)asmo_form:
                withmo_form.workorder_ids.edit(0)aswo_line:
                    wo_line.date_planned_start=Dt.now()

        wo_01=mo_01.workorder_ids
        wo_02=mo_02.workorder_ids
        self.assertTrue(wo_01.show_json_popover)
        self.assertTrue(wo_02.show_json_popover)

        wo_02.action_replan()

        self.assertFalse(wo_01.show_json_popover)
        self.assertFalse(wo_02.show_json_popover)
        self.assertEqual(wo_01.date_planned_finished,wo_02.date_planned_start)

    deftest_backorder_with_overconsumption(self):
        """Checkthatthecomponentsofthebackorderhavethecorrectquantities
        whenthereisoverconsumptionintheinitialMO
        """
        mo,_,_,_,_=self.generate_mo(qty_final=30,qty_base_1=2,qty_base_2=3)
        mo.action_confirm()
        mo.qty_producing=10
        mo.move_raw_ids[0].quantity_done=90
        mo.move_raw_ids[1].quantity_done=70
        action=mo.button_mark_done()
        backorder=Form(self.env['mrp.production.backorder'].with_context(**action['context']))
        backorder.save().action_backorder()
        mo_backorder=mo.procurement_group_id.mrp_production_ids[-1]

        #CheckquantitiesoftheoriginalMO
        self.assertEqual(mo.product_uom_qty,10.0)
        self.assertEqual(mo.qty_produced,10.0)
        move_prod_1=self.env['stock.move'].search([
            ('product_id','=',mo.bom_id.bom_line_ids[0].product_id.id),
            ('raw_material_production_id','=',mo.id)])
        move_prod_2=self.env['stock.move'].search([
            ('product_id','=',mo.bom_id.bom_line_ids[1].product_id.id),
            ('raw_material_production_id','=',mo.id)])
        self.assertEqual(sum(move_prod_1.mapped('quantity_done')),90.0)
        self.assertEqual(sum(move_prod_1.mapped('product_uom_qty')),90.0)
        self.assertEqual(sum(move_prod_2.mapped('quantity_done')),70.0)
        self.assertEqual(sum(move_prod_2.mapped('product_uom_qty')),70.0)

        #CheckquantitiesofthebackorderMO
        self.assertEqual(mo_backorder.product_uom_qty,20.0)
        move_prod_1_bo=self.env['stock.move'].search([
            ('product_id','=',mo.bom_id.bom_line_ids[0].product_id.id),
            ('raw_material_production_id','=',mo_backorder.id)])
        move_prod_2_bo=self.env['stock.move'].search([
            ('product_id','=',mo.bom_id.bom_line_ids[1].product_id.id),
            ('raw_material_production_id','=',mo_backorder.id)])
        self.assertEqual(sum(move_prod_1_bo.mapped('product_uom_qty')),60.0)
        self.assertEqual(sum(move_prod_2_bo.mapped('product_uom_qty')),40.0)

    deftest_update_qty_to_consume_of_component(self):
        """
        TheUoMofthefinishedproducthasaroundingprecisionequalto1.0
        andtheUoMofthecomponenthasadecimalone.Whentheproducingqty
        isset,anonchangeautocompletetheconsumedquantityofthecomponent.
        Then,whenupdatingthe'toconsume'quantityofthecomponents,their
        consumedquantityisupdatedagain.Thetestensuresthatthisupdate
        respectstheroundingprecisions
        """
        self.uom_dozen.rounding=1
        self.bom_4.product_uom_id=self.uom_dozen

        mo_form=Form(self.env['mrp.production'])
        mo_form.bom_id=self.bom_4
        mo=mo_form.save()
        mo.action_confirm()

        withForm(mo)asmo_form:
            mo_form.qty_producing=1
            withmo_form.move_raw_ids.edit(0)asraw:
                raw.product_uom_qty=1.25

        self.assertEqual(mo.move_raw_ids.quantity_done,1.25)

    deftest_onchange_bom_ids_and_picking_type(self):
        warehouse01=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        warehouse02,warehouse03=self.env['stock.warehouse'].create([
            {'name':'SecondWarehouse','code':'WH02'},
            {'name':'ThirdWarehouse','code':'WH03'},
        ])

        finished_product=self.env['product.product'].create({'name':'finishedproduct'})
        bom_wh01,bom_wh02=self.env['mrp.bom'].create([{
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'bom_line_ids':[(0,0,{'product_id':self.product_0.id,'product_qty':1})],
            'picking_type_id':wh.manu_type_id.id,
            'sequence':wh.id,
        }forwhin[warehouse01,warehouse02]])

        #PrioritizeBoMofWH02
        bom_wh01.sequence=bom_wh02.sequence+1

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finished_product
        self.assertEqual(mo_form.bom_id,bom_wh02,'ShouldselectthefirstBoMinthelist,whateverthepickingtypeis')
        self.assertEqual(mo_form.picking_type_id,warehouse02.manu_type_id)

        mo_form.bom_id=bom_wh01
        self.assertEqual(mo_form.picking_type_id,warehouse01.manu_type_id,'ShouldbeadaptedbecauseofthefoundBoM')

        mo_form.bom_id=bom_wh02
        self.assertEqual(mo_form.picking_type_id,warehouse02.manu_type_id,'ShouldbeadaptedbecauseofthefoundBoM')

        mo_form.picking_type_id=warehouse01.manu_type_id
        self.assertEqual(mo_form.bom_id,bom_wh02,'Shouldnotchange')
        self.assertEqual(mo_form.picking_type_id,warehouse01.manu_type_id,'Shouldnotchange')

        mo_form.picking_type_id=warehouse03.manu_type_id
        mo_form.bom_id=bom_wh01
        self.assertEqual(mo_form.picking_type_id,warehouse01.manu_type_id,'ShouldbeadaptedbecauseofthefoundBoM'
                                                                            '(theselectedpickingtypeshouldbeignored)')

        mo_form=Form(self.env['mrp.production'].with_context(default_picking_type_id=warehouse03.manu_type_id.id))
        mo_form.product_id=finished_product
        self.assertFalse(mo_form.bom_id,'ShouldnotfindanyBoM,becauseofthedefinedpickingtype')
        self.assertEqual(mo_form.picking_type_id,warehouse03.manu_type_id)

        mo_form=Form(self.env['mrp.production'].with_context(default_picking_type_id=warehouse01.manu_type_id.id))
        mo_form.product_id=finished_product
        self.assertEqual(mo_form.bom_id,bom_wh01,'ShouldselecttheBoMthatmatchesthedefaultpickingtype')
        self.assertEqual(mo_form.picking_type_id,warehouse01.manu_type_id,'Shouldbethedefaultone')

        mo_form.bom_id=bom_wh02
        self.assertEqual(mo_form.picking_type_id,warehouse01.manu_type_id,'Shouldnotchange,becauseofdefaultvalue')

        mo_form.picking_type_id=warehouse02.manu_type_id
        self.assertEqual(mo_form.bom_id,bom_wh02,'Shouldnotchange')
        self.assertEqual(mo_form.picking_type_id,warehouse02.manu_type_id,'Shouldnotchange')

        mo_form.picking_type_id=warehouse02.manu_type_id
        mo_form.bom_id=bom_wh02
        self.assertEqual(mo_form.picking_type_id,warehouse01.manu_type_id,'Shouldbeadaptedbecauseofthedefaultvalue')
