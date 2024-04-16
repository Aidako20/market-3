#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    manufacturing_lead=fields.Float(related='company_id.manufacturing_lead',string="ManufacturingLeadTime",readonly=False)
    use_manufacturing_lead=fields.Boolean(string="DefaultManufacturingLeadTime",config_parameter='mrp.use_manufacturing_lead')
    group_mrp_byproducts=fields.Boolean("By-Products",
        implied_group='mrp.group_mrp_byproducts')
    module_mrp_mps=fields.Boolean("MasterProductionSchedule")
    module_mrp_plm=fields.Boolean("ProductLifecycleManagement(PLM)")
    module_mrp_workorder=fields.Boolean("WorkOrders")
    module_quality_control=fields.Boolean("Quality")
    module_mrp_subcontracting=fields.Boolean("Subcontracting")
    group_mrp_routings=fields.Boolean("MRPWorkOrders",
        implied_group='mrp.group_mrp_routings')
    group_locked_by_default=fields.Boolean("LockQuantitiesToConsume",implied_group='mrp.group_locked_by_default')

    @api.onchange('use_manufacturing_lead')
    def_onchange_use_manufacturing_lead(self):
        ifnotself.use_manufacturing_lead:
            self.manufacturing_lead=0.0

    @api.onchange('group_mrp_routings')
    def_onchange_group_mrp_routings(self):
        #Ifweactivate'MRPWorkOrders',itmeansthatweneedtoinstall'mrp_workorder'.
        #Theoppositeisnotalwaystrue:othermodules(suchas'quality_mrp_workorder')may
        #dependon'mrp_workorder',soweshouldnotautomaticallyuninstallthemoduleif'MRP
        #WorkOrders'isdeactivated.
        #Longstoryshort:if'mrp_workorder'isalreadyinstalled,wedon'tuninstallitbasedon
        #group_mrp_routings
        ifself.group_mrp_routings:
            self.module_mrp_workorder=True
        elifnotself.env['ir.module.module'].search([('name','=','mrp_workorder'),('state','=','installed')]):
            self.module_mrp_workorder=False
