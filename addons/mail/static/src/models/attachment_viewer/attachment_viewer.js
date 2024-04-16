flectra.define('mail/static/src/models/attachment_viewer/attachment_viewer.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,many2many,many2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classAttachmentViewerextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *Closetheattachmentviewerbyclosingitslinkeddialog.
         */
        close(){
            constdialog=this.env.models['mail.dialog'].find(dialog=>dialog.record===this);
            if(dialog){
                dialog.delete();
            }
        }
    }

    AttachmentViewer.fields={
        /**
         *Angleoftheimage.Changeswhentheuserrotatesit.
         */
        angle:attr({
            default:0,
        }),
        attachment:many2one('mail.attachment'),
        attachments:many2many('mail.attachment',{
            inverse:'attachmentViewer',
        }),
        /**
         *Determinewhethertheimageisloadingornot.Usefultodiplay
         *aspinnerwhenloadingimageinitially.
         */
        isImageLoading:attr({
            default:false,
        }),
        /**
         *Scalesizeoftheimage.Changeswhenuserzoomsin/out.
         */
        scale:attr({
            default:1,
        }),
    };

    AttachmentViewer.modelName='mail.attachment_viewer';

    returnAttachmentViewer;
}

registerNewModel('mail.attachment_viewer',factory);

});
