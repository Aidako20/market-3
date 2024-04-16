flectra.define('hr/static/src/models/user/user.js',function(require){
'usestrict';

const{
    registerFieldPatchModel,
}=require('mail/static/src/model/model_core.js');
const{one2one}=require('mail/static/src/model/model_field.js');

registerFieldPatchModel('mail.user','hr/static/src/models/user/user.js',{
    /**
     *Employeerelatedtothisuser.
     */
    employee:one2one('hr.employee',{
        inverse:'user',
    }),
});

});
