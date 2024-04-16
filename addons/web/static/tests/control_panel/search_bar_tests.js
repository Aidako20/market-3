flectra.define('web.search_bar_tests',function(require){
    "usestrict";

    const{Model}=require('web/static/src/js/model.js');
    constRegistry=require("web.Registry");
    constSearchBar=require('web.SearchBar');
    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;
    const{createActionManager,createComponent}=testUtils;

    QUnit.module('Components',{
        beforeEach:function(){
            this.data={
                partner:{
                    fields:{
                        bar:{string:"Bar",type:'many2one',relation:'partner'},
                        birthday:{string:"Birthday",type:'date'},
                        birth_datetime:{string:"BirthDateTime",type:'datetime'},
                        foo:{string:"Foo",type:'char'},
                        bool:{string:"Bool",type:'boolean'},
                    },
                    records:[
                        {id:1,display_name:"Firstrecord",foo:"yop",bar:2,bool:true,birthday:'1983-07-15',birth_datetime:'1983-07-1501:00:00'},
                        {id:2,display_name:"Secondrecord",foo:"blip",bar:1,bool:false,birthday:'1982-06-04',birth_datetime:'1982-06-0402:00:00'},
                        {id:3,display_name:"Thirdrecord",foo:"gnap",bar:1,bool:false,birthday:'1985-09-13',birth_datetime:'1985-09-1303:00:00'},
                        {id:4,display_name:"Fourthrecord",foo:"plop",bar:2,bool:true,birthday:'1983-05-05',birth_datetime:'1983-05-0504:00:00'},
                        {id:5,display_name:"Fifthrecord",foo:"zoup",bar:2,bool:true,birthday:'1800-01-01',birth_datetime:'1800-01-0105:00:00'},
                    ],
                },
            };

            this.actions=[{
                id:1,
                name:"PartnersAction",
                res_model:'partner',
                search_view_id:[false,'search'],
                type:'ir.actions.act_window',
                views:[[false,'list']],
            }];

            this.archs={
                'partner,false,list':`
                <tree>
                    <fieldname="foo"/>
                </tree>`,
                'partner,false,search':`
                <search>
                    <fieldname="foo"/>
                    <fieldname="birthday"/>
                    <fieldname="birth_datetime"/>
                    <fieldname="bar"context="{'bar':self}"/>
                    <filterstring="DateFieldFilter"name="positive"date="birthday"/>
                    <filterstring="DateFieldGroupby"name="coolName"context="{'group_by':'birthday:day'}"/>
                </search>`,
            };
        },
    },function(){

        QUnit.module('SearchBar');

        QUnit.test('basicrendering',asyncfunction(assert){
            assert.expect(1);

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
            });
            awaitactionManager.doAction(1);

            assert.strictEqual(document.activeElement,
                actionManager.el.querySelector('.o_searchviewinput.o_searchview_input'),
                "searchviewinputshouldbefocused");

            actionManager.destroy();
        });

        QUnit.test('navigationwithfacets',asyncfunction(assert){
            assert.expect(4);

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
            });
            awaitactionManager.doAction(1);

            //addafacet
            awaitcpHelpers.toggleGroupByMenu(actionManager);
            awaitcpHelpers.toggleMenuItem(actionManager,0);
            awaitcpHelpers.toggleMenuItemOption(actionManager,0,0);
            assert.containsOnce(actionManager,'.o_searchview.o_searchview_facet',
                "thereshouldbeonefacet");
            assert.strictEqual(document.activeElement,
                actionManager.el.querySelector('.o_searchviewinput.o_searchview_input'));

            //presslefttofocusthefacet
            awaittestUtils.dom.triggerEvent(document.activeElement,'keydown',{key:'ArrowLeft'});
            assert.strictEqual(document.activeElement,actionManager.el.querySelector('.o_searchview.o_searchview_facet'));

            //pressrighttofocustheinput
            awaittestUtils.dom.triggerEvent(document.activeElement,'keydown',{key:'ArrowRight'});
            assert.strictEqual(document.activeElement,actionManager.el.querySelector('.o_searchviewinput.o_searchview_input'));

            actionManager.destroy();
        });

        QUnit.test('searchdateanddatetimefields.Supportoftimezones',asyncfunction(assert){
            assert.expect(4);

            letsearchReadCount=0;
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                session:{
                    getTZOffset(){
                        return360;
                    }
                },
                asyncmockRPC(route,args){
                    if(route==='/web/dataset/search_read'){
                        switch(searchReadCount){
                            case0:
                                //Doneonloading
                                break;
                            case1:
                                assert.deepEqual(args.domain,[["birthday","=","1983-07-15"]],
                                    "Adateshouldstaywhattheuserhasinput,buttransmittedinserver'sformat");
                                break;
                            case2:
                                //Doneonclosingthefirstfacet
                                break;
                            case3:
                                assert.deepEqual(args.domain,[["birth_datetime","=","1983-07-1418:00:00"]],
                                    "AdatetimeshouldbetransformedinUTCandtransmittedinserver'sformat");
                                break;
                        }
                        searchReadCount++;
                    }
                    returnthis._super(...arguments);
                },
            });
            awaitactionManager.doAction(1);

            //Datecase
            letsearchInput=actionManager.el.querySelector('.o_searchview_input');
            awaittestUtils.fields.editInput(searchInput,'07/15/1983');
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});

            assert.strictEqual(actionManager.el.querySelector('.o_searchview_facet.o_facet_values').innerText.trim(),
                '07/15/1983',
                'Theformatofthedateinthefacetshouldbeinlocale');

            //CloseFacet
            awaittestUtils.dom.click($('.o_searchview_facet.o_facet_remove'));

            //DateTimecase
            searchInput=actionManager.el.querySelector('.o_searchview_input');
            awaittestUtils.fields.editInput(searchInput,'07/15/198300:00:00');
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});

            assert.strictEqual(actionManager.el.querySelector('.o_searchview_facet.o_facet_values').innerText.trim(),
                '07/15/198300:00:00',
                'Theformatofthedatetimeinthefacetshouldbeinlocale');

            actionManager.destroy();
        });

        QUnit.test("autocompletemenuclickoutinteractions",asyncfunction(assert){
            assert.expect(9);

            constfields=this.data.partner.fields;

            classTestModelExtensionextendsModel.Extension{
                get(property){
                    switch(property){
                        case'facets':
                            return[];
                        case'filters':
                            returnObject.keys(fields).map((fname,index)=>Object.assign({
                                description:fields[fname].string,
                                fieldName:fname,
                                fieldType:fields[fname].type,
                                id:index,
                            },fields[fname]));
                        default:
                            break;
                    }
                }
            }
            classMockedModelextendsModel{}
            MockedModel.registry=newRegistry({Test:TestModelExtension,});
            constsearchModel=newMockedModel({Test:{}});
            constsearchBar=awaitcreateComponent(SearchBar,{
                data:this.data,
                env:{searchModel},
                props:{fields},
            });
            constinput=searchBar.el.querySelector('.o_searchview_input');

            assert.containsNone(searchBar,'.o_searchview_autocomplete');

            awaittestUtils.controlPanel.editSearch(searchBar,"Hellothere");

            assert.strictEqual(input.value,"Hellothere","inputvalueshouldbeupdated");
            assert.containsOnce(searchBar,'.o_searchview_autocomplete');

            awaittestUtils.dom.triggerEvent(input,'keydown',{key:'Escape'});

            assert.strictEqual(input.value,"","inputvalueshouldbeempty");
            assert.containsNone(searchBar,'.o_searchview_autocomplete');

            awaittestUtils.controlPanel.editSearch(searchBar,"GeneralKenobi");

            assert.strictEqual(input.value,"GeneralKenobi","inputvalueshouldbeupdated");
            assert.containsOnce(searchBar,'.o_searchview_autocomplete');

            awaittestUtils.dom.click(document.body);

            assert.strictEqual(input.value,"","inputvalueshouldbeempty");
            assert.containsNone(searchBar,'.o_searchview_autocomplete');

            searchBar.destroy();
        });

        QUnit.test('selectanautocompletefield',asyncfunction(assert){
            assert.expect(3);

            letsearchReadCount=0;
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                asyncmockRPC(route,args){
                    if(route==='/web/dataset/search_read'){
                        switch(searchReadCount){
                            case0:
                                //Doneonloading
                                break;
                            case1:
                                assert.deepEqual(args.domain,[["foo","ilike","a"]]);
                                break;
                        }
                        searchReadCount++;
                    }
                    returnthis._super(...arguments);
                },
            });
            awaitactionManager.doAction(1);

            constsearchInput=actionManager.el.querySelector('.o_searchview_input');
            awaittestUtils.fields.editInput(searchInput,'a');
            assert.containsN(actionManager,'.o_searchview_autocompleteli',2,
                "thereshouldbe2resultfor'a'insearchbarautocomplete");

            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});
            assert.strictEqual(actionManager.el.querySelector('.o_searchview_input_container.o_facet_values').innerText.trim(),
                "a","Thereshouldbeafieldfacetwithlabel'a'");

            actionManager.destroy();
        });

        QUnit.test('autocompleteinputistrimmed',asyncfunction(assert){
            assert.expect(3);

            letsearchReadCount=0;
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                asyncmockRPC(route,args){
                    if(route==='/web/dataset/search_read'){
                        switch(searchReadCount){
                            case0:
                                //Doneonloading
                                break;
                            case1:
                                assert.deepEqual(args.domain,[["foo","ilike","a"]]);
                                break;
                        }
                        searchReadCount++;
                    }
                    returnthis._super(...arguments);
                },
            });
            awaitactionManager.doAction(1);

            constsearchInput=actionManager.el.querySelector('.o_searchview_input');
            awaittestUtils.fields.editInput(searchInput,'a');
            assert.containsN(actionManager,'.o_searchview_autocompleteli',2,
                "thereshouldbe2resultfor'a'insearchbarautocomplete");

            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});
            assert.strictEqual(actionManager.el.querySelector('.o_searchview_input_container.o_facet_values').innerText.trim(),
                "a","Thereshouldbeafieldfacetwithlabel'a'");

            actionManager.destroy();
        });

        QUnit.test('selectanautocompletefieldwith`context`key',asyncfunction(assert){
            assert.expect(9);

            letsearchReadCount=0;
            constfirstLoading=testUtils.makeTestPromise();
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                asyncmockRPC(route,args){
                    if(route==='/web/dataset/search_read'){
                        switch(searchReadCount){
                            case0:
                                firstLoading.resolve();
                                break;
                            case1:
                                assert.deepEqual(args.domain,[["bar","=",1]]);
                                assert.deepEqual(args.context.bar,[1]);
                                break;
                            case2:
                                assert.deepEqual(args.domain,["|",["bar","=",1],["bar","=",2]]);
                                assert.deepEqual(args.context.bar,[1,2]);
                                break;
                        }
                        searchReadCount++;
                    }
                    returnthis._super(...arguments);
                },
            });
            awaitactionManager.doAction(1);
            awaitfirstLoading;
            assert.strictEqual(searchReadCount,1,"thereshouldbe1search_read");
            constsearchInput=actionManager.el.querySelector('.o_searchview_input');

            //'r'keytofilteronbar"FirstRecord"
            awaittestUtils.fields.editInput(searchInput,'record');
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowRight'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});

            assert.strictEqual(actionManager.el.querySelector('.o_searchview_input_container.o_facet_values').innerText.trim(),
                "Firstrecord",
                "theautocompletionfacetshouldbecorrect");
            assert.strictEqual(searchReadCount,2,"thereshouldbe2search_read");

            //'r'keytofilteronbar"SecondRecord"
            awaittestUtils.fields.editInput(searchInput,'record');
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowRight'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});

            assert.strictEqual(actionManager.el.querySelector('.o_searchview_input_container.o_facet_values').innerText.trim(),
                "FirstrecordorSecondrecord",
                "theautocompletionfacetshouldbecorrect");
            assert.strictEqual(searchReadCount,3,"thereshouldbe3search_read");

            actionManager.destroy();
        });

        QUnit.test('nosearchtexttriggersareload',asyncfunction(assert){
            assert.expect(2);

            //Switchtopivottoensurethattheeventcomesfromthecontrolpanel
            //(pivotdoesnothaveahandleron"reload"event).
            this.actions[0].views=[[false,'pivot']];
            this.archs['partner,false,pivot']=`
            <pivot>
                <fieldname="foo"type="row"/>
            </pivot>`;

            letrpcs;
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                mockRPC:function(){
                    rpcs++;
                    returnthis._super.apply(this,arguments);
                },
            });
            awaitactionManager.doAction(1);

            constsearchInput=actionManager.el.querySelector('.o_searchview_input');
            rpcs=0;
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});

            assert.containsNone(actionManager,'.o_searchview_facet_label');
            assert.strictEqual(rpcs,2,"shouldhavereloaded");

            actionManager.destroy();
        });

        QUnit.test('selecting(noresult)triggersare-render',asyncfunction(assert){
            assert.expect(3);

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
            });

            awaitactionManager.doAction(1);

            constsearchInput=actionManager.el.querySelector('.o_searchview_input');

            //'a'keytofilternothingonbar
            awaittestUtils.fields.editInput(searchInput,'hellothere');
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowRight'});
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'ArrowDown'});

            assert.strictEqual(actionManager.el.querySelector('.o_searchview_autocomplete.o_selection_focus').innerText.trim(),"(noresult)",
                "thereshouldbenoresultfor'a'inbar");

            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Enter'});

            assert.containsNone(actionManager,'.o_searchview_facet_label');
            assert.strictEqual(actionManager.el.querySelector('.o_searchview_input').value,"",
                "thesearchinputshouldbere-rendered");

            actionManager.destroy();
        });

        QUnit.test('updatesuggestedfiltersinautocompletemenuwithJapaneseIME',asyncfunction(assert){
            assert.expect(4);

            //ThegoalhereistosimulateasmanyeventshappeningduringanIME
            //assistedcompositionsessionaspossible.Someoftheseeventsare
            //nothandledbutaretriggeredtoensuretheydonotinterfere.
            constTEST="TEST";
            constテスト="テスト";
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
            });
            awaitactionManager.doAction(1);
            constsearchInput=actionManager.el.querySelector('.o_searchview_input');

            //Simulatetyping"TEST"onsearchview.
            for(leti=0;i<TEST.length;i++){
                constkey=TEST[i].toUpperCase();
                awaittestUtils.dom.triggerEvent(searchInput,'keydown',
                    {key,isComposing:true});
                if(i===0){
                    //Compositionisinitiatedafterthefirstkeydown
                    awaittestUtils.dom.triggerEvent(searchInput,'compositionstart');
                }
                awaittestUtils.dom.triggerEvent(searchInput,'keypress',
                    {key,isComposing:true});
                searchInput.value=TEST.slice(0,i+1);
                awaittestUtils.dom.triggerEvent(searchInput,'keyup',
                    {key,isComposing:true});
                awaittestUtils.dom.triggerEvent(searchInput,'input',
                    {inputType:'insertCompositionText',isComposing:true});
            }
            assert.containsOnce(actionManager.el,'.o_searchview_autocomplete',
                "shoulddisplayautocompletedropdownmenuontypingsomethinginsearchview"
            );
            assert.strictEqual(
                actionManager.el.querySelector('.o_searchview_autocompleteli').innerText.trim(),
                "SearchFoofor:TEST",
                `1stfiltersuggestionshouldbebasedontypedword"TEST"`
            );

            //Simulatesoft-selectionofanothersuggestionfromIMEthroughkeyboardnavigation.
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',
                {key:'ArrowDown',isComposing:true});
            awaittestUtils.dom.triggerEvent(searchInput,'keypress',
                {key:'ArrowDown',isComposing:true});
            searchInput.value=テスト;
            awaittestUtils.dom.triggerEvent(searchInput,'keyup',
                {key:'ArrowDown',isComposing:true});
            awaittestUtils.dom.triggerEvent(searchInput,'input',
                {inputType:'insertCompositionText',isComposing:true});

            assert.strictEqual(
                actionManager.el.querySelector('.o_searchview_autocompleteli').innerText.trim(),
                "SearchFoofor:テスト",
                `1stfiltersuggestionshouldbeupdatedwithsoft-selectiontypedword"テスト"`
            );

            //Simulateselectiononsuggestionitem"TEST"fromIME.
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',
                {key:'Enter',isComposing:true});
            awaittestUtils.dom.triggerEvent(searchInput,'keypress',
                {key:'Enter',isComposing:true});
            searchInput.value=TEST;
            awaittestUtils.dom.triggerEvent(searchInput,'keyup',
                {key:'Enter',isComposing:true});
            awaittestUtils.dom.triggerEvent(searchInput,'input',
                {inputType:'insertCompositionText',isComposing:true});

            //Endofthecomposition
            awaittestUtils.dom.triggerEvent(searchInput,'compositionend');

            assert.strictEqual(
                actionManager.el.querySelector('.o_searchview_autocompleteli').innerText.trim(),
                "SearchFoofor:TEST",
                `1stfiltersuggestionshouldfinallybeupdatedwithclickselectiononword"TEST"fromIME`
            );

            actionManager.destroy();
        });

        QUnit.test('opensearchviewautocompleteonpastevalueusingmouse',asyncfunction(assert){
            assert.expect(1);

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
            });

            awaitactionManager.doAction(1);
            //Simulatepastetextthroughthemouse.
            constsearchInput=actionManager.el.querySelector('.o_searchview_input');
            searchInput.value="ABC";
            awaittestUtils.dom.triggerEvent(searchInput,'input',
                {inputType:'insertFromPaste'});
            awaittestUtils.nextTick();
            assert.containsOnce(actionManager,'.o_searchview_autocomplete',
                "shoulddisplayautocompletedropdownmenuonpasteinsearchview");

            actionManager.destroy();
        });

        QUnit.test('selectautocompletedmany2one',asyncfunction(assert){
            assert.expect(5);

            constarchs=Object.assign({},this.archs,{
                'partner,false,search':`
                    <search>
                        <fieldname="foo"/>
                        <fieldname="birthday"/>
                        <fieldname="birth_datetime"/>
                        <fieldname="bar"operator="child_of"/>
                    </search>`,
            });
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs,
                data:this.data,
                asyncmockRPC(route,{domain}){
                    if(route==='/web/dataset/search_read'){
                        assert.step(JSON.stringify(domain));
                    }
                    returnthis._super(...arguments);
                },
            });
            awaitactionManager.doAction(1);

            awaitcpHelpers.editSearch(actionManager,"rec");
            awaittestUtils.dom.click(actionManager.el.querySelector('.o_searchview_autocompleteli:last-child'));

            awaitcpHelpers.removeFacet(actionManager,0);

            awaitcpHelpers.editSearch(actionManager,"rec");
            awaittestUtils.dom.click(actionManager.el.querySelector('.o_expand'));
            awaittestUtils.dom.click(actionManager.el.querySelector('.o_searchview_autocompleteli.o_menu_item.o_indent'));

            assert.verifySteps([
                '[]',
                '[["bar","child_of","rec"]]',//Incompletestring->Namesearch
                '[]',
                '[["bar","child_of",1]]',//Suggestionselect->SpecificID
            ]);

            actionManager.destroy();
        });

        QUnit.test('"null"asautocompletevalue',asyncfunction(assert){
            assert.expect(4);

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                mockRPC(route,args){
                    if(route==='/web/dataset/search_read'){
                        assert.step(JSON.stringify(args.domain));
                    }
                    returnthis._super(...arguments);
                },
            });

            awaitactionManager.doAction(1);

            awaitcpHelpers.editSearch(actionManager,"null");

            assert.strictEqual(actionManager.$('.o_searchview_autocomplete.o_selection_focus').text(),
                "SearchFoofor:null");

            awaittestUtils.dom.click(actionManager.el.querySelector('.o_searchview_autocompleteli.o_selection_focusa'));

            assert.verifySteps([
                JSON.stringify([]),//initialsearch
                JSON.stringify([["foo","ilike","null"]]),
            ]);

            actionManager.destroy();
        });

        QUnit.test('autocompletionwithabooleanfield',asyncfunction(assert){
            assert.expect(9);

            this.archs['partner,false,search']='<search><fieldname="bool"/></search>';

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
                mockRPC(route,args){
                    if(route==='/web/dataset/search_read'){
                        assert.step(JSON.stringify(args.domain));
                    }
                    returnthis._super(...arguments);
                },
            });

            awaitactionManager.doAction(1);

            awaitcpHelpers.editSearch(actionManager,"y");

            assert.containsN(actionManager,'.o_searchview_autocompleteli',2);
            assert.strictEqual(actionManager.$('.o_searchview_autocompleteli:last-child').text(),"Yes");

            //select"Yes"
            awaittestUtils.dom.click(actionManager.el.querySelector('.o_searchview_autocompleteli:last-child'));

            awaitcpHelpers.removeFacet(actionManager,0);

            awaitcpHelpers.editSearch(actionManager,"No");

            assert.containsN(actionManager,'.o_searchview_autocompleteli',2);
            assert.strictEqual(actionManager.$('.o_searchview_autocompleteli:last-child').text(),"No");

            //select"No"
            awaittestUtils.dom.click(actionManager.el.querySelector('.o_searchview_autocompleteli:last-child'));


            assert.verifySteps([
                JSON.stringify([]),//initialsearch
                JSON.stringify([["bool","=",true]]),
                JSON.stringify([]),
                JSON.stringify([["bool","=",false]]),
            ]);

            actionManager.destroy();
        });

        QUnit.test("referencefieldsaresupportedinsearchview",asyncfunction(assert){
            assert.expect(7);

            this.data.partner.fields.ref={type:'reference',string:"Reference"};
            this.data.partner.records.forEach((record,i)=>{
                record.ref=`ref${String(i).padStart(3,"0")}`;
            });
            constarchs=Object.assign({},this.archs,{
                'partner,false,search':`
                    <search>
                        <fieldname="ref"/>
                    </search>`,
            });
            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs,
                data:this.data,
                asyncmockRPC(route,{domain}){
                    if(route==='/web/dataset/search_read'){
                        assert.step(JSON.stringify(domain));
                    }
                    returnthis._super(...arguments);

                }
            });
            awaitactionManager.doAction(1);

            awaitcpHelpers.editSearch(actionManager,"ref");
            awaitcpHelpers.validateSearch(actionManager);

            assert.containsN(actionManager,".o_data_row",5);

            awaitcpHelpers.removeFacet(actionManager,0);
            awaitcpHelpers.editSearch(actionManager,"ref002");
            awaitcpHelpers.validateSearch(actionManager);

            assert.containsOnce(actionManager,".o_data_row");

            assert.verifySteps([
                '[]',
                '[["ref","ilike","ref"]]',
                '[]',
                '[["ref","ilike","ref002"]]',
            ]);

            actionManager.destroy();
        });

        QUnit.test('focusshouldbeonsearchbarwhenswitchingbetweenviews',asyncfunction(assert){
            assert.expect(4);

            this.actions[0].views=[[false,'list'],[false,'form']];
            this.archs['partner,false,form']=`
            <form>
                <group>
                    <fieldname="display_name"/>
                </group>
            </form>`;

            constactionManager=awaitcreateActionManager({
                actions:this.actions,
                archs:this.archs,
                data:this.data,
            });

            awaitactionManager.doAction(1);

            assert.containsOnce(actionManager,'.o_list_view');
            assert.strictEqual(document.activeElement,actionManager.el.querySelector('.o_searchviewinput.o_searchview_input'),
                "searchviewshouldhavefocus");

            awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_cell:first'));
            assert.containsOnce(actionManager,'.o_form_view');
            awaittestUtils.dom.click(actionManager.$('.o_back_button'));
            assert.strictEqual(document.activeElement,actionManager.el.querySelector('.o_searchviewinput.o_searchview_input'),
                "searchviewshouldhavefocus");

            actionManager.destroy();
        });
    });
});
