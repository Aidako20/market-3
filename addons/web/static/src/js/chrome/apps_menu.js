flectra.define('web.AppsMenu',function(require){
"usestrict";

varWidget=require('web.Widget');

varAppsMenu=Widget.extend({
    template:'AppsMenu',
    events:{
        'click.o_app':'_onAppsMenuItemClicked',
    },
    /**
     *@override
     *@param{web.Widget}parent
     *@param{Object}menuData
     *@param{Object[]}menuData.children
     */
    init:function(parent,menuData){
        this._super.apply(this,arguments);
        this._activeApp=undefined;
        this._apps=_.map(menuData.children,function(appMenuData){
            return{
                actionID:parseInt(appMenuData.action.split(',')[1]),
                menuID:appMenuData.id,
                name:appMenuData.name,
                xmlID:appMenuData.xmlid,
            };
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{Object[]}
     */
    getApps:function(){
        returnthis._apps;
    },
    /**
     *Openthefirstappinthelistofapps.Returnswhetheronewasfound.
     *
     *@returns{Boolean}
     */
    openFirstApp:function(){
        if(!this._apps.length){
            returnfalse;
        }
        varfirstApp=this._apps[0];
        this._openApp(firstApp);
        returntrue;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}app
     */
    _openApp:function(app){
        this._setActiveApp(app);
        this.trigger_up('app_clicked',{
            action_id:app.actionID,
            menu_id:app.menuID,
        });
    },
    /**
     *@private
     *@param{Object}app
     */
    _setActiveApp:function(app){
        var$oldActiveApp=this.$('.o_app.active');
        $oldActiveApp.removeClass('active');
        var$newActiveApp=this.$('.o_app[data-action-id="'+app.actionID+'"]');
        $newActiveApp.addClass('active');
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenclickingonanitemintheappsmenu.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onAppsMenuItemClicked:function(ev){
        var$target=$(ev.currentTarget);
        varactionID=$target.data('action-id');
        varmenuID=$target.data('menu-id');
        varapp=_.findWhere(this._apps,{actionID:actionID,menuID:menuID});
        this._openApp(app);
    },

});

returnAppsMenu;

});
