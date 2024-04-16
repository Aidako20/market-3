flectra.define('website_hr_recruitment.form',function(require){
'usestrict';

varcore=require('web.core');
varFormEditorRegistry=require('website_form.form_editor_registry');

var_t=core._t;

FormEditorRegistry.add('apply_job',{
    formFields:[{
        type:'char',
        modelRequired:true,
        name:'partner_name',
        string:'YourName',
    },{
        type:'email',
        required:true,
        name:'email_from',
        string:'YourEmail',
    },{
        type:'char',
        required:true,
        name:'partner_phone',
        string:'PhoneNumber',
    },{
        type:'text',
        name:'description',
        string:'ShortIntroduction',
    },{
        type:'binary',
        custom:true,
        name:'Resume',
    }],
    fields:[{
        name:'job_id',
        type:'many2one',
        relation:'hr.job',
        string:_t('AppliedJob'),
    },{
        name:'department_id',
        type:'many2one',
        relation:'hr.department',
        string:_t('Department'),
    }],
    successPage:'/job-thank-you',
});

});
