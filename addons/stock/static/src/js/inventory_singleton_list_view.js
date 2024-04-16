flectra.define('stock.SingletonListView',function(require){
'usestrict';

varInventoryReportListView=require('stock.InventoryReportListView');
varSingletonListController=require('stock.SingletonListController');
varviewRegistry=require('web.view_registry');

varSingletonListView=InventoryReportListView.extend({
    config:_.extend({},InventoryReportListView.prototype.config,{
        Controller:SingletonListController,
    }),
});

viewRegistry.add('singleton_list',SingletonListView);

returnSingletonListView;

});
