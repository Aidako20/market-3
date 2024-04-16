flectra.define('mrp.MrpDocumentsKanbanView',function(require){
"usestrict";

constKanbanView=require('web.KanbanView');
constMrpDocumentsKanbanController=require('mrp.MrpDocumentsKanbanController');
constMrpDocumentsKanbanRenderer=require('mrp.MrpDocumentsKanbanRenderer');
constviewRegistry=require('web.view_registry');

constMrpDocumentsKanbanView=KanbanView.extend({
    config:Object.assign({},KanbanView.prototype.config,{
        Controller:MrpDocumentsKanbanController,
        Renderer:MrpDocumentsKanbanRenderer,
    }),
});

viewRegistry.add('mrp_documents_kanban',MrpDocumentsKanbanView);

returnMrpDocumentsKanbanView;

});
