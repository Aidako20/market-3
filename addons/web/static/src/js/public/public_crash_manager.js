flectra.define('web.PublicCrashManager',function(require){
"usestrict";

constcore=require('web.core');
constCrashManager=require('web.CrashManager').CrashManager;

constPublicCrashManager=CrashManager.extend({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _displayWarning(message,title,options){
        this.displayNotification(Object.assign({},options,{
            title,
            message,
            sticky:true,
        }));
    },
});

core.serviceRegistry.add('crash_manager',PublicCrashManager);

return{
    CrashManager:PublicCrashManager,
};

});
