#-*-coding:utf-8-*-

fromflectra.testsimporttagged
fromflectra.exceptionsimportUserError
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon

@tagged('post_install','-at_install')
classTestSwissQRCode(AccountTestInvoicingCommon):
    """TeststhegenerationofSwissQR-codesoninvoices
    """

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_ch.l10nch_chart_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].qr_code=True
        cls.company_data['company'].country_id=None

        cls.swiss_iban=cls.env['res.partner.bank'].create({
            'acc_number':'CH1538815158384538437',
            'partner_id':cls.company_data['company'].partner_id.id,
        })

        cls.swiss_qr_iban=cls.env['res.partner.bank'].create({
            'acc_number':'CH2130808001234567827',
            'partner_id':cls.company_data['company'].partner_id.id,
        })

        cls.ch_qr_invoice=cls.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':cls.partner_a.id,
            'currency_id':cls.env.ref('base.CHF').id,
            'partner_bank_id':cls.swiss_iban.id,
            'company_id':cls.company_data['company'].id,
            'payment_reference':"Papaavulefifidelolo",
            'invoice_line_ids':[
                (0,0,{'quantity':1,'price_unit':100})
            ],
        })

    def_assign_partner_address(self,partner):
        partner.write({
            'country_id':self.env.ref('base.ch').id,
            'street':"Crabstreet,11",
            'city':"CrabCity",
            'zip':"4242",
        })

    deftest_swiss_qr_code_generation(self):
        """CheckdifferentcasesofSwissQR-codegeneration,whenqr_methodis
        specifiedbeforehand.
        """
        self.ch_qr_invoice.qr_code_method='ch_qr'

        #FirstcheckwitharegularIBAN
        withself.assertRaises(UserError,msg="Itshouldn'tbepossibletogenerateaSwissQR-codeforpartnerswithoutacompleteSwissaddress."):
            self.ch_qr_invoice.generate_qr_code()

        #Settingtheaddressshouldmakeitwork
        self._assign_partner_address(self.ch_qr_invoice.company_id.partner_id)
        self._assign_partner_address(self.ch_qr_invoice.partner_id)

        self.ch_qr_invoice.generate_qr_code()

        #Now,checkwithaQR-IBANasthepaymentaccount
        self.ch_qr_invoice.partner_bank_id=self.swiss_qr_iban

        withself.assertRaises(UserError,msg="Itshouldn'tbepossibletogenerateaSwissQR-cdeforaQR-IBANwithoutgivingitavalidQR-referenceaspaymentreference."):
            self.ch_qr_invoice.generate_qr_code()

        #AssigningaQRreferenceshouldfixit
        self.ch_qr_invoice.payment_reference='210000000003139471430009017'

        #eveniftheinvoiceisnotissuedfromSwitzerlandwewanttogeneratethecode
        self.ch_qr_invoice.company_id.partner_id.country_id=self.env.ref('base.fr')
        self.ch_qr_invoice.generate_qr_code()

    deftest_ch_qr_code_detection(self):
        """ChecksSwissQR-codeauto-detectionwhennospecificQR-method
        isgiventotheinvoice.
        """
        self._assign_partner_address(self.ch_qr_invoice.company_id.partner_id)
        self._assign_partner_address(self.ch_qr_invoice.partner_id)
        self.ch_qr_invoice.generate_qr_code()
        self.assertEqual(self.ch_qr_invoice.qr_code_method,'ch_qr',"SwissQR-codegeneratorshouldhavebeenchosenforthisinvoice.")
