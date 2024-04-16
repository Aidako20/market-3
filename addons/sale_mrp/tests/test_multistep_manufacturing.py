#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.addons.mrp.tests.commonimportTestMrpCommon


classTestMultistepManufacturing(TestMrpCommon):

    defsetUp(self):
        super(TestMultistepManufacturing,self).setUp()

        self.env.ref('stock.route_warehouse0_mto').active=True
        self.MrpProduction=self.env['mrp.production']
        #Createwarehouse
        warehouse_form=Form(self.env['stock.warehouse'])
        warehouse_form.name='Test'
        warehouse_form.code='Test'
        self.warehouse=warehouse_form.save()

        self.uom_unit=self.env.ref('uom.product_uom_unit')

        #Createmanufacturedproduct
        product_form=Form(self.env['product.product'])
        product_form.name='Stick'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        product_form.route_ids.clear()
        product_form.route_ids.add(self.warehouse.manufacture_pull_id.route_id)
        product_form.route_ids.add(self.warehouse.mto_pull_id.route_id)
        self.product_manu=product_form.save()

        #Createrawproductformanufacturedproduct
        product_form=Form(self.env['product.product'])
        product_form.name='RawStick'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        self.product_raw=product_form.save()

        #Createbomformanufacturedproduct
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.product_manu
        bom_product_form.product_tmpl_id=self.product_manu.product_tmpl_id
        bom_product_form.product_qty=1.0
        bom_product_form.type='normal'
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.product_raw
            bom_line.product_qty=2.0
        self.bom_prod_manu=bom_product_form.save()

        #Createsaleorder
        sale_form=Form(self.env['sale.order'])
        sale_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        sale_form.picking_policy='direct'
        sale_form.warehouse_id=self.warehouse
        withsale_form.order_line.new()asline:
            line.name=self.product_manu.name
            line.product_id=self.product_manu
            line.product_uom_qty=1.0
            line.product_uom=self.uom_unit
            line.price_unit=10.0
        self.sale_order=sale_form.save()

    deftest_00_manufacturing_step_one(self):
        """TestingforStep-1"""
        #Changestepsofmanufacturing.
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='mrp_one_step'
        #Confirmsaleorder.
        self.sale_order.action_confirm()
        #Checkallprocurementsforcreatedsaleorder
        mo_procurement=self.MrpProduction.search([('origin','=',self.sale_order.name)])
        #Getmanufacturedprocurement
        self.assertEqual(mo_procurement.location_src_id.id,self.warehouse.lot_stock_id.id,"Sourceloctiondoesnotmatch.")
        self.assertEqual(mo_procurement.location_dest_id.id,self.warehouse.lot_stock_id.id,"Destinationlocationdoesnotmatch.")
        self.assertEqual(len(mo_procurement),1,"NoProcurement!")

    deftest_01_manufacturing_step_two(self):
        """TestingforStep-2"""
        withForm(self.warehouse)aswarehouse:
            warehouse.manufacture_steps='pbm'
        self.sale_order.action_confirm()
        #Getmanufacturedprocurement
        mo_procurement=self.MrpProduction.search([('origin','=',self.sale_order.name)])
        mo=self.env['mrp.production'].search([
            ('origin','=',self.sale_order.name),
            ('product_id','=',self.product_manu.id),
        ])
        self.assertEqual(self.sale_order.action_view_mrp_production()['res_id'],mo.id)
        self.assertEqual(mo_procurement.location_src_id.id,self.warehouse.pbm_loc_id.id,"Sourceloctiondoesnotmatch.")
        self.assertEqual(mo_procurement.location_dest_id.id,self.warehouse.lot_stock_id.id,"Destinationlocationdoesnotmatch.")

        self.assertEqual(len(mo_procurement),1,"NoProcurement!")

    deftest_cancel_multilevel_manufacturing(self):
        """TestingformultilevelManufacturingorders.
            Whenusercreatesmulti-levelmanufacturingorders,
            andthencancelleschildmanufacturingorder,
            anactivityshouldbegeneratedonparentMO,tonotifyuserthat
            demandsfromchildMOhasbeencancelled.
        """

        product_form=Form(self.env['product.product'])
        product_form.name='Screw'
        self.product_screw=product_form.save()

        #Addroutesformanufacturingandmaketoordertotherawmaterialproduct
        withForm(self.product_raw)asp1:
            p1.route_ids.clear()
            p1.route_ids.add(self.warehouse_1.manufacture_pull_id.route_id)
            p1.route_ids.add(self.warehouse_1.mto_pull_id.route_id)

        #NewBoMforrawmaterialproduct,itwillgenerateanotherProductionorderi.e.childProductionorder
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.product_raw
        bom_product_form.product_tmpl_id=self.product_raw.product_tmpl_id
        bom_product_form.product_qty=1.0
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.product_screw
            bom_line.product_qty=5.0
        self.bom_prod_manu=bom_product_form.save()

        #createMOfromsaleorder.
        self.sale_order.action_confirm()
        #FindchildMO.
        child_manufaturing=self.env['mrp.production'].search([('product_id','=',self.product_raw.id)])
        self.assertTrue((len(child_manufaturing.ids)==1),'Manufacturingorderofrawmaterialmustbegenerated.')
        #CancelchildMO.
        child_manufaturing.action_cancel()
        manufaturing_from_so=self.env['mrp.production'].search([('product_id','=',self.product_manu.id)])
        #CheckifactivityisgeneratedornotonparentMO.
        exception=self.env['mail.activity'].search([('res_model','=','mrp.production'),
                                                      ('res_id','=',manufaturing_from_so.id)])
        self.assertEqual(len(exception.ids),1,'Whenusercancelledchildmanufacturing,exceptionmustbegeneratedonparentmanufacturing.')
