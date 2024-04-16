#coding:utf-8

#Copyright2015Eezee-It

importdatetime
fromdateutilimportparser
importjson
importlogging
importpytz
importre
importtime
fromhashlibimportsha256

fromwerkzeugimporturls

fromflectraimportmodels,fields,api
fromflectra.tools.float_utilsimportfloat_compare
fromflectra.tools.translateimport_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment_sips.controllers.mainimportSipsController

from.constimportSIPS_SUPPORTED_CURRENCIES

_logger=logging.getLogger(__name__)


classAcquirerSips(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[('sips','Sips')],ondelete={'sips':'setdefault'})
    sips_merchant_id=fields.Char('MerchantID',required_if_provider='sips',groups='base.group_user')
    sips_secret=fields.Char('SecretKey',size=64,required_if_provider='sips',groups='base.group_user')
    sips_test_url=fields.Char("Testurl",required_if_provider='sips',default='https://payment-webinit.simu.sips-services.com/paymentInit')
    sips_prod_url=fields.Char("Productionurl",required_if_provider='sips',default='https://payment-webinit.sips-services.com/paymentInit')
    sips_version=fields.Char("InterfaceVersion",required_if_provider='sips',default='HP_2.31')
    sips_key_version=fields.Integer("SecretKeyVersion",required_if_provider='sips',default=2)

    def_sips_generate_shasign(self,values):
        """Generatetheshasignforincomingoroutgoingcommunications.
        :paramdictvalues:transactionvalues
        :returnstring:shasign
        """
        ifself.provider!='sips':
            raiseValidationError(_('Incorrectpaymentacquirerprovider'))
        data=values['Data']
        key=self.sips_secret

        shasign=sha256((data+key).encode('utf-8'))
        returnshasign.hexdigest()

    defsips_form_generate_values(self,values):
        self.ensure_one()
        base_url=self.get_base_url()
        currency=self.env['res.currency'].sudo().browse(values['currency_id'])
        sips_currency=SIPS_SUPPORTED_CURRENCIES.get(currency.name)
        ifnotsips_currency:
            raiseValidationError(_('CurrencynotsupportedbyWordline:%s')%currency.name)
        #roundedtoitssmallestunit,dependsonthecurrency
        amount=round(values['amount']*(10**sips_currency.decimal))

        sips_tx_values=dict(values)
        data={
            'amount':amount,
            'currencyCode':sips_currency.iso_id,
            'merchantId':self.sips_merchant_id,
            'normalReturnUrl':urls.url_join(base_url,SipsController._return_url),
            'automaticResponseUrl':urls.url_join(base_url,SipsController._notify_url),
            'transactionReference':values['reference'],
            'statementReference':values['reference'],
            'keyVersion':self.sips_key_version,
        }
        sips_tx_values.update({
            'Data':'|'.join([f'{k}={v}'fork,vindata.items()]),
            'InterfaceVersion':self.sips_version,
        })

        return_context={}
        ifsips_tx_values.get('return_url'):
            return_context['return_url']=urls.url_quote(sips_tx_values.get('return_url'))
        return_context['reference']=sips_tx_values['reference']
        sips_tx_values['Data']+='|returnContext=%s'%(json.dumps(return_context))

        shasign=self._sips_generate_shasign(sips_tx_values)
        sips_tx_values['Seal']=shasign
        returnsips_tx_values

    defsips_get_form_action_url(self):
        self.ensure_one()
        returnself.sips_prod_urlifself.state=='enabled'elseself.sips_test_url


classTxSips(models.Model):
    _inherit='payment.transaction'

    _sips_valid_tx_status=['00']
    _sips_wait_tx_status=['90','99']
    _sips_refused_tx_status=['05','14','34','54','75','97']
    _sips_error_tx_status=['03','12','24','25','30','40','51','63','94']
    _sips_pending_tx_status=['60']
    _sips_cancel_tx_status=['17']

    @api.model
    def_compute_reference(self,values=None,prefix=None):
        res=super()._compute_reference(values=values,prefix=prefix)
        acquirer=self.env['payment.acquirer'].browse(values.get('acquirer_id'))
        ifacquirerandacquirer.provider=='sips':
            returnre.sub(r'[^0-9a-zA-Z]+','x',res)+'x'+str(int(time.time()))
        returnres

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    def_sips_data_to_object(self,data):
        res={}
        forelementindata.split('|'):
            (key,value)=element.split('=')
            res[key]=value
        returnres

    @api.model
    def_sips_form_get_tx_from_data(self,data):
        """Givenadatadictcomingfromsips,verifyitandfindtherelated
        transactionrecord."""

        data=self._sips_data_to_object(data.get('Data'))
        reference=data.get('transactionReference')

        ifnotreference:
            return_context=json.loads(data.get('returnContext','{}'))
            reference=return_context.get('reference')

        payment_tx=self.search([('reference','=',reference)])
        ifnotpayment_tx:
            error_msg=_('Sips:receiveddataforreference%s;noorderfound')%reference
            _logger.error(error_msg)
            raiseValidationError(error_msg)
        returnpayment_tx

    def_sips_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        data=self._sips_data_to_object(data.get('Data'))

        #amountsshouldmatch
        #getcurrencydecimalsfromconst
        sips_currency=SIPS_SUPPORTED_CURRENCIES.get(self.currency_id.name)
        #convertfrominttofloatusingdecimalsfromcurrency
        amount_converted=float(data.get('amount','0.0'))/(10**sips_currency.decimal)
        iffloat_compare(amount_converted,self.amount,sips_currency.decimal)!=0:
            invalid_parameters.append(('amount',data.get('amount'),'%.2f'%self.amount))

        returninvalid_parameters

    def_sips_form_validate(self,data):
        data=self._sips_data_to_object(data.get('Data'))
        status=data.get('responseCode')
        date=data.get('transactionDateTime')
        ifdate:
            try:
                #dateutil.parser2.5.3andupshouldhandledatesformattedas
                #'2020-04-08T05:54:18+02:00',whichstrptimedoesnot
                #(+02:00doesnotworkas%zexpects+0200beforePython3.7)
                #Seeflectra/flectra#49160
                date=parser.parse(date).astimezone(pytz.utc).replace(tzinfo=None)
            except:
                #fallbackonnowtoavoidfailingtoregisterthepayment
                #becauseaproviderformatstheirdatesbadlyorbecause
                #somelibraryisnotbehaving
                date=fields.Datetime.now()
        data={
            'acquirer_reference':data.get('transactionReference'),
            'date':date,
        }
        res=False
        ifstatusinself._sips_valid_tx_status:
            msg=f'ref:{self.reference},gotvalidresponse[{status}],setasdone.'
            _logger.info(msg)
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_done()
            res=True
        elifstatusinself._sips_error_tx_status:
            msg=f'ref:{self.reference},gotresponse[{status}],setascancel.'
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_cancel()
        elifstatusinself._sips_wait_tx_status:
            msg=f'ref:{self.reference},gotwaitresponse[{status}],setascancel.'
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_cancel()
        elifstatusinself._sips_refused_tx_status:
            msg=f'ref:{self.reference},gotrefusedresponse[{status}],setascancel.'
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_cancel()
        elifstatusinself._sips_pending_tx_status:
            msg=f'ref:{self.reference},gotpendingresponse[{status}],setaspending.'
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_pending()
        elifstatusinself._sips_cancel_tx_status:
            msg=f'ref:{self.reference},gotcancelresponse[{status}],setascancel.'
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_cancel()
        else:
            msg=f'ref:{self.reference},gotunrecognizedresponse[{status}],setascancel.'
            data.update(state_message=msg)
            self.write(data)
            self._set_transaction_cancel()

        _logger.info(msg)
        returnres
