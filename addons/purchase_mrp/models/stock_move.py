#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,models
fromflectra.tools.float_utilsimportfloat_is_zero
fromflectra.exceptionsimportUserError


classStockMove(models.Model):
    _inherit='stock.move'

    def_prepare_phantom_move_values(self,bom_line,product_qty,quantity_done):
        vals=super(StockMove,self)._prepare_phantom_move_values(bom_line,product_qty,quantity_done)
        ifself.purchase_line_id:
            vals['purchase_line_id']=self.purchase_line_id.id
        returnvals

    def_get_valuation_price_and_qty(self,related_aml,to_curr):
        valuation_price_unit_total,valuation_total_qty=super()._get_valuation_price_and_qty(related_aml,to_curr)
        kit_bom=self.env['mrp.bom']._bom_find(product=related_aml.product_id,company_id=related_aml.company_id.id,bom_type='phantom')
        ifkit_bom:
            order_qty=related_aml.product_id.uom_id._compute_quantity(related_aml.quantity,kit_bom.product_uom_id)
            filters={
                'incoming_moves':lambdam:m.location_id.usage=='supplier'and(notm.origin_returned_move_idor(m.origin_returned_move_idandm.to_refund)),
                'outgoing_moves':lambdam:m.location_id.usage!='supplier'andm.to_refund
            }
            valuation_total_qty=self._compute_kit_quantities(related_aml.product_id,order_qty,kit_bom,filters)
            valuation_total_qty=kit_bom.product_uom_id._compute_quantity(valuation_total_qty,related_aml.product_id.uom_id)
            iffloat_is_zero(valuation_total_qty,precision_rounding=related_aml.product_uom_id.roundingorrelated_aml.product_id.uom_id.rounding):
                raiseUserError(_('Flectraisnotabletogeneratetheanglosaxonentries.Thetotalvaluationof%siszero.')%related_aml.product_id.display_name)
        returnvaluation_price_unit_total,valuation_total_qty
