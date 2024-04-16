#-*-coding:utf-8-*-
fromflectraimporthttp
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.httpimportrequest


classWebsiteSale(WebsiteSale):

    @http.route(['/shop/pricelist'])
    defpricelist(self,promo,**post):
        order=request.website.sale_get_order()
        coupon_status=request.env['sale.coupon.apply.code'].sudo().apply_coupon(order,promo)
        ifcoupon_status.get('not_found'):
            returnsuper(WebsiteSale,self).pricelist(promo,**post)
        elifcoupon_status.get('error'):
            request.session['error_promo_code']=coupon_status['error']
        returnrequest.redirect(post.get('r','/shop/cart'))

    @http.route(['/shop/payment'],type='http',auth="public",website=True)
    defpayment(self,**post):
        order=request.website.sale_get_order()
        order.recompute_coupon_lines()
        returnsuper(WebsiteSale,self).payment(**post)

    @http.route(['/shop/cart'],type='http',auth="public",website=True)
    defcart(self,access_token=None,revive='',**post):
        order=request.website.sale_get_order()
        order.recompute_coupon_lines()
        returnsuper(WebsiteSale,self).cart(access_token=access_token,revive=revive,**post)

    #Override
    #Addintherenderingthefree_shipping_line
    def_get_shop_payment_values(self,order,**kwargs):
        values=super(WebsiteSale,self)._get_shop_payment_values(order,**kwargs)
        values['free_shipping_lines']=order._get_free_shipping_lines()
        returnvalues
