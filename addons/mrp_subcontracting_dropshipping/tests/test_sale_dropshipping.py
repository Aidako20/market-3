#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm

fromflectra.addons.mrp_subcontracting.tests.commonimportTestMrpSubcontractingCommon


classTestSaleDropshippingFlows(TestMrpSubcontractingCommon):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()

        cls.supplier=cls.env["res.partner"].create({"name":"Supplier"})
        cls.customer=cls.env["res.partner"].create({"name":"Customer"})
        cls.dropship_route=cls.env.ref('stock_dropshipping.route_drop_shipping')

    deftest_dropship_with_different_suppliers(self):
        """
        Supposeakitwith3componentssuppliedby3vendors
        Whendropshippingthiskit,if2componentsaredeliveredandifthelast
        pickingiscancelled,weshouldconsiderthekitasfullydelivered.
        """
        partners=self.env['res.partner'].create([{'name':'Vendor%s'%i}foriinrange(4)])
        compo01,compo02,compo03,kit=self.env['product.product'].create([{
            'name':name,
            'type':'consu',
            'route_ids':[(6,0,[self.dropship_route.id])],
            'seller_ids':[(0,0,{'name':seller.id})],
        }forname,sellerinzip(['Compo01','Compo02','Compo03','Kit'],partners)])

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo01.id,'product_qty':1}),
                (0,0,{'product_id':compo02.id,'product_qty':1}),
                (0,0,{'product_id':compo03.id,'product_qty':1}),
            ],
        })

        sale_order=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'picking_policy':'direct',
            'order_line':[
                (0,0,{'name':kit.name,'product_id':kit.id,'product_uom_qty':1}),
            ],
        })
        sale_order.action_confirm()
        self.assertEqual(sale_order.order_line.qty_delivered,0)

        purchase_orders=self.env['purchase.order'].search([('partner_id','in',partners.ids)])
        purchase_orders.button_confirm()
        self.assertEqual(sale_order.order_line.qty_delivered,0)

        #Deliverthefirstone
        picking=sale_order.picking_ids.filtered(lambdap:p.partner_id==partners[0])
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()
        self.assertEqual(sale_order.order_line.qty_delivered,0)

        #Deliverthethirdone
        picking=sale_order.picking_ids.filtered(lambdap:p.partner_id==partners[2])
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()
        self.assertEqual(sale_order.order_line.qty_delivered,0)

        #Cancelthesecondone
        sale_order.picking_ids[1].action_cancel()
        self.assertEqual(sale_order.order_line.qty_delivered,1)

    deftest_return_kit_and_delivered_qty(self):
        """
        Sellakitthankstothedropshippingroute,returnitthendeliveritagain
        Thedeliveredquantityshouldbecorrectlycomputed
        """
        compo,kit=self.env['product.product'].create([{
            'name':n,
            'type':'consu',
            'route_ids':[(6,0,[self.dropship_route.id])],
            'seller_ids':[(0,0,{'name':self.supplier.id})],
        }fornin['Compo','Kit']])

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo.id,'product_qty':1}),
            ],
        })

        sale_order=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'picking_policy':'direct',
            'order_line':[
                (0,0,{'name':kit.name,'product_id':kit.id,'product_uom_qty':1}),
            ],
        })
        sale_order.action_confirm()
        self.env['purchase.order'].search([],order='iddesc',limit=1).button_confirm()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0)

        picking=sale_order.picking_ids
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()
        self.assertEqual(sale_order.order_line.qty_delivered,1.0)

        forcasein['return','deliveragain']:
            delivered_before_case=1.0ifcase=='return'else0.0
            delivered_after_case=0.0ifcase=='return'else1.0
            return_form=Form(self.env['stock.return.picking'].with_context(active_ids=[picking.id],active_id=picking.id,active_model='stock.picking'))
            return_wizard=return_form.save()
            action=return_wizard.create_returns()
            picking=self.env['stock.picking'].browse(action['res_id'])
            self.assertEqual(sale_order.order_line.qty_delivered,delivered_before_case,"Incorrectdeliveredqtyforcase'%s'"%case)

            action=picking.button_validate()
            wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
            wizard.process()
            self.assertEqual(sale_order.order_line.qty_delivered,delivered_after_case,"Incorrectdeliveredqtyforcase'%s'"%case)

    deftest_partial_return_kit_and_delivered_qty(self):
        """
        Supposeakitwith4xthesamedropshippedcomponent
        Supposeacomplexdeliveryprocess:
            -Deliver2(withbackorder)
            -Return2
            -Deliver1(withbackorder)
            -Deliver1(process"done")
            -Deliver1(fromthereturn)
            -Deliver1(fromthereturn)
        Thetestcheckstheall-or-nothingpolicyofthedeliveredquantity
        Thisquantityshouldbe1.0afterthelastdelivery
        """
        compo,kit=self.env['product.product'].create([{
            'name':n,
            'type':'consu',
            'route_ids':[(6,0,[self.dropship_route.id])],
            'seller_ids':[(0,0,{'name':self.supplier.id})],
        }fornin['Compo','Kit']])

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo.id,'product_qty':4}),
            ],
        })

        sale_order=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'picking_policy':'direct',
            'order_line':[
                (0,0,{'name':kit.name,'product_id':kit.id,'product_uom_qty':1}),
            ],
        })
        sale_order.action_confirm()
        self.env['purchase.order'].search([],order='iddesc',limit=1).button_confirm()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0,"Deliveredcomponents:0/4")

        picking01=sale_order.picking_ids
        picking01.move_lines.quantity_done=2
        action=picking01.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0,"Deliveredcomponents:2/4")

        #Createareturnofpicking01(withbothcomponents)
        return_form=Form(self.env['stock.return.picking'].with_context(active_id=picking01.id,active_model='stock.picking'))
        wizard=return_form.save()
        wizard.product_return_moves.write({'quantity':2.0})
        res=wizard.create_returns()
        return01=self.env['stock.picking'].browse(res['res_id'])

        return01.move_lines.quantity_done=2
        return01.button_validate()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0,"Deliveredcomponents:0/4")

        picking02=picking01.backorder_ids
        picking02.move_lines.quantity_done=1
        action=picking02.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0,"Deliveredcomponents:1/4")

        picking03=picking02.backorder_ids
        picking03.move_lines.quantity_done=1
        picking03.button_validate()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0,"Deliveredcomponents:2/4")

        #Createareturnofreturn01(with1component)
        return_form=Form(self.env['stock.return.picking'].with_context(active_id=return01.id,active_model='stock.picking'))
        wizard=return_form.save()
        wizard.product_return_moves.write({'quantity':1.0})
        res=wizard.create_returns()
        picking04=self.env['stock.picking'].browse(res['res_id'])

        picking04.move_lines.quantity_done=1
        picking04.button_validate()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0,"Deliveredcomponents:3/4")

        #Createasecondreturnofreturn01(with1component,thelastone)
        return_form=Form(self.env['stock.return.picking'].with_context(active_id=return01.id,active_model='stock.picking'))
        wizard=return_form.save()
        wizard.product_return_moves.write({'quantity':1.0})
        res=wizard.create_returns()
        picking04=self.env['stock.picking'].browse(res['res_id'])

        picking04.move_lines.quantity_done=1
        picking04.button_validate()
        self.assertEqual(sale_order.order_line.qty_delivered,1,"Deliveredcomponents:4/4")

    deftest_cancelled_picking_and_delivered_qty(self):
        """
        ThedeliveredquantityshouldbezeroifallSMarecancelled
        """
        compo,kit=self.env['product.product'].create([{
            'name':n,
            'type':'consu',
            'route_ids':[(6,0,[self.dropship_route.id])],
            'seller_ids':[(0,0,{'name':self.supplier.id})],
        }fornin['Compo','Kit']])

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo.id,'product_qty':1}),
            ],
        })

        sale_order=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'picking_policy':'direct',
            'order_line':[
                (0,0,{'name':kit.name,'product_id':kit.id,'product_uom_qty':1}),
            ],
        })
        sale_order.action_confirm()
        self.env['purchase.order'].search([],order='iddesc',limit=1).button_confirm()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0)

        sale_order.picking_ids.action_cancel()
        self.assertEqual(sale_order.order_line.qty_delivered,0.0)

    deftest_sale_kit_with_dropshipped_component(self):
        """
        Thetestchecksthedeliveredquantityofakitwhenoneofthe
        componentsisdropshipped
        """
        compo01,compo02,kit=self.env['product.product'].create([{
            'name':n,
            'type':'consu',
        }fornin['compo01','compo02','superkit']])

        compo02.write({
            'route_ids':[(6,0,[self.dropship_route.id])],
            'seller_ids':[(0,0,{'name':self.supplier.id})],
        })

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo01.id,'product_qty':1}),
                (0,0,{'product_id':compo02.id,'product_qty':1}),
            ],
        })

        sale_order=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'picking_policy':'direct',
            'order_line':[
                (0,0,{'name':kit.name,'product_id':kit.id,'product_uom_qty':1}),
            ],
        })
        sale_order.action_confirm()
        self.env['purchase.order'].search([],order='iddesc',limit=1).button_confirm()

        sale_order.picking_ids.move_lines.quantity_done=1
        sale_order.picking_ids[0].button_validate()
        sale_order.picking_ids[1].button_validate()

        self.assertEqual(sale_order.order_line.qty_delivered,1.0)
