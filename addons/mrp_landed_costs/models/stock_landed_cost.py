#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classStockLandedCost(models.Model):
    _inherit='stock.landed.cost'

    target_model=fields.Selection(selection_add=[
        ('manufacturing',"ManufacturingOrders")
    ],ondelete={'manufacturing':'setdefault'})
    mrp_production_ids=fields.Many2many(
        'mrp.production',string='Manufacturingorder',
        copy=False,states={'done':[('readonly',True)]},groups='stock.group_stock_manager')
    allowed_mrp_production_ids=fields.Many2many(
        'mrp.production',compute='_compute_allowed_mrp_production_ids',groups='stock.group_stock_manager')

    @api.depends('company_id')
    def_compute_allowed_mrp_production_ids(self):
        forcostinself:
            moves=self.env['stock.move'].search([
                ('stock_valuation_layer_ids','!=',False),
                ('production_id','!=',False),
                ('company_id','=',cost.company_id.id)
            ])
            self.allowed_mrp_production_ids=moves.production_id

    @api.onchange('target_model')
    def_onchange_target_model(self):
        super()._onchange_target_model()
        ifself.target_model!='manufacturing':
            self.mrp_production_ids=False

    def_get_targeted_move_ids(self):
        returnsuper()._get_targeted_move_ids()|self.mrp_production_ids.move_finished_ids
