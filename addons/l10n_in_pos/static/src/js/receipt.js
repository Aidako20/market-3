flectra.define('l10n_in_pos.receipt',function(require){
"usestrict";

varmodels=require('point_of_sale.models');

models.load_fields('product.product','l10n_in_hsn_code');

var_super_orderline=models.Orderline.prototype;
models.Orderline=models.Orderline.extend({
    export_for_printing:function(){
        varline=_super_orderline.export_for_printing.apply(this,arguments);
        line.l10n_in_hsn_code=this.get_product().l10n_in_hsn_code;
        returnline;
    },
});

});
