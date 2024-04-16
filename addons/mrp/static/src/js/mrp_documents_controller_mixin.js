flectra.define('mrp.controllerMixin',function(require){
'usestrict';

const{_t,qweb}=require('web.core');
constfileUploadMixin=require('web.fileUploadMixin');
constDocumentViewer=require('mrp.MrpDocumentViewer');

constMrpDocumentsControllerMixin=Object.assign({},fileUploadMixin,{
    events:{
        'click.o_mrp_documents_kanban_upload':'_onClickMrpDocumentsUpload',
    },
    custom_events:Object.assign({},fileUploadMixin.custom_events,{
        kanban_image_clicked:'_onKanbanPreview',
        upload_file:'_onUploadFile',
    }),

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Calledrightafterthereloadoftheview.
     */
    asyncreload(){
        awaitthis._renderFileUploads();
    },

    /**
     *@override
     *@param{jQueryElement}$node
     */
    renderButtons($node){
        this.$buttons=$(qweb.render('MrpDocumentsKanbanView.buttons'));
        this.$buttons.appendTo($node);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _getFileUploadRoute(){
        return'/mrp/upload_attachment';
    },

    /**
     *@override
     *@param{integer}param0.recordId
     */
    _makeFileUploadFormDataKeys(){
        constcontext=this.model.get(this.handle,{raw:true}).getContext();
        return{
            res_id:context.default_res_id,
            res_model:context.default_res_model,
        };
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickMrpDocumentsUpload(){
        const$uploadInput=$('<input>',{
            type:'file',
            name:'files[]',
            multiple:'multiple'
        });
        $uploadInput.on('change',asyncev=>{
            awaitthis._uploadFiles(ev.target.files);
            $uploadInput.remove();
        });
        $uploadInput.click();
    },

    /**
     *Handlescustomeventtodisplaythedocumentviewer.
     *
     *@private
     *@param{FlectraEvent}ev
     *@param{integer}ev.data.recordID
     *@param{Array<Object>}ev.data.recordList
     */
    _onKanbanPreview(ev){
        ev.stopPropagation();
        constdocuments=ev.data.recordList;
        constdocumentID=ev.data.recordID;
        constdocumentViewer=newDocumentViewer(this,documents,documentID);
        documentViewer.appendTo(this.$('.o_mrp_documents_kanban_view'));
    },

    /**
     *Speciallycreatedtocall`_uploadFiles`methodfromtests.
     *
     *@private
     *@param{FlectraEvent}ev
     */
    async_onUploadFile(ev){
        awaitthis._uploadFiles(ev.data.files);
    },

    /**
     *@override
     *@param{Object}param0
     *@param{XMLHttpRequest}param0.xhr
     */
    _onUploadLoad({xhr}){
        constresult=xhr.status===200
            ?JSON.parse(xhr.response)
            :{
                error:_.str.sprintf(_t("statuscode:%s</br>message:%s"),xhr.status,xhr.response)
            };
        if(result.error){
            this.do_notify(_t("Error"),result.error,true);
        }
        fileUploadMixin._onUploadLoad.apply(this,arguments);
    },
});

returnMrpDocumentsControllerMixin;

});
