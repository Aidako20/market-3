flectra.define('web.abstract_view_tests',function(require){
"usestrict";

varAbstractView=require('web.AbstractView');
varajax=require('web.ajax');
vartestUtils=require('web.test_utils');

varcreateActionManager=testUtils.createActionManager;
varcreateView=testUtils.createView;

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            fake_model:{
                fields:{},
                record:[],
            },
            foo:{
                fields:{
                    foo:{string:"Foo",type:"char"},
                    bar:{string:"Bar",type:"boolean"},
                },
                records:[
                    {id:1,bar:true,foo:"yop"},
                    {id:2,bar:true,foo:"blip"},
                ]
            },
        };
    },
},function(){

    QUnit.module('AbstractView');

    QUnit.test('lazyloadingofjslibs(inparallel)',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(6);

        varprom=testUtils.makeTestPromise();
        varloadJS=ajax.loadJS;
        ajax.loadJS=function(url){
            assert.step(url);
            returnprom.then(function(){
                assert.step(url+'loaded');
            });
        };

        varView=AbstractView.extend({
            jsLibs:[['a','b']],
        });
        createView({
            View:View,
            arch:'<fake/>',
            data:this.data,
            model:'fake_model',
        }).then(function(view){
            assert.verifySteps(['aloaded','bloaded'],
                "shouldwaitforbothlibstobeloaded");
            ajax.loadJS=loadJS;
            view.destroy();
            done();
        });

        awaittestUtils.nextTick();
        assert.verifySteps(['a','b'],"bothlibsshouldbeloadedinparallel");
        prom.resolve();
    });

    QUnit.test('lazyloadingofjslibs(sequentially)',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(10);

        varproms={
            a: testUtils.makeTestPromise(),
            b: testUtils.makeTestPromise(),
            c: testUtils.makeTestPromise(),
        };
        varloadJS=ajax.loadJS;
        ajax.loadJS=function(url){
            assert.step(url);
            returnproms[url].then(function(){
                assert.step(url+'loaded');
            });
        };

        varView=AbstractView.extend({
            jsLibs:[
                ['a','b'],
                'c',
            ],
        });
        createView({
            View:View,
            arch:'<fake/>',
            data:this.data,
            model:'fake_model',
        }).then(function(view){
            assert.verifySteps(['cloaded'],"shouldwaitforalllibstobeloaded");
            ajax.loadJS=loadJS;
            view.destroy();
            done();
        });
        awaittestUtils.nextTick();
        assert.verifySteps(['a','b'],"libs'a'and'b'shouldbeloadedinparallel");
        awaitproms.b.resolve();
        awaittestUtils.nextTick();
        assert.verifySteps(['bloaded'],"shouldwaitfor'a'and'b'tobeloadedbeforeloading'c'");
        awaitproms.a.resolve();
        awaittestUtils.nextTick();
        assert.verifySteps(['aloaded','c'],"shouldload'c'when'a'and'b'areloaded");
        awaitproms.c.resolve();
    });

    QUnit.test('group_byfromcontextcanbeastring,insteadofalistofstrings',asyncfunction(assert){
        assert.expect(1);

        varactionManager=awaitcreateActionManager({
            actions:[{
                id:1,
                name:'Foo',
                res_model:'foo',
                type:'ir.actions.act_window',
                views:[[false,'list']],
                context:{
                    group_by:'bar',
                },
            }],
            archs:{
                'foo,false,list':'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
                'foo,false,search':'<search></search>',
            },
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.deepEqual(args.kwargs.groupby,['bar']);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaitactionManager.doAction(1);

        actionManager.destroy();
    });

});
});
