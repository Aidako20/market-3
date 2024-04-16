#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.addons.website.toolsimportMockRequest
fromflectra.tests.commonimporttagged


@tagged('post_install','-at_install')
classWebsiteSaleCartPayment(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.website=cls.env['website'].get_current_website()
        withMockRequest(cls.env,website=cls.website):
            cls.order=cls.website.sale_get_order(force_create=True) #Createthecarttoretrieve

        cls.acquirer=cls.env['payment.acquirer'].create({
            'name':"DummyAcquirer",
            'provider':'manual',
            'state':'test',
            'journal_id':cls.company_data['default_journal_bank'].id,
        })
        cls.tx=cls.env['payment.transaction'].create({
            'amount':1111.11,
            'currency_id':cls.currency_euro.id,
            'acquirer_id':cls.acquirer.id,
            'reference':"TestTransaction",
            'partner_id':cls.buyer.id,
        })
        cls.order.write({'transaction_ids':[(6,0,[cls.tx.id])]})

    deftest_unpaid_orders_can_be_retrieved(self):
        """Testthatfetchingsalesorderslinkedtoapaymenttransactioninthestates'draft',
        'cancel',or'error'returnstheorders."""
        forunpaid_order_tx_statein('draft','cancel','error'):
            self.tx.state=unpaid_order_tx_state
            withMockRequest(self.env,website=self.website,sale_order_id=self.order.id):
                self.assertEqual(
                    self.website.sale_get_order(),
                    self.order,
                    msg=f"Thetransactionstate'{unpaid_order_tx_state}'shouldnotprevent"
                        f"retrievingthelinkedorder.",
                )

    deftest_paid_orders_cannot_be_retrieved(self):
        """Testthatfetchingsalesorderslinkedtoapaymenttransactioninthestates'pending',
        'authorized',or'done'returnsanemptyrecordsettopreventupdatingthepaidorders."""
        withpatch(
            'flectra.addons.payment.models.payment_acquirer.PaymentAcquirer._get_feature_support',
            return_value={'authorize':['manual'],'tokenize':[],'fees':[]},
        ):
            forpaid_order_tx_statein('pending','authorized','done'):
                self.tx.state=paid_order_tx_state
                withMockRequest(self.env,website=self.website,sale_order_id=self.order.id):
                    self.assertFalse(
                        self.website.sale_get_order(),
                        msg=f"Thetransactionstate'{paid_order_tx_state}'shouldpreventretrieving"
                        f"thelinkedorder.",
                    )
