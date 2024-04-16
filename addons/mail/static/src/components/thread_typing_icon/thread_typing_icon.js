flectra.define('mail/static/src/components/thread_typing_icon/thread_typing_icon.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');

const{Component}=owl;

classThreadTypingIconextendsComponent{

    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
    }

}

Object.assign(ThreadTypingIcon,{
    defaultProps:{
        animation:'none',
        size:'small',
    },
    props:{
        animation:{
            type:String,
            validate:prop=>['bounce','none','pulse'].includes(prop),
        },
        size:{
            type:String,
            validate:prop=>['small','medium'].includes(prop),
        },
        title:{
            type:String,
            optional:true,
        }
    },
    template:'mail.ThreadTypingIcon',
});

returnThreadTypingIcon;

});
