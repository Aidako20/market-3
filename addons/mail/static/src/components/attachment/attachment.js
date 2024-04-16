flectra.define('mail/static/src/components/attachment/attachment.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constcomponents={
    AttachmentDeleteConfirmDialog:require('mail/static/src/components/attachment_delete_confirm_dialog/attachment_delete_confirm_dialog.js'),
};

const{Component,useState}=owl;

classAttachmentextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth:{
                attachmentLocalIds:1,
            },
        });
        useStore(props=>{
            constattachment=this.env.models['mail.attachment'].get(props.attachmentLocalId);
            return{
                attachment:attachment?attachment.__state:undefined,
            };
        });
        this.state=useState({
            hasDeleteConfirmDialog:false,
        });
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
     *Returntheurloftheattachment.Temporaryattachments,a.k.a.uploading
     *attachments,donothaveanurl.
     *
     *@returns{string}
     */
    getattachmentUrl(){
        if(this.attachment.isTemporary){
            return'';
        }
        returnthis.env.session.url('/web/content',{
            id:this.attachment.id,
            download:true,
        });
    }

    /**
     *Getthedetailsmodeafterautomodeiscomputed
     *
     *@returns{string}'card','hover'or'none'
     */
    getdetailsMode(){
        if(this.props.detailsMode!=='auto'){
            returnthis.props.detailsMode;
        }
        if(this.attachment.fileType!=='image'){
            return'card';
        }
        return'hover';
    }

    /**
     *Gettheattachmentrepresentationstyletobeapplied
     *
     *@returns{string}
     */
    getimageStyle(){
        if(this.attachment.fileType!=='image'){
            return'';
        }
        if(this.env.isQUnitTest){
            //background-image:urlishardlymockable,andattachmentsin
            //QUnittestsdonotactuallyexistinDB,sostyleshouldnot
            //befetchedatall.
            return'';
        }
        letsize;
        if(this.detailsMode==='card'){
            size='38x38';
        }else{
            //Thesizeofbackground-imagedependsontheprops.imageSize
            //tosyncwithwidthandheightof`.o_Attachment_image`.
            if(this.props.imageSize==="large"){
                size='400x400';
            }elseif(this.props.imageSize==="medium"){
                size='200x200';
            }elseif(this.props.imageSize==="small"){
                size='100x100';
            }
        }
        //background-sizesettooverridevaluefrom`o_image`whichmakessmallimagestretched
        return`background-image:url(/web/image/${this.attachment.id}/${size});background-size:auto;`;
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Downloadtheattachmentwhenclickingondonwloadicon.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickDownload(ev){
        ev.stopPropagation();
        window.location=`/web/content/ir.attachment/${this.attachment.id}/datas?download=true`;
    }

    /**
     *Opentheattachmentviewerwhenclickingonviewableattachment.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickImage(ev){
        if(!this.attachment.isViewable){
            return;
        }
        this.env.models['mail.attachment'].view({
            attachment:this.attachment,
            attachments:this.props.attachmentLocalIds.map(
                attachmentLocalId=>this.env.models['mail.attachment'].get(attachmentLocalId)
            ),
        });
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickUnlink(ev){
        ev.stopPropagation();
        if(!this.attachment){
            return;
        }
        if(this.attachment.isLinkedToComposer){
            this.attachment.remove();
            this.trigger('o-attachment-removed',{attachmentLocalId:this.props.attachmentLocalId});
        }else{
            this.state.hasDeleteConfirmDialog=true;
        }
    }

   /**
    *@private
    */
    _onDeleteConfirmDialogClosed(){
        this.state.hasDeleteConfirmDialog=false;
    }
}

Object.assign(Attachment,{
    components,
    defaultProps:{
        attachmentLocalIds:[],
        detailsMode:'auto',
        imageSize:'medium',
        isDownloadable:false,
        isEditable:true,
        showExtension:true,
        showFilename:true,
    },
    props:{
        attachmentLocalId:String,
        attachmentLocalIds:{
            type:Array,
            element:String,
        },
        detailsMode:{
            type:String,
            validate:prop=>['auto','card','hover','none'].includes(prop),
        },
        imageSize:{
            type:String,
            validate:prop=>['small','medium','large'].includes(prop),
        },
        isDownloadable:Boolean,
        isEditable:Boolean,
        showExtension:Boolean,
        showFilename:Boolean,
    },
    template:'mail.Attachment',
});

returnAttachment;

});
