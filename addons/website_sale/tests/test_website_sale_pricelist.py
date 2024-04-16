#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromunittest.mockimportpatch

fromflectra.addons.base.tests.commonimportTransactionCaseWithUserDemo,HttpCaseWithUserPortal
fromflectra.addons.website.toolsimportMockRequest
fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase,TransactionCase
fromflectra.toolsimportDotDict

'''/!\/!\
Calling`get_pricelist_available`aftersetting`property_product_pricelist`on
apartnerwillnotworkasexpected.Thatfieldwillchangetheoutputof
`get_pricelist_available`butmodifyingitwillnotinvalidatethecache.
Thus,testsshouldnotdo:

   self.env.user.partner_id.property_product_pricelist=my_pricelist
   pls=self.get_pricelist_available()
   self.assertEqual(...)
   self.env.user.partner_id.property_product_pricelist=another_pricelist
   pls=self.get_pricelist_available()
   self.assertEqual(...)

as`_get_pl_partner_order`cachewon'tbeinvalidatebetweenthecalls,output
won'tbetheoneexpectedandtestswillactuallynottestanything.
Trytokeeponecallto`get_pricelist_available`bytestmethod.
'''


@tagged('post_install','-at_install')
classTestWebsitePriceList(TransactionCase):

    #Mockneddedbecauserequest.sessiondoesn'texistduringtest
    def_get_pricelist_available(self,show_visible=False):
        returnself.get_pl(self.args.get('show'),self.args.get('current_pl'),self.args.get('country'))

    defsetUp(self):
        super(TestWebsitePriceList,self).setUp()
        self.env.user.partner_id.country_id=False #Removecountrytoavoidpropertypricelistcomputed.
        self.website=self.env.ref('website.default_website')
        self.website.user_id=self.env.user

        (self.env['product.pricelist'].search([])-self.env.ref('product.list0')).write({'website_id':False,'active':False})
        self.benelux=self.env['res.country.group'].create({
            'name':'BeNeLux',
            'country_ids':[(6,0,(self.env.ref('base.be')+self.env.ref('base.lu')+self.env.ref('base.nl')).ids)]
        })
        self.list_benelux=self.env['product.pricelist'].create({
            'name':'Benelux',
            'selectable':True,
            'website_id':self.website.id,
            'country_group_ids':[(4,self.benelux.id)],
            'sequence':2,
        })
        item_benelux=self.env['product.pricelist.item'].create({
            'pricelist_id':self.list_benelux.id,
            'compute_price':'percentage',
            'base':'list_price',
            'percent_price':10,
            'currency_id':self.env.ref('base.EUR').id,
        })


        self.list_christmas=self.env['product.pricelist'].create({
            'name':'Christmas',
            'selectable':False,
            'website_id':self.website.id,
            'country_group_ids':[(4,self.env.ref('base.europe').id)],
            'sequence':20,
        })
        item_christmas=self.env['product.pricelist.item'].create({
            'pricelist_id':self.list_christmas.id,
            'compute_price':'formula',
            'base':'list_price',
            'price_discount':20,
        })

        list_europe=self.env['product.pricelist'].create({
            'name':'EUR',
            'selectable':True,
            'website_id':self.website.id,
            'country_group_ids':[(4,self.env.ref('base.europe').id)],
            'sequence':3,
            'currency_id':self.env.ref('base.EUR').id,
        })
        item_europe=self.env['product.pricelist.item'].create({
            'pricelist_id':list_europe.id,
            'compute_price':'formula',
            'base':'list_price',
        })
        self.env.ref('product.list0').website_id=self.website.id
        self.website.pricelist_id=self.ref('product.list0')

        ca_group=self.env['res.country.group'].create({
            'name':'Canada',
            'country_ids':[(6,0,[self.ref('base.ca')])]
        })
        self.env['product.pricelist'].create({
            'name':'Canada',
            'selectable':True,
            'website_id':self.website.id,
            'country_group_ids':[(6,0,[ca_group.id])],
            'sequence':10
        })
        self.args={
            'show':False,
            'current_pl':False,
        }
        patcher=patch('flectra.addons.website_sale.models.website.Website.get_pricelist_available',wraps=self._get_pricelist_available)
        patcher.start()
        self.addCleanup(patcher.stop)

    defget_pl(self,show,current_pl,country):
        self.website.invalidate_cache(['pricelist_ids'],[self.website.id])
        pl_ids=self.website._get_pl_partner_order(
            country,
            show,
            self.website.pricelist_id.id,
            current_pl,
            self.website.pricelist_ids
        )
        returnself.env['product.pricelist'].browse(pl_ids)

    deftest_get_pricelist_available_show(self):
        show=True
        current_pl=False

        country_list={
            False:['PublicPricelist','EUR','Benelux','Canada'],
            'BE':['EUR','Benelux'],
            'IT':['EUR'],
            'CA':['Canada'],
            'US':['PublicPricelist','EUR','Benelux','Canada']
        }
        forcountry,resultincountry_list.items():
            pls=self.get_pl(show,current_pl,country)
            self.assertEqual(len(set(pls.mapped('name'))&set(result)),len(pls),'Testfailedfor%s(%s%svs%s%s)'
                              %(country,len(pls),pls.mapped('name'),len(result),result))

    deftest_get_pricelist_available_not_show(self):
        show=False
        current_pl=False

        country_list={
            False:['PublicPricelist','EUR','Benelux','Christmas','Canada'],
            'BE':['EUR','Benelux','Christmas'],
            'IT':['EUR','Christmas'],
            'US':['PublicPricelist','EUR','Benelux','Christmas','Canada'],
            'CA':['Canada']
        }

        forcountry,resultincountry_list.items():
            pls=self.get_pl(show,current_pl,country)
            self.assertEqual(len(set(pls.mapped('name'))&set(result)),len(pls),'Testfailedfor%s(%s%svs%s%s)'
                              %(country,len(pls),pls.mapped('name'),len(result),result))

    deftest_get_pricelist_available_promocode(self):
        christmas_pl=self.list_christmas.id

        country_list={
            False:True,
            'BE':True,
            'IT':True,
            'US':True,
            'CA':False
        }

        forcountry,resultincountry_list.items():
            self.args['country']=country
            #mockpatchmethodcouldnotpassenvcontext
            available=self.website.is_pricelist_available(christmas_pl)
            ifresult:
                self.assertTrue(available,'AssertTruefailedfor%s'%country)
            else:
                self.assertFalse(available,'AssertFalsefailedfor%s'%country)

    deftest_get_pricelist_available_show_with_auto_property(self):
        show=True
        self.env.user.partner_id.country_id=self.env.ref('base.be') #AddEURpricelistauto
        current_pl=False

        country_list={
            False:['PublicPricelist','EUR','Benelux','Canada'],
            'BE':['EUR','Benelux'],
            'IT':['EUR'],
            'CA':['EUR','Canada'],
            'US':['PublicPricelist','EUR','Benelux','Canada']
        }
        forcountry,resultincountry_list.items():
            pls=self.get_pl(show,current_pl,country)
            self.assertEqual(len(set(pls.mapped('name'))&set(result)),len(pls),'Testfailedfor%s(%s%svs%s%s)'
                              %(country,len(pls),pls.mapped('name'),len(result),result))

    deftest_pricelist_combination(self):
        product=self.env['product.product'].create({
            'name':'SuperProduct',
            'list_price':100,
            'taxes_id':False,
        })
        current_website=self.env['website'].get_current_website()
        website_pricelist=current_website.get_current_pricelist()
        website_pricelist.write({
            'discount_policy':'with_discount',
            'item_ids':[(5,0,0),(0,0,{
                'applied_on':'1_product',
                'product_tmpl_id':product.product_tmpl_id.id,
                'min_quantity':500,
                'compute_price':'percentage',
                'percent_price':63,
            })]
        })
        promo_pricelist=self.env['product.pricelist'].create({
            'name':'SuperPricelist',
            'discount_policy':'without_discount',
            'item_ids':[(0,0,{
                'applied_on':'1_product',
                'product_tmpl_id':product.product_tmpl_id.id,
                'base':'pricelist',
                'base_pricelist_id':website_pricelist.id,
                'compute_price':'formula',
                'price_discount':25
            })]
        })
        so=self.env['sale.order'].create({
            'partner_id':self.env.user.partner_id.id,
            'order_line':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':1,
                'product_uom':product.uom_id.id,
                'price_unit':product.list_price,
                'tax_id':False,
            })]
        })
        sol=so.order_line
        self.assertEqual(sol.price_total,100.0)
        so.pricelist_id=promo_pricelist
        withMockRequest(self.env,website=current_website,sale_order_id=so.id):
            so._cart_update(product_id=product.id,line_id=sol.id,set_qty=500)
        self.assertEqual(sol.price_unit,37.0,'Bothreductionsshouldbeapplied')
        self.assertEqual(sol.price_reduce,27.75,'Bothreductionsshouldbeapplied')
        self.assertEqual(sol.price_total,13875)

    deftest_pricelist_with_no_list_price(self):
        product=self.env['product.product'].create({
            'name':'SuperProduct',
            'list_price':0,
            'taxes_id':False,
        })
        current_website=self.env['website'].get_current_website()
        website_pricelist=current_website.get_current_pricelist()
        website_pricelist.write({
            'discount_policy':'without_discount',
            'item_ids':[(5,0,0),(0,0,{
                'applied_on':'1_product',
                'product_tmpl_id':product.product_tmpl_id.id,
                'min_quantity':0,
                'compute_price':'fixed',
                'fixed_price':10,
            })]
        })
        so=self.env['sale.order'].create({
            'partner_id':self.env.user.partner_id.id,
            'order_line':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':5,
                'product_uom':product.uom_id.id,
                'price_unit':product.list_price,
                'tax_id':False,
            })]
        })
        sol=so.order_line
        self.assertEqual(sol.price_total,0)
        so.pricelist_id=website_pricelist
        withMockRequest(self.env,website=current_website,sale_order_id=so.id):
            so._cart_update(product_id=product.id,line_id=sol.id,set_qty=5)
        self.assertEqual(sol.price_unit,10.0,'Pricelistpriceshouldbeapplied')
        self.assertEqual(sol.price_reduce,10.0,'Pricelistpriceshouldbeapplied')
        self.assertEqual(sol.price_total,50.0)


defsimulate_frontend_context(self,website_id=1):
    #Mockthismethodwillbeenoughtosimulatefrontendcontextinmostmethods
    defget_request_website():
        returnself.env['website'].browse(website_id)
    patcher=patch('flectra.addons.website.models.ir_http.get_request_website',wraps=get_request_website)
    patcher.start()
    self.addCleanup(patcher.stop)


@tagged('post_install','-at_install')
classTestWebsitePriceListAvailable(TransactionCase):
    #Thisisenoughtoavoidamock(request.session/websitedonotexistduringtest)
    defget_pricelist_available(self,show_visible=False,website_id=1,country_code=None,website_sale_current_pl=None):
        request=DotDict({
            'website':self.env['website'].browse(website_id),
            'session':{
                'geoip':{
                    'country_code':country_code,
                },
                'website_sale_current_pl':website_sale_current_pl,
            },
        })
        returnself.env['website']._get_pricelist_available(request,show_visible)

    defsetUp(self):
        super(TestWebsitePriceListAvailable,self).setUp()
        Pricelist=self.env['product.pricelist']
        Website=self.env['website']

        #Setup2websites
        self.website=Website.browse(1)
        self.website2=Website.create({'name':'Website2'})

        #Removeexistingpricelistsandcreatenewones
        existing_pricelists=Pricelist.search([])
        self.backend_pl=Pricelist.create({
            'name':'BackendPricelist',
            'website_id':False,
        })
        self.generic_pl_select=Pricelist.create({
            'name':'GenericSelectablePricelist',
            'selectable':True,
            'website_id':False,
        })
        self.generic_pl_code=Pricelist.create({
            'name':'GenericCodePricelist',
            'code':'GENERICCODE',
            'website_id':False,
        })
        self.generic_pl_code_select=Pricelist.create({
            'name':'GenericCodeSelectablePricelist',
            'code':'GENERICCODESELECT',
            'selectable':True,
            'website_id':False,
        })
        self.w1_pl=Pricelist.create({
            'name':'Website1Pricelist',
            'website_id':self.website.id,
        })
        self.w1_pl_select=Pricelist.create({
            'name':'Website1PricelistSelectable',
            'website_id':self.website.id,
            'selectable':True,
        })
        self.w1_pl_code_select=Pricelist.create({
            'name':'Website1PricelistCodeSelectable',
            'website_id':self.website.id,
            'code':'W1CODESELECT',
            'selectable':True,
        })
        self.w1_pl_code=Pricelist.create({
            'name':'Website1PricelistCode',
            'website_id':self.website.id,
            'code':'W1CODE',
        })
        self.w2_pl=Pricelist.create({
            'name':'Website2Pricelist',
            'website_id':self.website2.id,
        })
        existing_pricelists.write({'active':False})

        simulate_frontend_context(self)

    deftest_get_pricelist_available(self):
        #all_pl=self.backend_pl+self.generic_pl_select+self.generic_pl_code+self.generic_pl_code_select+self.w1_pl+self.w1_pl_select+self.w1_pl_code+self.w1_pl_code_select+self.w2_pl

        #Testgetallavailablepricelists
        pls_to_return=self.generic_pl_select+self.generic_pl_code+self.generic_pl_code_select+self.w1_pl+self.w1_pl_select+self.w1_pl_code+self.w1_pl_code_select
        pls=self.get_pricelist_available()
        self.assertEqual(pls,pls_to_return,"Everypricelisthavingthecorrectwebsite_idsetor(nowebsite_idbutacodeorselectable)shouldbereturned")

        #Testgetallavailableandvisiblepricelists
        pls_to_return=self.generic_pl_select+self.generic_pl_code_select+self.w1_pl_select+self.w1_pl_code_select
        pls=self.get_pricelist_available(show_visible=True)
        self.assertEqual(pls,pls_to_return,"Onlyselectablepricelistswebsitecompliant(website_idFalseorcurrentwebsite)shouldbereturned")

    deftest_property_product_pricelist_for_inactive_partner(self):
        #`_get_partner_pricelist_multi`shouldconsiderinactiveuserswhensearchingforpricelists.
        #Realcaseifforpublicuser.His`property_product_pricelist`needtobesetasitispassed
        #through`_get_pl_partner_order`asthe`website_pl`whensearchingforavailablepricelists
        #foractiveusers.
        public_partner=self.env.ref('base.public_partner')
        self.assertFalse(public_partner.active,"Ensurepublicpartnerisinactive(purposeofthistest)")
        pl=public_partner.property_product_pricelist
        self.assertEqual(len(pl),1,"Inactivepartnershouldstillgeta`property_product_pricelist`")


@tagged('post_install','-at_install')
classTestWebsitePriceListAvailableGeoIP(TestWebsitePriceListAvailable):
    defsetUp(self):
        super(TestWebsitePriceListAvailableGeoIP,self).setUp()
        #clean`property_product_pricelist`forpartnerforthistest(cleansetup)
        self.env['ir.property'].search([('res_id','=','res.partner,%s'%self.env.user.partner_id.id)]).unlink()

        #setdifferentcountrygroupsonpricelists
        c_EUR=self.env.ref('base.europe')
        c_BENELUX=self.env['res.country.group'].create({
            'name':'BeNeLux',
            'country_ids':[(6,0,(self.env.ref('base.be')+self.env.ref('base.lu')+self.env.ref('base.nl')).ids)]
        })

        self.BE=self.env.ref('base.be')
        NL=self.env.ref('base.nl')
        c_BE=self.env['res.country.group'].create({'name':'Belgium','country_ids':[(6,0,[self.BE.id])]})
        c_NL=self.env['res.country.group'].create({'name':'Netherlands','country_ids':[(6,0,[NL.id])]})

        (self.backend_pl+self.generic_pl_select+self.generic_pl_code+self.w1_pl_select).write({'country_group_ids':[(6,0,[c_BE.id])]})
        (self.generic_pl_code_select+self.w1_pl+self.w2_pl).write({'country_group_ids':[(6,0,[c_BENELUX.id])]})
        (self.w1_pl_code).write({'country_group_ids':[(6,0,[c_EUR.id])]})
        (self.w1_pl_code_select).write({'country_group_ids':[(6,0,[c_NL.id])]})

        #       pricelist       |selectable|website|code|countrygroup|
        #----------------------------------------------------------------------|
        #backend_pl             |           |        |     |           BE|
        #generic_pl_select      |     V    |        |     |           BE|
        #generic_pl_code        |           |        |  V |           BE|
        #generic_pl_code_select |     V    |        |  V |      BENELUX|
        #w1_pl                  |           |   1   |     |      BENELUX|
        #w1_pl_select           |     V    |   1   |     |           BE|
        #w1_pl_code_select      |     V    |   1   |  V |           NL|
        #w1_pl_code             |           |   1   |  V |          EUR|
        #w2_pl                  |           |   2   |     |      BENELUX|

        #availableplforwebsite1forGeoIPBE(anythingexceptwebsite2,backendandNL)
        self.website1_be_pl=self.generic_pl_select+self.generic_pl_code+self.w1_pl_select+self.generic_pl_code_select+self.w1_pl+self.w1_pl_code

    deftest_get_pricelist_available_geoip(self):
        #Testgetallavailablepricelistswithgeoipandnopartnerpricelist(ir.property)

        #property_product_pricelistwillalsobereturnedintheavailablepricelists
        self.website1_be_pl+=self.env.user.partner_id.property_product_pricelist

        pls=self.get_pricelist_available(country_code=self.BE.code)
        self.assertEqual(pls,self.website1_be_pl,"OnlypricelistsforBEandaccessibleonwebsiteshouldbereturned,andthepartnerpl")

    deftest_get_pricelist_available_geoip2(self):
        #Testgetallavailablepricelistswithgeoipandapartnerpricelist(ir.property)notwebsitecompliant
        self.env.user.partner_id.property_product_pricelist=self.backend_pl
        pls=self.get_pricelist_available(country_code=self.BE.code)
        self.assertEqual(pls,self.website1_be_pl,"OnlypricelistsforBEandaccessibleonwebsiteshouldbereturnedaspartnerplisnotwebsitecompliant")

    deftest_get_pricelist_available_geoip3(self):
        #Testgetallavailablepricelistswithgeoipandapartnerpricelist(ir.property)websitecompliant(butnotgeoipcompliant)
        self.env.user.partner_id.property_product_pricelist=self.w1_pl_code_select
        pls=self.get_pricelist_available(country_code=self.BE.code)
        self.assertEqual(pls,self.website1_be_pl,"OnlypricelistsforBEandaccessibleonwebsiteshouldbereturned,butnotthepartnerpricelistasitiswebsitecompliantbutnotGeoIPcompliant.")

    deftest_get_pricelist_available_geoip4(self):
        #Testgetallavailablewithgeoipandvisiblepricelists+promopl
        pls_to_return=self.generic_pl_select+self.w1_pl_select+self.generic_pl_code_select
        #property_product_pricelistwillalsobereturnedintheavailablepricelists
        pls_to_return+=self.env.user.partner_id.property_product_pricelist

        current_pl=self.w1_pl_code
        pls=self.get_pricelist_available(country_code=self.BE.code,show_visible=True,website_sale_current_pl=current_pl.id)
        self.assertEqual(pls,pls_to_return+current_pl,"OnlypricelistsforBE,accessibleenwebsiteandselectableshouldbereturned.Itshouldalsoreturntheappliedpromopl")


@tagged('post_install','-at_install')
classTestWebsitePriceListHttp(HttpCaseWithUserPortal):
    deftest_get_pricelist_available_multi_company(self):
        '''Testthatthe`property_product_pricelist`of`res.partner`isnot
            computedasSUPERUSER_ID.
            Indeed,`property_product_pricelist`isa_computethatendsup
            doingasearchon`product.pricelist`thatwoulebypassthe
            pricelistmulti-company`ir.rule`.Thenitwouldreturnpricelists
            fromanothercompanyandthecodewouldraiseanaccesserrorwhen
            readingthat`property_product_pricelist`.
        '''
        test_company=self.env['res.company'].create({'name':'TestCompany'})
        test_company.flush()
        self.env['product.pricelist'].create({
            'name':'BackendPricelistFor"TestCompany"',
            'website_id':False,
            'company_id':test_company.id,
            'sequence':1,
        })

        self.authenticate('portal','portal')
        r=self.url_open('/shop')
        self.assertEqual(r.status_code,200,"Thepageshouldnotraiseanaccesserrorbecauseofreadingpricelistsfromothercompanies")


@tagged('post_install','-at_install')
classTestWebsitePriceListMultiCompany(TransactionCaseWithUserDemo):
    defsetUp(self):
        '''Createabasicmulti-companypricelistenvironment:
        -Setup2companieswiththeirowncompany-restrictedpricelisteach.
        -Adddemouserinthose2companies
        -Foreachcompany,addthatcompanypricelisttothedemouserpartner.
        -Setwebsite'scompanytocompany2
        -Demouserwillstillbeincompany1
        '''
        super(TestWebsitePriceListMultiCompany,self).setUp()

        self.demo_user=self.user_demo

        #Createandadddemouserto2companies
        self.company1=self.demo_user.company_id
        self.company2=self.env['res.company'].create({'name':'TestCompany'})
        self.demo_user.company_ids+=self.company2
        #Setcompany2ascurrentcompanyfordemouser
        Website=self.env['website']
        self.website=self.env.ref('website.default_website')
        self.website.company_id=self.company2
        #Deleteunusedwebsite,itwillmakePLmanipulationeasier,avoiding
        #UserErrorbeingthrownwhenawebsitewouldn'thaveanyPLleft.
        Website.search([('id','!=',self.website.id)]).unlink()
        self.website2=Website.create({
            'name':'Website2',
            'company_id':self.company1.id,
        })

        #Createacompanypricelistforeachcompanyandsetittodemouser
        self.c1_pl=self.env['product.pricelist'].create({
            'name':'Company1Pricelist',
            'company_id':self.company1.id,
            #The`website_id`fieldwilldefaulttothecompany'swebsite,
            #inthiscase`self.website2`.

        })
        self.c2_pl=self.env['product.pricelist'].create({
            'name':'Company2Pricelist',
            'company_id':self.company2.id,
            'website_id':False,
        })
        self.demo_user.partner_id.with_company(self.company1.id).property_product_pricelist=self.c1_pl
        self.demo_user.partner_id.with_company(self.company2.id).property_product_pricelist=self.c2_pl

        #Ensureeverythingwasdonecorrectly
        self.assertEqual(self.demo_user.partner_id.with_company(self.company1.id).property_product_pricelist,self.c1_pl)
        self.assertEqual(self.demo_user.partner_id.with_company(self.company2.id).property_product_pricelist,self.c2_pl)
        irp1=self.env['ir.property'].with_company(self.company1)._get("property_product_pricelist","res.partner",self.demo_user.partner_id.id)
        irp2=self.env['ir.property'].with_company(self.company2)._get("property_product_pricelist","res.partner",self.demo_user.partner_id.id)
        self.assertEqual((irp1,irp2),(self.c1_pl,self.c2_pl),"Ensurethereisan`ir.property`fordemopartnerforeverycompany,andthatthepricelististhecompanyspecificone.")
        #----------------------------------IR.PROPERTY-------------------------------------
        #id|           name             |    res_id   |company_id|  value_reference
        #------------------------------------------------------------------------------------
        #1 |'property_product_pricelist'|              |     1    |product.pricelist,1
        #2 |'property_product_pricelist'|              |     2    |product.pricelist,2
        #3 |'property_product_pricelist'|res.partner,8|     1    |product.pricelist,10
        #4 |'property_product_pricelist'|res.partner,8|     2    |product.pricelist,11

    deftest_property_product_pricelist_multi_company(self):
        '''Testthatthe`property_product_pricelist`of`res.partner`isread
            forthecompanyofthewebsiteandnotthecurrentusercompany.
            Thisisthecaseiftheuservisitawebsiteforwhichthecompany
            isnotthesameasitsuser'scompany.

            Here,asdemouser(company1),wewillvisitwebsite1(company2).
            Itshouldreturntheir.propertyfordemouserforcompany2andnot
            forthecompany1asweshouldgetthewebsite'scompanypricelist
            andnotthedemouser'scurrentcompanypricelist.
        '''
        simulate_frontend_context(self,self.website.id)

        #Firstcheck:Itshouldreturnir.property,4ascompany_idis
        #website.company_idandnotenv.user.company_id
        company_id=self.website.company_id.id
        partner=self.demo_user.partner_id.with_company(company_id)
        demo_pl=partner.property_product_pricelist
        self.assertEqual(demo_pl,self.c2_pl)

        #Secondthingtocheck:Itshouldnoterrorinreadrightaccesserror
        #Indeed,their.ruleforpricelistsrightsaboutcompanyshouldallowto
        #alsoreadapricelistfromanothercompanyifthatcompanyistheone
        #fromthecurrentlyvisitedwebsite.
        self.env(user=self.user_demo)['product.pricelist'].browse(demo_pl.id).name

    deftest_archive_pricelist_1(self):
        '''Testthatwhenapricelistisarchived,thecheckthatverifythat
            allwebsitehaveatleastonepricelisthaveaccesstoall
            pricelists(consideringallcompanies).
        '''

        self.c2_pl.website_id=self.website
        c2_pl2=self.c2_pl.copy({'name':'Copyofc2_pl'})
        self.env['product.pricelist'].search([
            ('id','notin',(self.c2_pl+self.c1_pl+c2_pl2).ids)
        ]).write({'active':False})

        #----------------PRICELISTS----------------
        #   name   |  website_id | company_id  |
        #--------------------------------------------
        #self.c1_pl|self.website2|self.company1|
        #self.c2_pl|self.website |self.company2|
        #c2_pl2    |self.website |self.company2|

        self.demo_user.groups_id+=self.env.ref('sales_team.group_sale_manager')

        #Thetestishere:whilehavingaccessonlytoself.company2records,
        #archiveshouldnotraiseanerror
        self.c2_pl.with_user(self.demo_user).with_context(allowed_company_ids=self.company2.ids).write({'active':False})
