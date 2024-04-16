flectra.define('stock.StockOrderpointListModel',function(require){
"usestrict";

varcore=require('web.core');
varListModel=require('web.ListModel');

varqweb=core.qweb;


varStockOrderpointListModel=ListModel.extend({

    //-------------------------------------------------------------------------
    //Public
    //-------------------------------------------------------------------------
    /**
     */
    replenish:function(recordResIds){
      varself=this;
      returnthis._rpc({
          model:this.loadParams.modelName,
          method:'action_replenish',
          args:[recordResIds],
          context:this.loadParams.context,
      }).then(function(){
          returnself.do_action('stock.action_replenishment');
      });
    },

    snooze:function(recordResIds){
      varself=this;
      returnthis.do_action('stock.action_orderpoint_snooze',{
          additional_context:{
              default_orderpoint_ids:recordResIds
          },
          on_close:()=>self.do_action('stock.action_replenishment')
      });
    },
});

returnStockOrderpointListModel;

});
