flectra.define('project.project_kanban',function(require){
'usestrict';

varKanbanController=require('web.KanbanController');
varKanbanView=require('web.KanbanView');
varKanbanColumn=require('web.KanbanColumn');
varview_registry=require('web.view_registry');
varKanbanRecord=require('web.KanbanRecord');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
     //YTITODO:Shouldbetransformedintoaextendandspecifictoproject
    _openRecord:function(){
        if(this.selectionMode!==true&&this.modelName==='project.project'&&
            this.$(".o_project_kanban_boxesa").length){
            this.$('.o_project_kanban_boxesa').first().click();
        }else{
            this._super.apply(this,arguments);
        }
    },
});

varProjectKanbanController=KanbanController.extend({
    custom_events:_.extend({},KanbanController.prototype.custom_events,{
        'kanban_column_delete_wizard':'_onDeleteColumnWizard',
    }),

    _onDeleteColumnWizard:function(ev){
        ev.stopPropagation();
        constself=this;
        constcolumn_id=ev.target.id;
        varstate=this.model.get(this.handle,{raw:true});
        this._rpc({
            model:'project.task.type',
            method:'unlink_wizard',
            args:[column_id],
            context:state.getContext(),
        }).then(function(res){
            self.do_action(res);
        });
    }
});

varProjectKanbanView=KanbanView.extend({
    config:_.extend({},KanbanView.prototype.config,{
        Controller:ProjectKanbanController
    }),
});

KanbanColumn.include({
    _onDeleteColumn:function(event){
        if(this.modelName==='project.task'&&this.groupedBy==='stage_id'){
            event.preventDefault();
            this.trigger_up('kanban_column_delete_wizard');
            return;
        }
        this._super.apply(this,arguments);
    }
});

view_registry.add('project_kanban',ProjectKanbanView);

returnProjectKanbanController;
});
