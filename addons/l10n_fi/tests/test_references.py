#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimporttagged
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.exceptionsimportUserError


@tagged('post_install','-at_install')
classPaymentReferenceTest(AccountTestInvoicingCommon):
    """
    AllreferencesvalidatedwiththereferencecalculatorbyNordeaBank
    http://www.nordea.fi/en/corporate-customers/payments/invoicing-and-payments/reference-number-calculator.html
    """

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_fi.fi_chart_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.invoice=cls.init_invoice('out_invoice',products=cls.product_a+cls.product_b)

    deftest_payment_reference_fi(self):

        compute=self.invoice.compute_payment_reference_finnish

        #Common
        self.assertEqual('1232',compute('INV123'))
        self.assertEqual('1326',compute('132'))
        self.assertEqual('1290',compute('ABC1B2B9C'))

        #Insufficient
        self.assertEqual('1119',compute('-1'))
        self.assertEqual('1106',compute('0'))
        self.assertEqual('1261',compute('26'))

        #Excesslength
        self.assertEqual('12345678901234567894',compute('123456789012345678901234567890'))

        #Invalid
        withself.assertRaises(UserError):
            compute('QWERTY')

    deftest_payment_reference_rf(self):

        compute=self.invoice.compute_payment_reference_finnish_rf

        #Common
        self.assertEqual('RF111232',compute('INV123'))
        self.assertEqual('RF921326',compute('132'))
        self.assertEqual('RF941290',compute('ABC1B2B9C'))

        #Insufficient
        self.assertEqual('RF551119',compute('-1'))
        self.assertEqual('RF181106',compute('0'))
        self.assertEqual('RF041261',compute('26'))

        #Excesslength
        self.assertEqual('RF0912345678901234567894',compute('123456789012345678901234567890'))

        #Invalid
        withself.assertRaises(UserError):
            compute('QWERTY')
