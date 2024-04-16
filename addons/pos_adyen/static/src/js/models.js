flectra.define('pos_adyen.models',function(require){
varmodels=require('point_of_sale.models');
varPaymentAdyen=require('pos_adyen.payment');

models.register_payment_method('adyen',PaymentAdyen);
models.register_payment_method('flectra_adyen',PaymentAdyen);
models.load_fields('pos.payment.method','adyen_terminal_identifier');

constsuperPaymentline=models.Paymentline.prototype;
models.Paymentline=models.Paymentline.extend({
    initialize:function(attr,options){
        superPaymentline.initialize.call(this,attr,options);
        this.terminalServiceId=this.terminalServiceId ||null;
    },
    export_as_JSON:function(){
        constjson=superPaymentline.export_as_JSON.call(this);
        json.terminal_service_id=this.terminalServiceId;
        returnjson;
    },
    init_from_JSON:function(json){
        superPaymentline.init_from_JSON.apply(this,arguments);
        this.terminalServiceId=json.terminal_service_id;
    },
    setTerminalServiceId:function(id){
        this.terminalServiceId=id;
    }
});

});
