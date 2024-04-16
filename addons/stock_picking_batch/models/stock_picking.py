#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockPicking(models.Model):
    _inherit="stock.picking"

    batch_id=fields.Many2one(
        'stock.picking.batch',string='BatchTransfer',
        check_company=True,
        states={'done':[('readonly',True)],'cancel':[('readonly',True)]},
        help='Batchassociatedtothistransfer',copy=False)

    @api.model
    defcreate(self,vals):
        res=super().create(vals)
        ifvals.get('batch_id'):
            res.batch_id._sanity_check()
        returnres

    defwrite(self,vals):
        res=super().write(vals)
        ifvals.get('batch_id'):
            ifnotself.batch_id.picking_type_id:
                self.batch_id.picking_type_id=self.picking_type_id[0]
            self.batch_id._sanity_check()
        returnres

    def_should_show_transfers(self):
        iflen(self.batch_id)==1andself==self.batch_id.picking_ids:
            returnFalse
        returnsuper()._should_show_transfers()
