flectra.define('mass_mailing.mass_mailing',function(require){
"usestrict";

varKanbanColumn=require('web.KanbanColumn');

KanbanColumn.include({
    init:function(){
        this._super.apply(this,arguments);
        if(this.modelName==='mailing.mailing'){
            this.draggable=false;
        }
    },
});

});
