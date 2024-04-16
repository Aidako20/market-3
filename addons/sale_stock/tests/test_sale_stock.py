#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,timedelta

fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.addons.sale.tests.commonimportTestSaleCommon
fromflectra.exceptionsimportUserError
fromflectra.testsimportForm,tagged
fromflectra.tests.commonimportSavepointCase


@tagged('post_install','-at_install')
classTestSaleStock(TestSaleCommon,ValuationReconciliationTestCommon):

    def_get_new_sale_order(self,amount=10.0,product=False):
        """Createsandreturnsasaleorderwithonedefaultorderline.

        :paramfloatamount:quantityofproductfortheorderline(10bydefault)
        """
        product=productorself.company_data['product_delivery_no']
        sale_order_vals={
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':amount,
                'product_uom':product.uom_id.id,
                'price_unit':product.list_price})],
            'pricelist_id':self.company_data['default_pricelist'].id,
        }
        sale_order=self.env['sale.order'].create(sale_order_vals)
        returnsale_order

    deftest_00_sale_stock_invoice(self):
        """
        TestSO'schangeswhenplayingaroundwithstockmoves,quants,packoperations,pickings
        andwhateverothermodelthereisinstockwith"invoiceondelivery"products
        """
        self.so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':p.name,
                    'product_id':p.id,
                    'product_uom_qty':2,
                    'product_uom':p.uom_id.id,
                    'price_unit':p.list_price,
                })forpin(
                    self.company_data['product_order_no'],
                    self.company_data['product_service_delivery'],
                    self.company_data['product_service_order'],
                    self.company_data['product_delivery_no'],
                )],
            'pricelist_id':self.company_data['default_pricelist'].id,
            'picking_policy':'direct',
        })

        #confirmourstandardso,checkthepicking
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids,'SaleStock:nopickingcreatedfor"invoiceondelivery"storableproducts')
        #invoiceonorder
        self.so._create_invoices()

        #deliverpartially,checktheso'sinvoice_statusanddeliveredquantities
        self.assertEqual(self.so.invoice_status,'no','SaleStock:soinvoice_statusshouldbe"nothingtoinvoice"afterinvoicing')
        pick=self.so.picking_ids
        pick.move_lines.write({'quantity_done':1})
        wiz_act=pick.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()
        self.assertEqual(self.so.invoice_status,'toinvoice','SaleStock:soinvoice_statusshouldbe"toinvoice"afterpartialdelivery')
        del_qties=[sol.qty_deliveredforsolinself.so.order_line]
        del_qties_truth=[1.0ifsol.product_id.typein['product','consu']else0.0forsolinself.so.order_line]
        self.assertEqual(del_qties,del_qties_truth,'SaleStock:deliveredquantitiesarewrongafterpartialdelivery')
        #invoiceondelivery:onlystorableproducts
        inv_1=self.so._create_invoices()
        self.assertTrue(all([il.product_id.invoice_policy=='delivery'forilininv_1.invoice_line_ids]),
                        'SaleStock:invoiceshouldonlycontain"invoiceondelivery"products')

        #completethedeliveryandcheckinvoice_statusagain
        self.assertEqual(self.so.invoice_status,'no',
                         'SaleStock:soinvoice_statusshouldbe"nothingtoinvoice"afterpartialdeliveryandinvoicing')
        self.assertEqual(len(self.so.picking_ids),2,'SaleStock:numberofpickingsshouldbe2')
        pick_2=self.so.picking_ids.filtered('backorder_id')
        pick_2.move_lines.write({'quantity_done':1})
        self.assertTrue(pick_2.button_validate(),'SaleStock:secondpickingshouldbefinalwithoutneedforabackorder')
        self.assertEqual(self.so.invoice_status,'toinvoice','SaleStock:soinvoice_statusshouldbe"toinvoice"aftercompletedelivery')
        del_qties=[sol.qty_deliveredforsolinself.so.order_line]
        del_qties_truth=[2.0ifsol.product_id.typein['product','consu']else0.0forsolinself.so.order_line]
        self.assertEqual(del_qties,del_qties_truth,'SaleStock:deliveredquantitiesarewrongaftercompletedelivery')
        #Withouttimesheet,wemanuallysetthedeliveredqtyfortheproductserv_del
        self.so.order_line.sorted()[1]['qty_delivered']=2.0
        #Thereisabugwith`new`and`_origin`
        #Ifyoucreateafirstnewfromarecord,thenchangeavalueontheoriginrecord,thancreateanothernew,
        #thisothernewwonthavetheupdatedvalueoftheoriginrecord,buttheonefromthepreviousnew
        #Heretheproblemliesintheuseof`new`in`move=self_ctx.new(new_vals)`,
        #andthefactthismethodiscalledmultipletimesinthesametransactiontestcase.
        #Here,weupdate`qty_delivered`ontheoriginrecord,butthe`new`recordswhichareincachewiththisorderline
        #asoriginarenotupdated,northefieldsthatdependsonit.
        self.so.flush()
        forfieldinself.env['sale.order.line']._fields.values():
            forres_idinlist(self.env.cache._data[field]):
                ifnotres_id:
                    self.env.cache._data[field].pop(res_id)
        inv_id=self.so._create_invoices()
        self.assertEqual(self.so.invoice_status,'invoiced',
                         'SaleStock:soinvoice_statusshouldbe"fullyinvoiced"aftercompletedeliveryandinvoicing')

    deftest_01_sale_stock_order(self):
        """
        TestSO'schangeswhenplayingaroundwithstockmoves,quants,packoperations,pickings
        andwhateverothermodelthereisinstockwith"invoiceonorder"products
        """
        #let'scheatandputallourproductsto"invoiceonorder"
        self.so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[(0,0,{
                'name':p.name,
                'product_id':p.id,
                'product_uom_qty':2,
                'product_uom':p.uom_id.id,
                'price_unit':p.list_price,
                })forpin(
                    self.company_data['product_order_no'],
                    self.company_data['product_service_delivery'],
                    self.company_data['product_service_order'],
                    self.company_data['product_delivery_no'],
                )],
            'pricelist_id':self.company_data['default_pricelist'].id,
            'picking_policy':'direct',
        })
        forsolinself.so.order_line:
            sol.product_id.invoice_policy='order'
        #confirmourstandardso,checkthepicking
        self.so.order_line._compute_product_updatable()
        self.assertTrue(self.so.order_line.sorted()[0].product_updatable)
        self.so.action_confirm()
        self.so.order_line._compute_product_updatable()
        self.assertFalse(self.so.order_line.sorted()[0].product_updatable)
        self.assertTrue(self.so.picking_ids,'SaleStock:nopickingcreatedfor"invoiceonorder"storableproducts')
        #let'sdoaninvoiceforadepositof5%

        advance_product=self.env['product.product'].create({
            'name':'Deposit',
            'type':'service',
            'invoice_policy':'order',
        })
        adv_wiz=self.env['sale.advance.payment.inv'].with_context(active_ids=[self.so.id]).create({
            'advance_payment_method':'percentage',
            'amount':5.0,
            'product_id':advance_product.id,
        })
        act=adv_wiz.with_context(open_invoices=True).create_invoices()
        inv=self.env['account.move'].browse(act['res_id'])
        self.assertEqual(inv.amount_untaxed,self.so.amount_untaxed*5.0/100.0,'SaleStock:depositinvoiceiswrong')
        self.assertEqual(self.so.invoice_status,'toinvoice','SaleStock:soshouldbetoinvoiceafterinvoicingdeposit')
        #invoiceonorder:everythingshouldbeinvoiced
        self.so._create_invoices(final=True)
        self.assertEqual(self.so.invoice_status,'invoiced','SaleStock:soshouldbefullyinvoicedaftersecondinvoice')

        #deliver,checkthedeliveredquantities
        pick=self.so.picking_ids
        pick.move_lines.write({'quantity_done':2})
        self.assertTrue(pick.button_validate(),'SaleStock:completedeliveryshouldnotneedabackorder')
        del_qties=[sol.qty_deliveredforsolinself.so.order_line]
        del_qties_truth=[2.0ifsol.product_id.typein['product','consu']else0.0forsolinself.so.order_line]
        self.assertEqual(del_qties,del_qties_truth,'SaleStock:deliveredquantitiesarewrongafterpartialdelivery')
        #invoiceondelivery:nothingtoinvoice
        withself.assertRaises(UserError):
            self.so._create_invoices()

    deftest_02_sale_stock_return(self):
        """
        TestaSOwithaproductinvoicedondelivery.DeliverandinvoicetheSO,thendoareturn
        ofthepicking.Checkthatarefundinvoiceiswellgenerated.
        """
        #intialso
        self.product=self.company_data['product_delivery_no']
        so_vals={
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[(0,0,{
                'name':self.product.name,
                'product_id':self.product.id,
                'product_uom_qty':5.0,
                'product_uom':self.product.uom_id.id,
                'price_unit':self.product.list_price})],
            'pricelist_id':self.company_data['default_pricelist'].id,
        }
        self.so=self.env['sale.order'].create(so_vals)

        #confirmourstandardso,checkthepicking
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids,'SaleStock:nopickingcreatedfor"invoiceondelivery"storableproducts')

        #invoiceinondelivery,nothingshouldbeinvoiced
        self.assertEqual(self.so.invoice_status,'no','SaleStock:soinvoice_statusshouldbe"no"insteadof"%s".'%self.so.invoice_status)

        #delivercompletely
        pick=self.so.picking_ids
        pick.move_lines.write({'quantity_done':5})
        pick.button_validate()

        #Checkquantitydelivered
        del_qty=sum(sol.qty_deliveredforsolinself.so.order_line)
        self.assertEqual(del_qty,5.0,'SaleStock:deliveredquantityshouldbe5.0insteadof%saftercompletedelivery'%del_qty)

        #Checkinvoice
        self.assertEqual(self.so.invoice_status,'toinvoice','SaleStock:soinvoice_statusshouldbe"toinvoice"insteadof"%s"beforeinvoicing'%self.so.invoice_status)
        self.inv_1=self.so._create_invoices()
        self.assertEqual(self.so.invoice_status,'invoiced','SaleStock:soinvoice_statusshouldbe"invoiced"insteadof"%s"afterinvoicing'%self.so.invoice_status)
        self.assertEqual(len(self.inv_1),1,'SaleStock:onlyoneinvoiceinsteadof"%s"shouldbecreated'%len(self.inv_1))
        self.assertEqual(self.inv_1.amount_untaxed,self.inv_1.amount_untaxed,'SaleStock:amountinSOandinvoiceshouldbethesame')
        self.inv_1.action_post()

        #Createreturnpicking
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=pick.ids,active_id=pick.sorted().ids[0],
            active_model='stock.picking'))
        return_wiz=stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity=2.0#Returnonly2
        return_wiz.product_return_moves.to_refund=True#Refundthese2
        res=return_wiz.create_returns()
        return_pick=self.env['stock.picking'].browse(res['res_id'])

        #Validatepicking
        return_pick.move_lines.write({'quantity_done':2})
        return_pick.button_validate()

        #Checkinvoice
        self.assertEqual(self.so.invoice_status,'toinvoice','SaleStock:soinvoice_statusshouldbe"toinvoice"insteadof"%s"afterpickingreturn'%self.so.invoice_status)
        self.assertAlmostEqual(self.so.order_line.sorted()[0].qty_delivered,3.0,msg='SaleStock:deliveredquantityshouldbe3.0insteadof"%s"afterpickingreturn'%self.so.order_line.sorted()[0].qty_delivered)
        #let'sdoaninvoicewithrefunds
        adv_wiz=self.env['sale.advance.payment.inv'].with_context(active_ids=[self.so.id]).create({
            'advance_payment_method':'delivered',
        })
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.inv_2=self.so.invoice_ids.filtered(lambdar:r.state=='draft')
        self.assertAlmostEqual(self.inv_2.invoice_line_ids.sorted()[0].quantity,2.0,msg='SaleStock:refundquantityontheinvoiceshouldbe2.0insteadof"%s".'%self.inv_2.invoice_line_ids.sorted()[0].quantity)
        self.assertEqual(self.so.invoice_status,'no','SaleStock:soinvoice_statusshouldbe"no"insteadof"%s"afterinvoicingthereturn'%self.so.invoice_status)

    deftest_03_sale_stock_delivery_partial(self):
        """
        TestaSOwithaproductinvoicedondelivery.DeliverpartiallyandinvoicetheSO,when
        theSOisseton'done',theSOshouldbefullyinvoiced.
        """
        #intialso
        self.product=self.company_data['product_delivery_no']
        so_vals={
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'order_line':[(0,0,{
                'name':self.product.name,
                'product_id':self.product.id,
                'product_uom_qty':5.0,
                'product_uom':self.product.uom_id.id,
                'price_unit':self.product.list_price})],
            'pricelist_id':self.company_data['default_pricelist'].id,
        }
        self.so=self.env['sale.order'].create(so_vals)

        #confirmourstandardso,checkthepicking
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids,'SaleStock:nopickingcreatedfor"invoiceondelivery"storableproducts')

        #invoiceinondelivery,nothingshouldbeinvoiced
        self.assertEqual(self.so.invoice_status,'no','SaleStock:soinvoice_statusshouldbe"nothingtoinvoice"')

        #deliverpartially
        pick=self.so.picking_ids
        pick.move_lines.write({'quantity_done':4})
        res_dict=pick.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process_cancel_backorder()

        #CheckExceptionerrorisloggedonSO
        activity=self.env['mail.activity'].search([('res_id','=',self.so.id),('res_model','=','sale.order')])
        self.assertEqual(len(activity),1,'Whennobackorderiscreatedforapartialdelivery,awarningerrorshouldbeloggedinitsoriginSO')

        #Checkquantitydelivered
        del_qty=sum(sol.qty_deliveredforsolinself.so.order_line)
        self.assertEqual(del_qty,4.0,'SaleStock:deliveredquantityshouldbe4.0afterpartialdelivery')

        #Checkinvoice
        self.assertEqual(self.so.invoice_status,'toinvoice','SaleStock:soinvoice_statusshouldbe"toinvoice"beforeinvoicing')
        self.inv_1=self.so._create_invoices()
        self.assertEqual(self.so.invoice_status,'no','SaleStock:soinvoice_statusshouldbe"no"afterinvoicing')
        self.assertEqual(len(self.inv_1),1,'SaleStock:onlyoneinvoiceshouldbecreated')
        self.assertEqual(self.inv_1.amount_untaxed,self.inv_1.amount_untaxed,'SaleStock:amountinSOandinvoiceshouldbethesame')

        self.so.action_done()
        self.assertEqual(self.so.invoice_status,'invoiced','SaleStock:soinvoice_statusshouldbe"invoiced"whensettodone')

    deftest_04_create_picking_update_saleorderline(self):
        """
        Testthatupdatingmultiplesaleorderlinesafterasuccessfuldeliverycreatesasinglepickingcontaining
        thenewmovelines.
        """
        #selltwoproducts
        item1=self.company_data['product_order_no'] #consumable
        item1.type='consu'
        item2=self.company_data['product_delivery_no']   #storable
        item2.type='product'   #storable

        self.so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':1,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
                (0,0,{'name':item2.name,'product_id':item2.id,'product_uom_qty':1,'product_uom':item2.uom_id.id,'price_unit':item2.list_price}),
            ],
        })
        self.so.action_confirm()

        #deliverthem
        #Oneofthemoveisforaconsumableproduct,thusisassigned.Thesecondoneisfora
        #storableproduct,thusisunavailable.Hitting`button_validate`willfirstaskto
        #processallthereservedquantitiesand,iftheuserchosetoprocess,asecondwizard
        #willasktocreateabackorderfortheunavailableproduct.
        self.assertEqual(len(self.so.picking_ids),1)
        res_dict=self.so.picking_ids.sorted()[0].button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        self.assertEqual(wizard._name,'stock.immediate.transfer')
        res_dict=wizard.process()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        self.assertEqual(wizard._name,'stock.backorder.confirmation')
        wizard.process()

        #Now,theoriginalpickingisdoneandthereisanewone(thebackorder).
        self.assertEqual(len(self.so.picking_ids),2)
        forpickinginself.so.picking_ids:
            move=picking.move_lines
            ifpicking.backorder_id:
                self.assertEqual(move.product_id.id,item2.id)
                self.assertEqual(move.state,'confirmed')
            else:
                self.assertEqual(picking.move_lines.product_id.id,item1.id)
                self.assertEqual(move.state,'done')

        #updatethetwooriginalsaleorderlines
        self.so.write({
            'order_line':[
                (1,self.so.order_line.sorted()[0].id,{'product_uom_qty':2}),
                (1,self.so.order_line.sorted()[1].id,{'product_uom_qty':2}),
            ]
        })
        #asinglepickingshouldbecreatedforthenewdelivery
        self.assertEqual(len(self.so.picking_ids),2)
        backorder=self.so.picking_ids.filtered(lambdap:p.backorder_id)
        self.assertEqual(len(backorder.move_lines),2)
        forbackorder_moveinbackorder.move_lines:
            ifbackorder_move.product_id.id==item1.id:
                self.assertEqual(backorder_move.product_qty,1)
            elifbackorder_move.product_id.id==item2.id:
                self.assertEqual(backorder_move.product_qty,2)

        #addanewsaleorderlines
        self.so.write({
            'order_line':[
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':1,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
            ]
        })
        self.assertEqual(sum(backorder.move_lines.filtered(lambdam:m.product_id.id==item1.id).mapped('product_qty')),2)

    deftest_05_create_picking_update_saleorderline(self):
        """Sametestthantest_04butonlywithenoughproductsinstocksothatthereservation
        issuccessful.
        """
        #selltwoproducts
        item1=self.company_data['product_order_no'] #consumable
        item1.type='consu' #consumable
        item2=self.company_data['product_delivery_no']   #storable
        item2.type='product'   #storable

        self.env['stock.quant']._update_available_quantity(item2,self.company_data['default_warehouse'].lot_stock_id,2)
        self.so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':1,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
                (0,0,{'name':item2.name,'product_id':item2.id,'product_uom_qty':1,'product_uom':item2.uom_id.id,'price_unit':item2.list_price}),
            ],
        })
        self.so.action_confirm()

        #deliverthem
        self.assertEqual(len(self.so.picking_ids),1)
        res_dict=self.so.picking_ids.sorted()[0].button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.process()
        self.assertEqual(self.so.picking_ids.sorted()[0].state,"done")

        #updatethetwooriginalsaleorderlines
        self.so.write({
            'order_line':[
                (1,self.so.order_line.sorted()[0].id,{'product_uom_qty':2}),
                (1,self.so.order_line.sorted()[1].id,{'product_uom_qty':2}),
            ]
        })
        #asinglepickingshouldbecreatedforthenewdelivery
        self.assertEqual(len(self.so.picking_ids),2)

    deftest_05_confirm_cancel_confirm(self):
        """Confirmasaleorder,cancelit,settoquotation,changethe
        partner,confirmitagain:theseconddeliveryordershouldhave
        thenewpartner.
        """
        item1=self.company_data['product_order_no']
        partner1=self.partner_a.id
        partner2=self.env['res.partner'].create({'name':'AnotherTestPartner'})
        so1=self.env['sale.order'].create({
            'partner_id':partner1,
            'order_line':[(0,0,{
                'name':item1.name,
                'product_id':item1.id,
                'product_uom_qty':1,
                'product_uom':item1.uom_id.id,
                'price_unit':item1.list_price,
            })],
        })
        so1.action_confirm()
        self.assertEqual(len(so1.picking_ids),1)
        self.assertEqual(so1.picking_ids.partner_id.id,partner1)
        so1.action_cancel()
        so1.action_draft()
        so1.partner_id=partner2
        so1.partner_shipping_id=partner2 #setbyanonchange
        so1.action_confirm()
        self.assertEqual(len(so1.picking_ids),2)
        picking2=so1.picking_ids.filtered(lambdap:p.state!='cancel')
        self.assertEqual(picking2.partner_id.id,partner2.id)

    deftest_06_uom(self):
        """Selladozenofproductsstockedinunits.Checkthatthequantitiesonthesaleorder
        linesaswellasthedeliveredquantitiesarehandledindozenwhilethemovesthemselves
        arehandledinunits.Edittheorderedquantities,checkthatthequantitesarecorrectly
        updatedonthemoves.Edittheir.config_parametertopropagatetheuomofthesaleorder
        linestothemovesandeditalasttimetheorderedquantities.Deliver,checkthe
        quantities.
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_dozen=self.env.ref('uom.product_uom_dozen')
        item1=self.company_data['product_order_no']

        self.assertEqual(item1.uom_id.id,uom_unit.id)

        #selladozen
        so1=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[(0,0,{
                'name':item1.name,
                'product_id':item1.id,
                'product_uom_qty':1,
                'product_uom':uom_dozen.id,
                'price_unit':item1.list_price,
            })],
        })
        so1.action_confirm()

        #themoveshouldbe12units
        #note:move.product_qty=computedfield,alwaysintheuomofthequant
        #      move.product_uom_qty=storedfieldrepresentingtheinitialdemandinmove.product_uom
        move1=so1.picking_ids.move_lines[0]
        self.assertEqual(move1.product_uom_qty,12)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,12)

        #editthesoline,sell2dozen,themoveshouldnowbe24units
        so1.write({
            'order_line':[
                (1,so1.order_line.id,{'product_uom_qty':2}),
            ]
        })
        #Theabovewillcreateasecondmove,andthenthetwomoveswillbemergedin_merge_moves`
        #Thepickingmovesarenotwellsortedbecausethenewmovehasjustbeencreated,andthisinfluencestheresultingmove,
        #inwhichmovethetwosaremerged.
        #But,thisdoesn'tseemreallyimportantwhichistheresultingmove,butinthistestwehavetoensure
        #weusetheresultingmovetocomparetheqty.
        #```
        #formovesinmoves_to_merge:
        #    #linkallmovelinestorecord0(theonewewillkeep).
        #    moves.mapped('move_line_ids').write({'move_id':moves[0].id})
        #    #mergemovedata
        #    moves[0].write(moves._merge_moves_fields())
        #    #updatemergedmovesdicts
        #    moves_to_unlink|=moves[1:]
        #```
        move1=so1.picking_ids.move_lines[0]
        self.assertEqual(move1.product_uom_qty,24)
        self.assertEqual(move1.product_uom.id,uom_unit.id)
        self.assertEqual(move1.product_qty,24)

        #forcethepropagationoftheuom,sell3dozen
        self.env['ir.config_parameter'].sudo().set_param('stock.propagate_uom','1')
        so1.write({
            'order_line':[
                (1,so1.order_line.id,{'product_uom_qty':3}),
            ]
        })
        move2=so1.picking_ids.move_lines.filtered(lambdam:m.product_uom.id==uom_dozen.id)
        self.assertEqual(move2.product_uom_qty,1)
        self.assertEqual(move2.product_uom.id,uom_dozen.id)
        self.assertEqual(move2.product_qty,12)

        #delivereverything
        move1.quantity_done=24
        move2.quantity_done=1
        so1.picking_ids.button_validate()

        #checkthedeliveredquantity
        self.assertEqual(so1.order_line.qty_delivered,3.0)

    deftest_07_forced_qties(self):
        """Makemultiplesaleorderlinesofthesameproductwhichisn'tavailableinstock.On
        thepicking,createnewmovelines(throughthedetailedoperationsview).Seethatthemove
        linesarecorrectlydispatchedthroughthemoves.
        """
        uom_unit=self.env.ref('uom.product_uom_unit')
        uom_dozen=self.env.ref('uom.product_uom_dozen')
        item1=self.company_data['product_order_no']

        self.assertEqual(item1.uom_id.id,uom_unit.id)

        #selladozen
        so1=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':item1.name,
                    'product_id':item1.id,
                    'product_uom_qty':1,
                    'product_uom':uom_dozen.id,
                    'price_unit':item1.list_price,
                }),
                (0,0,{
                    'name':item1.name,
                    'product_id':item1.id,
                    'product_uom_qty':1,
                    'product_uom':uom_dozen.id,
                    'price_unit':item1.list_price,
                }),
                (0,0,{
                    'name':item1.name,
                    'product_id':item1.id,
                    'product_uom_qty':1,
                    'product_uom':uom_dozen.id,
                    'price_unit':item1.list_price,
                }),
            ],
        })
        so1.action_confirm()

        self.assertEqual(len(so1.picking_ids.move_lines),3)
        so1.picking_ids.write({
            'move_line_ids':[
                (0,0,{
                    'product_id':item1.id,
                    'product_uom_qty':0,
                    'qty_done':1,
                    'product_uom_id':uom_dozen.id,
                    'location_id':so1.picking_ids.location_id.id,
                    'location_dest_id':so1.picking_ids.location_dest_id.id,
                }),
                (0,0,{
                    'product_id':item1.id,
                    'product_uom_qty':0,
                    'qty_done':1,
                    'product_uom_id':uom_dozen.id,
                    'location_id':so1.picking_ids.location_id.id,
                    'location_dest_id':so1.picking_ids.location_dest_id.id,
                }),
                (0,0,{
                    'product_id':item1.id,
                    'product_uom_qty':0,
                    'qty_done':1,
                    'product_uom_id':uom_dozen.id,
                    'location_id':so1.picking_ids.location_id.id,
                    'location_dest_id':so1.picking_ids.location_dest_id.id,
                }),
            ],
        })
        so1.picking_ids.button_validate()
        self.assertEqual(so1.picking_ids.state,'done')
        self.assertEqual(so1.order_line.mapped('qty_delivered'),[1,1,1])

    deftest_08_quantities(self):
        """Changethepickingcodeofthereceiptstointernal.MakeaSOfor10units,gotothe
        pickingandreturn5,edittheSOlineto15units.

        Thepurposeofthetestistochecktheconsistenciesacrossthedeliveredquantitiesandthe
        procurementquantities.
        """
        #Changethecodeofthepickingtypereceipt
        self.env['stock.picking.type'].search([('code','=','incoming')]).write({'code':'internal'})

        #Sellanddeliver10units
        item1=self.company_data['product_order_no']
        uom_unit=self.env.ref('uom.product_uom_unit')
        so1=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':item1.name,
                    'product_id':item1.id,
                    'product_uom_qty':10,
                    'product_uom':uom_unit.id,
                    'price_unit':item1.list_price,
                }),
            ],
        })
        so1.action_confirm()

        picking=so1.picking_ids
        wiz_act=picking.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        #Return5units
        stock_return_picking_form=Form(self.env['stock.return.picking'].with_context(
            active_ids=picking.ids,
            active_id=picking.sorted().ids[0],
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

        self.assertEqual(so1.order_line.qty_delivered,5)

        #Deliver15insteadof10.
        so1.write({
            'order_line':[
                (1,so1.order_line.sorted()[0].id,{'product_uom_qty':15}),
            ]
        })

        #Anewmoveof10unit(15-5units)
        self.assertEqual(so1.order_line.qty_delivered,5)
        self.assertEqual(so1.picking_ids.sorted('id')[-1].move_lines.product_qty,10)

    deftest_09_qty_available(self):
        """createasaleorderinwarehouse1,changetowarehouse2andcheckthe
        availablequantitiesonsaleorderlinesarewellupdated"""
        #selltwoproducts
        item1=self.company_data['product_order_no']
        item1.type='product'

        warehouse1=self.company_data['default_warehouse']
        self.env['stock.quant']._update_available_quantity(item1,warehouse1.lot_stock_id,10)
        self.env['stock.quant']._update_reserved_quantity(item1,warehouse1.lot_stock_id,3)

        warehouse2=self.env['stock.warehouse'].create({
            'partner_id':self.partner_a.id,
            'name':'Zizizatestwarehouse',
            'code':'Test',
        })
        self.env['stock.quant']._update_available_quantity(item1,warehouse2.lot_stock_id,5)
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':1,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
            ],
        })
        line=so.order_line[0]
        self.assertAlmostEqual(line.scheduled_date,datetime.now(),delta=timedelta(seconds=10))
        self.assertEqual(line.virtual_available_at_date,10)
        self.assertEqual(line.free_qty_today,7)
        self.assertEqual(line.qty_available_today,10)
        self.assertEqual(line.warehouse_id,warehouse1)
        self.assertEqual(line.qty_to_deliver,1)
        so.warehouse_id=warehouse2
        #invalidateproductcachetoensureqty_availableisrecomputed
        #bcwarehouseisn'tinthedepends_contextofqty_available
        line.product_id.invalidate_cache()
        self.assertEqual(line.virtual_available_at_date,5)
        self.assertEqual(line.free_qty_today,5)
        self.assertEqual(line.qty_available_today,5)
        self.assertEqual(line.warehouse_id,warehouse2)
        self.assertEqual(line.qty_to_deliver,1)

    deftest_10_qty_available(self):
        """createasaleordercontainingthreetimesthesameproduct.The
        quantityavailableshouldbedifferentforthe3lines"""
        item1=self.company_data['product_order_no']
        item1.type='product'
        self.env['stock.quant']._update_available_quantity(item1,self.company_data['default_warehouse'].lot_stock_id,10)
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':5,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':5,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
                (0,0,{'name':item1.name,'product_id':item1.id,'product_uom_qty':5,'product_uom':item1.uom_id.id,'price_unit':item1.list_price}),
            ],
        })
        self.assertEqual(so.order_line.mapped('free_qty_today'),[10,5,0])

    deftest_11_return_with_refund(self):
        """Createsasaleorder,validsitanditsdelivery,thencreatesa
        return.Thereturnmustrefundbydefaultandthesaleorderdelivered
        quantitymustbeupdated.
        """
        #Createsasaleorderfor10products.
        sale_order=self._get_new_sale_order()
        #Validsthesaleorder,thenvalidsthedelivery.
        sale_order.action_confirm()
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(sale_order.order_line.qty_delivered,0)
        picking=sale_order.picking_ids
        picking.move_lines.write({'quantity_done':10})
        picking.button_validate()

        #Checksthedeliveryamount(mustbe10).
        self.assertEqual(sale_order.order_line.qty_delivered,10)
        #Createsareturnfromthedeliverypicking.
        return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids,active_id=picking.id,
            active_model='stock.picking'))
        return_wizard=return_picking_form.save()
        #Checksthefield`to_refund`ischecked(mustbecheckedbydefault).
        self.assertEqual(return_wizard.product_return_moves.to_refund,True)
        self.assertEqual(return_wizard.product_return_moves.quantity,10)

        #Validsthereturnpicking.
        res=return_wizard.create_returns()
        return_picking=self.env['stock.picking'].browse(res['res_id'])
        return_picking.move_lines.write({'quantity_done':10})
        return_picking.button_validate()
        #Checksthedeliveryamount(mustbe0).
        self.assertEqual(sale_order.order_line.qty_delivered,0)

    deftest_12_return_without_refund(self):
        """Dotheexactthingthanin`test_11_return_with_refund`exceptwe
        setonFalsetherefundandchecksthesaleorderdeliveredquantity
        isn'tchanged.
        """
        #Createsasaleorderfor10products.
        sale_order=self._get_new_sale_order()
        #Validsthesaleorder,thenvalidsthedelivery.
        sale_order.action_confirm()
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(sale_order.order_line.qty_delivered,0)
        picking=sale_order.picking_ids
        picking.move_lines.write({'quantity_done':10})
        picking.button_validate()

        #Checksthedeliveryamount(mustbe10).
        self.assertEqual(sale_order.order_line.qty_delivered,10)
        #Createsareturnfromthedeliverypicking.
        return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids,active_id=picking.id,
            active_model='stock.picking'))
        return_wizard=return_picking_form.save()
        #Checksthefield`to_refund`ischecked,thenunchecksit.
        self.assertEqual(return_wizard.product_return_moves.to_refund,True)
        self.assertEqual(return_wizard.product_return_moves.quantity,10)
        return_wizard.product_return_moves.to_refund=False
        #Validsthereturnpicking.
        res=return_wizard.create_returns()
        return_picking=self.env['stock.picking'].browse(res['res_id'])
        return_picking.move_lines.write({'quantity_done':10})
        return_picking.button_validate()
        #Checksthedeliveryamount(muststillbe10).
        self.assertEqual(sale_order.order_line.qty_delivered,10)

    deftest_13_delivered_qty(self):
        """Createsasaleorder,validsitandaddsanewmovelineinthedeliveryfora
        productwithaninvoicingpolicyon'order',thenchecksanewSOlinewascreated.
        Afterthat,createsasecondsaleorderanddoesthesamethingbutwithaproduct
        withandinvoicingpolicyon'ordered'.
        """
        product_inv_on_delivered=self.company_data['product_delivery_no']
        #Configureaproductwithinvoicingpolicyonorder.
        product_inv_on_order=self.env['product.product'].create({
            'name':'Shenaniffluffy',
            'type':'consu',
            'invoice_policy':'order',
            'list_price':55.0,
        })
        #Createsasaleorderfor3productsinvoicedonqty.delivered.
        sale_order=self._get_new_sale_order(amount=3)
        #Confirmsthesaleorder,thenincreasesthedeliveredqty.,addsanew
        #lineandvalidsthedelivery.
        sale_order.action_confirm()
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(len(sale_order.order_line),1)
        self.assertEqual(sale_order.order_line.qty_delivered,0)
        picking=sale_order.picking_ids

        picking_form=Form(picking)
        withpicking_form.move_line_ids_without_package.edit(0)asmove:
            move.qty_done=5
        withpicking_form.move_line_ids_without_package.new()asnew_move:
            new_move.product_id=product_inv_on_order
            new_move.qty_done=5
        picking=picking_form.save()
        picking.button_validate()

        #Checkanewsaleorderlinewascorrectlycreated.
        self.assertEqual(len(sale_order.order_line),2)
        so_line_1=sale_order.order_line[0]
        so_line_2=sale_order.order_line[1]
        self.assertEqual(so_line_1.product_id.id,product_inv_on_delivered.id)
        self.assertEqual(so_line_1.product_uom_qty,3)
        self.assertEqual(so_line_1.qty_delivered,5)
        self.assertEqual(so_line_1.price_unit,70.0)
        self.assertEqual(so_line_2.product_id.id,product_inv_on_order.id)
        self.assertEqual(so_line_2.product_uom_qty,0)
        self.assertEqual(so_line_2.qty_delivered,5)
        self.assertEqual(
            so_line_2.price_unit,0,
            "Shouldn'tgettheproductpriceastheinvoicepolicyisonqty.ordered")

        #Createsasecondsaleorderfor3productinvoicedonqty.ordered.
        sale_order=self._get_new_sale_order(product=product_inv_on_order,amount=3)
        #Confirmsthesaleorder,thenincreasesthedeliveredqty.,addsanew
        #lineandvalidsthedelivery.
        sale_order.action_confirm()
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(len(sale_order.order_line),1)
        self.assertEqual(sale_order.order_line.qty_delivered,0)
        picking=sale_order.picking_ids

        picking_form=Form(picking)
        withpicking_form.move_line_ids_without_package.edit(0)asmove:
            move.qty_done=5
        withpicking_form.move_line_ids_without_package.new()asnew_move:
            new_move.product_id=product_inv_on_delivered
            new_move.qty_done=5
        picking=picking_form.save()
        picking.button_validate()

        #Checkanewsaleorderlinewascorrectlycreated.
        self.assertEqual(len(sale_order.order_line),2)
        so_line_1=sale_order.order_line[0]
        so_line_2=sale_order.order_line[1]
        self.assertEqual(so_line_1.product_id.id,product_inv_on_order.id)
        self.assertEqual(so_line_1.product_uom_qty,3)
        self.assertEqual(so_line_1.qty_delivered,5)
        self.assertEqual(so_line_1.price_unit,55.0)
        self.assertEqual(so_line_2.product_id.id,product_inv_on_delivered.id)
        self.assertEqual(so_line_2.product_uom_qty,0)
        self.assertEqual(so_line_2.qty_delivered,5)
        self.assertEqual(
            so_line_2.price_unit,70.0,
            "Shouldgettheproductpriceastheinvoicepolicyisonqty.delivered")

    deftest_14_delivered_qty_in_multistep(self):
        """Createsasaleorderwithdeliveryintwo-step.Processthepick&
        shipandcheckwedon'thaveextraSOline.Then,dothesamebutwith
        addingaextramoveandcheckonlyoneextraSOlinewascreated.
        """
        #Setthedeliveryintwosteps.
        warehouse=self.company_data['default_warehouse']
        warehouse.delivery_steps='pick_ship'
        #Configureaproductwithinvoicingpolicyonorder.
        product_inv_on_order=self.env['product.product'].create({
            'name':'Shenaniffluffy',
            'type':'consu',
            'invoice_policy':'order',
            'list_price':55.0,
        })
        #Createasaleorder.
        sale_order=self._get_new_sale_order()
        #Confirmsthesaleorder,thenvalidspickanddelivery.
        sale_order.action_confirm()
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(len(sale_order.order_line),1)
        self.assertEqual(sale_order.order_line.qty_delivered,0)
        pick=sale_order.picking_ids.filtered(lambdap:p.picking_type_code=='internal')
        delivery=sale_order.picking_ids.filtered(lambdap:p.picking_type_code=='outgoing')

        picking_form=Form(pick)
        withpicking_form.move_line_ids_without_package.edit(0)asmove:
            move.qty_done=10
        pick=picking_form.save()
        pick.button_validate()

        picking_form=Form(delivery)
        withpicking_form.move_line_ids_without_package.edit(0)asmove:
            move.qty_done=10
        delivery=picking_form.save()
        delivery.button_validate()

        #Checknonewsaleorderlinewascreated.
        self.assertEqual(len(sale_order.order_line),1)
        self.assertEqual(sale_order.order_line.product_uom_qty,10)
        self.assertEqual(sale_order.order_line.qty_delivered,10)
        self.assertEqual(sale_order.order_line.price_unit,70.0)

        #Createsasecondsaleorder.
        sale_order=self._get_new_sale_order()
        #Confirmsthesaleorderthenaddanewlineforananotherproductinthepick/out.
        sale_order.action_confirm()
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(len(sale_order.order_line),1)
        self.assertEqual(sale_order.order_line.qty_delivered,0)
        pick=sale_order.picking_ids.filtered(lambdap:p.picking_type_code=='internal')
        delivery=sale_order.picking_ids.filtered(lambdap:p.picking_type_code=='outgoing')

        picking_form=Form(pick)
        withpicking_form.move_line_ids_without_package.edit(0)asmove:
            move.qty_done=10
        withpicking_form.move_line_ids_without_package.new()asnew_move:
            new_move.product_id=product_inv_on_order
            new_move.qty_done=10
        pick=picking_form.save()
        pick.button_validate()

        picking_form=Form(delivery)
        withpicking_form.move_line_ids_without_package.edit(0)asmove:
            move.qty_done=10
        withpicking_form.move_line_ids_without_package.new()asnew_move:
            new_move.product_id=product_inv_on_order
            new_move.qty_done=10
        delivery=picking_form.save()
        delivery.button_validate()

        #Checkanewsaleorderlinewascorrectlycreated.
        self.assertEqual(len(sale_order.order_line),2)
        so_line_1=sale_order.order_line[0]
        so_line_2=sale_order.order_line[1]
        self.assertEqual(so_line_1.product_id.id,self.company_data['product_delivery_no'].id)
        self.assertEqual(so_line_1.product_uom_qty,10)
        self.assertEqual(so_line_1.qty_delivered,10)
        self.assertEqual(so_line_1.price_unit,70.0)
        self.assertEqual(so_line_2.product_id.id,product_inv_on_order.id)
        self.assertEqual(so_line_2.product_uom_qty,0)
        self.assertEqual(so_line_2.qty_delivered,10)
        self.assertEqual(so_line_2.price_unit,0)

    deftest_08_sale_return_qty_and_cancel(self):
        """
        TestaSOwithaproductondeliverywitha5quantity.
        Createtwoinvoices:onefor3quantityandonefor2quantity
        ThencancelSaleorder,itwon'traiseanywarning,itshouldbecancelled.
        """
        partner=self.partner_a
        product=self.company_data['product_delivery_no']
        so_vals={
            'partner_id':partner.id,
            'partner_invoice_id':partner.id,
            'partner_shipping_id':partner.id,
            'order_line':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':5.0,
                'product_uom':product.uom_id.id,
                'price_unit':product.list_price})],
            'pricelist_id':self.company_data['default_pricelist'].id,
        }
        so=self.env['sale.order'].create(so_vals)

        #confirmtheso
        so.action_confirm()

        #deliverpartially
        pick=so.picking_ids
        pick.move_lines.write({'quantity_done':3})

        wiz_act=pick.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        #createinvoicefor3quantityandpostit
        inv_1=so._create_invoices()
        inv_1.action_post()
        self.assertEqual(inv_1.state,'posted','invoiceshouldbeinpostedstate')

        pick_2=so.picking_ids.filtered('backorder_id')
        pick_2.move_lines.write({'quantity_done':2})
        pick_2.button_validate()

        #createinvoiceforremaining2quantity
        inv_2=so._create_invoices()
        self.assertEqual(inv_2.state,'draft','invoiceshouldbeindraftstate')

        #checkthestatusofinvoicesaftercancellingtheorder
        so.action_cancel()
        wizard=self.env['sale.order.cancel'].with_context({'order_id':so.id}).create({'order_id':so.id})
        wizard.action_cancel()
        self.assertEqual(inv_1.state,'posted','Apostedinvoicestateshouldremainposted')
        self.assertEqual(inv_2.state,'cancel','Adraftedinvoicestateshouldbecancelled')

    deftest_15_cancel_delivery(self):
        """Supposetheoption"LockConfirmedSales"enabledandaproductwiththeinvoicing
        policysetto"Deliveredquantities".Whencancellingthedeliveryofsuchaproduct,the
        invoicestatusoftheassociatedSOshouldbe'NothingtoInvoice'
        """
        group_auto_done=self.env['ir.model.data'].xmlid_to_object('sale.group_auto_done_setting')
        self.env.user.groups_id=[(4,group_auto_done.id)]

        product=self.product_a
        partner=self.partner_a
        so=self.env['sale.order'].create({
            'partner_id':partner.id,
            'partner_invoice_id':partner.id,
            'partner_shipping_id':partner.id,
            'order_line':[(0,0,{
                'name':product.name,
                'product_id':product.id,
                'product_uom_qty':2,
                'product_uom':product.uom_id.id,
                'price_unit':product.list_price
            })],
            'pricelist_id':self.env.ref('product.list0').id,
        })
        so.action_confirm()
        self.assertEqual(so.state,'done')
        so.picking_ids.action_cancel()

        self.assertEqual(so.invoice_status,'no')

    deftest_16_multi_uom(self):
        yards_uom=self.env['uom.uom'].create({
            'category_id':self.env.ref('uom.uom_categ_length').id,
            'name':'Yards',
            'factor_inv':0.9144,
            'uom_type':'bigger',
        })
        product=self.env.ref('product.product_product_11').copy({
            'uom_id':self.env.ref('uom.product_uom_meter').id,
            'uom_po_id':yards_uom.id,
        })
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':product.name,
                    'product_id':product.id,
                    'product_uom_qty':4.0,
                    'product_uom':yards_uom.id,
                    'price_unit':1.0,
                })
            ],
        })
        so.action_confirm()
        picking=so.picking_ids[0]
        picking.move_lines.write({'quantity_done':3.66})
        picking.button_validate()
        self.assertEqual(so.order_line.mapped('qty_delivered'),[4.0],'Sale:noconversionerrorondeliveryindifferentuom"')

    deftest_17_deliver_more_and_multi_uom(self):
        """
        DeliveranadditionalproductwithaUoMdifferentthanitsdefaultone
        ThisUoMshouldbethesameonthegeneratedSOline
        """
        uom_m_id=self.ref("uom.product_uom_meter")
        uom_km_id=self.ref("uom.product_uom_km")
        self.product_b.write({
            'uom_id':uom_m_id,
            'uom_po_id':uom_m_id,
        })

        so=self._get_new_sale_order(product=self.product_a)
        so.action_confirm()

        picking=so.picking_ids
        self.env['stock.move'].create({
            'picking_id':picking.id,
            'location_id':picking.location_id.id,
            'location_dest_id':picking.location_dest_id.id,
            'name':self.product_b.name,
            'product_id':self.product_b.id,
            'product_uom_qty':1,
            'product_uom':uom_km_id,
        })
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()

        self.assertEqual(so.order_line[1].product_id,self.product_b)
        self.assertEqual(so.order_line[1].qty_delivered,1)
        self.assertEqual(so.order_line[1].product_uom.id,uom_km_id)

    deftest_multiple_returns(self):
        #Createsasaleorderfor10products.
        sale_order=self._get_new_sale_order()
        #Validsthesaleorder,thenvalidsthedelivery.
        sale_order.action_confirm()
        picking=sale_order.picking_ids
        picking.move_lines.write({'quantity_done':10})
        picking.button_validate()

        #Createsareturnfromthedeliverypicking.
        return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids,active_id=picking.id,
            active_model='stock.picking'))
        return_wizard=return_picking_form.save()
        #Checkthatthecorrectquantityissetontheretrun
        self.assertEqual(return_wizard.product_return_moves.quantity,10)
        return_wizard.product_return_moves.quantity=2
        #Validsthereturnpicking.
        res=return_wizard.create_returns()
        return_picking=self.env['stock.picking'].browse(res['res_id'])
        return_picking.move_lines.write({'quantity_done':2})
        return_picking.button_validate()

        #Createsasecondreturnfromthedeliverypicking.
        return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids,active_id=picking.id,
            active_model='stock.picking'))
        return_wizard=return_picking_form.save()
        #Checkthattheremainingquantityissetontheretrun
        self.assertEqual(return_wizard.product_return_moves.quantity,8)

    deftest_exception_delivery_partial_multi(self):
        '''
        Whenabackorderiscancelledforapickinginmulti-picking,
        therelatedSOshouldhaveanexceptionlogged
        '''
        #Create2saleorders
        so_1=self._get_new_sale_order()
        so_1.action_confirm()
        picking_1=so_1.picking_ids
        picking_1.move_lines.write({'quantity_done':1})

        so_2=self._get_new_sale_order()
        so_2.action_confirm()
        picking_2=so_2.picking_ids
        picking_2.move_lines.write({'quantity_done':2})

        #multi-pickingvalidation
        pick=picking_1|picking_2
        res_dict=pick.button_validate()
        wizard=Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.backorder_confirmation_line_ids[1].write({'to_backorder':False})
        wizard.process()

        #CheckExceptionerrorisloggedonso_2
        activity=self.env['mail.activity'].search([('res_id','=',so_2.id),('res_model','=','sale.order')])
        self.assertEqual(len(activity),1,'Whennobackorderiscreatedforapartialdelivery,awarningerrorshouldbeloggedinitsoriginSO')

    deftest_3_steps_and_unpack(self):
        """
        Whenremovingthepackageofastock.move.linemid-flowina3-stepsdeliverywithbackorders,makesurethat
        theOUTpickingdoesnotgetpackagesagainonitsstock.move.line.
        Steps:
        -createaSOofproductAfor10units
        -onPICK_1picking:put2unitsinDoneandputinapackage,validate,createabackorder
        -onPACK_1picking:removethedestinationpackageforthe2units,validate,createabackorder
        -onOUTpicking:thestock.move.lineshouldnothaveapackage
        -onPICK_2picking:put2unitsinDoneandputinapackage,validate,createabackorder
        -onOUTpicking:thestock.move.lineshouldstillnothaveapackage
        -onPACK_2:validate,createabackorder
        -onOUTpicking:thereshouldbe2stock.move.lines,onewithpackageandonewithout
        """
        warehouse=self.company_data.get('default_warehouse')
        self.env['res.config.settings'].write({
            'group_stock_tracking_lot':True,
            'group_stock_adv_location':True,
            'group_stock_multi_locations':True,
        })
        warehouse.delivery_steps='pick_pack_ship'
        self.env['stock.quant']._update_available_quantity(self.test_product_delivery,warehouse.lot_stock_id,10)

        so_1=self._get_new_sale_order(product=self.test_product_delivery)
        so_1.action_confirm()
        pick_picking=so_1.picking_ids.filtered(lambdap:p.picking_type_id==warehouse.pick_type_id)
        pack_picking=so_1.picking_ids.filtered(lambdap:p.picking_type_id==warehouse.pack_type_id)
        out_picking=so_1.picking_ids.filtered(lambdap:p.picking_type_id==warehouse.out_type_id)

        pick_picking.move_lines.quantity_done=2
        pick_picking.action_put_in_pack()
        backorder_wizard_dict=pick_picking.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        pack_picking.move_line_ids.result_package_id=False
        pack_picking.move_lines.quantity_done=2
        backorder_wizard_dict=pack_picking.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertEqual(out_picking.move_line_ids.package_id.id,False)
        self.assertEqual(out_picking.move_line_ids.result_package_id.id,False)

        pick_picking_2=so_1.picking_ids.filtered(lambdax:x.picking_type_id==warehouse.pick_type_idandx.state!='done')

        pick_picking_2.move_lines.quantity_done=2
        package_2=pick_picking_2.action_put_in_pack()
        backorder_wizard_dict=pick_picking_2.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertEqual(out_picking.move_line_ids.package_id.id,False)
        self.assertEqual(out_picking.move_line_ids.result_package_id.id,False)

        pack_picking_2=so_1.picking_ids.filtered(lambdap:p.picking_type_id==warehouse.pack_type_idandp.state!='done')

        pack_picking_2.move_lines.quantity_done=2
        backorder_wizard_dict=pack_picking_2.button_validate()
        backorder_wizard=Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertRecordValues(out_picking.move_line_ids,[{'result_package_id':False},{'result_package_id':package_2.id}])

classTestSaleStockOnly(SavepointCase):

    deftest_no_automatic_assign(self):
        """
        ThistestensuresthatwhenapickingisgeneratedfromaSO,thequantitiesarenot
        automaticallyreserved(theautomaticreservationshouldonlyhappenwhen`procurement_jit`
        isinstalled)
        """
        product=self.env['product.product'].create({'name':'SuperProduct','type':'product'})
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        self.env['stock.quant']._update_available_quantity(product,warehouse.lot_stock_id,3)

        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'ResPartnerTest'})
        withso_form.order_line.new()asline:
            line.product_id=product
            line.product_uom_qty=3
        so=so_form.save()
        so.action_confirm()

        picking=so.picking_ids
        self.assertEqual(picking.state,'confirmed')
        self.assertEqual(picking.move_lines.reserved_availability,0.0)

        picking.move_lines.quantity_done=1
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()

        backorder=picking.backorder_ids
        self.assertEqual(backorder.state,'confirmed')
        self.assertEqual(backorder.move_lines.reserved_availability,0.0)
