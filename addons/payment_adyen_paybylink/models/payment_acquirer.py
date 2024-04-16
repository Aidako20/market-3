#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importre
importrequests

fromwerkzeugimporturls

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError

fromflectra.addons.payment_adyen_paybylinkimportutilsasadyen_utils
fromflectra.addons.payment_adyen_paybylink.constimportAPI_ENDPOINT_VERSIONS


_logger=logging.getLogger(__name__)


classPaymentAcquirer(models.Model):
    _inherit='payment.acquirer'

    adyen_api_key=fields.Char(
        string="APIKey",
        help="TheAPIkeyofthewebserviceuser",
        required_if_provider='adyen',
        groups='base.group_user',
    )
    adyen_hmac_key=fields.Char(
        string="HMACKey",
        help="TheHMACkeyofthewebhook",
        required_if_provider='adyen',
        groups='base.group_user',
    )
    adyen_checkout_api_url=fields.Char(
        string="CheckoutAPIURL",
        help="ThebaseURLfortheCheckoutAPIendpoints",
        required_if_provider='adyen',
    )
    #Wesetadefaultforthenowunusedkeyfieldsratherthanmakingthemnotrequiredtoavoid
    #theerrorlogatDBinitwhentheORMtriestosetthe'NOTNULL'constraintonthosefields.
    adyen_skin_code=fields.Char(default="Donotusethisfield")
    adyen_skin_hmac_key=fields.Char(default="Donotusethisfield")

    @api.model_create_multi
    defcreate(self,values_list):
        forvaluesinvalues_list:
            self._adyen_trim_api_urls(values)
        returnsuper().create(values_list)

    defwrite(self,values):
        self._adyen_trim_api_urls(values)
        #Wesetadefaultforthenowunusedkeyfieldsratherthanmakingthemnotrequiredto
        #avoidtheerrorlogatDBinitwhentheORMtriestosetthe'NOTNULL'constrainton
        #thosefields.
        values.update(
            adyen_skin_code="Donotusethisfield",
            adyen_skin_hmac_key="Donotusethisfield",
        )
        returnsuper().write(values)

    @api.model
    def_adyen_trim_api_urls(self,values):
        """RemovetheversionandtheendpointfromtheurlofAdyenAPIfields.

        :paramdictvalues:Thecreateorwritevalues
        :return:None
        """
        #Testthevalueincasewe'reduplicatinganacquirer
        ifvalues.get('adyen_checkout_api_url'):
            values['adyen_checkout_api_url']=re.sub(
                r'[vV]\d+(/.*)?','',values['adyen_checkout_api_url']
            )

    defadyen_form_generate_values(self,values):
        base_url=self.get_base_url()

        payment_amount=self._adyen_convert_amount(values['amount'],values['currency'])
        values['adyen_paybylink_data']={
            'reference':values['reference'],
            'amount':{
                'value':'%d'%payment_amount,
                'currency':values['currency']andvalues['currency'].nameor'',
            },
            'merchantAccount':self.adyen_merchant_account,
            'shopperLocale':values.get('partner_lang',''),
            'returnUrl':urls.url_join(base_url,'/payment/process'),
            'shopperEmail':values.get('partner_email')orvalues.get('billing_partner_email',''),
            'shopperReference':self._adyen_compute_shopper_reference(values.get('partner_id')),
            'shopperName':{
                'firstName':values.get('partner_first_name'),
                'lastName':values.get('partner_last_name'),
            },
            'telephoneNumber':values.get('partner_phone'),
            'billingAddress':adyen_utils.format_partner_address(values.get('billing_partner')),
            'deliveryAddress':adyen_utils.format_partner_address(values.get('partner')),
        }

        returnvalues

    defadyen_get_form_action_url(self):
        """Overrideofadyen_get_form_action_url"""
        form_action_url_values=self._context.get('form_action_url_values')
        ifform_action_url_values:
            returnself._adyen_get_paybylink(form_action_url_values['adyen_paybylink_data'])
        returnFalse

    def_adyen_get_paybylink(self,data):
        paybylink_response=self._adyen_make_request(
            url_field_name='adyen_checkout_api_url',
            endpoint='/paymentLinks',
            payload=data,
        )
        returnpaybylink_response['url']

    def_adyen_make_request(
        self,url_field_name,endpoint,endpoint_param=None,payload=None,method='POST'
    ):
        """MakearequesttoAdyenAPIatthespecifiedendpoint.

        Note:self.ensure_one()

        :paramstrurl_field_name:ThenameofthefieldholdingthebaseURLfortherequest
        :paramstrendpoint:Theendpointtobereachedbytherequest
        :paramstrendpoint_param:Avariablerequiredbysomeendpointswhichareinterpolatedwith
                                   itifprovided.Forexample,theacquirerreferenceofthesource
                                   transactionforthe'/payments/{}/refunds'endpoint.
        :paramdictpayload:Thepayloadoftherequest
        :paramstrmethod:TheHTTPmethodoftherequest
        :return:TheJSON-formattedcontentoftheresponse
        :rtype:dict
        :raise:ValidationErrorifanHTTPerroroccurs
        """

        def_build_url(_base_url,_version,_endpoint):
            """BuildanAPIURLbyappendingtheversionandendpointtoabaseURL.

            ThefinalURLfollowsthispattern:`<_base>/V<_version>/<_endpoint>`.

            :paramstr_base_url:Thebaseoftheurlprefixedwith`https://`
            :paramint_version:Theversionoftheendpoint
            :paramstr_endpoint:TheendpointoftheURL.
            :return:ThefinalURL
            :rtype:str
            """
            _base=_base_url.rstrip('/') #Removepotentialtrailingslash
            _endpoint=_endpoint.lstrip('/') #Removepotentialleadingslash
            returnf'{_base}/V{_version}/{_endpoint}'

        self.ensure_one()

        base_url=self[url_field_name] #RestrictrequestURLtothestoredAPIURLfields
        version=API_ENDPOINT_VERSIONS[endpoint]
        endpoint=endpointifnotendpoint_paramelseendpoint.format(endpoint_param)
        url=_build_url(base_url,version,endpoint)
        headers={'X-API-Key':self.adyen_api_key}
        try:
            response=requests.request(method,url,json=payload,headers=headers,timeout=60)
            response.raise_for_status()
        exceptrequests.exceptions.ConnectionError:
            _logger.exception("unabletoreachendpointat%s",url)
            raiseValidationError("Adyen:"+_("CouldnotestablishtheconnectiontotheAPI."))
        exceptrequests.exceptions.HTTPErroraserror:
            _logger.exception(
                "invalidAPIrequestat%swithdata%s:%s",url,payload,error.response.text
            )
            raiseValidationError("Adyen:"+_("ThecommunicationwiththeAPIfailed."))
        returnresponse.json()

    def_adyen_compute_shopper_reference(self,partner_id):
        """ComputeauniquereferenceofthepartnerforAdyen.

        Thisisusedforthe`shopperReference`fieldincommunicationswithAdyenandstoredinthe
        `adyen_shopper_reference`fieldon`payment.token`ifthepaymentmethodistokenized.

        :paramrecordsetpartner_id:Thepartnermakingthetransaction,asa`res.partner`id
        :return:Theuniquereferenceforthepartner
        :rtype:str
        """
        return'FLECTRA_PARTNER_{partner_id}'.format(partner_id=partner_id)
