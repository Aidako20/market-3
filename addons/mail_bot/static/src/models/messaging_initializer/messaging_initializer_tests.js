flectra.define('mail_bot/static/src/models/messaging_initializer/messaging_initializer_tests.js',function(require){
"usestrict";

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail_bot',{},function(){
QUnit.module('models',{},function(){
QUnit.module('messaging_initializer',{},function(){
QUnit.module('messaging_initializer_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},params,{
                data:this.data,
            }));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});


QUnit.test('FlectraBotinitializedatinit',asyncfunction(assert){
    //TODOthistestshouldbecompletedincombinationwith
    //implementing_mockMailChannelInitFlectraBottask-2300480
    assert.expect(2);

    awaitthis.start({
        env:{
            session:{
                flectrabot_initialized:false,
            },
        },
        asyncmockRPC(route,args){
            if(args.method==='init_flectrabot'){
                assert.step('init_flectrabot');
            }
            returnthis._super(...arguments);
        },
    });

    assert.verifySteps(
        ['init_flectrabot'],
        "shouldhaveinitializedFlectraBotatinit"
    );
});

});
});
});

});
