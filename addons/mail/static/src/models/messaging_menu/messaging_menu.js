flectra.define('mail/static/src/models/messaging_menu/messaging_menu.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,one2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classMessagingMenuextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *Closethemessagingmenu.Shouldresetitsinternalstate.
         */
        close(){
            this.update({isOpen:false});
        }

        /**
         *Togglethevisibilityofthemessagingmenu"newmessage"inputin
         *mobile.
         */
        toggleMobileNewMessage(){
            this.update({isMobileNewMessageToggled:!this.isMobileNewMessageToggled});
        }

        /**
         *Togglewhetherthemessagingmenuisopenornot.
         */
        toggleOpen(){
            this.update({isOpen:!this.isOpen});
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@private
         */
        _computeInboxMessagesAutoloader(){
            if(!this.isOpen){
                return;
            }
            constinbox=this.env.messaging.inbox;
            if(!inbox||!inbox.mainCache){
                return;
            }
            //populatesomeneedactionmessagesonthreads.
            inbox.mainCache.update({isCacheRefreshRequested:true});
        }

        /**
         *@private
         *@returns{integer}
         */
        _updateCounter(){
            if(!this.env.messaging){
                return0;
            }
            constinboxMailbox=this.env.messaging.inbox;
            constunreadChannels=this.env.models['mail.thread'].all(thread=>
                thread.displayCounter>0&&
                thread.model==='mail.channel'&&
                thread.isPinned
            );
            letcounter=unreadChannels.length;
            if(inboxMailbox){
                counter+=inboxMailbox.counter;
            }
            if(this.messaging.notificationGroupManager){
                counter+=this.messaging.notificationGroupManager.groups.reduce(
                    (total,group)=>total+group.notifications.length,
                    0
                );
            }
            if(this.messaging.isNotificationPermissionDefault()){
                counter++;
            }
            returncounter;
        }

        /**
         *@override
         */
        _updateAfter(previous){
            constcounter=this._updateCounter();
            if(this.counter!==counter){
                this.update({counter});
            }
        }

    }

    MessagingMenu.fields={
        /**
         *Tabselectedinthemessagingmenu.
         *Either'all','chat'or'channel'.
         */
        activeTabId:attr({
            default:'all',
        }),
        counter:attr({
            default:0,
        }),
        /**
         *Dummyfieldtoautomaticallyloadmessagesofinboxwhenmessaging
         *menuisopen.
         *
         *Usefulbecauseneedactionnotificationsrequirefetchinginbox
         *messagestowork.
         */
        inboxMessagesAutoloader:attr({
            compute:'_computeInboxMessagesAutoloader',
            dependencies:[
                'isOpen',
                'messagingInbox',
                'messagingInboxMainCache',
            ],
        }),
        /**
         *Determinewhetherthemobilenewmessageinputisvisibleornot.
         */
        isMobileNewMessageToggled:attr({
            default:false,
        }),
        /**
         *Determinewhetherthemessagingmenudropdownisopenornot.
         */
        isOpen:attr({
            default:false,
        }),
        messaging:one2one('mail.messaging',{
            inverse:'messagingMenu',
        }),
        messagingInbox:one2one('mail.thread',{
            related:'messaging.inbox',
        }),
        messagingInboxMainCache:one2one('mail.thread_cache',{
            related:'messagingInbox.mainCache',
        }),
    };

    MessagingMenu.modelName='mail.messaging_menu';

    returnMessagingMenu;
}

registerNewModel('mail.messaging_menu',factory);

});
