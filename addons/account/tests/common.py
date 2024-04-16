#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields
fromflectra.tests.commonimportSavepointCase,HttpSavepointCase,tagged,Form

importtime
importbase64
fromlxmlimportetree

@tagged('post_install','-at_install')
classAccountTestInvoicingCommon(SavepointCase):

    @classmethod
    defcopy_account(cls,account):
        suffix_nb=1
        whileTrue:
            new_code='%s(%s)'%(account.code,suffix_nb)
            ifaccount.search_count([('company_id','=',account.company_id.id),('code','=',new_code)]):
                suffix_nb+=1
            else:
                returnaccount.copy(default={'code':new_code})

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super(AccountTestInvoicingCommon,cls).setUpClass()

        assert'post_install'incls.test_tags,'ThistestrequiresaCoAtobeinstalled,itshouldbetagged"post_install"'

        ifchart_template_ref:
            chart_template=cls.env.ref(chart_template_ref)
        else:
            chart_template=cls.env.ref('l10n_generic_coa.configurable_chart_template',raise_if_not_found=False)
        ifnotchart_template:
            cls.tearDownClass()
            #skipTestraisesexception
            cls.skipTest(cls,"AccountingTestsskippedbecausetheuser'scompanyhasnochartofaccounts.")

        #Createuser.
        user=cls.env['res.users'].create({
            'name':'BecauseIamaccountman!',
            'login':'accountman',
            'password':'accountman',
            'groups_id':[(6,0,cls.env.user.groups_id.ids),(4,cls.env.ref('account.group_account_user').id)],
        })
        user.partner_id.email='accountman@test.com'

        #Shadowthecurrentenvironment/cursorwithonehavingthereportuser.
        #Thisismandatorytotestaccessrights.
        cls.env=cls.env(user=user)
        cls.cr=cls.env.cr

        cls.company_data_2=cls.setup_company_data('company_2_data',chart_template=chart_template)
        cls.company_data=cls.setup_company_data('company_1_data',chart_template=chart_template)

        user.write({
            'company_ids':[(6,0,(cls.company_data['company']+cls.company_data_2['company']).ids)],
            'company_id':cls.company_data['company'].id,
        })

        cls.currency_data=cls.setup_multi_currency_data()

        #====Taxes====
        cls.tax_sale_a=cls.company_data['default_tax_sale']
        cls.tax_sale_b=cls.company_data['default_tax_sale'].copy()
        cls.tax_purchase_a=cls.company_data['default_tax_purchase']
        cls.tax_purchase_b=cls.company_data['default_tax_purchase'].copy()
        cls.tax_armageddon=cls.setup_armageddon_tax('complex_tax',cls.company_data)

        #====Products====
        cls.product_a=cls.env['product.product'].create({
            'name':'product_a',
            'uom_id':cls.env.ref('uom.product_uom_unit').id,
            'lst_price':1000.0,
            'standard_price':800.0,
            'property_account_income_id':cls.company_data['default_account_revenue'].id,
            'property_account_expense_id':cls.company_data['default_account_expense'].id,
            'taxes_id':[(6,0,cls.tax_sale_a.ids)],
            'supplier_taxes_id':[(6,0,cls.tax_purchase_a.ids)],
        })
        cls.product_b=cls.env['product.product'].create({
            'name':'product_b',
            'uom_id':cls.env.ref('uom.product_uom_dozen').id,
            'lst_price':200.0,
            'standard_price':160.0,
            'property_account_income_id':cls.copy_account(cls.company_data['default_account_revenue']).id,
            'property_account_expense_id':cls.copy_account(cls.company_data['default_account_expense']).id,
            'taxes_id':[(6,0,(cls.tax_sale_a+cls.tax_sale_b).ids)],
            'supplier_taxes_id':[(6,0,(cls.tax_purchase_a+cls.tax_purchase_b).ids)],
        })

        #====Fiscalpositions====
        cls.fiscal_pos_a=cls.env['account.fiscal.position'].create({
            'name':'fiscal_pos_a',
            'tax_ids':[
                (0,None,{
                    'tax_src_id':cls.tax_sale_a.id,
                    'tax_dest_id':cls.tax_sale_b.id,
                }),
                (0,None,{
                    'tax_src_id':cls.tax_purchase_a.id,
                    'tax_dest_id':cls.tax_purchase_b.id,
                }),
            ],
            'account_ids':[
                (0,None,{
                    'account_src_id':cls.product_a.property_account_income_id.id,
                    'account_dest_id':cls.product_b.property_account_income_id.id,
                }),
                (0,None,{
                    'account_src_id':cls.product_a.property_account_expense_id.id,
                    'account_dest_id':cls.product_b.property_account_expense_id.id,
                }),
            ],
        })

        #====Paymentterms====
        cls.pay_terms_a=cls.env.ref('account.account_payment_term_immediate')
        cls.pay_terms_b=cls.env['account.payment.term'].create({
            'name':'30%AdvanceEndofFollowingMonth',
            'note':'Paymentterms:30%AdvanceEndofFollowingMonth',
            'line_ids':[
                (0,0,{
                    'value':'percent',
                    'value_amount':30.0,
                    'sequence':400,
                    'days':0,
                    'option':'day_after_invoice_date',
                }),
                (0,0,{
                    'value':'balance',
                    'value_amount':0.0,
                    'sequence':500,
                    'days':31,
                    'option':'day_following_month',
                }),
            ],
        })

        #====Partners====
        cls.partner_a=cls.env['res.partner'].create({
            'name':'partner_a',
            'property_payment_term_id':cls.pay_terms_a.id,
            'property_supplier_payment_term_id':cls.pay_terms_a.id,
            'property_account_receivable_id':cls.company_data['default_account_receivable'].id,
            'property_account_payable_id':cls.company_data['default_account_payable'].id,
            'company_id':False,
        })
        cls.partner_b=cls.env['res.partner'].create({
            'name':'partner_b',
            'property_payment_term_id':cls.pay_terms_b.id,
            'property_supplier_payment_term_id':cls.pay_terms_b.id,
            'property_account_position_id':cls.fiscal_pos_a.id,
            'property_account_receivable_id':cls.company_data['default_account_receivable'].copy().id,
            'property_account_payable_id':cls.company_data['default_account_payable'].copy().id,
            'company_id':False,
        })

        #====Cashrounding====
        cls.cash_rounding_a=cls.env['account.cash.rounding'].create({
            'name':'add_invoice_line',
            'rounding':0.05,
            'strategy':'add_invoice_line',
            'profit_account_id':cls.company_data['default_account_revenue'].copy().id,
            'loss_account_id':cls.company_data['default_account_expense'].copy().id,
            'rounding_method':'UP',
        })
        cls.cash_rounding_b=cls.env['account.cash.rounding'].create({
            'name':'biggest_tax',
            'rounding':0.05,
            'strategy':'biggest_tax',
            'rounding_method':'DOWN',
        })

    @classmethod
    defsetup_company_data(cls,company_name,chart_template=None,**kwargs):
        '''Createanewcompanyhavingthenamepassedasparameter.
        Achartofaccountswillbeinstalledtothiscompany:thesameasthecurrentcompanyone.
        Thecurrentuserwillgetaccesstothiscompany.

        :paramchart_template:Thecharttemplatetobeusedonthisnewcompany.
        :paramcompany_name:Thenameofthecompany.
        :return:Adictionarywillbereturnedcontainingallrelevantaccountingdatafortesting.
        '''
        defsearch_account(company,chart_template,field_name,domain):
            template_code=chart_template[field_name].code
            domain=[('company_id','=',company.id)]+domain

            account=None
            iftemplate_code:
                account=cls.env['account.account'].search(domain+[('code','=like',template_code+'%')],limit=1)

            ifnotaccount:
                account=cls.env['account.account'].search(domain,limit=1)
            returnaccount

        chart_template=chart_templateorcls.env.company.chart_template_id
        company=cls.env['res.company'].create({
            'name':company_name,
            **kwargs,
        })
        cls.env.user.company_ids|=company

        chart_template.try_loading(company=company)

        #Thecurrencycouldbedifferentaftertheinstallationofthecharttemplate.
        ifkwargs.get('currency_id'):
            company.write({'currency_id':kwargs['currency_id']})

        return{
            'company':company,
            'currency':company.currency_id,
            'default_account_revenue':cls.env['account.account'].search([
                    ('company_id','=',company.id),
                    ('user_type_id','=',cls.env.ref('account.data_account_type_revenue').id)
                ],limit=1),
            'default_account_expense':cls.env['account.account'].search([
                    ('company_id','=',company.id),
                    ('user_type_id','=',cls.env.ref('account.data_account_type_expenses').id)
                ],limit=1),
            'default_account_receivable':search_account(company,chart_template,'property_account_receivable_id',[
                ('user_type_id.type','=','receivable')
            ]),
            'default_account_payable':cls.env['account.account'].search([
                    ('company_id','=',company.id),
                    ('user_type_id.type','=','payable')
                ],limit=1),
            'default_account_assets':cls.env['account.account'].search([
                    ('company_id','=',company.id),
                    ('user_type_id','=',cls.env.ref('account.data_account_type_current_assets').id)
                ],limit=1),
            'default_account_tax_sale':company.account_sale_tax_id.mapped('invoice_repartition_line_ids.account_id'),
            'default_account_tax_purchase':company.account_purchase_tax_id.mapped('invoice_repartition_line_ids.account_id'),
            'default_journal_misc':cls.env['account.journal'].search([
                    ('company_id','=',company.id),
                    ('type','=','general')
                ],limit=1),
            'default_journal_sale':cls.env['account.journal'].search([
                    ('company_id','=',company.id),
                    ('type','=','sale')
                ],limit=1),
            'default_journal_purchase':cls.env['account.journal'].search([
                    ('company_id','=',company.id),
                    ('type','=','purchase')
                ],limit=1),
            'default_journal_bank':cls.env['account.journal'].search([
                    ('company_id','=',company.id),
                    ('type','=','bank')
                ],limit=1),
            'default_journal_cash':cls.env['account.journal'].search([
                    ('company_id','=',company.id),
                    ('type','=','cash')
                ],limit=1),
            'default_tax_sale':company.account_sale_tax_id,
            'default_tax_purchase':company.account_purchase_tax_id,
        }

    @classmethod
    defsetup_multi_currency_data(cls,default_values={},rate2016=3.0,rate2017=2.0):
        foreign_currency=cls.env['res.currency'].create({
            'name':'GoldCoin',
            'symbol':'☺',
            'rounding':0.001,
            'position':'after',
            'currency_unit_label':'Gold',
            'currency_subunit_label':'Silver',
            **default_values,
        })
        rate1=cls.env['res.currency.rate'].create({
            'name':'2016-01-01',
            'rate':rate2016,
            'currency_id':foreign_currency.id,
            'company_id':cls.env.company.id,
        })
        rate2=cls.env['res.currency.rate'].create({
            'name':'2017-01-01',
            'rate':rate2017,
            'currency_id':foreign_currency.id,
            'company_id':cls.env.company.id,
        })
        return{
            'currency':foreign_currency,
            'rates':rate1+rate2,
        }

    @classmethod
    defsetup_armageddon_tax(cls,tax_name,company_data):
        returncls.env['account.tax'].create({
            'name':'%s(group)'%tax_name,
            'amount_type':'group',
            'amount':0.0,
            'children_tax_ids':[
                (0,0,{
                    'name':'%s(child1)'%tax_name,
                    'amount_type':'percent',
                    'amount':20.0,
                    'price_include':True,
                    'include_base_amount':True,
                    'tax_exigibility':'on_invoice',
                    'invoice_repartition_line_ids':[
                        (0,0,{
                            'factor_percent':100,
                            'repartition_type':'base',
                        }),
                        (0,0,{
                            'factor_percent':40,
                            'repartition_type':'tax',
                            'account_id':company_data['default_account_tax_sale'].id,
                        }),
                        (0,0,{
                            'factor_percent':60,
                            'repartition_type':'tax',
                            #/!\Noaccountset.
                        }),
                    ],
                    'refund_repartition_line_ids':[
                        (0,0,{
                            'factor_percent':100,
                            'repartition_type':'base',
                        }),
                        (0,0,{
                            'factor_percent':40,
                            'repartition_type':'tax',
                            'account_id':company_data['default_account_tax_sale'].id,
                        }),
                        (0,0,{
                            'factor_percent':60,
                            'repartition_type':'tax',
                            #/!\Noaccountset.
                        }),
                    ],
                }),
                (0,0,{
                    'name':'%s(child2)'%tax_name,
                    'amount_type':'percent',
                    'amount':10.0,
                    'tax_exigibility':'on_payment',
                    'cash_basis_transition_account_id':company_data['default_account_tax_sale'].copy().id,
                    'invoice_repartition_line_ids':[
                        (0,0,{
                            'factor_percent':100,
                            'repartition_type':'base',
                        }),
                        (0,0,{
                            'factor_percent':100,
                            'repartition_type':'tax',
                            'account_id':company_data['default_account_tax_sale'].id,
                        }),
                    ],
                    'refund_repartition_line_ids':[
                        (0,0,{
                            'factor_percent':100,
                            'repartition_type':'base',
                        }),

                        (0,0,{
                            'factor_percent':100,
                            'repartition_type':'tax',
                            'account_id':company_data['default_account_tax_sale'].id,
                        }),
                    ],
                }),
            ],
        })

    @classmethod
    definit_invoice(cls,move_type,partner=None,invoice_date=None,post=False,products=None,amounts=None,taxes=None,currency=None):
        products=[]ifproductsisNoneelseproducts
        amounts=[]ifamountsisNoneelseamounts
        move_form=Form(cls.env['account.move'].with_context(default_move_type=move_type,account_predictive_bills_disable_prediction=True))
        move_form.invoice_date=invoice_dateorfields.Date.from_string('2019-01-01')
        move_form.date=move_form.invoice_date
        move_form.partner_id=partnerorcls.partner_a
        move_form.currency_id=currencyifcurrencyelsecls.company_data['currency']

        forproductinproducts:
            withmove_form.invoice_line_ids.new()asline_form:
                line_form.product_id=product
                iftaxes:
                    line_form.tax_ids.clear()
                    line_form.tax_ids.add(taxes)

        foramountinamounts:
            withmove_form.invoice_line_ids.new()asline_form:
                line_form.name="testline"
                #Weuseaccount_predictive_bills_disable_predictioncontextkeysothat
                #thisdoesn'ttriggerpredictionincaseenterprise(henceaccount_predictive_bills)isinstalled
                line_form.price_unit=amount
                iftaxes:
                    line_form.tax_ids.clear()
                    fortaxintaxes:
                        line_form.tax_ids.add(tax)

        rslt=move_form.save()

        ifpost:
            rslt.action_post()

        returnrslt

    defassertInvoiceValues(self,move,expected_lines_values,expected_move_values):
        defsort_lines(lines):
            returnlines.sorted(lambdaline:(line.exclude_from_invoice_tab,notbool(line.tax_line_id),line.nameor'',line.balance))
        self.assertRecordValues(sort_lines(move.line_ids.sorted()),expected_lines_values)
        self.assertRecordValues(sort_lines(move.invoice_line_ids.sorted()),expected_lines_values[:len(move.invoice_line_ids)])
        self.assertRecordValues(move,[expected_move_values])

    ####################################################
    #XmlComparison
    ####################################################

    def_turn_node_as_dict_hierarchy(self,node):
        '''Turnthenodeasapythondictionarytobecomparedlaterwithanotherone.
        Allowtoignorethemanagementofnamespaces.
        :paramnode:   Anodeinsideanxmltree.
        :return:       Apythondictionary.
        '''
        tag_split=node.tag.split('}')
        tag_wo_ns=tag_split[-1]
        attrib_wo_ns={k:vfork,vinnode.attrib.items()if'}'notink}
        return{
            'tag':tag_wo_ns,
            'namespace':Noneiflen(tag_split)<2elsetag_split[0],
            'text':(node.textor'').strip(),
            'attrib':attrib_wo_ns,
            'children':[self._turn_node_as_dict_hierarchy(child_node)forchild_nodeinnode.getchildren()],
        }

    defassertXmlTreeEqual(self,xml_tree,expected_xml_tree):
        '''Comparetwolxml.etree.
        :paramxml_tree:           Thecurrenttree.
        :paramexpected_xml_tree:  Theexpectedtree.
        '''

        defassertNodeDictEqual(node_dict,expected_node_dict):
            '''Comparenodescreatedbythe`_turn_node_as_dict_hierarchy`method.
            :paramnode_dict:          Thenodetocomparewith.
            :paramexpected_node_dict: Theexpectednode.
            '''
            #Checktag.
            self.assertEqual(node_dict['tag'],expected_node_dict['tag'])

            #Checkattributes.
            node_dict_attrib={k:'___ignore___'ifexpected_node_dict['attrib'].get(k)=='___ignore___'elsev
                                fork,vinnode_dict['attrib'].items()}
            expected_node_dict_attrib={k:vfork,vinexpected_node_dict['attrib'].items()ifv!='___remove___'}
            self.assertDictEqual(
                node_dict_attrib,
                expected_node_dict_attrib,
                "Elementattributesaredifferentfornode%s"%node_dict['tag'],
            )

            #Checktext.
            ifexpected_node_dict['text']!='___ignore___':
                self.assertEqual(
                    node_dict['text'],
                    expected_node_dict['text'],
                    "Elementtextaredifferentfornode%s"%node_dict['tag'],
                )

            #Checkchildren.
            self.assertEqual(
                [child['tag']forchildinnode_dict['children']],
                [child['tag']forchildinexpected_node_dict['children']],
                "Numberofchildrenelementsfornode%sisdifferent."%node_dict['tag'],
            )

            forchild_node_dict,expected_child_node_dictinzip(node_dict['children'],expected_node_dict['children']):
                assertNodeDictEqual(child_node_dict,expected_child_node_dict)

        assertNodeDictEqual(
            self._turn_node_as_dict_hierarchy(xml_tree),
            self._turn_node_as_dict_hierarchy(expected_xml_tree),
        )

    defwith_applied_xpath(self,xml_tree,xpath):
        '''Appliesthexpathtothexml_treepassedasparameter.
        :paramxml_tree:   Aninstanceofetree.
        :paramxpath:      Thexpathtoapplyasastring.
        :return:           Theresultingetreeafterapplyingthexpaths.
        '''
        diff_xml_tree=etree.fromstring('<data>%s</data>'%xpath)
        returnself.env['ir.ui.view'].apply_inheritance_specs(xml_tree,diff_xml_tree)

    defget_xml_tree_from_attachment(self,attachment):
        '''Extractaninstanceofetreefromanir.attachment.
        :paramattachment: Anir.attachment.
        :return:           Aninstanceofetree.
        '''
        returnetree.fromstring(base64.b64decode(attachment.with_context(bin_size=False).datas))

    defget_xml_tree_from_string(self,xml_tree_str):
        '''Convertthestringpassedasparametertoaninstanceofetree.
        :paramxml_tree_str:   Astringrepresentinganxml.
        :return:               Aninstanceofetree.
        '''
        returnetree.fromstring(xml_tree_str)


@tagged('post_install','-at_install')
classAccountTestInvoicingHttpCommon(AccountTestInvoicingCommon,HttpSavepointCase):
    pass


classTestAccountReconciliationCommon(AccountTestInvoicingCommon):

    """Testsforreconciliation(account.tax)

    Testusedtocheckthatwhendoingasaleorpurchaseinvoiceinadifferentcurrency,
    theresultwillbebalanced.
    """

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company=cls.company_data['company']
        cls.company.currency_id=cls.env.ref('base.EUR')

        cls.partner_agrolait=cls.env['res.partner'].create({
            'name':'DecoAddict',
            'is_company':True,
            'country_id':cls.env.ref('base.us').id,
        })
        cls.partner_agrolait_id=cls.partner_agrolait.id
        cls.currency_swiss_id=cls.env.ref("base.CHF").id
        cls.currency_usd_id=cls.env.ref("base.USD").id
        cls.currency_euro_id=cls.env.ref("base.EUR").id
        cls.account_rcv=cls.company_data['default_account_receivable']
        cls.account_rsa=cls.company_data['default_account_payable']
        cls.product=cls.env['product.product'].create({
            'name':'ProductProduct4',
            'standard_price':500.0,
            'list_price':750.0,
            'type':'consu',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })

        cls.bank_journal_euro=cls.env['account.journal'].create({'name':'Bank','type':'bank','code':'BNK67'})
        cls.account_euro=cls.bank_journal_euro.default_account_id

        cls.bank_journal_usd=cls.env['account.journal'].create({'name':'BankUS','type':'bank','code':'BNK68','currency_id':cls.currency_usd_id})
        cls.account_usd=cls.bank_journal_usd.default_account_id

        cls.fx_journal=cls.company.currency_exchange_journal_id
        cls.diff_income_account=cls.company.income_currency_exchange_account_id
        cls.diff_expense_account=cls.company.expense_currency_exchange_account_id

        cls.inbound_payment_method=cls.env['account.payment.method'].sudo().create({
            'name':'inbound',
            'code':'IN',
            'payment_type':'inbound',
        })

        cls.expense_account=cls.company_data['default_account_expense']
        #cashbasisintermediaryaccount
        cls.tax_waiting_account=cls.env['account.account'].create({
            'name':'TAX_WAIT',
            'code':'TWAIT',
            'user_type_id':cls.env.ref('account.data_account_type_current_liabilities').id,
            'reconcile':True,
            'company_id':cls.company.id,
        })
        #cashbasisfinalaccount
        cls.tax_final_account=cls.env['account.account'].create({
            'name':'TAX_TO_DEDUCT',
            'code':'TDEDUCT',
            'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
            'company_id':cls.company.id,
        })
        cls.tax_base_amount_account=cls.env['account.account'].create({
            'name':'TAX_BASE',
            'code':'TBASE',
            'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
            'company_id':cls.company.id,
        })
        cls.company.account_cash_basis_base_account_id=cls.tax_base_amount_account.id


        #Journals
        cls.purchase_journal=cls.company_data['default_journal_purchase']
        cls.cash_basis_journal=cls.env['account.journal'].create({
            'name':'CABA',
            'code':'CABA',
            'type':'general',
        })
        cls.general_journal=cls.company_data['default_journal_misc']

        #TaxCashBasis
        cls.tax_cash_basis=cls.env['account.tax'].create({
            'name':'cashbasis20%',
            'type_tax_use':'purchase',
            'company_id':cls.company.id,
            'amount':20,
            'tax_exigibility':'on_payment',
            'cash_basis_transition_account_id':cls.tax_waiting_account.id,
            'invoice_repartition_line_ids':[
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'base',
                    }),

                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'tax',
                        'account_id':cls.tax_final_account.id,
                    }),
                ],
            'refund_repartition_line_ids':[
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'base',
                    }),

                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'tax',
                        'account_id':cls.tax_final_account.id,
                    }),
                ],
        })
        cls.env['res.currency.rate'].create([
            {
                'currency_id':cls.env.ref('base.EUR').id,
                'name':'2010-01-02',
                'rate':1.0,
            },{
                'currency_id':cls.env.ref('base.USD').id,
                'name':'2010-01-02',
                'rate':1.2834,
            },{
                'currency_id':cls.env.ref('base.USD').id,
                'name':time.strftime('%Y-06-05'),
                'rate':1.5289,
            }
        ])

    def_create_invoice(self,move_type='out_invoice',invoice_amount=50,currency_id=None,partner_id=None,date_invoice=None,payment_term_id=False,auto_validate=False):
        date_invoice=date_invoiceortime.strftime('%Y')+'-07-01'

        invoice_vals={
            'move_type':move_type,
            'partner_id':partner_idorself.partner_agrolait_id,
            'invoice_date':date_invoice,
            'date':date_invoice,
            'invoice_line_ids':[(0,0,{
                'name':'productthatcost%s'%invoice_amount,
                'quantity':1,
                'price_unit':invoice_amount,
                'tax_ids':[(6,0,[])],
            })]
        }

        ifpayment_term_id:
            invoice_vals['invoice_payment_term_id']=payment_term_id

        ifcurrency_id:
            invoice_vals['currency_id']=currency_id

        invoice=self.env['account.move'].with_context(default_move_type=move_type).create(invoice_vals)
        ifauto_validate:
            invoice.action_post()
        returninvoice

    defcreate_invoice(self,move_type='out_invoice',invoice_amount=50,currency_id=None):
        returnself._create_invoice(move_type=move_type,invoice_amount=invoice_amount,currency_id=currency_id,auto_validate=True)

    defcreate_invoice_partner(self,move_type='out_invoice',invoice_amount=50,currency_id=None,partner_id=False,payment_term_id=False):
        returnself._create_invoice(
            move_type=move_type,
            invoice_amount=invoice_amount,
            currency_id=currency_id,
            partner_id=partner_id,
            payment_term_id=payment_term_id,
            auto_validate=True
        )

    defmake_payment(self,invoice_record,bank_journal,amount=0.0,amount_currency=0.0,currency_id=None,reconcile_param=[]):
        bank_stmt=self.env['account.bank.statement'].create({
            'journal_id':bank_journal.id,
            'date':time.strftime('%Y')+'-07-15',
            'name':'payment'+invoice_record.name,
            'line_ids':[(0,0,{
                'payment_ref':'payment',
                'partner_id':self.partner_agrolait_id,
                'amount':amount,
                'amount_currency':amount_currency,
                'foreign_currency_id':currency_id,
            })],
        })
        bank_stmt.button_post()

        bank_stmt.line_ids[0].reconcile(reconcile_param)
        returnbank_stmt

    defmake_customer_and_supplier_flows(self,invoice_currency_id,invoice_amount,bank_journal,amount,amount_currency,transaction_currency_id):
        #wecreateaninvoiceingiveninvoice_currency
        invoice_record=self.create_invoice(move_type='out_invoice',invoice_amount=invoice_amount,currency_id=invoice_currency_id)
        #weencodeapaymentonit,onthegivenbank_journalwithamount,amount_currencyandtransaction_currencygiven
        line=invoice_record.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        bank_stmt=self.make_payment(invoice_record,bank_journal,amount=amount,amount_currency=amount_currency,currency_id=transaction_currency_id,reconcile_param=[{'id':line.id}])
        customer_move_lines=bank_stmt.line_ids.line_ids

        #wecreateasupplierbillingiveninvoice_currency
        invoice_record=self.create_invoice(move_type='in_invoice',invoice_amount=invoice_amount,currency_id=invoice_currency_id)
        #weencodeapaymentonit,onthegivenbank_journalwithamount,amount_currencyandtransaction_currencygiven
        line=invoice_record.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        bank_stmt=self.make_payment(invoice_record,bank_journal,amount=-amount,amount_currency=-amount_currency,currency_id=transaction_currency_id,reconcile_param=[{'id':line.id}])
        supplier_move_lines=bank_stmt.line_ids.line_ids
        returncustomer_move_lines,supplier_move_lines
