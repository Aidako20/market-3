#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale_timesheet.tests.commonimportTestCommonSaleTimesheet
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestSaleService(TestCommonSaleTimesheet):
    """Thistestsuiteprovidechecksformiscellaneoussmallthings."""

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.sale_order=cls.env['sale.order'].with_context(mail_notrack=True,mail_create_nolog=True).create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
        })

    deftest_sale_service(self):
        """Testtaskcreationwhenconfirmingasale_orderwiththecorrespondingproduct"""
        sale_order_line=self.env['sale.order.line'].create({
            'order_id':self.sale_order.id,
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price
        })

        self.sale_order.order_line._compute_product_updatable()
        self.assertTrue(sale_order_line.product_updatable)
        self.sale_order.action_confirm()
        self.sale_order.order_line._compute_product_updatable()

        self.sale_order.action_confirm()
        self.sale_order.order_line._compute_product_updatable()
        self.assertFalse(sale_order_line.product_updatable)
        self.assertEqual(self.sale_order.invoice_status,'no','SaleService:thereshouldbenothingtoinvoiceaftervalidation')

        #checktaskcreation
        project=self.project_global
        task=project.task_ids.filtered(lambdat:t.name=='%s:%s'%(self.sale_order.name,self.product_delivery_timesheet2.name))
        self.assertTrue(task,'SaleService:taskisnotcreated,oritbadlynamed')
        self.assertEqual(task.partner_id,self.sale_order.partner_id,'SaleService:customershouldbethesameontaskandonSO')
        self.assertEqual(task.email_from,self.sale_order.partner_id.email,'SaleService:TaskEmailshouldbethesameastheSOcustomerEmail')

        #logtimesheetontask
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':project.id,
            'task_id':task.id,
            'unit_amount':50,
            'employee_id':self.employee_manager.id,
        })
        self.assertEqual(self.sale_order.invoice_status,'toinvoice','SaleService:thereshouldbesale_ordermethingtoinvoiceafterregisteringtimesheets')
        self.sale_order._create_invoices()

        self.assertTrue(sale_order_line.product_uom_qty==sale_order_line.qty_delivered==sale_order_line.qty_invoiced,'SaleService:lineshouldbeinvoicedcompletely')
        self.assertEqual(self.sale_order.invoice_status,'invoiced','SaleService:SOshouldbeinvoiced')
        self.assertEqual(self.sale_order.tasks_count,1,"AtaskshouldhavebeencreatedonSOconfirmation.")

        #AddalineontheconfirmedSO,anditshouldgenerateanewtaskdirectly
        product_service_task=self.env['product.product'].create({
            'name':"DeliveredService",
            'standard_price':30,
            'list_price':90,
            'type':'service',
            'invoice_policy':'delivery',
            'uom_id':self.env.ref('uom.product_uom_hour').id,
            'uom_po_id':self.env.ref('uom.product_uom_hour').id,
            'default_code':'SERV-DELI',
            'service_type':'timesheet',
            'service_tracking':'task_global_project',
            'project_id':project.id
        })

        self.env['sale.order.line'].create({
            'name':product_service_task.name,
            'product_id':product_service_task.id,
            'product_uom_qty':10,
            'product_uom':product_service_task.uom_id.id,
            'price_unit':product_service_task.list_price,
            'order_id':self.sale_order.id,
        })

        self.assertEqual(self.sale_order.tasks_count,2,"AddinganewservicelineonaconfirmerSOshouldcreateanewtask.")

        #notpossibletodeleteatasklinkedtoaSOL
        withself.assertRaises(ValidationError):
            task.unlink()

    deftest_timesheet_uom(self):
        """Testtimesheetinvoicinganduomconversion"""
        #createSOandconfirmit
        uom_days=self.env.ref('uom.product_uom_day')
        sale_order_line=self.env['sale.order.line'].create({
            'order_id':self.sale_order.id,
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':5,
            'product_uom':uom_days.id,
            'price_unit':self.product_delivery_timesheet3.list_price
        })
        self.sale_order.action_confirm()
        task=self.env['project.task'].search([('sale_line_id','=',sale_order_line.id)])

        #let'slogsometimesheets
        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':16,
            'employee_id':self.employee_manager.id,
        })
        self.assertEqual(sale_order_line.qty_delivered,2,'Sale:uomconversionoftimesheetsiswrong')

        self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task.project_id.id,
            'task_id':task.id,
            'unit_amount':24,
            'employee_id':self.employee_user.id,
        })
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.invoice_status,'invoiced','SaleTimesheet:"invoiceondelivery"timesheetsshouldnotmodifytheinvoice_statusoftheso')

    deftest_task_so_line_assignation(self):
        #createSOlineandconfirmit
        so_line_deliver_global_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':10,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price,
            'order_id':self.sale_order.id,
        })
        so_line_deliver_global_project.product_id_change()
        self.sale_order.action_confirm()
        task_serv2=self.env['project.task'].search([('sale_line_id','=',so_line_deliver_global_project.id)])

        #let'slogsometimesheets(ontheprojectcreatedbyso_line_ordered_project_only)
        timesheets=self.env['account.analytic.line']
        timesheets|=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':4,
            'employee_id':self.employee_user.id,
        })
        timesheets|=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':1,
            'employee_id':self.employee_manager.id,
        })
        self.assertTrue(all([billing_type=='billable_time'forbilling_typeintimesheets.mapped('timesheet_invoice_type')]),"Alltimesheetslinkedtothetaskshouldbeon'billabletime'")
        self.assertEqual(so_line_deliver_global_project.qty_to_invoice,5,"Quantitytoinvoiceshouldhavebeenincreasedwhenloggingtimesheetondeliveredquantitiestask")

        #invoiceSO,andvalidateinvoice
        invoice=self.sale_order._create_invoices()[0]
        invoice.action_post()

        #maketasknonbillable
        task_serv2.write({'sale_line_id':False})
        self.assertTrue(all([billing_type=='billable_time'forbilling_typeintimesheets.mapped('timesheet_invoice_type')]),"billabletypeoftimesheetshouldnotchangewhentranferingtaskintoanotherproject")
        self.assertEqual(task_serv2.timesheet_ids.mapped('so_line'),so_line_deliver_global_project,"OldinvoicedtimesheetarenotmodifiedwhenchangingthetaskSOline")

        #trytoupdatetimesheets,catcherror'Youcannotmodifyinvoicedtimesheet'
        withself.assertRaises(UserError):
            timesheets.write({'so_line':False})

    deftest_delivered_quantity(self):
        #createSOlineandconfirmit
        so_line_deliver_new_task_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':10,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })
        so_line_deliver_new_task_project.product_id_change()
        self.sale_order.action_confirm()
        task_serv2=self.env['project.task'].search([('sale_line_id','=',so_line_deliver_new_task_project.id)])

        #addatimesheet
        timesheet1=self.env['account.analytic.line'].create({
            'name':'TestLine',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':4,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(so_line_deliver_new_task_project.qty_delivered,timesheet1.unit_amount,'Deliveredquantityshouldbethesamethenitsonlyrelatedtimesheet.')

        #removetheonlytimesheet
        timesheet1.unlink()
        self.assertEqual(so_line_deliver_new_task_project.qty_delivered,0.0,'Deliveredquantityshouldberesettozero,sincethereisnomoretimesheet.')

        #log2newtimesheets
        timesheet2=self.env['account.analytic.line'].create({
            'name':'TestLine2',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':4,
            'employee_id':self.employee_user.id,
        })
        timesheet3=self.env['account.analytic.line'].create({
            'name':'TestLine3',
            'project_id':task_serv2.project_id.id,
            'task_id':task_serv2.id,
            'unit_amount':2,
            'employee_id':self.employee_user.id,
        })
        self.assertEqual(so_line_deliver_new_task_project.qty_delivered,timesheet2.unit_amount+timesheet3.unit_amount,'Deliveredquantityshouldbethesumofthe2timesheetsunitamounts.')

        #removetimesheet2
        timesheet2.unlink()
        self.assertEqual(so_line_deliver_new_task_project.qty_delivered,timesheet3.unit_amount,'Deliveredquantityshouldberesettothesumofremainingtimesheetsunitamounts.')

    deftest_sale_create_task(self):
        """CheckthatconfirmingSOcreatecorrectlyatask,andreconfirmingitdoesnotcreateasecondone.Alsocheckchanging
            theorderedquantityofaSOlinethathavecreatedataskshouldupdatetheplannedhoursofthistask.
        """
        so_line1=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':7,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })

        #confirmSO
        self.sale_order.action_confirm()

        self.assertTrue(so_line1.task_id,"SOconfirmationshouldcreateataskandlinkittoSOL")
        self.assertTrue(so_line1.project_id,"SOconfirmationshouldcreateaprojectandlinkittoSOL")
        self.assertEqual(self.sale_order.tasks_count,1,"TheSOshouldhaveonlyonetask")
        self.assertEqual(so_line1.task_id.sale_line_id,so_line1,"Thecreatedtaskisalsolinkedtoitsoriginsaleline,forinvoicingpurpose.")
        self.assertFalse(so_line1.task_id.user_id,"Thecreatedtaskshouldbeunassigned")
        self.assertEqual(so_line1.product_uom_qty,so_line1.task_id.planned_hours,"TheplannedhoursshouldbethesameastheorderedquantityofthenativeSOline")

        so_line1.write({'product_uom_qty':20})
        self.assertEqual(so_line1.product_uom_qty,so_line1.task_id.planned_hours,"TheplannedhoursshouldhavechangedwhenupdatingtheorderedquantityofthenativeSOline")

        #cancelSO
        self.sale_order.action_cancel()

        self.assertTrue(so_line1.task_id,"SOcancellationshouldkeepthetask")
        self.assertTrue(so_line1.project_id,"SOcancellationshouldcreateaproject")
        self.assertEqual(self.sale_order.tasks_count,1,"TheSOshouldstillhaveonlyonetask")
        self.assertEqual(so_line1.task_id.sale_line_id,so_line1,"Thecreatedtaskisalsolinkedtoitsoriginsaleline,forinvoicingpurpose.")

        so_line1.write({'product_uom_qty':30})
        self.assertEqual(so_line1.product_uom_qty,so_line1.task_id.planned_hours,"Theplannedhoursshouldhavechangedwhenupdatingtheorderedquantity,evenafterSOcancellation")

        #reconfirmSO
        self.sale_order.action_draft()
        self.sale_order.action_confirm()

        self.assertTrue(so_line1.task_id,"SOreconfirmationshouldnothavecreateanothertask")
        self.assertTrue(so_line1.project_id,"SOreconfirmationshouldbithavecreateanotherproject")
        self.assertEqual(self.sale_order.tasks_count,1,"TheSOshouldstillhaveonlyonetask")
        self.assertEqual(so_line1.task_id.sale_line_id,so_line1,"Thecreatedtaskisalsolinkedtoitsoriginsaleline,forinvoicingpurpose.")

        self.sale_order.action_done()
        withself.assertRaises(UserError):
            so_line1.write({'product_uom_qty':20})

    deftest_sale_create_project(self):
        """ASOwithmultipleproductthatshouldcreateproject(withandwithouttemplate)like;
                Line1:Service1createprojectwithTemplateA===>projectcreatedwithtemplateA
                Line2:Service2createprojectnotemplate==>emptyprojectcreated
                Line3:Service3createprojectwithTemplateA===>Don'tcreateanyprojectbecauseline1hasalreadycreatedaprojectwithtemplateA
                Line4:Service4createprojectnotemplate==>Don'tcreateanyprojectbecauseline2hasalreadycreatedanemptyproject
                Line5:Service5createprojectwithTemplateB===>projectcreatedwithtemplateB
        """
        #secondprojecttemplateanditsassociatedproduct
        project_template2=self.env['project.project'].create({
            'name':'SecondProjectTEMPLATEforservices',
            'allow_timesheets':True,
            'active':False, #thistemplateisarchived
        })
        Stage=self.env['project.task.type'].with_context(default_project_id=project_template2.id)
        stage1_tmpl2=Stage.create({
            'name':'Stage1',
            'sequence':1
        })
        stage2_tmpl2=Stage.create({
            'name':'Stage2',
            'sequence':2
        })
        product_deli_ts_tmpl=self.env['product.product'].create({
            'name':"Servicedelivered,createprojectonlybasedontemplateB",
            'standard_price':17,
            'list_price':34,
            'type':'service',
            'invoice_policy':'delivery',
            'uom_id':self.env.ref('uom.product_uom_hour').id,
            'uom_po_id':self.env.ref('uom.product_uom_hour').id,
            'default_code':'SERV-DELI4',
            'service_type':'timesheet',
            'service_tracking':'project_only',
            'project_template_id':project_template2.id,
            'project_id':False,
            'taxes_id':False,
            'property_account_income_id':self.account_sale.id,
        })

        #create5solines
        so_line1=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet5.name,
            'product_id':self.product_delivery_timesheet5.id,
            'product_uom_qty':11,
            'product_uom':self.product_delivery_timesheet5.uom_id.id,
            'price_unit':self.product_delivery_timesheet5.list_price,
            'order_id':self.sale_order.id,
        })
        so_line2=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet4.name,
            'product_id':self.product_order_timesheet4.id,
            'product_uom_qty':10,
            'product_uom':self.product_order_timesheet4.uom_id.id,
            'price_unit':self.product_order_timesheet4.list_price,
            'order_id':self.sale_order.id,
        })
        so_line3=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet5.name,
            'product_id':self.product_delivery_timesheet5.id,
            'product_uom_qty':5,
            'product_uom':self.product_delivery_timesheet5.uom_id.id,
            'price_unit':self.product_delivery_timesheet5.list_price,
            'order_id':self.sale_order.id,
        })
        so_line4=self.env['sale.order.line'].create({
            'name':self.product_delivery_manual3.name,
            'product_id':self.product_delivery_manual3.id,
            'product_uom_qty':4,
            'product_uom':self.product_delivery_manual3.uom_id.id,
            'price_unit':self.product_delivery_manual3.list_price,
            'order_id':self.sale_order.id,
        })
        so_line5=self.env['sale.order.line'].create({
            'name':product_deli_ts_tmpl.name,
            'product_id':product_deli_ts_tmpl.id,
            'product_uom_qty':8,
            'product_uom':product_deli_ts_tmpl.uom_id.id,
            'price_unit':product_deli_ts_tmpl.list_price,
            'order_id':self.sale_order.id,
        })

        #confirmSO
        self.sale_order.action_confirm()

        #checkeachlinehasornogeneratesomething
        self.assertTrue(so_line1.project_id,"Line1shouldhavecreateaprojectbasedontemplateA")
        self.assertTrue(so_line2.project_id,"Line2shouldhavecreateanemptyproject")
        self.assertEqual(so_line3.project_id,so_line1.project_id,"Line3shouldreuseprojectofline1")
        self.assertEqual(so_line4.project_id,so_line2.project_id,"Line4shouldreuseprojectofline2")
        self.assertTrue(so_line4.task_id,"Line4shouldhavecreateanewtask,evenifnoprojectcreated.")
        self.assertTrue(so_line5.project_id,"Line5shouldhavecreateaprojectbasedontemplateB")

        #checkallgeneratedprojectshouldbeactive,evenifthetemplateisnot
        self.assertTrue(so_line1.project_id.active,"ProjectofLine1shouldbeactive")
        self.assertTrue(so_line2.project_id.active,"ProjectofLine2shouldbeactive")
        self.assertTrue(so_line5.project_id.active,"ProjectofLine5shouldbeactive")

        #checkgeneratedstuffarecorrect
        self.assertTrue(so_line1.project_idinself.project_template_state.project_ids,"Stage1fromtemplateBshouldbepartofprojectfromsoline1")
        self.assertTrue(so_line1.project_idinself.project_template_state.project_ids,"Stage1fromtemplateBshouldbepartofprojectfromsoline1")

        self.assertTrue(so_line5.project_idinstage1_tmpl2.project_ids,"Stage1fromtemplateBshouldbepartofprojectfromsoline5")
        self.assertTrue(so_line5.project_idinstage2_tmpl2.project_ids,"Stage2fromtemplateBshouldbepartofprojectfromsoline5")

        self.assertTrue(so_line1.project_id.allow_timesheets,"Createprojectshouldallowtimesheets")
        self.assertTrue(so_line2.project_id.allow_timesheets,"Createprojectshouldallowtimesheets")
        self.assertTrue(so_line5.project_id.allow_timesheets,"Createprojectshouldallowtimesheets")

        self.assertEqual(so_line4.task_id.project_id,so_line2.project_id,"Taskcreatedwithline4shouldhavetheprojectbasedontemplateAoftheSO.")

        self.assertEqual(so_line1.project_id.sale_line_id,so_line1,"SOlineofprojectwithtemplateAshouldbetheonethatcreateit.")
        self.assertEqual(so_line2.project_id.sale_line_id,so_line2,"SOlineofprojectshouldbetheonethatcreateit.")
        self.assertEqual(so_line5.project_id.sale_line_id,so_line5,"SOlineofprojectwithtemplateBshouldbetheonethatcreateit.")

    deftest_sale_task_in_project_with_project(self):
        """Thiswilltestthenew'task_in_project'servicetrackingcorrectlycreatestasksandprojects
            whenaproject_idisconfiguredontheparentsale_order(reftask#1915660).

            Setup:
            -Configureaproject_idontheSO
            -SOline1:aproductwithitsdeliverytrackingsetto'task_in_project'
            -SOline2:thesameproductasSOline1
            -SOline3:aproductwithitsdeliverytrackingsetto'project_only'
            -Confirmsale_order

            Expectedresult:
            -2taskscreatedontheproject_idconfiguredontheSO
            -1projectcreatedwiththecorrecttemplateforthe'project_only'product
        """

        self.sale_order.write({'project_id':self.project_global.id})
        self.sale_order._onchange_project_id()
        self.assertEqual(self.sale_order.analytic_account_id,self.analytic_account_sale,"ChangingtheprojectontheSOshouldsettheanalyticaccountaccordingly.")

        so_line1=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet3.name,
            'product_id':self.product_order_timesheet3.id,
            'product_uom_qty':11,
            'product_uom':self.product_order_timesheet3.uom_id.id,
            'price_unit':self.product_order_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })
        so_line2=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet3.name,
            'product_id':self.product_order_timesheet3.id,
            'product_uom_qty':10,
            'product_uom':self.product_order_timesheet3.uom_id.id,
            'price_unit':self.product_order_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })
        so_line3=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet4.name,
            'product_id':self.product_order_timesheet4.id,
            'product_uom_qty':5,
            'product_uom':self.product_order_timesheet4.uom_id.id,
            'price_unit':self.product_order_timesheet4.list_price,
            'order_id':self.sale_order.id,
        })

        #temporaryproject_template_idforourchecks
        self.product_order_timesheet4.write({
            'project_template_id':self.project_template.id
        })
        self.sale_order.action_confirm()
        #removeitaftertheconfirmbecauseothertestsdon'tlikeit
        self.product_order_timesheet4.write({
            'project_template_id':False
        })

        self.assertTrue(so_line1.task_id,"so_line1shouldcreateataskasitsproduct'sservice_trackingissetas'task_in_project'")
        self.assertEqual(so_line1.task_id.project_id,self.project_global,"Theprojectonso_line1'staskshouldbeproject_globalasconfiguredonitsparentsale_order")
        self.assertTrue(so_line2.task_id,"so_line2shouldcreateataskasitsproduct'sservice_trackingissetas'task_in_project'")
        self.assertEqual(so_line2.task_id.project_id,self.project_global,"Theprojectonso_line2'staskshouldbeproject_globalasconfiguredonitsparentsale_order")
        self.assertFalse(so_line3.task_id.name,"so_line3shouldnotcreateataskasitsproduct'sservice_trackingissetas'project_only'")
        self.assertNotEqual(so_line3.project_id,self.project_template,"so_line3shouldcreateanewprojectandnotdirectlyusetheconfiguredtemplate")
        self.assertIn(self.project_template.name,so_line3.project_id.name,"Thecreatedprojectforso_line3shouldusetheconfiguredtemplate")

    deftest_sale_task_in_project_without_project(self):
        """Thiswilltestthenew'task_in_project'servicetrackingcorrectlycreatestasksandprojects
            whentheparentsale_orderdoesNOThaveaconfiguredproject_id(reftask#1915660).

            Setup:
            -SOline1:aproductwithitsdeliverytrackingsetto'task_in_project'
            -Confirmsale_order

            Expectedresult:
            -1projectcreatedwiththecorrecttemplateforthe'task_in_project'becausetheSO
              doesnothaveaconfiguredproject_id
            -1taskcreatedfromthisnewproject
        """

        so_line1=self.env['sale.order.line'].create({
            'name':self.product_order_timesheet3.name,
            'product_id':self.product_order_timesheet3.id,
            'product_uom_qty':10,
            'product_uom':self.product_order_timesheet3.uom_id.id,
            'price_unit':self.product_order_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })

        #temporaryproject_template_idforourchecks
        self.product_order_timesheet3.write({
            'project_template_id':self.project_template.id
        })
        self.sale_order.action_confirm()
        #removeitaftertheconfirmbecauseothertestsdon'tlikeit
        self.product_order_timesheet3.write({
            'project_template_id':False
        })

        self.assertTrue(so_line1.task_id,"so_line1shouldcreateataskasitsproduct'sservice_trackingissetas'task_in_project'")
        self.assertNotEqual(so_line1.project_id,self.project_template,"so_line1shouldcreateanewprojectandnotdirectlyusetheconfiguredtemplate")
        self.assertIn(self.project_template.name,so_line1.project_id.name,"Thecreatedprojectforso_line1shouldusetheconfiguredtemplate")

    deftest_billable_task_and_subtask(self):
        """TestifsubtasksandtasksarebilledonthecorrectSOline"""
        #createSOlineandconfirmit
        so_line_deliver_new_task_project=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':10,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })
        so_line_deliver_new_task_project_2=self.env['sale.order.line'].create({
            'name':self.product_delivery_timesheet3.name+"(2)",
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':10,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price,
            'order_id':self.sale_order.id,
        })
        so_line_deliver_new_task_project.product_id_change()
        so_line_deliver_new_task_project_2.product_id_change()
        self.sale_order.action_confirm()

        project=so_line_deliver_new_task_project.project_id
        task=so_line_deliver_new_task_project.task_id

        self.assertEqual(project.sale_line_id,so_line_deliver_new_task_project,"Thecreatedprojectshouldbelinkedtothesoline")
        self.assertEqual(task.sale_line_id,so_line_deliver_new_task_project,"Thecreatedtaskshouldbelinkedtothesoline")

        #createanewtaskandsubtask
        subtask=self.env['project.task'].create({
            'parent_id':task.id,
            'project_id':project.id,
            'name':'%s:substask1'%(task.name,),
        })
        task2=self.env['project.task'].create({
            'project_id':project.id,
            'name':'%s:substask1'%(task.name,)
        })

        self.assertEqual(subtask.sale_line_id,task.sale_line_id,"By,default,achildtaskshouldhavethesameSOlineasitsmother")
        self.assertEqual(task2.sale_line_id,project.sale_line_id,"AnewtaskinabillableprojectshouldhavethesameSOlineasitsproject")
        self.assertEqual(task2.partner_id,so_line_deliver_new_task_project.order_partner_id,"AnewtaskinabillableprojectshouldhavethesameSOlineasitsproject")

        #movingsubtaskinanotherproject
        subtask.write({'project_id':self.project_global.id})

        self.assertEqual(subtask.sale_line_id,task.sale_line_id,"AchildtaskshouldalwayshavethesameSOlineasitsmother,evenwhenchangingproject")
        self.assertEqual(subtask.sale_line_id,so_line_deliver_new_task_project)

        #changingtheSOlineofthemothertask
        task.write({'sale_line_id':so_line_deliver_new_task_project_2.id})

        self.assertEqual(subtask.sale_line_id,so_line_deliver_new_task_project,"AchildtaskisnotimpactedbythechangeofSOlineofitsmother")
        self.assertEqual(task.sale_line_id,so_line_deliver_new_task_project_2,"AmothertaskcanhaveitsSOlinesetmanually")

        #changingtheSOlineofasubtask
        subtask.write({'sale_line_id':so_line_deliver_new_task_project_2.id})

        self.assertEqual(subtask.sale_line_id,so_line_deliver_new_task_project_2,"AchildcanhaveitsSOlinesetmanually")

    deftest_change_ordered_qty(self):
        """ChangingtheorderedquantityofaSOlinethathavecreatedataskshouldupdatetheplannedhoursofthistask"""
        sale_order_line=self.env['sale.order.line'].create({
            'order_id':self.sale_order.id,
            'name':self.product_delivery_timesheet2.name,
            'product_id':self.product_delivery_timesheet2.id,
            'product_uom_qty':50,
            'product_uom':self.product_delivery_timesheet2.uom_id.id,
            'price_unit':self.product_delivery_timesheet2.list_price
        })

        self.sale_order.action_confirm()
        self.assertEqual(sale_order_line.product_uom_qty,sale_order_line.task_id.planned_hours,"TheplannedhoursshouldbethesameastheorderedquantityofthenativeSOline")

        sale_order_line.write({'product_uom_qty':20})
        self.assertEqual(sale_order_line.product_uom_qty,sale_order_line.task_id.planned_hours,"TheplannedhoursshouldhavechangedwhenupdatingtheorderedquantityofthenativeSOline")

        self.sale_order.action_cancel()
        sale_order_line.write({'product_uom_qty':30})
        self.assertEqual(sale_order_line.product_uom_qty,sale_order_line.task_id.planned_hours,"Theplannedhoursshouldhavechangedwhenupdatingtheorderedquantity,evenafterSOcancellation")

        self.sale_order.action_done()
        withself.assertRaises(UserError):
            sale_order_line.write({'product_uom_qty':20})

    deftest_copy_billable_project_and_task(self):
        sale_order_line=self.env['sale.order.line'].create({
            'order_id':self.sale_order.id,
            'name':self.product_delivery_timesheet3.name,
            'product_id':self.product_delivery_timesheet3.id,
            'product_uom_qty':5,
            'product_uom':self.product_delivery_timesheet3.uom_id.id,
            'price_unit':self.product_delivery_timesheet3.list_price
        })
        self.sale_order.action_confirm()
        task=self.env['project.task'].search([('sale_line_id','=',sale_order_line.id)])
        project=sale_order_line.project_id

        #copytheproject
        project_copy=project.copy()
        self.assertFalse(project_copy.sale_line_id,"DuplicatingprojectshoulderaseitsSaleline")
        self.assertFalse(project_copy.sale_order_id,"DuplicatingprojectshoulderaseitsSaleorder")
        self.assertEqual(len(project.tasks),len(project_copy.tasks),"Copiedprojectmusthavethesamenumberoftasks")
        self.assertFalse(project_copy.tasks.mapped('sale_line_id'),"ThetasksoftheduplicatedprojectshouldnothaveaSaleLineset.")

        #copythetask
        task_copy=task.copy()
        self.assertEqual(task_copy.sale_line_id,task.sale_line_id,"DuplicatingtaskshouldkeepitsSaleline")
