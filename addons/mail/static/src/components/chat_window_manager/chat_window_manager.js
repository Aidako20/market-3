flectra.define('mail/static/src/components/chat_window_manager/chat_window_manager.js',function(require){
'usestrict';

constcomponents={
    ChatWindow:require('mail/static/src/components/chat_window/chat_window.js'),
    ChatWindowHiddenMenu:require('mail/static/src/components/chat_window_hidden_menu/chat_window_hidden_menu.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classChatWindowManagerextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constchatWindowManager=this.env.messaging&&this.env.messaging.chatWindowManager;
            constallOrderedVisible=chatWindowManager
                ?chatWindowManager.allOrderedVisible
                :[];
            return{
                allOrderedVisible,
                allOrderedVisibleThread:allOrderedVisible.map(chatWindow=>chatWindow.thread),
                chatWindowManager,
                chatWindowManagerHasHiddenChatWindows:chatWindowManager&&chatWindowManager.hasHiddenChatWindows,
                isMessagingInitialized:this.env.isMessagingInitialized(),
            };
        },{
            compareDepth:{
                allOrderedVisible:1,
                allOrderedVisibleThread:1,
            },
        });
    }

}

Object.assign(ChatWindowManager,{
    components,
    props:{},
    template:'mail.ChatWindowManager',
});

returnChatWindowManager;

});
