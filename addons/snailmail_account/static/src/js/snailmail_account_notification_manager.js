flectra.define('snailmail_account.NotificationManager',function(require){
"usestrict";

varAbstractService=require('web.AbstractService');
varcore=require("web.core");

varSnailmailAccountNotificationManager= AbstractService.extend({
    dependencies:['bus_service'],

    /**
     *@override
     */
    start:function(){
        this._super.apply(this,arguments);
        this.call('bus_service','onNotification',this,this._onNotification);
    },

    _onNotification:function(notifs){
        varself=this;
        _.each(notifs,function(notif){
            varmodel=notif[0][1];
            vartype=notif[1].type;
            if(model==='res.partner'&&type==='snailmail_invalid_address'){
                self.do_warn(notif[1].title, notif[1].message);
            }
        });
    }

});

core.serviceRegistry.add('snailmail_account_notification_service',SnailmailAccountNotificationManager);

returnSnailmailAccountNotificationManager;

});
