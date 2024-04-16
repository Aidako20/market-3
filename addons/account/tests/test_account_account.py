#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectra.exceptionsimportUserError,ValidationError


@tagged('post_install','-at_install')
classTestAccountAccount(AccountTestInvoicingCommon):

    deftest_changing_account_company(self):
        '''Ensureyoucan'tchangethecompanyofanaccount.accountiftherearesomejournalentries'''

        self.env['account.move'].create({
            'move_type':'entry',
            'date':'2019-01-01',
            'line_ids':[
                (0,0,{
                    'name':'line_debit',
                    'account_id':self.company_data['default_account_revenue'].id,
                }),
                (0,0,{
                    'name':'line_credit',
                    'account_id':self.company_data['default_account_revenue'].id,
                }),
            ],
        })

        withself.assertRaises(UserError),self.cr.savepoint():
            self.company_data['default_account_revenue'].company_id=self.company_data_2['company']

    deftest_toggle_reconcile(self):
        '''Testthefeaturewhentheusersetsanaccountasreconcile/notreconcilewithexistingjournalentries.'''
        account=self.company_data['default_account_revenue']

        move=self.env['account.move'].create({
            'move_type':'entry',
            'date':'2019-01-01',
            'line_ids':[
                (0,0,{
                    'account_id':account.id,
                    'currency_id':self.currency_data['currency'].id,
                    'debit':100.0,
                    'credit':0.0,
                    'amount_currency':200.0,
                }),
                (0,0,{
                    'account_id':account.id,
                    'currency_id':self.currency_data['currency'].id,
                    'debit':0.0,
                    'credit':100.0,
                    'amount_currency':-200.0,
                }),
            ],
        })
        move.action_post()

        self.assertRecordValues(move.line_ids,[
            {'reconciled':False,'amount_residual':0.0,'amount_residual_currency':0.0},
            {'reconciled':False,'amount_residual':0.0,'amount_residual_currency':0.0},
        ])

        #Settheaccountasreconcileandfullyreconcilesomething.
        account.reconcile=True
        self.env['account.move.line'].invalidate_cache()

        self.assertRecordValues(move.line_ids,[
            {'reconciled':False,'amount_residual':100.0,'amount_residual_currency':200.0},
            {'reconciled':False,'amount_residual':-100.0,'amount_residual_currency':-200.0},
        ])

        move.line_ids.reconcile()
        self.assertRecordValues(move.line_ids,[
            {'reconciled':True,'amount_residual':0.0,'amount_residual_currency':0.0},
            {'reconciled':True,'amount_residual':0.0,'amount_residual_currency':0.0},
        ])

        #Setbacktoanotreconcileaccountandcheckthejournalitems.
        move.line_ids.remove_move_reconcile()
        account.reconcile=False
        self.env['account.move.line'].invalidate_cache()

        self.assertRecordValues(move.line_ids,[
            {'reconciled':False,'amount_residual':0.0,'amount_residual_currency':0.0},
            {'reconciled':False,'amount_residual':0.0,'amount_residual_currency':0.0},
        ])

    deftest_toggle_reconcile_with_partials(self):
        '''Testthefeaturewhentheusersetsanaccountasreconcile/notreconcilewithpartialreconciliation.'''
        account=self.company_data['default_account_revenue']

        move=self.env['account.move'].create({
            'move_type':'entry',
            'date':'2019-01-01',
            'line_ids':[
                (0,0,{
                    'account_id':account.id,
                    'currency_id':self.currency_data['currency'].id,
                    'debit':100.0,
                    'credit':0.0,
                    'amount_currency':200.0,
                }),
                (0,0,{
                    'account_id':account.id,
                    'currency_id':self.currency_data['currency'].id,
                    'debit':0.0,
                    'credit':50.0,
                    'amount_currency':-100.0,
                }),
                (0,0,{
                    'account_id':self.company_data['default_account_expense'].id,
                    'currency_id':self.currency_data['currency'].id,
                    'debit':0.0,
                    'credit':50.0,
                    'amount_currency':-100.0,
                }),
            ],
        })
        move.action_post()

        #Settheaccountasreconcileandpartiallyreconcilesomething.
        account.reconcile=True
        self.env['account.move.line'].invalidate_cache()

        move.line_ids.filtered(lambdaline:line.account_id==account).reconcile()

        #Trytosettheaccountasanot-reconcileone.
        withself.assertRaises(UserError),self.cr.savepoint():
            account.reconcile=False

    deftest_toggle_reconcile_outstanding_account(self):
        '''Testthefeaturewhentheusersetsanaccountasnotreconcilablewhenajournal
        isconfiguredwiththisaccountasthepaymentcreditordebitaccount.
        Sincesuchanaccountshouldbereconcilablebynature,aValidationErrorisraised.'''
        withself.assertRaises(ValidationError),self.cr.savepoint():
            self.company_data['default_journal_bank'].payment_debit_account_id.reconcile=False
        withself.assertRaises(ValidationError),self.cr.savepoint():
            self.company_data['default_journal_bank'].payment_credit_account_id.reconcile=False

    deftest_remove_account_from_account_group(self):
        """Testifanaccountiswellremovedfromaccountgroup"""
        group=self.env['account.group'].create({
            'name':'test_group',
            'code_prefix_start':401000,
            'code_prefix_end':402000,
            'company_id':self.env.company.id
        })

        account_1=self.company_data['default_account_revenue'].copy({'code':401000})
        account_2=self.company_data['default_account_revenue'].copy({'code':402000})

        self.assertRecordValues(account_1+account_2,[{'group_id':group.id}]*2)

        group.code_prefix_end=401000

        self.assertRecordValues(account_1+account_2,[{'group_id':group.id},{'group_id':False}])
