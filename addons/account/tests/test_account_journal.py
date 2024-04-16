#-*-coding:utf-8-*-
importflectra.tools
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectra.exceptionsimportUserError,ValidationError


@tagged('post_install','-at_install')
classTestAccountJournal(AccountTestInvoicingCommon):

    deftest_constraint_currency_consistency_with_accounts(self):
        '''Theaccountslinkedtoabank/cashjournalmustsharethesameforeigncurrency
        ifspecified.
        '''
        journal_bank=self.company_data['default_journal_bank']
        journal_bank.currency_id=self.currency_data['currency']

        #Trytosetadifferentcurrencyonthe'debit'account.
        withself.assertRaises(ValidationError),self.cr.savepoint():
            journal_bank.default_account_id.currency_id=self.company_data['currency']

    deftest_changing_journal_company(self):
        '''Ensureyoucan'tchangethecompanyofanaccount.journaliftherearesomejournalentries'''

        self.env['account.move'].create({
            'move_type':'entry',
            'date':'2019-01-01',
            'journal_id':self.company_data['default_journal_sale'].id,
        })

        withself.assertRaises(UserError),self.cr.savepoint():
            self.company_data['default_journal_sale'].company_id=self.company_data_2['company']

    deftest_account_control_create_journal_entry(self):
        move_vals={
            'line_ids':[
                (0,0,{
                    'name':'debit',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'debit':100.0,
                    'credit':0.0,
                }),
                (0,0,{
                    'name':'credit',
                    'account_id':self.company_data['default_account_expense'].id,
                    'debit':0.0,
                    'credit':100.0,
                }),
            ],
        }

        #Shouldfailbecause'default_account_expense'isnotallowed.
        self.company_data['default_journal_misc'].account_control_ids|=self.company_data['default_account_revenue']
        withself.assertRaises(UserError),self.cr.savepoint():
            self.env['account.move'].create(move_vals)

        #Shouldbeallowedbecausebothaccountsareaccepted.
        self.company_data['default_journal_misc'].account_control_ids|=self.company_data['default_account_expense']
        self.env['account.move'].create(move_vals)

    deftest_default_account_type_control_create_journal_entry(self):
        move_vals={
            'line_ids':[
                (0,0,{
                    'name':'debit',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'debit':100.0,
                    'credit':0.0,
                }),
                (0,0,{
                    'name':'credit',
                    'account_id':self.company_data['default_account_expense'].id,
                    'debit':0.0,
                    'credit':100.0,
                }),
            ],
        }

        #Setthe'default_account_id'onthejournalandmakesureitwillnotraiseanerror,
        #evenifitisnotexplicitlyincludedinthe'type_control_ids'.
        self.company_data['default_journal_misc'].default_account_id=self.company_data['default_account_expense'].id

        #Shouldfailbecause'default_account_revenue'typeisnotallowed.
        self.company_data['default_journal_misc'].type_control_ids|=self.company_data['default_account_receivable'].user_type_id
        withself.assertRaises(UserError),self.cr.savepoint():
            self.env['account.move'].create(move_vals)

        #Shouldpassbecausebothaccounttypesareallowed.
        #'default_account_revenue'explicitlyand'default_account_expense'implicitly.
        self.company_data['default_journal_misc'].type_control_ids|=self.company_data['default_account_revenue'].user_type_id
        self.env['account.move'].create(move_vals)

    deftest_account_control_existing_journal_entry(self):
        self.env['account.move'].create({
            'line_ids':[
                (0,0,{
                    'name':'debit',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'debit':100.0,
                    'credit':0.0,
                }),
                (0,0,{
                    'name':'credit',
                    'account_id':self.company_data['default_account_expense'].id,
                    'debit':0.0,
                    'credit':100.0,
                }),
            ],
        })

        #Thereisalreadyanotherlineusingthe'default_account_expense'account.
        withself.assertRaises(ValidationError),self.cr.savepoint():
            self.company_data['default_journal_misc'].account_control_ids|=self.company_data['default_account_revenue']

        #Assigningbothshouldbeallowed
        self.company_data['default_journal_misc'].account_control_ids=\
            self.company_data['default_account_revenue']+self.company_data['default_account_expense']

    @flectra.tools.mute_logger('flectra.addons.account.models.account_journal')
    deftest_account_journal_alias_name(self):
        journal=self.company_data['default_journal_misc']
        self.assertEqual(journal._get_alias_values(journal.type)['alias_name'],'MiscellaneousOperations-company_1_data')
        self.assertEqual(journal._get_alias_values(journal.type,'ぁ')['alias_name'],'MISC-company_1_data')
        journal.name='ぁ'
        self.assertEqual(journal._get_alias_values(journal.type)['alias_name'],'MISC-company_1_data')
        journal.code='ぁ'
        self.assertEqual(journal._get_alias_values(journal.type)['alias_name'],'general-company_1_data')

        self.company_data_2['company'].name='ぁ'
        company_2_id=str(self.company_data_2['company'].id)
        journal_2=self.company_data_2['default_journal_sale']
        self.assertEqual(journal_2._get_alias_values(journal_2.type)['alias_name'],'CustomerInvoices-'+company_2_id)
        journal_2.name='ぁ'
        self.assertEqual(journal_2._get_alias_values(journal_2.type)['alias_name'],'INV-'+company_2_id)
        journal_2.code='ぁ'
        self.assertEqual(journal_2._get_alias_values(journal_2.type)['alias_name'],'sale-'+company_2_id)
