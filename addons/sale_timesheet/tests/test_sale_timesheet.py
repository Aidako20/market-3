#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdate,timedelta

fromflectra.fieldsimportDate
fromflectra.toolsimportfloat_is_zero
fromflectra.exceptionsimportUserError
fromflectra.addons.sale_timesheet.tests.commonimportTestCommonSaleTimesheet
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestSaleTimesheet(TestCommonSaleTimesheet):
    """Thistestsuiteprovidetestsforthe3mainflowsofsellingservices:
            -Sellingservicesbasedonorderedquantities
            -Sellingtimesheetbasedondeliveredquantities
            -Sellingmilestones,basedonmanualdeliveredquantities
        Forthat,wecheckthetask/projectcreated,theinvoicedamounts,thedelivered
        quantitieschanges, ...
    """

    deftest_timesheet_order(self):
        """Testtimesheetinvoicingwith'invoiceonorder'timetrackedproducts
                1.createSOwith2orderedproductandconfirm
                2.createinvoice
                3.logtimesheet
                4.addnewSOline(orderedservice)
                5.createnewinvoice
        """
        #createSOandconfirmit
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        so_line_ordered_project_only=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet4.name,
            'product_id':self.product_order_timesheet4.id,
            'product_uom_qty':10,
            'product_uom':self.product_order_timesheet4.uom_id.id,
            'price_unit':self.product_order_timesheet4.list_price,
            'order_id':sale_order.id,
        })
        so_line_ordered_global_project=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet2.name,
            'product_id':self.product_order_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_order_timesheet2.uom_id.id,
            'price_unit':self.product_order_timesheet2.list_price,
            'order_id':sale_order.id,
        })
        so_line_ordered_project_only.product_id_change()
        so_line_ordered_global_project.product_id_change()
        sale_order.action_confirm()
        task_serv2=self.env['project.task'].search([('sale_line_id','=',so_line_ordered_global_project.id)])
        project_serv1=self.env['project.project'].search([('sale_line_id','=',so_line_ordered_project_only.id)])

        self.assertEqual(sale_order.tasks_count,1,"OnetaskshouldhavebeencreatedonSOconfirmation")
        self.assertEqual(len(sale_order.project_ids),2,"OneprojectshouldhavebeencreatedbytheSO,whenconfirmed+theonefromSOline2'taskinglobalproject'")
        self.assertEqual(sale_order.analytic_account_id,project_serv1.analytic_account_id,"ThecreatedprojectshouldbelinkedtotheanalyticaccountoftheSO")

        #createinvoice
        invoice1=sale_order._create_invoices()[0]

        #let'slogsometimesheets(ontheprojectcreatedbyso_line_ordered_project_only)
        timesheet1=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':10.5,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(so_line_ordered_global_project.qty_delivered,10.5,'Timesheetdirectlyonprojectdoesnotincreasedeliveredquantityonsoline')
        self.assertEqual(sale_order.invoice_status,'invoiced','SaleTimesheet:"invoiceonorder"timesheetsshouldnotmodifytheinvoice_statusoftheso')
        self.assertEqual(timesheet1.timesheet_invoice_type,'billable_fixed',"TimesheetslinkedtoSOlinewithorderedproductshoulbebebillablefixed")
        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

        timesheet2=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':39.5,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(so_line_ordered_global_project.qty_delivered,50,'SaleTimesheet:timesheetdoesnotincreasedeliveredquantityonsoline')
        self.assertEqual(sale_order.invoice_status,'invoiced','SaleTimesheet:"invoiceonorder"timesheetsshouldnotmodifytheinvoice_statusoftheso')
        self.assertEqual(timesheet2.timesheet_invoice_type,'billable_fixed',"TimesheetslinkedtoSOlinewithorderedproductshoulbebebillablefixed")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheetshouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

        timesheet3=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'unit_amount':10,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(so_line_ordered_project_only.qty_delivered,0.0,'Timesheetdirectlyonprojectdoesnotincreasedeliveredquantityonsoline')
        self.assertEqual(timesheet3.timesheet_invoice_type,'non_billable_project',"Timesheetswithouttaskshoulbebe'noprojectfound'")
        self.assertFalse(timesheet3.timesheet_invoice_id,"Thetimesheetshouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

        #logtimesheetontaskinglobalproject(higherthantheinitialordreredqty)
        timesheet4=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':5,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(sale_order.invoice_status,'upselling','SaleTimesheet:"invoiceonorder"timesheetsshouldnotmodifytheinvoice_statusoftheso')
        self.assertFalse(timesheet4.timesheet_invoice_id,"Thetimesheetshouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

        #addsolinewithprodudct"createtaskinnewproject".
        so_line_ordered_task_in_project=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet3.name,
            'product_id':self.product_order_timesheet3.id,
            'product_uom_qty':3,
            'product_uom':self.product_order_timesheet3.uom_id.id,
            'price_unit':self.product_order_timesheet3.list_price,
            'order_id':sale_order.id,
        })

        self.assertEqual(sale_order.invoice_status,'toinvoice','SaleTimesheet:Addinganewserviceline(soline)shouldputtheSOin"toinvocie"state.')
        self.assertEqual(sale_order.tasks_count,2,"Twotasks(1perSOline)shouldhavebeencreatedonSOconfirmation")
        self.assertEqual(len(sale_order.project_ids),2,"NonewprojectshouldhavebeencreatedbytheSO,whenselling'newtaskinnewproject'product,sinceitreusetheonefrom'projectonly'.")

        #getfirstinvoicelineofsalelinelinkedtotimesheet1
        invoice_line_1=so_line_ordered_global_project.invoice_lines.filtered(lambdaline:line.move_id==invoice1)

        self.assertEqual(so_line_ordered_global_project.product_uom_qty,invoice_line_1.quantity,"Theinvoice(ordered)quantityshouldnotchangewhencreatingtimesheet")

        #timesheetcanbemodified
        timesheet1.write({'unit_amount':12})

        self.assertEqual(so_line_ordered_global_project.product_uom_qty,invoice_line_1.quantity,"Theinvoice(ordered)quantityshouldnotchangewhenmodifyingtimesheet")

        #createsecondinvoice
        invoice2=sale_order._create_invoices()[0]

        self.assertEqual(len(sale_order.invoice_ids),2,"AsecondinvoiceshouldhavebeencreatedfromtheSO")
        self.assertTrue(float_is_zero(invoice2.amount_total-so_line_ordered_task_in_project.price_unit*3,precision_digits=2),'Sale:invoicegenerationontimesheetsproductiswrong')

        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheet2shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet3.timesheet_invoice_id,"Thetimesheet3shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet4.timesheet_invoice_id,"Thetimesheet4shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

        #validatethefirstinvoice
        invoice1.action_post()

        self.assertEqual(so_line_ordered_global_project.product_uom_qty,invoice_line_1.quantity,"Theinvoice(ordered)quantityshouldnotchangewhenmodifyingtimesheet")
        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheet2shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet3.timesheet_invoice_id,"Thetimesheet3shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet4.timesheet_invoice_id,"Thetimesheet4shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

        #timesheetcanstillbemodified
        timesheet1.write({'unit_amount':13})

    deftest_timesheet_delivery(self):
        """Testtimesheetinvoicingwith'invoiceondelivery'timetrackedproducts
                1.CreateSOandconfirmit
                2.logtimesheet
                3.createinvoice
                4.logothertimesheet
                5.createasecondinvoice
                6.addnewSOline(deliveredservice)
        """
        #createSOandconfirmit
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        so_line_deliver_global_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price,
            'order_id':sale_order.id,
        })
        so_line_deliver_task_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':20,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price,
            'order_id':sale_order.id,
        })
        so_line_deliver_global_project.product_id_change()
        so_line_deliver_task_project.product_id_change()

        #confirmSO
        sale_order.action_confirm()
        task_serv1=self.env['project.task'].search([('sale_line_id','=',so_line_deliver_global_project.id)])
        task_serv2=self.env['project.task'].search([('sale_line_id','=',so_line_deliver_task_project.id)])
        project_serv2=self.env['project.project'].search([('sale_line_id','=',so_line_deliver_task_project.id)])

        self.assertEqual(task_serv1.project_id,self.project_global,"SaleTimesheet:taskshouldbecreatedinglobalproject")
        self.assertTrue(task_serv1,"SaleTimesheet:onSOconfirmation,ataskshouldhavebeencreatedinglobalproject")
        self.assertTrue(task_serv2,"SaleTimesheet:onSOconfirmation,ataskshouldhavebeencreatedinanewproject")
        self.assertEqual(sale_order.invoice_status,'no','SaleTimesheet:"invoiceondelivery"shouldnotneedtobeinvoicedonsoconfirmation')
        self.assertEqual(sale_order.analytic_account_id,task_serv2.project_id.analytic_account_id,"SOshouldhavecreateaproject")
        self.assertEqual(sale_order.tasks_count,2,"Twotasks(1perSOline)shouldhavebeencreatedonSOconfirmation")
        self.assertEqual(len(sale_order.project_ids),2,"OneprojectshouldhavebeencreatedbytheSO,whenconfirmed+theonefromSOline1'taskinglobalproject'")
        self.assertEqual(sale_order.analytic_account_id,project_serv2.analytic_account_id,"ThecreatedprojectshouldbelinkedtotheanalyticaccountoftheSO")

        #let'slogsometimesheets
        timesheet1=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv1.project_id.id, #globalproject
            'task_id':task_serv1.id,
            'unit_amount':10.5,
            'employee_id':self.employee_manager.id,
        })
        self.assertEqual(so_line_deliver_global_project.invoice_status,'toinvoice','SaleTimesheet:"invoiceondelivery"timesheetsshouldsetthesolinein"toinvoice"statuswhenlogged')
        self.assertEqual(so_line_deliver_task_project.invoice_status,'no','SaleTimesheet:solineinvoicestatusshouldnotchangewhennotimesheetlinkedtotheline')
        self.assertEqual(sale_order.invoice_status,'toinvoice','SaleTimesheet:"invoiceondelivery"timesheetsshouldsetthesoin"toinvoice"statuswhenlogged')
        self.assertEqual(timesheet1.timesheet_invoice_type,'billable_time',"TimesheetslinkedtoSOlinewithdeliveredproductshoulbebebillabletime")
        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoiceyet")

        #invoiceSO
        invoice1=sale_order._create_invoices()
        self.assertTrue(float_is_zero(invoice1.amount_total-so_line_deliver_global_project.price_unit*10.5,precision_digits=2),'Sale:invoicegenerationontimesheetsproductiswrong')
        self.assertEqual(timesheet1.timesheet_invoice_id,invoice1,"Thetimesheet1shouldnotbelinkedtotheinvoice1,asweareindeliveredquantity(evenifinvoiceisindraft")
        withself.assertRaises(UserError): #Wecannotmodifytimesheetlinkedtoinvoice(evendraftones)
            timesheet1.write({'unit_amount':42})

        #logsometimesheetsagain
        timesheet2=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv1.project_id.id, #globalproject
            'task_id':task_serv1.id,
            'unit_amount':39.5,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(so_line_deliver_global_project.invoice_status,'toinvoice','SaleTimesheet:"invoiceondelivery"timesheetsshouldsetthesolinein"toinvoice"statuswhenlogged')
        self.assertEqual(so_line_deliver_task_project.invoice_status,'no','SaleTimesheet:solineinvoicestatusshouldnotchangewhennotimesheetlinkedtotheline')
        self.assertEqual(sale_order.invoice_status,'toinvoice','SaleTimesheet:"invoiceondelivery"timesheetsshouldnotmodifytheinvoice_statusoftheso')
        self.assertEqual(timesheet2.timesheet_invoice_type,'billable_time',"TimesheetslinkedtoSOlinewithdeliveredproductshoulbebebillabletime")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheet2shouldnotbelinkedtotheinvoiceyet")

        #createasecondinvoice
        invoice2=sale_order._create_invoices()[0]
        self.assertEqual(len(sale_order.invoice_ids),2,"AsecondinvoiceshouldhavebeencreatedfromtheSO")
        self.assertEqual(so_line_deliver_global_project.invoice_status,'invoiced','SaleTimesheet:"invoiceondelivery"timesheetsshouldsetthesolinein"toinvoice"statuswhenlogged')
        self.assertEqual(sale_order.invoice_status,'no','SaleTimesheet:"invoiceondelivery"timesheetsshouldbeinvoicedcompletelybynow')
        self.assertEqual(timesheet2.timesheet_invoice_id,invoice2,"Thetimesheet2shouldnotbelinkedtotheinvoice2")
        withself.assertRaises(UserError): #Wecannotmodifytimesheetlinkedtoinvoice(evendraftones)
            timesheet2.write({'unit_amount':42})

        #addalineonSO
        so_line_deliver_only_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet4.name,
            'product_id':self.product_delivery_timesheet4.id,
            'product_uom_qty':5,
            'product_uom':self.product_delivery_timesheet4.uom_id.id,
            'price_unit':self.product_delivery_timesheet4.list_price,
            'order_id':sale_order.id,
        })
        self.assertEqual(len(sale_order.project_ids),2,"NonewprojectshouldhavebeencreatedbytheSO,whenselling'projectonly'product,sinceitreusetheonefrom'newtaskinnewproject'.")

        #let'slogsometimesheetsontheproject
        timesheet3=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':project_serv2.id,
            'unit_amount':7,
            'employee_id':self.employee_user.id,
        })
        self.assertTrue(float_is_zero(so_line_deliver_only_project.qty_delivered,precision_digits=2),"TimesheetingonprojectshouldnotincrementedthedeliveredquantityontheSOline")
        self.assertEqual(sale_order.invoice_status,'toinvoice','SaleTimesheet:"invoiceondelivery"timesheetsshouldhavequantitytoinvoice')
        self.assertEqual(timesheet3.timesheet_invoice_type,'non_billable_project',"Timesheetswithouttaskshoulbebe'noprojectfound'")
        self.assertFalse(timesheet3.timesheet_invoice_id,"Thetimesheet3shouldnotbelinkedtotheinvoiceyet")

        #let'slogsometimesheetsonthetask(newtask/newproject)
        timesheet4=self.env['account.analytic.line'].create({
            'name':'TestLine4',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':7,
            'employee_id':self.employee_user.id,
        })
        self.assertFalse(timesheet4.timesheet_invoice_id,"Thetimesheet4shouldnotbelinkedtotheinvoiceyet")

        #modifyanoninvoicedtimesheet
        timesheet4.write({'unit_amount':42})

        self.assertFalse(timesheet4.timesheet_invoice_id,"Thetimesheet4shouldnotstillbelinkedtotheinvoice")

        #validatethesecondinvoice
        invoice2.action_post()

        self.assertEqual(timesheet1.timesheet_invoice_id,invoice1,"Thetimesheet1shouldnotbelinkedtotheinvoice1,evenaftervalidation")
        self.assertEqual(timesheet2.timesheet_invoice_id,invoice2,"Thetimesheet2shouldnotbelinkedtotheinvoice1,evenaftervalidation")
        self.assertFalse(timesheet3.timesheet_invoice_id,"Thetimesheet3shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")
        self.assertFalse(timesheet4.timesheet_invoice_id,"Thetimesheet4shouldnotbelinkedtotheinvoice,sinceweareinorderedquantity")

    deftest_timesheet_manual(self):
        """Testtimesheetinvoicingwith'invoiceondelivery'timetrackedproducts
        """
        #createSOandconfirmit
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        so_line_manual_global_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_manual2.name,
            'product_id':self.product_delivery_manual2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_manual2.uom_id.id,
            'price_unit':self.product_delivery_manual2.list_price,
            'order_id':sale_order.id,
        })
        so_line_manual_only_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_manual4.name,
            'product_id':self.product_delivery_manual4.id,
            'product_uom_qty':20,
            'product_uom':self.product_delivery_manual4.uom_id.id,
            'price_unit':self.product_delivery_manual4.list_price,
            'order_id':sale_order.id,
        })

        #confirmSO
        sale_order.action_confirm()
        self.assertTrue(sale_order.project_ids,"SalesOrdershouldhavecreateaproject")
        self.assertEqual(sale_order.invoice_status,'no','SaleTimesheet:manuallyproductshouldnotneedtobeinvoicedonsoconfirmation')

        project_serv2=so_line_manual_only_project.project_id
        self.assertTrue(project_serv2,"Asecondprojectiscreatedwhenselling'projectonly'afterSOconfirmation.")
        self.assertEqual(sale_order.analytic_account_id,project_serv2.analytic_account_id,"ThecreatedprojectshouldbelinkedtotheanalyticaccountoftheSO")

        #let'slogsometimesheets(ontaskandproject)
        timesheet1=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':self.project_global.id, #globalproject
            'task_id':so_line_manual_global_project.task_id.id,
            'unit_amount':6,
            'employee_id':self.employee_manager.id,
        })

        timesheet2=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':self.project_global.id, #globalproject
            'unit_amount':3,
            'employee_id':self.employee_manager.id,
        })

        self.assertEqual(len(sale_order.project_ids),2,"OneprojectshouldhavebeencreatedbytheSO,whenconfirmed+theonecomingfromSOline1'taskinglobalproject'.")
        self.assertEqual(so_line_manual_global_project.task_id.sale_line_id,so_line_manual_global_project,"TaskfromamilestoneproductshouldbelinkedtoitsSOlinetoo")
        self.assertEqual(timesheet1.timesheet_invoice_type,'billable_fixed',"Milestonetimesheetgoesinbillablefixedcategory")
        self.assertTrue(float_is_zero(so_line_manual_global_project.qty_delivered,precision_digits=2),"MilestoneTimesheetingshouldnotincrementedthedeliveredquantityontheSOline")
        self.assertEqual(so_line_manual_global_project.qty_to_invoice,0.0,"Manualserviceshouldnotbeaffectedbytimesheetontheircreatedtask.")
        self.assertEqual(so_line_manual_only_project.qty_to_invoice,0.0,"Manualserviceshouldnotbeaffectedbytimesheetontheircreatedproject.")
        self.assertEqual(sale_order.invoice_status,'no','SaleTimesheet:"invoiceondelivery"shouldnotneedtobeinvoicedonsoconfirmation')

        self.assertEqual(timesheet1.timesheet_invoice_type,'billable_fixed',"TimesheetslinkedtoSOlinewithorderedproductshoulbebebillablefixedsinceitisamilestone")
        self.assertEqual(timesheet2.timesheet_invoice_type,'non_billable_project',"Timesheetswithouttaskshoulbebe'noprojectfound'")
        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoice")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheet2shouldnotbelinkedtotheinvoice")

        #invoiceSO
        sale_order.order_line.write({'qty_delivered':5})
        invoice1=sale_order._create_invoices()

        forinvoice_lineininvoice1.invoice_line_ids:
            self.assertEqual(invoice_line.quantity,5,"Theinvoicedquantityshouldbe5,asmanuallysetonSOlines")

        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoice,sincetimesheetsareusedfortimetrackinginmilestone")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheet2shouldnotbelinkedtotheinvoice,sincetimesheetsareusedfortimetrackinginmilestone")

        #validatetheinvoice
        invoice1.action_post()

        self.assertFalse(timesheet1.timesheet_invoice_id,"Thetimesheet1shouldnotbelinkedtotheinvoice,evenafterinvoicevalidation")
        self.assertFalse(timesheet2.timesheet_invoice_id,"Thetimesheet2shouldnotbelinkedtotheinvoice,evenafterinvoicevalidation")

    deftest_timesheet_invoice(self):
        """Testtocreateinvoicesforthesaleorderwithtimesheets

            1)createsaleorder
            2)trytocreateaninvoiceforthetimesheets10daysbefore
            3)createinvoiceforthetimesheets6daysbefore
            4)createinvoiceforthetimesheets4daysbefore
            5)createinvoiceforthetimesheetsfromtoday
        """
        today=Date.context_today(self.env.user)
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        #SectionLine
        so_line_ordered_project_only=self.env['sale.order.line'].create({
            'name':"SectionName",
            'order_id':sale_order.id,
            'display_type':'line_section',
        })
        so_line_deliver_global_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price,
            'order_id':sale_order.id,
        })
        so_line_deliver_task_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':20,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price,
            'order_id':sale_order.id,
        })
        so_line_deliver_global_project.product_id_change()
        so_line_deliver_task_project.product_id_change()

        #confirmSO
        sale_order.action_confirm()
        task_serv1=self.env['project.task'].search([('sale_line_id','=',so_line_deliver_global_project.id)])
        task_serv2=self.env['project.task'].search([('sale_line_id','=',so_line_deliver_task_project.id)])
        project_serv2=self.env['project.project'].search([('sale_line_id','=',so_line_deliver_task_project.id)])

        timesheet1=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv1.project_id.id,
            'task_id':task_serv1.id,
            'unit_amount':10,
            'employee_id':self.employee_manager.id,
            'date':today-timedelta(days=6)
        })

        timesheet2=self.env['account.analytic.line'].create({
            'name':'TestLine2',
            'project_id':task_serv1.project_id.id,
            'task_id':task_serv1.id,
            'unit_amount':20,
            'employee_id':self.employee_manager.id,
            'date':today-timedelta(days=1)
        })

        timesheet3=self.env['account.analytic.line'].create({
            'name':'TestLine3',
            'project_id':task_serv1.project_id.id,
            'task_id':task_serv1.id,
            'unit_amount':10,
            'employee_id':self.employee_manager.id,
            'date':today-timedelta(days=5)
        })

        timesheet4=self.env['account.analytic.line'].create({
            'name':'TestLine4',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':30,
            'employee_id':self.employee_manager.id
        })
        self.assertEqual(so_line_deliver_global_project.invoice_status,'toinvoice')
        self.assertEqual(so_line_deliver_task_project.invoice_status,'toinvoice')
        self.assertEqual(sale_order.invoice_status,'toinvoice')

        #Contextforsale.advance.payment.invwizard
        self.context={
            'active_model':'sale.order',
            'active_ids':[sale_order.id],
            'active_id':sale_order.id,
            'default_journal_id':self.company_data['default_journal_sale'].id
        }

        #invoiceSO
        wizard=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered',
            'date_start_invoice_timesheet':today-timedelta(days=16),
            'date_end_invoice_timesheet':today-timedelta(days=10)
        })

        self.assertTrue(wizard.invoicing_timesheet_enabled,'The"date_start_invoice_timesheet"and"date_end_invoice_timesheet"fieldshouldbevisibleinthewizardbecauseaproductinsaleorderhasservice_policyto"TimesheetonTask"')

        withself.assertRaises(UserError):
            wizard.create_invoices()

        self.assertFalse(sale_order.invoice_ids,'Normally,noinvoicewillbecreatedbecausethetimesheetloggedisaftertheperioddefinedindate_start_invoice_timesheetanddate_end_invoice_timesheetfield')

        wizard.write({
            'date_start_invoice_timesheet':today-timedelta(days=10),
            'date_end_invoice_timesheet':today-timedelta(days=6)
        })
        wizard.create_invoices()

        self.assertTrue(sale_order.invoice_ids,'Oneinvoiceshouldbecreatedbecausethetimesheetloggedisbetweentheperioddefinedinwizard')

        invoice=sale_order.invoice_ids[0]
        self.assertEqual(so_line_deliver_global_project.qty_invoiced,timesheet1.unit_amount)

        #validateinvoice
        invoice.action_post()

        wizard.write({
            'date_start_invoice_timesheet':today-timedelta(days=16),
            'date_end_invoice_timesheet':today-timedelta(days=4)
        })
        wizard.create_invoices()

        self.assertEqual(len(sale_order.invoice_ids),2)
        invoice2=sale_order.invoice_ids[-1]

        self.assertEqual(so_line_deliver_global_project.qty_invoiced,timesheet1.unit_amount+timesheet3.unit_amount,"Thelastinvoicedoneshouldhavethequantityofthetimesheet3,becausethedatethistimesheetistheonlyonebeforethe'date_end_invoice_timesheet'fieldinthewizard.")

        wizard.write({
            'date_start_invoice_timesheet':today-timedelta(days=4),
            'date_end_invoice_timesheet':today
        })

        wizard.create_invoices()

        self.assertEqual(len(sale_order.invoice_ids),3)
        invoice3=sale_order.invoice_ids[-1]

        #Checkifalltimesheetshavebeeninvoiced
        self.assertEqual(so_line_deliver_global_project.qty_invoiced,timesheet1.unit_amount+timesheet2.unit_amount+timesheet3.unit_amount)
        self.assertTrue(so_line_deliver_task_project.invoice_lines)
        self.assertEqual(so_line_deliver_task_project.qty_invoiced,timesheet4.unit_amount)

    deftest_transfert_project(self):
        """Transferttaskwithtimesheettoanotherproject."""
        Timesheet=self.env['account.analytic.line']
        Task=self.env['project.task']
        today=Date.context_today(self.env.user)

        task=Task.with_context(default_project_id=self.project_global.id).create({
            'name':'firsttask',
            'partner_id':self.partner_a.id,
            'planned_hours':10,
        })

        Timesheet.create({
            'project_id':self.project_global.id,
            'task_id':task.id,
            'name':'myfirsttimesheet',
            'unit_amount':4,
        })

        timesheet_count1=Timesheet.search_count([('project_id','=',self.project_global.id)])
        timesheet_count2=Timesheet.search_count([('project_id','=',self.project_template.id)])
        self.assertEqual(timesheet_count1,1,"Onetimesheetinproject_global")
        self.assertEqual(timesheet_count2,0,"Notimesheetinproject_template")
        self.assertEqual(len(task.timesheet_ids),1,"Thetimesheetshouldbelinkedtotask")

        #changeprojectoftask,asthetimesheetisnotyetinvoiced,thetimesheetwillchangehisproject
        task.write({
            'project_id':self.project_template.id
        })

        timesheet_count1=Timesheet.search_count([('project_id','=',self.project_global.id)])
        timesheet_count2=Timesheet.search_count([('project_id','=',self.project_template.id)])
        self.assertEqual(timesheet_count1,0,"Notimesheetinproject_global")
        self.assertEqual(timesheet_count2,1,"Onetimesheetinproject_template")
        self.assertEqual(len(task.timesheet_ids),1,"Thetimesheetstillshouldbelinkedtotask")

        wizard=self.env['project.task.create.sale.order'].with_context(active_id=task.id,active_model='project.task').create({
            'product_id':self.product_delivery_timesheet3.id
        })

        #WecreatetheSOandtheinvoice
        action=wizard.action_create_sale_order()
        sale_order=self.env['sale.order'].browse(action['res_id'])
        self.context={
            'active_model':'sale.order',
            'active_ids':[sale_order.id],
            'active_id':sale_order.id,
            'default_journal_id':self.company_data['default_journal_sale'].id
        }
        wizard=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered',
            'date_start_invoice_timesheet':today-timedelta(days=4),
            'date_end_invoice_timesheet':today
        })
        wizard.create_invoices()

        Timesheet.create({
            'project_id':self.project_template.id,
            'task_id':task.id,
            'name':'mysecondtimesheet',
            'unit_amount':6,
        })

        self.assertEqual(Timesheet.search_count([('project_id','=',self.project_template.id)]),2,"2timesheetsinproject_template")

        #changeprojectoftask,thetimesheetnotyetinvoicedwillchangeitsproject.Thetimesheetalreadyinvoicedwillnotchangehisproject.
        task.write({
            'project_id':self.project_global.id
        })

        timesheet_count1=Timesheet.search_count([('project_id','=',self.project_global.id)])
        timesheet_count2=Timesheet.search_count([('project_id','=',self.project_template.id)])
        self.assertEqual(timesheet_count1,1,"Onetimesheetinproject_global")
        self.assertEqual(timesheet_count2,1,"Stillonetimesheetinproject_template")
        self.assertEqual(len(task.timesheet_ids),2,"The2timesheetstillshouldbelinkedtotask")

    deftest_change_customer_and_SOL_after_invoiced_timesheet(self):
        sale_order1=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        sale_order2=self.env['sale.order'].create({
            'partner_id':self.partner_b.id,
            'partner_invoice_id':self.partner_b.id,
            'partner_shipping_id':self.partner_b.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        so1_product_global_project_so_line=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price,
            'order_id':sale_order1.id,
        })
        so2_product_global_project_so_line=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':20,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price,
            'order_id':sale_order2.id,
        })

        sale_order1.action_confirm()
        sale_order2.action_confirm()

        task_so1=self.env['project.task'].search([('sale_line_id','=',so1_product_global_project_so_line.id)])
        task_so2=self.env['project.task'].search([('sale_line_id','=',so2_product_global_project_so_line.id)])

        self.assertEqual(self.partner_a,task_so1.partner_id,"TheCustomerofthefirsttaskshouldbeequaltopartner_a.")
        self.assertEqual(self.partner_b,task_so2.partner_id,"TheCustomerofthesecondtaskshouldbeequaltopartner_b.")
        self.assertEqual(sale_order1.partner_id,task_so1.partner_id,"TheCustomerofthefirsttaskshouldbeequaltotheCustomerofthefirstSalesOrder.")
        self.assertEqual(sale_order2.partner_id,task_so2.partner_id,"TheCustomerofthesecondtaskshouldbeequaltotheCustomerofthesecondSalesOrder.")

        task_so1_timesheet1=self.env['account.analytic.line'].create({
            'name':'TestLine1',
            'project_id':task_so1.project_id.id,
            'task_id':task_so1.id,
            'unit_amount':5,
            'employee_id':self.employee_user.id,
        })

        invoice=sale_order1._create_invoices()
        invoice.action_post()

        self.assertEqual(self.partner_a,task_so1_timesheet1.partner_id,"TheTask'sTimesheetentryshouldhavethesamepartnerthanonthetask1andSalesOrder1.")

        task_so1_timesheet2=self.env['account.analytic.line'].create({
            'name':'TestLine2',
            'project_id':task_so1.project_id.id,
            'task_id':task_so1.id,
            'unit_amount':3,
            'employee_id':self.employee_user.id,
        })

        task_so1.write({
            'partner_id':self.partner_b.id,
            'sale_line_id':so2_product_global_project_so_line.id,
        })

        self.assertEqual(self.partner_a,task_so1_timesheet1.partner_id,"TheTask'sfirstTimesheetentryshouldnothavechangedasitwasalreadyinvoiced(itspartnershouldstillbepartner_a).")
        self.assertEqual(self.partner_b,task_so1_timesheet2.partner_id,"TheTask'ssecondTimesheetentryshouldhaveitspartnerchanged,asitwasnotinvoicedandtheTask'spartner/customerchanged.")
        self.assertEqual(so1_product_global_project_so_line,task_so1_timesheet1.so_line,"TheTask'sfirstTimesheetentryshouldnothavechangedasitwasalreadyinvoiced(itsso_lineshouldstillbeequaltothefirstSalesOrderline).")
        self.assertEqual(so2_product_global_project_so_line,task_so1_timesheet2.so_line,"TheTask'ssecondTimesheetentryshouldhaveit'sso_linechanged,astheSalesOrderItemoftheTaskchanged,andthisentrywasnotinvoiced.")

    deftest_timesheet_upsell(self):
        """Testtimesheetupsellingandemail"""

        sale_order=self.env['sale.order'].with_context(mail_notrack=True,mail_create_nolog=True).create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'user_id':self.user_employee_company_B.id,
        })
        #createSOandconfirmit
        uom_days=self.env.ref('uom.product_uom_day')
        sale_order_line=self.env['sale.order.line'].create({
            'order_id':sale_order.id,
            'name':self.product_order_timesheet3.name,
            'product_id':self.product_order_timesheet3.id,
            'product_uom_qty':1,
            'product_uom':uom_days.id,
            'price_unit':self.product_order_timesheet3.list_price,
        })
        sale_order.action_confirm()
        task=sale_order_line.task_id

        #let'slogsometimesheets
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':8,
            'employee_id':self.employee_manager.id,
        })

        sale_order._create_invoices()
        last_message_id=self.env['mail.message'].search([('model','=','sale.order'),('res_id','=',sale_order.id)],limit=1).idor0
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':5,
            'employee_id':self.employee_user.id,
        })

        self.assertEqual(sale_order.invoice_status,'upselling','SaleTimesheet:"invoiceondelivery"timesheetsshouldnotmodifytheinvoice_statusoftheso')
        message_sent=self.env['mail.message'].search([
            ('id','>',last_message_id),
            ('subject','like','Upsell'),
            ('model','=','sale.order'),
            ('res_id','=',sale_order.id),
        ])

        self.assertEqual(len(message_sent),1,'SaleTimesheet:Anemailshouldalwaysbesenttothesalepersonwhenthestateofthesaleorderchangetoupselling')

        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':5,
            'employee_id':self.employee_user.id,
        })

        message_sent=self.env['mail.message'].search([
            ('id','>',last_message_id),
            ('subject','like','Upsell'),
            ('model','=','sale.order'),
            ('res_id','=',sale_order.id),
        ])
        self.assertEqual(len(message_sent),1,'SaleTimesheet:Anemailshouldonlybesenttothesalepersonwhenthestateofthesaleorderchangetoupselling')

    deftest_unlink_timesheet(self):
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        so_line=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price,
            'order_id':sale_order.id,
        })
        sale_order.action_confirm()
        task=so_line.task_id

        #let'slogsometimesheets
        analytic_line=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':50,
            'employee_id':self.employee_manager.id,
        })

        move=sale_order._create_invoices()
        self.assertEqual(analytic_line.timesheet_invoice_id,move,"Thetimesheetshouldbelinkedtomove")

        move.with_context(check_move_validity=False).line_ids[0].unlink()
        self.assertFalse(analytic_line.timesheet_invoice_id,"Thetimesheetshouldhavebeenunlinkedfrommove")
