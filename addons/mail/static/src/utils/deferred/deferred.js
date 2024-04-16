flectra.define('mail/static/src/utils/deferred/deferred.js',function(require){
'usestrict';

/**
 *@returns{Deferred}
 */
functionmakeDeferred(){
    letresolve;
    letreject;
    constprom=newPromise(function(res,rej){
        resolve=res.bind(this);
        reject=rej.bind(this);
    });
    prom.resolve=(...args)=>resolve(...args);
    prom.reject=(...args)=>reject(...args);
    returnprom;
}

return{makeDeferred};

});
