#-*-coding:utf-8-*-

fromflectraimportmodels,_
fromflectra.addons.account_edi_ubl_cii.models.account_edi_commonimportCOUNTRY_EAS

fromstdnum.noimportmva


classAccountEdiXmlUBLBIS3(models.AbstractModel):
    _name="account.edi.xml.ubl_bis3"
    _inherit='account.edi.xml.ubl_21'
    _description="UBLBISBilling3.0.12"

    """
    *DocumentationofEHFBilling3.0:https://anskaffelser.dev/postaward/g3/
    *EHF2.0isnolongerused:
      https://anskaffelser.dev/postaward/g2/announcement/2019-11-14-removal-old-invoicing-specifications/
    *OfficialdocforEHFBilling3.0istheOpenPeppolBIS3doc+
      https://anskaffelser.dev/postaward/g3/spec/current/billing-3.0/norway/

        "BasedonworkdoneinPEPPOLBISBilling3.0,DifihasincludedNorwegianrulesinPEPPOLBISBilling3.0and
        doesnotseeaneedtoimplementadifferentCIUStargetingtheNorwegianmarket.ImplementationofEHFBilling
        3.0isthereforedonebyimplementingPEPPOLBISBilling3.0withoutextensionsorextrarules."

    Thus,EHF3andBis3areactuallythesameformat.ThespecificrulesforNOdefinedinBis3areaddedinBis3.
    """

    #-------------------------------------------------------------------------
    #EXPORT
    #-------------------------------------------------------------------------

    def_export_invoice_filename(self,invoice):
        returnf"{invoice.name.replace('/','_')}_ubl_bis3.xml"

    def_export_invoice_ecosio_schematrons(self):
        return{
            'invoice':'eu.peppol.bis3:invoice:3.13.0',
            'credit_note':'eu.peppol.bis3:creditnote:3.13.0',
        }

    def_get_country_vals(self,country):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_country_vals(country)

        vals.pop('name',None)

        returnvals

    def_get_partner_party_tax_scheme_vals_list(self,partner,role):
        #EXTENDSaccount.edi.xml.ubl_21
        vals_list=super()._get_partner_party_tax_scheme_vals_list(partner,role)

        ifnotpartner.vat:
            return[]

        forvalsinvals_list:
            vals.pop('registration_name',None)
            vals.pop('registration_address_vals',None)

            #/!\ForAustraliancompanies,theABNisencodedontheVATfield,butdoesn'thavethe2digitsprefix,
            #causingavalidationerror
            ifpartner.country_id.code=="AU"andpartner.vatandnotpartner.vat.upper().startswith("AU"):
                vals['company_id']="AU"+partner.vat

            ifpartner.country_id.code=="LU"and'l10n_lu_peppol_identifier'inpartner._fieldsandpartner.l10n_lu_peppol_identifier:
                vals['company_id']=partner.l10n_lu_peppol_identifier

        #sources:
        # https://anskaffelser.dev/postaward/g3/spec/current/billing-3.0/norway/#_applying_foretaksregisteret
        # https://docs.peppol.eu/poacc/billing/3.0/bis/#national_rules(NO-R-002(warning))
        ifpartner.country_id.code=="NO"androle=='supplier':
            vals_list.append({
                'company_id':"Foretaksregisteret",
                'tax_scheme_id':"TAX",
            })

        returnvals_list

    def_get_partner_party_legal_entity_vals_list(self,partner):
        #EXTENDSaccount.edi.xml.ubl_21
        vals_list=super()._get_partner_party_legal_entity_vals_list(partner)

        forvalsinvals_list:
            vals.pop('registration_address_vals',None)
            ifpartner.country_id.code=='NL'and'l10n_nl_oin'inpartner._fields:
                endpoint=partner.l10n_nl_oinorpartner.l10n_nl_kvk
                scheme='0190'ifpartner.l10n_nl_oinelse'0106'
                vals.update({
                    'company_id':endpoint,
                    'company_id_attrs':{'schemeID':scheme},
                })
            ifpartner.country_id.code=="LU"and'l10n_lu_peppol_identifier'inpartner._fieldsandpartner.l10n_lu_peppol_identifier:
                vals['company_id']=partner.l10n_lu_peppol_identifier
            ifpartner.country_id.code=='DK':
                #DK-R-014:ForDanishSuppliersitismandatorytospecifyschemeIDas"0184"(DKCVR-number)when
                #PartyLegalEntity/CompanyIDisusedforAccountingSupplierParty
                vals['company_id_attrs']={'schemeID':'0184'}

        returnvals_list

    def_get_partner_contact_vals(self,partner):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_partner_contact_vals(partner)

        vals.pop('id',None)

        returnvals

    def_get_partner_party_vals(self,partner,role):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_partner_party_vals(partner,role)

        vals['endpoint_id']=partner.vat
        vals['endpoint_id_attrs']={'schemeID':COUNTRY_EAS.get(partner.country_id.code)}

        ifpartner.country_id.code=='NO'and'l10n_no_bronnoysund_number'inpartner._fields:
            vals.update({
                'endpoint_id':partner.l10n_no_bronnoysund_number,
                'endpoint_id_attrs':{'schemeID':'0192'},
            })
        #[BR-NL-1]Dutchsupplierregistrationnumber(AccountingSupplierParty/Party/PartyLegalEntity/CompanyID);
        #WithaDutchsupplier(NL),SchemeIDmayonlycontain106(ChamberofCommercenumber)or190(OINnumber).
        #[BR-NL-10]AtaDutchsupplier,foraDutchcustomer(AccountingCustomerParty)thecustomerregistration
        #numbermustbefilledwithChamberofCommerceorOIN.SchemeIDmayonlycontain106(Chamberof
        #Commercenumber)or190(OINnumber).
        ifpartner.country_id.code=='NL'and'l10n_nl_oin'inpartner._fields:
            ifpartner.l10n_nl_oin:
                vals.update({
                    'endpoint_id':partner.l10n_nl_oin,
                    'endpoint_id_attrs':{'schemeID':'0190'},
                })
            elifpartner.l10n_nl_kvk:
                vals.update({
                    'endpoint_id':partner.l10n_nl_kvk,
                    'endpoint_id_attrs':{'schemeID':'0106'},
                })
        ifpartner.country_id.code=='SG'and'l10n_sg_unique_entity_number'inpartner._fields:
            vals.update({
                'endpoint_id':partner.l10n_sg_unique_entity_number,
                'endpoint_id_attrs':{'schemeID':'0195'},
            })
        ifpartner.country_id.code=="LU"and'l10n_lu_peppol_identifier'inpartner._fieldsandpartner.l10n_lu_peppol_identifier:
            vals['endpoint_id']=partner.l10n_lu_peppol_identifier

        returnvals

    def_get_partner_party_identification_vals_list(self,partner):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_partner_party_identification_vals_list(partner)

        ifpartner.country_id.code=='NL'and'l10n_nl_oin'inpartner._fields:
            endpoint=partner.l10n_nl_oinorpartner.l10n_nl_kvk
            vals.append({
                'id':endpoint,
            })
        returnvals

    def_get_delivery_vals_list(self,invoice):
        #EXTENDSaccount.edi.xml.ubl_21
        supplier=invoice.company_id.partner_id.commercial_partner_id
        customer=invoice.commercial_partner_id

        economic_area=self.env.ref('base.europe').country_ids.mapped('code')+['NO']
        intracom_delivery=(customer.country_id.codeineconomic_area
                             andsupplier.country_id.codeineconomic_area
                             andsupplier.country_id!=customer.country_id)

        ifnotintracom_delivery:
            return[]

        #[BR-IC-12]-InanInvoicewithaVATbreakdown(BG-23)wheretheVATcategorycode(BT-118)is
        #"Intra-communitysupply"theDelivertocountrycode(BT-80)shallnotbeblank.

        #[BR-IC-11]-InanInvoicewithaVATbreakdown(BG-23)wheretheVATcategorycode(BT-118)is
        #"Intra-communitysupply"theActualdeliverydate(BT-72)ortheInvoicingperiod(BG-14)
        #shallnotbeblank.

        if'partner_shipping_id'ininvoice._fields:
            partner_shipping=invoice.partner_shipping_id
        else:
            partner_shipping=customer

        return[{
            'actual_delivery_date':invoice.invoice_date,
            'delivery_location_vals':{
                'delivery_address_vals':self._get_partner_address_vals(partner_shipping),
            },
        }]

    def_get_partner_address_vals(self,partner):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_partner_address_vals(partner)
        #schematron/openpeppol/3.13.0/xslt/CEN-EN16931-UBL.xslt
        #[UBL-CR-225]-AUBLinvoiceshouldnotincludetheAccountingCustomerPartyPartyPostalAddressCountrySubentityCode
        vals.pop('country_subentity_code',None)
        returnvals

    def_get_financial_institution_branch_vals(self,bank):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_financial_institution_branch_vals(bank)
        #schematron/openpeppol/3.13.0/xslt/CEN-EN16931-UBL.xslt
        #[UBL-CR-664]-AUBLinvoiceshouldnotincludetheFinancialInstitutionBranchFinancialInstitution
        #xpathtest:not(//cac:FinancialInstitution)
        vals.pop('id_attrs',None)
        vals.pop('financial_institution_vals',None)
        returnvals

    def_get_invoice_payment_means_vals_list(self,invoice):
        #EXTENDSaccount.edi.xml.ubl_21
        vals_list=super()._get_invoice_payment_means_vals_list(invoice)

        forvalsinvals_list:
            vals.pop('payment_due_date',None)
            vals.pop('instruction_id',None)
            ifvals.get('payment_id_vals'):
                vals['payment_id_vals']=vals['payment_id_vals'][:1]

        returnvals_list

    def_get_tax_category_list(self,invoice,taxes):
        #EXTENDSaccount.edi.xml.ubl_21
        vals_list=super()._get_tax_category_list(invoice,taxes)

        forvalsinvals_list:
            vals.pop('name')

        returnvals_list

    def_get_invoice_tax_totals_vals_list(self,invoice,taxes_vals):
        #EXTENDSaccount.edi.xml.ubl_21
        vals_list=super()._get_invoice_tax_totals_vals_list(invoice,taxes_vals)

        forvalsinvals_list:
            vals['currency_dp']=2
            forsubtotal_valsinvals.get('tax_subtotal_vals',[]):
                subtotal_vals.pop('percent',None)
                subtotal_vals['currency_dp']=2

        returnvals_list

    def_get_invoice_line_item_vals(self,line,taxes_vals):
        #EXTENDSaccount.edi.xml.ubl_21
        line_item_vals=super()._get_invoice_line_item_vals(line,taxes_vals)

        forvalinline_item_vals['classified_tax_category_vals']:
            #[UBL-CR-601]TaxExemptionReasonmustnotappearinInvoiceLineItemClassifiedTaxCategory
            #[BR-E-10]TaxExemptionReasonmustonlyappearinTaxTotalTaxSubtotalTaxCategory
            val.pop('tax_exemption_reason')

        returnline_item_vals

    def_get_invoice_line_allowance_vals_list(self,line,tax_values_list):
        #EXTENDSaccount.edi.xml.ubl_21
        vals_list=super()._get_invoice_line_allowance_vals_list(line,tax_values_list)

        forvalsinvals_list:
            vals['currency_dp']=2

        returnvals_list

    def_get_invoice_line_vals(self,line,taxes_vals):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._get_invoice_line_vals(line,taxes_vals)

        vals.pop('tax_total_vals',None)

        vals['currency_dp']=2
        vals['price_vals']['currency_dp']=2

        returnvals

    def_export_invoice_vals(self,invoice):
        #EXTENDSaccount.edi.xml.ubl_21
        vals=super()._export_invoice_vals(invoice)

        vals['vals'].update({
            'customization_id':'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0',
            'profile_id':'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
            'currency_dp':2,
            'ubl_version_id':None,
        })
        vals['vals']['legal_monetary_total_vals']['currency_dp']=2

        #[NL-R-001]ForsuppliersintheNetherlands,ifthedocumentisacreditnote,thedocumentMUST
        #containaninvoicereference(cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID)
        ifvals['supplier'].country_id.code=='NL'and'refund'ininvoice.move_type:
            vals['vals'].update({
                'billing_reference_vals':{
                    'id':invoice.ref,
                    'issue_date':None,
                }
            })

        returnvals

    def_export_invoice_constraints(self,invoice,vals):
        #EXTENDSaccount.edi.xml.ubl_21
        constraints=super()._export_invoice_constraints(invoice,vals)
        constraints.update(
            self._invoice_constraints_peppol_en16931_ubl(invoice,vals)
        )
        constraints.update(
            self._invoice_constraints_cen_en16931_ubl(invoice,vals)
        )

        returnconstraints

    def_invoice_constraints_cen_en16931_ubl(self,invoice,vals):
        """
        correspondstotheerrorsraisedby'schematron/openpeppol/3.13.0/xslt/CEN-EN16931-UBL.xslt'forinvoices.
        Thisxsltwasobtainedbytransformingthecorrespondingsch
        https://docs.peppol.eu/poacc/billing/3.0/files/CEN-EN16931-UBL.sch.
        """
        eu_countries=self.env.ref('base.europe').country_ids
        intracom_delivery=(vals['customer'].country_idineu_countries
                             andvals['supplier'].country_idineu_countries
                             andvals['customer'].country_id!=vals['supplier'].country_id)

        constraints={
            #[BR-S-02]-AnInvoicethatcontainsanInvoiceline(BG-25)wheretheInvoiceditemVATcategorycode
            #(BT-151)is"Standardrated"shallcontaintheSellerVATIdentifier(BT-31),theSellertaxregistration
            #identifier(BT-32)and/ortheSellertaxrepresentativeVATidentifier(BT-63).
            #---
            #[BR-CO-26]-Inorderforthebuyertoautomaticallyidentifyasupplier,theSelleridentifier(BT-29),
            #theSellerlegalregistrationidentifier(BT-30)and/ortheSellerVATidentifier(BT-31)shallbepresent.
            'cen_en16931_seller_vat_identifier':self._check_required_fields(
                vals['supplier'],'vat' #thischeckislargerthantherulesabove
            ),
            #[BR-61]-IfthePaymentmeanstypecode(BT-81)meansSEPAcredittransfer,Localcredittransferor
            #Non-SEPAinternationalcredittransfer,thePaymentaccountidentifier(BT-84)shallbepresent.
            #note:Paymentaccountidentifieris<cac:PayeeFinancialAccount>
            #note:noneedtocheckaccount_number,becauseit'sarequiredfieldforapartner_bank
            'cen_en16931_payment_account_identifier':self._check_required_fields(
                invoice,'partner_bank_id'
            )ifvals['vals']['payment_means_vals_list'][0]['payment_means_code']in(30,58)elseNone,
            #[BR-62]-TheSellerelectronicaddress(BT-34)shallhaveaSchemeidentifier.
            #ifthisfails,itmightjustbeamissingcountrywhenmappingthecountrytotheEAScode
            'cen_en16931_seller_EAS':self._check_required_fields(
                vals['vals']['accounting_supplier_party_vals']['party_vals']['endpoint_id_attrs'],'schemeID',
                _("NoElectronicAddressScheme(EAS)couldbefoundfor%s.",vals['customer'].name)
            ),
            #[BR-63]-TheBuyerelectronicaddress(BT-49)shallhaveaSchemeidentifier.
            #ifthisfails,itmightjustbeamissingcountrywhenmappingthecountrytotheEAScode
            'cen_en16931_buyer_EAS':self._check_required_fields(
                vals['vals']['accounting_customer_party_vals']['party_vals']['endpoint_id_attrs'],'schemeID',
                _("NoElectronicAddressScheme(EAS)couldbefoundfor%s.",vals['customer'].name)
            ),
            #[BR-IC-12]-InanInvoicewithaVATbreakdown(BG-23)wheretheVATcategorycode(BT-118)is
            #"Intra-communitysupply"theDelivertocountrycode(BT-80)shallnotbeblank.
            'cen_en16931_delivery_country_code':self._check_required_fields(
                vals['vals']['delivery_vals_list'][0],'delivery_location_vals',
                _("Forintracommunitysupply,thedeliveryaddressshouldbeincluded.")
            )ifintracom_deliveryelseNone,

            #[BR-IC-11]-InanInvoicewithaVATbreakdown(BG-23)wheretheVATcategorycode(BT-118)is
            #"Intra-communitysupply"theActualdeliverydate(BT-72)ortheInvoicingperiod(BG-14)
            #shallnotbeblank.
            'cen_en16931_delivery_date_invoicing_period':self._check_required_fields(
                vals['vals']['delivery_vals_list'][0],'actual_delivery_date',
                _("Forintracommunitysupply,theactualdeliverydateortheinvoicingperiodshouldbeincluded.")
            )andself._check_required_fields(
                vals['vals']['invoice_period_vals_list'][0],['start_date','end_date'],
                _("Forintracommunitysupply,theactualdeliverydateortheinvoicingperiodshouldbeincluded.")
            )ifintracom_deliveryelseNone,
        }

        forlineininvoice.invoice_line_ids.filtered(lambdax:x.display_typenotin('line_note','line_section')):
            iflen(line.tax_ids.flatten_taxes_hierarchy().filtered(lambdat:t.amount_type!='fixed'))!=1:
                #[UBL-SR-48]-Invoicelinesshallhaveoneandonlyoneclassifiedtaxcategory.
                #/!\exception:possibletohaveanynumberofecotaxes(fixedtax)witharegularpercentagetax
                constraints.update({'cen_en16931_tax_line':_("Eachinvoicelineshallhaveoneandonlyonetax.")})

        returnconstraints

    def_invoice_constraints_peppol_en16931_ubl(self,invoice,vals):
        """
        correspondstotheerrorsraisedby'schematron/openpeppol/3.13.0/xslt/PEPPOL-EN16931-UBL.xslt'for
        invoicesinecosio.Thisxsltwasobtainedbytransformingthecorrespondingsch
        https://docs.peppol.eu/poacc/billing/3.0/files/PEPPOL-EN16931-UBL.sch.

        Thenationalrules(https://docs.peppol.eu/poacc/billing/3.0/bis/#national_rules)areincludedinthisfile.
        Theyalwaysrefertothesupplier'scountry.
        """
        constraints={
            #PEPPOL-EN16931-R020:SellerelectronicaddressMUSTbeprovided
            'peppol_en16931_ubl_seller_endpoint':self._check_required_fields(
                vals['supplier'],'vat'
            ),
            #PEPPOL-EN16931-R010:BuyerelectronicaddressMUSTbeprovided
            'peppol_en16931_ubl_buyer_endpoint':self._check_required_fields(
                vals['customer'],'vat'
            ),
            #PEPPOL-EN16931-R003:AbuyerreferenceorpurchaseorderreferenceMUSTbeprovided.
            'peppol_en16931_ubl_buyer_ref_po_ref':
                "Abuyerreferenceorpurchaseorderreferencemustbeprovided."ifself._check_required_fields(
                    vals['vals'],'buyer_reference'
                )andself._check_required_fields(vals['vals'],'order_reference')elseNone,
        }

        ifvals['supplier'].country_id.code=='NL':
            constraints.update({
                #[NL-R-001]ForsuppliersintheNetherlands,ifthedocumentisacreditnote,thedocumentMUSTcontain
                #aninvoicereference(cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID)
                'nl_r_001':self._check_required_fields(invoice,'ref')if'refund'ininvoice.move_typeelse'',

                #[NL-R-002]ForsuppliersintheNetherlandsthesupplier’saddress(cac:AccountingSupplierParty/cac:Party
                #/cac:PostalAddress)MUSTcontainstreetname(cbc:StreetName),city(cbc:CityName)andpostcode(cbc:PostalZone)
                'nl_r_002_street':self._check_required_fields(vals['supplier'],'street'),
                'nl_r_002_zip':self._check_required_fields(vals['supplier'],'zip'),
                'nl_r_002_city':self._check_required_fields(vals['supplier'],'city'),

                #[NL-R-003]ForsuppliersintheNetherlands,thelegalentityidentifierMUSTbeeithera
                #KVKorOINnumber(schemeID0106or0190)
                'nl_r_003':_(
                    "Thesupplier%smusthaveaKVKorOINnumber.",
                    vals['supplier'].display_name
                )if'l10n_nl_oin'notinvals['supplier']._fieldsor'l10n_nl_kvk'notinvals['supplier']._fieldselse'',

                #[NL-R-007]ForsuppliersintheNetherlands,thesupplierMUSTprovideameansofpayment
                #(cac:PaymentMeans)ifthepaymentisfromcustomertosupplier
                'nl_r_007':self._check_required_fields(invoice,'partner_bank_id')
            })

            ifvals['customer'].country_id.code=='NL':
                constraints.update({
                    #[NL-R-004]ForsuppliersintheNetherlands,ifthecustomerisintheNetherlands,thecustomer
                    #address(cac:AccountingCustomerParty/cac:Party/cac:PostalAddress)MUSTcontainthestreetname
                    #(cbc:StreetName),thecity(cbc:CityName)andpostcode(cbc:PostalZone)
                    'nl_r_004_street':self._check_required_fields(vals['customer'],'street'),
                    'nl_r_004_city':self._check_required_fields(vals['customer'],'city'),
                    'nl_r_004_zip':self._check_required_fields(vals['customer'],'zip'),

                    #[NL-R-005]ForsuppliersintheNetherlands,ifthecustomerisintheNetherlands,
                    #thecustomer’slegalentityidentifierMUSTbeeitheraKVKorOINnumber(schemeID0106or0190)
                    'nl_r_005':_(
                        "Thecustomer%smusthaveaKVKorOINnumber.",
                        vals['customer'].display_name
                    )if'l10n_nl_oin'notinvals['customer']._fieldsor'l10n_nl_kvk'notinvals['customer']._fieldselse'',
                })

        ifvals['supplier'].country_id.code=='NO':
            vat=vals['supplier'].vat
            constraints.update({
                #NO-R-001:ForNorwegiansuppliers,aVATnumberMUSTbethecountrycodeprefixNOfollowedbya
                #validNorwegianorganizationnumber(ninenumbers)followedbythelettersMVA.
                #Note:mva.is_valid("179728982MVA")isTruewhileitlackstheNOprefix
                'no_r_001':_(
                    "TheVATnumberofthesupplierdoesnotseemtobevalid.Itshouldbeoftheform:NO179728982MVA."
                )ifnotmva.is_valid(vat)orlen(vat)!=14orvat[:2]!='NO'orvat[-3:]!='MVA'else"",

                'no_supplier_bronnoysund':_(
                    "Thesupplier%smusthaveaBronnoysundcompanyregistry.",
                    vals['supplier'].display_name
                )if'l10n_no_bronnoysund_number'notinvals['supplier']._fieldsornotvals['supplier'].l10n_no_bronnoysund_numberelse"",
            })
        ifvals['customer'].country_id.code=='NO':
            constraints.update({
                'no_customer_bronnoysund':_(
                    "Thesupplier%smusthaveaBronnoysundcompanyregistry.",
                    vals['customer'].display_name
                )if'l10n_no_bronnoysund_number'notinvals['customer']._fieldsornotvals['customer'].l10n_no_bronnoysund_numberelse"",
            })

        returnconstraints
