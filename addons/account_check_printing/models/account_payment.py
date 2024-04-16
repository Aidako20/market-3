#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError,ValidationError,RedirectWarning
fromflectra.tools.miscimportformatLang,format_date

INV_LINES_PER_STUB=9


classAccountPaymentRegister(models.TransientModel):
    _inherit="account.payment.register"

    @api.depends('payment_type','journal_id','partner_id')
    def_compute_payment_method_id(self):
        super()._compute_payment_method_id()
        forrecordinself:
            preferred=record.partner_id.with_company(record.company_id).property_payment_method_id
            ifrecord.payment_type=='outbound'andpreferredinrecord.journal_id.outbound_payment_method_ids:
                record.payment_method_id=preferred

classAccountPayment(models.Model):
    _inherit="account.payment"

    check_amount_in_words=fields.Char(
        string="AmountinWords",
        store=True,
        compute='_compute_check_amount_in_words',
    )
    check_manual_sequencing=fields.Boolean(related='journal_id.check_manual_sequencing')
    check_number=fields.Char(
        string="CheckNumber",
        store=True,
        readonly=True,
        copy=False,
        compute='_compute_check_number',
        inverse='_inverse_check_number',
        help="Theselectedjournalisconfiguredtoprintchecknumbers.Ifyourpre-printedcheckpaperalreadyhasnumbers"
             "orifthecurrentnumberingiswrong,youcanchangeitinthejournalconfigurationpage.",
    )

    @api.constrains('check_number','journal_id')
    def_constrains_check_number(self):
        payment_checks=self.filtered('check_number')
        ifnotpayment_checks:
            return
        forpayment_checkinpayment_checks:
            ifnotpayment_check.check_number.isdecimal():
                raiseValidationError(_('Checknumberscanonlyconsistofdigits'))
        self.flush()
        self.env.cr.execute("""
            SELECTpayment.check_number,move.journal_id
              FROMaccount_paymentpayment
              JOINaccount_movemoveONmove.id=payment.move_id
              JOINaccount_journaljournalONjournal.id=move.journal_id,
                   account_paymentother_payment
              JOINaccount_moveother_moveONother_move.id=other_payment.move_id
             WHEREpayment.check_number::BIGINT=other_payment.check_number::BIGINT
               ANDmove.journal_id=other_move.journal_id
               ANDpayment.id!=other_payment.id
               ANDpayment.idIN%(ids)s
               ANDmove.state='posted'
               ANDother_move.state='posted'
               ANDpayment.check_numberISNOTNULL
               ANDother_payment.check_numberISNOTNULL
        """,{
            'ids':tuple(payment_checks.ids),
        })
        res=self.env.cr.dictfetchall()
        ifres:
            raiseValidationError(_(
                'Thefollowingnumbersarealreadyused:\n%s',
                '\n'.join(_(
                    '%(number)sinjournal%(journal)s',
                    number=r['check_number'],
                    journal=self.env['account.journal'].browse(r['journal_id']).display_name,
                )forrinres)
            ))

    @api.depends('payment_method_id','currency_id','amount')
    def_compute_check_amount_in_words(self):
        forpayinself:
            ifpay.currency_id:
                pay.check_amount_in_words=pay.currency_id.amount_to_text(pay.amount)
            else:
                pay.check_amount_in_words=False

    @api.depends('journal_id','payment_method_code')
    def_compute_check_number(self):
        forpayinself:
            ifpay.journal_id.check_manual_sequencingandpay.payment_method_code=='check_printing':
                sequence=pay.journal_id.check_sequence_id
                pay.check_number=sequence.get_next_char(sequence.number_next_actual)
            else:
                pay.check_number=False

    def_inverse_check_number(self):
        forpaymentinself:
            ifpayment.check_number:
                sequence=payment.journal_id.check_sequence_id.sudo()
                sequence.padding=len(payment.check_number)

    @api.depends('payment_type','journal_id','partner_id')
    def_compute_payment_method_id(self):
        super()._compute_payment_method_id()
        forrecordinself:
            preferred=record.partner_id.with_company(record.company_id).property_payment_method_id
            ifrecord.payment_type=='outbound'andpreferredinrecord.journal_id.outbound_payment_method_ids:
                record.payment_method_id=preferred

    defaction_post(self):
        payment_method_check=self.env.ref('account_check_printing.account_payment_method_check')
        forpaymentinself.filtered(lambdap:p.payment_method_id==payment_method_checkandp.check_manual_sequencing):
            sequence=payment.journal_id.check_sequence_id
            payment.check_number=sequence.next_by_id()
        returnsuper(AccountPayment,self).action_post()

    defprint_checks(self):
        """Checkthattherecordsetisvalid,setthepaymentsstatetosentandcallprint_checks()"""
        #Sincethismethodcanbecalledviaaclient_action_multi,weneedtomakesurethereceivedrecordsarewhatweexpect
        self=self.filtered(lambdar:r.payment_method_id.code=='check_printing'andr.state!='reconciled')

        iflen(self)==0:
            raiseUserError(_("Paymentstoprintasachecksmusthave'Check'selectedaspaymentmethodand"
                              "nothavealreadybeenreconciled"))
        ifany(payment.journal_id!=self[0].journal_idforpaymentinself):
            raiseUserError(_("Inordertoprintmultiplechecksatonce,theymustbelongtothesamebankjournal."))

        ifnotself[0].journal_id.check_manual_sequencing:
            #Thewizardasksforthenumberprintedonthefirstpre-printedcheck
            #sopaymentsareattributedthenumberofthecheckthe'llbeprintedon.
            self.env.cr.execute("""
                  SELECTpayment.id
                    FROMaccount_paymentpayment
                    JOINaccount_movemoveONmovE.id=payment.move_id
                   WHEREjournal_id=%(journal_id)s
                   ANDpayment.check_numberISNOTNULL
                ORDERBYpayment.check_number::BIGINTDESC
                   LIMIT1
            """,{
                'journal_id':self.journal_id.id,
            })
            last_printed_check=self.browse(self.env.cr.fetchone())
            number_len=len(last_printed_check.check_numberor"")
            next_check_number='%0{}d'.format(number_len)%(int(last_printed_check.check_number)+1)

            return{
                'name':_('PrintPre-numberedChecks'),
                'type':'ir.actions.act_window',
                'res_model':'print.prenumbered.checks',
                'view_mode':'form',
                'target':'new',
                'context':{
                    'payment_ids':self.ids,
                    'default_next_check_number':next_check_number,
                }
            }
        else:
            self.filtered(lambdar:r.state=='draft').action_post()
            returnself.do_print_checks()

    defaction_unmark_sent(self):
        self.write({'is_move_sent':False})

    defaction_void_check(self):
        self.action_draft()
        self.action_cancel()

    defdo_print_checks(self):
        check_layout=self.company_id.account_check_printing_layout
        redirect_action=self.env.ref('account.action_account_config')
        ifnotcheck_layoutorcheck_layout=='disabled':
            msg=_("Youhavetochooseachecklayout.Forthis,goinInvoicing/AccountingSettings,searchfor'Checkslayout'andsetone.")
            raiseRedirectWarning(msg,redirect_action.id,_('Gototheconfigurationpanel'))
        report_action=self.env.ref(check_layout,False)
        ifnotreport_action:
            msg=_("SomethingwentwrongwithCheckLayout,pleaseselectanotherlayoutinInvoicing/AccountingSettingsandtryagain.")
            raiseRedirectWarning(msg,redirect_action.id,_('Gototheconfigurationpanel'))
        self.write({'is_move_sent':True})
        returnreport_action.report_action(self)

    #######################
    #CHECKPRINTINGMETHODS
    #######################
    def_check_fill_line(self,amount_str):
        returnamount_strand(amount_str+'').ljust(200,'*')or''

    def_check_build_page_info(self,i,p):
        multi_stub=self.company_id.account_check_printing_multi_stub
        return{
            'sequence_number':self.check_number,
            'manual_sequencing':self.journal_id.check_manual_sequencing,
            'date':format_date(self.env,self.date),
            'partner_id':self.partner_id,
            'partner_name':self.partner_id.name,
            'currency':self.currency_id,
            'state':self.state,
            'amount':formatLang(self.env,self.amount,currency_obj=self.currency_id)ifi==0else'VOID',
            'amount_in_word':self._check_fill_line(self.check_amount_in_words)ifi==0else'VOID',
            'memo':self.ref,
            'stub_cropped':notmulti_stubandlen(self.move_id._get_reconciled_invoices())>INV_LINES_PER_STUB,
            #Ifthepaymentdoesnotreferenceaninvoice,thereisnostublinetodisplay
            'stub_lines':p,
        }

    def_check_get_pages(self):
        """Returnsthedatastructureusedbythetemplate:alistofdictscontainingwhattoprintonpages.
        """
        stub_pages=self._check_make_stub_pages()or[False]
        pages=[]
        fori,pinenumerate(stub_pages):
            pages.append(self._check_build_page_info(i,p))
        returnpages

    def_check_make_stub_pages(self):
        """Thestubisthesummaryofpaidinvoices.Itmayspillonseveralpages,inwhichcaseonlythecheckon
            firstpageisvalid.Thisfunctionreturnsalistofstublinesperpage.
        """
        self.ensure_one()

        defprepare_vals(invoice,partials):
            number='-'.join([invoice.name,invoice.ref]ifinvoice.refelse[invoice.name])

            ifinvoice.is_outbound()orinvoice.move_type=='entry':
                invoice_sign=1
                partial_field='debit_amount_currency'
            else:
                invoice_sign=-1
                partial_field='credit_amount_currency'

            ifinvoice.currency_id.is_zero(invoice.amount_residual):
                amount_residual_str='-'
            else:
                amount_residual_str=formatLang(self.env,invoice_sign*invoice.amount_residual,currency_obj=invoice.currency_id)

            return{
                'due_date':format_date(self.env,invoice.invoice_date_due),
                'number':number,
                'amount_total':formatLang(self.env,invoice_sign*invoice.amount_total,currency_obj=invoice.currency_id),
                'amount_residual':amount_residual_str,
                'amount_paid':formatLang(self.env,invoice_sign*sum(partials.mapped(partial_field)),currency_obj=self.currency_id),
                'currency':invoice.currency_id,
            }

        #Decodethereconciliationtokeeponlybills.
        term_lines=self.line_ids.filtered(lambdaline:line.account_id.internal_typein('receivable','payable'))
        invoices=(term_lines.matched_debit_ids.debit_move_id.move_id+term_lines.matched_credit_ids.credit_move_id.move_id)\
            .filtered(lambdamove:move.is_outbound()ormove.move_type=='entry')

        invoices=invoices.sorted(lambdax:x.invoice_date_dueorx.date)

        #Grouppartialsbyinvoices.
        invoice_map={invoice:self.env['account.partial.reconcile']forinvoiceininvoices}
        forpartialinterm_lines.matched_debit_ids:
            invoice=partial.debit_move_id.move_id
            ifinvoiceininvoice_map:
                invoice_map[invoice]|=partial
        forpartialinterm_lines.matched_credit_ids:
            invoice=partial.credit_move_id.move_id
            ifinvoiceininvoice_map:
                invoice_map[invoice]|=partial

        #Preparestub_lines.
        if'out_refund'ininvoices.mapped('move_type'):
            stub_lines=[{'header':True,'name':"Bills"}]
            stub_lines+=[prepare_vals(invoice,partials)
                           forinvoice,partialsininvoice_map.items()
                           ifinvoice.move_type=='in_invoice']
            stub_lines+=[{'header':True,'name':"Refunds"}]
            stub_lines+=[prepare_vals(invoice,partials)
                           forinvoice,partialsininvoice_map.items()
                           ifinvoice.move_type=='out_refund']
        else:
            stub_lines=[prepare_vals(invoice,partials)
                          forinvoice,partialsininvoice_map.items()
                          ifinvoice.move_typein('in_invoice','entry')]

        #Cropthestublinesorsplitthemonmultiplepages
        ifnotself.company_id.account_check_printing_multi_stub:
            #Ifweneedtocropthestub,leaveplaceforanellipsisline
            num_stub_lines=len(stub_lines)>INV_LINES_PER_STUBandINV_LINES_PER_STUB-1orINV_LINES_PER_STUB
            stub_pages=[stub_lines[:num_stub_lines]]
        else:
            stub_pages=[]
            i=0
            whilei<len(stub_lines):
                #Makesurewedon'tstartthecreditsectionattheendofapage
                iflen(stub_lines)>=i+INV_LINES_PER_STUBandstub_lines[i+INV_LINES_PER_STUB-1].get('header'):
                    num_stub_lines=INV_LINES_PER_STUB-1orINV_LINES_PER_STUB
                else:
                    num_stub_lines=INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i+num_stub_lines])
                i+=num_stub_lines

        returnstub_pages

    def_check_make_stub_line(self,invoice):
        """Returnthedictusedtodisplayaninvoice/refundinthestub
        """
        #DEPRECATED:TOBEREMOVEDINMASTER
        #Findtheaccount.partial.reconcilewhicharecommontotheinvoiceandthepayment
        ifinvoice.move_typein['in_invoice','out_refund']:
            invoice_sign=1
            invoice_payment_reconcile=invoice.line_ids.mapped('matched_debit_ids').filtered(lambdar:r.debit_move_idinself.line_ids)
        else:
            invoice_sign=-1
            invoice_payment_reconcile=invoice.line_ids.mapped('matched_credit_ids').filtered(lambdar:r.credit_move_idinself.line_ids)

        ifself.currency_id!=self.journal_id.company_id.currency_id:
            amount_paid=abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid=abs(sum(invoice_payment_reconcile.mapped('amount')))

        amount_residual=invoice_sign*invoice.amount_residual

        return{
            'due_date':format_date(self.env,invoice.invoice_date_due),
            'number':invoice.refandinvoice.name+'-'+invoice.reforinvoice.name,
            'amount_total':formatLang(self.env,invoice_sign*invoice.amount_total,currency_obj=invoice.currency_id),
            'amount_residual':formatLang(self.env,amount_residual,currency_obj=invoice.currency_id)ifamount_residual*10**4!=0else'-',
            'amount_paid':formatLang(self.env,invoice_sign*amount_paid,currency_obj=self.currency_id),
            'currency':invoice.currency_id,
        }
