#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_

classSaleOrder(models.Model):
    _inherit="sale.order"

    def_get_no_effect_on_threshold_lines(self):
        self.ensure_one()
        #Donotcountshippingandfreeshipping
        free_delivery_product=self.env['coupon.program'].search([('reward_type','=','free_shipping')]).mapped('discount_line_product_id')
        lines=self.order_line.filtered(lambdaline:line.is_deliveryorline.product_idinfree_delivery_product)
        returnlines+super(SaleOrder,self)._get_no_effect_on_threshold_lines()

    def_get_paid_order_lines(self):
        """Returnsthetaxesincludedsaleordertotalamountwithouttherewardsamount"""
        free_reward_product=self.env['coupon.program'].search([('reward_type','=','product')]).mapped('discount_line_product_id')
        returnself.order_line.filtered(lambdax:not(x.is_reward_lineorx.is_delivery)orx.product_idinfree_reward_product)

    def_get_reward_line_values(self,program):
        ifprogram.reward_type=='free_shipping':
            return[self._get_reward_values_free_shipping(program)]
        else:
            returnsuper(SaleOrder,self)._get_reward_line_values(program)

    def_get_reward_values_free_shipping(self,program):
        delivery_line=self.order_line.filtered(lambdax:x.is_delivery)
        taxes=delivery_line.product_id.taxes_id.filtered(lambdat:t.company_id.id==self.company_id.id)
        taxes=self.fiscal_position_id.map_tax(taxes)
        return{
            'name':_("Discount:%s",program.name),
            'product_id':program.discount_line_product_id.id,
            'price_unit':delivery_lineand-delivery_line.price_unitor0.0,
            'product_uom_qty':1.0,
            'product_uom':program.discount_line_product_id.uom_id.id,
            'order_id':self.id,
            'is_reward_line':True,
            'tax_id':[(4,tax.id,False)fortaxintaxes],
        }

    def_get_cheapest_line(self):
        #Unitpricestaxincluded
        returnmin(self.order_line.filtered(lambdax:notx.is_reward_lineandnotx.is_deliveryandx.price_reduce>0),key=lambdax:x['price_reduce'])

classSalesOrderLine(models.Model):
    _inherit="sale.order.line"

    defunlink(self):
        #Duetodelivery_setanddelivery_unsetmethodsthatarecalledeverywhere,don'tunlink
        #rewardlinesifit'safreeshipping
        self=self.exists()
        orders=self.mapped('order_id')
        applied_programs=orders.mapped('no_code_promo_program_ids')+\
                           orders.mapped('code_promo_program_id')+\
                           orders.mapped('applied_coupon_ids').mapped('program_id')
        free_shipping_products=applied_programs.filtered(
            lambdaprogram:program.reward_type=='free_shipping'
        ).mapped('discount_line_product_id')
        lines_to_unlink=self.filtered(lambdaline:line.product_idnotinfree_shipping_products)
        #Unlesstheselinesarethelastones
        res=super(SalesOrderLine,lines_to_unlink).unlink()
        only_free_shipping_line_orders=orders.filtered(lambdaorder:len(order.order_line.ids)==1andorder.order_line.is_reward_line)
        super(SalesOrderLine,only_free_shipping_line_orders.mapped('order_line')).unlink()
        returnres
