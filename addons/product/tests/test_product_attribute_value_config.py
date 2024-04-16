#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime
frompsycopg2importIntegrityError

fromflectra.exceptionsimportUserError,ValidationError
fromflectra.testsimporttagged
fromflectra.tests.commonimportSavepointCase
fromflectra.toolsimportmute_logger


classTestProductAttributeValueCommon(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super(TestProductAttributeValueCommon,cls).setUpClass()

        cls.computer=cls.env['product.template'].create({
            'name':'SuperComputer',
            'price':2000,
        })

        cls._add_ssd_attribute()
        cls._add_ram_attribute()
        cls._add_hdd_attribute()

        cls.computer_case=cls.env['product.template'].create({
            'name':'SuperComputerCase'
        })

        cls._add_size_attribute()

    @classmethod
    def_add_ssd_attribute(cls):
        cls.ssd_attribute=cls.env['product.attribute'].create({'name':'Memory','sequence':1})
        cls.ssd_256=cls.env['product.attribute.value'].create({
            'name':'256GB',
            'attribute_id':cls.ssd_attribute.id,
            'sequence':1,
        })
        cls.ssd_512=cls.env['product.attribute.value'].create({
            'name':'512GB',
            'attribute_id':cls.ssd_attribute.id,
            'sequence':2,
        })

        cls._add_ssd_attribute_line()

    @classmethod
    def_add_ssd_attribute_line(cls):
        cls.computer_ssd_attribute_lines=cls.env['product.template.attribute.line'].create({
            'product_tmpl_id':cls.computer.id,
            'attribute_id':cls.ssd_attribute.id,
            'value_ids':[(6,0,[cls.ssd_256.id,cls.ssd_512.id])],
        })
        cls.computer_ssd_attribute_lines.product_template_value_ids[0].price_extra=200
        cls.computer_ssd_attribute_lines.product_template_value_ids[1].price_extra=400

    @classmethod
    def_add_ram_attribute(cls):
        cls.ram_attribute=cls.env['product.attribute'].create({'name':'RAM','sequence':2})
        cls.ram_8=cls.env['product.attribute.value'].create({
            'name':'8GB',
            'attribute_id':cls.ram_attribute.id,
            'sequence':1,
        })
        cls.ram_16=cls.env['product.attribute.value'].create({
            'name':'16GB',
            'attribute_id':cls.ram_attribute.id,
            'sequence':2,
        })
        cls.ram_32=cls.env['product.attribute.value'].create({
            'name':'32GB',
            'attribute_id':cls.ram_attribute.id,
            'sequence':3,
        })
        cls.computer_ram_attribute_lines=cls.env['product.template.attribute.line'].create({
            'product_tmpl_id':cls.computer.id,
            'attribute_id':cls.ram_attribute.id,
            'value_ids':[(6,0,[cls.ram_8.id,cls.ram_16.id,cls.ram_32.id])],
        })
        cls.computer_ram_attribute_lines.product_template_value_ids[0].price_extra=20
        cls.computer_ram_attribute_lines.product_template_value_ids[1].price_extra=40
        cls.computer_ram_attribute_lines.product_template_value_ids[2].price_extra=80

    @classmethod
    def_add_hdd_attribute(cls):
        cls.hdd_attribute=cls.env['product.attribute'].create({'name':'HDD','sequence':3})
        cls.hdd_1=cls.env['product.attribute.value'].create({
            'name':'1To',
            'attribute_id':cls.hdd_attribute.id,
            'sequence':1,
        })
        cls.hdd_2=cls.env['product.attribute.value'].create({
            'name':'2To',
            'attribute_id':cls.hdd_attribute.id,
            'sequence':2,
        })
        cls.hdd_4=cls.env['product.attribute.value'].create({
            'name':'4To',
            'attribute_id':cls.hdd_attribute.id,
            'sequence':3,
        })

        cls._add_hdd_attribute_line()

    @classmethod
    def_add_hdd_attribute_line(cls):
        cls.computer_hdd_attribute_lines=cls.env['product.template.attribute.line'].create({
            'product_tmpl_id':cls.computer.id,
            'attribute_id':cls.hdd_attribute.id,
            'value_ids':[(6,0,[cls.hdd_1.id,cls.hdd_2.id,cls.hdd_4.id])],
        })
        cls.computer_hdd_attribute_lines.product_template_value_ids[0].price_extra=2
        cls.computer_hdd_attribute_lines.product_template_value_ids[1].price_extra=4
        cls.computer_hdd_attribute_lines.product_template_value_ids[2].price_extra=8

    def_add_ram_exclude_for(self):
        self._get_product_value_id(self.computer_ram_attribute_lines,self.ram_16).update({
            'exclude_for':[(0,0,{
                'product_tmpl_id':self.computer.id,
                'value_ids':[(6,0,[self._get_product_value_id(self.computer_hdd_attribute_lines,self.hdd_1).id])]
            })]
        })

    @classmethod
    def_add_size_attribute(cls):
        cls.size_attribute=cls.env['product.attribute'].create({'name':'Size','sequence':4})
        cls.size_m=cls.env['product.attribute.value'].create({
            'name':'M',
            'attribute_id':cls.size_attribute.id,
            'sequence':1,
        })
        cls.size_l=cls.env['product.attribute.value'].create({
            'name':'L',
            'attribute_id':cls.size_attribute.id,
            'sequence':2,
        })
        cls.size_xl=cls.env['product.attribute.value'].create({
            'name':'XL',
            'attribute_id':cls.size_attribute.id,
            'sequence':3,
        })
        cls.computer_case_size_attribute_lines=cls.env['product.template.attribute.line'].create({
            'product_tmpl_id':cls.computer_case.id,
            'attribute_id':cls.size_attribute.id,
            'value_ids':[(6,0,[cls.size_m.id,cls.size_l.id,cls.size_xl.id])],
        })

    def_get_product_value_id(self,product_template_attribute_lines,product_attribute_value):
        returnproduct_template_attribute_lines.product_template_value_ids.filtered(
            lambdaproduct_value_id:product_value_id.product_attribute_value_id==product_attribute_value)[0]

    def_get_product_template_attribute_value(self,product_attribute_value,model=False):
        """
            Returnthe`product.template.attribute.value`matching
                `product_attribute_value`forself.

            :param:recordsetofoneproduct.attribute.value
            :return:recordsetofoneproduct.template.attribute.valueiffound
                elseempty
        """
        ifnotmodel:
            model=self.computer
        returnmodel.valid_product_template_attribute_line_ids.filtered(
            lambdal:l.attribute_id==product_attribute_value.attribute_id
        ).product_template_value_ids.filtered(
            lambdav:v.product_attribute_value_id==product_attribute_value
        )

    def_add_exclude(self,m1,m2,product_template=False):
        m1.update({
            'exclude_for':[(0,0,{
                'product_tmpl_id':(product_templateorself.computer).id,
                'value_ids':[(6,0,[m2.id])]
            })]
        })


@tagged('post_install','-at_install')
classTestProductAttributeValueConfig(TestProductAttributeValueCommon):

    deftest_product_template_attribute_values_creation(self):
        self.assertEqual(len(self.computer_ssd_attribute_lines.product_template_value_ids),2,
            'Productattributevalues(ssd)werenotautomaticallycreated')
        self.assertEqual(len(self.computer_ram_attribute_lines.product_template_value_ids),3,
            'Productattributevalues(ram)werenotautomaticallycreated')
        self.assertEqual(len(self.computer_hdd_attribute_lines.product_template_value_ids),3,
            'Productattributevalues(hdd)werenotautomaticallycreated')
        self.assertEqual(len(self.computer_case_size_attribute_lines.product_template_value_ids),3,
            'Productattributevalues(size)werenotautomaticallycreated')

    deftest_get_variant_for_combination(self):
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)

        #completelydefinedvariant
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1
        ok_variant=self.computer._get_variant_for_combination(combination)
        self.assertEqual(ok_variant.product_template_attribute_value_ids,combination)

        #overdefinedvariant
        combination=computer_ssd_256+computer_ram_8+computer_ram_16+computer_hdd_1
        variant=self.computer._get_variant_for_combination(combination)
        self.assertEqual(len(variant),0)

        #underdefinedvariant
        combination=computer_ssd_256+computer_ram_8
        variant=self.computer._get_variant_for_combination(combination)
        self.assertFalse(variant)

    deftest_product_filtered_exclude_for(self):
        """
            SuperComputerhas18variantstotal(2ssd*3ram*3hdd)
            RAM16excludesHDD1,thatmatches2variants:
            -SSD256RAM16HDD1
            -SSD512RAM16HDD1

            =>Therehastobe16variantsleftwhenfiltered
        """
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ssd_512=self._get_product_template_attribute_value(self.ssd_512)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)

        self.assertEqual(len(self.computer._get_possible_variants()),18)
        self._add_ram_exclude_for()
        self.assertEqual(len(self.computer._get_possible_variants()),16)
        self.assertTrue(self.computer._get_variant_for_combination(computer_ssd_256+computer_ram_8+computer_hdd_1)._is_variant_possible())
        self.assertFalse(self.computer._get_variant_for_combination(computer_ssd_256+computer_ram_16+computer_hdd_1))
        self.assertFalse(self.computer._get_variant_for_combination(computer_ssd_512+computer_ram_16+computer_hdd_1))

    deftest_children_product_filtered_exclude_for(self):
        """
            SuperComputerCasehas3variantstotal(3size)
            ReferenceproductComputerwithHDD4excludesSizeM
            Thefollowingvariantwillbeexcluded:
            -SizeM

            =>Therehastobe2variantsleftwhenfiltered
        """
        computer_hdd_4=self._get_product_template_attribute_value(self.hdd_4)
        computer_size_m=self._get_product_template_attribute_value(self.size_m,self.computer_case)
        self._add_exclude(computer_hdd_4,computer_size_m,self.computer_case)
        self.assertEqual(len(self.computer_case._get_possible_variants(computer_hdd_4)),2)
        self.assertFalse(self.computer_case._get_variant_for_combination(computer_size_m)._is_variant_possible(computer_hdd_4))

    deftest_is_combination_possible(self):
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        self._add_exclude(computer_ram_16,computer_hdd_1)

        #CASE:basic
        self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))

        #CASE:ram16excludinghdd1
        self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_16+computer_hdd_1))

        #CASE:underdefinedcombination
        self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_16))

        #CASE:nocombination,novariant,justreturntheonlyvariant
        mouse=self.env['product.template'].create({'name':'Mouse'})
        self.assertTrue(mouse._is_combination_possible(self.env['product.template.attribute.value']))

        #prepworkforthelastpartofthetest
        color_attribute=self.env['product.attribute'].create({'name':'Color'})
        color_red=self.env['product.attribute.value'].create({
            'name':'Red',
            'attribute_id':color_attribute.id,
        })
        color_green=self.env['product.attribute.value'].create({
            'name':'Green',
            'attribute_id':color_attribute.id,
        })
        self.env['product.template.attribute.line'].create({
            'product_tmpl_id':mouse.id,
            'attribute_id':color_attribute.id,
            'value_ids':[(6,0,[color_red.id,color_green.id])],
        })

        mouse_color_red=self._get_product_template_attribute_value(color_red,mouse)
        mouse_color_green=self._get_product_template_attribute_value(color_green,mouse)

        self._add_exclude(computer_ssd_256,mouse_color_green,mouse)

        variant=self.computer._get_variant_for_combination(computer_ssd_256+computer_ram_8+computer_hdd_1)

        #CASE:wrongattributes(mouse_color_rednotoncomputer)
        self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_16+mouse_color_red))

        #CASE:parentok
        self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1,mouse_color_red))
        self.assertTrue(mouse._is_combination_possible(mouse_color_red,computer_ssd_256+computer_ram_8+computer_hdd_1))

        #CASE:parentexclusionbutgooddirection(parentisdirectional)
        self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1,mouse_color_green))

        #CASE:parentexclusionandwrongdirection(parentisdirectional)
        self.assertFalse(mouse._is_combination_possible(mouse_color_green,computer_ssd_256+computer_ram_8+computer_hdd_1))

        #CASE:deletedcombination
        variant.unlink()
        self.assertFalse(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))

        #CASE:ifmultiplevariantsexistforthesamecombinationandatleast
        #oneofthemisnotarchived,thecombinationispossible
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1
        self.env['product.product'].create({
            'product_tmpl_id':self.computer.id,
            'product_template_attribute_value_ids':[(6,0,combination.ids)],
            'active':False,
        })
        self.env['product.product'].create({
            'product_tmpl_id':self.computer.id,
            'product_template_attribute_value_ids':[(6,0,combination.ids)],
            'active':True,
        })
        self.assertTrue(self.computer._is_combination_possible(computer_ssd_256+computer_ram_8+computer_hdd_1))

    deftest_get_first_possible_combination(self):
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ssd_512=self._get_product_template_attribute_value(self.ssd_512)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_ram_32=self._get_product_template_attribute_value(self.ram_32)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        computer_hdd_2=self._get_product_template_attribute_value(self.hdd_2)
        computer_hdd_4=self._get_product_template_attribute_value(self.hdd_4)
        self._add_exclude(computer_ram_16,computer_hdd_1)

        #Basiccase:testalliterationsofgenerator
        gen=self.computer._get_possible_combinations()
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_8+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_8+computer_hdd_2)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_8+computer_hdd_4)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_16+computer_hdd_2)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_16+computer_hdd_4)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_32+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_32+computer_hdd_2)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_32+computer_hdd_4)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_8+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_8+computer_hdd_2)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_8+computer_hdd_4)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_16+computer_hdd_2)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_16+computer_hdd_4)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_32+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_32+computer_hdd_2)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_32+computer_hdd_4)
        self.assertIsNone(next(gen,None))

        #Giveprioritytoram_16butitisnotallowedbyhdd_1soitshouldreturnhhd_2instead
        #Testinvalidate_cacheonproduct.attribute.valuewrite
        computer_ram_16.product_attribute_value_id.sequence=-1
        self.assertEqual(self.computer._get_first_possible_combination(),computer_ssd_256+computer_ram_16+computer_hdd_2)

        #Movedowntheram,soitwilltrytochangetheraminsteadofthehdd
        #Testinvalidate_cacheonproduct.attributewrite
        self.ram_attribute.sequence=10
        self.assertEqual(self.computer._get_first_possible_combination(),computer_ssd_256+computer_ram_8+computer_hdd_1)

        #Giveprioritytoram_32andisallowedwiththerestsoitshouldreturnit
        self.ram_attribute.sequence=2
        computer_ram_16.product_attribute_value_id.sequence=2
        computer_ram_32.product_attribute_value_id.sequence=-1
        self.assertEqual(self.computer._get_first_possible_combination(),computer_ssd_256+computer_ram_32+computer_hdd_1)

        #Giveprioritytoram_16butnowitisnotallowinganyhddsoitshouldreturnram_8instead
        computer_ram_32.product_attribute_value_id.sequence=3
        computer_ram_16.product_attribute_value_id.sequence=-1
        self._add_exclude(computer_ram_16,computer_hdd_2)
        self._add_exclude(computer_ram_16,computer_hdd_4)
        self.assertEqual(self.computer._get_first_possible_combination(),computer_ssd_256+computer_ram_8+computer_hdd_1)

        #Onlythelastcombinationispossible
        computer_ram_16.product_attribute_value_id.sequence=2
        self._add_exclude(computer_ram_8,computer_hdd_1)
        self._add_exclude(computer_ram_8,computer_hdd_2)
        self._add_exclude(computer_ram_8,computer_hdd_4)
        self._add_exclude(computer_ram_32,computer_hdd_1)
        self._add_exclude(computer_ram_32,computer_hdd_2)
        self._add_exclude(computer_ram_32,computer_ssd_256)
        self.assertEqual(self.computer._get_first_possible_combination(),computer_ssd_512+computer_ram_32+computer_hdd_4)

        #Notpossibletoaddanexclusionwhenonlyonevariantisleft->itdeletestheproducttemplateassociatedtoit
        withself.assertRaises(UserError),self.cr.savepoint():
            self._add_exclude(computer_ram_32,computer_hdd_4)

        #Ifanexclusionruledeletesallvariantsatonceitdoesnotdeletethetemplate.
        #Herewecantest`_get_first_possible_combination`withaproducttemplatewithnovariants
        #Deletesallexclusions
        forexclusionincomputer_ram_32.exclude_for:
            computer_ram_32.write({
                'exclude_for':[(2,exclusion.id,0)]
            })

        #Activatesallexclusionsatonce
        computer_ram_32.write({
            'exclude_for':[(0,computer_ram_32.exclude_for.id,{
                'product_tmpl_id':self.computer.id,
                'value_ids':[(6,0,[computer_hdd_1.id,computer_hdd_2.id,computer_hdd_4.id,computer_ssd_256.id,computer_ssd_512.id])]
            })]
        })

        self.assertEqual(self.computer._get_first_possible_combination(),self.env['product.template.attribute.value'])
        gen=self.computer._get_possible_combinations()
        self.assertIsNone(next(gen,None))

        #Testingparentcase
        mouse=self.env['product.template'].create({'name':'Mouse'})
        self.assertTrue(mouse._is_combination_possible(self.env['product.template.attribute.value']))

        #prepworkforthelastpartofthetest
        color_attribute=self.env['product.attribute'].create({'name':'Color'})
        color_red=self.env['product.attribute.value'].create({
            'name':'Red',
            'attribute_id':color_attribute.id,
        })
        color_green=self.env['product.attribute.value'].create({
            'name':'Green',
            'attribute_id':color_attribute.id,
        })
        self.env['product.template.attribute.line'].create({
            'product_tmpl_id':mouse.id,
            'attribute_id':color_attribute.id,
            'value_ids':[(6,0,[color_red.id,color_green.id])],
        })

        mouse_color_red=self._get_product_template_attribute_value(color_red,mouse)
        mouse_color_green=self._get_product_template_attribute_value(color_green,mouse)

        self._add_exclude(computer_ssd_256,mouse_color_red,mouse)
        self.assertEqual(mouse._get_first_possible_combination(parent_combination=computer_ssd_256+computer_ram_8+computer_hdd_1),mouse_color_green)

        #Testtoseeifseveralattribute_lineforsameattributeiswellhandled
        color_blue=self.env['product.attribute.value'].create({
            'name':'Blue',
            'attribute_id':color_attribute.id,
        })
        color_yellow=self.env['product.attribute.value'].create({
            'name':'Yellow',
            'attribute_id':color_attribute.id,
        })
        self.env['product.template.attribute.line'].create({
            'product_tmpl_id':mouse.id,
            'attribute_id':color_attribute.id,
            'value_ids':[(6,0,[color_blue.id,color_yellow.id])],
        })
        mouse_color_yellow=self._get_product_template_attribute_value(color_yellow,mouse)
        self.assertEqual(mouse._get_first_possible_combination(necessary_values=mouse_color_yellow),mouse_color_red+mouse_color_yellow)

        #Makingsureit'snotextremelyslow(hastodiscardinvalidcombinationsearly!)
        product_template=self.env['product.template'].create({
            'name':'manycombinations',
        })

        foriinrange(10):
            #createtheattributes
            product_attribute=self.env['product.attribute'].create({
                'name':"att%s"%i,
                'create_variant':'dynamic',
                'sequence':i,
            })

            forjinrange(50):
                #createtheattributevalues
                value=self.env['product.attribute.value'].create([{
                    'name':"val%s"%j,
                    'attribute_id':product_attribute.id,
                    'sequence':j,
                }])

            #setattributeandattributevaluesonthetemplate
            self.env['product.template.attribute.line'].create([{
                'attribute_id':product_attribute.id,
                'product_tmpl_id':product_template.id,
                'value_ids':[(6,0,product_attribute.value_ids.ids)]
            }])

        self._add_exclude(
            self._get_product_template_attribute_value(product_template.attribute_line_ids[1].value_ids[0],
                                                       model=product_template),
            self._get_product_template_attribute_value(product_template.attribute_line_ids[0].value_ids[0],
                                                       model=product_template),
            product_template)
        self._add_exclude(
            self._get_product_template_attribute_value(product_template.attribute_line_ids[0].value_ids[0],
                                                       model=product_template),
            self._get_product_template_attribute_value(product_template.attribute_line_ids[1].value_ids[1],
                                                       model=product_template),
            product_template)

        combination=self.env['product.template.attribute.value']
        foridx,ptalinenumerate(product_template.attribute_line_ids):
            ifidx!=1:
                value=ptal.product_template_value_ids[0]
            else:
                value=ptal.product_template_value_ids[2]
            combination+=value

        started_at=time.time()
        self.assertEqual(product_template._get_first_possible_combination(),combination)
        elapsed=time.time()-started_at
        #Itshouldbeaboutinstantaneous,0.5toavoidfalsepositives
        self.assertLess(elapsed,0.5)




    deftest_get_closest_possible_combinations(self):
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ssd_512=self._get_product_template_attribute_value(self.ssd_512)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_ram_16=self._get_product_template_attribute_value(self.ram_16)
        computer_ram_32=self._get_product_template_attribute_value(self.ram_32)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        computer_hdd_2=self._get_product_template_attribute_value(self.hdd_2)
        computer_hdd_4=self._get_product_template_attribute_value(self.hdd_4)
        self._add_exclude(computer_ram_16,computer_hdd_1)

        #CASEnothingspecial(test2iterations)
        gen=self.computer._get_closest_possible_combinations(None)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_8+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_8+computer_hdd_2)

        #CASEcontainscomputer_hdd_1(testalliterations)
        gen=self.computer._get_closest_possible_combinations(computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_8+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_256+computer_ram_32+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_8+computer_hdd_1)
        self.assertEqual(next(gen),computer_ssd_512+computer_ram_32+computer_hdd_1)
        self.assertIsNone(next(gen,None))

        #CASEcontainscomputer_hdd_2
        self.assertEqual(self.computer._get_closest_possible_combination(computer_hdd_2),
            computer_ssd_256+computer_ram_8+computer_hdd_2)

        #CASEcontainscomputer_hdd_2,computer_ram_16
        self.assertEqual(self.computer._get_closest_possible_combination(computer_hdd_2+computer_ram_16),
            computer_ssd_256+computer_ram_16+computer_hdd_2)

        #CASEinvalidcombination(excluded):
        self.assertEqual(self.computer._get_closest_possible_combination(computer_hdd_1+computer_ram_16),
            computer_ssd_256+computer_ram_8+computer_hdd_1)

        #CASEinvalidcombination(toomuch):
        self.assertEqual(self.computer._get_closest_possible_combination(computer_ssd_256+computer_ram_8+computer_hdd_4+computer_hdd_2),
            computer_ssd_256+computer_ram_8+computer_hdd_4)

        #Makesurethisisnotextremelyslow:
        product_template=self.env['product.template'].create({
            'name':'manycombinations',
        })

        foriinrange(10):
            #createtheattributes
            product_attribute=self.env['product.attribute'].create({
                'name':"att%s"%i,
                'create_variant':'dynamic',
                'sequence':i,
            })

            forjinrange(10):
                #createtheattributevalues
                self.env['product.attribute.value'].create([{
                    'name':"val%s/%s"%(i,j),
                    'attribute_id':product_attribute.id,
                    'sequence':j,
                }])

            #setattributeandattributevaluesonthetemplate
            self.env['product.template.attribute.line'].create([{
                'attribute_id':product_attribute.id,
                'product_tmpl_id':product_template.id,
                'value_ids':[(6,0,product_attribute.value_ids.ids)]
            }])

        #Getavalueinthemiddleforeachattributetomakesureitwould
        #taketimetoreachit(ifloopingonebyonelikebeforethefix).
        combination=self.env['product.template.attribute.value']
        forptalinproduct_template.attribute_line_ids:
            combination+=ptal.product_template_value_ids[5]

        started_at=time.time()
        self.assertEqual(product_template._get_closest_possible_combination(combination),combination)
        elapsed=time.time()-started_at
        #Itshouldtakearound10ms,buttoavoidfalsepositiveswecheckan
        #highervalue.Beforethefixitwouldtakehours.
        self.assertLess(elapsed,0.5)

    deftest_clear_caches(self):
        """Thegoalofthistestistomakesurethecacheisinvalidatedwhen
        itshouldbe."""
        computer_ssd_256=self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8=self._get_product_template_attribute_value(self.ram_8)
        computer_hdd_1=self._get_product_template_attribute_value(self.hdd_1)
        combination=computer_ssd_256+computer_ram_8+computer_hdd_1

        #CASE:initialresultof_get_variant_for_combination
        variant=self.computer._get_variant_for_combination(combination)
        self.assertTrue(variant)

        #CASE:clear_cachesinproduct.productunlink
        variant.unlink()
        self.assertFalse(self.computer._get_variant_for_combination(combination))

        #CASE:clear_cachesinproduct.productcreate
        variant=self.env['product.product'].create({
            'product_tmpl_id':self.computer.id,
            'product_template_attribute_value_ids':[(6,0,combination.ids)],
        })
        self.assertEqual(variant,self.computer._get_variant_for_combination(combination))

        #CASE:clear_cachesinproduct.productwrite
        variant.product_template_attribute_value_ids=False
        self.assertFalse(self.computer._get_variant_id_for_combination(combination))

    deftest_constraints(self):
        """Thegoalofthistestistomakesureconstraintsarecorrect."""
        withself.assertRaises(UserError,msg="can'tchangevariantscreationmodeofattributeusedonproduct"):
            self.ram_attribute.create_variant='no_variant'

        withself.assertRaises(UserError,msg="can'tdeleteattributeusedonproduct"):
            self.ram_attribute.unlink()

        withself.assertRaises(UserError,msg="can'tchangetheattributeofanvalueusedonproduct"):
            self.ram_32.attribute_id=self.hdd_attribute.id

        withself.assertRaises(UserError,msg="can'tdeletevalueusedonproduct"):
            self.ram_32.unlink()

        withself.assertRaises(ValidationError,msg="can'thaveattributewithoutvalueonproduct"):
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id':self.computer_case.id,
                'attribute_id':self.hdd_attribute.id,
                'value_ids':[(6,0,[])],
            })

        withself.assertRaises(ValidationError,msg="valueattributemustmatchlineattribute"):
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id':self.computer_case.id,
                'attribute_id':self.ram_attribute.id,
                'value_ids':[(6,0,[self.ssd_256.id])],
            })

        withself.assertRaises(UserError,msg="can'tchangetheattributeofanattributeline"):
            self.computer_ssd_attribute_lines.attribute_id=self.hdd_attribute.id

        withself.assertRaises(UserError,msg="can'tchangetheproductofanattributeline"):
            self.computer_ssd_attribute_lines.product_tmpl_id=self.computer_case.id

        withself.assertRaises(UserError,msg="can'tchangethevalueofaproducttemplateattributevalue"):
            self.computer_ram_attribute_lines.product_template_value_ids[0].product_attribute_value_id=self.hdd_1

        withself.assertRaises(UserError,msg="can'tchangetheproductofaproducttemplateattributevalue"):
            self.computer_ram_attribute_lines.product_template_value_ids[0].product_tmpl_id=self.computer_case.id

        withmute_logger('flectra.sql_db'),self.assertRaises(IntegrityError,msg="can'thavetwovalueswiththesamenameforthesameattribute"):
            self.env['product.attribute.value'].create({
                'name':'32GB',
                'attribute_id':self.ram_attribute.id,
            })

    deftest_inactive_related_product_update(self):
        """
            Createaproductandgiveitaproductattributethenarchiveit,deletetheproductattribute,
            unarchivetheproductandcheckthattheproductisnotrelatedtotheproductattribute.
        """
        product_attribut=self.env['product.attribute'].create({
            'name':'PA',
            'sequence':1,
            'create_variant':'no_variant',
        })
        a1=self.env['product.attribute.value'].create({
            'name':'pa_value',
            'attribute_id':product_attribut.id,
            'sequence':1,
        })
        product=self.env['product.template'].create({
            'name':'P1',
            'type':'consu',
            'attribute_line_ids':[(0,0,{
                'attribute_id':product_attribut.id,
                'value_ids':[(6,0,[a1.id])],
            })]
        })
        self.assertTrue(product_attribut.is_used_on_products,'Theproductattributemusthaveanassociatedproduct')
        product.action_archive()
        self.assertFalse(product.active,'Theproductshouldbearchived.')
        product.write({'attribute_line_ids':[[5,0,0]]})
        product.action_unarchive()
        self.assertTrue(product.active,'Theproductshouldbeunarchived.')
        self.assertFalse(product_attribut.is_used_on_products,'Theproductattributemustnothaveanassociatedproduct')
