#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
importhmac
importjson
importlogging
fromwerkzeugimporturls

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError
fromflectra.addons.payment_odoo_by_adyen.controllers.mainimportFlectraByAdyenController

_logger=logging.getLogger(__name__)


classAcquirerFlectraByAdyen(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
       ('flectra_adyen','FlectraPaymentsbyAdyen')
    ],ondelete={'flectra_adyen':'setdefault'})
    flectra_adyen_account_id=fields.Many2one('adyen.account',required_if_provider='flectra_adyen',related='company_id.adyen_account_id')
    flectra_adyen_payout_id=fields.Many2one('adyen.payout',required_if_provider='flectra_adyen',string='AdyenPayout',domain="[('adyen_account_id','=',flectra_adyen_account_id)]")

    @api.constrains('provider','state')
    def_check_flectra_adyen_test(self):
        forpayment_acquirerinself:
            ifpayment_acquirer.provider=='flectra_adyen'andpayment_acquirer.state=='test':
                raiseValidationError(_('FlectraPaymentsbyAdyenisnotavailableintestmode.'))

    def_get_feature_support(self):
        res=super(AcquirerFlectraByAdyen,self)._get_feature_support()
        res['tokenize'].append('flectra_adyen')
        returnres

    @api.model
    def_flectra_adyen_format_amount(self,amount,currency_id):
        return{
            'value':int(amount*(10**currency_id.decimal_places)),
            'currency':currency_id.name,
        }

    @api.model
    def_flectra_adyen_compute_signature(self,amount,currency_id,reference):
        secret=self.env['ir.config_parameter'].sudo().get_param('database.secret')
        token_str='%s%s%s'%(
            int(amount*(10**currency_id.decimal_places)),
            currency_id.name,
            reference
        )
        returnhmac.new(secret.encode('utf-8'),token_str.encode('utf-8'),hashlib.sha256).hexdigest()

    defflectra_adyen_form_generate_values(self,values):
        #Don'tusethevaluereturnedby`self.get_base_url`forthenotification_urlas
        #`request.httprequest.url_root`couldbeforgedtoretrievethesignatureand
        #fakeapaymentupdate
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        data={
            'adyen_uuid':self.flectra_adyen_account_id.adyen_uuid,
            'payout':self.flectra_adyen_payout_id.code,
            'amount':self._flectra_adyen_format_amount(values['amount'],values['currency']),
            'reference':values['reference'],
            'shopperLocale':values.get('partner_lang'),
            'metadata':{
                'merchant_signature':self._flectra_adyen_compute_signature(values['amount'],values['currency'],values['reference']),
                'notification_url':urls.url_join(base_url,FlectraByAdyenController._notification_url),
            },
            'returnUrl':urls.url_join(self.get_base_url(),'/payment/process'),
        }

        ifself.save_tokenin['ask','always']:
            data.update({
                'shopperReference':'%s_%s'%(self.flectra_adyen_account_id.adyen_uuid,values['partner_id']),
                'storePaymentMethod':True,
                'recurringProcessingModel':'CardOnFile',
            })

        values.update({
            'data':json.dumps(data),
        })
        returnvalues

    defflectra_adyen_get_form_action_url(self):
        self.ensure_one()
        proxy_url=self.env['ir.config_parameter'].sudo().get_param('adyen_platforms.proxy_url')
        returnurls.url_join(proxy_url,'pay_by_link')

    defflectra_adyen_create_account(self):
        returnself.env['adyen.account'].action_create_redirect()

classTxFlectraByAdyen(models.Model):
    _inherit='payment.transaction'

    defflectra_adyen_s2s_do_transaction(self,**kwargs):
        self.ensure_one()
        #Don'tusethevaluereturnedby`self.get_base_url`forthenotification_urlas
        #`request.httprequest.url_root`couldbeforgedtoretrievethesignatureand
        #fakeapaymentupdate
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        data={
            'payout':self.acquirer_id.flectra_adyen_payout_id.code,
            'amount':self.acquirer_id._flectra_adyen_format_amount(self.amount,self.currency_id),
            'reference':self.reference,
            'paymentMethod':{
                'type':self.payment_token_id.flectra_adyen_payment_method_type,
                'storedPaymentMethodId':self.payment_token_id.acquirer_ref,
            },
            'shopperReference':'%s_%s'%(self.acquirer_id.flectra_adyen_account_id.adyen_uuid,self.partner_id.id),
            'shopperInteraction':'ContAuth',
            'metadata':{
                'merchant_signature':self.acquirer_id._flectra_adyen_compute_signature(self.amount,self.currency_id,self.reference),
                'notification_url':urls.url_join(base_url,FlectraByAdyenController._notification_url),
            },
            'returnUrl':urls.url_join(self.get_base_url(),'/payment/process'),
        }
        self.acquirer_id.flectra_adyen_account_id._adyen_rpc('payments',data)

    @api.model
    def_flectra_adyen_form_get_tx_from_data(self,data):
        reference=data.get('merchantReference')
        ifnotreference:
            error_msg=_('FlectraPaymentsbyAdyen:receiveddatawithmissingreference(%s)',reference)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        tx=self.env['payment.transaction'].search([('reference','=',reference)])
        ifnottxorlen(tx)>1:
            error_msg=_('FlectraPaymentsbyAdyen:receiveddataforreference%s')%(reference)
            ifnottx:
                error_msg+=_(';noorderfound')
            else:
                error_msg+=_(';multipleorderfound')
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        returntx

    def_flectra_adyen_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        ifself.acquirer_referenceanddata.get('pspReference')!=self.acquirer_reference:
            invalid_parameters.append(('pspReference',data.get('pspReference'),self.acquirer_reference))

        returninvalid_parameters

    def_flectra_adyen_form_validate(self,data):
        merchant_signature=self.acquirer_id._flectra_adyen_compute_signature(self.amount,self.currency_id,self.reference)
        ifmerchant_signature!=data['additionalData']['metadata.merchant_signature']:
            returnFalse

        #Savetoken
        ifself.partner_idandnotself.payment_token_idand\
               (self.type=='form_save'orself.acquirer_id.save_token=='always')\
               and'recurring.shopperReference'indata['additionalData']:
            res=self.acquirer_id.flectra_adyen_account_id._adyen_rpc('payment_methods',{
                'shopperReference':data['additionalData']['recurring.shopperReference']
            })
            stored_payment_methods=res['storedPaymentMethods']
            pm_id=data['additionalData']['recurring.recurringDetailReference']
            token_id=self.env['payment.token'].create({
                'name':_("CardNoXXXXXXXXXXXX%s",data['additionalData']['cardSummary']),
                'acquirer_ref':pm_id,
                'acquirer_id':self.acquirer_id.id,
                'partner_id':self.partner_id.id,
                'flectra_adyen_payment_method_type':next(pm['type']forpminstored_payment_methodsifpm['id']==pm_id)
            })
            self.payment_token_id=token_id

        #Updatestatus
        ifdata['success']:
            self.write({'acquirer_reference':data.get('pspReference')})
            self._set_transaction_done()
            returnTrue
        else:
            error=_('FlectraPaymentbyAdyen:feedbackerror')
            _logger.info(error)
            self.write({'state_message':error})
            self._set_transaction_cancel()
            returnFalse

classPaymentToken(models.Model):
    _inherit='payment.token'

    flectra_adyen_payment_method_type=fields.Char(string='PaymentMethodType')
