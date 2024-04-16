#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classMrpConsumptionWarning(models.TransientModel):
    _name='mrp.consumption.warning'
    _description="Wizardincaseofconsumptioninwarning/strictandmorecomponenthasbeenusedforaMO(relatedtothebom)"

    mrp_production_ids=fields.Many2many('mrp.production')
    mrp_production_count=fields.Integer(compute="_compute_mrp_production_count")

    consumption=fields.Selection([
        ('flexible','Allowed'),
        ('warning','Allowedwithwarning'),
        ('strict','Blocked')],compute="_compute_consumption")
    mrp_consumption_warning_line_ids=fields.One2many('mrp.consumption.warning.line','mrp_consumption_warning_id')

    @api.depends("mrp_production_ids")
    def_compute_mrp_production_count(self):
        forwizardinself:
            wizard.mrp_production_count=len(wizard.mrp_production_ids)

    @api.depends("mrp_consumption_warning_line_ids.consumption")
    def_compute_consumption(self):
        forwizardinself:
            consumption_map=set(wizard.mrp_consumption_warning_line_ids.mapped("consumption"))
            wizard.consumption="strict"inconsumption_mapand"strict"or"warning"inconsumption_mapand"warning"or"flexible"

    defaction_confirm(self):
        ctx=dict(self.env.context)
        ctx.pop('default_mrp_production_ids',None)
        action_from_do_finish=False
        ifself.env.context.get('from_workorder'):
            ifself.env.context.get('active_model')=='mrp.workorder':
                action_from_do_finish=self.env['mrp.workorder'].browse(self.env.context.get('active_id')).do_finish()
        action_from_mark_done=self.mrp_production_ids.with_context(ctx,skip_consumption=True).button_mark_done()
        returnaction_from_do_finishoraction_from_mark_done

    defaction_cancel(self):
        ifself.env.context.get('from_workorder')andlen(self.mrp_production_ids)==1:
            return{
                'type':'ir.actions.act_window',
                'res_model':'mrp.production',
                'views':[[self.env.ref('mrp.mrp_production_form_view').id,'form']],
                'res_id':self.mrp_production_ids.id,
                'target':'main',
            }

classMrpConsumptionWarningLine(models.TransientModel):
    _name='mrp.consumption.warning.line'
    _description="Lineofissueconsumption"

    mrp_consumption_warning_id=fields.Many2one('mrp.consumption.warning',"ParentWizard",readonly=True,required=True,ondelete="cascade")
    mrp_production_id=fields.Many2one('mrp.production',"ManufacturingOrder",readonly=True,required=True,ondelete="cascade")
    consumption=fields.Selection(related="mrp_production_id.consumption")

    product_id=fields.Many2one('product.product',"Product",readonly=True,required=True)
    product_uom_id=fields.Many2one('uom.uom',"UnitofMeasure",related="product_id.uom_id",readonly=True)
    product_consumed_qty_uom=fields.Float("Consumed",readonly=True)
    product_expected_qty_uom=fields.Float("ToConsume",readonly=True)
