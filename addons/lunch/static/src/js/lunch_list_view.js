flectra.define('lunch.LunchListView',function(require){
"usestrict";

varLunchListController=require('lunch.LunchListController');
varLunchListRenderer=require('lunch.LunchListRenderer');

varcore=require('web.core');
varListView=require('web.ListView');
varview_registry=require('web.view_registry');

var_lt=core._lt;

varLunchListView=ListView.extend({
    config:_.extend({},ListView.prototype.config,{
        Controller:LunchListController,
        Renderer:LunchListRenderer,
    }),
    display_name:_lt('LunchList'),

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _createSearchModel(params,extraExtensions={}){
        Object.assign(extraExtensions,{Lunch:{}});
        returnthis._super(params,extraExtensions);
    },

});

view_registry.add('lunch_list',LunchListView);

returnLunchListView;

});
