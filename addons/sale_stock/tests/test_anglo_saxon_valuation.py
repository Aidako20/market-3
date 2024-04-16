#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm,tagged
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.exceptionsimportUserError


@tagged('post_install','-at_install')
classTestAngloSaxonValuation(ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.env.user.company_id.anglo_saxon_accounting=True

        cls.product=cls.env['product.product'].create({
            'name':'product',
            'type':'product',
            'categ_id':cls.stock_account_product_categ.id,
        })

    def_inv_adj_two_units(self):
        inventory=self.env['stock.inventory'].create({
            'name':'test',
            'location_ids':[(4,self.company_data['default_warehouse'].lot_stock_id.id)],
            'product_ids':[(4,self.product.id)],
        })
        inventory.action_start()
        self.env['stock.inventory.line'].create({
            'inventory_id':inventory.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_id':self.product.id,
            'product_qty':2,
        })
        inventory.action_validate()

    def_so_and_confirm_two_units(self):
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':2.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':12,
                    'tax_id':False, #nolovetaxesamls
                })],
        })
        sale_order.action_confirm()
        returnsale_order

    def_fifo_in_one_eight_one_ten(self):
        #Puttwoitemsinstock.
        in_move_1=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':8,
        })
        in_move_1._action_confirm()
        in_move_1.quantity_done=1
        in_move_1._action_done()
        in_move_2=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':10,
        })
        in_move_2._action_confirm()
        in_move_2.quantity_done=1
        in_move_2._action_done()

    #-------------------------------------------------------------------------
    #StandardOrdered
    #-------------------------------------------------------------------------
    deftest_standard_ordered_invoice_pre_delivery(self):
        """Standardpricesetto10.Get2unitsinstock.Saleorder2@12.Standardpriceset
        to14.Invoice2withoutdelivering.TheamountinStockOUTandCOGSshouldbe14*2.
        """
        self.product.categ_id.property_cost_method='standard'
        self.product.invoice_policy='order'
        self.product.standard_price=10.0

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #standardpriceto14
        self.product.standard_price=14.0

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,28)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,28)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_standard_ordered_invoice_post_partial_delivery_1(self):
        """Standardpricesetto10.Get2unitsinstock.Saleorder2@12.Deliver1,invoice1,
        changethestandardpriceto14,deliverone,changethestandardpriceto16,invoice1.
        TheamountsusedinStockOUTandCOGSshouldbe10then14."""
        self.product.categ_id.property_cost_method='standard'
        self.product.invoice_policy='order'
        self.product.standard_price=10.0

        #Puttwoitemsinstock.
        sale_order=self._so_and_confirm_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #Invoice1
        invoice=sale_order._create_invoices()
        invoice_form=Form(invoice)
        withinvoice_form.invoice_line_ids.edit(0)asinvoice_line:
            invoice_line.quantity=1
        invoice_form.save()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,10)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,10)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,12)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,12)

        #changethestandardpriceto14
        self.product.standard_price=14.0

        #deliverthebackorder
        sale_order.picking_ids[0].move_lines.quantity_done=1
        sale_order.picking_ids[0].button_validate()

        #changethestandardpriceto16
        self.product.standard_price=16.0

        #invoice1
        invoice2=sale_order._create_invoices()
        invoice2.action_post()
        amls=invoice2.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,14)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,14)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,12)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,12)

    deftest_standard_ordered_invoice_post_delivery(self):
        """Standardpricesetto10.Get2unitsinstock.Saleorder2@12.Deliver1,changethe
        standardpriceto14,deliverone,invoice2.TheamountsusedinStockOUTandCOGSshould
        be12*2."""
        self.product.categ_id.property_cost_method='standard'
        self.product.invoice_policy='order'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #changethestandardpriceto14
        self.product.standard_price=14.0

        #deliverthebackorder
        sale_order.picking_ids.filtered('backorder_id').move_lines.quantity_done=1
        sale_order.picking_ids.filtered('backorder_id').button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,24)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,24)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    #-------------------------------------------------------------------------
    #StandardDelivered
    #-------------------------------------------------------------------------
    deftest_standard_delivered_invoice_pre_delivery(self):
        """Notpossibletoinvoicepredelivery."""
        self.product.categ_id.property_cost_method='standard'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Invoicethesaleorder.
        #Nothingdelivered=nothingtoinvoice.
        withself.assertRaises(UserError):
            sale_order._create_invoices()

    deftest_standard_delivered_invoice_post_partial_delivery(self):
        """Standardpricesetto10.Get2unitsinstock.Saleorder2@12.Deliver1,invoice1,
        changethestandardpriceto14,deliverone,changethestandardpriceto16,invoice1.
        TheamountsusedinStockOUTandCOGSshouldbe10then14."""
        self.product.categ_id.property_cost_method='standard'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        sale_order=self._so_and_confirm_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #Invoice1
        invoice=sale_order._create_invoices()
        invoice_form=Form(invoice)
        withinvoice_form.invoice_line_ids.edit(0)asinvoice_line:
            invoice_line.quantity=1
        invoice_form.save()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,10)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,10)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,12)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,12)

        #changethestandardpriceto14
        self.product.standard_price=14.0

        #deliverthebackorder
        sale_order.picking_ids[0].move_lines.quantity_done=1
        sale_order.picking_ids[0].button_validate()

        #changethestandardpriceto16
        self.product.standard_price=16.0

        #invoice1
        invoice2=sale_order._create_invoices()
        invoice2.action_post()
        amls=invoice2.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,14)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,14)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,12)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,12)

    deftest_standard_delivered_invoice_post_delivery(self):
        """Standardpricesetto10.Get2unitsinstock.Saleorder2@12.Deliver1,changethe
        standardpriceto14,deliverone,invoice2.TheamountsusedinStockOUTandCOGSshould
        be12*2."""
        self.product.categ_id.property_cost_method='standard'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #changethestandardpriceto14
        self.product.standard_price=14.0

        #deliverthebackorder
        sale_order.picking_ids.filtered('backorder_id').move_lines.quantity_done=1
        sale_order.picking_ids.filtered('backorder_id').button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,24)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,24)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    #-------------------------------------------------------------------------
    #AVCOOrdered
    #-------------------------------------------------------------------------
    deftest_avco_ordered_invoice_pre_delivery(self):
        """Standardpricesetto10.Saleorder2@12.Invoicewithoutdelivering."""
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='order'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,20)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,20)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_avco_ordered_invoice_post_partial_delivery(self):
        """Standardpricesetto10.Saleorder2@12.Invoiceafterdelivering1."""
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='order'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,20)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,20)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_avco_ordered_invoice_post_delivery(self):
        """Standardpricesetto10.Saleorder2@12.Invoiceafterfulldelivery."""
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='order'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=2
        sale_order.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,20)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,20)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_avco_ordered_return_and_receipt(self):
        """Sellanddeliversomeproductsbeforetheuserencodestheproductsreceipt"""
        product=self.product
        product.invoice_policy='order'
        product.type='product'
        product.categ_id.property_cost_method='average'
        product.categ_id.property_valuation='real_time'
        product.list_price=100
        product.standard_price=50

        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':5.0,
                'product_uom':product.uom_id.id,
                'price_unit':product.list_price})],
        })
        so.action_confirm()

        pick=so.picking_ids
        pick.move_lines.write({'quantity_done':5})
        pick.button_validate()

        product.standard_price=40

        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=pick.ids,active_id=pick.sorted().ids[0],active_model='stock.picking'))
        return_wiz=stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity=1
        return_wiz.product_return_moves.to_refund=False
        res=return_wiz.create_returns()

        return_pick=self.env['stock.picking'].browse(res['res_id'])
        return_pick.move_lines.write({'quantity_done':1})
        return_pick.button_validate()

        picking=self.env['stock.picking'].create({
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'picking_type_id':self.company_data['default_warehouse'].in_type_id.id,
        })
        #Wedon'tsettheprice_unitsothatthe`standard_price`willbeused(see_get_price_unit()):
        self.env['stock.move'].create({
            'name':'test_immediate_validate_1',
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'picking_id':picking.id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'quantity_done':1,
        })
        picking.button_validate()

        invoice=so._create_invoices()
        invoice.action_post()
        self.assertEqual(invoice.state,'posted')

    #-------------------------------------------------------------------------
    #AVCODelivered
    #-------------------------------------------------------------------------
    deftest_avco_delivered_invoice_pre_delivery(self):
        """Standardpricesetto10.Saleorder2@12.Invoicewithoutdelivering."""
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Invoicethesaleorder.
        #Nothingdelivered=nothingtoinvoice.
        withself.assertRaises(UserError):
            sale_order._create_invoices()

    deftest_avco_delivered_invoice_post_partial_delivery(self):
        """Standardpricesetto10.Saleorder2@12.Invoiceafterdelivering1."""
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,10)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,10)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,12)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,12)

    deftest_avco_delivered_invoice_post_delivery(self):
        """Standardpricesetto10.Saleorder2@12.Invoiceafterfulldelivery."""
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        #Puttwoitemsinstock.
        self._inv_adj_two_units()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()
        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=2
        sale_order.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,20)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,20)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_avco_partially_owned_and_delivered_invoice_post_delivery(self):
        """
        Standardpricesetto10.Saleorder2@12.Oneofthedelivered
        productswasownedbyanexternalpartner.Invoiceafterfulldelivery.
        """
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        self.env['stock.quant']._update_available_quantity(self.product,self.company_data['default_warehouse'].lot_stock_id,1,owner_id=self.partner_b)
        self.env['stock.quant']._update_available_quantity(self.product,self.company_data['default_warehouse'].lot_stock_id,1)

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()
        #Deliverbothproducts(thereshouldbetwoSML)
        sale_order.picking_ids.move_line_ids.qty_done=1
        sale_order.picking_ids.button_validate()

        #Invoiceonebyone
        invoice01=sale_order._create_invoices()
        withForm(invoice01)asinvoice_form:
            withinvoice_form.invoice_line_ids.edit(0)asline_form:
                line_form.quantity=1
        invoice01.action_post()

        invoice02=sale_order._create_invoices()
        invoice02.action_post()

        #COGSshouldignoretheownedproduct
        self.assertRecordValues(invoice01.line_ids,[
            #pylint:disable=bad-whitespace
            {'account_id':self.company_data['default_account_revenue'].id,    'debit':0,    'credit':12},
            {'account_id':self.company_data['default_account_receivable'].id, 'debit':12,   'credit':0},
            {'account_id':self.company_data['default_account_stock_out'].id,  'debit':0,    'credit':10},
            {'account_id':self.company_data['default_account_expense'].id,    'debit':10,   'credit':0},
        ])
        self.assertRecordValues(invoice02.line_ids,[
            #pylint:disable=bad-whitespace
            {'account_id':self.company_data['default_account_revenue'].id,    'debit':0,    'credit':12},
            {'account_id':self.company_data['default_account_receivable'].id, 'debit':12,   'credit':0},
        ])

    deftest_avco_fully_owned_and_delivered_invoice_post_delivery(self):
        """
        Standardpricesetto10.Saleorder2@12.Theproductsareownedbyan
        externalpartner.Invoiceafterfulldelivery.
        """
        self.product.categ_id.property_cost_method='average'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        self.env['stock.quant']._update_available_quantity(self.product,self.company_data['default_warehouse'].lot_stock_id,2,owner_id=self.partner_b)

        sale_order=self._so_and_confirm_two_units()
        sale_order.picking_ids.move_line_ids.qty_done=2
        sale_order.picking_ids.button_validate()

        invoice=sale_order._create_invoices()
        invoice.action_post()

        #COGSshouldnotexistbecausetheproductsareownedbyanexternalpartner
        amls=invoice.line_ids
        self.assertRecordValues(amls,[
            #pylint:disable=bad-whitespace
            {'account_id':self.company_data['default_account_revenue'].id,    'debit':0,    'credit':24},
            {'account_id':self.company_data['default_account_receivable'].id, 'debit':24,   'credit':0},
        ])

    #-------------------------------------------------------------------------
    #FIFOOrdered
    #-------------------------------------------------------------------------
    deftest_fifo_ordered_invoice_pre_delivery(self):
        """Receiveat8thenat10.Saleorder2@12.Invoicewithoutdelivering.
        Asnostandardpriceisset,theStockOUTandCOGSamountsare0."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='order'

        self._fifo_in_one_eight_one_ten()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertAlmostEqual(stock_out_aml.credit,16)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertAlmostEqual(cogs_aml.debit,16)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_fifo_ordered_invoice_post_partial_delivery(self):
        """Receive1@8,1@10,so2@12,standardprice12,deliver1,invoice2:theCOGSamount
        shouldbe20:1reallydeliveredat10andtheothervaluedatthestandardprice10."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='order'

        self._fifo_in_one_eight_one_ten()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #upatethestandardpriceto12
        self.product.standard_price=12

        #Invoice2
        invoice=sale_order._create_invoices()
        invoice_form=Form(invoice)
        withinvoice_form.invoice_line_ids.edit(0)asinvoice_line:
            invoice_line.quantity=2
        invoice_form.save()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,20)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,20)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_fifo_ordered_invoice_post_delivery(self):
        """Receiveat8thenat10.Saleorder2@12.Invoiceafterdeliveringeverything."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='order'

        self._fifo_in_one_eight_one_ten()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=2
        sale_order.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,18)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,18)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    #-------------------------------------------------------------------------
    #FIFODelivered
    #-------------------------------------------------------------------------
    deftest_fifo_delivered_invoice_pre_delivery(self):
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        self._fifo_in_one_eight_one_ten()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Invoicethesaleorder.
        #Nothingdelivered=nothingtoinvoice.
        withself.assertRaises(UserError):
            invoice_id=sale_order._create_invoices()

    deftest_fifo_delivered_invoice_post_partial_delivery(self):
        """Receive1@8,1@10,so2@12,standardprice12,deliver1,invoice2:thepriceusedshouldbe10:
        oneat8andoneat10."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'

        self._fifo_in_one_eight_one_ten()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=1
        wiz=sale_order.picking_ids.button_validate()
        wiz=Form(self.env[wiz['res_model']].with_context(wiz['context'])).save()
        wiz.process()

        #upatethestandardpriceto12
        self.product.standard_price=12

        #Invoice2
        invoice=sale_order._create_invoices()
        invoice_form=Form(invoice)
        withinvoice_form.invoice_line_ids.edit(0)asinvoice_line:
            invoice_line.quantity=2
        invoice_form.save()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,20)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,20)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_fifo_delivered_invoice_post_delivery(self):
        """Receiveat8thenat10.Saleorder2@12.Invoiceafterdeliveringeverything."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        self._fifo_in_one_eight_one_ten()

        #Createandconfirmasaleorderfor2@12
        sale_order=self._so_and_confirm_two_units()

        #Deliverone.
        sale_order.picking_ids.move_lines.quantity_done=2
        sale_order.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,18)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,18)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,24)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,24)

    deftest_fifo_delivered_invoice_post_delivery_2(self):
        """Receiveat8thenat10.Saleorder10@12anddeliverwithoutreceivingthe2missing.
        receive2@12.Invoice."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        in_move_1=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':8,
            'price_unit':10,
        })
        in_move_1._action_confirm()
        in_move_1.quantity_done=8
        in_move_1._action_done()

        #Createandconfirmasaleorderfor2@12
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':10.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':12,
                    'tax_id':False, #nolovetaxesamls
                })],
        })
        sale_order.action_confirm()

        #Deliver10
        sale_order.picking_ids.move_lines.quantity_done=10
        sale_order.picking_ids.button_validate()

        #Makethesecondreceipt
        in_move_2=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':2,
            'price_unit':12,
        })
        in_move_2._action_confirm()
        in_move_2.quantity_done=2
        in_move_2._action_done()
        self.assertEqual(self.product.stock_valuation_layer_ids[-1].value,-4) #wesenttwoat10buttheyshouldhavebeensentat12
        self.assertEqual(self.product.stock_valuation_layer_ids[-1].quantity,0)
        self.assertEqual(sale_order.order_line.move_ids.stock_valuation_layer_ids[-1].quantity,0)

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,104)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,104)
        self.assertEqual(cogs_aml.credit,0)
        receivable_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml.debit,120)
        self.assertEqual(receivable_aml.credit,0)
        income_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml.debit,0)
        self.assertEqual(income_aml.credit,120)

    deftest_fifo_delivered_invoice_post_delivery_3(self):
        """Receive5@8,receive8@12,sale1@20,deliver,sale6@20,deliver.Makesurenorouding
        issuesappearonthesecondinvoice."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'

        #+5@8
        in_move_1=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':5,
            'price_unit':8,
        })
        in_move_1._action_confirm()
        in_move_1.quantity_done=5
        in_move_1._action_done()

        #+8@12
        in_move_2=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':8,
            'price_unit':12,
        })
        in_move_2._action_confirm()
        in_move_2.quantity_done=8
        in_move_2._action_done()

        #sale1@20,deliver,invoice
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':1,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':20,
                    'tax_id':False,
                })],
        })
        sale_order.action_confirm()
        sale_order.picking_ids.move_lines.quantity_done=1
        sale_order.picking_ids.button_validate()
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #sale6@20,deliver,invoice
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':6,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':20,
                    'tax_id':False,
                })],
        })
        sale_order.action_confirm()
        sale_order.picking_ids.move_lines.quantity_done=6
        sale_order.picking_ids.button_validate()
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #checkthelastanglosaxoninvoiceline
        amls=invoice.line_ids
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,56)
        self.assertEqual(cogs_aml.credit,0)

    deftest_fifo_delivered_invoice_post_delivery_4(self):
        """Receive8@10.Saleorder10@12.Deliverandalsoinvoiceitwithoutreceivingthe2missing.
        Now,receive2@12.Makesurepricedifferenceiscorrectlyreflectedinexpenseaccount."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'
        self.product.standard_price=10

        in_move_1=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':8,
            'price_unit':10,
        })
        in_move_1._action_confirm()
        in_move_1.quantity_done=8
        in_move_1._action_done()

        #Createandconfirmasaleorderfor10@12
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':10.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':12,
                    'tax_id':False, #nolovetaxesamls
                })],
        })
        sale_order.action_confirm()

        #Deliver10
        sale_order.picking_ids.move_lines.quantity_done=10
        sale_order.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice=sale_order._create_invoices()
        invoice.action_post()

        #Makethesecondreceipt
        in_move_2=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':2,
            'price_unit':12,
        })
        in_move_2._action_confirm()
        in_move_2.quantity_done=2
        in_move_2._action_done()

        #checkthelastanglosaxonmoveline
        revalued_anglo_expense_amls=sale_order.picking_ids.mapped('move_lines.stock_valuation_layer_ids')[-1].stock_move_id.account_move_ids[-1].mapped('line_ids')
        revalued_cogs_aml=revalued_anglo_expense_amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(revalued_cogs_aml.debit,4,'Pricedifferenceshouldhavecorrectlyreflectedinexpenseaccount.')

    deftest_fifo_delivered_invoice_post_delivery_with_return(self):
        """Receive2@10.SO12@12.Return1fromSO1.SO21@12.Receive1@20.
        Re-deliverreturnedfromSO1.Invoiceafterdeliveringeverything."""
        self.product.categ_id.property_cost_method='fifo'
        self.product.invoice_policy='delivery'

        #Receive2@10.
        in_move_1=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':2,
            'price_unit':10,
        })
        in_move_1._action_confirm()
        in_move_1.quantity_done=2
        in_move_1._action_done()

        #Create,confirmanddeliverasaleorderfor2@12(SO1)
        so_1=self._so_and_confirm_two_units()
        so_1.picking_ids.move_lines.quantity_done=2
        so_1.picking_ids.button_validate()

        #Return1fromSO1
        stock_return_picking_form=Form(
            self.env['stock.return.picking'].with_context(
                active_ids=so_1.picking_ids.ids,active_id=so_1.picking_ids.ids[0],active_model='stock.picking')
        )
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=1.0
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.action_assign()
        return_pick.move_lines.quantity_done=1
        return_pick._action_done()

        #Create,confirmanddeliverasaleorderfor1@12(SO2)
        so_2=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':1.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':12,
                    'tax_id':False, #nolovetaxesamls
                })],
        })
        so_2.action_confirm()
        so_2.picking_ids.move_lines.quantity_done=1
        so_2.picking_ids.button_validate()

        #Receive1@20
        in_move_2=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':20,
        })
        in_move_2._action_confirm()
        in_move_2.quantity_done=1
        in_move_2._action_done()

        #Re-deliverreturned1fromSO1
        stock_redeliver_picking_form=Form(
            self.env['stock.return.picking'].with_context(
                active_ids=return_pick.ids,active_id=return_pick.ids[0],active_model='stock.picking')
        )
        stock_redeliver_picking=stock_redeliver_picking_form.save()
        stock_redeliver_picking.product_return_moves.quantity=1.0
        stock_redeliver_picking_action=stock_redeliver_picking.create_returns()
        redeliver_pick=self.env['stock.picking'].browse(stock_redeliver_picking_action['res_id'])
        redeliver_pick.action_assign()
        redeliver_pick.move_lines.quantity_done=1
        redeliver_pick._action_done()

        #Invoicethesaleorders
        invoice_1=so_1._create_invoices()
        invoice_1.action_post()
        invoice_2=so_2._create_invoices()
        invoice_2.action_post()

        #Checktheresultingaccountingentries
        amls_1=invoice_1.line_ids
        self.assertEqual(len(amls_1),4)
        stock_out_aml_1=amls_1.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml_1.debit,0)
        self.assertEqual(stock_out_aml_1.credit,30)
        cogs_aml_1=amls_1.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml_1.debit,30)
        self.assertEqual(cogs_aml_1.credit,0)
        receivable_aml_1=amls_1.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml_1.debit,24)
        self.assertEqual(receivable_aml_1.credit,0)
        income_aml_1=amls_1.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml_1.debit,0)
        self.assertEqual(income_aml_1.credit,24)

        amls_2=invoice_2.line_ids
        self.assertEqual(len(amls_2),4)
        stock_out_aml_2=amls_2.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml_2.debit,0)
        self.assertEqual(stock_out_aml_2.credit,10)
        cogs_aml_2=amls_2.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml_2.debit,10)
        self.assertEqual(cogs_aml_2.credit,0)
        receivable_aml_2=amls_2.filtered(lambdaaml:aml.account_id==self.company_data['default_account_receivable'])
        self.assertEqual(receivable_aml_2.debit,12)
        self.assertEqual(receivable_aml_2.credit,0)
        income_aml_2=amls_2.filtered(lambdaaml:aml.account_id==self.company_data['default_account_revenue'])
        self.assertEqual(income_aml_2.debit,0)
        self.assertEqual(income_aml_2.credit,12)

    deftest_fifo_uom_computation(self):
        self.env.company.anglo_saxon_accounting=True
        self.product.categ_id.property_cost_method='fifo'
        self.product.categ_id.property_valuation='real_time'
        quantity=50.0
        self.product.list_price=1.5
        self.product.standard_price=2.0
        unit_12=self.env['uom.uom'].create({
            'name':'Packof12units',
            'category_id':self.product.uom_id.category_id.id,
            'uom_type':'bigger',
            'factor_inv':12,
            'rounding':1,
        })

        #Create,confirmanddeliverasaleorderfor12@1.5withoutreceptionwithstd_price=2.0(SO1)
        so_1=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':1,
                    'product_uom':unit_12.id,
                    'price_unit':18,
                    'tax_id':False, #nolovetaxesamls
                })],
        })
        so_1.action_confirm()
        so_1.picking_ids.move_lines.quantity_done=12
        so_1.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice_1=so_1._create_invoices()
        invoice_1.action_post()
        """
        Invoice1

        CorrectJournalItems

        Name                           Debit      Credit

        ProductSales                   0.00$     18.00$
        AccountReceivable             18.00$      0.00$
        DefaultAccountStockOut       0.00$     24.00$
        Expenses                       24.00$      0.00$
        """
        aml=invoice_1.line_ids
        #ProductSales
        self.assertEqual(aml[0].debit,  0,0)
        self.assertEqual(aml[0].credit,18,0)
        #AccountReceivable
        self.assertEqual(aml[1].debit, 18,0)
        self.assertEqual(aml[1].credit, 0,0)
        #DefaultAccountStockOut
        self.assertEqual(aml[2].debit,  0,0)
        self.assertEqual(aml[2].credit,24,0)
        #Expenses
        self.assertEqual(aml[3].debit, 24,0)
        self.assertEqual(aml[3].credit, 0,0)

        #Createstockmove1
        in_move_1=self.env['stock.move'].create({
            'name':'a',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':quantity,
            'price_unit':1.0,
        })
        in_move_1._action_confirm()
        in_move_1.quantity_done=quantity
        in_move_1._action_done()

        #Create,confirmanddeliverasaleorderfor12@1.5withreception(50*1.0,50*0.0)(SO2)
        so_2=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':1,
                    'product_uom':unit_12.id,
                    'price_unit':18,
                    'tax_id':False, #nolovetaxesamls
                })],
        })
        so_2.action_confirm()
        so_2.picking_ids.move_lines.quantity_done=12
        so_2.picking_ids.button_validate()

        #Invoicethesaleorder.
        invoice_2=so_2._create_invoices()
        invoice_2.action_post()

        """
        Invoice2

        CorrectJournalItems

        Name                           Debit      Credit

        ProductSales                   0.00$      18.0$
        AccountReceivable             18.00$       0.0$
        DefaultAccountStockOut       0.00$      12.0$
        Expenses                       12.00$       0.0$
        """
        aml=invoice_2.line_ids
        #ProductSales
        self.assertEqual(aml[0].debit,  0,0)
        self.assertEqual(aml[0].credit,18,0)
        #AccountReceivable
        self.assertEqual(aml[1].debit, 18,0)
        self.assertEqual(aml[1].credit, 0,0)
        #DefaultAccountStockOut
        self.assertEqual(aml[2].debit,  0,0)
        self.assertEqual(aml[2].credit,12,0)
        #Expenses
        self.assertEqual(aml[3].debit, 12,0)
        self.assertEqual(aml[3].credit, 0,0)

    deftest_fifo_return_and_credit_note(self):
        """
        Whenpostingacreditnoteforareturnedproduct,thevalueoftheanglo-saxolines
        shouldbebasedonthereturnedproduct'svalue
        """
        self.product.categ_id.property_cost_method='fifo'

        #Receiveone@10,one@20andone@60
        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpin[10,20,60]])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Sell3units
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':3.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        #Deliver1@10,then1@20andthen1@60
        pickings=[]
        picking=so.picking_ids
        whilepicking:
            pickings.append(picking)
            picking.move_lines.quantity_done=1
            action=picking.button_validate()
            ifisinstance(action,dict):
                wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
                wizard.process()
            picking=picking.backorder_ids

        invoice=so._create_invoices()
        invoice.action_post()

        #Receiveone@100
        in_moves=self.env['stock.move'].create({
            'name':'INmove@100',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':100,
        })
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Returnthesecondpicking(i.e.1@20)
        ctx={'active_id':pickings[1].id,'active_model':'stock.picking'}
        return_wizard=Form(self.env['stock.return.picking'].with_context(ctx)).save()
        return_picking_id,dummy=return_wizard._create_returns()
        return_picking=self.env['stock.picking'].browse(return_picking_id)
        return_picking.move_lines.quantity_done=1
        return_picking.button_validate()

        #Addacreditnoteforthereturnedproduct
        ctx={'active_model':'account.move','active_ids':invoice.ids}
        refund_wizard=self.env['account.move.reversal'].with_context(ctx).create({'refund_method':'refund'})
        action=refund_wizard.reverse_moves()
        reverse_invoice=self.env['account.move'].browse(action['res_id'])
        withForm(reverse_invoice)asreverse_invoice_form:
            withreverse_invoice_form.invoice_line_ids.edit(0)asline:
                line.quantity=1
        reverse_invoice.action_post()

        amls=reverse_invoice.line_ids
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,20,'Shouldbetothevalueofthereturnedproduct')
        self.assertEqual(stock_out_aml.credit,0)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,0)
        self.assertEqual(cogs_aml.credit,20,'Shouldbetothevalueofthereturnedproduct')

    deftest_fifo_return_and_create_invoice(self):
        """
        Whencreatinganinvoiceforareturnedproduct,thevalueoftheanglo-saxolines
        shouldbebasedonthereturnedproduct'svalue
        """
        self.product.categ_id.property_cost_method='fifo'

        #Receiveone@10,one@20andone@60
        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpin[10,20,60]])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Sell3units
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':3.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        #Deliver1@10,then1@20andthen1@60
        pickings=[]
        picking=so.picking_ids
        whilepicking:
            pickings.append(picking)
            picking.move_lines.quantity_done=1
            action=picking.button_validate()
            ifisinstance(action,dict):
                wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
                wizard.process()
            picking=picking.backorder_ids

        invoice=so._create_invoices()
        invoice.action_post()

        #Receiveone@100
        in_moves=self.env['stock.move'].create({
            'name':'INmove@100',
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':100,
        })
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Returnthesecondpicking(i.e.1@20)
        ctx={'active_id':pickings[1].id,'active_model':'stock.picking'}
        return_wizard=Form(self.env['stock.return.picking'].with_context(ctx)).save()
        return_picking_id,dummy=return_wizard._create_returns()
        return_picking=self.env['stock.picking'].browse(return_picking_id)
        return_picking.move_lines.quantity_done=1
        return_picking.button_validate()

        #Createanewinvoiceforthereturnedproduct
        ctx={'active_model':'sale.order','active_ids':so.ids}
        create_invoice_wizard=self.env['sale.advance.payment.inv'].with_context(ctx).create({'advance_payment_method':'delivered'})
        create_invoice_wizard.create_invoices()
        reverse_invoice=so.invoice_ids[-1]
        withForm(reverse_invoice)asreverse_invoice_form:
            withreverse_invoice_form.invoice_line_ids.edit(0)asline:
                line.quantity=1
        reverse_invoice.action_post()

        amls=reverse_invoice.line_ids
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,20,'Shouldbetothevalueofthereturnedproduct')
        self.assertEqual(stock_out_aml.credit,0)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,0)
        self.assertEqual(cogs_aml.credit,20,'Shouldbetothevalueofthereturnedproduct')

    deftest_fifo_several_invoices_reset_repost(self):
        self.product.categ_id.property_cost_method='fifo'

        svl_values=[10,15,65]
        total_value=sum(svl_values)
        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpinsvl_values])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':3.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        #Deliveronebyone,soitcreatesanout-SVLeachtime.
        #Theninvoicethedeliveredquantity
        invoices=self.env['account.move']
        picking=so.picking_ids
        whilepicking:
            picking.move_lines.quantity_done=1
            action=picking.button_validate()
            ifisinstance(action,dict):
                wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
                wizard.process()
            picking=picking.backorder_ids

            invoice=so._create_invoices()
            invoice.action_post()
            invoices|=invoice

        out_account=self.product.categ_id.property_stock_account_output_categ_id
        invoice01,_invoice02,invoice03=invoices
        cogs=invoices.line_ids.filtered(lambdal:l.account_id==out_account)
        self.assertEqual(cogs.mapped('credit'),svl_values)

        #Resetandreposteachinvoice
        fori,invinenumerate(invoices):
            inv.button_draft()
            inv.action_post()
            cogs=invoices.line_ids.filtered(lambdal:l.account_id==out_account)
            self.assertEqual(cogs.mapped('credit'),svl_values,'Incorrectvalueswhilepostingagaininvoice%s'%(i+1))

        #Resetandrepostallinvoices(weonlycheckthetotalvalueasthe
        #distributionchangesbutdoesnotreallymatter)
        invoices.button_draft()
        invoices.action_post()
        cogs=invoices.line_ids.filtered(lambdal:l.account_id==out_account)
        self.assertEqual(sum(cogs.mapped('credit')),total_value)

        #Resetandrepostfewinvoices(weonlycheckthetotalvalueasthe
        #distributionchangesbutdoesnotreallymatter)
        (invoice01|invoice03).button_draft()
        (invoice01|invoice03).action_post()
        cogs=invoices.line_ids.filtered(lambdal:l.account_id==out_account)
        self.assertEqual(sum(cogs.mapped('credit')),total_value)

    deftest_fifo_reverse_and_create_new_invoice(self):
        """
        FIFOautomated
        Receive1@10,1@50
        Deliver1
        Posttheinvoice,addacreditnotewithoption'newdraftinv'
        Postthesecondinvoice
        COGSshouldbebasedonthedeliveredproduct
        """
        self.product.categ_id.property_cost_method='fifo'

        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.product.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpin[10,50]])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product.name,
                    'product_id':self.product.id,
                    'product_uom_qty':1.0,
                    'product_uom':self.product.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        picking=so.picking_ids
        picking.move_lines.quantity_done=1.0
        picking.button_validate()

        invoice01=so._create_invoices()
        invoice01.action_post()

        wizard=self.env['account.move.reversal'].with_context(active_model="account.move",active_ids=invoice01.ids).create({
            'refund_method':'modify',
        })
        invoice02=self.env['account.move'].browse(wizard.reverse_moves()['res_id'])
        invoice02.action_post()

        amls=invoice02.line_ids
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_stock_out'])
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,10)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.company_data['default_account_expense'])
        self.assertEqual(cogs_aml.debit,10)
        self.assertEqual(cogs_aml.credit,0)
