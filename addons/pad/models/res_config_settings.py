#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    pad_server=fields.Char(related='company_id.pad_server',string="PadServer",readonly=False)
    pad_key=fields.Char(related='company_id.pad_key',string="PadAPIKey",readonly=False)
