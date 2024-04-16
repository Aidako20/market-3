#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importzipfile
importio
importre
importlogging
importemail
importemail.policy
importdateutil
importpytz

fromlxmlimportetree
fromdatetimeimportdatetime
fromxmlrpcimportclientasxmlrpclib

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportValidationError,UserError
fromflectra.addons.l10n_it_edi.tools.remove_signatureimportremove_signature


_logger=logging.getLogger(__name__)

classFetchmailServer(models.Model):
    _name='fetchmail.server'
    _inherit='fetchmail.server'

    l10n_it_is_pec=fields.Boolean('PECserver',help="IfPECServer,onlymailfrom'...@pec.fatturapa.it'willbeprocessed.")
    l10n_it_last_uid=fields.Integer(string='LastmessageUID',default=1)

    def_search_edi_invoice(self,att_name,send_state=False):
        """Searchsentl10n_it_edifatturaPAinvoices"""

        conditions=[
            ('move_id',"!=",False),
            ('edi_format_id.code','=','fattura_pa'),
            ('attachment_id.name','=',att_name),
        ]
        ifsend_state:
            conditions.append(('move_id.l10n_it_send_state','=',send_state))

        returnself.env['account.edi.document'].search(conditions,limit=1).move_id

    @api.constrains('l10n_it_is_pec','server_type')
    def_check_pec(self):
        forrecordinself:
            ifrecord.l10n_it_is_pecandrecord.server_type!='imap':
                raiseValidationError(_("PECmailservermustbeoftypeIMAP."))

    deffetch_mail(self):
        """WARNING:meantforcronusageonly-willcommit()aftereachemail!"""

        MailThread=self.env['mail.thread']
        forserverinself.filtered(lambdas:s.l10n_it_is_pec):
            _logger.info('startcheckingfornewemailson%sPECserver%s',server.server_type,server.name)

            count,failed=0,0
            imap_server=None
            try:
                imap_server=server.connect()
                imap_server.select()

                #Onlydownloadnewemails
                email_filter=['(UID%s:*)'%(server.l10n_it_last_uid)]

                #Thel10n_it_edi.fatturapa_bypass_incoming_address_filterpreventsthesenderaddresscheckonincomingemail.
                bypass_incoming_address_filter=self.env['ir.config_parameter'].get_param('l10n_it_edi.bypass_incoming_address_filter',False)
                ifnotbypass_incoming_address_filter:
                    email_filter.append('(FROM"@pec.fatturapa.it")')

                data=imap_server.uid('search',None,*email_filter)[1]

                new_max_uid=server.l10n_it_last_uid
                foruidindata[0].split():
                    ifint(uid)<=server.l10n_it_last_uid:
                        #Wegetalwaysminimum1message. Ifnonewmessage,wereceivethenewestalreadymanaged.
                        continue

                    result,data=imap_server.uid('fetch',uid,'(RFC822)')

                    ifnotdata[0]:
                        continue
                    message=data[0][1]

                    #Toleavethemailinthestateinwhichtheywere.
                    if"Seen"notindata[1].decode("utf-8"):
                        imap_server.uid('STORE',uid,'+FLAGS','(\\Seen)')
                    else:
                        imap_server.uid('STORE',uid,'-FLAGS','(\\Seen)')

                    #Seedetailsinmessage_process()inmail_thread.py
                    ifisinstance(message,xmlrpclib.Binary):
                        message=bytes(message.data)
                    ifisinstance(message,str):
                        message=message.encode('utf-8')
                    msg_txt=email.message_from_bytes(message,policy=email.policy.SMTP)

                    try:
                        self._attachment_invoice(msg_txt)
                        new_max_uid=max(new_max_uid,int(uid))
                    exceptException:
                        _logger.info('Failedtoprocessmailfrom%sserver%s.',server.server_type,server.name,exc_info=True)
                        failed+=1
                    self._cr.commit()
                    count+=1
                server.write({'l10n_it_last_uid':new_max_uid})
                _logger.info("Fetched%demail(s)on%sserver%s;%dsucceeded,%dfailed.",count,server.server_type,server.name,(count-failed),failed)
            exceptException:
                _logger.info("Generalfailurewhentryingtofetchmailfrom%sserver%s.",server.server_type,server.name,exc_info=True)
            finally:
                ifimap_server:
                    imap_server.close()
                    imap_server.logout()
                server.write({'date':fields.Datetime.now()})
        returnsuper(FetchmailServer,self.filtered(lambdas:nots.l10n_it_is_pec)).fetch_mail()

    def_attachment_invoice(self,msg_txt):
        parsed_values=self.env['mail.thread']._message_parse_extract_payload(msg_txt)
        body,attachments=parsed_values['body'],parsed_values['attachments']
        from_address=msg_txt.get('from')
        forattachmentinattachments:
            split_attachment=attachment.fname.rpartition('.')
            iflen(split_attachment)<3:
                _logger.info('E-invoicefilenamenotcompliant:%s',attachment.fname)
                continue
            attachment_name=split_attachment[0]
            attachment_ext=split_attachment[2]
            split_underscore=attachment_name.rsplit('_',2)
            iflen(split_underscore)<2:
                _logger.info('E-invoicefilenamenotcompliant:%s',attachment.fname)
                continue

            ifattachment_ext!='zip':
                ifsplit_underscore[1]in['RC','NS','MC','MT','EC','SE','NE','DT']:
                    #wehaveareceipt
                    self._message_receipt_invoice(split_underscore[1],attachment)
                else:
                    att_filename=attachment.fname
                    match=re.search("[A-Z]{2}[A-Za-z0-9]{2,28}_[A-Za-z0-9]{0,5}.((?i:xml.p7m|xml))",att_filename)
                    #Ifmatch,wehaveaninvoice.
                    ifmatch:
                        #Ifit'ssigned,thecontenthasabytestypeandwejustremovethesignature'senvelope
                        ifmatch.groups()[0].lower()=='xml.p7m':
                            att_content_data=remove_signature(attachment.content)
                            #Iftheenvelopecannotberemoved,theremove_signaturereturnsNone,soweskip
                            ifnotatt_content_data:
                                _logger.warning("E-invoicecouldn'tberead:%s",att_filename)
                                continue
                            att_filename=att_filename.replace('.xml.p7m','.xml')
                        else:
                            #Otherwise,itshouldbeanutf-8encodedXMLstring
                            att_content_data=attachment.content.encode()
                    self._create_invoice_from_mail(att_content_data,att_filename,from_address)
            else:
                ifsplit_underscore[1]=='AT':
                    #Attestazionediavvenutatrasmissionedellafatturaconimpossibilitàdirecapito
                    self._message_AT_invoice(attachment)
                else:
                    _logger.info('NewE-invoiceinzipfile:%s',attachment.fname)
                    self._create_invoice_from_mail_with_zip(attachment,from_address)

    def_create_invoice_from_mail(self,att_content_data,att_name,from_address):
        """Createsaninvoicefromthecontentofanemailpresentinir.attachments

        :paramatt_content_data:  The'utf-8'encodedbytesstringrepresentingthecontentoftheattachment.
        :paramatt_name:          Theattachment'sfilename.
        :paramfrom_address:      Thesenderaddressoftheemail.
        """

        invoices=self.env['account.move']

        #Checkifwealreadyimportedtheemailasanattachment
        existing=self.env['ir.attachment'].search([('name','=',att_name),('res_model','=','account.move')])
        ifexisting:
            _logger.info('E-invoicealreadyexist:%s',att_name)
            returninvoices

        #Createthenewattachmentforthefile
        attachment=self.env['ir.attachment'].create({
            'name':att_name,
            'raw':att_content_data,
            'res_model':'account.move',
            'type':'binary'})

        #Decodethefile.
        try:
            tree=etree.fromstring(att_content_data)
        exceptException:
            _logger.info('Thexmlfileisbadlyformatted:%s',att_name)
            returninvoices

        invoices=self.env.ref('l10n_it_edi.edi_fatturaPA')._create_invoice_from_xml_tree(att_name,tree)
        ifnotinvoices:
            _logger.info('E-invoicenotfoundinfile:%s',att_name)
            returninvoices
        invoices.l10n_it_send_state="new"
        invoices.invoice_source_email=from_address
        forinvoiceininvoices:
            invoice.with_context(no_new_invoice=True,default_res_id=invoice.id)\
                    .message_post(body=(_("OriginalE-invoiceXMLfile")),attachment_ids=[attachment.id])

        self._cr.commit()

        _logger.info('NewE-invoices(%s),ids:%s',att_name,[x.idforxininvoices])
        returninvoices

    def_create_invoice_from_mail_with_zip(self,attachment_zip,from_address):
        withzipfile.ZipFile(io.BytesIO(attachment_zip.content))asz:
            foratt_nameinz.namelist():
                existing=self.env['ir.attachment'].search([('name','=',att_name),('res_model','=','account.move')])
                ifexisting:
                    #invoicealreadyexist
                    _logger.info('E-invoiceinzipfile(%s)alreadyexist:%s',attachment_zip.fname,att_name)
                    continue
                att_content=z.open(att_name).read()

                self._create_invoice_from_mail(att_content,att_name,from_address)

    def_message_AT_invoice(self,attachment_zip):
        withzipfile.ZipFile(io.BytesIO(attachment_zip.content))asz:
            forattachment_nameinz.namelist():
                split_name_attachment=attachment_name.rpartition('.')
                iflen(split_name_attachment)<3:
                    continue
                split_underscore=split_name_attachment[0].rsplit('_',2)
                iflen(split_underscore)<2:
                    continue
                ifsplit_underscore[1]=='AT':
                    attachment=z.open(attachment_name).read()
                    _logger.info('NewATreceiptfor:%s',split_underscore[0])
                    try:
                        tree=etree.fromstring(attachment)
                    except:
                        _logger.info('Errorindecodingnewreceiptfile:%s',attachment_name)
                        return

                    elements=tree.xpath('//NomeFile')
                    ifelementsandelements[0].text:
                        filename=elements[0].text
                    else:
                        return

                    related_invoice=self._search_edi_invoice(filename)
                    ifnotrelated_invoice:
                        _logger.info('Error:invoicenotfoundforreceiptfile:%s',filename)
                        return

                    related_invoice.l10n_it_send_state='failed_delivery'
                    info=self._return_multi_line_xml(tree,['//IdentificativoSdI','//DataOraRicezione','//MessageId','//PecMessageId','//Note'])
                    related_invoice.message_post(
                        body=(_("EScertifythatithasreceivedtheinvoiceandthatthefile\
                        couldnotbedeliveredtotheaddressee.<br/>%s")%(info))
                    )

    def_message_receipt_invoice(self,receipt_type,attachment):

        try:
            tree=etree.fromstring(attachment.content.encode())
        except:
            _logger.info('Errorindecodingnewreceiptfile:%s',attachment.fname)
            return{}

        elements=tree.xpath('//NomeFile')
        ifelementsandelements[0].text:
            filename=elements[0].text
        else:
            return{}

        ifreceipt_type=='RC':
            #Deliveryreceipt
            #ThisisthereceiptsentbytheEStothetransmittingsubjecttocommunicate
            #deliveryofthefiletotheaddressee
            related_invoice=self._search_edi_invoice(filename,'sent')
            ifnotrelated_invoice:
                _logger.info('Error:invoicenotfoundforreceiptfile:%s',attachment.fname)
                return
            related_invoice.l10n_it_send_state='delivered'
            info=self._return_multi_line_xml(tree,['//IdentificativoSdI','//DataOraRicezione','//DataOraConsegna','//Note'])
            related_invoice.message_post(
                body=(_("E-Invoiceisdeliverytothedestinatory:<br/>%s")%(info))
            )

        elifreceipt_type=='NS':
            #Rejectionnotice
            #ThisisthereceiptsentbytheEStothetransmittingsubjectifoneormoreof
            #thecheckscarriedoutbytheESonthefilereceiveddonothaveasuccessfulresult.
            related_invoice=self._search_edi_invoice(filename,'sent')
            ifnotrelated_invoice:
                _logger.info('Error:invoicenotfoundforreceiptfile:%s',attachment.fname)
                return
            related_invoice.l10n_it_send_state='invalid'
            error=self._return_error_xml(tree)
            related_invoice.message_post(
                body=(_("ErrorsintheE-Invoice:<br/>%s")%(error))
            )
            related_invoice.activity_schedule(
                'mail.mail_activity_data_todo',
                summary='Rejectionnotice',
                user_id=related_invoice.invoice_user_id.idifrelated_invoice.invoice_user_idelseself.env.user.id)

        elifreceipt_type=='MC':
            #Faileddeliverynotice
            #ThisisthereceiptsentbytheEStothetransmittingsubjectifthefileisnot
            #deliveredtotheaddressee.
            related_invoice=self._search_edi_invoice(filename,'sent')
            ifnotrelated_invoice:
                _logger.info('Error:invoicenotfoundforreceiptfile:%s',attachment.fname)
                return
            info=self._return_multi_line_xml(tree,[
                '//IdentificativoSdI',
                '//DataOraRicezione',
                '//Descrizione',
                '//MessageId',
                '//Note'])
            related_invoice.message_post(
                body=(_("TheE-invoiceisnotdeliveredtotheaddressee.TheExchangeSystemis\
                unabletodeliverthefiletothePublicAdministration.TheExchangeSystemwill\
                contactthePAtoreporttheproblemandrequestthattheyprovideasolution.\
                Duringthefollowing15days,theExchangeSystemwilltrytoforwardtheFatturaPA\
                filetotheAdministrationinquestionagain.Moreinformation:<br/>%s")%(info))
            )

        elifreceipt_type=='NE':
            #Outcomenotice
            #ThisisthereceiptsentbytheEStotheinvoicesendertocommunicatetheresult
            #(acceptanceorrefusaloftheinvoice)ofthecheckscarriedoutonthedocumentby
            #theaddressee.
            related_invoice=self._search_edi_invoice(filename,'delivered')
            ifnotrelated_invoice:
                _logger.info('Error:invoicenotfoundforreceiptfile:%s',attachment.fname)
                return
            elements=tree.xpath('//Esito')
            ifelementsandelements[0].text:
                ifelements[0].text=='EC01':
                    related_invoice.l10n_it_send_state='delivered_accepted'
                elifelements[0].text=='EC02':
                    related_invoice.l10n_it_send_state='delivered_refused'

            info=self._return_multi_line_xml(tree,
                                               ['//Esito',
                                                '//Descrizione',
                                                '//IdentificativoSdI',
                                                '//DataOraRicezione',
                                                '//DataOraConsegna',
                                                '//Note'
                                               ])
            related_invoice.message_post(
                body=(_("Outcomenotice:%s<br/>%s")%(related_invoice.l10n_it_send_state,info))
            )
            ifrelated_invoice.l10n_it_send_state=='delivered_refused':
                related_invoice.activity_schedule(
                    'mail.mail_activity_todo',
                    user_id=related_invoice.invoice_user_id.idifrelated_invoice.invoice_user_idelseself.env.user.id,
                    summary='Outcomenotice:Refused')

        #elifreceipt_type=='MT':
            #Metadatafile
            #ThisisthefilesentbytheEStotheaddresseetogetherwiththeinvoicefile,
            #containingthemainreferencedataofthefileusefulforprocessing,including
            #theIdentificativoSDI.
            #UselessforFlectra

        elifreceipt_type=='DT':
            #Deadlinepassednotice
            #ThisisthereceiptsentbytheEStoboththeinvoicesenderandtheinvoice
            #addresseetocommunicatetheexpiryofthemaximumtermforcommunicationof
            #acceptance/refusal.
            related_invoice=self._search_edi_invoice(filename,'delivered')
            ifnotrelated_invoice:
                _logger.info('Error:invoicenotfoundforreceiptfile:%s',attachment.fname)
                return
            related_invoice.l10n_it_send_state='delivered_expired'
            info=self._return_multi_line_xml(tree,[
                '//Descrizione',
                '//IdentificativoSdI',
                '//Note'])
            related_invoice.message_post(
                body=(_("Expirationofthemaximumtermforcommunicationofacceptance/refusal:\
                 %s<br/>%s")%(filename,info))
            )

    def_return_multi_line_xml(self,tree,element_tags):
        output_str="<ul>"

        forelement_taginelement_tags:
            elements=tree.xpath(element_tag)
            ifnotelements:
                continue
            forelementinelements:
                ifelement.text:
                    text="".join(element.text.split())
                    output_str+="<li>%s:%s</li>"%(element.tag,text)
        returnoutput_str+"</ul>"

    def_return_error_xml(self,tree):
        output_str="<ul>"

        elements=tree.xpath('//Errore')
        ifnotelements:
            return
        forelementinelements:
            descrizione="".join(element[1].text.split())
            ifdescrizione:
                output_str+="<li>Errore%s:%s</li>"%(element[0].text,descrizione)
        returnoutput_str+"</ul>"

classIrMailServer(models.Model):
    _name="ir.mail_server"
    _inherit="ir.mail_server"

    def_get_test_email_addresses(self):
        self.ensure_one()

        company=self.env["res.company"].search([("l10n_it_mail_pec_server_id","=",self.id)],limit=1)
        ifnotcompany:
            #it'snotaPECserver
            returnsuper()._get_test_email_addresses()
        email_from=self.smtp_user
        ifnotemail_from:
            raiseUserError(_('PleaseconfigureUsernameforthisServerPEC'))
        email_to=company.l10n_it_address_recipient_fatturapa
        ifnotemail_to:
            raiseUserError(_('PleaseconfigureGovernmentPEC-mail	incompanysettings'))
        returnemail_from,email_to

    defbuild_email(self,email_from,email_to,subject,body,email_cc=None,email_bcc=None,reply_to=False,
                attachments=None,message_id=None,references=None,object_id=False,subtype='plain',headers=None,
                body_alternative=None,subtype_alternative='plain'):

        ifself.env.context.get('wo_bounce_return_path')andheaders:
            headers['Return-Path']=email_from
        returnsuper(IrMailServer,self).build_email(email_from,email_to,subject,body,email_cc=email_cc,email_bcc=email_bcc,reply_to=reply_to,
                attachments=attachments,message_id=message_id,references=references,object_id=object_id,subtype=subtype,headers=headers,
                body_alternative=body_alternative,subtype_alternative=subtype_alternative)
