#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models
fromflectra.addons.website.modelsimportir_http


classProductProduct(models.Model):
    _inherit='product.product'

    cart_qty=fields.Integer(compute='_compute_cart_qty')

    def_compute_cart_qty(self):
        website=ir_http.get_request_website()
        ifnotwebsite:
            self.cart_qty=0
            return
        cart=website.sale_get_order()
        forproductinself:
            product.cart_qty=sum(cart.order_line.filtered(lambdap:p.product_id.id==product.id).mapped('product_uom_qty'))ifcartelse0
