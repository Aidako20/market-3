#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.httpimportrequest


classHttp(models.AbstractModel):
    _inherit='ir.http'

    defsession_info(self):
        result=super(Http,self).session_info()
        ifresult['is_admin']:
            result['web_tours']=request.env['web_tour.tour'].get_consumed_tours()
        returnresult
