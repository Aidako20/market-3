#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportmodels,_


classCoupon(models.Model):
    _inherit="coupon.coupon"

    def_check_coupon_code(self,order):
        ifself.program_id.reward_type=='free_shipping'andnotorder.order_line.filtered(lambdaline:line.is_delivery):
            return{'error':_('Theshippingcostsarenotintheorderlines.')}
        returnsuper(Coupon,self)._check_coupon_code(order)
