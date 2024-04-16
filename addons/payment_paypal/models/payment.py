#coding:utf-8

importjson
importlogging

importdateutil.parser
importpytz
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment_paypal.controllers.mainimportPaypalController
fromflectra.tools.float_utilsimportfloat_compare


_logger=logging.getLogger(__name__)


classAcquirerPaypal(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('paypal','Paypal')
    ],ondelete={'paypal':'setdefault'})
    paypal_email_account=fields.Char('Email',required_if_provider='paypal',groups='base.group_user')
    paypal_seller_account=fields.Char(
        'MerchantAccountID',groups='base.group_user',
        help='TheMerchantIDisusedtoensurecommunicationscomingfromPaypalarevalidandsecured.')
    paypal_use_ipn=fields.Boolean('UseIPN',default=True,help='PaypalInstantPaymentNotification',groups='base.group_user')
    paypal_pdt_token=fields.Char(string='PDTIdentityToken',help='PaymentDataTransferallowsyoutoreceivenotificationofsuccessfulpaymentsastheyaremade.',groups='base.group_user')
    #Defaultpaypalfees
    fees_dom_fixed=fields.Float(default=0.35)
    fees_dom_var=fields.Float(default=3.4)
    fees_int_fixed=fields.Float(default=0.35)
    fees_int_var=fields.Float(default=3.9)

    def_get_feature_support(self):
        """Getadvancedfeaturesupportbyprovider.

        Eachprovidershouldadditstechnicalinthecorresponding
        keyforthefollowingfeatures:
            *fees:supportpaymentfeescomputations
            *authorize:supportauthorizingpayment(separates
                         authorizationandcapture)
            *tokenize:supportsavingpaymentdatainapayment.tokenize
                        object
        """
        res=super(AcquirerPaypal,self)._get_feature_support()
        res['fees'].append('paypal')
        returnres

    @api.model
    def_get_paypal_urls(self,environment):
        """PaypalURLS"""
        ifenvironment=='prod':
            return{
                'paypal_form_url':'https://www.paypal.com/cgi-bin/webscr',
                'paypal_rest_url':'https://api.paypal.com/v1/oauth2/token',
            }
        else:
            return{
                'paypal_form_url':'https://www.sandbox.paypal.com/cgi-bin/webscr',
                'paypal_rest_url':'https://api.sandbox.paypal.com/v1/oauth2/token',
            }

    defpaypal_compute_fees(self,amount,currency_id,country_id):
        """Computepaypalfees.

            :paramfloatamount:theamounttopay
            :paramintegercountry_id:anIDofares.country,orNone.Thisis
                                       thecustomer'scountry,tobecomparedto
                                       theacquirercompanycountry.
            :returnfloatfees:computedfees
        """
        ifnotself.fees_active:
            return0.0
        country=self.env['res.country'].browse(country_id)
        ifcountryandself.company_id.sudo().country_id.id==country.id:
            percentage=self.fees_dom_var
            fixed=self.fees_dom_fixed
        else:
            percentage=self.fees_int_var
            fixed=self.fees_int_fixed
        fees=(percentage/100.0*amount+fixed)/(1-percentage/100.0)
        returnfees

    defpaypal_form_generate_values(self,values):
        base_url=self.get_base_url()

        paypal_tx_values=dict(values)
        paypal_tx_values.update({
            'cmd':'_xclick',
            'business':self.paypal_email_account,
            'item_name':'%s:%s'%(self.company_id.name,values['reference']),
            'item_number':values['reference'],
            'amount':values['amount'],
            'currency_code':values['currency']andvalues['currency'].nameor'',
            'address1':values.get('partner_address'),
            'city':values.get('partner_city'),
            'country':values.get('partner_country')andvalues.get('partner_country').codeor'',
            'state':values.get('partner_state')and(values.get('partner_state').codeorvalues.get('partner_state').name)or'',
            'email':values.get('partner_email'),
            'zip_code':values.get('partner_zip'),
            'first_name':values.get('partner_first_name'),
            'last_name':values.get('partner_last_name'),
            'paypal_return':urls.url_join(base_url,PaypalController._return_url),
            'notify_url':urls.url_join(base_url,PaypalController._notify_url),
            'cancel_return':urls.url_join(base_url,PaypalController._cancel_url),
            'handling':'%.2f'%paypal_tx_values.pop('fees',0.0)ifself.fees_activeelseFalse,
            'custom':json.dumps({'return_url':'%s'%paypal_tx_values.pop('return_url')})ifpaypal_tx_values.get('return_url')elseFalse,
        })
        returnpaypal_tx_values

    defpaypal_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_paypal_urls(environment)['paypal_form_url']


classTxPaypal(models.Model):
    _inherit='payment.transaction'

    paypal_txn_type=fields.Char('Transactiontype')

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_paypal_form_get_tx_from_data(self,data):
        reference,txn_id=data.get('item_number'),data.get('txn_id')
        ifnotreferenceornottxn_id:
            error_msg=_('Paypal:receiveddatawithmissingreference(%s)ortxn_id(%s)')%(reference,txn_id)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        #findtx->@TDENOTEusetxn_id?
        txs=self.env['payment.transaction'].search([('reference','=',reference)])
        ifnottxsorlen(txs)>1:
            error_msg='Paypal:receiveddataforreference%s'%(reference)
            ifnottxs:
                error_msg+=';noorderfound'
            else:
                error_msg+=';multipleorderfound'
            _logger.info(error_msg)
            raiseValidationError(error_msg)
        returntxs[0]

    def_paypal_form_get_invalid_parameters(self,data):
        invalid_parameters=[]
        _logger.info('ReceivedanotificationfromPaypalwithIPNversion%s',data.get('notify_version'))
        ifdata.get('test_ipn'):
            _logger.warning(
                'ReceivedanotificationfromPaypalusingsandbox'
            ),

        #TODO:txn_id:shoudlbefalseatdraft,setafterwards,andverifiedwithtxndetails
        ifself.acquirer_referenceanddata.get('txn_id')!=self.acquirer_reference:
            invalid_parameters.append(('txn_id',data.get('txn_id'),self.acquirer_reference))
        #checkwhatisbuyed
        iffloat_compare(float(data.get('mc_gross','0.0')),(self.amount+self.fees),2)!=0:
            invalid_parameters.append(('mc_gross',data.get('mc_gross'),'%.2f'%(self.amount+self.fees))) #mc_grossisamount+fees
        ifdata.get('mc_currency')!=self.currency_id.name:
            invalid_parameters.append(('mc_currency',data.get('mc_currency'),self.currency_id.name))
        if'handling_amount'indataandfloat_compare(float(data.get('handling_amount')),self.fees,2)!=0:
            invalid_parameters.append(('handling_amount',data.get('handling_amount'),self.fees))
        #checkbuyer
        ifself.payment_token_idanddata.get('payer_id')!=self.payment_token_id.acquirer_ref:
            invalid_parameters.append(('payer_id',data.get('payer_id'),self.payment_token_id.acquirer_ref))
        #checkseller
        ifdata.get('receiver_id')andself.acquirer_id.paypal_seller_accountanddata['receiver_id']!=self.acquirer_id.paypal_seller_account:
            invalid_parameters.append(('receiver_id',data.get('receiver_id'),self.acquirer_id.paypal_seller_account))
        ifnotdata.get('receiver_id')ornotself.acquirer_id.paypal_seller_account:
            #Checkreceiver_emailonlyifreceiver_idwasnotchecked.
            #InPaypal,thisispossibletoconfigureasreceiver_emailadifferentemailthanthebusinessemail(theloginemail)
            #InFlectra,thereisonlyonefieldforthePaypalemail:thebusinessemail.Thisisn'tpossibletosetareceiver_email
            #differentthanthebusinessemail.Therefore,ifyouwantsuchaconfigurationinyourPaypal,youarethenobligedtofill
            #theMerchantIDinthePaypalpaymentacquirerinFlectra,sothecheckisperformedonthisvariableinsteadofthereceiver_email.
            #Atleastoneofthetwochecksmustbedone,toavoidfraudsters.
            ifdata.get('receiver_email')anddata.get('receiver_email')!=self.acquirer_id.paypal_email_account:
                invalid_parameters.append(('receiver_email',data.get('receiver_email'),self.acquirer_id.paypal_email_account))
            ifdata.get('business')anddata.get('business')!=self.acquirer_id.paypal_email_account:
                invalid_parameters.append(('business',data.get('business'),self.acquirer_id.paypal_email_account))

        returninvalid_parameters

    def_paypal_form_validate(self,data):
        status=data.get('payment_status')
        former_tx_state=self.state
        res={
            'acquirer_reference':data.get('txn_id'),
            'paypal_txn_type':data.get('payment_type'),
        }
        ifnotself.acquirer_id.paypal_pdt_tokenandnotself.acquirer_id.paypal_seller_accountandstatusin['Completed','Processed','Pending']:
            template=self.env.ref('payment_paypal.mail_template_paypal_invite_user_to_configure',False)
            iftemplate:
                render_template=template._render({
                    'acquirer':self.acquirer_id,
                },engine='ir.qweb')
                mail_body=self.env['mail.render.mixin']._replace_local_links(render_template)
                mail_values={
                    'body_html':mail_body,
                    'subject':_('AddyourPaypalaccounttoFlectra'),
                    'email_to':self.acquirer_id.paypal_email_account,
                    'email_from':self.acquirer_id.create_uid.email_formatted,
                    'author_id':self.acquirer_id.create_uid.partner_id.id,
                }
                self.env['mail.mail'].sudo().create(mail_values).send()

        ifstatusin['Completed','Processed']:
            try:
                #dateutilandpytzdon'trecognizeabbreviationsPDT/PST
                tzinfos={
                    'PST':-8*3600,
                    'PDT':-7*3600,
                }
                date=dateutil.parser.parse(data.get('payment_date'),tzinfos=tzinfos).astimezone(pytz.utc).replace(tzinfo=None)
            except:
                date=fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            ifself.state=='done'andself.state!=former_tx_state:
                _logger.info('ValidatedPaypalpaymentfortx%s:setasdone'%(self.reference))
                returnself.write(res)
            returnTrue
        elifstatusin['Pending','Expired']:
            res.update(state_message=data.get('pending_reason',''))
            self._set_transaction_pending()
            ifself.state=='pending'andself.state!=former_tx_state:
                _logger.info('ReceivednotificationforPaypalpayment%s:setaspending'%(self.reference))
                returnself.write(res)
            returnTrue
        else:
            error='ReceivedunrecognizedstatusforPaypalpayment%s:%s,setaserror'%(self.reference,status)
            res.update(state_message=error)
            self._set_transaction_cancel()
            ifself.state=='cancel'andself.state!=former_tx_state:
                _logger.info(error)
                returnself.write(res)
            returnTrue
