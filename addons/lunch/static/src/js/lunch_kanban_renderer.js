flectra.define('lunch.LunchKanbanRenderer',function(require){
"usestrict";

/**
 *ThisfiledefinestheRendererfortheLunchKanbanview,whichisan
 *overrideoftheKanbanRenderer.
 */

varLunchKanbanRecord=require('lunch.LunchKanbanRecord');

varKanbanRenderer=require('web.KanbanRenderer');

varLunchKanbanRenderer=KanbanRenderer.extend({
    config:_.extend({},KanbanRenderer.prototype.config,{
        KanbanRecord:LunchKanbanRecord,
    }),

    /**
     *@override
     */
    start:function(){
        this.$el.addClass('o_lunch_viewo_lunch_kanban_viewposition-relativealign-content-startflex-grow-1flex-shrink-1');
        returnthis._super.apply(this,arguments);
    },
});

returnLunchKanbanRenderer;

});
