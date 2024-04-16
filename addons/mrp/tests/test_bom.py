#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportexceptions
fromflectra.testsimportForm
fromflectra.addons.mrp.tests.commonimportTestMrpCommon
fromflectra.toolsimportfloat_compare,float_round,float_repr


classTestBoM(TestMrpCommon):

    deftest_01_explode(self):
        boms,lines=self.bom_1.explode(self.product_4,3)
        self.assertEqual(set([bom[0].idforbominboms]),set(self.bom_1.ids))
        self.assertEqual(set([line[0].idforlineinlines]),set(self.bom_1.bom_line_ids.ids))

        boms,lines=self.bom_3.explode(self.product_6,3)
        self.assertEqual(set([bom[0].idforbominboms]),set((self.bom_2|self.bom_3).ids))
        self.assertEqual(
            set([line[0].idforlineinlines]),
            set((self.bom_2|self.bom_3).mapped('bom_line_ids').filtered(lambdaline:notline.child_bom_idorline.child_bom_id.type!='phantom').ids))

    deftest_10_variants(self):
        test_bom=self.env['mrp.bom'].create({
            'product_id':self.product_7_3.id,
            'product_tmpl_id':self.product_7_template.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':4.0,
            'type':'normal',
        })
        test_bom.write({
            'operation_ids':[
                (0,0,{'name':'CuttingMachine','workcenter_id':self.workcenter_1.id,'time_cycle':12,'sequence':1}),
                (0,0,{'name':'WeldMachine','workcenter_id':self.workcenter_1.id,'time_cycle':18,'sequence':2}),
            ],
        })
        test_bom_l1=self.env['mrp.bom.line'].create({
            'bom_id':test_bom.id,
            'product_id':self.product_2.id,
            'product_qty':2,
        })
        test_bom_l2=self.env['mrp.bom.line'].create({
            'bom_id':test_bom.id,
            'product_id':self.product_3.id,
            'product_qty':2,
            'bom_product_template_attribute_value_ids':[(4,self.product_7_attr1_v1.id)],
        })
        test_bom_l3=self.env['mrp.bom.line'].create({
            'bom_id':test_bom.id,
            'product_id':self.product_4.id,
            'product_qty':2,
            'bom_product_template_attribute_value_ids':[(4,self.product_7_attr1_v2.id)],
        })
        boms,lines=test_bom.explode(self.product_7_3,4)
        self.assertIn(test_bom,[b[0]forbinboms])
        self.assertIn(test_bom_l1,[l[0]forlinlines])
        self.assertNotIn(test_bom_l2,[l[0]forlinlines])
        self.assertNotIn(test_bom_l3,[l[0]forlinlines])

        boms,lines=test_bom.explode(self.product_7_1,4)
        self.assertIn(test_bom,[b[0]forbinboms])
        self.assertIn(test_bom_l1,[l[0]forlinlines])
        self.assertIn(test_bom_l2,[l[0]forlinlines])
        self.assertNotIn(test_bom_l3,[l[0]forlinlines])

        boms,lines=test_bom.explode(self.product_7_2,4)
        self.assertIn(test_bom,[b[0]forbinboms])
        self.assertIn(test_bom_l1,[l[0]forlinlines])
        self.assertNotIn(test_bom_l2,[l[0]forlinlines])
        self.assertIn(test_bom_l3,[l[0]forlinlines])

    deftest_11_multi_level_variants(self):
        tmp_picking_type=self.env['stock.picking.type'].create({
            'name':'Manufacturing',
            'code':'mrp_operation',
            'sequence_code':'TMP',
            'sequence_id':self.env['ir.sequence'].create({
                'code':'mrp.production',
                'name':'tmp_production_sequence',
            }).id,
        })
        test_bom_1=self.env['mrp.bom'].create({
            'product_tmpl_id':self.product_5.product_tmpl_id.id,
            'product_uom_id':self.product_5.uom_id.id,
            'product_qty':1.0,
            'type':'phantom'
        })
        test_bom_1.write({
            'operation_ids':[
                (0,0,{'name':'GiftWrapMaching','workcenter_id':self.workcenter_1.id,'time_cycle':15,'sequence':1}),
            ],
        })
        test_bom_1_l1=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_1.id,
            'product_id':self.product_3.id,
            'product_qty':3,
        })

        test_bom_2=self.env['mrp.bom'].create({
            'product_id':self.product_7_3.id,
            'product_tmpl_id':self.product_7_template.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':4.0,
            'type':'normal',
        })
        test_bom_2.write({
            'operation_ids':[
                (0,0,{'name':'CuttingMachine','workcenter_id':self.workcenter_1.id,'time_cycle':12,'sequence':1}),
                (0,0,{'name':'WeldMachine','workcenter_id':self.workcenter_1.id,'time_cycle':18,'sequence':2}),
            ]
        })
        test_bom_2_l1=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_2.id,
            'product_id':self.product_2.id,
            'product_qty':2,
        })
        test_bom_2_l2=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_2.id,
            'product_id':self.product_5.id,
            'product_qty':2,
            'bom_product_template_attribute_value_ids':[(4,self.product_7_attr1_v1.id)],
        })
        test_bom_2_l3=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_2.id,
            'product_id':self.product_5.id,
            'product_qty':2,
            'bom_product_template_attribute_value_ids':[(4,self.product_7_attr1_v2.id)],
        })
        test_bom_2_l4=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_2.id,
            'product_id':self.product_4.id,
            'product_qty':2,
        })

        #checkproduct>product_tmpl
        boms,lines=test_bom_2.explode(self.product_7_1,4)
        self.assertEqual(set((test_bom_2|self.bom_2).ids),set([b[0].idforbinboms]))
        self.assertEqual(set((test_bom_2_l1|test_bom_2_l4|self.bom_2.bom_line_ids).ids),set([l[0].idforlinlines]))

        #checksequencepriority
        test_bom_1.write({'sequence':1})
        boms,lines=test_bom_2.explode(self.product_7_1,4)
        self.assertEqual(set((test_bom_2|test_bom_1).ids),set([b[0].idforbinboms]))
        self.assertEqual(set((test_bom_2_l1|test_bom_2_l4|test_bom_1.bom_line_ids).ids),set([l[0].idforlinlines]))

        #checkwithanotherpicking_type
        test_bom_1.write({'picking_type_id':self.warehouse_1.manu_type_id.id})
        self.bom_2.write({'picking_type_id':tmp_picking_type.id})
        test_bom_2.write({'picking_type_id':tmp_picking_type.id})
        boms,lines=test_bom_2.explode(self.product_7_1,4)
        self.assertEqual(set((test_bom_2|self.bom_2).ids),set([b[0].idforbinboms]))
        self.assertEqual(set((test_bom_2_l1|test_bom_2_l4|self.bom_2.bom_line_ids).ids),set([l[0].idforlinlines]))

        #checkrecursion
        test_bom_3=self.env['mrp.bom'].create({
            'product_id':self.product_9.id,
            'product_tmpl_id':self.product_9.product_tmpl_id.id,
            'product_uom_id':self.product_9.uom_id.id,
            'product_qty':1.0,
            'consumption':'flexible',
            'type':'normal'
        })
        test_bom_4=self.env['mrp.bom'].create({
            'product_id':self.product_10.id,
            'product_tmpl_id':self.product_10.product_tmpl_id.id,
            'product_uom_id':self.product_10.uom_id.id,
            'product_qty':1.0,
            'consumption':'flexible',
            'type':'phantom'
        })
        test_bom_3_l1=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_3.id,
            'product_id':self.product_10.id,
            'product_qty':1.0,
        })
        test_bom_4_l1=self.env['mrp.bom.line'].create({
            'bom_id':test_bom_4.id,
            'product_id':self.product_9.id,
            'product_qty':1.0,
        })
        withself.assertRaises(exceptions.UserError):
            test_bom_3.explode(self.product_9,1)

    deftest_12_multi_level_variants2(self):
        """Testskipbomlinewithsameattributevaluesinbomlines."""

        Product=self.env['product.product']
        ProductAttribute=self.env['product.attribute']
        ProductAttributeValue=self.env['product.attribute.value']

        #ProductAttribute
        att_color=ProductAttribute.create({'name':'Color','sequence':1})
        att_size=ProductAttribute.create({'name':'size','sequence':2})

        #ProductAttributecolorValue
        att_color_red=ProductAttributeValue.create({'name':'red','attribute_id':att_color.id,'sequence':1})
        att_color_blue=ProductAttributeValue.create({'name':'blue','attribute_id':att_color.id,'sequence':2})
        #ProductAttributesizeValue
        att_size_big=ProductAttributeValue.create({'name':'big','attribute_id':att_size.id,'sequence':1})
        att_size_medium=ProductAttributeValue.create({'name':'medium','attribute_id':att_size.id,'sequence':2})

        #CreateTemplateProduct
        product_template=self.env['product.template'].create({
            'name':'Sofa',
            'attribute_line_ids':[
                (0,0,{
                    'attribute_id':att_color.id,
                    'value_ids':[(6,0,[att_color_red.id,att_color_blue.id])]
                }),
                (0,0,{
                    'attribute_id':att_size.id,
                    'value_ids':[(6,0,[att_size_big.id,att_size_medium.id])]
                })
            ]
        })

        sofa_red=product_template.attribute_line_ids[0].product_template_value_ids[0]
        sofa_blue=product_template.attribute_line_ids[0].product_template_value_ids[1]

        sofa_big=product_template.attribute_line_ids[1].product_template_value_ids[0]
        sofa_medium=product_template.attribute_line_ids[1].product_template_value_ids[1]

        #CreatecomponentsOfBOM
        product_A=Product.create({
            'name':'Wood'})
        product_B=Product.create({
            'name':'Clothes'})

        #CreateBOM
        self.env['mrp.bom'].create({
            'product_tmpl_id':product_template.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{
                    'product_id':product_A.id,
                    'product_qty':1,
                    'bom_product_template_attribute_value_ids':[(4,sofa_red.id),(4,sofa_blue.id),(4,sofa_big.id)],
                }),
                (0,0,{
                    'product_id':product_B.id,
                    'product_qty':1,
                    'bom_product_template_attribute_value_ids':[(4,sofa_red.id),(4,sofa_blue.id)]
                })
            ]
        })

        dict_consumed_products={
            sofa_red+sofa_big:product_A+product_B,
            sofa_red+sofa_medium:product_B,
            sofa_blue+sofa_big:product_A+product_B,
            sofa_blue+sofa_medium:product_B,
        }

        #Createproductionorderforallvariants.
        forcombination,consumed_productsindict_consumed_products.items():
            product=product_template.product_variant_ids.filtered(lambdap:p.product_template_attribute_value_ids==combination)
            mrp_order_form=Form(self.env['mrp.production'])
            mrp_order_form.product_id=product
            mrp_order=mrp_order_form.save()

            #Checkconsumedmaterialsinproductionorder.
            self.assertEqual(mrp_order.move_raw_ids.product_id,consumed_products)

    deftest_13_bom_kit_qty(self):
        self.env['mrp.bom'].create({
            'product_id':self.product_7_3.id,
            'product_tmpl_id':self.product_7_template.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':4.0,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{
                    'product_id':self.product_2.id,
                    'product_qty':2,
                }),
                (0,0,{
                    'product_id':self.product_3.id,
                    'product_qty':2,
                })
            ]
        })
        location=self.env.ref('stock.stock_location_stock')
        self.env['stock.quant']._update_available_quantity(self.product_2,location,4.0)
        self.env['stock.quant']._update_available_quantity(self.product_3,location,8.0)
        #Forcethekitproductavailableqtytobecomputedatthesametimethanitscomponentquantities
        #Because`qty_available`ofabomkit"recurse"on`qty_available`ofitscomponent,
        #andthisisatrickythingfortheORM:
        #`qty_available`getscalledfor`product_7_3`,`product_2`and`product_3`
        #whichthenrecurseoncalling`qty_available`for`product_2`and`product_3`tocomputethequantityof
        #thekit`product_7_3`.`product_2`and`product_3`getsprotectedatthefirstcallofthecomputemethod,
        #endingtherecursecalltonotcallthecomputemethodandjustlefttheFalsyvalue`0.0`
        #forthecomponentsavailableqty.
        kit_product_qty,_,_=(self.product_7_3+self.product_2+self.product_3).mapped("qty_available")
        self.assertEqual(kit_product_qty,8)

    deftest_14_bom_kit_qty_multi_uom(self):
        uom_dozens=self.env.ref('uom.product_uom_dozen')
        uom_unit=self.env.ref('uom.product_uom_unit')
        product_unit=self.env['product.product'].create({
            'name':'Testunits',
            'type':'product',
            'uom_id':uom_unit.id,
        })
        product_dozens=self.env['product.product'].create({
            'name':'Testdozens',
            'type':'product',
            'uom_id':uom_dozens.id,
        })

        self.env['mrp.bom'].create({
            'product_tmpl_id':product_unit.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{
                    'product_id':product_dozens.id,
                    'product_qty':1,
                    'product_uom_id':uom_unit.id,
                })
            ]
        })
        location=self.env.ref('stock.stock_location_stock')
        self.env['stock.quant']._update_available_quantity(product_dozens,location,1.0)
        self.assertEqual(product_unit.qty_available,12.0)

    deftest_13_negative_on_hand_qty(self):
        #WesettheProductUnitofMeasuredigitsto5.
        #Becausefloat_round(-384.0,5)=-384.00000000000006
        #Andfloat_round(-384.0,2)=-384.0
        precision=self.env.ref('product.decimal_product_uom')
        precision.digits=5

        #WesettheUnit(s)roundingto0.0001(digit=4)
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_unit.rounding=0.0001

        _=self.env['mrp.bom'].create({
            'product_id':self.product_2.id,
            'product_tmpl_id':self.product_2.product_tmpl_id.id,
            'product_uom_id':uom_unit.id,
            'product_qty':1.00,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{
                    'product_id':self.product_3.id,
                    'product_qty':1.000,
                }),
            ]
        })

        self.env['stock.quant']._update_available_quantity(self.product_3,self.env.ref('stock.stock_location_stock'),-384.0)

        kit_product_qty=self.product_2.qty_available #Withoutproduct_3intheprefetch
        #Usethefloat_reprtoremoveextrasmalldecimal(andrepresentthefront-endbehavior)
        self.assertEqual(float_repr(float_round(kit_product_qty,precision_digits=precision.digits),precision_digits=precision.digits),'-384.00000')

        self.product_2.invalidate_cache(fnames=['qty_available'],ids=self.product_2.ids)
        kit_product_qty,_=(self.product_2+self.product_3).mapped("qty_available") #Withproduct_3intheprefetch
        self.assertEqual(float_repr(float_round(kit_product_qty,precision_digits=precision.digits),precision_digits=precision.digits),'-384.00000')

    deftest_13_bom_kit_qty_multi_uom(self):
        uom_dozens=self.env.ref('uom.product_uom_dozen')
        uom_unit=self.env.ref('uom.product_uom_unit')
        product_unit=self.env['product.product'].create({
            'name':'Testunits',
            'type':'product',
            'uom_id':uom_unit.id,
        })
        product_dozens=self.env['product.product'].create({
            'name':'Testdozens',
            'type':'product',
            'uom_id':uom_dozens.id,
        })

        self.env['mrp.bom'].create({
            'product_tmpl_id':product_unit.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{
                    'product_id':product_dozens.id,
                    'product_qty':1,
                    'product_uom_id':uom_unit.id,
                })
            ]
        })
        location=self.env.ref('stock.stock_location_stock')
        self.env['stock.quant']._update_available_quantity(product_dozens,location,1.0)
        self.assertEqual(product_unit.qty_available,12.0)

    deftest_20_bom_report(self):
        """Simulateacrumblereceiptwithmrpandopenthebomstructure
        reportandcheckthatdatainsdearecorrect.
        """
        uom_kg=self.env.ref('uom.product_uom_kgm')
        uom_litre=self.env.ref('uom.product_uom_litre')
        crumble=self.env['product.product'].create({
            'name':'Crumble',
            'type':'product',
            'uom_id':uom_kg.id,
            'uom_po_id':uom_kg.id,
        })
        butter=self.env['product.product'].create({
            'name':'Butter',
            'type':'product',
            'uom_id':uom_kg.id,
            'uom_po_id':uom_kg.id,
            'standard_price':7.01
        })
        biscuit=self.env['product.product'].create({
            'name':'Biscuit',
            'type':'product',
            'uom_id':uom_kg.id,
            'uom_po_id':uom_kg.id,
            'standard_price':1.5
        })
        bom_form_crumble=Form(self.env['mrp.bom'])
        bom_form_crumble.product_tmpl_id=crumble.product_tmpl_id
        bom_form_crumble.product_qty=11
        bom_form_crumble.product_uom_id=uom_kg
        bom_crumble=bom_form_crumble.save()

        workcenter=self.env['mrp.workcenter'].create({
            'costs_hour':10,
            'name':'DesertsTable'
        })

        withForm(bom_crumble)asbom:
            withbom.bom_line_ids.new()asline:
                line.product_id=butter
                line.product_uom_id=uom_kg
                line.product_qty=5
            withbom.bom_line_ids.new()asline:
                line.product_id=biscuit
                line.product_uom_id=uom_kg
                line.product_qty=6
            withbom.operation_ids.new()asoperation:
                operation.workcenter_id=workcenter
                operation.name='Preparebiscuits'
                operation.time_cycle_manual=5
            withbom.operation_ids.new()asoperation:
                operation.workcenter_id=workcenter
                operation.name='Preparebutter'
                operation.time_cycle_manual=3
            withbom.operation_ids.new()asoperation:
                operation.workcenter_id=workcenter
                operation.name='Mixmanually'
                operation.time_cycle_manual=5

        #TESTBOMSTRUCTUREVALUEWITHBOMQUANTITY
        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_crumble.id,searchQty=11,searchVariant=False)
        #5min'Preparebiscuits'+3min'Preparebutter'+5min'Mixmanually'=13minutesfor1biscuitsso13*11=143minutes
        self.assertEqual(report_values['lines']['operations_time'],143.0,'Operationtimeshouldbethesamefor1unitorforthebatch')
        #Operationcostisthesumofoperationline.
        self.assertEqual(float_compare(report_values['lines']['operations_cost'],23.84,precision_digits=2),0,'143minutefor10$/hours->23.84')

        forcomponent_lineinreport_values['lines']['components']:
            #standardprice*bomlinequantity*currentquantity/bomfinishedproductquantity
            ifcomponent_line['prod_id']==butter.id:
                #5kgofbutterat7.01$for11kgofcrumble->35.05$
                self.assertEqual(float_compare(component_line['total'],(7.01*5),precision_digits=2),0)
            ifcomponent_line['prod_id']==biscuit.id:
                #6kgofbiscuitsat1.50$for11kgofcrumble->9$
                self.assertEqual(float_compare(component_line['total'],(1.5*6),precision_digits=2),0)
        #totalprice=35.05+9+operation_cost(23.84)=67.89
        self.assertEqual(float_compare(report_values['lines']['total'],67.89,precision_digits=2),0,'ProductBomPriceisnotcorrect')
        self.assertEqual(float_compare(report_values['lines']['total']/11.0,6.17,precision_digits=2),0,'ProductUnitBomPriceisnotcorrect')

        #TESTBOMSTRUCTUREVALUEBYUNIT
        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_crumble.id,searchQty=1,searchVariant=False)
        #5min'Preparebiscuits'+3min'Preparebutter'+5min'Mixmanually'=13minutes
        self.assertEqual(report_values['lines']['operations_time'],13.0,'Operationtimeshouldbethesamefor1unitorforthebatch')
        #Operationcostisthesumofoperationline.
        operation_cost=float_round(5/60*10,precision_digits=2)*2+float_round(3/60*10,precision_digits=2)
        self.assertEqual(float_compare(report_values['lines']['operations_cost'],operation_cost,precision_digits=2),0,'13minutefor10$/hours->2.16')

        forcomponent_lineinreport_values['lines']['components']:
            #standardprice*bomlinequantity*currentquantity/bomfinishedproductquantity
            ifcomponent_line['prod_id']==butter.id:
                #5kgofbutterat7.01$for11kgofcrumble->/11forpriceperunit(3.19)
                self.assertEqual(float_compare(component_line['total'],(7.01*5)*(1/11),precision_digits=2),0)
            ifcomponent_line['prod_id']==biscuit.id:
                #6kgofbiscuitsat1.50$for11kgofcrumble->/11forpriceperunit(0.82)
                self.assertEqual(float_compare(component_line['total'],(1.5*6)*(1/11),precision_digits=2),0)
        #totalprice=3.19+0.82+operation_cost(0.83+0.83+0.5=2.16)=6,17
        self.assertEqual(float_compare(report_values['lines']['total'],6.17,precision_digits=2),0,'ProductUnitBomPriceisnotcorrect')

        #TESTOPERATIONCOSTWHENPRODUCEDQTY>BOMQUANTITY
        report_values_12=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_crumble.id,searchQty=12,searchVariant=False)
        report_values_22=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_crumble.id,searchQty=22,searchVariant=False)

        #Operationcost=47.66€=256(min)*10€/h
        self.assertEqual(float_compare(report_values_22['lines']['operations_cost'],47.66,precision_digits=2),0,'Operationcostisnotcorrect')

        #CreateamorecomplexBoMwithasubproduct
        cheese_cake=self.env['product.product'].create({
            'name':'CheeseCake300g',
            'type':'product',
        })
        cream=self.env['product.product'].create({
            'name':'cream',
            'type':'product',
            'uom_id':uom_litre.id,
            'uom_po_id':uom_litre.id,
            'standard_price':5.17,
        })
        bom_form_cheese_cake=Form(self.env['mrp.bom'])
        bom_form_cheese_cake.product_tmpl_id=cheese_cake.product_tmpl_id
        bom_form_cheese_cake.product_qty=60
        bom_form_cheese_cake.product_uom_id=self.uom_unit
        bom_cheese_cake=bom_form_cheese_cake.save()

        workcenter_2=self.env['mrp.workcenter'].create({
            'name':'cakemounting',
            'costs_hour':20,
            'time_start':10,
            'time_stop':15
        })

        withForm(bom_cheese_cake)asbom:
            withbom.bom_line_ids.new()asline:
                line.product_id=cream
                line.product_uom_id=uom_litre
                line.product_qty=3
            withbom.bom_line_ids.new()asline:
                line.product_id=crumble
                line.product_uom_id=uom_kg
                line.product_qty=5.4
            withbom.operation_ids.new()asoperation:
                operation.workcenter_id=workcenter
                operation.name='Mixcheeseandcrumble'
                operation.time_cycle_manual=10
            withbom.operation_ids.new()asoperation:
                operation.workcenter_id=workcenter_2
                operation.name='Cakemounting'
                operation.time_cycle_manual=5

        #TESTCHEESEBOMSTRUCTUREVALUEWITHBOMQUANTITY
        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_cheese_cake.id,searchQty=60,searchVariant=False)
        #Operationtime=15min*60+time_start+time_stop=925
        self.assertEqual(report_values['lines']['operations_time'],925.0,'Operationtimeshouldbethesamefor1unitorforthebatch')
        #Operationcostisthesumofoperationline:(60*10)/60*10€+(10+15+60*5)/60*20€=208,33€
        self.assertEqual(float_compare(report_values['lines']['operations_cost'],208.33,precision_digits=2),0)

        forcomponent_lineinreport_values['lines']['components']:
            #standardprice*bomlinequantity*currentquantity/bomfinishedproductquantity
            ifcomponent_line['prod_id']==cream.id:
                #3literofcreamat5.17$for60unitofcheesecake->15.51$
                self.assertEqual(float_compare(component_line['total'],(3*5.17),precision_digits=2),0)
            ifcomponent_line['prod_id']==crumble.id:
                #5.4kgofcrumbleatthecostofabatch.
                crumble_cost=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_crumble.id,searchQty=5.4,searchVariant=False)['lines']['total']
                self.assertEqual(float_compare(component_line['total'],crumble_cost,precision_digits=2),0)
        #totalprice=Cream(15.51€)+crumble_cost(34.63€)+operation_cost(208,33)=258.47€
        self.assertEqual(float_compare(report_values['lines']['total'],258.47,precision_digits=2),0,'ProductBomPriceisnotcorrect')

    deftest_bom_report_dozens(self):
        """Simulateadrawerbomwithdozensasbomunits
        """
        uom_dozen=self.env.ref('uom.product_uom_dozen')
        uom_unit=self.env.ref('uom.product_uom_unit')
        drawer=self.env['product.product'].create({
            'name':'drawer',
            'type':'product',
            'uom_id':uom_unit.id,
            'uom_po_id':uom_unit.id,
        })
        screw=self.env['product.product'].create({
            'name':'screw',
            'type':'product',
            'uom_id':uom_unit.id,
            'uom_po_id':uom_unit.id,
            'standard_price':7.01
        })

        bom_form_drawer=Form(self.env['mrp.bom'])
        bom_form_drawer.product_tmpl_id=drawer.product_tmpl_id
        bom_form_drawer.product_qty=11
        bom_form_drawer.product_uom_id=uom_dozen
        bom_drawer=bom_form_drawer.save()

        workcenter=self.env['mrp.workcenter'].create({
            'costs_hour':10,
            'name':'DesertsTable'
        })

        withForm(bom_drawer)asbom:
            withbom.bom_line_ids.new()asline:
                line.product_id=screw
                line.product_uom_id=uom_unit
                line.product_qty=5
            withbom.operation_ids.new()asoperation:
                operation.workcenter_id=workcenter
                operation.name='Screwdrawer'
                operation.time_cycle_manual=5

        #TESTBOMSTRUCTUREVALUEWITHBOMQUANTITY
        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_drawer.id,searchQty=11,searchVariant=False)
        #5min'Preparebiscuits'+3min'Preparebutter'+5min'Mixmanually'=13minutes
        self.assertEqual(report_values['lines']['operations_time'],660.0,'Operationtimeshouldbethesamefor1unitorforthebatch')


    deftest_21_bom_report_variant(self):
        """TestasubBoMprocesswithmultiplevariants.
        BOM1:
        producttemplate=car
        quantity=5units
        -redpaint50l->redcar(product.product)
        -bluepaint50l->bluecar
        -reddashboardwithgps->redcarwithGPS
        -reddashboardw/hgps->redw/hGPS
        -bluedashboardwithgps->bluecarwithGPS
        -bluedashboardw/hgps->bluew/hGPS

        BOM2:
        product_tmpl=dashboard
        quantity=2
        -redpaint1l->reddashboard(product.product)
        -bluepaint1l->bluedashboard
        -gps->dashboardwithgps

        CheckthePriceforaBlueCarwithGPS->910$:
        10lofbluepaint->200$
        1bluedashboardGPS->710$:
            -0.5lofbluepaint->10$
            -GPS->700$

        Checkthepriceforaredcar->10.5lofredpaint->210$
        """
        #Createaproducttemplatecarwithattributesgps(yes,no),color(red,blue)
        self.car=self.env['product.template'].create({
            'name':'Car',
        })
        self.gps_attribute=self.env['product.attribute'].create({'name':'GPS','sequence':1})
        self.gps_yes=self.env['product.attribute.value'].create({
            'name':'Yes',
            'attribute_id':self.gps_attribute.id,
            'sequence':1,
        })
        self.gps_no=self.env['product.attribute.value'].create({
            'name':'No',
            'attribute_id':self.gps_attribute.id,
            'sequence':2,
        })

        self.car_gps_attribute_line=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.car.id,
            'attribute_id':self.gps_attribute.id,
            'value_ids':[(6,0,[self.gps_yes.id,self.gps_no.id])],
        })
        self.car_gps_yes=self.car_gps_attribute_line.product_template_value_ids[0]
        self.car_gps_no=self.car_gps_attribute_line.product_template_value_ids[1]

        self.color_attribute=self.env['product.attribute'].create({'name':'Color','sequence':1})
        self.color_red=self.env['product.attribute.value'].create({
            'name':'Red',
            'attribute_id':self.color_attribute.id,
            'sequence':1,
        })
        self.color_blue=self.env['product.attribute.value'].create({
            'name':'Blue',
            'attribute_id':self.color_attribute.id,
            'sequence':2,
        })

        self.car_color_attribute_line=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.car.id,
            'attribute_id':self.color_attribute.id,
            'value_ids':[(6,0,[self.color_red.id,self.color_blue.id])],
        })
        self.car_color_red=self.car_color_attribute_line.product_template_value_ids[0]
        self.car_color_blue=self.car_color_attribute_line.product_template_value_ids[1]

        #Blueandredpaint
        uom_litre=self.env.ref('uom.product_uom_litre')
        self.paint=self.env['product.template'].create({
            'name':'Paint',
            'uom_id':uom_litre.id,
            'uom_po_id':uom_litre.id
        })
        self.paint_color_attribute_line=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.paint.id,
            'attribute_id':self.color_attribute.id,
            'value_ids':[(6,0,[self.color_red.id,self.color_blue.id])],
        })
        self.paint_color_red=self.paint_color_attribute_line.product_template_value_ids[0]
        self.paint_color_blue=self.paint_color_attribute_line.product_template_value_ids[1]

        self.paint.product_variant_ids.write({'standard_price':20})

        self.dashboard=self.env['product.template'].create({
            'name':'Dashboard',
            'standard_price':1000,
        })

        self.dashboard_gps_attribute_line=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.dashboard.id,
            'attribute_id':self.gps_attribute.id,
            'value_ids':[(6,0,[self.gps_yes.id,self.gps_no.id])],
        })
        self.dashboard_gps_yes=self.dashboard_gps_attribute_line.product_template_value_ids[0]
        self.dashboard_gps_no=self.dashboard_gps_attribute_line.product_template_value_ids[1]

        self.dashboard_color_attribute_line=self.env['product.template.attribute.line'].create({
            'product_tmpl_id':self.dashboard.id,
            'attribute_id':self.color_attribute.id,
            'value_ids':[(6,0,[self.color_red.id,self.color_blue.id])],
        })
        self.dashboard_color_red=self.dashboard_color_attribute_line.product_template_value_ids[0]
        self.dashboard_color_blue=self.dashboard_color_attribute_line.product_template_value_ids[1]

        self.gps=self.env['product.product'].create({
            'name':'GPS',
            'standard_price':700,
        })

        bom_form_car=Form(self.env['mrp.bom'])
        bom_form_car.product_tmpl_id=self.car
        bom_form_car.product_qty=5
        withbom_form_car.bom_line_ids.new()asline:
            line.product_id=self.paint._get_variant_for_combination(self.paint_color_red)
            line.product_uom_id=uom_litre
            line.product_qty=50
            line.bom_product_template_attribute_value_ids.add(self.car_color_red)
        withbom_form_car.bom_line_ids.new()asline:
            line.product_id=self.paint._get_variant_for_combination(self.paint_color_blue)
            line.product_uom_id=uom_litre
            line.product_qty=50
            line.bom_product_template_attribute_value_ids.add(self.car_color_blue)
        withbom_form_car.bom_line_ids.new()asline:
            line.product_id=self.dashboard._get_variant_for_combination(self.dashboard_gps_yes+self.dashboard_color_red)
            line.product_qty=5
            line.bom_product_template_attribute_value_ids.add(self.car_gps_yes)
            line.bom_product_template_attribute_value_ids.add(self.car_color_red)
        withbom_form_car.bom_line_ids.new()asline:
            line.product_id=self.dashboard._get_variant_for_combination(self.dashboard_gps_yes+self.dashboard_color_blue)
            line.product_qty=5
            line.bom_product_template_attribute_value_ids.add(self.car_gps_yes)
            line.bom_product_template_attribute_value_ids.add(self.car_color_blue)
        withbom_form_car.bom_line_ids.new()asline:
            line.product_id=self.dashboard._get_variant_for_combination(self.dashboard_gps_no+self.dashboard_color_red)
            line.product_qty=5
            line.bom_product_template_attribute_value_ids.add(self.car_gps_no)
            line.bom_product_template_attribute_value_ids.add(self.car_color_red)
        withbom_form_car.bom_line_ids.new()asline:
            line.product_id=self.dashboard._get_variant_for_combination(self.dashboard_gps_no+self.dashboard_color_blue)
            line.product_qty=5
            line.bom_product_template_attribute_value_ids.add(self.car_gps_no)
            line.bom_product_template_attribute_value_ids.add(self.car_color_blue)
        bom_car=bom_form_car.save()

        bom_dashboard=Form(self.env['mrp.bom'])
        bom_dashboard.product_tmpl_id=self.dashboard
        bom_dashboard.product_qty=2
        withbom_dashboard.bom_line_ids.new()asline:
            line.product_id=self.paint._get_variant_for_combination(self.paint_color_red)
            line.product_uom_id=uom_litre
            line.product_qty=1
            line.bom_product_template_attribute_value_ids.add(self.dashboard_color_red)
        withbom_dashboard.bom_line_ids.new()asline:
            line.product_id=self.paint._get_variant_for_combination(self.paint_color_blue)
            line.product_uom_id=uom_litre
            line.product_qty=1
            line.bom_product_template_attribute_value_ids.add(self.dashboard_color_blue)
        withbom_dashboard.bom_line_ids.new()asline:
            line.product_id=self.gps
            line.product_qty=2
            line.bom_product_template_attribute_value_ids.add(self.dashboard_gps_yes)
        bom_dashboard=bom_dashboard.save()

        blue_car_with_gps=self.car._get_variant_for_combination(self.car_color_blue+self.car_gps_yes)

        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_car.id,searchQty=1,searchVariant=blue_car_with_gps.id)
        #Twolines.bluedashboardwithgpsandbluepaint.
        self.assertEqual(len(report_values['lines']['components']),2)

        #10lofbluepaint
        blue_paint=self.paint._get_variant_for_combination(self.paint_color_blue)
        self.assertEqual(blue_paint.id,report_values['lines']['components'][0]['prod_id'])
        self.assertEqual(report_values['lines']['components'][0]['prod_qty'],10)
        #1bluedashboardwithGPS
        blue_dashboard_gps=self.dashboard._get_variant_for_combination(self.dashboard_color_blue+self.dashboard_gps_yes)
        self.assertEqual(blue_dashboard_gps.id,report_values['lines']['components'][1]['prod_id'])
        self.assertEqual(report_values['lines']['components'][1]['prod_qty'],1)
        component=report_values['lines']['components'][1]
        report_values_dashboad=self.env['report.mrp.report_bom_structure']._get_bom(
            component['child_bom'],component['prod_id'],component['prod_qty'],
            component['line_id'],component['level']+1)

        self.assertEqual(len(report_values_dashboad['components']),2)
        self.assertEqual(blue_paint.id,report_values_dashboad['components'][0]['prod_id'])
        self.assertEqual(self.gps.id,report_values_dashboad['components'][1]['prod_id'])

        #0.5lofpaintatpriceof20$/litre->10$
        self.assertEqual(report_values_dashboad['components'][0]['total'],10)
        #GPS700$
        self.assertEqual(report_values_dashboad['components'][1]['total'],700)

        #DashboardbluewithGPSshouldhaveaBoMcostof710$
        self.assertEqual(report_values['lines']['components'][1]['total'],710)
        #10lofpaintatpriceof20$/litre->200$
        self.assertEqual(report_values['lines']['components'][0]['total'],200)

        #TotalcostofbluecarwithGPS:10+700+200=910
        self.assertEqual(report_values['lines']['total'],910)

        red_car_without_gps=self.car._get_variant_for_combination(self.car_color_red+self.car_gps_no)

        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_car.id,searchQty=1,searchVariant=red_car_without_gps.id)
        #SamemaththanbeforebutwithoutGPS
        self.assertEqual(report_values['lines']['total'],210)

    deftest_22_bom_report_recursive_bom(self):
        """TestreportwithrecursiveBoManddifferentquantities.
        BoM1:
        product=Finished(units)
        quantity=100units
        -Semi-Finished5kg

        BoM2:
        product=Semi-Finished(kg)
        quantity=11kg
        -Assembly2dozens

        BoM3:
        product=Assembly(dozens)
        quantity=5dozens
        -RawMaterial4litres(product.product5$/litre)

        CheckthePricefor80unitsofFinished->2.92$:
        """
        #Createaproductstemplates
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_kg=self.env.ref('uom.product_uom_kgm')
        uom_dozen=self.env.ref('uom.product_uom_dozen')
        uom_litre=self.env.ref('uom.product_uom_litre')

        finished=self.env['product.product'].create({
            'name':'Finished',
            'type':'product',
            'uom_id':uom_unit.id,
            'uom_po_id':uom_unit.id,
        })

        semi_finished=self.env['product.product'].create({
            'name':'Semi-Finished',
            'type':'product',
            'uom_id':uom_kg.id,
            'uom_po_id':uom_kg.id,
        })

        assembly=self.env['product.product'].create({
            'name':'Assembly',
            'type':'product',
            'uom_id':uom_dozen.id,
            'uom_po_id':uom_dozen.id,
        })

        raw_material=self.env['product.product'].create({
            'name':'RawMaterial',
            'type':'product',
            'uom_id':uom_litre.id,
            'uom_po_id':uom_litre.id,
            'standard_price':5,
        })

        #Createbom
        bom_finished=Form(self.env['mrp.bom'])
        bom_finished.product_tmpl_id=finished.product_tmpl_id
        bom_finished.product_qty=100
        withbom_finished.bom_line_ids.new()asline:
            line.product_id=semi_finished
            line.product_uom_id=uom_kg
            line.product_qty=5
        bom_finished=bom_finished.save()

        bom_semi_finished=Form(self.env['mrp.bom'])
        bom_semi_finished.product_tmpl_id=semi_finished.product_tmpl_id
        bom_semi_finished.product_qty=11
        withbom_semi_finished.bom_line_ids.new()asline:
            line.product_id=assembly
            line.product_uom_id=uom_dozen
            line.product_qty=2
        bom_semi_finished=bom_semi_finished.save()

        bom_assembly=Form(self.env['mrp.bom'])
        bom_assembly.product_tmpl_id=assembly.product_tmpl_id
        bom_assembly.product_qty=5
        withbom_assembly.bom_line_ids.new()asline:
            line.product_id=raw_material
            line.product_uom_id=uom_litre
            line.product_qty=4
        bom_assembly=bom_assembly.save()

        report_values=self.env['report.mrp.report_bom_structure']._get_report_data(bom_id=bom_finished.id,searchQty=80)

        self.assertAlmostEqual(report_values['lines']['total'],2.92)

    deftest_validate_no_bom_line_with_same_product(self):
        """
        CannotsetaBOMlineonaBOMwiththesameproductastheBOMitself
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        finished=self.env['product.product'].create({
            'name':'Finished',
            'type':'product',
            'uom_id':uom_unit.id,
            'uom_po_id':uom_unit.id,
        })
        bom_finished=Form(self.env['mrp.bom'])
        bom_finished.product_tmpl_id=finished.product_tmpl_id
        bom_finished.product_qty=100
        withbom_finished.bom_line_ids.new()asline:
            line.product_id=finished
            line.product_uom_id=uom_unit
            line.product_qty=5
        withself.assertRaises(exceptions.ValidationError),self.cr.savepoint():
            bom_finished=bom_finished.save()

    deftest_validate_no_bom_line_with_same_product_variant(self):
        """
        CannotsetaBOMlineonaBOMwiththesameproductvariantastheBOMitself
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        bom_finished=Form(self.env['mrp.bom'])
        bom_finished.product_tmpl_id=self.product_7_template
        bom_finished.product_id=self.product_7_3
        bom_finished.product_qty=100
        withbom_finished.bom_line_ids.new()asline:
            line.product_id=self.product_7_3
            line.product_uom_id=uom_unit
            line.product_qty=5
        withself.assertRaises(exceptions.ValidationError),self.cr.savepoint():
            bom_finished=bom_finished.save()
        
    deftest_validate_bom_line_with_different_product_variant(self):
        """
        CansetaBOMlineonaBOMwithadifferentproductvariantastheBOMitself(sameproduct)
        UsecaseforexampleAblackT-shirtmade fromawhiteT-shirtand
        blackcolor.
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        bom_finished=Form(self.env['mrp.bom'])
        bom_finished.product_tmpl_id=self.product_7_template
        bom_finished.product_id=self.product_7_3
        bom_finished.product_qty=100
        withbom_finished.bom_line_ids.new()asline:
            line.product_id=self.product_7_2
            line.product_uom_id=uom_unit
            line.product_qty=5
        bom_finished=bom_finished.save()

    deftest_validate_bom_line_with_variant_of_bom_product(self):
        """
        CansetaBOMlineonaBOMwithaproductvariantwhentheBOMhasnovariantselected
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        bom_finished=Form(self.env['mrp.bom'])
        bom_finished.product_tmpl_id=self.product_6.product_tmpl_id
        #noproduct_id
        bom_finished.product_qty=100
        withbom_finished.bom_line_ids.new()asline:
            line.product_id=self.product_7_2
            line.product_uom_id=uom_unit
            line.product_qty=5
        bom_finished=bom_finished.save()

    deftest_bom_kit_with_sub_kit(self):
        p1,p2,p3,p4=self.make_prods(4)
        self.make_bom(p1,p2,p3)
        self.make_bom(p2,p3,p4)

        loc=self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"]._update_available_quantity(p3,loc,10)
        self.env["stock.quant"]._update_available_quantity(p4,loc,10)
        self.assertEqual(p1.qty_available,5.0)
        self.assertEqual(p2.qty_available,10.0)
        self.assertEqual(p3.qty_available,10.0)

    deftest_update_bom_in_routing_workcenter(self):
        """
        ThistestchecksthebehaviourofupdatingtheBoMassociatedwitharoutingworkcenter,
        ItverifiesthatthelinkbetweentheBOMlinesandtheoperationiscorrectlydeleted.
        """
        p1,c1,c2=self.make_prods(3)
        bom=self.env['mrp.bom'].create({
            'product_tmpl_id':p1.product_tmpl_id.id,
            'product_qty':1.0,
            'bom_line_ids':[(0,0,{'product_id':c1.id,'product_qty':1.0}),
                             (0,0,{'product_id':c2.id,'product_qty':1.0})],
        })
        operation=self.env['mrp.routing.workcenter'].create({
            'name':'Operation',
            'workcenter_id':self.env.ref('mrp.mrp_workcenter_1').id,
            'bom_id':bom.id,
        })
        bom.bom_line_ids.operation_id=operation
        self.assertEqual(operation.bom_id,bom)
        operation.bom_id=self.bom_1
        self.assertEqual(operation.bom_id,self.bom_1)
        self.assertFalse(bom.bom_line_ids.operation_id)
