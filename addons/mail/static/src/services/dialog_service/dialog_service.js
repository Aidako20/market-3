flectra.define('mail/static/src/services/dialog_service/dialog_service.js',function(require){
'usestrict';

constcomponents={
    DialogManager:require('mail/static/src/components/dialog_manager/dialog_manager.js'),
};

constAbstractService=require('web.AbstractService');
const{bus,serviceRegistry}=require('web.core');

constDialogService=AbstractService.extend({
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
        constDialogManagerComponent=components.DialogManager;
        this.component=newDialogManagerComponent(null);
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
        if(document.querySelector('.o_DialogManager')){
            return;
        }
        awaitthis._mount();
    },
    async_onShowHomeMenu(){
        if(!this._webClientReady){
            return;
        }
        if(document.querySelector('.o_DialogManager')){
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
    }
});

serviceRegistry.add('dialog',DialogService);

returnDialogService;

});
