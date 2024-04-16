flectra.define('mail/static/src/components/dialog_manager/dialog_manager.js',function(require){
'usestrict';

constcomponents={
    Dialog:require('mail/static/src/components/dialog/dialog.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classDialogManagerextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constdialogManager=this.env.messaging&&this.env.messaging.dialogManager;
            return{
                dialogManager:dialogManager?dialogManager.__state:undefined,
            };
        });
    }

    mounted(){
        this._checkDialogOpen();
    }

    patched(){
        this._checkDialogOpen();
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _checkDialogOpen(){
        if(!this.env.messaging){
            /**
             *Messagingnotcreated,whichmeansessentialmodelslike
             *dialogmanagerarenotready,soopenstatusofdialoginDOM
             *isomittedduringthis(short)periodoftime.
             */
            return;
        }
        if(this.env.messaging.dialogManager.dialogs.length>0){
            document.body.classList.add('modal-open');
        }else{
            document.body.classList.remove('modal-open');
        }
    }

}

Object.assign(DialogManager,{
    components,
    props:{},
    template:'mail.DialogManager',
});

returnDialogManager;

});
