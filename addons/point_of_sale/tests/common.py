#-*-coding:utf-8-*-
fromrandomimportrandint
fromdatetimeimportdatetime

fromflectraimportfields,tools
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.tests.commonimportSavepointCase,Form
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestPointOfSaleCommon(ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].write({
            'point_of_sale_update_stock_quantities':'real',
        })

        cls.AccountBankStatement=cls.env['account.bank.statement']
        cls.AccountBankStatementLine=cls.env['account.bank.statement.line']
        cls.PosMakePayment=cls.env['pos.make.payment']
        cls.PosOrder=cls.env['pos.order']
        cls.PosSession=cls.env['pos.session']
        cls.company=cls.company_data['company']
        cls.product3=cls.env['product.product'].create({
            'name':'Product3',
            'list_price':450,
        })
        cls.product4=cls.env['product.product'].create({
            'name':'Product4',
            'list_price':750,
        })
        cls.partner1=cls.env['res.partner'].create({'name':'Partner1'})
        cls.partner4=cls.env['res.partner'].create({'name':'Partner4'})
        cls.pos_config=cls.env['pos.config'].create({
            'name':'Main',
            'journal_id':cls.company_data['default_journal_sale'].id,
            'invoice_journal_id':cls.company_data['default_journal_sale'].id,
        })
        cls.led_lamp=cls.env['product.product'].create({
            'name':'LEDLamp',
            'available_in_pos':True,
            'list_price':0.90,
        })
        cls.whiteboard_pen=cls.env['product.product'].create({
            'name':'WhiteboardPen',
            'available_in_pos':True,
            'list_price':1.20,
        })
        cls.newspaper_rack=cls.env['product.product'].create({
            'name':'NewspaperRack',
            'available_in_pos':True,
            'list_price':1.28,
        })
        cls.cash_payment_method=cls.env['pos.payment.method'].create({
            'name':'Cash',
            'receivable_account_id':cls.company_data['default_account_receivable'].id,
            'is_cash_count':True,
            'cash_journal_id':cls.company_data['default_journal_cash'].id,
            'company_id':cls.env.company.id,
        })
        cls.bank_payment_method=cls.env['pos.payment.method'].create({
            'name':'Bank',
            'receivable_account_id':cls.company_data['default_account_receivable'].id,
            'is_cash_count':False,
            'company_id':cls.env.company.id,
        })
        cls.credit_payment_method=cls.env['pos.payment.method'].create({
            'name':'Credit',
            'receivable_account_id':cls.company_data['default_account_receivable'].id,
            'split_transactions':True,
            'company_id':cls.env.company.id,
        })
        cls.pos_config.write({'payment_method_ids':[(4,cls.credit_payment_method.id),(4,cls.bank_payment_method.id),(4,cls.cash_payment_method.id)]})

        #CreatePOSjournal
        cls.pos_config.journal_id=cls.env['account.journal'].create({
            'type':'sale',
            'name':'PointofSale-Test',
            'code':'POSS-Test',
            'company_id':cls.env.company.id,
            'sequence':20
        })

        #createaVATtaxof10%,includedinthepublicprice
        Tax=cls.env['account.tax']
        account_tax_10_incl=Tax.create({
            'name':'VAT10percIncl',
            'amount_type':'percent',
            'amount':10.0,
            'price_include':True,
        })

        #assignthis10percenttaxonthe[PCSC234]PCAssembleSC234product
        #asasaletax
        cls.product3.taxes_id=[(6,0,[account_tax_10_incl.id])]

        #createaVATtaxof5%,whichisaddedtothepublicprice
        account_tax_05_incl=Tax.create({
            'name':'VAT5percIncl',
            'amount_type':'percent',
            'amount':5.0,
            'price_include':False,
        })

        #createasecondVATtaxof5%butthistimeforachildcompany,to
        #ensurethatonlyproducttaxesofthecurrentsession'scompanyareconsidered
        #(thistaxshouldbeignorewhencomputingorder'staxesinfollowingtests)
        account_tax_05_incl_chicago=Tax.create({
            'name':'VAT05percExcl(US)',
            'amount_type':'percent',
            'amount':5.0,
            'price_include':False,
            'company_id':cls.company_data_2['company'].id,
        })

        cls.product4.company_id=False
        #Iassignthose5percenttaxesonthePCSC349productasasaletaxes
        cls.product4.write(
            {'taxes_id':[(6,0,[account_tax_05_incl.id,account_tax_05_incl_chicago.id])]})

        #Setaccount_idinthegeneratedrepartitionlines.Automatically,nothingisset.
        invoice_rep_lines=(account_tax_05_incl|account_tax_10_incl).mapped('invoice_repartition_line_ids')
        refund_rep_lines=(account_tax_05_incl|account_tax_10_incl).mapped('refund_repartition_line_ids')

        #Expenseaccount,shouldjustbesomethingelsethanreceivable/payable
        (invoice_rep_lines|refund_rep_lines).write({'account_id':cls.company_data['default_account_tax_sale'].id})


@tagged('post_install','-at_install')
classTestPoSCommon(ValuationReconciliationTestCommon):
    """Setcommonvaluesfordifferentspecialtestcases.

    Theideaistosetupcommonvalueshereforthetests
    andimplementdifferentspecialscenariosbyinheriting
    thisclass.
    """

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].write({
            'point_of_sale_update_stock_quantities':'real',
            'country_id':cls.env['res.country'].create({
                'name':'PoSLand',
                'code':'WOW',
            }),
        })

        #Setbasicdefaults
        cls.company=cls.company_data['company']
        cls.pos_sale_journal=cls.env['account.journal'].create({
            'type':'sale',
            'name':'PointofSaleTest',
            'code':'POST',
            'company_id':cls.company.id,
            'sequence':20
        })
        cls.invoice_journal=cls.company_data['default_journal_sale']
        cls.receivable_account=cls.company_data['default_account_receivable']
        cls.tax_received_account=cls.company_data['default_account_tax_sale']
        cls.company.account_default_pos_receivable_account_id=cls.env['account.account'].create({
            'code':'X1012-POS',
            'name':'Debtors-(POS)',
            'reconcile':True,
            'user_type_id':cls.env.ref('account.data_account_type_receivable').id,
        })
        cls.pos_receivable_account=cls.company.account_default_pos_receivable_account_id
        cls.other_receivable_account=cls.env['account.account'].create({
            'name':'OtherReceivable',
            'code':'RCV00',
            'user_type_id':cls.env['account.account.type'].create({'name':'RCVtype','type':'receivable','internal_group':'asset'}).id,
            'internal_group':'asset',
            'reconcile':True,
        })

        #company_currencycanbedifferentfrom`base.USD`dependingonthelocalizationinstalled
        cls.company_currency=cls.company.currency_id
        #other_currencyisacurrencydifferentfromthecompany_currency
        #sometimescompany_currencyisdifferentfromUSD,sohandleappropriately.
        cls.other_currency=cls.currency_data['currency']

        cls.currency_pricelist=cls.env['product.pricelist'].create({
            'name':'PublicPricelist',
            'currency_id':cls.company_currency.id,
        })
        #SetPointofSaleconfigurations
        #basic_config
        #  -derivedfrom'point_of_sale.pos_config_main'withaddedinvoice_journal_idandcreditpaymentmethod.
        #other_currency_config
        #  -pos.configsettohavecurrencydifferentfromcompanycurrency.
        cls.basic_config=cls._create_basic_config()
        cls.other_currency_config=cls._create_other_currency_config()

        #Setproductcategories
        #categ_basic
        #  -justtheplain'product.product_category_all'
        #categ_anglo
        #  -productcategorywithfifoandreal_timevaluations
        #  -usedforcheckinganglosaxonaccountingbehavior
        cls.categ_basic=cls.env.ref('product.product_category_all')
        cls.env.company.anglo_saxon_accounting=True
        cls.categ_anglo=cls._create_categ_anglo()

        #otherbasics
        cls.sale_account=cls.categ_basic.property_account_income_categ_id
        cls.other_sale_account=cls.env['account.account'].search([
            ('company_id','=',cls.company.id),
            ('user_type_id','=',cls.env.ref('account.data_account_type_revenue').id),
            ('id','!=',cls.sale_account.id)
        ],limit=1)

        #Setcustomers
        cls.customer=cls.env['res.partner'].create({'name':'TestCustomer'})
        cls.other_customer=cls.env['res.partner'].create({'name':'OtherCustomer','property_account_receivable_id':cls.other_receivable_account.id})

        #Settaxes
        #cls.taxes=>dict
        #  keys:'tax7','tax10'(price_include=True),'tax_group_7_10'
        cls.taxes=cls._create_taxes()

        cls.stock_location_components=cls.env["stock.location"].create({
            'name':'Shelf1',
            'location_id':cls.company_data['default_warehouse'].lot_stock_id.id,
        })


    #####################
    ##privatemethods##
    #####################

    @classmethod
    def_create_basic_config(cls):
        new_config=Form(cls.env['pos.config'])
        new_config.name='PoSShopTest'
        new_config.module_account=True
        new_config.invoice_journal_id=cls.invoice_journal
        new_config.journal_id=cls.pos_sale_journal
        new_config.available_pricelist_ids.clear()
        new_config.available_pricelist_ids.add(cls.currency_pricelist)
        new_config.pricelist_id=cls.currency_pricelist
        config=new_config.save()
        cash_payment_method=cls.env['pos.payment.method'].create({
            'name':'Cash',
            'receivable_account_id':cls.pos_receivable_account.id,
            'is_cash_count':True,
            'cash_journal_id':cls.company_data['default_journal_cash'].id,
            'company_id':cls.env.company.id,
        })
        bank_payment_method=cls.env['pos.payment.method'].create({
            'name':'Bank',
            'receivable_account_id':cls.pos_receivable_account.id,
            'is_cash_count':False,
            'company_id':cls.env.company.id,
        })
        cash_split_pm=cls.env['pos.payment.method'].create({
            'name':'Split(Cash)PM',
            'receivable_account_id':cls.pos_receivable_account.id,
            'split_transactions':True,
            'is_cash_count':True,
            'cash_journal_id':cls.company_data['default_journal_cash'].id,
        })
        bank_split_pm=cls.env['pos.payment.method'].create({
            'name':'Split(Bank)PM',
            'receivable_account_id':cls.pos_receivable_account.id,
            'split_transactions':True,
        })
        config.write({'payment_method_ids':[(4,cash_split_pm.id),(4,bank_split_pm.id),(4,cash_payment_method.id),(4,bank_payment_method.id)]})
        returnconfig

    @classmethod
    def_create_other_currency_config(cls):
        (cls.other_currency.rate_ids|cls.company_currency.rate_ids).unlink()
        cls.env['res.currency.rate'].create({
            'rate':0.5,
            'currency_id':cls.other_currency.id,
            'name':datetime.today().date(),
        })
        other_cash_journal=cls.env['account.journal'].create({
            'name':'CashOther',
            'type':'cash',
            'company_id':cls.company.id,
            'code':'CSHO',
            'sequence':10,
            'currency_id':cls.other_currency.id
        })
        other_invoice_journal=cls.env['account.journal'].create({
            'name':'CustomerInvoiceOther',
            'type':'sale',
            'company_id':cls.company.id,
            'code':'INVO',
            'sequence':11,
            'currency_id':cls.other_currency.id
        })
        other_sales_journal=cls.env['account.journal'].create({
            'name':'PoSSaleOther',
            'type':'sale',
            'code':'POSO',
            'company_id':cls.company.id,
            'sequence':12,
            'currency_id':cls.other_currency.id
        })
        other_pricelist=cls.env['product.pricelist'].create({
            'name':'PublicPricelistOther',
            'currency_id':cls.other_currency.id,
        })
        other_cash_payment_method=cls.env['pos.payment.method'].create({
            'name':'CashOther',
            'receivable_account_id':cls.pos_receivable_account.id,
            'is_cash_count':True,
            'cash_journal_id':other_cash_journal.id,
        })
        other_bank_payment_method=cls.env['pos.payment.method'].create({
            'name':'BankOther',
            'receivable_account_id':cls.pos_receivable_account.id,
        })

        new_config=Form(cls.env['pos.config'])
        new_config.name='ShopOther'
        new_config.invoice_journal_id=other_invoice_journal
        new_config.journal_id=other_sales_journal
        new_config.use_pricelist=True
        new_config.available_pricelist_ids.clear()
        new_config.available_pricelist_ids.add(other_pricelist)
        new_config.pricelist_id=other_pricelist
        new_config.payment_method_ids.clear()
        new_config.payment_method_ids.add(other_cash_payment_method)
        new_config.payment_method_ids.add(other_bank_payment_method)
        config=new_config.save()
        returnconfig

    @classmethod
    def_create_categ_anglo(cls):
        returncls.env['product.category'].create({
            'name':'Anglo',
            'parent_id':False,
            'property_cost_method':'fifo',
            'property_valuation':'real_time',
            'property_stock_account_input_categ_id':cls.company_data['default_account_stock_in'].id,
            'property_stock_account_output_categ_id':cls.company_data['default_account_stock_out'].id,
        })

    @classmethod
    def_create_taxes(cls):
        """Createtaxes

        tax7:7%,excludedinproductprice
        tax10:10%,includedinproductprice
        tax21:21%,includedinproductprice
        """
        defcreate_tag(name):
            returncls.env['account.account.tag'].create({
                'name':name,
                'applicability':'taxes',
                'country_id':cls.env.company.country_id.id
            })

        cls.tax_tag_invoice_base=create_tag('InvoiceBasetag')
        cls.tax_tag_invoice_tax=create_tag('InvoiceTaxtag')
        cls.tax_tag_refund_base=create_tag('RefundBasetag')
        cls.tax_tag_refund_tax=create_tag('RefundTaxtag')

        defcreate_tax(percentage,price_include=False):
            returncls.env['account.tax'].create({
                'name':f'Tax{percentage}%',
                'amount':percentage,
                'price_include':price_include,
                'amount_type':'percent',
                'include_base_amount':False,
                'invoice_repartition_line_ids':[
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'base',
                        'tag_ids':[(6,0,cls.tax_tag_invoice_base.ids)],
                    }),
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'tax',
                        'account_id':cls.tax_received_account.id,
                        'tag_ids':[(6,0,cls.tax_tag_invoice_tax.ids)],
                    }),
                ],
                'refund_repartition_line_ids':[
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'base',
                        'tag_ids':[(6,0,cls.tax_tag_refund_base.ids)],
                    }),
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'tax',
                        'account_id':cls.tax_received_account.id,
                        'tag_ids':[(6,0,cls.tax_tag_refund_tax.ids)],
                    }),
                ],
            })
        defcreate_tax_fixed(amount,price_include=False):
            returncls.env['account.tax'].create({
                'name':f'Taxfixedamount{amount}',
                'amount':amount,
                'price_include':price_include,
                'include_base_amount':price_include,
                'amount_type':'fixed',
                'invoice_repartition_line_ids':[
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'base',
                        'tag_ids':[(6,0,cls.tax_tag_invoice_base.ids)],
                    }),
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'tax',
                        'account_id':cls.tax_received_account.id,
                        'tag_ids':[(6,0,cls.tax_tag_invoice_tax.ids)],
                    }),
                ],
                'refund_repartition_line_ids':[
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'base',
                        'tag_ids':[(6,0,cls.tax_tag_refund_base.ids)],
                    }),
                    (0,0,{
                        'factor_percent':100,
                        'repartition_type':'tax',
                        'account_id':cls.tax_received_account.id,
                        'tag_ids':[(6,0,cls.tax_tag_refund_tax.ids)],
                    }),
                ],
            })

        tax_fixed006=create_tax_fixed(0.06,price_include=True)
        tax_fixed012=create_tax_fixed(0.12,price_include=True)
        tax7=create_tax(7,price_include=False)
        tax10=create_tax(10,price_include=True)
        tax21=create_tax(21,price_include=True)


        tax_group_7_10=tax7.copy()
        withForm(tax_group_7_10)astax:
            tax.name='Tax7+10%'
            tax.amount_type='group'
            tax.children_tax_ids.add(tax7)
            tax.children_tax_ids.add(tax10)

        return{
            'tax7':tax7,
            'tax10':tax10,
            'tax21':tax21,
            'tax_fixed006':tax_fixed006,
            'tax_fixed012':tax_fixed012,
            'tax_group_7_10':tax_group_7_10
        }

    ####################
    ##publicmethods##
    ####################

    defcreate_random_uid(self):
        return('%05d-%03d-%04d'%(randint(1,99999),randint(1,999),randint(1,9999)))

    defcreate_ui_order_data(self,product_quantity_discount_triplet,customer=False,is_invoiced=False,payments=None,uid=None):
        """Mockstheorder_datageneratedbytheposui.

        Thisisusefulinmakingordersinanopenpossessionwithoutmakingtours.
        Itsfunctionalityistestedintest_pos_create_ui_order_data.py.

        Beforeuse,makesurethatselfissetwith:
            1.pricelist->thepricelistofthecurrentsession
            2.currency->currencyofthecurrentsession
            3.pos_session->thecurrentsession,equivalenttoconfig.current_session_id
            4.cash_pm->firstcashpaymentmethodinthecurrentsession
            5.config->theactivepos.config

        Theabovevaluesshouldbesetwhen`self.open_new_session`iscalled.

        :paramlist(tuple)product_quantity_discount_triplet:pairsof`orderedproduct`and`quantity`
        ortripletof`orderedproduct`,`quantity`anddiscount
        :paramlist(tuple)payments:pairof`payment_method`and`amount`
        """
        default_fiscal_position=self.config.default_fiscal_position_id
        fiscal_position=customer.property_account_position_idifcustomerelsedefault_fiscal_position

        defcreate_order_line(product,quantity,discount=0.0):
            price_unit=self.pricelist.get_product_price(product,quantity,False)
            tax_ids=fiscal_position.map_tax(product.taxes_id)
            price_unit_after_discount=price_unit*(1-discount/100.0)
            tax_values=(
                tax_ids.compute_all(price_unit_after_discount,self.currency,quantity)
                iftax_ids
                else{
                    'total_excluded':price_unit*quantity,
                    'total_included':price_unit*quantity,
                }
            )
            return(0,0,{
                'discount':discount,
                'id':randint(1,1000000),
                'pack_lot_ids':[],
                'price_unit':price_unit,
                'product_id':product.id,
                'price_subtotal':tax_values['total_excluded'],
                'price_subtotal_incl':tax_values['total_included'],
                'qty':quantity,
                'tax_ids':[(6,0,tax_ids.ids)]
            })

        defcreate_payment(payment_method,amount):
            return(0,0,{
                'amount':amount,
                'name':fields.Datetime.now(),
                'payment_method_id':payment_method.id,
            })

        uid=uidorself.create_random_uid()

        #1.generatetheorderlines
        order_lines=[
            create_order_line(product,quantity,discountanddiscount[0]or0.0)
            forproduct,quantity,*discount
            inproduct_quantity_discount_triplet
        ]

        #2.generatethepayments
        total_amount_incl=sum(line[2]['price_subtotal_incl']forlineinorder_lines)
        ifpaymentsisNone:
            payments=[create_payment(self.cash_pm,total_amount_incl)]
        else:
            payments=[
                create_payment(pm,amount)
                forpm,amountinpayments
            ]

        #3.completethefieldsoftheorder_data
        total_amount_base=sum(line[2]['price_subtotal']forlineinorder_lines)
        return{
            'data':{
                'amount_paid':sum(payment[2]['amount']forpaymentinpayments),
                'amount_return':0,
                'amount_tax':total_amount_incl-total_amount_base,
                'amount_total':total_amount_incl,
                'creation_date':fields.Datetime.to_string(fields.Datetime.now()),
                'fiscal_position_id':fiscal_position.id,
                'pricelist_id':self.config.pricelist_id.id,
                'lines':order_lines,
                'name':'Order%s'%uid,
                'partner_id':customerandcustomer.id,
                'pos_session_id':self.pos_session.id,
                'sequence_number':2,
                'statement_ids':payments,
                'uid':uid,
                'user_id':self.env.user.id,
                'to_invoice':is_invoiced,
            },
            'id':uid,
            'to_invoice':is_invoiced,
        }

    @classmethod
    defcreate_product(cls,name,category,lst_price,standard_price=None,tax_ids=None,sale_account=None):
        product=cls.env['product.product'].create({
            'type':'product',
            'available_in_pos':True,
            'taxes_id':[(5,0,0)]ifnottax_idselse[(6,0,tax_ids)],
            'name':name,
            'categ_id':category.id,
            'lst_price':lst_price,
            'standard_price':standard_priceifstandard_priceelse0.0,
        })
        ifsale_account:
            product.property_account_income_id=sale_account
        returnproduct

    @classmethod
    defadjust_inventory(cls,products,quantities):
        """Adjustinventoryofthegivenproducts
        """
        inventory=cls.env['stock.inventory'].create({
            'name':'Inventoryadjustment'
        })
        forproduct,qtyinzip(products,quantities):
            cls.env['stock.inventory.line'].create({
                'product_id':product.id,
                'product_uom_id':cls.env.ref('uom.product_uom_unit').id,
                'inventory_id':inventory.id,
                'product_qty':qty,
                'location_id':cls.stock_location_components.id,
            })
        inventory._action_start()
        inventory.action_validate()

    defopen_new_session(self):
        """Usedtoopennewpossessionineachconfiguration.

        -Theideaistoproperlysetvaluesthatareconstant
          andcommonlyusedinanopenpossession.
        -Callingthismethodisalsoaprerequisiteforusing
          `self.create_ui_order_data`function.

        Fields:
            *config:thepos.configcurrentlybeingused.
                Itsvalueissetat`self.setUp`oftheinheriting
                testclass.
            *session:thecurrent_session_idofconfig
            *currency:currencyofthecurrentpos.session
            *pricelist:thedefaultpricelistofthesession
            *cash_pm:cashpaymentmethodofthesession
            *bank_pm:bankpaymentmethodofthesession
            *cash_split_pm:creditpaymentmethodofthesession
            *bank_split_pm:splitbankpaymentmethodofthesession
        """
        self.config.open_session_cb(check_coa=False)
        self.pos_session=self.config.current_session_id
        self.currency=self.pos_session.currency_id
        self.pricelist=self.pos_session.config_id.pricelist_id
        self.cash_pm=self.pos_session.payment_method_ids.filtered(lambdapm:pm.is_cash_countandnotpm.split_transactions)[:1]
        self.bank_pm=self.pos_session.payment_method_ids.filtered(lambdapm:notpm.is_cash_countandnotpm.split_transactions)[:1]
        self.cash_split_pm=self.pos_session.payment_method_ids.filtered(lambdapm:pm.is_cash_countandpm.split_transactions)[:1]
        self.bank_split_pm=self.pos_session.payment_method_ids.filtered(lambdapm:notpm.is_cash_countandpm.split_transactions)[:1]
