#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged,new_test_user
fromflectra.tests.commonimportForm
fromflectraimportfields,api,SUPERUSER_ID
fromflectra.exceptionsimportValidationError,UserError,RedirectWarning
fromflectra.toolsimportmute_logger

fromdateutil.relativedeltaimportrelativedelta
fromfunctoolsimportreduce
importjson
importpsycopg2

fromcollectionsimportdefaultdict

@tagged('post_install','-at_install')
classTestAccountMove(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        tax_repartition_line=cls.company_data['default_tax_sale'].refund_repartition_line_ids\
            .filtered(lambdaline:line.repartition_type=='tax')
        cls.test_move=cls.env['account.move'].create({
            'move_type':'entry',
            'date':fields.Date.from_string('2016-01-01'),
            'line_ids':[
                (0,None,{
                    'name':'revenueline1',
                    'account_id':cls.company_data['default_account_revenue'].id,
                    'debit':500.0,
                    'credit':0.0,
                }),
                (0,None,{
                    'name':'revenueline2',
                    'account_id':cls.company_data['default_account_revenue'].id,
                    'debit':1000.0,
                    'credit':0.0,
                    'tax_ids':[(6,0,cls.company_data['default_tax_sale'].ids)],
                }),
                (0,None,{
                    'name':'taxline',
                    'account_id':cls.company_data['default_account_tax_sale'].id,
                    'debit':150.0,
                    'credit':0.0,
                    'tax_repartition_line_id':tax_repartition_line.id,
                }),
                (0,None,{
                    'name':'counterpartline',
                    'account_id':cls.company_data['default_account_expense'].id,
                    'debit':0.0,
                    'credit':1650.0,
                }),
            ]
        })

    deftest_custom_currency_on_account_1(self):
        custom_account=self.company_data['default_account_revenue'].copy()

        #Thecurrencysetontheaccountisnotthesameastheonesetonthecompany.
        #Itshouldraiseanerror.
        custom_account.currency_id=self.currency_data['currency']

        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.line_ids[0].account_id=custom_account

        #Thecurrencysetontheaccountisthesameastheonesetonthecompany.
        #Itshouldnotraiseanerror.
        custom_account.currency_id=self.company_data['currency']

        self.test_move.line_ids[0].account_id=custom_account

    deftest_misc_fiscalyear_lock_date_1(self):
        self.test_move.action_post()

        #Setthelockdateafterthejournalentrydate.
        self.test_move.company_id.fiscalyear_lock_date=fields.Date.from_string('2017-01-01')

        #lines[0]='counterpartline'
        #lines[1]='taxline'
        #lines[2]='revenueline1'
        #lines[3]='revenueline2'
        lines=self.test_move.line_ids.sorted('debit')

        #Editingthereferenceshouldbeallowed.
        self.test_move.ref='whatever'

        #Trytoeditalineintoalockedfiscalyear.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                    (1,lines[2].id,{'debit':lines[2].debit+100.0}),
                ],
            })

        #Trytoedittheaccountofaline.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.line_ids[0].write({'account_id':self.test_move.line_ids[0].account_id.copy().id})

        #Trytoeditaline.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                    (1,lines[3].id,{'debit':lines[3].debit+100.0}),
                ],
            })

        #Trytoaddanewtaxonaline.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[2].id,{'tax_ids':[(6,0,self.company_data['default_tax_purchase'].ids)]}),
                ],
            })

        #Trytocreateanewline.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                    (0,None,{
                        'name':'revenueline1',
                        'account_id':self.company_data['default_account_revenue'].id,
                        'debit':100.0,
                        'credit':0.0,
                    }),
                ],
            })

        #Youcan'tremovethejournalentryfromalockedperiod.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.date=fields.Date.from_string('2018-01-01')

        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.unlink()

        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.button_draft()

        #Trytoaddanewjournalentrypriortothelockdate.
        copy_move=self.test_move.copy({'date':'2017-01-01'})
        #Thedatehasbeenchangedtothefirstvaliddate.
        self.assertEqual(copy_move.date,copy_move.company_id.fiscalyear_lock_date+relativedelta(days=1))

    deftest_misc_fiscalyear_lock_date_2(self):
        self.test_move.action_post()

        #Createabankstatementtogetabalanceinthesuspenseaccount.
        statement=self.env['account.bank.statement'].create({
            'journal_id':self.company_data['default_journal_bank'].id,
            'date':'2016-01-01',
            'line_ids':[
                (0,0,{'payment_ref':'test','amount':10.0})
            ],
        })
        statement.button_post()

        #Youcan'tlockthefiscalyearifthereissomeunreconciledstatement.
        withself.assertRaises(RedirectWarning),self.cr.savepoint():
            self.test_move.company_id.fiscalyear_lock_date=fields.Date.from_string('2017-01-01')

    deftest_misc_tax_lock_date_1(self):
        self.test_move.action_post()

        #Setthetaxlockdateafterthejournalentrydate.
        self.test_move.company_id.tax_lock_date=fields.Date.from_string('2017-01-01')

        #lines[0]='counterpartline'
        #lines[1]='taxline'
        #lines[2]='revenueline1'
        #lines[3]='revenueline2'
        lines=self.test_move.line_ids.sorted('debit')

        #Trytoeditalinenotaffectingthetaxes.
        self.test_move.write({
            'line_ids':[
                (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                (1,lines[2].id,{'debit':lines[2].debit+100.0}),
            ],
        })

        #Trytoedittheaccountofaline.
        self.test_move.line_ids[0].write({'account_id':self.test_move.line_ids[0].account_id.copy().id})

        #Trytoeditalinehavingsometaxes.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                    (1,lines[3].id,{'debit':lines[3].debit+100.0}),
                ],
            })

        #Trytoaddanewtaxonaline.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[2].id,{'tax_ids':[(6,0,self.company_data['default_tax_purchase'].ids)]}),
                ],
            })

        #Trytoeditataxline.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                    (1,lines[1].id,{'debit':lines[1].debit+100.0}),
                ],
            })

        #Trytocreatealinenotaffectingthetaxes.
        self.test_move.write({
            'line_ids':[
                (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                (0,None,{
                    'name':'revenueline1',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'debit':100.0,
                    'credit':0.0,
                }),
            ],
        })

        #Trytocreatealineaffectingthetaxes.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.write({
                'line_ids':[
                    (1,lines[0].id,{'credit':lines[0].credit+100.0}),
                    (0,None,{
                        'name':'revenueline2',
                        'account_id':self.company_data['default_account_revenue'].id,
                        'debit':1000.0,
                        'credit':0.0,
                        'tax_ids':[(6,0,self.company_data['default_tax_sale'].ids)],
                    }),
                ],
            })

        #Youcan'tremovethejournalentryfromalockedperiod.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.date=fields.Date.from_string('2018-01-01')

        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.unlink()

        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.button_draft()

        copy_move=self.test_move.copy({'date':self.test_move.date})

        #/!\Thedateischangedautomaticallytothenextavailableoneduringthepost.
        copy_move.action_post()

        #Youcan'tchangethedatetoonebeinginalockedperiod.
        withself.assertRaises(UserError),self.cr.savepoint():
            copy_move.date=fields.Date.from_string('2017-01-01')

    deftest_misc_draft_reconciled_entries_1(self):
        draft_moves=self.env['account.move'].create([
            {
                'move_type':'entry',
                'line_ids':[
                    (0,None,{
                        'name':'move1receivableline',
                        'account_id':self.company_data['default_account_receivable'].id,
                        'debit':1000.0,
                        'credit':0.0,
                    }),
                    (0,None,{
                        'name':'move1counterpartline',
                        'account_id':self.company_data['default_account_expense'].id,
                        'debit':0.0,
                        'credit':1000.0,
                    }),
                ]
            },
            {
                'move_type':'entry',
                'line_ids':[
                    (0,None,{
                        'name':'move2receivableline',
                        'account_id':self.company_data['default_account_receivable'].id,
                        'debit':0.0,
                        'credit':2000.0,
                    }),
                    (0,None,{
                        'name':'move2counterpartline',
                        'account_id':self.company_data['default_account_expense'].id,
                        'debit':2000.0,
                        'credit':0.0,
                    }),
                ]
            },
        ])

        #lines[0]='move2receivableline'
        #lines[1]='move1counterpartline'
        #lines[2]='move1receivableline'
        #lines[3]='move2counterpartline'
        draft_moves.action_post()
        lines=draft_moves.mapped('line_ids').sorted('balance')

        (lines[0]+lines[2]).reconcile()

        #Youcan'twritesomethingimpactingthereconciliationonanalreadyreconciledline.
        withself.assertRaises(UserError),self.cr.savepoint():
            draft_moves[0].write({
                'line_ids':[
                    (1,lines[1].id,{'credit':lines[1].credit+100.0}),
                    (1,lines[2].id,{'debit':lines[2].debit+100.0}),
                ]
            })

        #Thewritemustnotraiseanythingbecausetheroundingofthemonetaryfieldshouldignoresuchtinyamount.
        draft_moves[0].write({
            'line_ids':[
                (1,lines[1].id,{'credit':lines[1].credit+0.0000001}),
                (1,lines[2].id,{'debit':lines[2].debit+0.0000001}),
            ]
        })

        #Youcan'tunlinkanalreadyreconciledline.
        withself.assertRaises(UserError),self.cr.savepoint():
            draft_moves.unlink()

    deftest_misc_always_balanced_move(self):
        '''Ensurethereisnowaytomake'''
        #Youcan'tremoveajournalitemmakingthejournalentryunbalanced.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.line_ids[0].unlink()

        #Samecheckusingwriteinsteadofunlink.
        withself.assertRaises(UserError),self.cr.savepoint():
            balance=self.test_move.line_ids[0].balance+5
            self.test_move.line_ids[0].write({
                'debit':balanceifbalance>0.0else0.0,
                'credit':-balanceifbalance<0.0else0.0,
            })

        #Youcanremovejournalitemsiftherelatedjournalentryisstillbalanced.
        self.test_move.line_ids.unlink()

    deftest_add_followers_on_post(self):
        #Addsomeexistingpartners,somefromanothercompany
        company=self.env['res.company'].create({'name':'Oopo'})
        company.flush()
        existing_partners=self.env['res.partner'].create([{
            'name':'Jean',
            'company_id':company.id,
        },{
            'name':'Paulus',
        }])
        self.test_move.message_subscribe(existing_partners.ids)

        user=new_test_user(self.env,login='jag',groups='account.group_account_invoice')

        move=self.test_move.with_user(user)
        partner=self.env['res.partner'].create({'name':'Belouga'})
        move.partner_id=partner

        move.action_post()
        self.assertEqual(move.message_partner_ids,self.env.user.partner_id|existing_partners|partner)

    deftest_misc_move_onchange(self):
        '''Testthebehaviorononchangesforaccount.movehaving'entry'astype.'''

        move_form=Form(self.env['account.move'])
        #Rate1:3
        move_form.date=fields.Date.from_string('2016-01-01')

        #Newlinethatshouldget400.0asdebit.
        withmove_form.line_ids.new()asline_form:
            line_form.name='debit_line'
            line_form.account_id=self.company_data['default_account_revenue']
            line_form.currency_id=self.currency_data['currency']
            line_form.amount_currency=1200.0

        #Newlinethatshouldget400.0ascredit.
        withmove_form.line_ids.new()asline_form:
            line_form.name='credit_line'
            line_form.account_id=self.company_data['default_account_revenue']
            line_form.currency_id=self.currency_data['currency']
            line_form.amount_currency=-1200.0
        move=move_form.save()

        self.assertRecordValues(
            move.line_ids.sorted('debit'),
            [
                {
                    'currency_id':self.currency_data['currency'].id,
                    'amount_currency':-1200.0,
                    'debit':0.0,
                    'credit':400.0,
                },
                {
                    'currency_id':self.currency_data['currency'].id,
                    'amount_currency':1200.0,
                    'debit':400.0,
                    'credit':0.0,
                },
            ],
        )

        #===Changethedatetochangethecurrencyconversion'srate===

        withForm(move)asmove_form:
            move_form.date=fields.Date.from_string('2017-01-01')

        self.assertRecordValues(
            move.line_ids.sorted('debit'),
            [
                {
                    'currency_id':self.currency_data['currency'].id,
                    'amount_currency':-1200.0,
                    'debit':0.0,
                    'credit':600.0,
                },
                {
                    'currency_id':self.currency_data['currency'].id,
                    'amount_currency':1200.0,
                    'debit':600.0,
                    'credit':0.0,
                },
            ],
        )

    deftest_included_tax(self):
        '''
        Testanaccount.move.lineiscreatedautomaticallywhenaddingatax.
        Thistestusesthefollowingscenario:
            -Createmanuallyadebitlineof1000havinganincludedtax.
            -Assumealinecontainingthetaxamountiscreatedautomatically.
            -Createmanuallyacreditlinetobalancethetwopreviouslines.
            -Savethemove.

        includedtax=20%

        Name                  |Debit    |Credit   |Tax_ids      |Tax_line_id'sname
        -----------------------|-----------|-----------|---------------|-------------------
        debit_line_1          |1000     |          |tax          |
        included_tax_line     |200      |          |              |included_tax_line
        credit_line_1         |          |1200     |              |
        '''

        self.included_percent_tax=self.env['account.tax'].create({
            'name':'included_tax_line',
            'amount_type':'percent',
            'amount':20,
            'price_include':True,
            'include_base_amount':False,
        })
        self.account=self.company_data['default_account_revenue']

        move_form=Form(self.env['account.move'].with_context(default_move_type='entry'))

        #Createanewaccount.move.linewithdebitamount.
        withmove_form.line_ids.new()asdebit_line:
            debit_line.name='debit_line_1'
            debit_line.account_id=self.account
            debit_line.debit=1000
            debit_line.tax_ids.clear()
            debit_line.tax_ids.add(self.included_percent_tax)

            self.assertTrue(debit_line.recompute_tax_line)

        #Createathirdaccount.move.linewithcreditamount.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='credit_line_1'
            credit_line.account_id=self.account
            credit_line.credit=1200

        move=move_form.save()

        self.assertRecordValues(move.line_ids,[
            {'name':'debit_line_1',            'debit':1000.0,   'credit':0.0,     'tax_ids':[self.included_percent_tax.id],     'tax_line_id':False},
            {'name':'included_tax_line',       'debit':200.0,    'credit':0.0,     'tax_ids':[],                                 'tax_line_id':self.included_percent_tax.id},
            {'name':'credit_line_1',           'debit':0.0,      'credit':1200.0,  'tax_ids':[],                                 'tax_line_id':False},
        ])

    deftest_misc_custom_tags(self):
        tag=self.env['account.account.tag'].create({
            'name':"test_misc_custom_tags",
            'applicability':'taxes',
            'country_id':self.env.ref('base.us').id,
        })
        move_form=Form(self.env['account.move'].with_context(default_move_type='entry'))
        withmove_form.line_ids.new()asdebit_line:
            debit_line.name='debit_line'
            debit_line.account_id=self.company_data['default_account_revenue']
            debit_line.debit=1000
            debit_line.tax_tag_ids.add(tag)
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='credit_line'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.credit=1000
        move=move_form.save()
        self.assertRecordValues(move.line_ids,[
            #pylint:disable=bad-whitespace
            {'debit':1000.0,  'credit':0.0,     'tax_tag_ids':tag.ids},
            {'debit':0.0,     'credit':1000.0,  'tax_tag_ids':[]},
        ])

    deftest_misc_prevent_unlink_posted_items(self):
        #Youcannotremovejournalitemsiftherelatedjournalentryisposted.
        self.test_move.action_post()
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_move.line_ids.unlink()

        #Youcanremovejournalitemsiftherelatedjournalentryisdraft.
        self.test_move.button_draft()
        self.test_move.line_ids.unlink()

    deftest_invoice_like_entry_reverse_caba(self):
        tax_waiting_account=self.env['account.account'].create({
            'name':'TAX_WAIT',
            'code':'TWAIT',
            'user_type_id':self.env.ref('account.data_account_type_current_liabilities').id,
            'reconcile':True,
            'company_id':self.company_data['company'].id,
        })
        tax_final_account=self.env['account.account'].create({
            'name':'TAX_TO_DEDUCT',
            'code':'TDEDUCT',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
            'company_id':self.company_data['company'].id,
        })
        tax_base_amount_account=self.env['account.account'].create({
            'name':'TAX_BASE',
            'code':'TBASE',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
            'company_id':self.company_data['company'].id,
        })
        self.env.company.account_cash_basis_base_account_id=tax_base_amount_account
        self.env.company.tax_exigibility=True
        tax_tags=defaultdict(dict)
        forline_type,repartition_typein[(l,r)forlin('invoice','refund')forrin('base','tax')]:
            tax_tags[line_type][repartition_type]=self.env['account.account.tag'].create({
                'name':'%s%stag'%(line_type,repartition_type),
                'applicability':'taxes',
                'country_id':self.env.ref('base.us').id,
            })
        tax=self.env['account.tax'].create({
            'name':'cashbasis10%',
            'type_tax_use':'sale',
            'amount':10,
            'tax_exigibility':'on_payment',
            'cash_basis_transition_account_id':tax_waiting_account.id,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(6,0,tax_tags['invoice']['base'].ids)],
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'account_id':tax_final_account.id,
                    'tag_ids':[(6,0,tax_tags['invoice']['tax'].ids)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(6,0,tax_tags['refund']['base'].ids)],
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'account_id':tax_final_account.id,
                    'tag_ids':[(6,0,tax_tags['refund']['tax'].ids)],
                }),
            ],
        })
        move=self.env['account.move'].create({
            'move_type':'entry',
            'date':fields.Date.from_string('2016-01-01'),
            'line_ids':[
                (0,None,{
                    'name':'revenueline',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'debit':0.0,
                    'credit':1000.0,
                    'tax_ids':[(6,0,tax.ids)],
                    'tax_tag_ids':[(6,0,tax_tags['invoice']['base'].ids)],
                }),
                (0,None,{
                    'name':'taxline1',
                    'account_id':tax_waiting_account.id,
                    'debit':0.0,
                    'credit':100.0,
                    'tax_tag_ids':[(6,0,tax_tags['invoice']['tax'].ids)],
                    'tax_repartition_line_id':tax.invoice_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax').id,
                }),
                (0,None,{
                    'name':'counterpartline',
                    'account_id':self.company_data['default_account_receivable'].id,
                    'debit':1100.0,
                    'credit':0.0,
                }),
            ]
        })
        move.action_post()
        #makepayment
        payment=self.env['account.payment'].create({
            'payment_type':'inbound',
            'payment_method_id':self.env.ref('account.account_payment_method_manual_in').id,
            'partner_type':'customer',
            'partner_id':self.partner_a.id,
            'amount':1100,
            'date':move.date,
            'journal_id':self.company_data['default_journal_bank'].id,
        })
        payment.action_post()
        (payment.move_id+move).line_ids.filtered(lambdax:x.account_id==self.company_data['default_account_receivable']).reconcile()
        #checkcabamove
        partial_rec=move.mapped('line_ids.matched_credit_ids')
        caba_move=self.env['account.move'].search([('tax_cash_basis_rec_id','=',partial_rec.id)])
        expected_values=[
            {
                'tax_line_id':False,
                'tax_repartition_line_id':False,
                'tax_ids':[],
                'tax_tag_ids':[],
                'account_id':tax_base_amount_account.id,
                'debit':1000.0,
                'credit':0.0,
            },
            {
                'tax_line_id':False,
                'tax_repartition_line_id':False,
                'tax_ids':tax.ids,
                'tax_tag_ids':tax_tags['invoice']['base'].ids,
                'account_id':tax_base_amount_account.id,
                'debit':0.0,
                'credit':1000.0,
            },

            {
                'tax_line_id':False,
                'tax_repartition_line_id':False,
                'tax_ids':[],
                'tax_tag_ids':[],
                'account_id':tax_waiting_account.id,
                'debit':100.0,
                'credit':0.0,
            },
            {
                'tax_line_id':tax.id,
                'tax_repartition_line_id':tax.invoice_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax').id,
                'tax_ids':[],
                'tax_tag_ids':tax_tags['invoice']['tax'].ids,
                'account_id':tax_final_account.id,
                'debit':0.0,
                'credit':100.0,
            },
        ]
        self.assertRecordValues(caba_move.line_ids,expected_values)
        #unreconcile
        debit_aml=move.line_ids.filtered('debit')
        debit_aml.remove_move_reconcile()
        #checkcabamovereverseissameascabamovewithonlydebit/creditinverted
        reversed_caba_move=self.env['account.move'].search([('reversed_entry_id','=',caba_move.id)])
        forvalueinexpected_values:
            value.update({
                'debit':value['credit'],
                'credit':value['debit'],
            })
        self.assertRecordValues(reversed_caba_move.line_ids,expected_values)

    def_get_cache_count(self,model_name='account.move',field_name='name'):
        model=self.env[model_name]
        field=model._fields[field_name]
        returnlen(self.env.cache.get_records(model,field))

    deftest_cache_invalidation(self):
        self.env['account.move'].invalidate_cache()
        lines=self.test_move.line_ids
        #prefetch
        lines.mapped('move_id.name')
        #checkaccount.movecache
        self.assertEqual(self._get_cache_count(),1)
        self.env['account.move.line'].invalidate_cache(ids=lines.ids)
        self.assertEqual(self._get_cache_count(),0)

    deftest_misc_prevent_edit_tax_on_posted_moves(self):
        #Youcannotremovejournalitemsiftherelatedjournalentryisposted.
        self.test_move.action_post()
        withself.assertRaisesRegex(UserError,"Youcannotmodifythetaxesrelatedtoapostedjournalitem"),\
             self.cr.savepoint():
            self.test_move.line_ids.filtered(lambdal:l.tax_ids).tax_ids=False

        withself.assertRaisesRegex(UserError,"Youcannotmodifythetaxesrelatedtoapostedjournalitem"),\
             self.cr.savepoint():
            self.test_move.line_ids.filtered(lambdal:l.tax_line_id).tax_line_id=False

        #Youcanremovejournalitemsiftherelatedjournalentryisdraft.
        self.test_move.button_draft()
        self.assertTrue(self.test_move.line_ids.unlink())
