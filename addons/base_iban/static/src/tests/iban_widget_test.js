flectra.define('base_iban.iban_widget_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('fields',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    acc_number:{string:"acc_number",type:"char"},
                },
                records:[{
                    id:1,
                    acc_number:"",
                }]
            },
        };
        //patch_.debouncetobefastandsynchronous
        this.underscoreDebounce=_.debounce;
        _.debounce=_.identity;
    },
    afterEach:function(){
        //unpatch_.debounce
        _.debounce=this.underscoreDebounce;
    }
},function(){

    QUnit.module('IbanWidget');

    QUnit.test('Ibanwidgetsarecorrectlyrendered',asyncfunction(assert){
        assert.expect(6);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><sheet><fieldname="acc_number"widget="iban"/></sheet></form>',
            mockRPC:function(route,args){
                if(args.method==='check_iban'){
                    console.log(args.args[1]==="BE000000000000000000")
                    returnPromise.resolve(args.args[1]==="BE000000000000000000");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.fields.editAndTrigger(form.$('.o_field_widget'),"BE00",'input');
        assert.containsOnce(form,'.o_iban_fail',"ShouldbeaFalseaccount,it'stooshort");
        assert.containsOnce(form,'.fa-times',"Shouldhaveacrosspictogram");

        awaittestUtils.fields.editAndTrigger(form.$('.o_field_widget'),"BE000000000000000000",'input');
        assert.containsOnce(form,'.text-success',"Shouldhavetext-success");
        assert.containsOnce(form,'.fa-check',"Shouldhaveavalidpictogram");

        awaittestUtils.fields.editAndTrigger(form.$('.o_field_widget'),"BE00xxxxxxxxxxxxxxxx",'input');
        assert.containsOnce(form,'.o_iban_fail',"ShouldbeFalseaccount");
        assert.containsOnce(form,'.fa-times',"Shouldhaveacrosspictogram");

        form.destroy();
    });
});
});
