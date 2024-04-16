flectra.define('web.web_client',function(require){
    //thismoduleisrequiredbythetest
    const{bus}=require('web.core');
    constWebClient=require('web.AbstractWebClient');

    //listentounhandledrejectedpromises,andwhentherejectionisnotdue
    //toacrash,preventthebrowserfromdisplayingan'unhandledrejection'
    //errorintheconsole,whichwouldmaketestscrashoneachPromise.reject()
    //somethingsimilarisdonebytheCrashManagerService,butbydefault,it
    //isn'tdeployedintests
    bus.on('crash_manager_unhandledrejection',this,function(ev){
        if(!ev.reason||!(ev.reasoninstanceofError)){
            ev.stopPropagation();
            ev.stopImmediatePropagation();
            ev.preventDefault();
        }
    });

    owl.config.mode="dev";

    constwebClient=newWebClient();
    returnwebClient;
});
