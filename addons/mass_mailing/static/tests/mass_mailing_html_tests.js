flectra.define('mass_mailing.field_html_tests',function(require){
"usestrict";

varajax=require('web.ajax');
varFormView=require('web.FormView');
varFieldHtml=require('web_editor.field.html');
varMassMailingFieldHtml=require('mass_mailing.FieldHtml');
vartestUtils=require('web.test_utils');
varweTestUtils=require('web_editor.test_utils');
varWysiwyg=require('web_editor.wysiwyg');


QUnit.module('mass_mailing',{},function(){
QUnit.module('fieldhtml',{
    beforeEach:function(){
        this.data=weTestUtils.wysiwygData({
            'mailing.mailing':{
                fields:{
                    display_name:{
                        string:"Displayedname",
                        type:"char"
                    },
                    body_html:{
                        string:"MessageBodyinline(tosend)",
                        type:"html"
                    },
                    body_arch:{
                        string:"MessageBodyforedition",
                        type:"html"
                    },
                },
                records:[{
                    id:1,
                    display_name:"firstrecord",
                    body_html:"<divclass='field_body'style='background-color:red;'><p>codetoedit</p></div>",
                    body_arch:"<divclass='field_body'><p>codetoedit</p></div>",
                }],
            },
        });

        testUtils.mock.patch(ajax,{
            loadAsset:function(xmlId){
                if(xmlId==='template.assets'){
                    returnPromise.resolve({
                        cssLibs:[],
                        cssContents:['.field_body{background-color:red;}']
                    });
                }
                if(xmlId==='template.assets_all_style'){
                    returnPromise.resolve({
                        cssLibs:$('link[href]:not([type="image/x-icon"])').map(function(){
                            return$(this).attr('href');
                        }).get(),
                        cssContents:['.field_body{background-color:red;}']
                    });
                }
                throw'Wrongtemplate';
            },
        });
    },
    afterEach:function(){
        testUtils.mock.unpatch(ajax);
    },
},function(){

QUnit.test('savearchandhtml',asyncfunction(assert){
    assert.expect(4);

    varform=awaittestUtils.createView({
        View:FormView,
        model:'mailing.mailing',
        data:this.data,
        arch:'<form>'+
            '  <fieldname="body_html"class="oe_read_only"widget="html"'+
            '      options="{'+
            '               \'cssReadonly\':\'template.assets\','+
            '      }"'+
            '  />'+
            '  <fieldname="body_arch"class="oe_edit_only"widget="mass_mailing_html"'+
            '      options="{'+
            '               \'snippets\':\'web_editor.snippets\','+
            '               \'cssEdit\':\'template.assets\','+
            '               \'inline-field\':\'body_html\''+
            '      }"'+
            '  />'+
            '</form>',
        res_id:1,
    });
    var$fieldReadonly=form.$('.oe_form_field[name="body_html"]');
    var$fieldEdit=form.$('.oe_form_field[name="body_arch"]');

    assert.strictEqual($fieldReadonly.css('display'),'block',"shoulddisplaythereadonlymode");
    assert.strictEqual($fieldEdit.css('display'),'none',"shouldhidetheeditmode");

    awaittestUtils.form.clickEdit(form);

    $fieldReadonly=form.$('.oe_form_field[name="body_html"]');
    $fieldEdit=form.$('.oe_form_field[name="body_arch"]');

    assert.strictEqual($fieldReadonly.css('display'),'none',"shouldhidethereadonlymode");
    assert.strictEqual($fieldEdit.css('display'),'block',"shoulddisplaytheeditmode");

    form.destroy();
});

});
});
});
