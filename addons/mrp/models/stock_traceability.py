fromflectraimportmodels,api

classMrpStockReport(models.TransientModel):
    _inherit='stock.traceability.report'

    @api.model
    def_get_reference(self,move_line):
        res_model,res_id,ref=super(MrpStockReport,self)._get_reference(move_line)
        ifmove_line.move_id.production_idandnotmove_line.move_id.scrapped:
            res_model='mrp.production'
            res_id=move_line.move_id.production_id.id
            ref=move_line.move_id.production_id.name
        ifmove_line.move_id.raw_material_production_idandnotmove_line.move_id.scrapped:
            res_model='mrp.production'
            res_id=move_line.move_id.raw_material_production_id.id
            ref=move_line.move_id.raw_material_production_id.name
        ifmove_line.move_id.unbuild_id:
            res_model='mrp.unbuild'
            res_id=move_line.move_id.unbuild_id.id
            ref=move_line.move_id.unbuild_id.name
        ifmove_line.move_id.consume_unbuild_id:
            res_model='mrp.unbuild'
            res_id=move_line.move_id.consume_unbuild_id.id
            ref=move_line.move_id.consume_unbuild_id.name
        returnres_model,res_id,ref

    @api.model
    def_get_linked_move_lines(self,move_line):
        move_lines,is_used=super(MrpStockReport,self)._get_linked_move_lines(move_line)
        ifnotmove_lines:
            move_lines=(move_line.move_id.consume_unbuild_idandmove_line.produce_line_ids)or(move_line.move_id.production_idandmove_line.consume_line_ids)
        ifnotis_used:
            is_used=(move_line.move_id.unbuild_idandmove_line.consume_line_ids)or(move_line.move_id.raw_material_production_idandmove_line.produce_line_ids)
        returnmove_lines,is_used
