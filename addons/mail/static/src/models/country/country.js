flectra.define('mail/static/src/models/country/country.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');
const{clear}=require('mail/static/src/model/model_field_command.js');

functionfactory(dependencies){

    classCountryextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@override
         */
        static_createRecordLocalId(data){
            return`${this.modelName}_${data.id}`;
        }

        /**
         *@private
         *@returns{string|undefined}
         */
        _computeFlagUrl(){
            if(!this.code){
                returnclear();
            }
            return`/base/static/img/country_flags/${this.code}.png`;
        }

    }

    Country.fields={
        code:attr(),
        flagUrl:attr({
            compute:'_computeFlagUrl',
            dependencies:[
                'code',
            ],
        }),
        id:attr(),
        name:attr(),
    };

    Country.modelName='mail.country';

    returnCountry;
}

registerNewModel('mail.country',factory);

});
