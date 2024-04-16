#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime

importflectra
fromflectraimportfields,tools
fromflectra.toolsimportfloat_compare,mute_logger,test_reports
fromflectra.tests.commonimportForm
fromflectra.addons.point_of_sale.tests.commonimportTestPointOfSaleCommon


@flectra.tests.tagged('post_install','-at_install')
classTestPointOfSaleFlow(TestPointOfSaleCommon):

    defcompute_tax(self,product,price,qty=1,taxes=None):
        ifnottaxes:
            taxes=product.taxes_id.filtered(lambdat:t.company_id.id==self.env.company.id)
        currency=self.pos_config.pricelist_id.currency_id
        res=taxes.compute_all(price,currency,qty,product=product)
        untax=res['total_excluded']
        returnuntax,sum(tax.get('amount',0.0)fortaxinres['taxes'])

    deftest_order_refund(self):
        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id
        #IcreateanewPoSorderwith2lines
        order=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':5.0,
                'qty':2.0,
                'tax_ids':[(6,0,self.product3.taxes_id.ids)],
                'price_subtotal':450*(1-5/100.0)*2,
                'price_subtotal_incl':450*(1-5/100.0)*2,
            }),(0,0,{
                'name':"OL/0002",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':5.0,
                'qty':3.0,
                'tax_ids':[(6,0,self.product4.taxes_id.ids)],
                'price_subtotal':300*(1-5/100.0)*3,
                'price_subtotal_incl':300*(1-5/100.0)*3,
            })],
            'amount_total':1710.0,
            'amount_tax':0.0,
            'amount_paid':0.0,
            'amount_return':0.0,
        })

        payment_context={"active_ids":order.ids,"active_id":order.id}
        order_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':order.amount_total,
            'payment_method_id':self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()
        self.assertAlmostEqual(order.amount_total,order.amount_paid,msg='Ordershouldbefullypaid.')

        #Icreatearefund
        refund_action=order.refund()
        refund=self.PosOrder.browse(refund_action['res_id'])

        self.assertEqual(order.amount_total,-1*refund.amount_total,
            "Therefunddoesnotcanceltheorder(%sand%s)"%(order.amount_total,refund.amount_total))

        payment_context={"active_ids":refund.ids,"active_id":refund.id}
        refund_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':refund.amount_total,
            'payment_method_id':self.cash_payment_method.id,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        refund_payment.with_context(**payment_context).check()

        self.assertEqual(refund.state,'paid',"Therefundisnotmarkedaspaid")
        self.assertTrue(refund.payment_ids.payment_method_id.is_cash_count,msg='Thereshouldonlybeonepaymentandpaidincash.')

        current_session.action_pos_session_closing_control()
        self.assertEqual(current_session.state,'closed',msg='Stateofcurrentsessionshouldbeclosed.')

    deftest_order_refund_lots(self):
        #openpossession
        self.pos_config.open_session_cb()
        current_session=self.pos_config.current_session_id

        #setupproductiwithSNtracingandcreatetwolots(1001,1002)
        self.stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.product2=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'tracking':'serial',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        inventory=self.env['stock.inventory'].create({
            'name':'addproduct2',
            'location_ids':[(4,self.stock_location.id)],
            'product_ids':[(4,self.product2.id)],
        })
        inventory.action_start()

        lot1=self.env['stock.production.lot'].create({
            'name':'1001',
            'product_id':self.product2.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'1002',
            'product_id':self.product2.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.inventory.line'].create([
            {
            'inventory_id':inventory.id,
            'location_id':self.stock_location.id,
            'product_id':self.product2.id,
            'prod_lot_id':lot1.id,
            'product_qty':1
            },
            {
            'inventory_id':inventory.id,
            'location_id':self.stock_location.id,
            'product_id':self.product2.id,
            'prod_lot_id':lot2.id,
            'product_qty':1
            },
        ])

        inventory.action_validate()

        #createposorderwiththetwoSNcreatedbefore

        order=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'id':1,
                'product_id':self.product2.id,
                'price_unit':6,
                'discount':0,
                'qty':2,
                'tax_ids':[[6,False,[]]],
                'price_subtotal':12,
                'price_subtotal_incl':12,
                'pack_lot_ids':[
                    [0,0,{'lot_name':'1001'}],
                    [0,0,{'lot_name':'1002'}],
                ]
            })],
            'pricelist_id':1,
            'amount_paid':12.0,
            'amount_total':12.0,
            'amount_tax':0.0,
            'amount_return':0.0,
            'to_invoice':False,
            })

        payment_context={"active_ids":order.ids,"active_id":order.id}
        order_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':order.amount_total,
            'payment_method_id':self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()

        #Icreatearefund
        refund_action=order.refund()
        refund=self.PosOrder.browse(refund_action['res_id'])

        order_lot_id=[lot_id.lot_nameforlot_idinorder.lines.pack_lot_ids]
        refund_lot_id=[lot_id.lot_nameforlot_idinrefund.lines.pack_lot_ids]
        self.assertEqual(
            order_lot_id,
            refund_lot_id,
            "Intherefundweshouldfindthesamelotasintheoriginalorder")

        payment_context={"active_ids":refund.ids,"active_id":refund.id}
        refund_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':refund.amount_total,
            'payment_method_id':self.cash_payment_method.id,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        refund_payment.with_context(**payment_context).check()

        self.assertEqual(refund.state,'paid',"Therefundisnotmarkedaspaid")
        current_session.action_pos_session_closing_control()

    deftest_order_to_picking(self):
        """
            InordertotestthePointofSaleinmodule,Iwilldothreeordersfromthesaletothepayment,
            invoicing+picking,butwillonlycheckthepickingconsistencyintheend.

            TODO:CheckthenegativepickingafterchangingthepickingrelationtoOne2many(alsoforamixedusecase),
            checkthequantity,thelocationsandreturnpickinglogic
        """

        #Iclickoncreateanewsessionbutton
        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id

        #IcreateaPoSorderwith2unitsofPCSC234at450EUR
        #and3unitsofPCSC349at300EUR.
        untax1,atax1=self.compute_tax(self.product3,450,2)
        untax2,atax2=self.compute_tax(self.product4,300,3)
        self.pos_order_pos1=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'partner_id':self.partner1.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':0.0,
                'qty':2.0,
                'tax_ids':[(6,0,self.product3.taxes_id.ids)],
                'price_subtotal':untax1,
                'price_subtotal_incl':untax1+atax1,
            }),(0,0,{
                'name':"OL/0002",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':0.0,
                'qty':3.0,
                'tax_ids':[(6,0,self.product4.taxes_id.ids)],
                'price_subtotal':untax2,
                'price_subtotal_incl':untax2+atax2,
            })],
            'amount_tax':atax1+atax2,
            'amount_total':untax1+untax2+atax1+atax2,
            'amount_paid':0,
            'amount_return':0,
        })

        context_make_payment={
            "active_ids":[self.pos_order_pos1.id],
            "active_id":self.pos_order_pos1.id
        }
        self.pos_make_payment_2=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':untax1+untax2+atax1+atax2
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos1.id}

        self.pos_make_payment_2.with_context(context_payment).check()
        #Icheckthattheorderismarkedaspaid
        self.assertEqual(
            self.pos_order_pos1.state,
            'paid',
            'Ordershouldbeinpaidstate.'
        )

        #Itestthatthepickingsarecreatedasexpectedduringpayment
        #Onepickingattachedandhavingallthepositivemovelinesinthecorrectstate
        self.assertEqual(
            self.pos_order_pos1.picking_ids[0].state,
            'done',
            'Pickingshouldbeindonestate.'
        )
        self.assertEqual(
            self.pos_order_pos1.picking_ids[0].move_lines.mapped('state'),
            ['done','done'],
            'MoveLinesshouldbeindonestate.'
        )

        #Icreateasecondorder
        untax1,atax1=self.compute_tax(self.product3,450,-2)
        untax2,atax2=self.compute_tax(self.product4,300,-3)
        self.pos_order_pos2=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'partner_id':self.partner1.id,
            'lines':[(0,0,{
                'name':"OL/0003",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':0.0,
                'qty':(-2.0),
                'tax_ids':[(6,0,self.product3.taxes_id.ids)],
                'price_subtotal':untax1,
                'price_subtotal_incl':untax1+atax1,
            }),(0,0,{
                'name':"OL/0004",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':0.0,
                'qty':(-3.0),
                'tax_ids':[(6,0,self.product4.taxes_id.ids)],
                'price_subtotal':untax2,
                'price_subtotal_incl':untax2+atax2,
            })],
            'amount_tax':atax1+atax2,
            'amount_total':untax1+untax2+atax1+atax2,
            'amount_paid':0,
            'amount_return':0,
        })

        context_make_payment={
            "active_ids":[self.pos_order_pos2.id],
            "active_id":self.pos_order_pos2.id
        }
        self.pos_make_payment_3=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':untax1+untax2+atax1+atax2
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos2.id}
        self.pos_make_payment_3.with_context(context_payment).check()

        #Icheckthattheorderismarkedaspaid
        self.assertEqual(
            self.pos_order_pos2.state,
            'paid',
            'Ordershouldbeinpaidstate.'
        )

        #Itestthatthepickingsarecreatedasexpected
        #Onepickingattachedandhavingallthepositivemovelinesinthecorrectstate
        self.assertEqual(
            self.pos_order_pos2.picking_ids[0].state,
            'done',
            'Pickingshouldbeindonestate.'
        )
        self.assertEqual(
            self.pos_order_pos2.picking_ids[0].move_lines.mapped('state'),
            ['done','done'],
            'MoveLinesshouldbeindonestate.'
        )

        untax1,atax1=self.compute_tax(self.product3,450,-2)
        untax2,atax2=self.compute_tax(self.product4,300,3)
        self.pos_order_pos3=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'partner_id':self.partner1.id,
            'lines':[(0,0,{
                'name':"OL/0005",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':0.0,
                'qty':(-2.0),
                'tax_ids':[(6,0,self.product3.taxes_id.ids)],
                'price_subtotal':untax1,
                'price_subtotal_incl':untax1+atax1,
            }),(0,0,{
                'name':"OL/0006",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':0.0,
                'qty':3.0,
                'tax_ids':[(6,0,self.product4.taxes_id.ids)],
                'price_subtotal':untax2,
                'price_subtotal_incl':untax2+atax2,
            })],
            'amount_tax':atax1+atax2,
            'amount_total':untax1+untax2+atax1+atax2,
            'amount_paid':0,
            'amount_return':0,
        })

        context_make_payment={
            "active_ids":[self.pos_order_pos3.id],
            "active_id":self.pos_order_pos3.id
        }
        self.pos_make_payment_4=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':untax1+untax2+atax1+atax2,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos3.id}
        self.pos_make_payment_4.with_context(context_payment).check()

        #Icheckthattheorderismarkedaspaid
        self.assertEqual(
            self.pos_order_pos3.state,
            'paid',
            'Ordershouldbeinpaidstate.'
        )

        #Itestthatthepickingsarecreatedasexpected
        #Onepickingattachedandhavingallthepositivemovelinesinthecorrectstate
        self.assertEqual(
            self.pos_order_pos3.picking_ids[0].state,
            'done',
            'Pickingshouldbeindonestate.'
        )
        self.assertEqual(
            self.pos_order_pos3.picking_ids[0].move_lines.mapped('state'),
            ['done'],
            'MoveLinesshouldbeindonestate.'
        )
        #Iclosethesessiontogeneratethejournalentries
        self.pos_config.current_session_id.action_pos_session_closing_control()

    deftest_order_to_picking02(self):
        """Thistestissimilartotest_order_to_pickingexceptthatthistime,therearethreeproducts:
            -Onetrackedbylot,withpreexistinglot
            -Onetrackedbylot,withoutpreexistinglot
            -Oneuntracked
            -Allareinasublocationofthemainwarehouse
        """
        tracked_product_w_lot,tracked_product_wo_lot,untracked_product=self.env['product.product'].create([{
            'name':'SuperProductTracked',
            'type':'product',
            'tracking':'lot',
            'available_in_pos':True,
        },{
            'name':'SuperProductTrackedNoLot',
            'type':'product',
            'tracking':'lot',
            'available_in_pos':True,
        },{
            'name':'SuperProductUntracked',
            'type':'product',
            'available_in_pos':True,
        }])
        wh_location=self.company_data['default_warehouse'].lot_stock_id
        shelf1_location=self.env['stock.location'].create({
            'name':'shelf1',
            'usage':'internal',
            'location_id':wh_location.id,
        })
        lot=self.env['stock.production.lot'].create({
            'name':'SuperLot',
            'product_id':tracked_product_w_lot.id,
            'company_id':self.env.company.id,
        })
        qty=2
        self.env['stock.quant']._update_available_quantity(tracked_product_w_lot,shelf1_location,qty,lot_id=lot)
        self.env['stock.quant']._update_available_quantity(tracked_product_wo_lot,shelf1_location,qty)
        self.env['stock.quant']._update_available_quantity(untracked_product,shelf1_location,qty)

        self.pos_config.open_session_cb()
        self.pos_config.current_session_id.update_stock_at_closing=False

        untax,atax=self.compute_tax(tracked_product_w_lot,1.15,1)

        foriinrange(qty):
            pos_order=self.PosOrder.create({
                'company_id':self.env.company.id,
                'session_id':self.pos_config.current_session_id.id,
                'pricelist_id':self.partner1.property_product_pricelist.id,
                'partner_id':self.partner1.id,
                'lines':[(0,0,{
                    'name':"OL/0001",
                    'product_id':tracked_product_w_lot.id,
                    'price_unit':untax+atax,
                    'discount':0.0,
                    'qty':1.0,
                    'tax_ids':[(6,0,tracked_product_w_lot.taxes_id.ids)],
                    'price_subtotal':untax,
                    'price_subtotal_incl':untax+atax,
                    'pack_lot_ids':[[0,0,{'lot_name':lot.name}]],
                }),(0,0,{
                    'name':"OL/0002",
                    'product_id':untracked_product.id,
                    'price_unit':untax+atax,
                    'discount':0.0,
                    'qty':1.0,
                    'tax_ids':[(6,0,untracked_product.taxes_id.ids)],
                    'price_subtotal':untax,
                    'price_subtotal_incl':untax+atax,
                }),(0,0,{
                    'name':"OL/0003",
                    'product_id':tracked_product_wo_lot.id,
                    'price_unit':untax+atax,
                    'discount':0.0,
                    'qty':1.0,
                    'tax_ids':[(6,0,tracked_product_wo_lot.taxes_id.ids)],
                    'price_subtotal':untax,
                    'price_subtotal_incl':untax+atax,
                    'pack_lot_ids':[[0,0,{'lot_name':'NewSuperLot'}]],
                })],
                'amount_tax':3*atax,
                'amount_total':3*(untax+atax),
                'amount_paid':0,
                'amount_return':0,
            })

            context_make_payment={
                "active_ids":[pos_order.id],
                "active_id":pos_order.id,
            }
            pos_make_payment=self.PosMakePayment.with_context(context_make_payment).create({
                'amount':3*(untax+atax),
            })
            context_payment={'active_id':pos_order.id}
            pos_make_payment.with_context(context_payment).check()

            self.assertEqual(pos_order.state,'paid')
            tracked_line_w_lot=pos_order.picking_ids.move_line_ids.filtered(lambdaml:ml.product_id.id==tracked_product_w_lot.id)
            tracked_line_wo_lot=pos_order.picking_ids.move_line_ids.filtered(lambdaml:ml.product_id.id==tracked_product_wo_lot.id)
            untracked_line=pos_order.picking_ids.move_line_ids-(tracked_line_w_lot|tracked_line_wo_lot)
            self.assertEqual(tracked_line_w_lot.lot_id,lot)
            self.assertTrue(tracked_line_wo_lot.lot_id)
            self.assertFalse(untracked_line.lot_id)
            self.assertEqual(tracked_line_w_lot.location_id,shelf1_location)
            self.assertEqual(tracked_line_wo_lot.location_id,pos_order.config_id.picking_type_id.default_location_src_id)
            self.assertEqual(untracked_line.location_id,shelf1_location)

        self.pos_config.current_session_id.action_pos_session_closing_control()

    deftest_order_to_invoice(self):

        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id

        untax1,atax1=self.compute_tax(self.product3,450*0.95,2)
        untax2,atax2=self.compute_tax(self.product4,300*0.95,3)
        #IcreateanewPoSorderwith2unitsofPC1at450EUR(TaxIncl)and3unitsofPCSC349at300EUR.(TaxExcl)
        self.pos_order_pos1=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':5.0,
                'qty':2.0,
                'tax_ids':[(6,0,self.product3.taxes_id.filtered(lambdat:t.company_id.id==self.env.company.id).ids)],
                'price_subtotal':untax1,
                'price_subtotal_incl':untax1+atax1,
            }),(0,0,{
                'name':"OL/0002",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':5.0,
                'qty':3.0,
                'tax_ids':[(6,0,self.product4.taxes_id.filtered(lambdat:t.company_id.id==self.env.company.id).ids)],
                'price_subtotal':untax2,
                'price_subtotal_incl':untax2+atax2,
            })],
            'amount_tax':atax1+atax2,
            'amount_total':untax1+untax2+atax1+atax2,
            'amount_paid':0.0,
            'amount_return':0.0,
        })

        #Iclickonthe"MakePayment"wizardtopaythePoSorder
        context_make_payment={"active_ids":[self.pos_order_pos1.id],"active_id":self.pos_order_pos1.id}
        self.pos_make_payment=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':untax1+untax2+atax1+atax2,
        })
        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos1.id}
        self.pos_make_payment.with_context(context_payment).check()

        #Icheckthattheorderismarkedaspaidandthereisnoinvoice
        #attachedtoit
        self.assertEqual(self.pos_order_pos1.state,'paid',"Ordershouldbeinpaidstate.")
        self.assertFalse(self.pos_order_pos1.account_move,'Invoiceshouldnotbeattachedtoorder.')

        #Igenerateaninvoicefromtheorder
        res=self.pos_order_pos1.action_pos_order_invoice()
        self.assertIn('res_id',res,"Invoiceshouldbecreated")

        #Itestthatthetotaloftheattachedinvoiceiscorrect
        invoice=self.env['account.move'].browse(res['res_id'])
        ifinvoice.state!='posted':
            invoice.action_post()
        self.assertAlmostEqual(
            invoice.amount_total,self.pos_order_pos1.amount_total,places=2,msg="Invoicenotcorrect")

        #Iclosethesessiontogeneratethejournalentries
        current_session.action_pos_session_closing_control()

        """InordertotestthereportsonBankStatementdefinedinpoint_of_salemodule,Icreateabankstatementline,confirmitandprintthereports"""

        #Iselecttheperiodandjournalforthebankstatement

        context_journal={'journal_type':'bank'}
        self.assertTrue(self.AccountBankStatement.with_context(
            context_journal)._default_journal(),'Journalhasnotbeenselected')
        journal=self.env['account.journal'].create({
            'name':'BankTest',
            'code':'BNKT',
            'type':'bank',
            'company_id':self.env.company.id,
        })
        #IcreateabankstatementwithOpeningandClosingbalance0.
        account_statement=self.AccountBankStatement.create({
            'balance_start':0.0,
            'balance_end_real':0.0,
            'date':time.strftime('%Y-%m-%d'),
            'journal_id':journal.id,
            'company_id':self.env.company.id,
            'name':'possessiontest',
        })
        #Icreatebankstatementline
        account_statement_line=self.AccountBankStatementLine.create({
            'amount':1000,
            'partner_id':self.partner4.id,
            'statement_id':account_statement.id,
            'payment_ref':'EXT001'
        })
        #ImodifythebankstatementandsettheClosingBalance.
        account_statement.write({
            'balance_end_real':1000.0,
        })

        #Ireconcilethebankstatement.
        new_aml_dicts=[{
            'account_id':self.partner4.property_account_receivable_id.id,
            'name':"EXT001",
            'credit':1000.0,
            'debit':0.0,
        }]

        #IconfirmthebankstatementusingConfirmbutton

        self.AccountBankStatement.button_validate()

    deftest_create_from_ui(self):
        """
        Simulationofsalescomingfromtheinterface,evenafterclosingthesession
        """

        #Iclickoncreateanewsessionbutton
        self.pos_config.open_session_cb(check_coa=False)

        current_session=self.pos_config.current_session_id
        num_starting_orders=len(current_session.order_ids)

        untax,atax=self.compute_tax(self.led_lamp,0.9)
        carrot_order={'data':
          {'amount_paid':untax+atax,
           'amount_return':0,
           'amount_tax':atax,
           'amount_total':untax+atax,
           'creation_date':fields.Datetime.to_string(fields.Datetime.now()),
           'fiscal_position_id':False,
           'pricelist_id':self.pos_config.available_pricelist_ids[0].id,
           'lines':[[0,
             0,
             {'discount':0,
              'id':42,
              'pack_lot_ids':[],
              'price_unit':0.9,
              'product_id':self.led_lamp.id,
              'price_subtotal':0.9,
              'price_subtotal_incl':1.04,
              'qty':1,
              'tax_ids':[(6,0,self.led_lamp.taxes_id.ids)]}]],
           'name':'Order00042-003-0014',
           'partner_id':False,
           'pos_session_id':current_session.id,
           'sequence_number':2,
           'statement_ids':[[0,
             0,
             {'amount':untax+atax,
              'name':fields.Datetime.now(),
              'payment_method_id':self.cash_payment_method.id}]],
           'uid':'00042-003-0014',
           'user_id':self.env.uid},
          'id':'00042-003-0014',
          'to_invoice':False}

        untax,atax=self.compute_tax(self.whiteboard_pen,1.2)
        zucchini_order={'data':
          {'amount_paid':untax+atax,
           'amount_return':0,
           'amount_tax':atax,
           'amount_total':untax+atax,
           'creation_date':fields.Datetime.to_string(fields.Datetime.now()),
           'fiscal_position_id':False,
           'pricelist_id':self.pos_config.available_pricelist_ids[0].id,
           'lines':[[0,
             0,
             {'discount':0,
              'id':3,
              'pack_lot_ids':[],
              'price_unit':1.2,
              'product_id':self.whiteboard_pen.id,
              'price_subtotal':1.2,
              'price_subtotal_incl':1.38,
              'qty':1,
              'tax_ids':[(6,0,self.whiteboard_pen.taxes_id.ids)]}]],
           'name':'Order00043-003-0014',
           'partner_id':False,
           'pos_session_id':current_session.id,
           'sequence_number':self.pos_config.journal_id.id,
           'statement_ids':[[0,
             0,
             {'amount':untax+atax,
              'name':fields.Datetime.now(),
              'payment_method_id':self.credit_payment_method.id}]],
           'uid':'00043-003-0014',
           'user_id':self.env.uid},
          'id':'00043-003-0014',
          'to_invoice':False}

        untax,atax=self.compute_tax(self.newspaper_rack,1.28)
        newspaper_rack_order={'data':
          {'amount_paid':untax+atax,
           'amount_return':0,
           'amount_tax':atax,
           'amount_total':untax+atax,
           'creation_date':fields.Datetime.to_string(fields.Datetime.now()),
           'fiscal_position_id':False,
           'pricelist_id':self.pos_config.available_pricelist_ids[0].id,
           'lines':[[0,
             0,
             {'discount':0,
              'id':3,
              'pack_lot_ids':[],
              'price_unit':1.28,
              'product_id':self.newspaper_rack.id,
              'price_subtotal':1.28,
              'price_subtotal_incl':1.47,
              'qty':1,
              'tax_ids':[[6,False,self.newspaper_rack.taxes_id.ids]]}]],
           'name':'Order00044-003-0014',
           'partner_id':False,
           'pos_session_id':current_session.id,
           'sequence_number':self.pos_config.journal_id.id,
           'statement_ids':[[0,
             0,
             {'amount':untax+atax,
              'name':fields.Datetime.now(),
              'payment_method_id':self.bank_payment_method.id}]],
           'uid':'00044-003-0014',
           'user_id':self.env.uid},
          'id':'00044-003-0014',
          'to_invoice':False}

        #Icreateanorderonanopensession
        self.PosOrder.create_from_ui([carrot_order])
        self.assertEqual(num_starting_orders+1,len(current_session.order_ids),"Submittedordernotencoded")

        #Iclosethesession
        current_session.action_pos_session_closing_control()
        self.assertEqual(current_session.state,'closed',"Sessionwasnotproperlyclosed")
        self.assertFalse(self.pos_config.current_session_id,"Currentsessionnotproperlyrecomputed")

        #Ikeepsellingafterthesessionisclosed
        withmute_logger('flectra.addons.point_of_sale.models.pos_order'):
            self.PosOrder.create_from_ui([zucchini_order,newspaper_rack_order])
        rescue_session=self.PosSession.search([
            ('config_id','=',self.pos_config.id),
            ('state','=','opened'),
            ('rescue','=',True)
        ])
        self.assertEqual(len(rescue_session),1,"One(andonlyone)rescuesessionshouldbecreatedfororphanorders")
        self.assertIn("(RESCUEFOR%s)"%current_session.name,rescue_session.name,"Rescuesessionisnotlinkedtothepreviousone")
        self.assertEqual(len(rescue_session.order_ids),2,"Rescuesessiondoesnotcontainbothorders")

        #Iclosetherescuesession
        rescue_session.action_pos_session_closing_control()
        self.assertEqual(rescue_session.state,'closed',"Rescuesessionwasnotproperlyclosed")

    deftest_order_to_payment_currency(self):
        """
            InordertotestthePointofSaleinmodule,Iwilldoafullflowfromthesaletothepaymentandinvoicing.
            Iwillusetwoproducts,onewithpriceincludinga10%tax,theotheronewith5%taxexcludedfromtheprice.
            Theorderwillbeinadifferentcurrencythanthecompanycurrency.
        """
        #MakesurethecompanyisinUSD
        self.env.cr.execute(
            "UPDATEres_companySETcurrency_id=%sWHEREid=%s",
            [self.env.ref('base.USD').id,self.env.company.id])

        #Demodataarecrappy,clean-uptherates
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name':'2010-01-01',
            'rate':2.0,
            'currency_id':self.env.ref('base.EUR').id,
        })

        #makeaconfigthathascurrencydifferentfromthecompany
        eur_pricelist=self.partner1.property_product_pricelist.copy(default={'currency_id':self.env.ref('base.EUR').id})
        sale_journal=self.env['account.journal'].create({
            'name':'PoSSaleEUR',
            'type':'sale',
            'code':'POSE',
            'company_id':self.company.id,
            'sequence':12,
            'currency_id':self.env.ref('base.EUR').id
        })
        eur_config=self.pos_config.create({
            'name':'ShopEURTest',
            'module_account':False,
            'journal_id':sale_journal.id,
            'use_pricelist':True,
            'available_pricelist_ids':[(6,0,eur_pricelist.ids)],
            'pricelist_id':eur_pricelist.id,
            'payment_method_ids':[(6,0,self.bank_payment_method.ids)]
        })

        #Iclickoncreateanewsessionbutton
        eur_config.open_session_cb(check_coa=False)
        current_session=eur_config.current_session_id

        #IcreateaPoSorderwith2unitsofPCSC234at450EUR(TaxIncl)
        #and3unitsofPCSC349at300EUR.(TaxExcl)

        untax1,atax1=self.compute_tax(self.product3,450,2)
        untax2,atax2=self.compute_tax(self.product4,300,3)
        self.pos_order_pos0=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'pricelist_id':eur_pricelist.id,
            'partner_id':self.partner1.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':0.0,
                'qty':2.0,
                'tax_ids':[(6,0,self.product3.taxes_id.filtered(lambdat:t.company_id==self.env.company).ids)],
                'price_subtotal':untax1,
                'price_subtotal_incl':untax1+atax1,
            }),(0,0,{
                'name':"OL/0002",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':0.0,
                'qty':3.0,
                'tax_ids':[(6,0,self.product4.taxes_id.filtered(lambdat:t.company_id==self.env.company).ids)],
                'price_subtotal':untax2,
                'price_subtotal_incl':untax2+atax2,
            })],
            'amount_tax':atax1+atax2,
            'amount_total':untax1+untax2+atax1+atax2,
            'amount_paid':0.0,
            'amount_return':0.0,
        })

        #Icheckthatthetotaloftheorderisnowequalto(450*2+
        #300*3*1.05)*0.95
        self.assertLess(
            abs(self.pos_order_pos0.amount_total-(450*2+300*3*1.05)),
            0.01,'Theorderhasawrongtotalincludingtaxanddiscounts')

        #Iclickonthe"MakePayment"wizardtopaythePoSorderwitha
        #partialamountof100.0EUR
        context_make_payment={"active_ids":[self.pos_order_pos0.id],"active_id":self.pos_order_pos0.id}
        self.pos_make_payment_0=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':100.0,
            'payment_method_id':self.bank_payment_method.id,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos0.id}
        self.pos_make_payment_0.with_context(context_payment).check()

        #Icheckthattheorderisnotmarkedaspaidyet
        self.assertEqual(self.pos_order_pos0.state,'draft','Ordershouldbeindraftstate.')

        #Onthesecondpaymentproposition,Icheckthatitproposesmethe
        #remainingbalancewhichis1790.0EUR
        defs=self.pos_make_payment_0.with_context({'active_id':self.pos_order_pos0.id}).default_get(['amount'])

        self.assertLess(
            abs(defs['amount']-((450*2+300*3*1.05)-100.0)),0.01,"Theremainingbalanceisincorrect.")

        #'Ipaytheremainingbalance.
        context_make_payment={
            "active_ids":[self.pos_order_pos0.id],"active_id":self.pos_order_pos0.id}

        self.pos_make_payment_1=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':(450*2+300*3*1.05)-100.0,
            'payment_method_id':self.bank_payment_method.id,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        self.pos_make_payment_1.with_context(context_make_payment).check()

        #Icheckthattheorderismarkedaspaid
        self.assertEqual(self.pos_order_pos0.state,'paid','Ordershouldbeinpaidstate.')

        #Igeneratethejournalentries
        current_session.action_pos_session_validate()

        #ItestthatthegeneratedjournalentryisattachedtothePoSorder
        self.assertTrue(current_session.move_id,"Journalentryshouldhavebeenattachedtothesession.")

        #Checktheamounts
        debit_lines=current_session.move_id.mapped('line_ids.debit')
        credit_lines=current_session.move_id.mapped('line_ids.credit')
        amount_currency_lines=current_session.move_id.mapped('line_ids.amount_currency')
        fora,binzip(sorted(debit_lines),[0.0,0.0,0.0,0.0,922.5]):
            self.assertAlmostEqual(a,b)
        fora,binzip(sorted(credit_lines),[0.0,22.5,40.91,409.09,450]):
            self.assertAlmostEqual(a,b)
        fora,binzip(sorted(amount_currency_lines),[-900,-818.18,-81.82,-45,1845]):
            self.assertAlmostEqual(a,b)

    deftest_order_to_invoice_no_tax(self):
        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id

        #IcreateanewPoSorderwith2unitsofPC1at450EUR(TaxIncl)and3unitsofPCSC349at300EUR.(TaxExcl)
        self.pos_order_pos1=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':5.0,
                'qty':2.0,
                'price_subtotal':855,
                'price_subtotal_incl':855,
            }),(0,0,{
                'name':"OL/0002",
                'product_id':self.product4.id,
                'price_unit':300,
                'discount':5.0,
                'qty':3.0,
                'price_subtotal':855,
                'price_subtotal_incl':855,
            })],
            'amount_tax':855*2,
            'amount_total':855*2,
            'amount_paid':0.0,
            'amount_return':0.0,
        })

        #Iclickonthe"MakePayment"wizardtopaythePoSorder
        context_make_payment={"active_ids":[self.pos_order_pos1.id],"active_id":self.pos_order_pos1.id}
        self.pos_make_payment=self.PosMakePayment.with_context(context_make_payment).create({
            'amount':855*2,
        })
        #Iclickonthevalidatebuttontoregisterthepayment.
        context_payment={'active_id':self.pos_order_pos1.id}
        self.pos_make_payment.with_context(context_payment).check()

        #Icheckthattheorderismarkedaspaidandthereisnoinvoice
        #attachedtoit
        self.assertEqual(self.pos_order_pos1.state,'paid',"Ordershouldbeinpaidstate.")
        self.assertFalse(self.pos_order_pos1.account_move,'Invoiceshouldnotbeattachedtoorderyet.')

        #Igenerateaninvoicefromtheorder
        res=self.pos_order_pos1.action_pos_order_invoice()
        self.assertIn('res_id',res,"Noinvoicecreated")

        #Itestthatthetotaloftheattachedinvoiceiscorrect
        invoice=self.env['account.move'].browse(res['res_id'])
        ifinvoice.state!='posted':
            invoice.action_post()
        self.assertAlmostEqual(
            invoice.amount_total,self.pos_order_pos1.amount_total,places=2,msg="Invoicenotcorrect")

        forilineininvoice.invoice_line_ids:
            self.assertFalse(iline.tax_ids)

        self.pos_config.current_session_id.action_pos_session_closing_control()

    deftest_order_with_deleted_tax(self):
        #createtax
        dummy_50_perc_tax=self.env['account.tax'].create({
            'name':'Tax50%',
            'amount_type':'percent',
            'amount':50.0,
            'price_include':0
        })

        #settaxtoproduct
        product5=self.env['product.product'].create({
            'name':'product5',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'taxes_id':dummy_50_perc_tax.ids
        })

        #sellproductthrupos
        self.pos_config.open_session_cb(check_coa=False)
        pos_session=self.pos_config.current_session_id
        untax,atax=self.compute_tax(product5,10.0)
        product5_order={'data':
          {'amount_paid':untax+atax,
           'amount_return':0,
           'amount_tax':atax,
           'amount_total':untax+atax,
           'creation_date':fields.Datetime.to_string(fields.Datetime.now()),
           'fiscal_position_id':False,
           'pricelist_id':self.pos_config.available_pricelist_ids[0].id,
           'lines':[[0,
             0,
             {'discount':0,
              'id':42,
              'pack_lot_ids':[],
              'price_unit':10.0,
              'product_id':product5.id,
              'price_subtotal':10.0,
              'price_subtotal_incl':15.0,
              'qty':1,
              'tax_ids':[(6,0,product5.taxes_id.ids)]}]],
           'name':'Order12345-123-1234',
           'partner_id':False,
           'pos_session_id':pos_session.id,
           'sequence_number':2,
           'statement_ids':[[0,
             0,
             {'amount':untax+atax,
              'name':fields.Datetime.now(),
              'payment_method_id':self.cash_payment_method.id}]],
           'uid':'12345-123-1234',
           'user_id':self.env.uid},
          'id':'12345-123-1234',
          'to_invoice':False}
        self.PosOrder.create_from_ui([product5_order])

        #deletetax
        dummy_50_perc_tax.unlink()

        #closesession(shouldnotfailhere)
        pos_session.action_pos_session_closing_control()

        #checkthedifferenceline
        diff_line=pos_session.move_id.line_ids.filtered(lambdaline:line.name=='DifferenceatclosingPoSsession')
        self.assertAlmostEqual(diff_line.credit,5.0,msg="Missingamountof5.0")

    deftest_order_refund_picking(self):
        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id
        current_session.update_stock_at_closing=True
        #IcreateanewPoSorderwith1line
        order=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':self.product3.id,
                'price_unit':450,
                'discount':5.0,
                'qty':2.0,
                'tax_ids':[(6,0,self.product3.taxes_id.ids)],
                'price_subtotal':450*(1-5/100.0)*2,
                'price_subtotal_incl':450*(1-5/100.0)*2,
            })],
            'amount_total':1710.0,
            'amount_tax':0.0,
            'amount_paid':0.0,
            'amount_return':0.0,
            'to_invoice':True
        })

        payment_context={"active_ids":order.ids,"active_id":order.id}
        order_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':order.amount_total,
            'payment_method_id':self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()

        #Icreatearefund
        refund_action=order.refund()
        refund=self.PosOrder.browse(refund_action['res_id'])

        payment_context={"active_ids":refund.ids,"active_id":refund.id}
        refund_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':refund.amount_total,
            'payment_method_id':self.cash_payment_method.id,
        })

        #Iclickonthevalidatebuttontoregisterthepayment.
        refund_payment.with_context(**payment_context).check()

        refund.action_pos_order_invoice()
        self.assertEqual(refund.picking_count,1)

    deftest_journal_entries_category_without_account(self):
        #createanewproductcategorywithoutaccount
        category=self.env['product.category'].create({
            'name':'Categorywithoutaccount',
            'property_account_income_categ_id':False,
            'property_account_expense_categ_id':False,
        })
        product=self.env['product.product'].create({
            'name':'Productwithcategorywithoutaccount',
            'type':'product',
            'categ_id':category.id,
        })
        account=self.env['account.account'].create({
            'name':'Accountforcategorywithoutaccount',
            'code':'X1111',
            'user_type_id':self.env.ref('account.data_account_type_revenue').id,
            'reconcile':True,
        })

        self.pos_config.journal_id.default_account_id=account.id
        #createanewposorderwiththeproduct
        self.pos_config.open_session_cb(check_coa=False)
        current_session=self.pos_config.current_session_id
        order=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'pricelist_id':self.partner1.property_product_pricelist.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id':product.id,
                'price_unit':10,
                'discount':0.0,
                'qty':1,
                'tax_ids':[],
                'price_subtotal':10,
                'price_subtotal_incl':10,
            })],
            'amount_total':10,
            'amount_tax':0.0,
            'amount_paid':10,
            'amount_return':0.0,
            'to_invoice':True
        })
        #createapayment
        payment_context={"active_ids":order.ids,"active_id":order.id}
        order_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':order.amount_total,
            'payment_method_id':self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()
        current_session.action_pos_session_closing_control()
        self.assertEqual(current_session.move_id.line_ids[0].account_id.id,account.id)

    deftest_tracked_product_with_owner(self):
        #openpossession
        self.pos_config.open_session_cb()
        current_session=self.pos_config.current_session_id

        #setupproductiwithSNtracingandcreatetwolots(1001,1002)
        self.stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.product2=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'tracking':'serial',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        lot1=self.env['stock.production.lot'].create({
            'name':'1001',
            'product_id':self.product2.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(self.product2,self.stock_location,1,lot_id=lot1,owner_id=self.partner1)


        #createposorderwiththetwoSNcreatedbefore

        order=self.PosOrder.create({
            'company_id':self.env.company.id,
            'session_id':current_session.id,
            'partner_id':self.partner1.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'id':1,
                'product_id':self.product2.id,
                'price_unit':6,
                'discount':0,
                'qty':1,
                'tax_ids':[[6,False,[]]],
                'price_subtotal':6,
                'price_subtotal_incl':6,
                'pack_lot_ids':[
                    [0,0,{'lot_name':'1001'}],
                ]
            })],
            'pricelist_id':self.pos_config.pricelist_id.id,
            'amount_paid':6.0,
            'amount_total':6.0,
            'amount_tax':0.0,
            'amount_return':0.0,
            'to_invoice':False,
            })

        payment_context={"active_ids":order.ids,"active_id":order.id}
        order_payment=self.PosMakePayment.with_context(**payment_context).create({
            'amount':order.amount_total,
            'payment_method_id':self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()
        current_session.action_pos_session_closing_control()
        self.assertEqual(current_session.picking_ids.move_line_ids.owner_id.id,self.partner1.id)
