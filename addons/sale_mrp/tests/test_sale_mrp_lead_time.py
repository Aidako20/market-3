#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectraimportfields
fromflectra.addons.stock.tests.common2importTestStockCommon

fromflectra.testsimportForm


classTestSaleMrpLeadTime(TestStockCommon):

    defsetUp(self):
        super(TestSaleMrpLeadTime,self).setUp()
        self.env.ref('stock.route_warehouse0_mto').active=True
        #Updatetheproduct_1withtype,route,ManufacturingLeadTimeandCustomerLeadTime
        withForm(self.product_1)asp1:
            p1.type='product'
            p1.produce_delay=5.0
            p1.sale_delay=5.0
            p1.route_ids.clear()
            p1.route_ids.add(self.warehouse_1.manufacture_pull_id.route_id)
            p1.route_ids.add(self.warehouse_1.mto_pull_id.route_id)

        #Updatetheproduct_2withtype
        withForm(self.product_2)asp2:
            p2.type='consu'

        #CreateBillofmaterialsforproduct_1
        withForm(self.env['mrp.bom'])asbom:
            bom.product_tmpl_id=self.product_1.product_tmpl_id
            bom.product_qty=2
            withbom.bom_line_ids.new()asline:
                line.product_id=self.product_2
                line.product_qty=4

    deftest_00_product_company_level_delays(self):
        """Inordertocheckscheduledate,setproduct'sManufacturingLeadTime
            andCustomerLeadTimeandalsosetcompany'sManufacturingLeadTime
            andSalesSafetyDays."""

        company=self.env.ref('base.main_company')

        #UpdatecompanywithManufacturingLeadTimeandSalesSafetyDays
        company.write({'manufacturing_lead':3.0,
                       'security_lead':3.0})

        #Createsaleorderofproduct_1
        order_form=Form(self.env['sale.order'])
        order_form.partner_id=self.partner_1
        withorder_form.order_line.new()asline:
            line.product_id=self.product_1
            line.product_uom_qty=10
        order=order_form.save()
        #Confirmsaleorder
        order.action_confirm()

        #Checkmanufacturingordercreatedornot
        manufacturing_order=self.env['mrp.production'].search([('product_id','=',self.product_1.id),('move_dest_ids','in',order.picking_ids[0].move_lines.ids)])
        self.assertTrue(manufacturing_order,'Manufacturingordershouldbecreated.')

        #Checkscheduledateofpicking
        deadline_picking=fields.Datetime.from_string(order.date_order)+timedelta(days=self.product_1.sale_delay)
        out_date=deadline_picking-timedelta(days=company.security_lead)
        self.assertAlmostEqual(
            order.picking_ids[0].scheduled_date,out_date,
            delta=timedelta(seconds=1),
            msg='Scheduledateofpickingshouldbeequalto:Orderdate+CustomerLeadTime-SalesSafetyDays.'
        )
        self.assertAlmostEqual(
            order.picking_ids[0].date_deadline,deadline_picking,
            delta=timedelta(seconds=1),
            msg='Deadlinedateofpickingshouldbeequalto:Orderdate+CustomerLeadTime.'
        )

        #Checkscheduledateanddeadlineofmanufacturingorder
        mo_scheduled=out_date-timedelta(days=self.product_1.produce_delay)-timedelta(days=company.manufacturing_lead)
        self.assertAlmostEqual(
            fields.Datetime.from_string(manufacturing_order.date_planned_start),mo_scheduled,
            delta=timedelta(seconds=1),
            msg="Scheduledateofmanufacturingordershouldbeequalto:Scheduledateofpicking-product'sManufacturingLeadTime-company'sManufacturingLeadTime."
        )
        self.assertAlmostEqual(
            fields.Datetime.from_string(manufacturing_order.date_deadline),deadline_picking,
            delta=timedelta(seconds=1),
            msg="Deadlinedateofmanufacturingordershouldbeequaltothedeadlineofsalepicking"
        )

    deftest_01_product_route_level_delays(self):
        """Inordertocheckscheduledates,setproduct'sManufacturingLeadTime
            andCustomerLeadTimeandalsosetwarehouseroute'sdelay."""

        #Updatewarehouse_1withOutgoingShippingspick+pack+ship
        self.warehouse_1.write({'delivery_steps':'pick_pack_ship'})

        #Setdelayonpullrule
        forpull_ruleinself.warehouse_1.delivery_route_id.rule_ids:
            pull_rule.write({'delay':2})

        #Createsaleorderofproduct_1
        order_form=Form(self.env['sale.order'])
        order_form.partner_id=self.partner_1
        order_form.warehouse_id=self.warehouse_1
        withorder_form.order_line.new()asline:
            line.product_id=self.product_1
            line.product_uom_qty=6
        order=order_form.save()
        #Confirmsaleorder
        order.action_confirm()

        #Runscheduler
        self.env['procurement.group'].run_scheduler()

        #Checkmanufacturingordercreatedornot
        manufacturing_order=self.env['mrp.production'].search([('product_id','=',self.product_1.id)])
        self.assertTrue(manufacturing_order,'Manufacturingordershouldbecreated.')

        #Checkthepickingcratedornot
        self.assertTrue(order.picking_ids,"Pickingsshouldbecreated.")

        #Checkscheduledateofshiptypepicking
        out=order.picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse_1.out_type_id)
        out_min_date=fields.Datetime.from_string(out.scheduled_date)
        out_date=fields.Datetime.from_string(order.date_order)+timedelta(days=self.product_1.sale_delay)-timedelta(days=out.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            out_min_date,out_date,
            delta=timedelta(seconds=10),
            msg='Scheduledateofshiptypepickingshouldbeequalto:orderdate+CustomerLeadTime-pullruledelay.'
        )

        #Checkscheduledateofpacktypepicking
        pack=order.picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse_1.pack_type_id)
        pack_min_date=fields.Datetime.from_string(pack.scheduled_date)
        pack_date=out_date-timedelta(days=pack.move_lines[0].rule_id.delay)
        self.assertAlmostEqual(
            pack_min_date,pack_date,
            delta=timedelta(seconds=10),
            msg='Scheduledateofpacktypepickingshouldbeequalto:Scheduledateofshiptypepicking-pullruledelay.'
        )

        #Checkscheduledateofpicktypepicking
        pick=order.picking_ids.filtered(lambdar:r.picking_type_id==self.warehouse_1.pick_type_id)
        pick_min_date=fields.Datetime.from_string(pick.scheduled_date)
        self.assertAlmostEqual(
            pick_min_date,pack_date,
            delta=timedelta(seconds=10),
            msg='Scheduledateofpicktypepickingshouldbeequalto:Scheduledateofpacktypepicking.'
        )

        #Checkscheduledateanddeadlinedateofmanufacturingorder
        mo_scheduled=out_date-timedelta(days=self.product_1.produce_delay)-timedelta(days=self.warehouse_1.delivery_route_id.rule_ids[0].delay)-timedelta(days=self.env.ref('base.main_company').manufacturing_lead)
        self.assertAlmostEqual(
            fields.Datetime.from_string(manufacturing_order.date_planned_start),mo_scheduled,
            delta=timedelta(seconds=1),
            msg="Scheduledateofmanufacturingordershouldbeequalto:Scheduledateofpicking-product'sManufacturingLeadTime-delaypull_rule."
        )
        self.assertAlmostEqual(
            manufacturing_order.date_deadline,order.picking_ids[0].date_deadline,
            delta=timedelta(seconds=1),
            msg="Deadlinedateofmanufacturingordershouldbeequaltothedeadlineofsalepicking"
        )
