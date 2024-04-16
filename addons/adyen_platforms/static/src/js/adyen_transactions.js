flectra.define('adyen_platforms.transactions',function(require){
"usestrict";

varListController=require('web.ListController');
varListView=require('web.ListView');
varviewRegistry=require('web.view_registry');

varTransactionsListController=ListController.extend({
    buttons_template:'AdyenTransactionsListView.buttons',
    events:_.extend({},ListController.prototype.events,{
        'click.o_button_sync_transactions':'_onTransactionsSync',
    }),

    _onTransactionsSync:function(){
        varself=this;
        this._rpc({
            model:'adyen.transaction',
            method:'sync_adyen_transactions',
            args:[],
        }).then(function(){
            self.trigger_up('reload');
        });
    }
});

varTransactionsListView=ListView.extend({
    config:_.extend({},ListView.prototype.config,{
        Controller:TransactionsListController,
    }),
});

viewRegistry.add('adyen_transactions_tree',TransactionsListView);
});
