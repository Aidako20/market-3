#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockScrap(models.Model):
    _inherit='stock.scrap'

    production_id=fields.Many2one(
        'mrp.production','ManufacturingOrder',
        states={'done':[('readonly',True)]},check_company=True)
    workorder_id=fields.Many2one(
        'mrp.workorder','WorkOrder',
        states={'done':[('readonly',True)]},
        help='Nottorestrictorpreferquants,butinformative.',check_company=True)

    @api.onchange('workorder_id')
    def_onchange_workorder_id(self):
        ifself.workorder_id:
            self.location_id=self.workorder_id.production_id.location_src_id.id

    @api.onchange('production_id')
    def_onchange_production_id(self):
        ifself.production_id:
            self.location_id=self.production_id.move_raw_ids.filtered(lambdax:x.statenotin('done','cancel'))andself.production_id.location_src_id.idorself.production_id.location_dest_id.id

    def_prepare_move_values(self):
        vals=super(StockScrap,self)._prepare_move_values()
        ifself.production_id:
            vals['origin']=vals['origin']orself.production_id.name
            ifself.product_idinself.production_id.move_finished_ids.mapped('product_id'):
                vals.update({'production_id':self.production_id.id})
            else:
                vals.update({'raw_material_production_id':self.production_id.id})
        returnvals
