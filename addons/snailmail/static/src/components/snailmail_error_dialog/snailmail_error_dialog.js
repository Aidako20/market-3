flectra.define('snailmail/static/src/components/snailmail_error_dialog/snailmail_error_dialog.js',function(require){
'usestrict';

constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constDialog=require('web.OwlDialog');

const{Component}=owl;
const{useRef}=owl.hooks;

classSnailmailErrorDialogextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useStore(props=>{
            constmessage=this.env.models['mail.message'].get(props.messageLocalId);
            constnotifications=message?message.notifications:[];
            return{
                message:message?message.__state:undefined,
                notifications:notifications.map(notification=>
                    notification?notification.__state:undefined
                ),
                snailmail_credits_url:this.env.messaging.snailmail_credits_url,
                snailmail_credits_url_trial:this.env.messaging.snailmail_credits_url_trial,
            };
        },{
            compareDepth:{
                notifications:1,
            },
        });
        //tomanuallytriggerthedialogcloseevent
        this._dialogRef=useRef('dialog');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{boolean}
     */
    gethasCreditsError(){
        return(
            this.notification.failure_type==='sn_credit'||
            this.notification.failure_type==='sn_trial'
        );
    }

    /**
     *@returns{mail.message}
     */
    getmessage(){
        returnthis.env.models['mail.message'].get(this.props.messageLocalId);
    }

    /**
     *@returns{mail.notification}
     */
    getnotification(){
        //Messagesfromsnailmailareconsideredtohaveatmostonenotification.
        returnthis.message.notifications[0];
    }

    /**
     *@returns{string}
     */
    gettitle(){
        returnthis.env._t("Failedletter");
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickCancelLetter(){
        this._dialogRef.comp._close();
        this.message.cancelLetter();
    }

    /**
     *@private
     */
    _onClickClose(){
        this._dialogRef.comp._close();
    }

    /**
     *@private
     */
    _onClickResendLetter(){
        this._dialogRef.comp._close();
        this.message.resendLetter();
    }

}

Object.assign(SnailmailErrorDialog,{
    components:{Dialog},
    props:{
        messageLocalId:String,
    },
    template:'snailmail.SnailmailErrorDialog',
});

returnSnailmailErrorDialog;

});
