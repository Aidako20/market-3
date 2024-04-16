flectra.define('mail/static/src/components/messaging_menu/messaging_menu.js',function(require){
'usestrict';

constcomponents={
    AutocompleteInput:require('mail/static/src/components/autocomplete_input/autocomplete_input.js'),
    MobileMessagingNavbar:require('mail/static/src/components/mobile_messaging_navbar/mobile_messaging_navbar.js'),
    NotificationList:require('mail/static/src/components/notification_list/notification_list.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constpatchMixin=require('web.patchMixin');

const{Component}=owl;

classMessagingMenuextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        /**
         *globalJSgeneratedIDforthiscomponent.Usefultoprovidea
         *customclasstoautocompleteinput,sothatclickinanautocomplete
         *itemisnotconsideredasaclickawayfrommessagingmenuinmobile.
         */
        this.id=_.uniqueId('o_messagingMenu_');
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            return{
                isDeviceMobile:this.env.messaging&&this.env.messaging.device.isMobile,
                isDiscussOpen:this.env.messaging&&this.env.messaging.discuss.isOpen,
                isMessagingInitialized:this.env.isMessagingInitialized(),
                messagingMenu:this.env.messaging&&this.env.messaging.messagingMenu.__state,
            };
        });

        //bindsincepassedasprops
        this._onMobileNewMessageInputSelect=this._onMobileNewMessageInputSelect.bind(this);
        this._onMobileNewMessageInputSource=this._onMobileNewMessageInputSource.bind(this);
        this._onClickCaptureGlobal=this._onClickCaptureGlobal.bind(this);
        this._constructor(...args);
    }

    /**
     *Allowspatchingconstructor.
     */
    _constructor(){}

    mounted(){
        document.addEventListener('click',this._onClickCaptureGlobal,true);
    }

    willUnmount(){
        document.removeEventListener('click',this._onClickCaptureGlobal,true);
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.discuss}
     */
    getdiscuss(){
        returnthis.env.messaging&&this.env.messaging.discuss;
    }

    /**
     *@returns{mail.messaging_menu}
     */
    getmessagingMenu(){
        returnthis.env.messaging&&this.env.messaging.messagingMenu;
    }

    /**
     *@returns{string}
     */
    getmobileNewMessageInputPlaceholder(){
        returnthis.env._t("Searchuser...");
    }

    /**
     *@returns{Object[]}
     */
    gettabs(){
        return[{
            icon:'fafa-envelope',
            id:'all',
            label:this.env._t("All"),
        },{
            icon:'fafa-user',
            id:'chat',
            label:this.env._t("Chat"),
        },{
            icon:'fafa-users',
            id:'channel',
            label:this.env._t("Channel"),
        }];
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Closesthemenuwhenclickingoutside,ifappropriate.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickCaptureGlobal(ev){
        if(!this.env.messaging){
            /**
             *Messagingnotcreated,whichmeansessentialmodelslike
             *messagingmenuarenotready,souserinteractionsareomitted
             *duringthis(short)periodoftime.
             */
            return;
        }
        //ignoreclickinsidethemenu
        if(this.el.contains(ev.target)){
            return;
        }
        //inallothercases:closethemessagingmenuwhenclickingoutside
        this.messagingMenu.close();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickDesktopTabButton(ev){
        this.messagingMenu.update({activeTabId:ev.currentTarget.dataset.tabId});
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickNewMessage(ev){
        if(!this.env.messaging.device.isMobile){
            this.env.messaging.chatWindowManager.openNewMessage();
            this.messagingMenu.close();
        }else{
            this.messagingMenu.toggleMobileNewMessage();
        }
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickToggler(ev){
        //avoidfollowingdummyhref
        ev.preventDefault();
        if(!this.env.messaging){
            /**
             *Messagingnotcreated,whichmeansessentialmodelslike
             *messagingmenuarenotready,souserinteractionsareomitted
             *duringthis(short)periodoftime.
             */
            return;
        }
        this.messagingMenu.toggleOpen();
    }

    /**
     *@private
     *@param{CustomEvent}ev
     */
    _onHideMobileNewMessage(ev){
        ev.stopPropagation();
        this.messagingMenu.toggleMobileNewMessage();
    }

    /**
     *@private
     *@param{Event}ev
     *@param{Object}ui
     *@param{Object}ui.item
     *@param{integer}ui.item.id
     */
    _onMobileNewMessageInputSelect(ev,ui){
        this.env.messaging.openChat({partnerId:ui.item.id});
    }

    /**
     *@private
     *@param{Object}req
     *@param{string}req.term
     *@param{function}res
     */
    _onMobileNewMessageInputSource(req,res){
        constvalue=_.escape(req.term);
        this.env.models['mail.partner'].imSearch({
            callback:partners=>{
                constsuggestions=partners.map(partner=>{
                    return{
                        id:partner.id,
                        value:partner.nameOrDisplayName,
                        label:partner.nameOrDisplayName,
                    };
                });
                res(_.sortBy(suggestions,'label'));
            },
            keyword:value,
            limit:10,
        });
    }

    /**
     *@private
     *@param{CustomEvent}ev
     *@param{Object}ev.detail
     *@param{string}ev.detail.tabId
     */
    _onSelectMobileNavbarTab(ev){
        ev.stopPropagation();
        this.messagingMenu.update({activeTabId:ev.detail.tabId});
    }

}

Object.assign(MessagingMenu,{
    components,
    props:{},
    template:'mail.MessagingMenu',
});

returnpatchMixin(MessagingMenu);

});
