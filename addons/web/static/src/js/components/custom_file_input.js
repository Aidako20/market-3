flectra.define('web.CustomFileInput',function(require){
    "usestrict";

    const{Component,hooks}=owl;
    const{useRef}=hooks;

    /**
     *Customfileinput
     *
     *Componentrepresentingacustomizedinputoftypefile.Ittakesasub-template
     *initsdefaultt-slotandusesitasthetriggertoopenthefileupload
     *prompt.
     *@extendsComponent
     */
    classCustomFileInputextendsComponent{
        /**
         *@param{Object}[props]
         *@param{string}[props.accepted_file_extensions='*']Comma-separated
         *     listofauthorizedfileextensions(defaulttoall).
         *@param{string}[props.action='/web/binary/upload']Routecalledwhen
         *     afileisuploadedintheinput.
         *@param{string}[props.id]
         *@param{string}[props.model]
         *@param{string}[props.multi_upload=false]Whethertheinputshouldallow
         *     touploadmultiplefilesatonce.
         */
        constructor(){
            super(...arguments);

            this.fileInputRef=useRef('file-input');
        }

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *Uploadanattachmenttothegivenactionwiththegivenparameters:
         *-ufile:listoffilescontainedinthefileinput
         *-csrf_token:CSRFtokenprovidedbytheflectraglobalobject
         *-model:aspecificmodelwhichwillbegivenwhencreatingtheattachment
         *-id:theidofthemodeltargetinstance
         *@private
         */
        async_onFileInputChange(){
            const{action,model,id}=this.props;
            constparams={
                csrf_token:flectra.csrf_token,
                ufile:[...this.fileInputRef.el.files],
            };
            if(model){
                params.model=model;
            }
            if(id){
                params.id=id;
            }
            constfileData=awaitthis.env.services.httpRequest(action,params,'text');
            constparsedFileData=JSON.parse(fileData);
            if(parsedFileData.error){
                thrownewError(parsedFileData.error);
            }
            this.trigger('uploaded',{files:parsedFileData});
        }

        /**
         *Redirectclicksfromthetriggerelementtotheinput.
         *@private
         */
        _onTriggerClicked(){
            this.fileInputRef.el.click();
        }
    }
    CustomFileInput.defaultProps={
        accepted_file_extensions:'*',
        action:'/web/binary/upload',
        multi_upload:false,
    };
    CustomFileInput.props={
        accepted_file_extensions:{type:String,optional:1},
        action:{type:String,optional:1},
        id:{type:Number,optional:1},
        model:{type:String,optional:1},
        multi_upload:{type:Boolean,optional:1},
    };
    CustomFileInput.template='web.CustomFileInput';

    returnCustomFileInput;
});
