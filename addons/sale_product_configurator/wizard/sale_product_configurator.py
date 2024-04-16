#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classSaleProductConfigurator(models.TransientModel):
    _name='sale.product.configurator'
    _description='SaleProductConfigurator'

    product_template_id=fields.Many2one(
        'product.template',string="Product",
        required=True,domain=[('sale_ok','=',True),('attribute_line_ids.value_ids','!=',False)])
    quantity=fields.Integer('Quantity')
    pricelist_id=fields.Many2one('product.pricelist','Pricelist',readonly=True)
    product_template_attribute_value_ids=fields.Many2many(
        'product.template.attribute.value','product_configurator_template_attribute_value_rel',string='AttributeValues',readonly=True)
    product_custom_attribute_value_ids=fields.Many2many(
        'product.attribute.custom.value','product_configurator_custom_attribute_value_rel',string="CustomValues")
    product_no_variant_attribute_value_ids=fields.Many2many(
        'product.template.attribute.value','product_configurator_no_variant_attribute_value_rel',string="ExtraValues")
