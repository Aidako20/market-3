flectra.define('web.public.lazyloader',function(require){
'usestrict';

varblockEvents=['submit','click'];
varblockFunction=function(ev){
    ev.preventDefault();
    ev.stopImmediatePropagation();
};

varwaitingLazy=false;

/**
 *BlockstheDOMsectionswhichexplicitlyrequirethelazyloadedJStobe
 *working(thosesectionsshouldbemarkedwiththe'o_wait_lazy_js'class).
 *
 *@seestopWaitingLazy
 */
functionwaitLazy(){
    if(waitingLazy){
        return;
    }
    waitingLazy=true;

    varlazyEls=document.querySelectorAll('.o_wait_lazy_js');
    for(vari=0;i<lazyEls.length;i++){
        varelement=lazyEls[i];
        blockEvents.forEach(function(evType){
            element.addEventListener(evType,blockFunction);
        });
    }

    document.body.classList.add('o_lazy_js_waiting');
}
/**
 *UnblockstheDOMsectionsblockedby@seewaitLazyandremovestherelated
 *'o_wait_lazy_js'classfromthewholeDOM.
 */
functionstopWaitingLazy(){
    if(!waitingLazy){
        return;
    }
    waitingLazy=false;

    varlazyEls=document.querySelectorAll('.o_wait_lazy_js');
    for(vari=0;i<lazyEls.length;i++){
        varelement=lazyEls[i];
        blockEvents.forEach(function(evType){
            element.removeEventListener(evType,blockFunction);
        });
        element.classList.remove('o_wait_lazy_js');
    }

    document.body.classList.remove('o_lazy_js_waiting');
}

//StartwaitingforlazyloadingassoonastheDOMisavailable
if(document.readyState!=='loading'){
    waitLazy();
}else{
    document.addEventListener('DOMContentLoaded',function(){
        waitLazy();
    });
}

//Assoonaseverythingisfullyloaded,startloadingalltheremainingJS
//andunblocktherelatedDOMsectionwhenallofithavebeenloadedand
//executed
vardoResolve=null;
var_allScriptsLoaded=newPromise(function(resolve){
    if(doResolve){
        resolve();
    }else{
        doResolve=resolve;
    }
}).then(function(){
    stopWaitingLazy();
});
if(document.readyState==='complete'){
    setTimeout(_loadScripts,0);
}else{
    window.addEventListener('load',function(){
        setTimeout(_loadScripts,0);
    });
}

/**
 *@param{DOMElement[]}scripts
 *@param{integer}index
 */
function_loadScripts(scripts,index){
    if(scripts===undefined){
        scripts=document.querySelectorAll('script[data-src]');
    }
    if(index===undefined){
        index=0;
    }
    if(index>=scripts.length){
        if(typeofdoResolve==='function'){
            doResolve();
        }else{
            doResolve=true;
        }
        return;
    }
    varscript=scripts[index];
    script.addEventListener('load',_loadScripts.bind(this,scripts,index+1));
    script.src=script.dataset.src;
    script.removeAttribute('data-src');
}

return{
    loadScripts:_loadScripts,
    allScriptsLoaded:_allScriptsLoaded,
};
});
