#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectra.exceptionsimportUserError
fromflectra.fieldsimportDatetime
fromflectra.tests.commonimportForm,SavepointCase


def_create_accounting_data(env):
    """Createtheaccountsandjournalsusedinstockvaluation.

    :paramenv:environmentusedtocreatetherecords
    :return:aninputaccount,anoutputaccount,avaluationaccount,anexpenseaccount,astockjournal
    """
    stock_input_account=env['account.account'].create({
        'name':'StockInput',
        'code':'StockIn',
        'user_type_id':env.ref('account.data_account_type_current_assets').id,
        'reconcile':True,
    })
    stock_output_account=env['account.account'].create({
        'name':'StockOutput',
        'code':'StockOut',
        'user_type_id':env.ref('account.data_account_type_current_assets').id,
        'reconcile':True,
    })
    stock_valuation_account=env['account.account'].create({
        'name':'StockValuation',
        'code':'StockValuation',
        'user_type_id':env.ref('account.data_account_type_current_assets').id,
        'reconcile':True,
    })
    expense_account=env['account.account'].create({
        'name':'ExpenseAccount',
        'code':'ExpenseAccount',
        'user_type_id':env.ref('account.data_account_type_expenses').id,
        'reconcile':True,
    })
    stock_journal=env['account.journal'].create({
        'name':'StockJournal',
        'code':'STJTEST',
        'type':'general',
    })
    returnstock_input_account,stock_output_account,stock_valuation_account,expense_account,stock_journal


classTestStockValuation(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super(TestStockValuation,cls).setUpClass()
        cls.stock_location=cls.env.ref('stock.stock_location_stock')
        cls.customer_location=cls.env.ref('stock.stock_location_customers')
        cls.supplier_location=cls.env.ref('stock.stock_location_suppliers')
        cls.partner=cls.env['res.partner'].create({'name':'xxx'})
        cls.owner1=cls.env['res.partner'].create({'name':'owner1'})
        cls.uom_unit=cls.env.ref('uom.product_uom_unit')
        cls.product1=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'default_code':'prda',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.product2=cls.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.inventory_user=cls.env['res.users'].create({
            'name':'PaulinePoivraisselle',
            'login':'pauline',
            'email':'p.p@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[cls.env.ref('stock.group_stock_user').id])]
        })

        cls.stock_input_account,cls.stock_output_account,cls.stock_valuation_account,cls.expense_account,cls.stock_journal=_create_accounting_data(cls.env)
        cls.product1.categ_id.property_valuation='real_time'
        cls.product2.categ_id.property_valuation='real_time'
        cls.product1.write({
            'property_account_expense_id':cls.expense_account.id,
        })
        cls.product1.categ_id.write({
            'property_stock_account_input_categ_id':cls.stock_input_account.id,
            'property_stock_account_output_categ_id':cls.stock_output_account.id,
            'property_stock_valuation_account_id':cls.stock_valuation_account.id,
            'property_stock_journal':cls.stock_journal.id,
        })

    def_get_stock_input_move_lines(self):
        returnself.env['account.move.line'].search([
            ('account_id','=',self.stock_input_account.id),
        ],order='date,id')

    def_get_stock_output_move_lines(self):
        returnself.env['account.move.line'].search([
            ('account_id','=',self.stock_output_account.id),
        ],order='date,id')

    def_get_stock_valuation_move_lines(self):
        returnself.env['account.move.line'].search([
            ('account_id','=',self.stock_valuation_account.id),
        ],order='date,id')


    def_make_in_move(self,product,quantity,unit_cost=None):
        """Helpertocreateandvalidateareceiptmove.
        """
        unit_cost=unit_costorproduct.standard_price
        in_move=self.env['stock.move'].create({
            'name':'in%sunits@%sperunit'%(str(quantity),str(unit_cost)),
            'product_id':product.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.env.ref('stock.stock_location_stock').id,
            'product_uom':self.env.ref('uom.product_uom_unit').id,
            'product_uom_qty':quantity,
            'price_unit':unit_cost,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })

        in_move._action_confirm()
        in_move._action_assign()
        in_move.move_line_ids.qty_done=quantity
        in_move._action_done()

        returnin_move.with_context(svl=True)

    def_make_out_move(self,product,quantity):
        """Helpertocreateandvalidateadeliverymove.
        """
        out_move=self.env['stock.move'].create({
            'name':'out%sunits'%str(quantity),
            'product_id':product.id,
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id,
            'product_uom':self.env.ref('uom.product_uom_unit').id,
            'product_uom_qty':quantity,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        out_move._action_confirm()
        out_move._action_assign()
        out_move.move_line_ids.qty_done=quantity
        out_move._action_done()
        returnout_move.with_context(svl=True)

    deftest_realtime(self):
        """Stockmovesupdatestockvaluewithproductxcostprice,
        pricechangeupdatesthestockvaluebasedoncurrentstocklevel.
        """
        #Enter10productswhilepriceis5.0
        self.product1.standard_price=5.0
        move1=self.env['stock.move'].create({
            'name':'IN10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        #Setpriceto6.0
        self.product1.standard_price=6.0
        stock_aml,price_change_aml=self._get_stock_valuation_move_lines()
        self.assertEqual(stock_aml.debit,50)
        self.assertEqual(price_change_aml.debit,10)
        self.assertEqual(price_change_aml.ref,'prda')
        self.assertEqual(price_change_aml.product_id,self.product1)

    deftest_fifo_perpetual_1(self):
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #receive10units@10.00perunit
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'IN10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        #stock_accountvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)

        #accountvaluesformove1
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),1)
        move1_input_aml=input_aml[-1]
        self.assertEqual(move1_input_aml.debit,0)
        self.assertEqual(move1_input_aml.credit,100)

        valuation_aml=self._get_stock_valuation_move_lines()
        move1_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),1)
        self.assertEqual(move1_valuation_aml.debit,100)
        self.assertEqual(move1_valuation_aml.credit,0)
        self.assertEqual(move1_valuation_aml.product_id.id,self.product1.id)
        self.assertEqual(move1_valuation_aml.quantity,10)
        self.assertEqual(move1_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        self.assertEqual(len(output_aml),0)

        #---------------------------------------------------------------------
        #receive10units@8.00perunit
        #---------------------------------------------------------------------
        move2=self.env['stock.move'].create({
            'name':'IN10units@8.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':8.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        #stock_accountvaluesformove2
        self.assertEqual(move2.stock_valuation_layer_ids.unit_cost,8.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move2.stock_valuation_layer_ids.value,80.0)

        #accountvaluesformove2
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),2)
        move2_input_aml=input_aml[-1]
        self.assertEqual(move2_input_aml.debit,0)
        self.assertEqual(move2_input_aml.credit,80)

        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),2)
        self.assertEqual(move2_valuation_aml.debit,80)
        self.assertEqual(move2_valuation_aml.credit,0)
        self.assertEqual(move2_valuation_aml.product_id.id,self.product1.id)
        self.assertEqual(move2_valuation_aml.quantity,10)
        self.assertEqual(move2_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        self.assertEqual(len(output_aml),0)

        #---------------------------------------------------------------------
        #sale3units
        #---------------------------------------------------------------------
        move3=self.env['stock.move'].create({
            'name':'Sale3units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=3.0
        move3._action_done()

        #stock_accountvaluesformove3
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmove
        self.assertEqual(move3.stock_valuation_layer_ids.value,-30.0) #took3itemsfrommove1@10.00perunit

        #accountvaluesformove3
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),2)

        valuation_aml=self._get_stock_valuation_move_lines()
        move3_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),3)
        self.assertEqual(move3_valuation_aml.debit,0)
        self.assertEqual(move3_valuation_aml.credit,30)
        self.assertEqual(move3_valuation_aml.product_id.id,self.product1.id)
        #FIXMEsle
        #self.assertEqual(move3_valuation_aml.quantity,-3)
        self.assertEqual(move3_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        move3_output_aml=output_aml[-1]
        self.assertEqual(len(output_aml),1)
        self.assertEqual(move3_output_aml.debit,30)
        self.assertEqual(move3_output_aml.credit,0)

        #---------------------------------------------------------------------
        #Increasereceivedquantityofmove1from10to12,itshouldcreate
        #anewstocklayeratthetopofthequeue.
        #---------------------------------------------------------------------
        move1.quantity_done=12

        #stock_accountvaluesformove3
        self.assertEqual(move1.stock_valuation_layer_ids.sorted()[-1].unit_cost,10.0)
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('remaining_qty')),9.0)
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('value')),120.0) #move1isnow10@10+2@10

        #accountvaluesformove1
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),3)
        move1_correction_input_aml=input_aml[-1]
        self.assertEqual(move1_correction_input_aml.debit,0)
        self.assertEqual(move1_correction_input_aml.credit,20)

        valuation_aml=self._get_stock_valuation_move_lines()
        move1_correction_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),4)
        self.assertEqual(move1_correction_valuation_aml.debit,20)
        self.assertEqual(move1_correction_valuation_aml.credit,0)
        self.assertEqual(move1_correction_valuation_aml.product_id.id,self.product1.id)
        self.assertEqual(move1_correction_valuation_aml.quantity,2)
        self.assertEqual(move1_correction_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        self.assertEqual(len(output_aml),1)

        #---------------------------------------------------------------------
        #Sale9units,theunitsavailablefromthepreviousincreasearenotsent
        #immediatelyasthenewlayerisatthetopofthequeue.
        #---------------------------------------------------------------------
        move4=self.env['stock.move'].create({
            'name':'Sale9units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':9.0,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=9.0
        move4._action_done()

        #stock_accountvaluesformove4
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmove
        self.assertEqual(move4.stock_valuation_layer_ids.value,-86.0) #took9itemsfrommove1@10.00perunit

        #accountvaluesformove4
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),3)

        valuation_aml=self._get_stock_valuation_move_lines()
        move4_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),5)
        self.assertEqual(move4_valuation_aml.debit,0)
        self.assertEqual(move4_valuation_aml.credit,86)
        self.assertEqual(move4_valuation_aml.product_id.id,self.product1.id)
        #FIXMEsle
        #self.assertEqual(move4_valuation_aml.quantity,-9)
        self.assertEqual(move4_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        move4_output_aml=output_aml[-1]
        self.assertEqual(len(output_aml),2)
        self.assertEqual(move4_output_aml.debit,86)
        self.assertEqual(move4_output_aml.credit,0)

        #---------------------------------------------------------------------
        #Sale20units,wefallinnegativestockfor10units.Thesesare
        #valuedatthelastFIFOcostandthetotalisnegative.
        #---------------------------------------------------------------------
        move5=self.env['stock.move'].create({
            'name':'Sale20units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':20.0,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=20.0
        move5._action_done()

        #stock_accountvaluesformove5
        #(took8fromthesecondreceiptand2fromtheincreaseofthefirstreceipt)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,-10.0)
        self.assertEqual(move5.stock_valuation_layer_ids.value,-184.0)

        #accountvaluesformove5
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),3)

        valuation_aml=self._get_stock_valuation_move_lines()
        move5_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),6)
        self.assertEqual(move5_valuation_aml.debit,0)
        self.assertEqual(move5_valuation_aml.credit,184)
        self.assertEqual(move5_valuation_aml.product_id.id,self.product1.id)
        #self.assertEqual(move5_valuation_aml.quantity,-20)
        self.assertEqual(move5_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        move5_output_aml=output_aml[-1]
        self.assertEqual(len(output_aml),3)
        self.assertEqual(move5_output_aml.debit,184)
        self.assertEqual(move5_output_aml.credit,0)

        #---------------------------------------------------------------------
        #Receive10units@12.00tocounterbalancethenegative,thevacuum
        #willbecalleddirectly:10@10shouldberevalued10@12
        #---------------------------------------------------------------------
        move6=self.env['stock.move'].create({
            'name':'IN10units@12.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':12.0,
        })
        move6._action_confirm()
        move6._action_assign()
        move6.move_line_ids.qty_done=10.0
        move6._action_done()

        #stock_accountvaluesformove6
        self.assertEqual(move6.stock_valuation_layer_ids.unit_cost,12.0)
        self.assertEqual(move6.stock_valuation_layer_ids.remaining_qty,0.0) #alreadyconsumedbythenextvacuum
        self.assertEqual(move6.stock_valuation_layer_ids.value,120)

        #vacuumaml,10@10shouldhavebeen10@12,getridof20
        valuation_aml=self._get_stock_valuation_move_lines()
        vacuum_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),8)
        self.assertEqual(vacuum_valuation_aml.balance,-20)
        self.assertEqual(vacuum_valuation_aml.product_id.id,self.product1.id)
        self.assertEqual(vacuum_valuation_aml.quantity,0)
        self.assertEqual(vacuum_valuation_aml.product_uom_id.id,self.uom_unit.id)

        output_aml=self._get_stock_output_move_lines()
        vacuum_output_aml=output_aml[-1]
        self.assertEqual(len(output_aml),4)
        self.assertEqual(vacuum_output_aml.balance,20)

        #---------------------------------------------------------------------
        #Editmove6,receiveless:2innegativestock
        #---------------------------------------------------------------------
        move6.quantity_done=8

        #stock_accountvaluesformove6
        self.assertEqual(move6.stock_valuation_layer_ids.sorted()[-1].remaining_qty,-2)
        self.assertEqual(move6.stock_valuation_layer_ids.sorted()[-1].value,-20)

        #accountvaluesformove1
        input_aml=self._get_stock_input_move_lines()
        move6_correction_input_aml=input_aml[-1]
        self.assertEqual(move6_correction_input_aml.debit,20)
        self.assertEqual(move6_correction_input_aml.credit,0)

        valuation_aml=self._get_stock_valuation_move_lines()
        move6_correction_valuation_aml=valuation_aml[-1]
        self.assertEqual(move6_correction_valuation_aml.debit,0)
        self.assertEqual(move6_correction_valuation_aml.credit,20)
        self.assertEqual(move6_correction_valuation_aml.product_id.id,self.product1.id)
        #FIXMEsle
        #self.assertEqual(move6_correction_valuation_aml.quantity,-2)
        self.assertEqual(move6_correction_valuation_aml.product_uom_id.id,self.uom_unit.id)

        #-----------------------------------------------------------
        #receive4tocounterbalancenow
        #-----------------------------------------------------------
        move7=self.env['stock.move'].create({
            'name':'IN4units@15.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':4.0,
            'price_unit':15.0,
        })
        move7._action_confirm()
        move7._action_assign()
        move7.move_line_ids.qty_done=4.0
        move7._action_done()

        #accountvaluesaftervacuum
        input_aml=self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml),7)
        move6_correction2_input_aml=input_aml[-1]
        self.assertEqual(move6_correction2_input_aml.debit,10)
        self.assertEqual(move6_correction2_input_aml.credit,0)

        valuation_aml=self._get_stock_valuation_move_lines()
        move6_correction2_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),11)
        self.assertEqual(move6_correction2_valuation_aml.debit,0)
        self.assertEqual(move6_correction2_valuation_aml.credit,10)
        self.assertEqual(move6_correction2_valuation_aml.product_id.id,self.product1.id)
        self.assertEqual(move6_correction2_valuation_aml.quantity,0)
        self.assertEqual(move6_correction_valuation_aml.product_uom_id.id,self.uom_unit.id)

        #---------------------------------------------------------------------
        #Ending
        #---------------------------------------------------------------------
        self.assertEqual(self.product1.quantity_svl,2)
        self.assertEqual(self.product1.value_svl,30)
        #checkonaccountingentries
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),30)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),380)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),380)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),350)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),320)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

    deftest_fifo_perpetual_2(self):
        """Normalfifoflow(nonegativehandling)"""
        #http://accountingexplained.com/financial/inventories/fifo-method
        self.product1.categ_id.property_cost_method='fifo'

        #BeginningInventory:68units@15.00perunit
        move1=self.env['stock.move'].create({
            'name':'68units@15.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':68.0,
            'price_unit':15,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=68.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,1020.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,68.0)

        #Purchase140units@15.50perunit
        move2=self.env['stock.move'].create({
            'name':'140units@15.50perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':140.0,
            'price_unit':15.50,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=140.0
        move2._action_done()

        self.assertEqual(move2.stock_valuation_layer_ids.value,2170.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,68.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,140.0)

        #Sale94units@19.00perunit
        move3=self.env['stock.move'].create({
            'name':'Sale94units@19.00perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':94.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=94.0
        move3._action_done()


        #note:it'llhavetoget68unitsfromthefirstbatchand26fromthesecondone
        #soitsvalueshouldbe-((68*15)+(26*15.5))=-1423
        self.assertEqual(move3.stock_valuation_layer_ids.value,-1423.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,114)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

        #Purchase40units@16.00perunit
        move4=self.env['stock.move'].create({
            'name':'140units@15.50perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':40.0,
            'price_unit':16,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=40.0
        move4._action_done()

        self.assertEqual(move4.stock_valuation_layer_ids.value,640.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,114)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,40.0)

        #Purchase78units@16.50perunit
        move5=self.env['stock.move'].create({
            'name':'Purchase78units@16.50perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':78.0,
            'price_unit':16.5,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=78.0
        move5._action_done()

        self.assertEqual(move5.stock_valuation_layer_ids.value,1287.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,114)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,40.0)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,78.0)

        #Sale116units@19.50perunit
        move6=self.env['stock.move'].create({
            'name':'Sale116units@19.50perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':116.0,
        })
        move6._action_confirm()
        move6._action_assign()
        move6.move_line_ids.qty_done=116.0
        move6._action_done()

        #note:it'llhavetoget114unitsfromthemove2and2frommove4
        #soitsvalueshouldbe-((114*15.5)+(2*16))=1735
        self.assertEqual(move6.stock_valuation_layer_ids.value,-1799.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,38.0)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,78.0)
        self.assertEqual(move6.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

        #Sale62units@21perunit
        move7=self.env['stock.move'].create({
            'name':'Sale62units@21perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':62.0,
        })
        move7._action_confirm()
        move7._action_assign()
        move7.move_line_ids.qty_done=62.0
        move7._action_done()

        #note:it'llhavetoget38unitsfromthemove4and24frommove5
        #soitsvalueshouldbe-((38*16)+(24*16.5))=608+396
        self.assertEqual(move7.stock_valuation_layer_ids.value,-1004.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,54.0)
        self.assertEqual(move6.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move7.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

        #send10unitsinourtransitlocation,thevalorisationshouldnotbeimpacted
        transit_location=self.env['stock.location'].search([
            ('company_id','=',self.env.company.id),
            ('usage','=','transit'),
            ('active','=',False)
        ],limit=1)
        transit_location.active=True
        move8=self.env['stock.move'].create({
            'name':'Send10unitsintransit',
            'location_id':self.stock_location.id,
            'location_dest_id':transit_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move8._action_confirm()
        move8._action_assign()
        move8.move_line_ids.qty_done=10.0
        move8._action_done()

        self.assertEqual(move8.stock_valuation_layer_ids.value,0.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,54.0)
        self.assertEqual(move6.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move7.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move8.stock_valuation_layer_ids.remaining_qty,0.0) #unusedininternalmoves

        #Sale10units@16.5perunit
        move9=self.env['stock.move'].create({
            'name':'Sale10units@16.5perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move9._action_confirm()
        move9._action_assign()
        move9.move_line_ids.qty_done=10.0
        move9._action_done()

        #note:it'llhavetoget10unitsfrommove5soitsvalueshould
        #be-(10*16.50)=-165
        self.assertEqual(move9.stock_valuation_layer_ids.value,-165.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,44.0)
        self.assertEqual(move6.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move7.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move8.stock_valuation_layer_ids.remaining_qty,0.0) #unusedininternalmoves
        self.assertEqual(move9.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

    deftest_fifo_perpetual_3(self):
        """Normalfifoflow(nonegativehandling)"""
        self.product1.categ_id.property_cost_method='fifo'

        #in10@100
        move1=self.env['stock.move'].create({
            'name':'in10@100',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':100,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,1000.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)

        #in10@80
        move2=self.env['stock.move'].create({
            'name':'in10@80',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':80,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        self.assertEqual(move2.stock_valuation_layer_ids.value,800.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,10.0)

        #out15
        move3=self.env['stock.move'].create({
            'name':'out15',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=15.0
        move3._action_done()


        #note:it'llhavetoget10unitsfrommove1and5frommove2
        #soitsvalueshouldbe-((10*100)+(5*80))=-1423
        self.assertEqual(move3.stock_valuation_layer_ids.value,-1400.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,5)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

        #in5@60
        move4=self.env['stock.move'].create({
            'name':'in5@60',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
            'price_unit':60,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=5.0
        move4._action_done()

        self.assertEqual(move4.stock_valuation_layer_ids.value,300.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,5)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,5.0)

        #out7
        move5=self.env['stock.move'].create({
            'name':'out7',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':7.0,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=7.0
        move5._action_done()

        #note:it'llhavetoget5unitsfromthemove2and2frommove4
        #soitsvalueshouldbe-((5*80)+(2*60))=520
        self.assertEqual(move5.stock_valuation_layer_ids.value,-520.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,3.0)
        self.assertEqual(move5.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

    deftest_fifo_perpetual_4(self):
        """Fifoandreturnhandling."""
        self.product1.categ_id.property_cost_method='fifo'

        #in8@10
        move1=self.env['stock.move'].create({
            'name':'in8@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':8.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=8.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,80.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,8.0)

        #in4@16
        move2=self.env['stock.move'].create({
            'name':'in4@16',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':4.0,
            'price_unit':16,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=4.0
        move2._action_done()


        self.assertEqual(move2.stock_valuation_layer_ids.value,64)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,4.0)

        #out10
        out_pick=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':self.env['res.partner'].search([],limit=1).id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move3=self.env['stock.move'].create({
            'name':'out10',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'picking_id':out_pick.id,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=10.0
        move3._action_done()


        #note:it'llhavetoget8unitsfrommove1and2frommove2
        #soitsvalueshouldbe-((8*10)+(2*16))=-116
        self.assertEqual(move3.stock_valuation_layer_ids.value,-112.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,2)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves

        #in2@6
        move4=self.env['stock.move'].create({
            'name':'in2@6',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'price_unit':6,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=2.0
        move4._action_done()

        self.assertEqual(move4.stock_valuation_layer_ids.value,12.0)

        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,2)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinoutmoves
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty,2.0)

        self.assertEqual(self.product1.standard_price,16)

        #return
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=out_pick.ids,active_id=out_pick.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity=1.0#Returnonly2
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done=1.0
        return_pick.with_user(self.inventory_user)._action_done()

        self.assertEqual(self.product1.standard_price,16)

        self.assertAlmostEqual(return_pick.move_lines.stock_valuation_layer_ids.unit_cost,11.2)

    deftest_fifo_negative_1(self):
        """Sendproductsthatyoudonothave.Valuethefirstoutgoingmovetothestandard
        price,receiveinmultipletimesthedeliveredquantityandrun_fifo_vacuumtocompensate.
        """
        self.product1.categ_id.property_cost_method='fifo'

        #Weexpecttheusertosetmanuallysetastandardpricetoitsproductsifitsfirst
        #transferissendingproductsthathedoesn'thave.
        self.product1.product_tmpl_id.standard_price=8.0

        #---------------------------------------------------------------------
        #Send50unitsyoudon'thave
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'50out',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':50.0,
            'price_unit':0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':50.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,-400.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,-50.0) #normallyunusedinoutmoves,butasitmovednegativestockwemarkit
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,8)

        #accountvaluesformove1
        valuation_aml=self._get_stock_valuation_move_lines()
        move1_valuation_aml=valuation_aml[-1]
        self.assertEqual(move1_valuation_aml.debit,0)
        self.assertEqual(move1_valuation_aml.credit,400)
        output_aml=self._get_stock_output_move_lines()
        move1_output_aml=output_aml[-1]
        self.assertEqual(move1_output_aml.debit,400)
        self.assertEqual(move1_output_aml.credit,0)

        #---------------------------------------------------------------------
        #Receive40units@15
        #---------------------------------------------------------------------
        move2=self.env['stock.move'].create({
            'name':'40in@15',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':40.0,
            'price_unit':15.0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':40.0,
            })]
        })
        move2._action_confirm()
        move2._action_done()

        #stockvaluesformove2
        self.assertEqual(move2.stock_valuation_layer_ids.value,600.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0)
        self.assertEqual(move2.stock_valuation_layer_ids.unit_cost,15.0)

        #---------------------------------------------------------------------
        #Thevacuumran
        #---------------------------------------------------------------------
        #accountvaluesaftervacuum
        valuation_aml=self._get_stock_valuation_move_lines()
        vacuum1_valuation_aml=valuation_aml[-1]
        self.assertEqual(vacuum1_valuation_aml.debit,0)
        #280wascreditedmoreinvaluation(wecompensated40itemshere,soinitially40were
        #valuedat8->320increditbutnowweactuallysent40@15=600,sothedifferenceis
        #280morecredited)
        self.assertEqual(vacuum1_valuation_aml.credit,280)
        output_aml=self._get_stock_output_move_lines()
        vacuum1_output_aml=output_aml[-1]
        self.assertEqual(vacuum1_output_aml.debit,280)
        self.assertEqual(vacuum1_output_aml.credit,0)

        #---------------------------------------------------------------------
        #Receive20units@25
        #---------------------------------------------------------------------
        move3=self.env['stock.move'].create({
            'name':'20in@25',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':20.0,
            'price_unit':25.0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':20.0
            })]
        })
        move3._action_confirm()
        move3._action_done()

        #---------------------------------------------------------------------
        #Thevacuumran
        #---------------------------------------------------------------------

        #stockvaluesformove1-3
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('value')),-850.0) #40@15+10@25
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('remaining_qty')),0.0)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')),600.0)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('remaining_qty')),0.0)
        self.assertEqual(sum(move3.stock_valuation_layer_ids.mapped('value')),500.0)
        self.assertEqual(sum(move3.stock_valuation_layer_ids.mapped('remaining_qty')),10.0)

        #accountvaluesaftervacuum
        valuation_aml=self._get_stock_valuation_move_lines()
        vacuum2_valuation_aml=valuation_aml[-1]
        self.assertEqual(vacuum2_valuation_aml.debit,0)
        #thereisstill10@8tocompensatewith10@25->170tocreditmoreinthevaluationaccount
        self.assertEqual(vacuum2_valuation_aml.credit,170)
        output_aml=self._get_stock_output_move_lines()
        vacuum2_output_aml=output_aml[-1]
        self.assertEqual(vacuum2_output_aml.debit,170)
        self.assertEqual(vacuum2_output_aml.credit,0)

        #---------------------------------------------------------------------
        #Ending
        #---------------------------------------------------------------------
        self.assertEqual(self.product1.quantity_svl,10)
        self.assertEqual(self.product1.value_svl,250)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),1100)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),1100)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),850)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),850)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

    deftest_fifo_negative_2(self):
        """Receives10units,sendmore,theextraquantityshouldbevaluedatthelastfifo
        price,runningthevacuumshouldnotdoanything.Receive2unitsatthepricethetwo
        extraunitsweresent,checkthatnoaccountingentriesarecreated.
        """
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #Receive10@10
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'10in',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)

        #accountvaluesformove1
        valuation_aml=self._get_stock_valuation_move_lines()
        move1_valuation_aml=valuation_aml[-1]
        self.assertEqual(move1_valuation_aml.debit,100)
        self.assertEqual(move1_valuation_aml.credit,0)
        input_aml=self._get_stock_input_move_lines()
        move1_input_aml=input_aml[-1]
        self.assertEqual(move1_input_aml.debit,0)
        self.assertEqual(move1_input_aml.credit,100)

        self.assertEqual(len(move1.account_move_ids),1)

        #---------------------------------------------------------------------
        #Send12
        #---------------------------------------------------------------------
        move2=self.env['stock.move'].create({
            'name':'12out(2negative)',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12.0,
            'price_unit':0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':12.0,
            })]
        })
        move2._action_confirm()
        move2._action_done()

        #stockvaluesformove2
        self.assertEqual(move2.stock_valuation_layer_ids.value,-120.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,-2.0)

        #accountvaluesformove2
        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(move2_valuation_aml.debit,0)
        self.assertEqual(move2_valuation_aml.credit,120)
        output_aml=self._get_stock_output_move_lines()
        move2_output_aml=output_aml[-1]
        self.assertEqual(move2_output_aml.debit,120)
        self.assertEqual(move2_output_aml.credit,0)

        self.assertEqual(len(move2.account_move_ids),1)

        #---------------------------------------------------------------------
        #Runthevacuum
        #---------------------------------------------------------------------
        self.product1._run_fifo_vacuum()

        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)
        self.assertEqual(move2.stock_valuation_layer_ids.value,-120.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,-2.0)

        self.assertEqual(len(move1.account_move_ids),1)
        self.assertEqual(len(move2.account_move_ids),1)

        self.assertEqual(self.product1.quantity_svl,-2)
        self.assertEqual(self.product1.value_svl,-20)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),100)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),100)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),120)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),120)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

        #Nowreceiveexactlytheextraunitsatexactlythepricesent,no
        #accountingentriesshouldbecreatedafterthevacuum.
        #---------------------------------------------------------------------
        #Receive2@10
        #---------------------------------------------------------------------
        move3=self.env['stock.move'].create({
            'name':'10in',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':2.0,
            })]
        })
        move3._action_confirm()
        move3._action_done()

        #---------------------------------------------------------------------
        #Ending
        #---------------------------------------------------------------------
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')),-120.0)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('remaining_qty')),0)
        self.assertEqual(move3.stock_valuation_layer_ids.value,20)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move3.stock_valuation_layer_ids.unit_cost,10.0)

        self.assertEqual(len(move1.account_move_ids),1)
        self.assertEqual(len(move2.account_move_ids),1)
        self.assertEqual(len(move3.account_move_ids),1) #thecreatedaccountmoveisduetothereceipt

        #nothingshouldhavechangedintheaccountingregardingtheoutput
        self.assertEqual(self.product1.quantity_svl,0)
        self.assertEqual(self.product1.value_svl,0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),120)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),120)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),120)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),120)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

    deftest_fifo_negative_3(self):
        """Receives10units,send10units,thensendmore:theextraquantityshouldbevalued
        atthelastfifoprice,runningthevacuumshouldnotdoanything.
        """
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #Receive10@10
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'10in',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)

        #accountvaluesformove1
        valuation_aml=self._get_stock_valuation_move_lines()
        move1_valuation_aml=valuation_aml[-1]
        self.assertEqual(move1_valuation_aml.debit,100)
        self.assertEqual(move1_valuation_aml.credit,0)
        input_aml=self._get_stock_input_move_lines()
        move1_input_aml=input_aml[-1]
        self.assertEqual(move1_input_aml.debit,0)
        self.assertEqual(move1_input_aml.credit,100)

        self.assertEqual(len(move1.account_move_ids),1)

        #---------------------------------------------------------------------
        #Send10
        #---------------------------------------------------------------------
        move2=self.env['stock.move'].create({
            'name':'10out',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move2._action_confirm()
        move2._action_done()

        #stockvaluesformove2
        self.assertEqual(move2.stock_valuation_layer_ids.value,-100.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0.0)

        #accountvaluesformove2
        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(move2_valuation_aml.debit,0)
        self.assertEqual(move2_valuation_aml.credit,100)
        output_aml=self._get_stock_output_move_lines()
        move2_output_aml=output_aml[-1]
        self.assertEqual(move2_output_aml.debit,100)
        self.assertEqual(move2_output_aml.credit,0)

        self.assertEqual(len(move2.account_move_ids),1)

        #---------------------------------------------------------------------
        #Send21
        #---------------------------------------------------------------------
        #FIXMEslelastfifopricenotupdatedontheproduct?
        move3=self.env['stock.move'].create({
            'name':'10in',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':21.0,
            'price_unit':0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':21.0,
            })]
        })
        move3._action_confirm()
        move3._action_done()

        #stockvaluesformove3
        self.assertEqual(move3.stock_valuation_layer_ids.value,-210.0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,-21.0)

        #accountvaluesformove3
        valuation_aml=self._get_stock_valuation_move_lines()
        move3_valuation_aml=valuation_aml[-1]
        self.assertEqual(move3_valuation_aml.debit,0)
        self.assertEqual(move3_valuation_aml.credit,210)
        output_aml=self._get_stock_output_move_lines()
        move3_output_aml=output_aml[-1]
        self.assertEqual(move3_output_aml.debit,210)
        self.assertEqual(move3_output_aml.credit,0)

        self.assertEqual(len(move3.account_move_ids),1)

        #---------------------------------------------------------------------
        #Runthevacuum
        #---------------------------------------------------------------------
        self.product1._run_fifo_vacuum()
        self.assertEqual(len(move3.account_move_ids),1)

        #thevacuumshouldn'tdoanythinginthiscase
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)
        self.assertEqual(move2.stock_valuation_layer_ids.value,-100.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move3.stock_valuation_layer_ids.value,-210.0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,-21.0)

        self.assertEqual(len(move1.account_move_ids),1)
        self.assertEqual(len(move2.account_move_ids),1)
        self.assertEqual(len(move3.account_move_ids),1)

        #---------------------------------------------------------------------
        #Ending
        #---------------------------------------------------------------------
        self.assertEqual(self.product1.quantity_svl,-21)
        self.assertEqual(self.product1.value_svl,-210)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),100)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),100)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),310)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),310)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

    deftest_fifo_add_move_in_done_picking_1(self):
        """Theflowis:

        product2stdprice=20
        IN0110@10product1
        IN0110@20product2
        IN01correction10@20->11@20(product2)
        DO0111product2
        DO021product2
        DO02correction1->2(negativestock)
        IN032@30product2
        vacuum
        """
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #Receive10@10
        #---------------------------------------------------------------------
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
        })

        move1=self.env['stock.move'].create({
            'picking_id':receipt.id,
            'name':'10in',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)

        #---------------------------------------------------------------------
        #Addastockmove,receive10@20ofanotherproduct
        #---------------------------------------------------------------------
        self.product2.categ_id.property_cost_method='fifo'
        self.product2.standard_price=20
        move2=self.env['stock.move'].create({
            'picking_id':receipt.id,
            'name':'10in',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product2.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'move_line_ids':[(0,0,{
                'product_id':self.product2.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move2._action_done()

        self.assertEqual(move2.stock_valuation_layer_ids.value,200.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move2.stock_valuation_layer_ids.unit_cost,20.0)

        self.assertEqual(self.product1.quantity_svl,10)
        self.assertEqual(self.product1.value_svl,100)
        self.assertEqual(self.product2.quantity_svl,10)
        self.assertEqual(self.product2.value_svl,200)

        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),300)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),0)

        #---------------------------------------------------------------------
        #Editthepreviousstockmove,receive11
        #---------------------------------------------------------------------
        move2.quantity_done=11

        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')),220.0) #aftercorrection,themoveshouldbevaluedat11@20
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('remaining_qty')),11.0)
        self.assertEqual(move2.stock_valuation_layer_ids.sorted()[-1].unit_cost,20.0)

        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),320)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),0)

        #---------------------------------------------------------------------
        #Send11product2
        #---------------------------------------------------------------------
        delivery=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'partner_id':self.partner.id,
            'picking_type_id':self.env.ref('stock.picking_type_out').id,
        })
        move3=self.env['stock.move'].create({
            'picking_id':delivery.id,
            'name':'11out',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product2.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':11.0,
            'move_line_ids':[(0,0,{
                'product_id':self.product2.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':11.0,
            })]
        })

        move3._action_confirm()
        move3._action_done()

        self.assertEqual(move3.stock_valuation_layer_ids.value,-220.0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertEqual(move3.stock_valuation_layer_ids.unit_cost,20.0)
        self.assertEqual(self.product2.qty_available,0)
        self.assertEqual(self.product2.quantity_svl,0)

        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),320)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),220)

        #---------------------------------------------------------------------
        #Addonemoveofproduct2,this'llmakesomenegativestock.
        #---------------------------------------------------------------------

        #FIXME:uncommentwhennegativestockishandled
        #move4=self.env['stock.move'].create({
        #   'picking_id':delivery.id,
        #   'name':'1out',
        #   'location_id':self.stock_location.id,
        #   'location_dest_id':self.customer_location.id,
        #   'product_id':self.product2.id,
        #   'product_uom':self.uom_unit.id,
        #   'product_uom_qty':1.0,
        #   'state':'done', #simulatedefault_getoverride
        #   'move_line_ids':[(0,0,{
        #       'product_id':self.product2.id,
        #       'location_id':self.stock_location.id,
        #       'location_dest_id':self.customer_location.id,
        #       'product_uom_id':self.uom_unit.id,
        #       'qty_done':1.0,
        #   })]
        #})
        #self.assertEqual(move4.value,-20.0)
        #self.assertEqual(move4.remaining_qty,-1.0)
        #self.assertEqual(move4.price_unit,-20.0)

        #self.assertEqual(self.product2.qty_available,-1)

        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),320)
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),240)

        ##---------------------------------------------------------------------
        ##editthecreatedmove,add1
        ##---------------------------------------------------------------------
        #move4.quantity_done=2

        #self.assertEqual(self.product2.qty_available,-2)
        #self.assertEqual(move4.value,-40.0)
        #self.assertEqual(move4.remaining_qty,-2.0)
        #self.assertEqual(move4.price_unit,-20.0)

        #self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        #self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),320)#10*10+11*20
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),320)
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),260)
        #self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),260)
        #self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

        #self.env['stock.move']._run_fifo_vacuum()

        #self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        #self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),320)#10*10+11*20
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),320)
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),260)
        #self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),260)
        #self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

        ##---------------------------------------------------------------------
        ##receive2products2@30
        ##---------------------------------------------------------------------
        #move5=self.env['stock.move'].create({
        #   'picking_id':receipt.id,
        #   'name':'10in',
        #   'location_id':self.supplier_location.id,
        #   'location_dest_id':self.stock_location.id,
        #   'product_id':self.product2.id,
        #   'product_uom':self.uom_unit.id,
        #   'product_uom_qty':2.0,
        #   'price_unit':30,
        #   'move_line_ids':[(0,0,{
        #       'product_id':self.product2.id,
        #       'location_id':self.supplier_location.id,
        #       'location_dest_id':self.stock_location.id,
        #       'product_uom_id':self.uom_unit.id,
        #       'qty_done':2.0,
        #   })]
        #})
        #move5._action_confirm()
        #move5._action_done()

        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),380)
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),260)

        ##---------------------------------------------------------------------
        ##runvacuum
        ##---------------------------------------------------------------------
        #self.env['stock.move']._run_fifo_vacuum()

        #self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        #self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),380)#10*10+11*20
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),380)
        #self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),280)#260/
        #self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),280)
        #self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

        #self.assertEqual(self.product2.qty_available,0)
        #self.assertEqual(self.product2.stock_value,0)
        #self.assertEqual(move4.remaining_value,0)
        #self.assertEqual(move4.value,-60) #aftercorrection,themoveisvalued-(2*30)

    deftest_fifo_add_moveline_in_done_move_1(self):
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #Receive10@10
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'10in',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)

        self.assertEqual(len(move1.account_move_ids),1)

        #---------------------------------------------------------------------
        #Addanewmovelinetoreceive10more
        #---------------------------------------------------------------------
        self.assertEqual(len(move1.move_line_ids),1)
        self.env['stock.move.line'].create({
            'move_id':move1.id,
            'product_id':move1.product_id.id,
            'qty_done':10,
            'product_uom_id':move1.product_uom.id,
            'location_id':move1.location_id.id,
            'location_dest_id':move1.location_dest_id.id,
        })
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('value')),200.0)
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('remaining_qty')),20.0)
        self.assertEqual(move1.stock_valuation_layer_ids.sorted()[-1].unit_cost,10.0)

        self.assertEqual(len(move1.account_move_ids),2)

        self.assertEqual(self.product1.quantity_svl,20)
        self.assertEqual(self.product1.value_svl,200)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),200)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),200)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),0)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

    deftest_fifo_edit_done_move1(self):
        """IncreaseOUTdonemovewhilequantitiesareavailable.
        """
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #Receive10@10
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'receive10@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)

        #accountvaluesformove1
        valuation_aml=self._get_stock_valuation_move_lines()
        move1_valuation_aml=valuation_aml[-1]
        self.assertEqual(move1_valuation_aml.debit,100)
        self.assertEqual(move1_valuation_aml.credit,0)
        input_aml=self._get_stock_input_move_lines()
        move1_input_aml=input_aml[-1]
        self.assertEqual(move1_input_aml.debit,0)
        self.assertEqual(move1_input_aml.credit,100)

        self.assertEqual(len(move1.account_move_ids),1)

        self.assertAlmostEqual(self.product1.quantity_svl,10.0)
        self.assertEqual(self.product1.value_svl,100)

        #---------------------------------------------------------------------
        #Receive10@12
        #---------------------------------------------------------------------
        move2=self.env['stock.move'].create({
            'name':'receive10@12',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':12,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move2._action_confirm()
        move2._action_done()

        #stockvaluesformove2
        self.assertEqual(move2.stock_valuation_layer_ids.value,120.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move2.stock_valuation_layer_ids.unit_cost,12.0)

        #accountvaluesformove2
        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(move2_valuation_aml.debit,120)
        self.assertEqual(move2_valuation_aml.credit,0)
        input_aml=self._get_stock_input_move_lines()
        move2_input_aml=input_aml[-1]
        self.assertEqual(move2_input_aml.debit,0)
        self.assertEqual(move2_input_aml.credit,120)

        self.assertEqual(len(move2.account_move_ids),1)

        self.assertAlmostEqual(self.product1.qty_available,20.0)
        self.assertAlmostEqual(self.product1.quantity_svl,20.0)
        self.assertEqual(self.product1.value_svl,220)

        #---------------------------------------------------------------------
        #Send8
        #---------------------------------------------------------------------
        move3=self.env['stock.move'].create({
            'name':'12out(2negative)',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':8.0,
            'price_unit':0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':8.0,
            })]
        })
        move3._action_confirm()
        move3._action_done()

        #stockvaluesformove3
        self.assertEqual(move3.stock_valuation_layer_ids.value,-80.0)
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty,0.0)

        #accountvaluesformove3
        valuation_aml=self._get_stock_valuation_move_lines()
        move3_valuation_aml=valuation_aml[-1]
        self.assertEqual(move3_valuation_aml.debit,0) #FIXMEsleshiiiiiiieeeeetwith_contextoutmovedoesn'twork?
        output_aml=self._get_stock_output_move_lines()
        move3_output_aml=output_aml[-1]
        self.assertEqual(move3_output_aml.debit,80)
        self.assertEqual(move3_output_aml.credit,0)

        self.assertEqual(len(move3.account_move_ids),1)

        self.assertAlmostEqual(self.product1.qty_available,12.0)
        self.assertAlmostEqual(self.product1.quantity_svl,12.0)
        self.assertEqual(self.product1.value_svl,140)

        #---------------------------------------------------------------------
        #Editlastmove,send14instead
        #itshouldsend2@10and4@12
        #---------------------------------------------------------------------
        move3.quantity_done=14
        self.assertEqual(move3.product_qty,14)
        #oldvalue:-80-(8@10)
        #newvalue:-148=>-(10@10+4@12)
        self.assertEqual(sum(move3.stock_valuation_layer_ids.mapped('value')),-148)

        #accountvaluesformove3
        valuation_aml=self._get_stock_valuation_move_lines()
        move3_valuation_aml=valuation_aml[-1]
        self.assertEqual(move3_valuation_aml.debit,0)
        output_aml=self._get_stock_output_move_lines()
        move3_output_aml=output_aml[-1]
        self.assertEqual(move3_output_aml.debit,68)
        self.assertEqual(move3_output_aml.credit,0)

        self.assertEqual(len(move3.account_move_ids),2)

        self.assertEqual(self.product1.value_svl,72)

        #---------------------------------------------------------------------
        #Ending
        #---------------------------------------------------------------------
        self.assertEqual(self.product1.qty_available,6)
        self.assertAlmostEqual(self.product1.quantity_svl,6.0)
        self.assertEqual(self.product1.value_svl,72)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('debit')),0)
        self.assertEqual(sum(self._get_stock_input_move_lines().mapped('credit')),220)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('debit')),220)
        self.assertEqual(sum(self._get_stock_valuation_move_lines().mapped('credit')),148)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('debit')),148)
        self.assertEqual(sum(self._get_stock_output_move_lines().mapped('credit')),0)

    deftest_fifo_edit_done_move2(self):
        """Decrease,thenincreaseOUTdonemovewhilequantitiesareavailable.
        """
        self.product1.categ_id.property_cost_method='fifo'

        #---------------------------------------------------------------------
        #Receive10@10
        #---------------------------------------------------------------------
        move1=self.env['stock.move'].create({
            'name':'receive10@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.supplier_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move1._action_confirm()
        move1._action_done()

        #stockvaluesformove1
        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.unit_cost,10.0)

        #---------------------------------------------------------------------
        #Send10
        #---------------------------------------------------------------------
        move2=self.env['stock.move'].create({
            'name':'12out(2negative)',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':0,
            'move_line_ids':[(0,0,{
                'product_id':self.product1.id,
                'location_id':self.stock_location.id,
                'location_dest_id':self.customer_location.id,
                'product_uom_id':self.uom_unit.id,
                'qty_done':10.0,
            })]
        })
        move2._action_confirm()
        move2._action_done()

        #stockvaluesformove2
        self.assertEqual(move2.stock_valuation_layer_ids.value,-100.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0.0)

        #---------------------------------------------------------------------
        #Actually,send8inthelastmove
        #---------------------------------------------------------------------
        move2.quantity_done=8

        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')),-80.0) #themoveactuallysent8@10

        self.assertEqual(sum(self.product1.stock_valuation_layer_ids.mapped('remaining_qty')),2)

        self.product1.qty_available=2
        self.product1.value_svl=20
        self.product1.quantity_svl=2

        #---------------------------------------------------------------------
        #Actually,send10inthelastmove
        #---------------------------------------------------------------------
        move2.quantity_done=10

        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')),-100.0) #themoveactuallysent10@10
        self.assertEqual(sum(self.product1.stock_valuation_layer_ids.mapped('remaining_qty')),0)

        self.assertEqual(self.product1.quantity_svl,0)
        self.assertEqual(self.product1.value_svl,0)

    deftest_fifo_standard_price_upate_1(self):
        product=self.env['product.product'].create({
            'name':'product1',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        product.product_tmpl_id.categ_id.property_cost_method='fifo'
        self._make_in_move(product,3,unit_cost=17)
        self._make_in_move(product,1,unit_cost=23)
        self._make_out_move(product,3)
        self.assertEqual(product.standard_price,23)

    deftest_fifo_standard_price_upate_2(self):
        product=self.env['product.product'].create({
            'name':'product1',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        product.product_tmpl_id.categ_id.property_cost_method='fifo'
        self._make_in_move(product,5,unit_cost=17)
        self._make_in_move(product,1,unit_cost=23)
        self._make_out_move(product,4)
        self.assertEqual(product.standard_price,17)

    deftest_fifo_standard_price_upate_3(self):
        """Standardpricemustbesetonmoveinifnoproductandiffirstmove."""
        product=self.env['product.product'].create({
            'name':'product1',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        product.product_tmpl_id.categ_id.property_cost_method='fifo'
        self._make_in_move(product,5,unit_cost=17)
        self._make_in_move(product,1,unit_cost=23)
        self.assertEqual(product.standard_price,17)
        self._make_out_move(product,4)
        self.assertEqual(product.standard_price,17)
        self._make_out_move(product,1)
        self.assertEqual(product.standard_price,23)
        self._make_out_move(product,1)
        self.assertEqual(product.standard_price,23)
        self._make_in_move(product,1,unit_cost=77)
        self.assertEqual(product.standard_price,77)

    deftest_average_perpetual_1(self):
        #http://accountingexplained.com/financial/inventories/avco-method
        self.product1.categ_id.property_cost_method='average'

        #BeginningInventory:60units@15.00perunit
        move1=self.env['stock.move'].create({
            'name':'60units@15.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':60.0,
            'price_unit':15,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=60.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,900.0)

        #Purchase140units@15.50perunit
        move2=self.env['stock.move'].create({
            'name':'140units@15.50perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':140.0,
            'price_unit':15.50,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=140.0
        move2._action_done()

        self.assertEqual(move2.stock_valuation_layer_ids.value,2170.0)

        #Sale190units@15.35perunit
        move3=self.env['stock.move'].create({
            'name':'Sale190units@19.00perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':190.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=190.0
        move3._action_done()

        self.assertEqual(move3.stock_valuation_layer_ids.value,-2916.5)

        #Purchase70units@$16.00perunit
        move4=self.env['stock.move'].create({
            'name':'70units@$16.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':70.0,
            'price_unit':16.00,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=70.0
        move4._action_done()

        self.assertEqual(move4.stock_valuation_layer_ids.value,1120.0)

        #Sale30units@$19.50perunit
        move5=self.env['stock.move'].create({
            'name':'30units@$19.50perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':30.0,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=30.0
        move5._action_done()

        self.assertEqual(move5.stock_valuation_layer_ids.value,-477.56)

        #Receives10unitsbutassignthemtoanowner,thevaluationshouldnotbeimpacted.
        move6=self.env['stock.move'].create({
            'name':'10unitstoanowner',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':99,
        })
        move6._action_confirm()
        move6._action_assign()
        move6.move_line_ids.owner_id=self.owner1.id
        move6.move_line_ids.qty_done=10.0
        move6._action_done()

        self.assertEqual(move6.stock_valuation_layer_ids.value,0)

        #Sale50units@$19.50perunit(nostockanymore)
        move7=self.env['stock.move'].create({
            'name':'50units@$19.50perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':50.0,
        })
        move7._action_confirm()
        move7._action_assign()
        move7.move_line_ids.qty_done=50.0
        move7._action_done()

        self.assertEqual(move7.stock_valuation_layer_ids.value,-795.94)
        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_average_perpetual_2(self):
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'Receive10unitsat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()
        self.assertEqual(self.product1.standard_price,10)

        move2=self.env['stock.move'].create({
            'name':'Receive10unitsat15',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()
        self.assertEqual(self.product1.standard_price,12.5)

        move3=self.env['stock.move'].create({
            'name':'Deliver15units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=15.0
        move3._action_done()
        self.assertEqual(self.product1.standard_price,12.5)

        move4=self.env['stock.move'].create({
            'name':'Deliver10units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=10.0
        move4._action_done()
        #note:5unitsweresentestimatedat12.5(negativestock)
        self.assertEqual(self.product1.standard_price,12.5)
        self.assertEqual(self.product1.quantity_svl,-5)
        self.assertEqual(self.product1.value_svl,-62.5)

        move2.move_line_ids.qty_done=20
        #incrementingthereceipttriggeredthevacuum,thenegativestockiscorrected
        self.assertEqual(self.product1.stock_valuation_layer_ids[-1].value,-12.5)

        self.assertEqual(self.product1.quantity_svl,5)
        self.assertEqual(self.product1.value_svl,75)
        self.assertEqual(self.product1.standard_price,15)

    deftest_average_perpetual_3(self):
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'Receive 10unitsat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        move2=self.env['stock.move'].create({
            'name':'Receive10unitsat15',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        move3=self.env['stock.move'].create({
            'name':'Deliver15units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=15.0
        move3._action_done()

        move4=self.env['stock.move'].create({
            'name':'Deliver10units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=10.0
        move4._action_done()
        move2.move_line_ids.qty_done=0
        self.assertEqual(self.product1.value_svl,-187.5)

    deftest_average_perpetual_4(self):
        """receive1@10,receive1@5insteadof3@5"""
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'Receive1unitat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1.0
        move1._action_done()

        move2=self.env['stock.move'].create({
            'name':'Receive3unitsat5',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':3.0,
            'price_unit':5,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=1.0
        move2._action_done()

        self.assertAlmostEqual(self.product1.quantity_svl,2.0)
        self.assertAlmostEqual(self.product1.standard_price,7.5)

    deftest_average_perpetual_5(self):
        '''Setowneronincomingmove=>novaluation'''
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'Receive1unitat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1.0
        move1.move_line_ids.owner_id=self.owner1.id
        move1._action_done()

        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_average_perpetual_6(self):
        """Batchvalidationofmoves"""
        self.product1.product_tmpl_id.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'Receive1unitat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1.0

        move2=self.env['stock.move'].create({
            'name':'Receive1unitsat5',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':5,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=1.0

        #Receivebothatthesametime
        (move1|move2)._action_done()

        self.assertAlmostEqual(self.product1.standard_price,7.5)
        self.assertEqual(self.product1.quantity_svl,2)
        self.assertEqual(self.product1.value_svl,15)

    deftest_average_perpetual_7(self):
        """Testeditinthepast.Receive5@10,receive10@20,editthefirstmovetoreceive
        15instead.
        """
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'IN5@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5,
            'price_unit':10,
        })
        move1._action_confirm()
        move1.quantity_done=5
        move1._action_done()

        self.assertAlmostEqual(self.product1.standard_price,10)
        self.assertAlmostEqual(move1.stock_valuation_layer_ids.value,50)
        self.assertAlmostEqual(self.product1.quantity_svl,5)
        self.assertAlmostEqual(self.product1.value_svl,50)

        move2=self.env['stock.move'].create({
            'name':'IN10@20',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':20,
        })
        move2._action_confirm()
        move2.quantity_done=10
        move2._action_done()

        self.assertAlmostEqual(self.product1.standard_price,16.67)
        self.assertAlmostEqual(move2.stock_valuation_layer_ids.value,200)
        self.assertAlmostEqual(self.product1.quantity_svl,15)
        self.assertAlmostEqual(self.product1.value_svl,250)

        move1.move_line_ids.qty_done=15

        self.assertAlmostEqual(self.product1.standard_price,14.0)
        self.assertAlmostEqual(len(move1.stock_valuation_layer_ids),2)
        self.assertAlmostEqual(move1.stock_valuation_layer_ids.sorted()[-1].value,100)
        self.assertAlmostEqual(self.product1.quantity_svl,25)
        self.assertAlmostEqual(self.product1.value_svl,350)

    deftest_average_perpetual_8(self):
        """Receive1@10,thendropship1@20,finallyreturnthedropship.Dropshipshouldnot
            impacttheprice.
        """
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'IN1@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1,
            'price_unit':10,
        })
        move1._action_confirm()
        move1.quantity_done=1
        move1._action_done()

        self.assertAlmostEqual(self.product1.standard_price,10)

        move2=self.env['stock.move'].create({
            'name':'IN1@20',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1,
            'price_unit':20,
        })
        move2._action_confirm()
        move2.quantity_done=1
        move2._action_done()

        self.assertAlmostEqual(self.product1.standard_price,10.0)

        move3=self.env['stock.move'].create({
            'name':'IN1@20',
            'location_id':self.customer_location.id,
            'location_dest_id':self.supplier_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1,
            'price_unit':20,
        })
        move3._action_confirm()
        move3.quantity_done=1
        move3._action_done()

        self.assertAlmostEqual(self.product1.standard_price,10.0)

    deftest_average_perpetual_9(self):
        """Whenaproducthasanavailablequantityof-5,editanincomingshipmentandincrease
        thereceivedquantityby5units.
        """
        self.product1.categ_id.property_cost_method='average'
        #receive10
        move1=self.env['stock.move'].create({
            'name':'IN5@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':10,
        })
        move1._action_confirm()
        move1.quantity_done=10
        move1._action_done()

        #deliver15
        move2=self.env['stock.move'].create({
            'name':'Deliver10units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=15.0
        move2._action_done()

        #increasethereceiptto15
        move1.move_line_ids.qty_done=15

    deftest_average_stock_user(self):
        """deliveranaverageproductasastockuser."""
        self.product1.categ_id.property_cost_method='average'
        #receive10
        move1=self.env['stock.move'].create({
            'name':'IN5@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':10,
        })
        move1._action_confirm()
        move1.quantity_done=10
        move1._action_done()

        #sell15
        move2=self.env['stock.move'].create({
            'name':'Deliver10units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=15.0
        move2.with_user(self.inventory_user)._action_done()

    deftest_average_negative_1(self):
        """Testeditinthepast.Receive10,send20,editthesecondmovetoonlysend10.
        """
        self.product1.categ_id.property_cost_method='average'

        move1=self.env['stock.move'].create({
            'name':'Receive10unitsat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        move2=self.env['stock.move'].create({
            'name':'send20units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':20.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=20.0
        move2._action_done()

        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),2)
        self.assertEqual(move2_valuation_aml.debit,0)
        self.assertEqual(move2_valuation_aml.credit,200)

        move2.quantity_done=10.0

        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),3)
        self.assertEqual(move2_valuation_aml.debit,100)
        self.assertEqual(move2_valuation_aml.credit,0)

        move2.quantity_done=11.0

        valuation_aml=self._get_stock_valuation_move_lines()
        move2_valuation_aml=valuation_aml[-1]
        self.assertEqual(len(valuation_aml),4)
        self.assertEqual(move2_valuation_aml.debit,0)
        self.assertEqual(move2_valuation_aml.credit,10)

    deftest_average_negative_2(self):
        """Sendgoodsthatyoudon'thaveinstockandneverreceivedanyunit.
        """
        self.product1.categ_id.property_cost_method='average'

        #setastandardprice
        self.product1.standard_price=99

        #send10unitsthatwedonothave
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product1,self.stock_location),0)
        move1=self.env['stock.move'].create({
            'name':'test_average_negative_1',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1.quantity_done=10.0
        move1._action_done()
        self.assertEqual(move1.stock_valuation_layer_ids.value,-990.0) #asnomoveoutweredoneforthisproduct,fallbackonthestandardprice

    deftest_average_negative_3(self):
        """Sendgoodsthatyoudon'thaveinstockbutreceivedandsendsomeunitsbefore.
        """
        self.product1.categ_id.property_cost_method='average'

        #setastandardprice
        self.product1.standard_price=99

        #Receives10produtsat10
        move1=self.env['stock.move'].create({
            'name':'68units@15.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)

        #send10products
        move2=self.env['stock.move'].create({
            'name':'Sale94units@19.00perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        self.assertEqual(move2.stock_valuation_layer_ids.value,-100.0)
        self.assertEqual(move2.stock_valuation_layer_ids.remaining_qty,0.0) #unusedinaveragemove

        #send10productsagain
        move3=self.env['stock.move'].create({
            'name':'Sale94units@19.00perunit',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move3._action_confirm()
        move3.quantity_done=10.0
        move3._action_done()

        self.assertEqual(move3.stock_valuation_layer_ids.value,-100.0) #asnomoveoutweredoneforthisproduct,fallbackonlatestcost

    deftest_average_negative_4(self):
        self.product1.categ_id.property_cost_method='average'

        #setastandardprice
        self.product1.standard_price=99

        #Receives10produtsat10
        move1=self.env['stock.move'].create({
            'name':'68units@15.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)

    deftest_average_negative_5(self):
        self.product1.categ_id.property_cost_method='average'

        #in10@10
        move1=self.env['stock.move'].create({
            'name':'10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        self.assertEqual(move1.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(self.product1.standard_price,10)

        #in10@20
        move2=self.env['stock.move'].create({
            'name':'10units@20.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':20,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        self.assertEqual(move2.stock_valuation_layer_ids.value,200.0)
        self.assertEqual(self.product1.standard_price,15)

        #send5
        move3=self.env['stock.move'].create({
            'name':'Sale5units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        move3._action_confirm()
        move3.quantity_done=5.0
        move3._action_done()

        self.assertEqual(move3.stock_valuation_layer_ids.value,-75.0)
        self.assertEqual(self.product1.standard_price,15)

        #send30
        move4=self.env['stock.move'].create({
            'name':'Sale5units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':30.0,
        })
        move4._action_confirm()
        move4.quantity_done=30.0
        move4._action_done()

        self.assertEqual(move4.stock_valuation_layer_ids.value,-450.0)
        self.assertEqual(self.product1.standard_price,15)

        #in20@20
        move5=self.env['stock.move'].create({
            'name':'20units@20.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':20.0,
            'price_unit':20,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=20.0
        move5._action_done()
        self.assertEqual(move5.stock_valuation_layer_ids.value,400.0)

        #Move4isnowfixed,itinitiallysent30@15butthe5lastunitswerenegativeandestimated
        #at15(1125).Thenewreceiptmadethese5unitssentat20(1500),soa450valueisadded
        #tomove4.
        self.assertEqual(move4.stock_valuation_layer_ids[0].value,-450)

        #Sowehave5@20instock.
        self.assertEqual(self.product1.quantity_svl,5)
        self.assertEqual(self.product1.value_svl,100)
        self.assertEqual(self.product1.standard_price,20)

        #send5productstoemptytheinventory,theaveragepriceshouldnotgoto0
        move6=self.env['stock.move'].create({
            'name':'Sale5units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        move6._action_confirm()
        move6.quantity_done=5.0
        move6._action_done()

        self.assertEqual(move6.stock_valuation_layer_ids.value,-100.0)
        self.assertEqual(self.product1.standard_price,20)

        #in10@10,thenewaveragepriceshouldbe10
        move7=self.env['stock.move'].create({
            'name':'10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move7._action_confirm()
        move7._action_assign()
        move7.move_line_ids.qty_done=10.0
        move7._action_done()

        self.assertEqual(move7.stock_valuation_layer_ids.value,100.0)
        self.assertEqual(self.product1.standard_price,10)

    deftest_average_automated_with_cost_change(self):
        """TestofthehandlingofacostchangewithanegativestockquantitywithFIFO+AVCOcostingmethod"""
        self.product1.categ_id.property_cost_method='average'
        self.product1.categ_id.property_valuation='real_time'

        #Step1:Sell(andconfirm)10unitswedon'thave@100
        self.product1.standard_price=100
        move1=self.env['stock.move'].create({
            'name':'Sale10units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1.quantity_done=10.0
        move1._action_done()

        self.assertAlmostEqual(self.product1.quantity_svl,-10.0)
        self.assertEqual(move1.stock_valuation_layer_ids.value,-1000.0)
        self.assertAlmostEqual(self.product1.value_svl,-1000.0)

        #Step2:Changeproductcostfrom100to10->Nothingshouldappearininventory
        #valuationasthequantityisnegative
        self.product1.standard_price=10
        self.assertEqual(self.product1.value_svl,-1000.0)

        #Step3:Makeaninventoryadjustmenttosettototalcountedvalueat0->Inventory
        #valuationshouldbeat0withacompensationlayerat900(1000-100)
        inventory_location=self.product1.property_stock_inventory
        inventory_location.company_id=self.env.company.id

        move2=self.env['stock.move'].create({
            'name':'Adjustmentof10units',
            'location_id':inventory_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        #Checkifthemoveadjustmenthascorrectlybeendone
        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertAlmostEqual(move2.stock_valuation_layer_ids.value,100.0)

        #Checkifthecompensationlayerisasexpected,withfinalinventoryvaluebeing0
        self.assertAlmostEqual(self.product1.stock_valuation_layer_ids.sorted()[-1].value,900.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_average_manual_1(self):
        '''Setowneronincomingmove=>novaluation'''
        self.product1.categ_id.property_cost_method='average'
        self.product1.categ_id.property_valuation='manual_periodic'

        move1=self.env['stock.move'].create({
            'name':'Receive1unitat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1.0
        move1.move_line_ids.owner_id=self.owner1.id
        move1._action_done()

        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_standard_perpetual_1(self):
        '''Setowneronincomingmove=>novaluation'''
        self.product1.categ_id.property_cost_method='standard'

        move1=self.env['stock.move'].create({
            'name':'Receive1unitat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1.0
        move1.move_line_ids.owner_id=self.owner1.id
        move1._action_done()

        self.assertAlmostEqual(self.product1.qty_available,1.0)
        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_standard_manual_1(self):
        '''Setowneronincomingmove=>novaluation'''
        self.product1.categ_id.property_cost_method='standard'
        self.product1.categ_id.property_valuation='manual_periodic'

        move1=self.env['stock.move'].create({
            'name':'Receive1unitat10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=1.0
        move1.move_line_ids.owner_id=self.owner1.id
        move1._action_done()

        self.assertAlmostEqual(self.product1.qty_available,1.0)
        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_standard_manual_2(self):
        """Validateareceiptasaregularstockuser."""
        self.product1.categ_id.property_cost_method='standard'
        self.product1.categ_id.property_valuation='manual_periodic'

        self.product1.standard_price=10.0

        move1=self.env['stock.move'].with_user(self.inventory_user).create({
            'name':'IN10units',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

    deftest_standard_perpetual_2(self):
        """Validateareceiptasaregularstockuser."""
        self.product1.categ_id.property_cost_method='standard'
        self.product1.categ_id.property_valuation='real_time'

        self.product1.standard_price=10.0

        move1=self.env['stock.move'].with_user(self.inventory_user).create({
            'name':'IN10units',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

    deftest_change_cost_method_1(self):
        """ChangethecostmethodfromFIFOtoAVCO.
        """
        #---------------------------------------------------------------------
        #UseFIFO,makesomeoperations
        #---------------------------------------------------------------------
        self.product1.categ_id.property_cost_method='fifo'

        #receive10@10
        move1=self.env['stock.move'].create({
            'name':'10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        #receive10@15
        move2=self.env['stock.move'].create({
            'name':'10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        #sell1
        move3=self.env['stock.move'].create({
            'name':'Sale5units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=1.0
        move3._action_done()

        self.assertAlmostEqual(self.product1.quantity_svl,19)
        self.assertEqual(self.product1.value_svl,240)

        #---------------------------------------------------------------------
        #ChangetheproductionvaluationtoAVCO
        #---------------------------------------------------------------------
        self.product1.categ_id.property_cost_method='average'

        #valuationshouldstayto~240
        self.assertAlmostEqual(self.product1.quantity_svl,19)
        self.assertAlmostEqual(self.product1.value_svl,285,delta=0.03)

        #anaccountingentryshouldbecreated
        #FIXMEslecheckit

        self.assertEqual(self.product1.standard_price,15)

    deftest_change_cost_method_2(self):
        """ChangethecostmethodfromFIFOtostandard.
        """
        #---------------------------------------------------------------------
        #UseFIFO,makesomeoperations
        #---------------------------------------------------------------------
        self.product1.categ_id.property_cost_method='fifo'

        #receive10@10
        move1=self.env['stock.move'].create({
            'name':'10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()

        #receive10@15
        move2=self.env['stock.move'].create({
            'name':'10units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
            'price_unit':15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10.0
        move2._action_done()

        #sell1
        move3=self.env['stock.move'].create({
            'name':'Sale5units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=1.0
        move3._action_done()

        self.assertAlmostEqual(self.product1.quantity_svl,19)
        self.assertEqual(self.product1.value_svl,240)

        #---------------------------------------------------------------------
        #ChangetheproductionvaluationtoAVCO
        #---------------------------------------------------------------------
        self.product1.categ_id.property_cost_method='standard'

        #valuationshouldstayto~240
        self.assertAlmostEqual(self.product1.value_svl,285,delta=0.03)
        self.assertAlmostEqual(self.product1.quantity_svl,19)

        #noaccountingentryshouldbecreated
        #FIXMEslecheckit

        self.assertEqual(self.product1.standard_price,15)

    deftest_fifo_sublocation_valuation_1(self):
        """Setthemainstockasaviewlocation.Receive2unitsofa
        product,put1unitinaninternalsublocationandthesecond
        oneinascrapsublocation.Onlyasingleunit,theoneinthe
        internalsublocation,shouldbevalued.Then,sendthesetwo
        quantstoacustomer,onlytheoneintheinternallocation
        shouldbevalued.
        """
        self.product1.categ_id.property_cost_method='fifo'

        view_location=self.env['stock.location'].create({'name':'view','usage':'view'})
        subloc1=self.env['stock.location'].create({
            'name':'internal',
            'usage':'internal',
            'location_id':view_location.id,
        })
        #sanesettingsforascraplocation,company_iddoesn'tmatter
        subloc2=self.env['stock.location'].create({
            'name':'scrap',
            'usage':'inventory',
            'location_id':view_location.id,
            'scrap_location':True,
        })

        move1=self.env['stock.move'].create({
            'name':'2units@10.00perunit',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()

        move1.write({'move_line_ids':[
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':self.supplier_location.id,
                'location_dest_id':subloc1.id,
                'product_uom_id':self.uom_unit.id
            }),
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':self.supplier_location.id,
                'location_dest_id':subloc2.id,
                'product_uom_id':self.uom_unit.id
            }),
        ]})

        move1._action_done()
        self.assertEqual(move1.stock_valuation_layer_ids.value,10)
        self.assertEqual(move1.stock_valuation_layer_ids.remaining_qty,1)
        self.assertAlmostEqual(self.product1.qty_available,0.0)
        self.assertAlmostEqual(self.product1.quantity_svl,1.0)
        self.assertEqual(self.product1.value_svl,10)
        self.assertTrue(len(move1.account_move_ids),1)

        move2=self.env['stock.move'].create({
            'name':'2unitsout',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move2._action_confirm()
        move2._action_assign()

        move2.write({'move_line_ids':[
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':subloc1.id,
                'location_dest_id':self.supplier_location.id,
                'product_uom_id':self.uom_unit.id
            }),
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':subloc2.id,
                'location_dest_id':self.supplier_location.id,
                'product_uom_id':self.uom_unit.id
            }),
        ]})
        move2._action_done()
        self.assertEqual(move2.stock_valuation_layer_ids.value,-10)

    deftest_move_in_or_out(self):
        """Testafewcombinationofmoveandtheirmovelinesand
        checktheirvaluation.AvaluedmoveshouldbeINorOUT.
        CreatingamovethatisINandOUTshouldbeforbidden.
        """
        #aninternalmoveshouldbeconsideredasOUTifanyofitsmoveline
        #ismovedinascraplocation
        scrap=self.env['stock.location'].create({
            'name':'scrap',
            'usage':'inventory',
            'location_id':self.stock_location.id,
            'scrap_location':True,
        })

        move1=self.env['stock.move'].create({
            'name':'internalbutoutmove',
            'location_id':self.stock_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.write({'move_line_ids':[
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':self.stock_location.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id
            }),
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':self.stock_location.id,
                'location_dest_id':scrap.id,
                'product_uom_id':self.uom_unit.id
            }),
        ]})
        self.assertEqual(move1._is_out(),True)

        #amoveshouldbeconsideredasinvalidifsomeofitsmovelinesare
        #enteringthecompanyandsomeareleaving
        customer1=self.env['stock.location'].create({
            'name':'customer',
            'usage':'customer',
            'location_id':self.stock_location.id,
        })
        supplier1=self.env['stock.location'].create({
            'name':'supplier',
            'usage':'supplier',
            'location_id':self.stock_location.id,
        })
        move2=self.env['stock.move'].create({
            'name':'internalbutinandoutmove',
            'location_id':self.stock_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':2.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.write({'move_line_ids':[
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':customer1.id,
                'location_dest_id':self.stock_location.id,
                'product_uom_id':self.uom_unit.id
            }),
            (0,None,{
                'product_id':self.product1.id,
                'qty_done':1,
                'location_id':self.stock_location.id,
                'location_dest_id':customer1.id,
                'product_uom_id':self.uom_unit.id
            }),
        ]})
        self.assertEqual(move2._is_in(),True)
        self.assertEqual(move2._is_out(),True)
        withself.assertRaises(UserError):
            move2._action_done()

    deftest_at_date_standard_1(self):
        self.product1.categ_id.property_cost_method='standard'

        now=Datetime.now()
        date1=now-timedelta(days=8)
        date2=now-timedelta(days=7)
        date3=now-timedelta(days=6)
        date4=now-timedelta(days=5)
        date5=now-timedelta(days=4)
        date6=now-timedelta(days=3)
        date7=now-timedelta(days=2)
        date8=now-timedelta(days=1)

        #setthestandardpriceto10
        self.product1.standard_price=10.0

        #receive10
        move1=self.env['stock.move'].create({
            'name':'in10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10
        move1._action_done()
        move1.date=date2
        move1.stock_valuation_layer_ids._write({'create_date':date2})

        self.assertEqual(self.product1.quantity_svl,10)
        self.assertEqual(self.product1.value_svl,100)

        #receive20
        move2=self.env['stock.move'].create({
            'name':'in10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':20,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=20
        move2._action_done()
        move2.date=date3
        move2.stock_valuation_layer_ids._write({'create_date':date3})

        self.assertEqual(self.product1.quantity_svl,30)
        self.assertEqual(self.product1.value_svl,300)

        #send15
        move3=self.env['stock.move'].create({
            'name':'out10',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=15
        move3._action_done()
        move3.date=date4
        move3.stock_valuation_layer_ids._write({'create_date':date4})

        self.assertEqual(self.product1.quantity_svl,15)
        self.assertEqual(self.product1.value_svl,150)

        #setthestandardpriceto5
        self.product1.standard_price=5
        self.product1.stock_valuation_layer_ids.sorted()[-1]._write({'create_date':date5})

        self.assertEqual(self.product1.quantity_svl,15)
        self.assertEqual(self.product1.value_svl,75)

        #send10
        move4=self.env['stock.move'].create({
            'name':'out10',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=10
        move4._action_done()
        move4.date=date6
        move4.stock_valuation_layer_ids._write({'create_date':date6})

        self.assertEqual(self.product1.quantity_svl,5)
        self.assertEqual(self.product1.value_svl,25.0)

        #setthestandardpriceto7.5
        self.product1.standard_price=7.5
        self.product1.stock_valuation_layer_ids.sorted()[-1]._write({'create_date':date7})

        #receive90
        move5=self.env['stock.move'].create({
            'name':'in10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':90,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=90
        move5._action_done()
        move5.date=date8
        move5.stock_valuation_layer_ids._write({'create_date':date8})

        self.assertEqual(self.product1.quantity_svl,95)
        self.assertEqual(self.product1.value_svl,712.5)

        #Quantityavailableatdate
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).quantity_svl,0)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).quantity_svl,10)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date3)).quantity_svl,30)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date4)).quantity_svl,15)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date5)).quantity_svl,15)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date6)).quantity_svl,5)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date7)).quantity_svl,5)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date8)).quantity_svl,95)

        #Valuationatdate
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).value_svl,0)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).value_svl,100)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date3)).value_svl,300)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date4)).value_svl,150)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date5)).value_svl,75)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date6)).value_svl,25)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date8)).value_svl,712.5)

        #editthedonequantityofmove1,decreaseit
        move1.quantity_done=5

        #thechangeisonlyvisiblerightnow
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).quantity_svl,10)
        self.assertEqual(self.product1.quantity_svl,90)
        #aswhenwedecreaseaquantityonarecreipt,weconsideritasaoutmovewiththeprice
        #oftoday,thevaluewillbedecreaseof100-(5*7.5)
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('value')),62.5)
        #butthechangeisstillonlyvisiblerightnow
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).value_svl,100)

        #editmove4,send15insteadof10
        move4.quantity_done=15
        #-(10*5)-(5*7.5)
        self.assertEqual(sum(move4.stock_valuation_layer_ids.mapped('value')),-87.5)

        #thechangeisonlyvisiblerightnow
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date6)).value_svl,25)

        self.assertEqual(self.product1.quantity_svl,85)
        self.assertEqual(self.product1.value_svl,637.5)

    deftest_at_date_fifo_1(self):
        """Makesomeoperationsatdifferentdates,checkthattheresultsofthevaluationat
        datewizardareconsistent.Afterwards,editthedonequantityofsomeoperations.The
        valuationatdateresultsshouldtakethesechangesintoaccount.
        """
        self.product1.categ_id.property_cost_method='fifo'

        now=Datetime.now()
        date1=now-timedelta(days=8)
        date2=now-timedelta(days=7)
        date3=now-timedelta(days=6)
        date4=now-timedelta(days=5)
        date5=now-timedelta(days=4)
        date6=now-timedelta(days=3)

        #receive10@10
        move1=self.env['stock.move'].create({
            'name':'in10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10
        move1._action_done()
        move1.date=date1
        move1.stock_valuation_layer_ids._write({'create_date':date1})

        self.assertEqual(self.product1.quantity_svl,10)
        self.assertEqual(self.product1.value_svl,100)

        #receive10@12
        move2=self.env['stock.move'].create({
            'name':'in10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':12,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10
        move2._action_done()
        move2.date=date2
        move2.stock_valuation_layer_ids._write({'create_date':date2})

        self.assertAlmostEqual(self.product1.quantity_svl,20)
        self.assertEqual(self.product1.value_svl,220)

        #send15
        move3=self.env['stock.move'].create({
            'name':'out10',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':15,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=15
        move3._action_done()
        move3.date=date3
        move3.stock_valuation_layer_ids._write({'create_date':date3})

        self.assertAlmostEqual(self.product1.quantity_svl,5.0)
        self.assertEqual(self.product1.value_svl,60)

        #send20
        move4=self.env['stock.move'].create({
            'name':'out10',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':20,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=20
        move4._action_done()
        move4.date=date4
        move4.stock_valuation_layer_ids._write({'create_date':date4})

        self.assertAlmostEqual(self.product1.quantity_svl,-15.0)
        self.assertEqual(self.product1.value_svl,-180)

        #receive100@15
        move5=self.env['stock.move'].create({
            'name':'in10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':100,
            'price_unit':15,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=100
        move5._action_done()
        move5.date=date5
        move5.stock_valuation_layer_ids._write({'create_date':date5})

        #thevacuumran
        move4.stock_valuation_layer_ids.sorted()[-1]._write({'create_date':date6})

        self.assertEqual(self.product1.quantity_svl,85)
        self.assertEqual(self.product1.value_svl,1275)

        #Editthequantitydoneofmove1,increaseit.
        move1.quantity_done=20

        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).quantity_svl,10)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).value_svl,100)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).quantity_svl,20)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).value_svl,220)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date3)).quantity_svl,5)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date3)).value_svl,60)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date4)).quantity_svl,-15)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date4)).value_svl,-180)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date5)).quantity_svl,85)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date5)).value_svl,1320)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date6)).quantity_svl,85)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date6)).value_svl,1275)
        self.assertEqual(self.product1.quantity_svl,95)
        self.assertEqual(self.product1.value_svl,1375)

    deftest_at_date_fifo_2(self):
        self.product1.categ_id.property_cost_method='fifo'

        now=Datetime.now()
        date1=now-timedelta(days=8)
        date2=now-timedelta(days=7)
        date3=now-timedelta(days=6)
        date4=now-timedelta(days=5)
        date5=now-timedelta(days=4)

        #receive10@10
        move1=self.env['stock.move'].create({
            'name':'in10@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10
        move1._action_done()
        move1.date=date1
        move1.stock_valuation_layer_ids._write({'create_date':date1})

        self.assertAlmostEqual(self.product1.quantity_svl,10.0)
        self.assertEqual(self.product1.value_svl,100)

        #receive10@15
        move2=self.env['stock.move'].create({
            'name':'in10@15',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=10
        move2._action_done()
        move2.date=date2
        move2.stock_valuation_layer_ids._write({'create_date':date2})

        self.assertAlmostEqual(self.product1.quantity_svl,20.0)
        self.assertEqual(self.product1.value_svl,250)

        #send30
        move3=self.env['stock.move'].create({
            'name':'out30',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':30,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done=30
        move3._action_done()
        move3.date=date3
        move3.stock_valuation_layer_ids._write({'create_date':date3})

        self.assertAlmostEqual(self.product1.quantity_svl,-10.0)
        self.assertEqual(self.product1.value_svl,-150)

        #receive10@20
        move4=self.env['stock.move'].create({
            'name':'in10@20',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':20,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done=10
        move4._action_done()
        move4.date=date4
        move3.stock_valuation_layer_ids.sorted()[-1]._write({'create_date':date4})
        move4.stock_valuation_layer_ids._write({'create_date':date4})

        self.assertAlmostEqual(self.product1.quantity_svl,0.0)
        self.assertEqual(self.product1.value_svl,0)

        #receive10@10
        move5=self.env['stock.move'].create({
            'name':'in10@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10,
            'price_unit':10,
        })
        move5._action_confirm()
        move5._action_assign()
        move5.move_line_ids.qty_done=10
        move5._action_done()
        move5.date=date5
        move5.stock_valuation_layer_ids._write({'create_date':date5})

        self.assertAlmostEqual(self.product1.quantity_svl,10.0)
        self.assertEqual(self.product1.value_svl,100)

        #---------------------------------------------------------------------
        #ending:perpetualvaluation
        #---------------------------------------------------------------------
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).quantity_svl,10)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).value_svl,100)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).quantity_svl,20)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).value_svl,250)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date3)).quantity_svl,-10)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date3)).value_svl,-150)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date4)).quantity_svl,0)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date4)).value_svl,0)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date5)).quantity_svl,10)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date5)).value_svl,100)
        self.assertEqual(self.product1.quantity_svl,10)
        self.assertEqual(self.product1.value_svl,100)

    deftest_inventory_fifo_1(self):
        """Makeaninventoryfromalocationwithacompanyset,andensuretheproducthasastock
        value.Whentheproductissold,ensurethereisnoremainingquantityontheoriginalmove
        andnostockvalue.
        """
        self.product1.standard_price=15
        self.product1.categ_id.property_cost_method='fifo'
        inventory_location=self.product1.property_stock_inventory
        inventory_location.company_id=self.env.company.id

        #StartInventory:12units
        move1=self.env['stock.move'].create({
            'name':'Adjustmentof12units',
            'location_id':inventory_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=12.0
        move1._action_done()

        self.assertAlmostEqual(move1.stock_valuation_layer_ids.value,180.0)
        self.assertAlmostEqual(move1.stock_valuation_layer_ids.remaining_qty,12.0)
        self.assertAlmostEqual(self.product1.value_svl,180.0)

        #Sellthe12units
        move2=self.env['stock.move'].create({
            'name':'Sell12units',
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':12.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=12.0
        move2._action_done()

        self.assertAlmostEqual(move1.stock_valuation_layer_ids.remaining_qty,0.0)
        self.assertAlmostEqual(self.product1.value_svl,0.0)

    deftest_at_date_average_1(self):
        """Setacompanyontheinventoryloss,takeitemsfromtherethenputitemsthere,check
        thevaluesandquantitiesatdate.
        """
        now=Datetime.now()
        date1=now-timedelta(days=8)
        date2=now-timedelta(days=7)

        self.product1.standard_price=10
        self.product1.product_tmpl_id.cost_method='average'
        inventory_location=self.product1.property_stock_inventory
        inventory_location.company_id=self.env.company.id

        move1=self.env['stock.move'].create({
            'name':'Adjustmentof10units',
            'location_id':inventory_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':10.0,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done=10.0
        move1._action_done()
        move1.date=date1
        move1.stock_valuation_layer_ids._write({'create_date':date1})

        move2=self.env['stock.move'].create({
            'name':'Sell5units',
            'location_id':self.stock_location.id,
            'location_dest_id':inventory_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':5.0,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done=5.0
        move2._action_done()
        move2.date=date2
        move2.stock_valuation_layer_ids._write({'create_date':date2})

        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).quantity_svl,10)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date1)).value_svl,100)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).quantity_svl,5)
        self.assertEqual(self.product1.with_context(to_date=Datetime.to_string(date2)).value_svl,50)

    deftest_fifo_and_sml_owned_by_company(self):
        """
        WhenreceivingaFIFOproduct,ifthepickingisownedbythecompany,
        thereshouldbeaSVLandanaccountmovelinkedtotheproductSM
        """
        self.product1.categ_id.property_cost_method='fifo'

        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'owner_id':self.env.company.partner_id.id,
        })

        move=self.env['stock.move'].create({
            'picking_id':receipt.id,
            'name':'IN1@10',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':self.uom_unit.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        receipt.action_confirm()
        move.quantity_done=1
        receipt.button_validate()

        self.assertEqual(move.stock_valuation_layer_ids.value,10)
        self.assertEqual(move.stock_valuation_layer_ids.account_move_id.amount_total,10)

    deftest_create_svl_different_uom(self):
        """
        Createatransferanduseinthemoveadifferentunitofmeasurethan
        theonesetontheproductformandensurethatwhentheqtydoneischanged
        andthepickingisalreadyvalidated,ansvliscreatedintheuomsetintheproduct.
        """
        uom_dozen=self.env.ref('uom.product_uom_dozen')
        receipt=self.env['stock.picking'].create({
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'picking_type_id':self.env.ref('stock.picking_type_in').id,
            'owner_id':self.env.company.partner_id.id,
        })

        move=self.env['stock.move'].create({
            'picking_id':receipt.id,
            'name':'test',
            'location_id':self.supplier_location.id,
            'location_dest_id':self.stock_location.id,
            'product_id':self.product1.id,
            'product_uom':uom_dozen.id,
            'product_uom_qty':1.0,
            'price_unit':10,
        })
        receipt.action_confirm()
        move.quantity_done=1
        receipt.button_validate()

        self.assertEqual(self.product1.uom_name,'Units')
        self.assertEqual(self.product1.quantity_svl,12)
        move.quantity_done=2
        self.assertEqual(self.product1.quantity_svl,24)

    deftest_average_manual_price_change(self):
        """
        WhendoingaManualPriceChange,anSVLiscreatedtoupdatethevalue_svl.
        ThistestcheckthatthevalueofthisSVLiscorrectanddoesresultinnew_std_price*quantity.
        Todoso,wecreate2Inmoves,whichresultinastandardpriceroundedat$5.29,thenon-roundedvalue≃5.2857.
        Thenweupdatethestandardpriceto$7
        """
        self.product1.categ_id.property_cost_method='average'
        self._make_in_move(self.product1,5,unit_cost=5)
        self._make_in_move(self.product1,2,unit_cost=6)
        self.product1.write({'standard_price':7})
        self.assertEqual(self.product1.value_svl,49)

    deftest_average_manual_revaluation(self):
        self.product1.categ_id.property_cost_method='average'

        self._make_in_move(self.product1,1,unit_cost=20)
        self._make_in_move(self.product1,1,unit_cost=30)
        self.assertEqual(self.product1.standard_price,25)

        Form(self.env['stock.valuation.layer.revaluation'].with_context({
            'default_product_id':self.product1.id,
            'default_company_id':self.env.company.id,
            'default_account_id':self.stock_valuation_account,
            'default_added_value':-10.0,
        })).save().action_validate_revaluation()

        self.assertEqual(self.product1.standard_price,20)

    deftest_fifo_manual_revaluation(self):
        revaluation_vals={
            'default_product_id':self.product1.id,
            'default_company_id':self.env.company.id,
            'default_account_id':self.stock_valuation_account,
        }
        self.product1.categ_id.property_cost_method='fifo'

        self._make_in_move(self.product1,1,unit_cost=15)
        self._make_in_move(self.product1,1,unit_cost=30)
        self.assertEqual(self.product1.standard_price,15)

        Form(self.env['stock.valuation.layer.revaluation'].with_context({
            **revaluation_vals,
            'default_added_value':-10.0,
        })).save().action_validate_revaluation()

        self.assertEqual(self.product1.standard_price,10)

        revaluation=Form(self.env['stock.valuation.layer.revaluation'].with_context({
            **revaluation_vals,
            'default_added_value':-25.0,
        })).save()

        withself.assertRaises(UserError):
            revaluation.action_validate_revaluation()
