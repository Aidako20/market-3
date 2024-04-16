#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdecimal
importlogging
importuuid

fromhashlibimportmd5
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.tools.float_utilsimportfloat_compare,float_round,float_split


_logger=logging.getLogger(__name__)


classPaymentAcquirerPayulatam(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('payulatam','PayULatam')
    ],ondelete={'payulatam':'setdefault'})
    payulatam_merchant_id=fields.Char(string="PayULatamMerchantID",required_if_provider='payulatam',groups='base.group_user')
    payulatam_account_id=fields.Char(string="PayULatamAccountID",required_if_provider='payulatam',groups='base.group_user')
    payulatam_api_key=fields.Char(string="PayULatamAPIKey",required_if_provider='payulatam',groups='base.group_user')

    def_get_payulatam_urls(self,environment):
        """PayUlatamURLs"""
        ifenvironment=='prod':
            return'https://checkout.payulatam.com/ppp-web-gateway-payu/'
        return'https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu/'

    def_payulatam_generate_sign(self,inout,values):
        ifinoutnotin('in','out'):
            raiseException("Typemustbe'in'or'out'")

        ifinout=='in':
            data_string=('~').join((self.payulatam_api_key,self.payulatam_merchant_id,values['referenceCode'],
                                      str(values['amount']),values['currency']))
        else:
            #"Confirmation"and"Response"pageshaveadifferentwaytocalculatewhattheycallthe`new_value`
            ifself.env.context.get('payulatam_is_confirmation_page'):
                #https://developers.payulatam.com/latam/en/docs/integrations/webcheckout-integration/confirmation-page.html#signature-validation
                #Forconfirmationpage,PayULatamroundtothefirstdigitifthesecondoneisazero
                #togeneratetheirsignature.
                #e.g:
                # 150.00->150.0
                # 150.26->150.26
                #ThishappenstobePython3'sdefaultbehaviorwhencastingto`float`.
                new_value="%d.%d"%float_split(float(values.get('TX_VALUE')),2)
            else:
                #https://developers.payulatam.com/latam/en/docs/integrations/webcheckout-integration/response-page.html#signature-validation
                #PayULatamusethe"Roundhalftoeven"roundingmethodtogeneratetheirsignature.
                new_value=decimal.Decimal(values.get('TX_VALUE')).quantize(
                    decimal.Decimal('0.1'),decimal.ROUND_HALF_EVEN)
            data_string=('~').join((self.payulatam_api_key,self.payulatam_merchant_id,values['referenceCode'],
                                      str(new_value),values['currency'],values.get('transactionState')))
        returnmd5(data_string.encode('utf-8')).hexdigest()

    defpayulatam_form_generate_values(self,values):
        tx=self.env['payment.transaction'].search([('reference','=',values.get('reference'))])
        #payulatamwillnotallowanypaymenttwiseevenifpaymentwasfailedlasttime.
        #so,replacereferencecodeifpaymentisnotdoneorpending.
        iftx.statenotin['done','pending']:
            tx.reference=str(uuid.uuid4())
        payulatam_values=dict(
            values,
            merchantId=self.payulatam_merchant_id,
            accountId=self.payulatam_account_id,
            description=values.get('reference'),
            referenceCode=tx.reference,
            amount=float_round(values['amount'],2),
            tax='0', #ThisisthetransactionVAT.IfVATzeroissentthesystem,19%willbeappliedautomatically.Itcancontaintwodecimals.Eg19000.00.InthewhereyoudonotchargeVAT,itshouldshouldbesetas0.
            taxReturnBase='0',
            currency=values['currency'].name,
            buyerEmail=values['partner_email'],
            responseUrl=urls.url_join(self.get_base_url(),'/payment/payulatam/response'),
            confirmationUrl=urls.url_join(self.get_base_url(),'/payment/payulatam/webhook'),
        )
        payulatam_values['signature']=self._payulatam_generate_sign("in",payulatam_values)
        returnpayulatam_values

    defpayulatam_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_payulatam_urls(environment)


classPaymentTransactionPayulatam(models.Model):
    _inherit='payment.transaction'

    @api.model
    def_payulatam_form_get_tx_from_data(self,data):
        """Givenadatadictcomingfrompayulatam,verifyitandfindtherelated
        transactionrecord."""
        reference,txnid,sign=data.get('referenceCode'),data.get('transactionId'),data.get('signature')
        ifnotreferenceornottxnidornotsign:
            raiseValidationError(_('PayULatam:receiveddatawithmissingreference(%s)ortransactionid(%s)orsign(%s)')%(reference,txnid,sign))

        transaction=self.search([('reference','=',reference)])

        ifnottransaction:
            error_msg=(_('PayULatam:receiveddataforreference%s;noorderfound')%(reference))
            raiseValidationError(error_msg)
        eliflen(transaction)>1:
            error_msg=(_('PayULatam:receiveddataforreference%s;multipleordersfound')%(reference))
            raiseValidationError(error_msg)

        #verifyshasign
        sign_check=transaction.acquirer_id._payulatam_generate_sign('out',data)
        ifsign_check.upper()!=sign.upper():
            raiseValidationError(('PayULatam:invalidsign,received%s,computed%s,fordata%s')%(sign,sign_check,data))
        returntransaction

    def_payulatam_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        ifself.acquirer_referenceanddata.get('transactionId')!=self.acquirer_reference:
            invalid_parameters.append(('Referencecode',data.get('transactionId'),self.acquirer_reference))
        iffloat_compare(float(data.get('TX_VALUE','0.0')),self.amount,2)!=0:
            invalid_parameters.append(('Amount',data.get('TX_VALUE'),'%.2f'%self.amount))
        ifdata.get('merchantId')!=self.acquirer_id.payulatam_merchant_id:
            invalid_parameters.append(('MerchantId',data.get('merchantId'),self.acquirer_id.payulatam_merchant_id))
        returninvalid_parameters

    def_payulatam_form_validate(self,data):
        self.ensure_one()

        status=data.get('lapTransactionState')ordata.find('transactionResponse').find('state').text
        res={
            'acquirer_reference':data.get('transactionId')ordata.find('transactionResponse').find('transactionId').text,
            'state_message':data.get('message')or""
        }

        ifstatus=='APPROVED':
            _logger.info('ValidatedPayULatampaymentfortx%s:setasdone'%(self.reference))
            res.update(state='done',date=fields.Datetime.now())
            self._set_transaction_done()
            self.write(res)
            self.execute_callback()
            returnTrue
        elifstatus=='PENDING':
            _logger.info('ReceivednotificationforPayULatampayment%s:setaspending'%(self.reference))
            res.update(state='pending')
            self._set_transaction_pending()
            returnself.write(res)
        elifstatusin['EXPIRED','DECLINED']:
            _logger.info('ReceivednotificationforPayULatampayment%s:setasCancel'%(self.reference))
            res.update(state='cancel')
            self._set_transaction_cancel()
            returnself.write(res)
        else:
            error='ReceivedunrecognizedstatusforPayULatampayment%s:%s,setaserror'%(self.reference,status)
            _logger.info(error)
            res.update(state='cancel',state_message=error)
            self._set_transaction_cancel()
            returnself.write(res)
