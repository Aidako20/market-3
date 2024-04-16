#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.addons.sale.tests.commonimportTestSaleCommon
fromflectraimportfields
fromflectra.testsimporttagged

fromdatetimeimporttimedelta


@tagged('post_install','-at_install')
classTestSaleStockLeadTime(TestSaleCommon,ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #Updatetheproduct_1withtypeandCustomerLeadTime
        cls.test_product_order.sale_delay=5.0

    deftest_00_product_company_level_delays(self):
        """Inordertocheckscheduledate,setproduct'sCustomerLeadTime
            andcompany'sSalesSafetyDays."""

        #UpdatecompanywithSalesSafetyDays
        self.env.company.security_lead=3.00

        #Createsaleorderofproduct_1
        order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
            'picking_policy':'direct',
            'warehouse_id':self.company_data['default_warehouse'].id,
            'order_line':[(0,0,{'name':self.test_product_order.name,
                                   'product_id':self.test_product_order.id,
                                   'product_uom_qty':10,
                                   'product_uom':self.env.ref('uom.product_uom_unit').id,
                                   'customer_lead':self.test_product_order.sale_delay})]})

        #Confirmourstandardsaleorder
        order.action_confirm()

        #Checkthepickingcratedornot
        self.assertTrue(order.picking_ids,"Pickingshouldbecreated.")

        #Checkscheduledateofpicking
        out_date=fields.Datetime.from_string(order.date_order)+timedelta(days=self.test_product_order.sale_delay)-timedelta(days=self.env.company.security_lead)
        min_date=fields.Datetime.from_string(order.picking_ids[0].scheduled_date)
        self.assertTrue(abs(min_date-out_date)<=timedelta(seconds=1),'Scheduledateofpickingshouldbeequalto:orderdate+CustomerLeadTime-SalesSafetyDays.')

    deftest_01_product_route_level_delays(self):
        """Inordertocheckscheduledates,setproduct'sCustomerLeadTime
            andwarehouseroute'sdelay."""

        #Updatewarehouse_1withOutgoingShippingspick+pack+ship
        self.company_data['default_warehouse'].write({'delivery_steps':'pick_pack_ship'})

        #Setdelayonpullrule
        forpull_ruleinself.company_data['default_warehouse'].delivery_route_id.rule_ids:
            pull_rule.write({'delay':2})

        #Createsaleorderofproduct_1
        order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
            'picking_policy':'direct',
            'warehouse_id':self.company_data['default_warehouse'].id,
            'order_line':[(0,0,{'name':self.test_product_order.name,
                                   'product_id':self.test_product_order.id,
                                   'product_uom_qty':5,
                                   'product_uom':self.env.ref('uom.product_uom_unit').id,
                                   'customer_lead':self.test_product_order.sale_delay})]})

        #Confirmourstandardsaleorder
        order.action_confirm()

        #Checkthepickingcratedornot
        self.assertTrue(order.picking_ids,"Pickingsshouldbecreated.")

        #Checkscheduledateofshiptypepicking
        out=order.picking_ids.filtered(lambdar:r.picking_type_id==self.company_data['default_warehouse'].out_type_id)
        out_min_date=fields.Datetime.from_string(out.scheduled_date)
        out_date=fields.Datetime.from_string(order.date_order)+timedelta(days=self.test_product_order.sale_delay)-timedelta(days=out.move_lines[0].rule_id.delay)
        self.assertTrue(abs(out_min_date-out_date)<=timedelta(seconds=1),'Scheduledateofshiptypepickingshouldbeequalto:orderdate+CustomerLeadTime-pullruledelay.')

        #Checkscheduledateofpacktypepicking
        pack=order.picking_ids.filtered(lambdar:r.picking_type_id==self.company_data['default_warehouse'].pack_type_id)
        pack_min_date=fields.Datetime.from_string(pack.scheduled_date)
        pack_date=out_date-timedelta(days=pack.move_lines[0].rule_id.delay)
        self.assertTrue(abs(pack_min_date-pack_date)<=timedelta(seconds=1),'Scheduledateofpacktypepickingshouldbeequalto:Scheduledateofshiptypepicking-pullruledelay.')

        #Checkscheduledateofpicktypepicking
        pick=order.picking_ids.filtered(lambdar:r.picking_type_id==self.company_data['default_warehouse'].pick_type_id)
        pick_min_date=fields.Datetime.from_string(pick.scheduled_date)
        pick_date=pack_date-timedelta(days=pick.move_lines[0].rule_id.delay)
        self.assertTrue(abs(pick_min_date-pick_date)<=timedelta(seconds=1),'Scheduledateofpicktypepickingshouldbeequalto:Scheduledateofpacktypepicking-pullruledelay.')

    deftest_02_delivery_date_propagation(self):
        """Inordertocheckdeadlinedatepropagation,setproduct'sCustomerLeadTime
            andwarehouseroute'sdelayinstockrules"""

        #Example:
        #->SetWarehousewithOutgoingShipments:pick+pack+ship
        #->SetDelay:5daysonstockrules
        #->SetCustomerLeadTimeonproduct:30days
        #->SetSalesSafetyDays:2days
        #->CreateanSOandconfirmitwithconfirmationDate:12/18/2018

        #->Pickings:OUT->ScheduledDate:01/12/2019,DeadlineDate:01/14/2019
        #             PACK->ScheduledDate:01/07/2019,DeadlineDate:01/09/2019
        #             PICK->ScheduledDate:01/02/2019,DeadlineDate:01/04/2019

        #->Now,changecommitment_dateinthesaleorder=out_deadline_date+5days

        #->DeadlineDateshouldbechangedandScheduleddateshouldbeunchanged:
        #             OUT ->DeadlineDate:01/19/2019
        #             PACK->DeadlineDate:01/14/2019
        #             PICK->DeadlineDate:01/09/2019

        #UpdatecompanywithSalesSafetyDays
        self.env.company.security_lead=2.00

        #Updatewarehouse_1withOutgoingShippingspick+pack+ship
        self.company_data['default_warehouse'].write({'delivery_steps':'pick_pack_ship'})

        #Setdelayonpullrule
        self.company_data['default_warehouse'].delivery_route_id.rule_ids.write({'delay':5})

        #Updatetheproduct_1withtypeandCustomerLeadTime
        self.test_product_order.write({'type':'product','sale_delay':30.0})

        #Now,createsaleorderofproduct_1withcustomer_leadsetonproduct
        order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
            'picking_policy':'direct',
            'warehouse_id':self.company_data['default_warehouse'].id,
            'order_line':[(0,0,{'name':self.test_product_order.name,
                                   'product_id':self.test_product_order.id,
                                   'product_uom_qty':5,
                                   'product_uom':self.env.ref('uom.product_uom_unit').id,
                                   'customer_lead':self.test_product_order.sale_delay})]})

        #Confirmourstandardsaleorder
        order.action_confirm()

        #Checkthepickingcratedornot
        self.assertTrue(order.picking_ids,"Pickingsshouldbecreated.")

        #Checkschedule/deadlinedateofshiptypepicking
        out=order.picking_ids.filtered(lambdar:r.picking_type_id==self.company_data['default_warehouse'].out_type_id)
        deadline_date=order.date_order+timedelta(days=self.test_product_order.sale_delay)-timedelta(days=out.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            out.date_deadline,deadline_date,delta=timedelta(seconds=1),
            msg='Deadlinedateofshiptypepickingshouldbeequalto:orderdate+CustomerLeadTime-pullruledelay.')
        out_scheduled_date=deadline_date-timedelta(days=self.env.company.security_lead)
        self.assertAlmostEqual(
            out.scheduled_date,out_scheduled_date,delta=timedelta(seconds=1),
            msg='Scheduledateofshiptypepickingshouldbeequalto:orderdate+CustomerLeadTime-pullruledelay-security_lead')

        #Checkschedule/deadlinedateofpacktypepicking
        pack=order.picking_ids.filtered(lambdar:r.picking_type_id==self.company_data['default_warehouse'].pack_type_id)
        pack_scheduled_date=out_scheduled_date-timedelta(days=pack.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            pack.scheduled_date,pack_scheduled_date,delta=timedelta(seconds=1),
            msg='Scheduledateofpacktypepickingshouldbeequalto:Scheduledateofshiptypepicking-pullruledelay.')
        deadline_date-=timedelta(days=pack.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            pack.date_deadline,deadline_date,delta=timedelta(seconds=1),
            msg='Deadlinedateofpacktypepickingshouldbeequalto:Deadlinedateofshiptypepicking-pullruledelay.')

        #Checkschedule/deadlinedateofpicktypepicking
        pick=order.picking_ids.filtered(lambdar:r.picking_type_id==self.company_data['default_warehouse'].pick_type_id)
        pick_scheduled_date=pack_scheduled_date-timedelta(days=pick.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            pick.scheduled_date,pick_scheduled_date,delta=timedelta(seconds=1),
            msg='Scheduledateofpacktypepickingshouldbeequalto:Scheduledateofshiptypepicking-pullruledelay.')
        deadline_date-=timedelta(days=pick.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            pick.date_deadline,deadline_date,delta=timedelta(seconds=1),
            msg='Deadlinedateofpacktypepickingshouldbeequalto:Deadlinedateofshiptypepicking-pullruledelay.')

        #Nowchangethecommitmentdate(DeliveryDate)ofthesaleorder
        new_deadline=deadline_date+timedelta(days=5)
        order.write({'commitment_date':new_deadline})

        #Nowcheckdate_deadlineofpick,packandoutareforced
        #TODO:addnoteincaseofchangeofdeadlineandcheck
        self.assertEqual(out.date_deadline,new_deadline)
        new_deadline-=timedelta(days=pack.move_lines[0].rule_id.delay)
        self.assertEqual(pack.date_deadline,new_deadline)
        new_deadline-=timedelta(days=pick.move_lines[0].rule_id.delay)
        self.assertEqual(pick.date_deadline,new_deadline)
