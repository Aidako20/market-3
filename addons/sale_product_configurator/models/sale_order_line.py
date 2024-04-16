#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    is_configurable_product=fields.Boolean('Istheproductconfigurable?',related="product_template_id.has_configurable_attributes")
    product_template_attribute_value_ids=fields.Many2many(related='product_id.product_template_attribute_value_ids',readonly=True)
