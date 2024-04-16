#-*-coding:utf-8-*-

fromflectraimportmodels,_
fromflectra.toolsimporthtml2plaintext,cleanup_xml_node
fromlxmlimportetree


classAccountEdiXmlUBL20(models.AbstractModel):
    _name="account.edi.xml.ubl_20"
    _inherit='account.edi.common'
    _description="UBL2.0"

    #-------------------------------------------------------------------------
    #EXPORT
    #-------------------------------------------------------------------------

    def_export_invoice_filename(self,invoice):
        returnf"{invoice.name.replace('/','_')}_ubl_20.xml"

    def_export_invoice_ecosio_schematrons(self):
        return{
            'invoice':'org.oasis-open:invoice:2.0',
            'credit_note':'org.oasis-open:creditnote:2.0',
        }

    def_get_country_vals(self,country):
        return{
            'country':country,

            'identification_code':country.code,
            'name':country.name,
        }

    def_get_partner_party_identification_vals_list(self,partner):
        return[]

    def_get_partner_address_vals(self,partner):
        return{
            'street_name':partner.street,
            'additional_street_name':partner.street2,
            'city_name':partner.city,
            'postal_zone':partner.zip,
            'country_subentity':partner.state_id.name,
            'country_subentity_code':partner.state_id.code,
            'country_vals':self._get_country_vals(partner.country_id),
        }

    def_get_partner_party_tax_scheme_vals_list(self,partner,role):
        return[{
            'registration_name':partner.name,
            'company_id':partner.vat,
            'registration_address_vals':self._get_partner_address_vals(partner),
            'TaxScheme_vals':{},
            'tax_scheme_id':'VAT',
        }]

    def_get_partner_party_legal_entity_vals_list(self,partner):
        commercial_partner=partner.commercial_partner_id

        return[{
            'commercial_partner':commercial_partner,

            'registration_name':commercial_partner.name,
            'company_id':commercial_partner.vat,
            'registration_address_vals':self._get_partner_address_vals(commercial_partner),
        }]

    def_get_partner_contact_vals(self,partner):
        return{
            'id':partner.id,
            'name':partner.name,
            'telephone':partner.phoneorpartner.mobile,
            'electronic_mail':partner.email,
        }

    def_get_partner_party_vals(self,partner,role):
        return{
            'partner':partner,
            'party_identification_vals':self._get_partner_party_identification_vals_list(partner),
            'party_name_vals':[{'name':partner.name}],
            'postal_address_vals':self._get_partner_address_vals(partner),
            'party_tax_scheme_vals':self._get_partner_party_tax_scheme_vals_list(partner,role),
            'party_legal_entity_vals':self._get_partner_party_legal_entity_vals_list(partner),
            'contact_vals':self._get_partner_contact_vals(partner),
        }

    def_get_invoice_period_vals_list(self,invoice):
        """
        Fornow,wecannotfillthisdatafromaninvoice
        Thiscorrespondstothe'deliveryorinvoiceperiod'.ForUBLBis3,inthecaseofintra-communitysupply,
        theActualdeliverydate(BT-72)ortheInvoicingperiod(BG-14)shouldbepresentundertheform:
        {
            'start_date':str,
            'end_date':str,
        }.
        """
        return[]

    def_get_delivery_vals_list(self,invoice):
        #thedataisoptional,exceptforublbis3(seetheoverride,whereweneedtosetadefaultdeliveryaddress)
        if'partner_shipping_id'ininvoice._fields:
            return[{
                'actual_delivery_date':None,
                'delivery_location_vals':{
                    'delivery_address_vals':self._get_partner_address_vals(invoice.partner_shipping_id),
                },
            }]
        else:
            return[]

    def_get_bank_address_vals(self,bank):
        return{
            'street_name':bank.street,
            'additional_street_name':bank.street2,
            'city_name':bank.city,
            'postal_zone':bank.zip,
            'country_subentity':bank.state.name,
            'country_subentity_code':bank.state.code,
            'country_vals':self._get_country_vals(bank.country),
        }

    def_get_financial_institution_vals(self,bank):
        return{
            'bank':bank,
            'id':bank.bic,
            'id_attrs':{'schemeID':'BIC'},
            'name':bank.name,
            'address_vals':self._get_bank_address_vals(bank),
        }

    def_get_financial_institution_branch_vals(self,bank):
        return{
            'bank':bank,
            'id':bank.bic,
            'id_attrs':{'schemeID':'BIC'},
            'financial_institution_vals':self._get_financial_institution_vals(bank),
        }

    def_get_financial_account_vals(self,partner_bank):
        vals={
            'bank_account':partner_bank,
            'id':partner_bank.acc_number.replace('',''),
        }

        ifpartner_bank.bank_id:
            vals['financial_institution_branch_vals']=self._get_financial_institution_branch_vals(partner_bank.bank_id)

        returnvals

    def_get_invoice_payment_means_vals_list(self,invoice):
        vals={
            'payment_means_code':30,
            'payment_means_code_attrs':{'name':'credittransfer'},
            'payment_due_date':invoice.invoice_date_dueorinvoice.invoice_date,
            'instruction_id':invoice.payment_reference,
            'payment_id_vals':[invoice.payment_referenceorinvoice.name],
        }

        ifinvoice.partner_bank_id:
            vals['payee_financial_account_vals']=self._get_financial_account_vals(invoice.partner_bank_id)

        return[vals]

    def_get_invoice_payment_terms_vals_list(self,invoice):
        payment_term=invoice.invoice_payment_term_id
        ifpayment_term:
            return[{'note_vals':[payment_term.name]}]
        else:
            return[]

    def_get_invoice_tax_totals_vals_list(self,invoice,taxes_vals):
        balance_sign=-1ifinvoice.is_inbound()else1
        tax_totals_vals={
            'currency':invoice.currency_id,
            'currency_dp':invoice.currency_id.decimal_places,
            'tax_amount':balance_sign*taxes_vals['tax_amount_currency'],
            'tax_subtotal_vals':[],
        }
        forgrouping_key,valsintaxes_vals['tax_details'].items():
            ifgrouping_key['tax_amount_type']!='fixed':
                tax_totals_vals['tax_subtotal_vals'].append({
                    'currency':invoice.currency_id,
                    'currency_dp':invoice.currency_id.decimal_places,
                    'taxable_amount':balance_sign*vals['base_amount_currency'],
                    'tax_amount':balance_sign*vals['tax_amount_currency'],
                    'percent':vals['_tax_category_vals_']['percent'],
                    'tax_category_vals':vals['_tax_category_vals_'],
                })
        return[tax_totals_vals]

    def_get_invoice_line_item_vals(self,line,taxes_vals):
        """Methodusedtofillthecac:InvoiceLine/cac:Itemnode.
        Itprovidesinformationaboutwhattheproductyouareselling.

        :paramline:       Aninvoiceline.
        :paramtaxes_vals: Thetaxdetailsforthecurrentinvoiceline.
        :return:           Apythondictionary.

        """
        product=line.product_id
        taxes=line.tax_ids.flatten_taxes_hierarchy().filtered(lambdat:t.amount_type!='fixed')
        tax_category_vals_list=self._get_tax_category_list(line.move_id,taxes)
        description=line.nameandline.name.replace('\n',',')

        return{
            #Simpledescriptionaboutwhatyouareselling.
            'description':description,

            #Thenameoftheitem.
            'name':product.name,

            #Identifieroftheproduct.
            'sellers_item_identification_vals':{'id':product.code},

            #Themaintaxapplied.Onlyoneisallowed.
            'classified_tax_category_vals':tax_category_vals_list,
        }

    def_get_document_allowance_charge_vals_list(self,invoice):
        """
        https://docs.peppol.eu/poacc/billing/3.0/bis/#_document_level_allowance_or_charge
        """
        return[]

    def_get_invoice_line_allowance_vals_list(self,line,tax_values_list=None):
        """Methodusedtofillthecac:InvoiceLine>cac:AllowanceChargenode.

        AllowancesaredistinguishedfromchargesusingtheChargeIndicatornodewith'false'asvalue.

        NotethatallowancechargesdonotexistforcreditnotesinUBL2.0,soifweapplydiscountinFlectra
        thenetpricewillnotbeconsistentwiththeunitprice,butwecannotdoanythingaboutit

        :paramline:   Aninvoiceline.
        :return:       Alistofpythondictionaries.
        """
        fixed_tax_charge_vals_list=[]
        balance_sign=-1ifline.move_id.is_inbound()else1
        forgrouping_key,tax_detailsintax_values_list['tax_details'].items():
            ifgrouping_key['tax_amount_type']=='fixed':
                fixed_tax_charge_vals_list.append({
                    'currency_name':line.currency_id.name,
                    'currency_dp':line.currency_id.decimal_places,
                    'charge_indicator':'true',
                    'allowance_charge_reason_code':'AEO',
                    'allowance_charge_reason':tax_details['group_tax_details'][0]['tax_id'].name,
                    'amount':balance_sign*tax_details['tax_amount_currency'],
                })

        ifnotline.discount:
            returnfixed_tax_charge_vals_list

        #Pricesubtotalwithoutdiscount:
        net_price_subtotal=line.price_subtotal
        #Pricesubtotalwithdiscount:
        ifline.discount==100.0:
            gross_price_subtotal=0.0
        else:
            gross_price_subtotal=line.currency_id.round(net_price_subtotal/(1.0-(line.discountor0.0)/100.0))

        allowance_vals={
            'currency_name':line.currency_id.name,
            'currency_dp':line.currency_id.decimal_places,

            #Mustbe'false'sincethismethodisforallowances.
            'charge_indicator':'false',

            #Areasonshouldbeprovided.InFlectra,weonlymanagediscounts.
            #Fullcodelistisavailablehere:
            #https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5189/
            'allowance_charge_reason_code':95,

            #Thediscountshouldbeprovidedasanamount.
            'amount':gross_price_subtotal-net_price_subtotal,
        }

        return[allowance_vals]+fixed_tax_charge_vals_list

    def_get_invoice_line_price_vals(self,line):
        """Methodusedtofillthecac:InvoiceLine/cac:Pricenode.
        Itprovidesinformationaboutthepriceappliedforthegoodsandservicesinvoiced.

        :paramline:   Aninvoiceline.
        :return:       Apythondictionary.
        """
        #Pricesubtotalwithoutdiscount:
        net_price_subtotal=line.price_subtotal
        #Pricesubtotalwithdiscount:
        ifline.discount==100.0:
            gross_price_subtotal=0.0
        else:
            gross_price_subtotal=net_price_subtotal/(1.0-(line.discountor0.0)/100.0)
        #Pricesubtotalwithdiscount/quantity:
        gross_price_unit=gross_price_subtotal/line.quantityifline.quantityelse0.0

        uom=super()._get_uom_unece_code(line)

        return{
            'currency':line.currency_id,
            'currency_dp':line.currency_id.decimal_places,

            #Thepriceofanitem,exclusiveofVAT,aftersubtractingitempricediscount.
            'price_amount':gross_price_unit,
            'product_price_dp':self.env['decimal.precision'].precision_get('ProductPrice'),

            #Thenumberofitemunitstowhichthepriceapplies.
            #settingtoNone->thexmlwillnotcomprisetheBaseQuantity(it'snotmandatory)
            'base_quantity':None,
            'base_quantity_attrs':{'unitCode':uom},
        }

    def_get_invoice_line_vals(self,line,taxes_vals):
        """Methodusedtofillthecac:InvoiceLinenode.
        Itprovidesinformationabouttheinvoiceline.

        :paramline:   Aninvoiceline.
        :return:       Apythondictionary.
        """
        allowance_charge_vals_list=self._get_invoice_line_allowance_vals_list(line,taxes_vals)

        uom=super()._get_uom_unece_code(line)
        total_fixed_tax_amount=sum([
            vals['amount']
            forvalsinallowance_charge_vals_list
            ifvals['allowance_charge_reason_code']=='AEO'
        ])
        return{
            'currency':line.currency_id,
            'currency_dp':line.currency_id.decimal_places,
            'invoiced_quantity':line.quantity,
            'invoiced_quantity_attrs':{'unitCode':uom},
            'line_extension_amount':line.price_subtotal+total_fixed_tax_amount,
            'allowance_charge_vals':allowance_charge_vals_list,
            'tax_total_vals':self._get_invoice_tax_totals_vals_list(line.move_id,taxes_vals),
            'item_vals':self._get_invoice_line_item_vals(line,taxes_vals),
            'price_vals':self._get_invoice_line_price_vals(line),
        }

    def_export_invoice_vals(self,invoice):
        defgrouping_key_generator(tax_values):
            tax=tax_values['tax_id']
            tax_category_vals=self._get_tax_category_list(invoice,tax)[0]
            grouping_key={
                'tax_category_id':tax_category_vals['id'],
                'tax_category_percent':tax_category_vals['percent'],
                '_tax_category_vals_':tax_category_vals,
                'tax_amount_type':tax.amount_type,
            }
            #Ifthetaxisfixed,wewanttohaveonegrouppertax
            #s.t.whentheinvoiceisimported,wecantrytoguessthefixedtaxes
            iftax.amount_type=='fixed':
                grouping_key['tax_name']=tax.name
            returngrouping_key

        #Validatethestructureofthetaxes
        self._validate_taxes(invoice)

        #Computethetaxdetailsforthewholeinvoiceandeachinvoicelineseparately.
        taxes_vals=invoice._prepare_edi_tax_details(grouping_key_generator=grouping_key_generator)

        #FixedTaxes:filterthemonthedocumentlevel,andadaptthetotals
        #Fixedtaxesarenotsupposedtobetaxesinreallive.However,thisisthewayinFlectratomanagerecupel
        #taxesinBelgium.Sinceonlyonetaxisallowed,thefixedtaxisremovedfromtotalsoflinesbutadded
        #asanextracharge/allowance.
        fixed_taxes_keys=[kforkintaxes_vals['tax_details']ifk['tax_amount_type']=='fixed']
        forkeyinfixed_taxes_keys:
            fixed_tax_details=taxes_vals['tax_details'].pop(key)
            taxes_vals['tax_amount_currency']-=fixed_tax_details['tax_amount_currency']
            taxes_vals['tax_amount']-=fixed_tax_details['tax_amount']
            taxes_vals['base_amount_currency']+=fixed_tax_details['tax_amount_currency']
            taxes_vals['base_amount']+=fixed_tax_details['tax_amount']

        #Computevaluesforinvoicelines.
        line_extension_amount=0.0

        invoice_lines=invoice.invoice_line_ids.filtered(lambdaline:notline.display_type)
        document_allowance_charge_vals_list=self._get_document_allowance_charge_vals_list(invoice)
        invoice_line_vals_list=[]
        forline_id,lineinenumerate(invoice_lines):
            line_taxes_vals=taxes_vals['invoice_line_tax_details'][line]
            line_vals=self._get_invoice_line_vals(line,line_taxes_vals)
            ifnotline_vals.get('id'):
                line_vals['id']=line_id+1
            invoice_line_vals_list.append(line_vals)

            line_extension_amount+=line_vals['line_extension_amount']

        #Computethetotalallowance/chargeamounts.
        allowance_total_amount=0.0
        forallowance_charge_valsindocument_allowance_charge_vals_list:
            ifallowance_charge_vals['charge_indicator']=='false':
                allowance_total_amount+=allowance_charge_vals['amount']

        supplier=invoice.company_id.partner_id.commercial_partner_id
        customer=invoice.commercial_partner_id

        #OrderReference/SalesOrderID(sales_order_id)isoptional
        sales_order_id='sale_line_ids'ininvoice.invoice_line_ids._fields\
                         and",".join(invoice.invoice_line_ids.sale_line_ids.order_id.mapped('name'))
        #OrderReference/ID(order_reference)ismandatoryinsidetheOrderReferencenode!
        order_reference=invoice.reforinvoice.nameifsales_order_idelseinvoice.ref

        balance_sign=-1ifinvoice.is_inbound()else1
        vals={
            'builder':self,
            'invoice':invoice,
            'supplier':supplier,
            'customer':customer,

            'taxes_vals':taxes_vals,

            'format_float':self.format_float,
            'AddressType_template':'account_edi_ubl_cii.ubl_20_AddressType',
            'ContactType_template':'account_edi_ubl_cii.ubl_20_ContactType',
            'PartyType_template':'account_edi_ubl_cii.ubl_20_PartyType',
            'PaymentMeansType_template':'account_edi_ubl_cii.ubl_20_PaymentMeansType',
            'TaxCategoryType_template':'account_edi_ubl_cii.ubl_20_TaxCategoryType',
            'TaxTotalType_template':'account_edi_ubl_cii.ubl_20_TaxTotalType',
            'AllowanceChargeType_template':'account_edi_ubl_cii.ubl_20_AllowanceChargeType',
            'InvoiceLineType_template':'account_edi_ubl_cii.ubl_20_InvoiceLineType',
            'InvoiceType_template':'account_edi_ubl_cii.ubl_20_InvoiceType',

            'vals':{
                'ubl_version_id':2.0,
                'id':invoice.name,
                'issue_date':invoice.invoice_date,
                'due_date':invoice.invoice_date_due,
                'note_vals':[html2plaintext(invoice.narration)]ifinvoice.narrationelse[],
                'order_reference':order_reference,
                'sales_order_id':sales_order_id,
                'accounting_supplier_party_vals':{
                    'party_vals':self._get_partner_party_vals(supplier,role='supplier'),
                },
                'accounting_customer_party_vals':{
                    'party_vals':self._get_partner_party_vals(customer,role='customer'),
                },
                'invoice_period_vals_list':self._get_invoice_period_vals_list(invoice),
                'delivery_vals_list':self._get_delivery_vals_list(invoice),
                'payment_means_vals_list':self._get_invoice_payment_means_vals_list(invoice),
                'payment_terms_vals':self._get_invoice_payment_terms_vals_list(invoice),
                #allowancesatthedocumentlevel,theallowancesoninvoices(eg.discount)areoninvoice_line_vals
                'allowance_charge_vals':document_allowance_charge_vals_list,
                'tax_total_vals':self._get_invoice_tax_totals_vals_list(invoice,taxes_vals),
                'legal_monetary_total_vals':{
                    'currency':invoice.currency_id,
                    'currency_dp':invoice.currency_id.decimal_places,
                    'line_extension_amount':line_extension_amount,
                    'tax_exclusive_amount':balance_sign*taxes_vals['base_amount_currency'],
                    'tax_inclusive_amount':invoice.amount_total,
                    'allowance_total_amount':allowance_total_amountorNone,
                    'prepaid_amount':invoice.amount_total-invoice.amount_residual,
                    'payable_amount':invoice.amount_residual,
                },
                'invoice_line_vals':invoice_line_vals_list,
                'currency_dp':invoice.currency_id.decimal_places, #currencydecimalplaces
            },
        }

        ifinvoice.move_type=='out_invoice':
            vals['main_template']='account_edi_ubl_cii.ubl_20_Invoice'
            vals['vals']['invoice_type_code']=380
        else:
            vals['main_template']='account_edi_ubl_cii.ubl_20_CreditNote'
            vals['vals']['credit_note_type_code']=381

        returnvals

    def_export_invoice_constraints(self,invoice,vals):
        constraints=self._invoice_constraints_common(invoice)
        constraints.update({
            'ubl20_supplier_name_required':self._check_required_fields(vals['supplier'],'name'),
            'ubl20_customer_name_required':self._check_required_fields(vals['customer'],'name'),
            'ubl20_commercial_customer_name_required':self._check_required_fields(vals['customer'].commercial_partner_id,'name'),
            'ubl20_invoice_name_required':self._check_required_fields(invoice,'name'),
            'ubl20_invoice_date_required':self._check_required_fields(invoice,'invoice_date'),
        })
        returnconstraints

    def_export_invoice(self,invoice):
        vals=self._export_invoice_vals(invoice)
        errors=[constraintforconstraintinself._export_invoice_constraints(invoice,vals).values()ifconstraint]
        xml_content=self.env['ir.qweb']._render(vals['main_template'],vals)
        returnetree.tostring(cleanup_xml_node(xml_content),xml_declaration=True,encoding='UTF-8'),set(errors)

    #-------------------------------------------------------------------------
    #IMPORT
    #-------------------------------------------------------------------------

    def_import_fill_invoice_form(self,journal,tree,invoice_form,qty_factor):
        logs=[]

        ifqty_factor==-1:
            logs.append(_("Theinvoicehasbeenconvertedintoacreditnoteandthequantitieshavebeenreverted."))

        #====partner_id====

        role="Customer"ifinvoice_form.journal_id.type=='sale'else"Supplier"
        vat=self._find_value(f'//cac:Accounting{role}Party/cac:Party//cbc:CompanyID',tree)
        phone=self._find_value(f'//cac:Accounting{role}Party/cac:Party//cbc:Telephone',tree)
        mail=self._find_value(f'//cac:Accounting{role}Party/cac:Party//cbc:ElectronicMail',tree)
        name=self._find_value(f'//cac:Accounting{role}Party/cac:Party//cbc:Name',tree)
        self._import_retrieve_and_fill_partner(invoice_form,name=name,phone=phone,mail=mail,vat=vat)

        #====currency_id====

        currency_code_node=tree.find('.//{*}DocumentCurrencyCode')
        ifcurrency_code_nodeisnotNone:
            currency=self.env['res.currency'].with_context(active_test=False).search([
                ('name','=',currency_code_node.text),
            ],limit=1)
            ifcurrency:
                ifnotcurrency.active:
                    logs.append(_("Thecurrency'%s'isnotactive.",currency.name))
                invoice_form.currency_id=currency
            else:
                logs.append(_("Couldnotretrievecurrency:%s.Didyouenablethemulticurrencyoption"
                              "andactivatethecurrency?",currency_code_node.text))

        #====Reference====

        ref_node=tree.find('./{*}ID')
        ifref_nodeisnotNone:
            invoice_form.ref=ref_node.text

        #===Note/narration====

        narration=""
        note_node=tree.find('./{*}Note')
        ifnote_nodeisnotNoneandnote_node.text:
            narration+=note_node.text+"\n"

        payment_terms_node=tree.find('./{*}PaymentTerms/{*}Note') #e.g.'Paymentwithin10days,2%discount'
        ifpayment_terms_nodeisnotNoneandpayment_terms_node.text:
            narration+=payment_terms_node.text+"\n"

        invoice_form.narration=narration

        #====payment_reference====

        payment_reference_node=tree.find('./{*}PaymentMeans/{*}PaymentID')
        ifpayment_reference_nodeisnotNone:
            invoice_form.payment_reference=payment_reference_node.text

        #====invoice_date====

        invoice_date_node=tree.find('./{*}IssueDate')
        ifinvoice_date_nodeisnotNone:
            invoice_form.invoice_date=invoice_date_node.text

        #====invoice_date_due====

        forxpathin('./{*}DueDate','.//{*}PaymentDueDate'):
            invoice_date_due_node=tree.find(xpath)
            ifinvoice_date_due_nodeisnotNone:
                invoice_form.invoice_date_due=invoice_date_due_node.text
                break

        #====invoice_incoterm_id====

        incoterm_code_node=tree.find('./{*}TransportExecutionTerms/{*}DeliveryTerms/{*}ID')
        ifincoterm_code_nodeisnotNone:
            incoterm=self.env['account.incoterms'].search([('code','=',incoterm_code_node.text)],limit=1)
            ifincoterm:
                invoice_form.invoice_incoterm_id=incoterm

        #====invoice_line_ids:AllowanceCharge(documentlevel)====

        logs+=self._import_fill_invoice_allowance_charge(tree,invoice_form,journal,qty_factor)

        #====Prepaidamount====

        prepaid_node=tree.find('./{*}LegalMonetaryTotal/{*}PrepaidAmount')
        logs+=self._import_log_prepaid_amount(invoice_form,prepaid_node,qty_factor)

        #====invoice_line_ids:InvoiceLine/CreditNoteLine====

        invoice_line_tag='InvoiceLine'ifinvoice_form.move_typein('in_invoice','out_invoice')orqty_factor==-1else'CreditNoteLine'
        fori,invl_elinenumerate(tree.findall('./{*}'+invoice_line_tag)):
            withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                invoice_line_form.sequence=i
                invl_logs=self._import_fill_invoice_line_form(journal,invl_el,invoice_form,invoice_line_form,qty_factor)
                logs+=invl_logs

        returninvoice_form,logs

    def_import_fill_invoice_line_form(self,journal,tree,invoice_form,invoice_line_form,qty_factor):
        logs=[]

        #Product.
        name=self._find_value('./cac:Item/cbc:Name',tree)
        invoice_line_form.product_id=self.env['account.edi.format']._retrieve_product(
            default_code=self._find_value('./cac:Item/cac:SellersItemIdentification/cbc:ID',tree),
            name=name,
            barcode=self._find_value("./cac:Item/cac:StandardItemIdentification/cbc:ID[@schemeID='0160']",tree),
        )
        #forceoriginallinedescriptioninsteadoftheonecopiedfromproduct'sSalesDescription
        ifname:
            invoice_line_form.name=name

        #Description
        description_node=tree.find('./{*}Item/{*}Description')
        name_node=tree.find('./{*}Item/{*}Name')
        ifdescription_nodeisnotNone:
            invoice_line_form.name=description_node.text
        elifname_nodeisnotNone:
            invoice_line_form.name=name_node.text #FallbackonNameifDescriptionisnotfound.

        xpath_dict={
            'basis_qty':[
                './{*}Price/{*}BaseQuantity',
            ],
            'gross_price_unit':'./{*}Price/{*}AllowanceCharge/{*}BaseAmount',
            'rebate':'./{*}Price/{*}AllowanceCharge/{*}Amount',
            'net_price_unit':'./{*}Price/{*}PriceAmount',
            'billed_qty': './{*}InvoicedQuantity'ifinvoice_form.move_typein('in_invoice','out_invoice')orqty_factor==-1else'./{*}CreditedQuantity',
            'allowance_charge':'.//{*}AllowanceCharge',
            'allowance_charge_indicator':'./{*}ChargeIndicator',
            'allowance_charge_amount':'./{*}Amount',
            'allowance_charge_reason':'./{*}AllowanceChargeReason',
            'allowance_charge_reason_code':'./{*}AllowanceChargeReasonCode',
            'line_total_amount':'./{*}LineExtensionAmount',
        }
        inv_line_vals=self._import_fill_invoice_line_values(tree,xpath_dict,invoice_line_form,qty_factor)
        #retrievetaxnodes
        tax_nodes=tree.findall('.//{*}Item/{*}ClassifiedTaxCategory/{*}Percent')
        ifnottax_nodes:
            forelemintree.findall('.//{*}TaxTotal'):
                tax_nodes+=elem.findall('.//{*}TaxSubtotal/{*}Percent')
        returnself._import_fill_invoice_line_taxes(journal,tax_nodes,invoice_line_form,inv_line_vals,logs)

    #-------------------------------------------------------------------------
    #IMPORT:helpers
    #-------------------------------------------------------------------------

    def_get_import_document_amount_sign(self,filename,tree):
        """
        InUBL,aninvoicehastag'Invoice'andacreditnotehastag'CreditNote'.However,acreditnotecanbe
        expressedasaninvoicewithnegativeamounts.Forthiscase,weneedafactortotaketheopposite
        ofeachquantityintheinvoice.
        """
        iftree.tag=='{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice':
            amount_node=tree.find('.//{*}LegalMonetaryTotal/{*}TaxExclusiveAmount')
            ifamount_nodeisnotNoneandfloat(amount_node.text)<0:
                return('in_refund','out_refund'),-1
            return('in_invoice','out_invoice'),1
        iftree.tag=='{urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2}CreditNote':
            return('in_refund','out_refund'),1
        returnNone,None
