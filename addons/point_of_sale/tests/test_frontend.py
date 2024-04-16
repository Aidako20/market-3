#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
fromflectra.apiimportEnvironment
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT
fromdatetimeimportdate,timedelta

importflectra.tests


classTestPointOfSaleHttpCommon(flectra.tests.HttpCase):

    defsetUp(self):
        super().setUp()
        env=self.env(user=self.env.ref('base.user_admin'))

        journal_obj=env['account.journal']
        account_obj=env['account.account']
        main_company=env.ref('base.main_company')
        self.main_pos_config=env.ref('point_of_sale.pos_config_main')

        env['res.partner'].create({
            'name':'DecoAddict',
        })

        account_receivable=account_obj.create({'code':'X1012',
                                                 'name':'AccountReceivable-Test',
                                                 'user_type_id':env.ref('account.data_account_type_receivable').id,
                                                 'reconcile':True})
        self.env.company.account_default_pos_receivable_account_id=account_receivable

        self.env['ir.property']._set_default('property_account_receivable_id','res.partner',account_receivable,main_company)

        cash_journal=journal_obj.create({
            'name':'CashTest',
            'type':'cash',
            'company_id':main_company.id,
            'code':'CSH',
            'sequence':10,
        })

        #Archiveallexistingproducttoavoidnoiseduringthetours
        all_pos_product=self.env['product.product'].search([('available_in_pos','=',True)])
        discount=self.env.ref('point_of_sale.product_product_consumable')
        self.tip=self.env.ref('point_of_sale.product_product_tip')
        (all_pos_product-discount-self.tip)._write({'active':False})

        #InDESKScateg:DeskPad
        pos_categ_desks=env.ref('point_of_sale.pos_category_desks')

        #InDESKScateg:WhiteboardPen
        pos_categ_misc=env.ref('point_of_sale.pos_category_miscellaneous')

        #InCHAIRcateg:LetterTray
        pos_categ_chairs=env.ref('point_of_sale.pos_category_chairs')

        #testanextrapriceonanattribute
        pear=env['product.product'].create({
            'name':'WhiteboardPen',
            'available_in_pos':True,
            'list_price':1.20,
            'taxes_id':False,
            'weight':0.01,
            'to_weight':True,
            'pos_categ_id':pos_categ_misc.id,
        })
        wall_shelf=env['product.product'].create({
            'name':'WallShelfUnit',
            'available_in_pos':True,
            'list_price':1.98,
            'taxes_id':False,
            'barcode':'2100005000000',
        })
        small_shelf=env['product.product'].create({
            'name':'SmallShelf',
            'available_in_pos':True,
            'list_price':2.83,
            'taxes_id':False,
        })
        magnetic_board=env['product.product'].create({
            'name':'MagneticBoard',
            'available_in_pos':True,
            'list_price':1.98,
            'taxes_id':False,
            'barcode':'2305000000004',
        })
        monitor_stand=env['product.product'].create({
            'name':'MonitorStand',
            'available_in_pos':True,
            'list_price':3.19,
            'taxes_id':False,
            'barcode':'0123456789', #Nopatterninbarcodenomenclature
        })
        desk_pad=env['product.product'].create({
            'name':'DeskPad',
            'available_in_pos':True,
            'list_price':1.98,
            'taxes_id':False,
            'pos_categ_id':pos_categ_desks.id,
        })
        letter_tray=env['product.product'].create({
            'name':'LetterTray',
            'available_in_pos':True,
            'list_price':4.80,
            'taxes_id':False,
            'pos_categ_id':pos_categ_chairs.id,
        })
        desk_organizer=env['product.product'].create({
            'name':'DeskOrganizer',
            'available_in_pos':True,
            'list_price':5.10,
            'taxes_id':False,
        })
        configurable_chair=env['product.product'].create({
            'name':'ConfigurableChair',
            'available_in_pos':True,
            'list_price':10,
            'taxes_id':False,
        })

        attribute=env['product.attribute'].create({
            'name':'add2',
        })
        attribute_value=env['product.attribute.value'].create({
            'name':'add2',
            'attribute_id':attribute.id,
        })
        line=env['product.template.attribute.line'].create({
            'product_tmpl_id':pear.product_tmpl_id.id,
            'attribute_id':attribute.id,
            'value_ids':[(6,0,attribute_value.ids)]
        })
        line.product_template_value_ids[0].price_extra=2

        chair_color_attribute=env['product.attribute'].create({
            'name':'Color',
            'display_type':'color',
            'create_variant':'no_variant',
        })
        chair_color_red=env['product.attribute.value'].create({
            'name':'Red',
            'attribute_id':chair_color_attribute.id,
            'html_color':'#ff0000',
        })
        chair_color_blue=env['product.attribute.value'].create({
            'name':'Blue',
            'attribute_id':chair_color_attribute.id,
            'html_color':'#0000ff',
        })
        chair_color_line=env['product.template.attribute.line'].create({
            'product_tmpl_id':configurable_chair.product_tmpl_id.id,
            'attribute_id':chair_color_attribute.id,
            'value_ids':[(6,0,[chair_color_red.id,chair_color_blue.id])]
        })
        chair_color_line.product_template_value_ids[0].price_extra=1

        chair_legs_attribute=env['product.attribute'].create({
            'name':'ChairLegs',
            'display_type':'select',
            'create_variant':'no_variant',
        })
        chair_legs_metal=env['product.attribute.value'].create({
            'name':'Metal',
            'attribute_id':chair_legs_attribute.id,
        })
        chair_legs_wood=env['product.attribute.value'].create({
            'name':'Wood',
            'attribute_id':chair_legs_attribute.id,
        })
        chair_legs_line=env['product.template.attribute.line'].create({
            'product_tmpl_id':configurable_chair.product_tmpl_id.id,
            'attribute_id':chair_legs_attribute.id,
            'value_ids':[(6,0,[chair_legs_metal.id,chair_legs_wood.id])]
        })

        chair_fabrics_attribute=env['product.attribute'].create({
            'name':'Fabrics',
            'display_type':'radio',
            'create_variant':'no_variant',
        })
        chair_fabrics_leather=env['product.attribute.value'].create({
            'name':'Leather',
            'attribute_id':chair_fabrics_attribute.id,
        })
        chair_fabrics_other=env['product.attribute.value'].create({
            'name':'Other',
            'attribute_id':chair_fabrics_attribute.id,
            'is_custom':True,
        })
        chair_fabrics_line=env['product.template.attribute.line'].create({
            'product_tmpl_id':configurable_chair.product_tmpl_id.id,
            'attribute_id':chair_fabrics_attribute.id,
            'value_ids':[(6,0,[chair_fabrics_leather.id,chair_fabrics_other.id])]
        })
        chair_color_line.product_template_value_ids[1].is_custom=True

        fixed_pricelist=env['product.pricelist'].create({
            'name':'Fixed',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':1,
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
                'applied_on':'0_product_variant',
                'product_id':wall_shelf.id,
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':13.95, #testforissueslikein7f260ab517ebde634fc274e928eb062463f0d88f
                'applied_on':'0_product_variant',
                'product_id':small_shelf.id,
            })],
        })

        env['product.pricelist'].create({
            'name':'Percentage',
            'item_ids':[(0,0,{
                'compute_price':'percentage',
                'percent_price':100,
                'applied_on':'0_product_variant',
                'product_id':wall_shelf.id,
            }),(0,0,{
                'compute_price':'percentage',
                'percent_price':99,
                'applied_on':'0_product_variant',
                'product_id':small_shelf.id,
            }),(0,0,{
                'compute_price':'percentage',
                'percent_price':0,
                'applied_on':'0_product_variant',
                'product_id':magnetic_board.id,
            })],
        })

        env['product.pricelist'].create({
            'name':'Formula',
            'item_ids':[(0,0,{
                'compute_price':'formula',
                'price_discount':6,
                'price_surcharge':5,
                'applied_on':'0_product_variant',
                'product_id':wall_shelf.id,
            }),(0,0,{
                #.99prices
                'compute_price':'formula',
                'price_surcharge':-0.01,
                'price_round':1,
                'applied_on':'0_product_variant',
                'product_id':small_shelf.id,
            }),(0,0,{
                'compute_price':'formula',
                'price_min_margin':10,
                'price_max_margin':100,
                'applied_on':'0_product_variant',
                'product_id':magnetic_board.id,
            }),(0,0,{
                'compute_price':'formula',
                'price_surcharge':10,
                'price_max_margin':5,
                'applied_on':'0_product_variant',
                'product_id':monitor_stand.id,
            }),(0,0,{
                'compute_price':'formula',
                'price_discount':-100,
                'price_min_margin':5,
                'price_max_margin':20,
                'applied_on':'0_product_variant',
                'product_id':desk_pad.id,
            })],
        })

        env['product.pricelist'].create({
            'name':'min_quantityordering',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':1,
                'applied_on':'0_product_variant',
                'min_quantity':2,
                'product_id':wall_shelf.id,
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
                'applied_on':'0_product_variant',
                'min_quantity':1,
                'product_id':wall_shelf.id,
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
                'applied_on':'0_product_variant',
                'min_quantity':2,
                'product_id':env.ref('point_of_sale.product_product_consumable').id,
            })],
        })

        env['product.pricelist'].create({
            'name':'Producttemplate',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':1,
                'applied_on':'1_product',
                'product_tmpl_id':wall_shelf.product_tmpl_id.id,
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
            })],
        })

        product_category_3=env['product.category'].create({
            'name':'Services',
            'parent_id':env.ref('product.product_category_1').id,
        })

        env['product.pricelist'].create({
            #nocategoryhasprecedenceovercategory
            'name':'Categoryvsnocategory',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':1,
                'applied_on':'2_product_category',
                'categ_id':product_category_3.id, #All/Saleable/Services
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
            })],
        })

        p=env['product.pricelist'].create({
            'name':'Category',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
                'applied_on':'2_product_category',
                'categ_id':env.ref('product.product_category_all').id,
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':1,
                'applied_on':'2_product_category',
                'categ_id':product_category_3.id, #All/Saleable/Services
            })],
        })

        today=date.today()
        one_week_ago=today-timedelta(weeks=1)
        two_weeks_ago=today-timedelta(weeks=2)
        one_week_from_now=today+timedelta(weeks=1)
        two_weeks_from_now=today+timedelta(weeks=2)

        public_pricelist=env['product.pricelist'].create({
            'name':'PublicPricelist',
        })

        env['product.pricelist'].create({
            'name':'Dates',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':1,
                'date_start':two_weeks_ago.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_end':one_week_ago.strftime(DEFAULT_SERVER_DATE_FORMAT),
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':2,
                'date_start':today.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_end':one_week_from_now.strftime(DEFAULT_SERVER_DATE_FORMAT),
            }),(0,0,{
                'compute_price':'fixed',
                'fixed_price':3,
                'date_start':one_week_from_now.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_end':two_weeks_from_now.strftime(DEFAULT_SERVER_DATE_FORMAT),
            })],
        })

        cost_base_pricelist=env['product.pricelist'].create({
            'name':'Costbase',
            'item_ids':[(0,0,{
                'base':'standard_price',
                'compute_price':'percentage',
                'percent_price':55,
            })],
        })

        pricelist_base_pricelist=env['product.pricelist'].create({
            'name':'Pricelistbase',
            'item_ids':[(0,0,{
                'base':'pricelist',
                'base_pricelist_id':cost_base_pricelist.id,
                'compute_price':'percentage',
                'percent_price':15,
            })],
        })

        env['product.pricelist'].create({
            'name':'Pricelistbase2',
            'item_ids':[(0,0,{
                'base':'pricelist',
                'base_pricelist_id':pricelist_base_pricelist.id,
                'compute_price':'percentage',
                'percent_price':3,
            })],
        })

        env['product.pricelist'].create({
            'name':'Pricelistbaserounding',
            'item_ids':[(0,0,{
                'base':'pricelist',
                'base_pricelist_id':fixed_pricelist.id,
                'compute_price':'percentage',
                'percent_price':0.01,
            })],
        })

        excluded_pricelist=env['product.pricelist'].create({
            'name':'Notloaded'
        })
        res_partner_18=self.env['res.partner'].create({
            'name':'LumberInc',
            'is_company':True,
        })
        res_partner_18.property_product_pricelist=excluded_pricelist

        partner=self.env['res.partner'].create({
            'name':'TESTPARTNER',
            'email':'test@partner.com',
        })

        #setthecompanycurrencytoUSD,otherwiseitwillassume
        #euro's.thiswillcauseissuesasthesalesjournalisin
        #USD,becauseofthisallproductswouldhaveadifferent
        #price
        main_company.currency_id=env.ref('base.USD')

        test_sale_journal=journal_obj.create({'name':'SalesJournal-Test',
                                                'code':'TSJ',
                                                'type':'sale',
                                                'company_id':main_company.id})

        all_pricelists=env['product.pricelist'].search([('id','!=',excluded_pricelist.id)])
        all_pricelists.write(dict(currency_id=main_company.currency_id.id))

        src_tax=env['account.tax'].create({'name':"SRC",'amount':10})
        dst_tax=env['account.tax'].create({'name':"DST",'amount':5})

        letter_tray.taxes_id=[(6,0,[src_tax.id])]

        self.main_pos_config.write({
            'tax_regime_selection':True,
            'fiscal_position_ids':[(0,0,{
                                            'name':"FP-POS-2M",
                                            'tax_ids':[
                                                (0,0,{'tax_src_id':src_tax.id,
                                                      'tax_dest_id':src_tax.id}),
                                                (0,0,{'tax_src_id':src_tax.id,
                                                      'tax_dest_id':dst_tax.id})]
                                            })],
            'journal_id':test_sale_journal.id,
            'invoice_journal_id':test_sale_journal.id,
            'payment_method_ids':[(0,0,{'name':'Cash',
                                            'is_cash_count':True,
                                            'cash_journal_id':cash_journal.id,
                                            'receivable_account_id':account_receivable.id,
            })],
            'use_pricelist':True,
            'pricelist_id':public_pricelist.id,
            'available_pricelist_ids':[(4,pricelist.id)forpricelistinall_pricelists],
            'module_pos_loyalty':False,
        })

        #Changethedefaultsalepricelistofcustomers,
        #sothejstestscanexpectdeterministicallythispricelistwhenselectingacustomer.
        env['ir.property']._set_default("property_product_pricelist","res.partner",public_pricelist,main_company)


@flectra.tests.tagged('post_install','-at_install')
classTestUi(TestPointOfSaleHttpCommon):
    deftest_01_pos_basic_order(self):

        self.main_pos_config.write({
            'iface_tipproduct':True,
            'tip_product_id':self.tip.id,
        })

        #openasession,the/pos/uicontrollerwillredirecttoit
        self.main_pos_config.open_session_cb(check_coa=False)

        #neededbecausetestsarerunbeforethemoduleismarkedas
        #installed.Injswebwillonlyloadqwebcomingfrommodules
        #thatarereturnedbythebackendinmodule_boot.Without
        #thisyouendupwithjs,cssbutnoqweb.
        self.env['ir.module.module'].search([('name','=','point_of_sale')],limit=1).state='installed'

        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'pos_pricelist',login="admin")
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'pos_basic_order',login="admin")
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'ProductScreenTour',login="admin")
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'PaymentScreenTour',login="admin")
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'ReceiptScreenTour',login="admin")

        fororderinself.env['pos.order'].search([]):
            self.assertEqual(order.state,'paid',"Validatedorderhaspaymentof"+str(order.amount_paid)+"andtotalof"+str(order.amount_total))

        #checkifemailfromReceiptScreenTourisproperlysent
        email_count=self.env['mail.mail'].search_count([('email_to','=','test@receiptscreen.com')])
        self.assertEqual(email_count,1)

    deftest_02_pos_with_invoiced(self):
        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'ChromeTour',login="admin")
        n_invoiced=self.env['pos.order'].search_count([('state','=','invoiced')])
        n_paid=self.env['pos.order'].search_count([('state','=','paid')])
        self.assertEqual(n_invoiced,1,'Thereshouldbe1invoicedorder.')
        self.assertEqual(n_paid,2,'Thereshouldbe2paidorder.')

    deftest_03_order_management(self):
        self.main_pos_config.write({'manage_orders':True,'module_account':True})
        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'OrderManagementScreenTour',login="admin")

    deftest_04_product_configurator(self):
        self.main_pos_config.write({'product_configurator':True})
        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config,'ProductConfiguratorTour',login="admin")

    deftest_05_ticket_screen(self):
        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'TicketScreenTour',login="admin")

    deftest_fixed_tax_negative_qty(self):
        """Assertthenegativeamountofanegative-quantityorderline
            withzero-amountproductwithfixedtax.
        """

        #setupthezero-amountproduct
        tax_received_account=self.env['account.account'].create({
            'name':'TAX_BASE',
            'code':'TBASE',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
            'company_id':self.env.company.id,
        })
        fixed_tax=self.env['account.tax'].create({
            'name':'fixedamounttax',
            'amount_type':'fixed',
            'amount':1,
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                }),
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'account_id':tax_received_account.id,
                }),
            ],
        })
        zero_amount_product=self.env['product.product'].create({
            'name':'ZeroAmountProduct',
            'available_in_pos':True,
            'list_price':0,
            'taxes_id':[(6,0,[fixed_tax.id])],
        })

        #Makeanorderwiththezero-amountproductfromthefrontend.
        #Weneedtodothisbecauseofthefixinthe"compute_all"port.
        self.main_pos_config.write({'iface_tax_included':'total'})
        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'FixedTaxNegativeQty',login="admin")
        pos_session=self.main_pos_config.current_session_id

        #Closethesessionandcheckthesessionjournalentry.
        pos_session.action_pos_session_validate()

        lines=pos_session.move_id.line_ids.sorted('balance')

        #orderinthetourispaidusingthebankpaymentmethod.
        bank_pm=self.main_pos_config.payment_method_ids.filtered(lambdapm:pm.name=='Bank')

        self.assertEqual(lines[0].account_id,bank_pm.receivable_account_id)
        self.assertAlmostEqual(lines[0].balance,-1)
        self.assertEqual(lines[1].account_id,zero_amount_product.categ_id.property_account_income_categ_id)
        self.assertAlmostEqual(lines[1].balance,0)
        self.assertEqual(lines[2].account_id,tax_received_account)
        self.assertAlmostEqual(lines[2].balance,1)

    deftest_fiscal_position_no_tax(self):
        #createataxof15%withpriceincluded
        tax=self.env['account.tax'].create({
            'name':'Tax15%',
            'amount':15,
            'price_include':True,
            'amount_type':'percent',
            'type_tax_use':'sale',
        })

        #createaproductwiththetax
        self.product=self.env['product.product'].create({
            'name':'TestProduct',
            'taxes_id':[(6,0,[tax.id])],
            'list_price':100,
            'available_in_pos':True,
        })

        #createafiscalpositionthatmapthetaxtonotax
        fiscal_position=self.env['account.fiscal.position'].create({
            'name':'NoTax',
            'tax_ids':[(0,0,{
                'tax_src_id':tax.id,
                'tax_dest_id':False,
            })],
        })

        pricelist=self.env['product.pricelist'].create({
            'name':'TestPricelist',
            'discount_policy':'without_discount',
        })

        self.main_pos_config.write({
            'tax_regime_selection':True,
            'fiscal_position_ids':[(6,0,[fiscal_position.id])],
            'available_pricelist_ids':[(6,0,[pricelist.id])],
            'pricelist_id':pricelist.id,
        })
        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'FiscalPositionNoTax',login="admin")

    deftest_06_pos_discount_display_with_multiple_pricelist(self):
        """TestthediscountdisplayonthePOSscreenwhenmultiplepricelistsareused."""
        test_product=self.env['product.product'].create({
            'name':'TestProduct',
            'available_in_pos':True,
            'list_price':10,
        })

        base_pricelist=self.env['product.pricelist'].create({
            'name':'base_pricelist',
            'discount_policy':'without_discount',
        })

        self.env['product.pricelist.item'].create({
            'pricelist_id':base_pricelist.id,
            'product_tmpl_id':test_product.product_tmpl_id.id,
            'compute_price':'fixed',
            'applied_on':'1_product',
            'fixed_price':7,
        })

        special_pricelist=self.env['product.pricelist'].create({
            'name':'special_pricelist',
            'discount_policy':'without_discount',
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id':special_pricelist.id,
            'base':'pricelist',
            'base_pricelist_id':base_pricelist.id,
            'compute_price':'formula',
            'applied_on':'3_global',
            'price_discount':10,
        })

        self.main_pos_config.write({
            'pricelist_id':base_pricelist.id,
            'available_pricelist_ids':[(6,0,[base_pricelist.id,special_pricelist.id])],
        })

        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.main_pos_config.id,'ReceiptScreenDiscountWithPricelistTour',login="admin")

    deftest_07_pos_barcodes_scan(self):
        barcode_rule=self.env.ref("point_of_sale.barcode_rule_client")
        barcode_rule.pattern=barcode_rule.pattern+"|234"
        #shouldintheorybechangedintheJScodeto`|^234`
        #Ifnot,itwillfailasitwillmistakenlymatchwiththeproductbarcode"0123456789"

        self.main_pos_config.open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?debug=1&config_id=%d"%self.main_pos_config.id,'BarcodeScanningTour',login="admin")
