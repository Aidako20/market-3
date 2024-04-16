flectra.define('web.concurrency_tests',function(require){
"usestrict";

varconcurrency=require('web.concurrency');
vartestUtils=require('web.test_utils');

varmakeTestPromise=testUtils.makeTestPromise;
varmakeTestPromiseWithAssert=testUtils.makeTestPromiseWithAssert;

QUnit.module('core',{},function(){

    QUnit.module('concurrency');

    QUnit.test('mutex:simplescheduling',asyncfunction(assert){
        assert.expect(5);
        varmutex=newconcurrency.Mutex();

        varprom1=makeTestPromiseWithAssert(assert,'prom1');
        varprom2=makeTestPromiseWithAssert(assert,'prom2');

        mutex.exec(function(){returnprom1;});
        mutex.exec(function(){returnprom2;});

        assert.verifySteps([]);

        awaitprom1.resolve();

        assert.verifySteps(['okprom1']);

        awaitprom2.resolve();

        assert.verifySteps(['okprom2']);
    });

    QUnit.test('mutex:simpleScheduling2',asyncfunction(assert){
        assert.expect(5);
        varmutex=newconcurrency.Mutex();

        varprom1=makeTestPromiseWithAssert(assert,'prom1');
        varprom2=makeTestPromiseWithAssert(assert,'prom2');

        mutex.exec(function(){returnprom1;});
        mutex.exec(function(){returnprom2;});

        assert.verifySteps([]);

        awaitprom2.resolve();

        assert.verifySteps(['okprom2']);

        awaitprom1.resolve();

        assert.verifySteps(['okprom1']);
    });

    QUnit.test('mutex:reject',asyncfunction(assert){
        assert.expect(7);
        varmutex=newconcurrency.Mutex();

        varprom1=makeTestPromiseWithAssert(assert,'prom1');
        varprom2=makeTestPromiseWithAssert(assert,'prom2');
        varprom3=makeTestPromiseWithAssert(assert,'prom3');

        mutex.exec(function(){returnprom1;}).catch(function(){});
        mutex.exec(function(){returnprom2;}).catch(function(){});
        mutex.exec(function(){returnprom3;}).catch(function(){});

        assert.verifySteps([]);

        prom1.resolve();
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okprom1']);

        prom2.catch(function(){
           assert.verifySteps(['koprom2']);
        });
        prom2.reject({name:"sdkjfmqsjdfmsjkdfkljsdq"});
        awaittestUtils.nextMicrotaskTick();

        prom3.resolve();
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okprom3']);
    });

    QUnit.test('mutex:getUnlockedDefchecks',asyncfunction(assert){
        assert.expect(9);

        varmutex=newconcurrency.Mutex();

        varprom1=makeTestPromiseWithAssert(assert,'prom1');
        varprom2=makeTestPromiseWithAssert(assert,'prom2');

        mutex.getUnlockedDef().then(function(){
            assert.step('mutexunlocked(1)');
        });

        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['mutexunlocked(1)']);

        mutex.exec(function(){returnprom1;});
        awaittestUtils.nextMicrotaskTick();

        mutex.getUnlockedDef().then(function(){
            assert.step('mutexunlocked(2)');
        });

        assert.verifySteps([]);

        mutex.exec(function(){returnprom2;});
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps([]);

        awaitprom1.resolve();

        assert.verifySteps(['okprom1']);

        prom2.resolve();
        awaittestUtils.nextTick();

        assert.verifySteps(['okprom2','mutexunlocked(2)']);
    });

    QUnit.test('DropPrevious:basicusecase',asyncfunction(assert){
        assert.expect(4);

        vardp=newconcurrency.DropPrevious();

        varprom1=makeTestPromise(assert,'prom1');
        varprom2=makeTestPromise(assert,'prom2');

        dp.add(prom1).then(()=>assert.step('shouldnotgohere'))
                     .catch(()=>assert.step("rejecteddp1"));
        dp.add(prom2).then(()=>assert.step("okdp2"));

        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['rejecteddp1']);

        prom2.resolve();
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okdp2']);
    });

    QUnit.test('DropPrevious:resolvefirstbeforelast',asyncfunction(assert){
        assert.expect(4);

        vardp=newconcurrency.DropPrevious();

        varprom1=makeTestPromise(assert,'prom1');
        varprom2=makeTestPromise(assert,'prom2');

        dp.add(prom1).then(()=>assert.step('shouldnotgohere'))
                     .catch(()=>assert.step("rejecteddp1"));
        dp.add(prom2).then(()=>assert.step("okdp2"));


        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['rejecteddp1']);

        prom1.resolve();
        prom2.resolve();
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okdp2']);
    });

    QUnit.test('DropMisordered:resolveallcorrectlyordered,sync',asyncfunction(assert){
        assert.expect(1);

        vardm=newconcurrency.DropMisordered(),
            flag=false;

        vard1=makeTestPromise();
        vard2=makeTestPromise();

        varr1=dm.add(d1),
            r2=dm.add(d2);

        Promise.all([r1,r2]).then(function(){
            flag=true;
        });

        d1.resolve();
        d2.resolve();
        awaittestUtils.nextTick();

        assert.ok(flag);
    });

    QUnit.test("DropMisordered:don'tresolvemis-ordered,sync",asyncfunction(assert){
        assert.expect(4);

        vardm=newconcurrency.DropMisordered(),
            done1=false,
            done2=false,
            fail1=false,
            fail2=false;

        vard1=makeTestPromise();
        vard2=makeTestPromise();

        dm.add(d1).then(function(){done1=true;})
                    .catch(function(){fail1=true;});
        dm.add(d2).then(function(){done2=true;})
                    .catch(function(){fail2=true;});

        d2.resolve();
        d1.resolve();
        awaittestUtils.nextMicrotaskTick();

        //d1isinlimbo
        assert.ok(!done1);
        assert.ok(!fail1);

        //d2isfulfilled
        assert.ok(done2);
        assert.ok(!fail2);
    });

    QUnit.test('DropMisordered:failmis-orderedflag,sync',asyncfunction(assert){
        assert.expect(4);

        vardm=newconcurrency.DropMisordered(true/*failMisordered*/),
            done1=false,
            done2=false,
            fail1=false,
            fail2=false;

        vard1=makeTestPromise();
        vard2=makeTestPromise();

        dm.add(d1).then(function(){done1=true;})
                    .catch(function(){fail1=true;});
        dm.add(d2).then(function(){done2=true;})
                    .catch(function(){fail2=true;});

        d2.resolve();
        d1.resolve();
        awaittestUtils.nextMicrotaskTick();

        //d1isinlimbo
        assert.ok(!done1);
        assert.ok(fail1);

        //d2isresolved
        assert.ok(done2);
        assert.ok(!fail2);
    });

    QUnit.test('DropMisordered:resolveallcorrectlyordered,async',function(assert){
        vardone=assert.async();
        assert.expect(1);

        vardm=newconcurrency.DropMisordered();

        vard1=makeTestPromise();
        vard2=makeTestPromise();

        varr1=dm.add(d1),
            r2=dm.add(d2);

        setTimeout(function(){d1.resolve();},10);
        setTimeout(function(){d2.resolve();},20);

        Promise.all([r1,r2]).then(function(){
            assert.ok(true);
            done();
        });
    });

    QUnit.test("DropMisordered:don'tresolvemis-ordered,async",function(assert){
        vardone=assert.async();
        assert.expect(4);

        vardm=newconcurrency.DropMisordered(),
            done1=false,done2=false,
            fail1=false,fail2=false;

        vard1=makeTestPromise();
        vard2=makeTestPromise();

        dm.add(d1).then(function(){done1=true;})
                    .catch(function(){fail1=true;});
        dm.add(d2).then(function(){done2=true;})
                    .catch(function(){fail2=true;});

        setTimeout(function(){d1.resolve();},20);
        setTimeout(function(){d2.resolve();},10);

        setTimeout(function(){
            //d1isinlimbo
            assert.ok(!done1);
            assert.ok(!fail1);

            //d2isresolved
            assert.ok(done2);
            assert.ok(!fail2);
            done();
        },30);
    });

    QUnit.test('DropMisordered:failmis-orderedflag,async',function(assert){
        vardone=assert.async();
        assert.expect(4);

        vardm=newconcurrency.DropMisordered(true),
            done1=false,done2=false,
            fail1=false,fail2=false;

        vard1=makeTestPromise();
        vard2=makeTestPromise();

        dm.add(d1).then(function(){done1=true;})
                    .catch(function(){fail1=true;});
        dm.add(d2).then(function(){done2=true;})
                    .catch(function(){fail2=true;});

        setTimeout(function(){d1.resolve();},20);
        setTimeout(function(){d2.resolve();},10);

        setTimeout(function(){
            //d1isfailed
            assert.ok(!done1);
            assert.ok(fail1);

            //d2isresolved
            assert.ok(done2);
            assert.ok(!fail2);
            done();
        },30);
    });

    QUnit.test('MutexedDropPrevious:simple',asyncfunction(assert){
        assert.expect(5);

        varm=newconcurrency.MutexedDropPrevious();
        vard1=makeTestPromise();

        d1.then(function(){
            assert.step("d1resolved");
        });
        m.exec(function(){returnd1;}).then(function(result){
            assert.step("p1done");
            assert.strictEqual(result,'d1');
        });

        assert.verifySteps([]);
        d1.resolve('d1');
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(["d1resolved","p1done"]);
    });

    QUnit.test('MutexedDropPrevious:d2arrivesafterd1resolution',asyncfunction(assert){
        assert.expect(8);

        varm=newconcurrency.MutexedDropPrevious();
        vard1=makeTestPromiseWithAssert(assert,'d1');

        m.exec(function(){returnd1;}).then(function(){
            assert.step("p1resolved");
        });

        assert.verifySteps([]);
        d1.resolve('d1');
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okd1','p1resolved']);

        vard2=makeTestPromiseWithAssert(assert,'d2');
        m.exec(function(){returnd2;}).then(function(){
            assert.step("p2resolved");
        });

        assert.verifySteps([]);
        d2.resolve('d2');
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okd2','p2resolved']);
    });

    QUnit.test('MutexedDropPrevious:p1doesnotreturnadeferred',asyncfunction(assert){
        assert.expect(7);

        varm=newconcurrency.MutexedDropPrevious();

        m.exec(function(){return42;}).then(function(){
            assert.step("p1resolved");
        });

        assert.verifySteps([]);
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['p1resolved']);

        vard2=makeTestPromiseWithAssert(assert,'d2');
        m.exec(function(){returnd2;}).then(function(){
            assert.step("p2resolved");
        });

        assert.verifySteps([]);
        d2.resolve('d2');
        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['okd2','p2resolved']);
    });

    QUnit.test('MutexedDropPrevious:p2arrivesbeforep1resolution',asyncfunction(assert){
        assert.expect(8);

        varm=newconcurrency.MutexedDropPrevious();
        vard1=makeTestPromiseWithAssert(assert,'d1');

        m.exec(function(){returnd1;}).catch(function(){
            assert.step("p1rejected");
        });
        assert.verifySteps([]);

        vard2=makeTestPromiseWithAssert(assert,'d2');
        m.exec(function(){returnd2;}).then(function(){
            assert.step("p2resolved");
        });

        assert.verifySteps([]);
        d1.resolve('d1');
        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['p1rejected','okd1']);

        d2.resolve('d2');
        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['okd2','p2resolved']);
    });

    QUnit.test('MutexedDropPrevious:3arrivesbefore2initialization',asyncfunction(assert){
        assert.expect(10);
        varm=newconcurrency.MutexedDropPrevious();

        vard1=makeTestPromiseWithAssert(assert,'d1');
        vard3=makeTestPromiseWithAssert(assert,'d3');

        m.exec(function(){returnd1;}).catch(function(){
            assert.step('p1rejected');
        });

        m.exec(function(){
            assert.ok(false,"shouldnotexecutethisfunction");
        }).catch(function(){
            assert.step('p2rejected');
        });

        m.exec(function(){returnd3;}).then(function(result){
            assert.strictEqual(result,'d3');
            assert.step('p3resolved');
        });

        assert.verifySteps([]);

        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['p1rejected','p2rejected']);

        d1.resolve('d1');
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okd1']);

        d3.resolve('d3');
        awaittestUtils.nextTick();


        assert.verifySteps(['okd3','p3resolved']);
    });

    QUnit.test('MutexedDropPrevious:3arrivesafter2initialization',asyncfunction(assert){
        assert.expect(15);
        varm=newconcurrency.MutexedDropPrevious();

        vard1=makeTestPromiseWithAssert(assert,'d1');
        vard2=makeTestPromiseWithAssert(assert,'d2');
        vard3=makeTestPromiseWithAssert(assert,'d3');

        m.exec(function(){
            assert.step('executed1');
            returnd1;
        }).catch(function(){
            assert.step('p1rejected');
        });

        m.exec(function(){
            assert.step('executed2');
            returnd2;
        }).catch(function(){
            assert.step('p2rejected');
        });

        assert.verifySteps(['executed1']);

        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['p1rejected']);

        d1.resolve('d1');
        awaittestUtils.nextMicrotaskTick();

        assert.verifySteps(['okd1','executed2']);

        m.exec(function(){
            assert.step('executed3');
            returnd3;
        }).then(function(){
            assert.step('p3resolved');
        });
        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['p2rejected']);

        d2.resolve();
        awaittestUtils.nextMicrotaskTick();
        assert.verifySteps(['okd2','executed3']);

        d3.resolve();
        awaittestUtils.nextTick();
        assert.verifySteps(['okd3','p3resolved']);

     });

    QUnit.test('MutexedDropPrevious:2inthenof1with3',asyncfunction(assert){
        assert.expect(9);

        varm=newconcurrency.MutexedDropPrevious();

        vard1=makeTestPromiseWithAssert(assert,'d1');
        vard2=makeTestPromiseWithAssert(assert,'d2');
        vard3=makeTestPromiseWithAssert(assert,'d3');
        varp3;

        m.exec(function(){returnd1;})
            .catch(function(){
                assert.step('p1rejected');
                p3=m.exec(function(){
                    returnd3;
                }).then(function(){
                    assert.step('p3resolved');
                });
                returnp3;
            });

        awaittestUtils.nextTick();
        assert.verifySteps([]);

        m.exec(function(){
            assert.ok(false,'shouldnotexecutethisfunction');
            returnd2;
        }).catch(function(){
            assert.step('p2rejected');
        });

        awaittestUtils.nextTick();
        assert.verifySteps(['p1rejected','p2rejected']);

        d1.resolve('d1');
        awaittestUtils.nextTick();

        assert.verifySteps(['okd1']);

        d3.resolve('d3');
        awaittestUtils.nextTick();

        assert.verifySteps(['okd3','p3resolved']);
    });

});

});
