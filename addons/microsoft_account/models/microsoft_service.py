#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
importjson
importlogging

importrequests
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_

_logger=logging.getLogger(__name__)

TIMEOUT=20

MICROSOFT_AUTH_ENDPOINT='https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
MICROSOFT_TOKEN_ENDPOINT='https://login.microsoftonline.com/common/oauth2/v2.0/token'
MICROSOFT_GRAPH_ENDPOINT='https://graph.microsoft.com'

RESOURCE_NOT_FOUND_STATUSES=(204,404)

classMicrosoftService(models.AbstractModel):
    _name='microsoft.service'
    _description='MicrosoftService'

    def_get_calendar_scope(self):
        return'offline_accessopenidCalendars.ReadWrite'

    @api.model
    defgenerate_refresh_token(self,service,authorization_code):
        """CallMicrosoftAPItorefreshthetoken,withthegivenauthorizationcode
            :paramservice:thenameofthemicrosoftservicetoactualize
            :paramauthorization_code:thecodetoexchangeagainstthenewrefreshtoken
            :returnsthenewrefreshtoken
        """
        Parameters=self.env['ir.config_parameter'].sudo()
        client_id=Parameters.get_param('microsoft_%s_client_id'%service)
        client_secret=Parameters.get_param('microsoft_%s_client_secret'%service)
        redirect_uri=Parameters.get_param('microsoft_redirect_uri')

        scope=self._get_calendar_scope()

        #GettheRefreshTokenFromMicrosoftAndstoreitinir.config_parameter
        headers={"Content-type":"application/x-www-form-urlencoded"}
        data={
            'client_id':client_id,
            'redirect_uri':redirect_uri,
            'client_secret':client_secret,
            'scope':scope,
            'grant_type':"refresh_token"
        }
        try:
            req=requests.post(MICROSOFT_TOKEN_ENDPOINT,data=data,headers=headers,timeout=TIMEOUT)
            req.raise_for_status()
            content=req.json()
        exceptIOError:
            error_msg=_("Somethingwentwrongduringyourtokengeneration.MaybeyourAuthorizationCodeisinvalidoralreadyexpired")
            raiseself.env['res.config.settings'].get_config_warning(error_msg)

        returncontent.get('refresh_token')

    @api.model
    def_get_authorize_uri(self,from_url,service,scope):
        """ThismethodreturntheurlneededtoallowthisinstanceofFlectratoaccesstothescope
            ofgmailspecifiedasparameters
        """
        state={
            'd':self.env.cr.dbname,
            's':service,
            'f':from_url
        }

        get_param=self.env['ir.config_parameter'].sudo().get_param
        base_url=get_param('web.base.url',default='http://www.flectrahq.com?NoBaseUrl')
        client_id=get_param('microsoft_%s_client_id'%(service,),default=False)

        encoded_params=urls.url_encode({
            'response_type':'code',
            'client_id':client_id,
            'state':json.dumps(state),
            'scope':scope,
            'redirect_uri':base_url+'/microsoft_account/authentication',
            'access_type':'offline'
        })
        return"%s?%s"%(MICROSOFT_AUTH_ENDPOINT,encoded_params)

    @api.model
    def_get_microsoft_tokens(self,authorize_code,service):
        """CallMicrosoftAPItoexchangeauthorizationcodeagainsttoken,withPOSTrequest,to
            notberedirected.
        """
        get_param=self.env['ir.config_parameter'].sudo().get_param
        base_url=get_param('web.base.url',default='http://www.flectrahq.com?NoBaseUrl')
        client_id=get_param('microsoft_%s_client_id'%(service,),default=False)
        client_secret=get_param('microsoft_%s_client_secret'%(service,),default=False)
        scope=self._get_calendar_scope()

        headers={"content-type":"application/x-www-form-urlencoded"}
        data={
            'code':authorize_code,
            'client_id':client_id,
            'client_secret':client_secret,
            'grant_type':'authorization_code',
            'scope':scope,
            'redirect_uri':base_url+'/microsoft_account/authentication'
        }
        try:
            dummy,response,dummy=self._do_request(MICROSOFT_TOKEN_ENDPOINT,params=data,headers=headers,method='POST',preuri='')
            access_token=response.get('access_token')
            refresh_token=response.get('refresh_token')
            ttl=response.get('expires_in')
            returnaccess_token,refresh_token,ttl
        exceptrequests.HTTPError:
            error_msg=_("Somethingwentwrongduringyourtokengeneration.MaybeyourAuthorizationCodeisinvalid")
            raiseself.env['res.config.settings'].get_config_warning(error_msg)

    @api.model
    def_do_request(self,uri,params=None,headers=None,method='POST',preuri=MICROSOFT_GRAPH_ENDPOINT,timeout=TIMEOUT):
        """ExecutetherequesttoMicrosoftAPI.Returnatuple('HTTP_CODE','HTTP_RESPONSE')
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
            urls.url_parse(url).hostforurlin(MICROSOFT_TOKEN_ENDPOINT,MICROSOFT_GRAPH_ENDPOINT)
        ]

        _logger.debug("Uri:%s-Type:%s-Headers:%s-Params:%s!"%(uri,method,headers,params))

        ask_time=fields.Datetime.now()
        try:
            ifmethod.upper()in('GET','DELETE'):
                res=requests.request(method.lower(),preuri+uri,headers=headers,params=params,timeout=timeout)
            elifmethod.upper()in('POST','PATCH','PUT'):
                res=requests.request(method.lower(),preuri+uri,data=params,headers=headers,timeout=timeout)
            else:
                raiseException(_('Methodnotsupported[%s]notin[GET,POST,PUT,PATCHorDELETE]!',method))
            res.raise_for_status()
            status=res.status_code

            ifint(status)inRESOURCE_NOT_FOUND_STATUSES:
                response={}
            else:
                #Someanswersreturnemptycontent
                response=res.contentandres.json()or{}

            try:
                ask_time=datetime.strptime(res.headers.get('date'),"%a,%d%b%Y%H:%M:%S%Z")
            except:
                pass
        exceptrequests.HTTPErroraserror:
            iferror.response.status_codeinRESOURCE_NOT_FOUND_STATUSES:
                status=error.response.status_code
                response={}
            else:
                _logger.exception("Badmicrosoftrequest:%s!",error.response.content)
                raiseerror
        return(status,response,ask_time)
