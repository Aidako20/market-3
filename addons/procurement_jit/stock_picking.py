#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classStockPicking(models.Model):
    _inherit='stock.picking'

    def_needs_automatic_assign(self):
        self.ensure_one()
        ifself.sale_id:
            returnTrue
        returnsuper()._needs_automatic_assign()
