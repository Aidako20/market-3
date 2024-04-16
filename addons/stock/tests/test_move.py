#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError
fromflectra.testsimportForm
fromflectra.tests.commonimportSavepointCase


classStockMove(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super(StockMove,cls).setUpClass()
        cls.stock_location=cls.env.ref('stock.stock_location_stock')
        cls.customer_location=cls.env.ref('stock.stock_location_customers')
        cls.supplier_location=cls.env.ref('stock.stock_location_suppliers')
        cls.pack_location=cls.env.ref('stock.location_pack_zone')
        cls.pack_location.active=True
        cls.transit_location=cls.env['stock.location'].search([
            ('company_id','=',cls.env.company.id),
            ('usage','=','transit'),
            ('active','=',False)
        ],limit=1)
        cls.transit_location.active=True
        cls.uom_unit=cls.env.ref('uom.product_uom_unit')
        cls.uom_dozen=cls.env.ref('uom.product_uom_dozen')
        cls.product=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.product_serial=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'tracking':'serial',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.product_lot=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'tracking':'lot',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.product_consu=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'consu',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })

    defgather_relevant(self,product_id,location_id,lot_id=None,package_id=None,owner_id=None,strict=False):
        quants=self.env['stock.quant']._gather(product_id,location_id,lot_id=lot_id,package_id=package_id,owner_id=owner_id,strict=strict)
        returnquants.filtered(lambdaq:not(q.quantity==0andq.reserved_quantity==0))

    deftest_in_1(self):
        """Receiveproductsfromasupplier.Checkthatamovelineiscreatedandthatthe
        receptioncorrectlyincreaseasinglequantinstock.
        """
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #fillthemoveline
        move_line=move1.move_line_ids[0]
        self.assertEqual(move_line.product_qty,100.0)
        self.assertEqual(move_line.qty_done,0.0)
        move_line.qty_done=100.0

        #validation
        move1._action_done()
        self.assertEqual(move1.state,'done')
        #noquantsarecreatedinthesupplierlocation
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.supplier_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.supplier_location,allow_negative=True),-100.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),100.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.supplier_location)),1.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

    deftest_in_2(self):
        """Receive5trackedproductsfromasupplier.Thecreatemovelineshouldhave5
        reserved.Ifiassignthe5itemstolot1,thereservationshouldnotchange.Once
        ivalidate,thereceptioncorrectlyincreaseasinglequantinstock.
        """
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        move_line=move1.move_line_ids[0]
        self.assertEqual(move_line.product_qty,5)
        move_line.lot_name='lot1'
        move_line.qty_done=5.0
        self.assertEqual(move_line.product_qty,5) #don'tchangereservation

        move1._action_done()
        self.assertEqual(move_line.product_qty,0) #changereservationto0fordonemove
        self.assertEqual(move1.state,'done')

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.supplier_location),0.0)
        supplier_quants=self.gather_relevant(self.product_lot,self.supplier_location)
        self.assertEqual(sum(supplier_quants.mapped('quantity')),-5.0)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location),5.0)
        self.assertEqual(len(self.gather_relevant(self.product_lot,self.supplier_location)),1.0)
        quants=self.gather_relevant(self.product_lot,self.stock_location)
        self.assertEqual(len(quants),1.0)
        forquantinquants:
            self.assertNotEqual(quant.in_date,False)

    deftest_in_3(self):
        """Receive5serial-trackedproductsfromasupplier.Thesystemshouldcreate5different
        moveline.
        """
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),5)
        move_line=move1.move_line_ids[0]
        self.assertEqual(move1.reserved_availability,5)

        i=0
        formove_lineinmove1.move_line_ids:
            move_line.lot_name='sn%s'%i
            move_line.qty_done=1
            i+=1
        self.assertEqual(move1.quantity_done,5.0)
        self.assertEqual(move1.product_qty,5) #don'tchangereservation

        move1._action_done()

        self.assertEqual(move1.quantity_done,5.0)
        self.assertEqual(move1.product_qty,5) #don'tchangereservation
        self.assertEqual(move1.state,'done')

        #Quantbalanceshouldresultwith5quantinsupplierandstock
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.supplier_location),0.0)
        supplier_quants=self.gather_relevant(self.product_serial,self.supplier_location)
        self.assertEqual(sum(supplier_quants.mapped('quantity')),-5.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),5.0)

        self.assertEqual(len(self.gather_relevant(self.product_serial,self.supplier_location)),5.0)
        quants=self.gather_relevant(self.product_serial,self.stock_location)
        self.assertEqual(len(quants),5.0)
        forquantinquants:
            self.assertNotEqual(quant.in_date,False)

    deftest_out_1(self):
        """Sendproductstoaclient.Checkthatamovelineiscreatedreservingproductsin
        stockandthatthedeliverycorrectlyremovethesinglequantinstock.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,100)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),100.0)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_out_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        #Shouldbeareservedquantityandthusaquant.
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

        #fillthemoveline
        move_line=move1.move_line_ids[0]
        self.assertEqual(move_line.product_qty,100.0)
        self.assertEqual(move_line.qty_done,0.0)
        move_line.qty_done=100.0

        #validation
        move1._action_done()
        self.assertEqual(move1.state,'done')
        #Checkthereisonequantincustomerlocation
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.customer_location),100.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.customer_location)),1.0)
        #thereshouldbenoquantamymoreinthestocklocation
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)

    deftest_out_2(self):
        """Sendaconsumableproducttoaclient.Checkthatamovelineiscreatedbut
            quantsarenotimpacted.
        """
        #makesomestock

        self.product.type='consu'
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_out_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        #Shouldbeareservedquantityandthusaquant.
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)

        #fillthemoveline
        move_line=move1.move_line_ids[0]
        self.assertEqual(move_line.product_qty,100.0)
        self.assertEqual(move_line.qty_done,0.0)
        move_line.qty_done=100.0

        #validation
        move1._action_done()
        self.assertEqual(move1.state,'done')
        #noquantsarecreatedinthecustomerlocationsinceit'saconsumable
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.customer_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.customer_location)),0.0)
        #thereshouldbenoquantamymoreinthestocklocation
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)

    deftest_mixed_tracking_reservation_1(self):
        """Sendproductstrackedbylottoacustomer.Inyourstock,therearetrackedand
        untrackedquants.Twomoveslinesshouldbecreated:oneforthetrackedones,another
        fortheuntrackedones.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,2)
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,3,lot_id=lot1)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location),5.0)
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(len(move1.move_line_ids),2)

    deftest_mixed_tracking_reservation_2(self):
        """Sendproductstrackedbylottoacustomer.Inyourstock,therearetwotrackedand
        mulitpleuntrackedquants.Thereshouldbeasmanymovelinesastherearequants
        reserved.Editthereservemovelinestosetthemtonewserialnumbers,thereservation
        shouldstay.Validateandthefinalquantityinstockshouldbe0,notnegative.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,2)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),4.0)
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':4.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(len(move1.move_line_ids),4)
        formlinmove1.move_line_ids:
            self.assertEqual(ml.product_qty,1.0)

        #assignlot3andlot4tobothuntrackedmovelines
        lot3=self.env['stock.production.lot'].create({
            'name':'lot3',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot4=self.env['stock.production.lot'].create({
            'name':'lot4',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        untracked_move_line=move1.move_line_ids.filtered(lambdaml:notml.lot_id)
        untracked_move_line[0].lot_id=lot3
        untracked_move_line[1].lot_id=lot4
        formlinmove1.move_line_ids:
            self.assertEqual(ml.product_qty,1.0)

        #nochangesonquants,evenifimadesomemovelineswithalotidwhomreservedonuntrackedquants
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location,strict=True)),1.0) #withaqtyof2
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location,lot_id=lot1,strict=True).filtered(lambdaq:q.lot_id)),1.0)
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location,lot_id=lot2,strict=True).filtered(lambdaq:q.lot_id)),1.0)
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location,lot_id=lot3,strict=True).filtered(lambdaq:q.lot_id)),0)
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location,lot_id=lot4,strict=True).filtered(lambdaq:q.lot_id)),0)

        move1.move_line_ids.write({'qty_done':1.0})

        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot2,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot3,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot4,strict=True),0.0)

    deftest_mixed_tracking_reservation_3(self):
        """Sendtwoproductstrackedbylottoacustomer.Inyourstock,theretwotrackedquants
        andtwountracked.Oncethemoveisvalidated,addmovelinestoalsomovethetwountracked
        onesandassignthemserialnumbersonthefly.Thefinalquantityinstockshouldbe0,not
        negative.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot2)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),2.0)
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.write({'qty_done':1.0})
        move1._action_done()

        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,2)
        lot3=self.env['stock.production.lot'].create({
            'name':'lot3',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot4=self.env['stock.production.lot'].create({
            'name':'lot4',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.move.line'].create({
            'move_id':move1.id,
            'product_id':move1.product_id.id,
            'qty_done':1,
            'product_uom_id':move1.product_uom.id,
            'location_id':move1.location_id.id,
            'location_dest_id':move1.location_dest_id.id,
            'lot_id':lot3.id,
        })
        self.env['stock.move.line'].create({
            'move_id':move1.id,
            'product_id':move1.product_id.id,
            'qty_done':1,
            'product_uom_id':move1.product_uom.id,
            'location_id':move1.location_id.id,
            'location_dest_id':move1.location_dest_id.id,
            'lot_id':lot4.id
        })

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot2,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot3,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot4,strict=True),0.0)

    deftest_mixed_tracking_reservation_4(self):
        """Sendtwoproductstrackedbylottoacustomer.Inyourstock,theretwotrackedquants
        andonuntracked.Oncethemoveisvalidated,editoneofthedonemovelinetochangethe
        serialnumbertoonethatisnotinstock.Theoriginalserialshouldgobacktostockand
        theuntrackedquantshouldbetrackedontheflyandsentinstead.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot2)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),2.0)
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.write({'qty_done':1.0})
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot2,strict=True),0.0)

        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1)
        lot3=self.env['stock.production.lot'].create({
            'name':'lot3',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })

        move1.move_line_ids[1].lot_id=lot3

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot2,strict=True),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot3,strict=True),0.0)

    deftest_mixed_tracking_reservation_5(self):
        move1=self.env['stock.move'].create({
            'name':'test_jenaimarre_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'confirmed')

        #createanuntrackedquant
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0)
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })

        #createanewmovelinewithalotnotassignedtoanyquant
        self.env['stock.move.line'].create({
            'move_id':move1.id,
            'product_id':move1.product_id.id,
            'qty_done':1,
            'product_uom_id':move1.product_uom.id,
            'location_id':move1.location_id.id,
            'location_dest_id':move1.location_dest_id.id,
            'lot_id':lot1.id
        })
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.reserved_availability,0)

        #validatingthemovelineshouldmovethelot,notcreateanegativequantinstock
        move1._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location)),0.0)

    deftest_mixed_tracking_reservation_6(self):
        #createanuntrackedquant
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0)
        move1=self.env['stock.move'].create({
            'name':'test_jenaimarre_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')

        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })

        move_line=move1.move_line_ids
        move_line.lot_id=lot1
        self.assertEqual(move_line.product_qty,1.0)
        move_line.lot_id=lot2
        self.assertEqual(move_line.product_qty,1.0)
        move_line.qty_done=1

        #validatingthemovelineshouldmovethelot,notcreateanegativequantinstock
        move1._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.stock_location)),0.0)

    deftest_mixed_tracking_reservation_7(self):
        """Similartest_mixed_tracking_reservation_2butcreatesfirstthetrackedquant,thenthe
        untrackedones.Whenaddingalottotheuntrackedmoveline,itshouldnotdecreasethe
        untrackedquantthenincreaseanon-existingtrackedonethatwillfallbackonthe
        untrackedquant.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),2.0)
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(len(move1.move_line_ids),2)
        formlinmove1.move_line_ids:
            self.assertEqual(ml.product_qty,1.0)

        untracked_move_line=move1.move_line_ids.filtered(lambdaml:notml.lot_id).lot_id=lot2
        formlinmove1.move_line_ids:
            self.assertEqual(ml.product_qty,1.0)

        move1.move_line_ids.write({'qty_done':1.0})

        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot2,strict=True),0.0)
        quants=self.gather_relevant(self.product_serial,self.stock_location)
        self.assertEqual(len(quants),0)

    deftest_mixed_tracking_reservation_8(self):
        """Sendoneproducttrackedbylottoacustomer.Inyourstock,thereareonetrackedand
        oneuntrackedquant.Reservethemove,theneditthelottoonenotpresentinstock.The
        systemwillupdatethereservationandusetheuntrackedquant.Nowunreserve,noerror
        shouldhappen
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })

        #atfirst,weonlymakethetrackedquantavailableinstocktomakesurethisoneisselected
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1,lot_id=lot1)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_mixed_tracking_reservation_7',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(move1.move_line_ids.lot_id.id,lot1.id)

        #changethelot_idtoonenotavailableinstockwhileanuntrackedquantisavailable
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1)
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        move1.move_line_ids.lot_id=lot2
        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(move1.move_line_ids.lot_id.id,lot2.id)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),1.0)

        #unreserve
        move1._do_unreserve()

        self.assertEqual(move1.reserved_availability,0.0)
        self.assertEqual(len(move1.move_line_ids),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,strict=True),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1,strict=True),2.0)

    deftest_putaway_1(self):
        """Receiveproductsfromasupplier.Checkthatputawayrulesarerightlyappliedon
        thereceiptmoveline.
        """
        #Thistestwillapplyaputawaystrategyonthestocklocationtoputeverything
        #incominginthesublocationshelf1.
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        #putawayfromstocktoshelf1
        putaway=self.env['stock.putaway.rule'].create({
            'category_id':self.env.ref('product.product_category_all').id,
            'location_in_id':self.stock_location.id,
            'location_out_id':shelf1_location.id,
        })
        self.stock_location.write({
            'putaway_rule_ids':[(4,putaway.id,0)]
        })

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf1_location.id)

    deftest_putaway_2(self):
        """Receiveproductsfromasupplier.Checkthatputawayrulesarerightlyappliedon
        thereceiptmoveline.
        """
        #Thistestwillapplyaputawaystrategybyproductonthestocklocationtoputeverything
        #incominginthesublocationshelf1.
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        #putawayfromstocktoshelf1
        putaway=self.env['stock.putaway.rule'].create({
            'product_id':self.product.id,
            'location_in_id':self.stock_location.id,
            'location_out_id':shelf1_location.id,
        })
        self.stock_location.write({
            'putaway_rule_ids':[(4,putaway.id,0)],
        })

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_2',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf1_location.id)

    deftest_putaway_3(self):
        """Receiveproductsfromasupplier.Checkthatputawayrulesarerightlyappliedon
        thereceiptmoveline.
        """
        #Thistestwillapplyboththeputawaystrategybyproductandcategory.Wecheckhere
        #thattheputawaybyproducttakesprecedence.

        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf2',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        putaway_category=self.env['stock.putaway.rule'].create({
            'category_id':self.env.ref('product.product_category_all').id,
            'location_in_id':self.supplier_location.id,
            'location_out_id':shelf1_location.id,
        })
        putaway_product=self.env['stock.putaway.rule'].create({
            'product_id':self.product.id,
            'location_in_id':self.supplier_location.id,
            'location_out_id':shelf2_location.id,
        })
        self.stock_location.write({
            'putaway_rule_ids':[(6,0,[
                putaway_category.id,
                putaway_product.id
            ])],
        })

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_3',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf2_location.id)

    deftest_putaway_4(self):
        """Receiveproductsfromasupplier.Checkthatputawayrulesarerightlyappliedon
        thereceiptmoveline.
        """
        #Thistestwillapplyboththeputawaystrategybyproductandcategory.Wecheckhere
        #thatifaputawaybyproductisnotmatched,thefallbacktothecategoryiscorrectly
        #done.

        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf2',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        #putawayfromstocktoshelf1
        putaway_category=self.env['stock.putaway.rule'].create({
            'category_id':self.env.ref('product.product_category_all').id,
            'location_in_id':self.stock_location.id,
            'location_out_id':shelf1_location.id,
        })
        putaway_product=self.env['stock.putaway.rule'].create({
            'product_id':self.product_consu.id,
            'location_in_id':self.stock_location.id,
            'location_out_id':shelf2_location.id,
        })
        self.stock_location.write({
            'putaway_rule_ids':[(6,0,[
                putaway_category.id,
                putaway_product.id,
            ])],
        })

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_4',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf1_location.id)

    deftest_putaway_5(self):
        """Receiveproductsfromasupplier.Checkthatputawayrulesarerightlyappliedon
        thereceiptmoveline.
        """
        #Thistestwillapplyputawaystrategybycategory.
        #Wecheckherethattheputawaybycategoryworkswhenthecategoryis
        #setonparentcategoryoftheproduct.

        shelf_location=self.env['stock.location'].create({
            'name':'shelf',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        putaway=self.env['stock.putaway.rule'].create({
            'category_id':self.env.ref('product.product_category_all').id,
            'location_in_id':self.supplier_location.id,
            'location_out_id':shelf_location.id,
        })
        self.stock_location.write({
            'putaway_rule_ids':[(6,0,[
                putaway.id,
            ])],
        })
        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_5',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf_location.id)

    deftest_putaway_6(self):
        """Receiveproductsfromasupplier.Checkthatputawayrulesarerightlyappliedon
        thereceiptmoveline.
        """
        #Thistestwillapplytwoputawaystrategiesbycategory.Wecheckhere
        #thatthemostspecificputawaytakesprecedence.

        child_category=self.env['product.category'].create({
            'name':'child_category',
            'parent_id':self.ref('product.product_category_all'),
        })
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf2',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        putaway_category_all=self.env['stock.putaway.rule'].create({
            'category_id':self.env.ref('product.product_category_all').id,
            'location_in_id':self.supplier_location.id,
            'location_out_id':shelf1_location.id,
        })
        putaway_category_office_furn=self.env['stock.putaway.rule'].create({
            'category_id':child_category.id,
            'location_in_id':self.supplier_location.id,
            'location_out_id':shelf2_location.id,
        })
        self.stock_location.write({
            'putaway_rule_ids':[(6,0,[
                putaway_category_all.id,
                putaway_category_office_furn.id,
            ])],
        })
        self.product.categ_id=child_category

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_6',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf2_location.id)

    deftest_putaway_7(self):
        """Checksparentslocationsarealsobrowsedwhenlookingforputaways.

        WH/Stock>WH/Stock/Floor1>WH/Stock/Floor1/Rack1>WH/Stock/Floor1/Rack1/Shelf2
        TheputawayisonFloor1tosendtoShelf2
        AmovefromsuppliertoRack1shouldsendtoshelf2
        """
        floor1=self.env['stock.location'].create({
            'name':'floor1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        rack1=self.env['stock.location'].create({
            'name':'rack1',
            'usage':'internal',
            'location_id':floor1.id,
        })
        shelf2=self.env['stock.location'].create({
            'name':'shelf2',
            'usage':'internal',
            'location_id':rack1.id,
        })

        #putawayfloor1->shelf2
        putaway=self.env['stock.putaway.rule'].create({
            'product_id':self.product.id,
            'location_in_id':floor1.id,
            'location_out_id':shelf2.id,
        })
        floor1.write({
            'putaway_rule_ids':[(4,putaway.id,0)],
        })

        #stockmovesupplier->rack1
        move1=self.env['stock.move'].create({
            'name':'test_putaway_6',
            'location_id':self.supplier_location.id,
            'location_dest_id':rack1.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        #checkiftheputawaywasrightlyapplied
        self.assertEqual(move1.move_line_ids.location_dest_id.id,shelf2.id)

    deftest_availability_1(self):
        """Checkthatthe`availability`fieldonamoveiscorrectlycomputedwhenthereis
        morethanenoughproductsinstock.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,150.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_putaway_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.supplier_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),150.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)
        self.assertEqual(move1.availability,100.0)

    deftest_availability_2(self):
        """Checkthatthe`availability`fieldonamoveiscorrectlycomputedwhenthereis
        notenoughproductsinstock.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,50.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_putaway_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.supplier_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),50.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)
        self.assertEqual(move1.availability,50.0)

    deftest_availability_3(self):
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,-1.0,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot2)
        move1=self.env['stock.move'].create({
            'name':'test_availability_3',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(move1.reserved_availability,1.0)

    deftest_availability_4(self):
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,30.0)
        move1=self.env['stock.move'].create({
            'name':'test_availability_4',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')

        move2=self.env['stock.move'].create({
            'name':'test_availability_4',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move2._action_confirm()
        move2._action_assign()

        #set15asquantitydoneforthefirstand30asthesecond
        move1.move_line_ids.qty_done=15
        move2.move_line_ids.qty_done=30

        #validatethesecond,thefirstshouldbeunreserved
        move2._action_done()

        self.assertEqual(move1.state,'confirmed')
        self.assertEqual(move1.move_line_ids.qty_done,15)
        self.assertEqual(move2.state,'done')

        stock_quants=self.gather_relevant(self.product,self.stock_location)
        self.assertEqual(len(stock_quants),0)
        customer_quants=self.gather_relevant(self.product,self.customer_location)
        self.assertEqual(customer_quants.quantity,30)
        self.assertEqual(customer_quants.reserved_quantity,0)

    deftest_availability_5(self):
        """Checkthatrerunactionassignonlycreatenewstockmove
        linesinsteadofaddingquantityinexistingone.
        """
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,2.0)
        #movefromshelf1
        move=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':4.0,
        })
        move._action_confirm()
        move._action_assign()

        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,4.0)
        move._action_assign()

        self.assertEqual(len(move.move_line_ids),4.0)

    deftest_availability_6(self):
        """Checkthat,inthescenariowhereamoveisinabiggeruomthantheuomofthequants
        andthisuomonlyallowsentirenumbers,wedon'tmakeapartialreservationwhenthe
        quantityavailableisnotenoughtoreservethemove.Checkalsothatitisnotpossible
        toset`quantity_done`withavaluenothonouringtheUOM'srounding.
        """
        #onthedozenuom,settheroundingset1.0
        self.uom_dozen.rounding=1

        #6unitsareavailableinstock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,6.0)

        #themoveshouldnotbereserved
        move=self.env['stock.move'].create({
            'name':'test_availability_6',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1,
        })
        move._action_confirm()
        move._action_assign()
        self.assertEqual(move.state,'confirmed')

        #thequantsshouldbeleftuntouched
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),6.0)

        #make8unitsavailable,themoveshouldagainnotbereservabale
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0)
        move._action_assign()
        self.assertEqual(move.state,'confirmed')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),8.0)

        #make12unitsavailable,thistimethemoveshouldbereservable
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,4.0)
        move._action_assign()
        self.assertEqual(move.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        #Checkitisn'tpossibletosetanyvaluetoquantity_done
        withself.assertRaises(UserError):
            move.quantity_done=0.1
            move._action_done()

        withself.assertRaises(UserError):
            move.quantity_done=1.1
            move._action_done()

        withself.assertRaises(UserError):
            move.quantity_done=0.9
            move._action_done()

        move.quantity_done=1
        move._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.customer_location),12.0)

    deftest_availability_7(self):
        """Checkthat,inthescenariowhereamoveisinabiggeruomthantheuomofthequants
        andthisuomonlyallowsentirenumbers,weonlyreservequantityhonouringtheuom's
        roundingevenifthequantityissetacrossmultiplequants.
        """
        #onthedozenuom,settheroundingset1.0
        self.uom_dozen.rounding=1

        #make12quantsof1
        foriinrange(1,13):
            lot_id=self.env['stock.production.lot'].create({
                'name':'lot%s'%str(i),
                'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
            })
            self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot_id)

        #themoveshouldbereserved
        move=self.env['stock.move'].create({
            'name':'test_availability_7',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1,
        })
        move._action_confirm()
        move._action_assign()
        self.assertEqual(move.state,'assigned')
        self.assertEqual(len(move.move_line_ids.mapped('product_uom_id')),1)
        self.assertEqual(move.move_line_ids.mapped('product_uom_id'),self.uom_unit)

        formove_lineinmove.move_line_ids:
            move_line.qty_done=1
        move._action_done()

        self.assertEqual(move.product_uom_qty,1)
        self.assertEqual(move.product_uom.id,self.uom_dozen.id)
        self.assertEqual(move.state,'done')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.customer_location),12.0)
        self.assertEqual(len(self.gather_relevant(self.product_serial,self.customer_location)),12)

    deftest_availability_8(self):
        """Testtheassignmentmechanismwhentheproductquantityisdecreasedonapartially
            reservedstockmove.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,3.0)
        self.assertAlmostEqual(self.product.qty_available,3.0)

        move_partial=self.env['stock.move'].create({
            'name':'test_partial',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })

        move_partial._action_confirm()
        move_partial._action_assign()
        self.assertAlmostEqual(self.product.virtual_available,-2.0)
        self.assertEqual(move_partial.state,'partially_available')
        move_partial.product_uom_qty=3.0
        move_partial._action_assign()
        self.assertEqual(move_partial.state,'assigned')

    deftest_availability_9(self):
        """Testtheassignmentmechanismwhentheproductquantityisincrease
        onareceiptmove.
        """
        move_receipt=self.env['stock.move'].create({
            'name':'test_receipt_edit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
        })

        move_receipt._action_confirm()
        move_receipt._action_assign()
        self.assertEqual(move_receipt.state,'assigned')
        move_receipt.product_uom_qty=3.0
        move_receipt._action_assign()
        self.assertEqual(move_receipt.state,'assigned')
        self.assertEqual(move_receipt.move_line_ids.product_uom_qty,3)

    deftest_unreserve_1(self):
        """Checkthatunreservingastockmovesetstheproductsreservedasavailableand
        setthestatebacktoconfirmed.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,150.0)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.supplier_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),150.0)
        self.assertEqual(move1.availability,100.0)

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),50.0)

        #unreserve
        move1._do_unreserve()
        self.assertEqual(len(move1.move_line_ids),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),150.0)
        self.assertEqual(move1.state,'confirmed')

    deftest_unreserve_2(self):
        """Checkthatunreservingastockmovesetstheproductsreservedasavailableand
        setthestatebacktoconfirmedeveniftheyareinapack.
        """
        package1=self.env['stock.quant.package'].create({'name':'test_unreserve_2_pack'})

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,150.0,package_id=package1)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_putaway_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.supplier_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100.0,
        })

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),150.0)
        self.assertEqual(move1.availability,100.0)

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),50.0)

        #unreserve
        move1._do_unreserve()
        self.assertEqual(len(move1.move_line_ids),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),150.0)
        self.assertEqual(move1.state,'confirmed')

    deftest_unreserve_3(self):
        """Similarto`test_unreserve_1`butcheckingthequantsmoreindetails.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_out_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        quants=self.gather_relevant(self.product,self.stock_location)
        self.assertEqual(len(quants),1.0)
        self.assertEqual(quants.quantity,2.0)
        self.assertEqual(quants.reserved_quantity,2.0)

        move1._do_unreserve()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(len(quants),1.0)
        self.assertEqual(quants.quantity,2.0)
        self.assertEqual(quants.reserved_quantity,0.0)
        self.assertEqual(len(move1.move_line_ids),0.0)

    deftest_unreserve_4(self):
        """Checktheunreservationofapartiallyavailablestockmove.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_out_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'partially_available')
        self.assertEqual(len(move1.move_line_ids),1)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        quants=self.gather_relevant(self.product,self.stock_location)
        self.assertEqual(len(quants),1.0)
        self.assertEqual(quants.quantity,2.0)
        self.assertEqual(quants.reserved_quantity,2.0)

        move1._do_unreserve()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(len(quants),1.0)
        self.assertEqual(quants.quantity,2.0)
        self.assertEqual(quants.reserved_quantity,0.0)
        self.assertEqual(len(move1.move_line_ids),0.0)

    deftest_unreserve_5(self):
        """Checktheunreservationofastockmovereservedonmultiplequants.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,3)
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':2,
        })
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),5)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_unreserve_5',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        move1._do_unreserve()

        quants=self.gather_relevant(self.product,self.stock_location)
        self.assertEqual(len(quants),2.0)
        forquantinquants:
            self.assertEqual(quant.reserved_quantity,0)

    deftest_unreserve_6(self):
        """Inasituationwithanegativeandapositivequant,reserveandunreserve.
        """
        q1=self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':-10,
            'reserved_quantity':0,
        })

        q2=self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':30.0,
            'reserved_quantity':10.0,
        })

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)

        move1=self.env['stock.move'].create({
            'name':'test_unreserve_6',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        self.assertEqual(move1.move_line_ids.product_qty,10)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(q2.reserved_quantity,20)

        move1._do_unreserve()
        self.assertEqual(move1.state,'confirmed')
        self.assertEqual(len(move1.move_line_ids),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)
        self.assertEqual(q2.reserved_quantity,10)

    deftest_unreserve_7(self):
        """Checktheunreservationofastockmovedeleteonlystockmovelines
        withoutquantitydone.
        """
        product=self.env['product.product'].create({
            'name':'product',
            'tracking':'serial',
            'type':'product',
        })

        serial_numbers=self.env['stock.production.lot'].create([{
            'name':str(x),
            'product_id':product.id,
            'company_id':self.env.company.id,
        }forxinrange(5)])

        forserialinserial_numbers:
            self.env['stock.quant'].create({
                'product_id':product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
                'lot_id':serial.id,
                'reserved_quantity':0.0,
            })

        move1=self.env['stock.move'].create({
            'name':'test_unreserve_7',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':5.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),5)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(product,self.stock_location),0.0)

        #Checkstateischangedevenwith0movelinesunlinked
        move1.move_line_ids.write({'qty_done':1})
        move1._do_unreserve()
        self.assertEqual(len(move1.move_line_ids),5)
        self.assertEqual(move1.state,'confirmed')
        move1._action_assign()
        #setaquantitydoneonthetwofirstmovelines
        move1.move_line_ids.write({'qty_done':0})
        move1.move_line_ids[0].qty_done=1
        move1.move_line_ids[1].qty_done=1

        move1._do_unreserve()
        self.assertEqual(move1.state,'confirmed')
        self.assertEqual(len(move1.move_line_ids),2)
        self.assertEqual(move1.move_line_ids.mapped('qty_done'),[1,1])
        self.assertEqual(move1.move_line_ids.mapped('product_uom_qty'),[0,0])

    deftest_link_assign_1(self):
        """Testtheassignmentmechanismwhentwochainedstockmovestrytomoveoneunitofan
        untrackedproduct.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_1_2',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})

        (move_stock_pack+move_pack_cust)._action_confirm()
        move_stock_pack._action_assign()
        move_stock_pack.move_line_ids[0].qty_done=1.0
        move_stock_pack._action_done()
        self.assertEqual(len(move_pack_cust.move_line_ids),1)
        move_line=move_pack_cust.move_line_ids[0]
        self.assertEqual(move_line.location_id.id,self.pack_location.id)
        self.assertEqual(move_line.location_dest_id.id,self.customer_location.id)
        self.assertEqual(move_pack_cust.state,'assigned')

    deftest_link_assign_2(self):
        """Testtheassignmentmechanismwhentwochainedstockmovestrytomoveoneunitofa
        trackedproduct.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot1)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location,lot1)),1.0)

        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_2_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_2_2',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})

        (move_stock_pack+move_pack_cust)._action_confirm()
        move_stock_pack._action_assign()

        move_line_stock_pack=move_stock_pack.move_line_ids[0]
        self.assertEqual(move_line_stock_pack.lot_id.id,lot1.id)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location,lot1)),1.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.pack_location,lot1)),0.0)

        move_line_stock_pack.qty_done=1.0
        move_stock_pack._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location,lot1)),0.0)

        move_line_pack_cust=move_pack_cust.move_line_ids[0]
        self.assertEqual(move_line_pack_cust.lot_id.id,lot1.id)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.pack_location,lot_id=lot1),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.pack_location,lot1)),1.0)

    deftest_link_assign_3(self):
        """Testtheassignmentmechanismwhenthreechainedstockmoves(2sources,1dest)tryto
        movemultipleunitsofanuntrackedproduct.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

        move_stock_pack_1=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_stock_pack_2=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_1_2',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move_stock_pack_1.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_stock_pack_2.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack_1.id,0),(4,move_stock_pack_2.id,0)]})

        (move_stock_pack_1+move_stock_pack_2+move_pack_cust)._action_confirm()

        #assignandfulfillthefirstmove
        move_stock_pack_1._action_assign()
        self.assertEqual(move_stock_pack_1.state,'assigned')
        self.assertEqual(len(move_stock_pack_1.move_line_ids),1)
        move_stock_pack_1.move_line_ids[0].qty_done=1.0
        move_stock_pack_1._action_done()
        self.assertEqual(move_stock_pack_1.state,'done')

        #thedestinationmoveshouldbepartiallyavailableandhaveonemoveline
        self.assertEqual(move_pack_cust.state,'partially_available')
        self.assertEqual(len(move_pack_cust.move_line_ids),1)
        #Shouldhave1quantinstock_locationandanotherinpack_location
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.pack_location)),1.0)

        move_stock_pack_2._action_assign()
        self.assertEqual(move_stock_pack_2.state,'assigned')
        self.assertEqual(len(move_stock_pack_2.move_line_ids),1)
        move_stock_pack_2.move_line_ids[0].qty_done=1.0
        move_stock_pack_2._action_done()
        self.assertEqual(move_stock_pack_2.state,'done')

        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.pack_location)),1.0)

        self.assertEqual(move_pack_cust.state,'assigned')
        self.assertEqual(len(move_pack_cust.move_line_ids),1)
        move_line_1=move_pack_cust.move_line_ids[0]
        self.assertEqual(move_line_1.location_id.id,self.pack_location.id)
        self.assertEqual(move_line_1.location_dest_id.id,self.customer_location.id)
        self.assertEqual(move_line_1.product_qty,2.0)
        self.assertEqual(move_pack_cust.state,'assigned')

    deftest_link_assign_4(self):
        """Testtheassignmentmechanismwhenthreechainedstockmoves(2sources,1dest)tryto
        movemultipleunitsofatrackedbylotproduct.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0,lot_id=lot1)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location,lot1)),1.0)

        move_stock_pack_1=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_stock_pack_2=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_1_2',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move_stock_pack_1.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_stock_pack_2.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack_1.id,0),(4,move_stock_pack_2.id,0)]})

        (move_stock_pack_1+move_stock_pack_2+move_pack_cust)._action_confirm()

        #assignandfulfillthefirstmove
        move_stock_pack_1._action_assign()
        self.assertEqual(len(move_stock_pack_1.move_line_ids),1)
        self.assertEqual(move_stock_pack_1.move_line_ids[0].lot_id.id,lot1.id)
        move_stock_pack_1.move_line_ids[0].qty_done=1.0
        move_stock_pack_1._action_done()

        #thedestinationmoveshouldbepartiallyavailableandhaveonemoveline
        self.assertEqual(len(move_pack_cust.move_line_ids),1)

        move_stock_pack_2._action_assign()
        self.assertEqual(len(move_stock_pack_2.move_line_ids),1)
        self.assertEqual(move_stock_pack_2.move_line_ids[0].lot_id.id,lot1.id)
        move_stock_pack_2.move_line_ids[0].qty_done=1.0
        move_stock_pack_2._action_done()

        self.assertEqual(len(move_pack_cust.move_line_ids),1)
        move_line_1=move_pack_cust.move_line_ids[0]
        self.assertEqual(move_line_1.location_id.id,self.pack_location.id)
        self.assertEqual(move_line_1.location_dest_id.id,self.customer_location.id)
        self.assertEqual(move_line_1.product_qty,2.0)
        self.assertEqual(move_line_1.lot_id.id,lot1.id)
        self.assertEqual(move_pack_cust.state,'assigned')

    deftest_link_assign_5(self):
        """Testtheassignmentmechanismwhenthreechainedstockmoves(1sources,2dest)tryto
        movemultipleunitsofanuntrackedproduct.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0)

        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move_pack_cust_1=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_pack_cust_2=self.env['stock.move'].create({
            'name':'test_link_assign_1_2',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust_1.id,0),(4,move_pack_cust_2.id,0)]})
        move_pack_cust_1.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})
        move_pack_cust_2.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})

        (move_stock_pack+move_pack_cust_1+move_pack_cust_2)._action_confirm()

        #assignandfulfillthefirstmove
        move_stock_pack._action_assign()
        self.assertEqual(len(move_stock_pack.move_line_ids),1)
        move_stock_pack.move_line_ids[0].qty_done=2.0
        move_stock_pack._action_done()

        #thedestinationmovesshouldbeavailableandhaveonemoveline
        self.assertEqual(len(move_pack_cust_1.move_line_ids),1)
        self.assertEqual(len(move_pack_cust_2.move_line_ids),1)

        move_pack_cust_1.move_line_ids[0].qty_done=1.0
        move_pack_cust_2.move_line_ids[0].qty_done=1.0
        (move_pack_cust_1+move_pack_cust_2)._action_done()

    deftest_link_assign_6(self):
        """Testtheassignmentmechanismwhenfourchainedstockmoves(2sources,2dest)tryto
        movemultipleunitsofanuntrackedbylotproduct.Thisparticulartestcasesimulatesatwo
        stepreceiptswithbackorder.
        """
        move_supp_stock_1=self.env['stock.move'].create({
            'name':'test_link_assign_6_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
        })
        move_supp_stock_2=self.env['stock.move'].create({
            'name':'test_link_assign_6_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move_stock_stock_1=self.env['stock.move'].create({
            'name':'test_link_assign_6_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
        })
        move_stock_stock_1.write({'move_orig_ids':[(4,move_supp_stock_1.id,0),(4,move_supp_stock_2.id,0)]})
        move_stock_stock_2=self.env['stock.move'].create({
            'name':'test_link_assign_6_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
        })
        move_stock_stock_2.write({'move_orig_ids':[(4,move_supp_stock_1.id,0),(4,move_supp_stock_2.id,0)]})

        (move_supp_stock_1+move_supp_stock_2+move_stock_stock_1+move_stock_stock_2)._action_confirm()
        move_supp_stock_1._action_assign()
        self.assertEqual(move_supp_stock_1.state,'assigned')
        self.assertEqual(move_supp_stock_2.state,'assigned')
        self.assertEqual(move_stock_stock_1.state,'waiting')
        self.assertEqual(move_stock_stock_2.state,'waiting')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        #dothefistmove,it'llbring3unitsinstocklocationsoonly`move_stock_stock_1`
        #shouldbeassigned
        move_supp_stock_1.move_line_ids.qty_done=3.0
        move_supp_stock_1._action_done()
        self.assertEqual(move_supp_stock_1.state,'done')
        self.assertEqual(move_supp_stock_2.state,'assigned')
        self.assertEqual(move_stock_stock_1.state,'assigned')
        self.assertEqual(move_stock_stock_2.state,'waiting')

    deftest_link_assign_7(self):
        #onthedozenuom,settheroundingset1.0
        self.uom_dozen.rounding=1

        #6unitsareavailableinstock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,6.0)

        #createpickingsandmovesforapick->packmtoscenario
        picking_stock_pack=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_internal').id,
        })
        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_assign_7',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
            'picking_id':picking_stock_pack.id,
        })
        picking_pack_cust=self.env['stock.picking'].create({
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_7',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
            'picking_id':picking_pack_cust.id,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})
        (move_stock_pack+move_pack_cust)._action_confirm()

        #thepickshouldnotbereservablebecauseoftheroundingofthedozen
        move_stock_pack._action_assign()
        self.assertEqual(move_stock_pack.state,'confirmed')
        move_pack_cust._action_assign()
        self.assertEqual(move_pack_cust.state,'waiting')

        #movethe6unitsbyaddinganunreservedmoveline
        move_stock_pack.write({'move_line_ids':[(0,0,{
            'product_id':self.product.id,
            'product_uom_id':self.uom_unit.id,
            'qty_done':6,
            'product_uom_qty':0,
            'lot_id':False,
            'package_id':False,
            'result_package_id':False,
            'location_id':move_stock_pack.location_id.id,
            'location_dest_id':move_stock_pack.location_dest_id.id,
            'picking_id':picking_stock_pack.id,
        })]})

        #thequantitydoneonthemoveshouldnotrespecttheroundingofthemoveline
        self.assertEqual(move_stock_pack.quantity_done,0.5)

        #createthebackorderintheuomofthequants
        backorder_wizard_dict=picking_stock_pack.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()
        self.assertEqual(move_stock_pack.state,'done')
        self.assertEqual(move_stock_pack.quantity_done,0.5)
        self.assertEqual(move_stock_pack.product_uom_qty,0.5)

        #thesecondmoveshouldnotbereservablebecauseoftheroundingonthedozen
        move_pack_cust._action_assign()
        self.assertEqual(move_pack_cust.state,'partially_available')
        move_line_pack_cust=move_pack_cust.move_line_ids
        self.assertEqual(move_line_pack_cust.product_uom_qty,6)
        self.assertEqual(move_line_pack_cust.product_uom_id.id,self.uom_unit.id)

        #moveadozenonthebackordertoseehowwehandletheextramove
        backorder=self.env['stock.picking'].search([('backorder_id','=',picking_stock_pack.id)])
        backorder.move_lines.write({'move_line_ids':[(0,0,{
            'product_id':self.product.id,
            'product_uom_id':self.uom_dozen.id,
            'qty_done':1,
            'product_uom_qty':0,
            'lot_id':False,
            'package_id':False,
            'result_package_id':False,
            'location_id':backorder.location_id.id,
            'location_dest_id':backorder.location_dest_id.id,
            'picking_id':backorder.id,
        })]})
        backorder.button_validate()
        backorder_move=backorder.move_lines
        self.assertEqual(backorder_move.state,'done')
        self.assertEqual(backorder_move.quantity_done,12.0)
        self.assertEqual(backorder_move.product_uom_qty,12.0)
        self.assertEqual(backorder_move.product_uom,self.uom_unit)

        #thesecondmoveshouldnowbereservable
        move_pack_cust._action_assign()
        self.assertEqual(move_pack_cust.state,'assigned')
        self.assertEqual(move_line_pack_cust.product_uom_qty,12)
        self.assertEqual(move_line_pack_cust.product_uom_id.id,self.uom_unit.id)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,move_stock_pack.location_dest_id),6)

    deftest_link_assign_8(self):
        """Settheroundingofthedozento1.0,createachainoftwomoveforadozen,theproduct
        concernedistrackedbyserialnumber.Checkthattheflowisok.
        """
        #onthedozenuom,settheroundingset1.0
        self.uom_dozen.rounding=1

        #6unitsareavailableinstock
        foriinrange(1,13):
            lot_id=self.env['stock.production.lot'].create({
                'name':'lot%s'%str(i),
                'product_id':self.product_serial.id,
                'company_id':self.env.company.id,
            })
            self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot_id)

        #createpickingsandmovesforapick->packmtoscenario
        picking_stock_pack=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_internal').id,
        })
        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_assign_7',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
            'picking_id':picking_stock_pack.id,
        })
        picking_pack_cust=self.env['stock.picking'].create({
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_7',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
            'picking_id':picking_pack_cust.id,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})
        (move_stock_pack+move_pack_cust)._action_confirm()

        move_stock_pack._action_assign()
        self.assertEqual(move_stock_pack.state,'assigned')
        move_pack_cust._action_assign()
        self.assertEqual(move_pack_cust.state,'waiting')

        formlinmove_stock_pack.move_line_ids:
            ml.qty_done=1
        picking_stock_pack.button_validate()
        self.assertEqual(move_pack_cust.state,'assigned')
        formlinmove_pack_cust.move_line_ids:
            self.assertEqual(ml.product_uom_qty,1)
            self.assertEqual(ml.product_uom_id.id,self.uom_unit.id)
            self.assertTrue(bool(ml.lot_id.id))

    deftest_link_assign_9(self):
        """Createanuom"3units"whichis3timestheunitsbutwithoutrounding.Create3
        quantsinstockandtwochainedmoves.Thefirstmovewillbringthe3quantsbutthe
        secondonlyvalidate2andcreateabackorderforthelastone.Checkthatthereservation
        iscorrectlyclearedupforthelastone.
        """
        uom_3units=self.env['uom.uom'].create({
            'name':'3units',
            'category_id':self.uom_unit.category_id.id,
            'factor_inv':3,
            'rounding':1,
            'uom_type':'bigger',
        })
        foriinrange(1,4):
            lot_id=self.env['stock.production.lot'].create({
                'name':'lot%s'%str(i),
                'product_id':self.product_serial.id,
                'company_id':self.env.company.id,
            })
            self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot_id)

        picking_stock_pack=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_internal').id,
        })
        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_assign_9',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product_serial.id,
            'product_uom':uom_3units.id,
            'product_uom_qty':1.0,
            'picking_id':picking_stock_pack.id,
        })
        picking_pack_cust=self.env['stock.picking'].create({
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_0',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_serial.id,
            'product_uom':uom_3units.id,
            'product_uom_qty':1.0,
            'picking_id':picking_pack_cust.id,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})
        (move_stock_pack+move_pack_cust)._action_confirm()

        picking_stock_pack.action_assign()
        formlinpicking_stock_pack.move_lines.move_line_ids:
            ml.qty_done=1
        picking_stock_pack.button_validate()
        self.assertEqual(picking_pack_cust.state,'assigned')
        formlinpicking_pack_cust.move_lines.move_line_ids:
            ifml.lot_id.name!='lot3':
                ml.qty_done=1
        res_dict_for_back_order=picking_pack_cust.button_validate()
        backorder_wizard=self.env[(res_dict_for_back_order.get('res_model'))].browse(res_dict_for_back_order.get('res_id')).with_context(res_dict_for_back_order['context'])
        backorder_wizard.process()
        backorder=self.env['stock.picking'].search([('backorder_id','=',picking_pack_cust.id)])
        backordered_move=backorder.move_lines

        #duetotherounding,thebackorderedquantityis0.999;weshoudln'tbeabletoreserve
        #0.999onatrackedbyserialnumberquant
        backordered_move._action_assign()
        self.assertEqual(backordered_move.reserved_availability,0)

        #forcetheserialnumberandvalidate
        lot3=self.env['stock.production.lot'].search([('name','=',"lot3")])
        backorder.write({'move_line_ids':[(0,0,{
            'product_id':self.product_serial.id,
            'product_uom_id':self.uom_unit.id,
            'qty_done':1,
            'product_uom_qty':0,
            'lot_id':lot3.id,
            'package_id':False,
            'result_package_id':False,
            'location_id':backordered_move.location_id.id,
            'location_dest_id':backordered_move.location_dest_id.id,
            'move_id':backordered_move.id,
        })]})

        backorder.button_validate()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.customer_location),3)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.pack_location),0)

    deftest_link_assign_10(self):
        """Testtheassignmentmechanismwithpartialavailability.
        """
        #makesomestock:
        #  stocklocation:2.0
        #  packlocation:-1.0
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1.0)

        move_out=self.env['stock.move'].create({
            'name':'test_link_assign_out',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move_out._action_confirm()
        move_out._action_assign()
        move_out.quantity_done=1.0
        move_out._action_done()
        self.assertEqual(len(self.gather_relevant(self.product,self.pack_location)),1.0)

        move_stock_pack=self.env['stock.move'].create({
            'name':'test_link_assign_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move_pack_cust=self.env['stock.move'].create({
            'name':'test_link_assign_1_2',
            'location_id':self.pack_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move_stock_pack.write({'move_dest_ids':[(4,move_pack_cust.id,0)]})
        move_pack_cust.write({'move_orig_ids':[(4,move_stock_pack.id,0)]})

        (move_stock_pack+move_pack_cust)._action_confirm()
        move_stock_pack._action_assign()
        move_stock_pack.quantity_done=2.0
        move_stock_pack._action_done()
        self.assertEqual(len(move_pack_cust.move_line_ids),1)

        self.assertAlmostEqual(move_pack_cust.reserved_availability,1.0)
        self.assertEqual(move_pack_cust.state,'partially_available')

    deftest_use_reserved_move_line_1(self):
        """Testthat_free_reservationworkwhenquantityisonlyavailableon
        reservedmovelines.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,10.0)
        move1=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        move2=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move2._action_confirm()
        move2._action_assign()
        move3=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':0.0,
            'quantity_done':1.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3._action_done()
        self.assertEqual(move3.state,'done')
        quant=self.env['stock.quant']._gather(self.product,self.stock_location)
        self.assertEqual(quant.quantity,9.0)
        self.assertEqual(quant.reserved_quantity,9.0)

    deftest_use_reserved_move_line_2(self):
        #make12unitsavailableinstock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,12.0)

        #reserve12units
        move1=self.env['stock.move'].create({
            'name':'test_use_reserved_move_line_2_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        quant=self.env['stock.quant']._gather(self.product,self.stock_location)
        self.assertEqual(quant.quantity,12)
        self.assertEqual(quant.reserved_quantity,12)

        #forceamoveof1dozen
        move2=self.env['stock.move'].create({
            'name':'test_use_reserved_move_line_2_2',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1,
        })
        move2._action_confirm()
        move2._action_assign()
        self.assertEqual(move2.state,'confirmed')
        move2._set_quantity_done(1)
        move2._action_done()

        #mov1shouldbeunreservedandthequantshouldbeunlinked
        self.assertEqual(move1.state,'confirmed')
        quant=self.env['stock.quant']._gather(self.product,self.stock_location)
        self.assertEqual(quant.quantity,0)
        self.assertEqual(quant.reserved_quantity,0)

    deftest_use_unreserved_move_line_1(self):
        """Testthatvalidatingastockmovelinkedtoanuntrackedproductreservedbyanotherone
        correctlyunreservestheotherone.
        """
        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)

        #preparetheconflictingmove
        move1=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move2=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })

        #reservethosemove
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        move2._action_confirm()
        move2._action_assign()
        self.assertEqual(move2.state,'confirmed')

        #usetheproductfromthefirstone
        move2.write({'move_line_ids':[(0,0,{
            'product_id':self.product.id,
            'product_uom_id':self.uom_unit.id,
            'qty_done':1,
            'product_uom_qty':0,
            'lot_id':False,
            'package_id':False,
            'result_package_id':False,
            'location_id':move2.location_id.id,
            'location_dest_id':move2.location_dest_id.id,
        })]})
        move2._action_done()

        #thefirstmoveshouldgobacktoconfirmed
        self.assertEqual(move1.state,'confirmed')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

    deftest_use_unreserved_move_line_2(self):
        """Testthatvalidatingastockmovelinkedtoatrackedproductreservedbyanotherone
        correctlyunreservestheotherone.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })

        #makesomestock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot1)

        #preparetheconflictingmove
        move1=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move2=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_1_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })

        #reservethosemove
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),1.0)
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        move2._action_confirm()
        move2._action_assign()
        self.assertEqual(move2.state,'confirmed')

        #usetheproductfromthefirstone
        move2.write({'move_line_ids':[(0,0,{
            'product_id':self.product.id,
            'product_uom_id':self.uom_unit.id,
            'qty_done':1,
            'product_uom_qty':0,
            'lot_id':lot1.id,
            'package_id':False,
            'result_package_id':False,
            'location_id':move2.location_id.id,
            'location_dest_id':move2.location_dest_id.id,
        })]})
        move2._action_done()

        #thefirstmoveshouldgobacktoconfirmed
        self.assertEqual(move1.state,'confirmed')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),0.0)

    deftest_use_unreserved_move_line_3(self):
        """Testthebehaviorof`_free_reservation`whenranonarecordsetofmovelineswhere
        someareassignedandsomeareforceassigned.`_free_reservation`shouldnotusean
        alreadyprocessedmovelinewhenlookingforamovelinecandidatetounreserve.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)

        move1=self.env['stock.move'].create({
            'name':'test_use_unreserved_move_line_3',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.quantity_done=1

        #addaforcedmovelinein`move1`
        move1.write({'move_line_ids':[(0,0,{
            'product_id':self.product.id,
            'product_uom_id':self.uom_unit.id,
            'qty_done':2,
            'product_uom_qty':0,
            'lot_id':False,
            'package_id':False,
            'result_package_id':False,
            'location_id':move1.location_id.id,
            'location_dest_id':move1.location_dest_id.id,
        })]})
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.customer_location),3.0)

    deftest_use_unreserved_move_line_4(self):
        product_01=self.env['product.product'].create({
            'name':'Product01',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        product_02=self.env['product.product'].create({
            'name':'Product02',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        self.env['stock.quant']._update_available_quantity(product_01,self.stock_location,1)
        self.env['stock.quant']._update_available_quantity(product_02,self.stock_location,1)

        customer=self.env['res.partner'].create({'name':'SuperPartner'})
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':customer.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })

        p01_move=self.env['stock.move'].create({
            'name':'SuperMove01',
            'location_id':picking.location_id.id,
            'location_dest_id':picking.location_dest_id.id,
            'picking_id':picking.id,
            'product_id':product_01.id,
            'product_uom_qty':1,
            'product_uom':product_01.uom_id.id,
        })
        p02_move=self.env['stock.move'].create({
            'name':'SuperMove02',
            'location_id':picking.location_id.id,
            'location_dest_id':picking.location_dest_id.id,
            'picking_id':picking.id,
            'product_id':product_02.id,
            'product_uom_qty':1,
            'product_uom':product_02.uom_id.id,
        })

        picking.action_confirm()
        picking.action_assign()
        p01_move.product_uom_qty=0
        picking.do_unreserve()
        picking.action_assign()
        p01_move.product_uom_qty=1
        self.assertEqual(p01_move.state,'confirmed')

    deftest_edit_reserved_move_line_1(self):
        """Testthateditingastockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthereservation.Inthiscase,weeditthesublocationwherewetakethe
        producttoanothersublocationwhereaproductisavailable.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.env['stock.quant']._update_available_quantity(self.product,shelf2_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

        move1.move_line_ids.location_id=shelf2_location.id

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_edit_reserved_move_line_2(self):
        """Testthateditingastockmovelinelinkedtoatrackedproductcorrectlyanddirectly
        adaptsthereservation.Inthiscase,weeditthelottoanotheravailableone.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)

        move1.move_line_ids.lot_id=lot2.id

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),0.0)

    deftest_edit_reserved_move_line_3(self):
        """Testthateditingastockmovelinelinkedtoapackedproductcorrectlyanddirectly
        adaptsthereservation.Inthiscase,weeditthepackagetoanotheravailableone.
        """
        package1=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_3'})
        package2=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_3'})

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,package_id=package1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,package_id=package2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package2),1.0)

        move1.move_line_ids.package_id=package2.id

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package2),0.0)

    deftest_edit_reserved_move_line_4(self):
        """Testthateditingastockmovelinelinkedtoanownedproductcorrectlyanddirectly
        adaptsthereservation.Inthiscase,weedittheownertoanotheravailableone.
        """
        owner1=self.env['res.partner'].create({'name':'test_edit_reserved_move_line_4_1'})
        owner2=self.env['res.partner'].create({'name':'test_edit_reserved_move_line_4_2'})

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,owner_id=owner1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,owner_id=owner2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner2),1.0)

        move1.move_line_ids.owner_id=owner2.id

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner2),0.0)

    deftest_edit_reserved_move_line_5(self):
        """Testthateditingastockmovelinelinkedtoapackedandtrackedproductcorrectly
        anddirectlyadaptsthereservation.Inthiscase,weeditthelottoanotheravailableone
        thatisnotinapack.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        package1=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_5'})

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot1,package_id=package1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1,package_id=package1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)
        move_line=move1.move_line_ids[0]
        move_line.write({'package_id':False,'lot_id':lot2.id})

        self.assertEqual(move1.reserved_availability,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),0.0)

    deftest_edit_reserved_move_line_6(self):
        """Testthateditingastockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthereservation.Inthiscase,weeditthesublocationwherewetakethe
        producttoanothersublocationwhereaproductisNOTavailable.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()

        self.assertEqual(move1.move_line_ids.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        move1.move_line_ids.location_id=shelf2_location.id

        self.assertEqual(move1.move_line_ids.state,'confirmed')
        self.assertEqual(move1.reserved_availability,0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)

    deftest_edit_reserved_move_line_7(self):
        """Send5trackedproductstoaclient,buttheseproductsdonothaveanylotsetinour
        inventoryyet:weonlysetthematdeliverytime.Thecreatedmovelineshouldhave5items
        withoutanylotset,ifweedittosetthemtolot1,thereservationshouldnotchange.
        Validatingthestockmoveshouldshouldnotcreateanegativequantforthislotinstock
        location.
        #"""
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        #makesomestockwithoutassigningalotid
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,5)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)
        move_line=move1.move_line_ids[0]
        self.assertEqual(move_line.product_qty,5)
        move_line.qty_done=5.0
        self.assertEqual(move_line.product_qty,5) #don'tchangereservation
        move_line.lot_id=lot1
        self.assertEqual(move_line.product_qty,5) #don'tchangereservationwhenassgningalotnow

        move1._action_done()
        self.assertEqual(move_line.product_qty,0) #changereservationto0fordonemove
        self.assertEqual(move1.state,'done')

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_lot,self.stock_location)),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_lot,self.stock_location,lot_id=lot1,strict=True)),0.0)

    deftest_edit_reserved_move_line_8(self):
        """Send5trackedproductstoaclient,butsomeoftheseproductsdonothaveanylotset
        inourinventoryyet:weonlysetthematdeliverytime.Addingalot_idonthemoveline
        thatdoesnothaveanyshouldnotchangeitsreservation,andvalidatingshouldnotcreate
        anegativequantforthislotinstock.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        #makesomestockwithoutassigningalotid
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,3)
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,2,lot_id=lot1)

        #creation
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        self.assertEqual(move1.state,'draft')

        #confirmation
        move1._action_confirm()
        self.assertEqual(move1.state,'confirmed')

        #assignment
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),2)

        tracked_move_line=None
        untracked_move_line=None
        formove_lineinmove1.move_line_ids:
            ifmove_line.lot_id:
                tracked_move_line=move_line
            else:
                untracked_move_line=move_line

        self.assertEqual(tracked_move_line.product_qty,2)
        tracked_move_line.qty_done=2

        self.assertEqual(untracked_move_line.product_qty,3)
        untracked_move_line.lot_id=lot2
        self.assertEqual(untracked_move_line.product_qty,3) #don'tchangereservation
        untracked_move_line.qty_done=3
        self.assertEqual(untracked_move_line.product_qty,3) #don'tchangereservation

        move1._action_done()
        self.assertEqual(untracked_move_line.product_qty,0) #changereservationto0fordonemove
        self.assertEqual(tracked_move_line.product_qty,0) #changereservationto0fordonemove
        self.assertEqual(move1.state,'done')

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1,strict=True),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot2,strict=True),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_lot,self.stock_location)),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_lot,self.stock_location,lot_id=lot1,strict=True)),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_lot,self.stock_location,lot_id=lot2,strict=True)),0.0)

    deftest_edit_reserved_move_line_9(self):
        """
        WhenwritingonthereservedquantityontheSML,aprocesstriesto
        reservethequantswiththatnewquantity.Ifitfails(forinstance
        becausethewrittenquantityismorethanactuallyavailable),this
        quantityshouldberesetto0.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)

        out_move=self.env['stock.move'].create({
            'name':self.product.name,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom_qty':1,
            'product_uom':self.product.uom_id.id,
        })
        out_move._action_confirm()
        out_move._action_assign()

        #trytomanuallyassignmorethanavailable
        out_move.move_line_ids.product_uom_qty=2

        self.assertTrue(out_move.move_line_ids)
        self.assertEqual(out_move.move_line_ids.product_uom_qty,0,"Thereservedquantityshouldbecancelled")

    deftest_edit_done_move_line_1(self):
        """Testthateditingadonestockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthetransfer.Inthiscase,weeditthesublocationwherewetakethe
        producttoanothersublocationwhereaproductisavailable.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.env['stock.quant']._update_available_quantity(self.product,shelf2_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)

        #movefromshelf1
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

        #editoncedone,weactuallymovedfromshelf2
        move1.move_line_ids.location_id=shelf2_location.id

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_edit_done_move_line_2(self):
        """Testthateditingadonestockmovelinelinkedtoatrackedproductcorrectlyanddirectly
        adaptsthetransfer.Inthiscase,weeditthelottoanotheravailableone.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)

        move1.move_line_ids.lot_id=lot2.id

        #reserved_availabilityshouldalwaysbeen0fordonemove.
        self.assertEqual(move1.reserved_availability,0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),0.0)

    deftest_edit_done_move_line_3(self):
        """Testthateditingadonestockmovelinelinkedtoapackedproductcorrectlyanddirectly
        adaptsthetransfer.Inthiscase,weeditthepackagetoanotheravailableone.
        """
        package1=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_3'})
        package2=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_3'})

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,package_id=package1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,package_id=package2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package2),1.0)

        move1.move_line_ids.package_id=package2.id

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,package_id=package2),0.0)

    deftest_edit_done_move_line_4(self):
        """Testthateditingadonestockmovelinelinkedtoanownedproductcorrectlyanddirectly
        adaptsthetransfer.Inthiscase,weedittheownertoanotheravailableone.
        """
        owner1=self.env['res.partner'].create({'name':'test_edit_reserved_move_line_4_1'})
        owner2=self.env['res.partner'].create({'name':'test_edit_reserved_move_line_4_2'})

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,owner_id=owner1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,owner_id=owner2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner2),1.0)

        move1.move_line_ids.owner_id=owner2.id

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,owner_id=owner2),0.0)

    deftest_edit_done_move_line_5(self):
        """Testthateditingadonestockmovelinelinkedtoapackedandtrackedproductcorrectly
        anddirectlyadaptsthetransfer.Inthiscase,weeditthelottoanotheravailableone
        thatisnotinapack.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product.id,
            'company_id':self.env.company.id,
        })
        package1=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_5'})

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot1,package_id=package1)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0,lot_id=lot2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1,package_id=package1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),1.0)
        move_line=move1.move_line_ids[0]
        move_line.write({'package_id':False,'lot_id':lot2.id})

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot1,package_id=package1),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,lot_id=lot2),0.0)

    deftest_edit_done_move_line_6(self):
        """Testthateditingadonestockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthetransfer.Inthiscase,weeditthesublocationwherewetakethe
        producttoanothersublocationwhereaproductisNOTavailable.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        move1.move_line_ids.location_id=shelf2_location.id

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location,allow_negative=True),-1.0)

    deftest_edit_done_move_line_7(self):
        """Testthateditingadonestockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthetransfer.Inthiscase,weeditthesublocationwherewetakethe
        producttoanothersublocationwhereaproductisNOTavailablebecauseithasbeenreserved
        byanothermove.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        shelf2_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.env['stock.quant']._update_available_quantity(self.product,shelf2_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),1.0)

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        move2=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move2._action_confirm()
        move2._action_assign()

        self.assertEqual(move2.state,'assigned')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        move1.move_line_ids.location_id=shelf2_location.id

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf2_location),0.0)
        self.assertEqual(move2.state,'confirmed')

    deftest_edit_done_move_line_8(self):
        """Testthateditingadonestockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthetransfer.Inthiscase,weincrementthequantitydone(andwedonot
        havemoreinstock.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

        #movefromshelf1
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(move1.product_uom_qty,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        #editoncedone,weactuallymoved2products
        move1.move_line_ids.qty_done=2

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location,allow_negative=True),-1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,allow_negative=True),-1.0)
        self.assertEqual(move1.product_uom_qty,2.0)

    deftest_edit_done_move_line_9(self):
        """Testthateditingadonestockmovelinelinkedtoanuntrackedproductcorrectlyand
        directlyadaptsthetransfer.Inthiscase,we"cancel"themovebyzeroingtheqtydone.
        """
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':self.stock_location.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,shelf1_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

        #movefromshelf1
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1._action_done()

        self.assertEqual(move1.product_uom_qty,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

        #editoncedone,weactuallymoved2products
        move1.move_line_ids.qty_done=0

        self.assertEqual(move1.product_uom_qty,0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,shelf1_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_edit_done_move_line_10(self):
        """Editthequantitydoneforanincomingmoveshoudldalsoremovethequantifthere
            arenoproductinstock.
        """
        #movefromshelf1
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10
        move1._action_done()

        quant=self.gather_relevant(self.product,self.stock_location)
        self.assertEqual(len(quant),1.0)

        #editoncedone,weactuallymoved2products
        move1.move_line_ids.qty_done=0

        quant=self.gather_relevant(self.product,self.stock_location)
        self.assertEqual(len(quant),0.0)
        self.assertEqual(move1.product_uom_qty,0.0)

    deftest_edit_done_move_line_11(self):
        """Addamovelineandcheckifthequantisupdated
        """
        owner=self.env['res.partner'].create({'name':'Jean'})
        picking=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'partner_id':owner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        #movefromshelf1
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        picking.action_confirm()
        picking.action_assign()
        move1.move_line_ids.qty_done=10
        picking._action_done()
        self.assertEqual(move1.product_uom_qty,10.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)
        self.env['stock.move.line'].create({
            'picking_id':move1.move_line_ids.picking_id.id,
            'move_id':move1.move_line_ids.move_id.id,
            'product_id':move1.move_line_ids.product_id.id,
            'qty_done':move1.move_line_ids.qty_done,
            'product_uom_id':move1.product_uom.id,
            'location_id':move1.move_line_ids.location_id.id,
            'location_dest_id':move1.move_line_ids.location_dest_id.id,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),20.0)
        move1.move_line_ids[1].qty_done=5
        self.assertEqual(move1.product_uom_qty,15.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),15.0)

    deftest_edit_done_move_line_12(self):
        """Testthateditingadonestockmovelinelinkedatrackedproductcorrectlyanddirectly
        adaptsthetransfer.Inthiscase,weeditthelottoanotherone,buttheoriginalmoveline
        isnotinthedefaultproduct'sUOM.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        package1=self.env['stock.quant.package'].create({'name':'test_edit_done_move_line_12'})
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1.move_line_ids.lot_id=lot1.id
        move1._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1),12.0)

        #Changethedonequantityfrom1dozentotwodozen
        move1.move_line_ids.qty_done=2
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1),24.0)

    deftest_edit_done_move_line_13(self):
        """Testthateditingadonestockmovelinelinkedtoapackedandtrackedproductcorrectly
        anddirectlyadaptsthetransfer.Inthiscase,weeditthelottoanotheravailableone
        thatweputinthesamepack.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        package1=self.env['stock.quant.package'].create({'name':'test_edit_reserved_move_line_5'})

        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1
        move1.move_line_ids.lot_id=lot1.id
        move1.move_line_ids.result_package_id=package1.id
        move1._action_done()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1,package_id=package1),1.0)

        move1.move_line_ids.write({'lot_id':lot2.id})

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1,package_id=package1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot2,package_id=package1),1.0)

    deftest_edit_done_move_line_14(self):
        """TestthateditingadonestockmovelinewithadifferentUoMfromitsstockmovecorrectly
        updatesthequantwhenitsqtyand/oritsUoMisedited.Alsocheckthatwedon'tallowediting
        adonestockmove'sUoM.
        """
        move1=self.env['stock.move'].create({
            'name':'test_edit_moveline',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.product_uom_id=self.uom_dozen
        move1.move_line_ids.qty_done=1
        move1._action_done()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),12.0)

        move1.move_line_ids.qty_done=2
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),24.0)
        self.assertEqual(move1.product_uom_qty,24.0)
        self.assertEqual(move1.product_qty,24.0)

        move1.move_line_ids.product_uom_id=self.uom_unit
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(move1.product_uom_qty,2.0)
        self.assertEqual(move1.product_qty,2.0)

        withself.assertRaises(UserError):
            move1.product_uom=self.uom_dozen

    deftest_immediate_validate_1(self):
        """Inapickingwithasingleavailablemove,clickingonvalidatewithoutfillingany
        quantitiesshouldopenawizardaskingtoprocessallthereservation(so,thewholemove).
        """
        partner=self.env['res.partner'].create({'name':'Jean'})
        picking=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.env['stock.move'].create({
            'name':'test_immediate_validate_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        picking.action_confirm()
        picking.action_assign()
        res_dict=picking.button_validate()
        self.assertEqual(res_dict.get('res_model'),'stock.immediate.transfer')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)

    deftest_immediate_validate_2(self):
        """Inapickingwithasinglepartiallyavailablemove,clickingonvalidatewithout
        fillinganyquantitiesshouldopenawizardaskingtoprocessallthereservation(so,only
        apartoftheinitialdemand).Validatingthiswizardshouldopenanotheroneaskingfor
        thecreationofabackorder.Ifthebackorderiscreated,itshouldcontainthequantities
        notprocessed.
        """
        partner=self.env['res.partner'].create({'name':'Jean'})
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,5.0)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        self.env['stock.move'].create({
            'name':'test_immediate_validate_2',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        picking.action_confirm()
        picking.action_assign()
        #Only5productsarereservedonthemoveof10,clickon`button_validate`.
        res_dict=picking.button_validate()
        self.assertEqual(res_dict.get('res_model'),'stock.immediate.transfer')
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        res_dict_for_back_order=wizard.process()
        self.assertEqual(res_dict_for_back_order.get('res_model'),'stock.backorder.confirmation')
        backorder_wizard=self.env[(res_dict_for_back_order.get('res_model'))].browse(res_dict_for_back_order.get('res_id')).with_context(res_dict_for_back_order['context'])
        #Chosetocreateabackorder.
        backorder_wizard.process()

        #Only5productsshouldbeprocessedontheinitialmove.
        self.assertEqual(picking.move_lines.state,'done')
        self.assertEqual(picking.move_lines.quantity_done,5.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)

        #Thebackodershouldcontainamovefortheother5produts.
        backorder=self.env['stock.picking'].search([('backorder_id','=',picking.id)])
        self.assertEqual(len(backorder),1.0)
        self.assertEqual(backorder.move_lines.product_uom_qty,5.0)

    deftest_immediate_validate_3(self):
        """Inapickingwithtwomoves,onepartiallyavailableandoneunavailable,clicking
        onvalidatewithoutfillinganyquantitiesshouldopenawizardaskingtoprocessallthe
        reservation(so,onlyapartofoneofthemoves).Validatingthiswizardshouldopen
        anotheroneaskingforthecreationofabackorder.Ifthebackorderiscreated,itshould
        containthequantitiesnotprocessed.
        """
        product5=self.env['product.product'].create({
            'name':'Product5',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1)

        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_internal').id,
        })
        product1_move=self.env['stock.move'].create({
            'name':'product1_move',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100,
        })
        product5_move=self.env['stock.move'].create({
            'name':'product3_move',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'picking_id':picking.id,
            'product_id':product5.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100,
        })
        picking.action_confirm()
        picking.action_assign()

        #product1_moveshouldbepartiallyavailable(1/100),product5_moveshouldbetotally
        #unavailable(0/100)
        self.assertEqual(product1_move.state,'partially_available')
        self.assertEqual(product5_move.state,'confirmed')

        action=picking.button_validate()
        self.assertEqual(action.get('res_model'),'stock.immediate.transfer')
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        action=wizard.process()
        self.assertTrue(isinstance(action,dict),'Shouldopenbackorderwizard')
        self.assertEqual(action.get('res_model'),'stock.backorder.confirmation')
        wizard=self.env[(action.get('res_model'))].browse(action.get('res_id')).with_context(action.get('context'))
        wizard.process()
        backorder=self.env['stock.picking'].search([('backorder_id','=',picking.id)])
        self.assertEqual(len(backorder),1.0)

        #Thebackordershouldcontain99product1and100product5.
        forbackorder_moveinbackorder.move_lines:
            ifbackorder_move.product_id.id==self.product.id:
                self.assertEqual(backorder_move.product_qty,99)
            elifbackorder_move.product_id.id==product5.id:
                self.assertEqual(backorder_move.product_qty,100)

    deftest_immediate_validate_4(self):
        """Inapickingwithasingleavailabletrackedbylotmove,clickingonvalidatewithout
        fillinganyquantitiesshouldpopuptheimmediatetransferwizard.
        """
        partner=self.env['res.partner'].create({'name':'Jean'})
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,5.0,lot_id=lot1)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        #movefromshelf1
        self.env['stock.move'].create({
            'name':'test_immediate_validate_4',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_id':picking.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        picking.action_confirm()
        picking.action_assign()
        #Noquantitiesfilled,immediatetransferwizardshouldpopup.
        immediate_trans_wiz_dict=picking.button_validate()
        self.assertEqual(immediate_trans_wiz_dict.get('res_model'),'stock.immediate.transfer')
        immediate_trans_wiz=Form(self.env[immediate_trans_wiz_dict['res_model']].with_context(immediate_trans_wiz_dict['context'])).save()
        immediate_trans_wiz.process()

        self.assertEqual(picking.move_lines.quantity_done,5.0)
        #Checkmove_linesdata
        self.assertEqual(len(picking.move_lines.move_line_ids),1)
        self.assertEqual(picking.move_lines.move_line_ids.lot_id,lot1)
        self.assertEqual(picking.move_lines.move_line_ids.qty_done,5.0)
        #Checkquantsdata
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0.0)

    def_create_picking_test_immediate_validate_5(self,picking_type_id,product_id):
        picking=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_type_id':picking_type_id.id,
        })
        self.env['stock.move'].create({
            'name':'move1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_id':picking.id,
            'picking_type_id':picking_type_id.id,
            'product_id':product_id.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })

        picking.action_confirm()

        forlineinpicking.move_line_ids:
            line.qty_done=line.product_uom_qty

        returnpicking

    deftest_immediate_validate_5(self):
        """Inareceiptwithasingletrackedbyserialnumbersmove,clickingonvalidatewithout
        fillinganyquantitiesnorlotshouldopenanUserErrorexceptifthepickingtypeis
        configuredtoallowotherwise.
        """
        picking_type_id=self.env.ref('stock.picking_type_in')
        product_id=self.product_serial
        self.assertTrue(picking_type_id.use_create_lotsorpicking_type_id.use_existing_lots)
        self.assertEqual(product_id.tracking,'serial')

        picking=self._create_picking_test_immediate_validate_5(picking_type_id,product_id)
        #shouldraisebecausenoserialnumberswerespecified
        self.assertRaises(UserError,picking.button_validate)

        picking_type_id.use_create_lots=False
        picking_type_id.use_existing_lots=False
        picking=self._create_picking_test_immediate_validate_5(picking_type_id,product_id)
        picking.button_validate()
        self.assertEqual(picking.state,'done')

    deftest_immediate_validate_6(self):
        """Inareceiptpickingwithtwomoves,onetrackedandoneuntracked,clickingon
        validatewithoutfillinganyquantitiesshoulddisplaysanUserErroraslongasnoquantity
        doneandlot_nameissetonthetrackedmove.Nowiftheuservalidatesthepicking,the
        wizardtellingtheuserallreservedquantitieswillbeprocessedwillNOTbeopened.This
        wizardisonlyopeneifnoquantitieswerefilled.Sovalidatingthepickingatthisstate
        willopenanotherwizardaskingforthecreationofabackorder.Now,iftheuserprocessed
        onthesecondmovemorethanthereservation,awizardwillaskhimtoconfirm.
        """
        picking_type=self.env.ref('stock.picking_type_in')
        picking_type.use_create_lots=True
        picking_type.use_existing_lots=False
        picking=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_type_id':picking_type.id,
        })
        self.env['stock.move'].create({
            'name':'product1_move',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1,
        })
        product3_move=self.env['stock.move'].create({
            'name':'product3_move',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_id':picking.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1,
        })
        picking.action_confirm()
        picking.action_assign()

        withself.assertRaises(UserError):
            picking.button_validate()
        product3_move.move_line_ids[0].qty_done=1
        withself.assertRaises(UserError):
            picking.button_validate()
        product3_move.move_line_ids[0].lot_name='271828'
        action=picking.button_validate() #shouldopenbackorderwizard

        self.assertTrue(isinstance(action,dict),'Shouldopenbackorderwizard')
        self.assertEqual(action.get('res_model'),'stock.backorder.confirmation')

    deftest_immediate_validate_7(self):
        """Inapickingwithasingleunavailablemove,clickingonvalidatewithoutfillingany
        quantitiesshoulddisplayanUserErrortellingtheuserhecannotprocessapickingwithout
        anyprocessedquantity.
        """
        partner=self.env['res.partner'].create({'name':'Jean'})
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        self.env['stock.move'].create({
            'name':'test_immediate_validate_2',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        picking.action_confirm()
        picking.action_assign()

        scrap=self.env['stock.scrap'].create({
            'picking_id':picking.id,
            'product_id':self.product.id,
            'product_uom_id':self.uom_unit.id,
            'scrap_qty':5.0,
        })
        scrap.do_scrap()

        #Noproductsarereservedonthemoveof10,clickon`button_validate`.
        withself.assertRaises(UserError):
            picking.button_validate()

    deftest_immediate_validate_8(self):
        """Validatethreereceiptsatonce."""
        partner=self.env['res.partner'].create({'name':'Pierre'})
        receipt1=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.env['stock.move'].create({
            'name':'test_immediate_validate_8_1',
            'location_id':receipt1.location_id.id,
            'location_dest_id':receipt1.location_dest_id.id,
            'picking_id':receipt1.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        receipt1.action_confirm()
        receipt2=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.env['stock.move'].create({
            'name':'test_immediate_validate_8_2',
            'location_id':receipt2.location_id.id,
            'location_dest_id':receipt2.location_dest_id.id,
            'picking_id':receipt2.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        receipt2.action_confirm()
        receipt3=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        self.env['stock.move'].create({
            'name':'test_immediate_validate_8_3',
            'location_id':receipt3.location_id.id,
            'location_dest_id':receipt3.location_dest_id.id,
            'picking_id':receipt3.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        receipt3.action_confirm()

        immediate_trans_wiz_dict=(receipt1+receipt2).button_validate()
        immediate_trans_wiz=Form(self.env[immediate_trans_wiz_dict['res_model']].with_context(immediate_trans_wiz_dict['context'])).save()
        #Thedifferenttransfersaredisplayedtotheusers.
        self.assertTrue(immediate_trans_wiz.show_transfers)
        #Alltransfersareprocessedbydefault
        self.assertEqual(immediate_trans_wiz.immediate_transfer_line_ids.mapped('to_immediate'),[True,True])
        #Onlytransferreceipt1
        immediate_trans_wiz.immediate_transfer_line_ids.filtered(lambdaline:line.picking_id==receipt2).to_immediate=False
        immediate_trans_wiz.process()
        self.assertEqual(receipt1.state,'done')
        self.assertEqual(receipt2.state,'assigned')
        #Transferreceipt2andreceipt3.
        immediate_trans_wiz_dict=(receipt3+receipt2).button_validate()
        immediate_trans_wiz=Form(self.env[immediate_trans_wiz_dict['res_model']].with_context(immediate_trans_wiz_dict['context'])).save()
        immediate_trans_wiz.process()
        self.assertEqual(receipt2.state,'done')
        self.assertEqual(receipt3.state,'done')

    deftest_set_quantity_done_1(self):
        move1=self.env['stock.move'].create({
            'name':'test_set_quantity_done_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move2=self.env['stock.move'].create({
            'name':'test_set_quantity_done_2',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        (move1+move2)._action_confirm()
        (move1+move2).write({'quantity_done':1})
        self.assertEqual(move1.quantity_done,1)
        self.assertEqual(move2.quantity_done,1)

    deftest_initial_demand_1(self):
        """Checkthattheinitialdemandissetto0whencreatingamovebyhand,and
        thatchangingtheproductonthemovedonotresettheinitialdemand.
        """
        move1=self.env['stock.move'].create({
            'name':'test_in_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
        })
        self.assertEqual(move1.state,'draft')
        self.assertEqual(move1.product_uom_qty,0)
        move1.product_uom_qty=100
        move1.product_id=self.product_serial
        move1.onchange_product_id()
        self.assertEqual(move1.product_uom_qty,100)

    deftest_scrap_1(self):
        """Checkthecreatedstockmoveandtheimpactonquantswhenwescrapa
        storableproduct.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1)
        scrap=self.env['stock.scrap'].create({
            'product_id':self.product.id,
            'product_uom_id':self.product.uom_id.id,
            'scrap_qty':1,
        })
        scrap.do_scrap()
        self.assertEqual(scrap.state,'done')
        move=scrap.move_id
        self.assertEqual(move.state,'done')
        self.assertEqual(move.quantity_done,1)
        self.assertEqual(move.scrapped,True)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)

    deftest_scrap_2(self):
        """Checkthecreatedstockmoveandtheimpactonquantswhenwescrapa
        consumableproduct.
        """
        scrap=self.env['stock.scrap'].create({
            'product_id':self.product_consu.id,
            'product_uom_id':self.product_consu.uom_id.id,
            'scrap_qty':1,
        })
        self.assertEqual(scrap.name,'New','NameshouldbeNewindraftstate')
        scrap.do_scrap()
        self.assertTrue(scrap.name.startswith('SP/'),'SequenceshouldbeChangedafterdo_scrap')
        self.assertEqual(scrap.state,'done')
        move=scrap.move_id
        self.assertEqual(move.state,'done')
        self.assertEqual(move.quantity_done,1)
        self.assertEqual(move.scrapped,True)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_consu,self.stock_location),0)

    deftest_scrap_3(self):
        """Scraptheproductofareservedmoveline.Checkthatthemovelineis
        correctlydeletedandthattheassociatedstockmoveisnotassignedanymore.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1)
        move1=self.env['stock.move'].create({
            'name':'test_scrap_3',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(len(move1.move_line_ids),1)

        scrap=self.env['stock.scrap'].create({
            'product_id':self.product.id,
            'product_uom_id':self.product.uom_id.id,
            'scrap_qty':1,
        })
        scrap.do_scrap()
        self.assertEqual(move1.state,'confirmed')
        self.assertEqual(len(move1.move_line_ids),0)

    deftest_scrap_4(self):
        """Scraptheproductofapicking.Thenmodifythe
        donelinkedstockmoveandensurethescrapquantityisalso
        updated.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,10)
        partner=self.env['res.partner'].create({'name':'Kimberley'})
        picking=self.env['stock.picking'].create({
            'name':'Asinglepickingwithonemovetoscrap',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move1=self.env['stock.move'].create({
            'name':'Amovetoconfirmandscrapitsproduct',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_id':picking.id,
        })
        move1._action_confirm()

        self.assertEqual(move1.state,'confirmed')
        scrap=self.env['stock.scrap'].create({
            'product_id':self.product.id,
            'product_uom_id':self.product.uom_id.id,
            'scrap_qty':5,
            'picking_id':picking.id,
        })

        scrap.action_validate()
        self.assertEqual(len(picking.move_lines),2)
        scrapped_move=picking.move_lines.filtered(lambdam:m.state=='done')
        self.assertTrue(scrapped_move,'Noscrappedmovecreated.')
        self.assertEqual(scrapped_move.scrap_ids.ids,[scrap.id],'Wrongscraplinkedtothemove.')
        self.assertEqual(scrap.scrap_qty,5,'Scrapquantityhasbeenmodifiedandisnotcorrectanymore.')

        scrapped_move.quantity_done=8
        self.assertEqual(scrap.scrap_qty,8,'Scrapquantityisnotupdated.')

    deftest_scrap_5(self):
        """Scraptheproductofareservedmovelinewheretheproductisreservedinanother
        unitofmeasure.Checkthatthemovelineiscorrectlyupdatedafterthescrap.
        """
        #4unitsareavailableinstock
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,4)

        #trytoreserveadozen
        partner=self.env['res.partner'].create({'name':'Kimberley'})
        picking=self.env['stock.picking'].create({
            'name':'Asinglepickingwithonemovetoscrap',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move1=self.env['stock.move'].create({
            'name':'Amovetoconfirmandscrapitsproduct',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':1.0,
            'picking_id':picking.id,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.reserved_availability,0.33)

        #scrapaunit
        scrap=self.env['stock.scrap'].create({
            'product_id':self.product.id,
            'product_uom_id':self.product.uom_id.id,
            'scrap_qty':1,
            'picking_id':picking.id,
        })
        scrap.action_validate()

        self.assertEqual(scrap.state,'done')
        self.assertEqual(move1.reserved_availability,0.25)

    deftest_scrap_6(self):
        """CheckthatscrapcorrectlyhandleUoM."""
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1)
        scrap=self.env['stock.scrap'].create({
            'product_id':self.product.id,
            'product_uom_id':self.uom_dozen.id,
            'scrap_qty':1,
        })
        warning_message=scrap.action_validate()
        self.assertEqual(warning_message.get('res_model','WrongModel'),'stock.warn.insufficient.qty.scrap')
        insufficient_qty_wizard=self.env['stock.warn.insufficient.qty.scrap'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'scrap_id':scrap.id,
            'quantity':1,
            'product_uom_name':self.product.uom_id.name
        })
        insufficient_qty_wizard.action_done()
        self.assertEqual(self.env['stock.quant']._gather(self.product,self.stock_location).quantity,-11)

    deftest_scrap_7(self):
        """
        Supposeauserwantstoscrapsomeproductsthankstointernalmoves.
        Thistestchecksthestateofthepickingbasedonfewcases
        """
        scrap_location=self.env['stock.location'].search([('company_id','=',self.env.company.id),('scrap_location','=',True)],limit=1)
        internal_operation=self.env['stock.picking.type'].with_context(active_test=False).search([('code','=','internal'),('company_id','=',self.env.company.id)],limit=1)
        internal_operation.active=True

        product01=self.product
        product02=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'product',
        })

        self.env['stock.quant']._update_available_quantity(product01,self.stock_location,3)
        self.env['stock.quant']._update_available_quantity(product02,self.stock_location,1)

        scrap_picking01,scrap_picking02,scrap_picking03=self.env['stock.picking'].create([{
            'location_id':self.stock_location.id,
            'location_dest_id':scrap_location.id,
            'picking_type_id':internal_operation.id,
            'move_lines':[(0,0,{
                'name':'Scrap%s'%product.display_name,
                'location_id':self.stock_location.id,
                'location_dest_id':scrap_location.id,
                'product_id':product.id,
                'product_uom':product.uom_id.id,
                'product_uom_qty':1.0,
                'picking_type_id':internal_operation.id,
            })forproductinproducts],
        }forproductsin[(product01,),(product01,),(product01,product02)]])

        (scrap_picking01+scrap_picking02+scrap_picking03).action_confirm()

        #AllSMareprocessed
        scrap_picking01.move_lines.quantity_done=1
        scrap_picking01.button_validate()

        #AllSMarecancelled
        scrap_picking02.action_cancel()

        #ProcessoneSMandcanceltheotherone
        pick03_prod01_move=scrap_picking03.move_lines.filtered(lambdasm:sm.product_id==product01)
        pick03_prod02_move=scrap_picking03.move_lines-pick03_prod01_move
        pick03_prod01_move.quantity_done=1
        pick03_prod02_move._action_cancel()
        scrap_picking03.button_validate()

        self.assertEqual(scrap_picking01.move_lines.state,'done')
        self.assertEqual(scrap_picking01.state,'done')

        self.assertEqual(scrap_picking02.move_lines.state,'cancel')
        self.assertEqual(scrap_picking02.state,'cancel')

        self.assertEqual(pick03_prod01_move.state,'done')
        self.assertEqual(pick03_prod02_move.state,'cancel')
        self.assertEqual(scrap_picking03.state,'done')

        self.assertEqual(self.env['stock.quant']._get_available_quantity(product01,self.stock_location),1)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(product02,self.stock_location),1)

    deftest_in_date_1(self):
        """Checkthatmovingatrackedquantkeepstheincomingdate.
        """
        move1=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.lot_name='lot1'
        move1.move_line_ids.qty_done=1
        move1._action_done()

        quant=self.gather_relevant(self.product_lot,self.stock_location)
        self.assertEqual(len(quant),1.0)
        self.assertNotEqual(quant.in_date,False)

        #Keepareferencetotheinitialincomingdateinordertocompareitlater.
        initial_incoming_date=quant.in_date

        move2=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=1
        move2._action_done()

        quant=self.gather_relevant(self.product_lot,self.pack_location)
        self.assertEqual(len(quant),1.0)
        self.assertEqual(quant.in_date,initial_incoming_date)

    deftest_in_date_2(self):
        """Checkthateditingadonemovelineforatrackedproductandchangingitslot
        correctlyrestorestheoriginallotwithitsincomingdateandremovethenewlot
        withitsincomingdate.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        #receivelot1
        move1=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.lot_id=lot1
        move1.move_line_ids.qty_done=1
        move1._action_done()

        #receivelot2
        move2=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.lot_id=lot2
        move2.move_line_ids.qty_done=1
        move2._action_done()

        initial_in_date_lot2=self.env['stock.quant'].search([
            ('location_id','=',self.stock_location.id),
            ('product_id','=',self.product_lot.id),
            ('lot_id','=',lot2.id),
        ]).in_date

        #Editlot1'sincomingdate.
        quant_lot1=self.env['stock.quant'].search([
            ('location_id','=',self.stock_location.id),
            ('product_id','=',self.product_lot.id),
            ('lot_id','=',lot1.id),
        ])
        fromflectra.fieldsimportDatetime
        fromdatetimeimporttimedelta
        initial_in_date_lot1=Datetime.now()-timedelta(days=5)
        quant_lot1.in_date=initial_in_date_lot1

        #Moveonequanttopacklocation
        move3=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=1
        move3._action_done()
        quant_in_pack=self.env['stock.quant'].search([
            ('product_id','=',self.product_lot.id),
            ('location_id','=',self.pack_location.id),
        ])
        #Aslot1hasanolderdateandFIFOissetbydefault,it'stheonethatshouldbe
        #inpack.
        self.assertEqual(len(quant_in_pack),1)
        self.assertAlmostEqual(quant_in_pack.in_date,initial_in_date_lot1,delta=timedelta(seconds=1))
        self.assertEqual(quant_in_pack.lot_id,lot1)

        #Now,editthemovelineandactuallymovetheotherlot
        move3.move_line_ids.lot_id=lot2

        #Checkthatlot1correctlyisbacktostockwithitsrightin_date
        quant_lot1=self.env['stock.quant'].search([
            ('location_id.usage','=','internal'),
            ('product_id','=',self.product_lot.id),
            ('lot_id','=',lot1.id),
            ('quantity','!=',0),
        ])
        self.assertEqual(quant_lot1.location_id,self.stock_location)
        self.assertAlmostEqual(quant_lot1.in_date,initial_in_date_lot1,delta=timedelta(seconds=1))

        #Checkthatlo2isinpackwithisrightin_date
        quant_lot2=self.env['stock.quant'].search([
            ('location_id.usage','=','internal'),
            ('product_id','=',self.product_lot.id),
            ('lot_id','=',lot2.id),
            ('quantity','!=',0),
        ])
        self.assertEqual(quant_lot2.location_id,self.pack_location)
        self.assertAlmostEqual(quant_lot2.in_date,initial_in_date_lot2,delta=timedelta(seconds=1))

    deftest_in_date_3(self):
        """Checkthat,whencreatingamovelineonadonestockmove,thelotanditsincoming
        datearecorrectlymovedtothedestinationlocation.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        #receivelot1
        move1=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.lot_id=lot1
        move1.move_line_ids.qty_done=1
        move1._action_done()

        #receivelot2
        move2=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.lot_id=lot2
        move2.move_line_ids.qty_done=1
        move2._action_done()

        initial_in_date_lot2=self.env['stock.quant'].search([
            ('location_id','=',self.stock_location.id),
            ('product_id','=',self.product_lot.id),
            ('lot_id','=',lot2.id),
            ('quantity','!=',0),
        ]).in_date

        #Editlot1'sincomingdate.
        quant_lot1=self.env['stock.quant'].search([
            ('location_id.usage','=','internal'),
            ('product_id','=',self.product_lot.id),
            ('lot_id','=',lot1.id),
            ('quantity','!=',0),
        ])
        fromflectra.fieldsimportDatetime
        fromdatetimeimporttimedelta
        initial_in_date_lot1=Datetime.now()-timedelta(days=5)
        quant_lot1.in_date=initial_in_date_lot1

        #Moveonequanttopacklocation
        move3=self.env['stock.move'].create({
            'name':'test_in_date_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.pack_location.id,
            'product_id':self.product_lot.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=1
        move3._action_done()

        #Now,alsomovelot2
        self.env['stock.move.line'].create({
            'move_id':move3.id,
            'product_id':move3.product_id.id,
            'qty_done':1,
            'product_uom_id':move3.product_uom.id,
            'location_id':move3.location_id.id,
            'location_dest_id':move3.location_dest_id.id,
            'lot_id':lot2.id,
        })

        quants=self.env['stock.quant'].search([
            ('location_id.usage','=','internal'),
            ('product_id','=',self.product_lot.id),
            ('quantity','!=',0),
        ])
        self.assertEqual(len(quants),2)
        forquantinquants:
            ifquant.lot_id==lot1:
                self.assertAlmostEqual(quant.in_date,initial_in_date_lot1,delta=timedelta(seconds=1))
            elifquant.lot_id==lot2:
                self.assertAlmostEqual(quant.in_date,initial_in_date_lot2,delta=timedelta(seconds=1))

    deftest_edit_initial_demand_1(self):
        """Increaseinitialdemandonceeverythingisreservedandcheckif
        theexistingmove_lineisupdated.
        """
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.product_uom_qty=15
        #_action_assignisautomaticallycalled
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(move1.product_uom_qty,15)
        self.assertEqual(len(move1.move_line_ids),1)

    deftest_edit_initial_demand_2(self):
        """Decreaseinitialdemandonceeverythingisreservedandcheckif
        theexistingmove_linehasbeendroppedaftertheupdatedandanother
        iscreatedoncethemoveisreserved.
        """
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        self.assertEqual(move1.state,'assigned')
        move1.product_uom_qty=5
        self.assertEqual(move1.state,'assigned')
        self.assertEqual(move1.product_uom_qty,5)
        self.assertEqual(len(move1.move_line_ids),1)

    deftest_initial_demand_3(self):
        """Increasetheinitialdemandonareceiptpicking,thesystemshouldautomatically
        reservethenewquantity.
        """
        picking=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'immediate_transfer':True,
        })
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'quantity_done':10.0,
            'picking_id':picking.id,
        })
        picking._autoconfirm_picking()
        self.assertEqual(picking.state,'assigned')
        move1.quantity_done=12
        self.assertEqual(picking.state,'assigned')

    deftest_initial_demand_4(self):
        """Increasetheinitialdemandonadeliverypicking,thesystemshouldnotautomatically
        reservethenewquantity.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,12)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'picking_id':picking.id,
        })
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.state,'assigned')
        move1.product_uom_qty=12
        self.assertEqual(picking.state,'assigned') #actually,partiallyavailable
        self.assertEqual(move1.state,'partially_available')
        picking.action_assign()
        self.assertEqual(move1.state,'assigned')

    deftest_change_product_type(self):
        """Changingtypeofanexistingproductwillraiseausererrorif
            -somemovearereserved
            -switchingfromastockableproductwhenqty_availableisnotzero
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,10)
        move1=self.env['stock.move'].create({
            'name':'test_customer',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move1._action_confirm()
        move1._action_assign()

        withself.assertRaises(UserError):
            self.product.type='consu'
        move1._action_cancel()

        withself.assertRaises(UserError):
            self.product.type='consu'

        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,-self.product.qty_available)
        self.product.type='consu'

        move2=self.env['stock.move'].create({
            'name':'test_customer',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })

        move2._action_confirm()
        move2._action_assign()

        withself.assertRaises(UserError):
            self.product.type='product'
        move2._action_cancel()
        self.product.type='product'

    deftest_edit_done_picking_1(self):
        """Addanewmovelineinadonepickingshouldgeneratean
        associatedmove.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,12)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'picking_id':picking.id,
        })
        picking.action_confirm()
        picking.action_assign()
        move1.quantity_done=10
        picking._action_done()

        self.assertEqual(len(picking.move_lines),1,'Onemoveshouldexistforthepicking.')
        self.assertEqual(len(picking.move_line_ids),1,'Onemovelineshouldexistforthepicking.')

        ml=self.env['stock.move.line'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom_id':self.uom_unit.id,
            'qty_done':2.0,
            'picking_id':picking.id,
        })

        self.assertEqual(len(picking.move_lines),2,'Thenewmoveassociatedtothemovelinedoesnotexist.')
        self.assertEqual(len(picking.move_line_ids),2,'Itshouldbe2movelinesforthepicking.')
        self.assertTrue(ml.move_idinpicking.move_lines,'Linksarenotcorrectbetweenpicking,movesandmovelines.')
        self.assertEqual(picking.state,'done','Pickingshouldstilldoneafteraddinganewmoveline.')
        self.assertTrue(all(move.state=='done'formoveinpicking.move_lines),'Wrongstateformove.')

    deftest_put_in_pack_1(self):
        """Checkthatreservingamoveandaddingitsmovelinesto
        differentpackagesworkasexpected.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'picking_id':picking.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)
        move1.quantity_done=1
        picking.action_put_in_pack()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)
        self.assertEqual(len(picking.move_line_ids),2)
        unpacked_ml=picking.move_line_ids.filtered(lambdaml:notml.result_package_id)
        self.assertEqual(unpacked_ml.product_qty,1)
        unpacked_ml.qty_done=1
        picking.action_put_in_pack()
        self.assertEqual(len(picking.move_line_ids),2)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)
        picking.button_validate()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.customer_location),2)

    deftest_put_in_pack_2(self):
        """Checkthatreservingmoveswithoutdonequantity
        addinginsamepackage.
        """
        product1=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1)
        self.env['stock.quant']._update_available_quantity(product1,self.stock_location,2)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_id':picking.id,
        })
        move2=self.env['stock.move'].create({
            'name':'test_transit_2',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'picking_id':picking.id,
        })
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(product1,self.stock_location),0)
        picking.action_put_in_pack()
        self.assertEqual(len(picking.move_line_ids),2)
        self.assertEqual(picking.move_line_ids[0].qty_done,1,"Stockmovelineshouldhave1quantityasadonequantity.")
        self.assertEqual(picking.move_line_ids[1].qty_done,2,"Stockmovelineshouldhave2quantityasadonequantity.")
        line1_result_package=picking.move_line_ids[0].result_package_id
        line2_result_package=picking.move_line_ids[1].result_package_id
        self.assertEqual(line1_result_package,line2_result_package,"ProductandProduct1shouldbeinasamepackage.")

    deftest_put_in_pack_3(self):
        """Checkthatonereservingmovewithoutdonequantityand
        anotherreservingmovewithdonequantityaddingindifferent
        package.
        """
        product1=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1)
        self.env['stock.quant']._update_available_quantity(product1,self.stock_location,2)
        picking=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move1=self.env['stock.move'].create({
            'name':'test_transit_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'picking_id':picking.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move2=self.env['stock.move'].create({
            'name':'test_transit_2',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'picking_id':picking.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(product1,self.stock_location),0)
        move1.quantity_done=1
        picking.action_put_in_pack()
        move2.quantity_done=2
        picking.action_put_in_pack()
        self.assertEqual(len(picking.move_line_ids),2)
        line1_result_package=picking.move_line_ids[0].result_package_id
        line2_result_package=picking.move_line_ids[1].result_package_id
        self.assertNotEqual(line1_result_package,line2_result_package,"ProductandProduct1shouldbeinadifferentpackage.")

    deftest_forecast_availability(self):
        """Makeanoutgoingpickingindozensforaproductstoredinunits.
        Checkthatreserved_availabityisexpressedinmoveuomandforecast_availabilityisinproductbaseuom
        """
        #createproduct
        product=self.env['product.product'].create({
            'name':'ProductInUnits',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        #makesomestock
        self.env['stock.quant']._update_available_quantity(product,self.stock_location,36.0)
        #createpicking
        picking_out=self.env['stock.picking'].create({
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id})
        move=self.env['stock.move'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom':self.uom_dozen.id,
            'product_uom_qty':2.0,
            'picking_id':picking_out.id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id})
        #confirm
        picking_out.action_confirm()
        #checkavailability
        picking_out.action_assign()
        #checkreserved_availabityexpressedinmoveuom
        self.assertEqual(move.reserved_availability,2)
        #checkforecast_availabilityexpressedinproductbaseuom
        self.assertEqual(move.forecast_availability,24)
