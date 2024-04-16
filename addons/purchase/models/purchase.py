#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,time
fromdateutil.relativedeltaimportrelativedelta
fromitertoolsimportgroupby
frompytzimporttimezone,UTC
fromwerkzeug.urlsimporturl_encode

fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT
fromflectra.tools.float_utilsimportfloat_is_zero
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.tools.miscimportformatLang,get_lang,format_amount


classPurchaseOrder(models.Model):
    _name="purchase.order"
    _inherit=['portal.mixin','mail.thread','mail.activity.mixin']
    _description="PurchaseOrder"
    _order='prioritydesc,iddesc'

    @api.depends('order_line.price_total')
    def_amount_all(self):
        fororderinself:
            amount_untaxed=amount_tax=0.0
            forlineinorder.order_line:
                line._compute_amount()
                amount_untaxed+=line.price_subtotal
                amount_tax+=line.price_tax
            currency=order.currency_idororder.partner_id.property_purchase_currency_idorself.env.company.currency_id
            order.update({
                'amount_untaxed':currency.round(amount_untaxed),
                'amount_tax':currency.round(amount_tax),
                'amount_total':amount_untaxed+amount_tax,
            })

    @api.depends('state','order_line.qty_to_invoice')
    def_get_invoiced(self):
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        fororderinself:
            iforder.statenotin('purchase','done'):
                order.invoice_status='no'
                continue

            ifany(
                notfloat_is_zero(line.qty_to_invoice,precision_digits=precision)
                forlineinorder.order_line.filtered(lambdal:notl.display_type)
            ):
                order.invoice_status='toinvoice'
            elif(
                all(
                    float_is_zero(line.qty_to_invoice,precision_digits=precision)
                    forlineinorder.order_line.filtered(lambdal:notl.display_type)
                )
                andorder.invoice_ids
            ):
                order.invoice_status='invoiced'
            else:
                order.invoice_status='no'

    @api.depends('order_line.invoice_lines.move_id')
    def_compute_invoice(self):
        fororderinself:
            invoices=order.mapped('order_line.invoice_lines.move_id')
            order.invoice_ids=invoices
            order.invoice_count=len(invoices)

    READONLY_STATES={
        'purchase':[('readonly',True)],
        'done':[('readonly',True)],
        'cancel':[('readonly',True)],
    }

    name=fields.Char('OrderReference',required=True,index=True,copy=False,default='New')
    priority=fields.Selection(
        [('0','Normal'),('1','Urgent')],'Priority',default='0',index=True)
    origin=fields.Char('SourceDocument',copy=False,
        help="Referenceofthedocumentthatgeneratedthispurchaseorder"
             "request(e.g.asalesorder)")
    partner_ref=fields.Char('VendorReference',copy=False,
        help="Referenceofthesalesorderorbidsentbythevendor."
             "It'susedtodothematchingwhenyoureceivethe"
             "productsasthisreferenceisusuallywrittenonthe"
             "deliveryordersentbyyourvendor.")
    date_order=fields.Datetime('OrderDeadline',required=True,states=READONLY_STATES,index=True,copy=False,default=fields.Datetime.now,
        help="DepictsthedatewithinwhichtheQuotationshouldbeconfirmedandconvertedintoapurchaseorder.")
    date_approve=fields.Datetime('ConfirmationDate',readonly=1,index=True,copy=False)
    partner_id=fields.Many2one('res.partner',string='Vendor',required=True,states=READONLY_STATES,change_default=True,tracking=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]",help="YoucanfindavendorbyitsName,TIN,EmailorInternalReference.")
    dest_address_id=fields.Many2one('res.partner',domain="['|',('company_id','=',False),('company_id','=',company_id)]",string='DropShipAddress',states=READONLY_STATES,
        help="Putanaddressifyouwanttodeliverdirectlyfromthevendortothecustomer."
             "Otherwise,keepemptytodelivertoyourowncompany.")
    currency_id=fields.Many2one('res.currency','Currency',required=True,states=READONLY_STATES,
        default=lambdaself:self.env.company.currency_id.id)
    state=fields.Selection([
        ('draft','RFQ'),
        ('sent','RFQSent'),
        ('toapprove','ToApprove'),
        ('purchase','PurchaseOrder'),
        ('done','Locked'),
        ('cancel','Cancelled')
    ],string='Status',readonly=True,index=True,copy=False,default='draft',tracking=True)
    order_line=fields.One2many('purchase.order.line','order_id',string='OrderLines',states={'cancel':[('readonly',True)],'done':[('readonly',True)]},copy=True)
    notes=fields.Text('TermsandConditions')

    invoice_count=fields.Integer(compute="_compute_invoice",string='BillCount',copy=False,default=0,store=True)
    invoice_ids=fields.Many2many('account.move',compute="_compute_invoice",string='Bills',copy=False,store=True)
    invoice_status=fields.Selection([
        ('no','NothingtoBill'),
        ('toinvoice','WaitingBills'),
        ('invoiced','FullyBilled'),
    ],string='BillingStatus',compute='_get_invoiced',store=True,readonly=True,copy=False,default='no')
    date_planned=fields.Datetime(
        string='ReceiptDate',index=True,copy=False,compute='_compute_date_planned',store=True,readonly=False,
        help="Deliverydatepromisedbyvendor.Thisdateisusedtodetermineexpectedarrivalofproducts.")
    date_calendar_start=fields.Datetime(compute='_compute_date_calendar_start',readonly=True,store=True)

    amount_untaxed=fields.Monetary(string='UntaxedAmount',store=True,readonly=True,compute='_amount_all',tracking=True)
    amount_tax=fields.Monetary(string='Taxes',store=True,readonly=True,compute='_amount_all')
    amount_total=fields.Monetary(string='Total',store=True,readonly=True,compute='_amount_all')

    fiscal_position_id=fields.Many2one('account.fiscal.position',string='FiscalPosition',domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    payment_term_id=fields.Many2one('account.payment.term','PaymentTerms',domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    incoterm_id=fields.Many2one('account.incoterms','Incoterm',states={'done':[('readonly',True)]},help="InternationalCommercialTermsareaseriesofpredefinedcommercialtermsusedininternationaltransactions.")

    product_id=fields.Many2one('product.product',related='order_line.product_id',string='Product',readonly=False)
    user_id=fields.Many2one(
        'res.users',string='PurchaseRepresentative',index=True,tracking=True,
        default=lambdaself:self.env.user,check_company=True)
    company_id=fields.Many2one('res.company','Company',required=True,index=True,states=READONLY_STATES,default=lambdaself:self.env.company.id)
    currency_rate=fields.Float("CurrencyRate",compute='_compute_currency_rate',compute_sudo=True,store=True,readonly=True,help='Ratiobetweenthepurchaseordercurrencyandthecompanycurrency')

    mail_reminder_confirmed=fields.Boolean("ReminderConfirmed",default=False,readonly=True,copy=False,help="Trueifthereminderemailisconfirmedbythevendor.")
    mail_reception_confirmed=fields.Boolean("ReceptionConfirmed",default=False,readonly=True,copy=False,help="TrueifPOreceptionisconfirmedbythevendor.")

    receipt_reminder_email=fields.Boolean('ReceiptReminderEmail',related='partner_id.receipt_reminder_email',readonly=False)
    reminder_date_before_receipt=fields.Integer('DaysBeforeReceipt',related='partner_id.reminder_date_before_receipt',readonly=False)

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

    def_compute_access_url(self):
        super(PurchaseOrder,self)._compute_access_url()
        fororderinself:
            order.access_url='/my/purchase/%s'%(order.id)

    @api.depends('state','date_order','date_approve')
    def_compute_date_calendar_start(self):
        fororderinself:
            order.date_calendar_start=order.date_approveif(order.statein['purchase','done'])elseorder.date_order

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        domain=[]
        ifname:
            domain=['|',('name',operator,name),('partner_ref',operator,name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    @api.depends('date_order','currency_id','company_id','company_id.currency_id')
    def_compute_currency_rate(self):
        fororderinself:
            order.currency_rate=self.env['res.currency']._get_conversion_rate(order.company_id.currency_id,order.currency_id,order.company_id,order.date_order)

    @api.depends('order_line.date_planned')
    def_compute_date_planned(self):
        """date_planned=theearliestdate_plannedacrossallorderlines."""
        fororderinself:
            dates_list=order.order_line.filtered(lambdax:notx.display_typeandx.date_planned).mapped('date_planned')
            ifdates_list:
                order.date_planned=fields.Datetime.to_string(min(dates_list))
            else:
                order.date_planned=False

    @api.depends('name','partner_ref')
    defname_get(self):
        result=[]
        forpoinself:
            name=po.name
            ifpo.partner_ref:
                name+='('+po.partner_ref+')'
            ifself.env.context.get('show_total_amount')andpo.amount_total:
                name+=':'+formatLang(self.env,po.amount_total,currency_obj=po.currency_id)
            result.append((po.id,name))
        returnresult

    @api.onchange('date_planned')
    defonchange_date_planned(self):
        ifself.date_planned:
            self.order_line.filtered(lambdaline:notline.display_type).date_planned=self.date_planned

    defwrite(self,vals):
        vals,partner_vals=self._write_partner_values(vals)
        res=super().write(vals)
        ifpartner_vals:
            self.partner_id.sudo().write(partner_vals) #Becausethepurchaseuserdoesn'thavewriteon`res.partner`
        returnres

    @api.model
    defcreate(self,vals):
        company_id=vals.get('company_id',self.default_get(['company_id'])['company_id'])
        #Ensuresdefaultpickingtypeandcurrencyaretakenfromtherightcompany.
        self_comp=self.with_company(company_id)
        ifvals.get('name','New')=='New':
            seq_date=None
            if'date_order'invals:
                seq_date=fields.Datetime.context_timestamp(self,fields.Datetime.to_datetime(vals['date_order']))
            vals['name']=self_comp.env['ir.sequence'].next_by_code('purchase.order',sequence_date=seq_date)or'/'
        vals,partner_vals=self._write_partner_values(vals)
        res=super(PurchaseOrder,self_comp).create(vals)
        ifpartner_vals:
            res.sudo().write(partner_vals) #Becausethepurchaseuserdoesn'thavewriteon`res.partner`
        returnres

    defunlink(self):
        fororderinself:
            ifnotorder.state=='cancel':
                raiseUserError(_('Inordertodeleteapurchaseorder,youmustcancelitfirst.'))
        returnsuper(PurchaseOrder,self).unlink()

    defcopy(self,default=None):
        ctx=dict(self.env.context)
        ctx.pop('default_product_id',None)
        self=self.with_context(ctx)
        new_po=super(PurchaseOrder,self).copy(default=default)
        forlineinnew_po.order_line:
            ifline.product_id:
                seller=line.product_id._select_seller(
                    partner_id=line.partner_id,quantity=line.product_qty,
                    date=line.order_id.date_orderandline.order_id.date_order.date(),uom_id=line.product_uom)
                line.date_planned=line._get_date_planned(seller)
        returnnew_po

    def_must_delete_date_planned(self,field_name):
        #Tobeoverridden
        returnfield_name=='order_line'

    defonchange(self,values,field_name,field_onchange):
        """OverrideonchangetoNOTtoupdatealldate_plannedonPOlineswhen
        date_plannedonPOisupdatedbythechangeofdate_plannedonPOlines.
        """
        result=super(PurchaseOrder,self).onchange(values,field_name,field_onchange)
        ifself._must_delete_date_planned(field_name)and'value'inresult:
            already_exist=[ol[1]forolinvalues.get('order_line',[])ifol[1]]
            forlineinresult['value'].get('order_line',[]):
                ifline[0]<2and'date_planned'inline[2]andline[1]inalready_exist:
                    delline[2]['date_planned']
        returnresult

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'state'ininit_valuesandself.state=='purchase':
            ifinit_values['state']=='toapprove':
                returnself.env.ref('purchase.mt_rfq_approved')
            returnself.env.ref('purchase.mt_rfq_confirmed')
        elif'state'ininit_valuesandself.state=='toapprove':
            returnself.env.ref('purchase.mt_rfq_confirmed')
        elif'state'ininit_valuesandself.state=='done':
            returnself.env.ref('purchase.mt_rfq_done')
        returnsuper(PurchaseOrder,self)._track_subtype(init_values)

    def_get_report_base_filename(self):
        self.ensure_one()
        return'PurchaseOrder-%s'%(self.name)

    @api.onchange('partner_id','company_id')
    defonchange_partner_id(self):
        #Ensuresallpropertiesandfiscalpositions
        #aretakenwiththecompanyoftheorder
        #ifnotdefined,with_companydoesn'tchangeanything.
        self=self.with_company(self.company_id)
        ifnotself.partner_id:
            self.fiscal_position_id=False
            self.currency_id=self.env.company.currency_id.id
        else:
            self.fiscal_position_id=self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
            self.payment_term_id=self.partner_id.property_supplier_payment_term_id.id
            self.currency_id=self.partner_id.property_purchase_currency_id.idorself.env.company.currency_id.id
        return{}

    @api.onchange('fiscal_position_id','company_id')
    def_compute_tax_id(self):
        """
        TriggertherecomputeofthetaxesifthefiscalpositionischangedonthePO.
        """
        self.order_line._compute_tax_id()

    @api.onchange('partner_id')
    defonchange_partner_id_warning(self):
        ifnotself.partner_idornotself.env.user.has_group('purchase.group_warning_purchase'):
            return
        warning={}
        title=False
        message=False

        partner=self.partner_id

        #Ifpartnerhasnowarning,checkitscompany
        ifpartner.purchase_warn=='no-message'andpartner.parent_id:
            partner=partner.parent_id

        ifpartner.purchase_warnandpartner.purchase_warn!='no-message':
            #Blockifpartneronlyhaswarningbutparentcompanyisblocked
            ifpartner.purchase_warn!='block'andpartner.parent_idandpartner.parent_id.purchase_warn=='block':
                partner=partner.parent_id
            title=_("Warningfor%s",partner.name)
            message=partner.purchase_warn_msg
            warning={
                'title':title,
                'message':message
            }
            ifpartner.purchase_warn=='block':
                self.update({'partner_id':False})
            return{'warning':warning}
        return{}

    defaction_rfq_send(self):
        '''
        Thisfunctionopensawindowtocomposeanemail,withtheedipurchasetemplatemessageloadedbydefault
        '''
        self.ensure_one()
        ir_model_data=self.env['ir.model.data']
        try:
            ifself.env.context.get('send_rfq',False):
                template_id=ir_model_data.get_object_reference('purchase','email_template_edi_purchase')[1]
            else:
                template_id=ir_model_data.get_object_reference('purchase','email_template_edi_purchase_done')[1]
        exceptValueError:
            template_id=False
        try:
            compose_form_id=ir_model_data.get_object_reference('mail','email_compose_message_wizard_form')[1]
        exceptValueError:
            compose_form_id=False
        ctx=dict(self.env.contextor{})
        ctx.update({
            'default_model':'purchase.order',
            'active_model':'purchase.order',
            'active_id':self.ids[0],
            'default_res_id':self.ids[0],
            'default_use_template':bool(template_id),
            'default_template_id':template_id,
            'default_composition_mode':'comment',
            'custom_layout':"mail.mail_notification_paynow",
            'force_email':True,
            'mark_rfq_as_sent':True,
        })

        #InthecaseofaRFQoraPO,wewantthe"View..."buttoninlinewiththestateofthe
        #object.Therefore,wepassthemodeldescriptioninthecontext,inthelanguageinwhich
        #thetemplateisrendered.
        lang=self.env.context.get('lang')
        if{'default_template_id','default_model','default_res_id'}<=ctx.keys():
            template=self.env['mail.template'].browse(ctx['default_template_id'])
            iftemplateandtemplate.lang:
                lang=template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

        self=self.with_context(lang=lang)
        ifself.statein['draft','sent']:
            ctx['model_description']=_('RequestforQuotation')
        else:
            ctx['model_description']=_('PurchaseOrder')

        return{
            'name':_('ComposeEmail'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(compose_form_id,'form')],
            'view_id':compose_form_id,
            'target':'new',
            'context':ctx,
        }

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,**kwargs):
        ifself.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambdao:o.state=='draft').write({'state':'sent'})
        returnsuper(PurchaseOrder,self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    defprint_quotation(self):
        self.write({'state':"sent"})
        returnself.env.ref('purchase.report_purchase_quotation').report_action(self)

    defbutton_approve(self,force=False):
        self=self.filtered(lambdaorder:order._approval_allowed())
        self.write({'state':'purchase','date_approve':fields.Datetime.now()})
        self.filtered(lambdap:p.company_id.po_lock=='lock').write({'state':'done'})
        return{}

    defbutton_draft(self):
        self.write({'state':'draft'})
        return{}

    defbutton_confirm(self):
        fororderinself:
            iforder.statenotin['draft','sent']:
                continue
            order._add_supplier_to_product()
            #Dealwithdoublevalidationprocess
            iforder._approval_allowed():
                order.button_approve()
            else:
                order.write({'state':'toapprove'})
            iforder.partner_idnotinorder.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        returnTrue

    defbutton_cancel(self):
        fororderinself:
            forinvinorder.invoice_ids:
                ifinvandinv.statenotin('cancel','draft'):
                    raiseUserError(_("Unabletocancelthispurchaseorder.Youmustfirstcanceltherelatedvendorbills."))

        self.write({'state':'cancel','mail_reminder_confirmed':False})

    defbutton_unlock(self):
        self.write({'state':'purchase'})

    defbutton_done(self):
        self.write({'state':'done','priority':'0'})

    def_add_supplier_to_product(self):
        #Addthepartnerinthesupplierlistoftheproductifthesupplierisnotregisteredfor
        #thisproduct.Welimitto10thenumberofsuppliersforaproducttoavoidthemessthat
        #couldbecausedforsomegenericproducts("Miscellaneous").
        forlineinself.order_line:
            #Donotaddacontactasasupplier
            partner=self.partner_idifnotself.partner_id.parent_idelseself.partner_id.parent_id
            ifline.product_idandpartnernotinline.product_id.seller_ids.mapped('name')andlen(line.product_id.seller_ids)<=10:
                #Convertthepriceintherightcurrency.
                currency=partner.property_purchase_currency_idorself.env.company.currency_id
                price=self.currency_id._convert(line.price_unit,currency,line.company_id,line.date_orderorfields.Date.today(),round=False)
                #Computethepriceforthetemplate'sUoM,becausethesupplier'sUoMisrelatedtothatUoM.
                ifline.product_id.product_tmpl_id.uom_po_id!=line.product_uom:
                    default_uom=line.product_id.product_tmpl_id.uom_po_id
                    price=line.product_uom._compute_price(price,default_uom)

                supplierinfo={
                    'name':partner.id,
                    'sequence':max(line.product_id.seller_ids.mapped('sequence'))+1ifline.product_id.seller_idselse1,
                    'min_qty':0.0,
                    'price':price,
                    'currency_id':currency.id,
                    'delay':0,
                }
                #Incasetheorderpartnerisacontactaddress,anewsupplierinfoiscreatedon
                #theparentcompany.Inthiscase,wekeeptheproductnameandcode.
                seller=line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_orderandline.order_id.date_order.date(),
                    uom_id=line.product_uom)
                ifseller:
                    supplierinfo['product_name']=seller.product_name
                    supplierinfo['product_code']=seller.product_code
                vals={
                    'seller_ids':[(0,0,supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                exceptAccessError: #nowriteaccessrights->justignore
                    break

    defaction_create_invoice(self):
        """CreatetheinvoiceassociatedtothePO.
        """
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')

        #1)Prepareinvoicevalsandclean-upthesectionlines
        invoice_vals_list=[]
        sequence=10
        fororderinself:
            iforder.invoice_status!='toinvoice':
                continue

            order=order.with_company(order.company_id)
            pending_section=None
            #Invoicevalues.
            invoice_vals=order._prepare_invoice()
            #Invoicelinevalues(keeponlynecessarysections).
            forlineinorder.order_line:
                ifline.display_type=='line_section':
                    pending_section=line
                    continue
                ifnotfloat_is_zero(line.qty_to_invoice,precision_digits=precision):
                    ifpending_section:
                        line_vals=pending_section._prepare_account_move_line()
                        line_vals.update({'sequence':sequence})
                        invoice_vals['invoice_line_ids'].append((0,0,line_vals))
                        sequence+=1
                        pending_section=None
                    line_vals=line._prepare_account_move_line()
                    line_vals.update({'sequence':sequence})
                    invoice_vals['invoice_line_ids'].append((0,0,line_vals))
                    sequence+=1
            invoice_vals_list.append(invoice_vals)

        ifnotinvoice_vals_list:
            raiseUserError(_('Thereisnoinvoiceableline.Ifaproducthasacontrolpolicybasedonreceivedquantity,pleasemakesurethataquantityhasbeenreceived.'))

        #2)groupby(company_id,partner_id,currency_id)forbatchcreation
        new_invoice_vals_list=[]
        forgrouping_keys,invoicesingroupby(invoice_vals_list,key=lambdax:(x.get('company_id'),x.get('partner_id'),x.get('currency_id'))):
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
        moves=self.env['account.move']
        AccountMove=self.env['account.move'].with_context(default_move_type='in_invoice')
        forvalsininvoice_vals_list:
            moves|=AccountMove.with_company(vals['company_id']).create(vals)

        #4)Somemovesmightactuallyberefunds:convertthemifthetotalamountisnegative
        #Wedothisafterthemoveshavebeencreatedsinceweneedtaxes,etc.toknowifthetotal
        #isactuallynegativeornot
        moves.filtered(lambdam:m.currency_id.round(m.amount_total)<0).action_switch_invoice_into_refund_credit_note()

        returnself.action_view_invoice(moves)

    def_prepare_invoice(self):
        """Preparethedictofvaluestocreatethenewinvoiceforapurchaseorder.
        """
        self.ensure_one()
        move_type=self._context.get('default_move_type','in_invoice')
        journal=self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        ifnotjournal:
            raiseUserError(_('Pleasedefineanaccountingpurchasejournalforthecompany%s(%s).')%(self.company_id.name,self.company_id.id))

        partner_invoice_id=self.partner_id.address_get(['invoice'])['invoice']
        partner_bank_id=self.partner_id.commercial_partner_id.bank_ids.filtered_domain(['|',('company_id','=',False),('company_id','=',self.company_id.id)])[:1]
        invoice_vals={
            'ref':self.partner_refor'',
            'move_type':move_type,
            'narration':self.notes,
            'currency_id':self.currency_id.id,
            'invoice_user_id':self.user_idandself.user_id.idorself.env.user.id,
            'partner_id':partner_invoice_id,
            'fiscal_position_id':(self.fiscal_position_idorself.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference':self.partner_refor'',
            'partner_bank_id':partner_bank_id.id,
            'invoice_origin':self.name,
            'invoice_payment_term_id':self.payment_term_id.id,
            'invoice_line_ids':[],
            'company_id':self.company_id.id,
        }
        returninvoice_vals

    defaction_view_invoice(self,invoices=False):
        """Thisfunctionreturnsanactionthatdisplayexistingvendorbillsof
        givenpurchaseorderids.Whenonlyonefound,showthevendorbill
        immediately.
        """
        ifnotinvoices:
            #Invoice_idsmaybefiltereddependingontheuser.Toensurewegetall
            #invoicesrelatedtothepurchaseorder,wereadtheminsudotofillthe
            #cache.
            self.sudo()._read(['invoice_ids'])
            invoices=self.invoice_ids

        result=self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        #choosetheview_modeaccordingly
        iflen(invoices)>1:
            result['domain']=[('id','in',invoices.ids)]
        eliflen(invoices)==1:
            res=self.env.ref('account.view_move_form',False)
            form_view=[(resandres.idorFalse,'form')]
            if'views'inresult:
                result['views']=form_view+[(state,view)forstate,viewinresult['views']ifview!='form']
            else:
                result['views']=form_view
            result['res_id']=invoices.id
        else:
            result={'type':'ir.actions.act_window_close'}

        returnresult

    @api.model
    defretrieve_dashboard(self):
        """Thisfunctionreturnsthevaluestopopulatethecustomdashboardin
            thepurchaseorderviews.
        """
        self.check_access_rights('read')

        result={
            'all_to_send':0,
            'all_waiting':0,
            'all_late':0,
            'my_to_send':0,
            'my_waiting':0,
            'my_late':0,
            'all_avg_order_value':0,
            'all_avg_days_to_purchase':0,
            'all_total_last_7_days':0,
            'all_sent_rfqs':0,
            'company_currency_symbol':self.env.company.currency_id.symbol
        }

        one_week_ago=fields.Datetime.to_string(fields.Datetime.now()-relativedelta(days=7))

        #Getlistoftranslationvalues
        Translation=self.env['ir.translation']
        list_old_value_char=[]
        list_new_value_char=[]
        field_name='ir.model.fields.selection,name'
        forlanginself.env['res.lang'].search_read([],['code']):
            list_old_value_char.append(Translation._get_source(field_name,'model',lang['code'],source='RFQ'))
            list_new_value_char.append(Translation._get_source(field_name,'model',lang['code'],source='RFQSent'))

        #Thisqueryisbrittlesinceitdependsonthelabelvaluesofaselectionfield
        #notchanging,butwedon'thaveadirecttimetrackerofwhenastatechanges
        query="""SELECTCOUNT(1)
                   FROMmail_tracking_valuev
                   LEFTJOINmail_messagemON(v.mail_message_id=m.id)
                   JOINpurchase_orderpoON(po.id=m.res_id)
                   WHEREm.create_date>=%s
                     ANDm.model='purchase.order'
                     ANDm.message_type='notification'
                     ANDv.old_value_charIN%s
                     ANDv.new_value_charIN%s
                     ANDpo.company_id=%s;
                """

        self.env.cr.execute(query,(one_week_ago,tuple(list_old_value_char),tuple(list_new_value_char),self.env.company.id))
        res=self.env.cr.fetchone()
        result['all_sent_rfqs']=res[0]or0

        #easycounts
        po=self.env['purchase.order']
        result['all_to_send']=po.search_count([('state','=','draft')])
        result['my_to_send']=po.search_count([('state','=','draft'),('user_id','=',self.env.uid)])
        result['all_waiting']=po.search_count([('state','=','sent'),('date_order','>=',fields.Datetime.now())])
        result['my_waiting']=po.search_count([('state','=','sent'),('date_order','>=',fields.Datetime.now()),('user_id','=',self.env.uid)])
        result['all_late']=po.search_count([('state','in',['draft','sent','toapprove']),('date_order','<',fields.Datetime.now())])
        result['my_late']=po.search_count([('state','in',['draft','sent','toapprove']),('date_order','<',fields.Datetime.now()),('user_id','=',self.env.uid)])

        #Calculatedvalues('avgordervalue','avgdaystopurchase',and'totallast7days')notethat'avgordervalue'and
        #'totallast7days'takesintoaccountexchangerateandcurrentcompany'scurrency'sprecision.Minofcurrencyprecision
        #istakentoeasilyextractitfromquery.
        #ThisisdoneviaSQLforscalabilityreasons
        query="""SELECTAVG(COALESCE(po.amount_total/NULLIF(po.currency_rate,0),po.amount_total)),
                          AVG(extract(epochfromage(po.date_approve,po.create_date)/(24*60*60)::decimal(16,2))),
                          SUM(CASEWHENpo.date_approve>=%sTHENCOALESCE(po.amount_total/NULLIF(po.currency_rate,0),po.amount_total)ELSE0END)
                   FROMpurchase_orderpo
                   JOINres_companycompON(po.company_id=comp.id)
                   WHEREpo.statein('purchase','done')
                     ANDpo.company_id=%s
                """
        self._cr.execute(query,(one_week_ago,self.env.company.id))
        res=self.env.cr.fetchone()
        result['all_avg_days_to_purchase']=round(res[1]or0,2)
        currency=self.env.company.currency_id
        result['all_avg_order_value']=format_amount(self.env,res[0]or0,currency)
        result['all_total_last_7_days']=format_amount(self.env,res[2]or0,currency)

        returnresult

    def_send_reminder_mail(self,send_single=False):
        ifnotself.user_has_groups('purchase.group_send_reminder'):
            return

        template=self.env.ref('purchase.email_template_edi_purchase_reminder',raise_if_not_found=False)
        iftemplate:
            orders=selfifsend_singleelseself._get_orders_to_remind()
            fororderinorders:
                date=order.date_planned
                ifdateand(send_singleor(date-relativedelta(days=order.reminder_date_before_receipt)).date()==datetime.today().date()):
                    order.with_context(is_reminder=True).message_post_with_template(template.id,email_layout_xmlid="mail.mail_notification_paynow",composition_mode='comment')

    defsend_reminder_preview(self):
        self.ensure_one()
        ifnotself.user_has_groups('purchase.group_send_reminder'):
            return

        template=self.env.ref('purchase.email_template_edi_purchase_reminder',raise_if_not_found=False)
        iftemplateandself.env.user.emailandself.id:
            template.with_context(is_reminder=True).send_mail(
                self.id,
                force_send=True,
                raise_exception=False,
                email_values={'email_to':self.env.user.email,'recipient_ids':[]},
                notif_layout="mail.mail_notification_paynow")
            return{'toast_message':_("Asampleemailhasbeensentto%s.")%self.env.user.email}

    @api.model
    def_get_orders_to_remind(self):
        """Whenautosendingaremindermail,onlysendforunconfirmedpurchase
        orderandnotallproductsareservice."""
        returnself.search([
            ('receipt_reminder_email','=',True),
            ('state','in',['purchase','done']),
            ('mail_reminder_confirmed','=',False)
        ]).filtered(lambdap:p.mapped('order_line.product_id.product_tmpl_id.type')!=['service'])

    defget_confirm_url(self,confirm_type=None):
        """Createurlforconfirmreminderorpurchasereceptionemailforsending
        inmail."""
        ifconfirm_typein['reminder','reception']:
            param=url_encode({
                'confirm':confirm_type,
                'confirmed_date':self.date_plannedandself.date_planned.date(),
            })
            returnself.get_portal_url(query_string='&%s'%param)
        returnself.get_portal_url()

    defget_update_url(self):
        """Createportalurlforusertoupdatethescheduleddateonpurchase
        orderlines."""
        update_param=url_encode({'update':'True'})
        returnself.get_portal_url(query_string='&%s'%update_param)

    defconfirm_reminder_mail(self,confirmed_date=False):
        fororderinself:
            iforder.statein['purchase','done']andnotorder.mail_reminder_confirmed:
                order.mail_reminder_confirmed=True
                date=confirmed_dateorself.date_planned.date()
                order.message_post(body=_("%(name)sconfirmedthereceiptwilltakeplaceon%(date)s.",name=order.partner_id.name,date=date))

    def_approval_allowed(self):
        """Returnswhethertheorderqualifiestobeapprovedbythecurrentuser"""
        self.ensure_one()
        return(
            self.company_id.po_double_validation=='one_step'
            or(self.company_id.po_double_validation=='two_step'
                andself.amount_total<self.env.company.currency_id._convert(
                    self.company_id.po_double_validation_amount,self.currency_id,self.company_id,
                    self.date_orderorfields.Date.today()))
            orself.user_has_groups('purchase.group_purchase_manager'))

    def_confirm_reception_mail(self):
        fororderinself:
            iforder.statein['purchase','done']andnotorder.mail_reception_confirmed:
                order.mail_reception_confirmed=True
                order.message_post(body=_("Theorderreceipthasbeenacknowledgedby%(name)s.",name=order.partner_id.name))

    def_update_date_planned_for_lines(self,updated_dates):
        #createorupdatetheactivity
        activity=self.env['mail.activity'].search([
            ('summary','=',_('DateUpdated')),
            ('res_model_id','=','purchase.order'),
            ('res_id','=',self.id),
            ('user_id','=',self.user_id.id)],limit=1)
        ifactivity:
            self._update_update_date_activity(updated_dates,activity)
        else:
            self._create_update_date_activity(updated_dates)

        #updatethedateonPOline
        forline,dateinupdated_dates:
            line._update_date_planned(date)

    def_create_update_date_activity(self,updated_dates):
        note=_('<p>%smodifiedreceiptdatesforthefollowingproducts:</p>')%self.partner_id.name
        forline,dateinupdated_dates:
            note+=_('<p>&nbsp;-%sfrom%sto%s</p>')%(line.product_id.display_name,line.date_planned.date(),date.date())
        activity=self.activity_schedule(
            'mail.mail_activity_data_warning',
            summary=_("DateUpdated"),
            user_id=self.user_id.id
        )
        #addthenoteafterweposttheactivitybecausethenotecanbesoon
        #changedwhenupdatingthedateofthenextPOline.Soinsteadof
        #sendingamailwithincompletenote,wesendonewithnonote.
        activity.note=note
        returnactivity

    def_update_update_date_activity(self,updated_dates,activity):
        forline,dateinupdated_dates:
            activity.note+=_('<p>&nbsp;-%sfrom%sto%s</p>')%(line.product_id.display_name,line.date_planned.date(),date.date())

    def_write_partner_values(self,vals):
        partner_values={}
        if'receipt_reminder_email'invals:
            partner_values['receipt_reminder_email']=vals.pop('receipt_reminder_email')
        if'reminder_date_before_receipt'invals:
            partner_values['reminder_date_before_receipt']=vals.pop('reminder_date_before_receipt')
        returnvals,partner_values


classPurchaseOrderLine(models.Model):
    _name='purchase.order.line'
    _description='PurchaseOrderLine'
    _order='order_id,sequence,id'

    name=fields.Text(string='Description',required=True)
    sequence=fields.Integer(string='Sequence',default=10)
    product_qty=fields.Float(string='Quantity',digits='ProductUnitofMeasure',required=True)
    product_uom_qty=fields.Float(string='TotalQuantity',compute='_compute_product_uom_qty',store=True)
    date_planned=fields.Datetime(string='DeliveryDate',index=True,
        help="Deliverydateexpectedfromvendor.Thisdaterespectivelydefaultstovendorpricelistleadtimethentoday'sdate.")
    taxes_id=fields.Many2many('account.tax',string='Taxes',domain=['|',('active','=',False),('active','=',True)])
    product_uom=fields.Many2one('uom.uom',string='UnitofMeasure',domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id')
    product_id=fields.Many2one('product.product',string='Product',domain=[('purchase_ok','=',True)],change_default=True)
    product_type=fields.Selection(related='product_id.type',readonly=True)
    price_unit=fields.Float(string='UnitPrice',required=True,digits='ProductPrice')

    price_subtotal=fields.Monetary(compute='_compute_amount',string='Subtotal',store=True)
    price_total=fields.Monetary(compute='_compute_amount',string='Total',store=True)
    price_tax=fields.Float(compute='_compute_amount',string='Tax',store=True)

    order_id=fields.Many2one('purchase.order',string='OrderReference',index=True,required=True,ondelete='cascade')
    account_analytic_id=fields.Many2one('account.analytic.account',store=True,string='AnalyticAccount',compute='_compute_account_analytic_id',readonly=False)
    analytic_tag_ids=fields.Many2many('account.analytic.tag',store=True,string='AnalyticTags',compute='_compute_analytic_tag_ids',readonly=False)
    company_id=fields.Many2one('res.company',related='order_id.company_id',string='Company',store=True,readonly=True)
    state=fields.Selection(related='order_id.state',store=True,readonly=False)

    invoice_lines=fields.One2many('account.move.line','purchase_line_id',string="BillLines",readonly=True,copy=False)

    #ReplacebyinvoicedQty
    qty_invoiced=fields.Float(compute='_compute_qty_invoiced',string="BilledQty",digits='ProductUnitofMeasure',store=True)

    qty_received_method=fields.Selection([('manual','Manual')],string="ReceivedQtyMethod",compute='_compute_qty_received_method',store=True,
        help="Accordingtoproductconfiguration,thereceivedquantitycanbeautomaticallycomputedbymechanism:\n"
             " -Manual:thequantityissetmanuallyontheline\n"
             " -StockMoves:thequantitycomesfromconfirmedpickings\n")
    qty_received=fields.Float("ReceivedQty",compute='_compute_qty_received',inverse='_inverse_qty_received',compute_sudo=True,store=True,digits='ProductUnitofMeasure')
    qty_received_manual=fields.Float("ManualReceivedQty",digits='ProductUnitofMeasure',copy=False)
    qty_to_invoice=fields.Float(compute='_compute_qty_invoiced',string='ToInvoiceQuantity',store=True,readonly=True,
                                  digits='ProductUnitofMeasure')

    partner_id=fields.Many2one('res.partner',related='order_id.partner_id',string='Partner',readonly=True,store=True)
    currency_id=fields.Many2one(related='order_id.currency_id',store=True,string='Currency',readonly=True)
    date_order=fields.Datetime(related='order_id.date_order',string='OrderDate',readonly=True)

    display_type=fields.Selection([
        ('line_section',"Section"),
        ('line_note',"Note")],default=False,help="TechnicalfieldforUXpurpose.")

    _sql_constraints=[
        ('accountable_required_fields',
            "CHECK(display_typeISNOTNULLOR(product_idISNOTNULLANDproduct_uomISNOTNULLANDdate_plannedISNOTNULL))",
            "Missingrequiredfieldsonaccountablepurchaseorderline."),
        ('non_accountable_null_fields',
            "CHECK(display_typeISNULLOR(product_idISNULLANDprice_unit=0ANDproduct_uom_qty=0ANDproduct_uomISNULLANDdate_plannedisNULL))",
            "Forbiddenvaluesonnon-accountablepurchaseorderline"),
    ]

    @api.depends('product_qty','price_unit','taxes_id')
    def_compute_amount(self):
        forlineinself:
            vals=line._prepare_compute_all_values()
            taxes=line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax':sum(t.get('amount',0.0)fortintaxes.get('taxes',[])),
                'price_total':taxes['total_included'],
                'price_subtotal':taxes['total_excluded'],
            })

    def_prepare_compute_all_values(self):
        #Hookmethodtoreturnsthedifferentargumentvaluesforthe
        #compute_allmethod,duetothefactthatdiscountsmechanism
        #isnotimplementedyetonthepurchaseorders.
        #Thismethodshoulddisappearassoonasthisfeatureis
        #alsointroducedlikeinthesalesmodule.
        self.ensure_one()
        return{
            'price_unit':self.price_unit,
            'currency_id':self.order_id.currency_id,
            'product_qty':self.product_qty,
            'product':self.product_id,
            'partner':self.order_id.partner_id,
        }

    def_compute_tax_id(self):
        forlineinself:
            line=line.with_company(line.company_id)
            fpos=line.order_id.fiscal_position_idorline.order_id.fiscal_position_id.get_fiscal_position(line.order_id.partner_id.id)
            #filtertaxesbycompany
            taxes=line.product_id.supplier_taxes_id.filtered(lambdar:r.company_id==line.env.company)
            line.taxes_id=fpos.map_tax(taxes,line.product_id,line.order_id.partner_id)

    @api.depends('invoice_lines.move_id.state','invoice_lines.quantity','qty_received','product_uom_qty','order_id.state')
    def_compute_qty_invoiced(self):
        forlineinself:
            #computeqty_invoiced
            qty=0.0
            forinv_lineinline.invoice_lines:
                ifinv_line.move_id.statenotin['cancel']:
                    ifinv_line.move_id.move_type=='in_invoice':
                        qty+=inv_line.product_uom_id._compute_quantity(inv_line.quantity,line.product_uom)
                    elifinv_line.move_id.move_type=='in_refund':
                        qty-=inv_line.product_uom_id._compute_quantity(inv_line.quantity,line.product_uom)
            line.qty_invoiced=qty

            #computeqty_to_invoice
            ifline.order_id.statein['purchase','done']:
                ifline.product_id.purchase_method=='purchase':
                    line.qty_to_invoice=line.product_qty-line.qty_invoiced
                else:
                    line.qty_to_invoice=line.qty_received-line.qty_invoiced
            else:
                line.qty_to_invoice=0

    @api.depends('product_id','product_id.type')
    def_compute_qty_received_method(self):
        forlineinself:
            ifline.product_idandline.product_id.typein['consu','service']:
                line.qty_received_method='manual'
            else:
                line.qty_received_method=False

    @api.depends('qty_received_method','qty_received_manual')
    def_compute_qty_received(self):
        forlineinself:
            ifline.qty_received_method=='manual':
                line.qty_received=line.qty_received_manualor0.0
            else:
                line.qty_received=0.0

    @api.onchange('qty_received')
    def_inverse_qty_received(self):
        """Whenwritingonqty_received,ifthevalueshouldbemodifymanually(`qty_received_method`='manual'only),
            thenweputthevaluein`qty_received_manual`.Otherwise,`qty_received_manual`shouldbeFalsesincethe
            receivedqtyisautomaticallycomputebyothermecanisms.
        """
        forlineinself:
            ifline.qty_received_method=='manual':
                line.qty_received_manual=line.qty_received
            else:
                line.qty_received_manual=0.0

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            ifvalues.get('display_type',self.default_get(['display_type'])['display_type']):
                values.update(product_id=False,price_unit=0,product_uom_qty=0,product_uom=False,date_planned=False)
            else:
                values.update(self._prepare_add_missing_fields(values))

        lines=super().create(vals_list)
        forlineinlines:
            ifline.product_idandline.order_id.state=='purchase':
                msg=_("Extralinewith%s")%(line.product_id.display_name,)
                line.order_id.message_post(body=msg)
        returnlines

    defwrite(self,values):
        if'display_type'invaluesandself.filtered(lambdaline:line.display_type!=values.get('display_type')):
            raiseUserError(_("Youcannotchangethetypeofapurchaseorderline.Insteadyoushoulddeletethecurrentlineandcreateanewlineofthepropertype."))

        if'product_qty'invalues:
            forlineinself:
                ifline.order_id.state=='purchase':
                    line.order_id.message_post_with_view('purchase.track_po_line_template',
                                                         values={'line':line,'product_qty':values['product_qty']},
                                                         subtype_id=self.env.ref('mail.mt_note').id)
        if'qty_received'invalues:
            forlineinself:
                line._track_qty_received(values['qty_received'])
        returnsuper(PurchaseOrderLine,self).write(values)

    defunlink(self):
        forlineinself:
            ifline.order_id.statein['purchase','done']:
                raiseUserError(_('Cannotdeleteapurchaseorderlinewhichisinstate\'%s\'.')%(line.state,))
        returnsuper(PurchaseOrderLine,self).unlink()

    @api.model
    def_get_date_planned(self,seller,po=False):
        """ReturnthedatetimevaluetouseasScheduleDate(``date_planned``)for
           POLinesthatcorrespondtothegivenproduct.seller_ids,
           whenorderedat`date_order_str`.

           :paramModelseller:usedtofetchthedeliverydelay(ifnoseller
                                isprovided,thedelayis0)
           :paramModelpo:purchase.order,necessaryonlyifthePOlineis
                            notyetattachedtoaPO.
           :rtype:datetime
           :return:desiredScheduleDateforthePOline
        """
        date_order=po.date_orderifpoelseself.order_id.date_order
        ifdate_order:
            date_planned=date_order+relativedelta(days=seller.delayifsellerelse0)
        else:
            date_planned=datetime.today()+relativedelta(days=seller.delayifsellerelse0)
        returnself._convert_to_middle_of_day(date_planned)

    @api.depends('product_id','date_order')
    def_compute_account_analytic_id(self):
        forrecinself:
            ifnotrec.display_type:
                default_analytic_account=rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.order_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.date_order,
                    company_id=rec.company_id.id,
                )
                ifdefault_analytic_account:
                    rec.account_analytic_id=default_analytic_account.analytic_id

    @api.depends('product_id','date_order')
    def_compute_analytic_tag_ids(self):
        forrecinself:
            ifnotrec.display_type:
                default_analytic_account=rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.order_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.date_order,
                    company_id=rec.company_id.id,
                )
                ifdefault_analytic_account:
                    rec.analytic_tag_ids=default_analytic_account.analytic_tag_ids

    @api.onchange('product_id','company_id')
    defonchange_product_id(self):
        ifnotself.product_idornotself.company_id:
            return

        #Resetdate,priceandquantitysince_onchange_quantitywillprovidedefaultvalues
        self.price_unit=self.product_qty=0.0

        self._product_id_change()

        self._suggest_quantity()
        self._onchange_quantity()

    def_product_id_change(self):
        ifnotself.product_id:
            return

        self.product_uom=self.product_id.uom_po_idorself.product_id.uom_id
        product_lang=self.product_id.with_context(
            lang=get_lang(self.env,self.partner_id.lang).code,
            partner_id=self.partner_id.id,
            company_id=self.company_id.id,
        )
        self.name=self._get_product_purchase_description(product_lang)

        self._compute_tax_id()

    @api.onchange('product_id')
    defonchange_product_id_warning(self):
        ifnotself.product_idornotself.env.user.has_group('purchase.group_warning_purchase'):
            return
        warning={}
        title=False
        message=False

        product_info=self.product_id

        ifproduct_info.purchase_line_warn!='no-message':
            title=_("Warningfor%s",product_info.name)
            message=product_info.purchase_line_warn_msg
            warning['title']=title
            warning['message']=message
            ifproduct_info.purchase_line_warn=='block':
                self.product_id=False
            return{'warning':warning}
        return{}

    @api.onchange('product_qty','product_uom','company_id')
    def_onchange_quantity(self):
        ifnotself.product_idorself.invoice_linesornotself.company_id:
            return
        params={'order_id':self.order_id}
        seller=self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_orderandself.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        ifsellerornotself.date_planned:
            self.date_planned=self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        #Ifnotseller,usethestandardprice.Itneedsapropercurrencyconversion.
        ifnotseller:
            po_line_uom=self.product_uomorself.product_id.uom_po_id
            price_unit=self.env['account.tax']._fix_tax_included_price_company(
                self.product_id.uom_id._compute_price(self.product_id.standard_price,po_line_uom),
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            ifprice_unitandself.order_id.currency_idandself.order_id.company_id.currency_id!=self.order_id.currency_id:
                price_unit=self.order_id.company_id.currency_id._convert(
                    price_unit,
                    self.order_id.currency_id,
                    self.order_id.company_id,
                    self.date_orderorfields.Date.today(),
                )

            self.price_unit=price_unit
            return

        price_unit=self.env['account.tax']._fix_tax_included_price_company(seller.price,self.product_id.supplier_taxes_id,self.taxes_id,self.company_id)ifsellerelse0.0
        ifprice_unitandsellerandself.order_id.currency_idandseller.currency_id!=self.order_id.currency_id:
            price_unit=seller.currency_id._convert(
                price_unit,self.order_id.currency_id,self.order_id.company_id,self.date_orderorfields.Date.today())

        ifsellerandself.product_uomandseller.product_uom!=self.product_uom:
            price_unit=seller.product_uom._compute_price(price_unit,self.product_uom)

        self.price_unit=price_unit

        default_names=[]
        vendors=self.product_id._prepare_sellers({})
        forvendorinvendors:
            product_ctx={'seller_id':vendor.id,'lang':get_lang(self.env,self.partner_id.lang).code}
            default_names.append(self._get_product_purchase_description(self.product_id.with_context(product_ctx)))

        if(self.nameindefault_namesornotself.name):
            product_ctx={'seller_id':seller.id,'lang':get_lang(self.env,self.partner_id.lang).code}
            self.name=self._get_product_purchase_description(self.product_id.with_context(product_ctx))

    @api.depends('product_uom','product_qty','product_id.uom_id')
    def_compute_product_uom_qty(self):
        forlineinself:
            ifline.product_idandline.product_id.uom_id!=line.product_uom:
                line.product_uom_qty=line.product_uom._compute_quantity(line.product_qty,line.product_id.uom_id)
            else:
                line.product_uom_qty=line.product_qty

    def_suggest_quantity(self):
        '''
        Suggestaminimalquantitybasedontheseller
        '''
        ifnotself.product_id:
            return
        seller_min_qty=self.product_id.seller_ids\
            .filtered(lambdar:r.name==self.order_id.partner_idand(notr.product_idorr.product_id==self.product_id))\
            .sorted(key=lambdar:r.min_qty)
        ifseller_min_qty:
            self.product_qty=seller_min_qty[0].min_qtyor1.0
            self.product_uom=seller_min_qty[0].product_uom
        else:
            self.product_qty=1.0

    def_get_product_purchase_description(self,product_lang):
        self.ensure_one()
        name=product_lang.display_name
        ifproduct_lang.description_purchase:
            name+='\n'+product_lang.description_purchase

        returnname

    def_prepare_account_move_line(self,move=False):
        self.ensure_one()
        aml_currency=moveandmove.currency_idorself.currency_id
        date=moveandmove.dateorfields.Date.today()
        res={
            'display_type':self.display_type,
            'sequence':self.sequence,
            'name':'%s:%s'%(self.order_id.name,self.name),
            'product_id':self.product_id.id,
            'product_uom_id':self.product_uom.id,
            'quantity':self.qty_to_invoice,
            'price_unit':self.currency_id._convert(self.price_unit,aml_currency,self.company_id,date,round=False),
            'tax_ids':[(6,0,self.taxes_id.ids)],
            'analytic_account_id':self.account_analytic_id.id,
            'analytic_tag_ids':[(6,0,self.analytic_tag_ids.ids)],
            'purchase_line_id':self.id,
        }
        ifnotmove:
            returnres

        ifself.currency_id==move.company_id.currency_id:
            currency=False
        else:
            currency=move.currency_id

        res.update({
            'move_id':move.id,
            'currency_id':currencyandcurrency.idorFalse,
            'date_maturity':move.invoice_date_due,
            'partner_id':move.partner_id.id,
        })
        returnres

    @api.model
    def_prepare_add_missing_fields(self,values):
        """Deducemissingrequiredfieldsfromtheonchange"""
        res={}
        onchange_fields=['name','price_unit','product_qty','product_uom','taxes_id','date_planned']
        ifvalues.get('order_id')andvalues.get('product_id')andany(fnotinvaluesforfinonchange_fields):
            line=self.new(values)
            line.onchange_product_id()
            forfieldinonchange_fields:
                iffieldnotinvalues:
                    res[field]=line._fields[field].convert_to_write(line[field],line)
        returnres

    @api.model
    def_prepare_purchase_order_line(self,product_id,product_qty,product_uom,company_id,supplier,po):
        partner=supplier.name
        uom_po_qty=product_uom._compute_quantity(product_qty,product_id.uom_po_id)
        #_select_sellerisusedifthesupplierhavedifferentpricedepending
        #thequantitiesordered.
        today=fields.Date.today()
        seller=product_id.with_company(company_id)._select_seller(
            partner_id=partner,
            quantity=uom_po_qty,
            date=po.date_orderandmax(po.date_order.date(),today)ortoday,
            uom_id=product_id.uom_po_id)

        taxes=product_id.supplier_taxes_id
        fpos=po.fiscal_position_id
        taxes_id=fpos.map_tax(taxes,product_id,seller.name)
        iftaxes_id:
            taxes_id=taxes_id.filtered(lambdax:x.company_id.id==company_id.id)

        price_unit=self.env['account.tax']._fix_tax_included_price_company(seller.price,product_id.supplier_taxes_id,taxes_id,company_id)ifsellerelse0.0
        ifprice_unitandsellerandpo.currency_idandseller.currency_id!=po.currency_id:
            price_unit=seller.currency_id._convert(
                price_unit,po.currency_id,po.company_id,po.date_orderorfields.Date.today())

        product_lang=product_id.with_prefetch().with_context(
            lang=partner.lang,
            partner_id=partner.id,
        )
        name=product_lang.with_context(seller_id=seller.id).display_name
        ifproduct_lang.description_purchase:
            name+='\n'+product_lang.description_purchase

        date_planned=self.order_id.date_plannedorself._get_date_planned(seller,po=po)

        return{
            'name':name,
            'product_qty':uom_po_qty,
            'product_id':product_id.id,
            'product_uom':product_id.uom_po_id.id,
            'price_unit':price_unit,
            'date_planned':date_planned,
            'taxes_id':[(6,0,taxes_id.ids)],
            'order_id':po.id,
        }

    def_convert_to_middle_of_day(self,date):
        """Returnadatetimewhichisthenoonoftheinputdate(time)according
        toorderuser'stimezone,converttoUTCtime.
        """
        tz=timezone(self.order_id.user_id.tzorself.company_id.partner_id.tzor'UTC')
        date=date.astimezone(tz)#dateisUTC,applyingtheoffsetcouldchangetheday
        returntz.localize(datetime.combine(date,time(12))).astimezone(UTC).replace(tzinfo=None)

    def_update_date_planned(self,updated_date):
        self.date_planned=updated_date

    def_track_qty_received(self,new_qty):
        self.ensure_one()
        ifnew_qty!=self.qty_receivedandself.order_id.state=='purchase':
            self.order_id.message_post_with_view(
                'purchase.track_po_line_qty_received_template',
                values={'line':self,'qty_received':new_qty},
                subtype_id=self.env.ref('mail.mt_note').id
            )
