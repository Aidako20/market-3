#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classSaleCoupon(models.Model):
    _inherit='coupon.coupon'

    def_check_coupon_code(self,order):
        ifself.program_id.website_idandself.program_id.website_id!=order.website_id:
            return{'error':'Thiscouponisnotvalidonthiswebsite.'}
        returnsuper()._check_coupon_code(order)
