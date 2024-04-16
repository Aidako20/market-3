flectra.define('pos_adyen.PaymentScreen',function(require){
    "usestrict";

    constPaymentScreen=require('point_of_sale.PaymentScreen');
    constRegistries=require('point_of_sale.Registries');
    const{onMounted}=owl.hooks;

    constPosAdyenPaymentScreen=PaymentScreen=>classextendsPaymentScreen{
        constructor(){
            super(...arguments);
            onMounted(()=>{
                constpendingPaymentLine=this.currentOrder.paymentlines.find(
                    paymentLine=>paymentLine.payment_method.use_payment_terminal==='adyen'&&
                        (!paymentLine.is_done()&&paymentLine.get_payment_status()!=='pending')
                );
                if(pendingPaymentLine){
                    constpaymentTerminal=pendingPaymentLine.payment_method.payment_terminal;
                    paymentTerminal.set_most_recent_service_id(pendingPaymentLine.terminalServiceId);
                    pendingPaymentLine.set_payment_status('waiting');
                    paymentTerminal.start_get_status_polling().then(isPaymentSuccessful=>{
                        if(isPaymentSuccessful){
                            pendingPaymentLine.set_payment_status('done');
                            pendingPaymentLine.can_be_reversed=paymentTerminal.supports_reversals;
                        }else{
                            pendingPaymentLine.set_payment_status('retry');
                        }
                    });
                }
            });
        }
    };

    Registries.Component.extend(PaymentScreen,PosAdyenPaymentScreen);

    returnPaymentScreen;
});
