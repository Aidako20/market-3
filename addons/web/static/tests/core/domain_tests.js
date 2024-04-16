flectra.define('web.domain_tests',function(require){
"usestrict";

varDomain=require('web.Domain');

QUnit.module('core',{},function(){

    QUnit.module('domain');

    QUnit.test("empty",function(assert){
        assert.expect(1);
        assert.ok(newDomain([]).compute({}));
    });

    QUnit.test("basic",function(assert){
        assert.expect(3);

        varfields={
            a:3,
            group_method:'line',
            select1:'day',
            rrule_type:'monthly',
        };
        assert.ok(newDomain([['a','=',3]]).compute(fields));
        assert.ok(newDomain([['group_method','!=','count']]).compute(fields));
        assert.ok(newDomain([['select1','=','day'],['rrule_type','=','monthly']]).compute(fields));
    });

    QUnit.test("or",function(assert){
        assert.expect(3);

        varweb={
            section_id:null,
            user_id:null,
            member_ids:null,
        };
        varcurrentDomain=[
            '|',
                ['section_id','=',42],
                '|',
                    ['user_id','=',3],
                    ['member_ids','in',[3]]
        ];
        assert.ok(newDomain(currentDomain).compute(_.extend({},web,{section_id:42})));
        assert.ok(newDomain(currentDomain).compute(_.extend({},web,{user_id:3})));
        assert.ok(newDomain(currentDomain).compute(_.extend({},web,{member_ids:3})));
    });

    QUnit.test("not",function(assert){
        assert.expect(2);

        varfields={
            a:5,
            group_method:'line',
        };
        assert.ok(newDomain(['!',['a','=',3]]).compute(fields));
        assert.ok(newDomain(['!',['group_method','=','count']]).compute(fields));
    });

    QUnit.test("domainsinitializedwithanumber",function(assert){
        assert.expect(2);

        assert.ok(newDomain(1).compute({}));
        assert.notOk(newDomain(0).compute({}));
    });

    QUnit.test("invaliddomainsshouldnotsucceed",function(assert){
        assert.expect(3);
        assert.throws(
            ()=>newDomain(['|',['hr_presence_state','=','absent']]),
            /invaliddomain.*\(missing1segment/
        );
        assert.throws(
            ()=>newDomain(['|','|',['hr_presence_state','=','absent'],['attendance_state','=','checked_in']]),
            /invaliddomain.*\(missing1segment/
        );
        assert.throws(
            ()=>newDomain(['&',['composition_mode','!=','mass_post']]),
            /invaliddomain.*\(missing1segment/
        );
    });

    QUnit.test("domain<=>condition",function(assert){
        assert.expect(3);

        vardomain=[
            '|',
                '|',
                    '|',
                        '&',['doc.amount','>',33],['doc.toto','!=',null],
                        '&',['doc.bidule.active','=',true],['truc','in',[2,3]],
                    ['gogo','=','gogovalue'],
                ['gogo','!=',false]
        ];
        varcondition='((doc.amount>33anddoc.totoisnotNoneordoc.bidule.activeisTrueandtrucin[2,3])orgogo=="gogovalue")orgogo';

        assert.equal(Domain.prototype.domainToCondition(domain),condition);
        assert.deepEqual(Domain.prototype.conditionToDomain(condition),domain);
        assert.deepEqual(Domain.prototype.conditionToDomain(
            'docandtotoisNoneornottata'),
            ['|','&',['doc','!=',false],['toto','=',null],['tata','=',false]]);
    });

    QUnit.test("condition'afieldisset'doesnotconverttoadomain",function(assert){
        assert.expect(1);
        varexpected=[["doc.blabla","!=",false]];
        varcondition="doc.blabla";

        varactual=Domain.prototype.conditionToDomain(condition);

        assert.deepEqual(actual,expected);
    });

    QUnit.test("conditionwithafunctionshouldfail",function(assert){
        assert.expect(1);
        varcondition="doc.blabla()";

        assert.throws(function(){Domain.prototype.conditionToDomain(condition);});
    });

    QUnit.test("emptyconditionshouldnotfail",function(assert){
        assert.expect(2);
        varcondition="";
        varactual=Domain.prototype.conditionToDomain(condition);
        assert.strictEqual(typeof(actual),typeof([]));
        assert.strictEqual(actual.length,0);
    });
    QUnit.test("undefinedconditionshouldnotfail",function(assert){
        assert.expect(2);
        varcondition=undefined;
        varactual=Domain.prototype.conditionToDomain(condition);
        assert.strictEqual(typeof(actual),typeof([]));
        assert.strictEqual(actual.length,0);
    });

    QUnit.test("computetruedomain",function(assert){
        assert.expect(1);
        assert.ok(newDomain(Domain.TRUE_DOMAIN).compute({}));
    });

    QUnit.test("computefalsedomain",function(assert){
        assert.expect(1);
        assert.notOk(newDomain(Domain.FALSE_DOMAIN).compute({}));
    });

    QUnit.test("arrayToString",function(assert){
        assert.expect(14);

        constarrayToString=Domain.prototype.arrayToString;

        //domainscontainingnull,falseortrue
        assert.strictEqual(arrayToString([['name','=',null]]),'[["name","=",None]]');
        assert.strictEqual(arrayToString([['name','=',false]]),'[["name","=",False]]');
        assert.strictEqual(arrayToString([['name','=',true]]),'[["name","=",True]]');
        assert.strictEqual(arrayToString([['name','=','null']]),'[["name","=","null"]]');
        assert.strictEqual(arrayToString([['name','=','false']]),'[["name","=","false"]]');
        assert.strictEqual(arrayToString([['name','=','true']]),'[["name","=","true"]]');
        assert.strictEqual(arrayToString([['name','in',[true,false]]]),'[["name","in",[True,False]]]');
        assert.strictEqual(arrayToString([['name','in',[null]]]),'[["name","in",[None]]]');
        
        assert.strictEqual(arrayToString([['name','in',["foo","bar"]]]),'[["name","in",["foo","bar"]]]');
        assert.strictEqual(arrayToString([['name','in',[1,2]]]),'[["name","in",[1,2]]]');
        assert.strictEqual(arrayToString(),'[]');

        assert.strictEqual(arrayToString(['&',['name','=','foo'],['type','=','bar']]),'["&",["name","=","foo"],["type","=","bar"]]');
        assert.strictEqual(arrayToString(['|',['name','=','foo'],['type','=','bar']]),'["|",["name","=","foo"],["type","=","bar"]]');

        //stringdomainsarenotprocessed
        assert.strictEqual(arrayToString('[["name","ilike","foo"]]'),'[["name","ilike","foo"]]');
    });

    QUnit.test("like,=like,ilikeand=ilike",function(assert){
        assert.expect(16);

        assert.ok(newDomain([['a','like','value']]).compute({a:'value'}));
        assert.ok(newDomain([['a','like','value']]).compute({a:'somevalue'}));
        assert.notOk(newDomain([['a','like','value']]).compute({a:'SomeValue'}));
        assert.notOk(newDomain([['a','like','value']]).compute({a:false}));

        assert.ok(newDomain([['a','=like','%value']]).compute({a:'value'}));
        assert.ok(newDomain([['a','=like','%value']]).compute({a:'somevalue'}));
        assert.notOk(newDomain([['a','=like','%value']]).compute({a:'SomeValue'}));
        assert.notOk(newDomain([['a','=like','%value']]).compute({a:false}));

        assert.ok(newDomain([['a','ilike','value']]).compute({a:'value'}));
        assert.ok(newDomain([['a','ilike','value']]).compute({a:'somevalue'}));
        assert.ok(newDomain([['a','ilike','value']]).compute({a:'SomeValue'}));
        assert.notOk(newDomain([['a','ilike','value']]).compute({a:false}));

        assert.ok(newDomain([['a','=ilike','%value']]).compute({a:'value'}));
        assert.ok(newDomain([['a','=ilike','%value']]).compute({a:'somevalue'}));
        assert.ok(newDomain([['a','=ilike','%value']]).compute({a:'SomeValue'}));
        assert.notOk(newDomain([['a','=ilike','%value']]).compute({a:false}));
    });
});
});
