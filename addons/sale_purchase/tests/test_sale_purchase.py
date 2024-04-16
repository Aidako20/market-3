#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError,AccessError
fromflectra.testsimporttagged
fromflectra.addons.sale_purchase.tests.commonimportTestCommonSalePurchaseNoChart


@tagged('-at_install','post_install')
classTestSalePurchase(TestCommonSalePurchaseNoChart):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #createagenericSaleOrderwith2classicalproductsandapurchaseservice
        SaleOrder=cls.env['sale.order'].with_context(tracking_disable=True)
        cls.sale_order_1=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })
        cls.sol1_service_deliver=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_service_delivery'].name,
            'product_id':cls.company_data['product_service_delivery'].id,
            'product_uom_qty':1,
            'product_uom':cls.company_data['product_service_delivery'].uom_id.id,
            'price_unit':cls.company_data['product_service_delivery'].list_price,
            'order_id':cls.sale_order_1.id,
            'tax_id':False,
        })
        cls.sol1_product_order=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_order_no'].name,
            'product_id':cls.company_data['product_order_no'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_order_no'].uom_id.id,
            'price_unit':cls.company_data['product_order_no'].list_price,
            'order_id':cls.sale_order_1.id,
            'tax_id':False,
        })
        cls.sol1_service_purchase_1=cls.env['sale.order.line'].create({
            'name':cls.service_purchase_1.name,
            'product_id':cls.service_purchase_1.id,
            'product_uom_qty':4,
            'product_uom':cls.service_purchase_1.uom_id.id,
            'price_unit':cls.service_purchase_1.list_price,
            'order_id':cls.sale_order_1.id,
            'tax_id':False,
        })

        cls.sale_order_2=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })
        cls.sol2_product_deliver=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_delivery_no'].name,
            'product_id':cls.company_data['product_delivery_no'].id,
            'product_uom_qty':5,
            'product_uom':cls.company_data['product_delivery_no'].uom_id.id,
            'price_unit':cls.company_data['product_delivery_no'].list_price,
            'order_id':cls.sale_order_2.id,
            'tax_id':False,
        })
        cls.sol2_service_order=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_service_order'].name,
            'product_id':cls.company_data['product_service_order'].id,
            'product_uom_qty':6,
            'product_uom':cls.company_data['product_service_order'].uom_id.id,
            'price_unit':cls.company_data['product_service_order'].list_price,
            'order_id':cls.sale_order_2.id,
            'tax_id':False,
        })
        cls.sol2_service_purchase_2=cls.env['sale.order.line'].create({
            'name':cls.service_purchase_2.name,
            'product_id':cls.service_purchase_2.id,
            'product_uom_qty':7,
            'product_uom':cls.service_purchase_2.uom_id.id,
            'price_unit':cls.service_purchase_2.list_price,
            'order_id':cls.sale_order_2.id,
            'tax_id':False,
        })

    deftest_sale_create_purchase(self):
        """Confirming2salesorderswithaservicethatshouldcreateaPO,thencancellingthePOshouldshedule1nextactivityperSO"""
        self.sale_order_1.action_confirm()
        self.sale_order_2.action_confirm()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.supplierinfo1.name.id),('state','=','draft')])
        purchase_lines_so1=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_1.order_line.ids)])
        purchase_line1=purchase_lines_so1[0]

        purchase_lines_so2=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_2.order_line.ids)])
        purchase_line2=purchase_lines_so2[0]

        self.assertEqual(len(purchase_order),1,"OnlyonePOshouldhavebeencreated,fromthe2Salesorders")
        self.assertEqual(len(purchase_order.order_line),2,"Thepurchaseordershouldhave2lines")
        self.assertEqual(len(purchase_lines_so1),1,"OnlyoneSOlinefromSO1shouldhavecreateaPOline")
        self.assertEqual(len(purchase_lines_so2),1,"OnlyoneSOlinefromSO2shouldhavecreateaPOline")
        self.assertEqual(len(purchase_order.activity_ids),0,"NoactivityshouldbescheduledonthePO")
        self.assertEqual(purchase_order.state,'draft',"ThecreatedPOshouldbeindraftstate")

        self.assertNotEqual(purchase_line1.product_id,purchase_line2.product_id,"The2POlineshouldhavedifferentproducts")
        self.assertEqual(purchase_line1.product_id,self.sol1_service_purchase_1.product_id,"ThecreatePOlinemusthavethesameproductasitsmotherSOline")
        self.assertEqual(purchase_line2.product_id,self.sol2_service_purchase_2.product_id,"ThecreatePOlinemusthavethesameproductasitsmotherSOline")

        purchase_order.button_cancel()

        self.assertEqual(len(self.sale_order_1.activity_ids),1,"OneactivityshouldbescheduledontheSO1sincethePOhasbeencancelled")
        self.assertEqual(self.sale_order_1.user_id,self.sale_order_1.activity_ids[0].user_id,"TheactivityshouldbeassignedtotheSOresponsible")

        self.assertEqual(len(self.sale_order_2.activity_ids),1,"OneactivityshouldbescheduledontheSO2sincethePOhasbeencancelled")
        self.assertEqual(self.sale_order_2.user_id,self.sale_order_2.activity_ids[0].user_id,"TheactivityshouldbeassignedtotheSOresponsible")

    deftest_uom_conversion(self):
        """TestgeneratedPOusetherightUoMaccordingtoproductconfiguration"""
        self.sale_order_2.action_confirm()
        purchase_line=self.env['purchase.order.line'].search([('sale_line_id','=',self.sol2_service_purchase_2.id)]) #onlyoneline

        self.assertTrue(purchase_line,"TheSOlineshouldgenerateaPOline")
        self.assertEqual(purchase_line.product_uom,self.service_purchase_2.uom_po_id,"TheUoMonthepurchaselineshouldbetheonefromtheproductconfiguration")
        self.assertNotEqual(purchase_line.product_uom,self.sol2_service_purchase_2.product_uom,"Astheproductconfiguration,theUoMontheSOlineshouldstillbedifferentfromtheoneonthePOline")
        self.assertEqual(purchase_line.product_qty,self.sol2_service_purchase_2.product_uom_qty*12,"ThequantityfromtheSOshouldbeconvertedwiththUoMfactoronthePOline")

    deftest_no_supplier(self):
        """TestconfirmingSOwithproductwithnosupplierraiseError"""
        #deletethesuppliers
        self.supplierinfo1.unlink()
        #confirmtheSOshouldraiseUserError
        withself.assertRaises(UserError):
            self.sale_order_1.action_confirm()

    deftest_reconfirm_sale_order(self):
        """ConfirmSO,cancelit,thenre-confirmitshouldnotregenerateapurchaseline"""
        self.sale_order_1.action_confirm()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.supplierinfo1.name.id),('state','=','draft')])
        purchase_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_1.order_line.ids)])
        purchase_line=purchase_lines[0]

        self.assertEqual(len(purchase_lines),1,"OnlyonepurchaselineshouldbecreatedonSOconfirmation")
        self.assertEqual(len(purchase_order),1,"OnepurchaseordershouldhavebeencreatedonSOconfirmation")
        self.assertEqual(len(purchase_order.order_line),1,"OnlyonelineonPO,afterSOconfirmation")
        self.assertEqual(purchase_order,purchase_lines.order_id,"Thegeneratedpurchaselineshouldbeinthegeneratedpurchaseorder")
        self.assertEqual(purchase_order.state,'draft',"Generatedpurchaseshouldbeindraftstate")
        self.assertEqual(purchase_line.price_unit,self.supplierinfo1.price,"Purchaselinepriceistheonefromthesupplier")
        self.assertEqual(purchase_line.product_qty,self.sol1_service_purchase_1.product_uom_qty,"QuantityonSOlineisnotthesameonthepurchaseline(sameUoM)")

        self.sale_order_1.action_cancel()

        self.assertEqual(len(purchase_order.activity_ids),1,"OneactivityshouldbescheduledonthePOsinceaSOhasbeencancelled")

        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.supplierinfo1.name.id),('state','=','draft')])
        purchase_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_1.order_line.ids)])
        purchase_line=purchase_lines[0]

        self.assertEqual(len(purchase_lines),1,"AlwaysonepurchaselineevenafterSOcancellation")
        self.assertTrue(purchase_order,"AlwaysonepurchaseorderevenafterSOcancellation")
        self.assertEqual(len(purchase_order.order_line),1,"StillonelineonPO,evenafterSOcancellation")
        self.assertEqual(purchase_order,purchase_lines.order_id,"Thegeneratedpurchaselineshouldstillbeinthegeneratedpurchaseorder")
        self.assertEqual(purchase_order.state,'draft',"Generatedpurchaseshouldstillbeindraftstate")
        self.assertEqual(purchase_line.price_unit,self.supplierinfo1.price,"Purchaselinepriceisstilltheonefromthesupplier")
        self.assertEqual(purchase_line.product_qty,self.sol1_service_purchase_1.product_uom_qty,"QuantityonSOlineshouldstillbethesameonthepurchaseline(sameUoM)")

        self.sale_order_1.action_draft()
        self.sale_order_1.action_confirm()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.supplierinfo1.name.id),('state','=','draft')])
        purchase_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_1.order_line.ids)])
        purchase_line=purchase_lines[0]

        self.assertEqual(len(purchase_lines),1,"StillonlyonepurchaselineshouldbecreatedevenafterSOreconfirmation")
        self.assertEqual(len(purchase_order),1,"StillonepurchaseordershouldbeafterSOreconfirmation")
        self.assertEqual(len(purchase_order.order_line),1,"OnlyonelineonPO,evenafterSOreconfirmation")
        self.assertEqual(purchase_order,purchase_lines.order_id,"Thegeneratedpurchaselineshouldbeinthegeneratedpurchaseorder")
        self.assertEqual(purchase_order.state,'draft',"Generatedpurchaseshouldbeindraftstate")
        self.assertEqual(purchase_line.price_unit,self.supplierinfo1.price,"Purchaselinepriceistheonefromthesupplier")
        self.assertEqual(purchase_line.product_qty,self.sol1_service_purchase_1.product_uom_qty,"QuantityonSOlineisnotthesameonthepurchaseline(sameUoM)")

    deftest_update_ordered_sale_quantity(self):
        """Testthepurchaseorderbehoviorwhenchangingtheorderedquantityonthesaleorderline.
            IncreaseofqtyontheSO
            -IfPOisdraft['draft','sent','toapprove']:increasethequantityonthePO
            -IfPOisconfirmed['purchase','done','cancel']:createanewPO

            DecreaseofqtyontheSO
            -IfPOisdraft ['draft','sent','toapprove']:nextactivityonthePO
            -IfPOisconfirmed['purchase','done','cancel']:nextactivityonthePO
        """
        self.sale_order_1.action_confirm()

        purchase_order=self.env['purchase.order'].search([('partner_id','=',self.supplierinfo1.name.id),('state','=','draft')])
        purchase_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_1.order_line.ids)])
        purchase_line=purchase_lines[0]

        self.assertEqual(purchase_order.state,'draft',"Thecreatedpurchaseshouldbeindraftstate")
        self.assertFalse(purchase_order.activity_ids,"ThereisnoactivitiesonthePO")
        self.assertEqual(purchase_line.product_qty,self.sol1_service_purchase_1.product_uom_qty,"QuantityonSOlineisnotthesameonthepurchaseline(sameUoM)")

        #increasetheorderedquantityonsaleline
        self.sol1_service_purchase_1.write({'product_uom_qty':self.sol1_service_purchase_1.product_uom_qty+12}) #product_uom_qty=16
        self.assertEqual(purchase_line.product_qty,self.sol1_service_purchase_1.product_uom_qty,"ThequantityofdraftPOlineshouldbeincreasedastheonefromthesalelinechanged")

        sale_line_old_quantity=self.sol1_service_purchase_1.product_uom_qty

        #decreasetheorderedquantityonsaleline
        self.sol1_service_purchase_1.write({'product_uom_qty':self.sol1_service_purchase_1.product_uom_qty-3}) #product_uom_qty=13
        self.assertEqual(len(purchase_order.activity_ids),1,"OneactivityshouldhavebeencreatedonthePO")
        self.assertEqual(purchase_order.activity_ids.user_id,purchase_order.user_id,"ActivityassignedtoPOresponsible")
        self.assertEqual(purchase_order.activity_ids.state,'today',"Activityisfortoday,asitisurgent")

        #confirmthePO
        purchase_order.button_confirm()

        #decreasetheorderedquantityonsaleline
        self.sol1_service_purchase_1.write({'product_uom_qty':self.sol1_service_purchase_1.product_uom_qty-5}) #product_uom_qty=8

        purchase_order.invalidate_cache() #Note:creatingasecondactivitywillnotrefreshthecache

        self.assertEqual(purchase_line.product_qty,sale_line_old_quantity,"ThequantityonthePOlineshouldnothavechanged.")
        self.assertEqual(len(purchase_order.activity_ids),2,"asecondactivityshouldhavebeencreatedonthePO")
        self.assertEqual(purchase_order.activity_ids.mapped('user_id'),purchase_order.user_id,"ActivitiesassignedtoPOresponsible")
        self.assertEqual(purchase_order.activity_ids.mapped('state'),['today','today'],"Activitiesarefortoday,asitisurgent")

        #increasetheorderedquantityonsaleline
        delta=8
        self.sol1_service_purchase_1.write({'product_uom_qty':self.sol1_service_purchase_1.product_uom_qty+delta}) #product_uom_qty=16

        self.assertEqual(purchase_line.product_qty,sale_line_old_quantity,"ThequantityonthePOlineshouldnothavechanged.")
        self.assertEqual(len(purchase_order.activity_ids),2,"Always2activityonconfirmedthePO")

        purchase_order2=self.env['purchase.order'].search([('partner_id','=',self.supplierinfo1.name.id),('state','=','draft')])
        purchase_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.sale_order_1.order_line.ids)])
        purchase_lines2=purchase_lines.filtered(lambdapol:pol.order_id==purchase_order2)
        purchase_line2=purchase_lines2[0]

        self.assertTrue(purchase_order2,"AsecondPOiscreatedbyincreasingsalequantitywhenfirstPOisconfirmed")
        self.assertEqual(purchase_order2.state,'draft',"ThesecondPOisindraftstate")
        self.assertNotEqual(purchase_order,purchase_order2,"The2POaredifferent")
        self.assertEqual(len(purchase_lines),2,"ThesameSaleLinehascreated2purchaselines")
        self.assertEqual(len(purchase_order2.order_line),1,"The2ndPOhasonlyoneline")
        self.assertEqual(purchase_line2.sale_line_id,self.sol1_service_purchase_1,"The2ndPOlinecamefromtheSOlinesol1_service_purchase_1")
        self.assertEqual(purchase_line2.product_qty,delta,"ThequantityofthenewPOlineisthequantityaddedontheSaleLine,afterfirstPOconfirmation")

    deftest_pol_description(self):
        service=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'service',
            'service_to_purchase':True,
            'seller_ids':[(0,0,{
                'name':self.partner_vendor_service.id,
                'min_qty':1,
                'price':10,
                'product_code':'C01',
                'product_name':'Name01',
                'sequence':1,
            })]
        })

        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':service.name,
                    'product_id':service.id,
                    'product_uom_qty':1,
                })
            ],
        })
        so.action_confirm()

        po=self.env['purchase.order'].search([('partner_id','=',self.partner_vendor_service.id)],order='iddesc',limit=1)
        self.assertEqual(po.order_line.name,"[C01]Name01")
