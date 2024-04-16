#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra

fromflectraimporttools
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon

@flectra.tests.tagged('post_install','-at_install')
classTestPoSMultipleReceivableAccounts(TestPoSCommon):
    """Testforinvoicedorderswithcustomershavingreceivableaccountdifferentfromdefault

    Thus,forthistest,therearetworeceivableaccountsinvolvedandaresetinthe
    customers.
        self.customer->self.receivable_account
        self.other_customer->self.other_receivable_account

    NOTEThatbothreceivableaccountsabovearedifferentfromtheposreceivableaccount.
    """

    defsetUp(self):
        super(TestPoSMultipleReceivableAccounts,self).setUp()
        self.config=self.basic_config
        self.product1=self.create_product(
            'Product1',
            self.categ_basic,
            lst_price=10.99,
            standard_price=5.0,
            tax_ids=self.taxes['tax7'].ids,
        )
        self.product2=self.create_product(
            'Product2',
            self.categ_basic,
            lst_price=19.99,
            standard_price=10.0,
            tax_ids=self.taxes['tax10'].ids,
            sale_account=self.other_sale_account,
        )
        self.product3=self.create_product(
            'Product3',
            self.categ_basic,
            lst_price=30.99,
            standard_price=15.0,
            tax_ids=self.taxes['tax_group_7_10'].ids,
        )
        self.adjust_inventory([self.product1,self.product2,self.product3],[100,50,50])

    deftest_01_invoiced_order_from_other_customer(self):
        """
        Orders
        ======
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order  |payments|invoiced?|product |qty|untaxed|tax                     |total |
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order1|cash    |no       |product1|10 |109.9  |7.69[7%]               |117.59|
        |        |         |          |product2|10 |181.73 |18.17[10%]             |199.9 |
        |        |         |          |product3|10 |281.73 |19.72[7%]+28.17[10%]|329.62|
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order2|bank    |no       |product1|5  |54.95  |3.85[7%]               |58.80 |
        |        |         |          |product2|5  |90.86  |9.09[10%]              |99.95 |
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order3|bank    |yes      |product2|5  |90.86  |9.09[10%]              |99.95 |
        |        |         |          |product3|5  |140.86 |9.86[7%]+14.09[10%] |164.81|
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       |-164.85|
        |sale_account       |-281.73|
        |other_sale_account |-272.59|
        |tax7%             | -31.26|
        |tax10%            | -55.43|
        |posreceivablecash| 647.11|
        |posreceivablebank| 423.51|
        |otherreceivable   |-264.76|
        +---------------------+---------+
        |Totalbalance      |   0.00|
        +---------------------+---------+
        """
        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product1,10),(self.product2,10),(self.product3,10)]))
        orders.append(self.create_ui_order_data(
            [(self.product1,5),(self.product2,5)],
            payments=[(self.bank_pm,158.75)],
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,5),(self.product3,5)],
            payments=[(self.bank_pm,264.76)],
            customer=self.other_customer,
            is_invoiced=True,
            uid='09876-098-0987',
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #checkifthereisoneinvoicedorder
        self.assertEqual(len(self.pos_session.order_ids.filtered(lambdaorder:order.state=='invoiced')),1,'Thereshouldonlybeoneinvoicedorder.')

        #closethesession
        self.pos_session.action_pos_session_validate()

        session_move=self.pos_session.move_id
        #Thereshouldbenolinecorrespondingtheoriginalreceivableaccount
        #Butthereshouldbealineforother_receivable_accountbecause
        #thatistheproperty_account_receivable_idofthecustomer
        #oftheinvoicedorder.
        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertFalse(receivable_line,msg='Thereshouldbenomovelinefortheoriginalreceivableaccount.')
        other_receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_receivable_account)
        self.assertAlmostEqual(other_receivable_line.balance,-264.76)

    deftest_02_all_orders_invoiced_mixed_customers(self):
        """
        Orders
        ======
        +---------+----------+---------------------+----------+-----+---------+--------------------------+--------+
        |order  |payments|invoiced?          |product |qty|untaxed|tax                     | total|
        +---------+----------+---------------------+----------+-----+---------+--------------------------+--------+
        |order1|cash    |yes,other_customer|product1| 10| 109.90|7.69[7%]               |117.59|
        |        |         |                    |product2| 10| 181.73|18.17[10%]             |199.90|
        |        |         |                    |product3| 10| 281.73|19.72[7%]+28.17[10%]|329.62|
        +---------+----------+---------------------+----------+-----+---------+--------------------------+--------+
        |order2|bank    |yes,customer      |product1|  5|  54.95|3.85[7%]               | 58.80|
        |        |         |                    |product2|  5|  90.86|9.09[10%]              | 99.95|
        +---------+----------+---------------------+----------+-----+---------+--------------------------+--------+
        |order3|bank    |yes,othercustomer|product2|  5|  90.86|9.09[10%]              | 99.95|
        |        |         |                    |product3|  5| 140.86|9.86[7%]+14.09[10%] |164.81|
        +---------+----------+---------------------+----------+-----+---------+--------------------------+--------+

        ExpectedResult
        ===============
        +------------------+---------+
        |account         |balance|
        +------------------+---------+
        |receivablecash | 647.11|
        |receivablebank | 423.51|
        |otherreceivable|-911.87|
        |receivable      |-158.75|
        +------------------+---------+
        |Totalbalance   |   0.00|
        +------------------+---------+

        """
        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product2,10),(self.product3,10)],
            customer=self.other_customer,
            is_invoiced=True,
            uid='09876-098-0987',
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,5),(self.product2,5)],
            payments=[(self.bank_pm,158.75)],
            customer=self.customer,
            is_invoiced=True,
            uid='09876-098-0988',
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,5),(self.product3,5)],
            payments=[(self.bank_pm,264.76)],
            customer=self.other_customer,
            is_invoiced=True,
            uid='09876-098-0989',
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        #checkifthereisoneinvoicedorder
        self.assertEqual(len(self.pos_session.order_ids.filtered(lambdaorder:order.state=='invoiced')),3,'Allordersshouldbeinvoiced.')

        #closethesession
        self.pos_session.action_pos_session_validate()

        session_move=self.pos_session.move_id

        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertAlmostEqual(receivable_line.balance,-158.75)
        other_receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_receivable_account)
        self.assertAlmostEqual(other_receivable_line.balance,-911.87)
        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,423.51)
        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,647.11)
