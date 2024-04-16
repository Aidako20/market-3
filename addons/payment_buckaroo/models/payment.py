#coding:utf-8
fromhashlibimportsha1
importlogging

fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment_buckaroo.controllers.mainimportBuckarooController

fromflectra.tools.float_utilsimportfloat_compare

_logger=logging.getLogger(__name__)


defnormalize_keys_upper(data):
    """Setallkeysofadictionnarytouppercase

    Buckarooparametersnamesarecaseinsensitive
    converteverythingtouppercasetobeabletoeasilydetectedthepresence
    ofaparameterbycheckingtheuppercasekeyonly
    """
    return{key.upper():valforkey,valindata.items()}


classAcquirerBuckaroo(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('buckaroo','Buckaroo')
    ],ondelete={'buckaroo':'setdefault'})
    brq_websitekey=fields.Char('WebsiteKey',required_if_provider='buckaroo',groups='base.group_user')
    brq_secretkey=fields.Char('SecretKey',required_if_provider='buckaroo',groups='base.group_user')

    def_get_buckaroo_urls(self,environment):
        """BuckarooURLs
        """
        ifenvironment=='prod':
            return{
                'buckaroo_form_url':'https://checkout.buckaroo.nl/html/',
            }
        else:
            return{
                'buckaroo_form_url':'https://testcheckout.buckaroo.nl/html/',
            }

    def_buckaroo_generate_digital_sign(self,inout,values):
        """Generatetheshasignforincomingoroutgoingcommunications.

        :parambrowseacquirer:thepayment.acquirerbrowserecord.Itshould
                                haveashakeyinshakyout
        :paramstringinout:'in'(flectracontactingbuckaroo)or'out'(buckaroo
                             contactingflectra).
        :paramdictvalues:transactionvalues

        :returnstring:shasign
        """
        assertinoutin('in','out')
        assertself.provider=='buckaroo'

        keys="add_returndataBrq_amountBrq_cultureBrq_currencyBrq_invoicenumberBrq_returnBrq_returncancelBrq_returnerrorBrq_returnrejectbrq_testBrq_websitekey".split()

        defget_value(key):
            ifvalues.get(key):
                returnvalues[key]
            return''

        values=dict(valuesor{})

        ifinout=='out':
            forkeyinlist(values):
                #caseinsensitivekeys
                ifkey.upper()=='BRQ_SIGNATURE':
                    delvalues[key]
                    break

            items=sorted(values.items(),key=lambdapair:pair[0].lower())
            sign=''.join('%s=%s'%(k,urls.url_unquote_plus(v))fork,vinitems)
        else:
            sign=''.join('%s=%s'%(k,get_value(k))forkinkeys)
        #Addthepre-sharedsecretkeyattheendofthesignature
        sign=sign+self.brq_secretkey
        shasign=sha1(sign.encode('utf-8')).hexdigest()
        returnshasign

    defbuckaroo_form_generate_values(self,values):
        base_url=self.get_base_url()
        buckaroo_tx_values=dict(values)
        buckaroo_tx_values.update({
            'Brq_websitekey':self.brq_websitekey,
            'Brq_amount':values['amount'],
            'Brq_currency':values['currency']andvalues['currency'].nameor'',
            'Brq_invoicenumber':values['reference'],
            'brq_test':Trueifself.state=='test'elseFalse,
            'Brq_return':urls.url_join(base_url,BuckarooController._return_url),
            'Brq_returncancel':urls.url_join(base_url,BuckarooController._cancel_url),
            'Brq_returnerror':urls.url_join(base_url,BuckarooController._exception_url),
            'Brq_returnreject':urls.url_join(base_url,BuckarooController._reject_url),
            'Brq_culture':(values.get('partner_lang')or'en_US').replace('_','-'),
            'add_returndata':buckaroo_tx_values.pop('return_url','')or'',
        })
        buckaroo_tx_values['Brq_signature']=self._buckaroo_generate_digital_sign('in',buckaroo_tx_values)
        returnbuckaroo_tx_values

    defbuckaroo_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_buckaroo_urls(environment)['buckaroo_form_url']


classTxBuckaroo(models.Model):
    _inherit='payment.transaction'

    #buckaroostatus
    _buckaroo_valid_tx_status=[190]
    _buckaroo_pending_tx_status=[790,791,792,793]
    _buckaroo_cancel_tx_status=[890,891]
    _buckaroo_error_tx_status=[490,491,492]
    _buckaroo_reject_tx_status=[690]

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_buckaroo_form_get_tx_from_data(self,data):
        """Givenadatadictcomingfrombuckaroo,verifyitandfindtherelated
        transactionrecord."""
        origin_data=dict(data)
        data=normalize_keys_upper(data)
        reference,pay_id,shasign=data.get('BRQ_INVOICENUMBER'),data.get('BRQ_PAYMENT'),data.get('BRQ_SIGNATURE')
        ifnotreferenceornotpay_idornotshasign:
            error_msg=_('Buckaroo:receiveddatawithmissingreference(%s)orpay_id(%s)orshasign(%s)')%(reference,pay_id,shasign)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        tx=self.search([('reference','=',reference)])
        ifnottxorlen(tx)>1:
            error_msg=_('Buckaroo:receiveddataforreference%s')%(reference)
            ifnottx:
                error_msg+=_(';noorderfound')
            else:
                error_msg+=_(';multipleorderfound')
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        #verifyshasign
        shasign_check=tx.acquirer_id._buckaroo_generate_digital_sign('out',origin_data)
        ifshasign_check.upper()!=shasign.upper():
            error_msg=_('Buckaroo:invalidshasign,received%s,computed%s,fordata%s')%(shasign,shasign_check,data)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        returntx

    def_buckaroo_form_get_invalid_parameters(self,data):
        invalid_parameters=[]
        data=normalize_keys_upper(data)
        ifself.acquirer_referenceanddata.get('BRQ_TRANSACTIONS')!=self.acquirer_reference:
            invalid_parameters.append(('TransactionId',data.get('BRQ_TRANSACTIONS'),self.acquirer_reference))
        #checkwhatisbuyed
        iffloat_compare(float(data.get('BRQ_AMOUNT','0.0')),self.amount,2)!=0:
            invalid_parameters.append(('Amount',data.get('BRQ_AMOUNT'),'%.2f'%self.amount))
        ifdata.get('BRQ_CURRENCY')!=self.currency_id.name:
            invalid_parameters.append(('Currency',data.get('BRQ_CURRENCY'),self.currency_id.name))

        returninvalid_parameters

    def_buckaroo_form_validate(self,data):
        data=normalize_keys_upper(data)
        status_code=int(data.get('BRQ_STATUSCODE','0'))
        ifstatus_codeinself._buckaroo_valid_tx_status:
            self.write({'acquirer_reference':data.get('BRQ_TRANSACTIONS')})
            self._set_transaction_done()
            returnTrue
        elifstatus_codeinself._buckaroo_pending_tx_status:
            self.write({'acquirer_reference':data.get('BRQ_TRANSACTIONS')})
            self._set_transaction_pending()
            returnTrue
        elifstatus_codeinself._buckaroo_cancel_tx_status:
            self.write({'acquirer_reference':data.get('BRQ_TRANSACTIONS')})
            self._set_transaction_cancel()
            returnTrue
        else:
            error='Buckaroo:feedbackerror'
            _logger.info(error)
            self.write({
                'state_message':error,
                'acquirer_reference':data.get('BRQ_TRANSACTIONS'),
            })
            self._set_transaction_cancel()
            returnFalse
