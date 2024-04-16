#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
importflectra
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon

@flectra.tests.tagged('post_install','-at_install')
classTestPoSWithFiscalPosition(TestPoSCommon):
    """Teststoposorderswithfiscalposition.

    keywords/phrases:fiscalposition
    """

    @classmethod
    defsetUpClass(cls):
        super(TestPoSWithFiscalPosition,cls).setUpClass()

        cls.config=cls.basic_config

        cls.new_tax_17=cls.env['account.tax'].create({'name':'NewTax17%','amount':17})
        cls.new_tax_17.invoice_repartition_line_ids.write({'account_id':cls.tax_received_account.id})

        cls.fpos=cls._create_fiscal_position()
        cls.fpos_no_tax_dest=cls._create_fiscal_position_no_tax_dest()

        cls.product1=cls.create_product(
            'Product1',
            cls.categ_basic,
            lst_price=10.99,
            standard_price=5.0,
            tax_ids=cls.taxes['tax7'].ids,
        )
        cls.product2=cls.create_product(
            'Product2',
            cls.categ_basic,
            lst_price=19.99,
            standard_price=10.0,
            tax_ids=cls.taxes['tax10'].ids,
        )
        cls.product3=cls.create_product(
            'Product3',
            cls.categ_basic,
            lst_price=30.99,
            standard_price=15.0,
            tax_ids=cls.taxes['tax7'].ids,
        )
        cls.adjust_inventory([cls.product1,cls.product2,cls.product3],[100,50,50])

    @classmethod
    def_create_fiscal_position(cls):
        fpos=cls.env['account.fiscal.position'].create({'name':'TestFiscalPosition'})

        account_fpos=cls.env['account.fiscal.position.account'].create({
            'position_id':fpos.id,
            'account_src_id':cls.sale_account.id,
            'account_dest_id':cls.other_sale_account.id,
        })
        tax_fpos=cls.env['account.fiscal.position.tax'].create({
            'position_id':fpos.id,
            'tax_src_id':cls.taxes['tax7'].id,
            'tax_dest_id':cls.new_tax_17.id,
        })
        fpos.write({
            'account_ids':[(6,0,account_fpos.ids)],
            'tax_ids':[(6,0,tax_fpos.ids)],
        })
        returnfpos

    @classmethod
    def_create_fiscal_position_no_tax_dest(cls):
        fpos_no_tax_dest=cls.env['account.fiscal.position'].create({'name':'TestFiscalPosition'})
        account_fpos=cls.env['account.fiscal.position.account'].create({
            'position_id':fpos_no_tax_dest.id,
            'account_src_id':cls.sale_account.id,
            'account_dest_id':cls.other_sale_account.id,
        })
        tax_fpos=cls.env['account.fiscal.position.tax'].create({
            'position_id':fpos_no_tax_dest.id,
            'tax_src_id':cls.taxes['tax7'].id,
        })
        fpos_no_tax_dest.write({
            'account_ids':[(6,0,account_fpos.ids)],
            'tax_ids':[(6,0,tax_fpos.ids)],
        })
        returnfpos_no_tax_dest

    deftest_01_no_invoice_fpos(self):
        """orderswithoutinvoice

        Orders
        ======
        +---------+----------+---------------+----------+-----+---------+-----------------+--------+
        |order  |payments|invoiced?    |product |qty|untaxed|tax            | total|
        +---------+----------+---------------+----------+-----+---------+-----------------+--------+
        |order1|cash    |yes,customer|product1| 10| 109.90|18.68[7%->17%]|128.58|
        |        |         |              |product2| 10| 181.73|18.17[10%]    |199.90|
        |        |         |              |product3| 10| 309.90|52.68[7%->17%]|362.58|
        +---------+----------+---------------+----------+-----+---------+-----------------+--------+
        |order2|cash    |yes,customer|product1|  5|  54.95|9.34[7%->17%] | 64.29|
        |        |         |              |product2|  5|  90.86|9.09[10%]     | 99.95|
        +---------+----------+---------------+----------+-----+---------+-----------------+--------+
        |order3|bank    |no           |product2|  5|  90.86|9.09[10%]     | 99.95|
        |        |         |              |product3|  5| 154.95|10.85[7%]     | 165.8|
        +---------+----------+---------------+----------+-----+---------+-----------------+--------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       |-154.95| (forthe7%baseamount)
        |sale_account       | -90.86| (forthe10%baseamount)
        |other_sale_account |-474.75| (forthe17%baseamount)
        |other_sale_account |-272.59| (forthe10%baseamount)
        |tax17%            | -80.70|
        |tax10%            | -36.35|
        |tax7%             | -10.85|
        |posreceivablebank| 265.75|
        |posreceivablecash| 855.30|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """

        self.customer.write({'property_account_position_id':self.fpos.id})
        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product2,10),(self.product3,10)],
            customer=self.customer
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,5),(self.product2,5)],
            customer=self.customer,
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,5),(self.product3,5)],
            payments=[(self.bank_pm,265.75)],
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

        sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        lines_balance=[-154.95,-90.86]
        self.assertEqual(len(sale_account_lines),len(lines_balance))
        forbalance,amountinzip(sorted(sale_account_lines.mapped('balance')),sorted(lines_balance)):
            self.assertAlmostEqual(balance,amount)

        other_sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_sale_account)
        lines_balance=[-474.75,-272.59]
        self.assertEqual(len(other_sale_account_lines),len(lines_balance))
        forbalance,amountinzip(sorted(other_sale_account_lines.mapped('balance')),sorted(lines_balance)):
            self.assertAlmostEqual(balance,amount)

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,265.75)

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,855.3)

        manually_calculated_taxes=(-80.7,-36.35,-10.85)
        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)
        self.assertAlmostEqual(len(manually_calculated_taxes),len(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        self.assertTrue(receivable_line_cash.full_reconcile_id)

    deftest_02_no_invoice_fpos_no_tax_dest(self):
        """Customerwithfiscalpositionthatmapsataxtonotax.

        Orders
        ======
        +---------+----------+---------------+----------+-----+---------+-------------+--------+
        |order  |payments|invoiced?    |product |qty|untaxed|tax        | total|
        +---------+----------+---------------+----------+-----+---------+-------------+--------+
        |order1|bank    |yes,customer|product1| 10| 109.90|0          |109.90|
        |        |         |              |product2| 10| 181.73|18.17[10%]|199.90|
        |        |         |              |product3| 10| 309.90|0          |309.90|
        +---------+----------+---------------+----------+-----+---------+-------------+--------+
        |order2|cash    |yes,customer|product1|  5|  54.95|0          | 54.95|
        |        |         |              |product2|  5|  90.86|9.09[10%] | 99.95|
        +---------+----------+---------------+----------+-----+---------+-------------+--------+
        |order3|bank    |no           |product2|  5|  90.86|9.09[10%] | 99.95|
        |        |         |              |product3|  5| 154.95|10.85[7%] |165.80|
        +---------+----------+---------------+----------+-----+---------+-------------+--------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       |-154.95| (forthe7%baseamount)
        |sale_account       | -90.86| (forthe10%baseamount)
        |other_sale_account |-272.59| (forthe10%baseamount)
        |other_sale_account |-474.75| (notax)
        |tax10%            | -36.35|
        |tax7%             | -10.85|
        |posreceivablebank| 885.45|
        |posreceivablecash|  154.9|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """

        self.customer.write({'property_account_position_id':self.fpos_no_tax_dest.id})
        self.open_new_session()
        #createorders
        orders=[]
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product2,10),(self.product3,10)],
            customer=self.customer,
            payments=[(self.bank_pm,619.7)],
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,5),(self.product2,5)],
            customer=self.customer,
        ))
        orders.append(self.create_ui_order_data(
            [(self.product2,5),(self.product3,5)],
            payments=[(self.bank_pm,265.75)],
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

        sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        lines_balance=[-154.95,-90.86]
        self.assertEqual(len(sale_account_lines),len(lines_balance))
        forbalance,amountinzip(sorted(sale_account_lines.mapped('balance')),sorted(lines_balance)):
            self.assertAlmostEqual(balance,amount)

        other_sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_sale_account)
        lines_balance=[-474.75,-272.59]
        self.assertEqual(len(other_sale_account_lines),len(lines_balance))
        forbalance,amountinzip(sorted(other_sale_account_lines.mapped('balance')),sorted(lines_balance)):
            self.assertAlmostEqual(balance,amount)

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,885.45)

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,154.9)

        manually_calculated_taxes=[-36.35,-10.85]
        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)
        self.assertAlmostEqual(len(manually_calculated_taxes),len(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        self.assertTrue(receivable_line_cash.full_reconcile_id)

    deftest_03_invoiced_fpos(self):
        """Invoice2orders.

        Orders
        ======
        +---------+----------+---------------------+----------+-----+---------+-----------------+--------+
        |order  |payments|invoiced?          |product |qty|untaxed|tax            | total|
        +---------+----------+---------------------+----------+-----+---------+-----------------+--------+
        |order1|bank    |yes,customer      |product1| 10| 109.90|18.68[7%->17%]|128.58|
        |        |         |                    |product2| 10| 181.73|18.17[10%]    |199.90|
        |        |         |                    |product3| 10| 309.90|52.68[7%->17%]|362.58|
        +---------+----------+---------------------+----------+-----+---------+-----------------+--------+
        |order2|cash    |no,customer       |product1|  5|  54.95|9.34[7%->17%] | 64.29|
        |        |         |                    |product2|  5|  90.86|9.09[10%]     | 99.95|
        +---------+----------+---------------------+----------+-----+---------+-----------------+--------+
        |order3|cash    |yes,other_customer|product2|  5|  90.86|9.09[10%]     | 99.95|
        |        |         |                    |product3|  5| 154.95|10.85[7%]     |165.80|
        +---------+----------+---------------------+----------+-----+---------+-----------------+--------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |other_sale_account | -54.95| (forthe17%baseamount)
        |other_sale_account | -90.86| (forthe10%baseamount)
        |tax10%            |  -9.09|
        |tax17%            |  -9.34|
        |posreceivablecash| 429.99|
        |posreceivablebank| 691.06|
        |receivable         |-691.06|
        |otherreceivable   |-265.75|
        +---------------------+---------+
        |Totalbalance      |    0.0|
        +---------------------+---------+
        """

        self.customer.write({'property_account_position_id':self.fpos.id})
        self.open_new_session()
        #createorders
        orders=[]
        uid1=self.create_random_uid()
        orders.append(self.create_ui_order_data(
            [(self.product1,10),(self.product2,10),(self.product3,10)],
            customer=self.customer,
            payments=[(self.bank_pm,691.06)],
            is_invoiced=True,
            uid=uid1
        ))
        orders.append(self.create_ui_order_data(
            [(self.product1,5),(self.product2,5)],
            customer=self.customer,
        ))
        uid2=self.create_random_uid()
        orders.append(self.create_ui_order_data(
            [(self.product2,5),(self.product3,5)],
            customer=self.other_customer,
            is_invoiced=True,
            uid=uid2,
        ))
        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')

        invoiced_order_1=self.pos_session.order_ids.filtered(lambdaorder:uid1inorder.pos_reference)
        invoiced_order_2=self.pos_session.order_ids.filtered(lambdaorder:uid2inorder.pos_reference)

        self.assertTrue(invoiced_order_1,msg='Invoicedorder1shouldexist.')
        self.assertTrue(invoiced_order_2,msg='Invoicedorder2shouldexist.')
        self.assertTrue(invoiced_order_1.account_move,msg='Invoicedorder1shouldhaveinvoice(account_move).')
        self.assertTrue(invoiced_order_2.account_move,msg='Invoicedorder2shouldhaveinvoice(account_move).')

        #NOTETestsofvaluesintheinvoiceaccountinglinesisnotdonehere.

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        session_move=self.pos_session.move_id

        sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertFalse(sale_account_lines,msg='Thereshouldbenoself.sale_accountlines.')

        other_sale_account_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_sale_account)
        lines_balance=[-54.95,-90.86]
        self.assertEqual(len(other_sale_account_lines),len(lines_balance))
        forbalance,amountinzip(sorted(other_sale_account_lines.mapped('balance')),sorted(lines_balance)):
            self.assertAlmostEqual(balance,amount)

        receivable_line_bank=session_move.line_ids.filtered(lambdaline:self.bank_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_bank.balance,691.06)

        receivable_line_cash=session_move.line_ids.filtered(lambdaline:self.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,429.99)

        manually_calculated_taxes=[-9.09,-9.34]
        tax_lines=session_move.line_ids.filtered(lambdaline:line.account_id==self.tax_received_account)
        self.assertAlmostEqual(len(manually_calculated_taxes),len(tax_lines.mapped('balance')))
        fort1,t2inzip(sorted(manually_calculated_taxes),sorted(tax_lines.mapped('balance'))):
            self.assertAlmostEqual(t1,t2,msg='Taxesshouldbecorrectlycombined.')

        receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertAlmostEqual(receivable_line.balance,-691.06,msg='Thatisnotthecorrectreceivablelinebalance.')

        other_receivable_line=session_move.line_ids.filtered(lambdaline:line.account_id==self.other_receivable_account)
        self.assertAlmostEqual(other_receivable_line.balance,-265.75,msg='Thatisnotthecorrectotherreceivablelinebalance.')

        self.assertTrue(receivable_line_cash.full_reconcile_id)
        self.assertTrue(receivable_line.full_reconcile_id)
        self.assertTrue(other_receivable_line.full_reconcile_id)
