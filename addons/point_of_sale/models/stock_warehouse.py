#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classWarehouse(models.Model):
    _inherit="stock.warehouse"

    pos_type_id=fields.Many2one('stock.picking.type',string="PointofSaleOperationType")

    def_get_sequence_values(self):
        sequence_values=super(Warehouse,self)._get_sequence_values()
        sequence_values.update({
            'pos_type_id':{
                'name':self.name+''+_('PickingPOS'),
                'prefix':self.code+'/POS/',
                'padding':5,
                'company_id':self.company_id.id,
            }
        })
        returnsequence_values

    def_get_picking_type_update_values(self):
        picking_type_update_values=super(Warehouse,self)._get_picking_type_update_values()
        picking_type_update_values.update({
            'pos_type_id':{'default_location_src_id':self.lot_stock_id.id}
        })
        returnpicking_type_update_values

    def_get_picking_type_create_values(self,max_sequence):
        picking_type_create_values,max_sequence=super(Warehouse,self)._get_picking_type_create_values(max_sequence)
        picking_type_create_values.update({
            'pos_type_id':{
                'name':_('PoSOrders'),
                'code':'outgoing',
                'default_location_src_id':self.lot_stock_id.id,
                'default_location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'sequence':max_sequence+1,
                'sequence_code':'POS',
                'company_id':self.company_id.id,
                'show_operations':False,
            }
        })
        returnpicking_type_create_values,max_sequence+2

    @api.model
    def_create_missing_pos_picking_types(self):
        warehouses=self.env['stock.warehouse'].search([('pos_type_id','=',False)])
        forwarehouseinwarehouses:
            new_vals=warehouse._create_or_update_sequences_and_picking_types()
            warehouse.write(new_vals)
