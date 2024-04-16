#-*-coding:utf-8-*-
fromflectraimportmodels,_
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT,float_repr,is_html_empty,html2plaintext,cleanup_xml_node
fromlxmlimportetree

fromdatetimeimportdatetime

importlogging

_logger=logging.getLogger(__name__)

DEFAULT_FACTURX_DATE_FORMAT='%Y%m%d'


classAccountEdiXmlCII(models.AbstractModel):
    _name="account.edi.xml.cii"
    _inherit='account.edi.common'
    _description="Factur-x/XRechnungCII2.2.0"

    def_export_invoice_filename(self,invoice):
        return"factur-x.xml"

    def_export_invoice_ecosio_schematrons(self):
        return{
            'invoice':'de.xrechnung:cii:2.2.0',
            'credit_note':'de.xrechnung:cii:2.2.0',
        }

    def_export_invoice_constraints(self,invoice,vals):
        constraints=self._invoice_constraints_common(invoice)
        constraints.update({
            #[BR-08]-AnInvoiceshallcontaintheSellerpostaladdress(BG-5).
            #[BR-09]-TheSellerpostaladdress(BG-5)shallcontainaSellercountrycode(BT-40).
            'seller_postal_address':self._check_required_fields(
                vals['record']['company_id']['partner_id']['commercial_partner_id'],'country_id'
            ),
            #[BR-DE-9]Theelement"Buyerpostcode"(BT-53)mustbetransmitted.(onlymandatoryinGermany?)
            'buyer_postal_address':self._check_required_fields(
                vals['record']['commercial_partner_id'],'zip'
            ),
            #[BR-DE-4]Theelement"Sellerpostcode"(BT-38)mustbetransmitted.(onlymandatoryinGermany?)
            'seller_post_code':self._check_required_fields(
                vals['record']['company_id']['partner_id']['commercial_partner_id'],'zip'
            ),
            #[BR-CO-26]-Inorderforthebuyertoautomaticallyidentifyasupplier,theSelleridentifier(BT-29),
            #theSellerlegalregistrationidentifier(BT-30)and/ortheSellerVATidentifier(BT-31)shallbepresent.
            'seller_identifier':self._check_required_fields(
                vals['record']['company_id'],['vat'] #'siret'
            ),
            #[BR-DE-1]AnInvoicemustcontaininformationon"PAYMENTINSTRUCTIONS"(BG-16)
            #firstcheckthatapartner_bank_idexists,thencheckthatthereisanaccountnumber
            'seller_payment_instructions_1':self._check_required_fields(
                vals['record'],'partner_bank_id'
            ),
            'seller_payment_instructions_2':self._check_required_fields(
                vals['record']['partner_bank_id'],'sanitized_acc_number',
                _("Thefield'SanitizedAccountNumber'isrequiredontheRecipientBank.")
            ),
            #[BR-DE-6]Theelement"Sellercontacttelephonenumber"(BT-42)mustbetransmitted.
            'seller_phone':self._check_required_fields(
                vals['record']['company_id']['partner_id']['commercial_partner_id'],['phone','mobile'],
            ),
            #[BR-DE-7]Theelement"Sellercontactemailaddress"(BT-43)mustbetransmitted.
            'seller_email':self._check_required_fields(
                vals['record']['company_id'],'email'
            ),
            #[BR-CO-04]-EachInvoiceline(BG-25)shallbecategorizedwithanInvoiceditemVATcategorycode(BT-151).
            'tax_invoice_line':self._check_required_tax(vals),
            #[BR-IC-02]-AnInvoicethatcontainsanInvoiceline(BG-25)wheretheInvoiceditemVATcategorycode(BT-151)
            #is"Intra-communitysupply"shallcontaintheSellerVATIdentifier(BT-31)ortheSellertaxrepresentative
            #VATidentifier(BT-63)andtheBuyerVATidentifier(BT-48).
            'intracom_seller_vat':self._check_required_fields(vals['record']['company_id'],'vat')ifvals['intracom_delivery']elseNone,
            'intracom_buyer_vat':self._check_required_fields(vals['record']['commercial_partner_id'],'vat')ifvals['intracom_delivery']elseNone,
            #[BR-IG-05]-InanInvoiceline(BG-25)wheretheInvoiceditemVATcategorycode(BT-151)is"IGIC"the
            #invoiceditemVATrate(BT-152)shallbegreaterthan0(zero).
            'igic_tax_rate':self._check_non_0_rate_tax(vals)
                ifvals['record']['commercial_partner_id']['country_id']['code']=='ES'
                    andvals['record']['commercial_partner_id']['zip']
                    andvals['record']['commercial_partner_id']['zip'][:2]in['35','38']elseNone,
        })
        returnconstraints

    def_check_required_tax(self,vals):
        forline_valsinvals['invoice_line_vals_list']:
            line=line_vals['line']
            ifnotvals['tax_details']['invoice_line_tax_details'][line]['tax_details']:
                return_("Youshouldincludeatleastonetaxperinvoiceline.[BR-CO-04]-EachInvoiceline(BG-25)"
                         "shallbecategorizedwithanInvoiceditemVATcategorycode(BT-151).")

    def_check_non_0_rate_tax(self,vals):
        forline_valsinvals['invoice_line_vals_list']:
            tax_rate_list=line_vals['line'].tax_ids.flatten_taxes_hierarchy().mapped("amount")
            ifnotany([rate>0forrateintax_rate_list]):
                return_("WhentheCanaryIslandGeneralIndirectTax(IGIC)applies,thetaxrateon"
                         "eachinvoicelineshouldbegreaterthan0.")

    def_get_scheduled_delivery_time(self,invoice):
        #don'tcreateabridgeonlytogetline.sale_line_ids.order_id.picking_ids.date_done
        #line.sale_line_ids.order_id.picking_ids.scheduled_dateorline.sale_line_ids.order_id.commitment_date
        returninvoice.invoice_date

    def_get_invoicing_period(self,invoice):
        #gettheInvoicingperiod(BG-14):alistofdatescoveredbytheinvoice
        #don'tcreateabridgetogetthedaterangefromthetimesheet_ids
        return[invoice.invoice_date]

    def_get_exchanged_document_vals(self,invoice):
        return{
            'id':invoice.name,
            'type_code':'380'ifinvoice.move_type=='out_invoice'else'381',
            'issue_date_time':invoice.invoice_date,
            'included_note':html2plaintext(invoice.narration)ifinvoice.narrationelse"",
        }

    def_export_invoice_vals(self,invoice):

        defformat_date(dt):
            #FormatthedateintheFactur-xstandard.
            dt=dtordatetime.now()
            returndt.strftime(DEFAULT_FACTURX_DATE_FORMAT)

        defformat_monetary(number,decimal_places=2):
            #Facturxrequiresthemonetaryvaluestoberoundedto2decimalvalues
            returnfloat_repr(number,decimal_places)

        defgrouping_key_generator(tax_values):
            tax=tax_values['tax_id']
            grouping_key={
                **self._get_tax_unece_codes(invoice,tax),
                'amount':tax.amount,
                'amount_type':tax.amount_type,
            }
            #Ifthetaxisfixed,wewanttohaveonegrouppertax
            #s.t.whentheinvoiceisimported,wecantrytoguessthefixedtaxes
            iftax.amount_type=='fixed':
                grouping_key['tax_name']=tax.name
            returngrouping_key

        #Validatethestructureofthetaxes
        self._validate_taxes(invoice)

        #Createfilecontent.
        tax_details=invoice._prepare_edi_tax_details(grouping_key_generator=grouping_key_generator)

        #FixedTaxes:filterthemonthedocumentlevel,andadaptthetotals
        #Fixedtaxesarenotsupposedtobetaxesinreallive.However,thisisthewayinFlectratomanagerecupel
        #taxesinBelgium.Sinceonlyonetaxisallowed,thefixedtaxisremovedfromtotalsoflinesbutadded
        #asanextracharge/allowance.
        fixed_taxes_keys=[kforkintax_details['tax_details']ifk['amount_type']=='fixed']
        forkeyinfixed_taxes_keys:
            fixed_tax_details=tax_details['tax_details'].pop(key)
            tax_details['tax_amount_currency']-=fixed_tax_details['tax_amount_currency']
            tax_details['tax_amount']-=fixed_tax_details['tax_amount']
            tax_details['base_amount_currency']+=fixed_tax_details['tax_amount_currency']
            tax_details['base_amount']+=fixed_tax_details['tax_amount']

        if'siret'ininvoice.company_id._fieldsandinvoice.company_id.siret:
            seller_siret=invoice.company_id.siret
        else:
            seller_siret=invoice.company_id.company_registry

        buyer_siret=False
        if'siret'ininvoice.commercial_partner_id._fieldsandinvoice.commercial_partner_id.siret:
            buyer_siret=invoice.commercial_partner_id.siret
        template_values={
            **invoice._prepare_edi_vals_to_export(),
            'tax_details':tax_details,
            'format_date':format_date,
            'format_monetary':format_monetary,
            'is_html_empty':is_html_empty,
            'scheduled_delivery_time':self._get_scheduled_delivery_time(invoice),
            'intracom_delivery':False,
            'ExchangedDocument_vals':self._get_exchanged_document_vals(invoice),
            'seller_specified_legal_organization':seller_siret,
            'buyer_specified_legal_organization':buyer_siret,
            'ship_to_trade_party':invoice.partner_shipping_idif'partner_shipping_id'ininvoice._fieldsandinvoice.partner_shipping_id
                elseinvoice.commercial_partner_id,
            #ChorusProfields
            'buyer_reference':invoice.buyer_referenceif'buyer_reference'ininvoice._fields
                andinvoice.buyer_referenceelseinvoice.commercial_partner_id.ref,
            'purchase_order_reference':invoice.purchase_order_referenceif'purchase_order_reference'ininvoice._fields
                andinvoice.purchase_order_referenceelseinvoice.reforinvoice.name,
            'contract_reference':invoice.contract_referenceif'contract_reference'ininvoice._fields
                andinvoice.contract_referenceelse'',
        }

        #datausedforIncludedSupplyChainTradeLineItem/SpecifiedLineTradeSettlement
        forline_valsintemplate_values['invoice_line_vals_list']:
            line=line_vals['line']
            line_vals['unece_uom_code']=self._get_uom_unece_code(line)

        #datausedforApplicableHeaderTradeSettlement/ApplicableTradeTax(attheendofthexml)
        fortax_detail_valsintemplate_values['tax_details']['tax_details'].values():
            #/!\-0.0==0.0inpythonbutnotinXSLT,soitcanraiseafatalerrorwhenvalidatingtheXML
            #if0.0isexpectedand-0.0isgiven.
            amount_currency=tax_detail_vals['tax_amount_currency']
            tax_detail_vals['calculated_amount']=template_values['balance_multiplicator']*amount_currency\
                ifnotinvoice.currency_id.is_zero(amount_currency)else0

            iftax_detail_vals.get('tax_category_code')=='K':
                template_values['intracom_delivery']=True
            #[BR-IC-11]-InanInvoicewithaVATbreakdown(BG-23)wheretheVATcategorycode(BT-118)is
            #"Intra-communitysupply"theActualdeliverydate(BT-72)ortheInvoicingperiod(BG-14)shallnotbeblank.
            iftax_detail_vals.get('tax_category_code')=='K'andnottemplate_values['scheduled_delivery_time']:
                date_range=self._get_invoicing_period(invoice)
                template_values['billing_start']=min(date_range)
                template_values['billing_end']=max(date_range)

        #OneofthedifferencebetweenXRechnungandFacturxisthefollowing.SubmittingaFacturxtoXRechnung
        #validatorraisesawarning,butsubmittingaXRechnungtoFacturxraisesanerror.
        supplier=invoice.company_id.partner_id.commercial_partner_id
        ifsupplier.country_id.code=='DE':
            template_values['document_context_id']="urn:cen.eu:en16931:2017#compliant#urn:xoev-de:kosit:standard:xrechnung_2.2"
        else:
            template_values['document_context_id']="urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended"

        #Fixedtaxes:addthemaschargesontheinvoicelines
        balance_sign=-1ifinvoice.is_inbound()else1
        forline_valsintemplate_values['invoice_line_vals_list']:
            line_vals['allowance_charge_vals_list']=[]
            forgrouping_key,tax_detailintax_details['invoice_line_tax_details'][line_vals['line']]['tax_details'].items():
                ifgrouping_key['amount_type']=='fixed':
                    line_vals['allowance_charge_vals_list'].append({
                        'indicator':'true',
                        'reason':tax_detail['group_tax_details'][0]['tax_id'].name,
                        'reason_code':'AEO',
                        'amount':balance_sign*tax_detail['tax_amount_currency'],
                    })
            sum_fixed_taxes=sum(x['amount']forxinline_vals['allowance_charge_vals_list'])
            line_vals['line_total_amount']=line_vals['line'].price_subtotal+sum_fixed_taxes

        #Fixedtaxes:setthetotaladjustedamountsonthedocumentlevel
        template_values['tax_basis_total_amount']=balance_sign*tax_details['base_amount_currency']
        template_values['tax_total_amount']=balance_sign*tax_details['tax_amount_currency']

        returntemplate_values

    def_export_invoice(self,invoice):
        vals=self._export_invoice_vals(invoice)
        errors=[constraintforconstraintinself._export_invoice_constraints(invoice,vals).values()ifconstraint]
        xml_content=self.env['ir.qweb']._render('account_edi_ubl_cii.account_invoice_facturx_export_22',vals)
        returnetree.tostring(cleanup_xml_node(xml_content),xml_declaration=True,encoding='UTF-8'),set(errors)

    #-------------------------------------------------------------------------
    #IMPORT
    #-------------------------------------------------------------------------

    def_import_fill_invoice_form(self,journal,tree,invoice_form,qty_factor):
        logs=[]

        ifqty_factor==-1:
            logs.append(_("Theinvoicehasbeenconvertedintoacreditnoteandthequantitieshavebeenreverted."))

        #====partner_id====

        role=invoice_form.journal_id.type=='purchase'and'SellerTradeParty'or'BuyerTradeParty'
        name=self._find_value(f"//ram:{role}/ram:Name",tree)
        mail=self._find_value(f"//ram:{role}//ram:URIID[@schemeID='SMTP']",tree)
        vat=self._find_value(f"//ram:{role}/ram:SpecifiedTaxRegistration/ram:ID",tree)
        phone=self._find_value(f"//ram:{role}/ram:DefinedTradeContact/ram:TelephoneUniversalCommunication/ram:CompleteNumber",tree)
        self._import_retrieve_and_fill_partner(invoice_form,name=name,phone=phone,mail=mail,vat=vat)

        #====currency_id====

        currency_code_node=tree.find('.//{*}InvoiceCurrencyCode')
        ifcurrency_code_nodeisnotNone:
            currency=self.env['res.currency'].with_context(active_test=False).search([
                ('name','=',currency_code_node.text),
            ],limit=1)
            ifcurrency:
                ifnotcurrency.active:
                    logs.append(_("Thecurrency'%s'isnotactive.",currency.name))
                invoice_form.currency_id=currency
            else:
                logs.append(_("Couldnotretrievecurrency:%s.Didyouenablethemulticurrencyoptionand"
                              "activatethecurrency?",currency_code_node.text))

        #====Reference====

        ref_node=tree.find('./{*}ExchangedDocument/{*}ID')
        ifref_nodeisnotNone:
            invoice_form.ref=ref_node.text

        #===Note/narration====

        narration=""
        note_node=tree.find('./{*}ExchangedDocument/{*}IncludedNote/{*}Content')
        ifnote_nodeisnotNoneandnote_node.text:
            narration+=note_node.text+"\n"

        payment_terms_node=tree.find('.//{*}SpecifiedTradePaymentTerms/{*}Description')
        ifpayment_terms_nodeisnotNoneandpayment_terms_node.text:
            narration+=payment_terms_node.text+"\n"

        invoice_form.narration=narration

        #====payment_reference====

        payment_reference_node=tree.find('.//{*}BuyerOrderReferencedDocument/{*}IssuerAssignedID')
        ifpayment_reference_nodeisnotNone:
            invoice_form.payment_reference=payment_reference_node.text

        #====invoice_date====

        invoice_date_node=tree.find('./{*}ExchangedDocument/{*}IssueDateTime/{*}DateTimeString')
        ifinvoice_date_nodeisnotNoneandinvoice_date_node.text:
            date_str=invoice_date_node.text.strip()
            date_obj=datetime.strptime(date_str,DEFAULT_FACTURX_DATE_FORMAT)
            invoice_form.invoice_date=date_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)

        #====invoice_date_due====

        invoice_date_due_node=tree.find('.//{*}SpecifiedTradePaymentTerms/{*}DueDateDateTime/{*}DateTimeString')
        ifinvoice_date_due_nodeisnotNoneandinvoice_date_due_node.text:
            date_str=invoice_date_due_node.text.strip()
            date_obj=datetime.strptime(date_str,DEFAULT_FACTURX_DATE_FORMAT)
            invoice_form.invoice_date_due=date_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)

        #====invoice_line_ids:AllowanceCharge(documentlevel)====

        logs+=self._import_fill_invoice_allowance_charge(tree,invoice_form,journal,qty_factor)

        #====Prepaidamount====

        prepaid_node=tree.find('.//{*}ApplicableHeaderTradeSettlement/'
                                 '{*}SpecifiedTradeSettlementHeaderMonetarySummation/{*}TotalPrepaidAmount')
        logs+=self._import_log_prepaid_amount(invoice_form,prepaid_node,qty_factor)

        #====invoice_line_ids====

        line_nodes=tree.findall('./{*}SupplyChainTradeTransaction/{*}IncludedSupplyChainTradeLineItem')
        ifline_nodesisnotNone:
            fori,invl_elinenumerate(line_nodes):
                withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                    invoice_line_form.sequence=i
                    invl_logs=self._import_fill_invoice_line_form(journal,invl_el,invoice_form,invoice_line_form,qty_factor)
                    logs+=invl_logs

        returninvoice_form,logs

    def_import_fill_invoice_line_form(self,journal,tree,invoice_form,invoice_line_form,qty_factor):
        logs=[]

        #Product.
        name=self._find_value('.//ram:SpecifiedTradeProduct/ram:Name',tree)
        invoice_line_form.product_id=self.env['account.edi.format']._retrieve_product(
            default_code=self._find_value('.//ram:SpecifiedTradeProduct/ram:SellerAssignedID',tree),
            name=name,
            barcode=self._find_value('.//ram:SpecifiedTradeProduct/ram:GlobalID',tree)
        )
        #forceoriginallinedescriptioninsteadoftheonecopiedfromproduct'sSalesDescription
        ifname:
            invoice_line_form.name=name

        xpath_dict={
            'basis_qty':[
                './{*}SpecifiedLineTradeAgreement/{*}GrossPriceProductTradePrice/{*}BasisQuantity',
                './{*}SpecifiedLineTradeAgreement/{*}NetPriceProductTradePrice/{*}BasisQuantity'
            ],
            'gross_price_unit':'./{*}SpecifiedLineTradeAgreement/{*}GrossPriceProductTradePrice/{*}ChargeAmount',
            'rebate':'./{*}SpecifiedLineTradeAgreement/{*}GrossPriceProductTradePrice/{*}AppliedTradeAllowanceCharge/{*}ActualAmount',
            'net_price_unit':'./{*}SpecifiedLineTradeAgreement/{*}NetPriceProductTradePrice/{*}ChargeAmount',
            'billed_qty':'./{*}SpecifiedLineTradeDelivery/{*}BilledQuantity',
            'allowance_charge':'.//{*}SpecifiedLineTradeSettlement/{*}SpecifiedTradeAllowanceCharge',
            'allowance_charge_indicator':'./{*}ChargeIndicator/{*}Indicator',
            'allowance_charge_amount':'./{*}ActualAmount',
            'allowance_charge_reason':'./{*}Reason',
            'allowance_charge_reason_code':'./{*}ReasonCode',
            'line_total_amount':'./{*}SpecifiedLineTradeSettlement/{*}SpecifiedTradeSettlementLineMonetarySummation/{*}LineTotalAmount',
        }
        inv_line_vals=self._import_fill_invoice_line_values(tree,xpath_dict,invoice_line_form,qty_factor)
        #retrievetaxnodes
        tax_nodes=tree.findall('.//{*}ApplicableTradeTax/{*}RateApplicablePercent')
        returnself._import_fill_invoice_line_taxes(journal,tax_nodes,invoice_line_form,inv_line_vals,logs)

    #-------------------------------------------------------------------------
    #IMPORT:helpers
    #-------------------------------------------------------------------------

    def_get_import_document_amount_sign(self,filename,tree):
        """
        Infactur-x,aninvoicehascode380andacreditnotehascode381.However,acreditnotecanbeexpressed
        asaninvoicewithnegativeamounts.Forthiscase,weneedafactortotaketheoppositeofeachquantity
        intheinvoice.
        """
        move_type_code=tree.find('.//{*}ExchangedDocument/{*}TypeCode')
        ifmove_type_codeisNone:
            returnNone,None
        ifmove_type_code.text=='381':
            return('in_refund','out_refund'),1
        ifmove_type_code.text=='380':
            amount_node=tree.find('.//{*}SpecifiedTradeSettlementHeaderMonetarySummation/{*}TaxBasisTotalAmount')
            ifamount_nodeisnotNoneandfloat(amount_node.text)<0:
                return('in_refund','out_refund'),-1
            return('in_invoice','out_invoice'),1
