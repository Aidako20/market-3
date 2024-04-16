flectra.define('mail/static/src/components/notification_popover/notification_popover.js',function(require){
'usestrict';

const{Component}=owl;
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

classNotificationPopoverextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth:{
                notificationLocalIds:1,
            },
        });
        useStore(props=>{
            constnotifications=props.notificationLocalIds.map(
                notificationLocalId=>this.env.models['mail.notification'].get(notificationLocalId)
            );
            return{
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
            case'bounce':
                return'fafa-exclamation';
            case'exception':
                return'fafa-exclamation';
            case'ready':
                return'fafa-send-o';
            case'canceled':
                return'fafa-trash-o';
        }
        return'';
    }

    /**
     *@returns{string}
     */
    geticonTitle(){
        switch(this.notification.notification_status){
            case'sent':
                returnthis.env._t("Sent");
            case'bounce':
                returnthis.env._t("Bounced");
            case'exception':
                returnthis.env._t("Error");
            case'ready':
                returnthis.env._t("Ready");
            case'canceled':
                returnthis.env._t("Canceled");
        }
        return'';
    }

    /**
     *@returns{mail.notification[]}
     */
    getnotifications(){
        returnthis.props.notificationLocalIds.map(
            notificationLocalId=>this.env.models['mail.notification'].get(notificationLocalId)
        );
    }

}

Object.assign(NotificationPopover,{
    props:{
        notificationLocalIds:{
            type:Array,
            element:String,
        },
    },
    template:'mail.NotificationPopover',
});

returnNotificationPopover;

});
