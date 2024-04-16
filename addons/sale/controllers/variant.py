#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classVariantController(http.Controller):
    @http.route(['/sale/get_combination_info'],type='json',auth="user",methods=['POST'])
    defget_combination_info(self,product_template_id,product_id,combination,add_qty,pricelist_id,**kw):
        combination=request.env['product.template.attribute.value'].browse(combination)
        pricelist=self._get_pricelist(pricelist_id)
        ProductTemplate=request.env['product.template']
        if'context'inkw:
            ProductTemplate=ProductTemplate.with_context(**kw.get('context'))
        product_template=ProductTemplate.browse(int(product_template_id))
        res=product_template._get_combination_info(combination,int(product_idor0),int(add_qtyor1),pricelist)
        if'parent_combination'inkw:
            parent_combination=request.env['product.template.attribute.value'].browse(kw.get('parent_combination'))
            ifnotcombination.exists()andproduct_id:
                product=request.env['product.product'].browse(int(product_id))
                ifproduct.exists():
                    combination=product.product_template_attribute_value_ids
            res.update({
                'is_combination_possible':product_template._is_combination_possible(combination=combination,parent_combination=parent_combination),
            })
        returnres

    @http.route(['/sale/create_product_variant'],type='json',auth="user",methods=['POST'])
    defcreate_product_variant(self,product_template_id,product_template_attribute_value_ids,**kwargs):
        returnrequest.env['product.template'].browse(int(product_template_id)).create_product_variant(product_template_attribute_value_ids)

    def_get_pricelist(self,pricelist_id,pricelist_fallback=False):
        returnrequest.env['product.pricelist'].browse(int(pricelist_idor0))
