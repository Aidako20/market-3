#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
fromfunctoolsimportpartial
fromitertoolsimportgroupby

fromflectraimportapi,fields,models,SUPERUSER_ID,_
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.tools.miscimportformatLang,get_lang
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_is_zero,float_compare



fromwerkzeug.urlsimporturl_encode


classSaleOrder(models.Model):
    _name="sale.order"
    _inherit=['portal.mixin','mail.thread','mail.activity.mixin','utm.mixin']
    _description="SalesOrder"
    _order='date_orderdesc,iddesc'
    _check_company_auto=True

    def_default_validity_date(self):
        ifself.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):
            days=self.env.company.quotation_validity_days
            ifdays>0:
                returnfields.Date.to_string(datetime.now()+timedelta(days))
        returnFalse

    def_get_default_require_signature(self):
        returnself.env.company.portal_confirmation_sign

    def_get_default_require_payment(self):
        returnself.env.company.portal_confirmation_pay

    @api.depends('order_line.price_total')
    def_amount_all(self):
        """
        ComputethetotalamountsoftheSO.
        """
        fororderinself:
            amount_untaxed=amount_tax=0.0
            forlineinorder.order_line:
                amount_untaxed+=line.price_subtotal
                amount_tax+=line.price_tax
            order.update({
                'amount_untaxed':amount_untaxed,
                'amount_tax':amount_tax,
                'amount_total':amount_untaxed+amount_tax,
            })

    @api.depends('order_line.invoice_lines')
    def_get_invoiced(self):
        #Theinvoice_idsareobtainedthankstotheinvoicelinesoftheSO
        #lines,andwealsosearchforpossiblerefundscreateddirectlyfrom
        #existinginvoices.Thisisnecessarysincesucharefundisnot
        #directlylinkedtotheSO.
        fororderinself:
            invoices=order.order_line.invoice_lines.move_id.filtered(lambdar:r.move_typein('out_invoice','out_refund'))
            order.invoice_ids=invoices
            order.invoice_count=len(invoices)

    @api.depends('state','order_line.invoice_status')
    def_get_invoice_status(self):
        """
        ComputetheinvoicestatusofaSO.Possiblestatuses:
        -no:iftheSOisnotinstatus'sale'or'done',weconsiderthatthereisnothingto
          invoice.Thisisalsothedefaultvalueiftheconditionsofnootherstatusismet.
        -toinvoice:ifanySOlineis'toinvoice',thewholeSOis'toinvoice'
        -invoiced:ifallSOlinesareinvoiced,theSOisinvoiced.
        -upselling:ifallSOlinesareinvoicedorupselling,thestatusisupselling.
        """
        unconfirmed_orders=self.filtered(lambdaso:so.statenotin['sale','done'])
        unconfirmed_orders.invoice_status='no'
        confirmed_orders=self-unconfirmed_orders
        ifnotconfirmed_orders:
            return
        line_invoice_status_all=[
            (d['order_id'][0],d['invoice_status'])
            fordinself.env['sale.order.line'].read_group([
                    ('order_id','in',confirmed_orders.ids),
                    ('is_downpayment','=',False),
                    ('display_type','=',False),
                ],
                ['order_id','invoice_status'],
                ['order_id','invoice_status'],lazy=False)]
        fororderinconfirmed_orders:
            line_invoice_status=[d[1]fordinline_invoice_status_allifd[0]==order.id]
            iforder.statenotin('sale','done'):
                order.invoice_status='no'
            elifany(invoice_status=='toinvoice'forinvoice_statusinline_invoice_status):
                order.invoice_status='toinvoice'
            elifline_invoice_statusandall(invoice_status=='invoiced'forinvoice_statusinline_invoice_status):
                order.invoice_status='invoiced'
            elifline_invoice_statusandall(invoice_statusin('invoiced','upselling')forinvoice_statusinline_invoice_status):
                order.invoice_status='upselling'
            else:
                order.invoice_status='no'

    @api.model
    defget_empty_list_help(self,help):
        self=self.with_context(
            empty_list_help_document_name=_("saleorder"),
        )
        returnsuper(SaleOrder,self).get_empty_list_help(help)

    @api.model
    def_default_note(self):
        returnself.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')andself.env.company.invoice_termsor''

    @api.model
    def_get_default_team(self):
        returnself.env['crm.team']._get_default_team_id()

    @api.onchange('fiscal_position_id')
    def_compute_tax_id(self):
        """
        TriggertherecomputeofthetaxesifthefiscalpositionischangedontheSO.
        """
        fororderinself:
            order.order_line._compute_tax_id()

    def_search_invoice_ids(self,operator,value):
        ifoperator=='in'andvalue:
            self.env.cr.execute("""
                SELECTarray_agg(so.id)
                    FROMsale_orderso
                    JOINsale_order_linesolONsol.order_id=so.id
                    JOINsale_order_line_invoice_relsoli_relONsoli_rel.order_line_id=sol.id
                    JOINaccount_move_lineamlONaml.id=soli_rel.invoice_line_id
                    JOINaccount_moveamONam.id=aml.move_id
                WHERE
                    am.move_typein('out_invoice','out_refund')AND
                    am.id=ANY(%s)
            """,(list(value),))
            so_ids=self.env.cr.fetchone()[0]or[]
            return[('id','in',so_ids)]
        elifoperator=='='andnotvalue:
            #specialcasefor[('invoice_ids','=',False)],i.e."Invoicesisnotset"
            #
            #Wecannotjustsearch[('order_line.invoice_lines','=',False)]
            #becauseitreturnsorderswithuninvoicedlines,whichisnot
            #same"Invoicesisnotset"(somelinesmayhaveinvoicesandsome
            #doesn't)
            #
            #Asolutionismakinginvertedsearchfirst("orderswithinvoiced
            #lines")andtheninvertresults("getallotherorders")
            #
            #Domainbelowreturnssubsetof('order_line.invoice_lines','!=',False)
            order_ids=self._search([
                ('order_line.invoice_lines.move_id.move_type','in',('out_invoice','out_refund'))
            ])
            return[('id','notin',order_ids)]
        return['&',('order_line.invoice_lines.move_id.move_type','in',('out_invoice','out_refund')),('order_line.invoice_lines.move_id',operator,value)]

    name=fields.Char(string='OrderReference',required=True,copy=False,readonly=True,states={'draft':[('readonly',False)]},index=True,default=lambdaself:_('New'))
    origin=fields.Char(string='SourceDocument',help="Referenceofthedocumentthatgeneratedthissalesorderrequest.")
    client_order_ref=fields.Char(string='CustomerReference',copy=False)
    reference=fields.Char(string='PaymentRef.',copy=False,
        help='Thepaymentcommunicationofthissaleorder.')
    state=fields.Selection([
        ('draft','Quotation'),
        ('sent','QuotationSent'),
        ('sale','SalesOrder'),
        ('done','Locked'),
        ('cancel','Cancelled'),
        ],string='Status',readonly=True,copy=False,index=True,tracking=3,default='draft')
    date_order=fields.Datetime(string='OrderDate',required=True,readonly=True,index=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]},copy=False,default=fields.Datetime.now,help="Creationdateofdraft/sentorders,\nConfirmationdateofconfirmedorders.")
    validity_date=fields.Date(string='Expiration',readonly=True,copy=False,states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
                                default=_default_validity_date)
    is_expired=fields.Boolean(compute='_compute_is_expired',string="Isexpired")
    require_signature=fields.Boolean('OnlineSignature',default=_get_default_require_signature,readonly=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        help='Requestaonlinesignaturetothecustomerinordertoconfirmordersautomatically.')
    require_payment=fields.Boolean('OnlinePayment',default=_get_default_require_payment,readonly=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        help='Requestanonlinepaymenttothecustomerinordertoconfirmordersautomatically.')
    create_date=fields.Datetime(string='CreationDate',readonly=True,index=True,help="Dateonwhichsalesorderiscreated.")

    user_id=fields.Many2one(
        'res.users',string='Salesperson',index=True,tracking=2,default=lambdaself:self.env.user,
        domain=lambdaself:"[('groups_id','=',{}),('share','=',False),('company_ids','=',company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)

    partner_id=fields.Many2one(
        'res.partner',string='Customer',readonly=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        required=True,change_default=True,index=True,tracking=1,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",)
    partner_invoice_id=fields.Many2one(
        'res.partner',string='InvoiceAddress',
        readonly=True,required=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)],'sale':[('readonly',False)]},
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",)
    partner_shipping_id=fields.Many2one(
        'res.partner',string='DeliveryAddress',readonly=True,required=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)],'sale':[('readonly',False)]},
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",)

    pricelist_id=fields.Many2one(
        'product.pricelist',string='Pricelist',check_company=True, #Unrequiredcompany
        required=True,readonly=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",tracking=1,
        help="Ifyouchangethepricelist,onlynewlyaddedlineswillbeaffected.")
    currency_id=fields.Many2one(related='pricelist_id.currency_id',depends=["pricelist_id"],store=True)
    analytic_account_id=fields.Many2one(
        'account.analytic.account','AnalyticAccount',
        compute='_compute_analytic_account_id',store=True,
        readonly=False,copy=False,check_company=True, #Unrequiredcompany
        states={'sale':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]},
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",
        help="Theanalyticaccountrelatedtoasalesorder.")

    order_line=fields.One2many('sale.order.line','order_id',string='OrderLines',states={'cancel':[('readonly',True)],'done':[('readonly',True)]},copy=True,auto_join=True)

    invoice_count=fields.Integer(string='InvoiceCount',compute='_get_invoiced',readonly=True)
    invoice_ids=fields.Many2many("account.move",string='Invoices',compute="_get_invoiced",readonly=True,copy=False,search="_search_invoice_ids")
    invoice_status=fields.Selection([
        ('upselling','UpsellingOpportunity'),
        ('invoiced','FullyInvoiced'),
        ('toinvoice','ToInvoice'),
        ('no','NothingtoInvoice')
        ],string='InvoiceStatus',compute='_get_invoice_status',store=True,readonly=True)

    note=fields.Text('Termsandconditions',default=_default_note)

    amount_untaxed=fields.Monetary(string='UntaxedAmount',store=True,readonly=True,compute='_amount_all',tracking=5)
    amount_by_group=fields.Binary(string="Taxamountbygroup",compute='_amount_by_group',help="type:[(name,amount,base,formatedamount,formatedbase)]")
    amount_tax=fields.Monetary(string='Taxes',store=True,readonly=True,compute='_amount_all')
    amount_total=fields.Monetary(string='Total',store=True,readonly=True,compute='_amount_all',tracking=4)
    currency_rate=fields.Float("CurrencyRate",compute='_compute_currency_rate',compute_sudo=True,store=True,digits=(12,6),readonly=True,help='Therateofthecurrencytothecurrencyofrate1applicableatthedateoftheorder')

    payment_term_id=fields.Many2one(
        'account.payment.term',string='PaymentTerms',check_company=True, #Unrequiredcompany
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",)
    fiscal_position_id=fields.Many2one(
        'account.fiscal.position',string='FiscalPosition',
        domain="[('company_id','=',company_id)]",check_company=True,
        help="Fiscalpositionsareusedtoadapttaxesandaccountsforparticularcustomersorsalesorders/invoices."
        "Thedefaultvaluecomesfromthecustomer.")
    company_id=fields.Many2one('res.company','Company',required=True,index=True,default=lambdaself:self.env.company)
    team_id=fields.Many2one(
        'crm.team','SalesTeam',
        change_default=True,default=_get_default_team,check_company=True, #Unrequiredcompany
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")

    signature=fields.Image('Signature',help='Signaturereceivedthroughtheportal.',copy=False,attachment=True,max_width=1024,max_height=1024)
    signed_by=fields.Char('SignedBy',help='NameofthepersonthatsignedtheSO.',copy=False)
    signed_on=fields.Datetime('SignedOn',help='Dateofthesignature.',copy=False)

    commitment_date=fields.Datetime('DeliveryDate',copy=False,
                                      states={'done':[('readonly',True)],'cancel':[('readonly',True)]},
                                      help="Thisisthedeliverydatepromisedtothecustomer."
                                           "Ifset,thedeliveryorderwillbescheduledbasedon"
                                           "thisdateratherthanproductleadtimes.")
    expected_date=fields.Datetime("ExpectedDate",compute='_compute_expected_date',store=False, #Note:cannotbestoredsincedependsontoday()
        help="Deliverydateyoucanpromisetothecustomer,computedfromtheminimumleadtimeoftheorderlines.")
    amount_undiscounted=fields.Float('AmountBeforeDiscount',compute='_compute_amount_undiscounted',digits=0)

    type_name=fields.Char('TypeName',compute='_compute_type_name')

    transaction_ids=fields.Many2many('payment.transaction','sale_order_transaction_rel','sale_order_id','transaction_id',
                                       string='Transactions',copy=False,readonly=True)
    authorized_transaction_ids=fields.Many2many('payment.transaction',compute='_compute_authorized_transaction_ids',
                                                  string='AuthorizedTransactions',copy=False,readonly=True)
    show_update_pricelist=fields.Boolean(string='HasPricelistChanged',
                                           help="TechnicalField,Trueifthepricelistwaschanged;\n"
                                                "thiswillthendisplayarecomputationbutton")
    tag_ids=fields.Many2many('crm.tag','sale_order_tag_rel','order_id','tag_id',string='Tags')

    _sql_constraints=[
        ('date_order_conditional_required',"CHECK((stateIN('sale','done')ANDdate_orderISNOTNULL)ORstateNOTIN('sale','done'))","Aconfirmedsalesorderrequiresaconfirmationdate."),
    ]

    @api.constrains('company_id','order_line')
    def_check_order_line_company_id(self):
        fororderinself:
            companies=order.order_line.product_id.company_id
            ifcompaniesandcompanies!=order.company_id:
                bad_products=order.order_line.product_id.filtered(lambdap:p.company_idandp.company_id!=order.company_id)
                raiseValidationError(_(
                    "Yourquotationcontainsproductsfromcompany%(product_company)swhereasyourquotationbelongstocompany%(quote_company)s.\nPleasechangethecompanyofyourquotationorremovetheproductsfromothercompanies(%(bad_products)s).",
                    product_company=','.join(companies.mapped('display_name')),
                    quote_company=order.company_id.display_name,
                    bad_products=','.join(bad_products.mapped('display_name')),
                ))

    @api.depends('pricelist_id','date_order','company_id')
    def_compute_currency_rate(self):
        fororderinself:
            ifnotorder.company_id:
                order.currency_rate=order.currency_id.with_context(date=order.date_order).rateor1.0
                continue
            eliforder.company_id.currency_idandorder.currency_id: #thefollowingcrashesifanyoneisundefined
                order.currency_rate=self.env['res.currency']._get_conversion_rate(order.company_id.currency_id,order.currency_id,order.company_id,order.date_order)
            else:
                order.currency_rate=1.0

    def_compute_access_url(self):
        super(SaleOrder,self)._compute_access_url()
        fororderinself:
            order.access_url='/my/orders/%s'%(order.id)

    def_compute_is_expired(self):
        today=fields.Date.today()
        fororderinself:
            order.is_expired=order.state=='sent'andorder.validity_dateandorder.validity_date<today

    @api.depends('order_line.customer_lead','date_order','order_line.state')
    def_compute_expected_date(self):
        """Forserviceandconsumable,weonlytakethemindates.Thismethodisextendedinsale_stockto
            takethepicking_policyofSOintoaccount.
        """
        self.mapped("order_line") #Prefetchindication
        fororderinself:
            dates_list=[]
            forlineinorder.order_line.filtered(lambdax:x.state!='cancel'andnotx._is_delivery()andnotx.display_type):
                dt=line._expected_date()
                dates_list.append(dt)
            ifdates_list:
                order.expected_date=fields.Datetime.to_string(min(dates_list))
            else:
                order.expected_date=False

    @api.depends('partner_id','date_order')
    def_compute_analytic_account_id(self):
        fororderinself:
            ifnotorder.analytic_account_id:
                default_analytic_account=order.env['account.analytic.default'].sudo().account_get(
                    partner_id=order.partner_id.id,
                    user_id=order.env.uid,
                    date=order.date_order,
                    company_id=order.company_id.id,
                )
                order.analytic_account_id=default_analytic_account.analytic_id

    @api.onchange('expected_date')
    def_onchange_commitment_date(self):
        self.commitment_date=self.expected_date

    @api.depends('transaction_ids')
    def_compute_authorized_transaction_ids(self):
        fortransinself:
            trans.authorized_transaction_ids=trans.transaction_ids.filtered(lambdat:t.state=='authorized')

    def_compute_amount_undiscounted(self):
        fororderinself:
            total=0.0
            forlineinorder.order_line:
                total+=(line.price_subtotal*100)/(100-line.discount)ifline.discount!=100else(line.price_unit*line.product_uom_qty)
            order.amount_undiscounted=total

    @api.depends('state')
    def_compute_type_name(self):
        forrecordinself:
            record.type_name=_('Quotation')ifrecord.statein('draft','sent','cancel')else_('SalesOrder')

    defunlink(self):
        fororderinself:
            iforder.statenotin('draft','cancel'):
                raiseUserError(_('Youcannotdeleteasentquotationoraconfirmedsalesorder.Youmustfirstcancelit.'))
        returnsuper(SaleOrder,self).unlink()

    defvalidate_taxes_on_sales_order(self):
        #Overrideforcorrecttaxcloudcomputation
        #whenusingcouponanddelivery
        returnTrue

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'state'ininit_valuesandself.state=='sale':
            returnself.env.ref('sale.mt_order_confirmed')
        elif'state'ininit_valuesandself.state=='sent':
            returnself.env.ref('sale.mt_order_sent')
        returnsuper(SaleOrder,self)._track_subtype(init_values)

    @api.onchange('partner_shipping_id','partner_id','company_id')
    defonchange_partner_shipping_id(self):
        """
        Triggerthechangeoffiscalpositionwhentheshippingaddressismodified.
        """
        self.fiscal_position_id=self.env['account.fiscal.position'].with_company(self.company_id).get_fiscal_position(self.partner_id.id,self.partner_shipping_id.id)
        return{}

    @api.onchange('partner_id')
    defonchange_partner_id(self):
        """
        Updatethefollowingfieldswhenthepartnerischanged:
        -Pricelist
        -Paymentterms
        -Invoiceaddress
        -Deliveryaddress
        -SalesTeam
        """
        ifnotself.partner_id:
            self.update({
                'partner_invoice_id':False,
                'partner_shipping_id':False,
                'fiscal_position_id':False,
            })
            return

        self=self.with_company(self.company_id)

        addr=self.partner_id.address_get(['delivery','invoice'])
        partner_user=self.partner_id.user_idorself.partner_id.commercial_partner_id.user_id
        values={
            'pricelist_id':self.partner_id.property_product_pricelistandself.partner_id.property_product_pricelist.idorFalse,
            'payment_term_id':self.partner_id.property_payment_term_idandself.partner_id.property_payment_term_id.idorFalse,
            'partner_invoice_id':addr['invoice'],
            'partner_shipping_id':addr['delivery'],
        }
        user_id=partner_user.id
        ifnotself.env.context.get('not_self_saleperson'):
            user_id=user_idorself.env.context.get('default_user_id',self.env.uid)
        ifuser_idandself.user_id.id!=user_id:
            values['user_id']=user_id

        ifself.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')andself.env.company.invoice_terms:
            values['note']=self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        ifnotself.env.context.get('not_self_saleperson')ornotself.team_id:
            values['team_id']=self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|',('company_id','=',self.company_id.id),('company_id','=',False)],user_id=user_id)
        self.update(values)

    @api.onchange('user_id')
    defonchange_user_id(self):
        ifself.user_id:
            self.team_id=self.env['crm.team'].with_context(
                default_team_id=self.team_id.id
            )._get_default_team_id(user_id=self.user_id.id)

    @api.onchange('partner_id')
    defonchange_partner_id_warning(self):
        ifnotself.partner_id:
            return
        warning={}
        title=False
        message=False
        partner=self.partner_id

        #Ifpartnerhasnowarning,checkitscompany
        ifpartner.sale_warn=='no-message'andpartner.parent_id:
            partner=partner.parent_id

        ifpartner.sale_warnandpartner.sale_warn!='no-message':
            #Blockifpartneronlyhaswarningbutparentcompanyisblocked
            ifpartner.sale_warn!='block'andpartner.parent_idandpartner.parent_id.sale_warn=='block':
                partner=partner.parent_id
            title=_("Warningfor%s")%partner.name
            message=partner.sale_warn_msg
            warning={
                    'title':title,
                    'message':message,
            }
            ifpartner.sale_warn=='block':
                self.update({'partner_id':False,'partner_invoice_id':False,'partner_shipping_id':False,'pricelist_id':False})
                return{'warning':warning}

        ifwarning:
            return{'warning':warning}

    @api.onchange('commitment_date')
    def_onchange_commitment_date(self):
        """Warnifthecommitmentdatesissoonerthantheexpecteddate"""
        if(self.commitment_dateandself.expected_dateandself.commitment_date<self.expected_date):
            return{
                'warning':{
                    'title':_('Requesteddateistoosoon.'),
                    'message':_("Thedeliverydateissoonerthantheexpecteddate."
                                 "Youmaybeunabletohonorthedeliverydate.")
                }
            }

    @api.onchange('pricelist_id','order_line')
    def_onchange_pricelist_id(self):
        ifself.order_lineandself.pricelist_idandself._origin.pricelist_id!=self.pricelist_id:
            self.show_update_pricelist=True
        else:
            self.show_update_pricelist=False

    def_get_update_prices_lines(self):
        """Hooktoexcludespecificlineswhichshouldnotbeupdatedbasedonpricelistrecomputation"""
        returnself.order_line.filtered(lambdaline:notline.display_type)

    defupdate_prices(self):
        self.ensure_one()
        forlineinself._get_update_prices_lines():
            line.product_uom_change()
            line.discount=0 #Force0asdiscountforthecaseswhen_onchange_discountdirectlyreturns
            line._onchange_discount()
        self.show_update_pricelist=False
        self.message_post(body=_("Productpriceshavebeenrecomputedaccordingtopricelist<b>%s<b>",self.pricelist_id.display_name))

    @api.model
    defcreate(self,vals):
        if'company_id'invals:
            self=self.with_company(vals['company_id'])
        ifvals.get('name',_('New'))==_('New'):
            seq_date=None
            if'date_order'invals:
                seq_date=fields.Datetime.context_timestamp(self,fields.Datetime.to_datetime(vals['date_order']))
            vals['name']=self.env['ir.sequence'].next_by_code('sale.order',sequence_date=seq_date)or_('New')

        #Makessurepartner_invoice_id','partner_shipping_id'and'pricelist_id'aredefined
        ifany(fnotinvalsforfin['partner_invoice_id','partner_shipping_id','pricelist_id']):
            partner=self.env['res.partner'].browse(vals.get('partner_id'))
            addr=partner.address_get(['delivery','invoice'])
            vals['partner_invoice_id']=vals.setdefault('partner_invoice_id',addr['invoice'])
            vals['partner_shipping_id']=vals.setdefault('partner_shipping_id',addr['delivery'])
            vals['pricelist_id']=vals.setdefault('pricelist_id',partner.property_product_pricelist.id)
        result=super(SaleOrder,self).create(vals)
        returnresult

    def_compute_field_value(self,field):
        iffield.name=='invoice_status'andnotself.env.context.get('mail_activity_automation_skip'):
            filtered_self=self.filtered(lambdaso:so.user_idandso._origin.invoice_status!='upselling')
        super()._compute_field_value(field)
        iffield.name!='invoice_status'orself.env.context.get('mail_activity_automation_skip'):
            return

        filtered_self=filtered_self.filtered(lambdaso:so.invoice_status=='upselling')
        ifnotfiltered_self:
            return

        filtered_self.activity_unlink(['sale.mail_act_sale_upsell'])
        fororderinfiltered_self:
            order.activity_schedule(
                'sale.mail_act_sale_upsell',
                user_id=order.user_id.id,
                note=_("Upsell<ahref='#'data-oe-model='%s'data-oe-id='%d'>%s</a>forcustomer<ahref='#'data-oe-model='%s'data-oe-id='%s'>%s</a>")%(
                         order._name,order.id,order.name,
                         order.partner_id._name,order.partner_id.id,order.partner_id.display_name))

    defcopy_data(self,default=None):
        ifdefaultisNone:
            default={}
        if'order_line'notindefault:
            default['order_line']=[(0,0,line.copy_data()[0])forlineinself.order_line.filtered(lambdal:notl.is_downpayment)]
        returnsuper(SaleOrder,self).copy_data(default)

    defname_get(self):
        ifself._context.get('sale_show_partner_name'):
            res=[]
            fororderinself:
                name=order.name
                iforder.partner_id.name:
                    name='%s-%s'%(name,order.partner_id.name)
                res.append((order.id,name))
            returnres
        returnsuper(SaleOrder,self).name_get()

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        ifself._context.get('sale_show_partner_name'):
            ifoperator=='ilike'andnot(nameor'').strip():
                domain=[]
            elifoperatorin('ilike','like','=','=like','=ilike'):
                domain=expression.AND([
                    argsor[],
                    ['|',('name',operator,name),('partner_id.name',operator,name)]
                ])
                returnself._search(domain,limit=limit,access_rights_uid=name_get_uid)
        returnsuper(SaleOrder,self)._name_search(name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    def_prepare_invoice(self):
        """
        Preparethedictofvaluestocreatethenewinvoiceforasalesorder.Thismethodmaybe
        overriddentoimplementcustominvoicegeneration(makingsuretocallsuper()toestablish
        acleanextensionchain).
        """
        self.ensure_one()
        journal=self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        ifnotjournal:
            raiseUserError(_('Pleasedefineanaccountingsalesjournalforthecompany%s(%s).')%(self.company_id.name,self.company_id.id))

        invoice_vals={
            'ref':self.client_order_refor'',
            'move_type':'out_invoice',
            'narration':self.note,
            'currency_id':self.pricelist_id.currency_id.id,
            'campaign_id':self.campaign_id.id,
            'medium_id':self.medium_id.id,
            'source_id':self.source_id.id,
            'user_id':self.user_id.id,
            'invoice_user_id':self.user_id.id,
            'team_id':self.team_id.id,
            'partner_id':self.partner_invoice_id.id,
            'partner_shipping_id':self.partner_shipping_id.id,
            'fiscal_position_id':(self.fiscal_position_idorself.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id':self.company_id.partner_id.bank_ids.filtered(lambdabank:bank.company_id.idin(self.company_id.id,False))[:1].id,
            'journal_id':journal.id, #companycomesfromthejournal
            'invoice_origin':self.name,
            'invoice_payment_term_id':self.payment_term_id.id,
            'payment_reference':self.reference,
            'transaction_ids':[(6,0,self.transaction_ids.ids)],
            'invoice_line_ids':[],
            'company_id':self.company_id.id,
        }
        returninvoice_vals

    defaction_quotation_sent(self):
        ifself.filtered(lambdaso:so.state!='draft'):
            raiseUserError(_('Onlydraftorderscanbemarkedassentdirectly.'))
        fororderinself:
            order.message_subscribe(partner_ids=order.partner_id.ids)
        self.write({'state':'sent'})

    defaction_view_invoice(self):
        invoices=self.mapped('invoice_ids')
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        iflen(invoices)>1:
            action['domain']=[('id','in',invoices.ids)]
        eliflen(invoices)==1:
            form_view=[(self.env.ref('account.view_move_form').id,'form')]
            if'views'inaction:
                action['views']=form_view+[(state,view)forstate,viewinaction['views']ifview!='form']
            else:
                action['views']=form_view
            action['res_id']=invoices.id
        else:
            action={'type':'ir.actions.act_window_close'}

        context={
            'default_move_type':'out_invoice',
        }
        iflen(self)==1:
            context.update({
                'default_partner_id':self.partner_id.id,
                'default_partner_shipping_id':self.partner_shipping_id.id,
                'default_invoice_payment_term_id':self.payment_term_id.idorself.partner_id.property_payment_term_id.idorself.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin':self.name,
            })
        action['context']=context
        returnaction

    def_get_invoice_grouping_keys(self):
        return['company_id','partner_id','currency_id']

    @api.model
    def_nothing_to_invoice_error(self):
        msg=_("""Thereisnothingtoinvoice!\n
Reason(s)ofthisbehaviorcouldbe:
-Youshoulddeliveryourproductsbeforeinvoicingthem.
-Youshouldmodifytheinvoicingpolicyofyourproduct:Opentheproduct,gotothe"Salestab"andmodifyinvoicingpolicyfrom"deliveredquantities"to"orderedquantities".
        """)
        returnUserError(msg)

    def_get_invoiceable_lines(self,final=False):
        """Returntheinvoiceablelinesfororder`self`."""
        down_payment_line_ids=[]
        invoiceable_line_ids=[]
        pending_section=None
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')

        forlineinself.order_line:
            ifline.display_type=='line_section':
                #Onlyinvoicethesectionifoneofitslinesisinvoiceable
                pending_section=line
                continue
            ifline.display_type!='line_note'andfloat_is_zero(line.qty_to_invoice,precision_digits=precision):
                continue
            ifline.qty_to_invoice>0or(line.qty_to_invoice<0andfinal)orline.display_type=='line_note':
                ifline.is_downpayment:
                    #Keepdownpaymentlinesseparately,toputthemtogether
                    #attheendoftheinvoice,inaspecificdedicatedsection.
                    down_payment_line_ids.append(line.id)
                    continue
                ifpending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section=None
                invoiceable_line_ids.append(line.id)

        returnself.env['sale.order.line'].browse(invoiceable_line_ids+down_payment_line_ids)

    def_create_invoices(self,grouped=False,final=False,date=None):
        """
        CreatetheinvoiceassociatedtotheSO.
        :paramgrouped:ifTrue,invoicesaregroupedbySOid.IfFalse,invoicesaregroupedby
                        (partner_invoice_id,currency)
        :paramfinal:ifTrue,refundswillbegeneratedifnecessary
        :returns:listofcreatedinvoices
        """
        ifnotself.env['account.move'].check_access_rights('create',False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            exceptAccessError:
                returnself.env['account.move']

        #1)Createinvoices.
        invoice_vals_list=[]
        invoice_item_sequence=0#Incrementalsequencingtokeepthelinesorderontheinvoice.
        fororderinself:
            order=order.with_company(order.company_id)
            current_section_vals=None
            down_payments=order.env['sale.order.line']

            invoice_vals=order._prepare_invoice()
            invoiceable_lines=order._get_invoiceable_lines(final)

            ifnotany(notline.display_typeforlineininvoiceable_lines):
                continue

            invoice_line_vals=[]
            down_payment_section_added=False
            forlineininvoiceable_lines:
                ifnotdown_payment_section_addedandline.is_downpayment:
                    #Createadedicatedsectionforthedownpayments
                    #(putattheendoftheinvoiceable_lines)
                    invoice_line_vals.append(
                        (0,0,order._prepare_down_payment_section_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    down_payment_section_added=True
                    invoice_item_sequence+=1
                invoice_line_vals.append(
                    (0,0,line._prepare_invoice_line(
                        sequence=invoice_item_sequence,
                    )),
                )
                invoice_item_sequence+=1

            invoice_vals['invoice_line_ids']+=invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        ifnotinvoice_vals_list:
            raiseself._nothing_to_invoice_error()

        #2)Manage'grouped'parameter:groupby(partner_id,currency_id).
        ifnotgrouped:
            new_invoice_vals_list=[]
            invoice_grouping_keys=self._get_invoice_grouping_keys()
            invoice_vals_list=sorted(invoice_vals_list,key=lambdax:[x.get(grouping_key)forgrouping_keyininvoice_grouping_keys])
            forgrouping_keys,invoicesingroupby(invoice_vals_list,key=lambdax:[x.get(grouping_key)forgrouping_keyininvoice_grouping_keys]):
                origins=set()
                payment_refs=set()
                refs=set()
                ref_invoice_vals=None
                forinvoice_valsininvoices:
                    ifnotref_invoice_vals:
                        ref_invoice_vals=invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids']+=invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref':','.join(refs)[:2000],
                    'invoice_origin':','.join(origins),
                    'payment_reference':len(payment_refs)==1andpayment_refs.pop()orFalse,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list=new_invoice_vals_list

        #3)Createinvoices.

        #Aspartoftheinvoicecreation,wemakesurethesequenceofmultipleSOdonotinterfere
        #inasingleinvoice.Example:
        #SO1:
        #-SectionA(sequence:10)
        #-ProductA(sequence:11)
        #SO2:
        #-SectionB(sequence:10)
        #-ProductB(sequence:11)
        #
        #IfSO1&2aregroupedinthesameinvoice,theresultwillbe:
        #-SectionA(sequence:10)
        #-SectionB(sequence:10)
        #-ProductA(sequence:11)
        #-ProductB(sequence:11)
        #
        #Resequencingshouldbesafe,howeverweresequenceonlyiftherearelessinvoicesthan
        #orders,meaningagroupingmighthavebeendone.Thiscouldalsomeanthatonlyapart
        #oftheselectedSOareinvoiceable,butresequencinginthiscaseshouldn'tbeanissue.
        iflen(invoice_vals_list)<len(self):
            SaleOrderLine=self.env['sale.order.line']
            forinvoiceininvoice_vals_list:
                sequence=1
                forlineininvoice['invoice_line_ids']:
                    line[2]['sequence']=SaleOrderLine._get_invoice_line_sequence(new=sequence,old=line[2]['sequence'])
                    sequence+=1

        #Managethecreationofinvoicesinsudobecauseasalespersonmustbeabletogenerateaninvoicefroma
        #saleorderwithout"billing"accessrights.However,heshouldnotbeabletocreateaninvoicefromscratch.
        moves=self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        #4)Somemovesmightactuallyberefunds:convertthemifthetotalamountisnegative
        #Wedothisafterthemoveshavebeencreatedsinceweneedtaxes,etc.toknowifthetotal
        #isactuallynegativeornot
        iffinal:
            moves.sudo().filtered(lambdam:m.amount_total<0).action_switch_invoice_into_refund_credit_note()
        formoveinmoves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self':move,'origin':move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        returnmoves

    defaction_draft(self):
        orders=self.filtered(lambdas:s.statein['cancel','sent'])
        returnorders.write({
            'state':'draft',
            'signature':False,
            'signed_by':False,
            'signed_on':False,
        })

    defaction_cancel(self):
        cancel_warning=self._show_cancel_wizard()
        ifcancel_warning:
            return{
                'name':_('CancelSalesOrder'),
                'view_mode':'form',
                'res_model':'sale.order.cancel',
                'view_id':self.env.ref('sale.sale_order_cancel_view_form').id,
                'type':'ir.actions.act_window',
                'context':{'default_order_id':self.id},
                'target':'new'
            }
        returnself._action_cancel()

    def_action_cancel(self):
        inv=self.invoice_ids.filtered(lambdainv:inv.state=='draft')
        inv.button_cancel()
        returnself.write({'state':'cancel'})

    def_show_cancel_wizard(self):
        fororderinself:
            iforder.invoice_ids.filtered(lambdainv:inv.state=='draft')andnotorder._context.get('disable_cancel_warning'):
                returnTrue
        returnFalse

    def_find_mail_template(self,force_confirmation_template=False):
        self.ensure_one()
        template_id=False

        ifforce_confirmation_templateor(self.state=='sale'andnotself.env.context.get('proforma',False)):
            template_id=int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
            template_id=self.env['mail.template'].search([('id','=',template_id)]).id
            ifnottemplate_id:
                template_id=self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation',raise_if_not_found=False)
        ifnottemplate_id:
            template_id=self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale',raise_if_not_found=False)

        returntemplate_id

    defaction_quotation_send(self):
        '''Opensawizardtocomposeanemail,withrelevantmailtemplateloadedbydefault'''
        self.ensure_one()
        template_id=self._find_mail_template()
        lang=self.env.context.get('lang')
        template=self.env['mail.template'].browse(template_id)
        iftemplate.lang:
            lang=template._render_lang(self.ids)[self.id]
        ctx={
            'default_model':'sale.order',
            'default_res_id':self.ids[0],
            'default_use_template':bool(template_id),
            'default_template_id':template_id,
            'default_composition_mode':'comment',
            'mark_so_as_sent':True,
            'custom_layout':"mail.mail_notification_paynow",
            'proforma':self.env.context.get('proforma',False),
            'force_email':True,
            'model_description':self.with_context(lang=lang).type_name,
        }
        return{
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(False,'form')],
            'view_id':False,
            'target':'new',
            'context':ctx,
        }

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,**kwargs):
        ifself.env.context.get('mark_so_as_sent'):
            self.filtered(lambdao:o.state=='draft').with_context(tracking_disable=True).write({'state':'sent'})
        returnsuper(SaleOrder,self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def_sms_get_number_fields(self):
        """Nophoneormobilefieldisavailableonsalemodel.InsteadSMSwill
        fallbackonpartner-basedcomputationusing``_sms_get_partner_fields``."""
        return[]

    def_sms_get_partner_fields(self):
        return['partner_id']

    def_send_order_confirmation_mail(self):
        ifself.env.su:
            #sendingmailinsudowasmeantforitbeingsentfromsuperuser
            self=self.with_user(SUPERUSER_ID)
        fororderinself:
            template_id=order._find_mail_template(force_confirmation_template=True)
            iftemplate_id:
                order.with_context(force_send=True).message_post_with_template(template_id,composition_mode='comment',email_layout_xmlid="mail.mail_notification_paynow")

    defaction_done(self):
        fororderinself:
            tx=order.sudo().transaction_ids.get_last_transaction()
            iftxandtx.state=='pending'andtx.acquirer_id.provider=='transfer':
                tx._set_transaction_done()
                tx.write({'is_processed':True})
        returnself.write({'state':'done'})

    defaction_unlock(self):
        self.write({'state':'sale'})

    def_action_confirm(self):
        """ImplementationofadditionnalmecanismofSalesOrderconfirmation.
            Thismethodshouldbeextendedwhentheconfirmationshouldgenerated
            otherdocuments.Inthismethod,theSOarein'sale'state(notyet'done').
        """
        #createananalyticaccountifatleastanexpenseproduct
        fororderinself:
            ifany(expense_policynotin[False,'no']forexpense_policyinorder.order_line.mapped('product_id.expense_policy')):
                ifnotorder.analytic_account_id:
                    order._create_analytic_account()

        returnTrue

    def_prepare_confirmation_values(self):
        return{
            'state':'sale',
            'date_order':fields.Datetime.now()
        }

    defaction_confirm(self):
        ifself._get_forbidden_state_confirm()&set(self.mapped('state')):
            raiseUserError(_(
                'Itisnotallowedtoconfirmanorderinthefollowingstates:%s'
            )%(','.join(self._get_forbidden_state_confirm())))

        fororderinself.filtered(lambdaorder:order.partner_idnotinorder.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        #Contextkey'default_name'issometimespropagateduptohere.
        #Wedon'tneeditanditcreatesissuesinthecreationoflinkedrecords.
        context=self._context.copy()
        context.pop('default_name',None)

        self.with_context(context)._action_confirm()
        ifself.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        returnTrue

    def_get_forbidden_state_confirm(self):
        return{'done','cancel'}

    def_prepare_analytic_account_data(self,prefix=None):
        """
        Preparemethodforanalyticaccountdata

        :paramprefix:Theprefixoftheto-be-createdanalyticaccountname
        :typeprefix:string
        :return:dictionaryofvaluefornewanalyticaccountcreation
        """
        name=self.name
        ifprefix:
            name=prefix+":"+self.name
        return{
            'name':name,
            'code':self.client_order_ref,
            'company_id':self.company_id.id,
            'partner_id':self.partner_id.id
        }

    def_create_analytic_account(self,prefix=None):
        fororderinself:
            analytic=self.env['account.analytic.account'].create(order._prepare_analytic_account_data(prefix))
            order.analytic_account_id=analytic

    def_amount_by_group(self):
        fororderinself:
            currency=order.currency_idororder.company_id.currency_id
            fmt=partial(formatLang,self.with_context(lang=order.partner_id.lang).env,currency_obj=currency)
            res={}
            forlineinorder.order_line:
                price_reduce=line.price_unit*(1.0-line.discount/100.0)
                taxes=line.tax_id.compute_all(price_reduce,quantity=line.product_uom_qty,product=line.product_id,partner=order.partner_shipping_id)['taxes']
                fortaxinline.tax_id:
                    group=tax.tax_group_id
                    res.setdefault(group,{'amount':0.0,'base':0.0})
                    fortintaxes:
                        ift['id']==tax.idort['id']intax.children_tax_ids.ids:
                            res[group]['amount']+=t['amount']
                            res[group]['base']+=t['base']
            res=sorted(res.items(),key=lambdal:l[0].sequence)

            #roundamountandprevent-0.00
            forgroup_datainres:
                group_data[1]['amount']=currency.round(group_data[1]['amount'])+0.0
                group_data[1]['base']=currency.round(group_data[1]['base'])+0.0

            order.amount_by_group=[(
                l[0].name,l[1]['amount'],l[1]['base'],
                fmt(l[1]['amount']),fmt(l[1]['base']),
                len(res),
            )forlinres]

    defhas_to_be_signed(self,include_draft=False):
        return(self.state=='sent'or(self.state=='draft'andinclude_draft))andnotself.is_expiredandself.require_signatureandnotself.signature

    defhas_to_be_paid(self,include_draft=False):
        transaction=self.get_portal_last_transaction()
        return(self.state=='sent'or(self.state=='draft'andinclude_draft))andnotself.is_expiredandself.require_paymentandtransaction.state!='done'andself.amount_total

    def_notify_get_groups(self,msg_vals=None):
        """Giveaccessbuttontousersandportalcustomerasportalisintegrated
        insale.Customerandportalgrouphaveprobablynorighttosee
        thedocumentsotheydon'thavetheaccessbutton."""
        groups=super(SaleOrder,self)._notify_get_groups(msg_vals=msg_vals)

        self.ensure_one()
        ifself.statenotin('draft','cancel'):
            forgroup_name,group_method,group_dataingroups:
                ifgroup_namenotin('customer','portal'):
                    group_data['has_button_access']=True

        returngroups

    def_create_payment_transaction(self,vals):
        '''Similartoself.env['payment.transaction'].create(vals)butthevaluesarefilledwiththe
        currentsalesordersfields(e.g.thepartnerorthecurrency).
        :paramvals:Thevaluestocreateanewpayment.transaction.
        :return:Thenewlycreatedpayment.transactionrecord.
        '''
        #Ensurethecurrenciesarethesame.
        currency=self[0].pricelist_id.currency_id
        ifany(so.pricelist_id.currency_id!=currencyforsoinself):
            raiseValidationError(_('Atransactioncan\'tbelinkedtosalesordershavingdifferentcurrencies.'))

        #Ensurethepartnerarethesame.
        partner=self[0].partner_invoice_id
        ifany(so.partner_invoice_id!=partnerforsoinself):
            raiseValidationError(_('Atransactioncan\'tbelinkedtosalesordershavingdifferentpartners.'))

        #Trytoretrievetheacquirer.However,fallbacktothetoken'sacquirer.
        acquirer_id=vals.get('acquirer_id')
        acquirer=False
        payment_token_id=vals.get('payment_token_id')

        ifpayment_token_id:
            payment_token=self.env['payment.token'].sudo().browse(payment_token_id)

            #Checkpayment_token/acquirermatchingortaketheacquirerfromtoken
            ifacquirer_id:
                acquirer=self.env['payment.acquirer'].browse(acquirer_id)
                ifpayment_tokenandpayment_token.acquirer_id!=acquirer:
                    raiseValidationError(_('Invalidtokenfound!Tokenacquirer%s!=%s')%(
                    payment_token.acquirer_id.name,acquirer.name))
            else:
                acquirer=payment_token.acquirer_id

            ifpayment_tokenandpayment_token.partner_id!=partner:
                raiseValidationError(_('Invalidtokenfound!'))

        #Checkanacquireristhere.
        ifnotacquirer_idandnotacquirer:
            raiseValidationError(_('Apaymentacquirerisrequiredtocreateatransaction.'))

        ifnotacquirer:
            acquirer=self.env['payment.acquirer'].browse(acquirer_id)

        #Checkajournalissetonacquirer.
        ifnotacquirer.journal_id:
            raiseValidationError(_('Ajournalmustbespecifiedfortheacquirer%s.',acquirer.name))

        ifnotacquirer_idandacquirer:
            vals['acquirer_id']=acquirer.id

        vals.update({
            'amount':sum(self.mapped('amount_total')),
            'currency_id':currency.id,
            'partner_id':partner.id,
            'sale_order_ids':[(6,0,self.ids)],
            'type':self[0]._get_payment_type(vals.get('type')=='form_save'),
        })

        transaction=self.env['payment.transaction'].create(vals)

        #Processdirectlyifpayment_token
        iftransaction.payment_token_id:
            transaction.s2s_do_transaction()

        returntransaction

    defpreview_sale_order(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'self',
            'url':self.get_portal_url(),
        }

    def_force_lines_to_invoice_policy_order(self):
        forlineinself.order_line:
            ifself.statein['sale','done']:
                line.qty_to_invoice=line.product_uom_qty-line.qty_invoiced
            else:
                line.qty_to_invoice=0

    defpayment_action_capture(self):
        self.authorized_transaction_ids.action_capture()

    defpayment_action_void(self):
        self.authorized_transaction_ids.action_void()

    defget_portal_last_transaction(self):
        self.ensure_one()
        returnself.transaction_ids.get_last_transaction()

    @api.model
    def_get_customer_lead(self,product_tmpl_id):
        returnFalse

    def_get_report_base_filename(self):
        self.ensure_one()
        return'%s%s'%(self.type_name,self.name)

    def_get_payment_type(self,tokenize=False):
        self.ensure_one()
        return'form_save'iftokenizeelse'form'

    def_get_portal_return_action(self):
        """Returntheactionusedtodisplayorderswhenreturningfromcustomerportal."""
        self.ensure_one()
        returnself.env.ref('sale.action_quotations_with_onboarding')

    @api.model
    def_prepare_down_payment_section_line(self,**optional_values):
        """
        Preparethedictofvaluestocreateanewdownpaymentsectionforasalesorderline.

        :paramoptional_values:anyparameterthatshouldbeaddedtothereturneddownpaymentsection
        """
        context={'lang':self.partner_id.lang}
        down_payments_section_line={
            'display_type':'line_section',
            'name':_('DownPayments'),
            'product_id':False,
            'product_uom_id':False,
            'quantity':0,
            'discount':0,
            'price_unit':0,
            'account_id':False
        }
        delcontext
        ifoptional_values:
            down_payments_section_line.update(optional_values)
        returndown_payments_section_line

    defadd_option_to_order_with_taxcloud(self):
        self.ensure_one()


classSaleOrderLine(models.Model):
    _name='sale.order.line'
    _description='SalesOrderLine'
    _order='order_id,sequence,id'
    _check_company_auto=True

    @api.depends('state','product_uom_qty','qty_delivered','qty_to_invoice','qty_invoiced')
    def_compute_invoice_status(self):
        """
        ComputetheinvoicestatusofaSOline.Possiblestatuses:
        -no:iftheSOisnotinstatus'sale'or'done',weconsiderthatthereisnothingto
          invoice.Thisisalsohtedefaultvalueiftheconditionsofnootherstatusismet.
        -toinvoice:werefertothequantitytoinvoiceoftheline.Refertomethod
          `_get_to_invoice_qty()`formoreinformationonhowthisquantityiscalculated.
        -upselling:thisispossibleonlyforaproductinvoicedonorderedquantitiesforwhich
          wedeliveredmorethanexpected.Thecouldariseif,forexample,aprojecttookmore
          timethanexpectedbutwedecidednottoinvoicetheextracosttotheclient.This
          occursonylinstate'sale',sothatwhenaSOissettodone,theupsellingopportunity
          isremovedfromthelist.
        -invoiced:thequantityinvoicedislargerorequaltothequantityordered.
        """
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        forlineinself:
            ifline.statenotin('sale','done'):
                line.invoice_status='no'
            elifline.is_downpaymentandline.untaxed_amount_to_invoice==0:
                line.invoice_status='invoiced'
            elifnotfloat_is_zero(line.qty_to_invoice,precision_digits=precision):
                line.invoice_status='toinvoice'
            elifline.state=='sale'andline.product_id.invoice_policy=='order'and\
                    line.product_uom_qty>=0.0and\
                    float_compare(line.qty_delivered,line.product_uom_qty,precision_digits=precision)==1:
                line.invoice_status='upselling'
            eliffloat_compare(line.qty_invoiced,line.product_uom_qty,precision_digits=precision)>=0:
                line.invoice_status='invoiced'
            else:
                line.invoice_status='no'

    def_expected_date(self):
        self.ensure_one()
        order_date=fields.Datetime.from_string(self.order_id.date_orderifself.order_id.date_orderandself.order_id.statein['sale','done']elsefields.Datetime.now())
        returnorder_date+timedelta(days=self.customer_leador0.0)

    @api.depends('product_uom_qty','discount','price_unit','tax_id')
    def_compute_amount(self):
        """
        ComputetheamountsoftheSOline.
        """
        forlineinself:
            price=line.price_unit*(1-(line.discountor0.0)/100.0)
            taxes=line.tax_id.compute_all(price,line.order_id.currency_id,line.product_uom_qty,product=line.product_id,partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax':sum(t.get('amount',0.0)fortintaxes.get('taxes',[])),
                'price_total':taxes['total_included'],
                'price_subtotal':taxes['total_excluded'],
            })

    @api.depends('product_id','order_id.state','qty_invoiced','qty_delivered')
    def_compute_product_updatable(self):
        forlineinself:
            ifline.statein['done','cancel']or(line.state=='sale'and(line.qty_invoiced>0orline.qty_delivered>0)):
                line.product_updatable=False
            else:
                line.product_updatable=True

    #notriggerproduct_id.invoice_policytoavoidretroactivelychangingSO
    @api.depends('qty_invoiced','qty_delivered','product_uom_qty','order_id.state')
    def_get_to_invoice_qty(self):
        """
        Computethequantitytoinvoice.Iftheinvoicepolicyisorder,thequantitytoinvoiceis
        calculatedfromtheorderedquantity.Otherwise,thequantitydeliveredisused.
        """
        forlineinself:
            ifline.order_id.statein['sale','done']:
                ifline.product_id.invoice_policy=='order':
                    line.qty_to_invoice=line.product_uom_qty-line.qty_invoiced
                else:
                    line.qty_to_invoice=line.qty_delivered-line.qty_invoiced
            else:
                line.qty_to_invoice=0

    @api.depends('invoice_lines.move_id.state','invoice_lines.quantity')
    def_get_invoice_qty(self):
        """
        Computethequantityinvoiced.Ifcaseofarefund,thequantityinvoicedisdecreased.Note
        thatthisisthecaseonlyiftherefundisgeneratedfromtheSOandthatisintentional:if
        arefundmadewouldautomaticallydecreasetheinvoicedquantity,thenthereisariskofreinvoicing
        itautomatically,whichmaynotbewantedatall.That'swhytherefundhastobecreatedfromtheSO
        """
        forlineinself:
            qty_invoiced=0.0
            forinvoice_lineinline.invoice_lines:
                ifinvoice_line.move_id.state!='cancel':
                    ifinvoice_line.move_id.move_type=='out_invoice':
                        qty_invoiced+=invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,line.product_uom)
                    elifinvoice_line.move_id.move_type=='out_refund':
                        qty_invoiced-=invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,line.product_uom)
            line.qty_invoiced=qty_invoiced

    @api.depends('price_unit','discount')
    def_get_price_reduce(self):
        forlineinself:
            line.price_reduce=line.price_unit*(1.0-line.discount/100.0)

    @api.depends('price_total','product_uom_qty')
    def_get_price_reduce_tax(self):
        forlineinself:
            line.price_reduce_taxinc=line.price_total/line.product_uom_qtyifline.product_uom_qtyelse0.0

    @api.depends('price_subtotal','product_uom_qty')
    def_get_price_reduce_notax(self):
        forlineinself:
            line.price_reduce_taxexcl=line.price_subtotal/line.product_uom_qtyifline.product_uom_qtyelse0.0

    def_compute_tax_id(self):
        forlineinself:
            line=line.with_company(line.company_id)
            fpos=line.order_id.fiscal_position_idorline.order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
            #Ifcompany_idisset,alwaysfiltertaxesbythecompany
            taxes=line.product_id.taxes_id.filtered(lambdat:t.company_id==line.env.company)
            line.tax_id=fpos.map_tax(taxes,line.product_id,line.order_id.partner_shipping_id)

    @api.model
    def_prepare_add_missing_fields(self,values):
        """Deducemissingrequiredfieldsfromtheonchange"""
        res={}
        onchange_fields=['name','price_unit','product_uom','tax_id']
        ifvalues.get('order_id')andvalues.get('product_id')andany(fnotinvaluesforfinonchange_fields):
            line=self.new(values)
            line.product_id_change()
            forfieldinonchange_fields:
                iffieldnotinvalues:
                    res[field]=line._fields[field].convert_to_write(line[field],line)
        returnres

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            ifvalues.get('display_type',self.default_get(['display_type'])['display_type']):
                values.update(product_id=False,price_unit=0,product_uom_qty=0,product_uom=False,customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))

        lines=super().create(vals_list)
        forlineinlines:
            ifline.product_idandline.order_id.state=='sale':
                msg=_("Extralinewith%s")%(line.product_id.display_name,)
                line.order_id.message_post(body=msg)
                #createananalyticaccountifatleastanexpenseproduct
                ifline.product_id.expense_policynotin[False,'no']andnotline.order_id.analytic_account_id:
                    line.order_id._create_analytic_account()
        returnlines

    _sql_constraints=[
        ('accountable_required_fields',
            "CHECK(display_typeISNOTNULLOR(product_idISNOTNULLANDproduct_uomISNOTNULL))",
            "Missingrequiredfieldsonaccountablesaleorderline."),
        ('non_accountable_null_fields',
            "CHECK(display_typeISNULLOR(product_idISNULLANDprice_unit=0ANDproduct_uom_qty=0ANDproduct_uomISNULLANDcustomer_lead=0))",
            "Forbiddenvaluesonnon-accountablesaleorderline"),
    ]

    def_update_line_quantity(self,values):
        orders=self.mapped('order_id')
        fororderinorders:
            order_lines=self.filtered(lambdax:x.order_id==order)
            msg="<b>"+_("Theorderedquantityhasbeenupdated.")+"</b><ul>"
            forlineinorder_lines:
                msg+="<li>%s:<br/>"%line.product_id.display_name
                msg+=_(
                    "OrderedQuantity:%(old_qty)s->%(new_qty)s",
                    old_qty=line.product_uom_qty,
                    new_qty=values["product_uom_qty"]
                )+"<br/>"
                ifline.product_id.typein('consu','product'):
                    msg+=_("DeliveredQuantity:%s",line.qty_delivered)+"<br/>"
                msg+=_("InvoicedQuantity:%s",line.qty_invoiced)+"<br/>"
            msg+="</ul>"
            order.message_post(body=msg)

    defwrite(self,values):
        if'display_type'invaluesandself.filtered(lambdaline:line.display_type!=values.get('display_type')):
            raiseUserError(_("Youcannotchangethetypeofasaleorderline.Insteadyoushoulddeletethecurrentlineandcreateanewlineofthepropertype."))

        if'product_uom_qty'invalues:
            precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
            self.filtered(
                lambdar:r.state=='sale'andfloat_compare(r.product_uom_qty,values['product_uom_qty'],precision_digits=precision)!=0)._update_line_quantity(values)

        #PreventwritingonalockedSO.
        protected_fields=self._get_protected_fields()
        if'done'inself.mapped('order_id.state')andany(finvalues.keys()forfinprotected_fields):
            protected_fields_modified=list(set(protected_fields)&set(values.keys()))
            fields=self.env['ir.model.fields'].search([
                ('name','in',protected_fields_modified),('model','=',self._name)
            ])
            raiseUserError(
                _('Itisforbiddentomodifythefollowingfieldsinalockedorder:\n%s')
                %'\n'.join(fields.mapped('field_description'))
            )

        result=super(SaleOrderLine,self).write(values)
        returnresult

    order_id=fields.Many2one('sale.order',string='OrderReference',required=True,ondelete='cascade',index=True,copy=False)
    name=fields.Text(string='Description',required=True)
    sequence=fields.Integer(string='Sequence',default=10)

    invoice_lines=fields.Many2many('account.move.line','sale_order_line_invoice_rel','order_line_id','invoice_line_id',string='InvoiceLines',copy=False)
    invoice_status=fields.Selection([
        ('upselling','UpsellingOpportunity'),
        ('invoiced','FullyInvoiced'),
        ('toinvoice','ToInvoice'),
        ('no','NothingtoInvoice')
        ],string='InvoiceStatus',compute='_compute_invoice_status',store=True,readonly=True,default='no')
    price_unit=fields.Float('UnitPrice',required=True,digits='ProductPrice',default=0.0)

    price_subtotal=fields.Monetary(compute='_compute_amount',string='Subtotal',readonly=True,store=True)
    price_tax=fields.Float(compute='_compute_amount',string='TotalTax',readonly=True,store=True)
    price_total=fields.Monetary(compute='_compute_amount',string='Total',readonly=True,store=True)

    price_reduce=fields.Float(compute='_get_price_reduce',string='PriceReduce',digits='ProductPrice',readonly=True,store=True)
    tax_id=fields.Many2many('account.tax',string='Taxes',context={'active_test':False})
    price_reduce_taxinc=fields.Monetary(compute='_get_price_reduce_tax',string='PriceReduceTaxinc',readonly=True,store=True)
    price_reduce_taxexcl=fields.Monetary(compute='_get_price_reduce_notax',string='PriceReduceTaxexcl',readonly=True,store=True)

    discount=fields.Float(string='Discount(%)',digits='Discount',default=0.0)

    product_id=fields.Many2one(
        'product.product',string='Product',domain="[('sale_ok','=',True),'|',('company_id','=',False),('company_id','=',company_id)]",
        change_default=True,ondelete='restrict',check_company=True) #Unrequiredcompany
    product_template_id=fields.Many2one(
        'product.template',string='ProductTemplate',
        related="product_id.product_tmpl_id",domain=[('sale_ok','=',True)])
    product_updatable=fields.Boolean(compute='_compute_product_updatable',string='CanEditProduct',readonly=True,default=True)
    product_uom_qty=fields.Float(string='Quantity',digits='ProductUnitofMeasure',required=True,default=1.0)
    product_uom=fields.Many2one('uom.uom',string='UnitofMeasure',domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id',readonly=True)
    product_uom_readonly=fields.Boolean(compute='_compute_product_uom_readonly')
    product_custom_attribute_value_ids=fields.One2many('product.attribute.custom.value','sale_order_line_id',string="CustomValues",copy=True)

    #M2Mholdingthevaluesofproduct.attributewithcreate_variantfieldsetto'no_variant'
    #Itallowskeepingtrackoftheextra_priceassociatedtothoseattributevaluesandaddthemtotheSOlinedescription
    product_no_variant_attribute_value_ids=fields.Many2many('product.template.attribute.value',string="ExtraValues",ondelete='restrict')

    qty_delivered_method=fields.Selection([
        ('manual','Manual'),
        ('analytic','AnalyticFromExpenses')
    ],string="Methodtoupdatedeliveredqty",compute='_compute_qty_delivered_method',compute_sudo=True,store=True,readonly=True,
        help="Accordingtoproductconfiguration,thedeliveredquantitycanbeautomaticallycomputedbymechanism:\n"
             " -Manual:thequantityissetmanuallyontheline\n"
             " -AnalyticFromexpenses:thequantityisthequantitysumfrompostedexpenses\n"
             " -Timesheet:thequantityisthesumofhoursrecordedontaskslinkedtothissaleline\n"
             " -StockMoves:thequantitycomesfromconfirmedpickings\n")
    qty_delivered=fields.Float('DeliveredQuantity',copy=False,compute='_compute_qty_delivered',inverse='_inverse_qty_delivered',compute_sudo=True,store=True,digits='ProductUnitofMeasure',default=0.0)
    qty_delivered_manual=fields.Float('DeliveredManually',copy=False,digits='ProductUnitofMeasure',default=0.0)
    qty_to_invoice=fields.Float(
        compute='_get_to_invoice_qty',string='ToInvoiceQuantity',store=True,readonly=True,
        digits='ProductUnitofMeasure')
    qty_invoiced=fields.Float(
        compute='_get_invoice_qty',string='InvoicedQuantity',store=True,readonly=True,
        compute_sudo=True,
        digits='ProductUnitofMeasure')

    untaxed_amount_invoiced=fields.Monetary("UntaxedInvoicedAmount",compute='_compute_untaxed_amount_invoiced',compute_sudo=True,store=True)
    untaxed_amount_to_invoice=fields.Monetary("UntaxedAmountToInvoice",compute='_compute_untaxed_amount_to_invoice',compute_sudo=True,store=True)

    salesman_id=fields.Many2one(related='order_id.user_id',store=True,string='Salesperson',readonly=True)
    currency_id=fields.Many2one(related='order_id.currency_id',depends=['order_id.currency_id'],store=True,string='Currency',readonly=True)
    company_id=fields.Many2one(related='order_id.company_id',string='Company',store=True,readonly=True,index=True)
    order_partner_id=fields.Many2one(related='order_id.partner_id',store=True,string='Customer',readonly=False)
    analytic_tag_ids=fields.Many2many(
        'account.analytic.tag',string='AnalyticTags',
        compute='_compute_analytic_tag_ids',store=True,readonly=False,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    analytic_line_ids=fields.One2many('account.analytic.line','so_line',string="Analyticlines")
    is_expense=fields.Boolean('Isexpense',help="Istrueifthesalesorderlinecomesfromanexpenseoravendorbills")
    is_downpayment=fields.Boolean(
        string="Isadownpayment",help="Downpaymentsaremadewhencreatinginvoicesfromasalesorder."
        "Theyarenotcopiedwhenduplicatingasalesorder.")

    state=fields.Selection(
        related='order_id.state',string='OrderStatus',readonly=True,copy=False,store=True,default='draft')

    customer_lead=fields.Float(
        'LeadTime',required=True,default=0.0,
        help="Numberofdaysbetweentheorderconfirmationandtheshippingoftheproductstothecustomer")

    display_type=fields.Selection([
        ('line_section',"Section"),
        ('line_note',"Note")],default=False,help="TechnicalfieldforUXpurpose.")

    @api.depends('state')
    def_compute_product_uom_readonly(self):
        forlineinself:
            line.product_uom_readonly=line.statein['sale','done','cancel']

    @api.depends('state','is_expense')
    def_compute_qty_delivered_method(self):
        """Salemodulecomputedeliveredqtyforproduct[('type','in',['consu']),('service_type','=','manual')]
                -consu+expense_policy:analytic(sumofanalyticunit_amount)
                -consu+noexpense_policy:manual(setmanuallyonSOL)
                -service(+service_type='manual',theonlyavailableoption):manual

            Thisistruewhenonlysaleisinstalled:sale_stockredifinethebehaviorfor'consu'type,
            andsale_timesheetimplementsthebehaviorof'service'+service_type=timesheet.
        """
        forlineinself:
            ifline.is_expense:
                line.qty_delivered_method='analytic'
            else: #serviceandconsu
                line.qty_delivered_method='manual'

    @api.depends('qty_delivered_method','qty_delivered_manual','analytic_line_ids.so_line','analytic_line_ids.unit_amount','analytic_line_ids.product_uom_id')
    def_compute_qty_delivered(self):
        """ThismethodcomputethedeliveredquantityoftheSOlines:itcoversthecaseprovidebysalemodule,aka
            expense/vendorbills(sumofunit_amountofAAL),andmanualcase.
            Thismethodshouldbeoverriddentoprovideotherwaytoautomaticallycomputedeliveredqty.Overridesshould
            taketheirconcernedsolines,computeandsetthe`qty_delivered`field,andcallsuperwiththeremaining
            records.
        """
        #computeforanalyticlines
        lines_by_analytic=self.filtered(lambdasol:sol.qty_delivered_method=='analytic')
        mapping=lines_by_analytic._get_delivered_quantity_by_analytic([('amount','<=',0.0)])
        forso_lineinlines_by_analytic:
            so_line.qty_delivered=mapping.get(so_line.idorso_line._origin.id,0.0)
        #computeformanuallines
        forlineinself:
            ifline.qty_delivered_method=='manual':
                line.qty_delivered=line.qty_delivered_manualor0.0

    def_get_delivered_quantity_by_analytic(self,additional_domain):
        """ComputeandwritethedeliveredquantityofcurrentSOlines,basedontheirrelated
            analyticlines.
            :paramadditional_domain:domaintorestrictAALtoincludeincomputation(requiredsincetimesheetisanAALwithaproject...)
        """
        result={}

        #avoidrecomputationifnoSOlinesconcerned
        ifnotself:
            returnresult

        #groupanalyticlinesbyproductuomandsoline
        domain=expression.AND([[('so_line','in',self.ids)],additional_domain])
        data=self.env['account.analytic.line'].read_group(
            domain,
            ['so_line','unit_amount','product_uom_id'],['product_uom_id','so_line'],lazy=False
        )

        #convertuomandsumallunit_amountofanalyticlinestogetthedeliveredqtyofSOlines
        #browsesolinesandproductuomsheretomakethemsharethesameprefetch
        lines=self.browse([item['so_line'][0]foritemindata])
        lines_map={line.id:lineforlineinlines}
        product_uom_ids=[item['product_uom_id'][0]foritemindataifitem['product_uom_id']]
        product_uom_map={uom.id:uomforuominself.env['uom.uom'].browse(product_uom_ids)}
        foritemindata:
            ifnotitem['product_uom_id']:
                continue
            so_line_id=item['so_line'][0]
            so_line=lines_map[so_line_id]
            result.setdefault(so_line_id,0.0)
            uom=product_uom_map.get(item['product_uom_id'][0])
            ifso_line.product_uom.category_id==uom.category_id:
                qty=uom._compute_quantity(item['unit_amount'],so_line.product_uom,rounding_method='HALF-UP')
            else:
                qty=item['unit_amount']
            result[so_line_id]+=qty

        returnresult

    @api.onchange('qty_delivered')
    def_inverse_qty_delivered(self):
        """Whenwritingonqty_delivered,ifthevalueshouldbemodifymanually(`qty_delivered_method`='manual'only),
            thenweputthevaluein`qty_delivered_manual`.Otherwise,`qty_delivered_manual`shouldbeFalsesincethe
            deliveredqtyisautomaticallycomputebyothermecanisms.
        """
        forlineinself:
            ifline.qty_delivered_method=='manual':
                line.qty_delivered_manual=line.qty_delivered
            else:
                line.qty_delivered_manual=0.0

    @api.depends('invoice_lines','invoice_lines.price_total','invoice_lines.move_id.state','invoice_lines.move_id.move_type')
    def_compute_untaxed_amount_invoiced(self):
        """Computetheuntaxedamountalreadyinvoicedfromthesaleorderline,takingtherefundattached
            thesolineintoaccount.Thisamountiscomputedas
                SUM(inv_line.price_subtotal)-SUM(ref_line.price_subtotal)
            where
                `inv_line`isacustomerinvoicelinelinkedtotheSOline
                `ref_line`isacustomercreditnote(refund)linelinkedtotheSOline
        """
        forlineinself:
            amount_invoiced=0.0
            forinvoice_lineinline.invoice_lines:
                ifinvoice_line.move_id.state=='posted':
                    invoice_date=invoice_line.move_id.invoice_dateorfields.Date.today()
                    ifinvoice_line.move_id.move_type=='out_invoice':
                        amount_invoiced+=invoice_line.currency_id._convert(invoice_line.price_subtotal,line.currency_id,line.company_id,invoice_date)
                    elifinvoice_line.move_id.move_type=='out_refund':
                        amount_invoiced-=invoice_line.currency_id._convert(invoice_line.price_subtotal,line.currency_id,line.company_id,invoice_date)
            line.untaxed_amount_invoiced=amount_invoiced

    @api.depends('state','price_reduce','product_id','untaxed_amount_invoiced','qty_delivered','product_uom_qty')
    def_compute_untaxed_amount_to_invoice(self):
        """Totalofremainingamounttoinvoiceonthesaleorderline(taxesexcl.)as
                total_sol-amountalreadyinvoiced
            whereTotal_soldependsontheinvoicepolicyoftheproduct.

            Note:Draftinvoiceareignoredonpurpose,the'toinvoice'amountshould
            comeonlyfromtheSOlines.
        """
        forlineinself:
            amount_to_invoice=0.0
            ifline.statein['sale','done']:
                #Note:donotuseprice_subtotalfieldasitreturnszerowhentheorderedquantityis
                #zero.Itcausesproblemforexpenseline(e.i.:orderedqty=0,deliqty=4,
                #price_unit=20;subtotaliszero),butwhenyoucaninvoicetheline,youseean
                #amountandnotzero.Sincewecomputeuntaxedamount,wecanusedirectlytheprice
                #reduce(toincludediscount)withoutusing`compute_all()`methodontaxes.
                price_subtotal=0.0
                uom_qty_to_consider=line.qty_deliveredifline.product_id.invoice_policy=='delivery'elseline.product_uom_qty
                price_reduce=line.price_unit*(1-(line.discountor0.0)/100.0)
                price_subtotal=price_reduce*uom_qty_to_consider
                iflen(line.tax_id.filtered(lambdatax:tax.price_include))>0:
                    #Asincludedtaxesarenotexcludedfromthecomputedsubtotal,`compute_all()`method
                    #hastobecalledtoretrievethesubtotalwithoutthem.
                    #`price_reduce_taxexcl`cannotbeusedasitiscomputedfrom`price_subtotal`field.(seeupperNote)
                    price_subtotal=line.tax_id.compute_all(
                        price_reduce,
                        currency=line.order_id.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id)['total_excluded']

                ifany(line.invoice_lines.mapped(lambdal:l.discount!=line.discount)):
                    #Incaseofre-invoicingwithdifferentdiscountwetrytocalculatemanuallythe
                    #remainingamounttoinvoice
                    amount=0
                    forlinline.invoice_lines:
                        iflen(l.tax_ids.filtered(lambdatax:tax.price_include))>0:
                            amount+=l.tax_ids.compute_all(l.currency_id._convert(l.price_unit,line.currency_id,line.company_id,l.dateorfields.Date.today(),round=False)*l.quantity)['total_excluded']
                        else:
                            amount+=l.currency_id._convert(l.price_unit,line.currency_id,line.company_id,l.dateorfields.Date.today(),round=False)*l.quantity

                    amount_to_invoice=max(price_subtotal-amount,0)
                else:
                    amount_to_invoice=price_subtotal-line.untaxed_amount_invoiced

            line.untaxed_amount_to_invoice=amount_to_invoice

    @api.depends('product_id','order_id.date_order','order_id.partner_id')
    def_compute_analytic_tag_ids(self):
        forlineinself:
            ifnotline.display_typeandline.state=='draft':
                default_analytic_account=line.env['account.analytic.default'].sudo().account_get(
                    product_id=line.product_id.id,
                    partner_id=line.order_id.partner_id.id,
                    user_id=self.env.uid,
                    date=line.order_id.date_order,
                    company_id=line.company_id.id,
                )
                line.analytic_tag_ids=default_analytic_account.analytic_tag_ids

    def_get_invoice_line_sequence(self,new=0,old=0):
        """
        Methodintendedtobeoverriddeninthird-partymoduleifwewanttopreventtheresequencing
        ofinvoicelines.

        :paramintnew:  thenewlinesequence
        :paramintold:  theoldlinesequence

        :return:         thesequenceoftheSOline,bydefaultthenewone.
        """
        returnneworold

    def_prepare_invoice_line(self,**optional_values):
        """
        Preparethedictofvaluestocreatethenewinvoicelineforasalesorderline.

        :paramqty:floatquantitytoinvoice
        :paramoptional_values:anyparameterthatshouldbeaddedtothereturnedinvoiceline
        """
        self.ensure_one()
        res={
            'display_type':self.display_type,
            'sequence':self.sequence,
            'name':self.name,
            'product_id':self.product_id.id,
            'product_uom_id':self.product_uom.id,
            'quantity':self.qty_to_invoice,
            'discount':self.discount,
            'price_unit':self.price_unit,
            'tax_ids':[(6,0,self.tax_id.ids)],
            'analytic_account_id':self.order_id.analytic_account_id.idifnotself.display_typeelseFalse,
            'analytic_tag_ids':[(6,0,self.analytic_tag_ids.ids)],
            'sale_line_ids':[(4,self.id)],
        }
        ifoptional_values:
            res.update(optional_values)
        ifself.display_type:
            res['account_id']=False
        returnres

    def_prepare_procurement_values(self,group_id=False):
        """Preparespecifickeyformovesorothercomponentsthatwillbecreatedfromastockrule
        commingfromasaleorderline.Thismethodcouldbeoverrideinordertoaddothercustomkeythatcould
        beusedinmove/pocreation.
        """
        return{}

    def_get_display_price(self,product):
        #TODO:movemeinmaster/saas-16onsale.order
        #awa:don'tknowifit'sstillthecasesinceweneedthe"product_no_variant_attribute_value_ids"fieldnow
        #tobeabletocomputethefullprice

        #itispossiblethatano_variantattributeisstillinavariantif
        #thetypeoftheattributehasbeenchangedaftercreation.
        no_variant_attributes_price_extra=[
            ptav.price_extraforptavinself.product_no_variant_attribute_value_ids.filtered(
                lambdaptav:
                    ptav.price_extraand
                    ptavnotinproduct.product_template_attribute_value_ids
            )
        ]
        ifno_variant_attributes_price_extra:
            product=product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )

        ifself.order_id.pricelist_id.discount_policy=='with_discount':
            returnproduct.with_context(pricelist=self.order_id.pricelist_id.id,uom=self.product_uom.id).price
        product_context=dict(self.env.context,partner_id=self.order_id.partner_id.id,date=self.order_id.date_order,uom=self.product_uom.id)

        final_price,rule_id=self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(productorself.product_id,self.product_uom_qtyor1.0,self.order_id.partner_id)
        base_price,currency=self.with_context(product_context)._get_real_price_currency(product,rule_id,self.product_uom_qty,self.product_uom,self.order_id.pricelist_id.id)
        ifcurrency!=self.order_id.pricelist_id.currency_id:
            base_price=currency._convert(
                base_price,self.order_id.pricelist_id.currency_id,
                self.order_id.company_idorself.env.company,self.order_id.date_orderorfields.Date.today())
        #negativediscounts(=surcharge)areincludedinthedisplayprice
        returnmax(base_price,final_price)

    @api.onchange('product_id')
    defproduct_id_change(self):
        ifnotself.product_id:
            return
        valid_values=self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        #removetheis_customvaluesthatdon'tbelongtothistemplate
        forpacvinself.product_custom_attribute_value_ids:
            ifpacv.custom_product_template_attribute_value_idnotinvalid_values:
                self.product_custom_attribute_value_ids-=pacv

        #removetheno_variantattributesthatdon'tbelongtothistemplate
        forptavinself.product_no_variant_attribute_value_ids:
            ifptav._originnotinvalid_values:
                self.product_no_variant_attribute_value_ids-=ptav

        vals={}
        ifnotself.product_uomor(self.product_id.uom_id.id!=self.product_uom.id):
            vals['product_uom']=self.product_id.uom_id
            vals['product_uom_qty']=self.product_uom_qtyor1.0

        lang=get_lang(self.env,self.order_id.partner_id.lang).code
        product=self.product_id.with_context(
            lang=lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty')orself.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        vals.update(name=self.with_context(lang=lang).get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        ifself.order_id.pricelist_idandself.order_id.partner_id:
            vals['price_unit']=product._get_tax_included_unit_price(
                self.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                'sale',
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(product),
                product_currency=self.order_id.currency_id
            )
        self.update(vals)

        title=False
        message=False
        result={}
        warning={}
        ifproduct.sale_line_warn!='no-message':
            title=_("Warningfor%s",product.name)
            message=product.sale_line_warn_msg
            warning['title']=title
            warning['message']=message
            result={'warning':warning}
            ifproduct.sale_line_warn=='block':
                self.product_id=False

        returnresult

    @api.onchange('product_uom','product_uom_qty')
    defproduct_uom_change(self):
        ifnotself.product_uomornotself.product_id:
            self.price_unit=0.0
            return
        ifself.order_id.pricelist_idandself.order_id.partner_id:
            product=self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit=product._get_tax_included_unit_price(
                self.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                'sale',
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(product),
                product_currency=self.order_id.currency_id
            )

    defname_get(self):
        result=[]
        forso_lineinself.sudo():
            name='%s-%s'%(so_line.order_id.name,so_line.nameandso_line.name.split('\n')[0]orso_line.product_id.name)
            ifso_line.order_partner_id.ref:
                name='%s(%s)'%(name,so_line.order_partner_id.ref)
            result.append((so_line.id,name))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        ifoperatorin('ilike','like','=','=like','=ilike'):
            args=expression.AND([
                argsor[],
                ['|',('order_id.name',operator,name),('name',operator,name)]
            ])
            returnself._search(args,limit=limit,access_rights_uid=name_get_uid)
        returnsuper(SaleOrderLine,self)._name_search(name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    def_check_line_unlink(self):
        """
        Checkwetheralinecanbedeletedornot.

        Linescannotbedeletediftheorderisconfirmed;downpayment
        lineswhohavenotyetbeeninvoicedbypassthatexception.
        Also,allowdeletingUXlines(notes/sections).
        :rtype:recordsetsale.order.line
        :returns:setoflinesthatcannotbedeleted
        """
        returnself.filtered(lambdaline:line.statein('sale','done')and(line.invoice_linesornotline.is_downpayment)andnotline.display_type)

    defunlink(self):
        ifself._check_line_unlink():
            raiseUserError(_('Youcannotremoveanorderlineoncethesalesorderisconfirmed.\nYoushouldrathersetthequantityto0.'))
        returnsuper(SaleOrderLine,self).unlink()

    def_get_real_price_currency(self,product,rule_id,qty,uom,pricelist_id):
        """Retrievethepricebeforeapplyingthepricelist
            :paramobjproduct:objectofcurrentproductrecord
            :paremfloatqty:totalquentityofproduct
            :paramtupleprice_and_rule:tuple(price,suitable_rule)comingfrompricelistcomputation
            :paramobjuom:unitofmeasureofcurrentorderline
            :paramintegerpricelist_id:pricelistidofsalesorder"""
        PricelistItem=self.env['product.pricelist.item']
        field_name='lst_price'
        currency_id=None
        product_currency=product.currency_id
        ifrule_id:
            pricelist_item=PricelistItem.browse(rule_id)
            ifpricelist_item.pricelist_id.discount_policy=='without_discount':
                whilepricelist_item.base=='pricelist'andpricelist_item.base_pricelist_idandpricelist_item.base_pricelist_id.discount_policy=='without_discount':
                    price,rule_id=pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product,qty,self.order_id.partner_id)
                    pricelist_item=PricelistItem.browse(rule_id)

            ifpricelist_item.base=='standard_price':
                field_name='standard_price'
                product_currency=product.cost_currency_id
            elifpricelist_item.base=='pricelist'andpricelist_item.base_pricelist_id:
                field_name='price'
                product=product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency=pricelist_item.base_pricelist_id.currency_id
            currency_id=pricelist_item.pricelist_id.currency_id

        ifnotcurrency_id:
            currency_id=product_currency
            cur_factor=1.0
        else:
            ifcurrency_id.id==product_currency.id:
                cur_factor=1.0
            else:
                cur_factor=currency_id._get_conversion_rate(product_currency,currency_id,self.company_idorself.env.company,self.order_id.date_orderorfields.Date.today())

        product_uom=self.env.context.get('uom')orproduct.uom_id.id
        ifuomanduom.id!=product_uom:
            #theunitpriceisinadifferentuom
            uom_factor=uom._compute_price(1.0,product.uom_id)
        else:
            uom_factor=1.0

        returnproduct[field_name]*uom_factor*cur_factor,currency_id

    def_get_protected_fields(self):
        return[
            'product_id','name','price_unit','product_uom','product_uom_qty',
            'tax_id','analytic_tag_ids'
        ]

    def_onchange_product_id_set_customer_lead(self):
        pass

    @api.onchange('product_id','price_unit','product_uom','product_uom_qty','tax_id')
    def_onchange_discount(self):
        ifnot(self.product_idandself.product_uomand
                self.order_id.partner_idandself.order_id.pricelist_idand
                self.order_id.pricelist_id.discount_policy=='without_discount'and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        self.discount=0.0
        product=self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context=dict(self.env.context,partner_id=self.order_id.partner_id.id,date=self.order_id.date_order,uom=self.product_uom.id)

        price,rule_id=self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id,self.product_uom_qtyor1.0,self.order_id.partner_id)
        new_list_price,currency=self.with_context(product_context)._get_real_price_currency(product,rule_id,self.product_uom_qty,self.product_uom,self.order_id.pricelist_id.id)

        ifnew_list_price!=0:
            ifself.order_id.pricelist_id.currency_id!=currency:
                #weneednew_list_priceinthesamecurrencyasprice,whichisintheSO'spricelist'scurrency
                new_list_price=currency._convert(
                    new_list_price,self.order_id.pricelist_id.currency_id,
                    self.order_id.company_idorself.env.company,self.order_id.date_orderorfields.Date.today())
            discount=(new_list_price-price)/new_list_price*100
            if(discount>0andnew_list_price>0)or(discount<0andnew_list_price<0):
                self.discount=discount

    def_is_delivery(self):
        self.ensure_one()
        returnFalse

    defget_sale_order_line_multiline_description_sale(self,product):
        """Computeadefaultmultilinedescriptionforthissalesorderline.

        Inmostcasestheproductdescriptionisenoughbutsometimesweneedtoappendinformationthatonly
        existsonthesaleorderlineitself.
        e.g:
        -customattributesandattributesthatdon'tcreatevariants,bothintroducedbythe"productconfigurator"
        -inevent_saleweneedtoknowspecificallythesalesorderlineaswellastheproducttogeneratethename:
          theproductisnotsufficientbecausewealsoneedtoknowtheevent_idandtheevent_ticket_id(bothwhichbelongtothesaleorderline).
        """
        returnproduct.get_product_multiline_description_sale()+self._get_sale_order_line_multiline_description_variants()

    def_get_sale_order_line_multiline_description_variants(self):
        """Whenusingno_variantattributesoris_customvalues,theproduct
        itselfisnotsufficienttocreatethedescription:weneedtoadd
        informationaboutthosespecialattributesandvalues.

        :return:thedescriptionrelatedtospecialvariantattributes/values
        :rtype:string
        """
        ifnotself.product_custom_attribute_value_idsandnotself.product_no_variant_attribute_value_ids:
            return""

        name="\n"

        custom_ptavs=self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs=self.product_no_variant_attribute_value_ids._origin

        #displaytheno_variantattributes,exceptthosethatarealso
        #displayedbyacustom(avoidduplicatedescription)
        forptavin(no_variant_ptavs-custom_ptavs):
            name+="\n"+ptav.display_name

        #Sortthevaluesaccordingto_ordersettings,becauseitdoesn'tworkforvirtualrecordsinonchange
        custom_values=sorted(self.product_custom_attribute_value_ids,key=lambdar:(r.custom_product_template_attribute_value_id.id,r.id))
        #displaytheis_customvalues
        forpacvincustom_values:
            name+="\n"+pacv.display_name

        returnname
