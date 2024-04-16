#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_

classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        rslt=super()._load(sale_tax_rate,purchase_tax_rate,company)

        ifcompany.account_tax_fiscal_country_idinself.env.ref('base.europe').country_ids:
            company._map_eu_taxes()

        returnrslt
