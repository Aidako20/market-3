#-*-coding:utf-8-*-
fromdatetimeimporttimedelta

fromflectraimportapi,fields,models
fromflectra.httpimportrequest


classSaleOrder(models.Model):
    _inherit="sale.order"

    def_compute_website_order_line(self):
        """Thismethodwillmergemultiplediscountlinesgeneratedbyasameprogram
            intoasingleone(temporarylinewith`new()`).
            Thiscasewillonlyoccurwhentheprogramisadiscountappliedonmultiple
            productswithdifferenttaxes.
            Inthiscase,eachtaxeswillhavetheirowndiscountline.Thisisrequired
            tohavecorrectamountoftaxesaccordingtothediscount.
            Butwewan'ttheselinestobe`visually`mergedintoasingleoneinthe
            e-commercesincetheendusershouldonlyseeonediscountline.
            Thisisonlypossiblesincewedon'tshowtaxesincart.
            eg:
                line1:10%discountonproductwithtax`A`-$15
                line2:10%discountonproductwithtax`B`-$11.5
                line3:10%discountonproductwithtax`C`-$10
            wouldbe`hidden`and`replaced`by
                line1:10%discount-$36.5

            Note:Thelinewillbecreatedwithouttax(es)andtheamountwillbecomputed
                  dependingifB2BorB2Cisenabled.
        """
        super()._compute_website_order_line()
        fororderinself:
            #TODO:potentialperformancebottleneckdownstream
            programs=order._get_applied_programs_with_rewards_on_current_order()
            forprograminprograms:
                program_lines=order.order_line.filtered(lambdaline:
                    line.product_id==program.discount_line_product_id)
                iflen(program_lines)>1:
                    ifself.env.user.has_group('sale.group_show_price_subtotal'):
                        price_unit=sum(program_lines.mapped('price_subtotal'))
                    else:
                        price_unit=sum(program_lines.mapped('price_total'))
                    #TODO:batchthenflush
                    order.website_order_line+=self.env['sale.order.line'].new({
                        'product_id':program_lines[0].product_id.id,
                        'price_unit':price_unit,
                        'name':program_lines[0].name,
                        'product_uom_qty':1,
                        'product_uom':program_lines[0].product_uom.id,
                        'order_id':order.id,
                        'is_reward_line':True,
                    })
                    order.website_order_line-=program_lines

    def_compute_cart_info(self):
        super(SaleOrder,self)._compute_cart_info()
        fororderinself:
            reward_lines=order.website_order_line.filtered(lambdaline:line.is_reward_line)
            order.cart_quantity-=int(sum(reward_lines.mapped('product_uom_qty')))

    defget_promo_code_error(self,delete=True):
        error=request.session.get('error_promo_code')
        iferroranddelete:
            request.session.pop('error_promo_code')
        returnerror

    def_get_coupon_program_domain(self):
        return[('website_id','in',[False,self.website_id.id])]

    def_cart_update(self,product_id=None,line_id=None,add_qty=0,set_qty=0,**kwargs):
        res=super(SaleOrder,self)._cart_update(product_id=product_id,line_id=line_id,add_qty=add_qty,set_qty=set_qty,**kwargs)
        self.recompute_coupon_lines()
        returnres

    def_get_free_shipping_lines(self):
        self.ensure_one()
        free_shipping_prgs_ids=self._get_applied_programs_with_rewards_on_current_order().filtered(lambdap:p.reward_type=='free_shipping')
        ifnotfree_shipping_prgs_ids:
            returnself.env['sale.order.line']
        free_shipping_product_ids=free_shipping_prgs_ids.mapped('discount_line_product_id')
        returnself.order_line.filtered(lambdal:l.product_idinfree_shipping_product_ids)

    @api.autovacuum
    def_gc_abandoned_coupons(self,*args,**kwargs):
        """Remove/freecouponfromabandonnedecommerceorder."""
        ICP=self.env['ir.config_parameter']
        validity=ICP.get_param('website_sale_coupon.abandonned_coupon_validity',4)
        validity=fields.Datetime.to_string(fields.datetime.now()-timedelta(days=int(validity)))
        coupon_to_reset=self.env['coupon.coupon'].search([
            ('state','=','used'),
            ('sales_order_id.state','=','draft'),
            ('sales_order_id.write_date','<',validity),
            ('sales_order_id.website_id','!=',False),
        ])
        forcouponincoupon_to_reset:
            coupon.sales_order_id.applied_coupon_ids-=coupon
        coupon_to_reset.write({'state':'new'})
        coupon_to_reset.mapped('sales_order_id').recompute_coupon_lines()
