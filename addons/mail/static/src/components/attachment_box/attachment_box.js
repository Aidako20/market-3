flectra.define('mail/static/src/components/attachment_box/attachment_box.js',function(require){
'usestrict';

constcomponents={
    AttachmentList:require('mail/static/src/components/attachment_list/attachment_list.js'),
    DropZone:require('mail/static/src/components/drop_zone/drop_zone.js'),
    FileUploader:require('mail/static/src/components/file_uploader/file_uploader.js'),
};
constuseDragVisibleDropZone=require('mail/static/src/component_hooks/use_drag_visible_dropzone/use_drag_visible_dropzone.js');
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;
const{useRef}=owl.hooks;

classAttachmentBoxextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        this.isDropZoneVisible=useDragVisibleDropZone();
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            return{
                thread,
                threadAllAttachments:thread?thread.allAttachments:[],
                threadId:thread&&thread.id,
                threadModel:thread&&thread.model,
            };
        },{
            compareDepth:{
                threadAllAttachments:1,
            },
        });
        /**
         *Referenceofthefileuploader.
         *Usefultoprogrammaticallypromptsthebrowserfileuploader.
         */
        this._fileUploaderRef=useRef('fileUploader');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *GetanobjectwhichispassedtoFileUploadercomponenttobeusedwhen
     *creatingattachment.
     *
     *@returns{Object}
     */
    getnewAttachmentExtraData(){
        return{
            originThread:[['link',this.thread]],
        };
    }

    /**
     *@returns{mail.thread|undefined}
     */
    getthread(){
        returnthis.env.models['mail.thread'].get(this.props.threadLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onAttachmentCreated(ev){
        //FIXMECouldbechangedbyspyingattachmentscount(task-2252858)
        this.trigger('o-attachments-changed');
    }

    /**
     *@private
     *@param{Event}ev
     */
    _onAttachmentRemoved(ev){
        //FIXMECouldbechangedbyspyingattachmentscount(task-2252858)
        this.trigger('o-attachments-changed');
    }

    /**
     *@private
     *@param{Event}ev
     */
    _onClickAdd(ev){
        ev.preventDefault();
        ev.stopPropagation();
        this._fileUploaderRef.comp.openBrowserFileUploader();
    }

    /**
     *@private
     *@param{CustomEvent}ev
     *@param{Object}ev.detail
     *@param{FileList}ev.detail.files
     */
    async_onDropZoneFilesDropped(ev){
        ev.stopPropagation();
        awaitthis._fileUploaderRef.comp.uploadFiles(ev.detail.files);
        this.isDropZoneVisible.value=false;
    }

}

Object.assign(AttachmentBox,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.AttachmentBox',
});

returnAttachmentBox;

});
