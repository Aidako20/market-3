#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockWarnInsufficientQtyUnbuild(models.TransientModel):
    _name='stock.warn.insufficient.qty.unbuild'
    _inherit='stock.warn.insufficient.qty'
    _description='WarnInsufficientUnbuildQuantity'

    unbuild_id=fields.Many2one('mrp.unbuild','Unbuild')

    def_get_reference_document_company_id(self):
        returnself.unbuild_id.company_id

    defaction_done(self):
        self.ensure_one()
        returnself.unbuild_id.action_unbuild()
