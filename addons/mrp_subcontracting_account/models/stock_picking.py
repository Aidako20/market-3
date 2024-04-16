#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.osv.expressionimportOR


classStockPicking(models.Model):
    _inherit='stock.picking'

    defaction_view_stock_valuation_layers(self):
        action=super(StockPicking,self).action_view_stock_valuation_layers()
        subcontracted_productions=self._get_subcontracted_productions()
        ifnotsubcontracted_productions:
            returnaction
        domain=action['domain']
        domain_subcontracting=[('id','in',(subcontracted_productions.move_raw_ids|subcontracted_productions.move_finished_ids).stock_valuation_layer_ids.ids)]
        domain=OR([domain,domain_subcontracting])
        returndict(action,domain=domain)
