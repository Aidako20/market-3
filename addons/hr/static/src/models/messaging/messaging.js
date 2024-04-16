flectra.define('hr/static/src/models/messaging/messaging.js',function(require){
'usestrict';

const{
    registerInstancePatchModel,
}=require('mail/static/src/model/model_core.js');

registerInstancePatchModel('mail.messaging','hr/static/src/models/messaging/messaging.js',{
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     *@param{integer}[param0.employeeId]
     */
    asyncgetChat({employeeId}){
        if(employeeId){
            constemployee=this.env.models['hr.employee'].insert({id:employeeId});
            returnemployee.getChat();
        }
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    asyncopenProfile({id,model}){
        if(model==='hr.employee'||model==='hr.employee.public'){
            constemployee=this.env.models['hr.employee'].insert({id});
            returnemployee.openProfile(model);
        }
        returnthis._super(...arguments);
    },
});

});
