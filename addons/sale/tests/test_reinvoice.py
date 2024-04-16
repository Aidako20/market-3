#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromfreezegunimportfreeze_time
fromflectra.addons.sale.tests.commonimportTestSaleCommon
fromflectra.testsimportForm,tagged


@tagged('post_install','-at_install')
classTestReInvoice(TestSaleCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.analytic_account=cls.env['account.analytic.account'].create({
            'name':'TestAA',
            'code':'TESTSALE_REINVOICE',
            'company_id':cls.partner_a.company_id.id,
            'partner_id':cls.partner_a.id
        })

        cls.sale_order=cls.env['sale.order'].with_context(mail_notrack=True,mail_create_nolog=True).create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'analytic_account_id':cls.analytic_account.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })

        cls.AccountMove=cls.env['account.move'].with_context(
            default_move_type='in_invoice',
            default_invoice_date=cls.sale_order.date_order,
            mail_notrack=True,
            mail_create_nolog=True,
        )

    deftest_at_cost(self):
        """Testvendorbillatcostforproductbasedonorderedanddeliveredquantities."""
        #createSOlineandconfirmSO(withonlyoneline)
        sale_order_line1=self.env['sale.order.line'].create({
            'name':self.company_data['product_order_cost'].name,
            'product_id':self.company_data['product_order_cost'].id,
            'product_uom_qty':2,
            'qty_delivered':1,
            'product_uom':self.company_data['product_order_cost'].uom_id.id,
            'price_unit':self.company_data['product_order_cost'].list_price,
            'order_id':self.sale_order.id,
        })
        sale_order_line1.product_id_change()
        sale_order_line2=self.env['sale.order.line'].create({
            'name':self.company_data['product_delivery_cost'].name,
            'product_id':self.company_data['product_delivery_cost'].id,
            'product_uom_qty':4,
            'qty_delivered':1,
            'product_uom':self.company_data['product_delivery_cost'].uom_id.id,
            'price_unit':self.company_data['product_delivery_cost'].list_price,
            'order_id':self.sale_order.id,
        })
        sale_order_line2.product_id_change()

        self.sale_order.onchange_partner_id()
        self.sale_order._compute_tax_id()
        self.sale_order.action_confirm()

        #createinvoicelinesandvalidateit
        move_form=Form(self.AccountMove)
        move_form.partner_id=self.partner_a
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_order_cost']
            line_form.quantity=3.0
            line_form.analytic_account_id=self.analytic_account
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_delivery_cost']
            line_form.quantity=3.0
            line_form.analytic_account_id=self.analytic_account
        invoice_a=move_form.save()
        invoice_a.action_post()

        sale_order_line3=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line1andsol.product_id==self.company_data['product_order_cost'])
        sale_order_line4=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line2andsol.product_id==self.company_data['product_delivery_cost'])

        self.assertTrue(sale_order_line3,"Anewsalelineshouldhavebeencreatedwithorderedproduct")
        self.assertTrue(sale_order_line4,"Anewsalelineshouldhavebeencreatedwithdeliveredproduct")
        self.assertEqual(len(self.sale_order.order_line),4,"Thereshouldbe4linesontheSO(2vendorbilllinescreated)")
        self.assertEqual(len(self.sale_order.order_line.filtered(lambdasol:sol.is_expense)),2,"Thereshouldbe4linesontheSO(2vendorbilllinescreated)")

        self.assertEqual((sale_order_line3.price_unit,sale_order_line3.qty_delivered,sale_order_line3.product_uom_qty,sale_order_line3.qty_invoiced),(self.company_data['product_order_cost'].standard_price,3,0,0),'Salelineiswrongafterconfirmingvendorinvoice')
        self.assertEqual((sale_order_line4.price_unit,sale_order_line4.qty_delivered,sale_order_line4.product_uom_qty,sale_order_line4.qty_invoiced),(self.company_data['product_delivery_cost'].standard_price,3,0,0),'Salelineiswrongafterconfirmingvendorinvoice')

        self.assertEqual(sale_order_line3.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOlineshouldbecomputedbyanalyticamount")
        self.assertEqual(sale_order_line4.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOlineshouldbecomputedbyanalyticamount")

        #createsecondinvoicelinesandvalidateit
        move_form=Form(self.AccountMove)
        move_form.partner_id=self.partner_a
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_order_cost']
            line_form.quantity=2.0
            line_form.analytic_account_id=self.analytic_account
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_delivery_cost']
            line_form.quantity=2.0
            line_form.analytic_account_id=self.analytic_account
        invoice_b=move_form.save()
        invoice_b.action_post()

        sale_order_line5=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line1andsol!=sale_order_line3andsol.product_id==self.company_data['product_order_cost'])
        sale_order_line6=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line2andsol!=sale_order_line4andsol.product_id==self.company_data['product_delivery_cost'])

        self.assertTrue(sale_order_line5,"Anewsalelineshouldhavebeencreatedwithorderedproduct")
        self.assertTrue(sale_order_line6,"Anewsalelineshouldhavebeencreatedwithdeliveredproduct")

        self.assertEqual(len(self.sale_order.order_line),6,"Thereshouldbestill4linesontheSO,nonewcreated")
        self.assertEqual(len(self.sale_order.order_line.filtered(lambdasol:sol.is_expense)),4,"Thereshouldbestill2expenseslinesontheSO")

        self.assertEqual((sale_order_line5.price_unit,sale_order_line5.qty_delivered,sale_order_line5.product_uom_qty,sale_order_line5.qty_invoiced),(self.company_data['product_order_cost'].standard_price,2,0,0),'Saleline5iswrongafterconfirming2evendorinvoice')
        self.assertEqual((sale_order_line6.price_unit,sale_order_line6.qty_delivered,sale_order_line6.product_uom_qty,sale_order_line6.qty_invoiced),(self.company_data['product_delivery_cost'].standard_price,2,0,0),'Saleline6iswrongafterconfirming2evendorinvoice')

    @freeze_time('2020-01-15')
    deftest_sales_team_invoiced(self):
        """Testinvoicedfieldfrom salesteamonytakeintoaccounttheamountthesaleschannelhasinvoicedthismonth"""

        invoices=self.env['account.move'].create([
            {
                'move_type':'out_invoice',
                'partner_id':self.partner_a.id,
                'invoice_date':'2020-01-10',
                'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':1000.0})],
            },
            {
                'move_type':'out_refund',
                'partner_id':self.partner_a.id,
                'invoice_date':'2020-01-10',
                'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':500.0})],
            },
            {
                'move_type':'in_invoice',
                'partner_id':self.partner_a.id,
                'invoice_date':'2020-01-01',
                'date':'2020-01-01',
                'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':800.0})],
            },
        ])
        invoices.action_post()

        forinvoiceininvoices:
            self.env['account.payment.register']\
                .with_context(active_model='account.move',active_ids=invoice.ids)\
                .create({})\
                ._create_payments()

        invoices.flush()
        self.assertRecordValues(invoices.team_id,[{'invoiced':500.0}])

    deftest_sales_price(self):
        """Testinvoicingvendorbillatsalespriceforproductsbasedondeliveredandorderedquantities.ChecknoexistingSOlineisincremented,butwheninvoicinga
            secondtime,incrementonlythedeliveredsoline.
        """
        #createSOlineandconfirmSO(withonlyoneline)
        sale_order_line1=self.env['sale.order.line'].create({
            'name':self.company_data['product_delivery_sales_price'].name,
            'product_id':self.company_data['product_delivery_sales_price'].id,
            'product_uom_qty':2,
            'qty_delivered':1,
            'product_uom':self.company_data['product_delivery_sales_price'].uom_id.id,
            'price_unit':self.company_data['product_delivery_sales_price'].list_price,
            'order_id':self.sale_order.id,
        })
        sale_order_line1.product_id_change()
        sale_order_line2=self.env['sale.order.line'].create({
            'name':self.company_data['product_order_sales_price'].name,
            'product_id':self.company_data['product_order_sales_price'].id,
            'product_uom_qty':3,
            'qty_delivered':1,
            'product_uom':self.company_data['product_order_sales_price'].uom_id.id,
            'price_unit':self.company_data['product_order_sales_price'].list_price,
            'order_id':self.sale_order.id,
        })
        sale_order_line2.product_id_change()
        self.sale_order._compute_tax_id()
        self.sale_order.action_confirm()

        #createinvoicelinesandvalidateit
        move_form=Form(self.AccountMove)
        move_form.partner_id=self.partner_a
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_delivery_sales_price']
            line_form.quantity=3.0
            line_form.analytic_account_id=self.analytic_account
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_order_sales_price']
            line_form.quantity=3.0
            line_form.analytic_account_id=self.analytic_account
        invoice_a=move_form.save()
        invoice_a.action_post()

        sale_order_line3=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line1andsol.product_id==self.company_data['product_delivery_sales_price'])
        sale_order_line4=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line2andsol.product_id==self.company_data['product_order_sales_price'])

        self.assertTrue(sale_order_line3,"Anewsalelineshouldhavebeencreatedwithorderedproduct")
        self.assertTrue(sale_order_line4,"Anewsalelineshouldhavebeencreatedwithdeliveredproduct")
        self.assertEqual(len(self.sale_order.order_line),4,"Thereshouldbe4linesontheSO(2vendorbilllinescreated)")
        self.assertEqual(len(self.sale_order.order_line.filtered(lambdasol:sol.is_expense)),2,"Thereshouldbe4linesontheSO(2vendorbilllinescreated)")

        self.assertEqual((sale_order_line3.price_unit,sale_order_line3.qty_delivered,sale_order_line3.product_uom_qty,sale_order_line3.qty_invoiced),(self.company_data['product_delivery_sales_price'].list_price,3,0,0),'Salelineiswrongafterconfirmingvendorinvoice')
        self.assertEqual((sale_order_line4.price_unit,sale_order_line4.qty_delivered,sale_order_line4.product_uom_qty,sale_order_line4.qty_invoiced),(self.company_data['product_order_sales_price'].list_price,3,0,0),'Salelineiswrongafterconfirmingvendorinvoice')

        self.assertEqual(sale_order_line3.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOline3shouldbecomputedbyanalyticamount")
        self.assertEqual(sale_order_line4.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOline4shouldbecomputedbyanalyticamount")

        #createsecondinvoicelinesandvalidateit
        move_form=Form(self.AccountMove)
        move_form.partner_id=self.partner_a
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_delivery_sales_price']
            line_form.quantity=2.0
            line_form.analytic_account_id=self.analytic_account
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_order_sales_price']
            line_form.quantity=2.0
            line_form.analytic_account_id=self.analytic_account
        invoice_b=move_form.save()
        invoice_b.action_post()

        sale_order_line5=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line1andsol!=sale_order_line3andsol.product_id==self.company_data['product_delivery_sales_price'])
        sale_order_line6=self.sale_order.order_line.filtered(lambdasol:sol!=sale_order_line2andsol!=sale_order_line4andsol.product_id==self.company_data['product_order_sales_price'])

        self.assertFalse(sale_order_line5,"Nonewsalelineshouldhavebeencreatedwithdeliveredproduct!!")
        self.assertTrue(sale_order_line6,"Anewsalelineshouldhavebeencreatedwithorderedproduct")

        self.assertEqual(len(self.sale_order.order_line),5,"Thereshouldbe5linesontheSO,1newcreatedand1incremented")
        self.assertEqual(len(self.sale_order.order_line.filtered(lambdasol:sol.is_expense)),3,"Thereshouldbe3expenseslinesontheSO")

        self.assertEqual((sale_order_line6.price_unit,sale_order_line6.qty_delivered,sale_order_line4.product_uom_qty,sale_order_line6.qty_invoiced),(self.company_data['product_order_sales_price'].list_price,2,0,0),'Salelineiswrongafterconfirming2evendorinvoice')

    deftest_no_expense(self):
        """Testinvoicingvendorbillwithnopolicy.Checknothinghappen."""
        #confirmSO
        sale_order_line=self.env['sale.order.line'].create({
            'name':self.company_data['product_delivery_no'].name,
            'product_id':self.company_data['product_delivery_no'].id,
            'product_uom_qty':2,
            'qty_delivered':1,
            'product_uom':self.company_data['product_delivery_no'].uom_id.id,
            'price_unit':self.company_data['product_delivery_no'].list_price,
            'order_id':self.sale_order.id,
        })
        self.sale_order._compute_tax_id()
        self.sale_order.action_confirm()

        #createinvoicelinesandvalidateit
        move_form=Form(self.AccountMove)
        move_form.partner_id=self.partner_a
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_delivery_no']
            line_form.quantity=3.0
            line_form.analytic_account_id=self.analytic_account
        invoice_a=move_form.save()
        invoice_a.action_post()

        self.assertEqual(len(self.sale_order.order_line),1,"NoSOlineshouldhavebeencreated(orremoved)whenvalidatingvendorbill")
        self.assertTrue(invoice_a.mapped('line_ids.analytic_line_ids'),"Analyticlinesshouldbegenerated")

    deftest_not_reinvoicing_invoiced_so_lines(self):
        """TestthatinvoicedSOlinesarenotre-invoiced."""
        so_line1=self.env['sale.order.line'].create({
            'name':self.company_data['product_delivery_cost'].name,
            'product_id':self.company_data['product_delivery_cost'].id,
            'product_uom_qty':1,
            'product_uom':self.company_data['product_delivery_cost'].uom_id.id,
            'price_unit':self.company_data['product_delivery_cost'].list_price,
            'discount':100.00,
            'order_id':self.sale_order.id,
        })
        so_line1.product_id_change()
        so_line2=self.env['sale.order.line'].create({
            'name':self.company_data['product_delivery_sales_price'].name,
            'product_id':self.company_data['product_delivery_sales_price'].id,
            'product_uom_qty':1,
            'product_uom':self.company_data['product_delivery_sales_price'].uom_id.id,
            'price_unit':self.company_data['product_delivery_sales_price'].list_price,
            'discount':100.00,
            'order_id':self.sale_order.id,
        })
        so_line2.product_id_change()

        self.sale_order.onchange_partner_id()
        self.sale_order._compute_tax_id()
        self.sale_order.action_confirm()

        forlineinself.sale_order.order_line:
            line.qty_delivered=1
        #createinvoiceandvalidateit
        invoice=self.sale_order._create_invoices()
        invoice.action_post()

        so_line3=self.sale_order.order_line.filtered(lambdasol:sol!=so_line1andsol.product_id==self.company_data['product_delivery_cost'])
        so_line4=self.sale_order.order_line.filtered(lambdasol:sol!=so_line2andsol.product_id==self.company_data['product_delivery_sales_price'])

        self.assertFalse(so_line3,"Nore-invoicingshouldhavecreatedanewsalelinewithproduct#1")
        self.assertFalse(so_line4,"Nore-invoicingshouldhavecreatedanewsalelinewithproduct#2")
        self.assertEqual(so_line1.qty_delivered,1,"Nore-invoicingshouldhaveimpactedexisingSOline1")
        self.assertEqual(so_line2.qty_delivered,1,"Nore-invoicingshouldhaveimpactedexisingSOline2")
