#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.tools.miscimportformat_datetime


classStockQuantityHistory(models.TransientModel):
    _inherit='stock.quantity.history'

    defopen_at_date(self):
        active_model=self.env.context.get('active_model')
        ifactive_model=='stock.valuation.layer':
            action=self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
            action['domain']=[('create_date','<=',self.inventory_datetime),('product_id.type','=','product')]
            action['display_name']=format_datetime(self.env,self.inventory_datetime)
            returnaction

        returnsuper(StockQuantityHistory,self).open_at_date()
