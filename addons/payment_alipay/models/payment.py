#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromhashlibimportmd5
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.tools.float_utilsimportfloat_compare
fromflectra.addons.payment_alipay.controllers.mainimportAlipayController
fromflectra.addons.payment.models.payment_acquirerimportValidationError

_logger=logging.getLogger(__name__)


classPaymentAcquirer(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('alipay','Alipay')
    ],ondelete={'alipay':'setdefault'})
    alipay_payment_method=fields.Selection([
        ('express_checkout','ExpressCheckout(onlyforChineseMerchant)'),
        ('standard_checkout','Cross-border'),
    ],string='Account',default='express_checkout',
        help=" *Cross-border:FortheOverseasseller\n *ExpressCheckout:FortheChineseSeller")
    alipay_merchant_partner_id=fields.Char(
        string='MerchantPartnerID',required_if_provider='alipay',groups='base.group_user',
        help='TheMerchantPartnerIDisusedtoensurecommunicationscomingfromAlipayarevalidandsecured.')
    alipay_md5_signature_key=fields.Char(
        string='MD5SignatureKey',required_if_provider='alipay',groups='base.group_user',
        help="TheMD5privatekeyisthe32-bytestringwhichiscomposedofEnglishlettersandnumbers.")
    alipay_seller_email=fields.Char(string='AlipaySellerEmail',groups='base.group_user')

    def_get_feature_support(self):
        res=super(PaymentAcquirer,self)._get_feature_support()
        res['fees'].append('alipay')
        returnres

    @api.model
    def_get_alipay_urls(self,environment):
        """AlipayURLS"""
        ifenvironment=='prod':
            return'https://mapi.alipay.com/gateway.do'
        return'https://openapi.alipaydev.com/gateway.do'

    defalipay_compute_fees(self,amount,currency_id,country_id):
        """Computealipayfees.

            :paramfloatamount:theamounttopay
            :paramintegercountry_id:anIDofares.country,orNone.Thisis
                                       thecustomer'scountry,tobecomparedto
                                       theacquirercompanycountry.
            :returnfloatfees:computedfees
        """
        fees=0.0
        ifself.fees_active:
            country=self.env['res.country'].browse(country_id)
            ifcountryandself.company_id.sudo().country_id.id==country.id:
                percentage=self.fees_dom_var
                fixed=self.fees_dom_fixed
            else:
                percentage=self.fees_int_var
                fixed=self.fees_int_fixed
            fees=(percentage/100.0*amount+fixed)/(1-percentage/100.0)
        returnfees

    def_build_sign(self,val):
        #Rearrangeparametersinthedatasetalphabetically
        data_to_sign=sorted(val.items())
        #Excludeparametersthatshouldnotbesigned
        data_to_sign=["{}={}".format(k,v)fork,vindata_to_signifknotin['sign','sign_type','reference']]
        #Andconnectrearrangedparameterswith&
        data_string='&'.join(data_to_sign)
        data_string+=self.alipay_md5_signature_key
        returnmd5(data_string.encode('utf-8')).hexdigest()

    def_get_alipay_tx_values(self,values):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        alipay_tx_values=({
            '_input_charset':'utf-8',
            'notify_url':urls.url_join(base_url,AlipayController._notify_url),
            'out_trade_no':values.get('reference'),
            'partner':self.alipay_merchant_partner_id,
            'return_url':urls.url_join(base_url,AlipayController._return_url),
            'subject':values.get('reference'),
            'total_fee':'%.2f'%(values.get('amount')+values.get('fees')),
        })
        ifself.alipay_payment_method=='standard_checkout':
            alipay_tx_values.update({
                'service':'create_forex_trade',
                'product_code':'NEW_OVERSEAS_SELLER',
                'currency':values.get('currency').name,
            })
        else:
            alipay_tx_values.update({
                'service':'create_direct_pay_by_user',
                'payment_type':1,
                'seller_email':self.alipay_seller_email,
            })
        sign=self._build_sign(alipay_tx_values)
        alipay_tx_values.update({
            'sign_type':'MD5',
            'sign':sign,
        })
        returnalipay_tx_values

    defalipay_form_generate_values(self,values):
        values.update(self._get_alipay_tx_values(values))
        returnvalues

    defalipay_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_alipay_urls(environment)


classPaymentTransaction(models.Model):
    _inherit='payment.transaction'

    def_check_alipay_configuration(self,vals):
        acquirer_id=int(vals.get('acquirer_id'))
        acquirer=self.env['payment.acquirer'].sudo().browse(acquirer_id)
        ifacquirerandacquirer.provider=='alipay'andacquirer.alipay_payment_method=='express_checkout':
            currency_id=int(vals.get('currency_id'))
            ifcurrency_id:
                currency=self.env['res.currency'].sudo().browse(currency_id)
                ifcurrencyandcurrency.name!='CNY':
                    _logger.info("OnlyCNYcurrencyisallowedforAlipayExpressCheckout")
                    raiseValidationError(_("""
                        OnlytransactionsinChineseYuan(CNY)areallowedforAlipayExpressCheckout.\n
                        IfyouwishtouseanothercurrencythanCNYforyourtransactions,switchyour
                        configurationtoaCross-borderaccountontheAlipaypaymentacquirerinFlectra.
                    """))
        returnTrue

    defwrite(self,vals):
        ifvals.get('currency_id')orvals.get('acquirer_id'):
            forpaymentinself:
                check_vals={
                    'acquirer_id':vals.get('acquirer_id',payment.acquirer_id.id),
                    'currency_id':vals.get('currency_id',payment.currency_id.id)
                }
                payment._check_alipay_configuration(check_vals)
        returnsuper(PaymentTransaction,self).write(vals)

    @api.model
    defcreate(self,vals):
        self._check_alipay_configuration(vals)
        returnsuper(PaymentTransaction,self).create(vals)

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_alipay_form_get_tx_from_data(self,data):
        reference,txn_id,sign=data.get('reference'),data.get('trade_no'),data.get('sign')
        ifnotreferenceornottxn_id:
            _logger.info('Alipay:receiveddatawithmissingreference(%s)ortxn_id(%s)'%(reference,txn_id))
            raiseValidationError(_('Alipay:receiveddatawithmissingreference(%s)ortxn_id(%s)')%(reference,txn_id))

        txs=self.env['payment.transaction'].search([('reference','=',reference)])
        ifnottxsorlen(txs)>1:
            error_msg=_('Alipay:receiveddataforreference%s')%(reference)
            logger_msg='Alipay:receiveddataforreference%s'%(reference)
            ifnottxs:
                error_msg+=_(';noorderfound')
                logger_msg+=';noorderfound'
            else:
                error_msg+=_(';multipleorderfound')
                logger_msg+=';multipleorderfound'
            _logger.info(logger_msg)
            raiseValidationError(error_msg)

        #verifysign
        sign_check=txs.acquirer_id._build_sign(data)
        ifsign!=sign_check:
            _logger.info('Alipay:invalidsign,received%s,computed%s,fordata%s'%(sign,sign_check,data))
            raiseValidationError(_('Alipay:invalidsign,received%s,computed%s,fordata%s')%(sign,sign_check,data))

        returntxs

    def_alipay_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        iffloat_compare(float(data.get('total_fee','0.0')),(self.amount+self.fees),2)!=0:
            invalid_parameters.append(('total_fee',data.get('total_fee'),'%.2f'%(self.amount+self.fees))) #mc_grossisamount+fees
        ifself.acquirer_id.alipay_payment_method=='standard_checkout':
            ifdata.get('currency')!=self.currency_id.name:
                invalid_parameters.append(('currency',data.get('currency'),self.currency_id.name))
        else:
            ifdata.get('seller_email')!=self.acquirer_id.alipay_seller_email:
                invalid_parameters.append(('seller_email',data.get('seller_email'),self.acquirer_id.alipay_seller_email))
        returninvalid_parameters

    def_alipay_form_validate(self,data):
        ifself.statein['done']:
            _logger.info('Alipay:tryingtovalidateanalreadyvalidatedtx(ref%s)',self.reference)
            returnTrue

        status=data.get('trade_status')
        res={
            'acquirer_reference':data.get('trade_no'),
        }
        ifstatusin['TRADE_FINISHED','TRADE_SUCCESS']:
            _logger.info('ValidatedAlipaypaymentfortx%s:setasdone'%(self.reference))
            date_validate=fields.Datetime.now()
            res.update(date=date_validate)
            self._set_transaction_done()
            self.write(res)
            self.execute_callback()
            returnTrue
        elifstatus=='TRADE_CLOSED':
            _logger.info('ReceivednotificationforAlipaypayment%s:setasCanceled'%(self.reference))
            res.update(state_message=data.get('close_reason',''))
            self._set_transaction_cancel()
            returnself.write(res)
        else:
            error='ReceivedunrecognizedstatusforAlipaypayment%s:%s,setaserror'%(self.reference,status)
            _logger.info(error)
            res.update(state_message=error)
            self._set_transaction_error()
            returnself.write(res)
