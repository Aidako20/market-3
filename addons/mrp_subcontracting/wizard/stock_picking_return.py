#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields


classReturnPicking(models.TransientModel):
    _inherit='stock.return.picking'

    subcontract_location_id=fields.Many2one('stock.location',compute='_compute_subcontract_location_id')

    @api.depends('picking_id')
    def_compute_subcontract_location_id(self):
        forrecordinself:
            record.subcontract_location_id=record.picking_id.partner_id.with_company(
                record.picking_id.company_id
            ).property_stock_subcontractor

    @api.onchange('picking_id')
    def_onchange_picking_id(self):
        res=super(ReturnPicking,self)._onchange_picking_id()
        ifany(return_line.quantity>0andreturn_line.move_id.is_subcontractforreturn_lineinself.product_return_moves):
            self.location_id=self.picking_id.partner_id.with_company(self.picking_id.company_id).property_stock_subcontractor
        returnres

    def_prepare_move_default_values(self,return_line,new_picking):
        vals=super(ReturnPicking,self)._prepare_move_default_values(return_line,new_picking)
        vals['is_subcontract']=False
        returnvals
