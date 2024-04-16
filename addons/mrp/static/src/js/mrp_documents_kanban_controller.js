flectra.define('mrp.MrpDocumentsKanbanController',function(require){
"usestrict";

/**
 *ThisfiledefinestheControllerfortheMRPDocumentsKanbanview,whichisan
 *overrideoftheKanbanController.
 */

constMrpDocumentsControllerMixin=require('mrp.controllerMixin');

constKanbanController=require('web.KanbanController');

constMrpDocumentsKanbanController=KanbanController.extend(MrpDocumentsControllerMixin,{
    events:Object.assign({},KanbanController.prototype.events,MrpDocumentsControllerMixin.events),
    custom_events:Object.assign({},KanbanController.prototype.custom_events,MrpDocumentsControllerMixin.custom_events),

    /**
     *@override
    */
    init(){
        this._super(...arguments);
        MrpDocumentsControllerMixin.init.apply(this,arguments);
    },
    /**
     *Overridetoupdatetherecordsselection.
     *
     *@override
    */
    asyncreload(){
        awaitthis._super(...arguments);
        awaitMrpDocumentsControllerMixin.reload.apply(this,arguments);
    },
});

returnMrpDocumentsKanbanController;

});
