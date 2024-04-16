#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.hr_expense.tests.commonimportTestExpenseCommon
fromflectra.testsimporttagged
fromflectra.exceptionsimportUserError


@tagged('post_install','-at_install')
classTestExpenseMultiCompany(TestExpenseCommon):

    deftest_expense_sheet_multi_company_approve(self):
        self.expense_employee.company_id=self.company_data_2['company']

        #Theexpenseemployeeisabletoacreateanexpensesheetforcompany_2.

        expense_sheet=self.env['hr.expense.sheet']\
            .with_user(self.expense_user_employee)\
            .with_context(allowed_company_ids=self.company_data_2['company'].ids)\
            .create({
                'name':'FirstExpenseforemployee',
                'employee_id':self.expense_employee.id,
                'journal_id':self.company_data_2['default_journal_purchase'].id,
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
        self.assertRecordValues(expense_sheet,[{'company_id':self.company_data_2['company'].id}])

        #Theexpenseemployeeisabletosubmittheexpensesheet.

        expense_sheet.with_user(self.expense_user_employee).action_submit_sheet()

        #Anexpensemanagerisnotabletoapprovewithoutaccesstocompany_2.

        withself.assertRaises(UserError):
            expense_sheet\
                .with_user(self.expense_user_manager)\
                .with_context(allowed_company_ids=self.company_data['company'].ids)\
                .approve_expense_sheets()

        #Anexpensemanagerisabletoapprovewithaccesstocompany_2.

        expense_sheet\
            .with_user(self.expense_user_manager)\
            .with_context(allowed_company_ids=self.company_data_2['company'].ids)\
            .approve_expense_sheets()

        #Anexpensemanagerhavingaccountingaccessrightsisnotabletocreatethejournalentrywithoutaccess
        #tocompany_2.

        withself.assertRaises(UserError):
            expense_sheet\
                .with_user(self.env.user)\
                .with_context(allowed_company_ids=self.company_data['company'].ids)\
                .action_sheet_move_create()

        #Anexpensemanagerhavingaccountingaccessrightsisabletocreatethejournalentrywithaccessto
        #company_2.

        expense_sheet\
            .with_user(self.env.user)\
            .with_context(allowed_company_ids=self.company_data_2['company'].ids)\
            .action_sheet_move_create()

    deftest_expense_sheet_multi_company_refuse(self):
        self.expense_employee.company_id=self.company_data_2['company']

        #Theexpenseemployeeisabletoacreateanexpensesheetforcompany_2.

        expense_sheet=self.env['hr.expense.sheet']\
            .with_user(self.expense_user_employee)\
            .with_context(allowed_company_ids=self.company_data_2['company'].ids)\
            .create({
                'name':'FirstExpenseforemployee',
                'employee_id':self.expense_employee.id,
                'journal_id':self.company_data_2['default_journal_purchase'].id,
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
        self.assertRecordValues(expense_sheet,[{'company_id':self.company_data_2['company'].id}])

        #Theexpenseemployeeisabletosubmittheexpensesheet.

        expense_sheet.with_user(self.expense_user_employee).action_submit_sheet()

        #Anexpensemanagerisnotabletoapprovewithoutaccesstocompany_2.

        withself.assertRaises(UserError):
            expense_sheet\
                .with_user(self.expense_user_manager)\
                .with_context(allowed_company_ids=self.company_data['company'].ids)\
                .refuse_sheet('')

        #Anexpensemanagerisabletoapprovewithaccesstocompany_2.

        expense_sheet\
            .with_user(self.expense_user_manager)\
            .with_context(allowed_company_ids=self.company_data_2['company'].ids)\
            .refuse_sheet('')
