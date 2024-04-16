#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra
importtime
fromflectraimportfields
fromflectra.testsimportcommon

classTestAngloSaxonCommon(common.TransactionCase):

    defsetUp(self):
        super(TestAngloSaxonCommon,self).setUp()
        self.PosMakePayment=self.env['pos.make.payment']
        self.PosOrder=self.env['pos.order']
        self.Statement=self.env['account.bank.statement']
        self.company=self.env.ref('base.main_company')
        self.warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        self.partner=self.env['res.partner'].create({'name':'Partner1'})
        self.category=self.env.ref('product.product_category_all')
        self.category=self.category.copy({'name':'Newcategory','property_valuation':'real_time'})
        account_type_rcv=self.env.ref('account.data_account_type_receivable')
        account_type_inc=self.env.ref('account.data_account_type_revenue')
        account_type_exp=self.env.ref('account.data_account_type_expenses')
        self.account=self.env['account.account'].create({'name':'Receivable','code':'RCV00','user_type_id':account_type_rcv.id,'reconcile':True})
        account_expense=self.env['account.account'].create({'name':'Expense','code':'EXP00','user_type_id':account_type_exp.id,'reconcile':True})
        account_income=self.env['account.account'].create({'name':'Income','code':'INC00','user_type_id':account_type_inc.id,'reconcile':True})
        account_output=self.env['account.account'].create({'name':'Output','code':'OUT00','user_type_id':account_type_exp.id,'reconcile':True})
        account_valuation=self.env['account.account'].create({'name':'Valuation','code':'STV00','user_type_id':account_type_exp.id,'reconcile':True})
        self.partner.property_account_receivable_id=self.account
        self.category.property_account_income_categ_id=account_income
        self.category.property_account_expense_categ_id=account_expense
        self.category.property_stock_account_input_categ_id=self.account
        self.category.property_stock_account_output_categ_id=account_output
        self.category.property_stock_valuation_account_id=account_valuation
        self.category.property_stock_journal=self.env['account.journal'].create({'name':'Stockjournal','type':'sale','code':'STK00'})
        self.pos_config=self.env.ref('point_of_sale.pos_config_main')
        self.pos_config=self.pos_config.copy({'name':'NewPOSconfig'})
        self.product=self.env['product.product'].create({
            'name':'Newproduct',
            'standard_price':100,
            'available_in_pos':True,
            'type':'product',
        })
        self.company.anglo_saxon_accounting=True
        self.company.point_of_sale_update_stock_quantities='real'
        self.product.categ_id=self.category
        self.product.property_account_expense_id=account_expense
        self.product.property_account_income_id=account_income
        sale_journal=self.env['account.journal'].create({'name':'POSjournal','type':'sale','code':'POS00'})
        self.pos_config.journal_id=sale_journal
        self.cash_journal=self.env['account.journal'].create({'name':'CASHjournal','type':'cash','code':'CSH00'})
        self.sale_journal=self.env['account.journal'].create({'name':'SALEjournal','type':'sale','code':'INV00'})
        self.pos_config.invoice_journal_id=self.sale_journal
        self.cash_payment_method=self.env['pos.payment.method'].create({
            'name':'CashTest',
            'is_cash_count':True,
            'cash_journal_id':self.cash_journal.id,
            'receivable_account_id':self.account.id,
        })
        self.pos_config.write({'payment_method_ids':[(6,0,self.cash_payment_method.ids)]})


@flectra.tests.tagged('post_install','-at_install')
classTestAngloSaxonFlow(TestAngloSaxonCommon):

    deftest_create_account_move_line(self):
        #Thistestwillcheckthatthecorrectjournalentriesarecreatedwhenaproductinrealtimevaluation
        #issoldinacompanyusinganglo-saxon
        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id
        self.cash_journal.loss_account_id=self.account

        #IcreateaPoSorderwith1unitofNewproductat450EUR
        self.pos_order_pos0=self.PosOrder.create({
            'company_id':self.company.id,
            'partner_id':self.partner.id,
            'pricelist_id':self.company.partner_id.property_product_pricelist.id,
            'session_id':self.pos_config.current_session_id.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product.id,
                'price_unit':450,
                'discount':0.0,
                'qty':1.0,
                'price_subtotal':450,
                'price_subtotal_incl':450,
            })],
            'amount_total':450,
            'amount_tax':0,
            'amount_paid':0,
            'amount_return':0,
        })

        #Imakeapaymenttofullypaytheorder
        context_make_payment={"active_ids":[self.pos_order_pos0.id],"active_id":self.pos_order_pos0.id}
        self.pos_make_payment_0=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':450.0,
            'payment_method_id':self.cash_payment_method.id,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos0.id}
        self.pos_make_payment_0.with_context(context_payment).check()

        #Icheckthattheorderismarkedaspaid
        self.assertEqual(self.pos_order_pos0.state,'paid','Ordershouldbeinpaidstate.')
        self.assertEqual(self.pos_order_pos0.amount_paid,450,'Amountpaidfortheordershouldbeupdated.')

        #Iclosethecurrentsessiontogeneratethejournalentries
        current_session_id=self.pos_config.current_session_id
        current_session_id._check_pos_session_balance()
        current_session_id.action_pos_session_close()
        self.assertEqual(current_session_id.state,'closed','Checkthatsessionisclosed')

        #Checkifthereisaccount_moveintheorder.
        #Thereshouldn'tbebecausetheorderisnotinvoiced.
        self.assertFalse(self.pos_order_pos0.account_move,'Thereshouldbenoinvoiceintheorder.')

        #Itestthatthegeneratedjournalentriesarecorrect.
        account_output=self.category.property_stock_account_output_categ_id
        expense_account=self.category.property_account_expense_categ_id
        aml=current_session.move_id.line_ids
        aml_output=aml.filtered(lambdal:l.account_id.id==account_output.id)
        aml_expense=aml.filtered(lambdal:l.account_id.id==expense_account.id)
        self.assertEqual(aml_output.credit,self.product.standard_price,"CostofGoodSoldentrymissingormismatching")
        self.assertEqual(aml_expense.debit,self.product.standard_price,"CostofGoodSoldentrymissingormismatching")

    def_prepare_pos_order(self):
        """Setthecostmethodof`self.product`asFIFO.Receive5@5and5@1and
        createa`pos.order`recordselling7units@450.
        """
        #checkfifoCostingMethodofproduct.category
        self.product.categ_id.property_cost_method='fifo'
        self.product.standard_price=5.0
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product.id,
            'inventory_quantity':5.0,
            'location_id':self.warehouse.lot_stock_id.id,
        })
        self.product.standard_price=1.0
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product.id,
            'inventory_quantity':10.0,
            'location_id':self.warehouse.lot_stock_id.id,
        })
        self.assertEqual(self.product.value_svl,30,"Valueshouldbe(5*5+5*1)=30")
        self.assertEqual(self.product.quantity_svl,10)

        self.pos_config.module_account=True
        self.pos_config.open_session_cb(check_coa=False)

        pos_order_values={
            'company_id':self.company.id,
            'partner_id':self.partner.id,
            'pricelist_id':self.company.partner_id.property_product_pricelist.id,
            'session_id':self.pos_config.current_session_id.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product.id,
                'price_unit':450,
                'discount':0.0,
                'qty':7.0,
                'price_subtotal':7*450,
                'price_subtotal_incl':7*450,
            })],
            'amount_total':7*450,
            'amount_tax':0,
            'amount_paid':0,
            'amount_return':0,
        }

        returnself.PosOrder.create(pos_order_values)

    deftest_fifo_valuation_no_invoice(self):
        """Registerapaymentandvalidateasessionaftersellingafifo
        productwithoutmakinganinvoiceforthecustomer"""
        pos_order_pos0=self._prepare_pos_order()
        context_make_payment={"active_ids":[pos_order_pos0.id],"active_id":pos_order_pos0.id}
        self.pos_make_payment_0=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':7*450.0,
            'payment_method_id':self.cash_payment_method.id,
        })

        #registerthepayment
        context_payment={'active_id':pos_order_pos0.id}
        self.pos_make_payment_0.with_context(context_payment).check()

        #validatethesession
        current_session_id=self.pos_config.current_session_id
        current_session_id.action_pos_session_validate()

        #checktheanglosaxonmovelines
        #withuninvoicedorders,theaccount_movefieldofpos.orderisempty.
        #theaccountinglinesareinmove_idofpos.session.
        session_move=pos_order_pos0.session_id.move_id
        line=session_move.line_ids.filtered(lambdal:l.debitandl.account_id==self.category.property_account_expense_categ_id)
        self.assertEqual(session_move.journal_id,self.pos_config.journal_id)
        self.assertEqual(line.debit,27,'Asitisafifoproduct,themove\'svalueshouldbe5*5+2*1')

    deftest_fifo_valuation_with_invoice(self):
        """Registerapaymentandvalidateasessionaftersellingafifo
        productandmakeaninvoiceforthecustomer"""
        pos_order_pos0=self._prepare_pos_order()
        context_make_payment={"active_ids":[pos_order_pos0.id],"active_id":pos_order_pos0.id}
        self.pos_make_payment_0=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':7*450.0,
            'payment_method_id':self.cash_payment_method.id,
        })

        #registerthepayment
        context_payment={'active_id':pos_order_pos0.id}
        self.pos_make_payment_0.with_context(context_payment).check()

        #Createthecustomerinvoice
        pos_order_pos0.action_pos_order_invoice()

        #validatethesession
        current_session_id=self.pos_config.current_session_id
        current_session_id.action_pos_session_validate()

        #checktheanglosaxonmovelines
        line=pos_order_pos0.account_move.line_ids.filtered(lambdal:l.debitandl.account_id==self.category.property_account_expense_categ_id)
        self.assertEqual(pos_order_pos0.account_move.journal_id,self.pos_config.invoice_journal_id)
        self.assertEqual(line.debit,27,'Asitisafifoproduct,themove\'svalueshouldbe5*5+2*1')
