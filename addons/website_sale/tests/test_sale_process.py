#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests

fromflectraimportapi
fromflectra.addons.base.tests.commonimportHttpCaseWithUserDemo,TransactionCaseWithUserDemo,HttpCaseWithUserPortal
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.addons.website_sale.tests.commonimportTestWebsiteSaleCommon
fromflectra.addons.website.toolsimportMockRequest


@flectra.tests.tagged('post_install','-at_install')
classTestUi(HttpCaseWithUserDemo,TestWebsiteSaleCommon):

    defsetUp(self):
        super(TestUi,self).setUp()
        product_product_7=self.env['product.product'].create({
            'name':'StorageBox',
            'standard_price':70.0,
            'list_price':79.0,
            'website_published':True,
        })
        self.product_attribute_1=self.env['product.attribute'].create({
            'name':'Legs',
            'sequence':10,
        })
        product_attribute_value_1=self.env['product.attribute.value'].create({
            'name':'Steel',
            'attribute_id':self.product_attribute_1.id,
            'sequence':1,
        })
        product_attribute_value_2=self.env['product.attribute.value'].create({
            'name':'Aluminium',
            'attribute_id':self.product_attribute_1.id,
            'sequence':2,
        })
        self.product_product_11_product_template=self.env['product.template'].create({
            'name':'ConferenceChair(CONFIG)',
            'list_price':16.50,
            'accessory_product_ids':[(4,product_product_7.id)],
        })
        self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.product_product_11_product_template.id,
            'attribute_id':self.product_attribute_1.id,
            'value_ids':[(4,product_attribute_value_1.id),(4,product_attribute_value_2.id)],
        })

        self.product_product_1_product_template=self.env['product.template'].create({
            'name':'Chairfloorprotection',
            'list_price':12.0,
        })

        cash_journal=self.env['account.journal'].create({'name':'Cash-Test','type':'cash','code':'CASH-Test'})
        self.env.ref('payment.payment_acquirer_transfer').journal_id=cash_journal

        #AvoidShipping/Billingaddresspage
        (self.env.ref('base.partner_admin')+self.partner_demo).write({
            'street':'215VineSt',
            'city':'Scranton',
            'zip':'18503',
            'country_id':self.env.ref('base.us').id,
            'state_id':self.env.ref('base.state_us_39').id,
            'phone':'+1555-555-5555',
            'email':'admin@yourcompany.example.com',
        })

    deftest_01_admin_shop_tour(self):
        self.start_tour("/",'shop',login="admin")

    deftest_02_admin_checkout(self):
        self.start_tour("/",'shop_buy_product',login="admin")

    deftest_03_demo_checkout(self):
        self.start_tour("/",'shop_buy_product',login="demo")

    deftest_04_admin_website_sale_tour(self):
        tax_group=self.env['account.tax.group'].create({'name':'Tax15%'})
        tax=self.env['account.tax'].create({
            'name':'Tax15%',
            'amount':15,
            'type_tax_use':'sale',
            'tax_group_id':tax_group.id
        })
        #storagebox
        self.product_product_7=self.env['product.product'].create({
            'name':'StorageBoxTest',
            'standard_price':70.0,
            'list_price':79.0,
            'categ_id':self.env.ref('product.product_category_all').id,
            'website_published':True,
            'invoice_policy':'delivery',
        })
        self.product_product_7.taxes_id=[tax.id]
        self.env['res.config.settings'].create({
            'auth_signup_uninvited':'b2c',
            'show_line_subtotals_tax_selection':'tax_excluded',
            'group_show_line_subtotals_tax_excluded':True,
            'group_show_line_subtotals_tax_included':False,
        }).execute()

        self.start_tour("/",'website_sale_tour')


@flectra.tests.tagged('post_install','-at_install')
classTestWebsiteSaleCheckoutAddress(TransactionCaseWithUserDemo,HttpCaseWithUserPortal):
    '''Thegoalofthismethodclassistotesttheaddressmanagementon
        thecheckout(new/editbilling/shipping,company_id,website_id..).
    '''

    defsetUp(self):
        super(TestWebsiteSaleCheckoutAddress,self).setUp()
        self.website=self.env.ref('website.default_website')
        self.country_id=self.env.ref('base.be').id
        self.WebsiteSaleController=WebsiteSale()
        self.default_address_values={
            'name':'ares.partneraddress','email':'email@email.email','street':'ooo',
            'city':'ooo','zip':'1200','country_id':self.country_id,'submitted':1,
        }

    def_create_so(self,partner_id=None):
        returnself.env['sale.order'].create({
            'partner_id':partner_id,
            'website_id':self.website.id,
            'order_line':[(0,0,{
                'product_id':self.env['product.product'].create({
                    'name':'ProductA',
                    'list_price':100,
                    'website_published':True,
                    'sale_ok':True}).id,
                'name':'ProductA',
            })]
        })

    def_get_last_address(self,partner):
        '''Usefultoretrievethelastcreatedshippingaddress'''
        returnpartner.child_ids.sorted('id',reverse=True)[0]

    #TESTWEBSITE
    deftest_01_create_shipping_address_specific_user_account(self):
        '''Ensure`website_id`iscorrectlyset(specific_user_account)'''
        p=self.env.user.partner_id
        so=self._create_so(p.id)

        withMockRequest(self.env,website=self.website,sale_order_id=so.id)asreq:
            req.httprequest.method="POST"
            self.WebsiteSaleController.address(**self.default_address_values)
            self.assertFalse(self._get_last_address(p).website_id,"Newshippingaddressshouldnothaveawebsitesetonit(nospecific_user_account).")

            self.website.specific_user_account=True

            self.WebsiteSaleController.address(**self.default_address_values)
            self.assertEqual(self._get_last_address(p).website_id,self.website,"Newshippingaddressshouldhaveawebsitesetonit(specific_user_account).")

    #TESTCOMPANY
    def_setUp_multicompany_env(self):
        '''Have2companiesA&B.
            Have1website1whichcompanyisB
            HaveadminoncompanyA
        '''
        self.company_a=self.env['res.company'].create({
            'name':'CompanyA',
        })
        self.company_b=self.env['res.company'].create({
            'name':'CompanyB',
        })
        self.company_c=self.env['res.company'].create({
            'name':'CompanyC',
        })
        self.website.company_id=self.company_b
        self.env.user.company_id=self.company_a

        self.demo_user=self.user_demo
        self.demo_user.company_ids+=self.company_c
        self.demo_user.company_id=self.company_c
        self.demo_partner=self.demo_user.partner_id

        self.portal_user=self.user_portal
        self.portal_partner=self.portal_user.partner_id

    deftest_02_demo_address_and_company(self):
        '''Thistestensurethatthecompany_idoftheaddress(partner)is
            correctlysetandalso,isnotwronglychanged.
            eg:newshippingshouldusethecompanyofthewebsiteandnotthe
                onefromtheadmin,andeditingabillingshouldnotchangeits
                company.
        '''
        self._setUp_multicompany_env()
        so=self._create_so(self.demo_partner.id)

        env=api.Environment(self.env.cr,self.demo_user.id,{})
        #changealsowebsiteenvfor`sale_get_order`tonotchangeorderpartner_id
        withMockRequest(env,website=self.website.with_env(env),sale_order_id=so.id)asreq:
            req.httprequest.method="POST"

            #1.Loggedinuser,newshipping
            self.WebsiteSaleController.address(**self.default_address_values)
            new_shipping=self._get_last_address(self.demo_partner)
            self.assertTrue(new_shipping.company_id!=self.env.user.company_id,"Loggedinusernewshippingshouldnotgetthecompanyofthesudo()neithertheonefromit'spartner..")
            self.assertEqual(new_shipping.company_id,self.website.company_id,"..buttheonefromthewebsite.")

            #2.Loggedinuser/internaluser,shouldnoteditnameoremailaddressofbilling
            self.default_address_values['partner_id']=self.demo_partner.id
            self.WebsiteSaleController.address(**self.default_address_values)
            self.assertEqual(self.demo_partner.company_id,self.company_c,"Loggedinusereditedbilling(thepartneritself)shouldnotgetitscompanymodified.")
            self.assertNotEqual(self.demo_partner.name,self.default_address_values['name'],"Employeecannotchangetheirnameduringthecheckoutprocess.")
            self.assertNotEqual(self.demo_partner.email,self.default_address_values['email'],"Employeecannotchangetheiremailduringthecheckoutprocess.")

    deftest_03_public_user_address_and_company(self):
        '''Sameastest_02butwithpublicuser'''
        self._setUp_multicompany_env()
        so=self._create_so(self.website.user_id.partner_id.id)

        env=api.Environment(self.env.cr,self.website.user_id.id,{})
        #changealsowebsiteenvfor`sale_get_order`tonotchangeorderpartner_id
        withMockRequest(env,website=self.website.with_env(env),sale_order_id=so.id)asreq:
            req.httprequest.method="POST"

            #1.Publicuser,newbilling
            self.default_address_values['partner_id']=-1
            self.WebsiteSaleController.address(**self.default_address_values)
            new_partner=so.partner_id
            self.assertNotEqual(new_partner,self.website.user_id.partner_id,"NewbillingshouldhavecreatedanewpartnerandassignitontheSO")
            self.assertEqual(new_partner.company_id,self.website.company_id,"Thenewpartnershouldgetthecompanyofthewebsite")

            #2.Publicuser,editbilling
            self.default_address_values['partner_id']=new_partner.id
            self.WebsiteSaleController.address(**self.default_address_values)
            self.assertEqual(new_partner.company_id,self.website.company_id,"Publicusereditedbilling(thepartneritself)shouldnotgetitscompanymodified.")

    deftest_04_apply_empty_pl(self):
        '''Ensureemptyplcoderesettheappliedpl'''
        so=self._create_so(self.env.user.partner_id.id)
        eur_pl=self.env['product.pricelist'].create({
            'name':'EUR_test',
            'website_id':self.website.id,
            'code':'EUR_test',
        })

        withMockRequest(self.env,website=self.website,sale_order_id=so.id):
            self.WebsiteSaleController.pricelist('EUR_test')
            self.assertEqual(so.pricelist_id,eur_pl,"EnsureEUR_testisapplied")

            self.WebsiteSaleController.pricelist('')
            self.assertNotEqual(so.pricelist_id,eur_pl,"Pricelistshouldberemovedwhensendinganemptyplcode")

    deftest_05_portal_user_address_and_company(self):
        '''Sameastest_03butwithportaluser'''
        self._setUp_multicompany_env()
        so=self._create_so(self.portal_partner.id)

        env=api.Environment(self.env.cr,self.portal_user.id,{})
        #changealsowebsiteenvfor`sale_get_order`tonotchangeorderpartner_id
        withMockRequest(env,website=self.website.with_env(env),sale_order_id=so.id)asreq:
            req.httprequest.method="POST"

            #1.Portaluser,newshipping,samewiththeloginuser
            self.WebsiteSaleController.address(**self.default_address_values)
            new_shipping=self._get_last_address(self.portal_partner)
            self.assertTrue(new_shipping.company_id!=self.env.user.company_id,"Portalusernewshippingshouldnotgetthecompanyofthesudo()neithertheonefromit'spartner..")
            self.assertEqual(new_shipping.company_id,self.website.company_id,"..buttheonefromthewebsite.")

            #2.Portaluser,editbilling
            self.default_address_values['partner_id']=self.portal_partner.id
            self.WebsiteSaleController.address(**self.default_address_values)
            #Namecannotbechangedifthereareissuedinvoices
            self.assertNotEqual(self.portal_partner.name,self.default_address_values['name'],"PortalUsershouldnotbeabletochangethenameiftheyhaveinvoicesundertheirname.")

    deftest_06_payment_term_when_address_change(self):
        '''Thistestensuresthatthepaymenttermsetwhentriggering
            `onchange_partner_id`bychangingtheaddressofawebsitesale
            orderiscomputedby`sale_get_payment_term`.
        '''
        self._setUp_multicompany_env()
        product_id=self.env['product.product'].create({
            'name':'ProductA',
            'list_price':100,
            'website_published':True,
            'sale_ok':True}).id

        env=api.Environment(self.env.cr,self.portal_user.id,{})
        withMockRequest(env,website=self.website.with_env(env).with_context(website_id=self.website.id))asreq:
            req.httprequest.method="POST"

            self.WebsiteSaleController.cart_update(product_id)
            so=self.portal_user.sale_order_ids[0]
            self.assertTrue(so.payment_term_id,"Apaymenttermshouldbesetbydefaultonthesaleorder")

            self.default_address_values['partner_id']=self.portal_partner.id
            self.default_address_values['name']=self.portal_partner.name
            self.WebsiteSaleController.address(**self.default_address_values)
            self.assertTrue(so.payment_term_id,"Apaymenttermshouldstillbesetonthesaleorder")

            so.website_id=False
            self.WebsiteSaleController.address(**self.default_address_values)
            self.assertFalse(so.payment_term_id,"Thewebsitedefaultpaymenttermshouldnotbesetonasaleordernotcomingfromthewebsite")
