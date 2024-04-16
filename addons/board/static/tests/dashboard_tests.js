flectra.define('board.dashboard_tests',function(require){
"usestrict";

varBoardView=require('board.BoardView');

varListController=require('web.ListController');
vartestUtils=require('web.test_utils');
varListRenderer=require('web.ListRenderer');
varpyUtils=require('web.py_utils');

constcpHelpers=testUtils.controlPanel;
varcreateActionManager=testUtils.createActionManager;
varcreateView=testUtils.createView;

constpatchDate=testUtils.mock.patchDate;

QUnit.module('Dashboard',{
    beforeEach:function(){
        this.data={
            board:{
                fields:{
                },
                records:[
                ]
            },
            partner:{
                fields:{
                    display_name:{string:"Displayedname",type:"char",searchable:true},
                    foo:{string:"Foo",type:"char",default:"MylittleFooValue",searchable:true},
                    bar:{string:"Bar",type:"boolean"},
                    int_field:{string:"Integerfield",type:"integer",group_operator:'sum'},
                },
                records:[{
                    id:1,
                    display_name:"firstrecord",
                    foo:"yop",
                    int_field:3,
                },{
                    id:2,
                    display_name:"secondrecord",
                    foo:"lalala",
                    int_field:5,
                },{
                    id:4,
                    display_name:"aaa",
                    foo:"abc",
                    int_field:2,
                }],
            },
        };
    },
});

QUnit.test('dashboardbasicrendering',asyncfunction(assert){
    assert.expect(4);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
            '</form>',
    });

    assert.doesNotHaveClass(form.renderer.$el,'o_dashboard',
        "shouldnothavetheo_dashboardcssclass");

    form.destroy();

    form=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column></column>'+
                '</board>'+
            '</form>',
    });

    assert.hasClass(form.renderer.$el,'o_dashboard',
        "withadashboard,therenderershouldhavethepropercssclass");
    assert.containsOnce(form,'.o_dashboard.o_view_nocontent',
        "shouldhaveanocontenthelper");
    assert.strictEqual(form.$('.o_control_panel.breadcrumb-item').text(),"MyDashboard",
        "shouldhavethecorrecttitle");
    form.destroy();
});

QUnit.test('displaythenocontenthelper',asyncfunction(assert){
    assert.expect(1);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column></column>'+
                '</board>'+
            '</form>',
        viewOptions:{
            action:{
                help:'<pclass="hello">clicktoaddapartner</p>'
            }
        },
    });

    assert.containsOnce(form,'.o_dashboard.o_view_nocontent',
        "shouldhaveanocontenthelperwithactionhelp");
    form.destroy();
});

QUnit.test('basicfunctionality,withonesubaction',asyncfunction(assert){
    assert.expect(26);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{&quot;orderedBy&quot;:[{&quot;name&quot;:&quot;foo&quot;,&quot;asc&quot;:True}]}"view_mode="list"string="ABC"name="51"domain="[[\'foo\',\'!=\',\'False\']]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route,args){
            if(route==='/web/action/load'){
                assert.step('loadaction');
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list']],
                });
            }
            if(route==='/web/dataset/search_read'){
                assert.deepEqual(args.domain,[['foo','!=','False']],"thedomainshouldbepassed");
                assert.deepEqual(args.context.orderedBy,[{
                        'name':'foo',
                        'asc':true,
                    }],
                    'orderedByispresentinthesearchreadwhenspecifiedonthecustomaction'
                );
            }
            if(route==='/web/view/edit_custom'){
                assert.step('editcustom');
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
        },
    });

    assert.containsOnce(form,'.oe_dashboard_links',
        "shouldhaverenderedalinkdiv");
    assert.containsOnce(form,'table.oe_dashboard[data-layout="2-1"]',
        "shouldhaverenderedatable");
    assert.containsNone(form,'td.o_list_record_selector',
        "tdshouldnothavealistselector");
    assert.strictEqual(form.$('h2span.oe_header_txt:contains(ABC)').length,1,
        "shouldhaverenderedaheaderwithactionstring");
    assert.containsN(form,'tr.o_data_row',3,
        "shouldhaverendered3datarows");

    assert.ok(form.$('.oe_content').is(':visible'),"contentisvisible");

    awaittestUtils.dom.click(form.$('.oe_fold'));

    assert.notOk(form.$('.oe_content').is(':visible'),"contentisnolongervisible");

    awaittestUtils.dom.click(form.$('.oe_fold'));

    assert.ok(form.$('.oe_content').is(':visible'),"contentisvisibleagain");
    assert.verifySteps(['loadaction','editcustom','editcustom']);

    assert.strictEqual($('.modal').length,0,"shouldhavenomodalopen");

    awaittestUtils.dom.click(form.$('button.oe_dashboard_link_change_layout'));

    assert.strictEqual($('.modal').length,1,"shouldhaveopenedamodal");
    assert.strictEqual($('.modalli[data-layout="2-1"]i.oe_dashboard_selected_layout').length,1,
        "shouldmarkcurrentlyselectedlayout");

    awaittestUtils.dom.click($('.modal.oe_dashboard_layout_selectorli[data-layout="1-1"]'));

    assert.strictEqual($('.modal').length,0,"shouldhavenomodalopen");
    assert.containsOnce(form,'table.oe_dashboard[data-layout="1-1"]',
        "shouldhaverenderedatablewithcorrectlayout");


    assert.containsOnce(form,'.oe_action',"shouldhaveonedisplayedaction");
    awaittestUtils.dom.click(form.$('span.oe_close'));

    assert.strictEqual($('.modal').length,1,"shouldhaveopenedamodal");

    //confirmthecloseoperation
    awaittestUtils.dom.click($('.modalbutton.btn-primary'));

    assert.strictEqual($('.modal').length,0,"shouldhavenomodalopen");
    assert.containsNone(form,'.oe_action',"shouldhavenodisplayedaction");

    assert.verifySteps(['editcustom','editcustom']);
    form.destroy();
});

QUnit.test('viewsinthedashboarddonothaveacontrolpanel',asyncfunction(assert){
    assert.expect(2);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<form>'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list'],[5,'form']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
        },
    });

    assert.containsOnce(form,'.o_action.o_list_view');
    assert.containsNone(form,'.o_action.o_control_panel');

    form.destroy();
});

QUnit.test('canrenderanactionwithoutview_modeattribute',asyncfunction(assert){
    //Theview_modeattributeisautomaticallysettothe'action'nodeswhen
    //theactionisaddedtothedashboardusingthe'Addtodashboard'button
    //inthesearchview.However,otherdashboardviewscanbewrittenbyhand
    //(seeopenacademytutorial),andinthiscase,wedon'twanthardcode
    //action'sparams(likecontextordomain),asthedashboardcandirectly
    //retrievethemfromtheaction.Sameappliesfortheview_type,asthe
    //firstviewoftheactioncanbeused,bydefault.
    assert.expect(3);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actionstring="ABC"name="51"context="{\'a\':1}"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
        },
        mockRPC:function(route,args){
            if(route==='/board/static/src/img/layout_1-1-1.png'){
                returnPromise.resolve();
            }
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    context:'{"b":2}',
                    domain:'[["foo","=","yop"]]',
                    res_model:'partner',
                    views:[[4,'list'],[false,'form']],
                });
            }
            if(args.method==='load_views'){
                assert.deepEqual(args.kwargs.context,{a:1,b:2},
                    "shouldhavemixedbothcontexts");
            }
            if(route==='/web/dataset/search_read'){
                assert.deepEqual(args.domain,[['foo','=','yop']],
                    "shouldusethedomainoftheaction");
            }
            returnthis._super.apply(this,arguments);
        },
    });

    assert.strictEqual(form.$('.oe_action:contains(ABC).o_list_view').length,1,
        "thelistview(firstviewofaction)shouldhavebeenrenderedcorrectly");

    form.destroy();
});

QUnit.test('cansortasublist',asyncfunction(assert){
    assert.expect(2);

    this.data.partner.fields.foo.sortable=true;

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
        },
    });

    assert.strictEqual($('tr.o_data_row').text(),'yoplalalaabc',
        "shouldhavecorrectinitialdata");

    awaittestUtils.dom.click(form.$('th.o_column_sortable:contains(Foo)'));

    assert.strictEqual($('tr.o_data_row').text(),'abclalalayop',
        "datashouldhavebeensorted");
    form.destroy();
});

QUnit.test('canopenarecord',asyncfunction(assert){
    assert.expect(1);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
        },
        intercepts:{
            do_action:function(event){
                assert.deepEqual(event.data.action,{
                    res_id:1,
                    res_model:'partner',
                    type:'ir.actions.act_window',
                    views:[[false,'form']],
                },"shoulddoado_actionwithcorrectparameters");
            },
        },
    });

    awaittestUtils.dom.click(form.$('tr.o_data_rowtd:contains(yop)'));
    form.destroy();
});

QUnit.test('canopenrecordusingactionformview',asyncfunction(assert){
    assert.expect(1);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list'],[5,'form']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
            'partner,5,form':
                '<formstring="Partner"><fieldname="display_name"/></form>',
        },
        intercepts:{
            do_action:function(event){
                assert.deepEqual(event.data.action,{
                    res_id:1,
                    res_model:'partner',
                    type:'ir.actions.act_window',
                    views:[[5,'form']],
                },"shoulddoado_actionwithcorrectparameters");
            },
        },
    });

    awaittestUtils.dom.click(form.$('tr.o_data_rowtd:contains(yop)'));
    form.destroy();
});

QUnit.test('candraganddropaview',asyncfunction(assert){
    assert.expect(5);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list']],
                });
            }
            if(route==='/web/view/edit_custom'){
                assert.step('editcustom');
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
        },
    });

    assert.containsOnce(form,'td.index_0.oe_action',
        "initialactionisincolumn0");

    awaittestUtils.dom.dragAndDrop(form.$('.oe_dashboard_column.index_0.oe_header'),
        form.$('.oe_dashboard_column.index_1'));
    assert.containsNone(form,'td.index_0.oe_action',
        "initialactionisnotincolumn0");
    assert.containsOnce(form,'td.index_1.oe_action',
        "initialactionisinincolumn1");
    assert.verifySteps(['editcustom']);

    form.destroy();
});

QUnit.test('twicethesameactioninadashboard',asyncfunction(assert){
    assert.expect(2);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                        '<actioncontext="{}"view_mode="kanban"string="DEF"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list'],[5,'kanban']],
                });
            }
            if(route==='/web/view/edit_custom'){
                assert.step('editcustom');
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<treestring="Partner"><fieldname="foo"/></tree>',
            'partner,5,kanban':
                '<kanban><templates><tt-name="kanban-box">'+
                    '<div><fieldname="foo"/></div>'+
                '</t></templates></kanban>',
        },
    });

    var$firstAction=form.$('.oe_action:contains(ABC)');
    assert.strictEqual($firstAction.find('.o_list_view').length,1,
        "listviewshouldbedisplayedin'ABC'block");
    var$secondAction=form.$('.oe_action:contains(DEF)');
    assert.strictEqual($secondAction.find('.o_kanban_view').length,1,
        "kanbanviewshouldbedisplayedin'DEF'block");

    form.destroy();
});

QUnit.test('non-existingactioninadashboard',asyncfunction(assert){
    assert.expect(1);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="kanban"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        intercepts:{
            load_views:function(){
                thrownewError('load_viewsshouldnotbecalled');
            }
        },
        mockRPC:function(route){
            if(route==='/board/static/src/img/layout_1-1-1.png'){
                returnPromise.resolve();
            }
            if(route==='/web/action/load'){
                //serveransweriftheactiondoesn'texistanymore
                returnPromise.resolve(false);
            }
            returnthis._super.apply(this,arguments);
        },
    });

    assert.strictEqual(form.$('.oe_action:contains(ABC)').length,1,
        "thereshouldbeaboxforthenon-existingaction");

    form.destroy();
});

QUnit.test('clickingonakanban\'sbuttonshouldtriggertheaction',asyncfunction(assert){
    assert.expect(2);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actionname="149"string="Partner"view_mode="kanban"id="action_0_1"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        archs:{
            'partner,false,kanban':
                '<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                    '<div>'+
                    '<fieldname="foo"/>'+
                    '</div>'+
                    '<div><buttonname="sitting_on_a_park_bench"type="object">Eyinglittlegirlswithbadintent</button>'+
                    '</div>'+
                '</t></templates></kanban>',
        },
        intercepts:{
            execute_action:function(event){
                vardata=event.data;
                assert.strictEqual(data.env.model,'partner',"shouldhavecorrectmodel");
                assert.strictEqual(data.action_data.name,'sitting_on_a_park_bench',
                    "shouldcallcorrectmethod");
            }
        },

        mockRPC:function(route){
            if(route==='/board/static/src/img/layout_1-1-1.png'){
                returnPromise.resolve();
            }
            if(route==='/web/action/load'){
                returnPromise.resolve({res_model:'partner',view_mode:'kanban',views:[[false,'kanban']]});
            }
            if(route==='/web/dataset/search_read'){
                returnPromise.resolve({records:[{foo:'aqualung'}]});
            }
            returnthis._super.apply(this,arguments);
        }
    });

    awaittestUtils.dom.click(form.$('.o_kanban_test').find('button:first'));

    form.destroy();
});

QUnit.test('subviewsareawareofattachinordetachfromtheDOM',asyncfunction(assert){
    assert.expect(2);

    //patchlistrenderer`on_attach_callback`forthetestonly
    testUtils.mock.patch(ListRenderer,{
        on_attach_callback:function(){
            assert.step('subviewon_attach_callback');
        }
    });

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<liststring="Partner"><fieldname="foo"/></list>',
        },
    });

    assert.verifySteps(['subviewon_attach_callback']);

    //restoreon_attach_callbackofListRenderer
    testUtils.mock.unpatch(ListRenderer);

    form.destroy();
});

QUnit.test('dashboardinterceptscustomeventstriggeredbysubcontrollers',asyncfunction(assert){
    assert.expect(1);

    //wepatchtheListControllertoforceittotriggerthecustomeventsthat
    //wewantthedashboardtointercept(tostopthemortotweaktheirdata)
    testUtils.mock.patch(ListController,{
        start:function(){
            this.trigger_up('update_filters');
            returnthis._super.apply(this,arguments);
        },
    });

    varboard=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({res_model:'partner',views:[[false,'list']]});
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,false,list':'<treestring="Partner"/>',
        },
        intercepts:{
            update_filters:assert.step.bind(assert,'update_filters'),
        },
    });

    assert.verifySteps([]);

    testUtils.mock.unpatch(ListController);
    board.destroy();
});

QUnit.test('saveactionstodashboard',asyncfunction(assert){
    assert.expect(6);

    testUtils.patch(ListController,{
        getOwnedQueryParams:function(){
            varresult=this._super.apply(this,arguments);
            result.context={
                'fire':'onthebayou',
            };
            returnresult;
        }
    });

    this.data['partner'].fields.foo.sortable=true;

    varactionManager=awaitcreateActionManager({
        data:this.data,
        archs:{
            'partner,false,list':'<list><fieldname="foo"/></list>',
            'partner,false,search':'<search></search>',
        },
        mockRPC:function(route,args){
            if(route==='/board/add_to_dashboard'){
                assert.deepEqual(args.context_to_save.group_by,['foo'],
                    'Thegroup_byshouldhavebeensaved');
                assert.deepEqual(args.context_to_save.orderedBy,
                    [{
                        name:'foo',
                        asc:true,
                    }],
                    'TheorderedByshouldhavebeensaved');
                assert.strictEqual(args.context_to_save.fire,'onthebayou',
                    'Thecontextofacontrollershouldbepassedandflattened');
                assert.strictEqual(args.action_id,1,
                    "shouldsavethecorrectaction");
                assert.strictEqual(args.view_mode,'list',
                    "shouldsavethecorrectviewtype");
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        }
    });

    awaitactionManager.doAction({
        id:1,
        res_model:'partner',
        type:'ir.actions.act_window',
        views:[[false,'list']],
    });

    assert.containsOnce(actionManager,'.o_list_view',
        "shoulddisplaythelistview");

    //Sortthelist
    awaittestUtils.dom.click($('.o_column_sortable'));

    //GroupIt
    awaitcpHelpers.toggleGroupByMenu(actionManager);
    awaitcpHelpers.toggleAddCustomGroup(actionManager);
    awaitcpHelpers.applyGroup(actionManager);

    //addthisactiontodashboard
    awaitcpHelpers.toggleFavoriteMenu(actionManager);

    awaittestUtils.dom.click($('.o_add_to_board>button'));
    awaittestUtils.fields.editInput($('.o_add_to_boardinput'),'aname');
    awaittestUtils.dom.click($('.o_add_to_boarddivbutton'));

    testUtils.unpatch(ListController);

    actionManager.destroy();
});

QUnit.test('savetwosearchestodashboard',asyncfunction(assert){
    //thesecondsearchsavedshouldnotbeinfluencedbythefirst
    assert.expect(2);

    varactionManager=awaitcreateActionManager({
        data:this.data,
        archs:{
            'partner,false,list':'<list><fieldname="foo"/></list>',
            'partner,false,search':'<search></search>',
        },
        mockRPC:function(route,args){
            if(route==='/board/add_to_dashboard'){
                if(filter_count===0){
                    assert.deepEqual(args.domain,[["display_name","ilike","a"]],
                        "thecorrectdomainshouldbesent");
                }
                if(filter_count===1){
                    assert.deepEqual(args.domain,[["display_name","ilike","b"]],
                        "thecorrectdomainshouldbesent");
                }

                filter_count+=1;
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        },
    });

    awaitactionManager.doAction({
        id:1,
        res_model:'partner',
        type:'ir.actions.act_window',
        views:[[false,'list']],
    });

    varfilter_count=0;
    //Addafirstfilter
    awaitcpHelpers.toggleFilterMenu(actionManager);
    awaitcpHelpers.toggleAddCustomFilter(actionManager);
    awaittestUtils.fields.editInput(actionManager.el.querySelector('.o_generator_menu_value.o_input'),'a');
    awaitcpHelpers.applyFilter(actionManager);

    //Addittodashboard
    awaitcpHelpers.toggleFavoriteMenu(actionManager);
    awaittestUtils.dom.click($('.o_add_to_board>button'));
    awaittestUtils.dom.click($('.o_add_to_boarddivbutton'));

    //Removeit
    awaittestUtils.dom.click(actionManager.el.querySelector('.o_facet_remove'));

    //Addthesecondfilter
    awaitcpHelpers.toggleFilterMenu(actionManager);
    awaitcpHelpers.toggleAddCustomFilter(actionManager);
    awaittestUtils.fields.editInput(actionManager.el.querySelector('.o_generator_menu_value.o_input'),"b");
    awaitcpHelpers.applyFilter(actionManager);
    //Addittodashboard
    awaitcpHelpers.toggleFavoriteMenu(actionManager);
    awaittestUtils.dom.click(actionManager.el.querySelector('.o_add_to_board>button'));
    awaittestUtils.dom.click(actionManager.el.querySelector('.o_add_to_boarddivbutton'));

    actionManager.destroy();
});

QUnit.test('saveaactiondomaintodashboard',asyncfunction(assert){
    //Viewdomainsaretobeaddedtothedashboarddomain
    assert.expect(1);

    varview_domain=["display_name","ilike","a"];
    varfilter_domain=["display_name","ilike","b"];

    //Thefilterdomainalreadycontainstheviewdomain,butisalwaysaddedbydashboard..,
    varexpected_domain=['&',view_domain,'&',view_domain,filter_domain];

    varactionManager=awaitcreateActionManager({
        data:this.data,
        archs:{
            'partner,false,list':'<list><fieldname="foo"/></list>',
            'partner,false,search':'<search></search>',
        },
        mockRPC:function(route,args){
            if(route==='/board/add_to_dashboard'){
                assert.deepEqual(args.domain,expected_domain,
                    "thecorrectdomainshouldbesent");
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        },
    });

    awaitactionManager.doAction({
        id:1,
        res_model:'partner',
        type:'ir.actions.act_window',
        views:[[false,'list']],
        domain:[view_domain],
    });

    //Addafilter
    awaitcpHelpers.toggleFilterMenu(actionManager);
    awaitcpHelpers.toggleAddCustomFilter(actionManager);
    awaittestUtils.fields.editInput(
        actionManager.el.querySelector('.o_generator_menu_value.o_input'),
        "b"
    );
    awaitcpHelpers.applyFilter(actionManager);
    //Addittodashboard
    awaitcpHelpers.toggleFavoriteMenu(actionManager);
    awaittestUtils.dom.click(actionManager.el.querySelector('.o_add_to_board>button'));
    //add
    awaittestUtils.dom.click(actionManager.el.querySelector('.o_add_to_boarddivbutton'));

    actionManager.destroy();
});

QUnit.test("Viewsshouldbeloadedintheuser'slanguage",asyncfunction(assert){
    assert.expect(2);
    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        session:{user_context:{lang:'fr_FR'}},
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{\'lang\':\'en_US\'}"view_mode="list"string="ABC"name="51"domain="[]"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route,args){
            if(args.method==='load_views'){
                assert.deepEqual(pyUtils.eval('context',args.kwargs.context),{lang:'fr_FR'},
                    'Theviewsshouldbeloadedwiththecorrectcontext');
            }
            if(route==="/web/dataset/search_read"){
                assert.equal(args.context.lang,'fr_FR',
                    'Thedatashouldbeloadedwiththecorrectcontext');
            }
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'list']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<liststring="Partner"><fieldname="foo"/></list>',
        },
    });

    form.destroy();
});

QUnit.test("Dashboardshouldusecorrectgroupby",asyncfunction(assert){
    assert.expect(1);
    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{\'group_by\':[\'bar\']}"string="ABC"name="51"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route,args){
            if(args.method==='web_read_group'){
                assert.deepEqual(args.kwargs.groupby,['bar'],
                    'userdefinedgroupbyshouldhaveprecedenceonactiongroupby');
            }
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    context:{
                        group_by:'some_field',
                    },
                    views:[[4,'list']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<liststring="Partner"><fieldname="foo"/></list>',
        },
    });

    form.destroy();
});

QUnit.test("Dashboardshouldusecorrectgroupbywhendefinedasastringofonefield",asyncfunction(assert){
    assert.expect(1);
    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<formstring="MyDashboard">'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actioncontext="{\'group_by\':\'bar\'}"string="ABC"name="51"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route,args){
            if(args.method==='web_read_group'){
                assert.deepEqual(args.kwargs.groupby,['bar'],
                    'userdefinedgroupbyshouldhaveprecedenceonactiongroupby');
            }
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    context:{
                        group_by:'some_field',
                    },
                    views:[[4,'list']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,list':
                '<liststring="Partner"><fieldname="foo"/></list>',
        },
    });

    form.destroy();
});

QUnit.test('clickonacellofpivotviewinsidedashboard',asyncfunction(assert){
    assert.expect(3);

    varform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:'<form>'+
                '<boardstyle="2-1">'+
                    '<column>'+
                        '<actionview_mode="pivot"string="ABC"name="51"></action>'+
                    '</column>'+
                '</board>'+
            '</form>',
        mockRPC:function(route){
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    res_model:'partner',
                    views:[[4,'pivot']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner,4,pivot':'<pivot><fieldname="int_field"type="measure"/></pivot>',
        },
        intercepts:{
            do_action:function(){
                assert.step('doaction');
            },
        },
    });

    assert.verifySteps([]);

    awaittestUtils.dom.click(form.$('.o_pivot.o_pivot_cell_value'));

    assert.verifySteps(['doaction']);

    form.destroy();
});

QUnit.test('correctlysavethetimerangesofareportingviewincomparisonmode',asyncfunction(assert){
    assert.expect(1);

    constunpatchDate=patchDate(2020,6,1,11,0,0);

    this.data.partner.fields.date={string:'Date',type:'date',sortable:true};

    constactionManager=awaitcreateActionManager({
        data:this.data,
        archs:{
            'partner,false,pivot':'<pivot><fieldname="foo"/></pivot>',
            'partner,false,search':'<search><filtername="Date"date="date"/></search>',
        },
        mockRPC:function(route,args){
            if(route==='/board/add_to_dashboard'){
                assert.deepEqual(args.context_to_save.comparison,{
                    comparisonId:"previous_period",
                    fieldName:"date",
                    fieldDescription:"Date",
                    rangeDescription:"July2020",
                    range:["&",["date",">=","2020-07-01"],["date","<=","2020-07-31"]],
                    comparisonRange:["&",["date",">=","2020-06-01"],["date","<=","2020-06-30"]],
                    comparisonRangeDescription:"June2020",
                });
                returnPromise.resolve(true);
            }
            returnthis._super.apply(this,arguments);
        },
    });

    awaitactionManager.doAction({
        id:1,
        res_model:'partner',
        type:'ir.actions.act_window',
        views:[[false,'pivot']],
    });

    //filteronJuly2020
    awaitcpHelpers.toggleFilterMenu(actionManager);
    awaitcpHelpers.toggleMenuItem(actionManager,'Date');
    awaitcpHelpers.toggleMenuItemOption(actionManager,'Date','July');

    //compareJuly2020toJune2020
    awaitcpHelpers.toggleComparisonMenu(actionManager);
    awaitcpHelpers.toggleMenuItem(actionManager,0);

    //addtheviewtothedashboard
    awaitcpHelpers.toggleFavoriteMenu(actionManager);

    awaittestUtils.dom.click($('.o_add_to_board>button'));
    awaittestUtils.fields.editInput($('.o_add_to_boardinput'),'aname');
    awaittestUtils.dom.click($('.o_add_to_boarddivbutton'));

    unpatchDate();
    actionManager.destroy();
});

QUnit.test('correctlydisplaythetimerangedescriptionsofareportingviewincomparisonmode',asyncfunction(assert){
    assert.expect(1);

    this.data.partner.fields.date={string:'Date',type:'date',sortable:true};
    this.data.partner.records[0].date='2020-07-15';

    constform=awaitcreateView({
        View:BoardView,
        model:'board',
        data:this.data,
        arch:`<formstring="MyDashboard">
                <boardstyle="2-1">
                    <column>
                        <actionstring="ABC"name="51"></action>
                    </column>
                </board>
            </form>`,
        archs:{
            'partner,1,pivot':
                '<pivotstring="Partner"></pivot>',
        },
        mockRPC:function(route,args){
            if(route==='/board/static/src/img/layout_1-1-1.png'){
                returnPromise.resolve();
            }
            if(route==='/web/action/load'){
                returnPromise.resolve({
                    context:JSON.stringify({comparison:{
                        comparisonId:"previous_period",
                        fieldName:"date",
                        fieldDescription:"Date",
                        rangeDescription:"July2020",
                        range:["&",["date",">=","2020-07-01"],["date","<=","2020-07-31"]],
                        comparisonRange:["&",["date",">=","2020-06-01"],["date","<=","2020-06-30"]],
                        comparisonRangeDescription:"June2020",
                    }}),
                    domain:'[]',
                    res_model:'partner',
                    views:[[1,'pivot']],
                });
            }
            returnthis._super.apply(this,arguments);
        },
    });

    assert.deepEqual(
        [...form.el.querySelectorAll('div.o_pivotth.o_pivot_origin_row')].map(el=>el.innerText),
        ['June2020','July2020','Variation']
    );

    form.destroy();
});
});
