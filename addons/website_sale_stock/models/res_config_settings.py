#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    inventory_availability=fields.Selection([
        ('never','Sellregardlessofinventory'),
        ('always','Showinventoryonwebsiteandpreventsalesifnotenoughstock'),
        ('threshold','Showinventorywhenbelowthethresholdandpreventsalesifnotenoughstock'),
        ('custom','Showproduct-specificnotifications'),
    ],string='InventoryAvailability',default='never')
    available_threshold=fields.Float(string='AvailabilityThreshold')
    website_warehouse_id=fields.Many2one('stock.warehouse',related='website_id.warehouse_id',domain="[('company_id','=',website_company_id)]",readonly=False)

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        IrDefault=self.env['ir.default'].sudo()
        IrDefault.set('product.template','inventory_availability',self.inventory_availability)
        IrDefault.set('product.template','available_threshold',self.available_thresholdifself.inventory_availability=='threshold'elseNone)

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        IrDefault=self.env['ir.default'].sudo()
        res.update(inventory_availability=IrDefault.get('product.template','inventory_availability')or'never',
                   available_threshold=IrDefault.get('product.template','available_threshold')or5.0)
        returnres

    @api.onchange('website_company_id')
    def_onchange_website_company_id(self):
        ifself.website_warehouse_id.company_id!=self.website_company_id:
            return{'value':{'website_warehouse_id':False}}
