flectra.define('lunch.LunchPaymentDialog',function(require){
"usestrict";

varDialog=require('web.Dialog');

varLunchPaymentDialog=Dialog.extend({
    template:'lunch.LunchPaymentDialog',

    init:function(parent,options){
        this._super.apply(this,arguments);

        options=options||{};

        this.message=options.message||'';
    },
});

returnLunchPaymentDialog;

});
