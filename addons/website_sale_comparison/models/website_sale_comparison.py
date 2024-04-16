#-*-coding:utf-8-*-

fromcollectionsimportOrderedDict

fromflectraimportfields,models


classProductAttributeCategory(models.Model):
    _name="product.attribute.category"
    _description="ProductAttributeCategory"
    _order='sequence,id'

    name=fields.Char("CategoryName",required=True,translate=True)
    sequence=fields.Integer("Sequence",default=10,index=True)

    attribute_ids=fields.One2many('product.attribute','category_id',string="RelatedAttributes",domain="[('category_id','=',False)]")


classProductAttribute(models.Model):
    _inherit='product.attribute'
    _order='category_id,sequence,id'

    category_id=fields.Many2one('product.attribute.category',string="Category",index=True,
                                  help="Setacategorytoregroupsimilarattributesunder"
                                  "thesamesectionintheComparisonpageofeCommerce")


classProductTemplateAttributeLine(models.Model):
    _inherit='product.template.attribute.line'

    def_prepare_categories_for_display(self):
        """Ontheproductpagegrouptogethertheattributelinesthatconcern
        attributesthatareinthesamecategory.

        Thereturnedcategoriesareorderedfollowingtheirdefaultorder.

        :return:OrderedDict[{
            product.attribute.category:[product.template.attribute.line]
        }]
        """
        attributes=self.attribute_id
        categories=OrderedDict([(cat,self.env['product.template.attribute.line'])forcatinattributes.category_id.sorted()])
        ifany(notpa.category_idforpainattributes):
            #category_idisnotrequiredandthemappeddoesnotreturnempty
            categories[self.env['product.attribute.category']]=self.env['product.template.attribute.line']
        forptalinself:
            categories[ptal.attribute_id.category_id]|=ptal
        returncategories


classProductProduct(models.Model):
    _inherit='product.product'

    def_prepare_categories_for_display(self):
        """Onthecomparisonpagegrouponthesamelinethevaluesofeach
        productthatconcernthesameattributes,andthengroupthose
        attributespercategory.

        Thereturnedcategoriesareorderedfollowingtheirdefaultorder.

        :return:OrderedDict[{
            product.attribute.category:OrderedDict[{
                product.attribute:OrderedDict[{
                    product:[product.template.attribute.value]
                }]
            }]
        }]
        """
        attributes=self.product_tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes().attribute_id.sorted()
        categories=OrderedDict([(cat,OrderedDict())forcatinattributes.category_id.sorted()])
        ifany(notpa.category_idforpainattributes):
            #category_idisnotrequiredandthemappeddoesnotreturnempty
            categories[self.env['product.attribute.category']]=OrderedDict()
        forpainattributes:
            categories[pa.category_id][pa]=OrderedDict([(
                product,
                product.product_template_attribute_value_ids.filtered(lambdaptav:ptav.attribute_id==pa)
            )forproductinself])

        returncategories
