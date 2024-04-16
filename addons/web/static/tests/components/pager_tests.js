flectra.define('web.pager_tests',function(require){
    "usestrict";

    constPager=require('web.Pager');
    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;
    const{createComponent}=testUtils;

    QUnit.module('Components',{},function(){

        QUnit.module('Pager');

        QUnit.test('basicinteractions',asyncfunction(assert){
            assert.expect(2);

            constpager=awaitcreateComponent(Pager,{
                props:{
                    currentMinimum:1,
                    limit:4,
                    size:10,
                },
                intercepts:{
                    'pager-changed':function(ev){
                        Object.assign(this.state,ev.detail);
                    },
                },
            });

            assert.strictEqual(cpHelpers.getPagerValue(pager),"1-4",
                "currentMinimumshouldbesetto1");

            awaitcpHelpers.pagerNext(pager);

            assert.strictEqual(cpHelpers.getPagerValue(pager),"5-8",
                "currentMinimumshouldnowbe5");

            pager.destroy();
        });

        QUnit.test('editthepager',asyncfunction(assert){
            assert.expect(4);

            constpager=awaitcreateComponent(Pager,{
                props:{
                    currentMinimum:1,
                    limit:4,
                    size:10,
                },
                intercepts:{
                    'pager-changed':function(ev){
                        Object.assign(this.state,ev.detail);
                    },
                },
            });

            awaittestUtils.dom.click(pager.el.querySelector('.o_pager_value'));

            assert.containsOnce(pager,'input',
                "thepagershouldcontainaninput");
            assert.strictEqual(cpHelpers.getPagerValue(pager),"1-4",
                "theinputshouldhavecorrectvalue");

            //changethelimit
            awaitcpHelpers.setPagerValue(pager,"1-6");

            assert.containsNone(pager,'input',
                "thepagershouldnotcontainaninputanymore");
            assert.strictEqual(cpHelpers.getPagerValue(pager),"1-6",
                "thelimitshouldhavebeenupdated");

            pager.destroy();
        });

        QUnit.test("keydownonpagerwithsamevalue",asyncfunction(assert){
            assert.expect(7);

            constpager=awaitcreateComponent(Pager,{
                props:{
                    currentMinimum:1,
                    limit:4,
                    size:10,
                },
                intercepts:{
                    "pager-changed":()=>assert.step("pager-changed"),
                },
            });

            //Entereditmode
            awaittestUtils.dom.click(pager.el.querySelector('.o_pager_value'));

            assert.containsOnce(pager,"input");
            assert.strictEqual(cpHelpers.getPagerValue(pager),"1-4");
            assert.verifySteps([]);

            //Exiteditmode
            awaittestUtils.dom.triggerEvent(pager.el.querySelector('input'),"keydown",{key:"Enter"});

            assert.containsNone(pager,"input");
            assert.strictEqual(cpHelpers.getPagerValue(pager),"1-4");
            assert.verifySteps(["pager-changed"]);

            pager.destroy();
        });

        QUnit.test('pagervalueformatting',asyncfunction(assert){
            assert.expect(8);

            constpager=awaitcreateComponent(Pager,{
                props:{
                    currentMinimum:1,
                    limit:4,
                    size:10,
                },
                intercepts:{
                    'pager-changed':function(ev){
                        Object.assign(this.state,ev.detail);
                    },
                },
            });

            assert.strictEqual(cpHelpers.getPagerValue(pager),"1-4","Initialvalueshouldbecorrect");

            asyncfunctioninputAndAssert(input,expected,reason){
                awaitcpHelpers.setPagerValue(pager,input);
                assert.strictEqual(cpHelpers.getPagerValue(pager),expected,
                    `Pagervalueshouldbe"${expected}"whengiven"${input}":${reason}`);
            }

            awaitinputAndAssert("4-4","4","valuesaresquashedwhenminimum=maximum");
            awaitinputAndAssert("1-11","1-10","maximumisflooredtosizewhenoutofrange");
            awaitinputAndAssert("20-15","10","combinationofthe2assertionsabove");
            awaitinputAndAssert("6-5","10","fallbacktopreviousvaluewhenminimum>maximum");
            awaitinputAndAssert("definitelyValidNumber","10","fallbacktopreviousvalueifnotanumber");
            awaitinputAndAssert("1, 2  ","1-2","valueisnormalizedandacceptsseveralseparators");
            awaitinputAndAssert("3 8","3-8","valueacceptswhitespace(s)asaseparator");

            pager.destroy();
        });

        QUnit.test('pagerdisabling',asyncfunction(assert){
            assert.expect(10);

            constreloadPromise=testUtils.makeTestPromise();
            constpager=awaitcreateComponent(Pager,{
                props:{
                    currentMinimum:1,
                    limit:4,
                    size:10,
                },
                intercepts:{
                    //Thegoalhereistotestthereactivityofthepager;ina
                    //typicalviews,wedisablethepagerafterswitchingpage
                    //toavoidswitchingtwicewiththesameaction(doubleclick).
                    'pager-changed':asyncfunction(ev){
                        //1.Simulatea(long)serveraction
                        awaitreloadPromise;
                        //2.Updatetheviewwithloadeddata
                        Object.assign(this.state,ev.detail);
                    },
                },
            });
            constpagerButtons=pager.el.querySelectorAll('button');

            //Clickandcheckbuttonisdisabled
            awaitcpHelpers.pagerNext(pager);
            assert.ok(pager.el.querySelector('button.o_pager_next').disabled);
            //Trytoeditthepagervalue
            awaittestUtils.dom.click(pager.el.querySelector('.o_pager_value'));

            assert.strictEqual(pagerButtons.length,2,"thetwobuttonsshouldbedisplayed");
            assert.ok(pagerButtons[0].disabled,"'previous'isdisabled");
            assert.ok(pagerButtons[1].disabled,"'next'isdisabled");
            assert.strictEqual(pager.el.querySelector('.o_pager_value').tagName,'SPAN',
                "pagereditionisprevented");

            //Serveractionisdone
            reloadPromise.resolve();
            awaittestUtils.nextTick();

            assert.strictEqual(pagerButtons.length,2,"thetwobuttonsshouldbedisplayed");
            assert.notOk(pagerButtons[0].disabled,"'previous'isenabled");
            assert.notOk(pagerButtons[1].disabled,"'next'isenabled");
            assert.strictEqual(cpHelpers.getPagerValue(pager),"5-8","valuehasbeenupdated");

            awaittestUtils.dom.click(pager.el.querySelector('.o_pager_value'));

            assert.strictEqual(pager.el.querySelector('.o_pager_value').tagName,'INPUT',
                "pagereditionisre-enabled");

            pager.destroy();
        });
    });
});
