#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
fromwerkzeug.exceptionsimportBadRequest
fromwerkzeug.utilsimportredirect

fromflectraimporthttp,registry
fromflectra.httpimportrequest


classGoogleAuth(http.Controller):

    @http.route('/google_account/authentication',type='http',auth="public")
    defoauth2callback(self,**kw):
        """Thisroute/functioniscalledbyGooglewhenuserAccept/RefusetheconsentofGoogle"""
        state=json.loads(kw.get('state','{}'))
        dbname=state.get('d')
        service=state.get('s')
        url_return=state.get('f')
        base_url=request.httprequest.url_root.strip('/')
        if(notdbnameornotserviceor(kw.get('code')andnoturl_return)):
            raiseBadRequest()

        withregistry(dbname).cursor()ascr:
            ifkw.get('code'):
                access_token,refresh_token,ttl=request.env['google.service'].with_context(base_url=base_url)._get_google_tokens(kw['code'],service)
                #LULTODOonlydefinedingoogle_calendar
                request.env.user._set_auth_tokens(access_token,refresh_token,ttl)
                returnredirect(url_return)
            elifkw.get('error'):
                returnredirect("%s%s%s"%(url_return,"?error=",kw['error']))
            else:
                returnredirect("%s%s"%(url_return,"?error=Unknown_error"))
