flectra.define('web.custom_checkbox_tests',function(require){
    "usestrict";

    constCustomCheckbox=require('web.CustomCheckbox');
    consttestUtils=require('web.test_utils');

    const{createComponent,dom:testUtilsDom}=testUtils;

    QUnit.module('Components',{},function(){

        QUnit.module('CustomCheckbox');

        QUnit.test('testcheckbox:defaultvalues',asyncfunction(assert){
            assert.expect(6);

            constcheckbox=awaitcreateComponent(CustomCheckbox,{});

            assert.containsOnce(checkbox.el,'input');
            assert.containsNone(checkbox.el,'input:disabled');
            assert.containsOnce(checkbox.el,'label');

            constinput=checkbox.el.querySelector('input');
            assert.notOk(input.checked,'checkboxshouldbeunchecked');
            assert.ok(input.id.startsWith('checkbox-comp-'));

            awaittestUtilsDom.click(checkbox.el.querySelector('label'));
            assert.ok(input.checked,'checkboxshouldbechecked');

            checkbox.destroy();
        });

        QUnit.test('testcheckbox:customvalues',asyncfunction(assert){
            assert.expect(6);

            constcheckbox=awaitcreateComponent(CustomCheckbox,{
                props:{
                    id:'my-custom-checkbox',
                    disabled:true,
                    value:true,
                    text:'checkbox',
                }
            });

            assert.containsOnce(checkbox.el,'input');
            assert.containsOnce(checkbox.el,'input:disabled');
            assert.containsOnce(checkbox.el,'label');

            constinput=checkbox.el.querySelector('input');
            assert.ok(input.checked,'checkboxshouldbechecked');
            assert.strictEqual(input.id,'my-custom-checkbox');
            assert.ok(input.checked,'checkboxshouldbechecked');

            checkbox.destroy();
        });
    });
});
