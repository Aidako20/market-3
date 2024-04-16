#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importfunctools
importjson
importlogging
importos

importwerkzeug.urls
importwerkzeug.utils
fromwerkzeug.exceptionsimportBadRequest

fromflectraimportapi,http,SUPERUSER_ID,_
fromflectra.exceptionsimportAccessDenied
fromflectra.httpimportrequest
fromflectraimportregistryasregistry_get
fromflectra.tools.miscimportclean_context

fromflectra.addons.auth_signup.controllers.mainimportAuthSignupHomeasHome
fromflectra.addons.web.controllers.mainimportdb_monodb,ensure_db,set_cookie_and_redirect,login_and_redirect


_logger=logging.getLogger(__name__)


#----------------------------------------------------------
#helpers
#----------------------------------------------------------
deffragment_to_query_string(func):
    @functools.wraps(func)
    defwrapper(self,*a,**kw):
        kw.pop('debug',False)
        ifnotkw:
            return"""<html><head><script>
                varl=window.location;
                varq=l.hash.substring(1);
                varr=l.pathname+l.search;
                if(q.length!==0){
                    vars=l.search?(l.search==='?'?'':'&'):'?';
                    r=l.pathname+l.search+s+q;
                }
                if(r==l.pathname){
                    r='/';
                }
                window.location=r;
            </script></head><body></body></html>"""
        returnfunc(self,*a,**kw)
    returnwrapper


#----------------------------------------------------------
#Controller
#----------------------------------------------------------
classOAuthLogin(Home):
    deflist_providers(self):
        try:
            providers=request.env['auth.oauth.provider'].sudo().search_read([('enabled','=',True)])
        exceptException:
            providers=[]
        forproviderinproviders:
            return_url=request.httprequest.url_root+'auth_oauth/signin'
            state=self.get_state(provider)
            params=dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
                #nonce=base64.urlsafe_b64encode(os.urandom(16)),
            )
            provider['auth_link']="%s?%s"%(provider['auth_endpoint'],werkzeug.urls.url_encode(params))
        returnproviders

    defget_state(self,provider):
        redirect=request.params.get('redirect')or'web'
        ifnotredirect.startswith(('//','http://','https://')):
            redirect='%s%s'%(request.httprequest.url_root,redirect[1:]ifredirect[0]=='/'elseredirect)
        state=dict(
            d=request.session.db,
            p=provider['id'],
            r=werkzeug.urls.url_quote_plus(redirect),
        )
        token=request.params.get('token')
        iftoken:
            state['t']=token
        returnstate

    @http.route()
    defweb_login(self,*args,**kw):
        ensure_db()
        ifrequest.httprequest.method=='GET'andrequest.session.uidandrequest.params.get('redirect'):
            #Redirectifalreadyloggedinandredirectparamispresent
            returnhttp.redirect_with_hash(request.params.get('redirect'))
        providers=self.list_providers()

        response=super(OAuthLogin,self).web_login(*args,**kw)
        ifresponse.is_qweb:
            error=request.params.get('oauth_error')
            iferror=='1':
                error=_("Signupisnotallowedonthisdatabase.")
            eliferror=='2':
                error=_("AccessDenied")
            eliferror=='3':
                error=_("Youdonothaveaccesstothisdatabaseoryourinvitationhasexpired.Pleaseaskforaninvitationandbesuretofollowthelinkinyourinvitationemail.")
            else:
                error=None

            response.qcontext['providers']=providers
            iferror:
                response.qcontext['error']=error

        returnresponse

    defget_auth_signup_qcontext(self):
        result=super(OAuthLogin,self).get_auth_signup_qcontext()
        result["providers"]=self.list_providers()
        returnresult


classOAuthController(http.Controller):

    @http.route('/auth_oauth/signin',type='http',auth='none')
    @fragment_to_query_string
    defsignin(self,**kw):
        state=json.loads(kw['state'])
        dbname=state['d']
        ifnothttp.db_filter([dbname]):
            returnBadRequest()
        provider=state['p']
        context=clean_context(state.get('c',{}))
        registry=registry_get(dbname)
        withregistry.cursor()ascr:
            try:
                env=api.Environment(cr,SUPERUSER_ID,context)
                credentials=env['res.users'].sudo().auth_oauth(provider,kw)
                cr.commit()
                action=state.get('a')
                menu=state.get('m')
                redirect=werkzeug.urls.url_unquote_plus(state['r'])ifstate.get('r')elseFalse
                url='/web'
                ifredirect:
                    url=redirect
                elifaction:
                    url='/web#action=%s'%action
                elifmenu:
                    url='/web#menu_id=%s'%menu
                resp=login_and_redirect(*credentials,redirect_url=url)
                #Since/webishardcoded,verifyuserhasrighttolandonit
                ifwerkzeug.urls.url_parse(resp.location).path=='/web'andnotrequest.env.user.has_group('base.group_user'):
                    resp.location='/'
                returnresp
            exceptAttributeError:
                #auth_signupisnotinstalled
                _logger.error("auth_signupnotinstalledondatabase%s:oauthsignupcancelled."%(dbname,))
                url="/web/login?oauth_error=1"
            exceptAccessDenied:
                #oauthcredentialsnotvalid,usercouldbeonatemporarysession
                _logger.info('OAuth2:accessdenied,redirecttomainpageincaseavalidsessionexists,withoutsettingcookies')
                url="/web/login?oauth_error=3"
                redirect=werkzeug.utils.redirect(url,303)
                redirect.autocorrect_location_header=False
                returnredirect
            exceptExceptionase:
                #signuperror
                _logger.exception("OAuth2:%s"%str(e))
                url="/web/login?oauth_error=2"

        returnset_cookie_and_redirect(url)

    @http.route('/auth_oauth/oea',type='http',auth='none')
    defoea(self,**kw):
        """loginuserviaFlectraAccountprovider"""
        dbname=kw.pop('db',None)
        ifnotdbname:
            dbname=db_monodb()
        ifnotdbname:
            returnBadRequest()
        ifnothttp.db_filter([dbname]):
            returnBadRequest()

        registry=registry_get(dbname)
        withregistry.cursor()ascr:
            try:
                env=api.Environment(cr,SUPERUSER_ID,{})
                provider=env.ref('auth_oauth.provider_openerp')
            exceptValueError:
                returnset_cookie_and_redirect('/web?db=%s'%dbname)
            assertprovider._name=='auth.oauth.provider'

        state={
            'd':dbname,
            'p':provider.id,
            'c':{'no_user_creation':True},
        }

        kw['state']=json.dumps(state)
        returnself.signin(**kw)
