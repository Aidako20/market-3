flectra.define('im_livechat/static/src/components/notification_list/notification_list.js',function(require){
'usestrict';

constcomponents={
    NotificationList:require('mail/static/src/components/notification_list/notification_list.js'),
};

const{patch}=require('web.utils');

components.NotificationList._allowedFilters.push('livechat');

patch(components.NotificationList,'im_livechat/static/src/components/notification_list/notification_list.js',{

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Overridetoincludelivechatchannels.
     *
     *@override
     */
    _useStoreSelectorThreads(props){
        if(props.filter==='livechat'){
            returnthis.env.models['mail.thread'].all(thread=>
                thread.channel_type==='livechat'&&
                thread.isPinned&&
                thread.model==='mail.channel'
            );
        }
        returnthis._super(...arguments);
    },

});

});
