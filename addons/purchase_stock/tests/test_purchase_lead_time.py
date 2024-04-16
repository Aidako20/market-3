#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta,time
fromunittest.mockimportpatch

fromflectraimportfields
from.commonimportPurchaseTestCommon
fromflectra.tests.commonimportForm


classTestPurchaseLeadTime(PurchaseTestCommon):

    deftest_00_product_company_level_delays(self):
        """Tocheckdates,setproduct'sDeliveryLeadTime
            andcompany'sPurchaseLeadTime."""

        company=self.env.ref('base.main_company')

        #UpdatecompanywithPurchaseLeadTime
        company.write({'po_lead':3.00})

        #Makeprocurementrequestfromproduct_1'sformview,createprocurementandcheckit'sstate
        date_planned=fields.Datetime.to_string(fields.datetime.now()+timedelta(days=10))
        self._create_make_procurement(self.product_1,15.00,date_planned=date_planned)
        purchase=self.env['purchase.order.line'].search([('product_id','=',self.product_1.id)],limit=1).order_id

        #Confirmpurchaseorder
        purchase.button_confirm()

        #Checkorderdateofpurchaseorder
        order_date=fields.Datetime.from_string(date_planned)-timedelta(days=company.po_lead)-timedelta(days=self.product_1.seller_ids.delay)
        self.assertEqual(purchase.date_order,order_date,'Orderdateshouldbeequalto:Dateoftheprocurementorder-PurchaseLeadTime-DeliveryLeadTime.')

        #Checkscheduleddateofpurchaseorder
        schedule_date=datetime.combine(order_date+timedelta(days=self.product_1.seller_ids.delay),time.min).replace(tzinfo=None,hour=12)
        self.assertEqual(purchase.order_line.date_planned,schedule_date,'Scheduledateshouldbeequalto:OrderdateofPurchaseorder+DeliveryLeadTime.')

        #checkthepickingcreatedornot
        self.assertTrue(purchase.picking_ids,"Pickingshouldbecreated.")

        #CheckscheduledanddeadlinedateofInTypeshipment
        self.assertEqual(purchase.picking_ids.scheduled_date,schedule_date,'ScheduledateofIntypeshipmentshouldbeequalto:scheduledateofpurchaseorder.')
        self.assertEqual(purchase.picking_ids.date_deadline,schedule_date+timedelta(days=company.po_lead),'Deadlinedateofshouldbeequalto:scheduledateofpurchaseorder+lead_po.')

    deftest_01_product_level_delay(self):
        """Tocheckscheduledatesofmultiplepurchaseorderlineofthesamepurchaseorder,
            wecreatetwoprocurementsforthetwodifferentproductwithsamevendor
            anddifferentDeliveryLeadTime."""

        company=self.env.ref('base.main_company')
        company.write({'po_lead':0.00})

        #Makeprocurementrequestfromproduct_1'sformview,createprocurementandcheckit'sstate
        date_planned1=fields.Datetime.to_string(fields.datetime.now()+timedelta(days=10))
        self._create_make_procurement(self.product_1,10.00,date_planned=date_planned1)
        purchase1=self.env['purchase.order.line'].search([('product_id','=',self.product_1.id)],limit=1).order_id

        #Makeprocurementrequestfromproduct_2'sformview,createprocurementandcheckit'sstate
        date_planned2=fields.Datetime.to_string(fields.datetime.now()+timedelta(days=10))
        self._create_make_procurement(self.product_2,5.00,date_planned=date_planned2)
        purchase2=self.env['purchase.order.line'].search([('product_id','=',self.product_2.id)],limit=1).order_id

        #Checkpurchaseorderissameornot
        self.assertEqual(purchase1,purchase2,'Purchaseordersshouldbesameforthetwodifferentproductwithsamevendor.')

        #Confirmpurchaseorder
        purchase1.button_confirm()

        #Checkorderdateofpurchaseorder
        order_line_pro_1=purchase2.order_line.filtered(lambdar:r.product_id==self.product_1)
        order_line_pro_2=purchase2.order_line.filtered(lambdar:r.product_id==self.product_2)
        order_date=fields.Datetime.from_string(date_planned1)-timedelta(days=self.product_1.seller_ids.delay)
        self.assertEqual(purchase2.date_order,order_date,'Orderdateshouldbeequalto:Dateoftheprocurementorder-DeliveryLeadTime.')

        #Checkscheduleddateofpurchaseorderlineforproduct_1
        schedule_date_1=datetime.combine(order_date+timedelta(days=self.product_1.seller_ids.delay),time.min).replace(tzinfo=None,hour=12)
        self.assertEqual(order_line_pro_1.date_planned,schedule_date_1,'Scheduledateofpurchaseorderlineforproduct_1shouldbeequalto:Orderdateofpurchaseorder+DeliveryLeadTimeofproduct_1.')

        #Checkscheduleddateofpurchaseorderlineforproduct_2
        schedule_date_2=datetime.combine(order_date+timedelta(days=self.product_2.seller_ids.delay),time.min).replace(tzinfo=None,hour=12)
        self.assertEqual(order_line_pro_2.date_planned,schedule_date_2,'Scheduledateofpurchaseorderlineforproduct_2shouldbeequalto:Orderdateofpurchaseorder+DeliveryLeadTimeofproduct_2.')

        #Checkscheduleddateofpurchaseorder
        po_schedule_date=min(schedule_date_1,schedule_date_2)
        self.assertEqual(purchase2.order_line[1].date_planned,po_schedule_date,'Scheduledateofpurchaseordershouldbeminimumofscheduledatesofpurchaseorderlines.')

        #Checkthepickingcreatedornot
        self.assertTrue(purchase2.picking_ids,"Pickingshouldbecreated.")

        #CheckscheduleddateofInTypeshipment
        self.assertEqual(purchase2.picking_ids.scheduled_date,po_schedule_date,'ScheduledateofIntypeshipmentshouldbesameasscheduledateofpurchaseorder.')

        #Checkdeadlineofpickings
        self.assertEqual(purchase2.picking_ids.date_deadline,purchase2.date_planned,"Deadlineofpickingsshouldbeequalstothereceiptdateofpurchase")
        purchase_form=Form(purchase2)
        purchase_form.date_planned=purchase2.date_planned+timedelta(days=2)
        purchase_form.save()
        self.assertEqual(purchase2.picking_ids.date_deadline,purchase2.date_planned,"Deadlineofpickingsshouldbepropagate")

    deftest_02_product_route_level_delays(self):
        """Inordertocheckdates,setproduct'sDeliveryLeadTime
            andwarehouseroute'sdelay."""

        company=self.env.ref('base.main_company')
        company.write({'po_lead':1.00})

        #Updatewarehouse_1withIncomingShipments3steps
        self.warehouse_1.write({'reception_steps':'three_steps'})

        #Setdelayonpushrule
        forpush_ruleinself.warehouse_1.reception_route_id.rule_ids:
            push_rule.write({'delay':2})

        rule_delay=sum(self.warehouse_1.reception_route_id.rule_ids.mapped('delay'))

        date_planned=fields.Datetime.to_string(fields.datetime.now()+timedelta(days=10))
        #Createprocurementorderofproduct_1
        self.env['procurement.group'].run([self.env['procurement.group'].Procurement(
            self.product_1,5.000,self.uom_unit,self.warehouse_1.lot_stock_id,'TestschedulerforRFQ','/',self.env.company,
            {
                'warehouse_id':self.warehouse_1,
                'date_planned':date_planned, #10daysaddedtocurrentdateofprocurementtogetfuturescheduledateandorderdateofpurchaseorder.
                'date_deadline':date_planned, #10daysaddedtocurrentdateofprocurementtogetfuturescheduledateandorderdateofpurchaseorder.
                'rule_id':self.warehouse_1.buy_pull_id,
                'group_id':False,
                'route_ids':[],
            }
        )])

        #Confirmpurchaseorder
        purchase=self.env['purchase.order.line'].search([('product_id','=',self.product_1.id)],limit=1).order_id
        purchase.button_confirm()

        #Checkorderdateofpurchaseorder
        order_date=fields.Datetime.from_string(date_planned)-timedelta(days=self.product_1.seller_ids.delay+rule_delay+company.po_lead)
        self.assertEqual(purchase.date_order,order_date,'Orderdateshouldbeequalto:Dateoftheprocurementorder-DeliveryLeadTime(supplierandpullrules).')

        #Checkscheduleddateofpurchaseorder
        schedule_date=order_date+timedelta(days=self.product_1.seller_ids.delay+rule_delay+company.po_lead)
        self.assertEqual(date_planned,str(schedule_date),'Scheduledateshouldbeequalto:OrderdateofPurchaseorder+DeliveryLeadTime(supplierandpullrules).')

        #Checkthepickingcratedornot
        self.assertTrue(purchase.picking_ids,"Pickingshouldbecreated.")

        #CheckscheduleddateofInternalTypeshipment
        incoming_shipment1=self.env['stock.picking'].search([('move_lines.product_id','in',(self.product_1.id,self.product_2.id)),('picking_type_id','=',self.warehouse_1.int_type_id.id),('location_id','=',self.warehouse_1.wh_input_stock_loc_id.id),('location_dest_id','=',self.warehouse_1.wh_qc_stock_loc_id.id)])
        incoming_shipment1_date=order_date+timedelta(days=self.product_1.seller_ids.delay+company.po_lead)
        self.assertEqual(incoming_shipment1.scheduled_date,incoming_shipment1_date,'ScheduledateofInternalTypeshipmentforinputstocklocationshouldbeequalto:scheduledateofpurchaseorder+pushruledelay.')
        self.assertEqual(incoming_shipment1.date_deadline,incoming_shipment1_date)
        old_deadline1=incoming_shipment1.date_deadline

        incoming_shipment2=self.env['stock.picking'].search([('picking_type_id','=',self.warehouse_1.int_type_id.id),('location_id','=',self.warehouse_1.wh_qc_stock_loc_id.id),('location_dest_id','=',self.warehouse_1.lot_stock_id.id)])
        incoming_shipment2_date=schedule_date-timedelta(days=incoming_shipment2.move_lines[0].rule_id.delay)
        self.assertEqual(incoming_shipment2.scheduled_date,incoming_shipment2_date,'ScheduledateofInternalTypeshipmentforqualitycontrolstocklocationshouldbeequalto:scheduledateofInternaltypeshipmentforinputstocklocation+pushruledelay..')
        self.assertEqual(incoming_shipment2.date_deadline,incoming_shipment2_date)
        old_deadline2=incoming_shipment2.date_deadline

        #Modifythedate_plannedofthepurchase->propagatethedeadline
        purchase_form=Form(purchase)
        purchase_form.date_planned=purchase.date_planned+timedelta(days=1)
        purchase_form.save()
        self.assertEqual(incoming_shipment2.date_deadline,old_deadline2+timedelta(days=1),'Deadlineshouldbepropagate')
        self.assertEqual(incoming_shipment1.date_deadline,old_deadline1+timedelta(days=1),'Deadlineshouldbepropagate')

    deftest_merge_po_line(self):
        """Changethatmergingpolineforsameprocurementisdone."""

        #createaproductwithmanufactureroute
        product_1=self.env['product.product'].create({
            'name':'AAA',
            'route_ids':[(4,self.route_buy)],
            'seller_ids':[(0,0,{'name':self.partner_1.id,'delay':5})]
        })

        #createamoveforproduct_1fromstocktooutputandreservetotriggerthe
        #rule
        move_1=self.env['stock.move'].create({
            'name':'move_1',
            'product_id':product_1.id,
            'product_uom':self.ref('uom.product_uom_unit'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'product_uom_qty':10,
            'procure_method':'make_to_order'
        })

        move_1._action_confirm()
        po_line=self.env['purchase.order.line'].search([
            ('product_id','=',product_1.id),
        ])
        self.assertEqual(len(po_line),1,'thepurchaseorderlineisnotcreated')
        self.assertEqual(po_line.product_qty,10,'thepurchaseorderlinehasawrongquantity')

        move_2=self.env['stock.move'].create({
            'name':'move_2',
            'product_id':product_1.id,
            'product_uom':self.ref('uom.product_uom_unit'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_output'),
            'product_uom_qty':5,
            'procure_method':'make_to_order'
        })

        move_2._action_confirm()
        po_line=self.env['purchase.order.line'].search([
            ('product_id','=',product_1.id),
        ])
        self.assertEqual(len(po_line),1,'thepurchaseorderlinesshouldbemerged')
        self.assertEqual(po_line.product_qty,15,'thepurchaseorderlinehasawrongquantity')

    deftest_merge_po_line_3(self):
        """Changemergingpolineifsameprocurementisdonedependingoncustomvalues."""
        company=self.env.ref('base.main_company')
        company.write({'po_lead':0.00})

        #ThesellerhasaspecificproductnameandcodewhichmustbekeptinthePOline
        self.t_shirt.seller_ids.write({
            'product_name':'VendorName',
            'product_code':'VendorCode',
        })
        partner=self.t_shirt.seller_ids[:1].name
        t_shirt=self.t_shirt.with_context(
            lang=partner.lang,
            partner_id=partner.id,
        )

        #Createprocurementorderofproduct_1
        ProcurementGroup=self.env['procurement.group']
        procurement_values={
            'warehouse_id':self.warehouse_1,
            'rule_id':self.warehouse_1.buy_pull_id,
            'date_planned':fields.Datetime.to_string(fields.datetime.now()+timedelta(days=10)),
            'group_id':False,
            'route_ids':[],
        }

        procurement_values['product_description_variants']='Color(Red)'
        order_1_values=procurement_values
        ProcurementGroup.run([self.env['procurement.group'].Procurement(
            self.t_shirt,5,self.uom_unit,self.warehouse_1.lot_stock_id,
            self.t_shirt.name,'/',self.env.company,order_1_values)
        ])
        purchase_order=self.env['purchase.order.line'].search([('product_id','=',self.t_shirt.id)],limit=1).order_id
        order_line_description=purchase_order.order_line.product_id._get_description(purchase_order.picking_type_id)
        self.assertEqual(len(purchase_order.order_line),1,'wrongnumberoforderlineiscreated')
        self.assertEqual(purchase_order.order_line.name,t_shirt.display_name+"\n"+"Color(Red)",'wrongdescriptioninpolines')

        procurement_values['product_description_variants']='Color(Red)'
        order_2_values=procurement_values
        ProcurementGroup.run([self.env['procurement.group'].Procurement(
            self.t_shirt,10,self.uom_unit,self.warehouse_1.lot_stock_id,
            self.t_shirt.name,'/',self.env.company,order_2_values)
        ])
        self.env['procurement.group'].run_scheduler()
        self.assertEqual(len(purchase_order.order_line),1,'linewithsamecustomvalueshouldbemerged')
        self.assertEqual(purchase_order.order_line[0].product_qty,15,'linewithsamecustomvalueshouldbemergedandqtyshouldbeupdate')

        procurement_values['product_description_variants']='Color(Green)'

        order_3_values=procurement_values
        ProcurementGroup.run([self.env['procurement.group'].Procurement(
            self.t_shirt,10,self.uom_unit,self.warehouse_1.lot_stock_id,
            self.t_shirt.name,'/',self.env.company,order_3_values)
        ])
        self.assertEqual(len(purchase_order.order_line),2,'linewithdifferentcustomvalueshouldnotbemerged')
        self.assertEqual(purchase_order.order_line.filtered(lambdax:x.product_qty==15).name,t_shirt.display_name+"\n"+"Color(Red)",'wrongdescriptioninpolines')
        self.assertEqual(purchase_order.order_line.filtered(lambdax:x.product_qty==10).name,t_shirt.display_name+"\n"+"Color(Green)",'wrongdescriptioninpolines')

        purchase_order.button_confirm()
        self.assertEqual(purchase_order.picking_ids[0].move_ids_without_package.filtered(lambdax:x.product_uom_qty==15).description_picking,order_line_description+"\nColor(Red)",'wrongdescriptioninpicking')
        self.assertEqual(purchase_order.picking_ids[0].move_ids_without_package.filtered(lambdax:x.product_uom_qty==10).description_picking,order_line_description+"\nColor(Green)",'wrongdescriptioninpicking')

    deftest_reordering_days_to_purchase(self):
        company=self.env.ref('base.main_company')
        company2=self.env['res.company'].create({
            'name':'SecondCompany',
        })
        company.write({'po_lead':0.00})
        self.patcher=patch('flectra.addons.stock.models.stock_orderpoint.fields.Date',wraps=fields.Date)
        self.mock_date=self.patcher.start()

        vendor=self.env['res.partner'].create({
            'name':'Colruyt'
        })
        vendor2=self.env['res.partner'].create({
            'name':'Delhaize'
        })

        self.env.company.days_to_purchase=2.0

        product=self.env['product.product'].create({
            'name':'Chicory',
            'type':'product',
            'seller_ids':[
                (0,0,{'name':vendor2.id,'delay':15.0,'company_id':company2.id}),
                (0,0,{'name':vendor.id,'delay':1.0,'company_id':company.id})
            ]
        })
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=product
        orderpoint_form.product_min_qty=0.0
        orderpoint=orderpoint_form.save()

        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'].with_company(company2))
        orderpoint_form.product_id=product
        orderpoint_form.product_min_qty=0.0
        orderpoint=orderpoint_form.save()

        warehouse=self.env['stock.warehouse'].search([],limit=1)
        delivery_moves=self.env['stock.move']
        foriinrange(0,6):
            delivery_moves|=self.env['stock.move'].create({
                'name':'Delivery',
                'date':datetime.today()+timedelta(days=i),
                'product_id':product.id,
                'product_uom':product.uom_id.id,
                'product_uom_qty':5.0,
                'location_id':warehouse.lot_stock_id.id,
                'location_dest_id':self.ref('stock.stock_location_customers'),
            })
        delivery_moves._action_confirm()
        self.env['procurement.group'].run_scheduler()
        po_line=self.env['purchase.order.line'].search([('product_id','=',product.id)])
        expected_date_order=fields.Date.today()+timedelta(days=2)
        self.assertEqual(fields.Date.to_date(po_line.order_id.date_order),expected_date_order)
        self.assertEqual(len(po_line),1)
        self.assertEqual(po_line.product_uom_qty,20.0)
        self.assertEqual(len(po_line.order_id),1)
        orderpoint_form=Form(orderpoint)
        orderpoint_form.save()

        self.mock_date.today.return_value=fields.Date.today()+timedelta(days=1)
        orderpoint._compute_qty()
        self.env['procurement.group'].run_scheduler()
        po_line02=self.env['purchase.order.line'].search([('product_id','=',product.id)])
        self.assertEqual(po_line02,po_line,'TheorderpointexecutionshouldnotcreateanewPOL')
        self.assertEqual(fields.Date.to_date(po_line.order_id.date_order),expected_date_order,'TheOrderDeadlineshouldnotchange')
        self.assertEqual(po_line.product_uom_qty,25.0,'TheexistingPOLshouldbeupdatedwiththequantityofthelastexecution')
        self.patcher.stop()

    deftest_supplier_lead_time(self):
        """Basicstockconfigurationandasupplierwithaminimumqtyandaleadtime"""
        self.env['stock.warehouse.orderpoint'].search([]).unlink()
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=self.product_1
        orderpoint_form.product_min_qty=10
        orderpoint_form.product_max_qty=50
        orderpoint=orderpoint_form.save()

        self.env['product.supplierinfo'].search([('product_tmpl_id','=',self.product_1.product_tmpl_id.id)]).unlink()
        self.env['product.supplierinfo'].create({
            'name':self.partner_1.id,
            'min_qty':1,
            'price':1,
            'delay':7,
            'product_tmpl_id':self.product_1.product_tmpl_id.id,
        })

        self.env['procurement.group'].run_scheduler()
        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.partner_1.id)])

        today=fields.Datetime.start_of(fields.Datetime.now(),'day')
        self.assertEqual(purchase_order.date_order,today)
        self.assertEqual(fields.Datetime.start_of(purchase_order.date_planned,'day'),today+timedelta(days=7))
