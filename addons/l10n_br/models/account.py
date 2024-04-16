#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAccountTaxTemplate(models.Model):
    """Addfieldsusedtodefinesomebraziliantaxes"""
    _inherit='account.tax.template'

    tax_discount=fields.Boolean(string='DiscountthisTaxinPrince',
                                    help="Markitfor(ICMS,PISeetc.).")
    base_reduction=fields.Float(string='Redution',digits=0,required=True,
                                    help="Umpercentualdecimalem%entre0-1.",default=0)
    amount_mva=fields.Float(string='MVAPercent',digits=0,required=True,
                                help="Umpercentualdecimalem%entre0-1.",default=0)


classAccountTax(models.Model):
    """Addfieldsusedtodefinesomebraziliantaxes"""
    _inherit='account.tax'

    tax_discount=fields.Boolean(string='DiscountthisTaxinPrince',
                                  help="Markitfor(ICMS,PISeetc.).")
    base_reduction=fields.Float(string='Redution',digits=0,required=True,
                                  help="Umpercentualdecimalem%entre0-1.",default=0)
    amount_mva=fields.Float(string='MVAPercent',digits=0,required=True,
                              help="Umpercentualdecimalem%entre0-1.",default=0)
