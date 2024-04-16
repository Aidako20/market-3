flectra.define('l10n_fr_pos_cert.pos',function(require){
"usestrict";

const{Gui}=require('point_of_sale.Gui');
varmodels=require('point_of_sale.models');
varrpc=require('web.rpc');
varsession=require('web.session');
varcore=require('web.core');
varutils=require('web.utils');

var_t=core._t;
varround_di=utils.round_decimals;

var_super_posmodel=models.PosModel.prototype;
models.PosModel=models.PosModel.extend({
    is_french_country:function(){
      varfrench_countries=['FR','MF','MQ','NC','PF','RE','GF','GP','TF'];
      if(!this.company.country){
        Gui.showPopup("ErrorPopup",{
            'title':_t("MissingCountry"),
            'body': _.str.sprintf(_t('Thecompany%sdoesn\'thaveacountryset.'),this.company.name),
        });
        returnfalse;
      }
      return_.contains(french_countries,this.company.country.code);
    },
    delete_current_order:function(){
        if(this.is_french_country()&&this.get_order().get_orderlines().length){
            Gui.showPopup("ErrorPopup",{
                'title':_t("FiscalDataModuleerror"),
                'body': _t("Deletingofordersisnotallowed."),
            });
        }else{
            _super_posmodel.delete_current_order.apply(this,arguments);
        }
    },

    disallowLineQuantityChange(){
        letresult=_super_posmodel.disallowLineQuantityChange.bind(this)();
        returnthis.is_french_country()||result;
    }
});


var_super_order=models.Order.prototype;
models.Order=models.Order.extend({
    initialize:function(){
        _super_order.initialize.apply(this,arguments);
        this.l10n_fr_hash=this.l10n_fr_hash||false;
        this.save_to_db();
    },
    export_for_printing:function(){
      varresult=_super_order.export_for_printing.apply(this,arguments);
      result.l10n_fr_hash=this.get_l10n_fr_hash();
      returnresult;
    },
    set_l10n_fr_hash:function(l10n_fr_hash){
      this.l10n_fr_hash=l10n_fr_hash;
    },
    get_l10n_fr_hash:function(){
      returnthis.l10n_fr_hash;
    },
    wait_for_push_order:function(){
      varresult=_super_order.wait_for_push_order.apply(this,arguments);
      result=Boolean(result||this.pos.is_french_country());
      returnresult;
    }
});

varorderline_super=models.Orderline.prototype;
models.Orderline=models.Orderline.extend({
    can_be_merged_with:function(orderline){
        if(this.pos.is_french_country()){
            constorder=this.pos.get_order();
            constlastId=order.orderlines.last().cid;
            if((order.orderlines._byId[lastId].product.id!==orderline.product.id||order.orderlines._byId[lastId].quantity<0)){
                returnfalse;
            }
            returnorderline_super.can_be_merged_with.apply(this,arguments);
        }
        returnorderline_super.can_be_merged_with.apply(this,arguments);
    }
});

});
