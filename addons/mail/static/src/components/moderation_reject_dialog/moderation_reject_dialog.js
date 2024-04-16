flectra.define('mail/static/src/components/moderation_reject_dialog/moderation_reject_dialog.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constcomponents={
    Dialog:require('web.OwlDialog'),
};

const{Component,useState}=owl;
const{useRef}=owl.hooks;

classModerationRejectDialogextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth:{
                messageLocalIds:1,
            },
        });
        this.state=useState({
            title:this.env._t("MessageRejected"),
            comment:this.env._t("Yourmessagewasrejectedbymoderator."),
        });
        useStore(props=>{
            constmessages=props.messageLocalIds.map(localId=>
                this.env.models['mail.message'].get(localId)
            );
            return{
                messages:messages.map(message=>message?message.__state:undefined),
            };
        },{
            compareDepth:{
                messages:1,
            },
        });
        //tomanuallytriggerthedialogcloseevent
        this._dialogRef=useRef('dialog');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.message[]}
     */
    getmessages(){
        returnthis.props.messageLocalIds.map(localId=>
            this.env.models['mail.message'].get(localId)
        );
    }

    /**
     *@returns{string}
     */
    getSEND_EXPLANATION_TO_AUTHOR(){
        returnthis.env._t("Sendexplanationtoauthor");
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickCancel(){
        this._dialogRef.comp._close();
    }

    /**
     *@private
     */
    _onClickReject(){
        this._dialogRef.comp._close();
        constkwargs={
            title:this.state.title,
            comment:this.state.comment,
        };
        this.env.models['mail.message'].moderate(this.messages,'reject',kwargs);
    }

}

Object.assign(ModerationRejectDialog,{
    components,
    props:{
        messageLocalIds:{
            type:Array,
            element:String,
        },
    },
    template:'mail.ModerationRejectDialog',
});

returnModerationRejectDialog;

});
