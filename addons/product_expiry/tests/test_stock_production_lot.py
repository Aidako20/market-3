#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.stock.tests.commonimportTestStockCommon
fromflectra.tests.commonimportForm


classTestStockProductionLot(TestStockCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestStockProductionLot,cls).setUpClass()
        #Createsatrackedproductwithexpirationdates.
        cls.apple_product=cls.ProductObj.create({
            'name':'Apple',
            'type':'product',
            'tracking':'lot',
            'use_expiration_date':True,
            'expiration_time':10,
            'use_time':5,
            'removal_time':8,
            'alert_time':4,
        })

    deftest_00_stock_production_lot(self):
        """TestScheduledTaskonlotwithanalert_dateinthepastcreatesanactivity"""

        #createproduct
        self.productAAA=self.ProductObj.create({
            'name':'ProductAAA',
            'type':'product',
            'tracking':'lot',
            'company_id':self.env.company.id,
        })

        #createanewlotwithwithalertdateinthepast
        self.lot1_productAAA=self.LotObj.create({
            'name':'Lot1ProductAAA',
            'product_id':self.productAAA.id,
            'alert_date':fields.Date.to_string(datetime.today()-relativedelta(days=15)),
            'company_id':self.env.company.id,
        })

        picking_in=self.PickingObj.create({
            'picking_type_id':self.picking_type_in,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location
        })

        move_a=self.MoveObj.create({
            'name':self.productAAA.name,
            'product_id':self.productAAA.id,
            'product_uom_qty':33,
            'product_uom':self.productAAA.uom_id.id,
            'picking_id':picking_in.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location
        })
        
        self.assertEqual(picking_in.move_lines.state,'draft','Wrongstateofmoveline.')
        picking_in.action_confirm()
        self.assertEqual(picking_in.move_lines.state,'assigned','Wrongstateofmoveline.')

        #Replacepackoperationofincomingshipments.
        picking_in.action_assign()
        move_a.move_line_ids.qty_done=33
        move_a.move_line_ids.lot_id=self.lot1_productAAA.id

        #TransferIncomingShipment.
        picking_in._action_done()

        #runscheduledtasks
        self.env['stock.production.lot']._alert_date_exceeded()

        #checkanewactivityhasbeencreated
        activity_id=self.env.ref('product_expiry.mail_activity_type_alert_date_reached').id
        activity_count=self.env['mail.activity'].search_count([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productAAA.id)
        ])
        self.assertEqual(activity_count,1,'Noactivitycreatedwhilethereshouldbeone')

        #runtheschedulerasecondtime
        self.env['stock.production.lot']._alert_date_exceeded()

        #checkthereisstillonlyoneactivity,noadditionalactivityiscreatedifthereisalreadyanexistingactivity
        activity_count=self.env['mail.activity'].search_count([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productAAA.id)
        ])
        self.assertEqual(activity_count,1,'Thereshouldbeoneandonlyoneactivity')

        #marktheactivityasdone
        mail_activity=self.env['mail.activity'].search([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productAAA.id)
        ])
        mail_activity.action_done()

        #checkthereisnomoreactivity(becauseitisalreadydone)
        activity_count=self.env['mail.activity'].search_count([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productAAA.id)
        ])
        self.assertEqual(activity_count,0,"Asactivityisdone,thereshouldn'tbeanyrelatedactivity")
                
        #runtheschedulerathirdtime
        self.env['stock.production.lot']._alert_date_exceeded()

        #checkthereisnoactivitycreated
        activity_count=self.env['mail.activity'].search_count([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productAAA.id)
        ])
        self.assertEqual(activity_count,0,"Asthereisalreadyanactivitymarkedasdone,thereshouldn'tbeanyrelatedactivitycreatedforthislot")

    deftest_01_stock_production_lot(self):
        """TestScheduledTaskonlotwithanalert_dateinfuturedoesnotcreateanactivity"""

        #createproduct
        self.productBBB=self.ProductObj.create({
            'name':'ProductBBB',
            'type':'product',
            'tracking':'lot'
        })

        #createanewlotwithwithalertdateinthepast
        self.lot1_productBBB=self.LotObj.create({
            'name':'Lot1ProductBBB',
            'product_id':self.productBBB.id,
            'alert_date':fields.Date.to_string(datetime.today()+relativedelta(days=15)),
            'company_id':self.env.company.id,
        })

        picking_in=self.PickingObj.create({
            'picking_type_id':self.picking_type_in,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location})

        move_b=self.MoveObj.create({
            'name':self.productBBB.name,
            'product_id':self.productBBB.id,
            'product_uom_qty':44,
            'product_uom':self.productBBB.uom_id.id,
            'picking_id':picking_in.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location})
        
        self.assertEqual(picking_in.move_lines.state,'draft','Wrongstateofmoveline.')
        picking_in.action_confirm()
        self.assertEqual(picking_in.move_lines.state,'assigned','Wrongstateofmoveline.')

        #Replacepackoperationofincomingshipments.
        picking_in.action_assign()
        move_b.move_line_ids.qty_done=44
        move_b.move_line_ids.lot_id=self.lot1_productBBB.id

        #TransferIncomingShipment.
        picking_in._action_done()

        #runscheduledtasks
        self.env['stock.production.lot']._alert_date_exceeded()

        #checkanewactivityhasnotbeencreated
        activity_id=self.env.ref('product_expiry.mail_activity_type_alert_date_reached').id
        activity_count=self.env['mail.activity'].search_count([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productBBB.id)
        ])
        self.assertEqual(activity_count,0,"Anactivityhasbeencreatedwhileitshouldn't")

    deftest_02_stock_production_lot(self):
        """TestScheduledTaskonlotwithoutanalert_datedoesnotcreateanactivity"""

        #createproduct
        self.productCCC=self.ProductObj.create({'name':'ProductCCC','type':'product','tracking':'lot'})

        #createanewlotwithwithalertdateinthepast
        self.lot1_productCCC=self.LotObj.create({'name':'Lot1ProductCCC','product_id':self.productCCC.id,'company_id':self.env.company.id})

        picking_in=self.PickingObj.create({
            'picking_type_id':self.picking_type_in,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location})

        move_c=self.MoveObj.create({
            'name':self.productCCC.name,
            'product_id':self.productCCC.id,
            'product_uom_qty':44,
            'product_uom':self.productCCC.uom_id.id,
            'picking_id':picking_in.id,
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location})
        
        self.assertEqual(picking_in.move_lines.state,'draft','Wrongstateofmoveline.')
        picking_in.action_confirm()
        self.assertEqual(picking_in.move_lines.state,'assigned','Wrongstateofmoveline.')

        #Replacepackoperationofincomingshipments.
        picking_in.action_assign()
        move_c.move_line_ids.qty_done=55
        move_c.move_line_ids.lot_id=self.lot1_productCCC.id

        #TransferIncomingShipment.
        picking_in._action_done()

        #runscheduledtasks
        self.env['stock.production.lot']._alert_date_exceeded()

        #checkanewactivityhasnotbeencreated
        activity_id=self.env.ref('product_expiry.mail_activity_type_alert_date_reached').id
        activity_count=self.env['mail.activity'].search_count([
            ('activity_type_id','=',activity_id),
            ('res_model_id','=',self.env.ref('stock.model_stock_production_lot').id),
            ('res_id','=',self.lot1_productCCC.id)
        ])
        self.assertEqual(activity_count,0,"Anactivityhasbeencreatedwhileitshouldn't")

    deftest_03_onchange_expiration_date(self):
        """Updatesthe`expiration_date`ofthelotproductionandchecksotherdate
        fieldsareupdatedaswell."""
        #Keepstrackofthecurrentdatetimeandsetadeltaforthecompares.
        today_date=datetime.today()
        time_gap=timedelta(seconds=10)
        #Createsanewlotnumberandsavesit...
        lot_form=Form(self.LotObj)
        lot_form.name='AppleBox#1'
        lot_form.product_id=self.apple_product
        lot_form.company_id=self.env.company
        apple_lot=lot_form.save()
        #...thenchecksdatefieldshavetheexpectedvalues.
        self.assertAlmostEqual(
            today_date+timedelta(days=self.apple_product.expiration_time),
            apple_lot.expiration_date,delta=time_gap)
        self.assertAlmostEqual(
            today_date+timedelta(days=self.apple_product.use_time),
            apple_lot.use_date,delta=time_gap)
        self.assertAlmostEqual(
            today_date+timedelta(days=self.apple_product.removal_time),
            apple_lot.removal_date,delta=time_gap)
        self.assertAlmostEqual(
            today_date+timedelta(days=self.apple_product.alert_time),
            apple_lot.alert_date,delta=time_gap)

        difference=timedelta(days=20)
        new_date=apple_lot.expiration_date+difference
        old_use_date=apple_lot.use_date
        old_removal_date=apple_lot.removal_date
        old_alert_date=apple_lot.alert_date

        #Modifiesthelot`expiration_date`...
        lot_form=Form(apple_lot)
        lot_form.expiration_date=new_date
        apple_lot=lot_form.save()

        #...thenchecksallotherdatefieldswerecorrecltyupdated.
        self.assertAlmostEqual(
            apple_lot.use_date,old_use_date+difference,delta=time_gap)
        self.assertAlmostEqual(
            apple_lot.removal_date,old_removal_date+difference,delta=time_gap)
        self.assertAlmostEqual(
            apple_lot.alert_date,old_alert_date+difference,delta=time_gap)

    deftest_04_expiration_date_on_receipt(self):
        """Testwecansetanexpirationdateonreceiptandallexpiration
        datewillbecorrectlyset."""
        partner=self.env['res.partner'].create({
            'name':'Apple\'sJoe',
            'company_id':self.env.ref('base.main_company').id,
        })
        expiration_date=datetime.today()+timedelta(days=30)
        time_gap=timedelta(seconds=10)

        #Receivesatrackedproductionusingexpirationdate.
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.apple_product
            move.product_uom_qty=4
        receipt=picking_form.save()
        receipt.action_confirm()

        #Definesadateduringthereceipt.
        move_form=Form(receipt.move_ids_without_package,view="stock.view_stock_move_operations")
        withmove_form.move_line_ids.new()asline:
            line.lot_name='AppleBox#2'
            line.expiration_date=expiration_date
            line.qty_done=4
        move=move_form.save()

        receipt._action_done()
        #Getbackthelotcreatedwhenthepickingwasdone...
        apple_lot=self.env['stock.production.lot'].search(
            [('product_id','=',self.apple_product.id)],
            limit=1,
        )
        #...andchecksalldatefieldsarecorrectlyset.
        self.assertAlmostEqual(
            apple_lot.expiration_date,expiration_date,delta=time_gap)
        self.assertAlmostEqual(
            apple_lot.use_date,expiration_date-timedelta(days=5),delta=time_gap)
        self.assertAlmostEqual(
            apple_lot.removal_date,expiration_date-timedelta(days=2),delta=time_gap)
        self.assertAlmostEqual(
            apple_lot.alert_date,expiration_date-timedelta(days=6),delta=time_gap)

    deftest_04_2_expiration_date_on_receipt(self):
        """Testwecansetanexpirationdateonreceiptevenifallexpiration
        daterelatedfieldsaren'tsetonproduct."""
        partner=self.env['res.partner'].create({
            'name':'Apple\'sJoe',
            'company_id':self.env.ref('base.main_company').id,
        })
        #Unsetsomefields.
        self.apple_product.expiration_time=False
        self.apple_product.removal_time=False

        expiration_date=datetime.today()+timedelta(days=30)
        time_gap=timedelta(seconds=10)

        #Receivesatrackedproductionusingexpirationdate.
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_in')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.apple_product
            move.product_uom_qty=4
        receipt=picking_form.save()
        receipt.action_confirm()

        #Definesadateduringthereceipt.
        move=receipt.move_ids_without_package[0]
        line=move.move_line_ids[0]
        self.assertEqual(move.use_expiration_date,True)
        line.lot_name='AppleBox#3'
        line.expiration_date=expiration_date
        line.qty_done=4

        receipt._action_done()
        #Getbackthelotcreatedwhenthepickingwasdone...
        apple_lot=self.env['stock.production.lot'].search(
            [('product_id','=',self.apple_product.id)],
            limit=1,
        )
        #...andchecksalldatefieldsarecorrectlyset.
        self.assertAlmostEqual(
            apple_lot.expiration_date,expiration_date,delta=time_gap,
            msg="Mustbedefineeveniftheproduct's`expiration_time`isn'tset.")
        self.assertAlmostEqual(
            apple_lot.use_date,expiration_date+timedelta(days=5),delta=time_gap)
        self.assertAlmostEqual(
            apple_lot.removal_date,expiration_date+timedelta(days=self.apple_product.removal_time),delta=time_gap,
            msg="`removal_date`shouldalwaysbecalculatedwhenanexpirationdateisdefined")
        self.assertAlmostEqual(
            apple_lot.alert_date,expiration_date+timedelta(days=4),delta=time_gap)

    deftest_05_confirmation_on_delivery(self):
        """Testwhenusertriestodeliveryexpiredlot,he/shegetsa
        confirmationwizard."""
        partner=self.env['res.partner'].create({
            'name':'Cider&Son',
            'company_id':self.env.ref('base.main_company').id,
        })
        #Creates3lots(1non-expiredlot,2expiredlots)
        lot_form=Form(self.LotObj) #Createsthelot.
        lot_form.name='good-apple-lot'
        lot_form.product_id=self.apple_product
        lot_form.company_id=self.env.company
        good_lot=lot_form.save()

        lot_form=Form(self.LotObj) #Createsthelot.
        lot_form.name='expired-apple-lot-01'
        lot_form.product_id=self.apple_product
        lot_form.company_id=self.env.company
        expired_lot_1=lot_form.save()
        lot_form=Form(expired_lot_1) #Editsthelottomakeitexpired.
        lot_form.expiration_date=datetime.today()-timedelta(days=10)
        expired_lot_1=lot_form.save()

        #Case#1:makeadeliverywithnoexpiredlot.
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.apple_product
            move.product_uom_qty=4
        #Savesandconfirmsit...
        delivery_1=picking_form.save()
        delivery_1.action_confirm()
        #...thencreateamovelinewiththenon-expiredlotandvalidsthepicking.
        delivery_1.move_line_ids_without_package=[(5,0),(0,0,{
            'company_id':self.env.company.id,
            'location_id':delivery_1.move_lines.location_id.id,
            'location_dest_id':delivery_1.move_lines.location_dest_id.id,
            'lot_id':good_lot.id,
            'product_id':self.apple_product.id,
            'product_uom_id':self.apple_product.uom_id.id,
            'qty_done':4,
        })]
        res=delivery_1.button_validate()
        #Validateadeliveryforgoodproductsmustnotraiseanything.
        self.assertEqual(res,True)

        #Case#2:makeadeliverywithonenon-expiredlotandoneexpiredlot.
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.apple_product
            move.product_uom_qty=8
        #Savesandconfirmsit...
        delivery_2=picking_form.save()
        delivery_2.action_confirm()
        #...thencreateamovelineforthenon-expiredlotandforanexpired
        #lotandvalidsthepicking.
        delivery_2.move_line_ids_without_package=[(5,0),(0,0,{
            'company_id':self.env.company.id,
            'location_id':delivery_2.move_lines.location_id.id,
            'location_dest_id':delivery_2.move_lines.location_dest_id.id,
            'lot_id':good_lot.id,
            'product_id':self.apple_product.id,
            'product_uom_id':self.apple_product.uom_id.id,
            'qty_done':4,
        }),(0,0,{
            'company_id':self.env.company.id,
            'location_id':delivery_2.move_lines.location_id.id,
            'location_dest_id':delivery_2.move_lines.location_dest_id.id,
            'lot_id':expired_lot_1.id,
            'product_id':self.apple_product.id,
            'product_uom_id':self.apple_product.uom_id.id,
            'qty_done':4,
        })]
        res=delivery_2.button_validate()
        #Validateadeliverycontainingexpiredproductsmustraiseaconfirmationwizard.
        self.assertNotEqual(res,True)
        self.assertEqual(res['res_model'],'expiry.picking.confirmation')

        #Case#3:makeadeliverywithonlyonexpiredlot.
        picking_form=Form(self.env['stock.picking'])
        picking_form.partner_id=partner
        picking_form.picking_type_id=self.env.ref('stock.picking_type_out')
        withpicking_form.move_ids_without_package.new()asmove:
            move.product_id=self.apple_product
            move.product_uom_qty=4
        #Savesandconfirmsit...
        delivery_3=picking_form.save()
        delivery_3.action_confirm()
        #...thencreatetwomovelineswithexpiredlotandvalidsthepicking.
        delivery_3.move_line_ids_without_package=[(5,0),(0,0,{
            'company_id':self.env.company.id,
            'location_id':delivery_3.move_lines.location_id.id,
            'location_dest_id':delivery_3.move_lines.location_dest_id.id,
            'lot_id':expired_lot_1.id,
            'product_id':self.apple_product.id,
            'product_uom_id':self.apple_product.uom_id.id,
            'qty_done':4,
        })]
        res=delivery_3.button_validate()
        #Validateadeliverycontainingexpiredproductsmustraiseaconfirmationwizard.
        self.assertNotEqual(res,True)
        self.assertEqual(res['res_model'],'expiry.picking.confirmation')

    deftest_edit_removal_date_in_inventory_mode(self):
        """Trytoeditremoval_datewiththeinventorymode.
        """
        user_group_stock_manager=self.env.ref('stock.group_stock_manager')
        self.demo_user=mail_new_test_user(
            self.env,
            name='Demouser',
            login='userdemo',
            email='d.d@example.com',
            groups='stock.group_stock_manager',
        )
        lot_form=Form(self.LotObj)
        lot_form.name='LOT001'
        lot_form.product_id=self.apple_product
        lot_form.company_id=self.env.company
        apple_lot=lot_form.save()

        quant=self.StockQuantObj.with_context(inventory_mode=True).create({
            'product_id':self.apple_product.id,
            'location_id':self.stock_location,
            'quantity':10,
            'lot_id':apple_lot.id,
        })
        #Trytowriteonquantwithinventorymode
        new_date=datetime.today()+timedelta(days=15)
        quant.with_user(self.demo_user).with_context(inventory_mode=True).write({'removal_date':new_date})
        self.assertEqual(quant.removal_date,new_date)

    deftest_apply_lot_date_on_sml(self):
        """
        WhenassigningalottoaSML,ifthelothasanexpirationdate,
        thelattershouldbeappliedontheSML
        """
        exp_date=fields.Datetime.today()+relativedelta(days=15)

        lot=self.env['stock.production.lot'].create({
            'name':'Lot1',
            'product_id':self.apple_product.id,
            'expiration_date':fields.Datetime.to_string(exp_date),
            'company_id':self.env.company.id,
        })

        sml=self.env['stock.move.line'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'product_id':self.apple_product.id,
            'qty_done':3,
            'product_uom_id':self.apple_product.uom_id.id,
            'lot_id':lot.id,
            'company_id':self.env.company.id,
        })

        self.assertEqual(sml.expiration_date,exp_date)

        exp_date=exp_date+relativedelta(days=10)
        lot.expiration_date=exp_date
        self.assertEqual(sml.expiration_date,exp_date)

    deftest_apply_lot_without_date_on_sml(self):
        """
        WhenassigningalottoaSML,ifthelothasnoexpirationdate,
        datesonlotandSMLshouldbecorrectlyset
        """
        #createlotwithoutexpirationdate
        lot=self.env['stock.production.lot'].create({
            'name':'Lot1',
            'product_id':self.apple_product.id,
            'company_id':self.env.company.id,
        })

        sml=self.env['stock.move.line'].create({
            'location_id':self.supplier_location,
            'location_dest_id':self.stock_location,
            'product_id':self.apple_product.id,
            'qty_done':3,
            'product_uom_id':self.apple_product.uom_id.id,
            'lot_id':lot.id,
            'company_id':self.env.company.id,
        })
        today_date=datetime.today()
        time_gap=timedelta(seconds=10)
        exp_date=today_date+timedelta(days=self.apple_product.expiration_time)

        self.assertAlmostEqual(sml.expiration_date,exp_date,delta=time_gap)

        self.assertAlmostEqual(
            lot.expiration_date,exp_date,delta=time_gap)
        self.assertAlmostEqual(
            lot.use_date,today_date+timedelta(days=self.apple_product.use_time),delta=time_gap)
        self.assertAlmostEqual(
            lot.removal_date,today_date+timedelta(days=self.apple_product.removal_time),delta=time_gap)
        self.assertAlmostEqual(
            lot.alert_date,today_date+timedelta(days=self.apple_product.alert_time),delta=time_gap)
