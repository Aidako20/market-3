flectra.define('web.data_manager_tests',function(require){
    "usestrict";

    constconfig=require('web.config');
    constDataManager=require('web.DataManager');
    constMockServer=require('web.MockServer');
    constrpc=require('web.rpc');
    consttestUtils=require('web.test_utils');

    /**
     *Createasimpledatamanagerwithmockedfunctions:
     *-mockRPC->rpc.query
     *-isDebug->config.isDebug
     *@param{Object}params
     *@param{Object}params.archs
     *@param{Object}params.data
     *@param{Function}params.isDebug
     *@param{Function}params.mockRPC
     *@returns{DataManager}
     */
    functioncreateDataManager({archs,data,isDebug,mockRPC}){
        constdataManager=newDataManager();
        constserver=newMockServer(data,{archs});

        constserverMethods={
            asyncload_views({kwargs,model}){
                const{options,views}=kwargs;
                constfields=server.fieldsGet(model);
                constfields_views={};
                for(const[viewId,viewType]ofviews){
                    constarch=archs[[model,viewId||false,viewType].join()];
                    fields_views[viewType]=server.fieldsViewGet({arch,model,viewId});
                }
                constresult={fields,fields_views};
                if(options.load_filters){
                    result.filters=data['ir.filters'].records.filter(r=>r.model_id===model);
                }
                returnresult;
            },
            asyncget_filters({args,model}){
                returndata[model].records.filter(r=>r.model_id===args[0]);
            },
            asynccreate_or_replace({args}){
                constid=data['ir.filters'].records.reduce((i,r)=>Math.max(i,r.id),0)+1;
                constfilter=Object.assign(args[0],{id});
                data['ir.filters'].records.push(filter);
                returnid;
            },
            asyncunlink({args}){
                data['ir.filters'].records=data['ir.filters'].records.filter(
                    r=>r.id!==args[0]
                );
                returntrue;
            },
        };

        testUtils.mock.patch(rpc,{
            asyncquery({method}){
                this._super=serverMethods[method].bind(this,...arguments);
                returnmockRPC.apply(this,arguments);
            },
        });
        testUtils.mock.patch(config,{isDebug});

        returndataManager;
    }

    QUnit.module("Services",{
        beforeEach(){
            this.archs={
                'oui,10,kanban':'<kanban/>',
                'oui,20,search':'<search/>',
            };
            this.data={
                oui:{fields:{},records:[]},
                'ir.filters':{
                    fields:{
                        context:{type:"Text",string:"Context"},
                        domain:{type:"Text",string:"Domain"},
                        model_id:{type:"Selection",string:"Model"},
                        name:{type:"Char",string:"Name"},
                    },
                    records:[{
                        id:2,
                        context:'{}',
                        domain:'[]',
                        model_id:'oui',
                        name:"Favorite",
                    }]
                }
            };
            this.loadViewsParams={
                model:"oui",
                context:{},
                views_descr:[
                    [10,'kanban'],
                    [20,'search'],
                ],
            };
        },
        afterEach(){
            testUtils.mock.unpatch(rpc);
            testUtils.mock.unpatch(config);
        },
    },function(){

        QUnit.module("Datamanager");

        QUnit.test("Loadviewswithfilters(non-debugmode)",asyncfunction(assert){
            assert.expect(4);

            constdataManager=createDataManager({
                archs:this.archs,
                data:this.data,
                isDebug(){
                    returnfalse;
                },
                asyncmockRPC({method,model}){
                    assert.step([model,method].join('.'));
                    returnthis._super(...arguments);
                },
            });

            constfirstLoad=awaitdataManager.load_views(this.loadViewsParams,{
                load_filters:true,
            });
            constsecondLoad=awaitdataManager.load_views(this.loadViewsParams,{
                load_filters:true,
            });
            constfilters=awaitdataManager.load_filters({modelName:'oui'});

            assert.deepEqual(firstLoad,secondLoad,
                "querywithsameparamsandoptionsshouldyieldthesameresults");
            assert.deepEqual(firstLoad.search.favoriteFilters,filters,
                "loadfiltersshouldyieldthesameresultasthefirstload_views'filters");
            assert.verifySteps(['oui.load_views'],
                "onlyloadoncewhennotinassetsdebugging");
        });

        QUnit.test("Loadviewswithfilters(debugmode)",asyncfunction(assert){
            assert.expect(6);

            constdataManager=createDataManager({
                archs:this.archs,
                data:this.data,
                isDebug(){
                    returntrue;//assets
                },
                asyncmockRPC({method,model}){
                    assert.step([model,method].join('.'));
                    returnthis._super(...arguments);
                },
            });

            constfirstLoad=awaitdataManager.load_views(this.loadViewsParams,{
                load_filters:true,
            });
            constsecondLoad=awaitdataManager.load_views(this.loadViewsParams,{
                load_filters:true,
            });
            constfilters=awaitdataManager.load_filters({modelName:'oui'});

            assert.deepEqual(firstLoad,secondLoad,
                "querywithsameparamsandoptionsshouldyieldthesameresults");
            assert.deepEqual(firstLoad.search.favoriteFilters,filters,
                "loadfiltersshouldyieldthesameresultasthefirstload_views'filters");
            assert.verifySteps([
                'oui.load_views',
                'oui.load_views',
                'ir.filters.get_filters',
            ],"reloadeachtimewheninassetsdebugging");
        });

        QUnit.test("Cacheinvalidationandfiltersaddition/deletion",asyncfunction(assert){
            assert.expect(10);

            constdataManager=createDataManager({
                archs:this.archs,
                data:this.data,
                isDebug(){
                    returnfalse;//Cacheonlyworksif'debug!==assets'
                },
                asyncmockRPC({method,model}){
                    assert.step([model,method].join('.'));
                    returnthis._super(...arguments);
                },
            });

            //Afewunnecessary'load_filters'aredoneinthistesttoassert
            //thatthecacheinvalidationmechanicsareworking.
            letfilters;

            constfirstLoad=awaitdataManager.load_views(this.loadViewsParams,{
                load_filters:true,
            });
            //Cacheisvalid->shouldnottriggeranRPC
            filters=awaitdataManager.load_filters({modelName:'oui'});
            assert.deepEqual(firstLoad.search.favoriteFilters,filters,
                "load_filtersandload_views.searchshouldreturnthesamefilters");

            constfilterId=awaitdataManager.create_filter({
                context:"{}",
                domain:"[]",
                model_id:'oui',
                name:"Temp",
            });
            //Cacheisnotvalidanymore->triggersa'get_filters'
            filters=awaitdataManager.load_filters({modelName:'oui'});
            //Cacheisvalid->shouldnottriggeranRPC
            filters=awaitdataManager.load_filters({modelName:'oui'});

            assert.strictEqual(filters.length,2,
                "Anewfiltershouldhavebeenadded");
            assert.ok(filters.find(f=>f.id===filterId)===filters[filters.length-1],
                "Createfiltershouldreturntheidofthelastcreatedfilter");

            awaitdataManager.delete_filter(filterId);

            //Viewscacheisvalidbutfilterscacheisnot->triggersa'get_filters'
            constsecondLoad=awaitdataManager.load_views(this.loadViewsParams,{
                load_filters:true,
            });
            filters=secondLoad.search.favoriteFilters;
            //Filterscacheisonceagainvalid->noRPC
            constexpectedFilters=awaitdataManager.load_filters({modelName:'oui'});

            assert.deepEqual(filters,expectedFilters,
                "Filtersloadedbytheload_viewsshouldbeequaltotheresultofaload_filters");

            assert.verifySteps([
                'oui.load_views',
                'ir.filters.create_or_replace',
                'ir.filters.get_filters',
                'ir.filters.unlink',
                'ir.filters.get_filters',
            ],"servershouldhavebeencalledonlywhenneeded");
        });
    });
});
