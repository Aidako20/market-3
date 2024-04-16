flectra.define('mail/static/src/component_hooks/use_store/use_store_tests.js',function(require){
'usestrict';

constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
const{
    afterNextRender,
    nextAnimationFrame,
}=require('mail/static/src/utils/test_utils.js');

const{Component,QWeb,Store}=owl;
const{onPatched,useGetters}=owl.hooks;
const{xml}=owl.tags;

QUnit.module('mail',{},function(){
QUnit.module('component_hooks',{},function(){
QUnit.module('use_store',{},function(){
QUnit.module('use_store_tests.js',{
    beforeEach(){
        constqweb=newQWeb();
        this.env={qweb};
    },
    afterEach(){
        this.env=undefined;
        this.store=undefined;
    },
});


QUnit.test("comparekeys,nodepth,primitives",asyncfunction(assert){
    assert.expect(8);
    this.store=newStore({
        env:this.env,
        getters:{
            get({state},key){
                returnstate[key];
            },
        },
        state:{
            obj:{
                subObj1:'a',
                subObj2:'b',
                use1:true,
            },
        },
    });
    this.env.store=this.store;
    letcount=0;
    classMyComponentextendsComponent{
        constructor(){
            super(...arguments);
            this.storeGetters=useGetters();
            this.storeProps=useStore(props=>{
                constobj=this.storeGetters.get('obj');
                return{
                    res:obj.use1?obj.subObj1:obj.subObj2,
                };
            });
            onPatched(()=>{
                count++;
            });
        }
    }
    Object.assign(MyComponent,{
        env:this.env,
        props:{},
        template:xml`<divt-esc="storeProps.res"/>`,
    });

    constfixture=document.querySelector('#qunit-fixture');

    constmyComponent=newMyComponent();
    awaitmyComponent.mount(fixture);
    assert.strictEqual(count,0,
        'shouldnotdetectanupdateinitially');
    assert.strictEqual(fixture.textContent,'a',
        'shoulddisplaythecontentofsubObj1');

    awaitafterNextRender(()=>{
        this.store.state.obj.use1=false;
    });
    assert.strictEqual(count,1,
        'shoulddetectanupdatebecausetheselectorisreturningadifferentvalue(wassubObj1,nowissubObj2)');
    assert.strictEqual(fixture.textContent,'b',
        'shoulddisplaythecontentofsubObj2');

    this.store.state.obj.subObj2='b';
    //theremustbenorenderhere
    awaitnextAnimationFrame();
    assert.strictEqual(count,1,
        'shouldnotdetectanupdatebecausethesameprimitivevaluewasassigned(subObj2wasalready"b")');
    assert.strictEqual(fixture.textContent,'b',
        'shouldstilldisplaythecontentofsubObj2');

    awaitafterNextRender(()=>{
        this.store.state.obj.subObj2='d';
    });
    assert.strictEqual(count,2,
        'shoulddetectanupdatebecausetheselectorisreturningadifferentvalueforsubObj2');
    assert.strictEqual(fixture.textContent,'d',
        'shoulddisplaythenewcontentofsubObj2');

    myComponent.destroy();
});

QUnit.test("comparekeys,depth1,proxy",asyncfunction(assert){
    assert.expect(8);
    this.store=newStore({
        env:this.env,
        getters:{
            get({state},key){
                returnstate[key];
            },
        },
        state:{
            obj:{
                subObj1:{a:'a'},
                subObj2:{a:'b'},
                use1:true,
            },
        },
    });
    this.env.store=this.store;
    letcount=0;
    classMyComponentextendsComponent{
        constructor(){
            super(...arguments);
            this.storeGetters=useGetters();
            this.storeProps=useStore(props=>{
                constobj=this.storeGetters.get('obj');
                return{
                    array:[obj.use1?obj.subObj1:obj.subObj2],
                };
            },{
                compareDepth:{
                    array:1,
                },
            });
            onPatched(()=>{
                count++;
            });
        }
    }
    Object.assign(MyComponent,{
        env:this.env,
        props:{},
        template:xml`<divt-esc="storeProps.array[0].a"/>`,
    });

    constfixture=document.querySelector('#qunit-fixture');

    constmyComponent=newMyComponent();
    awaitmyComponent.mount(fixture);
    assert.strictEqual(count,0,
        'shouldnotdetectanupdateinitially');
    assert.strictEqual(fixture.textContent,'a',
        'shoulddisplaythecontentofsubObj1');

    awaitafterNextRender(()=>{
        this.store.state.obj.use1=false;
    });
    assert.strictEqual(count,1,
        'shoulddetectanupdatebecausetheselectorisreturningadifferentvalue(wassubObj1,nowissubObj2)');
    assert.strictEqual(fixture.textContent,'b',
        'shoulddisplaythecontentofsubObj2');

    this.store.state.obj.subObj1.a='c';
    //theremustbenorenderhere
    awaitnextAnimationFrame();
    assert.strictEqual(count,1,
        'shouldnotdetectanupdatebecausesubObj1waschangedbutonlysubObj2isselected');
    assert.strictEqual(fixture.textContent,'b',
        'shouldstilldisplaythecontentofsubObj2');

    awaitafterNextRender(()=>{
        this.store.state.obj.subObj2.a='d';
    });
    assert.strictEqual(count,2,
        'shoulddetectanupdatebecausethevalueofsubObj2changed');
    assert.strictEqual(fixture.textContent,'d',
        'shoulddisplaythenewcontentofsubObj2');

    myComponent.destroy();
});

});
});
});

});
