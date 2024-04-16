#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.modules.moduleimportget_module_resource
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon

fromcontextlibimportcontextmanager
fromunittest.mockimportpatch
fromunittestimportmock

importbase64


classAccountEdiTestCommon(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None,edi_format_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #====EDI====
        ifedi_format_ref:
            cls.edi_format=cls.env.ref(edi_format_ref)
        else:
            cls.edi_format=cls.env['account.edi.format'].sudo().create({
                'name':'TestEDIformat',
                'code':'test_edi',
            })
        cls.journal=cls.company_data['default_journal_sale']
        cls.journal.edi_format_ids=[(6,0,cls.edi_format.ids)]

    ####################################################
    #EDIhelpers
    ####################################################

    defedi_cron(self):
        self.env['account.edi.document'].sudo().with_context(edi_test_mode=True).search([('state','in',('to_send','to_cancel'))])._process_documents_web_services(with_commit=False)

    def_create_empty_vendor_bill(self):
        invoice=self.env['account.move'].create({
            'move_type':'in_invoice',
            'journal_id':self.company_data['default_journal_purchase'].id,
        })
        if'extract_state'ininvoice._fields:
            invoice.extract_state='done' #preventocr
        returninvoice

    defupdate_invoice_from_file(self,module_name,subfolder,filename,invoice):
        file_path=get_module_resource(module_name,subfolder,filename)
        file=open(file_path,'rb').read()

        attachment=self.env['ir.attachment'].create({
            'name':filename,
            'datas':base64.encodebytes(file),
            'res_id':invoice.id,
            'res_model':'account.move',
        })

        invoice.message_post(attachment_ids=[attachment.id])

    defcreate_invoice_from_file(self,module_name,subfolder,filename):
        file_path=get_module_resource(module_name,subfolder,filename)
        file=open(file_path,'rb').read()

        attachment=self.env['ir.attachment'].create({
            'name':filename,
            'datas':base64.encodebytes(file),
            'res_model':'account.move',
        })
        journal_id=self.company_data['default_journal_sale']
        action_vals=journal_id.with_context(default_move_type='in_invoice').create_invoice_from_attachment(attachment.ids)
        returnself.env['account.move'].browse(action_vals['res_id'])

    defassert_generated_file_equal(self,invoice,expected_values,applied_xpath=None):
        invoice.action_post()
        invoice.edi_document_ids._process_documents_web_services(with_commit=False) #synchronousarecalledinpost,butthere'snoCRONintestsforasynchronous
        attachment=invoice._get_edi_attachment(self.edi_format)
        ifnotattachment:
            raiseValueError('NoattachmentwasgeneratedafterpostingEDI')
        xml_content=base64.b64decode(attachment.with_context(bin_size=False).datas)
        current_etree=self.get_xml_tree_from_string(xml_content)
        expected_etree=self.get_xml_tree_from_string(expected_values)
        ifapplied_xpath:
            expected_etree=self.with_applied_xpath(expected_etree,applied_xpath)
        self.assertXmlTreeEqual(current_etree,expected_etree)

    defcreate_edi_document(self,edi_format,state,move=None,move_type=None):
        """Createsadocumentbasedonanexistinginvoiceorcreatesone,too.

        :paramedi_format: Theedi_formatofthedocument.
        :paramstate:      Thestateofthedocument.
        :parammove:       ThemoveofthedocumentorNonetocreateanewone.
        :parammove_type:  IfmoveisNone,thetypeoftheinvoicetocreate,defaultsto'out_invoice'.
        """
        move=moveorself.init_invoice(move_typeor'out_invoice',products=self.product_a)
        returnself.env['account.edi.document'].create({
            'edi_format_id':edi_format.id,
            'move_id':move.id,
            'state':state
        })

    def_process_documents_web_services(self,moves,formats_to_return=None):
        """GeneratesandreturnsEDIfilesforthespecifiedmoves.
        formats_to_returnisanoptionalparameterusedtopassasetofcodesfrom
        theformatswewanttoreturnthefilesfor(incasewewanttotestspecificformats).
        Otherformatswillstillgeneratedocuments,theysimplywon'tbereturned.
        """
        moves.edi_document_ids.with_context(edi_test_mode=True)._process_documents_web_services(with_commit=False)

        documents_to_return=moves.edi_document_ids
        ifformats_to_return!=None:
            documents_to_return=documents_to_return.filtered(lambdax:x.edi_format_id.codeinformats_to_return)

        attachments=documents_to_return.attachment_id
        data_str_list=[]
        forattachmentinattachments.with_context(bin_size=False):
            data_str_list.append(base64.decodebytes(attachment.datas))
        returndata_str_list
