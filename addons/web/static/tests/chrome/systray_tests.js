flectra.define('web.systray_tests',function(require){
    "usestrict";

    vartestUtils=require('web.test_utils');
    varSystrayMenu=require('web.SystrayMenu');
    varWidget=require('web.Widget');

    QUnit.test('Addingasynccomponentstotheregistryrespectsthesequence',asyncfunction(assert){
        assert.expect(2);
        varparent=awaittestUtils.createParent({});
        varprom=testUtils.makeTestPromise();

        varsynchronousFirstWidget=Widget.extend({
            sequence:3,//biggersequencemeansmoretotheleft
            start:function(){
                this.$el.addClass('first');
            }
        });
        varasynchronousSecondWidget=Widget.extend({
            sequence:1,//smallersequencemeansmoretotheright
            willStart:function(){
                returnprom;
            },
            start:function(){
                this.$el.addClass('second');
            }
        });

        SystrayMenu.Items=[synchronousFirstWidget,asynchronousSecondWidget];
        varmenu=newSystrayMenu(parent);

        menu.appendTo($('#qunit-fixture'));
        awaittestUtils.nextTick();
        prom.resolve();
        awaittestUtils.nextTick();

        assert.hasClass(menu.$('div:eq(0)'),'first');
        assert.hasClass(menu.$('div:eq(1)'),'second');

        parent.destroy();
    })
});
