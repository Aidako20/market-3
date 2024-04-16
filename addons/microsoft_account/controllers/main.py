#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
fromwerkzeug.utilsimportredirect

fromflectraimporthttp,registry
fromflectra.httpimportrequest


classMicrosoftAuth(http.Controller):

    @http.route('/microsoft_account/authentication',type='http',auth="public")
    defoauth2callback(self,**kw):
        """Thisroute/functioniscalledbyMicrosoftwhenuserAccept/RefusetheconsentofMicrosoft"""
        state=json.loads(kw['state'])
        dbname=state.get('d')
        service=state.get('s')
        url_return=state.get('f')

        withregistry(dbname).cursor()ascr:
            ifkw.get('code'):
                access_token,refresh_token,ttl=request.env['microsoft.service']._get_microsoft_tokens(kw['code'],service)
                request.env.user._set_microsoft_auth_tokens(access_token,refresh_token,ttl)
                returnredirect(url_return)
            elifkw.get('error'):
                returnredirect("%s%s%s"%(url_return,"?error=",kw['error']))
            else:
                returnredirect("%s%s"%(url_return,"?error=Unknown_error"))
