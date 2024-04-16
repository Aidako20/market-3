#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestImportVendorBill(AccountTestInvoicingCommon):

    deftest_retrieve_partner(self):

        defretrieve_partner(vat,import_vat):
            self.partner_a.with_context(no_vat_validation=True).vat=vat
            self.partner_a.flush()
            returnself.env['account.edi.format']._retrieve_partner(vat=import_vat)

        self.assertEqual(self.partner_a,retrieve_partner('BE0477472701','BE0477472701'))
        self.assertEqual(self.partner_a,retrieve_partner('BE0477472701','0477472701'))
        self.assertEqual(self.partner_a,retrieve_partner('BE0477472701','477472701'))
        self.assertEqual(self.partner_a,retrieve_partner('0477472701','BE0477472701'))
        self.assertEqual(self.partner_a,retrieve_partner('477472701','BE0477472701'))
        self.assertEqual(self.env['res.partner'],retrieve_partner('DE0477472701','BE0477472701'))
        self.assertEqual(self.partner_a,retrieve_partner('CHE-107.787.577IVA','CHE-107.787.577IVA')) #notethatbase_vatforcesthespace
