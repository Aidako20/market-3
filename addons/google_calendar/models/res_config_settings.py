#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    cal_client_id=fields.Char("Client_id",config_parameter='google_calendar_client_id',default='')
    cal_client_secret=fields.Char("Client_key",config_parameter='google_calendar_client_secret',default='')
