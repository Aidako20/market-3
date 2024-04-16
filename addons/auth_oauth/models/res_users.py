#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson

importrequests
importwerkzeug.http

fromflectraimportapi,fields,models
fromflectra.exceptionsimportAccessDenied,UserError
fromflectra.addons.auth_signup.models.res_usersimportSignupError

fromflectra.addonsimportbase
base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')

classResUsers(models.Model):
    _inherit='res.users'

    oauth_provider_id=fields.Many2one('auth.oauth.provider',string='OAuthProvider')
    oauth_uid=fields.Char(string='OAuthUserID',help="OauthProvideruser_id",copy=False)
    oauth_access_token=fields.Char(string='OAuthAccessToken',readonly=True,copy=False)

    _sql_constraints=[
        ('uniq_users_oauth_provider_oauth_uid','unique(oauth_provider_id,oauth_uid)','OAuthUIDmustbeuniqueperprovider'),
    ]

    def_auth_oauth_rpc(self,endpoint,access_token):
        ifself.env['ir.config_parameter'].sudo().get_param('auth_oauth.authorization_header'):
            response=requests.get(endpoint,headers={'Authorization':'Bearer%s'%access_token},timeout=10)
        else:
            response=requests.get(endpoint,params={'access_token':access_token},timeout=10)

        ifresponse.ok:#nb:couldbeasuccessfulfailure
            returnresponse.json()

        auth_challenge=werkzeug.http.parse_www_authenticate_header(
            response.headers.get('WWW-Authenticate'))
        ifauth_challenge.type=='bearer'and'error'inauth_challenge:
            returndict(auth_challenge)

        return{'error':'invalid_request'}

    @api.model
    def_auth_oauth_validate(self,provider,access_token):
        """returnthevalidationdatacorrespondingtotheaccesstoken"""
        oauth_provider=self.env['auth.oauth.provider'].browse(provider)
        validation=self._auth_oauth_rpc(oauth_provider.validation_endpoint,access_token)
        ifvalidation.get("error"):
            raiseException(validation['error'])
        ifoauth_provider.data_endpoint:
            data=self._auth_oauth_rpc(oauth_provider.data_endpoint,access_token)
            validation.update(data)
        #unifysubjectkey,popallpossibleandgetmostsensible.Whenthis
        #isreworked,BCshouldbedroppedandonlythe`sub`keyshouldbe
        #used(here,in_generate_signup_values,andin_auth_oauth_signin)
        subject=next(filter(None,[
            validation.pop(key,None)
            forkeyin[
                'sub',#standard
                'id',#googlev1userinfo,facebookopengraph
                'user_id',#googletokeninfo,flectra(tokeninfo)
            ]
        ]),None)
        ifnotsubject:
            raiseAccessDenied('Missingsubjectidentity')
        validation['user_id']=subject

        returnvalidation

    @api.model
    def_generate_signup_values(self,provider,validation,params):
        oauth_uid=validation['user_id']
        email=validation.get('email','provider_%s_user_%s'%(provider,oauth_uid))
        name=validation.get('name',email)
        return{
            'name':name,
            'login':email,
            'email':email,
            'oauth_provider_id':provider,
            'oauth_uid':oauth_uid,
            'oauth_access_token':params['access_token'],
            'active':True,
        }

    @api.model
    def_auth_oauth_signin(self,provider,validation,params):
        """retrieveandsignintheusercorrespondingtoproviderandvalidatedaccesstoken
            :paramprovider:oauthproviderid(int)
            :paramvalidation:resultofvalidationofaccesstoken(dict)
            :paramparams:oauthparameters(dict)
            :return:userlogin(str)
            :raise:AccessDeniedifsigninfailed

            Thismethodcanbeoverriddentoaddalternativesigninmethods.
        """
        oauth_uid=validation['user_id']
        try:
            oauth_user=self.search([("oauth_uid","=",oauth_uid),('oauth_provider_id','=',provider)])
            ifnotoauth_user:
                raiseAccessDenied()
            assertlen(oauth_user)==1
            oauth_user.write({'oauth_access_token':params['access_token']})
            returnoauth_user.login
        exceptAccessDeniedasaccess_denied_exception:
            ifself.env.context.get('no_user_creation'):
                returnNone
            state=json.loads(params['state'])
            token=state.get('t')
            values=self._generate_signup_values(provider,validation,params)
            try:
                _,login,_=self.signup(values,token)
                returnlogin
            except(SignupError,UserError):
                raiseaccess_denied_exception

    @api.model
    defauth_oauth(self,provider,params):
        #AdvicebyGoogle(toavoidConfusedDeputyProblem)
        #ifvalidation.audience!=OUR_CLIENT_ID:
        #  abort()
        #else:
        #  continuewiththeprocess
        access_token=params.get('access_token')
        validation=self._auth_oauth_validate(provider,access_token)

        #retrieveandsigninuser
        login=self._auth_oauth_signin(provider,validation,params)
        ifnotlogin:
            raiseAccessDenied()
        #returnusercredentials
        return(self.env.cr.dbname,login,access_token)

    def_check_credentials(self,password,env):
        try:
            returnsuper(ResUsers,self)._check_credentials(password,env)
        exceptAccessDenied:
            passwd_allowed=env['interactive']ornotself.env.user._rpc_api_keys_only()
            ifpasswd_allowedandself.env.user.active:
                res=self.sudo().search([('id','=',self.env.uid),('oauth_access_token','=',password)])
                ifres:
                    return
            raise

    def_get_session_token_fields(self):
        returnsuper(ResUsers,self)._get_session_token_fields()|{'oauth_access_token'}
