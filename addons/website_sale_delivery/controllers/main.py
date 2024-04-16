#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.exceptionsimportUserError,ValidationError


classWebsiteSaleDelivery(WebsiteSale):

    @http.route(['/shop/payment'],type='http',auth="public",website=True)
    defpayment(self,**post):
        order=request.website.sale_get_order()
        carrier_id=post.get('carrier_id')
        ifcarrier_id:
            carrier_id=int(carrier_id)
        iforder:
            order._check_carrier_quotation(force_carrier_id=carrier_id)
            ifcarrier_id:
                returnrequest.redirect("/shop/payment")

        returnsuper(WebsiteSaleDelivery,self).payment(**post)

    @http.route()
    defpayment_transaction(self,*args,**kwargs):
        order=request.website.sale_get_order()
        ifnotorder.is_all_serviceandnotorder.delivery_set:
            raiseValidationError(_('Thereisanissuewithyourdeliverymethod.Pleaserefreshthepageandtryagain.'))
        returnsuper().payment_transaction(*args,**kwargs)

    @http.route(['/shop/update_carrier'],type='json',auth='public',methods=['POST'],website=True,csrf=False)
    defupdate_eshop_carrier(self,**post):
        order=request.website.sale_get_order()
        carrier_id=int(post['carrier_id'])
        iforder:
            order._check_carrier_quotation(force_carrier_id=carrier_id)
        returnself._update_website_sale_delivery_return(order,**post)

    @http.route(['/shop/carrier_rate_shipment'],type='json',auth='public',methods=['POST'],website=True)
    defcart_carrier_rate_shipment(self,carrier_id,**kw):
        order=request.website.sale_get_order(force_create=True)

        ifnotint(carrier_id)inorder._get_delivery_methods().ids:
            raiseUserError(_('Itseemsthatadeliverymethodisnotcompatiblewithyouraddress.Pleaserefreshthepageandtryagain.'))

        Monetary=request.env['ir.qweb.field.monetary']

        res={'carrier_id':carrier_id}
        carrier=request.env['delivery.carrier'].sudo().browse(int(carrier_id))
        rate=carrier.rate_shipment(order)
        ifrate.get('success'):
            tax_ids=carrier.product_id.taxes_id.filtered(lambdat:t.company_id==order.company_id)
            iftax_ids:
                fpos=order.fiscal_position_id
                tax_ids=fpos.map_tax(tax_ids,carrier.product_id,order.partner_shipping_id)
                taxes=tax_ids.compute_all(
                    rate['price'],
                    currency=order.currency_id,
                    quantity=1.0,
                    product=carrier.product_id,
                    partner=order.partner_shipping_id,
                )
                ifrequest.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                    rate['price']=taxes['total_excluded']
                else:
                    rate['price']=taxes['total_included']

            res['status']=True
            res['new_amount_delivery']=Monetary.value_to_html(rate['price'],{'display_currency':order.currency_id})
            res['is_free_delivery']=notbool(rate['price'])
            res['error_message']=rate['warning_message']
        else:
            res['status']=False
            res['new_amount_delivery']=Monetary.value_to_html(0.0,{'display_currency':order.currency_id})
            res['error_message']=rate['error_message']
        returnres

    deforder_lines_2_google_api(self,order_lines):
        """Transformsalistoforderlinesintoadictforgoogleanalytics"""
        order_lines_not_delivery=order_lines.filtered(lambdaline:notline.is_delivery)
        returnsuper(WebsiteSaleDelivery,self).order_lines_2_google_api(order_lines_not_delivery)

    deforder_2_return_dict(self,order):
        """Returnsthetracking_cartdictoftheorderforGoogleanalytics"""
        ret=super(WebsiteSaleDelivery,self).order_2_return_dict(order)
        forlineinorder.order_line:
            ifline.is_delivery:
                ret['transaction']['shipping']=line.price_unit
        returnret

    def_get_shop_payment_values(self,order,**kwargs):
        values=super(WebsiteSaleDelivery,self)._get_shop_payment_values(order,**kwargs)
        has_storable_products=any(line.product_id.typein['consu','product']forlineinorder.order_line)

        ifnotorder._get_delivery_methods()andhas_storable_products:
            values['errors'].append(
                (_('Sorry,weareunabletoshipyourorder'),
                 _('Noshippingmethodisavailableforyourcurrentorderandshippingaddress.'
                   'Pleasecontactusformoreinformation.')))

        ifhas_storable_products:
            iforder.carrier_idandnotorder.delivery_rating_success:
                order._remove_delivery_line()

            delivery_carriers=order._get_delivery_methods()
            values['deliveries']=delivery_carriers.sudo()

        values['delivery_has_storable']=has_storable_products
        values['delivery_action_id']=request.env.ref('delivery.action_delivery_carrier_form').id
        returnvalues

    def_update_website_sale_delivery_return(self,order,**post):
        Monetary=request.env['ir.qweb.field.monetary']
        carrier_id=int(post['carrier_id'])
        currency=order.currency_id
        iforder:
            return{
                'status':order.delivery_rating_success,
                'error_message':order.delivery_message,
                'carrier_id':carrier_id,
                'is_free_delivery':notbool(order.amount_delivery),
                'new_amount_delivery':Monetary.value_to_html(order.amount_delivery,{'display_currency':currency}),
                'new_amount_untaxed':Monetary.value_to_html(order.amount_untaxed,{'display_currency':currency}),
                'new_amount_tax':Monetary.value_to_html(order.amount_tax,{'display_currency':currency}),
                'new_amount_total':Monetary.value_to_html(order.amount_total,{'display_currency':currency}),
            }
        return{}
