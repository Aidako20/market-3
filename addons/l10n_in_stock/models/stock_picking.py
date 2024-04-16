#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classStockPicking(models.Model):
    _inherit='stock.picking'

    def_should_generate_commercial_invoice(self):
        super(StockPicking,self)._should_generate_commercial_invoice()
        returnTrue
