flectra.define('point_of_sale.tests.ComponentRegistry',function(require){
    'usestrict';

    constRegistries=require('point_of_sale.Registries');

    QUnit.module('unittestsforComponentRegistry',{
        before(){},
    });

    QUnit.test('basicextend',asyncfunction(assert){
        assert.expect(5);

        classA{
            constructor(){
                assert.step('A');
            }
        }
        Registries.Component.add(A);

        letA1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A1');
                }
            };
        Registries.Component.extend(A,A1);

        Registries.Component.freeze();

        constRegA=Registries.Component.get(A);
        leta=newRegA();
        assert.verifySteps(['A','A1']);
        assert.ok(ainstanceofRegA);
        assert.ok(RegA.name==='A');
    });

    QUnit.test('addByExtending',asyncfunction(assert){
        assert.expect(8);

        classA{
            constructor(){
                assert.step('A');
            }
        }
        Registries.Component.add(A);

        letB=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B');
                }
            };
        Registries.Component.addByExtending(B,A);

        letA1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A1');
                }
            };
        Registries.Component.extend(A,A1);

        letA2=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A2');
                }
            };
        Registries.Component.extend(A,A2);

        Registries.Component.freeze();

        constRegA=Registries.Component.get(A);
        constRegB=Registries.Component.get(B);
        letb=newRegB();
        assert.verifySteps(['A','A1','A2','B']);
        assert.ok(binstanceofRegA);
        assert.ok(binstanceofRegB);
        assert.ok(RegB.name==='B');
    });

    QUnit.test('extendtheonethatisaddedbyextending',asyncfunction(assert){
        assert.expect(6);

        classA{
            constructor(){
                assert.step('A');
            }
        }
        Registries.Component.add(A);

        letB=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B');
                }
            };
        Registries.Component.addByExtending(B,A);

        letB1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B1');
                }
            };
        Registries.Component.extend(B,B1);

        letB2=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B2');
                }
            };
        Registries.Component.extend(B,B2);

        letA1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A1');
                }
            };
        Registries.Component.extend(A,A1);

        Registries.Component.freeze();

        constRegB=Registries.Component.get(B);
        newRegB();
        assert.verifySteps(['A','A1','B','B1','B2']);
    });

    QUnit.test('addByExtendingbasedonaddedbyextending',asyncfunction(assert){
        assert.expect(10);

        classA{
            constructor(){
                assert.step('A');
            }
        }
        Registries.Component.add(A);

        letB=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B');
                }
            };
        Registries.Component.addByExtending(B,A);

        letA1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A1');
                }
            };
        Registries.Component.extend(A,A1);

        letC=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('C');
                }
            };
        Registries.Component.addByExtending(C,B);

        letB7=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B7');
                }
            };
        Registries.Component.extend(B,B7);

        Registries.Component.freeze();

        constRegA=Registries.Component.get(A);
        constRegB=Registries.Component.get(B);
        constRegC=Registries.Component.get(C);
        letc=newRegC();
        assert.verifySteps(['A','A1','B','B7','C']);
        assert.ok(cinstanceofRegA);
        assert.ok(cinstanceofRegB);
        assert.ok(cinstanceofRegC);
        assert.ok(RegC.name==='C');
    });

    QUnit.test('deeperinheritance',asyncfunction(assert){
        assert.expect(9);

        classA{
            constructor(){
                assert.step('A');
            }
        }
        Registries.Component.add(A);

        letB=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B');
                }
            };
        Registries.Component.addByExtending(B,A);

        letA1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A1');
                }
            };
        Registries.Component.extend(A,A1);

        letC=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('C');
                }
            };
        Registries.Component.addByExtending(C,B);

        letB2=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B2');
                }
            };
        Registries.Component.extend(B,B2);

        letB3=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('B3');
                }
            };
        Registries.Component.extend(B,B3);

        letA9=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A9');
                }
            };
        Registries.Component.extend(A,A9);

        letE=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('E');
                }
            };
        Registries.Component.addByExtending(E,C);

        Registries.Component.freeze();

        //|A|=>A9->A1->A
        //|B|=>B3->B2->B->|A|
        //|C|=>C->|B|
        //|E|=>E->|C|

        new(Registries.Component.get(E))();
        assert.verifySteps(['A','A1','A9','B','B2','B3','C','E']);
    });

    QUnit.test('mixins?',asyncfunction(assert){
        assert.expect(12);

        classA{
            constructor(){
                assert.step('A');
            }
        }
        Registries.Component.add(A);

        letMixin=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('Mixin');
                }
                mixinMethod(){
                    return'mixinMethod';
                }
                getmixinGetter(){
                    return'mixinGetter';
                }
            };

        //usethemixinwhendeclaringB.
        letB=x=>
            classextendsMixin(x){
                constructor(){
                    super();
                    assert.step('B');
                }
            };
        Registries.Component.addByExtending(B,A);

        letA1=x=>
            classextendsx{
                constructor(){
                    super();
                    assert.step('A1');
                }
            };
        Registries.Component.extend(A,A1);

        Registries.Component.freeze();

        B=Registries.Component.get(B);
        constb=newB();
        assert.verifySteps(['A','A1','Mixin','B']);
        //instanceofBshouldhavethemixinproperties
        assert.strictEqual(b.mixinMethod(),'mixinMethod');
        assert.strictEqual(b.mixinGetter,'mixinGetter');

        //instanceofAshouldnothavethemixinproperties
        A=Registries.Component.get(A);
        consta=newA();
        assert.verifySteps(['A','A1']);
        assert.notOk(a.mixinMethod);
        assert.notOk(a.mixinGetter);
    });

    QUnit.test('extendingmethods',asyncfunction(assert){
        assert.expect(16);

        classA{
            foo(){
                assert.step('Afoo');
            }
        }
        Registries.Component.add(A);

        letB=x=>
            classextendsx{
                bar(){
                    assert.step('Bbar');
                }
            };
        Registries.Component.addByExtending(B,A);

        letA1=x=>
            classextendsx{
                bar(){
                    assert.step('A1bar');
                    //shouldonlybeforA.
                }
            };
        Registries.Component.extend(A,A1);

        letB1=x=>
            classextendsx{
                foo(){
                    super.foo();
                    assert.step('B1foo');
                }
            };
        Registries.Component.extend(B,B1);

        letC=x=>
            classextendsx{
                foo(){
                    super.foo();
                    assert.step('Cfoo');
                }
                bar(){
                    super.bar();
                    assert.step('Cbar');
                }
            };
        Registries.Component.addByExtending(C,B);

        Registries.Component.freeze();

        A=Registries.Component.get(A);
        B=Registries.Component.get(B);
        C=Registries.Component.get(C);
        consta=newA();
        constb=newB();
        constc=newC();

        a.foo();
        assert.verifySteps(['Afoo']);
        b.foo();
        assert.verifySteps(['Afoo','B1foo']);
        c.foo();
        assert.verifySteps(['Afoo','B1foo','Cfoo']);

        a.bar();
        assert.verifySteps(['A1bar']);
        b.bar();
        assert.verifySteps(['Bbar']);
        c.bar();
        assert.verifySteps(['Bbar','Cbar']);
    });
});
