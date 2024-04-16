flectra.define('mail/static/src/widgets/notification_alert/notification_alert.js',function(require){
"usestrict";

constcomponents={
    NotificationAlert:require('mail/static/src/components/notification_alert/notification_alert.js'),
};

const{ComponentWrapper,WidgetAdapterMixin}=require('web.OwlCompatibility');

constWidget=require('web.Widget');
constwidgetRegistry=require('web.widget_registry');

classNotificationAlertWrapperextendsComponentWrapper{}

//-----------------------------------------------------------------------------
//DisplayNotificationalertonuserpreferencesformview
//-----------------------------------------------------------------------------
constNotificationAlert=Widget.extend(WidgetAdapterMixin,{
    /**
     *@override
     */
    init(){
        this._super(...arguments);
        this.component=undefined;
    },
    /**
     *@override
     */
    asyncstart(){
        awaitthis._super(...arguments);

        this.component=newNotificationAlertWrapper(
            this,
            components.NotificationAlert,
            {}
        );
        awaitthis.component.mount(this.el);
    },
});

widgetRegistry.add('notification_alert',NotificationAlert);

returnNotificationAlert;

});
