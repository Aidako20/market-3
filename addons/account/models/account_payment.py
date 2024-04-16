#-*-coding:utf-8-*-
fromlxmlimportetree

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError,ValidationError


classAccountPaymentMethod(models.Model):
    _name="account.payment.method"
    _description="PaymentMethods"
    _order='sequence'

    name=fields.Char(required=True,translate=True)
    code=fields.Char(required=True) #Forinternalidentification
    payment_type=fields.Selection([('inbound','Inbound'),('outbound','Outbound')],required=True)
    sequence=fields.Integer(help='UsedtoorderMethodsintheformview',default=10)


classAccountPayment(models.Model):
    _name="account.payment"
    _inherits={'account.move':'move_id'}
    _inherit=['mail.thread','mail.activity.mixin']
    _description="Payments"
    _order="datedesc,namedesc"
    _check_company_auto=True

    def_get_default_journal(self):
        '''Retrievethedefaultjournalfortheaccount.payment.
        /!\Thismethodwillnotoverridethemethodin'account.move'becausetheORM
        doesn'tallowoverridingmethodsusing_inherits.Then,thismethodwillbecalled
        manuallyin'create'and'new'.
        :return:Anaccount.journalrecord.
        '''
        returnself.env['account.move']._search_default_journal(('bank','cash'))

    #==Businessfields==
    move_id=fields.Many2one(
        comodel_name='account.move',
        string='JournalEntry',required=True,readonly=True,ondelete='cascade',
        check_company=True)

    is_reconciled=fields.Boolean(string="IsReconciled",store=True,
        compute='_compute_reconciliation_status',
        help="Technicalfieldindicatingifthepaymentisalreadyreconciled.")
    is_matched=fields.Boolean(string="IsMatchedWithaBankStatement",store=True,
        compute='_compute_reconciliation_status',
        help="Technicalfieldindicatingifthepaymenthasbeenmatchedwithastatementline.")
    available_partner_bank_ids=fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
    )
    partner_bank_id=fields.Many2one('res.partner.bank',string="RecipientBankAccount",
        readonly=False,store=True,
        compute='_compute_partner_bank_id',
        domain="[('id','in',available_partner_bank_ids)]",
        check_company=True)
    is_internal_transfer=fields.Boolean(string="IsInternalTransfer",
        readonly=False,store=True,
        compute="_compute_is_internal_transfer")
    qr_code=fields.Char(string="QRCode",
        compute="_compute_qr_code",
        help="QR-codereportURLtousetogeneratetheQR-codetoscanwithabankingapptoperformthispayment.")

    #==Paymentmethodsfields==
    payment_method_id=fields.Many2one('account.payment.method',string='PaymentMethod',
        readonly=False,store=True,
        compute='_compute_payment_method_id',
        domain="[('id','in',available_payment_method_ids)]",
        help="Manual:Getpaidbycash,checkoranyothermethodoutsideofFlectra.\n"\
        "Electronic:Getpaidautomaticallythroughapaymentacquirerbyrequestingatransactiononacardsavedbythecustomerwhenbuyingorsubscribingonline(paymenttoken).\n"\
        "Check:PaybillbycheckandprintitfromFlectra.\n"\
        "BatchDeposit:Encaseseveralcustomerchecksatoncebygeneratingabatchdeposittosubmittoyourbank.WhenencodingthebankstatementinFlectra,youaresuggestedtoreconcilethetransactionwiththebatchdeposit.Toenablebatchdeposit,moduleaccount_batch_paymentmustbeinstalled.\n"\
        "SEPACreditTransfer:PaybillfromaSEPACreditTransferfileyousubmittoyourbank.Toenablesepacredittransfer,moduleaccount_sepamustbeinstalled")
    available_payment_method_ids=fields.Many2many('account.payment.method',
        compute='_compute_payment_method_fields')
    hide_payment_method=fields.Boolean(
        compute='_compute_payment_method_fields',
        help="Technicalfieldusedtohidethepaymentmethodiftheselectedjournalhasonlyoneavailablewhichis'manual'")

    #==Synchronizedfieldswiththeaccount.move.lines==
    amount=fields.Monetary(currency_field='currency_id')
    payment_type=fields.Selection([
        ('outbound','SendMoney'),
        ('inbound','ReceiveMoney'),
    ],string='PaymentType',default='inbound',required=True)
    partner_type=fields.Selection([
        ('customer','Customer'),
        ('supplier','Vendor'),
    ],default='customer',tracking=True,required=True)
    payment_reference=fields.Char(string="PaymentReference",copy=False,
        help="Referenceofthedocumentusedtoissuethispayment.Eg.checknumber,filename,etc.")
    currency_id=fields.Many2one('res.currency',string='Currency',store=True,readonly=False,
        compute='_compute_currency_id',
        help="Thepayment'scurrency.")
    partner_id=fields.Many2one(
        comodel_name='res.partner',
        string="Customer/Vendor",
        store=True,readonly=False,ondelete='restrict',
        compute='_compute_partner_id',
        domain="['|',('parent_id','=',False),('is_company','=',True)]",
        check_company=True)
    destination_account_id=fields.Many2one(
        comodel_name='account.account',
        string='DestinationAccount',
        store=True,readonly=False,
        compute='_compute_destination_account_id',
        domain="[('user_type_id.type','in',('receivable','payable')),('company_id','=',company_id)]",
        check_company=True)

    #==Statbuttons==
    reconciled_invoice_ids=fields.Many2many('account.move',string="ReconciledInvoices",
        compute='_compute_stat_buttons_from_reconciliation',
        help="Invoiceswhosejournalitemshavebeenreconciledwiththesepayments.")
    reconciled_invoices_count=fields.Integer(string="#ReconciledInvoices",
        compute="_compute_stat_buttons_from_reconciliation")
    reconciled_bill_ids=fields.Many2many('account.move',string="ReconciledBills",
        compute='_compute_stat_buttons_from_reconciliation',
        help="Invoiceswhosejournalitemshavebeenreconciledwiththesepayments.")
    reconciled_bills_count=fields.Integer(string="#ReconciledBills",
        compute="_compute_stat_buttons_from_reconciliation")
    reconciled_statement_ids=fields.Many2many('account.bank.statement',string="ReconciledStatements",
        compute='_compute_stat_buttons_from_reconciliation',
        help="Statementsmatchedtothispayment")
    reconciled_statements_count=fields.Integer(string="#ReconciledStatements",
        compute="_compute_stat_buttons_from_reconciliation")

    #==Displaypurposefields==
    payment_method_code=fields.Char(
        related='payment_method_id.code',
        help="Technicalfieldusedtoadapttheinterfacetothepaymenttypeselected.")
    show_partner_bank_account=fields.Boolean(
        compute='_compute_show_require_partner_bank',
        help="Technicalfieldusedtoknowwhetherthefield`partner_bank_id`needstobedisplayedornotinthepaymentsformviews")
    require_partner_bank_account=fields.Boolean(
        compute='_compute_show_require_partner_bank',
        help="Technicalfieldusedtoknowwhetherthefield`partner_bank_id`needstoberequiredornotinthepaymentsformviews")
    country_code=fields.Char(related='company_id.country_id.code')

    _sql_constraints=[
        (
            'check_amount_not_negative',
            'CHECK(amount>=0.0)',
            "Thepaymentamountcannotbenegative.",
        ),
    ]

    #-------------------------------------------------------------------------
    #HELPERS
    #-------------------------------------------------------------------------

    def_seek_for_lines(self):
        '''Helperusedtodispatchthejournalitemsbetween:
        -Thelinesusingthetemporaryliquidityaccount.
        -Thelinesusingthecounterpartaccount.
        -Thelinesbeingthewrite-offlines.
        :return:(liquidity_lines,counterpart_lines,writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines=self.env['account.move.line']
        counterpart_lines=self.env['account.move.line']
        writeoff_lines=self.env['account.move.line']

        forlineinself.move_id.line_ids:
            ifline.account_idin(
                    self.journal_id.default_account_id,
                    self.journal_id.payment_debit_account_id,
                    self.journal_id.payment_credit_account_id,
            ):
                liquidity_lines+=line
            elifline.account_id.internal_typein('receivable','payable')orline.account_id==line.company_id.transfer_account_id:
                counterpart_lines+=line
            else:
                writeoff_lines+=line

        returnliquidity_lines,counterpart_lines,writeoff_lines

    def_prepare_payment_display_name(self):
        '''
        Hookmethodforinherit
        Whenyouwanttosetanewnameforpayment,youcanextendthismethod
        '''
        return{
            'outbound-customer':_("CustomerReimbursement"),
            'inbound-customer':_("CustomerPayment"),
            'outbound-supplier':_("VendorPayment"),
            'inbound-supplier':_("VendorReimbursement"),
        }

    def_prepare_move_line_default_vals(self,write_off_line_vals=None):
        '''Preparethedictionarytocreatethedefaultaccount.move.linesforthecurrentpayment.
        :paramwrite_off_line_vals:Optionaldictionarytocreateawrite-offaccount.move.lineeasilycontaining:
            *amount:      Theamounttobeaddedtothecounterpartamount.
            *name:        Thelabeltosetontheline.
            *account_id:  Theaccountonwhichcreatethewrite-off.
        :return:Alistofpythondictionarytobepassedtotheaccount.move.line's'create'method.
        '''
        self.ensure_one()
        write_off_line_vals=write_off_line_valsor{}

        ifnotself.journal_id.payment_debit_account_idornotself.journal_id.payment_credit_account_id:
            raiseUserError(_(
                "Youcan'tcreateanewpaymentwithoutanoutstandingpayments/receiptsaccountsetonthe%sjournal.",
                self.journal_id.display_name))

        #Computeamounts.
        write_off_amount_currency=write_off_line_vals.get('amount',0.0)

        ifself.payment_type=='inbound':
            #Receivemoney.
            liquidity_amount_currency=self.amount
        elifself.payment_type=='outbound':
            #Sendmoney.
            liquidity_amount_currency=-self.amount
            write_off_amount_currency*=-1
        else:
            liquidity_amount_currency=write_off_amount_currency=0.0

        write_off_balance=self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance=self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency=-liquidity_amount_currency-write_off_amount_currency
        counterpart_balance=-liquidity_balance-write_off_balance
        currency_id=self.currency_id.id

        ifself.is_internal_transfer:
            ifself.payment_type=='inbound':
                liquidity_line_name=_('Transferto%s',self.journal_id.name)
            else:#payment.payment_type=='outbound':
                liquidity_line_name=_('Transferfrom%s',self.journal_id.name)
        else:
            liquidity_line_name=self.payment_reference

        #Computeadefaultlabeltosetonthejournalitems.

        payment_display_name=self._prepare_payment_display_name()

        default_line_name=self.env['account.move.line']._get_default_line_name(
            _("InternalTransfer")ifself.is_internal_transferelsepayment_display_name['%s-%s'%(self.payment_type,self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list=[
            #Liquidityline.
            {
                'name':liquidity_line_nameordefault_line_name,
                'date_maturity':self.date,
                'amount_currency':liquidity_amount_currency,
                'currency_id':currency_id,
                'debit':liquidity_balanceifliquidity_balance>0.0else0.0,
                'credit':-liquidity_balanceifliquidity_balance<0.0else0.0,
                'partner_id':self.partner_id.id,
                'account_id':self.journal_id.payment_credit_account_id.idifliquidity_balance<0.0elseself.journal_id.payment_debit_account_id.id,
            },
            #Receivable/Payable.
            {
                'name':self.payment_referenceordefault_line_name,
                'date_maturity':self.date,
                'amount_currency':counterpart_amount_currency,
                'currency_id':currency_id,
                'debit':counterpart_balanceifcounterpart_balance>0.0else0.0,
                'credit':-counterpart_balanceifcounterpart_balance<0.0else0.0,
                'partner_id':self.partner_id.id,
                'account_id':self.destination_account_id.id,
            },
        ]
        ifnotself.currency_id.is_zero(write_off_amount_currency):
            #Write-offline.
            line_vals_list.append({
                'name':write_off_line_vals.get('name')ordefault_line_name,
                'amount_currency':write_off_amount_currency,
                'currency_id':currency_id,
                'debit':write_off_balanceifwrite_off_balance>0.0else0.0,
                'credit':-write_off_balanceifwrite_off_balance<0.0else0.0,
                'partner_id':self.partner_id.id,
                'account_id':write_off_line_vals.get('account_id'),
            })
        returnline_vals_list

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('move_id.line_ids.amount_residual','move_id.line_ids.amount_residual_currency','move_id.line_ids.account_id')
    def_compute_reconciliation_status(self):
        '''Computethefieldindicatingifthepaymentsarealreadyreconciledwithsomething.
        Thisfieldisusedfordisplaypurpose(e.g.displaythe'reconcile'buttonredirectingtothereconciliation
        widget).
        '''
        forpayinself:
            liquidity_lines,counterpart_lines,writeoff_lines=pay._seek_for_lines()

            ifnotpay.currency_idornotpay.id:
                pay.is_reconciled=False
                pay.is_matched=False
            elifpay.currency_id.is_zero(pay.amount):
                pay.is_reconciled=True
                pay.is_matched=True
            else:
                residual_field='amount_residual'ifpay.currency_id==pay.company_id.currency_idelse'amount_residual_currency'
                ifpay.journal_id.default_account_idandpay.journal_id.default_account_idinliquidity_lines.account_id:
                    #Allowusermanagingpaymentswithoutanystatementlinesbyusingthebankaccountdirectly.
                    #Inthatcase,theusermanagestransactionsonlyusingtheregisterpaymentwizard.
                    pay.is_matched=True
                else:
                    pay.is_matched=pay.currency_id.is_zero(sum(liquidity_lines.mapped(residual_field)))

                reconcile_lines=(counterpart_lines+writeoff_lines).filtered(lambdaline:line.account_id.reconcile)
                pay.is_reconciled=pay.currency_id.is_zero(sum(reconcile_lines.mapped(residual_field)))

    @api.model
    def_get_method_codes_using_bank_account(self):
        return['manual']

    @api.model
    def_get_method_codes_needing_bank_account(self):
        return[]

    @api.depends('payment_method_code')
    def_compute_show_require_partner_bank(self):
        """Computesifthedestinationbankaccountmustbedisplayedinthepaymentformview.Bydefault,it
        won'tbedisplayedbutsomemodulesmightchangethat,dependingonthepaymenttype."""
        forpaymentinself:
            payment.show_partner_bank_account=payment.payment_method_codeinself._get_method_codes_using_bank_account()
            payment.require_partner_bank_account=payment.state=='draft'andpayment.payment_method_codeinself._get_method_codes_needing_bank_account()

    @api.depends('partner_id','company_id','payment_type')
    def_compute_available_partner_bank_ids(self):
        forpayinself:
            ifpay.payment_type=='inbound':
                pay.available_partner_bank_ids=pay.journal_id.bank_account_id
            else:
                pay.available_partner_bank_ids=pay.partner_id.bank_ids\
                        .filtered(lambdax:x.company_id.idin(False,pay.company_id.id))._origin

    @api.depends('available_partner_bank_ids','journal_id')
    def_compute_partner_bank_id(self):
        '''Thedefaultpartner_bank_idwillbethefirstavailableonthepartner.'''
        forpayinself:
            ifpay.partner_bank_idnotinpay.available_partner_bank_ids._origin:
                pay.partner_bank_id=pay.available_partner_bank_ids[:1]._origin

    @api.depends('partner_id','destination_account_id','journal_id')
    def_compute_is_internal_transfer(self):
        forpaymentinself:
            is_partner_ok=payment.partner_id==payment.journal_id.company_id.partner_id
            is_account_ok=payment.destination_account_idandpayment.destination_account_id==payment.journal_id.company_id.transfer_account_id
            payment.is_internal_transfer=is_partner_okandis_account_ok

    @api.depends('payment_type','journal_id')
    def_compute_payment_method_id(self):
        '''Computethe'payment_method_id'field.
        Thisfieldisnotcomputedin'_compute_payment_method_fields'becauseit'sastorededitableone.
        '''
        forpayinself:
            ifpay.payment_type=='inbound':
                available_payment_methods=pay.journal_id.inbound_payment_method_ids
            else:
                available_payment_methods=pay.journal_id.outbound_payment_method_ids

            #Selectthefirstavailableonebydefault.
            ifpay.payment_method_idinavailable_payment_methods:
                pay.payment_method_id=pay.payment_method_id
            elifavailable_payment_methods:
                pay.payment_method_id=available_payment_methods[0]._origin
            else:
                pay.payment_method_id=False

    @api.depends('payment_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def_compute_payment_method_fields(self):
        forpayinself:
            ifpay.payment_type=='inbound':
                pay.available_payment_method_ids=pay.journal_id.inbound_payment_method_ids
            else:
                pay.available_payment_method_ids=pay.journal_id.outbound_payment_method_ids

            pay.hide_payment_method=len(pay.available_payment_method_ids)==1andpay.available_payment_method_ids.code=='manual'

    @api.depends('journal_id')
    def_compute_currency_id(self):
        forpayinself:
            pay.currency_id=pay.journal_id.currency_idorpay.journal_id.company_id.currency_id

    @api.depends('is_internal_transfer')
    def_compute_partner_id(self):
        forpayinself:
            ifpay.is_internal_transfer:
                pay.partner_id=pay.journal_id.company_id.partner_id
            elifpay.partner_id==pay.journal_id.company_id.partner_id:
                pay.partner_id=False
            else:
                pay.partner_id=pay.partner_id

    @api.depends('journal_id','partner_id','partner_type','is_internal_transfer')
    def_compute_destination_account_id(self):
        self.destination_account_id=False
        forpayinself:
            ifpay.is_internal_transfer:
                pay.destination_account_id=pay.journal_id.company_id.transfer_account_id
            elifpay.partner_type=='customer':
                #Receivemoneyfrominvoiceorsendmoneytorefundit.
                ifpay.partner_id:
                    pay.destination_account_id=pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id=self.env['account.account'].search([
                        ('company_id','=',pay.company_id.id),
                        ('internal_type','=','receivable'),
                        ('deprecated','=',False),
                    ],limit=1)
            elifpay.partner_type=='supplier':
                #Sendmoneytopayabillorreceivemoneytorefundit.
                ifpay.partner_id:
                    pay.destination_account_id=pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id=self.env['account.account'].search([
                        ('company_id','=',pay.company_id.id),
                        ('internal_type','=','payable'),
                        ('deprecated','=',False),
                    ],limit=1)

    @api.depends('partner_bank_id','amount','ref','currency_id','journal_id','move_id.state',
                 'payment_method_id','payment_type')
    def_compute_qr_code(self):
        forpayinself:
            ifpay.statein('draft','posted')\
                andpay.partner_bank_id\
                andpay.payment_method_id.code=='manual'\
                andpay.payment_type=='outbound'\
                andpay.currency_id:

                ifpay.partner_bank_id:
                    qr_code=pay.partner_bank_id.build_qr_code_base64(pay.amount,pay.ref,pay.ref,pay.currency_id,pay.partner_id)
                else:
                    qr_code=None

                ifqr_code:
                    pay.qr_code='''
                        <br/>
                        <imgclass="borderborder-darkrounded"src="{qr_code}"/>
                        <br/>
                        <strongclass="text-center">{txt}</strong>
                        '''.format(txt=_('Scanmewithyourbankingapp.'),
                                   qr_code=qr_code)
                    continue

            pay.qr_code=None

    @api.depends('move_id.line_ids.matched_debit_ids','move_id.line_ids.matched_credit_ids')
    def_compute_stat_buttons_from_reconciliation(self):
        '''Retrievetheinvoicesreconciledtothepaymentsthroughthereconciliation(account.partial.reconcile).'''
        stored_payments=self.filtered('id')
        ifnotstored_payments:
            self.reconciled_invoice_ids=False
            self.reconciled_invoices_count=0
            self.reconciled_bill_ids=False
            self.reconciled_bills_count=0
            self.reconciled_statement_ids=False
            self.reconciled_statements_count=0
            return

        self.env['account.journal'].flush(fnames=['payment_debit_account_id','payment_credit_account_id'])
        self.env['account.payment'].flush(fnames=['move_id'])
        self.env['account.move'].flush(fnames=['move_type','payment_id','statement_line_id','journal_id'])
        self.env['account.move.line'].flush(fnames=['move_id','account_id','statement_line_id'])
        self.env['account.partial.reconcile'].flush(fnames=['debit_move_id','credit_move_id'])

        self._cr.execute('''
            SELECT
                payment.id,
                ARRAY_AGG(DISTINCTinvoice.id)ASinvoice_ids,
                invoice.move_type
            FROMaccount_paymentpayment
            JOINaccount_movemoveONmove.id=payment.move_id
            JOINaccount_move_linelineONline.move_id=move.id
            JOINaccount_partial_reconcilepartON
                part.debit_move_id=line.id
                OR
                part.credit_move_id=line.id
            JOINaccount_move_linecounterpart_lineON
                part.debit_move_id=counterpart_line.id
                OR
                part.credit_move_id=counterpart_line.id
            JOINaccount_moveinvoiceONinvoice.id=counterpart_line.move_id
            JOINaccount_accountaccountONaccount.id=line.account_id
            WHEREaccount.internal_typeIN('receivable','payable')
                ANDpayment.idIN%(payment_ids)s
                ANDline.id!=counterpart_line.id
                ANDinvoice.move_typein('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt')
            GROUPBYpayment.id,invoice.move_type
        ''',{
            'payment_ids':tuple(stored_payments.ids)
        })
        query_res=self._cr.dictfetchall()
        self.reconciled_invoice_ids=self.reconciled_invoices_count=False
        self.reconciled_bill_ids=self.reconciled_bills_count=False
        forresinquery_res:
            pay=self.browse(res['id'])
            ifres['move_type']inself.env['account.move'].get_sale_types(True):
                pay.reconciled_invoice_ids+=self.env['account.move'].browse(res.get('invoice_ids',[]))
                pay.reconciled_invoices_count=len(res.get('invoice_ids',[]))
            else:
                pay.reconciled_bill_ids+=self.env['account.move'].browse(res.get('invoice_ids',[]))
                pay.reconciled_bills_count=len(res.get('invoice_ids',[]))

        self._cr.execute('''
            SELECT
                payment.id,
                ARRAY_AGG(DISTINCTcounterpart_line.statement_id)ASstatement_ids
            FROMaccount_paymentpayment
            JOINaccount_movemoveONmove.id=payment.move_id
            JOINaccount_journaljournalONjournal.id=move.journal_id
            JOINaccount_move_linelineONline.move_id=move.id
            JOINaccount_accountaccountONaccount.id=line.account_id
            JOINaccount_partial_reconcilepartON
                part.debit_move_id=line.id
                OR
                part.credit_move_id=line.id
            JOINaccount_move_linecounterpart_lineON
                part.debit_move_id=counterpart_line.id
                OR
                part.credit_move_id=counterpart_line.id
            WHERE(account.id=journal.payment_debit_account_idORaccount.id=journal.payment_credit_account_id)
                ANDpayment.idIN%(payment_ids)s
                ANDline.id!=counterpart_line.id
                ANDcounterpart_line.statement_idISNOTNULL
            GROUPBYpayment.id
        ''',{
            'payment_ids':tuple(stored_payments.ids)
        })
        query_res=dict((payment_id,statement_ids)forpayment_id,statement_idsinself._cr.fetchall())

        forpayinself:
            statement_ids=query_res.get(pay.id,[])
            pay.reconciled_statement_ids=[(6,0,statement_ids)]
            pay.reconciled_statements_count=len(statement_ids)

    #-------------------------------------------------------------------------
    #ONCHANGEMETHODS
    #-------------------------------------------------------------------------

    @api.onchange('posted_before','state','journal_id','date')
    def_onchange_journal_date(self):
        #Beforetherecordiscreated,themove_iddoesn'texistyet,andthenamewillnotbe
        #recomputedcorrectlyifwechangethejournalorthedate,leadingtoinconsitencies
        ifnotself.move_id:
            self.name=False

    @api.onchange('journal_id')
    def_onchange_journal(self):
        self.move_id._onchange_journal()

    #-------------------------------------------------------------------------
    #CONSTRAINTMETHODS
    #-------------------------------------------------------------------------

    @api.constrains('payment_method_id')
    def_check_payment_method_id(self):
        '''Ensurethe'payment_method_id'fieldisnotnull.
        Can'tbedoneusingtheregular'required=True'becausethefieldisacomputededitablestoredone.
        '''
        forpayinself:
            ifnotpay.payment_method_id:
                raiseValidationError(_("Pleasedefineapaymentmethodonyourpayment."))

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    @api.model
    deffields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        #OVERRIDEtoaddthe'available_partner_bank_ids'fielddynamicallyinsidetheview.
        #TOBEREMOVEDINMASTER
        res=super().fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
        ifview_type=='form':
            form_view_id=self.env['ir.model.data'].xmlid_to_res_id('account.view_account_payment_form')
            ifres.get('view_id')==form_view_id:
                tree=etree.fromstring(res['arch'])
                iflen(tree.xpath("//field[@name='available_partner_bank_ids']"))==0:
                    #Don'tforcepeopletoupdatetheaccountmodule.
                    form_view=self.env.ref('account.view_account_payment_form')
                    arch_tree=etree.fromstring(form_view.arch)
                    ifarch_tree.tag=='form':
                        arch_tree.insert(0,etree.Element('field',attrib={
                            'name':'available_partner_bank_ids',
                            'invisible':'1',
                        }))
                        form_view.sudo().write({'arch':etree.tostring(arch_tree,encoding='unicode')})
                        returnsuper().fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)

        returnres

    @api.model_create_multi
    defcreate(self,vals_list):
        #OVERRIDE
        write_off_line_vals_list=[]

        forvalsinvals_list:

            #Hacktoaddacustomwrite-offline.
            write_off_line_vals_list.append(vals.pop('write_off_line_vals',None))

            #Forcethemove_typetoavoidinconsistencywithresidual'default_move_type'insidethecontext.
            vals['move_type']='entry'

            #Forcethecomputationof'journal_id'sincethisfieldissetonaccount.movebutmusthavethe
            #bank/cashtype.
            if'journal_id'notinvals:
                vals['journal_id']=self._get_default_journal().id

            #Since'currency_id'isacomputededitablefield,itwillbecomputedlater.
            #Preventtheaccount.movetocallthe_get_default_currencymethodthatcouldraise
            #the'Pleasedefineanaccountingmiscellaneousjournalinyourcompany'error.
            if'currency_id'notinvals:
                journal=self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id']=journal.currency_id.idorjournal.company_id.currency_id.id

        payments=super().create(vals_list)

        fori,payinenumerate(payments):
            write_off_line_vals=write_off_line_vals_list[i]

            #Writepayment_idonthejournalentryplusthefieldsbeingstoredinbothmodelsbuthavingthesame
            #name,e.g.partner_bank_id.TheORMiscurrentlynotabletoperformsuchsynchronizationandmakethings
            #moredifficultbycreatingrelatedfieldsontheflytohandlethe_inherits.
            #Then,whenpartner_bank_idisinvals,thekeyisconsumedbyaccount.paymentbutisneverwrittenon
            #account.move.
            to_write={'payment_id':pay.id}
            fork,vinvals_list[i].items():
                ifkinself._fieldsandself._fields[k].storeandkinpay.move_id._fieldsandpay.move_id._fields[k].store:
                    to_write[k]=v

            if'line_ids'notinvals_list[i]:
                to_write['line_ids']=[(0,0,line_vals)forline_valsinpay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

            pay.move_id.write(to_write)

        returnpayments

    defwrite(self,vals):
        #OVERRIDE
        res=super().write(vals)
        self._synchronize_to_moves(set(vals.keys()))
        returnres

    defunlink(self):
        #OVERRIDEtounlinktheinheritedaccount.move(move_idfield)aswell.
        moves=self.with_context(force_delete=True).move_id
        res=super().unlink()
        moves.unlink()
        returnres

    @api.depends('move_id.name')
    defname_get(self):
        return[(payment.id,payment.move_id.nameor_('DraftPayment'))forpaymentinself]

    #-------------------------------------------------------------------------
    #SYNCHRONIZATIONaccount.payment<->account.move
    #-------------------------------------------------------------------------

    def_synchronize_from_moves(self,changed_fields):
        '''Updatetheaccount.paymentregardingitsrelatedaccount.move.
        Also,checkbothmodelsarestillconsistent.
        :paramchanged_fields:Asetcontainingallmodifiedfieldsonaccount.move.
        '''
        ifself._context.get('skip_account_move_synchronization'):
            return

        forpayinself.with_context(skip_account_move_synchronization=True):

            #Afterthemigrationto14.0,thejournalentrycouldbesharedbetweentheaccount.paymentandthe
            #account.bank.statement.line.Inthatcase,thesynchronizationwillonlybemadewiththestatementline.
            ifpay.move_id.statement_line_id:
                continue

            move=pay.move_id
            move_vals_to_write={}
            payment_vals_to_write={}

            if'journal_id'inchanged_fields:
                ifpay.journal_id.typenotin('bank','cash'):
                    raiseUserError(_("Apaymentmustalwaysbelongstoabankorcashjournal."))

            if'line_ids'inchanged_fields:
                all_lines=move.line_ids
                liquidity_lines,counterpart_lines,writeoff_lines=pay._seek_for_lines()

                iflen(liquidity_lines)!=1orlen(counterpart_lines)!=1:
                    raiseUserError(_(
                        "Thejournalentry%sreachedaninvalidstaterelativetoitspayment.\n"
                        "Tobeconsistent,thejournalentrymustalwayscontains:\n"
                        "-onejournaliteminvolvingtheoutstandingpayment/receiptsaccount.\n"
                        "-onejournaliteminvolvingareceivable/payableaccount.\n"
                        "-optionaljournalitems,allsharingthesameaccount.\n\n"
                    )%move.display_name)

                ifwriteoff_linesandlen(writeoff_lines.account_id)!=1:
                    raiseUserError(_(
                        "Thejournalentry%sreachedaninvalidstaterelativetoitspayment.\n"
                        "Tobeconsistent,allthewrite-offjournalitemsmustsharethesameaccount."
                    )%move.display_name)

                ifany(line.currency_id!=all_lines[0].currency_idforlineinall_lines):
                    raiseUserError(_(
                        "Thejournalentry%sreachedaninvalidstaterelativetoitspayment.\n"
                        "Tobeconsistent,thejournalitemsmustsharethesamecurrency."
                    )%move.display_name)

                ifany(line.partner_id!=all_lines[0].partner_idforlineinall_lines):
                    raiseUserError(_(
                        "Thejournalentry%sreachedaninvalidstaterelativetoitspayment.\n"
                        "Tobeconsistent,thejournalitemsmustsharethesamepartner."
                    )%move.display_name)

                ifnotpay.is_internal_transfer:
                    ifcounterpart_lines.account_id.user_type_id.type=='receivable':
                        payment_vals_to_write['partner_type']='customer'
                    else:
                        payment_vals_to_write['partner_type']='supplier'

                liquidity_amount=liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id':liquidity_lines.currency_id.id,
                    'partner_id':liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount':abs(liquidity_amount),
                    'currency_id':liquidity_lines.currency_id.id,
                    'destination_account_id':counterpart_lines.account_id.id,
                    'partner_id':liquidity_lines.partner_id.id,
                })
                ifliquidity_amount>0.0:
                    payment_vals_to_write.update({'payment_type':'inbound'})
                elifliquidity_amount<0.0:
                    payment_vals_to_write.update({'payment_type':'outbound'})

            move.write(move._cleanup_write_orm_values(move,move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay,payment_vals_to_write))

    def_synchronize_to_moves(self,changed_fields):
        '''Updatetheaccount.moveregardingthemodifiedaccount.payment.
        :paramchanged_fields:Alistcontainingallmodifiedfieldsonaccount.payment.
        '''
        ifself._context.get('skip_account_move_synchronization'):
            return

        ifnotany(field_nameinchanged_fieldsforfield_namein(
            'date','amount','payment_type','partner_type','payment_reference','is_internal_transfer',
            'currency_id','partner_id','destination_account_id','partner_bank_id','journal_id',
        )):
            return

        forpayinself.with_context(skip_account_move_synchronization=True):
            liquidity_lines,counterpart_lines,writeoff_lines=pay._seek_for_lines()

            #Makesuretopreservethewrite-offamount.
            #Thisallowstocreateanewpaymentwithcustom'line_ids'.

            ifliquidity_linesandcounterpart_linesandwriteoff_lines:

                counterpart_amount=sum(counterpart_lines.mapped('amount_currency'))
                writeoff_amount=sum(writeoff_lines.mapped('amount_currency'))

                #Tobeconsistentwiththepayment_differencemadeinaccount.payment.register,
                #'writeoff_amount'needstobesignedregardingthe'amount'fieldbeforethewrite.
                #Sincethewriteisalreadydoneatthispoint,weneedtobasethecomputationonaccountingvalues.
                if(counterpart_amount>0.0)==(writeoff_amount>0.0):
                    sign=-1
                else:
                    sign=1
                writeoff_amount=abs(writeoff_amount)*sign

                write_off_line_vals={
                    'name':writeoff_lines[0].name,
                    'amount':writeoff_amount,
                    'account_id':writeoff_lines[0].account_id.id,
                }
            else:
                write_off_line_vals={}

            line_vals_list=pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

            line_ids_commands=[]
            iflen(liquidity_lines)==1:
                line_ids_commands.append((1,liquidity_lines.id,line_vals_list[0]))
            else:
                forlineinliquidity_lines:
                    line_ids_commands.append((2,line.id,0))
                line_ids_commands.append((0,0,line_vals_list[0]))

            iflen(counterpart_lines)==1:
                line_ids_commands.append((1,counterpart_lines.id,line_vals_list[1]))
            else:
                forlineincounterpart_lines:
                    line_ids_commands.append((2,line.id,0))
                line_ids_commands.append((0,0,line_vals_list[1]))

            forlineinwriteoff_lines:
                line_ids_commands.append((2,line.id))

            forextra_line_valsinline_vals_list[2:]:
                line_ids_commands.append((0,0,extra_line_vals))

            #Updatetheexistingjournalitems.
            #Ifdealingwithmultiplewrite-offlines,theyaredroppedandanewoneisgenerated.

            pay.move_id.write({
                'partner_id':pay.partner_id.id,
                'currency_id':pay.currency_id.id,
                'partner_bank_id':pay.partner_bank_id.id,
                'line_ids':line_ids_commands,
            })

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------

    defmark_as_sent(self):
        self.write({'is_move_sent':True})

    defunmark_as_sent(self):
        self.write({'is_move_sent':False})

    defaction_post(self):
        '''draft->posted'''
        self.move_id._post(soft=False)

    defaction_cancel(self):
        '''draft->cancelled'''
        self.move_id.button_cancel()

    defaction_draft(self):
        '''posted->draft'''
        self.move_id.button_draft()

    defbutton_open_invoices(self):
        '''Redirecttheusertotheinvoice(s)paidbythispayment.
        :return:   Anactiononaccount.move.
        '''
        self.ensure_one()

        action={
            'name':_("PaidInvoices"),
            'type':'ir.actions.act_window',
            'res_model':'account.move',
            'context':{'create':False},
        }
        iflen(self.reconciled_invoice_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':self.reconciled_invoice_ids.id,
            })
        else:
            action.update({
                'view_mode':'list,form',
                'domain':[('id','in',self.reconciled_invoice_ids.ids)],
            })
        returnaction

    defbutton_open_bills(self):
        '''Redirecttheusertothebill(s)paidbythispayment.
        :return:   Anactiononaccount.move.
        '''
        self.ensure_one()

        action={
            'name':_("PaidBills"),
            'type':'ir.actions.act_window',
            'res_model':'account.move',
            'context':{'create':False},
        }
        iflen(self.reconciled_bill_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':self.reconciled_bill_ids.id,
            })
        else:
            action.update({
                'view_mode':'list,form',
                'domain':[('id','in',self.reconciled_bill_ids.ids)],
            })
        returnaction

    defbutton_open_statements(self):
        '''Redirecttheusertothestatementline(s)reconciledtothispayment.
        :return:   Anactiononaccount.move.
        '''
        self.ensure_one()

        action={
            'name':_("MatchedStatements"),
            'type':'ir.actions.act_window',
            'res_model':'account.bank.statement',
            'context':{'create':False},
        }
        iflen(self.reconciled_statement_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':self.reconciled_statement_ids.id,
            })
        else:
            action.update({
                'view_mode':'list,form',
                'domain':[('id','in',self.reconciled_statement_ids.ids)],
            })
        returnaction
