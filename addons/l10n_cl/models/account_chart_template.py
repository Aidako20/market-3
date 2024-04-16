#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.httpimportrequest


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        """SettaxcalculationroundingmethodrequiredinChileanlocalization"""
        res=super()._load(sale_tax_rate,purchase_tax_rate,company)
        ifcompany.country_id.code=='CL':
            company.write({'tax_calculation_rounding_method':'round_globally'})
        returnres
