flectra.define('website_sale.validate',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varcore=require('web.core');
var_t=core._t;

publicWidget.registry.websiteSaleValidate=publicWidget.Widget.extend({
    selector:'div.oe_website_sale_tx_status[data-order-id]',

    /**
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);
        this._poll_nbr=0;
        this._paymentTransationPollStatus();
        returndef;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _paymentTransationPollStatus:function(){
        varself=this;
        this._rpc({
            route:'/shop/payment/get_status/'+parseInt(this.$el.data('order-id')),
        }).then(function(result){
            self._poll_nbr+=1;
            if(result.recall){
                if(self._poll_nbr<20){
                    setTimeout(function(){
                        self._paymentTransationPollStatus();
                    },Math.ceil(self._poll_nbr/3)*1000);
                }else{
                    var$message=$(result.message);
                    var$warning= $("<iclass='fafa-warning'style='margin-right:10px;'>");
                    $warning.attr("title",_t("Wearewaitingforconfirmationfromthebankorthepaymentprovider"));
                    $message.find('span:first').prepend($warning);
                    result.message=$message.html();
                }
            }
            self.$el.html(result.message);
        });
    },
});
});
