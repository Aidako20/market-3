#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.toolsimportfloat_is_zero
from.commonimportTestSaleCommon
fromflectra.testsimportForm,tagged


@tagged('-at_install','post_install')
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

        #Context
        cls.context={
            'active_model':'sale.order',
            'active_ids':[cls.sale_order.id],
            'active_id':cls.sale_order.id,
            'default_journal_id':cls.company_data['default_journal_sale'].id,
        }

    def_check_order_search(self,orders,domain,expected_result):
        domain+=[('id','in',orders.ids)]
        result=self.env['sale.order'].search(domain)
        self.assertEqual(result,expected_result,"Unexpectedresultonsearchorders")

    deftest_search_invoice_ids(self):
        """Testsearchingoncomputedfieldsinvoice_ids"""

        #Makeqtyzerotohavealinewithoutinvoices
        self.sol_prod_order.product_uom_qty=0
        self.sale_order.action_confirm()

        #Testsbeforecreatinganinvoice
        self._check_order_search(self.sale_order,[('invoice_ids','=',False)],self.sale_order)
        self._check_order_search(self.sale_order,[('invoice_ids','!=',False)],self.env['sale.order'])

        #Createinvoice
        moves=self.sale_order._create_invoices()

        #Testsaftercreatingtheinvoice
        self._check_order_search(self.sale_order,[('invoice_ids','in',moves.ids)],self.sale_order)
        self._check_order_search(self.sale_order,[('invoice_ids','=',False)],self.env['sale.order'])
        self._check_order_search(self.sale_order,[('invoice_ids','!=',False)],self.sale_order)

    deftest_downpayment(self):
        """Testinvoicewithawayofdownpaymentandcheckdownpayment'sSOlineiscreated
            andalsocheckatotalamountofinvoiceisequaltoarespectivesaleorder'stotalamount
        """
        #ConfirmtheSO
        self.sale_order.action_confirm()
        self._check_order_search(self.sale_order,[('invoice_ids','=',False)],self.sale_order)
        #Let'sdoaninvoiceforadepositof100
        downpayment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'fixed',
            'fixed_amount':50,
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        downpayment2=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'fixed',
            'fixed_amount':50,
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        downpayment2.create_invoices()
        self._check_order_search(self.sale_order,[('invoice_ids','=',False)],self.env['sale.order'])

        self.assertEqual(len(self.sale_order.invoice_ids),2,'InvoiceshouldbecreatedfortheSO')
        downpayment_line=self.sale_order.order_line.filtered(lambdal:l.is_downpayment)
        self.assertEqual(len(downpayment_line),2,'SOlinedownpaymentshouldbecreatedonSO')

        #UpdatedeliveredquantityofSOlines
        self.sol_serv_deliver.write({'qty_delivered':4.0})
        self.sol_prod_deliver.write({'qty_delivered':2.0})

        #Let'sdoaninvoicewithrefunds
        payment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        payment.create_invoices()

        self.assertEqual(len(self.sale_order.invoice_ids),3,'InvoiceshouldbecreatedfortheSO')

        invoice=max(self.sale_order.invoice_ids)
        self.assertEqual(len(invoice.invoice_line_ids.filtered(lambdal:not(l.display_type=='line_section'andl.name=="DownPayments"))),len(self.sale_order.order_line),'Alllinesshouldbeinvoiced')
        self.assertEqual(len(invoice.invoice_line_ids.filtered(lambdal:l.display_type=='line_section'andl.name=="DownPayments")),1,'Asinglesectionfordownpaymentsshouldbepresent')
        self.assertEqual(invoice.amount_total,self.sale_order.amount_total-sum(downpayment_line.mapped('price_unit')),'Downpaymentshouldbeapplied')

    deftest_downpayment_line_remains_on_SO(self):
        """Testdownpayment'sSOlineiscreatedandremainsunchangedevenifeverythingisinvoiced
        """
        #CreatetheSOwithoneline
        sale_order=self.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })
        sale_order_line=self.env['sale.order.line'].with_context(tracking_disable=True).create({
            'name':self.company_data['product_order_no'].name,
            'product_id':self.company_data['product_order_no'].id,
            'product_uom_qty':5,
            'product_uom':self.company_data['product_order_no'].uom_id.id,
            'price_unit':self.company_data['product_order_no'].list_price,
            'order_id':sale_order.id,
            'tax_id':False,
        })
        #ConfirmtheSO
        sale_order.action_confirm()
        #UpdatedeliveredquantityofSOline
        sale_order_line.write({'qty_delivered':5.0})
        context={
            'active_model':'sale.order',
            'active_ids':[sale_order.id],
            'active_id':sale_order.id,
            'default_journal_id':self.company_data['default_journal_sale'].id,
        }
        #Let'sdoaninvoiceforadownpaymentof50
        downpayment=self.env['sale.advance.payment.inv'].with_context(context).create({
            'advance_payment_method':'fixed',
            'fixed_amount':50,
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        #Let'sdotheinvoice
        payment=self.env['sale.advance.payment.inv'].with_context(context).create({
            'deposit_account_id':self.company_data['default_account_revenue'].id
        })
        payment.create_invoices()
        #Confirmallinvoices
        forinvoiceinsale_order.invoice_ids:
            invoice.action_post()
        downpayment_line=sale_order.order_line.filtered(lambdal:l.is_downpayment)
        self.assertEqual(downpayment_line[0].price_unit,50,'ThedownpaymentunitpriceshouldnotchangeonSO')

    deftest_downpayment_percentage_tax_icl(self):
        """Testinvoicewithapercentagedownpaymentandanincludedtax
            Checkthetotalamountofinvoiceiscorrectandequaltoarespectivesaleorder'stotalamount
        """
        #ConfirmtheSO
        self.sale_order.action_confirm()
        tax_downpayment=self.company_data['default_tax_sale'].copy({'price_include':True})
        #Let'sdoaninvoiceforadepositof100
        product_id=self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        product_id=self.env['product.product'].browse(int(product_id)).exists()
        product_id.taxes_id=tax_downpayment.ids
        payment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'percentage',
            'amount':50,
            'deposit_account_id':self.company_data['default_account_revenue'].id,
        })
        payment.create_invoices()

        self.assertEqual(len(self.sale_order.invoice_ids),1,'InvoiceshouldbecreatedfortheSO')
        downpayment_line=self.sale_order.order_line.filtered(lambdal:l.is_downpayment)
        self.assertEqual(len(downpayment_line),1,'SOlinedownpaymentshouldbecreatedonSO')
        self.assertEqual(downpayment_line.price_unit,self.sale_order.amount_total/2,'downpaymentshouldhavethecorrectamount')

        invoice=self.sale_order.invoice_ids[0]
        downpayment_aml=invoice.line_ids.filtered(lambdal:not(l.display_type=='line_section'andl.name=="DownPayments"))[0]
        self.assertEqual(downpayment_aml.price_total,self.sale_order.amount_total/2,'downpaymentshouldhavethecorrectamount')
        self.assertEqual(downpayment_aml.price_unit,self.sale_order.amount_total/2,'downpaymentshouldhavethecorrectamount')
        invoice.action_post()
        self.assertEqual(downpayment_line.price_unit,self.sale_order.amount_total/2,'downpaymentshouldhavethecorrectamount')

    deftest_invoice_with_discount(self):
        """TestinvoicewithadiscountandcheckdiscountappliedonbothSOlinesandaninvoicelines"""
        #UpdatediscountanddeliveredquantityonSOlines
        self.sol_prod_order.write({'discount':20.0})
        self.sol_serv_deliver.write({'discount':20.0,'qty_delivered':4.0})
        self.sol_serv_order.write({'discount':-10.0})
        self.sol_prod_deliver.write({'qty_delivered':2.0})

        forlineinself.sale_order.order_line.filtered(lambdal:l.discount):
            product_price=line.price_unit*line.product_uom_qty
            self.assertEqual(line.discount,(product_price-line.price_subtotal)/product_price*100,'Discountshouldbeappliedonorderline')

        #linesareindraft
        forlineinself.sale_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_to_invoice,precision_digits=2),"Theamounttoinvoiceshouldbezero,asthelineisindrafstate")
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced,precision_digits=2),"Theinvoicedamountshouldbezero,asthelineisindraftstate")

        self.sale_order.action_confirm()

        forlineinself.sale_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced,precision_digits=2),"Theinvoicedamountshouldbezero,asthelineisindraftstate")

        self.assertEqual(self.sol_serv_order.untaxed_amount_to_invoice,297,"Theuntaxedamounttoinvoiceiswrong")
        self.assertEqual(self.sol_serv_deliver.untaxed_amount_to_invoice,self.sol_serv_deliver.qty_delivered*self.sol_serv_deliver.price_reduce,"Theuntaxedamounttoinvoiceshouldbeqtydeli*pricereduce,so4*(180-36)")
        #'untaxed_amount_to_invoice'isinvalidwhen'sale_stock'isinstalled.
        #self.assertEqual(self.sol_prod_deliver.untaxed_amount_to_invoice,140,"Theuntaxedamounttoinvoiceshouldbeqtydeli*pricereduce,so4*(180-36)")

        #Let'sdoaninvoicewithinvoiceablelines
        payment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered'
        })
        self._check_order_search(self.sale_order,[('invoice_ids','=',False)],self.sale_order)
        payment.create_invoices()
        self._check_order_search(self.sale_order,[('invoice_ids','=',False)],self.env['sale.order'])
        invoice=self.sale_order.invoice_ids[0]
        invoice.action_post()

        #CheckdiscountappearedonbothSOlinesandinvoicelines
        forline,inv_lineinzip(self.sale_order.order_line,invoice.invoice_line_ids):
            self.assertEqual(line.discount,inv_line.discount,'Discountonlinesoforderandinvoiceshouldbesame')

    deftest_invoice(self):
        """TestcreateandinvoicefromtheSO,andcheckqtyinvoice/toinvoice,andtherelatedamounts"""
        #linesareindraft
        forlineinself.sale_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_to_invoice,precision_digits=2),"Theamounttoinvoiceshouldbezero,asthelineisindrafstate")
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced,precision_digits=2),"Theinvoicedamountshouldbezero,asthelineisindraftstate")

        #ConfirmtheSO
        self.sale_order.action_confirm()

        #Checkorderedquantity,quantitytoinvoiceandinvoicedquantityofSOlines
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,'Quantitytoinvoiceshouldbesameasorderedquantity')
                self.assertEqual(line.qty_invoiced,0.0,'InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO')
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
            else:
                self.assertEqual(line.qty_to_invoice,line.product_uom_qty,'Quantitytoinvoiceshouldbesameasorderedquantity')
                self.assertEqual(line.qty_invoiced,0.0,'InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO')
                self.assertEqual(line.untaxed_amount_to_invoice,line.product_uom_qty*line.price_unit,"Theamounttoinvoiceshouldthetotaloftheline,asthelineisconfirmed")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelineisconfirmed")

        #Let'sdoaninvoicewithinvoiceablelines
        payment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered'
        })
        payment.create_invoices()

        invoice=self.sale_order.invoice_ids[0]

        #Updatequantityofaninvoicelines
        move_form=Form(invoice)
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.quantity=3.0
        withmove_form.invoice_line_ids.edit(1)asline_form:
            line_form.quantity=2.0
        invoice=move_form.save()

        #amounttoinvoice/invoicedshouldnothavechanged(amountstakeonlyconfirmedinvoiceintoaccount)
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbezero")
                self.assertEqual(line.qty_invoiced,0.0,"Invoicedquantityshouldbezeroasdeliveredlinesarenotdeliveredyet")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity(noconfirmedinvoice)")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asnoinvoicearevalidatedfornow")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(self.sol_prod_order.qty_to_invoice,2.0,"ChangingthequantityondraftinvoiceupdatetheqtytoinvoiceonSOlines")
                    self.assertEqual(self.sol_prod_order.qty_invoiced,3.0,"ChangingthequantityondraftinvoiceupdatetheinvoicedqtyonSOlines")
                else:
                    self.assertEqual(self.sol_serv_order.qty_to_invoice,1.0,"ChangingthequantityondraftinvoiceupdatetheqtytoinvoiceonSOlines")
                    self.assertEqual(self.sol_serv_order.qty_invoiced,2.0,"ChangingthequantityondraftinvoiceupdatetheinvoicedqtyonSOlines")
                self.assertEqual(line.untaxed_amount_to_invoice,line.product_uom_qty*line.price_unit,"Theamounttoinvoiceshouldthetotaloftheline,asthelineisconfirmed(noconfirmedinvoice)")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asnoinvoicearevalidatedfornow")

        invoice.action_post()

        #CheckquantitytoinvoiceonSOlines
        forlineinself.sale_order.order_line:
            ifline.product_id.invoice_policy=='delivery':
                self.assertEqual(line.qty_to_invoice,0.0,"Quantitytoinvoiceshouldbesameasorderedquantity")
                self.assertEqual(line.qty_invoiced,0.0,"InvoicedquantityshouldbezeroasnoanyinvoicecreatedforSO")
                self.assertEqual(line.untaxed_amount_to_invoice,0.0,"Theamounttoinvoiceshouldbezero,asthelinebasedondeliveredquantity")
                self.assertEqual(line.untaxed_amount_invoiced,0.0,"Theinvoicedamountshouldbezero,asthelinebasedondeliveredquantity")
            else:
                ifline==self.sol_prod_order:
                    self.assertEqual(line.qty_to_invoice,2.0,"Theorderedsalelinearetotallyinvoiced(qtytoinvoiceiszero)")
                    self.assertEqual(line.qty_invoiced,3.0,"Theordered(prod)salelinearetotallyinvoiced(qtyinvoicedcomefromtheinvoicelines)")
                else:
                    self.assertEqual(line.qty_to_invoice,1.0,"Theorderedsalelinearetotallyinvoiced(qtytoinvoiceiszero)")
                    self.assertEqual(line.qty_invoiced,2.0,"Theordered(serv)salelinearetotallyinvoiced(qtyinvoiced=theinvoicelines)")
                self.assertEqual(line.untaxed_amount_to_invoice,line.price_unit*line.qty_to_invoice,"Amounttoinvoiceisnowsetasqtytoinvoice*unitpricesincenopricechangeoninvoice,fororderedproducts")
                self.assertEqual(line.untaxed_amount_invoiced,line.price_unit*line.qty_invoiced,"Amountinvoicedisnowsetasqtyinvoiced*unitpricesincenopricechangeoninvoice,fororderedproducts")

    deftest_multiple_sale_orders_on_same_invoice(self):
        """ThemodelallowstheassociationofmultipleSOlineslinkedtothesameinvoiceline.
            Checkthattheoperationsbehavewell,ifacustommodulecreatessuchasituation.
        """
        self.sale_order.action_confirm()
        payment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered'
        })
        payment.create_invoices()

        #createasecondSOwhoselinesarelinkedtothesameinvoicelines
        #thisisawaytocreateasituationwheresale_line_idshasmultipleitems
        sale_order_data=self.sale_order.copy_data()[0]
        sale_order_data['order_line']=[
            (0,0,line.copy_data({
                'invoice_lines':[(6,0,line.invoice_lines.ids)],
            })[0])
            forlineinself.sale_order.order_line
        ]
        self.sale_order.create(sale_order_data)

        #weshouldnowhaveatleastonemovelinelinkedtoseveralorderlines
        invoice=self.sale_order.invoice_ids[0]
        self.assertTrue(any(len(move_line.sale_line_ids)>1
                            formove_lineininvoice.line_ids))

        #howevertheseactionsshouldnotraise
        invoice.action_post()
        invoice.button_draft()
        invoice.button_cancel()

    deftest_invoice_with_sections(self):
        """TestcreateandinvoicewithsectionsfromtheSO,andcheckqtyinvoice/toinvoice,andtherelatedamounts"""

        sale_order=self.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })

        SaleOrderLine=self.env['sale.order.line'].with_context(tracking_disable=True)
        SaleOrderLine.create({
            'name':'Section',
            'display_type':'line_section',
            'order_id':sale_order.id,
        })
        sol_prod_deliver=SaleOrderLine.create({
            'name':self.company_data['product_order_no'].name,
            'product_id':self.company_data['product_order_no'].id,
            'product_uom_qty':5,
            'product_uom':self.company_data['product_order_no'].uom_id.id,
            'price_unit':self.company_data['product_order_no'].list_price,
            'order_id':sale_order.id,
            'tax_id':False,
        })

        #ConfirmtheSO
        sale_order.action_confirm()

        sol_prod_deliver.write({'qty_delivered':5.0})

        #Context
        self.context={
            'active_model':'sale.order',
            'active_ids':[sale_order.id],
            'active_id':sale_order.id,
            'default_journal_id':self.company_data['default_journal_sale'].id,
        }

        #Let'sdoaninvoicewithinvoiceablelines
        payment=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered'
        })
        payment.create_invoices()

        invoice=sale_order.invoice_ids[0]

        self.assertEqual(invoice.line_ids[0].display_type,'line_section')

    deftest_qty_invoiced(self):
        """Verifyuomroundingiscorrectlyconsideredduringqty_invoicedcompute"""
        sale_order=self.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
        })

        SaleOrderLine=self.env['sale.order.line'].with_context(tracking_disable=True)
        sol_prod_deliver=SaleOrderLine.create({
            'name':self.company_data['product_order_no'].name,
            'product_id':self.company_data['product_order_no'].id,
            'product_uom_qty':5,
            'product_uom':self.company_data['product_order_no'].uom_id.id,
            'price_unit':self.company_data['product_order_no'].list_price,
            'order_id':sale_order.id,
            'tax_id':False,
        })

        #ConfirmtheSO
        sale_order.action_confirm()

        sol_prod_deliver.write({'qty_delivered':5.0})
        #Context
        self.context={
            'active_model':'sale.order',
            'active_ids':[sale_order.id],
            'active_id':sale_order.id,
            'default_journal_id':self.company_data['default_journal_sale'].id,
        }

        #Let'sdoaninvoicewithinvoiceablelines
        invoicing_wizard=self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method':'delivered'
        })
        invoicing_wizard.create_invoices()

        self.assertEqual(sol_prod_deliver.qty_invoiced,5.0)
        #Wewouldhavetochangethedigitsofthefieldto
        #testagreaterdecimalprecision.
        quantity=5.13
        move_form=Form(sale_order.invoice_ids)
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.quantity=quantity
        move_form.save()

        #Defaultuomroundingto0.01
        qty_invoiced_field=sol_prod_deliver._fields.get('qty_invoiced')
        sol_prod_deliver.env.add_to_compute(qty_invoiced_field,sol_prod_deliver)
        self.assertEqual(sol_prod_deliver.qty_invoiced,quantity)

        #Roundingto0.1,shouldberoundedwithUP(ceil)rounding_method
        #Notfloororhalfuprounding.
        sol_prod_deliver.product_uom.rounding*=10
        sol_prod_deliver.product_uom.flush(['rounding'])
        expected_qty=5.2
        qty_invoiced_field=sol_prod_deliver._fields.get('qty_invoiced')
        sol_prod_deliver.env.add_to_compute(qty_invoiced_field,sol_prod_deliver)
        self.assertEqual(sol_prod_deliver.qty_invoiced,expected_qty)
