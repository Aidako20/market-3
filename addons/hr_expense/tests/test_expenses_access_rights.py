#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.hr_expense.tests.commonimportTestExpenseCommon
fromflectra.exceptionsimportAccessError,UserError
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestExpensesAccessRights(TestExpenseCommon):

    deftest_expense_access_rights(self):
        '''Theexpenseemployeecan'tbeabletocreateanexpenseforsomeoneelse.'''

        expense_employee_2=self.env['hr.employee'].create({
            'name':'expense_employee_2',
            'user_id':self.env.user.id,
            'address_home_id':self.env.user.partner_id.id,
            'address_id':self.env.user.partner_id.id,
        })

        withself.assertRaises(AccessError):
            self.env['hr.expense'].with_user(self.expense_user_employee).create({
                'name':"Superboycostumewashing",
                'employee_id':expense_employee_2.id,
                'product_id':self.product_a.id,
                'quantity':1,
                'unit_amount':1,
            })

    deftest_expense_sheet_access_rights_approve(self):

        #Theexpenseemployeeisabletoacreateanexpensesheet.

        expense_sheet=self.env['hr.expense.sheet'].with_user(self.expense_user_employee).create({
            'name':'FirstExpenseforemployee',
            'employee_id':self.expense_employee.id,
            'journal_id':self.company_data['default_journal_purchase'].id,
            'accounting_date':'2017-01-01',
            'expense_line_ids':[
                (0,0,{
                    #Expensewithoutforeigncurrencybutanalyticaccount.
                    'name':'expense_1',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':1000.0,
                    'employee_id':self.expense_employee.id,
                }),
            ],
        })
        self.assertRecordValues(expense_sheet,[{'state':'draft'}])

        #Theexpenseemployeeisabletosubmittheexpensesheet.

        expense_sheet.with_user(self.expense_user_employee).action_submit_sheet()
        self.assertRecordValues(expense_sheet,[{'state':'submit'}])

        #Theexpenseemployeeisnotabletoapproveitselftheexpensesheet.

        withself.assertRaises(UserError):
            expense_sheet.with_user(self.expense_user_employee).approve_expense_sheets()
        self.assertRecordValues(expense_sheet,[{'state':'submit'}])

        #Anexpensemanagerisrequiredforthisstep.

        expense_sheet.with_user(self.expense_user_manager).approve_expense_sheets()
        self.assertRecordValues(expense_sheet,[{'state':'approve'}])

        #Anexpensemanagerisnotabletocreatethejournalentry.

        withself.assertRaises(UserError):
            expense_sheet.with_user(self.expense_user_manager).action_sheet_move_create()
        self.assertRecordValues(expense_sheet,[{'state':'approve'}])

        #Anexpensemanagerhavingaccountingaccessrightsisabletocreatethejournalentry.

        expense_sheet.with_user(self.env.user).action_sheet_move_create()
        self.assertRecordValues(expense_sheet,[{'state':'post'}])

    deftest_expense_sheet_access_rights_refuse(self):

        #Theexpenseemployeeisabletoacreateanexpensesheet.

        expense_sheet=self.env['hr.expense.sheet'].with_user(self.expense_user_employee).create({
            'name':'FirstExpenseforemployee',
            'employee_id':self.expense_employee.id,
            'journal_id':self.company_data['default_journal_purchase'].id,
            'accounting_date':'2017-01-01',
            'expense_line_ids':[
                (0,0,{
                    #Expensewithoutforeigncurrencybutanalyticaccount.
                    'name':'expense_1',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':1000.0,
                    'employee_id':self.expense_employee.id,
                }),
            ],
        })
        self.assertRecordValues(expense_sheet,[{'state':'draft'}])

        #Theexpenseemployeeisabletosubmittheexpensesheet.

        expense_sheet.with_user(self.expense_user_employee).action_submit_sheet()
        self.assertRecordValues(expense_sheet,[{'state':'submit'}])

        #Theexpenseemployeeisnotabletorefuseitselftheexpensesheet.

        withself.assertRaises(UserError):
            expense_sheet.with_user(self.expense_user_employee).refuse_sheet('')
        self.assertRecordValues(expense_sheet,[{'state':'submit'}])

        #Anexpensemanagerisrequiredforthisstep.

        expense_sheet.with_user(self.expense_user_manager).refuse_sheet('')
        self.assertRecordValues(expense_sheet,[{'state':'cancel'}])
