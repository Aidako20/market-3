#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels
fromflectra.httpimportrequest


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_dispatch(cls):
        affiliate_id=request.httprequest.args.get('affiliate_id')
        ifaffiliate_id:
            request.session['affiliate_id']=int(affiliate_id)
        returnsuper(IrHttp,cls)._dispatch()
