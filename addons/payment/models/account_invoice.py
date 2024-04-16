#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classAccountMove(models.Model):
    _inherit='account.move'

    transaction_ids=fields.Many2many('payment.transaction','account_invoice_transaction_rel','invoice_id','transaction_id',
                                       string='Transactions',copy=False,readonly=True)
    authorized_transaction_ids=fields.Many2many('payment.transaction',compute='_compute_authorized_transaction_ids',
                                                  string='AuthorizedTransactions',copy=False,readonly=True)

    @api.depends('transaction_ids')
    def_compute_authorized_transaction_ids(self):
        fortransinself:
            trans.authorized_transaction_ids=trans.transaction_ids.filtered(lambdat:t.state=='authorized')

    defget_portal_last_transaction(self):
        self.ensure_one()
        returnself.with_context(active_test=False).transaction_ids.get_last_transaction()

    def_create_payment_transaction(self,vals):
        '''Similartoself.env['payment.transaction'].create(vals)butthevaluesarefilledwiththe
        currentinvoicesfields(e.g.thepartnerorthecurrency).
        :paramvals:Thevaluestocreateanewpayment.transaction.
        :return:Thenewlycreatedpayment.transactionrecord.
        '''
        #Ensurethecurrenciesarethesame.
        currency=self[0].currency_id
        ifany(inv.currency_id!=currencyforinvinself):
            raiseValidationError(_('Atransactioncan\'tbelinkedtoinvoiceshavingdifferentcurrencies.'))

        #Ensurethepartnerarethesame.
        partner=self[0].partner_id
        ifany(inv.partner_id!=partnerforinvinself):
            raiseValidationError(_('Atransactioncan\'tbelinkedtoinvoiceshavingdifferentpartners.'))

        #Trytoretrievetheacquirer.However,fallbacktothetoken'sacquirer.
        acquirer_id=vals.get('acquirer_id')
        acquirer=None
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
                raiseValidationError(_(
                    'Thetransactionwasabortedbecauseyouarenotthecustomerofthisinvoice.'
                    'Loginas%stobeabletousethispaymentmethod.'
                )%partner.name)
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
            'amount':sum(self.mapped('amount_residual')),
            'currency_id':currency.id,
            'partner_id':partner.id,
            'invoice_ids':[(6,0,self.ids)],
        })

        transaction=self.env['payment.transaction'].create(vals)

        #Processdirectlyifpayment_token
        iftransaction.payment_token_id:
            transaction.s2s_do_transaction()

        returntransaction

    defpayment_action_capture(self):
        self.authorized_transaction_ids.action_capture()

    defpayment_action_void(self):
        self.authorized_transaction_ids.action_void()
