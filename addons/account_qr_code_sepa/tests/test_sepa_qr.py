#-*-coding:utf-8-*-

fromflectra.exceptionsimportUserError
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectraimportfields

@tagged('post_install','-at_install')
classTestSEPAQRCode(AccountTestInvoicingCommon):
    """TeststhegenerationofSwissQR-codesoninvoices
    """

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].qr_code=True
        cls.acc_sepa_iban=cls.env['res.partner.bank'].create({
            'acc_number':'BE15001559627230',
            'partner_id':cls.company_data['company'].partner_id.id,
        })

        cls.acc_non_sepa_iban=cls.env['res.partner.bank'].create({
            'acc_number':'SA4420000001234567891234',
            'partner_id':cls.company_data['company'].partner_id.id,
        })

        cls.sepa_qr_invoice=cls.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':cls.partner_a.id,
            'currency_id':cls.env.ref('base.EUR').id,
            'partner_bank_id':cls.acc_sepa_iban.id,
            'company_id':cls.company_data['company'].id,
            'invoice_line_ids':[
                (0,0,{'quantity':1,'price_unit':100})
            ],
        })

    deftest_sepa_qr_code_generation(self):
        """CheckdifferentcasesofSEPAQR-codegeneration,whenqr_methodis
        specifiedbeforehand.
        """
        self.sepa_qr_invoice.qr_code_method='sct_qr'

        #UsingaSEPAIBANshouldwork
        self.sepa_qr_invoice.generate_qr_code()

        #Usinganon-SEPAIBANshouldn't
        self.sepa_qr_invoice.partner_bank_id=self.acc_non_sepa_iban
        withself.assertRaises(UserError,msg="Itshouldn'tbepossibletogenerateaSEPAQR-codeforIBANofcountriesoutsideSEPAzone."):
            self.sepa_qr_invoice.generate_qr_code()

        #Changingthecurrencyshouldbreakitaswell
        self.sepa_qr_invoice.partner_bank_id=self.acc_sepa_iban
        self.sepa_qr_invoice.currency_id=self.env.ref('base.USD').id
        withself.assertRaises(UserError,msg="Itshouldn'tbepossibletogenerateaSEPAQR-codeforanothercurrencyasEUR."):
            self.sepa_qr_invoice.generate_qr_code()

    deftest_sepa_qr_code_detection(self):
        """ChecksSEPAQR-codeauto-detectionwhennospecificQR-method
        isgiventotheinvoice.
        """
        self.sepa_qr_invoice.generate_qr_code()
        self.assertEqual(self.sepa_qr_invoice.qr_code_method,'sct_qr',"SEPAQR-codegeneratorshouldhavebeenchosenforthisinvoice.")

    deftest_out_invoice_create_refund_qr_code(self):
        self.sepa_qr_invoice.generate_qr_code()
        self.sepa_qr_invoice.action_post()
        move_reversal=self.env['account.move.reversal'].with_context(active_model="account.move",active_ids=self.sepa_qr_invoice.ids).create({
            'date':fields.Date.from_string('2019-02-01'),
            'reason':'noreason',
            'refund_method':'refund',
        })
        reversal=move_reversal.reverse_moves()
        reverse_move=self.env['account.move'].browse(reversal['res_id'])

        self.assertFalse(reverse_move.qr_code_method,"qr_code_methodforcreditnoteshouldbeNone")
