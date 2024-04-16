#coding:utf-8

importdatetime

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError


classAccountPayment(models.Model):
    _inherit='account.payment'

    payment_transaction_id=fields.Many2one('payment.transaction',string='PaymentTransaction',readonly=True)
    payment_token_id=fields.Many2one(
        'payment.token',string="Savedpaymenttoken",
        domain="""[
            (payment_method_code=='electronic','=',1),
            ('company_id','=',company_id),
            ('acquirer_id.capture_manually','=',False),
            ('acquirer_id.journal_id','=',journal_id),
            ('partner_id','in',related_partner_ids),
        ]""",
        help="Notethattokensfromacquirerssettoonlyauthorizetransactions(insteadofcapturingtheamount)arenotavailable.")
    related_partner_ids=fields.Many2many('res.partner',compute='_compute_related_partners',compute_sudo=True)

    def_get_payment_chatter_link(self):
        self.ensure_one()
        return'<ahref=#data-oe-model=account.paymentdata-oe-id=%d>%s</a>'%(self.id,self.name)

    @api.depends('partner_id.commercial_partner_id.child_ids')
    def_compute_related_partners(self):
        forpinself:
            p.related_partner_ids=(
                p.partner_id
              |p.partner_id.commercial_partner_id
              |p.partner_id.commercial_partner_id.child_ids
            )._origin

    @api.onchange('partner_id','payment_method_id','journal_id')
    def_onchange_set_payment_token_id(self):
        ifnot(self.payment_method_code=='electronic'andself.partner_idandself.journal_id):
            self.payment_token_id=False
            return

        self.payment_token_id=self.env['payment.token'].search([
            ('partner_id','in',self.related_partner_ids.ids),
            ('acquirer_id.capture_manually','=',False),
            ('acquirer_id.journal_id','=',self.journal_id.id),
         ],limit=1)

    def_prepare_payment_transaction_vals(self):
        self.ensure_one()
        return{
            'amount':self.amount,
            'reference':self.ref,
            'currency_id':self.currency_id.id,
            'partner_id':self.partner_id.id,
            'partner_country_id':self.partner_id.country_id.id,
            'payment_token_id':self.payment_token_id.id,
            'acquirer_id':self.payment_token_id.acquirer_id.id,
            'payment_id':self.id,
            'type':'server2server',
        }

    def_create_payment_transaction(self,vals=None):
        forpayinself:
            ifpay.payment_transaction_id:
                raiseValidationError(_('Apaymenttransactionalreadyexists.'))
            elifnotpay.payment_token_id:
                raiseValidationError(_('Atokenisrequiredtocreateanewpaymenttransaction.'))

        transactions=self.env['payment.transaction']
        forpayinself:
            transaction_vals=pay._prepare_payment_transaction_vals()

            ifvals:
                transaction_vals.update(vals)

            transaction=self.env['payment.transaction'].create(transaction_vals)
            transactions+=transaction

            #Linkthetransactiontothepayment.
            pay.payment_transaction_id=transaction

        returntransactions

    defaction_validate_invoice_payment(self):
        res=super(AccountPayment,self).action_validate_invoice_payment()
        self.mapped('payment_transaction_id').filtered(lambdax:x.state=='done'andnotx.is_processed)._post_process_after_done()
        returnres

    defaction_post(self):
        #Postthepayments"normally"ifnotransactionsareneeded.
        #Ifnot,lettheacquirerupdatesthestate.
        #                               __________           ______________
        #                              |Payments|         |Transactions|
        #                              |__________|         |______________|
        #                                 ||                     |   |
        #                                 ||                     |   |
        #                                 ||                     |   |
        # __________ nos2srequired  __\/______  s2srequired|   |s2s_do_transaction()
        #| Posted |<-----------------| post() |----------------   |
        #|__________|                 |__________|<-----             |
        #                                               |             |
        #                                              OR---------------
        # __________                   __________     |
        #|Cancelled|<-----------------|cancel()|<-----
        #|__________|                 |__________|

        payments_need_trans=self.filtered(lambdapay:pay.payment_token_idandnotpay.payment_transaction_id)
        transactions=payments_need_trans._create_payment_transaction()

        res=super(AccountPayment,self-payments_need_trans).action_post()

        transactions.s2s_do_transaction()

        #Postpaymentsforissuedtransactions.
        transactions._post_process_after_done()
        payments_trans_done=payments_need_trans.filtered(lambdapay:pay.payment_transaction_id.state=='done')
        super(AccountPayment,payments_trans_done).action_post()
        payments_trans_not_done=payments_need_trans.filtered(lambdapay:pay.payment_transaction_id.state!='done')
        payments_trans_not_done.action_cancel()

        returnres
