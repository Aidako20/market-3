#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    microsoft_outlook_client_identifier=fields.Char('OutlookClientId',config_parameter='microsoft_outlook_client_id')
    microsoft_outlook_client_secret=fields.Char('OutlookClientSecret',config_parameter='microsoft_outlook_client_secret')
