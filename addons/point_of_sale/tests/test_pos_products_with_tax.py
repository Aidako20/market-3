#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools

importflectra
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon
fromflectra.tests.commonimportForm


@flectra.tests.tagged('post_install','-at_install')
classTestPoSProductsWithTax(TestPoSCommon):
    """TestnormalconfigurationPoSsellingproductswithtax
    """

    defsetUp(self):
        super(TestPoSProductsWithTax,self).setUp()

        self.config=self.basic_config
        self.product1=self.create_product(
            'Product1',
            self.categ_basic,
            10.0,
            5.0,
            tax_ids=self.taxes['tax7'].ids,
        )
        self.product2=self.create_product(
            'Product2',
            self.categ_basic,
            20.0,
            10.0,
            tax_ids=self.taxes['tax10'].ids,
        )
        self.product3=self.create_product(
            'Product3',
            self.categ_basic,
            30.0,
            15.0,
            tax_ids=self.taxes['tax_group_7_10'].ids,
        )
        self.product4=self.create_product(
            'Product4',
            self.categ_basic,
            54.99,
            tax_ids=[self.taxes['tax_fixed006'].id,self.taxes['tax_fixed012'].id,self.taxes['tax21'].id],
        )
        self.adjust_inventory([self.product1,self.product2,self.product3],[100,50,50])

    deftest_orders_no_invoiced(self):
        """Testfororderswithoutinvoice

        Orders
        ======
        +---------+----------+-----------+----------+-----+---------+-----------------------+--------+
        |order  |payments|invoiced?|product |qty|untaxed|tax                  | total|
        +---------+----------+-----------+----------+-----+---------+-----------------------+--------+
        |order1|cash    |no       |product1| 10|    100|7                    |   107|
        |        |         |          |product2|  5|  90.91|9.09                 |   100|
        +---------+----------+-----------+----------+-----+---------+-----------------------+--------+
        |order2|cash    |no       |product2|  7| 127.27|12.73                |   140|
        |        |         |          |product3|  4| 109.09|10.91[10%]+7.64[7%]|127.64|
        +---------+----------+-----------+----------+-----+---------+-----------------------+--------+
        |order3|bank    |no       |product1|  1|     10|0.7                  |  10.7|
        |        |         |          |product2|  3|  54.55|5.45                 |    60|
        |        |         |          |product3|  5| 136.36|13.64[10%]+9.55[7%]|159.55|
        +---------+----------+-----------+----------+-----+---------+-----------------------+--------+

        Calculatedtaxes
        ================
            totaltax7%only+grouptax(10+7%)
                (7+0.7)+(7.64+9.55)=7.7+17.19=24.89
            totaltax10%only+grouptax(10+7%)
                (9.09+12.73+5.45)+(10.91+13.64)=27.27+24.55=51.82

        Thus,manually_calculated_taxes=(-24,89,-51.82)
        """

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product1,10),(self.product2,5)]))
        orders.append(self.create_ui_order_data([(self.product2,7),(self.product3,4)]))
        orders.append(self.create_ui_order_data(
            [(self.product1,1),(self.product3,5),(self.product2,3)],
            payments=[(self.bank_pm,230.25)]
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sales_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sum(sales_lines.mapped('balance')),-628.18,msg='Saleslinebalanceshouldbeequaltountaxedordersamount.')

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,230.25,msg='Bankreceivableshouldbeequaltothetotalbankpayments.')

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,474.64,msg='Cashreceivableshouldbeequaltothetotalcashpayments.')

        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)

        manually_calculated_taxes=(-24.89,-51.82)
        self.assertAlmostEqual(sum(manually_calculated_taxes),sum(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        base_amounts=(355.45,518.18)
        self.assertAlmostEqual(sum(base_amounts),sum(tax_lines.mapped('tax_base_amount')))

        self.assertTrue(receivable_line_cash.full_reconcile_id,'Cashreceivablelineshouldbefully-reconciled.')

    deftest_orders_with_invoiced(self):
        """Testfororders:onewithinvoice

        Orders
        ======
        +---------+----------+---------------+----------+-----+---------+---------------+--------+
        |order  |payments|invoiced?    |product |qty|untaxed|tax          | total|
        +---------+----------+---------------+----------+-----+---------+---------------+--------+
        |order1|cash    |no           |product1|  6|     60|4.2          |  64.2|
        |        |         |              |product2|  3|  54.55|5.45         |    60|
        |        |         |              |product3|  1|  27.27|2.73+1.91  | 31.91|
        +---------+----------+---------------+----------+-----+---------+---------------+--------+
        |order2|bank    |no           |product1|  1|     10|0.7          |  10.7|
        |        |         |              |product2| 20| 363.64|36.36        |   400|
        +---------+----------+---------------+----------+-----+---------+---------------+--------+
        |order3|bank    |yes,customer|product1| 10|    100|7            |   107|
        |        |         |              |product3| 10| 272.73|27.27+19.09|319.09|
        +---------+----------+---------------+----------+-----+---------+---------------+--------+

        Calculatedtaxes
        ================
            totaltax7%only
                4.2+0.7=>4.9+1.91=6.81
            totaltax10%only
                5.45+36.36=>41.81+2.73=44.54

        Thus,manually_calculated_taxes=(-6.81,-44.54)
        """

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product3,1),(self.product1,6),(self.product2,3)],
            payments=[(self.cash_pm,156.11)],
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,20),(self.product1,1)],
            payments=[(self.bank_pm,410.7)],
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product3,10)],
            payments=[(self.bank_pm,426.09)],
            customer=self.customer,
            is_invoiced=True,
            uid='09876-098-0987',
        ))
        orders.append(self.create_ui_order_data(
            [(self.product4,1)],
            payments=[(self.bank_pm,54.99)],
            customer=self.customer,
            is_invoiced=True,
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(4,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #checkaccountmoveintheinvoicedorder
        invoiced_orders=self.pos_session.order_ids.filtered(lambdaorder:order.is_invoiced)
        self.assertEqual(2,len(invoiced_orders),'Onlyoneorderisinvoicedinthistest.')
        invoices=invoiced_orders.mapped('account_move')
        self.assertAlmostEqual(sum(invoices.mapped('amount_total')),481.08)

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        #checksalesline
        #shouldnotincludetaxamounts
        sales_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sum(sales_lines.mapped('balance')),-515.46)

        #checkreceivableline
        #shouldbeequivalenttoreceivableintheinvoices
        #shouldalsobefully-reconciled
        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_idinself.receivable_account+self.env['account.account'].search([('name','=','AccountReceivable')])andline.name=='Frominvoicedorders')
        self.assertAlmostEqual(receivable_line.balance,-481.08)
        self.assertTrue(receivable_line.full_reconcile_id,msg='Receivablelineforinvoicesshouldbefullyreconciled.')

        pos_receivable_line_bank=session_move.line_ids.filtered(
            lambdaline:self.bank_pm.nameinline.nameandline.account_id==self.bank_pm.receivable_account_id
        )
        self.assertAlmostEqual(pos_receivable_line_bank.balance,891.78)

        pos_receivable_line_cash=session_move.line_ids.filtered(
            lambdaline:self.cash_pm.nameinline.nameandline.account_id==self.bank_pm.receivable_account_id
        )
        self.assertAlmostEqual(pos_receivable_line_cash.balance,156.11)
        self.assertTrue(pos_receivable_line_cash.full_reconcile_id)

        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertAlmostEqual(receivable_line.balance,-sum(invoices.mapped('amount_total')))

        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)

        manually_calculated_taxes=(-6.81,-44.54)
        self.assertAlmostEqual(sum(manually_calculated_taxes),sum(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        base_amounts=(97.27,445.46) #computationdoesnotincludeinvoicedorder.
        self.assertAlmostEqual(sum(base_amounts),sum(tax_lines.mapped('tax_base_amount')))

    deftest_return_order(self):
        """Testreturnorder

        Order(invoiced)
        ======
        +----------+----------+---------------+----------+-----+---------+-------------+-------+
        |order   |payments|invoiced?    |product |qty|untaxed|tax        |total|
        +----------+----------+---------------+----------+-----+---------+-------------+-------+
        |order1 |cash    |yes,customer|product1|  3|     30|2.1        | 32.1|
        |         |         |              |product2|  2|  36.36|3.64       |   40|
        |         |         |              |product3|  1|  27.27|2.73+1.91|31.91|
        +----------+----------+---------------+----------+-----+---------+-------------+-------+

        Theorderisinvoicedsothetaxoftheinvoicedorderisintheaccount_moveoftheorder.
        However,thereturnorderisnotinvoiced,thus,thejournalitemsareinthesession_move,
        whichwillcontainthetaxlinesofthereturnedproducts.

        manually_calculated_taxes=(4.01,6.37)
        """

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,3),(self.product2,2),(self.product3,1)],
            payments=[(self.cash_pm,104.01)],
            customer=self.customer,
            is_invoiced=True,
            uid='12345-123-1234',
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(1,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #returnorder
        order_to_return=self.pos_session.order_ids.filtered(lambdaorder:'12345-123-1234'inorder.pos_reference)
        order_to_return.refund()

        refund_order=self.pos_session.order_ids.filtered(lambdaorder:order.state=='draft')
        context_make_payment={"active_ids":[refund_order.id],"active_id":refund_order.id}
        make_payment=self.env['pos.make.payment'].with_context(context_make_payment).create({
            'payment_method_id':self.cash_pm.id,
            'amount':-104.01,
        })
        make_payment.check()
        self.assertEqual(refund_order.state,'paid','Paymentisregistered,ordershouldbepaid.')
        self.assertAlmostEqual(refund_order.amount_paid,-104.01,msg='Amountpaidforreturnordershouldbenegative.')

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        #insteadofcredit,thesaleslineshouldbedebit
        sales_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sum(sales_lines.mapped('balance')),93.63)

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertFalse(receivable_line_bank,msg='Thereshouldbenobankreceivablelinebecausenobankpaymentmade.')

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertFalse(receivable_line_cash,msg='Thereshouldbenocashreceivablelinebecauseitiscombinedwiththeoriginalcashpayment.')

        manually_calculated_taxes=(4.01,6.37) #shouldbepositivesinceitisreturnorder
        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)
        self.assertAlmostEqual(sum(manually_calculated_taxes),sum(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombinedandshouldbedebit.')

    deftest_entry_move_creation_with_unrelated_pos_session_open(self):
        """
            EnsurecorrecttagsassignmentduringentrymovecreationwhileaPOSsessionisstillopen
        """
        #Createanewtaxwithitscorrespondingtaxreportlines
        #inordertosimulatethetagsaffectation
        tax_report=self.env["account.tax.report"].create({
            "name":"Taxreport",
        })
        base_20=self.env["account.tax.report.line"].create({
            "name":"Base20",
            "tag_name":"20B",
            "report_id":tax_report.id,
            "sequence":1,
        })
        base_20_tag_plus,base_20_tag_minus=base_20.tag_ids.sorted("tax_negate")
        tax_20=self.env["account.tax.report.line"].create({
            "name":"20",
            "tag_name":"20T",
            "report_id":tax_report.id,
            "sequence":2,
        })
        tax_20_tag_plus,tax_20_tag_minus=tax_20.tag_ids.sorted("tax_negate")
        tax_20_incl=self.env['account.tax'].create({
            "name":"20%",
            "amount":20,
            "amount_type":"percent",
            "type_tax_use":"sale",
            'price_include':True,
            "invoice_repartition_line_ids":[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(6,0,base_20_tag_plus.ids)],
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'account_id':self.tax_received_account.id,
                    'tag_ids':[(6,0,tax_20_tag_plus.ids)],
                }),
            ]
        })
        self.open_new_session()
        self.env['pos.order'].create_from_ui([self.create_ui_order_data([
            (self.product1,1),
        ])])

        #Createanentry
        withForm(self.env["account.move"].with_context(
                default_move_type="entry"))asmove_form:
            withmove_form.line_ids.new()asline_form:
                line_form.account_id=self.sale_account
                line_form.credit=50.0
                line_form.tax_ids.add(tax_20_incl)
            withmove_form.line_ids.new()asline_form_2:
                line_form_2.account_id=self.pos_receivable_account
                line_form_2.debit=60.0
        move=move_form.save()
        #EnsurethattagsarenotaffectedbyopenedPOSsession
        sale_line_tag=move.line_ids.filtered(
            lambdaline:line.account_id==self.sale_account).tax_tag_ids
        self.assertEqual(sale_line_tag,base_20_tag_minus)
        tax_line_tag=move.line_ids.filtered(
            lambdaline:line.account_id==self.tax_received_account).tax_tag_ids
        self.assertEqual(tax_line_tag,tax_20_tag_minus)

        #ClosePOSsession
        self.pos_session.action_pos_session_validate()

        #Createanentry-checkiftheresultisthesameasabove
        withForm(self.env["account.move"].with_context(
                default_move_type="entry"))asmove_form:
            withmove_form.line_ids.new()asline_form:
                line_form.account_id=self.sale_account
                line_form.credit=50.0
                line_form.tax_ids.add(tax_20_incl)
            withmove_form.line_ids.new()asline_form_2:
                line_form_2.account_id=self.pos_receivable_account
                line_form_2.debit=60.0
        move=move_form.save()
        #EnsurethattagsarenotaffectedbyopenedPOSsession
        sale_line_tag=move.line_ids.filtered(
            lambdaline:line.account_id==self.sale_account).tax_tag_ids
        self.assertEqual(sale_line_tag,base_20_tag_minus)
        tax_line_tag=move.line_ids.filtered(
            lambdaline:line.account_id==self.tax_received_account).tax_tag_ids
        self.assertEqual(tax_line_tag,tax_20_tag_minus)

    deftest_pos_create_correct_account_move(self):
        """Testfororderswithglobalroundingdisabled

        Orders
        ======
        +---------+----------+-----------+----------+------+----------+------------------+--------+
        |order  |payments|invoiced?|product |qty | untaxed|tax             | total|
        +---------+----------+-----------+----------+------+----------+------------------+--------+
        |order1|cash    |no       |product1|   1|    10.0| 2.10           | 12.10|
        |        |         |          |product2|  -1|    -5.0|-1.05           | -6.05|
        +---------+----------+-----------+----------+------+----------+------------------+--------+
        """
        tax_21_incl=self.taxes['tax21']
        product1=self.create_product(
            name='Product1',
            category=self.categ_basic,
            lst_price=12.10,
            tax_ids=tax_21_incl.ids,
        )
        product2=self.create_product(
            name='Product2',
            category=self.categ_basic,
            lst_price=6.05,
            tax_ids=tax_21_incl.ids,
        )
        self.open_new_session()
        self.env['pos.order'].create_from_ui([self.create_ui_order_data([
            (product1,1),
            (product2,-1),
        ])])
        self.pos_session.action_pos_session_validate()

        lines=self.pos_session.move_id.line_ids.sorted('balance')
        self.assertEqual(2,len(lines.filtered(lambdal:l.tax_ids)),"Taxesshouldhavebeenseton2lines")
        self.assertEqual(4,len(lines.filtered(lambdal:l.tax_tag_ids)),"Tagsshouldhavebeenseton4lines")
        self.assertRecordValues(lines,[
            {'account_id':self.sale_account.id,          'balance':-10.0,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_invoice_base.ids},
            {'account_id':self.tax_received_account.id,  'balance':-2.10,'tax_ids':[],             'tax_tag_ids':self.tax_tag_invoice_tax.ids},
            {'account_id':self.tax_received_account.id,  'balance': 1.05,'tax_ids':[],             'tax_tag_ids':self.tax_tag_refund_tax.ids},
            {'account_id':self.sale_account.id,          'balance': 5.00,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_refund_base.ids},
            {'account_id':self.pos_receivable_account.id,'balance': 6.05,'tax_ids':[],             'tax_tag_ids':[]},
        ])

    deftest_pos_create_account_move_round_globally(self):
        """Testfororderswithglobalroundingenabled

        Orders
        ======
        +---------+----------+-----------+----------+------+----------+------------------+--------+
        |order  |payments|invoiced?|product |qty | untaxed|tax             | total|
        +---------+----------+-----------+----------+------+----------+------------------+--------+
        |order1|cash    |no       |product1|   1|    10.0| 2.10           | 12.10|
        |        |         |          |product2|  -1|    -5.0|-1.05           | -6.05|
        +---------+----------+-----------+----------+------+----------+------------------+--------+
        """
        tax_21_incl=self.taxes['tax21']
        tax_21_incl.company_id.tax_calculation_rounding_method='round_globally'

        product1=self.create_product(
            name='Product1',
            category=self.categ_basic,
            lst_price=12.10,
            tax_ids=tax_21_incl.ids,
        )
        product2=self.create_product(
            name='Product2',
            category=self.categ_basic,
            lst_price=6.05,
            tax_ids=tax_21_incl.ids,
        )
        self.open_new_session()
        self.env['pos.order'].create_from_ui([self.create_ui_order_data([
            (product1,1),
            (product2,-1),
        ])])
        self.pos_session.action_pos_session_validate()

        lines=self.pos_session.move_id.line_ids.sorted('balance')
        self.assertEqual(2,len(lines.filtered(lambdal:l.tax_ids)),"Taxesshouldhavebeenseton2lines")
        self.assertEqual(4,len(lines.filtered(lambdal:l.tax_tag_ids)),"Tagsshouldhavebeenseton4lines")
        self.assertRecordValues(lines,[
            {'account_id':self.sale_account.id,          'balance':-10.0,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_invoice_base.ids},
            {'account_id':self.tax_received_account.id,  'balance':-2.10,'tax_ids':[],             'tax_tag_ids':self.tax_tag_invoice_tax.ids},
            {'account_id':self.tax_received_account.id,  'balance': 1.05,'tax_ids':[],             'tax_tag_ids':self.tax_tag_refund_tax.ids},
            {'account_id':self.sale_account.id,          'balance': 5.00,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_refund_base.ids},
            {'account_id':self.pos_receivable_account.id,'balance': 6.05,'tax_ids':[],             'tax_tag_ids':[]},
        ])

    deftest_pos_create_correct_account_move_round_globally_discount(self):
        """Testfororderswithglobalroundingenabled

        Orders
        ======
        +---------+----------+------+----------+------+---------------------+-----------+---------------------------+---------+--------+--------+
        |order  |payments|inv?|product |qty |originalpriceunit|Discount |priceunitafterdiscount|untaxed|tax   | total|
        +---------+----------+------+----------+------+---------------------+-----------+---------------------------+---------+--------+--------+
        |order1|cash    |no  |product1|   1|              12.10|       5%|                    10.89|   9.00|  1.89| 10.89|
        |        |         |     |product2|  -1|               6.05|       5%|                     5.45|  -4.50| -0.95|-5.445|
        +---------+----------+------+----------+------+---------------------+-----------+---------------------------+---------+--------+--------+
        """
        tax_21_incl=self.taxes['tax21']
        tax_21_incl.company_id.tax_calculation_rounding_method='round_globally'

        product1=self.create_product(
            name='Product1',
            category=self.categ_basic,
            lst_price=12.10,
            tax_ids=tax_21_incl.ids,
        )
        product2=self.create_product(
            name='Product2',
            category=self.categ_basic,
            lst_price=6.05,
            tax_ids=tax_21_incl.ids,
        )
        self.open_new_session()
        self.env['pos.order'].create_from_ui([self.create_ui_order_data([
            (product1,1,10),
            (product2,-1,10),
        ])])
        self.pos_session.action_pos_session_validate()

        lines=self.pos_session.move_id.line_ids.sorted('balance')

        self.assertEqual(2,len(lines.filtered(lambdal:l.tax_ids)),"Taxesshouldhavebeenseton2lines")
        self.assertEqual(4,len(lines.filtered(lambdal:l.tax_tag_ids)),"Tagsshouldhavebeenseton4lines")
        self.assertRecordValues(lines,[
            {'account_id':self.sale_account.id,          'balance':-9.0,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_invoice_base.ids},
            {'account_id':self.tax_received_account.id,  'balance':-1.89,'tax_ids':[],             'tax_tag_ids':self.tax_tag_invoice_tax.ids},
            {'account_id':self.tax_received_account.id,  'balance': 0.95,'tax_ids':[],             'tax_tag_ids':self.tax_tag_refund_tax.ids},
            {'account_id':self.sale_account.id,          'balance':  4.5,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_refund_base.ids},
            {'account_id':self.pos_receivable_account.id,'balance': 5.44,'tax_ids':[],             'tax_tag_ids':[]},
        ])

    deftest_pos_create_correct_account_move_round_globally_discount_real_use_case(self):
        """Testfororderswithglobalroundingenabled

        Orders
        ======
        +---------+----------+------+----------+------+---------------------+-----------+---------------------------+---------+--------+--------+
        |order  |payments|inv?|product |qty |originalpriceunit|Discount |priceunitafterdiscount|untaxed|tax   | total|
        +---------+----------+------+----------+------+---------------------+-----------+---------------------------+---------+--------+--------+
        |order1|cash    |no  |product1|   6|              11.80|       5%|                    11.21|  55.59| 11.67| 67.26|
        |        |         |     |product2|  -6|              15.30|       5%|                   14.535| -72.07|-15.14|-87.21|
        +---------+----------+------+----------+------+---------------------+-----------+---------------------------+---------+--------+--------+
        """
        tax_21_incl=self.taxes['tax21']
        tax_21_incl.company_id.tax_calculation_rounding_method='round_globally'

        product1=self.create_product(
            name='Product1',
            category=self.categ_basic,
            lst_price=11.80,
            tax_ids=tax_21_incl.ids,
        )
        product2=self.create_product(
            name='Product2',
            category=self.categ_basic,
            lst_price=15.30,
            tax_ids=tax_21_incl.ids,
        )
        self.open_new_session()
        self.env['pos.order'].create_from_ui([self.create_ui_order_data([
            (product1,6,5),
            (product2,-6,5),
        ])])
        self.pos_session.action_pos_session_validate()

        lines=self.pos_session.move_id.line_ids.sorted('balance')

        self.assertEqual(2,len(lines.filtered(lambdal:l.tax_ids)),"Taxesshouldhavebeenseton2lines")
        self.assertEqual(4,len(lines.filtered(lambdal:l.tax_tag_ids)),"Tagsshouldhavebeenseton4lines")
        self.assertRecordValues(lines,[
            {'account_id':self.sale_account.id,          'balance':-55.59,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_invoice_base.ids},
            {'account_id':self.pos_receivable_account.id,'balance':-19.95,'tax_ids':[],             'tax_tag_ids':[]},
            {'account_id':self.tax_received_account.id,  'balance':-11.67,'tax_ids':[],             'tax_tag_ids':self.tax_tag_invoice_tax.ids},
            {'account_id':self.tax_received_account.id,  'balance': 15.14,'tax_ids':[],             'tax_tag_ids':self.tax_tag_refund_tax.ids},
            {'account_id':self.sale_account.id,          'balance': 72.07,'tax_ids':tax_21_incl.ids,'tax_tag_ids':self.tax_tag_refund_base.ids},
        ])

    deftest_fixed_tax_positive_qty(self):

        fixed_tax=self.env['account.tax'].create({
            'name':'fixedamounttax',
            'amount_type':'fixed',
            'amount':1,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(6,0,self.tax_tag_invoice_base.ids)],
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'account_id':self.tax_received_account.id,
                    'tag_ids':[(6,0,self.tax_tag_invoice_tax.ids)],
                }),
            ],
        })

        zero_amount_product=self.env['product.product'].create({
            'name':'ZeroAmountProduct',
            'available_in_pos':True,
            'list_price':0,
            'taxes_id':[(6,0,[fixed_tax.id])],
        })

        self.open_new_session()
        self.env['pos.order'].create_from_ui([self.create_ui_order_data([
            (zero_amount_product,1),
        ])])
        self.pos_session.action_pos_session_validate()

        lines=self.pos_session.move_id.line_ids.sorted('balance')

        self.assertRecordValues(lines,[
            {'account_id':self.tax_received_account.id,'balance':-1},
            {'account_id':self.sale_account.id,'balance':0},
            {'account_id':self.pos_receivable_account.id,'balance':1},
        ])
