flectra.define('mail/static/src/components/notification_request/notification_request.js',function(require){
'usestrict';

constcomponents={
    PartnerImStatusIcon:require('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classNotificationRequestextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            return{
                isDeviceMobile:this.env.messaging.device.isMobile,
                partnerRoot:this.env.messaging.partnerRoot
                    ?this.env.messaging.partnerRoot.__state
                    :undefined,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{string}
     */
    getHeaderText(){
        return_.str.sprintf(
            this.env._t("%shasarequest"),
            this.env.messaging.partnerRoot.nameOrDisplayName
        );
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Handletheresponseoftheuserwhenpromptedwhetherpushnotifications
     *aregrantedordenied.
     *
     *@private
     *@param{string}value
     */
    _handleResponseNotificationPermission(value){
        //manuallyforcerecomputebecausethepermissionisnotinthestore
        this.env.messaging.messagingMenu.update();
        if(value!=='granted'){
            this.env.services['bus_service'].sendNotification(
                this.env._t("Permissiondenied"),
                this.env._t("Flectrawillnothavethepermissiontosendnativenotificationsonthisdevice.")
            );
        }
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClick(){
        constwindowNotification=this.env.browser.Notification;
        constdef=windowNotification&&windowNotification.requestPermission();
        if(def){
            def.then(this._handleResponseNotificationPermission.bind(this));
        }
        if(!this.env.messaging.device.isMobile){
            this.env.messaging.messagingMenu.close();
        }
    }

}

Object.assign(NotificationRequest,{
    components,
    props:{},
    template:'mail.NotificationRequest',
});

returnNotificationRequest;

});
