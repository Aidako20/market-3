#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimporttagged,Form


@tagged('post_install','-at_install')
classTestStockLandedCostsMrp(ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestStockLandedCostsMrp,cls).setUpClass()
        #References
        cls.supplier_id=cls.env['res.partner'].create({'name':'MyTestSupplier'}).id
        cls.customer_id=cls.env['res.partner'].create({'name':'MyTestCustomer'}).id
        cls.picking_type_in_id=cls.env.ref('stock.picking_type_in')
        cls.picking_type_out_id=cls.env.ref('stock.picking_type_out')
        cls.supplier_location_id=cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location_id=cls.company_data['default_warehouse'].lot_stock_id
        cls.customer_location_id=cls.env.ref('stock.stock_location_customers')
        cls.categ_all=cls.env.ref('product.product_category_all')
        #Createproductrefrigerator&oven
        cls.product_component1=cls.env['product.product'].create({
            'name':'Component1',
            'type':'product',
            'standard_price':1.0,
            'categ_id':cls.categ_all.id
        })
        cls.product_component2=cls.env['product.product'].create({
            'name':'Component2',
            'type':'product',
            'standard_price':2.0,
            'categ_id':cls.categ_all.id
        })
        cls.product_refrigerator=cls.env['product.product'].create({
            'name':'Refrigerator',
            'type':'product',
            'categ_id':cls.categ_all.id
        })
        cls.uom_unit=cls.env.ref('uom.product_uom_unit')
        cls.bom_refri=cls.env['mrp.bom'].create({
            'product_id':cls.product_refrigerator.id,
            'product_tmpl_id':cls.product_refrigerator.product_tmpl_id.id,
            'product_uom_id':cls.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
        })
        cls.bom_refri_line1=cls.env['mrp.bom.line'].create({
            'bom_id':cls.bom_refri.id,
            'product_id':cls.product_component1.id,
            'product_qty':3,
        })
        cls.bom_refri_line2=cls.env['mrp.bom.line'].create({
            'bom_id':cls.bom_refri.id,
            'product_id':cls.product_component2.id,
            'product_qty':1,
        })
        #Warehouses
        cls.warehouse_1=cls.env['stock.warehouse'].create({
            'name':'BaseWarehouse',
            'reception_steps':'one_step',
            'delivery_steps':'ship_only',
            'code':'BWH'})

        cls.product_refrigerator.categ_id.property_cost_method='fifo'
        cls.product_refrigerator.categ_id.property_valuation='real_time'
        cls.product_refrigerator.categ_id.property_stock_account_input_categ_id=cls.company_data['default_account_stock_in']
        cls.product_refrigerator.categ_id.property_stock_account_output_categ_id=cls.company_data['default_account_stock_out']

        #Createservicetypeproduct1.Labour2.Brokerage3.Transportation4.Packaging
        cls.landed_cost=cls.env['product.product'].create({
            'name':'LandedCost',
            'type':'service',
        })
        cls.allow_user=cls.env['res.users'].with_context({'no_reset_password':True}).create({
            'name':"Adviser",
            'login':"fm",
            'email':"accountmanager@yourcompany.com",
            'groups_id':[(6,0,[cls.env.ref('account.group_account_manager').id,cls.env.ref('mrp.group_mrp_user').id,cls.env.ref('stock.group_stock_manager').id])]
        })

    deftest_landed_cost_on_mrp(self):
        inventory=self.env['stock.inventory'].create({
            'name':'Initialinventory',
            'line_ids':[(0,0,{
                'product_id':self.product_component1.id,
                'product_uom_id':self.product_component1.uom_id.id,
                'product_qty':500,
                'location_id':self.warehouse_1.lot_stock_id.id
            }),(0,0,{
                'product_id':self.product_component2.id,
                'product_uom_id':self.product_component2.uom_id.id,
                'product_qty':500,
                'location_id':self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_start()
        inventory.action_validate()

        man_order_form=Form(self.env['mrp.production'].with_user(self.allow_user))
        man_order_form.product_id=self.product_refrigerator
        man_order_form.bom_id=self.bom_refri
        man_order_form.product_qty=2.0
        man_order=man_order_form.save()

        self.assertEqual(man_order.state,'draft',"Productionordershouldbeindraftstate.")
        man_order.action_confirm()
        self.assertEqual(man_order.state,'confirmed',"Productionordershouldbeinconfirmedstate.")

        #checkproductionmove
        production_move=man_order.move_finished_ids
        self.assertEqual(production_move.product_id,self.product_refrigerator)

        first_move=man_order.move_raw_ids.filtered(lambdamove:move.product_id==self.product_component1)
        self.assertEqual(first_move.product_qty,6.0)
        first_move=man_order.move_raw_ids.filtered(lambdamove:move.product_id==self.product_component2)
        self.assertEqual(first_move.product_qty,2.0)

        #produceproduct
        mo_form=Form(man_order.with_user(self.allow_user))
        mo_form.qty_producing=2
        man_order=mo_form.save()


        man_order.button_mark_done()

        landed_cost=Form(self.env['stock.landed.cost'].with_user(self.allow_user)).save()
        landed_cost.target_model='manufacturing'

        self.assertTrue(man_order.idinlanded_cost.allowed_mrp_production_ids.ids)
        landed_cost.mrp_production_ids=[(6,0,[man_order.id])]
        landed_cost.cost_lines=[(0,0,{'product_id':self.landed_cost.id,'price_unit':5.0,'split_method':'equal'})]

        landed_cost.button_validate()

        self.assertEqual(landed_cost.state,'done')
        self.assertTrue(landed_cost.account_move_id)
        #Linktoonelayerofproduct_refrigerator
        self.assertEqual(len(landed_cost.stock_valuation_layer_ids),1)
        self.assertEqual(landed_cost.stock_valuation_layer_ids.product_id,self.product_refrigerator)
        self.assertEqual(landed_cost.stock_valuation_layer_ids.value,5.0)

    deftest_landed_cost_on_mrp_02(self):
        """
            Testthatauserwhohasmanageraccesstostockcancreateandvalidatealandedcostlinked
            toaManufacturingorderwithouttheneedforMRPaccess
        """
        #Createauserwithonlymanageraccesstostock
        stock_manager=self.env['res.users'].with_context({'no_reset_password':True}).create({
            'name':"StockManager",
            'login':"test",
            'email':"test@test.com",
            'groups_id':[(6,0,[self.env.ref('stock.group_stock_manager').id])]
        })
        #Makesomestockandreserve
        self.env['stock.quant']._update_available_quantity(self.product_component1,self.warehouse_1.lot_stock_id,10)
        self.env['stock.quant']._update_available_quantity(self.product_component2,self.warehouse_1.lot_stock_id,10)

        #CreateandconfirmaMOwithauserwhohasaccesstoMRP
        man_order_form=Form(self.env['mrp.production'].with_user(self.allow_user))
        man_order_form.product_id=self.product_refrigerator
        man_order_form.bom_id=self.bom_refri
        man_order_form.product_qty=1.0
        man_order=man_order_form.save()
        man_order.action_confirm()
        #produceproduct
        man_order_form.qty_producing=1
        man_order_form.save()
        man_order.button_mark_done()

        #Createthelandedcostwiththestock_manageruser
        landed_cost=Form(self.env['stock.landed.cost'].with_user(stock_manager)).save()
        landed_cost.target_model='manufacturing'

        #CheckthattheMOcanbeselectedbythestock_mangeruser
        self.assertTrue(man_order.idinlanded_cost.allowed_mrp_production_ids.ids)
        landed_cost.mrp_production_ids=[(6,0,[man_order.id])]

        #Checkthathecanvalidatethelandedcostwithoutanaccesserror
        landed_cost.with_user(stock_manager).button_validate()
        self.assertEqual(landed_cost.state,'done')
