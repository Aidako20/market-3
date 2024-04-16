flectra.define('mass_mailing.ListKanbanView',function(require){
"usestrict";

varMassMailingListKanbanRenderer=require('mass_mailing.ListKanbanRenderer');

varKanbanView=require('web.KanbanView');
varview_registry=require('web.view_registry');

varMassMailingListKanbanView=KanbanView.extend({
    config:_.extend({},KanbanView.prototype.config,{
        Renderer:MassMailingListKanbanRenderer,
    }),
});

view_registry.add('mass_mailing_list_kanban',MassMailingListKanbanView);

returnMassMailingListKanbanView;

});
