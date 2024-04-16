fromflectraimportmodels,fields,_
fromflectra.exceptionsimportUserError
from.account_edi_proxy_authimportFlectraEdiProxyAuth

fromcryptography.hazmat.backendsimportdefault_backend
fromcryptography.hazmat.primitives.asymmetricimportrsa
fromcryptography.hazmat.primitivesimportserialization
fromcryptography.hazmat.primitivesimporthashes
fromcryptography.hazmat.primitives.asymmetricimportpadding
fromcryptography.fernetimportFernet
frompsycopg2importOperationalError
importrequests
importuuid
importbase64
importlogging


_logger=logging.getLogger(__name__)


DEFAULT_SERVER_URL='https://l10n-it-edi.api.flectrahq.com'
DEFAULT_TEST_SERVER_URL='https://iap-services-test.flectrahq.com'
TIMEOUT=30


classAccountEdiProxyError(Exception):

    def__init__(self,code,message=False):
        self.code=code
        self.message=message
        super().__init__(messageorcode)


classAccountEdiProxyClientUser(models.Model):
    """Representsauseroftheproxyforanelectronicinvoicingformat.
    Anedi_proxy_userhasauniqueidentificationonaspecificformat(forexample,thevatforPeppol)which
    allowstoidentifyhimwhenreceivingadocumentaddressedtohim.Itislinkedtoaspecificcompanyonaspecific
    Flectradatabase.
    Italsoownsakeywithwhicheachfileshouldbedecryptedwith(theproxyencryptallthefileswiththepublickey).
    """
    _name='account_edi_proxy_client.user'
    _description='AccountEDIproxyuser'

    active=fields.Boolean(default=True)
    id_client=fields.Char(required=True,index=True)
    company_id=fields.Many2one('res.company',string='Company',required=True,
        default=lambdaself:self.env.company)
    edi_format_id=fields.Many2one('account.edi.format',required=True)
    edi_format_code=fields.Char(related='edi_format_id.code',readonly=True)
    edi_identification=fields.Char(required=True,help="Theuniqueidthatidentifiesthisuserforontheediformat,typicallythevat")
    private_key=fields.Binary(required=True,attachment=False,groups="base.group_system",help="Thekeytoencryptalltheuser'sdata")
    refresh_token=fields.Char(groups="base.group_system")

    _sql_constraints=[
        ('unique_id_client','unique(id_client)','Thisid_clientisalreadyusedonanotheruser.'),
        ('unique_edi_identification_per_format','unique(edi_identification,edi_format_id)','Thisediidentificationisalreadyassignedtoauser'),
    ]

    def_get_demo_state(self):
        demo_state=self.env['ir.config_parameter'].sudo().get_param('account_edi_proxy_client.demo',False)
        return'prod'ifdemo_statein['prod',False]else'test'ifdemo_state=='test'else'demo'

    def_get_server_url(self):
        returnDEFAULT_TEST_SERVER_URLifself._get_demo_state()=='test'elseself.env['ir.config_parameter'].sudo().get_param('account_edi_proxy_client.edi_server_url',DEFAULT_SERVER_URL)

    def_make_request(self,url,params=False):
        '''Makearequesttoproxyandhandlethegenericelementsofthereponse(errors,newrefreshtoken).
        '''
        payload={
            'jsonrpc':'2.0',
            'method':'call',
            'params':paramsor{},
            'id':uuid.uuid4().hex,
        }

        ifself._get_demo_state()=='demo':
            #Lastbarrier:incasethedemomodeisnothandledbythecaller,weblockaccess.
            raiseException("Can'taccesstheproxyindemomode")

        try:
            response=requests.post(
                url,
                json=payload,
                timeout=TIMEOUT,
                headers={'content-type':'application/json'},
                auth=FlectraEdiProxyAuth(user=self)).json()
        except(ValueError,requests.exceptions.ConnectionError,requests.exceptions.MissingSchema,requests.exceptions.Timeout,requests.exceptions.HTTPError):
            raiseAccountEdiProxyError('connection_error',
                _('Theurlthatthisservicerequestedreturnedanerror.Theurlittriedtocontactwas%s',url))

        if'error'inresponse:
            message=_('Theurlthatthisservicerequestedreturnedanerror.Theurlittriedtocontactwas%s.%s',url,response['error']['message'])
            ifresponse['error']['code']==404:
                message=_('Theurlthatthisservicedoesnotexist.Theurlittriedtocontactwas%s',url)
            raiseAccountEdiProxyError('connection_error',message)

        proxy_error=response['result'].pop('proxy_error',False)
        ifproxy_error:
            error_code=proxy_error['code']
            iferror_code=='refresh_token_expired':
                self._renew_token()
                ifnotself.env.context.get('test_skip_commit'):
                    self.env.cr.commit()#Wedonotwanttoloseitifinthe_make_requestbelowsomethinggoeswrong
                returnself._make_request(url,params)
            iferror_code=='no_such_user':
                #Thiserrorisalsoraisediftheuserdidn'texchangedataandsomeoneelseclaimedtheedi_identificaiton.
                self.sudo().active=False
            raiseAccountEdiProxyError(error_code,proxy_error['message']orFalse)

        returnresponse['result']

    def_register_proxy_user(self,company,edi_format,edi_identification):
        '''Generatethepublic_key/private_keythatwillbeusedtoencryptthefile,sendarequesttotheproxy
        toregistertheuserwiththepublickeyandcreatetheuserwiththeprivatekey.

        :paramcompany:thecompanyoftheuser.
        :paramedi_identification:TheuniqueIDthatidentifiesthisuseronthisedinetworkandtowhichthefileswillbeaddressed.
                                   Typicallythevat.
        '''
        #public_exponent=65537isadefaultvaluethatshouldbeusedmostofthetime,asperthedocumentationofcryptography.
        #key_size=2048isconsideredareasonabledefaultkeysize,asperthedocumentationofcryptography.
        #seehttps://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
        private_key=rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        private_pem=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key=private_key.public_key()
        public_pem=public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        ifself._get_demo_state()=='demo':
            #simulateregistration
            response={'id_client':f'demo{company.id}','refresh_token':'demo'}
        else:
            try:
                #b64encodereturnsabytestring,weneeditasastring
                response=self._make_request(self._get_server_url()+'/iap/account_edi/1/create_user',params={
                    'dbuuid':company.env['ir.config_parameter'].get_param('database.uuid'),
                    'company_id':company.id,
                    'edi_format_code':edi_format.code,
                    'edi_identification':edi_identification,
                    'public_key':base64.b64encode(public_pem).decode()
                })
            exceptAccountEdiProxyErrorase:
                raiseUserError(e.message)
            if'error'inresponse:
                raiseUserError(response['error'])

        self.create({
            'id_client':response['id_client'],
            'company_id':company.id,
            'edi_format_id':edi_format.id,
            'edi_identification':edi_identification,
            'private_key':base64.b64encode(private_pem),
            'refresh_token':response['refresh_token'],
        })

    def_renew_token(self):
        '''Requesttheproxyforanewrefreshtoken.

        Requesttotheproxyshouldbemadewitharefreshtokenthatexpireafter24htoavoid
        thatmultipledatabaseusethesamecredentials.Whenreceivinganerrorforanexpiredrefresh_token,
        Thismethodmakesarequesttogetanewrefreshtoken.
        '''
        try:
            withself.env.cr.savepoint(flush=False):
                self.env.cr.execute('SELECT*FROMaccount_edi_proxy_client_userWHEREidIN%sFORUPDATENOWAIT',[tuple(self.ids)])
        exceptOperationalErrorase:
            ife.pgcode=='55P03':
                return
            raisee
        response=self._make_request(self._get_server_url()+'/iap/account_edi/1/renew_token')
        if'error'inresponse:
            #canhappenifthedatabasewasduplicatedandtherefresh_tokenwasrefreshedbytheotherdatabase.
            #wedon'twanttwodatabasetobeabletoquerytheproxywiththesameuser
            #becauseitcouldleadtonotinconsistentdata.
            _logger.error(response['error'])
        self.sudo().refresh_token=response['refresh_token']

    def_decrypt_data(self,data,symmetric_key):
        '''Decryptthedata.Notethatthedataisencryptedwithasymmetrickey,whichisencryptedwithanasymmetrickey.
        Wemustthereforedecryptthesymmetrickey.

        :paramdata:           Thedatatodecrypt.
        :paramsymmetric_key:  Thesymmetric_keyencryptedwithself.private_key.public_key()
        '''
        private_key=serialization.load_pem_private_key(
            base64.b64decode(self.sudo().private_key),
            password=None,
            backend=default_backend()
        )
        key=private_key.decrypt(
            base64.b64decode(symmetric_key),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        f=Fernet(key)
        returnf.decrypt(base64.b64decode(data))
