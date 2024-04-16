#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
fromcollectionsimportOrderedDict
fromdatetimeimportdatetime,timedelta
importio
importunittest.mock

fromPILimportImage

from.importcommon
fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportTransactionCase,Form


classTestVariantsSearch(TransactionCase):

    defsetUp(self):
        res=super(TestVariantsSearch,self).setUp()
        self.size_attr=self.env['product.attribute'].create({'name':'Size'})
        self.size_attr_value_s=self.env['product.attribute.value'].create({'name':'S','attribute_id':self.size_attr.id})
        self.size_attr_value_m=self.env['product.attribute.value'].create({'name':'M','attribute_id':self.size_attr.id})
        self.size_attr_value_l=self.env['product.attribute.value'].create({'name':'L','attribute_id':self.size_attr.id})
        self.product_shirt_template=self.env['product.template'].create({
            'name':'Shirt',
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(6,0,[self.size_attr_value_l.id])],
            })]
        })
        returnres

    deftest_attribute_line_search(self):
        search_not_to_be_found=self.env['product.template'].search(
            [('attribute_line_ids','=','M')]
        )
        self.assertNotIn(self.product_shirt_template,search_not_to_be_found,
                         'ShirtshouldnotbefoundsearchingM')

        search_attribute=self.env['product.template'].search(
            [('attribute_line_ids','=','Size')]
        )
        self.assertIn(self.product_shirt_template,search_attribute,
                      'ShirtshouldbefoundsearchingSize')

        search_value=self.env['product.template'].search(
            [('attribute_line_ids','=','L')]
        )
        self.assertIn(self.product_shirt_template,search_value,
                      'ShirtshouldbefoundsearchingL')

    deftest_name_search(self):
        self.product_slip_template=self.env['product.template'].create({
            'name':'Slip',
        })
        res=self.env['product.product'].name_search('Shirt',[],'notilike',None)
        res_ids=[r[0]forrinres]
        self.assertIn(self.product_slip_template.product_variant_ids.id,res_ids,
                      'Slipshouldbefoundsearching\'notilike\'')


classTestVariants(common.TestProductCommon):

    defsetUp(self):
        res=super(TestVariants,self).setUp()
        self.size_attr=self.env['product.attribute'].create({'name':'Size'})
        self.size_attr_value_s=self.env['product.attribute.value'].create({'name':'S','attribute_id':self.size_attr.id})
        self.size_attr_value_m=self.env['product.attribute.value'].create({'name':'M','attribute_id':self.size_attr.id})
        self.size_attr_value_l=self.env['product.attribute.value'].create({'name':'L','attribute_id':self.size_attr.id})
        returnres

    deftest_variants_is_product_variant(self):
        template=self.product_7_template
        variants=template.product_variant_ids
        self.assertFalse(template.is_product_variant,
                         'Producttemplateisnotavariant')
        self.assertEqual({True},set(v.is_product_variantforvinvariants),
                         'Productvariantsarevariants')

    deftest_variants_creation_mono(self):
        test_template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(4,self.size_attr_value_s.id)],
            })]
        })

        #producedvariants:onevariant,becausemonovalue
        self.assertEqual(len(test_template.product_variant_ids),1)
        self.assertEqual(test_template.product_variant_ids.product_template_attribute_value_ids.product_attribute_value_id,self.size_attr_value_s)

    deftest_variants_creation_mono_double(self):
        test_template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.prod_att_1.id,
                'value_ids':[(4,self.prod_attr1_v2.id)],
            }),(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(4,self.size_attr_value_s.id)],
            })]
        })

        #producedvariants:onevariant,becauseonly1combinationispossible
        self.assertEqual(len(test_template.product_variant_ids),1)
        self.assertEqual(test_template.product_variant_ids.product_template_attribute_value_ids.product_attribute_value_id,self.size_attr_value_s+self.prod_attr1_v2)

    deftest_variants_creation_mono_multi(self):
        test_template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.prod_att_1.id,
                'value_ids':[(4,self.prod_attr1_v2.id)],
            }),(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(4,self.size_attr_value_s.id),(4,self.size_attr_value_m.id)],
            })]
        })
        sofa_attr1_v2=test_template.attribute_line_ids[0].product_template_value_ids[0]
        sofa_size_s=test_template.attribute_line_ids[1].product_template_value_ids[0]
        sofa_size_m=test_template.attribute_line_ids[1].product_template_value_ids[1]

        #producedvariants:twovariants,simplematrix
        self.assertEqual(len(test_template.product_variant_ids),2)
        forptavinsofa_size_s+sofa_size_m:
            products=self.env['product.product'].search([
                ('product_tmpl_id','=',test_template.id),
                ('product_template_attribute_value_ids','in',ptav.id),
                ('product_template_attribute_value_ids','in',sofa_attr1_v2.id)
            ])
            self.assertEqual(len(products),1)

    deftest_variants_creation_matrix(self):
        test_template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.prod_att_1.id,
                'value_ids':[(4,self.prod_attr1_v1.id),(4,self.prod_attr1_v2.id)],
            }),(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(4,self.size_attr_value_s.id),(4,self.size_attr_value_m.id),(4,self.size_attr_value_l.id)],
            })]
        })

        sofa_attr1_v1=test_template.attribute_line_ids[0].product_template_value_ids[0]
        sofa_attr1_v2=test_template.attribute_line_ids[0].product_template_value_ids[1]
        sofa_size_s=test_template.attribute_line_ids[1].product_template_value_ids[0]
        sofa_size_m=test_template.attribute_line_ids[1].product_template_value_ids[1]
        sofa_size_l=test_template.attribute_line_ids[1].product_template_value_ids[2]

        #producedvariants:valuematrix:2x3values
        self.assertEqual(len(test_template.product_variant_ids),6)
        forvalue_1insofa_attr1_v1+sofa_attr1_v2:
            forvalue_2insofa_size_s+sofa_size_m+sofa_size_l:
                products=self.env['product.product'].search([
                    ('product_tmpl_id','=',test_template.id),
                    ('product_template_attribute_value_ids','in',value_1.id),
                    ('product_template_attribute_value_ids','in',value_2.id)
                ])
                self.assertEqual(len(products),1)

    deftest_variants_creation_multi_update(self):
        test_template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.prod_att_1.id,
                'value_ids':[(4,self.prod_attr1_v1.id),(4,self.prod_attr1_v2.id)],
            }),(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(4,self.size_attr_value_s.id),(4,self.size_attr_value_m.id)],
            })]
        })
        size_attribute_line=test_template.attribute_line_ids.filtered(lambdaline:line.attribute_id==self.size_attr)
        test_template.write({
            'attribute_line_ids':[(1,size_attribute_line.id,{
                'value_ids':[(4,self.size_attr_value_l.id)],
            })]
        })

    deftest_variants_copy(self):
        template=self.env['product.template'].create({
            'name':'TestCopy',
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size_attr.id,
                'value_ids':[(4,self.size_attr_value_s.id),(4,self.size_attr_value_m.id)],
            })]
        })
        self.assertEqual(len(template.product_variant_ids),2)
        self.assertEqual(template.name,'TestCopy')

        #testcopyoftemplate
        template_copy=template.copy()
        self.assertEqual(template.name,'TestCopy')
        self.assertEqual(template_copy.name,'TestCopy(copy)')
        self.assertEqual(len(template_copy.product_variant_ids),2)

        #testcopyofvariant(actuallyjustcopyingtemplate)
        variant_copy=template_copy.product_variant_ids[0].copy()
        self.assertEqual(template.name,'TestCopy')
        self.assertEqual(template_copy.name,'TestCopy(copy)')
        self.assertEqual(variant_copy.name,'TestCopy(copy)(copy)')
        self.assertEqual(len(variant_copy.product_variant_ids),2)

    deftest_dynamic_variants_copy(self):
        self.color_attr=self.env['product.attribute'].create({'name':'Color','create_variant':'dynamic'})
        self.color_attr_value_r=self.env['product.attribute.value'].create({'name':'Red','attribute_id':self.color_attr.id})
        self.color_attr_value_b=self.env['product.attribute.value'].create({'name':'Blue','attribute_id':self.color_attr.id})

        #testcopyofvariantwithdynamicattribute
        template_dyn=self.env['product.template'].create({
            'name':'TestDynamical',
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.color_attr.id,
                'value_ids':[(4,self.color_attr_value_r.id),(4,self.color_attr_value_b.id)],
            })]
        })

        self.assertEqual(len(template_dyn.product_variant_ids),0)
        self.assertEqual(template_dyn.name,'TestDynamical')

        variant_dyn=template_dyn._create_product_variant(template_dyn._get_first_possible_combination())
        self.assertEqual(len(template_dyn.product_variant_ids),1)

        variant_dyn_copy=variant_dyn.copy()
        template_dyn_copy=variant_dyn_copy.product_tmpl_id
        self.assertEqual(len(template_dyn_copy.product_variant_ids),1)
        self.assertEqual(template_dyn_copy.name,'TestDynamical(copy)')

    deftest_standard_price(self):
        """Ensuretemplatevaluesarecorrectly(re)computeddependingonthecontext"""
        one_variant_product=self.product_1
        self.assertEqual(one_variant_product.product_variant_count,1)

        company_a=self.env.company
        company_b=self.env['res.company'].create({'name':'CB','currency_id':self.env.ref('base.VEF').id})

        self.assertEqual(one_variant_product.cost_currency_id,company_a.currency_id)
        self.assertEqual(one_variant_product.with_company(company_b).cost_currency_id,company_b.currency_id)

        one_variant_template=one_variant_product.product_tmpl_id
        self.assertEqual(one_variant_product.standard_price,one_variant_template.standard_price)
        one_variant_product.with_company(company_b).standard_price=500.0
        self.assertEqual(
            one_variant_product.with_company(company_b).standard_price,
            one_variant_template.with_company(company_b).standard_price
        )
        self.assertEqual(
            500.0,
            one_variant_template.with_company(company_b).standard_price
        )

    deftest_archive_variant(self):
        template=self.env['product.template'].create({
            'name':'template'
        })
        self.assertEqual(len(template.product_variant_ids),1)

        template.write({
            'attribute_line_ids':[(0,False,{
                'attribute_id':self.size_attr.id,
                'value_ids':[
                    (4,self.size_attr.value_ids[0].id,self.size_attr_value_s),
                    (4,self.size_attr.value_ids[1].id,self.size_attr_value_m)
                ],
            })]
        })
        self.assertEqual(len(template.product_variant_ids),2)
        variant_1=template.product_variant_ids[0]
        variant_1.toggle_active()
        self.assertFalse(variant_1.active)
        self.assertEqual(len(template.product_variant_ids),1)
        self.assertEqual(len(template.with_context(
            active_test=False).product_variant_ids),2)
        variant_1.toggle_active()
        self.assertTrue(variant_1.active)
        self.assertTrue(template.active)

    deftest_template_barcode(self):
        template=self.env['product.template'].create({
            'name':'template',
            'barcode':'test',
        })
        self.assertEqual(len(template.product_variant_ids),1)
        self.assertEqual(template.barcode,'test')

        template.product_variant_ids.action_archive()
        self.assertFalse(template.active)
        template.invalidate_cache(['barcode'])
        self.assertEqual(template.barcode,'test')
        template.product_variant_ids.action_unarchive()
        template.action_unarchive()

        template.write({
            'attribute_line_ids':[(0,False,{
                'attribute_id':self.size_attr.id,
                'value_ids':[
                    (4,self.size_attr.value_ids[0].id,self.size_attr_value_s),
                    (4,self.size_attr.value_ids[1].id,self.size_attr_value_m)
                ],
            })]
        })
        self.assertFalse(template.barcode) #2activevariants-->nobarcodeontemplate

        variant_1=template.product_variant_ids[0]
        variant_2=template.product_variant_ids[1]

        variant_1.barcode='v1_barcode'
        variant_2.barcode='v2_barcode'

        variant_1.action_archive()
        template.invalidate_cache(['barcode'])
        self.assertEqual(template.barcode,variant_2.barcode) #1activevariant-->barcodeontemplate

        variant_1.action_unarchive()
        template.invalidate_cache(['barcode'])
        self.assertFalse(template.barcode) #2activevariants-->nobarcodeontemplate

    deftest_archive_all_variants(self):
        template=self.env['product.template'].create({
            'name':'template'
        })
        self.assertEqual(len(template.product_variant_ids),1)

        template.write({
            'attribute_line_ids':[(0,False,{
                'attribute_id':self.size_attr.id,
                'value_ids':[
                    (4,self.size_attr.value_ids[0].id,self.size_attr_value_s),
                    (4,self.size_attr.value_ids[1].id,self.size_attr_value_m)
                ],
            })]
        })
        self.assertEqual(len(template.product_variant_ids),2)
        variant_1=template.product_variant_ids[0]
        variant_2=template.product_variant_ids[1]
        template.product_variant_ids.toggle_active()
        self.assertFalse(variant_1.active,'Shouldarchiveallvariants')
        self.assertFalse(template.active,'Shouldarchiverelatedtemplate')
        variant_1.toggle_active()
        self.assertTrue(variant_1.active,'Shouldactivatevariant')
        self.assertFalse(variant_2.active,'Shouldnotre-activateothervariant')
        self.assertTrue(template.active,'Shouldre-activatetemplate')

classTestVariantsNoCreate(common.TestProductCommon):

    defsetUp(self):
        super(TestVariantsNoCreate,self).setUp()
        self.size=self.env['product.attribute'].create({
            'name':'Size',
            'create_variant':'no_variant',
            'value_ids':[(0,0,{'name':'S'}),(0,0,{'name':'M'}),(0,0,{'name':'L'})],
        })
        self.size_S=self.size.value_ids[0]
        self.size_M=self.size.value_ids[1]
        self.size_L=self.size.value_ids[2]

    deftest_create_mono(self):
        """createaproductwitha'nocreate'attributewithasinglevalue"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size.id,
                'value_ids':[(4,self.size_S.id)],
            })],
        })
        self.assertEqual(len(template.product_variant_ids),1)
        self.assertFalse(template.product_variant_ids.product_template_attribute_value_ids)

    deftest_update_mono(self):
        """modifyaproductwitha'nocreate'attributewithasinglevalue"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
        })
        self.assertEqual(len(template.product_variant_ids),1)

        template.write({
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size.id,
                'value_ids':[(4,self.size_S.id)],
            })],
        })
        self.assertEqual(len(template.product_variant_ids),1)
        self.assertFalse(template.product_variant_ids.product_template_attribute_value_ids)

    deftest_create_multi(self):
        """createaproductwitha'nocreate'attributewithseveralvalues"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size.id,
                'value_ids':[(6,0,self.size.value_ids.ids)],
            })],
        })
        self.assertEqual(len(template.product_variant_ids),1)
        self.assertFalse(template.product_variant_ids.product_template_attribute_value_ids)

    deftest_update_multi(self):
        """modifyaproductwitha'nocreate'attributewithseveralvalues"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
        })
        self.assertEqual(len(template.product_variant_ids),1)

        template.write({
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.size.id,
                'value_ids':[(6,0,self.size.value_ids.ids)],
            })],
        })
        self.assertEqual(len(template.product_variant_ids),1)
        self.assertFalse(template.product_variant_ids.product_template_attribute_value_ids)

    deftest_create_mixed_mono(self):
        """createaproductwithregularand'nocreate'attributes"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[
                (0,0,{#novariantsforthisone
                    'attribute_id':self.size.id,
                    'value_ids':[(4,self.size_S.id)],
                }),
                (0,0,{#twovariantsforthisone
                    'attribute_id':self.prod_att_1.id,
                    'value_ids':[(4,self.prod_attr1_v1.id),(4,self.prod_attr1_v2.id)],
                }),
            ],
        })
        self.assertEqual(len(template.product_variant_ids),2)
        self.assertEqual(
            {variant.product_template_attribute_value_ids.product_attribute_value_idforvariantintemplate.product_variant_ids},
            {self.prod_attr1_v1,self.prod_attr1_v2},
        )

    deftest_update_mixed_mono(self):
        """modifyaproductwithregularand'nocreate'attributes"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
        })
        self.assertEqual(len(template.product_variant_ids),1)

        template.write({
            'attribute_line_ids':[
                (0,0,{#novariantsforthisone
                    'attribute_id':self.size.id,
                    'value_ids':[(4,self.size_S.id)],
                }),
                (0,0,{#twovariantsforthisone
                    'attribute_id':self.prod_att_1.id,
                    'value_ids':[(4,self.prod_attr1_v1.id),(4,self.prod_attr1_v2.id)],
                }),
            ],
        })
        self.assertEqual(len(template.product_variant_ids),2)
        self.assertEqual(
            {variant.product_template_attribute_value_ids.product_attribute_value_idforvariantintemplate.product_variant_ids},
            {self.prod_attr1_v1,self.prod_attr1_v2},
        )

    deftest_create_mixed_multi(self):
        """createaproductwithregularand'nocreate'attributes"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[
                (0,0,{#novariantsforthisone
                    'attribute_id':self.size.id,
                    'value_ids':[(6,0,self.size.value_ids.ids)],
                }),
                (0,0,{#twovariantsforthisone
                    'attribute_id':self.prod_att_1.id,
                    'value_ids':[(4,self.prod_attr1_v1.id),(4,self.prod_attr1_v2.id)],
                }),
            ],
        })
        self.assertEqual(len(template.product_variant_ids),2)
        self.assertEqual(
            {variant.product_template_attribute_value_ids.product_attribute_value_idforvariantintemplate.product_variant_ids},
            {self.prod_attr1_v1,self.prod_attr1_v2},
        )

    deftest_update_mixed_multi(self):
        """modifyaproductwithregularand'nocreate'attributes"""
        template=self.env['product.template'].create({
            'name':'Sofa',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
        })
        self.assertEqual(len(template.product_variant_ids),1)

        template.write({
            'attribute_line_ids':[
                (0,0,{#novariantsforthisone
                    'attribute_id':self.size.id,
                    'value_ids':[(6,0,self.size.value_ids.ids)],
                }),
                (0,0,{#twovariantsforthisone
                    'attribute_id':self.prod_att_1.id,
                    'value_ids':[(4,self.prod_attr1_v1.id),(4,self.prod_attr1_v2.id)],
                }),
            ],
        })
        self.assertEqual(len(template.product_variant_ids),2)
        self.assertEqual(
            {variant.product_template_attribute_value_ids.product_attribute_value_idforvariantintemplate.product_variant_ids},
            {self.prod_attr1_v1,self.prod_attr1_v2},
        )

    deftest_update_variant_with_nocreate(self):
        """updatevariantswitha'nocreate'valueonvariant"""
        template=self.env['product.template'].create({
            'name':'Sofax',
            'uom_id':self.uom_unit.id,
            'uom_po_id':self.uom_unit.id,
            'attribute_line_ids':[
                (0,0,{#onevariantforthisone
                    'attribute_id':self.prod_att_1.id,
                    'value_ids':[(6,0,self.prod_attr1_v1.ids)],
                }),
            ],
        })
        self.assertEqual(len(template.product_variant_ids),1)
        template.attribute_line_ids=[(0,0,{
            'attribute_id':self.size.id,
            'value_ids':[(6,0,self.size_S.ids)],
        })]
        self.assertEqual(len(template.product_variant_ids),1)
        #no_variantattributeshouldnotappearonthevariant
        self.assertNotIn(self.size_S,template.product_variant_ids.product_template_attribute_value_ids.product_attribute_value_id)


classTestVariantsManyAttributes(common.TestAttributesCommon):

    deftest_01_create_no_variant(self):
        toto=self.env['product.template'].create({
            'name':'Toto',
            'attribute_line_ids':[(0,0,{
                'attribute_id':attribute.id,
                'value_ids':[(6,0,attribute.value_ids.ids)],
            })forattributeinself.attributes],
        })
        self.assertEqual(len(toto.attribute_line_ids.mapped('attribute_id')),10)
        self.assertEqual(len(toto.attribute_line_ids.mapped('value_ids')),100)
        self.assertEqual(len(toto.product_variant_ids),1)

    deftest_02_create_dynamic(self):
        self.attributes.write({'create_variant':'dynamic'})
        toto=self.env['product.template'].create({
            'name':'Toto',
            'attribute_line_ids':[(0,0,{
                'attribute_id':attribute.id,
                'value_ids':[(6,0,attribute.value_ids.ids)],
            })forattributeinself.attributes],
        })
        self.assertEqual(len(toto.attribute_line_ids.mapped('attribute_id')),10)
        self.assertEqual(len(toto.attribute_line_ids.mapped('value_ids')),100)
        self.assertEqual(len(toto.product_variant_ids),0)

    deftest_03_create_always(self):
        self.attributes.write({'create_variant':'always'})
        withself.assertRaises(UserError):
            self.env['product.template'].create({
                'name':'Toto',
                'attribute_line_ids':[(0,0,{
                    'attribute_id':attribute.id,
                    'value_ids':[(6,0,attribute.value_ids.ids)],
                })forattributeinself.attributes],
            })

    deftest_04_create_no_variant_dynamic(self):
        self.attributes[:5].write({'create_variant':'dynamic'})
        toto=self.env['product.template'].create({
            'name':'Toto',
            'attribute_line_ids':[(0,0,{
                'attribute_id':attribute.id,
                'value_ids':[(6,0,attribute.value_ids.ids)],
            })forattributeinself.attributes],
        })
        self.assertEqual(len(toto.attribute_line_ids.mapped('attribute_id')),10)
        self.assertEqual(len(toto.attribute_line_ids.mapped('value_ids')),100)
        self.assertEqual(len(toto.product_variant_ids),0)

    deftest_05_create_no_variant_always(self):
        self.attributes[:2].write({'create_variant':'always'})
        toto=self.env['product.template'].create({
            'name':'Toto',
            'attribute_line_ids':[(0,0,{
                'attribute_id':attribute.id,
                'value_ids':[(6,0,attribute.value_ids.ids)],
            })forattributeinself.attributes],
        })
        self.assertEqual(len(toto.attribute_line_ids.mapped('attribute_id')),10)
        self.assertEqual(len(toto.attribute_line_ids.mapped('value_ids')),100)
        self.assertEqual(len(toto.product_variant_ids),100)

    deftest_06_create_dynamic_always(self):
        self.attributes[:5].write({'create_variant':'dynamic'})
        self.attributes[5:].write({'create_variant':'always'})
        toto=self.env['product.template'].create({
            'name':'Toto',
            'attribute_line_ids':[(0,0,{
                'attribute_id':attribute.id,
                'value_ids':[(6,0,attribute.value_ids.ids)],
            })forattributeinself.attributes],
        })
        self.assertEqual(len(toto.attribute_line_ids.mapped('attribute_id')),10)
        self.assertEqual(len(toto.attribute_line_ids.mapped('value_ids')),100)
        self.assertEqual(len(toto.product_variant_ids),0)

    deftest_07_create_no_create_dynamic_always(self):
        self.attributes[3:6].write({'create_variant':'dynamic'})
        self.attributes[6:].write({'create_variant':'always'})
        toto=self.env['product.template'].create({
            'name':'Toto',
            'attribute_line_ids':[(0,0,{
                'attribute_id':attribute.id,
                'value_ids':[(6,0,attribute.value_ids.ids)],
            })forattributeinself.attributes],
        })
        self.assertEqual(len(toto.attribute_line_ids.mapped('attribute_id')),10)
        self.assertEqual(len(toto.attribute_line_ids.mapped('value_ids')),100)
        self.assertEqual(len(toto.product_variant_ids),0)


classTestVariantsImages(common.TestProductCommon):

    defsetUp(self):
        res=super(TestVariantsImages,self).setUp()

        self.colors=OrderedDict([('none',''),('red','#FF0000'),('green','#00FF00'),('blue','#0000FF')])
        self.images={}

        product_attribute=self.env['product.attribute'].create({'name':'Color'})

        self.template=self.env['product.template'].create({
            'name':'template',
        })

        color_values=self.env['product.attribute.value'].create([{
            'name':color,
            'attribute_id':product_attribute.id,
            'sequence':i,
        }fori,colorinenumerate(self.colors)])

        ptal=self.env['product.template.attribute.line'].create({
            'attribute_id':product_attribute.id,
            'product_tmpl_id':self.template.id,
            'value_ids':[(6,0,color_values.ids)],
        })

        forcolor_valueinptal.product_template_value_ids[1:]:
            f=io.BytesIO()
            Image.new('RGB',(800,500),self.colors[color_value.name]).save(f,'PNG')
            f.seek(0)
            self.images.update({color_value.name:base64.b64encode(f.read())})

            self.template._get_variant_for_combination(color_value).write({
                'image_variant_1920':self.images[color_value.name],
            })
        #thefirstonehasnoimage
        self.variants=self.template.product_variant_ids

        returnres

    deftest_variant_images(self):
        """Checkthatonvariant,theimageusedistheimage_variant_1920ifset,
        anddefaultstothetemplateimageotherwise.
        """
        #PretendsetuphappenedinanoldertransactionbyupdatingontheSQLlayerandmakingsureitgetsreloaded
        #Using_write()insteadofwrite()becausewrite()onlyallowsupdatinglogaccessfieldsatboottime
        before=datetime.now()-timedelta(hours=1)
        self.template._write({
            'create_date':before,
            'write_date':before,
        })
        self.variants._write({
            'create_date':before,
            'write_date':before,
        })
        self.template.invalidate_cache(['create_date','write_date'],self.template.ids)
        self.variants.invalidate_cache(['create_date','write_date'],self.variants.ids)

        f=io.BytesIO()
        Image.new('RGB',(800,500),'#000000').save(f,'PNG')
        f.seek(0)
        image_black=base64.b64encode(f.read())

        images=self.variants.mapped('image_1920')
        self.assertEqual(len(set(images)),4)

        variant_no_image=self.variants[0]
        old_last_update=variant_no_image['__last_update']
        self.assertFalse(variant_no_image.image_1920)
        self.template.image_1920=image_black
        self.template.write({'write_date':datetime.now()})
        new_last_update=variant_no_image['__last_update']

        #thefirsthasnoimagevariant,alltheothersdo
        self.assertFalse(variant_no_image.image_variant_1920)
        self.assertTrue(all(images[1:]))

        #templateimageisthesameasthisone,sinceithasnoimagevariant
        self.assertEqual(variant_no_image.image_1920,self.template.image_1920)
        #havingchangedthetemplateimageshouldnothavechangedthese
        self.assertEqual(images[1:],self.variants.mapped('image_1920')[1:])

        #lastupdatechangedforthevariantwithoutimage
        self.assertLess(old_last_update,new_last_update)

    deftest_update_images_with_archived_variants(self):
        """Updateimagesaftervariantshavebeenarchived"""
        self.variants[1:].write({'active':False})
        self.variants[0].image_1920=self.images['red']
        self.assertEqual(self.template.image_1920,self.images['red'])
        self.assertEqual(self.variants[0].image_variant_1920,False)
        self.assertEqual(self.variants[0].image_1920,self.images['red'])


classTestVariantsArchive(common.TestProductCommon):
    """Onceavariantisusedonorders/invoices,etc,theycan'tbeunlinked.
       Asaresult,updatingattributesonaproducttemplatewouldsimply
       archivethevariantsinstead.Wemakesurethatateachupdate,wehave
       thecorrectactiveandinactiverecords.

       Inthesetests,weusethecommandssentbytheJSframeworktotheORM
       whenusingtheinterface.
    """
    defsetUp(self):
        res=super(TestVariantsArchive,self).setUp()

        self.pa_color=self.env['product.attribute'].create({'name':"color",'sequence':1})
        color_values=self.env['product.attribute.value'].create([{
            'name':n,
            'sequence':i,
            'attribute_id':self.pa_color.id,
        }fori,ninenumerate(['white','black'])])
        self.pav_color_white=color_values[0]
        self.pav_color_black=color_values[1]

        self.pa_size=self.env['product.attribute'].create({'name':"size",'sequence':2})
        size_values=self.env['product.attribute.value'].create([{
            'name':n,
            'sequence':i,
            'attribute_id':self.pa_size.id,
        }fori,ninenumerate(['s','m'])])
        self.pav_size_s=size_values[0]
        self.pav_size_m=size_values[1]

        self.template=self.env['product.template'].create({
            'name':'consumeproduct',
            'attribute_line_ids':self._get_add_all_attributes_command(),
        })
        self._update_color_vars(self.template.attribute_line_ids[0])
        self._update_size_vars(self.template.attribute_line_ids[1])
        returnres

    deftest_01_update_variant_unlink(self):
        """Variantsarenotusedanywhere,soremovinganattributelinewould
           unlinkthevariantsandcreatenewones.Nothingtoofancyhere.
        """
        variants_2x2=self.template.product_variant_ids
        self._assert_2color_x_2size()

        #Removethesizeline,correspondingvariantswillberemovedtoosince
        #theyareusednowhere.Sinceweonlykeptcolor,weshouldhaveasmany
        #variantsasithasvalues.
        self._remove_ptal_size()
        self._assert_2color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        #Were-addthelinewejustremoved,soweshouldgetnewvariants.
        self._add_ptal_size_s_m()
        self._assert_2color_x_2size()
        self.assertFalse(self.template.product_variant_ids&variants_2x2)

    deftest_02_update_variant_archive_1_value(self):
        """Wedothesameoperationsonthetemplateasintheprevioustest,
           exceptwesimulatethatthevariantscan'tbeunlinked.

           Itfollowsthatvariantsshouldbearchivedinstead,sotheresults
           shouldallbedifferentfromprevioustest.

           Inthistestwehavealinethathasonlyonepossiblevalue:
           thisishandleddifferentlythanthecasewherewehavemorethan
           onevalue,sinceitdoesnotaddnewvariants.
        """
        self._remove_ptal_size()
        self._add_ptal_size_s()

        #createapatchtomakeasifonevariantwasundeletable
        #(e.g.presentinafieldwithondelete=restrict)
        Product=self.env['product.product']

        defunlink(self):
            raiseException('just')
        Product._patch_method('unlink',unlink)

        variants_2x1=self.template.product_variant_ids
        self._assert_2color_x_1size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        #Removethesizeline,whichistheonewithonlyonepossiblevalue.
        #Variantsshouldbekept,justthesinglevalueremovedfromthem.
        self._remove_ptal_size()
        self.assertEqual(variants_2x1,self.template.product_variant_ids)
        self._assert_2color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        #Addthelinejustremoved,soitisaddedbacktothevariants.
        self._add_ptal_size_s()
        self.assertEqual(variants_2x1,self.template.product_variant_ids)
        self._assert_2color_x_1size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        Product._revert_method('unlink')

    deftest_02_update_variant_archive_2_value(self):
        """Wedothesameoperationsonthetemplateasintheprevioustests,
           exceptwesimulatethatthevariantscan'tbeunlinked.

           Itfollowsthatvariantsshouldbearchivedinstead,sotheresults
           shouldallbedifferentfromprevioustest.
        """
        Product=self.env['product.product']

        defunlink(slef):
            raiseException('just')
        Product._patch_method('unlink',unlink)

        variants_2x2=self.template.product_variant_ids
        self._assert_2color_x_2size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        #CASEremoveoneattributeline(goingfrom2*2to2*1)
        #Sincetheycan'tbeunlinked,existingvariantsshouldbearchived.
        self._remove_ptal_size()
        variants_2x0=self.template.product_variant_ids
        self._assert_2color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x2)
        self._assert_2color_x_2size(archived_variants)

        #Addthelinejustremoved,sogetbackthepreviousvariants.
        #Sincetheycan'tbeunlinked,existingvariantsshouldbearchived.
        self._add_ptal_size_s_m()
        self.assertEqual(self.template.product_variant_ids,variants_2x2)
        self._assert_2color_x_2size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x0)
        self._assert_2color_x_0size(archived_variants)

        #weredothewholeremove/readtocheck
        self._remove_ptal_size()
        self.assertEqual(self.template.product_variant_ids,variants_2x0)
        self._assert_2color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x2)
        self._assert_2color_x_2size(archived_variants)

        self._add_ptal_size_s_m()
        self.assertEqual(self.template.product_variant_ids,variants_2x2)
        self._assert_2color_x_2size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x0)
        self._assert_2color_x_0size(archived_variants)

        self._remove_ptal_size()
        self.assertEqual(self.template.product_variant_ids,variants_2x0)
        self._assert_2color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x2)
        self._assert_2color_x_2size(archived_variants)

        #Thistimeweonlyaddoneofthetwoattributeswe'vebeenremoving.
        #Thisisasinglevalueline,sothevalueissimplyaddedtoexisting
        #variants.
        self._add_ptal_size_s()
        self.assertEqual(self.template.product_variant_ids,variants_2x0)
        self._assert_2color_x_1size()
        self.assertEqual(archived_variants,variants_2x2)
        self._assert_2color_x_2size(archived_variants)

        Product._revert_method('unlink')

    deftest_03_update_variant_archive_3_value(self):
        self._remove_ptal_size()
        self._add_ptal_size_s()

        Product=self.env['product.product']

        defunlink(slef):
            raiseException('just')
        Product._patch_method('unlink',unlink)

        self._assert_2color_x_1size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)
        variants_2x1=self.template.product_variant_ids

        #CASE:removesinglevalueline,novariantchange
        self._remove_ptal_size()
        self.assertEqual(self.template.product_variant_ids,variants_2x1)
        self._assert_2color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        #CASE:emptycombination,thisgeneratesanewvariant
        self.template.write({'attribute_line_ids':[(2,self.ptal_color.id)]})
        self._assert_0color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x1)
        self._assert_2color_x_0size(archived_variants) #singlevalueareremoved
        variant_0x0=self.template.product_variant_ids

        #CASE:addsinglevalueonempty
        self._add_ptal_size_s()
        self.assertEqual(self.template.product_variant_ids,variant_0x0)
        self._assert_0color_x_1size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x1)
        self._assert_2color_x_0size(archived_variants) #singlevalueareremoved

        #CASE:emptyagain
        self._remove_ptal_size()
        self.assertEqual(self.template.product_variant_ids,variant_0x0)
        self._assert_0color_x_0size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x1)
        self._assert_2color_x_0size(archived_variants) #singlevalueareremoved

        #CASE:re-addeverything
        self.template.write({
            'attribute_line_ids':self._get_add_all_attributes_command(),
        })
        self._update_color_vars(self.template.attribute_line_ids[0])
        self._update_size_vars(self.template.attribute_line_ids[1])
        self._assert_2color_x_2size()
        archived_variants=self._get_archived_variants()
        self.assertEqual(archived_variants,variants_2x1+variant_0x0)

        Product._revert_method('unlink')

    deftest_04_from_to_single_values(self):
        Product=self.env['product.product']

        defunlink(slef):
            raiseException('just')
        Product._patch_method('unlink',unlink)

        #CASE:removeonevalue,linebecomingsinglevalue
        variants_2x2=self.template.product_variant_ids
        self.ptal_size.write({'value_ids':[(3,self.pav_size_m.id)]})
        self._assert_2color_x_1size()
        self.assertEqual(self.template.product_variant_ids,variants_2x2[0]+variants_2x2[2])
        archived_variants=self._get_archived_variants()
        self._assert_2color_x_1size(archived_variants,ptav=self.ptav_size_m)
        self.assertEqual(archived_variants,variants_2x2[1]+variants_2x2[3])

        #CASE:addbackthevalue
        self.ptal_size.write({'value_ids':[(4,self.pav_size_m.id)]})
        self._assert_2color_x_2size()
        self.assertEqual(self.template.product_variant_ids,variants_2x2)
        archived_variants=self._get_archived_variants()
        self.assertFalse(archived_variants)

        #CASE:removeonevalue,linebecomingsinglevalue,andthenremove
        #theremainingvalue
        self.ptal_size.write({'value_ids':[(3,self.pav_size_m.id)]})
        self._remove_ptal_size()
        self._assert_2color_x_0size()
        self.assertFalse(self.template.product_variant_ids&variants_2x2)
        archived_variants=self._get_archived_variants()
        self._assert_2color_x_2size(archived_variants)
        self.assertEqual(archived_variants,variants_2x2)
        variants_2x0=self.template.product_variant_ids

        #CASE:addbackthevalues
        self._add_ptal_size_s_m()
        self._assert_2color_x_2size()
        self.assertEqual(self.template.product_variant_ids,variants_2x2)
        archived_variants=self._get_archived_variants()
        self._assert_2color_x_0size(archived_variants)
        self.assertEqual(archived_variants,variants_2x0)

        Product._revert_method('unlink')

    deftest_name_search_dynamic_attributes(self):
        dynamic_attr=self.env['product.attribute'].create({
            'name':'Dynamic',
            'create_variant':'dynamic',
            'value_ids':[(0,False,{'name':'ValueDynamic'})],
        })
        template=self.env['product.template'].create({
            'name':'cimanyd',
            'attribute_line_ids':[(0,False,{
                'attribute_id':dynamic_attr.id,
                'value_ids':[(4,dynamic_attr.value_ids[0].id,False)],
            })]
        })
        self.assertEqual(len(template.product_variant_ids),0)

        name_searched=self.env['product.template'].name_search(name='cima')
        self.assertIn(template.id,[ng[0]fornginname_searched])

    deftest_uom_update_variant(self):
        """Changingtheuomonthetemplatedonotbehavethesame
        aschangingontheproductproduct."""
        units=self.env.ref('uom.product_uom_unit')
        cm=self.env.ref('uom.product_uom_cm')
        template=self.env['product.template'].create({
            'name':'kardon'
        })

        template_form=Form(template)
        template_form.uom_id=cm
        self.assertEqual(template_form.uom_po_id,cm)
        template=template_form.save()

        variant_form=Form(template.product_variant_ids)
        variant_form.uom_id=units
        self.assertEqual(variant_form.uom_po_id,units)
        variant=variant_form.save()
        self.assertEqual(variant.uom_po_id,units)
        self.assertEqual(template.uom_po_id,units)

    deftest_dynamic_attributes_archiving(self):
        Product=self.env['product.product']
        ProductAttribute=self.env['product.attribute']
        ProductAttributeValue=self.env['product.attribute.value']

        #Patchunlinkmethodtoforcearchivinginsteaddeleting
        defunlink(self):
            self.active=False
        Product._patch_method('unlink',unlink)

        #Creatingattributes
        pa_color=ProductAttribute.create({'sequence':1,'name':'color','create_variant':'dynamic'})
        color_values=ProductAttributeValue.create([{
            'name':n,
            'sequence':i,
            'attribute_id':pa_color.id,
        }fori,ninenumerate(['white','black'])])
        pav_color_white=color_values[0]
        pav_color_black=color_values[1]

        pa_size=ProductAttribute.create({'sequence':2,'name':'size','create_variant':'dynamic'})
        size_values=ProductAttributeValue.create([{
            'name':n,
            'sequence':i,
            'attribute_id':pa_size.id,
        }fori,ninenumerate(['s','m'])])
        pav_size_s=size_values[0]
        pav_size_m=size_values[1]

        pa_material=ProductAttribute.create({'sequence':3,'name':'material','create_variant':'no_variant'})
        material_values=ProductAttributeValue.create([{
            'name':'Wood',
            'sequence':1,
            'attribute_id':pa_material.id,
        }])
        pav_material_wood=material_values[0]

        #Defineatemplatewithonlycolorattribute&whitevalue
        template=self.env['product.template'].create({
            'name':'testproduct',
            'attribute_line_ids':[(0,0,{
                'attribute_id':pa_color.id,
                'value_ids':[(6,0,[pav_color_white.id])],
            })],
        })

        #Createavariant(becauseofdynamicattribute)
        ptav_white=self.env['product.template.attribute.value'].search([
            ('attribute_line_id','=',template.attribute_line_ids.id),
            ('product_attribute_value_id','=',pav_color_white.id)
        ])
        product_white=template._create_product_variant(ptav_white)

        #Addinganewvaluetoanexistingattributeshouldnotarchivethevariant
        template.write({
            'attribute_line_ids':[(1,template.attribute_line_ids[0].id,{
                'attribute_id':pa_color.id,
                'value_ids':[(4,pav_color_black.id,False)],
            })]
        })
        self.assertTrue(product_white.active)

        #Removinganattributevalueshouldarchivetheproductusingit
        template.write({
            'attribute_line_ids':[(1,template.attribute_line_ids[0].id,{
                'value_ids':[(3,pav_color_white.id,0)],
            })]
        })
        self.assertFalse(product_white.active)
        self.assertFalse(template._is_combination_possible_by_config(
            combination=product_white.product_template_attribute_value_ids,
            ignore_no_variant=True,
        ))

        #Creatingaproductwiththesameattributesfortestingduplicates
        product_white_duplicate=Product.create({
            'product_tmpl_id':template.id,
            'product_template_attribute_value_ids':[(6,0,[ptav_white.id])],
            'active':False,
        })
        #Resetarchivingforthenextassert
        template.write({
            'attribute_line_ids':[(1,template.attribute_line_ids[0].id,{
                'value_ids':[(4,pav_color_white.id,0)],
            })]
        })
        self.assertTrue(product_white.active)
        self.assertFalse(product_white_duplicate.active)

        #Addinganewattributeshouldarchivetheoldvariant
        template.write({
            'attribute_line_ids':[(0,0,{
                'attribute_id':pa_size.id,
                'value_ids':[(6,0,[pav_size_s.id,pav_size_m.id])],
            })]
        })
        self.assertFalse(product_white.active)

        #Resetarchivingforthenextassert
        template.write({
            'attribute_line_ids':[(3,template.attribute_line_ids[1].id,0)]
        })
        self.assertTrue(product_white.active)

        #Addingano_variantattributeshouldnotarchivetheproduct
        template.write({
            'attribute_line_ids':[(0,0,{
                'attribute_id':pa_material.id,
                'value_ids':[(6,0,[pav_material_wood.id])],
            })]
        })
        self.assertTrue(product_white.active)

        Product._revert_method('unlink')

    deftest_set_barcode(self):
        tmpl=self.product_0.product_tmpl_id
        tmpl.barcode='123'
        self.assertEqual(tmpl.barcode,'123')
        self.assertEqual(self.product_0.barcode,'123')

        tmpl.toggle_active()

        tmpl.barcode='456'
        tmpl.invalidate_cache(fnames=['barcode'],ids=tmpl.ids)
        self.assertEqual(tmpl.barcode,'456')
        self.assertEqual(self.product_0.barcode,'456')

    def_update_color_vars(self,ptal):
        self.ptal_color=ptal
        self.assertEqual(self.ptal_color.attribute_id,self.pa_color)
        self.ptav_color_white=self.ptal_color.product_template_value_ids[0]
        self.assertEqual(self.ptav_color_white.product_attribute_value_id,self.pav_color_white)
        self.ptav_color_black=self.ptal_color.product_template_value_ids[1]
        self.assertEqual(self.ptav_color_black.product_attribute_value_id,self.pav_color_black)

    def_update_size_vars(self,ptal):
        self.ptal_size=ptal
        self.assertEqual(self.ptal_size.attribute_id,self.pa_size)
        self.ptav_size_s=self.ptal_size.product_template_value_ids[0]
        self.assertEqual(self.ptav_size_s.product_attribute_value_id,self.pav_size_s)
        iflen(self.ptal_size.product_template_value_ids)>1:
            self.ptav_size_m=self.ptal_size.product_template_value_ids[1]
            self.assertEqual(self.ptav_size_m.product_attribute_value_id,self.pav_size_m)

    def_get_add_all_attributes_command(self):
        return[(0,0,{
            'attribute_id':pa.id,
            'value_ids':[(6,0,pa.value_ids.ids)],
        })forpainself.pa_color+self.pa_size]

    def_get_archived_variants(self):
        #Changecontexttoalsogetarchivedvalueswhenreadingthemfromthe
        #variants.
        returnself.env['product.product'].with_context(active_test=False).search([
            ('active','=',False),
            ('product_tmpl_id','=',self.template.id)
        ])

    def_remove_ptal_size(self):
        self.template.write({'attribute_line_ids':[(2,self.ptal_size.id)]})

    def_add_ptal_size_s_m(self):
        self.template.write({
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.pa_size.id,
                'value_ids':[(6,0,(self.pav_size_s+self.pav_size_m).ids)],
            })],
        })
        self._update_size_vars(self.template.attribute_line_ids[-1])

    def_add_ptal_size_s(self):
        self.template.write({
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.pa_size.id,
                'value_ids':[(6,0,self.pav_size_s.ids)],
            })],
        })
        self._update_size_vars(self.template.attribute_line_ids[-1])

    def_get_combinations_names(self,combinations):
        return'|'.join([','.join(c.mapped('name'))forcincombinations])

    def_assert_required_combinations(self,variants,required_values):
        actual_values=[v.product_template_attribute_value_idsforvinvariants]
        self.assertEqual(set(required_values),set(actual_values),
            "\nRequired:%s\nActual:  %s"%(self._get_combinations_names(required_values),self._get_combinations_names(actual_values)))

    def_assert_2color_x_2size(self,variants=None):
        """Assertthefullmatrix2colorx2size"""
        variants=variantsorself.template.product_variant_ids
        self.assertEqual(len(variants),4)
        self._assert_required_combinations(variants,required_values=[
            self.ptav_color_white+self.ptav_size_s,
            self.ptav_color_white+self.ptav_size_m,
            self.ptav_color_black+self.ptav_size_s,
            self.ptav_color_black+self.ptav_size_m,
        ])

    def_assert_2color_x_1size(self,variants=None,ptav=None):
        """Assertthematrix2colorx1size"""
        variants=variantsorself.template.product_variant_ids
        self.assertEqual(len(variants),2)
        self._assert_required_combinations(variants,required_values=[
            self.ptav_color_white+(ptavorself.ptav_size_s),
            self.ptav_color_black+(ptavorself.ptav_size_s),
        ])

    def_assert_2color_x_0size(self,variants=None):
        """Assertthematrix2colorxnosize"""
        variants=variantsorself.template.product_variant_ids
        self.assertEqual(len(variants),2)
        self._assert_required_combinations(variants,required_values=[
            self.ptav_color_white,
            self.ptav_color_black,
        ])

    def_assert_0color_x_1size(self,variants=None):
        """Assertthematrixnocolorx1size"""
        variants=variantsorself.template.product_variant_ids
        self.assertEqual(len(variants),1)
        self.assertEqual(variants[0].product_template_attribute_value_ids,self.ptav_size_s)

    def_assert_0color_x_0size(self,variants=None):
        """Assertthematrixnocolorxnosize"""
        variants=variantsorself.template.product_variant_ids
        self.assertEqual(len(variants),1)
        self.assertFalse(variants[0].product_template_attribute_value_ids)


classTestVariantWrite(TransactionCase):

    deftest_active_one2many(self):
        template=self.env['product.template'].create({'name':'Foo','description':'Foo'})
        self.assertEqual(len(template.product_variant_ids),1)

        #checktheconsistencyofone2manyfieldproduct_variant_idsw.r.t.activevariants
        variant1=template.product_variant_ids
        variant2=self.env['product.product'].create({'product_tmpl_id':template.id})
        self.assertEqual(template.product_variant_ids,variant1+variant2)

        variant2.active=False
        self.assertEqual(template.product_variant_ids,variant1)

        variant2.active=True
        self.assertEqual(template.product_variant_ids,variant1+variant2)

        variant1.active=False
        self.assertEqual(template.product_variant_ids,variant2)

    deftest_write_inherited_field(self):
        product=self.env['product.product'].create({'name':'Foo','description':'Foo'})
        self.assertEqual(product.name,'Foo')
        self.assertEqual(product.description,'Foo')

        self.env['product.pricelist'].create({
            'name':'Foo',
            'item_ids':[(0,0,{'product_id':product.id,'fixed_price':1})],
        })

        #patchtemplate.writetomodifypricelistitems,whichcausessome
        #cacheinvalidation
        Template=self.registry['product.template']
        Template_write=Template.write

        defwrite(self,vals):
            result=Template_write(self,vals)
            items=self.env['product.pricelist.item'].search([('product_id','=',product.id)])
            items.fixed_price=2
            returnresult

        withunittest.mock.patch.object(Template,'write',write):
            #changeboth'name'and'description':duetosomeprogrammedcache
            #invalidation,thesecondfieldmaynotbeproperlyassigned
            product.write({'name':'Bar','description':'Bar'})
            self.assertEqual(product.name,'Bar')
            self.assertEqual(product.description,'Bar')


classTestVariantsExclusion(common.TestProductCommon):
    defsetUp(self):
        res=super(TestVariantsExclusion,self).setUp()
        self.smartphone=self.env['product.template'].create({
            'name':'Smartphone',
        })

        self.size_attr=self.env['product.attribute'].create({'name':'Size'})
        self.size_attr_value_s=self.env['product.attribute.value'].create({'name':'S','attribute_id':self.size_attr.id})
        self.size_attr_value_xl=self.env['product.attribute.value'].create({'name':'XL','attribute_id':self.size_attr.id})

        self.storage_attr=self.env['product.attribute'].create({'name':'Storage'})
        self.storage_attr_value_128=self.env['product.attribute.value'].create({'name':'128','attribute_id':self.storage_attr.id})
        self.storage_attr_value_256=self.env['product.attribute.value'].create({'name':'256','attribute_id':self.storage_attr.id})

        #addattributestoproduct
        self.smartphone_size_attribute_lines=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.smartphone.id,
            'attribute_id':self.size_attr.id,
            'value_ids':[(6,0,[self.size_attr_value_s.id,self.size_attr_value_xl.id])],
        })

        self.smartphone_storage_attribute_lines=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.smartphone.id,
            'attribute_id':self.storage_attr.id,
            'value_ids':[(6,0,[self.storage_attr_value_128.id,self.storage_attr_value_256.id])],
        })

        defget_ptav(model,att):
            returnmodel.valid_product_template_attribute_line_ids.filtered(
                lambdal:l.attribute_id==att.attribute_id
            ).product_template_value_ids.filtered(
                lambdav:v.product_attribute_value_id==att
            )
        self.smartphone_s=get_ptav(self.smartphone,self.size_attr_value_s)
        self.smartphone_256=get_ptav(self.smartphone,self.storage_attr_value_256)
        self.smartphone_128=get_ptav(self.smartphone,self.storage_attr_value_128)
        returnres

    deftest_variants_1_exclusion(self):
        #CreateoneexclusionforSmartphoneS
        self.smartphone_s.write({
            'exclude_for':[(0,0,{
                'product_tmpl_id':self.smartphone.id,
                'value_ids':[(6,0,[self.smartphone_256.id])]
            })]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),3,'Withexclusion{s:[256]},thesmartphoneshouldhave3activedifferentvariants')

        #Deleteexclusion
        self.smartphone_s.write({
            'exclude_for':[(2,self.smartphone_s.exclude_for.id,0)]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),4,'Withnoexclusion,thesmartphoneshouldhave4activedifferentvariants')

    deftest_variants_2_exclusions_same_line(self):
        #CreatetwoexclusionsforSmartphoneSonthesameline
        self.smartphone_s.write({
            'exclude_for':[(0,0,{
                'product_tmpl_id':self.smartphone.id,
                'value_ids':[(6,0,[self.smartphone_128.id,self.smartphone_256.id])]
            })]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),2,'Withexclusion{s:[128,256]},thesmartphoneshouldhave2activedifferentvariants')

        #Deleteoneexclusionoftheline
        self.smartphone_s.write({
            'exclude_for':[(1,self.smartphone_s.exclude_for.id,{
                'product_tmpl_id':self.smartphone.id,
                'value_ids':[(6,0,[self.smartphone_128.id])]
            })]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),3,'Withexclusion{s:[128]},thesmartphoneshouldhave3activedifferentvariants')

        #Deleteexclusion
        self.smartphone_s.write({
            'exclude_for':[(2,self.smartphone_s.exclude_for.id,0)]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),4,'Withnoexclusion,thesmartphoneshouldhave4activedifferentvariants')

    deftest_variants_2_exclusions_different_lines(self):
        #add1exclusion
        self.smartphone_s.write({
            'exclude_for':[(0,0,{
                'product_tmpl_id':self.smartphone.id,
                'value_ids':[(6,0,[self.smartphone_128.id])]
            })]
        })

        #add1exclusiononadifferentline
        self.smartphone_s.write({
            'exclude_for':[(0,0,{
                'product_tmpl_id':self.smartphone.id,
                'value_ids':[(6,0,[self.smartphone_256.id])]
            })]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),2,'Withexclusion{s:[128,256]},thesmartphoneshouldhave2activedifferentvariants')

        #deleteoneexclusionline
        self.smartphone_s.write({
            'exclude_for':[(2,self.smartphone_s.exclude_for.ids[0],0)]
        })
        self.assertEqual(len(self.smartphone.product_variant_ids),3,'Withoneexclusion,thesmartphoneshouldhave3activedifferentvariants')
