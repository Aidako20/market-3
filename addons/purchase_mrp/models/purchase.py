#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    mrp_production_count=fields.Integer(
        "CountofMOSource",
        compute='_compute_mrp_production_count',
        groups='mrp.group_mrp_user')

    @api.depends('order_line.move_dest_ids.group_id.mrp_production_ids')
    def_compute_mrp_production_count(self):
        forpurchaseinself:
            purchase.mrp_production_count=len(purchase.order_line.move_dest_ids.group_id.mrp_production_ids|
                                                purchase.order_line.move_ids.move_dest_ids.group_id.mrp_production_ids)

    defaction_view_mrp_productions(self):
        self.ensure_one()
        mrp_production_ids=(self.order_line.move_dest_ids.group_id.mrp_production_ids|self.order_line.move_ids.move_dest_ids.group_id.mrp_production_ids).ids
        action={
            'res_model':'mrp.production',
            'type':'ir.actions.act_window',
        }
        iflen(mrp_production_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':mrp_production_ids[0],
            })
        else:
            action.update({
                'name':_("ManufacturingSourceof%s",self.name),
                'domain':[('id','in',mrp_production_ids)],
                'view_mode':'tree,form',
            })
        returnaction


classPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    def_compute_qty_received(self):
        kit_lines=self.env['purchase.order.line']
        forlineinself:
            ifline.qty_received_method=='stock_moves'andline.move_ids.filtered(lambdam:m.state!='cancel'):
                kit_bom=self.env['mrp.bom']._bom_find(product=line.product_id,company_id=line.company_id.id,bom_type='phantom')
                ifkit_bom:
                    moves=line.move_ids.filtered(lambdam:m.state=='done'andnotm.scrapped)
                    order_qty=line.product_uom._compute_quantity(line.product_uom_qty,kit_bom.product_uom_id)
                    filters={
                        'incoming_moves':lambdam:m.location_id.usage=='supplier'and(notm.origin_returned_move_idor(m.origin_returned_move_idandm.to_refund)),
                        'outgoing_moves':lambdam:m.location_id.usage!='supplier'andm.to_refund
                    }
                    line.qty_received=moves._compute_kit_quantities(line.product_id,order_qty,kit_bom,filters)
                    kit_lines+=line
        super(PurchaseOrderLine,self-kit_lines)._compute_qty_received()

    def_get_upstream_documents_and_responsibles(self,visited):
        return[(self.order_id,self.order_id.user_id,visited)]
    
    def_get_qty_procurement(self):
        self.ensure_one()
        #SpecificcasewhenwechangetheqtyonaPOforakitproduct.
        #Wedon'ttrytobetoosmartandkeepasimpleapproach:wecomparethequantitybefore
        #andafterupdate,andreturnthedifference.Wedon'ttakeintoaccountwhatwasalready
        #sent,oranyotherexceptionalcase.
        bom=self.env['mrp.bom'].sudo()._bom_find(product=self.product_id)
        ifbomandbom.type=='phantom'and'previous_product_qty'inself.env.context:
            returnself.env.context['previous_product_qty'].get(self.id,0.0)
        returnsuper()._get_qty_procurement()

