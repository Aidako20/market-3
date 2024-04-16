flectra.define('l10n_fr_pos_cert.PaymentScreen',function(require){

    constPaymentScreen=require('point_of_sale.PaymentScreen');
    constRegistries=require('point_of_sale.Registries');
    constsession=require('web.session');

    constPosFrPaymentScreen=PaymentScreen=>classextendsPaymentScreen{
        async_postPushOrderResolve(order,order_server_ids){
            try{
                if(this.env.pos.is_french_country()){
                    letresult=awaitthis.rpc({
                        model:'pos.order',
                        method:'search_read',
                        domain:[['id','in',order_server_ids]],
                        fields:['l10n_fr_hash'],
                        context:session.user_context,
                    });
                    order.set_l10n_fr_hash(result[0].l10n_fr_hash||false);
                }
            }finally{
                returnsuper._postPushOrderResolve(...arguments);
            }
        }
    };

    Registries.Component.extend(PaymentScreen,PosFrPaymentScreen);

    returnPaymentScreen;
});
