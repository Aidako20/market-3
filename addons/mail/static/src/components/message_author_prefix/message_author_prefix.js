flectra.define('mail/static/src/components/message_author_prefix/message_author_prefix.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classMessageAuthorPrefixextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constmessage=this.env.models['mail.message'].get(props.messageLocalId);
            constauthor=message?message.author:undefined;
            constthread=props.threadLocalId
                ?this.env.models['mail.thread'].get(props.threadLocalId)
                :undefined;
            return{
                author:author?author.__state:undefined,
                currentPartner:this.env.messaging.currentPartner
                    ?this.env.messaging.currentPartner.__state
                    :undefined,
                message:message?message.__state:undefined,
                thread:thread?thread.__state:undefined,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.message}
     */
    getmessage(){
        returnthis.env.models['mail.message'].get(this.props.messageLocalId);
    }

    /**
     *@returns{mail.thread|undefined}
     */
    getthread(){
        returnthis.env.models['mail.thread'].get(this.props.threadLocalId);
    }

}

Object.assign(MessageAuthorPrefix,{
    props:{
        messageLocalId:String,
        threadLocalId:{
            type:String,
            optional:true,
        },
    },
    template:'mail.MessageAuthorPrefix',
});

returnMessageAuthorPrefix;

});
