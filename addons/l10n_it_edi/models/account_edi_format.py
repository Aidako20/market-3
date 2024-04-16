#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,_
fromflectra.tests.commonimportForm
fromflectra.exceptionsimportUserError
fromflectra.addons.l10n_it_edi.tools.remove_signatureimportremove_signature
fromflectra.osv.expressionimportOR,AND

fromlxmlimportetree
fromdatetimeimportdatetime
importre
importlogging


_logger=logging.getLogger(__name__)

DEFAULT_FACTUR_ITALIAN_DATE_FORMAT='%Y-%m-%d'


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    #-------------------------------------------------------------------------
    #Helpers
    #-------------------------------------------------------------------------

    @api.model
    def_l10n_it_edi_generate_electronic_invoice_filename(self,invoice):
        '''ReturnsanameconformtotheFatturapaSpecifications:
           SeeESdocumentation2.2
        '''
        a="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        #Eachcompanyshouldhaveitsownfilenamesequence.Ifitdoesnotexist,createit
        n=self.env['ir.sequence'].with_company(invoice.company_id).next_by_code('l10n_it_edi.fattura_filename')
        ifnotn:
            #Theoffsetisusedtoavoidconflictswithexistingfilenames
            offset=62**4
            sequence=self.env['ir.sequence'].sudo().create({
                'name':'FatturaPAFilenameSequence',
                'code':'l10n_it_edi.fattura_filename',
                'company_id':invoice.company_id.id,
                'number_next':offset,
            })
            n=sequence._next()
        #Thenisreturnedasastring,butwerequireanint
        n=int(''.join(filter(lambdac:c.isdecimal(),n)))

        progressive_number=""
        whilen:
            (n,m)=divmod(n,len(a))
            progressive_number=a[m]+progressive_number

        return'%(country_code)s%(codice)s_%(progressive_number)s.xml'%{
            'country_code':invoice.company_id.country_id.code,
            'codice':self.env['res.partner']._l10n_it_normalize_codice_fiscale(invoice.company_id.l10n_it_codice_fiscale),
            'progressive_number':progressive_number.zfill(5),
        }

    def_l10n_it_edi_check_invoice_configuration(self,invoice):
        errors=self._l10n_it_edi_check_ordinary_invoice_configuration(invoice)

        ifnoterrors:
            errors=self._l10n_it_edi_check_simplified_invoice_configuration(invoice)

        returnerrors

    def_l10n_it_edi_is_self_invoice(self,invoice):
        """
            ItalianEDIrequiresVendorbillscomingfromEUcountriestobesentasself-invoices.
            WerecognizethesecasesbasedonthetaxesthattargettheVJtaxgrids,whichimply
            theuseofVATExternalReverseCharge.
        """
        report_lines_xmlids=invoice.line_ids.tax_tag_ids.tax_report_line_ids.mapped(lambdax:x.get_external_id().get(x.id,''))
        return(invoice.is_purchase_document()
                andany([x.startswith("l10n_it.tax_report_line_vj")forxinreport_lines_xmlids]))

    def_l10n_it_edi_check_ordinary_invoice_configuration(self,invoice):
        errors=[]
        seller=invoice.company_id
        buyer=invoice.commercial_partner_id
        is_self_invoice=self._l10n_it_edi_is_self_invoice(invoice)
        ifis_self_invoice:
            seller,buyer=buyer,seller

        #<1.1.1.1>
        ifnotseller.country_id:
            errors.append(_("%smusthaveacountry",seller.display_name))

        #<1.1.1.2>
        ifnotinvoice.company_id.vat:
            errors.append(_("%smusthaveaVATnumber",seller.display_name))
        ifseller.vatandlen(seller.vat)>30:
            errors.append(_("ThemaximumlengthforVATnumberis30.%shaveaVATnumbertoolong:%s.",seller.display_name,seller.vat))

        #<1.2.1.2>
        ifnotis_self_invoiceandnotseller.l10n_it_codice_fiscale:
            errors.append(_("%smusthaveacodicefiscalenumber",seller.display_name))

        #<1.2.1.8>
        ifnotis_self_invoiceandnotseller.l10n_it_tax_system:
            errors.append(_("Theseller'scompanymusthaveataxsystem."))

        #<1.2.2>
        ifnotseller.streetandnotseller.street2:
            errors.append(_("%smusthaveastreet.",seller.display_name))
        ifnotseller.zip:
            errors.append(_("%smusthaveapostcode.",seller.display_name))
        eliflen(seller.zip)!=5andseller.country_id.code=='IT':
            errors.append(_("%smusthaveapostcodeoflength5.",seller.display_name))
        ifnotseller.city:
            errors.append(_("%smusthaveacity.",seller.display_name))
        ifnotseller.country_id:
            errors.append(_("%smusthaveacountry.",seller.display_name))

        ifnotis_self_invoiceandseller.l10n_it_has_tax_representativeandnotseller.l10n_it_tax_representative_partner_id.vat:
            errors.append(_("Taxrepresentativepartner%sof%smusthaveataxnumber.",seller.l10n_it_tax_representative_partner_id.display_name,seller.display_name))

        #<1.4.1>
        ifnotbuyer.vatandnotbuyer.l10n_it_codice_fiscaleandbuyer.country_id.code=='IT':
            errors.append(_("Thebuyer,%s,orhiscompanymusthaveaVATnumberand/orataxcode(CodiceFiscale).",buyer.display_name))

        ifis_self_invoiceandself._l10n_it_edi_services_or_goods(invoice)=='both':
            errors.append(_("CannotapplyReverseChargetoabillwhichcontainsbothservicesandgoods."))

        ifis_self_invoiceandnotbuyer.partner_id.l10n_it_pa_index:
            errors.append(_("Vendorbillssentasself-invoicestotheSdIrequireavalidPAIndex(CodiceDestinatario)onthecompany'scontact."))

        #<2.2.1>
        forinvoice_lineininvoice.invoice_line_ids:
            ifnotinvoice_line.display_typeandlen(invoice_line.tax_ids)!=1:
                errors.append(_("Inline%s,youmustselectoneandonlyonetaxbyline.",invoice_line.name))

        fortax_lineininvoice.line_ids.filtered(lambdaline:line.tax_line_id):
            ifnottax_line.tax_line_id.l10n_it_kind_exonerationandtax_line.tax_line_id.amount==0:
                errors.append(_("%shasanamountof0.0,youmustindicatethekindofexoneration.",tax_line.name))

        returnerrors

    def_l10n_it_edi_is_simplified(self,invoice):
        """
            SimplifiedInvoicesareawayfortheinvoiceissuertocreateaninvoicewithlimiteddata.
            Example:aconsultantgoestotherestaurantandwantstheinvoiceinsteadofthereceipt,
            tobeabletodeducttheexpensefromhisTaxes.TheItalianStateallowstherestaurant
            toissueaSimplifiedInvoicewiththeVATnumberonly,tospeeduptimes,insteadof
            requiringtheaddressandotherinformationsaboutthebuyer.
            Onlyinvoicesunderthethresholdof400Euroesareallowed,toavoidthistool
            beabusedforbiggertransactions,thatwouldenablelesstransparencytotaxinstitutions.
        """
        buyer=invoice.commercial_partner_id
        returnall([
            self.env.ref('l10n_it_edi.account_invoice_it_simplified_FatturaPA_export',raise_if_not_found=False),
            notself._l10n_it_edi_is_self_invoice(invoice),
            self._l10n_it_edi_check_buyer_invoice_configuration(invoice),
            notbuyer.country_idorbuyer.country_id.code=='IT',
            buyer.l10n_it_codice_fiscaleor(buyer.vatand(buyer.vat[:2].upper()=='IT'orbuyer.vat[:2].isdecimal())),
            invoice.amount_total<=400,
        ])

    def_l10n_it_edi_check_simplified_invoice_configuration(self,invoice):
        return[]ifself._l10n_it_edi_is_simplified(invoice)elseself._l10n_it_edi_check_buyer_invoice_configuration(invoice)

    def_l10n_it_edi_partner_in_eu(self,partner):
        europe=self.env.ref('base.europe',raise_if_not_found=False)
        country=partner.country_id
        returnnoteuropeornotcountryorcountryineurope.country_ids

    def_l10n_it_edi_services_or_goods(self,invoice):
        """
            ServicesandgoodshavedifferenttaxgridswhenVATisReverseCharged,andtheycan't
            bemixedinthesameinvoice,becausetheTipoDocumentodependsonwhichwhichkind
            ofproductisboughtandit'sunambiguous.
        """
        scopes=[]
        forlineininvoice.invoice_line_ids.filtered(lambdal:notl.display_type):
            tax_ids_with_tax_scope=line.tax_ids.filtered(lambdax:x.tax_scope)
            iftax_ids_with_tax_scope:
                scopes+=tax_ids_with_tax_scope.mapped('tax_scope')
            else:
                scopes.append(line.product_idandline.product_id.typeor'consu')

        ifset(scopes)==set(['consu','service']):
            return"both"
        returnscopesandscopes.pop()

    def_l10n_it_edi_check_buyer_invoice_configuration(self,invoice):
        errors=[]
        buyer=invoice.commercial_partner_id

        #<1.4.2>
        ifnotbuyer.streetandnotbuyer.street2:
            errors.append(_("%smusthaveastreet.",buyer.display_name))
        ifnotbuyer.country_id:
            errors.append(_("%smusthaveacountry.",buyer.display_name))
        ifnotbuyer.zip:
            errors.append(_("%smusthaveapostcode.",buyer.display_name))
        eliflen(buyer.zip)!=5andbuyer.country_id.code=='IT':
            errors.append(_("%smusthaveapostcodeoflength5.",buyer.display_name))
        ifnotbuyer.city:
            errors.append(_("%smusthaveacity.",buyer.display_name))

        returnerrors

    def_l10n_it_goods_in_italy(self,invoice):
        """
            ThereisaspecificTipoDocumento(DocumentTypeTD19)andtaxgrid(VJ3)forgoods
            thatarephisicallyinItalybutareinaVATdeposit,meaningthatthegoods
            havenotpassedcustoms.
        """
        report_lines_xmlids=invoice.line_ids.tax_tag_ids.tax_report_line_ids.mapped(lambdax:x.get_external_id().get(x.id,''))
        returnany([x=="l10n_it.tax_report_line_vj3"forxinreport_lines_xmlids])

    def_l10n_it_document_type_mapping(self):
        return{
            'TD01':dict(move_types=['out_invoice'],import_type='in_invoice',downpayment=False),
            'TD02':dict(move_types=['out_invoice'],import_type='in_invoice',downpayment=True),
            'TD04':dict(move_types=['out_refund'],import_type='in_refund'),
            'TD07':dict(move_types=['out_invoice'],import_type='in_invoice',simplified=True),
            'TD08':dict(move_types=['out_refund'],import_type='in_refund',simplified=True),
            'TD09':dict(move_types=['out_invoice'],import_type='in_invoice',simplified=True),
            'TD17':dict(move_types=['in_invoice','in_refund'],import_type='in_invoice',self_invoice=True,services_or_goods="service"),
            'TD18':dict(move_types=['in_invoice','in_refund'],import_type='in_invoice',self_invoice=True,services_or_goods="consu",partner_in_eu=True),
            'TD19':dict(move_types=['in_invoice','in_refund'],import_type='in_invoice',self_invoice=True,services_or_goods="consu",goods_in_italy=True),
        }

    def_l10n_it_get_document_type(self,invoice):
        is_simplified=self._l10n_it_edi_is_simplified(invoice)
        is_self_invoice=self._l10n_it_edi_is_self_invoice(invoice)
        services_or_goods=self._l10n_it_edi_services_or_goods(invoice)
        goods_in_italy=services_or_goods=='consu'andself._l10n_it_goods_in_italy(invoice)
        partner_in_eu=self._l10n_it_edi_partner_in_eu(invoice.commercial_partner_id)
        forcode,infosinself._l10n_it_document_type_mapping().items():
            info_services_or_goods=infos.get('services_or_goods',"both")
            info_partner_in_eu=infos.get('partner_in_eu',False)
            ifall([
                invoice.move_typeininfos.get('move_types',False),
                #Onlycheckdownpaymentifthekeyisspecifiedinthedocument_type_mappingentry
                #Ifit'snotspecified,theget()willreturnNoneandtheconditionwillbeTrue
                infos.get('downpayment')in(None,invoice._is_downpayment()),
                is_self_invoice==infos.get('self_invoice',False),
                is_simplified==infos.get('simplified',False),
                info_services_or_goodsin("both",services_or_goods),
                info_partner_in_euin(False,partner_in_eu),
                goods_in_italy==infos.get('goods_in_italy',False),
            ]):
                returncode

        returnNone

    def_l10n_it_is_simplified_document_type(self,document_type):
        returnself._l10n_it_document_type_mapping().get(document_type,{}).get('simplified',False)

    #-------------------------------------------------------------------------
    #Export
    #-------------------------------------------------------------------------

    def_is_embedding_to_invoice_pdf_needed(self):
        #OVERRIDE
        self.ensure_one()
        returnTrueifself.code=='fattura_pa'elsesuper()._is_embedding_to_invoice_pdf_needed()

    def_is_compatible_with_journal(self,journal):
        #OVERRIDE
        self.ensure_one()
        ifself.code!='fattura_pa':
            returnsuper()._is_compatible_with_journal(journal)
        returnjournal.typein('sale','purchase')andjournal.country_code=='IT'

    def_l10n_it_edi_is_required_for_invoice(self,invoice):
        """Istheedirequiredforthisinvoicebasedonthemethod(here:PECmail)
            Deprecated:infuturereleasePECmailwillberemoved.
            TOOVERRIDE
        """
        return((invoice.is_sale_document()orself._l10n_it_get_document_type(invoice))
                andinvoice.country_code=='IT'
                andinvoice.l10n_it_send_statenotin('sent','delivered','delivered_accepted'))

    def_is_required_for_invoice(self,invoice):
        #OVERRIDE
        self.ensure_one()
        ifself.code!='fattura_pa':
            returnsuper()._is_required_for_invoice(invoice)

        returnself._l10n_it_edi_is_required_for_invoice(invoice)

    def_post_fattura_pa(self,invoices):
        #TOOVERRIDE
        invoice=invoices #nobatchingensurethatweonlyhaveoneinvoice
        invoice.l10n_it_send_state='other'
        invoice._check_before_xml_exporting()
        ifinvoice.l10n_it_einvoice_idandinvoice.l10n_it_send_statenotin['invalid','to_send']:
            return{'error':_("Youcan'tregenerateanE-Invoicewhenthefirstoneissentandtherearenoerrors")}
        ifinvoice.l10n_it_einvoice_id:
            invoice.l10n_it_einvoice_id.unlink()
        res=invoice.invoice_generate_xml()
        ifinvoice._is_commercial_partner_pa():
            invoice.message_post(
                body=(_("InvoicesforPAarenotmanagedbyFlectra,youcandownloadthedocumentandsenditonyourown."))
            )
        else:
            invoice.l10n_it_send_state='to_send'
        return{invoice:res}

    def_post_invoice_edi(self,invoices,test_mode=False):
        #OVERRIDE
        self.ensure_one()
        edi_result=super()._post_invoice_edi(invoices,test_mode=test_mode)
        ifself.code!='fattura_pa':
            returnedi_result

        returnself._post_fattura_pa(invoices)

    #-------------------------------------------------------------------------
    #Import
    #-------------------------------------------------------------------------

    def_check_filename_is_fattura_pa(self,filename):
        returnre.search("[A-Z]{2}[A-Za-z0-9]{2,28}_[A-Za-z0-9]{0,5}.((?i:xml.p7m|xml))",filename)

    def_is_fattura_pa(self,filename,tree=None):
        returnself.code=='fattura_pa'andself._check_filename_is_fattura_pa(filename)

    def_create_invoice_from_xml_tree(self,filename,tree,journal=None):
        self.ensure_one()
        ifself._is_fattura_pa(filename,tree):
            returnself._import_fattura_pa(tree,self.env['account.move'])
        returnsuper()._create_invoice_from_xml_tree(filename,tree,journal=journal)

    def_update_invoice_from_xml_tree(self,filename,tree,invoice):
        self.ensure_one()
        ifself._is_fattura_pa(filename,tree):
            iflen(tree.xpath('//FatturaElettronicaBody'))>1:
                invoice.message_post(body='Theattachmentcontainsmultipleinvoices,thisinvoicewasnotupdatedfromit.',
                                     message_type='comment',
                                     subtype_xmlid='mail.mt_note',
                                     author_id=self.env.ref('base.partner_root').id)
            else:
                returnself._import_fattura_pa(tree,invoice)
        returnsuper()._update_invoice_from_xml_tree(filename,tree,invoice)

    def_decode_p7m_to_xml(self,filename,content):
        decoded_content=remove_signature(content)
        ifnotdecoded_content:
            returnNone

        try:
            #SomemalformedXMLareacceptedbyFatturaPA,thisexpendscompatibility
            parser=etree.XMLParser(recover=True)
            xml_tree=etree.fromstring(decoded_content,parser)
        exceptExceptionase:
            _logger.exception("Errorwhenconvertingthexmlcontenttoetree:%s",e)
            returnNone
        ifnotlen(xml_tree):
            returnNone

        returnxml_tree

    def_create_invoice_from_binary(self,filename,content,extension):
        self.ensure_one()
        ifextension.lower()=='.xml.p7m'andself._is_fattura_pa(filename):
            decoded_content=self._decode_p7m_to_xml(filename,content)
            ifdecoded_contentisnotNone:
                returnself._import_fattura_pa(decoded_content,self.env['account.move'])
        returnsuper()._create_invoice_from_binary(filename,content,extension)

    def_update_invoice_from_binary(self,filename,content,extension,invoice):
        self.ensure_one()
        ifextension.lower()=='.xml.p7m'andself._is_fattura_pa(filename):
            decoded_content=self._decode_p7m_to_xml(filename,content)
            ifdecoded_contentisnotNone:
                returnself._import_fattura_pa(decoded_content,invoice)
        returnsuper()._update_invoice_from_binary(filename,content,extension,invoice)

    def_convert_date_from_xml(self,xsdate_str):
        """DatesinFatturaPAareISO8601dateformat,pattern'[-]CCYY-MM-DD[Z|(+|-)hh:mm]'"""
        xsdate_str=xsdate_str.strip()
        xsdate_pattern=r"^-?(?P<date>-?\d{4}-\d{2}-\d{2})(?P<tz>[zZ]|[+-]\d{2}:\d{2})?$"
        try:
            match=re.match(xsdate_pattern,xsdate_str)
            converted_date=datetime.strptime(match.group("date"),DEFAULT_FACTUR_ITALIAN_DATE_FORMAT).date()
        exceptException:
            converted_date=False
        returnconverted_date

    def_import_fattura_pa(self,tree,invoice):
        """Decodesafattura_painvoiceintoaninvoice.

        :paramtree:   thefattura_patreetodecode.
        :paraminvoice:theinvoicetoupdateoranemptyrecordset.
        :returns:      theinvoicewherethefattura_padatawasimported.
        """
        invoices=self.env['account.move']
        first_run=True

        #possibletohavemultipleinvoicesinthecaseofaninvoicebatch,thebatchitselfisrepeatedforeveryinvoiceofthebatch
        forbody_treeintree.xpath('//FatturaElettronicaBody'):
            ifnotfirst_runornotinvoice:
                #makesurealltheiterationscreateanewinvoicerecord(exceptthefirstwhichcouldhavealreadycreatedone)
                invoice=self.env['account.move']
            first_run=False

            #Typemustbepresentinthecontexttogettherightbehaviorofthe_default_journalmethod(account.move).
            #journal_idmustbepresentinthecontexttogettherightbehaviorofthe_default_accountmethod(account.move.line).
            elements=tree.xpath('//CessionarioCommittente//IdCodice')
            company=elementsandself.env['res.company'].search([('vat','ilike',elements[0].text)],limit=1)
            ifnotcompany:
                elements=tree.xpath('//CessionarioCommittente//CodiceFiscale')
                company=elementsandself.env['res.company'].search([('l10n_it_codice_fiscale','ilike',elements[0].text)],limit=1)
                ifnotcompany:
                    #OnlyinvoiceswithacorrectVATorCodiceFiscalecanbeimported
                    _logger.warning('NocompanyfoundwithVATorCodiceFiscalelike%r.',elements[0].text)
                    continue

            #Refundtype.
            #TD01==invoice
            #TD02==advance/downpaymentoninvoice
            #TD03==advance/downpaymentonfee
            #TD04==creditnote
            #TD05==debitnote
            #TD06==fee
            #TD07==simplifiedinvoice
            #TD08==simplifiedcreditnote
            #TD09==simplifieddebitnote
            #Forunsupporteddocumenttypes,justassumein_invoice,andlogthatthetypeisunsupported
            elements=tree.xpath('//DatiGeneraliDocumento/TipoDocumento')
            document_type=elements[0].textifelementselse''
            move_type=self._l10n_it_document_type_mapping().get(document_type,{}).get('import_type',False)
            ifnotmove_type:
                move_type="in_invoice"
                _logger.info('Documenttypenotmanaged:%s.Invoicetypeissetbydefault.',document_type)

            simplified=self._l10n_it_is_simplified_document_type(document_type)

            #SetupthecontextfortheInvoiceForm
            invoice_ctx=invoice.with_company(company)\
                                 .with_context(default_move_type=move_type)

            #movecouldbeasinglerecord(editing)orbeempty(new).
            withForm(invoice_ctx)asinvoice_form:
                message_to_log=[]

                #Partner(firststeptoavoidwarning'Warning!Youmustfirstselectapartner.').<1.2>
                elements=tree.xpath('//CedentePrestatore//IdCodice')
                partner=elementsandself.env['res.partner'].search(['&',('vat','ilike',elements[0].text),'|',('company_id','=',company.id),('company_id','=',False)],limit=1)
                ifnotpartner:
                    elements=tree.xpath('//CedentePrestatore//CodiceFiscale')
                    ifelements:
                        codice=elements[0].text
                        domains=[[('l10n_it_codice_fiscale','=',codice)]]
                        ifre.match(r'^[0-9]{11}$',codice):
                            domains.append([('l10n_it_codice_fiscale','=','IT'+codice)])
                        elifre.match(r'^IT[0-9]{11}$',codice):
                            domains.append([('l10n_it_codice_fiscale','=',self.env['res.partner']._l10n_it_normalize_codice_fiscale(codice))])
                        partner=elementsandself.env['res.partner'].search(
                            AND([OR(domains),OR([[('company_id','=',company.id)],[('company_id','=',False)]])]),limit=1)
                ifnotpartner:
                    elements=tree.xpath('//DatiTrasmissione//Email')
                    partner=elementsandself.env['res.partner'].search(['&','|',('email','=',elements[0].text),('l10n_it_pec_email','=',elements[0].text),'|',('company_id','=',company.id),('company_id','=',False)],limit=1)
                ifpartner:
                    invoice_form.partner_id=partner
                else:
                    message_to_log.append("%s<br/>%s"%(
                        _("Vendornotfound,usefulinformationsfromXMLfile:"),
                        invoice._compose_info_message(
                            tree,'.//CedentePrestatore')))

                #Numberingattributedbythetransmitter.<1.1.2>
                elements=tree.xpath('//ProgressivoInvio')
                ifelements:
                    invoice_form.payment_reference=elements[0].text

                elements=body_tree.xpath('.//DatiGeneraliDocumento//Numero')
                ifelements:
                    invoice_form.ref=elements[0].text

                #Currency.<2.1.1.2>
                elements=body_tree.xpath('.//DatiGeneraliDocumento/Divisa')
                ifelements:
                    currency_str=elements[0].text
                    currency=self.env.ref('base.%s'%currency_str.upper(),raise_if_not_found=False)
                    ifcurrency!=self.env.company.currency_idandcurrency.active:
                        invoice_form.currency_id=currency

                #Date.<2.1.1.3>
                elements=body_tree.xpath('.//DatiGeneraliDocumento/Data')
                ifelements:
                    document_date=self._convert_date_from_xml(elements[0].text)
                    ifdocument_date:
                        invoice_form.invoice_date=document_date
                    else:
                        message_to_log.append("%s<br/>%s"%(
                            _("DocumentdateinvalidinXMLfile:"),
                            invoice._compose_info_message(elements[0],'.')
                        ))

                # DatiBollo.<2.1.1.6>
                elements=body_tree.xpath('.//DatiGeneraliDocumento/DatiBollo/ImportoBollo')
                ifelements:
                    invoice_form.l10n_it_stamp_duty=float(elements[0].text)


                #Comment.<2.1.1.11>
                elements=body_tree.xpath('.//DatiGeneraliDocumento//Causale')
                forelementinelements:
                    invoice_form.narration='%s%s\n'%(invoice_form.narrationor'',element.text)

                #Informationsrelativetothepurchaseorder,thecontract,theagreement,
                #thereceptionphaseorinvoicespreviouslytransmitted
                #<2.1.2>-<2.1.6>
                fordocument_typein['DatiOrdineAcquisto','DatiContratto','DatiConvenzione','DatiRicezione','DatiFattureCollegate']:
                    elements=body_tree.xpath('.//DatiGenerali/'+document_type)
                    ifelements:
                        forelementinelements:
                            message_to_log.append("%s%s<br/>%s"%(document_type,_("fromXMLfile:"),
                            invoice._compose_info_message(element,'.')))

                # DatiDDT.<2.1.8>
                elements=body_tree.xpath('.//DatiGenerali/DatiDDT')
                ifelements:
                    message_to_log.append("%s<br/>%s"%(
                        _("TransportinformationsfromXMLfile:"),
                        invoice._compose_info_message(body_tree,'.//DatiGenerali/DatiDDT')))

                #Duedate.<2.4.2.5>
                elements=body_tree.xpath('.//DatiPagamento/DettaglioPagamento/DataScadenzaPagamento')
                ifelements:
                    date_str=elements[0].text.strip()
                    ifdate_str:
                        due_date=self._convert_date_from_xml(date_str)
                        ifdue_date:
                            invoice_form.invoice_date_due=fields.Date.to_string(due_date)
                        else:
                            message_to_log.append("%s<br/>%s"%(
                                _("PaymentduedateinvalidinXMLfile:"),
                                invoice._compose_info_message(elements[0],'.')
                            ))

                #Totalamount.<2.4.2.6>
                elements=body_tree.xpath('.//ImportoPagamento')
                amount_total_import=0
                forelementinelements:
                    amount_total_import+=float(element.text)
                ifamount_total_import:
                    message_to_log.append(_("TotalamountfromtheXMLFile:%s")%(
                        amount_total_import))

                #Bankaccount.<2.4.2.13>
                ifinvoice_form.move_typenotin('out_invoice','in_refund'):
                    elements=body_tree.xpath('.//DatiPagamento/DettaglioPagamento/IBAN')
                    ifelements:
                        ifinvoice_form.partner_idandinvoice_form.partner_id.commercial_partner_id:
                            bank=self.env['res.partner.bank'].search([
                                ('acc_number','=',elements[0].text),
                                ('partner_id','=',invoice_form.partner_id.commercial_partner_id.id),
                                ('company_id','in',[invoice_form.company_id.id,False])
                            ],order='company_id',limit=1)
                        else:
                            bank=self.env['res.partner.bank'].search([
                                ('acc_number','=',elements[0].text),('company_id','in',[invoice_form.company_id.id,False])
                            ],order='company_id',limit=1)
                        ifbank:
                            invoice_form.partner_bank_id=bank
                        else:
                            message_to_log.append("%s<br/>%s"%(
                                _("Bankaccountnotfound,usefulinformationsfromXMLfile:"),
                                invoice._compose_multi_info_message(
                                    body_tree,['.//DatiPagamento//Beneficiario',
                                        './/DatiPagamento//IstitutoFinanziario',
                                        './/DatiPagamento//IBAN',
                                        './/DatiPagamento//ABI',
                                        './/DatiPagamento//CAB',
                                        './/DatiPagamento//BIC',
                                        './/DatiPagamento//ModalitaPagamento'])))
                else:
                    elements=body_tree.xpath('.//DatiPagamento/DettaglioPagamento')
                    ifelements:
                        message_to_log.append("%s<br/>%s"%(
                            _("Bankaccountnotfound,usefulinformationsfromXMLfile:"),
                            invoice._compose_info_message(body_tree,'.//DatiPagamento')))

                #Invoicelines.<2.2.1>
                ifnotsimplified:
                    elements=body_tree.xpath('.//DettaglioLinee')
                else:
                    elements=body_tree.xpath('.//DatiBeniServizi')

                ifelements:
                    forelementinelements:
                        withinvoice_form.invoice_line_ids.new()asinvoice_line_form:

                            #Sequence.
                            line_elements=element.xpath('.//NumeroLinea')
                            ifline_elements:
                                invoice_line_form.sequence=int(line_elements[0].text)

                            #Product.
                            elements_code=element.xpath('.//CodiceArticolo')
                            ifelements_code:
                                forelement_codeinelements_code:
                                    type_code=element_code.xpath('.//CodiceTipo')[0]
                                    code=element_code.xpath('.//CodiceValore')[0]
                                    iftype_code.text=='EAN':
                                        product=self.env['product.product'].search([('barcode','=',code.text)])
                                        ifproduct:
                                            invoice_line_form.product_id=product
                                            break
                                    ifpartner:
                                        product_supplier=self.env['product.supplierinfo'].search([('name','=',partner.id),('product_code','=',code.text)],limit=2)
                                        ifproduct_supplierandlen(product_supplier)==1andproduct_supplier.product_id:
                                            invoice_line_form.product_id=product_supplier.product_id
                                            break
                                ifnotinvoice_line_form.product_id:
                                    forelement_codeinelements_code:
                                        code=element_code.xpath('.//CodiceValore')[0]
                                        product=self.env['product.product'].search([('default_code','=',code.text)],limit=2)
                                        ifproductandlen(product)==1:
                                            invoice_line_form.product_id=product
                                            break

                            #Label.
                            line_elements=element.xpath('.//Descrizione')
                            ifline_elements:
                                invoice_line_form.name="".join(line_elements[0].text.split())

                            #Quantity.
                            line_elements=element.xpath('.//Quantita')
                            ifline_elements:
                                invoice_line_form.quantity=float(line_elements[0].text)
                            else:
                                invoice_line_form.quantity=1

                            #Taxes
                            percentage=None
                            price_subtotal=0
                            ifnotsimplified:
                                tax_element=element.xpath('.//AliquotaIVA')
                                iftax_elementandtax_element[0].text:
                                    percentage=float(tax_element[0].text)
                            else:
                                amount_element=element.xpath('.//Importo')
                                ifamount_elementandamount_element[0].text:
                                    amount=float(amount_element[0].text)
                                    tax_element=element.xpath('.//Aliquota')
                                    iftax_elementandtax_element[0].text:
                                        percentage=float(tax_element[0].text)
                                        price_subtotal=amount/(1+percentage/100)
                                    else:
                                        tax_element=element.xpath('.//Imposta')
                                        iftax_elementandtax_element[0].text:
                                            tax_amount=float(tax_element[0].text)
                                            price_subtotal=amount-tax_amount
                                            percentage=round(tax_amount/price_subtotal*100)

                            natura_element=element.xpath('.//Natura')
                            invoice_line_form.tax_ids.clear()
                            ifpercentageisnotNone:
                                ifnatura_elementandnatura_element[0].text:
                                    l10n_it_kind_exoneration=natura_element[0].text
                                    tax=self.env['account.tax'].search([
                                        ('company_id','=',invoice_form.company_id.id),
                                        ('amount_type','=','percent'),
                                        ('type_tax_use','=','purchase'),
                                        ('amount','=',percentage),
                                        ('l10n_it_kind_exoneration','=',l10n_it_kind_exoneration),
                                    ],limit=1)
                                else:
                                    tax=self.env['account.tax'].search([
                                        ('company_id','=',invoice_form.company_id.id),
                                        ('amount_type','=','percent'),
                                        ('type_tax_use','=','purchase'),
                                        ('amount','=',percentage),
                                    ],limit=1)
                                    l10n_it_kind_exoneration=''

                                iftax:
                                    invoice_line_form.tax_ids.add(tax)
                                else:
                                    ifl10n_it_kind_exoneration:
                                        message_to_log.append(_("Taxnotfoundwithpercentage:%sandexoneration%sforthearticle:%s")%(
                                            percentage,
                                            l10n_it_kind_exoneration,
                                            invoice_line_form.name))
                                    else:
                                        message_to_log.append(_("Taxnotfoundwithpercentage:%sforthearticle:%s")%(
                                            percentage,
                                            invoice_line_form.name))

                            #PriceUnit.
                            ifnotsimplified:
                                line_elements=element.xpath('.//PrezzoUnitario')
                                ifline_elements:
                                    invoice_line_form.price_unit=float(line_elements[0].text)
                            else:
                                invoice_line_form.price_unit=price_subtotal

                            #Discounts
                            discount_elements=element.xpath('.//ScontoMaggiorazione')
                            ifdiscount_elements:
                                discount_element=discount_elements[0]
                                discount_percentage=discount_element.xpath('.//Percentuale')
                                #Specialcaseofonly1percentagediscount
                                ifdiscount_percentageandlen(discount_elements)==1:
                                    discount_type=discount_element.xpath('.//Tipo')
                                    discount_sign=1
                                    ifdiscount_typeanddiscount_type[0].text=='MG':
                                        discount_sign=-1
                                    invoice_line_form.discount=discount_sign*float(discount_percentage[0].text)
                                #Discountsincascadesummarizedin1percentage
                                else:
                                    total=float(element.xpath('.//PrezzoTotale')[0].text)
                                    discount=100-(100*total)/(invoice_line_form.quantity*invoice_line_form.price_unit)
                                    invoice_line_form.discount=discount


                #Globaldiscountsummarizedin1amount
                discount_elements=body_tree.xpath('.//DatiGeneraliDocumento/ScontoMaggiorazione')
                ifdiscount_elements:
                    taxable_amount=invoice_form.amount_untaxed
                    discounted_amount=taxable_amount
                    fordiscount_elementindiscount_elements:
                        discount_type=discount_element.xpath('.//Tipo')
                        discount_sign=1
                        ifdiscount_typeanddiscount_type[0].text=='MG':
                            discount_sign=-1
                        discount_amount=discount_element.xpath('.//Importo')
                        ifdiscount_amount:
                            discounted_amount-=discount_sign*float(discount_amount[0].text)
                            continue
                        discount_percentage=discount_element.xpath('.//Percentuale')
                        ifdiscount_percentage:
                            discounted_amount*=1-discount_sign*float(discount_percentage[0].text)/100

                    general_discount=discounted_amount-taxable_amount
                    sequence=len(elements)+1

                    withinvoice_form.invoice_line_ids.new()asinvoice_line_global_discount:
                        invoice_line_global_discount.tax_ids.clear()
                        invoice_line_global_discount.sequence=sequence
                        invoice_line_global_discount.name='SCONTO'ifgeneral_discount<0else'MAGGIORAZIONE'
                        invoice_line_global_discount.price_unit=general_discount

            new_invoice=invoice_form.save()
            new_invoice.l10n_it_send_state="other"

            elements=body_tree.xpath('.//Allegati')
            ifelements:
                forelementinelements:
                    name_attachment=element.xpath('.//NomeAttachment')[0].text
                    attachment_64=str.encode(element.xpath('.//Attachment')[0].text)
                    attachment_64=self.env['ir.attachment'].create({
                        'name':name_attachment,
                        'datas':attachment_64,
                        'type':'binary',
                        'res_model':'account.move',
                        'res_id':new_invoice.id,
                    })

                    #default_res_idishadtocontexttoavoidfacturxtoimporthiscontent
                    #no_new_invoicetopreventfromloopingonthemessage_postthatwouldcreateanewinvoicewithoutit
                    new_invoice.with_context(no_new_invoice=True,default_res_id=new_invoice.id).message_post(
                        body=(_("AttachmentfromXML")),
                        attachment_ids=[attachment_64.id]
                    )

            formessageinmessage_to_log:
                new_invoice.message_post(body=message)

            invoices+=new_invoice

        returninvoices
