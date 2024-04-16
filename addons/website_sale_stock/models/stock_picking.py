#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api,fields
fromflectra.tools.translateimport_


classStockPicking(models.Model):
    _inherit='stock.picking'

    website_id=fields.Many2one('website',related='sale_id.website_id',string='Website',
                                 help='Websitethispickingbelongsto.',
                                 store=True,readonly=True)

