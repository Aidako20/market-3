#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.addons.website_sale.controllers.variantimportWebsiteSaleVariantController


classWebsiteSaleStockVariantController(WebsiteSaleVariantController):
    @http.route()
    defget_combination_info_website(self,product_template_id,product_id,combination,add_qty,**kw):
        kw['context']=kw.get('context',{})
        kw['context'].update(website_sale_stock_get_quantity=True)
        returnsuper(WebsiteSaleStockVariantController,self).get_combination_info_website(product_template_id,product_id,combination,add_qty,**kw)
