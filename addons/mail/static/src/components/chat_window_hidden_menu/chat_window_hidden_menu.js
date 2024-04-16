flectra.define('mail/static/src/components/chat_window_hidden_menu/chat_window_hidden_menu.js',function(require){
'usestrict';

constcomponents={
    ChatWindowHeader:require('mail/static/src/components/chat_window_header/chat_window_header.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;
const{useRef}=owl.hooks;

classChatWindowHiddenMenuextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useStore(props=>{
            constchatWindowManager=this.env.messaging.chatWindowManager;
            constdevice=this.env.messaging.device;
            constlocale=this.env.messaging.locale;
            return{
                chatWindowManager:chatWindowManager?chatWindowManager.__state:undefined,
                device:device?device.__state:undefined,
                localeTextDirection:locale?locale.textDirection:undefined,
            };
        });
        this._onClickCaptureGlobal=this._onClickCaptureGlobal.bind(this);
        /**
         *Referenceofthedropuplist.Usefultoauto-setmaxheightbasedon
         *browserscreenheight.
         */
        this._listRef=useRef('list');
        /**
         *Theintentofthetogglebuttondependsonthelastrenderedstate.
         */
        this._wasMenuOpen;
    }

    mounted(){
        this._apply();
        document.addEventListener('click',this._onClickCaptureGlobal,true);
    }

    patched(){
        this._apply();
    }

    willUnmount(){
        document.removeEventListener('click',this._onClickCaptureGlobal,true);
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _apply(){
        this._applyListHeight();
        this._applyOffset();
        this._wasMenuOpen=this.env.messaging.chatWindowManager.isHiddenMenuOpen;
    }

    /**
     *@private
     */
    _applyListHeight(){
        constdevice=this.env.messaging.device;
        constheight=device.globalWindowInnerHeight/2;
        this._listRef.el.style['max-height']=`${height}px`;
    }

    /**
     *@private
     */
    _applyOffset(){
        consttextDirection=this.env.messaging.locale.textDirection;
        constoffsetFrom=textDirection==='rtl'?'left':'right';
        constoppositeFrom=offsetFrom==='right'?'left':'right';
        constoffset=this.env.messaging.chatWindowManager.visual.hidden.offset;
        this.el.style[offsetFrom]=`${offset}px`;
        this.el.style[oppositeFrom]='auto';
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Closesthemenuwhenclickingoutside.
     *Mustbedoneascapturetoavoidstoppropagation.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickCaptureGlobal(ev){
        if(this.el.contains(ev.target)){
            return;
        }
        this.env.messaging.chatWindowManager.closeHiddenMenu();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickToggle(ev){
        if(this._wasMenuOpen){
            this.env.messaging.chatWindowManager.closeHiddenMenu();
        }else{
            this.env.messaging.chatWindowManager.openHiddenMenu();
        }
    }

    /**
     *@private
     *@param{CustomEvent}ev
     *@param{Object}ev.detail
     *@param{mail.chat_window}ev.detail.chatWindow
     */
    _onClickedChatWindow(ev){
        constchatWindow=ev.detail.chatWindow;
        chatWindow.makeActive();
        this.env.messaging.chatWindowManager.closeHiddenMenu();
    }

}

Object.assign(ChatWindowHiddenMenu,{
    components,
    props:{},
    template:'mail.ChatWindowHiddenMenu',
});

returnChatWindowHiddenMenu;

});
