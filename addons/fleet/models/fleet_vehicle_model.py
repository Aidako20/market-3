#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classFleetVehicleModel(models.Model):
    _name='fleet.vehicle.model'
    _description='Modelofavehicle'
    _order='nameasc'

    name=fields.Char('Modelname',required=True)
    brand_id=fields.Many2one('fleet.vehicle.model.brand','Manufacturer',required=True,help='Manufacturerofthevehicle')
    vendors=fields.Many2many('res.partner','fleet_vehicle_model_vendors','model_id','partner_id',string='Vendors')
    manager_id=fields.Many2one('res.users','FleetManager',default=lambdaself:self.env.uid,
                                 domain=lambdaself:[('groups_id','in',self.env.ref('fleet.fleet_group_manager').id)])
    image_128=fields.Image(related='brand_id.image_128',readonly=True)
    active=fields.Boolean(default=True)
    vehicle_type=fields.Selection([('car','Car'),('bike','Bike')],default='car',required=True)

    @api.depends('name','brand_id')
    defname_get(self):
        res=[]
        forrecordinself:
            name=record.name
            ifrecord.brand_id.name:
                name=record.brand_id.name+'/'+name
            res.append((record.id,name))
        returnres

    defwrite(self,vals):
        if'manager_id'invals:
            old_manager=self.manager_id.idifself.manager_idelseNone

            self.env['fleet.vehicle'].search([('model_id','=',self.id),('manager_id','=',old_manager)]).write({'manager_id':vals['manager_id']})

        returnsuper(FleetVehicleModel,self).write(vals)


classFleetVehicleModelBrand(models.Model):
    _name='fleet.vehicle.model.brand'
    _description='Brandofthevehicle'
    _order='model_countdesc,nameasc'

    name=fields.Char('Make',required=True)
    image_128=fields.Image("Logo",max_width=128,max_height=128)
    model_count=fields.Integer(compute="_compute_model_count",string="",store=True)
    model_ids=fields.One2many('fleet.vehicle.model','brand_id')

    @api.depends('model_ids')
    def_compute_model_count(self):
        Model=self.env['fleet.vehicle.model']
        forrecordinself:
            record.model_count=Model.search_count([('brand_id','=',record.id)])

    defaction_brand_model(self):
        self.ensure_one()
        view={
            'type':'ir.actions.act_window',
            'view_mode':'tree,form',
            'res_model':'fleet.vehicle.model',
            'name':'Models',
            'context':{'search_default_brand_id':self.id,'default_brand_id':self.id}
        }

        returnview
