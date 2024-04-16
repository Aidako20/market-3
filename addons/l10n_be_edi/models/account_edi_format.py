#-*-coding:utf-8-*-

fromflectraimportmodels

importbase64


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    def_is_efff(self,filename,tree):
        returnself.code=='efff_1'andtree.tag=='{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice'

    def_create_invoice_from_xml_tree(self,filename,tree,journal=None):
        self.ensure_one()
        ifself._is_efff(filename,tree)andnotself._is_account_edi_ubl_cii_available():
            returnself._create_invoice_from_ubl(tree)
        returnsuper()._create_invoice_from_xml_tree(filename,tree,journal=journal)

    def_update_invoice_from_xml_tree(self,filename,tree,invoice):
        self.ensure_one()
        ifself._is_efff(filename,tree)andnotself._is_account_edi_ubl_cii_available():
            returnself._update_invoice_from_ubl(tree,invoice)
        returnsuper()._update_invoice_from_xml_tree(filename,tree,invoice)

    def_is_compatible_with_journal(self,journal):
        self.ensure_one()
        ifself.code!='efff_1'orself._is_account_edi_ubl_cii_available():
            returnsuper()._is_compatible_with_journal(journal)
        returnjournal.type=='sale'andjournal.country_code=='BE'

    def_post_invoice_edi(self,invoices,test_mode=False):
        self.ensure_one()
        ifself.code!='efff_1'orself._is_account_edi_ubl_cii_available():
            returnsuper()._post_invoice_edi(invoices,test_mode=test_mode)
        res={}
        forinvoiceininvoices:
            attachment=self._export_efff(invoice)
            res[invoice]={'attachment':attachment}
        returnres

    def_export_efff(self,invoice):
        self.ensure_one()
        #Createfilecontent.
        xml_content=b"<?xmlversion='1.0'encoding='UTF-8'?>"
        xml_content+=self.env.ref('account_edi_ubl.export_ubl_invoice')._render(invoice._get_ubl_values())
        xml_name='%s.xml'%invoice._get_efff_name()
        returnself.env['ir.attachment'].create({
            'name':xml_name,
            'datas':base64.encodebytes(xml_content),
            'mimetype':'application/xml',
        })
