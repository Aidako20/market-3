flectra.define('stock.StockOrderpointListView',function(require){
"usestrict";

varListView=require('web.ListView');
varStockOrderpointListController=require('stock.StockOrderpointListController');
varStockOrderpointListModel=require('stock.StockOrderpointListModel');
varviewRegistry=require('web.view_registry');


varStockOrderpointListView=ListView.extend({
    config:_.extend({},ListView.prototype.config,{
        Controller:StockOrderpointListController,
        Model:StockOrderpointListModel,
    }),
});

viewRegistry.add('stock_orderpoint_list',StockOrderpointListView);

returnStockOrderpointListView;

});
