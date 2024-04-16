#coding:utf-8

importbase64
importjson
importbinascii
fromcollectionsimportOrderedDict
importhashlib
importhmac
importlogging
fromitertoolsimportchain

fromwerkzeugimporturls

fromflectraimportapi,fields,models,tools,_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment_adyen.controllers.mainimportAdyenController
fromflectra.tools.pycompatimportto_text

_logger=logging.getLogger(__name__)

#https://docs.adyen.com/developers/development-resources/currency-codes
CURRENCY_CODE_MAPS={
    "BHD":3,
    "CVE":0,
    "DJF":0,
    "GNF":0,
    "IDR":0,
    "JOD":3,
    "JPY":0,
    "KMF":0,
    "KRW":0,
    "KWD":3,
    "LYD":3,
    "OMR":3,
    "PYG":0,
    "RWF":0,
    "TND":3,
    "UGX":0,
    "VND":0,
    "VUV":0,
    "XAF":0,
    "XOF":0,
    "XPF":0,
}


classAcquirerAdyen(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('adyen','Adyen')
    ],ondelete={'adyen':'setdefault'})
    adyen_merchant_account=fields.Char('MerchantAccount',required_if_provider='adyen',groups='base.group_user')
    adyen_skin_code=fields.Char('SkinCode',required_if_provider='adyen',groups='base.group_user')
    adyen_skin_hmac_key=fields.Char('SkinHMACKey',required_if_provider='adyen',groups='base.group_user')

    @api.model
    def_adyen_convert_amount(self,amount,currency):
        """
        Adyenrequirestheamounttobemultipliedby10^k,
        wherekdependsonthecurrencycode.
        """
        k=CURRENCY_CODE_MAPS.get(currency.name,2)
        paymentAmount=int(tools.float_round(amount,k)*(10**k))
        returnpaymentAmount

    @api.model
    def_get_adyen_urls(self,environment):
        """AdyenURLs:yhpp:hostedpaymentpage:pay.shtmlforsingle,select.shtmlformultiple"""
        return{
            'adyen_form_url':'https://%s.adyen.com/hpp/pay.shtml'%('live'ifenvironment=='prod'elseenvironment),
        }

    def_adyen_generate_merchant_sig_sha256(self,inout,values):
        """Generatetheshasignforincomingoroutgoingcommunications.,whenusingtheSHA-256
        signature.

        :paramstringinout:'in'(flectracontactingadyen)or'out'(adyen
                             contactingflectra).Inthislastcaseonlysome
                             fieldsshouldbecontained(seee-Commercebasic)
        :paramdictvalues:transactionvalues
        :returnstring:shasign
        """
        defescapeVal(val):
            returnval.replace('\\','\\\\').replace(':','\\:')

        defsignParams(parms):
            signing_string=':'.join(
                escapeVal(v)
                forvinchain(parms.keys(),parms.values())
            )
            hm=hmac.new(hmac_key,signing_string.encode('utf-8'),hashlib.sha256)
            returnbase64.b64encode(hm.digest())

        assertinoutin('in','out')
        assertself.provider=='adyen'

        ifinout=='in':
            #AllthefieldssenttoAdyenmustbeincludedinthesignature.ALLthefucking
            #fields,despitewhatisclaimedinthedocumentation.Forexample,in
            #https://docs.adyen.com/developers/hpp-manual,itisstated:"TheresURLparameterdoes
            #notneedtobeincludedinthesignature."It'satrap,itmustbeincludedaswell!
            keys=[
                'merchantReference','paymentAmount','currencyCode','shipBeforeDate','skinCode',
                'merchantAccount','sessionValidity','merchantReturnData','shopperEmail',
                'shopperReference','allowedMethods','blockedMethods','offset',
                'shopperStatement','recurringContract','billingAddressType',
                'deliveryAddressType','brandCode','countryCode','shopperLocale','orderData',
                'offerEmail','resURL',
            ]
        else:
            keys=[
                'authResult','merchantReference','merchantReturnData','paymentMethod',
                'pspReference','shopperLocale','skinCode',
            ]

        hmac_key=binascii.a2b_hex(self.adyen_skin_hmac_key.encode('ascii'))
        raw_values={k:values.get(k,'')forkinkeysifkinvalues}
        raw_values_ordered=OrderedDict(sorted(raw_values.items(),key=lambdat:t[0]))

        returnsignParams(raw_values_ordered)

    def_adyen_generate_merchant_sig(self,inout,values):
        """Generatetheshasignforincomingoroutgoingcommunications,whenusingtheSHA-1
        signature(deprecatedbyAdyen).

        :paramstringinout:'in'(flectracontactingadyen)or'out'(adyen
                             contactingflectra).Inthislastcaseonlysome
                             fieldsshouldbecontained(seee-Commercebasic)
        :paramdictvalues:transactionvalues

        :returnstring:shasign
        """
        assertinoutin('in','out')
        assertself.provider=='adyen'

        ifinout=='in':
            keys="paymentAmountcurrencyCodeshipBeforeDatemerchantReferenceskinCodemerchantAccountsessionValidityshopperEmailshopperReferencerecurringContractallowedMethodsblockedMethodsshopperStatementmerchantReturnDatabillingAddressTypedeliveryAddressTypeoffset".split()
        else:
            keys="authResultpspReferencemerchantReferenceskinCodemerchantReturnData".split()

        defget_value(key):
            ifvalues.get(key):
                returnvalues[key]
            return''

        sign=''.join('%s'%get_value(k)forkinkeys).encode('ascii')
        key=self.adyen_skin_hmac_key.encode('ascii')
        returnbase64.b64encode(hmac.new(key,sign,hashlib.sha1).digest())

    defadyen_form_generate_values(self,values):
        base_url=self.get_base_url()
        #tmp
        importdatetime
        fromdateutilimportrelativedelta

        paymentAmount=self._adyen_convert_amount(values['amount'],values['currency'])
        ifself.provider=='adyen'andlen(self.adyen_skin_hmac_key)==64:
            tmp_date=datetime.datetime.today()+relativedelta.relativedelta(days=1)

            values.update({
                'merchantReference':values['reference'],
                'paymentAmount':'%d'%paymentAmount,
                'currencyCode':values['currency']andvalues['currency'].nameor'',
                'shipBeforeDate':tmp_date.strftime('%Y-%m-%d'),
                'skinCode':self.adyen_skin_code,
                'merchantAccount':self.adyen_merchant_account,
                'shopperLocale':values.get('partner_lang',''),
                'sessionValidity':tmp_date.isoformat('T')[:19]+"Z",
                'resURL':urls.url_join(base_url,AdyenController._return_url),
                'merchantReturnData':json.dumps({'return_url':'%s'%values.pop('return_url')})ifvalues.get('return_url','')elseFalse,
                'shopperEmail':values.get('partner_email')orvalues.get('billing_partner_email')or'',
            })
            values['merchantSig']=self._adyen_generate_merchant_sig_sha256('in',values)

        else:
            tmp_date=datetime.date.today()+relativedelta.relativedelta(days=1)

            values.update({
                'merchantReference':values['reference'],
                'paymentAmount':'%d'%paymentAmount,
                'currencyCode':values['currency']andvalues['currency'].nameor'',
                'shipBeforeDate':tmp_date,
                'skinCode':self.adyen_skin_code,
                'merchantAccount':self.adyen_merchant_account,
                'shopperLocale':values.get('partner_lang'),
                'sessionValidity':tmp_date,
                'resURL':urls.url_join(base_url,AdyenController._return_url),
                'merchantReturnData':json.dumps({'return_url':'%s'%values.pop('return_url')})ifvalues.get('return_url')elseFalse,
            })
            values['merchantSig']=self._adyen_generate_merchant_sig('in',values)

        returnvalues

    defadyen_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_adyen_urls(environment)['adyen_form_url']


classTxAdyen(models.Model):
    _inherit='payment.transaction'

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_adyen_form_get_tx_from_data(self,data):
        reference,pspReference=data.get('merchantReference'),data.get('pspReference')
        ifnotreferenceornotpspReference:
            error_msg=_('Adyen:receiveddatawithmissingreference(%s)ormissingpspReference(%s)')%(reference,pspReference)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        #findtx->@TDENOTEusepspReference?
        tx=self.env['payment.transaction'].search([('reference','=',reference)])
        ifnottxorlen(tx)>1:
            error_msg=_('Adyen:receiveddataforreference%s')%(reference)
            ifnottx:
                error_msg+=_(';noorderfound')
            else:
                error_msg+=_(';multipleorderfound')
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        #verifyshasign
        iflen(tx.acquirer_id.adyen_skin_hmac_key)==64:
            shasign_check=tx.acquirer_id._adyen_generate_merchant_sig_sha256('out',data)
        else:
            shasign_check=tx.acquirer_id._adyen_generate_merchant_sig('out',data)
        ifto_text(shasign_check)!=to_text(data.get('merchantSig')):
            error_msg=_('Adyen:invalidmerchantSig,received%s,computed%s')%(data.get('merchantSig'),shasign_check)
            _logger.warning(error_msg)
            raiseValidationError(error_msg)

        returntx

    def_adyen_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        #referenceatacquirer:pspReference
        ifself.acquirer_referenceanddata.get('pspReference')!=self.acquirer_reference:
            invalid_parameters.append(('pspReference',data.get('pspReference'),self.acquirer_reference))
        #seller
        ifdata.get('skinCode')!=self.acquirer_id.adyen_skin_code:
            invalid_parameters.append(('skinCode',data.get('skinCode'),self.acquirer_id.adyen_skin_code))
        #result
        ifnotdata.get('authResult'):
            invalid_parameters.append(('authResult',data.get('authResult'),'something'))

        returninvalid_parameters

    def_adyen_form_validate(self,data):
        status=data.get('authResult','PENDING')
        ifstatus=='AUTHORISED':
            self.write({'acquirer_reference':data.get('pspReference')})
            self._set_transaction_done()
            returnTrue
        elifstatus=='PENDING':
            self.write({'acquirer_reference':data.get('pspReference')})
            self._set_transaction_pending()
            returnTrue
        else:
            error=_('Adyen:feedbackerror')
            _logger.info(error)
            self.write({'state_message':error})
            self._set_transaction_cancel()
            returnFalse
