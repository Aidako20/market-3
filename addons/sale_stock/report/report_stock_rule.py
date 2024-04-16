#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classReportStockRule(models.AbstractModel):
    _inherit='report.stock.report_stock_rule'

    @api.model
    def_get_routes(self,data):
        res=super(ReportStockRule,self)._get_routes(data)
        ifdata.get('so_route_ids'):
            res=self.env['stock.location.route'].browse(data['so_route_ids'])|res
        returnres
