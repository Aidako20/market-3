flectra.define('mail/static/src/components/notification_alert/notification_alert.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classNotificationAlertextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constisMessagingInitialized=this.env.isMessagingInitialized();
            return{
                isMessagingInitialized,
                isNotificationBlocked:this.isNotificationBlocked,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{boolean}
     */
    getisNotificationBlocked(){
        if(!this.env.isMessagingInitialized()){
            returnfalse;
        }
        constwindowNotification=this.env.browser.Notification;
        return(
            windowNotification&&
            windowNotification.permission!=="granted"&&
            !this.env.messaging.isNotificationPermissionDefault()
        );
    }

}

Object.assign(NotificationAlert,{
    props:{},
    template:'mail.NotificationAlert',
});

returnNotificationAlert;

});
