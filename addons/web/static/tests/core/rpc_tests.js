flectra.define('web.rpc_tests',function(require){
"usestrict";

varrpc=require('web.rpc');

QUnit.module('core',{},function(){

    QUnit.module('RPCBuilder');

    QUnit.test('basicrpc(route)',function(assert){
        assert.expect(1);

        varquery=rpc.buildQuery({
            route:'/my/route',
        });
        assert.strictEqual(query.route,'/my/route',"shouldhavetheproperroute");
    });

    QUnit.test('rpconroutewithparameters',function(assert){
        assert.expect(1);

        varquery=rpc.buildQuery({
            route:'/my/route',
            params:{hey:'there',model:'test'},
        });

        assert.deepEqual(query.params,{hey:'there',model:'test'},
                    "shouldtransfertheproperparameters");
    });

    QUnit.test('basicrpc,withnocontext',function(assert){
        assert.expect(1);

        varquery=rpc.buildQuery({
            model:'partner',
            method:'test',
            kwargs:{},
        });
        assert.notOk(query.params.kwargs.context,
            "doesnotautomaticallyaddacontext");
    });

    QUnit.test('basicrpc,withcontext',function(assert){
        assert.expect(1);

        varquery=rpc.buildQuery({
            model:'partner',
            method:'test',
            context:{a:1},
        });

        assert.deepEqual(query.params.kwargs.context,{a:1},
            "properlytransferthecontext");
    });

    QUnit.test('basicrpc,withcontext,part2',function(assert){
        assert.expect(1);

        varquery=rpc.buildQuery({
            model:'partner',
            method:'test',
            kwargs:{context:{a:1}},
        });

        assert.deepEqual(query.params.kwargs.context,{a:1},
            "properlytransferthecontext");

    });

    QUnit.test('basicrpc(methodofmodel)',function(assert){
        assert.expect(3);

        varquery=rpc.buildQuery({
            model:'partner',
            method:'test',
            kwargs:{context:{a:1}},
        });

        assert.strictEqual(query.route,'/web/dataset/call_kw/partner/test',
            "shouldcalltheproperroute");
        assert.strictEqual(query.params.model,'partner',
            "shouldcorrectlyspecifythemodel");
        assert.strictEqual(query.params.method,'test',
            "shouldcorrectlyspecifythemethod");
    });

    QUnit.test('rpcwithargsandkwargs',function(assert){
        assert.expect(4);
        varquery=rpc.buildQuery({
            model:'partner',
            method:'test',
            args:['arg1',2],
            kwargs:{k:78},
        });

        assert.strictEqual(query.route,'/web/dataset/call_kw/partner/test',
            "shouldcalltheproperroute");
        assert.strictEqual(query.params.args[0],'arg1',
            "shouldcallwithcorrectargs");
        assert.strictEqual(query.params.args[1],2,
            "shouldcallwithcorrectargs");
        assert.strictEqual(query.params.kwargs.k,78,
            "shouldcallwithcorrectkargs");
    });

    QUnit.test('search_readcontroller',function(assert){
        assert.expect(1);
        varquery=rpc.buildQuery({
            route:'/web/dataset/search_read',
            model:'partner',
            domain:['a','=',1],
            fields:['name'],
            limit:32,
            offset:2,
            orderBy:[{name:'yop',asc:true},{name:'aa',asc:false}],
        });
        assert.deepEqual(query.params,{
            context:{},
            domain:['a','=',1],
            fields:['name'],
            limit:32,
            offset:2,
            model:'partner',
            sort:'yopASC,aaDESC',
        },"shouldhavecorrectargs");
    });

    QUnit.test('search_readmethod',function(assert){
        assert.expect(1);
        varquery=rpc.buildQuery({
            model:'partner',
            method:'search_read',
            domain:['a','=',1],
            fields:['name'],
            limit:32,
            offset:2,
            orderBy:[{name:'yop',asc:true},{name:'aa',asc:false}],
        });
        assert.deepEqual(query.params,{
            args:[],
            kwargs:{
                domain:['a','=',1],
                fields:['name'],
                offset:2,
                limit:32,
                order:'yopASC,aaDESC'
            },
            method:'search_read',
            model:'partner'
        },"shouldhavecorrectkwargs");
    });

    QUnit.test('search_readwithargs',function(assert){
        assert.expect(1);
        varquery=rpc.buildQuery({
            model:'partner',
            method:'search_read',
            args:[
                ['a','=',1],
                ['name'],
                2,
                32,
                'yopASC,aaDESC',
            ]
        });
        assert.deepEqual(query.params,{
            args:[['a','=',1],['name'],2,32,'yopASC,aaDESC'],
            kwargs:{},
            method:'search_read',
            model:'partner'
        },"shouldhavecorrectargs");
    });

    QUnit.test('read_group',function(assert){
        assert.expect(2);

        varquery=rpc.buildQuery({
            model:'partner',
            method:'read_group',
            domain:['a','=',1],
            fields:['name'],
            groupBy:['product_id'],
            context:{abc:'def'},
            lazy:true,
        });

        assert.deepEqual(query.params,{
            args:[],
            kwargs:{
                context:{abc:'def'},
                domain:['a','=',1],
                fields:['name'],
                groupby:['product_id'],
                lazy:true,
            },
            method:'read_group',
            model:'partner',
        },"shouldhavecorrectargs");
        assert.equal(query.route,'/web/dataset/call_kw/partner/read_group',
            "shouldcallcorrectroute");
    });

    QUnit.test('read_groupwithkwargs',function(assert){
        assert.expect(1);

        varquery=rpc.buildQuery({
            model:'partner',
            method:'read_group',
            domain:['a','=',1],
            fields:['name'],
            groupBy:['product_id'],
            lazy:false,
            kwargs:{context:{abc:'def'}}
        });

        assert.deepEqual(query.params,{
            args:[],
            kwargs:{
                context:{abc:'def'},
                domain:['a','=',1],
                fields:['name'],
                groupby:['product_id'],
                lazy:false,
            },
            method:'read_group',
            model:'partner',
        },"shouldhavecorrectargs");
    });

    QUnit.test('read_groupwithnodomain,norfields',function(assert){
        assert.expect(7);
        varquery=rpc.buildQuery({
            model:'partner',
            method:'read_group',
        });

        assert.deepEqual(query.params.kwargs.domain,[],"shouldhave[]asdefaultdomain");
        assert.deepEqual(query.params.kwargs.fields,[],"shouldhavefalseasdefaultfields");
        assert.deepEqual(query.params.kwargs.groupby,[],"shouldhavefalseasdefaultgroupby");
        assert.deepEqual(query.params.kwargs.offset,undefined,"shouldnotenforceadefaultvalueforoffst");
        assert.deepEqual(query.params.kwargs.limit,undefined,"shouldnotenforceadefaultvalueforlimit");
        assert.deepEqual(query.params.kwargs.orderby,undefined,"shouldnotenforceadefaultvaluefororderby");
        assert.deepEqual(query.params.kwargs.lazy,undefined,"shouldnotenforceadefaultvalueforlazy");
    });

    QUnit.test('read_groupwithargsandkwargs',function(assert){
        assert.expect(9);
        varquery=rpc.buildQuery({
            model:'partner',
            method:'read_group',
            kwargs:{
                domain:['name','=','saucisse'],
                fields:['category_id'],
                groupby:['country_id'],
            },
        });

        assert.deepEqual(query.params.kwargs.domain,['name','=','saucisse'],"shouldhave['name','=','saucisse']category_idasdefaultdomain");
        assert.deepEqual(query.params.kwargs.fields,['category_id'],"shouldhavecategory_idasdefaultfields");
        assert.deepEqual(query.params.kwargs.groupby,['country_id'],"shouldhavecountry_idasdefaultgroupby");

        varquery=rpc.buildQuery({
            model:'partner',
            method:'read_group',
            args:[['name','=','saucisse']],
            kwargs:{
                fields:['category_id'],
                groupby:['country_id'],
            },
        });

        assert.deepEqual(query.params.kwargs.domain,undefined,"shouldnotenforceadefaultvaluefordomain");
        assert.deepEqual(query.params.kwargs.fields,['category_id'],"shouldhavecategory_idasdefaultfields");
        assert.deepEqual(query.params.kwargs.groupby,['country_id'],"shouldhavecountry_idasdefaultgroupby");

        varquery=rpc.buildQuery({
            model:'partner',
            method:'read_group',
            args:[['name','=','saucisse'],['category_id'],['country_id']],
        });

        assert.deepEqual(query.params.kwargs.domain,undefined,"shouldnotenforceadefaultvaluefordomain");
        assert.deepEqual(query.params.kwargs.fields,undefined,"shouldnotenforceadefaultvaluefor fields");
        assert.deepEqual(query.params.kwargs.groupby,undefined,"shouldnotenforceadefaultvaluefor groupby");
    });

    QUnit.test('search_readwithnodomain,norfields',function(assert){
        assert.expect(5);
        varquery=rpc.buildQuery({
            model:'partner',
            method:'search_read',
        });

        assert.deepEqual(query.params.kwargs.domain,undefined,"shouldnotenforceadefaultvaluefordomain");
        assert.deepEqual(query.params.kwargs.fields,undefined,"shouldnotenforceadefaultvalueforfields");
        assert.deepEqual(query.params.kwargs.offset,undefined,"shouldnotenforceadefaultvalueforoffset");
        assert.deepEqual(query.params.kwargs.limit,undefined,"shouldnotenforceadefaultvalueforlimit");
        assert.deepEqual(query.params.kwargs.order,undefined,"shouldnotenforceadefaultvaluefororderby");
    });

    QUnit.test('search_readcontrollerwithnodomain,norfields',function(assert){
        assert.expect(5);
        varquery=rpc.buildQuery({
            model:'partner',
            route:'/web/dataset/search_read',
        });

        assert.deepEqual(query.params.domain,undefined,"shouldnotenforceadefaultvaluefordomain");
        assert.deepEqual(query.params.fields,undefined,"shouldnotenforceadefaultvalueforfields");
        assert.deepEqual(query.params.offset,undefined,"shouldnotenforceadefaultvalueforgroupby");
        assert.deepEqual(query.params.limit,undefined,"shouldnotenforceadefaultvalueforlimit");
        assert.deepEqual(query.params.sort,undefined,"shouldnotenforceadefaultvaluefororder");
    });
});

});
