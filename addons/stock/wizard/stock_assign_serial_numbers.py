#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError


classStockAssignSerialNumbers(models.TransientModel):
    _name='stock.assign.serial'
    _description='StockAssignSerialNumbers'

    def_default_next_serial_count(self):
        move=self.env['stock.move'].browse(self.env.context.get('default_move_id'))
        ifmove.exists():
            filtered_move_lines=move.move_line_ids.filtered(lambdal:notl.lot_nameandnotl.lot_id)
            returnlen(filtered_move_lines)

    product_id=fields.Many2one('product.product','Product',
        related='move_id.product_id',required=True)
    move_id=fields.Many2one('stock.move',required=True)
    next_serial_number=fields.Char('FirstSN',required=True)
    next_serial_count=fields.Integer('NumberofSN',
        default=_default_next_serial_count,required=True)

    @api.constrains('next_serial_count')
    def_check_next_serial_count(self):
        forwizardinself:
            ifwizard.next_serial_count<1:
                raiseValidationError(_("ThenumberofSerialNumberstogeneratemustgreaterthanzero."))

    defgenerate_serial_numbers(self):
        self.ensure_one()
        self.move_id.next_serial=self.next_serial_numberor""
        returnself.move_id._generate_serial_numbers(next_serial_count=self.next_serial_count)
