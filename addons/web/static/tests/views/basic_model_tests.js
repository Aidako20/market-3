flectra.define('web.basic_model_tests',function(require){
    "usestrict";

    varBasicModel=require('web.BasicModel');
    varFormView=require('web.FormView');
    vartestUtils=require('web.test_utils');

    varcreateModel=testUtils.createModel;
    varcreateView=testUtils.createView;

    QUnit.module('Views',{
        beforeEach:function(){
            this.data={
                partner:{
                    fields:{
                        display_name:{string:"STRING",type:'char'},
                        //thefollowing2fieldsmustremaininthatordertocheckthat
                        //activehaspriorityoverx_activedespitetheorder
                        x_active:{string:"CustomActive",type:'boolean',default:true},
                        active:{string:"Active",type:'boolean',default:true},
                        total:{string:"Total",type:'integer'},
                        foo:{string:"Foo",type:'char'},
                        bar:{string:"Bar",type:'integer'},
                        qux:{string:"Qux",type:'many2one',relation:'partner'},
                        product_id:{string:"Favoriteproduct",type:'many2one',relation:'product'},
                        product_ids:{string:"Favoriteproducts",type:'one2many',relation:'product'},
                        category:{string:"CategoryM2M",type:'many2many',relation:'partner_type'},
                        date:{string:"DateField",type:'date'},
                        reference:{string:"ReferenceField",type:'reference',selection:[["product","Product"],["partner_type","PartnerType"],["partner","Partner"]]},
                    },
                    records:[
                        {id:1,foo:'blip',bar:1,product_id:37,category:[12],display_name:"firstpartner",date:"2017-01-25"},
                        {id:2,foo:'gnap',bar:2,product_id:41,display_name:"secondpartner"},
                    ],
                    onchanges:{},
                },
                product:{
                    fields:{
                        display_name:{string:"ProductDisplayName",type:"char"},
                        name:{string:"ProductName",type:"char"},
                        category:{string:"CategoryM2M",type:'many2many',relation:'partner_type'},
                        active:{string:"Active",type:'boolean',default:true},
                    },
                    records:[
                        {id:37,display_name:"xphone"},
                        {id:41,display_name:"xpad"}
                    ]
                },
                partner_type:{
                    fields:{
                        display_name:{string:"PartnerType",type:"char"},
                        date:{string:"DateField",type:'date'},
                        x_active:{string:"CustomActive",type:'boolean',default:true},
                    },
                    records:[
                        {id:12,display_name:"gold",date:"2017-01-25"},
                        {id:14,display_name:"silver"},
                        {id:15,display_name:"bronze"}
                    ]
                },
                partner_title:{
                    fields:{
                        display_name:{string:"PartnerTitle",type:'char'},
                    },
                    records:[
                        {id:42,display_name:"Dr."},
                    ]
                }
            };

            //addrelatedfieldstocategory.
            this.data.partner.fields.category.relatedFields=
                $.extend(true,{},this.data.partner_type.fields);
            this.params={
                res_id:2,
                modelName:'partner',
                fields:this.data.partner.fields,
            };
        },
    },function(){
        QUnit.module('BasicModel');

        QUnit.test('contextisgivenwhenusingaresequence',asyncfunction(assert){
            assert.expect(2);
            deletethis.params["res_id"];
            this.data.product.fields.sequence={string:"Sequence",type:"integer"};

            constmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/resequence'){
                        assert.deepEqual(args.context,{active_field:2},
                            "contextshouldbecorrectafteraresequence");
                    }
                    elseif(args.method==="read"){
                        assert.deepEqual(args.kwargs.context,{active_field:2},
                            "contextshouldbecorrectaftera'read'RPC");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            constparams=_.extend(this.params,{
                context:{active_field:2},
                groupedBy:['product_id'],
                fieldNames:['foo'],
            });
    
            model.load(params)
                .then(function(stateID){
                    returnmodel.resequence('product',[41,37],stateID);
                })
                .then(function(){
                    model.destroy();
                });
        });

        QUnit.test('canprocessx2manycommands',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.fields.product_ids.default=[[0,0,{category:[]}]];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="product_ids"/>
                    </form>
                `,
                archs:{
                    'product,false,list':`
                        <tree>
                            <fieldname="display_name"/>
                        </tree>
                    `,
                    'product,false,kanban':`
                        <kanban>
                            <templates><tt-name="kanban-box">
                                <div><fieldname="display_name"/></div>
                            </t></templates>
                        </kanban>
                    `,
                },
                viewOptions:{
                    mode:'edit',
                },
                mockRPC(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.verifySteps([
                'load_views',
                'onchange',
            ]);
            assert.containsOnce(form,'.o_field_x2many_list','shouldhaverenderedax2manylist');
            assert.containsOnce(form,'.o_data_row','shouldhaveadded1recordasdefault');
            assert.containsOnce(form,'.o_field_x2many_list_row_add','shouldhaverenderedax2manyaddrowonlist');
            form.destroy();
        });

        QUnit.test('canprocessx2manycommands(withmultiplefields)',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.product_ids.default=[[0,0,{category:[]}]];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="product_ids"/>
                    </form>
                `,
                archs:{
                    'product,false,list':`
                        <tree>
                            <fieldname="display_name"/>
                            <fieldname="active"/>
                        </tree>
                    `,
                },
                mockRPC(route,args){
                    if(args.method==="create"){
                        constproduct_ids=args.args[0].product_ids;
                        constvalues=product_ids[0][2];
                        assert.strictEqual(values.active,true,"activefieldshouldbeset");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('canloadarecord',asyncfunction(assert){
            assert.expect(7);

            this.params.fieldNames=['foo'];
            this.params.context={active_field:2};

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.deepEqual(args.kwargs.context,{
                        active_field:2,
                        bin_size:true,
                        someKey:'somevalue',
                    },"shouldhavesentthecorrectcontext");
                    returnthis._super.apply(this,arguments);
                },
                session:{
                    user_context:{someKey:'somevalue'},
                }
            });

            assert.strictEqual(model.get(1),null,"shouldreturnnullfornonexistingkey");

            varresultID=awaitmodel.load(this.params);
            //itisastring,becauseitisusedasakeyinanobject
            assert.strictEqual(typeofresultID,'string',"resultshouldbeavalidid");

            varrecord=model.get(resultID);
            assert.strictEqual(record.res_id,2,"res_idreadshouldbethesameasasked");
            assert.strictEqual(record.type,'record',"shouldbeoftype'record'");
            assert.strictEqual(record.data.foo,"gnap","shouldcorrectlyreadvalue");
            assert.strictEqual(record.data.bar,undefined,"shouldnotfetchthefield'bar'");
            model.destroy();
        });

        QUnit.test('rejectsloadingarecordwithinvalidid',asyncfunction(assert){
            assert.expect(1);

            this.params.res_id=99;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });
            try{
                awaitmodel.load(this.params);
            }
            catch(e){
                assert.ok("loadshouldreturnarejecteddeferredforaninvalidid");
            }

            model.destroy();
        });

        QUnit.test('notifychangewithmany2one',asyncfunction(assert){
            assert.expect(2);

            this.params.fieldNames=['foo','qux'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.qux,false,"quxfieldshouldbefalse");
            awaitmodel.notifyChanges(resultID,{qux:{id:1,display_name:"hello"}});

            record=model.get(resultID);
            assert.strictEqual(record.data.qux.data.id,1,"quxfieldshouldbe1");
            model.destroy();
        });

        QUnit.test('notifychangeonmany2one:unsetandresetsamevalue',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[1].qux=1;

            this.params.fieldNames=['qux'];
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.qux.data.id,1,"quxvalueshouldbe1");

            awaitmodel.notifyChanges(resultID,{qux:false});
            record=model.get(resultID);
            assert.strictEqual(record.data.qux,false,"quxshouldbeunset");

            awaitmodel.notifyChanges(resultID,{qux:{id:1,display_name:'second_partner'}});
            record=model.get(resultID);
            assert.strictEqual(record.data.qux.data.id,1,"quxvalueshouldbe1again");
            model.destroy();
        });

        QUnit.test('writeonamany2one',asyncfunction(assert){
            assert.expect(4);
            varself=this;

            this.params.fieldNames=['product_id'];

            varrpcCount=0;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id.data.display_name,'xpad',
                "shouldbeinitializedwithcorrectvalue");

            awaitmodel.notifyChanges(resultID,{product_id:{id:37,display_name:'xphone'}});

            record=model.get(resultID);
            assert.strictEqual(record.data.product_id.data.display_name,'xphone',
                "shouldbechangedwithcorrectvalue");

            awaitmodel.save(resultID);

            assert.strictEqual(self.data.partner.records[1].product_id,37,
                "shouldhavereallysavedthedata");
            assert.strictEqual(rpcCount,3,"shouldhavedone3rpc:1read,1write,1read");
            model.destroy();
        });

        QUnit.test('basiconchange',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.fields.foo.onChange=true;
            this.data.partner.onchanges.foo=function(obj){
                obj.bar=obj.foo.length;
            };

            this.params.fieldNames=['foo','bar'];
            this.params.context={hello:'world'};

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        varcontext=args.kwargs.context;
                        assert.deepEqual(context,{hello:'world'},
                            "contextshouldbesentbytheonchange");
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.foo,'gnap',"foofieldisproperlyinitialized");
            assert.strictEqual(record.data.bar,2,"barfieldisproperlyinitialized");

            awaitmodel.notifyChanges(resultID,{foo:'marypoppins'});

            record=model.get(resultID);
            assert.strictEqual(record.data.foo,'marypoppins',"onchangehasbeenapplied");
            assert.strictEqual(record.data.bar,12,"onchangehasbeenapplied");
            model.destroy();
        });

        QUnit.test('onchangewithamany2one',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.fields.product_id.onChange=true;
            this.data.partner.onchanges.product_id=function(obj){
                if(obj.product_id===37){
                    obj.foo="spacelollipop";
                }
            };

            this.params.fieldNames=['foo','product_id'];

            varrpcCount=0;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        assert.strictEqual(args.args[2],"product_id",
                            "shouldsendtheonlychangedfieldasastring,notalist");
                    }
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.foo,'gnap',"foofieldisproperlyinitialized");
            assert.strictEqual(record.data.product_id.data.id,41,"product_idfieldisproperlyinitialized");

            awaitmodel.notifyChanges(resultID,{product_id:{id:37,display_name:'xphone'}});

            record=model.get(resultID);
            assert.strictEqual(record.data.foo,'spacelollipop',"onchangehasbeenapplied");
            assert.strictEqual(rpcCount,2,"shouldhavedone2rpc:1readand1onchange");
            model.destroy();
        });

        QUnit.test('onchangeonaone2manynotinview(fieldNames)',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.fields.foo.onChange=true;
            this.data.partner.onchanges.foo=function(obj){
                obj.bar=obj.foo.length;
                obj.product_ids=[];
            };

            this.params.fieldNames=['foo'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.foo,'gnap',"foofieldisproperlyinitialized");
            assert.strictEqual(record.data.bar,undefined,"barfieldisnotloaded");
            assert.strictEqual(record.data.product_ids,undefined,"product_idsfieldisnotloaded");

            awaitmodel.notifyChanges(resultID,{foo:'marypoppins'});

            record=model.get(resultID);
            assert.strictEqual(record.data.foo,'marypoppins',"onchangehasbeenapplied");
            assert.strictEqual(record.data.bar,12,"onchangehasbeenapplied");
            assert.strictEqual(record.data.product_ids,undefined,
                "onchangeonproduct_ids(one2many)hasnotbeenapplied");
            model.destroy();
        });

        QUnit.test('notifyChangeonaone2many',asyncfunction(assert){
            assert.expect(9);

            this.data.partner.records[1].product_ids=[37];
            this.params.fieldNames=['product_ids'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        assert.strictEqual(args.model,'product');
                    }
                    returnthis._super(route,args);
                },
            });

            varo2mParams={
                modelName:'product',
                fields:this.data.product.fields,
                fieldNames:['display_name'],
            };
            varresultID=awaitmodel.load(this.params);
            varnewRecordID=awaitmodel.load(o2mParams);
            varrecord=model.get(resultID);
            varx2mListID=record.data.product_ids.id;

            assert.strictEqual(record.data.product_ids.count,1,
                "thereshouldbeonerecordintherelation");

            //triggera'ADD'command
            awaitmodel.notifyChanges(resultID,{product_ids:{operation:'ADD',id:newRecordID}});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                operation:'ADD',id:newRecordID,
            }],"_changesshouldbecorrect");
            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,2,
                "thereshouldbetworecordsintherelation");

            //triggera'UPDATE'command
            awaitmodel.notifyChanges(resultID,{product_ids:{operation:'UPDATE',id:newRecordID}});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                operation:'ADD',id:newRecordID,
            },{
                operation:'UPDATE',id:newRecordID,
            }],"_changesshouldbecorrect");
            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,2,
                "thereshouldbetworecordsintherelation");

            //triggera'DELETE'commandontheexistingrecord
            varexistingRecordID=record.data.product_ids.data[0].id;
            awaitmodel.notifyChanges(resultID,{product_ids:{operation:'DELETE',ids:[existingRecordID]}});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                operation:'ADD',id:newRecordID,
            },{
                operation:'UPDATE',id:newRecordID,
            },{
                operation:'DELETE',id:existingRecordID,
            }],
                "_changesshouldbecorrect");
            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,1,
                "thereshouldbeonerecordintherelation");

            //triggera'DELETE'commandonthenewrecord
            awaitmodel.notifyChanges(resultID,{product_ids:{operation:'DELETE',ids:[newRecordID]}});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                operation:'DELETE',id:existingRecordID,
            }],"_changesshouldbecorrect");
            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,0,
                "thereshouldbenorecordintherelation");

            model.destroy();
        });

        QUnit.test('notifyChangeonamany2one,withoutdisplay_name',asyncfunction(assert){
            assert.expect(3);

            this.params.fieldNames=['product_id'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        assert.strictEqual(args.model,'product');
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id.data.display_name,'xpad',
                "product_idfieldissettoxpad");

            awaitmodel.notifyChanges(resultID,{product_id:{id:37}});

            record=model.get(resultID);
            assert.strictEqual(record.data.product_id.data.display_name,'xphone',
                "display_nameshouldhavebeenfetched");
            model.destroy();
        });

        QUnit.test('onchangeonacharwithanunchangedmany2one',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.fields.foo.onChange=true;
            this.data.partner.onchanges.foo=function(obj){
                obj.foo=obj.foo+"alligator";
            };

            this.params.fieldNames=['foo','product_id'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        assert.strictEqual(args.args[1].product_id,41,"shouldsendcorrectvalue");
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            awaitmodel.notifyChanges(resultID,{foo:'cookie'});
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.foo,'cookiealligator',"onchangehasbeenapplied");
            model.destroy();
        });

        QUnit.test('onchangeonacharwithanothermany2onenotsettoavalue',asyncfunction(assert){
            assert.expect(2);
            this.data.partner.records[0].product_id=false;
            this.data.partner.fields.foo.onChange=true;
            this.data.partner.onchanges.foo=function(obj){
                obj.foo=obj.foo+"alligator";
            };

            this.params.fieldNames=['foo','product_id'];
            this.params.res_id=1;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id,false,"product_idisnotset");

            awaitmodel.notifyChanges(resultID,{foo:'cookie'});
            record=model.get(resultID);
            assert.strictEqual(record.data.foo,'cookiealligator',"onchangehasbeenapplied");
            model.destroy();
        });

        QUnit.test('cangetamany2many',asyncfunction(assert){
            assert.expect(3);

            this.params.res_id=1;
            this.params.fieldsInfo={
                default:{
                    category:{
                        fieldsInfo:{default:{display_name:{}}},
                        relatedFields:{display_name:{type:"char"}},
                        viewType:'default',
                    },
                },
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.category.data[0].res_id,12,
                "shouldhaveloadedmany2manyres_ids");
            assert.strictEqual(record.data.category.data[0].data.display_name,"gold",
                "shouldhaveloadedmany2manydisplay_name");
            record=model.get(resultID,{raw:true});
            assert.deepEqual(record.data.category,[12],
                "withoptionraw,categoryshouldonlyreturnids");
            model.destroy();
        });

        QUnit.test('canusecommandaddandgetmany2manyvaluewithdatefield',asyncfunction(assert){
            assert.expect(2);

            this.params.fieldsInfo={
                default:{
                    category:{
                        fieldsInfo:{default:{date:{}}},
                        relatedFields:{date:{type:"date"}},
                        viewType:'default',
                    },
                },
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varchanges={
                category:{operation:'ADD_M2M',ids:[{id:12}]}
            };
            awaitmodel.notifyChanges(resultID,changes);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.category.data.length,1,"shouldhaveaddedonecategory");
            assert.strictEqual(record.data.category.data[0].data.dateinstanceofmoment,
                true,"shouldhaveadateparsedinamomentobject");
            model.destroy();
        });

        QUnit.test('many2manywithADD_M2Mcommandandcontextwithparentkey',asyncfunction(assert){
            assert.expect(1);

            this.data.partner_type.fields.some_char={type:"char"};
            this.params.fieldsInfo={
                default:{
                    category:{
                        fieldsInfo:{default:{some_char:{context:"{'a':parent.foo}"}}},
                        relatedFields:{some_char:{type:"char"}},
                        viewType:'default',
                    },
                    foo:{},
                },
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varchanges={
                category:{operation:'ADD_M2M',ids:[{id:12}]}
            };
            awaitmodel.notifyChanges(resultID,changes);
            varrecord=model.get(resultID);
            varcategoryRecord=record.data.category.data[0];
            assert.deepEqual(categoryRecord.getContext({fieldName:'some_char'}),{a:'gnap'},
                "shouldproperlyevaluatecontext");
            model.destroy();
        });

        QUnit.test('canfetchalist',asyncfunction(assert){
            assert.expect(4);

            this.params.fieldNames=['foo'];
            this.params.domain=[];
            this.params.groupedBy=[];
            this.params.res_id=undefined;
            this.params.context={active_field:2};

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.strictEqual(args.context.active_field,2,
                        "shouldhavesentthecorrectcontext");
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);

            assert.strictEqual(record.type,'list',"recordfetchedshouldbealist");
            assert.strictEqual(record.data.length,2,"shouldhavefetched2records");
            assert.strictEqual(record.data[0].data.foo,'blip',"firstrecordshouldhave'blip'infoofield");
            model.destroy();
        });

        QUnit.test('fetchx2manysinlist,withnottoomanyrpcs',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].category=[12,15];
            this.data.partner.records[1].category=[12,14];

            this.params.fieldNames=['category'];
            this.params.domain=[];
            this.params.groupedBy=[];
            this.params.res_id=undefined;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.step(route);
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);

            assert.strictEqual(record.data[0].data.category.data.length,2,
                "firstrecordshouldhave2categoriesloaded");
            assert.verifySteps(["/web/dataset/search_read"],
                "shouldhavedone2rpc(searchreadandreadcategory)");
            model.destroy();
        });

        QUnit.test('canmakeadefault_recordwiththehelpofonchange',asyncfunction(assert){
            assert.expect(5);

            this.params.context={};
            this.params.fieldNames=['product_id','category','product_ids'];
            this.params.res_id=undefined;
            this.params.type='record';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id,false,"m2odefaultvalueshouldbefalse");
            assert.deepEqual(record.data.product_ids.data,[],"o2mdefaultshouldbe[]");
            assert.deepEqual(record.data.category.data,[],"m2mdefaultshouldbe[]");

            assert.verifySteps(['onchange']);

            model.destroy();
        });

        QUnit.test('default_getreturninganonrequestedfield',asyncfunction(assert){
            //'default_get'returnsadefaultvalueforthefieldsgivenin
            //arguments.Itshouldnotreturnavalueforfieldsthathavenotbe
            //requested.However,ithappens(e.g.res.users),andthewebclient
            //shouldnotcrashwhenthissituationoccurs(thefieldshouldsimply
            //beignored).
            assert.expect(2);

            this.params.context={};
            this.params.fieldNames=['category'];
            this.params.res_id=undefined;
            this.params.type='record';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    varresult=this._super(route,args);
                    if(args.method==='default_get'){
                        result.product_ids=[[6,0,[37,41]]];
                    }
                    returnresult;
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.ok('category'inrecord.data,
                "shouldhaveprocessed'category'");
            assert.notOk('product_ids'inrecord.data,
                "shouldhaveignored'product_ids'");

            model.destroy();
        });

        QUnit.test('canmakeadefault_recordwithdefaultrelationalvalues',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.fields.product_id.default=37;
            this.data.partner.fields.product_ids.default=[
                [0,false,{name:'xmac'}],
                [0,false,{name:'xcloud'}]
            ];
            this.data.partner.fields.category.default=[
                [6,false,[12,14]]
            ];

            this.params.fieldNames=['product_id','category','product_ids'];
            this.params.res_id=undefined;
            this.params.type='record';
            this.params.fieldsInfo={
                form:{
                    category:{},
                    product_id:{},
                    product_ids:{
                        fieldsInfo:{
                            default:{name:{}},
                        },
                        relatedFields:this.data.product.fields,
                        viewType:'default',
                    },
                },
            };
            this.params.viewType='form';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.deepEqual(record.data.product_id.data.display_name,'xphone',
                "m2odefaultshouldbexphone");
            assert.deepEqual(record.data.product_ids.data.length,
                2,"o2mdefaultshouldhavetworecords");
            assert.deepEqual(record.data.product_ids.data[0].data.name,
                'xmac',"firsto2mdefaultvalueshouldbexmac");
            assert.deepEqual(record.data.category.res_ids,[12,14],
                "m2mdefaultshouldbe[12,14]");

            assert.verifySteps(['onchange']);

            model.destroy();
        });

        QUnit.test('default_record,withonchangeonmany2one',asyncfunction(assert){
            assert.expect(1);

            //theonchangeisdonebythemockRPCbecausewewanttoreturnavalue
            //of'false',whichdoesnotworkwiththemockservermockOnChangemethod.
            this.data.partner.onchanges.product_id=true;

            this.params.context={};
            this.params.fieldNames=['product_id'];
            this.params.res_id=undefined;
            this.params.type='record';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({value:{product_id:false}});
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id,false,"m2odefaultvalueshouldbefalse");
            model.destroy();
        });

        QUnit.test('defaultrecord:batchnamegetsonsamemodelandres_id',asyncfunction(assert){
            assert.expect(3);

            varrpcCount=0;
            varfields=this.data.partner.fields;
            fields.other_product_id=_.extend({},fields.product_id);
            fields.product_id.default=37;
            fields.other_product_id.default=41;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            varparams={
                context:{},
                fieldNames:['other_product_id','product_id'],
                fields:fields,
                modelName:'partner',
                type:'record',
            };

            varresultID=awaitmodel.load(params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id.data.display_name,"xphone",
                "shouldhavefetchedcorrectname");
            assert.strictEqual(record.data.other_product_id.data.display_name,"xpad",
                "shouldhavefetchedcorrectname");
            assert.strictEqual(rpcCount,1,"shouldhavedone1rpc:onchange");
            model.destroy();
        });

        QUnit.test('undoingachangekeepstherecorddirty',asyncfunction(assert){
            assert.expect(4);

            this.params.fieldNames=['foo'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.foo,"gnap","foofieldshouldproperlybeset");
            assert.ok(!model.isDirty(resultID),"recordshouldnotbedirty");
            awaitmodel.notifyChanges(resultID,{foo:"hello"});
            assert.ok(model.isDirty(resultID),"recordshouldbedirty");
            awaitmodel.notifyChanges(resultID,{foo:"gnap"});
            assert.ok(model.isDirty(resultID),"recordshouldbedirty");
            model.destroy();
        });

        QUnit.test('isDirtyworkscorrectlyonlistmadeempty',asyncfunction(assert){
            assert.expect(3);

            this.params.fieldNames=['category'];
            this.params.res_id=1;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            varcategory_value=record.data.category;
            assert.ok(_.isObject(category_value),"categoryfieldshouldhavebeenfetched");
            assert.strictEqual(category_value.data.length,1,"categoryfieldshouldcontainonerecord");
            awaitmodel.notifyChanges(resultID,{
                category:{
                    operation:'DELETE',
                    ids:[category_value.data[0].id],
                }
            });
            assert.ok(model.isDirty(resultID),"recordshouldbeconsidereddirty");
            model.destroy();
        });

        QUnit.test('canduplicatearecord',asyncfunction(assert){
            assert.expect(4);

            this.params.fieldNames=['foo'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.display_name,"secondpartner",
                "recordshouldhavecorrectdisplayname");
            assert.strictEqual(record.data.foo,"gnap","fooshouldbesettocorrectvalue");
            varduplicateID=awaitmodel.duplicateRecord(resultID);
            varduplicate=model.get(duplicateID);
            assert.strictEqual(duplicate.data.display_name,"secondpartner(copy)",
                "recordshouldhavebeenduplicated");
            assert.strictEqual(duplicate.data.foo,"gnap","fooshouldbesettocorrectvalue");
            model.destroy();
        });

        QUnit.test('recordwithmany2onesettosomevalue,thensetittonone',asyncfunction(assert){
            assert.expect(3);

            this.params.fieldNames=['product_id'];

            varself=this;
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_id.data.display_name,'xpad',"product_idshouldbeset");
            awaitmodel.notifyChanges(resultID,{product_id:false});

            record=model.get(resultID);
            assert.strictEqual(record.data.product_id,false,"product_idshouldnotbeset");

            awaitmodel.save(resultID);

            assert.strictEqual(self.data.partner.records[1].product_id,false,
                "shouldhavesavedthenewproduct_idvalue");
            model.destroy();
        });

        QUnit.test('internalstateofgroupsremainswhenreloading',asyncfunction(assert){
            assert.expect(10);

            this.params.fieldNames=['foo'];
            this.params.domain=[];
            this.params.limit=80;
            this.params.groupedBy=['product_id'];
            this.params.res_id=undefined;

            varfilterEnabled=false;
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='web_read_group'&&filterEnabled){
                        //asthisisnotyetsupportedbytheMockServer,simulates
                        //aread_groupthatreturnsemptygroups
                        //thisisthecaseforseveralmodels(e.g.project.task
                        //groupedbystage_id)
                        returnthis._super.apply(this,arguments).then(function(result){
                            //artificiallyfilteroutrecordsoffirstgroup
                            result.groups[0].product_id_count=0;
                            returnresult;
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.length,2,"shouldhave2groups");
            vargroupID=record.data[0].id;
            assert.strictEqual(model.localData[groupID].parentID,resultID,
                "parentIDshouldbecorrectlysetongroups");

            awaitmodel.toggleGroup(groupID);

            record=model.get(resultID);
            assert.ok(record.data[0].isOpen,"firstgroupshouldbeopen");
            assert.strictEqual(record.data[0].data.length,1,
                "firstgroupshouldhaveonerecord");
            assert.strictEqual(record.data[0].limit,80,
                "limitshouldbe80bydefault");

            //changethelimitandoffsetofthefirstgroup
            model.localData[record.data[0].id].limit=10;

            awaitmodel.reload(resultID);
            record=model.get(resultID);
            assert.ok(record.data[0].isOpen,"firstgroupshouldstillbeopen");
            assert.strictEqual(record.data[0].data.length,1,
                "firstgroupshouldstillhaveonerecord");
            assert.strictEqual(record.data[0].limit,10,
                "newlimitshouldhavebeenkept");

            //filtersomerecordsout:theopengroupshouldstayopenbutnow
            //beempty
            filterEnabled=true;
            awaitmodel.reload(resultID);
            record=model.get(resultID);
            assert.strictEqual(record.data[0].count,0,
                "firstgroup'scountshouldbe0");
            assert.strictEqual(record.data[0].data.length,0,
                "firstgroup'sdatashouldbeempty'");
            model.destroy();
        });

        QUnit.test('groupondatefieldwithmagicgroupingmethod',asyncfunction(assert){
            assert.expect(1);

            this.params.fieldNames=['foo'];
            this.params.groupedBy=['date:month'];
            this.params.res_id=undefined;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='web_read_group'){
                        assert.deepEqual(args.kwargs.fields,['foo','date'],
                            "shouldhavecorrectlytrimmedthemagicgroupinginfofromthefieldname");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaitmodel.load(this.params);
            model.destroy();
        });


        QUnit.test('readgroupwhengroupedbyaselectionfield',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.fields.selection={
                type:'selection',
                selection:[['a','A'],['b','B']],
            };
            this.data.partner.records[0].selection='a';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });
            varparams={
                modelName:'partner',
                fields:this.data.partner.fields,
                fieldNames:['foo'],
                groupedBy:['selection'],
            };

            varresultID=awaitmodel.load(params);
            vardataPoint=model.get(resultID);
            assert.strictEqual(dataPoint.data.length,2,"shouldhavetwogroups");

            vargroupFalse=_.findWhere(dataPoint.data,{value:false});
            assert.ok(groupFalse,"shouldhaveagroupforvaluefalse");
            assert.deepEqual(groupFalse.domain,[['selection','=',false]],
                "group'sdomainshouldbecorrect");

            vargroupA=_.findWhere(dataPoint.data,{value:'A'});
            assert.ok(groupA,"shouldhaveagroupforvalue'a'");
            assert.deepEqual(groupA.domain,[['selection','=','a']],
                "group'sdomainshouldbecorrect");
            model.destroy();
        });

        QUnit.test('createrecord,thensave',asyncfunction(assert){
            assert.expect(5);

            this.params.fieldNames=['product_ids'];
            this.params.res_id=undefined;
            this.params.type='record';
            this.params.context={active_field:2};

            varid;
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        //hastobedonebeforethecallto_super
                        assert.deepEqual(args.args[0].product_ids,[],"shouldnothaveanycommand");
                        assert.notOk('category'inargs.args[0],"shouldnothaveotherfields");

                        assert.strictEqual(args.kwargs.context.active_field,2,
                            "record'scontextshouldbecorrectlypassed");
                    }
                    varresult=this._super(route,args);
                    if(args.method==='create'){
                        result.then(function(res){
                            id=res;
                        });
                    }
                    returnresult;
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            awaitmodel.save(record.id,{reload:false});
            record=model.get(resultID);
            assert.strictEqual(record.res_id,id,"shouldhavecorrectidfromserver");
            assert.strictEqual(record.data.id,id,"shouldhavecorrectidfromserver");
            model.destroy();
        });

        QUnit.test('writecommandsonaone2many',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[1].product_ids=[37];

            this.params.fieldNames=['product_ids'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[0],[2],"shouldwriteonres_id=2");
                        varcommands=args.args[1].product_ids;
                        assert.deepEqual(commands[0],[4,37,false],"firstcommandshouldbea4");
                        //TODO:uncommentnextline
                        //assert.strictEqual(commands[1],[0,false,{name:"toy"}],"secondcommandshouldbea0");
                        assert.strictEqual(commands[1][0],0,"secondcommandshouldbea0");
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID,{raw:true});
            assert.deepEqual(record.data.product_ids,[37],"shouldhavecorrectinitialvalue");

            varrelatedRecordID=awaitmodel.makeRecord('product',[{
                name:'name',
                string:"ProductName",
                type:"char",
                value:"xpod"
            }
            ]);
            awaitmodel.notifyChanges(record.id,{
                product_ids:{operation:"ADD",id:relatedRecordID}
            });
            awaitmodel.save(record.id);
            model.destroy();
        });

        QUnit.test('createcommandsonaone2many',asyncfunction(assert){
            assert.expect(3);

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    returnthis._super(route,args);
                },
            });

            this.params.fieldsInfo={
                default:{
                    product_ids:{
                        fieldsInfo:{
                            default:{
                                display_name:{type:'string'},
                            }
                        },
                        viewType:'default',
                    }
                }
            };
            this.params.res_id=undefined;
            this.params.type='record';

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_ids.data.length,0,
                "one2manyshouldstartwithalistoflength0");

            awaitmodel.notifyChanges(record.id,{
                product_ids:{
                    operation:"CREATE",
                    data:{
                        display_name:'coucou',
                    },
                },
            });
            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.data.length,1,
                "one2manyshouldbealistoflength1");
            assert.strictEqual(record.data.product_ids.data[0].data.display_name,"coucou",
                "one2manyshouldhavecorrectdata");
            model.destroy();
        });

        QUnit.test('onchangewithaone2manyonanewrecord',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.fields.total.default=50;
            this.data.partner.fields.product_ids.onChange=true;
            this.data.partner.onchanges.product_ids=function(obj){
                obj.total+=100;
            };

            this.params.fieldNames=['total','product_ids'];
            this.params.res_id=undefined;
            this.params.type='record';
            this.params.fieldsInfo={
                form:{
                    product_ids:{
                        fieldsInfo:{
                            default:{name:{}},
                        },
                        relatedFields:this.data.product.fields,
                        viewType:'default',
                    },
                    total:{},
                },
            };
            this.params.viewType='form';

            varo2mRecordParams={
                fields:this.data.product.fields,
                fieldNames:['name'],
                modelName:'product',
                type:'record',
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='onchange'&&args.args[1].total===150){
                        assert.deepEqual(args.args[1].product_ids,[[0,args.args[1].product_ids[0][1],{name:"xpod"}]],
                            "Shouldhavesentthecreatecommandintheonchange");
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.product_ids.data.length,0,
                "one2manyshouldstartwithalistoflength0");

            //makeadefaultrecordfortherelatedmodel
            varrelatedRecordID=awaitmodel.load(o2mRecordParams);
            //updatethesubrecord
            awaitmodel.notifyChanges(relatedRecordID,{name:'xpod'});
            //addthesubrecordtotheo2mofthemainrecord
            awaitmodel.notifyChanges(resultID,{
                product_ids:{operation:"ADD",id:relatedRecordID}
            });

            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.data.length,1,
                "one2manyshouldbealistoflength1");
            assert.strictEqual(record.data.product_ids.data[0].data.name,"xpod",
                "one2manyshouldhavecorrectdata");
            model.destroy();
        });

        QUnit.test('datesareproperlyloadedandparsed(record)',asyncfunction(assert){
            assert.expect(2);

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varparams={
                fieldNames:['date'],
                fields:this.data.partner.fields,
                modelName:'partner',
                res_id:1,
            };

            awaitmodel.load(params).then(function(resultID){
                varrecord=model.get(resultID);
                assert.ok(record.data.dateinstanceofmoment,
                    "fetcheddatefieldshouldhavebeenformatted");
            });

            params.res_id=2;

            awaitmodel.load(params).then(function(resultID){
                varrecord=model.get(resultID);
                assert.strictEqual(record.data.date,false,
                    "unsetdatefieldshouldbefalse");
            });
            model.destroy();
        });

        QUnit.test('datesareproperlyloadedandparsed(list)',asyncfunction(assert){
            assert.expect(2);

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varparams={
                fieldNames:['date'],
                fields:this.data.partner.fields,
                modelName:'partner',
                type:'list',
            };

            awaitmodel.load(params).then(function(resultID){
                varrecord=model.get(resultID);
                varfirstRecord=record.data[0];
                varsecondRecord=record.data[1];
                assert.ok(firstRecord.data.dateinstanceofmoment,
                    "fetcheddatefieldshouldhavebeenformatted");
                assert.strictEqual(secondRecord.data.date,false,
                    "ifdateisnotset,itshouldbefalse");
            });
            model.destroy();
        });

        QUnit.test('datesareproperlyloadedandparsed(default_get)',asyncfunction(assert){
            assert.expect(1);

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varparams={
                fieldNames:['date'],
                fields:this.data.partner.fields,
                modelName:'partner',
                type:'record',
            };

            awaitmodel.load(params).then(function(resultID){
                varrecord=model.get(resultID);
                assert.strictEqual(record.data.date,false,"datedefaultvalueshouldbefalse");
            });
            model.destroy();
        });

        QUnit.test('default_getonx2manymayreturnalistofids',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.category.default=[12,14];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varparams={
                fieldNames:['category'],
                fields:this.data.partner.fields,
                modelName:'partner',
                type:'record',
            };

            awaitmodel.load(params).then(function(resultID){
                varrecord=model.get(resultID);
                assert.ok(_.isEqual(record.data.category.res_ids,[12,14]),
                    "categoryfieldshouldhavecorrectdefaultvalue");
            });

            model.destroy();
        });

        QUnit.test('default_get:fetchmany2onewithdefault(empty&not)insidex2manys',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.fields.category_m2o={
                type:'many2one',
                relation:'partner_type',
            };
            this.data.partner.fields.o2m={
                string:"O2M",type:'one2many',relation:'partner',default:[
                    [6,0,[]],
                    [0,0,{category_m2o:false,o2m:[]}],
                    [0,0,{category_m2o:12,o2m:[]}],
                ],
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varparams={
                fieldNames:['o2m'],
                fields:this.data.partner.fields,
                fieldsInfo:{
                    form:{
                        o2m:{
                            relatedFields:this.data.partner.fields,
                            fieldsInfo:{
                                list:{
                                    category_m2o:{
                                        relatedFields:{display_name:{}},
                                    },
                                },
                            },
                            viewType:'list',
                        },
                    },
                },
                modelName:'partner',
                type:'record',
                viewType:'form',
            };

            varresultID=awaitmodel.load(params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.o2m.count,2,"o2mfieldshouldcontain2records");
            assert.strictEqual(record.data.o2m.data[0].data.category_m2o,false,
                "firstcategoryfieldshouldbeempty");
            assert.strictEqual(record.data.o2m.data[1].data.category_m2o.data.display_name,"gold",
                "secondcategoryfieldshouldhavebeencorrectlyfetched");

            model.destroy();
        });

        QUnit.test('default_get:fetchx2manysinsidex2manys',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.fields.o2m={
                string:"O2M",type:'one2many',relation:'partner',default:[[6,0,[1]]],
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varparams={
                fieldNames:['o2m'],
                fields:this.data.partner.fields,
                fieldsInfo:{
                    form:{
                        o2m:{
                            relatedFields:this.data.partner.fields,
                            fieldsInfo:{
                                list:{
                                    category:{
                                        relatedFields:{display_name:{}},
                                    },
                                },
                            },
                            viewType:'list',
                        },
                    },
                },
                modelName:'partner',
                type:'record',
                viewType:'form',
            };

            varresultID=awaitmodel.load(params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.o2m.count,1,"o2mfieldshouldcontain1record");
            varcategoryList=record.data.o2m.data[0].data.category;
            assert.strictEqual(categoryList.count,1,
                "categoryfieldshouldcontain1record");
            assert.strictEqual(categoryList.data[0].data.display_name,
                'gold',"categoryrecordsshouldhavebeenfetched");

            model.destroy();
        });

        QUnit.test('contextsanddomainscanbeproperlyfetched',asyncfunction(assert){
            assert.expect(8);

            this.data.partner.fields.product_id.context="{'hello':'world','test':foo}";
            this.data.partner.fields.product_id.domain="[['hello','like','world'],['test','like',foo]]";

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            this.params.fieldNames=['product_id','foo'];

            varresultID=awaitmodel.load(this.params);
            varrecordPartner=model.get(resultID);
            assert.strictEqual(typeofrecordPartner.getContext,"function",
                "partnerrecordshouldhaveagetContextfunction");
            assert.strictEqual(typeofrecordPartner.getDomain,"function",
                "partnerrecordshouldhaveagetDomainfunction");
            assert.deepEqual(recordPartner.getContext(),{},
                "askingforacontextwithoutafieldnameshouldfetchthesession/user/viewcontext");
            assert.deepEqual(recordPartner.getDomain(),[],
                "askingforadomainwithoutafieldnameshouldfetchthesession/user/viewdomain");
            assert.deepEqual(
                recordPartner.getContext({fieldName:"product_id"}),
                {hello:"world",test:"gnap"},
                "askingforacontextwithafieldnameshouldfetchthefieldcontext(evaluated)");
            assert.deepEqual(
                recordPartner.getDomain({fieldName:"product_id"}),
                [["hello","like","world"],["test","like","gnap"]],
                "askingforadomainwithafieldnameshouldfetchthefielddomain(evaluated)");
            model.destroy();

            //Tryagainwithxmloverrideoffielddomainandcontext
            model=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            this.params.fieldsInfo={
                default:{
                    foo:{},
                    product_id:{
                        context:"{'hello2':'world','test2':foo}",
                        domain:"[['hello2','like','world'],['test2','like',foo]]",
                    },
                }
            };

            resultID=awaitmodel.load(this.params);
            recordPartner=model.get(resultID);
            assert.deepEqual(
                recordPartner.getContext({fieldName:"product_id"}),
                {hello2:"world",test2:"gnap"},
                "fieldcontextshouldhavebeenoverriddenbyxmlattribute");
            assert.deepEqual(
                recordPartner.getDomain({fieldName:"product_id"}),
                [["hello2","like","world"],["test2","like","gnap"]],
                "fielddomainshouldhavebeenoverriddenbyxmlattribute");
            model.destroy();
        });

        QUnit.test('dontwriteonreadonlyfields(writeandcreate)',asyncfunction(assert){
            assert.expect(6);

            this.params.fieldNames=['foo','bar'];
            this.data.partner.fields.foo.onChange=true;
            this.data.partner.onchanges.foo=function(obj){
                obj.bar=obj.foo.length;
            };
            this.params.fieldsInfo={
                default:{
                    foo:{},
                    bar:{
                        modifiers:{
                            readonly:true,
                        },
                    },
                }
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1],{foo:"verylongstring"},
                            "shouldonlysavefoofield");
                    }
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0],{foo:"anotherverylongstring"},
                            "shouldonlysavefoofield");
                    }
                    returnthis._super(route,args);
                },
            });
            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.bar,2,
                "shouldbeinitializedwithcorrectvalue");

            awaitmodel.notifyChanges(resultID,{foo:"verylongstring"});

            record=model.get(resultID);
            assert.strictEqual(record.data.bar,14,
                "shouldbechangedwithcorrectvalue");

            awaitmodel.save(resultID);

            //startagain,butwithanewrecord
            deletethis.params.res_id;
            resultID=awaitmodel.load(this.params);
            record=model.get(resultID);
            assert.strictEqual(record.data.bar,0,
                "shouldbeinitializedwithcorrectvalue(0asinteger)");

            awaitmodel.notifyChanges(resultID,{foo:"anotherverylongstring"});

            record=model.get(resultID);
            assert.strictEqual(record.data.bar,21,
                "shouldbechangedwithcorrectvalue");

            awaitmodel.save(resultID);
            model.destroy();
        });

        QUnit.test('dontwriteonreadonlyfieldsunlesssaveattributeisset',asyncfunction(assert){
            assert.expect(6);

            this.params.fieldNames=['foo','bar'];
            this.data.partner.fields.foo.onChange=true;
            this.data.partner.onchanges.foo=function(obj){
                obj.bar=obj.foo.length;
            };
            this.params.fieldsInfo={
                default:{
                    foo:{},
                    bar:{
                        modifiers:{
                            readonly:true,
                        },
                        force_save:true,
                    },
                }
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1],{bar:14,foo:"verylongstring"},
                            "shouldonlysavefoofield");
                    }
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0],{bar:21,foo:"anotherverylongstring"},
                            "shouldonlysavefoofield");
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.bar,2,
                "shouldbeinitializedwithcorrectvalue");

            awaitmodel.notifyChanges(resultID,{foo:"verylongstring"});

            record=model.get(resultID);
            assert.strictEqual(record.data.bar,14,
                "shouldbechangedwithcorrectvalue");

            awaitmodel.save(resultID);

            //startagain,butwithanewrecord
            deletethis.params.res_id;
            resultID=awaitmodel.load(this.params);
            record=model.get(resultID);
            assert.strictEqual(record.data.bar,0,
                "shouldbeinitializedwithcorrectvalue(0asinteger)");

            awaitmodel.notifyChanges(resultID,{foo:"anotherverylongstring"});

            record=model.get(resultID);
            assert.strictEqual(record.data.bar,21,
                "shouldbechangedwithcorrectvalue");

            awaitmodel.save(resultID);
            model.destroy();
        });

        QUnit.test('default_getwithone2manyvalues',asyncfunction(assert){
            assert.expect(1);

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    if(args.method==='default_get'){
                        returnPromise.resolve({
                            product_ids:[[0,0,{"name":"xdroid"}]]
                        });
                    }
                    returnthis._super(route,args);
                },
            });
            varparams={
                fieldNames:['product_ids'],
                fields:this.data.partner.fields,
                modelName:'partner',
                type:'record',
                fieldsInfo:{
                    form:{
                        product_ids:{
                            fieldsInfo:{
                                default:{name:{}},
                            },
                            relatedFields:this.data.product.fields,
                            viewType:'default',
                        },
                    },
                },
                viewType:'form',
            };
            varresultID=awaitmodel.load(params);
            assert.strictEqual(typeofresultID,'string',"resultshouldbeavalidid");
            model.destroy();
        });

        QUnit.test('callmakeRecordwithapre-fetchedmany2onefield',asyncfunction(assert){
            assert.expect(3);
            varrpcCount=0;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            model.makeRecord('coucou',[{
                name:'partner_id',
                relation:'partner',
                type:'many2one',
                value:[1,'firstpartner'],
            }],{
                    partner_id:{
                        options:{
                            no_open:true,
                        },
                    },
                }).then(function(recordID){
                    varrecord=model.get(recordID);
                    assert.deepEqual(record.fieldsInfo.default.partner_id,{options:{no_open:true}},
                        "makeRecordshouldhavegeneratedthefieldsInfo");
                    assert.deepEqual(record.data.partner_id.data,{id:1,display_name:'firstpartner'},
                        "many2oneshouldcontainthepartnerwithid1");
                    assert.strictEqual(rpcCount,0,"makeRecordshouldnothavedoneanyrpc");
                });
            model.destroy();
        });

        QUnit.test('callmakeRecordwithamany2manyfield',asyncfunction(assert){
            assert.expect(5);
            varrpcCount=0;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            varrecordID=awaitmodel.makeRecord('coucou',[{
                name:'partner_ids',
                fields:[{
                    name:'id',
                    type:'integer',
                },{
                    name:'display_name',
                    type:'char',
                }],
                relation:'partner',
                type:'many2many',
                value:[1,2],
            }]);
            varrecord=model.get(recordID);
            assert.deepEqual(record.fieldsInfo.default.partner_ids,{},
                "makeRecordshouldhavegeneratedthefieldsInfo");
            assert.strictEqual(record.data.partner_ids.count,2,
                "thereshouldbe2elementsinthemany2many");
            assert.strictEqual(record.data.partner_ids.data.length,2,
                "many2manyshouldbealistoflength2");
            assert.deepEqual(record.data.partner_ids.data[0].data,{id:1,display_name:'firstpartner'},
                "many2manyshouldcontainthepartnerwithid1");
            assert.strictEqual(rpcCount,1,"makeRecordshouldhavedone1rpc");
            model.destroy();
        });

        QUnit.test('callmakeRecordwithapre-fetchedmany2manyfield',asyncfunction(assert){
            assert.expect(5);
            varrpcCount=0;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            varrecordID=awaitmodel.makeRecord('coucou',[{
                name:'partner_ids',
                fields:[{
                    name:'id',
                    type:'integer',
                },{
                    name:'display_name',
                    type:'char',
                }],
                relation:'partner',
                type:'many2many',
                value:[{
                    id:1,
                    display_name:"firstpartner",
                },{
                    id:2,
                    display_name:"secondpartner",
                }],
            }]);
            varrecord=model.get(recordID);
            assert.deepEqual(record.fieldsInfo.default.partner_ids,{},
                "makeRecordshouldhavegeneratedthefieldsInfo");
            assert.strictEqual(record.data.partner_ids.count,2,
                "thereshouldbe2elementsinthemany2many");
            assert.strictEqual(record.data.partner_ids.data.length,2,
                "many2manyshouldbealistoflength2");
            assert.deepEqual(record.data.partner_ids.data[0].data,{id:1,display_name:'firstpartner'},
                "many2manyshouldcontainthepartnerwithid1");
            assert.strictEqual(rpcCount,0,"makeRecordshouldnothavedoneanyrpc");
            model.destroy();
        });

        QUnit.test('callmakeRecordwithaselectionfield',asyncfunction(assert){
            assert.expect(4);
            varrpcCount=0;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super.apply(this,arguments);
                },
            });

            varrecordID=awaitmodel.makeRecord('partner',[{
                name:'status',
                string:'Status',
                type:'selection',
                selection:[['draft','Draft'],['done','Done'],['failed','Failed']],
                value:'done',
            }]);
            varrecord=model.get(recordID);
            assert.deepEqual(record.fieldsInfo.default.status,{},
                "makeRecordshouldhavegeneratedthefieldsInfo");
            assert.strictEqual(record.data.status,'done',
                "shouldhaveavalue'done'");
            assert.strictEqual(record.fields.status.selection.length,3,
                "shouldhave3keysforselection");
            assert.strictEqual(rpcCount,0,"makeRecordshouldhavedone0rpc");
            model.destroy();
        });

        QUnit.test('callmakeRecordwithareferencefield',asyncfunction(assert){
            assert.expect(2);
            letrpcCount=0;

            constmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    rpcCount++;
                    returnthis._super(route,args);
                },
            });

            constfield=this.data.partner.fields.reference;
            constrecordID=awaitmodel.makeRecord('coucou',[{
                name:'reference',
                type:'reference',
                selection:field.selection,
                value:'product,37',
            }]);
            constrecord=model.get(recordID);
            assert.deepEqual(record.data.reference.data,{id:37,display_name:'xphone'});
            assert.strictEqual(rpcCount,1);

            model.destroy();
        });

        QUnit.test('checkid,active_id,active_ids,active_modelvaluesinrecord\'scontext',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.fields.product_id.context="{'id':id,'active_id':active_id,'active_ids':active_ids,'active_model':active_model}";

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            this.params.fieldNames=['product_id'];

            varresultID=awaitmodel.load(this.params);
            varrecordPartner=model.get(resultID);
            assert.deepEqual(
                recordPartner.getContext({fieldName:"product_id"}),
                {id:2,active_id:2,active_ids:[2],active_model:"partner"},
                "wrongvaluesforid,active_id,active_idsoractive_model");

            //Tryagainwithoutrecord
            this.params.res_id=undefined;

            resultID=awaitmodel.load(this.params);
            recordPartner=model.get(resultID);
            assert.deepEqual(
                recordPartner.getContext({fieldName:"product_id"}),
                {id:false,active_id:false,active_ids:[],active_model:"partner"},
                "wrongvaluesforid,active_id,active_idsoractive_model.Havetobedefinedevenifthereisnorecord.");

            model.destroy();
        });

        QUnit.test('loadmodelwithmany2manyfieldproperlyfetched',asyncfunction(assert){
            assert.expect(2);

            this.params.fieldNames=['category'];
            this.params.res_id=1;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super(route,args);
                },
            });

            awaitmodel.load(this.params);
            assert.verifySteps(['read'],
                "thereshouldbeonlyoneread");
            model.destroy();
        });

        QUnit.test('datashouldcontainallfieldsinview,defaultbeingfalse',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.product_ids.default=[
                [6,0,[]],
                [0,0,{name:'new'}],
            ];
            this.data.product.fields.date={string:"Date",type:"date"};

            varparams={
                fieldNames:['product_ids'],
                modelName:'partner',
                fields:this.data.partner.fields,
                fieldsInfo:{
                    form:{
                        product_ids:{
                            relatedFields:this.data.product.fields,
                            fieldsInfo:{list:{name:{},date:{}}},
                            viewType:'list',
                        }
                    },
                },
                res_id:undefined,
                type:'record',
                viewType:'form',
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            awaitmodel.load(params).then(function(resultID){
                varrecord=model.get(resultID);
                assert.strictEqual(record.data.product_ids.data[0].data.date,false,
                    "datevalueshouldbeindata,andshouldbefalse");
            });

            model.destroy();
        });

        QUnit.test('changesarediscardedwhenreloadingfromanewrecord',asyncfunction(assert){
            //practicalusecase:clickon'Create'toopenaformviewinedit
            //mode(newrecord),clickon'Discard',thenopenanexistingrecord
            assert.expect(2);

            this.data.partner.fields.foo.default='default';
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            //loadanewrecord(default_get)
            varparams=_.extend(this.params,{
                res_id:undefined,
                type:'record',
                fieldNames:['foo'],
            });
            varresultID=awaitmodel.load(params);
            varrecord=model.get(resultID);
            assert.strictEqual(record.data.foo,'default',
                "shouldbethedefaultvalue");

            //reloadwithid2
            resultID=awaitmodel.reload(record.id,{currentId:2});
            record=model.get(resultID);
            assert.strictEqual(record.data.foo,'gnap',
                "shouldbethevalueofrecord2");

            model.destroy();
        });

        QUnit.test('hasaproperevaluationcontext',asyncfunction(assert){
            assert.expect(6);

            constunpatchDate=testUtils.mock.patchDate(1997,0,9,12,0,0);
            this.params.fieldNames=Object.keys(this.data.partner.fields);
            this.params.res_id=1;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            const{evalContext}=model.get(resultID);
            assert.strictEqual(typeofevalContext.datetime,"object");
            assert.strictEqual(typeofevalContext.relativedelta,"object");
            assert.strictEqual(typeofevalContext.time,"object");
            assert.strictEqual(typeofevalContext.context_today,"function");
            assert.strictEqual(typeofevalContext.tz_offset,"function");
            constblackListedKeys=[
                "time",
                "datetime",
                "relativedelta",
                "context_today",
                "tz_offset",
            ];
            //Removeuncomparablevaluesfromtheevaluationcontext
            for(constkeyofblackListedKeys){
                deleteevalContext[key];
            }
            assert.deepEqual(evalContext,{
                active:true,
                active_id:1,
                active_ids:[1],
                active_model:"partner",
                bar:1,
                category:[12],
                current_company_id:false,
                current_date:moment().format('YYYY-MM-DD'),
                today:moment().format('YYYY-MM-DD'),
                now:moment().utc().format('YYYY-MM-DDHH:mm:ss'),
                date:"2017-01-25",
                display_name:"firstpartner",
                foo:"blip",
                id:1,
                product_id:37,
                product_ids:[],
                qux:false,
                reference:false,
                total:0,
                x_active:true,
            },"shouldusetheproperevalcontext");
            model.destroy();
            unpatchDate();
        });

        QUnit.test('x2manysincontextsanddomainsarecorrectlyevaluated',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].product_ids=[37,41];
            this.params.fieldNames=Object.keys(this.data.partner.fields);
            this.params.fieldsInfo={
                form:{
                    qux:{
                        context:"{'category':category,'product_ids':product_ids}",
                        domain:"[['id','in',category],['id','in',product_ids]]",
                        relatedFields:this.data.partner.fields,
                    },
                    category:{
                        relatedFields:this.data.partner_type.fields,
                    },
                    product_ids:{
                        relatedFields:this.data.product.fields,
                    },
                },
            };
            this.params.viewType='form';
            this.params.res_id=1;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            varcontext=record.getContext({fieldName:'qux'});
            vardomain=record.getDomain({fieldName:'qux'});

            assert.deepEqual(context,{
                category:[12],
                product_ids:[37,41],
            },"x2manyvaluesincontextmanipulatedclient-sideshouldbelistsofids");
            assert.strictEqual(JSON.stringify(context),
                "{\"category\":[[6,false,[12]]],\"product_ids\":[[4,37,false],[4,41,false]]}",
                "x2manyvaluesincontextsenttotheservershouldbecommands");
            assert.deepEqual(domain,[
                ['id','in',[12]],
                ['id','in',[37,41]],
            ],"x2manyvaluesindomainsshouldbelistsofids");
            assert.strictEqual(JSON.stringify(domain),
                "[[\"id\",\"in\",[12]],[\"id\",\"in\",[37,41]]]",
                "x2manyvaluesindomainsshouldbelistsofids");
            model.destroy();
        });

        QUnit.test('fetchreferencesinlist,withnottoomanyrpcs',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].reference='product,37';
            this.data.partner.records[1].reference='product,41';

            this.params.fieldNames=['reference'];
            this.params.domain=[];
            this.params.groupedBy=[];
            this.params.res_id=undefined;

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.step(route);
                    if(route==="/web/dataset/call_kw/product/name_get"){
                        assert.deepEqual(args.args,[[37,41]],
                            "thename_getshouldcontaintheproductids");
                    }
                    returnthis._super(route,args);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);

            assert.strictEqual(record.data[0].data.reference.data.display_name,"xphone",
                "name_getshouldhavebeencorrectlyfetched");
            assert.verifySteps(["/web/dataset/search_read","/web/dataset/call_kw/product/name_get"],
                "shouldhavedone2rpc(searchreadandname_getforproduct)");
            model.destroy();
        });

        QUnit.test('reloadanewrecord',asyncfunction(assert){
            assert.expect(6);

            this.params.context={};
            this.params.fieldNames=['product_id','category','product_ids'];
            this.params.res_id=undefined;
            this.params.type='record';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super(route,args);
                },
            });

            varrecordID=awaitmodel.load(this.params);
            recordID=awaitmodel.reload(recordID);
            assert.verifySteps(['onchange','onchange']);
            varrecord=model.get(recordID);
            assert.strictEqual(record.data.product_id,false,
                "m2odefaultvalueshouldbefalse");
            assert.deepEqual(record.data.product_ids.data,[],
                "o2mdefaultshouldbe[]");
            assert.deepEqual(record.data.category.data,[],
                "m2mdefaultshouldbe[]");

            model.destroy();
        });

        QUnit.test('default_getwithvaluefalseforaone2many',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.product_ids.default=false;
            this.params.fieldNames=['product_ids'];
            this.params.res_id=undefined;
            this.params.type='record';

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.deepEqual(record.data.product_ids.data,[],"o2mdefaultshouldbe[]");

            model.destroy();
        });

        QUnit.test('onlyx2manylists(static)shouldbesortedclient-side',asyncfunction(assert){
            assert.expect(1);

            this.params.modelName='partner_type';
            this.params.res_id=undefined;
            this.params.orderedBy=[{name:'display_name',asc:true}];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
                mockRPC:function(route){
                    if(route==='/web/dataset/search_read'){
                        //simulaterandomnsortformtheserver
                        returnPromise.resolve({
                            length:3,
                            records:[
                                {id:12,display_name:"gold",date:"2017-01-25"},
                                {id:15,display_name:"bronze"},
                                {id:14,display_name:"silver"},
                            ],
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            varresultID=awaitmodel.load(this.params);
            varlist=model.get(resultID);
            assert.deepEqual(_.map(list.data,'res_id'),[12,15,14],
                "shouldhavekepttheorderfromtheserver");
            model.destroy();
        });

        QUnit.test('onchangeonabooleanfield',asyncfunction(assert){
            assert.expect(2);

            varnewFields={
                foobool:{
                    type:'boolean',
                    string:'foobool',
                },
                foobool2:{
                    type:'boolean',
                    string:'foobool2',
                },
            };
            _.extend(this.data.partner.fields,newFields);

            this.data.partner.fields.foobool.onChange=true;
            this.data.partner.onchanges.foobool=function(obj){
                if(obj.foobool){
                    obj.foobool2=true;
                }
            };

            this.data.partner.records[0].foobool=false;
            this.data.partner.records[0].foobool2=true;

            this.params.res_id=1;
            this.params.fieldNames=['foobool','foobool2'];
            this.params.fields=this.data.partner.fields;
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            awaitmodel.notifyChanges(resultID,{foobool2:false});
            record=model.get(resultID);
            assert.strictEqual(record.data.foobool2,false,"foobool2fieldshouldbefalse");
            awaitmodel.notifyChanges(resultID,{foobool:true});
            record=model.get(resultID);
            assert.strictEqual(record.data.foobool2,true,"foobool2fieldshouldbetrue");
            model.destroy();
        });

        QUnit.test('notifyChangeDELETE_ALLonaone2many',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[1].product_ids=[37,38];
            this.params.fieldNames=['product_ids'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varo2mParams={
                modelName:'product',
                fields:this.data.product.fields,
            };

            varresultID=awaitmodel.load(this.params);
            varnewRecordID=awaitmodel.load(o2mParams);
            varrecord=model.get(resultID);
            varx2mListID=record.data.product_ids.id;

            assert.strictEqual(record.data.product_ids.count,2,
                "thereshouldbetworecordsintherelation");

            awaitmodel.notifyChanges(resultID,{product_ids:{operation:'ADD',id:newRecordID}});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                operation:'ADD',id:newRecordID,
            }],"_changesshouldbecorrect");

            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,3,
                "thereshouldbethreerecordsintherelation");

            awaitmodel.notifyChanges(resultID,{product_ids:{operation:'DELETE_ALL'}});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                id:37,
                operation:"DELETE"
            },{
                id:38,
                operation:"DELETE"
            }],"_changesshouldcontainthetwo'DELETE'operations");

            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,0,
                "thereshouldbenomorerecordsintherelation");
            model.destroy();
        });

        QUnit.test('notifyChangeMULTIonaone2many',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[1].product_ids=[37,38];
            this.params.fieldNames=['product_ids'];

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varo2mParams={
                modelName:'product',
                fields:this.data.product.fields,
            };

            varresultID=awaitmodel.load(this.params);
            varnewRecordID=awaitmodel.load(o2mParams);
            varrecord=model.get(resultID);
            varx2mListID=record.data.product_ids.id;

            assert.strictEqual(record.data.product_ids.count,2,
                "thereshouldbetworecordsintherelation");

            awaitmodel.notifyChanges(resultID,{product_ids:{
                operation:'MULTI',
                commands:[{
                    operation:'DELETE_ALL'
                },{
                    operation:'ADD',
                    id:newRecordID
                }]
            }});

            assert.deepEqual(model.localData[x2mListID]._changes,[{
                id:37,
                operation:"DELETE"
            },{
                id:38,
                operation:"DELETE"
            },{
                operation:'ADD',id:newRecordID,
            }],"_changesshouldbecorrect");

            record=model.get(resultID);
            assert.strictEqual(record.data.product_ids.count,1,
                "thereshouldbeonerecordintherelation");

            assert.strictEqual(record.data.product_ids.data[0].id,newRecordID,
                "theidshouldmatch");
        });

        QUnit.test('notifyChangeMULTIonamany2many',asyncfunction(assert){
            assert.expect(3);

            this.params.fieldsInfo={
                default:{
                    category:{
                        fieldsInfo:{default:{some_char:{context:"{'a':parent.foo}"}}},
                        relatedFields:{some_char:{type:"char"}},
                        viewType:'default',
                    },
                    foo:{},
                },
            };

            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });

            varresultID=awaitmodel.load(this.params);
            varchanges={
                category:{
                    operation:'MULTI',
                    commands:[{
                        operation:'ADD_M2M',
                        ids:[{id:23},{id:24},{id:25}]
                    },{
                        operation:'ADD_M2M',
                        ids:[{id:26}]
                    }]
                }
            };
            awaitmodel.notifyChanges(resultID,changes);
            varrecord=model.get(resultID);
            varcategoryRecord=record.data.category;

            assert.strictEqual(categoryRecord.data.length,4,
                "thereshould2recordsintherelation");

            awaitmodel.notifyChanges(resultID,{category:{
                operation:'MULTI',
                commands:[{
                    operation:'DELETE_ALL'
                },{
                    operation:'ADD_M2M',
                    ids:[{id:27}]
                }]
            }});
            record=model.get(resultID);
            categoryRecord=record.data.category;
            assert.strictEqual(categoryRecord.data.length,1,
                "thereshould1recordintherelation");

            assert.strictEqual(record.data.category.data[0].data.id,27,
                "theidshouldmatch");

            model.destroy();
        });

        QUnit.test('identifycorrectactivefield',asyncfunction(assert){
            assert.expect(4);
            varmodel=awaitcreateModel({
                Model:BasicModel,
                data:this.data,
            });
            //checkthatactivefieldisreturnedifpresent
            this.params.res_id=37;
            this.params.modelName='product'
            this.params.fields=this.data.product.fields;
            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.equal(model.getActiveField(record),'active','shouldhavereturned"active"fieldname');
            //checkthatactivefieldisnotreturnedifnotpresent
            this.params.res_id=42;
            this.params.modelName='partner_title';
            this.params.fields=this.data.partner_title.fields;
            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.equal(model.getActiveField(record),undefined,'shouldnothavereturnedanyfieldname');
            //checkthatx_activefieldisreturnedifx_activepresent
            this.params.res_id=12;
            this.params.modelName='partner_type';
            this.params.fields=this.data.partner_type.fields;
            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.equal(model.getActiveField(record),'x_active','shouldhavereturned"x_active"fieldname');

            //checkthatactivefieldisreturnedifbothactiveandx_activepresent
            this.params.res_id=1;
            this.params.modelName='partner';
            this.params.fields=this.data.partner.fields;
            varresultID=awaitmodel.load(this.params);
            varrecord=model.get(resultID);
            assert.equal(model.getActiveField(record),'active','shouldhavereturned"active"fieldname');
        });
    });
});
