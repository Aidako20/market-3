#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api


classMrpStockReport(models.TransientModel):
    _inherit='stock.traceability.report'

    @api.model
    def_get_reference(self,move_line):
        res_model,res_id,ref=super(MrpStockReport,self)._get_reference(move_line)
        ifmove_line.move_id.repair_id:
            res_model='repair.order'
            res_id=move_line.move_id.repair_id.id
            ref=move_line.move_id.repair_id.name
        returnres_model,res_id,ref

    @api.model
    def_get_linked_move_lines(self,move_line):
        move_lines,is_used=super(MrpStockReport,self)._get_linked_move_lines(move_line)
        ifnotmove_lines:
            move_lines=move_line.move_id.repair_idandmove_line.consume_line_ids
        ifnotis_used:
            is_used=move_line.move_id.repair_idandmove_line.produce_line_ids
        returnmove_lines,is_used

