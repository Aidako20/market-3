#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.addons.base.models.res_bankimportsanitize_account_number
fromflectra.toolsimportremove_accents
importlogging
importre
importwarnings

_logger=logging.getLogger(__name__)


classAccountJournalGroup(models.Model):
    _name='account.journal.group'
    _description="AccountJournalGroup"
    _check_company_auto=True

    name=fields.Char("JournalGroup",required=True,translate=True)
    company_id=fields.Many2one('res.company',required=True,default=lambdaself:self.env.company)
    excluded_journal_ids=fields.Many2many('account.journal',string="ExcludedJournals",domain="[('company_id','=',company_id)]",
        check_company=True)
    sequence=fields.Integer(default=10)


classAccountJournal(models.Model):
    _name="account.journal"
    _description="Journal"
    _order='sequence,type,code'
    _inherit=['mail.thread','mail.activity.mixin']
    _check_company_auto=True

    def_default_inbound_payment_methods(self):
        returnself.env.ref('account.account_payment_method_manual_in')

    def_default_outbound_payment_methods(self):
        returnself.env.ref('account.account_payment_method_manual_out')

    def__get_bank_statements_available_sources(self):
        return[('undefined',_('UndefinedYet'))]

    def_get_bank_statements_available_sources(self):
        returnself.__get_bank_statements_available_sources()

    def_default_alias_domain(self):
        returnself.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")

    def_default_invoice_reference_model(self):
        """Gettheinvoicereferencemodelaccordingtothecompany'scountry."""
        country_code=self.env.company.country_id.code
        country_code=country_codeandcountry_code.lower()
        ifcountry_code:
            formodelinself._fields['invoice_reference_model'].get_values(self.env):
                ifmodel.startswith(country_code):
                    returnmodel
        return'flectra'

    name=fields.Char(string='JournalName',required=True)
    code=fields.Char(string='ShortCode',size=5,required=True,help="Shorternameusedfordisplay.Thejournalentriesofthisjournalwillalsobenamedusingthisprefixbydefault.")
    active=fields.Boolean(default=True,help="SetactivetofalsetohidetheJournalwithoutremovingit.")
    type=fields.Selection([
            ('sale','Sales'),
            ('purchase','Purchase'),
            ('cash','Cash'),
            ('bank','Bank'),
            ('general','Miscellaneous'),
        ],required=True,
        inverse='_inverse_type',
        help="Select'Sale'forcustomerinvoicesjournals.\n"\
        "Select'Purchase'forvendorbillsjournals.\n"\
        "Select'Cash'or'Bank'forjournalsthatareusedincustomerorvendorpayments.\n"\
        "Select'General'formiscellaneousoperationsjournals.")
    type_control_ids=fields.Many2many('account.account.type','journal_account_type_control_rel','journal_id','type_id',string='Allowedaccounttypes')
    account_control_ids=fields.Many2many('account.account','journal_account_control_rel','journal_id','account_id',string='Allowedaccounts',
        check_company=True,
        domain="[('deprecated','=',False),('company_id','=',company_id),('is_off_balance','=',False)]")
    default_account_type=fields.Many2one('account.account.type',compute="_compute_default_account_type")
    default_account_id=fields.Many2one(
        comodel_name='account.account',check_company=True,copy=False,ondelete='restrict',
        string='DefaultAccount',
        domain="[('deprecated','=',False),('company_id','=',company_id),"
               "'|',('user_type_id','=',default_account_type),('user_type_id','in',type_control_ids),"
               "('user_type_id.type','notin',('receivable','payable'))]")
    payment_debit_account_id=fields.Many2one(
        comodel_name='account.account',check_company=True,copy=False,ondelete='restrict',
        help="Incomingpaymentsentriestriggeredbyinvoices/refundswillbepostedontheOutstandingReceiptsAccount"
             "anddisplayedasbluelinesinthebankreconciliationwidget.Duringthereconciliationprocess,concerned"
             "transactionswillbereconciledwithentriesontheOutstandingReceiptsAccountinsteadofthe"
             "receivableaccount.",string='OutstandingReceiptsAccount',
        domain=lambdaself:"[('deprecated','=',False),('company_id','=',company_id),\
                             ('user_type_id.type','notin',('receivable','payable')),\
                             '|',('user_type_id','=',%s),('id','=',default_account_id)]"%self.env.ref('account.data_account_type_current_assets').id)
    payment_credit_account_id=fields.Many2one(
        comodel_name='account.account',check_company=True,copy=False,ondelete='restrict',
        help="Outgoingpaymentsentriestriggeredbybills/creditnoteswillbepostedontheOutstandingPaymentsAccount"
             "anddisplayedasbluelinesinthebankreconciliationwidget.Duringthereconciliationprocess,concerned"
             "transactionswillbereconciledwithentriesontheOutstandingPaymentsAccountinsteadofthe"
             "payableaccount.",string='OutstandingPaymentsAccount',
        domain=lambdaself:"[('deprecated','=',False),('company_id','=',company_id),\
                             ('user_type_id.type','notin',('receivable','payable')),\
                             '|',('user_type_id','=',%s),('id','=',default_account_id)]"%self.env.ref('account.data_account_type_current_assets').id)
    suspense_account_id=fields.Many2one(
        comodel_name='account.account',check_company=True,ondelete='restrict',readonly=False,store=True,
        compute='_compute_suspense_account_id',
        help="Bankstatementstransactionswillbepostedonthesuspenseaccountuntilthefinalreconciliation"
             "allowingfindingtherightaccount.",string='SuspenseAccount',
        domain=lambdaself:"[('deprecated','=',False),('company_id','=',company_id),\
                             ('user_type_id.type','notin',('receivable','payable')),\
                             ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_current_assets').id)
    restrict_mode_hash_table=fields.Boolean(string="LockPostedEntrieswithHash",
        help="Ifticked,theaccountingentryorinvoicereceivesahashassoonasitispostedandcannotbemodifiedanymore.")
    sequence=fields.Integer(help='UsedtoorderJournalsinthedashboardview',default=10)

    invoice_reference_type=fields.Selection(string='CommunicationType',required=True,selection=[('none','Free'),('partner','BasedonCustomer'),('invoice','BasedonInvoice')],default='invoice',help='Youcansetherethedefaultcommunicationthatwillappearoncustomerinvoices,oncevalidated,tohelpthecustomertorefertothatparticularinvoicewhenmakingthepayment.')
    invoice_reference_model=fields.Selection(string='CommunicationStandard',required=True,selection=[('flectra','Flectra'),('euro','European')],default=_default_invoice_reference_model,help="Youcanchoosedifferentmodelsforeachtypeofreference.ThedefaultoneistheFlectrareference.")

    #groups_id=fields.Many2many('res.groups','account_journal_group_rel','journal_id','group_id',string='Groups')
    currency_id=fields.Many2one('res.currency',help='Thecurrencyusedtoenterstatement',string="Currency")
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,index=True,default=lambdaself:self.env.company,
        help="Companyrelatedtothisjournal")
    country_code=fields.Char(related='company_id.country_id.code',readonly=True)

    refund_sequence=fields.Boolean(string='DedicatedCreditNoteSequence',help="Checkthisboxifyoudon'twanttosharethesamesequenceforinvoicesandcreditnotesmadefromthisjournal",default=False)
    sequence_override_regex=fields.Text(help="Technicalfieldusedtoenforcecomplexsequencecompositionthatthesystemwouldnormallymisunderstand.\n"\
                                          "Thisisaregexthatcanincludeallthefollowingcapturegroups:prefix1,year,prefix2,month,prefix3,seq,suffix.\n"\
                                          "Theprefix*groupsaretheseparatorsbetweentheyear,monthandtheactualincreasingsequencenumber(seq).\n"\

                                          "e.g:^(?P<prefix1>.*?)(?P<year>\d{4})(?P<prefix2>\D*?)(?P<month>\d{2})(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$")

    inbound_payment_method_ids=fields.Many2many(
        comodel_name='account.payment.method',
        relation='account_journal_inbound_payment_method_rel',
        column1='journal_id',
        column2='inbound_payment_method',
        domain=[('payment_type','=','inbound')],
        string='InboundPaymentMethods',
        compute='_compute_inbound_payment_method_ids',
        store=True,
        readonly=False,
        help="Manual:Getpaidbycash,checkoranyothermethodoutsideofFlectra.\n"
             "Electronic:Getpaidautomaticallythroughapaymentacquirerbyrequestingatransaction"
             "onacardsavedbythecustomerwhenbuyingorsubscribingonline(paymenttoken).\n"
             "BatchDeposit:Encaseseveralcustomerchecksatoncebygeneratingabatchdepositto"
             "submittoyourbank.WhenencodingthebankstatementinFlectra,youaresuggestedto"
             "reconcilethetransactionwiththebatchdeposit.Enablethisoptionfromthesettings."
    )
    outbound_payment_method_ids=fields.Many2many(
        comodel_name='account.payment.method',
        relation='account_journal_outbound_payment_method_rel',
        column1='journal_id',
        column2='outbound_payment_method',
        domain=[('payment_type','=','outbound')],
        string='OutboundPaymentMethods',
        compute='_compute_outbound_payment_method_ids',
        store=True,
        readonly=False,
        help="Manual:PaybillbycashoranyothermethodoutsideofFlectra.\n"
             "Check:PaybillbycheckandprintitfromFlectra.\n"
             "SEPACreditTransfer:PaybillfromaSEPACreditTransferfileyousubmittoyour"
             "bank.Enablethisoptionfromthesettings."
    )
    at_least_one_inbound=fields.Boolean(compute='_methods_compute',store=True)
    at_least_one_outbound=fields.Boolean(compute='_methods_compute',store=True)
    profit_account_id=fields.Many2one(
        comodel_name='account.account',check_company=True,
        help="Usedtoregisteraprofitwhentheendingbalanceofacashregisterdiffersfromwhatthesystemcomputes",
        string='ProfitAccount',
        domain=lambdaself:"[('deprecated','=',False),('company_id','=',company_id),\
                             ('user_type_id.type','notin',('receivable','payable')),\
                             ('user_type_id','in',%s)]"%[self.env.ref('account.data_account_type_revenue').id,
                                                             self.env.ref('account.data_account_type_other_income').id])
    loss_account_id=fields.Many2one(
        comodel_name='account.account',check_company=True,
        help="Usedtoregisteralosswhentheendingbalanceofacashregisterdiffersfromwhatthesystemcomputes",
        string='LossAccount',
        domain=lambdaself:"[('deprecated','=',False),('company_id','=',company_id),\
                             ('user_type_id.type','notin',('receivable','payable')),\
                             ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_expenses').id)

    #Bankjournalsfields
    company_partner_id=fields.Many2one('res.partner',related='company_id.partner_id',string='AccountHolder',readonly=True,store=False)
    bank_account_id=fields.Many2one('res.partner.bank',
        string="BankAccount",
        ondelete='restrict',copy=False,
        check_company=True,
        domain="[('partner_id','=',company_partner_id),'|',('company_id','=',False),('company_id','=',company_id)]")
    bank_statements_source=fields.Selection(selection=_get_bank_statements_available_sources,string='BankFeeds',default='undefined',help="Defineshowthebankstatementswillberegistered")
    bank_acc_number=fields.Char(related='bank_account_id.acc_number',readonly=False)
    bank_id=fields.Many2one('res.bank',related='bank_account_id.bank_id',readonly=False)

    #Salejournalsfields
    sale_activity_type_id=fields.Many2one('mail.activity.type',string='ScheduleActivity',default=False,help="Activitywillbeautomaticallyscheduledonpaymentduedate,improvingcollectionprocess.")
    sale_activity_user_id=fields.Many2one('res.users',string="ActivityUser",help="LeaveemptytoassigntheSalespersonoftheinvoice.")
    sale_activity_note=fields.Text('ActivitySummary')

    #aliasconfigurationforjournals
    alias_id=fields.Many2one('mail.alias',string='EmailAlias',help="Sendoneseparateemailforeachinvoice.\n\n"
                                                                  "Anyfileextensionwillbeaccepted.\n\n"
                                                                  "OnlyPDFandXMLfileswillbeinterpretedbyFlectra",copy=False)
    alias_domain=fields.Char('Aliasdomain',compute='_compute_alias_domain',default=_default_alias_domain,compute_sudo=True)
    alias_name=fields.Char('AliasName',copy=False,compute='_compute_alias_name',inverse='_inverse_type',help="Itcreatesdraftinvoicesandbillsbysendinganemail.",readonly=False)

    journal_group_ids=fields.Many2many('account.journal.group',
        domain="[('company_id','=',company_id)]",
        check_company=True,
        string="JournalGroups")

    secure_sequence_id=fields.Many2one('ir.sequence',
        help='Sequencetousetoensurethesecurisationofdata',
        check_company=True,
        readonly=True,copy=False)

    _sql_constraints=[
        ('code_company_uniq','unique(code,name,company_id)','Thecodeandnameofthejournalmustbeuniquepercompany!'),
    ]

    @api.depends('type')
    def_compute_default_account_type(self):
        default_account_id_types={
            'bank':'account.data_account_type_liquidity',
            'cash':'account.data_account_type_liquidity',
            'sale':'account.data_account_type_revenue',
            'purchase':'account.data_account_type_expenses'
        }

        forjournalinself:
            ifjournal.typeindefault_account_id_types:
                journal.default_account_type=self.env.ref(default_account_id_types[journal.type]).id
            else:
                journal.default_account_type=False

    @api.depends('type')
    def_compute_outbound_payment_method_ids(self):
        forjournalinself:
            ifjournal.typein('bank','cash'):
                journal.outbound_payment_method_ids=self._default_outbound_payment_methods()
            else:
                journal.outbound_payment_method_ids=False

    @api.depends('type')
    def_compute_inbound_payment_method_ids(self):
        forjournalinself:
            ifjournal.typein('bank','cash'):
                journal.inbound_payment_method_ids=self._default_inbound_payment_methods()
            else:
                journal.inbound_payment_method_ids=False

    @api.depends('company_id','type')
    def_compute_suspense_account_id(self):
        forjournalinself:
            ifjournal.typenotin('bank','cash'):
                journal.suspense_account_id=False
            elifjournal.suspense_account_id:
                journal.suspense_account_id=journal.suspense_account_id
            elifjournal.company_id.account_journal_suspense_account_id:
                journal.suspense_account_id=journal.company_id.account_journal_suspense_account_id
            else:
                journal.suspense_account_id=False

    def_inverse_type(self):
        forrecordinself:
            record._update_mail_alias()

    def_compute_alias_domain(self):
        alias_domain=self._default_alias_domain()
        forrecordinself:
            record.alias_domain=alias_domain

    @api.depends('alias_id')
    def_compute_alias_name(self):
        forrecordinself:
            record.alias_name=record.alias_id.alias_name

    @api.constrains('type_control_ids')
    def_constrains_type_control_ids(self):
        self.env['account.move.line'].flush(['account_id','journal_id'])
        self.flush(['type_control_ids'])
        self._cr.execute("""
            SELECTaml.id
            FROMaccount_move_lineaml
            WHEREaml.journal_idin(%s)
            ANDEXISTS(SELECT1FROMjournal_account_type_control_relrelWHERErel.journal_id=aml.journal_id)
            ANDNOTEXISTS(SELECT1FROMaccount_accountacc
                            JOINjournal_account_type_control_relrelONacc.user_type_id=rel.type_id
                            WHEREacc.id=aml.account_idANDrel.journal_id=aml.journal_id)
            ANDaml.display_typeISNULL
        """,tuple(self.ids))
        ifself._cr.fetchone():
            raiseValidationError(_('Somejournalitemsalreadyexistinthisjournalbutwithaccountsfromdifferenttypesthantheallowedones.'))

    @api.constrains('account_control_ids')
    def_constrains_account_control_ids(self):
        self.env['account.move.line'].flush(['account_id','journal_id'])
        self.flush(['account_control_ids'])
        self._cr.execute("""
            SELECTaml.id
            FROMaccount_move_lineaml
            WHEREaml.journal_idin(%s)
            ANDEXISTS(SELECT1FROMjournal_account_control_relrelWHERErel.journal_id=aml.journal_id)
            ANDNOTEXISTS(SELECT1FROMjournal_account_control_relrelWHERErel.account_id=aml.account_idANDrel.journal_id=aml.journal_id)
            ANDaml.display_typeISNULL
        """,tuple(self.ids))
        ifself._cr.fetchone():
            raiseValidationError(_('Somejournalitemsalreadyexistinthisjournalbutwithotheraccountsthantheallowedones.'))

    @api.constrains('type','bank_account_id')
    def_check_bank_account(self):
        forjournalinself:
            ifjournal.type=='bank'andjournal.bank_account_id:
                ifjournal.bank_account_id.company_idandjournal.bank_account_id.company_id!=journal.company_id:
                    raiseValidationError(_('Thebankaccountofabankjournalmustbelongtothesamecompany(%s).',journal.company_id.name))
                #Abankaccountcanbelongtoacustomer/supplier,inwhichcasetheirpartner_idisthecustomer/supplier.
                #Ortheyarepartofabankjournalandtheirpartner_idmustbethecompany'spartner_id.
                ifjournal.bank_account_id.partner_id!=journal.company_id.partner_id:
                    raiseValidationError(_('Theholderofajournal\'sbankaccountmustbethecompany(%s).',journal.company_id.name))

    @api.constrains('company_id')
    def_check_company_consistency(self):
        ifnotself:
            return

        self.flush(['company_id'])
        self._cr.execute('''
            SELECTmove.id
            FROMaccount_movemove
            JOINaccount_journaljournalONjournal.id=move.journal_id
            WHEREmove.journal_idIN%s
            ANDmove.company_id!=journal.company_id
        ''',[tuple(self.ids)])
        ifself._cr.fetchone():
            raiseUserError(_("Youcan'tchangethecompanyofyourjournalsincetherearesomejournalentrieslinkedtoit."))

    @api.constrains('type','default_account_id')
    def_check_type_default_account_id_type(self):
        forjournalinself:
            ifjournal.typein('sale','purchase')andjournal.default_account_id.user_type_id.typein('receivable','payable'):
                raiseValidationError(_("Thetypeofthejournal'sdefaultcredit/debitaccountshouldn'tbe'receivable'or'payable'."))

    @api.constrains('active')
    def_check_auto_post_draft_entries(self):
        #constraintshouldbetestedjustafterarchivingajournal,butshouldn'tberaisedwhenunarchivingajournalcontainingdraftentries
        forjournalinself.filtered(lambdaj:notj.active):
            pending_moves=self.env['account.move'].search([
                ('journal_id','=',journal.id),
                ('state','=','draft')
            ],limit=1)

            ifpending_moves:
                raiseValidationError(_("Youcannotarchiveajournalcontainingdraftjournalentries.\n\n"
                                        "Toproceed:\n"
                                        "1/clickonthetop-rightbutton'JournalEntries'fromthisjournalform\n"
                                        "2/thenfilteron'Draft'entries\n"
                                        "3/selectthemallandpostordeletethemthroughtheactionmenu"))

    @api.onchange('type')
    def_onchange_type(self):
        self.refund_sequence=self.typein('sale','purchase')

    def_get_alias_values(self,type,alias_name=None):
        """Thisfunctionverifiesthattheuser-givenmailalias(oritsfallback)doesn'tcontainnon-asciichars.
            Thefallbacksarethejournal'sname,code,ortype-thesearesuffixedwiththe
            company'snameorid(incasethecompany'snameisnotasciieither).
        """
        defget_company_suffix():
            ifself.company_id!=self.env.ref('base.main_company'):
                try:
                    remove_accents(self.company_id.name).encode('ascii')
                    return'-'+str(self.company_id.name)
                exceptUnicodeEncodeError:
                    return'-'+str(self.company_id.id)
            return''

        ifnotalias_name:
            alias_name=self.name
            alias_name+=get_company_suffix()
        try:
            remove_accents(alias_name).encode('ascii')
        exceptUnicodeEncodeError:
            try:
                remove_accents(self.code).encode('ascii')
                safe_alias_name=self.code
            exceptUnicodeEncodeError:
                safe_alias_name=self.type
            safe_alias_name+=get_company_suffix()
            _logger.warning("Cannotuse'%s'asemailalias,fallbackto'%s'",
                alias_name,safe_alias_name)
            alias_name=safe_alias_name
        return{
            'alias_defaults':{'move_type':type=='purchase'and'in_invoice'or'out_invoice','company_id':self.company_id.id,'journal_id':self.id},
            'alias_parent_thread_id':self.id,
            'alias_name':alias_name,
        }

    defunlink(self):
        bank_accounts=self.env['res.partner.bank'].browse()
        forbank_accountinself.mapped('bank_account_id'):
            accounts=self.search([('bank_account_id','=',bank_account.id)])
            ifaccounts<=self:
                bank_accounts+=bank_account
        self.mapped('alias_id').sudo().unlink()
        ret=super(AccountJournal,self).unlink()
        bank_accounts.unlink()
        returnret

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        default=dict(defaultor{})
        default.update(
            code=_("%s(copy)")%(self.codeor''),
            name=_("%s(copy)")%(self.nameor''))
        returnsuper(AccountJournal,self).copy(default)

    def_update_mail_alias(self,vals=None):
        ifvalsisnotNone:
            warnings.warn(
                '`vals`isadeprecatedargumentof`_update_mail_alias`',
                DeprecationWarning,
                stacklevel=2
            )
        self.ensure_one()
        ifself.typein('purchase','sale'):
            alias_values=self._get_alias_values(type=self.type,alias_name=self.alias_name)
            ifself.alias_id:
                self.alias_id.sudo().write(alias_values)
            else:
                alias_values['alias_model_id']=self.env['ir.model']._get('account.move').id
                alias_values['alias_parent_model_id']=self.env['ir.model']._get('account.journal').id
                self.alias_id=self.env['mail.alias'].sudo().create(alias_values)
        elifself.alias_id:
            self.alias_id.unlink()

    defwrite(self,vals):
        forjournalinself:
            company=journal.company_id
            if('company_id'invalsandjournal.company_id.id!=vals['company_id']):
                ifself.env['account.move'].search([('journal_id','=',journal.id)],limit=1):
                    raiseUserError(_('Thisjournalalreadycontainsitems,thereforeyoucannotmodifyitscompany.'))
                company=self.env['res.company'].browse(vals['company_id'])
                ifjournal.bank_account_id.company_idandjournal.bank_account_id.company_id!=company:
                    journal.bank_account_id.write({
                        'company_id':company.id,
                        'partner_id':company.partner_id.id,
                    })
            if'currency_id'invals:
                ifjournal.bank_account_id:
                    journal.bank_account_id.currency_id=vals['currency_id']
            if'bank_account_id'invals:
                ifnotvals.get('bank_account_id'):
                    raiseUserError(_('Youcannotremovethebankaccountfromthejournalonceset.'))
                else:
                    bank_account=self.env['res.partner.bank'].browse(vals['bank_account_id'])
                    ifbank_account.partner_id!=company.partner_id:
                        raiseUserError(_("Thepartnersofthejournal'scompanyandtherelatedbankaccountmismatch."))
            if'restrict_mode_hash_table'invalsandnotvals.get('restrict_mode_hash_table'):
                journal_entry=self.env['account.move'].sudo().search([('journal_id','=',self.id),('state','=','posted'),('secure_sequence_number','!=',0)],limit=1)
                ifjournal_entry:
                    field_string=self._fields['restrict_mode_hash_table'].get_description(self.env)['string']
                    raiseUserError(_("Youcannotmodifythefield%sofajournalthatalreadyhasaccountingentries.",field_string))
        result=super(AccountJournal,self).write(vals)

        #Ensuretheliquidityaccountsaresharingthesameforeigncurrency.
        if'currency_id'invals:
            forjournalinself.filtered(lambdajournal:journal.typein('bank','cash')):
                journal.default_account_id.currency_id=journal.currency_id

        #Createthebank_account_idifnecessary
        if'bank_acc_number'invals:
            forjournalinself.filtered(lambdar:r.type=='bank'andnotr.bank_account_id):
                journal.set_bank_account(vals.get('bank_acc_number'),vals.get('bank_id'))
        forrecordinself:
            ifrecord.restrict_mode_hash_tableandnotrecord.secure_sequence_id:
                record._create_secure_sequence(['secure_sequence_id'])

        returnresult

    @api.model
    defget_next_bank_cash_default_code(self,journal_type,company):
        journal_code_base=(journal_type=='cash'and'CSH'or'BNK')
        journals=self.env['account.journal'].search([('code','like',journal_code_base+'%'),('company_id','=',company.id)])
        fornuminrange(1,100):
            #journal_codehasamaximalsizeof5,hencewecanenforcetheboundarynum<100
            journal_code=journal_code_base+str(num)
            ifjournal_codenotinjournals.mapped('code'):
                returnjournal_code

    @api.model
    def_prepare_liquidity_account_vals(self,company,code,vals):
        return{
            'name':vals.get('name'),
            'code':code,
            'user_type_id':self.env.ref('account.data_account_type_liquidity').id,
            'currency_id':vals.get('currency_id'),
            'company_id':company.id,
        }

    @api.model
    def_fill_missing_values(self,vals):
        journal_type=vals.get('type')

        #'type'fieldisrequired.
        ifnotjournal_type:
            return

        #===Fillmissingcompany===
        company=self.env['res.company'].browse(vals['company_id'])ifvals.get('company_id')elseself.env.company
        vals['company_id']=company.id

        #Don'tgetthedigitson'chart_template_id'sincethecharttemplatecouldbeacustomone.
        random_account=self.env['account.account'].search([('company_id','=',company.id)],limit=1)
        digits=len(random_account.code)ifrandom_accountelse6

        liquidity_type=self.env.ref('account.data_account_type_liquidity')
        current_assets_type=self.env.ref('account.data_account_type_current_assets')

        ifjournal_typein('bank','cash'):
            has_liquidity_accounts=vals.get('default_account_id')
            has_payment_accounts=vals.get('payment_debit_account_id')orvals.get('payment_credit_account_id')
            has_profit_account=vals.get('profit_account_id')
            has_loss_account=vals.get('loss_account_id')

            ifjournal_type=='bank':
                liquidity_account_prefix=company.bank_account_code_prefixor''
            else:
                liquidity_account_prefix=company.cash_account_code_prefixorcompany.bank_account_code_prefixor''

            #===Fillmissingname===
            vals['name']=vals.get('name')orvals.get('bank_acc_number')

            #===Fillmissingcode===
            if'code'notinvals:
                vals['code']=self.get_next_bank_cash_default_code(journal_type,company)
                ifnotvals['code']:
                    raiseUserError(_("Cannotgenerateanunusedjournalcode.Pleasefillthe'Shortcode'field."))

            #===Fillmissingaccounts===
            ifnothas_liquidity_accounts:
                default_account_code=self.env['account.account']._search_new_account_code(company,digits,liquidity_account_prefix)
                default_account_vals=self._prepare_liquidity_account_vals(company,default_account_code,vals)
                vals['default_account_id']=self.env['account.account'].create(default_account_vals).id
            ifnothas_payment_accounts:
                vals['payment_debit_account_id']=self.env['account.account'].create({
                    'name':_("OutstandingReceipts"),
                    'code':self.env['account.account']._search_new_account_code(company,digits,liquidity_account_prefix),
                    'reconcile':True,
                    'user_type_id':current_assets_type.id,
                    'company_id':company.id,
                }).id
                vals['payment_credit_account_id']=self.env['account.account'].create({
                    'name':_("OutstandingPayments"),
                    'code':self.env['account.account']._search_new_account_code(company,digits,liquidity_account_prefix),
                    'reconcile':True,
                    'user_type_id':current_assets_type.id,
                    'company_id':company.id,
                }).id
            ifjournal_type=='cash'andnothas_profit_account:
                vals['profit_account_id']=company.default_cash_difference_income_account_id.id
            ifjournal_type=='cash'andnothas_loss_account:
                vals['loss_account_id']=company.default_cash_difference_expense_account_id.id

        #===Fillmissingrefund_sequence===
        if'refund_sequence'notinvals:
            vals['refund_sequence']=vals['type']in('sale','purchase')

    @api.model
    defcreate(self,vals):
        #OVERRIDE
        self._fill_missing_values(vals)

        journal=super(AccountJournal,self.with_context(mail_create_nolog=True)).create(vals)

        #Createthebank_account_idifnecessary
        ifjournal.type=='bank'andnotjournal.bank_account_idandvals.get('bank_acc_number'):
            journal.set_bank_account(vals.get('bank_acc_number'),vals.get('bank_id'))

        returnjournal

    defset_bank_account(self,acc_number,bank_id=None):
        """Createares.partner.bank(ifnotexists)andsetitasvalueofthefieldbank_account_id"""
        self.ensure_one()
        res_partner_bank=self.env['res.partner.bank'].search([('sanitized_acc_number','=',sanitize_account_number(acc_number)),
                                                                ('company_id','=',self.company_id.id)],limit=1)
        ifres_partner_bank:
            self.bank_account_id=res_partner_bank.id
        else:
            self.bank_account_id=self.env['res.partner.bank'].create({
                'acc_number':acc_number,
                'bank_id':bank_id,
                'company_id':self.company_id.id,
                'currency_id':self.currency_id.id,
                'partner_id':self.company_id.partner_id.id,
            }).id

    defname_get(self):
        res=[]
        forjournalinself:
            name=journal.name
            ifjournal.currency_idandjournal.currency_id!=journal.company_id.currency_id:
                name="%s(%s)"%(name,journal.currency_id.name)
            res+=[(journal.id,name)]
        returnres

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]

        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        else:
            connector='&'ifoperatorinexpression.NEGATIVE_TERM_OPERATORSelse'|'
            domain=[connector,('code',operator,name),('name',operator,name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    @api.depends('inbound_payment_method_ids','outbound_payment_method_ids')
    def_methods_compute(self):
        forjournalinself:
            journal.at_least_one_inbound=bool(len(journal.inbound_payment_method_ids))
            journal.at_least_one_outbound=bool(len(journal.outbound_payment_method_ids))

    defaction_configure_bank_journal(self):
        """Thisfunctioniscalledbythe"configure"buttonofbankjournals,
        visibleondashboardifnobankstatementsourcehasbeendefinedyet
        """
        #Wesimplycallthesetupbarfunction.
        returnself.env['res.company'].setting_init_bank_account_action()

    def_create_invoice_from_attachment(self,attachment_ids=None):
        """
        Createinvoicesfromtheattachments(forinstanceaFactur-XXMLfile)
        """
        attachments=self.env['ir.attachment'].browse(attachment_ids)
        ifnotattachments:
            raiseUserError(_("Noattachmentwasprovided"))

        invoices=self.env['account.move']
        forattachmentinattachments:
            decoders=self.env['account.move']._get_create_invoice_from_attachment_decoders()
            invoice=False
            fordecoderinsorted(decoders,key=lambdad:d[0]):
                invoice=decoder[1](attachment)
                ifinvoice:
                    break
            ifnotinvoice:
                invoice=self.env['account.move'].create({})
            invoice.with_context(no_new_invoice=True).message_post(attachment_ids=[attachment.id])
            attachment.write({'res_model':'account.move','res_id':invoice.id})
            invoices+=invoice
        returninvoices

    defcreate_invoice_from_attachment(self,attachment_ids=None):
        """
        Createinvoicesfromtheattachments(forinstanceaFactur-XXMLfile)
        andredirecttheusertothenewlycreatedinvoice(s).
        :paramattachment_ids:listofattachmentids
        :return:actiontoopenthecreatedinvoices
        """
        invoices=self._create_invoice_from_attachment(attachment_ids)
        action_vals={
            'name':_('GeneratedDocuments'),
            'domain':[('id','in',invoices.ids)],
            'res_model':'account.move',
            'views':[[False,"tree"],[False,"form"]],
            'type':'ir.actions.act_window',
            'context':self._context
        }
        iflen(invoices)==1:
            action_vals.update({'res_id':invoices[0].id,'view_mode':'form'})
        else:
            action_vals['view_mode']='tree,form'
        returnaction_vals

    def_create_invoice_from_single_attachment(self,attachment):
        """Createsaninvoiceandposttheattachment.Iftherelatedmodules
            areinstalled,itwilltriggerOCRortheimportfromtheEDI.
            DEPRECATED:usecreate_invoice_from_attachmentinstead

            :returns:thecreatedinvoice.
        """
        invoice_action=self.create_invoice_from_attachment(attachment.ids)
        returnself.env['account.move'].browse(invoice_action['res_id'])

    def_create_secure_sequence(self,sequence_fields):
        """Thisfunctioncreatesano_gapsequenceoneachjournalinselfthatwillensure
        auniquenumberisgiventoallpostedaccount.moveinsuchawaythatwecanalways
        findthepreviousmoveofajournalentryonaspecificjournal.
        """
        forjournalinself:
            vals_write={}
            forseq_fieldinsequence_fields:
                ifnotjournal[seq_field]:
                    vals={
                        'name':_('Securisationof%s-%s')%(seq_field,journal.name),
                        'code':'SECUR%s-%s'%(journal.id,seq_field),
                        'implementation':'no_gap',
                        'prefix':'',
                        'suffix':'',
                        'padding':0,
                        'company_id':journal.company_id.id}
                    seq=self.env['ir.sequence'].create(vals)
                    vals_write[seq_field]=seq.id
            ifvals_write:
                journal.write(vals_write)

    #-------------------------------------------------------------------------
    #REPORTINGMETHODS
    #-------------------------------------------------------------------------

    def_get_journal_bank_account_balance(self,domain=None):
        '''Getthebankbalanceofthecurrentjournalbyfilteringthejournalitemsusingthejournal'saccounts.

        /!\Thecurrentjournalisnotpartoftheapplieddomain.Thisistheexpectedbehaviorsinceweonlywant
        alogicbasedonaccounts.

        :paramdomain: Anadditionaldomaintobeappliedontheaccount.move.linemodel.
        :return:       Tuplehavingbalanceexpressedinjournal'scurrency
                        alongwiththetotalnumberofmovelineshavingthesameaccountasofthejournal'sdefaultaccount.
        '''
        self.ensure_one()
        self.env['account.move.line'].check_access_rights('read')

        ifnotself.default_account_id:
            return0.0,0

        domain=(domainor[])+[
            ('account_id','in',tuple(self.default_account_id.ids)),
            ('display_type','notin',('line_section','line_note')),
            ('parent_state','!=','cancel'),
        ]
        query=self.env['account.move.line']._where_calc(domain)
        tables,where_clause,where_params=query.get_sql()

        query='''
            SELECT
                COUNT(account_move_line.id)ASnb_lines,
                COALESCE(SUM(account_move_line.balance),0.0),
                COALESCE(SUM(account_move_line.amount_currency),0.0)
            FROM'''+tables+'''
            WHERE'''+where_clause+'''
        '''

        company_currency=self.company_id.currency_id
        journal_currency=self.currency_idifself.currency_idandself.currency_id!=company_currencyelseFalse

        self._cr.execute(query,where_params)
        nb_lines,balance,amount_currency=self._cr.fetchone()
        returnamount_currencyifjournal_currencyelsebalance,nb_lines

    def_get_journal_outstanding_payments_account_balance(self,domain=None,date=None):
        '''Gettheoutstandingpaymentsbalanceofthecurrentjournalbyfilteringthejournalitemsusingthe
        journal'saccounts.

        :paramdomain: Anadditionaldomaintobeappliedontheaccount.move.linemodel.
        :paramdate:   Thedatetobeusedwhenperformingthecurrencyconversions.
        :return:       Thebalanceexpressedinthejournal'scurrency.
        '''
        self.ensure_one()
        self.env['account.move.line'].check_access_rights('read')
        conversion_date=dateorfields.Date.context_today(self)

        accounts=self.payment_debit_account_id+self.payment_credit_account_id
        ifnotaccounts:
            return0.0,0

        #Allowusermanagingpaymentswithoutanystatementlines.
        #Inthatcase,theusermanagestransactionsonlyusingtheregisterpaymentwizard.
        ifself.default_account_idinaccounts:
            return0.0,0

        domain=(domainor[])+[
            ('account_id','in',tuple(accounts.ids)),
            ('display_type','notin',('line_section','line_note')),
            ('parent_state','!=','cancel'),
            ('reconciled','=',False),
            ('journal_id','=',self.id),
        ]
        query=self.env['account.move.line']._where_calc(domain)
        tables,where_clause,where_params=query.get_sql()

        self._cr.execute('''
            SELECT
                COUNT(account_move_line.id)ASnb_lines,
                account_move_line.currency_id,
                account.reconcileASis_account_reconcile,
                SUM(account_move_line.amount_residual)ASamount_residual,
                SUM(account_move_line.balance)ASbalance,
                SUM(account_move_line.amount_residual_currency)ASamount_residual_currency,
                SUM(account_move_line.amount_currency)ASamount_currency
            FROM'''+tables+'''
            JOINaccount_accountaccountONaccount.id=account_move_line.account_id
            WHERE'''+where_clause+'''
            GROUPBYaccount_move_line.currency_id,account.reconcile
        ''',where_params)

        company_currency=self.company_id.currency_id
        journal_currency=self.currency_idifself.currency_idandself.currency_id!=company_currencyelseFalse
        balance_currency=journal_currencyorcompany_currency

        total_balance=0.0
        nb_lines=0
        forresinself._cr.dictfetchall():
            nb_lines+=res['nb_lines']

            amount_currency=res['amount_residual_currency']ifres['is_account_reconcile']elseres['amount_currency']
            balance=res['amount_residual']ifres['is_account_reconcile']elseres['balance']

            ifres['currency_id']andjournal_currencyandres['currency_id']==journal_currency.id:
                total_balance+=amount_currency
            elifjournal_currency:
                total_balance+=company_currency._convert(balance,balance_currency,self.company_id,conversion_date)
            else:
                total_balance+=balance
        returntotal_balance,nb_lines

    def_get_last_bank_statement(self,domain=None):
        '''Retrievethelastbankstatementcreatedusingthisjournal.
        :paramdomain: Anadditionaldomaintobeappliedontheaccount.bank.statementmodel.
        :return:       Anaccount.bank.statementrecordoranemptyrecordset.
        '''
        self.ensure_one()
        last_statement_domain=(domainor[])+[('journal_id','=',self.id)]
        last_statement=self.env['account.bank.statement'].search(last_statement_domain,order='datedesc,iddesc',limit=1)
        returnlast_statement
