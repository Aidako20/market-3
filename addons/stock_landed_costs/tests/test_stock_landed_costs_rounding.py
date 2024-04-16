#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.stock_landed_costs.tests.commonimportTestStockLandedCostsCommon
fromflectra.testsimporttagged,Form


@tagged('post_install','-at_install')
classTestStockLandedCostsRounding(TestStockLandedCostsCommon):

    deftest_stock_landed_costs_rounding(self):
        #Inordertotesttheroundinginlandedcostsfeatureofstock,Icreate2landedcost

        #Defineundivisibleunits
        product_uom_unit_round_1=self.env.ref('uom.product_uom_unit')
        product_uom_unit_round_1.write({
            'name':'UndivisibleUnits',
            'rounding':1.0,
        })

        #Icreate2productswithdifferentcostpricesandconfigurethemforreal_time
        #valuationandrealpricecostingmethod
        product_landed_cost_3=self.env['product.product'].create({
            'name':"LCproduct3",
            'uom_id':product_uom_unit_round_1.id,
        })
        product_landed_cost_3.product_tmpl_id.categ_id.property_cost_method='fifo'
        product_landed_cost_3.product_tmpl_id.categ_id.property_stock_account_input_categ_id=self.company_data['default_account_expense']
        product_landed_cost_3.product_tmpl_id.categ_id.property_stock_account_output_categ_id=self.company_data['default_account_revenue']

        product_landed_cost_4=self.env['product.product'].create({
            'name':"LCproduct4",
            'uom_id':product_uom_unit_round_1.id,
        })
        product_landed_cost_4.product_tmpl_id.categ_id.property_cost_method='fifo'
        product_landed_cost_4.product_tmpl_id.categ_id.property_valuation='real_time'
        product_landed_cost_4.product_tmpl_id.categ_id.property_stock_account_input_categ_id=self.company_data['default_account_expense']
        product_landed_cost_4.product_tmpl_id.categ_id.property_stock_account_output_categ_id=self.company_data['default_account_revenue']

        picking_default_vals=self.env['stock.picking'].default_get(list(self.env['stock.picking'].fields_get()))

        #Icreate2pickingsmovingthoseproducts
        vals=dict(picking_default_vals,**{
            'name':'LC_pick_3',
            'picking_type_id':self.warehouse.in_type_id.id,
            'move_lines':[(0,0,{
                'product_id':product_landed_cost_3.id,
                'product_uom_qty':13,
                'product_uom':product_uom_unit_round_1.id,
                'location_id':self.ref('stock.stock_location_customers'),
                'location_dest_id':self.warehouse.lot_stock_id.id,
            })],
        })
        picking_landed_cost_3=self.env['stock.picking'].new(vals)
        picking_landed_cost_3.onchange_picking_type()
        picking_landed_cost_3.move_lines.onchange_product_id()
        picking_landed_cost_3.move_lines.name='move3'
        vals=picking_landed_cost_3._convert_to_write(picking_landed_cost_3._cache)
        picking_landed_cost_3=self.env['stock.picking'].create(vals)

        vals=dict(picking_default_vals,**{
            'name':'LC_pick_4',
            'picking_type_id':self.warehouse.in_type_id.id,
            'move_lines':[(0,0,{
                'product_id':product_landed_cost_4.id,
                'product_uom_qty':1,
                'product_uom':self.ref('uom.product_uom_dozen'),
                'location_id':self.ref('stock.stock_location_customers'),
                'location_dest_id':self.warehouse.lot_stock_id.id,
                'price_unit':17.00/12.00,
            })],
        })
        picking_landed_cost_4=self.env['stock.picking'].new(vals)
        picking_landed_cost_4.onchange_picking_type()
        picking_landed_cost_4.move_lines.onchange_product_id()
        picking_landed_cost_4.move_lines.name='move4'
        vals=picking_landed_cost_4._convert_to_write(picking_landed_cost_4._cache)
        picking_landed_cost_4=self.env['stock.picking'].create(vals)

        #WeperformallthetestsforLC_pick_3
        #IreceivepickingLC_pick_3,andcheckhowmanyquantsarecreated
        picking_landed_cost_3.move_lines.price_unit=1.0
        picking_landed_cost_3.action_confirm()
        picking_landed_cost_3.action_assign()
        picking_landed_cost_3._action_done()

        virtual_interior_design=self.env['product.product'].create({'name':'VirtualInteriorDesign'})

        #Icreatealandedcostforpicking3
        default_vals=self.env['stock.landed.cost'].default_get(list(self.env['stock.landed.cost'].fields_get()))
        default_vals.update({
            'picking_ids':[picking_landed_cost_3.id],
            'account_journal_id':self.expenses_journal,
            'cost_lines':[(0,0,{'product_id':virtual_interior_design.id})],
            'valuation_adjustment_lines':[],
        })
        stock_landed_cost_2=self.env['stock.landed.cost'].new(default_vals)
        stock_landed_cost_2.cost_lines.onchange_product_id()
        stock_landed_cost_2.cost_lines.name='equalsplit'
        stock_landed_cost_2.cost_lines.split_method='equal'
        stock_landed_cost_2.cost_lines.price_unit=15
        vals=stock_landed_cost_2._convert_to_write(stock_landed_cost_2._cache)
        stock_landed_cost_2=self.env['stock.landed.cost'].create(vals)

        #IcomputethelandedcostusingComputebutton
        stock_landed_cost_2.compute_landed_cost()

        #Icheckthevaluationadjustmentlines
        forvaluationinstock_landed_cost_2.valuation_adjustment_lines:
            self.assertEqual(valuation.additional_landed_cost,15)

        #Iconfirmthelandedcost
        stock_landed_cost_2.button_validate()

        #Icheckthatthelandedcostisnow"Closed"andthatithasanaccountingentry
        self.assertEqual(stock_landed_cost_2.state,'done')
        self.assertTrue(stock_landed_cost_2.account_move_id)

        #WeperformallthetestsforLC_pick_4
        #IreceivepickingLC_pick_4,andcheckhowmanyquantsarecreated
        picking_landed_cost_4.move_lines.price_unit=17.0/12.0
        picking_landed_cost_4.action_confirm()
        picking_landed_cost_4.action_assign()
        picking_landed_cost_4._action_done()

        #Icreatealandedcostforpicking4
        default_vals=self.env['stock.landed.cost'].default_get(list(self.env['stock.landed.cost'].fields_get()))
        default_vals.update({
            'picking_ids':[picking_landed_cost_4.id],
            'account_journal_id':self.expenses_journal,
            'cost_lines':[(0,0,{'product_id':virtual_interior_design.id})],
            'valuation_adjustment_lines':[],
        })
        stock_landed_cost_3=self.env['stock.landed.cost'].new(default_vals)
        stock_landed_cost_3.cost_lines.onchange_product_id()
        stock_landed_cost_3.cost_lines.name='equalsplit'
        stock_landed_cost_3.cost_lines.split_method='equal'
        stock_landed_cost_3.cost_lines.price_unit=11
        vals=stock_landed_cost_3._convert_to_write(stock_landed_cost_3._cache)
        stock_landed_cost_3=self.env['stock.landed.cost'].create(vals)

        #IcomputethelandedcostusingComputebutton
        stock_landed_cost_3.compute_landed_cost()

        #Icheckthevaluationadjustmentlines
        forvaluationinstock_landed_cost_3.valuation_adjustment_lines:
            self.assertEqual(valuation.additional_landed_cost,11)

        #Iconfirmthelandedcost
        stock_landed_cost_3.button_validate()

        #Icheckthatthelandedcostisnow"Closed"andthatithasanaccountingentry
        self.assertEqual(stock_landed_cost_3.state,'done')
        self.assertTrue(stock_landed_cost_3.account_move_id)

    deftest_stock_landed_costs_rounding_02(self):
        """Thelandedcostsshouldbecorrectlycomputed,evenwhenthedecimalaccuracy
        ofthedeciamlpriceisincreased."""
        self.env.ref("product.decimal_price").digits=4

        fifo_pc=self.env['product.category'].create({
            'name':'FifoCategory',
            'parent_id':self.env.ref("product.product_category_all").id,
            'property_valuation':'real_time',
            'property_cost_method':'fifo',
        })

        products=self.Product.create([{
            'name':'SuperProduct%s'%price,
            'categ_id':fifo_pc.id,
            'type':'product',
            'standard_price':price,
        }forpricein[0.91,0.93,75.17,20.54]])

        landed_product=self.Product.create({
            'name':'LandedCosts',
            'type':'service',
            'landed_cost_ok':True,
            'split_method_landed_cost':'by_quantity',
            'standard_price':1000.0,
        })

        po=self.env['purchase.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[(0,0,{
                'product_id':product.id,
                'product_qty':qty,
                'price_unit':product.standard_price,
            })forproduct,qtyinzip(products,[6,6,3,6])]
        })
        po.button_confirm()

        res_dict=po.picking_ids.button_validate()
        validate_wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict.get('context'))).save()
        validate_wizard.process()

        lc_form=Form(self.LandedCost)
        lc_form.picking_ids.add(po.picking_ids)
        withlc_form.cost_lines.new()asline:
            line.product_id=landed_product
        lc=lc_form.save()
        lc.compute_landed_cost()

        self.assertEqual(sum(lc.valuation_adjustment_lines.mapped('additional_landed_cost')),1000.0)

    deftest_stock_landed_costs_rounding_03(self):
        """
        StorableAVCOproduct
        Receive:
            5@5
            5@8
            5@7
            20@7.33
        Addlandedcostof$5toeachreceipt(exceptthefirstone)
        Deliver:
            23
            2
            10
        Attheend,theSVLvalueshouldbezero
        """
        self.product_a.type='product'
        self.product_a.categ_id.property_cost_method='average'

        stock_location=self.warehouse.lot_stock_id
        supplier_location_id=self.ref('stock.stock_location_suppliers')
        customer_location_id=self.ref('stock.stock_location_customers')

        receipts=self.env['stock.picking'].create([{
            'picking_type_id':self.warehouse.in_type_id.id,
            'location_id':supplier_location_id,
            'location_dest_id':stock_location.id,
            'move_lines':[(0,0,{
                'name':self.product_a.name,
                'product_id':self.product_a.id,
                'price_unit':price,
                'product_uom':self.product_a.uom_id.id,
                'product_uom_qty':qty,
                'location_id':supplier_location_id,
                'location_dest_id':stock_location.id,
            })]
        }forqty,pricein[
            (5,5.0),
            (5,8.0),
            (5,7.0),
            (20,7.33),
        ]])

        receipts.action_confirm()
        forminreceipts.move_lines:
            m.quantity_done=m.product_uom_qty
        receipts.button_validate()

        landed_costs=self.env['stock.landed.cost'].create([{
            'picking_ids':[(6,0,picking.ids)],
            'account_journal_id':self.expenses_journal.id,
            'cost_lines':[(0,0,{
                'name':'equalsplit',
                'split_method':'equal',
                'price_unit':5.0,
                'product_id':self.landed_cost.id
            })],
        }forpickinginreceipts[1:]])
        landed_costs.compute_landed_cost()
        landed_costs.button_validate()

        self.assertEqual(self.product_a.standard_price,7.47)

        deliveries=self.env['stock.picking'].create([{
            'picking_type_id':self.warehouse.out_type_id.id,
            'location_id':stock_location.id,
            'location_dest_id':customer_location_id,
            'move_lines':[(0,0,{
                'name':self.product_a.name,
                'product_id':self.product_a.id,
                'product_uom':self.product_a.uom_id.id,
                'product_uom_qty':qty,
                'location_id':stock_location.id,
                'location_dest_id':customer_location_id,
            })]
        }forqtyin[23,2,10]])

        deliveries.action_confirm()
        formindeliveries.move_lines:
            m.quantity_done=m.product_uom_qty
        deliveries.button_validate()

        self.assertEqual(self.product_a.value_svl,0)
