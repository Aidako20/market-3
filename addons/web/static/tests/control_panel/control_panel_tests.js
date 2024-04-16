flectra.define('web.control_panel_tests',function(require){
    "usestrict";

    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;
    const{createControlPanel}=testUtils;

    QUnit.module('ControlPanel',{
        beforeEach(){
            this.fields={
                display_name:{string:"Displayedname",type:'char',searchable:true},
                foo:{string:"Foo",type:"char",default:"MylittleFooValue",store:true,sortable:true,searchable:true},
                date_field:{string:"Date",type:"date",store:true,sortable:true,searchable:true},
                float_field:{string:"Float",type:"float",searchable:true},
                bar:{string:"Bar",type:"many2one",relation:'partner',searchable:true},
            };
        }
    },function(){

        QUnit.test('defaultfieldoperator',asyncfunction(assert){
            assert.expect(2);

            constfields={
                foo_op:{string:"FooOp",type:"char",store:true,sortable:true,searchable:true},
                foo:{string:"Foo",type:"char",store:true,sortable:true,searchable:true},
                bar_op:{string:"BarOp",type:"many2one",relation:'partner',searchable:true},
                bar:{string:"Bar",type:"many2one",relation:'partner',searchable:true},
                selec:{string:"Selec",type:"selection",selection:[['red',"Red"],['black',"Black"]]},
            };
            constarch=`
                <search>
                    <fieldname="bar"/>
                    <fieldname="bar_op"operator="child_of"/>
                    <fieldname="foo"/>
                    <fieldname="foo_op"operator="="/>
                    <fieldname="selec"/>
                </search>`;
            constsearchMenuTypes=[];
            constparams={
                cpModelConfig:{
                    arch,
                    fields,
                    context:{
                        show_filterC:true,
                        search_default_bar:10,
                        search_default_bar_op:10,
                        search_default_foo:"foo",
                        search_default_foo_op:"foo_op",
                        search_default_selec:'red',
                    },
                    searchMenuTypes,
                },
                cpProps:{fields,searchMenuTypes},
                env:{
                    session:{
                        asyncrpc(){
                            return[[10,"DecoAddict"]];
                        },
                    },
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.deepEqual(
                cpHelpers.getFacetTexts(controlPanel).map(t=>t.replace(/\s/g,"")),
                [
                    "BarDecoAddict",
                    "BarOpDecoAddict",
                    "Foofoo",
                    "FooOpfoo_op",
                    "SelecRed"
                ]
            );
            assert.deepEqual(
                controlPanel.getQuery().domain,
                [
                    "&","&","&","&",
                    ["bar","=",10],
                    ["bar_op","child_of",10],
                    ["foo","ilike","foo"],
                    ["foo_op","=","foo_op"],
                    ["selec","=","red"],
                ]
            );

            controlPanel.destroy();
        });

        QUnit.module('Keyboardnavigation');

        QUnit.test('removeafacetwithbackspace',asyncfunction(assert){
            assert.expect(2);

            constparams={
                cpModelConfig:{
                    arch:`<search><fieldname="foo"/></search>`,
                    fields:this.fields,
                    context:{search_default_foo:"a"},
                    searchMenuTypes:['filter'],
                },
                cpProps:{fields:this.fields},
            };

            constcontrolPanel=awaitcreateControlPanel(params);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Foo\na']);

            //deleteafacet
            constsearchInput=controlPanel.el.querySelector('input.o_searchview_input');
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Backspace'});

            assert.containsNone(controlPanel,'div.o_searchviewdiv.o_searchview_facet');

            //deletenothing(shouldnotcrash)
            awaittestUtils.dom.triggerEvent(searchInput,'keydown',{key:'Backspace'});

            controlPanel.destroy();
        });

        QUnit.test('fieldsandfilterswithgroups/invisibleattribute',asyncfunction(assert){
            //navigationandautomaticmenuclosuredon'tworkhere(idon'tknowwhyyet)-->
            //shouldbetestedseparatly
            assert.expect(16);

            constarch=`
                <search>
                    <fieldname="display_name"string="FooB"invisible="1"/>
                    <fieldname="foo"string="FooA"/>
                    <filtername="filterA"string="FA"domain="[]"/>
                    <filtername="filterB"string="FB"invisible="1"domain="[]"/>
                    <filtername="filterC"string="FC"invisible="notcontext.get('show_filterC')"domain="[]"/>
                    <filtername="groupByA"string="GA"context="{'group_by':'date_field:day'}"/>
                    <filtername="groupByB"string="GB"context="{'group_by':'date_field:day'}"invisible="1"/>
                </search>`;
            constsearchMenuTypes=['filter','groupBy'];
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    context:{
                        show_filterC:true,
                        search_default_display_name:'value',
                        search_default_filterB:true,
                        search_default_groupByB:true
                    },
                    searchMenuTypes
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            functionselectorContainsValue(selector,value,shouldContain){
                constelements=[...controlPanel.el.querySelectorAll(selector)];
                constregExp=newRegExp(value);
                constmatches=elements.filter(el=>regExp.test(el.innerText.replace(/\s/g,"")));
                assert.strictEqual(matches.length,shouldContain?1:0,
                    `${selector}inthecontrolpanelshould${shouldContain?'':'not'}contain"${value}".`
                );
            }

            //defaultfilters/fieldsshouldbeactivatedevenifinvisible
            assert.containsN(controlPanel,'div.o_searchview_facet',3);
            selectorContainsValue('.o_searchview_facet',"FooBvalue",true);
            selectorContainsValue('.o_searchview_facet.o_facet_values',"FB",true);
            selectorContainsValue('.o_searchview_facet.o_facet_values',"GB",true);

            awaitcpHelpers.toggleFilterMenu(controlPanel);

            selectorContainsValue('.o_menu_itema',"FA",true);
            selectorContainsValue('.o_menu_itema',"FB",false);
            selectorContainsValue('.o_menu_itema',"FC",true);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);

            selectorContainsValue('.o_menu_itema',"GA",true);
            selectorContainsValue('.o_menu_itema',"GB",false);

            //'a'tofilternothingonbar
            awaitcpHelpers.editSearch(controlPanel,'a');

            //theonlyiteminautocompletemenushouldbeFooA:a
            selectorContainsValue('.o_searchview_autocomplete',"SearchFooAfor:a",true);
            awaitcpHelpers.validateSearch(controlPanel);
            selectorContainsValue('.o_searchview_facet',"FooAa",true);

            //TheitemsintheFiltersmenuandtheGroupBymenushouldbethesameasbefore
            awaitcpHelpers.toggleFilterMenu(controlPanel);

            selectorContainsValue('.o_menu_itema',"FA",true);
            selectorContainsValue('.o_menu_itema',"FB",false);
            selectorContainsValue('.o_menu_itema',"FC",true);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);

            selectorContainsValue('.o_menu_itema',"GA",true);
            selectorContainsValue('.o_menu_itema',"GB",false);

            controlPanel.destroy();
        });

        QUnit.test('invisiblefieldsandfilterswithunknownrelatedfieldsshouldnotberendered',asyncfunction(assert){
            assert.expect(2);

            //Thistestcaseconsidersthatthecurrentuserisnotamemberof
            //the"base.group_system"groupandboth"bar"and"date_field"fields
            //havefield-levelaccesscontrolthatlimitaccesstothemonlyfrom
            //thatgroup.
            //
            //AsMockServercurrentlydoesnotsupport"groups"accesscontrol,we:
            //
            //-emulatefield-levelaccesscontroloffields_get()byremoving
            //  "bar"and"date_field"fromthemodelfields
            //-setfilterswithgroups="base.group_system"as`invisible=1`in
            //  viewtoemulatethebehavioroffields_view_get()
            //  [seeir.ui.view`_apply_group()`]

            deletethis.fields.bar;
            deletethis.fields.date_field;

            constsearchMenuTypes=[];
            constparams={
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.containsNone(controlPanel.el,'div.o_search_optionsdiv.o_filter_menu',
                "thereshouldnotbefilterdropdown");
            assert.containsNone(controlPanel.el,'div.o_search_optionsdiv.o_group_by_menu',
                "thereshouldnotbegroupbydropdown");

            controlPanel.destroy();
        });

        QUnit.test('groupbymenuisnotrenderedifsearchMenuTypesdoesnothavegroupBy',asyncfunction(assert){
            assert.expect(2);

            constarch=`<search/>`;
            constsearchMenuTypes=['filter'];
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.containsOnce(controlPanel.el,'div.o_search_optionsdiv.o_filter_menu');
            assert.containsNone(controlPanel.el,'div.o_search_optionsdiv.o_group_by_menu');

            controlPanel.destroy();
        });

        QUnit.test('searchfieldshouldbeautofocused',asyncfunction(assert){
            assert.expect(2);
    
            constcontrolPanel=awaitcreateControlPanel({
                model:'partner',
                arch:'<search/>',
                data:this.data,
                env:{
                    device:{
                        isMobileDevice:false,
                    },
                },
            });
    
            assert.containsOnce(controlPanel,'.o_searchview_input',"hasasearchfield");
            assert.containsOnce(controlPanel,'.o_searchview_input:focus-within',
                "hasautofocusedsearchfield");
    
            controlPanel.destroy();
        });
    
        QUnit.test("searchfield'sautofocusshouldbedisabledonmobiledevice",asyncfunction(assert){
            assert.expect(2);
    
            constcontrolPanel=awaitcreateControlPanel({
                model:'partner',
                arch:'<search/>',
                data:this.data,
                env:{
                    device:{
                        isMobileDevice:true,
                    },
                },
            });
    
            assert.containsOnce(controlPanel,'.o_searchview_input',"hasasearchfield");
            assert.containsNone(controlPanel,'.o_searchview_input:focus-within',
                "hasn'tautofocusedsearchfield");
    
            controlPanel.destroy();
        });

    });
});
