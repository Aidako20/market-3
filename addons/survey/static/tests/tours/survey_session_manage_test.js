flectra.define('survey.session_manage_test',function(require){
"usestrict";

varSessionManager=require('survey.session_manage');
/**
 *Smalloverridefortest/tourpurposes.
 */
SessionManager.include({
    /**
     *-Triggerthefetchofanswerresultsimmediatelyatthestart.
     *(Insteadofwasting2secondswaitingafterthestart).
     *-Setthefadein/outtimeto1mstoavoidunnecessarydelays.
     *-Avoidrefreshingtheresultsevery2seconds
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments)
            .then(this._refreshResults.bind(this))
            .then(function(){
                self.fadeInOutTime=1;
                clearInterval(self.resultsRefreshInterval);
            });
    },

    /**
     *Forcethetimerto"now"toavoidintroducingpotentialtestbreaking
     *timelyvariables(rpc/smallserverdelay/...)ifthestart_question_timeflickers.
     */
    _startTimer:function(){
        this.$el.data('timer',moment.utc());
        returnthis._super.apply(this,arguments);
    }
});

returnSessionManager;

});
