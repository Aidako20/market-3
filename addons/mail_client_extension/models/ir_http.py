#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.exceptionsimportBadRequest

fromflectraimportmodels
fromflectra.httpimportrequest

classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_auth_method_outlook(cls):
        access_token=request.httprequest.headers.get('Authorization')
        ifnotaccess_token:
            raiseBadRequest('Accesstokenmissing')

        ifaccess_token.startswith('Bearer'):
            access_token=access_token[7:]

        user_id=request.env["res.users.apikeys"]._check_credentials(scope='flectra.plugin.outlook',key=access_token)
        ifnotuser_id:
            raiseBadRequest('Accesstokeninvalid')

        #taketheidentityoftheAPIkeyuser
        request.uid=user_id