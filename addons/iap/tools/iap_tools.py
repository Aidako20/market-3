#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importcontextlib
importlogging
importjson
importrequests
importuuid
fromunittest.mockimportpatch

fromflectraimportexceptions,_
fromflectra.tests.commonimportBaseCase
fromflectra.toolsimportpycompat

_logger=logging.getLogger(__name__)

DEFAULT_ENDPOINT='https://iap.flectrahq.com'


#Weneedtomockiap_jsonrpcduringtestsaswedon'twanttoperformrealcallstoRPCendpoints
defiap_jsonrpc_mocked(*args,**kwargs):
    raiseexceptions.AccessError("Unavailableduringtests.")


iap_patch=patch('flectra.addons.iap.tools.iap_tools.iap_jsonrpc',iap_jsonrpc_mocked)


defsetUp(self):
    old_setup_func(self)
    iap_patch.start()
    self.addCleanup(iap_patch.stop)


old_setup_func=BaseCase.setUp
BaseCase.setUp=setUp

#----------------------------------------------------------
#Helpersforbothclientsandproxy
#----------------------------------------------------------

defiap_get_endpoint(env):
    url=env['ir.config_parameter'].sudo().get_param('iap.endpoint',DEFAULT_ENDPOINT)
    returnurl

#----------------------------------------------------------
#Helpersforclients
#----------------------------------------------------------

classInsufficientCreditError(Exception):
    pass


defiap_jsonrpc(url,method='call',params=None,timeout=15):
    """
    CallstheprovidedJSON-RPCendpoint,unwrapstheresultand
    returnsJSON-RPCerrorsasexceptions.
    """
    payload={
        'jsonrpc':'2.0',
        'method':method,
        'params':params,
        'id':uuid.uuid4().hex,
    }

    _logger.info('iapjsonrpc%s',url)
    try:
        req=requests.post(url,json=payload,timeout=timeout)
        req.raise_for_status()
        response=req.json()
        if'error'inresponse:
            name=response['error']['data'].get('name').rpartition('.')[-1]
            message=response['error']['data'].get('message')
            ifname=='InsufficientCreditError':
                e_class=InsufficientCreditError
            elifname=='AccessError':
                e_class=exceptions.AccessError
            elifname=='UserError':
                e_class=exceptions.UserError
            else:
                raiserequests.exceptions.ConnectionError()
            e=e_class(message)
            e.data=response['error']['data']
            raisee
        returnresponse.get('result')
    except(ValueError,requests.exceptions.ConnectionError,requests.exceptions.MissingSchema,requests.exceptions.Timeout,requests.exceptions.HTTPError)ase:
        raiseexceptions.AccessError(
            _('Theurlthatthisservicerequestedreturnedanerror.Pleasecontacttheauthoroftheapp.Theurlittriedtocontactwas%s',url)
        )

#----------------------------------------------------------
#Helpersforproxy
#----------------------------------------------------------

classIapTransaction(object):

    def__init__(self):
        self.credit=None


defiap_authorize(env,key,account_token,credit,dbuuid=False,description=None,credit_template=None,ttl=4320):
    endpoint=iap_get_endpoint(env)
    params={
        'account_token':account_token,
        'credit':credit,
        'key':key,
        'description':description,
        'ttl':ttl
    }
    ifdbuuid:
        params.update({'dbuuid':dbuuid})
    try:
        transaction_token=iap_jsonrpc(endpoint+'/iap/1/authorize',params=params)
    exceptInsufficientCreditErrorase:
        ifcredit_template:
            arguments=json.loads(e.args[0])
            arguments['body']=pycompat.to_text(env['ir.qweb']._render(credit_template))
            e.args=(json.dumps(arguments),)
        raisee
    returntransaction_token


defiap_cancel(env,transaction_token,key):
    endpoint=iap_get_endpoint(env)
    params={
        'token':transaction_token,
        'key':key,
    }
    r=iap_jsonrpc(endpoint+'/iap/1/cancel',params=params)
    returnr


defiap_capture(env,transaction_token,key,credit):
    endpoint=iap_get_endpoint(env)
    params={
        'token':transaction_token,
        'key':key,
        'credit_to_capture':credit,
    }
    r=iap_jsonrpc(endpoint+'/iap/1/capture',params=params)
    returnr


@contextlib.contextmanager
defiap_charge(env,key,account_token,credit,dbuuid=False,description=None,credit_template=None):
    """
    Accountchargecontextmanager:takesaholdfor``credit``
    amountbeforeexecutingthebody,thencapturesitifthere
    isnoerror,orcancelsitifthebodygeneratesanexception.

    :paramstrkey:serviceidentifier
    :paramstraccount_token:useridentifier
    :paramintcredit:costofthebody'soperation
    :paramdescription:adescriptionofthepurposeofthecharge,
                        theuserwillbeabletoseeitintheir
                        dashboard
    :typedescription:str
    :paramcredit_template:aQWebtemplatetorenderandshowtothe
                            useriftheiraccountdoesnothaveenough
                            creditsfortherequestedoperation
    :typecredit_template:str
    """
    transaction_token=iap_authorize(env,key,account_token,credit,dbuuid,description,credit_template)
    try:
        transaction=IapTransaction()
        transaction.credit=credit
        yieldtransaction
    exceptExceptionase:
        r=iap_cancel(env,transaction_token,key)
        raisee
    else:
        r=iap_capture(env,transaction_token,key,transaction.credit)
