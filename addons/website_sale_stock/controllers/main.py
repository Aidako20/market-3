#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.exceptionsimportValidationError


classWebsiteSaleStock(WebsiteSale):
    @http.route()
    defpayment_transaction(self,*args,**kwargs):
        """Paymenttransactionoverridetodoublecheckcartquantitiesbefore
        placingtheorder
        """
        order=request.website.sale_get_order()
        values=[]
        forlineinorder.order_line:
            ifline.product_id.type=='product'andline.product_id.inventory_availabilityin['always','threshold']:
                cart_qty=sum(order.order_line.filtered(lambdap:p.product_id.id==line.product_id.id).mapped('product_uom_qty'))
                avl_qty=line.product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
                ifcart_qty>avl_qty:
                    values.append(_(
                        'Youaskfor%(quantity)sproductsbutonly%(available_qty)sisavailable',
                        quantity=cart_qty,
                        available_qty=avl_qtyifavl_qty>0else0
                    ))
        ifvalues:
            raiseValidationError('.'.join(values)+'.')
        returnsuper(WebsiteSaleStock,self).payment_transaction(*args,**kwargs)
