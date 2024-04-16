#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    cal_microsoft_client_id=fields.Char("MicrosoftClient_id",config_parameter='microsoft_calendar_client_id',default='')
    cal_microsoft_client_secret=fields.Char("MicrosoftClient_key",config_parameter='microsoft_calendar_client_secret',default='')
