flectra.define('mail/static/src/models/dialog/dialog.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{many2one,one2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classDialogextendsdependencies['mail.model']{}

    Dialog.fields={
        manager:many2one('mail.dialog_manager',{
            inverse:'dialogs',
        }),
        /**
         *Contentofdialogthatisdirectlylinkedtoarecordthatmodels
         *aUIcomponent,suchasAttachmentViewer.Theserecordsmustbe
         *createdfrom@see`mail.dialog_manager:open()`.
         */
        record:one2one('mail.model',{
            isCausal:true,
        }),
    };

    Dialog.modelName='mail.dialog';

    returnDialog;
}

registerNewModel('mail.dialog',factory);

});
