flectra.define('website_event.display_timer_widget',function(require){
'usestrict';

varcore=require('web.core');
var_t=core._t;
varpublicWidget=require('web.public.widget');

publicWidget.registry.displayTimerWidget=publicWidget.Widget.extend({
    selector:'.o_display_timer',

    /**
     *Thiswidgetallowstodisplayadomelementattheendofacertaintimelaps.
     *Thereare2timersavailable:
     *  -Themain-timer:displaytheDOMelement(usingthedisplayClass)attheendofthistimer.
     *  -Thepre-timer:additionaltimertodisplaythemain-timer.Thispre-timercanbeinvisibleorvisible,
     *                   dependingofthestartCountdownDisplayoption.Oncethepre-timerisover,
                          themain-timerisdisplayed.
     *@override
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.options=self.$target.data();
            self.preCountdownDisplay=self.options["preCountdownDisplay"];
            self.preCountdownTime=self.options["preCountdownTime"];
            self.preCountdownText=self.options["preCountdownText"];

            self.mainCountdownTime=self.options["mainCountdownTime"];
            self.mainCountdownText=self.options["mainCountdownText"];
            self.mainCountdownDisplay=self.options["mainCountdownDisplay"];

            self.displayClass=self.options["displayClass"];

            if(self.preCountdownDisplay){
                $(self.$el).parent().removeClass('d-none');
            }

            self._checkTimer();
            self.interval=setInterval(function(){self._checkTimer();},1000);
        });
    },

    /**
     *Thismethodremoves1secondtothecurrenttimer(pre-timerormain-timer)
     *andcallthemethodtoupdatetheDOM,unlessmain-timerisover.Inthatlastcase,
     *theDOMelementtoshowisdisplayed.
     *
     *@private
     */
    _checkTimer:function(){
        varnow=newDate();

        varremainingPreSeconds=this.preCountdownTime-(now.getTime()/1000);
        if(remainingPreSeconds<=1){
            this.$('.o_countdown_text').text(this.mainCountdownText);
            if(this.mainCountdownDisplay){
                $(this.$el).parent().removeClass('d-none');
            }
            varremainingMainSeconds=this.mainCountdownTime-(now.getTime()/1000);
            if(remainingMainSeconds<=1){
                clearInterval(this.interval);
                $(this.displayClass).removeClass('d-none');
                $(this.$el).parent().addClass('d-none');
            }else{
                this._updateCountdown(remainingMainSeconds);
            }
        }else{
            this._updateCountdown(remainingPreSeconds);
        }
    },

    /**
     *ThismethodupdatetheDOMtodisplaytheremainingtime.
     *fromseconds,themethodextractthenumberofdays,hours,minutesandsecondsand
     *overridethedifferentDOMelementsvalues.
     *
     *@private
     */
    _updateCountdown:function(remainingTime){
        varremainingSeconds=remainingTime;
        vardays=Math.floor(remainingSeconds/86400);

        remainingSeconds=remainingSeconds%86400;
        varhours=Math.floor(remainingSeconds/3600);

        remainingSeconds=remainingSeconds%3600;
        varminutes=Math.floor(remainingSeconds/60);

        remainingSeconds=Math.floor(remainingSeconds%60);

        this.$("span.o_timer_days").text(days);
        this.$("span.o_timer_hours").text(this._zeroPad(hours,2));
        this.$("span.o_timer_minutes").text(this._zeroPad(minutes,2));
        this.$("span.o_timer_seconds").text(this._zeroPad(remainingSeconds,2));
    },

    /**
     *Smalltooltoaddleadingzérostothegivennumber,infunctionoftheneedednumberofleadingzéros.
     *
     *@private
     */
    _zeroPad:function(num,places){
      varzero=places-num.toString().length+1;
      returnnewArray(+(zero>0&&zero)).join("0")+num;
    },

});

returnpublicWidget.registry.countdownWidget;

});
