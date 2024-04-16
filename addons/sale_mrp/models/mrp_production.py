#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classMrpProduction(models.Model):
    _inherit='mrp.production'

    sale_order_count=fields.Integer(
        "CountofSourceSO",
        compute='_compute_sale_order_count',
        groups='sales_team.group_sale_salesman')

    @api.depends('procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id')
    def_compute_sale_order_count(self):
        forproductioninself:
            production.sale_order_count=len(production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id)

    defaction_view_sale_orders(self):
        self.ensure_one()
        sale_order_ids=self.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
        action={
            'res_model':'sale.order',
            'type':'ir.actions.act_window',
        }
        iflen(sale_order_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':sale_order_ids[0],
            })
        else:
            action.update({
                'name':_("SourcesSaleOrdersof%s",self.name),
                'domain':[('id','in',sale_order_ids)],
                'view_mode':'tree,form',
            })
        returnaction
