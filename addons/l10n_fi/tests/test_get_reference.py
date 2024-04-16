#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classInvoiceGetReferenceTest(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_fi.fi_chart_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.invoice=cls.init_invoice('out_invoice',products=cls.product_a+cls.product_b)

    deftest_get_reference_finnish_invoice(self):
        self.assertFalse(self.invoice.payment_reference)
        self.invoice.journal_id.invoice_reference_model='fi'
        self.invoice.action_post()
        self.assertTrue(self.invoice.payment_reference)

    deftest_get_reference_finnish_partner(self):
        self.assertFalse(self.invoice.payment_reference)
        self.invoice.journal_id.invoice_reference_type='partner'
        self.invoice.journal_id.invoice_reference_model='fi'
        self.invoice.action_post()
        self.assertTrue(self.invoice.payment_reference)

    deftest_get_reference_finnish_rf_invoice(self):
        self.assertFalse(self.invoice.payment_reference)
        self.invoice.journal_id.invoice_reference_model='fi_rf'
        self.invoice.action_post()
        self.assertTrue(self.invoice.payment_reference)

    deftest_get_reference_finnish_rf_partner(self):
        self.assertFalse(self.invoice.payment_reference)
        self.invoice.journal_id.invoice_reference_type='partner'
        self.invoice.journal_id.invoice_reference_model='fi_rf'
        self.invoice.action_post()
        self.assertTrue(self.invoice.payment_reference)
