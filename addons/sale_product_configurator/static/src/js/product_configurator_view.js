flectra.define('sale_product_configurator.ProductConfiguratorFormView',function(require){
"usestrict";

varProductConfiguratorFormController=require('sale_product_configurator.ProductConfiguratorFormController');
varProductConfiguratorFormRenderer=require('sale_product_configurator.ProductConfiguratorFormRenderer');
varFormView=require('web.FormView');
varviewRegistry=require('web.view_registry');

varProductConfiguratorFormView=FormView.extend({
    config:_.extend({},FormView.prototype.config,{
        Controller:ProductConfiguratorFormController,
        Renderer:ProductConfiguratorFormRenderer,
    }),
});

viewRegistry.add('product_configurator_form',ProductConfiguratorFormView);

returnProductConfiguratorFormView;

});
