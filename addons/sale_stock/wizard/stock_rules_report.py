#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockRulesReport(models.TransientModel):
    _inherit='stock.rules.report'

    so_route_ids=fields.Many2many('stock.location.route',string='Applyspecificroutes',
        domain="[('sale_selectable','=',True)]",help="ChoosetoapplySOlinesspecificroutes.")

    def_prepare_report_data(self):
        data=super(StockRulesReport,self)._prepare_report_data()
        data['so_route_ids']=self.so_route_ids.ids
        returndata
