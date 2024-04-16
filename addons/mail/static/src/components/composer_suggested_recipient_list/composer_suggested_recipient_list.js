flectra.define('mail/static/src/components/composer_suggested_recipient_list/composer_suggested_recipient_list.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;
const{useState}=owl.hooks;

constcomponents={
    ComposerSuggestedRecipient:require('mail/static/src/components/composer_suggested_recipient/composer_suggested_recipient.js'),
};

classComposerSuggestedRecipientListextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state=useState({
            hasShowMoreButton:false,
        });
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            return{
                threadSuggestedRecipientInfoList:thread?thread.suggestedRecipientInfoList:[],
            };
        },{
            compareDepth:{
                threadSuggestedRecipientInfoList:1,
            },
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

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickShowLess(ev){
        this.state.hasShowMoreButton=false;
    }

    /**
     *@private
     */
    _onClickShowMore(ev){
        this.state.hasShowMoreButton=true;
    }

}

Object.assign(ComposerSuggestedRecipientList,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.ComposerSuggestedRecipientList',
});

returnComposerSuggestedRecipientList;
});
