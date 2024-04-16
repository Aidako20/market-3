flectra.define('point_of_sale.PaymentScreenNumpad',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classPaymentScreenNumpadextendsPosComponent{
        constructor(){
            super(...arguments);
            this.decimalPoint=this.env._t.database.parameters.decimal_point;
        }
    }
    PaymentScreenNumpad.template='PaymentScreenNumpad';

    Registries.Component.add(PaymentScreenNumpad);

    returnPaymentScreenNumpad;
});
