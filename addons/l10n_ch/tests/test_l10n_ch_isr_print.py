#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectra.exceptionsimportValidationError


@tagged('post_install','-at_install')
classISRTest(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_ch.l10nch_chart_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)

    defprint_isr(self,invoice):
        try:
            invoice.isr_print()
            returnTrue
        exceptValidationError:
            returnFalse

    deftest_l10n_ch_postals(self):

        defassertBankAccountValid(account_number,expected_account_type,expected_postal=None):
            partner_bank=self.env['res.partner.bank'].create({
                'acc_number':account_number,
                'partner_id':self.partner_a.id,
            })
            expected_vals={'acc_type':expected_account_type}
            ifexpected_postalisnotNone:
                expected_vals['l10n_ch_postal']=expected_postal

            self.assertRecordValues(partner_bank,[expected_vals])

        assertBankAccountValid('010391391','postal',expected_postal='010391391')
        assertBankAccountValid('010391394','bank')
        assertBankAccountValid('CH6309000000250097798','iban',expected_postal='25-9779-8')
        assertBankAccountValid('GR1601101250000000012300695','iban',expected_postal=False)

    deftest_isr(self):
        isr_bank_account=self.env['res.partner.bank'].create({
            'acc_number':"ISR{}number",
            'partner_id':self.env.company.partner_id.id,
            'l10n_ch_isr_subscription_chf':'01-39139-1',
        })

        invoice_chf=self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':self.partner_a.id,
            'partner_bank_id':isr_bank_account.id,
            'currency_id':self.env.ref('base.CHF').id,
            'invoice_date':'2019-01-01',
            'invoice_line_ids':[(0,0,{'product_id':self.product_a.id})],
        })
        invoice_chf.action_post()
        self.assertTrue(self.print_isr(invoice_chf))

        invoice_eur=self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':self.partner_a.id,
            'partner_bank_id':isr_bank_account.id,
            'currency_id':self.env.ref('base.EUR').id,
            'invoice_date':'2019-01-01',
            'invoice_line_ids':[(0,0,{'product_id':self.product_a.id})],
        })
        invoice_eur.action_post()
        self.assertFalse(self.print_isr(invoice_eur))
