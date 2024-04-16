flectra.define('website_form.form_editor_registry',function(require){
'usestrict';

varRegistry=require('web.Registry');

returnnewRegistry();

});

flectra.define('website_form.send_mail_form',function(require){
'usestrict';

varcore=require('web.core');
varFormEditorRegistry=require('website_form.form_editor_registry');

var_t=core._t;

FormEditorRegistry.add('send_mail',{
    formFields:[{
        type:'char',
        custom:true,
        required:true,
        name:'YourName',
    },{
        type:'tel',
        custom:true,
        name:'PhoneNumber',
    },{
        type:'email',
        modelRequired:true,
        name:'email_from',
        string:'YourEmail',
    },{
        type:'char',
        custom:true,
        name:'YourCompany',
    },{
        type:'char',
        modelRequired:true,
        name:'subject',
        string:'Subject',
    },{
        type:'text',
        custom:true,
        required:true,
        name:'YourQuestion',
    }],
    fields:[{
        name:'email_to',
        type:'char',
        required:true,
        string:_t('RecipientEmail'),
        defaultValue:'info@yourcompany.example.com',
    }],
});

});
