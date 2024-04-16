#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classReportStockRule(models.AbstractModel):
    _inherit='report.stock.report_stock_rule'

    @api.model
    def_get_rule_loc(self,rule,product_id):
        """Weoverridethismethodtohandlebuyruleswhichdonothavealocation_src_id.
        """
        res=super(ReportStockRule,self)._get_rule_loc(rule,product_id)
        ifrule.action=='buy':
            res['source']=self.env.ref('stock.stock_location_suppliers')
        returnres
