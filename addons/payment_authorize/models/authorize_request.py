#-*-coding:utf-8-*-
importjson
importlogging
importrequests

fromuuidimportuuid4

fromflectraimport_
fromflectra.exceptionsimportUserError

fromflectra.addons.payment.models.payment_acquirerimport_partner_split_name

_logger=logging.getLogger(__name__)


classAuthorizeAPI():
    """Authorize.netGatewayAPIintegration.

    ThisclassallowscontactingtheAuthorize.netAPIwithsimpleoperation
    requests.Itimplementsa*verylimited*subsetofthecompleteAPI
    (http://developer.authorize.net/api/reference);namely:
        -CustomerProfile/PaymentProfilecreation
        -Transactionauthorization/capture/voiding
    """

    AUTH_ERROR_STATUS=3

    def__init__(self,acquirer):
        """Initiatetheenvironmentwiththeacquirerdata.

        :paramrecordacquirer:payment.acquireraccountthatwillbecontacted
        """
        ifacquirer.state=='enabled':
            self.url='https://api.authorize.net/xml/v1/request.api'
        else:
            self.url='https://apitest.authorize.net/xml/v1/request.api'

        self.state=acquirer.state
        self.name=acquirer.authorize_login
        self.transaction_key=acquirer.authorize_transaction_key

    def_authorize_request(self,data):
        _logger.info('_authorize_request:SendingvaluestoURL%s,values:\n%s',self.url,data)
        resp=requests.post(self.url,json.dumps(data))
        resp.raise_for_status()
        resp=json.loads(resp.content)
        _logger.info("_authorize_request:Receivedresponse:\n%s",resp)
        messages=resp.get('messages')
        ifmessagesandmessages.get('resultCode')=='Error':
            return{
                'err_code':messages.get('message')[0].get('code'),
                'err_msg':messages.get('message')[0].get('text')
            }

        returnresp

    #Customerprofiles
    defcreate_customer_profile(self,partner,opaqueData):
        """CreateapaymentandcustomerprofileintheAuthorize.netbackend.

        Createsacustomerprofileforthepartner/creditcardcombinationandlinks
        acorrespondingpaymentprofiletoit.NotethatasinglepartnerintheFlectra
        databasecanhavemultiplecustomerprofilesinAuthorize.net(i.e.acustomer
        profileiscreatedforeveryres.partner/payment.tokencouple).

        :paramrecordpartner:theres.partnerrecordofthecustomer
        :paramstrcardnumber:cardnumberinstringformat(numbersonly,noseparator)
        :paramstrexpiration_date:expirationdatein'YYYY-MM'stringformat
        :paramstrcard_code:three-orfour-digitverificationnumber

        :return:adictcontainingtheprofile_idandpayment_profile_idofthe
                 newlycreatedcustomerprofileandpaymentprofile
        :rtype:dict
        """
        values={
            'createCustomerProfileRequest':{
                'merchantAuthentication':{
                    'name':self.name,
                    'transactionKey':self.transaction_key
                },
                'profile':{
                    'description':('FLECTRA-%s-%s'%(partner.id,uuid4().hex[:8]))[:20],
                    'email':partner.emailor'',
                    'paymentProfiles':{
                        'customerType':'business'ifpartner.is_companyelse'individual',
                        'billTo':{
                            'firstName':''ifpartner.is_companyelse_partner_split_name(partner.name)[0][:50],
                            'lastName': partner.name[:50]ifpartner.is_companyelse_partner_split_name(partner.name)[1][:50],
                            'address':(partner.streetor''+(partner.street2ifpartner.street2else''))orNone,
                            'city':partner.city,
                            'state':partner.state_id.nameorNone,
                            'zip':partner.zipor'',
                            'country':partner.country_id.nameorNone,
                            'phoneNumber':partner.phoneor'',
                        },
                        'payment':{
                            'opaqueData':{
                                'dataDescriptor':opaqueData.get('dataDescriptor'),
                                'dataValue':opaqueData.get('dataValue')
                            }
                        }
                    }
                },
                'validationMode':'liveMode'ifself.state=='enabled'else'testMode'
            }
        }

        response=self._authorize_request(values)

        ifresponseandresponse.get('err_code'):
            raiseUserError(_(
                "Authorize.netError:\nCode:%s\nMessage:%s",
                response.get('err_code'),response.get('err_msg'),
            ))

        return{
            'profile_id':response.get('customerProfileId'),
            'payment_profile_id':response.get('customerPaymentProfileIdList')[0]
        }

    defcreate_customer_profile_from_tx(self,partner,transaction_id):
        """CreateanAuth.netpayment/customerprofilefromanexistingtransaction.

        Createsacustomerprofileforthepartner/creditcardcombinationandlinks
        acorrespondingpaymentprofiletoit.NotethatasinglepartnerintheFlectra
        databasecanhavemultiplecustomerprofilesinAuthorize.net(i.e.acustomer
        profileiscreatedforeveryres.partner/payment.tokencouple).

        Notethatthisfunctionmakes2callstotheauthorizeapi,sinceweneedto
        obtainapartialcardnumbertogenerateameaningfulpayment.tokenname.

        :paramrecordpartner:theres.partnerrecordofthecustomer
        :paramstrtransaction_id:idoftheauthorizedtransactioninthe
                                   Authorize.netbackend

        :return:adictcontainingtheprofile_idandpayment_profile_idofthe
                 newlycreatedcustomerprofileandpaymentprofileaswellasthe
                 lastdigitsofthecardnumber
        :rtype:dict
        """
        values={
            'createCustomerProfileFromTransactionRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
                'transId':transaction_id,
                'customer':{
                    'merchantCustomerId':('FLECTRA-%s-%s'%(partner.id,uuid4().hex[:8]))[:20],
                    'email':partner.emailor''
                }
            }
        }

        response=self._authorize_request(values)

        ifnotresponse.get('customerProfileId'):
            _logger.warning(
                'Unabletocreatecustomerpaymentprofile,datamissingfromtransaction.Transaction_id:%s-Partner_id:%s'
                %(transaction_id,partner)
            )
            returnFalse

        res={
            'profile_id':response.get('customerProfileId'),
            'payment_profile_id':response.get('customerPaymentProfileIdList')[0]
        }

        values={
            'getCustomerPaymentProfileRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
                'customerProfileId':res['profile_id'],
                'customerPaymentProfileId':res['payment_profile_id'],
            }
        }

        response=self._authorize_request(values)

        res['name']=response.get('paymentProfile',{}).get('payment',{}).get('creditCard',{}).get('cardNumber')
        returnres

    #Transactionmanagement
    defauth_and_capture(self,token,amount,reference):
        """Authorizeandcaptureapaymentforthegivenamount.

        Authorizeandimmediatelycaptureapaymentforthegivenpayment.token
        recordforthespecifiedamountwithreferenceascommunication.

        :paramrecordtoken:thepayment.tokenrecordthatmustbecharged
        :paramstramount:transactionamount(upto15digitswithdecimalpoint)
        :paramstrreference:usedas"invoiceNumber"intheAuthorize.netbackend

        :return:adictcontainingtheresponsecode,transactionidandtransactiontype
        :rtype:dict
        """
        values={
            'createTransactionRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
                'transactionRequest':{
                    'transactionType':'authCaptureTransaction',
                    'amount':str(amount),
                    'profile':{
                        'customerProfileId':token.authorize_profile,
                        'paymentProfile':{
                            'paymentProfileId':token.acquirer_ref,
                        }
                    },
                    'order':{
                        'invoiceNumber':reference[:20],
                        'description':reference[:255],
                    }
                }

            }
        }
        response=self._authorize_request(values)

        ifresponseandresponse.get('err_code'):
            return{
                'x_response_code':self.AUTH_ERROR_STATUS,
                'x_response_reason_text':response.get('err_msg')
            }

        result={
            'x_response_code':response.get('transactionResponse',{}).get('responseCode'),
            'x_trans_id':response.get('transactionResponse',{}).get('transId'),
            'x_type':'auth_capture'
        }
        errors=response.get('transactionResponse',{}).get('errors')
        iferrors:
            result['x_response_reason_text']='\n'.join([e.get('errorText')foreinerrors])
        returnresult

    defauthorize(self,token,amount,reference):
        """Authorizeapaymentforthegivenamount.

        Authorize(withoutcapture)apaymentforthegivenpayment.token
        recordforthespecifiedamountwithreferenceascommunication.

        :paramrecordtoken:thepayment.tokenrecordthatmustbecharged
        :paramstramount:transactionamount(upto15digitswithdecimalpoint)
        :paramstrreference:usedas"invoiceNumber"intheAuthorize.netbackend

        :return:adictcontainingtheresponsecode,transactionidandtransactiontype
        :rtype:dict
        """
        values={
            'createTransactionRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
                'transactionRequest':{
                    'transactionType':'authOnlyTransaction',
                    'amount':str(amount),
                    'profile':{
                        'customerProfileId':token.authorize_profile,
                        'paymentProfile':{
                            'paymentProfileId':token.acquirer_ref,
                        }
                    },
                    'order':{
                        'invoiceNumber':reference[:20],
                        'description':reference[:255],
                    }
                }

            }
        }
        response=self._authorize_request(values)

        ifresponseandresponse.get('err_code'):
            return{
                'x_response_code':self.AUTH_ERROR_STATUS,
                'x_response_reason_text':response.get('err_msg')
            }

        return{
            'x_response_code':response.get('transactionResponse',{}).get('responseCode'),
            'x_trans_id':response.get('transactionResponse',{}).get('transId'),
            'x_type':'auth_only'
        }

    defcapture(self,transaction_id,amount):
        """Captureapreviouslyauthorizedpaymentforthegivenamount.

        Captureaprevisoulyauthorizedpayment.Notethattheamountisrequired
        eventhoughwedonotsupportpartialcapture.

        :paramstrtransaction_id:idoftheauthorizedtransactioninthe
                                   Authorize.netbackend
        :paramstramount:transactionamount(upto15digitswithdecimalpoint)

        :return:adictcontainingtheresponsecode,transactionidandtransactiontype
        :rtype:dict
        """
        values={
            'createTransactionRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
                'transactionRequest':{
                    'transactionType':'priorAuthCaptureTransaction',
                    'amount':str(amount),
                    'refTransId':transaction_id,
                }
            }
        }

        response=self._authorize_request(values)

        ifresponseandresponse.get('err_code'):
            return{
                'x_response_code':self.AUTH_ERROR_STATUS,
                'x_response_reason_text':response.get('err_msg')
            }

        return{
            'x_response_code':response.get('transactionResponse',{}).get('responseCode'),
            'x_trans_id':response.get('transactionResponse',{}).get('transId'),
            'x_type':'prior_auth_capture'
        }

    defvoid(self,transaction_id):
        """Voidapreviouslyauthorizedpayment.

        :paramstrtransaction_id:theidoftheauthorizedtransactioninthe
                                   Authorize.netbackend

        :return:adictcontainingtheresponsecode,transactionidandtransactiontype
        :rtype:dict
        """
        values={
            'createTransactionRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
                'transactionRequest':{
                    'transactionType':'voidTransaction',
                    'refTransId':transaction_id
                }
            }
        }

        response=self._authorize_request(values)

        ifresponseandresponse.get('err_code'):
            return{
                'x_response_code':self.AUTH_ERROR_STATUS,
                'x_response_reason_text':response.get('err_msg')
            }

        return{
            'x_response_code':response.get('transactionResponse',{}).get('responseCode'),
            'x_trans_id':response.get('transactionResponse',{}).get('transId'),
            'x_type':'void'
        }

    #Test
    deftest_authenticate(self):
        """TestAuthorize.netcommunicationwithasimplecredentialscheck.

        :return:Trueifauthenticationwassuccessful,elseFalse(orthrowsanerror)
        :rtype:bool
        """
        values={
            'authenticateTestRequest':{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key
                },
            }
        }

        response=self._authorize_request(values)
        ifresponseandresponse.get('err_code'):
            returnFalse
        returnTrue

    #ClientKey
    defget_client_secret(self):
        """CreateaclientsecretthatwillbeneededfortheAcceptJSintegration."""
        values={
            "getMerchantDetailsRequest":{
                "merchantAuthentication":{
                    "name":self.name,
                    "transactionKey":self.transaction_key,
                }
            }
        }
        response=self._authorize_request(values)
        client_secret=response.get('publicClientKey')
        returnclient_secret
