flectra.define('mail/static/src/models/notification/notification.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,many2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classNotificationextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@static
         *@param{Object}data
         *@return{Object}
         */
        staticconvertData(data){
            constdata2={};
            if('failure_type'indata){
                data2.failure_type=data.failure_type;
            }
            if('id'indata){
                data2.id=data.id;
            }
            if('notification_status'indata){
                data2.notification_status=data.notification_status;
            }
            if('notification_type'indata){
                data2.notification_type=data.notification_type;
            }
            if('res_partner_id'indata){
                if(!data.res_partner_id){
                    data2.partner=[['unlink-all']];
                }else{
                    data2.partner=[
                        ['insert',{
                            display_name:data.res_partner_id[1],
                            id:data.res_partner_id[0],
                        }],
                    ];
                }
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

    Notification.fields={
        failure_type:attr(),
        id:attr(),
        message:many2one('mail.message',{
            inverse:'notifications',
        }),
        notification_status:attr(),
        notification_type:attr(),
        partner:many2one('mail.partner'),
    };

    Notification.modelName='mail.notification';

    returnNotification;
}

registerNewModel('mail.notification',factory);

});
