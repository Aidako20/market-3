flectra.define('pos_hr.PaymentScreen',function(require){
    'usestrict';

    constPaymentScreen=require('point_of_sale.PaymentScreen');
    constRegistries=require('point_of_sale.Registries');

    constPosHrPaymentScreen=(PaymentScreen_)=>
          classextendsPaymentScreen_{
              async_finalizeValidation(){
                  this.currentOrder.employee=this.env.pos.get_cashier();
                  awaitsuper._finalizeValidation();
              }
          };

    Registries.Component.extend(PaymentScreen,PosHrPaymentScreen);

    returnPaymentScreen;
});
