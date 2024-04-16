flectra.define('web.class_tests',function(require){
"usestrict";

varClass=require('web.Class');

QUnit.module('core',{},function(){

    QUnit.module('Class');


    QUnit.test('Basicclasscreation',function(assert){
        assert.expect(2);

        varC=Class.extend({
            foo:function(){
                returnthis.somevar;
            }
        });
        vari=newC();
        i.somevar=3;

        assert.ok(iinstanceofC);
        assert.strictEqual(i.foo(),3);
    });

    QUnit.test('Classinitialization',function(assert){
        assert.expect(2);

        varC1=Class.extend({
            init:function(){
                this.foo=3;
            }
        });
        varC2=Class.extend({
            init:function(arg){
                this.foo=arg;
            }
        });

        vari1=newC1(),
            i2=newC2(42);

        assert.strictEqual(i1.foo,3);
        assert.strictEqual(i2.foo,42);
    });

    QUnit.test('Inheritance',function(assert){
        assert.expect(3);

        varC0=Class.extend({
            foo:function(){
                return1;
            }
        });
        varC1=C0.extend({
            foo:function(){
                return1+this._super();
            }
        });
        varC2=C1.extend({
            foo:function(){
                return1+this._super();
            }
        });

        assert.strictEqual(newC0().foo(),1);
        assert.strictEqual(newC1().foo(),2);
        assert.strictEqual(newC2().foo(),3);
    });

    QUnit.test('In-placeextension',function(assert){
        assert.expect(4);

        varC0=Class.extend({
            foo:function(){
                return3;
            },
            qux:function(){
                return3;
            },
            bar:3
        });

        C0.include({
            foo:function(){
                return5;
            },
            qux:function(){
                return2+this._super();
            },
            bar:5,
            baz:5
        });

        assert.strictEqual(newC0().bar,5);
        assert.strictEqual(newC0().baz,5);
        assert.strictEqual(newC0().foo(),5);
        assert.strictEqual(newC0().qux(),5);
    });

    QUnit.test('In-placeextensionandinheritance',function(assert){
        assert.expect(4);

        varC0=Class.extend({
            foo:function(){return1;},
            bar:function(){return1;}
        });
        varC1=C0.extend({
            foo:function(){return1+this._super();}
        });
        assert.strictEqual(newC1().foo(),2);
        assert.strictEqual(newC1().bar(),1);

        C1.include({
            foo:function(){return2+this._super();},
            bar:function(){return1+this._super();}
        });
        assert.strictEqual(newC1().foo(),4);
        assert.strictEqual(newC1().bar(),2);
    });

    QUnit.test('In-placeextensionsalterexistinginstances',function(assert){
        assert.expect(4);

        varC0=Class.extend({
            foo:function(){return1;},
            bar:function(){return1;}
        });
        vari=newC0();
        assert.strictEqual(i.foo(),1);
        assert.strictEqual(i.bar(),1);

        C0.include({
            foo:function(){return2;},
            bar:function(){return2+this._super();}
        });
        assert.strictEqual(i.foo(),2);
        assert.strictEqual(i.bar(),3);
    });

    QUnit.test('In-placeextensionofsubclassedtypes',function(assert){
        assert.expect(3);

        varC0=Class.extend({
            foo:function(){return1;},
            bar:function(){return1;}
        });
        varC1=C0.extend({
            foo:function(){return1+this._super();},
            bar:function(){return1+this._super();}
        });
        vari=newC1();

        assert.strictEqual(i.foo(),2);

        C0.include({
            foo:function(){return2;},
            bar:function(){return2+this._super();}
        });

        assert.strictEqual(i.foo(),3);
        assert.strictEqual(i.bar(),4);
    });


});

});
