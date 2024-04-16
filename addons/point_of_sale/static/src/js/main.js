flectra.define('web.web_client',function(require){
    'usestrict';

    constAbstractService=require('web.AbstractService');
    constenv=require('web.env');
    constWebClient=require('web.AbstractWebClient');
    constChrome=require('point_of_sale.Chrome');
    constRegistries=require('point_of_sale.Registries');
    const{configureGui}=require('point_of_sale.Gui');

    owl.config.mode=env.isDebug()?'dev':'prod';
    owl.Component.env=env;

    Registries.Component.add(owl.misc.Portal);

    functionsetupResponsivePlugin(env){
        constisMobile=()=>window.innerWidth<=768;
        env.isMobile=isMobile();
        constupdateEnv=owl.utils.debounce(()=>{
            if(env.isMobile!==isMobile()){
                env.isMobile=!env.isMobile;
                env.qweb.forceUpdate();
            }
        },15);
        window.addEventListener("resize",updateEnv);
    }

    setupResponsivePlugin(owl.Component.env);

    asyncfunctionstartPosApp(webClient){
        Registries.Component.freeze();
        awaitenv.session.is_bound;
        env.qweb.addTemplates(env.session.owlTemplates);
        env.bus=newowl.core.EventBus();
        awaitowl.utils.whenReady();
        awaitwebClient.setElement(document.body);
        awaitwebClient.start();
        webClient.isStarted=true;
        constchrome=new(Registries.Component.get(Chrome))(null,{webClient});
        awaitchrome.mount(document.querySelector('.o_action_manager'));
        configureGui({component:chrome});
        awaitchrome.start();
    }

    AbstractService.prototype.deployServices(env);
    constwebClient=newWebClient();
    startPosApp(webClient);
    returnwebClient;
});
