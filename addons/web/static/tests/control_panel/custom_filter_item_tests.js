flectra.define('web.filter_menu_generator_tests',function(require){
    "usestrict";

    constDomain=require('web.Domain');
    constCustomFilterItem=require('web.CustomFilterItem');
    constActionModel=require('web/static/src/js/views/action_model.js');
    constpyUtils=require('web.py_utils');
    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;
    const{createComponent}=testUtils;

    QUnit.module('Components',{
        beforeEach:function(){
            this.fields={
                date_field:{name:'date_field',string:"Adate",type:'date',searchable:true},
                date_time_field:{name:'date_time_field',string:"DateTime",type:'datetime',searchable:true},
                boolean_field:{name:'boolean_field',string:"BooleanField",type:'boolean',default:true,searchable:true},
                binary_field:{name:'binary_field',string:"BinaryField",type:'binary',searchable:true},
                char_field:{name:'char_field',string:"CharField",type:'char',default:"foo",trim:true,searchable:true},
                float_field:{name:'float_field',string:"FloatyMcFloatface",type:'float',searchable:true},
                color:{name:'color',string:"Color",type:'selection',selection:[['black',"Black"],['white',"White"]],searchable:true},
            };
        },
    },function(){

        QUnit.module('CustomFilterItem');

        QUnit.test('basicrendering',asyncfunction(assert){
            assert.expect(17);

            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{
                    searchModel:newActionModel(),
                },
            });

            assert.strictEqual(cfi.el.innerText.trim(),"AddCustomFilter");
            assert.hasClass(cfi.el,'o_generator_menu');
            assert.strictEqual(cfi.el.children.length,1);

            awaitcpHelpers.toggleAddCustomFilter(cfi);

            //Singlecondition
            assert.containsOnce(cfi,'div.o_filter_condition');
            assert.containsOnce(cfi,'div.o_filter_condition>select.o_generator_menu_field');
            assert.containsOnce(cfi,'div.o_filter_condition>select.o_generator_menu_operator');
            assert.containsOnce(cfi,'div.o_filter_condition>span.o_generator_menu_value');
            assert.containsNone(cfi,'div.o_filter_condition.o_or_filter');
            assert.containsNone(cfi,'div.o_filter_condition.o_generator_menu_delete');

            //nodeletionallowedonsinglecondition
            assert.containsNone(cfi,'div.o_filter_condition>i.o_generator_menu_delete');

            //Buttons
            assert.containsOnce(cfi,'div.o_add_filter_menu');
            assert.containsOnce(cfi,'div.o_add_filter_menu>button.o_apply_filter');
            assert.containsOnce(cfi,'div.o_add_filter_menu>button.o_add_condition');

            assert.containsOnce(cfi,'div.o_filter_condition');

            awaittestUtils.dom.click('button.o_add_condition');

            assert.containsN(cfi,'div.o_filter_condition',2);
            assert.containsOnce(cfi,'div.o_filter_condition.o_or_filter');
            assert.containsN(cfi,'div.o_filter_condition.o_generator_menu_delete',2);

            cfi.destroy();
        });

        QUnit.test('binaryfield:basicsearch',asyncfunction(assert){
            assert.expect(4);

            letexpectedFilters;
            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    assert.deepEqual(preFilters,expectedFilters);
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            //Defaultvalue
            expectedFilters=[{
                description:'BinaryFieldisset',
                domain:'[["binary_field","!=",False]]',
                type:'filter',
            }];
            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'binary_field');
            awaitcpHelpers.applyFilter(cfi);

            //Updatedvalue
            expectedFilters=[{
                description:'BinaryFieldisnotset',
                domain:'[["binary_field","=",False]]',
                type:'filter',
            }];
            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'binary_field');
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_operator'),'=');
            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        });

        QUnit.test('selectionfield:defaultandupdatedvalue',asyncfunction(assert){
            assert.expect(4);

            letexpectedFilters;
            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    assert.deepEqual(preFilters,expectedFilters);
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            //Defaultvalue
            expectedFilters=[{
                description:'Coloris"Black"',
                domain:'[["color","=","black"]]',
                type:'filter',
            }];
            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'color');
            awaitcpHelpers.applyFilter(cfi);

            //Updatedvalue
            expectedFilters=[{
                description:'Coloris"White"',
                domain:'[["color","=","white"]]',
                type:'filter',
            }];
            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'color');
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_valueselect'),'white');
            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        });
        QUnit.test('selectionfield:novalue',asyncfunction(assert){
            assert.expect(2);

            this.fields.color.selection=[];
            letexpectedFilters;
            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    assert.deepEqual(preFilters,expectedFilters);
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            //Defaultvalue
            expectedFilters=[{
                description:'Coloris""',
                domain:'[["color","=",""]]',
                type:'filter',
            }];
            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'color');
            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        })

        QUnit.test('addingasimplefilterworks',asyncfunction(assert){
            assert.expect(6);

            deletethis.fields.date_field;

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constpreFilter=preFilters[0];
                    assert.strictEqual(preFilter.type,'filter');
                    assert.strictEqual(preFilter.description,'BooleanFieldistrue');
                    assert.strictEqual(preFilter.domain,'[["boolean_field","=",True]]');
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'boolean_field');
            awaitcpHelpers.applyFilter(cfi);

            //Theonlythingvisibleshouldbethebutton'AddCustomeFilter';
            assert.strictEqual(cfi.el.children.length,1);
            assert.containsOnce(cfi,'button.o_add_custom_filter');

            cfi.destroy();
        });

        QUnit.test('filteringbyIDintervalworks',asyncfunction(assert){
            assert.expect(2);
            this.fields.id_field={name:'id_field',string:"ID",type:"id",searchable:true};

            constexpectedDomains=[
                [['id_field','>',10]],
                [['id_field','<=',20]],
            ];

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constpreFilter=preFilters[0];
                    //thisstepcombineatokenization/parsingfollowedbyastringformatting
                    letdomain=pyUtils.assembleDomains([preFilter.domain]);
                    domain=Domain.prototype.stringToArray(domain);
                    assert.deepEqual(domain,expectedDomains.shift());
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            asyncfunctiontestValue(operator,value){
                //openfiltermenugenerator,selectIDfield,switchoperator,typevalue,thenclickapply
                awaitcpHelpers.toggleAddCustomFilter(cfi);
                awaittestUtils.fields.editSelect(cfi.el.querySelector('select.o_generator_menu_field'),'id_field');
                awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_operator'),operator);
                awaittestUtils.fields.editInput(cfi.el.querySelector(
                    'div.o_filter_condition>span.o_generator_menu_valueinput'),
                    value
                );
                awaitcpHelpers.applyFilter(cfi);
            }

            for(constdomainofexpectedDomains){
                awaittestValue(domain[0][1],domain[0][2]);
            }

            cfi.destroy();
        });


        QUnit.test('commitsearchwithanextendedpropositionwithfieldchardoesnotcauseacrash',asyncfunction(assert){
            assert.expect(12);

            this.fields.many2one_field={name:'many2one_field',string:"Trululu",type:"many2one",searchable:true};
            constexpectedDomains=[
                [['many2one_field','ilike',`a`]],
                [['many2one_field','ilike',`"a"`]],
                [['many2one_field','ilike',`'a'`]],
                [['many2one_field','ilike',`'`]],
                [['many2one_field','ilike',`"`]],
                [['many2one_field','ilike',`\\`]],
            ];
            consttestedValues=[`a`,`"a"`,`'a'`,`'`,`"`,`\\`];

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constpreFilter=preFilters[0];
                    //thisstepcombineatokenization/parsingfollowedbyastringformatting
                    letdomain=pyUtils.assembleDomains([preFilter.domain]);
                    domain=Domain.prototype.stringToArray(domain);
                    assert.deepEqual(domain,expectedDomains.shift());
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            asyncfunctiontestValue(value){
                //openfiltermenugenerator,selecttrululufieldandenterstring`a`,thenclickapply
                awaitcpHelpers.toggleAddCustomFilter(cfi);
                awaittestUtils.fields.editSelect(cfi.el.querySelector('select.o_generator_menu_field'),'many2one_field');
                awaittestUtils.fields.editInput(cfi.el.querySelector(
                    'div.o_filter_condition>span.o_generator_menu_valueinput'),
                    value
                );
                awaitcpHelpers.applyFilter(cfi);
            }

            for(constvalueoftestedValues){
                awaittestValue(value);
            }

            deleteActionModel.registry.map.testExtension;
            cfi.destroy();
        });

        QUnit.test('customfilterdatetimewithequaloperator',asyncfunction(assert){
            assert.expect(5);

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constpreFilter=preFilters[0];
                    assert.strictEqual(preFilter.description,
                        'DateTimeisequalto"02/22/201711:00:00"',
                        "descriptionshouldbeinlocalizedformat");
                    assert.deepEqual(preFilter.domain,
                        '[["date_time_field","=","2017-02-2215:00:00"]]',
                        "domainshouldbeinUTCformat");
                    }
                }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                session:{
                    getTZOffset(){
                        return-240;
                    },
                },
                env:{searchModel},
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'date_time_field');

            assert.strictEqual(cfi.el.querySelector('.o_generator_menu_field').value,'date_time_field');
            assert.strictEqual(cfi.el.querySelector('.o_generator_menu_operator').value,'between');

            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_operator'),'=');
            awaittestUtils.fields.editSelect(cfi.el.querySelector('div.o_filter_condition>span.o_generator_menu_valueinput'),'02/22/201711:00:00');//inTZ
            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        });

        QUnit.test('customfilterdatetimebetweenoperator',asyncfunction(assert){
            assert.expect(5);

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constpreFilter=preFilters[0];
                    assert.strictEqual(preFilter.description,
                        'DateTimeisbetween"02/22/201711:00:00and02/22/201717:00:00"',
                        "descriptionshouldbeinlocalizedformat");
                    assert.deepEqual(preFilter.domain,
                        '[["date_time_field",">=","2017-02-2215:00:00"]'+
                        ',["date_time_field","<=","2017-02-2221:00:00"]]',
                        "domainshouldbeinUTCformat");
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                session:{
                    getTZOffset(){
                        return-240;
                    },
                },
                env:{searchModel},
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'date_time_field');

            assert.strictEqual(cfi.el.querySelector('.o_generator_menu_field').value,'date_time_field');
            assert.strictEqual(cfi.el.querySelector('.o_generator_menu_operator').value,'between');

            constvalueInputs=cfi.el.querySelectorAll('.o_generator_menu_value.o_input');
            awaittestUtils.fields.editSelect(valueInputs[0],'02/22/201711:00:00');//inTZ
            awaittestUtils.fields.editSelect(valueInputs[1],'02-22-201717:00:00');//inTZ
            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        });

        QUnit.test('defaultcustomfilterdatetime',asyncfunction(assert){
            assert.expect(5);

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constdomain=JSON.parse(args[0][0].domain);
                    assert.strictEqual(domain[0][2].split('')[1],
                        '04:00:00',
                        "domainshouldbeinUTCformat");
                    assert.strictEqual(domain[1][2].split('')[1],
                        '03:59:59',
                        "domainshouldbeinUTCformat");
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                session:{
                    getTZOffset(){
                        return-240;
                    },
                },
                env:{searchModel},
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'date_time_field');

            assert.strictEqual(cfi.el.querySelector('.o_generator_menu_field').value,'date_time_field');
            assert.strictEqual(cfi.el.querySelector('.o_generator_menu_operator').value,'between');

            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        });

        QUnit.test('inputvalueparsing',asyncfunction(assert){
            assert.expect(7);

            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{
                    searchModel:newActionModel(),
                },
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.dom.click('button.o_add_condition');

            const[floatSelect,idSelect]=cfi.el.querySelectorAll('.o_generator_menu_field');
            awaittestUtils.fields.editSelect(floatSelect,'float_field');
            awaittestUtils.fields.editSelect(idSelect,'id');

            const[floatInput,idInput]=cfi.el.querySelectorAll('.o_generator_menu_value.o_input');

            //Defaultvalues
            assert.strictEqual(floatInput.value,"0.0");
            assert.strictEqual(idInput.value,"0");

            //Floatparsing
            awaittestUtils.fields.editAndTrigger(floatInput,"4.2",["input","change"]);
            assert.strictEqual(floatInput.value,"4.2");
            awaittestUtils.fields.editAndTrigger(floatInput,"DefinitelyValidFloat",["input","change"]);
            //Stringinputinanumberinputgives"",whichisparsedas0
            assert.strictEqual(floatInput.value,"0.0");

            //Numberparsing
            awaittestUtils.fields.editAndTrigger(idInput,"4",["input","change"]);
            assert.strictEqual(idInput.value,"4");
            awaittestUtils.fields.editAndTrigger(idInput,"4.2",["input","change"]);
            assert.strictEqual(idInput.value,"4");
            awaittestUtils.fields.editAndTrigger(idInput,"DefinitelyValidID",["input","change"]);
            //Stringinputinanumberinputgives"",whichisparsedas0
            assert.strictEqual(idInput.value,"0");

            cfi.destroy();
        });

        QUnit.test('inputvalueparsingwithlanguage',asyncfunction(assert){
            assert.expect(5);

            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{
                    searchModel:newActionModel(),
                    _t:Object.assign(s=>s,{database:{parameters:{decimal_point:","}}}),
                },
                translateParameters:{
                    decimal_point:",",
                    thousands_sep:"",
                    grouping:[3,0],
                },
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.dom.click('button.o_add_condition');

            const[floatSelect]=cfi.el.querySelectorAll('.o_generator_menu_field');
            awaittestUtils.fields.editSelect(floatSelect,'float_field');

            const[floatInput]=cfi.el.querySelectorAll('.o_generator_menu_value.o_input');

            //Defaultvalues
            assert.strictEqual(floatInput.value,"0,0");

            //Floatparsing
            awaittestUtils.fields.editInput(floatInput,'4,');
            assert.strictEqual(floatInput.value,"4,");
            awaittestUtils.fields.editAndTrigger(floatInput,'4,2',["input","change"]);
            assert.strictEqual(floatInput.value,"4,2");
            awaittestUtils.fields.editAndTrigger(floatInput,'4,2,',["input","change"]);
            assert.strictEqual(floatInput.value,"4,2");
            awaittestUtils.fields.editAndTrigger(floatInput,"DefinitelyValidFloat",["input","change"]);
            //Theinputhereisastring,resultinginaparsingerrorinsteadof0
            assert.strictEqual(floatInput.value,"4,2");

            cfi.destroy();
        });

        QUnit.test('addcustomfilterwithmultiplevalues',asyncfunction(assert){
            assert.expect(2);

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constexpected=[
                        {
                            description:'Adateisequalto"01/09/1997"',
                            domain:'[["date_field","=","1997-01-09"]]',
                            type:"filter",
                        },
                        {
                            description:'BooleanFieldistrue',
                            domain:'[["boolean_field","=",True]]',
                            type:"filter",
                        },
                        {
                            description:'FloatyMcFloatfaceisequalto"7.2"',
                            domain:'[["float_field","=",7.2]]',
                            type:"filter",
                        },
                        {
                            description:'IDis"9"',
                            domain:'[["id","=",9]]',
                            type:"filter",
                        },
                    ];
                    assert.deepEqual(preFilters,expected,
                        "Conditionsshouldbeinthecorrectorderwithttherightvalues.");
                }
            }
            constsearchModel=newMockedSearchModel();
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{searchModel},
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.dom.click('button.o_add_condition');
            awaittestUtils.dom.click('button.o_add_condition');
            awaittestUtils.dom.click('button.o_add_condition');
            awaittestUtils.dom.click('button.o_add_condition');

            functiongetCondition(index,selector){
                constcondition=cfi.el.querySelectorAll('.o_filter_condition')[index];
                returncondition.querySelector(selector);
            }

            awaittestUtils.fields.editSelect(getCondition(0,'.o_generator_menu_field'),'date_field');
            awaittestUtils.fields.editSelect(getCondition(0,'.o_generator_menu_value.o_input'),'01/09/1997');

            awaittestUtils.fields.editSelect(getCondition(1,'.o_generator_menu_field'),'boolean_field');
            awaittestUtils.fields.editInput(getCondition(1,'.o_generator_menu_operator'),'!=');

            awaittestUtils.fields.editSelect(getCondition(2,'.o_generator_menu_field'),'char_field');
            awaittestUtils.fields.editInput(getCondition(2,'.o_generator_menu_value.o_input'),"Iwillbedeletedanyway");

            awaittestUtils.fields.editSelect(getCondition(3,'.o_generator_menu_field'),'float_field');
            awaittestUtils.fields.editAndTrigger(getCondition(3,'.o_generator_menu_value.o_input'),7.2,["input","change"]);

            awaittestUtils.fields.editSelect(getCondition(4,'.o_generator_menu_field'),'id');
            awaittestUtils.fields.editInput(getCondition(4,'.o_generator_menu_value.o_input'),9);

            awaittestUtils.dom.click(getCondition(2,'.o_generator_menu_delete'));

            awaitcpHelpers.applyFilter(cfi);

            cfi.destroy();
        });

        QUnit.test('floatinputcanbeempty',asyncfunction(assert){
            assert.expect(2);

            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:this.fields,
                },
                env:{
                    searchModel:newActionModel(),
                    _t:Object.assign(s=>s,{database:{parameters:{decimal_point:","}}}),
                },
                translateParameters:{
                    decimal_point:",",
                    thousands_sep:"",
                    grouping:[3,0],
                },
            });

            awaitcpHelpers.toggleAddCustomFilter(cfi);
            awaittestUtils.dom.click('button.o_add_condition');

            const[floatSelect]=cfi.el.querySelectorAll('.o_generator_menu_field');
            awaittestUtils.fields.editSelect(floatSelect,'float_field');

            const[floatInput]=cfi.el.querySelectorAll('.o_generator_menu_value.o_input');

            //Weintroduceapreviousvalueincasewedon'thaveadefaultvalue
            awaittestUtils.fields.editInput(floatInput,'3,14');
            assert.strictEqual(floatInput.value,'3,14');
            //Inputvaluecanbecompletelycleared
            awaittestUtils.fields.editInput(floatInput,'');
            assert.strictEqual(floatInput.value,'');

            cfi.destroy();
        });
    });
});
