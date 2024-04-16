#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged,Form


@tagged('post_install','-at_install')
classTestInvoiceTaxes(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].country_id=cls.env.ref('base.us')

        cls.percent_tax_1=cls.env['account.tax'].create({
            'name':'21%',
            'amount_type':'percent',
            'amount':21,
            'sequence':10,
        })
        cls.percent_tax_1_incl=cls.env['account.tax'].create({
            'name':'21%incl',
            'amount_type':'percent',
            'amount':21,
            'price_include':True,
            'include_base_amount':True,
            'sequence':20,
        })
        cls.percent_tax_2=cls.env['account.tax'].create({
            'name':'12%',
            'amount_type':'percent',
            'amount':12,
            'sequence':30,
        })
        cls.percent_tax_3_incl=cls.env['account.tax'].create({
            'name':'5%incl',
            'amount_type':'percent',
            'amount':5,
            'price_include':True,
            'include_base_amount':True,
            'sequence':40,
        })
        cls.group_tax=cls.env['account.tax'].create({
            'name':'group12%+21%',
            'amount_type':'group',
            'amount':21,
            'children_tax_ids':[
                (4,cls.percent_tax_1_incl.id),
                (4,cls.percent_tax_2.id)
            ],
            'sequence':40,
        })

        cls.tax_report=cls.env['account.tax.report'].create({
            'name':"Taxreport",
            'country_id':cls.company_data['company'].country_id.id,
        })

        cls.tax_report_line=cls.env['account.tax.report.line'].create({
            'name':'test_tax_report_line',
            'tag_name':'test_tax_report_line',
            'report_id':cls.tax_report.id,
            'sequence':10,
        })
        cls.tax_tag_pos=cls.tax_report_line.tag_ids.filtered(lambdax:notx.tax_negate)
        cls.tax_tag_neg=cls.tax_report_line.tag_ids.filtered(lambdax:x.tax_negate)
        cls.base_tax_report_line=cls.env['account.tax.report.line'].create({
            'name':'base_test_tax_report_line',
            'tag_name':'base_test_tax_report_line',
            'report_id':cls.tax_report.id,
            'sequence':10,
        })
        cls.base_tag_pos=cls.base_tax_report_line.tag_ids.filtered(lambdax:notx.tax_negate)
        cls.base_tag_neg=cls.base_tax_report_line.tag_ids.filtered(lambdax:x.tax_negate)

    def_create_invoice(self,taxes_per_line,inv_type='out_invoice',currency_id=False,invoice_payment_term_id=False):
        '''Createaninvoiceonthefly.

        :paramtaxes_per_line:Alistoftuple(price_unit,account.taxrecordset)
        '''
        vals={
            'move_type':inv_type,
            'partner_id':self.partner_a.id,
            'invoice_line_ids':[(0,0,{
                'name':'xxxx',
                'quantity':1,
                'price_unit':amount,
                'tax_ids':[(6,0,taxes.ids)],
            })foramount,taxesintaxes_per_line],
        }
        ifcurrency_id:
            vals['currency_id']=currency_id.id
        ifinvoice_payment_term_id:
            vals['invoice_payment_term_id']=invoice_payment_term_id.id
        returnself.env['account.move'].create(vals)

    deftest_one_tax_per_line(self):
        '''Test:
        price_unit|Taxes
        ------------------
        100       |21%
        121       |21%incl
        100       |12%

        Expected:
        Tax        |Taxes    |Base     |Amount
        --------------------------------------------
        21%        |/        |100      |21
        21%incl   |/        |100      |21
        12%        |/        |100      |12
        '''
        invoice=self._create_invoice([
            (100,self.percent_tax_1),
            (121,self.percent_tax_1_incl),
            (100,self.percent_tax_2),
        ])
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'),[
            {'name':self.percent_tax_1.name,      'tax_base_amount':100,'price_unit':21,'tax_ids':[]},
            {'name':self.percent_tax_1_incl.name, 'tax_base_amount':100,'price_unit':21,'tax_ids':[]},
            {'name':self.percent_tax_2.name,      'tax_base_amount':100,'price_unit':12,'tax_ids':[]},
        ])

    deftest_affecting_base_amount(self):
        '''Test:
        price_unit|Taxes
        ------------------
        121       |21%incl,12%
        100       |12%

        Expected:
        Tax        |Taxes    |Base     |Amount
        --------------------------------------------
        21%incl   |12%      |100      |21
        12%        |/        |121      |14.52
        12%        |/        |100      |12
        '''
        invoice=self._create_invoice([
            (121,self.percent_tax_1_incl+self.percent_tax_2),
            (100,self.percent_tax_2),
        ])
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id').sorted(lambdax:x.price_unit),[
            {'name':self.percent_tax_1_incl.name,     'tax_base_amount':100,'price_unit':21,     'tax_ids':[self.percent_tax_2.id]},
            {'name':self.percent_tax_2.name,          'tax_base_amount':221,'price_unit':26.52,  'tax_ids':[]},
        ])

    deftest_group_of_taxes(self):
        '''Test:
        price_unit|Taxes
        ------------------
        121       |21%incl+12%
        100       |12%

        Expected:
        Tax        |Taxes    |Base     |Amount
        --------------------------------------------
        21%incl   |/        |100      |21
        12%        |21%incl |121      |14.52
        12%        |/        |100      |12
        '''
        invoice=self._create_invoice([
            (121,self.group_tax),
            (100,self.percent_tax_2),
        ])
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id').sorted(lambdax:x.price_unit),[
            {'name':self.percent_tax_1_incl.name,     'tax_base_amount':100,'price_unit':21,     'tax_ids':[self.percent_tax_2.id]},
            {'name':self.percent_tax_2.name,          'tax_base_amount':221,'price_unit':26.52,  'tax_ids':[]},
        ])

    def_create_tax_tag(self,tag_name):
        returnself.env['account.account.tag'].create({
            'name':tag_name,
            'applicability':'taxes',
            'country_id':self.env.company.country_id.id,
        })

    deftest_tax_repartition(self):
        inv_base_tag=self._create_tax_tag('invoice_base')
        inv_tax_tag_10=self._create_tax_tag('invoice_tax_10')
        inv_tax_tag_90=self._create_tax_tag('invoice_tax_90')
        ref_base_tag=self._create_tax_tag('refund_base')
        ref_tax_tag=self._create_tax_tag('refund_tax')

        user_type=self.env.ref('account.data_account_type_current_assets')
        account_1=self.env['account.account'].create({'name':'test1','code':'test1','user_type_id':user_type.id})
        account_2=self.env['account.account'].create({'name':'test2','code':'test2','user_type_id':user_type.id})

        tax=self.env['account.tax'].create({
            'name':"Taxwithaccount",
            'amount_type':'fixed',
            'type_tax_use':'sale',
            'amount':42,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(4,inv_base_tag.id,0)],
                }),

                (0,0,{
                    'factor_percent':10,
                    'repartition_type':'tax',
                    'account_id':account_1.id,
                    'tag_ids':[(4,inv_tax_tag_10.id,0)],
                }),

                (0,0,{
                    'factor_percent':90,
                    'repartition_type':'tax',
                    'account_id':account_2.id,
                    'tag_ids':[(4,inv_tax_tag_90.id,0)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                    'tag_ids':[(4,ref_base_tag.id,0)],
                }),

                (0,0,{
                    'factor_percent':10,
                    'repartition_type':'tax',
                    'tag_ids':[(4,ref_tax_tag.id,0)],
                }),

                (0,0,{
                    'factor_percent':90,
                    'repartition_type':'tax',
                    'account_id':account_1.id,
                    'tag_ids':[(4,ref_tax_tag.id,0)],
                }),
            ],
        })

        #Testinvoicerepartition
        invoice=self._create_invoice([(100,tax)],inv_type='out_invoice')
        invoice.action_post()

        self.assertEqual(len(invoice.line_ids),4,"Thereshouldbe4accountmovelinescreatedfortheinvoice:payable,baseand2taxlines")
        inv_base_line=invoice.line_ids.filtered(lambdax:notx.tax_repartition_line_idandx.account_id.user_type_id.type!='receivable')
        self.assertEqual(len(inv_base_line),1,"Thereshouldbeonlyonebaselinegenerated")
        self.assertEqual(abs(inv_base_line.balance),100,"Baseamountshouldbe100")
        self.assertEqual(inv_base_line.tax_tag_ids,inv_base_tag,"Baselineshouldhavereceivedbasetag")
        inv_tax_lines=invoice.line_ids.filtered(lambdax:x.tax_repartition_line_id.repartition_type=='tax')
        self.assertEqual(len(inv_tax_lines),2,"Thereshouldbetwotaxlines,oneforeachrepartitionline.")
        self.assertEqual(abs(inv_tax_lines.filtered(lambdax:x.account_id==account_1).balance),4.2,"Taxlineonaccount1shouldamountto4.2(10%of42)")
        self.assertEqual(inv_tax_lines.filtered(lambdax:x.account_id==account_1).tax_tag_ids,inv_tax_tag_10,"Taxlineonaccount1shouldhave10%tag")
        self.assertAlmostEqual(abs(inv_tax_lines.filtered(lambdax:x.account_id==account_2).balance),37.8,2,"Taxlineonaccount2shouldamountto37.8(90%of42)")
        self.assertEqual(inv_tax_lines.filtered(lambdax:x.account_id==account_2).tax_tag_ids,inv_tax_tag_90,"Taxlineonaccount2shouldhave90%tag")

        #Testrefundrepartition
        refund=self._create_invoice([(100,tax)],inv_type='out_refund')
        refund.action_post()

        self.assertEqual(len(refund.line_ids),4,"Thereshouldbe4accountmovelinescreatedfortherefund:payable,baseand2taxlines")
        ref_base_line=refund.line_ids.filtered(lambdax:notx.tax_repartition_line_idandx.account_id.user_type_id.type!='receivable')
        self.assertEqual(len(ref_base_line),1,"Thereshouldbeonlyonebaselinegenerated")
        self.assertEqual(abs(ref_base_line.balance),100,"Baseamountshouldbe100")
        self.assertEqual(ref_base_line.tax_tag_ids,ref_base_tag,"Baselineshouldhavereceivedbasetag")
        ref_tax_lines=refund.line_ids.filtered(lambdax:x.tax_repartition_line_id.repartition_type=='tax')
        self.assertEqual(len(ref_tax_lines),2,"Thereshouldbetworefundtaxlines")
        self.assertEqual(abs(ref_tax_lines.filtered(lambdax:x.account_id==ref_base_line.account_id).balance),4.2,"Refundtaxlineonbaseaccountshouldamountto4.2(10%of42)")
        self.assertAlmostEqual(abs(ref_tax_lines.filtered(lambdax:x.account_id==account_1).balance),37.8,2,"Refundtaxlineonaccount1shouldamountto37.8(90%of42)")
        self.assertEqual(ref_tax_lines.mapped('tax_tag_ids'),ref_tax_tag,"Refundtaxlinesshouldhavetherighttag")

    deftest_division_tax(self):
        '''
        Testthatwhenusingdivisiontax,withpercentageamount
        100%anychangeonpriceunitiscorrectlyreflectedon
        thewholemove.

        Completescenario:
            -Createadivisiontax,100%amount,includedinprice.
            -Createaninvoice,withonlythementionedtax
            -Changeprice_unitoftheaml
            -Totalpriceofthemoveshouldchangeaswell
        '''

        sale_tax=self.env['account.tax'].create({
            'name':'tax',
            'type_tax_use':'sale',
            'amount_type':'division',
            'amount':100,
            'price_include':True,
            'include_base_amount':True,
        })
        invoice=self._create_invoice([(100,sale_tax)])
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'),[{
            'name':sale_tax.name,
            'tax_base_amount':0.0,
            'balance':-100,
        }])
        #changepriceunit,everythingshouldchangeaswell
        withForm(invoice)asinvoice_form:
            withinvoice_form.line_ids.edit(0)asline_edit:
                line_edit.price_unit=200

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'),[{
            'name':sale_tax.name,
            'tax_base_amount':0.0,
            'balance':-200,
        }])

    deftest_misc_journal_entry_tax_tags_sale(self):
        sale_tax=self.env['account.tax'].create({
            'name':'tax',
            'type_tax_use':'sale',
            'amount_type':'percent',
            'amount':10,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'repartition_type':'base',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.base_tag_pos.ids)],
                }),
                (0,0,{
                    'repartition_type':'tax',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.tax_tag_pos.ids)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'repartition_type':'base',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.base_tag_neg.ids)],
                }),
                (0,0,{
                    'repartition_type':'tax',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.tax_tag_neg.ids)],
                }),
            ],
        })

        inv_tax_rep_ln=sale_tax.invoice_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax')
        ref_tax_rep_ln=sale_tax.refund_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax')

        #===Taxindebit===

        move_form=Form(self.env['account.move'],view='account.view_move_form')
        move_form.ref='azerty'

        #Debitbasetaxline.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='debit_line_1'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.debit=1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(sale_tax)

            self.assertTrue(credit_line.recompute_tax_line)

        #Balancethejournalentry.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='balance'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.credit=1100.0

        move=move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'),[
            {'balance':-1100.0,   'tax_ids':[],             'tax_tag_ids':[],                     'tax_base_amount':0,      'tax_repartition_line_id':False},
            {'balance':100.0,     'tax_ids':[],             'tax_tag_ids':self.tax_tag_neg.ids,   'tax_base_amount':1000,   'tax_repartition_line_id':ref_tax_rep_ln.id},
            {'balance':1000.0,    'tax_ids':sale_tax.ids,   'tax_tag_ids':self.base_tag_neg.ids,  'tax_base_amount':0,      'tax_repartition_line_id':False},
        ])

        #===Taxincredit===

        move_form=Form(self.env['account.move'],view='account.view_move_form')
        move_form.ref='azerty'

        #Debitbasetaxline.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='debit_line_1'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.credit=1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(sale_tax)

            self.assertTrue(credit_line.recompute_tax_line)

        #Balancethejournalentry.
        withmove_form.line_ids.new()asdebit_line:
            debit_line.name='balance'
            debit_line.account_id=self.company_data['default_account_revenue']
            debit_line.debit=1100.0

        move=move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'),[
            {'balance':-1000.0,   'tax_ids':sale_tax.ids,   'tax_tag_ids':self.base_tag_neg.ids,  'tax_base_amount':0,      'tax_repartition_line_id':False},
            {'balance':-100.0,    'tax_ids':[],             'tax_tag_ids':self.tax_tag_neg.ids,   'tax_base_amount':1000,   'tax_repartition_line_id':inv_tax_rep_ln.id},
            {'balance':1100.0,    'tax_ids':[],             'tax_tag_ids':[],                     'tax_base_amount':0,      'tax_repartition_line_id':False},
        ])

    deftest_misc_journal_entry_tax_tags_purchase(self):
        purch_tax=self.env['account.tax'].create({
            'name':'tax',
            'type_tax_use':'purchase',
            'amount_type':'percent',
            'amount':10,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'repartition_type':'base',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.base_tag_pos.ids)],
                }),
                (0,0,{
                    'repartition_type':'tax',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.tax_tag_pos.ids)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'repartition_type':'base',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.base_tag_neg.ids)],
                }),
                (0,0,{
                    'repartition_type':'tax',
                    'factor_percent':100.0,
                    'tag_ids':[(6,0,self.tax_tag_neg.ids)],
                }),
            ],
        })

        inv_tax_rep_ln=purch_tax.invoice_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax')
        ref_tax_rep_ln=purch_tax.refund_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax')

        #===Taxindebit===

        move_form=Form(self.env['account.move'])
        move_form.ref='azerty'

        #Debitbasetaxline.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='debit_line_1'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.debit=1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(purch_tax)

            self.assertTrue(credit_line.recompute_tax_line)

        #Balancethejournalentry.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='balance'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.credit=1100.0

        move=move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'),[
            {'balance':-1100.0,   'tax_ids':[],             'tax_tag_ids':[],                     'tax_base_amount':0,      'tax_repartition_line_id':False},
            {'balance':100.0,     'tax_ids':[],             'tax_tag_ids':self.tax_tag_pos.ids,   'tax_base_amount':1000,   'tax_repartition_line_id':inv_tax_rep_ln.id},
            {'balance':1000.0,    'tax_ids':purch_tax.ids,  'tax_tag_ids':self.base_tag_pos.ids,  'tax_base_amount':0,      'tax_repartition_line_id':False},
        ])

        #===Taxincredit===

        move_form=Form(self.env['account.move'])
        move_form.ref='azerty'

        #Debitbasetaxline.
        withmove_form.line_ids.new()ascredit_line:
            credit_line.name='debit_line_1'
            credit_line.account_id=self.company_data['default_account_revenue']
            credit_line.credit=1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(purch_tax)

            self.assertTrue(credit_line.recompute_tax_line)

        #Balancethejournalentry.
        withmove_form.line_ids.new()asdebit_line:
            debit_line.name='balance'
            debit_line.account_id=self.company_data['default_account_revenue']
            debit_line.debit=1100.0

        move=move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'),[
            {'balance':-1000.0,   'tax_ids':purch_tax.ids,  'tax_tag_ids':self.base_tag_pos.ids,  'tax_base_amount':0,      'tax_repartition_line_id':False},
            {'balance':-100.0,    'tax_ids':[],             'tax_tag_ids':self.tax_tag_pos.ids,   'tax_base_amount':1000,   'tax_repartition_line_id':ref_tax_rep_ln.id},
            {'balance':1100.0,    'tax_ids':[],             'tax_tag_ids':[],                     'tax_base_amount':0,      'tax_repartition_line_id':False},
        ])

    deftest_misc_entry_tax_group_signs(self):
        """Testssigninversionofthetagsonmiscoperationsmadewithtax
        groups.
        """
        def_create_group_of_taxes(tax_type):
            #Weuseasymmetrictagsbetweenthechildtaxestoavoidshadowingerrors
            child1_sale_tax=self.env['account.tax'].create({
                'sequence':1,
                'name':'child1_%s'%tax_type,
                'type_tax_use':'none',
                'amount_type':'percent',
                'amount':5,
                'invoice_repartition_line_ids':[
                    (0,0,{
                        'repartition_type':'base',
                        'factor_percent':100.0,
                        'tag_ids':[(6,0,self.base_tag_pos.ids)],
                    }),
                    (0,0,{
                        'repartition_type':'tax',
                        'factor_percent':100.0,
                        'tag_ids':[(6,0,self.tax_tag_pos.ids)],
                    }),
                ],
                'refund_repartition_line_ids':[
                    (0,0,{
                        'repartition_type':'base',
                        'factor_percent':100.0,
                    }),
                    (0,0,{
                        'repartition_type':'tax',
                        'factor_percent':100.0,
                    }),
                ],
            })
            child2_sale_tax=self.env['account.tax'].create({
                'sequence':2,
                'name':'child2_%s'%tax_type,
                'type_tax_use':'none',
                'amount_type':'percent',
                'amount':10,
                'invoice_repartition_line_ids':[
                    (0,0,{
                        'repartition_type':'base',
                        'factor_percent':100.0,
                    }),
                    (0,0,{
                        'repartition_type':'tax',
                        'factor_percent':100.0,
                    }),
                ],
                'refund_repartition_line_ids':[
                    (0,0,{
                        'repartition_type':'base',
                        'factor_percent':100.0,
                        'tag_ids':[(6,0,self.base_tag_neg.ids)],
                    }),
                    (0,0,{
                        'repartition_type':'tax',
                        'factor_percent':100.0,
                        'tag_ids':[(6,0,self.tax_tag_neg.ids)],
                    }),
                ],
            })
            returnself.env['account.tax'].create({
                'name':'group_%s'%tax_type,
                'type_tax_use':tax_type,
                'amount_type':'group',
                'amount':10,
                'children_tax_ids':[(6,0,[child1_sale_tax.id,child2_sale_tax.id])]
            })

        def_create_misc_operation(tax,tax_field):
            withForm(self.env['account.move'],view='account.view_move_form')asmove_form:
                forline_fieldin('debit','credit'):
                    line_amount=tax_field==line_fieldand1000or1150
                    withmove_form.line_ids.new()asline_form:
                        line_form.name='%s_line'%line_field
                        line_form.account_id=self.company_data['default_account_revenue']
                        line_form.debit=line_field=='debit'andline_amountor0
                        line_form.credit=line_field=='credit'andline_amountor0

                        iftax_field==line_field:
                            line_form.tax_ids.clear()
                            line_form.tax_ids.add(tax)

            returnmove_form.save()

        sale_group=_create_group_of_taxes('sale')
        purchase_group=_create_group_of_taxes('purchase')

        #Saletaxondebit:userefundrepartition
        debit_sale_move=_create_misc_operation(sale_group,'debit')
        self.assertRecordValues(debit_sale_move.line_ids.sorted('balance'),[
            {'balance':-1150.0,   'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':0},
            {'balance':50.0,      'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':1000},
            {'balance':100.0,     'tax_ids':[],                 'tax_tag_ids':self.tax_tag_neg.ids,   'tax_base_amount':1000},
            {'balance':1000.0,    'tax_ids':sale_group.ids,     'tax_tag_ids':self.base_tag_neg.ids,  'tax_base_amount':0},
        ])

        #Saletaxoncredit:useinvoicerepartitionandinverttags
        credit_sale_move=_create_misc_operation(sale_group,'credit')
        self.assertRecordValues(credit_sale_move.line_ids.sorted('balance'),[
            {'balance':-1000.0,   'tax_ids':sale_group.ids,     'tax_tag_ids':self.base_tag_neg.ids,  'tax_base_amount':0},
            {'balance':-100.0,    'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':1000},
            {'balance':-50.0,     'tax_ids':[],                 'tax_tag_ids':self.tax_tag_neg.ids,   'tax_base_amount':1000},
            {'balance':1150.0,    'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':0},
        ])

        #Purchasetaxondebit:useinvoicerepartition
        debit_purchase_move=_create_misc_operation(purchase_group,'debit')
        self.assertRecordValues(debit_purchase_move.line_ids.sorted('balance'),[
            {'balance':-1150.0,   'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':0},
            {'balance':50.0,      'tax_ids':[],                 'tax_tag_ids':self.tax_tag_pos.ids,   'tax_base_amount':1000},
            {'balance':100.0,     'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':1000},
            {'balance':1000.0,    'tax_ids':purchase_group.ids, 'tax_tag_ids':self.base_tag_pos.ids,  'tax_base_amount':0},
        ])

        #Purchasetaxoncredit:userefundrepartitionandinverttags
        credit_purchase_move=_create_misc_operation(purchase_group,'credit')
        self.assertRecordValues(credit_purchase_move.line_ids.sorted('balance'),[
            {'balance':-1000.0,   'tax_ids':purchase_group.ids, 'tax_tag_ids':self.base_tag_pos.ids,  'tax_base_amount':0},
            {'balance':-100.0,    'tax_ids':[],                 'tax_tag_ids':self.tax_tag_pos.ids,   'tax_base_amount':1000},
            {'balance':-50.0,     'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':1000},
            {'balance':1150.0,    'tax_ids':[],                 'tax_tag_ids':[],                     'tax_base_amount':0},
        ])

    deftest_tax_calculation_foreign_currency_large_quantity(self):
        '''Test:
        Foreigncurrencywithrateof1.1726andtaxof21%
        price_unit|Quantity |Taxes
        ------------------
        2.82      |20000    |21%notincl
        '''
        self.env['res.currency.rate'].create({
            'name':'2018-01-01',
            'rate':1.1726,
            'currency_id':self.currency_data['currency'].id,
            'company_id':self.env.company.id,
        })
        self.currency_data['currency'].rounding=0.05

        invoice=self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':self.partner_a.id,
            'currency_id':self.currency_data['currency'].id,
            'invoice_date':'2018-01-01',
            'date':'2018-01-01',
            'invoice_line_ids':[(0,0,{
                'name':'xxxx',
                'quantity':20000,
                'price_unit':2.82,
                'tax_ids':[(6,0,self.percent_tax_1.ids)],
            })]
        })

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'),[{
            'tax_base_amount':48098.24,   #20000*2.82/1.1726
            'credit':10100.63,            #tax_base_amount*0.21
        }])

    deftest_ensure_no_unbalanced_entry(self):
        '''Ensuretonotcreateanunbalancedjournalentrywhensaving.'''
        self.env['res.currency.rate'].create({
            'name':'2018-01-01',
            'rate':0.654065014,
            'currency_id':self.currency_data['currency'].id,
            'company_id':self.env.company.id,
        })
        self.currency_data['currency'].rounding=0.05

        invoice=self._create_invoice([
            (5,self.percent_tax_3_incl),
            (10,self.percent_tax_3_incl),
            (50,self.percent_tax_3_incl),
        ],currency_id=self.currency_data['currency'],invoice_payment_term_id=self.pay_terms_a)
        invoice.action_post()

    deftest_tax_calculation_multi_currency(self):
        self.env['res.currency.rate'].create({
            'name':'2018-01-01',
            'rate':0.273748,
            'currency_id':self.currency_data['currency'].id,
            'company_id':self.env.company.id,
        })
        self.currency_data['currency'].rounding=0.01

        invoice=self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':self.partner_a.id,
            'currency_id':self.currency_data['currency'].id,
            'invoice_date':'2018-01-01',
            'date':'2018-01-01',
            'invoice_line_ids':[(0,0,{
                'name':'xxxx',
                'quantity':1,
                'price_unit':155.32,
                'tax_ids':[(6,0,self.percent_tax_1.ids)],
            })]
        })

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'),[{
            'tax_base_amount':567.38,     #155.32*1/(1/0.273748)
            'balance':-119.16,            #tax_base_amount*0.21
        }])

        self.assertRecordValues(invoice.line_ids.filtered(lambdal:notl.name),[{
            'balance':686.54
        }])

        withForm(invoice)asinvoice_form:
            invoice_form.currency_id=self.currency_data['currency']

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'),[{
            'tax_base_amount':567.38,
            'balance':-119.16,
        }])

        self.assertRecordValues(invoice.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable'),[{
            'balance':686.54
        }])

    deftest_change_tax_line_account_when_tax_zero_percent(self):
        """
        Thistestchecksthefollowingflow:
        -Invoicewiththreeinvoicelines:
            •Onewithtax>0%
            •Onewithtax==0%
            •Onewithtax==0fixed
        -Online_ids,changetheaccountofthetaxline
        Thetaxlineshouldstillbethereandtheaccountshouldbeeffectivelychanged
        """
        tax_0_percent,tax_0_fixed=self.env['account.tax'].create([
            {
                'name':'0%',
                'amount_type':'percent',
                'amount':0,
                'sequence':10,
            },
            {
                'name':'0fixed',
                'amount_type':'fixed',
                'amount':0,
                'sequence':10,
            }
        ])


        new_account_revenue=self.company_data['default_account_revenue'].copy()

        invoice=self._create_invoice([(500,self.percent_tax_1),(300,tax_0_percent),(100,tax_0_fixed)],inv_type='out_invoice')

        self.assertRecordValues(invoice.line_ids,[
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'xxxx',
                'tax_ids':self.percent_tax_1.ids,
                'debit':0.0,
                'credit':500.0,
            },
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'xxxx',
                'tax_ids':tax_0_percent.ids,
                'debit':0.0,
                'credit':300.0,
            },
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'xxxx',
                'tax_ids':tax_0_fixed.ids,
                'debit':0.0,
                'credit':100.0,
            },
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'21%',
                'tax_ids':[],
                'debit':0.0,
                'credit':105.0,
            },
            {
                'account_id':self.company_data['default_account_receivable'].id,
                'name':'',
                'tax_ids':[],
                'debit':1005.0,
                'credit':0.0,
            }
        ])

        withForm(invoice)asinvoice_form:
            withinvoice_form.line_ids.edit(3)asline:
                line.account_id=new_account_revenue

        self.assertRecordValues(invoice.line_ids,[
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'xxxx',
                'tax_ids':self.percent_tax_1.ids,
                'debit':0.0,
                'credit':500.0,
            },
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'xxxx',
                'tax_ids':tax_0_percent.ids,
                'debit':0.0,
                'credit':300.0,
            },
            {
                'account_id':self.company_data['default_account_revenue'].id,
                'name':'xxxx',
                'tax_ids':tax_0_fixed.ids,
                'debit':0.0,
                'credit':100.0,
            },
            {
                'account_id':new_account_revenue.id,
                'name':'21%',
                'tax_ids':[],
                'debit':0.0,
                'credit':105.0,
            },
            {
                'account_id':self.company_data['default_account_receivable'].id,
                'name':'',
                'tax_ids':[],
                'debit':1005.0,
                'credit':0.0,
            }
        ])
