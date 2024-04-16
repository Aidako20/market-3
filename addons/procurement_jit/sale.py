#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    def_action_launch_stock_rule(self,previous_product_uom_qty=False):
        res=super(SaleOrderLine,self)._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
        orders=list(set(x.order_idforxinself))
        fororderinorders:
            reassign=order.picking_ids.filtered(lambdax:x.state=='confirmed'or(x.statein['waiting','assigned']andnotx.printed))
            ifreassign:
                #TriggertheSchedulerforPickings
                reassign.action_confirm()
                reassign.action_assign()
        returnres
