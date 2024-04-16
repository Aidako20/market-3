#-*-coding:utf-8-*-

fromflectra.tests.commonimportTransactionCase,tagged
fromunittestimportskipIf
importos

directory=os.path.dirname(__file__)

try:
    frompdfminer.pdfinterpimportPDFResourceManager
exceptImportError:
    PDFResourceManager=None


@tagged('post_install','-at_install')
classTestCaseIndexation(TransactionCase):

    @skipIf(PDFResourceManagerisNone,"pdfminernotinstalled")
    deftest_attachment_pdf_indexation(self):
        withopen(os.path.join(directory,'files','test_content.pdf'),'rb')asfile:
            pdf=file.read()
            text=self.env['ir.attachment']._index(pdf,'application/pdf')
            self.assertEqual(text,'TestContent!!\x0c','theindexcontentshouldbecorrect')
