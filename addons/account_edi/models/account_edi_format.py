#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api
fromflectra.tools.pdfimportFlectraPdfFileReader,FlectraPdfFileWriter
fromflectra.osvimportexpression
fromflectra.toolsimporthtml_escape
fromflectra.exceptionsimportRedirectWarning
fromPyPDF2.utilsimportPdfReadError

fromlxmlimportetree
fromstructimporterrorasStructError
importbase64
importio
importlogging
importpathlib
importre


_logger=logging.getLogger(__name__)


classAccountEdiFormat(models.Model):
    _name='account.edi.format'
    _description='EDIformat'

    name=fields.Char()
    code=fields.Char(required=True)

    _sql_constraints=[
        ('unique_code','unique(code)','Thiscodealreadyexists')
    ]


    ####################################################
    #Low-levelmethods
    ####################################################

    @api.model_create_multi
    defcreate(self,vals_list):
        edi_formats=super().create(vals_list)

        #activatebydefaultonjournal
        journals=self.env['account.journal'].search([])
        forjournalinjournals:
            foredi_formatinedi_formats:
                ifedi_format._is_compatible_with_journal(journal):
                    journal.edi_format_ids+=edi_format

        #activatecron
        ifany(edi_format._needs_web_services()foredi_formatinedi_formats):
            self.env.ref('account_edi.ir_cron_edi_network').active=True

        returnedi_formats

    ####################################################
    #ExportmethodtooverridebasedonEDIFormat
    ####################################################

    def_get_invoice_edi_content(self,move):
        '''Createabytesliteralofthefilecontentrepresentingtheinvoice-tobeoverriddenbytheEDIFormat
        :returns:      bytesliteralofthecontentgenerated(typicallyXML).
        '''
        returnb''

    def_get_payment_edi_content(self,move):
        '''Createabytesliteralofthefilecontentrepresentingthepayment-tobeoverriddenbytheEDIFormat
        :returns:      bytesliteralofthecontentgenerated(typicallyXML).
        '''
        returnb''

    def_is_required_for_invoice(self,invoice):
        """IndicateifthisEDImustbegeneratedfortheinvoicepassedasparameter.

        :paraminvoice:Anaccount.movehavingtheinvoicetype.
        :returns:      TrueiftheEDImustbegenerated,Falseotherwise.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnTrue

    def_is_required_for_payment(self,payment):
        """IndicateifthisEDImustbegeneratedforthepaymentpassedasparameter.

        :parampayment:Anaccount.movelinkedtoeitheranaccount.payment,eitheranaccount.bank.statement.line.
        :returns:      TrueiftheEDImustbegenerated,Falseotherwise.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnFalse

    def_needs_web_services(self):
        """IndicateiftheEDImustbegeneratedasynchronouslythroughtosomewebservices.

        :return:Trueifsuchawebserviceisavailable,Falseotherwise.
        """
        self.ensure_one()
        returnFalse

    def_is_compatible_with_journal(self,journal):
        """IndicateiftheEDIformatshouldappearonthejournalpassedasparametertobeselectedbytheuser.
        IfTrue,thisEDIformatwillbeselectedbydefaultonthejournal.

        :paramjournal:Thejournal.
        :returns:      Trueifthisformatcanbeenabledbydefaultonthejournal,Falseotherwise.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnjournal.type=='sale'

    def_is_enabled_by_default_on_journal(self,journal):
        """IndicateiftheEDIformatshouldbeselectedbydefaultonthejournalpassedasparameter.
        IfTrue,thisEDIformatwillbeselectedbydefaultonthejournal.

        :paramjournal:Thejournal.
        :returns:Trueifthisformatshouldbeenabledbydefaultonthejournal,Falseotherwise.
        """
        returnTrue

    def_is_embedding_to_invoice_pdf_needed(self):
        """IndicateiftheEDImustbeembeddedinsidethePDFreport.

        :returns:Trueifthedocumentsneedtobeembedded,Falseotherwise.
        """
        #TOOVERRIDE
        returnFalse

    def_get_embedding_to_invoice_pdf_values(self,invoice):
        """Getthevaluestoembedtopdf.

        :returns:  Adictionary{'name':name,'datas':datas}orFalseiftherearenovaluestoembed.
        *name:    Thenameofthefile.
        *datas:   Thebytesotthefile.
        Toremoveinmaster
        """
        self.ensure_one()
        attachment=invoice._get_edi_attachment(self)
        ifnotattachmentornotself._is_embedding_to_invoice_pdf_needed():
            returnFalse
        datas=base64.b64decode(attachment.with_context(bin_size=False).datas)
        return{'name':attachment.name,'datas':datas}

    def_support_batching(self,move=None,state=None,company=None):
        """Indicateifwecansendmultipledocumentsinthesametimetothewebservices.
        IfTrue,the_post_%s_edimethodswillgetmultipledocumentsinthesametime.
        Otherwise,thesemethodswillbecalledwithonlyonerecordatatime.

        :returns:Trueifbatchingissupported,Falseotherwise.
        """
        #TOOVERRIDE
        returnFalse

    def_get_batch_key(self,move,state):
        """Returnsatuplethatwillbeusedaskeytopartitionnatetheinvoices/paymentswhencreatingbatches
        withmultipleinvoices/payments.
        Thetypeofmove(invoiceorpayment),itscompany_id,itsedistateandtheedi_formatareusedbydefault,if
        nofurtherpartitionisneededforthisformat,thismethodshouldreturn().

        :returns:Thekeytobeusedwhenpartitionningthebatches.
        """
        move.ensure_one()
        return()

    def_check_move_configuration(self,move):
        """Checksthemoveandrelevantrecordsforpotentialerror(missingdata,etc).

        :paraminvoice:Themovetocheck.
        :returns:      Alistoferrormessages.
        """
        #TOOVERRIDE
        return[]

    def_post_invoice_edi(self,invoices,test_mode=False):
        """Createthefilecontentrepresentingtheinvoice(andcallswebservicesifnecessary).

        :paraminvoices:   Alistofinvoicestopost.
        :paramtest_mode:  AflagindicatingtheEDIshouldonlysimulatetheEDIwithoutsendingdata.
        :returns:          Adictionarywiththeinvoiceaskeyandasvalue,anotherdictionary:
        *attachment:      Theattachmentrepresentingtheinvoiceinthisedi_formatiftheediwassuccessfullyposted.
        *error:           Anerroriftheediwasnotsuccessfullyposted.
        *blocking_level:   (optional,requiresaccount_edi_extended)Howbadistheerror(howshouldtheediflowbeblocked?)
        """
        #TOOVERRIDE
        self.ensure_one()
        return{}

    def_cancel_invoice_edi(self,invoices,test_mode=False):
        """Callsthewebservicestocanceltheinvoiceofthisdocument.

        :paraminvoices:   Alistofinvoicestocancel.
        :paramtest_mode:  AflagindicatingtheEDIshouldonlysimulatetheEDIwithoutsendingdata.
        :returns:          Adictionarywiththeinvoiceaskeyandasvalue,anotherdictionary:
        *success:         Trueiftheinvoicewassuccessfullycancelled.
        *error:           Anerroriftheediwasnotsuccessfullycancelled.
        *blocking_level:   (optional,requiresaccount_edi_extended)Howbadistheerror(howshouldtheediflowbeblocked?)
        """
        #TOOVERRIDE
        self.ensure_one()
        return{invoice:{'success':True}forinvoiceininvoices} #Bydefault,cancelsucceedsdoingnothing.

    def_post_payment_edi(self,payments,test_mode=False):
        """Createthefilecontentrepresentingthepayment(andcallswebservicesifnecessary).

        :parampayments:  Thepaymentstopost.
        :paramtest_mode:  AflagindicatingtheEDIshouldonlysimulatetheEDIwithoutsendingdata.
        :returns:          Adictionarywiththepaymentaskeyandasvalue,anotherdictionary:
        *attachment:      Theattachmentrepresentingthepaymentinthisedi_formatiftheediwassuccessfullyposted.
        *error:           Anerroriftheediwasnotsuccessfullyposted.
        *blocking_level:   (optional,requiresaccount_edi_extended)Howbadistheerror(howshouldtheediflowbeblocked?)
        """
        #TOOVERRIDE
        self.ensure_one()
        return{}

    def_cancel_payment_edi(self,payments,test_mode=False):
        """Callsthewebservicestocancelthepaymentofthisdocument.

        :parampayments: Alistofpaymentstocancel.
        :paramtest_mode:AflagindicatingtheEDIshouldonlysimulatetheEDIwithoutsendingdata.
        :returns:        Adictionarywiththepaymentaskeyandasvalue,anotherdictionary:
        *success:       Trueifthepaymentwassuccessfullycancelled.
        *error:         Anerroriftheediwasnotsuccessfullycancelled.
        *blocking_level: (optional,requiresaccount_edi_extended)Howbadistheerror(howshouldtheediflowbeblocked?)
        """
        #TOOVERRIDE
        self.ensure_one()
        return{payment:{'success':True}forpaymentinpayments} #Bydefault,cancelsucceedsdoingnothing.

    ####################################################
    #ImportmethodstooverridebasedonEDIFormat
    ####################################################

    def_create_invoice_from_xml_tree(self,filename,tree,journal=None):
        """Createanewinvoicewiththedatainsidethexml.

        :paramfilename:Thenameofthexml.
        :paramtree:    Thetreeofthexmltoimport.
        :paramjournal: Thejournalonwhichimportingtheinvoice.
        :returns:       Thecreatedinvoice.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnself.env['account.move']

    def_update_invoice_from_xml_tree(self,filename,tree,invoice):
        """Updateanexistinginvoicewiththedatainsidethexml.

        :paramfilename:Thenameofthexml.
        :paramtree:    Thetreeofthexmltoimport.
        :paraminvoice: Theinvoicetoupdate.
        :returns:       Theupdatedinvoice.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnself.env['account.move']

    def_create_invoice_from_pdf_reader(self,filename,reader):
        """Createanewinvoicewiththedatainsideapdf.

        :paramfilename:Thenameofthepdf.
        :paramreader:  TheFlectraPdfFileReaderofthepdftoimport.
        :returns:       Thecreatedinvoice.
        """
        #TOOVERRIDE
        self.ensure_one()

        returnself.env['account.move']

    def_update_invoice_from_pdf_reader(self,filename,reader,invoice):
        """Updateanexistinginvoicewiththedatainsidethepdf.

        :paramfilename:Thenameofthepdf.
        :paramreader:  TheFlectraPdfFileReaderofthepdftoimport.
        :paraminvoice: Theinvoicetoupdate.
        :returns:       Theupdatedinvoice.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnself.env['account.move']

    def_create_invoice_from_binary(self,filename,content,extension):
        """Createanewinvoicewiththedatainsideabinaryfile.

        :paramfilename: Thenameofthefile.
        :paramcontent:  Thecontentofthebinaryfile.
        :paramextension:Theextensionsasastring.
        :returns:        Thecreatedinvoice.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnself.env['account.move']

    def_update_invoice_from_binary(self,filename,content,extension,invoice):
        """Updateanexistinginvoicewiththedatainsideabinaryfile.

        :paramfilename:Thenameofthefile.
        :paramcontent: Thecontentofthebinaryfile.
        :paramextension:Theextensionsasastring.
        :paraminvoice: Theinvoicetoupdate.
        :returns:       Theupdatedinvoice.
        """
        #TOOVERRIDE
        self.ensure_one()
        returnself.env['account.move']

    def_prepare_invoice_report(self,pdf_writer,edi_document):
        """
        Prepareinvoicereporttobeprinted.
        :parampdf_writer:Thepdfwriterwiththeinvoicepdfcontentloaded.
        :paramedi_document:Theedidocumenttobeaddedtothepdffile.
        """
        #TOOVERRIDE
        self.ensure_one()
        ifself._is_embedding_to_invoice_pdf_needed()andedi_document.attachment_id:
            pdf_writer.embed_flectra_attachment(edi_document.attachment_id)

    ####################################################
    #ExportInternalmethods(notmeanttobeoverridden)
    ####################################################

    def_embed_edis_to_pdf(self,pdf_content,invoice):
        """CreatetheEDIdocumentoftheinvoiceandembeditinthepdf_content.

        :parampdf_content:thebytesrepresentingthepdftoaddtheEDIsto.
        :paraminvoice:theinvoicetogeneratetheEDIfrom.
        :returns:thesamepdf_contentwiththeEDIoftheinvoiceembedinit.
        """
        to_embed=invoice.edi_document_ids
        #Addtheattachmentstothepdffile
        ifto_embed:
            reader_buffer=io.BytesIO(pdf_content)
            reader=FlectraPdfFileReader(reader_buffer,strict=False)
            writer=FlectraPdfFileWriter()
            writer.cloneReaderDocumentRoot(reader)
            foredi_documentinto_embed:
                edi_document.edi_format_id._prepare_invoice_report(writer,edi_document)
            buffer=io.BytesIO()
            writer.write(buffer)
            pdf_content=buffer.getvalue()
            reader_buffer.close()
            buffer.close()
        returnpdf_content

    ####################################################
    #ImportInternalmethods(notmeanttobeoverridden)
    ####################################################

    def_decode_xml(self,filename,content):
        """Decodesanxmlintoalistofonedictionaryrepresentinganattachment.

        :paramfilename:   Thenameofthexml.
        :paramcontent:    Thebytesrepresentingthexml.
        :returns:          Alistwithadictionary.
        *filename:        Thenameoftheattachment.
        *content:         Thecontentoftheattachment.
        *type:            Thetypeoftheattachment.
        *xml_tree:        Thetreeofthexmliftypeisxml.
        """
        to_process=[]
        try:
            xml_tree=etree.fromstring(content)
        exceptExceptionase:
            _logger.exception("Errorwhenconvertingthexmlcontenttoetree:%s"%e)
            returnto_process
        iflen(xml_tree):
            to_process.append({
                'filename':filename,
                'content':content,
                'type':'xml',
                'xml_tree':xml_tree,
            })
        returnto_process

    def_decode_pdf(self,filename,content):
        """Decodesapdfandunwrapsub-attachmentintoalistofdictionaryeachrepresentinganattachment.

        :paramfilename:   Thenameofthepdf.
        :paramcontent:    Thebytesrepresentingthepdf.
        :returns:          Alistofdictionaryforeachattachment.
        *filename:        Thenameoftheattachment.
        *content:         Thecontentoftheattachment.
        *type:            Thetypeoftheattachment.
        *xml_tree:        Thetreeofthexmliftypeisxml.
        *pdf_reader:      Thepdf_readeriftypeispdf.
        """
        to_process=[]
        try:
            buffer=io.BytesIO(content)
            pdf_reader=FlectraPdfFileReader(buffer,strict=False)
        exceptExceptionase:
            #Malformedpdf
            _logger.exception("Errorwhenreadingthepdf:%s"%e)
            returnto_process

        #Processembeddedfiles.
        try:
            forxml_name,contentinpdf_reader.getAttachments():
                to_process.extend(self._decode_xml(xml_name,content))
        except(NotImplementedError,StructError,PdfReadError)ase:
            _logger.warning("Unabletoaccesstheattachmentsof%s.Triedtodecryptit,but%s."%(filename,e))

        #Processthepdfitself.
        to_process.append({
            'filename':filename,
            'content':content,
            'type':'pdf',
            'pdf_reader':pdf_reader,
        })

        returnto_process

    def_decode_binary(self,filename,content):
        """Decodesanyfileintoalistofonedictionaryrepresentinganattachment.
        Thisisafallbackforallfilesthatarenotdecodedbyothermethods.

        :paramfilename:   Thenameofthefile.
        :paramcontent:    Thebytesrepresentingthefile.
        :returns:          Alistwithadictionary.
        *filename:        Thenameoftheattachment.
        *content:         Thecontentoftheattachment.
        *type:            Thetypeoftheattachment.
        """
        return[{
            'filename':filename,
            'extension':''.join(pathlib.Path(filename).suffixes),
            'content':content,
            'type':'binary',
        }]

    def_decode_attachment(self,attachment):
        """Decodesanir.attachmentandunwrapsub-attachmentintoalistofdictionaryeachrepresentinganattachment.

        :paramattachment: Anir.attachmentrecord.
        :returns:          Alistofdictionaryforeachattachment.
        *filename:        Thenameoftheattachment.
        *content:         Thecontentoftheattachment.
        *type:            Thetypeoftheattachment.
        *xml_tree:        Thetreeofthexmliftypeisxml.
        *pdf_reader:      Thepdf_readeriftypeispdf.
        """
        content=base64.b64decode(attachment.with_context(bin_size=False).datas)
        to_process=[]

        #XMLattachmentsreceivedbymailhavea'text/plain'mimetype(cfr.contextkey:'attachments_mime_plainxml')
        #Therefore,ifcontentstartwith'<?xml',orifthefilenameendswith'.xml',itisconsideredasXML.
        is_text_plain_xml='text/plain'inattachment.mimetypeand(content.startswith(b'<?xml')orattachment.name.endswith('.xml'))
        if'pdf'inattachment.mimetype:
            to_process.extend(self._decode_pdf(attachment.name,content))
        elifattachment.mimetype.endswith('/xml')oris_text_plain_xml:
            to_process.extend(self._decode_xml(attachment.name,content))
        else:
            to_process.extend(self._decode_binary(attachment.name,content))

        returnto_process

    def_create_invoice_from_attachment(self,attachment):
        """Decodesanir.attachmenttocreateaninvoice.

        :paramattachment: Anir.attachmentrecord.
        :returns:          Theinvoicewheretoimportdata.
        """
        forfile_datainself._decode_attachment(attachment):
            foredi_formatinself:
                res=False
                try:
                    iffile_data['type']=='xml':
                        res=edi_format._create_invoice_from_xml_tree(file_data['filename'],file_data['xml_tree'])
                    eliffile_data['type']=='pdf':
                        res=edi_format._create_invoice_from_pdf_reader(file_data['filename'],file_data['pdf_reader'])
                        file_data['pdf_reader'].stream.close()
                    else:
                        res=edi_format._create_invoice_from_binary(file_data['filename'],file_data['content'],file_data['extension'])
                exceptRedirectWarningasrw:
                    raiserw
                exceptExceptionase:
                    _logger.exception("Errorimportingattachment\"%s\"asinvoicewithformat\"%s\"",file_data['filename'],edi_format.name,exc_info=True)
                ifres:
                    if'extract_state'inres:
                        #BypasstheOCRtopreventoverwritingdatawhenanEDIwassuccesfullyimported.
                        #TODO:removewhenweintegratetheOCRtotheEDIflow.
                        res.write({'extract_state':'done'})
                    returnres
        returnself.env['account.move']

    def_update_invoice_from_attachment(self,attachment,invoice):
        """Decodesanir.attachmenttoupdateaninvoice.

        :paramattachment: Anir.attachmentrecord.
        :returns:          Theinvoicewheretoimportdata.
        """
        forfile_datainself._decode_attachment(attachment):
            foredi_formatinself:
                res=False
                try:
                    iffile_data['type']=='xml':
                        res=edi_format._update_invoice_from_xml_tree(file_data['filename'],file_data['xml_tree'],invoice)
                    eliffile_data['type']=='pdf':
                        res=edi_format._update_invoice_from_pdf_reader(file_data['filename'],file_data['pdf_reader'],invoice)
                        file_data['pdf_reader'].stream.close()
                    else: #file_data['type']=='binary'
                        res=edi_format._update_invoice_from_binary(file_data['filename'],file_data['content'],file_data['extension'],invoice)
                exceptExceptionase:
                    _logger.exception("Errorimportingattachment\"%s\"asinvoicewithformat\"%s\"",file_data['filename'],edi_format.name,exc_info=True)
                ifres:
                    if'extract_state'inres:
                        #BypasstheOCRtopreventoverwritingdatawhenanEDIwassuccesfullyimported.
                        #TODO:removewhenweintegratetheOCRtotheEDIflow.
                        res.write({'extract_state':'done'})
                    returnres
        returnself.env['account.move']

    ####################################################
    #Importhelpers
    ####################################################

    def_find_value(self,xpath,xml_element,namespaces=None):
        element=xml_element.xpath(xpath,namespaces=namespaces)
        returnelement[0].textifelementelseNone

    @api.model
    def_retrieve_partner_with_vat(self,vat,extra_domain):
        ifnotvat:
            returnNone

        #Sometimes,thevatisspecifiedwithsomewhitespaces.
        normalized_vat=vat.replace('','')
        country_prefix=re.match('^[a-zA-Z]{2}|^',vat).group()

        partner=self.env['res.partner'].search(extra_domain+[('vat','in',(normalized_vat,vat))],limit=1)

        #Trytoremovethecountrycodeprefixfromthevat.
        ifnotpartnerandcountry_prefix:
            partner=self.env['res.partner'].search(extra_domain+[
                ('vat','in',(normalized_vat[2:],vat[2:])),
                ('country_id.code','=',country_prefix.upper()),
            ],limit=1)

            #Thecountrycouldbenotspecifiedonthepartner.
            ifnotpartner:
                partner=self.env['res.partner'].search(extra_domain+[
                    ('vat','in',(normalized_vat[2:],vat[2:])),
                    ('country_id','=',False),
                ],limit=1)

            #Thevatcouldbeastringofalphanumericvalueswithoutcountrycodebutwithmissingzerosatthe
            #beginning.
        ifnotpartner:
            try:
                vat_only_numeric=str(int(re.sub(r'^\D{2}','',normalized_vat)or0))
            exceptValueError:
                vat_only_numeric=None

            ifvat_only_numeric:
                query=self.env['res.partner']._where_calc(extra_domain+[('active','=',True)])
                tables,where_clause,where_params=query.get_sql()

                ifcountry_prefix:
                    vat_prefix_regex=f'({country_prefix})?'
                else:
                    vat_prefix_regex='([A-z]{2})?'

                self._cr.execute(f'''
                    SELECTres_partner.id
                    FROM{tables}
                    WHERE{where_clause}
                    ANDres_partner.vat~%s
                    LIMIT1
                ''',where_params+['^%s0*%s$'%(vat_prefix_regex,vat_only_numeric)])
                partner_row=self._cr.fetchone()
                ifpartner_row:
                    partner=self.env['res.partner'].browse(partner_row[0])

        returnpartner

    @api.model
    def_retrieve_partner_with_phone_mail(self,phone,mail,extra_domain):
        domains=[]
        ifphone:
            domains.append([('phone','=',phone)])
            domains.append([('mobile','=',phone)])
        ifmail:
            domains.append([('email','=',mail)])

        ifnotdomains:
            returnNone

        domain=expression.OR(domains)
        ifextra_domain:
            domain=expression.AND([domain,extra_domain])
        returnself.env['res.partner'].search(domain,limit=1)

    @api.model
    def_retrieve_partner_with_name(self,name,extra_domain):
        ifnotname:
            returnNone
        returnself.env['res.partner'].search([('name','ilike',name)]+extra_domain,limit=1)

    def_retrieve_partner(self,name=None,phone=None,mail=None,vat=None,domain=None):
        '''Searchallpartnersandfindonethatmatchesoneoftheparameters.
        :paramname:   Thenameofthepartner.
        :paramphone:  Thephoneormobileofthepartner.
        :parammail:   Themailofthepartner.
        :paramvat:    Thevatnumberofthepartner.
        :returns:      Apartneroranemptyrecordsetifnotfound.
        '''

        defsearch_with_vat(extra_domain):
            returnself._retrieve_partner_with_vat(vat,extra_domain)

        defsearch_with_phone_mail(extra_domain):
            returnself._retrieve_partner_with_phone_mail(phone,mail,extra_domain)

        defsearch_with_name(extra_domain):
            returnself._retrieve_partner_with_name(name,extra_domain)

        forsearch_methodin(search_with_vat,search_with_phone_mail,search_with_name):
            forextra_domainin([('company_id','=',self.env.company.id)],[]):
                partner=search_method(extra_domain)
                ifpartner:
                    returnpartner
        returnself.env['res.partner']

    def_retrieve_product(self,name=None,default_code=None,barcode=None):
        '''Searchallproductsandfindonethatmatchesoneoftheparameters.

        :paramname:           Thenameoftheproduct.
        :paramdefault_code:   Thedefault_codeoftheproduct.
        :parambarcode:        Thebarcodeoftheproduct.
        :returns:              Aproductoranemptyrecordsetifnotfound.
        '''
        ifnameand'\n'inname:
            #cutSalesDescriptionfromthename
            name=name.split('\n')[0]
        domains=[]
        ifdefault_code:
            domains.append([('default_code','=',default_code)])
        ifbarcode:
            domains.append([('barcode','=',barcode)])

        #Searchfortheproductwiththeexactname,thenilikethename
        name_domains=[('name','=',name)],[('name','ilike',name)]ifnameelse[]
        forname_domaininname_domains:
            product=self.env['product.product'].search(
                expression.AND([
                    expression.OR(domains+[name_domain]),
                    [('company_id','in',[False,self.env.company.id])],
                ]),
                limit=1,
            )
            ifproduct:
                returnproduct
        returnself.env['product.product']

    def_retrieve_tax(self,amount,type_tax_use):
        '''Searchalltaxesandfindonethatmatchesalloftheparameters.

        :paramamount:         Theamountofthetax.
        :paramtype_tax_use:   Thetypeofthetax.
        :returns:              Ataxoranemptyrecordsetifnotfound.
        '''
        returnself.env['account.tax'].search([
            ('amount','=',float(amount)),
            ('type_tax_use','=',type_tax_use),
            ('company_id','=',self.env.company.id),
        ],limit=1)

    def_retrieve_currency(self,code):
        '''Searchallcurrenciesandfindonethatmatchesthecode.

        :paramcode:Thecodeofthecurrency.
        :returns:   Acurrencyoranemptyrecordsetifnotfound.
        '''
        returnself.env['res.currency'].search([('name','=',code.upper())],limit=1)

    ####################################################
    #Otherhelpers
    ####################################################

    @api.model
    def_format_error_message(self,error_title,errors):
        bullet_list_msg=''.join('<li>%s</li>'%html_escape(msg)formsginerrors)
        return'%s<ul>%s</ul>'%(error_title,bullet_list_msg)

    def_is_account_edi_ubl_cii_available(self):
        returnhasattr(self,'_infer_xml_builder_from_tree')
