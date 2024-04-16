#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importre
fromdatetimeimportdatetime,timedelta
fromfreezegunimportfreeze_time

fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT
fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimportForm,tagged


@freeze_time("2021-01-1409:12:15")
@tagged('post_install','-at_install')
classTestPurchaseOrder(ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.product_id_1=cls.env['product.product'].create({'name':'LargeDesk','purchase_method':'purchase'})
        cls.product_id_2=cls.env['product.product'].create({'name':'ConferenceChair','purchase_method':'purchase'})

        cls.po_vals={
            'partner_id':cls.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':cls.product_id_1.name,
                    'product_id':cls.product_id_1.id,
                    'product_qty':5.0,
                    'product_uom':cls.product_id_1.uom_po_id.id,
                    'price_unit':500.0,
                    'date_planned':datetime.today().replace(hour=9).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0,0,{
                    'name':cls.product_id_2.name,
                    'product_id':cls.product_id_2.id,
                    'product_qty':5.0,
                    'product_uom':cls.product_id_2.uom_po_id.id,
                    'price_unit':250.0,
                    'date_planned':datetime.today().replace(hour=9).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }

    deftest_update_price_unit(self):
        self.po_vals["order_line"]=[self.po_vals["order_line"][0]]
        #weonlyneedonepurchaselineforthistest
        po=self.env['purchase.order'].create(self.po_vals)
        pol=po.order_line[0]
        po.button_confirm()
        self.assertEqual(len(pol.move_ids),1)
        self.assertEqual(pol.move_ids[0].price_unit,500)
        pol.price_unit=1
        self.assertEqual(pol.price_unit,1)
        #linebelowshouldn'tfail
        self.assertEqual(pol.move_ids[0].price_unit,1)

    deftest_00_purchase_order_flow(self):
        #Ensureproduct_id_2doesn'thaveres_partner_1assupplier
        ifself.partner_ainself.product_id_2.seller_ids.mapped('name'):
            id_to_remove=self.product_id_2.seller_ids.filtered(lambdar:r.name==self.partner_a).ids[0]ifself.product_id_2.seller_ids.filtered(lambdar:r.name==self.partner_a)elseFalse
            ifid_to_remove:
                self.product_id_2.write({
                    'seller_ids':[(2,id_to_remove,False)],
                })
        self.assertFalse(self.product_id_2.seller_ids.filtered(lambdar:r.name==self.partner_a),'Purchase:thepartnershouldnotbeinthelistoftheproductsuppliers')

        self.po=self.env['purchase.order'].create(self.po_vals)
        self.assertTrue(self.po,'Purchase:nopurchaseordercreated')
        self.assertEqual(self.po.invoice_status,'no','Purchase:POinvoice_statusshouldbe"Notpurchased"')
        self.assertEqual(self.po.order_line.mapped('qty_received'),[0.0,0.0],'Purchase:noproductshouldbereceived"')
        self.assertEqual(self.po.order_line.mapped('qty_invoiced'),[0.0,0.0],'Purchase:noproductshouldbeinvoiced"')

        self.po.button_confirm()
        self.assertEqual(self.po.state,'purchase','Purchase:POstateshouldbe"Purchase"')
        self.assertEqual(self.po.invoice_status,'toinvoice','Purchase:POinvoice_statusshouldbe"WaitingInvoices"')

        self.assertTrue(self.product_id_2.seller_ids.filtered(lambdar:r.name==self.partner_a),'Purchase:thepartnershouldbeinthelistoftheproductsuppliers')

        seller=self.product_id_2._select_seller(partner_id=self.partner_a,quantity=2.0,date=self.po.date_planned,uom_id=self.product_id_2.uom_po_id)
        price_unit=seller.priceifsellerelse0.0
        ifprice_unitandsellerandself.po.currency_idandseller.currency_id!=self.po.currency_id:
            price_unit=seller.currency_id._convert(price_unit,self.po.currency_id,self.po.company_id,self.po.date_order)
        self.assertEqual(price_unit,250.0,'Purchase:thepriceoftheproductforthesuppliershouldbe250.0.')

        self.assertEqual(self.po.picking_count,1,'Purchase:onepickingshouldbecreated"')
        self.picking=self.po.picking_ids[0]
        self.picking.move_line_ids.write({'qty_done':5.0})
        self.picking.button_validate()
        self.assertEqual(self.po.order_line.mapped('qty_received'),[5.0,5.0],'Purchase:allproductsshouldbereceived"')

        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.partner_id=self.partner_a
        move_form.purchase_id=self.po
        self.invoice=move_form.save()

        self.assertEqual(self.po.order_line.mapped('qty_invoiced'),[5.0,5.0],'Purchase:allproductsshouldbeinvoiced"')

    deftest_02_po_return(self):
        """
        TestaPOwithaproductonIncomingshipment.ValidatethePO,thendoareturn
        ofthepickingwithRefund.
        """
        #Draftpurchaseordercreated
        self.po=self.env['purchase.order'].create(self.po_vals)
        self.assertTrue(self.po,'Purchase:nopurchaseordercreated')
        self.assertEqual(self.po.order_line.mapped('qty_received'),[0.0,0.0],'Purchase:noproductshouldbereceived"')
        self.assertEqual(self.po.order_line.mapped('qty_invoiced'),[0.0,0.0],'Purchase:noproductshouldbeinvoiced"')

        self.po.button_confirm()
        self.assertEqual(self.po.state,'purchase','Purchase:POstateshouldbe"Purchase"')
        self.assertEqual(self.po.invoice_status,'toinvoice','Purchase:POinvoice_statusshouldbe"WaitingInvoices"')

        #Confirmthepurchaseorder
        self.po.button_confirm()
        self.assertEqual(self.po.state,'purchase','Purchase:POstateshouldbe"Purchase')
        self.assertEqual(self.po.picking_count,1,'Purchase:onepickingshouldbecreated"')
        self.picking=self.po.picking_ids[0]
        self.picking.move_line_ids.write({'qty_done':5.0})
        self.picking.button_validate()
        self.assertEqual(self.po.order_line.mapped('qty_received'),[5.0,5.0],'Purchase:allproductsshouldbereceived"')

        #AfterReceivingallproductscreatevendorbill.
        move_form=Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=self.partner_a
        move_form.purchase_id=self.po
        self.invoice=move_form.save()
        self.invoice.action_post()

        self.assertEqual(self.po.order_line.mapped('qty_invoiced'),[5.0,5.0],'Purchase:allproductsshouldbeinvoiced"')

        #Checkquantityreceived
        received_qty=sum(pol.qty_receivedforpolinself.po.order_line)
        self.assertEqual(received_qty,10.0,'Purchase:Receivedquantityshouldbe10.0insteadof%saftervalidatingincomingshipment'%received_qty)

        #Createreturnpicking
        pick=self.po.picking_ids
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=pick.ids,active_id=pick.ids[0],
            active_model='stock.picking'))
        return_wiz=stock_return_picking_form.save()
        return_wiz.product_return_moves.write({'quantity':2.0,'to_refund':True}) #Returnonly2
        res=return_wiz.create_returns()
        return_pick=self.env['stock.picking'].browse(res['res_id'])

        #Validatepicking
        return_pick.move_line_ids.write({'qty_done':2})

        return_pick.button_validate()

        #CheckReceivedquantity
        self.assertEqual(self.po.order_line[0].qty_received,3.0,'Purchase:deliveredquantityshouldbe3.0insteadof"%s"afterpickingreturn'%self.po.order_line[0].qty_received)
        #Createvendorbillforrefundqty
        move_form=Form(self.env['account.move'].with_context(default_move_type='in_refund'))
        move_form.invoice_date=move_form.date
        move_form.partner_id=self.partner_a
        move_form.purchase_id=self.po
        self.invoice=move_form.save()
        move_form=Form(self.invoice)
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.quantity=2.0
        withmove_form.invoice_line_ids.edit(1)asline_form:
            line_form.quantity=2.0
        self.invoice=move_form.save()
        self.invoice.action_post()

        self.assertEqual(self.po.order_line.mapped('qty_invoiced'),[3.0,3.0],'Purchase:Billedquantityshouldbe3.0')

    deftest_03_po_return_and_modify(self):
        """Changethepickingcodeofthedeliverytointernal.MakeaPOfor10units,gotothe
        pickingandreturn5,editthePOlineto15units.
        Thepurposeofthetestistochecktheconsistenciesacrossthereceivedquantitiesandthe
        procurementquantities.
        """
        #Changethecodeofthepickingtypedelivery
        self.env['stock.picking.type'].search([('code','=','outgoing')]).write({'code':'internal'})

        #Sellanddeliver10units
        item1=self.product_id_1
        uom_unit=self.env.ref('uom.product_uom_unit')
        po1=self.env['purchase.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':item1.name,
                    'product_id':item1.id,
                    'product_qty':10,
                    'product_uom':uom_unit.id,
                    'price_unit':123.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
            ],
        })
        po1.button_confirm()

        picking=po1.picking_ids
        wiz_act=picking.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        #Return5units
        stock_return_picking_form=Form(self.env['stock.return.picking'].with_context(
            active_ids=picking.ids,
            active_id=picking.ids[0],
            active_model='stock.picking'
        ))
        return_wiz=stock_return_picking_form.save()
        forreturn_moveinreturn_wiz.product_return_moves:
            return_move.write({
                'quantity':5,
                'to_refund':True
            })
        res=return_wiz.create_returns()
        return_pick=self.env['stock.picking'].browse(res['res_id'])
        wiz_act=return_pick.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        self.assertEqual(po1.order_line.qty_received,5)

        #Deliver15insteadof10.
        po1.write({
            'order_line':[
                (1,po1.order_line[0].id,{'product_qty':15}),
            ]
        })

        #Anewmoveof10unit(15-5units)
        self.assertEqual(po1.order_line.qty_received,5)
        self.assertEqual(po1.picking_ids[-1].move_lines.product_qty,10)

    deftest_04_update_date_planned(self):
        today=datetime.today().replace(hour=9,microsecond=0)
        tomorrow=datetime.today().replace(hour=9,microsecond=0)+timedelta(days=1)
        po=self.env['purchase.order'].create(self.po_vals)
        po.button_confirm()

        #updatefirstline
        po._update_date_planned_for_lines([(po.order_line[0],tomorrow)])
        self.assertEqual(po.order_line[0].date_planned,tomorrow)
        activity=self.env['mail.activity'].search([
            ('summary','=','DateUpdated'),
            ('res_model_id','=','purchase.order'),
            ('res_id','=',po.id),
        ])
        self.assertTrue(activity)
        self.assertIn(
            '<p>partner_amodifiedreceiptdatesforthefollowingproducts:</p><p>\xa0-LargeDeskfrom%sto%s</p><p>Thosedateshavebeenupdatedaccordinglyonthereceipt%s.</p>'%(today.date(),tomorrow.date(),po.picking_ids.name),
            activity.note,
        )

        #receiveproducts
        wiz_act=po.picking_ids.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        #updatesecondline
        old_date=po.order_line[1].date_planned
        po._update_date_planned_for_lines([(po.order_line[1],tomorrow)])
        self.assertEqual(po.order_line[1].date_planned,old_date)
        self.assertIn(
            '<p>partner_amodifiedreceiptdatesforthefollowingproducts:</p><p>\xa0-LargeDeskfrom%sto%s</p><p>\xa0-ConferenceChairfrom%sto%s</p><p>Thosedatescouldn’tbemodifiedaccordinglyonthereceipt%swhichhadalreadybeenvalidated.</p>'%(today.date(),tomorrow.date(),today.date(),tomorrow.date(),po.picking_ids.name),
            activity.note,
        )

    deftest_05_multi_company(self):
        company_a=self.env.user.company_id
        company_b=self.env['res.company'].create({
            "name":"TestCompany",
            "currency_id":self.env['res.currency'].with_context(active_test=False).search([
                ('id','!=',company_a.currency_id.id),
            ],limit=1).id
        })
        self.env.user.write({
            'company_id':company_b.id,
            'company_ids':[(4,company_b.id),(4,company_a.id)],
        })
        po=self.env['purchase.order'].create(dict(company_id=company_a.id,partner_id=self.partner_a.id))

        self.assertEqual(po.company_id,company_a)
        self.assertEqual(po.picking_type_id.warehouse_id.company_id,company_a)
        self.assertEqual(po.currency_id,po.company_id.currency_id)

    deftest_06_on_time_rate(self):
        company_a=self.env.user.company_id
        company_b=self.env['res.company'].create({
            "name":"TestCompany",
            "currency_id":self.env['res.currency'].with_context(active_test=False).search([
                ('id','!=',company_a.currency_id.id),
            ],limit=1).id
        })

        #Createapurchaseorderwith90%qtyreceivedforcompanyA
        self.env.user.write({
            'company_id':company_a.id,
            'company_ids':[(6,0,[company_a.id])],
        })
        po=self.env['purchase.order'].create(self.po_vals)
        po.order_line.write({'product_qty':10})
        po.button_confirm()
        picking=po.picking_ids[0]
        #Process9.0outofthe10.0orderedqty
        picking.move_line_ids.write({'qty_done':9.0})
        res_dict=picking.button_validate()
        #Nobackorder
        self.env['stock.backorder.confirmation'].with_context(res_dict['context']).process_cancel_backorder()
        #`on_time_rate`shouldbeequalstotheratioofquantityreceivedagainstquantityordered
        expected_rate=sum(picking.move_line_ids.mapped("qty_done"))/sum(po.order_line.mapped("product_qty"))*100
        self.assertEqual(expected_rate,po.on_time_rate)

        #Createapurchaseorderwith80%qtyreceivedforcompanyB
        #TheOn-TimeDeliveryRateshouldn'tbesharedaccrossmultiplecompanies
        self.env.user.write({
            'company_id':company_b.id,
            'company_ids':[(6,0,[company_b.id])],
        })
        po=self.env['purchase.order'].create(self.po_vals)
        po.order_line.write({'product_qty':10})
        po.button_confirm()
        picking=po.picking_ids[0]
        #Process8.0outofthe10.0orderedqty
        picking.move_line_ids.write({'qty_done':8.0})
        res_dict=picking.button_validate()
        #Nobackorder
        self.env['stock.backorder.confirmation'].with_context(res_dict['context']).process_cancel_backorder()
        #`on_time_rate`shouldbeequaltotheratioofquantityreceivedagainstquantityordered
        expected_rate=sum(picking.move_line_ids.mapped("qty_done"))/sum(po.order_line.mapped("product_qty"))*100
        self.assertEqual(expected_rate,po.on_time_rate)

        #Trickycornercase
        #As`purchase.order.on_time_rate`isarelatedto`partner_id.on_time_rate`
        #`on_time_rate`onthePOshouldequals`on_time_rate`onthepartner.
        #Relatedfieldsarebydefaultcomputedassudo
        #whilenon-storedcomputedfieldsarenotcomputedassudobydefault
        #Ifthecomputationoftherelatedfield(`purchase.order.on_time_rate`)wasasked
        #and`res.partner.on_time_rate`wasnotyetinthecache
        #the`sudo`requestedforthecomputationoftherelated`purchase.order.on_time_rate`
        #waspropagatedtothecomputationof`res.partner.on_time_rate`
        #andthereforethemulti-companyrecordruleswereignored.
        #1.Compute`res.partner.on_time_rate`regularnon-storedcomptuedfield
        partner_on_time_rate=po.partner_id.on_time_rate
        #2.Invalidatethecacheforthatrecordandfield,soit'snotreusedinthenextstep.
        po.partner_id.invalidate_cache(fnames=["on_time_rate"],ids=po.partner_id.ids)
        #3.Computetherelatedfield`purchase.order.on_time_rate`
        po_on_time_rate=po.on_time_rate
        #4.Checkbothareequals.
        self.assertEqual(partner_on_time_rate,po_on_time_rate)

    deftest_04_multi_uom(self):
        yards_uom=self.env['uom.uom'].create({
            'category_id':self.env.ref('uom.uom_categ_length').id,
            'name':'Yards',
            'factor_inv':0.9144,
            'uom_type':'bigger',
        })
        self.product_id_2.write({
            'uom_id':self.env.ref('uom.product_uom_meter').id,
            'uom_po_id':yards_uom.id,
        })
        po=self.env['purchase.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.product_id_2.name,
                    'product_id':self.product_id_2.id,
                    'product_qty':4.0,
                    'product_uom':self.product_id_2.uom_po_id.id,
                    'price_unit':1.0,
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ],
        })
        po.button_confirm()
        picking=po.picking_ids[0]
        picking.move_line_ids.write({'qty_done':3.66})
        picking.button_validate()
        self.assertEqual(po.order_line.mapped('qty_received'),[4.0],'Purchase:noconversionerroronreceiptindifferentuom"')

    deftest_message_qty_already_received(self):
        _product=self.env['product.product'].create({
            'name':'TempProduct',
            'type':'consu',
            'company_id':self.env.user.company_id.id,
        })

        _purchase_order=self.env['purchase.order'].create({
            'company_id':self.env.user.company_id.id,
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':_product.name,
                    'product_id':_product.id,
                    'product_qty':25.0,
                    'price_unit':250.0,
                })],
        })

        _purchase_order.button_confirm()

        first_picking=_purchase_order.picking_ids[0]
        first_picking.move_lines.quantity_done=5
        backorder_wizard_dict=first_picking.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        second_picking=_purchase_order.picking_ids[1]
        second_picking.move_lines.quantity_done=5
        backorder_wizard_dict=second_picking.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        third_picking=_purchase_order.picking_ids[2]
        third_picking.move_lines.quantity_done=5
        backorder_wizard_dict=third_picking.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        _message_content=_purchase_order.message_ids.mapped("body")[0]
        self.assertIsNotNone(re.search(r"ReceivedQuantity:5.0-&gt;10.0",_message_content),"Alreadyreceivedquantityisn'tcorrectlytakenintoconsideration")

    deftest_pol_description(self):
        """
        Supposeaproductwithseveralsellers,allwiththesamepartner.Onthepurchaseorder,theproduct
        descriptionshouldbebasedonthecorrectseller
        """
        self.env.user.write({'company_id':self.company_data['company'].id})

        product=self.env['product.product'].create({
            'name':'SuperProduct',
            'seller_ids':[(0,0,{
                'name':self.partner_a.id,
                'min_qty':1,
                'price':10,
                'product_code':'C01',
                'product_name':'Name01',
                'sequence':1,
            }),(0,0,{
                'name':self.partner_a.id,
                'min_qty':20,
                'price':2,
                'product_code':'C02',
                'product_name':'Name02',
                'sequence':2,
            })]
        })

        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=product
        orderpoint_form.product_min_qty=1
        orderpoint_form.product_max_qty=0.000
        order_point=orderpoint_form.save()

        self.env['procurement.group'].run_scheduler()

        pol=self.env['purchase.order.line'].search([('product_id','=',product.id)])
        self.assertEqual(pol.name,"[C01]Name01")

        withForm(pol.order_id)aspo_form:
            withpo_form.order_line.edit(0)aspol_form:
                pol_form.product_qty=25
        self.assertEqual(pol.name,"[C02]Name02")
