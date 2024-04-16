#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimportForm,common
fromflectra.exceptionsimportValidationError


CH_ISR_SUBSCRIPTION="01-162-8"
CH_POSTAL="10-8060-7"
CH_IBAN="CH1538815158384538437"
ISR_REFERENCE_GOOD="160001123456789012345678901"
ISR_REFERENCE_ZEROS="000000000000000012345678903"
ISR_REFERENCE_NO_ZEROS="12345678903"
ISR_REFERENCE_BAD="111111111111111111111111111"


classTestVendorBillISR(common.SavepointCase):
    """CheckwecanencodeVendorbillswithISRreferences

    TheISRisastructuredreferencewithachecksum.
    Userareguidedtoensuretheydon'tencodewrongISRreferences.
    OnlyvendorswithISRissueraccountssendISRreferences.

    ISRreferencescanbereceivedatleasttill2022.

    """

    @classmethod
    defsetUpClass(cls):
        super(TestVendorBillISR,cls).setUpClass()
        cls.abs_bank=cls.env["res.bank"].create(
            {"name":"AlternativeBankSchweiz","bic":"ABSOCH22XXX"}
        )
        cls.supplier1=cls.env["res.partner"].create({"name":"SupplierISR"})
        cls.supplier2=cls.env["res.partner"].create({"name":"Supplierpostal"})
        cls.supplier3=cls.env["res.partner"].create({"name":"SupplierIBAN"})

        cls.bank_acc_isr=cls.env['res.partner.bank'].create({
            "acc_number":"ISR01-162-8SupplierISR",
            "partner_id":cls.supplier1.id,
            "l10n_ch_postal":CH_ISR_SUBSCRIPTION,
        })
        cls.bank_acc_postal=cls.env['res.partner.bank'].create({
            "acc_number":CH_POSTAL,
            "partner_id":cls.supplier2.id,
            "l10n_ch_postal":CH_POSTAL,
        })
        cls.bank_acc_iban=cls.env['res.partner.bank'].create({
            "acc_number":CH_IBAN,
            "partner_id":cls.supplier2.id,
            "l10n_ch_postal":False,
        })

    deftest_isr_ref(self):
        """EnterISRreferencewithISRsubscriptionaccountnumber

        Thevendorbillcanbesaved.
        """
        self.env.company.country_id=self.env.ref('base.ch')
        form=Form(self.env["account.move"].with_context(
            default_move_type="in_invoice"),view="l10n_ch.isr_invoice_form")
        form.partner_id=self.supplier1
        form.partner_bank_id=self.bank_acc_isr

        form.payment_reference=ISR_REFERENCE_GOOD
        invoice=form.save()

        self.assertFalse(invoice.l10n_ch_isr_needs_fixing)

    deftest_isr_ref_with_zeros(self):
        """EnterISRreferencewithISRsubscriptionaccountnumber

        AnISRReferencecanhavelotsofzerosontheleft.

        Thevendorbillcanbesaved.
        """
        self.env.company.country_id=self.env.ref('base.ch')
        form=Form(self.env["account.move"].with_context(
            default_move_type="in_invoice"),view="l10n_ch.isr_invoice_form")
        form.partner_id=self.supplier1
        form.partner_bank_id=self.bank_acc_isr

        form.payment_reference=ISR_REFERENCE_ZEROS
        invoice=form.save()

        self.assertFalse(invoice.l10n_ch_isr_needs_fixing)

    deftest_isr_ref_no_zeros(self):
        """EnterISRreferencewithISRsubscriptionaccountnumber

        AnISRReferencefullofzeroscanbeenteredstartingbythe
        firstnonzerodigit.

        Thevendorbillcanbesaved.
        """
        self.env.company.country_id=self.env.ref('base.ch')
        form=Form(self.env["account.move"].with_context(
            default_move_type="in_invoice"),view="l10n_ch.isr_invoice_form")
        form.partner_id=self.supplier1
        form.partner_bank_id=self.bank_acc_isr

        form.payment_reference=ISR_REFERENCE_NO_ZEROS
        invoice=form.save()

        self.assertFalse(invoice.l10n_ch_isr_needs_fixing)

    deftest_isr_wrong_ref(self):
        """MistypeISRreferencewithISRsubscriptionaccountnumber
        Checkitwillshowthewarning
        """
        self.env.company.country_id=self.env.ref('base.ch')
        form=Form(self.env["account.move"].with_context(
            default_move_type="in_invoice"),view="l10n_ch.isr_invoice_form")
        form.partner_id=self.supplier1
        form.partner_bank_id=self.bank_acc_isr

        form.payment_reference=ISR_REFERENCE_BAD
        invoice=form.save()

        self.assertTrue(invoice.l10n_ch_isr_needs_fixing)