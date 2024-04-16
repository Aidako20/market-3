#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classAccountMove(models.Model):
    _inherit='account.move'

    website_id=fields.Many2one('website',related='partner_id.website_id',string='Website',
                                 help='Websitethroughwhichthisinvoicewascreated.',
                                 store=True,readonly=True,tracking=True)
