#-*-coding:utf-8-*-
fromfreezegunimportfreeze_time

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.tests.commonimportForm
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestReconciliationMatchingRules(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #################
        #Companysetup#
        #################
        cls.currency_data_2=cls.setup_multi_currency_data({
            'name':'DarkChocolateCoin',
            'symbol':'🍫',
            'currency_unit_label':'DarkChoco',
            'currency_subunit_label':'DarkCacaoPowder',
        },rate2016=10.0,rate2017=20.0)

        cls.company=cls.company_data['company']

        cls.account_pay=cls.company_data['default_account_payable']
        cls.current_assets_account=cls.env['account.account'].search([
            ('user_type_id','=',cls.env.ref('account.data_account_type_current_assets').id),
            ('company_id','=',cls.company.id)],limit=1)

        cls.bank_journal=cls.env['account.journal'].search([('type','=','bank'),('company_id','=',cls.company.id)],limit=1)
        cls.cash_journal=cls.env['account.journal'].search([('type','=','cash'),('company_id','=',cls.company.id)],limit=1)

        cls.tax21=cls.env['account.tax'].create({
            'name':'21%',
            'type_tax_use':'purchase',
            'amount':21,
        })

        cls.tax12=cls.env['account.tax'].create({
            'name':'12%',
            'type_tax_use':'purchase',
            'amount':12,
        })

        cls.partner_1=cls.env['res.partner'].create({'name':'partner_1','company_id':cls.company.id})
        cls.partner_2=cls.env['res.partner'].create({'name':'partner_2','company_id':cls.company.id})
        cls.partner_3=cls.env['res.partner'].create({'name':'partner_3','company_id':cls.company.id})

        ###############
        #Rulessetup#
        ###############
        cls.rule_1=cls.env['account.reconcile.model'].create({
            'name':'InvoicesMatchingRule',
            'sequence':'1',
            'rule_type':'invoice_matching',
            'auto_reconcile':False,
            'match_nature':'both',
            'match_same_currency':True,
            'match_total_amount':True,
            'match_total_amount_param':100,
            'match_partner':True,
            'match_partner_ids':[(6,0,(cls.partner_1+cls.partner_2+cls.partner_3).ids)],
            'company_id':cls.company.id,
            'line_ids':[(0,0,{'account_id':cls.current_assets_account.id})],
        })
        cls.rule_2=cls.env['account.reconcile.model'].create({
            'name':'write-offmodel',
            'rule_type':'writeoff_suggestion',
            'match_partner':True,
            'match_partner_ids':[],
            'line_ids':[(0,0,{'account_id':cls.current_assets_account.id})],
        })

        ##################
        #Invoicessetup#
        ##################
        cls.invoice_line_1=cls._create_invoice_line(100,cls.partner_1,'out_invoice')
        cls.invoice_line_2=cls._create_invoice_line(200,cls.partner_1,'out_invoice')
        cls.invoice_line_3=cls._create_invoice_line(300,cls.partner_1,'in_refund',name="RBILL/2019/09/0013")
        cls.invoice_line_4=cls._create_invoice_line(1000,cls.partner_2,'in_invoice')
        cls.invoice_line_5=cls._create_invoice_line(600,cls.partner_3,'out_invoice')
        cls.invoice_line_6=cls._create_invoice_line(600,cls.partner_3,'out_invoice',ref="RF123456")
        cls.invoice_line_7=cls._create_invoice_line(200,cls.partner_3,'out_invoice',pay_reference="RF123456")

        ####################
        #Statementssetup#
        ####################
        #TODO:account_number,partner_name,transaction_type,narration
        invoice_number=cls.invoice_line_1.move_id.name
        cls.bank_st,cls.bank_st_2,cls.cash_st=cls.env['account.bank.statement'].create([
            {
                'name':'testbankjournal',
                'journal_id':cls.bank_journal.id,
                'line_ids':[
                    (0,0,{
                        'date':'2020-01-01',
                        'payment_ref':'invoice%s-%s-%s'%tuple(invoice_number.split('/')[1:]),
                        'partner_id':cls.partner_1.id,
                        'amount':100,
                        'sequence':1,
                    }),
                    (0,0,{
                        'date':'2020-01-01',
                        'payment_ref':'xxxxx',
                        'partner_id':cls.partner_1.id,
                        'amount':600,
                        'sequence':2,
                    }),
                ],
            },{
                'name':'secondtestbankjournal',
                'journal_id':cls.bank_journal.id,
                'line_ids':[
                    (0,0,{
                        'date':'2020-01-01',
                        'payment_ref':'nawak',
                        'narration':'Communication:RF123456',
                        'partner_id':cls.partner_3.id,
                        'amount':600,
                        'sequence':1,
                    }),
                    (0,0,{
                        'date':'2020-01-01',
                        'payment_ref':'RF123456',
                        'partner_id':cls.partner_3.id,
                        'amount':600,
                        'sequence':2,
                    }),
                    (0,0,{
                        'date':'2020-01-01',
                        'payment_ref':'baaaaah',
                        'ref':'RF123456',
                        'partner_id':cls.partner_3.id,
                        'amount':600,
                        'sequence':2,
                    }),
                ],
            },{
                'name':'testcashjournal',
                'journal_id':cls.cash_journal.id,
                'line_ids':[
                    (0,0,{
                        'date':'2020-01-01',
                        'payment_ref':'yyyyy',
                        'partner_id':cls.partner_2.id,
                        'amount':-1000,
                        'sequence':1,
                    }),
                ],
            }
        ])

        cls.bank_line_1,cls.bank_line_2=cls.bank_st.line_ids
        cls.bank_line_3,cls.bank_line_4,cls.bank_line_5=cls.bank_st_2.line_ids
        cls.cash_line_1=cls.cash_st.line_ids
        cls._post_statements(cls)

    @classmethod
    def_create_invoice_line(cls,amount,partner,type,currency=None,pay_reference=None,ref=None,name=None):
        '''Createaninvoiceonthefly.'''
        invoice_form=Form(cls.env['account.move'].with_context(default_move_type=type,default_invoice_date='2019-09-01',default_date='2019-09-01'))
        invoice_form.partner_id=partner
        ifcurrency:
            invoice_form.currency_id=currency
        ifpay_reference:
            invoice_form.payment_reference=pay_reference
        ifref:
            invoice_form.ref=ref
        ifname:
            invoice_form.name=name
        withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
            invoice_line_form.name='xxxx'
            invoice_line_form.quantity=1
            invoice_line_form.price_unit=amount
            invoice_line_form.tax_ids.clear()
        invoice=invoice_form.save()
        invoice.action_post()
        lines=invoice.line_ids
        returnlines.filtered(lambdal:l.account_id.user_type_id.typein('receivable','payable'))

    def_post_statements(self):
        self.bank_st.balance_end_real=self.bank_st.balance_end
        self.bank_st_2.balance_end_real=self.bank_st_2.balance_end
        self.cash_st.balance_end_real=self.cash_st.balance_end
        (self.bank_st+self.bank_st_2+self.cash_st).button_post()

    @freeze_time('2020-01-01')
    def_check_statement_matching(self,rules,expected_values,statements=None):
        ifstatementsisNone:
            statements=self.bank_st+self.cash_st
        statement_lines=statements.mapped('line_ids').sorted()
        matching_values=rules._apply_rules(statement_lines,None)

        forst_line_id,valuesinmatching_values.items():
            values.pop('reconciled_lines',None)
            values.pop('write_off_vals',None)
            self.assertDictEqual(values,expected_values[st_line_id])

    deftest_matching_fields(self):
        #Checkwithoutrestriction.
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_2.id,
                self.invoice_line_3.id,
                self.invoice_line_1.id,
            ],'model':self.rule_1,
               'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })

    deftest_matching_fields_match_text_location(self):
        self.rule_1.match_text_location_label=True
        self.rule_1.match_text_location_reference=False
        self.rule_1.match_text_location_note=False
        self._check_statement_matching(self.rule_1,{
            self.bank_line_3.id:{'aml_ids':[self.invoice_line_5.id],'model':self.rule_1,'partner':self.bank_line_3.partner_id},
            self.bank_line_4.id:{'aml_ids':[self.invoice_line_7.id],'model':self.rule_1,'partner':self.bank_line_4.partner_id},
            self.bank_line_5.id:{'aml_ids':[self.invoice_line_6.id],'model':self.rule_1,'partner':self.bank_line_5.partner_id},
        },statements=self.bank_st_2)

        self.rule_1.match_text_location_label=True
        self.rule_1.match_text_location_reference=False
        self.rule_1.match_text_location_note=True
        self._check_statement_matching(self.rule_1,{
            self.bank_line_3.id:{'aml_ids':[self.invoice_line_6.id],'model':self.rule_1,'partner':self.bank_line_3.partner_id},
            self.bank_line_4.id:{'aml_ids':[self.invoice_line_7.id],'model':self.rule_1,'partner':self.bank_line_4.partner_id},
            self.bank_line_5.id:{'aml_ids':[self.invoice_line_5.id],'model':self.rule_1,'partner':self.bank_line_5.partner_id},
        },statements=self.bank_st_2)

        self.rule_1.match_text_location_label=True
        self.rule_1.match_text_location_reference=True
        self.rule_1.match_text_location_note=False
        self._check_statement_matching(self.rule_1,{
            self.bank_line_3.id:{'aml_ids':[self.invoice_line_5.id],'model':self.rule_1,'partner':self.bank_line_3.partner_id},
            self.bank_line_4.id:{'aml_ids':[self.invoice_line_7.id],'model':self.rule_1,'partner':self.bank_line_4.partner_id},
            self.bank_line_5.id:{'aml_ids':[self.invoice_line_7.id],'model':self.rule_1,'partner':self.bank_line_5.partner_id},
        },statements=self.bank_st_2)

        self.rule_1.match_text_location_label=True
        self.rule_1.match_text_location_reference=True
        self.rule_1.match_text_location_note=True
        self._check_statement_matching(self.rule_1,{
            self.bank_line_3.id:{'aml_ids':[self.invoice_line_6.id],'model':self.rule_1,'partner':self.bank_line_3.partner_id},
            self.bank_line_4.id:{'aml_ids':[self.invoice_line_7.id],'model':self.rule_1,'partner':self.bank_line_4.partner_id},
            self.bank_line_5.id:{'aml_ids':[self.invoice_line_7.id],'model':self.rule_1,'partner':self.bank_line_5.partner_id},
        },statements=self.bank_st_2)

        self.rule_1.match_text_location_label=False
        self.rule_1.match_text_location_reference=False
        self.rule_1.match_text_location_note=False
        self._check_statement_matching(self.rule_1,{
            self.bank_line_3.id:{'aml_ids':[self.invoice_line_5.id],'model':self.rule_1,'partner':self.bank_line_3.partner_id},
            self.bank_line_4.id:{'aml_ids':[self.invoice_line_5.id],'model':self.rule_1,'partner':self.bank_line_4.partner_id},
            self.bank_line_5.id:{'aml_ids':[self.invoice_line_6.id],'model':self.rule_1,'partner':self.bank_line_5.partner_id},
        },statements=self.bank_st_2)

    deftest_matching_fields_match_text_location_no_partner(self):
        self.bank_line_2.unlink()#Onelineisenoughforthistest
        self.bank_line_1.partner_id=None

        self.partner_1.name="BernardGagnant"

        self.rule_1.write({
            'match_partner':False,
            'match_partner_ids':[(5,0,0)],
            'line_ids':[(5,0,0)],
        })

        st_line_initial_vals={'ref':None,'payment_ref':'nothing','narration':None}
        recmod_initial_vals={'match_text_location_label':False,'match_text_location_note':False,'match_text_location_reference':False}

        rec_mod_options_to_fields={
            'match_text_location_label':'payment_ref',
            'match_text_location_note':'narration',
            'match_text_location_reference':'ref',
        }

        forrec_mod_field,st_line_fieldinrec_mod_options_to_fields.items():
            self.rule_1.write({**recmod_initial_vals,rec_mod_field:True})
            #Fullyreinitializethestatementline
            self.bank_line_1.write(st_line_initial_vals)

            #Nothingshouldmatch
            self._check_statement_matching(self.rule_1,{
                self.bank_line_1.id:{'aml_ids':[]},
            },statements=self.bank_st)

            #Testmatchingwiththeinvoiceref
            self.bank_line_1.write({st_line_field:self.invoice_line_1.move_id.payment_reference})

            self._check_statement_matching(self.rule_1,{
                self.bank_line_1.id:{'aml_ids':self.invoice_line_1.ids,'model':self.rule_1,'partner':self.env['res.partner']},
            },statements=self.bank_st)

            #Testmatchingwiththepartnername(reinitializingthestatementlinefirst)
            self.bank_line_1.write({**st_line_initial_vals,st_line_field:self.partner_1.name})

            self._check_statement_matching(self.rule_1,{
                self.bank_line_1.id:{'aml_ids':self.invoice_line_1.ids,'model':self.rule_1,'partner':self.env['res.partner']},
            },statements=self.bank_st)

    deftest_matching_fields_match_journal_ids(self):
        self.rule_1.match_journal_ids|=self.cash_st.journal_id
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_journal_ids|=self.bank_st.journal_id+self.cash_st.journal_id

    deftest_matching_fields_match_nature(self):
        self.rule_1.match_nature='amount_received'
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_2.id,
                self.invoice_line_3.id,
                self.invoice_line_1.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[]},
        })
        self.rule_1.match_nature='amount_paid'
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_nature='both'

    deftest_matching_fields_match_amount(self):
        self.rule_1.match_amount='lower'
        self.rule_1.match_amount_max=150
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[]},
        })
        self.rule_1.match_amount='greater'
        self.rule_1.match_amount_min=200
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_1.id,
                self.invoice_line_2.id,
                self.invoice_line_3.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_amount='between'
        self.rule_1.match_amount_min=200
        self.rule_1.match_amount_max=800
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_1.id,
                self.invoice_line_2.id,
                self.invoice_line_3.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[]},
        })
        self.rule_1.match_amount=False

    deftest_matching_fields_match_label(self):
        self.rule_1.match_label='contains'
        self.rule_1.match_label_param='yyyyy'
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_label='not_contains'
        self.rule_1.match_label_param='xxxxx'
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_label='match_regex'
        self.rule_1.match_label_param='xxxxx|yyyyy'
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_1.id,
                self.invoice_line_2.id,
                self.invoice_line_3.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_label=False

    deftest_matching_fields_match_total_amount(self):
        #Checkmatch_total_amount:lineamount>=totalresidualamount.
        self.rule_1.match_total_amount_param=90.0
        self.bank_line_1.amount+=10
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'status':'write_off','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_2.id,
                self.invoice_line_3.id,
                self.invoice_line_1.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_total_amount_param=100.0
        self.bank_line_1.amount-=10

        #Checkmatch_total_amount:lineamount<=totalresidualamount.
        self.rule_1.match_total_amount_param=90.0
        self.bank_line_1.amount-=10
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'status':'write_off','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_2.id,
                self.invoice_line_3.id,
                self.invoice_line_1.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_total_amount_param=100.0
        self.bank_line_1.amount+=10

        #Checkmatch_total_amount:lineamount>=totalresidualamount,match_total_amount_paramjustnotmatched.
        self.rule_1.match_total_amount_param=90.0
        self.bank_line_1.amount+=10.01
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_1.id,
                self.invoice_line_2.id,
                self.invoice_line_3.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_total_amount_param=100.0
        self.bank_line_1.amount-=10.01

        #Checkmatch_total_amount:lineamount<=totalresidualamount,match_total_amount_paramjustnotmatched.
        self.rule_1.match_total_amount_param=90.0
        self.bank_line_1.amount-=10.01
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_1.id,
                self.invoice_line_2.id,
                self.invoice_line_3.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_total_amount_param=100.0
        self.bank_line_1.amount+=10.01

    deftest_matching_fields_match_partner_category_ids(self):
        test_category=self.env['res.partner.category'].create({'name':'ConsultingServices'})
        test_category2=self.env['res.partner.category'].create({'name':'ConsultingServices2'})

        self.partner_2.category_id=test_category+test_category2
        self.rule_1.match_partner_category_ids|=test_category
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[]},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })
        self.rule_1.match_partner_category_ids=False

    deftest_mixin_rules(self):
        '''Testusageofrulestogether.'''
        #rule_1isusedbeforerule_2.
        self.rule_1.sequence=1
        self.rule_2.sequence=2

        self._check_statement_matching(self.rule_1+self.rule_2,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[
                self.invoice_line_2.id,
                self.invoice_line_3.id,
                self.invoice_line_1.id,
            ],'model':self.rule_1,'partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })

        #rule_2isusedbeforerule_1.
        self.rule_1.sequence=2
        self.rule_2.sequence=1

        self._check_statement_matching(self.rule_1+self.rule_2,{
            self.bank_line_1.id:{'aml_ids':[],'model':self.rule_2,'status':'write_off','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[],'model':self.rule_2,'status':'write_off','partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[],'model':self.rule_2,'status':'write_off','partner':self.cash_line_1.partner_id},
        })

        #rule_2isusedbeforerule_1butonlyonpartner_1.
        self.rule_2.match_partner_ids|=self.partner_1

        self._check_statement_matching(self.rule_1+self.rule_2,{
            self.bank_line_1.id:{'aml_ids':[],'model':self.rule_2,'status':'write_off','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[],'model':self.rule_2,'status':'write_off','partner':self.bank_line_2.partner_id},
            self.cash_line_1.id:{'aml_ids':[self.invoice_line_4.id],'model':self.rule_1,'partner':self.cash_line_1.partner_id},
        })

    deftest_auto_reconcile(self):
        '''Testautoreconciliation.'''
        self.bank_line_1.amount+=5

        self.rule_1.sequence=2
        self.rule_1.auto_reconcile=True
        self.rule_1.match_total_amount_param=90
        self.rule_2.sequence=1
        self.rule_2.match_partner_ids|=self.partner_2
        self.rule_2.auto_reconcile=True

        self._check_statement_matching(self.rule_1+self.rule_2,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'status':'reconciled','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
            self.cash_line_1.id:{'aml_ids':[],'model':self.rule_2,'status':'reconciled','partner':self.cash_line_1.partner_id},
        })

        #Checkfirstlinehasbeenwellreconciled.
        self.assertRecordValues(self.bank_line_1.line_ids,[
            {'partner_id':self.partner_1.id,'debit':105.0,'credit':0.0},
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':5.0},
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':100.0},
        ])

        #Checksecondlinehasbeenwellreconciled.
        self.assertRecordValues(self.cash_line_1.line_ids,[
            {'partner_id':self.partner_2.id,'debit':0.0,'credit':1000.0},
            {'partner_id':self.partner_2.id,'debit':1000.0,'credit':0.0},
        ])

    deftest_larger_invoice_auto_reconcile(self):
        '''Testautoreconciliationwithaninvoicewithlargeramountthanthe
        statementline's,forruleswithoutwrite-offs.'''
        self.bank_line_1.amount=40
        self.invoice_line_1.move_id.payment_reference=self.bank_line_1.payment_ref

        self.rule_1.sequence=2
        self.rule_1.auto_reconcile=True
        self.rule_1.line_ids=[(5,0,0)]

        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'status':'reconciled','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },statements=self.bank_st)

        #Checkfirstlinehasbeenwellreconciled.
        self.assertRecordValues(self.bank_line_1.line_ids,[
            {'partner_id':self.partner_1.id,'debit':40.0,'credit':0.0},
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':40.0},
        ])

        self.assertEqual(self.invoice_line_1.amount_residual,60.0,"Theinvoiceshouldhavebeenpartiallyreconciled")

    deftest_auto_reconcile_with_duplicate_match(self):
        """Ifmultiplebankstatementlinesmatchwiththesameinvoice,ensurethe
         correctlineisauto-validatedandnocrashinghappens.
        """

        #Onlytheinvoicedefinedinthistestshouldhavethispartner
        partner=self.env['res.partner'].create({'name':"TheOnlyOne"})
        invoice_line=self._create_invoice_line(
            2000,partner,'out_invoice',ref="REF7788")

        #Enableauto-validationanddon'trestrictthepartnersthatcanbematchedon
        #soournewlycreatedpartnercanbematched.
        self.rule_1.write({
            'auto_reconcile':True,
            'match_partner_ids':[(5,0,0)],
        })
        self.rule_1.match_partner_ids=[]

        #Thislinehasamatchingpaymentreferenceandtheexactamountofthe
        #invoice.Asaresultitshouldauto-validate.
        self.bank_line_1.amount=2000
        self.bank_line_1.partner_id=partner
        self.bank_line_1.payment_ref="REF7788"

        #Thislinedoesn'thaveamatchingamountorreference,butitdoeshavea
        #matchingpartner.
        self.bank_line_2.amount=1800
        self.bank_line_2.partner_id=partner
        self.bank_line_2.payment_ref="something"

        #Verifytheauto-validationhappenswiththefirstline,andnoexceptions.
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{
                'aml_ids':[invoice_line.id],
                'model':self.rule_1,
                'status':'reconciled',
                'partner':self.bank_line_1.partner_id
            },
            self.bank_line_2.id:{
                'aml_ids':[]
            },
        },statements=self.bank_st)

    deftest_auto_reconcile_with_tax(self):
        '''Testautoreconciliationwithataxamountincludedinthebankstatementline'''
        self.rule_1.write({
            'auto_reconcile':True,
            'rule_type':'writeoff_suggestion',
            'line_ids':[(1,self.rule_1.line_ids.id,{
                'amount':50,
                'force_tax_included':True,
                'tax_ids':[(6,0,self.tax21.ids)],
            }),(0,0,{
                'amount':100,
                'force_tax_included':False,
                'tax_ids':[(6,0,self.tax12.ids)],
                'account_id':self.current_assets_account.id,
            })]
        })

        self.bank_line_1.amount=-121

        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[],'model':self.rule_1,'status':'reconciled','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[],'model':self.rule_1,'status':'reconciled','partner':self.bank_line_2.partner_id},
        },statements=self.bank_st)

        #Checkfirstlinehasbeenwellreconciled.
        self.assertRecordValues(self.bank_line_1.line_ids,[
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':121.0,'tax_ids':[],'tax_line_id':False},
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':7.26,'tax_ids':[],'tax_line_id':False},
            {'partner_id':self.partner_1.id,'debit':50.0,'credit':0.0,'tax_ids':[self.tax21.id],'tax_line_id':False},
            {'partner_id':self.partner_1.id,'debit':10.5,'credit':0.0,'tax_ids':[],'tax_line_id':self.tax21.id},
            {'partner_id':self.partner_1.id,'debit':60.5,'credit':0.0,'tax_ids':[self.tax12.id],'tax_line_id':False},
            {'partner_id':self.partner_1.id,'debit':7.26,'credit':0.0,'tax_ids':[],'tax_line_id':self.tax12.id},
        ])

    deftest_reverted_move_matching(self):
        partner=self.partner_1
        AccountMove=self.env['account.move']
        move=AccountMove.create({
            'journal_id':self.bank_journal.id,
            'line_ids':[
                (0,0,{
                    'account_id':self.account_pay.id,
                    'partner_id':partner.id,
                    'name':'Oneofthesedays',
                    'debit':10,
                }),
                (0,0,{
                    'account_id':self.bank_journal.payment_credit_account_id.id,
                    'partner_id':partner.id,
                    'name':'I\'mgonnacutyouintolittlepieces',
                    'credit':10,
                })
            ],
        })

        payment_bnk_line=move.line_ids.filtered(lambdal:l.account_id==self.bank_journal.payment_credit_account_id)

        move.action_post()
        move_reversed=move._reverse_moves()
        self.assertTrue(move_reversed.exists())

        self.bank_line_1.write({
            'payment_ref':'8',
            'partner_id':partner.id,
            'amount':-10,
        })
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[payment_bnk_line.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },statements=self.bank_st)

    deftest_match_different_currencies(self):
        partner=self.env['res.partner'].create({'name':'BernardGagnant'})
        self.rule_1.write({'match_partner_ids':[(6,0,partner.ids)],'match_same_currency':False})

        currency_inv=self.env.ref('base.EUR')
        currency_statement=self.env.ref('base.JPY')

        currency_statement.active=True

        invoice_line=self._create_invoice_line(100,partner,'out_invoice',currency=currency_inv)

        self.bank_line_1.write({'partner_id':partner.id,'foreign_currency_id':currency_statement.id,'amount_currency':100,'payment_ref':'test'})
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':invoice_line.ids,'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },statements=self.bank_st)

    deftest_auto_reconcile_with_tax_and_foreign_currency(self):
        '''Testautoreconciliationofabankstatementinforeigncurrencyjournalwithtaxincounterpartvalues'''

        currency_statement=self.currency_data_2['currency']

        journal=self.env['account.journal'].create({
            'name':'test_match_multi_currencies',
            'code':'xxxx',
            'type':'bank',
            'currency_id':currency_statement.id,
        })

        self.rule_1.write({
            'auto_reconcile':True,
            'rule_type':'writeoff_suggestion',
            'match_journal_ids':[(6,0,journal.ids)],
            'match_same_currency':False,
            'match_nature':'both',
            'match_partner':False,
            'match_label':'contains',
            'match_label_param':'Tournicoti', #Sothatweonlymatchwhatwewanttotest
            'line_ids':[(1,self.rule_1.line_ids.id,{
                'amount':100,
                'force_tax_included':True,
                'tax_ids':[(6,0,self.tax21.ids)],
            })]
        })

        statement=self.env['account.bank.statement'].create({
            'name':'test_match_multi_currencies',
            'journal_id':journal.id,
            'line_ids':[
                (0,0,{
                    'journal_id':journal.id,
                    'date':'2016-01-01',
                    'payment_ref':'TournicotiTest',
                    'amount':100.0,
                }),
            ],
        })
        statement_line=statement.line_ids

        statement.button_post()

        self._check_statement_matching(self.rule_1,{
            statement_line.id:{'aml_ids':[],'model':self.rule_1,'status':'reconciled','partner':self.env['res.partner']},
        },statements=statement)

        #Checkfirstlinehasbeenwellreconciled.
        self.assertRecordValues(statement_line.line_ids,[
            {'partner_id':False,'debit':10.0,'credit':0.0,'tax_ids':[],'tax_line_id':False},
            {'partner_id':False,'debit':0.0,'credit':8.26,'tax_ids':[self.tax21.id],'tax_line_id':False},
            {'partner_id':False,'debit':0.0,'credit':1.74,'tax_ids':[],'tax_line_id':self.tax21.id},
        ])

    deftest_invoice_matching_rule_no_partner(self):
        """Teststhatastatementlinewithoutanypartnercanbematchedtothe
        rightinvoiceiftheyhavethesamepaymentreference.
        """
        self.invoice_line_1.move_id.write({'payment_reference':'Tournicoti66'})

        self.bank_line_1.write({
            'payment_ref':'Tournicoti66',
            'partner_id':None,
            'amount':95,
        })

        self.rule_1.write({
            'line_ids':[(5,0,0)],
            'match_partner':False,
            'match_label':'contains',
            'match_label_param':'Tournicoti', #Sothatweonlymatchwhatwewanttotest
        })

        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },self.bank_st)

    deftest_inv_matching_rule_auto_rec_no_partner_with_writeoff(self):
        self.invoice_line_1.move_id.write({'payment_reference':'doudlidou355'})

        self.bank_line_1.write({
            'payment_ref':'doudlidou355',
            'partner_id':None,
            'amount':95,
        })

        self.rule_1.write({
            'match_partner':False,
            'match_label':'contains',
            'match_label_param':'doudlidou', #Sothatweonlymatchwhatwewanttotest
            'match_total_amount_param':90,
            'auto_reconcile':True,
        })

        #Checkbankreconciliation

        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id,'status':'reconciled'},
            self.bank_line_2.id:{'aml_ids':[]},
        },self.bank_st)

        #Checkinvoicelinehasbeenfullyreconciled,withawrite-off.
        self.assertRecordValues(self.bank_line_1.line_ids,[
            {'partner_id':self.partner_1.id,'debit':95.0,'credit':0.0,'account_id':self.bank_journal.default_account_id.id,'reconciled':False},
            {'partner_id':self.partner_1.id,'debit':5.0,'credit':0.0,'account_id':self.current_assets_account.id,'reconciled':False},
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':100.0,'account_id':self.invoice_line_1.account_id.id,'reconciled':True},
        ])

        self.assertEqual(self.invoice_line_1.amount_residual,0.0,"Theinvoiceshouldhavebeenfullyreconciled")

    deftest_partner_mapping_rule(self):
        self.bank_line_1.write({'partner_id':None,'payment_ref':'toto42','narration':None})
        self.bank_line_2.write({'partner_id':None})

        #Dothetestforbothrule1and2,sothatwecheckinvoicematchingandwrite-offrules
        forrulein(self.rule_1+self.rule_2):

            #Tocopeforminordifferencesinruleresults
            matching_amls=rule.rule_type=='invoice_matching'andself.invoice_line_1.idsor[]
            result_status=rule.rule_type=='writeoff_suggestion'and{'status':'write_off'}or{}

            match_result={**result_status,'aml_ids':matching_amls,'model':rule,'partner':self.partner_1}
            no_match_result={'aml_ids':[]}

            #Withoutmapping,thereshouldbenomatch
            self._check_statement_matching(rule,{
                self.bank_line_1.id:no_match_result,
                self.bank_line_2.id:no_match_result,
            },self.bank_st)

            #Weaddsomemappingforpaymentreferencetorule_1
            rule.write({
                'partner_mapping_line_ids':[(0,0,{
                    'partner_id':self.partner_1.id,
                    'payment_ref_regex':'toto.*',
                })]
            })

            #bank_line_1shouldnowmatch
            self._check_statement_matching(rule,{
                self.bank_line_1.id:match_result,
                self.bank_line_2.id:no_match_result,
            },self.bank_st)

            #Ifwenowaddanarrationregextothesamemappingline,nothingshouldmatch
            rule.partner_mapping_line_ids.write({'narration_regex':".*coincoin"})
            self.bank_line_1.write({'narration':None})#Resetfrompossiblepreviousiteration

            self._check_statement_matching(rule,{
                self.bank_line_1.id:no_match_result,
                self.bank_line_2.id:no_match_result,
            },self.bank_st)

            #Ifwesetthenarrationsothatitmatchesthenewmappingcriterium,line_1matches
            self.bank_line_1.write({'narration':"42coincoin"})

            self._check_statement_matching(rule,{
                self.bank_line_1.id:match_result,
                self.bank_line_2.id:no_match_result,
            },self.bank_st)

    deftest_partner_name_in_communication(self):
        self.invoice_line_1.partner_id.write({'name':"ArchibaldHaddock"})
        self.bank_line_1.write({'partner_id':None,'payment_ref':'1234//HADDOCK-Archibald'})
        self.bank_line_2.write({'partner_id':None})
        self.rule_1.write({'match_partner':False})

        #bank_line_1shouldmatch,asitscommunicationcontainstheinvoice'spartnername
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },self.bank_st)

    deftest_partner_name_with_regexp_chars(self):
        self.invoice_line_1.partner_id.write({'name':"Archibald+Haddock"})
        self.bank_line_1.write({'partner_id':None,'payment_ref':'1234//HADDOCK+Archibald'})
        self.bank_line_2.write({'partner_id':None})
        self.rule_1.write({'match_partner':False})

        #Thequeryshouldstillwork
        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },self.bank_st)

    deftest_match_multi_currencies(self):
        '''Ensurethematchingofcandidatesismadeusingtherightstatementlinecurrency.

        Inthistest,thevalueofthestatementlineis100USD=300GOL=900DARandwewanttomatchtwojournal
        itemsof:
        -100USD=200GOL(=600DARfromthestatementlinepointofview)
        -14USD=280DAR

        Bothjournalitemsshouldbesuggestedtotheuserbecausetheyrepresents98%ofthestatementlineamount
        (DAR).
        '''
        partner=self.env['res.partner'].create({'name':'BernardPerdant'})

        journal=self.env['account.journal'].create({
            'name':'test_match_multi_currencies',
            'code':'xxxx',
            'type':'bank',
            'currency_id':self.currency_data['currency'].id,
        })

        matching_rule=self.env['account.reconcile.model'].create({
            'name':'test_match_multi_currencies',
            'rule_type':'invoice_matching',
            'match_partner':True,
            'match_partner_ids':[(6,0,partner.ids)],
            'match_total_amount':True,
            'match_total_amount_param':95.0,
            'match_same_currency':False,
            'company_id':self.company_data['company'].id,
            'past_months_limit':False,
        })

        statement=self.env['account.bank.statement'].create({
            'name':'test_match_multi_currencies',
            'journal_id':journal.id,
            'line_ids':[
                (0,0,{
                    'journal_id':journal.id,
                    'date':'2016-01-01',
                    'payment_ref':'line',
                    'partner_id':partner.id,
                    'foreign_currency_id':self.currency_data_2['currency'].id,
                    'amount':300.0,           #Rateis3GOL=1USDin2016.
                    'amount_currency':900.0,  #Rateis10DAR=1USDin2016buttherateusedbythebankis9:1.
                }),
            ],
        })
        statement_line=statement.line_ids

        statement.button_post()

        move=self.env['account.move'].create({
            'move_type':'entry',
            'date':'2017-01-01',
            'journal_id':self.company_data['default_journal_misc'].id,
            'line_ids':[
                #Rateis2GOL=1USDin2017.
                #Thestatementlinewillconsiderthislineequivalentto600DAR.
                (0,0,{
                    'account_id':self.company_data['default_account_receivable'].id,
                    'partner_id':partner.id,
                    'currency_id':self.currency_data['currency'].id,
                    'debit':100.0,
                    'credit':0.0,
                    'amount_currency':200.0,
                }),
                #Rateis20GOL=1USDin2017.
                (0,0,{
                    'account_id':self.company_data['default_account_receivable'].id,
                    'partner_id':partner.id,
                    'currency_id':self.currency_data_2['currency'].id,
                    'debit':14.0,
                    'credit':0.0,
                    'amount_currency':280.0,
                }),
                #Linetobalancethejournalentry:
                (0,0,{
                    'account_id':self.company_data['default_account_revenue'].id,
                    'debit':0.0,
                    'credit':114.0,
                }),
            ],
        })
        move.action_post()

        move_line_1=move.line_ids.filtered(lambdaline:line.debit==100.0)
        move_line_2=move.line_ids.filtered(lambdaline:line.debit==14.0)

        self._check_statement_matching(matching_rule,{
            statement_line.id:{'aml_ids':(move_line_1+move_line_2).ids,'model':matching_rule,'partner':statement_line.partner_id}
        },statements=statement)

    @freeze_time('2020-01-01')
    deftest_inv_matching_with_write_off(self):
        self.rule_1.match_total_amount_param=90
        self.bank_st.line_ids[1].unlink()#Wedon'tneedthisonehere
        statement_line=self.bank_st.line_ids[0]
        statement_line.write({
            'payment_ref':self.invoice_line_1.move_id.payment_reference,
            'amount':90,
        })

        #Testtheinvoice-matchingpart
        self._check_statement_matching(self.rule_1,{
            statement_line.id:{'aml_ids':self.invoice_line_1.ids,'model':self.rule_1,'partner':self.invoice_line_1.partner_id,'status':'write_off'},
        },self.bank_st)

        #Testthewrite-offpart
        expected_write_off={
            'balance':10,
            'currency_id':self.company_data['currency'].id,
            'reconcile_model_id':self.rule_1.id,
            'account_id':self.current_assets_account.id,
        }

        matching_result=self.rule_1._apply_rules(statement_line)

        self.assertEqual(len(matching_result[statement_line.id].get('write_off_vals',[])),1,"Exactlyonewrite-offlineshouldbeproposed.")

        full_write_off_dict=matching_result[statement_line.id]['write_off_vals'][0]
        to_compare={
                key:full_write_off_dict[key]
                forkeyinexpected_write_off.keys()
        }

        self.assertDictEqual(expected_write_off,to_compare)

    deftest_inv_matching_with_write_off_autoreconcile(self):
        self.bank_line_1.amount=95

        self.rule_1.sequence=2
        self.rule_1.auto_reconcile=True
        self.rule_1.match_total_amount_param=90

        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'status':'reconciled','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[]},
        },statements=self.bank_st)

        #Checkfirstlinehasbeenproperlyreconciled.
        self.assertRecordValues(self.bank_line_1.line_ids,[
            {'partner_id':self.partner_1.id,'debit':95.0,'credit':0.0,'account_id':self.bank_journal.default_account_id.id,'reconciled':False},
            {'partner_id':self.partner_1.id,'debit':5.0,'credit':0.0,'account_id':self.current_assets_account.id,'reconciled':False},
            {'partner_id':self.partner_1.id,'debit':0.0,'credit':100.0,'account_id':self.invoice_line_1.account_id.id,'reconciled':True},
        ])

        self.assertEqual(self.invoice_line_1.amount_residual,0.0,"Theinvoiceshouldhavebeenfullyreconciled")

    deftest_avoid_amount_matching_bypass(self):
        """Bythedefault,ifthelabelofstatementlinesexactlymatchesapaymentreference,itbypassesanykindofamountverification.
        Thisisannoyinginsomesetups,soaconfigparameterwasintroducedtohandlethat.
        """
        self.env['ir.config_parameter'].set_param('account.disable_rec_models_bypass','1')
        self.rule_1.match_total_amount_param=90
        second_inv_matching_rule=self.env['account.reconcile.model'].create({
            'name':'InvoicesMatchingRule',
            'sequence':2,
            'rule_type':'invoice_matching',
            'auto_reconcile':False,
            'match_nature':'both',
            'match_same_currency':False,
            'match_total_amount':False,
            'match_partner':True,
            'company_id':self.company.id,
        })

        self.bank_line_1.write({
            'payment_ref':self.invoice_line_1.move_id.payment_reference,
            'amount':99,
        })
        self.bank_line_2.write({
            'payment_ref':self.invoice_line_2.move_id.payment_reference,
            'amount':1,
        })

        self._check_statement_matching(self.rule_1+second_inv_matching_rule,{
            self.bank_line_1.id:{'aml_ids':[self.invoice_line_1.id],'model':self.rule_1,'status':'write_off','partner':self.bank_line_1.partner_id},
            self.bank_line_2.id:{'aml_ids':[self.invoice_line_2.id],'model':second_inv_matching_rule,'partner':self.bank_line_2.partner_id}
        },statements=self.bank_st)

    deftest_payment_similar_communications(self):
        defcreate_payment_line(amount,memo,partner):
            payment=self.env['account.payment'].create({
                'amount':amount,
                'payment_type':'inbound',
                'partner_type':'customer',
                'partner_id':partner.id,
                'ref':memo,
                'destination_account_id':self.company_data['default_account_receivable'].id,
            })
            payment.action_post()

            returnpayment.line_ids.filtered(lambdax:x.account_id.user_type_id.typenotin{'receivable','payable'})

        payment_partner=self.env['res.partner'].create({
            'name':"BernardGagnant",
        })

        self.rule_1.match_partner_ids=[(6,0,payment_partner.ids)]

        pmt_line_1=create_payment_line(500,'a1b2c3',payment_partner)
        pmt_line_2=create_payment_line(500,'a1b2c3',payment_partner)
        pmt_line_3=create_payment_line(500,'d1e2f3',payment_partner)

        self.bank_line_1.write({
            'amount':1000,
            'payment_ref':'a1b2c3',
            'partner_id':payment_partner.id,
        })
        self.bank_line_2.unlink()
        self.rule_1.match_total_amount=False

        self._check_statement_matching(self.rule_1,{
            self.bank_line_1.id:{'aml_ids':(pmt_line_1+pmt_line_2).ids,'model':self.rule_1,'partner':payment_partner},
        },statements=self.bank_line_1.statement_id)

    deftest_tax_tags_inversion_with_reconciliation_model(self):
        country=self.env.ref('base.us')
        tax_report=self.env['account.tax.report'].create({
            'name':"Taxreport",
            'country_id':country.id,
        })
        tax_report_line=self.env['account.tax.report.line'].create({
            'name':'test_tax_report_line',
            'tag_name':'test_tax_report_line',
            'report_id':tax_report.id,
            'sequence':10,
        })
        tax_tag_pos=tax_report_line.tag_ids.filtered(lambdax:notx.tax_negate)
        tax_tag_neg=tax_report_line.tag_ids.filtered(lambdax:x.tax_negate)
        tax=self.env['account.tax'].create({
            'name':'TestTax',
            'amount':10,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(6,0,tax_tag_pos.ids)],
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'tag_ids':[(6,0,tax_tag_neg.ids)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(6,0,tax_tag_neg.ids)],
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'tag_ids':[(6,0,tax_tag_pos.ids)],
                }),
            ],
        })
        reconciliation_model=self.env['account.reconcile.model'].create({
            'name':'ChargewithTax',
            'line_ids':[(0,0,{
                'account_id':self.company_data['default_account_expense'].id,
                'amount_type':'percentage',
                'amount_string':'100',
                'tax_ids':[(6,0,tax.ids)]
            })]
        })
        bank_stmt=self.env['account.bank.statement'].create({
            'journal_id':self.bank_journal.id,
            'date':'2020-07-15',
            'name':'test',
            'line_ids':[(0,0,{
                'payment_ref':'testLine',
                'amount':5,
                'date':'2020-07-15',
            })]
        })
        res=reconciliation_model._get_write_off_move_lines_dict(bank_stmt.line_ids,5)
        self.assertEqual(len(res),2)
        self.assertEqual(
            res[0]['tax_tag_ids'],
            [(6,0,tax.refund_repartition_line_ids[0].tag_ids.ids)],
            'Thetagsofthefirstrepartitionlinearenotinverted'
        )
        self.assertEqual(
            res[1]['tax_tag_ids'],
            [(6,0,tax.refund_repartition_line_ids[1].tag_ids.ids)],
            'Thetagsofthesecondrepartitionlinearenotinverted'
        )

    deftest_matching_multi_currency_auto_validate(self):
        currency=self.setup_multi_currency_data(
            default_values={
                'name':'BlackChocolateCoin',
                'symbol':'🍫',
                'currency_unit_label':'BlackChoco',
                'currency_subunit_label':'BlackCacaoPowder',
            },
            rate2016=11.2674,
            rate2017=11.2674,
        )['currency']

        bank_journal=self.company_data['default_journal_bank'].copy()
        bank_journal.currency_id=currency

        invoice_line=self._create_invoice_line(100.0,self.partner_1,'out_invoice',currency=currency)

        statement=self.env['account.bank.statement'].create({
            'name':'test_matching_multi_currency_auto_validate',
            'journal_id':bank_journal.id,
            'line_ids':[
                (0,0,{
                    'journal_id':bank_journal.id,
                    'partner_id':self.partner_1.id,
                    'date':invoice_line.date,
                    'payment_ref':invoice_line.move_name,
                    'amount':invoice_line.amount_currency,
                }),
            ],
        })
        statement_line=statement.line_ids
        statement.button_post()

        matching_rule=self.env['account.reconcile.model'].create({
            'name':'test_matching_multi_currency_auto_validate',
            'rule_type':'invoice_matching',
            'match_partner':True,
            'match_partner_ids':[(6,0,self.partner_1.ids)],
            'match_total_amount':True,
            'match_total_amount_param':100.0,
            'match_same_currency':True,
            'past_months_limit':False,
            'auto_reconcile':True,
        })

        self._check_statement_matching(
            matching_rule,
            {
                statement_line.id:{
                    'aml_ids':invoice_line.ids,
                    'model':matching_rule,
                    'status':'reconciled',
                    'partner':self.partner_1,
                },
            },
            statements=statement,
        )

        self.assertRecordValues(statement_line.line_ids,[
            #pylint:disable=bad-whitespace
            {'amount_currency':100.0, 'debit':8.88, 'credit':0.0},
            {'amount_currency':-100.0,'debit':0.0,  'credit':8.88},
        ])
