#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra

fromflectraimporttools
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon


@flectra.tests.tagged('post_install','-at_install')
classTestPoSBasicConfig(TestPoSCommon):
    """TestPoSwithbasicconfiguration

    Thetestscontainbasescenariosinusingpos.
    Morespecializedcasesaretestedinothertests.
    """

    defsetUp(self):
        super(TestPoSBasicConfig,self).setUp()
        self.config=self.basic_config
        self.product0=self.create_product('Product0',self.categ_basic,0.0,0.0)
        self.product1=self.create_product('Product1',self.categ_basic,10.0,5)
        self.product2=self.create_product('Product2',self.categ_basic,20.0,10)
        self.product3=self.create_product('Product3',self.categ_basic,30.0,15)
        self.product4=self.create_product('Product_4',self.categ_basic,9.96,4.98)
        self.adjust_inventory([self.product1,self.product2,self.product3],[100,50,50])

    deftest_orders_no_invoiced(self):
        """Testfororderswithoutinvoice

        3orders
        -first2orderswithcashpayment
        -lastorderwithbankpayment

        Orders
        ======
        +---------+----------+-----------+----------+-----+-------+
        |order  |payments|invoiced?|product |qty|total|
        +---------+----------+-----------+----------+-----+-------+
        |order1|cash    |no       |product1| 10|  100|
        |        |         |          |product2|  5|  100|
        +---------+----------+-----------+----------+-----+-------+
        |order2|cash    |no       |product2|  7|  140|
        |        |         |          |product3|  1|   30|
        +---------+----------+-----------+----------+-----+-------+
        |order3|bank    |no       |product1|  1|   10|
        |        |         |          |product2|  3|   60|
        |        |         |          |product3|  5|  150|
        +---------+----------+-----------+----------+-----+-------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale               |   -590|
        |posreceivablecash|    370|
        |posreceivablebank|    220|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """
        start_qty_available={
            self.product1:self.product1.qty_available,
            self.product2:self.product2.qty_available,
            self.product3:self.product3.qty_available,
        }

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product1,10),(self.product2,5)]))
        orders.append(self.create_ui_order_data([(self.product2,7),(self.product3,1)]))
        orders.append(self.create_ui_order_data(
            [(self.product1,1),(self.product3,5),(self.product2,3)],
            payments=[(self.bank_pm,220)]
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(
            self.product1.qty_available+11,
            start_qty_available[self.product1],
        )
        self.assertEqual(
            self.product2.qty_available+15,
            start_qty_available[self.product2],
        )
        self.assertEqual(
            self.product3.qty_available+6,
            start_qty_available[self.product3],
        )

        #pickingandstockmovesshouldbeindonestate
        fororderinself.pos_session.order_ids:
            self.assertEqual(
                order.picking_ids[0].state,
                'done',
                'Pickingshouldbeindonestate.'
            )
            move_lines=order.picking_ids[0].move_lines
            self.assertEqual(
                move_lines.mapped('state'),
                ['done']*len(move_lines),
                'MoveLinesshouldbeindonestate.'
            )

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkaccountingvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sales_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sales_line.balance,-590.0,msg='Saleslinebalanceshouldbeequaltototalordersamount.')

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,220.0,msg='Bankreceivableshouldbeequaltothetotalbankpayments.')

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,370.0,msg='Cashreceivableshouldbeequaltothetotalcashpayments.')

        self.assertTrue(receivable_line_cash.full_reconcile_id,msg='Cashreceivablelineshouldbefully-reconciled.')

    deftest_orders_with_invoiced(self):
        """Testfororders:onewithinvoice

        3orders
        -order1,paidbycash
        -order2,paidbybank
        -order3,paidbybank,invoiced

        Orders
        ======
        +---------+----------+---------------+----------+-----+-------+
        |order  |payments|invoiced?    |product |qty|total|
        +---------+----------+---------------+----------+-----+-------+
        |order1|cash    |no           |product1|  6|   60|
        |        |         |              |product2|  3|   60|
        |        |         |              |product3|  1|   30|
        +---------+----------+---------------+----------+-----+-------+
        |order2|bank    |no           |product1|  1|   10|
        |        |         |              |product2| 20|  400|
        +---------+----------+---------------+----------+-----+-------+
        |order3|bank    |yes,customer|product1| 10|  100|
        |        |         |              |product3|  1|   30|
        +---------+----------+---------------+----------+-----+-------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale               |   -560|
        |posreceivablecash|    150|
        |posreceivablebank|    540|
        |receivable         |   -130|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """
        start_qty_available={
            self.product1:self.product1.qty_available,
            self.product2:self.product2.qty_available,
            self.product3:self.product3.qty_available,
        }

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product3,1),(self.product1,6),(self.product2,3)],
            payments=[(self.cash_pm,150)],
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,20),(self.product1,1)],
            payments=[(self.bank_pm,410)],
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product3,1)],
            payments=[(self.bank_pm,130)],
            customer=self.customer,
            is_invoiced=True,
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(
            self.product1.qty_available+17,
            start_qty_available[self.product1],
        )
        self.assertEqual(
            self.product2.qty_available+23,
            start_qty_available[self.product2],
        )
        self.assertEqual(
            self.product3.qty_available+2,
            start_qty_available[self.product3],
        )

        #pickingandstockmovesshouldbeindonestate
        #noexceptionforinvoicedorders
        fororderinself.pos_session.order_ids:
            self.assertEqual(
                order.picking_ids[0].state,
                'done',
                'Pickingshouldbeindonestate.'
            )
            move_lines=order.picking_ids[0].move_lines
            self.assertEqual(
                move_lines.mapped('state'),
                ['done']*len(move_lines),
                'MoveLinesshouldbeindonestate.'
            )

        #checkaccountmoveintheinvoicedorder
        invoiced_order=self.pos_session.order_ids.filtered(lambdaorder:order.account_move)
        self.assertEqual(1,len(invoiced_order),'Onlyoneorderisinvoicedinthistest.')
        invoice=invoiced_order.account_move
        self.assertAlmostEqual(invoice.amount_total,130,msg='Amounttotalshouldbe130.Productisuntaxed.')
        invoice_receivable_line=invoice.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)

        #checkstateofordersbeforevalidatingthesession.
        self.assertEqual('invoiced',invoiced_order.state,msg="stateshouldbe'invoiced'forinvoicedorders.")
        uninvoiced_orders=self.pos_session.order_ids-invoiced_order
        self.assertTrue(
            all([order.state=='paid'fororderinuninvoiced_orders]),
            msg="stateshouldbe'paid'foruninvoicedordersbeforevalidatingthesession."
        )

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkstateofordersaftervalidatingthesession.
        self.assertTrue(
            all([order.state=='done'fororderinuninvoiced_orders]),
            msg="Stateshouldbe'done'foruninvoicedordersaftervalidatingthesession."
        )

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sales_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sales_line.balance,-(orders_total-invoice.amount_total),msg='Saleslineshouldbetotalorderminusinvoicedorder.')

        pos_receivable_line_bank=session_move.line_ids.filtered(
            lambdaline:self.bank_pm.nameinline.nameandline.account_id==self.bank_pm.receivable_account_id
        )
        self.assertAlmostEqual(pos_receivable_line_bank.balance,540.0,msg='Bankreceivableshouldbeequaltothetotalbankpayments.')

        pos_receivable_line_cash=session_move.line_ids.filtered(
            lambdaline:self.cash_pm.nameinline.nameandline.account_id==self.bank_pm.receivable_account_id
        )
        self.assertAlmostEqual(pos_receivable_line_cash.balance,150.0,msg='Cashreceivableshouldbeequaltothetotalcashpayments.')

        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertAlmostEqual(receivable_line.balance,-invoice.amount_total)

        #cashreceivableandinvoicereceivablelinesshouldbefullyreconciled
        self.assertTrue(pos_receivable_line_cash.full_reconcile_id)
        self.assertTrue(receivable_line.full_reconcile_id)

        #matchingnumberofthereceivablelinesshouldbethesame
        self.assertEqual(receivable_line.full_reconcile_id,invoice_receivable_line.full_reconcile_id)

    deftest_orders_with_zero_valued_invoiced(self):
        """Oneinvoicedorderbutwithzeroreceivablelinebalance."""

        self.open_new_session()
        orders=[self.create_ui_order_data([(self.product0,1)],payments=[(self.bank_pm,0)],customer=self.customer,is_invoiced=True)]
        self.env['pos.order'].create_from_ui(orders)
        self.pos_session.action_pos_session_validate()

        invoice=self.pos_session.order_ids.account_move
        invoice_receivable_line=invoice.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        receivable_line=self.pos_session.move_id.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)

        self.assertTrue(invoice_receivable_line.reconciled)
        self.assertTrue(receivable_line.reconciled)

    deftest_return_order_invoiced(self):
        self.open_new_session()

        #createorder
        orders=[
            self.create_ui_order_data([(self.product1,10)],payments=[(self.cash_pm,100)],customer=self.customer,
                                      is_invoiced=True,uid='666-666-666')]
        self.env['pos.order'].create_from_ui(orders)
        order=self.pos_session.order_ids.filtered(lambdaorder:'666-666-666'inorder.pos_reference)

        #refund
        order.refund()
        refund_order=self.pos_session.order_ids.filtered(lambdaorder:order.state=='draft')

        #paytherefund
        context_make_payment={"active_ids":[refund_order.id],"active_id":refund_order.id}
        make_payment=self.env['pos.make.payment'].with_context(context_make_payment).create({
            'payment_method_id':self.cash_pm.id,
            'amount':-100,
        })
        make_payment.check()

        #invoicerefund
        refund_order.action_pos_order_invoice()

        #closethesession--justverify,thattherearenoerrors
        self.pos_session.action_pos_session_validate()

    deftest_return_order(self):
        """Testreturnorder

        2orders
        -2ndorderisreturned

        Orders
        ======
        +------------------+----------+-----------+----------+-----+-------+
        |order           |payments|invoiced?|product |qty|total|
        +------------------+----------+-----------+----------+-----+-------+
        |order1         |bank    |no       |product1|  1|   10|
        |                 |         |          |product2|  5|  100|
        +------------------+----------+-----------+----------+-----+-------+
        |order2         |cash    |no       |product1|  3|   30|
        |                 |         |          |product2|  2|   40|
        |                 |         |          |product3|  1|   30|
        +------------------+----------+-----------+----------+-----+-------+
        |order3(return)|cash    |no       |product1| -3|  -30|
        |                 |         |          |product2| -2|  -40|
        |                 |         |          |product3| -1|  -30|
        +------------------+----------+-----------+----------+-----+-------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale(sales)       |   -210|
        |sale(refund)      |    100|
        |posreceivablebank|    110|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """
        start_qty_available={
            self.product1:self.product1.qty_available,
            self.product2:self.product2.qty_available,
            self.product3:self.product3.qty_available,
        }

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,1),(self.product2,5)],
            payments=[(self.bank_pm,110)]
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,3),(self.product2,2),(self.product3,1)],
            payments=[(self.cash_pm,100)],
            uid='12345-123-1234'
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(2,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #returnorder
        order_to_return=self.pos_session.order_ids.filtered(lambdaorder:'12345-123-1234'inorder.pos_reference)
        order_to_return.refund()
        refund_order=self.pos_session.order_ids.filtered(lambdaorder:order.state=='draft')

        #checkifamounttopay
        self.assertAlmostEqual(refund_order.amount_total-refund_order.amount_paid,-100)

        #paytherefund
        context_make_payment={"active_ids":[refund_order.id],"active_id":refund_order.id}
        make_payment=self.env['pos.make.payment'].with_context(context_make_payment).create({
            'payment_method_id':self.cash_pm.id,
            'amount':-100,
        })
        make_payment.check()
        self.assertEqual(refund_order.state,'paid','Paymentisregistered,ordershouldbepaid.')
        self.assertAlmostEqual(refund_order.amount_paid,-100.0,msg='Amountpaidforreturnordershouldbenegative.')

        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(
            self.product1.qty_available+1,
            start_qty_available[self.product1],
        )
        self.assertEqual(
            self.product2.qty_available+5,
            start_qty_available[self.product2],
        )
        self.assertEqual(
            self.product3.qty_available,
            start_qty_available[self.product3],
        )

        #pickingandstockmovesshouldbeindonestate
        #noexceptionofreturnorders
        fororderinself.pos_session.order_ids:
            self.assertEqual(
                order.picking_ids[0].state,
                'done',
                'Pickingshouldbeindonestate.'
            )
            move_lines=order.picking_ids[0].move_lines
            self.assertEqual(
                move_lines.mapped('state'),
                ['done']*len(move_lines),
                'MoveLinesshouldbeindonestate.'
            )

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sale_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertEqual(len(sale_lines),2,msg='Thereshouldbelinesforbothsalesandrefund.')
        self.assertAlmostEqual(sum(sale_lines.mapped('balance')),-110.0)

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,110.0)

        #netcashinthesessioniszero,thus,thereshouldbenoreceivablecashline.
        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertFalse(receivable_line_cash,'Thereshouldbenoreceivablecashlinebecauseboththeorderandreturnorderarepaidwithcash-theycancelled.')

    deftest_split_cash_payments(self):
        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product2,5)],
            payments=[(self.cash_split_pm,100),(self.bank_pm,100)]
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,7),(self.product3,1)],
            payments=[(self.cash_split_pm,70),(self.bank_pm,100)]
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,1),(self.product3,5),(self.product2,3)],
            payments=[(self.cash_split_pm,120),(self.bank_pm,100)]
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        account_move=self.pos_session.move_id

        bank_receivable_lines=account_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertEqual(len(bank_receivable_lines),1,msg='Bankreceivablelinesshouldonlyhaveonelinebecauseit\'ssupposedtobecombined.')
        self.assertAlmostEqual(bank_receivable_lines.balance,300.0,msg='Bankreceivableshouldbeequaltothetotalbankpayments.')

        cash_receivable_lines=account_move.line_ids.filtered(lambdaline:self.cash_split_pm.nameinline.name)
        self.assertEqual(len(cash_receivable_lines),3,msg='Thereshouldbeanumberofcashreceivablelinesbecausethecash_pmis`split_transactions`.')
        self.assertAlmostEqual(sum(cash_receivable_lines.mapped('balance')),290,msg='Totalcashreceivablebalanceshouldbeequaltothetotalcashpayments.')

        forlineincash_receivable_lines:
            self.assertTrue(line.full_reconcile_id,msg='Eachcashreceivablelineshouldbefully-reconciled.')

    deftest_rounding_method(self):
        #setthecashroundingmethod
        self.config.cash_rounding=True
        self.config.rounding_method=self.env['account.cash.rounding'].create({
            'name':'add_invoice_line',
            'rounding':0.05,
            'strategy':'add_invoice_line',
            'profit_account_id':self.company['default_cash_difference_income_account_id'].copy().id,
            'loss_account_id':self.company['default_cash_difference_expense_account_id'].copy().id,
            'rounding_method':'HALF-UP',
        })

        self.open_new_session()

        """Testfororders:onewithinvoice

        3orders
        -order1,paidbycash
        -order2,paidbybank
        -order3,paidbybank,invoiced

        Orders
        ======
        +---------+----------+---------------+----------+-----+-------+
        |order  |payments|invoiced?    |product |qty|total|
        +---------+----------+---------------+----------+-----+-------+
        |order1|bank    |no           |product1|  6|   60|
        |        |         |              |product4|  4|39.84|
        +---------+----------+---------------+----------+-----+-------+
        |order2|bank    |yes          |product4|  3|29.88|
        |        |         |              |product2| 20|  400|
        +---------+----------+---------------+----------+-----+-------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale               |-596,56|
        |posreceivablebank| 516,64|
        |Roundingapplied   |  -0,01|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """

        #createorders
        orders=[]

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product4,3),(self.product2,20)],
            payments=[(self.bank_pm,429.90)]
        ))

        orders.append(self.create_ui_order_data(
            [(self.product1,6),(self.product4,4)],
            payments=[(self.bank_pm,99.85)]
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        self.assertEqual(orders[0]['data']['amount_return'],0,msg='Theamountreturnshouldbe0')
        self.assertEqual(orders[1]['data']['amount_return'],0,msg='Theamountreturnshouldbe0')

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_account_move=self.pos_session.move_id

        rounding_line=session_account_move.line_ids.filtered(lambdaline:line.name=='Roundingline')
        self.assertAlmostEqual(rounding_line.credit,0.03,msg='Thecreditshouldbeequalsto0.03')

    deftest_correct_partner_on_invoice_receivables(self):
        self.open_new_session()

        #createorders
        #eachorderwithtotalamountof100.
        orders=[]
        #from1stto8thorder:usethesamecustomer(self.customer)butvarieswithis_invoicedandpaymentmethod.
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.cash_pm,100)],customer=self.customer,is_invoiced=True,uid='00100-010-0001'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_pm,100)],customer=self.customer,is_invoiced=True,uid='00100-010-0002'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.cash_split_pm,100)],customer=self.customer,is_invoiced=True,uid='00100-010-0003'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_split_pm,100)],customer=self.customer,is_invoiced=True,uid='00100-010-0004'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.cash_pm,100)],customer=self.customer,uid='00100-010-0005'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_pm,100)],customer=self.customer,uid='00100-010-0006'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.cash_split_pm,100)],customer=self.customer,uid='00100-010-0007'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_split_pm,100)],customer=self.customer,uid='00100-010-0008'))
        #9thand10thordersforself.other_customer,bothinvoicedandpaidbybank
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_pm,100)],customer=self.other_customer,is_invoiced=True,uid='00100-010-0009'))
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_pm,100)],customer=self.other_customer,is_invoiced=True,uid='00100-010-0010'))
        #11thorder:invoicedtoself.customerwithbankpaymentmethod
        orders.append(self.create_ui_order_data([(self.product1,10)],payments=[(self.bank_pm,100)],customer=self.customer,is_invoiced=True,uid='00100-010-0011'))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #closethesession
        self.pos_session.action_pos_session_validate()

        #self.customer'sbanksplitpayments
        customer_pos_receivable_bank=self.pos_session.move_id.line_ids.filtered(lambdaline:line.partner_id==self.customerand'Split(Bank)PM'inline.name)
        self.assertEqual(len(customer_pos_receivable_bank),2,msg='thereare2banksplitpaymentsfromself.customer')
        self.assertEqual(bool(customer_pos_receivable_bank.full_reconcile_id),False,msg="thepos(bank)receivablelinesshouldn'tbereconciled")

        #self.customer'scashsplitpayments
        customer_pos_receivable_cash=self.pos_session.move_id.line_ids.filtered(lambdaline:line.partner_id==self.customerand'Split(Cash)PM'inline.name)
        self.assertEqual(len(customer_pos_receivable_cash),2,msg='thereare2cashsplitpaymentsfromself.customer')
        self.assertEqual(bool(customer_pos_receivable_cash.full_reconcile_id),True,msg="cashpos(cash)receivablelinesshouldbereconciled")

        #self.customer'sinvoicereceivablecounterpart
        customer_invoice_receivable_counterpart=self.pos_session.move_id.line_ids.filtered(lambdaline:line.partner_id==self.customerand'Frominvoicedorders'inline.name)
        self.assertEqual(len(customer_invoice_receivable_counterpart),1,msg='thereshouldoneaggregatedinvoicereceivablecounterpartforself.customer')
        self.assertEqual(bool(customer_invoice_receivable_counterpart.full_reconcile_id),True,msg='theaggregatedreceivableforself.customershouldbereconciled')
        self.assertEqual(customer_invoice_receivable_counterpart.balance,-500,msg='aggregatedbalanceshouldbe-500')

        #self.other_customeralsomadeinvoicedorders
        #therefore,itshouldalsohaveaggregatedreceivablecounterpartinthesession'saccount_move
        other_customer_invoice_receivable_counterpart=self.pos_session.move_id.line_ids.filtered(lambdaline:line.partner_id==self.other_customerand'Frominvoicedorders'inline.name)
        self.assertEqual(len(other_customer_invoice_receivable_counterpart),1,msg='thereshouldoneaggregatedinvoicereceivablecounterpartforself.other_customer')
        self.assertEqual(bool(other_customer_invoice_receivable_counterpart.full_reconcile_id),True,msg='theaggregatedreceivableforself.other_customershouldbereconciled')
        self.assertEqual(other_customer_invoice_receivable_counterpart.balance,-200,msg='aggregatedbalanceshouldbe-200')

    deftest_cash_register_if_no_order(self):
        #Processoneorderwithproduct3
        self.open_new_session()
        session=self.pos_session
        orders=[]
        order_data=self.create_ui_order_data([(self.product3,1)])
        amount_paid=order_data['data']['amount_paid']
        self.env['pos.order'].create_from_ui([order_data])
        session.action_pos_session_closing_control()

        cash_register=session.cash_register_id
        self.assertEqual(cash_register.balance_start,0)
        self.assertEqual(cash_register.balance_end_real,amount_paid)

        #Open/Closesessionwithoutanyorder
        self.open_new_session()
        session=self.pos_session
        session.action_pos_session_closing_control()
        cash_register=session.cash_register_id
        self.assertEqual(cash_register.balance_start,amount_paid)
        self.assertEqual(cash_register.balance_end_real,amount_paid)
        self.assertEqual(self.config.last_session_closing_cash,amount_paid)

        #Open/Closesessionwithcashcontrolandwithoutanyorder
        self.config.cash_control=True
        self.open_new_session()
        session=self.pos_session
        session.set_cashbox_pos(amount_paid,False)
        session.action_pos_session_closing_control()
        self.env['account.bank.statement.cashbox'].create([{
            'start_bank_stmt_ids':[],
            'end_bank_stmt_ids':[(4,session.cash_register_id.id,)],
            'cashbox_lines_ids':[(0,0,{'number':1,'coin_value':amount_paid})],
            'is_a_template':False
        }])
        session.action_pos_session_validate()
        self.assertEqual(cash_register.balance_start,amount_paid)
        self.assertEqual(cash_register.balance_end_real,amount_paid)
        self.assertEqual(self.config.last_session_closing_cash,amount_paid)

    deftest_start_balance_with_two_pos(self):
        """WhenhavingseveralPOSwithcashcontrol,thistestsensuresthateachPOShasitscorrectopeningamount"""

        defopen_and_check(pos_data):
            self.config=pos_data['config']
            self.open_new_session()
            session=self.pos_session
            self.assertEqual(session.cash_register_id.balance_start,pos_data['amount_paid'])
            session.set_cashbox_pos(pos_data['amount_paid'],False)

        self.config.cash_control=True
        pos01_config=self.config
        pos02_config=pos01_config.copy()
        pos01_data={'config':pos01_config,'p_qty':1,'amount_paid':0}
        pos02_data={'config':pos02_config,'p_qty':3,'amount_paid':0}

        forpos_datain[pos01_data,pos02_data]:
            open_and_check(pos_data)
            session=self.pos_session

            order_data=self.create_ui_order_data([(self.product3,pos_data['p_qty'])])
            pos_data['amount_paid']+=order_data['data']['amount_paid']
            self.env['pos.order'].create_from_ui([order_data])

            session.action_pos_session_closing_control()
            self.env['account.bank.statement.cashbox'].create([{
                'start_bank_stmt_ids':[],
                'end_bank_stmt_ids':[(4,session.cash_register_id.id,)],
                'cashbox_lines_ids':[(0,0,{'number':1,'coin_value':pos_data['amount_paid']})],
                'is_a_template':False
            }])
            session.action_pos_session_validate()

        open_and_check(pos01_data)
        open_and_check(pos02_data)

    deftest_refund_customer_reconcile(self):
        """Testreturninvoicedorder

                2orders
                -2ndorderisreturned

                Orders
                ======
                +------------------+----------+-----------+----------+-----+-------+
                |order           |payments|invoiced?|product |qty|total|
                +------------------+----------+-----------+----------+-----+-------+
                |order1         |bank    |yes      |product1|  3|   30|
                |                 |         |          |product2|  2|   40|
                |                 |         |          |product3|  1|   30|
                +------------------+----------+-----------+----------+-----+-------+
                |order2         |bank    |yes      |product1|  3|   30|
                |                 |         |          |product2|  2|   40|
                |                 |         |          |product3|  1|   30|
                +------------------+----------+-----------+----------+-----+-------+
                |order3(return)|bank    |yes      |product1| -3|  -30|
                |                 |         |          |product2| -2|  -40|
                |                 |         |          |product3| -1|  -30|
                +------------------+----------+-----------+----------+-----+-------+

                ExpectedResult
                ===============
                +---------------------+---------+
                |account            |balance|
                +---------------------+---------+
                |receivable         |   -100|
                |posreceivablebank|    100|
                +---------------------+---------+
                |Totalbalance      |    0.0|
                +---------------------+---------+
                """
        start_qty_available={
            self.product1:self.product1.qty_available,
            self.product2:self.product2.qty_available,
            self.product3:self.product3.qty_available,
        }

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,3),(self.product2,2),(self.product3,1)],
            payments=[(self.bank_pm,100)],
            is_invoiced=True,
            uid='12346-123-1234',
            customer=self.customer
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,3),(self.product2,2),(self.product3,1)],
            payments=[(self.bank_pm,100)],
            uid='12345-123-1234',
            is_invoiced=True,
            customer=self.customer
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(2,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,
                               msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #returnorder
        order_to_return=self.pos_session.order_ids.filtered(
            lambdaorder:'12345-123-1234'inorder.pos_reference)
        order_to_return.refund()
        refund_order=self.pos_session.order_ids.filtered(
            lambdaorder:order.state=='draft')

        #checkifamounttopay
        self.assertAlmostEqual(refund_order.amount_total-refund_order.amount_paid,
                               -100)

        #paytherefund
        context_make_payment={"active_ids":[refund_order.id],
                                "active_id":refund_order.id}
        make_payment=self.env['pos.make.payment'].with_context(
            context_make_payment).create({
            'payment_method_id':self.bank_pm.id,
            'amount':-100,
        })
        make_payment.check()
        self.assertEqual(refund_order.state,'paid',
                         'Paymentisregistered,ordershouldbepaid.')
        self.assertAlmostEqual(refund_order.amount_paid,-100.0,
                               msg='Amountpaidforreturnordershouldbenegative.')
        refund_order.action_pos_order_invoice()
        self.assertTrue(refund_order.account_move)
        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(
            self.product1.qty_available+3,
            start_qty_available[self.product1],
        )
        self.assertEqual(
            self.product2.qty_available+2,
            start_qty_available[self.product2],
        )
        self.assertEqual(
            self.product3.qty_available+1,
            start_qty_available[self.product3],
        )

        #pickingandstockmovesshouldbeindonestate
        #noexceptionofreturnorders
        fororderinself.pos_session.order_ids:
            self.assertEqual(
                order.picking_ids[0].state,
                'done',
                'Pickingshouldbeindonestate.'
            )
            move_lines=order.picking_ids[0].move_lines
            self.assertEqual(
                move_lines.mapped('state'),
                ['done']*len(move_lines),
                'MoveLinesshouldbeindonestate.'
            )

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sale_lines=session_move.line_ids.filtered(
            lambdaline:line.account_id==self.sale_account)
        self.assertEqual(len(sale_lines),0,
                         msg='Thereshouldbenolinesasallisinvoiced.')
        self.assertEqual(
            sum(session_move.line_ids.filtered(
                lambdaline:line.partner_id==self.customer
            ).mapped("balance")),
            -100
        )
        receivable_line_bank=session_move.line_ids.filtered(
            lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,100.0)
        fororderinself.pos_session.order_ids:
            self.assertEqual(0,order.account_move.amount_residual)

    deftest_multiple_customers_reconcile(self):
        """Testreturninvoicedorderfromanothercustomer

                2actions
                -1storderfromonecustomer
                -2ndorderisarefundfromanothercustomer

                Orders
                ======
                +------------------+----------+-----------+----------+-----+-------+
                |order           |payments|invoiced?|product |qty|total|
                +------------------+----------+-----------+----------+-----+-------+
                |order1         |bank    |yes      |product1|  3|   30|
                |                 |         |customer |product2|  2|   40|
                |                 |         |          |product3|  1|   30|
                +------------------+----------+-----------+----------+-----+-------+
                |order2(return)|bank    |yes      |product1| -3|  -30|
                |                 |         |other    |product2| -2|  -40|
                |                 |         |customer |product3| -1|  -30|
                +------------------+----------+-----------+----------+-----+-------+

                ExpectedResult
                ===============
                +---------------------------+---------+
                |account                  |balance|
                +---------------------------+---------+
                |receivablecustomer      |   -100|
                |receivableothercustomer|    100|
                |posreceivablebank      |      0|
                +---------------------------+---------+
                |Totalbalance            |    0.0|
                +---------------------------+---------+
                """
        start_qty_available={
            self.product1:self.product1.qty_available,
            self.product2:self.product2.qty_available,
            self.product3:self.product3.qty_available,
        }

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,3),(self.product2,2),(self.product3,1)],
            payments=[(self.bank_pm,100)],
            is_invoiced=True,
            uid='12346-123-1234',
            customer=self.customer
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,-3),(self.product2,-2),(self.product3,-1)],
            payments=[(self.bank_pm,-100)],
            uid='12345-123-1234',
            is_invoiced=True,
            customer=self.other_customer
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(2,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,
                               msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')
        self.assertEqual(
            self.product1.qty_available,
            start_qty_available[self.product1],
        )
        self.assertEqual(
            self.product2.qty_available,
            start_qty_available[self.product2],
        )
        self.assertEqual(
            self.product3.qty_available,
            start_qty_available[self.product3],
        )

        #pickingandstockmovesshouldbeindonestate
        #noexceptionofreturnorders
        fororderinself.pos_session.order_ids:
            self.assertEqual(
                order.picking_ids[0].state,
                'done',
                'Pickingshouldbeindonestate.'
            )
            move_lines=order.picking_ids[0].move_lines
            self.assertEqual(
                move_lines.mapped('state'),
                ['done']*len(move_lines),
                'MoveLinesshouldbeindonestate.'
            )

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sale_lines=session_move.line_ids.filtered(
            lambdaline:line.account_id==self.sale_account)
        self.assertEqual(len(sale_lines),0,
                         msg='Thereshouldbenolinesasallisinvoiced.')

        self.assertEqual(
            session_move.line_ids.filtered(
                lambdaline:line.partner_id==self.customer
            ).balance,
            -100
        )
        self.assertEqual(
            session_move.line_ids.filtered(
                lambdaline:line.partner_id==self.other_customer
            ).balance,
            100
        )
        receivable_line_bank=session_move.line_ids.filtered(
            lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,0.0)
        fororderinself.pos_session.order_ids:
            self.assertEqual(0,order.account_move.amount_residual)
