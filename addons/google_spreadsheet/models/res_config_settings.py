#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"

    google_drive_uri_copy=fields.Char(related='google_drive_uri',string='URICopy',help="TheURLtogeneratetheauthorizationcodefromGoogle",readonly=False)
