#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectraimportfields


@tagged('-at_install','post_install')
classValuationReconciliationTestCommon(AccountTestInvoicingCommon):
    """Baseclassfortestscheckinginterimaccountsreconciliationworks
    inanglosaxonaccounting.Itsetsupeverythingweneedinthetests,andis
    extendedinbothsale_stockandpurchasemodulestorunthe'true'tests.
    """

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.stock_account_product_categ=cls.env['product.category'].create({
            'name':'Testcategory',
            'property_valuation':'real_time',
            'property_cost_method':'fifo',
            'property_stock_valuation_account_id':cls.company_data['default_account_stock_valuation'].id,
            'property_stock_account_input_categ_id':cls.company_data['default_account_stock_in'].id,
            'property_stock_account_output_categ_id':cls.company_data['default_account_stock_out'].id,
        })

        uom_unit=cls.env.ref('uom.product_uom_unit')

        cls.test_product_order=cls.env['product.product'].create({
            'name':"Testproducttemplateinvoicedonorder",
            'standard_price':42.0,
            'type':'product',
            'categ_id':cls.stock_account_product_categ.id,
            'uom_id':uom_unit.id,
            'uom_po_id':uom_unit.id,
        })
        cls.test_product_delivery=cls.env['product.product'].create({
            'name':'Testproducttemplateinvoicedondelivery',
            'standard_price':42.0,
            'type':'product',
            'categ_id':cls.stock_account_product_categ.id,
            'uom_id':uom_unit.id,
            'uom_po_id':uom_unit.id,
        })

    @classmethod
    defsetup_company_data(cls,company_name,chart_template=None,**kwargs):
        company_data=super().setup_company_data(company_name,chart_template=chart_template,**kwargs)

        #Createstockconfig.
        company_data.update({
            'default_account_stock_in':cls.env['account.account'].create({
                'name':'default_account_stock_in',
                'code':'STOCKIN',
                'reconcile':True,
                'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
                'company_id':company_data['company'].id,
            }),
            'default_account_stock_out':cls.env['account.account'].create({
                'name':'default_account_stock_out',
                'code':'STOCKOUT',
                'reconcile':True,
                'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
                'company_id':company_data['company'].id,
            }),
            'default_account_stock_valuation':cls.env['account.account'].create({
                'name':'default_account_stock_valuation',
                'code':'STOCKVAL',
                'reconcile':True,
                'user_type_id':cls.env.ref('account.data_account_type_current_assets').id,
                'company_id':company_data['company'].id,
            }),
            'default_warehouse':cls.env['stock.warehouse'].search(
                [('company_id','=',company_data['company'].id)],
                limit=1,
            ),
        })
        returncompany_data

    defcheck_reconciliation(self,invoice,picking,full_reconcile=True,operation='purchase'):
        interim_account_id=self.company_data['default_account_stock_in'].idifoperation=='purchase'elseself.company_data['default_account_stock_out'].id
        invoice_line=invoice.line_ids.filtered(lambdaline:line.account_id.id==interim_account_id)

        stock_moves=picking.move_lines

        valuation_line=stock_moves.mapped('account_move_ids.line_ids').filtered(lambdax:x.account_id.id==interim_account_id)

        ifinvoice.is_purchase_document()andany(l.is_anglo_saxon_lineforlininvoice_line):
            self.assertEqual(len(invoice_line),2,"Onlytwoline2shouldhavebeenwrittenbyinvoiceinstockinputaccount")
            self.assertTrue(valuation_line.reconciledorinvoice_line[0].reconciledorinvoice_line[1].reconciled,"Thevaluationandinvoicelineshouldhavebeenreconciledtogether.")
        else:
            self.assertEqual(len(invoice_line),1,"Onlyonelineshouldhavebeenwrittenbyinvoiceinstockinputaccount")
            self.assertTrue(valuation_line.reconciledorinvoice_line.reconciled,"Thevaluationandinvoicelineshouldhavebeenreconciledtogether.")

        ifinvoice.move_typenotin('out_refund','in_refund'):
            self.assertEqual(len(valuation_line),1,"Onlyonelineshouldhavebeenwrittenforstockvaluationinstockinputaccount")

            iffull_reconcile:
                self.assertTrue(valuation_line.full_reconcile_id,"Thereconciliationshouldbetotalatthatpoint.")
            else:
                self.assertFalse(valuation_line.full_reconcile_id,"Thereconciliationshouldnotbetotalatthatpoint.")

    def_process_pickings(self,pickings,date=False,quantity=False):
        ifnotdate:
            date=fields.Date.today()
        pickings.action_confirm()
        pickings.action_assign()
        forpickinginpickings:
            formlinpicking.move_line_ids:
                ml.qty_done=quantityorml.product_qty
        pickings._action_done()
        self._change_pickings_date(pickings,date)

    def_change_pickings_date(self,pickings,date):
        pickings.mapped('move_lines').write({'date':date})
        pickings.mapped('move_lines.account_move_ids').write({'name':'/','state':'draft'})
        pickings.mapped('move_lines.account_move_ids').write({'date':date})
        pickings.move_lines.account_move_ids.action_post()
