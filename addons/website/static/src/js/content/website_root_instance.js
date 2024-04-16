flectra.define('root.widget',function(require){
'usestrict';

constAbstractService=require('web.AbstractService');
constenv=require('web.public_env');
varlazyloader=require('web.public.lazyloader');
varwebsiteRootData=require('website.root');

/**
 *ConfigureOwlwiththepublicenv
 */
owl.config.mode=env.isDebug()?"dev":"prod";
owl.Component.env=env;

/**
 *Deployservicesintheenv
 */
AbstractService.prototype.deployServices(env);

varwebsiteRoot=newwebsiteRootData.WebsiteRoot(null);
returnlazyloader.allScriptsLoaded.then(function(){
    returnwebsiteRoot.attachTo(document.body).then(function(){
        returnwebsiteRoot;
    });
});
});
