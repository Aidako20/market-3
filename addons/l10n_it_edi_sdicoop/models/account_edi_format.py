#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_,_lt
fromflectra.exceptionsimportUserError
fromflectra.addons.account_edi_proxy_client.models.account_edi_proxy_userimportAccountEdiProxyError

fromlxmlimportetree
importbase64
importlogging

_logger=logging.getLogger(__name__)


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    #-------------------------------------------------------------------------
    #Import
    #-------------------------------------------------------------------------

    def_cron_receive_fattura_pa(self):
        '''Checktheproxyforincominginvoices.
        '''
        proxy_users=self.env['account_edi_proxy_client.user'].search([('edi_format_id','=',self.env.ref('l10n_it_edi.edi_fatturaPA').id)])

        ifproxy_users._get_demo_state()=='demo':
            return

        forproxy_userinproxy_users:
            company=proxy_user.company_id
            try:
                res=proxy_user._make_request(proxy_user._get_server_url()+'/api/l10n_it_edi/1/in/RicezioneInvoice')

            exceptAccountEdiProxyErrorase:
                res={}
                _logger.error('ErrorwhilereceivingfilefromSdiCoop:%s',e)

            proxy_acks=[]
            forid_transaction,fatturainres.items():

                ifself.env['ir.attachment'].search([('name','=',fattura['filename']),('res_model','=','account.move')],limit=1):
                    #nameshouldbeunique,theinvoicealreadyexists
                    _logger.info('E-invoicealreadyexist:%s',fattura['filename'])
                    proxy_acks.append(id_transaction)
                    continue

                file=proxy_user._decrypt_data(fattura['file'],fattura['key'])

                try:
                    tree=etree.fromstring(file)
                exceptException:
                    #shouldnothappenasthefilehasbeencheckedbySdiCoop
                    _logger.info('Receivedfilebadlyformatted,skipping:\n%s',file)
                    continue
                invoice=self.env['account.move'].with_company(company).create({'move_type':'in_invoice'})
                attachment=self.env['ir.attachment'].create({
                    'name':fattura['filename'],
                    'raw':file,
                    'type':'binary',
                    'res_model':'account.move',
                    'res_id':invoice.id
                })
                ifnotself.env.context.get('test_skip_commit'):
                    self.env.cr.commit()#Incasesomethingfailsafter,westillhavetheattachment
                #Sothatwedon'tdeletetheattachmentwhendeletingtheinvoice
                attachment.res_id=False
                attachment.res_model=False
                invoice.unlink()
                invoice=self.env.ref('l10n_it_edi.edi_fatturaPA')._create_invoice_from_xml_tree(fattura['filename'],tree)
                attachment.write({'res_model':'account.move',
                                  'res_id':invoice.id})
                proxy_acks.append(id_transaction)
                ifnotself.env.context.get('test_skip_commit'):
                    self.env.cr.commit()

            ifproxy_acks:
                try:
                    proxy_user._make_request(proxy_user._get_server_url()+'/api/l10n_it_edi/1/ack',
                                            params={'transaction_ids':proxy_acks})
                exceptAccountEdiProxyErrorase:
                    _logger.error('ErrorwhilereceivingfilefromSdiCoop:%s',e)

    #-------------------------------------------------------------------------
    #Export
    #-------------------------------------------------------------------------

    def_get_invoice_edi_content(self,move):
        #OVERRIDE
        ifself.code!='fattura_pa':
            returnsuper()._get_invoice_edi_content(move)
        returnmove._export_as_xml()

    def_check_move_configuration(self,move):
        #OVERRIDE
        res=super()._check_move_configuration(move)
        ifself.code!='fattura_pa':
            returnres

        res.extend(self._l10n_it_edi_check_invoice_configuration(move))

        ifnotself._get_proxy_user(move.company_id):
            res.append(_("YoumustacceptthetermsandconditionsinthesettingstouseFatturaPA."))

        returnres

    def_needs_web_services(self):
        self.ensure_one()
        returnself.code=='fattura_pa'orsuper()._needs_web_services()

    def_l10n_it_edi_is_required_for_invoice(self,invoice):
        """_is_required_for_invoiceforSdiCoop.
            OVERRIDE
        """
        is_self_invoice=self._l10n_it_edi_is_self_invoice(invoice)
        return(
            (invoice.is_sale_document()or(is_self_invoiceandinvoice.is_purchase_document()))
            andinvoice.l10n_it_send_statenotin('sent','delivered','delivered_accepted')
            andinvoice.country_code=='IT'
        )

    def_support_batching(self,move=None,state=None,company=None):
        #OVERRIDE
        ifself.code=='fattura_pa':
            returnstate=='to_send'andmove.is_invoice()

        returnsuper()._support_batching(move=move,state=state,company=company)

    def_get_batch_key(self,move,state):
        #OVERRIDE
        ifself.code!='fattura_pa':
            returnsuper()._get_batch_key(move,state)

        returnmove.move_type,bool(move.l10n_it_edi_transaction)

    def_l10n_it_post_invoices_step_1(self,invoices):
        '''Sendtheinvoicestotheproxy.
        '''
        to_return={}

        to_send={}
        forinvoiceininvoices:
            xml=b"<?xmlversion='1.0'encoding='UTF-8'?>"+invoice._export_as_xml()
            filename=self._l10n_it_edi_generate_electronic_invoice_filename(invoice)
            attachment=self.env['ir.attachment'].create({
                'name':filename,
                'res_id':invoice.id,
                'res_model':invoice._name,
                'datas':base64.encodebytes(xml),
                'description':_('Italianinvoice:%s',invoice.move_type),
                'type':'binary',
            })
            invoice.l10n_it_edi_attachment_id=attachment

            ifinvoice._is_commercial_partner_pa():
                invoice.message_post(
                    body=(_("InvoicesforPAarenotmanagedbyFlectra,youcandownloadthedocumentandsenditonyourown."))
                )
                to_return[invoice]={'attachment':attachment,'success':True}
            else:
                to_send[filename]={
                    'invoice':invoice,
                    'data':{'filename':filename,'xml':base64.b64encode(xml).decode()}}

        company=invoices.company_id
        proxy_user=self._get_proxy_user(company)
        ifnotproxy_user: #proxyusershouldexist,becausethereisacheckin_check_move_configuration
            return{invoice:{
                'error':_("YoumustacceptthetermsandconditionsinthesettingstouseFatturaPA."),
                'blocking_level':'error'}forinvoiceininvoices}

        responses={}
        ifproxy_user._get_demo_state()=='demo':
            responses={i['data']['filename']:{'id_transaction':'demo'}foriinto_send.values()}
        else:
            try:
                responses=self._l10n_it_edi_upload([i['data']foriinto_send.values()],proxy_user)
            exceptAccountEdiProxyErrorase:
                return{invoice:{'error':e.message,'blocking_level':'error'}forinvoiceininvoices}

        forfilename,responseinresponses.items():
            invoice=to_send[filename]['invoice']
            to_return[invoice]=response
            if'id_transaction'inresponse:
                invoice.l10n_it_edi_transaction=response['id_transaction']
                to_return[invoice].update({
                    'error':_('TheinvoicewassenttoFatturaPA,butwearestillawaitingaresponse.Clickthelinkabovetocheckforanupdate.'),
                    'blocking_level':'info',
                })
        returnto_return

    def_l10n_it_post_invoices_step_2(self,invoices):
        '''CheckifthesentinvoiceshavebeenprocessedbyFatturaPA.
        '''
        to_check={i.l10n_it_edi_transaction:iforiininvoices}
        to_return={}
        company=invoices.company_id

        proxy_user=self._get_proxy_user(company)
        ifnotproxy_user: #proxyusershouldexist,becausethereisacheckin_check_move_configuration
            return{invoice:{
                'error':_("YoumustacceptthetermsandconditionsinthesettingstouseFatturaPA."),
                'blocking_level':'error'}forinvoiceininvoices}

        ifproxy_user._get_demo_state()=='demo':
            #simulatesuccessandbypassack
            return{invoice:{'attachment':invoice.l10n_it_edi_attachment_id}forinvoiceininvoices}
        else:
            try:
                responses=proxy_user._make_request(proxy_user._get_server_url()+'/api/l10n_it_edi/1/in/TrasmissioneFatture',
                                                    params={'ids_transaction':list(to_check.keys())})
            exceptAccountEdiProxyErrorase:
                return{invoice:{'error':e.message,'blocking_level':'error'}forinvoiceininvoices}

        proxy_acks=[]
        forid_transaction,responseinresponses.items():
            invoice=to_check[id_transaction]
            if'error'inresponse:
                to_return[invoice]=response
                continue

            state=response['state']
            ifstate=='awaiting_outcome':
                to_return[invoice]={
                    'error':_('TheinvoicewassenttoFatturaPA,butwearestillawaitingaresponse.Clickthelinkabovetocheckforanupdate.'),
                    'blocking_level':'info'}

            elifstate=='not_found':
                #Invoicedoesnotexistonproxy.Eitheritdoesnotbelongtothisproxy_useroritwasnotcreatedcorrectlywhen
                #itwassenttotheproxy.
                to_return[invoice]={'error':_('Youarenotallowedtocheckthestatusofthisinvoice.'),'blocking_level':'error'}

            elifstate=='ricevutaConsegna':
                ifinvoice._is_commercial_partner_pa():
                    to_return[invoice]={'error':_('Theinvoicehasbeensuccesfullytransmitted.Theaddresseehas15daystoacceptorrejectit.')}
                else:
                    to_return[invoice]={'attachment':invoice.l10n_it_edi_attachment_id,'success':True}
                proxy_acks.append(id_transaction)

            elifstate=='notificaMancataConsegna':
                ifinvoice._is_commercial_partner_pa():
                    to_return[invoice]={'error':_(
                        'Theinvoicehasbeenissued,butthedeliverytothePublicAdministration'
                        'hasfailed.TheExchangeSystemwillcontactthemtoreporttheproblem'
                        'andrequestthattheyprovideasolution.'
                        'Duringthefollowing10days,theExchangeSystemwilltrytoforwardthe'
                        'FatturaPAfiletothePublicAdministrationinquestionagain.'
                        'Shouldthisalsofail,theSystemwillnotifyFlectraofthefaileddelivery,'
                        'andyouwillberequiredtosendtheinvoicetotheAdministration'
                        'throughanotherchannel,outsideoftheExchangeSystem.')}
                else:
                    to_return[invoice]={'success':True,'attachment':invoice.l10n_it_edi_attachment_id}
                    invoice._message_log(body=_(
                        'Theinvoicehasbeenissued,butthedeliverytotheAddresseehas'
                        'failed.Youwillberequiredtosendacourtesycopyoftheinvoice'
                        'toyourcustomerthroughanotherchannel,outsideoftheExchange'
                        'System,andpromptlynotifyhimthattheoriginalisdeposited'
                        'inhispersonalareaontheportal"InvoicesandFees"ofthe'
                        'RevenueAgency.'))
                proxy_acks.append(id_transaction)

            elifstate=='NotificaDecorrenzaTermini':
                #ThisconditionispartofthePublicAdministrationflow
                invoice._message_log(body=_(
                    'Theinvoicehasbeencorrectlyissued.ThePublicAdministrationrecipient'
                    'had15daystoeitheracceptorrefusedthisdocument,buttheydidnotreply,'
                    'sofromnowonweconsideritaccepted.'))
                to_return[invoice]={'attachment':invoice.l10n_it_edi_attachment_id,'success':True}
                proxy_acks.append(id_transaction)

            #Inthetransactionstatesabove,wedon'tneedtoreadtheattachment.
            #Inthefollowingcasesinsteadweneedtoreadtheinformationinside
            #aboutthenotificationitself,i.e.theerrormessageincaseofrejection.
            else:
                attachment_file=response.get('file')
                ifnotattachment_file:#Itmeansthereisnostatusupdate,sowecanskipit
                    document=invoice.edi_document_ids.filtered(lambdad:d.edi_format_id.code=='fattura_pa')
                    to_return[invoice]={'error':document.error,'blocking_level':document.blocking_level}
                    continue

                xml=proxy_user._decrypt_data(attachment_file,response['key'])
                response_tree=etree.fromstring(xml)

                ifstate=='notificaScarto':
                    elements=response_tree.xpath('//Errore')
                    error_codes=[element.find('Codice').textforelementinelements]
                    errors=[element.find('Descrizione').textforelementinelements]
                    #Duplicatedinvoice
                    if'00404'inerror_codes:
                        idx=error_codes.index('00404')
                        invoice.message_post(body=_(
                            'ThisinvoicenumberhadalreadybeensubmittedtotheSdI,soitis'
                            'setasSent.Pleaseverifythatthesystemiscorrectlyconfigured,'
                            'becausethecorrectflowdoesnotneedtosendthesameinvoice'
                            'twiceforanyreason.\n'
                            'OriginalmessagefromtheSDI:%s',errors[idx]))
                        to_return[invoice]={'attachment':invoice.l10n_it_edi_attachment_id,'success':True}
                    else:
                        #Addhelpfultextifduplicatedfilenameerror
                        if'00002'inerror_codes:
                            idx=error_codes.index('00002')
                            errors[idx]=_(
                                'Thefilenameisduplicated.Tryagain(oradjusttheFatturaPAFilenamesequence).'
                                'OriginalmessagefromtheSDI:%s',[errors[idx]]
                            )
                        to_return[invoice]={'error':self._format_error_message(_('TheinvoicehasbeenrefusedbytheExchangeSystem'),errors),'blocking_level':'error'}
                        invoice.l10n_it_edi_transaction=False
                    proxy_acks.append(id_transaction)

                elifstate=='notificaEsito':
                    outcome=response_tree.find('Esito').text
                    ifoutcome=='EC01':
                        to_return[invoice]={'attachment':invoice.l10n_it_edi_attachment_id,'success':True}
                    else: #ECO2
                        to_return[invoice]={'error':_('Theinvoicewasrefusedbytheaddressee.'),'blocking_level':'error'}
                    proxy_acks.append(id_transaction)

        ifproxy_acks:
            try:
                proxy_user._make_request(proxy_user._get_server_url()+'/api/l10n_it_edi/1/ack',
                                        params={'transaction_ids':proxy_acks})
            exceptAccountEdiProxyErrorase:
                #Willbeignoredandackedagainnexttime.
                _logger.error('ErrorwhileackingfiletoSdiCoop:%s',e)

        returnto_return

    def_post_fattura_pa(self,invoices):
        #OVERRIDE
        ifnotinvoices[0].l10n_it_edi_transaction:
            returnself._l10n_it_post_invoices_step_1(invoices)
        else:
            returnself._l10n_it_post_invoices_step_2(invoices)

    #-------------------------------------------------------------------------
    #Proxymethods
    #-------------------------------------------------------------------------

    def_get_proxy_identification(self,company):
        ifself.code!='fattura_pa':
            returnsuper()._get_proxy_identification()

        ifnotcompany.l10n_it_codice_fiscale:
            raiseUserError(_('PleasefillyourcodicefiscaletobeabletoreceiveinvoicesfromFatturaPA'))

        returnself.env['res.partner']._l10n_it_normalize_codice_fiscale(company.l10n_it_codice_fiscale)

    def_l10n_it_edi_upload(self,files,proxy_user):
        '''Uploadfilestofatturapa.

        :paramfiles:   Alistofdictionary{filename,base64_xml}.
        :returns:       Adictionary.
        *message:      Messagefromfatturapa.
        *transactionId:ThefatturapaIDofthisrequest.
        *error:        Aneventualerror.
        *error_level:  Info,warning,error.
        '''
        ERRORS={
            'EI01':{'error':_lt('Attachedfileisempty'),'blocking_level':'error'},
            'EI02':{'error':_lt('Servicemomentarilyunavailable'),'blocking_level':'warning'},
            'EI03':{'error':_lt('Unauthorizeduser'),'blocking_level':'error'},
        }

        ifnotfiles:
            return{}

        result=proxy_user._make_request(proxy_user._get_server_url()+'/api/l10n_it_edi/1/out/SdiRiceviFile',params={'files':files})

        #Translatetheerrors.
        forfilenameinresult.keys():
            if'error'inresult[filename]:
                result[filename]=ERRORS.get(result[filename]['error'],{'error':result[filename]['error'],'blocking_level':'error'})

        returnresult
