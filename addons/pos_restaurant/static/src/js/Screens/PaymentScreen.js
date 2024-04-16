flectra.define('pos_restaurant.PosResPaymentScreen',function(require){
    'usestrict';

    constPaymentScreen=require('point_of_sale.PaymentScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    constPosResPaymentScreen=(PaymentScreen)=>
        classextendsPaymentScreen{
            constructor(){
                super(...arguments);
                useListener('send-payment-adjust',this._sendPaymentAdjust);
            }

            async_sendPaymentAdjust({detail:line}){
                constprevious_amount=line.get_amount();
                constamount_diff=line.order.get_total_with_tax()-line.order.get_total_paid();
                line.set_amount(previous_amount+amount_diff);
                line.set_payment_status('waiting');

                constpayment_terminal=line.payment_method.payment_terminal;
                constisAdjustSuccessful=awaitpayment_terminal.send_payment_adjust(line.cid);
                if(isAdjustSuccessful){
                    line.set_payment_status('done');
                }else{
                    line.set_amount(previous_amount);
                    line.set_payment_status('done');
                }
            }

            getnextScreen(){
                constorder=this.currentOrder;
                if(!this.env.pos.config.set_tip_after_payment||order.is_tipped){
                    returnsuper.nextScreen;
                }
                //Takethefirstpaymentmethodasthemainpayment.
                constmainPayment=order.get_paymentlines()[0];
                if(mainPayment.canBeAdjusted()){
                    return'TipScreen';
                }
                returnsuper.nextScreen;
            }
        };

    Registries.Component.extend(PaymentScreen,PosResPaymentScreen);

    returnPosResPaymentScreen;
});
