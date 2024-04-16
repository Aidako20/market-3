flectra.define('hr/static/src/models/employee/employee.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,one2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classEmployeeextendsdependencies['mail.model']{

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
            if('id'indata){
                data2.id=data.id;
            }
            if('user_id'indata){
                data2.hasCheckedUser=true;
                if(!data.user_id){
                    data2.user=[['unlink']];
                }else{
                    constpartnerNameGet=data['user_partner_id'];
                    constpartnerData={
                        display_name:partnerNameGet[1],
                        id:partnerNameGet[0],
                    };
                    constuserNameGet=data['user_id'];
                    constuserData={
                        id:userNameGet[0],
                        partner:[['insert',partnerData]],
                        display_name:userNameGet[1],
                    };
                    data2.user=[['insert',userData]];
                }
            }
            returndata2;
        }

        /**
         *Performsthe`read`RPConthe`hr.employee.public`.
         *
         *@static
         *@param{Object}param0
         *@param{Object}param0.context
         *@param{string[]}param0.fields
         *@param{integer[]}param0.ids
         */
        staticasyncperformRpcRead({context,fields,ids}){
            constemployeesData=awaitthis.env.services.rpc({
                model:'hr.employee.public',
                method:'read',
                args:[ids,fields],
                kwargs:{
                    context,
                },
            });
            this.env.models['hr.employee'].insert(employeesData.map(employeeData=>
                this.env.models['hr.employee'].convertData(employeeData)
            ));
        }

        /**
         *Performsthe`search_read`RPCon`hr.employee.public`.
         *
         *@static
         *@param{Object}param0
         *@param{Object}param0.context
         *@param{Array[]}param0.domain
         *@param{string[]}param0.fields
         */
        staticasyncperformRpcSearchRead({context,domain,fields}){
            constemployeesData=awaitthis.env.services.rpc({
                model:'hr.employee.public',
                method:'search_read',
                kwargs:{
                    context,
                    domain,
                    fields,
                },
            });
            this.env.models['hr.employee'].insert(employeesData.map(employeeData=>
                this.env.models['hr.employee'].convertData(employeeData)
            ));
        }

        /**
         *Checkswhetherthisemployeehasarelateduserandpartnerandlinks
         *themifapplicable.
         */
        asynccheckIsUser(){
            returnthis.env.models['hr.employee'].performRpcRead({
                ids:[this.id],
                fields:['user_id','user_partner_id'],
                context:{active_test:false},
            });
        }

        /**
         *Getsthechatbetweentheuserofthisemployeeandthecurrentuser.
         *
         *Ifachatisnotappropriate,anotificationisdisplayedinstead.
         *
         *@returns{mail.thread|undefined}
         */
        asyncgetChat(){
            if(!this.user&&!this.hasCheckedUser){
                awaitthis.async(()=>this.checkIsUser());
            }
            //preventchattingwithnon-users
            if(!this.user){
                this.env.services['notification'].notify({
                    message:this.env._t("Youcanonlychatwithemployeesthathaveadedicateduser."),
                    type:'info',
                });
                return;
            }
            returnthis.user.getChat();
        }

        /**
         *Opensachatbetweentheuserofthisemployeeandthecurrentuser
         *andreturnsit.
         *
         *Ifachatisnotappropriate,anotificationisdisplayedinstead.
         *
         *@param{Object}[options]forwardedto@see`mail.thread:open()`
         *@returns{mail.thread|undefined}
         */
        asyncopenChat(options){
            constchat=awaitthis.async(()=>this.getChat());
            if(!chat){
                return;
            }
            awaitthis.async(()=>chat.open(options));
            returnchat;
        }

        /**
         *Opensthemostappropriateviewthatisaprofileforthisemployee.
         */
        asyncopenProfile(model='hr.employee.public'){
            returnthis.env.messaging.openDocument({
                id:this.id,
                model:model,
            });
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

    Employee.fields={
        /**
         *Whetheranattemptwasalreadymadetofetchtheusercorresponding
         *tothisemployee.ThispreventsdoingthesameRPCmultipletimes.
         */
        hasCheckedUser:attr({
            default:false,
        }),
        /**
         *Uniqueidentifierforthisemployee.
         */
        id:attr(),
        /**
         *Partnerrelatedtothisemployee.
         */
        partner:one2one('mail.partner',{
            inverse:'employee',
            related:'user.partner',
        }),
        /**
         *Userrelatedtothisemployee.
         */
        user:one2one('mail.user',{
            inverse:'employee',
        }),
    };

    Employee.modelName='hr.employee';

    returnEmployee;
}

registerNewModel('hr.employee',factory);

});
