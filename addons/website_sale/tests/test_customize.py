#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromflectra.addons.base.tests.commonimportHttpCaseWithUserDemo,HttpCaseWithUserPortal
fromflectra.modules.moduleimportget_module_resource
fromflectra.testsimporttagged

@tagged('post_install','-at_install')
classTestUi(HttpCaseWithUserDemo,HttpCaseWithUserPortal):

    defsetUp(self):
        super(TestUi,self).setUp()
        #createatemplate
        product_template=self.env['product.template'].create({
            'name':'TestProduct',
            'is_published':True,
            'list_price':750,
        })

        tax=self.env['account.tax'].create({'name':"Testtax",'amount':10})
        product_template.taxes_id=tax

        product_attribute=self.env['product.attribute'].create({
            'name':'Legs',
            'sequence':10,
        })
        product_attribute_value_1=self.env['product.attribute.value'].create({
            'name':'Steel-Test',
            'attribute_id':product_attribute.id,
            'sequence':1,
        })
        product_attribute_value_2=self.env['product.attribute.value'].create({
            'name':'Aluminium',
            'attribute_id':product_attribute.id,
            'sequence':2,
        })

        #setattributeandattributevaluesonthetemplate
        self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute.id,
            'product_tmpl_id':product_template.id,
            'value_ids':[(6,0,[product_attribute_value_1.id,product_attribute_value_2.id])]
        }])

        #setadifferentpriceonthevariantstodifferentiatethem
        product_template_attribute_values=self.env['product.template.attribute.value']\
            .search([('product_tmpl_id','=',product_template.id)])

        forptavinproduct_template_attribute_values:
            ifptav.name=="Steel-Test":
                ptav.price_extra=0
            else:
                ptav.price_extra=50.4

        #Updatethepricelistcurrencyregardingenv.company_idcurrency_idincasecompanyhaschangedcurrencywithCOAinstallation.
        website=self.env['website'].get_current_website()
        pricelist=website.get_current_pricelist()
        pricelist.write({'currency_id':self.env.company.currency_id.id})

    deftest_01_admin_shop_customize_tour(self):
        #EnableVariantGroup
        self.env.ref('product.group_product_variant').write({'users':[(4,self.env.ref('base.user_admin').id)]})
        self.start_tour("/",'shop_customize',login="admin")

    deftest_02_admin_shop_custom_attribute_value_tour(self):
        #Makesurepricelistruleexist
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
        product_attribute_2=self.env['product.attribute'].create({
            'name':'Color',
            'sequence':20,
        })
        product_attribute_value_3=self.env['product.attribute.value'].create({
            'name':'White',
            'attribute_id':product_attribute_2.id,
            'sequence':1,
        })
        product_attribute_value_4=self.env['product.attribute.value'].create({
            'name':'Black',
            'attribute_id':product_attribute_2.id,
            'sequence':2,
        })

        #Createproducttemplate
        self.product_product_4_product_template=self.env['product.template'].create({
            'name':'CustomizableDesk(TEST)',
            'standard_price':500.0,
            'list_price':750.0,
        })

        #Generatevariants
        self.env['product.template.attribute.line'].create([{
            'product_tmpl_id':self.product_product_4_product_template.id,
            'attribute_id':self.product_attribute_1.id,
            'value_ids':[(4,product_attribute_value_1.id),(4,product_attribute_value_2.id)],
        },{
            'product_tmpl_id':self.product_product_4_product_template.id,
            'attribute_id':product_attribute_2.id,
            'value_ids':[(4,product_attribute_value_3.id),(4,product_attribute_value_4.id)],

        }])
        product_template=self.product_product_4_product_template

        #AddCustomAttribute
        product_attribute_value_7=self.env['product.attribute.value'].create({
            'name':'CustomTEST',
            'attribute_id':self.product_attribute_1.id,
            'sequence':3,
            'is_custom':True
        })
        self.product_product_4_product_template.attribute_line_ids[0].write({'value_ids':[(4,product_attribute_value_7.id)]})

        img_path=get_module_resource('product','static','img','product_product_11-image.png')
        img_content=base64.b64encode(open(img_path,"rb").read())
        self.product_product_11_product_template=self.env['product.template'].create({
            'name':'ConferenceChair(TEST)',
            'website_sequence':9999,#laule
            'image_1920':img_content,
            'list_price':16.50,
        })

        self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.product_product_11_product_template.id,
            'attribute_id':self.product_attribute_1.id,
            'value_ids':[(4,product_attribute_value_1.id),(4,product_attribute_value_2.id)],
        })
        self.product_product_11_product_template.attribute_line_ids[0].product_template_value_ids[1].price_extra=6.40

        #Setupasecondoptionalproduct
        self.product_product_1_product_template=self.env['product.template'].create({
            'name':'Chairfloorprotection',
            'list_price':12.0,
        })

        #fixrunbot,sometimesonepricelistischosen,sometimestheother...
        pricelists=self.env['website'].get_current_website().get_current_pricelist()|self.env.ref('product.list0')

        forpricelistinpricelists:
            ifnotpricelist.item_ids.filtered(lambdai:i.product_tmpl_id==product_templateandi.price_discount==20):
                self.env['product.pricelist.item'].create({
                    'base':'list_price',
                    'applied_on':'1_product',
                    'pricelist_id':pricelist.id,
                    'product_tmpl_id':product_template.id,
                    'price_discount':20,
                    'min_quantity':2,
                    'compute_price':'formula',
                })

            pricelist.discount_policy='without_discount'

        self.start_tour("/",'shop_custom_attribute_value',login="admin")

    deftest_03_public_tour_shop_dynamic_variants(self):
        """Thegoalofthistestistomakesureproductvariantswithdynamic
        attributescanbecreatedbythepublicuser(whenbeingaddedtocart).
        """

        #createtheattribute
        product_attribute=self.env['product.attribute'].create({
            'name':"DynamicAttribute",
            'create_variant':'dynamic',
        })

        #createtheattributevalues
        product_attribute_values=self.env['product.attribute.value'].create([{
            'name':"DynamicValue1",
            'attribute_id':product_attribute.id,
            'sequence':1,
        },{
            'name':"DynamicValue2",
            'attribute_id':product_attribute.id,
            'sequence':2,
        }])

        #createthetemplate
        product_template=self.env['product.template'].create({
            'name':'DynamicProduct',
            'website_published':True,
            'list_price':0,
        })

        #setattributeandattributevaluesonthetemplate
        self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute.id,
            'product_tmpl_id':product_template.id,
            'value_ids':[(6,0,product_attribute_values.ids)]
        }])

        #setadifferentpriceonthevariantstodifferentiatethem
        product_template_attribute_values=self.env['product.template.attribute.value']\
            .search([('product_tmpl_id','=',product_template.id)])

        forptavinproduct_template_attribute_values:
            ifptav.name=="DynamicValue1":
                ptav.price_extra=10
            else:
                #0tonotbotherwiththepricelistofthepublicuser
                ptav.price_extra=0

        self.start_tour("/",'tour_shop_dynamic_variants')

    deftest_04_portal_tour_deleted_archived_variants(self):
        """Thegoalofthistestistomakesuredeletedandarchivedvariants
        areshownasimpossiblecombinations.

        Using"portal"tohavevarioususersinthetests.
        """

        #createtheattribute
        product_attribute=self.env['product.attribute'].create({
            'name':"MyAttribute",
            'create_variant':'always',
        })

        #createtheattributevalues
        product_attribute_values=self.env['product.attribute.value'].create([{
            'name':"MyValue1",
            'attribute_id':product_attribute.id,
            'sequence':1,
        },{
            'name':"MyValue2",
            'attribute_id':product_attribute.id,
            'sequence':2,
        },{
            'name':"MyValue3",
            'attribute_id':product_attribute.id,
            'sequence':3,
        }])

        #createthetemplate
        product_template=self.env['product.template'].create({
            'name':'TestProduct2',
            'is_published':True,
        })

        #setattributeandattributevaluesonthetemplate
        self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute.id,
            'product_tmpl_id':product_template.id,
            'value_ids':[(6,0,product_attribute_values.ids)]
        }])

        #setadifferentpriceonthevariantstodifferentiatethem
        product_template_attribute_values=self.env['product.template.attribute.value']\
            .search([('product_tmpl_id','=',product_template.id)])

        product_template_attribute_values[0].price_extra=10
        product_template_attribute_values[1].price_extra=20
        product_template_attribute_values[2].price_extra=30

        #archivefirstcombination(firstvariant)
        product_template.product_variant_ids[0].active=False
        #deletesecondcombination(whichisnowfirstvariantsincecachehasbeencleared)
        product_template.product_variant_ids[0].unlink()

        self.start_tour("/",'tour_shop_deleted_archived_variants',login="portal")

    deftest_05_demo_tour_no_variant_attribute(self):
        """Thegoalofthistestistomakesureattributesno_variantare
        correctlyaddedtocart.

        Using"demo"tohavevarioususersinthetests.
        """

        #createtheattribute
        product_attribute_no_variant=self.env['product.attribute'].create({
            'name':"NoVariantAttribute",
            'create_variant':'no_variant',
        })

        #createtheattributevalue
        product_attribute_value_no_variant=self.env['product.attribute.value'].create({
            'name':"NoVariantValue",
            'attribute_id':product_attribute_no_variant.id,
        })

        #createthetemplate
        product_template=self.env['product.template'].create({
            'name':'TestProduct3',
            'website_published':True,
        })

        #setattributeandattributevalueonthetemplate
        ptal=self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute_no_variant.id,
            'product_tmpl_id':product_template.id,
            'value_ids':[(6,0,product_attribute_value_no_variant.ids)]
        }])

        #setapriceonthevalue
        ptal.product_template_value_ids.price_extra=10

        self.start_tour("/",'tour_shop_no_variant_attribute',login="demo")

    deftest_06_admin_list_view_b2c(self):
        self.env.ref('product.group_product_variant').write({'users':[(4,self.env.ref('base.user_admin').id)]})

        #activateb2c
        config=self.env['res.config.settings'].create({})
        config.show_line_subtotals_tax_selection="tax_included"
        config._onchange_sale_tax()
        config.execute()

        self.start_tour("/",'shop_list_view_b2c',login="admin")
