flectra.define('web.graph_view_tests',function(require){
"usestrict";

varsearchUtils=require('web.searchUtils');
varGraphView=require('web.GraphView');
vartestUtils=require('web.test_utils');
const{sortBy}=require('web.utils');

constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;
varpatchDate=testUtils.mock.patchDate;

const{INTERVAL_OPTIONS,PERIOD_OPTIONS,COMPARISON_OPTIONS}=searchUtils;

varINTERVAL_OPTION_IDS=Object.keys(INTERVAL_OPTIONS);

constyearIds=[];
constotherIds=[];
for(constidofObject.keys(PERIOD_OPTIONS)){
    constoption=PERIOD_OPTIONS[id];
    if(option.granularity==='year'){
        yearIds.push(id);
    }else{
        otherIds.push(id);
    }
}
constBASIC_DOMAIN_IDS=[];
for(constyearIdofyearIds){
    BASIC_DOMAIN_IDS.push(yearId);
    for(constidofotherIds){
        BASIC_DOMAIN_IDS.push(`${yearId}__${id}`);
    }
}
constGENERATOR_INDEXES={};
letindex=0;
for(constidofObject.keys(PERIOD_OPTIONS)){
    GENERATOR_INDEXES[id]=index++;
}

constCOMPARISON_OPTION_IDS=Object.keys(COMPARISON_OPTIONS);
constCOMPARISON_OPTION_INDEXES={};
index=0;
for(constcomparisonOptionIdofCOMPARISON_OPTION_IDS){
    COMPARISON_OPTION_INDEXES[comparisonOptionId]=index++;
}

varf=(a,b)=>[].concat(...a.map(d=>b.map(e=>[].concat(d,e))));
varcartesian=(a,b,...c)=>(b?cartesian(f(a,b),...c):a);

varCOMBINATIONS=cartesian(COMPARISON_OPTION_IDS,BASIC_DOMAIN_IDS);
varCOMBINATIONS_WITH_DATE=cartesian(COMPARISON_OPTION_IDS,BASIC_DOMAIN_IDS,INTERVAL_OPTION_IDS);

QUnit.assert.checkDatasets=function(graph,keys,expectedDatasets){
    keys=keysinstanceofArray?keys:[keys];
    expectedDatasets=expectedDatasetsinstanceofArray?
                            expectedDatasets:
                            [expectedDatasets];
    vardatasets=graph.renderer.chart.data.datasets;
    varactualValues=datasets.map(dataset=>_.pick(dataset,keys));
    this.pushResult({
        result:_.isEqual(actualValues,expectedDatasets),
        actual:actualValues,
        expected:expectedDatasets,
    });
};

QUnit.assert.checkLabels=function(graph,expectedLabels){
    varlabels=graph.renderer.chart.data.labels;
    this.pushResult({
        result:_.isEqual(labels,expectedLabels),
        actual:labels,
        expected:expectedLabels,
    });
};

QUnit.assert.checkLegend=function(graph,expectedLegendLabels){
    expectedLegendLabels=expectedLegendLabelsinstanceofArray?
                                expectedLegendLabels:
                                [expectedLegendLabels];
    varchart=graph.renderer.chart;
    varactualLegendLabels=chart.config.options.legend.labels.generateLabels(chart).map(o=>o.text);

    this.pushResult({
        result:_.isEqual(actualLegendLabels,expectedLegendLabels),
        actual:actualLegendLabels,
        expected:expectedLegendLabels,
    });
};

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            foo:{
                fields:{
                    foo:{string:"Foo",type:"integer",store:true},
                    bar:{string:"bar",type:"boolean"},
                    product_id:{string:"Product",type:"many2one",relation:'product',store:true},
                    color_id:{string:"Color",type:"many2one",relation:'color'},
                    date:{string:"Date",type:'date',store:true,sortable:true},
                    revenue:{string:"Revenue",type:'integer',store:true},
                },
                records:[
                    {id:1,foo:3,bar:true,product_id:37,date:"2016-01-01",revenue:1},
                    {id:2,foo:53,bar:true,product_id:37,color_id:7,date:"2016-01-03",revenue:2},
                    {id:3,foo:2,bar:true,product_id:37,date:"2016-03-04",revenue:3},
                    {id:4,foo:24,bar:false,product_id:37,date:"2016-03-07",revenue:4},
                    {id:5,foo:4,bar:false,product_id:41,date:"2016-05-01",revenue:5},
                    {id:6,foo:63,bar:false,product_id:41},
                    {id:7,foo:42,bar:false,product_id:41},
                    {id:8,foo:48,bar:false,product_id:41,date:"2016-04-01",revenue:8},
                ]
            },
            product:{
                fields:{
                    name:{string:"ProductName",type:"char"}
                },
                records:[{
                    id:37,
                    display_name:"xphone",
                },{
                    id:41,
                    display_name:"xpad",
                }]
            },
            color:{
                fields:{
                    name:{string:"Color",type:"char"}
                },
                records:[{
                    id:7,
                    display_name:"red",
                },{
                    id:14,
                    display_name:"black",
                }]
            },
        };
    }
},function(){

    QUnit.module('GraphView');

    QUnit.test('simplegraphrendering',asyncfunction(assert){
        assert.expect(5);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas',
                    "shouldcontainadivwithacanvaselement");
        assert.strictEqual(graph.renderer.state.mode,"bar",
            "shouldbeinbarchartmodebydefault");
        assert.checkLabels(graph,[[true],[false]]);
        assert.checkDatasets(graph,
            ['backgroundColor','data','label','originIndex','stack'],
            {
                backgroundColor:"#1f77b4",
                data:[3,5],
                label:"Count",
                originIndex:0,
                stack:"",
            }
        );
        assert.checkLegend(graph,'Count');

        graph.destroy();
    });

    QUnit.test('defaulttypeattribute',asyncfunction(assert){
        assert.expect(1);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="pie">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        assert.strictEqual(graph.renderer.state.mode,"pie","shouldbeinpiechartmodebydefault");

        graph.destroy();
    });

    QUnit.test('titleattribute',asyncfunction(assert){
        assert.expect(1);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphtitle="Partners"type="pie">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        assert.strictEqual(graph.$('.o_graph_rendererlabel').text(),"Partners",
            "shouldhave'Partnersastitle'");

        graph.destroy();
    });

    QUnit.test('fieldidnotingroupBy',asyncfunction(assert){
        assert.expect(1);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="id"/>'+
                '</graph>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    assert.deepEqual(args.kwargs.groupby,[],
                        'groupbyshouldnotcontainidfield');
                }
                returnthis._super.apply(this,arguments);
            },
        });
        graph.destroy();
    });

    QUnit.test('switchingmode',asyncfunction(assert){
        assert.expect(6);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="line">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        assert.strictEqual(graph.renderer.state.mode,"line","shouldbeinlinechartmodebydefault");
        assert.doesNotHaveClass(graph.$buttons.find('button[data-mode="bar"]'),'active',
            'bartypebuttonshouldnotbeactive');
        assert.hasClass(graph.$buttons.find('button[data-mode="line"]'),'active',
            'linetypebuttonshouldbeactive');

        awaittestUtils.dom.click(graph.$buttons.find('button[data-mode="bar"]'));
        assert.strictEqual(graph.renderer.state.mode,"bar","shouldbeinbarchartmodebydefault");
        assert.doesNotHaveClass(graph.$buttons.find('button[data-mode="line"]'),'active',
            'linetypebuttonshouldnotbeactive');
        assert.hasClass(graph.$buttons.find('button[data-mode="bar"]'),'active',
            'bartypebuttonshouldbeactive');

        graph.destroy();
    });

    QUnit.test('displayinglinechartwithonly1datapoint',asyncfunction(assert){
        assert.expect(1);
         //thistestmakessurethelinechartdoesnotcrashwhenonlyonedata
        //pointisdisplayed.
        this.data.foo.records=this.data.foo.records.slice(0,1);
        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="line">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        assert.containsOnce(graph,'canvas',"shouldhaveacanvas");

        graph.destroy();
    });

    QUnit.test('displayingchartdatawithmultiplegroupbys',asyncfunction(assert){
        //thistestmakessurethelinechartshowsalldatalabels(Xaxis)when
        //itisgroupedbyseveralfields
        assert.expect(6);

        vargraph=awaitcreateView({
            View:GraphView,
            model:'foo',
            data:this.data,
            arch:'<graphtype="bar"><fieldname="foo"/></graph>',
            groupBy:['product_id','bar','color_id'],
        });

        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,['true/Undefined','true/red','false/Undefined']);

        awaittestUtils.dom.click(graph.$buttons.find('button[data-mode="line"]'));
        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,['true/Undefined','true/red','false/Undefined']);

        awaittestUtils.dom.click(graph.$buttons.find('button[data-mode="pie"]'));
        assert.checkLabels(graph,[
            ["xphone",true,"Undefined"],
            ["xphone",true,"red"],
            ["xphone",false,"Undefined"],
            ["xpad",false,"Undefined"]
        ]);
        assert.checkLegend(graph,[
            'xphone/true/Undefined',
            'xphone/true/red',
            'xphone/false/Undefined',
            'xpad/false/Undefined'
        ]);

        graph.destroy();
    });

    QUnit.test('switchingmeasures',asyncfunction(assert){
        assert.expect(2);

        varrpcCount=0;

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Gloups">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
            mockRPC:function(route,args){
                rpcCount++;
                returnthis._super(route,args);
            },
        });
        awaitcpHelpers.toggleMenu(graph,"Measures");
        awaitcpHelpers.toggleMenuItem(graph,"Foo");

        assert.checkLegend(graph,'Foo');
        assert.strictEqual(rpcCount,2,"shouldhavedone2rpcs(2readgroups)");

        graph.destroy();
    });

    QUnit.test('nocontenthelper(barchart)',asyncfunction(assert){
        assert.expect(3);
        this.data.foo.records=[];

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`
                <graphstring="Gloups">
                    <fieldname="product_id"/>
                </graph>`,
            viewOptions:{
                action:{
                    help:'<pclass="abc">Thishelpershouldnotbedisplayedingraphviews</p>'
                }
            },
        });

        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas');
        assert.containsNone(graph,'div.o_view_nocontent');
        assert.containsNone(graph,'.abc');

        graph.destroy();
    });

    QUnit.test('nocontenthelper(piechart)',asyncfunction(assert){
        assert.expect(3);
        this.data.foo.records= [];

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`
                <graphtype="pie">
                    <fieldname="product_id"/>
                </graph>`,
            viewOptions:{
                action:{
                    help:'<pclass="abc">Thishelpershouldnotbedisplayedingraphviews</p>'
                }
            },
        });

        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas');
        assert.containsNone(graph,'div.o_view_nocontent');
        assert.containsNone(graph,'.abc');

        graph.destroy();
    });

    QUnit.test('renderpiechartincomparisonmode',asyncfunction(assert){
        assert.expect(2);

        constunpatchDate=patchDate(2020,4,19,1,0,0);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            context:{search_default_date_filter:1,},
            arch:'<graphtype="pie">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
            archs:{
                'foo,false,search':`
                    <search>
                        <filtername="date_filter"domain="[]"date="date"default_period="third_quarter"/>
                    </search>
                `,
            },
        });

        awaitcpHelpers.toggleComparisonMenu(graph);
        awaitcpHelpers.toggleMenuItem(graph,'Date:Previousperiod');

        assert.containsNone(graph,'div.o_view_nocontent',
        "shouldnotdisplaythenocontenthelper");
        assert.checkLegend(graph,'Nodata');

        unpatchDate();
        graph.destroy();
    });

    QUnit.test('fakedatainlinechart',asyncfunction(assert){
        assert.expect(1);

        constunpatchDate=patchDate(2020,4,19,1,0,0);

        this.data.foo.records=[];

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            context:{search_default_date_filter:1,},
            arch:'<graphtype="line">'+
                        '<fieldname="date"/>'+
                '</graph>',
            archs:{
                'foo,false,search':`
                    <search>
                        <filtername="date_filter"domain="[]"date="date"default_period="third_quarter"/>
                    </search>
                `,
            },
        });

        awaitcpHelpers.toggleComparisonMenu(graph);
        awaitcpHelpers.toggleMenuItem(graph,'Date:Previousperiod');

        assert.checkLabels(graph,[[''],['']]);

        unpatchDate();
        graph.destroy();
    });

    QUnit.test('nofillingcolorforperiodofcomparison',asyncfunction(assert){
        assert.expect(1);

        constunpatchDate=patchDate(2020,4,19,1,0,0);

        this.data.foo.records.forEach((r)=>{
            if(r.date){
                r.date=r.date.replace(/\d\d\d\d/,"2019");
            }
        });

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            context:{search_default_date_filter:1,},
            arch:'<graphtype="line">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
            archs:{
                'foo,false,search':`
                    <search>
                        <filtername="date_filter"domain="[]"date="date"default_period="this_year"/>
                    </search>
                `,
            },
        });

        awaitcpHelpers.toggleComparisonMenu(graph);
        awaitcpHelpers.toggleMenuItem(graph,'Date:Previousperiod');

        assert.checkDatasets(graph,["data","backgroundColor"],{data:[4,2]});

        unpatchDate();
        graph.destroy();
    });

    QUnit.test('nocontenthelperafterupdate',asyncfunction(assert){
        assert.expect(6);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`
                <graphstring="Gloups">
                    <fieldname="product_id"/>
                </graph>`,
            viewOptions:{
                action:{
                    help:'<pclass="abc">Thishelpershouldnotbedisplayedingraphviews</p>'
                }
            },
        });

        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas');
        assert.containsNone(graph,'div.o_view_nocontent');
        assert.containsNone(graph,'.abc');

        awaittestUtils.graph.reload(graph,{domain:[['product_id','<',0]]});

        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas');
        assert.containsNone(graph,'div.o_view_nocontent');
        assert.containsNone(graph,'.abc');

        graph.destroy();
    });

    QUnit.test('canreloadwithothergroupby',asyncfunction(assert){
        assert.expect(2);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Gloups">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
        });

        assert.checkLabels(graph,[['xphone'],['xpad']]);

        awaittestUtils.graph.reload(graph,{groupBy:['color_id']});
        assert.checkLabels(graph,[['Undefined'],['red']]);

        graph.destroy();
    });

    QUnit.test('getOwnedQueryParamscorrectlyreturnsmode,measure,andgroupbys',asyncfunction(assert){
        assert.expect(4);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Gloups">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
        });

        assert.deepEqual(graph.getOwnedQueryParams(),{
            context:{
                graph_mode:'bar',
                graph_measure:'__count__',
                graph_groupbys:['product_id'],
            }
        },"contextshouldbecorrect");

        awaitcpHelpers.toggleMenu(graph,"Measures");
        awaitcpHelpers.toggleMenuItem(graph,"Foo");

        assert.deepEqual(graph.getOwnedQueryParams(),{
            context:{
                graph_mode:'bar',
                graph_measure:'foo',
                graph_groupbys:['product_id'],
            },
        },"contextshouldbecorrect");

        awaittestUtils.dom.click(graph.$buttons.find('button[data-mode="line"]'));
        assert.deepEqual(graph.getOwnedQueryParams(),{
            context:{
                graph_mode:'line',
                graph_measure:'foo',
                graph_groupbys:['product_id'],
            },
        },"contextshouldbecorrect");

        awaittestUtils.graph.reload(graph,{groupBy:['product_id','color_id']});//changegroupbys
        assert.deepEqual(graph.getOwnedQueryParams(),{
            context:{
                graph_mode:'line',
                graph_measure:'foo',
                graph_groupbys:['product_id','color_id'],
            },
        },"contextshouldbecorrect");

        graph.destroy();
    });

    QUnit.test('correctlyusesgraph_keysfromthecontext',asyncfunction(assert){
        assert.expect(5);

        varlastOne=_.last(this.data.foo.records);
        lastOne.color_id=14;

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graph><fieldname="product_id"/></graph>',
            viewOptions:{
                context:{
                    graph_measure:'foo',
                    graph_mode:'line',
                    graph_groupbys:['color_id'],
                },
            },
        });
        //checkmeasurenameispresentinlegend
        assert.checkLegend(graph,'Foo');
        //checkmode
        assert.strictEqual(graph.renderer.state.mode,"line","shouldbeinlinechartmode");
        assert.doesNotHaveClass(graph.$buttons.find('button[data-mode="bar"]'),'active',
            'barchartbuttonshouldnotbeactive');
        assert.hasClass(graph.$buttons.find('button[data-mode="line"]'),'active',
            'linechartbuttonshouldbeactive');
        //checkgroupbyvalues('Undefined'isrejectedinlinechart)areinlabels
        assert.checkLabels(graph,[['red'],['black']]);

        graph.destroy();
    });

    QUnit.test('correctlyusegroup_bykeyfromthecontext',asyncfunction(assert){
        assert.expect(1);

        varlastOne=_.last(this.data.foo.records);
        lastOne.color_id=14;

        vargraph=awaitcreateView({
            View:GraphView,
            model:'foo',
            data:this.data,
            arch:'<graph><fieldname="product_id"/></graph>',
            groupBy:['color_id'],
            viewOptions:{
                context:{
                    graph_measure:'foo',
                    graph_mode:'line',
                },
            },
        });
        //checkgroupbyvalues('Undefined'isrejectedinlinechart)areinlabels
        assert.checkLabels(graph,[['red'],['black']]);

        graph.destroy();
    });

    QUnit.test('correctlyusesgraph_keysfromthecontext(atreload)',asyncfunction(assert){
        assert.expect(7);

        varlastOne=_.last(this.data.foo.records);
        lastOne.color_id=14;

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graph><fieldname="product_id"/></graph>',
        });

        assert.strictEqual(graph.renderer.state.mode,"bar","shouldbeinbarchartmode");
        assert.hasClass(graph.$buttons.find('button[data-mode="bar"]'),'active',
            'barchartbuttonshouldbeactive');

        varreloadParams={
            context:{
                graph_measure:'foo',
                graph_mode:'line',
                graph_groupbys:['color_id'],
            },
        };
        awaittestUtils.graph.reload(graph,reloadParams);

        //checkmeasure
        assert.checkLegend(graph,'Foo');
        //checkmode
        assert.strictEqual(graph.renderer.state.mode,"line","shouldbeinlinechartmode");
        assert.doesNotHaveClass(graph.$buttons.find('button[data-mode="bar"]'),'active',
            'barchartbuttonshouldnotbeactive');
        assert.hasClass(graph.$buttons.find('button[data-mode="line"]'),'active',
            'linechartbuttonshouldbeactive');
        //checkgroupbyvalues('Undefined'isrejectedinlinechart)areinlabels
        assert.checkLabels(graph,[['red'],['black']]);

        graph.destroy();
    });

    QUnit.test('reloadgraphwithcorrectfields',asyncfunction(assert){
        assert.expect(2);

        vargraph=awaitcreateView({
            View:GraphView,
            model:'foo',
            data:this.data,
            arch:'<graph>'+
                    '<fieldname="product_id"type="row"/>'+
                    '<fieldname="foo"type="measure"/>'+
                '</graph>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    assert.deepEqual(args.kwargs.fields,['product_id','foo'],
                        "shouldreadthecorrectfields");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.graph.reload(graph,{groupBy:[]});

        graph.destroy();
    });

    QUnit.test('initialgroupbyiskeptwhenreloading',asyncfunction(assert){
        assert.expect(8);

        vargraph=awaitcreateView({
            View:GraphView,
            model:'foo',
            data:this.data,
            arch:'<graph>'+
                    '<fieldname="product_id"type="row"/>'+
                    '<fieldname="foo"type="measure"/>'+
                '</graph>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    assert.deepEqual(args.kwargs.groupby,['product_id'],
                        "shouldgroupbythecorrectfield");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,'Foo');
        assert.checkDatasets(graph,'data',{data:[82,157]});

        awaittestUtils.graph.reload(graph,{groupBy:[]});
        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,'Foo');
        assert.checkDatasets(graph,'data',{data:[82,157]});

        graph.destroy();
    });

    QUnit.test('onlyprocessmostrecentdataforconcurrentgroupby',asyncfunction(assert){
        assert.expect(4);

        constgraph=awaitcreateView({
            View:GraphView,
            model:'foo',
            data:this.data,
            arch:`
                <graph>
                    <fieldname="product_id"type="row"/>
                    <fieldname="foo"type="measure"/>
                </graph>`,
        });

        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkDatasets(graph,'data',{data:[82,157]});

        testUtils.graph.reload(graph,{groupBy:['color_id']});
        awaittestUtils.graph.reload(graph,{groupBy:['date:month']});
        assert.checkLabels(graph,[['January2016'],['March2016'],['May2016'],['Undefined'],['April2016']]);
        assert.checkDatasets(graph,'data',{data:[56,26,4,105,48]});

        graph.destroy();
    });

    QUnit.test('useamany2oneasameasureshouldwork(withoutgroupBy)',asyncfunction(assert){
        assert.expect(4);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="product_id"type="measure"/>'+
                '</graph>',
        });
        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas',
                    "shouldcontainadivwithacanvaselement");
        assert.checkLabels(graph,[[]]);
        assert.checkLegend(graph,'Product');
        assert.checkDatasets(graph,'data',{data:[2]});

        graph.destroy();
    });

    QUnit.test('useamany2oneasameasureshouldwork(withgroupBy)',asyncfunction(assert){
        assert.expect(5);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="bar"type="row"/>'+
                        '<fieldname="product_id"type="measure"/>'+
                '</graph>',
        });
        assert.containsOnce(graph,'div.o_graph_canvas_containercanvas',
                    "shouldcontainadivwithacanvaselement");

        assert.strictEqual(graph.renderer.state.mode,"bar",
            "shouldbeinbarchartmodebydefault");
        assert.checkLabels(graph,[[true],[false]]);
        assert.checkLegend(graph,'Product');
        assert.checkDatasets(graph,'data',{data:[1,2]});

        graph.destroy();
    });

    QUnit.test('useamany2oneasameasureandasagroupbyshouldwork',asyncfunction(assert){
        assert.expect(3);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="product_id"type="row"/>'+
                '</graph>',
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });

        //needtosetthemeasurethiswaybecauseitcannotbesetinthe
        //arch.
        awaitcpHelpers.toggleMenu(graph,"Measures");
        awaitcpHelpers.toggleMenuItem(graph,"Product");

        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,'Product');
        assert.checkDatasets(graph,'data',{data:[1,1]});

        graph.destroy();
    });

    QUnit.test('notuseamany2oneasameasurebydefault',asyncfunction(assert){
        assert.expect(1);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
        });
        assert.notOk(graph.measures.product_id,
            "shouldnothaveproduct_idasmeasure");
        graph.destroy();
    });

    QUnit.test('useamany2oneasameasureifsetasadditionalfields',asyncfunction(assert){
        assert.expect(1);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="product_id"/>'+
                '</graph>',
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });

        assert.ok(graph.measures.find(m=>m.fieldName==='product_id'),
            "shouldhaveproduct_idasmeasure");

        graph.destroy();
    });

    QUnit.test('measuredropdownconsistency',asyncfunction(assert){
        assert.expect(2);

        constactionManager=awaittestUtils.createActionManager({
            archs:{
                'foo,false,graph':`
                    <graphstring="Partners"type="bar">
                        <fieldname="foo"type="measure"/>
                    </graph>`,
                'foo,false,search':`<search/>`,
                'foo,false,kanban':`
                    <kanban>
                        <templates>
                            <divt-name="kanban-box">
                                <fieldname="foo"/>
                            </div>
                        </templates>
                    </kanban>`,
            },
            data:this.data,
        });
        awaitactionManager.doAction({
            res_model:'foo',
            type:'ir.actions.act_window',
            views:[[false,'graph'],[false,'kanban']],
            flags:{
                graph:{
                    additionalMeasures:['product_id'],
                }
            },
        });

        assert.containsOnce(actionManager,'.o_control_panel.o_graph_measures_list',
            "Measuresdropdownispresentatinit"
        );

        awaitcpHelpers.switchView(actionManager,'kanban');
        awaitcpHelpers.switchView(actionManager,'graph');

        assert.containsOnce(actionManager,'.o_control_panel.o_graph_measures_list',
            "Measuresdropdownispresentafterreload"
        );

        actionManager.destroy();
    });

    QUnit.test('graphviewcrashwhenmovingfromsearchviewusingDownkey',asyncfunction(assert){
        assert.expect(1);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="pie">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });
        graph._giveFocus();
        assert.ok(true,"shouldnotgenerateanyerror");
        graph.destroy();
    });

    QUnit.test('graphmeasuresshouldbealphabeticallysorted',asyncfunction(assert){
        assert.expect(2);

        vardata=this.data;
        data.foo.fields.bouh={string:"bouh",type:"integer"};

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:data,
            arch:'<graphstring="Partners">'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="bouh"type="measure"/>'+
                  '</graph>',
        });

        awaitcpHelpers.toggleMenu(graph,"Measures");
        assert.strictEqual(graph.$buttons.find('.o_graph_measures_list.dropdown-item:first').text(),'bouh',
            "Bouhshouldbethefirstmeasure");
        assert.strictEqual(graph.$buttons.find('.o_graph_measures_list.dropdown-item:last').text(),'Count',
            "Countshouldbethelastmeasure");

        graph.destroy();
    });

    QUnit.test('Undefinedshouldappearinbar,piegraphbutnotinlinegraph',asyncfunction(assert){
        assert.expect(3);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            groupBy:['date'],
            data:this.data,
            arch:'<graphstring="Partners"type="line">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        function_indexOf(label){
            returngraph.renderer._indexOf(graph.renderer.chart.data.labels,label);
        }

        assert.strictEqual(_indexOf(['Undefined']),-1);

        awaittestUtils.dom.click(graph.$buttons.find('.o_graph_button[data-mode=bar]'));
        assert.ok(_indexOf(['Undefined'])>=0);

        awaittestUtils.dom.click(graph.$buttons.find('.o_graph_button[data-mode=pie]'));
        assert.ok(_indexOf(['Undefined'])>=0);

        graph.destroy();
    });

    QUnit.test('Undefinedshouldappearinbar,piegraphbutnotinlinegraphwithmultiplegroupbys',asyncfunction(assert){
        assert.expect(4);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            groupBy:['date','color_id'],
            data:this.data,
            arch:'<graphstring="Partners"type="line">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        function_indexOf(label){
            returngraph.renderer._indexOf(graph.renderer.chart.data.labels,label);
        }

        assert.strictEqual(_indexOf(['Undefined']),-1);

        awaittestUtils.dom.click(graph.$buttons.find('.o_graph_button[data-mode=bar]'));
        assert.ok(_indexOf(['Undefined'])>=0);

        awaittestUtils.dom.click(graph.$buttons.find('.o_graph_button[data-mode=pie]'));
        varlabels=graph.renderer.chart.data.labels;
        assert.ok(labels.filter(label=>/Undefined/.test(label.join(''))).length>=1);

        //Undefinedshouldnotappearafterswitchingbacktolinechart
        awaittestUtils.dom.click(graph.$buttons.find('.o_graph_button[data-mode=line]'));
        assert.strictEqual(_indexOf(['Undefined']),-1);

        graph.destroy();
    });

    QUnit.test('nocomparisonandnogroupby',asyncfunction(assert){
        assert.expect(9);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="bar">'+
                        '<fieldname="foo"type="measure"/>'+
                '</graph>',
        });


        assert.checkLabels(graph,[[]]);
        assert.checkLegend(graph,'Foo');
        assert.checkDatasets(graph,'data',{data:[239]});

        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=line]'));
        //thelabelsinlinechartistranslatedinthiscasetoavoidtohaveasingle
        //pointattheleftofthescreenandcharttoseemempty.
        assert.checkLabels(graph,[[''],[],['']]);
        assert.checkLegend(graph,'Foo');
        assert.checkDatasets(graph,'data',{data:[undefined,239]});
        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=pie]'));
        assert.checkLabels(graph,[[]]);
        assert.checkLegend(graph,'Total');
        assert.checkDatasets(graph,'data',{data:[239]});

        graph.destroy();
    });

    QUnit.test('nocomparisonandonegroupby',asyncfunction(assert){
        assert.expect(9);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="bar">'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="bar"type="row"/>'+
                '</graph>',
        });

        assert.checkLabels(graph,[[true],[false]]);
        assert.checkLegend(graph,'Foo');
        assert.checkDatasets(graph,'data',{data:[58,181]});

        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=line]'));
        assert.checkLabels(graph,[[true],[false]]);
        assert.checkLegend(graph,'Foo');
        assert.checkDatasets(graph,'data',{data:[58,181]});

        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=pie]'));

        assert.checkLabels(graph,[[true],[false]]);
        assert.checkLegend(graph,['true','false']);
        assert.checkDatasets(graph,'data',{data:[58,181]});

        graph.destroy();
    });
    QUnit.test('nocomparisonandtwogroupby',asyncfunction(assert){
        assert.expect(9);
        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="Partners"type="bar">'+
                        '<fieldname="foo"type="measure"/>'+
                '</graph>',
            groupBy:['product_id','color_id'],
        });

        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,['Undefined','red']);
        assert.checkDatasets(graph,['label','data'],[
            {
                label:'Undefined',
                data:[29,157],
            },
            {
                label:'red',
                data:[53,0],
            }
        ]);

        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=line]'));
        assert.checkLabels(graph,[['xphone'],['xpad']]);
        assert.checkLegend(graph,['Undefined','red']);
        assert.checkDatasets(graph,['label','data'],[
            {
                label:'Undefined',
                data:[29,157],
            },
            {
                label:'red',
                data:[53,0],
            }
        ]);

        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=pie]'));
        assert.checkLabels(graph,[['xphone','Undefined'],['xphone','red'],['xpad','Undefined']]);
        assert.checkLegend(graph,['xphone/Undefined','xphone/red','xpad/Undefined']);
        assert.checkDatasets(graph,['label','data'],{
                label:'',
                data:[29,53,157],
        });

        graph.destroy();
    });

    QUnit.test('graphviewonlykeepsfinergroupbyfilteroptionforagivengroupby',asyncfunction(assert){
        assert.expect(3);

        vargraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            groupBy:['date:year','product_id','date','date:quarter'],
            data:this.data,
            arch:'<graphstring="Partners"type="line">'+
                        '<fieldname="bar"/>'+
                '</graph>',
        });

        assert.checkLabels(graph,[["January2016"],["March2016"],["May2016"],["April2016"]]);
        //mockReadGroupdoesnotalwayssortgroups->May2016isbeforeApril2016forthatreason.
        assert.checkLegend(graph,["xphone","xpad"]);
        assert.checkDatasets(graph,['label','data'],[
            {
                label:'xphone',
                data:[2,2,0,0],
            },{
                label:'xpad',
                data:[0,0,1,1],
            }
        ]);

        graph.destroy();
    });

    QUnit.test('clickingonbarandpiechartstriggersado_action',asyncfunction(assert){
        assert.expect(5);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="FooAnalysis"><fieldname="bar"/></graph>',
            intercepts:{
                do_action:function(ev){
                    assert.deepEqual(ev.data.action,{
                        context:{},
                        domain:[["bar","=",true]],
                        name:"FooAnalysis",
                        res_model:"foo",
                        target:'current',
                        type:'ir.actions.act_window',
                        view_mode:'list',
                        views:[[false,'list'],[false,'form']],
                    },"shouldtriggerdo_actionwithcorrectactionparameter");
                }
            },
        });
        awaittestUtils.nextTick();//waitforthegraphtoberendered

        //barmode
        assert.strictEqual(graph.renderer.state.mode,"bar","shouldbeinbarchartmode");
        assert.checkDatasets(graph,['domain'],{
            domain:[[["bar","=",true]],[["bar","=",false]]],
        });

        letmyChart=graph.renderer.chart;
        letmeta=myChart.getDatasetMeta(0);
        letrectangle=myChart.canvas.getBoundingClientRect();
        letpoint=meta.data[0].getCenterPoint();
        awaittestUtils.dom.triggerEvent(myChart.canvas,'click',{
            pageX:rectangle.left+point.x,
            pageY:rectangle.top+point.y
        });

        //piemode
        awaittestUtils.dom.click(graph.$('.o_graph_button[data-mode=pie]'));
        assert.strictEqual(graph.renderer.state.mode,"pie","shouldbeinpiechartmode");

        myChart=graph.renderer.chart;
        meta=myChart.getDatasetMeta(0);
        rectangle=myChart.canvas.getBoundingClientRect();
        point=meta.data[0].getCenterPoint();
        awaittestUtils.dom.triggerEvent(myChart.canvas,'click',{
            pageX:rectangle.left+point.x,
            pageY:rectangle.top+point.y
        });

        graph.destroy();
    });

    QUnit.test('clickingchartstriggerado_actionwithcorrectviews',asyncfunction(assert){
        assert.expect(3);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphstring="FooAnalysis"><fieldname="bar"/></graph>',
            intercepts:{
                do_action:function(ev){
                    assert.deepEqual(ev.data.action,{
                        context:{},
                        domain:[["bar","=",true]],
                        name:"FooAnalysis",
                        res_model:"foo",
                        target:'current',
                        type:'ir.actions.act_window',
                        view_mode:'list',
                        views:[[364,'list'],[29,'form']],
                    },"shouldtriggerdo_actionwithcorrectactionparameter");
                }
            },
            viewOptions:{
                actionViews:[{
                    type:'list',
                    viewID:364,
                },{
                    type:'form',
                    viewID:29,
                }],
            },
        });
        awaittestUtils.nextTick();//waitforthegraphtoberendered

        assert.strictEqual(graph.renderer.state.mode,"bar","shouldbeinbarchartmode");
        assert.checkDatasets(graph,['domain'],{
            domain:[[["bar","=",true]],[["bar","=",false]]],
        });

        letmyChart=graph.renderer.chart;
        letmeta=myChart.getDatasetMeta(0);
        letrectangle=myChart.canvas.getBoundingClientRect();
        letpoint=meta.data[0].getCenterPoint();
        awaittestUtils.dom.triggerEvent(myChart.canvas,'click',{
            pageX:rectangle.left+point.x,
            pageY:rectangle.top+point.y
        });

        graph.destroy();
    });

    QUnit.test('graphviewwithattributedisable_linking="True"',asyncfunction(assert){
        assert.expect(2);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:'<graphdisable_linking="1"><fieldname="bar"/></graph>',
            intercepts:{
                do_action:function(){
                    thrownewError('Shouldnotperformado_action');
                },
            },
        });
        awaittestUtils.nextTick();//waitforthegraphtoberendered

        assert.strictEqual(graph.renderer.state.mode,"bar","shouldbeinbarchartmode");
        assert.checkDatasets(graph,['domain'],{
            domain:[[["bar","=",true]],[["bar","=",false]]],
        });

        letmyChart=graph.renderer.chart;
        letmeta=myChart.getDatasetMeta(0);
        letrectangle=myChart.canvas.getBoundingClientRect();
        letpoint=meta.data[0].getCenterPoint();
        awaittestUtils.dom.triggerEvent(myChart.canvas,'click',{
            pageX:rectangle.left+point.x,
            pageY:rectangle.top+point.y
        });

        graph.destroy();
    });

    QUnit.test('graphviewwithoutinvisibleattributeonfield',asyncfunction(assert){
        assert.expect(4);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`<graphstring="Partners"></graph>`,
        });

        awaittestUtils.dom.click(graph.$('.btn-group:firstbutton'));
        assert.containsN(graph,'li.o_menu_item',3,
            "thereshouldbethreemenuiteminthemeasuresdropdown(count,revenueandfoo)");
        assert.containsOnce(graph,'li.o_menu_itema:contains("Revenue")');
        assert.containsOnce(graph,'li.o_menu_itema:contains("Foo")');
        assert.containsOnce(graph,'li.o_menu_itema:contains("Count")');

        graph.destroy();
    });

    QUnit.test('graphviewwithinvisibleattributeonfield',asyncfunction(assert){
        assert.expect(2);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`
                <graphstring="Partners">
                    <fieldname="revenue"invisible="1"/>
                </graph>`,
        });

        awaittestUtils.dom.click(graph.$('.btn-group:firstbutton'));
        assert.containsN(graph,'li.o_menu_item',2,
            "thereshouldbeonlytwomenuiteminthemeasuresdropdown(countandfoo)");
        assert.containsNone(graph,'li.o_menu_itema:contains("Revenue")');

        graph.destroy();
    });

    QUnit.test('graphviewsortbymeasure',asyncfunction(assert){
        assert.expect(18);

        //changefirstrecordfromfooasthereare4recordscountforeachproduct
        this.data.product.records.push({id:38,display_name:"zphone"});
        this.data.foo.records[7].product_id=38;

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`<graphstring="Partners"order="desc">
                        <fieldname="product_id"/>
                </graph>`,
        });

        assert.containsN(graph,'button[data-order]',2,
            "thereshouldbetwoorderbuttonsforsortingaxislabelsinbarmode");
        assert.checkLegend(graph,'Count','measureshouldbebycount');
        assert.hasClass(graph.$('button[data-order="desc"]'),'active',
            'sortingshouldbeapplieondescendingorderbydefaultwhensorting="desc"');
        assert.checkDatasets(graph,'data',{data:[4,3,1]});

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="asc"]'));
        assert.hasClass(graph.$('button[data-order="asc"]'),'active',
            "ascendingordershouldbeapplied");
        assert.checkDatasets(graph,'data',{data:[1,3,4]});

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.hasClass(graph.$('button[data-order="desc"]'),'active',
            "descendingorderbuttonshouldbeactive");
        assert.checkDatasets(graph,'data',{data:[4,3,1]});

        //againclickondescendingbuttontodeactivateorderbutton
        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.doesNotHaveClass(graph.$('button[data-order="desc"]'),'active',
            "descendingorderbuttonshouldnotbeactive");
        assert.checkDatasets(graph,'data',{data:[4,3,1]});

        //setlinemode
        awaittestUtils.dom.click(graph.$buttons.find('button[data-mode="line"]'));
        assert.containsN(graph,'button[data-order]',2,
            "thereshouldbetwoorderbuttonsforsortingaxislabelsinlinemode");
        assert.checkLegend(graph,'Count','measureshouldbebycount');
        assert.doesNotHaveClass(graph.$('button[data-order="desc"]'),'active',
            "descendingordershouldbeapplied");
        assert.checkDatasets(graph,'data',{data:[4,3,1]});

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="asc"]'));
        assert.hasClass(graph.$('button[data-order="asc"]'),'active',
            "ascendingorderbuttonshouldbeactive");
        assert.checkDatasets(graph,'data',{data:[1,3,4]});

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.hasClass(graph.$('button[data-order="desc"]'),'active',
            "descendingorderbuttonshouldbeactive");
        assert.checkDatasets(graph,'data',{data:[4,3,1]});

        graph.destroy();
    });

    QUnit.test('graphviewsortbymeasureforgroupeddata',asyncfunction(assert){
        assert.expect(9);

        //changefirstrecordfromfooasthereare4recordscountforeachproduct
        this.data.product.records.push({id:38,display_name:"zphone",});
        this.data.foo.records[7].product_id=38;

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`<graphstring="Partners">
                        <fieldname="product_id"/>
                        <fieldname="bar"/>
                </graph>`,
        });

        assert.checkLegend(graph,["true","false"],'measureshouldbebycount');
        assert.containsN(graph,'button[data-order]',2,
            "thereshouldbetwoorderbuttonsforsortingaxislabels");
        assert.checkDatasets(graph,'data',[{data:[3,0,0]},{data:[1,3,1]}]);

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="asc"]'));
        assert.hasClass(graph.$('button[data-order="asc"]'),'active',
            "ascendingordershouldbeappliedbydefault");
        assert.checkDatasets(graph,'data',[{data:[1,3,1]},{data:[0,0,3]}]);

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.hasClass(graph.$('button[data-order="desc"]'),'active',
            "ascendingorderbuttonshouldbeactive");
        assert.checkDatasets(graph,'data',[{data:[1,3,1]},{data:[3,0,0]}]);

        //againclickondescendingbuttontodeactivateorderbutton
        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.doesNotHaveClass(graph.$('button[data-order="desc"]'),'active',
            "descendingorderbuttonshouldnotbeactive");
        assert.checkDatasets(graph,'data',[{data:[3,0,0]},{data:[1,3,1]}]);

        graph.destroy();
    });

    QUnit.test('graphviewsortbymeasureformultiplegroupeddata',asyncfunction(assert){
        assert.expect(9);

        //changefirstrecordfromfooasthereare4recordscountforeachproduct
        this.data.product.records.push({id:38,display_name:"zphone"});
        this.data.foo.records[7].product_id=38;

        //addfewmorerecordstodatatohavegroupeddatadatewise
        constdata=[
            {id:9,foo:48,bar:false,product_id:41,date:"2016-04-01"},
            {id:10,foo:49,bar:false,product_id:41,date:"2016-04-01"},
            {id:11,foo:50,bar:true,product_id:37,date:"2016-01-03"},
            {id:12,foo:50,bar:true,product_id:41,date:"2016-01-03"},
        ];

        Object.assign(this.data.foo.records,data);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`<graphstring="Partners">
                        <fieldname="product_id"/>
                        <fieldname="date"/>
                </graph>`,
            groupBy:['date','product_id']
        });

        assert.checkLegend(graph,["xpad","xphone","zphone"],'measureshouldbebycount');
        assert.containsN(graph,'button[data-order]',2,
            "thereshouldbetwoorderbuttonsforsortingaxislabels");
        assert.checkDatasets(graph,'data',[{data:[2,1,1,2]},{data:[0,1,0,0]},{data:[1,0,0,0]}]);

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="asc"]'));
        assert.hasClass(graph.$('button[data-order="asc"]'),'active',
            "ascendingordershouldbeappliedbydefault");
        assert.checkDatasets(graph,'data',[{data:[1,1,2,2]},{data:[0,1,0,0]},{data:[0,0,0,1]}]);

        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.hasClass(graph.$('button[data-order="desc"]'),'active',
            "descendingorderbuttonshouldbeactive");
        assert.checkDatasets(graph,'data',[{data:[1,0,0,0]},{data:[2,2,1,1]},{data:[0,0,1,0]}]);

        //againclickondescendingbuttontodeactivateorderbutton
        awaittestUtils.dom.click(graph.$buttons.find('button[data-order="desc"]'));
        assert.doesNotHaveClass(graph.$('button[data-order="desc"]'),'active',
            "descendingorderbuttonshouldnotbeactive");
        assert.checkDatasets(graph,'data',[{data:[2,1,1,2]},{data:[0,1,0,0]},{data:[1,0,0,0]}]);

        graph.destroy();
    });

    QUnit.test('emptygraphviewwithsampledata',asyncfunction(assert){
        assert.expect(8);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`
                <graphsample="1">
                    <fieldname="product_id"/>
                    <fieldname="date"/>
                </graph>`,
            domain:[['id','<',0]],
            viewOptions:{
                action:{
                    help:'<pclass="abc">clicktoaddafoo</p>'
                }
            },
        });

        assert.hasClass(graph.el,'o_view_sample_data');
        assert.containsOnce(graph,'.o_view_nocontent');
        assert.containsOnce(graph,'.o_graph_canvas_containercanvas');
        assert.hasClass(graph.$('.o_graph_canvas_container'),'o_sample_data_disabled');

        awaitgraph.reload({domain:[]});

        assert.doesNotHaveClass(graph.el,'o_view_sample_data');
        assert.containsNone(graph,'.o_view_nocontent');
        assert.containsOnce(graph,'.o_graph_canvas_containercanvas');
        assert.doesNotHaveClass(graph.$('.o_graph_canvas_container'),'o_sample_data_disabled');

        graph.destroy();
    });

    QUnit.test('nonemptygraphviewwithsampledata',asyncfunction(assert){
        assert.expect(8);

        constgraph=awaitcreateView({
            View:GraphView,
            model:"foo",
            data:this.data,
            arch:`
                <graphsample="1">
                    <fieldname="product_id"/>
                    <fieldname="date"/>
                </graph>`,
            viewOptions:{
                action:{
                    help:'<pclass="abc">clicktoaddafoo</p>'
                }
            },
        })

        assert.doesNotHaveClass(graph.el,'o_view_sample_data');
        assert.containsNone(graph,'.o_view_nocontent');
        assert.containsOnce(graph,'.o_graph_canvas_containercanvas');
        assert.doesNotHaveClass(graph.$('.o_graph_canvas_container'),'o_sample_data_disabled');

        awaitgraph.reload({domain:[['id','<',0]]});

        assert.doesNotHaveClass(graph.el,'o_view_sample_data');
        assert.containsOnce(graph,'.o_graph_canvas_containercanvas');
        assert.doesNotHaveClass(graph.$('.o_graph_canvas_container'),'o_sample_data_disabled');
        assert.containsNone(graph,'.o_view_nocontent');

        graph.destroy();
    });

    QUnit.module('GraphView:comparisonmode',{
        beforeEach:asyncfunction(){
            this.data.foo.records[0].date='2016-12-15';
            this.data.foo.records[1].date='2016-12-17';
            this.data.foo.records[2].date='2016-11-22';
            this.data.foo.records[3].date='2016-11-03';
            this.data.foo.records[4].date='2016-12-20';
            this.data.foo.records[5].date='2016-12-19';
            this.data.foo.records[6].date='2016-12-15';
            this.data.foo.records[7].date=undefined;

            this.data.foo.records.push({id:9,foo:48,bar:false,product_id:41,color_id:7,date:"2016-12-01"});
            this.data.foo.records.push({id:10,foo:17,bar:true,product_id:41,color_id:7,date:"2016-12-01"});
            this.data.foo.records.push({id:11,foo:45,bar:true,product_id:37,color_id:14,date:"2016-12-01"});
            this.data.foo.records.push({id:12,foo:48,bar:false,product_id:37,color_id:7,date:"2016-12-10"});
            this.data.foo.records.push({id:13,foo:48,bar:false,product_id:undefined,color_id:14,date:"2016-11-30"});
            this.data.foo.records.push({id:14,foo:-50,bar:true,product_id:41,color_id:14,date:"2016-12-15"});
            this.data.foo.records.push({id:15,foo:53,bar:false,product_id:41,color_id:14,date:"2016-11-01"});
            this.data.foo.records.push({id:16,foo:53,bar:true,product_id:undefined,color_id:7,date:"2016-09-01"});
            this.data.foo.records.push({id:17,foo:48,bar:false,product_id:41,color_id:undefined,date:"2016-08-01"});
            this.data.foo.records.push({id:18,foo:-156,bar:false,product_id:37,color_id:undefined,date:"2016-07-15"});
            this.data.foo.records.push({id:19,foo:31,bar:false,product_id:41,color_id:14,date:"2016-12-15"});
            this.data.foo.records.push({id:20,foo:109,bar:true,product_id:41,color_id:7,date:"2015-06-01"});

            this.data.foo.records=sortBy(this.data.foo.records,'date');

            this.unpatchDate=patchDate(2016,11,20,1,0,0);

            constgraph=awaitcreateView({
                View:GraphView,
                model:"foo",
                data:this.data,
                arch:`
                    <graphstring="Partners"type="bar">
                        <fieldname="foo"type="measure"/>
                    </graph>
                `,
                archs:{
                    'foo,false,search':`
                        <search>
                            <filtername="date"string="Date"context="{'group_by':'date'}"/>
                            <filtername="date_filter"string="DateFilter"date="date"/>
                            <filtername="bar"string="Bar"context="{'group_by':'bar'}"/>
                            <filtername="product_id"string="Product"context="{'group_by':'product_id'}"/>
                            <filtername="color_id"string="Color"context="{'group_by':'color_id'}"/>
                        </search>
                    `,
                },
                viewOptions:{
                    additionalMeasures:['product_id'],
                },
            });

            this.graph=graph;

            varcheckOnlyToCheck=true;
            varexhaustiveTest=false||checkOnlyToCheck;

            varself=this;
            asyncfunction*graphGenerator(combinations){
                vari=0;
                while(i<combinations.length){
                    varcombination=combinations[i];
                    if(!checkOnlyToCheck||combination.toString()inself.combinationsToCheck){
                        awaitself.setConfig(combination);
                    }
                    if(exhaustiveTest){
                        i++;
                    }else{
                        i+=Math.floor(1+Math.random()*20);
                    }
                    yieldcombination;
                }
            }

            this.combinationsToCheck={};
            this.testCombinations=asyncfunction(combinations,assert){
                forawait(varcombinationofgraphGenerator(combinations)){
                    //wecancheckparticularcombinationshere
                    if(combination.toString()inself.combinationsToCheck){
                        if(self.combinationsToCheck[combination].errorMessage){
                            assert.strictEqual(
                                graph.$('.o_nocontent_helpp').eq(1).text().trim(),
                                self.combinationsToCheck[combination].errorMessage
                            );
                        }else{
                            assert.checkLabels(graph,self.combinationsToCheck[combination].labels);
                            assert.checkLegend(graph,self.combinationsToCheck[combination].legend);
                            assert.checkDatasets(graph,['label','data'],self.combinationsToCheck[combination].datasets);
                        }
                    }
                }
            };

            constGROUPBY_NAMES=['Date','Bar','Product','Color'];

            this.selectTimeRanges=asyncfunction(comparisonOptionId,basicDomainId){
                constfacetEls=graph.el.querySelectorAll('.o_searchview_facet');
                constfacetIndex=[...facetEls].findIndex(el=>!!el.querySelector('span.fa-filter'));
                if(facetIndex>-1){
                    awaitcpHelpers.removeFacet(graph,facetIndex);
                }
                const[yearId,otherId]=basicDomainId.split('__');
                awaitcpHelpers.toggleFilterMenu(graph);
                awaitcpHelpers.toggleMenuItem(graph,'DateFilter');
                awaitcpHelpers.toggleMenuItemOption(graph,'DateFilter',GENERATOR_INDEXES[yearId]);
                if(otherId){
                    awaitcpHelpers.toggleMenuItemOption(graph,'DateFilter',GENERATOR_INDEXES[otherId]);
                }
                constitemIndex=COMPARISON_OPTION_INDEXES[comparisonOptionId];
                awaitcpHelpers.toggleComparisonMenu(graph);
                awaitcpHelpers.toggleMenuItem(graph,itemIndex);
            };

            //groupbymenuisassumedtobeclosed
            this.selectDateIntervalOption=asyncfunction(intervalOption){
                intervalOption=intervalOption||'month';
                constoptionIndex=INTERVAL_OPTION_IDS.indexOf(intervalOption);

                awaitcpHelpers.toggleGroupByMenu(graph);
                letwasSelected=false;
                if(this.keepFirst){
                    if(cpHelpers.isItemSelected(graph,2)){
                        wasSelected=true;
                        awaitcpHelpers.toggleMenuItem(graph,2);
                    }
                }
                awaitcpHelpers.toggleMenuItem(graph,0);
                if(!cpHelpers.isOptionSelected(graph,0,optionIndex)){
                    awaitcpHelpers.toggleMenuItemOption(graph,0,optionIndex);
                }
                for(leti=0;i<INTERVAL_OPTION_IDS.length;i++){
                    constoId=INTERVAL_OPTION_IDS[i];
                    if(oId!==intervalOption&&cpHelpers.isOptionSelected(graph,0,i)){
                        awaitcpHelpers.toggleMenuItemOption(graph,0,i);
                    }
                }

                if(this.keepFirst){
                    if(wasSelected&&!cpHelpers.isItemSelected(graph,2)){
                        awaitcpHelpers.toggleMenuItem(graph,2);
                    }
                }
                awaitcpHelpers.toggleGroupByMenu(graph);

            };

            //groupbymenuisassumedtobeclosed
            this.selectGroupBy=asyncfunction(groupByName){
                awaitcpHelpers.toggleGroupByMenu(graph);
                constindex=GROUPBY_NAMES.indexOf(groupByName);
                if(!cpHelpers.isItemSelected(graph,index)){
                    awaitcpHelpers.toggleMenuItem(graph,index);
                }
                awaitcpHelpers.toggleGroupByMenu(graph);
            };

            this.setConfig=asyncfunction(combination){
                awaitthis.selectTimeRanges(combination[0],combination[1]);
                if(combination.length===3){
                    awaitself.selectDateIntervalOption(combination[2]);
                }
            };

            this.setMode=asyncfunction(mode){
                awaittestUtils.dom.click($(`.o_control_panel.o_graph_button[data-mode="${mode}"]`));
            };

        },
        afterEach:function(){
            this.unpatchDate();
            this.graph.destroy();
        },
    },function(){
        QUnit.test('comparisonwithonegroupbyequaltocomparisondatefield',asyncfunction(assert){
            assert.expect(11);

            this.combinationsToCheck={
                'previous_period,this_year__this_month,day':{
                    labels:[...Array(6).keys()].map(x=>[x]),
                    legend:["December2016","November2016"],
                    datasets:[
                        {
                            data:[110,48,26,53,63,4],
                            label:"December2016",
                        },
                        {
                            data:[53,24,2,48],
                            label:"November2016",
                        }
                    ],
                }
            };

            varcombinations=COMBINATIONS_WITH_DATE;
            awaitthis.testCombinations(combinations,assert);
            awaitthis.setMode('line');
            awaitthis.testCombinations(combinations,assert);
            this.combinationsToCheck['previous_period,this_year__this_month,day']={
                labels:[...Array(6).keys()].map(x=>[x]),
                legend:[
                    "2016-12-01,2016-11-01",
                    "2016-12-10,2016-11-03",
                    "2016-12-15,2016-11-22",
                    "2016-12-17,2016-11-30",
                    "2016-12-19",
                    "2016-12-20"
                ],
                datasets:[
                    {
                        data:[110,48,26,53,63,4],
                        label:"December2016",
                    },
                    {
                        data:[53,24,2,48,0,0],
                        label:"November2016",
                    }
                ],
            };
            awaitthis.setMode('pie');
            awaitthis.testCombinations(combinations,assert);

            //isNotVisiblecannothavetwoelementssocheckingvisibilityoffirstelement
            assert.isNotVisible(this.graph.$('button[data-order]:first'),
                "thereshouldnotbeorderbuttonincomparisonmode");
            assert.ok(true,"Nocombinationcausesacrash");
        });

        QUnit.test('comparisonwithnogroupby',asyncfunction(assert){
            assert.expect(10);

            this.combinationsToCheck={
                'previous_period,this_year__this_month':{
                    labels:[[]],
                    legend:["December2016","November2016"],
                    datasets:[
                        {
                            data:[304],
                            label:"December2016",
                        },
                        {
                            data:[127],
                            label:"November2016",
                        }
                    ],
                }
            };

            varcombinations=COMBINATIONS;
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_period,this_year__this_month']={
                labels:[[''],[],['']],
                legend:["December2016","November2016"],
                datasets:[
                    {
                        data:[undefined,304],
                        label:"December2016",
                    },
                    {
                        data:[undefined,127],
                        label:"November2016",
                    }
                ],
            };
            awaitthis.setMode('line');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_period,this_year__this_month']= {
                labels:[[]],
                legend:["Total"],
                datasets:[
                    {
                        data:[304],
                        label:"December2016",
                    },
                    {
                        data:[127],
                        label:"November2016",
                    }
                ],
            };
            awaitthis.setMode('pie');
            awaitthis.testCombinations(combinations,assert);

            assert.ok(true,"Nocombinationcausesacrash");
        });

        QUnit.test('comparisonwithonegroupbydifferentfromcomparisondatefield',asyncfunction(assert){
            assert.expect(10);

            this.combinationsToCheck={
                'previous_period,this_year__this_month':{
                    labels:[["xpad"],["xphone"],["Undefined"]],
                    legend:["December2016","November2016"],
                    datasets:[
                        {
                            data:[155,149,0],
                            label:"December2016",
                        },
                        {
                            data:[53,26,48],
                            label:"November2016",
                        }
                    ],
                }
            };

            varcombinations=COMBINATIONS;
            awaitthis.selectGroupBy('Product');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_period,this_year__this_month']={
                labels:[["xpad"],["xphone"]],
                legend:["December2016","November2016"],
                datasets:[
                    {
                        data:[155,149],
                        label:"December2016",
                    },
                    {
                        data:[53,26],
                        label:"November2016",
                    }
                ],
            };
            awaitthis.setMode('line');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_period,this_year__this_month']={
                labels:[["xpad"],["xphone"],["Undefined"]],
                legend:["xpad","xphone","Undefined"],
                datasets:[
                    {
                        data:[155,149,0],
                        label:"December2016",
                    },
                    {
                        data:[53,26,48],
                        label:"November2016",
                    }
                ],
            };
            awaitthis.setMode('pie');
            awaitthis.testCombinations(combinations,assert);

            assert.ok(true,"Nocombinationcausesacrash");
        });

        QUnit.test('comparisonwithtwogroupbywithfirstgroupbyequaltocomparisondatefield',asyncfunction(assert){
            assert.expect(10);

            this.keepFirst=true;
            this.combinationsToCheck={
                'previous_period,this_year__this_month,day':{
                    labels:[...Array(6).keys()].map(x=>[x]),
                    legend:[
                        "December2016/xpad",
                        "December2016/xphone",
                        "November2016/xpad",
                        "November2016/xphone",
                        "November2016/Undefined"
                    ],
                    datasets:[
                        {
                          data:[65,0,23,0,63,4],
                          label:"December2016/xpad"
                        },
                        {
                          data:[45,48,3,53,0,0],
                          label:"December2016/xphone"
                        },
                        {
                          data:[53,0,0,0],
                          label:"November2016/xpad"
                        },
                        {
                          data:[0,24,2,0],
                          label:"November2016/xphone"
                        },
                        {
                          data:[0,0,0,48],
                          label:"November2016/Undefined"
                        }
                      ]
                }
            };

            varcombinations=COMBINATIONS_WITH_DATE;
            awaitthis.selectGroupBy('Product');
            awaitthis.testCombinations(combinations,assert);
            awaitthis.setMode('line');
            awaitthis.testCombinations(combinations,assert);


            this.combinationsToCheck['previous_period,this_year__this_month,day']={
                labels:[[0,"xpad"],[0,"xphone"],[1,"xphone"],[2,"xphone"],[2,"xpad"],[3,"xphone"],[4,"xpad"],[5,"xpad"],[3,"Undefined"]],
                legend:[
                    "2016-12-01,2016-11-01/xpad",
                    "2016-12-01,2016-11-01/xphone",
                    "2016-12-10,2016-11-03/xphone",
                    "2016-12-15,2016-11-22/xphone",
                    "2016-12-15,2016-11-22/xpad",
                    "2016-12-17,2016-11-30/xphone",
                    "2016-12-19/xpad",
                    "2016-12-20/xpad",
                    "2016-12-17,2016-11-30/Undefine..."
                ],
                datasets:[
                    {
                      "data":[65,45,48,3,23,53,63,4,0],
                      "label":"December2016"
                    },
                    {
                      "data":[53,0,24,2,0,0,0,0,48],
                      "label":"November2016"
                    }
                  ],
            };

            awaitthis.setMode('pie');
            awaitthis.testCombinations(combinations,assert);

            assert.ok(true,"Nocombinationcausesacrash");

            this.keepFirst=false;
        });

        QUnit.test('comparisonwithtwogroupbywithsecondgroupbyequaltocomparisondatefield',asyncfunction(assert){
            assert.expect(8);

            this.combinationsToCheck={
                'previous_period,this_year,quarter':{
                    labels:[["xphone"],["xpad"],["Undefined"]],
                    legend:[
                        "2016/Q32016",
                        "2016/Q42016",
                        "2015/Q22015"
                    ],
                    datasets:[
                        {
                            data:[-156,48,53],
                            label:"2016/Q32016",
                        },
                        {
                            data:[175,208,48],
                            label:"2016/Q42016",
                        },
                        {
                            data:[0,109,0],
                            label:"2015/Q22015",
                        },
                    ]
                }
            };

            constcombinations=COMBINATIONS_WITH_DATE;
            awaitthis.selectGroupBy('Product');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_period,this_year,quarter']={
                labels:[["xphone"],["xpad"]],
                legend:[
                    "2016/Q32016",
                    "2016/Q42016",
                    "2015/Q22015"
                ],
                datasets:[
                    {
                        data:[-156,48],
                        label:"2016/Q32016",
                    },
                    {
                        data:[175,208],
                        label:"2016/Q42016",
                    },
                    {
                        data:[0,109],
                        label:"2015/Q22015",
                    },
                ]
            };
            awaitthis.setMode('line');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_period,this_year,quarter']={
                errorMessage:'Piechartcannotmixpositiveandnegativenumbers.'+
                                'Trytochangeyourdomaintoonlydisplaypositiveresults'
            };
            awaitthis.setMode('pie');
            awaitthis.testCombinations(combinations,assert);

            assert.ok(true,"Nocombinationcausesacrash");
        });
        QUnit.test('comparisonwithtwogroupbywithnogroupbyequaltocomparisondatefield',asyncfunction(assert){
            assert.expect(10);

            this.combinationsToCheck={
                'previous_year,this_year__last_month':{
                    labels:[["xpad"],["xphone"],["Undefined"]],
                    legend:["November2016/false","November2016/true"],
                    datasets:[
                        {
                            data:[53,24,48],
                            label:"November2016/false",
                        },
                        {
                            data:[0,2,0],
                            label:"November2016/true",
                        }
                    ],
                }
            };

            varcombinations=COMBINATIONS;
            awaitthis.selectGroupBy('Product');
            awaitthis.selectGroupBy('Bar');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_year,this_year__last_month']={
                labels:[["xpad"],["xphone"]],
                legend:["November2016/false","November2016/true"],
                datasets:[
                    {
                        data:[53,24],
                        label:"November2016/false",
                    },
                    {
                        data:[0,2],
                        label:"November2016/true",
                    }
                ],
            };
            awaitthis.setMode('line');
            awaitthis.testCombinations(combinations,assert);

            this.combinationsToCheck['previous_year,this_year__last_month']={
                labels:
                [["xpad",false],["xphone",false],["xphone",true],["Undefined",false],["Nodata"]],
                legend:[
                    "xpad/false",
                    "xphone/false",
                    "xphone/true",
                    "Undefined/false",
                    "Nodata"
                ],
                datasets:[
                    {
                      "data":[53,24,2,48],
                      "label":"November2016"
                    },
                    {
                      "data":[undefined,undefined,undefined,undefined,1],
                      "label":"November2015"
                    }
                  ],
            };
            awaitthis.setMode('pie');
            awaitthis.testCombinations(combinations,assert);

            assert.ok(true,"Nocombinationcausesacrash");
        });
    });
});
});
