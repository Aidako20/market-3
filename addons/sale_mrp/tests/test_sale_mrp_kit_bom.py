#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase,Form


classTestSaleMrpKitBom(TransactionCase):

    def_create_product(self,name,type,price):
        returnself.env['product.product'].create({
            'name':name,
            'type':type,
            'standard_price':price,
        })

    deftest_sale_mrp_kit_bom_cogs(self):
        """CheckinvoiceCOGSamlaftersellinganddeliveringaproduct
        withKitBoMhavinganotherproductwithKitBoMascomponent"""

        #----------------------------------------------
        #BoMofKitA:
        #  -BoMType:Kit
        #  -Quantity:3
        #  -Components:
        #    *2xKitB
        #    *1xComponentA(Cost:$3,Storable)
        #
        #BoMofKitB:
        #  -BoMType:Kit
        #  -Quantity:10
        #  -Components:
        #    *2xComponentB(Cost:$4,Storable)
        #    *3xComponentBB(Cost:$5,Consumable)
        #----------------------------------------------

        self.env.user.company_id.anglo_saxon_accounting=True
        self.stock_input_account=self.env['account.account'].create({
            'name':'StockInput',
            'code':'StockIn',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
        })
        self.stock_output_account=self.env['account.account'].create({
            'name':'StockOutput',
            'code':'StockOut',
            'reconcile':True,
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
        })
        self.stock_valuation_account=self.env['account.account'].create({
            'name':'StockValuation',
            'code':'StockVal',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
        })
        self.expense_account=self.env['account.account'].create({
            'name':'ExpenseAccount',
            'code':'Exp',
            'user_type_id':self.env.ref('account.data_account_type_expenses').id,
        })
        self.income_account=self.env['account.account'].create({
            'name':'IncomeAccount',
            'code':'Inc',
            'user_type_id':self.env.ref('account.data_account_type_expenses').id,
        })
        self.stock_journal=self.env['account.journal'].create({
            'name':'StockJournal',
            'code':'STJTEST',
            'type':'general',
        })
        self.recv_account=self.env['account.account'].create({
            'name':'accountreceivable',
            'code':'RECV',
            'user_type_id':self.env.ref('account.data_account_type_receivable').id,
            'reconcile':True,
        })
        self.pay_account=self.env['account.account'].create({
            'name':'accountpayable',
            'code':'PAY',
            'user_type_id':self.env.ref('account.data_account_type_payable').id,
            'reconcile':True,
        })
        self.customer=self.env['res.partner'].create({
            'name':'customer',
            'property_account_receivable_id':self.recv_account.id,
            'property_account_payable_id':self.pay_account.id,
        })
        self.journal_sale=self.env['account.journal'].create({
            'name':'SaleJournal-Test',
            'code':'AJ-SALE',
            'type':'sale',
            'company_id':self.env.user.company_id.id,
        })

        self.component_a=self._create_product('ComponentA','product',3.00)
        self.component_b=self._create_product('ComponentB','product',4.00)
        self.component_bb=self._create_product('ComponentBB','consu',5.00)
        self.kit_a=self._create_product('KitA','product',0.00)
        self.kit_b=self._create_product('KitB','consu',0.00)

        self.kit_a.write({
            'categ_id':self.env.ref('product.product_category_all').id,
            'property_account_expense_id':self.expense_account.id,
            'property_account_income_id':self.income_account.id,
        })
        self.kit_a.categ_id.write({
            'property_stock_account_input_categ_id':self.stock_input_account.id,
            'property_stock_account_output_categ_id':self.stock_output_account.id,
            'property_stock_valuation_account_id':self.stock_valuation_account.id,
            'property_stock_journal':self.stock_journal.id,
            'property_valuation':'real_time',
        })

        #CreateBoMforKitA
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.kit_a
        bom_product_form.product_tmpl_id=self.kit_a.product_tmpl_id
        bom_product_form.product_qty=3.0
        bom_product_form.type='phantom'
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.kit_b
            bom_line.product_qty=2.0
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.component_a
            bom_line.product_qty=1.0
        self.bom_a=bom_product_form.save()

        #CreateBoMforKitB
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.kit_b
        bom_product_form.product_tmpl_id=self.kit_b.product_tmpl_id
        bom_product_form.product_qty=10.0
        bom_product_form.type='phantom'
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.component_b
            bom_line.product_qty=2.0
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.component_bb
            bom_line.product_qty=3.0
        self.bom_b=bom_product_form.save()

        so=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'order_line':[
                (0,0,{
                    'name':self.kit_a.name,
                    'product_id':self.kit_a.id,
                    'product_uom_qty':1.0,
                    'product_uom':self.kit_a.uom_id.id,
                    'price_unit':1,
                    'tax_id':False,
                })],
        })
        so.action_confirm()
        so.picking_ids.move_lines.quantity_done=1
        so.picking_ids.button_validate()

        invoice=so.with_context(default_journal_id=self.journal_sale.id)._create_invoices()
        invoice.action_post()

        #Checktheresultingaccountingentries
        amls=invoice.line_ids
        self.assertEqual(len(amls),4)
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==self.stock_output_account)
        self.assertEqual(stock_out_aml.debit,0)
        self.assertAlmostEqual(stock_out_aml.credit,1.53,msg="Shouldnotincludethevalueofconsumablecomponent")
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==self.expense_account)
        self.assertAlmostEqual(cogs_aml.debit,1.53,msg="Shouldnotincludethevalueofconsumablecomponent")
        self.assertEqual(cogs_aml.credit,0)

    deftest_reset_avco_kit(self):
        """
        Testaspecificusecase:Oneproductwith2variant,eachvarianthasitsownBoMwitheithercomponent_1or
        component_2.CreateaSOforoneofthevariant,confirm,cancel,resettodraftandthenchangetheproductof
        theSO->Thereshouldbenotraceback
        """
        component_1=self.env['product.product'].create({'name':'compo1'})
        component_2=self.env['product.product'].create({'name':'compo2'})

        product_category=self.env['product.category'].create({
            'name':'testavcokit',
            'property_cost_method':'average'
        })
        attributes=self.env['product.attribute'].create({'name':'Legs'})
        steel_legs=self.env['product.attribute.value'].create({'attribute_id':attributes.id,'name':'Steel'})
        aluminium_legs=self.env['product.attribute.value'].create(
            {'attribute_id':attributes.id,'name':'Aluminium'})

        product_template=self.env['product.template'].create({
            'name':'testproduct',
            'categ_id':product_category.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':attributes.id,
                'value_ids':[(6,0,[steel_legs.id,aluminium_legs.id])]
            })]
        })
        product_variant_ids=product_template.product_variant_ids
        #BoM1withcomponent_1
        self.env['mrp.bom'].create({
            'product_id':product_variant_ids[0].id,
            'product_tmpl_id':product_variant_ids[0].product_tmpl_id.id,
            'product_qty':1.0,
            'consumption':'flexible',
            'type':'phantom',
            'bom_line_ids':[(0,0,{'product_id':component_1.id,'product_qty':1})]
        })
        #BoM2withcomponent_2
        self.env['mrp.bom'].create({
            'product_id':product_variant_ids[1].id,
            'product_tmpl_id':product_variant_ids[1].product_tmpl_id.id,
            'product_qty':1.0,
            'consumption':'flexible',
            'type':'phantom',
            'bom_line_ids':[(0,0,{'product_id':component_2.id,'product_qty':1})]
        })
        partner=self.env['res.partner'].create({'name':'TestingMan'})
        so=self.env['sale.order'].create({
            'partner_id':partner.id,
        })
        #Createtheorderline
        self.env['sale.order.line'].create({
            'name':"Orderline",
            'product_id':product_variant_ids[0].id,
            'order_id':so.id,
        })
        so.action_confirm()
        so._action_cancel()
        so.action_draft()
        withForm(so)asso_form:
            withso_form.order_line.edit(0)asorder_line_change:
                #Theactualtest,thereshouldbenotracebackhere
                order_line_change.product_id=product_variant_ids[1]

    deftest_sale_mrp_kit_cost(self):
        """
         CheckthetotalcostofaKIT:
            #BoMofKitA:
                #-BoMType:Kit
                #-Quantity:1
                #-Components:
                #*1xComponentA(Cost:$6,QTY:1,UOM:Dozens)
                #*1xComponentB(Cost:$10,QTY:2,UOM:Unit)
            #costofKitA=(6*1*12)+(10*2)=$92
        """
        self.customer=self.env['res.partner'].create({
            'name':'customer'
        })
        
        self.kit_product=self._create_product('KitProduct','product',1.00)
        #Creatingcomponents
        self.component_a=self._create_product('ComponentA','product',1.00)
        self.component_a.product_tmpl_id.standard_price=6
        self.component_b=self._create_product('ComponentB','product',1.00)
        self.component_b.product_tmpl_id.standard_price=10
        
        cat=self.env['product.category'].create({
            'name':'fifo',
            'property_cost_method':'fifo'
        })
        self.kit_product.product_tmpl_id.categ_id=cat
        self.component_a.product_tmpl_id.categ_id=cat
        self.component_b.product_tmpl_id.categ_id=cat
        
        self.bom=self.env['mrp.bom'].create({
            'product_tmpl_id':self.kit_product.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'
        })
        
        self.env['mrp.bom.line'].create({
                'product_id':self.component_a.id,
                'product_qty':1.0,
                'bom_id':self.bom.id,
                'product_uom_id':self.env.ref('uom.product_uom_dozen').id,
        })
        self.env['mrp.bom.line'].create({
                'product_id':self.component_b.id,
                'product_qty':2.0,
                'bom_id':self.bom.id,
                'product_uom_id':self.env.ref('uom.product_uom_unit').id,
        })
    
        #CreateaSOwithoneunitofthekitproduct
        so=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'order_line':[
                (0,0,{
                    'name':self.kit_product.name,
                    'product_id':self.kit_product.id,
                    'product_uom_qty':1.0,
                    'product_uom':self.kit_product.uom_id.id,
                })],
        })
        bom=self.env['mrp.bom'].sudo()._bom_find(product=self.kit_product)
        so.action_confirm()
        line=so.order_line
        purchase_price=line.product_id.with_company(line.company_id)._compute_average_price(0,line.product_uom_qty,line.move_ids)
        self.assertEqual(purchase_price,92,"Thepurchasepricemustbethetotalcostofthecomponentsmultipliedbytheirunitofmeasure")

    deftest_qty_delivered_with_bom(self):
        """Checkthequantitydelivered,whenabomlinehasanonintegerquantity"""

        self.env['ir.model.data'].xmlid_to_object('product.decimal_product_uom').digits=5

        self.kit=self._create_product('Kit','product',0.00)
        self.comp=self._create_product('Component','product',0.00)

        #CreateBoMforKit
        bom_product_form=Form(self.env['mrp.bom'])
        bom_product_form.product_id=self.kit
        bom_product_form.product_tmpl_id=self.kit.product_tmpl_id
        bom_product_form.product_qty=1.0
        bom_product_form.type='phantom'
        withbom_product_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.comp
            bom_line.product_qty=0.08600
        self.bom=bom_product_form.save()


        self.customer=self.env['res.partner'].create({
            'name':'customer',
        })

        so=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'order_line':[
                (0,0,{
                    'name':self.kit.name,
                    'product_id':self.kit.id,
                    'product_uom_qty':10.0,
                    'product_uom':self.kit.uom_id.id,
                    'price_unit':1,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        self.assertTrue(so.picking_ids)
        self.assertEqual(so.order_line.qty_delivered,0)

        picking=so.picking_ids
        picking.move_lines.quantity_done=0.86000
        picking.button_validate()

        #Checksthedeliveryamount(mustbe10).
        self.assertEqual(so.order_line.qty_delivered,10)

    deftest_qty_delivered_with_bom_using_kit(self):
        """Checkthequantitydelivered,whenoneproductisakit
        andhisbomusesanotherproductthatisalsoakit"""

        self.kitA=self._create_product('KitA','consu',0.00)
        self.kitB=self._create_product('KitB','consu',0.00)
        self.compA=self._create_product('ComponentA','consu',0.00)
        self.compB=self._create_product('ComponentB','consu',0.00)

        #CreateBoMforKitB
        bom_product_formA=Form(self.env['mrp.bom'])
        bom_product_formA.product_id=self.kitB
        bom_product_formA.product_tmpl_id=self.kitB.product_tmpl_id
        bom_product_formA.product_qty=1.0
        bom_product_formA.type='phantom'
        withbom_product_formA.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.compA
            bom_line.product_qty=1
        withbom_product_formA.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.compB
            bom_line.product_qty=1
        self.bomA=bom_product_formA.save()

        #CreateBoMforKitA
        bom_product_formB=Form(self.env['mrp.bom'])
        bom_product_formB.product_id=self.kitA
        bom_product_formB.product_tmpl_id=self.kitA.product_tmpl_id
        bom_product_formB.product_qty=1.0
        bom_product_formB.type='phantom'
        withbom_product_formB.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.compA
            bom_line.product_qty=1
        withbom_product_formB.bom_line_ids.new()asbom_line:
            bom_line.product_id=self.kitB
            bom_line.product_qty=1
        self.bomB=bom_product_formB.save()

        self.customer=self.env['res.partner'].create({
            'name':'customer',
        })

        so=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'order_line':[
                (0,0,{
                    'name':self.kitA.name,
                    'product_id':self.kitA.id,
                    'product_uom_qty':1.0,
                    'product_uom':self.kitA.uom_id.id,
                    'price_unit':1,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        self.assertTrue(so.picking_ids)
        self.assertEqual(so.order_line.qty_delivered,0)

        picking=so.picking_ids
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()

        #Checksthedeliveryamount(mustbe1).
        self.assertEqual(so.order_line.qty_delivered,1)

    deftest_qty_delivered_with_bom_using_kit2(self):
        """Create2kitsproductsthathavecommoncomponentsandactivate2stepsdelivery
           Thencreateasaleorderwiththese2products,andputeverythinginapackin
           thefirststepofthedelivery.Aftertheshippingisdone,checkthedonequantity
           iscorrectforeachproducts.
        """

        wh=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        wh.write({'delivery_steps':'pick_ship'})

        kitAB=self._create_product('KitAB','product',0.00)
        kitABC=self._create_product('KitABC','product',0.00)
        compA=self._create_product('ComponentA','product',0.00)
        compB=self._create_product('ComponentB','product',0.00)
        compC=self._create_product('ComponentC','product',0.00)

        #CreateBoMforKitB
        bom_product_formA=Form(self.env['mrp.bom'])
        bom_product_formA.product_id=kitAB
        bom_product_formA.product_tmpl_id=kitAB.product_tmpl_id
        bom_product_formA.product_qty=1.0
        bom_product_formA.type='phantom'
        withbom_product_formA.bom_line_ids.new()asbom_line:
            bom_line.product_id=compA
            bom_line.product_qty=1
        withbom_product_formA.bom_line_ids.new()asbom_line:
            bom_line.product_id=compB
            bom_line.product_qty=1
        bom_product_formA.save()

        #CreateBoMforKitA
        bom_product_formB=Form(self.env['mrp.bom'])
        bom_product_formB.product_id=kitABC
        bom_product_formB.product_tmpl_id=kitABC.product_tmpl_id
        bom_product_formB.product_qty=1.0
        bom_product_formB.type='phantom'
        withbom_product_formB.bom_line_ids.new()asbom_line:
            bom_line.product_id=compA
            bom_line.product_qty=1
        withbom_product_formB.bom_line_ids.new()asbom_line:
            bom_line.product_id=compB
            bom_line.product_qty=1
        withbom_product_formB.bom_line_ids.new()asbom_line:
            bom_line.product_id=compC
            bom_line.product_qty=1
        bom_product_formB.save()

        customer=self.env['res.partner'].create({
            'name':'customer',
        })

        so=self.env['sale.order'].create({
            'partner_id':customer.id,
            'order_line':[
                (0,0,{
                    'name':kitAB.name,
                    'product_id':kitAB.id,
                    'product_uom_qty':1.0,
                    'product_uom':kitAB.uom_id.id,
                    'price_unit':1,
                    'tax_id':False,
                }),
                (0,0,{
                    'name':kitABC.name,
                    'product_id':kitABC.id,
                    'product_uom_qty':1.0,
                    'product_uom':kitABC.uom_id.id,
                    'price_unit':1,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        pick=so.picking_ids[0]
        ship=so.picking_ids[1]

        pick.move_lines[0].quantity_done=2
        pick.move_lines[1].quantity_done=2
        pick.move_lines[2].quantity_done=1

        pick.action_put_in_pack()
        pick.button_validate()

        ship.package_level_ids.write({'is_done':True})
        ship.package_level_ids._set_is_done()

        formoveinship.move_line_ids:
            self.assertEqual(move.product_uom_qty,move.qty_done,"Quantitydoneshouldbeequaltothequantityreservedinthemoveline")

    deftest_kit_in_delivery_slip(self):
        """
        Supposethisstructure:
        Saleorder:
            -Kit1withasalesdescription("test"):
                |-Compo1
            -Product1

        Thistestensuresthat,whendeliveringaKitproductwithasalesdescription,
        thedeliveryreportiscorrectlyprintedwithalltheproducts.
        """
        kit_1,component_1,product_1=self.env['product.product'].create([{
            'name':n,
            'type':'product',
        }fornin['Kit1','Compo1','Product1']])
        kit_1.description_sale="test"

        self.env['mrp.bom'].create([{
            'product_tmpl_id':kit_1.product_tmpl_id.id,
            'product_qty':1,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':component_1.id,'product_qty':1}),
            ],
        }])
        customer=self.env['res.partner'].create({
            'name':'customer',
        })
        so=self.env['sale.order'].create({
            'partner_id':customer.id,
            'order_line':[
                (0,0,{
                    'product_id':kit_1.id,
                    'product_uom_qty':1.0,
                }),
                (0,0,{
                    'product_id':product_1.id,
                    'product_uom_qty':1.0,
                })],
        })
        so.action_confirm()
        picking=so.picking_ids
        self.assertEqual(len(so.picking_ids.move_ids_without_package),2)
        picking.move_lines.quantity_done=1
        picking.button_validate()
        self.assertEqual(picking.state,'done')

        report=self.env['ir.actions.report']._get_report_from_name('stock.report_deliveryslip')
        html_report=report._render_qweb_html(picking.ids)[0].decode('utf-8').split('\n')
        keys=[
            "Kit1","Compo1",
            "Productsnotassociatedwithakit","Product1",
        ]
        forlineinhtml_report:
            ifnotkeys:
                break
            ifkeys[0]inline:
                keys=keys[1:]
        self.assertFalse(keys,"Allkeysshouldbeinthereportwiththedefinedorder")
