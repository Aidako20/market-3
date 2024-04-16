#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models


classSaleReport(models.Model):
    _inherit='sale.report'

    website_id=fields.Many2one('website',readonly=True)

    def_group_by_sale(self,groupby=''):
        res=super()._group_by_sale(groupby)
        res+=""",s.website_id"""
        returnres

    def_select_additional_fields(self,fields):
        fields['website_id']=",s.website_idaswebsite_id"
        returnsuper()._select_additional_fields(fields)
