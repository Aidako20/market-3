#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.httpimportrequest


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    defsession_info(self):
        user=request.env.user
        result=super(IrHttp,self).session_info()
        ifself.env.user.has_group('base.group_user'):
            result['notification_type']=user.notification_type
        returnresult
