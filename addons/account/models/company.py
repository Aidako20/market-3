#-*-coding:utf-8-*-

fromdatetimeimporttimedelta,datetime,date
importcalendar
fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.account.models.account_moveimportMAX_HASH_VERSION
fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError,UserError,RedirectWarning
fromflectra.tools.miscimportformat_date
fromflectra.tools.float_utilsimportfloat_round,float_is_zero
fromflectra.tests.commonimportForm


MONTH_SELECTION=[
    ('1','January'),
    ('2','February'),
    ('3','March'),
    ('4','April'),
    ('5','May'),
    ('6','June'),
    ('7','July'),
    ('8','August'),
    ('9','September'),
    ('10','October'),
    ('11','November'),
    ('12','December'),
]

ONBOARDING_STEP_STATES=[
    ('not_done',"Notdone"),
    ('just_done',"Justdone"),
    ('done',"Done"),
]
DASHBOARD_ONBOARDING_STATES=ONBOARDING_STEP_STATES+[('closed','Closed')]


classResCompany(models.Model):
    _inherit="res.company"

    #TODOcheckalltheoptions/fieldsareintheviews(settings+companyformview)
    fiscalyear_last_day=fields.Integer(default=31,required=True)
    fiscalyear_last_month=fields.Selection(MONTH_SELECTION,default='12',required=True)
    period_lock_date=fields.Date(string="LockDateforNon-Advisers",help="Onlyuserswiththe'Adviser'rolecaneditaccountspriortoandinclusiveofthisdate.Useitforperiodlockinginsideanopenfiscalyear,forexample.")
    fiscalyear_lock_date=fields.Date(string="LockDate",help="Nousers,includingAdvisers,caneditaccountspriortoandinclusiveofthisdate.Useitforfiscalyearlockingforexample.")
    tax_lock_date=fields.Date("TaxLockDate",help="Nouserscaneditjournalentriesrelatedtoataxpriorandinclusiveofthisdate.")
    transfer_account_id=fields.Many2one('account.account',
        domain=lambdaself:[('reconcile','=',True),('user_type_id.id','=',self.env.ref('account.data_account_type_current_assets').id),('deprecated','=',False)],string="Inter-BanksTransferAccount",help="Intermediaryaccountusedwhenmovingmoneyfromaliquidityaccounttoanother")
    expects_chart_of_accounts=fields.Boolean(string='ExpectsaChartofAccounts',default=True)
    chart_template_id=fields.Many2one('account.chart.template',help='Thecharttemplateforthecompany(ifany)')
    bank_account_code_prefix=fields.Char(string='Prefixofthebankaccounts')
    cash_account_code_prefix=fields.Char(string='Prefixofthecashaccounts')
    default_cash_difference_income_account_id=fields.Many2one('account.account',string="CashDifferenceIncomeAccount")
    default_cash_difference_expense_account_id=fields.Many2one('account.account',string="CashDifferenceExpenseAccount")
    account_journal_suspense_account_id=fields.Many2one('account.account',string='JournalSuspenseAccount')
    transfer_account_code_prefix=fields.Char(string='Prefixofthetransferaccounts')
    account_sale_tax_id=fields.Many2one('account.tax',string="DefaultSaleTax")
    account_purchase_tax_id=fields.Many2one('account.tax',string="DefaultPurchaseTax")
    tax_calculation_rounding_method=fields.Selection([
        ('round_per_line','RoundperLine'),
        ('round_globally','RoundGlobally'),
        ],default='round_per_line',string='TaxCalculationRoundingMethod')
    currency_exchange_journal_id=fields.Many2one('account.journal',string="ExchangeGainorLossJournal",domain=[('type','=','general')])
    income_currency_exchange_account_id=fields.Many2one(
        comodel_name='account.account',
        string="GainExchangeRateAccount",
        domain=lambdaself:"[('internal_type','=','other'),('deprecated','=',False),('company_id','=',id),\
                             ('user_type_id','in',%s)]"%[self.env.ref('account.data_account_type_revenue').id,
                                                             self.env.ref('account.data_account_type_other_income').id])
    expense_currency_exchange_account_id=fields.Many2one(
        comodel_name='account.account',
        string="LossExchangeRateAccount",
        domain=lambdaself:"[('internal_type','=','other'),('deprecated','=',False),('company_id','=',id),\
                             ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_expenses').id)
    anglo_saxon_accounting=fields.Boolean(string="Useanglo-saxonaccounting")
    property_stock_account_input_categ_id=fields.Many2one('account.account',string="InputAccountforStockValuation")
    property_stock_account_output_categ_id=fields.Many2one('account.account',string="OutputAccountforStockValuation")
    property_stock_valuation_account_id=fields.Many2one('account.account',string="AccountTemplateforStockValuation")
    bank_journal_ids=fields.One2many('account.journal','company_id',domain=[('type','=','bank')],string='BankJournals')
    tax_exigibility=fields.Boolean(string='UseCashBasis')
    account_tax_fiscal_country_id=fields.Many2one('res.country',string="FiscalCountry",compute='compute_account_tax_fiscal_country',store=True,readonly=False,help="Thecountrytousethetaxreportsfromforthiscompany")

    incoterm_id=fields.Many2one('account.incoterms',string='Defaultincoterm',
        help='InternationalCommercialTermsareaseriesofpredefinedcommercialtermsusedininternationaltransactions.')

    qr_code=fields.Boolean(string='DisplayQR-codeoninvoices')

    invoice_is_email=fields.Boolean('Emailbydefault',default=True)
    invoice_is_print=fields.Boolean('Printbydefault',default=True)

    #Fieldsofthesetupstepforopeningmove
    account_opening_move_id=fields.Many2one(string='OpeningJournalEntry',comodel_name='account.move',help="Thejournalentrycontainingtheinitialbalanceofallthiscompany'saccounts.")
    account_opening_journal_id=fields.Many2one(string='OpeningJournal',comodel_name='account.journal',related='account_opening_move_id.journal_id',help="Journalwheretheopeningentryofthiscompany'saccountinghasbeenposted.",readonly=False)
    account_opening_date=fields.Date(string='OpeningEntry',default=lambdaself:fields.Date.context_today(self).replace(month=1,day=1),required=True,help="Thatisthedateoftheopeningentry.")

    #Fieldsmarkingthecompletionofasetupstep
    account_setup_bank_data_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardingbankdatastep",default='not_done')
    account_setup_fy_data_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardingfiscalyearstep",default='not_done')
    account_setup_coa_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardingchartsofaccountstep",default='not_done')
    account_onboarding_invoice_layout_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardinginvoicelayoutstep",default='not_done')
    account_onboarding_create_invoice_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardingcreateinvoicestep",default='not_done')
    account_onboarding_sale_tax_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardingsaletaxstep",default='not_done')

    #accountdashboardonboarding
    account_invoice_onboarding_state=fields.Selection(DASHBOARD_ONBOARDING_STATES,string="Stateoftheaccountinvoiceonboardingpanel",default='not_done')
    account_dashboard_onboarding_state=fields.Selection(DASHBOARD_ONBOARDING_STATES,string="Stateoftheaccountdashboardonboardingpanel",default='not_done')
    invoice_terms=fields.Text(string='DefaultTermsandConditions',translate=True)
    account_setup_bill_state=fields.Selection(ONBOARDING_STEP_STATES,string="Stateoftheonboardingbillstep",default='not_done')

    #NeededinthePointofSale
    account_default_pos_receivable_account_id=fields.Many2one('account.account',string="DefaultPoSReceivableAccount")

    #AccrualAccounting
    expense_accrual_account_id=fields.Many2one('account.account',
        help="Accountusedtomovetheperiodofanexpense",
        domain="[('internal_group','=','liability'),('internal_type','notin',('receivable','payable')),('company_id','=',id)]")
    revenue_accrual_account_id=fields.Many2one('account.account',
        help="Accountusedtomovetheperiodofarevenue",
        domain="[('internal_group','=','asset'),('internal_type','notin',('receivable','payable')),('company_id','=',id)]")
    automatic_entry_default_journal_id=fields.Many2one('account.journal',help="Journalusedbydefaultformovingtheperiodofanentry",domain="[('type','=','general')]")

    #Technicalfieldtohidecountryspecificfieldsincompanyformview
    country_code=fields.Char(related='country_id.code')

    #Cashbasistaxes
    tax_cash_basis_journal_id=fields.Many2one(
        comodel_name='account.journal',
        string="CashBasisJournal")
    account_cash_basis_base_account_id=fields.Many2one(
        comodel_name='account.account',
        domain=[('deprecated','=',False)],
        string="BaseTaxReceivedAccount",
        help="Accountthatwillbesetonlinescreatedincashbasisjournalentryandusedtokeeptrackofthe"
             "taxbaseamount.")

    @api.constrains('account_opening_move_id','fiscalyear_last_day','fiscalyear_last_month')
    def_check_fiscalyear_last_day(self):
        #iftheuserexplicitlychoosesthe29thofFebruaryweallowit:
        #thereisno"fiscalyear_last_year"sowedonotknowhisintentions.
        forrecinself:
            ifrec.fiscalyear_last_day==29andrec.fiscalyear_last_month=='2':
                continue

            ifrec.account_opening_date:
                year=rec.account_opening_date.year
            else:
                year=datetime.now().year

            max_day=calendar.monthrange(year,int(rec.fiscalyear_last_month))[1]
            ifrec.fiscalyear_last_day>max_day:
                raiseValidationError(_("Invalidfiscalyearlastday"))

    @api.depends('country_id')
    defcompute_account_tax_fiscal_country(self):
        forrecordinself:
            record.account_tax_fiscal_country_id=record.country_id

    defget_and_update_account_invoice_onboarding_state(self):
        """Thismethodiscalledonthecontrollerrenderingmethodandensuresthattheanimations
            aredisplayedonlyonetime."""
        returnself.get_and_update_onbarding_state(
            'account_invoice_onboarding_state',
            self.get_account_invoice_onboarding_steps_states_names()
        )

    #YTIFIXME:Defineonlyonemethodthatreturns{'account':[],'sale':[],...}
    defget_account_invoice_onboarding_steps_states_names(self):
        """Necessarytoadd/editstepsfromothermodules(paymentacquirerinthiscase)."""
        return[
            'base_onboarding_company_state',
            'account_onboarding_invoice_layout_state',
            'account_onboarding_create_invoice_state',
        ]

    defget_and_update_account_dashboard_onboarding_state(self):
        """Thismethodiscalledonthecontrollerrenderingmethodandensuresthattheanimations
            aredisplayedonlyonetime."""
        returnself.get_and_update_onbarding_state(
            'account_dashboard_onboarding_state',
            self.get_account_dashboard_onboarding_steps_states_names()
        )

    defget_account_dashboard_onboarding_steps_states_names(self):
        """Necessarytoadd/editstepsfromothermodules(account_winbooks_importinthiscase)."""
        return[
            'account_setup_bill_state',
            'account_setup_bank_data_state',
            'account_setup_fy_data_state',
            'account_setup_coa_state',
        ]

    defget_new_account_code(self,current_code,old_prefix,new_prefix):
        digits=len(current_code)
        returnnew_prefix+current_code.replace(old_prefix,'',1).lstrip('0').rjust(digits-len(new_prefix),'0')

    defreflect_code_prefix_change(self,old_code,new_code):
        accounts=self.env['account.account'].search([('code','like',old_code),('internal_type','=','liquidity'),
            ('company_id','=',self.id)],order='codeasc')
        foraccountinaccounts:
            ifaccount.code.startswith(old_code):
                account.write({'code':self.get_new_account_code(account.code,old_code,new_code)})

    def_validate_fiscalyear_lock(self,values):
        ifvalues.get('fiscalyear_lock_date'):

            draft_entries=self.env['account.move'].search([
                ('company_id','in',self.ids),
                ('state','=','draft'),
                ('date','<=',values['fiscalyear_lock_date'])])
            ifdraft_entries:
                error_msg=_('Therearestillunpostedentriesintheperiodyouwanttolock.Youshouldeitherpostordeletethem.')
                action_error={
                    'view_mode':'tree',
                    'name':_('UnpostedEntries'),
                    'res_model':'account.move',
                    'type':'ir.actions.act_window',
                    'domain':[('id','in',draft_entries.ids)],
                    'search_view_id':[self.env.ref('account.view_account_move_filter').id,'search'],
                    'views':[[self.env.ref('account.view_move_tree').id,'list'],[self.env.ref('account.view_move_form').id,'form']],
                }
                raiseRedirectWarning(error_msg,action_error,_('Showunpostedentries'))

            unreconciled_statement_lines=self.env['account.bank.statement.line'].search([
                ('company_id','in',self.ids),
                ('is_reconciled','=',False),
                ('date','<=',values['fiscalyear_lock_date']),
                ('move_id.state','in',('draft','posted')),
            ])
            ifunreconciled_statement_lines:
                error_msg=_("Therearestillunreconciledbankstatementlinesintheperiodyouwanttolock."
                            "Youshouldeitherreconcileordeletethem.")
                action_error={
                    'type':'ir.actions.client',
                    'tag':'bank_statement_reconciliation_view',
                    'context':{'statement_line_ids':unreconciled_statement_lines.ids,'company_ids':self.ids},
                }
                raiseRedirectWarning(error_msg,action_error,_('ShowUnreconciledBankStatementLine'))

    def_get_user_fiscal_lock_date(self):
        """Getthefiscallockdateforthiscompanydependingontheuser"""
        self.ensure_one()
        lock_date=max(self.period_lock_dateordate.min,self.fiscalyear_lock_dateordate.min)
        ifself.user_has_groups('account.group_account_manager'):
            lock_date=self.fiscalyear_lock_dateordate.min
        returnlock_date

    defwrite(self,values):
        #restricttheclosingofFYiftherearestillunpostedentries
        self._validate_fiscalyear_lock(values)

        #Reflectthechangeonaccounts
        forcompanyinself:
            ifvalues.get('bank_account_code_prefix'):
                new_bank_code=values.get('bank_account_code_prefix')orcompany.bank_account_code_prefix
                company.reflect_code_prefix_change(company.bank_account_code_prefix,new_bank_code)

            ifvalues.get('cash_account_code_prefix'):
                new_cash_code=values.get('cash_account_code_prefix')orcompany.cash_account_code_prefix
                company.reflect_code_prefix_change(company.cash_account_code_prefix,new_cash_code)

            #forbidthechangeofcurrency_idiftherearealreadysomeaccountingentriesexisting
            if'currency_id'invaluesandvalues['currency_id']!=company.currency_id.id:
                ifself.env['account.move.line'].search([('company_id','=',company.id)]):
                    raiseUserError(_('Youcannotchangethecurrencyofthecompanysincesomejournalitemsalreadyexist'))

        returnsuper(ResCompany,self).write(values)

    @api.model
    defsetting_init_bank_account_action(self):
        """Calledbythe'BankAccounts'buttonofthesetupbar."""
        view_id=self.env.ref('account.setup_bank_account_wizard').id
        return{'type':'ir.actions.act_window',
                'name':_('CreateaBankAccount'),
                'res_model':'account.setup.bank.manual.config',
                'target':'new',
                'view_mode':'form',
                'views':[[view_id,'form']],
        }

    @api.model
    defsetting_init_fiscal_year_action(self):
        """Calledbythe'FiscalYearOpening'buttonofthesetupbar."""
        company=self.env.company
        company.create_op_move_if_non_existant()
        new_wizard=self.env['account.financial.year.op'].create({'company_id':company.id})
        view_id=self.env.ref('account.setup_financial_year_opening_form').id

        return{
            'type':'ir.actions.act_window',
            'name':_('AccountingPeriods'),
            'view_mode':'form',
            'res_model':'account.financial.year.op',
            'target':'new',
            'res_id':new_wizard.id,
            'views':[[view_id,'form']],
        }

    @api.model
    defsetting_chart_of_accounts_action(self):
        """Calledbythe'ChartofAccounts'buttonofthesetupbar."""
        company=self.env.company
        company.sudo().set_onboarding_step_done('account_setup_coa_state')

        #Ifanopeningmovehasalreadybeenposted,weopenthetreeviewshowingalltheaccounts
        ifcompany.opening_move_posted():
            return'account.action_account_form'

        #Otherwise,wecreatetheopeningmove
        company.create_op_move_if_non_existant()

        #Then,weopenwillopenacustomtreeviewallowingtoeditopeningbalancesoftheaccount
        view_id=self.env.ref('account.init_accounts_tree').id
        #Hidethecurrentyearearningsaccountasitisautomaticallycomputed
        domain=[('user_type_id','!=',self.env.ref('account.data_unaffected_earnings').id),('company_id','=',company.id)]
        return{
            'type':'ir.actions.act_window',
            'name':_('ChartofAccounts'),
            'res_model':'account.account',
            'view_mode':'tree',
            'limit':99999999,
            'search_view_id':self.env.ref('account.view_account_search').id,
            'views':[[view_id,'list']],
            'domain':domain,
        }

    @api.model
    defcreate_op_move_if_non_existant(self):
        """Createsanemptyopeningmovein'draft'stateforthecurrentcompany
        iftherewasn'talreadyonedefined.Forthis,thefunctionneedsatleast
        onejournaloftype'general'toexist(requiredbyaccount.move).
        """
        self.ensure_one()
        ifnotself.account_opening_move_id:
            default_journal=self.env['account.journal'].search([('type','=','general'),('company_id','=',self.id)],limit=1)

            ifnotdefault_journal:
                raiseUserError(_("Pleaseinstallachartofaccountsorcreateamiscellaneousjournalbeforeproceeding."))

            opening_date=self.account_opening_date-timedelta(days=1)

            self.account_opening_move_id=self.env['account.move'].create({
                'ref':_('OpeningJournalEntry'),
                'company_id':self.id,
                'journal_id':default_journal.id,
                'date':opening_date,
            })

    defopening_move_posted(self):
        """Returnstrueifthiscompanyhasanopeningaccountmoveandthismoveisposted."""
        returnbool(self.account_opening_move_id)andself.account_opening_move_id.state=='posted'

    defget_unaffected_earnings_account(self):
        """Returnstheunaffectedearningsaccountforthiscompany,creatingone
        ifnonehasyetbeendefined.
        """
        unaffected_earnings_type=self.env.ref("account.data_unaffected_earnings")
        account=self.env['account.account'].search([('company_id','=',self.id),
                                                      ('user_type_id','=',unaffected_earnings_type.id)])
        ifaccount:
            returnaccount[0]
        #Donotassume'999999'doesn'texistsincetheusermighthavecreatedsuchanaccount
        #manually.
        code=999999
        whileself.env['account.account'].search([('code','=',str(code)),('company_id','=',self.id)]):
            code-=1
        returnself.env['account.account'].create({
                'code':str(code),
                'name':_('UndistributedProfits/Losses'),
                'user_type_id':unaffected_earnings_type.id,
                'company_id':self.id,
            })

    defget_opening_move_differences(self,opening_move_lines):
        currency=self.currency_id
        balancing_move_line=opening_move_lines.filtered(lambdax:x.account_id==self.get_unaffected_earnings_account())

        debits_sum=credits_sum=0.0
        forlineinopening_move_lines:
            ifline!=balancing_move_line:
                #skiptheautobalancingmoveline
                debits_sum+=line.debit
                credits_sum+=line.credit

        difference=abs(debits_sum-credits_sum)
        debit_diff=(debits_sum>credits_sum)andfloat_round(difference,precision_rounding=currency.rounding)or0.0
        credit_diff=(debits_sum<credits_sum)andfloat_round(difference,precision_rounding=currency.rounding)or0.0
        returndebit_diff,credit_diff

    def_auto_balance_opening_move(self):
        """Checkstheopening_moveofthiscompany.Ifithasnotbeenpostedyet
        andisunbalanced,balancesitwithaautomaticaccount.move.lineinthe
        currentyearearningsaccount.
        """
        ifself.account_opening_move_idandself.account_opening_move_id.state=='draft':
            balancing_account=self.get_unaffected_earnings_account()
            currency=self.currency_id

            balancing_move_line=self.account_opening_move_id.line_ids.filtered(lambdax:x.account_id==balancing_account)
            #Therecouldbemultiplelinesifweimportedthebalancefromunaffectedearningsaccounttoo
            iflen(balancing_move_line)>1:
                self.with_context(check_move_validity=False).account_opening_move_id.line_ids-=balancing_move_line[1:]
                balancing_move_line=balancing_move_line[0]

            debit_diff,credit_diff=self.get_opening_move_differences(self.account_opening_move_id.line_ids)

            iffloat_is_zero(debit_diff+credit_diff,precision_rounding=currency.rounding):
                ifbalancing_move_line:
                    #zerodifferenceandexistingline:deletetheline
                    self.account_opening_move_id.line_ids-=balancing_move_line
            else:
                ifbalancing_move_line:
                    #Non-zerodifferenceandexistingline:edittheline
                    balancing_move_line.write({'debit':credit_diff,'credit':debit_diff})
                else:
                    #Non-zerodifferenceandnoexistingline:createanewline
                    self.env['account.move.line'].create({
                        'name':_('AutomaticBalancingLine'),
                        'move_id':self.account_opening_move_id.id,
                        'account_id':balancing_account.id,
                        'debit':credit_diff,
                        'credit':debit_diff,
                    })

    @api.model
    defaction_close_account_invoice_onboarding(self):
        """Marktheinvoiceonboardingpanelasclosed."""
        self.env.company.account_invoice_onboarding_state='closed'

    @api.model
    defaction_close_account_dashboard_onboarding(self):
        """Markthedashboardonboardingpanelasclosed."""
        self.env.company.account_dashboard_onboarding_state='closed'

    @api.model
    defaction_open_account_onboarding_sale_tax(self):
        """Onboardingstepfortheinvoicelayout."""
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_open_account_onboarding_sale_tax")
        action['res_id']=self.env.company.id
        returnaction

    @api.model
    defaction_open_account_onboarding_create_invoice(self):
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_open_account_onboarding_create_invoice")
        returnaction

    defaction_save_onboarding_invoice_layout(self):
        """Settheonboardingstepasdone"""
        ifbool(self.external_report_layout_id):
            self.set_onboarding_step_done('account_onboarding_invoice_layout_state')

    defaction_save_onboarding_sale_tax(self):
        """Settheonboardingstepasdone"""
        self.set_onboarding_step_done('account_onboarding_sale_tax_state')

    defget_chart_of_accounts_or_fail(self):
        account=self.env['account.account'].search([('company_id','=',self.id)],limit=1)
        iflen(account)==0:
            action=self.env.ref('account.action_account_config')
            msg=_(
                "Wecannotfindachartofaccountsforthiscompany,youshouldconfigureit.\n"
                "PleasegotoAccountConfigurationandselectorinstallafiscallocalization.")
            raiseRedirectWarning(msg,action.id,_("Gototheconfigurationpanel"))
        returnaccount

    @api.model
    def_action_check_hash_integrity(self):
        returnself.env.ref('account.action_report_account_hash_integrity').report_action(self.id)

    def_check_hash_integrity(self):
        """Checksthatallpostedmoveshavestillthesamedataaswhentheywereposted
        andraisesanerrorwiththeresult.
        """
        ifnotself.env.user.has_group('account.group_account_user'):
            raiseUserError(_('PleasecontactyouraccountanttoprinttheHashintegrityresult.'))

        defbuild_move_info(move):
            return(move.name,move.inalterable_hash,fields.Date.to_string(move.date))

        journals=self.env['account.journal'].search([('company_id','=',self.id)])
        results_by_journal={
            'results':[],
            'printing_date':format_date(self.env,fields.Date.to_string(fields.Date.context_today(self)))
        }

        forjournalinjournals:
            rslt={
                'journal_name':journal.name,
                'journal_code':journal.code,
                'restricted_by_hash_table':journal.restrict_mode_hash_tableand'V'or'X',
                'msg_cover':'',
                'first_hash':'None',
                'first_move_name':'None',
                'first_move_date':'None',
                'last_hash':'None',
                'last_move_name':'None',
                'last_move_date':'None',
            }
            ifnotjournal.restrict_mode_hash_table:
                rslt.update({'msg_cover':_('Thisjournalisnotinstrictmode.')})
                results_by_journal['results'].append(rslt)
                continue

            #Weneedthe`sudo()`toensurethatallthemovesaresearched,nomattertheuser'saccessrights.
            #Thisisrequiredinordertogenerateconsistenthashs.
            #Itisnotanissue,sincethedataisonlyusedtocomputeahashandnottoreturntheactualvalues.
            all_moves_count=self.env['account.move'].sudo().search_count([('state','=','posted'),('journal_id','=',journal.id)])
            moves=self.env['account.move'].sudo().search([('state','=','posted'),('journal_id','=',journal.id),
                                            ('secure_sequence_number','!=',0)],order="secure_sequence_numberASC")
            ifnotmoves:
                rslt.update({
                    'msg_cover':_('Thereisn\'tanyjournalentryflaggedfordatainalterabilityyetforthisjournal.'),
                })
                results_by_journal['results'].append(rslt)
                continue

            previous_hash=u''
            start_move_info=[]
            hash_corrupted=False
            current_hash_version=1
            formoveinmoves:
                computed_hash=move.with_context(hash_version=current_hash_version)._compute_hash(previous_hash=previous_hash)
                whilemove.inalterable_hash!=computed_hashandcurrent_hash_version<MAX_HASH_VERSION:
                    current_hash_version+=1
                    computed_hash=move.with_context(hash_version=current_hash_version)._compute_hash(previous_hash=previous_hash)
                ifmove.inalterable_hash!=computed_hash:
                    rslt.update({'msg_cover':_('Corrupteddataonjournalentrywithid%s.',move.id)})
                    results_by_journal['results'].append(rslt)
                    hash_corrupted=True
                    break
                ifnotprevious_hash:
                    #savethedateandsequencenumberofthefirstmovehashed
                    start_move_info=build_move_info(move)
                previous_hash=move.inalterable_hash
            end_move_info=build_move_info(move)

            ifhash_corrupted:
                continue

            rslt.update({
                        'first_move_name':start_move_info[0],
                        'first_hash':start_move_info[1],
                        'first_move_date':format_date(self.env,start_move_info[2]),
                        'last_move_name':end_move_info[0],
                        'last_hash':end_move_info[1],
                        'last_move_date':format_date(self.env,end_move_info[2]),
                    })
            iflen(moves)==all_moves_count:
                rslt.update({'msg_cover':_('Allentriesarehashed.')})
            else:
                rslt.update({'msg_cover':_('Entriesarehashedfrom%s(%s)')%(start_move_info[0],format_date(self.env,start_move_info[2]))})
            results_by_journal['results'].append(rslt)

        returnresults_by_journal

    defcompute_fiscalyear_dates(self,current_date):
        """
        Theroleofthismethodistoprovideafallbackwhenaccount_accountingisnotinstalled.
        Asthefiscalyearisirrelevantwhenaccount_accountingisnotinstalled,thismethodreturnsthecalendaryear.
        :paramcurrent_date:Adatetime.date/datetime.datetimeobject.
        :return:Adictionarycontaining:
            *date_from
            *date_to
        """

        return{'date_from':datetime(year=current_date.year,month=1,day=1).date(),
                'date_to':datetime(year=current_date.year,month=12,day=31).date()}
