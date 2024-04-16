#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.sale_timesheet.tests.commonimportTestCommonSaleTimesheet
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestProjectBilling(TestCommonSaleTimesheet):
    """Thistestsuiteprovidechecksformiscellaneoussmallthings."""

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #setup
        cls.employee_tde=cls.env['hr.employee'].create({
            'name':'EmployeeTDE',
            'timesheet_cost':42,
        })

        cls.partner_2=cls.env['res.partner'].create({
            'name':'CustomerfromtheSouth',
            'email':'customer.usd@south.com',
            'property_account_payable_id':cls.company_data['default_account_payable'].id,
            'property_account_receivable_id':cls.company_data['default_account_receivable'].id,
        })

        #SaleOrder1,noproject/taskcreated,usedtotimesheetatemployeerate
        SaleOrder=cls.env['sale.order'].with_context(tracking_disable=True)
        SaleOrderLine=cls.env['sale.order.line'].with_context(tracking_disable=True)
        cls.sale_order_1=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
        })

        cls.so1_line_order_no_task=SaleOrderLine.create({
            'name':cls.product_order_timesheet1.name,
            'product_id':cls.product_order_timesheet1.id,
            'product_uom_qty':10,
            'product_uom':cls.product_order_timesheet1.uom_id.id,
            'price_unit':cls.product_order_timesheet1.list_price,
            'order_id':cls.sale_order_1.id,
        })

        cls.so1_line_deliver_no_task=SaleOrderLine.create({
            'name':cls.product_delivery_timesheet1.name,
            'product_id':cls.product_delivery_timesheet1.id,
            'product_uom_qty':10,
            'product_uom':cls.product_delivery_timesheet1.uom_id.id,
            'price_unit':cls.product_delivery_timesheet1.list_price,
            'order_id':cls.sale_order_1.id,
        })
        #SaleOrder2,creates2projectbilledattaskrate
        cls.sale_order_2=SaleOrder.create({
            'partner_id':cls.partner_2.id,
            'partner_invoice_id':cls.partner_2.id,
            'partner_shipping_id':cls.partner_2.id,
        })
        cls.so2_line_deliver_project_task=SaleOrderLine.create({
            'order_id':cls.sale_order_2.id,
            'name':cls.product_delivery_timesheet3.name,
            'product_id':cls.product_delivery_timesheet3.id,
            'product_uom_qty':5,
            'product_uom':cls.product_delivery_timesheet3.uom_id.id,
            'price_unit':cls.product_delivery_timesheet3.list_price
        })
        cls.so2_line_deliver_project_template=SaleOrderLine.create({
            'order_id':cls.sale_order_2.id,
            'name':cls.product_delivery_timesheet5.name,
            'product_id':cls.product_delivery_timesheet5.id,
            'product_uom_qty':7,
            'product_uom':cls.product_delivery_timesheet5.uom_id.id,
            'price_unit':cls.product_delivery_timesheet5.list_price
        })
        cls.sale_order_2.action_confirm()

        #Projects:atleastoneperbillabletype
        Project=cls.env['project.project'].with_context(tracking_disable=True)
        cls.project_subtask=Project.create({
            'name':"SubTaskProject(nonbillable)",
            'allow_timesheets':True,
            'allow_billable':False,
            'partner_id':False,
        })
        cls.project_non_billable=Project.create({
            'name':"NonBillableProject",
            'allow_timesheets':True,
            'allow_billable':False,
            'partner_id':False,
            'subtask_project_id':cls.project_subtask.id,
        })
        cls.project_task_rate=cls.env['project.project'].search([('sale_line_id','=',cls.so2_line_deliver_project_task.id)],limit=1)
        cls.project_task_rate2=cls.env['project.project'].search([('sale_line_id','=',cls.so2_line_deliver_project_template.id)],limit=1)

        cls.project_employee_rate=Project.create({
            'name':"ProjectbilledatEmployeeRate",
            'allow_timesheets':True,
            'allow_billable':True,
            'bill_type':'customer_project',
            'pricing_type':'employee_rate',
            'sale_order_id':cls.sale_order_1.id,
            'partner_id':cls.sale_order_1.partner_id.id,
            'subtask_project_id':cls.project_subtask.id,
        })
        cls.project_employee_rate_manager=cls.env['project.sale.line.employee.map'].create({
            'project_id':cls.project_employee_rate.id,
            'sale_line_id':cls.so1_line_order_no_task.id,
            'employee_id':cls.employee_manager.id,
        })
        cls.project_employee_rate_user=cls.env['project.sale.line.employee.map'].create({
            'project_id':cls.project_employee_rate.id,
            'sale_line_id':cls.so1_line_deliver_no_task.id,
            'employee_id':cls.employee_user.id,
        })

    deftest_make_billable_at_task_rate(self):
        """Startingfromanonbillableproject,makeitbillableattaskrate"""
        Timesheet=self.env['account.analytic.line']
        Task=self.env['project.task']
        #setacustomerontheproject
        self.project_non_billable.write({
            'partner_id':self.partner_2.id
        })
        #createataskand2timesheets
        task=Task.with_context(default_project_id=self.project_non_billable.id).create({
            'name':'firsttask',
            'partner_id':self.project_non_billable.partner_id.id,
            'planned_hours':10,
        })
        timesheet1=Timesheet.create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':3,
            'employee_id':self.employee_manager.id,
        })
        timesheet2=Timesheet.create({
            'name':'TestLinetde',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':2,
            'employee_id':self.employee_tde.id,
        })

        #Changeprojecttobillableattaskrate
        self.project_non_billable.write({
            'allow_billable':True,
            'bill_type':'customer_project',
            'pricing_type':'fixed_rate',
        })
        task.timesheet_product_id=self.product_delivery_timesheet3

        #createwizard
        wizard=self.env['project.create.sale.order'].with_context(active_id=self.project_non_billable.id,active_model='project.project').create({})

        self.assertEqual(wizard.partner_id,self.project_non_billable.partner_id,"Thewizardshouldhavethesamepartnerastheproject")
        self.assertEqual(len(wizard.line_ids),1,"Thewizardshouldhaveoneline")
        self.assertEqual(wizard.line_ids.product_id,self.product_delivery_timesheet3,"Thewizardshouldhaveonelinewithrightproduct")

        #createtheSOfromtheproject
        action=wizard.action_create_sale_order()
        sale_order=self.env['sale.order'].browse(action['res_id'])

        self.assertEqual(sale_order.partner_id,self.project_non_billable.partner_id,"ThecustomeroftheSOshouldbethesameastheproject")
        self.assertEqual(len(sale_order.order_line),1,"TheSOshouldhave1line")
        self.assertEqual(sale_order.order_line.product_id,wizard.line_ids.product_id,"TheproductoftheonlySOLshouldbetheselectedonthewizard")
        self.assertEqual(sale_order.order_line.project_id,self.project_non_billable,"SOLshouldbelinkedtotheproject")
        self.assertTrue(sale_order.order_line.task_id,"TheSOLcreatesataskastheywerenotaskalreadypresentintheproject(systemlimitation)")
        self.assertEqual(sale_order.order_line.task_id.project_id,self.project_non_billable,"Thecreatedtaskshouldbeintheproject")
        self.assertEqual(sale_order.order_line.qty_delivered,timesheet1.unit_amount+timesheet2.unit_amount,"ThecreateSOLshouldhaveandeliveredquantityequalstothesumoftasks'timesheets")

    deftest_make_billable_at_employee_rate(self):
        """Startingfromanonbillableproject,makeitbillableatemployeerate"""
        Timesheet=self.env['account.analytic.line']
        Task=self.env['project.task']
        #setacustomerontheproject
        self.project_non_billable.write({
            'partner_id':self.partner_2.id
        })
        #createataskand2timesheets
        task=Task.with_context(default_project_id=self.project_non_billable.id).create({
            'name':'firsttask',
            'partner_id':self.project_non_billable.partner_id.id,
            'planned_hours':10,
        })
        timesheet1=Timesheet.create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':3,
            'employee_id':self.employee_manager.id,
        })
        timesheet2=Timesheet.create({
            'name':'TestLinetde',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':2,
            'employee_id':self.employee_user.id,
        })

        #Changeprojecttobillableatemployeerate
        self.project_non_billable.write({
            'allow_billable':True,
            'bill_type':'customer_project',
            'pricing_type':'employee_rate',
        })

        #createwizard
        wizard=self.env['project.create.sale.order'].with_context(active_id=self.project_non_billable.id,active_model='project.project').create({
            'partner_id':self.partner_2.id,
            'line_ids':[
                (0,0,{'product_id':self.product_delivery_timesheet1.id,'price_unit':15,'employee_id':self.employee_tde.id}), #productcreatesnoT
                (0,0,{'product_id':self.product_delivery_timesheet1.id,'price_unit':15,'employee_id':self.employee_manager.id}), #productcreatesnoT(sameproductthanpreviousone)
                (0,0,{'product_id':self.product_delivery_timesheet3.id,'price_unit':self.product_delivery_timesheet3.list_price,'employee_id':self.employee_user.id}), #productcreatesnewTinnewP
            ]
        })

        self.assertEqual(wizard.partner_id,self.project_non_billable.partner_id,"Thewizardshouldhavethesamepartnerastheproject")
        self.assertEqual(wizard.project_id,self.project_non_billable,"Thewizard'projectshouldbethenonbillableproject")

        #createtheSOfromtheproject
        action=wizard.action_create_sale_order()
        sale_order=self.env['sale.order'].browse(action['res_id'])

        self.assertEqual(sale_order.partner_id,self.project_non_billable.partner_id,"ThecustomeroftheSOshouldbethesameastheproject")
        self.assertEqual(len(sale_order.order_line),2,"TheSOshouldhave2lines,asinwizardmaptherewere2timethesameproductwiththesameprice(for2differentemployees)")
        self.assertEqual(len(self.project_non_billable.sale_line_employee_ids),3,"Theprojecthave3linesinitsmap")
        self.assertEqual(self.project_non_billable.sale_line_id,sale_order.order_line[0],"Thewizardsetssalelinefallbakconprojectasthefirstofthelist")
        self.assertEqual(task.sale_line_id,sale_order.order_line[0],"Thewizardsetssalelinefallbackontasks")
        self.assertEqual(task.partner_id,wizard.partner_id,"ThewizardsetsthecustomerontaskstomakeSOLlinefieldvisible")

        line1=sale_order.order_line.filtered(lambdasol:sol.product_id==self.product_delivery_timesheet1)
        line2=sale_order.order_line.filtered(lambdasol:sol.product_id==self.product_delivery_timesheet3)

        self.assertTrue(line1,"Saleline1withproduct1shouldexists")
        self.assertTrue(line2,"Saleline2withproduct3shouldexists")

        self.assertFalse(line1.project_id,"Saleline1shouldbelinkedtothe'nonbillable'project")
        self.assertEqual(line2.project_id,self.project_non_billable,"Saleline3shouldbelinkedtothe'nonbillable'project")
        self.assertEqual(line1.price_unit,15,"TheunitpriceofSOL1shouldbe15")
        self.assertEqual(line1.product_uom_qty,3,"TheorderedqtyofSOL1shouldbe3")
        self.assertEqual(line2.product_uom_qty,2,"TheorderedqtyofSOL2shouldbe2")

        self.assertEqual(self.project_non_billable.sale_line_employee_ids.mapped('sale_line_id'),sale_order.order_line,"TheSOlinesofthemapshouldbethesameofthesalesorder")
        self.assertEqual(timesheet1.so_line,line1,"Timesheet1shouldbelinkedtosaleline1,asemployeemanagercreatethetimesheet")
        self.assertEqual(timesheet2.so_line,line2,"Timesheet2shouldbelinkedtosaleline2,asemployeetdecreatethetimesheet")
        self.assertEqual(timesheet1.unit_amount,line1.qty_delivered,"Saleline1shouldhaveadeliveredqtyequalstothesumofitslinkedtimesheets")
        self.assertEqual(timesheet2.unit_amount,line2.qty_delivered,"Saleline2shouldhaveadeliveredqtyequalstothesumofitslinkedtimesheets")

    deftest_billing_employee_rate(self):
        """Checktaskandsubtaskcreation,andtimesheetinginaprojectbilledat'employeerate'.Thenmovethetaskintoa'taskrate'project."""
        Task=self.env['project.task'].with_context(tracking_disable=True)
        Timesheet=self.env['account.analytic.line']

        #createatask
        task=Task.with_context(default_project_id=self.project_employee_rate.id).create({
            'name':'firsttask',
            'partner_id':self.partner_a.id,
        })

        self.assertTrue(task.allow_billable,"Taskinproject'employeerate'shouldbebillable")
        self.assertEqual(task.bill_type,'customer_project',"Taskinproject'employeerate'shouldbebilledatemployeerate")
        self.assertEqual(task.pricing_type,'employee_rate',"Taskinproject'employeerate'shouldbebilledatemployeerate")
        self.assertFalse(task.sale_line_id,"Taskcreatedinaprojectbilledon'employeerate'shouldnotbelinkedtoaSOL")
        self.assertEqual(task.partner_id,task.project_id.partner_id,"Taskcreatedinaprojectbilledon'employeerate'shouldhavethesamecustomerastheonefromtheproject")

        #logtimesheetontask
        timesheet1=Timesheet.create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':50,
            'employee_id':self.employee_manager.id,
        })

        self.assertFalse(timesheet1.so_line,"ThetimesheetshouldbenotlinkedtotheprojectofthemapentrysincenoSOLinthelinkedtask.")

        task.write({
            'sale_line_id':self.project_employee_rate_user.sale_line_id.id
        })

        self.assertEqual(self.project_employee_rate_manager.sale_line_id,timesheet1.so_line,"ThetimesheetshouldbelinkedtotheSOLassociatedtotheEmployeemanagerinthemap")
        self.assertEqual(self.project_employee_rate_manager.project_id,timesheet1.project_id,"Thetimesheetshouldbelinkedtotheprojectofthemapentry")

        #createasubtask
        subtask=Task.with_context(default_project_id=self.project_employee_rate.subtask_project_id.id).create({
            'name':'firstsubtasktask',
            'parent_id':task.id,
        })

        self.assertFalse(subtask.allow_billable,"Subtaskinnonbillableprojectshouldbenonbillabletoo")
        self.assertFalse(subtask.project_id.allow_billable,"Thesubtaskprojectisnonbillableevenifthesubtaskis")
        self.assertEqual(subtask.partner_id,subtask.parent_id.partner_id,"Subtaskshouldhavethesamecustomerastheonefromtheirmother")

        #logtimesheetonsubtask
        timesheet2=Timesheet.create({
            'name':'TestLineonsubtask',
            'project_id':subtask.project_id.id,
            'task_id':subtask.id,
            'unit_amount':50,
            'employee_id':self.employee_user.id,
        })

        self.assertEqual(subtask.project_id,timesheet2.project_id,"Thetimesheetisinthesubtaskproject")
        self.assertNotEqual(self.project_employee_rate_user.project_id,timesheet2.project_id,"Thetimesheetshouldnotbelinkedtothebillingprojectforthemap")
        self.assertFalse(timesheet2.so_line,"ThetimesheetshouldnotbelinkedtoSOLasthetaskisinanonbillableproject")

        #movetaskintotaskrateproject
        task.write({
            'project_id':self.project_task_rate.id,
        })
        task._onchange_project()

        self.assertTrue(task.allow_billable,"Taskinproject'taskrate'shouldbebilledattaskrate")
        self.assertEqual(task.sale_line_id,self.project_task_rate.sale_line_id,"Taskmovedinataskratebillableproject")
        self.assertEqual(task.partner_id,task.project_id.partner_id,"Taskcreatedinaprojectbilledon'employeerate'shouldhavethesamecustomerastheonefromtheproject")

        #movesubtaskintotaskrateproject
        subtask.write({
            'project_id':self.project_task_rate2.id,
        })

        self.assertTrue(task.allow_billable,"Subtaskshouldkeepthebillabletypefromitsparent,evenwhentheyaremovedintoanotherproject")
        self.assertEqual(task.sale_line_id,self.project_task_rate.sale_line_id,"Subtaskshouldkeepthesamesaleorderlinethantheirmother,evenwhentheyaremovedintoanotherproject")

        #createasecondtaskinemployeerateproject
        task2=Task.with_context(default_project_id=self.project_employee_rate.id).create({
            'name':'firsttask',
            'partner_id':self.partner_a.id,
            'sale_line_id':False
        })

        #logtimesheetontaskin'employeerate'projectwithoutanyfallback(nomap,noSOLontask,noSOLonproject)
        timesheet3=Timesheet.create({
            'name':'TestLine',
            'project_id':task2.project_id.id,
            'task_id':task2.id,
            'unit_amount':3,
            'employee_id':self.employee_tde.id,
        })

        self.assertFalse(timesheet3.so_line,"ThetimesheetshouldnotbelinkedtoSOLasthereisnofallbackatall(nomap,noSOLontask,noSOLonproject)")

        #logtimesheetontaskin'employeerate'project(nomap,noSOLontask,butSOLonproject)
        timesheet4=Timesheet.create({
            'name':'TestLine',
            'project_id':task2.project_id.id,
            'task_id':task2.id,
            'unit_amount':4,
            'employee_id':self.employee_tde.id,
        })

        self.assertFalse(timesheet4.so_line,"ThetimesheetshouldnotbelinkedtoSOL,asnoentryforTDEinprojectmap")

    deftest_billing_task_rate(self):
        """
        Checktaskandsubtaskcreation,andtimesheetinginaprojectbilledat'taskrate'.
        Thenmovethetaskintoa'employeerate'projectthen,'nonbillable'.
        """
        Task=self.env['project.task'].with_context(tracking_disable=True)
        Timesheet=self.env['account.analytic.line']

        #setsubtaskprojectontaskrateproject
        self.project_task_rate.write({'subtask_project_id':self.project_subtask.id})

        #createatask
        task=Task.with_context(default_project_id=self.project_task_rate.id).create({
            'name':'firsttask',
        })
        task._onchange_project()

        self.assertEqual(task.sale_line_id,self.project_task_rate.sale_line_id,"Taskcreatedinaprojectbilledon'taskrate'shouldbelinkedtoaSOLoftheproject")
        self.assertEqual(task.partner_id,task.project_id.partner_id,"Taskcreatedinaprojectbilledon'employeerate'shouldhavethesamecustomerastheonefromtheproject")

        #logtimesheetontask
        timesheet1=Timesheet.create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':50,
            'employee_id':self.employee_manager.id,
        })

        self.assertEqual(self.project_task_rate.sale_line_id,timesheet1.so_line,"ThetimesheetshouldbelinkedtotheSOLassociatedtotheEmployeemanagerinthemap")

        #createasubtask
        subtask=Task.with_context(default_project_id=self.project_task_rate.subtask_project_id.id).create({
            'name':'firstsubtasktask',
            'parent_id':task.id,
        })

        self.assertEqual(subtask.partner_id,subtask.parent_id.partner_id,"Subtaskshouldhavethesamecustomerastheonefromtheirmother")

        #logtimesheetonsubtask
        timesheet2=Timesheet.create({
            'name':'TestLineonsubtask',
            'project_id':subtask.project_id.id,
            'task_id':subtask.id,
            'unit_amount':50,
            'employee_id':self.employee_user.id,
        })

        self.assertEqual(subtask.project_id,timesheet2.project_id,"Thetimesheetisinthesubtaskproject")
        self.assertFalse(timesheet2.so_line,"ThetimesheetshouldnotbelinkedtoSOLasit'sanonbillableproject")

        #movetaskandsubtaskintotaskrateproject
        task.write({
            'project_id':self.project_employee_rate.id,
        })
        task._onchange_project()
        subtask.write({
            'project_id':self.project_employee_rate.id,
        })
        subtask._onchange_project()

        self.assertFalse(task.sale_line_id,"Taskmovedinaemployeeratebillableprojecthaveemptysoline")
        self.assertEqual(task.partner_id,task.project_id.partner_id,"Taskcreatedinaprojectbilledon'employeerate'shouldhavethesamecustomerastheonefromtheproject")

        self.assertFalse(subtask.sale_line_id,"Subaskmovedinaemployeeratebillableprojecthaveemptysoline")
        self.assertEqual(subtask.partner_id,task.project_id.partner_id,"Subaskcreatedinaprojectbilledon'employeerate'shouldhavethesamecustomerastheonefromtheproject")
