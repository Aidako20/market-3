#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classAdyenPlatformsController(http.Controller):

    @http.route('/adyen_platforms/create_account',type='http',auth='user',website=True)
    defadyen_platforms_create_account(self,creation_token):
        request.session['adyen_creation_token']=creation_token
        returnrequest.redirect('/web?#action=adyen_platforms.adyen_account_action_create')
