flectra.define('web.upgrade_fields_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('fields',{},function(){

QUnit.module('upgrade_fields',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    bar:{string:"Bar",type:"boolean"},
                },
            }
        };
    },
},function(){

    QUnit.module('UpgradeBoolean');

    QUnit.test('widgetupgrade_booleaninaformview',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="bar"widget="upgrade_boolean"/></form>',
        });

        awaittestUtils.dom.click(form.$('input:checkbox'));
        assert.strictEqual($('.modal').length,1,
            "the'UpgradetoEnterprise'dialogshouldbeopened");

        form.destroy();
    });

    QUnit.test('widgetupgrade_booleaninaformview',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<divclass="o_field"><fieldname="bar"widget="upgrade_boolean"/></div>'+
                    '<divclass="o_label"><labelfor="bar"/><div>Coucou</div></div>'+
                '</form>',
        });

        assert.containsNone(form,'.o_field.badge',
            "theupgradebadgeshouldn'tbeinsidethefieldsection");
        assert.containsOnce(form,'.o_label.badge',
            "theupgradebadgeshouldbeinsidethelabelsection");
        assert.strictEqual(form.$('.o_label').text(),"Bar EnterpriseCoucou",
            "theupgradelabelshouldbeinsidethelabelsection");
        form.destroy();
    });

});
});
});
