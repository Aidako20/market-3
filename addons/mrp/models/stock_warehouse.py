#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError,UserError


classStockWarehouse(models.Model):
    _inherit='stock.warehouse'

    manufacture_to_resupply=fields.Boolean(
        'ManufacturetoResupply',default=True,
        help="Whenproductsaremanufactured,theycanbemanufacturedinthiswarehouse.")
    manufacture_pull_id=fields.Many2one(
        'stock.rule','ManufactureRule')
    manufacture_mto_pull_id=fields.Many2one(
        'stock.rule','ManufactureMTORule')
    pbm_mto_pull_id=fields.Many2one(
        'stock.rule','PickingBeforeManufacturingMTORule')
    sam_rule_id=fields.Many2one(
        'stock.rule','StockAfterManufacturingRule')
    manu_type_id=fields.Many2one(
        'stock.picking.type','ManufacturingOperationType',
        domain="[('code','=','mrp_operation'),('company_id','=',company_id)]",check_company=True)

    pbm_type_id=fields.Many2one('stock.picking.type','PickingBeforeManufacturingOperationType',check_company=True)
    sam_type_id=fields.Many2one('stock.picking.type','StockAfterManufacturingOperationType',check_company=True)

    manufacture_steps=fields.Selection([
        ('mrp_one_step','Manufacture(1step)'),
        ('pbm','Pickcomponentsandthenmanufacture(2steps)'),
        ('pbm_sam','Pickcomponents,manufactureandthenstoreproducts(3steps)')],
        'Manufacture',default='mrp_one_step',required=True,
        help="Produce:Movethecomponentstotheproductionlocation\
        directlyandstartthemanufacturingprocess.\nPick/Produce:Unload\
        thecomponentsfromtheStocktoInputlocationfirst,andthen\
        transferittotheProductionlocation.")

    pbm_route_id=fields.Many2one('stock.location.route','PickingBeforeManufacturingRoute',ondelete='restrict')

    pbm_loc_id=fields.Many2one('stock.location','PickingbeforeManufacturingLocation',check_company=True)
    sam_loc_id=fields.Many2one('stock.location','StockafterManufacturingLocation',check_company=True)

    defget_rules_dict(self):
        result=super(StockWarehouse,self).get_rules_dict()
        production_location_id=self._get_production_location()
        forwarehouseinself:
            result[warehouse.id].update({
                'mrp_one_step':[],
                'pbm':[
                    self.Routing(warehouse.lot_stock_id,warehouse.pbm_loc_id,warehouse.pbm_type_id,'pull'),
                    self.Routing(warehouse.pbm_loc_id,production_location_id,warehouse.manu_type_id,'pull'),
                ],
                'pbm_sam':[
                    self.Routing(warehouse.lot_stock_id,warehouse.pbm_loc_id,warehouse.pbm_type_id,'pull'),
                    self.Routing(warehouse.pbm_loc_id,production_location_id,warehouse.manu_type_id,'pull'),
                    self.Routing(warehouse.sam_loc_id,warehouse.lot_stock_id,warehouse.sam_type_id,'push'),
                ],
            })
            result[warehouse.id].update(warehouse._get_receive_rules_dict())
        returnresult

    @api.model
    def_get_production_location(self):
        location=self.env['stock.location'].search([('usage','=','production'),('company_id','=',self.company_id.id)],limit=1)
        ifnotlocation:
            raiseUserError(_('Can\'tfindanyproductionlocation.'))
        returnlocation

    def_get_routes_values(self):
        routes=super(StockWarehouse,self)._get_routes_values()
        routes.update({
            'pbm_route_id':{
                'routing_key':self.manufacture_steps,
                'depends':['manufacture_steps','manufacture_to_resupply'],
                'route_update_values':{
                    'name':self._format_routename(route_type=self.manufacture_steps),
                    'active':self.manufacture_steps!='mrp_one_step',
                },
                'route_create_values':{
                    'product_categ_selectable':True,
                    'warehouse_selectable':True,
                    'product_selectable':False,
                    'company_id':self.company_id.id,
                    'sequence':10,
                },
                'rules_values':{
                    'active':True,
                }
            }
        })
        routes.update(self._get_receive_routes_values('manufacture_to_resupply'))
        returnroutes

    def_get_route_name(self,route_type):
        names={
            'mrp_one_step':_('Manufacture(1step)'),
            'pbm':_('Pickcomponentsandthenmanufacture'),
            'pbm_sam':_('Pickcomponents,manufactureandthenstoreproducts(3steps)'),
        }
        ifroute_typeinnames:
            returnnames[route_type]
        else:
            returnsuper(StockWarehouse,self)._get_route_name(route_type)

    def_get_global_route_rules_values(self):
        rules=super(StockWarehouse,self)._get_global_route_rules_values()
        location_src=self.manufacture_steps=='mrp_one_step'andself.lot_stock_idorself.pbm_loc_id
        production_location=self._get_production_location()
        location_id=self.manufacture_steps=='pbm_sam'andself.sam_loc_idorself.lot_stock_id
        rules.update({
            'manufacture_pull_id':{
                'depends':['manufacture_steps','manufacture_to_resupply'],
                'create_values':{
                    'action':'manufacture',
                    'procure_method':'make_to_order',
                    'company_id':self.company_id.id,
                    'picking_type_id':self.manu_type_id.id,
                    'route_id':self._find_global_route('mrp.route_warehouse0_manufacture',_('Manufacture')).id
                },
                'update_values':{
                    'active':self.manufacture_to_resupply,
                    'name':self._format_rulename(location_id,False,'Production'),
                    'location_id':location_id.id,
                    'propagate_cancel':self.manufacture_steps=='pbm_sam'
                },
            },
            'manufacture_mto_pull_id':{
                'depends':['manufacture_steps','manufacture_to_resupply'],
                'create_values':{
                    'procure_method':'mts_else_mto',
                    'company_id':self.company_id.id,
                    'action':'pull',
                    'auto':'manual',
                    'route_id':self._find_global_route('stock.route_warehouse0_mto',_('MakeToOrder')).id,
                    'location_id':production_location.id,
                    'location_src_id':location_src.id,
                    'picking_type_id':self.manu_type_id.id
                },
                'update_values':{
                    'name':self._format_rulename(location_src,production_location,'MTO'),
                    'active':self.manufacture_to_resupply,
                },
            },
            'pbm_mto_pull_id':{
                'depends':['manufacture_steps','manufacture_to_resupply'],
                'create_values':{
                    'procure_method':'make_to_order',
                    'company_id':self.company_id.id,
                    'action':'pull',
                    'auto':'manual',
                    'route_id':self._find_global_route('stock.route_warehouse0_mto',_('MakeToOrder')).id,
                    'name':self._format_rulename(self.lot_stock_id,self.pbm_loc_id,'MTO'),
                    'location_id':self.pbm_loc_id.id,
                    'location_src_id':self.lot_stock_id.id,
                    'picking_type_id':self.pbm_type_id.id
                },
                'update_values':{
                    'active':self.manufacture_steps!='mrp_one_step'andself.manufacture_to_resupply,
                }
            },
            #Thepurposetomovesamruleinthemanufacturerouteinsteadof
            #pbm_route_idistoavoidconflictwithreceiptinmultiple
            #step.Forexampleiftheproductismanufactureandreceiptintwo
            #stepitwouldconflictinWH/Stocksinceproductcouldcomefrom
            #WH/post-prodorWH/input.Wedonothavethisconflictwith
            #manufactureroutesinceitissetontheproduct.
            'sam_rule_id':{
                'depends':['manufacture_steps','manufacture_to_resupply'],
                'create_values':{
                    'procure_method':'make_to_order',
                    'company_id':self.company_id.id,
                    'action':'pull',
                    'auto':'manual',
                    'route_id':self._find_global_route('mrp.route_warehouse0_manufacture',_('Manufacture')).id,
                    'name':self._format_rulename(self.sam_loc_id,self.lot_stock_id,False),
                    'location_id':self.lot_stock_id.id,
                    'location_src_id':self.sam_loc_id.id,
                    'picking_type_id':self.sam_type_id.id
                },
                'update_values':{
                    'active':self.manufacture_steps=='pbm_sam'andself.manufacture_to_resupply,
                }
            }

        })
        returnrules

    def_get_locations_values(self,vals,code=False):
        values=super(StockWarehouse,self)._get_locations_values(vals,code=code)
        def_values=self.default_get(['manufacture_steps'])
        manufacture_steps=vals.get('manufacture_steps',def_values['manufacture_steps'])
        code=vals.get('code')orcodeor''
        code=code.replace('','').upper()
        company_id=vals.get('company_id',self.company_id.id)
        values.update({
            'pbm_loc_id':{
                'name':_('Pre-Production'),
                'active':manufacture_stepsin('pbm','pbm_sam'),
                'usage':'internal',
                'barcode':self._valid_barcode(code+'-PREPRODUCTION',company_id)
            },
            'sam_loc_id':{
                'name':_('Post-Production'),
                'active':manufacture_steps=='pbm_sam',
                'usage':'internal',
                'barcode':self._valid_barcode(code+'-POSTPRODUCTION',company_id)
            },
        })
        returnvalues

    def_get_sequence_values(self):
        values=super(StockWarehouse,self)._get_sequence_values()
        values.update({
            'pbm_type_id':{'name':self.name+''+_('Sequencepickingbeforemanufacturing'),'prefix':self.code+'/PC/','padding':5,'company_id':self.company_id.id},
            'sam_type_id':{'name':self.name+''+_('Sequencestockaftermanufacturing'),'prefix':self.code+'/SFP/','padding':5,'company_id':self.company_id.id},
            'manu_type_id':{'name':self.name+''+_('Sequenceproduction'),'prefix':self.code+'/MO/','padding':5,'company_id':self.company_id.id},
        })
        returnvalues

    def_get_picking_type_create_values(self,max_sequence):
        data,next_sequence=super(StockWarehouse,self)._get_picking_type_create_values(max_sequence)
        data.update({
            'pbm_type_id':{
                'name':_('PickComponents'),
                'code':'internal',
                'use_create_lots':True,
                'use_existing_lots':True,
                'default_location_src_id':self.lot_stock_id.id,
                'default_location_dest_id':self.pbm_loc_id.id,
                'sequence':next_sequence+1,
                'sequence_code':'PC',
                'company_id':self.company_id.id,
            },
            'sam_type_id':{
                'name':_('StoreFinishedProduct'),
                'code':'internal',
                'use_create_lots':True,
                'use_existing_lots':True,
                'default_location_src_id':self.sam_loc_id.id,
                'default_location_dest_id':self.lot_stock_id.id,
                'sequence':next_sequence+3,
                'sequence_code':'SFP',
                'company_id':self.company_id.id,
            },
            'manu_type_id':{
                'name':_('Manufacturing'),
                'code':'mrp_operation',
                'use_create_lots':True,
                'use_existing_lots':True,
                'sequence':next_sequence+2,
                'sequence_code':'MO',
                'company_id':self.company_id.id,
            },
        })
        returndata,max_sequence+4

    def_get_picking_type_update_values(self):
        data=super(StockWarehouse,self)._get_picking_type_update_values()
        data.update({
            'pbm_type_id':{
                'active':self.manufacture_to_resupplyandself.manufacture_stepsin('pbm','pbm_sam')andself.active,
                'barcode':self.code.replace("","").upper()+"-PC",
            },
            'sam_type_id':{
                'active':self.manufacture_to_resupplyandself.manufacture_steps=='pbm_sam'andself.active,
                'barcode':self.code.replace("","").upper()+"-SFP",
            },
            'manu_type_id':{
                'active':self.manufacture_to_resupplyandself.active,
                'default_location_src_id':self.manufacture_stepsin('pbm','pbm_sam')andself.pbm_loc_id.idorself.lot_stock_id.id,
                'default_location_dest_id':self.manufacture_steps=='pbm_sam'andself.sam_loc_id.idorself.lot_stock_id.id,
            },
        })
        returndata

    def_create_missing_locations(self,vals):
        super()._create_missing_locations(vals)
        forcompany_idinself.company_id:
            location=self.env['stock.location'].search([('usage','=','production'),('company_id','=',company_id.id)],limit=1)
            ifnotlocation:
                company_id._create_production_location()

    defwrite(self,vals):
        ifany(fieldinvalsforfieldin('manufacture_steps','manufacture_to_resupply')):
            forwarehouseinself:
                warehouse._update_location_manufacture(vals.get('manufacture_steps',warehouse.manufacture_steps))
        returnsuper(StockWarehouse,self).write(vals)

    def_get_all_routes(self):
        routes=super(StockWarehouse,self)._get_all_routes()
        routes|=self.filtered(lambdaself:self.manufacture_to_resupplyandself.manufacture_pull_idandself.manufacture_pull_id.route_id).mapped('manufacture_pull_id').mapped('route_id')
        returnroutes

    def_update_location_manufacture(self,new_manufacture_step):
        self.mapped('pbm_loc_id').write({'active':new_manufacture_step!='mrp_one_step'})
        self.mapped('sam_loc_id').write({'active':new_manufacture_step=='pbm_sam'})

    def_update_name_and_code(self,name=False,code=False):
        res=super(StockWarehouse,self)._update_name_and_code(name,code)
        #changethemanufacturestockrulename
        forwarehouseinself:
            ifwarehouse.manufacture_pull_idandname:
                warehouse.manufacture_pull_id.write({'name':warehouse.manufacture_pull_id.name.replace(warehouse.name,name,1)})
        returnres

classOrderpoint(models.Model):
    _inherit="stock.warehouse.orderpoint"

    @api.constrains('product_id')
    defcheck_product_is_not_kit(self):
        ifself.env['mrp.bom'].search(['|',('product_id','in',self.product_id.ids),
                                            '&',('product_id','=',False),('product_tmpl_id','in',self.product_id.product_tmpl_id.ids),
                                       ('type','=','phantom')],count=True):
            raiseValidationError(_("Aproductwithakit-typebillofmaterialscannothaveareorderingrule."))
