#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.exceptionsimportUserError,AccessError
fromflectra.testsimportForm,tagged
fromflectra.toolsimportfloat_compare

from.commonimportTestSaleCommon


@tagged('post_install','-at_install')
classTestSaleOrder(TestSaleCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        SaleOrder=cls.env['sale.order'].with_context(tracking_disable=True)

        #setupusers
        cls.crm_team0=cls.env['crm.team'].create({
            'name':'crmteam0',
            'company_id':cls.company_data['company'].id
        })
        cls.crm_team1=cls.env['crm.team'].create({
            'name':'crmteam1',
            'company_id':cls.company_data['company'].id
        })
        cls.user_in_team=cls.env['res.users'].create({
            'email':'team0user@example.com',
            'login':'team0user',
            'name':'UserinTeam0',
            'sale_team_id':cls.crm_team0.id
        })
        cls.user_not_in_team=cls.env['res.users'].create({
            'email':'noteamuser@example.com',
            'login':'noteamuser',
            'name':'UserNotInTeam',
        })

        #createagenericSaleOrderwithallclassicalproductsandemptypricelist
        cls.sale_order=SaleOrder.create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })
        cls.sol_product_order=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_order_no'].name,
            'product_id':cls.company_data['product_order_no'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_order_no'].uom_id.id,
            'price_unit':cls.company_data['product_order_no'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_serv_deliver=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_service_delivery'].name,
            'product_id':cls.company_data['product_service_delivery'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_service_delivery'].uom_id.id,
            'price_unit':cls.company_data['product_service_delivery'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_serv_order=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_service_order'].name,
            'product_id':cls.company_data['product_service_order'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_service_order'].uom_id.id,
            'price_unit':cls.company_data['product_service_order'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_product_deliver=cls.env['sale.order.line'].create({
            'name':cls.company_data['product_delivery_no'].name,
            'product_id':cls.company_data['product_delivery_no'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_delivery_no'].uom_id.id,
            'price_unit':cls.company_data['product_delivery_no'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })

    deftest_sale_order(self):
        """Testthesalesorderflow(invoicingandquantityupdates)
            -Invoicerepeatedlywhilevarryingdeliveredquantitiesandcheckthatinvoicearealwayswhatweexpect
        """
        #TODO?:validateinvoiceandregisterpayments
        self.sale_order.order_line.read(['name','price_unit','product_uom_qty','price_total'])

        self.assertEqual(self.sale_order.amount_total,1240.0,'Sale:totalamountiswrong')
        self.sale_order.order_line._compute_product_updatable()
        self.assertTrue(self.sale_order.order_line[0].product_updatable)
        #sendquotation
        email_act=self.sale_order.action_quotation_send()
        email_ctx=email_act.get('context',{})
        self.sale_order.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        self.assertTrue(self.sale_order.state=='sent','Sale:stateaftersendingiswrong')
        self.sale_order.order_line._compute_product_updatable()
        self.assertTrue(self.sale_order.order_line[0].product_updatable)

        #confirmquotation
        self.sale_order.action_confirm()
        self.assertTrue(self.sale_order.state=='sale')
        self.assertTrue(self.sale_order.invoice_status=='toinvoice')

        #createinvoice:only'invoiceonorder'productsareinvoiced
        invoice=self.sale_order._create_invoices()
        self.assertEqual(len(invoice.invoice_line_ids),2,'Sale:invoiceismissinglines')
        self.assertEqual(invoice.amount_total,740.0,'Sale:invoicetotalamountiswrong')
        self.assertTrue(self.sale_order.invoice_status=='no','Sale:SOstatusafterinvoicingshouldbe"nothingtoinvoice"')
        self.assertTrue(len(self.sale_order.invoice_ids)==1,'Sale:invoiceismissing')
        self.sale_order.order_line._compute_product_updatable()
        self.assertFalse(self.sale_order.order_line[0].product_updatable)

        #deliverlinesexcept'timeandmaterial'theninvoiceagain
        forlineinself.sale_order.order_line:
            line.qty_delivered=2ifline.product_id.expense_policy=='no'else0
        self.assertTrue(self.sale_order.invoice_status=='toinvoice','Sale:SOstatusafterdeliveryshouldbe"toinvoice"')
        invoice2=self.sale_order._create_invoices()
        self.assertEqual(len(invoice2.invoice_line_ids),2,'Sale:secondinvoiceismissinglines')
        self.assertEqual(invoice2.amount_total,500.0,'Sale:secondinvoicetotalamountiswrong')
        self.assertTrue(self.sale_order.invoice_status=='invoiced','Sale:SOstatusafterinvoicingeverythingshouldbe"invoiced"')
        self.assertTrue(len(self.sale_order.invoice_ids)==2,'Sale:invoiceismissing')

        #gooverthesoldquantity
        self.sol_serv_order.write({'qty_delivered':10})
        self.assertTrue(self.sale_order.invoice_status=='upselling','Sale:SOstatusafterincreasingdeliveredqtyhigherthanorderedqtyshouldbe"upselling"')

        #upsellandinvoice
        self.sol_serv_order.write({'product_uom_qty':10})
        #Thereisabugwith`new`and`_origin`
        #Ifyoucreateafirstnewfromarecord,thenchangeavalueontheoriginrecord,thancreateanothernew,
        #thisothernewwonthavetheupdatedvalueoftheoriginrecord,buttheonefromthepreviousnew
        #Heretheproblemliesintheuseof`new`in`move=self_ctx.new(new_vals)`,
        #andthefactthismethodiscalledmultipletimesinthesametransactiontestcase.
        #Here,weupdate`qty_delivered`ontheoriginrecord,butthe`new`recordswhichareincachewiththisorderline
        #asoriginarenotupdated,northefieldsthatdependsonit.
        self.sol_serv_order.flush()
        forfieldinself.env['sale.order.line']._fields.values():
            forres_idinlist(self.env.cache._data[field]):
                ifnotres_id:
                    self.env.cache._data[field].pop(res_id)

        invoice3=self.sale_order._create_invoices()
        self.assertEqual(len(invoice3.invoice_line_ids),1,'Sale:thirdinvoiceismissinglines')
        self.assertEqual(invoice3.amount_total,720.0,'Sale:secondinvoicetotalamountiswrong')
        self.assertTrue(self.sale_order.invoice_status=='invoiced','Sale:SOstatusafterinvoicingeverything(includingtheupsel)shouldbe"invoiced"')

    deftest_sale_order_send_to_self(self):
        #whensender(loggedinuser)isalsopresentinrecipientsofthemailcomposer,
        #usershouldreceivemail.
        sale_order=self.env['sale.order'].with_user(self.company_data['default_user_salesman']).create({
            'partner_id':self.company_data['default_user_salesman'].partner_id.id,
            'order_line':[[0,0,{
                'name': self.company_data['product_order_no'].name,
                'product_id':self.company_data['product_order_no'].id,
                'product_uom_qty':1,
                'price_unit':self.company_data['product_order_no'].list_price,
            }]]
        })
        email_ctx=sale_order.action_quotation_send().get('context',{})
        #Weneedtopreventautomaildeletion,andsowecopythetemplateandsendthemailwith
        #addedconfigurationincopiedtemplate.Itwillallowustocheckwhethermailisbeing
        #senttotoauthorornot(incaseauthorispresentin'Recipients'ofcomposer).
        mail_template=self.env['mail.template'].browse(email_ctx.get('default_template_id')).copy({'auto_delete':False})
        #sendthemailwithsameuserascustomer
        sale_order.with_context(**email_ctx).with_user(self.company_data['default_user_salesman']).message_post_with_template(mail_template.id)
        self.assertTrue(sale_order.state=='sent','Sale:stateshouldbechangedtosent')
        mail_message=sale_order.message_ids[0]
        self.assertEqual(mail_message.author_id,sale_order.partner_id,'Sale:authorshouldbesameascustomer')
        self.assertEqual(mail_message.author_id,mail_message.partner_ids,'Sale:authorshouldbeincomposerrecipientsthanksto"partner_to"fieldsetontemplate')
        self.assertEqual(mail_message.partner_ids,mail_message.sudo().mail_ids.recipient_ids,'Sale:authorshouldreceivemailduetopresenceincomposerrecipients')

    deftest_invoice_state_when_ordered_quantity_is_negative(self):
        """WhenyouinvoiceaSOlinewithaproductthatisinvoicedonorderedquantitiesandhasnegativeorderedquantity,
        thistestensuresthatthe invoicingstatusoftheSOlineis'invoiced'(andnot'upselling')."""
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[(0,0,{
                'product_id':self.company_data['product_order_no'].id,
                'product_uom_qty':-1,
            })]
        })
        sale_order.action_confirm()
        sale_order._create_invoices(final=True)
        self.assertTrue(sale_order.invoice_status=='invoiced','Sale:TheinvoicingstatusoftheSOshouldbe"invoiced"')

    deftest_sale_sequence(self):
        self.env['ir.sequence'].search([
            ('code','=','sale.order'),
        ]).write({
            'use_date_range':True,'prefix':'SO/%(range_year)s/',
        })
        sale_order=self.sale_order.copy({'date_order':'2019-01-01'})
        self.assertTrue(sale_order.name.startswith('SO/2019/'))
        sale_order=self.sale_order.copy({'date_order':'2020-01-01'})
        self.assertTrue(sale_order.name.startswith('SO/2020/'))
        #InEU/BXLtz,thisisactuallyalready01/01/2020
        sale_order=self.sale_order.with_context(tz='Europe/Brussels').copy({'date_order':'2019-12-3123:30:00'})
        self.assertTrue(sale_order.name.startswith('SO/2020/'))

    deftest_unlink_cancel(self):
        """Testdeletingandcancellingsalesordersdependingontheirstateandontheuser'srights"""
        #SOinstate'draft'canbedeleted
        so_copy=self.sale_order.copy()
        withself.assertRaises(AccessError):
            so_copy.with_user(self.company_data['default_user_employee']).unlink()
        self.assertTrue(so_copy.unlink(),'Sale:deletingaquotationshouldbepossible')

        #SOinstate'cancel'canbedeleted
        so_copy=self.sale_order.copy()
        so_copy.action_confirm()
        self.assertTrue(so_copy.state=='sale','Sale:SOshouldbeinstate"sale"')
        so_copy.action_cancel()
        self.assertTrue(so_copy.state=='cancel','Sale:SOshouldbeinstate"cancel"')
        withself.assertRaises(AccessError):
            so_copy.with_user(self.company_data['default_user_employee']).unlink()
        self.assertTrue(so_copy.unlink(),'Sale:deletingacancelledSOshouldbepossible')

        #SOinstate'sale'or'done'cannotbedeleted
        self.sale_order.action_confirm()
        self.assertTrue(self.sale_order.state=='sale','Sale:SOshouldbeinstate"sale"')
        withself.assertRaises(UserError):
            self.sale_order.unlink()

        self.sale_order.action_done()
        self.assertTrue(self.sale_order.state=='done','Sale:SOshouldbeinstate"done"')
        withself.assertRaises(UserError):
            self.sale_order.unlink()

    deftest_cost_invoicing(self):
        """Testconfirmingavendorinvoicetoreinvoicecostontheso"""
        serv_cost=self.env['product.product'].create({
            'name':"Orderedatcost",
            'standard_price':160,
            'list_price':180,
            'type':'consu',
            'invoice_policy':'order',
            'expense_policy':'cost',
            'default_code':'PROD_COST',
            'service_type':'manual',
        })
        prod_gap=self.company_data['product_service_order']
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[(0,0,{'name':prod_gap.name,'product_id':prod_gap.id,'product_uom_qty':2,'product_uom':prod_gap.uom_id.id,'price_unit':prod_gap.list_price})],
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        so.action_confirm()
        so._create_analytic_account()

        inv=self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'partner_id':self.partner_a.id,
            'invoice_date':so.date_order,
            'invoice_line_ids':[
                (0,0,{
                    'name':serv_cost.name,
                    'product_id':serv_cost.id,
                    'product_uom_id':serv_cost.uom_id.id,
                    'quantity':2,
                    'price_unit':serv_cost.standard_price,
                    'analytic_account_id':so.analytic_account_id.id,
                }),
            ],
        })
        inv.action_post()
        sol=so.order_line.filtered(lambdal:l.product_id==serv_cost)
        self.assertTrue(sol,'Sale:costinvoicingdoesnotaddlineswhenconfirmingvendorinvoice')
        self.assertEqual((sol.price_unit,sol.qty_delivered,sol.product_uom_qty,sol.qty_invoiced),(160,2,0,0),'Sale:lineiswrongafterconfirmingvendorinvoice')

    deftest_sale_with_taxes(self):
        """TestSOwithtaxesappliedonitslinesandchecksubtotalappliedonitslinesandtotalappliedontheSO"""
        #Createataxwithpriceincluded
        tax_include=self.env['account.tax'].create({
            'name':'Taxwithpriceinclude',
            'amount':10,
            'price_include':True
        })
        #Createataxwithpricenotincluded
        tax_exclude=self.env['account.tax'].create({
            'name':'Taxwithnopriceinclude',
            'amount':10,
        })

        #Applytaxesonthesaleorderlines
        self.sol_product_order.write({'tax_id':[(4,tax_include.id)]})
        self.sol_serv_deliver.write({'tax_id':[(4,tax_include.id)]})
        self.sol_serv_order.write({'tax_id':[(4,tax_exclude.id)]})
        self.sol_product_deliver.write({'tax_id':[(4,tax_exclude.id)]})

        #Triggeronchangetoresetdiscount,unitprice,subtotal,...
        forlineinself.sale_order.order_line:
            line.product_id_change()
            line._onchange_discount()

        forlineinself.sale_order.order_line:
            ifline.tax_id.price_include:
                price=line.price_unit*line.product_uom_qty-line.price_tax
            else:
                price=line.price_unit*line.product_uom_qty

            self.assertEqual(float_compare(line.price_subtotal,price,precision_digits=2),0)

        self.assertEqual(self.sale_order.amount_total,
                          self.sale_order.amount_untaxed+self.sale_order.amount_tax,
                          'Taxesshouldbeapplied')

    deftest_so_create_multicompany(self):
        """Checkthatonlytaxesoftherightcompanyareappliedonthelines."""

        #PreparingtestData
        product_shared=self.env['product.template'].create({
            'name':'sharedproduct',
            'invoice_policy':'order',
            'taxes_id':[(6,False,(self.company_data['default_tax_sale']+self.company_data_2['default_tax_sale']).ids)],
            'property_account_income_id':self.company_data['default_account_revenue'].id,
        })

        so_1=self.env['sale.order'].with_user(self.company_data['default_user_salesman']).create({
            'partner_id':self.env['res.partner'].create({'name':'Apartner'}).id,
            'company_id':self.company_data['company'].id,
        })
        so_1.write({
            'order_line':[(0,False,{'product_id':product_shared.product_variant_id.id,'order_id':so_1.id})],
        })

        self.assertEqual(so_1.order_line.tax_id,self.company_data['default_tax_sale'],
            'Onlytaxesfromtherightcompanyareputbydefault')
        so_1.action_confirm()
        #i'mnotinterestedingroups/acls,butinthemulti-companyflowonly
        #thesudoisthereforthatanddoesnotimpacttheinvoicethatgetscreated
        #thegoalhereistoinvoiceincompany1(becausetheorderisincompany1)whilebeing
        #'mainly'incompany2(throughthecontext),theinvoiceshouldbeincompany1
        inv=so_1.sudo()\
            .with_context(allowed_company_ids=(self.company_data['company']+self.company_data_2['company']).ids)\
            ._create_invoices()
        self.assertEqual(inv.company_id,self.company_data['company'],'invoicesshouldbecreatedinthecompanyoftheSO,notthemaincompanyofthecontext')

    deftest_group_invoice(self):
        """Testthatinvoicingmultiplesalesorderforthesamecustomerworks."""
        #Create3SOsforthesamepartner,oneofwhichthatusesanothercurrency
        eur_pricelist=self.env['product.pricelist'].create({'name':'EUR','currency_id':self.env.ref('base.EUR').id})
        so1=self.sale_order.with_context(mail_notrack=True).copy()
        so1.pricelist_id=eur_pricelist
        so2=so1.copy()
        usd_pricelist=self.env['product.pricelist'].create({'name':'USD','currency_id':self.env.ref('base.USD').id})
        so3=so1.copy()
        so1.pricelist_id=usd_pricelist
        orders=so1|so2|so3
        orders.action_confirm()
        #Createtheinvoicingwizardandinvoiceallofthematonce
        wiz=self.env['sale.advance.payment.inv'].with_context(active_ids=orders.ids,open_invoices=True).create({})
        res=wiz.create_invoices()
        #Checkthatexactly2invoicesaregenerated
        self.assertEqual(len(res['domain'][0][2]),2,"Groupinginvoicing3ordersforthesamepartnerwith2currenciesshouldcreateexactly2invoices")

    deftest_so_note_to_invoice(self):
        """TestthatnotesfromSOarepushedintoinvoices"""

        sol_note=self.env['sale.order.line'].create({
            'name':'Thisisanote',
            'display_type':'line_note',
            'product_id':False,
            'product_uom_qty':0,
            'product_uom':False,
            'price_unit':0,
            'order_id':self.sale_order.id,
            'tax_id':False,
        })

        #confirmquotation
        self.sale_order.action_confirm()

        #createinvoice
        invoice=self.sale_order._create_invoices()

        #checknotefromSOhasbeenpushedininvoice
        self.assertEqual(len(invoice.invoice_line_ids.filtered(lambdaline:line.display_type=='line_note')),1,'NoteSOlineshouldhavebeenpushedtotheinvoice')

    deftest_multi_currency_discount(self):
        """Verifythecurrencyusedforpricelistprice&discountcomputation."""
        products=self.env["product.product"].search([],limit=2)
        product_1=products[0]
        product_2=products[1]

        #MakesurethecompanyisinUSD
        main_company=self.env.ref('base.main_company')
        main_curr=main_company.currency_id
        current_curr=self.env.company.currency_id
        other_curr=self.currency_data['currency']
        #main_company.currency_id=other_curr#product.currency_idwhennocompany_idset
        other_company=self.env["res.company"].create({
            "name":"Test",
            "currency_id":other_curr.id
        })
        user_in_other_company=self.env["res.users"].create({
            "company_id":other_company.id,
            "company_ids":[(6,0,[other_company.id])],
            "name":"E.T",
            "login":"hohoho",
        })
        user_in_other_company.groups_id|=self.env.ref('product.group_discount_per_so_line')
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':'2010-01-01',
            'rate':2.0,
            'currency_id':main_curr.id,
            "company_id":False,
        })

        product_1.company_id=False
        product_2.company_id=False

        self.assertEqual(product_1.currency_id,main_curr)
        self.assertEqual(product_2.currency_id,main_curr)
        self.assertEqual(product_1.cost_currency_id,current_curr)
        self.assertEqual(product_2.cost_currency_id,current_curr)

        product_1_ctxt=product_1.with_user(user_in_other_company)
        product_2_ctxt=product_2.with_user(user_in_other_company)
        self.assertEqual(product_1_ctxt.currency_id,main_curr)
        self.assertEqual(product_2_ctxt.currency_id,main_curr)
        self.assertEqual(product_1_ctxt.cost_currency_id,other_curr)
        self.assertEqual(product_2_ctxt.cost_currency_id,other_curr)

        product_1.lst_price=100.0
        product_2_ctxt.standard_price=10.0#costiscompany_dependent

        pricelist=self.env["product.pricelist"].create({
            "name":"Testmulti-currency",
            "discount_policy":"without_discount",
            "currency_id":other_curr.id,
            "item_ids":[
                (0,0,{
                    "base":"list_price",
                    "product_id":product_1.id,
                    "compute_price":"percentage",
                    "percent_price":20,
                }),
                (0,0,{
                    "base":"standard_price",
                    "product_id":product_2.id,
                    "compute_price":"percentage",
                    "percent_price":10,
                })
            ]
        })

        #CreateaSOintheothercompany
        ##################################
        #product_currency=main_company.currency_idwhennocompany_idontheproduct

        #CASE1:
        #companycurrency=socurrency
        #product_1.currency!=socurrency
        #product_2.cost_currency_id=socurrency
        sales_order=product_1_ctxt.with_context(mail_notrack=True,mail_create_nolog=True).env["sale.order"].create({
            "partner_id":self.env.user.partner_id.id,
            "pricelist_id":pricelist.id,
            "order_line":[
                (0,0,{
                    "product_id":product_1.id,
                    "product_uom_qty":1.0
                }),
                (0,0,{
                    "product_id":product_2.id,
                    "product_uom_qty":1.0
                })
            ]
        })
        forlineinsales_order.order_line:
            #Createvaluesautofilldoesnotcomputediscount.
            line._onchange_discount()

        so_line_1=sales_order.order_line[0]
        so_line_2=sales_order.order_line[1]
        self.assertEqual(so_line_1.discount,20)
        self.assertEqual(so_line_1.price_unit,50.0)
        self.assertEqual(so_line_2.discount,10)
        self.assertEqual(so_line_2.price_unit,10)

        #CASE2
        #companycurrency!=socurrency
        #product_1.currency==socurrency
        #product_2.cost_currency_id!=socurrency
        pricelist.currency_id=main_curr
        sales_order=product_1_ctxt.with_context(mail_notrack=True,mail_create_nolog=True).env["sale.order"].create({
            "partner_id":self.env.user.partner_id.id,
            "pricelist_id":pricelist.id,
            "order_line":[
                #Verifydiscountisconsideredincreatehack
                (0,0,{
                    "product_id":product_1.id,
                    "product_uom_qty":1.0
                }),
                (0,0,{
                    "product_id":product_2.id,
                    "product_uom_qty":1.0
                })
            ]
        })
        forlineinsales_order.order_line:
            line._onchange_discount()

        so_line_1=sales_order.order_line[0]
        so_line_2=sales_order.order_line[1]
        self.assertEqual(so_line_1.discount,20)
        self.assertEqual(so_line_1.price_unit,100.0)
        self.assertEqual(so_line_2.discount,10)
        self.assertEqual(so_line_2.price_unit,20)

    deftest_assign_sales_team_from_partner_user(self):
        """Usetheteamfromthecustomer'ssalesperson,ifitisset"""
        partner=self.env['res.partner'].create({
            'name':'CustomerofUserInTeam',
            'user_id':self.user_in_team.id,
            'team_id':self.crm_team1.id,
        })
        sale_order=self.env['sale.order'].create({
            'partner_id':partner.id,
        })
        sale_order.onchange_partner_id()
        self.assertEqual(sale_order.team_id.id,self.crm_team0.id,'Shouldassigntoteamofsalesperson')

    deftest_assign_sales_team_from_partner_team(self):
        """Ifnoteamsetonthecustomer'ssalesperson,fallbacktothecustomer'steam"""
        partner=self.env['res.partner'].create({
            'name':'CustomerofUserNotInTeam',
            'user_id':self.user_not_in_team.id,
            'team_id':self.crm_team1.id,
        })
        sale_order=self.env['sale.order'].create({
            'partner_id':partner.id,
        })
        sale_order.onchange_partner_id()
        self.assertEqual(sale_order.team_id.id,self.crm_team1.id,'Shouldassigntoteamofpartner')

    deftest_assign_sales_team_when_changing_user(self):
        """Whenweassignasalesperson,changetheteamonthesalesordertotheirteam"""
        sale_order=self.env['sale.order'].create({
            'user_id':self.user_not_in_team.id,
            'partner_id':self.partner_a.id,
            'team_id':self.crm_team1.id
        })
        sale_order.user_id=self.user_in_team
        sale_order.onchange_user_id()
        self.assertEqual(sale_order.team_id.id,self.crm_team0.id,'Shouldassigntoteamofsalesperson')

    deftest_keep_sales_team_when_changing_user_with_no_team(self):
        """Whenweassignasalespersonthathasnoteam,donotresettheteamtodefault"""
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'team_id':self.crm_team1.id
        })
        sale_order.user_id=self.user_not_in_team
        sale_order.onchange_user_id()
        self.assertEqual(sale_order.team_id.id,self.crm_team1.id,'Shouldnotresettheteamtodefault')

    deftest_discount_and_untaxed_subtotal(self):
        """WhenaddingadiscountonaSOline,thistestensuresthattheuntaxedamounttoinvoiceis
        equaltotheuntaxedsubtotal"""
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[(0,0,{
                'product_id':self.product_a.id,
                'product_uom_qty':38,
                'price_unit':541.26,
                'discount':2.00,
            })]
        })
        sale_order.action_confirm()
        line=sale_order.order_line
        self.assertEqual(line.untaxed_amount_to_invoice,0)

        line.qty_delivered=38
        #(541.26-0.02*541.26)*38=20156.5224~=20156.52
        self.assertEqual(line.price_subtotal,20156.52)
        self.assertEqual(line.untaxed_amount_to_invoice,line.price_subtotal)

        #Samewithanincluded-in-pricetax
        sale_order=sale_order.copy()
        line=sale_order.order_line
        line.tax_id=[(0,0,{
            'name':'SuperTax',
            'amount_type':'percent',
            'amount':15.0,
            'price_include':True,
        })]
        sale_order.action_confirm()
        self.assertEqual(line.untaxed_amount_to_invoice,0)

        line.qty_delivered=38
        #(541,26/1,15)*,98*38=17527,410782609~=17527.41
        self.assertEqual(line.price_subtotal,17527.41)
        self.assertEqual(line.untaxed_amount_to_invoice,line.price_subtotal)

    deftest_discount_and_amount_undiscounted(self):
        """WhenaddingadiscountonaSOline,thistestensuresthatamountundiscountedis
        consistentwiththeusedtax"""
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[(0,0,{
                'product_id':self.product_a.id,
                'product_uom_qty':1,
                'price_unit':100.0,
                'discount':1.00,
            })]
        })
        sale_order.action_confirm()
        line=sale_order.order_line

        #testdiscountandqty1
        self.assertEqual(sale_order.amount_undiscounted,100.0)
        self.assertEqual(line.price_subtotal,99.0)

        #morequantity1->3
        sale_form=Form(sale_order)
        withsale_form.order_line.edit(0)asline_form:
            line_form.product_uom_qty=3.0
            line_form.price_unit=100.0
        sale_order=sale_form.save()

        self.assertEqual(sale_order.amount_undiscounted,300.0)
        self.assertEqual(line.price_subtotal,297.0)

        #undiscounted
        withsale_form.order_line.edit(0)asline_form:
            line_form.discount=0.0
        sale_order=sale_form.save()
        self.assertEqual(line.price_subtotal,300.0)
        self.assertEqual(sale_order.amount_undiscounted,300.0)

        #Samewithanincluded-in-pricetax
        sale_order=sale_order.copy()
        line=sale_order.order_line
        line.tax_id=[(0,0,{
            'name':'SuperTax',
            'amount_type':'percent',
            'amount':10.0,
            'price_include':True,
        })]
        line.discount=50.0
        sale_order.action_confirm()

        #300with10%incltax->272.72totaltaxexcludedwithoutdiscount
        #136.36pricetaxexcludedwithdiscountapplied
        self.assertEqual(sale_order.amount_undiscounted,272.72)
        self.assertEqual(line.price_subtotal,136.36)

    deftest_free_product_and_price_include_fixed_tax(self):
        """Checkthatfixedtaxincludearecorrectlycomputedwhiletheprice_unitis0
        """
        #pleaseensurethistestremainsconsistentwith
        #test_out_invoice_line_onchange_2_taxes_fixed_price_include_free_productinaccountmodule
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[(0,0,{
                'product_id':self.company_data['product_order_no'].id,
                'product_uom_qty':1,
                'price_unit':0.0,
            })]
        })
        sale_order.action_confirm()
        line=sale_order.order_line
        line.tax_id=[
            (0,0,{
                'name':'BEBAT0.05',
                'type_tax_use':'sale',
                'amount_type':'fixed',
                'amount':0.05,
                'price_include':True,
                'include_base_amount':True,
            }),
            (0,0,{
                'name':'Recupel0.25',
                'type_tax_use':'sale',
                'amount_type':'fixed',
                'amount':0.25,
                'price_include':True,
                'include_base_amount':True,
            }),
        ]
        sale_order.action_confirm()
        self.assertRecordValues(sale_order,[{
            'amount_untaxed':-0.30,
            'amount_tax':0.30,
            'amount_total':0.0,
        }])

    deftest_sol_name_search(self):
        #Shouldn'traise
        self.env['sale.order']._search([('order_line','ilike','acoustic')])

        name_search_data=self.env['sale.order.line'].name_search(name=self.sale_order.name)
        sol_ids_found=dict(name_search_data).keys()
        self.assertEqual(list(sol_ids_found),self.sale_order.order_line.ids)

    deftest_sale_order_analytic_tag_change(self):
        self.env.user.groups_id+=self.env.ref('analytic.group_analytic_accounting')
        self.env.user.groups_id+=self.env.ref('analytic.group_analytic_tags')

        analytic_account_super=self.env['account.analytic.account'].create({'name':'SuperAccount'})
        analytic_account_great=self.env['account.analytic.account'].create({'name':'GreatAccount'})
        analytic_tag_super=self.env['account.analytic.tag'].create({'name':'SuperTag'})
        analytic_tag_great=self.env['account.analytic.tag'].create({'name':'GreatTag'})
        super_product=self.env['product.product'].create({'name':'SuperProduct'})
        great_product=self.env['product.product'].create({'name':'GreatProduct'})
        product_no_account=self.env['product.product'].create({'name':'ProductNoAccount'})
        self.env['account.analytic.default'].create([
            {
                'analytic_id':analytic_account_super.id,
                'product_id':super_product.id,
                'analytic_tag_ids':[analytic_tag_super.id],
            },
            {
                'analytic_id':analytic_account_great.id,
                'product_id':great_product.id,
                'analytic_tag_ids':[analytic_tag_great.id],
            },
        ])
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
        })
        sol=self.env['sale.order.line'].create({
            'name':super_product.name,
            'product_id':super_product.id,
            'order_id':sale_order.id,
        })

        self.assertEqual(sol.analytic_tag_ids.id,analytic_tag_super.id,"Theanalytictagshouldbesetto'SuperTag'")
        sol.write({'product_id':great_product.id})
        self.assertEqual(sol.analytic_tag_ids.id,analytic_tag_great.id,"Theanalytictagshouldbesetto'GreatTag'")
        sol.write({'product_id':product_no_account.id})
        self.assertFalse(sol.analytic_tag_ids.id,"Theanalyticaccountshouldnotbeset")

        so_no_analytic_account=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
        })
        sol_no_analytic_account=self.env['sale.order.line'].create({
            'name':super_product.name,
            'product_id':super_product.id,
            'order_id':so_no_analytic_account.id,
            'analytic_tag_ids':False,
        })
        so_no_analytic_account.action_confirm()
        self.assertFalse(sol_no_analytic_account.analytic_tag_ids.id,"Thecomputeshouldnotoverwritewhattheuserhasset.")
