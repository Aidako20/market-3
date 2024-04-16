#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classL10nInAccountInvoiceReport(models.Model):
    _inherit="l10n_in.account.invoice.report"

    def_from(self):
        from_str=super(L10nInAccountInvoiceReport,self)._from()
        returnfrom_str.replace(
            "LEFTJOINres_country_statepsONps.id=p.state_id",
            """
            LEFTJOINres_partnerdpONdp.id=am.partner_shipping_id
            LEFTJOINres_country_statepsONps.id=dp.state_id
            """
        )

    def_where(self):
        where_str=super(L10nInAccountInvoiceReport,self)._where()
        where_str+="""AND(aml.product_idISNULLoraml.product_id!=COALESCE(
            (SELECTvaluefromir_config_parameterwherekey='sale.default_deposit_product_id'),'0')::int)
            """
        returnwhere_str
