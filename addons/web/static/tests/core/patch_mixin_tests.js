flectra.define("web.patchMixin_tests",function(require){
"usestrict";

constpatchMixin=require('web.patchMixin');

QUnit.module('core',{},function(){

    QUnit.module('patchMixin',{},function(){

        QUnit.test('basicuse',function(assert){
            assert.expect(4);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            consta=newA();
            a.f();

            assert.ok(ainstanceofA);
            assert.verifySteps([
                'A.constructor',
                'A.f',
            ]);
        });

        QUnit.test('simplepatch',function(assert){
            assert.expect(5);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch.f');
                    }
                }
            );

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'patch.constructor',
                'A.f',
                'patch.f',
            ]);
        });

        QUnit.test('twopatchesonsamebaseclass',function(assert){
            assert.expect(7);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch1',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch1.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch1.f');
                    }
                }
            );

            A.patch('patch2',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch2.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch2.f');
                    }
                }
            );

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'patch1.constructor',
                'patch2.constructor',
                'A.f',
                'patch1.f',
                'patch2.f',
            ]);
        });

        QUnit.test('twopatcheswithsamenameonsamebaseclass',function(assert){
            assert.expect(1);

            constA=patchMixin(class{});

            A.patch('patch',T=>classextendsT{});

            //keysshouldbeunique
            assert.throws(()=>{
                A.patch('patch',T=>classextendsT{});
            });
        });

        QUnit.test('unpatch',function(assert){
            assert.expect(8);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch.f');
                    }
                }
            );

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'patch.constructor',
                'A.f',
                'patch.f',
            ]);

            A.unpatch('patch');

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'A.f',
            ]);
        });

        QUnit.test('unpatch2',function(assert){
            assert.expect(12);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch1',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch1.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch1.f');
                    }
                }
            );

            A.patch('patch2',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch2.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch2.f');
                    }
                }
            );

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'patch1.constructor',
                'patch2.constructor',
                'A.f',
                'patch1.f',
                'patch2.f',
            ]);

            A.unpatch('patch1');

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'patch2.constructor',
                'A.f',
                'patch2.f',
            ]);
        });

        QUnit.test('unpatchinexistent',function(assert){
            assert.expect(1);

            constA=patchMixin(class{});
            A.patch('patch',T=>classextendsT{});

            A.unpatch('patch');
            assert.throws(()=>{
                A.unpatch('inexistent-patch');
            });
        });

        QUnit.test('patchforspecialization',function(assert){
            assert.expect(1);

            letargs=[];

            constA=patchMixin(
                class{
                    constructor(){
                        args=['A',...arguments];
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super('patch',...arguments);
                    }
                }
            );

            newA('instantiation');

            assert.deepEqual(args,['A','patch','instantiation']);
        });

        QUnit.test('instancefields',function(assert){
            assert.expect(1);

            constA=patchMixin(
                class{
                    constructor(){
                        this.x=['A'];
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        this.x.push('patch');
                    }
                }
            );

            consta=newA();
            assert.deepEqual(a.x,['A','patch']);
        });

        QUnit.test('callinstancemethoddefinedinpatch',function(assert){
            assert.expect(3);

            constA=patchMixin(
                class{}
            );

            assert.notOk((newA()).f);

            A.patch('patch',T=>
                classextendsT{
                    f(){
                        assert.step('patch.f');
                    }
                }
            );

            (newA()).f();
            assert.verifySteps(['patch.f']);
        });

        QUnit.test('classmethods',function(assert){
            assert.expect(7);

            constA=patchMixin(
                class{
                    staticf(){
                        assert.step('A');
                    }
                }
            );

            A.f();
            assert.verifySteps(['A']);

            A.patch('patch',T=>
                classextendsT{
                    staticf(){
                        super.f();
                        assert.step('patch');
                    }
                }
            );

            A.f();
            assert.verifySteps(['A','patch']);

            A.unpatch('patch');

            A.f();
            assert.verifySteps(['A']);
        });

        QUnit.test('classfields',function(assert){
            assert.expect(4);

            classA{}
            A.foo=['A'];
            A.bar='A';

            constPatchableA=patchMixin(A);

            PatchableA.patch('patch',T=>{
                classPatchextendsT{}

                Patch.foo=[...T.foo,'patchedA'];
                Patch.bar='patchedA';

                returnPatch;
            });

            assert.deepEqual(PatchableA.foo,['A','patchedA']);
            assert.strictEqual(PatchableA.bar,'patchedA');

            PatchableA.unpatch('patch');

            assert.deepEqual(PatchableA.foo,['A']);
            assert.strictEqual(PatchableA.bar,'A');
        });

        QUnit.test('lazypatch',function(assert){
            assert.expect(4);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            consta=newA();

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        //willnotbecalled
                        assert.step('patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch.f');
                    }
                }
            );

            a.f();

            assert.verifySteps([
                'A.constructor',
                'A.f',
                'patch.f',
            ]);
        });


        QUnit.module('inheritance');

        QUnit.test('inheritingapatchableclass',function(assert){
            assert.expect(8);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            classBextendsA{
                constructor(){
                    super();
                    assert.step('B.constructor');
                }
                f(){
                    super.f();
                    assert.step('B.f');
                }
            }

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'A.f',
            ]);

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'B.constructor',
                'A.f',
                'B.f',
            ]);
        });

        QUnit.test('inheritingapatchableclassthathaspatch',function(assert){
            assert.expect(12);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch.f');
                    }
                }
            );

            classBextendsA{
                constructor(){
                    super();
                    assert.step('B.constructor');
                }
                f(){
                    super.f();
                    assert.step('B.f');
                }
            }

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'patch.constructor',
                'A.f',
                'patch.f',
            ]);

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'patch.constructor',
                'B.constructor',
                'A.f',
                'patch.f',
                'B.f',
            ]);
        });

        QUnit.test('patchinheritedpatchableclass',function(assert){
            assert.expect(10);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            constB=patchMixin(
                classextendsA{
                    constructor(){
                        super();
                        assert.step('B.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.f');
                    }
                }
            );

            B.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch.f');
                    }
                }
            );

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'A.f',
            ]);

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'B.constructor',
                'patch.constructor',
                'A.f',
                'B.f',
                'patch.f',
            ]);
        });

        QUnit.test('patchinheritedpatchedclass',function(assert){
            assert.expect(14);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('A.patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('A.patch.f');
                    }
                }
            );

            /**
             */!\WARNING/!\
             *
             *IfyouwanttopatchclassB,makeitpatchable
             *otherwiseitwillpatchclassA!
             */
            constB=patchMixin(
                classextendsA{
                    constructor(){
                        super();
                        assert.step('B.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.f');
                    }
                }
            );

            B.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('B.patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.patch.f');
                    }
                }
            );

            consta=newA();
            a.f();

            assert.verifySteps([
                'A.constructor',
                'A.patch.constructor',
                'A.f',
                'A.patch.f',
            ]);

            constb=newB();
            b.f();

            assert.verifySteps([
                'A.constructor',
                'A.patch.constructor',
                'B.constructor',
                'B.patch.constructor',
                'A.f',
                'A.patch.f',
                'B.f',
                'B.patch.f',
            ]);
        });

        QUnit.test('unpatchinheritedpatchedclass',function(assert){
            assert.expect(15);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('A.patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('A.patch.f');
                    }
                }
            );

            constB=patchMixin(
                classextendsA{
                    constructor(){
                        super();
                        assert.step('B.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.f');
                    }
                }
            );

            B.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('B.patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.patch.f');
                    }
                }
            );

            A.unpatch('patch');

            (newA()).f();

            assert.verifySteps([
                'A.constructor',
                'A.f',
            ]);

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'B.constructor',
                'B.patch.constructor',
                'A.f',
                'B.f',
                'B.patch.f',
            ]);

            B.unpatch('patch');

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'B.constructor',
                'A.f',
                'B.f',
            ]);
        });

        QUnit.test('unpatchinheritedpatchedclass2',function(assert){
            assert.expect(12);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('A.patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('A.patch.f');
                    }
                }
            );

            constB=patchMixin(
                classextendsA{
                    constructor(){
                        super();
                        assert.step('B.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.f');
                    }
                }
            );

            B.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        assert.step('B.patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('B.patch.f');
                    }
                }
            );

            B.unpatch('patch');

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'A.patch.constructor',
                'B.constructor',
                'A.f',
                'A.patch.f',
                'B.f',
            ]);

            A.unpatch('patch');

            (newB()).f();

            assert.verifySteps([
                'A.constructor',
                'B.constructor',
                'A.f',
                'B.f',
            ]);
        });

        QUnit.test('classmethods',function(assert){
            assert.expect(12);

            constA=patchMixin(
                class{
                    staticf(){
                        assert.step('A');
                    }
                }
            );

            constB=patchMixin(
                classextendsA{
                    staticf(){
                        super.f();
                        assert.step('B');
                    }
                }
            );

            A.patch('patch',T=>
                classextendsT{
                    staticf(){
                        super.f();
                        assert.step('A.patch');
                    }
                }
            );

            B.patch('patch',T=>
                classextendsT{
                    staticf(){
                        super.f();
                        assert.step('B.patch');
                    }
                }
            );

            B.f();
            assert.verifySteps(['A','A.patch','B','B.patch']);

            A.unpatch('patch');

            B.f();
            assert.verifySteps(['A','B','B.patch']);

            B.unpatch('patch');

            B.f();
            assert.verifySteps(['A','B']);
        });

        QUnit.test('classfields',function(assert){
            assert.expect(3);

            classA{}
            A.foo=['A'];
            A.bar='A';

            constPatchableA=patchMixin(A);

            classBextendsPatchableA{}
            ///!\Thisisnotdynamic
            //soifA.fooispatchedafterthisassignment
            //B.foowon'thavethepatchesofA.foo
            B.foo=[...PatchableA.foo,'B'];
            B.bar='B';

            constPatchableB=patchMixin(B);

            PatchableA.patch('patch',T=>{
                classPatchextendsT{}

                Patch.foo=[...T.foo,'patchedA'];
                Patch.bar='patchedA';

                returnPatch;
            });

            PatchableB.patch('patch',T=>{
                classPatchextendsT{}

                Patch.foo=[...T.foo,'patchedB'];
                Patch.bar='patchedB';

                returnPatch;
            });

            assert.deepEqual(PatchableB.foo,['A',/*'patchedA',*/'B','patchedB']);
            assert.deepEqual(PatchableA.foo,['A','patchedA']);
            assert.strictEqual(PatchableB.bar,'patchedB');
        });

        QUnit.test('inheritanceandlazypatch',function(assert){
            assert.expect(6);

            constA=patchMixin(
                class{
                    constructor(){
                        assert.step('A.constructor');
                    }
                    f(){
                        assert.step('A.f');
                    }
                }
            );

            classBextendsA{
                constructor(){
                    super();
                    assert.step('B.constructor');
                }
                f(){
                    super.f();
                    assert.step('B.f');
                }
            }

            constb=newB();

            A.patch('patch',T=>
                classextendsT{
                    constructor(){
                        super();
                        //willnotbecalled
                        assert.step('patch.constructor');
                    }
                    f(){
                        super.f();
                        assert.step('patch.f');
                    }
                }
            );

            b.f();

            assert.verifySteps([
                'A.constructor',
                'B.constructor',
                'A.f',
                'patch.f',
                'B.f',
            ]);
        });

        QUnit.test('patchnotpatchableclassthatinheritspatchableclass',function(assert){
            assert.expect(1);

            constA=patchMixin(class{});
            classBextendsA{}

            //classBisnotpatchable
            assert.throws(()=>{
                B.patch('patch',T=>classextendsT{});
            });
        });
    });
});
});
