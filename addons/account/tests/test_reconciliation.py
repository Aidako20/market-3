#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime
importunittest
fromdatetimeimporttimedelta

fromflectraimportapi,fields
fromflectra.addons.account.tests.commonimportTestAccountReconciliationCommon
fromflectra.testsimportForm,tagged


@tagged('post_install','-at_install')
classTestReconciliationExec(TestAccountReconciliationCommon):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.env['res.currency.rate'].search([]).unlink()

    deftest_statement_euro_invoice_usd_transaction_euro_full(self):
        self.env['res.currency.rate'].create({
            'name':'%s-07-01'%time.strftime('%Y'),
            'rate':1.5289,
            'currency_id':self.currency_usd_id,
        })
        #Createacustomerinvoiceof50USD.
        partner=self.env['res.partner'].create({'name':'test'})
        move=self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'move_type':'out_invoice',
            'partner_id':partner.id,
            'invoice_date':'%s-07-01'%time.strftime('%Y'),
            'date':'%s-07-01'%time.strftime('%Y'),
            'currency_id':self.currency_usd_id,
            'invoice_line_ids':[
                (0,0,{'quantity':1,'price_unit':50.0,'name':'test'})
            ],
        })
        move.action_post()

        #Createabankstatementof40EURO.
        bank_stmt=self.env['account.bank.statement'].create({
            'journal_id':self.bank_journal_euro.id,
            'date':'%s-01-01'%time.strftime('%Y'),
            'line_ids':[
                (0,0,{
                    'payment_ref':'test',
                    'partner_id':partner.id,
                    'amount':40.0,
                    'date':'%s-01-01'%time.strftime('%Y')
                })
            ],
        })

        #Reconcilethebankstatementwiththeinvoice.
        receivable_line=move.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        bank_stmt.button_post()
        bank_stmt.line_ids[0].reconcile([
            {'id':receivable_line.id},
            {'name':'exchangedifference','balance':-7.3,'account_id':self.diff_income_account.id},
        ])

        self.assertRecordValues(bank_stmt.line_ids.line_ids,[
            {'debit':40.0,    'credit':0.0,     'amount_currency':40.0,   'currency_id':self.currency_euro_id},
            {'debit':0.0,     'credit':7.3,     'amount_currency':-7.3,   'currency_id':self.currency_euro_id},
            {'debit':0.0,     'credit':32.7,    'amount_currency':-32.7,  'currency_id':self.currency_euro_id},
        ])

        #Theinvoiceshouldbepaid,asthepaymentstotallycoveritstotal
        self.assertEqual(move.payment_state,'paid','Theinvoiceshouldbepaidbynow')
        self.assertTrue(receivable_line.reconciled,'Theinvoiceshouldbetotallyreconciled')
        self.assertTrue(receivable_line.full_reconcile_id,'Theinvoiceshouldhaveafullreconcilenumber')
        self.assertEqual(receivable_line.amount_residual,0,'Theinvoiceshouldbetotallyreconciled')
        self.assertEqual(receivable_line.amount_residual_currency,0,'Theinvoiceshouldbetotallyreconciled')

    @unittest.skip('adapttonewaccounting')
    deftest_balanced_exchanges_gain_loss(self):
        #Thepointofthistestistoshowthatwehandlecorrectlythegain/lossexchangesduringreconciliationsinforeigncurrencies.
        #Forinstance,withacompanysetinEUR,andaUSDratesetto0.033,
        #thereconciliationofaninvoiceof2.00USD(60.61EUR)andabankstatementoftwolinesof1.00USD(30.30EUR)
        #willleadtoanexchangeloss,thatshouldbehandledcorrectlywithinthejournalitems.
        env=api.Environment(self.cr,self.uid,{})
        #WeupdatethecurrencyrateofthecurrencyUSDinordertoforcethegain/lossexchangesinnextsteps
        rateUSDbis=env.ref("base.rateUSDbis")
        rateUSDbis.write({
            'name':time.strftime('%Y-%m-%d')+'00:00:00',
            'rate':0.033,
        })
        #Wecreateacustomerinvoiceof2.00USD
        invoice=self.account_invoice_model.create({
            'partner_id':self.partner_agrolait_id,
            'currency_id':self.currency_usd_id,
            'name':'Foreigninvoicewithexchangegain',
            'account_id':self.account_rcv_id,
            'move_type':'out_invoice',
            'invoice_date':time.strftime('%Y-%m-%d'),
            'date':time.strftime('%Y-%m-%d'),
            'journal_id':self.bank_journal_usd_id,
            'invoice_line':[
                (0,0,{
                    'name':'linethatwillleadtoanexchangegain',
                    'quantity':1,
                    'price_unit':2,
                })
            ]
        })
        invoice.action_post()
        #Wecreateabankstatementwithtwolinesof1.00USDeach.
        statement=self.env['account.bank.statement'].create({
            'journal_id':self.bank_journal_usd_id,
            'date':time.strftime('%Y-%m-%d'),
            'line_ids':[
                (0,0,{
                    'name':'halfpayment',
                    'partner_id':self.partner_agrolait_id,
                    'amount':1.0,
                    'date':time.strftime('%Y-%m-%d')
                }),
                (0,0,{
                    'name':'secondhalfpayment',
                    'partner_id':self.partner_agrolait_id,
                    'amount':1.0,
                    'date':time.strftime('%Y-%m-%d')
                })
            ]
        })

        #Weprocessthereconciliationoftheinvoicelinewiththetwobankstatementlines
        line_id=None
        forlininvoice.line_id:
            ifl.account_id.id==self.account_rcv_id:
                line_id=l
                break
        forstatement_lineinstatement.line_ids:
            statement_line.reconcile([{'id':line_id.id}])

        #Theinvoiceshouldbepaid,asthepaymentstotallycoveritstotal
        self.assertEqual(invoice.state,'paid','Theinvoiceshouldbepaidbynow')
        reconcile=None
        forpaymentininvoice.payment_ids:
            reconcile=payment.reconcile_model_id
            break
        #Theinvoiceshouldbereconciled(entirely,notapartialreconciliation)
        self.assertTrue(reconcile,'Theinvoiceshouldbetotallyreconciled')
        result={}
        exchange_loss_line=None
        forlineinreconcile.line_id:
            res_account=result.setdefault(line.account_id,{'debit':0.0,'credit':0.0,'count':0})
            res_account['debit']=res_account['debit']+line.debit
            res_account['credit']=res_account['credit']+line.credit
            res_account['count']+=1
            ifline.credit==0.01:
                exchange_loss_line=line
        #Weshouldbeabletofindamovelineof0.01EURontheDebtorsaccount,beingthecentwelostduringthecurrencyexchange
        self.assertTrue(exchange_loss_line,'Thereshouldbeonemovelineof0.01EURincredit')
        #Thejournalitemsofthereconciliationshouldhavetheirdebitandcredittotalequal
        #Besides,thetotaldebitandtotalcreditshouldbe60.61EUR(2.00USD)
        self.assertEqual(sum(res['debit']forresinresult.values()),60.61)
        self.assertEqual(sum(res['credit']forresinresult.items()),60.61)
        counterpart_exchange_loss_line=None
        forlineinexchange_loss_line.move_id.line_id:
            ifline.account_id.id==self.account_fx_expense_id:
                counterpart_exchange_loss_line=line
        # Weshouldbeabletofindamovelineof0.01EURontheForeignExchangeLossaccount
        self.assertTrue(counterpart_exchange_loss_line,'Thereshouldbeonemovelineof0.01EURonaccount"ForeignExchangeLoss"')

    deftest_manual_reconcile_wizard_opw678153(self):

        defcreate_move(name,amount,amount_currency,currency_id):
            debit_line_vals={
                'name':name,
                'debit':amount>0andamountor0.0,
                'credit':amount<0and-amountor0.0,
                'account_id':self.account_rcv.id,
                'amount_currency':amount_currency,
                'currency_id':currency_id,
            }
            credit_line_vals=debit_line_vals.copy()
            credit_line_vals['debit']=debit_line_vals['credit']
            credit_line_vals['credit']=debit_line_vals['debit']
            credit_line_vals['account_id']=self.account_rsa.id
            credit_line_vals['amount_currency']=-debit_line_vals['amount_currency']
            vals={
                'journal_id':self.bank_journal_euro.id,
                'line_ids':[(0,0,debit_line_vals),(0,0,credit_line_vals)]
            }
            move=self.env['account.move'].create(vals)
            move.action_post()
            returnmove.id
        move_list_vals=[
            ('1',-1.83,0,self.currency_swiss_id),
            ('2',728.35,795.05,self.currency_swiss_id),
            ('3',-4.46,0,self.currency_swiss_id),
            ('4',0.32,0,self.currency_swiss_id),
            ('5',14.72,16.20,self.currency_swiss_id),
            ('6',-737.10,-811.25,self.currency_swiss_id),
        ]
        move_ids=[]
        forname,amount,amount_currency,currency_idinmove_list_vals:
            move_ids.append(create_move(name,amount,amount_currency,currency_id))
        aml_recs=self.env['account.move.line'].search([('move_id','in',move_ids),('account_id','=',self.account_rcv.id),('reconciled','=',False)])
        aml_recs.reconcile()
        foramlinaml_recs:
            self.assertTrue(aml.reconciled,'Thejournalitemshouldbetotallyreconciled')
            self.assertEqual(aml.amount_residual,0,'Thejournalitemshouldbetotallyreconciled')
            self.assertEqual(aml.amount_residual_currency,0,'Thejournalitemshouldbetotallyreconciled')

    deftest_partial_reconcile_currencies_01(self):
        #               clientAccount(payable,rsa)
        #       Debit                     Credit
        #--------------------------------------------------------
        #Paya:25/0.5=50      |  Inva:50/0.5=100
        #Payb:50/0.75=66.66   |  Invb:50/0.75=66.66
        #Payc:25/0.8=31.25    |
        #
        #Debit_currency=100     |Creditcurrency=100
        #Debit=147.91           |Credit=166.66
        #BalanceDebit=18.75
        #CounterpartCreditgoesinExchangediff

        dest_journal_id=self.env['account.journal'].create({
            'name':'dest_journal_id',
            'type':'bank',
        })

        #SettingupratesforUSD(main_companyisinEUR)
        self.env['res.currency.rate'].create({'name':time.strftime('%Y')+'-'+'07'+'-01',
            'rate':0.5,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id})

        self.env['res.currency.rate'].create({'name':time.strftime('%Y')+'-'+'08'+'-01',
            'rate':0.75,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id})

        self.env['res.currency.rate'].create({'name':time.strftime('%Y')+'-'+'09'+'-01',
            'rate':0.80,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id})

        #PreparingInvoices(fromvendor)
        invoice_a=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'partner_id':self.partner_agrolait_id,
            'currency_id':self.currency_usd_id,
            'invoice_date':'%s-07-01'%time.strftime('%Y'),
            'date':'%s-07-01'%time.strftime('%Y'),
            'invoice_line_ids':[
                (0,0,{'product_id':self.product.id,'quantity':1,'price_unit':50.0})
            ],
        })
        invoice_b=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type':'in_invoice',
            'partner_id':self.partner_agrolait_id,
            'currency_id':self.currency_usd_id,
            'invoice_date':'%s-08-01'%time.strftime('%Y'),
            'date':'%s-08-01'%time.strftime('%Y'),
            'invoice_line_ids':[
                (0,0,{'product_id':self.product.id,'quantity':1,'price_unit':50.0})
            ],
        })
        (invoice_a+invoice_b).action_post()

        #PreparingPayments
        #Onepartialforinvoice_a(fullyassignedtoit)
        payment_a=self.env['account.payment'].create({'payment_type':'outbound',
            'amount':25,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_euro.id,
            'company_id':self.company.id,
            'date':time.strftime('%Y')+'-'+'07'+'-01',
            'partner_id':self.partner_agrolait_id,
            'payment_method_id':self.env.ref('account.account_payment_method_manual_out').id,
            'partner_type':'supplier'})

        #Onethatwillcompletethepaymentofa,therestgoestob
        payment_b=self.env['account.payment'].create({'payment_type':'outbound',
            'amount':50,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_euro.id,
            'company_id':self.company.id,
            'date':time.strftime('%Y')+'-'+'08'+'-01',
            'partner_id':self.partner_agrolait_id,
            'payment_method_id':self.env.ref('account.account_payment_method_manual_out').id,
            'partner_type':'supplier'})

        #Thelastonewillcompletethepaymentofb
        payment_c=self.env['account.payment'].create({'payment_type':'outbound',
            'amount':25,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_euro.id,
            'company_id':self.company.id,
            'date':time.strftime('%Y')+'-'+'09'+'-01',
            'partner_id':self.partner_agrolait_id,
            'payment_method_id':self.env.ref('account.account_payment_method_manual_out').id,
            'partner_type':'supplier'})

        payment_a.action_post()
        payment_b.action_post()
        payment_c.action_post()

        #Assigningpaymentstoinvoices
        debit_line_a=payment_a.line_ids.filtered(lambdal:l.debitandl.account_id==self.account_rsa)
        debit_line_b=payment_b.line_ids.filtered(lambdal:l.debitandl.account_id==self.account_rsa)
        debit_line_c=payment_c.line_ids.filtered(lambdal:l.debitandl.account_id==self.account_rsa)

        invoice_a.js_assign_outstanding_line(debit_line_a.id)
        invoice_a.js_assign_outstanding_line(debit_line_b.id)
        invoice_b.js_assign_outstanding_line(debit_line_b.id)
        invoice_b.js_assign_outstanding_line(debit_line_c.id)

        #Assertingcorrectness(onlyinthepayableaccount)
        full_reconcile=False
        reconciled_amls=(debit_line_a+debit_line_b+debit_line_c+(invoice_a+invoice_b).mapped('line_ids'))\
            .filtered(lambdal:l.account_id==self.account_rsa)
        foramlinreconciled_amls:
            self.assertEqual(aml.amount_residual,0.0)
            self.assertEqual(aml.amount_residual_currency,0.0)
            self.assertTrue(aml.reconciled)
            ifnotfull_reconcile:
                full_reconcile=aml.full_reconcile_id
            else:
                self.assertTrue(aml.full_reconcile_id==full_reconcile)

        full_rec_move=full_reconcile.exchange_move_id
        #Globallycheckwhethertheamountiscorrect
        self.assertEqual(sum(full_rec_move.mapped('line_ids.debit')),18.75)

        #Checkingifthedirectionofthemoveiscorrect
        full_rec_payable=full_rec_move.line_ids.filtered(lambdal:l.account_id==self.account_rsa)
        self.assertEqual(full_rec_payable.balance,18.75)

    deftest_unreconcile(self):
        #Usecase:
        #2invoicespaidwithasinglepayment.Unreconcilethepaymentwithoneinvoice,the
        #otherinvoiceshouldremainreconciled.
        inv1=self.create_invoice(invoice_amount=10,currency_id=self.currency_usd_id)
        inv2=self.create_invoice(invoice_amount=20,currency_id=self.currency_usd_id)
        payment=self.env['account.payment'].create({
            'payment_type':'inbound',
            'payment_method_id':self.env.ref('account.account_payment_method_manual_in').id,
            'partner_type':'customer',
            'partner_id':self.partner_agrolait_id,
            'amount':100,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_usd.id,
        })
        payment.action_post()
        credit_aml=payment.line_ids.filtered('credit')

        #Checkresidualbeforeassignation
        self.assertAlmostEqual(inv1.amount_residual,10)
        self.assertAlmostEqual(inv2.amount_residual,20)

        #Assigncreditandresidual
        inv1.js_assign_outstanding_line(credit_aml.id)
        inv2.js_assign_outstanding_line(credit_aml.id)
        self.assertAlmostEqual(inv1.amount_residual,0)
        self.assertAlmostEqual(inv2.amount_residual,0)

        #Unreconcileoneinvoiceatatimeandcheckresidual
        credit_aml.remove_move_reconcile()
        self.assertAlmostEqual(inv1.amount_residual,10)
        self.assertAlmostEqual(inv2.amount_residual,20)

    deftest_unreconcile_exchange(self):
        #Usecase:
        #-CompanycurrencyinEUR
        #-Create2ratesforUSD:
        #  1.0on2018-01-01
        #  0.5on2018-02-01
        #-Createaninvoiceon2018-01-02of111USD
        #-Registerapaymenton2018-02-02of111USD
        #-Unreconcilethepayment

        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-08-01',
            'rate':0.5,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id
        })
        inv=self.create_invoice(invoice_amount=111,currency_id=self.currency_usd_id)
        payment=self.env['account.payment'].create({
            'payment_type':'inbound',
            'payment_method_id':self.env.ref('account.account_payment_method_manual_in').id,
            'partner_type':'customer',
            'partner_id':self.partner_agrolait_id,
            'amount':111,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_usd.id,
            'date':time.strftime('%Y')+'-08-01',
        })
        payment.action_post()
        credit_aml=payment.line_ids.filtered('credit')

        #Checkresidualbeforeassignation
        self.assertAlmostEqual(inv.amount_residual,111)

        #Assigncredit,checkexchangemoveandresidual
        inv.js_assign_outstanding_line(credit_aml.id)
        self.assertEqual(len(payment.line_ids.mapped('full_reconcile_id').exchange_move_id),1)
        self.assertAlmostEqual(inv.amount_residual,0)

        #Unreconcileinvoiceandcheckresidual
        credit_aml.remove_move_reconcile()
        self.assertAlmostEqual(inv.amount_residual,111)

    deftest_revert_payment_and_reconcile(self):
        payment=self.env['account.payment'].create({
            'payment_method_id':self.inbound_payment_method.id,
            'payment_type':'inbound',
            'partner_type':'customer',
            'partner_id':self.partner_agrolait_id,
            'journal_id':self.bank_journal_usd.id,
            'date':'2018-06-04',
            'amount':666,
        })
        payment.action_post()

        self.assertEqual(len(payment.line_ids),2)

        bank_line=payment.line_ids.filtered(lambdal:l.account_id.id==self.bank_journal_usd.payment_debit_account_id.id)
        customer_line=payment.line_ids-bank_line

        self.assertEqual(len(bank_line),1)
        self.assertEqual(len(customer_line),1)
        self.assertNotEqual(bank_line.id,customer_line.id)

        self.assertEqual(bank_line.move_id.id,customer_line.move_id.id)
        move=bank_line.move_id

        #Reversingthepayment'smove
        reversed_move=move._reverse_moves([{'date':'2018-06-04'}])
        self.assertEqual(len(reversed_move),1)

        self.assertEqual(len(reversed_move.line_ids),2)

        #Testingthereconciliationmatchingbetweenthemovelinesandtheirreversedcounterparts
        reversed_bank_line=reversed_move.line_ids.filtered(lambdal:l.account_id.id==self.bank_journal_usd.payment_debit_account_id.id)
        reversed_customer_line=reversed_move.line_ids-reversed_bank_line

        self.assertEqual(len(reversed_bank_line),1)
        self.assertEqual(len(reversed_customer_line),1)
        self.assertNotEqual(reversed_bank_line.id,reversed_customer_line.id)
        self.assertEqual(reversed_bank_line.move_id.id,reversed_customer_line.move_id.id)

        self.assertEqual(reversed_bank_line.full_reconcile_id.id,bank_line.full_reconcile_id.id)
        self.assertEqual(reversed_customer_line.full_reconcile_id.id,customer_line.full_reconcile_id.id)


    deftest_revert_payment_and_reconcile_exchange(self):

        #Areversalofareconciledpaymentwhichcreatedacurrencyexchangeentry,shouldcreatereversalmoves
        #whichmovelinesshouldbereconciledtwobytwowiththeoriginalmove'slines

        def_determine_debit_credit_line(move):
            line_ids_reconciliable=move.line_ids.filtered(lambdal:l.account_id.reconcileorl.account_id.internal_type=='liquidity')
            returnline_ids_reconciliable.filtered(lambdal:l.debit),line_ids_reconciliable.filtered(lambdal:l.credit)

        def_move_revert_test_pair(move,revert):
            self.assertTrue(move.line_ids)
            self.assertTrue(revert.line_ids)

            move_lines=_determine_debit_credit_line(move)
            revert_lines=_determine_debit_credit_line(revert)

            #inthecaseoftheexchangeentry,onlyonepairoflineswillbefound
            ifmove_lines[0]andrevert_lines[1]:
                self.assertTrue(move_lines[0].full_reconcile_id.exists())
                self.assertEqual(move_lines[0].full_reconcile_id.id,revert_lines[1].full_reconcile_id.id)

            ifmove_lines[1]andrevert_lines[0]:
                self.assertTrue(move_lines[1].full_reconcile_id.exists())
                self.assertEqual(move_lines[1].full_reconcile_id.id,revert_lines[0].full_reconcile_id.id)

        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-08-01',
            'rate':0.5,
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id
        })
        inv=self.create_invoice(invoice_amount=111,currency_id=self.currency_usd_id)
        payment=self.env['account.payment'].create({
            'payment_type':'inbound',
            'payment_method_id':self.env.ref('account.account_payment_method_manual_in').id,
            'partner_type':'customer',
            'partner_id':self.partner_agrolait_id,
            'amount':111,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_usd.id,
            'date':time.strftime('%Y')+'-08-01',
        })
        payment.action_post()

        credit_aml=payment.line_ids.filtered('credit')
        inv.js_assign_outstanding_line(credit_aml.id)
        self.assertTrue(inv.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")

        exchange_reconcile=payment.line_ids.mapped('full_reconcile_id')
        exchange_move=exchange_reconcile.exchange_move_id
        payment_move=payment.line_ids[0].move_id

        reverted_payment_move=payment_move._reverse_moves([{'date':time.strftime('%Y')+'-08-01'}],cancel=True)

        #Afterreversalofpayment,theinvoiceshouldbeopen
        self.assertTrue(inv.state=='posted','Theinvoiceshouldbeopenagain')
        self.assertFalse(exchange_reconcile.exists())

        reverted_exchange_move=self.env['account.move'].search([('journal_id','=',exchange_move.journal_id.id),('ref','ilike',exchange_move.name)],limit=1)
        _move_revert_test_pair(payment_move,reverted_payment_move)
        _move_revert_test_pair(exchange_move,reverted_exchange_move)

    deftest_partial_reconcile_currencies_02(self):
        ####
        #Day1:InvoiceCust/001tocustomer(expressedinUSD)
        #MarketvalueofUSD(day1):1USD=0.5EUR
        #*Dr.100USD/50EUR-Accountsreceivable
        #*Cr.100USD/50EUR-Revenue
        ####
        dest_journal_id=self.env['account.journal'].create({
            'name':'turlututu',
            'type':'bank',
            'company_id':self.env.company.id,
        })

        self.env['res.currency.rate'].create({
            'currency_id':self.currency_usd_id,
            'name':time.strftime('%Y')+'-01-01',
            'rate':2,
        })

        invoice_cust_1=self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'move_type':'out_invoice',
            'partner_id':self.partner_agrolait_id,
            'invoice_date':'%s-01-01'%time.strftime('%Y'),
            'date':'%s-01-01'%time.strftime('%Y'),
            'currency_id':self.currency_usd_id,
            'invoice_line_ids':[
                (0,0,{'quantity':1,'price_unit':100.0,'name':'productthatcost100'})
            ],
        })
        invoice_cust_1.action_post()
        aml=invoice_cust_1.invoice_line_ids[0]
        self.assertEqual(aml.credit,50.0)
        #####
        #Day2:ReceivepaymentforhalfinvoiceCust/1(inUSD)
        #-------------------------------------------------------
        #MarketvalueofUSD(day2):1USD=1EUR

        #Paymenttransaction:
        #*Dr.50USD/50EUR-EURBank(valuedatmarketprice
        #atthetimeofreceivingthemoney)
        #*Cr.50USD/50EUR-AccountsReceivable
        #####
        self.env['res.currency.rate'].create({
            'currency_id':self.currency_usd_id,
            'name':time.strftime('%Y')+'-01-02',
            'rate':1,
        })

        payment=self.env['account.payment.register']\
            .with_context(active_model='account.move',active_ids=invoice_cust_1.ids)\
            .create({
                'payment_date':time.strftime('%Y')+'-01-02',
                'amount':50,
                'journal_id':dest_journal_id.id,
                'currency_id':self.currency_usd_id,
            })\
            ._create_payments()

        #Weexpectatthispointthattheinvoiceshouldstillbeopen,in'partial'state,
        #becausetheyoweusstill50CC.
        self.assertEqual(invoice_cust_1.payment_state,'partial','Invoiceisinstatus%s'%invoice_cust_1.state)

    deftest_multiple_term_reconciliation_opw_1906665(self):
        '''Testthatwhenregisteringapaymenttoaninvoicewithmultiple
        paymenttermlinesthereconciliationhappensagainsttheline
        withtheearliestdate_maturity
        '''

        payment_term=self.env['account.payment.term'].create({
            'name':'Payin2installments',
            'line_ids':[
                #Pay50%immediately
                (0,0,{
                    'value':'percent',
                    'value_amount':50,
                }),
                #Paytherestafter14days
                (0,0,{
                    'value':'balance',
                    'days':14,
                })
            ],
        })

        #can'tuseself.create_invoicebecauseitvalidatesandweneedtosetpayment_term_id
        invoice=self.create_invoice_partner(
            partner_id=self.partner_agrolait_id,
            payment_term_id=payment_term.id,
            currency_id=self.currency_usd_id,
        )

        payment=self.env['account.payment'].create({
            'date':time.strftime('%Y')+'-07-15',
            'payment_type':'inbound',
            'payment_method_id':self.env.ref('account.account_payment_method_manual_in').id,
            'partner_type':'customer',
            'partner_id':self.partner_agrolait_id,
            'amount':25,
            'currency_id':self.currency_usd_id,
            'journal_id':self.bank_journal_usd.id,
        })
        payment.action_post()

        receivable_line=payment.line_ids.filtered('credit')
        invoice.js_assign_outstanding_line(receivable_line.id)

        self.assertTrue(receivable_line.matched_debit_ids)

    deftest_reconciliation_with_currency(self):
        #reconciliationonanaccounthavingaforeigncurrencybeing
        #thesameasthecompanyone
        account_rcv=self.account_rcv
        account_rcv.currency_id=self.currency_euro_id
        aml_obj=self.env['account.move.line'].with_context(
            check_move_validity=False)
        general_move1=self.env['account.move'].create({
            'name':'general1',
            'journal_id':self.general_journal.id,
        })
        aml_obj.create({
            'name':'debit1',
            'account_id':account_rcv.id,
            'debit':11,
            'move_id':general_move1.id,
        })
        aml_obj.create({
            'name':'credit1',
            'account_id':self.account_rsa.id,
            'credit':11,
            'move_id':general_move1.id,
        })
        general_move1.action_post()
        general_move2=self.env['account.move'].create({
            'name':'general2',
            'journal_id':self.general_journal.id,
        })
        aml_obj.create({
            'name':'credit2',
            'account_id':account_rcv.id,
            'credit':10,
            'move_id':general_move2.id,
        })
        aml_obj.create({
            'name':'debit2',
            'account_id':self.account_rsa.id,
            'debit':10,
            'move_id':general_move2.id,
        })
        general_move2.action_post()
        general_move3=self.env['account.move'].create({
            'name':'general3',
            'journal_id':self.general_journal.id,
        })
        aml_obj.create({
            'name':'credit3',
            'account_id':account_rcv.id,
            'credit':1,
            'move_id':general_move3.id,
        })
        aml_obj.create({
            'name':'debit3',
            'account_id':self.account_rsa.id,
            'debit':1,
            'move_id':general_move3.id,
        })
        general_move3.action_post()
        to_reconcile=((general_move1+general_move2+general_move3)
            .mapped('line_ids')
            .filtered(lambdal:l.account_id.id==account_rcv.id))
        to_reconcile.reconcile()
        foramlinto_reconcile:
            self.assertEqual(aml.amount_residual,0.0)

    deftest_inv_refund_foreign_payment_writeoff_domestic2(self):
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.110600, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':self.company.id
        })
        inv1=self.create_invoice(invoice_amount=800,currency_id=self.currency_usd_id)
        inv2=self.create_invoice(move_type="out_refund",invoice_amount=400,currency_id=self.currency_usd_id)

        payment=self.env['account.payment'].create({
            'date':time.strftime('%Y')+'-07-15',
            'payment_method_id':self.inbound_payment_method.id,
            'payment_type':'inbound',
            'partner_type':'customer',
            'partner_id':inv1.partner_id.id,
            'amount':200.00,
            'journal_id':self.bank_journal_euro.id,
            'company_id':company.id,
        })
        payment.action_post()

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        inv2_receivable=inv2.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        pay_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        move_balance=self.env['account.move'].create({
            'partner_id':inv1.partner_id.id,
            'date':time.strftime('%Y')+'-07-01',
            'journal_id':self.bank_journal_euro.id,
            'line_ids':[
                (0,False,{'credit':160.16,'account_id':inv1_receivable.account_id.id,'name':'BalanceWriteOff'}),
                (0,False,{'debit':160.16,'account_id':self.diff_expense_account.id,'name':'BalanceWriteOff'}),
            ]
        })

        move_balance.action_post()
        move_balance_receiv=move_balance.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        (inv1_receivable+inv2_receivable+pay_receivable+move_balance_receiv).reconcile()

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,inv2_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,pay_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,move_balance_receiv.full_reconcile_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
        self.assertEqual(inv2.payment_state,'paid')

    deftest_inv_refund_foreign_payment_writeoff_domestic3(self):
        """
                    Receivable
                Domestic(Foreign)
        592.47(658.00)|                   INV1 >Doneinforeign
                        |  202.59(225.00) INV2 >Doneinforeign
                        |  372.10(413.25) PAYMENT>Doneindomestic(the413.25isvirtual,nonstored)
                        |   17.78 (19.75) WriteOff>Doneindomestic(the19.75isvirtual,nonstored)
        Reconciliationshouldbefull
        Invoicesshouldbemarkedaspaid
        """
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.110600, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })
        inv1=self.create_invoice(invoice_amount=658,currency_id=self.currency_usd_id)
        inv2=self.create_invoice(move_type="out_refund",invoice_amount=225,currency_id=self.currency_usd_id)

        payment=self.env['account.payment'].create({
            'payment_method_id':self.inbound_payment_method.id,
            'payment_type':'inbound',
            'partner_type':'customer',
            'partner_id':inv1.partner_id.id,
            'amount':372.10,
            'date':time.strftime('%Y')+'-07-01',
            'journal_id':self.bank_journal_euro.id,
            'company_id':company.id,
        })
        payment.action_post()

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        inv2_receivable=inv2.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        pay_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        move_balance=self.env['account.move'].create({
            'partner_id':inv1.partner_id.id,
            'date':time.strftime('%Y')+'-07-01',
            'journal_id':self.bank_journal_euro.id,
            'line_ids':[
                (0,False,{'credit':17.78,'account_id':inv1_receivable.account_id.id,'name':'BalanceWriteOff'}),
                (0,False,{'debit':17.78,'account_id':self.diff_expense_account.id,'name':'BalanceWriteOff'}),
            ]
        })

        move_balance.action_post()
        move_balance_receiv=move_balance.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        (inv1_receivable+inv2_receivable+pay_receivable+move_balance_receiv).reconcile()

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,inv2_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,pay_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,move_balance_receiv.full_reconcile_id)

        self.assertFalse(inv1_receivable.full_reconcile_id.exchange_move_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
        self.assertEqual(inv2.payment_state,'paid')

    deftest_inv_refund_foreign_payment_writeoff_domestic4(self):
        """
                    Receivable
                Domestic(Foreign)
        658.00(658.00)|                   INV1 >Doneinforeign
                        |  202.59(225.00) INV2 >Doneinforeign
                        |  372.10(413.25) PAYMENT>Doneindomestic(the413.25isvirtual,nonstored)
                        |   83.31 (92.52) WriteOff>Doneindomestic(the92.52isvirtual,nonstored)
        Reconciliationshouldbefull
        Invoicesshouldbemarkedaspaid
        """
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-15',
            'rate':1.110600, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })
        inv1=self._create_invoice(invoice_amount=658,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-01',auto_validate=True)
        inv2=self._create_invoice(move_type="out_refund",invoice_amount=225,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)

        payment=self.env['account.payment'].create({
            'date':time.strftime('%Y')+'-07-15',
            'payment_method_id':self.inbound_payment_method.id,
            'payment_type':'inbound',
            'partner_type':'customer',
            'partner_id':inv1.partner_id.id,
            'amount':372.10,
            'journal_id':self.bank_journal_euro.id,
            'company_id':company.id,
            'currency_id':self.currency_euro_id,
        })
        payment.action_post()

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        inv2_receivable=inv2.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        pay_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertEqual(inv1_receivable.balance,658)
        self.assertEqual(inv2_receivable.balance,-202.59)
        self.assertEqual(pay_receivable.balance,-372.1)

        move_balance=self.env['account.move'].create({
            'partner_id':inv1.partner_id.id,
            'date':time.strftime('%Y')+'-07-15',
            'journal_id':self.bank_journal_usd.id,
            'line_ids':[
                (0,False,{'credit':83.31,'account_id':inv1_receivable.account_id.id,'name':'BalanceWriteOff'}),
                (0,False,{'debit':83.31,'account_id':self.diff_expense_account.id,'name':'BalanceWriteOff'}),
            ]
        })

        move_balance.action_post()
        move_balance_receiv=move_balance.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        (inv1_receivable+inv2_receivable+pay_receivable+move_balance_receiv).reconcile()

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,inv2_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,pay_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,move_balance_receiv.full_reconcile_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
        self.assertEqual(inv2.payment_state,'paid')

    deftest_inv_refund_foreign_payment_writeoff_domestic5(self):
        """
                    Receivable
                Domestic(Foreign)
        600.00(600.00)|                   INV1 >Doneinforeign
                        |  250.00(250.00) INV2 >Doneinforeign
                        |  314.07(314.07) PAYMENT>Doneindomestic(foreignnonstored)
                        |   35.93 (60.93) WriteOff>Doneindomestic(foreignnonstored).WriteOffisincludedinpayment
        Reconciliationshouldbefull,withoutexchangedifference
        Invoicesshouldbemarkedaspaid
        """
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })

        inv1=self._create_invoice(invoice_amount=600,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)
        inv2=self._create_invoice(move_type="out_refund",invoice_amount=250,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        inv2_receivable=inv2.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertEqual(inv1_receivable.balance,600.00)
        self.assertEqual(inv2_receivable.balance,-250)

        #partiallypaytheinvoicewiththerefund
        inv1.js_assign_outstanding_line(inv2_receivable.id)
        self.assertEqual(inv1.amount_residual,350)

        payment=self.env['account.payment.register']\
            .with_context(active_model='account.move',active_ids=inv1.ids)\
            .create({
                'payment_date':time.strftime('%Y')+'-07-15',
                'amount':314.07,
                'journal_id':self.bank_journal_euro.id,
                'currency_id':self.currency_euro_id,
                'payment_difference_handling':'reconcile',
                'writeoff_account_id':self.diff_income_account.id,
            })\
            ._create_payments()

        payment_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        self.assertEqual(payment_receivable.balance,-350)

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,inv2_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,payment_receivable.full_reconcile_id)

        self.assertFalse(inv1_receivable.full_reconcile_id.exchange_move_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
        self.assertEqual(inv2.payment_state,'paid')

    deftest_inv_refund_foreign_payment_writeoff_domestic6(self):
        """
                    Receivable
                Domestic(Foreign)
        540.25(600.00)|                   INV1 >Doneinforeign
                        |  225.10(250.00) INV2 >Doneinforeign
                        |  315.15(350.00) PAYMENT>Doneindomestic(the350.00isvirtual,nonstored)
        """
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.1106, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })
        inv1=self._create_invoice(invoice_amount=600,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)
        inv2=self._create_invoice(move_type="out_refund",invoice_amount=250,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        inv2_receivable=inv2.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertEqual(inv1_receivable.balance,540.25)
        self.assertEqual(inv2_receivable.balance,-225.10)

        #partiallypaytheinvoicewiththerefund
        inv1.js_assign_outstanding_line(inv2_receivable.id)
        self.assertAlmostEqual(inv1.amount_residual,350)
        self.assertAlmostEqual(inv1_receivable.amount_residual,315.15)

        payment=self.env['account.payment.register']\
            .with_context(active_model='account.move',active_ids=inv1.ids)\
            .create({
                'payment_date':time.strftime('%Y')+'-07-15',
                'amount':314.07,
                'journal_id':self.bank_journal_euro.id,
                'currency_id':self.currency_euro_id,
                'payment_difference_handling':'reconcile',
                'writeoff_account_id':self.diff_income_account.id,
            })\
            ._create_payments()

        payment_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,inv2_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,payment_receivable.full_reconcile_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
        self.assertEqual(inv2.payment_state,'paid')

    deftest_inv_refund_foreign_payment_writeoff_domestic6bis(self):
        """
        Sameasdomestic6,butonlyinforeigncurrencies
        Obviously,itshouldleadtothesamekindofresults
        Herethereisnoexchangedifferenceentrythough
        """
        foreign_0=self.env['res.currency'].create({
            'name':'foreign0',
            'symbol':'F0'
        })
        foreign_1=self.env['res.currency'].browse(self.currency_usd_id)

        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })

        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':foreign_0.id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.1106, #Don'tchangethis!
            'currency_id':foreign_1.id,
            'company_id':company.id
        })
        inv1=self._create_invoice(invoice_amount=600,currency_id=foreign_1.id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)
        inv2=self._create_invoice(move_type="out_refund",invoice_amount=250,currency_id=foreign_1.id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        inv2_receivable=inv2.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertEqual(inv1_receivable.balance,540.25)
        self.assertEqual(inv2_receivable.balance,-225.10)

        #partiallypaytheinvoicewiththerefund
        inv1.js_assign_outstanding_line(inv2_receivable.id)
        self.assertAlmostEqual(inv1.amount_residual,350)
        self.assertAlmostEqual(inv1_receivable.amount_residual,315.15)

        payment=self.env['account.payment.register']\
            .with_context(active_model='account.move',active_ids=inv1.ids)\
            .create({
                'payment_date':time.strftime('%Y')+'-07-15',
                'amount':314.07,
                'journal_id':self.bank_journal_euro.id,
                'currency_id':foreign_0.id,
                'payment_difference_handling':'reconcile',
                'writeoff_account_id':self.diff_income_account.id,
            })\
            ._create_payments()

        payment_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,inv2_receivable.full_reconcile_id)
        self.assertEqual(inv1_receivable.full_reconcile_id,payment_receivable.full_reconcile_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
        self.assertEqual(inv2.payment_state,'paid')

    deftest_inv_refund_foreign_payment_writeoff_domestic7(self):
        """
                    Receivable
                Domestic(Foreign)
        5384.48(5980.00)|                     INV1 >Doneinforeign
                          |  5384.43(5979.95) PAYMENT>Doneindomestic(foreignnonstored)
                          |     0.05   (0.00) WriteOff>Doneindomestic(foreignnonstored).WriteOffisincludedinpayment,
                                                                so,theamountincurrencyisirrelevant
        Reconciliationshouldbefull,withoutexchangedifference
        Invoicesshouldbemarkedaspaid
        """
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.1106, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })
        inv1=self._create_invoice(invoice_amount=5980,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertAlmostEqual(inv1_receivable.balance,5384.48)

        payment=self.env['account.payment.register']\
            .with_context(active_model='account.move',active_ids=inv1.ids)\
            .create({
                'payment_date':time.strftime('%Y')+'-07-15',
                'amount':5384.43,
                'journal_id':self.bank_journal_euro.id,
                'currency_id':self.currency_euro_id,
                'payment_difference_handling':'reconcile',
                'writeoff_account_id':self.diff_income_account.id,
            })\
            ._create_payments()

        payment_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,payment_receivable.full_reconcile_id)

        self.assertFalse(inv1_receivable.full_reconcile_id.exchange_move_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")

    deftest_inv_refund_foreign_payment_writeoff_domestic8(self):
        """
        Roughlythesameas*_domestic7
        Thoughitsimulatesgoingthroughthereconciliationwidget
        BecausetheWriteOffisonadifferentlinethanthepayment
        """
        company=self.company
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.0,
            'currency_id':self.currency_euro_id,
            'company_id':company.id
        })
        self.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-07-01',
            'rate':1.1106, #Don'tchangethis!
            'currency_id':self.currency_usd_id,
            'company_id':company.id
        })
        inv1=self._create_invoice(invoice_amount=5980,currency_id=self.currency_usd_id,date_invoice=time.strftime('%Y')+'-07-15',auto_validate=True)

        inv1_receivable=inv1.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        self.assertAlmostEqual(inv1_receivable.balance,5384.48)

        Payment=self.env['account.payment']
        payment=Payment.create({
            'date':time.strftime('%Y')+'-07-15',
            'payment_method_id':self.inbound_payment_method.id,
            'payment_type':'inbound',
            'partner_type':'customer',
            'partner_id':inv1.partner_id.id,
            'amount':5384.43,
            'journal_id':self.bank_journal_euro.id,
            'company_id':company.id,
            'currency_id':self.currency_euro_id,
        })
        payment.action_post()
        payment_receivable=payment.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        move_balance=self.env['account.move'].create({
            'partner_id':inv1.partner_id.id,
            'date':time.strftime('%Y')+'-07-15',
            'journal_id':self.bank_journal_usd.id,
            'line_ids':[
                (0,False,{'credit':0.05,'account_id':inv1_receivable.account_id.id,'name':'BalanceWriteOff'}),
                (0,False,{'debit':0.05,'account_id':self.diff_expense_account.id,'name':'BalanceWriteOff'}),
            ]
        })
        move_balance.action_post()
        move_balance_receiv=move_balance.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        (inv1_receivable+payment_receivable+move_balance_receiv).reconcile()

        self.assertTrue(inv1_receivable.full_reconcile_id.exists())
        self.assertEqual(inv1_receivable.full_reconcile_id,payment_receivable.full_reconcile_id)
        self.assertEqual(move_balance_receiv.full_reconcile_id,inv1_receivable.full_reconcile_id)

        self.assertTrue(inv1.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")
