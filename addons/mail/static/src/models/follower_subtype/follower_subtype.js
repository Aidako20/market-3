flectra.define('mail/static/src/models/follower_subtype/follower_subtype.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classFollowerSubtypeextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@static
         *@param{Object}data
         *@returns{Object}
         */
        staticconvertData(data){
            constdata2={};
            if('default'indata){
                data2.isDefault=data.default;
            }
            if('id'indata){
                data2.id=data.id;
            }
            if('internal'indata){
                data2.isInternal=data.internal;
            }
            if('name'indata){
                data2.name=data.name;
            }
            if('parent_model'indata){
                data2.parentModel=data.parent_model;
            }
            if('res_model'indata){
                data2.resModel=data.res_model;
            }
            if('sequence'indata){
                data2.sequence=data.sequence;
            }
            returndata2;
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@override
         */
        static_createRecordLocalId(data){
            return`${this.modelName}_${data.id}`;
        }

    }

    FollowerSubtype.fields={
        id:attr(),
        isDefault:attr({
            default:false,
        }),
        isInternal:attr({
            default:false,
        }),
        name:attr(),
        //AKUFIXME:userelationinstead
        parentModel:attr(),
        //AKUFIXME:userelationinstead
        resModel:attr(),
        sequence:attr(),
    };

    FollowerSubtype.modelName='mail.follower_subtype';

    returnFollowerSubtype;
}

registerNewModel('mail.follower_subtype',factory);

});
