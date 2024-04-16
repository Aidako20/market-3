//definethe'web.web_client'modulebecausesomeothermodulesrequireit
flectra.define('web.web_client',asyncfunction(require){
    "usestrict";

    constsession=require("web.session");
    const{bus}=require('web.core');

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

    awaitsession.is_bound;
    session.owlTemplates=session.owlTemplates.replace(/t-transition/g,'transition');
});
