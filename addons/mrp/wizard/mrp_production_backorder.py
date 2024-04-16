#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMrpProductionBackorderLine(models.TransientModel):
    _name='mrp.production.backorder.line'
    _description="BackorderConfirmationLine"

    mrp_production_backorder_id=fields.Many2one('mrp.production.backorder','MOBackorder',required=True,ondelete="cascade")
    mrp_production_id=fields.Many2one('mrp.production','ManufacturingOrder',required=True,ondelete="cascade",readonly=True)
    to_backorder=fields.Boolean('ToBackorder')


classMrpProductionBackorder(models.TransientModel):
    _name='mrp.production.backorder'
    _description="Wizardtomarkasdoneorcreatebackorder"

    mrp_production_ids=fields.Many2many('mrp.production')

    mrp_production_backorder_line_ids=fields.One2many(
        'mrp.production.backorder.line',
        'mrp_production_backorder_id',
        string="BackorderConfirmationLines")
    show_backorder_lines=fields.Boolean("Showbackorderlines",compute="_compute_show_backorder_lines")

    @api.depends('mrp_production_backorder_line_ids')
    def_compute_show_backorder_lines(self):
        forwizardinself:
            wizard.show_backorder_lines=len(wizard.mrp_production_backorder_line_ids)>1

    defaction_close_mo(self):
        returnself.mrp_production_ids.with_context(skip_backorder=True).button_mark_done()

    defaction_backorder(self):
        ctx=dict(self.env.context)
        ctx.pop('default_mrp_production_ids',None)
        mo_ids_to_backorder=self.mrp_production_backorder_line_ids.filtered(lambdal:l.to_backorder).mrp_production_id.ids
        returnself.mrp_production_ids.with_context(ctx,skip_backorder=True,mo_ids_to_backorder=mo_ids_to_backorder).button_mark_done()
