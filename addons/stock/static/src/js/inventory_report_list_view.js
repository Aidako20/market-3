flectra.define('stock.InventoryReportListView',function(require){
"usestrict";

varListView=require('web.ListView');
varInventoryReportListController=require('stock.InventoryReportListController');
varviewRegistry=require('web.view_registry');


varInventoryReportListView=ListView.extend({
    config:_.extend({},ListView.prototype.config,{
        Controller:InventoryReportListController,
    }),
});

viewRegistry.add('inventory_report_list',InventoryReportListView);

returnInventoryReportListView;

});
