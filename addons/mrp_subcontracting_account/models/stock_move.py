#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classStockMove(models.Model):
    _inherit='stock.move'

    def_should_force_price_unit(self):
        self.ensure_one()
        returnself.is_subcontractorsuper()._should_force_price_unit()
