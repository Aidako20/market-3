#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimportcommon,Form

QR_IBAN='CH2130808001234567827'
ISR_SUBS_NUMBER="01-162-8"


classTestGenISRReference(AccountTestInvoicingCommon):
    """Checkconditionofgenerationofandcontentofthestructuredref"""

    @classmethod
    defsetUpClass(cls,chart_template_ref="l10n_ch.l10nch_chart_template"):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env=cls.env(context=dict(cls.env.context,tracking_disable=True))
        cls.bank=cls.env["res.bank"].create(
            {
                "name":"AlternativeBankSchweizAG",
                "bic":"ALSWCH21XXX",
            }
        )
        cls.bank_acc_isr=cls.env["res.partner.bank"].create(
            {
                "acc_number":"ISR",
                "l10n_ch_isr_subscription_chf":"01-162-8",
                "bank_id":cls.bank.id,
                "partner_id":cls.partner_a.id,
            }
        )
        cls.bank_acc_qriban=cls.env["res.partner.bank"].create(
            {
                "acc_number":QR_IBAN,
                "bank_id":cls.bank.id,
                "partner_id":cls.partner_a.id,
            }
        )
        cls.invoice=cls.init_invoice("out_invoice",products=cls.product_a+cls.product_b)

    deftest_isr(self):

        self.invoice.partner_bank_id=self.bank_acc_isr
        self.invoice.name="INV/01234567890"

        expected_isr="000000000000000012345678903"
        expected_isr_spaced="000000000000000012345678903"
        expected_optical_line="0100001307807>000000000000000012345678903+010001628>"
        self.assertEqual(self.invoice.l10n_ch_isr_number,expected_isr)
        self.assertEqual(self.invoice.l10n_ch_isr_number_spaced,expected_isr_spaced)
        self.assertEqual(self.invoice.l10n_ch_isr_optical_line,expected_optical_line)

    deftest_qrr(self):
        self.invoice.partner_bank_id=self.bank_acc_qriban

        self.invoice.name="INV/01234567890"

        expected_isr="000000000000000012345678903"
        expected_isr_spaced="000000000000000012345678903"
        self.assertEqual(self.invoice.l10n_ch_isr_number,expected_isr)
        self.assertEqual(self.invoice.l10n_ch_isr_number_spaced,expected_isr_spaced)
        #Noneedtocheckopticalline,wehavenouseforitwithQR-bill

    deftest_isr_long_reference(self):
        self.invoice.partner_bank_id=self.bank_acc_isr

        self.invoice.name="INV/123456789012345678901234567890"

        expected_isr="567890123456789012345678901"
        expected_isr_spaced="567890123456789012345678901"
        expected_optical_line="0100001307807>567890123456789012345678901+010001628>"
        self.assertEqual(self.invoice.l10n_ch_isr_number,expected_isr)
        self.assertEqual(self.invoice.l10n_ch_isr_number_spaced,expected_isr_spaced)
        self.assertEqual(self.invoice.l10n_ch_isr_optical_line,expected_optical_line)

    deftest_missing_isr_subscription_num(self):
        self.bank_acc_isr.l10n_ch_isr_subscription_chf=False

        self.invoice.partner_bank_id=self.bank_acc_isr

        self.assertFalse(self.invoice.l10n_ch_isr_number)
        self.assertFalse(self.invoice.l10n_ch_isr_number_spaced)
        self.assertFalse(self.invoice.l10n_ch_isr_optical_line)

    deftest_missing_isr_subscription_num_in_wrong_field(self):
        self.bank_acc_isr.l10n_ch_isr_subscription_chf=False
        self.bank_acc_isr.l10n_ch_postal=ISR_SUBS_NUMBER

        self.invoice.partner_bank_id=self.bank_acc_isr

        self.assertFalse(self.invoice.l10n_ch_isr_number)
        self.assertFalse(self.invoice.l10n_ch_isr_number_spaced)
        self.assertFalse(self.invoice.l10n_ch_isr_optical_line)

    deftest_no_bank_account(self):
        self.invoice.partner_bank_id=False

        self.assertFalse(self.invoice.l10n_ch_isr_number)
        self.assertFalse(self.invoice.l10n_ch_isr_number_spaced)
        self.assertFalse(self.invoice.l10n_ch_isr_optical_line)

    deftest_wrong_currency(self):
        self.invoice.partner_bank_id=self.bank_acc_isr
        self.invoice.currency_id=self.env.ref("base.BTN")

        self.assertFalse(self.invoice.l10n_ch_isr_number)
        self.assertFalse(self.invoice.l10n_ch_isr_number_spaced)
        self.assertFalse(self.invoice.l10n_ch_isr_optical_line)
