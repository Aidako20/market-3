flectra.define('mail/static/src/models/suggested_recipient_info/suggested_recipient_info.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,many2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classSuggestedRecipientInfoextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //private
        //----------------------------------------------------------------------

        /**
         *@private
         *@returns{string}
         */
        _computeEmail(){
            returnthis.partner&&this.partner.email||this.email;
        }

        /**
         *Preventsselectingarecipientthatdoesnothaveapartner.
         *
         *@private
         *@returns{boolean}
         */
        _computeIsSelected(){
            returnthis.partner?this.isSelected:false;
        }

        /**
         *@private
         *@returns{string}
         */
        _computeName(){
            returnthis.partner&&this.partner.nameOrDisplayName||this.name;
        }

    }

    SuggestedRecipientInfo.fields={
        /**
         *Determinestheemailof`this`.Itservesasvisualcluewhen
         *displaying`this`,andalsoservesasdefaultpartneremailwhen
         *creatinganewpartnerfrom`this`.
         */
        email:attr({
            compute:'_computeEmail',
            dependencies:[
                'email',
                'partnerEmail',
            ],
        }),
        /**
         *Determineswhether`this`willbeaddedtorecipientswhenpostinga
         *newmessageon`this.thread`.
         */
        isSelected:attr({
            compute:'_computeIsSelected',
            default:true,
            dependencies:[
                'isSelected',
                'partner',
            ],
        }),
        /**
         *Determinesthenameof`this`.Itservesasvisualcluewhen
         *displaying`this`,andalsoservesasdefaultpartnernamewhen
         *creatinganewpartnerfrom`this`.
         */
        name:attr({
            compute:'_computeName',
            dependencies:[
                'name',
                'partnerNameOrDisplayName',
            ],
        }),
        /**
         *Determinestheoptional`mail.partner`associatedto`this`.
         */
        partner:many2one('mail.partner'),
        /**
         *Servesascomputedependency.
         */
        partnerEmail:attr({
            related:'partner.email'
        }),
        /**
         *Servesascomputedependency.
         */
        partnerNameOrDisplayName:attr({
            related:'partner.nameOrDisplayName'
        }),
        /**
         *Determineswhy`this`isasuggestionfor`this.thread`.Itservesas
         *visualcluewhendisplaying`this`.
         */
        reason:attr(),
        /**
         *Determinesthe`mail.thread`concernedby`this.`
         */
        thread:many2one('mail.thread',{
            inverse:'suggestedRecipientInfoList',
        }),
    };

    SuggestedRecipientInfo.modelName='mail.suggested_recipient_info';

    returnSuggestedRecipientInfo;
}

registerNewModel('mail.suggested_recipient_info',factory);

});
