#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
importflectra
fromflectra.addons.point_of_sale.tests.commonimportTestPoSCommon

@flectra.tests.tagged('post_install','-at_install')
classTestPoSStock(TestPoSCommon):
    """Testsforanglosaxonaccountingscenario.
    """
    defsetUp(self):
        super(TestPoSStock,self).setUp()

        self.config=self.basic_config
        self.product1=self.create_product('Product1',self.categ_anglo,10.0,5.0)
        self.product2=self.create_product('Product2',self.categ_anglo,20.0,10.0)
        self.product3=self.create_product('Product3',self.categ_basic,30.0,15.0)
        #startinventorywith10itemsforeachproduct
        self.adjust_inventory([self.product1,self.product2,self.product3],[10,10,10])

        #changecost(standard_price)ofangloproducts
        #thensetinventoryfrom10->15
        self.product1.write({'standard_price':6.0})
        self.product2.write({'standard_price':6.0})
        self.adjust_inventory([self.product1,self.product2,self.product3],[15,15,15])

        #changecost(standard_price)ofangloproducts
        #thensetinventoryfrom15->25
        self.product1.write({'standard_price':13.0})
        self.product2.write({'standard_price':13.0})
        self.adjust_inventory([self.product1,self.product2,self.product3],[25,25,25])

        self.output_account=self.categ_anglo.property_stock_account_output_categ_id
        self.expense_account=self.categ_anglo.property_account_expense_categ_id
        self.valuation_account=self.categ_anglo.property_stock_valuation_account_id

    deftest_01_orders_no_invoiced(self):
        """

        Orders
        ======
        +---------+----------+-----+-------------+------------+
        |order  |product |qty|totalprice|totalcost|
        +---------+----------+-----+-------------+------------+
        |order1|product1| 10|      100.0|      50.0| ->10itemsatcostof5.0isconsumed,remains5itemsat6.0and10itemsat13.0
        |        |product2| 10|      200.0|     100.0| ->10itemsatcostof10.0isconsumed,remains5itemsat6.0and10itemsat13.0
        +---------+----------+-----+-------------+------------+
        |order2|product2|  7|      140.0|      56.0| ->5itemsatcostof6.0and2itemsatcostof13.0,remains8itemsatcostof13.0
        |        |product3|  7|      210.0|       0.0|
        +---------+----------+-----+-------------+------------+
        |order3|product1|  6|       60.0|      43.0| ->5itemsatcostof6.0and1itematcostof13.0,remains9itemsatcostof13.0
        |        |product2|  6|      120.0|      78.0| ->6itemsatcostof13.0,remains2itemsatcostof13.0
        |        |product3|  6|      180.0|       0.0|
        +---------+----------+-----+-------------+------------+

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       |-1010.0|
        |pos_receivable-cash| 1010.0|
        |expense_account    |  327.0|
        |output_account     | -327.0|
        +---------------------+---------+
        |Totalbalance      |   0.00|
        +---------------------+---------+
        """
        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product1,10),(self.product2,10)]))
        orders.append(self.create_ui_order_data([(self.product2,7),(self.product3,7)]))
        orders.append(self.create_ui_order_data([(self.product1,6),(self.product2,6),(self.product3,6)]))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')
        self.assertAlmostEqual(orders_total,1010.0,msg='Theorders\'stotalamountshouldequalthecomputed.')

        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(self.product1.qty_available,9)
        self.assertEqual(self.product2.qty_available,2)
        self.assertEqual(self.product3.qty_available,12)

        #pickingandstockmovesshouldbeindonestate
        fororderinself.pos_session.order_ids:
            self.assertEqual(order.picking_ids[0].state,'done','Pickingshouldbeindonestate.')
            self.assertTrue(all(state=='done'forstateinorder.picking_ids[0].move_lines.mapped('state')),'MoveLinesshouldbeindonestate.')

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        account_move=self.pos_session.move_id

        sales_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sales_line.balance,-orders_total,msg='Saleslinebalanceshouldbeequaltototalordersamount.')

        receivable_line_cash=account_move.line_ids.filtered(lambdaline:line.account_idinself.pos_receivable_account+self.env['account.account'].search([('name','=','AccountReceivable(PoS)')])andself.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,1010.0,msg='Cashreceivableshouldbeequaltothetotalcashpayments.')

        expense_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.expense_account)
        self.assertAlmostEqual(expense_line.balance,327.0)

        output_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.output_account)
        self.assertAlmostEqual(output_line.balance,-327.0)

        self.assertTrue(receivable_line_cash.full_reconcile_id,msg='Cashreceivablelineshouldbefully-reconciled.')
        self.assertTrue(output_line.full_reconcile_id,msg='Thestockoutputaccountlineshouldbefully-reconciled.')

    deftest_02_orders_with_invoice(self):
        """

        Orders
        ======
        Samewithtest_01butorder3isinvoiced.

        ExpectedResult
        ===============
        +---------------------+---------+
        |account            |balance|
        +---------------------+---------+
        |sale_account       | -650.0|
        |pos_receivable-cash| 1010.0|
        |receivable         | -360.0|
        |expense_account    |  206.0|
        |output_account     | -206.0|
        +---------------------+---------+
        |Totalbalance      |   0.00|
        +---------------------+---------+
        """
        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product1,10),(self.product2,10)]))
        orders.append(self.create_ui_order_data([(self.product2,7),(self.product3,7)]))
        invoiced_uid=self.create_random_uid()
        orders.append(self.create_ui_order_data(
            [(self.product1,6),(self.product2,6),(self.product3,6)],
            is_invoiced=True,
            customer=self.customer,
            uid=invoiced_uid,
        ))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(3,self.pos_session.order_count)
        orders_total=sum(order.amount_totalfororderinself.pos_session.order_ids)
        self.assertAlmostEqual(orders_total,self.pos_session.total_payments_amount,msg='Totalorderamountshouldbeequaltothetotalpaymentamount.')
        self.assertAlmostEqual(orders_total,1010.0,msg='Theorders\'stotalamountshouldequalthecomputed.')

        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(self.product1.qty_available,9)
        self.assertEqual(self.product2.qty_available,2)
        self.assertEqual(self.product3.qty_available,12)

        #pickingandstockmovesshouldbeindonestate
        fororderinself.pos_session.order_ids:
            self.assertEqual(order.picking_ids[0].state,'done','Pickingshouldbeindonestate.')
            self.assertTrue(all(state=='done'forstateinorder.picking_ids[0].move_lines.mapped('state')),'MoveLinesshouldbeindonestate.')

        #closethesession
        self.pos_session.action_pos_session_validate()

        #checkvaluesafterthesessionisclosed
        account_move=self.pos_session.move_id

        sales_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.sale_account)
        self.assertAlmostEqual(sales_line.balance,-650.0)

        receivable_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.receivable_account)
        self.assertAlmostEqual(receivable_line.balance,-360.0,msg='Receivablelinebalanceshouldequalthenegativeoftotalamountofinvoicedorders.')

        receivable_line_cash=account_move.line_ids.filtered(lambdaline:line.account_idinself.pos_receivable_account+self.env['account.account'].search([('name','=','AccountReceivable(PoS)')])andself.cash_pm.nameinline.name)
        self.assertAlmostEqual(receivable_line_cash.balance,1010.0,msg='Cashreceivableshouldbeequaltothetotalcashpayments.')

        expense_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.expense_account)
        self.assertAlmostEqual(expense_line.balance,206.0)

        output_line=account_move.line_ids.filtered(lambdaline:line.account_id==self.output_account)
        self.assertAlmostEqual(output_line.balance,-206.0)

        #checkorderjournalentry
        invoiced_order=self.pos_session.order_ids.filtered(lambdaorder:invoiced_uidinorder.pos_reference)
        invoiced_output_account_lines=invoiced_order.account_move.line_ids.filtered(lambdaline:line.account_id==self.output_account)
        self.assertAlmostEqual(sum(invoiced_output_account_lines.mapped('balance')),-121.0)

        #Thestockoutputaccountmovelinesoftheinvoicedordershouldbeproperlyreconciled
        formove_lineininvoiced_order.account_move.line_ids.filtered(lambdaline:line.account_id==self.output_account):
            self.assertTrue(move_line.full_reconcile_id)

        self.assertTrue(receivable_line_cash.full_reconcile_id,msg='Cashreceivablelineshouldbefully-reconciled.')
        self.assertTrue(output_line.full_reconcile_id,msg='Thestockoutputaccountlineshouldbefully-reconciled.')

    deftest_03_order_product_w_owner(self):
        """
        TestorderviaPOSaproducthavingstockowner.
        """

        group_owner=self.env.ref('stock.group_tracking_owner')
        self.env.user.write({'groups_id':[(4,group_owner.id)]})
        self.product4=self.create_product('Product3',self.categ_basic,30.0,15.0)
        inventory=self.env['stock.inventory'].create({
            'name':'Inventoryadjustment'
        })
        self.env['stock.inventory.line'].create({
            'product_id':self.product4.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'inventory_id':inventory.id,
            'product_qty':10,
            'partner_id':self.partner_a.id,
            'location_id':self.stock_location_components.id,
        })
        inventory._action_start()
        inventory.action_validate()

        self.open_new_session()

        #createorders
        orders=[]
        orders.append(self.create_ui_order_data([(self.product4,1)]))

        #syncorders
        order=self.env['pos.order'].create_from_ui(orders)

        #checkvaluesbeforeclosingthesession
        self.assertEqual(1,self.pos_session.order_count)

        #checkproductqty_availableaftersyncingtheorder
        self.assertEqual(self.product4.qty_available,9)

        #pickingandstockmovesshouldbeindonestate
        fororderinself.pos_session.order_ids:
            self.assertEqual(order.picking_ids[0].state,'done','Pickingshouldbeindonestate.')
            self.assertTrue(all(state=='done'forstateinorder.picking_ids[0].move_lines.mapped('state')),'MoveLinesshouldbeindonestate.')
            self.assertTrue(self.partner_a==order.picking_ids[0].move_lines[0].move_line_ids[0].owner_id,'MoveLinesOwnershouldbetakenintoaccount.')

        #closethesession
        self.pos_session.action_pos_session_validate()

    deftest_04_order_refund(self):
        self.categ4=self.env['product.category'].create({
            'name':'Category4',
            'property_cost_method':'fifo',
            'property_valuation':'real_time',
        })
        self.product4=self.create_product('Product4',self.categ4,30.0,15.0)

        self.open_new_session()
        orders=[]
        orders.append(self.create_ui_order_data([(self.product4,1)]))
        order=self.env['pos.order'].create_from_ui(orders)

        refund_action=self.env['pos.order'].browse(order[0]['id']).refund()
        refund=self.env['pos.order'].browse(refund_action['res_id'])

        payment_context={"active_ids":refund.ids,"active_id":refund.id}
        refund_payment=self.env['pos.make.payment'].with_context(**payment_context).create({
            'amount':refund.amount_total,
            'payment_method_id':self.cash_pm.id,
        })
        refund_payment.with_context(**payment_context).check()

        self.pos_session.action_pos_session_validate()
        expense_account_move_line=self.env['account.move.line'].search([('account_id','=',self.expense_account.id)])
        self.assertEqual(expense_account_move_line.balance,0.0,"Expenseaccountshouldbe0.0")
