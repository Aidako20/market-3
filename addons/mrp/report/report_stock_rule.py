#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classReportStockRule(models.AbstractModel):
    _inherit='report.stock.report_stock_rule'

    @api.model
    def_get_rule_loc(self,rule,product_id):
        """Weoverridethismethodtohandlemanufacturerulewhichdonothavealocation_src_id.
        """
        res=super(ReportStockRule,self)._get_rule_loc(rule,product_id)
        ifrule.action=='manufacture':
            res['source']=product_id.property_stock_production
        returnres
