#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importzipfile
importio
importlogging
importre

fromdatetimeimportdate,datetime
fromlxmlimportetree

fromflectraimportapi,fields,models,_
fromflectra.toolsimportfloat_repr,float_compare
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.addons.base.models.ir_mail_serverimportMailDeliveryException
fromflectra.tests.commonimportForm


_logger=logging.getLogger(__name__)

DEFAULT_FACTUR_ITALIAN_DATE_FORMAT='%Y-%m-%d'


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_it_send_state=fields.Selection([
        ('new','New'),
        ('other','Other'),
        ('to_send','Notyetsend'),
        ('sent','Sent,waitingforresponse'),
        ('invalid','Sent,butinvalid'),
        ('delivered','Thisinvoiceisdelivered'),
        ('delivered_accepted','Thisinvoiceisdeliveredandacceptedbydestinatory'),
        ('delivered_refused','Thisinvoiceisdeliveredandrefusedbydestinatory'),
        ('delivered_expired','Thisinvoiceisdeliveredandexpired(expiryofthemaximumtermforcommunicationofacceptance/refusal)'),
        ('failed_delivery','Deliveryimpossible,EScertifythatithasreceivedtheinvoiceandthatthefile\
                        couldnotbedeliveredtotheaddressee')#okwemustdonothing
    ],default='to_send',copy=False,string="FatturaPASendState")

    l10n_it_stamp_duty=fields.Float(default=0,string="DatiBollo",readonly=True,states={'draft':[('readonly',False)]})

    l10n_it_ddt_id=fields.Many2one('l10n_it.ddt',string='DDT',readonly=True,states={'draft':[('readonly',False)]},copy=False)

    l10n_it_einvoice_name=fields.Char(compute='_compute_l10n_it_einvoice')

    l10n_it_einvoice_id=fields.Many2one('ir.attachment',string="Electronicinvoice",compute='_compute_l10n_it_einvoice')

    @api.depends('edi_document_ids','edi_document_ids.attachment_id')
    def_compute_l10n_it_einvoice(self):
        fattura_pa=self.env.ref('l10n_it_edi.edi_fatturaPA')
        forinvoiceinself:
            einvoice=invoice.edi_document_ids.filtered(lambdad:d.edi_format_id==fattura_pa)
            invoice.l10n_it_einvoice_id=einvoice.attachment_id
            invoice.l10n_it_einvoice_name=einvoice.attachment_id.name

    def_check_before_xml_exporting(self):
        #DEPRECATEDuseAccountEdiFormat._l10n_it_edi_check_invoice_configurationinstead
        errors=self.env['account.edi.format']._l10n_it_edi_check_invoice_configuration(self)
        iferrors:
            raiseUserError(self.env['account.edi.format']._format_error_message(_("Invalidconfiguration:"),errors))

    definvoice_generate_xml(self):
        self.ensure_one()
        report_name=self.env['account.edi.format']._l10n_it_edi_generate_electronic_invoice_filename(self)

        data=b"<?xmlversion='1.0'encoding='UTF-8'?>"+self._export_as_xml()
        description=_('Italianinvoice:%s',self.move_type)
        attachment=self.env['ir.attachment'].create({
            'name':report_name,
            'res_id':self.id,
            'res_model':self._name,
            'datas':base64.encodebytes(data),
            'description':description,
            'type':'binary',
            })

        self.message_post(
            body=(_("E-Invoiceisgeneratedon%sby%s")%(fields.Datetime.now(),self.env.user.display_name))
        )
        return{'attachment':attachment}

    def_is_commercial_partner_pa(self):
        """
            ReturnsTrueifthedestinationoftheFatturaPAbelongstothePublicAdministration.
        """
        returnlen(self.commercial_partner_id.l10n_it_pa_indexor'') ==6

    def_l10n_it_edi_prepare_fatturapa_line_details(self,reverse_charge_refund=False,is_downpayment=False,convert_to_euros=True):
        """Returnsalistofdictionariespassedtothetemplatefortheinvoicelines(DettaglioLinee)
        """
        invoice_lines=[]
        lines=self.invoice_line_ids.filtered(lambdal:notl.display_type)

        fornum,lineinenumerate(lines):
            sign=-1ifline.move_id.is_inbound()else1
            price_subtotal=(line.balance*sign)ifconvert_to_euroselseline.price_subtotal
            #Theprice_subtotalshouldbeinvertedwhenthelineisareversechargerefund.
            ifreverse_charge_refund:
                price_subtotal=-price_subtotal

            #Unitprice
            price_unit=0
            ifline.quantityandline.discount!=100.0:
                price_unit=price_subtotal/((1-(line.discountor0.0)/100.0)*abs(line.quantity))
            else:
                price_unit=line.price_unit

            description=line.name
            ifnotis_downpayment:
                ifline.price_subtotal<0:
                    moves=line._get_downpayment_lines().move_id
                    ifmoves:
                        description+=','.join([move.nameformoveinmoves])

            line_dict={
                'line':line,
                'line_number':num+1,
                'description':descriptionor'NONAME',
                'unit_price':price_unit,
                'subtotal_price':price_subtotal,
            }
            invoice_lines.append(line_dict)
        returninvoice_lines

    def_l10n_it_edi_prepare_fatturapa_tax_details(self,tax_details,reverse_charge_refund=False):
        """Returnsanadapteddictionarypassedtothetemplateforthetaxlines(DatiRiepilogo)
        """
        for_tax_name,tax_dictintax_details['tax_details'].items():
            #TheassumptionisthatthecompanycurrencyisEUR.
            base_amount=tax_dict['base_amount']
            base_amount_currency=tax_dict['base_amount_currency']
            tax_amount=tax_dict['tax_amount']
            tax_amount_currency=tax_dict['tax_amount_currency']
            tax_rate=tax_dict['tax'].amount
            expected_base_amount_currency=tax_amount_currency*100/tax_rateiftax_rateelseFalse
            expected_base_amount=tax_amount*100/tax_rateiftax_rateelseFalse
            #Constraintswithintheedimakelocalroundingonpriceincludedtaxesaproblem.
            #Tosolvethisthereisa<Arrotondamento>or'rounding'field,suchthat:
            #  taxablebase=sum(taxablebaseforeachunit)+Arrotondamento
            iftax_dict['tax'].price_includeandtax_dict['tax'].amount_type=='percent':
                ifexpected_base_amount_currencyandfloat_compare(base_amount_currency,expected_base_amount_currency,2):
                    tax_dict['rounding']=base_amount_currency-(tax_amount_currency*100/tax_rate)
                    tax_dict['base_amount_currency']=base_amount_currency-tax_dict['rounding']
                ifexpected_base_amountandfloat_compare(base_amount,expected_base_amount,2):
                    tax_dict['rounding_euros']=base_amount-(tax_amount*100/tax_rate)
                    tax_dict['base_amount']=base_amount-tax_dict['rounding_euros']

            ifnotreverse_charge_refund:
                balance_multiplicator=-1ifself.is_inbound()else1
                iftax_dict['base_amount']!=0: #Weshouldn'tchange0into-0
                    tax_dict['base_amount']*=balance_multiplicator
                iftax_dict['base_amount_currency']!=0:
                    tax_dict['base_amount_currency']*=balance_multiplicator
                iftax_dict['tax_amount']!=0:
                    tax_dict['tax_amount']*=balance_multiplicator
                iftax_dict['tax_amount_currency']!=0:
                    tax_dict['tax_amount_currency']*=balance_multiplicator
        returntax_details

    def_prepare_fatturapa_export_values(self):
        self.ensure_one()

        defformat_date(dt):
            #Formatthedateintheitalianstandard.
            dt=dtordatetime.now()
            returndt.strftime(DEFAULT_FACTUR_ITALIAN_DATE_FORMAT)

        defformat_monetary(number,currency):
            #Formatthemonetaryvaluestoavoidtrailingdecimals(e.g.90.85000000000001).
            returnfloat_repr(number,min(2,currency.decimal_places))

        defformat_numbers(number):
            #formatnumbertostrwithbetween2and8decimals(eventifit's.00)
            number_splited=str(number).split('.')
            iflen(number_splited)==1:
                return"%.02f"%number

            cents=number_splited[1]
            iflen(cents)>8:
                return"%.08f"%number
            returnfloat_repr(number,max(2,len(cents)))

        defformat_numbers_two(number):
            #formatnumbertostrwith2(eventifit's.00)
            return"%.02f"%number

        defdiscount_type(discount):
            return'SC'ifdiscount>0else'MG'

        defformat_phone(number):
            ifnotnumber:
                returnFalse
            number=number.replace('','').replace('/','').replace('.','')
            iflen(number)>4andlen(number)<13:
                returnnumber
            returnFalse

        defget_vat_number(vat):
            ifvat[:2].isdecimal():
                returnvat.replace('','')
            returnvat[2:].replace('','')

        defget_vat_country(vat):
            ifvat[:2].isdecimal():
                return'IT'
            returnvat[:2].upper()

        defformat_alphanumeric(text_to_convert):
            returntext_to_convert.encode('latin-1','replace').decode('latin-1')iftext_to_convertelseFalse

        formato_trasmissione="FPA12"ifself._is_commercial_partner_pa()else"FPR12"

        #Flags
        in_eu=self.env['account.edi.format']._l10n_it_edi_partner_in_eu
        is_self_invoice=self.env['account.edi.format']._l10n_it_edi_is_self_invoice(self)
        document_type=self.env['account.edi.format']._l10n_it_get_document_type(self)
        ifself.env['account.edi.format']._l10n_it_is_simplified_document_type(document_type):
            formato_trasmissione="FSM10"

        document_type=self.env['account.edi.format']._l10n_it_get_document_type(self)
        #Representifthedocumentisareversechargerefundinasinglevariable
        reverse_charge=document_typein['TD17','TD18','TD19']
        is_downpayment=document_typein['TD02']
        reverse_charge_refund=self.move_type=='in_refund'andreverse_charge
        convert_to_euros=self.currency_id.name!='EUR'

        pdf=self.env.ref('account.account_invoices')._render_qweb_pdf(self.id)[0]
        pdf=base64.b64encode(pdf)
        pdf_name=re.sub(r'\W+','',self.name)+'.pdf'

        #taxmapfor0%taxeswhichhavenotax_line_id
        tax_map=dict()
        forlineinself.line_ids:
            fortaxinline.tax_ids:
                iftax.amount==0.0:
                    tax_map[tax]=tax_map.get(tax,0.0)+line.price_subtotal

        tax_details=self._prepare_edi_tax_details(
            filter_to_apply=lambdal:l['tax_repartition_line_id'].factor_percent>=0
        )

        company=self.company_id
        partner=self.commercial_partner_id
        buyer=partnerifnotis_self_invoiceelsecompany
        seller=companyifnotis_self_invoiceelsepartner
        codice_destinatario=(
            (is_self_invoiceandcompany.partner_id.l10n_it_pa_index)
            orpartner.l10n_it_pa_index
            or(partner.country_id.code=='IT'and'0000000')
            or'XXXXXXX')

        #Self-invoicesaretechnically-100%/+100%repartitioned
        #butfunctionallyneedtobeexportedas100%
        document_total=self.amount_total
        ifis_self_invoice:
            document_total+=sum([abs(v['tax_amount_currency'])fork,vintax_details['tax_details'].items()])
            ifreverse_charge_refund:
                document_total=-abs(document_total)

        #Referencelineforfindingtheconversionrateusedinthedocument
        conversion_line=self.invoice_line_ids.sorted(lambdal:abs(l.balance),reverse=True)[0]ifself.invoice_line_idselseNone
        conversion_rate=float_repr(
            abs(conversion_line.balance/conversion_line.amount_currency),precision_digits=5,
        )ifconvert_to_eurosandconversion_lineelseNone

        invoice_lines=self._l10n_it_edi_prepare_fatturapa_line_details(reverse_charge_refund,is_downpayment,convert_to_euros)
        tax_details=self._l10n_it_edi_prepare_fatturapa_tax_details(tax_details,reverse_charge_refund)

        #Createfilecontent.
        template_values={
            'record':self,
            'company':company,
            'sender':company,
            'sender_partner':company.partner_id,
            'partner':partner,
            'buyer':buyer,
            'buyer_partner':partnerifnotis_self_invoiceelsecompany.partner_id,
            'buyer_is_company':is_self_invoiceorpartner.is_company,
            'seller':seller,
            'seller_partner':company.partner_idifnotis_self_invoiceelsepartner,
            'currency':self.currency_idorself.company_currency_idifnotconvert_to_euroselseself.env.ref('base.EUR'),
            'document_total':document_total,
            'representative':company.l10n_it_tax_representative_partner_id,
            'codice_destinatario':codice_destinatario,
            'regime_fiscale':company.l10n_it_tax_systemifnotis_self_invoiceelse'RF18',
            'is_self_invoice':is_self_invoice,
            'partner_bank':self.partner_bank_id,
            'format_date':format_date,
            'format_monetary':format_monetary,
            'format_numbers':format_numbers,
            'format_numbers_two':format_numbers_two,
            'format_phone':format_phone,
            'format_alphanumeric':format_alphanumeric,
            'discount_type':discount_type,
            'formato_trasmissione':formato_trasmissione,
            'document_type':document_type,
            'pdf':pdf,
            'pdf_name':pdf_name,
            'tax_map':tax_map,
            'tax_details':tax_details,
            'abs':abs,
            'normalize_codice_fiscale':partner._l10n_it_normalize_codice_fiscale,
            'get_vat_number':get_vat_number,
            'get_vat_country':get_vat_country,
            'in_eu':in_eu,
            'rc_refund':reverse_charge_refund,
            'invoice_lines':invoice_lines,
            'conversion_rate':conversion_rate,
        }
        returntemplate_values

    def_export_as_xml(self):
        '''DEPRECATED:thiswillbemovedtoAccountEdiFormatinafutureversion.
        Createthexmlfilecontent.
        :return:TheXMLcontentasstr.
        '''
        template_values=self._prepare_fatturapa_export_values()
        ifnotself.env['account.edi.format']._l10n_it_is_simplified_document_type(template_values['document_type']):
            content=self.env.ref('l10n_it_edi.account_invoice_it_FatturaPA_export')._render(template_values)
        else:
            content=self.env.ref('l10n_it_edi.account_invoice_it_simplified_FatturaPA_export')._render(template_values)
            self.message_post(body=_("Asimplifiedinvoicewascreatedinsteadofanordinaryone.Thisisbecausetheinvoice\
                                    isadomesticinvoicewithatotalamountoflessthanorequalto400€andthecustomer'saddressisincomplete."))
        returncontent

    def_post(self,soft=True):
        #OVERRIDE
        posted=super()._post(soft=soft)

        formoveinposted.filtered(lambdam:m.l10n_it_send_state=='to_send'andm.move_typein['out_invoice','out_refund']andm.company_id.country_id.code=='IT'):
            move.send_pec_mail()

        returnposted

    defsend_pec_mail(self):
        self.ensure_one()
        allowed_state=['to_send','invalid']

        if(
            notself.company_id.l10n_it_mail_pec_server_id
            ornotself.company_id.l10n_it_mail_pec_server_id.active
            ornotself.company_id.l10n_it_address_send_fatturapa
        ):
            self.message_post(
                body=(_("ErrorwhensendingmailwithE-Invoice:YourcompanymusthaveamailPECserverandmustindicatethemailPECthatwillsendelectronicinvoice."))
                )
            self.l10n_it_send_state='invalid'
            return

        ifself.l10n_it_send_statenotinallowed_state:
            raiseUserError(_("%sisn'tinarightstate.Itmustbeina'Notyetsend'or'Invalid'state.")%(self.display_name))

        message=self.env['mail.message'].create({
            'subject':_('Sendingfile:%s')%(self.l10n_it_einvoice_name),
            'body':_('Sendingfile:%stoES:%s')%(self.l10n_it_einvoice_name,self.env.company.l10n_it_address_recipient_fatturapa),
            'author_id':self.env.user.partner_id.id,
            'email_from':self.env.company.l10n_it_address_send_fatturapa,
            'reply_to':self.env.company.l10n_it_address_send_fatturapa,
            'mail_server_id':self.env.company.l10n_it_mail_pec_server_id.id,
            'attachment_ids':[(6,0,self.l10n_it_einvoice_id.ids)],
        })

        mail_fattura=self.env['mail.mail'].sudo().with_context(wo_bounce_return_path=True).create({
            'mail_message_id':message.id,
            'email_to':self.env.company.l10n_it_address_recipient_fatturapa,
        })
        try:
            mail_fattura.send(raise_exception=True)
            self.message_post(
                body=(_("Mailsenton%sby%s")%(fields.Datetime.now(),self.env.user.display_name))
                )
            self.l10n_it_send_state='sent'
        exceptMailDeliveryExceptionaserror:
            self.message_post(
                body=(_("ErrorwhensendingmailwithE-Invoice:%s")%(error.args[0]))
                )
            self.l10n_it_send_state='invalid'

    def_compose_info_message(self,tree,element_tags):
        output_str=""
        elements=tree.xpath(element_tags)
        forelementinelements:
            output_str+="<ul>"
            forlineinelement.iter():
                ifline.text:
                    text="".join(line.text.split())
                    iftext:
                        output_str+="<li>%s:%s</li>"%(line.tag,text)
            output_str+="</ul>"
        returnoutput_str

    def_compose_multi_info_message(self,tree,element_tags):
        output_str="<ul>"

        forelement_taginelement_tags:
            elements=tree.xpath(element_tag)
            ifnotelements:
                continue
            forelementinelements:
                text="".join(element.text.split())
                iftext:
                    output_str+="<li>%s:%s</li>"%(element.tag,text)
        returnoutput_str+"</ul>"

classAccountTax(models.Model):
    _name="account.tax"
    _inherit="account.tax"

    l10n_it_vat_due_date=fields.Selection([
        ("I","[I]IVAadesigibilitàimmediata"),
        ("D","[D]IVAadesigibilitàdifferita"),
        ("S","[S]Scissionedeipagamenti")],default="I",string="VATduedate")

    l10n_it_has_exoneration=fields.Boolean(string="Hasexonerationoftax(Italy)",help="Taxhasataxexoneration.")
    l10n_it_kind_exoneration=fields.Selection(selection=[
            ("N1","[N1]Escluseexart.15"),
            ("N2","[N2]Nonsoggette"),
            ("N2.1","[N2.1]NonsoggetteadIVAaisensidegliartt.Da7a7-septiesdelDPR633/72"),
            ("N2.2","[N2.2]Nonsoggette–altricasi"),
            ("N3","[N3]Nonimponibili"),
            ("N3.1","[N3.1]Nonimponibili–esportazioni"),
            ("N3.2","[N3.2]Nonimponibili–cessioniintracomunitarie"),
            ("N3.3","[N3.3]Nonimponibili–cessioniversoSanMarino"),
            ("N3.4","[N3.4]Nonimponibili–operazioniassimilateallecessioniall’esportazione"),
            ("N3.5","[N3.5]Nonimponibili–aseguitodidichiarazionid’intento"),
            ("N3.6","[N3.6]Nonimponibili–altreoperazionichenonconcorronoallaformazionedelplafond"),
            ("N4","[N4]Esenti"),
            ("N5","[N5]Regimedelmargine/IVAnonespostainfattura"),
            ("N6","[N6]Inversionecontabile(perleoperazioniinreversechargeovveroneicasidiautofatturazioneperacquistiextraUEdiserviziovveroperimportazionidibenineisolicasiprevisti)"),
            ("N6.1","[N6.1]Inversionecontabile–cessionedirottamiealtrimaterialidirecupero"),
            ("N6.2","[N6.2]Inversionecontabile–cessionedioroeargentopuro"),
            ("N6.3","[N6.3]Inversionecontabile–subappaltonelsettoreedile"),
            ("N6.4","[N6.4]Inversionecontabile–cessionedifabbricati"),
            ("N6.5","[N6.5]Inversionecontabile–cessioneditelefonicellulari"),
            ("N6.6","[N6.6]Inversionecontabile–cessionediprodottielettronici"),
            ("N6.7","[N6.7]Inversionecontabile–prestazionicompartoedileesettoriconnessi"),
            ("N6.8","[N6.8]Inversionecontabile–operazionisettoreenergetico"),
            ("N6.9","[N6.9]Inversionecontabile–altricasi"),
            ("N7","[N7]IVAassoltainaltrostatoUE(venditeadistanzaexart.40c.3e4eart.41c.1lett.b, DL331/93;prestazionediserviziditelecomunicazioni,tele-radiodiffusioneedelettroniciexart.7-sexieslett.f,g,art.74-sexiesDPR633/72)")],
        string="Exoneration",
        help="Exonerationtype",
        default="N1")
    l10n_it_law_reference=fields.Char(string="LawReference",size=100)

    @api.constrains('l10n_it_has_exoneration',
                    'l10n_it_kind_exoneration',
                    'l10n_it_law_reference',
                    'amount',
                    'l10n_it_vat_due_date')
    def_check_exoneration_with_no_tax(self):
        fortaxinself:
            iftax.l10n_it_has_exoneration:
                ifnottax.l10n_it_kind_exonerationornottax.l10n_it_law_referenceortax.amount!=0:
                    raiseValidationError(_("Ifthetaxhasexoneration,youmustenterakindofexoneration,alawreferenceandtheamountofthetaxmustbe0.0."))
                iftax.l10n_it_kind_exoneration=='N6'andtax.l10n_it_vat_due_date=='S':
                    raiseUserError(_("'Scissionedeipagamenti'isnotcompatiblewithexonerationofkind'N6'"))
