#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    def_compute_is_mto(self):
        super(SaleOrderLine,self)._compute_is_mto()
        forlineinself:
            ifnotline.display_qty_widgetorline.is_mto:
                continue
            product_routes=line.route_idor(line.product_id.route_ids+line.product_id.categ_id.total_route_ids)
            forpull_ruleinproduct_routes.mapped('rule_ids'):
                ifpull_rule.picking_type_id.sudo().default_location_src_id.usage=='supplier'and\
                        pull_rule.picking_type_id.sudo().default_location_dest_id.usage=='customer':
                    line.is_mto=True
                    break

    def_get_qty_procurement(self,previous_product_uom_qty):
        #Peoplewithoutpurchaserightsshouldbeabletodothisoperation
        purchase_lines_sudo=self.sudo().purchase_line_ids
        ifpurchase_lines_sudo.filtered(lambdar:r.state!='cancel'):
            qty=0.0
            forpo_lineinpurchase_lines_sudo.filtered(lambdar:r.state!='cancel'):
                qty+=po_line.product_uom._compute_quantity(po_line.product_qty,self.product_uom,rounding_method='HALF-UP')
            returnqty
        else:
            returnsuper(SaleOrderLine,self)._get_qty_procurement(previous_product_uom_qty=previous_product_uom_qty)
