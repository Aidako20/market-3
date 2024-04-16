#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    @api.onchange('requisition_id')
    def_onchange_requisition_id(self):
        super(PurchaseOrder,self)._onchange_requisition_id()
        ifself.requisition_id:
            self.picking_type_id=self.requisition_id.picking_type_id.id
