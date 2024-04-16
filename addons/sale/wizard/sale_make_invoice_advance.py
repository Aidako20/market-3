#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classSaleAdvancePaymentInv(models.TransientModel):
    _name="sale.advance.payment.inv"
    _description="SalesAdvancePaymentInvoice"

    @api.model
    def_count(self):
        returnlen(self._context.get('active_ids',[]))

    @api.model
    def_default_product_id(self):
        product_id=self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        returnself.env['product.product'].browse(int(product_id)).exists()

    @api.model
    def_default_deposit_account_id(self):
        returnself._default_product_id()._get_product_accounts()['income']

    @api.model
    def_default_deposit_taxes_id(self):
        returnself._default_product_id().taxes_id

    @api.model
    def_default_has_down_payment(self):
        ifself._context.get('active_model')=='sale.order'andself._context.get('active_id',False):
            sale_order=self.env['sale.order'].browse(self._context.get('active_id'))
            returnsale_order.order_line.filtered(
                lambdasale_order_line:sale_order_line.is_downpayment
            )

        returnFalse

    @api.model
    def_default_currency_id(self):
        ifself._context.get('active_model')=='sale.order'andself._context.get('active_id',False):
            sale_order=self.env['sale.order'].browse(self._context.get('active_id'))
            returnsale_order.currency_id

    advance_payment_method=fields.Selection([
        ('delivered','Regularinvoice'),
        ('percentage','Downpayment(percentage)'),
        ('fixed','Downpayment(fixedamount)')
        ],string='CreateInvoice',default='delivered',required=True,
        help="Astandardinvoiceisissuedwithalltheorderlinesreadyforinvoicing,\
        accordingtotheirinvoicingpolicy(basedonorderedordeliveredquantity).")
    deduct_down_payments=fields.Boolean('Deductdownpayments',default=True)
    has_down_payments=fields.Boolean('Hasdownpayments',default=_default_has_down_payment,readonly=True)
    product_id=fields.Many2one('product.product',string='DownPaymentProduct',domain=[('type','=','service')],
        default=_default_product_id)
    count=fields.Integer(default=_count,string='OrderCount')
    amount=fields.Float('DownPaymentAmount',digits='Account',help="Thepercentageofamounttobeinvoicedinadvance,taxesexcluded.")
    currency_id=fields.Many2one('res.currency',string='Currency',default=_default_currency_id)
    fixed_amount=fields.Monetary('DownPaymentAmount(Fixed)',help="Thefixedamounttobeinvoicedinadvance,taxesexcluded.")
    deposit_account_id=fields.Many2one("account.account",string="IncomeAccount",domain=[('deprecated','=',False)],
        help="Accountusedfordeposits",default=_default_deposit_account_id)
    deposit_taxes_id=fields.Many2many("account.tax",string="CustomerTaxes",help="Taxesusedfordeposits",default=_default_deposit_taxes_id)

    @api.onchange('advance_payment_method')
    defonchange_advance_payment_method(self):
        ifself.advance_payment_method=='percentage':
            amount=self.default_get(['amount']).get('amount')
            return{'value':{'amount':amount}}
        return{}

    def_prepare_invoice_values(self,order,name,amount,so_line):
        invoice_vals={
            'ref':order.client_order_ref,
            'move_type':'out_invoice',
            'invoice_origin':order.name,
            'invoice_user_id':order.user_id.id,
            'narration':order.note,
            'partner_id':order.partner_invoice_id.id,
            'fiscal_position_id':(order.fiscal_position_idororder.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id':order.partner_shipping_id.id,
            'currency_id':order.pricelist_id.currency_id.id,
            'payment_reference':order.reference,
            'invoice_payment_term_id':order.payment_term_id.id,
            'partner_bank_id':order.company_id.partner_id.bank_ids[:1].id,
            'team_id':order.team_id.id,
            'campaign_id':order.campaign_id.id,
            'medium_id':order.medium_id.id,
            'source_id':order.source_id.id,
            'invoice_line_ids':[(0,0,{
                'name':name,
                'price_unit':amount,
                'quantity':1.0,
                'product_id':self.product_id.id,
                'product_uom_id':so_line.product_uom.id,
                'tax_ids':[(6,0,so_line.tax_id.ids)],
                'sale_line_ids':[(6,0,[so_line.id])],
                'analytic_tag_ids':[(6,0,so_line.analytic_tag_ids.ids)],
                'analytic_account_id':order.analytic_account_id.idifnotso_line.display_typeandorder.analytic_account_id.idelseFalse,
            })],
        }

        returninvoice_vals

    def_get_advance_details(self,order):
        context={'lang':order.partner_id.lang}
        ifself.advance_payment_method=='percentage':
            ifall(self.product_id.taxes_id.mapped('price_include')):
                amount=order.amount_total*self.amount/100
            else:
                amount=order.amount_untaxed*self.amount/100
            name=_("Downpaymentof%s%%")%(self.amount)
        else:
            amount=self.fixed_amount
            name=_('DownPayment')
        delcontext

        returnamount,name

    def_create_invoice(self,order,so_line,amount):
        if(self.advance_payment_method=='percentage'andself.amount<=0.00)or(self.advance_payment_method=='fixed'andself.fixed_amount<=0.00):
            raiseUserError(_('Thevalueofthedownpaymentamountmustbepositive.'))

        amount,name=self._get_advance_details(order)

        invoice_vals=self._prepare_invoice_values(order,name,amount,so_line)

        iforder.fiscal_position_id:
            invoice_vals['fiscal_position_id']=order.fiscal_position_id.id

        invoice=self.env['account.move'].with_company(order.company_id)\
            .sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self':invoice,'origin':order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        returninvoice

    def_prepare_so_line(self,order,analytic_tag_ids,tax_ids,amount):
        context={'lang':order.partner_id.lang}
        so_values={
            'name':_('DownPayment:%s')%(time.strftime('%m%Y'),),
            'price_unit':amount,
            'product_uom_qty':0.0,
            'order_id':order.id,
            'discount':0.0,
            'product_uom':self.product_id.uom_id.id,
            'product_id':self.product_id.id,
            'analytic_tag_ids':analytic_tag_ids,
            'tax_id':[(6,0,tax_ids)],
            'is_downpayment':True,
            'sequence':order.order_lineandorder.order_line[-1].sequence+1or10,
        }
        delcontext
        returnso_values

    defcreate_invoices(self):
        sale_orders=self.env['sale.order'].browse(self._context.get('active_ids',[]))

        ifself.advance_payment_method=='delivered':
            sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            #Createdepositproductifnecessary
            ifnotself.product_id:
                vals=self._prepare_deposit_product()
                self.product_id=self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id',self.product_id.id)

            sale_line_obj=self.env['sale.order.line']
            fororderinsale_orders:
                amount,name=self._get_advance_details(order)

                ifself.product_id.invoice_policy!='order':
                    raiseUserError(_('Theproductusedtoinvoiceadownpaymentshouldhaveaninvoicepolicysetto"Orderedquantities".Pleaseupdateyourdepositproducttobeabletocreateadepositinvoice.'))
                ifself.product_id.type!='service':
                    raiseUserError(_("Theproductusedtoinvoiceadownpaymentshouldbeoftype'Service'.Pleaseuseanotherproductorupdatethisproduct."))
                taxes=self.product_id.taxes_id.filtered(lambdar:notorder.company_idorr.company_id==order.company_id)
                tax_ids=order.fiscal_position_id.map_tax(taxes,self.product_id,order.partner_shipping_id).ids
                analytic_tag_ids=[]
                forlineinorder.order_line:
                    analytic_tag_ids=[(4,analytic_tag.id,None)foranalytic_taginline.analytic_tag_ids]

                so_line_values=self._prepare_so_line(order,analytic_tag_ids,tax_ids,amount)
                so_line=sale_line_obj.create(so_line_values)
                self._create_invoice(order,so_line,amount)
        ifself._context.get('open_invoices',False):
            returnsale_orders.action_view_invoice()
        return{'type':'ir.actions.act_window_close'}

    def_prepare_deposit_product(self):
        return{
            'name':'Downpayment',
            'type':'service',
            'invoice_policy':'order',
            'property_account_income_id':self.deposit_account_id.id,
            'taxes_id':[(6,0,self.deposit_taxes_id.ids)],
            'company_id':False,
        }

