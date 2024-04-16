flectra.define('web.comparison_menu_tests',function(require){
    "usestrict";

    const{
        controlPanel:cpHelpers,
        createControlPanel,
        mock,
    }=require('web.test_utils');

    const{patchDate}=mock;
    constsearchMenuTypes=['filter','comparison'];

    QUnit.module('Components',{
        beforeEach(){
            this.fields={
                birthday:{string:"Birthday",type:"date",store:true,sortable:true},
                date_field:{string:"Date",type:"date",store:true,sortable:true},
                float_field:{string:"Float",type:"float",group_operator:'sum'},
                foo:{string:"Foo",type:"char",store:true,sortable:true},
            };
            this.cpModelConfig={
                arch:`
                    <search>
                        <filtername="birthday"date="birthday"/>
                        <filtername="date_field"date="date_field"/>
                    </search>`,
                fields:this.fields,
                searchMenuTypes,
            };
        },
    },function(){

        QUnit.module('ComparisonMenu');

        QUnit.test('simplerendering',asyncfunction(assert){
            assert.expect(6);

            constunpatchDate=patchDate(1997,0,9,12,0,0);
            constparams={
                cpModelConfig:this.cpModelConfig,
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.containsOnce(controlPanel,".o_dropdown.o_filter_menu");
            assert.containsNone(controlPanel,".o_dropdown.o_comparison_menu");

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Birthday");
            awaitcpHelpers.toggleMenuItemOption(controlPanel,"Birthday","January");

            assert.containsOnce(controlPanel,'div.o_comparison_menu>buttoni.fa.fa-adjust');
            assert.strictEqual(controlPanel.el.querySelector('div.o_comparison_menu>buttonspan').innerText.trim(),"Comparison");

            awaitcpHelpers.toggleComparisonMenu(controlPanel);

            constcomparisonOptions=[...controlPanel.el.querySelectorAll(
                '.o_comparison_menuli'
            )];
            assert.strictEqual(comparisonOptions.length,2);
            assert.deepEqual(
                comparisonOptions.map(e=>e.innerText),
                ["Birthday:PreviousPeriod","Birthday:PreviousYear"]
            );

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('activateacomparisonworks',asyncfunction(assert){
            assert.expect(5);

            constunpatchDate=patchDate(1997,0,9,12,0,0);
            constparams={
                cpModelConfig:this.cpModelConfig,
                cpProps:{fields:this.fields,searchMenuTypes},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Birthday");
            awaitcpHelpers.toggleMenuItemOption(controlPanel,"Birthday","January");
            awaitcpHelpers.toggleComparisonMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Birthday:PreviousPeriod");

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[
                "Birthday:January1997",
                "Birthday:PreviousPeriod",
            ]);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Date");
            awaitcpHelpers.toggleMenuItemOption(controlPanel,"Date","December");
            awaitcpHelpers.toggleComparisonMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Date:PreviousYear");

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[
                ["Birthday:January1997","Date:December1996"].join("or"),
                "Date:PreviousYear",
            ]);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Date");
            awaitcpHelpers.toggleMenuItemOption(controlPanel,"Date","1996");

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[
                "Birthday:January1997",
            ]);

            awaitcpHelpers.toggleComparisonMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Birthday:PreviousYear");

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[
                "Birthday:January1997",
                "Birthday:PreviousYear",
            ]);

            awaitcpHelpers.removeFacet(controlPanel);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('notimeRangeskeyinsearchqueryif"comparison"notinsearchMenuTypes',asyncfunction(assert){
            assert.expect(1);

            this.cpModelConfig.searchMenuTypes=['filter'];
            constparams={
                cpModelConfig:this.cpModelConfig,
                cpProps:{fields:this.fields,searchMenuTypes:['filter']},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFilterMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"Birthday");
            awaitcpHelpers.toggleMenuItemOption(controlPanel,"Birthday",0);

            assert.notOk("timeRanges"incontrolPanel.getQuery());

            controlPanel.destroy();
        });
    });
});
