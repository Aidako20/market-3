#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
importjson
importlogging

importrequests
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)

TIMEOUT=20

GOOGLE_AUTH_ENDPOINT='https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_ENDPOINT='https://accounts.google.com/o/oauth2/token'
GOOGLE_API_BASE_URL='https://www.googleapis.com'


classGoogleService(models.AbstractModel):
    _name='google.service'
    _description='GoogleService'

    @api.model
    defgenerate_refresh_token(self,service,authorization_code):
        """CallGoogleAPItorefreshthetoken,withthegivenauthorizationcode
            :paramservice:thenameofthegoogleservicetoactualize
            :paramauthorization_code:thecodetoexchangeagainstthenewrefreshtoken
            :returnsthenewrefreshtoken
        """
        Parameters=self.env['ir.config_parameter'].sudo()
        client_id=Parameters.get_param('google_%s_client_id'%service)
        client_secret=Parameters.get_param('google_%s_client_secret'%service)
        redirect_uri=Parameters.get_param('google_redirect_uri')

        #GettheRefreshTokenFromGoogleAndstoreitinir.config_parameter
        headers={"Content-type":"application/x-www-form-urlencoded"}
        data={
            'code':authorization_code,
            'client_id':client_id,
            'client_secret':client_secret,
            'redirect_uri':redirect_uri,
            'grant_type':"authorization_code"
        }
        try:
            req=requests.post(GOOGLE_TOKEN_ENDPOINT,data=data,headers=headers,timeout=TIMEOUT)
            req.raise_for_status()
            content=req.json()
        exceptIOError:
            error_msg=_("Somethingwentwrongduringyourtokengeneration.MaybeyourAuthorizationCodeisinvalidoralreadyexpired")
            raiseself.env['res.config.settings'].get_config_warning(error_msg)

        returncontent.get('refresh_token')

    @api.model
    def_get_google_token_uri(self,service,scope):
        get_param=self.env['ir.config_parameter'].sudo().get_param
        encoded_params=urls.url_encode({
            'scope':scope,
            'redirect_uri':get_param('google_redirect_uri'),
            'client_id':get_param('google_%s_client_id'%service),
            'response_type':'code',
        })
        return'%s?%s'%(GOOGLE_AUTH_ENDPOINT,encoded_params)

    @api.model
    def_get_authorize_uri(self,from_url,service,scope=False):
        """ThismethodreturntheurlneededtoallowthisinstanceofFlectratoaccesstothescope
            ofgmailspecifiedasparameters
        """
        state={
            'd':self.env.cr.dbname,
            's':service,
            'f':from_url
        }

        get_param=self.env['ir.config_parameter'].sudo().get_param
        base_url=self._context.get('base_url')orself.env.user.get_base_url()
        client_id=get_param('google_%s_client_id'%(service,),default=False)

        encoded_params=urls.url_encode({
            'response_type':'code',
            'client_id':client_id,
            'state':json.dumps(state),
            'scope':scopeor'%s/auth/%s'%(GOOGLE_API_BASE_URL,service), #Ifnoscopeispassed,weuseservicebydefaulttogetadefaultscope
            'redirect_uri':base_url+'/google_account/authentication',
            'approval_prompt':'force',
            'access_type':'offline'
        })
        return"%s?%s"%(GOOGLE_AUTH_ENDPOINT,encoded_params)

    @api.model
    def_get_google_tokens(self,authorize_code,service):
        """CallGoogleAPItoexchangeauthorizationcodeagainsttoken,withPOSTrequest,to
            notberedirected.
        """
        get_param=self.env['ir.config_parameter'].sudo().get_param
        base_url=self._context.get('base_url')orself.env.user.get_base_url()
        client_id=get_param('google_%s_client_id'%(service,),default=False)
        client_secret=get_param('google_%s_client_secret'%(service,),default=False)

        headers={"content-type":"application/x-www-form-urlencoded"}
        data={
            'code':authorize_code,
            'client_id':client_id,
            'client_secret':client_secret,
            'grant_type':'authorization_code',
            'redirect_uri':base_url+'/google_account/authentication'
        }
        try:
            dummy,response,dummy=self._do_request(GOOGLE_TOKEN_ENDPOINT,params=data,headers=headers,method='POST',preuri='')
            access_token=response.get('access_token')
            refresh_token=response.get('refresh_token')
            ttl=response.get('expires_in')
            returnaccess_token,refresh_token,ttl
        exceptrequests.HTTPError:
            error_msg=_("Somethingwentwrongduringyourtokengeneration.MaybeyourAuthorizationCodeisinvalid")
            raiseself.env['res.config.settings'].get_config_warning(error_msg)

    @api.model
    def_get_access_token(self,refresh_token,service,scope):
        """Fetchtheaccesstokenthankstotherefreshtoken."""
        get_param=self.env['ir.config_parameter'].sudo().get_param
        client_id=get_param('google_%s_client_id'%service,default=False)
        client_secret=get_param('google_%s_client_secret'%service,default=False)

        ifnotclient_idornotclient_secret:
            raiseUserError(_('Google%sisnotyetconfigured.',service.title()))

        ifnotrefresh_token:
            raiseUserError(_('Therefreshtokenforauthenticationisnotset.'))

        try:
            result=requests.post(
                GOOGLE_TOKEN_ENDPOINT,
                data={
                    'client_id':client_id,
                    'client_secret':client_secret,
                    'refresh_token':refresh_token,
                    'grant_type':'refresh_token',
                    'scope':scope,
                },
                headers={'Content-type':'application/x-www-form-urlencoded'},
                timeout=TIMEOUT,
            )
            result.raise_for_status()
        exceptrequests.HTTPError:
            raiseUserError(
                _('Somethingwentwrongduringthetokengeneration.Pleaserequestagainanauthorizationcode.')
            )

        json_result=result.json()

        returnjson_result.get('access_token'),json_result.get('expires_in')

    @api.model
    def_do_request(self,uri,params=None,headers=None,method='POST',preuri=GOOGLE_API_BASE_URL,timeout=TIMEOUT):
        """ExecutetherequesttoGoogleAPI.Returnatuple('HTTP_CODE','HTTP_RESPONSE')
            :paramuri:theurltocontact
            :paramparams:dictoralreadyencodedparametersfortherequesttomake
            :paramheaders:headersofrequest
            :parammethod:themethodtousetomaketherequest
            :parampreuri:preurltoprependtoparamuri.
        """
        ifparamsisNone:
            params={}
        ifheadersisNone:
            headers={}

        asserturls.url_parse(preuri+uri).hostin[
            urls.url_parse(url).hostforurlin(GOOGLE_TOKEN_ENDPOINT,GOOGLE_API_BASE_URL)
        ]

        _logger.debug("Uri:%s-Type:%s-Headers:%s-Params:%s!",(uri,method,headers,params))

        ask_time=fields.Datetime.now()
        try:
            ifmethod.upper()in('GET','DELETE'):
                res=requests.request(method.lower(),preuri+uri,params=params,timeout=timeout)
            elifmethod.upper()in('POST','PATCH','PUT'):
                res=requests.request(method.lower(),preuri+uri,data=params,headers=headers,timeout=timeout)
            else:
                raiseException(_('Methodnotsupported[%s]notin[GET,POST,PUT,PATCHorDELETE]!')%(method))
            res.raise_for_status()
            status=res.status_code

            ifint(status)in(204,404): #Pagenotfound,noresponse
                response=False
            else:
                response=res.json()

            try:
                ask_time=datetime.strptime(res.headers.get('date'),"%a,%d%b%Y%H:%M:%S%Z")
            except:
                pass
        exceptrequests.HTTPErroraserror:
            iferror.response.status_codein(204,404):
                status=error.response.status_code
                response=""
            else:
                _logger.exception("Badgooglerequest:%s!",error.response.content)
                raiseerror
        return(status,response,ask_time)
