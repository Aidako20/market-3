#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    jitsi_server_domain=fields.Char(
        'JitsiServerDomain',default='meet.jit.si',config_parameter='website_jitsi.jitsi_server_domain',
        help='TheJitsiserverdomaincanbecustomizedthroughthesettingstouseadifferentserverthanthedefault"meet.jit.si"')
