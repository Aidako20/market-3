#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests

@flectra.tests.tagged('post_install','-at_install')
classTestFrontend(flectra.tests.HttpCase):
    defsetUp(self):
        super().setUp()
        self.env=self.env(user=self.env.ref('base.user_admin'))
        account_obj=self.env['account.account']

        printer=self.env['restaurant.printer'].create({
            'name':'KitchenPrinter',
            'proxy_ip':'localhost',
        })
        drinks_category=self.env['pos.category'].create({'name':'Drinks'})

        pos_config=self.env['pos.config'].create({
            'name':'Bar',
            'barcode_nomenclature_id':self.env.ref('barcodes.default_barcode_nomenclature').id,
            'module_pos_restaurant':True,
            'is_table_management':True,
            'iface_splitbill':True,
            'iface_printbill':True,
            'iface_orderline_notes':True,
            'printer_ids':[(4,printer.id)],
            'iface_start_categ_id':drinks_category.id,
            'start_category':True,
            'pricelist_id':self.env.ref('product.list0').id,
        })

        main_floor=self.env['restaurant.floor'].create({
            'name':'MainFloor',
            'pos_config_id':pos_config.id,
        })

        table_05=self.env['restaurant.table'].create({
            'name':'T5',
            'floor_id':main_floor.id,
            'seats':4,
            'position_h':100,
            'position_v':100,
        })
        table_04=self.env['restaurant.table'].create({
            'name':'T4',
            'floor_id':main_floor.id,
            'seats':4,
            'shape':'square',
            'position_h':150,
            'position_v':100,
        })
        table_02=self.env['restaurant.table'].create({
            'name':'T2',
            'floor_id':main_floor.id,
            'seats':4,
            'position_h':250,
            'position_v':100,
        })

        second_floor=self.env['restaurant.floor'].create({
            'name':'SecondFloor',
            'pos_config_id':pos_config.id,
        })

        table_01=self.env['restaurant.table'].create({
            'name':'T1',
            'floor_id':second_floor.id,
            'seats':4,
            'shape':'square',
            'position_h':100,
            'position_v':150,
        })
        table_03=self.env['restaurant.table'].create({
            'name':'T3',
            'floor_id':second_floor.id,
            'seats':4,
            'position_h':100,
            'position_v':250,
        })

        main_company=self.env.ref('base.main_company')

        account_receivable=account_obj.create({'code':'X1012',
                                                 'name':'AccountReceivable-Test',
                                                 'user_type_id':self.env.ref('account.data_account_type_receivable').id,
                                                 'reconcile':True})

        self.env['ir.property']._set_default(
            'property_account_receivable_id',
            'res.partner',
            account_receivable,
            main_company,
        )

        test_sale_journal=self.env['account.journal'].create({
            'name':'SalesJournal-Test',
            'code':'TSJ',
            'type':'sale',
            'company_id':main_company.id
            })

        cash_journal=self.env['account.journal'].create({
            'name':'CashTest',
            'code':'TCJ',
            'type':'sale',
            'company_id':main_company.id
            })

        pos_config.write({
            'journal_id':test_sale_journal.id,
            'invoice_journal_id':test_sale_journal.id,
            'payment_method_ids':[(0,0,{
                'name':'Cashrestaurant',
                'split_transactions':True,
                'receivable_account_id':account_receivable.id,
                'is_cash_count':True,
                'cash_journal_id':cash_journal.id,
            })],
        })

        coke=self.env['product.product'].create({
            'available_in_pos':True,
            'list_price':2.20,
            'name':'Coca-Cola',
            'weight':0.01,
            'pos_categ_id':drinks_category.id,
            'categ_id':self.env.ref('point_of_sale.product_category_pos').id,
            'taxes_id':[(6,0,[])],
        })

        water=self.env['product.product'].create({
            'available_in_pos':True,
            'list_price':2.20,
            'name':'Water',
            'weight':0.01,
            'pos_categ_id':drinks_category.id,
            'categ_id':self.env.ref('point_of_sale.product_category_pos').id,
            'taxes_id':[(6,0,[])],
        })

        minute_maid=self.env['product.product'].create({
            'available_in_pos':True,
            'list_price':2.20,
            'name':'MinuteMaid',
            'weight':0.01,
            'pos_categ_id':drinks_category.id,
            'categ_id':self.env.ref('point_of_sale.product_category_pos').id,
            'taxes_id':[(6,0,[])],
        })

        pricelist=self.env['product.pricelist'].create({'name':'RestaurantPricelist'})
        pos_config.write({'pricelist_id':pricelist.id})

        self.pos_config=pos_config

    deftest_01_pos_restaurant(self):

        self.pos_config.with_user(self.env.ref('base.user_admin')).open_session_cb(check_coa=False)

        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'pos_restaurant_sync',login="admin")

        self.assertEqual(1,self.env['pos.order'].search_count([('amount_total','=',4.4),('state','=','draft')]))
        self.assertEqual(1,self.env['pos.order'].search_count([('amount_total','=',4.4),('state','=','paid')]))

        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'pos_restaurant_sync_second_login',login="admin")

        self.assertEqual(0,self.env['pos.order'].search_count([('amount_total','=',4.4),('state','=','draft')]))
        self.assertEqual(1,self.env['pos.order'].search_count([('amount_total','=',2.2),('state','=','draft')]))
        self.assertEqual(2,self.env['pos.order'].search_count([('amount_total','=',4.4),('state','=','paid')]))

    deftest_02_others(self):
        self.pos_config.with_user(self.env.ref('base.user_admin')).open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'SplitBillScreenTour',login="admin")
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'ControlButtonsTour',login="admin")
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'FloorScreenTour',login="admin")

    deftest_03_order_management_integration(self):
        self.pos_config.write({'manage_orders':True})
        self.pos_config.with_user(self.env.ref('base.user_admin')).open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'PosResOrderManagementScreenTour',login="admin")

    deftest_04_ticket_screen(self):
        self.pos_config.with_user(self.env.ref('base.user_admin')).open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'PosResTicketScreenTour',login="admin")

    deftest_05_tip_screen(self):
        self.pos_config.write({'set_tip_after_payment':True,'iface_tipproduct':True,'tip_product_id':self.env.ref('point_of_sale.product_product_tip')})
        self.pos_config.with_user(self.env.ref('base.user_admin')).open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'PosResTipScreenTour',login="admin")

        order1=self.env['pos.order'].search([('pos_reference','ilike','%-0001')])
        order2=self.env['pos.order'].search([('pos_reference','ilike','%-0002')])
        order3=self.env['pos.order'].search([('pos_reference','ilike','%-0003')])
        order4=self.env['pos.order'].search([('pos_reference','ilike','%-0004')])
        self.assertTrue(order1.is_tippedandorder1.tip_amount==0.40)
        self.assertTrue(order2.is_tippedandorder2.tip_amount==1.00)
        self.assertTrue(order3.is_tippedandorder3.tip_amount==1.50)
        self.assertTrue(order4.is_tippedandorder4.tip_amount==1.00)

    deftest_06_split_bill_screen(self):
        self.pos_config.with_user(self.env.ref('base.user_admin')).open_session_cb(check_coa=False)
        self.start_tour("/pos/ui?config_id=%d"%self.pos_config.id,'SplitBillScreenTour2',login="admin")
