#-*-coding:utf-8-*-
fromflectraimporttests
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.toolsimportmute_logger


@tests.tagged('post_install','-at_install')
classTestSaleTransaction(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].country_id=cls.env.ref('base.us')

        cls.order=cls.env['sale.order'].create({
            'partner_id':cls.partner_a.id,
            'order_line':[
                (0,False,{
                    'product_id':cls.product_a.id,
                    'name':'1Product',
                    'price_unit':100.0,
                }),
            ],
        })
        cls.env.ref('payment.payment_acquirer_transfer').journal_id=cls.company_data['default_journal_cash']

        cls.transaction=cls.order._create_payment_transaction({
            'acquirer_id':cls.env.ref('payment.payment_acquirer_transfer').id,
        })

    deftest_sale_invoicing_from_transaction(self):
        '''Testthefollowingscenario:
        -Createasaleorder
        -Createatransactionforthesaleorder.
        -Confirmthetransactionbutnoinvoicegeneratedautomatically.
        -Createmanuallyaninvoiceforthissaleorder.
        =>Theinvoicemustbepaid.
        '''
        self.transaction._set_transaction_done()
        self.transaction._post_process_after_done()

        #Assertapostedpaymenthasbeengeneratedatthispoint.
        self.assertTrue(self.transaction.payment_id)
        self.assertEqual(self.transaction.payment_id.state,'posted')

        #Doesn'tworkwithstockinstalled.
        #invoice=self.order._create_invoices()
        #invoice.post()
        #
        #self.assertTrue(invoice.payment_statein('in_payment','paid'),"Invoiceshouldbepaid")

    deftest_sale_transaction_mismatch(self):
        """TestthatatransactionfortheincorrectamountdoesnotvalidatetheSO."""
        #modifyordertotal
        self.order.order_line[0].price_unit=200.0
        self.transaction._set_transaction_done()
        withmute_logger('flectra.addons.sale.models.payment'):
            self.transaction._post_process_after_done()
        self.assertEqual(self.order.state,'draft','atransactionforanincorrectamountshouldnotvalidateaquote')

    deftest_sale_transaction_partial_delivery(self):
        """Testthatwithautomaticinvoiceandinvoicingpolicybasedondeliveredquantity,atransactionforthepartial
        amountdoesnotvalidatetheSO."""
        #setautomaticinvoice
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice','True')
        #modifyordertotal
        self.order.order_line[0].price_unit=200.0
        #invoicingpolicyisbasedondeliveredquantity
        self.product_a.invoice_policy='delivery'
        self.transaction._set_transaction_done()
        withmute_logger('flectra.addons.sale.models.payment'):
            self.transaction.sudo()._post_process_after_done()
        self.assertEqual(self.order.state,'draft','apartialtransactionwithautomaticinvoiceandinvoice_policy=deliveryshouldnotvalidateaquote')
