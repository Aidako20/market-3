#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classStockValuationLayer(models.Model):
    """StockValuationLayer"""

    _inherit='stock.valuation.layer'

    stock_landed_cost_id=fields.Many2one('stock.landed.cost','LandedCost')

