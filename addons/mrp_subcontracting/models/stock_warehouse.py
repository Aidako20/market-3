#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_


classStockWarehouse(models.Model):
    _inherit='stock.warehouse'

    subcontracting_to_resupply=fields.Boolean(
        'ResupplySubcontractors',default=True,
        help="Resupplysubcontractorswithcomponents")

    subcontracting_mto_pull_id=fields.Many2one(
        'stock.rule','SubcontractingMTORule')
    subcontracting_pull_id=fields.Many2one(
        'stock.rule','SubcontractingMTSRule'
    )

    subcontracting_route_id=fields.Many2one('stock.location.route','ResupplySubcontractor',ondelete='restrict')

    subcontracting_type_id=fields.Many2one(
        'stock.picking.type','SubcontractingOperationType',
        domain=[('code','=','mrp_operation')])

    defget_rules_dict(self):
        result=super(StockWarehouse,self).get_rules_dict()
        subcontract_location_id=self._get_subcontracting_location()
        forwarehouseinself:
            result[warehouse.id].update({
                'subcontract':[
                    self.Routing(warehouse.lot_stock_id,subcontract_location_id,warehouse.out_type_id,'pull'),
                ]
            })
        returnresult

    def_get_routes_values(self):
        routes=super(StockWarehouse,self)._get_routes_values()
        routes.update({
            'subcontracting_route_id':{
                'routing_key':'subcontract',
                'depends':['subcontracting_to_resupply'],
                'route_create_values':{
                    'product_categ_selectable':False,
                    'warehouse_selectable':True,
                    'product_selectable':False,
                    'company_id':self.company_id.id,
                    'sequence':10,
                    'name':self._format_routename(name=_('ResupplySubcontractor'))
                },
                'route_update_values':{
                    'active':self.subcontracting_to_resupply,
                },
                'rules_values':{
                    'active':self.subcontracting_to_resupply,
                }
            }
        })
        returnroutes

    def_get_global_route_rules_values(self):
        rules=super(StockWarehouse,self)._get_global_route_rules_values()
        subcontract_location_id=self._get_subcontracting_location()
        production_location_id=self._get_production_location()
        rules.update({
            'subcontracting_mto_pull_id':{
                'depends':['subcontracting_to_resupply'],
                'create_values':{
                    'procure_method':'make_to_order',
                    'company_id':self.company_id.id,
                    'action':'pull',
                    'auto':'manual',
                    'route_id':self._find_global_route('stock.route_warehouse0_mto',_('MakeToOrder')).id,
                    'name':self._format_rulename(self.lot_stock_id,subcontract_location_id,'MTO'),
                    'location_id':subcontract_location_id.id,
                    'location_src_id':self.lot_stock_id.id,
                    'picking_type_id':self.out_type_id.id
                },
                'update_values':{
                    'active':self.subcontracting_to_resupply
                }
            },
            'subcontracting_pull_id':{
                'depends':['subcontracting_to_resupply'],
                'create_values':{
                    'procure_method':'make_to_order',
                    'company_id':self.company_id.id,
                    'action':'pull',
                    'auto':'manual',
                    'route_id':self._find_global_route('mrp_subcontracting.route_resupply_subcontractor_mto',
                                                        _('ResupplySubcontractoronOrder')).id,
                    'name':self._format_rulename(self.lot_stock_id,subcontract_location_id,False),
                    'location_id':production_location_id.id,
                    'location_src_id':subcontract_location_id.id,
                    'picking_type_id':self.out_type_id.id
                },
                'update_values':{
                    'active':self.subcontracting_to_resupply
                }
            },
        })
        returnrules

    def_get_picking_type_create_values(self,max_sequence):
        data,next_sequence=super(StockWarehouse,self)._get_picking_type_create_values(max_sequence)
        data.update({
            'subcontracting_type_id':{
                'name':_('Subcontracting'),
                'code':'mrp_operation',
                'use_create_components_lots':True,
                'sequence':next_sequence+2,
                'sequence_code':'SBC',
                'company_id':self.company_id.id,
            },
        })
        returndata,max_sequence+4

    def_get_sequence_values(self):
        values=super(StockWarehouse,self)._get_sequence_values()
        values.update({
            'subcontracting_type_id':{'name':self.name+''+_('Sequencesubcontracting'),'prefix':self.code+'/SBC/','padding':5,'company_id':self.company_id.id},
        })
        returnvalues

    def_get_picking_type_update_values(self):
        data=super(StockWarehouse,self)._get_picking_type_update_values()
        subcontract_location_id=self._get_subcontracting_location()
        production_location_id=self._get_production_location()
        data.update({
            'subcontracting_type_id':{
                'active':False,
                'default_location_src_id':subcontract_location_id.id,
                'default_location_dest_id':production_location_id.id,
            },
        })
        returndata

    def_get_subcontracting_location(self):
        returnself.company_id.subcontracting_location_id
