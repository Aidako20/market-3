#-*-coding:utf-8-*-
fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
importjson


classWebsiteSaleProductComparison(WebsiteSale):

    @http.route('/shop/compare/',type='http',auth="public",website=True,sitemap=False)
    defproduct_compare(self,**post):
        values={}
        product_ids=[int(i)foriinpost.get('products','').split(',')ifi.isdigit()]
        ifnotproduct_ids:
            returnrequest.redirect("/shop")
        #usesearchtocheckreadaccessoneachrecord/ids
        products=request.env['product.product'].search([('id','in',product_ids)])
        values['products']=products.with_context(display_default_code=False)
        returnrequest.render("website_sale_comparison.product_compare",values)

    @http.route(['/shop/get_product_data'],type='json',auth="public",website=True)
    defget_product_data(self,product_ids,cookies=None):
        ret={}
        pricelist_context,pricelist=self._get_pricelist_context()
        prods=request.env['product.product'].with_context(pricelist_context,display_default_code=False).search([('id','in',product_ids)])

        ifcookiesisnotNone:
            ret['cookies']=json.dumps(request.env['product.product'].search([('id','in',list(set(product_ids+cookies)))]).ids)

        prods.mapped('name')
        forprodinprods:
            ret[prod.id]={
                'render':request.env['ir.ui.view']._render_template(
                    "website_sale_comparison.product_product",
                    {'product':prod,'website':request.website}
                ),
                'product':dict(id=prod.id,name=prod.name,display_name=prod.display_name),
            }
        returnret
