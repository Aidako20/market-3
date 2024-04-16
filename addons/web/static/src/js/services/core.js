flectra.define('web.core',function(require){
"usestrict";

varBus=require('web.Bus');
varconfig=require('web.config');
varClass=require('web.Class');
varQWeb=require('web.QWeb');
varRegistry=require('web.Registry');
vartranslation=require('web.translation');

/**
 *Whethertheclientiscurrentlyin"debug"mode
 *
 *@typeBoolean
 */
varbus=newBus();

_.each('click,dblclick,keydown,keypress,keyup'.split(','),function(evtype){
    $('html').on(evtype,function(ev){
        bus.trigger(evtype,ev);
    });
});
_.each('resize,scroll'.split(','),function(evtype){
    $(window).on(evtype,function(ev){
        bus.trigger(evtype,ev);
    });
});

return{
    qweb:newQWeb(config.isDebug()),

    //coreclassesandfunctions
    Class:Class,
    bus:bus,
    main_bus:newBus(),
    _t:translation._t,
    _lt:translation._lt,

    //registries
    action_registry:newRegistry(),
    crash_registry:newRegistry(),
    serviceRegistry:newRegistry(),
    /**
     *@type{String}
     */
    csrf_token:flectra.csrf_token,
};

});
