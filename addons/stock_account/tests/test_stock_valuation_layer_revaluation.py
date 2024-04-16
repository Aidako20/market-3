#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError
fromflectra.testsimportForm
fromflectra.addons.stock_account.tests.test_stockvaluationimport_create_accounting_data
fromflectra.addons.stock_account.tests.test_stockvaluationlayerimportTestStockValuationCommon


classTestStockValuationLayerRevaluation(TestStockValuationCommon):
    @classmethod
    defsetUpClass(cls):
        super(TestStockValuationLayerRevaluation,cls).setUpClass()
        cls.stock_input_account,cls.stock_output_account,cls.stock_valuation_account,cls.expense_account,cls.stock_journal=_create_accounting_data(cls.env)
        cls.product1.write({
            'property_account_expense_id':cls.expense_account.id,
        })
        cls.product1.categ_id.write({
            'property_valuation':'real_time',
            'property_stock_account_input_categ_id':cls.stock_input_account.id,
            'property_stock_account_output_categ_id':cls.stock_output_account.id,
            'property_stock_valuation_account_id':cls.stock_valuation_account.id,
            'property_stock_journal':cls.stock_journal.id,
        })

        cls.product1.categ_id.property_valuation='real_time'

    deftest_stock_valuation_layer_revaluation_avco(self):
        self.product1.categ_id.property_cost_method='average'
        context={
            'default_product_id':self.product1.id,
            'default_company_id':self.env.company.id,
            'default_added_value':0.0
        }
        #Quantityofproduct1iszero,raise
        withself.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context(context)).save()

        self._make_in_move(self.product1,10,unit_cost=2)
        self._make_in_move(self.product1,10,unit_cost=4)

        self.assertEqual(self.product1.standard_price,3)
        self.assertEqual(self.product1.quantity_svl,20)

        old_layers=self.env['stock.valuation.layer'].search([('product_id','=',self.product1.id)],order="create_datedesc,iddesc")

        self.assertEqual(len(old_layers),2)
        self.assertEqual(old_layers[0].remaining_value,40)

        revaluation_wizard=Form(self.env['stock.valuation.layer.revaluation'].with_context(context))
        revaluation_wizard.added_value=20
        revaluation_wizard.account_id=self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        #Checkstandardpricechange
        self.assertEqual(self.product1.standard_price,4)
        self.assertEqual(self.product1.quantity_svl,20)

        #Checkthecreationofstock.valuation.layer
        new_layer=self.env['stock.valuation.layer'].search([('product_id','=',self.product1.id)],order="create_datedesc,iddesc",limit=1)
        self.assertEqual(new_layer.value,20)

        #Checktheremaingvalueofcurrentlayers
        self.assertEqual(old_layers[0].remaining_value,50)
        self.assertEqual(sum(slv.remaining_valueforslvinold_layers),80)

        #Checkaccountmove
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertEqual(len(new_layer.account_move_id.line_ids),2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")),20)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")),20)

        credit_lines=[lforlinnew_layer.account_move_id.line_idsifl.credit>0]
        self.assertEqual(len(credit_lines),1)
        self.assertEqual(credit_lines[0].account_id.id,self.stock_valuation_account.id)

    deftest_stock_valuation_layer_revaluation_avco_rounding(self):
        self.product1.categ_id.property_cost_method='average'
        context={
            'default_product_id':self.product1.id,
            'default_company_id':self.env.company.id,
            'default_added_value':0.0
        }
        #Quantityofproduct1iszero,raise
        withself.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context(context)).save()

        self._make_in_move(self.product1,1,unit_cost=1)
        self._make_in_move(self.product1,1,unit_cost=1)
        self._make_in_move(self.product1,1,unit_cost=1)

        self.assertEqual(self.product1.standard_price,1)
        self.assertEqual(self.product1.quantity_svl,3)

        old_layers=self.env['stock.valuation.layer'].search([('product_id','=',self.product1.id)],order="create_datedesc,iddesc")

        self.assertEqual(len(old_layers),3)
        self.assertEqual(old_layers[0].remaining_value,1)

        revaluation_wizard=Form(self.env['stock.valuation.layer.revaluation'].with_context(context))
        revaluation_wizard.added_value=1
        revaluation_wizard.account_id=self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        #Checkstandardpricechange
        self.assertEqual(self.product1.standard_price,1.33)
        self.assertEqual(self.product1.quantity_svl,3)

        #Checkthecreationofstock.valuation.layer
        new_layer=self.env['stock.valuation.layer'].search([('product_id','=',self.product1.id)],order="create_datedesc,iddesc",limit=1)
        self.assertEqual(new_layer.value,1)

        #Checktheremaingvalueofcurrentlayers
        self.assertEqual(sum(slv.remaining_valueforslvinold_layers),4)
        self.assertTrue(1.34inold_layers.mapped("remaining_value"))

        #Checkaccountmove
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertEqual(len(new_layer.account_move_id.line_ids),2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")),1)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")),1)

        credit_lines=[lforlinnew_layer.account_move_id.line_idsifl.credit>0]
        self.assertEqual(len(credit_lines),1)
        self.assertEqual(credit_lines[0].account_id.id,self.stock_valuation_account.id)

    deftest_stock_valuation_layer_revaluation_avco_rounding_2_digits(self):
        """
        Checkthattheroundingofthenewprice(cost)isequivalenttotheroundingofthestandardprice(cost)
        Thecheckisdoneindirectlyviathelayersvaluations.
        Ifcorrect=>roundingmethodiscorrecttoo
        """
        self.product1.categ_id.property_cost_method='average'

        self.env['decimal.precision'].search([
            ('name','=','ProductPrice'),
        ]).digits=2
        self.product1.write({'standard_price':0})

        #FirstMove
        self.product1.write({'standard_price':0.022})
        self._make_in_move(self.product1,10000)

        self.assertEqual(self.product1.standard_price,0.02)
        self.assertEqual(self.product1.quantity_svl,10000)

        layer=self.product1.stock_valuation_layer_ids
        self.assertEqual(layer.value,200)

        #SecondMove
        self.product1.write({'standard_price':0.053})

        self.assertEqual(self.product1.standard_price,0.05)
        self.assertEqual(self.product1.quantity_svl,10000)

        layers=self.product1.stock_valuation_layer_ids
        self.assertEqual(layers[0].value,200)
        self.assertEqual(layers[1].value,300)

    deftest_stock_valuation_layer_revaluation_avco_rounding_5_digits(self):
        """
        Checkthattheroundingofthenewprice(cost)isequivalenttotheroundingofthestandardprice(cost)
        Thecheckisdoneindirectlyviathelayersvaluations.
        Ifcorrect=>roundingmethodiscorrecttoo
        """
        self.product1.categ_id.property_cost_method='average'

        self.env['decimal.precision'].search([
            ('name','=','ProductPrice'),
        ]).digits=5

        #FirstMove
        self.product1.write({'standard_price':0.00875})
        self._make_in_move(self.product1,10000)

        self.assertEqual(self.product1.standard_price,0.00875)
        self.assertEqual(self.product1.quantity_svl,10000)

        layer=self.product1.stock_valuation_layer_ids
        self.assertEqual(layer.value,87.5)

        #SecondMove
        self.product1.write({'standard_price':0.00975})

        self.assertEqual(self.product1.standard_price,0.00975)
        self.assertEqual(self.product1.quantity_svl,10000)

        layers=self.product1.stock_valuation_layer_ids
        self.assertEqual(layers[0].value,87.5)
        self.assertEqual(layers[1].value,10)

    deftest_stock_valuation_layer_revaluation_fifo(self):
        self.product1.categ_id.property_cost_method='fifo'
        context={
            'default_product_id':self.product1.id,
            'default_company_id':self.env.company.id,
            'default_added_value':0.0
        }
        #Quantityofproduct1iszero,raise
        withself.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context(context)).save()

        self._make_in_move(self.product1,10,unit_cost=2)
        self._make_in_move(self.product1,10,unit_cost=4)

        self.assertEqual(self.product1.standard_price,2)
        self.assertEqual(self.product1.quantity_svl,20)

        old_layers=self.env['stock.valuation.layer'].search([('product_id','=',self.product1.id)],order="create_datedesc,iddesc")

        self.assertEqual(len(old_layers),2)
        self.assertEqual(old_layers[0].remaining_value,40)

        revaluation_wizard=Form(self.env['stock.valuation.layer.revaluation'].with_context(context))
        revaluation_wizard.added_value=20
        revaluation_wizard.account_id=self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        self.assertEqual(self.product1.standard_price,3)

        #Checkthecreationofstock.valuation.layer
        new_layer=self.env['stock.valuation.layer'].search([('product_id','=',self.product1.id)],order="create_datedesc,iddesc",limit=1)
        self.assertEqual(new_layer.value,20)

        #Checktheremaingvalueofcurrentlayers
        self.assertEqual(old_layers[0].remaining_value,50)
        self.assertEqual(sum(slv.remaining_valueforslvinold_layers),80)

        #Checkaccountmove
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertTrue(len(new_layer.account_move_id.line_ids),2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")),20)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")),20)

        credit_lines=[lforlinnew_layer.account_move_id.line_idsifl.credit>0]
        self.assertEqual(len(credit_lines),1)
