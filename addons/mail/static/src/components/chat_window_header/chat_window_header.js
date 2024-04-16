flectra.define('mail/static/src/components/chat_window_header/chat_window_header.js',function(require){
'usestrict';

constcomponents={
    ThreadIcon:require('mail/static/src/components/thread_icon/thread_icon.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classChatWindowHeaderextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constchatWindow=this.env.models['mail.chat_window'].get(props.chatWindowLocalId);
            constthread=chatWindow&&chatWindow.thread;
            return{
                chatWindow,
                chatWindowHasShiftLeft:chatWindow&&chatWindow.hasShiftLeft,
                chatWindowHasShiftRight:chatWindow&&chatWindow.hasShiftRight,
                chatWindowName:chatWindow&&chatWindow.name,
                isDeviceMobile:this.env.messaging.device.isMobile,
                thread,
                threadLocalMessageUnreadCounter:thread&&thread.localMessageUnreadCounter,
                threadMassMailing:thread&&thread.mass_mailing,
                threadModel:thread&&thread.model,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.chat_window}
     */
    getchatWindow(){
        returnthis.env.models['mail.chat_window'].get(this.props.chatWindowLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        constchatWindow=this.chatWindow;
        this.trigger('o-clicked',{chatWindow});
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickClose(ev){
        ev.stopPropagation();
        if(!this.chatWindow){
            return;
        }
        this.chatWindow.close();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickExpand(ev){
        ev.stopPropagation();
        this.chatWindow.expand();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickShiftLeft(ev){
        ev.stopPropagation();
        if(this.props.saveThreadScrollTop){
            this.props.saveThreadScrollTop();
        }
        this.chatWindow.shiftLeft();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickShiftRight(ev){
        ev.stopPropagation();
        if(this.props.saveThreadScrollTop){
            this.props.saveThreadScrollTop();
        }
        this.chatWindow.shiftRight();
    }

}

Object.assign(ChatWindowHeader,{
    components,
    defaultProps:{
        hasCloseAsBackButton:false,
        isExpandable:false,
    },
    props:{
        chatWindowLocalId:String,
        hasCloseAsBackButton:Boolean,
        isExpandable:Boolean,
        saveThreadScrollTop:{
            type:Function,
            optional:true,
        },
    },
    template:'mail.ChatWindowHeader',
});

returnChatWindowHeader;

});
