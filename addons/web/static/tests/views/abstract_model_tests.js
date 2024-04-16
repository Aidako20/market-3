flectra.define('web.abstract_model_tests',function(require){
    "usestrict";

    constAbstractModel=require('web.AbstractModel');
    constDomain=require('web.Domain');

    QUnit.module('Views',{},function(){
        QUnit.module('AbstractModel');

        QUnit.test('leavesamplemodewhenunknownrouteiscalledonsampleserver',asyncfunction(assert){
            assert.expect(4);

            constModel=AbstractModel.extend({
                _isEmpty(){
                    returntrue;
                },
                async__load(){
                    if(this.isSampleModel){
                        awaitthis._rpc({model:'partner',method:'unknown'});
                    }
                },
            });

            constmodel=newModel(null,{
                modelName:'partner',
                fields:{},
                useSampleModel:true,
                SampleModel:Model,
            });

            assert.ok(model.useSampleModel);
            assert.notOk(model._isInSampleMode);

            awaitmodel.load({});

            assert.notOk(model.useSampleModel);
            assert.notOk(model._isInSampleMode);

            model.destroy();
        });

        QUnit.test("don'tcathgeneralerroronsampleserverinsamplemode",asyncfunction(assert){
            assert.expect(5);

            consterror=newError();

            constModel=AbstractModel.extend({
                _isEmpty(){
                    returntrue;
                },
                async__reload(){
                    if(this.isSampleModel){
                        awaitthis._rpc({model:'partner',method:'read_group'});
                    }
                },
                async_rpc(){
                    throwerror;
                },
            });

            constmodel=newModel(null,{
                modelName:'partner',
                fields:{},
                useSampleModel:true,
                SampleModel:Model,
            });

            assert.ok(model.useSampleModel);
            assert.notOk(model._isInSampleMode);

            awaitmodel.load({});

            assert.ok(model.useSampleModel);
            assert.ok(model._isInSampleMode);

            asyncfunctionreloadModel(){
                try{
                    awaitmodel.reload();
                }catch(e){
                    assert.strictEqual(e,error);
                }
            }

            awaitreloadModel();

            model.destroy();
        });

        QUnit.test('fetchsampledata:concurrency',asyncfunction(assert){
            assert.expect(3);

            constModel=AbstractModel.extend({
                _isEmpty(){
                    returntrue;
                },
                __get(){
                    return{isSample:!!this.isSampleModel};
                },
            });

            constmodel=newModel(null,{
                modelName:'partner',
                fields:{},
                useSampleModel:true,
                SampleModel:Model,
            });

            awaitmodel.load({domain:Domain.FALSE_DOMAIN,});

            constbeforeReload=model.get(null,{withSampleData:true});

            constreloaded=model.reload(null,{domain:Domain.TRUE_DOMAIN});
            constduringReload=model.get(null,{withSampleData:true});

            awaitreloaded;

            constafterReload=model.get(null,{withSampleData:true});

            assert.strictEqual(beforeReload.isSample,true,
                "Sampledataflagmustbetruebeforereload"
            );
            assert.strictEqual(duringReload.isSample,true,
                "Sampledataflagmustbetrueduringreload"
            );
            assert.strictEqual(afterReload.isSample,false,
                "Sampledataflagmustbetrueafterreload"
            );
        });
    });
});
