#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockReturnPicking(models.TransientModel):
    _inherit="stock.return.picking"

    @api.model
    defdefault_get(self,default_fields):
        res=super(StockReturnPicking,self).default_get(default_fields)
        fori,k,valsinres.get('product_return_moves',[]):
            vals.update({'to_refund':True})
        returnres

    def_create_returns(self):
        new_picking_id,pick_type_id=super(StockReturnPicking,self)._create_returns()
        new_picking=self.env['stock.picking'].browse([new_picking_id])
        formoveinnew_picking.move_lines:
            return_picking_line=self.product_return_moves.filtered(lambdar:r.move_id==move.origin_returned_move_id)[:1]
            ifreturn_picking_lineandreturn_picking_line.to_refund:
                move.to_refund=True
        returnnew_picking_id,pick_type_id


classStockReturnPickingLine(models.TransientModel):
    _inherit="stock.return.picking.line"

    to_refund=fields.Boolean(string="UpdatequantitiesonSO/PO",default=True,
        help='Triggeradecreaseofthedelivered/receivedquantityintheassociatedSaleOrder/PurchaseOrder')
