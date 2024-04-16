#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit="res.company"
    _check_company_auto=True

    sale_order_template_id=fields.Many2one(
        "sale.order.template",string="DefaultSaleTemplate",
        domain="['|',('company_id','=',False),('company_id','=',id)]",
        check_company=True,
    )
