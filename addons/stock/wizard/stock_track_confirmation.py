#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classStockTrackConfirmation(models.TransientModel):
    _name='stock.track.confirmation'
    _description='StockTrackConfirmation'

    tracking_line_ids=fields.One2many('stock.track.line','wizard_id')
    inventory_id=fields.Many2one('stock.inventory','Inventory')

    defaction_confirm(self):
        forconfirmationinself:
            confirmation.inventory_id._action_done()

classStockTrackingLines(models.TransientModel):
    _name='stock.track.line'
    _description='StockTrackLine'

    product_id=fields.Many2one('product.product','Product',readonly=True)
    tracking=fields.Selection([('lot','Trackedbylot'),('serial','Trackedbyserialnumber')],readonly=True)
    wizard_id=fields.Many2one('stock.track.confirmation',readonly=True)
