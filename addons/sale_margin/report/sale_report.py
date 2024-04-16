#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSaleReport(models.Model):
    _inherit='sale.report'

    margin=fields.Float('Margin')

    def_select_additional_fields(self,fields):
        fields['margin']=",SUM(l.margin/CASECOALESCE(s.currency_rate,0)WHEN0THEN1.0ELSEs.currency_rateEND)ASmargin"
        returnsuper()._select_additional_fields(fields)
