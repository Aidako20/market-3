#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classProductTemplate(models.Model):
    _inherit='product.template'
    _check_company_auto=True

    optional_product_ids=fields.Many2many(
        'product.template','product_optional_rel','src_id','dest_id',
        string='OptionalProducts',help="OptionalProductsaresuggested"
        "wheneverthecustomerhits*AddtoCart*(cross-sellstrategy,"
        "e.g.forcomputers:warranty,software,etc.).",check_company=True)

    @api.depends('attribute_line_ids.value_ids.is_custom','attribute_line_ids.attribute_id.create_variant')
    def_compute_has_configurable_attributes(self):
        """Aproductisconsideredconfigurableif:
        -Ithasdynamicattributes
        -Ithasanyattributelinewithatleast2attributevaluesconfigured
        -Ithasatleastonecustomattributevalue"""
        forproductinself:
            product.has_configurable_attributes=any(attribute.create_variant=='dynamic'forattributeinproduct.mapped('attribute_line_ids.attribute_id'))\
                orany(len(attribute_line_id.value_ids)>=2forattribute_line_idinproduct.attribute_line_ids)\
                orany(attribute_value.is_customforattribute_valueinproduct.mapped('attribute_line_ids.value_ids'))

    defget_single_product_variant(self):
        """Methodusedbytheproductconfiguratortocheckiftheproductisconfigurableornot.

        Weneedtoopentheproductconfiguratoriftheproduct:
        -isconfigurable(seehas_configurable_attributes)
        -hasoptionalproducts"""
        self.ensure_one()
        res=super(ProductTemplate,self).get_single_product_variant()
        ifres.get('product_id',False):
            has_optional_products=False
            foroptional_productinself.product_variant_id.optional_product_ids:
                ifoptional_product.has_dynamic_attributes()oroptional_product._get_possible_variants(self.product_variant_id.product_template_attribute_value_ids):
                    has_optional_products=True
                    break
            res.update({'has_optional_products':has_optional_products})
        returnres
