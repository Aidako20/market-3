flectra.define('web.QuickCreateFormView',function(require){
"usestrict";

/**
 *ThisfiledefinestheQuickCreateFormView,anextensionoftheFormViewthat
 *isusedbytheRecordQuickCreateinKanbanviews.
 */

varBasicModel=require('web.BasicModel');
varFormController=require('web.FormController');
varFormRenderer=require('web.FormRenderer');
varFormView=require('web.FormView');
const{qweb}=require("web.core");

varQuickCreateFormRenderer=FormRenderer.extend({
    /**
     *@override
     */
    start:asyncfunction(){
        awaitthis._super.apply(this,arguments);
        this.$el.addClass('o_xxs_form_view');
        this.$el.removeClass('o_xxl_form_view');
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Overridetodonothingsothattherendererwon'tresizeonwindowresize
     *
     *@override
     */
    _applyFormSizeClass(){},

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     *@param{FlectraEvent}ev
     */
    _onNavigationMove:function(ev){
        vardirection=ev.data.direction;
        if(direction==='cancel'||direction==='next_line'){
            ev.stopPropagation();
            this.trigger_up(direction==='cancel'?'cancel':'add');
        }else{
            this._super.apply(this,arguments);
        }
    },
});

varQuickCreateFormModel=BasicModel.extend({
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{Object}thechangesofthegivenresource(servercommandsfor
     *  x2manys)
     */
    getChanges:function(localID){
        varrecord=this.localData[localID];
        returnthis._generateChanges(record,{changesOnly:false});
    },
});

varQuickCreateFormController=FormController.extend({
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Asksallfieldwidgetstonotifytheenvironmentwiththeircurrentvalue
     *(usefulforinstanceforinputfieldsthatstillhavethefocusandthat
     *couldhavenotnotifiedtheenvironmentoftheirchangesyet).
     *Synchronizeswiththecontroller'smutexincasetherewouldalreadybe
     *pendingchangesbeingapplied.
     *
     *@return{Promise}
     */
    commitChanges:function(){
        varmutexDef=this.mutex.getUnlockedDef();
        returnPromise.all([mutexDef,this.renderer.commitChanges(this.handle)]);
    },
    /**
     *@returns{Object}thechangesdoneonthecurrentrecord
     */
    getChanges:function(){
        returnthis.model.getChanges(this.handle);
    },

    /**
     *@override
     */
    renderButtons($node){
        this.$buttons=$(qweb.render('KanbanView.RecordQuickCreate.buttons'));
        if($node){
            this.$buttons.appendTo($node);
        }
    },

    /**
     *@override
     */
    updateButtons(){/*Noneedtoupdatethebuttons*/},
});

varQuickCreateFormView=FormView.extend({
    withControlPanel:false,
    config:_.extend({},FormView.prototype.config,{
        Model:QuickCreateFormModel,
        Renderer:QuickCreateFormRenderer,
        Controller:QuickCreateFormController,
    }),
});

returnQuickCreateFormView;

});
