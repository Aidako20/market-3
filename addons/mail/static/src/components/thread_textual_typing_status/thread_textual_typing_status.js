flectra.define('mail/static/src/components/thread_textual_typing_status/thread_textual_typing_status.js',function(require){
'usestrict';

constcomponents={
    ThreadTypingIcon:require('mail/static/src/components/thread_typing_icon/thread_typing_icon.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classThreadTextualTypingStatusextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            return{
                threadOrderedOtherTypingMembersLength:thread&&thread.orderedOtherTypingMembersLength,
                threadTypingStatusText:thread&&thread.typingStatusText,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.thread}
     */
    getthread(){
        returnthis.env.models['mail.thread'].get(this.props.threadLocalId);
    }

}

Object.assign(ThreadTextualTypingStatus,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.ThreadTextualTypingStatus',
});

returnThreadTextualTypingStatus;

});
