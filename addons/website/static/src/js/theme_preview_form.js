flectra.define('website.theme_preview_form',function(require){
"usestrict";

varFormController=require('web.FormController');
varFormView=require('web.FormView');
varviewRegistry=require('web.view_registry');
varcore=require('web.core');
varqweb=core.qweb;

/*
*Commoncodeforthemeinstallation/updatehandler.
*/
constThemePreviewControllerCommon={
    /**
     *Calledtoaddloadingeffectandinstall/pdatetheselectedthemedependingonaction.
     *
     *@private
     *@param{number}res_id
     *@param{String}action
     */
    _handleThemeAction(res_id,action){
        this.$loader=$(qweb.render('website.ThemePreview.Loader',{
            'showTips':action!=='button_refresh_theme',
        }));
        letactionCallback=undefined;
        this._addLoader();
        switch(action){
            case'button_choose_theme':
                actionCallback=result=>this.do_action(result);
                break;
            case'button_refresh_theme':
                actionCallback=()=>this._removeLoader();
                break;
        }
        constrpcData={
            model:'ir.module.module',
            method:action,
            args:[res_id],
            context:this.initialState.context,
        };
        constrpcOptions={
            shadow:true,
        };
        this._rpc(rpcData,rpcOptions)
            .then(actionCallback)
            .guardedCatch(()=>this._removeLoader());
    },
    /**
     *CalledtoaddloaderelementinDOM.
     *
     *@private
     */
    _addLoader(){
        $('body').append(this.$loader);
    },
    /**
     *@private
     */
    _removeLoader(){
        this.$loader.remove();
    }
};

varThemePreviewController=FormController.extend(ThemePreviewControllerCommon,{
    events:Object.assign({},FormController.prototype.events,{
        'click.o_use_theme':'_onStartNowClick',
        'click.o_switch_theme':'_onSwitchThemeClick',
        'changeinput[name="viewer"]':'_onSwitchButtonChange',
    }),
    /**
     *@override
     */
    start:function(){
        this.$el.addClass('o_view_form_theme_preview_controller');
        returnthis._super.apply(this,arguments);
    },

    //-------------------------------------------------------------------------
    //Public
    //-------------------------------------------------------------------------

    /**
     *@override
     */
    renderButtons:function($node){
        this.$buttons=$(qweb.render('website.ThemePreview.Buttons'));
        if($node){
            $node.html(this.$buttons);
        }
    },
    /**
     *Overridentopreventthecontrollerfromhidingthebuttons
     *@seeFormController
     *
     *@override
     */
    updateButtons:function(){},

    //-------------------------------------------------------------------------
    //Private
    //-------------------------------------------------------------------------
    /**
     *AddSwitcherViewMobile/Desktopnearpager
     *
     *@private
     */
    _updateControlPanelProps:asyncfunction(){
        constprops=this._super(...arguments);
        const$switchModeButton=$(qweb.render('website.ThemePreview.SwitchModeButton'));
        this.controlPanelProps.cp_content.$pager=$switchModeButton;
        returnprops;
    },

    //-------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------
    /**
     *Handlercalledwhenuserclickon'Desktop/Mobile'switcherbutton.
     *
     *@private
     */
    _onSwitchButtonChange:function(){
        this.$('.o_preview_frame').toggleClass('is_mobile');
    },
    /**
     *Handlercalledwhenuserclickon'Chooseanothertheme'button.
     *
     *@private
     */
    _onSwitchThemeClick:function(){
        this.trigger_up('history_back');
    },
    /**
     *Handlercalledwhenuserclickon'STARTNOW'buttoninformview.
     *
     *@private
     */
    _onStartNowClick:function(){
        this._handleThemeAction(this.getSelectedIds()[0],'button_choose_theme');
    },
});

varThemePreviewFormView=FormView.extend({
    config:_.extend({},FormView.prototype.config,{
        Controller:ThemePreviewController
    }),
});

viewRegistry.add('theme_preview_form',ThemePreviewFormView);

return{
    ThemePreviewControllerCommon:ThemePreviewControllerCommon
}
});
