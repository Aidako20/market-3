#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

classStockWarnInsufficientQtyRepair(models.TransientModel):
    _name='stock.warn.insufficient.qty.repair'
    _inherit='stock.warn.insufficient.qty'
    _description='WarnInsufficientRepairQuantity'

    repair_id=fields.Many2one('repair.order',string='Repair')

    def_get_reference_document_company_id(self):
        returnself.repair_id.company_id

    defaction_done(self):
        self.ensure_one()
        returnself.repair_id.action_repair_confirm()
