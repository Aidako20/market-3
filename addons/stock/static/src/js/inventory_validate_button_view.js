flectra.define('stock.InventoryValidationView',function(require){
"usestrict";

varInventoryValidationController=require('stock.InventoryValidationController');
varListView=require('web.ListView');
varviewRegistry=require('web.view_registry');

varInventoryValidationView=ListView.extend({
    config:_.extend({},ListView.prototype.config,{
        Controller:InventoryValidationController
    })
});

viewRegistry.add('inventory_validate_button',InventoryValidationView);

});
