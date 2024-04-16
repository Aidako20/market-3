#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimporttimedelta

fromflectra.addons.sale_timesheet.tests.commonimportTestCommonSaleTimesheet

fromflectra.exceptionsimportUserError
fromflectra.fieldsimportDate
fromflectra.testsimportForm,tagged


@tagged('-at_install','post_install')
classTestReInvoice(TestCommonSaleTimesheet):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #patchexpenseproductstomakethemservicescreatingtask/project
        service_values={
            'type':'service',
            'service_type':'timesheet',
            'service_tracking':'task_in_project'
        }
        cls.company_data['product_order_cost'].write(service_values)
        cls.company_data['product_delivery_cost'].write(service_values)
        cls.company_data['product_order_sales_price'].write(service_values)
        cls.company_data['product_delivery_sales_price'].write(service_values)
        cls.company_data['product_order_no'].write(service_values)

        #createAA,SOandinvoices
        cls.analytic_account=cls.env['account.analytic.account'].create({
            'name':'TestAA',
            'code':'TESTSALE_TIMESHEET_REINVOICE',
            'company_id':cls.company_data['company'].id,
            'partner_id':cls.partner_a.id
        })

        cls.sale_order=cls.env['sale.order'].with_context(mail_notrack=True,mail_create_nolog=True).create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'analytic_account_id':cls.analytic_account.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })

        cls.Invoice=cls.env['account.move'].with_context(
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
            'product_uom':self.company_data['product_order_cost'].uom_id.id,
            'price_unit':self.company_data['product_order_cost'].list_price,
            'order_id':self.sale_order.id,
        })
        sale_order_line1.product_id_change()
        sale_order_line2=self.env['sale.order.line'].create({
            'name':self.company_data['product_delivery_cost'].name,
            'product_id':self.company_data['product_delivery_cost'].id,
            'product_uom_qty':4,
            'product_uom':self.company_data['product_delivery_cost'].uom_id.id,
            'price_unit':self.company_data['product_delivery_cost'].list_price,
            'order_id':self.sale_order.id,
        })
        sale_order_line2.product_id_change()

        self.sale_order.onchange_partner_id()
        self.sale_order._compute_tax_id()
        self.sale_order.action_confirm()

        self.assertEqual(sale_order_line1.qty_delivered_method,'timesheet',"Deliveredquantityof'service'SOlineshouldbecomputedbytimesheetamount")
        self.assertEqual(sale_order_line2.qty_delivered_method,'timesheet',"Deliveredquantityof'service'SOlineshouldbecomputedbytimesheetamount")

        #let'slogsometimesheets(ontheprojectcreatedbysale_order_line1)
        task_sol1=sale_order_line1.task_id
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_sol1.project_id.id,
            'task_id':task_sol1.id,
            'unit_amount':1,
            'employee_id':self.employee_user.id,
            'company_id':self.company_data['company'].id,
        })

        move_form=Form(self.Invoice)
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

        self.assertEqual(sale_order_line1.qty_delivered,1,"ExisingSOline1shouldnotbeimpactedbyreinvoicingproductatcost")
        self.assertEqual(sale_order_line2.qty_delivered,0,"ExisingSOline2shouldnotbeimpactedbyreinvoicingproductatcost")

        self.assertFalse(sale_order_line3.task_id,"AddinganewexpenseSOlineshouldnotcreateatask(sol3)")
        self.assertFalse(sale_order_line4.task_id,"AddinganewexpenseSOlineshouldnotcreateatask(sol4)")
        self.assertEqual(len(self.sale_order.project_ids),1,"SOcreateonlyoneprojectwithitsserviceline.AddingnewexpenseSOlineshouldnotimpactthat")

        self.assertEqual((sale_order_line3.price_unit,sale_order_line3.qty_delivered,sale_order_line3.product_uom_qty,sale_order_line3.qty_invoiced),(self.company_data['product_order_cost'].standard_price,3.0,0,0),'Salelineiswrongafterconfirmingvendorinvoice')
        self.assertEqual((sale_order_line4.price_unit,sale_order_line4.qty_delivered,sale_order_line4.product_uom_qty,sale_order_line4.qty_invoiced),(self.company_data['product_delivery_cost'].standard_price,3.0,0,0),'Salelineiswrongafterconfirmingvendorinvoice')

        self.assertEqual(sale_order_line3.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOlineshouldbecomputedbyanalyticamount")
        self.assertEqual(sale_order_line4.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOlineshouldbecomputedbyanalyticamount")

        #createsecondinvoicelinesandvalidateit
        move_form=Form(self.Invoice)
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

        self.assertEqual((sale_order_line5.price_unit,sale_order_line5.qty_delivered,sale_order_line5.product_uom_qty,sale_order_line5.qty_invoiced),(self.company_data['product_order_cost'].standard_price,2.0,0,0),'Saleline5iswrongafterconfirming2evendorinvoice')
        self.assertEqual((sale_order_line6.price_unit,sale_order_line6.qty_delivered,sale_order_line6.product_uom_qty,sale_order_line6.qty_invoiced),(self.company_data['product_delivery_cost'].standard_price,2.0,0,0),'Saleline6iswrongafterconfirming2evendorinvoice')

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

        #let'slogsometimesheets(ontheprojectcreatedbysale_order_line1)
        task_sol1=sale_order_line1.task_id
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_sol1.project_id.id,
            'task_id':task_sol1.id,
            'unit_amount':1,
            'employee_id':self.employee_user.id,
        })

        #createinvoicelinesandvalidateit
        move_form=Form(self.Invoice)
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

        self.assertEqual(sale_order_line1.qty_delivered,1,"ExisingSOline1shouldnotbeimpactedbyreinvoicingproductatcost")
        self.assertEqual(sale_order_line2.qty_delivered,0,"ExisingSOline2shouldnotbeimpactedbyreinvoicingproductatcost")

        self.assertFalse(sale_order_line3.task_id,"AddinganewexpenseSOlineshouldnotcreateatask(sol3)")
        self.assertFalse(sale_order_line4.task_id,"AddinganewexpenseSOlineshouldnotcreateatask(sol4)")
        self.assertEqual(len(self.sale_order.project_ids),1,"SOcreateonlyoneprojectwithitsserviceline.AddingnewexpenseSOlineshouldnotimpactthat")

        self.assertEqual((sale_order_line3.price_unit,sale_order_line3.qty_delivered,sale_order_line3.product_uom_qty,sale_order_line3.qty_invoiced),(self.company_data['product_delivery_sales_price'].list_price,3.0,0,0),'Salelineiswrongafterconfirmingvendorinvoice')
        self.assertEqual((sale_order_line4.price_unit,sale_order_line4.qty_delivered,sale_order_line4.product_uom_qty,sale_order_line4.qty_invoiced),(self.company_data['product_order_sales_price'].list_price,3.0,0,0),'Salelineiswrongafterconfirmingvendorinvoice')

        self.assertEqual(sale_order_line3.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOline3shouldbecomputedbyanalyticamount")
        self.assertEqual(sale_order_line4.qty_delivered_method,'analytic',"Deliveredquantityof'expense'SOline4shouldbecomputedbyanalyticamount")

        #createsecondinvoicelinesandvalidateit
        move_form=Form(self.Invoice)
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

        self.assertEqual((sale_order_line6.price_unit,sale_order_line6.qty_delivered,sale_order_line4.product_uom_qty,sale_order_line6.qty_invoiced),(self.company_data['product_order_sales_price'].list_price,2.0,0,0),'Salelineiswrongafterconfirming2evendorinvoice')

    deftest_no_expense(self):
        """Testinvoicingvendorbillwithnopolicy.Checknothinghappen."""
        #confirmSO
        sale_order_line=self.env['sale.order.line'].create({
            'name':self.company_data['product_order_no'].name,
            'product_id':self.company_data['product_order_no'].id,
            'product_uom_qty':2,
            'qty_delivered':1,
            'product_uom':self.company_data['product_order_no'].uom_id.id,
            'price_unit':self.company_data['product_order_no'].list_price,
            'order_id':self.sale_order.id,
        })
        self.sale_order._compute_tax_id()
        self.sale_order.action_confirm()

        #createinvoicelinesandvalidateit
        move_form=Form(self.Invoice)
        move_form.partner_id=self.partner_a
        withmove_form.line_ids.new()asline_form:
            line_form.product_id=self.company_data['product_order_no']
            line_form.quantity=3.0
            line_form.analytic_account_id=self.analytic_account
        invoice_a=move_form.save()
        invoice_a.action_post()

        #let'slogsometimesheets(ontheprojectcreatedbysale_order_line1)
        task_sol1=sale_order_line.task_id
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_sol1.project_id.id,
            'task_id':task_sol1.id,
            'unit_amount':1,
            'employee_id':self.employee_user.id,
        })

        self.assertEqual(len(self.sale_order.order_line),1,"NoSOlineshouldhavebeencreated(orremoved)whenvalidatingvendorbill")
        self.assertEqual(sale_order_line.qty_delivered,1,"ThedeliveredquantityofSOlineshouldnothavebeenincremented")
        self.assertTrue(invoice_a.mapped('line_ids.analytic_line_ids'),"Analyticlinesshouldbegenerated")

    deftest_reversed_invoice_reinvoice_with_period(self):
        """
        Teststhatwhenreversinganinvoiceoftimesheetandselectingatime
        period,theqtytoinvoiceiscorrectlyfound
        Businessflow:
          Createasaleorderanddeliversomehours(invoiced=0)
          Createaninvoice
          Confirm(invoiced=1)
          AddCreditNote
          Confirm(invoiced=0)
          GobacktotheSO
          Createaninvoice
          Selectatimeperiod[1weekago,1weekinthefuture]
          Confirm
          ->Failsifthereisnothingtoinvoice
        """
        product=self.env['product.product'].create({
            'name':"Servicedelivered,createtaskinglobalproject",
            'standard_price':30,
            'list_price':90,
            'type':'service',
            'service_policy':'delivered_timesheet',
            'invoice_policy':'delivery',
            'default_code':'SERV-DELI2',
            'service_type':'timesheet',
            'service_tracking':'task_global_project',
            'project_id':self.project_global.id,
            'taxes_id':False,
            'property_account_income_id':self.account_sale.id,
        })
        today=Date.context_today(self.env.user)

        #Createsasalesorderforquantity3
        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'Toto'})
        withso_form.order_line.new()asline:
            line.product_id=product
            line.product_uom_qty=3.0
        sale_order=so_form.save()
        sale_order.action_confirm()

        #"Deliver"1of3
        task=sale_order.tasks_ids
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':1,
            'employee_id':self.employee_user.id,
            'company_id':self.company_data['company'].id,
        })

        context={
            "active_model":'sale.order',
            "active_ids":[sale_order.id],
            "active_id":sale_order.id,
            'open_invoices':True,
        }
        #Invoicethe1
        wizard=self.env['sale.advance.payment.inv'].with_context(context).create({
            'advance_payment_method':'delivered'
        })
        invoice_dict=wizard.create_invoices()
        #Confirmtheinvoice
        invoice=self.env['account.move'].browse(invoice_dict['res_id'])
        invoice.action_post()
        #Refundtheinvoice
        refund_invoice_wiz=self.env['account.move.reversal'].with_context(active_model="account.move",active_ids=[invoice.id]).create({
            'reason':'pleasereverse:c',
            'refund_method':'refund',
            'date':today,
        })
        refund_invoice=self.env['account.move'].browse(refund_invoice_wiz.reverse_moves()['res_id'])
        refund_invoice.action_post()
        #reversingwithaction_reverseandthenaction_postdoesnotresettheinvoice_statusto'toinvoice'intests

        #Recreatewizardtogetthenewinvoicescreated
        wizard=self.env['sale.advance.payment.inv'].with_context(context).create({
            'advance_payment_method':'delivered',
            'date_start_invoice_timesheet':today-timedelta(days=7),
            'date_end_invoice_timesheet':today+timedelta(days=7)
        })

        #Theactualtest:
        wizard.create_invoices() #Noexceptionshouldberaised,thereisindeedsomethingtobeinvoicedsinceitwasreversed

