flectra.define('survey.timer',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.SurveyTimerWidget=publicWidget.Widget.extend({
    //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    init:function(parent,params){
        this._super.apply(this,arguments);
        this.timer=params.timer;
        this.timeLimitMinutes=params.timeLimitMinutes;
        this.surveyTimerInterval=null;
        this.timeDifference=null;
        if(params.serverTime){
            this.timeDifference=moment.utc().diff(moment.utc(params.serverTime),'milliseconds');
        }
    },


    /**
    *Tworesponsabilities:ValidatethattimelimitisnotexceededandRuntimerotherwise.
    *Ifend-user'sclockORthesystemclock isde-synchronizedbeforethesurveyisstarted,weapplythe
    *differenceintimer(iftimedifferenceismorethan5seconds)sothatwecan
    *displaythe'absolute'counter
    *
    *@override
    */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.countDownDate=moment.utc(self.timer).add(self.timeLimitMinutes,'minutes');
            if(Math.abs(self.timeDifference)>=5000){
                self.countDownDate=self.countDownDate.add(self.timeDifference,'milliseconds');
            }
            if(self.timeLimitMinutes<=0||self.countDownDate.diff(moment.utc(),'seconds')<0){
                self.trigger_up('time_up');
            }else{
                self._updateTimer();
                self.surveyTimerInterval=setInterval(self._updateTimer.bind(self),1000);
            }
        });
    },

    //-------------------------------------------------------------------------
    //Private
    //-------------------------------------------------------------------------

    _formatTime:function(time){
        returntime>9?time:'0'+time;
    },

    /**
    *ThisfunctionisresponsibleforthevisualupdateofthetimerDOMeverysecond.
    *Whenthetimerunsout,ittriggersa'time_up'eventtonotifytheparentwidget.
    *
    *Weuseadiffinmillisandnotasecond,thatweroundtothenearestsecond.
    *Indeed,adifferenceof999millisisinterpretedas0secondbymoment,whichisproblematic
    *forourusecase.
    */
    _updateTimer:function(){
        vartimeLeft=Math.round(this.countDownDate.diff(moment.utc(),'milliseconds')/1000);

        if(timeLeft>=0){
            vartimeLeftMinutes=parseInt(timeLeft/60);
            vartimeLeftSeconds=timeLeft-(timeLeftMinutes*60);
            this.$el.text(this._formatTime(timeLeftMinutes)+':'+this._formatTime(timeLeftSeconds));
        }else{
            clearInterval(this.surveyTimerInterval);
            this.trigger_up('time_up');
        }
    },
});

returnpublicWidget.registry.SurveyTimerWidget;

});
