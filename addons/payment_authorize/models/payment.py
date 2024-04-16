#coding:utf-8
fromwerkzeugimporturls

from.authorize_requestimportAuthorizeAPI
importhashlib
importhmac
importlogging
importtime

fromflectraimport_,api,fields,models
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment_authorize.controllers.mainimportAuthorizeController
fromflectra.tools.float_utilsimportfloat_compare,float_repr
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)


classPaymentAcquirerAuthorize(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('authorize','Authorize.Net')
    ],ondelete={'authorize':'setdefault'})
    authorize_login=fields.Char(string='APILoginId',required_if_provider='authorize',groups='base.group_user')
    authorize_transaction_key=fields.Char(string='APITransactionKey',required_if_provider='authorize',groups='base.group_user')
    authorize_signature_key=fields.Char(string='APISignatureKey',required_if_provider='authorize',groups='base.group_user')
    authorize_client_key=fields.Char(string='APIClientKey',groups='base.group_user')

    @api.onchange('provider','check_validity')
    defonchange_check_validity(self):
        ifself.provider=='authorize'andself.check_validity:
            self.check_validity=False
            return{'warning':{
                'title':_("Warning"),
                'message':('ThisoptionisnotsupportedforAuthorize.net')}}

    defaction_client_secret(self):
        api=AuthorizeAPI(self)
        ifnotapi.test_authenticate():
            raiseUserError(_('UnabletofetchClientKey,makesuretheAPILoginandTransactionKeyarecorrect.'))
        self.authorize_client_key=api.get_client_secret()
        returnTrue

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
        res=super(PaymentAcquirerAuthorize,self)._get_feature_support()
        res['authorize'].append('authorize')
        res['tokenize'].append('authorize')
        returnres

    def_get_authorize_urls(self,environment):
        """AuthorizeURLs"""
        ifenvironment=='prod':
            return{'authorize_form_url':'https://secure2.authorize.net/gateway/transact.dll'}
        else:
            return{'authorize_form_url':'https://test.authorize.net/gateway/transact.dll'}

    def_authorize_generate_hashing(self,values):
        data='^'.join([
            values['x_login'],
            values['x_fp_sequence'],
            values['x_fp_timestamp'],
            values['x_amount'],
            values['x_currency_code']]).encode('utf-8')

        returnhmac.new(bytes.fromhex(self.authorize_signature_key),data,hashlib.sha512).hexdigest().upper()

    defauthorize_form_generate_values(self,values):
        self.ensure_one()
        #StatecodeisonlysupportedinUS,usestatenamebydefault
        #Seehttps://developer.authorize.net/api/reference/
        state=values['partner_state'].nameifvalues.get('partner_state')else''
        ifvalues.get('partner_country')andvalues.get('partner_country')==self.env.ref('base.us',False):
            state=values['partner_state'].codeifvalues.get('partner_state')else''
        billing_state=values['billing_partner_state'].nameifvalues.get('billing_partner_state')else''
        ifvalues.get('billing_partner_country')andvalues.get('billing_partner_country')==self.env.ref('base.us',False):
            billing_state=values['billing_partner_state'].codeifvalues.get('billing_partner_state')else''

        base_url=self.get_base_url()
        authorize_tx_values=dict(values)
        temp_authorize_tx_values={
            'x_login':self.authorize_login,
            'x_amount':float_repr(values['amount'],values['currency'].decimal_placesifvalues['currency']else2),
            'x_show_form':'PAYMENT_FORM',
            'x_type':'AUTH_CAPTURE'ifnotself.capture_manuallyelse'AUTH_ONLY',
            'x_method':'CC',
            'x_fp_sequence':'%s%s'%(self.id,int(time.time())),
            'x_version':'3.1',
            'x_relay_response':'TRUE',
            'x_fp_timestamp':str(int(time.time())),
            'x_relay_url':urls.url_join(base_url,AuthorizeController._return_url),
            'x_cancel_url':urls.url_join(base_url,AuthorizeController._cancel_url),
            'x_currency_code':values['currency']andvalues['currency'].nameor'',
            'address':values.get('partner_address'),
            'city':values.get('partner_city'),
            'country':values.get('partner_country')andvalues.get('partner_country').nameor'',
            'email':values.get('partner_email'),
            'zip_code':values.get('partner_zip'),
            'first_name':values.get('partner_first_name'),
            'last_name':values.get('partner_last_name'),
            'phone':values.get('partner_phone'),
            'state':state,
            'billing_address':values.get('billing_partner_address'),
            'billing_city':values.get('billing_partner_city'),
            'billing_country':values.get('billing_partner_country')andvalues.get('billing_partner_country').nameor'',
            'billing_email':values.get('billing_partner_email'),
            'billing_zip_code':values.get('billing_partner_zip'),
            'billing_first_name':values.get('billing_partner_first_name'),
            'billing_last_name':values.get('billing_partner_last_name'),
            'billing_phone':values.get('billing_partner_phone'),
            'billing_state':billing_state,
        }
        temp_authorize_tx_values['returndata']=authorize_tx_values.pop('return_url','')
        temp_authorize_tx_values['x_fp_hash']=self._authorize_generate_hashing(temp_authorize_tx_values)
        authorize_tx_values.update(temp_authorize_tx_values)
        returnauthorize_tx_values

    defauthorize_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_authorize_urls(environment)['authorize_form_url']

    @api.model
    defauthorize_s2s_form_process(self,data):
        values={
            'opaqueData':data.get('opaqueData'),
            'encryptedCardData':data.get('encryptedCardData'),
            'acquirer_id':int(data.get('acquirer_id')),
            'partner_id':int(data.get('partner_id'))
        }
        PaymentMethod=self.env['payment.token'].sudo().create(values)
        returnPaymentMethod

    defauthorize_s2s_form_validate(self,data):
        error=dict()
        mandatory_fields=["opaqueData","encryptedCardData"]
        #Validation
        forfield_nameinmandatory_fields:
            ifnotdata.get(field_name):
                error[field_name]='missing'
        returnFalseiferrorelseTrue

    defauthorize_test_credentials(self):
        self.ensure_one()
        transaction=AuthorizeAPI(self.acquirer_id)
        returntransaction.test_authenticate()

classTxAuthorize(models.Model):
    _inherit='payment.transaction'

    _authorize_valid_tx_status=1
    _authorize_pending_tx_status=4
    _authorize_cancel_tx_status=2
    _authorize_error_tx_status=3

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_authorize_form_get_tx_from_data(self,data):
        """Givenadatadictcomingfromauthorize,verifyitandfindtherelated
        transactionrecord."""
        reference,description,trans_id,fingerprint=data.get('x_invoice_num'),data.get('x_description'),data.get('x_trans_id'),data.get('x_SHA2_Hash')ordata.get('x_MD5_Hash')
        ifnotreferenceornottrans_idornotfingerprint:
            error_msg=_('Authorize:receiveddatawithmissingreference(%s)ortrans_id(%s)orfingerprint(%s)')%(reference,trans_id,fingerprint)
            _logger.info(error_msg)
            raiseValidationError(error_msg)
        tx=self.search(['|',('reference','=',reference),('reference','=',description)])
        ifnottxorlen(tx)>1:
            error_msg='Authorize:receiveddataforx_invoice_num%sandx_description%s'%(reference,description)
            ifnottx:
                error_msg+=';noorderfound'
            else:
                error_msg+=';multipleorderfound'
            _logger.info(error_msg)
            raiseValidationError(error_msg)
        returntx[0]

    def_authorize_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        ifself.acquirer_referenceanddata.get('x_trans_id')!=self.acquirer_reference:
            invalid_parameters.append(('TransactionId',data.get('x_trans_id'),self.acquirer_reference))
        #checkwhatisbuyed
        iffloat_compare(float(data.get('x_amount','0.0')),self.amount,2)!=0:
            invalid_parameters.append(('Amount',data.get('x_amount'),'%.2f'%self.amount))
        returninvalid_parameters

    def_authorize_form_validate(self,data):
        ifself.state=='done':
            _logger.warning('Authorize:tryingtovalidateanalreadyvalidatedtx(ref%s)'%self.reference)
            returnTrue
        status_code=int(data.get('x_response_code','0'))
        ifstatus_code==self._authorize_valid_tx_status:
            ifdata.get('x_type').lower()in['auth_capture','prior_auth_capture']:
                self.write({
                    'acquirer_reference':data.get('x_trans_id'),
                    'date':fields.Datetime.now(),
                })
                self._set_transaction_done()
            elifdata.get('x_type').lower()in['auth_only']:
                self.write({'acquirer_reference':data.get('x_trans_id')})
                self._set_transaction_authorized()
            ifself.partner_idandnotself.payment_token_idand\
               (self.type=='form_save'orself.acquirer_id.save_token=='always'):
                transaction=AuthorizeAPI(self.acquirer_id)
                res=transaction.create_customer_profile_from_tx(self.partner_id,self.acquirer_reference)
                ifres:
                    token_id=self.env['payment.token'].create({
                        'authorize_profile':res.get('profile_id'),
                        'name':res.get('name'),
                        'acquirer_ref':res.get('payment_profile_id'),
                        'acquirer_id':self.acquirer_id.id,
                        'partner_id':self.partner_id.id,
                    })
                    self.payment_token_id=token_id
            returnTrue
        elifstatus_code==self._authorize_pending_tx_status:
            self.write({'acquirer_reference':data.get('x_trans_id')})
            self._set_transaction_pending()
            returnTrue
        else:
            error=data.get('x_response_reason_text')
            _logger.info(error)
            self.write({
                'state_message':error,
                'acquirer_reference':data.get('x_trans_id'),
            })
            self._set_transaction_cancel()
            returnFalse

    defauthorize_s2s_do_transaction(self,**data):
        self.ensure_one()
        transaction=AuthorizeAPI(self.acquirer_id)

        ifnotself.payment_token_id.authorize_profile:
            raiseUserError(_('Invalidtokenfound:theAuthorizeprofileismissing.'
                              'Pleasemakesurethetokenhasavalidacquirerreference.'))

        ifnotself.acquirer_id.capture_manually:
            res=transaction.auth_and_capture(self.payment_token_id,round(self.amount,self.currency_id.decimal_places),self.reference)
        else:
            res=transaction.authorize(self.payment_token_id,round(self.amount,self.currency_id.decimal_places),self.reference)
        returnself._authorize_s2s_validate_tree(res)

    defauthorize_s2s_capture_transaction(self):
        self.ensure_one()
        transaction=AuthorizeAPI(self.acquirer_id)
        tree=transaction.capture(self.acquirer_referenceor'',round(self.amount,self.currency_id.decimal_places))
        returnself._authorize_s2s_validate_tree(tree)

    defauthorize_s2s_void_transaction(self):
        self.ensure_one()
        transaction=AuthorizeAPI(self.acquirer_id)
        tree=transaction.void(self.acquirer_referenceor'')
        returnself._authorize_s2s_validate_tree(tree)

    def_authorize_s2s_validate_tree(self,tree):
        returnself._authorize_s2s_validate(tree)

    def_authorize_s2s_validate(self,tree):
        ifself.state=='done':
            _logger.warning('Authorize:tryingtovalidateanalreadyvalidatedtx(ref%s)'%self.reference)
            returnTrue
        status_code=int(tree.get('x_response_code','0'))
        ifstatus_code==self._authorize_valid_tx_status:
            iftree.get('x_type').lower()in['auth_capture','prior_auth_capture']:
                init_state=self.state
                self.write({
                    'acquirer_reference':tree.get('x_trans_id'),
                    'date':fields.Datetime.now(),
                })

                self._set_transaction_done()

                ifinit_state!='authorized':
                    self.execute_callback()
            iftree.get('x_type').lower()=='auth_only':
                self.write({'acquirer_reference':tree.get('x_trans_id')})
                self._set_transaction_authorized()
                self.execute_callback()
            iftree.get('x_type').lower()=='void':
                self._set_transaction_cancel()
            returnTrue
        elifstatus_code==self._authorize_pending_tx_status:
            self.write({'acquirer_reference':tree.get('x_trans_id')})
            self._set_transaction_pending()
            returnTrue
        else:
            error=tree.get('x_response_reason_text')
            _logger.info(error)
            self.write({
                'acquirer_reference':tree.get('x_trans_id'),
            })
            self._set_transaction_error(msg=error)
            returnFalse


classPaymentToken(models.Model):
    _inherit='payment.token'

    authorize_profile=fields.Char(string='Authorize.netProfileID',help='Thiscontainstheuniquereference'
                                    'forthispartner/paymenttokencombinationintheAuthorize.netbackend')
    provider=fields.Selection(string='Provider',related='acquirer_id.provider',readonly=False)
    save_token=fields.Selection(string='SaveCards',related='acquirer_id.save_token',readonly=False)

    @api.model
    defauthorize_create(self,values):
        ifvalues.get('opaqueData')andvalues.get('encryptedCardData'):
            acquirer=self.env['payment.acquirer'].browse(values['acquirer_id'])
            partner=self.env['res.partner'].browse(values['partner_id'])
            transaction=AuthorizeAPI(acquirer)
            res=transaction.create_customer_profile(partner,values['opaqueData'])
            ifres.get('profile_id')andres.get('payment_profile_id'):
                return{
                    'authorize_profile':res.get('profile_id'),
                    'name':values['encryptedCardData'].get('cardNumber'),
                    'acquirer_ref':res.get('payment_profile_id'),
                    'verified':True
                }
            else:
                raiseValidationError(_('TheCustomerProfilecreationinAuthorize.NETfailed.'))
        else:
            returnvalues
