#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson
fromflectraimporthttp
fromflectra.httpimportrequest

fromflectra.addons.sale_product_configurator.controllers.mainimportProductConfiguratorController
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale

classWebsiteSaleProductConfiguratorController(ProductConfiguratorController):
    @http.route(['/sale_product_configurator/show_optional_products_website'],type='json',auth="public",methods=['POST'],website=True)
    defshow_optional_products_website(self,product_id,variant_values,**kw):
        """Specialroutetousewebsitelogicinget_combination_infooverride.
        ThisrouteiscalledinJSbyappending_websitetothebaseroute.
        """
        kw.pop('pricelist_id')
        returnself.show_optional_products(product_id,variant_values,request.website.get_current_pricelist(),**kw)

    @http.route(['/sale_product_configurator/optional_product_items_website'],type='json',auth="public",methods=['POST'],website=True)
    defoptional_product_items_website(self,product_id,**kw):
        """Specialroutetousewebsitelogicinget_combination_infooverride.
        ThisrouteiscalledinJSbyappending_websitetothebaseroute.
        """
        kw.pop('pricelist_id')
        returnself.optional_product_items(product_id,request.website.get_current_pricelist(),**kw)

classWebsiteSale(WebsiteSale):
    def_prepare_product_values(self,product,category,search,**kwargs):
        values=super(WebsiteSale,self)._prepare_product_values(product,category,search,**kwargs)

        values['optional_product_ids']=[p.with_context(active_id=p.id)forpinproduct.optional_product_ids]
        returnvalues

    @http.route(['/shop/cart/update_option'],type='http',auth="public",methods=['POST'],website=True,multilang=False)
    defcart_options_update_json(self,product_and_options,goto_shop=None,lang=None,**kwargs):
        """Thisrouteiscalledwhensubmittingtheoptionalproductmodal.
            Theproductwithoutparentisthemainproduct,theotherareoptions.
            OptionsneedtobelinkedtotheirparentswithauniqueID.
            Themainproductisthefirstproductinthelistandtheoptions
            needtoberightaftertheirparent.
            product_and_options{
                'product_id',
                'product_template_id',
                'quantity',
                'parent_unique_id',
                'unique_id',
                'product_custom_attribute_values',
                'no_variant_attribute_values'
            }
        """
        iflang:
            request.website=request.website.with_context(lang=lang)

        order=request.website.sale_get_order(force_create=True)
        iforder.state!='draft':
            request.session['sale_order_id']=None
            order=request.website.sale_get_order(force_create=True)

        product_and_options=json.loads(product_and_options)
        ifproduct_and_options:
            #Themainproductisthefirst,optionalproductsaretherest
            main_product=product_and_options[0]
            value=order._cart_update(
                product_id=main_product['product_id'],
                add_qty=main_product['quantity'],
                product_custom_attribute_values=main_product['product_custom_attribute_values'],
                no_variant_attribute_values=main_product['no_variant_attribute_values'],
            )

            #Linkoptionwithitsparent.
            option_parent={main_product['unique_id']:value['line_id']}
            foroptioninproduct_and_options[1:]:
                parent_unique_id=option['parent_unique_id']
                option_value=order._cart_update(
                    product_id=option['product_id'],
                    set_qty=option['quantity'],
                    linked_line_id=option_parent[parent_unique_id],
                    product_custom_attribute_values=option['product_custom_attribute_values'],
                    no_variant_attribute_values=option['no_variant_attribute_values'],
                )
                option_parent[option['unique_id']]=option_value['line_id']

        returnstr(order.cart_quantity)
