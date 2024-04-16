#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
fromflectra.addons.stock.tests.commonimportTestStockCommon
fromflectra.tests.commonimportForm
fromflectra.exceptionsimportUserError


classTestStockProductionLot(TestStockCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestStockProductionLot,cls).setUpClass()
        #Createsatrackedproductusingexpirationdates.
        cls.product_apple=cls.ProductObj.create({
            'name':'Apple',
            'type':'product',
            'tracking':'lot',
            'use_expiration_date':True,
            'expiration_time':10,
            'use_time':5,
            'removal_time':8,
            'alert_time':4,
        })
        #Createsanapplelot.
        lot_form=Form(cls.LotObj)
        lot_form.name='good-apple-lot'
        lot_form.product_id=cls.product_apple
        lot_form.company_id=cls.env.company
        cls.lot_good_apple=lot_form.save()
        #Createsanexpiredapplelot.
        lot_form=Form(cls.LotObj)
        lot_form.name='expired-apple-lot-01'
        lot_form.product_id=cls.product_apple
        lot_form.company_id=cls.env.company
        cls.lot_expired_apple=lot_form.save()
        lot_form=Form(cls.lot_expired_apple) #Editsthelottomakeitexpired.
        lot_form.expiration_date=datetime.today()-timedelta(days=10)
        cls.lot_expired_apple=lot_form.save()

        #CreatesaproducibleproductanditsBOM.
        cls.product_apple_pie=cls.ProductObj.create({
            'name':'ApplePie',
            'type':'product',
        })
        cls.bom_apple_pie=cls.env['mrp.bom'].create({
            'product_id':cls.product_apple_pie.id,
            'product_tmpl_id':cls.product_apple_pie.product_tmpl_id.id,
            'product_uom_id':cls.uom_unit.id,
            'product_qty':1.0,
            'consumption':'flexible',
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':cls.product_apple.id,'product_qty':3}),
            ]})

        cls.location_stock=cls.env['stock.location'].browse(cls.stock_location)

        #Creationofarouting
        cls.workcenter=cls.env['mrp.workcenter'].create({
            'name':'Bakery',
            'capacity':2,
            'time_start':10,
            'time_stop':5,
            'time_efficiency':80,
        })

    deftest_01_product_produce(self):
        """Checksuserdoesn'tgetaconfirmationwizardwhentheyproduceswith
        noexpiredcomponents."""
        #CreatesaManufacturingOrder...
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=self.product_apple_pie
        mo_form.bom_id=self.bom_apple_pie
        mo_form.product_qty=1
        mo=mo_form.save()
        mo.action_confirm()
        #...andtriestoproductwithanon-expiredlotascomponent.
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=3
            ml.lot_id=self.lot_good_apple
        details_operation_form.save()
        res=mo.button_mark_done()
        #Producingmustnotreturnawizardinthiscase.
        self.assertEqual(res,True)

    deftest_02_product_produce_using_expired(self):
        """Checksusergetsaconfirmationwizardwhentheyproduceswith
        expiredcomponents."""
        #CreatesaManufacturingOrder...
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=self.product_apple_pie
        mo_form.bom_id=self.bom_apple_pie
        mo_form.product_qty=1
        mo=mo_form.save()
        mo.action_confirm()
        #...andtriestoproductwithanexpiredlotascomponent.
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=3
            ml.lot_id=self.lot_expired_apple
        details_operation_form.save()
        res=mo.button_mark_done()
        #Producingmustreturnaconfirmationwizard.
        self.assertNotEqual(res,None)
        self.assertEqual(res['res_model'],'expiry.picking.confirmation')

