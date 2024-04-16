flectra.define('website_form_project.form',function(require){
'usestrict';

varcore=require('web.core');
varFormEditorRegistry=require('website_form.form_editor_registry');

var_t=core._t;

FormEditorRegistry.add('create_task',{
    formFields:[{
        type:'char',
        modelRequired:true,
        name:'name',
        string:'TaskTitle',
    },{
        type:'email',
        modelRequired:true,
        name:'email_from',
        string:'YourEmail',
    },{
        type:'char',
        name:'description',
        string:'Description',
    }],
    fields:[{
        name:'project_id',
        type:'many2one',
        relation:'project.project',
        string:_t('Project'),
    }],
});

});
