flectra.define('snailmail/static/src/components/snailmail_notification_popover/snailmail_notification_popover.js',function(require){
'usestrict';

const{Component}=owl;
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

classSnailmailNotificationPopoverextendsComponent{

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
                notifications:notifications.map(notification=>notification?notification.__state:undefined),
            };
        },{
            compareDepth:{
                notifications:1,
            },
        });
    }

    /**
     *@returns{string}
     */
    geticonClass(){
        switch(this.notification.notification_status){
            case'sent':
                return'fafa-check';
            case'ready':
                return'fafa-clock-o';
            case'canceled':
                return'fafa-trash-o';
            default:
                return'fafa-exclamationtext-danger';
        }
    }

    /**
     *@returns{string}
     */
    geticonTitle(){
        switch(this.notification.notification_status){
            case'sent':
                returnthis.env._t("Sent");
            case'ready':
                returnthis.env._t("AwaitingDispatch");
            case'canceled':
                returnthis.env._t("Canceled");
            default:
                returnthis.env._t("Error");
        }
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

}

Object.assign(SnailmailNotificationPopover,{
    props:{
        messageLocalId:String,
    },
    template:'snailmail.SnailmailNotificationPopover',
});

returnSnailmailNotificationPopover;

});
