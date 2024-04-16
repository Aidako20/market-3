#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classStockMoveLine(models.Model):
    _inherit='stock.move.line'

    def_should_bypass_reservation(self,location):
        """Ifthemovelineissubcontractedthenignorethereservation."""
        should_bypass_reservation=super(StockMoveLine,self)._should_bypass_reservation(location)
        ifnotshould_bypass_reservationandself.move_id.is_subcontract:
            returnTrue
        returnshould_bypass_reservation
