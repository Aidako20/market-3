flectra.define('mail/static/src/utils/timer/timer_tests.js',function(require){
'usestrict';

const{afterEach,beforeEach,nextTick,start}=require('mail/static/src/utils/test_utils.js');
constTimer=require('mail/static/src/utils/timer/timer.js');

const{TimerClearedError}=Timer;

QUnit.module('mail',{},function(){
QUnit.module('utils',{},function(){
QUnit.module('timer',{},function(){
QUnit.module('timer_tests.js',{
    beforeEach(){
        beforeEach(this);
        this.timers=[];

        this.start=async(params)=>{
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
        for(consttimerofthis.timers){
            timer.clear();
        }
        afterEach(this);
    },
});

QUnit.test('timerdoesnottimeoutoninitialization',asyncfunction(assert){
    assert.expect(3);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            0
        )
    );

    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutonimmediateinitialization"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutfrominitializationafter0ms"
    );

    awaitthis.env.testUtils.advanceTime(1000*1000);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutfrominitializationafter1000s"
    );
});

QUnit.test('timerstart(duration:0ms)',asyncfunction(assert){
    assert.expect(2);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            0
        )
    );

    this.timers[0].start();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.ok(
        hasTimedOut,
        "timershouldhavetimedoutonstartafter0ms"
    );
});

QUnit.test('timerstartobservetermination(duration:0ms)',asyncfunction(assert){
    assert.expect(6);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>{
                hasTimedOut=true;
                return'timeout_result';
            },
            0
        )
    );

    this.timers[0].start()
        .then(result=>{
            assert.strictEqual(
                result,
                'timeout_result',
                "valuereturnedbystartshouldbevaluereturnedbyfunctionontimeout"
            );
            assert.step('timeout');
        });
    awaitnextTick();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );
    assert.verifySteps(
        [],
        "timer.start()shouldnothaveyetobservedtimeout"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.ok(
        hasTimedOut,
        "timershouldhavetimedoutonstartafter0ms"
    );
    assert.verifySteps(
        ['timeout'],
        "timer.start()shouldhaveobservedtimeoutafter0ms"
    );
});

QUnit.test('timerstart(duration:1000s)',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            1000*1000
        )
    );

    this.timers[0].start();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutonstartafter0ms"
    );

    awaitthis.env.testUtils.advanceTime(1000);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutonstartafter1000ms"
    );

    awaitthis.env.testUtils.advanceTime(998*1000+999);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutonstartafter9999ms"
    );

    awaitthis.env.testUtils.advanceTime(1);
    assert.ok(
        hasTimedOut,
        "timershouldhavetimedoutonstartafter10s"
    );
});

QUnit.test('[nocancelationintercept]timerstartthenimmediateclear(duration:0ms)',asyncfunction(assert){
    assert.expect(4);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            0
        )
    );

    this.timers[0].start();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );

    this.timers[0].clear();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstartandclear"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter0msofclear"
    );

    awaitthis.env.testUtils.advanceTime(1000);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter1sofclear"
    );
});

QUnit.test('[nocancelationintercept]timerstartthenclearbeforetimeout(duration:1000ms)',asyncfunction(assert){
    assert.expect(4);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            1000
        )
    );

    this.timers[0].start();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );

    awaitthis.env.testUtils.advanceTime(999);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafter999msofstart"
    );

    this.timers[0].clear();
    awaitthis.env.testUtils.advanceTime(1);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter1msofclearthathappens999msafterstart(globally1sawait)"
    );

    awaitthis.env.testUtils.advanceTime(1000);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter1001msafterclear(timerfullycleared)"
    );
});

QUnit.test('[nocancelationintercept]timerstartthenresetbeforetimeout(duration:1000ms)',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            1000
        )
    );

    this.timers[0].start();
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );

    awaitthis.env.testUtils.advanceTime(999);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter999msofstart"
    );

    this.timers[0].reset();
    awaitthis.env.testUtils.advanceTime(1);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter1msofresetwhichhappens999msafterstart"
    );

    awaitthis.env.testUtils.advanceTime(998);
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutafter999msofreset"
    );

    awaitthis.env.testUtils.advanceTime(1);
    assert.ok(
        hasTimedOut,
        "timershouldnothavetimedoutafter1sofreset"
    );
});

QUnit.test('[withcancelationintercept]timerstartthenimmediateclear(duration:0ms)',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            0,
            {silentCancelationErrors:false}
        )
    );

    this.timers[0].start()
        .then(()=>{
            thrownewError("timer.start()shouldnotberesolved(shouldhavebeencanceledbyclear)");
        })
        .catch(error=>{
            assert.ok(
                errorinstanceofTimerClearedError,
                "ShouldgenerateaTimerclearederror(from`.clear()`)"
            );
            assert.step('timer_cleared');
        });
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );
    awaitnextTick();
    assert.verifySteps([],"shouldnothaveobservedclearedtimer(timernotyetcleared)");

    this.timers[0].clear();
    awaitnextTick();
    assert.verifySteps(
        ['timer_cleared'],
        "timer.start()shouldhaveobservedithasbeencleared"
    );
});

QUnit.test('[withcancelationintercept]timerstartthenimmediatereset(duration:0ms)',asyncfunction(assert){
    assert.expect(9);

    awaitthis.start({
        hasTimeControl:true,
    });

    lethasTimedOut=false;
    this.timers.push(
        newTimer(
            this.env,
            ()=>hasTimedOut=true,
            0,
            {silentCancelationErrors:false}
        )
    );

    this.timers[0].start()
        .then(()=>{
            thrownewError("timer.start()shouldnotobserveatimeout");
        })
        .catch(error=>{
            assert.ok(errorinstanceofTimerClearedError,"ShouldgenerateaTimerclearederror(from`.reset()`)");
            assert.step('timer_cleared');
        });
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterstart"
    );
    awaitnextTick();
    assert.verifySteps([],"shouldnothaveobservedclearedtimer(timernotyetcleared)");

    this.timers[0].reset()
        .then(()=>assert.step('timer_reset_timeout'));
    awaitnextTick();
    assert.verifySteps(
        ['timer_cleared'],
        "timer.start()shouldhaveobservedithasbeencleared"
    );
    assert.notOk(
        hasTimedOut,
        "timershouldnothavetimedoutimmediatelyafterreset"
    );

    awaitthis.env.testUtils.advanceTime(0);
    assert.ok(
        hasTimedOut,
        "timershouldhavetimedoutafterresettimeout"
    );
    assert.verifySteps(
        ['timer_reset_timeout'],
        "timer.reset()shouldhaveobservedithastimedout"
    );
});

});
});
});

});
