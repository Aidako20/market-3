flectra.define('pos_six.models',function(require){

varmodels=require('point_of_sale.models');
varPaymentSix=require('pos_six.payment');

models.register_payment_method('six',PaymentSix);
models.load_fields('pos.payment.method',['six_terminal_ip']);

});
