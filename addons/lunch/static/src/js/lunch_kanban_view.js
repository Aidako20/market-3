flectra.define('lunch.LunchKanbanView',function(require){
"usestrict";

varLunchKanbanController=require('lunch.LunchKanbanController');
varLunchKanbanRenderer=require('lunch.LunchKanbanRenderer');

varcore=require('web.core');
varKanbanView=require('web.KanbanView');
varview_registry=require('web.view_registry');

var_lt=core._lt;

varLunchKanbanView=KanbanView.extend({
    config:_.extend({},KanbanView.prototype.config,{
        Controller:LunchKanbanController,
        Renderer:LunchKanbanRenderer,
    }),
    display_name:_lt('LunchKanban'),

    /**
     *@override
     */
    _createSearchModel(params,extraExtensions={}){
        Object.assign(extraExtensions,{Lunch:{}});
        returnthis._super(params,extraExtensions);
    },
});

view_registry.add('lunch_kanban',LunchKanbanView);

returnLunchKanbanView;

});
