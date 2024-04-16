flectra.define('website_sale_coupon_delivery.checkout',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');
require('website_sale_delivery.checkout');

var_t=core._t;

publicWidget.registry.websiteSaleDelivery.include({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _handleCarrierUpdateResult:function(result){
        this._super.apply(this,arguments);
        if(result.new_amount_order_discounted){
            //Updatediscountoftheorder
            $('#order_discounted').html(result.new_amount_order_discounted);
        }
    },
    /**
     *@override
     */
    _handleCarrierUpdateResultBadge:function(result){
        this._super.apply(this,arguments);
        if(result.new_amount_order_discounted){
            //Weareinfreeshipping,soeverycarrierisFreebutwedon't
            //wanttoreplaceerrormessageby'Free'
            $('#delivery_carrier.badge:not(.o_wsale_delivery_carrier_error)').text(_t('Free'));
        }
    },
});
});
