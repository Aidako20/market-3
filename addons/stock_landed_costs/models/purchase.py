fromflectraimportapi,models

classPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    def_prepare_account_move_line(self,move=False):
        res=super()._prepare_account_move_line(move)
        res.update({'is_landed_costs_line':self.product_id.landed_cost_ok})
        returnres
