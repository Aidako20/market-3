#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_is_zero
fromflectra.toolsimportfloat_compare,float_round,float_repr
fromflectra.tools.miscimportformatLang,format_date
fromflectra.exceptionsimportUserError,ValidationError

importtime
importmath
importbase64
importre


classAccountCashboxLine(models.Model):
    """CashBoxDetails"""
    _name='account.cashbox.line'
    _description='CashBoxLine'
    _rec_name='coin_value'
    _order='coin_value'

    @api.depends('coin_value','number')
    def_sub_total(self):
        """CalculatesSubtotal"""
        forcashbox_lineinself:
            cashbox_line.subtotal=cashbox_line.coin_value*cashbox_line.number

    coin_value=fields.Float(string='Coin/BillValue',required=True,digits=0)
    number=fields.Integer(string='#Coins/Bills',help='OpeningUnitNumbers')
    subtotal=fields.Float(compute='_sub_total',string='Subtotal',digits=0,readonly=True)
    cashbox_id=fields.Many2one('account.bank.statement.cashbox',string="Cashbox")
    currency_id=fields.Many2one('res.currency',related='cashbox_id.currency_id')


classAccountBankStmtCashWizard(models.Model):
    """
    AccountBankStatementpopupthatallowsenteringcashdetails.
    """
    _name='account.bank.statement.cashbox'
    _description='BankStatementCashbox'
    _rec_name='id'

    cashbox_lines_ids=fields.One2many('account.cashbox.line','cashbox_id',string='CashboxLines')
    start_bank_stmt_ids=fields.One2many('account.bank.statement','cashbox_start_id')
    end_bank_stmt_ids=fields.One2many('account.bank.statement','cashbox_end_id')
    total=fields.Float(compute='_compute_total')
    currency_id=fields.Many2one('res.currency',compute='_compute_currency')

    @api.depends('start_bank_stmt_ids','end_bank_stmt_ids')
    def_compute_currency(self):
        forcashboxinself:
            cashbox.currency_id=False
            ifcashbox.end_bank_stmt_ids:
                cashbox.currency_id=cashbox.end_bank_stmt_ids[0].currency_id
            ifcashbox.start_bank_stmt_ids:
                cashbox.currency_id=cashbox.start_bank_stmt_ids[0].currency_id

    @api.depends('cashbox_lines_ids','cashbox_lines_ids.coin_value','cashbox_lines_ids.number')
    def_compute_total(self):
        forcashboxinself:
            cashbox.total=sum([line.subtotalforlineincashbox.cashbox_lines_ids])

    @api.model
    defdefault_get(self,fields):
        vals=super(AccountBankStmtCashWizard,self).default_get(fields)
        balance=self.env.context.get('balance')
        statement_id=self.env.context.get('statement_id')
        if'start_bank_stmt_ids'infieldsandnotvals.get('start_bank_stmt_ids')andstatement_idandbalance=='start':
            vals['start_bank_stmt_ids']=[(6,0,[statement_id])]
        if'end_bank_stmt_ids'infieldsandnotvals.get('end_bank_stmt_ids')andstatement_idandbalance=='close':
            vals['end_bank_stmt_ids']=[(6,0,[statement_id])]

        returnvals

    defname_get(self):
        result=[]
        forcashboxinself:
            result.append((cashbox.id,str(cashbox.total)))
        returnresult

    @api.model_create_multi
    defcreate(self,vals):
        cashboxes=super(AccountBankStmtCashWizard,self).create(vals)
        cashboxes._validate_cashbox()
        returncashboxes

    defwrite(self,vals):
        res=super(AccountBankStmtCashWizard,self).write(vals)
        self._validate_cashbox()
        returnres

    def_validate_cashbox(self):
        forcashboxinself:
            ifcashbox.start_bank_stmt_ids:
                cashbox.start_bank_stmt_ids.write({'balance_start':cashbox.total})
            ifcashbox.end_bank_stmt_ids:
                cashbox.end_bank_stmt_ids.write({'balance_end_real':cashbox.total})


classAccountBankStmtCloseCheck(models.TransientModel):
    """
    AccountBankStatementwizardthatcheckthatclosingbalanceiscorrect.
    """
    _name='account.bank.statement.closebalance'
    _description='BankStatementClosingBalance'

    defvalidate(self):
        bnk_stmt_id=self.env.context.get('active_id',False)
        ifbnk_stmt_id:
            self.env['account.bank.statement'].browse(bnk_stmt_id).button_validate()
        return{'type':'ir.actions.act_window_close'}


classAccountBankStatement(models.Model):
    _name="account.bank.statement"
    _description="BankStatement"
    _order="datedesc,namedesc,iddesc"
    _inherit=['mail.thread','sequence.mixin']
    _check_company_auto=True
    _sequence_index="journal_id"

    #Note:thereasonwhywedid2separatefunctionwiththesamedependencies(oneforbalance_startandoneforbalance_end_real)
    #isbecauseifwecreateabankstatementwithadefaultvalueforoneofthefieldbutnottheother,thecomputemethod
    #won'tbecalledandthereforetheotherfieldwillhaveavalueof0andwedon'twantthat.
    @api.depends('previous_statement_id','previous_statement_id.balance_end_real')
    def_compute_starting_balance(self):
        #Whenabankstatementisinsertedout-of-orderseveralfieldsneedstoberecomputed.
        #Astherecordstorecomputeareorderedbyid,itmayoccurthatthefirstrecord
        #torecomputestartarecursiverecomputationoffieldbalance_end_real
        #Toavoidthiswesorttherecordsbydate
        forstatementinself.sorted(key=lambdas:s.date):
            ifstatement.previous_statement_id.balance_end_real!=statement.balance_start:
                statement.balance_start=statement.previous_statement_id.balance_end_real
            else:
                #Needdefaultvalue
                statement.balance_start=statement.balance_startor0.0

    @api.depends('previous_statement_id','previous_statement_id.balance_end_real')
    def_compute_ending_balance(self):
        latest_statement=self.env['account.bank.statement'].search([('journal_id','=',self[0].journal_id.id)],limit=1)
        forstatementinself:
            #recomputebalance_end_realincaseweareinabankjournalandifwechangethe
            #balance_end_realofpreviousstatementaswedon'twant
            #holesincaseweaddastatementinbetween2othersstatements.
            #Weonlydothisforthebankjournalasweusethebalance_end_realincash
            #journalforverificationandcreatingcashdifferenceentriessowedon'twant
            #torecomputethevalueinthatcase
            ifstatement.journal_type=='bank':
                #Ifweareonlaststatementandthatstatementalreadyhasabalance_end_real,don'tchangethebalance_end_real
                #Otherwise,recomputebalance_end_realtopreventholesbetweenstatement.
                iflatest_statement.idandstatement.id==latest_statement.idandnotfloat_is_zero(statement.balance_end_real,precision_digits=statement.currency_id.decimal_places):
                    statement.balance_end_real=statement.balance_end_realor0.0
                else:
                    total_entry_encoding=sum([line.amountforlineinstatement.line_ids])
                    statement.balance_end_real=statement.previous_statement_id.balance_end_real+total_entry_encoding
            else:
                #Needdefaultvalue
                statement.balance_end_real=statement.balance_end_realor0.0

    @api.depends('line_ids','balance_start','line_ids.amount','balance_end_real')
    def_end_balance(self):
        forstatementinself:
            statement.total_entry_encoding=sum([line.amountforlineinstatement.line_ids])
            statement.balance_end=statement.balance_start+statement.total_entry_encoding
            statement.difference=statement.balance_end_real-statement.balance_end

    def_is_difference_zero(self):
        forbank_stmtinself:
            bank_stmt.is_difference_zero=float_is_zero(bank_stmt.difference,precision_digits=bank_stmt.currency_id.decimal_places)

    @api.depends('journal_id')
    def_compute_currency(self):
        forstatementinself:
            statement.currency_id=statement.journal_id.currency_idorstatement.company_id.currency_id

    @api.depends('move_line_ids')
    def_get_move_line_count(self):
        forstatementinself:
            statement.move_line_count=len(statement.move_line_ids)

    @api.model
    def_default_journal(self):
        journal_type=self.env.context.get('journal_type',False)
        company_id=self.env.company.id
        ifjournal_type:
            journals=self.env['account.journal'].search([('type','=',journal_type),('company_id','=',company_id)])
            ifjournals:
                returnjournals[0]
        returnself.env['account.journal']

    @api.depends('balance_start','previous_statement_id')
    def_compute_is_valid_balance_start(self):
        forbnkinself:
            bnk.is_valid_balance_start=(
                bnk.currency_id.is_zero(
                    bnk.balance_start-bnk.previous_statement_id.balance_end_real
                )
                ifbnk.previous_statement_id
                elseTrue
            )

    @api.depends('date','journal_id')
    def_get_previous_statement(self):
        forstinself:
            #Searchforthepreviousstatement
            domain=[('date','<=',st.date),('journal_id','=',st.journal_id.id)]
            #Thereasonwhywehavetoperformthistestisbecausewehavetwousecasehere:
            #Firstoneisincasewearecreatinganewrecord,inthatcasethatnewrecorddoes
            #nothaveanyidyet.Howeverifweareupdatinganexistingrecord,thedomaindate<=st.date
            #willfindtherecorditself,sowehavetoaddaconditioninthesearchtoignoreself.id
            ifnotisinstance(st.id,models.NewId):
                domain.extend(['|','&',('id','<',st.id),('date','=',st.date),'&',('id','!=',st.id),('date','!=',st.date)])
            previous_statement=self.search(domain,limit=1,order='datedesc,iddesc')
            st.previous_statement_id=previous_statement.id

    name=fields.Char(string='Reference',states={'open':[('readonly',False)]},copy=False,readonly=True)
    reference=fields.Char(string='ExternalReference',states={'open':[('readonly',False)]},copy=False,readonly=True,help="Usedtoholdthereferenceoftheexternalmeanthatcreatedthisstatement(nameofimportedfile,referenceofonlinesynchronization...)")
    date=fields.Date(required=True,states={'confirm':[('readonly',True)]},index=True,copy=False,default=fields.Date.context_today)
    date_done=fields.Datetime(string="ClosedOn")
    balance_start=fields.Monetary(string='StartingBalance',states={'confirm':[('readonly',True)]},compute='_compute_starting_balance',readonly=False,store=True,tracking=True)
    balance_end_real=fields.Monetary('EndingBalance',states={'confirm':[('readonly',True)]},compute='_compute_ending_balance',readonly=False,store=True,tracking=True)
    state=fields.Selection(string='Status',required=True,readonly=True,copy=False,tracking=True,selection=[
            ('open','New'),
            ('posted','Processing'),
            ('confirm','Validated'),
        ],default='open',
        help="Thecurrentstateofyourbankstatement:"
             "-New:FullyeditablewithdraftJournalEntries."
             "-Processing:NolongereditablewithpostedJournalentries,readyforthereconciliation."
             "-Validated:Alllinesarereconciled.Thereisnothinglefttoprocess.")
    currency_id=fields.Many2one('res.currency',compute='_compute_currency',string="Currency")
    journal_id=fields.Many2one('account.journal',string='Journal',required=True,states={'confirm':[('readonly',True)]},default=_default_journal,check_company=True)
    journal_type=fields.Selection(related='journal_id.type',help="Technicalfieldusedforusabilitypurposes")
    company_id=fields.Many2one('res.company',related='journal_id.company_id',string='Company',store=True,readonly=True,
        default=lambdaself:self.env.company)

    total_entry_encoding=fields.Monetary('TransactionsSubtotal',compute='_end_balance',store=True,help="Totaloftransactionlines.")
    balance_end=fields.Monetary('ComputedBalance',compute='_end_balance',store=True,help='BalanceascalculatedbasedonOpeningBalanceandtransactionlines')
    difference=fields.Monetary(compute='_end_balance',store=True,help="Differencebetweenthecomputedendingbalanceandthespecifiedendingbalance.")

    line_ids=fields.One2many('account.bank.statement.line','statement_id',string='Statementlines',states={'confirm':[('readonly',True)]},copy=True)
    move_line_ids=fields.One2many('account.move.line','statement_id',string='Entrylines',states={'confirm':[('readonly',True)]})
    move_line_count=fields.Integer(compute="_get_move_line_count")

    all_lines_reconciled=fields.Boolean(compute='_compute_all_lines_reconciled',
        help="Technicalfieldindicatingifallstatementlinesarefullyreconciled.")
    user_id=fields.Many2one('res.users',string='Responsible',required=False,default=lambdaself:self.env.user)
    cashbox_start_id=fields.Many2one('account.bank.statement.cashbox',string="StartingCashbox")
    cashbox_end_id=fields.Many2one('account.bank.statement.cashbox',string="EndingCashbox")
    is_difference_zero=fields.Boolean(compute='_is_difference_zero',string='Iszero',help="Checkifdifferenceiszero.")
    previous_statement_id=fields.Many2one('account.bank.statement',help='technicalfieldtocomputestartingbalancecorrectly',compute='_get_previous_statement',store=True)
    is_valid_balance_start=fields.Boolean(string="IsValidBalanceStart",store=True,
        compute="_compute_is_valid_balance_start",
        help="Technicalfieldtodisplayawarningmessageincasestartingbalanceisdifferentthanpreviousendingbalance")
    country_code=fields.Char(related='company_id.country_id.code')

    defwrite(self,values):
        res=super(AccountBankStatement,self).write(values)
        ifvalues.get('date')orvalues.get('journal'):
            #Ifwearechangingthedateorjournalofabankstatement,wehavetochangeitsprevious_statement_id.Thisisdone
            #automaticallyusingthecomputefunction,butwealsohavetochangetheprevious_statement_idofrecordsthatwere
            #previouslypointingtowardusandrecordsthatwerepointingtowardsournewprevious_statement_id.Thisisdonehere
            #bymarkingthoserecordasneedingtoberecomputed.
            #Notethatmarkingthefieldisnotenoughaswealsohavetorecomputeallitsotherfieldsthataredependingon'previous_statement_id'
            #hencetheneedtocallmodifiedafterwards.
            to_recompute=self.search([('previous_statement_id','in',self.ids),('id','notin',self.ids),('journal_id','in',self.mapped('journal_id').ids)])
            ifto_recompute:
                self.env.add_to_compute(self._fields['previous_statement_id'],to_recompute)
                to_recompute.modified(['previous_statement_id'])
            next_statements_to_recompute=self.search([('previous_statement_id','in',[st.previous_statement_id.idforstinself]),('id','notin',self.ids),('journal_id','in',self.mapped('journal_id').ids)])
            ifnext_statements_to_recompute:
                self.env.add_to_compute(self._fields['previous_statement_id'],next_statements_to_recompute)
                next_statements_to_recompute.modified(['previous_statement_id'])
        returnres

    @api.model_create_multi
    defcreate(self,values):
        res=super(AccountBankStatement,self).create(values)
        #Uponbankstmtcreation,itispossiblethatthestatementisinsertedbetweentwootherstatementsandnotattheend
        #Inthatcase,wehavetosearchforstatementthatarepointingtothesameprevious_statement_idasourselveinorderto
        #changetheirprevious_statement_idtous.Thisisdonebymarkingthefield'previous_statement_id'toberecomputedforsuchrecords.
        #Notethatmarkingthefieldisnotenoughaswealsohavetorecomputeallitsotherfieldsthataredependingon'previous_statement_id'
        #hencetheneedtocallmodifiedafterwards.
        #Thereasonwearedoingthishereandnotinacomputefieldisthatitisnoteasytowritedependenciesforsuchfield.
        next_statements_to_recompute=self.search([('previous_statement_id','in',[st.previous_statement_id.idforstinres]),('id','notin',res.ids),('journal_id','in',res.journal_id.ids)])
        ifnext_statements_to_recompute:
            self.env.add_to_compute(self._fields['previous_statement_id'],next_statements_to_recompute)
            next_statements_to_recompute.modified(['previous_statement_id'])
        returnres

    @api.depends('line_ids.is_reconciled')
    def_compute_all_lines_reconciled(self):
        forstatementinself:
            statement.all_lines_reconciled=all(st_line.is_reconciledforst_lineinstatement.line_ids)

    @api.onchange('journal_id')
    defonchange_journal_id(self):
        forst_lineinself.line_ids:
            st_line.journal_id=self.journal_id
            st_line.currency_id=self.journal_id.currency_idorself.company_id.currency_id

    def_check_balance_end_real_same_as_computed(self):
        """Checkthebalance_end_real(encodedmanuallybytheuser)isequalstothebalance_end(computedbyflectra)."""
        returnself._check_cash_balance_end_real_same_as_computed()andself._check_bank_balance_end_real_same_as_computed()

    def_check_cash_balance_end_real_same_as_computed(self):
        """Checkthebalance_end_real(encodedmanuallybytheuser)isequalstothebalance_end(computedbyflectra).
            Foracashstatement,ifthereisadifference,thedifferentissetautomaticallytoaprofit/lossaccount.
        """
        forstatementinself.filtered(lambdastmt:stmt.journal_type=='cash'):
            ifnotstatement.currency_id.is_zero(statement.difference):
                st_line_vals={
                    'statement_id':statement.id,
                    'journal_id':statement.journal_id.id,
                    'amount':statement.difference,
                    'date':statement.date,
                }

                ifstatement.currency_id.compare_amounts(statement.difference,0.0)<0.0:
                    ifnotstatement.journal_id.loss_account_id:
                        raiseUserError(_(
                            "Pleasegoonthe%sjournalanddefineaLossAccount."
                            "Thisaccountwillbeusedtorecordcashdifference.",
                            statement.journal_id.name
                        ))

                    st_line_vals['payment_ref']=_("Cashdifferenceobservedduringthecounting(Loss)")
                    st_line_vals['counterpart_account_id']=statement.journal_id.loss_account_id.id
                else:
                    #statement.difference>0.0
                    ifnotstatement.journal_id.profit_account_id:
                        raiseUserError(_(
                            "Pleasegoonthe%sjournalanddefineaProfitAccount."
                            "Thisaccountwillbeusedtorecordcashdifference.",
                            statement.journal_id.name
                        ))

                    st_line_vals['payment_ref']=_("Cashdifferenceobservedduringthecounting(Profit)")
                    st_line_vals['counterpart_account_id']=statement.journal_id.profit_account_id.id

                self.env['account.bank.statement.line'].create(st_line_vals)
        returnTrue

    def_check_bank_balance_end_real_same_as_computed(self):
        """Checkthebalance_end_real(encodedmanuallybytheuser)isequalstothebalance_end(computedbyflectra)."""
        forstatementinself.filtered(lambdastmt:stmt.journal_type=='bank'):
            ifnotstatement.currency_id.is_zero(statement.difference):
                balance_end_real=formatLang(self.env,statement.balance_end_real,currency_obj=statement.currency_id)
                balance_end=formatLang(self.env,statement.balance_end,currency_obj=statement.currency_id)
                raiseUserError(_(
                    'Theendingbalanceisincorrect!\nTheexpectedbalance(%(real_balance)s)isdifferentfromthecomputedone(%(computed_balance)s).',
                    real_balance=balance_end_real,
                    computed_balance=balance_end
                ))
        returnTrue

    defunlink(self):
        forstatementinself:
            ifstatement.state!='open':
                raiseUserError(_('Inordertodeleteabankstatement,youmustfirstcancelittodeleterelatedjournalitems.'))
            #Explicitlyunlinkbankstatementlinessoitwillcheckthattherelatedjournalentrieshavebeendeletedfirst
            statement.line_ids.unlink()
            #Someotherbankstatementsmightbelinktothisone,sointhatcasewehavetoswitchtheprevious_statement_id
            #fromthatstatementtotheonelinkedtothisstatement
            next_statement=self.search([('previous_statement_id','=',statement.id),('journal_id','=',statement.journal_id.id)])
            ifnext_statement:
                next_statement.previous_statement_id=statement.previous_statement_id
        returnsuper(AccountBankStatement,self).unlink()

    #-------------------------------------------------------------------------
    #CONSTRAINTMETHODS
    #-------------------------------------------------------------------------

    @api.constrains('journal_id')
    def_check_journal(self):
        forstatementinself:
            ifany(st_line.journal_id!=statement.journal_idforst_lineinstatement.line_ids):
                raiseValidationError(_('Thejournalofabankstatementlinemustalwaysbethesameasthebankstatementone.'))

    def_constrains_date_sequence(self):
        #Multipleimportmethodssetthenametothingsthatarenotsequences:
        #i.e.Statementfrom{date1}to{date2}
        #Itmakesthisconstraintnotapplicable,anditislessneededonbankstatementsasit
        #isonlyanindicationandnotsomethinglegal.
        return

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------

    defopen_cashbox_id(self):
        self.ensure_one()
        context=dict(self.env.contextor{})
        ifcontext.get('balance'):
            context['statement_id']=self.id
            ifcontext['balance']=='start':
                cashbox_id=self.cashbox_start_id.id
            elifcontext['balance']=='close':
                cashbox_id=self.cashbox_end_id.id
            else:
                cashbox_id=False

            action={
                'name':_('CashControl'),
                'view_mode':'form',
                'res_model':'account.bank.statement.cashbox',
                'view_id':self.env.ref('account.view_account_bnk_stmt_cashbox_footer').id,
                'type':'ir.actions.act_window',
                'res_id':cashbox_id,
                'context':context,
                'target':'new'
            }

            returnaction

    defbutton_post(self):
        '''Movethebankstatementsfrom'draft'to'posted'.'''
        ifany(statement.state!='open'forstatementinself):
            raiseUserError(_("Onlynewstatementscanbeposted."))

        self._check_cash_balance_end_real_same_as_computed()

        forstatementinself:
            ifnotstatement.name:
                statement._set_next_sequence()

        self.write({'state':'posted'})
        lines_of_moves_to_post=self.line_ids.filtered(lambdaline:line.move_id.state!='posted')
        iflines_of_moves_to_post:
            lines_of_moves_to_post.move_id._post(soft=False)

    defbutton_validate(self):
        ifany(statement.state!='posted'ornotstatement.all_lines_reconciledforstatementinself):
            raiseUserError(_('Alltheaccountentrieslinesmustbeprocessedinordertovalidatethestatement.'))

        forstatementinself:

            #Chatter.
            statement.message_post(body=_('Statement%sconfirmed.',statement.name))

            #Bankstatementreport.
            ifstatement.journal_id.type=='bank':
                content,content_type=self.env.ref('account.action_report_account_statement')._render(statement.id)
                self.env['ir.attachment'].create({
                    'name':statement.nameand_("BankStatement%s.pdf",statement.name)or_("BankStatement.pdf"),
                    'type':'binary',
                    'datas':base64.encodebytes(content),
                    'res_model':statement._name,
                    'res_id':statement.id
                })

        self._check_balance_end_real_same_as_computed()
        self.write({'state':'confirm','date_done':fields.Datetime.now()})

    defbutton_validate_or_action(self):
        ifself.journal_type=='cash'andnotself.currency_id.is_zero(self.difference):
            returnself.env['ir.actions.act_window']._for_xml_id('account.action_view_account_bnk_stmt_check')

        returnself.button_validate()

    defbutton_reopen(self):
        '''Movethebankstatementsbacktothe'open'state.'''
        ifany(statement.state=='draft'forstatementinself):
            raiseUserError(_("Onlyvalidatedstatementscanberesettonew."))

        self.write({'state':'open'})
        self.line_ids.move_id.button_draft()
        self.line_ids.button_undo_reconciliation()

    defbutton_reprocess(self):
        """Movethebankstatementsbacktothe'posted'state."""
        ifany(statement.state!='confirm'forstatementinself):
            raiseUserError(_("OnlyValidatedstatementscanberesettonew."))

        self.write({'state':'posted','date_done':False})

    defbutton_journal_entries(self):
        return{
            'name':_('JournalEntries'),
            'view_mode':'tree,form',
            'res_model':'account.move',
            'view_id':False,
            'type':'ir.actions.act_window',
            'domain':[('id','in',self.line_ids.move_id.ids)],
            'context':{
                'journal_id':self.journal_id.id,
            }
        }

    def_get_last_sequence_domain(self,relaxed=False):
        self.ensure_one()
        where_string="WHEREjournal_id=%(journal_id)sANDname!='/'"
        param={'journal_id':self.journal_id.id}

        ifnotrelaxed:
            domain=[('journal_id','=',self.journal_id.id),('id','!=',self.idorself._origin.id),('name','!=',False)]
            previous_name=self.search(domain+[('date','<',self.date)],order='datedesc',limit=1).name
            ifnotprevious_name:
                previous_name=self.search(domain,order='datedesc',limit=1).name
            sequence_number_reset=self._deduce_sequence_number_reset(previous_name)
            ifsequence_number_reset=='year':
                where_string+="ANDdate_trunc('year',date)=date_trunc('year',%(date)s)"
                param['date']=self.date
            elifsequence_number_reset=='month':
                where_string+="ANDdate_trunc('month',date)=date_trunc('month',%(date)s)"
                param['date']=self.date
        returnwhere_string,param

    def_get_starting_sequence(self):
        self.ensure_one()
        return"%s%s%04d/%02d/00000"%(self.journal_id.code,_('Statement'),self.date.year,self.date.month)


classAccountBankStatementLine(models.Model):
    _name="account.bank.statement.line"
    _inherits={'account.move':'move_id'}
    _description="BankStatementLine"
    _order="statement_iddesc,date,sequence,iddesc"
    _check_company_auto=True

    #FIXME:Fieldshavingthesamenameinbothtablesareconfusing(partner_id&state).Wedon'tchangeitbecause:
    #-It'samesstotrack/fix.
    #-Somefieldsherecouldbesimplifiedwhentheonchangeswillbegoneinaccount.move.
    #Shouldbeimprovedinthefuture.

    #==Businessfields==
    move_id=fields.Many2one(
        comodel_name='account.move',
        auto_join=True,
        string='JournalEntry',required=True,readonly=True,ondelete='cascade',
        check_company=True)
    statement_id=fields.Many2one(
        comodel_name='account.bank.statement',
        string='Statement',index=True,required=True,ondelete='cascade',
        check_company=True)

    sequence=fields.Integer(index=True,help="Givesthesequenceorderwhendisplayingalistofbankstatementlines.",default=1)
    account_number=fields.Char(string='BankAccountNumber',help="Technicalfieldusedtostorethebankaccountnumberbeforeitscreation,upontheline'sprocessing")
    partner_name=fields.Char(
        help="Thisfieldisusedtorecordthethirdpartynamewhenimportingbankstatementinelectronicformat,"
             "whenthepartnerdoesn'texistyetinthedatabase(orcannotbefound).")
    transaction_type=fields.Char(string='TransactionType')
    payment_ref=fields.Char(string='Label',required=True)
    amount=fields.Monetary(currency_field='currency_id')
    amount_currency=fields.Monetary(currency_field='foreign_currency_id',
        help="Theamountexpressedinanoptionalothercurrencyifitisamulti-currencyentry.")
    foreign_currency_id=fields.Many2one('res.currency',string='ForeignCurrency',
        help="Theoptionalothercurrencyifitisamulti-currencyentry.")
    amount_residual=fields.Float(string="ResidualAmount",
        compute="_compute_is_reconciled",
        store=True,
        help="Theamountlefttobereconciledonthisstatementline(signedaccordingtoitsmovelines'balance),expressedinitscurrency.Thisisatechnicalfieldusetospeeduptheapplicationofreconciliationmodels.")
    currency_id=fields.Many2one('res.currency',string='JournalCurrency')
    partner_id=fields.Many2one(
        comodel_name='res.partner',
        string='Partner',ondelete='restrict',
        domain="['|',('parent_id','=',False),('is_company','=',True)]",
        check_company=True)
    payment_ids=fields.Many2many(
        comodel_name='account.payment',
        relation='account_payment_account_bank_statement_line_rel',
        string='Auto-generatedPayments',
        help="Paymentsgeneratedduringthereconciliationofthisbankstatementlines.")

    #==Displaypurposefields==
    is_reconciled=fields.Boolean(string='IsReconciled',store=True,
        compute='_compute_is_reconciled',
        help="Technicalfieldindicatingifthestatementlineisalreadyreconciled.")
    state=fields.Selection(related='statement_id.state',string='Status',readonly=True)
    country_code=fields.Char(related='company_id.country_id.code')

    #-------------------------------------------------------------------------
    #HELPERS
    #-------------------------------------------------------------------------

    def_seek_for_lines(self):
        '''Helperusedtodispatchthejournalitemsbetween:
        -Thelinesusingtheliquidityaccount.
        -Thelinesusingthetransferaccount.
        -Thelinesbeingnotinoneofthetwopreviouscategories.
        :return:(liquidity_lines,suspense_lines,other_lines)
        '''
        liquidity_lines=self.env['account.move.line']
        suspense_lines=self.env['account.move.line']
        other_lines=self.env['account.move.line']

        forlineinself.move_id.line_ids:
            ifline.account_id==self.journal_id.default_account_id:
                liquidity_lines+=line
            elifline.account_id==self.journal_id.suspense_account_id:
                suspense_lines+=line
            else:
                other_lines+=line
        returnliquidity_lines,suspense_lines,other_lines

    @api.model
    def_prepare_liquidity_move_line_vals(self):
        '''Preparevaluestocreateanewaccount.move.linerecordcorrespondingtothe
        liquidityline(havingthebank/cashaccount).
        :return:       Thevaluestocreateanewaccount.move.linerecord.
        '''
        self.ensure_one()

        statement=self.statement_id
        journal=statement.journal_id
        company_currency=journal.company_id.currency_id
        journal_currency=journal.currency_idorcompany_currency

        ifself.foreign_currency_idandjournal_currency:
            currency_id=journal_currency.id
            ifself.foreign_currency_id==company_currency:
                amount_currency=self.amount
                balance=self.amount_currency
            else:
                amount_currency=self.amount
                balance=journal_currency._convert(amount_currency,company_currency,journal.company_id,self.date)
        elifself.foreign_currency_idandnotjournal_currency:
            amount_currency=self.amount_currency
            balance=self.amount
            currency_id=self.foreign_currency_id.id
        elifnotself.foreign_currency_idandjournal_currency:
            currency_id=journal_currency.id
            amount_currency=self.amount
            balance=journal_currency._convert(amount_currency,journal.company_id.currency_id,journal.company_id,self.date)
        else:
            currency_id=company_currency.id
            amount_currency=self.amount
            balance=self.amount

        return{
            'name':self.payment_ref,
            'move_id':self.move_id.id,
            'partner_id':self.partner_id.id,
            'currency_id':currency_id,
            'account_id':journal.default_account_id.id,
            'debit':balance>0andbalanceor0.0,
            'credit':balance<0and-balanceor0.0,
            'amount_currency':amount_currency,
        }

    @api.model
    def_prepare_counterpart_move_line_vals(self,counterpart_vals,move_line=None):
        '''Preparevaluestocreateanewaccount.move.linemove_line.
        Bydefault,withoutspecified'counterpart_vals'or'move_line',thecounterpartlineis
        createdusingthesuspenseaccount.Otherwise,thismethodisalsocalledduringthe
        reconciliationtopreparethestatementline'sjournalentry.Inthatcase,
        'counterpart_vals'willbeusedtocreateacustomaccount.move.line(fromthereconciliationwidget)
        and'move_line'willbeusedtocreatethecounterpartofanexistingaccount.move.linetowhich
        thenewlycreatedjournalitemwillbereconciled.
        :paramcounterpart_vals:   Apythondictionarycontaining:
            'balance':                 Optionalamounttoconsiderduringthereconciliation.Ifaforeigncurrencyissetonthe
                                        counterpartlineinthesameforeigncurrencyasthestatementline,thenthisamountis
                                        consideredastheamountinforeigncurrency.Ifnotspecified,thefullbalanceistook.
                                        Thisvaluemustbeprovidedifmove_lineisnot.
            'amount_residual':         Theresidualamounttoreconcileexpressedinthecompany'scurrency.
                                        /!\Thisvalueshouldbeequivalenttomove_line.amount_residualexceptwewant
                                        toavoidbrowsingtherecordwhentheonlythingweneedinanoverviewofthe
                                        reconciliation,forexampleinthereconciliationwidget.
            'amount_residual_currency':Theresidualamounttoreconcileexpressedintheforeign'scurrency.
                                        Usingthiskeydoesn'tmakesensewithoutpassing'currency_id'invals.
                                        /!\Thisvalueshouldbeequivalenttomove_line.amount_residual_currencyexcept
                                        wewanttoavoidbrowsingtherecordwhentheonlythingweneedinanoverview
                                        ofthereconciliation,forexampleinthereconciliationwidget.
            **kwargs:                  Additionalvaluesthatneedtolandontheaccount.move.linetocreate.
        :parammove_line:          Anoptionalaccount.move.linemove_linerepresentingthecounterpartlinetoreconcile.
        :return:                   Thevaluestocreateanewaccount.move.linemove_line.
        '''
        self.ensure_one()

        statement=self.statement_id
        journal=statement.journal_id
        company_currency=journal.company_id.currency_id
        journal_currency=journal.currency_idorcompany_currency
        foreign_currency=self.foreign_currency_idorjournal_currencyorcompany_currency
        statement_line_rate=(self.amount_currency/self.amount)ifself.amountelse0.0

        balance_to_reconcile=counterpart_vals.pop('balance',None)
        amount_residual=-counterpart_vals.pop('amount_residual',move_line.amount_residualifmove_lineelse0.0)\
            ifbalance_to_reconcileisNoneelsebalance_to_reconcile
        amount_residual_currency=-counterpart_vals.pop('amount_residual_currency',move_line.amount_residual_currencyifmove_lineelse0.0)\
            ifbalance_to_reconcileisNoneelsebalance_to_reconcile

        if'currency_id'incounterpart_vals:
            currency_id=counterpart_vals['currency_id']orforeign_currency.id
        elifmove_line:
            currency_id=move_line.currency_id.idorcompany_currency.id
        else:
            currency_id=foreign_currency.id

        ifcurrency_idnotin(foreign_currency.id,journal_currency.id):
            currency_id=company_currency.id
            amount_residual_currency=0.0

        amounts={
            company_currency.id:0.0,
            journal_currency.id:0.0,
            foreign_currency.id:0.0,
        }

        amounts[currency_id]=amount_residual_currency
        amounts[company_currency.id]=amount_residual

        ifcurrency_id==journal_currency.idandjournal_currency!=company_currency:
            ifforeign_currency!=company_currency:
                amounts[company_currency.id]=journal_currency._convert(amounts[currency_id],company_currency,journal.company_id,self.date)
            ifstatement_line_rate:
                amounts[foreign_currency.id]=amounts[currency_id]*statement_line_rate
        elifcurrency_id==foreign_currency.idandself.foreign_currency_id:
            ifstatement_line_rate:
                amounts[journal_currency.id]=amounts[foreign_currency.id]/statement_line_rate
                ifforeign_currency!=company_currency:
                    amounts[company_currency.id]=journal_currency._convert(amounts[journal_currency.id],company_currency,journal.company_id,self.date)
        else:
            amounts[journal_currency.id]=company_currency._convert(amounts[company_currency.id],journal_currency,journal.company_id,self.date)
            ifstatement_line_rate:
                amounts[foreign_currency.id]=amounts[journal_currency.id]*statement_line_rate

        ifforeign_currency==company_currencyandjournal_currency!=company_currencyandself.foreign_currency_id:
            balance=amounts[foreign_currency.id]
        else:
            balance=amounts[company_currency.id]

        ifforeign_currency!=company_currencyandself.foreign_currency_id:
            amount_currency=amounts[foreign_currency.id]
            currency_id=foreign_currency.id
        elifjournal_currency!=company_currencyandnotself.foreign_currency_id:
            amount_currency=amounts[journal_currency.id]
            currency_id=journal_currency.id
        else:
            amount_currency=amounts[company_currency.id]
            currency_id=company_currency.id

        return{
            **counterpart_vals,
            'name':counterpart_vals.get('name',move_line.nameifmove_lineelse''),
            'move_id':self.move_id.id,
            'partner_id':self.partner_id.idorcounterpart_vals.get('partner_id',move_line.partner_id.idifmove_lineelseFalse),
            'currency_id':currency_id,
            'account_id':counterpart_vals.get('account_id',move_line.account_id.idifmove_lineelseFalse),
            'debit':balanceifbalance>0.0else0.0,
            'credit':-balanceifbalance<0.0else0.0,
            'amount_currency':amount_currency,
        }

    @api.model
    def_prepare_move_line_default_vals(self,counterpart_account_id=None):
        '''Preparethedictionarytocreatethedefaultaccount.move.linesforthecurrentaccount.bank.statement.line
        record.
        :return:Alistofpythondictionarytobepassedtotheaccount.move.line's'create'method.
        '''
        self.ensure_one()

        ifnotcounterpart_account_id:
            counterpart_account_id=self.journal_id.suspense_account_id.id

        ifnotcounterpart_account_id:
            raiseUserError(_(
                "Youcan'tcreateanewstatementlinewithoutasuspenseaccountsetonthe%sjournal."
            )%self.journal_id.display_name)

        liquidity_line_vals=self._prepare_liquidity_move_line_vals()

        #Ensurethecounterpartwillhaveabalanceexactlyequalstotheamountinjournalcurrency.
        #Thisavoidsomeroundingissueswhenthecurrencyratebetweentwocurrenciesisnotsymmetrical.
        #E.g:
        #A.convert(amount_a,B)=amount_b
        #B.convert(amount_b,A)=amount_c!=amount_a

        counterpart_vals={
            'name':self.payment_ref,
            'account_id':counterpart_account_id,
            'amount_residual':liquidity_line_vals['debit']-liquidity_line_vals['credit'],
        }

        ifself.foreign_currency_idandself.foreign_currency_id!=self.company_currency_id:
            #Ensurethecounterpartwillhaveexactlythesameamountinforeigncurrencyastheamountsetinthe
            #statementlinetoavoidsomeroundingissueswhenmakingacurrencyconversion.

            counterpart_vals.update({
                'currency_id':self.foreign_currency_id.id,
                'amount_residual_currency':self.amount_currency,
            })
        elifliquidity_line_vals['currency_id']:
            #Ensurethecounterpartwillhaveabalanceexactlyequalstotheamountinjournalcurrency.
            #Thisavoidsomeroundingissueswhenthecurrencyratebetweentwocurrenciesisnotsymmetrical.
            #E.g:
            #A.convert(amount_a,B)=amount_b
            #B.convert(amount_b,A)=amount_c!=amount_a

            counterpart_vals.update({
                'currency_id':liquidity_line_vals['currency_id'],
                'amount_residual_currency':liquidity_line_vals['amount_currency'],
            })

        counterpart_line_vals=self._prepare_counterpart_move_line_vals(counterpart_vals)
        return[liquidity_line_vals,counterpart_line_vals]

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('journal_id','currency_id','amount','foreign_currency_id','amount_currency',
                 'move_id.to_check',
                 'move_id.line_ids.account_id','move_id.line_ids.amount_currency',
                 'move_id.line_ids.amount_residual_currency','move_id.line_ids.currency_id',
                 'move_id.line_ids.matched_debit_ids','move_id.line_ids.matched_credit_ids')
    def_compute_is_reconciled(self):
        '''Computethefieldindicatingifthestatementlinesarealreadyreconciledwithsomething.
        Thisfieldisusedfordisplaypurpose(e.g.displaythe'cancel'buttononthestatementlines).
        Alsocomputestheresidualamountofthestatementline.
        '''
        forst_lineinself:
            liquidity_lines,suspense_lines,other_lines=st_line._seek_for_lines()

            #Computeresidualamount
            ifst_line.to_check:
                st_line.amount_residual=-st_line.amount_currencyifst_line.foreign_currency_idelse-st_line.amount
            elifsuspense_lines.account_id.reconcile:
                st_line.amount_residual=sum(suspense_lines.mapped('amount_residual_currency'))
            else:
                st_line.amount_residual=sum(suspense_lines.mapped('amount_currency'))

            #Computeis_reconciled
            ifnotst_line.id:
                #Newrecord:Thejournalitemsarenotyetthere.
                st_line.is_reconciled=False
            elifsuspense_lines:
                #Incaseofthestatementlinecomesfromanolderversion,itcouldhavearesidualamountofzero.
                st_line.is_reconciled=suspense_lines.currency_id.is_zero(st_line.amount_residual)
            elifst_line.currency_id.is_zero(st_line.amount):
                st_line.is_reconciled=True
            else:
                #Thejournalentryseemsreconciled.
                st_line.is_reconciled=True

    #-------------------------------------------------------------------------
    #CONSTRAINTMETHODS
    #-------------------------------------------------------------------------

    @api.constrains('amount','amount_currency','currency_id','foreign_currency_id','journal_id')
    def_check_amounts_currencies(self):
        '''Ensuretheconsistencythespecifiedamountsandthecurrencies.'''

        forst_lineinself:
            ifst_line.journal_id!=st_line.statement_id.journal_id:
                raiseValidationError(_('Thejournalofastatementlinemustalwaysbethesameasthebankstatementone.'))
            ifst_line.foreign_currency_id==st_line.currency_id:
                raiseValidationError(_("Theforeigncurrencymustbedifferentthanthejournalone:%s",st_line.currency_id.name))
            ifnotst_line.foreign_currency_idandst_line.amount_currency:
                raiseValidationError(_("Youcan'tprovideanamountinforeigncurrencywithoutspecifyingaforeigncurrency."))

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    @api.model_create_multi
    defcreate(self,vals_list):
        #OVERRIDE
        counterpart_account_ids=[]

        forvalsinvals_list:
            statement=self.env['account.bank.statement'].browse(vals['statement_id'])
            ifstatement.state!='open'andself._context.get('check_move_validity',True):
                raiseUserError(_("Youcanonlycreatestatementlineinopenbankstatements."))

            #Forcethemove_typetoavoidinconsistencywithresidual'default_move_type'insidethecontext.
            vals['move_type']='entry'

            journal=statement.journal_id
            #Ensurethejournalisthesameasthestatementone.
            vals['journal_id']=journal.id
            vals['currency_id']=(journal.currency_idorjournal.company_id.currency_id).id
            if'date'notinvals:
                vals['date']=statement.date

            #Avoidhavingthesameforeign_currency_idascurrency_id.
            journal_currency=journal.currency_idorjournal.company_id.currency_id
            ifvals.get('foreign_currency_id')==journal_currency.id:
                vals['foreign_currency_id']=None
                vals['amount_currency']=0.0

            #Hacktoforcedifferentaccountinsteadofthesuspenseaccount.
            counterpart_account_ids.append(vals.pop('counterpart_account_id',None))

        st_lines=super().create(vals_list)

        fori,st_lineinenumerate(st_lines):
            counterpart_account_id=counterpart_account_ids[i]

            to_write={'statement_line_id':st_line.id}
            if'line_ids'notinvals_list[i]:
                to_write['line_ids']=[(0,0,line_vals)forline_valsinst_line._prepare_move_line_default_vals(counterpart_account_id=counterpart_account_id)]

            st_line.move_id.write(to_write)

        returnst_lines

    defwrite(self,vals):
        #OVERRIDE
        res=super().write(vals)
        self._synchronize_to_moves(set(vals.keys()))
        returnres

    defunlink(self):
        #OVERRIDEtounlinktheinheritedaccount.move(move_idfield)aswell.
        moves=self.with_context(force_delete=True).mapped('move_id')
        res=super().unlink()
        moves.unlink()
        returnres

    #-------------------------------------------------------------------------
    #SYNCHRONIZATIONaccount.bank.statement.line<->account.move
    #-------------------------------------------------------------------------

    def_synchronize_from_moves(self,changed_fields):
        '''Updatetheaccount.bank.statement.lineregardingitsrelatedaccount.move.
        Also,checkbothmodelsarestillconsistent.
        :paramchanged_fields:Asetcontainingallmodifiedfieldsonaccount.move.
        '''
        ifself._context.get('skip_account_move_synchronization'):
            return

        forst_lineinself.with_context(skip_account_move_synchronization=True):
            move=st_line.move_id
            move_vals_to_write={}
            st_line_vals_to_write={}

            if'state'inchanged_fields:
                if(st_line.state=='open'andmove.state!='draft')or(st_line.statein('posted','confirm')andmove.state!='posted'):
                    raiseUserError(_(
                        "Youcan'tmanuallychangethestateofjournalentry%s,asithasbeencreatedbybank"
                        "statement%s."
                    )%(st_line.move_id.display_name,st_line.statement_id.display_name))

            if'line_ids'inchanged_fields:
                liquidity_lines,suspense_lines,other_lines=st_line._seek_for_lines()
                company_currency=st_line.journal_id.company_id.currency_id
                journal_currency=st_line.journal_id.currency_idifst_line.journal_id.currency_id!=company_currencyelseFalse

                iflen(liquidity_lines)!=1:
                    raiseUserError(_(
                        "Thejournalentry%sreachedaninvalidstateregardingitsrelatedstatementline.\n"
                        "Tobeconsistent,thejournalentrymustalwayshaveexactlyonejournaliteminvolvingthe"
                        "bank/cashaccount."
                    )%st_line.move_id.display_name)

                st_line_vals_to_write.update({
                    'payment_ref':liquidity_lines.name,
                    'partner_id':liquidity_lines.partner_id.id,
                })

                #Update'amount'accordingtotheliquidityline.

                ifjournal_currency:
                    st_line_vals_to_write.update({
                        'amount':liquidity_lines.amount_currency,
                    })
                else:
                    st_line_vals_to_write.update({
                        'amount':liquidity_lines.balance,
                    })

                iflen(suspense_lines)==1:

                    ifjournal_currencyandsuspense_lines.currency_id==journal_currency:

                        #Thesuspenselineisexpressedinthejournal'scurrencymeaningtheforeigncurrency
                        #setonthestatementlineisnolongerneeded.

                        st_line_vals_to_write.update({
                            'amount_currency':0.0,
                            'foreign_currency_id':False,
                        })

                    elifnotjournal_currencyandsuspense_lines.currency_id==company_currency:

                        #Don'tsetaspecificforeigncurrencyonthestatementline.

                        st_line_vals_to_write.update({
                            'amount_currency':0.0,
                            'foreign_currency_id':False,
                        })

                    else:

                        #Updatethestatementlineregardingtheforeigncurrencyofthesuspenseline.

                        st_line_vals_to_write.update({
                            'amount_currency':-suspense_lines.amount_currency,
                            'foreign_currency_id':suspense_lines.currency_id.id,
                        })

                move_vals_to_write.update({
                    'partner_id':liquidity_lines.partner_id.id,
                    'currency_id':(st_line.foreign_currency_idorjournal_currencyorcompany_currency).id,
                })

            move.write(move._cleanup_write_orm_values(move,move_vals_to_write))
            st_line.write(move._cleanup_write_orm_values(st_line,st_line_vals_to_write))

    def_synchronize_to_moves(self,changed_fields):
        '''Updatetheaccount.moveregardingthemodifiedaccount.bank.statement.line.
        :paramchanged_fields:Alistcontainingallmodifiedfieldsonaccount.bank.statement.line.
        '''
        ifself._context.get('skip_account_move_synchronization'):
            return

        ifnotany(field_nameinchanged_fieldsforfield_namein(
            'payment_ref','amount','amount_currency',
            'foreign_currency_id','currency_id','partner_id',
        )):
            return

        forst_lineinself.with_context(skip_account_move_synchronization=True):
            liquidity_lines,suspense_lines,other_lines=st_line._seek_for_lines()
            company_currency=st_line.journal_id.company_id.currency_id
            journal_currency=st_line.journal_id.currency_idifst_line.journal_id.currency_id!=company_currencyelseFalse

            line_vals_list=st_line._prepare_move_line_default_vals()
            line_ids_commands=[(1,liquidity_lines.id,line_vals_list[0])]

            ifsuspense_lines:
                line_ids_commands.append((1,suspense_lines.id,line_vals_list[1]))
            else:
                line_ids_commands.append((0,0,line_vals_list[1]))

            forlineinother_lines:
                line_ids_commands.append((2,line.id))

            st_line.move_id.write({
                'partner_id':st_line.partner_id.id,
                'currency_id':(st_line.foreign_currency_idorjournal_currencyorcompany_currency).id,
                'line_ids':line_ids_commands,
            })

    #-------------------------------------------------------------------------
    #RECONCILIATIONMETHODS
    #-------------------------------------------------------------------------

    def_prepare_reconciliation(self,lines_vals_list,create_payment_for_invoice=False):
        '''Helperforthe"reconcile"methodusedtogetafullpreviewofthereconciliationresult.Thismethodis
        quiteusefultodealwithreconcilemodelsorthereconciliationwidgetbecauseitensuresthevaluesseenby
        theuserareexactlythevaluesyougetafterreconciling.

        :paramlines_vals_list:            Seethe'reconcile'method.
        :paramcreate_payment_for_invoice: Aflagindicatingthestatementlinemustcreatepaymentsontheflyduring
                                            thereconciliation.
        :return:Thedifftobeappliedonthestatementlineasatuple
        (
            lines_to_create:   Thevaluestocreatetheaccount.move.lineonthestatementline.
            payments_to_create:Thevaluestocreatetheaccount.payments.
            open_balance_vals: Adictionarytocreatetheopen-balancelineorNoneifthereconciliationisfull.
            existing_lines:    Thecounterpartlinestowhichthereconciliationwillbedone.
        )
        '''

        self.ensure_one()
        journal=self.journal_id
        company_currency=journal.company_id.currency_id
        foreign_currency=self.foreign_currency_idorjournal.currency_idorcompany_currency

        liquidity_lines,suspense_lines,other_lines=self._seek_for_lines()

        #Ensurethestatementlinehasnotyetbeenalreadyreconciled.
        #Ifthemovehas'to_check'enabled,itmeansthestatementlinehascreatedsomelinesthat
        #needtobecheckedlaterandreplacedbytherealones.
        ifnotself.move_id.to_checkandother_lines:
            raiseUserError(_("Thestatementlinehasalreadybeenreconciled."))

        #Alistofdictionarycontaining:
        #-line_vals:         Thevaluestocreatetheaccount.move.lineonthestatementline.
        #-payment_vals:      Theoptionalvaluestocreateabridgeaccount.payment
        #-counterpart_line:  Theoptionalcounterpartlinetoreconcilewith'line'.
        reconciliation_overview=[]

        total_balance=liquidity_lines.balance
        total_amount_currency=-self._prepare_move_line_default_vals()[1]['amount_currency']

        #Step1:Split'lines_vals_list'intotwobatches:
        #-Theexistingaccount.move.linesthatneedtobereconciledwiththestatementline.
        #      =>Willbemanagedatstep2.
        #-Theaccount.move.linestobecreatedfromscratch.
        #      =>Willbemanageddirectly.

        to_browse_ids=[]
        to_process_vals=[]
        forvalsinlines_vals_list:
            #Don'tmodifytheparamsdirectly.
            vals=dict(vals)

            if'id'invals:
                #Existingaccount.move.line.
                to_browse_ids.append(vals.pop('id'))
                to_process_vals.append(vals)
            else:
                #Newlycreatedaccount.move.linefromscratch.
                line_vals=self._prepare_counterpart_move_line_vals(vals)
                total_balance+=line_vals['debit']-line_vals['credit']
                total_amount_currency+=line_vals['amount_currency']

                reconciliation_overview.append({
                    'line_vals':line_vals,
                })

        #Step2:Browsecounterpartlinesallinoneandprocessthem.

        existing_lines=self.env['account.move.line'].browse(to_browse_ids)
        forline,counterpart_valsinzip(existing_lines,to_process_vals):
            line_vals=self._prepare_counterpart_move_line_vals(counterpart_vals,move_line=line)
            balance=line_vals['debit']-line_vals['credit']
            amount_currency=line_vals['amount_currency']

            reconciliation_vals={
                'line_vals':line_vals,
                'counterpart_line':line,
            }

            ifcreate_payment_for_invoiceandline.account_internal_typein('receivable','payable'):

                #Preparevaluestocreateanewaccount.payment.
                payment_vals=self.env['account.payment.register']\
                    .with_context(active_model='account.move.line',active_ids=line.ids)\
                    .create({
                        'amount':abs(amount_currency)ifline_vals['currency_id']elseabs(balance),
                        'payment_date':self.date,
                        'payment_type':'inbound'ifbalance<0.0else'outbound',
                        'journal_id':self.journal_id.id,
                        'currency_id':(self.foreign_currency_idorself.currency_id).id,
                     })\
                     ._create_payment_vals_from_wizard()

                ifpayment_vals['payment_type']=='inbound':
                    liquidity_account=self.journal_id.payment_debit_account_id
                else:
                    liquidity_account=self.journal_id.payment_credit_account_id

                #Preservetherateofthestatementline.
                payment_vals['line_ids']=[
                    #Receivable/Payableline.
                    (0,0,{
                        **line_vals,
                    }),

                    #Liquidityline.
                    (0,0,{
                        **line_vals,
                        'amount_currency':-line_vals['amount_currency'],
                        'debit':line_vals['credit'],
                        'credit':line_vals['debit'],
                        'account_id':liquidity_account.id,
                    }),
                ]

                #Preparethelinetobereconciledwiththepayment.
                ifpayment_vals['payment_type']=='inbound':
                    #Receivemoney.
                    line_vals['account_id']=self.journal_id.payment_debit_account_id.id
                elifpayment_vals['payment_type']=='outbound':
                    #Sendmoney.
                    line_vals['account_id']=self.journal_id.payment_credit_account_id.id

                reconciliation_vals['payment_vals']=payment_vals

            reconciliation_overview.append(reconciliation_vals)

            total_balance+=balance
            total_amount_currency+=amount_currency

        #Step3:Fixroundingissueduetocurrencyconversions.
        #Addtheremainingbalanceonthefirstencounteredlinestartingwiththecustomones.

        ifforeign_currency.is_zero(total_amount_currency)andnotcompany_currency.is_zero(total_balance):
            vals=reconciliation_overview[0]['line_vals']
            new_balance=vals['debit']-vals['credit']-total_balance
            vals.update({
                'debit':new_balanceifnew_balance>0.0else0.0,
                'credit':-new_balanceifnew_balance<0.0else0.0,
            })
            total_balance=0.0

        #Step4:Ifthejournalentryisnotyetbalanced,createanopenbalance.

        ifself.company_currency_id.round(total_balance):
            counterpart_vals={
                'name':'%s:%s'%(self.payment_ref,_('OpenBalance')),
                'balance':-total_balance,
                'currency_id':self.company_currency_id.id,
            }

            partner=self.partner_idorexisting_lines.mapped('partner_id')[:1]
            ifpartner:
                ifself.amount>0:
                    open_balance_account=partner.with_company(self.company_id).property_account_receivable_id
                else:
                    open_balance_account=partner.with_company(self.company_id).property_account_payable_id

                counterpart_vals['account_id']=open_balance_account.id
                counterpart_vals['partner_id']=partner.id
            else:
                ifself.amount>0:
                    open_balance_account=self.company_id.partner_id.with_company(self.company_id).property_account_receivable_id
                else:
                    open_balance_account=self.company_id.partner_id.with_company(self.company_id).property_account_payable_id
                counterpart_vals['account_id']=open_balance_account.id

            open_balance_vals=self._prepare_counterpart_move_line_vals(counterpart_vals)
        else:
            open_balance_vals=None

        returnreconciliation_overview,open_balance_vals

    defreconcile(self,lines_vals_list,to_check=False):
        '''Performareconciliationonthecurrentaccount.bank.statement.linewithsome
        counterpartaccount.move.line.
        Ifthestatementlineentryisnotfullybalancedafterthereconciliation,anopenbalancewillbecreated
        usingthepartner.

        :paramlines_vals_list:Alistofpythondictionarycontaining:
            'id':              Optionalidofanexistingaccount.move.line.
                                Foreachlinehavingan'id',anewlinewillbecreatedinthecurrentstatementline.
            'balance':         Optionalamounttoconsiderduringthereconciliation.Ifaforeigncurrencyissetonthe
                                counterpartlineinthesameforeigncurrencyasthestatementline,thenthisamountis
                                consideredastheamountinforeigncurrency.Ifnotspecified,thefullbalanceistaken.
                                Thisvaluemustbeprovidedif'id'isnot.
            **kwargs:          Customvaluestobesetonthenewlycreatedaccount.move.line.
        :paramto_check:       Markthecurrentstatementlineas"to_check"(seefieldformoredetails).
        '''
        self.ensure_one()
        liquidity_lines,suspense_lines,other_lines=self._seek_for_lines()

        reconciliation_overview,open_balance_vals=self._prepare_reconciliation(lines_vals_list)

        #====Manageres.partner.bank====

        ifself.account_numberandself.partner_idandnotself.partner_bank_id:
            self.partner_bank_id=self._find_or_create_bank_account()

        #====Checkopenbalance====

        ifopen_balance_vals:
            ifnotopen_balance_vals.get('partner_id'):
                raiseUserError(_("Unabletocreateanopenbalanceforastatementlinewithoutapartnerset."))
            ifnotopen_balance_vals.get('account_id'):
                raiseUserError(_("Unabletocreateanopenbalanceforastatementlinebecausethereceivable"
                                  "/payableaccountsaremissingonthepartner."))

        #====Create&reconcilepayments====
        #Whenreconcilingtoareceivable/payableaccount,createanpaymentonthefly.

        pay_reconciliation_overview=[reconciliation_vals
                                       forreconciliation_valsinreconciliation_overview
                                       ifreconciliation_vals.get('payment_vals')]
        ifpay_reconciliation_overview:
            payment_vals_list=[reconciliation_vals['payment_vals']forreconciliation_valsinpay_reconciliation_overview]
            payments=self.env['account.payment'].create(payment_vals_list)

            payments.action_post()

            forreconciliation_vals,paymentinzip(pay_reconciliation_overview,payments):
                reconciliation_vals['payment']=payment

                #Reconcilethenewlycreatedpaymentwiththecounterpartline.
                (reconciliation_vals['counterpart_line']+payment.line_ids)\
                    .filtered(lambdaline:line.account_id==reconciliation_vals['counterpart_line'].account_id)\
                    .reconcile()

        #====Create&reconcilelinesonthebankstatementline====

        to_create_commands=[(0,0,open_balance_vals)]ifopen_balance_valselse[]
        to_delete_commands=[(2,line.id)forlineinsuspense_lines+other_lines]

        #Cleanuppreviouslines.
        self.move_id.with_context(check_move_validity=False,skip_account_move_synchronization=True,force_delete=True).write({
            'line_ids':to_delete_commands+to_create_commands,
            'to_check':to_check,
        })

        line_vals_list=[reconciliation_vals['line_vals']forreconciliation_valsinreconciliation_overview]
        new_lines=self.env['account.move.line'].create(line_vals_list)
        new_lines=new_lines.with_context(skip_account_move_synchronization=True)
        forreconciliation_vals,lineinzip(reconciliation_overview,new_lines):
            ifreconciliation_vals.get('payment'):
                accounts=(self.journal_id.payment_debit_account_id,self.journal_id.payment_credit_account_id)
                counterpart_line=reconciliation_vals['payment'].line_ids.filtered(lambdaline:line.account_idinaccounts)
            elifreconciliation_vals.get('counterpart_line'):
                counterpart_line=reconciliation_vals['counterpart_line']
            else:
                continue

            (line+counterpart_line).reconcile()

        #Assignpartnerifneeded(forexample,whenreconcilingastatement
        #linewithnopartner,withaninvoice;assignthepartnerofthisinvoice)
        ifnotself.partner_id:
            rec_overview_partners=set(overview['counterpart_line'].partner_id.id
                                        foroverviewinreconciliation_overview
                                        ifoverview.get('counterpart_line'))
            iflen(rec_overview_partners)==1andrec_overview_partners!={False}:
                self.line_ids.write({'partner_id':rec_overview_partners.pop()})

        #Refreshanalyticlines.
        self.move_id.line_ids.analytic_line_ids.unlink()
        self.move_id.line_ids.create_analytic_lines()

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------

    def_find_or_create_bank_account(self):
        bank_account=self.env['res.partner.bank'].search(
            [('company_id','=',self.company_id.id),('acc_number','=',self.account_number)])
        ifnotbank_account:
            bank_account=self.env['res.partner.bank'].create({
                'acc_number':self.account_number,
                'partner_id':self.partner_id.id,
                'company_id':self.company_id.id,
            })
        returnbank_account

    defbutton_undo_reconciliation(self):
        '''Undothereconciliationmadesonthestatementlineandresettheirjournalitems
        totheiroriginalstates.
        '''
        self.line_ids.remove_move_reconcile()
        self.payment_ids.unlink()

        forst_lineinself:
            st_line.with_context(force_delete=True).write({
                'to_check':False,
                'line_ids':[(5,0)]+[(0,0,line_vals)forline_valsinst_line._prepare_move_line_default_vals()],
            })
