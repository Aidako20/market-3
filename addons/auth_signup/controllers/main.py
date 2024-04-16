#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
importwerkzeug

fromflectraimporthttp,tools,_
fromflectra.addons.auth_signup.models.res_usersimportSignupError
fromflectra.addons.web.controllers.mainimportensure_db,Home,SIGN_UP_REQUEST_PARAMS
fromflectra.addons.base_setup.controllers.mainimportBaseSetup
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classAuthSignupHome(Home):

    @http.route()
    defweb_login(self,*args,**kw):
        ensure_db()
        response=super(AuthSignupHome,self).web_login(*args,**kw)
        response.qcontext.update(self.get_auth_signup_config())
        ifrequest.httprequest.method=='GET'andrequest.session.uidandrequest.params.get('redirect'):
            #Redirectifalreadyloggedinandredirectparamispresent
            returnhttp.redirect_with_hash(request.params.get('redirect'))
        returnresponse

    @http.route('/web/signup',type='http',auth='public',website=True,sitemap=False)
    defweb_auth_signup(self,*args,**kw):
        qcontext=self.get_auth_signup_qcontext()

        ifnotqcontext.get('token')andnotqcontext.get('signup_enabled'):
            raisewerkzeug.exceptions.NotFound()

        if'error'notinqcontextandrequest.httprequest.method=='POST':
            try:
                self.do_signup(qcontext)
                #Sendanaccountcreationconfirmationemail
                User=request.env['res.users']
                user_sudo=User.sudo().search(
                    User._get_login_domain(qcontext.get('login')),order=User._get_login_order(),limit=1
                )
                template=request.env.ref('auth_signup.mail_template_user_signup_account_created',raise_if_not_found=False)
                ifuser_sudoandtemplate:
                    template.sudo().send_mail(user_sudo.id,force_send=True)
                returnself.web_login(*args,**kw)
            exceptUserErrorase:
                qcontext['error']=e.args[0]
            except(SignupError,AssertionError)ase:
                ifrequest.env["res.users"].sudo().search([("login","=",qcontext.get("login"))]):
                    qcontext["error"]=_("Anotheruserisalreadyregisteredusingthisemailaddress.")
                else:
                    _logger.error("%s",e)
                    qcontext['error']=_("Couldnotcreateanewaccount.")

        response=request.render('auth_signup.signup',qcontext)
        response.headers['X-Frame-Options']='DENY'
        returnresponse

    @http.route('/web/reset_password',type='http',auth='public',website=True,sitemap=False)
    defweb_auth_reset_password(self,*args,**kw):
        qcontext=self.get_auth_signup_qcontext()

        ifnotqcontext.get('token')andnotqcontext.get('reset_password_enabled'):
            raisewerkzeug.exceptions.NotFound()

        if'error'notinqcontextandrequest.httprequest.method=='POST':
            try:
                ifqcontext.get('token'):
                    self.do_signup(qcontext)
                    returnself.web_login(*args,**kw)
                else:
                    login=qcontext.get('login')
                    assertlogin,_("Nologinprovided.")
                    _logger.info(
                        "Passwordresetattemptfor<%s>byuser<%s>from%s",
                        login,request.env.user.login,request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message']=_("Anemailhasbeensentwithcredentialstoresetyourpassword")
            exceptUserErrorase:
                qcontext['error']=e.args[0]
            exceptSignupError:
                qcontext['error']=_("Couldnotresetyourpassword")
                _logger.exception('errorwhenresettingpassword')
            exceptExceptionase:
                qcontext['error']=str(e)

        response=request.render('auth_signup.reset_password',qcontext)
        response.headers['X-Frame-Options']='DENY'
        returnresponse

    defget_auth_signup_config(self):
        """retrievethemoduleconfig(whichfeaturesareenabled)fortheloginpage"""

        get_param=request.env['ir.config_parameter'].sudo().get_param
        return{
            'disable_database_manager':nottools.config['list_db'],
            'signup_enabled':request.env['res.users']._get_signup_invitation_scope()=='b2c',
            'reset_password_enabled':get_param('auth_signup.reset_password')=='True',
        }

    defget_auth_signup_qcontext(self):
        """Sharedhelperreturningtherenderingcontextforsignupandresetpassword"""
        qcontext={k:vfor(k,v)inrequest.params.items()ifkinSIGN_UP_REQUEST_PARAMS}
        qcontext.update(self.get_auth_signup_config())
        ifnotqcontext.get('token')andrequest.session.get('auth_signup_token'):
            qcontext['token']=request.session.get('auth_signup_token')
        ifqcontext.get('token'):
            try:
                #retrievetheuserinfo(name,loginoremail)correspondingtoasignuptoken
                token_infos=request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                fork,vintoken_infos.items():
                    qcontext.setdefault(k,v)
            except:
                qcontext['error']=_("Invalidsignuptoken")
                qcontext['invalid_token']=True
        returnqcontext

    defdo_signup(self,qcontext):
        """Sharedhelperthatcreatesares.partneroutofatoken"""
        values={key:qcontext.get(key)forkeyin('login','name','password')}
        ifnotvalues:
            raiseUserError(_("Theformwasnotproperlyfilledin."))
        ifvalues.get('password')!=qcontext.get('confirm_password'):
            raiseUserError(_("Passwordsdonotmatch;pleaseretypethem."))
        supported_lang_codes=[codeforcode,_inrequest.env['res.lang'].get_installed()]
        lang=request.context.get('lang','')
        iflanginsupported_lang_codes:
            values['lang']=lang
        self._signup_with_values(qcontext.get('token'),values)
        request.env.cr.commit()

    def_signup_with_values(self,token,values):
        db,login,password=request.env['res.users'].sudo().signup(values,token)
        request.env.cr.commit()    #asauthenticatewilluseitsowncursorweneedtocommitthecurrenttransaction
        uid=request.session.authenticate(db,login,password)
        ifnotuid:
            raiseSignupError(_('AuthenticationFailed.'))

classAuthBaseSetup(BaseSetup):
    @http.route('/base_setup/data',type='json',auth='user')
    defbase_setup_data(self,**kwargs):
        res=super().base_setup_data(**kwargs)
        res.update({'resend_invitation':True})
        returnres
