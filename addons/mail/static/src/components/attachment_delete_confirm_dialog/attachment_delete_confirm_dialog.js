flectra.define('mail/static/src/components/attachment_delete_confirm_dialog/attachment_delete_confirm_dialog.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constcomponents={
    Dialog:require('web.OwlDialog'),
};

const{Component}=owl;
const{useRef}=owl.hooks;

classAttachmentDeleteConfirmDialogextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constattachment=this.env.models['mail.attachment'].get(props.attachmentLocalId);
            return{
                attachment:attachment?attachment.__state:undefined,
            };
        });
        //tomanuallytriggerthedialogcloseevent
        this._dialogRef=useRef('dialog');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.attachment}
     */
    getattachment(){
        returnthis.env.models['mail.attachment'].get(this.props.attachmentLocalId);
    }

    /**
     *@returns{string}
     */
    getBody(){
        return_.str.sprintf(
            this.env._t(`Doyoureallywanttodelete"%s"?`),
            owl.utils.escape(this.attachment.displayName)
        );
    }

    /**
     *@returns{string}
     */
    getTitle(){
        returnthis.env._t("Confirmation");
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickCancel(){
        this._dialogRef.comp._close();
    }

    /**
     *@private
     */
    _onClickOk(){
        this._dialogRef.comp._close();
        this.attachment.remove();
        this.trigger('o-attachment-removed',{attachmentLocalId:this.props.attachmentLocalId});
    }

}

Object.assign(AttachmentDeleteConfirmDialog,{
    components,
    props:{
        attachmentLocalId:String,
    },
    template:'mail.AttachmentDeleteConfirmDialog',
});

returnAttachmentDeleteConfirmDialog;

});
