#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson
importlogging
importpprint
importrandom
importrequests
importstring
fromwerkzeug.exceptionsimportForbidden

fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError

_logger=logging.getLogger(__name__)

classPosPaymentMethod(models.Model):
    _inherit='pos.payment.method'

    def_get_payment_terminal_selection(self):
        returnsuper(PosPaymentMethod,self)._get_payment_terminal_selection()+[('flectra_adyen','FlectraPaymentsbyAdyen'),('adyen','Adyen')]

    #Adyen
    adyen_api_key=fields.Char(string="AdyenAPIkey",help='UsedwhenconnectingtoAdyen:https://docs.adyen.com/user-management/how-to-get-the-api-key/#description',copy=False)
    adyen_terminal_identifier=fields.Char(help='[Terminalmodel]-[Serialnumber],forexample:P400Plus-123456789',copy=False)
    adyen_test_mode=fields.Boolean(help='Runtransactionsinthetestenvironment.')

    #FlectraPaymentsbyAdyen
    adyen_account_id=fields.Many2one('adyen.account',related='company_id.adyen_account_id')
    adyen_payout_id=fields.Many2one('adyen.payout',string='AdyenPayout',domain="[('adyen_account_id','=',adyen_account_id)]")
    adyen_terminal_id=fields.Many2one('adyen.terminal',string='AdyenTerminal',domain="[('adyen_account_id','=',adyen_account_id)]")

    adyen_latest_response=fields.Char(help='TechnicalfieldusedtobufferthelatestasynchronousnotificationfromAdyen.',copy=False,groups='base.group_erp_manager')
    adyen_latest_diagnosis=fields.Char(help='Technicalfieldusedtodetermineiftheterminalisstillconnected.',copy=False,groups='base.group_erp_manager')

    @api.constrains('adyen_terminal_identifier')
    def_check_adyen_terminal_identifier(self):
        forpayment_methodinself:
            ifnotpayment_method.adyen_terminal_identifier:
                continue
            #sudo()tosearchallcompanies
            existing_payment_method=self.sudo().search([('id','!=',payment_method.id),
                                                   ('adyen_terminal_identifier','=',payment_method.adyen_terminal_identifier)],
                                                  limit=1)
            ifexisting_payment_method:
                ifexisting_payment_method.company_id==payment_method.company_id:
                    raiseValidationError(_('Terminal%sisalreadyusedonpaymentmethod%s.')
                                      %(payment_method.adyen_terminal_identifier,existing_payment_method.display_name))
                else:
                    raiseValidationError(_('Terminal%sisalreadyusedincompany%sonpaymentmethod%s.')
                                          %(payment_method.adyen_terminal_identifier,
                                             existing_payment_method.company_id.name,
                                             existing_payment_method.display_name))

    def_get_adyen_endpoints(self):
        return{
            'terminal_request':'https://terminal-api-%s.adyen.com/async',
        }

    @api.onchange('adyen_terminal_id')
    defonchange_use_payment_terminal(self):
        forpayment_methodinself:
            ifpayment_method.use_payment_terminal=='flectra_adyen'andpayment_method.adyen_terminal_id:
                payment_method.adyen_terminal_identifier=payment_method.adyen_terminal_id.terminal_uuid

    def_is_write_forbidden(self,fields):
        whitelisted_fields=set(('adyen_latest_response','adyen_latest_diagnosis'))
        returnsuper(PosPaymentMethod,self)._is_write_forbidden(fields-whitelisted_fields)

    def_adyen_diagnosis_request_data(self,pos_config_name):
        service_id=''.join(random.choices(string.ascii_letters+string.digits,k=10))
        return{
            "SaleToPOIRequest":{
                "MessageHeader":{
                    "ProtocolVersion":"3.0",
                    "MessageClass":"Service",
                    "MessageCategory":"Diagnosis",
                    "MessageType":"Request",
                    "ServiceID":service_id,
                    "SaleID":pos_config_name,
                    "POIID":self.adyen_terminal_identifier,
                },
                "DiagnosisRequest":{
                    "HostDiagnosisFlag":False
                }
            }
        }

    defget_latest_adyen_status(self,pos_config_name):
        _logger.info('get_latest_adyen_status\n%s',pos_config_name)
        self.ensure_one()

        latest_response=self.sudo().adyen_latest_response
        latest_response=json.loads(latest_response)iflatest_responseelseFalse

        return{
            'latest_response':latest_response,
        }

    defproxy_adyen_request(self,data,operation=False):
        '''NecessarybecauseAdyen'sendpointsdon'thaveCORSenabled'''
        ifdata['SaleToPOIRequest']['MessageHeader']['MessageCategory']=='Payment':#Clearonlyifitisapaymentrequest
            self.sudo().adyen_latest_response='' #avoidhandlingoldresponsesmultipletimes

        ifnotoperation:
            operation='terminal_request'

        ifself.use_payment_terminal=='flectra_adyen':
            returnself._proxy_adyen_request_flectra_proxy(data,operation)
        else:
            returnself._proxy_adyen_request_direct(data,operation)

    def_proxy_adyen_request_direct(self,data,operation):
        self.ensure_one()
        TIMEOUT=10

        _logger.info('requesttoadyen\n%s',pprint.pformat(data))

        environment='test'ifself.adyen_test_modeelse'live'
        endpoint=self._get_adyen_endpoints()[operation]%environment
        headers={
            'x-api-key':self.adyen_api_key,
        }
        req=requests.post(endpoint,json=data,headers=headers,timeout=TIMEOUT)

        #Authenticationerrordoesn'treturnJSON
        ifreq.status_code==401:
            return{
                'error':{
                    'status_code':req.status_code,
                    'message':req.text
                }
            }

        ifreq.text=='ok':
            returnTrue

        returnreq.json()

    def_proxy_adyen_request_flectra_proxy(self,data,operation):
        try:
            returnself.env.company.sudo().adyen_account_id._adyen_rpc(operation,{
                'request_data':data,
                'account_code':self.sudo().adyen_payout_id.code,
                'notification_url':self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            })
        exceptForbidden:
            return{
                'error':{
                    'status_code':401,
                }
            }
