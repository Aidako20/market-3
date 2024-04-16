flectra.define('mail/static/src/utils/utils.js',function(require){
'usestrict';

const{delay}=require('web.concurrency');
const{
    patch:webUtilsPatch,
    unaccent,
    unpatch:webUtilsUnpatch,
}=require('web.utils');

//------------------------------------------------------------------------------
//Public
//------------------------------------------------------------------------------

constclassPatchMap=newWeakMap();
consteventHandledWeakMap=newWeakMap();

/**
 *Returnsthegivenstringaftercleaningit.Thegoalofthecleanistogive
 *moreconvenientresultswhencomparingittopotentialsearchresults,on
 *whichthecleanshouldalsobecalledbeforecomparingthem.
 *
 *@param{string}searchTerm
 *@returns{string}
 */
functioncleanSearchTerm(searchTerm){
    returnunaccent(searchTerm.toLowerCase());
}

/**
 *Executestheprovidedfunctionsinorder,butwithapotentialdelaybetween
 *themiftheytaketoomuchtime.Thisisdoneinordertoavoidblockingthe
 *mainthreadfortoolong.
 *
 *@param{function[]}functions
 *@param{integer}[maxTimeFrame=100]time(inms)untiladelayisintroduced
 */
asyncfunctionexecuteGracefully(functions,maxTimeFrame=100){
    letstartDate=newDate();
    for(constfuncoffunctions){
        if(newDate()-startDate>maxTimeFrame){
            awaitnewPromise(resolve=>setTimeout(resolve));
            startDate=newDate();
        }
        awaitfunc();
    }
}

/**
 *ReturnswhetherthegiveneventhasbeenhandledwiththegivenmarkName.
 *
 *@param{Event}ev
 *@param{string}markName
 *@returns{boolean}
 */
functionisEventHandled(ev,markName){
    if(!eventHandledWeakMap.get(ev)){
        returnfalse;
    }
    returneventHandledWeakMap.get(ev).includes(markName);
}

/**
 *MarksthegiveneventashandledbythegivenmarkName.Usefultoallow
 *handlersinthepropagationchaintomakeadecisionbasedonwhathas
 *alreadybeendone.
 *
 *@param{Event}ev
 *@param{string}markName
 */
functionmarkEventHandled(ev,markName){
    if(!eventHandledWeakMap.get(ev)){
        eventHandledWeakMap.set(ev,[]);
    }
    eventHandledWeakMap.get(ev).push(markName);
}

/**
 *Waitatasktick,sothatanythinginmicro-taskqueuethatcanbeprocessed
 *isprocessed.
 */
asyncfunctionnextTick(){
    awaitdelay(0);
}

/**
 *Inspiredbyweb.utils:patchutilityfunction
 *
 *@param{Class}Class
 *@param{string}patchName
 *@param{Object}patch
 *@returns{function}unpatchfunction
 */
functionpatchClassMethods(Class,patchName,patch){
    letmetadata=classPatchMap.get(Class);
    if(!metadata){
        metadata={
            origMethods:{},
            patches:{},
            current:[]
        };
        classPatchMap.set(Class,metadata);
    }
    if(metadata.patches[patchName]){
        thrownewError(`Patch[${patchName}]alreadyexists`);
    }
    metadata.patches[patchName]=patch;
    applyPatch(Class,patch);
    metadata.current.push(patchName);

    functionapplyPatch(Class,patch){
        Object.keys(patch).forEach(function(methodName){
            constmethod=patch[methodName];
            if(typeofmethod==="function"){
                constoriginal=Class[methodName];
                if(!(methodNameinmetadata.origMethods)){
                    metadata.origMethods[methodName]=original;
                }
                Class[methodName]=function(...args){
                    constpreviousSuper=this._super;
                    this._super=original;
                    constres=method.call(this,...args);
                    this._super=previousSuper;
                    returnres;
                };
            }
        });
    }

    return()=>unpatchClassMethods.bind(Class,patchName);
}

/**
 *@param{Class}Class
 *@param{string}patchName
 *@param{Object}patch
 *@returns{function}unpatchfunction
 */
functionpatchInstanceMethods(Class,patchName,patch){
    returnwebUtilsPatch(Class,patchName,patch);
}

/**
 *Inspiredbyweb.utils:unpatchutilityfunction
 *
 *@param{Class}Class
 *@param{string}patchName
 */
functionunpatchClassMethods(Class,patchName){
    letmetadata=classPatchMap.get(Class);
    if(!metadata){
        return;
    }
    classPatchMap.delete(Class);

    //resettooriginal
    for(letkinmetadata.origMethods){
        Class[k]=metadata.origMethods[k];
    }

    //applyotherpatches
    for(letnameofmetadata.current){
        if(name!==patchName){
            patchClassMethods(Class,name,metadata.patches[name]);
        }
    }
}

/**
 *@param{Class}Class
 *@param{string}patchName
 */
functionunpatchInstanceMethods(Class,patchName){
    returnwebUtilsUnpatch(Class,patchName);
}

//------------------------------------------------------------------------------
//Export
//------------------------------------------------------------------------------

return{
    cleanSearchTerm,
    executeGracefully,
    isEventHandled,
    markEventHandled,
    nextTick,
    patchClassMethods,
    patchInstanceMethods,
    unpatchClassMethods,
    unpatchInstanceMethods,
};

});
