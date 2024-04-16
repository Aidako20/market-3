#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.hr_expense.tests.commonimportTestExpenseCommon
fromflectra.testsimporttagged,Form
fromflectra.tools.miscimportformatLang
fromflectraimportfields
fromflectra.exceptionsimportUserError


@tagged('-at_install','post_install')
classTestExpenses(TestExpenseCommon):

    deftest_expense_values(self):
        """Checkingaccountingmoveentriesandanalyticentrieswhensubmittingexpense"""

        #Theexpenseemployeeisabletoacreateanexpensesheet.
        #Thetotalshouldbe1725.0because:
        #-firstline:1000.0(unitamount)+150.0(tax)=1150.0
        #-secondline:(1500.0(unitamount)+225.0(tax))*1/3(rate)=575.0.

        expense_sheet=self.env['hr.expense.sheet'].create({
            'name':'FirstExpenseforemployee',
            'employee_id':self.expense_employee.id,
            'journal_id':self.company_data['default_journal_purchase'].id,
            'accounting_date':'2017-01-01',
            'expense_line_ids':[
                (0,0,{
                    #Expensewithoutforeigncurrency.
                    'name':'expense_1',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':1000.0,
                    'tax_ids':[(6,0,self.company_data['default_tax_purchase'].ids)],
                    'analytic_account_id':self.analytic_account_1.id,
                    'employee_id':self.expense_employee.id,
                }),
                (0,0,{
                    #Expensewithforeigncurrency(rate1:3).
                    'name':'expense_1',
                    'date':'2016-01-01',
                    'product_id':self.product_b.id,
                    'unit_amount':1500.0,
                    'tax_ids':[(6,0,self.company_data['default_tax_purchase'].ids)],
                    'analytic_account_id':self.analytic_account_2.id,
                    'currency_id':self.currency_data['currency'].id,
                    'employee_id':self.expense_employee.id,
                }),
            ],
        })

        #Checkexpensesheetvalues.
        self.assertRecordValues(expense_sheet,[{'state':'draft','total_amount':1725.0}])

        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()

        #Checkexpensesheetjournalentryvalues.
        self.assertRecordValues(expense_sheet.account_move_id.line_ids.sorted('balance'),[
            #Receivableline(companycurrency):
            {
                'debit':0.0,
                'credit':1150.0,
                'amount_currency':-1150.0,
                'account_id':self.company_data['default_account_payable'].id,
                'product_id':False,
                'currency_id':self.company_data['currency'].id,
                'tax_line_id':False,
                'analytic_account_id':False,
            },
            #Receivableline(foreigncurrency):
            {
                'debit':0.0,
                'credit':575.0,
                'amount_currency':-1725.0,
                'account_id':self.company_data['default_account_payable'].id,
                'product_id':False,
                'currency_id':self.currency_data['currency'].id,
                'tax_line_id':False,
                'analytic_account_id':False,
            },
            #Taxline(foreigncurrency):
            {
                'debit':75.0,
                'credit':0.0,
                'amount_currency':225.0,
                'account_id':self.company_data['default_account_tax_purchase'].id,
                'product_id':False,
                'currency_id':self.currency_data['currency'].id,
                'tax_line_id':self.company_data['default_tax_purchase'].id,
                'analytic_account_id':False,
            },
            #Taxline(companycurrency):
            {
                'debit':150.0,
                'credit':0.0,
                'amount_currency':150.0,
                'account_id':self.company_data['default_account_tax_purchase'].id,
                'product_id':False,
                'currency_id':self.company_data['currency'].id,
                'tax_line_id':self.company_data['default_tax_purchase'].id,
                'analytic_account_id':False,
            },
            #Productline(foreigncurrency):
            {
                'debit':500.0,
                'credit':0.0,
                'amount_currency':1500.0,
                'account_id':self.company_data['default_account_expense'].id,
                'product_id':self.product_b.id,
                'currency_id':self.currency_data['currency'].id,
                'tax_line_id':False,
                'analytic_account_id':self.analytic_account_2.id,
            },
            #Productline(companycurrency):
            {
                'debit':1000.0,
                'credit':0.0,
                'amount_currency':1000.0,
                'account_id':self.company_data['default_account_expense'].id,
                'product_id':self.product_a.id,
                'currency_id':self.company_data['currency'].id,
                'tax_line_id':False,
                'analytic_account_id':self.analytic_account_1.id,
            },
        ])

        #Checkexpenseanalyticlines.
        self.assertRecordValues(expense_sheet.account_move_id.line_ids.analytic_line_ids.sorted('amount'),[
            {
                'amount':-1000.0,
                'date':fields.Date.from_string('2017-01-01'),
                'account_id':self.analytic_account_1.id,
                'currency_id':self.company_data['currency'].id,
            },
            {
                'amount':-500.0,
                'date':fields.Date.from_string('2017-01-01'),
                'account_id':self.analytic_account_2.id,
                'currency_id':self.company_data['currency'].id,
            },
        ])

    deftest_account_entry_multi_currency(self):
        """Checkingaccountingmoveentriesandanalyticentrieswhensubmittingexpense.With
            multi-currency.Andtaxes."""

        #Clean-uptherates
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",[self.env.ref('base.USD').id,self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'currency_id':self.env.ref('base.EUR').id,
            'company_id':self.env.company.id,
            'rate':2.0,
            'name':'2010-01-01',
        })

        expense=self.env['hr.expense.sheet'].create({
            'name':'ExpenseforDickTracy',
            'employee_id':self.expense_employee.id,
        })
        tax=self.env['account.tax'].create({
            'name':'Expense10%',
            'amount':10,
            'amount_type':'percent',
            'type_tax_use':'purchase',
            'price_include':True,
        })
        expense_line=self.env['hr.expense'].create({
            'name':'ChoucrouteSaucisse',
            'employee_id':self.expense_employee.id,
            'product_id':self.product_a.id,
            'unit_amount':700.00,
            'tax_ids':[(6,0,tax.ids)],
            'sheet_id':expense.id,
            'analytic_account_id':self.analytic_account_1.id,
            'currency_id':self.env.ref('base.EUR').id,
        })

        #Stateshoulddefaulttodraft
        self.assertEqual(expense.state,'draft','ExpenseshouldbecreatedinDraftstate')
        #SubmittedtoManager
        expense.action_submit_sheet()
        self.assertEqual(expense.state,'submit','ExpenseisnotinReportedstate')
        #Approve
        expense.approve_expense_sheets()
        self.assertEqual(expense.state,'approve','ExpenseisnotinApprovedstate')
        #CreateExpenseEntries
        expense.action_sheet_move_create()
        self.assertEqual(expense.state,'post','ExpenseisnotinWaitingPaymentstate')
        self.assertTrue(expense.account_move_id.id,'ExpenseJournalEntryisnotcreated')

        #Shouldgetthisresult[(0.0,350.0,-700.0),(318.18,0.0,636.36),(31.82,0.0,63.64)]
        forlineinexpense.account_move_id.line_ids:
            ifline.credit:
                self.assertAlmostEqual(line.credit,350.0)
                self.assertAlmostEqual(line.amount_currency,-700.0)
                self.assertEqual(len(line.analytic_line_ids),0,"Thecreditmovelineshouldnothaveanalyticlines")
                self.assertFalse(line.product_id,"Productofcreditmovelineshouldbefalse")
            else:
                ifnotline.tax_line_id==tax:
                    self.assertAlmostEqual(line.debit,318.18)
                    self.assertAlmostEqual(line.amount_currency,636.36)
                    self.assertEqual(len(line.analytic_line_ids),1,"Thedebitmovelineshouldhave1analyticlines")
                    self.assertEqual(line.product_id,self.product_a,"Productofdebitmovelineshouldbetheonefromtheexpense")
                else:
                    self.assertEqual(line.tax_base_amount,318.18)
                    self.assertAlmostEqual(line.debit,31.82)
                    self.assertAlmostEqual(line.amount_currency,63.64)
                    self.assertEqual(len(line.analytic_line_ids),0,"Thetaxmovelineshouldnothaveanalyticlines")
                    self.assertFalse(line.product_id,"Productoftaxmovelineshouldbefalse")

    deftest_expenses_with_tax_and_lockdate(self):
        '''Testcreatingajournalentryformultipleexpensesusingtaxes.Alockdateissetinordertotrigger
        therecomputationofthetaxesbaseamount.
        '''
        self.env.company.tax_lock_date='2020-02-01'

        expense=self.env['hr.expense.sheet'].create({
            'name':'ExpenseforJohnSmith',
            'employee_id':self.expense_employee.id,
            'accounting_date':'2020-01-01'
        })

        foriinrange(2):
            expense_line=self.env['hr.expense'].create({
                'name':'CarTravelExpenses',
                'employee_id':self.expense_employee.id,
                'product_id':self.product_a.id,
                'unit_amount':350.00,
                'tax_ids':[(6,0,[self.tax_purchase_a.id])],
                'sheet_id':expense.id,
                'analytic_account_id':self.analytic_account_1.id,
            })
            expense_line._onchange_product_id_date_account_id()

        expense.action_submit_sheet()
        expense.approve_expense_sheets()

        #Assertnot"Cannotcreateunbalancedjournalentry"error.
        expense.action_sheet_move_create()

    deftest_reconcile_payment(self):
        tax=self.env['account.tax'].create({
            'name':'taxabc',
            'type_tax_use':'purchase',
            'amount_type':'percent',
            'amount':15,
            'price_include':False,
            'include_base_amount':False,
            'tax_exigibility':'on_payment'
        })
        current_assets_type=self.env.ref('account.data_account_type_current_assets')
        company=self.env.company.id
        tax.cash_basis_transition_account_id=self.env['account.account'].create({
            'name':"test",
            'code':999991,
            'reconcile':True,
            'user_type_id':current_assets_type.id,
            'company_id':company,
        }).id

        sheet=self.env['hr.expense.sheet'].create({
            'company_id':company,
            'employee_id':self.expense_employee.id,
            'name':'testsheet',
            'expense_line_ids':[
                (0,0,{
                    'name':'expense_1',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':10.0,
                    'employee_id':self.expense_employee.id,
                    'tax_ids':tax
                }),
                (0,0,{
                    'name':'expense_2',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':1.0,
                    'employee_id':self.expense_employee.id,
                    'tax_ids':tax
                }),
            ],
        })


        #actions
        sheet.action_submit_sheet()
        sheet.approve_expense_sheets()
        sheet.action_sheet_move_create()
        action_data=sheet.action_register_payment()
        wizard= Form(self.env['account.payment.register'].with_context(action_data['context'])).save()
        action=wizard.action_create_payments()
        self.assertEqual(sheet.state,'done','allaccount.move.linelinkedtoexpensesmustbereconciledafterpayment')
        
        move=self.env['account.payment'].browse(action['res_id']).move_id
        move.button_cancel()
        self.assertEqual(sheet.state,'cancel','Sheetstatemustbecancelwhenthepaymentlinkedtothatsheetiscanceled')

    deftest_print_expense_check(self):
        """
        Testthecheckcontentwhenprintingacheck
        thatcomesfromanexpense
        """
        sheet=self.env['hr.expense.sheet'].create({
            'company_id':self.env.company.id,
            'employee_id':self.expense_employee.id,
            'name':'testsheet',
            'expense_line_ids':[
                (0,0,{
                    'name':'expense_1',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':10.0,
                    'employee_id':self.expense_employee.id,
                }),
                (0,0,{
                    'name':'expense_2',
                    'date':'2016-01-01',
                    'product_id':self.product_a.id,
                    'unit_amount':1.0,
                    'employee_id':self.expense_employee.id,
                }),
            ],
        })

        #actions
        sheet.action_submit_sheet()
        sheet.approve_expense_sheets()
        sheet.action_sheet_move_create()
        action_data=sheet.action_register_payment()
        payment_method=self.env.company.bank_journal_ids.outbound_payment_method_ids.filtered(lambdam:m.code=='check_printing')
        withForm(self.env[action_data['res_model']].with_context(action_data['context']))aswiz_form:
            wiz_form.payment_method_id=payment_method
        wizard=wiz_form.save()
        action=wizard.action_create_payments()
        self.assertEqual(sheet.state,'done','allaccount.move.linelinkedtoexpensesmustbereconciledafterpayment')

        payment=self.env[action['res_model']].browse(action['res_id'])
        pages=payment._check_get_pages()
        stub_line=pages[0]['stub_lines'][:1]
        self.assertTrue(stub_line)
        move=self.env[action_data['context']['active_model']].browse(action_data['context']['active_ids'])
        self.assertDictEqual(stub_line[0],{
            'due_date':'',
            'number':'-'.join([move.name,move.ref]ifmove.refelse[move.name]),
            'amount_total':formatLang(self.env,11.0,currency_obj=self.env.company.currency_id),
            'amount_residual':'-',
            'amount_paid':formatLang(self.env,11.0,currency_obj=self.env.company.currency_id),
            'currency':self.env.company.currency_id
        })

    deftest_reset_move_to_draft(self):
        """
        Testthestateofanexpenseanditsreport
        afterresettingthepaidmovetodraft
        """
        #Createexpenseandreport
        expense=self.env['hr.expense'].create({
            'name':'expense_1',
            'employee_id':self.expense_employee.id,
            'product_id':self.product_a.id,
            'unit_amount':1000.00,
        })
        expense.action_submit_expenses()
        expense_sheet=expense.sheet_id

        self.assertEqual(expense.state,'draft','Expensestatemustbedraftbeforesheetsubmission')
        self.assertEqual(expense_sheet.state,'draft','Sheetstatemustbedraftbeforesubmission')

        #Submitreport
        expense_sheet.action_submit_sheet()

        self.assertEqual(expense.state,'reported','Expensestatemustbereportedaftersheetsubmission')
        self.assertEqual(expense_sheet.state,'submit','Sheetstatemustbesubmitaftersubmission')

        #Approvereport
        expense_sheet.approve_expense_sheets()

        self.assertEqual(expense.state,'approved','Expensestatemustbedraftaftersheetapproval')
        self.assertEqual(expense_sheet.state,'approve','Sheetstatemustbedraftafterapproval')

        #Createmove
        expense_sheet.action_sheet_move_create()

        self.assertEqual(expense.state,'approved','Expensestatemustbedraftafterpostingmove')
        self.assertEqual(expense_sheet.state,'post','Sheetstatemustbedraftafterpostingmove')

        #Paymove
        move=expense_sheet.account_move_id
        self.env['account.payment.register'].with_context(active_model='account.move',active_ids=move.ids).create({
            'amount':1000.0,
        })._create_payments()

        self.assertEqual(expense.state,'done','Expensestatemustbedoneafterpayment')
        self.assertEqual(expense_sheet.state,'done','Sheetstatemustbedoneafterpayment')

        #Resetmovetodraft
        move.button_draft()

        self.assertEqual(expense.state,'approved','Expensestatemustbeapprovedafterresettingmovetodraft')
        self.assertEqual(expense_sheet.state,'post','Sheetstatemustbedoneafterresettingmovetodraft')

        #Postandpaymoveagain
        move.action_post()
        self.env['account.payment.register'].with_context(active_model='account.move',active_ids=move.ids).create({
            'amount':1000.0,
        })._create_payments()

        self.assertEqual(expense.state,'done','Expensestatemustbedoneafterpayment')
        self.assertEqual(expense_sheet.state,'done','Sheetstatemustbedoneafterpayment')

    deftest_expense_from_attachments(self):
        #avoidpassingthroughextractionwheninstalled
        if'hr.expense.extract.words'inself.env:
            self.env.company.expense_extract_show_ocr_option_selection='no_send'
        self.env.user.employee_id=self.expense_employee.id
        attachment=self.env['ir.attachment'].create({
            'datas':b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=",
            'name':'file.png',
            'res_model':'hr.expense',
        })
        product=self.env['product.product'].search([('can_be_expensed','=',True)],limit=1)
        product.property_account_expense_id=self.company_data['default_account_payable']

        expense_id=self.env['hr.expense'].create_expense_from_attachments(attachment.id)['res_id']
        expense=self.env['hr.expense'].browse(expense_id)
        self.assertEqual(expense.account_id,product.property_account_expense_id,"Theexpenseaccountshouldbethedefaultoneoftheproduct")
