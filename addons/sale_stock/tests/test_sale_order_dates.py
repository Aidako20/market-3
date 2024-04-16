#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromdatetimeimporttimedelta
fromflectraimportfields
fromflectra.testsimportcommon,tagged


@tagged('post_install','-at_install')
classTestSaleExpectedDate(ValuationReconciliationTestCommon):

    deftest_sale_order_expected_date(self):
        """TestexpecteddateandeffectivedateofSalesOrders"""
        Product=self.env['product.product']

        product_A=Product.create({
            'name':'ProductA',
            'type':'product',
            'sale_delay':5,
            'uom_id':1,
        })
        product_B=Product.create({
            'name':'ProductB',
            'type':'product',
            'sale_delay':10,
            'uom_id':1,
        })
        product_C=Product.create({
            'name':'ProductC',
            'type':'product',
            'sale_delay':15,
            'uom_id':1,
        })

        self.env['stock.quant']._update_available_quantity(product_A,self.company_data['default_warehouse'].lot_stock_id,10)
        self.env['stock.quant']._update_available_quantity(product_B,self.company_data['default_warehouse'].lot_stock_id,10)
        self.env['stock.quant']._update_available_quantity(product_C,self.company_data['default_warehouse'].lot_stock_id,10)

        sale_order=self.env['sale.order'].create({
            'partner_id':self.env['res.partner'].create({'name':'ACustomer'}).id,
            'picking_policy':'direct',
            'order_line':[
                (0,0,{'name':product_A.name,'product_id':product_A.id,'customer_lead':product_A.sale_delay,'product_uom_qty':5}),
                (0,0,{'name':product_B.name,'product_id':product_B.id,'customer_lead':product_B.sale_delay,'product_uom_qty':5}),
                (0,0,{'name':product_C.name,'product_id':product_C.id,'customer_lead':product_C.sale_delay,'product_uom_qty':5})
            ],
        })

        #ifShippingPolicyissetto`direct`(whenSOisindraftstate)thenexpecteddateshouldbe
        #currentdate+shortestleadtimefromallofit'sorderlines
        expected_date=fields.Datetime.now()+timedelta(days=5)
        self.assertAlmostEqual(expected_date,sale_order.expected_date,
            msg="Wrongexpecteddateonsaleorder!",delta=timedelta(seconds=1))

        #ifShippingPolicyissetto`one`(whenSOisindraftstate)thenexpecteddateshouldbe
        #currentdate+longestleadtimefromallofit'sorderlines
        sale_order.write({'picking_policy':'one'})
        expected_date=fields.Datetime.now()+timedelta(days=15)
        self.assertAlmostEqual(expected_date,sale_order.expected_date,
            msg="Wrongexpecteddateonsaleorder!",delta=timedelta(seconds=1))

        sale_order.action_confirm()

        #SettingconfirmationdateofSOto5daysfromtodaysothattheexpected/effectivedatecouldbechecked
        #againstrealconfirmationdate
        confirm_date=fields.Datetime.now()+timedelta(days=5)
        sale_order.write({'date_order':confirm_date})

        #ifShippingPolicyissetto`one`(whenSOisconfirmed)thenexpecteddateshouldbe
        #SOconfirmationdate+longestleadtimefromallofit'sorderlines
        expected_date=confirm_date+timedelta(days=15)
        self.assertAlmostEqual(expected_date,sale_order.expected_date,
            msg="Wrongexpecteddateonsaleorder!",delta=timedelta(seconds=1))

        #ifShippingPolicyissetto`direct`(whenSOisconfirmed)thenexpecteddateshouldbe
        #SOconfirmationdate+shortestleadtimefromallofit'sorderlines
        sale_order.write({'picking_policy':'direct'})
        expected_date=confirm_date+timedelta(days=5)
        self.assertAlmostEqual(expected_date,sale_order.expected_date,
            msg="Wrongexpecteddateonsaleorder!",delta=timedelta(seconds=1))

        #Checkeffectivedate,itshouldbedateonwhichthefirstshipmentsuccessfullydeliveredtocustomer
        picking=sale_order.picking_ids[0]
        formlinpicking.move_line_ids:
            ml.qty_done=ml.product_uom_qty
        picking._action_done()
        self.assertEqual(picking.state,'done',"Pickingnotprocessedcorrectly!")
        self.assertEqual(fields.Date.context_today(sale_order),sale_order.effective_date,"Wrongeffectivedateonsaleorder!")

    deftest_sale_order_commitment_date(self):

        #InordertotesttheCommitmentDatefeatureinSalesOrdersinFlectra,
        #IcopyademoSalesOrderwithcommittedDateon2010-07-12
        new_order=self.env['sale.order'].create({
            'partner_id':self.env['res.partner'].create({'name':'APartner'}).id,
            'order_line':[(0,0,{
                'name':"Aproduct",
                'product_id':self.env['product.product'].create({
                    'name':'Aproduct',
                    'type':'product',
                }).id,
                'product_uom_qty':1,
                'price_unit':750,
            })],
            'commitment_date':'2010-07-12',
        })
        #IconfirmtheSalesOrder.
        new_order.action_confirm()
        #IverifythattheProcurementsandStockMoveshavebeengeneratedwiththecorrectdate
        security_delay=timedelta(days=new_order.company_id.security_lead)
        commitment_date=fields.Datetime.from_string(new_order.commitment_date)
        right_date=commitment_date-security_delay
        forlineinnew_order.order_line:
            self.assertEqual(line.move_ids[0].date,right_date,"TheexpecteddatefortheStockMoveiswrong")
