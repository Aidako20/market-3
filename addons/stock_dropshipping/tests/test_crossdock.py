#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon,Form
fromflectra.toolsimportmute_logger


classTestCrossdock(common.TransactionCase):

    deftest_00_crossdock(self):

        #Createasupplier
        supplier_crossdock=self.env['res.partner'].create({'name':"Crossdockingsupplier"})

        #Ifirstcreateawarehousewithpick-pack-shipandreceptionin2steps
        wh_pps=self.env['stock.warehouse'].create({
            'name':'WareHousePickPackShip',
            'code':'whpps',
            'reception_steps':'two_steps',
            'delivery_steps':'pick_pack_ship',
        })

        #Checkthatcross-dockrouteisactive
        self.assertTrue(wh_pps.crossdock_route_id.active,
            "Crossdockrouteshouldbeactivewhenreception_stepsisnotin'single_step'")

        p_f=Form(self.env['product.template'])
        p_f.name='PCE'
        p_f.type='product'
        p_f.categ_id=self.env.ref('product.product_category_1')
        p_f.list_price=100.0
        withp_f.seller_ids.new()asseller:
            seller.name=supplier_crossdock
        p_f.route_ids.add(wh_pps.crossdock_route_id)
        cross_shop_product=p_f.save()

        p_f.standard_price=70.0

        #Createasalesorderwithalineof100PCEincomingshipmentwithroute_idcrossdockshipping
        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        so_form.warehouse_id=wh_pps

        withmute_logger('flectra.tests.common.onchange'):
            #otherwisecomplainsthatthere'snotenoughinventoryand
            #apparentlythat'snormalaccordingto@jcoand@sle
            withso_form.order_line.new()asline:
                line.product_id=cross_shop_product.product_variant_ids
                line.product_uom_qty=100.0
            sale_order_crossdock=so_form.save()

        #Confirmsalesorder
        sale_order_crossdock.action_confirm()

        #Runthescheduler
        self.env['procurement.group'].run_scheduler()

        #Checkaquotationwascreatedforthecreatedsupplierandconfirmit
        po=self.env['purchase.order'].search([
            ('partner_id','=',supplier_crossdock.id),
            ('state','=','draft')
        ])
        self.assertTrue(po,"anRFQshouldhavebeencreatedbythescheduler")
        po.button_confirm()
