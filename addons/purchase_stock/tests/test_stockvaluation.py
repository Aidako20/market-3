#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime
fromdatetimeimportdatetime
fromunittest.mockimportpatch

fromflectraimportfields
fromflectra.testsimportForm
fromflectra.tests.commonimportTransactionCase,tagged
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT


classTestStockValuation(TransactionCase):
    defsetUp(self):
        super(TestStockValuation,self).setUp()
        self.supplier_location=self.env.ref('stock.stock_location_suppliers')
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.partner_id=self.env['res.partner'].create({
            'name':'WoodCornerPartner',
            'company_id':self.env.user.company_id.id,
        })
        self.product1=self.env['product.product'].create({
            'name':'LargeDesk',
            'standard_price':1299.0,
            'list_price':1799.0,
            #Ignoretaxcalculationsforthesetests.
            'supplier_taxes_id':False,
            'type':'product',
        })
        Account=self.env['account.account']
        self.stock_input_account=Account.create({
            'name':'StockInput',
            'code':'StockIn',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
            'reconcile':True,
        })
        self.stock_output_account=Account.create({
            'name':'StockOutput',
            'code':'StockOut',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
            'reconcile':True,
        })
        self.stock_valuation_account=Account.create({
            'name':'StockValuation',
            'code':'StockValuation',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
        })
        self.stock_journal=self.env['account.journal'].create({
            'name':'StockJournal',
            'code':'STJTEST',
            'type':'general',
        })
        self.product1.categ_id.write({
            'property_stock_account_input_categ_id':self.stock_input_account.id,
            'property_stock_account_output_categ_id':self.stock_output_account.id,
            'property_stock_valuation_account_id':self.stock_valuation_account.id,
            'property_stock_journal':self.stock_journal.id,
        })

    deftest_change_unit_cost_average_1(self):
        """Confirmapurchaseorderandcreatetheassociatedreceipt,changetheunitcostofthe
        purchaseorderbeforevalidatingthereceipt,thevalueofthereceivedgoodsshouldbeset
        accordingtothelastunitcost.
        """
        self.product1.product_tmpl_id.categ_id.property_cost_method='average'
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()

        picking1=po1.picking_ids[0]
        move1=picking1.move_lines[0]

        #theunitpriceofthepurchaseorderlineiscopiedtotheinmove
        self.assertEqual(move1.price_unit,100)

        #updatetheunitpriceonthepurchaseorderline
        po1.order_line.price_unit=200

        #theunitpriceonthestockmoveisupdated
        self.assertEqual(move1.price_unit,200)

        #validatethereceipt
        res_dict=picking1.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process()

        #theunitpriceofthevaluationlayerusedthelatestvalue
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,200)

        self.assertEqual(self.product1.value_svl,2000)

    deftest_standard_price_change_1(self):
        """Confirmapurchaseorderandcreatetheassociatedreceipt,changetheunitcostofthe
        purchaseorderandthestandardpriceoftheproductbeforevalidatingthereceipt,the
        valueofthereceivedgoodsshouldbesetaccordingtothelaststandardprice.
        """
        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'

        #setastandardprice
        self.product1.product_tmpl_id.standard_price=10

        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':11.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()

        picking1=po1.picking_ids[0]
        move1=picking1.move_lines[0]

        #themove'sunitpricereflectsthepurchaseorderline'scostevenifit'suselesswhen
        #theproduct'scostmethodisstandard
        self.assertEqual(move1.price_unit,11)

        #setanewstandardprice
        self.product1.product_tmpl_id.standard_price=12

        #theunitpriceonthestockmoveisnotdirectlyupdated
        self.assertEqual(move1.price_unit,11)

        #validatethereceipt
        res_dict=picking1.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process()

        #theunitpriceofthevaluationlayerusedthelatestvalue
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,12)

        self.assertEqual(self.product1.value_svl,120)

    deftest_change_currency_rate_average_1(self):
        """Confirmapurchaseorderinanothercurrencyandcreatetheassociatedreceipt,change
        thecurrencyrate,validatethereceiptandthencheckthatthevalueofthereceivedgoods
        issetaccordingtothelastcurrencyrate.
        """
        self.env['res.currency.rate'].search([]).unlink()
        usd_currency=self.env.ref('base.USD')
        self.env.company.currency_id=usd_currency.id

        eur_currency=self.env.ref('base.EUR')

        self.product1.product_tmpl_id.categ_id.property_cost_method='average'

        #defaultcurrencyisUSD,createapurchaseorderinEUR
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'currency_id':eur_currency.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()

        picking1=po1.picking_ids[0]
        move1=picking1.move_lines[0]

        #convertthepriceunitinthecompanycurrency
        price_unit_usd=po1.currency_id._convert(
            po1.order_line.price_unit,po1.company_id.currency_id,
            self.env.company,fields.Date.today(),round=False)

        #theunitpriceofthemoveistheunitpriceofthepurchaseorderlineconvertedin
        #thecompany'scurrency
        self.assertAlmostEqual(move1.price_unit,price_unit_usd,places=2)

        #changetherateofthecurrency
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y-%m-%d'),
            'rate':2.0,
            'currency_id':eur_currency.id,
            'company_id':po1.company_id.id,
        })
        eur_currency._compute_current_rate()
        price_unit_usd_new_rate=po1.currency_id._convert(
            po1.order_line.price_unit,po1.company_id.currency_id,
            self.env.company,fields.Date.today(),round=False)

        #thenewprice_unitislowerthanthinitialbecauseoftherate'schange
        self.assertLess(price_unit_usd_new_rate,price_unit_usd)

        #theunitpriceonthestockmoveisnotdirectlyupdated
        self.assertAlmostEqual(move1.price_unit,price_unit_usd,places=2)

        #validatethereceipt
        res_dict=picking1.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process()

        #theunitpriceofthevaluationlayerusedthelatestvalue
        self.assertAlmostEqual(move1.stock_valuation_layer_ids.unit_cost,price_unit_usd_new_rate)

        self.assertAlmostEqual(self.product1.value_svl,price_unit_usd_new_rate*10,delta=0.1)

    deftest_extra_move_fifo_1(self):
        """Checkthattheextramovewhenoverprocessingareceiptiscorrectlymergedbackin
        theoriginalmove.
        """
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()

        picking1=po1.picking_ids[0]
        move1=picking1.move_lines[0]
        move1.quantity_done=15
        picking1.button_validate()

        #thereshouldbeonlyonemove
        self.assertEqual(len(picking1.move_lines),1)
        self.assertEqual(move1.price_unit,100)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,100)
        self.assertEqual(move1.product_qty,15)
        self.assertEqual(self.product1.value_svl,1500)

    deftest_backorder_fifo_1(self):
        """Checkthatthebackorderedmovewhenunderprocessingareceiptcorrectlykeepthe
        priceunitoftheoriginalmove.
        """
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()

        picking1=po1.picking_ids[0]
        move1=picking1.move_lines[0]
        move1.quantity_done=5
        res_dict=picking1.button_validate()
        self.assertEqual(res_dict['res_model'],'stock.backorder.confirmation')
        wizard=self.env[(res_dict.get('res_model'))].browse(res_dict.get('res_id')).with_context(res_dict['context'])
        wizard.process()

        self.assertEqual(len(picking1.move_lines),1)
        self.assertEqual(move1.price_unit,100)
        self.assertEqual(move1.product_qty,5)

        picking2=po1.picking_ids.filtered(lambdap:p.backorder_id)
        move2=picking2.move_lines[0]
        self.assertEqual(len(picking2.move_lines),1)
        self.assertEqual(move2.price_unit,100)
        self.assertEqual(move2.product_qty,5)


@tagged('post_install','-at_install')
classTestStockValuationWithCOA(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.supplier_location=cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location=cls.env.ref('stock.stock_location_stock')
        cls.partner_id=cls.env['res.partner'].create({'name':'WoodCornerPartner'})
        cls.product1=cls.env['product.product'].create({'name':'LargeDesk'})

        cls.cat=cls.env['product.category'].create({
            'name':'cat',
        })
        cls.product1=cls.env['product.product'].create({
            'name':'product1',
            'type':'product',
            'categ_id':cls.cat.id,
        })
        cls.product1_copy=cls.env['product.product'].create({
            'name':'product1',
            'type':'product',
            'categ_id':cls.cat.id,
        })

        Account=cls.env['account.account']
        cls.usd_currency=cls.env.ref('base.USD')
        cls.eur_currency=cls.env.ref('base.EUR')

        cls.stock_input_account=Account.create({
            'name':'StockInput',
            'code':'StockIn',
            'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
            'reconcile':True,
        })
        cls.stock_output_account=Account.create({
            'name':'StockOutput',
            'code':'StockOut',
            'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
            'reconcile':True,
        })
        cls.stock_valuation_account=Account.create({
            'name':'StockValuation',
            'code':'StockValuation',
            'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
        })
        cls.price_diff_account=Account.create({
            'name':'pricediffaccount',
            'code':'pricediffaccount',
            'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
        })
        cls.stock_journal=cls.env['account.journal'].create({
            'name':'StockJournal',
            'code':'STJTEST',
            'type':'general',
        })
        cls.product1.categ_id.write({
            'property_valuation':'real_time',
            'property_stock_account_input_categ_id':cls.stock_input_account.id,
            'property_stock_account_output_categ_id':cls.stock_output_account.id,
            'property_stock_valuation_account_id':cls.stock_valuation_account.id,
            'property_stock_journal':cls.stock_journal.id,
        })

    deftest_fifo_anglosaxon_return(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #Receive10@10;createthevendorbill
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':10.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()
        receipt_po1=po1.picking_ids[0]
        receipt_po1.move_lines.quantity_done=10
        receipt_po1.button_validate()

        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=self.partner_id
        move_form.purchase_id=po1
        invoice_po1=move_form.save()
        invoice_po1.action_post()

        #Receive10@20;createthevendorbill
        po2=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':20.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po2.button_confirm()
        receipt_po2=po2.picking_ids[0]
        receipt_po2.move_lines.quantity_done=10
        receipt_po2.button_validate()

        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=self.partner_id
        move_form.purchase_id=po2
        invoice_po2=move_form.save()
        invoice_po2.action_post()

        #valuationofproduct1shouldbe300
        self.assertEqual(self.product1.value_svl,300)

        #returnthesecondpo
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=receipt_po2.ids,active_id=receipt_po2.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=10
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done=10
        return_pick.button_validate()

        #valuationofproduct1shouldbe200asthefirstitemswillbesentout
        self.assertEqual(self.product1.value_svl,200)

        #createacreditnoteforpo2
        move_form=Form(self.env['account.move'].with_context(default_move_type='in_refund'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=self.partner_id
        move_form.purchase_id=po2
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.quantity=10
        creditnote_po2=move_form.save()
        creditnote_po2.action_post()

        #checktheanglosaxonentries
        price_diff_entry=self.env['account.move.line'].search([('account_id','=',self.price_diff_account.id)])
        self.assertEqual(price_diff_entry.credit,100)

    deftest_anglosaxon_valuation(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #CreatePO
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_id
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=self.product1
            po_line.product_qty=1
            po_line.price_unit=10.0
        order=po_form.save()
        order.button_confirm()

        #Receivethegoods
        receipt=order.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #Createaninvoicewithadifferentprice
        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=order.partner_id
        move_form.purchase_id=order
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.price_unit=15.0
        invoice=move_form.save()
        invoice.action_post()

        #Checkwhatwaspostedinthepricedifferenceaccount
        price_diff_aml=self.env['account.move.line'].search([('account_id','=',self.price_diff_account.id)])
        self.assertEqual(len(price_diff_aml),1,"Onlyonelineshouldhavebeengeneratedinthepricedifferenceaccount.")
        self.assertAlmostEqual(price_diff_aml.debit,5,msg="Pricedifferenceshouldbeequalto5(15-10)")

        #Checkwhatwaspostedinstockinputaccount
        input_aml=self.env['account.move.line'].search([('account_id','=',self.stock_input_account.id)])
        self.assertEqual(len(input_aml),3,"Onlythreelinesshouldhavebeengeneratedinstockinputaccount:onewhenreceivingtheproduct,onewhenmakingtheinvoice.")
        invoice_amls=input_aml.filtered(lambdal:l.move_id==invoice)
        picking_aml=input_aml-invoice_amls
        self.assertAlmostEqual(sum(invoice_amls.mapped('debit')),15,msg="TotaldebitvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(sum(invoice_amls.mapped('credit')),5,msg="TotaldebitvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(sum(picking_aml.mapped('credit')),10,msg="TotalcreditvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")

    deftest_valuation_from_increasing_tax(self):
        """Checkthatataxwithoutaccountwillincrementthestockvalue.
        """

        tax_with_no_account=self.env['account.tax'].create({
            'name':"Taxwithnoaccount",
            'amount_type':'fixed',
            'amount':5,
            'sequence':8,
        })

        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'

        #Receive10@10;createthevendorbill
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'taxes_id':[(4,tax_with_no_account.id)],
                    'product_qty':10.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':10.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()
        receipt_po1=po1.picking_ids[0]
        receipt_po1.move_lines.quantity_done=10
        receipt_po1.button_validate()

        #valuationofproduct1shouldbe15asthetaxwithnoaccountset
        #hasgonetothestockaccount,andmustbereflectedininventoryvaluation
        self.assertEqual(self.product1.value_svl,150)

    deftest_standard_valuation_multicurrency(self):
        company=self.env.user.company_id
        company.anglo_saxon_accounting=True
        company.currency_id=self.usd_currency

        date_po='2019-01-01'

        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account
        self.product1.standard_price=10

        #SetUpcurrencyandrates  1$=2Euros
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",(self.usd_currency.id,company.id))
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.0,
            'currency_id':self.usd_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':2,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        #CreatePO
        po=self.env['purchase.order'].create({
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':1.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,#50$
                    'date_planned':date_po,
                }),
            ],
        })
        po.button_confirm()

        #Receivethegoods
        receipt=po.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #Createavendorbill
        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_po,
            'date':date_po,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[(0,0,{
                'name':'Test',
                'price_unit':100.0,
                'product_id':self.product1.id,
                'purchase_line_id':po.order_line.id,
                'quantity':1.0,
                'account_id':self.stock_input_account.id,
            })]
        })

        inv.action_post()

        #Checkwhatwaspostedinstockinputaccount
        input_amls=self.env['account.move.line'].search([('account_id','=',self.stock_input_account.id)])
        self.assertEqual(len(input_amls),3,"Onlythreelinesshouldhavebeengeneratedinstockinputaccount:onewhenreceivingtheproduct,onewhenmakingtheinvoice.")
        invoice_amls=input_amls.filtered(lambdal:l.move_id==inv)
        picking_aml=input_amls-invoice_amls
        payable_aml=invoice_amls.filtered(lambdal:l.amount_currency>0)
        diff_aml=invoice_amls-payable_aml

        #checkUSD
        self.assertAlmostEqual(payable_aml.debit,50,msg="TotaldebitvalueshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(picking_aml.credit,10,msg="creditvalueforstockshouldbeequaltothestandardpriceoftheproduct.")
        self.assertAlmostEqual(diff_aml.credit,40,msg="creditvalueforpricedifference")

        #checkEUR
        self.assertAlmostEqual(payable_aml.amount_currency,100,msg="TotaldebitvalueshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(picking_aml.amount_currency,-20,msg="creditvalueforstockshouldbeequaltothestandardpriceoftheproduct.")
        self.assertAlmostEqual(diff_aml.amount_currency,-80,msg="creditvalueforpricedifference")

    deftest_valuation_multicurecny_with_tax(self):
        """Checkthatataxwithoutaccountwillincrementthestockvalue.
        """

        company=self.env.user.company_id
        company.anglo_saxon_accounting=True
        company.currency_id=self.usd_currency

        date_po='2019-01-01'

        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #SetUpcurrencyandrates1$=2Euros
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",(self.usd_currency.id,company.id))
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.0,
            'currency_id':self.usd_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':2,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        tax_with_no_account=self.env['account.tax'].create({
            'name':"Taxwithnoaccount",
            'amount_type':'fixed',
            'amount':5,
            'sequence':8,
            'price_include':True,
        })

        #CreatePO
        po=self.env['purchase.order'].create({
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':1.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,#50$
                    'taxes_id':[(4,tax_with_no_account.id)],
                    'date_planned':date_po,
                }),
            ],
        })

        po.button_confirm()

        #Receivethegoods
        receipt=po.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #Createavendorbill
        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_po,
            'date':date_po,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[(0,0,{
                'name':'Test',
                'price_unit':100.0,
                'product_id':self.product1.id,
                'purchase_line_id':po.order_line.id,
                'quantity':1.0,
                'account_id':self.stock_input_account.id,
            })]
        })

        inv.action_post()

        #Checkwhatwaspostedinstockinputaccount
        input_amls=self.env['account.move.line'].search([('account_id','=',self.stock_input_account.id)])
        self.assertEqual(len(input_amls),2,"Onlytwolinesshouldhavebeengeneratedinstockinputaccount:onewhenreceivingtheproduct,onewhenmakingtheinvoice.")
        invoice_aml=input_amls.filtered(lambdal:l.move_id==inv)
        picking_aml=input_amls-invoice_aml

        #checkEUR
        self.assertAlmostEqual(invoice_aml.amount_currency,100,msg="TotaldebitvalueshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(picking_aml.amount_currency,-95,msg="creditvalueforstockshouldbeequaltotheuntaxedpriceoftheproduct.")

    deftest_average_realtime_anglo_saxon_valuation_multicurrency_same_date(self):
        """
        ThePOandinvoiceareinthesameforeigncurrency.
        ThePOisinvoicedonthesamedateasitscreation.
        Thisshouldn'tcreateapricedifferenceentry.
        """
        company=self.env.user.company_id
        company.anglo_saxon_accounting=True
        company.currency_id=self.usd_currency

        date_po='2019-01-01'

        #SetUpproduct
        self.product1.product_tmpl_id.cost_method='average'
        self.product1.product_tmpl_id.valuation='real_time'
        self.product1.product_tmpl_id.purchase_method='purchase'

        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #SetUpcurrencyandrates
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",(self.usd_currency.id,company.id))
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.0,
            'currency_id':self.usd_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.5,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        #Proceed
        po=self.env['purchase.order'].create({
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':1.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,
                    'date_planned':date_po,
                }),
            ],
        })
        po.button_confirm()

        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_po,
            'date':date_po,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[(0,0,{
                'name':'Test',
                'price_unit':100.0,
                'product_id':self.product1.id,
                'purchase_line_id':po.order_line.id,
                'quantity':1.0,
                'account_id':self.stock_input_account.id,
            })]
        })

        inv.action_post()

        move_lines=inv.line_ids
        self.assertEqual(len(move_lines),4)

        payable_line=move_lines.filtered(lambdal:l.account_id.internal_type=='payable')

        self.assertEqual(payable_line.amount_currency,-100.0)
        self.assertAlmostEqual(payable_line.balance,-66.67)

        stock_line=move_lines.filtered(lambdal:l.account_id==self.stock_input_accountandl.balance>0)
        self.assertEqual(stock_line.amount_currency,100.0)
        self.assertAlmostEqual(stock_line.balance,66.67)

    deftest_realtime_anglo_saxon_valuation_multicurrency_different_dates(self):
        """
        ThePOandinvoiceareinthesameforeigncurrency.
        ThePOisinvoicedatalaterdatethanitscreation.
        Thisshouldcreateapricedifferenceentryforstandardcostmethod
        Notforaveragecostmethodthough,sincethePOandinvoicehavethesamecurrency
        """
        company=self.env.user.company_id
        company.anglo_saxon_accounting=True
        company.currency_id=self.usd_currency
        self.product1.product_tmpl_id.categ_id.property_cost_method='average'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'

        date_po='2019-01-01'
        date_invoice='2019-01-16'

        #SetUpproductAverage
        self.product1.product_tmpl_id.write({
            'purchase_method':'purchase',
            'property_account_creditor_price_difference':self.price_diff_account.id,
        })

        #SetUpproductStandard
        #shouldhaveboughtat60USD
        #actuallyinvoicedat70EUR>35USD
        product_categ_standard=self.cat.copy({
            'property_cost_method':'standard',
            'property_stock_account_input_categ_id':self.stock_input_account.id,
            'property_stock_account_output_categ_id':self.stock_output_account.id,
            'property_stock_valuation_account_id':self.stock_valuation_account.id,
            'property_stock_journal':self.stock_journal.id,
        })
        product_standard=self.product1_copy
        product_standard.write({
            'categ_id':product_categ_standard.id,
            'name':'StandardVal',
            'standard_price':60,
            'property_account_creditor_price_difference':self.price_diff_account.id
        })

        #SetUpcurrencyandrates
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",(self.usd_currency.id,company.id))
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.0,
            'currency_id':self.usd_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.5,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_invoice,
            'rate':2,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        #ToallowtestingvalidationofPO
        def_today(*args,**kwargs):
            returndate_po
        patchers=[
            patch('flectra.fields.Date.context_today',_today),
        ]

        forpinpatchers:
            p.start()

        #Proceed
        po=self.env['purchase.order'].create({
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':self.product1.name,
                    'product_id':self.product1.id,
                    'product_qty':1.0,
                    'product_uom':self.product1.uom_po_id.id,
                    'price_unit':100.0,
                    'date_planned':date_po,
                }),
                (0,0,{
                    'name':product_standard.name,
                    'product_id':product_standard.id,
                    'product_qty':1.0,
                    'product_uom':product_standard.uom_po_id.id,
                    'price_unit':40.0,
                    'date_planned':date_po,
                }),
            ],
        })
        po.button_confirm()

        line_product_average=po.order_line.filtered(lambdal:l.product_id==self.product1)
        line_product_standard=po.order_line.filtered(lambdal:l.product_id==product_standard)

        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_invoice,
            'date':date_invoice,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[
                (0,0,{
                    'name':self.product1.name,
                    'price_subtotal':100.0,
                    'price_unit':100.0,
                    'product_id':self.product1.id,
                    'purchase_line_id':line_product_average.id,
                    'quantity':1.0,
                    'account_id':self.stock_input_account.id,
                }),
                (0,0,{
                    'name':product_standard.name,
                    'price_subtotal':70.0,
                    'price_unit':70.0,
                    'product_id':product_standard.id,
                    'purchase_line_id':line_product_standard.id,
                    'quantity':1.0,
                    'account_id':self.stock_input_account.id,
                })
            ]
        })

        inv.action_post()

        forpinpatchers:
            p.stop()

        move_lines=inv.line_ids
        self.assertEqual(len(move_lines),5)

        #Ensurenoexchangedifferencemovehasbeencreated
        self.assertTrue(all([notl.reconciledforlinmove_lines]))

        #PAYABLECHECK
        payable_line=move_lines.filtered(lambdal:l.account_id.internal_type=='payable')
        self.assertEqual(payable_line.amount_currency,-170.0)
        self.assertAlmostEqual(payable_line.balance,-85.00)

        #PRODUCTSCHECKS

        #NOEXCHANGEDIFFERENCE(average)
        #Weorderedforavalueof100EUR
        #Butbythetimeweareinvoicedforit
        #theforeigncurrencyappreciatedfrom1.5to2.0
        #Westillhavetopay100EUR,whichnowvaluesat50USD
        product_lines=move_lines.filtered(lambdal:l.product_id==self.product1)

        #Stock-wise,wehavebeeninvoiced100EUR,andweordered100EUR
        #thereisnopricedifference
        #However,100EURshouldbeconvertedatthetimeoftheinvoice
        stock_lines=product_lines.filtered(lambdal:l.account_id==self.stock_input_account)
        self.assertAlmostEqual(sum(stock_lines.mapped('amount_currency')),100.00)
        self.assertAlmostEqual(sum(stock_lines.mapped('balance')),50.00)

        #PRICEDIFFERENCE(STANDARD)
        #Weorderedaproductthatshouldhavecost60USD(120EUR)
        #However,weeffectivelygotinvoiced70EUR(35USD)
        product_lines=move_lines.filtered(lambdal:l.product_id==product_standard)

        stock_lines=product_lines.filtered(lambdal:l.account_id==self.stock_input_account)
        self.assertAlmostEqual(sum(stock_lines.mapped('amount_currency')),120.00)
        self.assertAlmostEqual(sum(stock_lines.mapped('balance')),60.00)

        price_diff_line=product_lines.filtered(lambdal:l.account_id==self.price_diff_account)
        self.assertEqual(price_diff_line.amount_currency,-50.00)
        self.assertAlmostEqual(price_diff_line.balance,-25.00)

    deftest_average_realtime_with_delivery_anglo_saxon_valuation_multicurrency_different_dates(self):
        """
        ThePOandinvoiceareinthesameforeigncurrency.
        ThedeliveryoccursinbetweenPOvalidationandinvoicing
        Theinvoiceiscreatedatanevendifferentdate
        Thisshouldcreateapricedifferenceentry.
        """
        company=self.env.user.company_id
        company.anglo_saxon_accounting=True
        company.currency_id=self.usd_currency
        self.product1.product_tmpl_id.categ_id.property_cost_method='average'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'

        date_po='2019-01-01'
        date_delivery='2019-01-08'
        date_invoice='2019-01-16'

        product_avg=self.product1_copy
        product_avg.write({
            'purchase_method':'purchase',
            'name':'AVG',
            'standard_price':60,
            'property_account_creditor_price_difference':self.price_diff_account.id
        })

        #SetUpcurrencyandrates
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",(self.usd_currency.id,company.id))
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.0,
            'currency_id':self.usd_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.5,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_delivery,
            'rate':0.7,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_invoice,
            'rate':2,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        #ToallowtestingvalidationofPOandDelivery
        today=date_po
        def_today(*args,**kwargs):
            returndatetime.strptime(today,"%Y-%m-%d").date()
        def_now(*args,**kwargs):
            returndatetime.strptime(today+'01:00:00',"%Y-%m-%d%H:%M:%S")

        patchers=[
            patch('flectra.fields.Date.context_today',_today),
            patch('flectra.fields.Datetime.now',_now),
        ]

        forpinpatchers:
            p.start()

        #Proceed
        po=self.env['purchase.order'].create({
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':product_avg.name,
                    'product_id':product_avg.id,
                    'product_qty':1.0,
                    'product_uom':product_avg.uom_po_id.id,
                    'price_unit':30.0,
                    'date_planned':date_po,
                })
            ],
        })
        po.button_confirm()

        line_product_avg=po.order_line.filtered(lambdal:l.product_id==product_avg)

        today=date_delivery
        picking=po.picking_ids
        (picking.move_lines
            .filtered(lambdal:l.purchase_line_id==line_product_avg)
            .write({'quantity_done':1.0}))

        picking.button_validate()
        #5Unitsreceivedatrate0.7=42.86
        self.assertAlmostEqual(product_avg.standard_price,42.86)

        today=date_invoice
        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_invoice,
            'date':date_invoice,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[
                (0,0,{
                    'name':product_avg.name,
                    'price_unit':30.0,
                    'product_id':product_avg.id,
                    'purchase_line_id':line_product_avg.id,
                    'quantity':1.0,
                    'account_id':self.stock_input_account.id,
                })
            ]
        })

        inv.action_post()

        forpinpatchers:
            p.stop()

        move_lines=inv.line_ids
        self.assertEqual(len(move_lines),2)

        #PAYABLECHECK
        payable_line=move_lines.filtered(lambdal:l.account_id.internal_type=='payable')
        self.assertEqual(payable_line.amount_currency,-30.0)
        self.assertAlmostEqual(payable_line.balance,-15.00)

        #PRODUCTSCHECKS

        #DELIVERYDIFFERENCE(AVERAGE)
        #Weorderedaproductat30EURvaluedat20USD
        #Wereceiveditwhentheexchangeratehasappreciated
        #So,theactualized20USDarenow20*1.5/0.7=42.86USD
        product_lines=move_lines.filtered(lambdal:l.product_id==product_avg)

        #Althoughthose42.86USDarejustduetotheexchangedifference
        stock_line=product_lines.filtered(lambdal:l.account_id==self.stock_input_account)
        self.assertEqual(stock_line.journal_id,inv.journal_id)
        self.assertEqual(stock_line.amount_currency,30.00)
        self.assertAlmostEqual(stock_line.balance,15.00)
        full_reconcile=stock_line.full_reconcile_id
        self.assertTrue(full_reconcile.exists())

        reconciled_lines=full_reconcile.reconciled_line_ids-stock_line
        self.assertEqual(len(reconciled_lines),2)

        stock_journal_line=reconciled_lines.filtered(lambdal:l.journal_id==self.stock_journal)
        self.assertEqual(stock_journal_line.amount_currency,-30.00)
        self.assertAlmostEqual(stock_journal_line.balance,-42.86)

        exhange_diff_journal=company.currency_exchange_journal_id.exists()
        exchange_stock_line=reconciled_lines.filtered(lambdal:l.journal_id==exhange_diff_journal)
        self.assertEqual(exchange_stock_line.amount_currency,0.00)
        self.assertAlmostEqual(exchange_stock_line.balance,27.86)

    deftest_average_realtime_with_two_delivery_anglo_saxon_valuation_multicurrency_different_dates(self):
        """
        ThePOandinvoiceareinthesameforeigncurrency.
        Thedeliveriesoccuratdifferenttimesandrates
        Theinvoiceiscreatedatanevendifferentdate
        Thisshouldcreateapricedifferenceentry.
        """
        company=self.env.user.company_id
        company.anglo_saxon_accounting=True
        company.currency_id=self.usd_currency
        exchange_diff_journal=company.currency_exchange_journal_id.exists()

        date_po='2019-01-01'
        date_delivery='2019-01-08'
        date_delivery1='2019-01-10'
        date_invoice='2019-01-16'
        date_invoice1='2019-01-20'

        self.product1.categ_id.property_valuation='real_time'
        self.product1.categ_id.property_cost_method='average'
        product_avg=self.product1_copy
        product_avg.write({
            'purchase_method':'purchase',
            'name':'AVG',
            'standard_price':0,
            'property_account_creditor_price_difference':self.price_diff_account.id
        })

        #SetUpcurrencyandrates
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",(self.usd_currency.id,company.id))
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.0,
            'currency_id':self.usd_currency.id,
            'company_id':company.id,
        })
        self.env['res.currency.rate'].create({
            'name':date_po,
            'rate':1.5,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_delivery,
            'rate':0.7,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })
        self.env['res.currency.rate'].create({
            'name':date_delivery1,
            'rate':0.8,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        self.env['res.currency.rate'].create({
            'name':date_invoice,
            'rate':2,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })
        self.env['res.currency.rate'].create({
            'name':date_invoice1,
            'rate':2.2,
            'currency_id':self.eur_currency.id,
            'company_id':company.id,
        })

        #ToallowtestingvalidationofPOandDelivery
        today=date_po
        def_today(*args,**kwargs):
            returndatetime.strptime(today,"%Y-%m-%d").date()
        def_now(*args,**kwargs):
            returndatetime.strptime(today+'01:00:00',"%Y-%m-%d%H:%M:%S")

        patchers=[
            patch('flectra.fields.Date.context_today',_today),
            patch('flectra.fields.Datetime.now',_now),
        ]

        forpinpatchers:
            p.start()

        #Proceed
        po=self.env['purchase.order'].create({
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'date_order':date_po,
            'order_line':[
                (0,0,{
                    'name':product_avg.name,
                    'product_id':product_avg.id,
                    'product_qty':10.0,
                    'product_uom':product_avg.uom_po_id.id,
                    'price_unit':30.0,
                    'date_planned':date_po,
                })
            ],
        })
        po.button_confirm()

        line_product_avg=po.order_line.filtered(lambdal:l.product_id==product_avg)

        today=date_delivery
        picking=po.picking_ids
        (picking.move_lines
            .filtered(lambdal:l.purchase_line_id==line_product_avg)
            .write({'quantity_done':5.0}))

        picking.button_validate()
        picking._action_done() #CreateBackorder
        #5Unitsreceivedatrate0.7=42.86
        self.assertAlmostEqual(product_avg.standard_price,42.86)

        today=date_invoice
        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_invoice,
            'date':date_invoice,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[
                (0,0,{
                    'name':product_avg.name,
                    'price_unit':20.0,
                    'product_id':product_avg.id,
                    'purchase_line_id':line_product_avg.id,
                    'quantity':5.0,
                    'account_id':self.stock_input_account.id,
                })
            ]
        })

        inv.action_post()

        today=date_delivery1
        backorder_picking=self.env['stock.picking'].search([('backorder_id','=',picking.id)])
        (backorder_picking.move_lines
            .filtered(lambdal:l.purchase_line_id==line_product_avg)
            .write({'quantity_done':5.0}))
        backorder_picking.button_validate()
        #5Unitsreceivedatrate0.7(42.86)+5Unitsreceivedatrate0.8(37.50)=40.18
        self.assertAlmostEqual(product_avg.standard_price,40.18)

        today=date_invoice1
        inv1=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'invoice_date':date_invoice1,
            'date':date_invoice1,
            'currency_id':self.eur_currency.id,
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[
                (0,0,{
                    'name':product_avg.name,
                    'price_unit':40.0,
                    'product_id':product_avg.id,
                    'purchase_line_id':line_product_avg.id,
                    'quantity':5.0,
                    'account_id':self.stock_input_account.id,
                })
            ]
        })

        inv1.action_post()

        forpinpatchers:
            p.stop()

        ##########################
        #      Invoice0       #
        ##########################
        move_lines=inv.line_ids
        self.assertEqual(len(move_lines),4)

        #PAYABLECHECK
        payable_line=move_lines.filtered(lambdal:l.account_id.internal_type=='payable')
        self.assertEqual(payable_line.amount_currency,-100.0)
        self.assertAlmostEqual(payable_line.balance,-50.00)

        ##PRODUCTSCHECKS

        #DELIVERYDIFFERENCE(AVERAGE)
        stock_lines=move_lines.filtered(lambdal:l.account_id==self.stock_input_account)
        self.assertEqual(len(stock_lines),2)
        self.assertAlmostEqual(sum(stock_lines.mapped('amount_currency')),150.00)
        self.assertAlmostEqual(sum(stock_lines.mapped('balance')),75.00)

        price_diff_line=move_lines.filtered(lambdal:l.account_id==self.price_diff_account)
        self.assertAlmostEqual(price_diff_line.amount_currency,-50.00)
        self.assertAlmostEqual(price_diff_line.balance,-25.00)

        full_reconcile=stock_lines.mapped('full_reconcile_id')
        self.assertTrue(full_reconcile.exists())

        reconciled_lines=full_reconcile.reconciled_line_ids-stock_lines
        self.assertEqual(len(reconciled_lines),2)

        stock_journal_line=reconciled_lines.filtered(lambdal:l.journal_id==self.stock_journal)
        self.assertEqual(stock_journal_line.amount_currency,-150)
        self.assertAlmostEqual(stock_journal_line.balance,-214.29)

        exchange_stock_line=reconciled_lines.filtered(lambdal:l.journal_id==exchange_diff_journal)
        self.assertEqual(exchange_stock_line.amount_currency,0.00)
        self.assertAlmostEqual(exchange_stock_line.balance,139.29)

        ##########################
        #      Invoice1       #
        ##########################
        move_lines=inv1.line_ids
        self.assertEqual(len(move_lines),4)

        #PAYABLECHECK
        payable_line=move_lines.filtered(lambdal:l.account_id.internal_type=='payable')
        self.assertEqual(payable_line.amount_currency,-200.0)
        self.assertAlmostEqual(payable_line.balance,-90.91)

        ##PRODUCTSCHECKS

        #DELIVERYDIFFERENCE(AVERAGE)
        stock_lines=move_lines.filtered(lambdal:l.account_id==self.stock_input_account)
        self.assertEqual(stock_lines.mapped('journal_id'),inv.journal_id)
        self.assertAlmostEqual(sum(stock_lines.mapped('amount_currency')),150.00)
        self.assertAlmostEqual(sum(stock_lines.mapped('balance')),68.18)

        price_diff_line=move_lines.filtered(lambdal:l.account_id==self.price_diff_account)
        self.assertEqual(price_diff_line.amount_currency,50.00)
        self.assertAlmostEqual(price_diff_line.balance,22.73)

        full_reconcile=stock_lines.mapped('full_reconcile_id')
        self.assertTrue(full_reconcile.exists())

        reconciled_lines=full_reconcile.reconciled_line_ids-stock_lines
        self.assertEqual(len(reconciled_lines),3)

        stock_journal_line=reconciled_lines.filtered(lambdal:l.journal_id==self.stock_journal)
        self.assertEqual(stock_journal_line.amount_currency,-150)
        self.assertAlmostEqual(stock_journal_line.balance,-187.5)

        exchange_stock_lines=reconciled_lines.filtered(lambdal:l.journal_id==exchange_diff_journal)
        self.assertAlmostEqual(sum(exchange_stock_lines.mapped('amount_currency')),0.00)
        self.assertAlmostEqual(sum(exchange_stock_lines.mapped('balance')),119.32)

    deftest_anglosaxon_valuation_price_total_diff_discount(self):
        """
        PO: priceunit:110
        Inv:priceunit:100
             discount:   10
        """
        self.env.company.anglo_saxon_accounting=True
        self.product1.categ_id.property_cost_method='fifo'
        self.product1.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #CreatePO
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_id
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=self.product1
            po_line.product_qty=1
            po_line.price_unit=110.0
        order=po_form.save()
        order.button_confirm()

        #Receivethegoods
        receipt=order.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #Createaninvoicewithadifferentpriceandadiscount
        invoice_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        invoice_form.invoice_date=invoice_form.date
        invoice_form.purchase_id=order
        withinvoice_form.invoice_line_ids.edit(0)asline_form:
            line_form.price_unit=100.0
            line_form.discount=10.0
        invoice=invoice_form.save()
        invoice.action_post()

        #Checkwhatwaspostedinthepricedifferenceaccount
        price_diff_aml=self.env['account.move.line'].search([('account_id','=',self.price_diff_account.id)])
        self.assertEqual(len(price_diff_aml),1,"Onlyonelineshouldhavebeengeneratedinthepricedifferenceaccount.")
        self.assertAlmostEqual(price_diff_aml.credit,20,msg="Pricedifferenceshouldbeequalto20(110-90)")

        #Checkwhatwaspostedinstockinputaccount
        input_aml=self.env['account.move.line'].search([('account_id','=',self.stock_input_account.id)])
        self.assertEqual(len(input_aml),3,"Onlytwolinesshouldhavebeengeneratedinstockinputaccount:onewhenreceivingtheproduct,twowhenmakingtheinvoice.")
        self.assertAlmostEqual(sum(input_aml.mapped('debit')),110,msg="TotaldebitvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(sum(input_aml.mapped('credit')),110,msg="TotalcreditvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")

    deftest_anglosaxon_valuation_discount(self):
        """
        PO: priceunit:100
        Inv:priceunit:100
             discount:   10
        """
        self.env.company.anglo_saxon_accounting=True
        self.product1.categ_id.property_cost_method='fifo'
        self.product1.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #CreatePO
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_id
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=self.product1
            po_line.product_qty=1
            po_line.price_unit=100.0
        order=po_form.save()
        order.button_confirm()

        #Receivethegoods
        receipt=order.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #Createaninvoicewithadifferentpriceandadiscount
        invoice_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        invoice_form.invoice_date=invoice_form.date
        invoice_form.purchase_id=order
        withinvoice_form.invoice_line_ids.edit(0)asline_form:
            line_form.tax_ids.clear()
            line_form.discount=10.0
        invoice=invoice_form.save()
        invoice.action_post()

        #Checkwhatwaspostedinthepricedifferenceaccount
        price_diff_aml=self.env['account.move.line'].search([('account_id','=',self.price_diff_account.id)])
        self.assertEqual(len(price_diff_aml),1,"Onlyonelineshouldhavebeengeneratedinthepricedifferenceaccount.")
        self.assertAlmostEqual(price_diff_aml.credit,10,msg="Pricedifferenceshouldbeequalto10(100-90)")

        #Checkwhatwaspostedinstockinputaccount
        input_aml=self.env['account.move.line'].search([('account_id','=',self.stock_input_account.id)])
        self.assertEqual(len(input_aml),3,"Threelinesgeneratedinstockinputaccount:onewhenreceivingtheproduct,twowhenmakingtheinvoice.")
        self.assertAlmostEqual(sum(input_aml.mapped('debit')),100,msg="TotaldebitvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(sum(input_aml.mapped('credit')),100,msg="TotalcreditvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")

    deftest_anglosaxon_valuation_price_unit_diff_discount(self):
        """
        PO: priceunit: 90
        Inv:priceunit:100
             discount:   10
        """
        self.env.company.anglo_saxon_accounting=True
        self.product1.categ_id.property_cost_method='fifo'
        self.product1.categ_id.property_valuation='real_time'
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #CreatePO
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_id
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=self.product1
            po_line.product_qty=1
            po_line.price_unit=90.0
        order=po_form.save()
        order.button_confirm()

        #Receivethegoods
        receipt=order.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #Createaninvoicewithadifferentpriceandadiscount
        invoice_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        invoice_form.invoice_date=invoice_form.date
        invoice_form.purchase_id=order
        withinvoice_form.invoice_line_ids.edit(0)asline_form:
            line_form.price_unit=100.0
            line_form.discount=10.0
        invoice=invoice_form.save()
        invoice.action_post()

        #Checkifsomethingwaspostedinthepricedifferenceaccount
        price_diff_aml=self.env['account.move.line'].search([('account_id','=',self.price_diff_account.id)])
        self.assertEqual(len(price_diff_aml),0,"Nolineshouldhavebeengeneratedinthepricedifferenceaccount.")

        #Checkwhatwaspostedinstockinputaccount
        input_aml=self.env['account.move.line'].search([('account_id','=',self.stock_input_account.id)])
        self.assertEqual(len(input_aml),2,"Onlytwolinesshouldhavebeengeneratedinstockinputaccount:onewhenreceivingtheproduct,onewhenmakingtheinvoice.")
        self.assertAlmostEqual(sum(input_aml.mapped('debit')),90,msg="TotaldebitvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")
        self.assertAlmostEqual(sum(input_aml.mapped('credit')),90,msg="TotalcreditvalueonstockinputaccountshouldbeequaltotheoriginalPOpriceoftheproduct.")

    deftest_anglosaxon_valuation_price_unit_diff_avco(self):
        """
        Inv:priceunit:100
        """
        self.env.company.anglo_saxon_accounting=True
        self.product1.categ_id.property_cost_method='average'
        self.product1.categ_id.property_valuation='real_time'
        self.product1.categ_id.property_account_creditor_price_difference_categ=self.price_diff_account
        self.product1.standard_price=1.01

        invoice=self.env['account.move'].create({
            'move_type':'in_invoice',
            'invoice_date':'2022-03-31',
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[
                (0,0,{'product_id':self.product1.id,'quantity':10.50,'price_unit':1.01,'tax_ids':self.tax_purchase_a.ids})
            ]
        })

        invoice.action_post()

        #Checkifsomethingwaspostedinthepricedifferenceaccount
        price_diff_aml=invoice.line_ids.filtered(lambdal:l.account_id==self.price_diff_account)
        self.assertEqual(len(price_diff_aml),0,"Nolineshouldhavebeengeneratedinthepricedifferenceaccount.")

    deftest_anglosaxon_valuation_price_unit_diff_standard(self):
        """
        Checkthepriceunitdifferenceaccountishitwiththecorrectamount
        """
        self.env.ref("product.decimal_price").digits=6
        self.env.company.anglo_saxon_accounting=True
        self.product1.categ_id.property_cost_method='standard'
        self.product1.categ_id.property_valuation='real_time'
        self.product1.categ_id.property_account_creditor_price_difference_categ=self.price_diff_account
        self.product1.standard_price=0.01719

        invoice=self.env['account.move'].create({
            'move_type':'in_invoice',
            'invoice_date':'2022-03-31',
            'partner_id':self.partner_id.id,
            'invoice_line_ids':[
                (0,0,{'product_id':self.product1.id,'quantity':30000,'price_unit':0.01782,'tax_ids':self.tax_purchase_a.ids})
            ]
        })

        invoice.action_post()

        #Checkifsomethingwaspostedinthepricedifferenceaccount
        price_diff_aml=invoice.line_ids.filtered(lambdal:l.account_id==self.price_diff_account)
        self.assertEqual(len(price_diff_aml),1,"Alineshouldhavebeengeneratedinthepricedifferenceaccount.")
        self.assertAlmostEqual(price_diff_aml.balance,18.90)
