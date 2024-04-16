flectra.define('web.menu_tests',function(require){
    "usestrict";

    consttestUtils=require('web.test_utils');
    constMenu=require('web.Menu');
    constSystrayMenu=require('web.SystrayMenu');
    constWidget=require('web.Widget');


    QUnit.module('chrome',{},function(){
        QUnit.module('Menu');

        QUnit.test('Systrayon_attach_callbackiscalled',asyncfunction(assert){
            assert.expect(4);

            constparent=awaittestUtils.createParent({});

            //Addsomewidgetstothesystray
            constWidget1=Widget.extend({
                on_attach_callback:()=>assert.step('on_attach_callbackwidget1')
            });
            constWidget2=Widget.extend({
                on_attach_callback:()=>assert.step('on_attach_callbackwidget2')
            });
            SystrayMenu.Items=[Widget1,Widget2];

            testUtils.mock.patch(SystrayMenu,{
                on_attach_callback:function(){
                    assert.step('on_attach_callbacksystray');
                    this._super(...arguments);
                }
            });

            constmenu=newMenu(parent,{children:[]});
            awaitmenu.appendTo($('#qunit-fixture'));

            assert.verifySteps([
                'on_attach_callbacksystray',
                'on_attach_callbackwidget1',
                'on_attach_callbackwidget2',
            ]);
            testUtils.mock.unpatch(SystrayMenu);
            parent.destroy();
        });
    });

});
