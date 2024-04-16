flectra.define('web.select_create_controllers_registry',function(require){
"usestrict";

return{};

});

flectra.define('web._select_create_controllers_registry',function(require){
"usestrict";

varKanbanController=require('web.KanbanController');
varListController=require('web.ListController');
varselect_create_controllers_registry=require('web.select_create_controllers_registry');

varSelectCreateKanbanController=KanbanController.extend({
    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Overridetoselecttheclickedrecordinsteadofopeningit
     *
     *@override
     *@private
     */
    _onOpenRecord:function(ev){
        varselectedRecord=this.model.get(ev.data.id);
        this.trigger_up('select_record',{
            id:selectedRecord.res_id,
            display_name:selectedRecord.data.display_name,
        });
    },
});

varSelectCreateListController=ListController.extend({
    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Overridetoselecttheclickedrecordinsteadofopeningit
     *
     *@override
     *@private
     */
    _onOpenRecord:function(ev){
        varselectedRecord=this.model.get(ev.data.id);
        this.trigger_up('select_record',{
            id:selectedRecord.res_id,
            display_name:selectedRecord.data.display_name,
        });
    },
});

_.extend(select_create_controllers_registry,{
    SelectCreateListController:SelectCreateListController,
    SelectCreateKanbanController:SelectCreateKanbanController,
});

});
