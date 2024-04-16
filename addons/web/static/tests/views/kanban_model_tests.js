flectra.define('web.kanban_model_tests',function(require){
"usestrict";

varKanbanModel=require('web.KanbanModel');
vartestUtils=require('web.test_utils');

varcreateModel=testUtils.createModel;

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    active:{string:"Active",type:"boolean",default:true},
                    display_name:{string:"STRING",type:'char'},
                    foo:{string:"Foo",type:'char'},
                    bar:{string:"Bar",type:'integer'},
                    qux:{string:"Qux",type:'many2one',relation:'partner'},
                    product_id:{string:"Favoriteproduct",type:'many2one',relation:'product'},
                    product_ids:{string:"Favoriteproducts",type:'one2many',relation:'product'},
                    category:{string:"CategoryM2M",type:'many2many',relation:'partner_type'},
                },
                records:[
                    {id:1,foo:'blip',bar:1,product_id:37,category:[12],display_name:"firstpartner"},
                    {id:2,foo:'gnap',bar:2,product_id:41,display_name:"secondpartner"},
                ],
                onchanges:{},
            },
            product:{
                fields:{
                    name:{string:"ProductName",type:"char"}
                },
                records:[
                    {id:37,display_name:"xphone"},
                    {id:41,display_name:"xpad"}
                ]
            },
            partner_type:{
                fields:{
                    display_name:{string:"PartnerType",type:"char"}
                },
                records:[
                    {id:12,display_name:"gold"},
                    {id:14,display_name:"silver"},
                    {id:15,display_name:"bronze"}
                ]
            },
        };

        //addrelatedfieldstocategory.
        this.data.partner.fields.category.relatedFields=
            $.extend(true,{},this.data.partner_type.fields);
        this.params={
            fields:this.data.partner.fields,
            limit:40,
            modelName:'partner',
            openGroupByDefault:true,
            viewType:'kanban',
        };
    },
},function(){

    QUnit.module('KanbanModel');

    QUnit.test('loadgrouped+addanewgroup',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(22);

        varcalledRoutes={};
        varmodel=awaitcreateModel({
            Model:KanbanModel,
            data:this.data,
            mockRPC:function(route){
                if(!(routeincalledRoutes)){
                    calledRoutes[route]=1;
                }else{
                    calledRoutes[route]++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        varparams=_.extend(this.params,{
            groupedBy:['product_id'],
            fieldNames:['foo'],
        });

        model.load(params).then(asyncfunction(resultID){
            //variouschecksontheloadresult
            varstate=model.get(resultID);
            assert.ok(_.isEqual(state.groupedBy,['product_id']),'shouldbegroupedby"product_id"');
            assert.strictEqual(state.data.length,2,'shouldhavefound2groups');
            assert.strictEqual(state.count,2,'bothgroupscontainonerecord');
            varxphoneGroup=_.findWhere(state.data,{res_id:37});
            assert.strictEqual(xphoneGroup.model,'partner','groupshouldhavecorrectmodel');
            assert.ok(xphoneGroup,'shouldhaveagroupforres_id37');
            assert.ok(xphoneGroup.isOpen,'"xphone"groupshouldbeopen');
            assert.strictEqual(xphoneGroup.value,'xphone','group37shouldbe"xphone"');
            assert.strictEqual(xphoneGroup.count,1,'"xphone"groupshouldhaveonerecord');
            assert.strictEqual(xphoneGroup.data.length,1,'shouldhavefetchedtherecordsinthegroup');
            assert.ok(_.isEqual(xphoneGroup.domain[0],['product_id','=',37]),
                'domainshouldbecorrect');
            assert.strictEqual(xphoneGroup.limit,40,'limitinagroupshouldbe40');

            //addanewgroup
            awaitmodel.createGroup('xpod',resultID);
            state=model.get(resultID);
            assert.strictEqual(state.data.length,3,'shouldnowhave3groups');
            assert.strictEqual(state.count,2,'therearestill2records');
            varxpodGroup=_.findWhere(state.data,{value:'xpod'});
            assert.strictEqual(xpodGroup.model,'partner','newgroupshouldhavecorrectmodel');
            assert.ok(xpodGroup,'shouldhavean"xpod"group');
            assert.ok(xpodGroup.isOpen,'newgroupshouldbeopen');
            assert.strictEqual(xpodGroup.count,0,'newgroupshouldcontainnorecord');
            assert.ok(_.isEqual(xpodGroup.domain[0],['product_id','=',xpodGroup.res_id]),
                'newgroupshouldhavecorrectdomain');

            //checktherpcsdone
            assert.strictEqual(Object.keys(calledRoutes).length,3,'threedifferentrouteshavebeencalled');
            varnbReadGroups=calledRoutes['/web/dataset/call_kw/partner/web_read_group'];
            varnbSearchRead=calledRoutes['/web/dataset/search_read'];
            varnbNameCreate=calledRoutes['/web/dataset/call_kw/product/name_create'];
            assert.strictEqual(nbReadGroups,1,'shouldhavedone1read_group');
            assert.strictEqual(nbSearchRead,2,'shouldhavedone2search_read');
            assert.strictEqual(nbNameCreate,1,'shouldhavedone1name_create');
            model.destroy();
            done();
        });
    });

    QUnit.test('archive/restoreacolumn',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(4);

        varmodel=awaitcreateModel({
            Model:KanbanModel,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/action_archive'){
                    this.data.partner.records[0].active=false;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        varparams=_.extend(this.params,{
            groupedBy:['product_id'],
            fieldNames:['foo'],
        });

        model.load(params).then(asyncfunction(resultID){
            varstate=model.get(resultID);
            varxphoneGroup=_.findWhere(state.data,{res_id:37});
            varxpadGroup=_.findWhere(state.data,{res_id:41});
            assert.strictEqual(xphoneGroup.count,1,'xphonegrouphasonerecord');
            assert.strictEqual(xpadGroup.count,1,'xpadgrouphasonerecord');

            //archivethecolumn'xphone'
            varrecordIDs=xphoneGroup.data.map(record=>record.res_id);
            awaitmodel.actionArchive(recordIDs,xphoneGroup.id);
            state=model.get(resultID);
            xphoneGroup=_.findWhere(state.data,{res_id:37});
            assert.strictEqual(xphoneGroup.count,0,'xphonegrouphasnorecordanymore');
            xpadGroup=_.findWhere(state.data,{res_id:41});
            assert.strictEqual(xpadGroup.count,1,'xpadgroupstillhasonerecord');
            model.destroy();
            done();
        });
    });

    QUnit.test('kanbanmodeldoesnotallownestedgroups',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(2);

        varmodel=awaitcreateModel({
            Model:KanbanModel,
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.deepEqual(args.kwargs.groupby,['product_id'],
                        "thesecondlevelofgroupByshouldhavebeenremoved");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        varparams=_.extend(this.params,{
            groupedBy:['product_id','qux'],
            fieldNames:['foo'],
        });

        model.load(params).then(function(resultID){
            varstate=model.get(resultID);

            assert.deepEqual(state.groupedBy,['product_id'],
                "thesecondlevelofgroupByshouldhavebeenremoved");

            model.destroy();
            done();
        });
    });

    QUnit.test('resequencecolumnsandrecords',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(8);

        this.data.product.fields.sequence={string:"Sequence",type:"integer"};
        this.data.partner.fields.sequence={string:"Sequence",type:"integer"};
        this.data.partner.records.push({id:3,foo:'aaa',product_id:37});

        varnbReseq=0;
        varmodel=awaitcreateModel({
            Model:KanbanModel,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    nbReseq++;
                    if(nbReseq===1){//resequencingcolumns
                        assert.deepEqual(args.ids,[41,37],
                            "idsshouldbecorrect");
                        assert.strictEqual(args.model,'product',
                            "modelshouldbecorrect");
                    }elseif(nbReseq===2){//resequencingrecords
                        assert.deepEqual(args.ids,[3,1],
                            "idsshouldbecorrect");
                        assert.strictEqual(args.model,'partner',
                            "modelshouldbecorrect");
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });
        varparams=_.extend(this.params,{
            groupedBy:['product_id'],
            fieldNames:['foo'],
        });

        model.load(params)
            .then(function(stateID){
                varstate=model.get(stateID);
                assert.strictEqual(state.data[0].res_id,37,
                    "firstgroupshouldberes_id37");

                //resequencecolumns
                returnmodel.resequence('product',[41,37],stateID);
            })
            .then(function(stateID){
                varstate=model.get(stateID);
                assert.strictEqual(state.data[0].res_id,41,
                    "firstgroupshouldberes_id41afterresequencing");
                assert.strictEqual(state.data[1].data[0].res_id,1,
                    "firstrecordshouldberes_id1");

                //resequencerecords
                returnmodel.resequence('partner',[3,1],state.data[1].id);
            })
            .then(function(groupID){
                vargroup=model.get(groupID);
                assert.strictEqual(group.data[0].res_id,3,
                    "firstrecordshouldberes_id3afterresequencing");

                model.destroy();
                done();
            });
    });

    QUnit.test('addrecordtogroup',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(8);

        varself=this;
        varmodel=awaitcreateModel({
            Model:KanbanModel,
            data:this.data,
        });
        varparams=_.extend(this.params,{
            groupedBy:['product_id'],
            fieldNames:['foo'],
        });

        model.load(params).then(function(stateID){
            self.data.partner.records.push({id:3,foo:'newrecord',product_id:37});

            varstate=model.get(stateID);
            assert.deepEqual(state.res_ids,[1,2],
                "stateshouldhavethecorrectres_ids");
            assert.strictEqual(state.count,2,
                "stateshouldhavethecorrectcount");
            assert.strictEqual(state.data[0].count,1,
                "firstgroupshouldcontainonerecord");

            returnmodel.addRecordToGroup(state.data[0].id,3).then(function(){
                varstate=model.get(stateID);
                assert.deepEqual(state.res_ids,[3,1,2],
                    "stateshouldhavethecorrectres_ids");
                assert.strictEqual(state.count,3,
                    "stateshouldhavethecorrectcount");
                assert.deepEqual(state.data[0].res_ids,[3,1],
                    "newrecord'sidshouldhavebeenaddedtotheres_ids");
                assert.strictEqual(state.data[0].count,2,
                    "firstgroupshouldnowcontaintworecords");
                assert.strictEqual(state.data[0].data[0].data.foo,'newrecord',
                    "newrecordshouldhavebeenfetched");
            });
        }).then(function(){
            model.destroy();
            done();
        })

    });

    QUnit.test('callget(raw:true)beforeloadingx2manydata',asyncfunction(assert){
        //Sometimes,getcanbecalledonadatapointthatiscurrentlybeing
        //reloaded,andthusinapartiallyupdatedstate(e.g.inakanban
        //view,theuserinteractswiththesearchview,andbeforetheviewis
        //fullyreloaded,itclicksonCREATE).Ideally,thisshouldn'thappen,
        //butwiththesyncAPIofget,wecan'tchangethateasily.Soatmost,
        //wecanensurethatitdoesn'tcrash.Moreover,sensitivefunctions
        //requestingthestateformorepreciseinformationthat,e.g.,the
        //count,candothatinthemutextoensurethatthestateisn't
        //currentlybeingreloaded.
        //Inthistest,wehaveagroupedkanbanviewwithaone2many,whose
        //relationaldataisloadedinbatch,onceforallgroups.Wecallget
        //whenthesearch_readforthefirstgrouphasreturned,butnotthe
        //second(andthus,thereadoftheone2manyhasn'tstartedyet).
        //Note:thistestcanberemovedassoonassearch_readsareperformed
        //alongsideread_group.
        vardone=assert.async();
        assert.expect(2);

        this.data.partner.records[1].product_ids=[37,41];
        this.params.fieldsInfo={
            kanban:{
                product_ids:{
                    fieldsInfo:{
                        default:{display_name:{},color:{}},
                    },
                    relatedFields:this.data.product.fields,
                    viewType:'default',
                },
            },
        };
        this.params.viewType='kanban';
        this.params.groupedBy=['foo'];

        varblock;
        vardef=testUtils.makeTestPromise();
        varmodel=awaitcreateModel({
            Model:KanbanModel,
            data:this.data,
            mockRPC:function(route){
                varresult=this._super.apply(this,arguments);
                if(route==='/web/dataset/search_read'&&block){
                    block=false;
                    returnPromise.all([def]).then(_.constant(result));
                }
                returnresult;
            },
        });

        model.load(this.params).then(function(handle){
            block=true;
            model.reload(handle,{});

            varstate=model.get(handle,{raw:true});
            assert.strictEqual(state.count,2);

            def.resolve();

            state=model.get(handle,{raw:true});
            assert.strictEqual(state.count,2);
        }).then(function(){
            model.destroy();
            done();
        });
    });
});

});
