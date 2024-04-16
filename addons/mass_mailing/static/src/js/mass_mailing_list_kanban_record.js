flectra.define('mass_mailing.ListKanbanRecord',function(require){
"usestrict";

varKanbanRecord=require('web.KanbanRecord');

varMassMailingListKanbanRecord=KanbanRecord.extend({
    /**
     *@override
     *@private
     */
    _openRecord:function(){
        this.$('.o_mailing_list_kanban_boxesa').first().click();
    }
});

returnMassMailingListKanbanRecord;

});
