flectra.define('root.widget',function(require){
'usestrict';

constAbstractService=require('web.AbstractService');
constenv=require('web.public_env');
varlazyloader=require('web.public.lazyloader');
varrootData=require('web.public.root');

/**
 *ConfigureOwlwiththepublicenv
 */
owl.config.mode=env.isDebug()?"dev":"prod";
owl.Component.env=env;

/**
 *Deployservicesintheenv
 */
AbstractService.prototype.deployServices(env);

/**
 *Thiswidgetisimportant,becausethetourmanagerneedsarootwidgetin
 *ordertowork.Therootwidgetmustbeaserviceproviderwiththeajax
 *service,sothatthetourmanagercanlettheserverknowwhentourshave
 *beenconsumed.
 */
varpublicRoot=newrootData.PublicRoot(null);
returnlazyloader.allScriptsLoaded.then(function(){
    returnpublicRoot.attachTo(document.body).then(function(){
        returnpublicRoot;
    });
});

});
