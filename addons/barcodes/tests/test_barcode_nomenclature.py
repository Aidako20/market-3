#-*-coding:utf-8-*-
fromflectra.testsimportcommon


classTestBarcodeNomenclature(common.TransactionCase):

    deftest_ean8_checksum(self):
        barcode_nomenclature=self.env['barcode.nomenclature']
        ean8="87111125"
        checksum=barcode_nomenclature.ean8_checksum(ean8)
        self.assertEqual(checksum,int(ean8[-1]))
        checksum=barcode_nomenclature.ean8_checksum("8711112")
        self.assertEqual(checksum,-1)
        checksum=barcode_nomenclature.ean8_checksum("871111256")
        self.assertEqual(checksum,-1)
