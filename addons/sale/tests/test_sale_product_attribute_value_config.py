#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields
fromflectra.addons.product.tests.test_product_attribute_value_configimportTestProductAttributeValueCommon
fromflectra.testsimporttagged


classTestSaleProductAttributeValueCommon(TestProductAttributeValueCommon):

    @classmethod
    def_setup_currency(cls,currency_ratio=2):
        """Getorcreateacurrency.Thismakesthetestnon-reliantondemo.

        Withaneasycurrencyrate,forasimple2ratiointhefollowingtests.
        """
        from_currency=cls.computer.currency_id
        cls._set_or_create_rate_today(from_currency,rate=1)

        to_currency=cls._get_or_create_currency("mycurrency","C")
        cls._set_or_create_rate_today(to_currency,currency_ratio)
        returnto_currency

    @classmethod
    def_set_or_create_rate_today(cls,currency,rate):
        """Getorcreateacurrencyratefortoday.Thismakesthetest
        non-reliantondemodata."""
        name=fields.Date.today()
        currency_id=currency.id
        company_id=cls.env.company.id

        CurrencyRate=cls.env['res.currency.rate']

        currency_rate=CurrencyRate.search([
            ('company_id','=',company_id),
            ('currency_id','=',currency_id),
            ('name','=',name),
        ])

        ifcurrency_rate:
            currency_rate.rate=rate
        else:
            CurrencyRate.create({
                'company_id':company_id,
                'currency_id':currency_id,
                'name':name,
                'rate':rate,
            })

    @classmethod
    def_get_or_create_currency(cls,name,symbol):
        """Getorcreateacurrencybasedonname.Thismakesthetest
        non-reliantondemodata."""
        currency=cls.env['res.currency'].search([('name','=',name)])
        returncurrencyorcurrency.create({
            'name':name,
            'symbol':symbol,
        })


@tagged('post_install','-at_install')
classTestSaleProductAttributeValueConfig(TestSaleProductAttributeValueCommon):
    def_setup_pricelist(self,currency_ratio=2):
        to_currency=self._setup_currency(currency_ratio)

        discount=10

        pricelist=self.env['product.pricelist'].create({
            'name':'testpl',
            'currency_id':to_currency.id,
            'company_id':self.computer.company_id.id,
        })

        pricelist_item=self.env['product.pricelist.item'].create({
            'min_quantity':2,
            'compute_price':'percentage',
            'percent_price':discount,
            'pricelist_id':pricelist.id,
        })

        return(pricelist,pricelist_item,currency_ratio,1-discount/100)

    deftest_01_is_combination_possible_archived(self):
        """Thegoalistotestthepossibilityofarchivedcombinations.

        Thistestcouldnotbeputintoproductmodulebecausetherewasno
        modelwhichhadproduct_idasrequiredandwithoutcascadeondelete.
        Herewehavethesalesorderlineinthissituation.

        Thisisanecessaryconditionfor`_create_variant_ids`toarchive
        insteadofdeletethevariants.
        """
        defdo_test(self):
            computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
            computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
            computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
            computer_hdd_2=self._get_product_template_attribute_value(self.hdd_2)

            variant=self.computer._get_variant_for_combination(computer_ssd_256+computer_ram_8+computer_hdd_1)
            variant2=self.computer._get_variant_for_combination(computer_ssd_256+computer_ram_8+computer_hdd_2)

            self.assertTrue(variant)
            self.assertTrue(variant2)

            #CreateadummySOtopreventthevariantfrombeingdeletedby
            #_create_variant_ids()becausethevariantisarelatedfieldthat
            #isrequiredontheSOline
            so=self.env['sale.order'].create({'partner_id':1})
            self.env['sale.order.line'].create({
                'order_id':so.id,
                'name':"test",
                'product_id':variant.id
            })
            #additionalvarianttotestcorrectignoringwhenmismatchvalues
            self.env['sale.order.line'].create({
                'order_id':so.id,
                'name':"test",
                'product_id':variant2.id
            })

            variant2.active=False
            #CASE:1notarchived,2archived
            self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))
            self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_2))
            #CASE:botharchivedcombination(withoutno_variant)
            variant.active=False
            self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_2))
            self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))

            #CASE:OKafterattributelineremoved
            self.computer_hdd_attribute_lines.write({'active':False})
            self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8))

            #CASE:notarchived(withno_variant)
            self.hdd_attribute.create_variant='no_variant'
            self._add_hdd_attribute_line()
            computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
            computer_hdd_2=self._get_product_template_attribute_value(self.hdd_2)

            self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))

            #CASE:archivedcombinationfound(withno_variant)
            variant=self.computer._get_variant_for_combination(computer_ssd_256+computer_ram_8+computer_hdd_1)
            variant.active=False
            self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))

            #CASE:archivedcombinationhasdifferentattributes(includingno_variant)
            self.computer_ssd_attribute_lines.write({'active':False})

            variant4=self.computer._get_variant_for_combination(computer_ram_8+computer_hdd_1)
            self.env['sale.order.line'].create({
                'order_id':so.id,
                'name':"test",
                'product_id':variant4.id
            })
            self.assertTrue(self.computer._is_combination_possible(computer_ram_8+computer_hdd_1))

            #CASE:archivedcombinationhasdifferentattributes(withoutno_variant)
            self.computer_hdd_attribute_lines.write({'active':False})
            self.hdd_attribute.create_variant='always'
            self._add_hdd_attribute_line()
            computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
            computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
            computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
            computer_hdd_2=self._get_product_template_attribute_value(self.hdd_2)

            variant5=self.computer._get_variant_for_combination(computer_ram_8+computer_hdd_1)
            self.env['sale.order.line'].create({
                'order_id':so.id,
                'name':"test",
                'product_id':variant5.id
            })

            self.assertTrue(variant4!=variant5)

            self.assertTrue(self.computer._is_combination_possible(computer_ram_8+computer_hdd_1))

        computer_ssd_256_before=self._get_product_template_attribute_value(self.ssd_256)

        do_test(self)

        #CASE:addbacktheremovedattributeandtryeverythingagain
        self.computer_ssd_attribute_lines=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.computer.id,
            'attribute_id':self.ssd_attribute.id,
            'value_ids':[(6,0,[self.ssd_256.id,self.ssd_512.id])],
        })

        computer_ssd_256_after=self._get_product_template_attribute_value(self.ssd_256)
        self.assertEqual(computer_ssd_256_after,computer_ssd_256_before)
        self.assertEqual(computer_ssd_256_after.attribute_line_id,computer_ssd_256_before.attribute_line_id)
        do_test(self)

    deftest_02_get_combination_info(self):
        #Ifusingmulti-company,company_idwillbeFalse,andthiscodeshould
        #stillwork.
        #Thecasewithacompany_idwillbeimplicitlytestedonwebsite_sale.
        self.computer.company_id=False

        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)

        #CASE:nopricelist,nocurrency,withexistingcombination,withprice_extraonattributes
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1
        computer_variant=self.computer._get_variant_for_combination(combination)

        res=self.computer._get_combination_info(combination)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],computer_variant.id)
        self.assertEqual(res['display_name'],"SuperComputer(256GB,8GB,1To)")
        self.assertEqual(res['price'],2222)
        self.assertEqual(res['list_price'],2222)
        self.assertEqual(res['price_extra'],222)

        #CASE:nocombination,productgiven
        res=self.computer._get_combination_info(self.env['product.template.attribute.value'],computer_variant.id)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],computer_variant.id)
        self.assertEqual(res['display_name'],"SuperComputer(256GB,8GB,1To)")
        self.assertEqual(res['price'],2222)
        self.assertEqual(res['list_price'],2222)
        self.assertEqual(res['price_extra'],222)

        #CASE:usingpricelist,quantityrule
        pricelist,pricelist_item,currency_ratio,discount_ratio=self._setup_pricelist()

        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],computer_variant.id)
        self.assertEqual(res['display_name'],"SuperComputer(256GB,8GB,1To)")
        self.assertEqual(res['price'],2222*currency_ratio*discount_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)

        #CASE:no_variantcombination,it'sanothervariantnow

        self.computer_ssd_attribute_lines.write({'active':False})
        self.ssd_attribute.create_variant='no_variant'
        self._add_ssd_attribute_line()
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1

        computer_variant_new=self.computer._get_variant_for_combination(combination)
        self.assertTrue(computer_variant_new)

        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],computer_variant_new.id)
        self.assertEqual(res['display_name'],"SuperComputer(8GB,1To)")
        self.assertEqual(res['price'],2222*currency_ratio*discount_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)

        #CASE:dynamiccombination,butthevariantalreadyexists
        self.computer_hdd_attribute_lines.write({'active':False})
        self.hdd_attribute.create_variant='dynamic'
        self._add_hdd_attribute_line()
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1

        computer_variant_new=self.computer._create_product_variant(combination)
        self.assertTrue(computer_variant_new)

        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],computer_variant_new.id)
        self.assertEqual(res['display_name'],"SuperComputer(8GB,1To)")
        self.assertEqual(res['price'],2222*currency_ratio*discount_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)

        #CASE:dynamiccombination,novariantexisting
        #Testinvalidate_cacheonproduct.template_create_variant_ids
        self._add_keyboard_attribute()
        combination+=self._get_product_template_attribute_value(self.keyboard_excluded)
        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],False)
        self.assertEqual(res['display_name'],"SuperComputer(8GB,1To,Excluded)")
        self.assertEqual(res['price'],(2222-5)*currency_ratio*discount_ratio)
        self.assertEqual(res['list_price'],(2222-5)*currency_ratio)
        self.assertEqual(res['price_extra'],(222-5)*currency_ratio)

        #CASE:pricelistsetvalueto0,novariant
        #Testinvalidate_cacheonproduct.pricelistwrite
        pricelist_item.percent_price=100
        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['product_template_id'],self.computer.id)
        self.assertEqual(res['product_id'],False)
        self.assertEqual(res['display_name'],"SuperComputer(8GB,1To,Excluded)")
        self.assertEqual(res['price'],0)
        self.assertEqual(res['list_price'],(2222-5)*currency_ratio)
        self.assertEqual(res['price_extra'],(222-5)*currency_ratio)

    deftest_03_get_combination_info_discount_policy(self):
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1

        pricelist,pricelist_item,currency_ratio,discount_ratio=self._setup_pricelist()

        pricelist.discount_policy='with_discount'

        #CASE:nodiscount,settingwith_discount
        res=self.computer._get_combination_info(combination,add_qty=1,pricelist=pricelist)
        self.assertEqual(res['price'],2222*currency_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)
        self.assertEqual(res['has_discounted_price'],False)

        #CASE:discount,settingwith_discount
        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['price'],2222*currency_ratio*discount_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)
        self.assertEqual(res['has_discounted_price'],False)

        #CASE:nodiscount,settingwithout_discount
        pricelist.discount_policy='without_discount'
        res=self.computer._get_combination_info(combination,add_qty=1,pricelist=pricelist)
        self.assertEqual(res['price'],2222*currency_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)
        self.assertEqual(res['has_discounted_price'],False)

        #CASE:discount,settingwithout_discount
        res=self.computer._get_combination_info(combination,add_qty=2,pricelist=pricelist)
        self.assertEqual(res['price'],2222*currency_ratio*discount_ratio)
        self.assertEqual(res['list_price'],2222*currency_ratio)
        self.assertEqual(res['price_extra'],222*currency_ratio)
        self.assertEqual(res['has_discounted_price'],True)

    deftest_04_create_product_variant_non_dynamic(self):
        """Thegoalofthistestistomakesurethecreate_product_variantdoes
        notcreatevariantifthetypeisnotdynamic.Itcanhoweverreturna
        variantifitalreadyexists."""
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        self._add_exclude(computer_ram_16,computer_hdd_1)

        #CASE:variantisalreadycreated,itshouldreturnit
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1
        variant1=self.computer._get_variant_for_combination(combination)
        self.assertEqual(self.computer._create_product_variant(combination),variant1)

        #CASE:variantdoesnotexist,buttemplateisnon-dynamic,soit
        #shouldnotcreateit
        Product=self.env['product.product']
        variant1.unlink()
        self.assertEqual(self.computer._create_product_variant(combination),Product)

    deftest_05_create_product_variant_dynamic(self):
        """Thegoalofthistestistomakesurethecreate_product_variantdoes
        workwithdynamic.Ifthecombinationispossible,itshouldcreateit.
        Ifit'snotpossible,itshouldnotcreateit."""
        self.computer_hdd_attribute_lines.write({'active':False})
        self.hdd_attribute.create_variant='dynamic'
        self._add_hdd_attribute_line()

        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        self._add_exclude(computer_ram_16,computer_hdd_1)

        #CASE:variantdoesnotexist,butcombinationisnotpossible
        #soitshouldnotcreateit
        impossible_combination=computer_ssd_256+computer_ram_16+computer_hdd_1
        Product=self.env['product.product']
        self.assertEqual(self.computer._create_product_variant(impossible_combination),Product)

        #CASE:thevariantdoesnotexist,andthecombinationispossible,so
        #itshouldcreateit
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1
        variant=self.computer._create_product_variant(combination)
        self.assertTrue(variant)

        #CASE:thevariantalreadyexists,soitshouldreturnit
        self.assertEqual(variant,self.computer._create_product_variant(combination))

    def_add_keyboard_attribute(self):
        self.keyboard_attribute=self.env['product.attribute'].create({
            'name':'Keyboard',
            'sequence':6,
            'create_variant':'dynamic',
        })
        self.keyboard_included=self.env['product.attribute.value'].create({
            'name':'Included',
            'attribute_id':self.keyboard_attribute.id,
            'sequence':1,
        })
        self.keyboard_excluded=self.env['product.attribute.value'].create({
            'name':'Excluded',
            'attribute_id':self.keyboard_attribute.id,
            'sequence':2,
        })
        self.computer_keyboard_attribute_lines=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.computer.id,
            'attribute_id':self.keyboard_attribute.id,
            'value_ids':[(6,0,[self.keyboard_included.id,self.keyboard_excluded.id])],
        })
        self.computer_keyboard_attribute_lines.product_template_value_ids[0].price_extra=5
        self.computer_keyboard_attribute_lines.product_template_value_ids[1].price_extra=-5
