#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
fromdatetimeimporttimedelta
fromfunctoolsimportpartial

importpsycopg2
importpytz
importre

fromflectraimportapi,fields,models,tools,_
fromflectra.toolsimportfloat_is_zero,float_round
fromflectra.exceptionsimportValidationError,UserError
fromflectra.httpimportrequest
fromflectra.osv.expressionimportAND
importbase64

_logger=logging.getLogger(__name__)


classPosOrder(models.Model):
    _name="pos.order"
    _description="PointofSaleOrders"
    _order="date_orderdesc,namedesc,iddesc"

    @api.model
    def_amount_line_tax(self,line,fiscal_position_id):
        taxes=line.tax_ids.filtered(lambdat:t.company_id.id==line.order_id.company_id.id)
        taxes=fiscal_position_id.map_tax(taxes,line.product_id,line.order_id.partner_id)
        price=line.price_unit*(1-(line.discountor0.0)/100.0)
        taxes=taxes.compute_all(price,line.order_id.pricelist_id.currency_id,line.qty,product=line.product_id,partner=line.order_id.partner_idorFalse)['taxes']
        returnsum(tax.get('amount',0.0)fortaxintaxes)

    @api.model
    def_order_fields(self,ui_order):
        process_line=partial(self.env['pos.order.line']._order_line_fields,session_id=ui_order['pos_session_id'])
        return{
            'user_id':     ui_order['user_id']orFalse,
            'session_id':  ui_order['pos_session_id'],
            'lines':       [process_line(l)forlinui_order['lines']]ifui_order['lines']elseFalse,
            'pos_reference':ui_order['name'],
            'sequence_number':ui_order['sequence_number'],
            'partner_id':  ui_order['partner_id']orFalse,
            'date_order':  ui_order['creation_date'].replace('T','')[:19],
            'fiscal_position_id':ui_order['fiscal_position_id'],
            'pricelist_id':ui_order['pricelist_id'],
            'amount_paid': ui_order['amount_paid'],
            'amount_total': ui_order['amount_total'],
            'amount_tax': ui_order['amount_tax'],
            'amount_return': ui_order['amount_return'],
            'company_id':self.env['pos.session'].browse(ui_order['pos_session_id']).company_id.id,
            'to_invoice':ui_order['to_invoice']if"to_invoice"inui_orderelseFalse,
            'is_tipped':ui_order.get('is_tipped',False),
            'tip_amount':ui_order.get('tip_amount',0),
        }

    @api.model
    def_payment_fields(self,order,ui_paymentline):
        return{
            'amount':ui_paymentline['amount']or0.0,
            'payment_date':ui_paymentline['name'],
            'payment_method_id':ui_paymentline['payment_method_id'],
            'card_type':ui_paymentline.get('card_type'),
            'cardholder_name':ui_paymentline.get('cardholder_name'),
            'transaction_id':ui_paymentline.get('transaction_id'),
            'payment_status':ui_paymentline.get('payment_status'),
            'ticket':ui_paymentline.get('ticket'),
            'pos_order_id':order.id,
        }

    #Thisdealswithordersthatbelongtoaclosedsession.Inorder
    #torecoverfromthissituationwecreateanewrescuesession,
    #makingitobviousthatsomethingwentwrong.
    #Anew,separate,rescuesessionispreferredforeverysuchrecovery,
    #toavoidaddingunrelatedorderstolivesessions.
    def_get_valid_session(self,order):
        PosSession=self.env['pos.session']
        closed_session=PosSession.browse(order['pos_session_id'])

        _logger.warning('session%s(ID:%s)wasclosedbutreceivedorder%s(total:%s)belongingtoit',
                        closed_session.name,
                        closed_session.id,
                        order['name'],
                        order['amount_total'])
        rescue_session=PosSession.search([
            ('state','notin',('closed','closing_control')),
            ('rescue','=',True),
            ('config_id','=',closed_session.config_id.id),
        ],limit=1)
        ifrescue_session:
            _logger.warning('reusingrecoverysession%sforsavingorder%s',rescue_session.name,order['name'])
            returnrescue_session

        _logger.warning('attemptingtocreaterecoverysessionforsavingorder%s',order['name'])
        new_session=PosSession.create({
            'config_id':closed_session.config_id.id,
            'name':_('(RESCUEFOR%(session)s)')%{'session':closed_session.name},
            'rescue':True, #avoidconflictwithlivesessions
        })
        #bypassopening_control(necessarywhenusingcashcontrol)
        new_session.action_pos_session_open()

        returnnew_session

    def_get_fields_for_draft_order(self):
        """Thismethodisheretobeoverriddeninordertoaddfieldsthatarerequiredfordraftorders."""
        return[]

    @api.model
    def_process_order(self,order,draft,existing_order):
        """Createorupdateanpos.orderfromagivendictionary.

        :paramdictorder:dictionaryrepresentingtheorder.
        :parambooldraft:Indicatethatthepos_orderisnotvalidatedyet.
        :paramexisting_order:ordertobeupdatedorFalse.
        :typeexisting_order:pos.order.
        :returns:idofcreated/updatedpos.order
        :rtype:int
        """
        order=order['data']
        pos_session=self.env['pos.session'].browse(order['pos_session_id'])
        ifpos_session.state=='closing_control'orpos_session.state=='closed':
            order['pos_session_id']=self._get_valid_session(order).id

        pos_order=False
        ifnotexisting_order:
            pos_order=self.create(self._order_fields(order))
        else:
            pos_order=existing_order
            pos_order.lines.unlink()
            order['user_id']=pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        pos_order=pos_order.with_company(pos_order.company_id)
        self=self.with_company(pos_order.company_id)
        self._process_payment_lines(order,pos_order,pos_session,draft)

        ifnotdraft:
            try:
                pos_order.action_pos_order_paid()
            exceptpsycopg2.DatabaseError:
                #donothidetransactionalerrors,theorder(s)won'tbesaved!
                raise
            exceptExceptionase:
                _logger.error('CouldnotfullyprocessthePOSOrder:%s',tools.ustr(e))
            pos_order._create_order_picking()

        ifpos_order.to_invoiceandpos_order.state=='paid':
            pos_order._generate_pos_order_invoice()

        returnpos_order.id


    def_process_payment_lines(self,pos_order,order,pos_session,draft):
        """Createaccount.bank.statement.linesfromthedictionarygiventotheparentfunction.

        Ifthepayment_lineisanupdatedversionofanexistingone,theexistingpayment_linewillfirstbe
        removedbeforemakinganewone.
        :parampos_order:dictionaryrepresentingtheorder.
        :typepos_order:dict.
        :paramorder:Orderobjectthepaymentlinesshouldbelongto.
        :typeorder:pos.order
        :parampos_session:PoSsessiontheorderwascreatedin.
        :typepos_session:pos.session
        :paramdraft:Indicatethatthepos_orderisnotvalidatedyet.
        :typedraft:bool.
        """
        prec_acc=order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines=self.env['pos.payment'].search([('pos_order_id','=',order.id)])
        order_bank_statement_lines.unlink()
        forpaymentsinpos_order['statement_ids']:
            order.add_payment(self._payment_fields(order,payments[2]))

        order.amount_paid=sum(order.payment_ids.mapped('amount'))

        ifnotdraftandnotfloat_is_zero(pos_order['amount_return'],prec_acc):
            cash_payment_method=pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            ifnotcash_payment_method:
                raiseUserError(_("Nocashstatementfoundforthissession.Unabletorecordreturnedcash."))
            return_payment_vals={
                'name':_('return'),
                'pos_order_id':order.id,
                'amount':-pos_order['amount_return'],
                'payment_date':fields.Datetime.now(),
                'payment_method_id':cash_payment_method.id,
                'is_change':True,
            }
            order.add_payment(return_payment_vals)

    def_prepare_invoice_line(self,order_line):
        display_name=order_line.product_id.get_product_multiline_description_sale()
        name=order_line.product_id.default_code+""+display_nameiforder_line.product_id.default_codeelsedisplay_name
        return{
            'product_id':order_line.product_id.id,
            'quantity':order_line.qtyifself.amount_total>=0else-order_line.qty,
            'discount':order_line.discount,
            'price_unit':order_line.price_unit,
            'name':name,
            'tax_ids':[(6,0,order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id':order_line.product_uom_id.id,
        }

    def_get_pos_anglo_saxon_price_unit(self,product,partner_id,quantity):
        moves=self.filtered(lambdao:o.partner_id.id==partner_id)\
            .mapped('picking_ids.move_lines')\
            ._filter_anglo_saxon_moves(product)\
            .sorted(lambdax:x.date)
        price_unit=product.with_company(self.company_id)._compute_average_price(0,quantity,moves)
        returnprice_unit

    name=fields.Char(string='OrderRef',required=True,readonly=True,copy=False,default='/')
    date_order=fields.Datetime(string='Date',readonly=True,index=True,default=fields.Datetime.now)
    user_id=fields.Many2one(
        comodel_name='res.users',string='Responsible',
        help="Personwhousesthecashregister.Itcanbeareliever,astudentoraninterimemployee.",
        default=lambdaself:self.env.uid,
        states={'done':[('readonly',True)],'invoiced':[('readonly',True)]},
    )
    amount_tax=fields.Float(string='Taxes',digits=0,readonly=True,required=True)
    amount_total=fields.Float(string='Total',digits=0,readonly=True,required=True)
    amount_paid=fields.Float(string='Paid',states={'draft':[('readonly',False)]},
        readonly=True,digits=0,required=True)
    amount_return=fields.Float(string='Returned',digits=0,required=True,readonly=True)
    lines=fields.One2many('pos.order.line','order_id',string='OrderLines',states={'draft':[('readonly',False)]},readonly=True,copy=True)
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True)
    pricelist_id=fields.Many2one('product.pricelist',string='Pricelist',required=True,states={
                                   'draft':[('readonly',False)]},readonly=True)
    partner_id=fields.Many2one('res.partner',string='Customer',change_default=True,index=True,states={'draft':[('readonly',False)],'paid':[('readonly',False)]})
    sequence_number=fields.Integer(string='SequenceNumber',help='Asession-uniquesequencenumberfortheorder',default=1)

    session_id=fields.Many2one(
        'pos.session',string='Session',required=True,index=True,
        domain="[('state','=','opened')]",states={'draft':[('readonly',False)]},
        readonly=True)
    config_id=fields.Many2one('pos.config',related='session_id.config_id',string="PointofSale",readonly=False)
    currency_id=fields.Many2one('res.currency',related='config_id.currency_id',string="Currency")
    currency_rate=fields.Float("CurrencyRate",compute='_compute_currency_rate',compute_sudo=True,store=True,digits=0,readonly=True,
        help='Therateofthecurrencytothecurrencyofrateapplicableatthedateoftheorder')

    invoice_group=fields.Boolean(related="config_id.module_account",readonly=False)
    state=fields.Selection(
        [('draft','New'),('cancel','Cancelled'),('paid','Paid'),('done','Posted'),('invoiced','Invoiced')],
        'Status',readonly=True,copy=False,default='draft',index=True)

    account_move=fields.Many2one('account.move',string='Invoice',readonly=True,copy=False,index=True)
    picking_ids=fields.One2many('stock.picking','pos_order_id')
    picking_count=fields.Integer(compute='_compute_picking_count')
    failed_pickings=fields.Boolean(compute='_compute_picking_count')
    picking_type_id=fields.Many2one('stock.picking.type',related='session_id.config_id.picking_type_id',string="OperationType",readonly=False)

    note=fields.Text(string='InternalNotes')
    nb_print=fields.Integer(string='NumberofPrint',readonly=True,copy=False,default=0)
    pos_reference=fields.Char(string='ReceiptNumber',readonly=True,copy=False)
    sale_journal=fields.Many2one('account.journal',related='session_id.config_id.journal_id',string='SalesJournal',store=True,readonly=True,ondelete='restrict')
    fiscal_position_id=fields.Many2one(
        comodel_name='account.fiscal.position',string='FiscalPosition',
        readonly=True,
        states={'draft':[('readonly',False)]},
    )
    payment_ids=fields.One2many('pos.payment','pos_order_id',string='Payments',readonly=True)
    session_move_id=fields.Many2one('account.move',string='SessionJournalEntry',related='session_id.move_id',readonly=True,copy=False)
    to_invoice=fields.Boolean('Toinvoice',copy=False)
    is_invoiced=fields.Boolean('IsInvoiced',compute='_compute_is_invoiced')
    is_tipped=fields.Boolean('Isthisalreadytipped?',readonly=True)
    tip_amount=fields.Float(string='TipAmount',digits=0,readonly=True)

    @api.depends('account_move')
    def_compute_is_invoiced(self):
        fororderinself:
            order.is_invoiced=bool(order.account_move)

    @api.depends('picking_ids','picking_ids.state')
    def_compute_picking_count(self):
        fororderinself:
            order.picking_count=len(order.picking_ids)
            order.failed_pickings=bool(order.picking_ids.filtered(lambdap:p.state!='done'))

    @api.depends('date_order','company_id','currency_id','company_id.currency_id')
    def_compute_currency_rate(self):
        fororderinself:
            order.currency_rate=self.env['res.currency']._get_conversion_rate(order.company_id.currency_id,order.currency_id,order.company_id,order.date_order)

    @api.onchange('payment_ids','lines')
    def_onchange_amount_all(self):
        fororderinself:
            ifnotorder.pricelist_id.currency_id:
                raiseUserError(_("Youcan't:createaposorderfromthebackendinterface,orunsetthepricelist,orcreateapos.orderinapythontestwithFormtool,oredittheformviewinstudioifnoPoSorderexist"))
            currency=order.pricelist_id.currency_id
            order.amount_paid=sum(payment.amountforpaymentinorder.payment_ids)
            order.amount_return=sum(payment.amount<0andpayment.amountor0forpaymentinorder.payment_ids)
            order.amount_tax=currency.round(sum(self._amount_line_tax(line,order.fiscal_position_id)forlineinorder.lines))
            amount_untaxed=currency.round(sum(line.price_subtotalforlineinorder.lines))
            order.amount_total=order.amount_tax+amount_untaxed

    def_compute_batch_amount_all(self):
        """
        Doesessentiallythesamethingas`_onchange_amount_all`butonlyforactuallyexistingrecords
        Itisintendedasahelpermethod,notasabusinessone
        Practicaltobeusedformigrations
        """
        amounts={order_id:{'paid':0,'return':0,'taxed':0,'taxes':0}fororder_idinself.ids}
        fororderinself.env['pos.payment'].read_group([('pos_order_id','in',self.ids)],['pos_order_id','amount'],['pos_order_id']):
            amounts[order['pos_order_id'][0]]['paid']=order['amount']
        fororderinself.env['pos.payment'].read_group(['&',('pos_order_id','in',self.ids),('amount','<',0)],['pos_order_id','amount'],['pos_order_id']):
            amounts[order['pos_order_id'][0]]['return']=order['amount']
        fororderinself.env['pos.order.line'].read_group([('order_id','in',self.ids)],['order_id','price_subtotal','price_subtotal_incl'],['order_id']):
            amounts[order['order_id'][0]]['taxed']=order['price_subtotal_incl']
            amounts[order['order_id'][0]]['taxes']=order['price_subtotal_incl']-order['price_subtotal']

        fororderinself:
            currency=order.pricelist_id.currency_id
            order.write({
                'amount_paid':amounts[order.id]['paid'],
                'amount_return':amounts[order.id]['return'],
                'amount_tax':currency.round(amounts[order.id]['taxes']),
                'amount_total':currency.round(amounts[order.id]['taxed'])
            })

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        ifself.partner_id:
            self.pricelist_id=self.partner_id.property_product_pricelist.id

    defunlink(self):
        forpos_orderinself.filtered(lambdapos_order:pos_order.statenotin['draft','cancel']):
            raiseUserError(_('Inordertodeleteasale,itmustbeneworcancelled.'))
        returnsuper(PosOrder,self).unlink()

    @api.model
    defcreate(self,values):
        session=self.env['pos.session'].browse(values['session_id'])
        values=self._complete_values_from_session(session,values)
        returnsuper(PosOrder,self).create(values)

    @api.model
    def_complete_values_from_session(self,session,values):
        ifvalues.get('state')andvalues['state']=='paid':
            values['name']=session.config_id.sequence_id._next()
        values.setdefault('pricelist_id',session.config_id.pricelist_id.id)
        values.setdefault('fiscal_position_id',session.config_id.default_fiscal_position_id.id)
        values.setdefault('company_id',session.config_id.company_id.id)
        returnvalues

    defwrite(self,vals):
        fororderinself:
            ifvals.get('state')andvals['state']=='paid'andorder.name=='/':
                vals['name']=order.config_id.sequence_id._next()
        returnsuper(PosOrder,self).write(vals)

    defaction_stock_picking(self):
        self.ensure_one()
        action=self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_ready')
        action['display_name']=_('Pickings')
        action['context']={}
        action['domain']=[('id','in',self.picking_ids.ids)]
        returnaction

    defaction_view_invoice(self):
        return{
            'name':_('CustomerInvoice'),
            'view_mode':'form',
            'view_id':self.env.ref('account.view_move_form').id,
            'res_model':'account.move',
            'context':"{'move_type':'out_invoice'}",
            'type':'ir.actions.act_window',
            'res_id':self.account_move.id,
        }

    def_is_pos_order_paid(self):
        returnfloat_is_zero(self._get_rounded_amount(self.amount_total)-self.amount_paid,precision_rounding=self.currency_id.rounding)

    def_get_rounded_amount(self,amount):
        ifself.config_id.cash_rounding:
            amount=float_round(amount,precision_rounding=self.config_id.rounding_method.rounding,rounding_method=self.config_id.rounding_method.rounding_method)
        currency=self.currency_id
        returncurrency.round(amount)ifcurrencyelseamount

    def_create_invoice(self,move_vals):
        self.ensure_one()
        new_move=self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type=move_vals['move_type']).create(move_vals)
        message=_("Thisinvoicehasbeencreatedfromthepointofsalesession:<ahref=#data-oe-model=pos.orderdata-oe-id=%d>%s</a>")%(self.id,self.name)
        new_move.message_post(body=message)
        ifself.config_id.cash_rounding:
            rounding_applied=float_round(self.amount_paid-self.amount_total,
                                           precision_rounding=new_move.currency_id.rounding)
            rounding_line=new_move.line_ids.filtered(lambdaline:line.is_rounding_line)
            ifrounding_lineandrounding_line.debit>0:
                rounding_line_difference=rounding_line.debit+rounding_applied
            elifrounding_lineandrounding_line.credit>0:
                rounding_line_difference=-rounding_line.credit+rounding_applied
            else:
                rounding_line_difference=rounding_applied
            ifrounding_applied:
                ifrounding_applied>0.0:
                    account_id=new_move.invoice_cash_rounding_id.loss_account_id.id
                else:
                    account_id=new_move.invoice_cash_rounding_id.profit_account_id.id
                ifrounding_line:
                    ifrounding_line_difference:
                        rounding_line.with_context(check_move_validity=False).write({
                            'debit':rounding_applied<0.0and-rounding_appliedor0.0,
                            'credit':rounding_applied>0.0androunding_appliedor0.0,
                            'account_id':account_id,
                            'price_unit':rounding_applied,
                        })

                else:
                    self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'debit':rounding_applied<0.0and-rounding_appliedor0.0,
                        'credit':rounding_applied>0.0androunding_appliedor0.0,
                        'quantity':1.0,
                        'amount_currency':rounding_applied,
                        'partner_id':new_move.partner_id.id,
                        'move_id':new_move.id,
                        'currency_id':new_move.currency_idifnew_move.currency_id!=new_move.company_id.currency_idelseFalse,
                        'company_id':new_move.company_id.id,
                        'company_currency_id':new_move.company_id.currency_id.id,
                        'is_rounding_line':True,
                        'sequence':9999,
                        'name':new_move.invoice_cash_rounding_id.name,
                        'account_id':account_id,
                    })
            else:
                ifrounding_line:
                    rounding_line.with_context(check_move_validity=False).unlink()
            ifrounding_line_difference:
                existing_terms_line=new_move.line_ids.filtered(
                    lambdaline:line.account_id.user_type_id.typein('receivable','payable'))
                ifexisting_terms_line.debit>0:
                    existing_terms_line_new_val=float_round(
                        existing_terms_line.debit+rounding_line_difference,
                        precision_rounding=new_move.currency_id.rounding)
                else:
                    existing_terms_line_new_val=float_round(
                        -existing_terms_line.credit+rounding_line_difference,
                        precision_rounding=new_move.currency_id.rounding)
                existing_terms_line.write({
                    'debit':existing_terms_line_new_val>0.0andexisting_terms_line_new_valor0.0,
                    'credit':existing_terms_line_new_val<0.0and-existing_terms_line_new_valor0.0,
                })

                new_move._recompute_payment_terms_lines()
        returnnew_move

    defaction_pos_order_paid(self):
        self.ensure_one()

        #TODO:addsupportformixofcashandnon-cashpaymentswhenbothcash_roundingandonly_round_cash_methodareTrue
        ifnotself.config_id.cash_rounding\
           orself.config_id.only_round_cash_method\
           andnotany(p.payment_method_id.is_cash_countforpinself.payment_ids):
            total=self.amount_total
        else:
            total=float_round(self.amount_total,precision_rounding=self.config_id.rounding_method.rounding,rounding_method=self.config_id.rounding_method.rounding_method)

        isPaid=float_is_zero(total-self.amount_paid,precision_rounding=self.currency_id.rounding)

        ifnotisPaidandnotself.config_id.cash_rounding:
            raiseUserError(_("Order%sisnotfullypaid.",self.name))
        elifnotisPaidandself.config_id.cash_rounding:
            currency=self.currency_id
            ifself.config_id.rounding_method.rounding_method=="HALF-UP":
                maxDiff=currency.round(self.config_id.rounding_method.rounding/2)
            else:
                maxDiff=currency.round(self.config_id.rounding_method.rounding)

            diff=currency.round(self.amount_total-self.amount_paid)
            ifnotabs(diff)<=maxDiff:
                raiseUserError(_("Order%sisnotfullypaid.",self.name))

        self.write({'state':'paid'})

        returnTrue

    def_prepare_invoice_vals(self):
        self.ensure_one()
        timezone=pytz.timezone(self._context.get('tz')orself.env.user.tzor'UTC')
        note=self.noteor''
        terms=''
        ifself.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')andself.env.company.invoice_terms:
            terms=self.with_context(lang=self.partner_id.lang).env.company.invoice_terms

        narration=note+'\n'+termsifnoteelseterms

        vals={
            'payment_reference':self.name,
            'invoice_origin':self.name,
            'journal_id':self.session_id.config_id.invoice_journal_id.id,
            'move_type':'out_invoice'ifself.amount_total>=0else'out_refund',
            'ref':self.name,
            'partner_id':self.partner_id.id,
            'narration':narration,
            #consideringpartner'ssalepricelist'scurrency
            'currency_id':self.pricelist_id.currency_id.id,
            'invoice_user_id':self.user_id.id,
            'invoice_date':self.date_order.astimezone(timezone).date(),
            'fiscal_position_id':self.fiscal_position_id.id,
            'invoice_line_ids':[(0,None,self._prepare_invoice_line(line))forlineinself.lines],
            'invoice_cash_rounding_id':self.config_id.rounding_method.id
            ifself.config_id.cash_roundingand(notself.config_id.only_round_cash_methodorany(p.payment_method_id.is_cash_countforpinself.payment_ids))
            elseFalse
        }
        returnvals
    defaction_pos_order_invoice(self):
        self.write({'to_invoice':True})
        res=self._generate_pos_order_invoice()
        ifself.company_id.anglo_saxon_accountingandself.session_id.update_stock_at_closing:
            self._create_order_picking()
        returnres

    def_generate_pos_order_invoice(self):
        moves=self.env['account.move']

        fororderinself:
            #ForcecompanyforallSUPERUSER_IDaction
            iforder.account_move:
                moves+=order.account_move
                continue

            ifnotorder.partner_id:
                raiseUserError(_('Pleaseprovideapartnerforthesale.'))

            move_vals=order._prepare_invoice_vals()
            new_move=order._create_invoice(move_vals)
            order.write({'account_move':new_move.id,'state':'invoiced'})
            new_move.sudo().with_company(order.company_id)._post()
            moves+=new_move

        ifnotmoves:
            return{}

        return{
            'name':_('CustomerInvoice'),
            'view_mode':'form',
            'view_id':self.env.ref('account.view_move_form').id,
            'res_model':'account.move',
            'context':"{'move_type':'out_invoice'}",
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'target':'current',
            'res_id':movesandmoves.ids[0]orFalse,
        }

    #thismethodisunused,andsoisthestate'cancel'
    defaction_pos_order_cancel(self):
        returnself.write({'state':'cancel'})

    @api.model
    defcreate_from_ui(self,orders,draft=False):
        """CreateandupdateOrdersfromthefrontendPoSapplication.

        Createnewordersandupdateordersthatareindraftstatus.Ifanorderalreadyexistswithastatus
        diferentfrom'draft'itwillbediscareded,otherwiseitwillbesavedtothedatabase.Ifsavedwith
        'draft'statustheordercanbeoverwrittenlaterbythisfunction.

        :paramorders:dictionarywiththeorderstobecreated.
        :typeorders:dict.
        :paramdraft:Indicateiftheordersarementtobefinalisedortemporarilysaved.
        :typedraft:bool.
        :Returns:list--listofdb-idsforthecreatedandupdatedorders.
        """
        order_ids=[]
        fororderinorders:
            existing_order=False
            if'server_id'inorder['data']:
                existing_order=self.env['pos.order'].search(['|',('id','=',order['data']['server_id']),('pos_reference','=',order['data']['name'])],limit=1)
            if(existing_orderandexisting_order.state=='draft')ornotexisting_order:
                order_ids.append(self._process_order(order,draft,existing_order))

        returnself.env['pos.order'].search_read(domain=[('id','in',order_ids)],fields=['id','pos_reference'])

    def_create_order_picking(self):
        self.ensure_one()
        ifnotself.session_id.update_stock_at_closingor(self.company_id.anglo_saxon_accountingandself.to_invoice):
            picking_type=self.config_id.picking_type_id
            ifself.partner_id.property_stock_customer:
                destination_id=self.partner_id.property_stock_customer.id
            elifnotpicking_typeornotpicking_type.default_location_dest_id:
                destination_id=self.env['stock.warehouse']._get_partner_locations()[0].id
            else:
                destination_id=picking_type.default_location_dest_id.id

            pickings=self.env['stock.picking']._create_picking_from_pos_order_lines(destination_id,self.lines,picking_type,self.partner_id)
            pickings.write({'pos_session_id':self.session_id.id,'pos_order_id':self.id,'origin':self.name})

    defadd_payment(self,data):
        """Createanewpaymentfortheorder"""
        self.ensure_one()
        self.env['pos.payment'].create(data)
        self.amount_paid=sum(self.payment_ids.mapped('amount'))

    def_prepare_refund_values(self,current_session):
        self.ensure_one()
        return{
            'name':self.name+_('REFUND'),
            'session_id':current_session.id,
            'date_order':fields.Datetime.now(),
            'pos_reference':self.pos_reference,
            'lines':False,
            'amount_tax':-self.amount_tax,
            'amount_total':-self.amount_total,
            'amount_paid':0,
        }

    def_prepare_mail_values(self,name,message,client,receipt):
        return{
            'subject':_('Receipt%s',name),
            'body_html':message,
            'author_id':self.env.user.partner_id.id,
            'email_from':self.env.company.emailorself.env.user.email_formatted,
            'email_to':client['email'],
            'attachment_ids':[(4,receipt.id)],
        }

    defrefund(self):
        """Createacopyoforder forrefundorder"""
        refund_orders=self.env['pos.order']
        fororderinself:
            #Whenarefundisperformed,wearecreatingitinasessionhavingthesameconfigastheoriginal
            #order.Itcanbethesamesession,orifithasbeenclosedthenewonethathasbeenopened.
            current_session=order.session_id.config_id.current_session_id
            ifnotcurrent_session:
                raiseUserError(_('Toreturnproduct(s),youneedtoopenasessioninthePOS%s',order.session_id.config_id.display_name))
            refund_order=order.copy(
                order._prepare_refund_values(current_session)
            )
            forlineinorder.lines:
                PosOrderLineLot=self.env['pos.pack.operation.lot']
                forpack_lotinline.pack_lot_ids:
                    PosOrderLineLot+=pack_lot.copy()
                line.copy(line._prepare_refund_data(refund_order,PosOrderLineLot))
            refund_orders|=refund_order

        return{
            'name':_('ReturnProducts'),
            'view_mode':'form',
            'res_model':'pos.order',
            'res_id':refund_orders.ids[0],
            'view_id':False,
            'context':self.env.context,
            'type':'ir.actions.act_window',
            'target':'current',
        }

    defaction_receipt_to_customer(self,name,client,ticket):
        ifnotself:
            returnFalse
        ifnotclient.get('email'):
            returnFalse

        message=_("<p>Dear%s,<br/>Hereisyourelectronicticketforthe%s.</p>")%(client['name'],name)
        filename='Receipt-'+name+'.jpg'
        receipt=self.env['ir.attachment'].create({
            'name':filename,
            'type':'binary',
            'datas':ticket,
            'res_model':'pos.order',
            'res_id':self.ids[0],
            'mimetype':'image/jpeg',
        })

        mail_values=self._prepare_mail_values(name,message,client,receipt)

        ifself.mapped('account_move'):
            report=self.env.ref('point_of_sale.pos_invoice_report')._render_qweb_pdf(self.ids[0])
            filename=name+'.pdf'
            attachment=self.env['ir.attachment'].create({
                'name':filename,
                'type':'binary',
                'datas':base64.b64encode(report[0]),
                'res_model':'pos.order',
                'res_id':self.ids[0],
                'mimetype':'application/x-pdf'
            })
            mail_values['attachment_ids']+=[(4,attachment.id)]

        mail=self.env['mail.mail'].sudo().create(mail_values)
        mail.send()

    @api.model
    defremove_from_ui(self,server_ids):
        """RemoveordersfromthefrontendPoSapplication

        Removeordersfromtheserverbyid.
        :paramserver_ids:listoftheid'soforderstoremovefromtheserver.
        :typeserver_ids:list.
        :returns:list--listofdb-idsfortheremovedorders.
        """
        orders=self.search([('id','in',server_ids),('state','=','draft')])
        orders.write({'state':'cancel'})
        #TODOLookslikedeletecascadeisabettersolution.
        orders.mapped('payment_ids').sudo().unlink()
        orders.sudo().unlink()
        returnorders.ids

    @api.model
    defsearch_paid_order_ids(self,config_id,domain,limit,offset):
        """Searchfor'paid'ordersthatsatisfythegivendomain,limitandoffset."""
        default_domain=['&',('config_id','=',config_id),'!','|',('state','=','draft'),('state','=','cancelled')]
        real_domain=AND([domain,default_domain])
        ids=self.search(AND([domain,default_domain]),limit=limit,offset=offset).ids
        totalCount=self.search_count(real_domain)
        return{'ids':ids,'totalCount':totalCount}

    def_export_for_ui(self,order):
        timezone=pytz.timezone(self._context.get('tz')orself.env.user.tzor'UTC')
        return{
            'lines':[[0,0,line]forlineinorder.lines.export_for_ui()],
            'statement_ids':[[0,0,payment]forpaymentinorder.payment_ids.export_for_ui()],
            'name':order.pos_reference,
            'uid':re.search('([0-9]|-){14}',order.pos_reference).group(0),
            'amount_paid':order.amount_paid,
            'amount_total':order.amount_total,
            'amount_tax':order.amount_tax,
            'amount_return':order.amount_return,
            'pos_session_id':order.session_id.id,
            'is_session_closed':order.session_id.state=='closed',
            'pricelist_id':order.pricelist_id.id,
            'partner_id':order.partner_id.id,
            'user_id':order.user_id.id,
            'sequence_number':order.sequence_number,
            'creation_date':order.date_order.astimezone(timezone),
            'fiscal_position_id':order.fiscal_position_id.id,
            'to_invoice':order.to_invoice,
            'state':order.state,
            'account_move':order.account_move.id,
            'id':order.id,
            'is_tipped':order.is_tipped,
            'tip_amount':order.tip_amount,
        }

    defexport_for_ui(self):
        """Returnsalistofdictwitheachitemhavingsimilarsignatureasthereturnof
            `export_as_JSON`ofmodels.Order.Thisisusefulforback-and-forthcommunication
            betweentheposfrontendandbackend.
        """
        returnself.mapped(self._export_for_ui)ifselfelse[]


classPosOrderLine(models.Model):
    _name="pos.order.line"
    _description="PointofSaleOrderLines"
    _rec_name="product_id"

    def_order_line_fields(self,line,session_id=None):
        iflineand'name'notinline[2]:
            session=self.env['pos.session'].browse(session_id).exists()ifsession_idelseNone
            ifsessionandsession.config_id.sequence_line_id:
                #setnamebasedonthesequencespecifiedontheconfig
                line[2]['name']=session.config_id.sequence_line_id._next()
            else:
                #fallbackonanypos.order.linesequence
                line[2]['name']=self.env['ir.sequence'].next_by_code('pos.order.line')

        iflineand'tax_ids'notinline[2]:
            product=self.env['product.product'].browse(line[2]['product_id'])
            line[2]['tax_ids']=[(6,0,[x.idforxinproduct.taxes_id])]
        #CleanupfieldssentbytheJS
        line=[
            line[0],line[1],{k:vfork,vinline[2].items()ifkinself.env['pos.order.line']._fields}
        ]
        returnline

    company_id=fields.Many2one('res.company',string='Company',related="order_id.company_id",store=True)
    name=fields.Char(string='LineNo',required=True,copy=False)
    notice=fields.Char(string='DiscountNotice')
    product_id=fields.Many2one('product.product',string='Product',domain=[('sale_ok','=',True)],required=True,change_default=True)
    price_unit=fields.Float(string='UnitPrice',digits=0)
    qty=fields.Float('Quantity',digits='ProductUnitofMeasure',default=1)
    price_subtotal=fields.Float(string='Subtotalw/oTax',digits=0,
        readonly=True,required=True)
    price_subtotal_incl=fields.Float(string='Subtotal',digits=0,
        readonly=True,required=True)
    discount=fields.Float(string='Discount(%)',digits=0,default=0.0)
    order_id=fields.Many2one('pos.order',string='OrderRef',ondelete='cascade',required=True,index=True)
    tax_ids=fields.Many2many('account.tax',string='Taxes',readonly=True)
    tax_ids_after_fiscal_position=fields.Many2many('account.tax',compute='_get_tax_ids_after_fiscal_position',string='TaxestoApply')
    pack_lot_ids=fields.One2many('pos.pack.operation.lot','pos_order_line_id',string='Lot/serialNumber')
    product_uom_id=fields.Many2one('uom.uom',string='ProductUoM',related='product_id.uom_id')
    currency_id=fields.Many2one('res.currency',related='order_id.currency_id')
    full_product_name=fields.Char('FullProductName')

    def_prepare_refund_data(self,refund_order,PosOrderLineLot):
        """
        Thispreparesdataforrefundorderline.Inheritancemayinjectmoredatahere

        @paramrefund_order:thepre-createdrefundorder
        @typerefund_order:pos.order

        @paramPosOrderLineLot:thepre-createdPackoperationLot
        @typePosOrderLineLot:pos.pack.operation.lot

        @return:dictionaryofdatawhichisforcreatingarefundorderlinefromtheoriginalline
        @rtype:dict
        """
        self.ensure_one()
        return{
            'name':self.name+_('REFUND'),
            'qty':-self.qty,
            'order_id':refund_order.id,
            'price_subtotal':-self.price_subtotal,
            'price_subtotal_incl':-self.price_subtotal_incl,
            'pack_lot_ids':PosOrderLineLot,
        }

    @api.model
    defcreate(self,values):
        ifvalues.get('order_id')andnotvalues.get('name'):
            #setnamebasedonthesequencespecifiedontheconfig
            config=self.env['pos.order'].browse(values['order_id']).session_id.config_id
            ifconfig.sequence_line_id:
                values['name']=config.sequence_line_id._next()
        ifnotvalues.get('name'):
            #fallbackonanypos.ordersequence
            values['name']=self.env['ir.sequence'].next_by_code('pos.order.line')
        returnsuper(PosOrderLine,self).create(values)

    defwrite(self,values):
        ifvalues.get('pack_lot_line_ids'):
            forplinvalues.get('pack_lot_ids'):
                ifpl[2].get('server_id'):
                    pl[2]['id']=pl[2]['server_id']
                    delpl[2]['server_id']
        returnsuper().write(values)

    @api.onchange('price_unit','tax_ids','qty','discount','product_id')
    def_onchange_amount_line_all(self):
        forlineinself:
            res=line._compute_amount_line_all()
            line.update(res)

    def_compute_amount_line_all(self):
        self.ensure_one()
        fpos=self.order_id.fiscal_position_id
        tax_ids_after_fiscal_position=fpos.map_tax(self.tax_ids,self.product_id,self.order_id.partner_id)
        price=self.price_unit*(1-(self.discountor0.0)/100.0)
        taxes=tax_ids_after_fiscal_position.compute_all(price,self.order_id.pricelist_id.currency_id,self.qty,product=self.product_id,partner=self.order_id.partner_id)
        return{
            'price_subtotal_incl':taxes['total_included'],
            'price_subtotal':taxes['total_excluded'],
        }

    @api.onchange('product_id')
    def_onchange_product_id(self):
        ifself.product_id:
            ifnotself.order_id.pricelist_id:
                raiseUserError(
                    _('Youhavetoselectapricelistinthesaleform!\n'
                      'Pleasesetonebeforechoosingaproduct.'))
            price=self.order_id.pricelist_id.get_product_price(
                self.product_id,self.qtyor1.0,self.order_id.partner_id)
            self._onchange_qty()
            self.tax_ids=self.product_id.taxes_id.filtered(lambdar:notself.company_idorr.company_id==self.company_id)
            tax_ids_after_fiscal_position=self.order_id.fiscal_position_id.map_tax(self.tax_ids,self.product_id,self.order_id.partner_id)
            self.price_unit=self.env['account.tax']._fix_tax_included_price_company(price,self.product_id.taxes_id,tax_ids_after_fiscal_position,self.company_id)

    @api.onchange('qty','discount','price_unit','tax_ids')
    def_onchange_qty(self):
        ifself.product_id:
            ifnotself.order_id.pricelist_id:
                raiseUserError(_('Youhavetoselectapricelistinthesaleform.'))
            price=self.price_unit*(1-(self.discountor0.0)/100.0)
            self.price_subtotal=self.price_subtotal_incl=price*self.qty
            if(self.product_id.taxes_id):
                taxes=self.product_id.taxes_id.compute_all(price,self.order_id.pricelist_id.currency_id,self.qty,product=self.product_id,partner=False)
                self.price_subtotal=taxes['total_excluded']
                self.price_subtotal_incl=taxes['total_included']

    @api.depends('order_id','order_id.fiscal_position_id')
    def_get_tax_ids_after_fiscal_position(self):
        forlineinself:
            line.tax_ids_after_fiscal_position=line.order_id.fiscal_position_id.map_tax(line.tax_ids,line.product_id,line.order_id.partner_id)

    def_export_for_ui(self,orderline):
        return{
            'qty':orderline.qty,
            'price_unit':orderline.price_unit,
            'price_subtotal':orderline.price_subtotal,
            'price_subtotal_incl':orderline.price_subtotal_incl,
            'product_id':orderline.product_id.id,
            'discount':orderline.discount,
            'tax_ids':[[6,False,orderline.tax_ids.mapped(lambdatax:tax.id)]],
            'id':orderline.id,
            'pack_lot_ids':[[0,0,lot]forlotinorderline.pack_lot_ids.export_for_ui()],
        }

    defexport_for_ui(self):
        returnself.mapped(self._export_for_ui)ifselfelse[]


classPosOrderLineLot(models.Model):
    _name="pos.pack.operation.lot"
    _description="Specifyproductlot/serialnumberinposorderline"
    _rec_name="lot_name"

    pos_order_line_id=fields.Many2one('pos.order.line')
    order_id=fields.Many2one('pos.order',related="pos_order_line_id.order_id",readonly=False)
    lot_name=fields.Char('LotName')
    product_id=fields.Many2one('product.product',related='pos_order_line_id.product_id',readonly=False)

    def_export_for_ui(self,lot):
        return{
            'lot_name':lot.lot_name,
        }

    defexport_for_ui(self):
        returnself.mapped(self._export_for_ui)ifselfelse[]

classReportSaleDetails(models.AbstractModel):

    _name='report.point_of_sale.report_saledetails'
    _description='PointofSaleDetails'


    @api.model
    defget_sale_details(self,date_start=False,date_stop=False,config_ids=False,session_ids=False):
        """Serialisetheordersoftherequestedtimeperiod,configsandsessions.

        :paramdate_start:ThedateTimetostart,defaulttoday00:00:00.
        :typedate_start:str.
        :paramdate_stop:ThedateTimetostop,defaultdate_start+23:59:59.
        :typedate_stop:str.
        :paramconfig_ids:PosConfigid'stoinclude.
        :typeconfig_ids:listofnumbers.
        :paramsession_ids:PosConfigid'stoinclude.
        :typesession_ids:listofnumbers.

        :returns:dict--Serialisedsales.
        """
        domain=[('state','in',['paid','invoiced','done'])]

        if(session_ids):
            domain=AND([domain,[('session_id','in',session_ids)]])
        else:
            ifdate_start:
                date_start=fields.Datetime.from_string(date_start)
            else:
                #startbydefaulttoday00:00:00
                user_tz=pytz.timezone(self.env.context.get('tz')orself.env.user.tzor'UTC')
                today=user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
                date_start=today.astimezone(pytz.timezone('UTC'))

            ifdate_stop:
                date_stop=fields.Datetime.from_string(date_stop)
                #avoidadate_stopsmallerthandate_start
                if(date_stop<date_start):
                    date_stop=date_start+timedelta(days=1,seconds=-1)
            else:
                #stopbydefaulttoday23:59:59
                date_stop=date_start+timedelta(days=1,seconds=-1)

            domain=AND([domain,
                [('date_order','>=',fields.Datetime.to_string(date_start)),
                ('date_order','<=',fields.Datetime.to_string(date_stop))]
            ])

            ifconfig_ids:
                domain=AND([domain,[('config_id','in',config_ids)]])

        orders=self.env['pos.order'].search(domain)

        user_currency=self.env.company.currency_id

        total=0.0
        products_sold={}
        taxes={}
        fororderinorders:
            ifuser_currency!=order.pricelist_id.currency_id:
                total+=order.pricelist_id.currency_id._convert(
                    order.amount_total,user_currency,order.company_id,order.date_orderorfields.Date.today())
            else:
                total+=order.amount_total
            currency=order.session_id.currency_id

            forlineinorder.lines:
                key=(line.product_id,line.price_unit,line.discount)
                products_sold.setdefault(key,0.0)
                products_sold[key]+=line.qty

                ifline.tax_ids_after_fiscal_position:
                    line_taxes=line.tax_ids_after_fiscal_position.sudo().compute_all(line.price_unit*(1-(line.discountor0.0)/100.0),currency,line.qty,product=line.product_id,partner=line.order_id.partner_idorFalse)
                    fortaxinline_taxes['taxes']:
                        taxes.setdefault(tax['id'],{'name':tax['name'],'tax_amount':0.0,'base_amount':0.0})
                        taxes[tax['id']]['tax_amount']+=tax['amount']
                        taxes[tax['id']]['base_amount']+=tax['base']
                else:
                    taxes.setdefault(0,{'name':_('NoTaxes'),'tax_amount':0.0,'base_amount':0.0})
                    taxes[0]['base_amount']+=line.price_subtotal_incl

        payment_ids=self.env["pos.payment"].search([('pos_order_id','in',orders.ids)]).ids
        ifpayment_ids:
            self.env.cr.execute("""
                SELECTmethod.name,sum(amount)total
                FROMpos_paymentASpayment,
                     pos_payment_methodASmethod
                WHEREpayment.payment_method_id=method.id
                    ANDpayment.idIN%s
                GROUPBYmethod.name
            """,(tuple(payment_ids),))
            payments=self.env.cr.dictfetchall()
        else:
            payments=[]

        return{
            'currency_precision':user_currency.decimal_places,
            'total_paid':user_currency.round(total),
            'payments':payments,
            'company_name':self.env.company.name,
            'taxes':list(taxes.values()),
            'products':sorted([{
                'product_id':product.id,
                'product_name':product.name,
                'code':product.default_code,
                'quantity':qty,
                'price_unit':price_unit,
                'discount':discount,
                'uom':product.uom_id.name
            }for(product,price_unit,discount),qtyinproducts_sold.items()],key=lambdal:l['product_name'])
        }

    @api.model
    def_get_report_values(self,docids,data=None):
        data=dict(dataor{})
        configs=self.env['pos.config'].browse(data['config_ids'])
        data.update(self.get_sale_details(data['date_start'],data['date_stop'],configs.ids))
        returndata

classAccountCashRounding(models.Model):
    _inherit='account.cash.rounding'

    @api.constrains('rounding','rounding_method','strategy')
    def_check_session_state(self):
        open_session=self.env['pos.session'].search([('config_id.rounding_method','=',self.id),('state','!=','closed')])
        ifopen_session:
            raiseValidationError(
                _("Youarenotallowedtochangethecashroundingconfigurationwhileapossessionusingitisalreadyopened."))
