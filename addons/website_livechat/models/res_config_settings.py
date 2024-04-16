#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    channel_id=fields.Many2one('im_livechat.channel',string='WebsiteLiveChannel',related='website_id.channel_id',readonly=False)
