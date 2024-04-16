#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classReplenishmentReport(models.AbstractModel):
    _inherit='report.stock.report_product_product_replenishment'

    def_compute_draft_quantity_count(self,product_template_ids,product_variant_ids,wh_location_ids):
        res=super()._compute_draft_quantity_count(product_template_ids,product_variant_ids,wh_location_ids)
        domain=self._product_sale_domain(product_template_ids,product_variant_ids)
        so_lines=self.env['sale.order.line'].search(domain)
        out_sum=0
        ifso_lines:
            product_uom=so_lines[0].product_id.uom_id
            quantities=so_lines.mapped(lambdaline:line.product_uom._compute_quantity(line.product_uom_qty,product_uom))
            out_sum=sum(quantities)
        res['draft_sale_qty']=out_sum
        res['qty']['out']+=out_sum
        returnres

    def_product_sale_domain(self,product_template_ids,product_variant_ids):
        domain=[('state','in',['draft','sent'])]
        ifproduct_template_ids:
            domain+=[('product_template_id','in',product_template_ids)]
        elifproduct_variant_ids:
            domain+=[('product_id','in',product_variant_ids)]
        warehouse_id=self.env.context.get('warehouse',False)
        ifwarehouse_id:
            domain+=[('warehouse_id','=',warehouse_id)]
        returndomain
