flectra.define('web.registry_tests',function(require){
"usestrict";

varRegistry=require('web.Registry');

QUnit.module('core',{},function(){

    QUnit.module('Registry');

    QUnit.test('keyset',function(assert){
        assert.expect(1);

        varregistry=newRegistry();
        varfoo={};

        registry
            .add('foo',foo);

        assert.strictEqual(registry.get('foo'),foo);
    });

    QUnit.test('getinitialkeys',function(assert){
        assert.expect(1);

        varregistry=newRegistry({a:1,});
        assert.deepEqual(
            registry.keys(),
            ['a'],
            "keysonprototypeshouldbereturned"
        );
    });

    QUnit.test('getinitialentries',function(assert){
        assert.expect(1);

        varregistry=newRegistry({a:1,});
        assert.deepEqual(
            registry.entries(),
            {a:1,},
            "entriesonprototypeshouldbereturned"
        );
    });

    QUnit.test('multiget',function(assert){
        assert.expect(1);

        varfoo={};
        varbar={};
        varregistry=newRegistry({
            foo:foo,
            bar:bar,
        });
        assert.strictEqual(
            registry.getAny(['qux','grault','bar','foo']),
            bar,
            "RegistrygetAnyshouldfindfirstdefinedkey");
    });

    QUnit.test('keysandvaluesareproperlyordered',function(assert){
        assert.expect(2);

        varregistry=newRegistry();

        registry
            .add('fred','foo',3)
            .add('george','bar',2)
            .add('ronald','qux',4);

        assert.deepEqual(registry.keys(),['george','fred','ronald']);
        assert.deepEqual(registry.values(),['bar','foo','qux']);
    });

    QUnit.test("predicatepreventsinvalidvalues",function(assert){
        assert.expect(5);

        constpredicate=value=>typeofvalue==="number";
        constregistry=newRegistry(null,predicate);
        registry.onAdd((key)=>assert.step(key));

        assert.ok(registry.add("age",23));
        assert.throws(
            ()=>registry.add("name","Fred"),
            newError(`Valueofkey"name"doesnotpasstheadditionpredicate.`)
        );
        assert.deepEqual(registry.entries(),{age:23});
        assert.verifySteps(["age"]);
    });
});

});
