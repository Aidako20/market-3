#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime

fromflectra.tests.commonimportTransactionCase,Form
fromflectra.toolsimportmute_logger


classTestSaleMrpProcurement(TransactionCase):

    deftest_sale_mrp(self):
        self.env.ref('stock.route_warehouse0_mto').active=True
        warehouse0=self.env.ref('stock.warehouse0')
        #Inordertotestthesale_mrpmoduleinOpenERP,Istartbycreatinganewproduct'SliderMobile'
        #IdefineproductcategoryMobileProductsSellable.

        withmute_logger('flectra.tests.common.onchange'):
            #Suppresswarningon"Changingyourcostmethod"whencreatinga
            #productcategory
            pc=Form(self.env['product.category'])
        pc.name='MobileProductsSellable'
        product_category_allproductssellable0=pc.save()

        uom_unit=self.env.ref('uom.product_uom_unit')

        self.assertIn("seller_ids",self.env['product.template'].fields_get())

        #IdefineproductforSliderMobile.
        product=Form(self.env['product.template'])

        product.categ_id=product_category_allproductssellable0
        product.list_price=200.0
        product.name='SliderMobile'
        product.type='product'
        product.uom_id=uom_unit
        product.uom_po_id=uom_unit
        product.route_ids.clear()
        product.route_ids.add(warehouse0.manufacture_pull_id.route_id)
        product.route_ids.add(warehouse0.mto_pull_id.route_id)
        product_template_slidermobile0=product.save()

        product_template_slidermobile0.standard_price=189

        product_component=Form(self.env['product.product'])
        product_component.name='Battery'
        product_product_bettery=product_component.save()

        withForm(self.env['mrp.bom'])asbom:
            bom.product_tmpl_id=product_template_slidermobile0
            withbom.bom_line_ids.new()asline:
                line.product_id=product_product_bettery
                line.product_qty=4

        #IcreateasaleorderforproductSlidermobile
        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'AnotherTestPartner'})
        withso_form.order_line.new()asline:
            line.product_id=product_template_slidermobile0.product_variant_ids
            line.price_unit=200
            line.product_uom_qty=500.0
            line.customer_lead=7.0
        sale_order_so0=so_form.save()

        #Iconfirmthesaleorder
        sale_order_so0.action_confirm()

        #Iverifythatamanufacturingorderhasbeengenerated,andthatitsnameandreferencearecorrect
        mo=self.env['mrp.production'].search([('origin','like',sale_order_so0.name)],limit=1)
        self.assertTrue(mo,'Manufacturingorderhasnotbeengenerated')

        #Checkthemoisdisplayedontheso
        self.assertEqual(mo.id,sale_order_so0.action_view_mrp_production()['res_id'])

    deftest_sale_mrp_pickings(self):
        """TestsaleofmultiplemrpproductsinMTO
        toavoidgeneratingmultipledeliveries
        tothecustomerlocation
        """
        self.env.ref('stock.route_warehouse0_mto').active=True
        #Createwarehouse
        self.customer_location=self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_customers')
        self.warehouse=self.env['stock.warehouse'].create({
            'name':'TestWarehouse',
            'code':'TWH'
        })

        self.uom_unit=self.env.ref('uom.product_uom_unit')

        #Createrawproductformanufacturedproduct
        product_form=Form(self.env['product.product'])
        product_form.name='RawStick'
        product_form.type='product'
        product_form.uom_id=self.uom_unit
        product_form.uom_po_id=self.uom_unit
        self.raw_product=product_form.save()

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

        #Createmanifacturedproductwhichusesanothermanifactured
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

        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'AnotherTestPartner'})
        withso_form.order_line.new()asline:
            line.product_id=self.complex_product
            line.price_unit=1
            line.product_uom_qty=1
        withso_form.order_line.new()asline:
            line.product_id=self.finished_product
            line.price_unit=1
            line.product_uom_qty=1
        sale_order_so0=so_form.save()

        sale_order_so0.action_confirm()

        #Verifybuttonsareworkingasexpected
        self.assertEqual(sale_order_so0.mrp_production_count,2,"Usershouldseethecorrectnumberofmanufactureordersinsmartbutton")

        pickings=sale_order_so0.picking_ids

        #Onedelivery...
        self.assertEqual(len(pickings),1)

        #...withtwoproducts
        move_lines=pickings[0].move_lines
        self.assertEqual(len(move_lines),2)
