#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.addons.base.models.decimal_precisionimportDecimalPrecision
fromflectra.exceptionsimportRedirectWarning,UserError,ValidationError,AccessError
fromflectra.toolsimportfloat_compare,date_utils,email_split,email_re,float_is_zero
fromflectra.tools.miscimportformatLang,format_date,get_lang
fromflectra.osvimportexpression

fromdatetimeimportdate,timedelta
fromcollectionsimportdefaultdict
fromcontextlibimportcontextmanager
fromitertoolsimportzip_longest
fromhashlibimportsha256
fromjsonimportdumps
fromunittest.mockimportpatch

importast
importjson
importre
importwarnings

MAX_HASH_VERSION=2


defcalc_check_digits(number):
    """Calculatetheextradigitsthatshouldbeappendedtothenumbertomakeitavalidnumber.
    Source:python-stdnumiso7064.mod_97_10.calc_check_digits
    """
    number_base10=''.join(str(int(x,36))forxinnumber)
    checksum=int(number_base10)%97
    return'%02d'%((98-100*checksum)%97)


classAccountMove(models.Model):
    _name="account.move"
    _inherit=['portal.mixin','mail.thread','mail.activity.mixin','sequence.mixin']
    _description="JournalEntry"
    _order='datedesc,namedesc,iddesc'
    _mail_post_access='read'
    _check_company_auto=True
    _sequence_index="journal_id"

    definit(self):
        super().init()
        self.env.cr.execute("""
            CREATEINDEXIFNOTEXISTSaccount_move_to_check_idx
            ONaccount_move(journal_id)WHEREto_check=true;
            CREATEINDEXIFNOTEXISTSaccount_move_payment_idx
            ONaccount_move(journal_id,state,payment_state,move_type,date);
        """)

    @property
    def_sequence_monthly_regex(self):
        returnself.journal_id.sequence_override_regexorsuper()._sequence_monthly_regex

    @property
    def_sequence_yearly_regex(self):
        returnself.journal_id.sequence_override_regexorsuper()._sequence_yearly_regex

    @property
    def_sequence_fixed_regex(self):
        returnself.journal_id.sequence_override_regexorsuper()._sequence_fixed_regex

    @api.model
    def_search_default_journal(self,journal_types):
        company_id=self._context.get('default_company_id',self.env.company.id)
        domain=[('company_id','=',company_id),('type','in',journal_types)]

        journal=None
        ifself._context.get('default_currency_id'):
            currency_domain=domain+[('currency_id','=',self._context['default_currency_id'])]
            journal=self.env['account.journal'].search(currency_domain,limit=1)

        ifnotjournal:
            journal=self.env['account.journal'].search(domain,limit=1)

        ifnotjournal:
            company=self.env['res.company'].browse(company_id)

            error_msg=_(
                "Nojournalcouldbefoundincompany%(company_name)sforanyofthosetypes:%(journal_types)s",
                company_name=company.display_name,
                journal_types=','.join(journal_types),
            )
            raiseUserError(error_msg)

        returnjournal

    @api.model
    def_get_default_journal(self):
        '''Getthedefaultjournal.
        Itcouldeitherbepassedthroughthecontextusingthe'default_journal_id'keycontainingitsid,
        eitherbedeterminedbythedefaulttype.
        '''
        move_type=self._context.get('default_move_type','entry')
        ifmove_typeinself.get_sale_types(include_receipts=True):
            journal_types=['sale']
        elifmove_typeinself.get_purchase_types(include_receipts=True):
            journal_types=['purchase']
        else:
            journal_types=self._context.get('default_move_journal_types',['general'])

        ifself._context.get('default_journal_id'):
            journal=self.env['account.journal'].browse(self._context['default_journal_id'])

            ifmove_type!='entry'andjournal.typenotinjournal_types:
                raiseUserError(_(
                    "Cannotcreateaninvoiceoftype%(move_type)swithajournalhaving%(journal_type)sastype.",
                    move_type=move_type,
                    journal_type=journal.type,
                ))
        else:
            journal=self._search_default_journal(journal_types)

        returnjournal

    #TODOremoveinmaster
    @api.model
    def_get_default_invoice_date(self):
        warnings.warn("Method'_get_default_invoice_date()'isdeprecatedandhasbeenremoved.",DeprecationWarning)
        returnfields.Date.context_today(self)ifself._context.get('default_move_type','entry')inself.get_purchase_types(include_receipts=True)elseFalse

    @api.model
    def_get_default_currency(self):
        '''Getthedefaultcurrencyfromeitherthejournal,eitherthedefaultjournal'scompany.'''
        journal=self._get_default_journal()
        returnjournal.currency_idorjournal.company_id.currency_id

    @api.model
    def_get_default_invoice_incoterm(self):
        '''Getthedefaultincotermforinvoice.'''
        returnself.env.company.incoterm_id

    #====Businessfields====
    name=fields.Char(string='Number',copy=False,compute='_compute_name',readonly=False,store=True,index=True,tracking=True)
    highest_name=fields.Char(compute='_compute_highest_name')
    show_name_warning=fields.Boolean(store=False)
    date=fields.Date(
        string='Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft':[('readonly',False)]},
        copy=False,
        default=fields.Date.context_today
    )
    ref=fields.Char(string='Reference',copy=False,tracking=True)
    narration=fields.Text(string='TermsandConditions')
    state=fields.Selection(selection=[
            ('draft','Draft'),
            ('posted','Posted'),
            ('cancel','Cancelled'),
        ],string='Status',required=True,readonly=True,copy=False,tracking=True,
        default='draft')
    posted_before=fields.Boolean(help="Technicalfieldforknowingifthemovehasbeenpostedbefore",copy=False)
    move_type=fields.Selection(selection=[
            ('entry','JournalEntry'),
            ('out_invoice','CustomerInvoice'),
            ('out_refund','CustomerCreditNote'),
            ('in_invoice','VendorBill'),
            ('in_refund','VendorCreditNote'),
            ('out_receipt','SalesReceipt'),
            ('in_receipt','PurchaseReceipt'),
        ],string='Type',required=True,store=True,index=True,readonly=True,tracking=True,
        default="entry",change_default=True)
    type_name=fields.Char('TypeName',compute='_compute_type_name')
    to_check=fields.Boolean(string='ToCheck',default=False,
        help='Ifthischeckboxisticked,itmeansthattheuserwasnotsureofalltherelatedinformationatthetimeofthecreationofthemoveandthatthemoveneedstobecheckedagain.')
    journal_id=fields.Many2one('account.journal',string='Journal',required=True,readonly=True,
        states={'draft':[('readonly',False)]},
        check_company=True,domain="[('id','in',suitable_journal_ids)]",
        default=_get_default_journal)
    suitable_journal_ids=fields.Many2many('account.journal',compute='_compute_suitable_journal_ids')
    company_id=fields.Many2one(comodel_name='res.company',string='Company',
                                 store=True,readonly=True,
                                 compute='_compute_company_id')
    company_currency_id=fields.Many2one(string='CompanyCurrency',readonly=True,
        related='company_id.currency_id')
    currency_id=fields.Many2one('res.currency',store=True,readonly=True,tracking=True,required=True,
        states={'draft':[('readonly',False)]},
        string='Currency',
        default=_get_default_currency)
    line_ids=fields.One2many('account.move.line','move_id',string='JournalItems',copy=True,readonly=True,
        states={'draft':[('readonly',False)]})
    partner_id=fields.Many2one('res.partner',readonly=True,tracking=True,
        states={'draft':[('readonly',False)]},
        check_company=True,
        string='Partner',change_default=True,ondelete='restrict')
    commercial_partner_id=fields.Many2one('res.partner',string='CommercialEntity',store=True,readonly=True,
        compute='_compute_commercial_partner_id',ondelete='restrict')
    country_code=fields.Char(related='company_id.country_id.code',readonly=True)
    user_id=fields.Many2one(string='User',related='invoice_user_id',
        help='Technicalfieldusedtofitthegenericbehaviorinmailtemplates.')
    is_move_sent=fields.Boolean(
        readonly=True,
        default=False,
        copy=False,
        tracking=True,
        help="Itindicatesthattheinvoice/paymenthasbeensent.",
    )
    partner_bank_id=fields.Many2one('res.partner.bank',string='RecipientBank',
        compute="_compute_partner_bank_id",store=True,readonly=False,
        help='BankAccountNumbertowhichtheinvoicewillbepaid.ACompanybankaccountifthisisaCustomerInvoiceorVendorCreditNote,otherwiseaPartnerbankaccountnumber.',
        check_company=True)
    payment_reference=fields.Char(string='PaymentReference',index=True,copy=False,
        compute='_compute_payment_reference',store=True,readonly=False,
        help="Thepaymentreferencetosetonjournalitems.")
    payment_id=fields.Many2one(
        index=True,
        comodel_name='account.payment',
        string="Payment",copy=False,check_company=True)
    statement_line_id=fields.Many2one(
        comodel_name='account.bank.statement.line',
        string="StatementLine",copy=False,check_company=True)

    #===Amountfields===
    amount_untaxed=fields.Monetary(string='UntaxedAmount',store=True,readonly=True,tracking=True,
        compute='_compute_amount')
    amount_tax=fields.Monetary(string='Tax',store=True,readonly=True,
        compute='_compute_amount')
    amount_total=fields.Monetary(string='Total',store=True,readonly=True,
        compute='_compute_amount',
        inverse='_inverse_amount_total')
    amount_residual=fields.Monetary(string='AmountDue',store=True,
        compute='_compute_amount')
    amount_untaxed_signed=fields.Monetary(string='UntaxedAmountSigned',store=True,readonly=True,
        compute='_compute_amount',currency_field='company_currency_id')
    amount_tax_signed=fields.Monetary(string='TaxSigned',store=True,readonly=True,
        compute='_compute_amount',currency_field='company_currency_id')
    amount_total_signed=fields.Monetary(string='TotalSigned',store=True,readonly=True,
        compute='_compute_amount',currency_field='company_currency_id')
    amount_residual_signed=fields.Monetary(string='AmountDueSigned',store=True,
        compute='_compute_amount',currency_field='company_currency_id')
    amount_by_group=fields.Binary(string="Taxamountbygroup",
        compute='_compute_invoice_taxes_by_group',
        help='EditTaxamountsifyouencounterroundingissues.')
    payment_state=fields.Selection(selection=[
        ('not_paid','NotPaid'),
        ('in_payment','InPayment'),
        ('paid','Paid'),
        ('partial','PartiallyPaid'),
        ('reversed','Reversed'),
        ('invoicing_legacy','InvoicingAppLegacy')],
        string="PaymentStatus",store=True,readonly=True,copy=False,tracking=True,
        compute='_compute_amount')

    #====Cashbasisfeaturefields====
    tax_cash_basis_rec_id=fields.Many2one(
        'account.partial.reconcile',
        string='TaxCashBasisEntryof',
        help="Technicalfieldusedtokeeptrackofthetaxcashbasisreconciliation."
             "Thisisneededwhencancellingthesource:itwillposttheinversejournalentrytocancelthatparttoo.")
    tax_cash_basis_move_id=fields.Many2one(
        comodel_name='account.move',
        index=True,
        string="OriginTaxCashBasisEntry",
        help="Thejournalentryfromwhichthistaxcashbasisjournalentryhasbeencreated.")

    #====Auto-postfeaturefields====
    auto_post=fields.Boolean(string='PostAutomatically',default=False,copy=False,
        help='Ifthischeckboxisticked,thisentrywillbeautomaticallypostedatitsdate.')

    #====Reversefeaturefields====
    reversed_entry_id=fields.Many2one('account.move',string="Reversalof",readonly=True,copy=False,
        check_company=True,index=True)
    reversal_move_id=fields.One2many('account.move','reversed_entry_id')

    #=========================================================
    #Invoicerelatedfields
    #=========================================================

    #====Businessfields====
    fiscal_position_id=fields.Many2one('account.fiscal.position',string='FiscalPosition',readonly=True,
        states={'draft':[('readonly',False)]},
        check_company=True,
        domain="[('company_id','=',company_id)]",ondelete="restrict",
        help="Fiscalpositionsareusedtoadapttaxesandaccountsforparticularcustomersorsalesorders/invoices."
             "Thedefaultvaluecomesfromthecustomer.")
    invoice_user_id=fields.Many2one('res.users',copy=False,tracking=True,
        string='Salesperson',
        default=lambdaself:self.env.user)
    invoice_date=fields.Date(string='Invoice/BillDate',readonly=True,index=True,copy=False,
        states={'draft':[('readonly',False)]})
    invoice_date_due=fields.Date(string='DueDate',readonly=True,index=True,copy=False,
        states={'draft':[('readonly',False)]})
    invoice_origin=fields.Char(string='Origin',readonly=True,tracking=True,
        help="Thedocument(s)thatgeneratedtheinvoice.")
    invoice_payment_term_id=fields.Many2one('account.payment.term',string='PaymentTerms',
        check_company=True,
        readonly=True,states={'draft':[('readonly',False)]})
    #/!\invoice_line_idsisjustasubsetofline_ids.
    invoice_line_ids=fields.One2many('account.move.line','move_id',string='Invoicelines',
        copy=False,readonly=True,
        domain=[('exclude_from_invoice_tab','=',False)],
        states={'draft':[('readonly',False)]})
    invoice_incoterm_id=fields.Many2one('account.incoterms',string='Incoterm',
        default=_get_default_invoice_incoterm,
        help='InternationalCommercialTermsareaseriesofpredefinedcommercialtermsusedininternationaltransactions.')
    display_qr_code=fields.Boolean(string="DisplayQR-code",compute='_compute_display_qr_code')
    qr_code_method=fields.Selection(string="PaymentQR-code",copy=False,
        selection=lambdaself:self.env['res.partner.bank'].get_available_qr_methods_in_sequence(),
        help="TypeofQR-codetobegeneratedforthepaymentofthisinvoice,whenprintingit.Ifleftblank,thefirstavailableandusablemethodwillbeused.")

    #====Paymentwidgetfields====
    invoice_outstanding_credits_debits_widget=fields.Text(groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_to_reconcile_info')
    invoice_has_outstanding=fields.Boolean(groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_to_reconcile_info')
    invoice_payments_widget=fields.Text(groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_reconciled_info')

    #====Vendorbillfields====
    invoice_vendor_bill_id=fields.Many2one('account.move',store=False,
        check_company=True,
        string='VendorBill',
        help="Auto-completefromapastbill.")
    invoice_source_email=fields.Char(string='SourceEmail',tracking=True)
    invoice_partner_display_name=fields.Char(compute='_compute_invoice_partner_display_info',store=True)

    #====Cashroundingfields====
    invoice_cash_rounding_id=fields.Many2one('account.cash.rounding',string='CashRoundingMethod',
        readonly=True,states={'draft':[('readonly',False)]},
        help='Definesthesmallestcoinageofthecurrencythatcanbeusedtopaybycash.')

    #====Displaypurposefields====
    invoice_filter_type_domain=fields.Char(compute='_compute_invoice_filter_type_domain',
        help="Technicalfieldusedtohaveadynamicdomainonjournal/taxesintheformview.")
    bank_partner_id=fields.Many2one('res.partner',help='Technicalfieldtogetthedomainonthebank',compute='_compute_bank_partner_id')
    invoice_has_matching_suspense_amount=fields.Boolean(compute='_compute_has_matching_suspense_amount',
        groups='account.group_account_invoice,account.group_account_readonly',
        help="Technicalfieldusedtodisplayanalertoninvoicesifthereisatleastamatchingamountinanysupsenseaccount.")
    tax_lock_date_message=fields.Char(
        compute='_compute_tax_lock_date_message',
        help="Technicalfieldusedtodisplayamessagewhentheinvoice'saccountingdateispriorofthetaxlockdate.")
    #TechnicalfieldtohideReconciledEntriesstatbutton
    has_reconciled_entries=fields.Boolean(compute="_compute_has_reconciled_entries")
    show_reset_to_draft_button=fields.Boolean(compute='_compute_show_reset_to_draft_button')

    #====HashFields====
    restrict_mode_hash_table=fields.Boolean(related='journal_id.restrict_mode_hash_table')
    secure_sequence_number=fields.Integer(string="InalteralbilityNoGapSequence#",readonly=True,copy=False,index=True)
    inalterable_hash=fields.Char(string="InalterabilityHash",readonly=True,copy=False)
    string_to_hash=fields.Char(compute='_compute_string_to_hash',readonly=True)

    @api.model
    def_field_will_change(self,record,vals,field_name):
        iffield_namenotinvals:
            returnFalse
        field=record._fields[field_name]
        iffield.type=='many2one':
            returnrecord[field_name].id!=vals[field_name]
        iffield.type=='many2many':
            current_ids=set(record[field_name].ids)
            after_write_ids=set(record.new({field_name:vals[field_name]})[field_name].ids)
            returncurrent_ids!=after_write_ids
        iffield.type=='one2many':
            returnTrue
        iffield.type=='monetary'andrecord[field.currency_field]:
            returnnotrecord[field.currency_field].is_zero(record[field_name]-vals[field_name])
        iffield.type=='float':
            record_value=field.convert_to_cache(record[field_name],record)
            to_write_value=field.convert_to_cache(vals[field_name],record)
            returnrecord_value!=to_write_value
        returnrecord[field_name]!=vals[field_name]

    @api.model
    def_cleanup_write_orm_values(self,record,vals):
        cleaned_vals=dict(vals)
        forfield_name,valueinvals.items():
            ifnotself._field_will_change(record,vals,field_name):
                delcleaned_vals[field_name]
        returncleaned_vals

    #-------------------------------------------------------------------------
    #ONCHANGEMETHODS
    #-------------------------------------------------------------------------

    def_get_accounting_date(self,invoice_date,has_tax):
        """Getcorrectaccountingdateforpreviousperiods,takingtaxlockdateintoaccount.

        Whenregisteringaninvoiceinthepast,westillwantthesequencetobeincreasing.
        Wethentakethelastdayoftheperiod,dependingonthesequenceformat.
        Ifthereisataxlockdateandtherearetaxesinvolved,weregistertheinvoiceatthe
        lastdateofthefirstopenperiod.

        :paraminvoice_date(datetime.date):Theinvoicedate
        :paramhas_tax(bool):Iffanytaxesareinvolvedinthelinesoftheinvoice
        :return(datetime.date):
        """
        tax_lock_date=self.company_id.tax_lock_date
        today=fields.Date.today()
        ifinvoice_dateandtax_lock_dateandhas_taxandinvoice_date<=tax_lock_date:
            invoice_date=tax_lock_date+timedelta(days=1)

        ifself.is_sale_document(include_receipts=True):
            returninvoice_date
        else:
            highest_name=self.highest_nameorself._get_last_sequence(relaxed=True,lock=False)
            number_reset=self._deduce_sequence_number_reset(highest_name)
            ifnothighest_nameornumber_reset=='month':
                if(today.year,today.month)>(invoice_date.year,invoice_date.month):
                    returndate_utils.get_month(invoice_date)[1]
                else:
                    returnmax(invoice_date,today)
            elifnumber_reset=='year':
                iftoday.year>invoice_date.year:
                    returndate(invoice_date.year,12,31)
                else:
                    returnmax(invoice_date,today)
        returninvoice_date

    @api.onchange('invoice_date','highest_name','company_id')
    def_onchange_invoice_date(self):
        ifself.invoice_date:
            ifnotself.invoice_payment_term_idand(notself.invoice_date_dueorself.invoice_date_due<self.invoice_date):
                self.invoice_date_due=self.invoice_date

            has_tax=bool(self.line_ids.tax_idsorself.line_ids.tax_tag_ids)
            accounting_date=self._get_accounting_date(self.invoice_date,has_tax)
            ifaccounting_date!=self.date:
                self.date=accounting_date
                self._onchange_currency()
            else:
                self._onchange_recompute_dynamic_lines()

    @api.onchange('journal_id')
    def_onchange_journal(self):
        ifself.journal_idandself.journal_id.currency_id:
            new_currency=self.journal_id.currency_id
            ifnew_currency!=self.currency_id:
                self.currency_id=new_currency
                self._onchange_currency()
        ifself.state=='draft'andself._get_last_sequence(lock=False)andself.nameandself.name!='/':
            self.name='/'

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        self=self.with_company(self.journal_id.company_id)

        warning={}
        ifself.partner_id:
            rec_account=self.partner_id.property_account_receivable_id
            pay_account=self.partner_id.property_account_payable_id
            ifnotrec_accountandnotpay_account:
                action=self.env.ref('account.action_account_config')
                msg=_('Cannotfindachartofaccountsforthiscompany,Youshouldconfigureit.\nPleasegotoAccountConfiguration.')
                raiseRedirectWarning(msg,action.id,_('Gototheconfigurationpanel'))
            p=self.partner_id
            ifp.invoice_warn=='no-message'andp.parent_id:
                p=p.parent_id
            ifp.invoice_warnandp.invoice_warn!='no-message':
                #Blockifpartneronlyhaswarningbutparentcompanyisblocked
                ifp.invoice_warn!='block'andp.parent_idandp.parent_id.invoice_warn=='block':
                    p=p.parent_id
                warning={
                    'title':_("Warningfor%s",p.name),
                    'message':p.invoice_warn_msg
                }
                ifp.invoice_warn=='block':
                    self.partner_id=False
                    return{'warning':warning}

        ifself.is_sale_document(include_receipts=True)andself.partner_id:
            self.invoice_payment_term_id=self.partner_id.property_payment_term_idorself.invoice_payment_term_id
            new_term_account=self.partner_id.commercial_partner_id.property_account_receivable_id
            self.narration=self.company_id.with_context(lang=self.partner_id.langorself.env.lang).invoice_terms
        elifself.is_purchase_document(include_receipts=True)andself.partner_id:
            self.invoice_payment_term_id=self.partner_id.property_supplier_payment_term_idorself.invoice_payment_term_id
            new_term_account=self.partner_id.commercial_partner_id.property_account_payable_id
        else:
            new_term_account=None

        forlineinself.line_ids:
            line.partner_id=self.partner_id.commercial_partner_id

            ifnew_term_accountandline.account_id.user_type_id.typein('receivable','payable'):
                line.account_id=new_term_account

        self._compute_bank_partner_id()

        #Findthenewfiscalposition.
        delivery_partner_id=self._get_invoice_delivery_partner_id()
        self.fiscal_position_id=self.env['account.fiscal.position'].get_fiscal_position(
            self.partner_id.id,delivery_id=delivery_partner_id)
        self._recompute_dynamic_lines()
        ifwarning:
            return{'warning':warning}

    @api.onchange('date','currency_id')
    def_onchange_currency(self):
        currency=self.currency_idorself.company_id.currency_id

        ifself.is_invoice(include_receipts=True):
            forlineinself._get_lines_onchange_currency():
                line.currency_id=currency
                line._onchange_currency()
        else:
            forlineinself.line_ids:
                line._onchange_currency()

        self._recompute_dynamic_lines(recompute_tax_base_amount=True)

    @api.onchange('payment_reference')
    def_onchange_payment_reference(self):
        forlineinself.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable')):
            line.name=self.payment_referenceor''

    @api.onchange('invoice_vendor_bill_id')
    def_onchange_invoice_vendor_bill(self):
        ifself.invoice_vendor_bill_id:
            #Copyinvoicelines.
            forlineinself.invoice_vendor_bill_id.invoice_line_ids:
                copied_vals=line.copy_data()[0]
                copied_vals['move_id']=self.id
                new_line=self.env['account.move.line'].new(copied_vals)
                new_line.recompute_tax_line=True

            #Copypaymentterms.
            self.invoice_payment_term_id=self.invoice_vendor_bill_id.invoice_payment_term_id

            #Copycurrency.
            ifself.currency_id!=self.invoice_vendor_bill_id.currency_id:
                self.currency_id=self.invoice_vendor_bill_id.currency_id
                self._onchange_currency()

            #Reset
            self.invoice_vendor_bill_id=False
            self._recompute_dynamic_lines()

    @api.onchange('move_type')
    def_onchange_type(self):
        '''Onchangemadetofilterthepartnersdependingofthetype.'''
        ifself.is_sale_document(include_receipts=True):
            ifself.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms'):
                self.narration=self.company_id.invoice_termsorself.env.company.invoice_terms

    @api.onchange('invoice_line_ids')
    def_onchange_invoice_line_ids(self):
        current_invoice_lines=self.line_ids.filtered(lambdaline:notline.exclude_from_invoice_tab)
        others_lines=self.line_ids-current_invoice_lines
        ifothers_linesandcurrent_invoice_lines-self.invoice_line_ids:
            others_lines[0].recompute_tax_line=True
        self.line_ids=others_lines+self.invoice_line_ids
        self._onchange_recompute_dynamic_lines()

    @api.onchange('line_ids','invoice_payment_term_id','invoice_date_due','invoice_cash_rounding_id','invoice_vendor_bill_id')
    def_onchange_recompute_dynamic_lines(self):
        self._recompute_dynamic_lines()

    @api.model
    def_get_tax_grouping_key_from_tax_line(self,tax_line):
        '''Createthedictionarybasedonataxlinethatwillbeusedaskeytogrouptaxestogether.
        /!\Mustbeconsistentwith'_get_tax_grouping_key_from_base_line'.
        :paramtax_line:   Anaccount.move.linebeingataxline(with'tax_repartition_line_id'setthen).
        :return:           Adictionarycontainingallfieldsonwhichthetaxwillbegrouped.
        '''
        return{
            'tax_repartition_line_id':tax_line.tax_repartition_line_id.id,
            'account_id':tax_line.account_id.id,
            'currency_id':tax_line.currency_id.id,
            'analytic_tag_ids':[(6,0,tax_line.tax_line_id.analyticandtax_line.analytic_tag_ids.idsor[])],
            'analytic_account_id':tax_line.tax_line_id.analyticandtax_line.analytic_account_id.id,
            'tax_ids':[(6,0,tax_line.tax_ids.ids)],
            'tax_tag_ids':[(6,0,tax_line.tax_tag_ids.ids)],
            'partner_id':tax_line.partner_id.id,
        }

    @api.model
    def_get_tax_grouping_key_from_base_line(self,base_line,tax_vals):
        '''Createthedictionarybasedonabaselinethatwillbeusedaskeytogrouptaxestogether.
        /!\Mustbeconsistentwith'_get_tax_grouping_key_from_tax_line'.
        :parambase_line:  Anaccount.move.linebeingabaseline(thatcouldcontainssomethingin'tax_ids').
        :paramtax_vals:   Anelementofcompute_all(...)['taxes'].
        :return:           Adictionarycontainingallfieldsonwhichthetaxwillbegrouped.
        '''
        tax_repartition_line=self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
        account=base_line._get_default_tax_account(tax_repartition_line)orbase_line.account_id
        return{
            'tax_repartition_line_id':tax_vals['tax_repartition_line_id'],
            'account_id':account.id,
            'currency_id':base_line.currency_id.id,
            'analytic_tag_ids':[(6,0,tax_vals['analytic']andbase_line.analytic_tag_ids.idsor[])],
            'analytic_account_id':tax_vals['analytic']andbase_line.analytic_account_id.id,
            'tax_ids':[(6,0,tax_vals['tax_ids'])],
            'tax_tag_ids':[(6,0,tax_vals['tag_ids'])],
            'partner_id':base_line.partner_id.id,
        }

    def_get_tax_force_sign(self):
        """Thesignmustbeforcedtoanegativesignincasethebalanceisoncredit
            toavoidnegatiftaxesamount.
            Example-CustomerInvoice:
            FixedTax | unitprice |  discount  | amount_tax |amount_total|
            -------------------------------------------------------------------------
                0.67  |     115     |    100%    |   -0.67   |     0
            -------------------------------------------------------------------------"""
        self.ensure_one()
        return-1ifself.move_typein('out_invoice','in_refund','out_receipt')else1

    def_preprocess_taxes_map(self,taxes_map):
        """Usefulincasewewanttopre-processtaxes_map"""
        returntaxes_map

    def_recompute_tax_lines(self,recompute_tax_base_amount=False,tax_rep_lines_to_recompute=None):
        """Computethedynamictaxlinesofthejournalentry.

        :paramrecompute_tax_base_amount:Flagforcingonlytherecomputationofthe`tax_base_amount`field.
        """
        self.ensure_one()
        in_draft_mode=self!=self._origin

        def_serialize_tax_grouping_key(grouping_dict):
            '''Serializethedictionaryvaluestobeusedinthetaxes_map.
            :paramgrouping_dict:Thevaluesreturnedby'_get_tax_grouping_key_from_tax_line'or'_get_tax_grouping_key_from_base_line'.
            :return:Astringrepresentingthevalues.
            '''
            return'-'.join(str(v)forvingrouping_dict.values())

        def_compute_base_line_taxes(base_line):
            '''Computetaxesamountsbothincompanycurrency/foreigncurrencyastheratiobetween
            amount_currency&balancecouldnotbethesameastheexpectedcurrencyrate.
            The'amount_currency'valuewillbesetoncompute_all(...)['taxes']inmulti-currency.
            :parambase_line:  Theaccount.move.lineowningthetaxes.
            :return:           Theresultofthecompute_allmethod.
            '''
            move=base_line.move_id

            ifmove.is_invoice(include_receipts=True):
                handle_price_include=True
                sign=-1ifmove.is_inbound()else1
                quantity=base_line.quantity
                is_refund=move.move_typein('out_refund','in_refund')
                price_unit_wo_discount=sign*base_line.price_unit*(1-(base_line.discount/100.0))
            else:
                handle_price_include=False
                quantity=1.0
                tax_type=base_line.tax_ids[0].type_tax_useifbase_line.tax_idselseNone
                is_refund=(tax_type=='sale'andbase_line.debit)or(tax_type=='purchase'andbase_line.credit)
                price_unit_wo_discount=base_line.amount_currency

            balance_taxes_res=base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            ifmove.move_type=='entry':
                repartition_field=is_refundand'refund_repartition_line_ids'or'invoice_repartition_line_ids'
                repartition_tags=base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(lambdax:x.repartition_type=='base').tag_ids
                tags_need_inversion=self._tax_tags_need_inversion(move,is_refund,tax_type)
                iftags_need_inversion:
                    balance_taxes_res['base_tags']=base_line._revert_signed_tags(repartition_tags).ids
                    fortax_resinbalance_taxes_res['taxes']:
                        tax_res['tag_ids']=base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            returnbalance_taxes_res

        taxes_map={}

        #====Addtaxlines====
        to_remove=self.env['account.move.line']
        forlineinself.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict=self._get_tax_grouping_key_from_tax_line(line)
            grouping_key=_serialize_tax_grouping_key(grouping_dict)
            ifgrouping_keyintaxes_map:
                #Alinewiththesamekeydoesalreadyexist,weonlyneedone
                #tomodifyit;wehavetodropthisone.
                to_remove+=line
            else:
                taxes_map[grouping_key]={
                    'tax_line':line,
                    'amount':0.0,
                    'tax_base_amount':0.0,
                    'grouping_dict':False,
                }
        ifnotrecompute_tax_base_amount:
            self.line_ids-=to_remove

        #====Mountbaselines====
        forlineinself.line_ids.filtered(lambdaline:notline.tax_repartition_line_id):
            #Don'tcallcompute_allifthereisnotax.
            ifnotline.tax_ids:
                ifnotrecompute_tax_base_amount:
                    line.tax_tag_ids=[(5,0,0)]
                continue

            compute_all_vals=_compute_base_line_taxes(line)

            #Assigntagsonbaseline
            ifnotrecompute_tax_base_amount:
                line.tax_tag_ids=compute_all_vals['base_tags']or[(5,0,0)]

            tax_exigible=True
            fortax_valsincompute_all_vals['taxes']:
                grouping_dict=self._get_tax_grouping_key_from_base_line(line,tax_vals)
                grouping_key=_serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line=self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax=tax_repartition_line.invoice_tax_idortax_repartition_line.refund_tax_id

                iftax.tax_exigibility=='on_payment':
                    tax_exigible=False

                taxes_map_entry=taxes_map.setdefault(grouping_key,{
                    'tax_line':None,
                    'amount':0.0,
                    'tax_base_amount':0.0,
                    'grouping_dict':False,
                })
                taxes_map_entry['amount']+=tax_vals['amount']
                taxes_map_entry['tax_base_amount']+=self._get_base_amount_to_display(tax_vals['base'],tax_repartition_line,tax_vals['group'])
                taxes_map_entry['grouping_dict']=grouping_dict
            ifnotrecompute_tax_base_amount:
                line.tax_exigible=tax_exigible

        #====Pre-processtaxes_map====
        taxes_map=self._preprocess_taxes_map(taxes_map)

        #====Processtaxes_map====
        fortaxes_map_entryintaxes_map.values():
            #Thetaxlineisnolongerusedinanybaselines,dropit.
            iftaxes_map_entry['tax_line']andnottaxes_map_entry['grouping_dict']:
                ifnotrecompute_tax_base_amount:
                    self.line_ids-=taxes_map_entry['tax_line']
                continue

            currency=self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

            #Don'tcreatetaxlineswithzerobalance.
            ifcurrency.is_zero(taxes_map_entry['amount']):
                iftaxes_map_entry['tax_line']andnotrecompute_tax_base_amount:
                    self.line_ids-=taxes_map_entry['tax_line']
                continue

            #tax_base_amountfieldisexpressedusingthecompanycurrency.
            tax_base_amount=currency._convert(taxes_map_entry['tax_base_amount'],self.company_currency_id,self.company_id,self.dateorfields.Date.context_today(self))

            #Recomputeonlythetax_base_amount.
            ifrecompute_tax_base_amount:
                iftaxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount=tax_base_amount
                continue

            balance=currency._convert(
                taxes_map_entry['amount'],
                self.company_currency_id,
                self.company_id,
                self.dateorfields.Date.context_today(self),
            )
            amount_currency=currency.round(taxes_map_entry['amount'])
            sign=-1ifself.is_inbound()else1
            to_write_on_line={
                'amount_currency':amount_currency,
                'currency_id':taxes_map_entry['grouping_dict']['currency_id'],
                'debit':balance>0.0andbalanceor0.0,
                'credit':balance<0.0and-balanceor0.0,
                'tax_base_amount':tax_base_amount,
                'price_total':sign*amount_currency,
                'price_subtotal':sign*amount_currency,
            }

            iftaxes_map_entry['tax_line']:
                #Updateanexistingtaxline.
                iftax_rep_lines_to_recomputeandtaxes_map_entry['tax_line'].tax_repartition_line_idnotintax_rep_lines_to_recompute:
                    continue

                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                #Createanewtaxline.
                create_method=in_draft_modeandself.env['account.move.line'].neworself.env['account.move.line'].create
                tax_repartition_line_id=taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line=self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)

                iftax_rep_lines_to_recomputeandtax_repartition_linenotintax_rep_lines_to_recompute:
                    continue

                tax=tax_repartition_line.invoice_tax_idortax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line']=create_method({
                    **to_write_on_line,
                    'name':tax.name,
                    'move_id':self.id,
                    'company_id':self.company_id.id,
                    'company_currency_id':self.company_currency_id.id,
                    'tax_base_amount':tax_base_amount,
                    'exclude_from_invoice_tab':True,
                    'tax_exigible':tax.tax_exigibility=='on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            ifin_draft_mode:
                taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))

    def_tax_tags_need_inversion(self,move,is_refund,tax_type):
        """Tellswhetherthetaxtagsneedtobeinvertedforagivenmove.

        :parammove:themoveforwhichwewanttocheckinversion
        :paramis_refund:whetherornottheoperationwewanttheinversionvalueforisarefund
        :paramtax_type:thetaxtypeoftheoperationwewanttheinversionvaluefor

        :return:Trueifthetagsneedtobeinverted
        """
        ifmove.move_type=='entry':
            return(tax_type=='sale'andnotis_refund)or(tax_type=='purchase'andis_refund)
        returnFalse

    @api.model
    def_get_base_amount_to_display(self,base_amount,tax_rep_ln,parent_tax_group=None):
        """Thebaseamountreturnedfortaxesbycompute_allhasisthebalance
        ofthebaseline.Forinboundoperations,positivesignisoncredit,so
        weneedtoinvertthesignofthisamountbeforedisplayingit.
        """
        source_tax=parent_tax_grouportax_rep_ln.invoice_tax_idortax_rep_ln.refund_tax_id
        if(tax_rep_ln.invoice_tax_idandsource_tax.type_tax_use=='sale')\
           or(tax_rep_ln.refund_tax_idandsource_tax.type_tax_use=='purchase'):
            return-base_amount
        returnbase_amount

    defupdate_lines_tax_exigibility(self):
        ifall(account.user_type_id.typenotin{'payable','receivable'}foraccountinself.mapped('line_ids.account_id')):
            self.line_ids.write({'tax_exigible':True})
        else:
            tax_lines_caba=self.line_ids.filtered(lambdax:x.tax_line_id.tax_exigibility=='on_payment')
            base_lines_caba=self.line_ids.filtered(lambdax:any(tax.tax_exigibility=='on_payment'
                                                                   or(tax.amount_type=='group'
                                                                       and'on_payment'intax.mapped('children_tax_ids.tax_exigibility'))
                                                               fortaxinx.tax_ids))
            caba_lines=tax_lines_caba+base_lines_caba
            caba_lines.write({'tax_exigible':False})
            (self.line_ids-caba_lines).write({'tax_exigible':True})

    def_recompute_cash_rounding_lines(self):
        '''Handlethecashroundingfeatureoninvoices.

        Insomecountries,thesmallestcoinsdonotexist.Forexample,inSwitzerland,thereisnocoinfor0.01CHF.
        Forthisreason,ifinvoicesarepaidincash,youhavetoroundtheirtotalamounttothesmallestcointhat
        existsinthecurrency.FortheCHF,thesmallestcoinis0.05CHF.

        Therearetwostrategiesfortherounding:

        1)Addalineontheinvoicefortherounding:Thecashroundinglineisaddedasanewinvoiceline.
        2)Addtheroundinginthebiggesttaxamount:Thecashroundinglineisaddedasanewtaxlineonthetax
        havingthebiggestbalance.
        '''
        self.ensure_one()
        in_draft_mode=self!=self._origin

        def_compute_cash_rounding(self,total_amount_currency):
            '''Computetheamountdifferencesduetothecashrounding.
            :paramself:                   Thecurrentaccount.moverecord.
            :paramtotal_amount_currency:  Theinvoice'stotalininvoice'scurrency.
            :return:                       Theamountdifferencesbothincompany'scurrency&invoice'scurrency.
            '''
            difference=self.invoice_cash_rounding_id.compute_difference(self.currency_id,total_amount_currency)
            ifself.currency_id==self.company_id.currency_id:
                diff_amount_currency=diff_balance=difference
            else:
                diff_amount_currency=difference
                diff_balance=self.currency_id._convert(diff_amount_currency,self.company_id.currency_id,self.company_id,self.date)
            returndiff_balance,diff_amount_currency

        def_apply_cash_rounding(self,diff_balance,diff_amount_currency,cash_rounding_line):
            '''Applythecashrounding.
            :paramself:                   Thecurrentaccount.moverecord.
            :paramdiff_balance:           Thecomputedbalancetosetonthenewroundingline.
            :paramdiff_amount_currency:   Thecomputedamountininvoice'scurrencytosetonthenewroundingline.
            :paramcash_rounding_line:     Theexistingcashroundingline.
            :return:                       Thenewlycreatedroundingline.
            '''
            rounding_line_vals={
                'debit':diff_balance>0.0anddiff_balanceor0.0,
                'credit':diff_balance<0.0and-diff_balanceor0.0,
                'quantity':1.0,
                'amount_currency':diff_amount_currency,
                'partner_id':self.partner_id.id,
                'move_id':self.id,
                'currency_id':self.currency_id.id,
                'company_id':self.company_id.id,
                'company_currency_id':self.company_id.currency_id.id,
                'is_rounding_line':True,
                'sequence':9999,
            }

            ifself.invoice_cash_rounding_id.strategy=='biggest_tax':
                biggest_tax_line=None
                fortax_lineinself.line_ids.filtered('tax_repartition_line_id'):
                    ifnotbiggest_tax_lineortax_line.price_subtotal>biggest_tax_line.price_subtotal:
                        biggest_tax_line=tax_line

                #Notaxfound.
                ifnotbiggest_tax_line:
                    return

                rounding_line_vals.update({
                    'name':_('%s(rounding)',biggest_tax_line.name),
                    'account_id':biggest_tax_line.account_id.id,
                    'tax_repartition_line_id':biggest_tax_line.tax_repartition_line_id.id,
                    'tax_tag_ids':[(6,0,biggest_tax_line.tax_tag_ids.ids)],
                    'tax_exigible':biggest_tax_line.tax_exigible,
                    'exclude_from_invoice_tab':True,
                })

            elifself.invoice_cash_rounding_id.strategy=='add_invoice_line':
                ifdiff_balance>0.0andself.invoice_cash_rounding_id.loss_account_id:
                    account_id=self.invoice_cash_rounding_id.loss_account_id.id
                else:
                    account_id=self.invoice_cash_rounding_id.profit_account_id.id
                rounding_line_vals.update({
                    'name':self.invoice_cash_rounding_id.name,
                    'account_id':account_id,
                })

            #Createorupdatethecashroundingline.
            ifcash_rounding_line:
                cash_rounding_line.update({
                    'amount_currency':rounding_line_vals['amount_currency'],
                    'debit':rounding_line_vals['debit'],
                    'credit':rounding_line_vals['credit'],
                    'account_id':rounding_line_vals['account_id'],
                })
            else:
                create_method=in_draft_modeandself.env['account.move.line'].neworself.env['account.move.line'].create
                cash_rounding_line=create_method(rounding_line_vals)

            ifin_draft_mode:
                cash_rounding_line.update(cash_rounding_line._get_fields_onchange_balance(force_computation=True))

        existing_cash_rounding_line=self.line_ids.filtered(lambdaline:line.is_rounding_line)

        #Thecashroundinghasbeenremoved.
        ifnotself.invoice_cash_rounding_id:
            self.line_ids-=existing_cash_rounding_line
            return

        #Thecashroundingstrategyhaschanged.
        ifself.invoice_cash_rounding_idandexisting_cash_rounding_line:
            strategy=self.invoice_cash_rounding_id.strategy
            old_strategy='biggest_tax'ifexisting_cash_rounding_line.tax_line_idelse'add_invoice_line'
            ifstrategy!=old_strategy:
                self.line_ids-=existing_cash_rounding_line
                existing_cash_rounding_line=self.env['account.move.line']

        others_lines=self.line_ids.filtered(lambdaline:line.account_id.user_type_id.typenotin('receivable','payable'))
        others_lines-=existing_cash_rounding_line
        total_amount_currency=sum(others_lines.mapped('amount_currency'))

        diff_balance,diff_amount_currency=_compute_cash_rounding(self,total_amount_currency)

        #Theinvoiceisalreadyrounded.
        ifself.currency_id.is_zero(diff_balance)andself.currency_id.is_zero(diff_amount_currency):
            self.line_ids-=existing_cash_rounding_line
            return

        _apply_cash_rounding(self,diff_balance,diff_amount_currency,existing_cash_rounding_line)

    def_recompute_payment_terms_lines(self):
        '''Computethedynamicpaymenttermlinesofthejournalentry.'''
        self.ensure_one()
        self=self.with_company(self.company_id)
        in_draft_mode=self!=self._origin
        today=fields.Date.context_today(self)
        self=self.with_company(self.journal_id.company_id)

        def_get_payment_terms_computation_date(self):
            '''Getthedatefrominvoicethatwillbeusedtocomputethepaymentterms.
            :paramself:   Thecurrentaccount.moverecord.
            :return:       Adatetime.dateobject.
            '''
            ifself.invoice_payment_term_id:
                returnself.invoice_dateortoday
            else:
                returnself.invoice_date_dueorself.invoice_dateortoday

        def_get_payment_terms_account(self,payment_terms_lines):
            '''Gettheaccountfrominvoicethatwillbesetasreceivable/payableaccount.
            :paramself:                   Thecurrentaccount.moverecord.
            :parampayment_terms_lines:    Thecurrentpaymenttermslines.
            :return:                       Anaccount.accountrecord.
            '''
            ifpayment_terms_lines:
                #Retrieveaccountfrompreviouspaymenttermslinesinordertoallowtheusertosetacustomone.
                returnpayment_terms_lines[0].account_id
            elifself.partner_id:
                #Retrieveaccountfrompartner.
                ifself.is_sale_document(include_receipts=True):
                    returnself.partner_id.property_account_receivable_id
                else:
                    returnself.partner_id.property_account_payable_id
            else:
                #Searchnewaccount.
                domain=[
                    ('company_id','=',self.company_id.id),
                    ('internal_type','=','receivable'ifself.move_typein('out_invoice','out_refund','out_receipt')else'payable'),
                    ('deprecated','=',False),
                ]
                returnself.env['account.account'].search(domain,limit=1)

        def_compute_payment_terms(self,date,total_balance,total_amount_currency):
            '''Computethepaymentterms.
            :paramself:                   Thecurrentaccount.moverecord.
            :paramdate:                   Thedatecomputedby'_get_payment_terms_computation_date'.
            :paramtotal_balance:          Theinvoice'stotalincompany'scurrency.
            :paramtotal_amount_currency:  Theinvoice'stotalininvoice'scurrency.
            :return:                       Alist<to_pay_company_currency,to_pay_invoice_currency,due_date>.
            '''
            ifself.invoice_payment_term_id:
                to_compute=self.invoice_payment_term_id.compute(total_balance,date_ref=date,currency=self.company_id.currency_id)
                ifself.currency_id==self.company_id.currency_id:
                    #Single-currency.
                    return[(b[0],b[1],b[1])forbinto_compute]
                else:
                    #Multi-currencies.
                    to_compute_currency=self.invoice_payment_term_id.compute(total_amount_currency,date_ref=date,currency=self.currency_id)
                    return[(b[0],b[1],ac[1])forb,acinzip(to_compute,to_compute_currency)]
            else:
                return[(fields.Date.to_string(date),total_balance,total_amount_currency)]

        def_compute_diff_payment_terms_lines(self,existing_terms_lines,account,to_compute):
            '''Processtheresultofthe'_compute_payment_terms'methodandcreates/updatescorrespondinginvoicelines.
            :paramself:                   Thecurrentaccount.moverecord.
            :paramexisting_terms_lines:   Thecurrentpaymenttermslines.
            :paramaccount:                Theaccount.accountrecordreturnedby'_get_payment_terms_account'.
            :paramto_compute:             Thelistreturnedby'_compute_payment_terms'.
            '''
            #Aswetrytoupdateexistinglines,sortthembyduedate.
            existing_terms_lines=existing_terms_lines.sorted(lambdaline:line.date_maturityortoday)
            existing_terms_lines_index=0

            #Recomputeamls:updateexistinglineorcreatenewoneforeachpaymentterm.
            new_terms_lines=self.env['account.move.line']
            fordate_maturity,balance,amount_currencyinto_compute:
                currency=self.journal_id.company_id.currency_id
                ifcurrencyandcurrency.is_zero(balance)andlen(to_compute)>1:
                    continue

                ifexisting_terms_lines_index<len(existing_terms_lines):
                    #Updateexistingline.
                    candidate=existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index+=1
                    candidate.update({
                        'date_maturity':date_maturity,
                        'amount_currency':-amount_currency,
                        'debit':balance<0.0and-balanceor0.0,
                        'credit':balance>0.0andbalanceor0.0,
                    })
                else:
                    #Createnewline.
                    create_method=in_draft_modeandself.env['account.move.line'].neworself.env['account.move.line'].create
                    candidate=create_method({
                        'name':self.payment_referenceor'',
                        'debit':balance<0.0and-balanceor0.0,
                        'credit':balance>0.0andbalanceor0.0,
                        'quantity':1.0,
                        'amount_currency':-amount_currency,
                        'date_maturity':date_maturity,
                        'move_id':self.id,
                        'currency_id':self.currency_id.id,
                        'account_id':account.id,
                        'partner_id':self.commercial_partner_id.id,
                        'exclude_from_invoice_tab':True,
                    })
                new_terms_lines+=candidate
                ifin_draft_mode:
                    candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
            returnnew_terms_lines

        existing_terms_lines=self.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        others_lines=self.line_ids.filtered(lambdaline:line.account_id.user_type_id.typenotin('receivable','payable'))
        company_currency_id=(self.company_idorself.env.company).currency_id
        total_balance=sum(others_lines.mapped(lambdal:company_currency_id.round(l.balance)))
        total_amount_currency=sum(others_lines.mapped('amount_currency'))

        ifnotothers_lines:
            self.line_ids-=existing_terms_lines
            return

        computation_date=_get_payment_terms_computation_date(self)
        account=_get_payment_terms_account(self,existing_terms_lines)
        to_compute=_compute_payment_terms(self,computation_date,total_balance,total_amount_currency)
        new_terms_lines=_compute_diff_payment_terms_lines(self,existing_terms_lines,account,to_compute)

        #Removeoldtermslinesthatarenolongerneeded.
        self.line_ids-=existing_terms_lines-new_terms_lines

        ifnew_terms_lines:
            self.payment_reference=new_terms_lines[-1].nameor''
            self.invoice_date_due=new_terms_lines[-1].date_maturity

    def_recompute_dynamic_lines(self,recompute_all_taxes=False,recompute_tax_base_amount=False):
        '''Recomputealllinesthatdependonothers.

        Forexample,taxlinesdependsonbaselines(lineshavingtax_idsset).Thisisalsothecaseofcashrounding
        linesthatdependonbaselinesortaxlinesdependingonthecashroundingstrategy.Whenapaymenttermisset,
        thismethodwillauto-balancethemovewithpaymenttermlines.

        :paramrecompute_all_taxes:Forcethecomputationoftaxes.IfsettoFalse,thecomputationwillbedone
                                    ornotdependingonthefield'recompute_tax_line'inlines.
        '''
        forinvoiceinself:
            #Dispatchlinesandpre-computesomeaggregatedvaluesliketaxes.
            expected_tax_rep_lines=set()
            current_tax_rep_lines=set()
            inv_recompute_all_taxes=recompute_all_taxes
            has_taxes=False
            forlineininvoice.line_ids:
                ifline.recompute_tax_line:
                    inv_recompute_all_taxes=True
                    line.recompute_tax_line=False
                ifline.tax_repartition_line_id:
                    current_tax_rep_lines.add(line.tax_repartition_line_id._origin)
                elifline.tax_ids:
                    has_taxes=True
                    ifinvoice.is_invoice(include_receipts=True):
                        is_refund=invoice.move_typein('out_refund','in_refund')
                    else:
                        tax_type=line.tax_ids[0].type_tax_use
                        is_refund=(tax_type=='sale'andline.debit)or(tax_type=='purchase'andline.credit)
                    taxes=line.tax_ids._origin.flatten_taxes_hierarchy().filtered(
                        lambdatax:(
                                tax.amount_type=='fixed'andnotinvoice.company_id.currency_id.is_zero(tax.amount)
                                ornotfloat_is_zero(tax.amount,precision_digits=4)
                        )
                    )
                    ifis_refund:
                        tax_rep_lines=taxes.refund_repartition_line_ids._origin.filtered(lambdax:x.repartition_type=="tax")
                    else:
                        tax_rep_lines=taxes.invoice_repartition_line_ids._origin.filtered(lambdax:x.repartition_type=="tax")
                    fortax_rep_lineintax_rep_lines:
                        expected_tax_rep_lines.add(tax_rep_line)
            delta_tax_rep_lines=expected_tax_rep_lines-current_tax_rep_lines

            #Computetaxes.
            ifhas_taxesorcurrent_tax_rep_lines:
                ifinv_recompute_all_taxes:
                    invoice._recompute_tax_lines()
                elifrecompute_tax_base_amount:
                    invoice._recompute_tax_lines(recompute_tax_base_amount=True)
                elifdelta_tax_rep_linesandnotself._context.get('move_reverse_cancel'):
                    invoice._recompute_tax_lines(tax_rep_lines_to_recompute=delta_tax_rep_lines)

            ifinvoice.is_invoice(include_receipts=True):

                #Computecashrounding.
                invoice._recompute_cash_rounding_lines()

                #Computepaymentterms.
                invoice._recompute_payment_terms_lines()

                #Onlysynchronizeone2manyinonchange.
                ifinvoice!=invoice._origin:
                    invoice.invoice_line_ids=invoice.line_ids.filtered(lambdaline:notline.exclude_from_invoice_tab)

    @api.depends('journal_id')
    def_compute_company_id(self):
        formoveinself:
            move.company_id=move.journal_id.company_idormove.company_idorself.env.company

    def_get_lines_onchange_currency(self):
        #OverrideneededforCOGS
        returnself.line_ids

    defonchange(self,values,field_name,field_onchange):
        #OVERRIDE
        #Asthedynamiclinesinthismodelarequitecomplex,weneedtoensuresomecomputationsaredoneexactly
        #atthebeginning/attheendoftheonchangemechanism.So,theonchangerecursivityisdisabled.
        returnsuper(AccountMove,self.with_context(recursive_onchanges=False)).onchange(values,field_name,field_onchange)

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('company_id','invoice_filter_type_domain')
    def_compute_suitable_journal_ids(self):
        forminself:
            journal_type=m.invoice_filter_type_domainor'general'
            company_id=m.company_id.idorself.env.company.id
            domain=[('company_id','=',company_id),('type','=',journal_type)]
            m.suitable_journal_ids=self.env['account.journal'].search(domain)

    @api.depends('posted_before','state','journal_id','date')
    def_compute_name(self):
        defjournal_key(move):
            return(move.journal_id,move.journal_id.refund_sequenceandmove.move_type)

        defdate_key(move):
            return(move.date.year,move.date.month)

        grouped=defaultdict( #key:journal_id,move_type
            lambda:defaultdict( #key:firstadjacent(date.year,date.month)
                lambda:{
                    'records':self.env['account.move'],
                    'format':False,
                    'format_values':False,
                    'reset':False
                }
            )
        )
        self=self.sorted(lambdam:(m.date,m.refor'',m.id))

        #Groupthemovesbyjournalandmonth
        formoveinself:
            move_has_name=move.nameandmove.name!='/'
            ifmove_has_nameormove.state!='posted':
                try:
                    ifnotmove.posted_before:
                        #Themovewasneverposted,sothenamecanpotentiallybechanged.
                        move._constrains_date_sequence()
                    #Eitherthemovewaspostedbefore,orthenamealreadymatchesthedate(ornonameordate).
                    #Wecanskiprecalculatingthenamewheneither
                    #-themovealreadyhasaname,or
                    #-themovehasnoname,butisinaperiodwithothermoves(sonameshouldbe`/`),or
                    #-themovehas(temporarily)nodateset
                    if(
                        move_has_nameandmove.posted_before
                        ornotmove_has_nameandmove._get_last_sequence(lock=False)
                        ornotmove.date
                    ):
                        continue
                exceptValidationError:
                    #Themovewasneverpostedandthecurrentnamedoesn'tmatchthedate.Weshouldcalculatethe
                    #namelateron,unless...
                    ifmove._get_last_sequence(lock=False):
                        #...weareinaperiodalreadycontainingmoves:resetthenameto`/`(draft)
                        move.name='/'
                        continue
            group=grouped[journal_key(move)][date_key(move)]
            ifnotgroup['records']:
                #Computeallthevaluesneededtosequencethiswholegroup
                move._set_next_sequence()
                group['format'],group['format_values']=move._get_sequence_format_param(move.name)
                group['reset']=move._deduce_sequence_number_reset(move.name)
            group['records']+=move

        #Fusionthegroupsdependingonthesequenceresetandtheformatusedbecause`seq`is
        #thesamecounterformultiplegroupsthatmightbespreadinmultiplemonths.
        final_batches=[]
        forjournal_groupingrouped.values():
            journal_group_changed=True
            fordate_groupinjournal_group.values():
                if(
                    journal_group_changed
                    orfinal_batches[-1]['format']!=date_group['format']
                    ordict(final_batches[-1]['format_values'],seq=0)!=dict(date_group['format_values'],seq=0)
                ):
                    final_batches+=[date_group]
                    journal_group_changed=False
                elifdate_group['reset']=='never':
                    final_batches[-1]['records']+=date_group['records']
                elif(
                    date_group['reset']=='year'
                    andfinal_batches[-1]['records'][0].date.year==date_group['records'][0].date.year
                ):
                    final_batches[-1]['records']+=date_group['records']
                else:
                    final_batches+=[date_group]

        #Givethenamebasedonpreviouslycomputedvalues
        forbatchinfinal_batches:
            formoveinbatch['records']:
                move.name=batch['format'].format(**batch['format_values'])
                batch['format_values']['seq']+=1
            batch['records']._compute_split_sequence()

        self.filtered(lambdam:notm.name).name='/'

    @api.depends('journal_id','date')
    def_compute_highest_name(self):
        forrecordinself:
            record.highest_name=record._get_last_sequence(lock=False)

    @api.onchange('name','highest_name')
    def_onchange_name_warning(self):
        ifself.nameandself.name!='/'andself.name<=(self.highest_nameor''):
            self.show_name_warning=True
        else:
            self.show_name_warning=False

        origin_name=self._origin.name
        ifnotorigin_nameororigin_name=='/':
            origin_name=self.highest_name
        ifself.nameandself.name!='/'andorigin_nameandorigin_name!='/':
            format,format_values=self._get_sequence_format_param(self.name)
            origin_format,origin_format_values=self._get_sequence_format_param(origin_name)

            if(
                format!=origin_format
                ordict(format_values,seq=0)!=dict(origin_format_values,seq=0)
            ):
                changed=_(
                    "Itwaspreviously'%(previous)s'anditisnow'%(current)s'.",
                    previous=origin_name,
                    current=self.name,
                )
                reset=self._deduce_sequence_number_reset(self.name)
                ifreset=='month':
                    detected=_(
                        "Thesequencewillrestartat1atthestartofeverymonth.\n"
                        "Theyeardetectedhereis'%(year)s'andthemonthis'%(month)s'.\n"
                        "Theincrementingnumberinthiscaseis'%(formatted_seq)s'."
                    )
                elifreset=='year':
                    detected=_(
                        "Thesequencewillrestartat1atthestartofeveryyear.\n"
                        "Theyeardetectedhereis'%(year)s'.\n"
                        "Theincrementingnumberinthiscaseis'%(formatted_seq)s'."
                    )
                else:
                    detected=_(
                        "Thesequencewillneverrestart.\n"
                        "Theincrementingnumberinthiscaseis'%(formatted_seq)s'."
                    )
                format_values['formatted_seq']="{seq:0{seq_length}d}".format(**format_values)
                detected=detected%format_values
                return{'warning':{
                    'title':_("Thesequenceformathaschanged."),
                    'message':"%s\n\n%s"%(changed,detected)
                }}

    @api.depends('state')
    def_compute_payment_reference(self):
        formoveinself.filtered(lambdam:(
            m.state=='posted'
            andm._auto_compute_invoice_reference()
        )):
            move.payment_reference=move._get_invoice_computed_reference()

    def_get_last_sequence_domain(self,relaxed=False):
        self.ensure_one()
        ifnotself.dateornotself.journal_id:
            return"WHEREFALSE",{}
        where_string="WHEREjournal_id=%(journal_id)sANDname!='/'"
        param={'journal_id':self.journal_id.id}

        ifnotrelaxed:
            domain=[('journal_id','=',self.journal_id.id),('id','!=',self.idorself._origin.id),('name','notin',('/','',False))]
            ifself.journal_id.refund_sequence:
                refund_types=('out_refund','in_refund')
                domain+=[('move_type','in'ifself.move_typeinrefund_typeselse'notin',refund_types)]
            reference_move_name=self.search(domain+[('date','<=',self.date)],order='datedesc',limit=1).name
            ifnotreference_move_name:
                reference_move_name=self.search(domain,order='dateasc',limit=1).name
            sequence_number_reset=self._deduce_sequence_number_reset(reference_move_name)
            ifsequence_number_reset=='year':
                where_string+="ANDdate_trunc('year',date::timestampwithouttimezone)=date_trunc('year',%(date)s)"
                param['date']=self.date
                param['anti_regex']=re.sub(r"\?P<\w+>","?:",self._sequence_monthly_regex.split('(?P<seq>')[0])+'$'
            elifsequence_number_reset=='month':
                where_string+="ANDdate_trunc('month',date::timestampwithouttimezone)=date_trunc('month',%(date)s)"
                param['date']=self.date
            else:
                param['anti_regex']=re.sub(r"\?P<\w+>","?:",self._sequence_yearly_regex.split('(?P<seq>')[0])+'$'

            ifparam.get('anti_regex')andnotself.journal_id.sequence_override_regex:
                where_string+="ANDsequence_prefix!~%(anti_regex)s"

        ifself.journal_id.refund_sequence:
            ifself.move_typein('out_refund','in_refund'):
                where_string+="ANDmove_typeIN('out_refund','in_refund')"
            else:
                where_string+="ANDmove_typeNOTIN('out_refund','in_refund')"

        returnwhere_string,param

    def_get_starting_sequence(self):
        self.ensure_one()
        starting_sequence="%s/%04d/%02d/0000"%(self.journal_id.code,self.date.year,self.date.month)
        ifself.journal_id.refund_sequenceandself.move_typein('out_refund','in_refund'):
            starting_sequence="R"+starting_sequence
        returnstarting_sequence

    @api.depends('move_type')
    def_compute_type_name(self):
        type_name_mapping={k:vfork,vin
                             self._fields['move_type']._description_selection(self.env)}
        replacements={'out_invoice':_('Invoice'),'out_refund':_('CreditNote')}

        forrecordinself:
            name=type_name_mapping[record.move_type]
            record.type_name=replacements.get(record.move_type,name)

    @api.depends('move_type')
    def_compute_invoice_filter_type_domain(self):
        formoveinself:
            ifmove.is_sale_document(include_receipts=True):
                move.invoice_filter_type_domain='sale'
            elifmove.is_purchase_document(include_receipts=True):
                move.invoice_filter_type_domain='purchase'
            else:
                move.invoice_filter_type_domain=False

    @api.depends('partner_id')
    def_compute_commercial_partner_id(self):
        formoveinself:
            move.commercial_partner_id=move.partner_id.commercial_partner_id

    @api.depends('bank_partner_id')
    def_compute_partner_bank_id(self):
        formoveinself:
            bank_ids=move.bank_partner_id.bank_ids.filtered(lambdabank:bank.company_idisFalseorbank.company_id==move.company_id)
            move.partner_bank_id=bank_idsandbank_ids[0]

    @api.depends('commercial_partner_id','move_type')
    def_compute_bank_partner_id(self):
        formoveinself:
            ifmove.is_inbound():
                move.bank_partner_id=move.company_id.partner_id
            else:
                move.bank_partner_id=move.commercial_partner_id

    @api.model
    def_get_invoice_in_payment_state(self):
        '''Hooktogivethestatewhentheinvoicebecomesfullypaid.Thisisnecessarybecausetheusersworking
        withonlyinvoicingdon'twanttoseethe'in_payment'state.Then,thismethodwillbeoverriddeninthe
        accountantmoduletoenablethe'in_payment'state.'''
        return'paid'

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def_compute_amount(self):
        in_invoices=self.filtered(lambdam:m.move_type=='in_invoice')
        out_invoices=self.filtered(lambdam:m.move_type=='out_invoice')
        others=self.filtered(lambdam:m.move_typenotin('in_invoice','out_invoice'))
        reversed_mapping=defaultdict(lambda:self.env['account.move'])
        forreverse_moveinself.env['account.move'].search([
            ('state','=','posted'),
            '|','|',
            '&',('reversed_entry_id','in',in_invoices.ids),('move_type','=','in_refund'),
            '&',('reversed_entry_id','in',out_invoices.ids),('move_type','=','out_refund'),
            '&',('reversed_entry_id','in',others.ids),('move_type','=','entry'),
        ]):
            reversed_mapping[reverse_move.reversed_entry_id]+=reverse_move

        caba_mapping=defaultdict(lambda:self.env['account.move'])
        caba_company_ids=self.company_id.filtered(lambdac:c.tax_exigibility)
        reverse_moves_ids=[move.idformovesinreversed_mapping.values()formoveinmoves]
        forcaba_moveinself.env['account.move'].search([
            ('tax_cash_basis_move_id','in',self.ids+reverse_moves_ids),
            ('state','=','posted'),
            ('move_type','=','entry'),
            ('company_id','in',caba_company_ids.ids)
        ]):
            caba_mapping[caba_move.tax_cash_basis_move_id]+=caba_move

        formoveinself:

            ifmove.payment_state=='invoicing_legacy':
                #invoicing_legacystateissetviaSQLwhensettingsettingfield
                #invoicing_switch_threshold(definedinaccount_accountant).
                #Theonlywayofgoingoutofthisstateisthroughthissetting,
                #sowedon'trecomputeithere.
                move.payment_state=move.payment_state
                continue

            total_untaxed=0.0
            total_untaxed_currency=0.0
            total_tax=0.0
            total_tax_currency=0.0
            total_to_pay=0.0
            total_residual=0.0
            total_residual_currency=0.0
            total=0.0
            total_currency=0.0
            currencies=move._get_lines_onchange_currency().currency_id

            forlineinmove.line_ids:
                ifmove.is_invoice(include_receipts=True):
                    #===Invoices===

                    ifnotline.exclude_from_invoice_tab:
                        #Untaxedamount.
                        total_untaxed+=line.balance
                        total_untaxed_currency+=line.amount_currency
                        total+=line.balance
                        total_currency+=line.amount_currency
                    elifline.tax_line_id:
                        #Taxamount.
                        total_tax+=line.balance
                        total_tax_currency+=line.amount_currency
                        total+=line.balance
                        total_currency+=line.amount_currency
                    elifline.account_id.user_type_id.typein('receivable','payable'):
                        #Residualamount.
                        total_to_pay+=line.balance
                        total_residual+=line.amount_residual
                        total_residual_currency+=line.amount_residual_currency
                else:
                    #===Miscellaneousjournalentry===
                    ifline.debit:
                        total+=line.balance
                        total_currency+=line.amount_currency

            ifmove.move_type=='entry'ormove.is_outbound():
                sign=1
            else:
                sign=-1
            move.amount_untaxed=sign*(total_untaxed_currencyiflen(currencies)==1elsetotal_untaxed)
            move.amount_tax=sign*(total_tax_currencyiflen(currencies)==1elsetotal_tax)
            move.amount_total=sign*(total_currencyiflen(currencies)==1elsetotal)
            move.amount_residual=-sign*(total_residual_currencyiflen(currencies)==1elsetotal_residual)
            move.amount_untaxed_signed=-total_untaxed
            move.amount_tax_signed=-total_tax
            move.amount_total_signed=abs(total)ifmove.move_type=='entry'else-total
            move.amount_residual_signed=total_residual

            currency=len(currencies)==1andcurrenciesormove.company_id.currency_id

            #Compute'payment_state'.
            new_pmt_state='not_paid'ifmove.move_type!='entry'elseFalse

            ifmove.is_invoice(include_receipts=True)andmove.state=='posted':

                ifcurrency.is_zero(move.amount_residual):
                    reconciled_payments=move._get_reconciled_payments()
                    ifnotreconciled_paymentsorall(payment.is_matchedforpaymentinreconciled_payments):
                        new_pmt_state='paid'
                    else:
                        new_pmt_state=move._get_invoice_in_payment_state()
                elifcurrency.compare_amounts(total_to_pay,total_residual)!=0:
                    new_pmt_state='partial'

            ifnew_pmt_state=='paid'andmove.move_typein('in_invoice','out_invoice','entry'):
                reverse_moves=reversed_mapping[move]
                caba_moves=caba_mapping[move]
                forreverse_moveinreverse_moves:
                    caba_moves|=caba_mapping[reverse_move]

                #Weonlyset'reversed'stateincasof1to1fullreconciliationwithareverseentry;otherwise,weusetheregular'paid'state
                #Weignorepotentialscashbasismovesreconciledbecausethetransitionaccountofthetaxisreconcilable
                reverse_moves_full_recs=reverse_moves.mapped('line_ids.full_reconcile_id')
                ifreverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambdax:xnotin(caba_moves+reverse_moves+reverse_moves_full_recs.mapped('exchange_move_id')))==move:
                    new_pmt_state='reversed'

            move.payment_state=new_pmt_state

    def_inverse_amount_total(self):
        formoveinself:
            iflen(move.line_ids)!=2ormove.is_invoice(include_receipts=True):
                continue

            to_write=[]

            amount_currency=abs(move.amount_total)
            balance=move.currency_id._convert(amount_currency,move.company_currency_id,move.company_id,move.date)

            forlineinmove.line_ids:
                ifnotline.currency_id.is_zero(balance-abs(line.balance)):
                    to_write.append((1,line.id,{
                        'debit':line.balance>0.0andbalanceor0.0,
                        'credit':line.balance<0.0andbalanceor0.0,
                        'amount_currency':line.balance>0.0andamount_currencyor-amount_currency,
                    }))

            move.write({'line_ids':to_write})

    def_get_domain_matching_suspense_moves(self):
        self.ensure_one()
        domain=self.env['account.move.line']._get_suspense_moves_domain()
        domain+=['|',('partner_id','=?',self.partner_id.id),('partner_id','=',False)]
        ifself.is_inbound():
            domain.append(('balance','=',-self.amount_residual))
        else:
            domain.append(('balance','=',self.amount_residual))
        returndomain

    def_compute_has_matching_suspense_amount(self):
        forrinself:
            res=False
            ifr.state=='posted'andr.is_invoice()andr.payment_state=='not_paid':
                domain=r._get_domain_matching_suspense_moves()
                #therearemorethanonebutlessthan5suspensemovesmatchingtheresidualamount
                if(0<self.env['account.move.line'].search_count(domain)<5):
                    domain2=[
                        ('payment_state','=','not_paid'),
                        ('state','=','posted'),
                        ('amount_residual','=',r.amount_residual),
                        ('move_type','=',r.move_type)]
                    #therearelessthan5otheropeninvoicesofthesametypewiththesameresidual
                    ifself.env['account.move'].search_count(domain2)<5:
                        res=True
            r.invoice_has_matching_suspense_amount=res

    @api.depends('partner_id','invoice_source_email','partner_id.name')
    def_compute_invoice_partner_display_info(self):
        formoveinself:
            vendor_display_name=move.partner_id.display_name
            ifnotvendor_display_name:
                ifmove.invoice_source_email:
                    vendor_display_name=_('@From:%(email)s',email=move.invoice_source_email)
                else:
                    vendor_display_name=_('#Createdby:%s',move.sudo().create_uid.nameorself.env.user.name)
            move.invoice_partner_display_name=vendor_display_name

    def_compute_payments_widget_to_reconcile_info(self):
        formoveinself:
            move.invoice_outstanding_credits_debits_widget=json.dumps(False)
            move.invoice_has_outstanding=False

            ifmove.state!='posted'\
                    ormove.payment_statenotin('not_paid','partial')\
                    ornotmove.is_invoice(include_receipts=True):
                continue

            pay_term_lines=move.line_ids\
                .filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))

            domain=[
                ('account_id','in',pay_term_lines.account_id.ids),
                ('parent_state','=','posted'),
                ('partner_id','=',move.commercial_partner_id.id),
                ('reconciled','=',False),
                '|',('amount_residual','!=',0.0),('amount_residual_currency','!=',0.0),
            ]

            payments_widget_vals={'outstanding':True,'content':[],'move_id':move.id}

            ifmove.is_inbound():
                domain.append(('balance','<',0.0))
                payments_widget_vals['title']=_('Outstandingcredits')
            else:
                domain.append(('balance','>',0.0))
                payments_widget_vals['title']=_('Outstandingdebits')

            forlineinself.env['account.move.line'].search(domain):

                ifline.currency_id==move.currency_id:
                    #Sameforeigncurrency.
                    amount=abs(line.amount_residual_currency)
                else:
                    #Differentforeigncurrencies.
                    amount=move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                ifmove.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name':line.reforline.move_id.name,
                    'amount':amount,
                    'currency':move.currency_id.symbol,
                    'id':line.id,
                    'move_id':line.move_id.id,
                    'position':move.currency_id.position,
                    'digits':[69,move.currency_id.decimal_places],
                    'payment_date':fields.Date.to_string(line.date),
                })

            ifnotpayments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget=json.dumps(payments_widget_vals)
            move.invoice_has_outstanding=True

    def_get_reconciled_info_JSON_values(self):
        self.ensure_one()

        reconciled_vals=[]
        forpartial,amount,counterpart_lineinself._get_reconciled_invoices_partials():
            ifcounterpart_line.move_id.ref:
                reconciliation_ref='%s(%s)'%(counterpart_line.move_id.name,counterpart_line.move_id.ref)
            else:
                reconciliation_ref=counterpart_line.move_id.name

            reconciled_vals.append({
                'name':counterpart_line.name,
                'journal_name':counterpart_line.journal_id.name,
                'amount':amount,
                'currency':self.currency_id.symbol,
                'digits':[69,self.currency_id.decimal_places],
                'position':self.currency_id.position,
                'date':counterpart_line.date,
                'payment_id':counterpart_line.id,
                'partial_id':partial.id,
                'account_payment_id':counterpart_line.payment_id.id,
                'payment_method_name':counterpart_line.payment_id.payment_method_id.nameifcounterpart_line.journal_id.type=='bank'elseNone,
                'move_id':counterpart_line.move_id.id,
                'ref':reconciliation_ref,
            })
        returnreconciled_vals

    @api.depends('move_type','line_ids.amount_residual')
    def_compute_payments_widget_reconciled_info(self):
        formoveinself:
            payments_widget_vals={'title':_('LessPayment'),'outstanding':False,'content':[]}

            ifmove.state=='posted'andmove.is_invoice(include_receipts=True):
                payments_widget_vals['content']=move._get_reconciled_info_JSON_values()

            ifpayments_widget_vals['content']:
                move.invoice_payments_widget=json.dumps(payments_widget_vals,default=date_utils.json_default)
            else:
                move.invoice_payments_widget=json.dumps(False)

    @api.depends('line_ids.price_subtotal','line_ids.tax_base_amount','line_ids.tax_line_id','partner_id','currency_id')
    def_compute_invoice_taxes_by_group(self):
        formoveinself:

            #Notworkingonsomethingelsethaninvoices.
            ifnotmove.is_invoice(include_receipts=True):
                move.amount_by_group=[]
                continue

            balance_multiplicator=-1ifmove.is_inbound()else1

            tax_lines=move.line_ids.filtered('tax_line_id')
            base_lines=move.line_ids.filtered('tax_ids')

            tax_group_mapping=defaultdict(lambda:{
                'base_lines':set(),
                'base_amount':0.0,
                'tax_amount':0.0,
            })

            #Computebaseamounts.
            forbase_lineinbase_lines:
                base_amount=balance_multiplicator*(base_line.amount_currencyifbase_line.currency_idelsebase_line.balance)

                fortaxinbase_line.tax_ids.flatten_taxes_hierarchy():

                    ifbase_line.tax_line_id.tax_group_id==tax.tax_group_id:
                        continue

                    tax_group_vals=tax_group_mapping[tax.tax_group_id]
                    ifbase_linenotintax_group_vals['base_lines']:
                        tax_group_vals['base_amount']+=base_amount
                        tax_group_vals['base_lines'].add(base_line)

            #Computetaxamounts.
            fortax_lineintax_lines:
                tax_amount=balance_multiplicator*(tax_line.amount_currencyiftax_line.currency_idelsetax_line.balance)
                tax_group_vals=tax_group_mapping[tax_line.tax_line_id.tax_group_id]
                tax_group_vals['tax_amount']+=tax_amount

            tax_groups=sorted(tax_group_mapping.keys(),key=lambdax:x.sequence)
            amount_by_group=[]
            fortax_groupintax_groups:
                tax_group_vals=tax_group_mapping[tax_group]
                amount_by_group.append((
                    tax_group.name,
                    tax_group_vals['tax_amount'],
                    tax_group_vals['base_amount'],
                    formatLang(self.env,tax_group_vals['tax_amount'],currency_obj=move.currency_id),
                    formatLang(self.env,tax_group_vals['base_amount'],currency_obj=move.currency_id),
                    len(tax_group_mapping),
                    tax_group.id
                ))
            move.amount_by_group=amount_by_group

    @api.model
    def_get_tax_key_for_group_add_base(self,line):
        """
        Usefulfor_compute_invoice_taxes_by_group
        mustbeconsistentwith_get_tax_grouping_key_from_tax_line
         @returnlist
        """
        #DEPRECATED:TOBEREMOVEDINMASTER
        return[line.tax_line_id.id]

    @api.depends('date','line_ids.debit','line_ids.credit','line_ids.tax_line_id','line_ids.tax_ids','line_ids.tax_tag_ids')
    def_compute_tax_lock_date_message(self):
        formoveinself:
            ifmove._affect_tax_report()andmove.company_id.tax_lock_dateandmove.dateandmove.date<=move.company_id.tax_lock_date:
                move.tax_lock_date_message=_(
                    "Theaccountingdateissetpriortothetaxlockdatewhichisseton%s."
                    "Hence,theaccountingdatewillbechangedtothenextavailabledatewhenposting.",
                    format_date(self.env,move.company_id.tax_lock_date))
            else:
                move.tax_lock_date_message=False

    @api.depends('restrict_mode_hash_table','state')
    def_compute_show_reset_to_draft_button(self):
        formoveinself:
            move.show_reset_to_draft_button=notmove.restrict_mode_hash_tableandmove.statein('posted','cancel')

    #-------------------------------------------------------------------------
    #BUSINESSMODELSSYNCHRONIZATION
    #-------------------------------------------------------------------------

    def_synchronize_business_models(self,changed_fields):
        '''Ensuretheconsistencybetween:
        account.payment&account.move
        account.bank.statement.line&account.move

        Theideaistocallthemethodperformingthesynchronizationofthebusiness
        modelsregardingtheirrelatedjournalentries.Toavoidcycling,the
        'skip_account_move_synchronization'keyisusedthroughthecontext.

        :paramchanged_fields:Asetcontainingallmodifiedfieldsonaccount.move.
        '''
        ifself._context.get('skip_account_move_synchronization'):
            return

        self_sudo=self.sudo()
        self_sudo.payment_id._synchronize_from_moves(changed_fields)
        self_sudo.statement_line_id._synchronize_from_moves(changed_fields)

    #-------------------------------------------------------------------------
    #CONSTRAINTMETHODS
    #-------------------------------------------------------------------------

    @api.constrains('name','journal_id','state')
    def_check_unique_sequence_number(self):
        moves=self.filtered(lambdamove:move.state=='posted')
        ifnotmoves:
            return

        self.flush(['name','journal_id','move_type','state'])

        #/!\Computedstoredfieldsarenotyetinsidethedatabase.
        self._cr.execute('''
            SELECTmove2.id,move2.name
            FROMaccount_movemove
            INNERJOINaccount_movemove2ON
                move2.name=move.name
                ANDmove2.journal_id=move.journal_id
                ANDmove2.move_type=move.move_type
                ANDmove2.id!=move.id
            WHEREmove.idIN%sANDmove2.state='posted'
        ''',[tuple(moves.ids)])
        res=self._cr.fetchall()
        ifres:
            raiseValidationError(_('Postedjournalentrymusthaveanuniquesequencenumberpercompany.\n'
                                    'Problematicnumbers:%s\n')%','.join(r[1]forrinres))

    @api.constrains('ref','move_type','partner_id','journal_id','invoice_date','state')
    def_check_duplicate_supplier_reference(self):
        moves=self.filtered(lambdamove:move.state=='posted'andmove.is_purchase_document()andmove.ref)
        ifnotmoves:
            return

        self.env["account.move"].flush([
            "ref","move_type","invoice_date","journal_id",
            "company_id","partner_id","commercial_partner_id",
        ])
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        #/!\Computedstoredfieldsarenotyetinsidethedatabase.
        self._cr.execute('''
            SELECTmove2.id
            FROMaccount_movemove
            JOINaccount_journaljournalONjournal.id=move.journal_id
            JOINres_partnerpartnerONpartner.id=move.partner_id
            INNERJOINaccount_movemove2ON
                move2.ref=move.ref
                ANDmove2.company_id=journal.company_id
                ANDmove2.commercial_partner_id=partner.commercial_partner_id
                ANDmove2.move_type=move.move_type
                AND(move.invoice_dateisNULLORmove2.invoice_date=move.invoice_date)
                ANDmove2.id!=move.id
            WHEREmove.idIN%s
        ''',[tuple(moves.ids)])
        duplicated_moves=self.browse([r[0]forrinself._cr.fetchall()])
        ifduplicated_moves:
            raiseValidationError(_('Duplicatedvendorreferencedetected.Youprobablyencodedtwicethesamevendorbill/creditnote:\n%s')%"\n".join(
                duplicated_moves.mapped(lambdam:"%(partner)s-%(ref)s-%(date)s"%{
                    'ref':m.ref,
                    'partner':m.partner_id.display_name,
                    'date':format_date(self.env,m.invoice_date),
                })
            ))

    def_check_balanced(self):
        '''Assertthemoveisfullybalanceddebit=credit.
        Anerrorisraisedifit'snotthecase.
        '''
        moves=self.filtered(lambdamove:move.line_ids)
        ifnotmoves:
            return

        #/!\Asthismethodiscalledincreate/write,wecan'tmaketheassumptionthecomputedstoredfields
        #arealreadydone.Then,thisqueryMUSTNOTdependofcomputedstoredfields(e.g.balance).
        #IthappensastheORMmakesthecreatewiththe'no_recompute'statement.
        self.env['account.move.line'].flush(self.env['account.move.line']._fields)
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECTline.move_id,ROUND(SUM(line.debit-line.credit),currency.decimal_places)
            FROMaccount_move_lineline
            JOINaccount_movemoveONmove.id=line.move_id
            JOINaccount_journaljournalONjournal.id=move.journal_id
            JOINres_companycompanyONcompany.id=journal.company_id
            JOINres_currencycurrencyONcurrency.id=company.currency_id
            WHEREline.move_idIN%s
            GROUPBYline.move_id,currency.decimal_places
            HAVINGROUND(SUM(line.debit-line.credit),currency.decimal_places)!=0.0;
        ''',[tuple(self.ids)])

        query_res=self._cr.fetchall()
        ifquery_res:
            ids=[res[0]forresinquery_res]
            sums=[res[1]forresinquery_res]
            raiseUserError(_("Cannotcreateunbalancedjournalentry.Ids:%s\nDifferencesdebit-credit:%s")%(ids,sums))

    def_check_fiscalyear_lock_date(self):
        formoveinself:
            lock_date=move.company_id._get_user_fiscal_lock_date()
            ifmove.date<=lock_date:
                ifself.user_has_groups('account.group_account_manager'):
                    message=_("Youcannotadd/modifyentriespriortoandinclusiveofthelockdate%s.",format_date(self.env,lock_date))
                else:
                    message=_("Youcannotadd/modifyentriespriortoandinclusiveofthelockdate%s.Checkthecompanysettingsorasksomeonewiththe'Adviser'role",format_date(self.env,lock_date))
                raiseUserError(message)
        returnTrue

    @api.constrains('move_type','journal_id')
    def_check_journal_type(self):
        forrecordinself:
            journal_type=record.journal_id.type

            ifrecord.is_sale_document()andjournal_type!='sale'orrecord.is_purchase_document()andjournal_type!='purchase':
                raiseValidationError(_("Thechosenjournalhasatypethatisnotcompatiblewithyourinvoicetype.Salesoperationsshouldgoto'sale'journals,andpurchaseoperationsto'purchase'ones."))

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    def_move_autocomplete_invoice_lines_values(self):
        '''Thismethodrecomputesdynamiclinesonthecurrentjournalentrythatincludetaxes,cashrounding
        andpaymenttermslines.
        '''
        self.ensure_one()

        forlineinself.line_ids.filtered(lambdal:notl.display_type):
            analytic_account=line._cache.get('analytic_account_id')

            #Dosomethingonlyoninvoicelines.
            ifline.exclude_from_invoice_tab:
                continue

            #Shortcuttoloadthedemodata.
            #Doingline.account_idtriggersadefault_get(['account_id'])thatcouldreturnsaresult.
            #Asection/notemustnothaveanaccount_idset.
            ifnotline._cache.get('account_id')andnotline._origin:
                line.account_id=line._get_computed_account()orself.journal_id.default_account_id
            ifline.product_idandnotline._cache.get('name'):
                line.name=line._get_computed_name()

            #Computetheaccountbeforethepartner_id
            #Incaseaccount_followupisinstalled
            #Settingthepartnerwillgettheaccount_idincache
            #Iftheaccount_idisnotincache,itwilltriggerthedefaultvalue
            #Whichiswronginsomecase
            #It'sbettertosettheaccount_idbeforethepartner_id
            #Ensurerelatedfieldsarewellcopied.
            ifline.partner_id!=self.partner_id.commercial_partner_id:
                line.partner_id=self.partner_id.commercial_partner_id
            line.date=self.date
            line.recompute_tax_line=True
            line.currency_id=self.currency_id
            ifanalytic_account:
                line.analytic_account_id=analytic_account

        self.line_ids._onchange_price_subtotal()
        self._recompute_dynamic_lines(recompute_all_taxes=True)

        values=self._convert_to_write(self._cache)
        values.pop('invoice_line_ids',None)
        returnvalues

    @api.model
    def_move_autocomplete_invoice_lines_create(self,vals_list):
        '''Duringthecreateofanaccount.movewithonly'invoice_line_ids'setandnot'line_ids',thismethodiscalled
        toautocomputeaccountinglinesoftheinvoice.Inthatcase,accountswillberetrievedandtaxes,cashrounding
        andpaymenttermswillbecomputed.Attheend,thevalueswillcontainsallaccountinglinesin'line_ids'
        andthemovesshouldbebalanced.

        :paramvals_list:  Thelistofvaluespassedtothe'create'method.
        :return:           Modifiedlistofvalues.
        '''
        new_vals_list=[]
        forvalsinvals_list:
            vals=dict(vals)

            ifvals.get('invoice_date')andnotvals.get('date'):
                vals['date']=vals['invoice_date']

            default_move_type=vals.get('move_type')orself._context.get('default_move_type')
            ctx_vals={}
            ifdefault_move_type:
                ctx_vals['default_move_type']=default_move_type
            ifvals.get('journal_id'):
                ctx_vals['default_journal_id']=vals['journal_id']
                #reorderthecompaniesinthecontextsothatthecompanyofthejournal
                #(whichwillbethecompanyofthemove)isthemainone,ensuringall
                #propertyfieldsarereadwiththecorrectcompany
                journal_company=self.env['account.journal'].browse(vals['journal_id']).company_id
                allowed_companies=self._context.get('allowed_company_ids',journal_company.ids)
                reordered_companies=sorted(allowed_companies,key=lambdacid:cid!=journal_company.id)
                ctx_vals['allowed_company_ids']=reordered_companies
            self_ctx=self.with_context(**ctx_vals)
            vals=self_ctx._add_missing_default_values(vals)

            is_invoice=vals.get('move_type')inself.get_invoice_types(include_receipts=True)

            if'line_ids'invals:
                vals.pop('invoice_line_ids',None)
                new_vals_list.append(vals)
                continue

            ifis_invoiceand'invoice_line_ids'invals:
                vals['line_ids']=vals['invoice_line_ids']

            vals.pop('invoice_line_ids',None)

            move=self_ctx.new(vals)
            new_vals_list.append(move._move_autocomplete_invoice_lines_values())

        returnnew_vals_list

    def_move_autocomplete_invoice_lines_write(self,vals):
        '''Duringthewriteofanaccount.movewithonly'invoice_line_ids'setandnot'line_ids',thismethodiscalled
        toautocomputeaccountinglinesoftheinvoice.Inthatcase,accountswillberetrievedandtaxes,cashrounding
        andpaymenttermswillbecomputed.Attheend,thevalueswillcontainsallaccountinglinesin'line_ids'
        andthemovesshouldbebalanced.

        :paramvals_list:  Apythondictrepresentingthevaluestowrite.
        :return:           Trueiftheauto-completiondidsomething,Falseotherwise.
        '''
        enable_autocomplete='invoice_line_ids'invalsand'line_ids'notinvalsandTrueorFalse

        ifnotenable_autocomplete:
            returnFalse

        vals['line_ids']=vals.pop('invoice_line_ids')
        forinvoiceinself:
            invoice_new=invoice.with_context(default_move_type=invoice.move_type,default_journal_id=invoice.journal_id.id).new(origin=invoice)
            invoice_new.update(vals)
            values=invoice_new._move_autocomplete_invoice_lines_values()
            values.pop('invoice_line_ids',None)
            invoice.write(values)
        returnTrue

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        default=dict(defaultor{})
        if(fields.Date.to_date(default.get('date'))orself.date)<=self.company_id._get_user_fiscal_lock_date():
            default['date']=self.company_id._get_user_fiscal_lock_date()+timedelta(days=1)
        ifself.move_type=='entry':
            default['partner_id']=False
        move=super().copy(default)

        ifmove.is_invoice(include_receipts=True):
            #Makesuretorecomputepaymentterms.Thiscouldbenecessaryifthedateisdifferentforexample.
            #Also,thisisnecessarywhencreatingacreditnotebecausethecurrentinvoiceiscopied.

            ifmove.currency_id!=self.company_id.currency_id:
                move.with_context(check_move_validity=False)._onchange_currency()
                move._check_balanced()
            move._recompute_payment_terms_lines()

        returnmove

    @api.model_create_multi
    defcreate(self,vals_list):
        #OVERRIDE
        ifany('state'invalsandvals.get('state')=='posted'forvalsinvals_list):
            raiseUserError(_('Youcannotcreateamovealreadyinthepostedstate.Pleasecreateadraftmoveandpostitafter.'))

        vals_list=self._move_autocomplete_invoice_lines_create(vals_list)
        rslt=super(AccountMove,self).create(vals_list)
        fori,valsinenumerate(vals_list):
            if'line_ids'invals:
                rslt[i].update_lines_tax_exigibility()
        returnrslt

    defwrite(self,vals):
        formoveinself:
            if(move.restrict_mode_hash_tableandmove.state=="posted"andset(vals).intersection(move._get_integrity_hash_fields())):
                raiseUserError(_("Youcannoteditthefollowingfieldsduetorestrictmodebeingactivatedonthejournal:%s.")%','.join(move._get_integrity_hash_fields()))
            if(move.restrict_mode_hash_tableandmove.inalterable_hashand'inalterable_hash'invals)or(move.secure_sequence_numberand'secure_sequence_number'invals):
                raiseUserError(_('Youcannotoverwritethevaluesensuringtheinalterabilityoftheaccounting.'))
            if(move.posted_beforeand'journal_id'invalsandmove.journal_id.id!=vals['journal_id']):
                raiseUserError(_('Youcannoteditthejournalofanaccountmoveifithasbeenpostedonce.'))
            if(move.nameandmove.name!='/'andmove.sequence_numbernotin(0,1)and'journal_id'invalsandmove.journal_id.id!=vals['journal_id']):
                raiseUserError(_('Youcannoteditthejournalofanaccountmoveifitalreadyhasasequencenumberassigned.'))

            #Youcan'tchangethedateofamovebeinginsidealockedperiod.
            if'date'invalsandmove.date!=vals['date']:
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            #Youcan'tpostsubtractamovetoalockedperiod.
            if'state'invalsandmove.state=='posted'andvals['state']!='posted':
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            ifmove.journal_id.sequence_override_regexandvals.get('name')andvals['name']!='/'andnotre.match(move.journal_id.sequence_override_regex,vals['name']):
                ifnotself.env.user.has_group('account.group_account_manager'):
                    raiseUserError(_('TheJournalEntrysequenceisnotconformtothecurrentformat.OnlytheAdvisorcanchangeit.'))
                move.journal_id.sequence_override_regex=False

        ifself._move_autocomplete_invoice_lines_write(vals):
            res=True
        else:
            vals.pop('invoice_line_ids',None)
            res=super(AccountMove,self.with_context(check_move_validity=False,skip_account_move_synchronization=True)).write(vals)

        #Youcan'tchangethedateofanot-lockedmovetoalockedperiod.
        #Youcan'tpostanewjournalentryinsidealockedperiod.
        if'date'invalsor'state'invals:
            self._check_fiscalyear_lock_date()
            self.mapped('line_ids')._check_tax_lock_date()

        if('state'invalsandvals.get('state')=='posted'):
            formoveinself.filtered(lambdam:m.restrict_mode_hash_tableandnot(m.secure_sequence_numberorm.inalterable_hash)).sorted(lambdam:(m.date,m.refor'',m.id)):
                new_number=move.journal_id.secure_sequence_id.next_by_id()
                vals_hashing={'secure_sequence_number':new_number,
                                'inalterable_hash':move._get_new_hash(new_number)}
                res|=super(AccountMove,move).write(vals_hashing)

        #Ensurethemoveisstillwellbalanced.
        if'line_ids'invals:
            ifself._context.get('check_move_validity',True):
                self._check_balanced()
            self.update_lines_tax_exigibility()

        self._synchronize_business_models(set(vals.keys()))

        returnres

    defunlink(self):
        formoveinself:
            ifmove.posted_beforeandnotself._context.get('force_delete'):
                raiseUserError(_("Youcannotdeleteanentrywhichhasbeenpostedonce."))
        self.line_ids.unlink()
        returnsuper(AccountMove,self).unlink()

    @api.depends('name','state')
    defname_get(self):
        result=[]
        formoveinself:
            ifself._context.get('name_groupby'):
                name='**%s**,%s'%(format_date(self.env,move.date),move._get_move_display_name())
                ifmove.ref:
                    name+='    (%s)'%move.ref
                ifmove.partner_id.name:
                    name+='-%s'%move.partner_id.name
            else:
                name=move._get_move_display_name(show_ref=True)
            result.append((move.id,name))
        returnresult

    def_creation_subtype(self):
        #OVERRIDE
        ifself.move_typein('out_invoice','out_receipt'):
            returnself.env.ref('account.mt_invoice_created')
        else:
            returnsuper(AccountMove,self)._creation_subtype()

    def_track_subtype(self,init_values):
        #OVERRIDEtoaddcustomsubtypedependingofthestate.
        self.ensure_one()

        ifnotself.is_invoice(include_receipts=True):
            returnsuper(AccountMove,self)._track_subtype(init_values)

        if'payment_state'ininit_valuesandself.payment_state=='paid':
            returnself.env.ref('account.mt_invoice_paid')
        elif'state'ininit_valuesandself.state=='posted'andself.is_sale_document(include_receipts=True):
            returnself.env.ref('account.mt_invoice_validated')
        returnsuper(AccountMove,self)._track_subtype(init_values)

    def_creation_message(self):
        #OVERRIDE
        ifnotself.is_invoice(include_receipts=True):
            returnsuper()._creation_message()
        return{
            'out_invoice':_('InvoiceCreated'),
            'out_refund':_('CreditNoteCreated'),
            'in_invoice':_('VendorBillCreated'),
            'in_refund':_('RefundCreated'),
            'out_receipt':_('SalesReceiptCreated'),
            'in_receipt':_('PurchaseReceiptCreated'),
        }[self.move_type]

    #-------------------------------------------------------------------------
    #RECONCILIATIONMETHODS
    #-------------------------------------------------------------------------

    def_collect_tax_cash_basis_values(self):
        '''Collectallinformationneededtocreatethetaxcashbasisjournalentries:
        -Determineifataxcashbasisjournalentryisneeded.
        -Computethelinestobeprocessedandtheamountsneededtocomputeapercentage.
        :return:Adictionary:
            *move:                    Thecurrentaccount.moverecordpassedasparameter.
            *to_process_lines:        Anaccount.move.linerecordsetbeingnotexigibleonthetaxreport.
            *currency:                Thecurrencyonwhichthepercentagehasbeencomputed.
            *total_balance:           sum(payment_term_lines.mapped('balance').
            *total_residual:          sum(payment_term_lines.mapped('amount_residual').
            *total_amount_currency:   sum(payment_term_lines.mapped('amount_currency').
            *total_residual_currency: sum(payment_term_lines.mapped('amount_residual_currency').
            *is_fully_paid:           Aflagindicatingthecurrentmoveisnowfullypaid.
        '''
        self.ensure_one()

        values={
            'move':self,
            'to_process_lines':self.env['account.move.line'],
            'total_balance':0.0,
            'total_residual':0.0,
            'total_amount_currency':0.0,
            'total_residual_currency':0.0,
        }

        currencies=set()
        has_term_lines=False
        forlineinself.line_ids:
            ifline.account_internal_typein('receivable','payable'):
                sign=1ifline.balance>0.0else-1

                currencies.add(line.currency_idorline.company_currency_id)
                has_term_lines=True
                values['total_balance']+=sign*line.balance
                values['total_residual']+=sign*line.amount_residual
                values['total_amount_currency']+=sign*line.amount_currency
                values['total_residual_currency']+=sign*line.amount_residual_currency

            elifnotline.tax_exigible:

                values['to_process_lines']+=line
                currencies.add(line.currency_idorline.company_currency_id)

        ifnotvalues['to_process_lines']ornothas_term_lines:
            returnNone

        #Computethecurrencyonwhichmadethepercentage.
        iflen(currencies)==1:
            values['currency']=list(currencies)[0]
        else:
            #Don'tsupportthecasewherethereismultipleinvolvedcurrencies.
            returnNone

        #Determineisthemoveisnowfullypaid.
        values['is_fully_paid']=self.company_id.currency_id.is_zero(values['total_residual'])\
                                  orvalues['currency'].is_zero(values['total_residual_currency'])

        returnvalues

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------

    @api.model
    defget_invoice_types(self,include_receipts=False):
        return['out_invoice','out_refund','in_refund','in_invoice']+(include_receiptsand['out_receipt','in_receipt']or[])

    defis_invoice(self,include_receipts=False):
        returnself.move_typeinself.get_invoice_types(include_receipts)

    @api.model
    defget_sale_types(self,include_receipts=False):
        return['out_invoice','out_refund']+(include_receiptsand['out_receipt']or[])

    defis_sale_document(self,include_receipts=False):
        returnself.move_typeinself.get_sale_types(include_receipts)

    @api.model
    defget_purchase_types(self,include_receipts=False):
        return['in_invoice','in_refund']+(include_receiptsand['in_receipt']or[])

    defis_purchase_document(self,include_receipts=False):
        returnself.move_typeinself.get_purchase_types(include_receipts)

    @api.model
    defget_inbound_types(self,include_receipts=True):
        return['out_invoice','in_refund']+(include_receiptsand['out_receipt']or[])

    defis_inbound(self,include_receipts=True):
        returnself.move_typeinself.get_inbound_types(include_receipts)

    @api.model
    defget_outbound_types(self,include_receipts=True):
        return['in_invoice','out_refund']+(include_receiptsand['in_receipt']or[])

    defis_outbound(self,include_receipts=True):
        returnself.move_typeinself.get_outbound_types(include_receipts)

    def_affect_tax_report(self):
        returnany(line._affect_tax_report()forlineinself.line_ids)

    def_get_invoice_reference_euro_invoice(self):
        """ThiscomputesthereferencebasedontheRFCreditorReference.
            Thedataofthereferenceisthedatabaseidnumberoftheinvoice.
            Forinstance,ifaninvoiceisissuedwithid43,thechecknumber
            is07sothereferencewillbe'RF0743'.
        """
        self.ensure_one()
        base=self.id
        check_digits=calc_check_digits('{}RF'.format(base))
        reference='RF{}{}'.format(check_digits,"".join(["".join(x)forxinzip_longest(*[iter(str(base))]*4,fillvalue="")]))
        returnreference

    def_get_invoice_reference_euro_partner(self):
        """ThiscomputesthereferencebasedontheRFCreditorReference.
            Thedataofthereferenceistheuserdefinedreferenceofthe
            partnerorthedatabaseidnumberoftheparter.
            Forinstance,ifaninvoiceisissuedforthepartnerwithinternal
            reference'foodbuyer654',thedigitswillbeextractedandusedas
            thedata.Thiswillleadtoachecknumberequalto00andthe
            referencewillbe'RF00654'.
            Ifnoreferenceissetforthepartner,itsidinthedatabasewill
            beused.
        """
        self.ensure_one()
        partner_ref=self.partner_id.ref
        partner_ref_nr=re.sub('\D','',partner_refor'')[-21:]orstr(self.partner_id.id)[-21:]
        partner_ref_nr=partner_ref_nr[-21:]
        check_digits=calc_check_digits('{}RF'.format(partner_ref_nr))
        reference='RF{}{}'.format(check_digits,"".join(["".join(x)forxinzip_longest(*[iter(partner_ref_nr)]*4,fillvalue="")]))
        returnreference

    def_get_invoice_reference_flectra_invoice(self):
        """ThiscomputesthereferencebasedontheFlectraformat.
            Wesimplyreturnthenumberoftheinvoice,definedonthejournal
            sequence.
        """
        self.ensure_one()
        returnself.name

    def_get_invoice_reference_flectra_partner(self):
        """ThiscomputesthereferencebasedontheFlectraformat.
            Thedatausedisthereferencesetonthepartneroritsdatabase
            idotherwise.Forinstanceifthereferenceofthecustomeris
            'dumbcustomer97',thereferencewillbe'CUST/dumbcustomer97'.
        """
        ref=self.partner_id.reforstr(self.partner_id.id)
        prefix=_('CUST')
        return'%s/%s'%(prefix,ref)

    def_get_invoice_computed_reference(self):
        self.ensure_one()
        ifself.journal_id.invoice_reference_type=='none':
            return''
        else:
            ref_function=getattr(self,'_get_invoice_reference_{}_{}'.format(self.journal_id.invoice_reference_model,self.journal_id.invoice_reference_type))
            ifref_function:
                returnref_function()
            else:
                raiseUserError(_('Thecombinationofreferencemodelandreferencetypeonthejournalisnotimplemented'))

    def_get_move_display_name(self,show_ref=False):
        '''Helpertogetthedisplaynameofaninvoicedependingofitstype.
        :paramshow_ref:   Aflagindicatingofthedisplaynamemustincludeornotthejournalentryreference.
        :return:           Astringrepresentingtheinvoice.
        '''
        self.ensure_one()
        draft_name=''
        ifself.state=='draft':
            draft_name+={
                'out_invoice':_('DraftInvoice'),
                'out_refund':_('DraftCreditNote'),
                'in_invoice':_('DraftBill'),
                'in_refund':_('DraftVendorCreditNote'),
                'out_receipt':_('DraftSalesReceipt'),
                'in_receipt':_('DraftPurchaseReceipt'),
                'entry':_('DraftEntry'),
            }[self.move_type]
            ifnotself.nameorself.name=='/':
                draft_name+='(*%s)'%str(self.id)
            else:
                draft_name+=''+self.name
        return(draft_nameorself.name)+(show_refandself.refand'(%s%s)'%(self.ref[:50],'...'iflen(self.ref)>50else'')or'')

    def_get_invoice_delivery_partner_id(self):
        '''Hookallowingtoretrievetherightdeliveryaddressdependingofinstalledmodules.
        :return:Ares.partnerrecord'sidrepresentingthedeliveryaddress.
        '''
        self.ensure_one()
        returnself.partner_id.address_get(['delivery'])['delivery']

    def_get_reconciled_payments(self):
        """Helperusedtoretrievethereconciledpaymentsonthisjournalentry"""
        reconciled_lines=self.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        reconciled_amls=reconciled_lines.mapped('matched_debit_ids.debit_move_id')+\
                          reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        returnreconciled_amls.move_id.payment_id

    def_get_reconciled_statement_lines(self):
        """Helperusedtoretrievethereconciledpaymentsonthisjournalentry"""
        reconciled_lines=self.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        reconciled_amls=reconciled_lines.mapped('matched_debit_ids.debit_move_id')+\
                          reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        returnreconciled_amls.move_id.statement_line_id

    def_get_reconciled_invoices(self):
        """Helperusedtoretrievethereconciledpaymentsonthisjournalentry"""
        reconciled_lines=self.line_ids.filtered(lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
        reconciled_amls=reconciled_lines.mapped('matched_debit_ids.debit_move_id')+\
                          reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        returnreconciled_amls.move_id.filtered(lambdamove:move.is_invoice(include_receipts=True))

    def_get_reconciled_invoices_partials(self):
        '''Helpertoretrievethedetailsaboutreconciledinvoices.
        :returnAlistoftuple(partial,amount,invoice_line).
        '''
        self.ensure_one()
        pay_term_lines=self.line_ids\
            .filtered(lambdaline:line.account_internal_typein('receivable','payable'))
        invoice_partials=[]

        forpartialinpay_term_lines.matched_debit_ids:
            invoice_partials.append((partial,partial.credit_amount_currency,partial.debit_move_id))
        forpartialinpay_term_lines.matched_credit_ids:
            invoice_partials.append((partial,partial.debit_amount_currency,partial.credit_move_id))
        returninvoice_partials

    def_reverse_move_vals(self,default_values,cancel=True):
        '''Reversevaluespassedasparameterbeingthecopiedvaluesoftheoriginaljournalentry.
        Forexample,debit/creditmustbeswitched.Thetaxlinesmustbeeditedincaseofrefunds.

        :paramdefault_values: Acopy_dateoftheoriginaljournalentry.
        :paramcancel:         Aflagindicatingthereverseismadetocanceltheoriginaljournalentry.
        :return:               Theupdateddefault_values.
        '''
        self.ensure_one()

        defcompute_tax_repartition_lines_mapping(move_vals):
            '''Computesandreturnsamappingbetweenthecurrentrepartitionlinestothenewexpectedone.
            :parammove_vals:  Thenewlycreatedinvoiceasapythondictionarytobepassedtothe'create'method.
            :return:           Amapinvoice_repartition_line=>refund_repartition_line.
            '''
            #invoice_repartition_line=>refund_repartition_line
            mapping={}

            forline_commandinmove_vals.get('line_ids',[]):
                line_vals=line_command[2] #(0,0,{...})

                ifline_vals.get('tax_line_id'):
                    #Taxline.
                    tax_ids=[line_vals['tax_line_id']]
                elifline_vals.get('tax_ids')andline_vals['tax_ids'][0][2]:
                    #Baseline.
                    tax_ids=line_vals['tax_ids'][0][2]
                else:
                    continue

                fortaxinself.env['account.tax'].browse(tax_ids).flatten_taxes_hierarchy():
                    forinv_rep_line,ref_rep_lineinzip(tax.invoice_repartition_line_ids,tax.refund_repartition_line_ids):
                        mapping[inv_rep_line]=ref_rep_line
            returnmapping

        definvert_tags_if_needed(repartition_line,tags):
            tax_type=repartition_line.tax_id.type_tax_use
            tags_need_inversion=self._tax_tags_need_inversion(
                self,
                (
                    (tax_type=='purchase'andline_vals['credit']>0)or
                    (tax_type=='sale'andline_vals['debit']>0)
                ),
                tax_type)
            iftags_need_inversion:
                returnself.env['account.move.line']._revert_signed_tags(tags)
            returntags

        move_vals=self.with_context(include_business_fields=True).copy_data(default=default_values)[0]
        #partner_bank_idfieldwillbesetby_compute_partner_bank_id
        if'partner_bank_id'inmove_vals:
            delmove_vals['partner_bank_id']
        is_refund=False
        ifmove_vals['move_type']in('out_refund','in_refund'):
            is_refund=True
        elifmove_vals['move_type']=='entry':
            base_lines=self.line_ids.filtered(lambdaline:line.tax_ids)
            tax_type=set(base_lines.tax_ids.mapped('type_tax_use'))
            iftax_type=={'sale'}andsum(base_lines.mapped('debit'))==0:
                is_refund=True
            eliftax_type=={'purchase'}andsum(base_lines.mapped('credit'))==0:
                is_refund=True

        tax_repartition_lines_mapping=compute_tax_repartition_lines_mapping(move_vals)ifis_refundelse{}

        forline_commandinmove_vals.get('line_ids',[]):
            line_vals=line_command[2] #(0,0,{...})

            #====Inversedebit/credit/amount_currency====
            amount_currency=-line_vals.get('amount_currency',0.0)
            balance=line_vals['credit']-line_vals['debit']

            line_vals.update({
                'amount_currency':amount_currency,
                'debit':balance>0.0andbalanceor0.0,
                'credit':balance<0.0and-balanceor0.0,
            })

            ifnotis_refundorself.tax_cash_basis_move_id:
                #Wedon'tmaptaxrepartitionfornon-refundoperations,norforcashbasisentries.
                #Indeed,cancellingacashbasisentryusuallyhappenswhenunreconcilingandinvoice,
                #inwhichcasewealwayswantthereverseentrytototallycanceltheoriginalone,keepingthesameaccounts,
                #tagsandrepartitionlines
                continue

            #====Maptaxrepartitionlines====
            ifline_vals.get('tax_repartition_line_id'):
                #Taxline.
                invoice_repartition_line=self.env['account.tax.repartition.line'].browse(line_vals['tax_repartition_line_id'])
                ifinvoice_repartition_linenotintax_repartition_lines_mapping:
                    raiseUserError(_("Itseemsthatthetaxeshavebeenmodifiedsincethecreationofthejournalentry.Youshouldcreatethecreditnotemanuallyinstead."))
                refund_repartition_line=tax_repartition_lines_mapping[invoice_repartition_line]

                #Findtherightaccount.
                account_id=self.env['account.move.line']._get_default_tax_account(refund_repartition_line).id
                ifnotaccount_id:
                    ifnotinvoice_repartition_line.account_id:
                        #Keepthecurrentaccountasthecurrentonecomesfromthebaseline.
                        account_id=line_vals['account_id']
                    else:
                        tax=invoice_repartition_line.invoice_tax_id
                        base_line=self.line_ids.filtered(lambdaline:taxinline.tax_ids.flatten_taxes_hierarchy())[0]
                        account_id=base_line.account_id.id

                tags=refund_repartition_line.tag_ids
                ifline_vals.get('tax_ids'):
                    subsequent_taxes=self.env['account.tax'].browse(line_vals['tax_ids'][0][2])
                    tags+=subsequent_taxes.refund_repartition_line_ids.filtered(lambdax:x.repartition_type=='base').tag_ids

                tags=invert_tags_if_needed(refund_repartition_line,tags)
                line_vals.update({
                    'tax_repartition_line_id':refund_repartition_line.id,
                    'account_id':account_id,
                    'tax_tag_ids':[(6,0,tags.ids)],
                })
            elifline_vals.get('tax_ids')andline_vals['tax_ids'][0][2]:
                #Baseline.
                taxes=self.env['account.tax'].browse(line_vals['tax_ids'][0][2]).flatten_taxes_hierarchy()
                invoice_repartition_lines=taxes\
                    .mapped('invoice_repartition_line_ids')\
                    .filtered(lambdaline:line.repartition_type=='base')
                refund_repartition_lines=invoice_repartition_lines\
                    .mapped(lambdaline:tax_repartition_lines_mapping[line])

                tag_ids=[]
                forrefund_repartition_lineinrefund_repartition_lines:
                    tag_ids+=invert_tags_if_needed(refund_repartition_line,refund_repartition_line.tag_ids).ids

                line_vals['tax_tag_ids']=[(6,0,tag_ids)]
        returnmove_vals

    def_reverse_moves(self,default_values_list=None,cancel=False):
        '''Reversearecordsetofaccount.move.
        Ifcancelparameteristrue,thereconcilableorliquiditylines
        ofeachoriginalmovewillbereconciledwithitsreverse's.

        :paramdefault_values_list:Alistofdefaultvaluestoconsiderpermove.
                                    ('type'&'reversed_entry_id'arecomputedinthemethod).
        :return:                   Anaccount.moverecordset,reverseofthecurrentself.
        '''
        ifnotdefault_values_list:
            default_values_list=[{}formoveinself]

        ifcancel:
            lines=self.mapped('line_ids')
            #Avoidmaximumrecursiondepth.
            iflines:
                lines.remove_move_reconcile()

        reverse_type_map={
            'entry':'entry',
            'out_invoice':'out_refund',
            'out_refund':'entry',
            'in_invoice':'in_refund',
            'in_refund':'entry',
            'out_receipt':'entry',
            'in_receipt':'entry',
        }

        move_vals_list=[]
        formove,default_valuesinzip(self,default_values_list):
            default_values.update({
                'move_type':reverse_type_map[move.move_type],
                'reversed_entry_id':move.id,
            })
            move_vals_list.append(move.with_context(move_reverse_cancel=cancel)._reverse_move_vals(default_values,cancel=cancel))

        reverse_moves=self.env['account.move'].create(move_vals_list)
        formove,reverse_moveinzip(self,reverse_moves.with_context(check_move_validity=False,move_reverse_cancel=cancel)):
            #Updateamount_currencyifthedatehaschanged.
            ifmove.date!=reverse_move.date:
                forlineinreverse_move.line_ids:
                    ifline.currency_id:
                        line._onchange_currency()
            reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
        reverse_moves._check_balanced()

        #Reconcilemovestogethertocancelthepreviousone.
        ifcancel:
            reverse_moves.with_context(move_reverse_cancel=cancel)._post(soft=False)
            formove,reverse_moveinzip(self,reverse_moves):
                group=defaultdict(list)
                forlinein(move.line_ids+reverse_move.line_ids).filtered(lambdal:notl.reconciled):
                    group[(line.account_id,line.currency_id)].append(line.id)
                for(account,dummy),line_idsingroup.items():
                    ifaccount.reconcileoraccount.internal_type=='liquidity':
                        self.env['account.move.line'].browse(line_ids).with_context(move_reverse_cancel=cancel).reconcile()

        returnreverse_moves

    defopen_reconcile_view(self):
        returnself.line_ids.open_reconcile_view()

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        #OVERRIDE
        #Addcustombehaviorwhenreceivinganewinvoicethroughthemail'sgateway.
        if(custom_valuesor{}).get('move_type','entry')notin('out_invoice','in_invoice'):
            returnsuper().message_new(msg_dict,custom_values=custom_values)

        company=self.env['res.company'].browse(custom_values['company_id'])ifcustom_values.get('company_id')elseself.env.company

        defis_internal_partner(partner):
            #Helpertoknowifthepartnerisaninternalone.
            returnpartner==company.partner_idor(partner.user_idsandall(user.has_group('base.group_user')foruserinpartner.user_ids))

        extra_domain=False
        ifcustom_values.get('company_id'):
            extra_domain=['|',('company_id','=',custom_values['company_id']),('company_id','=',False)]

        #Searchforpartnersincopy.
        cc_mail_addresses=email_split(msg_dict.get('cc',''))
        followers=[partnerforpartnerinself._mail_find_partner_from_emails(cc_mail_addresses,extra_domain)ifpartner]

        #Searchforpartnerthatsentthemail.
        from_mail_addresses=email_split(msg_dict.get('from',''))
        senders=partners=[partnerforpartnerinself._mail_find_partner_from_emails(from_mail_addresses,extra_domain)ifpartner]

        #Searchforpartnersusingtheuser.
        ifnotsenders:
            senders=partners=list(self._mail_search_on_user(from_mail_addresses))

        ifpartners:
            #Checkwearenotinthecasewhenaninternaluserforwardedthemailmanually.
            ifis_internal_partner(partners[0]):
                #Searchforpartnersinthemail'sbody.
                body_mail_addresses=set(email_re.findall(msg_dict.get('body')))
                partners=[
                    partner
                    forpartnerinself._mail_find_partner_from_emails(body_mail_addresses,extra_domain)
                    ifnotis_internal_partner(partner)andpartner.company_id.idin(False,company.id)
                ]

        #Littlehack:Injectthemail'ssubjectinthebody.
        ifmsg_dict.get('subject')andmsg_dict.get('body'):
            msg_dict['body']='<div><div><h3>%s</h3></div>%s</div>'%(msg_dict['subject'],msg_dict['body'])

        #Createtheinvoice.
        values={
            'name':'/', #wehavetogivethenameotherwiseitwillbesettothemail'ssubject
            'invoice_source_email':from_mail_addresses[0],
            'partner_id':partnersandpartners[0].idorFalse,
        }
        move_ctx=self.with_context(default_move_type=custom_values['move_type'],default_journal_id=custom_values['journal_id'])
        move=super(AccountMove,move_ctx).message_new(msg_dict,custom_values=values)
        move._compute_name() #becausethenameisgiven,weneedtorecomputeincaseitisthefirstinvoiceofthejournal

        #Assignfollowers.
        all_followers_ids=set(partner.idforpartnerinfollowers+senders+partnersifis_internal_partner(partner))
        move.message_subscribe(list(all_followers_ids))
        returnmove

    defpost(self):
        warnings.warn(
            "RedirectWarningmethod'post()'isadeprecatedaliasto'action_post()'or_post()",
            DeprecationWarning,
            stacklevel=2
        )
        returnself.action_post()

    def_post(self,soft=True):
        """Post/Validatethedocuments.

        Postingthedocumentswillgiveitanumber,andcheckthatthedocumentis
        complete(somefieldsmightnotberequiredifnotpostedbutarerequired
        otherwise).
        Ifthejournalislockedwithahashtable,itwillbeimpossibletochange
        somefieldsafterwards.

        :paramsoft(bool):ifTrue,futuredocumentsarenotimmediatelyposted,
            butaresettobeautopostedautomaticallyatthesetaccountingdate.
            Nothingwillbeperformedonthosedocumentsbeforetheaccountingdate.
        :returnModel<account.move>:thedocumentsthathavebeenposted
        """
        ifsoft:
            future_moves=self.filtered(lambdamove:move.date>fields.Date.context_today(self))
            future_moves.auto_post=True
            formoveinfuture_moves:
                msg=_('Thismovewillbepostedattheaccountingdate:%(date)s',date=format_date(self.env,move.date))
                move.message_post(body=msg)
            to_post=self-future_moves
        else:
            to_post=self

        #`user_has_group`won'tbebypassedby`sudo()`sinceitdoesn'tchangetheuseranymore.
        ifnotself.env.suandnotself.env.user.has_group('account.group_account_invoice'):
            raiseAccessError(_("Youdon'thavetheaccessrightstopostaninvoice."))
        formoveinto_post:
            ifmove.partner_bank_idandnotmove.partner_bank_id.active:
                raiseUserError(_("Therecipientbankaccountlinktothisinvoiceisarchived.\nSoyoucannotconfirmtheinvoice."))
            ifmove.state=='posted':
                raiseUserError(_('Theentry%s(id%s)isalreadyposted.')%(move.name,move.id))
            ifnotmove.line_ids.filtered(lambdaline:notline.display_type):
                raiseUserError(_('Youneedtoaddalinebeforeposting.'))
            ifmove.auto_postandmove.date>fields.Date.context_today(self):
                date_msg=move.date.strftime(get_lang(self.env).date_format)
                raiseUserError(_("Thismoveisconfiguredtobeauto-postedon%s",date_msg))

            ifnotmove.partner_id:
                ifmove.is_sale_document():
                    raiseUserError(_("Thefield'Customer'isrequired,pleasecompleteittovalidatetheCustomerInvoice."))
                elifmove.is_purchase_document():
                    raiseUserError(_("Thefield'Vendor'isrequired,pleasecompleteittovalidatetheVendorBill."))

            ifmove.is_invoice(include_receipts=True)andfloat_compare(move.amount_total,0.0,precision_rounding=move.currency_id.rounding)<0:
                raiseUserError(_("Youcannotvalidateaninvoicewithanegativetotalamount.Youshouldcreateacreditnoteinstead.Usetheactionmenutotransformitintoacreditnoteorrefund."))

            ifmove.line_ids.account_id.filtered(lambdaaccount:account.deprecated):
                raiseUserError(_("Alineofthismoveisusingadeprecatedaccount,youcannotpostit."))

            #Handlecasewhentheinvoice_dateisnotset.Inthatcase,theinvoice_dateissetattodayandthen,
            #linesarerecomputedaccordingly.
            #/!\'check_move_validity'mustbetheresincethedynamiclineswillberecomputedoutsidethe'onchange'
            #environment.
            ifnotmove.invoice_date:
                ifmove.is_sale_document(include_receipts=True):
                    move.invoice_date=fields.Date.context_today(self)
                    move.with_context(check_move_validity=False)._onchange_invoice_date()
                elifmove.is_purchase_document(include_receipts=True):
                    raiseUserError(_("TheBill/Refunddateisrequiredtovalidatethisdocument."))

            #Whentheaccountingdateispriortothetaxlockdate,moveitautomaticallytothenextavailabledate.
            #/!\'check_move_validity'mustbetheresincethedynamiclineswillberecomputedoutsidethe'onchange'
            #environment.
            if(move.company_id.tax_lock_dateandmove.date<=move.company_id.tax_lock_date)and(move.line_ids.tax_idsormove.line_ids.tax_tag_ids):
                move.date=move._get_accounting_date(move.invoice_dateormove.date,True)
                move.with_context(check_move_validity=False)._onchange_currency()


        formoveinto_post:
            #FixinconsistenciesthatmayoccureiftheOCRhasbeeneditingtheinvoiceatthesametimeofauser.Weforcethe
            #partneronthelinestobethesameastheoneonthemove,becausethat'stheonlyonetheusercansee/edit.
            wrong_lines=move.is_invoice()andmove.line_ids.filtered(lambdaaml:aml.partner_id!=move.commercial_partner_idandnotaml.display_type)
            ifwrong_lines:
                wrong_lines.partner_id=move.commercial_partner_id.id

        #Createtheanalyticlinesinbatchisfasterasitleadstolesscacheinvalidation.
        to_post.mapped('line_ids').create_analytic_lines()
        to_post.write({
            'state':'posted',
            'posted_before':True,
        })

        formoveinto_post:
            move.message_subscribe([p.idforpin[move.partner_id]ifpnotinmove.sudo().message_partner_ids])


        formoveinto_post:
            ifmove.is_sale_document()\
                    andmove.journal_id.sale_activity_type_id\
                    and(move.journal_id.sale_activity_user_idormove.invoice_user_id).idnotin(self.env.ref('base.user_root').id,False):
                move.activity_schedule(
                    date_deadline=min((datefordateinmove.line_ids.mapped('date_maturity')ifdate),default=move.date),
                    activity_type_id=move.journal_id.sale_activity_type_id.id,
                    summary=move.journal_id.sale_activity_note,
                    user_id=move.journal_id.sale_activity_user_id.idormove.invoice_user_id.id,
                )

        customer_count,supplier_count=defaultdict(int),defaultdict(int)
        formoveinto_post:
            ifmove.is_sale_document():
                customer_count[move.partner_id]+=1
            elifmove.is_purchase_document():
                supplier_count[move.partner_id]+=1
        forpartner,countincustomer_count.items():
            (partner|partner.commercial_partner_id)._increase_rank('customer_rank',count)
        forpartner,countinsupplier_count.items():
            (partner|partner.commercial_partner_id)._increase_rank('supplier_rank',count)

        #Triggeractionforpaidinvoicesinamountiszero
        to_post.filtered(
            lambdam:m.is_invoice(include_receipts=True)andm.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        #Forcebalancechecksincenothingpreventsanothermoduletocreateanincorrectentry.
        #Thisisperformedattheveryendtoavoidflushingfieldsbeforethewholeprocessing.
        to_post._check_balanced()
        returnto_post

    def_auto_compute_invoice_reference(self):
        '''Hooktobeoverriddentosetcustomconditionsforauto-computedinvoicereferences.
            :returnTrueifthemoveshouldgetaauto-computedreferenceelseFalse
            :rtypebool
        '''
        self.ensure_one()
        returnself.move_type=='out_invoice'andnotself.payment_reference

    defaction_reverse(self):
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_view_account_move_reversal")

        ifself.is_invoice():
            action['name']=_('CreditNote')

        returnaction

    defaction_post(self):
        self._post(soft=False)
        returnFalse

    defjs_assign_outstanding_line(self,line_id):
        '''Calledbythe'payment'widgettoreconcileasuggestedjournalitemtothepresent
        invoice.

        :paramline_id:Theidofthelinetoreconcilewiththecurrentinvoice.
        '''
        self.ensure_one()
        lines=self.env['account.move.line'].browse(line_id)
        lines+=self.line_ids.filtered(lambdaline:line.account_id==lines[0].account_idandnotline.reconciled)
        returnlines.reconcile()

    defjs_remove_outstanding_partial(self,partial_id):
        '''Calledbythe'payment'widgettoremoveareconciledentrytothepresentinvoice.

        :parampartial_id:Theidofanexistingpartialreconciledwiththecurrentinvoice.
        '''
        self.ensure_one()
        partial=self.env['account.partial.reconcile'].browse(partial_id)
        returnpartial.unlink()

    @api.model
    defsetting_upload_bill_wizard(self):
        """Calledbythe'FirstBill'buttonofthesetupbar."""
        self.env.company.sudo().set_onboarding_step_done('account_setup_bill_state')

        new_wizard=self.env['account.tour.upload.bill'].create({})
        view_id=self.env.ref('account.account_tour_upload_bill').id

        return{
            'type':'ir.actions.act_window',
            'name':_('Importyourfirstbill'),
            'view_mode':'form',
            'res_model':'account.tour.upload.bill',
            'target':'new',
            'res_id':new_wizard.id,
            'views':[[view_id,'form']],
        }

    defbutton_draft(self):
        AccountMoveLine=self.env['account.move.line']
        excluded_move_ids=[]

        ifself._context.get('suspense_moves_mode'):
            excluded_move_ids=AccountMoveLine.search(AccountMoveLine._get_suspense_moves_domain()+[('move_id','in',self.ids)]).mapped('move_id').ids

        formoveinself:
            ifmoveinmove.line_ids.mapped('full_reconcile_id.exchange_move_id'):
                raiseUserError(_('Youcannotresettodraftanexchangedifferencejournalentry.'))
            ifmove.tax_cash_basis_rec_id:
                raiseUserError(_('Youcannotresettodraftataxcashbasisjournalentry.'))
            ifmove.restrict_mode_hash_tableandmove.state=='posted'andmove.idnotinexcluded_move_ids:
                raiseUserError(_('Youcannotmodifyapostedentryofthisjournalbecauseitisinstrictmode.'))
            #Weremovealltheanalyticsentriesforthisjournal
            move.mapped('line_ids.analytic_line_ids').unlink()

        self.mapped('line_ids').remove_move_reconcile()
        self.write({'state':'draft','is_move_sent':False})

    defbutton_cancel(self):
        self.write({'auto_post':False,'state':'cancel'})

    defaction_invoice_sent(self):
        """Openawindowtocomposeanemail,withtheediinvoicetemplate
            messageloadedbydefault
        """
        self.ensure_one()
        template=self.env.ref('account.email_template_edi_invoice',raise_if_not_found=False)
        lang=False
        iftemplate:
            lang=template._render_lang(self.ids)[self.id]
        ifnotlang:
            lang=get_lang(self.env).code
        compose_form=self.env.ref('account.account_invoice_send_wizard_form',raise_if_not_found=False)
        ctx=dict(
            default_model='account.move',
            default_res_id=self.id,
            #Forthesakeofconsistencyweneedadefault_res_modelif
            #default_res_idisset.Notrenamingdefault_modelasitcan
            #createmanyside-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=templateandtemplate.idorFalse,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return{
            'name':_('SendInvoice'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'account.invoice.send',
            'views':[(compose_form.id,'form')],
            'view_id':compose_form.id,
            'target':'new',
            'context':ctx,
        }

    def_get_integrity_hash_fields(self):
        #Usethelatesthashversionbydefault,butkeeptheoldoneforbackwardcompatibilitywhengeneratingtheintegrityreport.
        hash_version=self._context.get('hash_version',MAX_HASH_VERSION)
        ifhash_version==1:
            return['date','journal_id','company_id']
        elifhash_version==MAX_HASH_VERSION:
            return['name','date','journal_id','company_id']
        raiseNotImplementedError(f"hash_version={hash_version}doesn'texist")

    def_get_integrity_hash_fields_and_subfields(self):
        returnself._get_integrity_hash_fields()+[f'line_ids.{subfield}'forsubfieldinself.line_ids._get_integrity_hash_fields()]

    def_get_new_hash(self,secure_seq_number):
        """Returnsthehashtowriteonjournalentrieswhentheygetposted"""
        self.ensure_one()
        #gettheonlyoneexactpreviousmoveinthesecurisationsequence
        prev_move=self.sudo().search([('state','=','posted'),
                                 ('company_id','=',self.company_id.id),
                                 ('journal_id','=',self.journal_id.id),
                                 ('secure_sequence_number','!=',0),
                                 ('secure_sequence_number','=',int(secure_seq_number)-1)])
        ifprev_moveandlen(prev_move)!=1:
            raiseUserError(
               _('Anerroroccuredwhencomputingtheinalterability.Impossibletogettheuniquepreviouspostedjournalentry.'))

        #buildandreturnthehash
        returnself._compute_hash(prev_move.inalterable_hashifprev_moveelseu'')

    def_compute_hash(self,previous_hash):
        """Computesthehashofthebrowse_recordgivenasself,basedonthehash
        ofthepreviousrecordinthecompany'ssecurisationsequencegivenasparameter"""
        self.ensure_one()
        hash_string=sha256((previous_hash+self.string_to_hash).encode('utf-8'))
        returnhash_string.hexdigest()

    @api.depends(lambdaself:self._get_integrity_hash_fields_and_subfields())
    @api.depends_context('hash_version')
    def_compute_string_to_hash(self):
        def_getattrstring(obj,field_str):
            field_value=obj[field_str]
            ifobj._fields[field_str].type=='many2one':
                field_value=field_value.id
            returnstr(field_value)

        formoveinself:
            values={}
            forfieldinmove._get_integrity_hash_fields():
                values[field]=_getattrstring(move,field)

            forlineinmove.line_ids:
                forfieldinline._get_integrity_hash_fields():
                    k='line_%d_%s'%(line.id,field)
                    values[k]=_getattrstring(line,field)
            #makethejsonserializationcanonical
            # (https://tools.ietf.org/html/draft-staykov-hu-json-canonical-form-00)
            move.string_to_hash=dumps(values,sort_keys=True,
                                                ensure_ascii=True,indent=None,
                                                separators=(',',':'))

    defaction_invoice_print(self):
        """Printtheinvoiceandmarkitassent,sothatwecanseemore
            easilythenextstepoftheworkflow
        """
        ifany(notmove.is_invoice(include_receipts=True)formoveinself):
            raiseUserError(_("Onlyinvoicescouldbeprinted."))

        self.filtered(lambdainv:notinv.is_move_sent).write({'is_move_sent':True})
        ifself.user_has_groups('account.group_account_invoice'):
            returnself.env.ref('account.account_invoices').report_action(self)
        else:
            returnself.env.ref('account.account_invoices_without_payment').report_action(self)

    defaction_invoice_paid(self):
        '''Hooktobeoverridedcalledwhentheinvoicemovestothepaidstate.'''
        pass

    defaction_register_payment(self):
        '''Opentheaccount.payment.registerwizardtopaytheselectedjournalentries.
        :return:Anactionopeningtheaccount.payment.registerwizard.
        '''
        return{
            'name':_('RegisterPayment'),
            'res_model':'account.payment.register',
            'view_mode':'form',
            'context':{
                'active_model':'account.move',
                'active_ids':self.ids,
            },
            'target':'new',
            'type':'ir.actions.act_window',
        }

    defaction_switch_invoice_into_refund_credit_note(self):
        ifany(move.move_typenotin('in_invoice','out_invoice')formoveinself):
            raiseValidationError(_("Thisactionisn'tavailableforthisdocument."))

        formoveinself:
            reversed_move=move._reverse_move_vals({},False)
            new_invoice_line_ids=[]
            forcmd,virtualid,line_valsinreversed_move['line_ids']:
                ifnotline_vals['exclude_from_invoice_tab']:
                    new_invoice_line_ids.append((0,0,line_vals))
            ifmove.amount_total<0:
                #Inverseallinvoice_line_ids
                forcmd,virtualid,line_valsinnew_invoice_line_ids:
                    line_vals.update({
                        'quantity':-line_vals['quantity'],
                        'amount_currency':-line_vals['amount_currency'],
                        'debit':line_vals['credit'],
                        'credit':line_vals['debit']
                    })
            move.write({
                'move_type':move.move_type.replace('invoice','refund'),
                'invoice_line_ids':[(5,0,0)],
            })
            move.write({'invoice_line_ids':new_invoice_line_ids})

    def_get_report_base_filename(self):
        returnself._get_move_display_name()

    def_get_name_invoice_report(self):
        """Thismethodneedtobeinheritbythelocalizationsiftheywanttoprintacustominvoicereportinsteadof
        thedefaultone.Forexamplepleasereviewthel10n_armodule"""
        self.ensure_one()
        return'account.report_invoice_document'

    defpreview_invoice(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'self',
            'url':self.get_portal_url(),
        }

    def_compute_access_url(self):
        super(AccountMove,self)._compute_access_url()
        formoveinself.filtered(lambdamove:move.is_invoice()):
            move.access_url='/my/invoices/%s'%(move.id)

    @api.depends('line_ids')
    def_compute_has_reconciled_entries(self):
        formoveinself:
            move.has_reconciled_entries=len(move.line_ids._reconciled_lines())>1

    @api.depends('company_id')
    def_compute_display_qr_code(self):
        forrecordinself:
            record.display_qr_code=(
                record.move_typein('out_invoice','out_receipt','in_invoice','in_receipt')
                andrecord.company_id.qr_code
            )

    defaction_view_reverse_entry(self):
        self.ensure_one()

        #Createaction.
        action={
            'name':_('ReverseMoves'),
            'type':'ir.actions.act_window',
            'res_model':'account.move',
        }
        reverse_entries=self.env['account.move'].search([('reversed_entry_id','=',self.id)])
        iflen(reverse_entries)==1:
            action.update({
                'view_mode':'form',
                'res_id':reverse_entries.id,
            })
        else:
            action.update({
                'view_mode':'tree',
                'domain':[('id','in',reverse_entries.ids)],
            })
        returnaction

    @api.model
    def_autopost_draft_entries(self):
        '''Thismethodiscalledfromacronjob.
        Itisusedtopostentriessuchasthosecreatedbythemodule
        account_asset.
        '''
        records=self.search([
            ('state','=','draft'),
            ('date','<=',fields.Date.context_today(self)),
            ('auto_post','=',True),
        ])

        foridsinself._cr.split_for_in_conditions(records.ids,size=100):
            moves=self.browse(ids)
            try: #trypostinginbatch
                withself.env.cr.savepoint():
                    moves._post()
            exceptUserError: #ifatleastonemovecannotbeposted,handlemovesonebyone
                formoveinmoves:
                    try:
                        withself.env.cr.savepoint():
                            move._post()
                    exceptUserErrorase:
                        move.to_check=True
                        msg=_('Themovecouldnotbepostedforthefollowingreason:%(error_message)s',error_message=e)
                        move.message_post(body=msg,
                                          message_type='comment',
                                          author_id=self.env.ref('base.partner_root').id)

            ifnotself.env.registry.in_test_mode():
                self._cr.commit()

    #offerthepossibilitytoduplicatethankstoabuttoninsteadofahiddenmenu,whichismorevisible
    defaction_duplicate(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['context']=dict(self.env.context)
        action['context']['form_view_initial_mode']='edit'
        action['context']['view_no_maturity']=False
        action['views']=[(self.env.ref('account.view_move_form').id,'form')]
        action['res_id']=self.copy().id
        returnaction

    @api.model
    def_move_dict_to_preview_vals(self,move_vals,currency_id=None):
        preview_vals={
            'group_name':"%s,%s"%(format_date(self.env,move_vals['date'])or_('[Notset]'),move_vals['ref']),
            'items_vals':move_vals['line_ids'],
        }
        forlineinpreview_vals['items_vals']:
            if'partner_id'inline[2]:
                #sudoisneededtocomputedisplay_nameinamulticompaniesenvironment
                line[2]['partner_id']=self.env['res.partner'].browse(line[2]['partner_id']).sudo().display_name
            line[2]['account_id']=self.env['account.account'].browse(line[2]['account_id']).display_nameor_('DestinationAccount')
            line[2]['debit']=currency_idandformatLang(self.env,line[2]['debit'],currency_obj=currency_id)orline[2]['debit']
            line[2]['credit']=currency_idandformatLang(self.env,line[2]['credit'],currency_obj=currency_id)orline[2]['debit']
        returnpreview_vals

    defgenerate_qr_code(self):
        """GeneratesandreturnsaQR-codegenerationURLforthisinvoice,
        raisinganerrormessageifsomethingismisconfigured.

        ThechosenQRgenerationmethodistheonesetinqr_methodfieldifthereisone,
        orthefirsteligibleonefound.Ifthissearchhadtobeperformedand
        andeligiblemethodwasfound,qr_methodfieldissettothismethodbefore
        returningtheURL.IfnoeligibleQRmethodcouldbefound,wereturnNone.
        """
        self.ensure_one()

        ifnotself.display_qr_code:
            returnNone

        qr_code_method=self.qr_code_method
        ifqr_code_method:
            #Iftheusersetaqrcodegeneratormanually,wecheckthatwecanuseit
            ifnotself.partner_bank_id._eligible_for_qr_code(self.qr_code_method,self.partner_id,self.currency_id):
                raiseUserError(_("ThechosenQR-codetypeisnoteligibleforthisinvoice."))
        else:
            #Elsewefindonethat'seligibleandassignittotheinvoice
            forcandidate_method,candidate_nameinself.env['res.partner.bank'].get_available_qr_methods_in_sequence():
                ifself.partner_bank_id._eligible_for_qr_code(candidate_method,self.partner_id,self.currency_id):
                    qr_code_method=candidate_method
                    break

        ifnotqr_code_method:
            #Noeligiblemethodcouldbefound;wecan'tgeneratetheQR-code
            returnNone

        unstruct_ref=self.refifself.refelseself.name
        rslt=self.partner_bank_id.build_qr_code_base64(self.amount_residual,unstruct_ref,self.payment_reference,self.currency_id,self.partner_id,qr_code_method,silent_errors=False)

        #Weonlysetqr_code_methodaftergeneratingtheurl;otherwise,it
        #couldbesetevenincaseofafailureintheQRcodegeneration
        #(whichwouldchangethefield,butnotrefreshUI,makingthedisplayeddatainconsistentwithdb)
        self.qr_code_method=qr_code_method

        returnrslt

    @contextmanager
    def_disable_discount_precision(self):
        """Disabletheuserdefinedprecisionfordiscounts.
        Thisisusefulforimportingdocumentscomingfromothersoftwaresandproviders.
        Thereasonningisthatifthedocumentthatweareimportinghasadiscount,it
        shouldn'tberoundedtothelocalsettings.
        """
        original_precision_get=DecimalPrecision.precision_get
        defprecision_get(self,application):
            ifapplication=='Discount':
                return100
            returnoriginal_precision_get(self,application)
        withpatch('flectra.addons.base.models.decimal_precision.DecimalPrecision.precision_get',new=precision_get):
            yield

    def_message_post_after_hook(self,new_message,message_values):
        #OVERRIDE
        #Whenpostingamessage,checktheattachmenttoseeifit'saninvoiceandupdatewiththeimporteddata.
        res=super()._message_post_after_hook(new_message,message_values)

        attachments=new_message.attachment_ids
        iflen(self)!=1ornotattachmentsorself.env.context.get('no_new_invoice')ornotself.is_invoice(include_receipts=True):
            returnres

        flectrabot=self.env.ref('base.partner_root')
        ifattachmentsandself.state!='draft':
            self.message_post(body=_('Theinvoiceisnotadraft,itwasnotupdatedfromtheattachment.'),
                              message_type='comment',
                              subtype_xmlid='mail.mt_note',
                              author_id=flectrabot.id)
            returnres
        ifattachmentsandself.line_ids:
            self.message_post(body=_('Theinvoicealreadycontainslines,itwasnotupdatedfromtheattachment.'),
                              message_type='comment',
                              subtype_xmlid='mail.mt_note',
                              author_id=flectrabot.id)
            returnres

        decoders=self.env['account.move']._get_update_invoice_from_attachment_decoders(self)
        fordecoderinsorted(decoders,key=lambdad:d[0]):
            #startwithmessage_main_attachment_id,thatwayifOCRisinstalled,onlythatonewillbeparsed.
            #thisisbasedonthefactthattheocrwillbethelastdecoder.
            forattachmentinattachments.sorted(lambdax:x!=self.message_main_attachment_id):
                withself._disable_discount_precision():
                    invoice=decoder[1](attachment,self)
                    ifinvoice:
                        returnres

        returnres

    def_get_create_invoice_from_attachment_decoders(self):
        """Returnsalistofmethodthatareabletocreateaninvoicefromanattachmentandapriority.

        :returns:  Alistoftuples(priority,method)wheremethodtakesanattachmentasparameter.
        """
        return[]

    def_get_update_invoice_from_attachment_decoders(self,invoice):
        """Returnsalistofmethodthatareabletocreateaninvoicefromanattachmentandapriority.

        :paraminvoice:Theinvoiceonwhichtoupdatethedata.
        :returns:      Alistoftuples(priority,method)wheremethodtakesanattachmentasparameter.
        """
        return[]

    def_notify_get_groups(self,msg_vals=None):
        """Giveaccessbuttontousersandportalcustomerasportalisintegrated
        inaccount.Customerandportalgrouphaveprobablynorighttosee
        thedocumentsotheydon'thavetheaccessbutton."""
        groups=super(AccountMove,self)._notify_get_groups(msg_vals=msg_vals)

        self.ensure_one()
        ifself.move_type!='entry':
            forgroup_name,_group_method,group_dataingroups:
                ifgroup_namein('portal_customer','customer'):
                    group_data['has_button_access']=True

                    #'notification_is_customer'isusedtodeterminewhetherthegroupshouldbesenttheaccess_token
                    group_data['notification_is_customer']=True

        returngroups

    def_is_downpayment(self):
        '''Returntrueiftheinvoiceisadownpayment.
        Down-paymentscanbecreatedfromasaleorder.Thismethodisoverriddeninthesaleordermodule.
        '''
        returnFalse


classAccountMoveLine(models.Model):
    _name="account.move.line"
    _description="JournalItem"
    _order="datedesc,move_namedesc,id"
    _check_company_auto=True

    #====Businessfields====
    move_id=fields.Many2one('account.move',string='JournalEntry',
        index=True,required=True,readonly=True,auto_join=True,ondelete="cascade",
        check_company=True,
        help="Themoveofthisentryline.")
    move_name=fields.Char(string='Number',related='move_id.name',store=True,index=True)
    date=fields.Date(related='move_id.date',store=True,readonly=True,index=True,copy=False,group_operator='min')
    ref=fields.Char(related='move_id.ref',store=True,copy=False,index=True,readonly=True)
    parent_state=fields.Selection(related='move_id.state',store=True,readonly=True)
    journal_id=fields.Many2one(related='move_id.journal_id',store=True,index=True,copy=False)
    company_id=fields.Many2one(related='move_id.company_id',store=True,readonly=True,default=lambdaself:self.env.company)
    company_currency_id=fields.Many2one(related='company_id.currency_id',string='CompanyCurrency',
        readonly=True,store=True,
        help='Utilityfieldtoexpressamountcurrency')
    tax_fiscal_country_id=fields.Many2one(comodel_name='res.country',related='move_id.company_id.account_tax_fiscal_country_id')
    account_id=fields.Many2one('account.account',string='Account',
        index=True,ondelete="cascade",
        domain="[('deprecated','=',False),('company_id','=','company_id'),('is_off_balance','=',False)]",
        check_company=True,
        tracking=True)
    account_internal_type=fields.Selection(related='account_id.user_type_id.type',string="InternalType",readonly=True)
    account_internal_group=fields.Selection(related='account_id.user_type_id.internal_group',string="InternalGroup",readonly=True)
    account_root_id=fields.Many2one(related='account_id.root_id',string="AccountRoot",store=True,readonly=True)
    sequence=fields.Integer(default=10)
    name=fields.Char(string='Label',tracking=True,compute='_compute_name',store=True,readonly=False)
    quantity=fields.Float(string='Quantity',
        default=lambdaself:0ifself._context.get('default_display_type')else1.0,digits='ProductUnitofMeasure',
        help="Theoptionalquantityexpressedbythisline,eg:numberofproductsold."
             "Thequantityisnotalegalrequirementbutisveryusefulforsomereports.")
    price_unit=fields.Float(string='UnitPrice',digits='ProductPrice')
    discount=fields.Float(string='Discount(%)',digits='Discount',default=0.0)
    debit=fields.Monetary(string='Debit',default=0.0,currency_field='company_currency_id')
    credit=fields.Monetary(string='Credit',default=0.0,currency_field='company_currency_id')
    balance=fields.Monetary(string='Balance',store=True,
        currency_field='company_currency_id',
        compute='_compute_balance',
        help="Technicalfieldholdingthedebit-creditinordertoopenmeaningfulgraphviewsfromreports")
    cumulated_balance=fields.Monetary(string='CumulatedBalance',store=False,
        currency_field='company_currency_id',
        compute='_compute_cumulated_balance',
        help="Cumulatedbalancedependingonthedomainandtheorderchosenintheview.")
    amount_currency=fields.Monetary(string='AmountinCurrency',store=True,copy=True,
        help="Theamountexpressedinanoptionalothercurrencyifitisamulti-currencyentry.")
    price_subtotal=fields.Monetary(string='Subtotal',store=True,readonly=True,
        currency_field='currency_id')
    price_total=fields.Monetary(string='Total',store=True,readonly=True,
        currency_field='currency_id')
    reconciled=fields.Boolean(compute='_compute_amount_residual',store=True)
    blocked=fields.Boolean(string='NoFollow-up',default=False,
        help="Youcancheckthisboxtomarkthisjournalitemasalitigationwiththeassociatedpartner")
    date_maturity=fields.Date(string='DueDate',index=True,tracking=True,
        help="Thisfieldisusedforpayableandreceivablejournalentries.Youcanputthelimitdateforthepaymentofthisline.")
    currency_id=fields.Many2one('res.currency',string='Currency',required=True)
    partner_id=fields.Many2one('res.partner',string='Partner',ondelete='restrict')
    product_uom_id=fields.Many2one('uom.uom',string='UnitofMeasure',domain="[('category_id','=',product_uom_category_id)]")
    product_id=fields.Many2one('product.product',string='Product',ondelete='restrict')
    product_uom_category_id=fields.Many2one('uom.category',related='product_id.uom_id.category_id')

    #====Originfields====
    reconcile_model_id=fields.Many2one('account.reconcile.model',string="ReconciliationModel",copy=False,readonly=True,check_company=True)
    payment_id=fields.Many2one('account.payment',index=True,store=True,
        string="OriginatorPayment",
        related='move_id.payment_id',
        help="Thepaymentthatcreatedthisentry")
    statement_line_id=fields.Many2one('account.bank.statement.line',index=True,store=True,
        string="OriginatorStatementLine",
        related='move_id.statement_line_id',
        help="Thestatementlinethatcreatedthisentry")
    statement_id=fields.Many2one(related='statement_line_id.statement_id',store=True,index=True,copy=False,
        help="Thebankstatementusedforbankreconciliation")

    #====Taxfields====
    tax_ids=fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        context={'active_test':False},
        check_company=True,
        help="Taxesthatapplyonthebaseamount")
    tax_line_id=fields.Many2one('account.tax',string='OriginatorTax',ondelete='restrict',store=True,
        compute='_compute_tax_line_id',help="Indicatesthatthisjournalitemisataxline")
    tax_group_id=fields.Many2one(related='tax_line_id.tax_group_id',string='Originatortaxgroup',
        readonly=True,store=True,
        help='technicalfieldforwidgettax-group-custom-field')
    tax_base_amount=fields.Monetary(string="BaseAmount",store=True,readonly=True,
        currency_field='company_currency_id')
    tax_exigible=fields.Boolean(string='AppearsinVATreport',default=True,readonly=True,
        help="Technicalfieldusedtomarkataxlineasexigibleinthevatreportornot(onlyexigiblejournalitems"
             "aredisplayed).Bydefaultallnewjournalitemsaredirectlyexigible,butwiththefeaturecash_basis"
             "ontaxes,somewillbecomeexigibleonlywhenthepaymentisrecorded.")
    tax_repartition_line_id=fields.Many2one(comodel_name='account.tax.repartition.line',
        string="OriginatorTaxDistributionLine",ondelete='restrict',readonly=True,
        check_company=True,
        help="Taxdistributionlinethatcausedthecreationofthismoveline,ifany")
    tax_tag_ids=fields.Many2many(string="Tags",comodel_name='account.account.tag',ondelete='restrict',context={'active_test':False},
        help="Tagsassignedtothislinebythetaxcreatingit,ifany.Itdeterminesitsimpactonfinancialreports.",tracking=True)
    tax_audit=fields.Char(string="TaxAuditString",compute="_compute_tax_audit",store=True,
        help="Computedfield,listingthetaxgridsimpactedbythisline,andtheamountitappliestoeachofthem.")

    #====Reconciliationfields====
    amount_residual=fields.Monetary(string='ResidualAmount',store=True,
        currency_field='company_currency_id',
        compute='_compute_amount_residual',
        help="Theresidualamountonajournalitemexpressedinthecompanycurrency.")
    amount_residual_currency=fields.Monetary(string='ResidualAmountinCurrency',store=True,
        compute='_compute_amount_residual',
        help="Theresidualamountonajournalitemexpressedinitscurrency(possiblynotthecompanycurrency).")
    full_reconcile_id=fields.Many2one('account.full.reconcile',string="Matching",copy=False,index=True,readonly=True)
    matched_debit_ids=fields.One2many('account.partial.reconcile','credit_move_id',string='MatchedDebits',
        help='Debitjournalitemsthatarematchedwiththisjournalitem.',readonly=True)
    matched_credit_ids=fields.One2many('account.partial.reconcile','debit_move_id',string='MatchedCredits',
        help='Creditjournalitemsthatarematchedwiththisjournalitem.',readonly=True)
    matching_number=fields.Char(string="Matching#",compute='_compute_matching_number',store=True,help="Matchingnumberforthisline,'P'ifitisonlypartiallyreconcile,orthenameofthefullreconcileifitexists.")

    #====Analyticfields====
    analytic_line_ids=fields.One2many('account.analytic.line','move_id',string='Analyticlines')
    analytic_account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',
        index=True,compute="_compute_analytic_account_id",store=True,readonly=False,check_company=True,copy=True)
    analytic_tag_ids=fields.Many2many('account.analytic.tag',string='AnalyticTags',
        compute="_compute_analytic_tag_ids",store=True,readonly=False,check_company=True,copy=True)

    #====Onchange/displaypurposefields====
    recompute_tax_line=fields.Boolean(store=False,readonly=True,
        help="Technicalfieldusedtoknowonwhichlinesthetaxesmustberecomputed.")
    display_type=fields.Selection([
        ('line_section','Section'),
        ('line_note','Note'),
    ],default=False,help="TechnicalfieldforUXpurpose.")
    is_rounding_line=fields.Boolean(help="Technicalfieldusedtoretrievethecashroundingline.")
    exclude_from_invoice_tab=fields.Boolean(help="Technicalfieldusedtoexcludesomelinesfromtheinvoice_line_idstabintheformview.")

    _sql_constraints=[
        (
            'check_credit_debit',
            'CHECK(credit+debit>=0ANDcredit*debit=0)',
            'Wrongcreditordebitvalueinaccountingentry!'
        ),
        (
            'check_accountable_required_fields',
             "CHECK(COALESCE(display_typeIN('line_section','line_note'),'f')ORaccount_idISNOTNULL)",
             "Missingrequiredaccountonaccountableinvoiceline."
        ),
        (
            'check_non_accountable_fields_null',
             "CHECK(display_typeNOTIN('line_section','line_note')OR(amount_currency=0ANDdebit=0ANDcredit=0ANDaccount_idISNULL))",
             "Forbiddenunitprice,accountandquantityonnon-accountableinvoiceline"
        ),
        (
            'check_amount_currency_balance_sign',
            '''CHECK(
                (
                    (currency_id!=company_currency_id)
                    AND
                    (
                        (debit-credit<=0ANDamount_currency<=0)
                        OR
                        (debit-credit>=0ANDamount_currency>=0)
                    )
                )
                OR
                (
                    currency_id=company_currency_id
                    AND
                    ROUND(debit-credit-amount_currency,2)=0
                )
            )''',
            "Theamountexpressedinthesecondarycurrencymustbepositivewhenaccountisdebitedandnegativewhen"
            "accountiscredited.Ifthecurrencyisthesameastheonefromthecompany,thisamountmuststrictly"
            "beequaltothebalance."
        ),
    ]

    #-------------------------------------------------------------------------
    #HELPERS
    #-------------------------------------------------------------------------

    @api.model
    def_get_default_line_name(self,document,amount,currency,date,partner=None):
        '''Helpertoconstructadefaultlabeltosetonjournalitems.

        E.g.VendorReimbursement$1,555.00-AzureInterior-05/14/2020.

        :paramdocument:   Astringrepresentingthetypeofthedocument.
        :paramamount:     Thedocument'samount.
        :paramcurrency:   Thedocument'scurrency.
        :paramdate:       Thedocument'sdate.
        :parampartner:    Theoptionalpartner.
        :return:           Astring.
        '''
        values=['%s%s'%(document,formatLang(self.env,amount,currency_obj=currency))]
        ifpartner:
            values.append(partner.display_name)
        values.append(format_date(self.env,fields.Date.to_string(date)))
        return'-'.join(values)

    @api.model
    def_get_default_tax_account(self,repartition_line):
        tax=repartition_line.invoice_tax_idorrepartition_line.refund_tax_id
        iftax.tax_exigibility=='on_payment':
            account=tax.cash_basis_transition_account_id
        else:
            account=repartition_line.account_id
        returnaccount

    def_get_integrity_hash_fields(self):
        #Usethenewhashversionbydefault,butkeeptheoldoneforbackwardcompatibilitywhengeneratingtheintegrityreport.
        hash_version=self._context.get('hash_version',MAX_HASH_VERSION)
        ifhash_version==1:
            return['debit','credit','account_id','partner_id']
        elifhash_version==MAX_HASH_VERSION:
            return['name','debit','credit','account_id','partner_id']
        raiseNotImplementedError(f"hash_version={hash_version}doesn'texist")

    def_get_computed_name(self):
        self.ensure_one()

        ifnotself.product_id:
            return''

        ifself.partner_id.lang:
            product=self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product=self.product_id

        values=[]
        ifproduct.partner_ref:
            values.append(product.partner_ref)
        ifself.journal_id.type=='sale':
            ifproduct.description_sale:
                values.append(product.description_sale)
        elifself.journal_id.type=='purchase':
            ifproduct.description_purchase:
                values.append(product.description_purchase)
        return'\n'.join(values)

    def_get_computed_price_unit(self):
        '''Helpertogetthedefaultpriceunitbasedontheproductbytakingcareofthetaxes
        setontheproductandthefiscalposition.
        :return:Thepriceunit.
        '''
        self.ensure_one()

        ifnotself.product_id:
            return0.0
        ifself.move_id.is_sale_document(include_receipts=True):
            document_type='sale'
        elifself.move_id.is_purchase_document(include_receipts=True):
            document_type='purchase'
        else:
            document_type='other'
        returnself.product_id._get_tax_included_unit_price(
            self.move_id.company_id,
            self.move_id.currency_id,
            self.move_id.date,
            document_type,
            fiscal_position=self.move_id.fiscal_position_id,
            product_uom=self.product_uom_id
        )

    def_get_computed_account(self):
        self.ensure_one()
        self=self.with_company(self.move_id.journal_id.company_id)

        ifnotself.product_id:
            return

        fiscal_position=self.move_id.fiscal_position_id
        accounts=self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        ifself.move_id.is_sale_document(include_receipts=True):
            #Outinvoice.
            returnaccounts['income']orself.account_id
        elifself.move_id.is_purchase_document(include_receipts=True):
            #Ininvoice.
            returnaccounts['expense']orself.account_id

    def_get_computed_taxes(self):
        self.ensure_one()

        ifself.move_id.is_sale_document(include_receipts=True):
            #Outinvoice.
            ifself.product_id.taxes_id:
                tax_ids=self.product_id.taxes_id.filtered(lambdatax:tax.company_id==self.move_id.company_id)
            else:
                tax_ids=self.account_id.tax_ids.filtered(lambdatax:tax.type_tax_use=='sale')
            ifnottax_idsandnotself.exclude_from_invoice_tab:
                tax_ids=self.move_id.company_id.account_sale_tax_id
        elifself.move_id.is_purchase_document(include_receipts=True):
            #Ininvoice.
            ifself.product_id.supplier_taxes_id:
                tax_ids=self.product_id.supplier_taxes_id.filtered(lambdatax:tax.company_id==self.move_id.company_id)
            else:
                tax_ids=self.account_id.tax_ids.filtered(lambdatax:tax.type_tax_use=='purchase')
            ifnottax_idsandnotself.exclude_from_invoice_tab:
                tax_ids=self.move_id.company_id.account_purchase_tax_id
        else:
            #Miscellaneousoperation.
            tax_ids=self.account_id.tax_ids

        ifself.company_idandtax_ids:
            tax_ids=tax_ids.filtered(lambdatax:tax.company_id==self.company_id)

        returntax_ids

    def_get_computed_uom(self):
        self.ensure_one()
        ifself.product_id:
            returnself.product_id.uom_id
        returnFalse

    def_set_price_and_tax_after_fpos(self):
        self.ensure_one()
        #Managethefiscalpositionafterthatandadapttheprice_unit.
        #E.g.mappingaprice-included-taxtoaprice-excluded-taxmust
        #removethetaxamountfromtheprice_unit.
        #However,mappingaprice-includedtaxtoanotherprice-includedtaxmustpreservethebalancebut
        #adapttheprice_unittothenewtax.
        #E.g.mappinga10%price-includedtaxtoa20%price-includedtaxforaprice_unitof110shouldpreserve
        #100asbalancebutset120asprice_unit.
        ifself.tax_idsandself.move_id.fiscal_position_idandself.move_id.fiscal_position_id.tax_ids:
            price_subtotal=self._get_price_total_and_subtotal()['price_subtotal']
            self.tax_ids=self.move_id.fiscal_position_id.map_tax(
                self.tax_ids._origin,
                partner=self.move_id.partner_id)
            accounting_vals=self._get_fields_onchange_subtotal(
                price_subtotal=price_subtotal,
                currency=self.move_id.company_currency_id)
            amount_currency=accounting_vals['amount_currency']
            business_vals=self._get_fields_onchange_balance(amount_currency=amount_currency)
            if'price_unit'inbusiness_vals:
                self.price_unit=business_vals['price_unit']

    @api.depends('product_id','account_id','partner_id','date')
    def_compute_analytic_account_id(self):
        forrecordinself:
            ifnotrecord.exclude_from_invoice_tabornotrecord.move_id.is_invoice(include_receipts=True):
                rec=self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.idorrecord.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                ifrec:
                    record.analytic_account_id=rec.analytic_id

    @api.depends('product_id','account_id','partner_id','date')
    def_compute_analytic_tag_ids(self):
        forrecordinself:
            ifnotrecord.exclude_from_invoice_tabornotrecord.move_id.is_invoice(include_receipts=True):
                rec=self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.idorrecord.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                ifrec:
                    record.analytic_tag_ids=rec.analytic_tag_ids

    @api.depends('move_id.payment_reference')
    def_compute_name(self):
        forlineinself.filtered(lambdal:notl.nameandl.account_id.user_type_id.typein('receivable','payable')):
            line.name=line.move_id.payment_reference

    def_get_price_total_and_subtotal(self,price_unit=None,quantity=None,discount=None,currency=None,product=None,partner=None,taxes=None,move_type=None):
        self.ensure_one()
        returnself._get_price_total_and_subtotal_model(
            price_unit=self.price_unitifprice_unitisNoneelseprice_unit,
            quantity=self.quantityifquantityisNoneelsequantity,
            discount=self.discountifdiscountisNoneelsediscount,
            currency=self.currency_idifcurrencyisNoneelsecurrency,
            product=self.product_idifproductisNoneelseproduct,
            partner=self.partner_idifpartnerisNoneelsepartner,
            taxes=self.tax_idsiftaxesisNoneelsetaxes,
            move_type=self.move_id.move_typeifmove_typeisNoneelsemove_type,
        )

    @api.model
    def_get_price_total_and_subtotal_model(self,price_unit,quantity,discount,currency,product,partner,taxes,move_type):
        '''Thismethodisusedtocompute'price_total'&'price_subtotal'.

        :paramprice_unit: Thecurrentpriceunit.
        :paramquantity:   Thecurrentquantity.
        :paramdiscount:   Thecurrentdiscount.
        :paramcurrency:   Theline'scurrency.
        :paramproduct:    Theline'sproduct.
        :parampartner:    Theline'spartner.
        :paramtaxes:      Theappliedtaxes.
        :parammove_type:  Thetypeofthemove.
        :return:           Adictionarycontaining'price_subtotal'&'price_total'.
        '''
        res={}

        #Compute'price_subtotal'.
        line_discount_price_unit=price_unit*(1-(discount/100.0))
        subtotal=quantity*line_discount_price_unit

        #Compute'price_total'.
        iftaxes:
            taxes_res=taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity,currency=currency,product=product,partner=partner,is_refund=move_typein('out_refund','in_refund'))
            res['price_subtotal']=taxes_res['total_excluded']
            res['price_total']=taxes_res['total_included']
        else:
            res['price_total']=res['price_subtotal']=subtotal
        #Incaseofmulticurrency,roundbeforeit'suseforcomputingdebitcredit
        ifcurrency:
            res={k:currency.round(v)fork,vinres.items()}
        returnres

    def_get_fields_onchange_subtotal(self,price_subtotal=None,move_type=None,currency=None,company=None,date=None):
        self.ensure_one()
        returnself._get_fields_onchange_subtotal_model(
            price_subtotal=self.price_subtotalifprice_subtotalisNoneelseprice_subtotal,
            move_type=self.move_id.move_typeifmove_typeisNoneelsemove_type,
            currency=self.currency_idifcurrencyisNoneelsecurrency,
            company=self.move_id.company_idifcompanyisNoneelsecompany,
            date=self.move_id.dateifdateisNoneelsedate,
        )

    @api.model
    def_get_fields_onchange_subtotal_model(self,price_subtotal,move_type,currency,company,date):
        '''Thismethodisusedtorecomputethevaluesof'amount_currency','debit','credit'duetoachangemade
        insomebusinessfields(affectingthe'price_subtotal'field).

        :paramprice_subtotal: Theuntaxedamount.
        :parammove_type:      Thetypeofthemove.
        :paramcurrency:       Theline'scurrency.
        :paramcompany:        Themove'scompany.
        :paramdate:           Themove'sdate.
        :return:               Adictionarycontaining'debit','credit','amount_currency'.
        '''
        ifmove_typeinself.move_id.get_outbound_types():
            sign=1
        elifmove_typeinself.move_id.get_inbound_types():
            sign=-1
        else:
            sign=1

        amount_currency=price_subtotal*sign
        balance=currency._convert(amount_currency,company.currency_id,company,dateorfields.Date.context_today(self))
        return{
            'amount_currency':amount_currency,
            'currency_id':currency.id,
            'debit':balance>0.0andbalanceor0.0,
            'credit':balance<0.0and-balanceor0.0,
        }

    def_get_fields_onchange_balance(self,quantity=None,discount=None,amount_currency=None,move_type=None,currency=None,taxes=None,price_subtotal=None,force_computation=False):
        self.ensure_one()
        returnself._get_fields_onchange_balance_model(
            quantity=self.quantityifquantityisNoneelsequantity,
            discount=self.discountifdiscountisNoneelsediscount,
            amount_currency=self.amount_currencyifamount_currencyisNoneelseamount_currency,
            move_type=self.move_id.move_typeifmove_typeisNoneelsemove_type,
            currency=(self.currency_idorself.move_id.currency_id)ifcurrencyisNoneelsecurrency,
            taxes=self.tax_idsiftaxesisNoneelsetaxes,
            price_subtotal=self.price_subtotalifprice_subtotalisNoneelseprice_subtotal,
            force_computation=force_computation,
        )

    @api.model
    def_get_fields_onchange_balance_model(self,quantity,discount,amount_currency,move_type,currency,taxes,price_subtotal,force_computation=False):
        '''Thismethodisusedtorecomputethevaluesof'quantity','discount','price_unit'duetoachangemade
        insomeaccountingfieldssuchas'balance'.

        Thismethodisabitcomplexasweneedtohandlesomespecialcases.
        Forexample,settingapositivebalancewitha100%discount.

        :paramquantity:       Thecurrentquantity.
        :paramdiscount:       Thecurrentdiscount.
        :paramamount_currency:Thenewbalanceinline'scurrency.
        :parammove_type:      Thetypeofthemove.
        :paramcurrency:       Thecurrency.
        :paramtaxes:          Theappliedtaxes.
        :paramprice_subtotal: Theprice_subtotal.
        :return:               Adictionarycontaining'quantity','discount','price_unit'.
        '''
        ifmove_typeinself.move_id.get_outbound_types():
            sign=1
        elifmove_typeinself.move_id.get_inbound_types():
            sign=-1
        else:
            sign=1
        amount_currency*=sign

        #Avoidroundingissuewhendealingwithpriceincludedtaxes.Forexample,whentheprice_unitis2300.0and
        #a5.5%priceincludedtaxisappliedonit,abalanceof2300.0/1.055=2180.094~2180.09iscomputed.
        #However,whentriggeringtheinverse,2180.09+(2180.09*0.055)=2180.09+119.90=2299.99iscomputed.
        #Toavoidthat,settheprice_subtotalatthebalanceifthedifferencebetweenthemlookslikearounding
        #issue.
        ifnotforce_computationandcurrency.is_zero(amount_currency-price_subtotal):
            return{}

        taxes=taxes.flatten_taxes_hierarchy()
        iftaxesandany(tax.price_includefortaxintaxes):
            #Inversetaxes.E.g:
            #
            #PriceUnit   |Taxes        |OriginatorTax   |PriceSubtotal    |PriceTotal
            #-----------------------------------------------------------------------------------
            #110          |10%incl,5% |                  |100              |115
            #10           |              |10%incl         |10               |10
            #5            |              |5%               |5                |5
            #
            #Whensettingthebalanceto-200,theexpectedresultis:
            #
            #PriceUnit   |Taxes        |OriginatorTax   |PriceSubtotal    |PriceTotal
            #-----------------------------------------------------------------------------------
            #220          |10%incl,5% |                  |200              |230
            #20           |              |10%incl         |20               |20
            #10           |              |5%               |10               |10
            force_sign=-1ifmove_typein('out_invoice','in_refund','out_receipt')else1
            taxes_res=taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency,currency=currency,handle_price_include=False)
            fortax_resintaxes_res['taxes']:
                tax=self.env['account.tax'].browse(tax_res['id'])
                iftax.price_include:
                    amount_currency+=tax_res['amount']

        discount_factor=1-(discount/100.0)
        ifamount_currencyanddiscount_factor:
            #discount!=100%
            vals={
                'quantity':quantityor1.0,
                'price_unit':amount_currency/discount_factor/(quantityor1.0),
            }
        elifamount_currencyandnotdiscount_factor:
            #discount==100%
            vals={
                'quantity':quantityor1.0,
                'discount':0.0,
                'price_unit':amount_currency/(quantityor1.0),
            }
        elifnotdiscount_factor:
            #balanceoflineis0,butdiscount ==100%sowedisplaythenormalunit_price
            vals={}
        else:
            #balanceis0,sounitpriceis0aswell
            vals={'price_unit':0.0}
        returnvals

    def_get_invoiced_qty_per_product(self):
        qties=defaultdict(float)
        foramlinself:
            qty=aml.product_uom_id._compute_quantity(aml.quantity,aml.product_id.uom_id)
            ifaml.move_id.move_type=='out_invoice':
                qties[aml.product_id]+=qty
            elifaml.move_id.move_type=='out_refund':
                qties[aml.product_id]-=qty
        returnqties

    #-------------------------------------------------------------------------
    #ONCHANGEMETHODS
    #-------------------------------------------------------------------------

    @api.onchange('amount_currency','currency_id','debit','credit','tax_ids','account_id','price_unit','quantity')
    def_onchange_mark_recompute_taxes(self):
        '''Recomputethedynamiconchangebasedontaxes.
        Iftheeditedlineisataxline,don'trecomputeanythingastheusermustbeableto
        setacustomvalue.
        '''
        forlineinself:
            ifnotline.tax_repartition_line_id:
                line.recompute_tax_line=True

    @api.onchange('analytic_account_id','analytic_tag_ids')
    def_onchange_mark_recompute_taxes_analytic(self):
        '''Triggertaxrecomputationonlywhensometaxeswithanalytics
        '''
        forlineinself:
            ifnotline.tax_repartition_line_idandany(tax.analyticfortaxinline.tax_ids):
                line.recompute_tax_line=True

    @api.onchange('product_id')
    def_onchange_product_id(self):
        forlineinself:
            ifnotline.product_idorline.display_typein('line_section','line_note'):
                continue

            line.name=line._get_computed_name()
            line.account_id=line._get_computed_account()
            taxes=line._get_computed_taxes()
            iftaxesandline.move_id.fiscal_position_id:
                taxes=line.move_id.fiscal_position_id.map_tax(taxes,partner=line.partner_id)
            line.tax_ids=taxes
            line.product_uom_id=line._get_computed_uom()
            line.price_unit=line._get_computed_price_unit()

    @api.onchange('product_uom_id')
    def_onchange_uom_id(self):
        '''Recomputethe'price_unit'dependingoftheunitofmeasure.'''
        ifself.display_typein('line_section','line_note'):
            return
        taxes=self._get_computed_taxes()
        iftaxesandself.move_id.fiscal_position_id:
            taxes=self.move_id.fiscal_position_id.map_tax(taxes,partner=self.partner_id)
        self.tax_ids=taxes
        self.price_unit=self._get_computed_price_unit()

    @api.onchange('account_id')
    def_onchange_account_id(self):
        '''Recompute'tax_ids'basedon'account_id'.
        /!\Don'tremoveexistingtaxesifthereisnoexplicittaxessetontheaccount.
        '''
        ifnotself.display_typeand(self.account_id.tax_idsornotself.tax_ids):
            taxes=self._get_computed_taxes()

            iftaxesandself.move_id.fiscal_position_id:
                taxes=self.move_id.fiscal_position_id.map_tax(taxes,partner=self.partner_id)

            self.tax_ids=taxes

    def_onchange_balance(self):
        forlineinself:
            ifline.currency_id==line.move_id.company_id.currency_id:
                line.amount_currency=line.balance
            else:
                continue
            ifnotline.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_fields_onchange_balance())

    @api.onchange('debit')
    def_onchange_debit(self):
        ifself.debit:
            self.credit=0.0
        self._onchange_balance()

    @api.onchange('credit')
    def_onchange_credit(self):
        ifself.credit:
            self.debit=0.0
        self._onchange_balance()

    @api.onchange('amount_currency')
    def_onchange_amount_currency(self):
        forlineinself:
            company=line.move_id.company_id
            balance=line.currency_id._convert(line.amount_currency,company.currency_id,company,line.move_id.dateorfields.Date.context_today(line))
            line.debit=balanceifbalance>0.0else0.0
            line.credit=-balanceifbalance<0.0else0.0

            ifnotline.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())

    @api.onchange('quantity','discount','price_unit','tax_ids')
    def_onchange_price_subtotal(self):
        forlineinself:
            ifnotline.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_price_total_and_subtotal())
            line.update(line._get_fields_onchange_subtotal())

    @api.onchange('currency_id')
    def_onchange_currency(self):
        forlineinself:
            company=line.move_id.company_id

            ifline.move_id.is_invoice(include_receipts=True):
                line._onchange_price_subtotal()
            elifnotline.move_id.reversed_entry_id:
                balance=line.currency_id._convert(line.amount_currency,company.currency_id,company,line.move_id.dateorfields.Date.context_today(line))
                line.debit=balanceifbalance>0.0else0.0
                line.credit=-balanceifbalance<0.0else0.0

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('full_reconcile_id.name','matched_debit_ids','matched_credit_ids')
    def_compute_matching_number(self):
        forrecordinself:
            ifrecord.full_reconcile_id:
                record.matching_number=record.full_reconcile_id.name
            elifrecord.matched_debit_idsorrecord.matched_credit_ids:
                record.matching_number='P'
            else:
                record.matching_number=None

    @api.depends('debit','credit')
    def_compute_balance(self):
        forlineinself:
            line.balance=line.debit-line.credit

    @api.model
    defsearch_read(self,domain=None,fields=None,offset=0,limit=None,order=None):
        defto_tuple(t):
            returntuple(map(to_tuple,t))ifisinstance(t,(list,tuple))elset
        #Makeanexplicitorderbecausewewillneedtoreverseit
        order=(orderorself._order)+',id'
        #Addthedomainandorderbyinordertocomputethecumulatedbalancein_compute_cumulated_balance
        returnsuper(AccountMoveLine,self.with_context(domain_cumulated_balance=to_tuple(domainor[]),order_cumulated_balance=order)).search_read(domain,fields,offset,limit,order)

    @api.model
    deffields_get(self,allfields=None,attributes=None):
        res=super().fields_get(allfields,attributes)
        ifres.get('cumulated_balance'):
            res['cumulated_balance']['exportable']=False
        returnres

    @api.depends_context('order_cumulated_balance','domain_cumulated_balance')
    def_compute_cumulated_balance(self):
        ifnotself.env.context.get('order_cumulated_balance'):
            #Wedonotcomefromsearch_read,sowearenotinalistview,soitdoesn'tmakeanysensetocomputethecumulatedbalance
            self.cumulated_balance=0
            return

        #getthewhereclause
        query=self._where_calc(list(self.env.context.get('domain_cumulated_balance')or[]))
        order_string=",".join(self._generate_order_by_inner(self._table,self.env.context.get('order_cumulated_balance'),query,reverse_direction=True))
        from_clause,where_clause,where_clause_params=query.get_sql()
        sql="""
            SELECTaccount_move_line.id,SUM(account_move_line.balance)OVER(
                ORDERBY%(order_by)s
                ROWSBETWEENUNBOUNDEDPRECEDINGANDCURRENTROW
            )
            FROM%(from)s
            WHERE%(where)s
        """%{'from':from_clause,'where':where_clauseor'TRUE','order_by':order_string}
        self.env.cr.execute(sql,where_clause_params)
        result={r[0]:r[1]forrinself.env.cr.fetchall()}
        forrecordinself:
            record.cumulated_balance=result[record.id]

    @api.depends('debit','credit','amount_currency','account_id','currency_id','parent_state','company_id',
                 'matched_debit_ids','matched_credit_ids')
    def_compute_amount_residual(self):
        """Computestheresidualamountofamovelinefromareconcilableaccountinthecompanycurrencyandtheline'scurrency.
            Thisamountwillbe0forfullyreconciledlinesorlinesfromanon-reconcilableaccount,theoriginallineamount
            forunreconciledlines,andsomethingin-betweenforpartiallyreconciledlines.
        """
        forlineinself:
            ifline.idand(line.account_id.reconcileorline.account_id.internal_type=='liquidity'):
                reconciled_balance=sum(line.matched_credit_ids.mapped('amount'))\
                                     -sum(line.matched_debit_ids.mapped('amount'))
                reconciled_amount_currency=sum(line.matched_credit_ids.mapped('debit_amount_currency'))\
                                             -sum(line.matched_debit_ids.mapped('credit_amount_currency'))

                line.amount_residual=line.balance-reconciled_balance

                ifline.currency_id:
                    line.amount_residual_currency=line.amount_currency-reconciled_amount_currency
                else:
                    line.amount_residual_currency=0.0

                line.reconciled=(
                    line.company_currency_id.is_zero(line.amount_residual)
                    and(notline.currency_idorline.currency_id.is_zero(line.amount_residual_currency))
                    and(line.matched_debit_idsorline.matched_credit_ids)
                )
            else:
                #Mustnothaveanyreconciliationsincethelineisnoteligibleforthat.
                line.amount_residual=0.0
                line.amount_residual_currency=0.0
                line.reconciled=False

    @api.depends('tax_repartition_line_id.invoice_tax_id','tax_repartition_line_id.refund_tax_id')
    def_compute_tax_line_id(self):
        """tax_line_idiscomputedasthetaxlinkedtotherepartitionlinecreating
        themove.
        """
        forrecordinself:
            rep_line=record.tax_repartition_line_id
            #Aconstraintonaccount.tax.repartition.lineensuresboththosefieldsaremutuallyexclusive
            record.tax_line_id=rep_line.invoice_tax_idorrep_line.refund_tax_id

    @api.depends('tax_tag_ids','debit','credit','journal_id')
    def_compute_tax_audit(self):
        separator='       '

        forrecordinself:
            currency=record.company_id.currency_id
            audit_str=''
            fortaginrecord.tax_tag_ids:

                ifrecord.move_id.tax_cash_basis_rec_id:
                    #Cashbasisentriesarealwaystreatedasmiscoperations,applyingthetagsigndirectlytothebalance
                    type_multiplicator=1
                else:
                    type_multiplicator=(record.journal_id.type=='sale'andself._get_not_entry_condition(record)and-1or1)*(self._get_refund_tax_audit_condition(record)and-1or1)

                tag_amount=type_multiplicator*(tag.tax_negateand-1or1)*record.balance

                iftag.tax_report_line_ids:
                    #Then,thetagcomesfromareportline,andhencehasa+or-sign(alsoinitsname)
                    forreport_lineintag.tax_report_line_ids:
                        audit_str+=separatorifaudit_strelse''
                        audit_str+=report_line.tag_name+':'+formatLang(self.env,tag_amount,currency_obj=currency)
                else:
                    #Then,it'safinancialtag(signisalways+,andnevershownintagname)
                    audit_str+=separatorifaudit_strelse''
                    audit_str+=tag.name+':'+formatLang(self.env,tag_amount,currency_obj=currency)

            record.tax_audit=audit_str

    def_get_not_entry_condition(self,aml):
        """
        Returnstheconditiontoexcludeentrymovetypestoavoidtheirtax_auditvalue
        toberevesediftheyarefromtypeentry.
        Thisfunctionisoverriddeninpos.
        """
        returnaml.move_id.move_type!='entry'

    def_get_refund_tax_audit_condition(self,aml):
        """Returnstheconditiontobeusedfortheprovidedmovelinetotell
        whetherornotitcomesfromarefundoperation.
        Thisisoverriddenbyposinordertotreatreturnsproperly.
        """
        returnaml.move_id.move_typein('in_refund','out_refund')

    #-------------------------------------------------------------------------
    #CONSTRAINTMETHODS
    #-------------------------------------------------------------------------

    @api.constrains('account_id','journal_id')
    def_check_constrains_account_id_journal_id(self):
        forlineinself.filtered(lambdax:x.display_typenotin('line_section','line_note')):
            account=line.account_id
            journal=line.move_id.journal_id

            ifaccount.deprecated:
                raiseUserError(_('Theaccount%s(%s)isdeprecated.')%(account.name,account.code))

            account_currency=account.currency_id
            ifaccount_currencyandaccount_currency!=line.company_currency_idandaccount_currency!=line.currency_id:
                raiseUserError(_('Theaccountselectedonyourjournalentryforcestoprovideasecondarycurrency.Youshouldremovethesecondarycurrencyontheaccount.'))

            ifaccount.allowed_journal_idsandjournalnotinaccount.allowed_journal_ids:
                raiseUserError(_('Youcannotusethisaccount(%s)inthisjournal,checkthefield\'AllowedJournals\'ontherelatedaccount.',account.display_name))

            ifaccountin(journal.default_account_id,journal.suspense_account_id):
                continue

            is_account_control_ok=notjournal.account_control_idsoraccountinjournal.account_control_ids
            is_type_control_ok=notjournal.type_control_idsoraccount.user_type_idinjournal.type_control_ids

            ifnotis_account_control_okornotis_type_control_ok:
                raiseUserError(_("Youcannotusethisaccount(%s)inthisjournal,checkthesection'Control-Access'under"
                                  "tab'AdvancedSettings'ontherelatedjournal.",account.display_name))

    @api.constrains('account_id','tax_ids','tax_line_id','reconciled')
    def_check_off_balance(self):
        forlineinself:
            ifline.account_id.internal_group=='off_balance':
                ifany(a.internal_group!=line.account_id.internal_groupforainline.move_id.line_ids.account_id):
                    raiseUserError(_('Ifyouwanttouse"Off-BalanceSheet"accounts,alltheaccountsofthejournalentrymustbeofthistype'))
                ifline.tax_idsorline.tax_line_id:
                    raiseUserError(_('YoucannotusetaxesonlineswithanOff-Balanceaccount'))
                ifline.reconciled:
                    raiseUserError(_('Linesfrom"Off-BalanceSheet"accountscannotbereconciled'))

    @api.constrains('product_uom_id')
    def_check_product_uom_category_id(self):
        forlineinself:
            ifline.product_uom_idandline.product_idandline.product_uom_id.category_id!=line.product_id.product_tmpl_id.uom_id.category_id:
                raiseUserError(_(
                    "TheUnitofMeasure(UoM)'%s'youhaveselectedforproduct'%s',"
                    "isincompatiblewithitscategory:%s.",
                    line.product_uom_id.name,
                    line.product_id.name,
                    line.product_id.product_tmpl_id.uom_id.category_id.name
                ))

    def_affect_tax_report(self):
        self.ensure_one()
        returnself.tax_idsorself.tax_line_idorself.tax_tag_ids.filtered(lambdax:x.applicability=="taxes")

    def_check_tax_lock_date(self):
        forlineinself.filtered(lambdal:l.move_id.state=='posted'):
            move=line.move_id
            ifmove.company_id.tax_lock_dateandmove.date<=move.company_id.tax_lock_dateandline._affect_tax_report():
                raiseUserError(_("Theoperationisrefusedasitwouldimpactanalreadyissuedtaxstatement."
                                  "Pleasechangethejournalentrydateorthetaxlockdatesetinthesettings(%s)toproceed.")
                                %format_date(self.env,move.company_id.tax_lock_date))

    def_check_reconciliation(self):
        forlineinself:
            ifline.matched_debit_idsorline.matched_credit_ids:
                raiseUserError(_("Youcannotdothismodificationonareconciledjournalentry."
                                  "Youcanjustchangesomenonlegalfieldsoryoumustunreconcilefirst.\n"
                                  "JournalEntry(id):%s(%s)")%(line.move_id.name,line.move_id.id))

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    definit(self):
        """changeindexonpartner_idtoamulti-columnindexon(partner_id,ref),thenewindexwillbehaveinthe
            samewaywhenwesearchonpartner_id,withtheadditionofbeingoptimalwhenhavingaquerythatwill
            searchonpartner_idandrefatthesametime(whichisthecasewhenweopenthebankreconciliationwidget)
        """
        cr=self._cr
        cr.execute('DROPINDEXIFEXISTSaccount_move_line_partner_id_index')
        cr.execute('SELECTindexnameFROMpg_indexesWHEREindexname=%s',('account_move_line_partner_id_ref_idx',))
        ifnotcr.fetchone():
            cr.execute('CREATEINDEXaccount_move_line_partner_id_ref_idxONaccount_move_line(partner_id,ref)')

    @api.model_create_multi
    defcreate(self,vals_list):
        #OVERRIDE
        ACCOUNTING_FIELDS=('debit','credit','amount_currency')
        BUSINESS_FIELDS=('price_unit','quantity','discount','tax_ids')

        forvalsinvals_list:
            move=self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id',move.company_id.currency_id.id)#importanttobypasstheORMlimitationwheremonetaryfieldsarenotrounded;moreinfointhecommitmessage

            #Ensurebalance==amount_currencyincaseofmissingcurrencyorsamecurrencyastheonefromthe
            #company.
            currency_id=vals.get('currency_id')ormove.company_id.currency_id.id
            ifcurrency_id==move.company_id.currency_id.id:
                balance=vals.get('debit',0.0)-vals.get('credit',0.0)
                vals.update({
                    'currency_id':currency_id,
                    'amount_currency':balance,
                })
            else:
                vals['amount_currency']=vals.get('amount_currency',0.0)

            ifmove.is_invoice(include_receipts=True):
                currency=move.currency_id
                partner=self.env['res.partner'].browse(vals.get('partner_id'))
                taxes=self.new({'tax_ids':vals.get('tax_ids',[])}).tax_ids
                tax_ids=set(taxes.ids)
                taxes=self.env['account.tax'].browse(tax_ids)

                #Ensureconsistencybetweenaccounting&businessfields.
                #Aswecan'texpresssuchsynchronizationascomputedfieldswithoutcycling,weneedtodoitboth
                #inonchangeandincreate/write.So,ifsomethingchangedinaccounting[resp.business]fields,
                #business[resp.accounting]fieldsarerecomputed.
                ifany(vals.get(field)forfieldinACCOUNTING_FIELDS):
                    price_subtotal=self._get_price_total_and_subtotal_model(
                        vals.get('price_unit',0.0),
                        vals.get('quantity',0.0),
                        vals.get('discount',0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                    ).get('price_subtotal',0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity',0.0),
                        vals.get('discount',0.0),
                        vals['amount_currency'],
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit',0.0),
                        vals.get('quantity',0.0),
                        vals.get('discount',0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                    ))
                elifany(vals.get(field)forfieldinBUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit',0.0),
                        vals.get('quantity',0.0),
                        vals.get('discount',0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.move_type,
                        currency,
                        move.company_id,
                        move.date,
                    ))

        lines=super(AccountMoveLine,self).create(vals_list)

        moves=lines.mapped('move_id')
        ifself._context.get('check_move_validity',True):
            moves._check_balanced()
        moves._check_fiscalyear_lock_date()
        lines._check_tax_lock_date()
        moves._synchronize_business_models({'line_ids'})

        returnlines

    defwrite(self,vals):
        #OVERRIDE
        ACCOUNTING_FIELDS=('debit','credit','amount_currency')
        BUSINESS_FIELDS=('price_unit','quantity','discount','tax_ids')
        PROTECTED_FIELDS_TAX_LOCK_DATE=['debit','credit','tax_line_id','tax_ids','tax_tag_ids']
        PROTECTED_FIELDS_LOCK_DATE=PROTECTED_FIELDS_TAX_LOCK_DATE+['account_id','journal_id','amount_currency','currency_id','partner_id']
        PROTECTED_FIELDS_RECONCILIATION=('account_id','date','debit','credit','amount_currency','currency_id')

        account_to_write=self.env['account.account'].browse(vals['account_id'])if'account_id'invalselseNone

        #Checkwritingadeprecatedaccount.
        ifaccount_to_writeandaccount_to_write.deprecated:
            raiseUserError(_('Youcannotuseadeprecatedaccount.'))

        inalterable_fields=set(self._get_integrity_hash_fields()).union({'inalterable_hash','secure_sequence_number'})
        hashed_moves=self.move_id.filtered('inalterable_hash')
        violated_fields=set(vals)&inalterable_fields
        ifhashed_movesandviolated_fields:
            raiseUserError(_(
                "Youcannoteditthefollowingfields:%s.\n"
                "Thefollowingentriesarealreadyhashed:\n%s",
                ','.join(f['string']forfinself.fields_get(violated_fields).values()),
                '\n'.join(hashed_moves.mapped('name')),
            ))
        forlineinself:
            ifline.parent_state=='posted':
                ifany(keyinvalsforkeyin('tax_ids','tax_line_id')):
                    raiseUserError(_('Youcannotmodifythetaxesrelatedtoapostedjournalitem,youshouldresetthejournalentrytodrafttodoso.'))

            #Checkthelockdate.
            ifany(self.env['account.move']._field_will_change(line,vals,field_name)forfield_nameinPROTECTED_FIELDS_LOCK_DATE):
                line.move_id._check_fiscalyear_lock_date()

            #Checkthetaxlockdate.
            ifany(self.env['account.move']._field_will_change(line,vals,field_name)forfield_nameinPROTECTED_FIELDS_TAX_LOCK_DATE):
                line._check_tax_lock_date()

            #Checkthereconciliation.
            ifany(self.env['account.move']._field_will_change(line,vals,field_name)forfield_nameinPROTECTED_FIELDS_RECONCILIATION):
                line._check_reconciliation()

            #Checkswitchingreceivable/payableaccounts.
            ifaccount_to_write:
                account_type=line.account_id.user_type_id.type
                ifline.move_id.is_sale_document(include_receipts=True):
                    if(account_type=='receivable'andaccount_to_write.user_type_id.type!=account_type)\
                            or(account_type!='receivable'andaccount_to_write.user_type_id.type=='receivable'):
                        raiseUserError(_("Youcanonlysetanaccounthavingthereceivabletypeonpaymenttermslinesforcustomerinvoice."))
                ifline.move_id.is_purchase_document(include_receipts=True):
                    if(account_type=='payable'andaccount_to_write.user_type_id.type!=account_type)\
                            or(account_type!='payable'andaccount_to_write.user_type_id.type=='payable'):
                        raiseUserError(_("Youcanonlysetanaccounthavingthepayabletypeonpaymenttermslinesforvendorbill."))

        #Trackingstuffcanbeskippedforperfsusingtracking_disablecontextkey
        ifnotself.env.context.get('tracking_disable',False):
            #Getalltrackedfields(withoutrelatedfieldsbecausethesefieldsmustbemanageontheirownmodel)
            tracking_fields=[]
            forvalueinvals:
                field=self._fields[value]
                ifhasattr(field,'related')andfield.related:
                    continue#Wedon'twanttotrackrelatedfield.
                ifhasattr(field,'tracking')andfield.tracking:
                    tracking_fields.append(value)
            ref_fields=self.env['account.move.line'].fields_get(tracking_fields)

            #Getinitialvaluesforeachline
            move_initial_values={}
            forlineinself.filtered(lambdal:l.move_id.posted_before):#Onlylineswithpostedoncemove.
                forfieldintracking_fields:
                    #Groupinitialvaluesbymove_id
                    ifline.move_id.idnotinmove_initial_values:
                        move_initial_values[line.move_id.id]={}
                    move_initial_values[line.move_id.id].update({field:line[field]})

        result=True
        forlineinself:
            cleaned_vals=line.move_id._cleanup_write_orm_values(line,vals)
            ifnotcleaned_vals:
                continue

            #Auto-fillamount_currencyifworkinginsingle-currency.
            if'currency_id'notincleaned_vals\
                andline.currency_id==line.company_currency_id\
                andany(field_nameincleaned_valsforfield_namein('debit','credit')):
                cleaned_vals.update({
                    'amount_currency':vals.get('debit',0.0)-vals.get('credit',0.0),
                })

            result|=super(AccountMoveLine,line).write(cleaned_vals)

            ifnotline.move_id.is_invoice(include_receipts=True):
                continue

            #Ensureconsistencybetweenaccounting&businessfields.
            #Aswecan'texpresssuchsynchronizationascomputedfieldswithoutcycling,weneedtodoitboth
            #inonchangeandincreate/write.So,ifsomethingchangedinaccounting[resp.business]fields,
            #business[resp.accounting]fieldsarerecomputed.
            ifany(fieldincleaned_valsforfieldinACCOUNTING_FIELDS):
                price_subtotal=line._get_price_total_and_subtotal().get('price_subtotal',0.0)
                to_write=line._get_fields_onchange_balance(price_subtotal=price_subtotal)
                to_write.update(line._get_price_total_and_subtotal(
                    price_unit=to_write.get('price_unit',line.price_unit),
                    quantity=to_write.get('quantity',line.quantity),
                    discount=to_write.get('discount',line.discount),
                ))
                result|=super(AccountMoveLine,line).write(to_write)
            elifany(fieldincleaned_valsforfieldinBUSINESS_FIELDS):
                to_write=line._get_price_total_and_subtotal()
                to_write.update(line._get_fields_onchange_subtotal(
                    price_subtotal=to_write['price_subtotal'],
                ))
                result|=super(AccountMoveLine,line).write(to_write)

        #Checktotal_debit==total_creditintherelatedmoves.
        ifself._context.get('check_move_validity',True):
            self.mapped('move_id')._check_balanced()

        self.mapped('move_id')._synchronize_business_models({'line_ids'})

        ifnotself.env.context.get('tracking_disable',False):
            #Createthedictforthemessagepost
            tracking_values={} #Trackingvaluestowriteinthemessagepost
            formove_id,modified_linesinmove_initial_values.items():
                tmp_move={move_id:[]}
                forlineinself.filtered(lambdal:l.move_id.id==move_id):
                    changes,tracking_value_ids=line._mail_track(ref_fields,modified_lines) #Returnatuplelike(changedfield,ORMcommand)
                    iftracking_value_ids:
                        forvalueintracking_value_ids:
                            selected_field=value[2] #GetthelastelementofthetupleinthelistofORMcommand.(changed,[(0,0,THIS)])
                            tmp_move[move_id].append({
                                'line_id':line.id,
                                **{'field_name':selected_field.get('field_desc')},
                                **self._get_formated_values(selected_field)
                            })
                    elifchanges:
                        forchangeinchanges:
                            field_name=line._fields[change].string #Getthefieldname
                            tmp_move[move_id].append({
                                'line_id':line.id,
                                'error':True,
                                'field_error':field_name,
                            })
                    else:
                        continue
                iflen(tmp_move[move_id])>0:
                    tracking_values.update(tmp_move)

            #Writeinthechatter.
            formoveinself.mapped('move_id'):
                fields=tracking_values.get(move.id,[])
                iflen(fields)>0:
                    msg=self._get_tracking_field_string(tracking_values.get(move.id))
                    move.message_post(body=msg) #Writeforeachconcernedmovethemessageinthechatter

        returnresult

    def_valid_field_parameter(self,field,name):
        #Ican'teven
        returnname=='tracking'orsuper()._valid_field_parameter(field,name)

    defunlink(self):
        moves=self.mapped('move_id')

        #Preventdeletinglinesonpostedentries
        ifnotself.env.context.get('force_delete',False)andany(m.state=='posted'forminmoves):
            raiseUserError(_('Youcannotdeleteanitemlinkedtoapostedentry.'))

        #Checkthelinesarenotreconciled(partiallyornot).
        self._check_reconciliation()

        #Checkthelockdate.
        moves._check_fiscalyear_lock_date()

        #Checkthetaxlockdate.
        self._check_tax_lock_date()

        res=super(AccountMoveLine,self).unlink()

        #Checktotal_debit==total_creditintherelatedmoves.
        ifself._context.get('check_move_validity',True):
            moves._check_balanced()

        returnres

    @api.model
    defdefault_get(self,default_fields):
        #OVERRIDE
        values=super(AccountMoveLine,self).default_get(default_fields)

        if'account_id'indefault_fieldsandnotvalues.get('account_id')\
            and(self._context.get('journal_id')orself._context.get('default_journal_id'))\
            andself._context.get('default_move_type')in('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt'):
            #Fillmissing'account_id'.
            journal=self.env['account.journal'].browse(self._context.get('default_journal_id')orself._context['journal_id'])
            values['account_id']=journal.default_account_id.id
        elifself._context.get('line_ids')andany(field_nameindefault_fieldsforfield_namein('debit','credit','account_id','partner_id')):
            move=self.env['account.move'].new({'line_ids':self._context['line_ids']})

            #Suggestdefaultvaluefordebit/credittobalancethejournalentry.
            balance=sum(line['debit']-line['credit']forlineinmove.line_ids)
            #ifwearehere,line_idsisincontext,sojournal_idshouldalsobe.
            journal=self.env['account.journal'].browse(self._context.get('default_journal_id')orself._context['journal_id'])
            currency=journal.exists()andjournal.company_id.currency_id
            ifcurrency:
                balance=currency.round(balance)
            ifbalance<0.0:
                values.update({'debit':-balance})
            ifbalance>0.0:
                values.update({'credit':balance})

            #Suggestdefaultvaluefor'partner_id'.
            if'partner_id'indefault_fieldsandnotvalues.get('partner_id'):
                iflen(move.line_ids[-2:])==2and move.line_ids[-1].partner_id==move.line_ids[-2].partner_id!=False:
                    values['partner_id']=move.line_ids[-2:].mapped('partner_id').id

            #Suggestdefaultvaluefor'account_id'.
            if'account_id'indefault_fieldsandnotvalues.get('account_id'):
                iflen(move.line_ids[-2:])==2and move.line_ids[-1].account_id==move.line_ids[-2].account_id!=False:
                    values['account_id']=move.line_ids[-2:].mapped('account_id').id
        ifvalues.get('display_type')orself.display_type:
            values.pop('account_id',None)
        returnvalues

    @api.depends('ref','move_id')
    defname_get(self):
        result=[]
        forlineinself:
            name=line.move_id.nameor''
            ifline.ref:
                name+="(%s)"%line.ref
            name+=(line.nameorline.product_id.display_name)and(''+(line.nameorline.product_id.display_name))or''
            result.append((line.id,name))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        ifoperator=='ilike':
            domain=['|','|',
                    ('name','ilike',name),
                    ('move_id','ilike',name),
                    ('product_id','ilike',name)]
            returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

        returnsuper()._name_search(name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    @api.model
    definvalidate_cache(self,fnames=None,ids=None):
        #Invalidatecacheofrelatedmoves
        iffnamesisNoneor'move_id'infnames:
            field=self._fields['move_id']
            lines=self.env.cache.get_records(self,field)ifidsisNoneelseself.browse(ids)
            move_ids={id_forid_inself.env.cache.get_values(lines,field)ifid_}
            ifmove_ids:
                self.env['account.move'].invalidate_cache(ids=move_ids)
        returnsuper().invalidate_cache(fnames=fnames,ids=ids)

    #-------------------------------------------------------------------------
    #TRACKINGMETHODS
    #-------------------------------------------------------------------------

    def_get_formated_values(self,tracked_field):
        iftracked_field.get('field_type')in('date','datetime'):
            return{
                'old_value':format_date(self.env,fields.Datetime.from_string(tracked_field.get('old_value_datetime'))),
                'new_value':format_date(self.env,fields.Datetime.from_string(tracked_field.get('new_value_datetime'))),
            }
        eliftracked_field.get('field_type')in('one2many','many2many','many2one'):
            return{
                'old_value':tracked_field.get('old_value_char',''),
                'new_value':tracked_field.get('new_value_char','')
            }
        else:
            return{
                'old_value':[valforkey,valintracked_field.items()if'old_value'inkey][0],#Getthefirstelementbecausewecreatealistlike['Elem']
                'new_value':[valforkey,valintracked_field.items()if'new_value'inkey][0],#Getthefirstelementbecausewecreatealistlike['Elem']
            }

    def_get_tracking_field_string(self,fields):
        ARROW_RIGHT='<divclass="o_Message_trackingValueSeparatoro_Message_trackingValueItemfafa-long-arrow-right"title="Changed"role="img"/>'
        msg='<ul>'
        forfieldinfields:
            redirect_link='<ahref=#data-oe-model=account.move.linedata-oe-id=%d>#%d</a>'%(field['line_id'],field['line_id'])#Accountmovelinelink
            iffield.get('error',False):
                msg+='<li>%s:%s</li>'%(
                    field['field_error'],
                    _('Amodificationhasbeenoperatedontheline%s.',redirect_link)
                )
            else:
                msg+='<li>%s:%s%s%s(%s)</li>'%(field['field_name'],field['old_value'],ARROW_RIGHT,field['new_value'],redirect_link)
        msg+='</ul>'
        returnmsg

    #-------------------------------------------------------------------------
    #RECONCILIATION
    #-------------------------------------------------------------------------

    def_prepare_reconciliation_partials(self):
        '''Preparethepartialsonthecurrentjournalitemstoperformthereconciliation.
        /!\Theorderofrecordsinselfisimportantbecausethejournalitemswillbereconciledusingthisorder.

        :return:Arecordsetofaccount.partial.reconcile.
        '''
        deffix_remaining_cent(currency,abs_residual,partial_amount):
            ifabs_residual-currency.rounding<=partial_amount<=abs_residual+currency.rounding:
                returnabs_residual
            else:
                returnpartial_amount

        debit_lines=iter(self.filtered(lambdaline:line.balance>0.0orline.amount_currency>0.0andnotline.reconciled))
        credit_lines=iter(self.filtered(lambdaline:line.balance<0.0orline.amount_currency<0.0andnotline.reconciled))
        void_lines=iter(self.filtered(lambdaline:notline.balanceandnotline.amount_currencyandnotline.reconciled))
        debit_line=None
        credit_line=None

        debit_amount_residual=0.0
        debit_amount_residual_currency=0.0
        credit_amount_residual=0.0
        credit_amount_residual_currency=0.0
        debit_line_currency=None
        credit_line_currency=None

        partials_vals_list=[]

        whileTrue:

            #Movetothenextavailabledebitline.
            ifnotdebit_line:
                debit_line=next(debit_lines,None)ornext(void_lines,None)
                ifnotdebit_line:
                    break
                debit_amount_residual=debit_line.amount_residual

                ifdebit_line.currency_id:
                    debit_amount_residual_currency=debit_line.amount_residual_currency
                    debit_line_currency=debit_line.currency_id
                else:
                    debit_amount_residual_currency=debit_amount_residual
                    debit_line_currency=debit_line.company_currency_id

            #Movetothenextavailablecreditline.
            ifnotcredit_line:
                credit_line=next(void_lines,None)ornext(credit_lines,None)
                ifnotcredit_line:
                    break
                credit_amount_residual=credit_line.amount_residual

                ifcredit_line.currency_id:
                    credit_amount_residual_currency=credit_line.amount_residual_currency
                    credit_line_currency=credit_line.currency_id
                else:
                    credit_amount_residual_currency=credit_amount_residual
                    credit_line_currency=credit_line.company_currency_id

            min_amount_residual=min(debit_amount_residual,-credit_amount_residual)

            ifdebit_line_currency==credit_line_currency:
                #Reconcileonthesamecurrency.

                min_amount_residual_currency=min(debit_amount_residual_currency,-credit_amount_residual_currency)
                min_debit_amount_residual_currency=min_amount_residual_currency
                min_credit_amount_residual_currency=min_amount_residual_currency

            else:
                #Reconcileonthecompany'scurrency.

                min_debit_amount_residual_currency=credit_line.company_currency_id._convert(
                    min_amount_residual,
                    debit_line.currency_id,
                    credit_line.company_id,
                    credit_line.date,
                )
                min_debit_amount_residual_currency=fix_remaining_cent(
                    debit_line.currency_id,
                    debit_amount_residual_currency,
                    min_debit_amount_residual_currency,
                )
                min_credit_amount_residual_currency=debit_line.company_currency_id._convert(
                    min_amount_residual,
                    credit_line.currency_id,
                    debit_line.company_id,
                    debit_line.date,
                )
                min_credit_amount_residual_currency=fix_remaining_cent(
                    credit_line.currency_id,
                    -credit_amount_residual_currency,
                    min_credit_amount_residual_currency,
                )

            debit_amount_residual-=min_amount_residual
            debit_amount_residual_currency-=min_debit_amount_residual_currency
            credit_amount_residual+=min_amount_residual
            credit_amount_residual_currency+=min_credit_amount_residual_currency

            partials_vals_list.append({
                'amount':min_amount_residual,
                'debit_amount_currency':min_debit_amount_residual_currency,
                'credit_amount_currency':min_credit_amount_residual_currency,
                'debit_move_id':debit_line.id,
                'credit_move_id':credit_line.id,
            })

            has_debit_residual_left=notdebit_line.company_currency_id.is_zero(debit_amount_residual)anddebit_amount_residual>0.0
            has_credit_residual_left=notcredit_line.company_currency_id.is_zero(credit_amount_residual)andcredit_amount_residual<0.0
            has_debit_residual_curr_left=notdebit_line_currency.is_zero(debit_amount_residual_currency)anddebit_amount_residual_currency>0.0
            has_credit_residual_curr_left=notcredit_line_currency.is_zero(credit_amount_residual_currency)andcredit_amount_residual_currency<0.0

            ifdebit_line_currency==credit_line_currency:
                #Thedebitlineisnowfullyreconciledbecause:
                #-eitheramount_residual&amount_residual_currencyareat0.
                #-eitherthecredit_lineisnotanexchangedifferenceone.
                ifnothas_debit_residual_curr_leftand(has_credit_residual_curr_leftornothas_debit_residual_left):
                    debit_line=None

                #Thecreditlineisnowfullyreconciledbecause:
                #-eitheramount_residual&amount_residual_currencyareat0.
                #-eitherthedebitisnotanexchangedifferenceone.
                ifnothas_credit_residual_curr_leftand(has_debit_residual_curr_leftornothas_credit_residual_left):
                    credit_line=None

            else:
                #Thedebitlineisnowfullyreconciledsinceamount_residualis0.
                ifnothas_debit_residual_left:
                    debit_line=None

                #Thecreditlineisnowfullyreconciledsinceamount_residualis0.
                ifnothas_credit_residual_left:
                    credit_line=None

        returnpartials_vals_list

    def_create_exchange_difference_move(self):
        '''Createtheexchangedifferencejournalentryonthecurrentjournalitems.
        :return:Anaccount.moverecord.
        '''

        def_add_lines_to_exchange_difference_vals(lines,exchange_diff_move_vals):
            '''Generatetheexchangedifferencevaluesusedtocreatethejournalitems
            inordertofixtheresidualamountsandaddtheminto'exchange_diff_move_vals'.

            1)Whenreconciledonthesameforeigncurrency,thejournalitemsare
            fullyreconciledregardingthiscurrencybutitcouldbenotthecase
            ofthebalancethatisexpressedusingthecompany'scurrency.Inthat
            case,weneedtocreateexchangedifferencejournalitemstoensurethis
            residualamountreacheszero.

            2)Whenreconciledonthecompanycurrencybuthavingdifferentforeign
            currencies,thejournalitemsarefullyreconciledregardingthecompany
            currencybutit'snotalwaysthecasefortheforeigncurrencies.Inthat
            case,theexchangedifferencejournalitemsarecreatedtoensurethis
            residualamountinforeigncurrencyreacheszero.

            :paramlines:                  Theaccount.move.linestowhichfixtheresidualamounts.
            :paramexchange_diff_move_vals:Thecurrentvalsoftheexchangedifferencejournalentry.
            :return:                       Alistofpair<line,sequence>toperformthereconciliation
                                            atthecreationoftheexchangedifferencemovewhere'line'
                                            istheaccount.move.linetowhichthe'sequence'-thexchange
                                            differencelinewillbereconciledwith.
            '''
            journal=self.env['account.journal'].browse(exchange_diff_move_vals['journal_id'])
            to_reconcile=[]

            forlineinlines:

                exchange_diff_move_vals['date']=max(exchange_diff_move_vals['date'],line.date)

                ifnotline.company_currency_id.is_zero(line.amount_residual):
                    #amount_residual_currency==0andamount_residualhastobefixed.

                    ifline.amount_residual>0.0:
                        exchange_line_account=journal.company_id.expense_currency_exchange_account_id
                    else:
                        exchange_line_account=journal.company_id.income_currency_exchange_account_id

                elifline.currency_idandnotline.currency_id.is_zero(line.amount_residual_currency):
                    #amount_residual==0andamount_residual_currencyhastobefixed.

                    ifline.amount_residual_currency>0.0:
                        exchange_line_account=journal.company_id.expense_currency_exchange_account_id
                    else:
                        exchange_line_account=journal.company_id.income_currency_exchange_account_id
                else:
                    continue

                sequence=len(exchange_diff_move_vals['line_ids'])
                exchange_diff_move_vals['line_ids']+=[
                    (0,0,{
                        'name':_('Currencyexchangeratedifference'),
                        'debit':-line.amount_residualifline.amount_residual<0.0else0.0,
                        'credit':line.amount_residualifline.amount_residual>0.0else0.0,
                        'amount_currency':-line.amount_residual_currency,
                        'account_id':line.account_id.id,
                        'currency_id':line.currency_id.id,
                        'partner_id':line.partner_id.id,
                        'sequence':sequence,
                    }),
                    (0,0,{
                        'name':_('Currencyexchangeratedifference'),
                        'debit':line.amount_residualifline.amount_residual>0.0else0.0,
                        'credit':-line.amount_residualifline.amount_residual<0.0else0.0,
                        'amount_currency':line.amount_residual_currency,
                        'account_id':exchange_line_account.id,
                        'currency_id':line.currency_id.id,
                        'partner_id':line.partner_id.id,
                        'sequence':sequence+1,
                    }),
                ]

                to_reconcile.append((line,sequence))

            returnto_reconcile

        def_add_cash_basis_lines_to_exchange_difference_vals(lines,exchange_diff_move_vals):
            '''Generatetheexchangedifferencevaluesusedtocreatethejournalitems
            inordertofixthecashbasislinesusingthetransferaccountinamulti-currencies
            environmentwhenthisaccountisnotareconcileone.

            Whenthetaxcashbasisjournalentriesaregeneratedandallinvolved
            transferaccountsetontaxesareallreconcilable,theaccountbalance
            willberesettozerobytheexchangedifferencejournalitemsgenerated
            above.However,thismechanismwillnotworkifthereisanytransfer
            accountsthatarenotreconcileandwearegeneratingthecashbasis
            journalitemsinaforeigncurrency.Inthatspecificcase,weneedto
            generateextrajournalitemsatthegenerationoftheexchangedifference
            journalentrytoensurethisbalanceisresettozeroandthen,willnot
            appearonthetaxreportleadingtoerroneoustaxbaseamount/taxamount.

            :paramlines:                  Theaccount.move.linestowhichfixtheresidualamounts.
            :paramexchange_diff_move_vals:Thecurrentvalsoftheexchangedifferencejournalentry.
            '''
            formoveinlines.move_id:
                account_vals_to_fix={}

                move_values=move._collect_tax_cash_basis_values()

                #Thecashbasisdoesn'tneedtobehandleforthismovebecausethereisanotherpaymentterm
                #linethatisnotyetfullypaid.
                ifnotmove_valuesornotmove_values['is_fully_paid']:
                    continue

                #==========================================================================
                #Addthebalanceofalltaxlinesofthecurrentmoveinorderinorder
                #tocomputetheresidualamountforeachofthem.
                #==========================================================================

                forlineinmove_values['to_process_lines'].filtered(lambdax:notx.reconciled):

                    vals={
                        'currency_id':line.currency_id.id,
                        'partner_id':line.partner_id.id,
                        'tax_ids':[(6,0,line.tax_ids.ids)],
                        'tax_tag_ids':[(6,0,line._convert_tags_for_cash_basis(line.tax_tag_ids).ids)],
                        'debit':line.debit,
                        'credit':line.credit,
                    }

                    ifline.tax_repartition_line_id:
                        #Taxline.
                        grouping_key=self.env['account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(line)
                        ifgrouping_keyinaccount_vals_to_fix:
                            debit=account_vals_to_fix[grouping_key]['debit']+vals['debit']
                            credit=account_vals_to_fix[grouping_key]['credit']+vals['credit']
                            balance=debit-credit

                            account_vals_to_fix[grouping_key].update({
                                'debit':balanceifbalance>0else0,
                                'credit':-balanceifbalance<0else0,
                                'tax_base_amount':account_vals_to_fix[grouping_key]['tax_base_amount']+line.tax_base_amount,
                            })
                        else:
                            account_vals_to_fix[grouping_key]={
                                **vals,
                                'account_id':line.account_id.id,
                                'tax_base_amount':line.tax_base_amount,
                                'tax_repartition_line_id':line.tax_repartition_line_id.id,
                            }
                    elifline.tax_ids:
                        #Baseline.
                        account_to_fix=line.company_id.account_cash_basis_base_account_id
                        ifnotaccount_to_fix:
                            continue

                        grouping_key=self.env['account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(line,account=account_to_fix)

                        ifgrouping_keynotinaccount_vals_to_fix:
                            account_vals_to_fix[grouping_key]={
                                **vals,
                                'account_id':account_to_fix.id,
                            }
                        else:
                            #Multiplebaselinescouldsharethesamekey,ifthesame
                            #cashbasistaxisusedaloneonseverallinesoftheinvoices
                            account_vals_to_fix[grouping_key]['debit']+=vals['debit']
                            account_vals_to_fix[grouping_key]['credit']+=vals['credit']

                #==========================================================================
                #Subtractthebalanceofallpreviouslygeneratedcashbasisjournalentries
                #inordertoretrievetheresidualbalanceofeachinvolvedtransferaccount.
                #==========================================================================

                cash_basis_moves=self.env['account.move'].search([('tax_cash_basis_move_id','=',move.id)])
                forlineincash_basis_moves.line_ids:
                    grouping_key=None
                    ifline.tax_repartition_line_id:
                        #Taxline.
                        grouping_key=self.env['account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(
                            line,
                            account=line.tax_line_id.cash_basis_transition_account_id,
                        )
                    elifline.tax_ids:
                        #Baseline.
                        grouping_key=self.env['account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(
                            line,
                            account=line.company_id.account_cash_basis_base_account_id,
                        )

                    ifgrouping_keynotinaccount_vals_to_fix:
                        continue

                    account_vals_to_fix[grouping_key]['debit']-=line.debit
                    account_vals_to_fix[grouping_key]['credit']-=line.credit

                #==========================================================================
                #Generatetheexchangedifferencejournalitems:
                #-toresetthebalanceofalltransferaccounttozero.
                #-fixroundingissuesonthetaxaccount/basetaxaccount.
                #==========================================================================

                forvaluesinaccount_vals_to_fix.values():
                    balance=values['debit']-values['credit']

                    ifmove.company_currency_id.is_zero(balance):
                        continue

                    ifvalues.get('tax_repartition_line_id'):
                        #Taxline.
                        tax_repartition_line=self.env['account.tax.repartition.line'].browse(values['tax_repartition_line_id'])
                        account=tax_repartition_line.account_idorself.env['account.account'].browse(values['account_id'])

                        sequence=len(exchange_diff_move_vals['line_ids'])
                        exchange_diff_move_vals['line_ids']+=[
                            (0,0,{
                                **values,
                                'name':_('Currencyexchangeratedifference(cashbasis)'),
                                'debit':balanceifbalance>0.0else0.0,
                                'credit':-balanceifbalance<0.0else0.0,
                                'account_id':account.id,
                                'sequence':sequence,
                            }),
                            (0,0,{
                                **values,
                                'name':_('Currencyexchangeratedifference(cashbasis)'),
                                'debit':-balanceifbalance<0.0else0.0,
                                'credit':balanceifbalance>0.0else0.0,
                                'account_id':values['account_id'],
                                'tax_ids':[],
                                'tax_tag_ids':[],
                                'tax_repartition_line_id':False,
                                'sequence':sequence+1,
                            }),
                        ]
                    else:
                        #Baseline.
                        sequence=len(exchange_diff_move_vals['line_ids'])
                        exchange_diff_move_vals['line_ids']+=[
                            (0,0,{
                                **values,
                                'name':_('Currencyexchangeratedifference(cashbasis)'),
                                'debit':balanceifbalance>0.0else0.0,
                                'credit':-balanceifbalance<0.0else0.0,
                                'sequence':sequence,
                            }),
                            (0,0,{
                                **values,
                                'name':_('Currencyexchangeratedifference(cashbasis)'),
                                'debit':-balanceifbalance<0.0else0.0,
                                'credit':balanceifbalance>0.0else0.0,
                                'tax_ids':[],
                                'tax_tag_ids':[],
                                'sequence':sequence+1,
                            }),
                        ]

        ifnotself:
            returnself.env['account.move']

        company=self[0].company_id
        journal=company.currency_exchange_journal_id

        exchange_diff_move_vals={
            'move_type':'entry',
            'date':date.min,
            'journal_id':journal.id,
            'line_ids':[],
        }

        #Fixresidualamounts.
        to_reconcile=_add_lines_to_exchange_difference_vals(self,exchange_diff_move_vals)

        #Fixcashbasisentries,onlyifnotcomingfromthemovereversalwizard.
        is_cash_basis_needed=self[0].account_internal_typein('receivable','payable')
        ifis_cash_basis_neededandnotself._context.get('move_reverse_cancel'):
            _add_cash_basis_lines_to_exchange_difference_vals(self,exchange_diff_move_vals)

        #==========================================================================
        #Createmoveandreconcile.
        #==========================================================================

        ifexchange_diff_move_vals['line_ids']:
            #Checktheconfigurationoftheexchangedifferencejournal.
            ifnotjournal:
                raiseUserError(_("Youshouldconfigurethe'ExchangeGainorLossJournal'inyourcompanysettings,tomanageautomaticallythebookingofaccountingentriesrelatedtodifferencesbetweenexchangerates."))
            ifnotjournal.company_id.expense_currency_exchange_account_id:
                raiseUserError(_("Youshouldconfigurethe'LossExchangeRateAccount'inyourcompanysettings,tomanageautomaticallythebookingofaccountingentriesrelatedtodifferencesbetweenexchangerates."))
            ifnotjournal.company_id.income_currency_exchange_account_id.id:
                raiseUserError(_("Youshouldconfigurethe'GainExchangeRateAccount'inyourcompanysettings,tomanageautomaticallythebookingofaccountingentriesrelatedtodifferencesbetweenexchangerates."))

            exchange_diff_move_vals['date']=max(exchange_diff_move_vals['date'],company._get_user_fiscal_lock_date()+timedelta(days=1))

            exchange_move=self.env['account.move'].create(exchange_diff_move_vals)
            exchange_move.line_ids.write({'tax_exigible':True})#Enforceexigibilityincasesomecashbasisadjustmentsweremadeinthisexchangedifference
        else:
            returnNone

        #Reconcilelinestothenewlycreatedexchangedifferencejournalentrybycreatingmorepartials.
        partials_vals_list=[]
        forsource_line,sequenceinto_reconcile:
            exchange_diff_line=exchange_move.line_ids[sequence]

            ifsource_line.company_currency_id.is_zero(source_line.amount_residual):
                exchange_field='amount_residual_currency'
            else:
                exchange_field='amount_residual'

            ifexchange_diff_line[exchange_field]>0.0:
                debit_line=exchange_diff_line
                credit_line=source_line
            else:
                debit_line=source_line
                credit_line=exchange_diff_line

            partials_vals_list.append({
                'amount':abs(source_line.amount_residual),
                'debit_amount_currency':abs(debit_line.amount_residual_currency),
                'credit_amount_currency':abs(credit_line.amount_residual_currency),
                'debit_move_id':debit_line.id,
                'credit_move_id':credit_line.id,
            })

        self.env['account.partial.reconcile'].create(partials_vals_list)

        returnexchange_move

    defreconcile(self):
        '''Reconcilethecurrentmovelinesalltogether.
        :return:Adictionaryrepresentingasummaryofwhathasbeendoneduringthereconciliation:
                *partials:            Arecorsetofallaccount.partial.reconcilecreatedduringthereconciliation.
                *full_reconcile:      Anaccount.full.reconcilerecordcreatedwhenthereisnothinglefttoreconcile
                                        intheinvolvedlines.
                *tax_cash_basis_moves:Anaccount.moverecordsetrepresentingthetaxcashbasisjournalentries.
        '''
        results={}

        ifnotself:
            returnresults

        #Listunpaidinvoices
        not_paid_invoices=self.move_id.filtered(
            lambdamove:move.is_invoice(include_receipts=True)andmove.payment_statenotin('paid','in_payment')
        )

        #====Checkthelinescanbereconciledtogether====
        company=None
        account=None
        forlineinself:
            ifline.reconciled:
                raiseUserError(_("Youaretryingtoreconcilesomeentriesthatarealreadyreconciled."))
            ifnotline.account_id.reconcileandline.account_id.internal_type!='liquidity':
                raiseUserError(_("Account%sdoesnotallowreconciliation.Firstchangetheconfigurationofthisaccounttoallowit.")
                                %line.account_id.display_name)
            ifline.move_id.state!='posted':
                raiseUserError(_('Youcanonlyreconcilepostedentries.'))
            ifcompanyisNone:
                company=line.company_id
            elifline.company_id!=company:
                raiseUserError(_("Entriesdoesn'tbelongtothesamecompany:%s!=%s")
                                %(company.display_name,line.company_id.display_name))
            ifaccountisNone:
                account=line.account_id
            elifline.account_id!=account:
                raiseUserError(_("Entriesarenotfromthesameaccount:%s!=%s")
                                %(account.display_name,line.account_id.display_name))

        sorted_lines=self.sorted(key=lambdaline:(line.date_maturityorline.date,line.currency_id))

        #====Collectallinvolvedlinesthroughtheexistingreconciliation====

        involved_lines=sorted_lines
        involved_partials=self.env['account.partial.reconcile']
        current_lines=involved_lines
        current_partials=involved_partials
        whilecurrent_lines:
            current_partials=(current_lines.matched_debit_ids+current_lines.matched_credit_ids)-current_partials
            involved_partials+=current_partials
            current_lines=(current_partials.debit_move_id+current_partials.credit_move_id)-current_lines
            involved_lines+=current_lines

        #====Createpartials====

        partials=self.env['account.partial.reconcile'].create(sorted_lines._prepare_reconciliation_partials())

        #Tracknewlycreatedpartials.
        results['partials']=partials
        involved_partials+=partials

        #====Createentriesforcashbasistaxes====

        is_cash_basis_needed=account.company_id.tax_exigibilityandaccount.user_type_id.typein('receivable','payable')
        ifis_cash_basis_neededandnotself._context.get('move_reverse_cancel'):
            tax_cash_basis_moves=partials._create_tax_cash_basis_moves()
            results['tax_cash_basis_moves']=tax_cash_basis_moves

        #====Checkifafullreconcileisneeded====

        ifinvolved_lines[0].currency_idandall(line.currency_id==involved_lines[0].currency_idforlineininvolved_lines):
            is_full_needed=all(line.currency_id.is_zero(line.amount_residual_currency)forlineininvolved_lines)
        else:
            is_full_needed=all(line.company_currency_id.is_zero(line.amount_residual)forlineininvolved_lines)

        ifis_full_needed:

            #====Createtheexchangedifferencemove====

            ifself._context.get('no_exchange_difference'):
                exchange_move=None
            else:
                exchange_move=involved_lines._create_exchange_difference_move()
                ifexchange_move:
                    exchange_move_lines=exchange_move.line_ids.filtered(lambdaline:line.account_id==account)

                    #Tracknewlycreatedlines.
                    involved_lines+=exchange_move_lines

                    #Tracknewlycreatedpartials.
                    exchange_diff_partials=exchange_move_lines.matched_debit_ids\
                                             +exchange_move_lines.matched_credit_ids
                    involved_partials+=exchange_diff_partials
                    results['partials']+=exchange_diff_partials

                    exchange_move._post(soft=False)

            #====Createthefullreconcile====

            results['full_reconcile']=self.env['account.full.reconcile'].create({
                'exchange_move_id':exchange_moveandexchange_move.id,
                'partial_reconcile_ids':[(6,0,involved_partials.ids)],
                'reconciled_line_ids':[(6,0,involved_lines.ids)],
            })

        #Triggeractionforpaidinvoices
        not_paid_invoices\
            .filtered(lambdamove:move.payment_statein('paid','in_payment'))\
            .action_invoice_paid()

        returnresults

    defremove_move_reconcile(self):
        """Undoareconciliation"""
        (self.matched_debit_ids+self.matched_credit_ids).unlink()

    def_copy_data_extend_business_fields(self,values):
        '''Hookallowingcopyingbusinessfieldsundercertainconditions.
        E.g.Thelinktothesaleorderlinesmustbepreservedincaseofarefund.
        '''
        self.ensure_one()

    defcopy_data(self,default=None):
        res=super(AccountMoveLine,self).copy_data(default=default)

        forline,valuesinzip(self,res):
            #Don'tcopythenameofapaymenttermline.
            ifline.move_id.is_invoice()andline.account_id.user_type_id.typein('receivable','payable'):
                values['name']=''
            #Don'tcopyrestrictedfieldsofnotes
            ifline.display_typein('line_section','line_note'):
                values['amount_currency']=0
                values['debit']=0
                values['credit']=0
                values['account_id']=False
            ifself._context.get('include_business_fields'):
                line._copy_data_extend_business_fields(values)
        returnres

    #-------------------------------------------------------------------------
    #MISC
    #-------------------------------------------------------------------------

    def_get_analytic_tag_ids(self):
        self.ensure_one()
        returnself.analytic_tag_ids.filtered(lambdar:notr.active_analytic_distribution).ids

    defcreate_analytic_lines(self):
        """Createanalyticitemsuponvalidationofanaccount.move.linehavingananalyticaccountorananalyticdistribution.
        """
        lines_to_create_analytic_entries=self.env['account.move.line']
        analytic_line_vals=[]
        forobj_lineinself:
            fortaginobj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
                fordistributionintag.analytic_distribution_ids:
                    analytic_line_vals.append(obj_line._prepare_analytic_distribution_line(distribution))
            ifobj_line.analytic_account_id:
                lines_to_create_analytic_entries|=obj_line

        #createanalyticentriesinbatch
        iflines_to_create_analytic_entries:
            analytic_line_vals+=lines_to_create_analytic_entries._prepare_analytic_line()

        self.env['account.analytic.line'].create(analytic_line_vals)

    def_prepare_analytic_line(self):
        """Preparethevaluesusedtocreate()anaccount.analytic.lineuponvalidationofanaccount.move.linehaving
            ananalyticaccount.Thismethodisintendedtobeextendedinothermodules.
            :returnlistofvaluestocreateanalytic.line
            :rtypelist
        """
        result=[]
        formove_lineinself:
            amount=(move_line.creditor0.0)-(move_line.debitor0.0)
            default_name=move_line.nameor(move_line.refor'/'+'--'+(move_line.partner_idandmove_line.partner_id.nameor'/'))
            result.append({
                'name':default_name,
                'date':move_line.date,
                'account_id':move_line.analytic_account_id.id,
                'group_id':move_line.analytic_account_id.group_id.id,
                'tag_ids':[(6,0,move_line._get_analytic_tag_ids())],
                'unit_amount':move_line.quantity,
                'product_id':move_line.product_idandmove_line.product_id.idorFalse,
                'product_uom_id':move_line.product_uom_idandmove_line.product_uom_id.idorFalse,
                'amount':amount,
                'general_account_id':move_line.account_id.id,
                'ref':move_line.ref,
                'move_id':move_line.id,
                'user_id':move_line.move_id.invoice_user_id.idorself._uid,
                'partner_id':move_line.partner_id.id,
                'company_id':move_line.analytic_account_id.company_id.idormove_line.move_id.company_id.id,
            })
        returnresult

    def_prepare_analytic_distribution_line(self,distribution):
        """Preparethevaluesusedtocreate()anaccount.analytic.lineuponvalidationofanaccount.move.linehaving
            analytictagswithanalyticdistribution.
        """
        self.ensure_one()
        amount=-self.balance*distribution.percentage/100.0
        default_name=self.nameor(self.refor'/'+'--'+(self.partner_idandself.partner_id.nameor'/'))
        return{
            'name':default_name,
            'date':self.date,
            'account_id':distribution.account_id.id,
            'group_id':distribution.account_id.group_id.id,
            'partner_id':self.partner_id.id,
            'tag_ids':[(6,0,[distribution.tag_id.id]+self._get_analytic_tag_ids())],
            'unit_amount':self.quantity,
            'product_id':self.product_idandself.product_id.idorFalse,
            'product_uom_id':self.product_uom_idandself.product_uom_id.idorFalse,
            'amount':amount,
            'general_account_id':self.account_id.id,
            'ref':self.ref,
            'move_id':self.id,
            'user_id':self.move_id.invoice_user_id.idorself._uid,
            'company_id':distribution.account_id.company_id.idorself.company_id.idorself.env.company.id,
        }

    @api.model
    def_query_get(self,domain=None):
        self.check_access_rights('read')

        context=dict(self._contextor{})
        domain=domainor[]
        ifnotisinstance(domain,(list,tuple)):
            domain=ast.literal_eval(domain)

        date_field='date'
        ifcontext.get('aged_balance'):
            date_field='date_maturity'
        ifcontext.get('date_to'):
            domain+=[(date_field,'<=',context['date_to'])]
        ifcontext.get('date_from'):
            ifnotcontext.get('strict_range'):
                domain+=['|',(date_field,'>=',context['date_from']),('account_id.user_type_id.include_initial_balance','=',True)]
            elifcontext.get('initial_bal'):
                domain+=[(date_field,'<',context['date_from'])]
            else:
                domain+=[(date_field,'>=',context['date_from'])]

        ifcontext.get('journal_ids'):
            domain+=[('journal_id','in',context['journal_ids'])]

        state=context.get('state')
        ifstateandstate.lower()!='all':
            domain+=[('parent_state','=',state)]

        ifcontext.get('company_id'):
            domain+=[('company_id','=',context['company_id'])]
        elifcontext.get('allowed_company_ids'):
            domain+=[('company_id','in',self.env.companies.ids)]
        else:
            domain+=[('company_id','=',self.env.company.id)]

        ifcontext.get('reconcile_date'):
            domain+=['|',('reconciled','=',False),'|',('matched_debit_ids.max_date','>',context['reconcile_date']),('matched_credit_ids.max_date','>',context['reconcile_date'])]

        ifcontext.get('account_tag_ids'):
            domain+=[('account_id.tag_ids','in',context['account_tag_ids'].ids)]

        ifcontext.get('account_ids'):
            domain+=[('account_id','in',context['account_ids'].ids)]

        ifcontext.get('analytic_tag_ids'):
            domain+=[('analytic_tag_ids','in',context['analytic_tag_ids'].ids)]

        ifcontext.get('analytic_account_ids'):
            domain+=[('analytic_account_id','in',context['analytic_account_ids'].ids)]

        ifcontext.get('partner_ids'):
            domain+=[('partner_id','in',context['partner_ids'].ids)]

        ifcontext.get('partner_categories'):
            domain+=[('partner_id.category_id','in',context['partner_categories'].ids)]

        where_clause=""
        where_clause_params=[]
        tables=''
        ifdomain:
            domain.append(('display_type','notin',('line_section','line_note')))
            domain.append(('parent_state','!=','cancel'))

            query=self._where_calc(domain)

            #Wrapthequerywith'company_idIN(...)'toavoidbypassingcompanyaccessrights.
            self._apply_ir_rules(query)

            tables,where_clause,where_clause_params=query.get_sql()
        returntables,where_clause,where_clause_params

    def_reconciled_lines(self):
        ids=[]
        foramlinself.filtered('account_id.reconcile'):
            ids.extend([r.debit_move_id.idforrinaml.matched_debit_ids]ifaml.credit>0else[r.credit_move_id.idforrinaml.matched_credit_ids])
            ids.append(aml.id)
        returnids

    defopen_reconcile_view(self):
        action=self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
        ids=self._reconciled_lines()
        action['domain']=[('id','in',ids)]
        returnaction

    defaction_automatic_entry(self):
        action=self.env['ir.actions.act_window']._for_xml_id('account.account_automatic_entry_wizard_action')
        #Forcethevaluesofthemovelineinthecontexttoavoidissues
        ctx=dict(self.env.context)
        ctx.pop('active_id',None)
        ctx.pop('default_journal_id',None)
        ctx['active_ids']=self.ids
        ctx['active_model']='account.move.line'
        action['context']=ctx
        returnaction

    @api.model
    def_get_suspense_moves_domain(self):
        return[
            ('move_id.to_check','=',True),
            ('full_reconcile_id','=',False),
            ('statement_line_id','!=',False),
        ]

    def_get_attachment_domains(self):
        self.ensure_one()
        domains=[[('res_model','=','account.move'),('res_id','=',self.move_id.id)]]
        ifself.statement_id:
            domains.append([('res_model','=','account.bank.statement'),('res_id','=',self.statement_id.id)])
        ifself.payment_id:
            domains.append([('res_model','=','account.payment'),('res_id','=',self.payment_id.id)])
        returndomains

    def_convert_tags_for_cash_basis(self,tags):
        """Cashbasisentriesaremanagedbythetaxreportjustlikemiscoperations.
        Soitmeansthatthetaxreportwillnotapplyanyadditionalmultiplicator
        tothebalanceofthecashbasislines.

        Forinvoicesmovelineswhosemultiplicatorwouldhavebeen-1(iftheir
        taxeshadnotCABA),itwillhencecausesigninversionifwedirectlycopy
        thetagsfromthoselines.Instead,weneedtoinvertallthesignsfromthese
        tags(iftheycomefromtaxreportlines;tagscreatedindataforfinancial
        reportswillstayonchanged).
        """
        self.ensure_one()
        tax_multiplicator=(self.journal_id.type=='sale'and-1or1)*(self.move_id.move_typein('in_refund','out_refund')and-1or1)
        iftax_multiplicator==-1:
            #Taketheoppositetagsinstead
            returnself._revert_signed_tags(tags)

        returntags

    @api.model
    def_revert_signed_tags(self,tags):
        rslt=self.env['account.account.tag']
        fortagintags:
            iftag.tax_report_line_ids:
                #tagcreatedbyanaccount.tax.report.line
                new_tag=tag.tax_report_line_ids[0].tag_ids.filtered(lambdax:x.tax_negate!=tag.tax_negate)
                rslt+=new_tag
            else:
                #tagcreatedindataforusebyanaccount.financial.html.report.line
                rslt+=tag

        returnrslt

    def_get_downpayment_lines(self):
        '''Returnthedownpaymentmovelinesassociatedwiththemoveline.
        Thismethodisoverriddeninthesaleordermodule.
        '''
        returnself.env['account.move.line']
