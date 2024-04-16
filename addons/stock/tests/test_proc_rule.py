#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime,timedelta

fromflectra.tests.commonimportForm,TransactionCase
fromflectra.toolsimportmute_logger
fromflectra.exceptionsimportUserError


classTestProcRule(TransactionCase):

    defsetUp(self):
        super(TestProcRule,self).setUp()

        self.uom_unit=self.env.ref('uom.product_uom_unit')
        self.product=self.env['product.product'].create({
            'name':'DeskCombination',
            'type':'consu',
        })
        self.partner=self.env['res.partner'].create({'name':'Partner'})

    deftest_endless_loop_rules_from_location(self):
        """Createsandconfigurearuletheway,whentryingtogetrulesfrom
        location,itgoesinastatewherethefoundruletriestotriggeranother
        rulebutfindsnothingelsethanitselfandsogetstuckinarecursionerror."""
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        reception_route=warehouse.reception_route_id
        self.product.type='product'

        #Createsadeliveryforthisproduct,thatway,thisproductwillbetoresupply.
        picking_form=Form(self.env['stock.picking'])
        picking_form.picking_type_id=warehouse.out_type_id
        withpicking_form.move_ids_without_package.new()asmove_line:
            move_line.product_id=self.product
            move_line.product_uom_qty=10
        delivery=picking_form.save()
        delivery.action_confirm()
        self.product._compute_quantities() #Computes`outgoing_qty`tohavetheorderpoint.

        #Then,createsaruleandaddsitintotheroute'srules.
        reception_route.rule_ids.action_archive()
        self.env['stock.rule'].create({
            'name':'LoopingRule',
            'route_id':reception_route.id,
            'location_id':warehouse.lot_stock_id.id,
            'location_src_id':warehouse.lot_stock_id.id,
            'action':'pull_push',
            'procure_method':'make_to_order',
            'picking_type_id':warehouse.int_type_id.id,
        })

        #TriestoopentheReplenishmentview->ItshouldraiseanUserError.
        withself.assertRaises(UserError):
            self.env['stock.warehouse.orderpoint'].action_open_orderpoints()

    deftest_proc_rule(self):
        #Createaproductroutecontainingastockrulethatwill
        #generateamovefromStockforeveryprocurementcreatedinOutput
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
        self.product.write({
            'route_ids':[(4,product_route.id)]})

        #CreateDeliveryOrderof10`product.product_product_3`fromOutput->Customer
        product=self.product
        vals={
            'name':'Deliveryorderforprocurement',
            'partner_id':self.partner.id,
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.ref('stock.stock_location_output'),
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'move_lines':[(0,0,{
                'name':'/',
                'product_id':product.id,
                'product_uom':product.uom_id.id,
                'product_uom_qty':10.00,
                'procure_method':'make_to_order',
            })],
        }
        pick_output=self.env['stock.picking'].create(vals)
        pick_output.move_lines.onchange_product_id()

        #Confirmdeliveryorder.
        pick_output.action_confirm()

        #Irunthescheduler.
        #Note:Ifpurchaseifalreadyinstalled,themethod_run_buywillbecalleddue
        #tothepurchasedemodata.Asweupdatethestockmoduletorunthistest,the
        #methodwon'tbeanattributeofstock.procurementatthismoment.Forthatreason
        #wemutetheloggerwhenrunningthescheduler.
        withmute_logger('flectra.addons.stock.models.procurement'):
            self.env['procurement.group'].run_scheduler()

        #Checkthatapickingwascreatedfromstocktooutput.
        moves=self.env['stock.move'].search([
            ('product_id','=',self.product.id),
            ('location_id','=',self.ref('stock.stock_location_stock')),
            ('location_dest_id','=',self.ref('stock.stock_location_output')),
            ('move_dest_ids','in',[pick_output.move_lines[0].id])
        ])
        self.assertEqual(len(moves.ids),1,"ItshouldhavecreatedapickingfromStocktoOutputwiththeoriginalpickingasdestination")

    deftest_propagate_deadline_move(self):
        deadline=datetime.now()
        move_dest=self.env['stock.move'].create({
            'name':'move_dest',
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'date_deadline':deadline,
            'location_id':self.ref('stock.stock_location_output'),
            'location_dest_id':self.ref('stock.stock_location_customers'),
        })

        move_orig=self.env['stock.move'].create({
            'name':'move_orig',
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'date_deadline':deadline,
            'move_dest_ids':[(4,move_dest.id)],
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'quantity_done':10,
        })
        new_deadline=move_orig.date_deadline-timedelta(days=6)
        move_orig.date_deadline=new_deadline
        self.assertEqual(move_dest.date_deadline,new_deadline,msg='deadlinedateshouldbepropagated')
        move_orig._action_done()
        self.assertAlmostEqual(move_orig.date,datetime.now(),delta=timedelta(seconds=10),msg='dateshouldbenow')
        self.assertEqual(move_orig.date_deadline,new_deadline,msg='deadlinedateshouldbeunchanged')
        self.assertEqual(move_dest.date_deadline,new_deadline,msg='deadlinedateshouldbeunchanged')

    deftest_reordering_rule_1(self):
        warehouse=self.env['stock.warehouse'].search([],limit=1)
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=self.product
        orderpoint_form.location_id=warehouse.lot_stock_id
        orderpoint_form.product_min_qty=0.0
        orderpoint_form.product_max_qty=5.0
        orderpoint=orderpoint_form.save()

        #getauto-createdpullrulefromwhenwarehouseiscreated
        rule=self.env['stock.rule'].search([
            ('route_id','=',warehouse.reception_route_id.id),
            ('location_id','=',warehouse.lot_stock_id.id),
            ('location_src_id','=',self.env.ref('stock.stock_location_suppliers').id),
            ('action','=','pull'),
            ('procure_method','=','make_to_stock'),
            ('picking_type_id','=',warehouse.in_type_id.id)])

        #addadelay[i.e.leaddays]soprocurementwillbetriggeredbasedonforecastedstock
        rule.delay=9.0

        delivery_move=self.env['stock.move'].create({
            'name':'Delivery',
            'date':datetime.today()+timedelta(days=5),
            'product_id':self.product.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12.0,
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.ref('stock.stock_location_customers'),
        })
        delivery_move._action_confirm()
        orderpoint._compute_qty()
        self.env['procurement.group'].run_scheduler()

        receipt_move=self.env['stock.move'].search([
            ('product_id','=',self.product.id),
            ('location_id','=',self.env.ref('stock.stock_location_suppliers').id)
        ])
        self.assertTrue(receipt_move)
        self.assertEqual(receipt_move.date.date(),date.today())
        self.assertEqual(receipt_move.product_uom_qty,17.0)

    deftest_reordering_rule_2(self):
        """Testwhenthereisnotenoughproducttoassignapicking=>automaticallyrun
        reorderingrule(RR).Addextraproducttoalreadyconfirmedpicking=>automatically
        runanotherRR
        """
        self.productA=self.env['product.product'].create({
            'name':'DeskCombination',
            'type':'product',
        })

        self.productB=self.env['product.product'].create({
            'name':'DeskDecoration',
            'type':'product',
        })

        warehouse=self.env['stock.warehouse'].search([],limit=1)
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=self.productA
        orderpoint_form.location_id=warehouse.lot_stock_id
        orderpoint_form.product_min_qty=0.0
        orderpoint_form.product_max_qty=5.0
        orderpoint=orderpoint_form.save()

        self.env['stock.warehouse.orderpoint'].create({
            'name':'ProductBRR',
            'location_id':warehouse.lot_stock_id.id,
            'product_id':self.productB.id,
            'product_min_qty':0,
            'product_max_qty':5,
        })

        self.env['stock.rule'].create({
            'name':'RuleSupplier',
            'route_id':warehouse.reception_route_id.id,
            'location_id':warehouse.lot_stock_id.id,
            'location_src_id':self.env.ref('stock.stock_location_suppliers').id,
            'action':'pull',
            'delay':9.0,
            'procure_method':'make_to_stock',
            'picking_type_id':warehouse.in_type_id.id,
        })

        delivery_picking=self.env['stock.picking'].create({
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'picking_type_id':self.ref('stock.picking_type_out'),
        })
        delivery_move=self.env['stock.move'].create({
            'name':'Delivery',
            'product_id':self.productA.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12.0,
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'picking_id':delivery_picking.id,
        })
        delivery_picking.action_confirm()
        delivery_picking.action_assign()

        receipt_move=self.env['stock.move'].search([
            ('product_id','=',self.productA.id),
            ('location_id','=',self.env.ref('stock.stock_location_suppliers').id)
        ])

        self.assertTrue(receipt_move)
        self.assertEqual(receipt_move.date.date(),date.today())
        self.assertEqual(receipt_move.product_uom_qty,17.0)

        delivery_picking.write({'move_lines':[(0,0,{
            'name':'ExtraMove',
            'product_id':self.productB.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
            'location_id':warehouse.lot_stock_id.id,
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'picking_id':delivery_picking.id,
            'additional':True
        })]})

        receipt_move2=self.env['stock.move'].search([
            ('product_id','=',self.productB.id),
            ('location_id','=',self.env.ref('stock.stock_location_suppliers').id)
        ])

        self.assertTrue(receipt_move2)
        self.assertEqual(receipt_move2.date.date(),date.today())
        self.assertEqual(receipt_move2.product_uom_qty,10.0)

    deftest_fixed_procurement_01(self):
        """Runaprocurementfor5productswhenthereareonly4instockthen
        checkthatMTOisappliedonthemoveswhentheruleissetto'mts_else_mto'
        """
        self.partner=self.env['res.partner'].create({'name':'Partner'})
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        warehouse.delivery_steps='pick_ship'
        final_location=self.partner.property_stock_customer

        #Createaproductandadd10unitsinstock
        product_a=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })
        self.env['stock.quant']._update_available_quantity(product_a,warehouse.lot_stock_id,10.0)

        #Createaroutewhichwillallows'wavepicking'
        wave_pg=self.env['procurement.group'].create({'name':'WavePG'})
        wave_route=self.env['stock.location.route'].create({
            'name':'WaveforProductA',
            'product_selectable':True,
            'sequence':1,
            'rule_ids':[(0,0,{
                'name':'Stock->outputrule',
                'action':'pull',
                'picking_type_id':self.ref('stock.picking_type_internal'),
                'location_src_id':self.ref('stock.stock_location_stock'),
                'location_id':self.ref('stock.stock_location_output'),
                'group_propagation_option':'fixed',
                'group_id':wave_pg.id,
            })],
        })

        #Setthisrouteon`product_a`
        product_a.write({
            'route_ids':[(4,wave_route.id)]
        })

        #Createaprocurementfor2units
        pg=self.env['procurement.group'].create({'name':'Wave1'})
        self.env['procurement.group'].run([
            pg.Procurement(
                product_a,
                2.0,
                product_a.uom_id,
                final_location,
                'wave_part_1',
                'wave_part_1',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg
                }
            )
        ])

        #2pickingsshouldbecreated:1forpick,1forship
        picking_pick=self.env['stock.picking'].search([('group_id','=',wave_pg.id)])
        picking_ship=self.env['stock.picking'].search([('group_id','=',pg.id)])
        self.assertAlmostEqual(picking_pick.move_lines.product_uom_qty,2.0)
        self.assertAlmostEqual(picking_ship.move_lines.product_uom_qty,2.0)

        #Createaprocurementfor3units
        pg=self.env['procurement.group'].create({'name':'Wave2'})
        self.env['procurement.group'].run([
            pg.Procurement(
                product_a,
                3.0,
                product_a.uom_id,
                final_location,
                'wave_part_2',
                'wave_part_2',
                warehouse.company_id,
                {
                    'warehouse_id':warehouse,
                    'group_id':pg
                }
            )
        ])

        #Thepickingforthepickoperationshouldbereusedandthelinesmerged.
        picking_ship=self.env['stock.picking'].search([('group_id','=',pg.id)])
        self.assertAlmostEqual(picking_pick.move_lines.product_uom_qty,5.0)
        self.assertAlmostEqual(picking_ship.move_lines.product_uom_qty,3.0)

    deftest_orderpoint_replenishment_view(self):
        """Createtwowarehouses+twomoves
        verifythatthereplenishmentviewisconsistent"""
        warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        warehouse_2,warehouse_3=self.env['stock.warehouse'].create([{
            'name':'WarehouseTwo',
            'code':'WH2',
            'resupply_wh_ids':[warehouse_1.id],
        },{
            'name':'WarehouseThree',
            'code':'WH3',
            'resupply_wh_ids':[warehouse_1.id],
        }])
        route_2=self.env['stock.location.route'].search([
            ('supplied_wh_id','=',warehouse_2.id),
            ('supplier_wh_id','=',warehouse_1.id),
        ])
        route_3=self.env['stock.location.route'].search([
            ('supplied_wh_id','=',warehouse_3.id),
            ('supplier_wh_id','=',warehouse_1.id),
        ])
        product=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'product',
            'route_ids':[route_2.id,route_3.id]
        })
        moves=self.env['stock.move'].create([{
            'name':'MoveWH2',
            'location_id':warehouse_2.lot_stock_id.id,
            'location_dest_id':self.partner.property_stock_customer.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':1,
        },{
            'name':'MoveWH3',
            'location_id':warehouse_3.lot_stock_id.id,
            'location_dest_id':self.partner.property_stock_customer.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':1,
        }])
        moves._action_confirm()
        #activateactionofopeningthereplenishmentview
        self.env['report.stock.quantity'].flush()
        self.env['stock.warehouse.orderpoint'].action_open_orderpoints()
        replenishments=self.env['stock.warehouse.orderpoint'].search([
            ('product_id','=',product.id),
        ])
        #Verifythatthelocationandtheroutemakesense
        self.assertRecordValues(replenishments,[
            {'location_id':warehouse_2.lot_stock_id.id,'route_id':route_2.id},
            {'location_id':warehouse_3.lot_stock_id.id,'route_id':route_3.id},
        ])


classTestProcRuleLoad(TransactionCase):
    defsetUp(cls):
        super(TestProcRuleLoad,cls).setUp()
        cls.skipTest("Performancetest,tooheavytorun.")

    deftest_orderpoint_1(self):
        """Try500productswitha1000RR(stock->shelf1andstock->shelf2)
        Alsorandomlyinclude4missconfiguration.
        """
        warehouse=self.env['stock.warehouse'].create({
            'name':'TestWarehouse',
            'code':'TWH'
        })
        warehouse.reception_steps='three_steps'
        supplier_loc=self.env.ref('stock.stock_location_suppliers')
        stock_loc=warehouse.lot_stock_id
        shelf1=self.env['stock.location'].create({
            'location_id':stock_loc.id,
            'usage':'internal',
            'name':'shelf1'
        })
        shelf2=self.env['stock.location'].create({
            'location_id':stock_loc.id,
            'usage':'internal',
            'name':'shelf2'
        })

        products=self.env['product.product'].create([{'name':i,'type':'product'}foriinrange(500)])
        self.env['stock.warehouse.orderpoint'].create([{
            'product_id':products[i//2].id,
            'location_id':(i%2==0)andshelf1.idorshelf2.id,
            'warehouse_id':warehouse.id,
            'product_min_qty':5,
            'product_max_qty':10,
        }foriinrange(1000)])

        self.env['stock.rule'].create({
            'name':'RuleShelf1',
            'route_id':warehouse.reception_route_id.id,
            'location_id':shelf1.id,
            'location_src_id':stock_loc.id,
            'action':'pull',
            'procure_method':'make_to_order',
            'picking_type_id':warehouse.int_type_id.id,
        })
        self.env['stock.rule'].create({
            'name':'RuleShelf2',
            'route_id':warehouse.reception_route_id.id,
            'location_id':shelf2.id,
            'location_src_id':stock_loc.id,
            'action':'pull',
            'procure_method':'make_to_order',
            'picking_type_id':warehouse.int_type_id.id,
        })
        self.env['stock.rule'].create({
            'name':'RuleSupplier',
            'route_id':warehouse.reception_route_id.id,
            'location_id':warehouse.wh_input_stock_loc_id.id,
            'location_src_id':supplier_loc.id,
            'action':'pull',
            'procure_method':'make_to_stock',
            'picking_type_id':warehouse.in_type_id.id,
        })

        wrong_route=self.env['stock.location.route'].create({
            'name':'WrongRoute',
        })
        self.env['stock.rule'].create({
            'name':'TrapRule',
            'route_id':wrong_route.id,
            'location_id':warehouse.wh_input_stock_loc_id.id,
            'location_src_id':supplier_loc.id,
            'action':'pull',
            'procure_method':'make_to_order',
            'picking_type_id':warehouse.in_type_id.id,
        })
        (products[50]|products[99]|products[150]|products[199]).write({
            'route_ids':[(4,wrong_route.id)]
        })
        self.env['procurement.group'].run_scheduler()
        self.assertTrue(self.env['stock.move'].search([('product_id','in',products.ids)]))
        forindexin[50,99,150,199]:
            self.assertTrue(self.env['mail.activity'].search([
                ('res_id','=',products[index].product_tmpl_id.id),
                ('res_model_id','=',self.env.ref('product.model_product_template').id)
            ]))
