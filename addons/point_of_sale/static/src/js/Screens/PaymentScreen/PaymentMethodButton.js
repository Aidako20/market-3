flectra.define('point_of_sale.PaymentMethodButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classPaymentMethodButtonextendsPosComponent{}
    PaymentMethodButton.template='PaymentMethodButton';

    Registries.Component.add(PaymentMethodButton);

    returnPaymentMethodButton;
});
