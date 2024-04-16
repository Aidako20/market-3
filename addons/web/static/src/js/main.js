flectra.define('web.web_client',function(require){
    "usestrict";

    constAbstractService=require('web.AbstractService');
    constenv=require('web.env');
    constsession=require("web.session");
    constWebClient=require('web.WebClient');

    //configuretheenvandsetitonOwlComponent
    owl.config.mode=env.isDebug()?"dev":"prod";
    owl.Component.env=env;

    //deployservicesintheenv
    AbstractService.prototype.deployServices(env);

    //addtheowltemplatestotheenvironmentandstartthewebclient
    constwebClient=newWebClient();
    asyncfunctionstartWebClient(){
        awaitsession.is_bound;
        env.qweb.addTemplates(session.owlTemplates);

        awaitowl.utils.whenReady();
        webClient.setElement($(document.body));
        webClient.start();
    }
    startWebClient();

    returnwebClient;
});
