flectra.define('web.filter_menu_tests',function(require){
    "usestrict";

    consttestUtils=require('web.test_utils');

    const{controlPanel:cpHelpers,createControlPanel,mock}=testUtils;
    const{patchDate}=mock;

    constsearchMenuTypes=['filter'];

    QUnit.module('Components',{
        beforeEach:function(){
            this.fields={
                date_field:{string:"Date",type:"date",store:true,sortable:true,searchable:true},
                foo:{string:"Foo",type:"char",store:true,sortable:true},
            };
        },
    },function(){

        QUnit.module('FilterMenu');

        QUnit.test('simplerenderingwithnofilter',asyncfunction(assert){
            assert.expect(2);

            constparams={
                cpModelConfig:{searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            assert.containsNone(controlPanel,'.o_menu_item,.dropdown-divider');
            assert.containsOnce(controlPanel,'div.o_generator_menu');

            controlPanel.destroy();
        });

        QUnit.test('simplerenderingwithasinglefilter',asyncfunction(assert){
            assert.expect(3);

            constarch=`
                <search>
                    <filterstring="Foo"name="foo"domain="[]"/>
                </search>`;
            constparams={
                cpModelConfig:{arch,fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            assert.containsOnce(controlPanel,'.o_menu_item');
            assert.containsOnce(controlPanel,'.dropdown-divider');
            assert.containsOnce(controlPanel,'div.o_generator_menu');

            controlPanel.destroy();
        });

        QUnit.test('shouldhaveDateandIDfieldproposedinthatorderin"AddcustomFilter"submenu',asyncfunction(assert){
            assert.expect(2);

            constparams={
                cpModelConfig:{fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleAddCustomFilter(controlPanel);
            constoptionEls=controlPanel.el.querySelectorAll('div.o_filter_condition>select.o_generator_menu_fieldoption');
            assert.strictEqual(optionEls[0].innerText.trim(),'Date');
            assert.strictEqual(optionEls[1].innerText.trim(),'ID');

            controlPanel.destroy();
        });

        QUnit.test('togglea"simple"filterinfiltermenuworks',asyncfunction(assert){
            assert.expect(9);

            constdomains=[
                [['foo','=','qsdf']],
                []
            ];
            constarch=`
                <search>
                    <filterstring="Foo"name="foo"domain="[['foo','=','qsdf']]"/>
                </search>`;
            constparams={
                cpModelConfig:{arch,searchMenuTypes},
                cpProps:{fields:{},searchMenuTypes},
                search:function(searchQuery){
                    const{domain}=searchQuery;
                    assert.deepEqual(domain,domains.shift());
                }
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            assert.notOk(cpHelpers.isItemSelected(controlPanel,0));
            awaitcpHelpers.toggleMenuItem(controlPanel,"Foo");

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Foo']);
            assert.containsOnce(controlPanel.el.querySelector('.o_searchview.o_searchview_facet'),
                'span.fa.fa-filter.o_searchview_facet_label');

            assert.ok(cpHelpers.isItemSelected(controlPanel,"Foo"));

            awaitcpHelpers.toggleMenuItem(controlPanel,"Foo");
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);
            assert.notOk(cpHelpers.isItemSelected(controlPanel,"Foo"));

            controlPanel.destroy();
        });

        QUnit.test('addacustomfilterworks',asyncfunction(assert){
            assert.expect(1);

            constparams={
                cpModelConfig:{fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleAddCustomFilter(controlPanel);
            //chooseIDfieldin'AddCustomefilter'menuandvalue1
            awaittestUtils.fields.editSelect(
                controlPanel.el.querySelector('div.o_filter_condition>select.o_generator_menu_field'),'id');
            awaittestUtils.fields.editInput(
                controlPanel.el.querySelector('div.o_filter_condition>span.o_generator_menu_value>input'),1);

            awaitcpHelpers.applyFilter(controlPanel);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['IDis"1"']);

            controlPanel.destroy();
        });

        QUnit.test('deactivateanewcustomfilterworks',asyncfunction(assert){
            assert.expect(4);

            constunpatchDate=patchDate(2020,1,5,12,20,0);

            constparams={
                cpModelConfig:{fields:this.fields,searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleAddCustomFilter(controlPanel);
            awaitcpHelpers.applyFilter(controlPanel);

            assert.ok(cpHelpers.isItemSelected(controlPanel,'Dateisequalto"02/05/2020"'));
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Dateisequalto"02/05/2020"']);

            awaitcpHelpers.toggleMenuItem(controlPanel,'Dateisequalto"02/05/2020"');

            assert.notOk(cpHelpers.isItemSelected(controlPanel,'Dateisequalto"02/05/2020"'));
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('filterbyadatefieldusingperiodworks',asyncfunction(assert){
            assert.expect(56);

            constunpatchDate=patchDate(2017,2,22,1,0,0);

            constbasicDomains=[
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]],
                ["&",["date_field",">=","2017-02-01"],["date_field","<=","2017-02-28"]],
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]],
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-01-31"]],
                ["|",
                    "&",["date_field",">=","2017-01-01"],["date_field","<=","2017-01-31"],
                    "&",["date_field",">=","2017-10-01"],["date_field","<=","2017-12-31"]
                ],
                ["&",["date_field",">=","2017-10-01"],["date_field","<=","2017-12-31"]],
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]],
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-03-31"]],
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]],
                ["&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]],
                ["|",
                    "&",["date_field",">=","2016-01-01"],["date_field","<=","2016-12-31"],
                    "&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]
                ],
                ["|",
                    "|",
                        "&",["date_field",">=","2015-01-01"],["date_field","<=","2015-12-31"],
                        "&",["date_field",">=","2016-01-01"],["date_field","<=","2016-12-31"],
                        "&",["date_field",">=","2017-01-01"],["date_field","<=","2017-12-31"]
                ],
                ["|",
                    "|",
                        "&",["date_field",">=","2015-03-01"],["date_field","<=","2015-03-31"],
                        "&",["date_field",">=","2016-03-01"],["date_field","<=","2016-03-31"],
                        "&",["date_field",">=","2017-03-01"],["date_field","<=","2017-03-31"]
                ]
            ];

            constarch=`
                <search>
                    <filterstring="Date"name="date_field"date="date_field"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_date_field:1},
                },
                cpProps:{fields:this.fields,searchMenuTypes},
                search:function(searchQuery){
                    //weinspectquerydomain
                    const{domain}=searchQuery;
                    if(domain.length){
                        assert.deepEqual(domain,basicDomains.shift());
                    }
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Date");

            constoptionEls=controlPanel.el.querySelectorAll('ul.o_menu_item_options>li.o_item_option>a');

            //defaultfiltershouldbeactivatedwiththeglobaldefaultperiod'this_month'
            const{domain}=controlPanel.getQuery();
            assert.deepEqual(
                domain,
                ["&",["date_field",">=","2017-03-01"],["date_field","<=","2017-03-31"]]
            );
            assert.ok(cpHelpers.isItemSelected(controlPanel,"Date"));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,"Date",0));

            //checkoptiondescriptions
            constoptionDescriptions=[...optionEls].map(e=>e.innerText.trim());
            constexpectedDescriptions=[
                'March','February','January',
                'Q4','Q3','Q2','Q1',
                '2017','2016','2015'
            ];
            assert.deepEqual(optionDescriptions,expectedDescriptions);

            //checkgenerateddomains
            conststeps=[
                {description:'March',facetContent:'Date:2017',selectedoptions:[7]},
                {description:'February',facetContent:'Date:February2017',selectedoptions:[1,7]},
                {description:'February',facetContent:'Date:2017',selectedoptions:[7]},
                {description:'January',facetContent:'Date:January2017',selectedoptions:[2,7]},
                {description:'Q4',facetContent:'Date:January2017/Q42017',selectedoptions:[2,3,7]},
                {description:'January',facetContent:'Date:Q42017',selectedoptions:[3,7]},
                {description:'Q4',facetContent:'Date:2017',selectedoptions:[7]},
                {description:'Q1',facetContent:'Date:Q12017',selectedoptions:[6,7]},
                {description:'Q1',facetContent:'Date:2017',selectedoptions:[7]},
                {description:'2017',selectedoptions:[]},
                {description:'2017',facetContent:'Date:2017',selectedoptions:[7]},
                {description:'2016',facetContent:'Date:2016/2017',selectedoptions:[7,8]},
                {description:'2015',facetContent:'Date:2015/2016/2017',selectedoptions:[7,8,9]},
                {description:'March',facetContent:'Date:March2015/March2016/March2017',selectedoptions:[0,7,8,9]}
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
                    assert.ok(cpHelpers.isOptionSelected(controlPanel,0,index),
                        `atstep${steps.indexOf(s)+1},option${expectedDescriptions[index]}shouldbeselected`);
                });
            }

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('filterbyadatefieldusingperiodworkseveninJanuary',asyncfunction(assert){
            assert.expect(5);

            constunpatchDate=patchDate(2017,0,7,3,0,0);

            constarch=`
                <search>
                    <filterstring="Date"name="some_filter"date="date_field"default_period="last_month"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{search_default_some_filter:1},
                },
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            const{domain}=controlPanel.getQuery();
            assert.deepEqual(domain,[
                '&',
                ["date_field",">=","2016-12-01"],
                ["date_field","<=","2016-12-31"]
            ]);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),["Date:December2016"]);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Date");

            assert.ok(cpHelpers.isItemSelected(controlPanel,"Date"));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,"Date",'December'));
            assert.ok(cpHelpers.isOptionSelected(controlPanel,"Date",'2016'));

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('`context`keyin<filter>isused',asyncfunction(assert){
            assert.expect(1);

            constarch=`
                <search>
                    <filterstring="Filter"name="some_filter"domain="[]"context="{'coucou_1':1}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes
                },
                cpProps:{fields:this.fields,searchMenuTypes},
                search:function(searchQuery){
                    //weinspectquerycontext
                    const{context}=searchQuery;
                    assert.deepEqual(context,{coucou_1:1});
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);

            controlPanel.destroy();
        });

        QUnit.test('FilterwithJSON-parsabledomainworks',asyncfunction(assert){
            assert.expect(1);

            constoriginalDomain=[['foo','=','GentlyWeeps']];
            constxml_domain=JSON.stringify(originalDomain);

            constarch=
                `<search>
                    <filterstring="Foo"name="gently_weeps"domain="${_.escape(xml_domain)}"/>
                </search>`;
            constparams={
                cpModelConfig:{
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                },
                cpProps:{fields:this.fields,searchMenuTypes},
                search:function(searchQuery){
                    const{domain}=searchQuery;
                    assert.deepEqual(domain,originalDomain,
                        'AJSONparsablexmldomainshouldbehandledjustlikeanyother'
                    );
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);

            controlPanel.destroy();
        });

        QUnit.test('filterwithdateattributesetassearch_default',asyncfunction(assert){
            assert.expect(1);

            constunpatchDate=patchDate(2019,6,31,13,43,0);

            constarch=
                `<search>
                    <filterstring="Date"name="date_field"date="date_field"default_period="last_month"/>
                </search>`,
                params={
                    cpModelConfig:{
                        arch,
                        fields:this.fields,
                        searchMenuTypes,
                        context:{
                            search_default_date_field:true
                        }
                    },
                    cpProps:{fields:this.fields,searchMenuTypes},
                };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),["Date:June2019"]);

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('filterdomainsarecorreclycombinedbyORandAND',asyncfunction(assert){
            assert.expect(2);

            constarch=
                `<search>
                    <filterstring="FilterGroup1"name="f_1_g1"domain="[['foo','=','f1_g1']]"/>
                    <separator/>
                    <filterstring="Filter1Group2"name="f1_g2"domain="[['foo','=','f1_g2']]"/>
                    <filterstring="Filter2GROUP2"name="f2_g2"domain="[['foo','=','f2_g2']]"/>
                </search>`,
                params={
                    cpModelConfig:{
                        arch,
                        fields:this.fields,
                        searchMenuTypes,
                        context:{
                            search_default_f_1_g1:true,
                            search_default_f1_g2:true,
                            search_default_f2_g2:true,
                        }
                    },
                    cpProps:{fields:this.fields,searchMenuTypes},
                };
            constcontrolPanel=awaitcreateControlPanel(params);

            const{domain}=controlPanel.getQuery();
            assert.deepEqual(domain,[
                '&',
                ['foo','=','f1_g1'],
                '|',
                ['foo','=','f1_g2'],
                ['foo','=','f2_g2']
            ]);

            assert.deepEqual(
                cpHelpers.getFacetTexts(controlPanel),
                ["FilterGroup1","Filter1Group2orFilter2GROUP2"]
            );

            controlPanel.destroy();
        });

        QUnit.test('archorderofgroupsoffilterspreserved',asyncfunction(assert){
            assert.expect(12);

            constarch=
                `<search>
                    <filterstring="1"name="coolName1"date="date_field"/>
                    <separator/>
                    <filterstring="2"name="coolName2"date="date_field"/>
                    <separator/>
                    <filterstring="3"name="coolName3"domain="[]"/>
                    <separator/>
                    <filterstring="4"name="coolName4"domain="[]"/>
                    <separator/>
                    <filterstring="5"name="coolName5"domain="[]"/>
                    <separator/>
                    <filterstring="6"name="coolName6"domain="[]"/>
                    <separator/>
                    <filterstring="7"name="coolName7"domain="[]"/>
                    <separator/>
                    <filterstring="8"name="coolName8"domain="[]"/>
                    <separator/>
                    <filterstring="9"name="coolName9"domain="[]"/>
                    <separator/>
                    <filterstring="10"name="coolName10"domain="[]"/>
                    <separator/>
                    <filterstring="11"name="coolName11"domain="[]"/>
                </search>`,
                params={
                    cpModelConfig:{
                        arch,
                        fields:this.fields,
                        searchMenuTypes,
                    },
                    cpProps:{fields:this.fields,searchMenuTypes},
                };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            assert.containsN(controlPanel,'.o_filter_menu.o_menu_item',11);

            constmenuItemEls=controlPanel.el.querySelectorAll('.o_filter_menu.o_menu_item');
            [...menuItemEls].forEach((e,index)=>{
                assert.strictEqual(e.innerText.trim(),String(index+1));
            });

            controlPanel.destroy();
        });
    });
});
