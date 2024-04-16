flectra.define('web.Bus',function(require){
"usestrict";

varClass=require('web.Class');
varmixins=require('web.mixins');

/**
 *EventBususedtobindeventsscopedinthecurrentinstance
 *
 *@classBus
 */
returnClass.extend(mixins.EventDispatcherMixin,{
    init:function(parent){
        mixins.EventDispatcherMixin.init.call(this);
        this.setParent(parent);
    },
});

});
