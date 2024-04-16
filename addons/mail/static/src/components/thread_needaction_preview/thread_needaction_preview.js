flectra.define('mail/static/src/components/thread_needaction_preview/thread_needaction_preview.js',function(require){
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

classThreadNeedactionPreviewextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            constmainThreadCache=thread?thread.mainCache:undefined;
            letlastNeedactionMessageAsOriginThreadAuthor;
            letlastNeedactionMessageAsOriginThread;
            letthreadCorrespondent;
            if(thread){
                lastNeedactionMessageAsOriginThread=mainThreadCache.lastNeedactionMessageAsOriginThread;
                threadCorrespondent=thread.correspondent;
            }
            if(lastNeedactionMessageAsOriginThread){
                lastNeedactionMessageAsOriginThreadAuthor=lastNeedactionMessageAsOriginThread.author;
            }
            return{
                isDeviceMobile:this.env.messaging.device.isMobile,
                lastNeedactionMessageAsOriginThread:lastNeedactionMessageAsOriginThread?lastNeedactionMessageAsOriginThread.__state:undefined,
                lastNeedactionMessageAsOriginThreadAuthor:lastNeedactionMessageAsOriginThreadAuthor
                    ?lastNeedactionMessageAsOriginThreadAuthor.__state
                    :undefined,
                thread:thread?thread.__state:undefined,
                threadCorrespondent:threadCorrespondent
                    ?threadCorrespondent.__state
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
        if(this.thread.moduleIcon){
            returnthis.thread.moduleIcon;
        }
        if(this.thread.correspondent){
            returnthis.thread.correspondent.avatarUrl;
        }
        if(this.thread.model==='mail.channel'){
            return`/web/image/mail.channel/${this.thread.id}/image_128`;
        }
        return'/mail/static/src/img/smiley/avatar.jpg';
    }

    /**
     *Getinlinecontentofthelastmessageofthisconversation.
     *
     *@returns{string}
     */
    getinlineLastNeedactionMessageBody(){
        if(!this.thread.lastNeedactionMessage){
            return'';
        }
        returnmailUtils.htmlToTextContentInline(this.thread.lastNeedactionMessage.prettyBody);
    }

    /**
     *Getinlinecontentofthelastmessageofthisconversation.
     *
     *@returns{string}
     */
    getinlineLastNeedactionMessageAsOriginThreadBody(){
        if(!this.thread.lastNeedactionMessageAsOriginThread){
            return'';
        }
        returnmailUtils.htmlToTextContentInline(this.thread.lastNeedactionMessageAsOriginThread.prettyBody);
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
        this.env.models['mail.message'].markAllAsRead([
            ['model','=',this.thread.model],
            ['res_id','=',this.thread.id],
        ]);
    }

}

Object.assign(ThreadNeedactionPreview,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.ThreadNeedactionPreview',
});

returnThreadNeedactionPreview;

});
