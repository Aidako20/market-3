flectra.define('mail/static/src/components/moderation_discard_dialog/moderation_discard_dialog.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constcomponents={
    Dialog:require('web.OwlDialog'),
};

const{Component}=owl;
const{useRef}=owl.hooks;

classModerationDiscardDialogextendsComponent{

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
     *@returns{string}
     */
    getBody(){
        if(this.messages.length===1){
            returnthis.env._t("Youaregoingtodiscard1message.");
        }
        return_.str.sprintf(
            this.env._t("Youaregoingtodiscard%smessages."),
            this.messages.length
        );
    }

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
    getTitle(){
        returnthis.env._t("Confirmation");
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
    _onClickDiscard(){
        this._dialogRef.comp._close();
        this.env.models['mail.message'].moderate(this.messages,'discard');
    }

}

Object.assign(ModerationDiscardDialog,{
    components,
    props:{
        messageLocalIds:{
            type:Array,
            element:String,
        },
    },
    template:'mail.ModerationDiscardDialog',
});

returnModerationDiscardDialog;

});
