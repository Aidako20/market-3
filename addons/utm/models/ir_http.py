#-*-coding:utf-8-*-
fromflectra.httpimportrequest
fromflectraimportmodels


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    defget_utm_domain_cookies(cls):
        returnrequest.httprequest.host

    @classmethod
    def_set_utm(cls,response):
        ifisinstance(response,Exception):
            returnresponse
        #theparentdispatchmightdestroythesession
        ifnotrequest.db:
            returnresponse

        domain=cls.get_utm_domain_cookies()
        forvar,dummy,cookinrequest.env['utm.mixin'].tracking_fields():
            ifvarinrequest.paramsandrequest.httprequest.cookies.get(var)!=request.params[var]:
                response.set_cookie(cook,request.params[var],domain=domain)
        returnresponse

    @classmethod
    def_dispatch(cls):
        response=super(IrHttp,cls)._dispatch()
        returncls._set_utm(response)

    @classmethod
    def_handle_exception(cls,exc):
        response=super(IrHttp,cls)._handle_exception(exc)
        returncls._set_utm(response)
