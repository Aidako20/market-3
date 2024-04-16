flectra.define('mail/static/src/components/composer_suggested_recipient/composer_suggested_recipient.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
constuseUpdate=require('mail/static/src/component_hooks/use_update/use_update.js');

const{FormViewDialog}=require('web.view_dialogs');
const{ComponentAdapter}=require('web.OwlCompatibility');
constsession=require('web.session');

const{Component}=owl;
const{useRef}=owl.hooks;

classFormViewDialogComponentAdapterextendsComponentAdapter{

    renderWidget(){
        //Ensurethedialogisproperlyreconstructed.Withoutthisline,itis
        //impossibletoopenthedialogagainafterhavingitclosedafirst
        //time,becausetheDOMofthedialoghasdisappeared.
        returnthis.willStart();
    }

}

constcomponents={
    FormViewDialogComponentAdapter,
};

classComposerSuggestedRecipientextendsComponent{

    constructor(...args){
        super(...args);
        this.id=_.uniqueId('o_ComposerSuggestedRecipient_');
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constsuggestedRecipientInfo=this.env.models['mail.suggested_recipient_info'].get(props.suggestedRecipientLocalId);
            constpartner=suggestedRecipientInfo&&suggestedRecipientInfo.partner;
            return{
                partner:partner&&partner.__state,
                suggestedRecipientInfo:suggestedRecipientInfo&&suggestedRecipientInfo.__state,
            };
        });
        useUpdate({func:()=>this._update()});
        /**
         *Formviewdialogclass.Usefultoreferenceitinthetemplate.
         */
        this.FormViewDialog=FormViewDialog;
        /**
         *Referenceofthecheckbox.Usefultoknowwhetheritwascheckedor
         *not,toproperlyupdatethecorrespondingstateintherecordorto
         *prompttheuserwiththepartnercreationdialog.
         */
        this._checkboxRef=useRef('checkbox');
        /**
         *Referenceofthepartnercreationdialog.Usefultoopenit,for
         *compatibilitywitholdcode.
         */
        this._dialogRef=useRef('dialog');
        /**
         *Whetherthedialogiscurrentlyopen.`_dialogRef`cannotbetrusted
         *toknowifthedialogisopenduetomanuallycalling`open`and
         *potentialoutofsyncwithcomponentadapter.
         */
        this._isDialogOpen=false;
        this._onDialogSaved=this._onDialogSaved.bind(this);
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{string|undefined}
     */
    getADD_AS_RECIPIENT_AND_FOLLOWER_REASON(){
        if(!this.suggestedRecipientInfo){
            returnundefined;
        }
        returnthis.env._t(_.str.sprintf(
            "Addasrecipientandfollower(reason:%s)",
            this.suggestedRecipientInfo.reason
        ));
    }

    /**
     *@returns{string}
     */
    getPLEASE_COMPLETE_CUSTOMER_S_INFORMATION(){
        returnthis.env._t("Pleasecompletecustomer'sinformation");
    }

    /**
     *@returns{mail.suggested_recipient_info}
     */
    getsuggestedRecipientInfo(){
        returnthis.env.models['mail.suggested_recipient_info'].get(this.props.suggestedRecipientInfoLocalId);
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _update(){
        if(this._checkboxRef.el&&this.suggestedRecipientInfo){
            this._checkboxRef.el.checked=this.suggestedRecipientInfo.isSelected;
        }
    }

    //--------------------------------------------------------------------------
    //Handler
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onChangeCheckbox(){
        constisChecked=this._checkboxRef.el.checked;
        this.suggestedRecipientInfo.update({isSelected:isChecked});
        if(!this.suggestedRecipientInfo.partner){
            //Recipientsmustalwaysbepartners.Onselectingasuggested
            //recipientthatdoesnothaveapartner,thepartnercreationform
            //shouldbeopened.
            if(isChecked&&this._dialogRef&&!this._isDialogOpen){
                constwidget=this._dialogRef.comp.widget;
                this._isDialogOpen=true;
                widget.on('closed',this,()=>{
                    this._isDialogOpen=false;
                    this._checkboxRef.el.checked=!!this.suggestedRecipientInfo.partner;
                });
                widget.context=Object.assign({},widget.context,session.user_context)
                widget.open();
            }
        }
    }

    /**
     *@private
     */
    _onDialogSaved(){
        constthread=this.suggestedRecipientInfo&&this.suggestedRecipientInfo.thread;
        if(!thread){
            return;
        }
        thread.fetchAndUpdateSuggestedRecipients();
    }
}

Object.assign(ComposerSuggestedRecipient,{
    components,
    props:{
        suggestedRecipientInfoLocalId:String,
    },
    template:'mail.ComposerSuggestedRecipient',
});

returnComposerSuggestedRecipient;

});
