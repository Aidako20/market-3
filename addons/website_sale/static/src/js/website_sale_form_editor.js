flectra.define('website_sale.form',function(require){
'usestrict';

varFormEditorRegistry=require('website_form.form_editor_registry');

FormEditorRegistry.add('create_customer',{
    formFields:[{
        type:'char',
        modelRequired:true,
        name:'name',
        string:'YourName',
    },{
        type:'email',
        required:true,
        name:'email',
        string:'YourEmail',
    },{
        type:'tel',
        name:'phone',
        string:'PhoneNumber',
    },{
        type:'char',
        name:'company_name',
        string:'CompanyName',
    }],
});

});
