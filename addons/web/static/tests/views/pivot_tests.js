flectra.define('web.pivot_tests',function(require){
"usestrict";

varcore=require('web.core');
varPivotView=require('web.PivotView');
constPivotController=require("web.PivotController");
vartestUtils=require('web.test_utils');
vartestUtilsDom=require('web.test_utils_dom');

var_t=core._t;
constcpHelpers=testUtils.controlPanel;
varcreateActionManager=testUtils.createActionManager;
varcreateView=testUtils.createView;
varpatchDate=testUtils.mock.patchDate;

/**
 *Helperfunctionthatreturns,givenapivotinstance,thevaluesofthe
 *table,separatedby','.
 *
 *@returns{string}
 */
vargetCurrentValues=function(pivot){
    returnpivot.$('.o_pivot_cell_valuediv').map(function(){
        return$(this).text();
    }).get().join();
};


QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    foo:{string:"Foo",type:"integer",searchable:true,group_operator:'sum'},
                    bar:{string:"bar",type:"boolean",store:true,sortable:true},
                    date:{string:"Date",type:"date",store:true,sortable:true},
                    product_id:{string:"Product",type:"many2one",relation:'product',store:true},
                    other_product_id:{string:"OtherProduct",type:"many2one",relation:'product',store:true},
                    non_stored_m2o:{string:"NonStoredM2O",type:"many2one",relation:'product'},
                    customer:{string:"Customer",type:"many2one",relation:'customer',store:true},
                    computed_field:{string:"Computedandnotstored",type:'integer',compute:true,group_operator:'sum'},
                    company_type:{
                        string:"CompanyType",type:"selection",
                        selection:[["company","Company"],["individual","individual"]],
                        searchable:true,sortable:true,store:true,
                    },
                },
                records:[
                    {
                        id:1,
                        foo:12,
                        bar:true,
                        date:'2016-12-14',
                        product_id:37,
                        customer:1,
                        computed_field:19,
                        company_type:'company',
                    },{
                        id:2,
                        foo:1,
                        bar:true,
                        date:'2016-10-26',
                        product_id:41,
                        customer:2,
                        computed_field:23,
                        company_type:'individual',
                    },{
                        id:3,
                        foo:17,
                        bar:true,
                        date:'2016-12-15',
                        product_id:41,
                        customer:2,
                        computed_field:26,
                        company_type:'company',
                    },{
                        id:4,
                        foo:2,
                        bar:false,
                        date:'2016-04-11',
                        product_id:41,
                        customer:1,
                        computed_field:19,
                        company_type:'individual',
                    },
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
            customer:{
                fields:{
                    name:{string:"CustomerName",type:"char"}
                },
                records:[{
                    id:1,
                    display_name:"First",
                },{
                    id:2,
                    display_name:"Second",
                }]
            },
        };
    },
},function(){
    QUnit.module('PivotView');

    QUnit.test('simplepivotrendering',asyncfunction(assert){
        assert.expect(3);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            mockRPC:function(route,args){
                assert.strictEqual(args.kwargs.lazy,false,
                    "theread_groupshouldbedonewiththelazy=falseoption");
                returnthis._super.apply(this,arguments);
            },
        });

        assert.hasClass(pivot.$('table'),'o_enable_linking',
            "tableshouldhaveclassname'o_enable_linking'");
        assert.strictEqual(pivot.$('td.o_pivot_cell_value:contains(32)').length,1,
                    "shouldcontainapivotcellwiththesumofallrecords");
        pivot.destroy();
    });

    QUnit.test('pivotrenderingwithwidget',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                        '<fieldname="foo"type="measure"widget="float_time"/>'+
                '</pivot>',
        });

        assert.strictEqual(pivot.$('td.o_pivot_cell_value:contains(32:00)').length,1,
                    "shouldcontainapivotcellwiththesumofallrecords");
        pivot.destroy();
    });

    QUnit.test('pivotrenderingwithstringattributeonfield',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo={string:"Foo",type:"integer",store:true,group_operator:'sum'};

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                        '<fieldname="foo"string="BAR"type="measure"/>'+
                '</pivot>',
        });

        assert.strictEqual(pivot.$('.o_pivot_measure_row').text(),"BAR",
                    "thedisplayednameshouldbetheonesetinthestringattribute");
        pivot.destroy();
    });

    QUnit.test('pivotrenderingwithstringattributeonnonstoredfield',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.fubar={string:"Fubar",type:"integer",store:false,group_operator:'sum'};

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                        '<fieldname="fubar"string="fubar"type="measure"/>'+
                '</pivot>',
        });
        assert.containsOnce(pivot,'.o_pivot','Nonstoredfieldscanhaveastringattribute');
        pivot.destroy();
    });

    QUnit.test('pivotrenderingwithinvisibleattributeonfield',asyncfunction(assert){
        assert.expect(3);
        //wheninvisible,afieldshouldneitherbeanactivemeasure,
        //norbeaselectablemeasure.
        _.extend(this.data.partner.fields,{
            foo:{string:"Foo",type:"integer",store:true,group_operator:'sum'},
            foo2:{string:"Foo2",type:"integer",store:true,group_operator:'sum'}
        });

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="foo2"type="measure"invisible="True"/>'+
                '</pivot>',
        });

        //thereshouldbeonlyonedisplayedmeasureastheotheroneisinvisible
        assert.containsOnce(pivot,'.o_pivot_measure_row');
        //thereshouldbeonlyonemeasurebesidescount,astheotheroneisinvisible
        assert.containsN(pivot,'.o_cp_bottom_left.dropdown-item',2);
        //theinvisiblefieldsouldn'tbeinthegroupablefieldsneither
        awaittestUtils.dom.click(pivot.$('.o_pivot_header_cell_closed:first'));
        assert.containsNone(pivot,'.o_pivot_field_menua[data-field="foo2"]');

        pivot.destroy();
    });

    QUnit.test('pivotviewwithout"string"attribute',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        //thisisimportantforexportfunctionality.
        assert.strictEqual(pivot.title,_t("Untitled"),"shouldhaveavalidtitle");
        pivot.destroy();
    });

    QUnit.test('groupheadersshouldhaveatooltip',asyncfunction(assert){
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="col"/>'+
                        '<fieldname="date"type="row"/>'+
                '</pivot>',
        });

        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:first').attr('data-original-title'),'Date');
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:first').attr('data-original-title'),'Product');

        pivot.destroy();
    });

    QUnit.test('pivotviewaddcomputedfieldsexplicitlydefinedasmeasure',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="computed_field"type="measure"/>'+
                '</pivot>',
        });

        assert.ok(pivot.measures.computed_field,"measurescontainsthefield'computed_field'");
        pivot.destroy();
    });

    QUnit.test('clickingonacelltriggersado_action',asyncfunction(assert){
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            intercepts:{
                do_action:function(ev){
                    assert.deepEqual(ev.data.action,{
                        context:{someKey:true,userContextKey:true},
                        domain:[['product_id','=',37]],
                        name:'Partners',
                        res_model:'partner',
                        target:'current',
                        type:'ir.actions.act_window',
                        view_mode:'list',
                        views:[[false,'list'],[2,'form']],
                    },"shouldtriggerdo_actionwiththecorrectargs");
                },
            },
            session:{
                user_context:{userContextKey:true},
            },
            viewOptions:{
                action:{
                    views:[
                        {viewID:2,type:'form'},
                        {viewID:5,type:'kanban'},
                        {viewID:false,type:'list'},
                        {viewID:false,type:'pivot'},
                    ],
                },
                context:{someKey:true,search_default_test:3},
                title:'Partners',
            }
        });

        assert.hasClass(pivot.$('table'),'o_enable_linking',
            "tableshouldhaveclassname'o_enable_linking'");
        awaittestUtils.dom.click(pivot.$('.o_pivot_cell_value:contains(12)'));//shouldtriggerado_action

        pivot.destroy();
    });

    QUnit.test('rowandcolumnarehighlightedwhenhoveringacell',asyncfunction(assert){
        assert.expect(11);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                        '<fieldname="foo"type="col"/>'+
                        '<fieldname="product_id"type="row"/>'+
                '</pivot>',
        });

        //checkrowhighlighting
        assert.hasClass(pivot.$('table'),'table-hover',
            "withclassName'table-hover',rowsarehighlighted(bootstrap)");

        //checkcolumnhighlighting
        //hoverthirdmeasure
        awaittestUtils.dom.triggerEvents(pivot.$('th.o_pivot_measure_row:nth(2)'),'mouseover');
        assert.containsN(pivot,'.o_cell_hover',3);
        for(vari=0;i<3;i++){
            assert.hasClass(pivot.$('tbodytr:nth('+i+')td:nth(2)'),'o_cell_hover');
        }
        awaittestUtils.dom.triggerEvents(pivot.$('th.o_pivot_measure_row:nth(2)'),'mouseout');
        assert.containsNone(pivot,'.o_cell_hover');

        //hoversecondcell,secondrow
        awaittestUtils.dom.triggerEvents(pivot.$('tbodytr:nth(1)td:nth(1)'),'mouseover');
        assert.containsN(pivot,'.o_cell_hover',3);
        for(i=0;i<3;i++){
            assert.hasClass(pivot.$('tbodytr:nth('+i+')td:nth(1)'),'o_cell_hover');
        }
        awaittestUtils.dom.triggerEvents(pivot.$('tbodytr:nth(1)td:nth(1)'),'mouseout');
        assert.containsNone(pivot,'.o_cell_hover');

        pivot.destroy();
    });

    QUnit.test('pivotviewwithdisable_linking="True"',asyncfunction(assert){
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotdisable_linking="True">'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            intercepts:{
                do_action:function(){
                    assert.ok(false,"shouldnottriggerdo_action");
                },
            },
        });

        assert.doesNotHaveClass(pivot.$('table'),'o_enable_linking',
            "tableshouldnothaveclassname'o_enable_linking'");
        assert.containsOnce(pivot,'.o_pivot_cell_value',
            "shouldhaveonecell");
        awaittestUtils.dom.click(pivot.$('.o_pivot_cell_value'));//shouldnottriggerado_action

        pivot.destroy();
    });

    QUnit.test('clickingonthe"Total"Cellwithtimerangeactivatedgivestherightactiondomain',asyncfunction(assert){
        assert.expect(2);

        varunpatchDate=patchDate(2016,11,20,1,0,0);
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot/>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='this_month'/>
                    </search>
                `,
            },
            intercepts:{
                do_action:function(ev){
                    assert.deepEqual(
                        ev.data.action.domain,
                        ["&",["date",">=","2016-12-01"],["date","<=","2016-12-31"]],
                        "shouldtriggerdo_actionwiththecorrectactiondomain"
                    );
                },
            },
            viewOptions:{
                context:{search_default_date_filter:true,},
                title:'Partners',
            },
        });

        assert.hasClass(pivot.$('table'),'o_enable_linking',
            "rootnodeshouldhaveclassname'o_enable_linking'");
        awaittestUtilsDom.click(pivot.$('.o_pivot_cell_value'));

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('clickingonafakecellvalue("emptygroup")incomparisonmodegivesanactiondomainequivalentto[[0,"=",1]]',asyncfunction(assert){
        assert.expect(3);

        varunpatchDate=patchDate(2016,11,20,1,0,0);

        this.data.partner.records[0].date='2016-11-15';
        this.data.partner.records[1].date='2016-11-17';
        this.data.partner.records[2].date='2016-11-22';
        this.data.partner.records[3].date='2016-11-03';

        varfirst_do_action=true;
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                    '</pivot>',
            intercepts:{
                do_action:function(ev){
                    if(first_do_action){
                        assert.deepEqual(
                            ev.data.action.domain,
                            ["&",["date",">=","2016-12-01"],["date","<=","2016-12-31"]],
                            "shouldtriggerdo_actionwiththecorrectactiondomain"
                        );
                    }else{
                        assert.deepEqual(
                            ev.data.action.domain,
                            [[0,"=",1]],
                            "shouldtriggerdo_actionwiththecorrectactiondomain"
                        );
                    }
                    first_do_action=false;
                },
            },
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='this_month'/>
                    </search>
                `,
            },
            viewOptions:{
                context:{search_default_date_filter:true,},
                title:'Partners',
            },
        });

        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        assert.hasClass(pivot.$('table'),'o_enable_linking',
            "rootnodeshouldhaveclassname'o_enable_linking'");
        //hereweclickonthegroupcorrespondingtoTotal/Total/ThisMonth
        pivot.$('.o_pivot_cell_value').eq(1).click();//shouldtriggerado_actionwithappropriatedomain
        //hereweclickonthegroupcorrespondingtoxphone/Total/ThisMonth
        pivot.$('.o_pivot_cell_value').eq(4).click();//shouldtriggerado_actionwithappropriatedomain

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('pivotviewgroupedbydatefield',asyncfunction(assert){
        assert.expect(2);

        vardata=this.data;
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="month"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            mockRPC:function(route,params){
                varwrong_fields=_.filter(params.kwargs.fields,function(field){
                    return!(field.split(':')[0]indata.partner.fields);
                });
                assert.ok(!wrong_fields.length,'fieldsgiventoread_groupshouldexistonthemodel');
                returnthis._super.apply(this,arguments);
            },
        });
        pivot.destroy();
    });

    QUnit.test('withoutmeasures,pivotviewuses__countbydefault',asyncfunction(assert){
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot></pivot>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    assert.deepEqual(args.kwargs.fields,['__count'],
                        "shouldmakearead_groupwithnovalidfields");
                }
                returnthis._super(route,args);
            }
        });

        var$countMeasure=pivot.$buttons.find('.dropdown-item[data-field=__count]:first');
        assert.hasClass($countMeasure,'selected',"Thecountmeasureshouldbeactivated");
        pivot.destroy();
    });

    QUnit.test('pivotviewcanbereloaded',asyncfunction(assert){
        assert.expect(4);
        varreadGroupCount=0;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot></pivot>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    readGroupCount++;
                }
                returnthis._super(route,args);
            }
        });

        assert.strictEqual(pivot.$('td.o_pivot_cell_value:contains(4)').length,1,
                    "shouldcontainapivotcellwiththenumberofallrecords");
        assert.strictEqual(readGroupCount,1,"shouldhavedone1rpc");

        awaittestUtils.pivot.reload(pivot,{domain:[['foo','>',10]]});
        assert.strictEqual(pivot.$('td.o_pivot_cell_value:contains(2)').length,1,
                    "shouldcontainapivotcellwiththenumberofremainingrecords");
        assert.strictEqual(readGroupCount,2,"shouldhavedone2rpcs");
        pivot.destroy();
    });

    QUnit.test('pivotviewgroupedbymany2onefield',asyncfunction(assert){
        assert.expect(3);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        assert.containsOnce(pivot,'.o_pivot_header_cell_opened',
            "shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('.o_pivot_header_cell_closed:contains(xphone)').length,1,
            "shoulddisplayoneheaderwith'xphone'");
        assert.strictEqual(pivot.$('.o_pivot_header_cell_closed:contains(xpad)').length,1,
            "shoulddisplayoneheaderwith'xpad'");
        pivot.destroy();
    });

    QUnit.test('basicfolding/unfolding',asyncfunction(assert){
        assert.expect(7);

        varrpcCount=0;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            mockRPC:function(){
                rpcCount++;
                returnthis._super.apply(this,arguments);
            },
        });
        assert.containsN(pivot,'tbodytr',3,
            "shouldhave3rows:1fortheopenedheader,and2fordata");

        //clickontheopenedheadertocloseit
        awaittestUtils.dom.click(pivot.$('.o_pivot_header_cell_opened'));

        assert.containsOnce(pivot,'tbodytr',"shouldhave1row");

        //clickonclosedheadertoopendropdown
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed'));
        assert.containsN(pivot,'.o_pivot_field_menu.dropdown-item[data-field="date"]',6,
            "shouldhavethedatefieldasproposition(Date,Day,Week,Month,QuarterandYear)");
        assert.containsOnce(pivot,'.o_pivot_field_menu.dropdown-item[data-field="product_id"]',
            "shouldhavetheproduct_idfieldasproposition");
        assert.containsNone(pivot,'.o_pivot_field_menu.dropdown-item[data-field="non_stored_m2o"]',
            "shouldnothavethenon_stored_m2ofieldasproposition");

        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="date"]:first'));

        assert.containsN(pivot,'tbodytr',4,
            "shouldhave4rows:oneforheader,3fordata");
        assert.strictEqual(rpcCount,3,
            "shouldhavedone3rpcs(initialload)+openheaderwithdifferentgroupbys");

        pivot.destroy();
    });

    QUnit.test('morefolding/unfolding',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        //opendropdowntozoomintofirstrow
        awaittestUtils.dom.clickFirst(pivot.$('tbody.o_pivot_header_cell_closed'));
        //clickondatebyday
        pivot.$('.dropdown-menu.show.o_inline_dropdown.dropdown-menu').toggle();//unfoldinlinedropdown
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="date"]:contains("Day")'));

        //opendropdowntozoomintosecondrow
        awaittestUtils.dom.clickLast(pivot.$('tbodyth.o_pivot_header_cell_closed'));

        assert.containsN(pivot,'tbodytr',7,
            "shouldhave7rows(1fortotal,1forxphone,1forxpad,4fordata)");

        pivot.destroy();
    });

    QUnit.test('foldandunfoldheadergroup',asyncfunction(assert){
        assert.expect(3);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        assert.containsN(pivot,'theadtr',3);

        //foldopenedcolgroup
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_opened'));
        assert.containsN(pivot,'theadtr',2);

        //unfoldit
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="product_id"]'));
        assert.containsN(pivot,'theadtr',3);

        pivot.destroy();
    });

    QUnit.test('unfoldsecondheadergroup',asyncfunction(assert){
        assert.expect(4);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        assert.containsN(pivot,'theadtr',3);
        varvalues=['12','20','32'];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        //unfoldit
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed:nth(1)'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="company_type"]'));
        assert.containsN(pivot,'theadtr',4);
        values=['12','3','17','32'];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        pivot.destroy();
    });

    QUnit.test('cantoggleextrameasure',asyncfunction(assert){
        assert.expect(8);

        varrpcCount=0;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            mockRPC:function(){
                rpcCount++;
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(pivot,'.o_pivot_cell_value',3,
            "shouldhave3cells:1fortheopenheader,and2fordata");
        assert.doesNotHaveClass(pivot.$buttons.find('.dropdown-item[data-field=__count]:first'),'selected',
            "the__countmeasureshouldnotbeselected");

        rpcCount=0;
        awaittestUtils.pivot.toggleMeasuresDropdown(pivot);
        awaittestUtils.pivot.clickMeasure(pivot,'__count');

        assert.hasClass(pivot.$buttons.find('.dropdown-item[data-field=__count]:first'),'selected',
            "the__countmeasureshouldbeselected");
        assert.containsN(pivot,'.o_pivot_cell_value',6,
            "shouldhave6cells:2fortheopenheader,and4fordata");
        assert.strictEqual(rpcCount,2,
            "shouldhavedone2rpcstoreloaddata");

        awaittestUtils.pivot.clickMeasure(pivot,'__count');

        assert.doesNotHaveClass(pivot.$buttons.find('.dropdown-item[data-field=__count]:first'),'selected',
            "the__countmeasureshouldnotbeselected");
        assert.containsN(pivot,'.o_pivot_cell_value',3,
            "shouldhave3cells:1fortheopenheader,and2fordata");
        assert.strictEqual(rpcCount,2,
            "shouldnothavedoneanyextrarpcs");

        pivot.destroy();
    });

    QUnit.test('nocontenthelperwhennoactivemeasure',asyncfunction(assert){
        assert.expect(4);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                '</pivot>',
        });

        assert.containsNone(pivot,'.o_view_nocontent',
            "shouldnothaveano_content_helper");
        assert.containsOnce(pivot,'table',
            "shouldhaveatableinDOM");

        awaittestUtils.pivot.toggleMeasuresDropdown(pivot);
        awaittestUtils.pivot.clickMeasure(pivot,'__count');

        assert.containsOnce(pivot,'.o_view_nocontent',
            "shouldhaveano_content_helper");
        assert.containsNone(pivot,'table',
            "shouldnothaveatableinDOM");
        pivot.destroy();
    });

    QUnit.test('nocontenthelperwhennodata',asyncfunction(assert){
        assert.expect(4);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners">'+
                '</pivot>',
        });

        assert.containsNone(pivot,'.o_view_nocontent',
            "shouldnothaveano_content_helper");
        assert.containsOnce(pivot,'table',
            "shouldhaveatableinDOM");

        awaittestUtils.pivot.reload(pivot,{domain:[['foo','=',12345]]});

        assert.containsOnce(pivot,'.o_view_nocontent',
            "shouldhaveano_content_helper");
        assert.containsNone(pivot,'table',
            "shouldnothaveatableinDOM");
        pivot.destroy();
    });

    QUnit.test('nocontenthelperwhennodata,part2',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records=[];

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners"></pivot>',
        });

        assert.containsOnce(pivot,'.o_view_nocontent',
            "shouldhaveano_content_helper");
        pivot.destroy();
    });

    QUnit.test('nocontenthelperwhennodata,part3',asyncfunction(assert){
        assert.expect(4);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotstring="Partners"></pivot>',
            viewOptions:{
                domain:[['foo','=',12345]]
            },
        });

        assert.containsOnce(pivot,'.o_view_nocontent',
            "shouldhaveano_content_helper");
        awaittestUtils.pivot.reload(pivot,{domain:[['foo','=',12345]]});
        assert.containsOnce(pivot,'.o_view_nocontent',
            "shouldstillhaveano_content_helper");
        awaittestUtils.pivot.reload(pivot,{domain:[]});
        assert.containsNone(pivot,'.o_view_nocontent',
            "shouldnothaveano_content_helper");

        //triestoopenafieldselectionmenu,tomakesureitwasnot
        //removedfromthedom.
        awaittestUtils.dom.clickFirst(pivot.$('.o_pivot_header_cell_closed'));
        assert.containsOnce(pivot,'.o_pivot_field_menu',
            "thefieldselectormenuexists");
        pivot.destroy();
    });

    QUnit.test('triestorestorepreviousstateafterdomainchange',asyncfunction(assert){
        assert.expect(5);

        varrpcCount=0;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            mockRPC:function(){
                rpcCount++;
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(pivot,'.o_pivot_cell_value',3,
            "shouldhave3cells:1fortheopenheader,and2fordata");
        assert.strictEqual(pivot.$('.o_pivot_measure_row:contains(Foo)').length,1,
            "shouldhave1rowformeasureFoo");

        awaittestUtils.pivot.reload(pivot,{domain:[['foo','=',12345]]});

        rpcCount=0;
        awaittestUtils.pivot.reload(pivot,{domain:[]});

        assert.equal(rpcCount,2,"shouldhavereloadeddata");
        assert.containsN(pivot,'.o_pivot_cell_value',3,
            "shouldstillhave3cells:1fortheopenheader,and2fordata");
        assert.strictEqual(pivot.$('.o_pivot_measure_row:contains(Foo)').length,1,
            "shouldstillhave1rowformeasureFoo");
        pivot.destroy();
    });

    QUnit.test('canbegroupedwiththeupdatefunction',asyncfunction(assert){
        assert.expect(4);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        assert.containsOnce(pivot,'.o_pivot_cell_value',
            "shouldhaveonly1cell");
        assert.containsOnce(pivot,'tbodytr',
            "shouldhave1rows");

        awaittestUtils.pivot.reload(pivot,{groupBy:['product_id']});

        assert.containsN(pivot,'.o_pivot_cell_value',3,
            "shouldhave3cells");
        assert.containsN(pivot,'tbodytr',3,
            "shouldhave3rows");
        pivot.destroy();
    });

    QUnit.test('cansortdatainacolumnbyclickingonheader',asyncfunction(assert){
        assert.expect(3);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="product_id"type="row"/>'+
                '</pivot>',
        });

        assert.strictEqual($('td.o_pivot_cell_value').text(),"321220",
            "shouldhavepropervaluesincells(total,result1,result2");

        awaittestUtils.dom.click(pivot.$('th.o_pivot_measure_row'));

        assert.strictEqual($('td.o_pivot_cell_value').text(),"321220",
            "shouldhavepropervaluesincells(total,result1,result2");

        awaittestUtils.dom.click(pivot.$('th.o_pivot_measure_row'));

        assert.strictEqual($('td.o_pivot_cell_value').text(),"322012",
            "shouldhavepropervaluesincells(total,result2,result1");

        pivot.destroy();
    });

    QUnit.test('canexpandallrows',asyncfunction(assert){
        assert.expect(7);

        varnbReadGroups=0;
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="product_id"type="row"/>'+
                '</pivot>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    nbReadGroups++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(nbReadGroups,2,"shouldhavedone2read_groupRPCS");
        assert.strictEqual(pivot.$('td.o_pivot_cell_value').text(),"321220",
            "shouldhavepropervaluesincells(total,result1,result2)");

        //expandondate:days,product
        nbReadGroups=0;
        awaittestUtils.pivot.reload(pivot,{groupBy:['date:days','product_id']});

        assert.strictEqual(nbReadGroups,3,"shouldhavedone3read_groupRPCS");
        assert.containsN(pivot,'tbodytr',8,
            "shouldhave7rows(total+3forDecemberand2forOctoberandApril)");

        //collapsethelasttworows
        awaittestUtils.dom.clickLast(pivot.$('.o_pivot_header_cell_opened'));
        awaittestUtils.dom.clickLast(pivot.$('.o_pivot_header_cell_opened'));

        assert.containsN(pivot,'tbodytr',6,
            "shouldhave6rowsnow");

        //expandall
        nbReadGroups=0;
        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_expand_button'));

        assert.strictEqual(nbReadGroups,3,"shouldhavedone3read_groupRPCS");
        assert.containsN(pivot,'tbodytr',8,
            "shouldhave8rowsagain");

        pivot.destroy();
    });

    QUnit.test('expandallwithadelay',asyncfunction(assert){
        assert.expect(3);

        vardef;
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="product_id"type="row"/>'+
                '</pivot>',
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read_group'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        //expandondate:days,product
        awaittestUtils.pivot.reload(pivot,{groupBy:['date:days','product_id']});
        assert.containsN(pivot,'tbodytr',8,
            "shouldhave7rows(total+3forDecemberand2forOctoberandApril)");

        //collapsethelasttworows
        awaittestUtils.dom.clickLast(pivot.$('.o_pivot_header_cell_opened'));
        awaittestUtils.dom.clickLast(pivot.$('.o_pivot_header_cell_opened'));

        assert.containsN(pivot,'tbodytr',6,
            "shouldhave6rowsnow");

        //expandall
        def=testUtils.makeTestPromise();
        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_expand_button'));
        awaittestUtils.nextTick();
        def.resolve();
        //awaittestUtils.returnAfterNextAnimationFrame();
        awaittestUtils.nextTick();
        assert.containsN(pivot,'tbodytr',8,
            "shouldhave8rowsagain");

       pivot.destroy();
    });

    QUnit.test('candownloadafile',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="month"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            session:{
                get_file:function(args){
                    assert.strictEqual(args.url,'/web/pivot/export_xlsx',
                        "shouldcallget_filewithcorrectparameters");
                    args.complete();
                },
            },
        });

        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_download'));
        pivot.destroy();
    });

    QUnit.test('downloadafilewithsinglemeasure,measurerowdisplayedintable',asyncfunction(assert){
        assert.expect(1);

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                '<fieldname="date"interval="month"type="col"/>'+
                '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            session:{
                get_file:function(args){
                    constdata=JSON.parse(args.data.data);
                    assert.strictEqual(data.measure_headers.length,4,
                        "shouldhavemeasure_headersindata");
                    args.complete();
                },
            },
        });

        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_download'));
        pivot.destroy();
    });

    QUnit.test('downloadbuttonisdisabledwhenthereisnodata',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records=[];

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="month"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        assert.hasAttrValue(pivot.$buttons.find('.o_pivot_download'),'disabled','disabled',
            "downloadbuttonshouldbedisabled");
        pivot.destroy();
    });

    QUnit.test('getOwnedQueryParamscorrectlyreturnsmeasuresandgroupbys',asyncfunction(assert){
        assert.expect(3);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="day"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:['date:day'],
                pivot_measures:['foo'],
                pivot_row_groupby:[],
            },
        },"contextshouldbecorrect");

        //expandheaderonfieldcustomer
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed:nth(1)'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="customer"]:first'));
        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:['date:day','customer'],
                pivot_measures:['foo'],
                pivot_row_groupby:[],
            },
        },"contextshouldbecorrect");

        //expandrowonfieldproduct_id
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="product_id"]:first'));
        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:['date:day','customer'],
                pivot_measures:['foo'],
                pivot_row_groupby:['product_id'],
            },
        },"contextshouldbecorrect");

        pivot.destroy();
    });

    QUnit.test('correctlyremovepivot_keysfromthecontext',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.amount={string:"Amount",type:"float",group_operator:'sum'};

        //Equivalenttoloadingwithdefaultfilter
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="day"type="col"/>'+
                        '<fieldname="amount"type="measure"/>'+
                '</pivot>',
            viewOptions:{
                context:{
                    pivot_measures:['foo'],
                    pivot_column_groupby:['customer'],
                    pivot_row_groupby:['product_id'],
                },
            },
        });

        //Equivalenttounloadthefilter
        varreloadParams={
            context:{},
        };
        awaitpivot.reload(reloadParams);

        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:['customer'],
                pivot_measures:['foo'],
                pivot_row_groupby:['product_id'],
            },
        },"contextshouldbecorrect");

        //Let'sgetridoftherowsgroupBy
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_opened'));

        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:['customer'],
                pivot_measures:['foo'],
                pivot_row_groupby:[],
            },
        },"contextshouldbecorrect");

        //Andnow,getridofthecolgroupby
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_opened'));

        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:[],
                pivot_measures:['foo'],
                pivot_row_groupby:[],
            },
        },"contextshouldbecorrect");

        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="product_id"]:first'));

        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:[],
                pivot_measures:['foo'],
                pivot_row_groupby:['product_id'],
            },
        },"contextshouldbecorrect");

        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="customer"]:first'));

        assert.deepEqual(pivot.getOwnedQueryParams(),{
            context:{
                pivot_column_groupby:['customer'],
                pivot_measures:['foo'],
                pivot_row_groupby:['product_id'],
            },
        },"contextshouldbecorrect");

        pivot.destroy();
    });

    QUnit.test('UnloadFilter,resetdisplay,loadanotherfilter',asyncfunction(assert){
        assert.expect(18);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            viewOptions:{
                context:{
                    pivot_measures:['foo'],
                    pivot_column_groupby:['customer'],
                    pivot_row_groupby:['product_id'],
                },
            },
        });

        //CheckColumns
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_opened').length,1,
            'Thecolumnshouldbegrouped');
        assert.strictEqual(pivot.$('theadtr:contains("First")').length,1,
            'Thereshouldbeacolumn"First"');
        assert.strictEqual(pivot.$('theadtr:contains("Second")').length,1,
            'Thereshouldbeacolumn"Second"');

        //CheckRows
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_opened').length,1,
            'Therowshouldbegrouped');
        assert.strictEqual(pivot.$('tbodytr:contains("xphone")').length,1,
            'Thereshouldbearow"xphone"');
        assert.strictEqual(pivot.$('tbodytr:contains("xpad")').length,1,
            'Thereshouldbearow"xpad"');

        //Equivalenttounloadthefilter
        varreloadParams={
            context:{},
        };
        awaitpivot.reload(reloadParams);
        //collapseallheaders
        awaittestUtils.dom.click(pivot.$('.o_pivot_header_cell_opened:first'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_header_cell_opened'));

        //CheckColumns
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed').length,1,
            'Thecolumnshouldnotbegrouped');
        assert.strictEqual(pivot.$('theadtr:contains("First")').length,0,
            'Thereshouldnotbeacolumn"First"');
        assert.strictEqual(pivot.$('theadtr:contains("Second")').length,0,
            'Thereshouldnotbeacolumn"Second"');

        //CheckRows
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed').length,1,
            'Therowshouldnotbegrouped');
        assert.strictEqual(pivot.$('tbodytr:contains("xphone")').length,0,
            'Thereshouldnotbearow"xphone"');
        assert.strictEqual(pivot.$('tbodytr:contains("xpad")').length,0,
            'Thereshouldnotbearow"xpad"');

        //Equivalenttoloadanotherfilter
        reloadParams={
            context:{
                pivot_measures:['foo'],
                pivot_column_groupby:['customer'],
                pivot_row_groupby:['product_id'],
            },
        };
        awaitpivot.reload(reloadParams);

        //CheckColumns
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_opened').length,1,
            'Thecolumnshouldbegrouped');
        assert.strictEqual(pivot.$('theadtr:contains("First")').length,1,
            'Thereshouldbeacolumn"First"');
        assert.strictEqual(pivot.$('theadtr:contains("Second")').length,1,
            'Thereshouldbeacolumn"Second"');

        //CheckRows
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_opened').length,1,
            'Therowshouldbegrouped');
        assert.strictEqual(pivot.$('tbodytr:contains("xphone")').length,1,
            'Thereshouldbearow"xphone"');
        assert.strictEqual(pivot.$('tbodytr:contains("xpad")').length,1,
            'Thereshouldbearow"xpad"');

        pivot.destroy();
    });

    QUnit.test('Reload,groupbycolumns,reload',asyncfunction(assert){
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot/>',
        });

        //Setacolumngroupby
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=customer]'));

        //Setadomain
        awaitpivot.update({domain:[['product_id','=',37]],groupBy:[],context:{}});

        varexpectedContext={pivot_column_groupby:['customer'],
                               pivot_measures:['__count'],
                               pivot_row_groupby:[]};

        //Checkthatcolumngroupbyswerenotlost
        assert.deepEqual(pivot.getOwnedQueryParams(),{context:expectedContext},
            'Columngroupbynotlostafterfirstreload');

        //Setacolumngroupby
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=product_id]'));

        //Setadomain
        awaitpivot.update({domain:[['product_id','=',41]],groupBy:[],context:{}});

        expectedContext={pivot_column_groupby:['customer','product_id'],
                           pivot_measures:['__count'],
                           pivot_row_groupby:[]};

        assert.deepEqual(pivot.getOwnedQueryParams(),{context:expectedContext},
            'Columngroupbynotlostaftersecondreload');

        pivot.destroy();
    });

    QUnit.test('foldedgroupsremainfoldedatreload',asyncfunction(assert){
        assert.expect(5);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                        '<fieldname="company_type"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        varvalues=[
            "29","3","32",
            "12",     "12",
            "17","3","20",
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        //expandacolgroup
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed:nth(1)'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="customer"]'));

        values=[
            "29","1","2","32",
            "12",          "12",
            "17","1","2","20",
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        //expandarowgroup
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed:nth(1)'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="other_product_id"]'));

        values=[
            "29","1","2","32",
            "12",          "12",
            "17","1","2","20",
            "17","1","2","20",
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        //reload(shouldkeepfoldedgroupsfoldedascol/rowgroupbysdidn'tchange)
        awaittestUtils.pivot.reload(pivot,{context:{},domain:[],groupBy:[]});

        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        awaittestUtils.dom.click(pivot.$('.o_pivot_expand_button'));

        //sanitycheckofwhatthetableshouldlooklikeifallgroupsare
        //expanded,toensurethattheformerassertsarepertinent
        values=[
            "12","17","1","2","32",
            "12",                "12",
            "12",                "12",
                  "17","1","2","20",
                  "17","1","2","20",
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));

        pivot.destroy();
    });

    QUnit.test('Emptyresultskeepgroupbys',asyncfunction(assert){
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot/>',
        });

        //Setacolumngroupby
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=customer]'));

        //Setadomainforemptyresults
        awaitpivot.update({domain:[['id','=',false]]});

        varexpectedContext={pivot_column_groupby:['customer'],
                               pivot_measures:['__count'],
                               pivot_row_groupby:[]};
        assert.deepEqual(pivot.getOwnedQueryParams(),{context:expectedContext},
            'Columngroupbynotlostafteremptyresults');

        //Setadomainfornotemptyresults
        awaitpivot.update({domain:[['product_id','=',37]]});

        assert.deepEqual(pivot.getOwnedQueryParams(),{context:expectedContext},
            'Columngroupbynotlostafterreloadafteremptyresults');

        pivot.destroy();
    });

    QUnit.test('correctlyusespivot_keysfromthecontext',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.fields.amount={string:"Amount",type:"float",group_operator:'sum'};

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="day"type="col"/>'+
                        '<fieldname="amount"type="measure"/>'+
                '</pivot>',
            viewOptions:{
                context:{
                    pivot_measures:['foo'],
                    pivot_column_groupby:['customer'],
                    pivot_row_groupby:['product_id'],
                },
            },
        });

        assert.containsOnce(pivot,'thead.o_pivot_header_cell_opened',
            "column:shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(First)').length,1,
            "column:shoulddisplayoneclosedheaderwith'First'");
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(Second)').length,1,
            "column:shoulddisplayoneclosedheaderwith'Second'");

        assert.containsOnce(pivot,'tbody.o_pivot_header_cell_opened',
            "row:shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xphone)').length,1,
            "row:shoulddisplayoneclosedheaderwith'xphone'");
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xpad)').length,1,
            "row:shoulddisplayoneclosedheaderwith'xpad'");

        assert.strictEqual(pivot.$('tbodytr:firsttd:nth(2)').text(),'32',
            "selectedmeasureshouldbefoo,withtotal32");

        pivot.destroy();
    });

    QUnit.test('cleartablecellsdataaftercloseGroup',asyncfunction(assert){
        assert.expect(2);

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot/>',
            groupBy:['product_id'],
        });

        awaittestUtils.dom.click(pivot.el.querySelector('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.el.querySelectorAll('.o_pivot_field_menu.dropdown-item[data-field="date"]')[0]);

        //closeandreopenrowgroupingsafterchangingvalue
        this.data.partner.records.find(r=>r.product_id===37).date='2016-10-27';
        awaittestUtils.dom.click(pivot.el.querySelector('tbody.o_pivot_header_cell_opened'));
        awaittestUtils.dom.click(pivot.el.querySelector('tbody.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.el.querySelector('.o_pivot_field_menu.dropdown-item[data-field="product_id"]'));
        assert.strictEqual(pivot.el.querySelectorAll('.o_pivot_cell_value')[4].innerText,'');//xphoneDecember2016

        //invertaxis,andreopencolumngroupings
        awaittestUtils.dom.click(pivot.el.querySelector('.o_cp_buttons.o_pivot_flip_button'));
        awaittestUtils.dom.click(pivot.el.querySelector('thead.o_pivot_header_cell_opened'));
        awaittestUtils.dom.click(pivot.el.querySelector('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.el.querySelector('.o_pivot_field_menu.dropdown-item[data-field="product_id"]'));
        assert.strictEqual(pivot.el.querySelectorAll('.o_pivot_cell_value')[3].innerText,'');//December2016xphone

        pivot.destroy();
    });

    QUnit.test('correctlygroupdataafterflip(1)',asyncfunction(assert){
        assert.expect(4);
        constactionManager=awaitcreateActionManager({
            data:this.data,
            archs:{
                'partner,false,pivot':"<pivot/>",
                'partner,false,search':`<search><filtername="bayou"string="Bayou"domain="[(1,'=',1)]"/></search>`,
                'partner,false,list':'<tree><fieldname="foo"/></tree>',
                'partner,false,form':'<form><fieldname="foo"/></form>',
            },
        });

        awaitactionManager.doAction({
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'pivot']],
            context:{group_by:["product_id"]},
        });

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //flipaxis
        awaittestUtils.dom.click(actionManager.el.querySelector('.o_cp_buttons.o_pivot_flip_button'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
            ]
        );

        //selectfilter"Bayou"incontrolpanel
        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"Bayou");
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //closerowheader"Total"
        awaittestUtils.dom.click(actionManager.el.querySelector('tbody.o_pivot_header_cell_opened'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total"
            ]
        );

        actionManager.destroy();
    });

    QUnit.test('correctlygroupdataafterflip(2)',asyncfunction(assert){
        assert.expect(5);
        constactionManager=awaitcreateActionManager({
            data:this.data,
            archs:{
                'partner,false,pivot':"<pivot/>",
                'partner,false,search':`<search><filtername="bayou"string="Bayou"domain="[(1,'=',1)]"/></search>`,
                'partner,false,list':'<tree><fieldname="foo"/></tree>',
                'partner,false,form':'<form><fieldname="foo"/></form>',
            },
        });

        awaitactionManager.doAction({
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'pivot']],
            context:{group_by:["product_id"]},
        });

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //selectfilter"Bayou"incontrolpanel
        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"Bayou");

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //flipaxis
        awaittestUtils.dom.click(actionManager.el.querySelector('.o_cp_buttons.o_pivot_flip_button'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total"
            ]
        );

        //unselectfilter"Bayou"incontrolpanel
        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"Bayou");
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //closerowheader"Total"
        awaittestUtils.dom.click(actionManager.el.querySelector('tbody.o_pivot_header_cell_opened'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...actionManager.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total"
            ]
        );

        actionManager.destroy();
    });

    QUnit.test('correctlygroupdataafterflip(3))',asyncfunction(assert){
        assert.expect(10);
        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:`
                <pivot>
                    <fieldname="product_id"type="row"/>
                    <fieldname="company_type"type="col"/>
                </pivot>
            `,
            archs:{
                'partner,false,search':`<search><filtername="bayou"string="Bayou"domain="[(1,'=',1)]"/></search>`,
            }
        });

        assert.deepEqual(
            [...pivot.el.querySelectorAll("theadth")].map(e=>e.innerText),
            [
                "","Total",                "",
                    "Company","individual",
                    "Count",  "Count",     "Count"
            ]
        );

        assert.deepEqual(
            [...pivot.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //closecolheader"Total"
        awaittestUtils.dom.click(pivot.el.querySelector('thead.o_pivot_header_cell_opened'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...pivot.el.querySelectorAll("theadth")].map(e=>e.innerText),
            [
                "","Total",
                    "Count"
              ]
        );
        assert.deepEqual(
            [...pivot.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //flipaxis
        awaittestUtils.dom.click(pivot.el.querySelector('.o_cp_buttons.o_pivot_flip_button'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...pivot.el.querySelectorAll("theadth")].map(e=>e.innerText),
            [
                "","Total",          "",
                    "xphone","xpad",
                    "Count", "Count","Count"
            ]
        );
        assert.deepEqual(
            [...pivot.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total"
            ]
        );

        //selectfilter"Bayou"incontrolpanel
        awaitcpHelpers.toggleFilterMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,"Bayou");
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...pivot.el.querySelectorAll("theadth")].map(e=>e.innerText),
            [
                "","Total",          "",
                    "xphone","xpad",
                    "Count", "Count","Count"
            ]
        );
        assert.deepEqual(
            [...pivot.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total",
                    "xphone",
                    "xpad"
            ]
        );

        //closerowheader"Total"
        awaittestUtils.dom.click(pivot.el.querySelector('tbody.o_pivot_header_cell_opened'));
        awaittestUtils.nextTick();

        assert.deepEqual(
            [...pivot.el.querySelectorAll("theadth")].map(e=>e.innerText),
            [
                "","Total",          "",
                    "xphone","xpad",
                    "Count", "Count","Count"
            ]
        );
        assert.deepEqual(
            [...pivot.el.querySelectorAll("tbodyth")].map(e=>e.innerText),
            [
                "Total"
            ]
        );

        pivot.destroy();
    });

    QUnit.test('correctlyusespivot_keysfromthecontext(atreload)',asyncfunction(assert){
        assert.expect(8);

        this.data.partner.fields.amount={string:"Amount",type:"float",group_operator:'sum'};

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"interval="day"type="col"/>'+
                        '<fieldname="amount"type="measure"/>'+
                '</pivot>',
        });

        assert.strictEqual(pivot.$('tbodytr:firsttd.o_pivot_cell_value:last').text(),'0.00',
            "theactivemeasureshouldbeamount");

        varreloadParams={
            context:{
                pivot_measures:['foo'],
                pivot_column_groupby:['customer'],
                pivot_row_groupby:['product_id'],
            },
        };
        awaittestUtils.pivot.reload(pivot,reloadParams);

        assert.containsOnce(pivot,'thead.o_pivot_header_cell_opened',
            "column:shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(First)').length,1,
            "column:shoulddisplayoneclosedheaderwith'First'");
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(Second)').length,1,
            "column:shoulddisplayoneclosedheaderwith'Second'");

        assert.containsOnce(pivot,'tbody.o_pivot_header_cell_opened',
            "row:shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xphone)').length,1,
            "row:shoulddisplayoneclosedheaderwith'xphone'");
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xpad)').length,1,
            "row:shoulddisplayoneclosedheaderwith'xpad'");

        assert.strictEqual(pivot.$('tbodytr:firsttd:nth(2)').text(),'32',
            "selectedmeasureshouldbefoo,withtotal32");

        pivot.destroy();
    });

    QUnit.test('correctlyusegroup_bykeyfromthecontext',asyncfunction(assert){
        assert.expect(7);

        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="customer"type="col"/>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            groupBy:['product_id'],
        });

        assert.containsOnce(pivot,'thead.o_pivot_header_cell_opened',
            'column:shouldhaveoneopenedheader');
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(First)').length,1,
            'column:shoulddisplayoneclosedheaderwith"First"');
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(Second)').length,1,
            'column:shoulddisplayoneclosedheaderwith"Second"');

        assert.containsOnce(pivot,'tbody.o_pivot_header_cell_opened',
            'row:shouldhaveoneopenedheader');
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xphone)').length,1,
            'row:shoulddisplayoneclosedheaderwith"xphone"');
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xpad)').length,1,
            'row:shoulddisplayoneclosedheaderwith"xpad"');

        assert.strictEqual(pivot.$('tbodytr:firsttd:nth(2)').text(),'32',
            'selectedmeasureshouldbefoo,withtotal32');

        pivot.destroy();
    });

    QUnit.test('correctlyusespivot_row_groupbykeywithdefaultgroupByfromthecontext',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.amount={string:"Amount",type:"float",group_operator:'sum'};

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="customer"type="col"/>'+
                        '<fieldname="date"interval="day"type="row"/>'+
                '</pivot>',
            groupBy:['customer'],
            viewOptions:{
                context:{
                    pivot_row_groupby:['product_id'],
                },
            },
        });

        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_opened').length,1,
            "column:shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(First)').length,1,
            "column:shoulddisplayoneclosedheaderwith'First'");
        assert.strictEqual(pivot.$('thead.o_pivot_header_cell_closed:contains(Second)').length,1,
            "column:shoulddisplayoneclosedheaderwith'Second'");

        //Withpivot_row_groupby,groupBycustomershouldreplaceandeventuallydisplayproduct_id
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_opened').length,1,
            "row:shouldhaveoneopenedheader");
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xphone)').length,1,
            "row:shoulddisplayoneclosedheaderwith'xphone'");
        assert.strictEqual(pivot.$('tbody.o_pivot_header_cell_closed:contains(xpad)').length,1,
            "row:shoulddisplayoneclosedheaderwith'xpad'");

        pivot.destroy();
    });

    QUnit.test('pivotstillhandles__count__measure',asyncfunction(assert){
        //forretro-compatibilityreasons,thepivotviewstillhandles
        //'__count__'measure.
        assert.expect(2);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot></pivot>',
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    assert.deepEqual(args.kwargs.fields,['__count'],
                        "shouldmakearead_groupwithfield__count");
                }
                returnthis._super(route,args);
            },
            viewOptions:{
                context:{
                    pivot_measures:['__count__'],
                },
            },
        });

        var$countMeasure=pivot.$buttons.find('.dropdown-item[data-field=__count]:first');
        assert.hasClass($countMeasure,'selected',"Thecountmeasureshouldbeactivated");

        pivot.destroy();
    });

    QUnit.test('notuseamany2oneasameasurebydefault',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="date"interval="month"type="col"/>'+
                '</pivot>',
        });
        assert.notOk(pivot.measures.product_id,
            "shouldnothaveproduct_idasmeasure");
        pivot.destroy();
    });

    QUnit.test('useamany2oneasameasurewithspecifiedadditionalmeasure',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="date"interval="month"type="col"/>'+
                '</pivot>',
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });
        assert.ok(pivot.measures.product_id,
            "shouldhaveproduct_idasmeasure");
        pivot.destroy();
    });

    QUnit.test('pivotviewwithmany2onefieldasameasure',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="measure"/>'+
                        '<fieldname="date"interval="month"type="col"/>'+
                '</pivot>',
        });

        assert.strictEqual(pivot.$('tabletbodytr').text().trim(),"Total2112",
            "shoulddisplayproduct_idcountasmeasure");
        pivot.destroy();
    });

    QUnit.test('m2oasmeasure,drillingdownintodata',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="measure"/>'+
                '</pivot>',
        });
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed'));
        //clickondatebymonth
        pivot.$('.dropdown-menu.show.o_inline_dropdown.dropdown-menu').toggle();//unfoldinlinedropdown
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="date"]:contains("Month")'));

        assert.strictEqual(pivot.$('.o_pivot_cell_value').text(),'2211',
            'shouldhaveloadedtheproperdata');
        pivot.destroy();
    });

    QUnit.test('pivotviewwithsamemany2onefieldasameasureandgroupedby',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                '</pivot>',
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });

        awaittestUtils.pivot.toggleMeasuresDropdown(pivot);
        awaittestUtils.pivot.clickMeasure(pivot,'product_id');
        assert.strictEqual(pivot.$('.o_pivot_cell_value').text(),'421131',
            'shouldhaveloadedtheproperdata');
        pivot.destroy();
    });

    QUnit.test('pivotviewwithsamemany2onefieldasameasureandgroupedby(anddrilldown)',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="measure"/>'+
                '</pivot>',
        });

        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed'));

        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field="product_id"]:first'));

        assert.strictEqual(pivot.$('.o_pivot_cell_value').text(),'211',
            'shouldhaveloadedtheproperdata');
        pivot.destroy();
    });

    QUnit.test('Rowandcolumngroupbysplusadomain',asyncfunction(assert){
        assert.expect(3);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="foo"type="measure"/>'+
                '</pivot>',
        });

        //Setacolumngroupby
        awaittestUtils.dom.click(pivot.$('thead.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=customer]:first'));

        //SetaRowgroupby
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=product_id]:first'));

        //Setadomain
        awaittestUtils.pivot.reload(pivot,{domain:[['product_id','=',41]]});

        varexpectedContext={
            context:{
                pivot_column_groupby:['customer'],
                pivot_measures:['foo'],
                pivot_row_groupby:['product_id'],
            },
        };

        //Mock'saveasfavorite'
        assert.deepEqual(pivot.getOwnedQueryParams(),expectedContext,
            'Thepivotviewshouldhavetherightcontext');

        var$xpadHeader=pivot.$('tbody.o_pivot_header_cell_closed[data-original-title=Product]');
        assert.equal($xpadHeader.length,1,
            'Thereshouldbeonlyoneproductlinebecauseofthedomain');

        assert.equal($xpadHeader.text(),'xpad',
            'Theproductshouldbetherightone');

        pivot.destroy();
    });

    QUnit.test('paralleldataloadingshoulddiscardallbutthelastone',asyncfunction(assert){
        assert.expect(2);

        vardef;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                      '<fieldname="foo"type="measure"/>'+
                  '</pivot>',
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read_group'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        def=testUtils.makeTestPromise();
        testUtils.pivot.reload(pivot,{groupBy:['product_id']});
        testUtils.pivot.reload(pivot,{groupBy:['product_id','customer']});
        awaitdef.resolve();
        awaittestUtils.nextTick();
        assert.containsN(pivot,'.o_pivot_cell_value',6,
            "shouldhave6cells");
        assert.containsN(pivot,'tbodytr',6,
            "shouldhave6rows");
        pivot.destroy();
    });

    QUnit.test('pivotmeasuresshouldbealphabeticallysorted',asyncfunction(assert){
        assert.expect(2);

        vardata=this.data;
        //It'simportanttocomparecapitalizedandlowercasedwords
        //tobesurethesortingiseffectivewithbothofthem
        data.partner.fields.bouh={string:"bouh",type:"integer",group_operator:'sum'};
        data.partner.fields.modd={string:"modd",type:"integer",group_operator:'sum'};
        data.partner.fields.zip={string:"Zip",type:"integer",group_operator:'sum'};

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:data,
            arch:'<pivot>'+
                        '<fieldname="zip"type="measure"/>'+
                        '<fieldname="foo"type="measure"/>'+
                        '<fieldname="bouh"type="measure"/>'+
                        '<fieldname="modd"type="measure"/>'+
                  '</pivot>',
        });
        assert.strictEqual(pivot.$buttons.find('.o_pivot_measures_list.dropdown-item:first').data('field'),'bouh',
            "Bouhshouldbethefirstmeasure");
        assert.strictEqual(pivot.$buttons.find('.o_pivot_measures_list.dropdown-item:last').data('field'),'__count',
            "Countshouldbethelastmeasure");

        pivot.destroy();
    });

    QUnit.test('pivotviewshouldusedefaultorderforautosorting',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivotdefault_order="fooasc">'+
                        '<fieldname="foo"type="measure"/>'+
                  '</pivot>',
        });

        assert.hasClass(pivot.$('theadtr:lastth:last'),'o_pivot_sort_order_asc',
                        "Lasttheadshouldbesortedinascendingorder");

        pivot.destroy();
    });

    QUnit.test('pivotviewcanbeflipped',asyncfunction(assert){
        assert.expect(5);

        varrpcCount=0;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="product_id"type="row"/>'+
                '</pivot>',
            mockRPC:function(){
                rpcCount++;
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(pivot,'tbodytr',3,
            "shouldhave3rows:1fortheopenheader,and2fordata");
        varvalues=[
            "4",
            "1",
            "3"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        rpcCount=0;
        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_flip_button'));

        assert.strictEqual(rpcCount,0,"shouldnothavedoneanyrpc");
        assert.containsOnce(pivot,'tbodytr',
            "shouldhave1rows:1forthemainheader");

        values=[
            "1","3","4"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        pivot.destroy();
    });

    QUnit.test('renderingofpivotviewwithcomparison',asyncfunction(assert){
        assert.expect(8);

        this.data.partner.records[0].date='2016-12-15';
        this.data.partner.records[1].date='2016-12-17';
        this.data.partner.records[2].date='2016-11-22';
        this.data.partner.records[3].date='2016-11-03';


        varunpatchDate=patchDate(2016,11,20,1,0,0);

        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="date"interval="month"type="col"/>'+
                    '<fieldname="foo"type="measure"/>'+
              '</pivot>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='last_year'/>
                    </search>
                `,
            },
            viewOptions:{
                additionalMeasures:['product_id'],
                context:{search_default_date_filter:1},
            },
            mockRPC:function(){
                returnthis._super.apply(this,arguments);
            },
            env:{
                dataManager:{
                    create_filter:asyncfunction(filter){
                        assert.deepEqual(filter.context,{
                            pivot_measures:['__count'],
                            pivot_column_groupby:[],
                            pivot_row_groupby:['product_id'],
                            group_by:[],
                            comparison:{
                                comparisonId:"previous_period",
                                comparisonRange:"[\"&\",[\"date\",\">=\",\"2016-11-01\"],[\"date\",\"<=\",\"2016-11-30\"]]",
                                comparisonRangeDescription:"November2016",
                                fieldDescription:"Date",
                                fieldName:"date",
                                range:"[\"&\",[\"date\",\">=\",\"2016-12-01\"],[\"date\",\"<=\",\"2016-12-31\"]]",
                                rangeDescription:"December2016"
                              },
                        });
                    }
                }
            },
        });

        //withnodata
        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        assert.strictEqual(pivot.$('.o_pivotp.o_view_nocontent_empty_folder').length,1);

        awaitcpHelpers.toggleFilterMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date');
        awaitcpHelpers.toggleMenuItemOption(pivot,'Date','December');
        awaitcpHelpers.toggleMenuItemOption(pivot,'Date','2016');
        awaitcpHelpers.toggleMenuItemOption(pivot,'Date','2015');

        assert.containsN(pivot,'.o_pivottheadtr:lastth',9,
            "lastheaderrowshouldcontains9cells(3*[December2016,November2016,Variation]");
        varvalues=[
            "19","0","-100%","0","13","100%","19","13","-31.58%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //withdata,withrowgroupby
        awaittestUtils.dom.click(pivot.$('.o_pivot.o_pivot_header_cell_closed').eq(2));
        awaittestUtils.dom.click(pivot.$('.o_pivot.o_pivot_field_menua[data-field="product_id"]'));
        values=[
            "19","0","-100%","0","13","100%","19","13","-31.58%",
            "19","0","-100%","0","1","100%","19","1","-94.74%",
                                "0","12","100%","0","12","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        awaittestUtils.pivot.toggleMeasuresDropdown(pivot);
        awaittestUtils.dom.click(pivot.$('.o_control_paneldiv.o_pivot_measures_lista[data-field="foo"]'));
        awaittestUtils.dom.click(pivot.$('.o_control_paneldiv.o_pivot_measures_lista[data-field="product_id"]'));
        values=[
            "1","0","-100%","0","2","100%","1","2","100%",
            "1","0","-100%","0","1","100%","1","1","0%",
                               "0","1","100%","0","1","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        awaittestUtils.dom.click(pivot.$('.o_control_paneldiv.o_pivot_measures_lista[data-field="__count"]'));
        awaittestUtils.dom.click(pivot.$('.o_control_paneldiv.o_pivot_measures_lista[data-field="product_id"]'));
        values=[
            "2","0","-100%","0","2","100%","2","2","0%",
            "2","0","-100%","0","1","100%","2","1","-50%",
                               "0","1","100%","0","1","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        awaittestUtils.dom.clickFirst(pivot.$('.o_pivot.o_pivot_header_cell_opened'));
        values=[
            "2","2","0%",
            "2","1","-50%",
            "0","1","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        awaitcpHelpers.toggleFavoriteMenu(pivot);
        awaitcpHelpers.toggleSaveFavorite(pivot);
        awaitcpHelpers.editFavoriteName(pivot,'Fav');
        awaitcpHelpers.saveFavorite(pivot);

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('exportdatainexcelwithcomparison',asyncfunction(assert){
        assert.expect(11);

        this.data.partner.records[0].date='2016-12-15';
        this.data.partner.records[1].date='2016-12-17';
        this.data.partner.records[2].date='2016-11-22';
        this.data.partner.records[3].date='2016-11-03';

        varunpatchDate=patchDate(2016,11,20,1,0,0);

        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="date"interval="month"type="col"/>'+
                    '<fieldname="foo"type="measure"/>'+
              '</pivot>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='antepenultimate_month'/>
                    </search>
                `,
            },
            viewOptions:{
                context:{search_default_date_filter:1},
            },
            session:{
                get_file:function(args){
                    vardata=JSON.parse(args.data.data);
                    _.each(data.col_group_headers,function(l){
                        vartitles=l.map(function(o){
                            returno.title;
                        });
                        assert.step(JSON.stringify(titles));
                    });
                    varmeasures=data.measure_headers.map(function(o){
                        returno.title;
                    });
                    assert.step(JSON.stringify(measures));
                    varorigins=data.origin_headers.map(function(o){
                        returno.title;
                    });
                    assert.step(JSON.stringify(origins));
                    assert.step(String(data.measure_count));
                    assert.step(String(data.origin_count));
                    varvaluesLength=data.rows.map(function(o){
                        returno.values.length;
                    });
                    assert.step(JSON.stringify(valuesLength));
                    assert.strictEqual(args.url,'/web/pivot/export_xlsx',
                        "shouldcallget_filewithcorrectparameters");
                    args.complete();
                },
            },
        });

        //opencomparisonmenu
        awaitcpHelpers.toggleComparisonMenu(pivot);
        //compareOctober2016toSeptember2016
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        //Withthedataabove,thetimerangescontainnorecord.
        assert.strictEqual(pivot.$('.o_pivotp.o_view_nocontent_empty_folder').length,1,"thereshouldbenodata");
        //exportdatashouldbeimpossiblesincethepivotbuttons
        //aredeactivated(exception:the'Measures'button).
        assert.ok(pivot.$('.o_control_panelbutton.o_pivot_download').prop('disabled'));

        awaitcpHelpers.toggleFilterMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date');
        awaitcpHelpers.toggleMenuItemOption(pivot,'Date','December');
        awaitcpHelpers.toggleMenuItemOption(pivot,'Date','October');

        //Withthedataabove,thetimerangescontainsomerecords.
        //exportdata.Shouldexecute'get_file'
        awaittestUtils.dom.click(pivot.$('.o_control_panelbutton.o_pivot_download'));

        assert.verifySteps([
            //colgroupheaders
            '["Total",""]',
            '["November2016","December2016"]',
            //measureheaders
            '["Foo","Foo","Foo"]',
            //originheaders
            '["November2016","December2016","Variation","November2016","December2016"'+
                ',"Variation","November2016","December2016","Variation"]',
            //numberof'measures'
            '1',
            //numberof'origins'
            '2',
            //rowsvalueslength
            '[9]',
        ]);

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('renderingofpivotviewwithcomparisonandcountmeasure',asyncfunction(assert){
        assert.expect(2);

        varmockMock=false;
        varnbReadGroup=0;

        this.data.partner.records[0].date='2016-12-15';
        this.data.partner.records[1].date='2016-12-17';
        this.data.partner.records[2].date='2016-12-22';
        this.data.partner.records[3].date='2016-12-03';

        varunpatchDate=patchDate(2016,11,20,1,0,0);

        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot><fieldname="customer"type="row"/></pivot>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='this_month'/>
                    </search>
                `,
            },
            viewOptions:{
                context:{search_default_date_filter:1},
            },
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read_group'&&mockMock){
                    nbReadGroup++;
                    if(nbReadGroup===4){
                        //thismodificationisnecessarybecausemockReadGroupdoesnot
                        //properlyreflecttheserverresponsewhenthereisnorecord
                        //andagroupbylistoflengthatleastone.
                        returnPromise.resolve([{}]);
                    }
                }
                returnresult;
            },
        });

        mockMock=true;

        //compareDecember2016toNovember2016
        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        varvalues=[
            "0","4","100%",
            "0","2","100%",
            "0","2","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join(','));
        assert.strictEqual(pivot.$('.o_pivot_header_cell_closed').length,3,
            "thereshouldbeexactlythreeclosedheader('Total','First','Second')");

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('cansortapivotviewwithcomparisonbyclickingonheader',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records[0].date='2016-12-15';
        this.data.partner.records[1].date='2016-12-17';
        this.data.partner.records[2].date='2016-11-22';
        this.data.partner.records[3].date='2016-11-03';

        varunpatchDate=patchDate(2016,11,20,1,0,0);
        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="date"interval="day"type="row"/>'+
                    '<fieldname="company_type"type="col"/>'+
                    '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='this_month'/>
                    </search>
                `,
            },
            viewOptions:{
                additionalMeasures:['product_id'],
                context:{search_default_date_filter:1},
            },
        });

        //compareDecember2016toNovember2016
        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        //initialsanitycheck
        varvalues=[
            "17","12","-29.41%","2","1","-50%","19","13","-31.58%",
            "17","0","-100%",                     "17","0","-100%",
                                   "2","0","-100%","2","0","-100%",
            "0","12","100%",                      "0","12","100%",
                                   "0","1","100%","0","1","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //clickon'Foo'incolumnTotal/Company(shouldsortbytheperiodofinterest,ASC)
        awaittestUtils.dom.click(pivot.$('.o_pivot_measure_row').eq(0));
        values=[
            "17","12","-29.41%","2","1","-50%","19","13","-31.58%",
                                   "2","0","-100%","2","0","-100%",
            "0","12","100%",                       "0","12","100%",
                                   "0","1","100%","0","1","100%",
            "17","0","-100%",                     "17","0","-100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //clickagainon'Foo'incolumnTotal/Company(shouldsortbytheperiodofinterest,DESC)
        awaittestUtils.dom.click(pivot.$('.o_pivot_measure_row').eq(0));
        values=[
            "17","12","-29.41%","2","1","-50%","19","13","-31.58%",
            "17","0","-100%",                     "17","0","-100%",
                                   "2","0","-100%","2","0","-100%",
            "0","12","100%",                      "0","12","100%",
                                   "0","1","100%","0","1","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //clickon'ThisMonth'incolumnTotal/Individual/Foo
        awaittestUtils.dom.click(pivot.$('.o_pivot_origin_row').eq(3));
        values=[
            "17","12","-29.41%","2","1","-50%","19","13","-31.58%",
            "17","0","-100%",                     "17","0","-100%",
            "0","12","100%",                      "0","12","100%",
                                   "0","1","100%","0","1","100%",
                                   "2","0","-100%", "2","0", "-100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //clickon'PreviousPeriod'incolumnTotal/Individual/Foo
        awaittestUtils.dom.click(pivot.$('.o_pivot_origin_row').eq(4));
        values=[
            "17","12","-29.41%","2","1","-50%","19","13","-31.58%",
            "17","0","-100%",                     "17","0","-100%",
                                   "2","0","-100%","2","0","-100%",
            "0","12","100%",                      "0","12","100%",
                                   "0","1","100%","0","1","100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //clickon'Variation'incolumnTotal/Foo
        awaittestUtils.dom.click(pivot.$('.o_pivot_origin_row').eq(8));
        values=[
            "17","12","-29.41%","2","1","-50%", "19","13","-31.58%",
            "17", "0","-100%",                     "17", "0","-100%",
                                   "2","0","-100%","2","0","-100%",
            "0","12", "100%",                      "0","12","100%",
                                   "0","1","100%", "0","1", "100%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('Clickonthemeasurelistbutnotonamenuitem',asyncfunction(assert){
        assert.expect(2);

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:`<pivot/>`,
        });

        //openthe"Measures"menu
        awaittestUtils.dom.click(pivot.el.querySelector('.o_cp_buttonsbutton'));

        //clickonthedividerinthe"Measures"menudoesnotcrash
        awaittestUtils.dom.click(pivot.el.querySelector('.o_pivot_measures_list.dropdown-divider'));
        //themenushouldstillbeopen
        assert.isVisible(pivot.el.querySelector('.o_pivot_measures_list'));

        //clickonthemeasurelistbutnotonamenuitemortheseparator
        awaittestUtils.dom.click(pivot.el.querySelector('.o_pivot_measures_list'));
        //themenushouldstillbeopen
        assert.isVisible(pivot.el.querySelector('.o_pivot_measures_list'));

        pivot.destroy();
    });

    QUnit.test('Navigationlistviewforagroupandbackwithbreadcrumbs',asyncfunction(assert){
        assert.expect(16);
        //createanactionmanagertotesttheinteractionswiththesearchview
        varreadGroupCount=0;

        varactionManager=awaitcreateActionManager({
            data:this.data,
            archs:{
                'partner,false,pivot':'<pivot>'+
                        '<fieldname="customer"type="row"/>'+
                  '</pivot>',
                'partner,false,search':'<search><filtername="bayou"string="Bayou"domain="[(\'foo\',\'=\',12)]"/></search>',
                'partner,false,list':'<tree><fieldname="foo"/></tree>',
                'partner,false,form':'<form><fieldname="foo"/></form>',
            },
            intercepts:{
                do_action:function(event){
                    varaction=event.data.action;
                    actionManager.doAction(action);
                }
            },
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    assert.step('read_group');
                    constdomain=args.kwargs.domain;
                    if([0,1].indexOf(readGroupCount)!==-1){
                        assert.deepEqual(domain,[],'domainempty');
                    }elseif([2,3,4,5].indexOf(readGroupCount)!==-1){
                        assert.deepEqual(domain,[['foo','=',12]],
                            'domainconservedwhenbackwithbreadcrumbs');
                    }
                    readGroupCount++;
                }
                if(route==='/web/dataset/search_read'){
                    assert.step('search_read');
                    constdomain=args.domain;
                    assert.deepEqual(domain,['&',['customer','=',1],['foo','=',12]],
                        'listdomainiscorrect');
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaitactionManager.doAction({
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'pivot']],
        });


        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,0);
        awaittestUtils.nextTick();

        awaittestUtilsDom.click(actionManager.$('.o_pivot_cell_value:nth(1)'));
        awaittestUtils.nextTick();

        assert.containsOnce(actionManager,'.o_list_view');

        awaittestUtilsDom.click(actionManager.$('.o_control_panelol.breadcrumbli.breadcrumb-item').eq(0));

        assert.verifySteps([
            'read_group','read_group',
            'read_group','read_group',
            'search_read',
            'read_group','read_group']);
        actionManager.destroy();
    });

    QUnit.test('Cellvaluesarekeptwhenflippinapivotviewincomparisonmode',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].date='2016-12-15';
        this.data.partner.records[1].date='2016-12-17';
        this.data.partner.records[2].date='2016-11-22';
        this.data.partner.records[3].date='2016-11-03';

        varunpatchDate=patchDate(2016,11,20,1,0,0);
        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="date"interval="day"type="row"/>'+
                    '<fieldname="company_type"type="col"/>'+
                    '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='this_month'/>
                    </search>
                `,
            },
            viewOptions:{
                additionalMeasures:['product_id'],
                context:{search_default_date_filter:1},
            },
        });

        //compareDecember2016toNovember2016
        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        //initialsanitycheck
        varvalues=[
            "17","12","-29.41%","2","1","-50%","19","13","-31.58%",
            "17","0","-100%",                     "17","0","-100%",
                                   "2","0","-100%","2","0","-100%",
            "0","12","100%",                      "0","12","100%",
                                   "0","1","100%","0","1","100%",


        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        //fliptable
        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_flip_button'));

        values=[
            "17","0","-100%","2","0","-100%","0","12","100%","0","1","100%","19","13","-31.58%",
            "17","0","-100%",                   "0","12","100%",                  "17","12","-29.41%",
                                "2","0","-100%",                   "0", "1","100%","2", "1", "-50%"
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('Flipthencompare,tablecolgroupbysarekept',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records[0].date='2016-12-15';
        this.data.partner.records[1].date='2016-12-17';
        this.data.partner.records[2].date='2016-11-22';
        this.data.partner.records[3].date='2016-11-03';

        varunpatchDate=patchDate(2016,11,20,1,0,0);
        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="date"interval="day"type="row"/>'+
                    '<fieldname="company_type"type="col"/>'+
                    '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="date_filter"date="date"domain="[]"default_period='this_month'/>
                    </search>
                `,
            },
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });


        assert.strictEqual(
            pivot.$('th').slice(0,5).text(),
            [
                '','Total',                '',
                    'Company','individual',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(8).text(),
            [
                'Total',
                    '2016-12-15',
                    '2016-12-17',
                    '2016-11-22',
                    '2016-11-03'
            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        //flip
        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_flip_button'));

        assert.strictEqual(
            pivot.$('th').slice(0,7).text(),
            [
                '','Total',                                               '',
                    '2016-12-15','2016-12-17','2016-11-22','2016-11-03',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(12).text(),
            [
                'Total',
                    'Company',
                    'individual'

            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        //FilteronDecember2016
        awaitcpHelpers.toggleFilterMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date');
        awaitcpHelpers.toggleMenuItemOption(pivot,'Date','December');

        //compareDecember2016toNovember2016
        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,'Date:Previousperiod');

        assert.strictEqual(
            pivot.$('th').slice(0,7).text(),
            [
                '','Total',                                               '',
                    '2016-11-22','2016-11-03','2016-12-15','2016-12-17',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(27).text(),
            [
                'Total',
                    'Company',
                    'individual'

            ].join(''),
            "Therowheadersshouldbeasexpected"
        );
        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('correctlycomputegroupdomainwhenadatefieldhasfalsevalue',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records.forEach(r=>r.date=false);

        varunpatchDate=patchDate(2016,11,20,1,0,0);
        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivoto_enable_linking="1">'+
                    '<fieldname="date"interval="day"type="row"/>'+
                '</pivot>',
            intercepts:{
                do_action:function(ev){
                    assert.deepEqual(ev.data.action.domain,[['date','=',false]]);
                },
            },
        });

        awaittestUtils.dom.click($('div.o_value')[1]);

        unpatchDate();
        pivot.destroy();
    });
    QUnit.test('Doesnotidentify"false"withfalseaskeyswhencreatinggrouptrees',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.favorite_animal={string:"Favoriteanimal",type:"char",store:true};
        this.data.partner.records[0].favorite_animal='Dog';
        this.data.partner.records[1].favorite_animal='false';
        this.data.partner.records[2].favorite_animal='Undefined';

        varunpatchDate=patchDate(2016,11,20,1,0,0);
        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivoto_enable_linking="1">'+
                    '<fieldname="favorite_animal"type="row"/>'+
                '</pivot>',

        });

        assert.strictEqual(
            pivot.$('th').slice(0,2).text(),
            [
                '','Total',                                               '',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(3).text(),
            [
                'Total',
                    'Dog',
                    'false',
                    'Undefined',
                    'Undefined'

            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        unpatchDate();
        pivot.destroy();
    });

    QUnit.test('groupbysaddedviacontrolpanelandexpandHeaderdonotstack',asyncfunction(assert){
        assert.expect(8);

        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });

        assert.strictEqual(
            pivot.$('th').slice(0,2).text(),
            [
                '','Total',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(3).text(),
            [
                'Total',
            ].join(''),
            "Therowheadersshouldbeasexpected"
        );


        //opengroupbymenuandaddnewgroupby
        awaitcpHelpers.toggleGroupByMenu(pivot);
        awaitcpHelpers.toggleAddCustomGroup(pivot);
        awaitcpHelpers.applyGroup(pivot);

        assert.strictEqual(
            pivot.$('th').slice(0,2).text(),
            [
                '','Total',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(3).text(),
            [
                'Total',
                    'Company',
                    'individual'
            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        //SetaRowgroupby
        awaittestUtils.dom.click(pivot.$('tbody.o_pivot_header_cell_closed').eq(0));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=product_id]:first'));

        assert.strictEqual(
            pivot.$('th').slice(0,2).text(),
            [
                '','Total',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(3).text(),
            [
                'Total',
                    'Company',
                        'xphone',
                        'xpad',
                    'individual'
            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        //opengroupbymenugeneratorandaddanewgroupby
        awaitcpHelpers.toggleGroupByMenu(pivot);
        awaitcpHelpers.toggleAddCustomGroup(pivot);
        awaitcpHelpers.selectGroup(pivot,'bar');
        awaitcpHelpers.applyGroup(pivot);

        assert.strictEqual(
            pivot.$('th').slice(0,2).text(),
            [
                '','Total',
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );
        assert.strictEqual(
            pivot.$('th').slice(3).text(),
            [
                'Total',
                    'Company',
                        'true',
                    'individual',
                        'true',
                        'Undefined'
            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        pivot.destroy();
    });

    QUnit.test('displayonlyonedropdownmenu',asyncfunction(assert){
        assert.expect(1);

        varpivot=awaitcreateView({
            View:PivotView,
            model:'partner',
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            viewOptions:{
                additionalMeasures:['product_id'],
            },
        });
        awaittestUtils.dom.clickFirst(pivot.$('th.o_pivot_header_cell_closed'));
        awaittestUtils.dom.click(pivot.$('.o_pivot_field_menu.dropdown-item[data-field=product_id]:first'));

        //Clickonthetwodropdown
        awaittestUtils.dom.click(pivot.$('th.o_pivot_header_cell_closed')[0]);
        awaittestUtils.dom.click(pivot.$('th.o_pivot_header_cell_closed')[1]);

        assert.containsOnce(pivot,'.o_pivot_field_menu','Onlyonedropdownshouldbedisplayedatatime');

        pivot.destroy();
    });

    QUnit.test('Serverorderiskeptbydefault',asyncfunction(assert){
        assert.expect(1);

        letisSecondReadGroup=false;

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                    '<fieldname="customer"type="row"/>'+
                    '<fieldname="foo"type="measure"/>'+
                '</pivot>',
            mockRPC:function(route,args){
                if(args.method==='read_group'&&isSecondReadGroup){
                    returnPromise.resolve([
                        {
                            customer:[2,'Second'],
                            foo:18,
                            __count:2,
                            __domain:[["customer","=",2]],
                        },
                        {
                            customer:[1,'First'],
                            foo:14,
                            __count:2,
                            __domain:[["customer","=",1]],
                        }
                    ]);
                }
                varresult=this._super.apply(this,arguments);
                isSecondReadGroup=true;
                returnresult;
            },
        });

        constvalues=[
            "32",//TotalValue
            "18",//Second
            "14",//First
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        pivot.destroy();
    });

    QUnit.test('comparisonwithtwogroupbys:rowsfromreferenceperiodshouldbedisplayed',asyncfunction(assert){
        assert.expect(3);
        patchDate(2023,2,22,1,0,0);

        this.data.partner.records=[
            {id:1,date:"2021-10-10",product_id:1,customer:1},
            {id:2,date:"2020-10-10",product_id:2,customer:1},
        ]
        this.data.product.records=[
            {id:1,display_name:"A"},
            {id:2,display_name:"B"},
        ]
        this.data.customer.records=[
            {id:1,display_name:"P"},
        ]

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot><fieldname="customer"type="row"/><fieldname="product_id"type="row"/></pivot>',
            archs:{
                "partner,false,search":"<search><filtername='date'date='date'/></search>"
            },
        });

        //compare2021to2020
        awaitcpHelpers.toggleFilterMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,"Date");
        awaitcpHelpers.toggleMenuItemOption(pivot,"Date","2021");
        awaitcpHelpers.toggleComparisonMenu(pivot);
        awaitcpHelpers.toggleMenuItem(pivot,0);

        assert.strictEqual(
            pivot.$('th').slice(0,6).text(),
            [
                        "Total",
                        "Count",
                "2020","2021","Variation"
            ].join(''),
            "Thecolheadersshouldbeasexpected"
        );

        assert.strictEqual(
            pivot.$('th').slice(6).text(),
            [
                'Total',
                    'P',
                        'B',
                        'A',
            ].join(''),
            "Therowheadersshouldbeasexpected"
        );

        constvalues=[
            "1","1","0%",
            "1","1","0%",
            "1","0","-100%",
            "0","1","100%",
        ];
        assert.strictEqual(getCurrentValues(pivot),values.join());

        pivot.destroy();
    });

    QUnit.test('pivotrenderingwithbooleanfield',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.bar={string:"bar",type:"boolean",store:true,searchable:true,group_operator:'bool_or'};
        this.data.partner.records=[{id:1,bar:true,date:'2019-12-14'},{id:2,bar:false,date:'2019-05-14'}];

        varpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"type="row"interval="day"/>'+
                        '<fieldname="bar"type="col"/>'+
                        '<fieldname="bar"string="SLAstatusFailed"type="measure"/>'+
                '</pivot>',
        });

        assert.strictEqual(pivot.$('tbodytr:contains("2019-12-14")').length,1,'Thereshouldbeafirstcolumn');
        assert.ok(pivot.$('tbodytr:contains("2019-12-14")[type="checkbox"]').is(':checked'),'firstcolumncontainscheckboxandvalueshouldbeticked');
        assert.strictEqual(pivot.$('tbodytr:contains("2019-05-14")').length,1,'Thereshouldbeasecondcolumn');
        assert.notOk(pivot.$('tbodytr:contains("2019-05-14")[type="checkbox"]').is(':checked'),"secondcolumnshouldhavecheckboxthatisnotcheckedbydefault");

        pivot.destroy();
    });

    QUnit.test('Allowtoaddbehaviourtobuttonsonpivot',asyncfunction(assert){
        assert.expect(2);

        let_testButtons=(ev)=>{
            if($(ev.target).hasClass("o_pivot_flip_button")){
                assert.step("o_pivot_flip_button")
            }
        }

        PivotController.include({
            _addIncludedButtons:asyncfunction(ev){
                awaitthis._super(...arguments);
                _testButtons(ev);
            },
        });

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:'<pivot>'+
                        '<fieldname="date"type="row"interval="day"/>'+
                        '<fieldname="bar"type="col"/>'+
                '</pivot>',
        });
        awaittestUtils.dom.click(pivot.$buttons.find('.o_pivot_flip_button'));
        assert.verifySteps(["o_pivot_flip_button"]);
        _testButtons=()=>true;
        pivot.destroy();
    });

    QUnit.test('emptypivotviewwithactionhelper',asyncfunction(assert){
        assert.expect(4);

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:`
                <pivot>
                    <fieldname="product_id"type="measure"/>
                    <fieldname="date"interval="month"type="col"/>
                </pivot>`,
            domain:[['id','<',0]],
            viewOptions:{
                action:{
                    help:'<pclass="abc">clicktoaddafoo</p>'
                }
            },
        });

        assert.containsOnce(pivot,'.o_view_nocontent.abc');
        assert.containsNone(pivot,'table');

        awaitpivot.reload({domain:[]});

        assert.containsNone(pivot,'.o_view_nocontent.abc');
        assert.containsOnce(pivot,'table');

        pivot.destroy();
    });

    QUnit.test('emptypivotviewwithsampledata',asyncfunction(assert){
        assert.expect(7);

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:`
                <pivotsample="1">
                    <fieldname="product_id"type="measure"/>
                    <fieldname="date"interval="month"type="col"/>
                </pivot>`,
            domain:[['id','<',0]],
            viewOptions:{
                action:{
                    help:'<pclass="abc">clicktoaddafoo</p>'
                }
            },
        });

        assert.hasClass(pivot.el,'o_view_sample_data');
        assert.containsOnce(pivot,'.o_view_nocontent.abc');
        assert.containsOnce(pivot,'table.o_sample_data_disabled');

        awaitpivot.reload({domain:[]});

        assert.doesNotHaveClass(pivot.el,'o_view_sample_data');
        assert.containsNone(pivot,'.o_view_nocontent.abc');
        assert.containsOnce(pivot,'table');
        assert.doesNotHaveClass(pivot.$('table'),'o_sample_data_disabled');

        pivot.destroy();
    });

    QUnit.test('nonemptypivotviewwithsampledata',asyncfunction(assert){
        assert.expect(7);

        constpivot=awaitcreateView({
            View:PivotView,
            model:"partner",
            data:this.data,
            arch:`
                <pivotsample="1">
                    <fieldname="product_id"type="measure"/>
                    <fieldname="date"interval="month"type="col"/>
                </pivot>`,
            viewOptions:{
                action:{
                    help:'<pclass="abc">clicktoaddafoo</p>'
                }
            },
        });

        assert.doesNotHaveClass(pivot.el,'o_view_sample_data');
        assert.containsNone(pivot,'.o_view_nocontent.abc');
        assert.containsOnce(pivot,'table');
        assert.doesNotHaveClass(pivot.$('table'),'o_sample_data_disabled');

        awaitpivot.reload({domain:[['id','<',0]]});

        assert.doesNotHaveClass(pivot.el,'o_view_sample_data');
        assert.containsOnce(pivot,'.o_view_nocontent.abc');
        assert.containsNone(pivot,'table');

        pivot.destroy();
    });
});
});
