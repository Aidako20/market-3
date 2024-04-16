#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_,tools
fromflectra.osvimportexpression
fromflectra.exceptionsimportUserError,ValidationError


classAccountAccountType(models.Model):
    _name="account.account.type"
    _description="AccountType"

    name=fields.Char(string='AccountType',required=True,translate=True)
    include_initial_balance=fields.Boolean(string="BringAccountsBalanceForward",help="Usedinreportstoknowifweshouldconsiderjournalitemsfromthebeginningoftimeinsteadoffromthefiscalyearonly.Accounttypesthatshouldberesettozeroateachnewfiscalyear(likeexpenses,revenue..)shouldnothavethisoptionset.")
    type=fields.Selection([
        ('other','Regular'),
        ('receivable','Receivable'),
        ('payable','Payable'),
        ('liquidity','Liquidity'),
    ],required=True,default='other',
        help="The'InternalType'isusedforfeaturesavailableon"\
        "differenttypesofaccounts:liquiditytypeisforcashorbankaccounts"\
        ",payable/receivableisforvendor/customeraccounts.")
    internal_group=fields.Selection([
        ('equity','Equity'),
        ('asset','Asset'),
        ('liability','Liability'),
        ('income','Income'),
        ('expense','Expense'),
        ('off_balance','OffBalance'),
    ],string="InternalGroup",
        required=True,
        help="The'InternalGroup'isusedtofilteraccountsbasedontheinternalgroupsetontheaccounttype.")
    note=fields.Text(string='Description')


classAccountAccount(models.Model):
    _name="account.account"
    _description="Account"
    _order="is_off_balance,code,company_id"
    _check_company_auto=True

    @api.constrains('internal_type','reconcile')
    def_check_reconcile(self):
        foraccountinself:
            ifaccount.internal_typein('receivable','payable')andaccount.reconcile==False:
                raiseValidationError(_('Youcannothaveareceivable/payableaccountthatisnotreconcilable.(accountcode:%s)',account.code))

    @api.constrains('user_type_id')
    def_check_user_type_id_unique_current_year_earning(self):
        data_unaffected_earnings=self.env.ref('account.data_unaffected_earnings')
        result=self.read_group([('user_type_id','=',data_unaffected_earnings.id)],['company_id'],['company_id'])
        forresinresult:
            ifres.get('company_id_count',0)>=2:
                account_unaffected_earnings=self.search([('company_id','=',res['company_id'][0]),
                                                           ('user_type_id','=',data_unaffected_earnings.id)])
                raiseValidationError(_('Youcannothavemorethanoneaccountwith"CurrentYearEarnings"astype.(accounts:%s)',[a.codeforainaccount_unaffected_earnings]))

    name=fields.Char(string="AccountName",required=True,index=True)
    currency_id=fields.Many2one('res.currency',string='AccountCurrency',
        help="Forcesallmovesforthisaccounttohavethisaccountcurrency.")
    code=fields.Char(size=64,required=True,index=True)
    deprecated=fields.Boolean(index=True,default=False)
    used=fields.Boolean(compute='_compute_used',search='_search_used')
    user_type_id=fields.Many2one('account.account.type',string='Type',required=True,
        help="AccountTypeisusedforinformationpurpose,togeneratecountry-specificlegalreports,andsettherulestocloseafiscalyearandgenerateopeningentries.")
    internal_type=fields.Selection(related='user_type_id.type',string="InternalType",store=True,readonly=True)
    internal_group=fields.Selection(related='user_type_id.internal_group',string="InternalGroup",store=True,readonly=True)
    #has_unreconciled_entries=fields.Boolean(compute='_compute_has_unreconciled_entries',
    #   help="Theaccounthasatleastoneunreconcileddebitandcreditsincelasttimetheinvoices&paymentsmatchingwasperformed.")
    reconcile=fields.Boolean(string='AllowReconciliation',default=False,
        help="Checkthisboxifthisaccountallowsinvoices&paymentsmatchingofjournalitems.")
    tax_ids=fields.Many2many('account.tax','account_account_tax_default_rel',
        'account_id','tax_id',string='DefaultTaxes',
        check_company=True,
        context={'append_type_to_tax_name':True})
    note=fields.Text('InternalNotes')
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,
        default=lambdaself:self.env.company)
    tag_ids=fields.Many2many('account.account.tag','account_account_account_tag',string='Tags',help="Optionaltagsyoumaywanttoassignforcustomreporting")
    group_id=fields.Many2one('account.group',compute='_compute_account_group',store=True,readonly=True)
    root_id=fields.Many2one('account.root',compute='_compute_account_root',store=True)
    allowed_journal_ids=fields.Many2many('account.journal',string="AllowedJournals",help="Defineinwhichjournalsthisaccountcanbeused.Ifempty,canbeusedinalljournals.")

    opening_debit=fields.Monetary(string="OpeningDebit",compute='_compute_opening_debit_credit',inverse='_set_opening_debit',help="Openingdebitvalueforthisaccount.")
    opening_credit=fields.Monetary(string="OpeningCredit",compute='_compute_opening_debit_credit',inverse='_set_opening_credit',help="Openingcreditvalueforthisaccount.")
    opening_balance=fields.Monetary(string="OpeningBalance",compute='_compute_opening_debit_credit',help="Openingbalancevalueforthisaccount.")

    is_off_balance=fields.Boolean(compute='_compute_is_off_balance',default=False,store=True,readonly=True)

    _sql_constraints=[
        ('code_company_uniq','unique(code,company_id)','Thecodeoftheaccountmustbeuniquepercompany!')
    ]

    @api.constrains('reconcile','internal_group','tax_ids')
    def_constrains_reconcile(self):
        forrecordinself:
            ifrecord.internal_group=='off_balance':
                ifrecord.reconcile:
                    raiseUserError(_('AnOff-Balanceaccountcannotbereconcilable'))
                ifrecord.tax_ids:
                    raiseUserError(_('AnOff-Balanceaccountcannothavetaxes'))

    @api.constrains('allowed_journal_ids')
    def_constrains_allowed_journal_ids(self):
        self.env['account.move.line'].flush(['account_id','journal_id'])
        self.flush(['allowed_journal_ids'])
        self._cr.execute("""
            SELECTaml.id
            FROMaccount_move_lineaml
            WHEREaml.account_idin%s
            ANDEXISTS(SELECT1FROMaccount_account_account_journal_relWHEREaccount_account_id=aml.account_id)
            ANDNOTEXISTS(SELECT1FROMaccount_account_account_journal_relWHEREaccount_account_id=aml.account_idANDaccount_journal_id=aml.journal_id)
        """,[tuple(self.ids)])
        ids=self._cr.fetchall()
        ifids:
            raiseValidationError(_('Somejournalitemsalreadyexistwiththisaccountbutinotherjournalsthantheallowedones.'))

    @api.constrains('currency_id')
    def_check_journal_consistency(self):
        '''Ensurethecurrencysetonthejournalisthesameasthecurrencysetonthe
        linkedaccounts.
        '''
        ifnotself:
            return

        self.env['account.account'].flush(['currency_id'])
        self.env['account.journal'].flush([
            'currency_id',
            'default_account_id',
            'payment_debit_account_id',
            'payment_credit_account_id',
            'suspense_account_id',
        ])
        self._cr.execute('''
            SELECTaccount.id,journal.id
            FROMaccount_accountaccount
            JOINres_companycompanyONcompany.id=account.company_id
            JOINaccount_journaljournalON
                journal.default_account_id=account.id
            WHEREaccount.idIN%s
            ANDjournal.typeIN('bank','cash')
            ANDjournal.currency_idISNOTNULL
            ANDjournal.currency_id!=company.currency_id
            ANDaccount.currency_id!=journal.currency_id
        ''',[tuple(self.ids)])
        res=self._cr.fetchone()
        ifres:
            account=self.env['account.account'].browse(res[0])
            journal=self.env['account.journal'].browse(res[1])
            raiseValidationError(_(
                "Theforeigncurrencysetonthejournal'%(journal)s'andtheaccount'%(account)s'mustbethesame.",
                journal=journal.display_name,
                account=account.display_name
            ))

    @api.constrains('company_id')
    def_check_company_consistency(self):
        ifnotself:
            return

        self.flush(['company_id'])
        self._cr.execute('''
            SELECTline.id
            FROMaccount_move_lineline
            JOINaccount_accountaccountONaccount.id=line.account_id
            WHEREline.account_idIN%s
            ANDline.company_id!=account.company_id
        ''',[tuple(self.ids)])
        ifself._cr.fetchone():
            raiseUserError(_("Youcan'tchangethecompanyofyouraccountsincetherearesomejournalitemslinkedtoit."))

    @api.constrains('user_type_id')
    def_check_user_type_id_sales_purchase_journal(self):
        ifnotself:
            return

        self.flush(['user_type_id'])
        self._cr.execute('''
            SELECTaccount.id
            FROMaccount_accountaccount
            JOINaccount_account_typeacc_typeONaccount.user_type_id=acc_type.id
            JOINaccount_journaljournalONjournal.default_account_id=account.id
            WHEREaccount.idIN%s
            ANDacc_type.typeIN('receivable','payable')
            ANDjournal.typeIN('sale','purchase')
            LIMIT1;
        ''',[tuple(self.ids)])

        ifself._cr.fetchone():
            raiseValidationError(_("Theaccountisalreadyinuseina'sale'or'purchase'journal.Thismeansthattheaccount'stypecouldn'tbe'receivable'or'payable'."))

    @api.constrains('reconcile')
    def_check_used_as_journal_default_debit_credit_account(self):
        accounts=self.filtered(lambdaa:nota.reconcile)
        ifnotaccounts:
            return

        self.flush(['reconcile'])
        self._cr.execute('''
            SELECTjournal.id
            FROMaccount_journaljournal
            WHERE(
                journal.payment_credit_account_idIN%(accounts)s
                ANDjournal.payment_credit_account_id!=journal.default_account_id
                )OR(
                journal.payment_debit_account_idIN%(accounts)s
                ANDjournal.payment_debit_account_id!=journal.default_account_id
            )
        ''',{'accounts':tuple(accounts.ids)})

        rows=self._cr.fetchall()
        ifrows:
            journals=self.env['account.journal'].browse([r[0]forrinrows])
            raiseValidationError(_(
                "Thisaccountisconfiguredin%(journal_names)sjournal(s)(ids%(journal_ids)s)aspaymentdebitorcreditaccount.Thismeansthatthisaccount'stypeshouldbereconcilable.",
                journal_names=journals.mapped('display_name'),
                journal_ids=journals.ids
            ))

    @api.depends('code')
    def_compute_account_root(self):
        #thiscomputesthefirst2digitsoftheaccount.
        #Thisfieldshouldhavebeenachar,buttheaimistouseitinasidepanelviewwithhierarchy,andit'sonlysupportedbymany2onefieldssofar.
        #Soinstead,wemakeitamany2onetoapsqlviewwithwhatweneedasrecords.
        forrecordinself:
            record.root_id=(ord(record.code[0])*1000+ord(record.code[1:2]or'\x00'))ifrecord.codeelseFalse

    @api.depends('code')
    def_compute_account_group(self):
        ifself.ids:
            self.env['account.group']._adapt_accounts_for_account_groups(self)
        else:
            self.group_id=False

    def_search_used(self,operator,value):
        ifoperatornotin['=','!=']ornotisinstance(value,bool):
            raiseUserError(_('Operationnotsupported'))
        ifoperator!='=':
            value=notvalue
        self._cr.execute("""
            SELECTidFROMaccount_accountaccount
            WHEREEXISTS(SELECT*FROMaccount_move_lineamlWHEREaml.account_id=account.idLIMIT1)
        """)
        return[('id','in'ifvalueelse'notin',[r[0]forrinself._cr.fetchall()])]

    def_compute_used(self):
        ids=set(self._search_used('=',True)[0][2])
        forrecordinself:
            record.used=record.idinids

    @api.model
    def_search_new_account_code(self,company,digits,prefix):
        fornuminrange(1,10000):
            new_code=str(prefix.ljust(digits-1,'0'))+str(num)
            rec=self.search([('code','=',new_code),('company_id','=',company.id)],limit=1)
            ifnotrec:
                returnnew_code
        raiseUserError(_('Cannotgenerateanunusedaccountcode.'))

    def_compute_opening_debit_credit(self):
        self.opening_debit=0
        self.opening_credit=0
        self.opening_balance=0
        ifnotself.ids:
            return
        self.env.cr.execute("""
            SELECTline.account_id,
                   SUM(line.balance)ASbalance,
                   SUM(line.debit)ASdebit,
                   SUM(line.credit)AScredit
              FROMaccount_move_lineline
              JOINres_companycompONcomp.id=line.company_id
             WHEREline.move_id=comp.account_opening_move_id
               ANDline.account_idIN%s
             GROUPBYline.account_id
        """,[tuple(self.ids)])
        result={r['account_id']:rforrinself.env.cr.dictfetchall()}
        forrecordinself:
            res=result.get(record.id)or{'debit':0,'credit':0,'balance':0}
            record.opening_debit=res['debit']
            record.opening_credit=res['credit']
            record.opening_balance=res['balance']

    @api.depends('internal_group')
    def_compute_is_off_balance(self):
        foraccountinself:
            account.is_off_balance=account.internal_group=="off_balance"

    def_set_opening_debit(self):
        forrecordinself:
            record._set_opening_debit_credit(record.opening_debit,'debit')

    def_set_opening_credit(self):
        forrecordinself:
            record._set_opening_debit_credit(record.opening_credit,'credit')

    def_set_opening_debit_credit(self,amount,field):
        """Genericfunctioncalledbybothopening_debitandopening_credit's
        inversefunction.'Amount'parameteristhevaluetobeset,andfield
        either'debit'or'credit',dependingonwhichoneofthesetwofields
        gotassigned.
        """
        self.company_id.create_op_move_if_non_existant()
        opening_move=self.company_id.account_opening_move_id

        ifopening_move.state=='draft':
            #checkwhetherweshouldcreateanewmovelineormodifyanexistingone
            account_op_lines=self.env['account.move.line'].search([('account_id','=',self.id),
                                                                      ('move_id','=',opening_move.id),
                                                                      (field,'!=',False),
                                                                      (field,'!=',0.0)])#0.0conditionimportantforimport

            ifaccount_op_lines:
                op_aml_debit=sum(account_op_lines.mapped('debit'))
                op_aml_credit=sum(account_op_lines.mapped('credit'))

                #Theremightbemorethanonelineonthisaccountiftheopeningentrywasmanuallyedited
                #Ifso,weneedtomergeallthoselinesintoonebeforemodifyingitsbalance
                opening_move_line=account_op_lines[0]
                iflen(account_op_lines)>1:
                    merge_write_cmd=[(1,opening_move_line.id,{'debit':op_aml_debit,'credit':op_aml_credit,'partner_id':None,'name':_("Openingbalance")})]
                    unlink_write_cmd=[(2,line.id)forlineinaccount_op_lines[1:]]
                    opening_move.write({'line_ids':merge_write_cmd+unlink_write_cmd})

                ifamount:
                    #modifytheline
                    opening_move_line.with_context(check_move_validity=False)[field]=amount
                else:
                    #deletetheline(noneedtokeepalinewithvalue=0)
                    opening_move_line.with_context(check_move_validity=False).unlink()

            elifamount:
                #createanewline,asnoneexistedbefore
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name':_('Openingbalance'),
                        field:amount,
                        'move_id':opening_move.id,
                        'account_id':self.id,
                })

            #Then,weautomaticallybalancetheopeningmove,tomakesureitstaysvalid
            ifnot'import_file'inself.env.context:
                #Whenimportingafile,avoidrecomputingtheopeningmoveforeachaccountanddoitattheend,forbetterperformances
                self.company_id._auto_balance_opening_move()

    @api.model
    defdefault_get(self,default_fields):
        """Ifwe'recreatinganewaccountthroughamany2one,therearechancesthatwetypedtheaccountcode
        insteadofitsname.Inthatcase,switchbothfieldsvalues.
        """
        if'name'notindefault_fieldsand'code'notindefault_fields:
            returnsuper().default_get(default_fields)
        default_name=self._context.get('default_name')
        default_code=self._context.get('default_code')
        ifdefault_nameandnotdefault_code:
            try:
                default_code=int(default_name)
            exceptValueError:
                pass
            ifdefault_code:
                default_name=False
        contextual_self=self.with_context(default_name=default_name,default_code=default_code)
        returnsuper(AccountAccount,contextual_self).default_get(default_fields)

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        domain=[]
        ifname:
            ifoperatorin('=','!='):
                domain=['|',('code','=',name.split('')[0]),('name',operator,name)]
            else:
                domain=['|',('code','=ilike',name.split('')[0]+'%'),('name',operator,name)]
            ifoperatorinexpression.NEGATIVE_TERM_OPERATORS:
                domain=['&','!']+domain[1:]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    @api.onchange('user_type_id')
    def_onchange_user_type_id(self):
        self.reconcile=self.internal_typein('receivable','payable')
        ifself.internal_type=='liquidity':
            self.reconcile=False
        elifself.internal_group=='off_balance':
            self.reconcile=False
            self.tax_ids=False

    defname_get(self):
        result=[]
        foraccountinself:
            name=account.code+''+account.name
            result.append((account.id,name))
        returnresult

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        default=dict(defaultor{})
        ifdefault.get('code',False):
            returnsuper(AccountAccount,self).copy(default)
        try:
            default['code']=(str(int(self.code)+10)or'').zfill(len(self.code))
            default.setdefault('name',_("%s(copy)")%(self.nameor''))
            whileself.env['account.account'].search([('code','=',default['code']),
                                                      ('company_id','=',default.get('company_id',False)orself.company_id.id)],limit=1):
                default['code']=(str(int(default['code'])+10)or'')
                default['name']=_("%s(copy)")%(self.nameor'')
        exceptValueError:
            default['code']=_("%s(copy)")%(self.codeor'')
            default['name']=self.name
        returnsuper(AccountAccount,self).copy(default)

    @api.model
    defload(self,fields,data):
        """Overriddenforbetterperformanceswhenimportingalistofaccount
        withopeningdebit/credit.Inthatcase,theauto-balanceispostpone
        untilthewholefilehasbeenimported.
        """
        rslt=super(AccountAccount,self).load(fields,data)

        if'import_file'inself.env.context:
            companies=self.search([('id','in',rslt['ids'])]).mapped('company_id')
            forcompanyincompanies:
                company._auto_balance_opening_move()
        returnrslt

    def_toggle_reconcile_to_true(self):
        '''Togglethe`reconcile´booleanfromFalse->True

        Notethat:lineswithdebit=credit=amount_currency=0aresetto`reconciled´=True
        '''
        ifnotself.ids:
            returnNone
        query="""
            UPDATEaccount_move_lineSET
                reconciled=CASEWHENdebit=0ANDcredit=0ANDamount_currency=0
                    THENtrueELSEfalseEND,
                amount_residual=(debit-credit),
                amount_residual_currency=amount_currency
            WHEREfull_reconcile_idISNULLandaccount_idIN%s
        """
        self.env.cr.execute(query,[tuple(self.ids)])

    def_toggle_reconcile_to_false(self):
        '''Togglethe`reconcile´booleanfromTrue->False

        Notethatitisdisallowedifsomelinesarepartiallyreconciled.
        '''
        ifnotself.ids:
            returnNone
        partial_lines_count=self.env['account.move.line'].search_count([
            ('account_id','in',self.ids),
            ('full_reconcile_id','=',False),
            ('|'),
            ('matched_debit_ids','!=',False),
            ('matched_credit_ids','!=',False),
        ])
        ifpartial_lines_count>0:
            raiseUserError(_('Youcannotswitchanaccounttopreventthereconciliation'
                              'ifsomepartialreconciliationsarestillpending.'))
        query="""
            UPDATEaccount_move_line
                SETamount_residual=0,amount_residual_currency=0
            WHEREfull_reconcile_idISNULLANDaccount_idIN%s
        """
        self.env.cr.execute(query,[tuple(self.ids)])

    defwrite(self,vals):
        #Donotallowchangingthecompany_idwhenaccount_move_linealreadyexist
        ifvals.get('company_id',False):
            move_lines=self.env['account.move.line'].search([('account_id','in',self.ids)],limit=1)
            foraccountinself:
                if(account.company_id.id!=vals['company_id'])andmove_lines:
                    raiseUserError(_('Youcannotchangetheownercompanyofanaccountthatalreadycontainsjournalitems.'))
        if'reconcile'invals:
            ifvals['reconcile']:
                self.filtered(lambdar:notr.reconcile)._toggle_reconcile_to_true()
            else:
                self.filtered(lambdar:r.reconcile)._toggle_reconcile_to_false()

        ifvals.get('currency_id'):
            foraccountinself:
                ifself.env['account.move.line'].search_count([('account_id','=',account.id),('currency_id','notin',(False,vals['currency_id']))]):
                    raiseUserError(_('Youcannotsetacurrencyonthisaccountasitalreadyhassomejournalentrieshavingadifferentforeigncurrency.'))

        returnsuper(AccountAccount,self).write(vals)

    defunlink(self):
        ifself.env['account.move.line'].search([('account_id','in',self.ids)],limit=1):
            raiseUserError(_('Youcannotperformthisactiononanaccountthatcontainsjournalitems.'))
        #CheckingwhethertheaccountissetasapropertytoanyPartnerornot
        values=['account.account,%s'%(account_id,)foraccount_idinself.ids]
        partner_prop_acc=self.env['ir.property'].sudo().search([('value_reference','in',values)],limit=1)
        ifpartner_prop_acc:
            account_name=partner_prop_acc.get_by_record().display_name
            raiseUserError(
                _('Youcannotremove/deactivatetheaccount%swhichissetonacustomerorvendor.',account_name)
            )
        returnsuper(AccountAccount,self).unlink()

    defaction_read_account(self):
        self.ensure_one()
        return{
            'name':self.display_name,
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'account.account',
            'res_id':self.id,
        }

    defaction_duplicate_accounts(self):
        foraccountinself.browse(self.env.context['active_ids']):
            account.copy()


classAccountGroup(models.Model):
    _name="account.group"
    _description='AccountGroup'
    _parent_store=True
    _order='code_prefix_start'

    parent_id=fields.Many2one('account.group',index=True,ondelete='cascade',readonly=True)
    parent_path=fields.Char(index=True)
    name=fields.Char(required=True)
    code_prefix_start=fields.Char()
    code_prefix_end=fields.Char()
    company_id=fields.Many2one('res.company',required=True,readonly=True,default=lambdaself:self.env.company)

    _sql_constraints=[
        (
            'check_length_prefix',
            'CHECK(char_length(COALESCE(code_prefix_start,\'\'))=char_length(COALESCE(code_prefix_end,\'\')))',
            'Thelengthofthestartingandtheendingcodeprefixmustbethesame'
        ),
    ]

    @api.onchange('code_prefix_start')
    def_onchange_code_prefix_start(self):
        ifnotself.code_prefix_endorself.code_prefix_end<self.code_prefix_start:
            self.code_prefix_end=self.code_prefix_start

    @api.onchange('code_prefix_end')
    def_onchange_code_prefix_end(self):
        ifnotself.code_prefix_startorself.code_prefix_start>self.code_prefix_end:
            self.code_prefix_start=self.code_prefix_end

    defname_get(self):
        result=[]
        forgroupinself:
            prefix=group.code_prefix_startandstr(group.code_prefix_start)
            ifprefixandgroup.code_prefix_end!=group.code_prefix_start:
                prefix+='-'+str(group.code_prefix_end)
            name=(prefixand(prefix+'')or'')+group.name
            result.append((group.id,name))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        else:
            criteria_operator=['|']ifoperatornotinexpression.NEGATIVE_TERM_OPERATORSelse['&','!']
            domain=criteria_operator+[('code_prefix_start','=ilike',name+'%'),('name',operator,name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    @api.constrains('code_prefix_start','code_prefix_end')
    def_constraint_prefix_overlap(self):
        self.env['account.group'].flush()
        query="""
            SELECTother.idFROMaccount_groupthis
            JOINaccount_groupother
              ONchar_length(other.code_prefix_start)=char_length(this.code_prefix_start)
             ANDother.id!=this.id
             ANDother.company_id=this.company_id
             AND(
                other.code_prefix_start<=this.code_prefix_startANDthis.code_prefix_start<=other.code_prefix_end
                OR
                other.code_prefix_start>=this.code_prefix_startANDthis.code_prefix_end>=other.code_prefix_start
            )
            WHEREthis.idIN%(ids)s
        """
        self.env.cr.execute(query,{'ids':tuple(self.ids)})
        res=self.env.cr.fetchall()
        ifres:
            raiseValidationError(_('AccountGroupswiththesamegranularitycan\'toverlap'))

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            if'code_prefix_start'invalsandnotvals.get('code_prefix_end'):
                vals['code_prefix_end']=vals['code_prefix_start']
        res_ids=super(AccountGroup,self).create(vals_list)
        res_ids._adapt_accounts_for_account_groups()
        res_ids._adapt_parent_account_group()
        returnres_ids

    defwrite(self,vals):
        res=super(AccountGroup,self).write(vals)
        if'code_prefix_start'invalsor'code_prefix_end'invals:
            self._adapt_accounts_for_account_groups()
            self._adapt_parent_account_group()
        returnres

    defunlink(self):
        forrecordinself:
            account_ids=self.env['account.account'].search([('group_id','=',record.id)])
            account_ids.write({'group_id':record.parent_id.id})

            children_ids=self.env['account.group'].search([('parent_id','=',record.id)])
            children_ids.write({'parent_id':record.parent_id.id})
        super(AccountGroup,self).unlink()

    def_adapt_accounts_for_account_groups(self,account_ids=None):
        """Ensureconsistencybetweenaccountsandaccountgroups.

        Findandsetthemostspecificgroupmatchingthecodeoftheaccount.
        Themostspecificistheonewiththelongestprefixesandwiththestarting
        prefixbeingsmallerthantheaccountcodeandtheendingprefixbeinggreater.
        """
        company_ids=account_ids.company_id.idsifaccount_idselseself.company_id.ids
        account_ids=account_ids.idsifaccount_idselse[]
        ifnotcompany_idsandnotaccount_ids:
            return
        self.env['account.group'].flush(self.env['account.group']._fields)
        self.env['account.account'].flush(self.env['account.account']._fields)

        account_where_clause=''
        where_params=[tuple(company_ids)]
        ifaccount_ids:
            account_where_clause='ANDaccount.idIN%s'
            where_params.append(tuple(account_ids))

        self._cr.execute(f'''
            WITHcandidates_account_groupsAS(
                SELECT
                    account.idASaccount_id,
                    ARRAY_AGG(agroup.idORDERBYchar_length(agroup.code_prefix_start)DESC,agroup.id)ASgroup_ids
                FROMaccount_accountaccount
                LEFTJOINaccount_groupagroup
                    ONagroup.code_prefix_start<=LEFT(account.code,char_length(agroup.code_prefix_start))
                    ANDagroup.code_prefix_end>=LEFT(account.code,char_length(agroup.code_prefix_end))
                    ANDagroup.company_id=account.company_id
                WHEREaccount.company_idIN%s{account_where_clause}
                GROUPBYaccount.id
            )
            UPDATEaccount_account
            SETgroup_id=rel.group_ids[1]
            FROMcandidates_account_groupsrel
            WHEREaccount_account.id=rel.account_id
        ''',where_params)
        self.env['account.account'].invalidate_cache(fnames=['group_id'])

    def_adapt_parent_account_group(self):
        """Ensureconsistencyofthehierarchyofaccountgroups.

        Findandsetthemostspecificparentforeachgroup.
        Themostspecificistheonewiththelongestprefixesandwiththestarting
        prefixbeingsmallerthanthechildprefixesandtheendingprefixbeinggreater.
        """
        ifnotself:
            return
        self.env['account.group'].flush(self.env['account.group']._fields)
        query="""
            WITHrelationAS(
       SELECTDISTINCTFIRST_VALUE(parent.id)OVER(PARTITIONBYchild.idORDERBYchild.id,char_length(parent.code_prefix_start)DESC)ASparent_id,
                       child.idASchild_id
                  FROMaccount_groupparent
                  JOINaccount_groupchild
                    ONchar_length(parent.code_prefix_start)<char_length(child.code_prefix_start)
                   ANDparent.code_prefix_start<=LEFT(child.code_prefix_start,char_length(parent.code_prefix_start))
                   ANDparent.code_prefix_end>=LEFT(child.code_prefix_end,char_length(parent.code_prefix_end))
                   ANDparent.id!=child.id
                   ANDparent.company_id=child.company_id
                 WHEREchild.company_idIN%(company_ids)s
            )
            UPDATEaccount_groupchild
               SETparent_id=relation.parent_id
              FROMrelation
             WHEREchild.id=relation.child_id;
        """
        self.env.cr.execute(query,{'company_ids':tuple(self.company_id.ids)})
        self.env['account.group'].invalidate_cache(fnames=['parent_id'])
        self.env['account.group'].search([('company_id','in',self.company_id.ids)])._parent_store_update()


classAccountRoot(models.Model):
    _name='account.root'
    _description='Accountcodesfirst2digits'
    _auto=False

    name=fields.Char()
    parent_id=fields.Many2one('account.root')
    company_id=fields.Many2one('res.company')

    definit(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute('''
            CREATEORREPLACEVIEW%sAS(
            SELECTDISTINCTASCII(code)*1000+ASCII(SUBSTRING(code,2,1))ASid,
                   LEFT(code,2)ASname,
                   ASCII(code)ASparent_id,
                   company_id
            FROMaccount_accountWHEREcodeISNOTNULL
            UNIONALL
            SELECTDISTINCTASCII(code)ASid,
                   LEFT(code,1)ASname,
                   NULL::intASparent_id,
                   company_id
            FROMaccount_accountWHEREcodeISNOTNULL
            )'''%(self._table,)
        )
