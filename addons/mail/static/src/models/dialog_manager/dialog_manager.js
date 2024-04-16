flectra.define('mail/static/src/models/dialog_manager/dialog_manager.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{one2many}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classDialogManagerextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@param{string}modelName
         *@param{Object}[recordData]
         */
        open(modelName,recordData){
            if(!modelName){
                thrownewError("Dialogshouldhavealinktoamodel");
            }
            constModel=this.env.models[modelName];
            if(!Model){
                thrownewError(`Nomodelexistswithname${modelName}`);
            }
            constrecord=Model.create(recordData);
            constdialog=this.env.models['mail.dialog'].create({
                manager:[['link',this]],
                record:[['link',record]],
            });
            returndialog;
        }

    }

    DialogManager.fields={
        //FIXME:dependentonimplementationthatusesinsertorderinrelations!!
        dialogs:one2many('mail.dialog',{
            inverse:'manager',
            isCausal:true,
        }),
    };

    DialogManager.modelName='mail.dialog_manager';

    returnDialogManager;
}

registerNewModel('mail.dialog_manager',factory);

});
