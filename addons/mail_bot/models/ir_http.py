#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classHttp(models.AbstractModel):
    _inherit='ir.http'

    defsession_info(self):
        res=super(Http,self).session_info()
        ifself.env.user.has_group('base.group_user'):
            res['flectrabot_initialized']=self.env.user.flectrabot_statenotin[False,'not_initialized']
        returnres
