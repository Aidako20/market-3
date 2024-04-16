flectra.define('mail/static/src/utils/throttle/throttle_tests.js',function(require){
'usestrict';

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');
constthrottle=require('mail/static/src/utils/throttle/throttle.js');
const{nextTick}=require('mail/static/src/utils/utils.js');

const{ThrottleReinvokedError,ThrottleCanceledError}=throttle;

QUnit.module('mail',{},function(){
QUnit.module('utils',{},function(){
QUnit.module('throttle',{},function(){
QUnit.module('throttle_tests.js',{
    beforeEach(){
        beforeEach(this);
        this.throttles=[];

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},params,{
                data:this.data,
            }));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        //Important:testsshouldcleanlyinterceptcancelationerrorsthat
        //mayresultfromthisteardown.
        for(consttofthis.throttles){
            t.clear();
        }
        afterEach(this);
    },
});

QUnit.test('singlecall',asyncfunction(assert){
    assert.expect(6);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasInvokedFunc=false;
    constthrottledFunc=throttle(
        this.env,
        ()=>{
            hasInvokedFunc=true;
            return'func_result';
        },
        0
    );
    this.throttles.push(throttledFunc);

    assert.notOk(
        hasInvokedFunc,
        "funcshouldnothavebeeninvokedonimmediatethrottleinitialization"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.notOk(
        hasInvokedFunc,
        "funcshouldnothavebeeninvokedfromthrottleinitializationafter0ms"
    );

    throttledFunc().then(res=>{
        assert.step('throttle_observed_invoke');
        assert.strictEqual(
            res,
            'func_result',
            "throttlecallreturnshouldforwardresultofinnerfunc"
        );
    });
    awaitnextTick();
    assert.ok(
        hasInvokedFunc,
        "funcshouldhavebeenimmediatelyinvokedonfirstthrottlecall"
    );
    assert.verifySteps(
        ['throttle_observed_invoke'],
        "throttleshouldhaveobservedinvokedonfirstthrottlecall"
    );
});

QUnit.test('2nd(throttled)call',asyncfunction(assert){
    assert.expect(8);

    awaitthis.start({
        hasTimeControl:true,
    });

    letfuncCalledAmount=0;
    constthrottledFunc=throttle(
        this.env,
        ()=>{
            funcCalledAmount++;
            return`func_result_${funcCalledAmount}`;
        },
        1000
    );
    this.throttles.push(throttledFunc);

    throttledFunc().then(result=>{
        assert.step('throttle_observed_invoke_1');
        assert.strictEqual(
            result,
            'func_result_1',
            "throttlecallreturnshouldforwardresultofinnerfunc1"
        );
    });
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_1'],
        "innerfunctionofthrottleshouldhavebeeninvokedon1stcall(immediatereturn)"
    );

    throttledFunc().then(res=>{
        assert.step('throttle_observed_invoke_2');
        assert.strictEqual(
            res,
            'func_result_2',
            "throttlecallreturnshouldforwardresultofinnerfunc2"
        );
    });
    awaitnextTick();
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeenimmediatelyinvokedafter2ndcallimmediatelyafter1stcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(999);
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter999msof2ndcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(1);
    assert.verifySteps(
        ['throttle_observed_invoke_2'],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter1sof2ndcall(throttledwith1sinternalclock)"
    );
});

QUnit.test('throttledcallreinvocation',asyncfunction(assert){
    assert.expect(11);

    awaitthis.start({
        hasTimeControl:true,
    });

    letfuncCalledAmount=0;
    constthrottledFunc=throttle(
        this.env,
        ()=>{
            funcCalledAmount++;
            return`func_result_${funcCalledAmount}`;
        },
        1000,
        {silentCancelationErrors:false}
    );
    this.throttles.push(throttledFunc);

    throttledFunc().then(result=>{
        assert.step('throttle_observed_invoke_1');
        assert.strictEqual(
            result,
            'func_result_1',
            "throttlecallreturnshouldforwardresultofinnerfunc1"
        );
    });
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_1'],
        "innerfunctionofthrottleshouldhavebeeninvokedon1stcall(immediatereturn)"
    );

    throttledFunc()
        .then(()=>{
            thrownewError("2ndthrottlecallshouldnotberesolved(shouldhavebeencanceledbyreinvocation)");
        })
        .catch(error=>{
            assert.ok(
                errorinstanceofThrottleReinvokedError,
                "ShouldgenerateaThrottlereinvokederror(fromanotherthrottlefunctioncall)"
            );
            assert.step('throttle_reinvoked_1');
        });
    awaitnextTick();
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeenimmediatelyinvokedafter2ndcallimmediatelyafter1stcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(999);
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter999msof2ndcall(throttledwith1sinternalclock)"
    );

    throttledFunc()
        .then(result=>{
            assert.step('throttle_observed_invoke_2');
            assert.strictEqual(
                result,
                'func_result_2',
                "throttlecallreturnshouldforwardresultofinnerfunc2"
            );
        });
    awaitnextTick();
    assert.verifySteps(
        ['throttle_reinvoked_1'],
        "2ndthrottlecallshouldhavebeencanceledfrom3rdthrottlecall(reinvokedbeforecoolingdownphasehasended)"
    );

    awaitthis.env.testUtils.advanceTime(1);
    assert.verifySteps(
        ['throttle_observed_invoke_2'],
        "innerfunctionofthrottleshouldhavebeeninvokedafter1sof1stcall(throttledwith1sinternalclock,3rdthrottlecallre-usetimerof2ndthrottlecall)"
    );
});

QUnit.test('flushthrottledcall',asyncfunction(assert){
    assert.expect(9);

    awaitthis.start({
        hasTimeControl:true,
    });

    constthrottledFunc=throttle(
        this.env,
        ()=>{},
        1000,
    );
    this.throttles.push(throttledFunc);

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_1'));
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_1'],
        "innerfunctionofthrottleshouldhavebeeninvokedon1stcall(immediatereturn)"
    );

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_2'));
    awaitnextTick();
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeenimmediatelyinvokedafter2ndcallimmediatelyafter1stcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(10);
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter10msof2ndcall(throttledwith1sinternalclock)"
    );

    throttledFunc.flush();
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_2'],
        "innerfunctionofthrottleshouldhavebeeninvokedfrom2ndcallafterflush"
    );

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_3'));
    awaitnextTick();
    awaitthis.env.testUtils.advanceTime(999);
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter999msof3rdcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(1);
    assert.verifySteps(
        ['throttle_observed_invoke_3'],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter999msof3rdcall(throttledwith1sinternalclock)"
    );
});

QUnit.test('cancelthrottledcall',asyncfunction(assert){
    assert.expect(10);

    awaitthis.start({
        hasTimeControl:true,
    });

    constthrottledFunc=throttle(
        this.env,
        ()=>{},
        1000,
        {silentCancelationErrors:false}
    );
    this.throttles.push(throttledFunc);

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_1'));
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_1'],
        "innerfunctionofthrottleshouldhavebeeninvokedon1stcall(immediatereturn)"
    );

    throttledFunc()
        .then(()=>{
            thrownewError("2ndthrottlecallshouldnotberesolved(shouldhavebeencanceled)");
        })
        .catch(error=>{
            assert.ok(
                errorinstanceofThrottleCanceledError,
                "ShouldgenerateaThrottlecancelederror(from`.cancel()`)"
            );
            assert.step('throttle_canceled');
        });
    awaitnextTick();
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeenimmediatelyinvokedafter2ndcallimmediatelyafter1stcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(500);
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter500msof2ndcall(throttledwith1sinternalclock)"
    );

    throttledFunc.cancel();
    awaitnextTick();
    assert.verifySteps(
        ['throttle_canceled'],
        "2ndthrottlefunctioncallshouldhavebeencanceled"
    );

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_3'));
    awaitnextTick();
    assert.verifySteps(
        [],
        "3rdthrottlefunctioncallshouldnothaveinvokedinnerfunctionyet(cancelreusesinnerclockofthrottle)"
    );

    awaitthis.env.testUtils.advanceTime(500);
    assert.verifySteps(
        ['throttle_observed_invoke_3'],
        "3rdthrottlefunctioncallshouldhaveinvokeinnerfunctionafter500ms(cancelreusesinnerclockofthrottlewhichwasat500msin,throttlesetat1ms)"
    );
});

QUnit.test('clearthrottledcall',asyncfunction(assert){
    assert.expect(9);

    awaitthis.start({
        hasTimeControl:true,
    });

    constthrottledFunc=throttle(
        this.env,
        ()=>{},
        1000,
        {silentCancelationErrors:false}
    );
    this.throttles.push(throttledFunc);

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_1'));
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_1'],
        "innerfunctionofthrottleshouldhavebeeninvokedon1stcall(immediatereturn)"
    );

    throttledFunc()
        .then(()=>{
            thrownewError("2ndthrottlecallshouldnotberesolved(shouldhavebeencanceledfromclear)");
        })
        .catch(error=>{
            assert.ok(
                errorinstanceofThrottleCanceledError,
                "ShouldgenerateaThrottlecancelederror(from`.clear()`)"
            );
            assert.step('throttle_canceled');
        });
    awaitnextTick();
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeenimmediatelyinvokedafter2ndcallimmediatelyafter1stcall(throttledwith1sinternalclock)"
    );

    awaitthis.env.testUtils.advanceTime(500);
    assert.verifySteps(
        [],
        "innerfunctionofthrottleshouldnothavebeeninvokedafter500msof2ndcall(throttledwith1sinternalclock)"
    );

    throttledFunc.clear();
    awaitnextTick();
    assert.verifySteps(
        ['throttle_canceled'],
        "2ndthrottlefunctioncallshouldhavebeencanceled(from`.clear()`)"
    );

    throttledFunc().then(()=>assert.step('throttle_observed_invoke_3'));
    awaitnextTick();
    assert.verifySteps(
        ['throttle_observed_invoke_3'],
        "3rdthrottlefunctioncallshouldhaveinvokeinnerfunctionimmediately(`.clear()`flushesthrottle)"
    );
});

});
});
});

});
