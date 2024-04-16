#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromdatetimeimporttimedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.toolsimportfloat_is_zero,float_compare


classPosSession(models.Model):
    _name='pos.session'
    _order='iddesc'
    _description='PointofSaleSession'
    _inherit=['mail.thread','mail.activity.mixin']

    POS_SESSION_STATE=[
        ('opening_control','OpeningControl'), #methodaction_pos_session_open
        ('opened','InProgress'),              #methodaction_pos_session_closing_control
        ('closing_control','ClosingControl'), #methodaction_pos_session_close
        ('closed','Closed&Posted'),
    ]

    company_id=fields.Many2one('res.company',related='config_id.company_id',string="Company",readonly=True)

    config_id=fields.Many2one(
        'pos.config',string='PointofSale',
        help="Thephysicalpointofsaleyouwilluse.",
        required=True,
        index=True)
    name=fields.Char(string='SessionID',required=True,readonly=True,default='/')
    user_id=fields.Many2one(
        'res.users',string='OpenedBy',
        required=True,
        index=True,
        readonly=True,
        states={'opening_control':[('readonly',False)]},
        default=lambdaself:self.env.uid,
        ondelete='restrict')
    currency_id=fields.Many2one('res.currency',related='config_id.currency_id',string="Currency",readonly=False)
    start_at=fields.Datetime(string='OpeningDate',readonly=True)
    stop_at=fields.Datetime(string='ClosingDate',readonly=True,copy=False)

    state=fields.Selection(
        POS_SESSION_STATE,string='Status',
        required=True,readonly=True,
        index=True,copy=False,default='opening_control')

    sequence_number=fields.Integer(string='OrderSequenceNumber',help='Asequencenumberthatisincrementedwitheachorder',default=1)
    login_number=fields.Integer(string='LoginSequenceNumber',help='Asequencenumberthatisincrementedeachtimeauserresumesthepossession',default=0)

    cash_control=fields.Boolean(compute='_compute_cash_all',string='HasCashControl',compute_sudo=True)
    cash_journal_id=fields.Many2one('account.journal',compute='_compute_cash_all',string='CashJournal',store=True)
    cash_register_id=fields.Many2one('account.bank.statement',compute='_compute_cash_all',string='CashRegister',store=True)

    cash_register_balance_end_real=fields.Monetary(
        related='cash_register_id.balance_end_real',
        string="EndingBalance",
        help="Totalofclosingcashcontrollines.",
        readonly=True)
    cash_register_balance_start=fields.Monetary(
        related='cash_register_id.balance_start',
        string="StartingBalance",
        help="Totalofopeningcashcontrollines.",
        readonly=True)
    cash_register_total_entry_encoding=fields.Monetary(
        compute='_compute_cash_balance',
        string='TotalCashTransaction',
        readonly=True,
        help="Totalofallpaidsalesorders")
    cash_register_balance_end=fields.Monetary(
        compute='_compute_cash_balance',
        string="TheoreticalClosingBalance",
        help="Sumofopeningbalanceandtransactions.",
        readonly=True)
    cash_register_difference=fields.Monetary(
        compute='_compute_cash_balance',
        string='BeforeClosingDifference',
        help="Differencebetweenthetheoreticalclosingbalanceandtherealclosingbalance.",
        readonly=True)
    cash_real_difference=fields.Monetary(string='Difference',readonly=True)
    cash_real_transaction=fields.Monetary(string='Transaction',readonly=True)
    cash_real_expected=fields.Monetary(string="Expected",readonly=True)

    order_ids=fields.One2many('pos.order','session_id', string='Orders')
    order_count=fields.Integer(compute='_compute_order_count')
    statement_ids=fields.One2many('account.bank.statement','pos_session_id',string='CashStatements',readonly=True)
    failed_pickings=fields.Boolean(compute='_compute_picking_count')
    picking_count=fields.Integer(compute='_compute_picking_count')
    picking_ids=fields.One2many('stock.picking','pos_session_id')
    rescue=fields.Boolean(string='RecoverySession',
        help="Auto-generatedsessionfororphanorders,ignoredinconstraints",
        readonly=True,
        copy=False)
    move_id=fields.Many2one('account.move',string='JournalEntry',index=True)
    payment_method_ids=fields.Many2many('pos.payment.method',related='config_id.payment_method_ids',string='PaymentMethods')
    total_payments_amount=fields.Float(compute='_compute_total_payments_amount',string='TotalPaymentsAmount')
    is_in_company_currency=fields.Boolean('IsUsingCompanyCurrency',compute='_compute_is_in_company_currency')
    update_stock_at_closing=fields.Boolean('Stockshouldbeupdatedatclosing')

    _sql_constraints=[('uniq_name','unique(name)',"ThenameofthisPOSSessionmustbeunique!")]

    @api.depends('currency_id','company_id.currency_id')
    def_compute_is_in_company_currency(self):
        forsessioninself:
            session.is_in_company_currency=session.currency_id==session.company_id.currency_id

    @api.depends('payment_method_ids','order_ids','cash_register_balance_start','cash_register_id')
    def_compute_cash_balance(self):
        forsessioninself:
            cash_payment_method=session.payment_method_ids.filtered('is_cash_count')[:1]
            ifcash_payment_method:
                total_cash_payment=0.0
                result=self.env['pos.payment'].read_group([('session_id','=',session.id),('payment_method_id','=',cash_payment_method.id)],['amount'],['session_id'])
                ifresult:
                    total_cash_payment=result[0]['amount']
                session.cash_register_total_entry_encoding=session.cash_register_id.total_entry_encoding+(
                    0.0ifsession.state=='closed'elsetotal_cash_payment
                )
                session.cash_register_balance_end=session.cash_register_balance_start+session.cash_register_total_entry_encoding
                session.cash_register_difference=session.cash_register_balance_end_real-session.cash_register_balance_end
            else:
                session.cash_register_total_entry_encoding=0.0
                session.cash_register_balance_end=0.0
                session.cash_register_difference=0.0

    @api.depends('order_ids.payment_ids.amount')
    def_compute_total_payments_amount(self):
        result=self.env['pos.payment'].read_group([('session_id','in',self.ids)],['amount'],['session_id'])
        session_amount_map=dict((data['session_id'][0],data['amount'])fordatainresult)
        forsessioninself:
            session.total_payments_amount=session_amount_map.get(session.id)or0

    def_compute_order_count(self):
        orders_data=self.env['pos.order'].read_group([('session_id','in',self.ids)],['session_id'],['session_id'])
        sessions_data={order_data['session_id'][0]:order_data['session_id_count']fororder_datainorders_data}
        forsessioninself:
            session.order_count=sessions_data.get(session.id,0)

    @api.depends('picking_ids','picking_ids.state')
    def_compute_picking_count(self):
        forsessioninself:
            session.picking_count=self.env['stock.picking'].search_count([('pos_session_id','=',session.id)])
            session.failed_pickings=bool(self.env['stock.picking'].search([('pos_session_id','=',session.id),('state','!=','done')],limit=1))

    defaction_stock_picking(self):
        self.ensure_one()
        action=self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_ready')
        action['display_name']=_('Pickings')
        action['context']={}
        action['domain']=[('id','in',self.picking_ids.ids)]
        returnaction

    @api.depends('config_id','statement_ids','payment_method_ids')
    def_compute_cash_all(self):
        #Onlyonecashregisterissupportedbypoint_of_sale.
        forsessioninself:
            session.cash_journal_id=session.cash_register_id=session.cash_control=False
            cash_payment_methods=session.payment_method_ids.filtered('is_cash_count')
            ifnotcash_payment_methods:
                continue
            forstatementinsession.statement_ids:
                ifstatement.journal_id==cash_payment_methods[0].cash_journal_id:
                    session.cash_control=session.config_id.cash_control
                    session.cash_journal_id=statement.journal_id.id
                    session.cash_register_id=statement.id
                    break #stopiterationafterfindingthecashjournal

    @api.constrains('config_id')
    def_check_pos_config(self):
        ifself.search_count([
                ('state','!=','closed'),
                ('config_id','=',self.config_id.id),
                ('rescue','=',False)
            ])>1:
            raiseValidationError(_("Anothersessionisalreadyopenedforthispointofsale."))

    @api.constrains('start_at')
    def_check_start_date(self):
        forrecordinself:
            company=record.config_id.journal_id.company_id
            start_date=record.start_at.date()
            if(company.period_lock_dateandstart_date<=company.period_lock_date)or(company.fiscalyear_lock_dateandstart_date<=company.fiscalyear_lock_date):
                raiseValidationError(_("Youcannotcreateasessionbeforetheaccountinglockdate."))

    def_check_bank_statement_state(self):
        forsessioninself:
            closed_statement_ids=session.statement_ids.filtered(lambdax:x.state!="open")
            ifclosed_statement_ids:
                raiseUserError(_("SomeCashRegistersarealreadyposted.Pleaseresetthemtonewinordertoclosethesession.\n"
                                  "CashRegisters:%r",list(statement.nameforstatementinclosed_statement_ids)))

    def_check_invoices_are_posted(self):
        unposted_invoices=self.order_ids.account_move.filtered(lambdax:x.state!='posted')
        ifunposted_invoices:
            raiseUserError(_('YoucannotclosethePOSwheninvoicesarenotposted.\n'
                              'Invoices:%s')%str.join('\n',
                                                         ['%s-%s'%(invoice.name,invoice.state)forinvoicein
                                                          unposted_invoices]))

    @api.model
    defcreate(self,values):
        config_id=values.get('config_id')orself.env.context.get('default_config_id')
        ifnotconfig_id:
            raiseUserError(_("YoushouldassignaPointofSaletoyoursession."))

        #journal_idisnotrequiredonthepos_configbecauseitdoesnot
        #existsattheinstallation.Ifnothingisconfiguredatthe
        #installationwedotheminimalconfiguration.Impossibletodoin
        #the.xmlfilesastheCoAisnotyetinstalled.
        pos_config=self.env['pos.config'].browse(config_id)
        ctx=dict(self.env.context,company_id=pos_config.company_id.id)

        pos_name=self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session')
        ifvalues.get('name'):
            pos_name+=''+values['name']

        cash_payment_methods=pos_config.payment_method_ids.filtered(lambdapm:pm.is_cash_count)
        statement_ids=self.env['account.bank.statement']
        ifself.user_has_groups('point_of_sale.group_pos_user'):
            statement_ids=statement_ids.sudo()
        forcash_journalincash_payment_methods.mapped('cash_journal_id'):
            ctx['journal_id']=cash_journal.idifpos_config.cash_controlandcash_journal.type=='cash'elseFalse
            st_values={
                'journal_id':cash_journal.id,
                'user_id':self.env.user.id,
                'name':pos_name,
            }
            statement_ids|=statement_ids.with_context(ctx).create(st_values)

        update_stock_at_closing=pos_config.company_id.point_of_sale_update_stock_quantities=="closing"

        values.update({
            'name':pos_name,
            'statement_ids':[(6,0,statement_ids.ids)],
            'config_id':config_id,
            'update_stock_at_closing':update_stock_at_closing,
        })

        ifself.user_has_groups('point_of_sale.group_pos_user'):
            res=super(PosSession,self.with_context(ctx).sudo()).create(values)
        else:
            res=super(PosSession,self.with_context(ctx)).create(values)
        res.action_pos_session_open()

        returnres

    defunlink(self):
        forsessioninself.filtered(lambdas:s.statement_ids):
            session.statement_ids.unlink()
        returnsuper(PosSession,self).unlink()

    deflogin(self):
        self.ensure_one()
        login_number=self.login_number+1
        self.write({
            'login_number':login_number,
        })
        returnlogin_number

    defaction_pos_session_open(self):
        #secondbrowsebecauseweneedtorefetchthedatafromtheDBforcash_register_id
        #weonlyopensessionsthathaven'talreadybeenopened
        forsessioninself.filtered(lambdasession:session.statein('new_session','opening_control')):
            values={}
            ifnotsession.start_at:
                values['start_at']=fields.Datetime.now()
            ifsession.config_id.cash_controlandnotsession.rescue:
                last_session=self.search([('config_id','=',session.config_id.id),('id','!=',session.id)],limit=1)
                session.cash_register_id.balance_start=last_session.cash_register_id.balance_end_realiflast_sessionelse0
                values['state']='opening_control'
            else:
                values['state']='opened'
            session.write(values)
        returnTrue

    defaction_pos_session_closing_control(self):
        self._check_pos_session_balance()
        forsessioninself:
            ifany(order.state=='draft'fororderinsession.order_ids):
                raiseUserError(_("YoucannotclosethePOSwhenordersarestillindraft"))
            ifsession.state=='closed':
                raiseUserError(_('Thissessionisalreadyclosed.'))
            session.write({'state':'closing_control','stop_at':fields.Datetime.now()})
            ifnotsession.config_id.cash_control:
                session.action_pos_session_close()
        returnTrue

    def_check_pos_session_balance(self):
        forsessioninself:
            forstatementinsession.statement_ids:
                if(statement!=session.cash_register_id)and(statement.balance_end!=statement.balance_end_real):
                    statement.write({'balance_end_real':statement.balance_end})

    defaction_pos_session_validate(self):
        self._check_pos_session_balance()
        returnself.action_pos_session_close()

    defaction_pos_session_close(self):
        #Sessionwithoutcashpaymentmethodwillnothaveacashregister.
        #However,therecouldbeotherpaymentmethods,thus,sessionstill
        #needstobevalidated.
        self._check_bank_statement_state()
        ifnotself.cash_register_id:
            returnself._validate_session()

        ifself.cash_controlandabs(self.cash_register_difference)>self.config_id.amount_authorized_diff:
            #Onlyposmanagercanclosestatementswithcash_register_differencegreaterthanamount_authorized_diff.
            ifnotself.user_has_groups("point_of_sale.group_pos_manager"):
                raiseUserError(_(
                    "Yourendingbalanceistoodifferentfromthetheoreticalcashclosing(%.2f),"
                    "themaximumallowedis:%.2f.Youcancontactyourmanagertoforceit."
                )%(self.cash_register_difference,self.config_id.amount_authorized_diff))
            else:
                returnself._warning_balance_closing()
        else:
            returnself._validate_session()

    def_validate_session(self):
        self.ensure_one()
        sudo=self.user_has_groups('point_of_sale.group_pos_user')
        ifself.order_idsorself.statement_ids.line_ids:
            self.cash_real_transaction=self.cash_register_total_entry_encoding
            self.cash_real_expected=self.cash_register_balance_end
            self.cash_real_difference=self.cash_register_difference
            ifself.state=='closed':
                raiseUserError(_('Thissessionisalreadyclosed.'))
            self._check_if_no_draft_orders()
            self._check_invoices_are_posted()
            ifself.update_stock_at_closing:
                self._create_picking_at_end_of_session()
            #Userswithoutanyaccountingrightswon'tbeabletocreatethejournalentry.Ifthis
            #case,switchtosudoforcreationandposting.
            try:
                withself.env.cr.savepoint():
                    self.with_company(self.company_id)._create_account_move()
            exceptAccessErrorase:
                ifsudo:
                    self.sudo().with_company(self.company_id)._create_account_move()
                else:
                    raisee
            ifself.move_id.line_ids:
                #Settheuninvoicedorders'stateto'done'
                self.env['pos.order'].search([('session_id','=',self.id),('state','=','paid')]).write({'state':'done'})
            else:
                self.move_id.sudo().unlink()
        else:
            statement=self.cash_register_id
            ifnotself.config_id.cash_control:
                statement.write({'balance_end_real':statement.balance_end})
            statement.button_post()
            statement.button_validate()
        self.write({'state':'closed'})
        return{
            'type':'ir.actions.client',
            'name':'PointofSaleMenu',
            'tag':'reload',
            'params':{'menu_id':self.env.ref('point_of_sale.menu_point_root').id},
        }

    def_create_picking_at_end_of_session(self):
        self.ensure_one()
        lines_grouped_by_dest_location={}
        picking_type=self.config_id.picking_type_id

        ifnotpicking_typeornotpicking_type.default_location_dest_id:
            session_destination_id=self.env['stock.warehouse']._get_partner_locations()[0].id
        else:
            session_destination_id=picking_type.default_location_dest_id.id

        fororderinself.order_ids:
            iforder.company_id.anglo_saxon_accountingandorder.is_invoiced:
                continue
            destination_id=order.partner_id.property_stock_customer.idorsession_destination_id
            ifdestination_idinlines_grouped_by_dest_location:
                lines_grouped_by_dest_location[destination_id]|=order.lines
            else:
                lines_grouped_by_dest_location[destination_id]=order.lines

        forlocation_dest_id,linesinlines_grouped_by_dest_location.items():
            pickings=self.env['stock.picking']._create_picking_from_pos_order_lines(location_dest_id,lines,picking_type)
            pickings.write({'pos_session_id':self.id,'origin':self.name})

    def_create_balancing_line(self,data):
        imbalance_amount=0
        forlineinself.move_id.line_ids:
            #itisanexcessdebitsoitshouldbecredited
            imbalance_amount+=line.debit-line.credit

        if(notfloat_is_zero(imbalance_amount,precision_rounding=self.currency_id.rounding)):
            balancing_vals=self._prepare_balancing_line_vals(imbalance_amount,self.move_id)
            MoveLine=data.get('MoveLine')
            MoveLine.create(balancing_vals)

        returndata

    def_prepare_balancing_line_vals(self,imbalance_amount,move):
        account=self._get_balancing_account()
        partial_vals={
            'name':_('DifferenceatclosingPoSsession'),
            'account_id':account.id,
            'move_id':move.id,
            'partner_id':False,
        }
        #`imbalance_amount`isalreadyintermsofcompanycurrencysoitistheamount_converted
        #paramwhencalling`_credit_amounts`.amountparamwillbetheconvertedvalueof
        #`imbalance_amount`fromcompanycurrencytothesessioncurrency.
        imbalance_amount_session=0
        if(notself.is_in_company_currency):
            imbalance_amount_session=self.company_id.currency_id._convert(imbalance_amount,self.currency_id,self.company_id,fields.Date.context_today(self))
        returnself._credit_amounts(partial_vals,imbalance_amount_session,imbalance_amount)

    def_get_balancing_account(self):
        propoerty_account=self.env['ir.property']._get('property_account_receivable_id','res.partner')
        returnself.company_id.account_default_pos_receivable_account_idorpropoerty_accountorself.env['account.account']

    def_create_account_move(self):
        """Createaccount.moveandaccount.move.linerecordsforthissession.

        Side-effectsinclude:
            -settingself.move_idtothecreatedaccount.moverecord
            -creatingandvalidatingaccount.bank.statementforcashpayments
            -reconcilingcashreceivablelines,invoicereceivablelinesandstockoutputlines
        """
        journal=self.config_id.journal_id
        #Passingdefault_journal_idforthecalculationofdefaultcurrencyofaccountmove
        #See_get_default_currencyintheaccount/account_move.py.
        account_move=self.env['account.move'].with_context(default_journal_id=journal.id).create({
            'journal_id':journal.id,
            'date':fields.Date.context_today(self),
            'ref':self.name,
        })
        self.write({'move_id':account_move.id})

        data={}
        data=self._accumulate_amounts(data)
        data=self._create_non_reconciliable_move_lines(data)
        data=self._create_cash_statement_lines_and_cash_move_lines(data)
        data=self._create_invoice_receivable_lines(data)
        data=self._create_stock_output_lines(data)
        data=self._create_balancing_line(data)

        ifaccount_move.line_ids:
            account_move._post()

        data=self._reconcile_account_move_lines(data)

    def_accumulate_amounts(self,data):
        #Accumulatetheamountsforeachaccountinglinesgroup
        #Eachdictmaps`key`->`amounts`,where`key`isthegroupkey.
        #E.g.`combine_receivables`isderivedfrompos.paymentrecords
        #intheself.order_idswithgroupkeyofthe`payment_method_id`
        #fieldofthepos.paymentrecord.
        amounts=lambda:{'amount':0.0,'amount_converted':0.0}
        tax_amounts=lambda:{'amount':0.0,'amount_converted':0.0,'base_amount':0.0,'base_amount_converted':0.0}
        split_receivables=defaultdict(amounts)
        split_receivables_cash=defaultdict(amounts)
        combine_receivables=defaultdict(amounts)
        combine_receivables_cash=defaultdict(amounts)
        invoice_receivables=defaultdict(amounts)
        sales=defaultdict(amounts)
        taxes=defaultdict(tax_amounts)
        stock_expense=defaultdict(amounts)
        stock_return=defaultdict(amounts)
        stock_output=defaultdict(amounts)
        rounding_difference={'amount':0.0,'amount_converted':0.0}
        #Trackthereceivablelinesoftheinvoicedorders'accountmovesforreconciliation
        #Thesereceivablelinesarereconciledtothecorrespondinginvoicereceivablelines
        #ofthissession'smove_id.
        order_account_move_receivable_lines=defaultdict(lambda:self.env['account.move.line'])
        rounded_globally=self.company_id.tax_calculation_rounding_method=='round_globally'
        fororderinself.order_ids:
            #Combineposreceivablelines
            #Separatecashpaymentsforcashreconciliationlater.
            forpaymentinorder.payment_ids:
                amount,date=payment.amount,payment.payment_date
                ifpayment.payment_method_id.split_transactions:
                    ifpayment.payment_method_id.is_cash_count:
                        split_receivables_cash[payment]=self._update_amounts(split_receivables_cash[payment],{'amount':amount},date)
                    else:
                        split_receivables[payment]=self._update_amounts(split_receivables[payment],{'amount':amount},date)
                else:
                    key=payment.payment_method_id
                    ifpayment.payment_method_id.is_cash_count:
                        combine_receivables_cash[key]=self._update_amounts(combine_receivables_cash[key],{'amount':amount},date)
                    else:
                        combine_receivables[key]=self._update_amounts(combine_receivables[key],{'amount':amount},date)

            iforder.is_invoiced:
                #Combineinvoicereceivablelines
                key=order.partner_id
                ifself.config_id.cash_rounding:
                    invoice_receivables[key]=self._update_amounts(invoice_receivables[key],{'amount':order.amount_paid},order.date_order)
                else:
                    invoice_receivables[key]=self._update_amounts(invoice_receivables[key],{'amount':order.amount_total},order.date_order)
                #sidelooptogatherreceivablelinesbyaccountforreconciliation
                formove_lineinorder.account_move.line_ids.filtered(lambdaaml:aml.account_id.internal_type=='receivable'andnotaml.reconciled):
                    key=(order.partner_id.commercial_partner_id.id,move_line.account_id.id)
                    order_account_move_receivable_lines[key]|=move_line
            else:
                order_taxes=defaultdict(tax_amounts)
                fororder_lineinorder.lines:
                    line=self._prepare_line(order_line)
                    #Combinesales/refundlines
                    sale_key=(
                        #account
                        line['income_account_id'],
                        #sign
                        -1ifline['amount']<0else1,
                        #fortaxes
                        tuple((tax['id'],tax['account_id'],tax['tax_repartition_line_id'])fortaxinline['taxes']),
                        line['base_tags'],
                    )
                    sales[sale_key]=self._update_amounts(sales[sale_key],{'amount':line['amount']},line['date_order'])
                    #Combinetaxlines
                    fortaxinline['taxes']:
                        tax_key=(tax['account_id']orline['income_account_id'],tax['tax_repartition_line_id'],tax['id'],tuple(tax['tag_ids']))
                        order_taxes[tax_key]=self._update_amounts(
                            order_taxes[tax_key],
                            {'amount':tax['amount'],'base_amount':tax['base']},
                            tax['date_order'],
                            round=notrounded_globally
                        )
                fortax_key,amountsinorder_taxes.items():
                    ifrounded_globally:
                        amounts=self._round_amounts(amounts)
                    foramount_key,amountinamounts.items():
                        taxes[tax_key][amount_key]+=amount

                ifself.company_id.anglo_saxon_accountingandorder.picking_ids.ids:
                    #Combinestocklines
                    stock_moves=self.env['stock.move'].sudo().search([
                        ('picking_id','in',order.picking_ids.ids),
                        ('company_id.anglo_saxon_accounting','=',True),
                        ('product_id.categ_id.property_valuation','=','real_time')
                    ])
                    formoveinstock_moves:
                        exp_key=move.product_id._get_product_accounts()['expense']
                        out_key=move.product_id.categ_id.property_stock_account_output_categ_id
                        signed_product_qty=move.product_qty
                        ifmove._is_in():
                            signed_product_qty*=-1
                        amount=signed_product_qty*move.product_id._compute_average_price(0,move.product_qty,move)
                        stock_expense[exp_key]=self._update_amounts(stock_expense[exp_key],{'amount':amount},move.picking_id.date,force_company_currency=True)
                        ifmove._is_in():
                            stock_return[out_key]=self._update_amounts(stock_return[out_key],{'amount':amount},move.picking_id.date,force_company_currency=True)
                        else:
                            stock_output[out_key]=self._update_amounts(stock_output[out_key],{'amount':amount},move.picking_id.date,force_company_currency=True)

                ifself.config_id.cash_rounding:
                    diff=order.amount_paid-order.amount_total
                    rounding_difference=self._update_amounts(rounding_difference,{'amount':diff},order.date_order)

                #Increasingcurrentpartner'scustomer_rank
                partners=(order.partner_id|order.partner_id.commercial_partner_id)
                partners._increase_rank('customer_rank')

        ifself.company_id.anglo_saxon_accounting:
            global_session_pickings=self.picking_ids.filtered(lambdap:notp.pos_order_id)
            ifglobal_session_pickings:
                stock_moves=self.env['stock.move'].sudo().search([
                    ('picking_id','in',global_session_pickings.ids),
                    ('company_id.anglo_saxon_accounting','=',True),
                    ('product_id.categ_id.property_valuation','=','real_time'),
                ])
                formoveinstock_moves:
                    exp_key=move.product_id._get_product_accounts()['expense']
                    out_key=move.product_id.categ_id.property_stock_account_output_categ_id
                    signed_product_qty=move.product_qty
                    ifmove._is_in():
                        signed_product_qty*=-1
                    amount=signed_product_qty*move.product_id._compute_average_price(0,move.product_qty,move)
                    stock_expense[exp_key]=self._update_amounts(stock_expense[exp_key],{'amount':amount},move.picking_id.date,force_company_currency=True)
                    ifmove._is_in():
                        stock_return[out_key]=self._update_amounts(stock_return[out_key],{'amount':amount},move.picking_id.date,force_company_currency=True)
                    else:
                        stock_output[out_key]=self._update_amounts(stock_output[out_key],{'amount':amount},move.picking_id.date,force_company_currency=True)
        MoveLine=self.env['account.move.line'].with_context(check_move_validity=False)

        data.update({
            'taxes':                              taxes,
            'sales':                              sales,
            'stock_expense':                      stock_expense,
            'split_receivables':                  split_receivables,
            'combine_receivables':                combine_receivables,
            'split_receivables_cash':             split_receivables_cash,
            'combine_receivables_cash':           combine_receivables_cash,
            'invoice_receivables':                invoice_receivables,
            'stock_return':                       stock_return,
            'stock_output':                       stock_output,
            'order_account_move_receivable_lines':order_account_move_receivable_lines,
            'rounding_difference':                rounding_difference,
            'MoveLine':                           MoveLine
        })
        returndata

    def_create_non_reconciliable_move_lines(self,data):
        #Createaccount.move.linerecordsfor
        #  -sales
        #  -taxes
        #  -stockexpense
        #  -non-cashsplitreceivables(notforautomaticreconciliation)
        #  -non-cashcombinereceivables(notforautomaticreconciliation)
        taxes=data.get('taxes')
        sales=data.get('sales')
        stock_expense=data.get('stock_expense')
        split_receivables=data.get('split_receivables')
        combine_receivables=data.get('combine_receivables')
        rounding_difference=data.get('rounding_difference')
        MoveLine=data.get('MoveLine')

        tax_vals=[self._get_tax_vals(key,amounts['amount'],amounts['amount_converted'],amounts['base_amount_converted'])forkey,amountsintaxes.items()ifamounts['amount']]
        #Checkifalltaxeslineshaveaccount_idassigned.Ifnot,therearerepartitionlinesofthetaxthathavenoaccount_id.
        tax_names_no_account=[line['name']forlineintax_valsifline['account_id']==False]
        iflen(tax_names_no_account)>0:
            error_message=_(
                'Unabletocloseandvalidatethesession.\n'
                'Pleasesetcorrespondingtaxaccountineachrepartitionlineofthefollowingtaxes:\n%s'
            )%','.join(tax_names_no_account)
            raiseUserError(error_message)
        rounding_vals=[]

        ifnotfloat_is_zero(rounding_difference['amount'],precision_rounding=self.currency_id.rounding)ornotfloat_is_zero(rounding_difference['amount_converted'],precision_rounding=self.currency_id.rounding):
            rounding_vals=[self._get_rounding_difference_vals(rounding_difference['amount'],rounding_difference['amount_converted'])]

        MoveLine.create(
            tax_vals
            +[self._get_sale_vals(key,amounts['amount'],amounts['amount_converted'])forkey,amountsinsales.items()]
            +[self._get_stock_expense_vals(key,amounts['amount'],amounts['amount_converted'])forkey,amountsinstock_expense.items()]
            +[self._get_split_receivable_vals(key,amounts['amount'],amounts['amount_converted'])forkey,amountsinsplit_receivables.items()]
            +[self._get_combine_receivable_vals(key,amounts['amount'],amounts['amount_converted'])forkey,amountsincombine_receivables.items()]
            +rounding_vals
        )
        returndata

    def_create_cash_statement_lines_and_cash_move_lines(self,data):
        #Createthesplitandcombinecashstatementlinesandaccountmovelines.
        #Keepthereferencebystatementforreconciliation.
        #`split_cash_statement_lines`maps`statement`->splitcashstatementlines
        #`combine_cash_statement_lines`maps`statement`->combinecashstatementlines
        #`split_cash_receivable_lines`maps`statement`->splitcashreceivablelines
        #`combine_cash_receivable_lines`maps`statement`->combinecashreceivablelines
        MoveLine=data.get('MoveLine')
        split_receivables_cash=data.get('split_receivables_cash')
        combine_receivables_cash=data.get('combine_receivables_cash')

        statements_by_journal_id={statement.journal_id.id:statementforstatementinself.statement_ids}
        #handlesplitcashpayments
        split_cash_statement_line_vals=defaultdict(list)
        split_cash_receivable_vals=defaultdict(list)
        forpayment,amountsinsplit_receivables_cash.items():
            statement=statements_by_journal_id[payment.payment_method_id.cash_journal_id.id]
            split_cash_statement_line_vals[statement].append(self._get_statement_line_vals(statement,payment.payment_method_id.receivable_account_id,amounts['amount'],date=payment.payment_date,partner=payment.pos_order_id.partner_id))
            split_cash_receivable_vals[statement].append(self._get_split_receivable_vals(payment,amounts['amount'],amounts['amount_converted']))
        #handlecombinecashpayments
        combine_cash_statement_line_vals=defaultdict(list)
        combine_cash_receivable_vals=defaultdict(list)
        forpayment_method,amountsincombine_receivables_cash.items():
            ifnotfloat_is_zero(amounts['amount'],precision_rounding=self.currency_id.rounding):
                statement=statements_by_journal_id[payment_method.cash_journal_id.id]
                combine_cash_statement_line_vals[statement].append(self._get_statement_line_vals(statement,payment_method.receivable_account_id,amounts['amount']))
                combine_cash_receivable_vals[statement].append(self._get_combine_receivable_vals(payment_method,amounts['amount'],amounts['amount_converted']))
        #createthestatementlinesandaccountmovelines
        BankStatementLine=self.env['account.bank.statement.line']
        split_cash_statement_lines={}
        combine_cash_statement_lines={}
        split_cash_receivable_lines={}
        combine_cash_receivable_lines={}
        forstatementinself.statement_ids:
            split_cash_statement_lines[statement]=BankStatementLine.create(split_cash_statement_line_vals[statement])
            combine_cash_statement_lines[statement]=BankStatementLine.create(combine_cash_statement_line_vals[statement])
            split_cash_receivable_lines[statement]=MoveLine.create(split_cash_receivable_vals[statement])
            combine_cash_receivable_lines[statement]=MoveLine.create(combine_cash_receivable_vals[statement])

        data.update(
            {'split_cash_statement_lines':   split_cash_statement_lines,
             'combine_cash_statement_lines': combine_cash_statement_lines,
             'split_cash_receivable_lines':  split_cash_receivable_lines,
             'combine_cash_receivable_lines':combine_cash_receivable_lines
             })
        returndata

    def_create_invoice_receivable_lines(self,data):
        #Createinvoicereceivablelinesforthissession'smove_id.
        #Keepreferenceoftheinvoicereceivablelinesbecause
        #theyarereconciledwiththelinesinorder_account_move_receivable_lines
        MoveLine=data.get('MoveLine')
        invoice_receivables=data.get('invoice_receivables')

        invoice_receivable_vals=defaultdict(list)
        invoice_receivable_lines={}
        forpartner,amountsininvoice_receivables.items():
            commercial_partner=partner.commercial_partner_id
            account_id=commercial_partner.property_account_receivable_id.id
            invoice_receivable_vals[commercial_partner].append(self._get_invoice_receivable_vals(account_id,amounts['amount'],amounts['amount_converted'],partner=commercial_partner))
        forcommercial_partner,valsininvoice_receivable_vals.items():
            account_id=commercial_partner.property_account_receivable_id.id
            receivable_lines=MoveLine.create(vals)
            forreceivable_lineinreceivable_lines:
                if(notreceivable_line.reconciled):
                    key=(commercial_partner.id,account_id)
                    ifkeynotininvoice_receivable_lines:
                        invoice_receivable_lines[key]=receivable_line
                    else:
                        invoice_receivable_lines[key]|=receivable_line

        data.update({'invoice_receivable_lines':invoice_receivable_lines})
        returndata

    def_create_stock_output_lines(self,data):
        #Keepreferencetothestockoutputlinesbecause
        #theyarereconciledwithoutputlinesinthestock.move'saccount.move.line
        MoveLine=data.get('MoveLine')
        stock_output=data.get('stock_output')
        stock_return=data.get('stock_return')

        stock_output_vals=defaultdict(list)
        stock_output_lines={}
        forstock_movesin[stock_output,stock_return]:
            foraccount,amountsinstock_moves.items():
                stock_output_vals[account].append(self._get_stock_output_vals(account,amounts['amount'],amounts['amount_converted']))

        foroutput_account,valsinstock_output_vals.items():
            stock_output_lines[output_account]=MoveLine.create(vals)

        data.update({'stock_output_lines':stock_output_lines})
        returndata

    def_reconcile_account_move_lines(self,data):
        #reconcilecashreceivablelines
        split_cash_statement_lines=data.get('split_cash_statement_lines')
        combine_cash_statement_lines=data.get('combine_cash_statement_lines')
        split_cash_receivable_lines=data.get('split_cash_receivable_lines')
        combine_cash_receivable_lines=data.get('combine_cash_receivable_lines')
        order_account_move_receivable_lines=data.get('order_account_move_receivable_lines')
        invoice_receivable_lines=data.get('invoice_receivable_lines')
        stock_output_lines=data.get('stock_output_lines')

        forstatementinself.statement_ids:
            ifnotself.config_id.cash_control:
                statement.write({'balance_end_real':statement.balance_end})
            statement.button_post()
            all_lines=(
                  split_cash_statement_lines[statement].mapped('move_id.line_ids').filtered(lambdaaml:aml.account_id.internal_type=='receivable')
                |combine_cash_statement_lines[statement].mapped('move_id.line_ids').filtered(lambdaaml:aml.account_id.internal_type=='receivable')
                |split_cash_receivable_lines[statement]
                |combine_cash_receivable_lines[statement]
            )
            accounts=all_lines.mapped('account_id')
            lines_by_account=[all_lines.filtered(lambdal:l.account_id==accountandnotl.reconciled)foraccountinaccounts]
            forlinesinlines_by_account:
                lines.reconcile()
            #Wetrytovalidatethestatementafterthereconciliationisdone
            #becausevalidatingthestatementrequireseachstatementlinetobe
            #reconciled.
            #Furthermore,ifthevalidationfailed,whichiscausedbyunreconciled
            #cashdifferencestatementline,wejustignorethat.Leavingthestatement
            #notyetvalidated.Manualreconciliationandvalidationshouldbemade
            #bytheuserintheaccountingapp.
            try:
                statement.button_validate()
            exceptUserError:
                pass

        #reconcileinvoicereceivablelines
        forkeyinorder_account_move_receivable_lines:
            (order_account_move_receivable_lines[key]
            |invoice_receivable_lines.get(key,self.env['account.move.line'])
            ).reconcile()

        #reconcilestockoutputlines
        pickings=self.picking_ids.filtered(lambdap:notp.pos_order_id)
        pickings|=self.order_ids.filtered(lambdao:noto.is_invoiced).mapped('picking_ids')
        stock_moves=self.env['stock.move'].search([('picking_id','in',pickings.ids)])
        stock_account_move_lines=self.env['account.move'].search([('stock_move_id','in',stock_moves.ids)]).mapped('line_ids')
        foraccount_idinstock_output_lines:
            (stock_output_lines[account_id]
            |stock_account_move_lines.filtered(lambdaaml:aml.account_id==account_id)
            ).filtered(lambdaaml:notaml.reconciled).reconcile()
        returndata

    def_prepare_line(self,order_line):
        """Derivefromorder_linetheorderdate,incomeaccount,amountandtaxesinformation.

        Theseinformationwillbeusedinaccumulatingtheamountsforsalesandtaxlines.
        """
        defget_income_account(order_line):
            product=order_line.product_id
            income_account=product.with_company(order_line.company_id)._get_product_accounts()['income']orself.config_id.journal_id.default_account_id
            ifnotincome_account:
                raiseUserError(_('Pleasedefineincomeaccountforthisproduct:"%s"(id:%d).')
                                %(product.name,product.id))
            returnorder_line.order_id.fiscal_position_id.map_account(income_account)

        tax_ids=order_line.tax_ids_after_fiscal_position\
                    .filtered(lambdat:t.company_id.id==order_line.order_id.company_id.id)
        sign=-1iforder_line.qty>=0else1
        price=sign*order_line.price_unit*(1-(order_line.discountor0.0)/100.0)
        #The'is_refund'parameterisusedtocomputethetaxtags.Ultimately,thetagsarepart
        #ofthekeyusedforsummingtaxes.SincethePOSUIdoesn'tsupportthetags,inconsistencies
        #mayarisein'RoundGlobally'.
        check_refund=lambdax:x.qty*x.price_unit<0
        is_refund=check_refund(order_line)
        tax_data=tax_ids.with_context(force_sign=sign).compute_all(price_unit=price,quantity=abs(order_line.qty),currency=self.currency_id,is_refund=is_refund)
        taxes=tax_data['taxes']
        #ForCashbasedtaxes,usetheaccountfromtherepartitionlineimmediatelyasithasbeenpaidalready
        fortaxintaxes:
            tax_rep=self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
            tax['account_id']=tax_rep.account_id.id
        date_order=order_line.order_id.date_order
        taxes=[{'date_order':date_order,**tax}fortaxintaxes]
        return{
            'date_order':order_line.order_id.date_order,
            'income_account_id':get_income_account(order_line).id,
            'amount':order_line.price_subtotal,
            'taxes':taxes,
            'base_tags':tuple(tax_data['base_tags']),
        }

    def_get_rounding_difference_vals(self,amount,amount_converted):
        ifself.config_id.cash_rounding:
            partial_args={
                'name':'Roundingline',
                'move_id':self.move_id.id,
            }
            iffloat_compare(0.0,amount,precision_rounding=self.currency_id.rounding)>0:   #loss
                partial_args['account_id']=self.config_id.rounding_method.loss_account_id.id
                returnself._debit_amounts(partial_args,-amount,-amount_converted)

            iffloat_compare(0.0,amount,precision_rounding=self.currency_id.rounding)<0:  #profit
                partial_args['account_id']=self.config_id.rounding_method.profit_account_id.id
                returnself._credit_amounts(partial_args,amount,amount_converted)

    def_get_split_receivable_vals(self,payment,amount,amount_converted):
        partial_vals={
            'account_id':payment.payment_method_id.receivable_account_id.id,
            'move_id':self.move_id.id,
            'partner_id':self.env["res.partner"]._find_accounting_partner(payment.partner_id).id,
            'name':'%s-%s'%(self.name,payment.payment_method_id.name),
        }
        returnself._debit_amounts(partial_vals,amount,amount_converted)

    def_get_combine_receivable_vals(self,payment_method,amount,amount_converted):
        partial_vals={
            'account_id':payment_method.receivable_account_id.id,
            'move_id':self.move_id.id,
            'name':'%s-%s'%(self.name,payment_method.name)
        }
        returnself._debit_amounts(partial_vals,amount,amount_converted)

    def_get_invoice_receivable_vals(self,account_id,amount,amount_converted,**kwargs):
        partner=kwargs.get('partner',False)
        partial_vals={
            'account_id':account_id,
            'move_id':self.move_id.id,
            'name':'Frominvoicedorders',
            'partner_id':partnerandpartner.idorFalse,
        }
        returnself._credit_amounts(partial_vals,amount,amount_converted)

    def_get_sale_vals(self,key,amount,amount_converted):
        account_id,sign,tax_keys,base_tag_ids=key
        tax_ids=set(tax[0]fortaxintax_keys)
        applied_taxes=self.env['account.tax'].browse(tax_ids)
        title='Sales'ifsign==1else'Refund'
        name='%suntaxed'%title
        ifapplied_taxes:
            name='%swith%s'%(title,','.join([tax.namefortaxinapplied_taxes]))
        partial_vals={
            'name':name,
            'account_id':account_id,
            'move_id':self.move_id.id,
            'tax_ids':[(6,0,tax_ids)],
            'tax_tag_ids':[(6,0,base_tag_ids)],
        }
        returnself._credit_amounts(partial_vals,amount,amount_converted)

    def_get_tax_vals(self,key,amount,amount_converted,base_amount_converted):
        account_id,repartition_line_id,tax_id,tag_ids=key
        tax=self.env['account.tax'].browse(tax_id)
        partial_args={
            'name':tax.name,
            'account_id':account_id,
            'move_id':self.move_id.id,
            'tax_base_amount':abs(base_amount_converted),
            'tax_repartition_line_id':repartition_line_id,
            'tax_tag_ids':[(6,0,tag_ids)],
        }
        returnself._debit_amounts(partial_args,amount,amount_converted)

    def_get_stock_expense_vals(self,exp_account,amount,amount_converted):
        partial_args={'account_id':exp_account.id,'move_id':self.move_id.id}
        returnself._debit_amounts(partial_args,amount,amount_converted,force_company_currency=True)

    def_get_stock_output_vals(self,out_account,amount,amount_converted):
        partial_args={'account_id':out_account.id,'move_id':self.move_id.id}
        returnself._credit_amounts(partial_args,amount,amount_converted,force_company_currency=True)

    def_get_statement_line_vals(self,statement,receivable_account,amount,date=False,partner=False):
        return{
            'date':fields.Date.context_today(self,timestamp=date),
            'amount':amount,
            'payment_ref':self.name,
            'statement_id':statement.id,
            'journal_id':statement.journal_id.id,
            'counterpart_account_id':receivable_account.id,
            'partner_id':partnerandself.env["res.partner"]._find_accounting_partner(partner).id
        }

    def_update_amounts(self,old_amounts,amounts_to_add,date,round=True,force_company_currency=False):
        """Responsibleforadding`amounts_to_add`to`old_amounts`consideringthecurrencyofthesession.

            old_amounts{                                                      new_amounts{
                amount                        amounts_to_add{                    amount
                amount_converted       +         amount              ->         amount_converted
               [base_amount                      [base_amount]                   [base_amount
                base_amount_converted]       }                                    base_amount_converted]
            }                                                                  }

        NOTE:
            -Noticethat`amounts_to_add`doesnothave`amount_converted`field.
                Thisfunctionisresponsibleincalculatingthe`amount_converted`fromthe
                `amount`of`amounts_to_add`whichisusedtoupdatethevaluesof`old_amounts`.
            -Valuesof`amount`and/or`base_amount`shouldalwaysbeinsession'scurrency[1].
            -Valueof`amount_converted`shouldbeincompany'scurrency

        [1]Exceptwhen`force_company_currency`=True.Itmeansthatvaluesin`amounts_to_add`
            isincompanycurrency.

        :paramsold_amountsdict:
            Amountstoupdate
        :paramsamounts_to_adddict:
            Amountsusedtoupdatetheold_amounts
        :paramsdatedate:
            Dateusedforconversion
        :paramsroundbool:
            Sameasroundparameterof`res.currency._convert`.
            DefaultstoTruebecausethatisthedefaultof`res.currency._convert`.
            WeputittoFalseifwewanttoroundglobally.
        :paramsforce_company_currencybool:
            IfTrue,thevaluesinamounts_to_addareincompany'scurrency.
            DefaultstoFalsebecauseitisonlyusedtoanglo-saxonlines.

        :returndict:newamountscombiningthevaluesof`old_amounts`and`amounts_to_add`.
        """
        #makeacopyoftheoldamounts
        new_amounts={**old_amounts}

        amount=amounts_to_add.get('amount')
        ifself.is_in_company_currencyorforce_company_currency:
            amount_converted=amount
        else:
            amount_converted=self._amount_converter(amount,date,round)

        #updateamountandamountconverted
        new_amounts['amount']+=amount
        new_amounts['amount_converted']+=amount_converted

        #considerbase_amountifpresent
        ifnotamounts_to_add.get('base_amount')==None:
            base_amount=amounts_to_add.get('base_amount')
            ifself.is_in_company_currencyorforce_company_currency:
                base_amount_converted=base_amount
            else:
                base_amount_converted=self._amount_converter(base_amount,date,round)

            #updatebase_amountandbase_amount_converted
            new_amounts['base_amount']+=base_amount
            new_amounts['base_amount_converted']+=base_amount_converted

        returnnew_amounts

    def_round_amounts(self,amounts):
        new_amounts={}
        forkey,amountinamounts.items():
            ifkey=='amount_converted':
                #roundtheamount_convertedusingthecompanycurrency.
                new_amounts[key]=self.company_id.currency_id.round(amount)
            else:
                new_amounts[key]=self.currency_id.round(amount)
        returnnew_amounts

    def_credit_amounts(self,partial_move_line_vals,amount,amount_converted,force_company_currency=False):
        """`partial_move_line_vals`iscompletedby`credit`ingthegivenamounts.

        NOTEAmountsinPoSareinthecurrencyofjournal_idinthesession.config_id.
        Thismeansthatamountfieldsinanyposrecordareactuallyequivalenttoamount_currency
        inaccountmodule.Understandingthisbasicisimportantincorrectlyassigningvaluesfor
        'amount'and'amount_currency'intheaccount.move.linerecord.

        :parampartial_move_line_valsdict:
            initialvaluesincreatingaccount.move.line
        :paramamountfloat:
            amountderivedfrompos.payment,pos.order,orpos.order.linerecords
        :paramamount_convertedfloat:
            convertedvalueof`amount`fromthegiven`session_currency`tocompanycurrency

        :returndict:completevaluesforcreating'amount.move.line'record
        """
        ifself.is_in_company_currencyorforce_company_currency:
            additional_field={}
        else:
            additional_field={
                'amount_currency':-amount,
                'currency_id':self.currency_id.id,
            }
        return{
            'debit':-amount_convertedifamount_converted<0.0else0.0,
            'credit':amount_convertedifamount_converted>0.0else0.0,
            **partial_move_line_vals,
            **additional_field,
        }

    def_debit_amounts(self,partial_move_line_vals,amount,amount_converted,force_company_currency=False):
        """`partial_move_line_vals`iscompletedby`debit`ingthegivenamounts.

        See_credit_amountsdocsformoredetails.
        """
        ifself.is_in_company_currencyorforce_company_currency:
            additional_field={}
        else:
            additional_field={
                'amount_currency':amount,
                'currency_id':self.currency_id.id,
            }
        return{
            'debit':amount_convertedifamount_converted>0.0else0.0,
            'credit':-amount_convertedifamount_converted<0.0else0.0,
            **partial_move_line_vals,
            **additional_field,
        }

    def_amount_converter(self,amount,date,round):
        #selfshouldbesinglerecordasthismethodisonlycalledinthesubfunctionsofself._validate_session
        returnself.currency_id._convert(amount,self.company_id.currency_id,self.company_id,date,round=round)

    defshow_journal_items(self):
        self.ensure_one()
        all_related_moves=self._get_related_account_moves()
        return{
            'name':_('JournalItems'),
            'type':'ir.actions.act_window',
            'res_model':'account.move.line',
            'view_mode':'tree',
            'view_id':self.env.ref('account.view_move_line_tree_grouped').id,
            'domain':[('id','in',all_related_moves.mapped('line_ids').ids)],
            'context':{
                'journal_type':'general',
                'search_default_group_by_move':1,
                'group_by':'move_id','search_default_posted':1,
                'name_groupby':1,
            },
        }

    def_get_related_account_moves(self):
        defget_matched_move_lines(aml):
            ifaml.credit>0:
                return[r.debit_move_id.idforrinaml.matched_debit_ids]
            else:
                return[r.credit_move_id.idforrinaml.matched_credit_ids]

        session_move=self.move_id
        #getallthelinkedmovelinestothisaccountmove.
        non_reconcilable_lines=session_move.line_ids.filtered(lambdaaml:notaml.account_id.reconcile)
        reconcilable_lines=session_move.line_ids-non_reconcilable_lines
        fully_reconciled_lines=reconcilable_lines.filtered(lambdaaml:aml.full_reconcile_id)
        partially_reconciled_lines=reconcilable_lines-fully_reconciled_lines

        cash_move_lines=self.env['account.move.line'].search([('statement_id','in',self.statement_ids.ids)])

        ids=(non_reconcilable_lines.ids
                +fully_reconciled_lines.mapped('full_reconcile_id').mapped('reconciled_line_ids').ids
                +sum(partially_reconciled_lines.mapped(get_matched_move_lines),partially_reconciled_lines.ids)
                +cash_move_lines.ids)

        returnself.env['account.move.line'].browse(ids).mapped('move_id')

    defaction_show_payments_list(self):
        return{
            'name':_('Payments'),
            'type':'ir.actions.act_window',
            'res_model':'pos.payment',
            'view_mode':'tree,form',
            'domain':[('session_id','=',self.id)],
            'context':{'search_default_group_by_payment_method':1}
        }

    defopen_frontend_cb(self):
        """Opentheposinterfacewithconfig_idasanextraargument.

        InvanillaPoSeachusercanonlyhaveoneactivesession,thereforeitwasnotneededtopasstheconfig_id
        onopeningasession.Itisalsopossibletologintosessionscreatedbyotherusers.

        :returns:dict
        """
        ifnotself.ids:
            return{}
        return{
            'type':'ir.actions.act_url',
            'target':'self',
            'url':self.config_id._get_pos_base_url()+'?config_id=%d'%self.config_id.id,
        }

    defopen_cashbox_pos(self):
        self.ensure_one()
        action=self.cash_register_id.open_cashbox_id()
        action['view_id']=self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
        action['context']['pos_session_id']=self.id
        action['context']['default_pos_id']=self.config_id.id
        returnaction

    defset_cashbox_pos(self,cashbox_value,notes):
        self.state='opened'
        self.cash_register_id.balance_start=cashbox_value
        ifnotes:
            self.env['mail.message'].create({
                        'body':notes,
                        'model':'account.bank.statement',
                        'res_id':self.cash_register_id.id,
                    })

    defaction_view_order(self):
        return{
            'name':_('Orders'),
            'res_model':'pos.order',
            'view_mode':'tree,form',
            'views':[
                (self.env.ref('point_of_sale.view_pos_order_tree_no_session_id').id,'tree'),
                (self.env.ref('point_of_sale.view_pos_pos_form').id,'form'),
                ],
            'type':'ir.actions.act_window',
            'domain':[('session_id','in',self.ids)],
        }

    @api.model
    def_alert_old_session(self):
        #Ifthesessionisopenformorethenoneweek,
        #loganextactivitytoclosethesession.
        sessions=self.sudo().search([('start_at','<=',(fields.datetime.now()-timedelta(days=7))),('state','!=','closed')])
        forsessioninsessions:
            ifself.env['mail.activity'].search_count([('res_id','=',session.id),('res_model','=','pos.session')])==0:
                session.activity_schedule(
                    'point_of_sale.mail_activity_old_session',
                    user_id=session.user_id.id,
                    note=_(
                        "YourPoSSessionisopensince%(date)s,weadviseyoutocloseitandtocreateanewone.",
                        date=session.start_at,
                    )
                )

    def_warning_balance_closing(self):
        self.ensure_one()

        context=dict(self._context)
        context['session_id']=self.id

        return{
            'name':_('Balancecontrol'),
            'view_type':'form',
            'view_mode':'form',
            'res_model':'closing.balance.confirm.wizard',
            'views':[(False,'form')],
            'type':'ir.actions.act_window',
            'context':context,
            'target':'new'
        }

    def_check_if_no_draft_orders(self):
        draft_orders=self.order_ids.filtered(lambdaorder:order.state=='draft')
        ifdraft_orders:
            raiseUserError(_(
                    'Therearestillordersindraftstateinthesession.'
                    'Payorcancelthefollowingorderstovalidatethesession:\n%s'
                )%','.join(draft_orders.mapped('name'))
            )
        returnTrue

classProcurementGroup(models.Model):
    _inherit='procurement.group'

    @api.model
    def_run_scheduler_tasks(self,use_new_cursor=False,company_id=False):
        super(ProcurementGroup,self)._run_scheduler_tasks(use_new_cursor=use_new_cursor,company_id=company_id)
        self.env['pos.session']._alert_old_session()
        ifuse_new_cursor:
            self.env.cr.commit()

classClosingBalanceConfirm(models.TransientModel):
    _name='closing.balance.confirm.wizard'
    _description='Thiswizardisusedtodisplayawarningmessageifthemanagerwantstocloseasessionwithatoohighdifferencebetweenrealandexpectedclosingbalance'

    defconfirm_closing_balance(self):
        current_session= self.env['pos.session'].browse(self._context['session_id'])
        returncurrent_session._validate_session()
