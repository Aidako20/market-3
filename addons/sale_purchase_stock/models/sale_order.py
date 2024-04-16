#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classSaleOrder(models.Model):
    _inherit='sale.order'

    @api.depends('procurement_group_id.stock_move_ids.created_purchase_line_id.order_id','procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id')
    def_compute_purchase_order_count(self):
        super(SaleOrder,self)._compute_purchase_order_count()

    def_get_purchase_orders(self):
        returnsuper(SaleOrder,self)._get_purchase_orders()|self.procurement_group_id.stock_move_ids.created_purchase_line_id.order_id|self.procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id
