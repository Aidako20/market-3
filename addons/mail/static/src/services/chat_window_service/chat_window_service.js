flectra.define('mail/static/src/services/chat_window_service/chat_window_service.js',function(require){
'usestrict';

constcomponents={
    ChatWindowManager:require('mail/static/src/components/chat_window_manager/chat_window_manager.js'),
};

constAbstractService=require('web.AbstractService');
const{bus,serviceRegistry}=require('web.core');

constChatWindowService=AbstractService.extend({
    /**
     *@override{web.AbstractService}
     */
    start(){
        this._super(...arguments);
        this._webClientReady=false;
        this._listenHomeMenu();
    },
    /**
     *@private
     */
    destroy(){
        if(this.component){
            this.component.destroy();
            this.component=undefined;
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@returns{Node}
     */
    _getParentNode(){
        returndocument.querySelector('body');
    },
    /**
     *@private
     */
    _listenHomeMenu(){
        bus.on('hide_home_menu',this,this._onHideHomeMenu.bind(this));
        bus.on('show_home_menu',this,this._onShowHomeMenu.bind(this));
        bus.on('web_client_ready',this,this._onWebClientReady.bind(this));
    },
    /**
     *@private
     */
    async_mount(){
        if(this.component){
            this.component.destroy();
            this.component=undefined;
        }
        constChatWindowManagerComponent=components.ChatWindowManager;
        this.component=newChatWindowManagerComponent(null);
        constparentNode=this._getParentNode();
        awaitthis.component.mount(parentNode);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    async_onHideHomeMenu(){
        if(!this._webClientReady){
            return;
        }
        if(document.querySelector('.o_ChatWindowManager')){
            return;
        }
        awaitthis._mount();
    },
    /**
     *@private
     */
    async_onShowHomeMenu(){
        if(!this._webClientReady){
            return;
        }
        if(document.querySelector('.o_ChatWindowManager')){
            return;
        }
        awaitthis._mount();
    },
    /**
     *@private
     */
    async_onWebClientReady(){
        awaitthis._mount();
        this._webClientReady=true;
    },
});

serviceRegistry.add('chat_window',ChatWindowService);

returnChatWindowService;

});
