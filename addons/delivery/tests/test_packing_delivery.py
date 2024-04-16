#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.stock.tests.test_packingimportTestPackingCommon


classTestPacking(TestPackingCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestPacking,cls).setUpClass()
        cls.uom_kg=cls.env.ref('uom.product_uom_kgm')
        cls.product_aw=cls.env['product.product'].create({
            'name':'ProductAW',
            'type':'product',
            'weight':2.4,
            'uom_id':cls.uom_kg.id,
            'uom_po_id':cls.uom_kg.id
        })
        cls.product_bw=cls.env['product.product'].create({
            'name':'ProductBW',
            'type':'product',
            'weight':0.3,
            'uom_id':cls.uom_kg.id,
            'uom_po_id':cls.uom_kg.id
        })
        test_carrier_product=cls.env['product.product'].create({
            'name':'Testcarrierproduct',
            'type':'service',
        })
        cls.test_carrier=cls.env['delivery.carrier'].create({
            'name':'Testcarrier',
            'delivery_type':'fixed',
            'product_id':test_carrier_product.id,
        })

    deftest_put_in_pack_weight_wizard(self):
        """Checkthatdedefaultweightiscorrectlysetbydefaultwhenusingthe'choose.delivery.package'wizard.
        Thispurposeofthiswizardis
        """
        self.env['stock.quant']._update_available_quantity(self.product_aw,self.stock_location,20.0)
        self.env['stock.quant']._update_available_quantity(self.product_bw,self.stock_location,20.0)

        picking_ship=self.env['stock.picking'].create({
            'partner_id':self.env['res.partner'].create({'name':'Apartner'}).id,
            'picking_type_id':self.warehouse.out_type_id.id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'carrier_id':self.test_carrier.id
        })
        move_line_paw=self.env['stock.move.line'].create({
            'product_id':self.product_aw.id,
            'product_uom_id':self.uom_kg.id,
            'picking_id':picking_ship.id,
            'qty_done':5,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id
        })
        move_line_pbw=self.env['stock.move.line'].create({
            'product_id':self.product_bw.id,
            'product_uom_id':self.uom_kg.id,
            'picking_id':picking_ship.id,
            'qty_done':5,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id
        })
        picking_ship.action_confirm()
        pack_action=picking_ship.action_put_in_pack()
        pack_action_ctx=pack_action['context']
        pack_action_model=pack_action['res_model']

        #Wemakesurethecorrectactionwasreturned
        self.assertEqual(pack_action_model,'choose.delivery.package')

        #Weinstanciatethewizardwiththecontextoftheactionandcheckthatthe
        #defaultweightwasset.
        pack_wiz=self.env['choose.delivery.package'].with_context(pack_action_ctx).create({})
        self.assertEqual(pack_wiz.shipping_weight,13.5)
