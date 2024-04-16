#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit='res.company'

    pad_server=fields.Char(help="Etherpadliteserver.Example:beta.primarypad.com")
    pad_key=fields.Char('PadApiKey',help="Etherpadliteapikey.",groups="base.group_system")
