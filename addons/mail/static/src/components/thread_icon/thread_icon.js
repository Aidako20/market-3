flectra.define('mail/static/src/components/thread_icon/thread_icon.js',function(require){
'usestrict';

constcomponents={
    ThreadTypingIcon:require('mail/static/src/components/thread_typing_icon/thread_typing_icon.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classThreadIconextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            constcorrespondent=thread?thread.correspondent:undefined;
            return{
                correspondent,
                correspondentImStatus:correspondent&&correspondent.im_status,
                history:this.env.messaging.history,
                inbox:this.env.messaging.inbox,
                moderation:this.env.messaging.moderation,
                partnerRoot:this.env.messaging.partnerRoot,
                starred:this.env.messaging.starred,
                thread,
                threadChannelType:thread&&thread.channel_type,
                threadModel:thread&&thread.model,
                threadOrderedOtherTypingMembersLength:thread&&thread.orderedOtherTypingMembers.length,
                threadPublic:thread&&thread.public,
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

Object.assign(ThreadIcon,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.ThreadIcon',
});

returnThreadIcon;

});
