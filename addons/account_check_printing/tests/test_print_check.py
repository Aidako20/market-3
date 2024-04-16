#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.addons.account_check_printing.models.account_paymentimportINV_LINES_PER_STUB
fromflectra.testsimporttagged
fromflectra.tools.miscimportNON_BREAKING_SPACE

importmath


@tagged('post_install','-at_install')
classTestPrintCheck(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.payment_method_check=cls.env.ref("account_check_printing.account_payment_method_check")

        cls.company_data['default_journal_bank'].write({
            'outbound_payment_method_ids':[(6,0,(
                cls.env.ref('account.account_payment_method_manual_out').id,
                cls.payment_method_check.id,
            ))],
        })

    deftest_in_invoice_check_manual_sequencing(self):
        '''Testthecheckgenerationforvendorbills.'''
        nb_invoices_to_test=INV_LINES_PER_STUB+1

        self.company_data['default_journal_bank'].write({
            'check_manual_sequencing':True,
            'check_next_number':'00042',
        })

        #Create10customerinvoices.
        in_invoices=self.env['account.move'].create([{
            'move_type':'in_invoice',
            'partner_id':self.partner_a.id,
            'date':'2017-01-01',
            'invoice_date':'2017-01-01',
            'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':100.0})]
        }foriinrange(nb_invoices_to_test)])
        in_invoices.action_post()

        #Createasinglepayment.
        payment=self.env['account.payment.register'].with_context(active_model='account.move',active_ids=in_invoices.ids).create({
            'group_payment':True,
            'payment_method_id':self.payment_method_check.id,
        })._create_payments()

        #Checkcreatedpayment.
        self.assertRecordValues(payment,[{
            'payment_method_id':self.payment_method_check.id,
            'check_amount_in_words':payment.currency_id.amount_to_text(100.0*nb_invoices_to_test),
            'check_number':'00042',
        }])

        #Checkpages.
        self.company_data['company'].account_check_printing_multi_stub=True
        report_pages=payment._check_get_pages()
        self.assertEqual(len(report_pages),int(math.ceil(len(in_invoices)/INV_LINES_PER_STUB)))

        self.company_data['company'].account_check_printing_multi_stub=False
        report_pages=payment._check_get_pages()
        self.assertEqual(len(report_pages),1)

    deftest_out_refund_check_manual_sequencing(self):
        '''Testthecheckgenerationforrefunds.'''
        nb_invoices_to_test=INV_LINES_PER_STUB+1

        self.company_data['default_journal_bank'].write({
            'check_manual_sequencing':True,
            'check_next_number':'00042',
        })

        #Create10refunds.
        out_refunds=self.env['account.move'].create([{
            'move_type':'out_refund',
            'partner_id':self.partner_a.id,
            'date':'2017-01-01',
            'invoice_date':'2017-01-01',
            'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':100.0})]
        }foriinrange(nb_invoices_to_test)])
        out_refunds.action_post()

        #Createasinglepayment.
        payment=self.env['account.payment.register'].with_context(active_model='account.move',active_ids=out_refunds.ids).create({
            'group_payment':True,
            'payment_method_id':self.payment_method_check.id,
        })._create_payments()

        #Checkcreatedpayment.
        self.assertRecordValues(payment,[{
            'payment_method_id':self.payment_method_check.id,
            'check_amount_in_words':payment.currency_id.amount_to_text(100.0*nb_invoices_to_test),
            'check_number':'00042',
        }])

        #Checkpages.
        self.company_data['company'].account_check_printing_multi_stub=True
        report_pages=payment._check_get_pages()
        self.assertEqual(len(report_pages),int(math.ceil(len(out_refunds)/INV_LINES_PER_STUB)))

        self.company_data['company'].account_check_printing_multi_stub=False
        report_pages=payment._check_get_pages()
        self.assertEqual(len(report_pages),1)

    deftest_multi_currency_stub_lines(self):
        #Invoiceincompany'scurrency:100$
        invoice=self.env['account.move'].create({
            'move_type':'in_invoice',
            'partner_id':self.partner_a.id,
            'date':'2016-01-01',
            'invoice_date':'2016-01-01',
            'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':100.0})]
        })
        invoice.action_post()

        #Partialpaymentinforeigncurrency:100Gol=33.33$.
        payment=self.env['account.payment.register'].with_context(active_model='account.move',active_ids=invoice.ids).create({
            'payment_method_id':self.payment_method_check.id,
            'currency_id':self.currency_data['currency'].id,
            'amount':100.0,
            'payment_date':'2017-01-01',
        })._create_payments()

        stub_pages=payment._check_make_stub_pages()

        self.assertEqual(stub_pages,[[{
            'due_date':'01/01/2016',
            'number':invoice.name,
            'amount_total':f'${NON_BREAKING_SPACE}100.00',
            'amount_residual':f'${NON_BREAKING_SPACE}50.00',
            'amount_paid':f'150.000{NON_BREAKING_SPACE}☺',
            'currency':invoice.currency_id,
        }]])

    deftest_in_invoice_check_manual_sequencing_with_multiple_payments(self):
        """
           Testthecheckgenerationforvendorbillswithmultiplepayments.
        """
        nb_invoices_to_test=INV_LINES_PER_STUB+1

        self.company_data['default_journal_bank'].write({
            'check_manual_sequencing':True,
            'check_next_number':'11111',
        })

        in_invoices=self.env['account.move'].create([{
            'move_type':'in_invoice',
            'partner_id':self.partner_a.id,
            'date':'2017-01-01',
            'invoice_date':'2017-01-01',
            'invoice_line_ids':[(0,0,{'product_id':self.product_a.id,'price_unit':100.0})]
        }foriinrange(nb_invoices_to_test)])
        in_invoices.action_post()

        payments=self.env['account.payment.register'].with_context(active_model='account.move',active_ids=in_invoices.ids).create({
            'group_payment':False,
            'payment_method_id':self.payment_method_check.id,
        })._create_payments()

        self.assertEqual(set(payments.mapped('check_number')),{str(x)forxinrange(11111,11111+nb_invoices_to_test)})

    deftest_print_great_pre_number_check(self):
        """
        Makesurewecanuseintegerofmorethan2147483647inchecksequence
         limitof`integer`typeinpsql:https://www.postgresql.org/docs/current/datatype-numeric.html
        """
        vals={
            'payment_type':'outbound',
            'partner_type':'supplier',
            'amount':100.0,
            'journal_id':self.company_data['default_journal_bank'].id,
            'payment_method_id':self.payment_method_check.id,
        }
        payment=self.env['account.payment'].create(vals)
        payment.action_post()
        self.assertTrue(payment.write({'check_number':'2147483647'}))
        self.assertTrue(payment.write({'check_number':'2147483648'}))

        payment_2=self.env['account.payment'].create(vals)
        payment_2.action_post()
        action_window=payment_2.print_checks()
        self.assertEqual(action_window['context']['default_next_check_number'],'2147483649',"Checknumbershouldhavebeenincrementedwithouterror.")
