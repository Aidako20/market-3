#-*-coding:utf-8-*-

fromflectraimport_,models
fromflectra.toolsimportfloat_repr
fromflectra.tests.commonimportForm
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.tools.float_utilsimportfloat_round
fromflectra.tools.miscimportformatLang

fromzeepimportClient

#-------------------------------------------------------------------------
#UNITOFMEASURE
#-------------------------------------------------------------------------
UOM_TO_UNECE_CODE={
    'uom.product_uom_unit':'C62',
    'uom.product_uom_dozen':'DZN',
    'uom.product_uom_kgm':'KGM',
    'uom.product_uom_gram':'GRM',
    'uom.product_uom_day':'DAY',
    'uom.product_uom_hour':'HUR',
    'uom.product_uom_ton':'TNE',
    'uom.product_uom_meter':'MTR',
    'uom.product_uom_km':'KMT',
    'uom.product_uom_cm':'CMT',
    'uom.product_uom_litre':'LTR',
    'uom.product_uom_cubic_meter':'MTQ',
    'uom.product_uom_lb':'LBR',
    'uom.product_uom_oz':'ONZ',
    'uom.product_uom_inch':'INH',
    'uom.product_uom_foot':'FOT',
    'uom.product_uom_mile':'SMI',
    'uom.product_uom_floz':'OZA',
    'uom.product_uom_qt':'QT',
    'uom.product_uom_gal':'GLL',
    'uom.product_uom_cubic_inch':'INQ',
    'uom.product_uom_cubic_foot':'FTQ',
}

#-------------------------------------------------------------------------
#ELECTRONICADDRESSSCHEME(EAS),seehttps://docs.peppol.eu/poacc/billing/3.0/codelist/eas/
#-------------------------------------------------------------------------
COUNTRY_EAS={
    'HU':9910,
    'AT':9915,
    'ES':9920,
    'AD':9922,
    'AL':9923,
    'BA':9924,
    'BE':9925,
    'BG':9926,
    'CH':9927,
    'CY':9928,
    'CZ':9929,
    'DE':9930,
    'DK':'0184',
    'EE':9931,
    'GB':9932,
    'GR':9933,
    'HR':9934,
    'IE':9935,
    'IT':'0211',
    'LI':9936,
    'LT':9937,
    'LU':9938,
    'LV':9939,
    'MC':9940,
    'ME':9941,
    'MK':9942,
    'MT':9943,
    'NL':9944,
    'PL':9945,
    'PT':9946,
    'RO':9947,
    'RS':9948,
    'SI':9949,
    'SK':9950,
    'SM':9951,
    'TR':9952,
    'VA':9953,
    'SE':9955,
    'FR':9957,
    'NO':'0192',
    'SG':'0195',
    'AU':'0151',
    'FI':'0213',
}


classAccountEdiCommon(models.AbstractModel):
    _name="account.edi.common"
    _description="CommonfunctionsforEDIdocuments:generatethedata,theconstraints,etc"

    #-------------------------------------------------------------------------
    #HELPERS
    #-------------------------------------------------------------------------

    defformat_float(self,amount,precision_digits):
        ifamountisNone:
            returnNone
        returnfloat_repr(float_round(amount,precision_digits),precision_digits)

    def_get_uom_unece_code(self,line):
        """
        listofcodes:https://docs.peppol.eu/poacc/billing/3.0/codelist/UNECERec20/
        orhttps://unece.org/fileadmin/DAM/cefact/recommendations/bkup_htm/add2c.htm(sortedbyletter)
        """
        xmlid=line.product_uom_id.get_external_id()
        ifxmlidandline.product_uom_id.idinxmlid:
            returnUOM_TO_UNECE_CODE.get(xmlid[line.product_uom_id.id],'C62')
        return'C62'

    def_find_value(self,xpath,tree):
        #avoid'TypeError:emptynamespaceprefixisnotsupportedinXPath'
        nsmap={k:vfork,vintree.nsmap.items()ifkisnotNone}
        returnself.env['account.edi.format']._find_value(xpath=xpath,xml_element=tree,namespaces=nsmap)

    #-------------------------------------------------------------------------
    #TAXES
    #-------------------------------------------------------------------------

    def_validate_taxes(self,invoice):
        """Validatethestructureofthetaxrepartitionlines(invalidstructurecouldleadtounexpectedresults)
        """
        fortaxininvoice.invoice_line_ids.tax_ids:
            try:
                tax._validate_repartition_lines()
            exceptValidationErrorase:
                error_msg=_("Tax'%s'isinvalid:%s",tax.name,e.args[0]) #args[0]givestheerrormessage
                raiseValidationError(error_msg)

    def_get_tax_unece_codes(self,invoice,tax):
        """
        Source:docofPeppol(buttheCEFnormisalsousedbyfactur-x,yetnotdetailed)
        https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-TaxTotal/cac-TaxSubtotal/cac-TaxCategory/cbc-TaxExemptionReasonCode/
        https://docs.peppol.eu/poacc/billing/3.0/codelist/vatex/
        https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305/
        :returns:{
            tax_category_code:str,
            tax_exemption_reason_code:str,
            tax_exemption_reason:str,
        }
        """
        defcreate_dict(tax_category_code=None,tax_exemption_reason_code=None,tax_exemption_reason=None):
            return{
                'tax_category_code':tax_category_code,
                'tax_exemption_reason_code':tax_exemption_reason_code,
                'tax_exemption_reason':tax_exemption_reason,
            }

        supplier=invoice.company_id.partner_id.commercial_partner_id
        customer=invoice.commercial_partner_id

        #addNorway,Iceland,Liechtenstein
        european_economic_area=self.env.ref('base.europe').country_ids.mapped('code')+['NO','IS','LI']

        ifcustomer.country_id.code=='ES'andcustomer.zip:
            ifcustomer.zip[:2]in('35','38'): #Canary
                #[BR-IG-10]-AVATbreakdown(BG-23)withVATCategorycode(BT-118)"IGIC"shallnothaveaVAT
                #exemptionreasoncode(BT-121)orVATexemptionreasontext(BT-120).
                returncreate_dict(tax_category_code='L')
            ifcustomer.zip[:2]in('51','52'):
                returncreate_dict(tax_category_code='M') #Ceuta&Mellila

        #see:https://anskaffelser.dev/postaward/g3/spec/current/billing-3.0/norway/#_value_added_tax_norwegian_mva
        ifcustomer.country_id.code=='NO':
            iftax.amount==25:
                returncreate_dict(tax_category_code='S',tax_exemption_reason=_('OutputVAT,regularrate'))
            iftax.amount==15:
                returncreate_dict(tax_category_code='S',tax_exemption_reason=_('OutputVAT,reducedrate,middle'))
            iftax.amount==11.11:
                returncreate_dict(tax_category_code='S',tax_exemption_reason=_('OutputVAT,reducedrate,rawfish'))
            iftax.amount==12:
                returncreate_dict(tax_category_code='S',tax_exemption_reason=_('OutputVAT,reducedrate,low'))

        ifsupplier.country_id==customer.country_id:
            ifnottaxortax.amount==0:
                #intheory,youshouldindicatethepreciselawarticle
                returncreate_dict(tax_category_code='E',tax_exemption_reason=_('Articles226items11to15Directive2006/112/EN'))
            else:
                returncreate_dict(tax_category_code='S') #standardVAT

        ifsupplier.country_id.codeineuropean_economic_area:
            iftax.amount!=0:
                #otherwise,thevalidatorwillcomplainbecauseGandKcodeshouldbeusedwith0%tax
                returncreate_dict(tax_category_code='S')
            ifcustomer.country_id.codenotineuropean_economic_area:
                returncreate_dict(
                    tax_category_code='G',
                    tax_exemption_reason_code='VATEX-EU-G',
                    tax_exemption_reason=_('ExportoutsidetheEU'),
                )
            ifcustomer.country_id.codeineuropean_economic_area:
                returncreate_dict(
                    tax_category_code='K',
                    tax_exemption_reason_code='VATEX-EU-IC',
                    tax_exemption_reason=_('Intra-Communitysupply'),
                )

        iftax.amount!=0:
            returncreate_dict(tax_category_code='S')
        else:
            returncreate_dict(tax_category_code='E',tax_exemption_reason=_('Articles226items11to15Directive2006/112/EN'))

    def_get_tax_category_list(self,invoice,taxes):
        """Fulllist:https://unece.org/fileadmin/DAM/trade/untdid/d16b/tred/tred5305.htm
        Subset:https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305/

        :paramtaxes:  account.taxrecords.
        :return:       AlistofvaluestofilltheTaxCategoryforeachtemplate.
        """
        res=[]
        fortaxintaxes:
            tax_unece_codes=self._get_tax_unece_codes(invoice,tax)
            res.append({
                'id':tax_unece_codes.get('tax_category_code'),
                'percent':tax.amountiftax.amount_type=='percent'elseFalse,
                'name':tax_unece_codes.get('tax_exemption_reason'),
                **tax_unece_codes,
            })
        returnres

    #-------------------------------------------------------------------------
    #CONSTRAINTS
    #-------------------------------------------------------------------------

    def_check_required_fields(self,record,field_names,custom_warning_message=""):
        """
        Thisfunctioncheckthatafieldexistsonarecordordictionaries
        returnsagenericerrormessageifit'snotthecaseoracustomoneifspecified
        """
        ifnotrecord:
            returncustom_warning_messageor_("Theelement%sisrequiredon%s.",record,','.join(field_names))

        ifnotisinstance(field_names,list):
            field_names=[field_names]

        has_values=any(record[field_name]forfield_nameinfield_names)
        #fieldispresent
        ifhas_values:
            return

        #fieldisnotpresent
        ifcustom_warning_messageorisinstance(record,dict):
            returncustom_warning_messageor_("Theelement%sisrequiredon%s.",record,','.join(field_names))

        display_field_names=record.fields_get(field_names)
        iflen(field_names)==1:
            display_field=f"'{display_field_names[field_names[0]]['string']}'"
            return_("Thefield%sisrequiredon%s.",display_field,record.display_name)
        else:
            display_fields=','.join(f"'{display_field_names[x]['string']}'"forxindisplay_field_names)
            return_("Atleastoneofthefollowingfields%sisrequiredon%s.",display_fields,record.display_name)

    #-------------------------------------------------------------------------
    #COMMONCONSTRAINTS
    #-------------------------------------------------------------------------

    def_invoice_constraints_common(self,invoice):
        #checkthatthereisataxoneachline
        forlineininvoice.invoice_line_ids.filtered(lambdax:notx.display_type):
            ifnotline.tax_ids:
                return{'tax_on_line':_("Eachinvoicelineshouldhaveatleastonetax.")}
        return{}

    #-------------------------------------------------------------------------
    #Importinvoice
    #-------------------------------------------------------------------------

    def_import_invoice(self,journal,filename,tree,existing_invoice=None):
        move_types,qty_factor=self._get_import_document_amount_sign(filename,tree)
        ifnotmove_types:
            return
        ifjournal.type=='purchase':
            move_type=move_types[0]
        elifjournal.type=='sale':
            move_type=move_types[1]
        else:
            return
        ifexisting_invoiceandexisting_invoice.move_type!=move_type:
            #withanemailaliastocreateaccount_move,firstthemoveiscreated(usingalias_defaults,which
            #containsmove_type='out_invoice')thentheattachmentisdecoded,ifitrepresentsacreditnote,
            #themovetypeneedstobechangedto'out_refund'
            types={move_type,existing_invoice.move_type}
            iftypes=={'out_invoice','out_refund'}ortypes=={'in_invoice','in_refund'}:
                existing_invoice.move_type=move_type
            else:
                return

        invoice=existing_invoiceorself.env['account.move']
        invoice_form=Form(invoice.with_context(
            account_predictive_bills_disable_prediction=True,
            default_move_type=move_type,
            default_journal_id=journal.id,
        ))
        invoice_form,logs=self._import_fill_invoice_form(journal,tree,invoice_form,qty_factor)
        invoice=invoice_form.save()
        ifinvoice:
            iflogs:
                body=_(
                    "<strong>Formatusedtoimporttheinvoice:%s</strong><p><li>%s</li></p>",
                    str(self._description),"</li><li>".join(logs)
                )
            else:
                body=_("<strong>Formatusedtoimporttheinvoice:%s</strong>",str(self._description))
            invoice.with_context(no_new_invoice=True).message_post(body=body)

        #===ImporttheembeddedPDFinthexmlifsomearefound===

        attachments=self.env['ir.attachment']
        additional_docs=tree.findall('./{*}AdditionalDocumentReference')
        fordocumentinadditional_docs:
            attachment_name=document.find('{*}ID')
            attachment_data=document.find('{*}Attachment/{*}EmbeddedDocumentBinaryObject')
            ifattachment_nameisnotNone\
                    andattachment_dataisnotNone\
                    andattachment_data.attrib.get('mimeCode')=='application/pdf':
                text=attachment_data.text
                #Normalizethenameofthefile:somee-fffemittersputthefullpathofthefile
                #(WindowsorLinuxstyle)and/orthenameofthexmlinsteadofthepdf.
                #Getonlythefilenamewithapdfextension.
                name=(attachment_name.textor'invoice').split('\\')[-1].split('/')[-1].split('.')[0]+'.pdf'
                attachment=self.env['ir.attachment'].create({
                    'name':name,
                    'res_id':invoice.id,
                    'res_model':'account.move',
                    'datas':text+'='*(len(text)%3), #Fixincorrectpadding
                    'type':'binary',
                    'mimetype':'application/pdf',
                })
                #Uponreceivinganemail(containinganxml)withaconfiguredaliastocreateinvoice,thexmlis
                #setasthemain_attachment.Toberenderedintheformview,thepdfshouldbethemain_attachment.
                ifinvoice.message_main_attachment_idand\
                        invoice.message_main_attachment_id.name.endswith('.xml')and\
                        'pdf'notininvoice.message_main_attachment_id.mimetype:
                    invoice.message_main_attachment_id=attachment
                attachments|=attachment
        ifattachments:
            invoice.with_context(no_new_invoice=True).message_post(attachment_ids=attachments.ids)

        returninvoice

    def_import_retrieve_and_fill_partner(self,invoice,name,phone,mail,vat):
        """Retrievethepartner,ifnomatchingpartnerisfound,createit(onlyifhehasavatandaname)
        """
        invoice.partner_id=self.env['account.edi.format']._retrieve_partner(name=name,phone=phone,mail=mail,vat=vat)
        ifnotinvoice.partner_idandnameandvat:
            invoice.partner_id=self.env['res.partner'].create({'name':name,'email':mail,'phone':phone})
            #aninvalidVATwillthrowaValidationError(see'check_vat'inbase_vat)
            try:
                invoice.partner_id.vat=vat
            exceptValidationError:
                invoice.partner_id.vat=False

    def_import_fill_invoice_allowance_charge(self,tree,invoice_form,journal,qty_factor):
        logs=[]
        if'{urn:oasis:names:specification:ubl:schema:xsd'intree.tag:
            is_ubl=True
        elif'{urn:un:unece:uncefact:data:standard:'intree.tag:
            is_ubl=False
        else:
            return

        xpath='./{*}AllowanceCharge'ifis_ublelse'./{*}SupplyChainTradeTransaction/{*}ApplicableHeaderTradeSettlement/{*}SpecifiedTradeAllowanceCharge'
        allowance_charge_nodes=tree.findall(xpath)
        forallow_elinallowance_charge_nodes:
            withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                invoice_line_form.sequence=0 #besuretoputtheselinesabovethe'real'invoicelines

                charge_factor=-1 #factoris-1fordiscount,1forcharge
                ifis_ubl:
                    charge_indicator_node=allow_el.find('./{*}ChargeIndicator')
                else:
                    charge_indicator_node=allow_el.find('./{*}ChargeIndicator/{*}Indicator')
                ifcharge_indicator_nodeisnotNone:
                    charge_factor=-1ifcharge_indicator_node.text=='false'else1

                name=""
                reason_code_node=allow_el.find('./{*}AllowanceChargeReasonCode'ifis_ublelse'./{*}ReasonCode')
                ifreason_code_nodeisnotNone:
                    name+=reason_code_node.text+""
                reason_node=allow_el.find('./{*}AllowanceChargeReason'ifis_ublelse'./{*}Reason')
                ifreason_nodeisnotNone:
                    name+=reason_node.text
                invoice_line_form.name=name

                amount_node=allow_el.find('./{*}Amount'ifis_ublelse'./{*}ActualAmount')
                base_amount_node=allow_el.find('./{*}BaseAmount'ifis_ublelse'./{*}BasisAmount')
                #Sincethereisnoquantityassociatedfortheallowance/chargeondocumentlevel,
                #ifwehaveaninvoicewithnegativeamounts,thepricewasmultipliedby-1andnotthequantity
                #Seethefileintest_files:'base-negative-inv-correction.xml'VS'base-example.xml'for'Insurance'
                ifbase_amount_nodeisnotNone:
                    invoice_line_form.price_unit=float(base_amount_node.text)*charge_factor*qty_factor
                    percent_node=allow_el.find('./{*}MultiplierFactorNumeric'ifis_ublelse'./{*}CalculationPercent')
                    ifpercent_nodeisnotNone:
                        invoice_line_form.quantity=float(percent_node.text)/100
                elifamount_nodeisnotNone:
                    invoice_line_form.price_unit=float(amount_node.text)*charge_factor*qty_factor

                invoice_line_form.tax_ids.clear() #clearthedefaulttaxesappliedtotheline
                tax_xpath='./{*}TaxCategory/{*}Percent'ifis_ublelse'./{*}CategoryTradeTax/{*}RateApplicablePercent'
                fortax_categ_percent_elinallow_el.findall(tax_xpath):
                    tax=self.env['account.tax'].search([
                        ('company_id','=',journal.company_id.id),
                        ('amount','=',float(tax_categ_percent_el.text)),
                        ('amount_type','=','percent'),
                        ('type_tax_use','=',journal.type),
                    ],limit=1)
                    iftax:
                        invoice_line_form.tax_ids.add(tax)
                    else:
                        logs.append(
                            _("Couldnotretrievethetax:%s%%forline'%s'.",
                              float(tax_categ_percent_el.text),
                              name)
                        )
        returnlogs

    def_import_fill_invoice_down_payment(self,invoice_form,prepaid_node,qty_factor):
        """
        DEPRECATED:removedinmaster
        Createsadownpaymentlineontheinvoiceatimportifprepaid_node(TotalPrepaidAmountinCII,
        PrepaidAmountinUBL)exists.
        qty_factor-1ifthexmlislabelledasaninvoicebuthasnegativeamounts->conversionintoacreditnote
        needed,soweneedthismultiplier.Otherwise,qty_factoris1.
        """
        ifprepaid_nodeisnotNoneandfloat(prepaid_node.text)!=0:
            #createasection
            withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                invoice_line_form.sequence=998
                invoice_line_form.display_type='line_section'
                invoice_line_form.name=_("DownPayments")
                invoice_line_form.price_unit=0
                invoice_line_form.quantity=0
                invoice_line_form.account_id=self.env['account.account']
            #createthelinewiththedownpayment
            withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                invoice_line_form.sequence=999
                invoice_line_form.name=_("DownPayment")
                invoice_line_form.price_unit=float(prepaid_node.text)
                invoice_line_form.quantity=qty_factor*-1
                invoice_line_form.tax_ids.clear()

    def_import_log_prepaid_amount(self,invoice_form,prepaid_node,qty_factor):
        """
        Logamessageinthechatteratimportifprepaid_node(TotalPrepaidAmountinCII,PrepaidAmountinUBL)exists.
        """
        prepaid_amount=float(prepaid_node.text)ifprepaid_nodeisnotNoneelse0.0
        ifnotinvoice_form.currency_id.is_zero(prepaid_amount):
            amount=prepaid_amount*qty_factor
            formatted_amount=formatLang(self.env,amount,currency_obj=invoice_form.currency_id)
            return[
                _("Apaymentof%swasdetected.",formatted_amount)
            ]
        return[]

    def_import_fill_invoice_line_values(self,tree,xpath_dict,invoice_line_form,qty_factor):
        """
        Readthexmlinvoice,extracttheinvoicelinevalues,computetheflectravalues
        tofillaninvoicelineform:quantity,price_unit,discount,product_uom_id.

        Thewayofcomputinginvoicelineisquitecomplicated:
        https://docs.peppol.eu/poacc/billing/3.0/bis/#_calculation_on_line_level(sameasinfactur-xdocumentation)

        line_net_subtotal=(gross_unit_price-rebate)*(billed_qty/basis_qty)-allow_charge_amount

        with(UBL|CII):
            *net_unit_price='Price/PriceAmount'|'NetPriceProductTradePrice'(mandatory)(BT-146)
            *gross_unit_price='Price/AllowanceCharge/BaseAmount'|'GrossPriceProductTradePrice'(optional)(BT-148)
            *basis_qty='Price/BaseQuantity'|'BasisQuantity'(optional,eitherbelownet_pricenodeor
                gross_pricenode)(BT-149)
            *billed_qty='InvoicedQuantity'|'BilledQuantity'(mandatory)(BT-129)
            *allow_charge_amount=sumof'AllowanceCharge'|'SpecifiedTradeAllowanceCharge'(samelevelasPrice)
                ONTHELINElevel(optional)(BT-136/BT-141)
            *line_net_subtotal='LineExtensionAmount'|'LineTotalAmount'(mandatory)(BT-131)
            *rebate='Price/AllowanceCharge'|'AppliedTradeAllowanceCharge'belowgross_pricenode!(BT-147)
                "itempricediscount"whichisdifferentfromtheusualallow_charge_amount
                gross_unit_price(BT-148)-rebate(BT-147)=net_unit_price(BT-146)

        InFlectra,weobtain:
        (1)=price_unit = gross_price_unit/basis_qty = (net_price_unit+rebate)/basis_qty
        (2)=quantity = billed_qty
        (3)=discount(convertedintoapercentage) = 100*(1-price_subtotal/(billed_qty*price_unit))
        (4)=price_subtotal

        Alternatively,wecouldalsoset:quantity=billed_qty/basis_qty

        WARNING,thebasisquantityparameterisannoying,forinstance,aninvoicewithaline:
            itemA |priceperunitofmeasure/unitprice:30 |uom=3pieces|billedqty=3|rebate=2 |untaxedtotal=28
        Indeed,30$/3pieces=10$/piece=>10*3(billedquantity)-2(rebate)=28

        UBLROUNDING:"theresultofItemlinenet
            amount=((Itemnetprice(BT-146)÷Itempricebasequantity(BT-149))×(InvoicedQuantity(BT-129))
        mustberoundedtotwodecimals,andtheallowance/chargeamountsarealsoroundedseparately."
        ItisnotpossibletodoitinFlectra.

        :paramstree
        :paramsxpath_dictdict:{
            'basis_qty':listofstr,
            'gross_price_unit':str,
            'rebate':str,
            'net_price_unit':str,
            'billed_qty':str,
            'allowance_charge':str,tobeusedinafindall!,
            'allowance_charge_indicator':str,relativexpathfromallowance_charge,
            'allowance_charge_amount':str,relativexpathfromallowance_charge,
            'line_total_amount':str,
        }
        :params:invoice_line_form
        :params:qty_factor
        :returns:{
            'quantity':float,
            'product_uom_id':(optional)uom.uom,
            'price_unit':float,
            'discount':float,
        }
        """
        #basis_qty(optional)
        basis_qty=1
        forxpathinxpath_dict['basis_qty']:
            basis_quantity_node=tree.find(xpath)
            ifbasis_quantity_nodeisnotNone:
                basis_qty=float(basis_quantity_node.text)or1

        #gross_price_unit(optional)
        gross_price_unit=None
        gross_price_unit_node=tree.find(xpath_dict['gross_price_unit'])
        ifgross_price_unit_nodeisnotNone:
            gross_price_unit=float(gross_price_unit_node.text)

        #rebate(optional)
        #Discount./!\asnopercentdiscountcanbesetonaline,needtoinferthepercentage
        #fromtheamountoftheactualamountofthediscount(theallowancecharge)
        rebate=0
        rebate_node=tree.find(xpath_dict['rebate'])
        net_price_unit_node=tree.find(xpath_dict['net_price_unit'])
        ifrebate_nodeisnotNone:
            rebate=float(rebate_node.text)
        elifnet_price_unit_nodeisnotNoneandgross_price_unit_nodeisnotNone:
            rebate=float(gross_price_unit_node.text)-float(net_price_unit_node.text)

        #net_price_unit(mandatory)
        net_price_unit=None
        ifnet_price_unit_nodeisnotNone:
            net_price_unit=float(net_price_unit_node.text)

        #billed_qty(mandatory)
        billed_qty=1
        product_uom_id=None
        quantity_node=tree.find(xpath_dict['billed_qty'])
        ifquantity_nodeisnotNone:
            billed_qty=float(quantity_node.text)
            uom_xml=quantity_node.attrib.get('unitCode')
            ifuom_xml:
                uom_infered_xmlid=[
                    flectra_xmlidforflectra_xmlid,uom_uneceinUOM_TO_UNECE_CODE.items()ifuom_unece==uom_xml
                ]
                ifuom_infered_xmlid:
                    product_uom_id=self.env.ref(uom_infered_xmlid[0],raise_if_not_found=False)

        #allow_charge_amount
        fixed_taxes_list=[]
        allow_charge_amount=0 #ifpositive:it'sadiscount,ifnegative:it'sacharge
        allow_charge_nodes=tree.findall(xpath_dict['allowance_charge'])
        forallow_charge_elinallow_charge_nodes:
            charge_indicator=allow_charge_el.find(xpath_dict['allowance_charge_indicator'])
            ifcharge_indicator.textandcharge_indicator.text.lower()=='false':
                discount_factor=1 #it'sadiscount
            else:
                discount_factor=-1 #it'sacharge
            amount=allow_charge_el.find(xpath_dict['allowance_charge_amount'])
            reason_code=allow_charge_el.find(xpath_dict['allowance_charge_reason_code'])
            reason=allow_charge_el.find(xpath_dict['allowance_charge_reason'])
            ifamountisnotNone:
                ifreason_codeisnotNoneandreason_code.text=='AEO'andreasonisnotNone:
                    #HandleFixedTaxes:whenexportingfromFlectra,weusetheallowance_chargenode
                    fixed_taxes_list.append({
                        'tax_name':reason.text,
                        'tax_amount':float(amount.text),
                    })
                else:
                    allow_charge_amount+=float(amount.text)*discount_factor

        #line_net_subtotal(mandatory)
        price_subtotal=None
        line_total_amount_node=tree.find(xpath_dict['line_total_amount'])
        ifline_total_amount_nodeisnotNone:
            price_subtotal=float(line_total_amount_node.text)

        ####################################################
        #Settingthevaluesontheinvoice_line_form
        ####################################################

        #quantity
        quantity=billed_qty*qty_factor

        #price_unit
        ifgross_price_unitisnotNone:
            price_unit=gross_price_unit/basis_qty
        elifnet_price_unitisnotNone:
            price_unit=(net_price_unit+rebate)/basis_qty
        elifprice_subtotalisnotNone:
            price_unit=(price_subtotal+allow_charge_amount)/(billed_qtyor1)
        else:
            raiseUserError(_("Nogrossprice,netpricenorlinesubtotalamountfoundforlineinxml"))

        #discount
        discount=0
        amount_fixed_taxes=sum(d['tax_amount']fordinfixed_taxes_list)
        ifbilled_qty*price_unit!=0andprice_subtotalisnotNone:
            discount=100*(1-(price_subtotal-amount_fixed_taxes)/(billed_qty*price_unit))

        #Sometimes,thexmlreceivedisverybad:unitprice=0,qty=1,butprice_subtotal=-200
        #forinstance,whenfillingadownpaymentasaninvoiceline.Theequationinthedocstringisnot
        #respected,andtheresultwillnotbecorrect,sowejustfollowthesimplerulebelow:
        ifnet_price_unit==0andprice_subtotal!=net_price_unit*(billed_qty/basis_qty)-allow_charge_amount:
            price_unit=price_subtotal/(billed_qtyor1)

        return{
            'quantity':quantity,
            'price_unit':price_unit,
            'discount':discount,
            'product_uom_id':product_uom_id,
            'fixed_taxes_list':fixed_taxes_list,
        }

    def_import_retrieve_fixed_tax(self,invoice_line_form,fixed_tax_vals):
        """Retrievethefixedtaxatimport,iterativelysearchforatax:
        1.notprice_includematchingthenameandtheamount
        2.notprice_includematchingtheamount
        3.price_includematchingthenameandtheamount
        4.price_includematchingtheamount
        """
        base_domain=[
            ('company_id','=',invoice_line_form.company_id.id),
            ('amount_type','=','fixed'),
            ('amount','=',fixed_tax_vals['tax_amount']),
        ]
        forprice_includein(False,True):
            fornamein(fixed_tax_vals['tax_name'],False):
                domain=base_domain+[('price_include','=',price_include)]
                ifname:
                    domain.append(('name','=',name))
                tax=self.env['account.tax'].search(domain,limit=1)
                iftax:
                    returntax
        returnself.env['account.tax']

    def_import_fill_invoice_line_taxes(self,journal,tax_nodes,invoice_line_form,inv_line_vals,logs):
        #Taxes:allamountsaretaxexcluded,sofirsttrytofetchprice_include=Falsetaxes,
        #ifnoresults,trytofetchtheprice_include=Truetaxes.Ifresults,needtoadapttheprice_unit.
        inv_line_vals['taxes']=[]
        fortax_nodeintax_nodes:
            amount=float(tax_node.text)
            domain=[
                ('company_id','=',journal.company_id.id),
                ('amount_type','=','percent'),
                ('type_tax_use','=',journal.type),
                ('amount','=',amount),
            ]
            tax_excl=self.env['account.tax'].search(domain+[('price_include','=',False)],limit=1)
            tax_incl=self.env['account.tax'].search(domain+[('price_include','=',True)],limit=1)
            iftax_excl:
                inv_line_vals['taxes'].append(tax_excl)
            eliftax_incl:
                inv_line_vals['taxes'].append(tax_incl)
                inv_line_vals['price_unit']*=(1+tax_incl.amount/100)
            else:
                logs.append(_("Couldnotretrievethetax:%s%%forline'%s'.",amount,invoice_line_form.name))

        #HandleFixedTaxes
        forfixed_tax_valsininv_line_vals['fixed_taxes_list']:
            tax=self._import_retrieve_fixed_tax(invoice_line_form,fixed_tax_vals)
            ifnottax:
                #Nothingfound:fixtheprice_units.t.linesubtotalismatchingtheoriginalinvoice
                inv_line_vals['price_unit']+=fixed_tax_vals['tax_amount']
            eliftax.price_include:
                inv_line_vals['taxes'].append(tax)
                inv_line_vals['price_unit']+=tax.amount
            else:
                inv_line_vals['taxes'].append(tax)

        #Setthevaluesontheline_form
        invoice_line_form.quantity=inv_line_vals['quantity']
        ifnotinv_line_vals.get('product_uom_id'):
            logs.append(
                _("Couldnotretrievetheunitofmeasureforlinewithlabel'%s'.",invoice_line_form.name))
        elifnotinvoice_line_form.product_id:
            #noproductsetontheline,noneedtocheckuomcompatibility
            invoice_line_form.product_uom_id=inv_line_vals['product_uom_id']
        elifinv_line_vals['product_uom_id'].category_id==invoice_line_form.product_id.product_tmpl_id.uom_id.category_id:
            #neededtocheckthattheuomiscompatiblewiththecategoryoftheproduct
            invoice_line_form.product_uom_id=inv_line_vals['product_uom_id']

        invoice_line_form.price_unit=inv_line_vals['price_unit']
        invoice_line_form.discount=inv_line_vals['discount']
        invoice_line_form.tax_ids.clear()
        fortaxininv_line_vals['taxes']:
            invoice_line_form.tax_ids.add(tax)
        returnlogs

    #-------------------------------------------------------------------------
    #CheckxmlusingthefreeAPIfromPh.Helger,don'tabuseit!
    #-------------------------------------------------------------------------

    def_check_xml_ecosio(self,invoice,xml_content,ecosio_formats):
        #seehttps://peppol.helger.com/public/locale-en_US/menuitem-validation-ws2
        ifnotecosio_formats:
            return
        soap_client=Client('https://peppol.helger.com/wsdvs?wsdl')
        ifinvoice.move_type=='out_invoice':
            ecosio_format=ecosio_formats['invoice']
        elifinvoice.move_type=='out_refund':
            ecosio_format=ecosio_formats['credit_note']
        else:
            invoice.with_context(no_new_invoice=True).message_post(
                body="ECOSIO:couldnotvalidatexml,formatsonlyexistforinvoiceorcreditnotes"
            )
            return
        ifnotecosio_format:
            return
        response=soap_client.service.validate(xml_content,ecosio_format)

        report=[]
        errors_cnt=0
        foriteminresponse['Result']:
            ifitem['artifactPath']:
                report.append(
                    "<li><fontstyle='color:Blue;'><strong>"+item['artifactPath']+"</strong></font></li>")
            fordetailinitem['Item']:
                ifdetail['errorLevel']=='WARN':
                    errors_cnt+=1
                    report.append(
                        "<li><fontstyle='color:Orange;'><strong>"+detail['errorText']+"</strong></font></li>")
                elifdetail['errorLevel']=='ERROR':
                    errors_cnt+=1
                    report.append(
                        "<li><fontstyle='color:Tomato;'><strong>"+detail['errorText']+"</strong></font></li>")

        iferrors_cnt==0:
            invoice.with_context(no_new_invoice=True).message_post(
                body=f"<fontstyle='color:Green;'><strong>ECOSIO:Allclearforformat{ecosio_format}!</strong></font>"
            )
        else:
            invoice.with_context(no_new_invoice=True).message_post(
                body=f"<fontstyle='color:Tomato;'><strong>ECOSIOERRORS/WARNINGSforformat{ecosio_format}</strong></font>:<ul>"
                     +"\n".join(report)+"</ul>"
            )
        returnresponse
