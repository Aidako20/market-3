flectra.define('pos_discount.models',function(require){
  "usestrict";

  varmodels=require('point_of_sale.models');

  varexisting_models=models.PosModel.prototype.models;
  varproduct_index=_.findIndex(existing_models,function(model){
      returnmodel.model==="product.product";
  });
  varproduct_model=existing_models[product_index];

  models.load_models([{
    model: product_model.model,
    fields:product_model.fields,
    order: product_model.order,
    domain:function(self){return[['id','=',self.config.discount_product_id[0]]];},
    context:product_model.context,
    loaded:product_model.loaded,
  }]);

});
