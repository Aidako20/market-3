#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime,timedelta

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.product.testsimportcommon
fromflectra.testsimportForm
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT


classTestCreatePicking(common.TestProductCommon):

    defsetUp(self):
        super(TestCreatePicking,self).setUp()
        self.partner_id=self.env['res.partner'].create({'name':'WoodCornerPartner'})
        self.product_id_1=self.env['product.product'].create({'name':'LargeDesk'})
        self.product_id_2=self.env['product.product'].create({'name':'ConferenceChair'})

        self.user_purchase_user=mail_new_test_user(
            self.env,
            name='PaulinePoivraisselle',
            login='pauline',
            email='pur@example.com',
            notification_type='inbox',
            groups='purchase.group_purchase_user',
        )

        self.po_vals={
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product_id_1.name,
                    'product_id':self.product_id_1.id,
                    'product_qty':5.0,
                    'product_uom':self.product_id_1.uom_po_id.id,
                    'price_unit':500.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }

    deftest_00_create_picking(self):

        #Draftpurchaseordercreated
        self.po=self.env['purchase.order'].create(self.po_vals)
        self.assertTrue(self.po,'Purchase:nopurchaseordercreated')

        #Purchaseorderconfirm
        self.po.button_confirm()
        self.assertEqual(self.po.state,'purchase','Purchase:POstateshouldbe"Purchase')
        self.assertEqual(self.po.picking_count,1,'Purchase:onepickingshouldbecreated')
        self.assertEqual(len(self.po.order_line.move_ids),1,'Onemoveshouldbecreated')
        #Changepurchaseorderlineproductquantity
        self.po.order_line.write({'product_qty':7.0})
        self.assertEqual(len(self.po.order_line.move_ids),1,'Thetwomovesshouldbemergedinone')

        #Validatefirstshipment
        self.picking=self.po.picking_ids[0]
        formlinself.picking.move_line_ids:
            ml.qty_done=ml.product_uom_qty
        self.picking._action_done()
        self.assertEqual(self.po.order_line.mapped('qty_received'),[7.0],'Purchase:allproductsshouldbereceived')


        #createneworderline
        self.po.write({'order_line':[
            (0,0,{
                'name':self.product_id_2.name,
                'product_id':self.product_id_2.id,
                'product_qty':5.0,
                'product_uom':self.product_id_2.uom_po_id.id,
                'price_unit':250.0,
                'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })]})
        self.assertEqual(self.po.picking_count,2,'Newpickingshouldbecreated')
        moves=self.po.order_line.mapped('move_ids').filtered(lambdax:x.statenotin('done','cancel'))
        self.assertEqual(len(moves),1,'Onemovesshouldhavebeencreated')

    deftest_01_check_double_validation(self):

        #makedoublevalidationtwostep
        self.env.company.write({'po_double_validation':'two_step','po_double_validation_amount':2000.00})

        #Draftpurchaseordercreated
        self.po=self.env['purchase.order'].with_user(self.user_purchase_user).create(self.po_vals)
        self.assertTrue(self.po,'Purchase:nopurchaseordercreated')

        #Purchaseorderconfirm
        self.po.button_confirm()
        self.assertEqual(self.po.state,'toapprove','Purchase:POstateshouldbe"toapprove".')

        #POapprovedbymanager
        self.po.env.user.groups_id+=self.env.ref("purchase.group_purchase_manager")
        self.po.button_approve()
        self.assertEqual(self.po.state,'purchase','POstateshouldbe"Purchase".')

    deftest_02_check_mto_chain(self):
        """Simulateamtochainwithapurchaseorder.Cancelthe
        purchaseordershouldalsochangetheprocure_methodofthe
        followingmovetoMTSinordertobeabletolinkittoa
        manuallycreatedpurchaseorder.
        """
        stock_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_stock')
        customer_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_customers')
        #routebuyshouldbetherebydefault
        partner=self.env['res.partner'].create({
            'name':'Jhon'
        })

        vendor=self.env['res.partner'].create({
            'name':'Roger'
        })

        seller=self.env['product.supplierinfo'].create({
            'name':partner.id,
            'price':12.0,
        })

        product=self.env['product.product'].create({
            'name':'product',
            'type':'product',
            'route_ids':[(4,self.ref('stock.route_warehouse0_mto')),(4,self.ref('purchase_stock.route_warehouse0_buy'))],
            'seller_ids':[(6,0,[seller.id])],
            'categ_id':self.env.ref('product.product_category_all').id,
            'supplier_taxes_id':[(6,0,[])],
        })

        customer_move=self.env['stock.move'].create({
            'name':'moveout',
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':100.0,
            'procure_method':'make_to_order',
        })

        customer_move._action_confirm()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',partner.id)])
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        #Checkpurchaseorderlinedata.
        purchase_order_line=purchase_order.order_line
        self.assertEqual(purchase_order_line.product_id,product,'Theproductonthepurchaseorderlineisnotcorrect.')
        self.assertEqual(purchase_order_line.price_unit,seller.price,'Thepurchaseorderlinepriceshouldbethesameastheseller.')
        self.assertEqual(purchase_order_line.product_qty,customer_move.product_uom_qty,'Thepurchaseorderlineqtyshouldbethesameasthemove.')
        self.assertEqual(purchase_order_line.price_subtotal,1200.0,'Thepurchaseorderlinesubtotalshouldbeequaltothemoveqty*sellerprice.')

        purchase_order.button_cancel()
        self.assertEqual(purchase_order.state,'cancel','Purchaseordershouldbecancelled.')
        self.assertEqual(customer_move.procure_method,'make_to_stock','Customermoveshouldbepassedtomts.')

        purchase=purchase_order.create({
            'partner_id':vendor.id,
            'order_line':[
                (0,0,{
                    'name':product.name,
                    'product_id':product.id,
                    'product_qty':100.0,
                    'product_uom':product.uom_po_id.id,
                    'price_unit':11.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        })
        self.assertTrue(purchase,'RFQshouldbecreated')
        purchase.button_confirm()

        picking=purchase.picking_ids
        self.assertTrue(picking,'Pickingshouldbecreated')

        #Processpickings
        picking.action_confirm()
        picking.move_lines.quantity_done=100.0
        picking.button_validate()

        #mtsmovewillbeautomaticallyassigned
        self.assertEqual(customer_move.state,'assigned','Automaticallyassignedduetotheincomingmovemakesitavailable.')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(product,stock_location),0.0,'Wrongquantityinstock.')

    deftest_03_uom(self):
        """Buyadozenofproductsstockedinunits.Checkthatthequantitiesonthepurchaseorder
        linesaswellasthereceivedquantitiesarehandledindozenwhilethemovesthemselves
        arehandledinunits.Edittheorderedquantities,checkthatthequantitesarecorrectly
        updatedonthemoves.Edittheir.config_parametertopropagatetheuomofthepurchaseorder
        linestothemovesandeditalasttimetheorderedquantities.Receive,checkthequantities.
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_dozen=self.env.ref('uom.product_uom_dozen')

        self.assertEqual(self.product_id_1.uom_po_id.id,uom_unit.id)

        #buyadozen
        po=self.env['purchase.order'].create(self.po_vals)

        po.order_line.product_qty=1
        po.order_line.product_uom=uom_dozen.id
        po.button_confirm()

        #themoveshouldbe12units
        #note:move.product_qty=computedfield,alwaysintheuomofthequant
        #      move.product_uom_qty=storedfieldrepresentingtheinitialdemandinmove.product_uom
        move1=po.picking_ids.move_lines.sorted()[0]
        self.assertEqual(move1.product_uom_qty,12)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,12)

        #editthesoline,sell2dozen,themoveshouldnowbe24units
        po.order_line.product_qty=2
        move1=po.picking_ids.move_lines.sorted()[0]
        self.assertEqual(move1.product_uom_qty,24)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,24)

        #forcethepropagationoftheuom,sell3dozen
        self.env['ir.config_parameter'].sudo().set_param('stock.propagate_uom','1')
        po.order_line.product_qty=3
        move2=po.picking_ids.move_lines.filtered(lambdam:m.product_uom.id==uom_dozen.id)
        self.assertEqual(move2.product_uom_qty,1)
        self.assertEqual(move2.product_uom.id,uom_dozen.id)
        self.assertEqual(move2.product_qty,12)

        #delivereverything
        move1.quantity_done=24
        move2.quantity_done=1
        po.picking_ids.button_validate()

        #checkthedeliveredquantity
        self.assertEqual(po.order_line.qty_received,3.0)

    deftest_04_mto_multiple_po(self):
        """Simulateamtochainwith2purchaseorder.
        Createamovewithqty1,confirmtheRFQthencreateanew
        movethatwillnotbemergedinthefirstone(simulateanincrease
        orderquantityonaSO).ItshouldgenerateanewRFQ,validate
        andreceiptthepickingthentrytoreservethedelivery
        picking.
        """
        stock_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_stock')
        customer_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_customers')
        picking_type_out=self.env['ir.model.data'].xmlid_to_object('stock.picking_type_out')
        #routebuyshouldbetherebydefault
        partner=self.env['res.partner'].create({
            'name':'Jhon'
        })

        seller=self.env['product.supplierinfo'].create({
            'name':partner.id,
            'price':12.0,
        })

        product=self.env['product.product'].create({
            'name':'product',
            'type':'product',
            'route_ids':[(4,self.ref('stock.route_warehouse0_mto')),(4,self.ref('purchase_stock.route_warehouse0_buy'))],
            'seller_ids':[(6,0,[seller.id])],
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        #Apickingisrequiresinceonlymovesinsidethesamepickingaremerged.
        customer_picking=self.env['stock.picking'].create({
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':picking_type_out.id,
        })

        customer_move=self.env['stock.move'].create({
            'name':'moveout',
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':80.0,
            'procure_method':'make_to_order',
            'picking_id':customer_picking.id,
        })

        customer_move._action_confirm()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',partner.id)])
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        #Checkpurchaseorderlinedata.
        purchase_order_line=purchase_order.order_line
        self.assertEqual(purchase_order_line.product_id,product,'Theproductonthepurchaseorderlineisnotcorrect.')
        self.assertEqual(purchase_order_line.price_unit,seller.price,'Thepurchaseorderlinepriceshouldbethesameastheseller.')
        self.assertEqual(purchase_order_line.product_qty,customer_move.product_uom_qty,'Thepurchaseorderlineqtyshouldbethesameasthemove.')

        purchase_order.button_confirm()

        customer_move_2=self.env['stock.move'].create({
            'name':'moveout',
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':20.0,
            'procure_method':'make_to_order',
            'picking_id':customer_picking.id,
        })

        customer_move_2._action_confirm()

        self.assertTrue(customer_move_2.exists(),'Thesecondcustomermoveshouldnotbemergedinthefirst.')
        self.assertEqual(sum(customer_picking.move_lines.mapped('product_uom_qty')),100.0)

        purchase_order_2=self.env['purchase.order'].search([('partner_id','=',partner.id),('state','=','draft')])
        self.assertTrue(purchase_order_2,'Nopurchaseordercreated.')

        purchase_order_2.button_confirm()

        purchase_order.picking_ids.move_lines.quantity_done=80.0
        purchase_order.picking_ids.button_validate()

        purchase_order_2.picking_ids.move_lines.quantity_done=20.0
        purchase_order_2.picking_ids.button_validate()

        self.assertEqual(sum(customer_picking.move_lines.mapped('reserved_availability')),100.0,'Thetotalquantityforthecustomermoveshouldbeavailableandreserved.')

    deftest_04_rounding(self):
        """WesettheUnit(s)roundingto1.0andensurebuying1.2unitsinaPOisroundedto1.0
            atreception.
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_unit.rounding=1.0

        #buyadozen
        po=self.env['purchase.order'].create(self.po_vals)

        po.order_line.product_qty=1.2
        po.button_confirm()

        #themoveshouldbe1.0units
        move1=po.picking_ids.move_lines[0]
        self.assertEqual(move1.product_uom_qty,1.0)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,1.0)

        #editthesoline,buy2.4units,themoveshouldnowbe2.0units
        po.order_line.product_qty=2.0
        self.assertEqual(move1.product_uom_qty,2.0)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,2.0)

        #delivereverything
        move1.quantity_done=2.0
        po.picking_ids.button_validate()

        #checkthedeliveredquantity
        self.assertEqual(po.order_line.qty_received,2.0)

    deftest_05_uom_rounding(self):
        """WesettheUnit(s)andDozen(s)roundingto1.0andensurebuying1.3dozensinaPOis
            roundedto1.0atreception.
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_dozen=self.env.ref('uom.product_uom_dozen')
        uom_unit.rounding=1.0
        uom_dozen.rounding=1.0

        #buy1.3dozen
        po=self.env['purchase.order'].create(self.po_vals)

        po.order_line.product_qty=1.3
        po.order_line.product_uom=uom_dozen.id
        po.button_confirm()

        #themoveshouldbe16.0units
        move1=po.picking_ids.move_lines[0]
        self.assertEqual(move1.product_uom_qty,16.0)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,16.0)

        #forcethepropagationoftheuom,buy2.6dozens,themove2shouldhave2dozens
        self.env['ir.config_parameter'].sudo().set_param('stock.propagate_uom','1')
        po.order_line.product_qty=2.6
        move2=po.picking_ids.move_lines.filtered(lambdam:m.product_uom.id==uom_dozen.id)
        self.assertEqual(move2.product_uom_qty,2)
        self.assertEqual(move2.product_uom.id,uom_dozen.id)
        self.assertEqual(move2.product_qty,24)

    defcreate_delivery_order(self):
        stock_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_stock')
        customer_location=self.env['ir.model.data'].xmlid_to_object('stock.stock_location_customers')
        unit=self.ref("uom.product_uom_unit")
        picking_type_out=self.env['ir.model.data'].xmlid_to_object('stock.picking_type_out')
        partner=self.env['res.partner'].create({'name':'AAA','email':'from.test@example.com'})
        supplier_info1=self.env['product.supplierinfo'].create({
            'name':partner.id,
            'price':50,
        })

        warehouse1=self.env.ref('stock.warehouse0')
        route_buy=warehouse1.buy_pull_id.route_id
        route_mto=warehouse1.mto_pull_id.route_id

        product=self.env['product.product'].create({
            'name':'UsbKeyboard',
            'type':'product',
            'uom_id':unit,
            'uom_po_id':unit,
            'seller_ids':[(6,0,[supplier_info1.id])],
            'route_ids':[(6,0,[route_buy.id,route_mto.id])]
        })

        delivery_order=self.env['stock.picking'].create({
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'partner_id':partner.id,
            'picking_type_id':picking_type_out.id,
        })

        customer_move=self.env['stock.move'].create({
            'name':'moveout',
            'location_id':stock_location.id,
            'location_dest_id':customer_location.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':10.0,
            'procure_method':'make_to_order',
            'picking_id':delivery_order.id,
        })

        customer_move._action_confirm()
        #findcreatedpotheproduct
        purchase_order=self.env['purchase.order'].search([('partner_id','=',partner.id)])

        returndelivery_order,purchase_order

    deftest_05_propagate_deadline(self):
        """Inordertocheckdeadlinedateofthedeliveryorderischangedandtheplanneddatenot."""

        #CreateDeliveryOrderandwithpropagatedateandminimumdelta
        delivery_order,purchase_order=self.create_delivery_order()

        #checkpoiscreatedornot
        self.assertTrue(purchase_order,'Nopurchaseordercreated.')

        purchase_order_line=purchase_order.order_line

        #changescheduleddateofpoline.
        purchase_order_line.write({'date_planned':purchase_order_line.date_planned+timedelta(days=5)})

        #Nowcheckscheduleddateanddeadlineofdeliveryorder.
        self.assertNotEqual(
            purchase_order_line.date_planned,delivery_order.scheduled_date,
            'Scheduleddeliveryorderdateshouldnotchanged.')
        self.assertEqual(
            purchase_order_line.date_planned,delivery_order.date_deadline,
            'Deliverydeadlinedateshouldbechanged.')

    deftest_07_differed_schedule_date(self):
        warehouse=self.env['stock.warehouse'].search([],limit=1)

        withForm(warehouse)asw:
            w.reception_steps='three_steps'
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_id
        withpo_form.order_line.new()asline:
            line.product_id=self.product_id_1
            line.date_planned=datetime.today()
            line.product_qty=1.0
        withpo_form.order_line.new()asline:
            line.product_id=self.product_id_1
            line.date_planned=datetime.today()+timedelta(days=7)
            line.product_qty=1.0
        po=po_form.save()

        po.button_approve()

        po.picking_ids.move_line_ids.write({
            'qty_done':1.0
        })
        po.picking_ids.button_validate()

        pickings=self.env['stock.picking'].search([('group_id','=',po.group_id.id)])
        forpickinginpickings:
            self.assertEqual(picking.scheduled_date.date(),date.today())

    deftest_update_quantity_and_return(self):
        po=self.env['purchase.order'].create(self.po_vals)

        po.order_line.product_qty=10
        po.button_confirm()

        first_picking=po.picking_ids
        first_picking.move_lines.quantity_done=5
        #createthebackorder
        backorder_wizard_dict=first_picking.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertEqual(len(po.picking_ids),2)

        #Createapartialreturn
        stock_return_picking_form=Form(
            self.env['stock.return.picking'].with_context(
                active_ids=first_picking.ids,
                active_id=first_picking.ids[0],
                active_model='stock.picking'
            )
        )
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=2.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.action_assign()
        return_pick.move_lines.quantity_done=2
        return_pick._action_done()

        self.assertEqual(po.order_line.qty_received,3)

        po.order_line.product_qty+=2
        backorder=po.picking_ids.filtered(lambdapicking:picking.state=='assigned')
        self.assertEqual(backorder.move_lines.product_uom_qty,9)
