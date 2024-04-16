flectra.define('hr.employee_language',function(require){
'usestrict';

varFormController=require('web.FormController');
varFormView=require('web.FormView');
varviewRegistry=require('web.view_registry');

varEmployeeFormController=FormController.extend({
    saveRecord:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            if(arguments[0].indexOf('lang')>=0){
                self.do_action('reload_context');
            }
        });
    },
});

varEmployeeProfileFormView=FormView.extend({
    config:_.extend({},FormView.prototype.config,{
        Controller:EmployeeFormController,
    }),
});

viewRegistry.add('hr_employee_profile_form',EmployeeProfileFormView);
returnEmployeeProfileFormView;
});
