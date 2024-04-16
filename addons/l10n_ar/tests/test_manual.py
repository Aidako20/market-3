#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
from.importcommon
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestManual(common.TestAr):

    @classmethod
    defsetUpClass(cls):
        super(TestManual,cls).setUpClass()
        cls.journal=cls._create_journal(cls,'preprinted')
        cls.partner=cls.res_partner_adhoc
        cls._create_test_invoices_like_demo(cls)

    deftest_01_create_invoice(self):
        """CreateandvalidateaninvoiceforaResponsableInscripto

        *Propersetthecurrentusercompany
        *Properlysetthetaxamountoftheproduct/partner
        *Properfiscalposition(thiscasenotfiscalpositionisselected)
        """
        invoice=self._create_invoice()
        self.assertEqual(invoice.company_id,self.company_ri,'createdwithwrongcompany')
        self.assertEqual(invoice.amount_tax,21,'invoicetaxesarenotproperlyset')
        self.assertEqual(invoice.amount_total,121.0,'invoicetaxeshasnotbeenappliedtothetotal')
        self.assertEqual(invoice.l10n_latam_document_type_id,self.document_type['invoice_a'],'selecteddocumenttypeshouldbeFacturaA')
        self._post(invoice)
        self.assertEqual(invoice.state,'posted','invoicehasnotbeenvalidateinFlectra')
        self.assertEqual(invoice.name,'FA-A%05d-00000002'%self.journal.l10n_ar_afip_pos_number,'Invoicenumberiswrong')

    deftest_02_fiscal_position(self):
        #ADHOCSA>IVAResponsableInscripto>WithoutFiscalPositon
        invoice=self._create_invoice({'partner':self.partner})
        self.assertFalse(invoice.fiscal_position_id,'Fiscalpositionshouldbesettoempty')

        #ConsumidorFinal>IVAResponsableInscripto>WithoutFiscalPositon
        invoice=self._create_invoice({'partner':self.partner_cf})
        self.assertFalse(invoice.fiscal_position_id,'Fiscalpositionshouldbesettoempty')

        #CerroCastor>IVALiberado–LeyNº19.640>Compras/VentasZonaFranca>IVAExento
        invoice=self._create_invoice({'partner':self.res_partner_cerrocastor})
        self.assertEqual(invoice.fiscal_position_id,self._search_fp('Compras/VentasZonaFranca'))

        #Expresso>Cliente/ProveedordelExterior> >IVAExento
        invoice=self._create_invoice({'partner':self.res_partner_expresso})
        self.assertEqual(invoice.fiscal_position_id,self._search_fp('Compras/Ventasalexterior'))

    deftest_03_corner_cases(self):
        """MonopartneroftypeServiceandVAT21"""
        self._post(self.demo_invoices['test_invoice_1'])

    deftest_04_corner_cases(self):
        """ExentopartnerwithmultipleVATtypes21,27and10,5'"""
        self._post(self.demo_invoices['test_invoice_2'])

    deftest_05_corner_cases(self):
        """RIpartnerwithVAT0and21"""
        self._post(self.demo_invoices['test_invoice_3'])

    deftest_06_corner_cases(self):
        """RIpartnerwithVATexemptand21"""
        self._post(self.demo_invoices['test_invoice_4'])

    deftest_07_corner_cases(self):
        """RIpartnerwithalltypeoftaxes"""
        self._post(self.demo_invoices['test_invoice_5'])

    deftest_08_corner_cases(self):
        """ConsumidorFinal"""
        self._post(self.demo_invoices['test_invoice_8'])

    deftest_09_corner_cases(self):
        """RIpartnerwithmanylinesinordertoproveroundingerror,with4 decimalsofprecisionforthe
        currencyand2decimalsfortheproducttheerrorappear"""
        self._post(self.demo_invoices['test_invoice_11'])

    deftest_10_corner_cases(self):
        """RIpartnerwithmanylinesinordertotestroundingerror,itisrequired tousea4decimalprecision
        inproductinordertotheerroroccur"""
        self._post(self.demo_invoices['test_invoice_12'])

    deftest_11_corner_cases(self):
        """RIpartnerwithmanylinesinordertotestzeroamount invoicesyroundingerror.itisrequiredto
        settheproductdecimalprecisionto4andchange260,59for260.60inordertoreproducetheerror"""
        self._post(self.demo_invoices['test_invoice_13'])

    deftest_12_corner_cases(self):
        """RIpartnerwith100%%ofdiscount"""
        self._post(self.demo_invoices['test_invoice_17'])

    deftest_13_corner_cases(self):
        """RIpartnerwith100%%ofdiscountandwithdifferentVATaliquots"""
        self._post(self.demo_invoices['test_invoice_18'])

    deftest_14_corner_cases(self):
        """ResponsableInscripto"inUSDandVAT21"""
        self._prepare_multicurrency_values()
        self._post(self.demo_invoices['test_invoice_10'])
