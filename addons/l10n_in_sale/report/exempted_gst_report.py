#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classL10nInExemptedReport(models.Model):
    _inherit="l10n_in.exempted.report"

    def_from(self):
        from_str=super(L10nInExemptedReport,self)._from()
        from_str+="""ANDaml.product_id!=COALESCE(
            (SELECTvaluefromir_config_parameterwherekey='sale.default_deposit_product_id'),'0')::int
            """
        returnfrom_str
