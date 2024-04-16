#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    def_prepare_stock_moves(self,picking):
        res=super(PurchaseOrderLine,self)._prepare_stock_moves(picking)
        forreinres:
            re['sale_line_id']=self.sale_line_id.id
        returnres

    def_find_candidate(self,product_id,product_qty,product_uom,location_id,name,origin,company_id,values):
        #ifthisisdefined,thisisadropshippingline,sono
        #thisistocorrectlymapdeliveredquantitiestothesolines
        lines=self.filtered(lambdapo_line:po_line.sale_line_id.id==values['sale_line_id'])ifvalues.get('sale_line_id')elseself
        returnsuper(PurchaseOrderLine,lines)._find_candidate(product_id,product_qty,product_uom,location_id,name,origin,company_id,values)

    @api.model
    def_prepare_purchase_order_line_from_procurement(self,product_id,product_qty,product_uom,company_id,values,po):
        res=super()._prepare_purchase_order_line_from_procurement(product_id,product_qty,product_uom,company_id,values,po)
        res['sale_line_id']=values.get('sale_line_id',False)
        returnres
