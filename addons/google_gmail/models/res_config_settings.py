#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    google_gmail_client_identifier=fields.Char('GmailClientId',config_parameter='google_gmail_client_id')
    google_gmail_client_secret=fields.Char('GmailClientSecret',config_parameter='google_gmail_client_secret')
