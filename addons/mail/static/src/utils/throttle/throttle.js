flectra.define('mail/static/src/utils/throttle/throttle.js',function(require){
'usestrict';

const{makeDeferred}=require('mail/static/src/utils/deferred/deferred.js');

/**
 *Thismoduledefineanutilityfunctionthatenablesthrottlingcallsona
 *providedfunction.Suchthrottledcallscanbecanceled,flushedand/or
 *cleared:
 *
 *-cancel:Cancelingathrottlefunctioncallmeansthatifafunctioncallis
 *  pendinginvocation,cancelremovesthispendingcallinvocation.Ithowever
 *  preservestheinternaltimerofthecoolingdownphaseofthisthrottle
 *  function,meaningthatanyfollowingthrottlefunctioncallwillbepending
 *  andhastowaitfortheremainingtimeofthecoolingdownphasebefore
 *  beinginvoked.
 *
 *-flush:Flushingathrottlefunctioncallmeansthatifafunctioncallis
 *  pendinginvocation,flushimmediatelyterminatesthecoolingdownphaseand
 *  thependingfunctioncallisimmediatelyinvoked.Flushalsoworkswithout
 *  anypendingfunctioncall:itjustterminatesthecoolingdownphase,so
 *  thatafollowingfunctioncallisguaranteedtobeimmediatelycalled.
 *
 *-clear:Clearingathrottlefunctioncombinescancelingandflushing
 *  together.
 */

//------------------------------------------------------------------------------
//Errors
//------------------------------------------------------------------------------

/**
 *ListofinternalandexternalThrottleerrors.
 *Internalerrorsareprefixedwith`_`.
 */

 /**
  *Errorwhenthrottlefunctionhasbeencanceledwith`.cancel()`.Usedto
  *letthecallerknowofthrottlefunctionthatthecallhasbeencanceled,
  *whichmeanstheinnerfunctionwillnotbecalled.Usuallycallershould
  *justacceptitandkindlytreatthiserrorasapolitewarning.
  */
classThrottleCanceledErrorextendsError{
    /**
     *@override
     */
    constructor(throttleId,...args){
        super(...args);
        this.name='ThrottleCanceledError';
        this.throttleId=throttleId;
    }
}
/**
 *Errorwhenthrottlefunctionhasbeenreinvokedagain.Usedtoletknow
 *callerofthrottlefunctionthatthecallhasbeencanceledandreplacedwith
 *anotherone,whichmeansthe(potentially)followinginnerfunctionwillbe
 *inthecontextofanothercall.Sameasfor`ThrottleCanceledError`,usually
 *callershouldjustacceptitandkindlytreatthiserrorasapolite
 *warning.
 */
classThrottleReinvokedErrorextendsError{
    /**
     *@override
     */
    constructor(throttleId,...args){
        super(...args);
        this.name='ThrottleReinvokedError';
        this.throttleId=throttleId;
    }
}
/**
 *Errorwhenthrottlefunctionhasbeenflushedwith`.flush()`.Used
 *internallytoimmediatelyinvokependinginnerfunctions,sinceaflushmeans
 *theterminationofcoolingdownphase.
 *
 *@private
 */
class_ThrottleFlushedErrorextendsError{
    /**
     *@override
     */
    constructor(throttleId,...args){
        super(...args);
        this.name='_ThrottleFlushedError';
        this.throttleId=throttleId;
    }
}

//------------------------------------------------------------------------------
//Private
//------------------------------------------------------------------------------

/**
 *Thisclassmodelsthebehaviourofthecancelable,flushableandclearable
 *throttleversionofaprovidedfunction.Seedefinitionsatthetopofthis
 *file.
 */
classThrottle{

    /**
     *@param{Object}envtheOWLenv
     *@param{function}funcprovidedfunctionformakingthrottledversion.
     *@param{integer}durationdurationofthe'cooldown'phase,i.e.
     *  theminimumdurationbetweenthemostrecentfunctioncallthathas
     *  beenmadeandthefollowingfunctioncall(ofcourse,assumingnoflush
     *  in-between).
     */
    constructor(env,func,duration){
        /**
         *ReferencetotheOWLenvirionment.Usefultofine-tunecontrolof
         *timeflowintests.
         *@seemail/static/src/utils/test_utils.js:start.hasTimeControl
         */
        this.env=env;
        /**
         *Uniqueidofthisthrottlefunction.UsefulfortheThrottleError
         *management,inordertodeterminewhethertheseerrorscomefrom
         *thisthrottleorfromanotherone(e.g.innerfunctionmakesuseof
         *anotherthrottle).
         */
        this.id=_.uniqueId('throttle_');
        /**
         *Deferredofcurrentcoolingdownphaseinprogress.Definedonlywhen
         *thereisacoolingdownphaseinprogress.Resolvedwhencoolingdown
         *phaseterminatesfromtimeout,andrejectedifflushed.
         *
         *@see_ThrottleFlushedErrorforrejectionofthisdeferred.
         */
        this._coolingDownDeferred=undefined;
        /**
         *Duration,inmilliseconds,ofthecooldownphase.
         */
        this._duration=duration;
        /**
         *Innerfunctiontobeinvokedandthrottled.
         */
        this._function=func;
        /**
         *Determineswhetherthethrottlefunctioniscurrentlyincooldown
         *phase.Cooldownphasehappensjustafterinnerfunctionhasbeen
         *invoked,andduringthistimeanyfollowingfunctioncallarepending
         *andwillbeinvokedonlyaftertheendofthecooldownphase(except
         *ifcanceled).
         */
        this._isCoolingDown=false;
        /**
         *Deferredofacurrentlypendinginvocationtoinnerfunction.Defined
         *onlyduringacoolingdownphaseandjustafterwhenthrottle
         *functionhasbeencalledduringthiscoolingdownphase.Itiskept
         *untilcoolingdownphaseends(eitherfromtimeoutorflushed
         *throttle)oruntilthrottleiscanceled(i.e.removespendinginvoke
         *whilekeepingcoolingdownphaseliveon).
         */
        this._pendingInvokeDeferred=undefined;
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Cancelanybufferedfunctioncallwhilekeepingthecooldownphase
     *running.
     */
    cancel(){
        if(!this._isCoolingDown){
            return;
        }
        if(!this._pendingInvokeDeferred){
            return;
        }
        this._pendingInvokeDeferred.reject(newThrottleCanceledError(this.id));
    }

    /**
     *Clearanybufferedfunctioncallandimmediatelyterminatesanycooling
     *downphaseinprogress.
     */
    clear(){
        this.cancel();
        this.flush();
    }

    /**
     *Calledwhenthereisacalltothefunction.Thisfunctionisthrottled,
     *sothetimeitiscalleddependsonwhetherthe"cooldownstage"occurs
     *ornot:
     *
     *-nocooldownstage:functioniscalledimmediately,anditstarts
     *     thecooldownstagewhensuccessful.
     *-incooldownstage:functioniscalledwhenthecooldownstagehas
     *     endedfromtimeout.
     *
     *Notethatafterthecooldownstage,onlythelastattemptedfunction
     *callwillbeconsidered.
     *
     *@param{...any}args
     *@throws{ThrottleReinvokedError|ThrottleCanceledError}
     *@returns{any}resultofcalledfunction,ifit'scalled.
     */
    asyncdo(...args){
        if(!this._isCoolingDown){
            returnthis._invokeFunction(...args);
        }
        if(this._pendingInvokeDeferred){
            this._pendingInvokeDeferred.reject(newThrottleReinvokedError(this.id));
        }
        try{
            this._pendingInvokeDeferred=makeDeferred();
            awaitPromise.race([this._coolingDownDeferred,this._pendingInvokeDeferred]);
        }catch(error){
            if(
                !(errorinstanceof_ThrottleFlushedError)||
                error.throttleId!==this.id
            ){
                throwerror;
            }
        }finally{
            this._pendingInvokeDeferred=undefined;
        }
        returnthis._invokeFunction(...args);
    }

    /**
     *Flushtheinternalthrottletimer,sothatthefollowingfunctioncall
     *isimmediate.Forinstance,ifthereisacooldownstage,itisaborted.
     */
    flush(){
        if(!this._isCoolingDown){
            return;
        }
        constcoolingDownDeferred=this._coolingDownDeferred;
        this._coolingDownDeferred=undefined;
        this._isCoolingDown=false;
        coolingDownDeferred.reject(new_ThrottleFlushedError(this.id));
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Invoketheinnerfunctionofthisthrottleandstartscoolingdownphase
     *immediatelyafter.
     *
     *@private
     *@param {...any}args
     */
    _invokeFunction(...args){
        constres=this._function(...args);
        this._startCoolingDown();
        returnres;
    }

    /**
     *Calledjustwhentheinnerfunctionisbeingcalled.Startsthecooling
     *downphase,whichturnanycalltothisthrottlefunctionaspending
     *innerfunctioncalls.Thiswillbecalledaftertheendofcoolingdown
     *phase(exceptifcanceled).
     */
    async_startCoolingDown(){
        if(this._coolingDownDeferred){
            thrownewError("Cannotstartcoolingdownifthere'salreadyacoolingdowninprogress.");
        }
        //Keeplocalreferenceofcoolingdowndeferred,becausetheonestored
        //on`this`couldbeoverwrittenbyanothercalltothisthrottle.
        constcoolingDownDeferred=makeDeferred();
        this._coolingDownDeferred=coolingDownDeferred;
        this._isCoolingDown=true;
        constcooldownTimeoutId=this.env.browser.setTimeout(
            ()=>coolingDownDeferred.resolve(),
            this._duration
        );
        letunexpectedError;
        try{
            awaitcoolingDownDeferred;
        }catch(error){
            if(
                !(errorinstanceof_ThrottleFlushedError)||
                error.throttleId!==this.id
            ){
                //Thisbranchingshouldneverhappen.
                //Stilldefinedincaseofprogrammingerror.
                unexpectedError=error;
            }
        }finally{
            this.env.browser.clearTimeout(cooldownTimeoutId);
            this._coolingDownDeferred=undefined;
            this._isCoolingDown=false;
        }
        if(unexpectedError){
            throwunexpectedError;
        }
    }

}

//------------------------------------------------------------------------------
//Public
//------------------------------------------------------------------------------

/**
 *Afunctionthatcreatesacancelable,flushableandclearablethrottle
 *versionofaprovidedfunction.Seedefinitionsatthetopofthisfile.
 *
 *Thisthrottlemechanismallowscallingafunctionatmostonceduringa
 *certainperiod:
 *
 *-Whenafunctioncallismade,itentersa'cooldown'phase,inwhichany
 *    attempttocallthefunctionisbuffereduntilthecooldownphaseends.
 *-Atmost1functioncallcanbebufferedduringthecooldownphase,andthe
 *    latestoneinthisphasewillbeconsideredatitsend.
 *-Whenacooldownphaseends,anybufferedfunctioncallwillbeperformed
 *    andanothercooldownphasewillfollowup.
 *
 *@param{Object}envtheOWLenv
 *@param{function}functhefunctiontothrottle.
 *@param{integer}durationduration,inmilliseconds,ofthecoolingdown
 *  phaseofthethrottling.
 *@param{Object}[param2={}]
 *@param{boolean}[param2.silentCancelationErrors=true]ifunset,caller
 *  ofthrottlefunctionwillobservesomeerrorsthatcomefromcurrent
 *  throttlecallthathasbeencanceled,suchaswhenthrottlefunctionhas
 *  beenexplicitlycanceledwith`.cancel()`orwhenanothernewthrottlecall
 *  hasbeenregistered.
 *  @seeThrottleCanceledErrorforwhenacallhasbeencanceledfromexplicit
 *    call.
 *  @seeThrottleReinvokedErrorforwhenacallhasbeencanceledfromanother
 *    newthrottlecallhasbeenregistered.
 *@returns{function}thecancelable,flushableandclearablethrottleversion
 *  oftheprovidedfunction.
 */
functionthrottle(
    env,
    func,
    duration,
    {silentCancelationErrors=true}={}
){
    constthrottleObj=newThrottle(env,func,duration);
    constcallable=async(...args)=>{
        try{
            //awaitisimportant,otherwiseerrorsarenotintercepted.
            returnawaitthrottleObj.do(...args);
        }catch(error){
            constisSelfReinvokedError=(
                errorinstanceofThrottleReinvokedError&&
                error.throttleId===throttleObj.id
            );
            constisSelfCanceledError=(
                errorinstanceofThrottleCanceledError&&
                error.throttleId===throttleObj.id
            );

            if(silentCancelationErrors&&(isSelfReinvokedError||isSelfCanceledError)){
                //Silentlyignorecancelationerrors.
                //Promiseisindefinitelypendingforasyncfunctions.
                returnnewPromise(()=>{});
            }else{
                throwerror;
            }
        }
    };
    Object.assign(callable,{
        cancel:()=>throttleObj.cancel(),
        clear:()=>throttleObj.clear(),
        flush:()=>throttleObj.flush(),
    });
    returncallable;
}

/**
 *Makeexternalthrottleerrorsaccessiblefromthrottlefunction.
 */
Object.assign(throttle,{
    ThrottleReinvokedError,
    ThrottleCanceledError,
});


returnthrottle;

});
