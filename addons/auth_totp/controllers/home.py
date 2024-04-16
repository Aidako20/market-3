#-*-coding:utf-8-*-
importre

importflectra.addons.web.controllers.main
fromflectraimporthttp,_
fromflectra.addons.auth_totp.models.res_usersimportTRUSTED_DEVICE_SCOPE
fromflectra.exceptionsimportAccessDenied
fromflectra.httpimportrequest

TRUSTED_DEVICE_COOKIE='td_id'
TRUSTED_DEVICE_AGE=90*86400#90daysexpiration


classHome(flectra.addons.web.controllers.main.Home):
    @http.route(
        '/web/login/totp',
        type='http',auth='public',methods=['GET','POST'],sitemap=False,
        website=True,multilang=False#websitebreakstheloginlayout...
    )
    defweb_totp(self,redirect=None,**kwargs):
        ifrequest.session.uid:
            returnhttp.redirect_with_hash(self._login_redirect(request.session.uid,redirect=redirect))

        ifnotrequest.session.pre_uid:
            returnhttp.redirect_with_hash('/web/login')

        error=None
        user=request.env['res.users'].browse(request.session.pre_uid)
        ifuserandrequest.httprequest.method=='GET':
            cookies=request.httprequest.cookies
            key=cookies.get(TRUSTED_DEVICE_COOKIE)
            ifkey:
                checked_credentials=request.env['res.users.apikeys']._check_credentials(scope=TRUSTED_DEVICE_SCOPE,key=key)
                ifchecked_credentials==user.id:
                    request.session.finalize()
                    returnhttp.redirect_with_hash(self._login_redirect(request.session.uid,redirect=redirect))

        elifuserandrequest.httprequest.method=='POST':
            try:
                withuser._assert_can_auth():
                    user._totp_check(int(re.sub(r'\s','',kwargs['totp_token'])))
            exceptAccessDenied:
                error=_("Verificationfailed,pleasedouble-checkthe6-digitcode")
            exceptValueError:
                error=_("Invalidauthenticationcodeformat.")
            else:
                request.session.finalize()
                response=http.redirect_with_hash(self._login_redirect(request.session.uid,redirect=redirect))
                ifkwargs.get('remember'):
                    name=_("%(browser)son%(platform)s",
                        browser=request.httprequest.user_agent.browser.capitalize(),
                        platform=request.httprequest.user_agent.platform.capitalize(),
                    )
                    geoip=request.session.get('geoip')
                    ifgeoip:
                        name+="(%s,%s)"%(geoip['city'],geoip['country_name'])

                    key=request.env['res.users.apikeys']._generate(TRUSTED_DEVICE_SCOPE,name)
                    response.set_cookie(
                        key=TRUSTED_DEVICE_COOKIE,
                        value=key,
                        max_age=TRUSTED_DEVICE_AGE,
                        httponly=True,
                        samesite='Lax'
                    )
                returnresponse

        returnrequest.render('auth_totp.auth_totp_form',{
            'error':error,
            'redirect':redirect,
        })
