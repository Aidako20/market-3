flectra.define('mass_mailing.ListKanbanRenderer',function(require){
"usestrict";

varMassMailingListKanbanRecord=require('mass_mailing.ListKanbanRecord');

varKanbanRenderer=require('web.KanbanRenderer');

varMassMailingListKanbanRenderer=KanbanRenderer.extend({
    config:_.extend({},KanbanRenderer.prototype.config,{
        KanbanRecord:MassMailingListKanbanRecord,
    })
});

returnMassMailingListKanbanRenderer;

});
