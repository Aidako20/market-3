#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
importre

fromflectraimportapi,fields,models,_,SUPERUSER_ID
fromflectra.toolsimportfloat_compare


_logger=logging.getLogger(__name__)


classPaymentAcquirer(models.Model):
    _inherit='payment.acquirer'

    so_reference_type=fields.Selection(string='Communication',
        selection=[
            ('so_name','BasedonDocumentReference'),
            ('partner','BasedonCustomerID')],default='so_name',
        help='Youcansetherethecommunicationtypethatwillappearonsalesorders.'
             'Thecommunicationwillbegiventothecustomerwhentheychoosethepaymentmethod.')


classPaymentTransaction(models.Model):
    _inherit='payment.transaction'

    sale_order_ids=fields.Many2many('sale.order','sale_order_transaction_rel','transaction_id','sale_order_id',
                                      string='SalesOrders',copy=False,readonly=True)
    sale_order_ids_nbr=fields.Integer(compute='_compute_sale_order_ids_nbr',string='#ofSalesOrders')

    def_compute_sale_order_reference(self,order):
        self.ensure_one()
        ifself.acquirer_id.so_reference_type=='so_name':
            returnorder.name
        else:
            #self.acquirer_id.so_reference_type=='partner'
            identification_number=order.partner_id.id
            return'%s/%s'%('CUST',str(identification_number%97).rjust(2,'0'))

    @api.depends('sale_order_ids')
    def_compute_sale_order_ids_nbr(self):
        fortransinself:
            trans.sale_order_ids_nbr=len(trans.sale_order_ids)

    def_log_payment_transaction_sent(self):
        super(PaymentTransaction,self)._log_payment_transaction_sent()
        fortransinself:
            post_message=trans._get_payment_transaction_sent_message()
            forsointrans.sale_order_ids:
                so.message_post(body=post_message)

    def_log_payment_transaction_received(self):
        super(PaymentTransaction,self)._log_payment_transaction_received()
        fortransinself.filtered(lambdat:t.providernotin('manual','transfer')):
            post_message=trans._get_payment_transaction_received_message()
            forsointrans.sale_order_ids:
                so.message_post(body=post_message)

    def_set_transaction_pending(self):
        #Overrideof'_set_transaction_pending'inthe'payment'module
        #tosentthequotationsautomatically.
        super(PaymentTransaction,self)._set_transaction_pending()

        forrecordinself:
            sales_orders=record.sale_order_ids.filtered(lambdaso:so.statein['draft','sent'])
            sales_orders.filtered(lambdaso:so.state=='draft').with_context(tracking_disable=True).write({'state':'sent'})

            ifrecord.acquirer_id.provider=='transfer':
                forsoinrecord.sale_order_ids:
                    so.reference=record._compute_sale_order_reference(so)
            #sendorderconfirmationmail
            sales_orders._send_order_confirmation_mail()

    def_check_amount_and_confirm_order(self):
        self.ensure_one()
        fororderinself.sale_order_ids.filtered(lambdaso:so.statein('draft','sent')):
            iforder.currency_id.compare_amounts(self.amount,order.amount_total)==0:
                order.with_context(send_email=True).action_confirm()
            else:
                _logger.warning(
                    '<%s>transactionAMOUNTMISMATCHfororder%s(ID%s):expected%r,got%r',
                    self.acquirer_id.provider,order.name,order.id,
                    order.amount_total,self.amount,
                )
                order.message_post(
                    subject=_("AmountMismatch(%s)",self.acquirer_id.provider),
                    body=_("Theorderwasnotconfirmeddespiteresponsefromtheacquirer(%s):ordertotalis%rbutacquirerrepliedwith%r.")%(
                        self.acquirer_id.provider,
                        order.amount_total,
                        self.amount,
                    )
                )

    def_set_transaction_authorized(self):
        #Overrideof'_set_transaction_authorized'inthe'payment'module
        #toconfirmthequotationsautomatically.
        super(PaymentTransaction,self)._set_transaction_authorized()
        sales_orders=self.mapped('sale_order_ids').filtered(lambdaso:so.statein('draft','sent'))
        fortxinself:
            tx._check_amount_and_confirm_order()

        #sendorderconfirmationmail
        sales_orders._send_order_confirmation_mail()

    def_reconcile_after_transaction_done(self):
        #Overrideof'_set_transaction_done'inthe'payment'module
        #toconfirmthequotationsautomaticallyandtogeneratetheinvoicesifneeded.
        sales_orders=self.mapped('sale_order_ids').filtered(lambdaso:so.statein('draft','sent'))
        fortxinself:
            tx._check_amount_and_confirm_order()
        #sendorderconfirmationmail
        sales_orders._send_order_confirmation_mail()
        #invoicethesaleordersifneeded
        self._invoice_sale_orders()
        res=super(PaymentTransaction,self)._reconcile_after_transaction_done()
        ifself.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice')andany(so.statein('sale','done')forsoinself.sale_order_ids):
            default_template=self.env['ir.config_parameter'].sudo().get_param('sale.default_email_template')
            ifdefault_template:
                fortransinself.filtered(lambdat:t.sale_order_ids.filtered(lambdaso:so.statein('sale','done'))):
                    trans=trans.with_company(trans.acquirer_id.company_id).with_context(
                        mark_invoice_as_sent=True,
                        company_id=trans.acquirer_id.company_id.id,
                    )
                    forinvoiceintrans.invoice_ids.with_user(SUPERUSER_ID):
                        invoice.message_post_with_template(int(default_template),email_layout_xmlid="mail.mail_notification_paynow")
        returnres

    def_invoice_sale_orders(self):
        ifself.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
            fortransinself.filtered(lambdat:t.sale_order_ids):
                trans=trans.with_company(trans.acquirer_id.company_id)\
                    .with_context(company_id=trans.acquirer_id.company_id.id)
                confirmed_orders=trans.sale_order_ids.filtered(lambdaso:so.statein('sale','done'))
                ifconfirmed_orders:
                    confirmed_orders._force_lines_to_invoice_policy_order()
                    invoices=confirmed_orders._create_invoices()
                    trans.invoice_ids=[(6,0,invoices.ids)]

    @api.model
    def_compute_reference_prefix(self,values):
        prefix=super(PaymentTransaction,self)._compute_reference_prefix(values)
        ifnotprefixandvaluesandvalues.get('sale_order_ids'):
            sale_orders=self.new({'sale_order_ids':values['sale_order_ids']}).sale_order_ids
            return','.join(sale_orders.mapped('name'))
        returnprefix

    defaction_view_sales_orders(self):
        action={
            'name':_('SalesOrder(s)'),
            'type':'ir.actions.act_window',
            'res_model':'sale.order',
            'target':'current',
        }
        sale_order_ids=self.sale_order_ids.ids
        iflen(sale_order_ids)==1:
            action['res_id']=sale_order_ids[0]
            action['view_mode']='form'
        else:
            action['view_mode']='tree,form'
            action['domain']=[('id','in',sale_order_ids)]
        returnaction

    #--------------------------------------------------
    #Toolsforpayment
    #--------------------------------------------------

    defrender_sale_button(self,order,submit_txt=None,render_values=None):
        values={
            'partner_id':order.partner_id.id,
            'type':self.type,
        }
        ifrender_values:
            values.update(render_values)
        #Notveryeleganttodothatherebutnochoiceregardingthedesign.
        self._log_payment_transaction_sent()
        returnself.acquirer_id.with_context(submit_class='btnbtn-primary',submit_txt=submit_txtor_('PayNow')).sudo().render(
            self.reference,
            order.amount_total,
            order.pricelist_id.currency_id.id,
            values=values,
        )
