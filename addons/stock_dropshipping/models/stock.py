#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classStockRule(models.Model):
    _inherit='stock.rule'

    @api.model
    def_get_procurements_to_merge_groupby(self,procurement):
        """Donotgrouppurchaseorderlineiftheyarelinkedtodifferent
        saleorderline.Thepurposeistocomputethedeliveredquantities.
        """
        returnprocurement.values.get('sale_line_id'),super(StockRule,self)._get_procurements_to_merge_groupby(procurement)

    @api.model
    def_get_procurements_to_merge_sorted(self,procurement):
        returnprocurement.values.get('sale_line_id'),super(StockRule,self)._get_procurements_to_merge_sorted(procurement)


classProcurementGroup(models.Model):
    _inherit="procurement.group"

    @api.model
    def_get_rule_domain(self,location,values):
        if'sale_line_id'invaluesandvalues.get('company_id'):
            return[('location_id','=',location.id),('action','!=','push'),('company_id','=',values['company_id'].id)]
        else:
            returnsuper(ProcurementGroup,self)._get_rule_domain(location,values)
