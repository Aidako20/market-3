flectra.define('crm.crm_kanban',function(require){
    "usestrict";

    /**
     *ThisKanbanModelmakesurewedisplayarainbowman
     *messagewhenaleadiswonafterwemoveditinthe
     *correctcolumnandwhenit'sgroupedbystage_id(default).
     */

    varKanbanModel=require('web.KanbanModel');
    varKanbanView=require('web.KanbanView');
    varviewRegistry=require('web.view_registry');

    varCrmKanbanModel=KanbanModel.extend({
        /**
         *Checkifthekanbanviewisgroupedby"stage_id"beforecheckingiftheleadiswon
         *anddisplayingapossiblerainbowmanmessage.
         *@override
         */
        moveRecord:asyncfunction(recordID,groupID,parentID){
            varresult=awaitthis._super(...arguments);
            if(this.localData[parentID].groupedBy[0]===this.defaultGroupedBy[0]){
                constmessage=awaitthis._rpc({
                    model:'crm.lead',
                    method:'get_rainbowman_message',
                    args:[[parseInt(this.localData[recordID].res_id)]],
                });
                if(message){
                    this.trigger_up('show_effect',{
                        message:message,
                        type:'rainbow_man',
                    });
                }
            }
            returnresult;
        },
    });

    varCrmKanbanView=KanbanView.extend({
        config:_.extend({},KanbanView.prototype.config,{
            Model:CrmKanbanModel,
        }),
    });

    viewRegistry.add('crm_kanban',CrmKanbanView);

    return{
        CrmKanbanModel:CrmKanbanModel,
        CrmKanbanView:CrmKanbanView,
    };

});
