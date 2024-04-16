flectra.define('snailmail/static/src/components/message/message.js',function(require){
'usestrict';

constcomponents={
    Message:require('mail/static/src/components/message/message.js'),
    SnailmailErrorDialog:require('snailmail/static/src/components/snailmail_error_dialog/snailmail_error_dialog.js'),
    SnailmailNotificationPopover:require('snailmail/static/src/components/snailmail_notification_popover/snailmail_notification_popover.js'),
};

const{patch}=require('web.utils');

const{useState}=owl;

Object.assign(components.Message.components,{
    SnailmailErrorDialog:components.SnailmailErrorDialog,
    SnailmailNotificationPopover:components.SnailmailNotificationPopover,
});

patch(components.Message,'snailmail/static/src/components/message/message.js',{
    /**
     *@override
     */
    _constructor(){
        this._super(...arguments);
        this.snailmailState=useState({
            //Determineiftheerrordialogisdisplayed.
            hasDialog:false,
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _onClickFailure(){
        if(this.message.message_type==='snailmail'){
            /**
             *Messagesfromsnailmailareconsideredtohaveatmostone
             *notification.Thefailuretypeofthewholemessageisconsidered
             *tobethesameastheonefromthatfirstnotification,andthe
             *clickactionwilldependonit.
             */
            switch(this.message.notifications[0].failure_type){
                case'sn_credit':
                    //URLonlyusedinthiscomponent,notreceivedatinit
                    this.env.messaging.fetchSnailmailCreditsUrl();
                    this.snailmailState.hasDialog=true;
                    break;
                case'sn_error':
                    this.snailmailState.hasDialog=true;
                    break;
                case'sn_fields':
                    this.message.openMissingFieldsLetterAction();
                    break;
                case'sn_format':
                    this.message.openFormatLetterAction();
                    break;
                case'sn_price':
                    this.snailmailState.hasDialog=true;
                    break;
                case'sn_trial':
                    //URLonlyusedinthiscomponent,notreceivedatinit
                    this.env.messaging.fetchSnailmailCreditsUrlTrial();
                    this.snailmailState.hasDialog=true;
                    break;
            }
        }else{
            this._super(...arguments);
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onDialogClosedSnailmailError(){
        this.snailmailState.hasDialog=false;
    },
});

});
