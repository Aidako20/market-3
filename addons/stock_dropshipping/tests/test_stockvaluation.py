#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimportForm,tagged


@tagged('post_install','-at_install')
classTestStockValuation(ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.supplier_location=cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location=cls.company_data['default_warehouse'].lot_stock_id
        cls.partner_id=cls.env['res.partner'].create({'name':'MyTestPartner'})
        cls.product1=cls.env['product.product'].create({
            'name':'LargeDesk',
            'type':'product',
            'categ_id':cls.stock_account_product_categ.id,
            'taxes_id':[(6,0,[])],
        })

    def_dropship_product1(self):
        #enablethedropshipandMTOrouteontheproduct
        dropshipping_route=self.env.ref('stock_dropshipping.route_drop_shipping')
        mto_route=self.env.ref('stock.route_warehouse0_mto')
        self.product1.write({'route_ids':[(6,0,[dropshipping_route.id,mto_route.id])]})

        #addavendor
        vendor1=self.env['res.partner'].create({'name':'vendor1'})
        seller1=self.env['product.supplierinfo'].create({
            'name':vendor1.id,
            'price':8,
        })
        self.product1.write({'seller_ids':[(6,0,[seller1.id])]})

        #selloneunitofthisproduct
        customer1=self.env['res.partner'].create({'name':'customer1'})
        self.sale_order1=self.env['sale.order'].create({
            'partner_id':customer1.id,
            'partner_invoice_id':customer1.id,
            'partner_shipping_id':customer1.id,
            'order_line':[(0,0,{
                'name':self.product1.name,
                'product_id':self.product1.id,
                'product_uom_qty':1,
                'product_uom':self.product1.uom_id.id,
                'price_unit':12,
                'tax_id':[(6,0,[])],
            })],
            'pricelist_id':self.env.ref('product.list0').id,
            'picking_policy':'direct',
        })
        self.sale_order1.action_confirm()

        #confirmthepurchaseorder
        self.purchase_order1=self.env['purchase.order'].search([('group_id','=',self.sale_order1.procurement_group_id.id)])
        self.purchase_order1.button_confirm()

        #validatethedropshippingpicking
        self.assertEqual(len(self.sale_order1.picking_ids),1)
        wizard=self.sale_order1.picking_ids.button_validate()
        immediate_transfer=Form(self.env[wizard['res_model']].with_context(wizard['context'])).save()
        immediate_transfer.process()
        self.assertEqual(self.sale_order1.picking_ids.state,'done')

        #createthevendorbill
        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.partner_id=vendor1
        move_form.purchase_id=self.purchase_order1
        move_form.invoice_date=move_form.date
        foriinrange(len(self.purchase_order1.order_line)):
            withmove_form.invoice_line_ids.edit(i)asline_form:
                line_form.tax_ids.clear()
        self.vendor_bill1=move_form.save()
        self.vendor_bill1.action_post()

        #createthecustomerinvoice
        self.customer_invoice1=self.sale_order1._create_invoices()
        self.customer_invoice1.action_post()

        all_amls=self.vendor_bill1.line_ids+self.customer_invoice1.line_ids
        ifself.sale_order1.picking_ids.move_lines.account_move_ids:
            all_amls|=self.sale_order1.picking_ids.move_lines.account_move_ids.line_ids
        returnall_amls

    def_check_results(self,expected_aml,expected_aml_count,all_amls):
        #Constructadictsimilarto`expected_aml`with`all_amls`inorderto
        #comparethem.
        result_aml={}
        foramlinall_amls:
            account_id=aml.account_id.id
            ifresult_aml.get(account_id):
                debit=result_aml[account_id][0]
                credit=result_aml[account_id][1]
                result_aml[account_id]=(debit+aml.debit,credit+aml.credit)
            else:
                result_aml[account_id]=(aml.debit,aml.credit)

        self.assertEqual(len(all_amls),expected_aml_count)

        fork,vinexpected_aml.items():
            self.assertEqual(result_aml[k],v)

    #-------------------------------------------------------------------------
    #Continental
    #-------------------------------------------------------------------------
    deftest_dropship_standard_perpetual_continental_ordered(self):
        self.env.company.anglo_saxon_accounting=False
        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='order'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (8.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
        }

        self._check_results(expected_aml,4,all_amls)

    deftest_dropship_standard_perpetual_continental_delivered(self):
        self.env.company.anglo_saxon_accounting=False
        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='delivery'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (8.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
        }

        self._check_results(expected_aml,4,all_amls)

    deftest_dropship_fifo_perpetual_continental_ordered(self):
        self.env.company.anglo_saxon_accounting=False
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='order'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (8.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
        }

        self._check_results(expected_aml,4,all_amls)

    deftest_dropship_fifo_perpetual_continental_delivered(self):
        self.env.company.anglo_saxon_accounting=False

        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='delivery'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (8.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
        }

        self._check_results(expected_aml,4,all_amls)

    #-------------------------------------------------------------------------
    #Anglosaxon
    #-------------------------------------------------------------------------
    deftest_dropship_standard_perpetual_anglosaxon_ordered(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='order'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (10.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
            self.company_data['default_account_stock_in'].id:      (8.0,10.0),
            self.company_data['default_account_stock_out'].id:     (10.0,10.0),
        }
        #InterimINisnotbalancedbecausebecausethere'sadifferencebetweenthepoline
        #priceunitandthestandardprice.Wecouldsetapricedifferenceaccountonthe
        #categorytocompensate.

        self._check_results(expected_aml,10,all_amls)

    deftest_dropship_standard_perpetual_anglosaxon_delivered(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='delivery'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (10.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
            self.company_data['default_account_stock_in'].id:      (8.0,10.0),
            self.company_data['default_account_stock_out'].id:     (10.0,10.0),
        }
        #InterimINisnotbalancedbecausebecausethere'sadifferencebetweenthepoline
        #priceunitandthestandardprice.Wecouldsetapricedifferenceaccountonthe
        #categorytocompensate.

        self._check_results(expected_aml,10,all_amls)

    deftest_dropship_fifo_perpetual_anglosaxon_ordered(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='order'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (8.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
            self.company_data['default_account_stock_in'].id:      (8.0,8.0),
            self.company_data['default_account_stock_out'].id:     (8.0,8.0),
        }

        self._check_results(expected_aml,10,all_amls)

    deftest_dropship_fifo_perpetual_anglosaxon_delivered(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='delivery'

        all_amls=self._dropship_product1()

        expected_aml={
            self.company_data['default_account_payable'].id:       (0.0,8.0),
            self.company_data['default_account_expense'].id:       (8.0,0.0),
            self.company_data['default_account_receivable'].id:    (12.0,0.0),
            self.company_data['default_account_revenue'].id:       (0.0,12.0),
            self.company_data['default_account_stock_in'].id:      (8.0,8.0),
            self.company_data['default_account_stock_out'].id:     (8.0,8.0),
        }
        self._check_results(expected_aml,10,all_amls)

    deftest_dropship_standard_perpetual_anglosaxon_ordered_return(self):
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='standard'
        self.product1.product_tmpl_id.standard_price=10
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='order'

        all_amls=self._dropship_product1()

        #returnwhatwe'vedone
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=self.sale_order1.picking_ids.ids,active_id=self.sale_order1.picking_ids.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done=1.0
        return_pick._action_done()
        self.assertEqual(return_pick.move_lines._is_dropshipped_returned(),True)

        all_amls_return=self.vendor_bill1.line_ids+self.customer_invoice1.line_ids
        ifself.sale_order1.picking_ids.mapped('move_lines.account_move_ids'):
            all_amls_return|=self.sale_order1.picking_ids.mapped('move_lines.account_move_ids.line_ids')

        #TwoextraAMLshouldhavebeencreatedforthereturn
        expected_aml={
            self.company_data['default_account_stock_in'].id:      (10.0,0.0),
            self.company_data['default_account_stock_out'].id:     (0.0,10.0),
        }

        self._check_results(expected_aml,4,all_amls_return-all_amls)

    deftest_dropship_fifo_return(self):
        """TestthereturnofadropshiporderwithaproductsettoFIFOcosting
        method.Theunitpriceiscorrectlycomputedonthereturnpickingsvl.
        """
        self.env.company.anglo_saxon_accounting=True
        self.product1.product_tmpl_id.categ_id.property_cost_method='fifo'
        self.product1.product_tmpl_id.categ_id.property_valuation='real_time'
        self.product1.product_tmpl_id.invoice_policy='order'

        self._dropship_product1()
        self.assertTrue(8inself.purchase_order1.picking_ids.move_lines.stock_valuation_layer_ids.mapped('value'))
        self.assertTrue(-8inself.purchase_order1.picking_ids.move_lines.stock_valuation_layer_ids.mapped('value'))

        #returnwhatwe'vedone
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=self.sale_order1.picking_ids.ids,active_id=self.sale_order1.picking_ids.ids[0],
            active_model='stock.picking'))
        stock_return_picking=stock_return_picking_form.save()
        stock_return_picking_action=stock_return_picking.create_returns()
        return_pick=self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done=1.0
        return_pick._action_done()

        self.assertTrue(8inreturn_pick.move_lines.stock_valuation_layer_ids.mapped('value'))
        self.assertTrue(-8inreturn_pick.move_lines.stock_valuation_layer_ids.mapped('value'))

        #returnagaintohaveanewdropshippickingfromadropshipreturn
        stock_return_picking_form_2=Form(self.env['stock.return.picking']
            .with_context(active_ids=return_pick.ids,active_id=return_pick.ids[0],
            active_model='stock.picking'))
        stock_return_picking_2=stock_return_picking_form_2.save()
        stock_return_picking_action_2=stock_return_picking_2.create_returns()
        return_pick_2=self.env['stock.picking'].browse(stock_return_picking_action_2['res_id'])
        return_pick_2.move_lines[0].move_line_ids[0].qty_done=1.0
        return_pick_2._action_done()

        self.assertTrue(8inreturn_pick_2.move_lines.stock_valuation_layer_ids.mapped('value'))
        self.assertTrue(-8inreturn_pick_2.move_lines.stock_valuation_layer_ids.mapped('value'))
