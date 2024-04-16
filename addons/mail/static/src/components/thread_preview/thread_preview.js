flectra.define('mail/static/src/components/thread_preview/thread_preview.js',function(require){
'usestrict';

constcomponents={
    MessageAuthorPrefix:require('mail/static/src/components/message_author_prefix/message_author_prefix.js'),
    PartnerImStatusIcon:require('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
constmailUtils=require('mail.utils');

const{Component}=owl;
const{useRef}=owl.hooks;

classThreadPreviewextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            letlastMessageAuthor;
            letlastMessage;
            if(thread){
                constorderedMessages=thread.orderedMessages;
                lastMessage=orderedMessages[orderedMessages.length-1];
            }
            if(lastMessage){
                lastMessageAuthor=lastMessage.author;
            }
            return{
                isDeviceMobile:this.env.messaging.device.isMobile,
                lastMessage:lastMessage?lastMessage.__state:undefined,
                lastMessageAuthor:lastMessageAuthor
                    ?lastMessageAuthor.__state
                    :undefined,
                thread:thread?thread.__state:undefined,
                threadCorrespondent:thread&&thread.correspondent
                    ?thread.correspondent.__state
                    :undefined,
            };
        });
        /**
         *Referenceofthe"markasread"button.Usefultodisablethe
         *top-levelclickhandlerwhenclickingonthisspecificbutton.
         */
        this._markAsReadRef=useRef('markAsRead');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Gettheimagerouteofthethread.
     *
     *@returns{string}
     */
    image(){
        if(this.thread.correspondent){
            returnthis.thread.correspondent.avatarUrl;
        }
        return`/web/image/mail.channel/${this.thread.id}/image_128`;
    }

    /**
     *Getinlinecontentofthelastmessageofthisconversation.
     *
     *@returns{string}
     */
    getinlineLastMessageBody(){
        if(!this.thread.lastMessage){
            return'';
        }
        returnmailUtils.htmlToTextContentInline(this.thread.lastMessage.prettyBody);
    }

    /**
     *@returns{mail.thread}
     */
    getthread(){
        returnthis.env.models['mail.thread'].get(this.props.threadLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        constmarkAsRead=this._markAsReadRef.el;
        if(markAsRead&&markAsRead.contains(ev.target)){
            //handledin`_onClickMarkAsRead`
            return;
        }
        this.thread.open();
        if(!this.env.messaging.device.isMobile){
            this.env.messaging.messagingMenu.close();
        }
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickMarkAsRead(ev){
        if(this.thread.lastNonTransientMessage){
            this.thread.markAsSeen(this.thread.lastNonTransientMessage);
        }
    }

}

Object.assign(ThreadPreview,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.ThreadPreview',
});

returnThreadPreview;

});
