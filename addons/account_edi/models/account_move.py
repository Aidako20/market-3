#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfrozendict


classAccountMove(models.Model):
    _inherit='account.move'

    edi_document_ids=fields.One2many(
        comodel_name='account.edi.document',
        inverse_name='move_id')
    edi_state=fields.Selection(
        selection=[('to_send','ToSend'),('sent','Sent'),('to_cancel','ToCancel'),('cancelled','Cancelled')],
        string="Electronicinvoicing",
        store=True,
        compute='_compute_edi_state',
        help='TheaggregatedstateofalltheEDIsofthismove')
    edi_error_count=fields.Integer(
        compute='_compute_edi_error_count',
        help='HowmanyEDIsareinerrorforthismove?')
    edi_web_services_to_process=fields.Text(
        compute='_compute_edi_web_services_to_process',
        help="TechnicalfieldtodisplaythedocumentsthatwillbeprocessedbytheCRON")
    edi_show_cancel_button=fields.Boolean(
        compute='_compute_edi_show_cancel_button')

    @api.depends('edi_document_ids.state')
    def_compute_edi_state(self):
        formoveinself:
            all_states=set(move.edi_document_ids.filtered(lambdad:d.edi_format_id._needs_web_services()).mapped('state'))
            ifall_states=={'sent'}:
                move.edi_state='sent'
            elifall_states=={'cancelled'}:
                move.edi_state='cancelled'
            elif'to_send'inall_states:
                move.edi_state='to_send'
            elif'to_cancel'inall_states:
                move.edi_state='to_cancel'
            else:
                move.edi_state=False

    @api.depends('edi_document_ids.error')
    def_compute_edi_error_count(self):
        formoveinself:
            move.edi_error_count=len(move.edi_document_ids.filtered(lambdad:d.error))

    @api.depends(
        'edi_document_ids',
        'edi_document_ids.state',
        'edi_document_ids.edi_format_id',
        'edi_document_ids.edi_format_id.name')
    def_compute_edi_web_services_to_process(self):
        formoveinself:
            to_process=move.edi_document_ids.filtered(lambdad:d.statein['to_send','to_cancel'])
            format_web_services=to_process.edi_format_id.filtered(lambdaf:f._needs_web_services())
            move.edi_web_services_to_process=','.join(f.nameforfinformat_web_services)

    @api.depends('restrict_mode_hash_table','state')
    def_compute_show_reset_to_draft_button(self):
        #OVERRIDE
        super()._compute_show_reset_to_draft_button()

        formoveinself:
            fordocinmove.edi_document_ids:
                ifdoc.edi_format_id._needs_web_services()\
                        anddoc.attachment_id\
                        anddoc.statein('sent','to_cancel')\
                        andmove.is_invoice(include_receipts=True)\
                        anddoc.edi_format_id._is_required_for_invoice(move):
                    move.show_reset_to_draft_button=False
                    break

    @api.depends(
        'state',
        'edi_document_ids.state',
        'edi_document_ids.attachment_id')
    def_compute_edi_show_cancel_button(self):
        formoveinself:
            ifmove.state!='posted':
                move.edi_show_cancel_button=False
                continue

            move.edi_show_cancel_button=any([doc.edi_format_id._needs_web_services()
                                               anddoc.attachment_id
                                               anddoc.state=='sent'
                                               andmove.is_invoice(include_receipts=True)
                                               anddoc.edi_format_id._is_required_for_invoice(move)
                                              fordocinmove.edi_document_ids])

    ####################################################
    #ExportElectronicDocument
    ####################################################

    @api.model
    def_add_edi_tax_values(self,results,grouping_key,serialized_grouping_key,tax_values):
        #Addtoglobalresults.
        results['tax_amount']+=tax_values['tax_amount']
        results['tax_amount_currency']+=tax_values['tax_amount_currency']

        #Addtotaxdetails.
        tax_details=results['tax_details'][serialized_grouping_key]
        tax_details.update(grouping_key)
        iftax_values['base_line_id']notinset(x['base_line_id']forxintax_details['group_tax_details']):
            tax_details['base_amount']+=tax_values['base_amount']
            tax_details['base_amount_currency']+=tax_values['base_amount_currency']

        tax_details['tax_amount']+=tax_values['tax_amount']
        tax_details['tax_amount_currency']+=tax_values['tax_amount_currency']
        tax_details['exemption_reason']=tax_values['tax_id'].name
        tax_details['group_tax_details'].append(tax_values)

    def_prepare_edi_tax_details(self,filter_to_apply=None,filter_invl_to_apply=None,grouping_key_generator=None):
        '''Computeamountsrelatedtotaxesforthecurrentinvoice.
        :paramfilter_to_apply:        Optionalfiltertoexcludesometaxvaluesfromthefinalresults.
                                        Thefilterisdefinedasamethodgettingadictionaryasparameter
                                        representingthetaxvaluesforasinglerepartitionline.
                                        Thisdictionarycontains:
            'base_line_id':            Anaccount.move.linerecord.
            'tax_id':                  Anaccount.taxrecord.
            'tax_repartition_line_id': Anaccount.tax.repartition.linerecord.
            'base_amount':             Thetaxbaseamountexpressedincompanycurrency.
            'tax_amount':              Thetaxamountexpressedincompanycurrency.
            'base_amount_currency':    Thetaxbaseamountexpressedinforeigncurrency.
            'tax_amount_currency':     Thetaxamountexpressedinforeigncurrency.
                                        IfthefilterisreturningFalse,itmeansthecurrenttaxvalueswillbe
                                        ignoredwhencomputingthefinalresults.
        :paramgrouping_key_generator: Optionalmethodusedtogrouptaxvaluestogether.Bydefault,thetaxvalues
                                        aregroupedbytax.Thisparameterisamethodgettingadictionaryasparameter
                                        (samesignatureas'filter_to_apply').
                                        Thismethodmustreturnsadictionarywherevalueswillbeusedtocreatethe
                                        grouping_keytoaggregatetaxvaluestogether.Thereturneddictionaryisadded
                                        toeachtaxdetailsinordertoretrievethefullgrouping_keylater.
        :return:                       Thefulltaxdetailsforthecurrentinvoiceandforeachinvoiceline
                                        separately.Thereturneddictionaryisthefollowing:
            'base_amount':             Thetotaltaxbaseamountincompanycurrencyforthewholeinvoice.
            'tax_amount':              Thetotaltaxamountincompanycurrencyforthewholeinvoice.
            'base_amount_currency':    Thetotaltaxbaseamountinforeigncurrencyforthewholeinvoice.
            'tax_amount_currency':     Thetotaltaxamountinforeigncurrencyforthewholeinvoice.
            'tax_details':             Amappingofeachgroupingkey(see'grouping_key_generator')toadictionary
                                        containing:
                'base_amount':             Thetaxbaseamountincompanycurrencyforthecurrentgroup.
                'tax_amount':              Thetaxamountincompanycurrencyforthecurrentgroup.
                'base_amount_currency':    Thetaxbaseamountinforeigncurrencyforthecurrentgroup.
                'tax_amount_currency':     Thetaxamountinforeigncurrencyforthecurrentgroup.
                'group_tax_details':       Thelistofalltaxvaluesaggregatedintothisgroup.
            'invoice_line_tax_details':Amappingofeachinvoicelinetoadictionarycontaining:
                'base_amount':         Thetotaltaxbaseamountincompanycurrencyforthewholeinvoiceline.
                'tax_amount':          Thetotaltaxamountincompanycurrencyforthewholeinvoiceline.
                'base_amount_currency':Thetotaltaxbaseamountinforeigncurrencyforthewholeinvoiceline.
                'tax_amount_currency': Thetotaltaxamountinforeigncurrencyforthewholeinvoiceline.
                'tax_details':         Amappingofeachgroupingkey(see'grouping_key_generator')toadictionary
                                        containing:
                    'base_amount':         Thetaxbaseamountincompanycurrencyforthecurrentgroup.
                    'tax_amount':          Thetaxamountincompanycurrencyforthecurrentgroup.
                    'base_amount_currency':Thetaxbaseamountinforeigncurrencyforthecurrentgroup.
                    'tax_amount_currency': Thetaxamountinforeigncurrencyforthecurrentgroup.
                    'group_tax_details':   Thelistofalltaxvaluesaggregatedintothisgroup.
        '''
        self.ensure_one()

        defdefault_grouping_key_generator(tax_values):
            return{'tax':tax_values['tax_id']}

        #Computethetaxesvaluesforeachinvoiceline.

        invoice_lines=self.invoice_line_ids.filtered(lambdaline:notline.display_type)
        iffilter_invl_to_apply:
            invoice_lines=invoice_lines.filtered(filter_invl_to_apply)

        invoice_lines_tax_values_dict={}
        sign=-1ifself.is_inbound()else1
        forinvoice_lineininvoice_lines:
            taxes_res=invoice_line.tax_ids.compute_all(
                invoice_line.price_unit*(1-(invoice_line.discount/100.0)),
                currency=invoice_line.currency_id,
                quantity=invoice_line.quantity,
                product=invoice_line.product_id,
                partner=invoice_line.partner_id,
                is_refund=invoice_line.move_id.move_typein('in_refund','out_refund'),
            )
            tax_values_list=invoice_lines_tax_values_dict[invoice_line]=[]
            rate=abs(invoice_line.balance)/abs(invoice_line.amount_currency)ifinvoice_line.amount_currencyelse0.0
            fortax_resintaxes_res['taxes']:
                tax_amount=tax_res['amount']*rate
                ifself.company_id.tax_calculation_rounding_method=='round_per_line':
                    tax_amount=invoice_line.company_currency_id.round(tax_amount)
                tax_values_list.append({
                    'base_line_id':invoice_line,
                    'tax_id':self.env['account.tax'].browse(tax_res['id']),
                    'tax_repartition_line_id':self.env['account.tax.repartition.line'].browse(tax_res['tax_repartition_line_id']),
                    'base_amount':sign*invoice_line.company_currency_id.round(tax_res['base']*rate),
                    'tax_amount':sign*tax_amount,
                    'base_amount_currency':sign*tax_res['base'],
                    'tax_amount_currency':sign*tax_res['amount'],
                })
        grouping_key_generator=grouping_key_generatorordefault_grouping_key_generator

        #Apply'filter_to_apply'.

        iffilter_to_apply:
            invoice_lines_tax_values_dict={
                invoice_line:[xforxintax_values_listiffilter_to_apply(x)]
                forinvoice_line,tax_values_listininvoice_lines_tax_values_dict.items()
            }

        #Initializetheresultsdict.

        invoice_global_tax_details={
            'base_amount':0.0,
            'tax_amount':0.0,
            'base_amount_currency':0.0,
            'tax_amount_currency':0.0,
            'tax_details':defaultdict(lambda:{
                'base_amount':0.0,
                'tax_amount':0.0,
                'base_amount_currency':0.0,
                'tax_amount_currency':0.0,
                'group_tax_details':[],
            }),
            'invoice_line_tax_details':defaultdict(lambda:{
                'base_amount':0.0,
                'tax_amount':0.0,
                'base_amount_currency':0.0,
                'tax_amount_currency':0.0,
                'tax_details':defaultdict(lambda:{
                    'base_amount':0.0,
                    'tax_amount':0.0,
                    'base_amount_currency':0.0,
                    'tax_amount_currency':0.0,
                    'group_tax_details':[],
                }),
            }),
        }

        #Apply'grouping_key_generator'to'invoice_lines_tax_values_list'andaddallvaluestothefinalresults.

        forinvoice_lineininvoice_lines:
            tax_values_list=invoice_lines_tax_values_dict[invoice_line]

            #Addtoinvoiceglobaltaxamounts.
            invoice_global_tax_details['base_amount']+=invoice_line.balance
            invoice_global_tax_details['base_amount_currency']+=invoice_line.amount_currency

            fortax_valuesintax_values_list:
                grouping_key=grouping_key_generator(tax_values)
                serialized_grouping_key=frozendict(grouping_key)

                #Addtoinvoicelineglobaltaxamounts.
                ifserialized_grouping_keynotininvoice_global_tax_details['invoice_line_tax_details'][invoice_line]:
                    invoice_line_global_tax_details=invoice_global_tax_details['invoice_line_tax_details'][invoice_line]
                    invoice_line_global_tax_details.update({
                        'base_amount':invoice_line.balance,
                        'base_amount_currency':invoice_line.amount_currency,
                    })
                else:
                    invoice_line_global_tax_details=invoice_global_tax_details['invoice_line_tax_details'][invoice_line]

                self._add_edi_tax_values(invoice_global_tax_details,grouping_key,serialized_grouping_key,tax_values)
                self._add_edi_tax_values(invoice_line_global_tax_details,grouping_key,serialized_grouping_key,tax_values)

        returninvoice_global_tax_details

    def_prepare_edi_vals_to_export(self):
        '''ThepurposeofthishelperistopreparevaluesinordertoexportaninvoicethroughtheEDIsystem.
        Thisincludesthecomputationofthetaxdetailsforeachinvoicelinethatcouldbeverydifficultto
        handleregardingthecomputationofthebaseamount.
        :return:Apythondictcontainingdefaultpre-processedvalues.
        '''
        self.ensure_one()

        res={
            'record':self,
            'balance_multiplicator':-1ifself.is_inbound()else1,
            'invoice_line_vals_list':[],
        }

        #Invoicelinesdetails.
        forindex,lineinenumerate(self.invoice_line_ids.filtered(lambdaline:notline.display_type),start=1):
            line_vals=line._prepare_edi_vals_to_export()
            line_vals['index']=index
            res['invoice_line_vals_list'].append(line_vals)

        #Totals.
        res.update({
            'total_price_subtotal_before_discount':sum(x['price_subtotal_before_discount']forxinres['invoice_line_vals_list']),
            'total_price_discount':sum(x['price_discount']forxinres['invoice_line_vals_list']),
        })

        returnres

    def_update_payments_edi_documents(self):
        '''Updatetheedidocumentslinkedtothecurrentjournalentries.Thesejournalentriesmustbelinkedtoan
        account.paymentofanaccount.bank.statement.line.Thisadditionalmethodisneededbecausethepaymentflowis
        notthesameastheinvoiceone.Indeed,theedidocumentsmustbeupdatedwhenthereconciliationwithsome
        invoicesischanging.
        '''
        edi_document_vals_list=[]
        forpaymentinself:
            edi_formats=payment._get_reconciled_invoices().journal_id.edi_format_ids+payment.edi_document_ids.edi_format_id
            edi_formats=self.env['account.edi.format'].browse(edi_formats.ids)#Avoidduplicates
            foredi_formatinedi_formats:
                existing_edi_document=payment.edi_document_ids.filtered(lambdax:x.edi_format_id==edi_format)

                ifedi_format._is_required_for_payment(payment):
                    ifexisting_edi_document:
                        existing_edi_document.write({
                            'state':'to_send',
                            'error':False,
                            'blocking_level':False,
                        })
                    else:
                        edi_document_vals_list.append({
                            'edi_format_id':edi_format.id,
                            'move_id':payment.id,
                            'state':'to_send',
                        })
                elifexisting_edi_document:
                    existing_edi_document.write({
                        'state':False,
                        'error':False,
                        'blocking_level':False,
                    })

        self.env['account.edi.document'].create(edi_document_vals_list)
        self.edi_document_ids._process_documents_no_web_services()

    def_post(self,soft=True):
        #OVERRIDE
        #Settheelectronicdocumenttobepostedandpostimmediatelyforsynchronousformats.
        posted=super()._post(soft=soft)

        edi_document_vals_list=[]
        formoveinposted:
            foredi_formatinmove.journal_id.edi_format_ids:
                is_edi_needed=move.is_invoice(include_receipts=False)andedi_format._is_required_for_invoice(move)

                ifis_edi_needed:
                    errors=edi_format._check_move_configuration(move)
                    iferrors:
                        raiseUserError(_("Invalidinvoiceconfiguration:\n\n%s")%'\n'.join(errors))

                    existing_edi_document=move.edi_document_ids.filtered(lambdax:x.edi_format_id==edi_format)
                    ifexisting_edi_document:
                        existing_edi_document.write({
                            'state':'to_send',
                            'attachment_id':False,
                        })
                    else:
                        edi_document_vals_list.append({
                            'edi_format_id':edi_format.id,
                            'move_id':move.id,
                            'state':'to_send',
                        })

        self.env['account.edi.document'].create(edi_document_vals_list)
        posted.edi_document_ids._process_documents_no_web_services()
        returnposted

    defbutton_cancel(self):
        #OVERRIDE
        #Settheelectronicdocumenttobecanceledandcancelimmediatelyforsynchronousformats.
        res=super().button_cancel()

        self.edi_document_ids.filtered(lambdadoc:doc.attachment_id).write({'state':'to_cancel','error':False,'blocking_level':False})
        self.edi_document_ids.filtered(lambdadoc:notdoc.attachment_id).write({'state':'cancelled','error':False,'blocking_level':False})
        self.edi_document_ids._process_documents_no_web_services()

        returnres

    defbutton_draft(self):
        #OVERRIDE
        formoveinself:
            ifmove.edi_show_cancel_button:
                raiseUserError(_(
                    "Youcan'teditthefollowingjournalentry%sbecauseanelectronicdocumenthasalreadybeen"
                    "sent.Pleaseusethe'RequestEDICancellation'buttoninstead."
                )%move.display_name)

        res=super().button_draft()

        self.edi_document_ids.write({'state':False,'error':False,'blocking_level':False})

        returnres

    defbutton_cancel_posted_moves(self):
        '''Marktheedi.documentrelatedtothismovetobecanceled.
        '''
        to_cancel_documents=self.env['account.edi.document']
        formoveinself:
            move._check_fiscalyear_lock_date()
            is_move_marked=False
            fordocinmove.edi_document_ids:
                ifdoc.edi_format_id._needs_web_services()\
                        anddoc.attachment_id\
                        anddoc.state=='sent'\
                        andmove.is_invoice(include_receipts=True)\
                        anddoc.edi_format_id._is_required_for_invoice(move):
                    to_cancel_documents|=doc
                    is_move_marked=True
            ifis_move_marked:
                move.message_post(body=_("AcancellationoftheEDIhasbeenrequested."))

        to_cancel_documents.write({'state':'to_cancel','error':False,'blocking_level':False})

    def_get_edi_document(self,edi_format):
        returnself.edi_document_ids.filtered(lambdad:d.edi_format_id==edi_format)

    def_get_edi_attachment(self,edi_format):
        returnself._get_edi_document(edi_format).attachment_id

    ####################################################
    #ImportElectronicDocument
    ####################################################

    def_get_create_invoice_from_attachment_decoders(self):
        #OVERRIDE
        res=super()._get_create_invoice_from_attachment_decoders()
        res.append((10,self.env['account.edi.format'].search([])._create_invoice_from_attachment))
        returnres

    def_get_update_invoice_from_attachment_decoders(self,invoice):
        #OVERRIDE
        res=super()._get_update_invoice_from_attachment_decoders(invoice)
        res.append((10,self.env['account.edi.format'].search([])._update_invoice_from_attachment))
        returnres

    ####################################################
    #Businessoperations
    ####################################################

    defaction_process_edi_web_services(self):
        docs=self.edi_document_ids.filtered(lambdad:d.statein('to_send','to_cancel'))
        if'blocking_level'inself.env['account.edi.document']._fields:
            docs=docs.filtered(lambdad:d.blocking_level!='error')
        docs._process_documents_web_services(with_commit=False)

classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    ####################################################
    #ExportElectronicDocument
    ####################################################

    def_prepare_edi_vals_to_export(self):
        '''Thepurposeofthishelperisthesameas'_prepare_edi_vals_to_export'butforasingleinvoiceline.
        Thisincludesthecomputationofthetaxdetailsforeachinvoicelineorthemanagementofthediscount.
        Indeed,insomeEDI,weneedtoprovideextravaluesdependingthediscountsuchas:
        -thediscountasanamountinsteadofapercentage.
        -theprice_unitbutaftersubtractionofthediscount.
        :return:Apythondictcontainingdefaultpre-processedvalues.
        '''
        self.ensure_one()

        ifself.discount==100.0:
            gross_price_subtotal=self.currency_id.round(self.price_unit*self.quantity)
        else:
            gross_price_subtotal=self.currency_id.round(self.price_subtotal/(1-self.discount/100.0))

        res={
            'line':self,
            'price_unit_after_discount':self.currency_id.round(self.price_unit*(1-(self.discount/100.0))),
            'price_subtotal_before_discount':gross_price_subtotal,
            'price_subtotal_unit':self.currency_id.round(self.price_subtotal/self.quantity)ifself.quantityelse0.0,
            'price_total_unit':self.currency_id.round(self.price_total/self.quantity)ifself.quantityelse0.0,
            'price_discount':gross_price_subtotal-self.price_subtotal,
            'price_discount_unit':(gross_price_subtotal-self.price_subtotal)/self.quantityifself.quantityelse0.0,
            'gross_price_total_unit':self.currency_id.round(gross_price_subtotal/self.quantity)ifself.quantityelse0.0,
            'unece_uom_code':self.product_id.product_tmpl_id.uom_id._get_unece_code(),
        }
        returnres

    defreconcile(self):
        #OVERRIDE
        #Insomecountries,thepaymentsmustbesenttothegovernmentundersomecondition.Oneofthemcouldbe
        #thereisatleastonereconciledinvoicetothepayment.Then,weneedtoupdatethestateoftheedi
        #documentsduringthereconciliation.
        all_lines=self+self.matched_debit_ids.debit_move_id+self.matched_credit_ids.credit_move_id
        payments=all_lines.move_id.filtered(lambdamove:move.payment_idormove.statement_line_id)

        invoices_per_payment_before={pay:pay._get_reconciled_invoices()forpayinpayments}
        res=super().reconcile()
        invoices_per_payment_after={pay:pay._get_reconciled_invoices()forpayinpayments}

        changed_payments=self.env['account.move']
        forpayment,invoices_afterininvoices_per_payment_after.items():
            invoices_before=invoices_per_payment_before[payment]

            ifset(invoices_after.ids)!=set(invoices_before.ids):
                changed_payments|=payment
        changed_payments._update_payments_edi_documents()

        returnres

    defremove_move_reconcile(self):
        #OVERRIDE
        #Whenapaymenthasbeensenttothegovernment,itusuallycontainssomeinformationaboutreconciled
        #invoices.Iftheuserbreaksareconciliation,therelatedpaymentsmustbecancelledproperlyandthen,anew
        #electronicdocumentmustbegenerated.
        all_lines=self+self.matched_debit_ids.debit_move_id+self.matched_credit_ids.credit_move_id
        payments=all_lines.move_id.filtered(lambdamove:move.payment_idormove.statement_line_id)

        invoices_per_payment_before={pay:pay._get_reconciled_invoices()forpayinpayments}
        res=super().remove_move_reconcile()
        invoices_per_payment_after={pay:pay._get_reconciled_invoices()forpayinpayments}

        changed_payments=self.env['account.move']
        forpayment,invoices_afterininvoices_per_payment_after.items():
            invoices_before=invoices_per_payment_before[payment]

            ifset(invoices_after.ids)!=set(invoices_before.ids):
                changed_payments|=payment
        changed_payments._update_payments_edi_documents()

        returnres
