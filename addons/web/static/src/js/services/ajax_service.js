flectra.define('web.AjaxService',function(require){
"usestrict";

varAbstractService=require('web.AbstractService');
varajax=require('web.ajax');
varcore=require('web.core');
varsession=require('web.session');

varAjaxService=AbstractService.extend({
    /**
     *@param{Object}libs-@seeajax.loadLibs
     *@param{Object}[context]-@seeajax.loadLibs
     *@param{Object}[tplRoute]-@seeajax.loadLibs
     */
    loadLibs:function(libs,context,tplRoute){
        returnajax.loadLibs(libs,context,tplRoute);
    },
    rpc:function(route,args,options,target){
        varrpcPromise;
        varpromise=newPromise(function(resolve,reject){
            rpcPromise=session.rpc(route,args,options);
            rpcPromise.then(function(result){
                if(!target.isDestroyed()){
                    resolve(result);
                }
            }).guardedCatch(function(reason){
                if(!target.isDestroyed()){
                    reject(reason);
                }
            });
        });
        promise.abort=rpcPromise.abort.bind(rpcPromise);
        returnpromise;
    },
});

core.serviceRegistry.add('ajax',AjaxService);

returnAjaxService;

});
