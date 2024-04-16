#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportmodels,_,api


classCouponProgram(models.Model):
    _inherit="coupon.program"

    def_filter_not_ordered_reward_programs(self,order):
        """
        Returnstheprogramswhentherewardisactuallyintheorderlines
        """
        programs=super(CouponProgram,self)._filter_not_ordered_reward_programs(order)
        #Donotfilteronfreedeliveryprograms.Asdelivery_unsetiscalledeverywhere(whichis
        #ratherstupid),thedeliverylineisunlikedtobecreatedagaininsteadofwritingonitto
        #modifytheprice_unit.Thatway,therewardisunlinkandisnotsetbackagain.
        returnprograms

    def_check_promo_code(self,order,coupon_code):
        ifself.reward_type=='free_shipping'andnotany(line.is_deliveryforlineinorder.order_line):
            return{'error':_('Theshippingcostsarenotintheorderlines.')}
        returnsuper(CouponProgram,self)._check_promo_code(order,coupon_code)
