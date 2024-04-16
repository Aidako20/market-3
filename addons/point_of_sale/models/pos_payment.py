fromflectraimportapi,fields,models,_
fromflectra.toolsimportformatLang
fromflectra.exceptionsimportValidationError


classPosPayment(models.Model):
    """Usedtoregisterpaymentsmadeinapos.order.

    See`payment_ids`fieldofpos.ordermodel.
    Themaincharacteristicsofpos.paymentcanbereadfrom
    `payment_method_id`.
    """

    _name="pos.payment"
    _description="PointofSalePayments"
    _order="iddesc"

    name=fields.Char(string='Label',readonly=True)
    pos_order_id=fields.Many2one('pos.order',string='Order',required=True)
    amount=fields.Monetary(string='Amount',required=True,currency_field='currency_id',readonly=True,help="Totalamountofthepayment.")
    payment_method_id=fields.Many2one('pos.payment.method',string='PaymentMethod',required=True)
    payment_date=fields.Datetime(string='Date',required=True,readonly=True,default=lambdaself:fields.Datetime.now())
    currency_id=fields.Many2one('res.currency',string='Currency',related='pos_order_id.currency_id')
    currency_rate=fields.Float(string='ConversionRate',related='pos_order_id.currency_rate',help='Conversionratefromcompanycurrencytoordercurrency.')
    partner_id=fields.Many2one('res.partner',string='Customer',related='pos_order_id.partner_id')
    session_id=fields.Many2one('pos.session',string='Session',related='pos_order_id.session_id',store=True,index=True)
    company_id=fields.Many2one('res.company',string='Company',related='pos_order_id.company_id') #TODO:addstore=Trueinmaster
    card_type=fields.Char('Typeofcardused')
    cardholder_name=fields.Char('CardholderName')
    transaction_id=fields.Char('PaymentTransactionID')
    payment_status=fields.Char('PaymentStatus')
    ticket=fields.Char('PaymentReceiptInfo')
    is_change=fields.Boolean(string='Isthispaymentchange?',default=False)

    defname_get(self):
        res=[]
        forpaymentinself:
            ifpayment.name:
                res.append((payment.id,'%s%s'%(payment.name,formatLang(self.env,payment.amount,currency_obj=payment.currency_id))))
            else:
                res.append((payment.id,formatLang(self.env,payment.amount,currency_obj=payment.currency_id)))
        returnres

    @api.constrains('payment_method_id')
    def_check_payment_method_id(self):
        forpaymentinself:
            ifpayment.payment_method_idnotinpayment.session_id.config_id.payment_method_ids:
                raiseValidationError(_('ThepaymentmethodselectedisnotallowedintheconfigofthePOSsession.'))

    def_export_for_ui(self,payment):
        return{
            'payment_method_id':payment.payment_method_id.id,
            'amount':payment.amount,
            'payment_status':payment.payment_status,
            'card_type':payment.card_type,
            'cardholder_name':payment.cardholder_name,
            'transaction_id':payment.transaction_id,
            'ticket':payment.ticket,
            'is_change':payment.is_change,
        }

    defexport_for_ui(self):
        returnself.mapped(self._export_for_ui)ifselfelse[]
