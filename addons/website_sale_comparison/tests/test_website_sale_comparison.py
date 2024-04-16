#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportOrderedDict
fromlxmlimportetree
fromflectraimporttools

importflectra.tests


@flectra.tests.tagged('-at_install','post_install')
classTestWebsiteSaleComparison(flectra.tests.TransactionCase):
    deftest_01_website_sale_comparison_remove(self):
        """Thistourmakessuretheproductpagestillworksafterthemodule
        `website_sale_comparison`hasbeenremoved.

        Technicallyitteststheremovalofcopiedviewsbythebasemethod
        `_remove_copied_views`.Theproblematicviewthathastoberemovedis
        `product_add_to_compare`becauseithasareferenceto`add_to_compare`.
        """
        #YTITODO:Adaptthistourwithoutdemodata
        #Istilldidn'tfigurewhy,butthistestfreezesonrunbot
        #withoutthedemodata
        iftools.config["without_demo"]:
            return

        Website0=self.env['website'].with_context(website_id=None)
        Website1=self.env['website'].with_context(website_id=1)

        #Createagenericinheritedview,withakeynotstartingwith
        #`website_sale_comparison`otherwisetheunlinkwillworkjustbasedon
        #thekey,butwewanttotestalsofor`MODULE_UNINSTALL_FLAG`.
        product_add_to_compare=Website0.viewref('website_sale_comparison.product_add_to_compare')
        test_view_key='my_test.my_key'
        self.env['ir.ui.view'].with_context(website_id=None).create({
            'name':'testinheritedview',
            'key':test_view_key,
            'inherit_id':product_add_to_compare.id,
            'arch':'<div/>',
        })

        #Retrievethegenericview
        product=Website0.viewref('website_sale.product')
        #TriggerCOWtocreatespecificviewsofthewholetree
        product.with_context(website_id=1).write({'name':'TriggerCOW'})

        #Verifyinitialstate:thespecificviewsexist
        self.assertEqual(Website1.viewref('website_sale.product').website_id.id,1)
        self.assertEqual(Website1.viewref('website_sale_comparison.product_add_to_compare').website_id.id,1)
        self.assertEqual(Website1.viewref(test_view_key).website_id.id,1)

        #Removethemodule(use`module_uninstall`becauseitisenoughtotest
        #whatwewanthere,noneed/can'tuse`button_immediate_uninstall`
        #becauseitwouldcommitthetesttransaction)
        website_sale_comparison=self.env['ir.module.module'].search([('name','=','website_sale_comparison')])
        website_sale_comparison.module_uninstall()

        #Checkthatthegenericviewiscorrectlyremoved
        self.assertFalse(Website0.viewref('website_sale_comparison.product_add_to_compare',raise_if_not_found=False))
        #Checkthatthespecificviewiscorrectlyremoved
        self.assertFalse(Website1.viewref('website_sale_comparison.product_add_to_compare',raise_if_not_found=False))

        #Checkthatthegenericinheritedviewiscorrectlyremoved
        self.assertFalse(Website0.viewref(test_view_key,raise_if_not_found=False))
        #Checkthatthespecificinheritedviewiscorrectlyremoved
        self.assertFalse(Website1.viewref(test_view_key,raise_if_not_found=False))


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    defsetUp(self):
        super(TestUi,self).setUp()
        self.template_margaux=self.env['product.template'].create({
            'name':"ChâteauMargaux",
            'website_published':True,
            'list_price':0,
        })
        self.attribute_varieties=self.env['product.attribute'].create({
            'name':'GrapeVarieties',
            'sequence':2,
        })
        self.attribute_vintage=self.env['product.attribute'].create({
            'name':'Vintage',
            'sequence':1,
        })
        self.values_varieties=self.env['product.attribute.value'].create({
            'name':n,
            'attribute_id':self.attribute_varieties.id,
            'sequence':i,
        }fori,ninenumerate(['CabernetSauvignon','Merlot','CabernetFranc','PetitVerdot']))
        self.values_vintage=self.env['product.attribute.value'].create({
            'name':n,
            'attribute_id':self.attribute_vintage.id,
            'sequence':i,
        }fori,ninenumerate(['2018','2017','2016','2015']))
        self.attribute_line_varieties=self.env['product.template.attribute.line'].create([{
            'product_tmpl_id':self.template_margaux.id,
            'attribute_id':self.attribute_varieties.id,
            'value_ids':[(6,0,v.ids)],
        }forvinself.values_varieties])
        self.attribute_line_vintage=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.template_margaux.id,
            'attribute_id':self.attribute_vintage.id,
            'value_ids':[(6,0,self.values_vintage.ids)],
        })
        self.variants_margaux=self.template_margaux._get_possible_variants_sorted()

        forvariant,priceinzip(self.variants_margaux,[487.32,394.05,532.44,1047.84]):
            variant.product_template_attribute_value_ids.filtered(lambdaptav:ptav.attribute_id==self.attribute_vintage).price_extra=price

    deftest_01_admin_tour_product_comparison(self):
        #YTIFIXME:Adapttoworkwithoutdemodata
        iftools.config["without_demo"]:
            return
        self.start_tour("/",'product_comparison',login='admin')

    deftest_02_attribute_multiple_lines(self):
        #Caseproductpagewith"Productattributestable"disabled(website_salestandardcase)
        self.env['website'].viewref('website_sale_comparison.product_attributes_body').active=False
        res=self.url_open('/shop/%d'%self.template_margaux.id)
        self.assertEqual(res.status_code,200)
        root=etree.fromstring(res.content,etree.HTMLParser())

        p=root.xpath('//div[@id="product_attributes_simple"]/p')[0]
        text=etree.tostring(p,encoding='unicode',method='text')
        self.assertEqual(text.replace('','').replace('\n',''),"GrapeVarieties:CabernetSauvignon,Merlot,CabernetFranc,PetitVerdot")

        #Caseproductpagewith"Productattributestable"enabled
        self.env['website'].viewref('website_sale_comparison.product_attributes_body').active=True
        res=self.url_open('/shop/%d'%self.template_margaux.id)
        self.assertEqual(res.status_code,200)
        root=etree.fromstring(res.content,etree.HTMLParser())

        tr_vintage=root.xpath('//div[@id="product_specifications"]//tr')[0]
        text_vintage=etree.tostring(tr_vintage,encoding='unicode',method='text')
        self.assertEqual(text_vintage.replace('','').replace('\n',''),"Vintage2018or2017or2016or2015")

        tr_varieties=root.xpath('//div[@id="product_specifications"]//tr')[1]
        text_varieties=etree.tostring(tr_varieties,encoding='unicode',method='text')
        self.assertEqual(text_varieties.replace('','').replace('\n',''),"GrapeVarietiesCabernetSauvignon,Merlot,CabernetFranc,PetitVerdot")

        #Casecomparepage
        res=self.url_open('/shop/compare/?products=%s'%','.join(str(id)foridinself.variants_margaux.ids))
        self.assertEqual(res.status_code,200)
        root=etree.fromstring(res.content,etree.HTMLParser())

        table=root.xpath('//table[@id="o_comparelist_table"]')[0]

        products=table.xpath('//a[@class="o_product_comparison_table"]')
        self.assertEqual(len(products),4)
        forproduct,nameinzip(products,['ChâteauMargaux(2018)','ChâteauMargaux(2017)','ChâteauMargaux(2016)','ChâteauMargaux(2015)']):
            text=etree.tostring(product,encoding='unicode',method='text')
            self.assertEqual(text.replace('','').replace('\n',''),name)

        tr_vintage=table.xpath('tbody/tr')[0]
        text_vintage=etree.tostring(tr_vintage,encoding='unicode',method='text')
        self.assertEqual(text_vintage.replace('','').replace('\n',''),"Vintage2018201720162015")

        tr_varieties=table.xpath('tbody/tr')[1]
        text_varieties=etree.tostring(tr_varieties,encoding='unicode',method='text')
        self.assertEqual(text_varieties.replace('','').replace('\n',''),"GrapeVarieties"+4*"CabernetSauvignon,Merlot,CabernetFranc,PetitVerdot")

    deftest_03_category_order(self):
        """Testthatcategoriesareshowninthecorrectorderwhenthe
        attributesareinadifferentorder."""
        category_vintage=self.env['product.attribute.category'].create({
            'name':'Vintage',
            'sequence':2,
        })
        category_varieties=self.env['product.attribute.category'].create({
            'name':'Varieties',
            'sequence':1,
        })
        self.attribute_vintage.category_id=category_vintage
        self.attribute_varieties.category_id=category_varieties

        prep_categories=self.template_margaux.valid_product_template_attribute_line_ids._prepare_categories_for_display()
        self.assertEqual(prep_categories,OrderedDict([
            (category_varieties,self.attribute_line_varieties),
            (category_vintage,self.attribute_line_vintage),
        ]))

        prep_categories=self.variants_margaux[0]._prepare_categories_for_display()
        self.assertEqual(prep_categories,OrderedDict([
            (category_varieties,OrderedDict([
                (self.attribute_varieties,OrderedDict([
                    (self.template_margaux.product_variant_id,self.attribute_line_varieties.product_template_value_ids)
                ]))
            ])),
            (category_vintage,OrderedDict([
                (self.attribute_vintage,OrderedDict([
                    (self.template_margaux.product_variant_id,self.attribute_line_vintage.product_template_value_ids[0])
                ]))
            ])),
        ]))
