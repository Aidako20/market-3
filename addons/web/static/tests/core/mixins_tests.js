flectra.define('web.mixins_tests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');

QUnit.module('core',{},function(){

    QUnit.module('mixins');

    QUnit.test('performado_actionproperly',function(assert){
        assert.expect(3);
        vardone=assert.async();

        varwidget=newWidget();

        testUtils.mock.intercept(widget,'do_action',function(event){
            assert.strictEqual(event.data.action,'test.some_action_id',
                "shouldhavesentproperactionname");
            assert.deepEqual(event.data.options,{clear_breadcrumbs:true},
                "shouldhavesentproperoptions");
            event.data.on_success();
        });

        widget.do_action('test.some_action_id',{clear_breadcrumbs:true}).then(function(){
            assert.ok(true,'deferredshouldhavebeenresolved');
            widget.destroy();
            done();
        });
    });


});

});

