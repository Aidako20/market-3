#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests
from.commonimportTestProductConfiguratorCommon


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpSavepointCase,TestProductConfiguratorCommon):

    defsetUp(self):
        super(TestUi,self).setUp()
        self.custom_pricelist=self.env['product.pricelist'].create({
            'name':'Custompricelist(TEST)',
            'item_ids':[(0,0,{
                'base':'list_price',
                'applied_on':'1_product',
                'product_tmpl_id':self.product_product_custo_desk.id,
                'price_discount':20,
                'min_quantity':2,
                'compute_price':'formula'
            })]
        })

    deftest_01_product_configurator(self):
        #Tobeabletotesttheproductconfigurator,adminusermusthaveaccessto"variants"feature,sowegivehimtherightgroupforthat
        self.env.ref('base.user_admin').write({'groups_id':[(4,self.env.ref('product.group_product_variant').id)]})
        self.start_tour("/web",'sale_product_configurator_tour',login="admin")

    deftest_02_product_configurator_advanced(self):
        #group_product_variant:usetheproductconfigurator
        #group_sale_pricelist:displaythepricelisttodeterminewhenitischangedafterchoosing
        #group_delivery_invoice_address:showtheshippingaddress(neededforatrigger)
        #                      thepartner
        self.env.ref('base.user_admin').write({
            'groups_id':[
                (4,self.env.ref('product.group_product_variant').id),
                (4,self.env.ref('product.group_product_pricelist').id),
                (4,self.env.ref('sale.group_delivery_invoice_address').id),
            ],
        })

        #Preparerelevanttestdata
        #Thisisnotincludedindemodatatoavoiduselessnoise
        product_attributes=self.env['product.attribute'].create([{
            'name':'PA1',
            'display_type':'radio',
            'create_variant':'dynamic'
        },{
            'name':'PA2',
            'display_type':'radio',
            'create_variant':'always'
        },{
            'name':'PA3',
            'display_type':'radio',
            'create_variant':'dynamic'
        },{
            'name':'PA4',
            'display_type':'select',
            'create_variant':'no_variant'
        },{
            'name':'PA5',
            'display_type':'select',
            'create_variant':'no_variant'
        },{
            'name':'PA7',
            'display_type':'color',
            'create_variant':'no_variant'
        },{
            'name':'PA8',
            'display_type':'radio',
            'create_variant':'no_variant'
        }])

        self.env['product.attribute.value'].create([{
            'name':'PAV'+str(i),
            'is_custom':i==9,
            'attribute_id':product_attribute.id
        }foriinrange(1,11)forproduct_attributeinproduct_attributes])

        product_template=self.product_product_custo_desk

        self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute.id,
            'product_tmpl_id':product_template.id,
            'value_ids':[(6,0,product_attribute.value_ids.ids)],
        }forproduct_attributeinproduct_attributes])
        self.start_tour("/web",'sale_product_configurator_advanced_tour',login="admin")

    deftest_03_product_configurator_edition(self):
        #Tobeabletotesttheproductconfigurator,adminusermusthaveaccessto"variants"feature,sowegivehimtherightgroupforthat
        self.env.ref('base.user_admin').write({'groups_id':[(4,self.env.ref('product.group_product_variant').id)]})
        self.start_tour("/web",'sale_product_configurator_edition_tour',login="admin")

    deftest_04_product_configurator_single_custom_value(self):
        #group_product_variant:usetheproductconfigurator
        #group_sale_pricelist:displaythepricelisttodeterminewhenitischangedafterchoosing
        #                      thepartner
        self.env.ref('base.user_admin').write({
            'groups_id':[
                (4,self.env.ref('product.group_product_variant').id),
                (4,self.env.ref('product.group_product_pricelist').id),
            ],
        })

        #Preparerelevanttestdata
        #Thisisnotincludedindemodatatoavoiduselessnoise
        product_attributes=self.env['product.attribute'].create([{
            'name':'productattribute',
            'display_type':'radio',
            'create_variant':'always'
        }])

        product_attribute_values=self.env['product.attribute.value'].create([{
            'name':'singleproductattributevalue',
            'is_custom':True,
            'attribute_id':product_attributes[0].id
        }])

        product_template=self.product_product_custo_desk

        self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attributes[0].id,
            'product_tmpl_id':product_template.id,
            'value_ids':[(6,0,[product_attribute_values[0].id])]
        }])
        self.start_tour("/web",'sale_product_configurator_single_custom_attribute_tour',login="admin")

    deftest_05_product_configurator_pricelist(self):
        """Thegoalofthistestistomakesurepricelistrulesarecorrectly
        appliedonthebackendproductconfigurator.
        AlsotestingB2Csetting:noimpactonthebackendconfigurator.
        """

        admin=self.env.ref('base.user_admin')

        #ActivateB2C
        self.env.ref('account.group_show_line_subtotals_tax_excluded').users-=admin
        self.env.ref('account.group_show_line_subtotals_tax_included').users|=admin

        #ActivepricelistonSO
        self.env.ref('product.group_product_pricelist').users|=admin

        #Adda15%taxondesk
        tax=self.env['account.tax'].create({'name':"Testtax",'amount':15})
        self.product_product_custo_desk.taxes_id=tax

        #RemovetaxfromConferenceChairandChairfloorprotection
        self.product_product_conf_chair.taxes_id=None
        self.product_product_conf_chair_floor_protect.taxes_id=None
        self.start_tour("/web",'sale_product_configurator_pricelist_tour',login="admin")

    deftest_06_product_configurator_optional_products(self):
        """Thegoalofthistestistocheckthattheproductconfigurator
        windowopenscorrectlyandletsyouselectoptionalproductseven
        ifthemainproductdoesnothavevariants.
        """
        #addanoptionalproducttotheofficechairandthecustodeskfortestingpurposes
        office_chair=self.env['product.product'].create({
            'name':'OfficeChairBlack',
        })

        custo_desk=self.product_product_custo_desk.product_variant_ids[0]
        office_chair.update({
            'optional_product_ids':[(6,0,[self.product_product_conf_chair_floor_protect.id])]
        })
        custo_desk.update({
            'optional_product_ids':[(6,0,[office_chair.product_tmpl_id.id,self.product_product_conf_chair.id])]
        })
        self.product_product_custo_desk.optional_product_ids=[(4,self.product_product_conf_chair.id)]
        self.start_tour("/web",'sale_product_configurator_optional_products_tour',login="admin")
