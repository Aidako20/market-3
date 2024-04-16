#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

from.commonimportTestSaleCommon
fromflectra.testsimportForm,tagged


@tagged('post_install','-at_install')
classTestSaleToInvoice(TestSaleCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #CreatetheSOwithfourorderlines
        cls.sale_order=cls.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id':cls.partner_a.id,
            'partner_invoice_id':cls.partner_a.id,
            'partner_shipping_id':cls.partner_a.id,
            'pricelist_id':cls.company_data['default_pricelist'].id,
        })
        SaleOrderLine=cls.env['sale.order.line'].with_context(tracking_disable=True)
        cls.sol_prod_order=SaleOrderLine.create({
            'name':cls.company_data['product_order_no'].name,
            'product_id':cls.company_data['product_order_no'].id,
            'product_uom_qty':5,
            'product_uom':cls.company_data['product_order_no'].uom_id.id,
            'price_unit':cls.company_data['product_order_no'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_serv_deliver=SaleOrderLine.create({
            'name':cls.company_data['product_service_delivery'].name,
            'product_id':cls.company_data['product_service_delivery'].id,
            'product_uom_qty':4,
            'product_uom':cls.company_data['product_service_delivery'].uom_id.id,
            'price_unit':cls.company_data['product_service_delivery'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_serv_order=SaleOrderLine.create({
            'name':cls.company_data['product_service_order'].name,
            'product_id':cls.company_data['product_service_order'].id,
            'product_uom_qty':3,
            'product_uom':cls.company_data['product_service_order'].uom_id.id,
            'price_unit':cls.company_data['product_service_order'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })
        cls.sol_prod_deliver=SaleOrderLine.create({
            'name':cls.company_data['product_delivery_no'].name,
            'product_id':cls.company_data['product_delivery_no'].id,
            'product_uom_qty':2,
            'product_uom':cls.company_data['product_delivery_no'].uom_id.id,
            'price_unit':cls.company_data['product_delivery_no'].list_price,
            'order_id':cls.sale_order.id,
            'tax_id':False,
        })

        #ConfirmtheSO
        cls.sale_order.action_confirm()

        #Createaninvoicewithinvoiceablelinesonly
        payment=cls.env['sale.advance.payment.inv'].with_context({
            'active_model':'sale.order',
            'active_ids':[cls.sale_order.id],
            'active_id':cls.sale_order.id,
            'default_journal_id':cls.company_data['default_journal_sale'].id,
        }).create({
            'advance_payment_method':'delivered'
        })
        payment.create_invoices()

        cls.invoice=cls.sale_order.invoice_ids[0]

    deftest_refund_create(self):
        #Validateinvoice
        self.invoice.action_post()

        #CheckquantitytoinvoiceonSOlines
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredqtyarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,0.0,"Theorderedsalelinearetotallyinvoiced(qtytoinvoiceiszero)")
                    self.assertEqual(line.qty_invoiced,5.0,"Theordered(prod)salelinearetotallyinvoiced(qtyinvoicedcomefromtheinvoicelines)")
                else:
                    self.assertEqual(line.qty_to_invoice,0.0,"Theorderedsalelinearetotallyinvoiced(qtytoinvoiceiszero)")
                    self.assertEqual(line.qty_invoiced,3.0,"Theordered(serv)salelinearetotallyinvoiced(qtyinvoiced=theinvoicelines)")
                self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*line.qty_to_invoice,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*line.qty_invoiced,"Amountinvoicedisnowsetasqtyinvoiced*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(len(line.invoice_lines),1,"Thelines'ordered'qtyareinvoiced,soitshouldbelinkedto1invoicelines")

        #Makeacreditnote
        credit_note_wizard=self.env['account.move.reversal'].with_context({'active_ids':[self.invoice.id],'active_id':self.invoice.id,'active_model':'account.move'}).create({
            'refund_method':'refund', #thisistheonlymodeforwhichtheSOlineislinkedtotherefund(https://github.com/flectra/flectra/commit/e680f29560ac20133c7af0c6364c6ef494662eac)
            'reason':'reasontestcreate',
        })
        credit_note_wizard.reverse_moves()
        invoice_refund=self.sale_order.invoice_ids.sorted(key=lambdainv:inv.id,reverse=False)[-1] #thefirstinvoice,itsrefund,andthenewinvoice

        #Checkinvoice'stypeandnumber
        self.assertEqual(invoice_refund.move_type,'out_refund','Thelastcreatedinvoicedshouldbearefund')
        self.assertEqual(invoice_refund.state,'draft','LastCustomerinvoicesshouldbeindraft')
        self.assertEqual(self.sale_order.invoice_count,2,"TheSOshouldhave2relatedinvoices:theoriginal,thenewrefund")
        self.assertEqual(len(self.sale_order.invoice_ids.filtered(lambdainv:inv.move_type=='out_refund')),1,"TheSOshouldbelinkedtoonlyonerefund")
        self.assertEqual(len(self.sale_order.invoice_ids.filtered(lambdainv:inv.move_type=='out_invoice')),1,"TheSOshouldbelinkedtoonlyonecustomerinvoices")

        #Atthistime,theinvoice1isopend(validated)anditsrefundisindraft,sotheamountsinvoicedarenotzerofor
        #invoicedsaleline.Theamountsonlytakevalidatedinvoice/refundintoaccount.
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSOlinebasedondeliveredqty")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,5.0,"Astherefundiscreated,theinvoicedquantitycanceleachother(consuordered)")
                    self.assertEqual(line.qty_invoiced,0.0,"TheqtytoinvoiceshouldhavedecreasedastherefundiscreatedfororderedconsuSOline")
                    self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Amounttoinvoiceiszeroastherefundisnotvalidated")
                    self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*5,"Amountinvoicedisnowsetasunitprice*orderedqty-refundqty)evenifthe")
                    self.assertEqual(len(line.invoice_lines),2,"Theline'orderedconsumable'isinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund)")
                else:
                    self.assertEqual(line.qty_to_invoice,3.0,"Astherefundiscreated,theinvoicedquantitycanceleachother(consuordered)")
                    self.assertEqual(line.qty_invoiced,0.0,"TheqtytoinvoiceshouldhavedecreasedastherefundiscreatedfororderedserviceSOline")
                    self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Amounttoinvoiceiszeroastherefundisnotvalidated")
                    self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*3,"Amountinvoicedisnowsetasunitprice*orderedqty-refundqty)evenifthe")
                    self.assertEqual(len(line.invoice_lines),2,"Theline'orderedservice'isinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund)")

        #Validatetherefund
        invoice_refund.action_post()

        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,5.0,"Astherefundstillexists,thequantitytoinvoiceistheorderedquantity")
                    self.assertEqual(line.qty_invoiced,0.0,"Theqtytoinvoiceshouldbezeroas,withtherefund,thequantitiescanceleachother")
                    self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*5,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,asrefundisvalidated")
                    self.assertEqual(line.untaxed_amount_invoiced,0.0,"Amountinvoiceddecreasedastherefundisnowconfirmed")
                    self.assertEqual(len(line.invoice_lines),2,"Theline'orderedconsumable'isinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund)")
                else:
                    self.assertEqual(line.qty_to_invoice,3.0,"Astherefundstillexists,thequantitytoinvoiceistheorderedquantity")
                    self.assertEqual(line.qty_invoiced,0.0,"Theqtytoinvoiceshouldbezeroas,withtherefund,thequantitiescanceleachother")
                    self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*3,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,asrefundisvalidated")
                    self.assertEqual(line.untaxed_amount_invoiced,0.0,"Amountinvoiceddecreasedastherefundisnowconfirmed")
                    self.assertEqual(len(line.invoice_lines),2,"Theline'orderedservice'isinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund)")

    deftest_refund_cancel(self):
        """Testinvoicewitharefundin'cancel'mode,meaningarefundwillbecreatedandautoconfirmtocompletelycancelthefirst
            customerinvoice.TheSOwillhave2invoice(customer+refund)inapaidstateattheend."""
        #Increasequantityofaninvoicelines
        withForm(self.invoice)asinvoice_form:
            withinvoice_form.invoice_line_ids.edit(0)asline_form:
                line_form.quantity=6
            withinvoice_form.invoice_line_ids.edit(1)asline_form:
                line_form.quantity=4

        #Validateinvoice
        self.invoice.action_post()

        #CheckquantitytoinvoiceonSOlines
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredqtyarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*line.qty_to_invoice,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*line.qty_invoiced,"Amountinvoicedisnowsetasqtyinvoiced*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(len(line.invoice_lines),1,"Thelines'ordered'qtyareinvoiced,soitshouldbelinkedto1invoicelines")

                self.assertEqual(line.qty_invoiced,line.product_uom_qty+1,"Thequantityinvoicedis+1unitfromtheoneofthesaleline,aswemodifiedinvoicelines(%s)"%(line.name,))
                self.assertEqual(line.qty_to_invoice,-1,"Thequantitytoinvoiceisnegativeasweinvoicemorethanordered")

        #Makeacreditnote
        credit_note_wizard=self.env['account.move.reversal'].with_context({'active_ids':self.invoice.ids,'active_id':self.invoice.id,'active_model':'account.move'}).create({
            'refund_method':'cancel',
            'reason':'reasontestcancel',
        })
        invoice_refund=self.env['account.move'].browse(credit_note_wizard.reverse_moves()['res_id'])

        #Checkinvoice'stypeandnumber
        self.assertEqual(invoice_refund.move_type,'out_refund','Thelastcreatedinvoicedshouldbeacustomerinvoice')
        self.assertEqual(invoice_refund.payment_state,'paid','LastCustomercreaditnoteshouldbeinpaidstate')
        self.assertEqual(self.sale_order.invoice_count,2,"TheSOshouldhave3relatedinvoices:theoriginal,therefund,andthenewone")
        self.assertEqual(len(self.sale_order.invoice_ids.filtered(lambdainv:inv.move_type=='out_refund')),1,"TheSOshouldbelinkedtoonlyonerefund")
        self.assertEqual(len(self.sale_order.invoice_ids.filtered(lambdainv:inv.move_type=='out_invoice')),1,"TheSOshouldbelinkedtoonlyonecustomerinvoices")

        #Atthistime,theinvoice1isopened(validated)anditsrefundvalidatedtoo,sotheamountsinvoicedarezerofor
        #allsaleline.AllinvoiceableSalelineshave
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSOlinebasedondeliveredqty")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                self.assertEqual(line.qty_to_invoice,line.product_uom_qty,"Thequantitytoinvoiceshouldbetheorderedquantity")
                self.assertEqual(line.qty_invoiced,0,"Thequantityinvoicediszeroastherefund(paid)completelycancelthefirstinvoice")

                self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*line.qty_to_invoice,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*line.qty_invoiced,"Amountinvoicedisnowsetasqtyinvoiced*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(len(line.invoice_lines),2,"Thelines'ordered'qtyareinvoiced,soitshouldbelinkedto1invoicelines")

    deftest_refund_modify(self):
        """Testinvoicewitharefundin'modify'mode,andcheckcustomerinvoicescreditnoteiscreatedfromrespectiveinvoice"""
        #Decreasequantityofaninvoicelines
        withForm(self.invoice)asinvoice_form:
            withinvoice_form.invoice_line_ids.edit(0)asline_form:
                line_form.quantity=3
            withinvoice_form.invoice_line_ids.edit(1)asline_form:
                line_form.quantity=2

        #Validateinvoice
        self.invoice.action_post()

        #CheckquantitytoinvoiceonSOlines
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredqtyarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,2.0,"Theorderedsalelinearetotallyinvoiced(qtytoinvoiceiszero)")
                    self.assertEqual(line.qty_invoiced,3.0,"Theordered(prod)salelinearetotallyinvoiced(qtyinvoicedcomefromtheinvoicelines)")
                else:
                    self.assertEqual(line.qty_to_invoice,1.0,"Theorderedsalelinearetotallyinvoiced(qtytoinvoiceiszero)")
                    self.assertEqual(line.qty_invoiced,2.0,"Theordered(serv)salelinearetotallyinvoiced(qtyinvoiced=theinvoicelines)")
                self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*line.qty_to_invoice,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*line.qty_invoiced,"Amountinvoicedisnowsetasqtyinvoiced*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(len(line.invoice_lines),1,"Thelines'ordered'qtyareinvoiced,soitshouldbelinkedto1invoicelines")

        #Makeacreditnote
        credit_note_wizard=self.env['account.move.reversal'].with_context({'active_ids':[self.invoice.id],'active_id':self.invoice.id,'active_model':'account.move'}).create({
            'refund_method':'modify', #thisistheonlymodeforwhichtheSOlineislinkedtotherefund(https://github.com/flectra/flectra/commit/e680f29560ac20133c7af0c6364c6ef494662eac)
            'reason':'reasontestmodify',
        })
        invoice_refund=self.env['account.move'].browse(credit_note_wizard.reverse_moves()['res_id'])

        #Checkinvoice'stypeandnumber
        self.assertEqual(invoice_refund.move_type,'out_invoice','Thelastcreatedinvoicedshouldbeacustomerinvoice')
        self.assertEqual(invoice_refund.state,'draft','LastCustomerinvoicesshouldbeindraft')
        self.assertEqual(self.sale_order.invoice_count,3,"TheSOshouldhave3relatedinvoices:theoriginal,therefund,andthenewone")
        self.assertEqual(len(self.sale_order.invoice_ids.filtered(lambdainv:inv.move_type=='out_refund')),1,"TheSOshouldbelinkedtoonlyonerefund")
        self.assertEqual(len(self.sale_order.invoice_ids.filtered(lambdainv:inv.move_type=='out_invoice')),2,"TheSOshouldbelinkedtotwocustomerinvoices")

        #Atthistime,theinvoice1anditsrefundareconfirmed,sotheamountsinvoicedarezero.Thethirdinvoice
        #(2ndcustomerinv)isindraftstate.
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,2.0,"Theqtytoinvoicedoesnotchangewhenconfirmingthenewinvoice(2)")
                    self.assertEqual(line.qty_invoiced,3.0,"Theordered(prod)salelinedoesnotchangeoninvoice2confirmation")
                    self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*5,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,fororderedproducts")
                    self.assertEqual(line.untaxed_amount_invoiced,0.0,"Amountinvoicediszeroastheinvoice1anditsrefundarereconcilied")
                    self.assertEqual(len(line.invoice_lines),3,"Theline'orderedconsumable'isinvoiced,soitshouldbelinkedto3invoicelines(invoiceandrefund)")
                else:
                    self.assertEqual(line.qty_to_invoice,1.0,"Theqtytoinvoicedoesnotchangewhenconfirmingthenewinvoice(2)")
                    self.assertEqual(line.qty_invoiced,2.0,"Theordered(serv)salelinedoesnotchangeoninvoice2confirmation")
                    self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*3,"Amounttoinvoiceisnowsetasunitprice*orderedqty-refundqty)evenifthe")
                    self.assertEqual(line.untaxed_amount_invoiced,0.0,"Amountinvoicediszeroastheinvoice1anditsrefundarereconcilied")
                    self.assertEqual(len(line.invoice_lines),3,"Theline'orderedservice'isinvoiced,soitshouldbelinkedto3invoicelines(invoiceandrefund)")

        #Changeunitoforderedproductonrefundlines
        move_form=Form(invoice_refund)
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.price_unit=100
        withmove_form.invoice_line_ids.edit(1)asline_form:
            line_form.price_unit=50
        invoice_refund=move_form.save()

        #Validatetherefund
        invoice_refund.action_post()

        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
                self.assertFalse(line.invoice_lines,"Thelinebasedondeliveredarenotinvoiced,sotheyshouldnotbelinkedtoinvoiceline,evenaftervalidation")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,2.0,"Theqtytoinvoicedoesnotchangewhenconfirmingthenewinvoice(3)")
                    self.assertEqual(line.qty_invoiced,3.0,"Theorderedsalelinearetotallyinvoiced(qtyinvoiced=orderedqty)")
                    self.assertEqual(line.untaxed_amount_to_invoice,1100.0,"")
                    self.assertEqual(line.untaxed_amount_invoiced,300.0,"")
                    self.assertEqual(len(line.invoice_lines),3,"Theline'orderedconsumable'isinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund),evenaftervalidation")
                else:
                    self.assertEqual(line.qty_to_invoice,1.0,"Theqtytoinvoicedoesnotchangewhenconfirmingthenewinvoice(3)")
                    self.assertEqual(line.qty_invoiced,2.0,"Theorderedsalelinearetotallyinvoiced(qtyinvoiced=orderedqty)")
                    self.assertEqual(line.untaxed_amount_to_invoice,170.0,"")
                    self.assertEqual(line.untaxed_amount_invoiced,100.0,"")
                    self.assertEqual(len(line.invoice_lines),3,"Theline'orderedservice'isinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund),evenaftervalidation")

    deftest_refund_invoice_with_downpayment(self):
        sale_order_refund=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        sol_product=self.env['sale.order.line'].create({
            'name':self.company_data['product_order_no'].name,
            'product_id':self.company_data['product_order_no'].id,
            'product_uom_qty':5,
            'product_uom':self.company_data['product_order_no'].uom_id.id,
            'price_unit':self.company_data['product_order_no'].list_price,
            'order_id':sale_order_refund.id,
            'tax_id':False,
        })

        sale_order_refund.action_confirm()
        so_context={
            'active_model':'sale.order',
            'active_ids':[sale_order_refund.id],
            'active_id':sale_order_refund.id,
            'default_journal_id':self.company_data['default_journal_sale'].id,
        }

        downpayment=self.env['sale.advance.payment.inv'].with_context(so_context).create({
            'advance_payment_method':'percentage',
            'amount':50,
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        sale_order_refund.invoice_ids[0].action_post()
        sol_downpayment=sale_order_refund.order_line[1]

        payment=self.env['sale.advance.payment.inv'].with_context(so_context).create({
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        payment.create_invoices()

        so_invoice=max(sale_order_refund.invoice_ids)
        self.assertEqual(len(so_invoice.invoice_line_ids.filtered(lambdal:not(l.display_type=='line_section'andl.name=="DownPayments"))),len(sale_order_refund.order_line),'Alllinesshouldbeinvoiced')
        self.assertEqual(len(so_invoice.invoice_line_ids.filtered(lambdal:l.display_type=='line_section'andl.name=="DownPayments")),1,'Asinglesectionfordownpaymentsshouldbepresent')
        self.assertEqual(so_invoice.amount_total,sale_order_refund.amount_total-sol_downpayment.price_unit,'Downpaymentshouldbeapplied')
        so_invoice.action_post()

        credit_note_wizard=self.env['account.move.reversal'].with_context({'active_ids':[so_invoice.id],'active_id':so_invoice.id,'active_model':'account.move'}).create({
            'refund_method':'refund',
            'reason':'reasontestrefundwithdownpayment',
        })
        credit_note_wizard.reverse_moves()
        invoice_refund=sale_order_refund.invoice_ids.sorted(key=lambdainv:inv.id,reverse=False)[-1]
        invoice_refund.action_post()

        self.assertEqual(sol_product.qty_to_invoice,5.0,"Astherefundstillexists,thequantitytoinvoiceistheorderedquantity")
        self.assertEqual(sol_product.qty_invoiced,0.0,"Theqtyinvoicedshouldbezeroas,withtherefund,thequantitiescanceleachother")
        self.assertEqual(sol_product.untaxed_amount_to_invoice,sol_product.price_unit*5,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,asrefundisvalidated")
        self.assertEqual(sol_product.untaxed_amount_invoiced,0.0,"Amountinvoiceddecreasedastherefundisnowconfirmed")
        self.assertEqual(len(sol_product.invoice_lines),2,"Theproductlineisinvoiced,soitshouldbelinkedto2invoicelines(invoiceandrefund)")

        self.assertEqual(sol_downpayment.qty_to_invoice,-1.0,"Asthedownpaymentwasinvoicedseparately,itwillstillhavetobedeductedfromthetotalinvoice(hence-1.0),aftertherefund.")
        self.assertEqual(sol_downpayment.qty_invoiced,1.0,"Theqtytoinvoiceshouldbe1as,withtherefund,theproductsarenotinvoicedanymore,butthedownpaymentstillis")
        self.assertEqual(sol_downpayment.untaxed_amount_to_invoice,-(sol_product.price_unit*5)/2,"Amounttoinvoicedecreasedastherefundisnowconfirmed")
        self.assertEqual(sol_downpayment.untaxed_amount_invoiced,(sol_product.price_unit*5)/2,"Amountinvoicedisnowsetashalfofallproducts'totalamounttoinvoice,asrefundisvalidated")
        self.assertEqual(len(sol_downpayment.invoice_lines),3,"Theproductlineisinvoiced,soitshouldbelinkedto3invoicelines(downpaymentinvoice,partialinvoiceandrefund)")
