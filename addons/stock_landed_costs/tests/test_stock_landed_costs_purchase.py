#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importunittest
fromflectra.addons.stock_landed_costs.tests.commonimportTestStockLandedCostsCommon
fromflectra.addons.stock_landed_costs.tests.test_stockvaluationlayerimportTestStockValuationLCCommon
fromflectra.addons.stock_account.tests.test_stockvaluationimport_create_accounting_data

fromflectra.testsimporttagged,Form


@tagged('post_install','-at_install')
classTestLandedCosts(TestStockLandedCostsCommon):

    defsetUp(self):
        super(TestLandedCosts,self).setUp()
        #Createpickingincomingshipment
        self.picking_in=self.Picking.create({
            'partner_id':self.supplier_id,
            'picking_type_id':self.warehouse.in_type_id.id,
            'location_id':self.supplier_location_id,
            'location_dest_id':self.warehouse.lot_stock_id.id})
        self.Move.create({
            'name':self.product_refrigerator.name,
            'product_id':self.product_refrigerator.id,
            'product_uom_qty':5,
            'product_uom':self.product_refrigerator.uom_id.id,
            'picking_id':self.picking_in.id,
            'location_id':self.supplier_location_id,
            'location_dest_id':self.warehouse.lot_stock_id.id})
        self.Move.create({
            'name':self.product_oven.name,
            'product_id':self.product_oven.id,
            'product_uom_qty':10,
            'product_uom':self.product_oven.uom_id.id,
            'picking_id':self.picking_in.id,
            'location_id':self.supplier_location_id,
            'location_dest_id':self.warehouse.lot_stock_id.id})
        #Createpickingoutgoingshipment
        self.picking_out=self.Picking.create({
            'partner_id':self.customer_id,
            'picking_type_id':self.warehouse.out_type_id.id,
            'location_id':self.warehouse.lot_stock_id.id,
            'location_dest_id':self.customer_location_id})
        self.Move.create({
            'name':self.product_refrigerator.name,
            'product_id':self.product_refrigerator.id,
            'product_uom_qty':2,
            'product_uom':self.product_refrigerator.uom_id.id,
            'picking_id':self.picking_out.id,
            'location_id':self.warehouse.lot_stock_id.id,
            'location_dest_id':self.customer_location_id})

    deftest_00_landed_costs_on_incoming_shipment(self):
        """Testlandedcostonincomingshipment"""
        #
        #(A)Purchaseproduct

        #        Services          Quantity      Weight     Volume
        #        -----------------------------------------------------
        #        1.Refrigerator        5           10         1
        #        2.Oven                10          20         1.5

        #(B)Addsomecostsonpurchase

        #        Services          Amount    SplitMethod
        #        -------------------------------------------
        #        1.labour           10       ByEqual
        #        2.brokerage        150      ByQuantity
        #        3.transportation   250      ByWeight
        #        4.packaging        20       ByVolume

        self.landed_cost.categ_id.property_valuation='real_time'

        #Processincomingshipment
        income_ship=self._process_incoming_shipment()
        #Createlandedcosts
        stock_landed_cost=self._create_landed_costs({
            'equal_price_unit':10,
            'quantity_price_unit':150,
            'weight_price_unit':250,
            'volume_price_unit':20},income_ship)
        #Computelandedcosts
        stock_landed_cost.compute_landed_cost()

        valid_vals={
            'equal':5.0,
            'by_quantity_refrigerator':50.0,
            'by_quantity_oven':100.0,
            'by_weight_refrigerator':50.0,
            'by_weight_oven':200,
            'by_volume_refrigerator':5.0,
            'by_volume_oven':15.0}

        #Checkvaluationadjustmentlinerecognizedornot
        self._validate_additional_landed_cost_lines(stock_landed_cost,valid_vals)
        #Validatethelandedcost.
        stock_landed_cost.button_validate()
        self.assertTrue(stock_landed_cost.account_move_id,'Landedcostsshouldbeavailableaccountmovelines')
        account_entry=self.env['account.move.line'].read_group(
            [('move_id','=',stock_landed_cost.account_move_id.id)],['debit','credit','move_id'],['move_id'])[0]
        self.assertEqual(account_entry['debit'],account_entry['credit'],'Debitandcreditarenotequal')
        self.assertEqual(account_entry['debit'],430.0,'WrongAccountEntry')

    deftest_00_landed_costs_on_incoming_shipment_without_real_time(self):
        chart_of_accounts=self.env.company.chart_template_id
        generic_coa=self.env.ref('l10n_generic_coa.configurable_chart_template')
        ifchart_of_accounts!=generic_coa:
            raiseunittest.SkipTest('Skipthistestasitworksonlywith%s(%sloaded)'%(generic_coa.name,chart_of_accounts.name))
        """Testlandedcostonincomingshipment"""
        #
        #(A)Purchaseproduct

        #        Services          Quantity      Weight     Volume
        #        -----------------------------------------------------
        #        1.Refrigerator        5           10         1
        #        2.Oven                10          20         1.5

        #(B)Addsomecostsonpurchase

        #        Services          Amount    SplitMethod
        #        -------------------------------------------
        #        1.labour           10       ByEqual
        #        2.brokerage        150      ByQuantity
        #        3.transportation   250      ByWeight
        #        4.packaging        20       ByVolume

        self.product_refrigerator.write({"categ_id":self.categ_manual_periodic.id})
        self.product_oven.write({"categ_id":self.categ_manual_periodic.id})
        #Processincomingshipment
        income_ship=self._process_incoming_shipment()
        #Createlandedcosts
        stock_landed_cost=self._create_landed_costs({
            'equal_price_unit':10,
            'quantity_price_unit':150,
            'weight_price_unit':250,
            'volume_price_unit':20},income_ship)
        #Computelandedcosts
        stock_landed_cost.compute_landed_cost()

        valid_vals={
            'equal':5.0,
            'by_quantity_refrigerator':50.0,
            'by_quantity_oven':100.0,
            'by_weight_refrigerator':50.0,
            'by_weight_oven':200,
            'by_volume_refrigerator':5.0,
            'by_volume_oven':15.0}

        #Checkvaluationadjustmentlinerecognizedornot
        self._validate_additional_landed_cost_lines(stock_landed_cost,valid_vals)
        #Validatethelandedcost.
        stock_landed_cost.button_validate()
        self.assertFalse(stock_landed_cost.account_move_id)

    deftest_01_negative_landed_costs_on_incoming_shipment(self):
        """Testnegativelandedcostonincomingshipment"""
        #
        #(A)PurchaseProduct

        #        Services          Quantity      Weight     Volume
        #        -----------------------------------------------------
        #        1.Refrigerator        5           10         1
        #        2.Oven                10          20         1.5

        #(B)Salerefrigerator'spartofthequantity

        #(C)Addsomecostsonpurchase

        #        Services          Amount    SplitMethod
        #        -------------------------------------------
        #        1.labour           10       ByEqual
        #        2.brokerage        150      ByQuantity
        #        3.transportation   250      ByWeight
        #        4.packaging        20       ByVolume

        #(D)Decreasecostthatalreadyaddedonpurchase
        #        (applynegativeentry)

        #        Services          Amount    SplitMethod
        #        -------------------------------------------
        #        1.labour           -5       ByEqual
        #        2.brokerage        -50      ByQuantity
        #        3.transportation   -50      ByWeight
        #        4.packaging        -5       ByVolume

        self.landed_cost.categ_id.property_valuation='real_time'

        #Processincomingshipment
        income_ship=self._process_incoming_shipment()
        #Refrigeratoroutgoingshipment.
        self._process_outgoing_shipment()
        #Applylandedcostforincomingshipment.
        stock_landed_cost=self._create_landed_costs({
            'equal_price_unit':10,
            'quantity_price_unit':150,
            'weight_price_unit':250,
            'volume_price_unit':20},income_ship)
        #Computelandedcosts
        stock_landed_cost.compute_landed_cost()
        valid_vals={
            'equal':5.0,
            'by_quantity_refrigerator':50.0,
            'by_quantity_oven':100.0,
            'by_weight_refrigerator':50.0,
            'by_weight_oven':200.0,
            'by_volume_refrigerator':5.0,
            'by_volume_oven':15.0}
        #Checkvaluationadjustmentlinerecognizedornot
        self._validate_additional_landed_cost_lines(stock_landed_cost,valid_vals)
        #Validatethelandedcost.
        stock_landed_cost.button_validate()
        self.assertTrue(stock_landed_cost.account_move_id,'Landedcostsshouldbeavailableaccountmovelines')
        #Createnegativelandedcostforpreviouslyincomingshipment.
        stock_negative_landed_cost=self._create_landed_costs({
            'equal_price_unit':-5,
            'quantity_price_unit':-50,
            'weight_price_unit':-50,
            'volume_price_unit':-5},income_ship)
        #Computenegativelandedcosts
        stock_negative_landed_cost.compute_landed_cost()
        valid_vals={
            'equal':-2.5,
            'by_quantity_refrigerator':-16.67,
            'by_quantity_oven':-33.33,
            'by_weight_refrigerator':-10.00,
            'by_weight_oven':-40.00,
            'by_volume_refrigerator':-1.25,
            'by_volume_oven':-3.75}
        #Checkvaluationadjustmentlinerecognizedornot
        self._validate_additional_landed_cost_lines(stock_negative_landed_cost,valid_vals)
        #Validatethelandedcost.
        stock_negative_landed_cost.button_validate()
        self.assertEqual(stock_negative_landed_cost.state,'done','Negativelandedcostsshouldbeindonestate')
        self.assertTrue(stock_negative_landed_cost.account_move_id,'Landedcostsshouldbeavailableaccountmovelines')
        account_entry=self.env['account.move.line'].read_group(
            [('move_id','=',stock_negative_landed_cost.account_move_id.id)],['debit','credit','move_id'],['move_id'])[0]
        self.assertEqual(account_entry['debit'],account_entry['credit'],'Debitandcreditarenotequal')
        move_lines=[
            {'name':'splitbyvolume-MicrowaveOven',                   'debit':3.75, 'credit':0.0},
            {'name':'splitbyvolume-MicrowaveOven',                   'debit':0.0,  'credit':3.75},
            {'name':'splitbyweight-MicrowaveOven',                   'debit':40.0, 'credit':0.0},
            {'name':'splitbyweight-MicrowaveOven',                   'debit':0.0,  'credit':40.0},
            {'name':'splitbyquantity-MicrowaveOven',                 'debit':33.33,'credit':0.0},
            {'name':'splitbyquantity-MicrowaveOven',                 'debit':0.0,  'credit':33.33},
            {'name':'equalsplit-MicrowaveOven',                       'debit':2.5,  'credit':0.0},
            {'name':'equalsplit-MicrowaveOven',                       'debit':0.0,  'credit':2.5},
            {'name':'splitbyvolume-Refrigerator:2.0alreadyout',    'debit':0.5,  'credit':0.0},
            {'name':'splitbyvolume-Refrigerator:2.0alreadyout',    'debit':0.0,  'credit':0.5},
            {'name':'splitbyweight-Refrigerator:2.0alreadyout',    'debit':4.0,  'credit':0.0},
            {'name':'splitbyweight-Refrigerator:2.0alreadyout',    'debit':0.0,  'credit':4.0},
            {'name':'splitbyweight-Refrigerator',                     'debit':0.0,  'credit':10.0},
            {'name':'splitbyweight-Refrigerator',                     'debit':10.0, 'credit':0.0},
            {'name':'splitbyvolume-Refrigerator',                     'debit':0.0,  'credit':1.25},
            {'name':'splitbyvolume-Refrigerator',                     'debit':1.25, 'credit':0.0},
            {'name':'splitbyquantity-Refrigerator:2.0alreadyout',  'debit':6.67, 'credit':0.0},
            {'name':'splitbyquantity-Refrigerator:2.0alreadyout',  'debit':0.0,  'credit':6.67},
            {'name':'splitbyquantity-Refrigerator',                   'debit':16.67,'credit':0.0},
            {'name':'splitbyquantity-Refrigerator',                   'debit':0.0,  'credit':16.67},
            {'name':'equalsplit-Refrigerator:2.0alreadyout',        'debit':1.0,  'credit':0.0},
            {'name':'equalsplit-Refrigerator:2.0alreadyout',        'debit':0.0,  'credit':1.0},
            {'name':'equalsplit-Refrigerator',                         'debit':2.5,  'credit':0.0},
            {'name':'equalsplit-Refrigerator',                         'debit':0.0,  'credit':2.5}
        ]
        ifstock_negative_landed_cost.account_move_id.company_id.anglo_saxon_accounting:
            move_lines+=[
                {'name':'splitbyvolume-Refrigerator:2.0alreadyout',    'debit':0.5,  'credit':0.0},
                {'name':'splitbyvolume-Refrigerator:2.0alreadyout',    'debit':0.0,  'credit':0.5},
                {'name':'splitbyweight-Refrigerator:2.0alreadyout',    'debit':4.0,  'credit':0.0},
                {'name':'splitbyweight-Refrigerator:2.0alreadyout',    'debit':0.0,  'credit':4.0},
                {'name':'splitbyquantity-Refrigerator:2.0alreadyout',  'debit':6.67, 'credit':0.0},
                {'name':'splitbyquantity-Refrigerator:2.0alreadyout',  'debit':0.0,  'credit':6.67},
                {'name':'equalsplit-Refrigerator:2.0alreadyout',        'debit':1.0,  'credit':0.0},
                {'name':'equalsplit-Refrigerator:2.0alreadyout',        'debit':0.0,  'credit':1.0},
            ]
        self.assertRecordValues(
            sorted(stock_negative_landed_cost.account_move_id.line_ids,key=lambdad:(d['name'],d['debit'])),
            sorted(move_lines,key=lambdad:(d['name'],d['debit'])),
        )

    def_process_incoming_shipment(self):
        """Twoproductincomingshipment."""
        #Confirmincomingshipment.
        self.picking_in.action_confirm()
        #Transferincomingshipment
        res_dict=self.picking_in.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict.get('context'))).save()
        wizard.process()
        returnself.picking_in

    def_process_outgoing_shipment(self):
        """OneproductOutgoingshipment."""
        #Confirmoutgoingshipment.
        self.picking_out.action_confirm()
        #Productassigntooutgoingshipments
        self.picking_out.action_assign()
        #Transferpicking.

        res_dict=self.picking_out.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process()

    def_create_landed_costs(self,value,picking_in):
        returnself.LandedCost.create(dict(
            picking_ids=[(6,0,[picking_in.id])],
            account_journal_id=self.expenses_journal.id,
            cost_lines=[
                (0,0,{
                    'name':'equalsplit',
                    'split_method':'equal',
                    'price_unit':value['equal_price_unit'],
                    'product_id':self.landed_cost.id}),
                (0,0,{
                    'name':'splitbyquantity',
                    'split_method':'by_quantity',
                    'price_unit':value['quantity_price_unit'],
                    'product_id':self.brokerage_quantity.id}),
                (0,0,{
                    'name':'splitbyweight',
                    'split_method':'by_weight',
                    'price_unit':value['weight_price_unit'],
                    'product_id':self.transportation_weight.id}),
                (0,0,{
                    'name':'splitbyvolume',
                    'split_method':'by_volume',
                    'price_unit':value['volume_price_unit'],
                    'product_id':self.packaging_volume.id})
            ],
        ))

    def_validate_additional_landed_cost_lines(self,stock_landed_cost,valid_vals):
        forvaluationinstock_landed_cost.valuation_adjustment_lines:
            add_cost=valuation.additional_landed_cost
            split_method=valuation.cost_line_id.split_method
            product=valuation.move_id.product_id
            ifsplit_method=='equal':
                self.assertEqual(add_cost,valid_vals['equal'],self._error_message(valid_vals['equal'],add_cost))
            elifsplit_method=='by_quantity'andproduct==self.product_refrigerator:
                self.assertEqual(add_cost,valid_vals['by_quantity_refrigerator'],self._error_message(valid_vals['by_quantity_refrigerator'],add_cost))
            elifsplit_method=='by_quantity'andproduct==self.product_oven:
                self.assertEqual(add_cost,valid_vals['by_quantity_oven'],self._error_message(valid_vals['by_quantity_oven'],add_cost))
            elifsplit_method=='by_weight'andproduct==self.product_refrigerator:
                self.assertEqual(add_cost,valid_vals['by_weight_refrigerator'],self._error_message(valid_vals['by_weight_refrigerator'],add_cost))
            elifsplit_method=='by_weight'andproduct==self.product_oven:
                self.assertEqual(add_cost,valid_vals['by_weight_oven'],self._error_message(valid_vals['by_weight_oven'],add_cost))
            elifsplit_method=='by_volume'andproduct==self.product_refrigerator:
                self.assertEqual(add_cost,valid_vals['by_volume_refrigerator'],self._error_message(valid_vals['by_volume_refrigerator'],add_cost))
            elifsplit_method=='by_volume'andproduct==self.product_oven:
                self.assertEqual(add_cost,valid_vals['by_volume_oven'],self._error_message(valid_vals['by_volume_oven'],add_cost))

    def_error_message(self,actucal_cost,computed_cost):
        return'AdditionalLandedCostshouldbe%sinsteadof%s'%(actucal_cost,computed_cost)


@tagged('post_install','-at_install')
classTestLandedCostsWithPurchaseAndInv(TestStockValuationLCCommon):
    deftest_invoice_after_lc(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.price_diff_account=self.env['account.account'].create({
            'name':'pricediffaccount',
            'code':'pricediffaccount',
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
        })
        self.product1.property_account_creditor_price_difference=self.price_diff_account

        #CreatePO
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.env['res.partner'].create({'name':'vendor'})
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=self.product1
            po_line.product_qty=1
            po_line.price_unit=455.0
        order=po_form.save()
        order.button_confirm()

        #Receivethegoods
        receipt=order.picking_ids[0]
        receipt.move_lines.quantity_done=1
        receipt.button_validate()

        #CheckSVLandAML
        svl=self.env['stock.valuation.layer'].search([('stock_move_id','=',receipt.move_lines.id)])
        self.assertAlmostEqual(svl.value,455)
        aml=self.env['account.move.line'].search([('account_id','=',self.company_data['default_account_stock_valuation'].id)])
        self.assertAlmostEqual(aml.debit,455)

        #CreateandvalidateLC
        lc=self.env['stock.landed.cost'].create(dict(
            picking_ids=[(6,0,[receipt.id])],
            account_journal_id=self.stock_journal.id,
            cost_lines=[
                (0,0,{
                    'name':'equalsplit',
                    'split_method':'equal',
                    'price_unit':99,
                    'product_id':self.productlc1.id,
                }),
            ],
        ))
        lc.compute_landed_cost()
        lc.button_validate()

        #CheckLC,SVLandAML
        self.assertAlmostEqual(lc.valuation_adjustment_lines.final_cost,554)
        svl=self.env['stock.valuation.layer'].search([('stock_move_id','=',receipt.move_lines.id)],order='iddesc',limit=1)
        self.assertAlmostEqual(svl.value,99)
        aml=self.env['account.move.line'].search([('account_id','=',self.company_data['default_account_stock_valuation'].id)],order='iddesc',limit=1)
        self.assertAlmostEqual(aml.debit,99)

        #Createaninvoicewiththesameprice
        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=order.partner_id
        move_form.purchase_id=order
        move=move_form.save()
        move.action_post()

        #Checknothingwaspostedinthepricedifferenceaccount
        price_diff_aml=self.env['account.move.line'].search([('account_id','=',self.price_diff_account.id),('move_id','=',move.id)])
        self.assertEqual(len(price_diff_aml),0,"Nolineshouldhavebeengeneratedinthepricedifferenceaccount.")
