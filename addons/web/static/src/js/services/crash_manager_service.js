flectra.define('crash_manager.service',function(require){
'usestrict';

constcore=require('web.core');
constCrashManager=require('web.CrashManager').CrashManager;

core.serviceRegistry.add('crash_manager',CrashManager);

});
