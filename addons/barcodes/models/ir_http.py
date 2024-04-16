#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    defsession_info(self):
        res=super(IrHttp,self).session_info()
        ifself.env.user.has_group('base.group_user'):
            res['max_time_between_keys_in_ms']=int(
                self.env['ir.config_parameter'].sudo().get_param('barcode.max_time_between_keys_in_ms',default='100'))
        returnres
