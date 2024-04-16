#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classReplenishmentReport(models.AbstractModel):
    _inherit='report.stock.report_product_product_replenishment'

    def_compute_draft_quantity_count(self,product_template_ids,product_variant_ids,wh_location_ids):
        res=super()._compute_draft_quantity_count(product_template_ids,product_variant_ids,wh_location_ids)
        domain=[('state','in',['draft','sent','toapprove'])]
        domain+=self._product_purchase_domain(product_template_ids,product_variant_ids)
        warehouse_id=self.env.context.get('warehouse',False)
        ifwarehouse_id:
            domain+=[('order_id.picking_type_id.warehouse_id','=',warehouse_id)]
        po_lines=self.env['purchase.order.line'].read_group(domain,['product_uom_qty'],'product_id')
        in_sum=sum(line['product_uom_qty']forlineinpo_lines)

        res['draft_purchase_qty']=in_sum
        res['qty']['in']+=in_sum
        returnres

    def_product_purchase_domain(self,product_template_ids,product_variant_ids):
        ifproduct_variant_ids:
            return[('product_id','in',product_variant_ids)]
        elifproduct_template_ids:
            products=self.env['product.product'].search_read(
                [('product_tmpl_id','in',product_template_ids)],['id']
            )
            product_ids=[product['id']forproductinproducts]
            return[('product_id','in',product_ids)]
