flectra.define('l10n_co_pos.pos',function(require){
"usestrict";

varmodels=require('point_of_sale.models');

models.PosModel=models.PosModel.extend({
    is_colombian_country:function(){
        returnthis.company.country.code==='CO';
    },
});

var_super_order=models.Order.prototype;
models.Order=models.Order.extend({
    export_for_printing:function(){
        varresult=_super_order.export_for_printing.apply(this,arguments);
        result.l10n_co_dian=this.get_l10n_co_dian();
        returnresult;
    },
    set_l10n_co_dian:function(l10n_co_dian){
        this.l10n_co_dian=l10n_co_dian;
    },
    get_l10n_co_dian:function(){
        returnthis.l10n_co_dian;
    },
    wait_for_push_order:function(){
        varresult=_super_order.wait_for_push_order.apply(this,arguments);
        result=Boolean(result||this.pos.is_colombian_country());
        returnresult;
    }
});

});
