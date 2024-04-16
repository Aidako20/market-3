#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError

fromdatetimeimportdate


classAccountPartialReconcile(models.Model):
    _name="account.partial.reconcile"
    _description="PartialReconcile"
    _rec_name="id"

    #====Reconciliationfields====
    debit_move_id=fields.Many2one(
        comodel_name='account.move.line',
        index=True,required=True)
    credit_move_id=fields.Many2one(
        comodel_name='account.move.line',
        index=True,required=True)
    full_reconcile_id=fields.Many2one(
        comodel_name='account.full.reconcile',
        string="FullReconcile",copy=False)

    #====Currencyfields====
    company_currency_id=fields.Many2one(
        comodel_name='res.currency',
        string="CompanyCurrency",
        related='company_id.currency_id',
        help="Utilityfieldtoexpressamountcurrency")
    debit_currency_id=fields.Many2one(
        comodel_name='res.currency',
        store=True,
        compute='_compute_debit_currency_id',
        string="Currencyofthedebitjournalitem.")
    credit_currency_id=fields.Many2one(
        comodel_name='res.currency',
        store=True,
        compute='_compute_credit_currency_id',
        string="Currencyofthecreditjournalitem.")

    #====Amountfields====
    amount=fields.Monetary(
        currency_field='company_currency_id',
        help="Alwayspositiveamountconcernedbythismatchingexpressedinthecompanycurrency.")
    debit_amount_currency=fields.Monetary(
        currency_field='debit_currency_id',
        help="Alwayspositiveamountconcernedbythismatchingexpressedinthedebitlineforeigncurrency.")
    credit_amount_currency=fields.Monetary(
        currency_field='credit_currency_id',
        help="Alwayspositiveamountconcernedbythismatchingexpressedinthecreditlineforeigncurrency.")

    #====Otherfields====
    company_id=fields.Many2one(
        comodel_name='res.company',
        string="Company",store=True,readonly=False,
        related='debit_move_id.company_id')
    max_date=fields.Date(
        string="MaxDateofMatchedLines",store=True,
        compute='_compute_max_date',
        help="Technicalfieldusedtodetermineatwhichdatethisreconciliationneedstobeshownonthe"
             "agedreceivable/payablereports.")

    #-------------------------------------------------------------------------
    #CONSTRAINTMETHODS
    #-------------------------------------------------------------------------

    @api.constrains('debit_currency_id','credit_currency_id')
    def_check_required_computed_currencies(self):
        bad_partials=self.filtered(lambdapartial:notpartial.debit_currency_idornotpartial.credit_currency_id)
        ifbad_partials:
            raiseValidationError(_("Missingforeigncurrenciesonpartialshavingids:%s",bad_partials.ids))

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('debit_move_id.date','credit_move_id.date')
    def_compute_max_date(self):
        forpartialinself:
            partial.max_date=max(
                partial.debit_move_id.date,
                partial.credit_move_id.date
            )

    @api.depends('debit_move_id')
    def_compute_debit_currency_id(self):
        forpartialinself:
            partial.debit_currency_id=partial.debit_move_id.currency_id\
                                        orpartial.debit_move_id.company_currency_id

    @api.depends('credit_move_id')
    def_compute_credit_currency_id(self):
        forpartialinself:
            partial.credit_currency_id=partial.credit_move_id.currency_id\
                                        orpartial.credit_move_id.company_currency_id

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    defunlink(self):
        #OVERRIDEtounlinkfullreconcilelinkedtothecurrentpartials
        #andreversethetaxcashbasisjournalentries.

        #Avoidcyclicunlinkcallswhenremovingthepartialsthatcouldremovesomefullreconcile
        #andthen,loopagainandagain.
        ifnotself:
            returnTrue

        #Retrievethematchingnumbertounlink.
        full_to_unlink=self.full_reconcile_id

        #RetrievetheCABAentriestoreverse.
        moves_to_reverse=self.env['account.move'].search([('tax_cash_basis_rec_id','in',self.ids)])

        #Unlinkpartialsbeforedoinganythingelsetoavoid'Recordhasalreadybeendeleted'duetotherecursion.
        res=super().unlink()

        #ReverseCABAentries.
        default_values_list=[{
            'date':move._get_accounting_date(move.date,move._affect_tax_report()),
            'ref':_('Reversalof:%s')%move.name,
        }formoveinmoves_to_reverse]
        moves_to_reverse._reverse_moves(default_values_list,cancel=True)

        #Removethematchingnumbers.
        full_to_unlink.unlink()

        returnres

    #-------------------------------------------------------------------------
    #RECONCILIATIONMETHODS
    #-------------------------------------------------------------------------

    def_collect_tax_cash_basis_values(self):
        '''Collectallinformationneededtocreatethetaxcashbasisjournalentriesonthecurrentpartials.
        :return:   Adictionarymappingeachmove_idtotheresultof'account_move._collect_tax_cash_basis_values'.
                    Also,addthe'partials'keysbeingalistofdictionary,oneforeachpartialtoprocess:
                        *partial:         Theaccount.partial.reconcilerecord.
                        *percentage:      Thereconciledpercentagerepresentedbythepartial.
                        *payment_rate:    Theappliedrateofthispartial.
        '''
        tax_cash_basis_values_per_move={}

        ifnotself:
            return{}

        forpartialinself:
            formovein{partial.debit_move_id.move_id,partial.credit_move_id.move_id}:

                #Collectdataaboutcashbasis.
                ifmove.idnotintax_cash_basis_values_per_move:
                    tax_cash_basis_values_per_move[move.id]=move._collect_tax_cash_basis_values()

                #Nothingtoprocessonthemove.
                ifnottax_cash_basis_values_per_move.get(move.id):
                    continue
                move_values=tax_cash_basis_values_per_move[move.id]

                #Checkthecashbasisconfigurationonlywhenatleastonecashbasistaxentryneedtobecreated.
                journal=partial.company_id.tax_cash_basis_journal_id

                ifnotjournal:
                    raiseUserError(_("Thereisnotaxcashbasisjournaldefinedforthe'%s'company.\n"
                                      "ConfigureitinAccounting/Configuration/Settings")%partial.company_id.display_name)

                partial_amount=0.0
                partial_amount_currency=0.0
                rate_amount=0.0
                rate_amount_currency=0.0

                ifpartial.debit_move_id.move_id==move:
                    partial_amount+=partial.amount
                    partial_amount_currency+=partial.debit_amount_currency
                    rate_amount-=partial.credit_move_id.balance
                    rate_amount_currency-=partial.credit_move_id.amount_currency
                    source_line=partial.debit_move_id
                    counterpart_line=partial.credit_move_id

                ifpartial.credit_move_id.move_id==move:
                    partial_amount+=partial.amount
                    partial_amount_currency+=partial.credit_amount_currency
                    rate_amount+=partial.debit_move_id.balance
                    rate_amount_currency+=partial.debit_move_id.amount_currency
                    source_line=partial.credit_move_id
                    counterpart_line=partial.debit_move_id

                ifpartial.debit_move_id.move_id.is_invoice(include_receipts=True)andpartial.credit_move_id.move_id.is_invoice(include_receipts=True):
                    #Willmatchwhenreconcilingarefundwithaninvoice.
                    #Inthiscase,wewanttousetherateofeachbusinnessdocumenttocomputeitscashbasisentry,
                    #nottherateofwhatit'sreconciledwith.
                    rate_amount=source_line.balance
                    rate_amount_currency=source_line.amount_currency
                    payment_date=move.date
                else:
                    payment_date=counterpart_line.date

                ifmove_values['currency']==move.company_id.currency_id:
                    #Percentagemadeoncompany'scurrency.
                    percentage=partial_amount/move_values['total_balance']
                else:
                    #Percentagemadeonforeigncurrency.
                    percentage=partial_amount_currency/move_values['total_amount_currency']

                ifsource_line.currency_id!=counterpart_line.currency_id:
                    #Whentheinvoiceandthepaymentarenotsharingthesameforeigncurrency,therateiscomputed
                    #on-the-flyusingthepaymentdate.
                    payment_rate=self.env['res.currency']._get_conversion_rate(
                        counterpart_line.company_currency_id,
                        source_line.currency_id,
                        counterpart_line.company_id,
                        payment_date,
                    )
                elifrate_amount:
                    payment_rate=rate_amount_currency/rate_amount
                else:
                    payment_rate=0.0

                partial_vals={
                    'partial':partial,
                    'percentage':percentage,
                    'payment_rate':payment_rate,
                }

                #Addpartials.
                move_values.setdefault('partials',[])
                move_values['partials'].append(partial_vals)

        #Clean-upmoveshavingnothingtoprocess.
        return{k:vfork,vintax_cash_basis_values_per_move.items()ifv}

    @api.model
    def_prepare_cash_basis_base_line_vals(self,base_line,balance,amount_currency):
        '''Preparethevaluestobeusedtocreatethecashbasisjournalitemsforthetaxbaseline
        passedasparameter.

        :parambase_line:      Anaccount.move.linebeingthebaseofsometaxes.
        :parambalance:        Thebalancetoconsiderforthisline.
        :paramamount_currency:Thebalanceinforeigncurrencytoconsiderforthisline.
        :return:               Apythondictionarythatcouldbepassedtothecreatemethodof
                                account.move.line.
        '''
        account=base_line.company_id.account_cash_basis_base_account_idorbase_line.account_id
        return{
            'name':base_line.move_id.name,
            'debit':balanceifbalance>0.0else0.0,
            'credit':-balanceifbalance<0.0else0.0,
            'amount_currency':amount_currency,
            'currency_id':base_line.currency_id.id,
            'partner_id':base_line.partner_id.id,
            'account_id':account.id,
            'tax_ids':[(6,0,base_line.tax_ids.ids)],
            'tax_tag_ids':[(6,0,base_line._convert_tags_for_cash_basis(base_line.tax_tag_ids).ids)],
            'tax_exigible':True,
        }

    @api.model
    def_prepare_cash_basis_counterpart_base_line_vals(self,cb_base_line_vals):
        '''Preparethemovelineusedasacounterpartofthelinecreatedby
        _prepare_cash_basis_base_line_vals.

        :paramcb_base_line_vals:  Thelinereturnedby_prepare_cash_basis_base_line_vals.
        :return:                   Apythondictionarythatcouldbepassedtothecreatemethodof
                                    account.move.line.
        '''
        return{
            'name':cb_base_line_vals['name'],
            'debit':cb_base_line_vals['credit'],
            'credit':cb_base_line_vals['debit'],
            'account_id':cb_base_line_vals['account_id'],
            'amount_currency':-cb_base_line_vals['amount_currency'],
            'currency_id':cb_base_line_vals['currency_id'],
            'partner_id':cb_base_line_vals['partner_id'],
            'tax_exigible':True,
        }

    @api.model
    def_prepare_cash_basis_tax_line_vals(self,tax_line,balance,amount_currency):
        '''Preparethemovelinecorrespondingtoataxinthecashbasisentry.

        :paramtax_line:       Anaccount.move.linerecordbeingataxline.
        :parambalance:        Thebalancetoconsiderforthisline.
        :paramamount_currency:Thebalanceinforeigncurrencytoconsiderforthisline.
        :return:               Apythondictionarythatcouldbepassedtothecreatemethodof
                                account.move.line.
        '''
        return{
            'name':tax_line.name,
            'debit':balanceifbalance>0.0else0.0,
            'credit':-balanceifbalance<0.0else0.0,
            'tax_base_amount':tax_line.tax_base_amount,
            'tax_repartition_line_id':tax_line.tax_repartition_line_id.id,
            'tax_ids':[(6,0,tax_line.tax_ids.ids)],
            'tax_tag_ids':[(6,0,tax_line._convert_tags_for_cash_basis(tax_line.tax_tag_ids).ids)],
            'account_id':tax_line.tax_repartition_line_id.account_id.idortax_line.company_id.account_cash_basis_base_account_id.idortax_line.account_id.id,
            'amount_currency':amount_currency,
            'currency_id':tax_line.currency_id.id,
            'partner_id':tax_line.partner_id.id,
            'tax_exigible':True,
        }

    @api.model
    def_prepare_cash_basis_counterpart_tax_line_vals(self,tax_line,cb_tax_line_vals):
        '''Preparethemovelineusedasacounterpartofthelinecreatedby
        _prepare_cash_basis_tax_line_vals.

        :paramtax_line:           Anaccount.move.linerecordbeingataxline.
        :paramcb_tax_line_vals:   Theresultof_prepare_cash_basis_counterpart_tax_line_vals.
        :return:                   Apythondictionarythatcouldbepassedtothecreatemethodof
                                    account.move.line.
        '''
        return{
            'name':cb_tax_line_vals['name'],
            'debit':cb_tax_line_vals['credit'],
            'credit':cb_tax_line_vals['debit'],
            'account_id':tax_line.account_id.id,
            'amount_currency':-cb_tax_line_vals['amount_currency'],
            'currency_id':cb_tax_line_vals['currency_id'],
            'partner_id':cb_tax_line_vals['partner_id'],
            'tax_exigible':True,
        }

    @api.model
    def_get_cash_basis_base_line_grouping_key_from_vals(self,base_line_vals):
        '''Getthegroupingkeyofacashbasisbaselinethathasn'tyetbeencreated.
        :parambase_line_vals: Thevaluestocreateanewaccount.move.linerecord.
        :return:               Thegroupingkeyasatuple.
        '''
        return(
            base_line_vals['currency_id'],
            base_line_vals['partner_id'],
            base_line_vals['account_id'],
            tuple(base_line_vals['tax_ids'][0][2]),    #Decode[(6,0,[...])]command
            tuple(base_line_vals['tax_tag_ids'][0][2]),#Decode[(6,0,[...])]command
        )

    @api.model
    def_get_cash_basis_base_line_grouping_key_from_record(self,base_line,account=None):
        '''Getthegroupingkeyofajournalitembeingabaseline.
        :parambase_line:  Anaccount.move.linerecord.
        :paramaccount:    Optionalaccounttoshadowthecurrentbase_lineone.
        :return:           Thegroupingkeyasatuple.
        '''
        return(
            base_line.currency_id.id,
            base_line.partner_id.id,
            (accountorbase_line.account_id).id,
            tuple(base_line.tax_ids.ids),
            tuple(base_line._convert_tags_for_cash_basis(base_line.tax_tag_ids).ids),
        )

    @api.model
    def_get_cash_basis_tax_line_grouping_key_from_vals(self,tax_line_vals):
        '''Getthegroupingkeyofacashbasistaxlinethathasn'tyetbeencreated.
        :paramtax_line_vals:  Thevaluestocreateanewaccount.move.linerecord.
        :return:               Thegroupingkeyasatuple.
        '''
        return(
            tax_line_vals['currency_id'],
            tax_line_vals['partner_id'],
            tax_line_vals['account_id'],
            tuple(tax_line_vals['tax_ids'][0][2]),     #Decode[(6,0,[...])]command
            tuple(tax_line_vals['tax_tag_ids'][0][2]), #Decode[(6,0,[...])]command
            tax_line_vals['tax_repartition_line_id'],
        )

    @api.model
    def_get_cash_basis_tax_line_grouping_key_from_record(self,tax_line,account=None):
        '''Getthegroupingkeyofajournalitembeingataxline.
        :paramtax_line:   Anaccount.move.linerecord.
        :paramaccount:    Optionalaccounttoshadowthecurrenttax_lineone.
        :return:           Thegroupingkeyasatuple.
        '''
        return(
            tax_line.currency_id.id,
            tax_line.partner_id.id,
            (accountortax_line.account_id).id,
            tuple(tax_line.tax_ids.ids),
            tuple(tax_line._convert_tags_for_cash_basis(tax_line.tax_tag_ids).ids),
            tax_line.tax_repartition_line_id.id,
        )

    @api.model
    def_fix_cash_basis_full_balance_coverage(self,move_values,partial_values,pending_cash_basis_lines,partial_lines_to_create):
        '''Thismethodisusedtoensurethefullcoverageofthecurrentmovewhenitbecomesfullypaid.
        Forexample,supposealineof0.03paid50-50.Withoutthismethod,eachcashbasisentrywillreport
        0.03/0.5=0.015~0.02percashentryonthetaxreportasbaseamount,foratotalof0.04.
        Thisiswrongbecauseweexpect0.03.onthetaxreportasbaseamount.Thisiswrongbecauseweexpect0.03.

        :parammove_values:                Thecollectedvaluesaboutcashbasisforthecurrentmove.
        :parampartial_values:             Thecollectedvaluesaboutcashbasisforthecurrentpartial.
        :parampending_cash_basis_lines:   Thepreviouslygeneratedlinesduringthisreconciliationbutnotyetcreated.
        :parampartial_lines_to_create:    Thegeneratedlinesforthecurrentandlastpartialmakingthemovefullypaid.
        '''
        #DEPRECATED:TOBEREMOVEDINMASTER
        residual_amount_per_group={}
        move=move_values['move']

        #==========================================================================
        #Part1:
        #Addthebalanceofalljournalitemsthatarenottaxexigibleinorderto
        #ensuretheexactbalancewillbereportontheTaxReport.
        #Thispartisneededwhenthemovewillbefullypaidafterthecurrent
        #reconciliation.
        #==========================================================================

        forlineinmove_values['to_process_lines']:
            ifline.tax_repartition_line_id:
                #Taxline.
                grouping_key=self._get_cash_basis_tax_line_grouping_key_from_record(
                    line,
                    account=line.tax_repartition_line_id.account_id,
                )
                residual_amount_per_group.setdefault(grouping_key,0.0)
                residual_amount_per_group[grouping_key]+=line['amount_currency']

            elifline.tax_ids:
                #Baseline.
                grouping_key=self._get_cash_basis_base_line_grouping_key_from_record(
                    line,
                    account=line.company_id.account_cash_basis_base_account_id,
                )
                residual_amount_per_group.setdefault(grouping_key,0.0)
                residual_amount_per_group[grouping_key]+=line['amount_currency']

        #==========================================================================
        #Part2:
        #Subtractallpreviouslycreatedcashbasisjournalitemsduringprevious
        #reconciliation.
        #==========================================================================

        previous_tax_cash_basis_moves=self.env['account.move'].search([
            '|',
            ('tax_cash_basis_rec_id','in',self.ids),
            ('tax_cash_basis_move_id','=',move.id),
        ])
        forlineinprevious_tax_cash_basis_moves.line_ids:
            ifline.tax_repartition_line_id:
                #Taxline.
                grouping_key=self._get_cash_basis_tax_line_grouping_key_from_record(line)
            elifline.tax_ids:
                #Baseline.
                grouping_key=self._get_cash_basis_base_line_grouping_key_from_record(line)
            else:
                continue

            ifgrouping_keynotinresidual_amount_per_group:
                #Thegrouping_keyisunknownregardingthecurrentlines.
                #Maybethismovehasbeencreatedbeforemigrationandthen,
                #wearenotabletoensurethefullcoverageofthebalance.
                return

            residual_amount_per_group[grouping_key]-=line['amount_currency']

        #==========================================================================
        #Part3:
        #Subtractallpendingcashbasisjournalitemsthatwillbecreatedduring
        #thisreconciliation.
        #==========================================================================

        forgrouping_key,balanceinpending_cash_basis_lines:
            residual_amount_per_group[grouping_key]-=balance

        #==========================================================================
        #Part4:
        #Fixthecurrentcashbasisjournalitemsinprogressbyreplacingthe
        #balancebytheresidualone.
        #==========================================================================

        forgrouping_key,aggregated_valsinpartial_lines_to_create.items():
            line_vals=aggregated_vals['vals']

            amount_currency=residual_amount_per_group[grouping_key]
            balance=partial_values['payment_rate']andamount_currency/partial_values['payment_rate']or0.0
            line_vals.update({
                'debit':balanceifbalance>0.0else0.0,
                'credit':-balanceifbalance<0.0else0.0,
                'amount_currency':amount_currency,
            })

    def_create_tax_cash_basis_moves(self):
        '''Createthetaxcashbasisjournalentries.
        :return:Thenewlycreatedjournalentries.
        '''
        tax_cash_basis_values_per_move=self._collect_tax_cash_basis_values()
        today=fields.Date.context_today(self)

        moves_to_create=[]
        to_reconcile_after=[]
        formove_valuesintax_cash_basis_values_per_move.values():
            move=move_values['move']
            pending_cash_basis_lines=[]

            forpartial_valuesinmove_values['partials']:
                partial=partial_values['partial']

                #Initthejournalentry.
                lock_date=move.company_id._get_user_fiscal_lock_date()
                move_date=partial.max_dateifpartial.max_date>(lock_dateordate.min)elsetoday
                move_vals={
                    'move_type':'entry',
                    'date':move_date,
                    'ref':move.name,
                    'journal_id':partial.company_id.tax_cash_basis_journal_id.id,
                    'line_ids':[],
                    'tax_cash_basis_rec_id':partial.id,
                    'tax_cash_basis_move_id':move.id,
                }

                #Trackingoflinesgroupedalltogether.
                #Usedtoreducethenumberofgeneratedlinesandtoavoidroundingissues.
                partial_lines_to_create={}

                forlineinmove_values['to_process_lines']:

                    #==========================================================================
                    #Computethebalanceofthecurrentlineonthecashbasisentry.
                    #Thisbalanceisapercentagerepresentingthepartofthejournalentry
                    #thatisactuallypaidbythecurrentpartial.
                    #==========================================================================

                    #Percentageexpressedintheforeigncurrency.
                    amount_currency=line.currency_id.round(line.amount_currency*partial_values['percentage'])
                    balance=partial_values['payment_rate']andamount_currency/partial_values['payment_rate']or0.0

                    #==========================================================================
                    #Preparethemirrorcashbasisjournalitemofthecurrentline.
                    #Groupthemalltogetherasmuchaspossibletoreducethenumberof
                    #generatedjournalitems.
                    #Alsotrackthecomputedbalanceinordertoavoidroundingissueswhen
                    #thejournalentrywillbefullypaid.Atthatcase,weexpecttheexact
                    #amountofeachlinehasbeencoveredbythecashbasisjournalentries
                    #andwellreportedintheTaxReport.
                    #==========================================================================

                    ifline.tax_repartition_line_id:
                        #Taxline.

                        cb_line_vals=self._prepare_cash_basis_tax_line_vals(line,balance,amount_currency)
                        grouping_key=self._get_cash_basis_tax_line_grouping_key_from_vals(cb_line_vals)
                    elifline.tax_ids:
                        #Baseline.

                        cb_line_vals=self._prepare_cash_basis_base_line_vals(line,balance,amount_currency)
                        grouping_key=self._get_cash_basis_base_line_grouping_key_from_vals(cb_line_vals)

                    ifgrouping_keyinpartial_lines_to_create:
                        aggregated_vals=partial_lines_to_create[grouping_key]['vals']

                        debit=aggregated_vals['debit']+cb_line_vals['debit']
                        credit=aggregated_vals['credit']+cb_line_vals['credit']
                        balance=debit-credit

                        aggregated_vals.update({
                            'debit':balanceifbalance>0else0,
                            'credit':-balanceifbalance<0else0,
                            'amount_currency':aggregated_vals['amount_currency']+cb_line_vals['amount_currency'],
                        })

                        ifline.tax_repartition_line_id:
                            aggregated_vals.update({
                                'tax_base_amount':aggregated_vals['tax_base_amount']+cb_line_vals['tax_base_amount'],
                            })
                            partial_lines_to_create[grouping_key]['tax_line']+=line
                    else:
                        partial_lines_to_create[grouping_key]={
                            'vals':cb_line_vals,
                        }
                        ifline.tax_repartition_line_id:
                            partial_lines_to_create[grouping_key].update({
                                'tax_line':line,
                            })

                #==========================================================================
                #Createthecounterpartjournalitems.
                #==========================================================================

                #Tobeabletoretrievethecorrectmatchingbetweenthetaxlinestoreconcile
                #later,thelineswillbecreatedusingaspecificsequence.
                sequence=0

                forgrouping_key,aggregated_valsinpartial_lines_to_create.items():
                    line_vals=aggregated_vals['vals']
                    line_vals['sequence']=sequence

                    pending_cash_basis_lines.append((grouping_key,line_vals['amount_currency']))

                    if'tax_repartition_line_id'inline_vals:
                        #Taxline.

                        tax_line=aggregated_vals['tax_line']
                        counterpart_line_vals=self._prepare_cash_basis_counterpart_tax_line_vals(tax_line,line_vals)
                        counterpart_line_vals['sequence']=sequence+1

                        iftax_line.account_id.reconcile:
                            move_index=len(moves_to_create)
                            to_reconcile_after.append((tax_line,move_index,counterpart_line_vals['sequence']))

                    else:
                        #Baseline.

                        counterpart_line_vals=self._prepare_cash_basis_counterpart_base_line_vals(line_vals)
                        counterpart_line_vals['sequence']=sequence+1

                    sequence+=2

                    move_vals['line_ids']+=[(0,0,counterpart_line_vals),(0,0,line_vals)]

                moves_to_create.append(move_vals)

        moves=self.env['account.move'].create(moves_to_create)
        moves._post(soft=False)

        #Reconcilethetaxlinesbeingonareconciletaxbasistransferaccount.
        forlines,move_index,sequenceinto_reconcile_after:

            #Inexpenses,allmovelinesarecreatedmanuallywithoutanygroupingontaxlines.
            #Inthatcase,'lines'couldbealreadyreconciled.
            lines=lines.filtered(lambdax:notx.reconciled)
            ifnotlines:
                continue

            counterpart_line=moves[move_index].line_ids.filtered(lambdaline:line.sequence==sequence)

            #Whendealingwithtinyamounts,thelinecouldhaveazeroamountandthen,bealreadyreconciled.
            ifcounterpart_line.reconciled:
                continue

            (lines+counterpart_line).reconcile()

        returnmoves
