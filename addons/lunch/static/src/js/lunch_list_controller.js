flectra.define('lunch.LunchListController',function(require){
"usestrict";

/**
 *ThisfiledefinestheControllerfortheLunchListview,whichisan
 *overrideoftheListController.
 */

varListController=require('web.ListController');
varLunchControllerCommon=require('lunch.LunchControllerCommon');

varLunchListController=ListController.extend(LunchControllerCommon,{
    custom_events:_.extend({},ListController.prototype.custom_events,LunchControllerCommon.custom_events),
});

returnLunchListController;

});
