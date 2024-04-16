flectra.define('mail/static/src/components/chatter/chatter.js',function(require){
'usestrict';

constcomponents={
    ActivityBox:require('mail/static/src/components/activity_box/activity_box.js'),
    AttachmentBox:require('mail/static/src/components/attachment_box/attachment_box.js'),
    ChatterTopbar:require('mail/static/src/components/chatter_topbar/chatter_topbar.js'),
    Composer:require('mail/static/src/components/composer/composer.js'),
    ThreadView:require('mail/static/src/components/thread_view/thread_view.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
constuseUpdate=require('mail/static/src/component_hooks/use_update/use_update.js');

const{Component}=owl;
const{useRef}=owl.hooks;

classChatterextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constchatter=this.env.models['mail.chatter'].get(props.chatterLocalId);
            constthread=chatter?chatter.thread:undefined;
            letattachments=[];
            if(thread){
                attachments=thread.allAttachments;
            }
            return{
                attachments:attachments.map(attachment=>attachment.__state),
                chatter:chatter?chatter.__state:undefined,
                composer:thread&&thread.composer,
                thread,
                threadActivitiesLength:thread&&thread.activities.length,
            };
        },{
            compareDepth:{
                attachments:1,
            },
        });
        useUpdate({func:()=>this._update()});
        /**
         *Referenceofthecomposer.Usefultofocusit.
         */
        this._composerRef=useRef('composer');
        /**
         *ReferenceofthescrollPanel(Realscrollelement).UsefultopasstheScrollelementto
         *childcomponenttohandleproperscrollableelement.
         */
        this._scrollPanelRef=useRef('scrollPanel');
        /**
         *Referenceofthemessagelist.Usefultotriggerthescrolleventonit.
         */
        this._threadRef=useRef('thread');
        this.getScrollableElement=this.getScrollableElement.bind(this);
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.chatter}
     */
    getchatter(){
        returnthis.env.models['mail.chatter'].get(this.props.chatterLocalId);
    }

    /**
     *@returns{Element|undefined}ScrollableElement
     */
    getScrollableElement(){
        if(!this._scrollPanelRef.el){
            return;
        }
        returnthis._scrollPanelRef.el;
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _notifyRendered(){
        this.trigger('o-chatter-rendered',{
            attachments:this.chatter.thread.allAttachments,
            thread:this.chatter.thread.localId,
        });
    }

    /**
     *@private
     */
    _update(){
        if(!this.chatter){
            return;
        }
        if(this.chatter.thread){
            this._notifyRendered();
        }
        if(this.chatter.isDoFocus){
            this.chatter.update({isDoFocus:false});
            constcomposer=this._composerRef.comp;
            if(composer){
                composer.focus();
            }
        }
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onComposerMessagePosted(){
        this.chatter.update({isComposerVisible:false});
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onScrollPanelScroll(ev){
        if(!this._threadRef.comp){
            return;
        }
        this._threadRef.comp.onScroll(ev);
    }

}

Object.assign(Chatter,{
    components,
    props:{
        chatterLocalId:String,
    },
    template:'mail.Chatter',
});

returnChatter;

});
