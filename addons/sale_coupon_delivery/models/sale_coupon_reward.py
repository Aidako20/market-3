#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_


classCouponReward(models.Model):
    _inherit='coupon.reward'
    _description="CouponReward"

    reward_type=fields.Selection(selection_add=[('free_shipping','FreeShipping')])

    defname_get(self):
        result=[]
        reward_names=super(CouponReward,self).name_get()
        free_shipping_reward_ids=self.filtered(lambdareward:reward.reward_type=='free_shipping').ids
        forresinreward_names:
            result.append((res[0],res[0]infree_shipping_reward_idsand_("FreeShipping")orres[1]))
        returnresult
