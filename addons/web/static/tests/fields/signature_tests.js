flectra.define('web.signature_field_tests',function(require){
"usestrict";

varajax=require('web.ajax');
varcore=require('web.core');
varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('fields',{},function(){

QUnit.module('signature',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    display_name:{string:"Name",type:"char"},
                    product_id:{string:"ProductName",type:"many2one",relation:'product'},
                    sign:{string:"Signature",type:"binary"},
                },
                records:[{
                    id:1,
                    display_name:"Pop'sChock'lit",
                    product_id:7,
                }],
                onchanges:{},
            },
            product:{
                fields:{
                    name:{string:"ProductName",type:"char"}
                },
                records:[{
                    id:7,
                    display_name:"VeggieBurger",
                }]
            },
        };
    }
},function(){

    QUnit.module('SignatureField',{
        before:function(){
            returnajax.loadXML('/web/static/src/xml/name_and_signature.xml',core.qweb);
        },
    });

    QUnit.test('Setsimplefieldin"full_name"nodeoption',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="sign"widget="signature"options="{\'full_name\':\'display_name\'}"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/sign/get_fonts/'){
                    returnPromise.resolve();
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'div[name=sign]div.o_signaturesvg',
            "shouldhaveavalidsignaturewidget");
        //Clickonthewidgettoopensignaturemodal
        awaittestUtils.dom.click(form.$('div[name=sign]div.o_signature'));
        assert.strictEqual($('.modal.modal-bodya.o_web_sign_auto_button').length,1,
            'shouldopenamodalwith"Auto"button');
        assert.strictEqual($('.modal.modal-body.o_web_sign_name_input').val(),"Pop'sChock'lit",
            'CorrectValueshouldbesetintheinputforautodrawingthesignature');

        form.destroy();
    });

    QUnit.test('Setm2ofieldin"full_name"nodeoption',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="sign"widget="signature"options="{\'full_name\':\'product_id\'}"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/sign/get_fonts/'){
                    returnPromise.resolve();
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'div[name=sign]div.o_signaturesvg',
            "shouldhaveavalidsignaturewidget");
        //Clickonthewidgettoopensignaturemodal
        awaittestUtils.dom.click(form.$('div[name=sign]div.o_signature'));
        assert.strictEqual($('.modal.modal-bodya.o_web_sign_auto_button').length,1,
            'shouldopenamodalwith"Auto"button');
        assert.strictEqual($('.modal.modal-body.o_web_sign_name_input').val(),"VeggieBurger",
            'CorrectValueshouldbesetintheinputforautodrawingthesignature');

        form.destroy();
    });

    QUnit.module('SignatureWidget');

    QUnit.test('SignaturewidgetrendersaSignbutton',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<header>'+
                        '<widgetname="signature"string="Sign"/>'+
                    '</header>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/sign/get_fonts/'){
                    returnPromise.resolve();
                }
                returnthis._super(route,args);
            },
        });

        assert.containsOnce(form,'button.o_sign_button.o_widget',
            "Shouldhaveasignaturewidgetbutton");
        assert.strictEqual($('.modal-dialog').length,0,
            "Shouldnothaveanymodal");
        //Clicksonthesignbuttontoopenthesignmodal.
        awaittestUtils.dom.click(form.$('span.o_sign_label'));
        assert.strictEqual($('.modal-dialog').length,1,
            "Shouldhaveonemodalopened");

        form.destroy();
    });

    QUnit.test('Signaturewidget:full_nameoption',asyncfunction(assert){
        assert.expect(2);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<header>'+
                        '<widgetname="signature"string="Sign"full_name="display_name"/>'+
                    '</header>'+
                    '<fieldname="display_name"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/sign/get_fonts/'){
                    returnPromise.resolve();
                }
                returnthis._super(route,args);
            },
        });

        //Clicksonthesignbuttontoopenthesignmodal.
        awaittestUtils.dom.click(form.$('span.o_sign_label'));
        assert.strictEqual($('.modal.modal-bodya.o_web_sign_auto_button').length,1,
            "Shouldopenamodalwith\"Auto\"button");
        assert.strictEqual($('.modal.modal-body.o_web_sign_name_input').val(),"Pop'sChock'lit",
            "CorrectValueshouldbesetintheinputforautodrawingthesignature");

        form.destroy();
    });

    QUnit.test('Signaturewidget:highlightoption',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<header>'+
                        '<widgetname="signature"string="Sign"highlight="1"/>'+
                    '</header>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/sign/get_fonts/'){
                    returnPromise.resolve();
                }
                returnthis._super(route,args);
            },
        });

        assert.hasClass(form.$('button.o_sign_button.o_widget'),'btn-primary',
            "Thebuttonmusthavethe'btn-primary'classas\"highlight=1\"");
        //Clicksonthesignbuttontoopenthesignmodal.
        awaittestUtils.dom.click(form.$('span.o_sign_label'));
        assert.isNotVisible($('.modal.modal-bodya.o_web_sign_auto_button'),
            "\"Auto\"buttonmustbeinvisible");
        assert.strictEqual($('.modal.modal-body.o_web_sign_name_input').val(),'',
            "Novalueshouldbesetintheinputforautodrawingthesignature");

        form.destroy();
    });
});
});
});
