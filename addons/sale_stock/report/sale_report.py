#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSaleReport(models.Model):
    _inherit="sale.report"

    warehouse_id=fields.Many2one('stock.warehouse','Warehouse',readonly=True)

    def_group_by_sale(self,groupby=''):
        res=super()._group_by_sale(groupby)
        res+=""",s.warehouse_id"""
        returnres

    def_select_additional_fields(self,fields):
        fields['warehouse_id']=",s.warehouse_idaswarehouse_id"
        returnsuper()._select_additional_fields(fields)
