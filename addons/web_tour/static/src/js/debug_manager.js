flectra.define('web_tour.DebugManager.Backend',function(require){
"usestrict";

varcore=require("web.core");
varDebugManager=require('web.DebugManager.Backend');
varDialog=require("web.Dialog");
varlocal_storage=require('web.local_storage');

vartour=require('web_tour.tour');
varutils=require('web_tour.utils');

varget_debugging_key=utils.get_debugging_key;

functionget_active_tours(){
    return_.difference(_.keys(tour.tours),tour.consumed_tours);
}

DebugManager.include({
    start:function(){
        this.consume_tours_enabled=get_active_tours().length>0;
        returnthis._super.apply(this,arguments);
    },
    consume_tours:function(){
        varactive_tours=get_active_tours();
        if(active_tours.length>0){//toursmighthavebeenconsumedmeanwhile
            this._rpc({
                    model:'web_tour.tour',
                    method:'consume',
                    args:[active_tours],
                })
                .then(function(){
                    for(consttourNameofactive_tours){
                        local_storage.removeItem(get_debugging_key(tourName));
                    }
                    window.location.reload();
                });
        }
    },
    start_tour:asyncfunction(){
        consttours=Object.values(tour.tours).sort((t1,t2)=>{
            return(t1.sequence-t2.sequence)||(t1.name<t2.name?-1:1);
        });
        constdialog=newDialog(this,{
            title:'Tours',
            $content:core.qweb.render('web_tour.ToursDialog',{
                onboardingTours:tours.filter(t=>!t.test),
                testingTours:tours.filter(t=>t.test),
            }),
        });
        awaitdialog.open().opened();
        dialog.$('.o_start_tour').on('click',this._onStartTour.bind(this));
        dialog.$('.o_test_tour').on('click',this._onTestTour.bind(this));
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Resetsthegiventourtoitsinitialstep,inonboardingmode.
     *
     *@private
     *@param{MouseEvent}
     */
    _onStartTour(ev){
        ev.preventDefault();
        tour.reset($(ev.target).data('name'));
    },
    /**
     *Startsthegiventourintestmode.
     *
     *@private
     *@param{MouseEvent}
     */
    _onTestTour(ev){
        ev.preventDefault();
        tour.run($(ev.target).data('name'));
    },
});

});
