/**
 *ThisfileallowsintroducingnewJSmoduleswithoutcontaminatingotherfiles.
 *ThisisusefulwhenbugfixingrequiresaddingsuchJSmodulesinstable
 *versionsofFlectra.Anymodulethatisdefinedinthisfileshouldbeisolated
 *initsownfileinmaster.
 */
flectra.define('mail/static/src/bugfix/bugfix.js',function(require){
'usestrict';

});

//Shouldbemovedtoitsownfileinmaster.
flectra.define('mail/static/src/component_hooks/use_rendered_values/use_rendered_values.js',function(require){
'usestrict';

const{Component}=owl;
const{onMounted,onPatched}=owl.hooks;

/**
 *Thishooksprovidessupportforaccessingthevaluesreturnedbythegiven
 *selectoratthetimeofthelastrender.Thevalueswillbeupdatedafter
 *everymount/patch.
 *
 *@param{function}selectorfunctionthatwillbeexecutedatthetimeofthe
 * renderandofwhichtheresultwillbestoredforfuturereference.
 *@returns{function}functiontocalltoretrievethelastrenderedvalues.
 */
functionuseRenderedValues(selector){
    constcomponent=Component.current;
    letrenderedValues;
    letpatchedValues;

    const__render=component.__render.bind(component);
    component.__render=function(){
        renderedValues=selector();
        return__render(...arguments);
    };
    onMounted(onUpdate);
    onPatched(onUpdate);
    functiononUpdate(){
        patchedValues=renderedValues;
    }
    return()=>patchedValues;
}

returnuseRenderedValues;

});

//Shouldbemovedtoitsownfileinmaster.
flectra.define('mail/static/src/component_hooks/use_update/use_update.js',function(require){
'usestrict';

const{Component}=owl;
const{onMounted,onPatched}=owl.hooks;

constexecutionQueue=[];

functionexecuteNextInQueue(){
    if(executionQueue.length===0){
        return;
    }
    const{component,func}=executionQueue.shift();
    if(component.__owl__.status!==5/*DESTROYED*/){
        func();
    }
    executeNextInQueue();
}

/**
 *@param{Object}param0
 *@param{Component}param0.component
 *@param{function}param0.func
 *@param{integer}param0.priority
 */
asyncfunctionaddFunctionToQueue({component,func,priority}){
    constindex=executionQueue.findIndex(item=>item.priority>priority);
    constitem={component,func,priority};
    if(index===-1){
        executionQueue.push(item);
    }else{
        executionQueue.splice(index,0,item);
    }
    //Timeouttoallowallcomponentstoregistertheirfunctionbefore
    //executinganyofthem,torespectallpriorities.
    awaitnewPromise(resolve=>setTimeout(resolve));
    executeNextInQueue();
}

/**
 *Thishookprovidessupportforexecutingcodeafterupdate(renderorpatch).
 *
 *@param{Object}param0
 *@param{function}param0.functhefunctiontoexecuteaftertheupdate.
 *@param{integer}[param0.priority]determinestheexecutionorderofthefunction
 * amongtheupdatefunctionofothercomponents.Lowerpriorityisexecuted
 * first.Ifnopriorityisgiven,thefunctionisexecutedimmediately.
 * Thisparamisdeprecatedbecausedesynchronizedupdateiscausingissueif
 * thereisanewrenderplannedinthemeantime(modelsdatabecomeobsolete
 * intheupdatemethod).
 */
functionuseUpdate({func,priority}){
    constcomponent=Component.current;
    onMounted(onUpdate);
    onPatched(onUpdate);
    functiononUpdate(){
        if(priority===undefined){
            func();
            return;
        }
        addFunctionToQueue({component,func,priority});
    }
}

returnuseUpdate;

});

//Shouldbemovedtoitsownfileinmaster.
flectra.define('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js',function(require){
'usestrict';

const{Component}=owl;
const{onPatched}=owl.hooks;

/**
 *Compares`a`and`b`uptothegiven`compareDepth`.
 *
 *@param{any}a
 *@param{any}b
 *@param{Object|integer}compareDepth
 *@returns{boolean}
 */
functionisEqual(a,b,compareDepth){
    constkeys=Object.keys(a);
    if(Object.keys(b).length!==keys.length){
        returnfalse;
    }
    for(constkeyofkeys){
        //thedepthcanbegiveneitherasanumber(forallkeys)oras
        //anobject(foreachkey)
        letdepth;
        if(typeofcompareDepth==='number'){
            depth=compareDepth;
        }else{
            depth=compareDepth[key]||0;
        }
        if(depth===0&&a[key]!==b[key]){
            returnfalse;
        }
        if(depth!==0){
            letnextDepth;
            if(typeofdepth==='number'){
                nextDepth=depth-1;
            }else{
                nextDepth=depth;
            }
            if(!isEqual(a[key],b[key],nextDepth)){
                returnfalse;
            }
        }
    }
    returntrue;
}

/**
 *Thishookoverridesthe`shouldUpdate`methodtoensurethecomponentisonly
 *updatedifitspropsactuallychanged.Thisisespeciallyusefultouseon
 *componentsforwhichanextrarendercostsproportionallyalotmorethan
 *comparingprops.
 *
 *@param{Object}[param0={}]
 *@param{Object}[param0.compareDepth={}]allowstospecifythecomparison
 * depthtouseforeachprop.Defaultisshallowcompare(depth=0).
 */
functionuseShouldUpdateBasedOnProps({compareDepth={}}={}){
    constcomponent=Component.current;
    letforceRender=false;
    component.shouldUpdate=nextProps=>{
        if(forceRender){
            returntrue;
        }
        constallNewProps=Object.assign({},nextProps);
        constdefaultProps=component.constructor.defaultProps;
        for(constkeyindefaultProps){
            if(allNewProps[key]===undefined){
                allNewProps[key]=defaultProps[key];
            }
        }
        forceRender=!isEqual(component.props,allNewProps,compareDepth);
        returnforceRender;
    };
    onPatched(()=>forceRender=false);
}

returnuseShouldUpdateBasedOnProps;

});
