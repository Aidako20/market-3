flectra.define('mail/static/src/utils/timer/timer.js',function(require){
'usestrict';

const{makeDeferred}=require('mail/static/src/utils/deferred/deferred.js');

//------------------------------------------------------------------------------
//Errors
//------------------------------------------------------------------------------

/**
 *ListofTimererrors.
 */

 /**
  *Errorwhentimerhasbeenclearedwith`.clear()`or`.reset()`.Usedto
  *letknowcalleroftimerthatthecountdownhasbeenaborted,which
  *meanstheinnerfunctionwillnotbecalled.Usuallycallershouldjust
  *acceptitandkindlytreatedthiserrorasapolitewarning.
  */
 classTimerClearedErrorextendsError{
    /**
     *@override
     */
    constructor(timerId,...args){
        super(...args);
        this.name='TimerClearedError';
        this.timerId=timerId;
    }
}

//------------------------------------------------------------------------------
//Private
//------------------------------------------------------------------------------

/**
 *Thisclasscreatesatimerwhich,whentimesout,callsafunction.
 *Notethatthetimerisnotstartedoninitialization(@seestartmethod).
 */
classTimer{

    /**
     *@param{Object}envtheOWLenv
     *@param{function}onTimeout
     *@param{integer}duration
     *@param{Object}[param3={}]
     *@param{boolean}[param3.silentCancelationErrors=true]ifunset,caller
     *  oftimerwillobservesomeerrorsthatcomefromcurrenttimercalls
     *  thathasbeenclearedwith`.clear()`or`.reset()`.
     *  @seeTimerClearedErrorforwhentimerhasbeenabortedfrom`.clear()`
     *    or`.reset()`.
     */
    constructor(env,onTimeout,duration,{silentCancelationErrors=true}={}){
        this.env=env;
        /**
         *Determinewhetherthetimerhasapendingtimeout.
         */
        this.isRunning=false;
        /**
         *Duration,inmilliseconds,untiltimertimesoutandcallsthe
         *timeoutfunction.
         */
        this._duration=duration;
        /**
         *Determinewhetherthecalleroftimer`.start()`and`.reset()`
         *shouldobservecancelationerrorsfrom`.clear()`or`.reset()`.
         */
        this._hasSilentCancelationErrors=silentCancelationErrors;
        /**
         *Thefunctionthatiscalledwhenthetimertimesout.
         */
        this._onTimeout=onTimeout;
        /**
         *Deferredofacurrentlypendinginvocationtoinnerfunctionon
         *timeout.
         */
        this._timeoutDeferred=undefined;
        /**
         *Internalreferenceof`setTimeout()`thatisusedtoinvokefunction
         *whentimertimesout.Usefultoclearitwhentimeriscleared/reset.
         */
        this._timeoutId=undefined;
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Clearthetimer,whichbasicallysetsthestateoftimerasifitwas
     *justinstantiated,withoutbeingstarted.Thisfunctionmakessenseonly
     *whenthistimerisrunning.
     */
    clear(){
        this.env.browser.clearTimeout(this._timeoutId);
        this.isRunning=false;
        if(!this._timeoutDeferred){
            return;
        }
        this._timeoutDeferred.reject(newTimerClearedError(this.id));
    }

    /**
     *Resetthetimer,i.e.thependingtimeoutisrefreshedwithinitial
     *duration.Thisfunctionmakessenseonlywhenthistimerisrunning.
     */
    asyncreset(){
        this.clear();
        awaitthis.start();
    }

    /**
     *Startsthetimer,i.e.afteracertainduration,ittimesoutandcalls
     *afunctionback.Thisfunctionmakessenseonlywhenthistimerisnot
     *yetrunning.
     *
     *@throws{Error}incasethetimerisalreadyrunning.
     */
    asyncstart(){
        if(this.isRunning){
            thrownewError("Cannotstartatimerthatiscurrentlyrunning.");
        }
        this.isRunning=true;
        consttimeoutDeferred=makeDeferred();
        this._timeoutDeferred=timeoutDeferred;
        consttimeoutId=this.env.browser.setTimeout(
            ()=>{
                this.isRunning=false;
                timeoutDeferred.resolve(this._onTimeout());
            },
            this._duration
        );
        this._timeoutId=timeoutId;
        letresult;
        try{
            result=awaittimeoutDeferred;
        }catch(error){
            if(
                !this._hasSilentCancelationErrors||
                !(errorinstanceofTimerClearedError)||
                error.timerId!==this.id
            ){
                //Thisbranchingshouldneverhappens.
                //Stilldefinedincaseofprogrammingerror.
                throwerror;
            }
        }finally{
            this.env.browser.clearTimeout(timeoutId);
            this._timeoutDeferred=undefined;
            this.isRunning=false;
        }
        returnresult;
    }

}

/**
 *Makeexternaltimererrorsaccessiblefromtimerclass.
 */
Object.assign(Timer,{
    TimerClearedError,
});

returnTimer;

});
