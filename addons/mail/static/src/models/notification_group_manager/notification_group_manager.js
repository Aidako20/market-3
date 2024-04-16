flectra.define('mail/static/src/models/notification_group_manager/notification_group_manager.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{one2many}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classNotificationGroupManagerextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        computeGroups(){
            for(constgroupofthis.groups){
                group.delete();
            }
            constgroups=[];
            //TODObatchinsert,betterlogictask-2258605
            this.env.messaging.currentPartner.failureNotifications.forEach(notification=>{
                constthread=notification.message.originThread;
                //Notificationsaregroupedbymodelandnotification_type.
                //Exceptforchannelwheretheyarealsogroupedbyidbecause
                //wewanttoopentheactualchannelindiscussorchatwindow
                //andnotitskanban/list/formview.
                constchannelId=thread.model==='mail.channel'?thread.id:null;
                constid=`${thread.model}/${channelId}/${notification.notification_type}`;
                constgroup=this.env.models['mail.notification_group'].insert({
                    id,
                    notification_type:notification.notification_type,
                    res_model:thread.model,
                    res_model_name:thread.model_name,
                });
                group.update({notifications:[['link',notification]]});
                //avoidlinkingthesamegrouptwicewhenaddinganotification
                //toanexistinggroup
                if(!groups.includes(group)){
                    groups.push(group);
                }
            });
            this.update({groups:[['link',groups]]});
        }

    }

    NotificationGroupManager.fields={
        groups:one2many('mail.notification_group'),
    };

    NotificationGroupManager.modelName='mail.notification_group_manager';

    returnNotificationGroupManager;
}

registerNewModel('mail.notification_group_manager',factory);

});
