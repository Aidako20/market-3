#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimporthttp
fromflectra.httpimportrequest

fromflectra.addons.sale.controllers.variantimportVariantController

classWebsiteSaleVariantController(VariantController):
    @http.route(['/sale/get_combination_info_website'],type='json',auth="public",methods=['POST'],website=True)
    defget_combination_info_website(self,product_template_id,product_id,combination,add_qty,**kw):
        """Specialroutetousewebsitelogicinget_combination_infooverride.
        ThisrouteiscalledinJSbyappending_websitetothebaseroute.
        """
        kw.pop('pricelist_id')
        res=self.get_combination_info(product_template_id,product_id,combination,add_qty,request.website.get_current_pricelist(),**kw)

        carousel_view=request.env['ir.ui.view']._render_template('website_sale.shop_product_carousel',
            values={
                'product':request.env['product.template'].browse(res['product_template_id']),
                'product_variant':request.env['product.product'].browse(res['product_id']),
            })
        res['carousel']=carousel_view
        returnres

    @http.route(auth="public")
    defcreate_product_variant(self,product_template_id,product_template_attribute_value_ids,**kwargs):
        """Overridebecauseonthewebsitethepublicusermustaccessit."""
        returnsuper(WebsiteSaleVariantController,self).create_product_variant(product_template_id,product_template_attribute_value_ids,**kwargs)
