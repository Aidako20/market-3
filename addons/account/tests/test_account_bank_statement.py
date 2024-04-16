#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportForm
fromflectra.exceptionsimportValidationError,UserError
fromflectraimportfields

fromunittest.mockimportpatch


classTestAccountBankStatementCommon(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #Weneedathirdcurrencyasyoucouldhaveacompany'scurrency!=journal'scurrency!=
        cls.currency_data_2=cls.setup_multi_currency_data(default_values={
            'name':'DarkChocolateCoin',
            'symbol':'🍫',
            'currency_unit_label':'DarkChoco',
            'currency_subunit_label':'DarkCacaoPowder',
        },rate2016=6.0,rate2017=4.0)
        cls.currency_data_3=cls.setup_multi_currency_data(default_values={
            'name':'BlackChocolateCoin',
            'symbol':'🍫',
            'currency_unit_label':'BlackChoco',
            'currency_subunit_label':'BlackCacaoPowder',
        },rate2016=12.0,rate2017=8.0)

        cls.bank_journal_1=cls.company_data['default_journal_bank']
        cls.bank_journal_2=cls.bank_journal_1.copy()
        cls.bank_journal_3=cls.bank_journal_2.copy()
        cls.currency_1=cls.company_data['currency']
        cls.currency_2=cls.currency_data['currency']
        cls.currency_3=cls.currency_data_2['currency']
        cls.currency_4=cls.currency_data_3['currency']

    defassertBankStatementLine(self,statement_line,expected_statement_line_vals,expected_move_line_vals):
        self.assertRecordValues(statement_line,[expected_statement_line_vals])
        self.assertRecordValues(statement_line.line_ids.sorted('balance'),expected_move_line_vals)


@tagged('post_install','-at_install')
classTestAccountBankStatement(TestAccountBankStatementCommon):

    #-------------------------------------------------------------------------
    #TESTSaboutthestatementmodel.
    #-------------------------------------------------------------------------

    deftest_starting_ending_balance_chaining(self):
        #Createfirststatementon2019-01-02.
        bnk1=self.env['account.bank.statement'].create({
            'name':'BNK1',
            'date':'2019-01-02',
            'journal_id':self.company_data['default_journal_bank'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':100.0})],
        })
        self.assertRecordValues(bnk1,[{
            'balance_start':0.0,
            'balance_end_real':100.0,
            'balance_end':100.0,
            'previous_statement_id':False,
        }])

        #Createanewstatementafterthatone.
        bnk2=self.env['account.bank.statement'].create({
            'name':'BNK2',
            'date':'2019-01-10',
            'journal_id':self.company_data['default_journal_bank'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':50.0})],
        })
        self.assertRecordValues(bnk2,[{
            'balance_start':100.0,
            'balance_end_real':150.0,
            'balance_end':150.0,
            'previous_statement_id':bnk1.id,
        }])

        #Createnewstatementwithgivenendingbalance.
        bnk3=self.env['account.bank.statement'].create({
            'name':'BNK3',
            'date':'2019-01-15',
            'journal_id':self.company_data['default_journal_bank'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':25.0})],
            'balance_end_real':200.0,
        })
        self.assertRecordValues(bnk3,[{
            'balance_start':150.0,
            'balance_end_real':200.0,
            'balance_end':175.0,
            'previous_statement_id':bnk2.id,
        }])

        #CreatenewstatementwithadaterightafterBNK1.
        bnk4=self.env['account.bank.statement'].create({
            'name':'BNK4',
            'date':'2019-01-03',
            'journal_id':self.company_data['default_journal_bank'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':100.0})],
        })
        self.assertRecordValues(bnk4,[{
            'balance_start':100.0,
            'balance_end_real':200.0,
            'balance_end':200.0,
            'previous_statement_id':bnk1.id,
        }])

        #BNK2/BNK3shouldhavechangedtheirpreviousstatements.
        self.assertRecordValues(bnk2,[{
            'balance_start':200.0,
            'balance_end_real':250.0,
            'balance_end':250.0,
            'previous_statement_id':bnk4.id,
        }])
        self.assertRecordValues(bnk3,[{
            'balance_start':250.0,
            'balance_end_real':200.0,
            'balance_end':275.0,
            'previous_statement_id':bnk2.id,
        }])

        #CorrecttheendingbalanceofBNK3.
        bnk3.balance_end_real=275

        #ChangedateofBNK4tobethelast.
        bnk4.date='2019-01-20'
        self.assertRecordValues(bnk1,[{
            'balance_start':0.0,
            'balance_end_real':100.0,
            'balance_end':100.0,
            'previous_statement_id':False,
        }])
        self.assertRecordValues(bnk2,[{
            'balance_start':100.0,
            'balance_end_real':150.0,
            'balance_end':150.0,
            'previous_statement_id':bnk1.id,
        }])
        self.assertRecordValues(bnk3,[{
            'balance_start':150.0,
            'balance_end_real':175.0,
            'balance_end':175.0,
            'previous_statement_id':bnk2.id,
        }])
        self.assertRecordValues(bnk4,[{
            'balance_start':175.0,
            'balance_end_real':200.0,
            'balance_end':275.0,
            'previous_statement_id':bnk3.id,
        }])

        #CorrecttheendingbalanceofBNK4.
        bnk4.balance_end_real=275

        #MoveBNK3tofirstposition.
        bnk3.date='2019-01-01'
        self.assertRecordValues(bnk3,[{
            'balance_start':0.0,
            'balance_end_real':25.0,
            'balance_end':25.0,
            'previous_statement_id':False,
        }])
        self.assertRecordValues(bnk1,[{
            'balance_start':25.0,
            'balance_end_real':125.0,
            'balance_end':125.0,
            'previous_statement_id':bnk3.id,
        }])
        self.assertRecordValues(bnk2,[{
            'balance_start':125.0,
            'balance_end_real':175.0,
            'balance_end':175.0,
            'previous_statement_id':bnk1.id,
        }])
        self.assertRecordValues(bnk4,[{
            'balance_start':175.0,
            'balance_end_real':275.0,
            'balance_end':275.0,
            'previous_statement_id':bnk2.id,
        }])

        #MoveBNK1tothethirdposition.
        bnk1.date='2019-01-11'
        self.assertRecordValues(bnk3,[{
            'balance_start':0.0,
            'balance_end_real':25.0,
            'balance_end':25.0,
            'previous_statement_id':False,
        }])
        self.assertRecordValues(bnk2,[{
            'balance_start':25.0,
            'balance_end_real':75.0,
            'balance_end':75.0,
            'previous_statement_id':bnk3.id,
        }])
        self.assertRecordValues(bnk1,[{
            'balance_start':75.0,
            'balance_end_real':175.0,
            'balance_end':175.0,
            'previous_statement_id':bnk2.id,
        }])
        self.assertRecordValues(bnk4,[{
            'balance_start':175.0,
            'balance_end_real':275.0,
            'balance_end':275.0,
            'previous_statement_id':bnk1.id,
        }])

        #DeleteBNK3andBNK1.
        (bnk3+bnk1).unlink()
        self.assertRecordValues(bnk2,[{
            'balance_start':0.0,
            'balance_end_real':50.0,
            'balance_end':50.0,
            'previous_statement_id':False,
        }])
        self.assertRecordValues(bnk4,[{
            'balance_start':50.0,
            'balance_end_real':275.0,
            'balance_end':150.0,
            'previous_statement_id':bnk2.id,
        }])

    deftest_statements_different_journal(self):
        #Createstatementsinbankjournal.
        bnk1_1=self.env['account.bank.statement'].create({
            'name':'BNK1_1',
            'date':'2019-01-01',
            'journal_id':self.company_data['default_journal_bank'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':100.0})],
            'balance_end_real':100.0,
        })
        bnk1_2=self.env['account.bank.statement'].create({
            'name':'BNK1_2',
            'date':'2019-01-10',
            'journal_id':self.company_data['default_journal_bank'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':50.0})],
        })

        #Createstatementsincashjournal.
        bnk2_1=self.env['account.bank.statement'].create({
            'name':'BNK2_1',
            'date':'2019-01-02',
            'journal_id':self.company_data['default_journal_cash'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':20.0})],
            'balance_end_real':20.0,
        })
        bnk2_2=self.env['account.bank.statement'].create({
            'name':'BNK2_2',
            'date':'2019-01-12',
            'journal_id':self.company_data['default_journal_cash'].id,
            'line_ids':[(0,0,{'payment_ref':'/','amount':10.0})],
        })
        self.assertRecordValues(bnk1_1,[{
            'balance_start':0.0,
            'balance_end_real':100.0,
            'balance_end':100.0,
            'previous_statement_id':False,
        }])
        self.assertRecordValues(bnk1_2,[{
            'balance_start':100.0,
            'balance_end_real':150.0,
            'balance_end':150.0,
            'previous_statement_id':bnk1_1.id,
        }])
        self.assertRecordValues(bnk2_1,[{
            'balance_start':0.0,
            'balance_end_real':20.0,
            'balance_end':20.0,
            'previous_statement_id':False,
        }])
        self.assertRecordValues(bnk2_2,[{
            'balance_start':20.0,
            'balance_end_real':0.0,
            'balance_end':30.0,
            'previous_statement_id':bnk2_1.id,
        }])

    deftest_cash_statement_with_difference(self):
        '''Acashstatementalwayscreatesanadditionallinetostorethecashdifferencetowardstheendingbalance.
        '''
        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.company_data['default_journal_cash'].id,
            'balance_end_real':100.0,
        })

        statement.button_post()

        self.assertRecordValues(statement.line_ids,[{
            'amount':100.0,
            'is_reconciled':True,
        }])

    deftest_bank_statement_with_difference(self):
        """Testthatabankstatementwithdifferencecouldbepostedbutnotvalidated."""
        bank_statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_1.id,
            'balance_start':10.0,
            'balance_end_real':100.0,
            'balance_end':10.0,
            'line_ids':[(0,0,{
                'date':fields.Date.to_date('2019-01-01'),
                'payment_ref':'transaction_abc',
                'amount':10,
                'partner_id':self.partner_a.id,
            })]
        })
        bank_statement.button_post()
        #Checkifthebankstatementiswellposted(Nocheckonthebalanceasthebalancecouldbeeditedafter).
        self.assertEqual(bank_statement.state,'posted')

        #Checkthatthebankstatementcouldn'tbevalidatedwithbalance_end!=balance_end_real
        withself.assertRaises(UserError):
            bank_statement.button_validate()

        #Checkifwecanvalidatethebankstatementifbalance_end==balance_end_real
        bank_statement.balance_end_real=bank_statement.balance_end
        forlineinbank_statement.line_ids:
            line.reconcile([{
                'name':line.payment_ref,
                'partner_id':line.partner_id.id,
                'currency_id':self.currency_1.id,
                'account_id':bank_statement.journal_id.suspense_account_id.id,
                'debit':10.0,
                'credit':0.0,
                'amount_currency':10.0,
            }])
        bank_statement.button_validate()
        self.assertEqual(bank_statement.state,'confirm')

@tagged('post_install','-at_install')
classTestAccountBankStatementLine(TestAccountBankStatementCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.statement=cls.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':cls.bank_journal_1.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':cls.partner_a.id,
                    'foreign_currency_id':cls.currency_2.id,
                    'amount':1250.0,
                    'amount_currency':2500.0,
                }),
            ],
        })
        cls.statement_line=cls.statement.line_ids

        cls.expected_st_line={
            'date':fields.Date.from_string('2019-01-01'),
            'journal_id':cls.statement.journal_id.id,
            'payment_ref':'line_1',
            'partner_id':cls.partner_a.id,
            'currency_id':cls.currency_1.id,
            'foreign_currency_id':cls.currency_2.id,
            'amount':1250.0,
            'amount_currency':2500.0,
            'is_reconciled':False,
        }

        cls.expected_bank_line={
            'name':cls.statement_line.payment_ref,
            'partner_id':cls.statement_line.partner_id.id,
            'currency_id':cls.currency_1.id,
            'account_id':cls.statement.journal_id.default_account_id.id,
            'debit':1250.0,
            'credit':0.0,
            'amount_currency':1250.0,
        }

        cls.expected_counterpart_line={
            'name':cls.statement_line.payment_ref,
            'partner_id':cls.statement_line.partner_id.id,
            'currency_id':cls.currency_2.id,
            'account_id':cls.statement.journal_id.suspense_account_id.id,
            'debit':0.0,
            'credit':1250.0,
            'amount_currency':-2500.0,
        }

    #-------------------------------------------------------------------------
    #TESTSaboutthestatementlinemodel.
    #-------------------------------------------------------------------------

    def_test_statement_line_edition(
            self,
            journal,
            amount,amount_currency,
            journal_currency,foreign_currency,
            expected_liquidity_values,expected_counterpart_values):
        '''Testtheeditionofastatementlinefromitselforfromitslinkedjournalentry.
        :paramjournal:                    Theaccount.journalrecordthatwillbesetonthestatementline.
        :paramamount:                     Theamountinjournal'scurrency.
        :paramamount_currency:            Theamountintheforeigncurrency.
        :paramjournal_currency:           Thejournal'scurrencyasares.currencyrecord.
        :paramforeign_currency:           Theforeigncurrencyasares.currencyrecord.
        :paramexpected_liquidity_values:  Theexpectedaccount.move.linevaluesfortheliquidityline.
        :paramexpected_counterpart_values:Theexpectedaccount.move.linevaluesforthecounterpartline.
        '''
        ifjournal_currency:
            journal.currency_id=journal_currency.id

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':journal.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':foreign_currencyandforeign_currency.id,
                    'amount':amount,
                    'amount_currency':amount_currency,
                }),
            ],
        })
        statement_line=statement.line_ids

        #====Testthestatementlineamountsarecorrect====
        #Ifthereisabuginthecompute/inversemethods,theamount/amount_currencycouldbe
        #incorrectdirectlyafterthecreationofthestatementline.

        self.assertRecordValues(statement_line,[{
            'amount':amount,
            'amount_currency':amount_currency,
        }])
        self.assertRecordValues(statement_line.move_id,[{
            'partner_id':self.partner_a.id,
            'currency_id':(statement_line.foreign_currency_idorstatement_line.currency_id).id,
        }])

        #====Testtheeditionofstatementlineamounts====
        #Thestatementlinemustremainconsistentwithitsaccount.move.
        #Totestthecompute/inversemethodsarecorrectlymanagingallcurrencysetup,
        #wechecktheeditionofamountsinbothdirectionsstatementline<->journalentry.

        #Checkinitialstateofthestatementline.
        liquidity_lines,suspense_lines,other_lines=statement_line._seek_for_lines()
        self.assertRecordValues(liquidity_lines,[expected_liquidity_values])
        self.assertRecordValues(suspense_lines,[expected_counterpart_values])

        #Checktheaccount.moveisstillcorrectaftereditingtheaccount.bank.statement.line.
        statement_line.write({
            'amount':statement_line.amount*2,
            'amount_currency':statement_line.amount_currency*2,
        })
        self.assertRecordValues(statement_line,[{
            'amount':amount*2,
            'amount_currency':amount_currency*2,
        }])
        self.assertRecordValues(liquidity_lines,[{
            **expected_liquidity_values,
            'debit':expected_liquidity_values.get('debit',0.0)*2,
            'credit':expected_liquidity_values.get('credit',0.0)*2,
            'amount_currency':expected_liquidity_values.get('amount_currency',0.0)*2,
        }])
        self.assertRecordValues(suspense_lines,[{
            'debit':expected_counterpart_values.get('debit',0.0)*2,
            'credit':expected_counterpart_values.get('credit',0.0)*2,
            'amount_currency':expected_counterpart_values.get('amount_currency',0.0)*2,
        }])

        #Checktheaccount.bank.statement.lineisstillcorrectaftereditingtheaccount.move.
        statement_line.move_id.write({'line_ids':[
            (1,liquidity_lines.id,{
                'debit':expected_liquidity_values.get('debit',0.0),
                'credit':expected_liquidity_values.get('credit',0.0),
                'amount_currency':expected_liquidity_values.get('amount_currency',0.0),
            }),
            (1,suspense_lines.id,{
                'debit':expected_counterpart_values.get('debit',0.0),
                'credit':expected_counterpart_values.get('credit',0.0),
                'amount_currency':expected_counterpart_values.get('amount_currency',0.0),
            }),
        ]})
        self.assertRecordValues(statement_line,[{
            'amount':amount,
            'amount_currency':amount_currency,
        }])

    def_test_edition_customer_and_supplier_flows(
            self,
            amount,amount_currency,
            journal_currency,foreign_currency,
            expected_liquidity_values,expected_counterpart_values):
        '''Test'_test_statement_line_edition'usingthecustomer(positiveamounts)
        &thesupplierflow(negativeamounts).
        :paramamount:                     Theamountinjournal'scurrency.
        :paramamount_currency:            Theamountintheforeigncurrency.
        :paramjournal_currency:           Thejournal'scurrencyasares.currencyrecord.
        :paramforeign_currency:           Theforeigncurrencyasares.currencyrecord.
        :paramexpected_liquidity_values:  Theexpectedaccount.move.linevaluesfortheliquidityline.
        :paramexpected_counterpart_values:Theexpectedaccount.move.linevaluesforthecounterpartline.
        '''

        #Checkthefullprocesswithpositiveamount(customerprocess).
        self._test_statement_line_edition(
            self.bank_journal_2,
            amount,amount_currency,
            journal_currency,foreign_currency,
            expected_liquidity_values,
            expected_counterpart_values,
        )

        #Checkthefullprocesswithnegativeamount(supplierprocess).
        self._test_statement_line_edition(
            self.bank_journal_3,
            -amount,-amount_currency,
            journal_currency,foreign_currency,
            {
                **expected_liquidity_values,
                'debit':expected_liquidity_values.get('credit',0.0),
                'credit':expected_liquidity_values.get('debit',0.0),
                'amount_currency':-expected_liquidity_values.get('amount_currency',0.0),
            },
            {
                **expected_counterpart_values,
                'debit':expected_counterpart_values.get('credit',0.0),
                'credit':expected_counterpart_values.get('debit',0.0),
                'amount_currency':-expected_counterpart_values.get('amount_currency',0.0),
            },
        )

    deftest_edition_journal_curr_2_statement_curr_3(self):
        self._test_edition_customer_and_supplier_flows(
            80.0,              120.0,
            self.currency_2,   self.currency_3,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-120.0,     'currency_id':self.currency_3.id},
        )

    deftest_edition_journal_curr_2_statement_curr_1(self):
        self._test_edition_customer_and_supplier_flows(
            120.0,             80.0,
            self.currency_2,   self.currency_1,
            {'debit':80.0,    'credit':0.0,     'amount_currency':120.0,      'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-80.0,      'currency_id':self.currency_1.id},
        )

    deftest_edition_journal_curr_1_statement_curr_2(self):
        self._test_edition_customer_and_supplier_flows(
            80.0,              120.0,
            self.currency_1,   self.currency_2,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-120.0,     'currency_id':self.currency_2.id},
        )

    deftest_edition_journal_curr_2_statement_false(self):
        self._test_edition_customer_and_supplier_flows(
            80.0,              0.0,
            self.currency_2,   False,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-80.0,      'currency_id':self.currency_2.id},
        )

    deftest_edition_journal_curr_1_statement_false(self):
        self._test_edition_customer_and_supplier_flows(
            80.0,              0.0,
            self.currency_1,   False,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-80.0,      'currency_id':self.currency_1.id},
        )

    deftest_zero_amount_journal_curr_1_statement_curr_2(self):
        self.bank_journal_2.currency_id=self.currency_1

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_2.id,
                    'amount':0.0,
                    'amount_currency':10.0,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids.move_id.line_ids,[
            {'debit':0.0,     'credit':0.0,     'amount_currency':0.0,        'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':0.0,     'amount_currency':-10.0,      'currency_id':self.currency_2.id},
        ])

    deftest_zero_amount_currency_journal_curr_1_statement_curr_2(self):
        self.bank_journal_2.currency_id=self.currency_1

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_2.id,
                    'amount':10.0,
                    'amount_currency':0.0,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids.move_id.line_ids,[
            {'debit':10.0,    'credit':0.0,     'amount_currency':10.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':10.0,    'amount_currency':0.0,        'currency_id':self.currency_2.id},
        ])

    deftest_zero_amount_journal_curr_2_statement_curr_1(self):
        self.bank_journal_2.currency_id=self.currency_2

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_1.id,
                    'amount':0.0,
                    'amount_currency':10.0,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids.move_id.line_ids,[
            {'debit':10.0,    'credit':0.0,     'amount_currency':0.0,        'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':10.0,    'amount_currency':-10.0,      'currency_id':self.currency_1.id},
        ])

    deftest_zero_amount_currency_journal_curr_2_statement_curr_1(self):
        self.bank_journal_2.currency_id=self.currency_2

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_1.id,
                    'amount':10.0,
                    'amount_currency':0.0,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids.move_id.line_ids,[
            {'debit':0.0,     'credit':0.0,     'amount_currency':10.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':0.0,     'amount_currency':0.0,        'currency_id':self.currency_1.id},
        ])

    deftest_zero_amount_journal_curr_2_statement_curr_3(self):
        self.bank_journal_2.currency_id=self.currency_2

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_3.id,
                    'amount':0.0,
                    'amount_currency':10.0,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids.move_id.line_ids,[
            {'debit':0.0,     'credit':0.0,     'amount_currency':0.0,        'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':0.0,     'amount_currency':-10.0,      'currency_id':self.currency_3.id},
        ])

    deftest_zero_amount_currency_journal_curr_2_statement_curr_3(self):
        self.bank_journal_2.currency_id=self.currency_2

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_3.id,
                    'amount':10.0,
                    'amount_currency':0.0,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids.move_id.line_ids,[
            {'debit':5.0,     'credit':0.0,     'amount_currency':10.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':5.0,     'amount_currency':0.0,        'currency_id':self.currency_3.id},
        ])

    deftest_constraints(self):
        defassertStatementLineConstraint(statement_vals,statement_line_vals):
            withself.assertRaises(Exception),self.cr.savepoint():
                self.env['account.bank.statement'].create({
                    **statement_vals,
                    'line_ids':[(0,0,statement_line_vals)],
                })

        statement_vals={
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_2.id,
        }
        statement_line_vals={
            'date':'2019-01-01',
            'payment_ref':'line_1',
            'partner_id':self.partner_a.id,
            'foreign_currency_id':False,
            'amount':10.0,
            'amount_currency':0.0,
        }

        #====Testconstraintsatcreation====

        #Can'thaveastandaloneamountinforeigncurrencywithoutforeigncurrencyset.
        assertStatementLineConstraint(statement_vals,{
            **statement_line_vals,
            'amount_currency':10.0,
        })

        #====Testconstraintsatedition====

        statement=self.env['account.bank.statement'].create({
            **statement_vals,
            'line_ids':[(0,0,statement_line_vals)],
        })
        st_line=statement.line_ids

        #Youcan'tmessedupthejournalentrybyaddinganotherliquidityline.
        addition_lines_to_create=[
            {
                'debit':1.0,
                'credit':0,
                'account_id':self.bank_journal_2.default_account_id.id,
                'move_id':st_line.move_id.id,
            },
            {
                'debit':0,
                'credit':1.0,
                'account_id':self.company_data['default_account_revenue'].id,
                'move_id':st_line.move_id.id,
            },
        ]
        withself.assertRaises(UserError),self.cr.savepoint():
            st_line.move_id.write({
                'line_ids':[(0,0,vals)forvalsinaddition_lines_to_create]
            })

        withself.assertRaises(UserError),self.cr.savepoint():
            st_line.line_ids.create(addition_lines_to_create)

        #Youcan'tsetthejournalentryinanunconsistentstate.
        withself.assertRaises(UserError),self.cr.savepoint():
            st_line.move_id.action_post()

    deftest_statement_line_move_onchange_1(self):
        '''Testtheconsistencybetweentheaccount.bank.statement.lineandthegeneratedaccount.move.lines
        usingtheformviewemulator.
        '''

        #Checktheinitialstateofthestatementline.
        self.assertBankStatementLine(self.statement_line,self.expected_st_line,[self.expected_counterpart_line,self.expected_bank_line])

        #Inversetheamount+changethem.
        withForm(self.statement)asstatement_form:
            withstatement_form.line_ids.edit(0)asst_line_form:
                st_line_form.amount=-2000.0
                st_line_form.amount_currency=-4000.0
                st_line_form.foreign_currency_id=self.currency_3

        self.assertBankStatementLine(self.statement_line,{
            **self.expected_st_line,
            'amount':-2000.0,
            'amount_currency':-4000.0,
            'foreign_currency_id':self.currency_3.id,
        },[
            {
                **self.expected_bank_line,
                'debit':0.0,
                'credit':2000.0,
                'amount_currency':-2000.0,
                'currency_id':self.currency_1.id,
            },
            {
                **self.expected_counterpart_line,
                'debit':2000.0,
                'credit':0.0,
                'amount_currency':4000.0,
                'currency_id':self.currency_3.id,
            },
        ])

        #Checkchangingthelabelandthepartner.
        withForm(self.statement)asstatement_form:
            withstatement_form.line_ids.edit(0)asst_line_form:
                st_line_form.payment_ref='line_1(bis)'
                st_line_form.partner_id=self.partner_b

        self.assertBankStatementLine(self.statement_line,{
            **self.expected_st_line,
            'payment_ref':self.statement_line.payment_ref,
            'partner_id':self.statement_line.partner_id.id,
            'amount':-2000.0,
            'amount_currency':-4000.0,
            'foreign_currency_id':self.currency_3.id,
        },[
            {
                **self.expected_bank_line,
                'name':self.statement_line.payment_ref,
                'partner_id':self.statement_line.partner_id.id,
                'debit':0.0,
                'credit':2000.0,
                'amount_currency':-2000.0,
                'currency_id':self.currency_1.id,
            },
            {
                **self.expected_counterpart_line,
                'name':self.statement_line.payment_ref,
                'partner_id':self.statement_line.partner_id.id,
                'debit':2000.0,
                'credit':0.0,
                'amount_currency':4000.0,
                'currency_id':self.currency_3.id,
            },
        ])

    #-------------------------------------------------------------------------
    #TESTSaboutreconciliation:
    #-Test'_prepare_counterpart_move_line_vals':onetestforeachcase.
    #-Test'reconcile':3cases:
    #      -Open-balanceindebit.
    #      -Open-balanceincredit.
    #      -Noopen-balance.
    #-Test'button_undo_reconciliation'.
    #-------------------------------------------------------------------------

    def_test_statement_line_reconciliation(
            self,
            journal,
            amount,amount_currency,counterpart_amount,
            journal_currency,foreign_currency,counterpart_currency,
            expected_liquidity_values,expected_counterpart_values):
        '''Testthereconciliationofastatementline.
        :paramjournal:                    Theaccount.journalrecordthatwillbesetonthestatementline.
        :paramamount:                     Theamountinjournal'scurrency.
        :paramamount_currency:            Theamountintheforeigncurrency.
        :paramcounterpart_amount:         Theamountoftheinvoicetoreconcile.
        :paramjournal_currency:           Thejournal'scurrencyasares.currencyrecord.
        :paramforeign_currency:           Theforeigncurrencyasares.currencyrecord.
        :paramcounterpart_currency:       Theinvoicecurrencyasares.currencyrecord.
        :paramexpected_liquidity_values:  Theexpectedaccount.move.linevaluesfortheliquidityline.
        :paramexpected_counterpart_values:Theexpectedaccount.move.linevaluesforthecounterpartline.
        '''
        ifjournal_currency:
            journal.currency_id=journal_currency.id

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':journal.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':foreign_currencyandforeign_currency.id,
                    'amount':amount,
                    'amount_currency':amount_currency,
                }),
            ],
        })
        statement_line=statement.line_ids

        #-Thereis3flowstocheck:
        #  *Theinvoicewillfullyreconcilethestatementline.
        #  *Theinvoicewillpartiallyreconcilethestatementlineandleadstoanopenbalanceindebit.
        #  *Theinvoicewillpartiallyreconcilethestatementlineandleadstoanopenbalanceincredit.
        #-Thedatesaredifferenttobesurethereconciliationwillpreservetheconversionratebankside.
        move_type='out_invoice'ifcounterpart_amount<0.0else'in_invoice'

        test_invoices=self.env['account.move'].create([
            {
                'move_type':move_type,
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'date':fields.Date.from_string('2016-01-01'),
                'partner_id':self.partner_a.id,
                'currency_id':counterpart_currency.id,
                'invoice_line_ids':[
                    (0,None,{
                        'name':'counterpartline,sameamount',
                        'account_id':self.company_data['default_account_revenue'].id,
                        'quantity':1,
                        'price_unit':abs(counterpart_amount),
                    }),
                ],
            },
            {
                'move_type':move_type,
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'date':fields.Date.from_string('2016-01-01'),
                'partner_id':self.partner_a.id,
                'currency_id':counterpart_currency.id,
                'invoice_line_ids':[
                    (0,None,{
                        'name':'counterpartline,loweramount',
                        'account_id':self.company_data['default_account_revenue'].id,
                        'quantity':1,
                        'price_unit':abs(counterpart_amount/2),
                    }),
                ],
            },
            {
                'move_type':move_type,
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'date':fields.Date.from_string('2016-01-01'),
                'partner_id':self.partner_a.id,
                'currency_id':counterpart_currency.id,
                'invoice_line_ids':[
                    (0,None,{
                        'name':'counterpartline,biggeramount',
                        'account_id':self.company_data['default_account_revenue'].id,
                        'quantity':1,
                        'price_unit':abs(counterpart_amount*2),
                    }),
                ],
            },
        ])
        test_invoices.action_post()
        statement.button_post()
        counterpart_lines=test_invoices.mapped('line_ids').filtered(lambdaline:line.account_internal_typein('receivable','payable'))

        #Checkthefullreconciliation.
        statement_line.reconcile([{'id':counterpart_lines[0].id}])
        liquidity_lines,suspense_lines,other_lines=statement_line._seek_for_lines()
        self.assertRecordValues(liquidity_lines,[expected_liquidity_values])
        self.assertRecordValues(other_lines,[expected_counterpart_values])

        #Checkthereconciliationwithpartialloweramount.
        statement_line.button_undo_reconciliation()
        statement_line.reconcile([{'id':counterpart_lines[1].id}])
        liquidity_lines,suspense_lines,other_lines=statement_line._seek_for_lines()
        self.assertRecordValues(liquidity_lines,[expected_liquidity_values])
        self.assertRecordValues(other_lines.sorted('balance',reverse=amount<0.0),[
            {
                **expected_counterpart_values,
                'debit':expected_counterpart_values.get('debit',0.0)/2,
                'credit':expected_counterpart_values.get('credit',0.0)/2,
                'amount_currency':expected_counterpart_values.get('amount_currency',0.0)/2,
            },
            {
                'debit':expected_counterpart_values.get('debit',0.0)/2,
                'credit':expected_counterpart_values.get('credit',0.0)/2,
                'amount_currency':expected_counterpart_values.get('amount_currency',0.0)/2,
                'currency_id':expected_counterpart_values.get('currency_id'),
            },
        ])

        #Checkthereconciliationwithpartialhigheramount.
        statement_line.button_undo_reconciliation()
        statement_line.reconcile([{'id':counterpart_lines[2].id}])
        liquidity_lines,suspense_lines,other_lines=statement_line._seek_for_lines()
        self.assertRecordValues(liquidity_lines,[expected_liquidity_values])
        self.assertRecordValues(other_lines.sorted('balance',reverse=amount<0.0),[
            {
                **expected_counterpart_values,
                'debit':expected_counterpart_values.get('debit',0.0)*2,
                'credit':expected_counterpart_values.get('credit',0.0)*2,
                'amount_currency':expected_counterpart_values.get('amount_currency',0.0)*2,
            },
            {
                'debit':expected_counterpart_values.get('credit',0.0),
                'credit':expected_counterpart_values.get('debit',0.0),
                'amount_currency':-expected_counterpart_values.get('amount_currency',0.0),
                'currency_id':expected_counterpart_values.get('currency_id'),
            },
        ])

        #Makesurethestatementlineisstillcorrect.
        self.assertRecordValues(statement_line,[{
            'amount':amount,
            'amount_currency':amount_currency,
        }])

    def_test_reconciliation_customer_and_supplier_flows(
            self,
            amount,amount_currency,counterpart_amount,
            journal_currency,foreign_currency,counterpart_currency,
            expected_liquidity_values,expected_counterpart_values):
        '''Test'_test_statement_line_reconciliation'usingthecustomer(positiveamounts)
        &thesupplierflow(negativeamounts).
        :paramamount:                     Theamountinjournal'scurrency.
        :paramamount_currency:            Theamountintheforeigncurrency.
        :paramcounterpart_amount:         Theamountoftheinvoicetoreconcile.
        :paramjournal_currency:           Thejournal'scurrencyasares.currencyrecord.
        :paramforeign_currency:           Theforeigncurrencyasares.currencyrecord.
        :paramcounterpart_currency:       Theinvoicecurrencyasares.currencyrecord.
        :paramexpected_liquidity_values:  Theexpectedaccount.move.linevaluesfortheliquidityline.
        :paramexpected_counterpart_values:Theexpectedaccount.move.linevaluesforthecounterpartline.
        '''

        #Checkthefullprocesswithpositiveamount(customerprocess).
        self._test_statement_line_reconciliation(
            self.bank_journal_2,
            amount,amount_currency,counterpart_amount,
            journal_currency,foreign_currency,counterpart_currency,
            expected_liquidity_values,
            expected_counterpart_values,
        )

        #Checkthefullprocesswithnegativeamount(supplierprocess).
        self._test_statement_line_reconciliation(
            self.bank_journal_3,
            -amount,-amount_currency,-counterpart_amount,
            journal_currency,foreign_currency,counterpart_currency,
            {
                **expected_liquidity_values,
                'debit':expected_liquidity_values.get('credit',0.0),
                'credit':expected_liquidity_values.get('debit',0.0),
                'amount_currency':-expected_liquidity_values.get('amount_currency',0.0),
            },
            {
                **expected_counterpart_values,
                'debit':expected_counterpart_values.get('credit',0.0),
                'credit':expected_counterpart_values.get('debit',0.0),
                'amount_currency':-expected_counterpart_values.get('amount_currency',0.0),
            },
        )

    deftest_reconciliation_journal_curr_2_statement_curr_3_counterpart_curr_3(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -120.0,
            self.currency_2,   self.currency_3,   self.currency_3,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-120.0,     'currency_id':self.currency_3.id},
        )

    deftest_reconciliation_journal_curr_2_statement_curr_1_counterpart_curr_2(self):
        self._test_reconciliation_customer_and_supplier_flows(
            120.0,             80.0,              -120.0,
            self.currency_2,   self.currency_1,   self.currency_2,
            {'debit':80.0,    'credit':0.0,     'amount_currency':120.0,      'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-80.0,      'currency_id':self.currency_1.id},
        )

    deftest_reconciliation_journal_curr_2_statement_curr_3_counterpart_curr_2(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -80.0,
            self.currency_2,   self.currency_3,   self.currency_2,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-120.0,     'currency_id':self.currency_3.id},
        )

    deftest_reconciliation_journal_curr_2_statement_curr_3_counterpart_curr_4(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -480.0,
            self.currency_2,   self.currency_3,   self.currency_4,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-120.0,     'currency_id':self.currency_3.id},
        )

    deftest_reconciliation_journal_curr_1_statement_curr_2_counterpart_curr_2(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -120.0,
            self.currency_1,   self.currency_2,   self.currency_2,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-120.0,     'currency_id':self.currency_2.id},
        )

    deftest_reconciliation_journal_curr_1_statement_curr_2_counterpart_curr_3(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -480.0,
            self.currency_1,   self.currency_2,   self.currency_3,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-120.0,     'currency_id':self.currency_2.id},
        )

    deftest_reconciliation_journal_curr_2_statement_false_counterpart_curr_2(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              0.0,               -80.0,
            self.currency_2,   False,             self.currency_2,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-80.0,      'currency_id':self.currency_2.id},
        )

    deftest_reconciliation_journal_curr_2_statement_false_counterpart_curr_3(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              0.0,               -240.0,
            self.currency_2,   False,             self.currency_3,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-80.0,      'currency_id':self.currency_2.id},
        )

    deftest_reconciliation_journal_curr_1_statement_false_counterpart_curr_3(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              0.0,               -480.0,
            self.currency_1,   False,             self.currency_3,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-80.0,      'currency_id':self.currency_1.id},
        )

    deftest_reconciliation_journal_curr_2_statement_curr_1_counterpart_curr_1(self):
        self._test_reconciliation_customer_and_supplier_flows(
            120.0,             80.0,              -80.0,
            self.currency_2,   self.currency_1,   self.currency_1,
            {'debit':80.0,    'credit':0.0,     'amount_currency':120.0,      'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-80.0,      'currency_id':self.currency_1.id},
        )

    deftest_reconciliation_journal_curr_2_statement_curr_3_counterpart_curr_1(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -40.0,
            self.currency_2,   self.currency_3,   self.currency_1,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-120.0,     'currency_id':self.currency_3.id},
        )

    deftest_reconciliation_journal_curr_1_statement_curr_2_counterpart_curr_1(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              120.0,             -80.0,
            self.currency_1,   self.currency_2,   self.currency_1,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-120.0,     'currency_id':self.currency_2.id},
        )

    deftest_reconciliation_journal_curr_2_statement_false_counterpart_curr_1(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              0.0,               -40.0,
            self.currency_2,   False,             self.currency_1,
            {'debit':40.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_2.id},
            {'debit':0.0,     'credit':40.0,    'amount_currency':-80.0,      'currency_id':self.currency_2.id},
        )

    deftest_reconciliation_journal_curr_1_statement_false_counterpart_curr_1(self):
        self._test_reconciliation_customer_and_supplier_flows(
            80.0,              0.0,               -80.0,
            self.currency_1,   False,             self.currency_1,
            {'debit':80.0,    'credit':0.0,     'amount_currency':80.0,       'currency_id':self.currency_1.id},
            {'debit':0.0,     'credit':80.0,    'amount_currency':-80.0,      'currency_id':self.currency_1.id},
        )

    deftest_reconciliation_move_draft(self):
        '''Ensuresthattheaccountmoveofareconciledstatementcannotbesettodraft
        '''
        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_1.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'amount':100.0,
                }),
            ],
        })

        statement.button_post()
        statement.line_ids[0].reconcile([{'name':'test','account_id':self.company_data['default_account_revenue'].id,'balance':-100}])

        statement.button_validate_or_action()
        account_move=statement.line_ids.move_id

        withself.assertRaises(UserError):
            account_move.button_draft()

    deftest_reconciliation_statement_line_state(self):
        '''Testthereconciliationonthebankstatementlinewithaforeigncurrencyonthejournal:
        -Ensurethestatementlineis_reconciledfieldiswellcomputed.
        -Ensurethereconciliationisworkingwellwhendealingwithaforeigncurrencyatdifferentdates.
        -Ensurethereconciliationcanbeundo.
        -Ensurethereconciliationisstillpossiblewithto_check.
        '''
        self.statement.button_post()

        receivable_acc_1=self.company_data['default_account_receivable']
        receivable_acc_2=self.copy_account(self.company_data['default_account_receivable'])
        payment_account=self.bank_journal_1.payment_debit_account_id
        random_acc_1=self.company_data['default_account_revenue']
        random_acc_2=self.copy_account(self.company_data['default_account_revenue'])
        test_move=self.env['account.move'].create({
            'move_type':'entry',
            'date':fields.Date.from_string('2016-01-01'),
            'line_ids':[
                (0,None,{
                    'name':'counterpartofthewholemove',
                    'account_id':random_acc_1.id,
                    'debit':0.0,
                    'credit':1030.0,
                }),
                (0,None,{
                    'name':'testline1-receivableaccount',
                    'account_id':receivable_acc_1.id,
                    'currency_id':self.currency_2.id,
                    'debit':500.0,
                    'credit':0.0,
                    'amount_currency':1500.0,
                }),
                (0,None,{
                    'name':'testline2-anotherreceivableaccount',
                    'account_id':receivable_acc_2.id,
                    'currency_id':self.currency_2.id,
                    'debit':500.0,
                    'credit':0.0,
                    'amount_currency':1500.0,
                }),
                (0,None,{
                    'name':'testline3-paymenttransferaccount',
                    'account_id':payment_account.id,
                    'currency_id':self.currency_2.id,
                    'debit':30.0,
                    'credit':0.0,
                    'amount_currency':90.0,
                }),
            ]
        })
        test_move.action_post()

        test_line_1=test_move.line_ids.filtered(lambdaline:line.account_id==receivable_acc_1)
        test_line_2=test_move.line_ids.filtered(lambdaline:line.account_id==receivable_acc_2)
        test_line_3=test_move.line_ids.filtered(lambdaline:line.account_id==payment_account)
        self.statement_line.reconcile([
            #testline1
            #Willreconcile300.0inbalance,600.0inamount_currency.
            {'id':test_line_1.id,'balance':-600.0},
            #testline2
            #Willreconcile250.0inbalance,500.0inamount_currency.
            {'id':test_line_2.id,'balance':-500.0},
            #testline3
            #Willreconcile30.0inbalance,90.0inamount_currency.
            {'id':test_line_3.id},
            #testline4
            #Willreconcile50.0inbalance,100.0inamount_currency.
            {'name':'whatever','account_id':random_acc_1.id,'balance':-100.0},
        ])

        self.assertBankStatementLine(self.statement_line,{
                **self.expected_st_line,
                'is_reconciled':True,
            },[
            {
                'name':'%s:OpenBalance'%self.statement_line.payment_ref,
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':receivable_acc_1.id, #Thisaccountisretrievedonthepartner.
                'debit':0.0,
                'credit':605.0,
                'amount_currency':-1210.0,
                'amount_residual':-605.0,
                'amount_residual_currency':-1210.0,
            },
            {
                'name':test_line_1.name,
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':receivable_acc_1.id,
                'debit':0.0,
                'credit':300.0,
                'amount_currency':-600.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                'name':test_line_2.name,
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':receivable_acc_2.id,
                'debit':0.0,
                'credit':250.0,
                'amount_currency':-500.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                'name':'whatever',
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':random_acc_1.id,
                'debit':0.0,
                'credit':50.0,
                'amount_currency':-100.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                'name':test_line_3.name,
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':test_line_3.account_id.id,
                'debit':0.0,
                'credit':45.0,
                'amount_currency':-90.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                **self.expected_bank_line,
                'amount_residual':1250.0,
                'amount_residual_currency':1250.0,
            },
        ])

        #Undothereconciliationtoreturntotheinitialstate.
        self.statement_line.button_undo_reconciliation()
        self.assertBankStatementLine(self.statement_line,self.expected_st_line,[self.expected_counterpart_line,self.expected_bank_line])

        #Modifythecounterpartlinewithto_checkenabled.
        self.statement_line.reconcile([
            {'name':'whatever','account_id':random_acc_1.id,'balance':-100.0},
        ],to_check=True)

        self.assertBankStatementLine(self.statement_line,{
                **self.expected_st_line,
                'is_reconciled':True,
            },[
            {
                'name':'%s:OpenBalance'%self.statement_line.payment_ref,
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':receivable_acc_1.id, #Thisaccountisretrievedonthepartner.
                'debit':0.0,
                'credit':1200.0,
                'amount_currency':-2400.0,
                'amount_residual':-1200.0,
                'amount_residual_currency':-2400.0,
            },
            {
                'name':'whatever',
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':random_acc_1.id,
                'debit':0.0,
                'credit':50.0,
                'amount_currency':-100.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                **self.expected_bank_line,
                'amount_residual':1250.0,
                'amount_residual_currency':1250.0,
            },
        ])

        #Modifythecounterpartline.Shouldbeallowedbytheto_checkenabled.
        self.statement_line.reconcile([
            {'name':'whateveragain','account_id':random_acc_2.id,'balance':-500.0},
        ])

        self.assertBankStatementLine(self.statement_line,{
                **self.expected_st_line,
                'is_reconciled':True,
            },[
            {
                'name':'%s:OpenBalance'%self.statement_line.payment_ref,
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':receivable_acc_1.id, #Thisaccountisretrievedonthepartner.
                'debit':0.0,
                'credit':1000.0,
                'amount_currency':-2000.0,
                'amount_residual':-1000.0,
                'amount_residual_currency':-2000.0,
            },
            {
                'name':'whateveragain',
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':random_acc_2.id,
                'debit':0.0,
                'credit':250.0,
                'amount_currency':-500.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                **self.expected_bank_line,
                'amount_residual':1250.0,
                'amount_residual_currency':1250.0,
            },
        ])

        #Thestatementlineisnolongerinthe'to_check'mode.
        #Reconcilingagainshouldraiseanerror.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.statement_line.reconcile([
                {'name':'whatever','account_id':random_acc_1.id,'balance':-100.0},
            ])

    deftest_reconciliation_statement_line_foreign_currency(self):
        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_1.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'foreign_currency_id':self.currency_2.id,
                    'amount':-80.0,
                    'amount_currency':-120.0,
                }),
            ],
        })
        statement.button_post()
        statement_line=statement.line_ids

        invoice=self.env['account.move'].create({
            'move_type':'in_invoice',
            'invoice_date':'2019-01-01',
            'date':'2019-01-01',
            'partner_id':self.partner_a.id,
            'currency_id':self.currency_2.id,
            'invoice_line_ids':[
                (0,None,{
                    'name':'counterpartline,sameamount',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'quantity':1,
                    'price_unit':120.0,
                }),
            ],
        })
        invoice.action_post()
        invoice_line=invoice.line_ids.filtered(lambdaline:line.account_internal_type=='payable')

        statement_line.reconcile([{'id':invoice_line.id}])

        self.assertRecordValues(statement_line.line_ids,[
            #pylint:disable=bad-whitespace
            {'amount_currency':-80.0,'currency_id':self.currency_1.id,  'balance':-80.0,  'reconciled':False},
            {'amount_currency':120.0,'currency_id':self.currency_2.id,  'balance':80.0,   'reconciled':True},
        ])

    deftest_reconciliation_statement_line_with_generated_payments(self):
        self.statement.button_post()

        receivable_account=self.company_data['default_account_receivable']
        payment_account=self.bank_journal_1.payment_debit_account_id
        random_account=self.company_data['default_account_revenue']
        test_move=self.env['account.move'].create({
            'move_type':'entry',
            'date':fields.Date.from_string('2016-01-01'),
            'line_ids':[
                (0,None,{
                    'name':'counterpartofthewholemove',
                    'account_id':random_account.id,
                    'debit':0.0,
                    'credit':1000.0,
                }),
                (0,None,{
                    'name':'testline1',
                    'account_id':receivable_account.id,
                    'debit':100.0,
                    'credit':0.0,
                }),
                (0,None,{
                    'name':'testline2',
                    'account_id':receivable_account.id,
                    'currency_id':self.currency_2.id,
                    'debit':900.0,
                    'credit':0.0,
                    'amount_currency':1500.0,
                }),
            ]
        })
        test_move.action_post()

        test_line_1=test_move.line_ids.filtered(lambdaline:line.name=='testline1')
        test_line_2=test_move.line_ids.filtered(lambdaline:line.name=='testline2')

        statement_line=self.statement_line
        StatementLine_prepare_reconciliation=type(statement_line)._prepare_reconciliation

        def_prepare_reconciliation(self,lines_vals_list,create_payment_for_invoice=False):
            ifself==statement_line:
                create_payment_for_invoice=True
            returnStatementLine_prepare_reconciliation(self,lines_vals_list,create_payment_for_invoice)

        withpatch.object(type(statement_line),'_prepare_reconciliation',_prepare_reconciliation):
            self.statement_line.reconcile([
                {'id':test_line_1.id,'balance':-50.0},
                {'id':test_line_2.id},
            ])

        self.assertBankStatementLine(self.statement_line,{
                **self.expected_st_line,
                'is_reconciled':True,
            },[
            {
                'name':'testline2',
                'account_id':payment_account.id,
                'currency_id':self.currency_2.id,
                'debit':0.0,
                'credit':750.0,
                'amount_currency':-1500.0,
            },
            {
                'name':'line_1:OpenBalance',
                'account_id':receivable_account.id,
                'currency_id':self.currency_2.id,
                'debit':0.0,
                'credit':450.0,
                'amount_currency':-900.0,
            },
            {
                'name':'testline1',
                'account_id':payment_account.id,
                'currency_id':self.currency_2.id,
                'debit':0.0,
                'credit':50.0,
                'amount_currency':-100.0,
            },
            self.expected_bank_line,
        ])

        #Checkgeneratedpayments.
        self.assertRecordValues(test_line_1.matched_credit_ids.credit_move_id.payment_id.line_ids.sorted('balance'),[
            {
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':test_line_1.account_id.id,
                'debit':0.0,
                'credit':50.0,
                'amount_currency':-100.0,
                'amount_residual':0.0,
                'amount_residual_currency':50.0,
            },
            {
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':payment_account.id,
                'debit':50.0,
                'credit':0.0,
                'amount_currency':100.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
        ])
        self.assertRecordValues(test_line_2.matched_credit_ids.credit_move_id.payment_id.line_ids.sorted('balance'),[
            {
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':test_line_2.account_id.id,
                'debit':0.0,
                'credit':750.0,
                'amount_currency':-1500.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
            {
                'partner_id':self.statement_line.partner_id.id,
                'currency_id':self.currency_2.id,
                'account_id':payment_account.id,
                'debit':750.0,
                'credit':0.0,
                'amount_currency':1500.0,
                'amount_residual':0.0,
                'amount_residual_currency':0.0,
            },
        ])

    deftest_conversion_rate_rounding_issue(self):
        '''Ensurethereconciliationiswellhandlingtheroundingissueduetomultiplecurrencyconversionrates.

        Inthistest,theresultingjournalentryafterreconciliationis:
        {'amount_currency':7541.66,   'debit':6446.97,  'credit':0.0}
        {'amount_currency':226.04,    'debit':193.22,   'credit':0.0}
        {'amount_currency':-7767.70,  'debit':0.0,      'credit':6640.19}
        ...but226.04/1.1698=193.23.Inthissituation,0.01hasbeenremovedfromthiswrite-offlineinorderto
        avoidanunecessaryopen-balancelinebeinganexchangedifferenceissue.
        '''
        self.bank_journal_2.currency_id=self.currency_2
        self.currency_data['rates'][-1].rate=1.1698

        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2017-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':'line_1',
                    'partner_id':self.partner_a.id,
                    'amount':7541.66,
                }),
            ],
        })
        statement.button_post()
        statement_line=statement.line_ids

        payment=self.env['account.payment'].create({
            'amount':7767.70,
            'date':'2019-01-01',
            'currency_id':self.currency_2.id,
            'payment_type':'inbound',
            'partner_type':'customer',
        })
        payment.action_post()
        liquidity_lines,counterpart_lines,writeoff_lines=payment._seek_for_lines()
        self.assertRecordValues(liquidity_lines,[{'amount_currency':7767.70}])

        statement_line.reconcile([
            {'id':liquidity_lines.id},
            {'balance':226.04,'account_id':self.company_data['default_account_revenue'].id,'name':"write-off"},
        ])

        self.assertRecordValues(statement_line.line_ids,[
            {'amount_currency':7541.66,   'debit':6446.97,  'credit':0.0},
            {'amount_currency':226.04,    'debit':193.22,   'credit':0.0},
            {'amount_currency':-7767.70,  'debit':0.0,      'credit':6640.19},
        ])

    deftest_zero_amount_statement_line(self):
        '''Ensurethestatementlineisdirectlymarkedasreconciledwhenhavinganamountofzero.'''
        self.company_data['company'].account_journal_suspense_account_id.reconcile=False

        statement=self.env['account.bank.statement'].with_context(skip_check_amounts_currencies=True).create({
            'name':'test_statement',
            'date':'2017-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':"Happynewyear",
                    'amount':0.0,
                }),
            ],
        })
        statement_line=statement.line_ids

        self.assertRecordValues(statement_line,[{'is_reconciled':True,'amount_residual':0.0}])

    deftest_bank_statement_line_analytic(self):
        '''Ensuretheanalyticlinesaregeneratedduringthereconciliation.'''
        analytic_account=self.env['account.analytic.account'].create({'name':'analytic_account'})

        statement=self.env['account.bank.statement'].with_context(skip_check_amounts_currencies=True).create({
            'name':'test_statement',
            'date':'2017-01-01',
            'journal_id':self.bank_journal_2.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':"line",
                    'amount':100.0,
                }),
            ],
        })
        statement_line=statement.line_ids

        statement_line.reconcile([{
            'balance':-100.0,
            'account_id':self.company_data['default_account_revenue'].id,
            'name':"write-off",
            'analytic_account_id':analytic_account.id,
        }])

        #Checktheanalyticaccountisthere.
        self.assertRecordValues(statement_line.line_ids.sorted('balance'),[
            {'balance':-100.0,'analytic_account_id':analytic_account.id},
            {'balance':100.0, 'analytic_account_id':False},
        ])

        #Checktheanalyticlines.
        self.assertRecordValues(statement_line.line_ids.analytic_line_ids,[
            {'amount':100.0,'account_id':analytic_account.id},
        ])

    deftest_reconciliation_line_with_no_partner(self):
        """
        Ensurethatentrylinesandstatementlinehavenopartnerwhenreconciling
        lineswithoutpartnerwithotherswithpartner
        """
        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_1.id,
            'line_ids':[
                (0,0,{
                    'date':'2022-01-01',
                    'payment_ref':"Happynewyear",
                    'amount':200.0,
                }),
            ],
        })
        statement.button_post()

        partner=self.env['res.partner'].create({'name':'test'})

        receivable_account=self.company_data['default_account_receivable']
        outstanding_account=self.company_data['default_journal_bank']['payment_debit_account_id']

        payments=self.env['account.payment'].create([
            {
                'name':'Paymentwithoutpartner',
                'date':fields.Date.from_string('2022-01-01'),
                'is_internal_transfer':False,
                'amount':100.0,
                'payment_type':'inbound',
                'partner_type':'customer',
                'destination_account_id':receivable_account.id,
                'journal_id':self.bank_journal_1.id,
            },
            {
                'name':'Paymentwithpartner',
                'date':fields.Date.from_string('2022-01-01'),
                'is_internal_transfer':False,
                'amount':100.0,
                'payment_type':'inbound',
                'partner_type':'customer',
                'partner_id':partner.id,
                'destination_account_id':receivable_account.id,
                'journal_id':self.bank_journal_1.id,
            },
        ])
        payments.action_post()

        statement_line=statement.line_ids

        statement_line.reconcile([
            {'id':payments[0].move_id.line_ids.filtered(lambdaline:line.account_id==outstanding_account).id},
            {'id':payments[1].move_id.line_ids.filtered(lambdaline:line.account_id==outstanding_account).id},
        ])

        self.assertRecordValues(
            statement.line_ids.move_id.line_ids,
            [
                {
                    'debit':200.0,
                    'credit':0.0,
                    'partner_id':False,
                    'account_id':self.bank_journal_1.default_account_id.id
                },
                {
                    'debit':0.0,
                    'credit':100.0,
                    'partner_id':False,
                    'account_id':outstanding_account.id
                },
                {
                    'debit':0.0,
                    'credit':100.0,
                    'partner_id':partner.id,
                    'account_id':outstanding_account.id
                },
            ])

        self.assertRecordValues(statement.line_ids,[{
            'partner_id':False,
        }])

    deftest_create_statement_line_with_inconsistent_currencies(self):
        statement=self.env['account.bank.statement'].create({
            'name':'test_statement',
            'date':'2019-01-01',
            'journal_id':self.bank_journal_1.id,
            'line_ids':[
                (0,0,{
                    'date':'2019-01-01',
                    'payment_ref':"Happynewyear",
                    'amount':200.0,
                    'amount_currency':200.0,
                    'foreign_currency_id':self.env.company.currency_id.id,
                }),
            ],
        })

        self.assertRecordValues(statement.line_ids,[{
            'currency_id':self.env.company.currency_id.id,
            'foreign_currency_id':False,
            'amount':200.0,
            'amount_currency':0.0,
        }])
