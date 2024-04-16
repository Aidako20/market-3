flectra.define('web_tour.DisableTour',function(require){
"usestrict";

varlocal_storage=require('web.local_storage');
varTourManager=require('web_tour.TourManager');
varutils=require('web_tour.utils');

varget_debugging_key=utils.get_debugging_key;

TourManager.include({
    /**
     *DisablestoursifFlectrainstalledwithdemodata.
     *
     *@override
     */
    _register:function(do_update,tour,name){
        //Consumingtourswhicharenotrunbytestcasenorcurrentlybeingdebugged
        if(!this.running_tour&&!local_storage.getItem(get_debugging_key(name))){
            this.consumed_tours.push(name);
        }
        returnthis._super.apply(this,arguments);
    },
});

});
