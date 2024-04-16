flectra.define('mail/static/src/widgets/messaging_menu/messaging_menu.js',function(require){
'usestrict';

constcomponents={
    MessagingMenu:require('mail/static/src/components/messaging_menu/messaging_menu.js'),
};

constSystrayMenu=require('web.SystrayMenu');
constWidget=require('web.Widget');

/**
 *FlectraWidget,necessarytoinstantiatecomponent.
 */
constMessagingMenu=Widget.extend({
    template:'mail.widgets.MessagingMenu',
    /**
     *@override
     */
    init(){
        this._super(...arguments);
        this.component=undefined;
    },
    /**
     *@override
     */
    destroy(){
        if(this.component){
            this.component.destroy();
        }
        this._super(...arguments);
    },
    asyncon_attach_callback(){
        constMessagingMenuComponent=components.MessagingMenu;
        this.component=newMessagingMenuComponent(null);
        awaitthis.component.mount(this.el);
        //unwrap
        this.el.parentNode.insertBefore(this.component.el,this.el);
        this.el.parentNode.removeChild(this.el);
    },
});

//Systraymenuitemsdisplayordermatchesorderinthelist
//lowerindexcomesfirst,anddisplayisfromrighttoleft.
//Formessaginmenu,itshouldcomebeforeactivitymenu,ifany
//otherwise,itisthenextsystrayitem.
constactivityMenuIndex=SystrayMenu.Items.findIndex(SystrayMenuItem=>
    SystrayMenuItem.prototype.name==='activity_menu');
if(activityMenuIndex>0){
    SystrayMenu.Items.splice(activityMenuIndex,0,MessagingMenu);
}else{
    SystrayMenu.Items.push(MessagingMenu);
}

returnMessagingMenu;

});
