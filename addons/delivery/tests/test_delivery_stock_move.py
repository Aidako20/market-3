#-*-coding:utf-8-*-

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged,Form


@tagged('post_install','-at_install')
classStockMoveInvoice(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.ProductProduct=cls.env['product.product']
        cls.SaleOrder=cls.env['sale.order']
        cls.AccountJournal=cls.env['account.journal']

        cls.partner_18=cls.env['res.partner'].create({'name':'MyTestCustomer'})
        cls.pricelist_id=cls.env.ref('product.list0')
        cls.product_11=cls.env['product.product'].create({'name':'Aproducttodeliver'})
        cls.product_cable_management_box=cls.env['product.product'].create({
            'name':'Anotherproducttodeliver',
            'weight':1.0,
            'invoice_policy':'order',
        })
        cls.product_uom_unit=cls.env.ref('uom.product_uom_unit')
        cls.product_delivery_normal=cls.env['product.product'].create({
            'name':'NormalDeliveryCharges',
            'invoice_policy':'order',
            'type':'service',
            'list_price':10.0,
            'categ_id':cls.env.ref('delivery.product_category_deliveries').id,
        })
        cls.normal_delivery=cls.env['delivery.carrier'].create({
            'name':'NormalDeliveryCharges',
            'fixed_price':10,
            'delivery_type':'fixed',
            'product_id':cls.product_delivery_normal.id,
        })

    deftest_01_delivery_stock_move(self):
        #Testifthestoredfieldsofstockmovesarecomputedwithinvoicebeforedeliveryflow
        self.sale_prepaid=self.SaleOrder.create({
            'partner_id':self.partner_18.id,
            'partner_invoice_id':self.partner_18.id,
            'partner_shipping_id':self.partner_18.id,
            'pricelist_id':self.pricelist_id.id,
            'order_line':[(0,0,{
                'name':'CableManagementBox',
                'product_id':self.product_cable_management_box.id,
                'product_uom_qty':2,
                'product_uom':self.product_uom_unit.id,
                'price_unit':750.00,
            })],
        })

        #IadddeliverycostinSalesorder
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id':self.sale_prepaid.id,
            'default_carrier_id':self.normal_delivery.id,
        }))
        choose_delivery_carrier=delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        #IconfirmtheSO.
        self.sale_prepaid.action_confirm()
        self.sale_prepaid._create_invoices()

        #Icheckthattheinvoicewascreated
        self.assertEqual(len(self.sale_prepaid.invoice_ids),1,"Invoicenotcreated.")

        #Iconfirmtheinvoice

        self.invoice=self.sale_prepaid.invoice_ids
        self.invoice.action_post()

        #Ipaytheinvoice.
        self.journal=self.AccountJournal.search([('type','=','cash'),('company_id','=',self.sale_prepaid.company_id.id)],limit=1)

        register_payments=self.env['account.payment.register'].with_context(active_model='account.move',active_ids=self.invoice.ids).create({
            'journal_id':self.journal.id,
        })
        register_payments._create_payments()

        #ChecktheSOafterpayingtheinvoice
        self.assertNotEqual(self.sale_prepaid.invoice_count,0,'ordernotinvoiced')
        self.assertTrue(self.sale_prepaid.invoice_status=='invoiced','orderisnotinvoiced')
        self.assertEqual(len(self.sale_prepaid.picking_ids),1,'pickingsnotgenerated')

        #Checkthestockmoves
        moves=self.sale_prepaid.picking_ids.move_lines
        self.assertEqual(moves[0].product_qty,2,'wrongproduct_qty')
        self.assertEqual(moves[0].weight,2.0,'wrongmoveweight')

        #Ship
        moves.move_line_ids.write({'qty_done':2})
        self.picking=self.sale_prepaid.picking_ids._action_done()
        self.assertEqual(moves[0].move_line_ids.sale_price,1725.0,'wrongshippingvalue')

    deftest_02_delivery_stock_move(self):
        #TestifSNproductshipmentlinehasthecorrectamount
        self.product_cable_management_box.write({
            'tracking':'serial'
        })

        serial_numbers=self.env['stock.production.lot'].create([{
            'name':str(x),
            'product_id':self.product_cable_management_box.id,
            'company_id':self.env.company.id,
        }forxinrange(5)])
 

        self.sale_prepaid=self.SaleOrder.create({
            'partner_id':self.partner_18.id,
            'partner_invoice_id':self.partner_18.id,
            'partner_shipping_id':self.partner_18.id,
            'pricelist_id':self.pricelist_id.id,
            'order_line':[(0,0,{
                'name':'CableManagementBox',
                'product_id':self.product_cable_management_box.id,
                'product_uom_qty':2,
                'product_uom':self.product_uom_unit.id,
                'price_unit':750.00,
            })],
        })

        #IadddeliverycostinSalesorder
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id':self.sale_prepaid.id,
            'default_carrier_id':self.normal_delivery.id,
        }))
        choose_delivery_carrier=delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        #IconfirmtheSO.
        self.sale_prepaid.action_confirm()
        moves=self.sale_prepaid.picking_ids.move_lines
        #Ship
        forml,lotinzip(moves.move_line_ids,serial_numbers):
            ml.write({'qty_done':1,'lot_id':lot.id})
        self.picking=self.sale_prepaid.picking_ids._action_done()
        self.assertEqual(moves[0].move_line_ids[0].sale_price,862.5,'wrongshippingvalue')

    deftest_delivery_carrier_from_confirmed_so(self):
        """Testifaddingshippingmethodinsaleorderafterconfirmation
           willadditinpickingstoo"""

        sale_order=self.SaleOrder.create({
            "partner_id":self.partner_18.id,
            "partner_invoice_id":self.partner_18.id,
            "partner_shipping_id":self.partner_18.id,
            "order_line":[(0,0,{
                "name":"CableManagementBox",
                "product_id":self.product_cable_management_box.id,
                "product_uom_qty":2,
                "product_uom":self.product_uom_unit.id,
                "price_unit":750.00,
            })],
        })

        sale_order.action_confirm()
        sale_order.picking_ids.move_lines.quantity_done=2
        sale_order.picking_ids.button_validate()

        #Returnpicking
        return_form=Form(self.env["stock.return.picking"].with_context(active_id=sale_order.picking_ids.id,active_model="stock.picking"))
        return_wizard=return_form.save()
        action=return_wizard.create_returns()
        return_picking=self.env["stock.picking"].browse(action["res_id"])

        #addnewproductsonewpickingiscreated
        sale_order.write({
            "order_line":[(0,0,{
                "name":"Anotherproducttodeliver",
                "product_id":self.product_11.id,
                "product_uom_qty":2,
                "product_uom":self.product_uom_unit.id,
                "price_unit":750.00,
            })],
        })

        #AdddeliverycostinSalesorder
        delivery_wizard=Form(self.env["choose.delivery.carrier"].with_context({
            "default_order_id":sale_order.id,
            "default_carrier_id":self.normal_delivery.id,
        }))
        choose_delivery_carrier=delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        #Checkthecarrierinpickingafterconfirmsaleorder
        delivery_for_product_11=sale_order.picking_ids.filtered(lambdap:self.product_11inp.move_lines.product_id)
        self.assertEqual(delivery_for_product_11.carrier_id,self.normal_delivery,"Theshippingmethodshouldbesetinpendingdeliveries.")

        done_delivery=sale_order.picking_ids.filtered(lambdap:p.state=="done")
        self.assertFalse(done_delivery.carrier_id.id,"Theshippingmethodshouldnotbesetindonedeliveries.")
        self.assertFalse(return_picking.carrier_id.id,"Theshippingmethodshouldnotsetinreturnpickings")
