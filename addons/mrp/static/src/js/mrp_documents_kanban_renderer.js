flectra.define('mrp.MrpDocumentsKanbanRenderer',function(require){
"usestrict";

/**
 *ThisfiledefinestheRendererfortheMRPDocumentsKanbanview,whichisan
 *overrideoftheKanbanRenderer.
 */

constKanbanRenderer=require('web.KanbanRenderer');
constMrpDocumentsKanbanRecord=require('mrp.MrpDocumentsKanbanRecord');

constMrpDocumentsKanbanRenderer=KanbanRenderer.extend({
    config:Object.assign({},KanbanRenderer.prototype.config,{
        KanbanRecord:MrpDocumentsKanbanRecord,
    }),
    /**
     *@override
     */
    asyncstart(){
        this.$el.addClass('o_mrp_documents_kanban_view');
        awaitthis._super(...arguments);
    },
});

returnMrpDocumentsKanbanRenderer;

});
