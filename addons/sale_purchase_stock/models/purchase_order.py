#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    @api.depends('order_line.move_dest_ids.group_id.sale_id','order_line.move_ids.move_dest_ids.group_id.sale_id')
    def_compute_sale_order_count(self):
        super(PurchaseOrder,self)._compute_sale_order_count()

    def_get_sale_orders(self):
        returnsuper(PurchaseOrder,self)._get_sale_orders()|self.order_line.move_dest_ids.group_id.sale_id|self.order_line.move_ids.move_dest_ids.group_id.sale_id
