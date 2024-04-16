#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models



classStockMoveLine(models.Model):
    _inherit='stock.move.line'

    def_compute_sale_price(self):
        kit_lines=self.filtered(lambdamove_line:move_line.move_id.bom_line_id.bom_id.type=='phantom')
        formove_lineinkit_lines:
            unit_price=move_line.product_id.list_price
            qty=move_line.product_uom_id._compute_quantity(move_line.qty_done,move_line.product_id.uom_id)
            move_line.sale_price=unit_price*qty
        super(StockMoveLine,self-kit_lines)._compute_sale_price()
