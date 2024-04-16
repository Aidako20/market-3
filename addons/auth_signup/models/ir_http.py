#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.httpimportrequest


classHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_dispatch(cls):
        #addsignuptokenorlogintothesessionifgiven
        if'auth_signup_token'inrequest.params:
            request.session['auth_signup_token']=request.params['auth_signup_token']
        if'auth_login'inrequest.params:
            request.session['auth_login']=request.params['auth_login']

        returnsuper(Http,cls)._dispatch()
