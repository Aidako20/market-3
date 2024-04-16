flectra.define('lunch.LunchKanbanController',function(require){
"usestrict";

/**
 *ThisfiledefinestheControllerfortheLunchKanbanview,whichisan
 *overrideoftheKanbanController.
 */

varKanbanController=require('web.KanbanController');
varLunchControllerCommon=require('lunch.LunchControllerCommon');

varLunchKanbanController=KanbanController.extend(LunchControllerCommon,{
    custom_events:_.extend({},KanbanController.prototype.custom_events,LunchControllerCommon.custom_events),
});

returnLunchKanbanController;

});
