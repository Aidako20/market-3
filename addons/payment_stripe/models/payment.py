#coding:utf-8

fromcollectionsimportnamedtuple
fromdatetimeimportdatetime
fromhashlibimportsha1,sha256
importhmac
importjson
importlogging
importrequests
importpprint
fromrequests.exceptionsimportHTTPError
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.httpimportrequest
fromflectra.tools.float_utilsimportfloat_round
fromflectra.toolsimportconsteq
fromflectra.exceptionsimportValidationError

fromflectra.addons.payment_stripe.controllers.mainimportStripeController

_logger=logging.getLogger(__name__)

#Thefollowingcurrenciesareintegeronly,seehttps://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES=[
    u'BIF',u'XAF',u'XPF',u'CLP',u'KMF',u'DJF',u'GNF',u'JPY',u'MGA',u'PYG',u'RWF',u'KRW',
    u'VUV',u'VND',u'XOF'
]
STRIPE_SIGNATURE_AGE_TOLERANCE=600 #inseconds


classPaymentAcquirerStripe(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('stripe','Stripe')
    ],ondelete={'stripe':'setdefault'})
    stripe_secret_key=fields.Char(required_if_provider='stripe',groups='base.group_user')
    stripe_publishable_key=fields.Char(required_if_provider='stripe',groups='base.group_user')
    stripe_webhook_secret=fields.Char(
        string='StripeWebhookSecret',groups='base.group_user',
        help="Ifyouenablewebhooks,thissecretisusedtoverifytheelectronic"
             "signatureofeventssentbyStripetoFlectra.FailingtosetthisfieldinFlectra"
             "willdisablethewebhooksystemforthisacquirerentirely.")
    stripe_image_url=fields.Char(
        "CheckoutImageURL",groups='base.group_user',
        help="ArelativeorabsoluteURLpointingtoasquareimageofyour"
             "brandorproduct.AsdefinedinyourStripeprofile.See:"
             "https://stripe.com/docs/checkout")

    defstripe_form_generate_values(self,tx_values):
        self.ensure_one()

        base_url=self.get_base_url()
        stripe_session_data={
            'line_items[][amount]':int(tx_values['amount']iftx_values['currency'].nameinINT_CURRENCIESelsefloat_round(tx_values['amount']*100,2)),
            'line_items[][currency]':tx_values['currency'].name,
            'line_items[][quantity]':1,
            'line_items[][name]':tx_values['reference'],
            'client_reference_id':tx_values['reference'],
            'success_url':urls.url_join(base_url,StripeController._success_url)+'?reference=%s'%urls.url_quote_plus(tx_values['reference']),
            'cancel_url':urls.url_join(base_url,StripeController._cancel_url)+'?reference=%s'%urls.url_quote_plus(tx_values['reference']),
            'payment_intent_data[description]':tx_values['reference'],
            'customer_email':tx_values.get('partner_email')ortx_values.get('billing_partner_email')orNone,
        }
        iftx_values['type']=='form_save':
            stripe_session_data['payment_intent_data[setup_future_usage]']='off_session'

        self._add_available_payment_method_types(stripe_session_data,tx_values)

        tx_values['session_id']=self.with_context(stripe_manual_payment=True)._create_stripe_session(stripe_session_data)

        returntx_values

    @api.model
    def_add_available_payment_method_types(self,stripe_session_data,tx_values):
        """
        Addpaymentmethodsavailableforthegiventransaction

        :paramstripe_session_data:dictionarytoaddthepaymentmethodtypesto
        :paramtx_values:valuesofthetransactiontoconsiderthepaymentmethodtypesfor
        """
        PMT=namedtuple('PaymentMethodType',['name','countries','currencies','recurrence'])
        all_payment_method_types=[
            PMT('card',[],[],'recurring'),
            PMT('ideal',['nl'],['eur'],'punctual'),
            PMT('bancontact',['be'],['eur'],'punctual'),
            PMT('eps',['at'],['eur'],'punctual'),
            PMT('giropay',['de'],['eur'],'punctual'),
            PMT('p24',['pl'],['eur','pln'],'punctual'),
        ]

        existing_icons=[(icon.nameor'').lower()foriconinself.env['payment.icon'].search([])]
        linked_icons=[(icon.nameor'').lower()foriconinself.payment_icon_ids]

        #Wedon'tfilteroutpmtinthecasetheicondoesn'texistatallasitwouldbe**implicit**exclusion
        icon_filtered=filter(lambdapmt:pmt.name=='card'or
                                           pmt.nameinlinked_iconsor
                                           pmt.namenotinexisting_icons,all_payment_method_types)
        country=(tx_values['billing_partner_country'].codeor'no_country').lower()
        pmt_country_filtered=filter(lambdapmt:notpmt.countriesorcountryinpmt.countries,icon_filtered)
        currency=(tx_values.get('currency').nameor'no_currency').lower()
        pmt_currency_filtered=filter(lambdapmt:notpmt.currenciesorcurrencyinpmt.currencies,pmt_country_filtered)
        pmt_recurrence_filtered=filter(lambdapmt:tx_values.get('type')!='form_save'orpmt.recurrence=='recurring',
                                    pmt_currency_filtered)

        available_payment_method_types=map(lambdapmt:pmt.name,pmt_recurrence_filtered)

        foridx,payment_method_typeinenumerate(available_payment_method_types):
            stripe_session_data[f'payment_method_types[{idx}]']=payment_method_type

    def_stripe_request(self,url,data=False,method='POST',idempotency_key=None):
        self.ensure_one()
        url=urls.url_join(self._get_stripe_api_url(),url)
        headers={
            'AUTHORIZATION':'Bearer%s'%self.sudo().stripe_secret_key,
            'Stripe-Version':'2019-05-16', #SetupIntentneedaspecificversion
        }
        ifmethod=='POST'andidempotency_key:
            headers['Idempotency-Key']=idempotency_key
        resp=requests.request(method,url,data=data,headers=headers)
        #Stripecansend4XXerrorsforpaymentfailure(notbadly-formedrequests)
        #checkiferror`code`ispresentin4XXresponseandraiseonlyifnot
        #cfrhttps://stripe.com/docs/error-codes
        #thesecanbemadecustomer-facing,astheyusuallyindicateaproblemwiththepayment
        #(e.g.insufficientfunds,expiredcard,etc.)
        #ifthecontextkey`stripe_manual_payment`issetthentheseerrorswillberaisedasValidationError,
        #otherwise,theywillbesilenced,andthewillbereturnednomatterthestatus.
        #Thiskeyshouldtypicallybesetforpaymentsinthepresentandunsetforautomatedpayments
        #(e.g.throughcrons)
        ifnotresp.okandself._context.get('stripe_manual_payment')and(400<=resp.status_code<500andresp.json().get('error',{}).get('code')):
            try:
                resp.raise_for_status()
            exceptHTTPError:
                _logger.error(resp.text)
                stripe_error=resp.json().get('error',{}).get('message','')
                error_msg=""+(_("Stripegaveusthefollowinginfoabouttheproblem:'%s'",stripe_error))
                raiseValidationError(error_msg)
        returnresp.json()

    def_create_stripe_session(self,kwargs):
        self.ensure_one()
        resp=self._stripe_request('checkout/sessions',kwargs)
        ifresp.get('payment_intent')andkwargs.get('client_reference_id'):
            tx=self.env['payment.transaction'].sudo().search([('reference','=',kwargs['client_reference_id'])])
            tx.stripe_payment_intent=resp['payment_intent']
        if'id'notinrespand'error'inresp:
            _logger.error(resp['error']['message'])
        returnresp['id']

    def_create_setup_intent(self,kwargs):
        self.ensure_one()
        params={
            'usage':'off_session',
        }
        _logger.info('_stripe_create_setup_intent:Sendingvaluestostripe,values:\n%s',pprint.pformat(params))

        res=self._stripe_request('setup_intents',params)

        _logger.info('_stripe_create_setup_intent:Valuesreceived:\n%s',pprint.pformat(res))
        returnres

    @api.model
    def_get_stripe_api_url(self):
        return'https://api.stripe.com/v1/'

    @api.model
    defstripe_s2s_form_process(self,data):
        if'card'indataandnotdata.get('card'):
            #comingbackfromacheckoutpaymentandiDeal(oranothernon-cardpm)
            #can'tsavethetokenifit'snotacard
            #notethatinthecaseofas2spayment,'card'wontbe
            #inthedatadictbecauseweneedtofetchitfromthestripeserver
            _logger.info('unabletosavecardinfofromStripesincethepaymentwasnotdonewithacard')
            returnself.env['payment.token']
        last4=data.get('card',{}).get('last4')
        ifnotlast4:
            #PMwascreatedwithasetupintent,needtogetlast4digitsthrough
            #yetanothercall-_-
            acquirer_id=self.env['payment.acquirer'].browse(int(data['acquirer_id']))
            pm=data.get('payment_method')
            res=acquirer_id._stripe_request('payment_methods/%s'%pm,data=False,method='GET')
            last4=res.get('card',{}).get('last4','****')

        payment_token=self.env['payment.token'].sudo().create({
            'acquirer_id':int(data['acquirer_id']),
            'partner_id':int(data['partner_id']),
            'stripe_payment_method':data.get('payment_method'),
            'name':'XXXXXXXXXXXX%s'%last4,
            'acquirer_ref':data.get('customer')
        })
        returnpayment_token

    def_get_feature_support(self):
        """Getadvancedfeaturesupportbyprovider.

        Eachprovidershouldadditstechnicalinthecorresponding
        keyforthefollowingfeatures:
            *tokenize:supportsavingpaymentdatainapayment.tokenize
                        object
        """
        res=super(PaymentAcquirerStripe,self)._get_feature_support()
        res['tokenize'].append('stripe')
        returnres

    def_handle_stripe_webhook(self,data):
        """ProcessawebhookpayloadfromStripe.

        Post-processawebhookpayloadtoactuponthematchingpayment.transaction
        recordinFlectra.
        """
        wh_type=data.get('type')
        ifwh_type!='checkout.session.completed':
            _logger.info('unsupportedwebhooktype%s,ignored',wh_type)
            returnFalse

        _logger.info('handling%swebhookeventfromstripe',wh_type)

        stripe_object=data.get('data',{}).get('object')
        ifnotstripe_object:
            raiseValidationError('StripeWebhookdatadoesnotconformtotheexpectedAPI.')
        ifwh_type=='checkout.session.completed':
            returnself._handle_checkout_webhook(stripe_object)
        returnFalse

    def_verify_stripe_signature(self):
        """
        :return:trueifandonlyifsignaturematcheshashofpayloadcalculatedwithsecret
        :raisesValidationError:ifsignaturedoesn'tmatch
        """
        ifnotself.stripe_webhook_secret:
            raiseValidationError('webhookeventreceivedbutwebhooksecretisnotconfigured')
        signature=request.httprequest.headers.get('Stripe-Signature')
        body=request.httprequest.data

        sign_data={k:vfor(k,v)in[s.split('=')forsinsignature.split(',')]}
        event_timestamp=int(sign_data['t'])
        ifdatetime.utcnow().timestamp()-event_timestamp>STRIPE_SIGNATURE_AGE_TOLERANCE:
            _logger.error('stripeeventistooold,eventisdiscarded')
            raiseValidationError('eventtimestampolderthantolerance')

        signed_payload="%s.%s"%(event_timestamp,body.decode('utf-8'))

        actual_signature=sign_data['v1']
        expected_signature=hmac.new(self.stripe_webhook_secret.encode('utf-8'),
                                      signed_payload.encode('utf-8'),
                                      sha256).hexdigest()

        ifnotconsteq(expected_signature,actual_signature):
            _logger.error(
                'incorrectwebhooksignaturefromStripe,checkifthewebhooksignature'
                'inFlectramatchestooneintheStripedashboard')
            raiseValidationError('incorrectwebhooksignature')

        returnTrue

    def_handle_checkout_webhook(self,checkout_object:dir):
        """
        Processacheckout.session.completedStripewebhookevent,
        markrelatedpaymentsuccessful

        :paramcheckout_object:providedintherequestbody
        :return:Trueifandonlyifhandlingwentwell,Falseotherwise
        :raisesValidationError:ifinputisn'tusable
        """
        tx_reference=checkout_object.get('client_reference_id')
        data={'reference':tx_reference}
        try:
            flectra_tx=self.env['payment.transaction']._stripe_form_get_tx_from_data(data)
        exceptValidationErrorase:
            _logger.info('Receivednotificationfortx%s.Skippeditbecauseof%s',tx_reference,e)
            returnFalse

        PaymentAcquirerStripe._verify_stripe_signature(flectra_tx.acquirer_id)

        url='payment_intents/%s'%flectra_tx.stripe_payment_intent
        stripe_tx=flectra_tx.acquirer_id._stripe_request(url)

        if'error'instripe_tx:
            error=stripe_tx['error']
            raiseValidationError("CouldnotfetchStripepaymentintentrelatedto%sbecauseof%s;see%s"%(
                flectra_tx,error['message'],error['doc_url']))

        ifstripe_tx.get('charges')andstripe_tx.get('charges').get('total_count'):
            charge=stripe_tx.get('charges').get('data')[0]
            data.update(charge)

        returnflectra_tx.form_feedback(data,'stripe')


classPaymentTransactionStripe(models.Model):
    _inherit='payment.transaction'

    stripe_payment_intent=fields.Char(string='StripePaymentIntentID',readonly=True)
    stripe_payment_intent_secret=fields.Char(string='StripePaymentIntentSecret',readonly=True)

    def_get_processing_info(self):
        res=super()._get_processing_info()
        ifself.acquirer_id.provider=='stripe':
            stripe_info={
                'stripe_payment_intent':self.stripe_payment_intent,
                'stripe_payment_intent_secret':self.stripe_payment_intent_secret,
                'stripe_publishable_key':self.acquirer_id.stripe_publishable_key,
            }
            res.update(stripe_info)
        returnres

    defform_feedback(self,data,acquirer_name):
        ifdata.get('reference')andacquirer_name=='stripe':
            transaction=self.env['payment.transaction'].search([('reference','=',data['reference'])])

            url='payment_intents/%s'%transaction.stripe_payment_intent
            resp=transaction.acquirer_id._stripe_request(url)
            ifresp.get('charges')andresp.get('charges').get('total_count'):
                resp=resp.get('charges').get('data')[0]

            data.update(resp)
            _logger.info('Stripe:enteringform_feedbackwithpostdata%s'%pprint.pformat(data))
        returnsuper(PaymentTransactionStripe,self).form_feedback(data,acquirer_name)

    def_stripe_create_payment_intent(self,acquirer_ref=None,email=None):
        ifnotself.payment_token_id.stripe_payment_method:
            #oldtokenbeforeusingsca,needtofetchdatafromtheapi
            self.payment_token_id._stripe_sca_migrate_customer()

        charge_params={
            'amount':int(self.amountifself.currency_id.nameinINT_CURRENCIESelsefloat_round(self.amount*100,2)),
            'currency':self.currency_id.name.lower(),
            'off_session':True,
            'confirm':True,
            'payment_method':self.payment_token_id.stripe_payment_method,
            'customer':self.payment_token_id.acquirer_ref,
            "description":self.reference,
        }
        ifnotself.env.context.get('off_session'):
            charge_params.update(setup_future_usage='off_session',off_session=False)
        _logger.info('_stripe_create_payment_intent:Sendingvaluestostripe,values:\n%s',pprint.pformat(charge_params))
        #CreateanidempotencykeyusingthehashofthetransactionreferenceandthedatabaseUUID
        database_uuid=self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        idempotency_key=sha1((database_uuid+self.reference).encode("utf-8")).hexdigest()
        res=self.acquirer_id._stripe_request('payment_intents',charge_params,idempotency_key=idempotency_key)
        ifres.get('charges')andres.get('charges').get('total_count'):
            res=res.get('charges').get('data')[0]

        _logger.info('_stripe_create_payment_intent:Valuesreceived:\n%s',pprint.pformat(res))
        returnres

    defstripe_s2s_do_transaction(self,**kwargs):
        self.ensure_one()
        result=self._stripe_create_payment_intent(acquirer_ref=self.payment_token_id.acquirer_ref,email=self.partner_email)
        returnself._stripe_s2s_validate_tree(result)

    def_create_stripe_refund(self):

        refund_params={
            'charge':self.acquirer_reference,
            'amount':int(float_round(self.amount*100,2)),#bydefault,striperefundthefullamount(wedon'treallyneedtospecifythevalue)
            'metadata[reference]':self.reference,
        }

        _logger.info('_create_stripe_refund:SendingvaluestostripeURL,values:\n%s',pprint.pformat(refund_params))
        #CreateanidempotencykeyusingthehashofthetransactionreferenceandthedatabaseUUID
        database_uuid=self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        idempotency_key=sha1((database_uuid+self.reference+'refunds').encode("utf-8")).hexdigest()
        res=self.acquirer_id._stripe_request('refunds',refund_params,idempotency_key=idempotency_key)
        _logger.info('_create_stripe_refund:Valuesreceived:\n%s',pprint.pformat(res))

        returnres

    defstripe_s2s_do_refund(self,**kwargs):
        self.ensure_one()
        result=self._create_stripe_refund()
        returnself._stripe_s2s_validate_tree(result)

    @api.model
    def_stripe_form_get_tx_from_data(self,data):
        """Givenadatadictcomingfromstripe,verifyitandfindtherelated
        transactionrecord."""
        reference=data.get('reference')
        ifnotreference:
            stripe_error=data.get('error',{}).get('message','')
            _logger.error('Stripe:invalidreplyreceivedfromstripeAPI,lookslike'
                          'thetransactionfailed.(error:%s)',stripe_erroror'n/a')
            error_msg=_("We'resorrytoreportthatthetransactionhasfailed.")
            ifstripe_error:
                error_msg+=""+(_("Stripegaveusthefollowinginfoabouttheproblem:'%s'")%
                                    stripe_error)
            error_msg+=""+_("Perhapstheproblemcanbesolvedbydouble-checkingyour"
                                 "creditcarddetails,orcontactingyourbank?")
            raiseValidationError(error_msg)

        tx=self.search([('reference','=',reference)])
        ifnottx:
            error_msg=_('Stripe:noorderfoundforreference%s',reference)
            _logger.error(error_msg)
            raiseValidationError(error_msg)
        eliflen(tx)>1:
            error_msg=_('Stripe:%(count)sordersfoundforreference%(reference)s',count=len(tx),reference=reference)
            _logger.error(error_msg)
            raiseValidationError(error_msg)
        returntx[0]

    def_stripe_s2s_validate_tree(self,tree):
        self.ensure_one()
        ifself.statenotin("draft","pending"):
            _logger.info('Stripe:tryingtovalidateanalreadyvalidatedtx(ref%s)',self.reference)
            returnTrue

        status=tree.get('status')
        tx_id=tree.get('id')
        tx_secret=tree.get("client_secret")
        pi_id=tree.get('payment_intent')
        vals={
            "date":fields.datetime.now(),
            "acquirer_reference":tx_id,
            "stripe_payment_intent":pi_idortx_id,
            "stripe_payment_intent_secret":tx_secret
        }
        ifstatus=='succeeded':
            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            ifself.type=='form_save':
                s2s_data={
                    'customer':tree.get('customer'),
                    'payment_method':tree.get('payment_method'),
                    'card':tree.get('payment_method_details').get('card'),
                    'acquirer_id':self.acquirer_id.id,
                    'partner_id':self.partner_id.id
                }
                token=self.acquirer_id.stripe_s2s_form_process(s2s_data)
                self.payment_token_id=token.id
            ifself.payment_token_id:
                self.payment_token_id.verified=True
            returnTrue
        ifstatusin('processing','requires_action'):
            self.write(vals)
            self._set_transaction_pending()
            returnTrue
        ifstatus=='requires_payment_method':
            self._set_transaction_cancel()
            self.acquirer_id._stripe_request('payment_intents/%s/cancel'%self.stripe_payment_intent)
            returnFalse
        else:
            error=tree.get("failure_message")ortree.get('error',{}).get('message')
            self._set_transaction_error(error)
            returnFalse

    def_stripe_form_get_invalid_parameters(self,data):
        invalid_parameters=[]
        ifdata.get('amount')!=int(self.amountifself.currency_id.nameinINT_CURRENCIESelsefloat_round(self.amount*100,2)):
            invalid_parameters.append(('Amount',data.get('amount'),self.amount*100))
        ifdata.get('currency')anddata.get('currency').upper()!=self.currency_id.name:
            invalid_parameters.append(('Currency',data.get('currency'),self.currency_id.name))
        ifdata.get('payment_intent')anddata.get('payment_intent')!=self.stripe_payment_intent:
            invalid_parameters.append(('PaymentIntent',data.get('payment_intent'),self.stripe_payment_intent))
        returninvalid_parameters

    def_stripe_form_validate(self,data):
        returnself._stripe_s2s_validate_tree(data)


classPaymentTokenStripe(models.Model):
    _inherit='payment.token'

    stripe_payment_method=fields.Char('PaymentMethodID')

    @api.model
    defstripe_create(self,values):
        ifvalues.get('stripe_payment_method')andnotvalues.get('acquirer_ref'):
            partner_id=self.env['res.partner'].browse(values.get('partner_id'))
            payment_acquirer=self.env['payment.acquirer'].browse(values.get('acquirer_id'))

            #createcustomertostipe
            customer_data={
                'email':partner_id.email
            }
            cust_resp=payment_acquirer._stripe_request('customers',customer_data)

            #linkcustomerwithpaymentmethod
            api_url_payment_method='payment_methods/%s/attach'%values['stripe_payment_method']
            method_data={
                'customer':cust_resp.get('id')
            }
            payment_acquirer._stripe_request(api_url_payment_method,method_data)
            return{
                'acquirer_ref':cust_resp['id'],
            }
        returnvalues

    def_stripe_sca_migrate_customer(self):
        """MigrateatokenfromtheoldimplementationofStripetotheSCAone.

        Intheoldimplementation,itwaspossibletocreateavalidchargejustby
        givingthecustomerreftoaskStripetousethedefaultsource(=default
        card).Sincewehaveaone-to-onematchingbetweenasavedcard,thisusedto
        workwell-butnowweneedtospecifythepaymentmethodforeachcallandso
        wehavetocontactstripetogetthedefaultsourceforthecustomerandsaveit
        inthepaymenttoken.
        Thisconversionwillhappenoncepertoken,thefirsttimeitgetsusedfollowing
        theinstallationofthemodule."""
        self.ensure_one()
        url="customers/%s"%(self.acquirer_ref)
        data=self.acquirer_id._stripe_request(url,method="GET")
        sources=data.get('sources',{}).get('data',[])
        pm_ref=False
        ifsources:
            iflen(sources)>1:
                _logger.warning('stripescacustomerconversion:thereshouldbeasinglesavedsourcepercustomer!')
            pm_ref=sources[0].get('id')
        else:
            url='payment_methods'
            params={
                'type':'card',
                'customer':self.acquirer_ref,
            }
            payment_methods=self.acquirer_id._stripe_request(url,params,method='GET')
            cards=payment_methods.get('data',[])
            iflen(cards)>1:
                _logger.warning('stripescacustomerconversion:thereshouldbeasinglesavedsourcepercustomer!')
            pm_ref=cardsandcards[0].get('id')
        ifnotpm_ref:
            raiseValidationError(_('UnabletoconvertStripecustomerforSCAcompatibility.IsthereatleastonecardforthiscustomerintheStripebackend?'))
        self.stripe_payment_method=pm_ref
        _logger.info('convertedoldcustomerreftosca-compatiblerecordforpaymenttoken%s',self.id)
