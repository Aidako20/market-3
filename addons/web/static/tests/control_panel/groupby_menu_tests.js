flectra.define('web.groupby_menu_tests',function(require){
    "usestrict";

    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;
    const{createControlPanel}=testUtils;

    constsearchMenuTypes=['groupBy'];

    QUnit.module('Components',{
        beforeEach:function(){
            this.fields={
                bar:{string:"Bar",type:"many2one",relation:'partner'},
                birthday:{string:"Birthday",type:"date",store:true,sortable:true},
                date_field:{string:"Date",type:"date",store:true,sortable:true},
                float_field:{string:"Float",type:"float",group_operator:'sum'},
                foo:{string:"Foo",type:"char",store:true,sortable:true},
            };
        },
    },function(){

        QUnit.module('GroupByMenu');

        QUnit.test('simplerenderingwithneithergroupbysnorgroupablefields',asyncfunction(assert){

            assert.expect(1);
            constparams={
                cpModelConfig:{searchMenuTypes},
                cpProps:{fields:{},searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.containsNone(controlPanel,'.o_menu_item,.dropdown-divider,div.o_generator_menu');

            controlPanel.destroy();
        });

        QUnit.test('simplerenderingwithnogroupby',asyncfunction(assert){
            assert.expect(5);

            constparams={
                cpModelConfig:{searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            assert.containsNone(controlPanel,'.o_menu_item,.dropdown-divider');
            assert.containsOnce(controlPanel,'div.o_generator_menu');

            awaitcpHelpers.toggleAddCustomGroup(controlPanel);

            constoptionEls=controlPanel.el.querySelectorAll('div.o_generator_menuselect.o_group_by_selectoroption');
            assert.strictEqual(optionEls[0].innerText.trim(),'Birthday');
            assert.strictEqual(optionEls[1].innerText.trim(),'Date');
            assert.strictEqual(optionEls[2].innerText.trim(),'Foo');

            controlPanel.destroy();
        });

        QUnit.test('simplerenderingwithasinglegroupby',asyncfunction(assert){
            assert.expect(4);

            constarch=`
                <search>
                    <filterstring="GroupbyFoo"name="gb_foo"context="{'group_by':'foo'}"/>
                </search>`;
            constparams={
                cpModelConfig:{arch,fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            assert.containsOnce(controlPanel,'.o_menu_item');
            assert.strictEqual(controlPanel.el.querySelector('.o_menu_item').innerText.trim(),"GroupbyFoo");
            assert.containsOnce(controlPanel,'.dropdown-divider');
            assert.containsOnce(controlPanel,'div.o_generator_menu');

            controlPanel.destroy();
        });

        QUnit.test('togglea"simple"groupbyingroupbymenuworks',asyncfunction(assert){
            assert.expect(9);

            constgroupBys=[['foo'],[]];
            constarch=`
                <search>
                    <filterstring="GroupbyFoo"name="gb_foo"context="{'group_by':'foo'}"/>
                </search>`;
            constparams={
                cpModelConfig:{arch,fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
                search:function(searchQuery){
                    const{groupBy}=searchQuery;
                    assert.deepEqual(groupBy,groupBys.shift());
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            assert.notOk(cpHelpers.isItemSelected(controlPanel,0));

            awaitcpHelpers.toggleMenuItem(controlPanel,0);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['GroupbyFoo']);
            assert.containsOnce(controlPanel.el.querySelector('.o_searchview.o_searchview_facet'),
                'span.fa.fa-bars.o_searchview_facet_label');
            assert.ok(cpHelpers.isItemSelected(controlPanel,0));

            awaitcpHelpers.toggleMenuItem(controlPanel,0);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);
            assert.notOk(cpHelpers.isItemSelected(controlPanel,0));

            controlPanel.destroy();
        });

        QUnit.test('togglea"simple"groupbyquicklydoesnotcrash',asyncfunction(assert){
            assert.expect(1);

            constarch=`
                <search>
                    <filterstring="GroupbyFoo"name="gb_foo"context="{'group_by':'foo'}"/>
                </search>`;
            constparams={
                cpModelConfig:{arch,fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);

            cpHelpers.toggleMenuItem(controlPanel,0);
            cpHelpers.toggleMenuItem(controlPanel,0);

            assert.ok(true);
            controlPanel.destroy();
        });

        QUnit.test('removea"GroupBy"facetproperlyunchecksgroupbysingroupbymenu',asyncfunction(assert){
            assert.expect(5);

            constarch=`
                <search>
                    <filterstring="GroupbyFoo"name="gb_foo"context="{'group_by':'foo'}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_gb_foo:1}
                },
                cpProps:{fields:this.fields,searchMenuTypes},
                search:function(searchQuery){
                    const{groupBy}=searchQuery;
                    assert.deepEqual(groupBy,[]);
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            constfacetEl=controlPanel.el.querySelector('.o_searchview.o_searchview_facet');
            assert.strictEqual(facetEl.innerText.trim(),"GroupbyFoo");
            assert.ok(cpHelpers.isItemSelected(controlPanel,0));

            awaittestUtils.dom.click(facetEl.querySelector('i.o_facet_remove'));
            assert.containsNone(controlPanel,'.o_searchview.o_searchview_facet');
            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            assert.notOk(cpHelpers.isItemSelected(controlPanel,0));

            controlPanel.destroy();
        });

        QUnit.test('groupbyadatefieldusingintervalworks',asyncfunction(assert){
            assert.expect(21);

            constgroupBys=[
                ['date_field:year','date_field:week'],
                ['date_field:year','date_field:month','date_field:week'],
                ['date_field:year','date_field:month'],
                ['date_field:year'],
                []
            ];

            constarch=`
                <search>
                    <filterstring="Date"name="date"context="{'group_by':'date_field:week'}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_date:1}
                },
                cpProps:{fields:this.fields,searchMenuTypes},
                search:function(searchQuery){
                    const{groupBy}=searchQuery;
                    assert.deepEqual(groupBy,groupBys.shift());
                },
            };

            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);

            constoptionEls=controlPanel.el.querySelectorAll('ul.o_menu_item_options>li.o_item_option>a');

            //defaultgroupbyshouldbeactivatedwiththe defaultinteval'week'
            const{groupBy}=controlPanel.getQuery();
            assert.deepEqual(groupBy,['date_field:week']);

            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,3));

            //checkoptiondescriptions
            constoptionDescriptions=[...optionEls].map(e=>e.innerText.trim());
            constexpectedDescriptions=['Year','Quarter','Month','Week','Day'];
            assert.deepEqual(optionDescriptions,expectedDescriptions);

            conststeps=[
                {description:'Year',facetContent:'Date:Year>Date:Week',selectedoptions:[0,3]},
                {description:'Month',facetContent:'Date:Year>Date:Month>Date:Week',selectedoptions:[0,2,3]},
                {description:'Week',facetContent:'Date:Year>Date:Month',selectedoptions:[0,2]},
                {description:'Month',facetContent:'Date:Year',selectedoptions:[0]},
                {description:'Year',selectedoptions:[]},
            ];
            for(constsofsteps){
                constindex=expectedDescriptions.indexOf(s.description);
                awaitcpHelpers.toggleMenuItemOption(controlPanel,0,index);
                if(s.facetContent){
                    assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[s.facetContent]);
                }else{
                    assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);
                }
                s.selectedoptions.forEach(index=>{
                    assert.ok(cpHelpers.isOptionSelected(controlPanel,0,index));
                });
            }
            controlPanel.destroy();
        });

        QUnit.test('intervaloptionsarecorrectlygroupedandordered',asyncfunction(assert){
            assert.expect(8);

            constarch=`
                <search>
                    <filterstring="Bar"name="bar"context="{'group_by':'bar'}"/>
                    <filterstring="Date"name="date"context="{'group_by':'date_field'}"/>
                    <filterstring="Foo"name="foo"context="{'group_by':'foo'}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_bar:1}
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };

            constcontrolPanel=awaitcreateControlPanel(params);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Bar']);

            //openmenu'GroupBy'
            awaitcpHelpers.toggleGroupByMenu(controlPanel);

            //Openthegroupby'Date'
            awaitcpHelpers.toggleMenuItem(controlPanel,'Date');
            //selectoption'week'
            awaitcpHelpers.toggleMenuItemOption(controlPanel,'Date','Week');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Bar>Date:Week']);

            //selectoption'day'
            awaitcpHelpers.toggleMenuItemOption(controlPanel,'Date','Day');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Bar>Date:Week>Date:Day']);

            //selectoption'year'
            awaitcpHelpers.toggleMenuItemOption(controlPanel,'Date','Year');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Bar>Date:Year>Date:Week>Date:Day']);

            //select'Foo'
            awaitcpHelpers.toggleMenuItem(controlPanel,'Foo');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Bar>Date:Year>Date:Week>Date:Day>Foo']);

            //selectoption'quarter'
            awaitcpHelpers.toggleMenuItem(controlPanel,'Date');
            awaitcpHelpers.toggleMenuItemOption(controlPanel,'Date','Quarter');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Bar>Date:Year>Date:Quarter>Date:Week>Date:Day>Foo']);

            //unselect'Bar'
            awaitcpHelpers.toggleMenuItem(controlPanel,'Bar');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Year>Date:Quarter>Date:Week>Date:Day>Foo']);

            //unselectoption'week'
            awaitcpHelpers.toggleMenuItem(controlPanel,'Date');
            awaitcpHelpers.toggleMenuItemOption(controlPanel,'Date','Week');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Year>Date:Quarter>Date:Day>Foo']);

            controlPanel.destroy();
        });

        QUnit.test('theIDfieldshouldnotbeproposedin"AddCustomGroup"menu',asyncfunction(assert){
            assert.expect(2);

            constfields={
                foo:{string:"Foo",type:"char",store:true,sortable:true},
                id:{sortable:true,string:'ID',type:'integer'}
            };
            constparams={
                cpModelConfig:{searchMenuTypes},
                cpProps:{fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            awaitcpHelpers.toggleAddCustomGroup(controlPanel);

            constoptionEls=controlPanel.el.querySelectorAll('div.o_generator_menuselect.o_group_by_selectoroption');
            assert.strictEqual(optionEls.length,1);
            assert.strictEqual(optionEls[0].innerText.trim(),"Foo");

            controlPanel.destroy();
        });

        QUnit.test('addadatefieldin"AddCustomeGroup"activateagroupbywithglobaldefaultoption"month"',asyncfunction(assert){
            assert.expect(4);

            constfields={
                date_field:{string:"Date",type:"date",store:true,sortable:true},
                id:{sortable:true,string:'ID',type:'integer'}
            };
            constparams={
                cpModelConfig:{fields,searchMenuTypes},
                cpProps:{fields,searchMenuTypes},
                search:function(searchQuery){
                    const{groupBy}=searchQuery;
                    assert.deepEqual(groupBy,['date_field:month']);
                }
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            awaitcpHelpers.toggleAddCustomGroup(controlPanel);
            awaitcpHelpers.applyGroup(controlPanel);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Month']);

            assert.ok(cpHelpers.isItemSelected(controlPanel,"Date"));
            awaitcpHelpers.toggleMenuItem(controlPanel,"Date");
            assert.ok(cpHelpers.isOptionSelected(controlPanel,"Date","Month"));

            controlPanel.destroy();
        });

        QUnit.test('defaultgroupbyscanbeordered',asyncfunction(assert){
            assert.expect(2);

            constarch=`
                <search>
                    <filterstring="Birthday"name="birthday"context="{'group_by':'birthday'}"/>
                    <filterstring="Date"name="date"context="{'group_by':'date_field:week'}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_birthday:2,search_default_date:1}
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };

            constcontrolPanel=awaitcreateControlPanel(params);

            //thedefautlgroupbysshouldbeactivatedintherightorder
            const{groupBy}=controlPanel.getQuery();
            assert.deepEqual(groupBy,['date_field:week','birthday:month']);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Week>Birthday:Month']);

            controlPanel.destroy();
        });

        QUnit.test('aseparatoringroupbysdoesnotcauseproblems',asyncfunction(assert){
            assert.expect(23);

            constarch=`
                <search>
                    <filterstring="Date"name="coolName"context="{'group_by':'date_field'}"/>
                    <separator/>
                    <filterstring="Bar"name="superName"context="{'group_by':'bar'}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };

            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);
            awaitcpHelpers.toggleMenuItemOption(controlPanel,0,4);

            assert.ok(cpHelpers.isItemSelected(controlPanel,0));
            assert.notOk(cpHelpers.isItemSelected(controlPanel,1));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,4),'selected');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Day']);

            awaitcpHelpers.toggleMenuItem(controlPanel,1);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);
            assert.ok(cpHelpers.isItemSelected(controlPanel,0));
            assert.ok(cpHelpers.isItemSelected(controlPanel,1));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,4),'selected');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Day>Bar']);

            awaitcpHelpers.toggleMenuItemOption(controlPanel,0,1);
            assert.ok(cpHelpers.isItemSelected(controlPanel,0));
            assert.ok(cpHelpers.isItemSelected(controlPanel,1));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,1),'selected');
            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,4),'selected');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Quarter>Date:Day>Bar']);

            awaitcpHelpers.toggleMenuItem(controlPanel,1);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);
            assert.ok(cpHelpers.isItemSelected(controlPanel,0));
            assert.notOk(cpHelpers.isItemSelected(controlPanel,1));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,1),'selected');
            assert.ok(cpHelpers.isOptionSelected(controlPanel,0,4),'selected');
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Date:Quarter>Date:Day']);

            awaitcpHelpers.removeFacet(controlPanel);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            awaitcpHelpers.toggleGroupByMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);
            assert.notOk(cpHelpers.isItemSelected(controlPanel,0));
            assert.notOk(cpHelpers.isItemSelected(controlPanel,1));
            assert.notOk(cpHelpers.isOptionSelected(controlPanel,0,1),'selected');
            assert.notOk(cpHelpers.isOptionSelected(controlPanel,0,4),'selected');

            controlPanel.destroy();
        });

        QUnit.test('falsysearchdefaultgroupbysarenotactivated',asyncfunction(assert){
            assert.expect(2);

            constarch=`
                <search>
                    <filterstring="Birthday"name="birthday"context="{'group_by':'birthday'}"/>
                    <filterstring="Date"name="date"context="{'group_by':'foo'}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_birthday:false,search_default_foo:0}
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };

            constcontrolPanel=awaitcreateControlPanel(params);
            const{groupBy}=controlPanel.getQuery();
            assert.deepEqual(groupBy,[]);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            controlPanel.destroy();
        });
    });
});
