#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importhashlib
importhmac

fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.toolsimportustr,consteq,float_compare


classPaymentLinkWizard(models.TransientModel):
    _name="payment.link.wizard"
    _description="GeneratePaymentLink"

    @api.model
    defdefault_get(self,fields):
        res=super(PaymentLinkWizard,self).default_get(fields)
        res_id=self._context.get('active_id')
        res_model=self._context.get('active_model')
        res.update({'res_id':res_id,'res_model':res_model})
        amount_field='amount_residual'ifres_model=='account.move'else'amount_total'
        ifres_idandres_model=='account.move':
            record=self.env[res_model].browse(res_id)
            res.update({
                'description':record.payment_reference,
                'amount':record[amount_field],
                'currency_id':record.currency_id.id,
                'partner_id':record.partner_id.id,
                'amount_max':record[amount_field],
            })
        returnres

    res_model=fields.Char('RelatedDocumentModel',required=True)
    res_id=fields.Integer('RelatedDocumentID',required=True)
    amount=fields.Monetary(currency_field='currency_id',required=True)
    amount_max=fields.Monetary(currency_field='currency_id')
    currency_id=fields.Many2one('res.currency')
    partner_id=fields.Many2one('res.partner')
    partner_email=fields.Char(related='partner_id.email')
    link=fields.Char(string='PaymentLink',compute='_compute_values')
    description=fields.Char('PaymentRef')
    access_token=fields.Char(compute='_compute_values')
    company_id=fields.Many2one('res.company',compute='_compute_company')

    @api.onchange('amount','description')
    def_onchange_amount(self):
        iffloat_compare(self.amount_max,self.amount,precision_rounding=self.currency_id.roundingor0.01)==-1:
            raiseValidationError(_("Pleasesetanamountsmallerthan%s.")%(self.amount_max))
        ifself.amount<=0:
            raiseValidationError(_("Thevalueofthepaymentamountmustbepositive."))

    @api.depends('amount','description','partner_id','currency_id')
    def_compute_values(self):
        secret=self.env['ir.config_parameter'].sudo().get_param('database.secret')
        forpayment_linkinself:
            token_str='%s%s%s'%(payment_link.partner_id.id,payment_link.amount,payment_link.currency_id.id)
            payment_link.access_token=hmac.new(secret.encode('utf-8'),token_str.encode('utf-8'),hashlib.sha256).hexdigest()
        #mustbecalledaftertokengeneration,obvsly-thelinkneedsanup-to-datetoken
        self._generate_link()

    @api.depends('res_model','res_id')
    def_compute_company(self):
        forlinkinself:
            record=self.env[link.res_model].browse(link.res_id)
            link.company_id=record.company_idif'company_id'inrecordelseFalse

    def_generate_link(self):
        forpayment_linkinself:
            record=self.env[payment_link.res_model].browse(payment_link.res_id)
            link=('%s/website_payment/pay?reference=%s&amount=%s&currency_id=%s'
                    '&partner_id=%s&access_token=%s')%(
                        record.get_base_url(),
                        urls.url_quote_plus(payment_link.description),
                        payment_link.amount,
                        payment_link.currency_id.id,
                        payment_link.partner_id.id,
                        payment_link.access_token
                    )
            ifpayment_link.company_id:
                link+='&company_id=%s'%payment_link.company_id.id
            ifpayment_link.res_model=='account.move':
                link+='&invoice_id=%s'%payment_link.res_id
            payment_link.link=link

    @api.model
    defcheck_token(self,access_token,partner_id,amount,currency_id):
        secret=self.env['ir.config_parameter'].sudo().get_param('database.secret')
        token_str='%s%s%s'%(partner_id,amount,currency_id)
        correct_token=hmac.new(secret.encode('utf-8'),token_str.encode('utf-8'),hashlib.sha256).hexdigest()
        ifconsteq(ustr(access_token),correct_token):
            returnTrue
        returnFalse