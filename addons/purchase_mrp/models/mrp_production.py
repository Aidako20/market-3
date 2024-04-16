#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classMrpProduction(models.Model):
    _inherit='mrp.production'

    purchase_order_count=fields.Integer(
        "CountofgeneratedPO",
        compute='_compute_purchase_order_count',
        groups='purchase.group_purchase_user')

    @api.depends('procurement_group_id.stock_move_ids.created_purchase_line_id.order_id','procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id')
    def_compute_purchase_order_count(self):
        forproductioninself:
            production.purchase_order_count=len(production.procurement_group_id.stock_move_ids.created_purchase_line_id.order_id|
                                                  production.procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id)

    defaction_view_purchase_orders(self):
        self.ensure_one()
        purchase_order_ids=(self.procurement_group_id.stock_move_ids.created_purchase_line_id.order_id|self.procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id).ids
        action={
            'res_model':'purchase.order',
            'type':'ir.actions.act_window',
        }
        iflen(purchase_order_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':purchase_order_ids[0],
            })
        else:
            action.update({
                'name':_("PurchaseOrdergeneratedfrom%s",self.name),
                'domain':[('id','in',purchase_order_ids)],
                'view_mode':'tree,form',
            })
        returnaction

    def_get_document_iterate_key(self,move_raw_id):
        iterate_key=super(MrpProduction,self)._get_document_iterate_key(move_raw_id)
        ifnotiterate_keyandmove_raw_id.created_purchase_line_id:
            iterate_key='created_purchase_line_id'
        returniterate_key
