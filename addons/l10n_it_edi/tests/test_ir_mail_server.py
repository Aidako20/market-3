#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
importlogging
fromcollectionsimportnamedtuple
fromunittest.mockimportpatch
fromfreezegunimportfreeze_time

fromflectraimporttools
fromflectra.testsimporttagged
fromflectra.addons.account_edi.tests.commonimportAccountEdiTestCommon
fromflectra.addons.l10n_it_edi.tools.remove_signatureimportremove_signature

_logger=logging.getLogger(__name__)

@tagged('post_install_l10n','post_install','-at_install')
classPecMailServerTests(AccountEdiTestCommon):
    """Maintestclassforthel10n_it_edivendorbillsXMLimportfromaPECmailaccount"""

    fake_test_content="""<?xmlversion="1.0"encoding="UTF-8"?>
        <p:FatturaElettronicaversione="FPR12"xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
        xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd">
          <FatturaElettronicaHeader>
            <CessionarioCommittente>
              <DatiAnagrafici>
                <CodiceFiscale>01234560157</CodiceFiscale>
              </DatiAnagrafici>
            </CessionarioCommittente>
          </FatturaElettronicaHeader>
          <FatturaElettronicaBody>
            <DatiGenerali>
              <DatiGeneraliDocumento>
                <TipoDocumento>TD02</TipoDocumento>
              </DatiGeneraliDocumento>
            </DatiGenerali>
          </FatturaElettronicaBody>
        </p:FatturaElettronica>"""

    @classmethod
    defsetUpClass(cls):
        """SetupthetestclasswithaPECmailserverandafakefatturaPAcontent"""

        super().setUpClass(chart_template_ref='l10n_it.l10n_it_chart_template_generic',
                           edi_format_ref='l10n_it_edi.edi_fatturaPA')

        #Usethecompany_data_2totestthatthee-invoiceisimportedfortherightcompany
        cls.company=cls.company_data_2['company']

        #Initializethecompany'scodicefiscale
        cls.company.l10n_it_codice_fiscale='01234560157'

        #Buildtestdata.
        #invoice_filename1isusedforvendorbillreceiptstests
        #invoice_filename2isusedforvendorbilltests
        cls.invoice_filename1='IT01234567890_FPR01.xml'
        cls.invoice_filename2='IT01234567890_FPR02.xml'
        cls.signed_invoice_filename='IT01234567890_FPR01.xml.p7m'
        cls.invoice_content=cls._get_test_file_content(cls.invoice_filename1)
        cls.signed_invoice_content=cls._get_test_file_content(cls.signed_invoice_filename)
        cls.invoice=cls.env['account.move'].create({
            'move_type':'in_invoice',
            'ref':'01234567890'
        })
        cls.attachment=cls.env['ir.attachment'].create({
            'name':cls.invoice_filename1,
            'raw':cls.invoice_content,
            'res_id':cls.invoice.id,
            'res_model':'account.move',
        })
        cls.edi_document=cls.env['account.edi.document'].create({
            'edi_format_id':cls.edi_format.id,
            'move_id':cls.invoice.id,
            'attachment_id':cls.attachment.id,
            'state':'sent'
        })

        #Initializethefetchmailserverthathastobetested
        cls.server=cls.env['fetchmail.server'].sudo().create({
            'name':'test_server',
            'server_type':'imap',
            'l10n_it_is_pec':True})

        cls.test_invoice_xmls={k:cls._get_test_file_content(v)fork,vin[
            ('normal_1','IT01234567890_FPR01.xml'),
            ('signed','IT01234567890_FPR01.xml.p7m'),
        ]}

    @classmethod
    def_get_test_file_content(cls,filename):
        """Getthecontentofatestfileinsidethismodule"""
        path='l10n_it_edi/tests/expected_xmls/'+filename
        withtools.file_open(path,mode='rb')astest_file:
            returntest_file.read()

    def_create_invoice(self,content,filename):
        """Createaninvoicefromgivenattachmentcontent"""
        withpatch.object(self.server._cr,'commit',return_value=None):
            iffilename.endswith(".p7m"):
                content=remove_signature(content)
            returnself.server._create_invoice_from_mail(content,filename,'fake@address.be')

    #-----------------------------
    #
    #Vendorbills
    #
    #-----------------------------

    deftest_receive_vendor_bill(self):
        """Testasamplee-invoicefilefromhttps://www.fatturapa.gov.it/export/documenti/fatturapa/v1.2/IT01234567890_FPR01.xml"""
        invoices=self._create_invoice(self.invoice_content,self.invoice_filename2)
        self.assertTrue(bool(invoices))

    deftest_receive_signed_vendor_bill(self):
        """Testasigned(P7M)samplee-invoicefilefromhttps://www.fatturapa.gov.it/export/documenti/fatturapa/v1.2/IT01234567890_FPR01.xml"""
        withfreeze_time('2020-04-06'):
            invoices=self._create_invoice(self.signed_invoice_content,self.signed_invoice_filename)
            self.assertRecordValues(invoices,[{
                'company_id':self.company.id,
                'name':'BILL/2014/12/0001',
                'invoice_date':datetime.date(2014,12,18),
                'ref':'01234567890',
            }])

    deftest_receive_same_vendor_bill_twice(self):
        """TestthatthesecondtimewearereceivingaPECmailwiththesameattachment,thesecondisdiscarded"""
        content=self.fake_test_content.encode()
        forresultin[True,False]:
            invoice=self._create_invoice(content,self.invoice_filename2)
            self.assertEqual(result,bool(invoice))

    #-----------------------------
    #
    #Receipts
    #
    #-----------------------------

    def_test_receipt(self,receipt_type,source_state,destination_state):
        """Testareceiptfromtheonesinthemodule'stestfiles"""

        #Simulatethe'sent'stateofthemove,evenifwedidn'tactuallysendanemailinthistest
        self.invoice.l10n_it_send_state=source_state

        #Createafakereceiptfromthetestfile
        receipt_filename='IT01234567890_FPR01_%s_001.xml'%receipt_type
        receipt_content=self._get_test_file_content(receipt_filename).decode()

        create_mail_attachment=namedtuple('Attachment',('fname','content','info'))
        receipt_mail_attachment=create_mail_attachment(receipt_filename,receipt_content,{})

        #Simulatethearrivalofthereceipt
        withpatch.object(self.server._cr,'commit',return_value=None):
            self.server._message_receipt_invoice(receipt_type,receipt_mail_attachment)

        #ChecktheDestinationstateoftheedi_document
        self.assertTrue(destination_state,self.edi_document.state)

    deftest_ricevuta_consegna(self):
        """Testareceiptadaptedfromhttps://www.fatturapa.gov.it/export/documenti/messaggi/v1.0/IT01234567890_11111_RC_001.xml"""
        self._test_receipt('RC','sent','delivered')

    deftest_decorrenza_termini(self):
        """Testareceiptadaptedfromhttps://www.fatturapa.gov.it/export/documenti/messaggi/v1.0/IT01234567890_11111_DT_001.xml"""
        self._test_receipt('DT','delivered','delivered_expired')
