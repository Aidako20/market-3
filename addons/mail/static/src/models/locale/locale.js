flectra.define('mail/static/src/models/locale/locale.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classLocaleextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@private
         *@returns{string}
         */
        _computeLanguage(){
            returnthis.env._t.database.parameters.code;
        }

        /**
         *@private
         *@returns{string}
         */
        _computeTextDirection(){
            returnthis.env._t.database.parameters.direction;
        }

    }

    Locale.fields={
        /**
         *Languageusedbyinterface,formattedlike{languageISO2}_{countryISO2}(eg:fr_FR).
         */
        language:attr({
            compute:'_computeLanguage',
        }),
        textDirection:attr({
            compute:'_computeTextDirection',
        }),
    };

    Locale.modelName='mail.locale';

    returnLocale;
}

registerNewModel('mail.locale',factory);

});
