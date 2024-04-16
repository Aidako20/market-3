flectra.define('l10n_co_pos.PaymentScreen',function(require){
    'usestrict';

    constPaymentScreen=require('point_of_sale.PaymentScreen');
    constRegistries=require('point_of_sale.Registries');
    constsession=require('web.session');

    constL10nCoPosPaymentScreen=PaymentScreen=>
        classextendsPaymentScreen{
            async_postPushOrderResolve(order,order_server_ids){
                try{
                    if(this.env.pos.is_colombian_country()){
                        constresult=awaitthis.rpc({
                            model:'pos.order',
                            method:'search_read',
                            domain:[['id','in',order_server_ids]],
                            fields:['name'],
                            context:session.user_context,
                        });
                        order.set_l10n_co_dian(result[0].name||false);
                    }
                }finally{
                    returnsuper._postPushOrderResolve(...arguments);
                }
            }
        };

    Registries.Component.extend(PaymentScreen,L10nCoPosPaymentScreen);

    returnPaymentScreen;
});
