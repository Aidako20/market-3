/**
 *The_throttleinunderscorehasthefeaturetocancelthethrottledfunction
 *onlystartingversion1.9.0
 *@todoremovethisinmasterandupdateunderscorejsto1.9.1
 */

//Returnsafunction,that,wheninvoked,willonlybetriggeredatmostonce
//duringagivenwindowoftime.Normally,thethrottledfunctionwillrun
//asmuchasitcan,withoutevergoingmorethanonceper`wait`duration;
//butifyou'dliketodisabletheexecutionontheleadingedge,pass
//`{leading:false}`.Todisableexecutiononthetrailingedge,ditto.

_.cancellableThrottleRemoveMeSoon=function(func,wait,options){
    vartimeout,context,args,result;
    varprevious=0;
    if(!options)options={};

    varlater=function(){
        previous=options.leading===false?0:_.now();
        timeout=null;
        result=func.apply(context,args);
        if(!timeout)context=args=null;
    };

    varthrottled=function(){
        varnow=_.now();
        if(!previous&&options.leading===false)previous=now;
        varremaining=wait-(now-previous);
        context=this;
        args=arguments;
        if(remaining<=0||remaining>wait){
            if(timeout){
                clearTimeout(timeout);
                timeout=null;
            }
            previous=now;
            result=func.apply(context,args);
            if(!timeout)context=args=null;
        }elseif(!timeout&&options.trailing!==false){
            timeout=setTimeout(later,remaining);
        }
        returnresult;
    };

    throttled.cancel=function(){
        clearTimeout(timeout);
        previous=0;
        timeout=context=args=null;
    };

    returnthrottled;
};
