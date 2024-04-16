#-*-coding:utf-8-*-

fromflectraimportapi,models,fields,tools,_
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT,float_repr,str2bool
fromflectra.tests.commonimportForm
fromflectra.exceptionsimportRedirectWarning,UserError

fromdatetimeimportdatetime
fromlxmlimportetree
fromPyPDF2importPdfFileReader
importbase64

importio

importlogging

_logger=logging.getLogger(__name__)


DEFAULT_FACTURX_DATE_FORMAT='%Y%m%d'


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    def_is_compatible_with_journal(self,journal):
        self.ensure_one()
        res=super()._is_compatible_with_journal(journal)
        ifself.code!='facturx_1_0_05'orself._is_account_edi_ubl_cii_available():
            returnres
        returnjournal.type=='sale'

    def_post_invoice_edi(self,invoices,test_mode=False):
        self.ensure_one()
        ifself.code!='facturx_1_0_05'orself._is_account_edi_ubl_cii_available():
            returnsuper()._post_invoice_edi(invoices,test_mode=test_mode)
        res={}
        forinvoiceininvoices:
            attachment=self._export_facturx(invoice)
            res[invoice]={'attachment':attachment}
        returnres

    def_is_embedding_to_invoice_pdf_needed(self):
        #OVERRIDE
        self.ensure_one()
        returnTrueifself.code=='facturx_1_0_05'elsesuper()._is_embedding_to_invoice_pdf_needed()

    def_get_embedding_to_invoice_pdf_values(self,invoice):
        values=super()._get_embedding_to_invoice_pdf_values(invoice)
        ifvaluesandself.code=='facturx_1_0_05':
            values['name']='factur-x.xml'
        returnvalues

    def_prepare_invoice_report(self,pdf_writer,edi_document):
        self.ensure_one()
        ifself.code!='facturx_1_0_05'orself._is_account_edi_ubl_cii_available():
            returnsuper()._prepare_invoice_report(pdf_writer,edi_document)
        ifnotedi_document.attachment_id:
            return

        pdf_writer.embed_flectra_attachment(edi_document.attachment_id,subtype='text/xml')
        ifnotpdf_writer.is_pdfaandstr2bool(self.env['ir.config_parameter'].sudo().get_param('edi.use_pdfa','False')):
            try:
                pdf_writer.convert_to_pdfa()
            exceptExceptionase:
                _logger.exception("ErrorwhileconvertingtoPDF/A:%s",e)
            metadata_template=self.env.ref('account_edi_facturx.account_invoice_pdfa_3_facturx_metadata',raise_if_not_found=False)
            ifmetadata_template:
                pdf_writer.add_file_metadata(metadata_template._render({
                    'title':edi_document.move_id.name,
                    'date':fields.Date.context_today(self),
                }))

    def_export_facturx(self,invoice):

        defformat_date(dt):
            #FormatthedateintheFactur-xstandard.
            dt=dtordatetime.now()
            returndt.strftime(DEFAULT_FACTURX_DATE_FORMAT)

        defformat_monetary(number,currency):
            #Formatthemonetaryvaluestoavoidtrailingdecimals(e.g.90.85000000000001).
            ifcurrency.is_zero(number): #Ensurethatweneverreturn-0.0
                number=0.0
            returnfloat_repr(number,currency.decimal_places)

        self.ensure_one()
        #Createfilecontent.
        seller_siret='siret'ininvoice.company_id._fieldsandinvoice.company_id.siretorinvoice.company_id.company_registry
        buyer_siret='siret'ininvoice.commercial_partner_id._fieldsandinvoice.commercial_partner_id.siret
        template_values={
            'record':invoice,
            'format_date':format_date,
            'format_monetary':format_monetary,
            'invoice_line_values':[],
            'seller_specified_legal_organization':seller_siret,
            'buyer_specified_legal_organization':buyer_siret,
            #ChorusPROfields
            'buyer_reference':'buyer_reference'ininvoice._fieldsandinvoice.buyer_referenceor'',
            'contract_reference':'contract_reference'ininvoice._fieldsandinvoice.contract_referenceor'',
            'purchase_order_reference':'purchase_order_reference'ininvoice._fieldsandinvoice.purchase_order_referenceor'',
        }
        #Taxlines.
        #Theoldsystemwasmakingonetotal"line"pertaxinthexml,byusingthetax_line_id.
        #Thenewoneismakingonetotal"line"foreachtaxcategoryandrategroup.
        aggregated_taxes_details=invoice._prepare_edi_tax_details(
            grouping_key_generator=lambdatax_values:{
                'unece_tax_category_code':tax_values['tax_id']._get_unece_category_code(invoice.commercial_partner_id,invoice.company_id),
                'amount':tax_values['tax_id'].amount
            }
        )['tax_details']

        balance_multiplicator=-1ifinvoice.is_inbound()else1
        #Mapthenewkeysfromthebackported_prepare_edi_tax_detailsintotheoldonesforcompatibilitywiththeold
        #template.Alsoapplythemultiplicationhereforconsistencybetweentheoldandnewtemplate.
        fortax_detailinaggregated_taxes_details.values():
            tax_detail['tax_base_amount']=balance_multiplicator*tax_detail['base_amount_currency']
            tax_detail['tax_amount']=balance_multiplicator*tax_detail['tax_amount_currency']

            #Theoldtemplatewouldgettheamountfromataxlinegiventoit,while
            #thenewonewouldgettheamountfromthedictionaryreturnedby_prepare_edi_tax_detailsdirectly.
            #Asthelinewasonlyusedtogetthetaxamount,givingitanylinewiththesameamountwillgiveacorrect
            #resultevenifthetaxlinedoesn'tmakemuchsenseasthisisatotalthatisnotlinkedtoaspecifictax.
            #Idon'thaveasolutionfor0%taxes,wewillgiveanemptylinethatwillallowtorenderthexml,butit
            #won'tbecompletelycorrect.(TheRateApplicablePercentwillbemissingforthatline)
            tax_detail['line']=invoice.line_ids.filtered(lambdal:l.tax_line_idandl.tax_line_id.amount==tax_detail['amount'])[:1]

        #Invoicelines.
        fori,lineinenumerate(invoice.invoice_line_ids.filtered(lambdal:notl.display_type)):
            price_unit_with_discount=line.price_unit*(1-(line.discount/100.0))
            taxes_res=line.tax_ids.with_context(force_sign=line.move_id._get_tax_force_sign()).compute_all(
                price_unit_with_discount,
                currency=line.currency_id,
                quantity=line.quantity,
                product=line.product_id,
                partner=invoice.partner_id,
                is_refund=line.move_id.move_typein('in_refund','out_refund'),
            )

            ifline.discount==100.0:
                gross_price_subtotal=line.currency_id.round(line.price_unit*line.quantity)
            else:
                gross_price_subtotal=line.currency_id.round(line.price_subtotal/(1-(line.discount/100.0)))
            line_template_values={
                'line':line,
                'index':i+1,
                'tax_details':[],
                'net_price_subtotal':taxes_res['total_excluded'],
                'price_discount_unit':(gross_price_subtotal-line.price_subtotal)/line.quantityifline.quantityelse0.0,
                'unece_uom_code':line.product_id.product_tmpl_id.uom_id._get_unece_code(),
                'gross_price_total_unit':line._prepare_edi_vals_to_export()['gross_price_total_unit']
            }

            fortax_resintaxes_res['taxes']:
                tax=self.env['account.tax'].browse(tax_res['id'])
                tax_category_code=tax._get_unece_category_code(invoice.commercial_partner_id,invoice.company_id)
                line_template_values['tax_details'].append({
                    'tax':tax,
                    'tax_amount':tax_res['amount'],
                    'tax_base_amount':tax_res['base'],
                    'unece_tax_category_code':tax_category_code,
                })

            template_values['invoice_line_values'].append(line_template_values)

        template_values['tax_details']=list(aggregated_taxes_details.values())

        xml_content=b"<?xmlversion='1.0'encoding='UTF-8'?>"
        xml_content+=self.env.ref('account_edi_facturx.account_invoice_facturx_export')._render(template_values)
        returnself.env['ir.attachment'].create({
            'name':'factur-x.xml',
            'datas':base64.encodebytes(xml_content),
            'mimetype':'application/xml'
        })

    def_is_facturx(self,filename,tree):
        returnself.code=='facturx_1_0_05'andtree.tag=='{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice'

    def_create_invoice_from_xml_tree(self,filename,tree,journal=None):
        self.ensure_one()
        ifself._is_facturx(filename,tree)andnotself._is_account_edi_ubl_cii_available():
            returnself._import_facturx(tree,self.env['account.move'])
        returnsuper()._create_invoice_from_xml_tree(filename,tree,journal=journal)

    def_update_invoice_from_xml_tree(self,filename,tree,invoice):
        self.ensure_one()
        ifself._is_facturx(filename,tree)andnotself._is_account_edi_ubl_cii_available():
            returnself._import_facturx(tree,invoice)
        returnsuper()._update_invoice_from_xml_tree(filename,tree,invoice)

    def_import_facturx(self,tree,invoice):
        """Decodesafactur-xinvoiceintoaninvoice.

        :paramtree:   thefactur-xtreetodecode.
        :paraminvoice:theinvoicetoupdateoranemptyrecordset.
        :returns:      theinvoicewherethefactur-xdatawasimported.
        """

        def_find_value(xpath,element=tree):
            returnself._find_value(xpath,element,tree.nsmap)

        amount_total_import=None

        default_move_type=False
        ifinvoice._context.get('default_journal_id'):
            journal=self.env['account.journal'].browse(self.env.context['default_journal_id'])
            default_move_type='out_invoice'ifjournal.type=='sale'else'in_invoice'
        elifinvoice._context.get('default_move_type'):
            default_move_type=self._context['default_move_type']
        elifinvoice.move_typeinself.env['account.move'].get_invoice_types(include_receipts=True):
            #incaseanattachmentissavedonadraftinvoicepreviouslycreated,wemight
            #havelostthedefaultvalueincontextbutthetypewasalreadyset
            default_move_type=invoice.move_type

        ifnotdefault_move_type:
            raiseUserError(_("Noinformationaboutthejournalorthetypeofinvoiceispassed"))
        ifdefault_move_type=='entry':
            return

        #Totalamount.
        elements=tree.xpath('//ram:GrandTotalAmount',namespaces=tree.nsmap)
        total_amount=elementsandfloat(elements[0].text)or0.0

        #Refundtype.
        #ThereistwomodestohandlerefundinFactur-X:
        #a)type_code==380forinvoice,type_code==381forrefund,allpositiveamounts.
        #b)type_code==380,negativeamountsincaseofrefund.
        #Tohandleboth,weconsiderthe'a'modeandswitchto'b'ifanegativeamountisencountered.
        elements=tree.xpath('//rsm:ExchangedDocument/ram:TypeCode',namespaces=tree.nsmap)
        type_code=elements[0].text

        default_move_type.replace('_refund','_invoice')
        iftype_code=='381':
            default_move_type='out_refund'ifdefault_move_type=='out_invoice'else'in_refund'
            refund_sign=-1
        else:
            #Handle'b'refundmode.
            iftotal_amount<0:
                default_move_type='out_refund'ifdefault_move_type=='out_invoice'else'in_refund'
            refund_sign=-1if'refund'indefault_move_typeelse1

        #Writethetypeasthejournalentryisalreadycreated.
        invoice.move_type=default_move_type

        #selfcouldbeasinglerecord(editing)orbeempty(new).
        withForm(invoice.with_context(default_move_type=default_move_type))asinvoice_form:
            self_ctx=self.with_company(invoice.company_id)

            #Partner(firststeptoavoidwarning'Warning!Youmustfirstselectapartner.').
            partner_type=invoice_form.journal_id.type=='purchase'and'SellerTradeParty'or'BuyerTradeParty'
            invoice_form.partner_id=self_ctx._retrieve_partner(
                name=self._find_value('//ram:'+partner_type+'/ram:Name',tree,namespaces=tree.nsmap),
                mail=self._find_value('//ram:'+partner_type+'//ram:URIID[@schemeID=\'SMTP\']',tree,namespaces=tree.nsmap),
                vat=self._find_value('//ram:'+partner_type+'/ram:SpecifiedTaxRegistration/ram:ID',tree,namespaces=tree.nsmap),
            )

            #Reference.
            elements=tree.xpath('//rsm:ExchangedDocument/ram:ID',namespaces=tree.nsmap)
            ifelements:
                invoice_form.ref=elements[0].text

            #Name.
            elements=tree.xpath('//ram:BuyerOrderReferencedDocument/ram:IssuerAssignedID',namespaces=tree.nsmap)
            ifelements:
                invoice_form.payment_reference=elements[0].text

            #Comment.
            elements=tree.xpath('//ram:IncludedNote/ram:Content',namespaces=tree.nsmap)
            ifelements:
                invoice_form.narration=elements[0].text

            #Getcurrencystringfornewinvoices,orinvoicescomingfromoutside
            elements=tree.xpath('//ram:InvoiceCurrencyCode',namespaces=tree.nsmap)
            ifelements:
                currency_str=elements[0].text
            #FallbackforoldinvoicesfromflectrawheretheInvoiceCurrencyCodewasnotpresent
            else:
                elements=tree.xpath('//ram:TaxTotalAmount',namespaces=tree.nsmap)
                ifelements:
                    currency_str=elements[0].attrib['currencyID']

            currency=self.env.ref('base.%s'%currency_str.upper(),raise_if_not_found=False)
            ifcurrencyandnotcurrency.active:
                error_msg=_('Thecurrency(%s)ofthedocumentyouareuploadingisnotactiveinthisdatabase.\n'
                              'Pleaseactivateitbeforetryingagaintoimport.',currency.name)
                error_action={
                    'view_mode':'form',
                    'res_model':'res.currency',
                    'type':'ir.actions.act_window',
                    'target':'new',
                    'res_id':currency.id,
                    'views':[[False,'form']]
                }
                raiseRedirectWarning(error_msg,error_action,_('Displaythecurrency'))
            ifcurrency!=self.env.company.currency_idandcurrency.active:
                invoice_form.currency_id=currency

            #Storexmltotalamount.
            amount_total_import=total_amount*refund_sign

            #Date.
            elements=tree.xpath('//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString',namespaces=tree.nsmap)
            ifelements:
                date_str=elements[0].text
                date_obj=datetime.strptime(date_str,DEFAULT_FACTURX_DATE_FORMAT)
                invoice_form.invoice_date=date_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)

            #Duedate.
            elements=tree.xpath('//ram:SpecifiedTradePaymentTerms/ram:DueDateDateTime/udt:DateTimeString',namespaces=tree.nsmap)
            ifelements:
                date_str=elements[0].text
                date_obj=datetime.strptime(date_str,DEFAULT_FACTURX_DATE_FORMAT)
                invoice_form.invoice_date_due=date_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)

            #Invoicelines.
            elements=tree.xpath('//ram:IncludedSupplyChainTradeLineItem',namespaces=tree.nsmap)
            ifelements:
                forelementinelements:
                    withinvoice_form.invoice_line_ids.new()asinvoice_line_form:

                        #Sequence.
                        line_elements=element.xpath('.//ram:AssociatedDocumentLineDocument/ram:LineID',namespaces=tree.nsmap)
                        ifline_elements:
                            invoice_line_form.sequence=int(line_elements[0].text)

                        #Product.
                        name=_find_value('.//ram:SpecifiedTradeProduct/ram:Name',element)
                        invoice_line_form.product_id=self_ctx._retrieve_product(
                            default_code=_find_value('.//ram:SpecifiedTradeProduct/ram:SellerAssignedID',element),
                            name=_find_value('.//ram:SpecifiedTradeProduct/ram:Name',element),
                            barcode=_find_value('.//ram:SpecifiedTradeProduct/ram:GlobalID',element)
                        )
                        #forceoriginallinedescriptioninsteadoftheonecopiedfromproduct'sSalesDescription
                        ifname:
                            invoice_line_form.name=name

                        #Quantity.
                        line_elements=element.xpath('.//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity',namespaces=tree.nsmap)
                        ifline_elements:
                            invoice_line_form.quantity=float(line_elements[0].text)

                        #PriceUnit.
                        line_elements=element.xpath('.//ram:GrossPriceProductTradePrice/ram:ChargeAmount',namespaces=tree.nsmap)
                        ifline_elements:
                            quantity_elements=element.xpath('.//ram:GrossPriceProductTradePrice/ram:BasisQuantity',namespaces=tree.nsmap)
                            ifquantity_elements:
                                invoice_line_form.price_unit=float(line_elements[0].text)/float(quantity_elements[0].text)
                            else:
                                invoice_line_form.price_unit=float(line_elements[0].text)
                            #ForGrossprice,weneedtocheckifadiscountmustbetakenintoaccount
                            discount_elements=element.xpath('.//ram:AppliedTradeAllowanceCharge',
                                                          namespaces=tree.nsmap)
                            ifdiscount_elements:
                                discount_percent_elements=element.xpath(
                                    './/ram:AppliedTradeAllowanceCharge/ram:CalculationPercent',namespaces=tree.nsmap)
                                ifdiscount_percent_elements:
                                    invoice_line_form.discount=float(discount_percent_elements[0].text)
                                else:
                                    #ifdiscountnotavailable,itwillbecomputedfromthegrossandnetprices.
                                    net_price_elements=element.xpath('.//ram:NetPriceProductTradePrice/ram:ChargeAmount',
                                                                  namespaces=tree.nsmap)
                                    ifnet_price_elements:
                                        quantity_elements=element.xpath(
                                            './/ram:NetPriceProductTradePrice/ram:BasisQuantity',namespaces=tree.nsmap)
                                        net_unit_price=float(net_price_elements[0].text)/float(quantity_elements[0].text)\
                                            ifquantity_elementselsefloat(net_price_elements[0].text)
                                        invoice_line_form.discount=(invoice_line_form.price_unit-net_unit_price)/invoice_line_form.price_unit*100.0
                        else:
                            line_elements=element.xpath('.//ram:NetPriceProductTradePrice/ram:ChargeAmount',namespaces=tree.nsmap)
                            ifline_elements:
                                quantity_elements=element.xpath('.//ram:NetPriceProductTradePrice/ram:BasisQuantity',namespaces=tree.nsmap)
                                ifquantity_elements:
                                    invoice_line_form.price_unit=float(line_elements[0].text)/float(quantity_elements[0].text)
                                else:
                                    invoice_line_form.price_unit=float(line_elements[0].text)

                        #Taxes
                        tax_element=element.xpath('.//ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:RateApplicablePercent',namespaces=tree.nsmap)
                        invoice_line_form.tax_ids.clear()
                        forelineintax_element:
                            tax=self_ctx._retrieve_tax(
                                amount=eline.text,
                                type_tax_use=invoice_form.journal_id.type
                            )
                            iftax:
                                invoice_line_form.tax_ids.add(tax)
            elifamount_total_import:
                #NolinesinBASICWL.
                withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                    invoice_line_form.name=invoice_form.commentor'/'
                    invoice_line_form.quantity=1
                    invoice_line_form.price_unit=amount_total_import

        returninvoice_form.save()
