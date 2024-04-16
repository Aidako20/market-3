#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra

fromflectraimporttools
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon

@flectra.tests.tagged('post_install','-at_install')
classTestPoSMultipleSaleAccounts(TestPoSCommon):
    """Testtoorderscontainingproductswithdifferentsaleaccounts

    keywords/phrases:DifferentIncomeAccounts

    Inthistest,twosale(income)accountsareinvolved:
        self.sale_account->defaultforproductsbecauseitisinthecategory
        self.other_sale_account->manuallysettoself.product2
    """

    defsetUp(self):
        super(TestPoSMultipleSaleAccounts,self).setUp()

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

    deftest_01_check_product_properties(self):
        self.assertEqual(self.product2.property_account_income_id,self.other_sale_account,'Incomeaccountfortheproduct2shouldbetheothersaleaccount.')
        self.assertFalse(self.product1.property_account_income_id,msg='Incomeaccountforproduct1shouldnotbeset.')
        self.assertFalse(self.product3.property_account_income_id,msg='Incomeaccountforproduct3shouldnotbeset.')
        self.assertEqual(self.product1.categ_id.property_account_income_categ_id,self.sale_account)
        self.assertEqual(self.product3.categ_id.property_account_income_categ_id,self.sale_account)

    deftest_02_orders_without_invoice(self):
        """orderswithoutinvoice

        Orders
        ======
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order  |payments|invoiced?|product |qty|untaxed|tax                     | total|
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order1|cash    |no       |product1| 10|  109.9|7.69[7%]               |117.59|
        |        |         |          |product2| 10| 181.73|18.17[10%]             | 199.9|
        |        |         |          |product3| 10| 281.73|19.72[7%]+28.17[10%]|329.62|
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order2|cash    |no       |product1|  5|  54.95|3.85[7%]               | 58.80|
        |        |         |          |product2|  5|  90.86|9.09[10%]              | 99.95|
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+
        |order3|bank    |no       |product2|  5|  90.86|9.09[10%]              | 99.95|
        |        |         |          |product3|  5| 140.86|9.86[7%]+14.09[10%] |164.81|
        +---------+----------+-----------+----------+-----+---------+--------------------------+--------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       |-164.85| (forthe7%baseamount)
        |sale_account       |-422.59| (forthe7+10%baseamount)
        |other_sale_account |-363.45|
        |tax7%             | -41.12|
        |tax10%            | -78.61|
        |posreceivablebank| 264.76|
        |posreceivablecash| 805.86|
        +---------------------+---------+
        |Totalbalance      |   0.00|
        +---------------------+---------+
        """

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product1,10),(self.product2,10),(self.product3,10)]))
        orders.append(self.create_ui_order_data([(self.product1,5),(self.product2,5)]))
        orders.append(self.create_ui_order_data([(self.product2,5),(self.product3,5)],payments=[(self.bank_pm,264.76)]))

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

        sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        forbalance,amountinzip(sorted(sale_account_lines.mapped('balance')),sorted([-164.85,-422.59])):
            self.assertAlmostEqual(balance,amount)

        other_sale_account_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_sale_account)
        self.assertAlmostEqual(other_sale_account_line.balance,-363.45)

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,264.76)

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,805.86)

        manually_calculated_taxes=(-41.12,-78.61)
        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)
        self.assertAlmostEqual(sum(manually_calculated_taxes),sum(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        self.assertTrue(receivable_line_cash.full_reconcile_id)

    deftest_03_orders_with_invoice(self):
        """orderswithinvoice

        Orders
        ======
        +---------+----------+---------------+----------+-----+---------+--------------------------+--------+
        |order  |payments|invoiced?    |product |qty|untaxed|tax                     | total|
        +---------+----------+---------------+----------+-----+---------+--------------------------+--------+
        |order1|cash    |no           |product1| 10|  109.9|7.69[7%]               |117.59|
        |        |         |              |product2| 10| 181.73|18.17[10%]             | 199.9|
        |        |         |              |product3| 10| 281.73|19.72[7%]+28.17[10%]|329.62|
        +---------+----------+---------------+----------+-----+---------+--------------------------+--------+
        |order2|bank    |no           |product1|  5|  54.95|3.85[7%]               | 58.80|
        |        |         |              |product2|  5|  90.86|9.09[10%]              | 99.95|
        +---------+----------+---------------+----------+-----+---------+--------------------------+--------+
        |order3|bank    |yes,customer|product2|  5|  90.86|9.09[10%]              | 99.95|
        |        |         |              |product3|  5| 140.86|9.86[7%]+14.09[10%] |164.81|
        +---------+----------+---------------+----------+-----+---------+--------------------------+--------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       |-164.85| (forthe7%baseamount)
        |sale_account       |-281.73| (forthe7+10%baseamount)
        |other_sale_account |-272.59|
        |tax7%             | -31.26|
        |tax10%            | -55.43|
        |posreceivablecash| 647.11|
        |posreceivablebank| 423.51|
        |receivable         |-264.76|
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
            customer=self.customer,
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

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        forbalance,amountinzip(sorted(sale_account_lines.mapped('balance')),sorted([-164.85,-281.73])):
            self.assertAlmostEqual(balance,amount)

        other_sale_account_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_sale_account)
        self.assertAlmostEqual(other_sale_account_line.balance,-272.59)

        pos_receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(pos_receivable_line_bank.balance,423.51)

        pos_receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(pos_receivable_line_cash.balance,647.11)

        manually_calculated_taxes=(-31.26,-55.43)
        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)
        self.assertAlmostEqual(sum(manually_calculated_taxes),sum(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertAlmostEqual(receivable_line.balance,-264.76)

        self.assertTrue(pos_receivable_line_cash.full_reconcile_id)
        self.assertTrue(receivable_line.full_reconcile_id)
