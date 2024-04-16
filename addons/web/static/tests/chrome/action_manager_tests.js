flectra.define('web.action_manager_tests',function(require){
"usestrict";

varActionManager=require('web.ActionManager');
varReportClientAction=require('report.client_action');
varNotification=require('web.Notification');
varNotificationService=require('web.NotificationService');
varAbstractAction=require('web.AbstractAction');
varAbstractStorageService=require('web.AbstractStorageService');
varBasicFields=require('web.basic_fields');
varcore=require('web.core');
varListController=require('web.ListController');
varStandaloneFieldManagerMixin=require('web.StandaloneFieldManagerMixin');
varRamStorage=require('web.RamStorage');
varReportService=require('web.ReportService');
varSessionStorageService=require('web.SessionStorageService');
vartestUtils=require('web.test_utils');
varWarningDialog=require('web.CrashManager').WarningDialog;
varWidget=require('web.Widget');

varcreateActionManager=testUtils.createActionManager;
constcpHelpers=testUtils.controlPanel;
const{xml}=owl.tags;

QUnit.module('ActionManager',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    foo:{string:"Foo",type:"char"},
                    bar:{string:"Bar",type:"many2one",relation:'partner'},
                    o2m:{string:"One2Many",type:"one2many",relation:'partner',relation_field:'bar'},
                },
                records:[
                    {id:1,display_name:"Firstrecord",foo:"yop",bar:2,o2m:[2,3]},
                    {id:2,display_name:"Secondrecord",foo:"blip",bar:1,o2m:[1,4,5]},
                    {id:3,display_name:"Thirdrecord",foo:"gnap",bar:1,o2m:[]},
                    {id:4,display_name:"Fourthrecord",foo:"plop",bar:2,o2m:[]},
                    {id:5,display_name:"Fifthrecord",foo:"zoup",bar:2,o2m:[]},
                ],
            },
            pony:{
                fields:{
                    name:{string:'Name',type:'char'},
                },
                records:[
                    {id:4,name:'TwilightSparkle'},
                    {id:6,name:'Applejack'},
                    {id:9,name:'Fluttershy'}
                ],
            },
        };

        this.actions=[{
            id:1,
            name:'PartnersAction1',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[1,'kanban']],
        },{
            id:2,
            type:'ir.actions.server',
        },{
            id:3,
            name:'Partners',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'list'],[1,'kanban'],[false,'form']],
        },{
            id:4,
            name:'PartnersAction4',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[1,'kanban'],[2,'list'],[false,'form']],
        },{
            id:5,
            name:'CreateaPartner',
            res_model:'partner',
            target:'new',
            type:'ir.actions.act_window',
            views:[[false,'form']],
        },{
            id:6,
            name:'Partner',
            res_id:2,
            res_model:'partner',
            target:'inline',
            type:'ir.actions.act_window',
            views:[[false,'form']],
        },{
            id:7,
            name:"SomeReport",
            report_name:'some_report',
            report_type:'qweb-pdf',
            type:'ir.actions.report',
        },{
            id:8,
            name:'FavoritePonies',
            res_model:'pony',
            type:'ir.actions.act_window',
            views:[[false,'list'],[false,'form']],
        },{
            id:9,
            name:'AClientAction',
            tag:'ClientAction',
            type:'ir.actions.client',
        },{
            id:10,
            type:'ir.actions.act_window_close',
        },{
            id:11,
            name:"AnotherReport",
            report_name:'another_report',
            report_type:'qweb-pdf',
            type:'ir.actions.report',
            close_on_report_download:true,
        },{
            id:12,
            name:"SomeHTMLReport",
            report_name:'some_report',
            report_type:'qweb-html',
            type:'ir.actions.report',
        }];

        this.archs={
            //kanbanviews
            'partner,1,kanban':'<kanban><templates><tt-name="kanban-box">'+
                    '<divclass="oe_kanban_global_click"><fieldname="foo"/></div>'+
                '</t></templates></kanban>',

            //listviews
            'partner,false,list':'<tree><fieldname="foo"/></tree>',
            'partner,2,list':'<treelimit="3"><fieldname="foo"/></tree>',
            'pony,false,list':'<tree><fieldname="name"/></tree>',

            //formviews
            'partner,false,form':'<form>'+
                    '<header>'+
                        '<buttonname="object"string="Callmethod"type="object"/>'+
                        '<buttonname="4"string="Executeaction"type="action"/>'+
                    '</header>'+
                    '<group>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                    '</group>'+
                '</form>',
            'pony,false,form':'<form>'+
                    '<fieldname="name"/>'+
                '</form>',

            //searchviews
            'partner,false,search':'<search><fieldname="foo"string="Foo"/></search>',
            'partner,1,search':'<search>'+
                   '<filtername="bar"help="Bar"domain="[(\'bar\',\'=\',1)]"/>'+
                '</search>',
            'pony,false,search':'<search></search>',
        };
    },
},function(){
    QUnit.module('Misc');

    QUnit.test('breadcrumbsandactionswithtargetinline',asyncfunction(assert){
        assert.expect(3);

        this.actions[3].views=[[false,'form']];
        this.actions[3].target='inline';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(4);
        assert.ok(!$('.o_control_panel').is(':visible'),
            "controlpanelshouldnotbevisible");

        awaitactionManager.doAction(1,{clear_breadcrumbs:true});
        assert.ok($('.o_control_panel').is(':visible'),
            "controlpanelshouldnowbevisible");
        assert.strictEqual($('.o_control_panel.breadcrumb').text(),"PartnersAction1",
            "shouldhaveonlyonecurrentactionvisibleinbreadcrumbs");

        actionManager.destroy();
    });

    QUnit.test('nowidgetmemoryleakswhendoingsomeactionstuff',asyncfunction(assert){
        assert.expect(1);

        vardelta=0;
        testUtils.mock.patch(Widget,{
            init:function(){
                delta++;
                this._super.apply(this,arguments);
            },
            destroy:function(){
                delta--;
                this._super.apply(this,arguments);
            },
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(8);

        varn=delta;
        awaitactionManager.doAction(4);

        //kanbanviewisloaded,switchtolistview
        awaitcpHelpers.switchView(actionManager,'list');
        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        //gobacktoaction7inbreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:first'));

        assert.strictEqual(delta,n,
            "shouldhaveproperlydestroyedallotherwidgets");
        actionManager.destroy();
        testUtils.mock.unpatch(Widget);
    });

    QUnit.test('nowidgetmemoryleakswhenexecutingactionsindialog',asyncfunction(assert){
        assert.expect(1);

        vardelta=0;
        testUtils.mock.patch(Widget,{
            init:function(){
                delta++;
                this._super.apply(this,arguments);
            },
            destroy:function(){
                if(!this.isDestroyed()){
                    delta--;
                }
                this._super.apply(this,arguments);
            },
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        varn=delta;

        awaitactionManager.doAction(5);
        awaitactionManager.doAction({type:'ir.actions.act_window_close'});

        assert.strictEqual(delta,n,
            "shouldhaveproperlydestroyedallwidgets");

        actionManager.destroy();
        testUtils.mock.unpatch(Widget);
    });

    QUnit.test('nomemoryleakswhenexecutinganactionwhileswitchingview',asyncfunction(assert){
        assert.expect(1);

        vardef;
        vardelta=0;
        testUtils.mock.patch(Widget,{
            init:function(){
                delta+=1;
                this._super.apply(this,arguments);
            },
            destroy:function(){
                delta-=1;
                this._super.apply(this,arguments);
            },
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        awaitactionManager.doAction(4);
        varn=delta;

        awaitactionManager.doAction(3,{clear_breadcrumbs:true});

        //switchtotheformview(thisrequestisblocked)
        def=testUtils.makeTestPromise();
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        //executeanotheractionmeanwhile(don'tblockthisrequest)
        awaitactionManager.doAction(4,{clear_breadcrumbs:true});

        //unblocktheswitchtotheformviewinaction3
        def.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(n,delta,
            "allwidgetsofaction3shouldhavebeendestroyed");

        actionManager.destroy();
        testUtils.mock.unpatch(Widget);
    });

    QUnit.test('nomemoryleakswhenexecutinganactionwhileloadingviews',asyncfunction(assert){
        assert.expect(1);

        vardef;
        vardelta=0;
        testUtils.mock.patch(Widget,{
            init:function(){
                delta+=1;
                this._super.apply(this,arguments);
            },
            destroy:function(){
                delta-=1;
                this._super.apply(this,arguments);
            },
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
               varresult=this._super.apply(this,arguments);
                if(args.method==='load_views'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        //executeaction4toknowthenumberofwidgetsitinstantiates
        awaitactionManager.doAction(4);
        varn=delta;

        //executeafirstaction(its'load_views'RPCisblocked)
        def=testUtils.makeTestPromise();
        actionManager.doAction(3,{clear_breadcrumbs:true});

        //executeanotheractionmeanwhile(andunlocktheRPC)
        actionManager.doAction(4,{clear_breadcrumbs:true});
        def.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(n,delta,
            "allwidgetsofaction3shouldhavebeendestroyed");

        actionManager.destroy();
        testUtils.mock.unpatch(Widget);
    });

    QUnit.test('nomemoryleakswhenexecutinganactionwhileloadingdataofdefaultview',asyncfunction(assert){
        assert.expect(1);

        vardef;
        vardelta=0;
        testUtils.mock.patch(Widget,{
            init:function(){
                delta+=1;
                this._super.apply(this,arguments);
            },
            destroy:function(){
                delta-=1;
                this._super.apply(this,arguments);
            },
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route){
                varresult=this._super.apply(this,arguments);
                if(route==='/web/dataset/search_read'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        //executeaction4toknowthenumberofwidgetsitinstantiates
        awaitactionManager.doAction(4);
        varn=delta;

        //executeafirstaction(its'search_read'RPCisblocked)
        def=testUtils.makeTestPromise();
        actionManager.doAction(3,{clear_breadcrumbs:true});

        //executeanotheractionmeanwhile(andunlocktheRPC)
        actionManager.doAction(4,{clear_breadcrumbs:true});
        def.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(n,delta,
            "allwidgetsofaction3shouldhavebeendestroyed");

        actionManager.destroy();
        testUtils.mock.unpatch(Widget);
    });

    QUnit.test('actionwith"no_breadcrumbs"settotrue',asyncfunction(assert){
        assert.expect(2);

        _.findWhere(this.actions,{id:4}).context={no_breadcrumbs:true};

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");

        //pushanotheractionflaggedwith'no_breadcrumbs=true'
        awaitactionManager.doAction(4);
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,0,
            "thebreadcrumbsshouldbeempty");

        actionManager.destroy();
    });

    QUnit.test('on_reverse_breadcrumbhandleriscorrectlycalled',asyncfunction(assert){
        assert.expect(3);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        //executeaction3andopenarecordinformview
        awaitactionManager.doAction(3);
        testUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        //executeaction4without'on_reverse_breadcrumb'handler,thengoback
        awaitactionManager.doAction(4);
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:first'));
        assert.verifySteps([]);

        //executeaction4withan'on_reverse_breadcrumb'handler,thengoback
        awaitactionManager.doAction(4,{
            on_reverse_breadcrumb:function(){
                assert.step('on_reverse_breadcrumb');
            }
        });
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:first'));
        assert.verifySteps(['on_reverse_breadcrumb']);

        actionManager.destroy();
    });

    QUnit.test('handles"history_back"event',asyncfunction(assert){
        assert.expect(2);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(4);
        awaitactionManager.doAction(3);
        actionManager.trigger_up('history_back');

        awaittestUtils.nextTick();
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'PartnersAction4',
            "breadcrumbsshoulddisplaythedisplay_nameoftheaction");

        actionManager.destroy();
    });

    QUnit.test('storesandrestoresscrollposition',asyncfunction(assert){
        assert.expect(7);

        varleft;
        vartop;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                getScrollPosition:function(ev){
                    assert.step('getScrollPosition');
                    ev.data.callback({left:left,top:top});
                },
                scrollTo:function(ev){
                    assert.step('scrollToleft'+ev.data.left+',top'+ev.data.top);
                },
            },
        });

        //executeafirstactionandsimulateascroll
        assert.step('executeaction3');
        awaitactionManager.doAction(3);
        left=50;
        top=100;

        //executeasecondaction(inwhichwedon'tscroll)
        assert.step('executeaction4');
        awaitactionManager.doAction(4);

        //gobackusingthebreadcrumbs
        assert.step('gobacktoaction3');
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));

        assert.verifySteps([
            'executeaction3',
            'executeaction4',
            'getScrollPosition',//ofaction3,beforeleavingit
            'gobacktoaction3',
            'getScrollPosition',//ofaction4,beforeleavingit
            'scrollToleft50,top100',//restorescrollpositionofaction3
        ]);

        actionManager.destroy();
    });

    QUnit.test('executinganactionwithtarget!="new"closesalldialogs',asyncfunction(assert){
        assert.expect(4);

        this.archs['partner,false,form']='<form>'+
                '<fieldname="o2m">'+
                    '<tree><fieldname="foo"/></tree>'+
                    '<form><fieldname="foo"/></form>'+
                '</field>'+
            '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(3);
        assert.containsOnce(actionManager,'.o_list_view');

        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsOnce(actionManager,'.o_form_view');

        awaittestUtils.dom.click(actionManager.$('.o_form_view.o_data_row:first'));
        assert.containsOnce(document.body,'.modal.o_form_view');

        awaitactionManager.doAction(1);//target!='new'
        assert.containsNone(document.body,'.modal');

        actionManager.destroy();
    });

    QUnit.test('executinganactionwithtarget"new"doesnotclosedialogs',asyncfunction(assert){
        assert.expect(4);

        this.archs['partner,false,form']='<form>'+
                '<fieldname="o2m">'+
                    '<tree><fieldname="foo"/></tree>'+
                    '<form><fieldname="foo"/></form>'+
                '</field>'+
            '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(3);
        assert.containsOnce(actionManager,'.o_list_view');

        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsOnce(actionManager,'.o_form_view');

        awaittestUtils.dom.click(actionManager.$('.o_form_view.o_data_row:first'));
        assert.containsOnce(document.body,'.modal.o_form_view');

        awaitactionManager.doAction(5);//target'new'
        assert.containsN(document.body,'.modal.o_form_view',2);

        actionManager.destroy();
    });

    QUnit.test('executingawindowactionwithonchangewarningdoesnothideit',asyncfunction(assert){
        assert.expect(2);

        this.archs['partner,false,form']=`
            <form>
              <fieldname="foo"/>
            </form>`;

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{},
                        warning:{
                            title:"Warning",
                            message:"Everythingisalright",
                            type:'dialog',
                        },
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                warning:function(event){
                    newWarningDialog(actionManager,{
                        title:event.data.title,
                    },event.data).open();
                },
            },
        });

        awaitactionManager.doAction(3);

        awaittestUtils.dom.click(actionManager.$('.o_list_button_add'));
        assert.containsOnce(
            $,
            '.modal.o_technical_modal.show',
            "Warningmodalshouldbeopened");

        awaittestUtils.dom.click($('.modal.o_technical_modal.showbutton.close'));
        assert.containsNone(
            $,
            '.modal.o_technical_modal.show',
            "Warningmodalshouldbeclosed");

        actionManager.destroy();
    });

    QUnit.module('PushState');

    QUnit.test('properlypushstate',asyncfunction(assert){
        assert.expect(3);

        varstateDescriptions=[
            {action:4,model:"partner",title:"PartnersAction4",view_type:"kanban"},
            {action:8,model:"pony",title:"FavoritePonies",view_type:"list"},
            {action:8,id:4,model:"pony",title:"TwilightSparkle",view_type:"form"},
        ];

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                push_state:function(event){
                    vardescr=stateDescriptions.shift();
                    assert.deepEqual(_.extend({},event.data.state),descr,
                        "shouldnotifytheenvironmentofnewstate");
                },
            },
        });
        awaitactionManager.doAction(4);
        awaitactionManager.doAction(8);
        awaittestUtils.dom.click(actionManager.$('tr.o_data_row:first'));

        actionManager.destroy();
    });

    QUnit.test('pushstateafteractionisloaded,notbefore',asyncfunction(assert){
        assert.expect(5);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                push_state:function(){
                    assert.step('push_state');
                },
            },
            mockRPC:function(route){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(4);
        assert.verifySteps([
            '/web/action/load',
            '/web/dataset/call_kw/partner',
            '/web/dataset/search_read',
            'push_state'
        ]);

        actionManager.destroy();
    });

    QUnit.test('donotpushstateforactionsintarget=new',asyncfunction(assert){
        assert.expect(3);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                push_state:function(){
                    assert.step('push_state');
                },
            },
        });
        awaitactionManager.doAction(4);
        assert.verifySteps(['push_state']);
        awaitactionManager.doAction(5);
        assert.verifySteps([]);

        actionManager.destroy();
    });

    QUnit.test('donotpushstatewhenactionfails',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                push_state:function(){
                    assert.step('push_state');
                },
            },
            mockRPC:function(route,args){
                if(args.method==='read'){
                    //thisistherpctoloadformview
                    returnPromise.reject();
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(8);
        assert.verifySteps(['push_state']);
        awaittestUtils.dom.click(actionManager.$('tr.o_data_row:first'));
        assert.verifySteps([]);
        //wemakesureherethatthelistviewisstillinthedom
        assert.containsOnce(actionManager,'.o_list_view',
            "thereshouldstillbealistviewindom");

        actionManager.destroy();
    });

    QUnit.module('LoadState');

    QUnit.test('shouldnotcrashoninvalidstate',asyncfunction(assert){
        assert.expect(2);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
         awaitactionManager.loadState({
            res_model:'partner',//thevalidkeyforthemodelis'model',not'res_model'
        });

        assert.strictEqual(actionManager.$el.text(),'',"shoulddisplaynothing");
        assert.verifySteps([]);

        actionManager.destroy();
    });

    QUnit.test('properlyloadclientactions',asyncfunction(assert){
        assert.expect(2);

        varClientAction=AbstractAction.extend({
            start:function(){
                this.$el.text('HelloWorld');
                this.$el.addClass('o_client_action_test');
            },
        });
        core.action_registry.add('HelloWorldTest',ClientAction);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.loadState({
            action:'HelloWorldTest',
        });

        assert.strictEqual(actionManager.$('.o_client_action_test').text(),
            'HelloWorld',"shouldhavecorrectlyrenderedtheclientaction");

        assert.verifySteps([]);

        actionManager.destroy();
        deletecore.action_registry.map.HelloWorldTest;
    });

    QUnit.test('properlyloadactwindowactions',asyncfunction(assert){
        assert.expect(6);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
         awaitactionManager.loadState({
            action:1,
        });

        assert.strictEqual($('.o_control_panel').length,1,
            "shouldhaverenderedacontrolpanel");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaverenderedakanbanview");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',
        ]);

        actionManager.destroy();
    });

    QUnit.test('properlyloadrecords',asyncfunction(assert){
        assert.expect(5);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
         awaitactionManager.loadState({
            id:2,
            model:'partner',
        });

        assert.containsOnce(actionManager,'.o_form_view',
            "shouldhaverenderedaformview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Secondrecord',
            "shouldhaveopenedthesecondrecord");

        assert.verifySteps([
            'load_views',
            'read',
        ]);

        actionManager.destroy();
    });

    QUnit.test('properlyloaddefaultrecord',asyncfunction(assert){
        assert.expect(5);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.loadState({
            action:3,
            id:"", //mighthappenwithbbqandid=&inURL
            model:'partner',
            view_type:'form',
        });

        assert.containsOnce(actionManager,'.o_form_view',
            "shouldhaverenderedaformview");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            'onchange',
        ]);

        actionManager.destroy();
    });

    QUnit.test('loadrequestedviewforactwindowactions',asyncfunction(assert){
        assert.expect(6);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
         awaitactionManager.loadState({
            action:3,
            view_type:'kanban',
        });

        assert.containsNone(actionManager,'.o_list_view',
            "shouldnothaverenderedalistview");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaverenderedakanbanview");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',
        ]);

        actionManager.destroy();
    });

    QUnit.test('lazyloadmultirecordviewifmonorecordoneisrequested',asyncfunction(assert){
        assert.expect(11);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.loadState({
            action:3,
            id:2,
            view_type:'form',
        });
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnothaverenderedalistview");
        assert.containsOnce(actionManager,'.o_form_view',
            "shouldhaverenderedaformview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Secondrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        //gobacktoLst
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldnowdisplaythelistview");
        assert.containsNone(actionManager,'.o_form_view',
            "shouldnotdisplaytheformviewanymore");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            'read',//readtheopenedrecord
            '/web/dataset/search_read',//searchreadwhencomingbacktoList
        ]);

        actionManager.destroy();
    });

    QUnit.test('lazyloadmultirecordviewwithpreviousaction',asyncfunction(assert){
        assert.expect(6);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(4);

        assert.strictEqual($('.o_control_panel.breadcrumbli').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumbli').text(),'PartnersAction4',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        awaitactionManager.doAction(3,{
            resID:2,
            viewType:'form',
        });

        assert.strictEqual($('.o_control_panel.breadcrumbli').length,3,
            "thereshouldbethreecontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumbli').text(),'PartnersAction4PartnersSecondrecord',
            "thebreadcrumbelementsshouldbecorrectlyordered");

        //gobacktoList
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:last'));

        assert.strictEqual($('.o_control_panel.breadcrumbli').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumbli').text(),'PartnersAction4Partners',
            "thebreadcrumbelementsshouldbecorrectlyordered");

        actionManager.destroy();
    });

    QUnit.test('lazyloadedmultirecordviewwithfailingmonorecordone',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='read'){
                    returnPromise.reject();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaitactionManager.loadState({
            action:3,
            id:2,
            view_type:'form',
        }).then(function(){
            assert.ok(false,'shouldnotresolvethedeferred');
        }).catch(function(){
            assert.ok(true,'shouldrejectthedeferred');
        });

        assert.containsNone(actionManager,'.o_form_view');
        assert.containsNone(actionManager,'.o_list_view');

        awaitactionManager.doAction(1);

        assert.containsOnce(actionManager,'.o_kanban_view');

        actionManager.destroy();
    });

    QUnit.test('changetheviewTypeofthecurrentaction',asyncfunction(assert){
        assert.expect(13);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        assert.containsOnce(actionManager,'.o_list_view',
            "shouldhaverenderedalistview");

        //switchtokanbanview
         awaitactionManager.loadState({
            action:3,
            view_type:'kanban',
        });

        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewanymore");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaveswitchedtothekanbanview");

        //switchtoformview,openrecord4
         awaitactionManager.loadState({
            action:3,
            id:4,
            view_type:'form',
        });

        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnotdisplaythekanbanviewanymore");
        assert.containsOnce(actionManager,'.o_form_view',
            "shouldhaveswitchedtotheformview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Fourthrecord',
            "shouldhaveopenedtherequestedrecord");

        //verifystepstoensurethatthewholeactionhasn'tbeenre-executed
        //(ifitwouldhavebeen,/web/action/loadandload_viewswouldappear
        //severaltimes)
        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//listview
            '/web/dataset/search_read',//kanbanview
            'read',//formview
        ]);

        actionManager.destroy();
    });

    QUnit.test('changetheidofthecurrentaction',asyncfunction(assert){
        assert.expect(11);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        //executeaction3andopenthefirstrecordinaformview
        awaitactionManager.doAction(3);
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        assert.containsOnce(actionManager,'.o_form_view',
            "shouldhaverenderedaformview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "shouldhaveopenedthefirstrecord");

        //switchtorecord4
        awaitactionManager.loadState({
            action:3,
            id:4,
            view_type:'form',
        });

        assert.containsOnce(actionManager,'.o_form_view',
            "shouldstilldisplaytheformview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Fourthrecord',
            "shouldhaveswitchedtotherequestedrecord");

        //verifystepstoensurethatthewholeactionhasn'tbeenre-executed
        //(ifitwouldhavebeen,/web/action/loadandload_viewswouldappear
        //twice)
        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//listview
            'read',//formview,record1
            'read',//formview,record4
        ]);

        actionManager.destroy();
    });

    QUnit.test('shouldnotpushaloadedstate',asyncfunction(assert){
        assert.expect(3);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                push_state:function(){
                    assert.step('push_state');
                },
            },
        });
        awaitactionManager.loadState({action:3});

        assert.verifySteps([],"shouldnotpushtheloadedstate");

        awaittestUtils.dom.click(actionManager.$('tr.o_data_row:first'));

        assert.verifySteps(['push_state'],
            "shouldpushthestateofitchangesafterwards");

        actionManager.destroy();
    });

    QUnit.test('shouldnotpushaloadedstateofaclientaction',asyncfunction(assert){
        assert.expect(4);

        varClientAction=AbstractAction.extend({
            init:function(parent,action,options){
                this._super.apply(this,arguments);
                this.controllerID=options.controllerID;
            },
            start:function(){
                varself=this;
                var$button=$('<button>').text('ClickMe!');
                $button.on('click',function(){
                    self.trigger_up('push_state',{
                        controllerID:self.controllerID,
                        state:{someValue:'X'},
                    });
                });
                this.$el.append($button);
                returnthis._super.apply(this,arguments);
            },
        });
        core.action_registry.add('ClientAction',ClientAction);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                push_state:function(ev){
                    assert.step('push_state');
                    assert.deepEqual(ev.data.state,{
                        action:9,
                        someValue:'X',
                        title:'AClientAction',
                    });
                },
            },
        });
         awaitactionManager.loadState({action:9});

        assert.verifySteps([],"shouldnotpushtheloadedstate");

        awaittestUtils.dom.click(actionManager.$('button'));

        assert.verifySteps(['push_state'],
            "shouldpushthestateofitchangesafterwards");

        actionManager.destroy();
    });

    QUnit.test('changeaparamofanir.actions.clientintheurl',asyncfunction(assert){
        assert.expect(7);

        varClientAction=AbstractAction.extend({
            hasControlPanel:true,
            init:function(parent,action){
                this._super.apply(this,arguments);
                varcontext=action.context;
                this.a=context.params&&context.params.a||'defaultvalue';
            },
            start:function(){
                assert.step('start');
                this.$('.o_content').text(this.a);
                this.$el.addClass('o_client_action');
                this.trigger_up('push_state',{
                    controllerID:this.controllerID,
                    state:{a:this.a},
                });
                returnthis._super.apply(this,arguments);
            },
        });
        core.action_registry.add('ClientAction',ClientAction);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        //executetheclientaction
        awaitactionManager.doAction(9);

        assert.strictEqual(actionManager.$('.o_client_action.o_content').text(),'defaultvalue',
            "shouldhaverenderedtheclientaction");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");

        //updateparam'a'intheurl
         awaitactionManager.loadState({
            action:9,
            a:'newvalue',
        });

        assert.strictEqual(actionManager.$('.o_client_action.o_content').text(),'newvalue',
            "shouldhavererenderedtheclientactionwiththecorrectparam");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldstillbeonecontrollerinthebreadcrumbs");

        //shouldhaveexecutedtheclientactiontwice
        assert.verifySteps(['start','start']);

        actionManager.destroy();
        deletecore.action_registry.map.ClientAction;
    });

    QUnit.test('loadawindowactionwithoutid(inamulti-recordview)',asyncfunction(assert){
        assert.expect(14);

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                session_storage:RamStorageService,
            },
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        testUtils.mock.intercept(actionManager,'call_service',function(ev){
            if(ev.data.service==='session_storage'){
                assert.step(ev.data.method);
            }
        },true);

        awaitactionManager.doAction(4);

        assert.containsOnce(actionManager,'.o_kanban_view',
            "shoulddisplayakanbanview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'PartnersAction4',
            "breadcrumbsshoulddisplaythedisplay_nameoftheaction");

         awaitactionManager.loadState({
            model:'partner',
            view_type:'list',
        });

        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'PartnersAction4',
            "shouldstillbeinthesameaction");
        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnolongerdisplayakanbanview");
        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplayalistview");

        assert.verifySteps([
            '/web/action/load',//action3
            'load_views',//action3
            '/web/dataset/search_read',//action3
            'setItem',//action3
            'getItem',//loadState
            'load_views',//loadedaction
            '/web/dataset/search_read',//loadedaction
            'setItem',//loadedaction
        ]);

        actionManager.destroy();
    });

    QUnit.test('statewithintegeractive_idsshouldnotcrash',asyncfunction(assert){
        assert.expect(0);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            mockRPC:function(route,args){
                if(route==='/web/action/run'){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.loadState({
            action:2,
            active_ids:3,
        });

        actionManager.destroy();
    });

    QUnit.module('Concurrencymanagement');

    QUnit.test('droppreviousactionsifpossible',asyncfunction(assert){
        assert.expect(6);

        vardef=testUtils.makeTestPromise();
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route){
                varresult=this._super.apply(this,arguments);
                assert.step(route);
                if(route==='/web/action/load'){
                    returndef.then(_.constant(result));
                }
                returnresult;
            },
        });
        actionManager.doAction(4);
        actionManager.doAction(8);

        def.resolve();
        awaittestUtils.nextTick();
        //action4loadsakanbanviewfirst,6loadsalistview.Wewantalist
        assert.containsOnce(actionManager,'.o_list_view',
            'thereshouldbealistviewinDOM');

        assert.verifySteps([
            '/web/action/load', //loadaction4
            '/web/action/load',//loadaction6
            '/web/dataset/call_kw/pony',//loadviewsforaction6
            '/web/dataset/search_read',//searchreadforlistviewaction6
        ]);

        actionManager.destroy();
    });

    QUnit.test('handleswitchingviewandswitchingbackonslownetwork',asyncfunction(assert){
        assert.expect(8);

        vardef=testUtils.makeTestPromise();
        vardefs=[Promise.resolve(),def,Promise.resolve()];

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route){
                assert.step(route);
                varresult=this._super.apply(this,arguments);
                if(route==='/web/dataset/search_read'){
                    vardef=defs.shift();
                    returndef.then(_.constant(result));
                }
                returnresult;
            },
        });
        awaitactionManager.doAction(4);

        //kanbanviewisloaded,switchtolistview
        awaitcpHelpers.switchView(actionManager,'list');

        //here,listviewisnotreadyyet,becausedefisnotresolved
        //switchbacktokanbanview
        awaitcpHelpers.switchView(actionManager,'kanban');

        //here,wewantthekanbanviewtoreloaditself,regardlessoflistview
        assert.verifySteps([
            "/web/action/load",            //initialloadaction
            "/web/dataset/call_kw/partner",//loadviews
            "/web/dataset/search_read",    //search_readforkanbanview
            "/web/dataset/search_read",    //search_readforlistview(notresolvedyet)
            "/web/dataset/search_read"     //search_readforkanbanviewreload(notresolvedyet)
        ]);

        //weresolvedef=>listviewisnowready(butwewanttoignoreit)
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(actionManager,'.o_kanban_view',
            "thereshouldbeakanbanviewindom");
        assert.containsNone(actionManager,'.o_list_view',
            "thereshouldnotbealistviewindom");

        actionManager.destroy();
    });

    QUnit.test('whenanserveractiontakestoomuchtime...',asyncfunction(assert){
        assert.expect(1);

        vardef=testUtils.makeTestPromise();

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route){
                if(route==='/web/action/run'){
                    returndef.then(_.constant(1));
                }
                returnthis._super.apply(this,arguments);
            },
        });

        actionManager.doAction(2);
        actionManager.doAction(4);

        def.resolve();
        awaittestUtils.nextTick();
        assert.strictEqual($('.o_control_panel.breadcrumb-item.active').text(),'PartnersAction4',
            'action4shouldbeloaded');

        actionManager.destroy();
    });

    QUnit.test('clickingquicklyonbreadcrumbs...',asyncfunction(assert){
        assert.expect(1);

        vardef=Promise.resolve();

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read'){
                    returndef.then(_.constant(result));
                }
                returnresult;
            },
        });

        //createasituationwith3breadcrumbs:kanban/form/list
        awaitactionManager.doAction(4);
        awaittestUtils.dom.click(actionManager.$('.o_kanban_record:first'));
        actionManager.doAction(8);

        //now,thenextreadoperationswillbepromise(thisistheread
        //operationfortheformviewreload)
        def=testUtils.makeTestPromise();
        awaittestUtils.nextTick();

        //clickonthebreadcrumbsfortheformview,thenonthekanbanview
        //beforetheformviewisfullyreloaded
        awaittestUtils.dom.click($('.o_control_panel.breadcrumb-item:eq(1)'));
        awaittestUtils.dom.click($('.o_control_panel.breadcrumb-item:eq(0)'));

        //resolvetheformviewread
        def.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual($('.o_control_panel.breadcrumb-item.active').text(),'PartnersAction4',
            'action4shouldbeloadedandvisible');

        actionManager.destroy();
    });

    QUnit.test('executeanewactionwhileloadingalazy-loadedcontroller',asyncfunction(assert){
        assert.expect(15);

        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                assert.step(args.method||route);
                if(route==='/web/dataset/search_read'&&args.model==='partner'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });
         awaitactionManager.loadState({
            action:4,
            id:2,
            view_type:'form',
        });

        assert.containsOnce(actionManager,'.o_form_view',
            "shoulddisplaytheformviewofaction4");

        //clicktogobacktoKanban(thisrequestisblocked)
        def=testUtils.makeTestPromise();
        awaittestUtils.nextTick();
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));

        assert.containsOnce(actionManager,'.o_form_view',
        "shouldstilldisplaytheformviewofaction4");

        //executeanotheractionmeanwhile(don'tblockthisrequest)
        awaitactionManager.doAction(8,{clear_breadcrumbs:true});

        assert.containsOnce(actionManager,'.o_list_view',
        "shoulddisplayaction8");
        assert.containsNone(actionManager,'.o_form_view',
        "shouldnolongerdisplaytheformview");

        assert.verifySteps([
            '/web/action/load',//loadstateaction4
            'load_views',//loadstateaction4
            'read',//readtheopenedrecord(action4)
            '/web/dataset/search_read',//blockedsearchreadwhencomingbacktoKanban(action4)
            '/web/action/load',//action8
            'load_views',//action8
            '/web/dataset/search_read',//searchreadaction8
        ]);

        //unblocktheswitchtoKanbaninaction4
        def.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(actionManager,'.o_list_view',
            "shouldstilldisplayaction8");
        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnotdisplaythekanbanviewofaction4");

        assert.verifySteps([]);

        actionManager.destroy();
    });

    QUnit.test('executeanewactionwhilehandlingacall_button',asyncfunction(assert){
        assert.expect(16);

        varself=this;
        vardef=testUtils.makeTestPromise();
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/web/dataset/call_button'){
                    returndef.then(_.constant(self.actions[0]));
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //executeaction3andopenarecordinformview
        awaitactionManager.doAction(3);
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        assert.containsOnce(actionManager,'.o_form_view',
            "shoulddisplaytheformviewofaction3");

        //clickon'Callmethod'button(thisrequestisblocked)
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains(Callmethod)'));

        assert.containsOnce(actionManager,'.o_form_view',
            "shouldstilldisplaytheformviewofaction3");

        //executeanotheraction
        awaitactionManager.doAction(8,{clear_breadcrumbs:true});

        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistviewofaction8");
        assert.containsNone(actionManager,'.o_form_view',
            "shouldnolongerdisplaytheformview");

        assert.verifySteps([
            '/web/action/load',//action3
            'load_views',//action3
            '/web/dataset/search_read',//listforaction3
            'read',//formforaction3
            'object',//clickon'Callmethod'button(thisrequestisblocked)
            '/web/action/load',//action8
            'load_views',//action8
            '/web/dataset/search_read',//listforaction8
        ]);

        //unblockthecall_buttonrequest
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldstilldisplaythelistviewofaction8");
        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnotdisplayaction1");

        assert.verifySteps([]);

        actionManager.destroy();
    });

    QUnit.test('executeanewactionwhileswitchingtoanothercontroller',asyncfunction(assert){
        assert.expect(15);

        /*
         *Thistest'sbottomlineisthatadoActionalwayshaspriority
         *overaswitchcontroller(clickingonarecordrowtogotoformview).
         *Ingeneral,thelastactionManager'soperationhasprioritybecausewewant
         *toallowtheusertomakemistakes,ortorapidlyreconsiderhernextaction.
         *HereweassertthattheactionManager'sRPCareinorder,buta'read'operation
         *isexpected,withthecurrentimplementation,totakeplacewhenswitchingtotheformview.
         *Ultimatelytheformview's'read'issuperfluous,butcanhappenatanypointoftheflow,
         *exceptattheveryend,whichshouldalwaysbethefinalaction'slist's'search_read'.
         */
        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read'){
                    assert.ok(true,"A'read'shouldhavebeendone.Checktest'scommentthough.");
                    returnPromise.resolve(def).then(_.constant(result));
                }
                assert.step(args.method||route);
                returnresult;
            },
        });

        awaitactionManager.doAction(3);

        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistviewofaction3");

        //switchtotheformview(thisrequestisblocked)
        def=testUtils.makeTestPromise();
        awaittestUtils.nextTick();
        testUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        assert.containsOnce(actionManager,'.o_list_view',
        "shouldstilldisplaythelistviewofaction3");

        //executeanotheractionmeanwhile(don'tblockthisrequest)
        awaitactionManager.doAction(4,{clear_breadcrumbs:true});

        assert.containsOnce(actionManager,'.o_kanban_view',
            "shoulddisplaythekanbanviewofaction8");
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnolongerdisplaythelistview");

        assert.verifySteps([
            '/web/action/load',//action3
            'load_views',//action3
            '/web/dataset/search_read',//searchreadoflistviewofaction3
            '/web/action/load',//action4
            'load_views',//action4
            '/web/dataset/search_read',//searchreadaction4
        ]);

        //unblocktheswitchtotheformviewinaction3
        def.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldstilldisplaythekanbanviewofaction8");
        assert.containsNone(actionManager,'.o_form_view',
            "shouldnotdisplaytheformviewofaction3");

        assert.verifySteps([]);

        actionManager.destroy();
    });

    QUnit.test('executeanewactionwhileloadingviews',asyncfunction(assert){
        assert.expect(10);

        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                assert.step(args.method||route);
                if(args.method==='load_views'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        //executeafirstaction(its'load_views'RPCisblocked)
        def=testUtils.makeTestPromise();
        actionManager.doAction(3);

        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewofaction3");

        awaittestUtils.nextTick();
        //executeanotheractionmeanwhile(andunlocktheRPC)
        actionManager.doAction(4);
        def.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(actionManager,'.o_kanban_view',
            "shoulddisplaythekanbanviewofaction4");
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewofaction3");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");

        assert.verifySteps([
            '/web/action/load',//action3
            'load_views',//action3
            '/web/action/load',//action4
            'load_views',//action4
            '/web/dataset/search_read',//searchreadaction4
        ]);

        actionManager.destroy();
    });

    QUnit.test('executeanewactionwhileloadingdataofdefaultview',asyncfunction(assert){
        assert.expect(11);

        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                assert.step(args.method||route);
                if(route==='/web/dataset/search_read'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        //executeafirstaction(its'search_read'RPCisblocked)
        def=testUtils.makeTestPromise();
        actionManager.doAction(3);

        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewofaction3");

        awaittestUtils.nextTick();
        //executeanotheractionmeanwhile(andunlocktheRPC)
        actionManager.doAction(4);
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shoulddisplaythekanbanviewofaction4");
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewofaction3");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");

        assert.verifySteps([
            '/web/action/load',//action3
            'load_views',//action3
            '/web/dataset/search_read',//searchreadaction3
            '/web/action/load',//action4
            'load_views',//action4
            '/web/dataset/search_read',//searchreadaction4
        ]);

        actionManager.destroy();
    });

    QUnit.test('openarecordwhilereloadingthelistview',asyncfunction(assert){
        assert.expect(12);

        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route){
                varresult=this._super.apply(this,arguments);
                if(route==='/web/dataset/search_read'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
        });

        awaitactionManager.doAction(3);

        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");
        assert.containsN(actionManager,'.o_list_view.o_data_row',5,
            "listviewshouldcontain5records");
        assert.strictEqual($('.o_control_panel.o_list_buttons').length,1,
            "listviewbuttonsshouldbedisplayedincontrolpanel");

        //reload(thesearch_readRPCwillbeblocked)
        def=testUtils.makeTestPromise();
        awaittestUtils.nextTick();
        awaitcpHelpers.switchView(actionManager,'list');

        assert.containsN(actionManager,'.o_list_view.o_data_row',5,
            "listviewshouldstillcontain5records");
        assert.strictEqual($('.o_control_panel.o_list_buttons').length,1,
            "listviewbuttonsshouldstillbedisplayedincontrolpanel");

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        assert.containsOnce(actionManager,'.o_form_view',
            "shoulddisplaytheformview");
        assert.strictEqual($('.o_control_panel.o_list_buttons').length,0,
            "listviewbuttonsshouldnolongerbedisplayedincontrolpanel");
        assert.strictEqual($('.o_control_panel.o_form_buttons_view').length,1,
            "formviewbuttonsshouldbedisplayedinstead");

        //unblockthesearch_readRPC
        def.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(actionManager,'.o_form_view',
            "shoulddisplaytheformview");
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistview");
        assert.strictEqual($('.o_control_panel.o_list_buttons').length,0,
            "listviewbuttonsshouldstillnotbedisplayedincontrolpanel");
        assert.strictEqual($('.o_control_panel.o_form_buttons_view').length,1,
            "formviewbuttonsshouldstillbedisplayedinstead");

        actionManager.destroy();
    });

    QUnit.module('ClientActions');

    QUnit.test('canexecuteclientactionsfromtagname',asyncfunction(assert){
        assert.expect(3);

        varClientAction=AbstractAction.extend({
            start:function(){
                this.$el.text('HelloWorld');
                this.$el.addClass('o_client_action_test');
            },
        });
        core.action_registry.add('HelloWorldTest',ClientAction);

        varactionManager=awaitcreateActionManager({
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            }
        });
        awaitactionManager.doAction('HelloWorldTest');

        assert.strictEqual($('.o_control_panel:visible').length,0,//AAB:globalselectoruntiltheControlPanelismovedfromActionManagertotheViews
            "shouldn'thaverenderedacontrolpanel");
        assert.strictEqual(actionManager.$('.o_client_action_test').text(),
            'HelloWorld',"shouldhavecorrectlyrenderedtheclientaction");
        assert.verifySteps([]);

        actionManager.destroy();
        deletecore.action_registry.map.HelloWorldTest;
    });

    QUnit.test('clientactionwithcontrolpanel',asyncfunction(assert){
        assert.expect(4);

        varClientAction=AbstractAction.extend({
            hasControlPanel:true,
            start:asyncfunction(){
                this.$('.o_content').text('HelloWorld');
                this.$el.addClass('o_client_action_test');
                this.controlPanelProps.title='Hello';
                awaitthis._super.apply(this,arguments);
            },
        });
        core.action_registry.add('HelloWorldTest',ClientAction);

        varactionManager=awaitcreateActionManager();
        awaitactionManager.doAction('HelloWorldTest');

        assert.strictEqual($('.o_control_panel:visible').length,1,
            "shouldhaverenderedacontrolpanel");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Hello',
            "breadcrumbsshouldstilldisplaythetitleofthecontroller");
        assert.strictEqual(actionManager.$('.o_client_action_test.o_content').text(),
            'HelloWorld',"shouldhavecorrectlyrenderedtheclientaction");

        actionManager.destroy();
        deletecore.action_registry.map.HelloWorldTest;
    });

    QUnit.test('stateispushedforclientactions',asyncfunction(assert){
        assert.expect(3);

        constClientAction=AbstractAction.extend({
            getTitle:function(){
                return'atitle';
            },
            getState:function(){
                return{foo:'baz'};
            }
        });
        constactionManager=awaitcreateActionManager({
            intercepts:{
                push_state:function(ev){
                    constexpectedState={action:'HelloWorldTest',foo:'baz',title:'atitle'};
                    assert.deepEqual(ev.data.state,expectedState,
                        "shouldincludeacompletestatedescription,includingcustomstate");
                    assert.step('pushstate');
                },
            },
        });
        core.action_registry.add('HelloWorldTest',ClientAction);

        awaitactionManager.doAction('HelloWorldTest');

        assert.verifySteps(['pushstate']);

        actionManager.destroy();
        deletecore.action_registry.map.HelloWorldTest;
    });

    QUnit.test('actioncanuseacustomcontrolpanel',asyncfunction(assert){
        assert.expect(1);

        classCustomControlPanelextendsowl.Component{}
        CustomControlPanel.template=xml/*xml*/`
            <divclass="custom-control-panel">Mycustomcontrolpanel</div>
        `
        constClientAction=AbstractAction.extend({
            hasControlPanel:true,
            config:{
                ControlPanel:CustomControlPanel
            },
        });
        constactionManager=awaitcreateActionManager();
        core.action_registry.add('HelloWorldTest',ClientAction);
        awaitactionManager.doAction('HelloWorldTest');
        assert.containsOnce(actionManager,'.custom-control-panel',
            "shouldhaveacustomcontrolpanel");

        actionManager.destroy();
        deletecore.action_registry.map.HelloWorldTest;
    });

    QUnit.test('breadcrumbisupdatedontitlechange',asyncfunction(assert){
        assert.expect(2);

        varClientAction=AbstractAction.extend({
            hasControlPanel:true,
            events:{
                click:function(){
                    this.updateControlPanel({title:'newtitle'});
                },
            },
            start:asyncfunction(){
                this.$('.o_content').text('HelloWorld');
                this.$el.addClass('o_client_action_test');
                this.controlPanelProps.title='initialtitle';
                awaitthis._super.apply(this,arguments);
            },
        });
        varactionManager=awaitcreateActionManager();
        core.action_registry.add('HelloWorldTest',ClientAction);
        awaitactionManager.doAction('HelloWorldTest');

        assert.strictEqual($('ol.breadcrumb').text(),"initialtitle",
            "shouldhaveinitialtitleasbreadcrumbcontent");

        awaittestUtils.dom.click(actionManager.$('.o_client_action_test'));
        assert.strictEqual($('ol.breadcrumb').text(),"newtitle",
            "shouldhaveupdatedtitleasbreadcrumbcontent");

        actionManager.destroy();
        deletecore.action_registry.map.HelloWorldTest;
    });

    QUnit.test('testdisplay_notificationclientaction',asyncfunction(assert){
        assert.expect(6);

        testUtils.mock.patch(Notification,{
            _animation:false,
        });

        constactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                notification:NotificationService,
            },
        });

        awaitactionManager.doAction(1);
        assert.containsOnce(actionManager,'.o_kanban_view');

        awaitactionManager.doAction({
            type:'ir.actions.client',
            tag:'display_notification',
            params:{
                title:'title',
                message:'message',
                sticky:true,
            }
        });
        constnotificationSelector='.o_notification_manager.o_notification';

        assert.containsOnce(document.body,notificationSelector,
            'anotificationshouldbepresent');

        constnotificationElement=document.body.querySelector(notificationSelector);
        assert.strictEqual(
            notificationElement.querySelector('.o_notification_title').textContent,
            'title',
            "thenotificationshouldhavethecorrecttitle"
        );
        assert.strictEqual(
            notificationElement.querySelector('.o_notification_content').textContent,
            'message',
            "thenotificationshouldhavethecorrectmessage"
        );

        assert.containsOnce(actionManager,'.o_kanban_view');

        awaittestUtils.dom.click(
            notificationElement.querySelector('.o_notification_close')
        );

        assert.containsNone(document.body,notificationSelector,
            "thenotificationshouldbedestroy");

        actionManager.destroy();
        testUtils.mock.unpatch(Notification);
    });

    QUnit.module('Serveractions');

    QUnit.test('canexecuteserveractionsfromdbID',asyncfunction(assert){
        assert.expect(9);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/web/action/run'){
                    assert.strictEqual(args.action_id,2,
                        "shouldcallthecorrectserveraction");
                    returnPromise.resolve(1);//executeaction1
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(2);

        assert.strictEqual($('.o_control_panel:visible').length,1,
            "shouldhaverenderedacontrolpanel");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaverenderedakanbanview");
        assert.verifySteps([
            '/web/action/load',
            '/web/action/run',
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',
        ]);

        actionManager.destroy();
    });

    QUnit.test('handleserveractionsreturningfalse',asyncfunction(assert){
        assert.expect(9);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/web/action/run'){
                    returnPromise.resolve(false);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //executeanactionintarget="new"
        awaitactionManager.doAction(5,{
            on_close:assert.step.bind(assert,'closehandler'),
        });
        assert.strictEqual($('.o_technical_modal.o_form_view').length,1,
            "shouldhaverenderedaformviewinamodal");

        //executeaserveractionthatreturnsfalse
        awaitactionManager.doAction(2);
        assert.strictEqual($('.o_technical_modal').length,0,
            "shouldhaveclosedthemodal");
        assert.verifySteps([
            '/web/action/load',//action5
            'load_views',
            'onchange',
            '/web/action/load',//action2
            '/web/action/run',
            'closehandler',
        ]);

        actionManager.destroy();
    });

    QUnit.module('Reportactions');

    QUnit.test('canexecutereportactionsfromdbID',asyncfunction(assert){
        assert.expect(5);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                report:ReportService,
            },
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/report/check_wkhtmltopdf'){
                    returnPromise.resolve('ok');
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                get_file:asyncfunction(params){
                    assert.step(params.url);
                    params.success();
                    params.complete();
                    returntrue;
                },
            },
        });
        awaitactionManager.doAction(7,{
            on_close:function(){
                assert.step('on_close');
            },
        });
        awaittestUtils.nextTick();
        assert.verifySteps([
            '/web/action/load',
            '/report/check_wkhtmltopdf',
            '/report/download',
            'on_close',
        ]);

        actionManager.destroy();
    });

    QUnit.test('reportactionscanclosemodalsandreloadviews',asyncfunction(assert){
        assert.expect(8);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                report:ReportService,
            },
            mockRPC:function(route,args){
                if(route==='/report/check_wkhtmltopdf'){
                    returnPromise.resolve('ok');
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                get_file:asyncfunction(params){
                    assert.step(params.url);
                    params.success();
                    params.complete();
                    returntrue;
                },
            },
        });

        //loadmodal
        awaitactionManager.doAction(5,{
            on_close:function(){
                assert.step('on_close');
            },
        });

        assert.strictEqual($('.o_technical_modal.o_form_view').length,1,
        "shouldhaverenderedaformviewinamodal");

        awaitactionManager.doAction(7,{
            on_close:function(){
                assert.step('on_printed');
            },
        });

        assert.strictEqual($('.o_technical_modal.o_form_view').length,1,
        "Themodalshouldstillexist");

        awaitactionManager.doAction(11);

        assert.strictEqual($('.o_technical_modal.o_form_view').length,0,
        "themodalshouldhavebeenclosedaftertheactionreport");

        assert.verifySteps([
            '/report/download',
            'on_printed',
            '/report/download',
            'on_close',
        ]);

        actionManager.destroy();
    });

    QUnit.test('shouldtriggeranotificationifwkhtmltopdfistoupgrade',asyncfunction(assert){
        assert.expect(5);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                report:ReportService,
                notification:NotificationService.extend({
                    notify:function(params){
                        assert.step(params.type||'notification');
                    }
                }),
            },
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/report/check_wkhtmltopdf'){
                    returnPromise.resolve('upgrade');
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                get_file:asyncfunction(params){
                    assert.step(params.url);
                    params.success();
                    params.complete();
                    returntrue;
                },
            },
        });
        awaitactionManager.doAction(7);
        assert.verifySteps([
            '/web/action/load',
            '/report/check_wkhtmltopdf',
            'warning',
            '/report/download',
        ]);

        actionManager.destroy();
    });

    QUnit.test('shouldopenthereportclientactionifwkhtmltopdfisbroken',asyncfunction(assert){
        assert.expect(7);

        //patchthereportclientactiontooverrideitsiframe'surlsothat
        //itdoesn'ttriggeranRPCwhenitisappendedtotheDOM(forthis
        //usecase,usingremoveSRCAttributedoesn'tworkastheRPCis
        //triggeredassoonastheiframeisintheDOM,evenifitssrc
        //attributeisremovedrightafter)
        testUtils.mock.patch(ReportClientAction,{
            start:function(){
                varself=this;
                returnthis._super.apply(this,arguments).then(function(){
                    self._rpc({route:self.iframe.getAttribute('src')});
                    self.iframe.setAttribute('src','about:blank');
                });
            }
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                report:ReportService,
                notification:NotificationService.extend({
                    notify:function(params){
                        assert.step(params.type||'notification');
                    }
                })
            },
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/report/check_wkhtmltopdf'){
                    returnPromise.resolve('broken');
                }
                if(route.includes('/report/html/some_report')){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                get_file:function(params){
                    assert.step(params.url);//shouldnotbecalled
                    returntrue;
                },
            },
        });
        awaitactionManager.doAction(7);

        assert.containsOnce(actionManager,'.o_report_iframe',
            "shouldhaveopenedthereportclientaction");
        assert.containsOnce(actionManager,'.o_cp_buttons.o_report_buttons.o_report_print');

        assert.verifySteps([
            '/web/action/load',
            '/report/check_wkhtmltopdf',
            'warning',
            '/report/html/some_report?context=%7B%7D',//reportclientaction'siframe
        ]);

        actionManager.destroy();
        testUtils.mock.unpatch(ReportClientAction);
    });

    QUnit.test('sendcontextincaseofhtmlreport',asyncfunction(assert){
        assert.expect(4);

        //patchthereportclientactiontooverrideitsiframe'surlsothat
        //itdoesn'ttriggeranRPCwhenitisappendedtotheDOM(forthis
        //usecase,usingremoveSRCAttributedoesn'tworkastheRPCis
        //triggeredassoonastheiframeisintheDOM,evenifitssrc
        //attributeisremovedrightafter)
        testUtils.mock.patch(ReportClientAction,{
            start:function(){
                varself=this;
                returnthis._super.apply(this,arguments).then(function(){
                    self._rpc({route:self.iframe.getAttribute('src')});
                    self.iframe.setAttribute('src','about:blank');
                });
            }
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                report:ReportService,
                notification:NotificationService.extend({
                    notify:function(params){
                        assert.step(params.type||'notification');
                    }
                })
            },
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route.includes('/report/html/some_report')){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                user_context:{
                    some_key:2,
                }
            },
        });
        awaitactionManager.doAction(12);

        assert.containsOnce(actionManager,'.o_report_iframe',
            "shouldhaveopenedthereportclientaction");

        assert.verifySteps([
            '/web/action/load',
            '/report/html/some_report?context=%7B%22some_key%22%3A2%7D',//reportclientaction'siframe
        ]);

        actionManager.destroy();
        testUtils.mock.unpatch(ReportClientAction);
    });

    QUnit.test('crashmanagerservicecalledonfailedreportdownloadactions',asyncfunction(assert){
        assert.expect(1);

        varactionManager=awaitcreateActionManager({
            data:this.data,
            actions:this.actions,
            services:{
                report:ReportService,
            },
            mockRPC:function(route){
                if(route==='/report/check_wkhtmltopdf'){
                    returnPromise.resolve('ok');
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                get_file:function(params){
                    params.error({
                        data:{
                            name:'error',
                            arguments:['couldnotdownloadfile'],
                        }
                    });
                    params.complete();
                },
            },
        });

        try{
            awaitactionManager.doAction(11);
        }catch(e){
            //eisundefinedifwelandherebecauseofarejectedpromise,
            //otherwise,itisanError,whichisnotwhatweexpect
            assert.strictEqual(e,undefined);
        }

        actionManager.destroy();
    });

    QUnit.module('WindowActions');

    QUnit.test('canexecuteact_windowactionsfromdbID',asyncfunction(assert){
        assert.expect(6);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(1);

        assert.strictEqual($('.o_control_panel').length,1,
            "shouldhaverenderedacontrolpanel");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaverenderedakanbanview");
        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',
        ]);

        actionManager.destroy();
    });

    QUnit.test('sidebarispresentinlistview',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                varres=this._super.apply(this,arguments);
                if(args.method==='load_views'){
                    assert.strictEqual(args.kwargs.options.toolbar,true,
                        "shouldaskfortoolbarinformation");
                    returnres.then(function(fieldsViews){
                        fieldsViews.list.toolbar={
                            print:[{name:"Printthatrecord"}],
                        };
                        returnfieldsViews;
                    });
                }
                returnres;
            },
        });
        awaitactionManager.doAction(3);

        assert.containsNone(actionManager,'.o_cp_action_menus');

        awaittestUtils.dom.clickFirst(actionManager.$('input.custom-control-input'));
        assert.isVisible(actionManager.$('.o_cp_action_menusbutton.o_dropdown_toggler_btn:contains("Print")'));
        assert.isVisible(actionManager.$('.o_cp_action_menusbutton.o_dropdown_toggler_btn:contains("Action")'));

        actionManager.destroy();
    });

    QUnit.test('canswitchbetweenviews',asyncfunction(assert){
        assert.expect(18);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");

        //switchtokanbanview
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnolongerdisplaythelistview");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shoulddisplaythekanbanview");

        //switchbacktolistview
        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");
        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnolongerdisplaythekanbanview");

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnolongerdisplaythelistview");
        assert.containsOnce(actionManager,'.o_form_view',
            "shoulddisplaytheformview");
        assert.strictEqual(actionManager.$('.o_field_widget[name=foo]').text(),'yop',
            "shouldhaveopenedthecorrectrecord");

        //gobacktolistviewusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");
        assert.containsNone(actionManager,'.o_form_view',
            "shouldnolongerdisplaytheformview");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//list
            '/web/dataset/search_read',//kanban
            '/web/dataset/search_read',//list
            'read',//form
            '/web/dataset/search_read',//list
        ]);

        actionManager.destroy();
    });

    QUnit.test('orderedByincontextisnotpropagatedwhenexecutinganotheraction',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.foo.sortable=true;

        this.archs['partner,false,form']='<header>'+
                                                '<buttonname="8"string="Executeaction"type="action"/>'+
                                            '</header>';

        varsearchReadCount=1;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    if(searchReadCount===1){
                        assert.strictEqual(args.model,'partner');
                        assert.notOk(args.sort);
                    }
                    if(searchReadCount===2){
                        assert.strictEqual(args.model,'partner');
                        assert.strictEqual(args.sort,"fooASC");
                    }
                    if(searchReadCount===3){
                        assert.strictEqual(args.model,'pony');
                        assert.notOk(args.sort);
                    }
                    searchReadCount+=1;
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        //Simulatetheactivationofafilter
        varsearchData={
            domains:[[["foo","=","yop"]]],
            contexts:[{
                orderedBy:[],
            }],
        };
        actionManager.trigger_up('search',searchData);

        //Sortrecords
        awaittestUtils.dom.click(actionManager.$('.o_list_viewth.o_column_sortable'));

        //gettotheformviewofthemodel,onthefirstrecord
         awaittestUtils.dom.click(actionManager.$('.o_data_cell:first'));

        //Changemodelbyclickingonthebuttonwithintheform
         awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton'));

        actionManager.destroy();
    });

    QUnit.test('breadcrumbsareupdatedwhenswitchingbetweenviews',asyncfunction(assert){
        assert.expect(15);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Partners',
            "breadcrumbsshoulddisplaythedisplay_nameoftheaction");

        //switchtokanbanview
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldstillbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Partners',
            "breadcrumbsshouldstilldisplaythedisplay_nameoftheaction");

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_kanban_view.o_kanban_record:first'));
        awaittestUtils.nextTick();
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        //gobacktokanbanviewusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Partners',
            "breadcrumbsshoulddisplaythedisplay_nameoftheaction");

        //switchbacktolistview
        awaitcpHelpers.switchView(actionManager,'list');
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldstillbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Partners',
            "breadcrumbsshouldstilldisplaythedisplay_nameoftheaction");

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        //gobacktolistviewusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldbebackonlistview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),'Partners',
            "breadcrumbsshoulddisplaythedisplay_nameoftheaction");

        actionManager.destroy();
    });

    QUnit.test('switchbuttonsareupdatedwhenswitchingbetweenviews',asyncfunction(assert){
        assert.expect(13);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.containsN(actionManager,'.o_control_panelbutton.o_switch_view',2,
            "shouldhavetwoswitchbuttons(listandkanban)");
        assert.containsOnce(actionManager,'.o_control_panelbutton.o_switch_view.active',
            "shouldhaveonlyoneactivebutton");
        assert.hasClass($('.o_control_panel.o_switch_view:first'),'o_list',
            "listswitchbuttonshouldbethefirstone");
        assert.hasClass($('.o_control_panel.o_switch_view.o_list'),'active',
            "listshouldbetheactiveview");

        //switchtokanbanview
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.containsN(actionManager,'.o_control_panel.o_switch_view',2,
            "shouldstillhavetwoswitchbuttons(listandkanban)");
        assert.containsOnce(actionManager,'.o_control_panel.o_switch_view.active',
            "shouldstillhaveonlyoneactivebutton");
        assert.hasClass($('.o_control_panel.o_switch_view:first'),'o_list',
            "listswitchbuttonshouldstillbethefirstone");
        assert.hasClass($('.o_control_panel.o_switch_view.o_kanban'),'active',
            "kanbanshouldnowbetheactiveview");

        //switchbacktolistview
        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsN(actionManager,'.o_control_panel.o_switch_view',2,
            "shouldstillhavetwoswitchbuttons(listandkanban)");
        assert.hasClass($('.o_control_panel.o_switch_view.o_list'),'active',
            "listshouldnowbetheactiveview");

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsNone(actionManager,'.o_control_panel.o_switch_view',
            "shouldnothaveanyswitchbuttons");

        //gobacktolistviewusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.containsN(actionManager,'.o_control_panel.o_switch_view',2,
            "shouldhavetwoswitchbuttons(listandkanban)");
        assert.hasClass($('.o_control_panel.o_switch_view.o_list'),'active',
            "listshouldbetheactiveview");

        actionManager.destroy();
    });

    QUnit.test('pagerisupdatedwhenswitchingbetweenviews',asyncfunction(assert){
        assert.expect(10);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(4);

        assert.strictEqual($('.o_control_panel.o_pager_value').text(),'1-5',
            "valueshouldbecorrectforkanban");
        assert.strictEqual($('.o_control_panel.o_pager_limit').text(),'5',
            "limitshouldbecorrectforkanban");

        //switchtolistview
        awaitcpHelpers.switchView(actionManager,'list');
        assert.strictEqual($('.o_control_panel.o_pager_value').text(),'1-3',
            "valueshouldbecorrectforlist");
        assert.strictEqual($('.o_control_panel.o_pager_limit').text(),'5',
            "limitshouldbecorrectforlist");

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.strictEqual($('.o_control_panel.o_pager_value').text(),'1',
            "valueshouldbecorrectforform");
        assert.strictEqual($('.o_control_panel.o_pager_limit').text(),'3',
            "limitshouldbecorrectforform");

        //gobacktolistviewusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.strictEqual($('.o_control_panel.o_pager_value').text(),'1-3',
            "valueshouldbecorrectforlist");
        assert.strictEqual($('.o_control_panel.o_pager_limit').text(),'5',
            "limitshouldbecorrectforlist");

        //switchbacktokanbanview
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.strictEqual($('.o_control_panel.o_pager_value').text(),'1-5',
            "valueshouldbecorrectforkanban");
        assert.strictEqual($('.o_control_panel.o_pager_limit').text(),'5',
            "limitshouldbecorrectforkanban");

        actionManager.destroy();
    });

    QUnit.test("domainiskeptwhenswitchingbetweenviews",asyncfunction(assert){
        assert.expect(5);

        this.actions[2].search_view_id=[1,'acustomsearchview'];

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(3);
        assert.containsN(actionManager,'.o_data_row',5);

        //activateadomain
        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"Bar");
        assert.containsN(actionManager,'.o_data_row',2);

        //switchtokanban
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',2);

        //removethedomain
        awaittestUtils.dom.click(actionManager.$('.o_searchview.o_facet_remove'));
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',5);

        //switchbacktolist
        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsN(actionManager,'.o_data_row',5);

        actionManager.destroy();
    });

    QUnit.test('thereisnoflickeringwhenswitchingbetweenviews',asyncfunction(assert){
        assert.expect(20);

        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(){
                varresult=this._super.apply(this,arguments);
                returnPromise.resolve(def).then(_.constant(result));
            },
        });
        awaitactionManager.doAction(3);

        //switchtokanbanview
        def=testUtils.makeTestPromise();
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldstilldisplaythelistview");
        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldn'tdisplaythekanbanviewyet");
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsNone(actionManager,'.o_list_view',
            "shouldn'tdisplaythelistviewanymore");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldnowdisplaythekanbanview");

        //switchbacktolistview
        def=testUtils.makeTestPromise();
        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldstilldisplaythekanbanview");
        assert.containsNone(actionManager,'.o_list_view',
            "shouldn'tdisplaythelistviewyet");
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldn'tdisplaythekanbanviewanymore");
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldnowdisplaythelistview");

        //openarecordinformview
        def=testUtils.makeTestPromise();
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldstilldisplaythelistview");
        assert.containsNone(actionManager,'.o_form_view',
            "shouldn'tdisplaytheformviewyet");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldstillbeonecontrollerinthebreadcrumbs");
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsNone(actionManager,'.o_list_view',
            "shouldnolongerdisplaythelistview");
        assert.containsOnce(actionManager,'.o_form_view',
            "shoulddisplaytheformview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");

        //gobacktolistviewusingthebreadcrumbs
        def=testUtils.makeTestPromise();
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));
        assert.containsOnce(actionManager,'.o_form_view',
            "shouldstilldisplaytheformview");
        assert.containsNone(actionManager,'.o_list_view',
            "shouldn'tdisplaythelistviewyet");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldstillbetwocontrollersinthebreadcrumbs");
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsNone(actionManager,'.o_form_view',
            "shouldnolongerdisplaytheformview");
        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");

        actionManager.destroy();
    });

    QUnit.test('breadcrumbsareupdatedwhendisplay_namechanges',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        //switchtoeditmodeandchangethedisplay_name
        awaittestUtils.dom.click($('.o_control_panel.o_form_button_edit'));
        awaittestUtils.fields.editInput(actionManager.$('.o_field_widget[name=display_name]'),'Newname');
        awaittestUtils.dom.click($('.o_control_panel.o_form_button_save'));

        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldstillbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Newname',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        actionManager.destroy();
    });

    QUnit.test('reversebreadcrumbworksonaccesskey"b"',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains(Executeaction)'));

        assert.containsN(actionManager,'.o_control_panel.breadcrumbli',3);

        var$previousBreadcrumb=actionManager.$('.o_control_panel.breadcrumbli.active').prev();
        assert.strictEqual($previousBreadcrumb.attr("accesskey"),"b",
            "previousbreadcrumbshouldhaveaccessKey'b'");
        awaittestUtils.dom.click($previousBreadcrumb);

        assert.containsN(actionManager,'.o_control_panel.breadcrumbli',2);

        var$previousBreadcrumb=actionManager.$('.o_control_panel.breadcrumbli.active').prev();
        assert.strictEqual($previousBreadcrumb.attr("accesskey"),"b",
            "previousbreadcrumbshouldhaveaccessKey'b'");

        actionManager.destroy();
    });

    QUnit.test('reloadpreviouscontrollerwhendiscardinganewrecord',asyncfunction(assert){
        assert.expect(8);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        //createanewrecord
        awaittestUtils.dom.click($('.o_control_panel.o_list_button_add'));
        assert.containsOnce(actionManager,'.o_form_view.o_form_editable',
            "shouldhaveopenedtheformviewineditmode");

        //discard
        awaittestUtils.dom.click($('.o_control_panel.o_form_button_cancel'));
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldhaveswitchedbacktothelistview");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//list
            'onchange',//form
            '/web/dataset/search_read',//list
        ]);

        actionManager.destroy();
    });

    QUnit.test('requestsforexecute_actionoftypeobjectarehandled',asyncfunction(assert){
        assert.expect(10);

        varself=this;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(route==='/web/dataset/call_button'){
                    assert.deepEqual(args,{
                        args:[[1]],
                        kwargs:{context:{some_key:2}},
                        method:'object',
                        model:'partner',
                    },"shouldcallroutewithcorrectarguments");
                    varrecord=_.findWhere(self.data.partner.records,{id:args.args[0][0]});
                    record.foo='valuechanged';
                    returnPromise.resolve(false);
                }
                returnthis._super.apply(this,arguments);
            },
            session:{user_context:{
                some_key:2,
            }},
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.strictEqual(actionManager.$('.o_field_widget[name=foo]').text(),'yop',
            "checkinitialvalueof'yop'field");

        //clickon'Callmethod'button(shouldcallanObjectmethod)
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains(Callmethod)'));
        assert.strictEqual(actionManager.$('.o_field_widget[name=foo]').text(),'valuechanged',
            "'yop'hasbeenchangedbytheserver,andshouldbeupdatedintheUI");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//listforaction3
            'read',//formforaction3
            'object',//clickon'Callmethod'button
            'read',//re-readformview
        ]);

        actionManager.destroy();
    });

    QUnit.test('requestsforexecute_actionoftypeactionarehandled',asyncfunction(assert){
        assert.expect(11);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        //clickon'Executeaction'button(shouldexecuteanaction)
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwopartsinthebreadcrumbs");
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains(Executeaction)'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,3,
            "thereturnedactionshouldhavebeenstackedoverthepreviousone");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "thereturnedactionshouldhavebeenexecuted");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//listforaction3
            'read',//formforaction3
            '/web/action/load',//clickon'Executeaction'button
            'load_views',
            '/web/dataset/search_read',//kanbanforaction4
        ]);

        actionManager.destroy();
    });

    QUnit.test('requestsforexecute_actionoftypeobject:disablebuttons',asyncfunction(assert){
        assert.expect(2);

        vardef;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_button'){
                    returnPromise.resolve(false);
                }elseif(args.method==='read'){
                    //Blockthe'read'call
                    varresult=this._super.apply(this,arguments);
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        //clickon'Callmethod'button(shouldcallanObjectmethod)
        def=testUtils.makeTestPromise();
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains(Callmethod)'));

        //Buttonsshouldbedisabled
        assert.strictEqual(
            actionManager.$('.o_form_viewbutton:contains(Callmethod)').attr('disabled'),
            'disabled','buttonsshouldbedisabled');

        //Releasethe'read'call
        def.resolve();
        awaittestUtils.nextTick();

        //Buttonsshouldbeenabledafterthereload
        assert.strictEqual(
            actionManager.$('.o_form_viewbutton:contains(Callmethod)').attr('disabled'),
            undefined,'buttonsshouldbedisabled')

        actionManager.destroy();
    });

    QUnit.test('canopendifferentrecordsfromamultirecordview',asyncfunction(assert){
        assert.expect(11);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        //openthefirstrecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");
        assert.strictEqual(actionManager.$('.o_field_widget[name=foo]').text(),'yop',
            "shouldhaveopenedthecorrectrecord");

        //gobacktolistviewusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba'));

        //openthesecondrecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:nth(1)'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Secondrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");
        assert.strictEqual(actionManager.$('.o_field_widget[name=foo]').text(),'blip',
            "shouldhaveopenedthecorrectrecord");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',//list
            'read',//form
            '/web/dataset/search_read',//list
            'read',//form
        ]);

        actionManager.destroy();
    });

    QUnit.test('restorepreviousviewstatewhenswitchingback',asyncfunction(assert){
        assert.expect(5);

        this.actions[2].views.unshift([false,'graph']);
        this.archs['partner,false,graph']='<graph></graph>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.hasClass($('.o_control_panel .fa-bar-chart-o'),'active',
            "barchartbuttonisactive");
        assert.doesNotHaveClass($('.o_control_panel .fa-area-chart'),'active',
            "linechartbuttonisnotactive");

        //displaylinechart
        awaittestUtils.dom.click($('.o_control_panel .fa-area-chart'));
        assert.hasClass($('.o_control_panel .fa-area-chart'),'active',
            "linechartbuttonisnowactive");

        //switchtokanbanandbacktographview
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.strictEqual($('.o_control_panel .fa-area-chart').length,0,
            "graphbuttonsarenolongerincontrolpanel");

        awaitcpHelpers.switchView(actionManager,'graph');
        assert.hasClass($('.o_control_panel .fa-area-chart'),'active',
            "linechartbuttonisstillactive");
        actionManager.destroy();
    });

    QUnit.test('viewswitcherisproperlyhighlightedingraphview',asyncfunction(assert){
        assert.expect(4);

        //note:thistestshouldbemovedtographtests?

        this.actions[2].views.splice(1,1,[false,'graph']);
        this.archs['partner,false,graph']='<graph></graph>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.hasClass($('.o_control_panel.o_switch_view.o_list'),'active',
            "listbuttonincontrolpanelisactive");
        assert.doesNotHaveClass($('.o_control_panel.o_switch_view.o_graph'),'active',
            "graphbuttonincontrolpanelisnotactive");

        //switchtographview
        awaitcpHelpers.switchView(actionManager,'graph');
        assert.doesNotHaveClass($('.o_control_panel.o_switch_view.o_list'),'active',
            "listbuttonincontrolpanelisnotactive");
        assert.hasClass($('.o_control_panel.o_switch_view.o_graph'),'active',
            "graphbuttonincontrolpanelisactive");
        actionManager.destroy();
    });

    QUnit.test('caninteractwithsearchview',asyncfunction(assert){
        assert.expect(2);

        this.archs['partner,false,search']='<search>'+
                '<group>'+
                    '<filtername="foo"string="foo"context="{\'group_by\':\'foo\'}"/>'+
                '</group>'+
            '</search>';
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.doesNotHaveClass(actionManager.$('.o_list_table'),'o_list_table_grouped',
            "listviewisnotgrouped");

        //opengroupbydropdown
        awaittestUtils.dom.click($('.o_control_panel.o_cp_bottom_rightbutton:contains(GroupBy)'));

        //clickonfirstlink
        awaittestUtils.dom.click($('.o_control_panel.o_group_by_menua:first'));

        assert.hasClass(actionManager.$('.o_list_table'),'o_list_table_grouped',
            'listviewisnowgrouped');

        actionManager.destroy();
    });

    QUnit.test('canopenamany2oneexternalwindow',asyncfunction(assert){
        //AAB:thistestcouldbemergedwith'many2onesinformviews'inrelational_fields_tests.js
        assert.expect(8);

        this.data.partner.records[0].bar=2;
        this.archs['partner,false,search']='<search>'+
                '<group>'+
                    '<filtername="foo"string="foo"context="{\'group_by\':\'foo\'}"/>'+
                '</group>'+
            '</search>';
        this.archs['partner,false,form']='<form>'+
            '<group>'+
                '<fieldname="foo"/>'+
                '<fieldname="bar"/>'+
            '</group>'+
        '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(route);
                if(args.method==="get_formview_id"){
                    returnPromise.resolve(false);
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        //openfirstrecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_data_row:first'));
        //clickonedit
        awaittestUtils.dom.click($('.o_control_panel.o_form_button_edit'));

        //clickonexternalbuttonform2o
        awaittestUtils.dom.click(actionManager.$('.o_external_button'));
        assert.verifySteps([
            '/web/action/load',            //initialloadaction
            '/web/dataset/call_kw/partner',//loadviews
            '/web/dataset/search_read',    //readlistviewdata
            '/web/dataset/call_kw/partner/read',//readformviewdata
            '/web/dataset/call_kw/partner/get_formview_id',//getformviewid
            '/web/dataset/call_kw/partner',//loadformviewformodal
            '/web/dataset/call_kw/partner/read'//readdataform2orecord
        ]);
        actionManager.destroy();
    });

    QUnit.test('askforconfirmationwhenleavinga"dirty"view',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(4);

        //openrecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_kanban_record:first'));

        //editrecord
        awaittestUtils.dom.click($('.o_control_panelbutton.o_form_button_edit'));
        awaittestUtils.fields.editInput(actionManager.$('input[name="foo"]'),'pinkypie');

        //gobacktokanbanview
        awaittestUtils.dom.click($('.o_control_panel.breadcrumb-item:firsta'));

        assert.strictEqual($('.modal.modal-body').text(),
            "Therecordhasbeenmodified,yourchangeswillbediscarded.Doyouwanttoproceed?",
            "shoulddisplayamodaldialogtoconfirmdiscardaction");

        //cancel
        awaittestUtils.dom.click($('.modal.modal-footerbutton.btn-secondary'));

        assert.containsOnce(actionManager,'.o_form_view',
            "shouldstillbeinformview");

        //gobackagaintokanbanview
        awaittestUtils.dom.click($('.o_control_panel.breadcrumb-item:firsta'));

        //confirmdiscard
        awaittestUtils.dom.click($('.modal.modal-footerbutton.btn-primary'));

        assert.containsNone(actionManager,'.o_form_view',
            "shouldnolongerbeinformview");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldbeinkanbanview");

        actionManager.destroy();
    });

    QUnit.test('limitsetinactionispassedtoeachcreatedcontroller',asyncfunction(assert){
        assert.expect(2);

        _.findWhere(this.actions,{id:3}).limit=2;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.containsN(actionManager,'.o_data_row',2,
            "shouldonlydisplay2record");

        //switchtokanbanview
        awaitcpHelpers.switchView(actionManager,'kanban');

        assert.strictEqual(actionManager.$('.o_kanban_record:not(.o_kanban_ghost)').length,2,
            "shouldonlydisplay2record");

        actionManager.destroy();
    });

    QUnit.test('gobacktoapreviousactionusingthebreadcrumbs',asyncfunction(assert){
        assert.expect(10);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        //pushanotheractionontopofthefirstone,andcomebacktotheformview
        awaitactionManager.doAction(4);
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,3,
            "thereshouldbethreecontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'PartnersAction4',
            "breadcrumbsshouldcontainthenameofthecurrentaction");
        //gobackusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:nth(1)'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Firstrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        //pushagaintheotheractionontopofthefirstone,andcomebacktothelistview
        awaitactionManager.doAction(4);
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,3,
            "thereshouldbethreecontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'PartnersAction4',
            "breadcrumbsshouldcontainthenameofthecurrentaction");
        //gobackusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:first'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,1,
            "thereshouldbeonecontrollerinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Partners',
            "breadcrumbsshouldcontainthenameofthecurrentaction");

        actionManager.destroy();
    });

    QUnit.test('formviewsarerestoredinreadonlywhencomingbackinbreadcrumbs',asyncfunction(assert){
        assert.expect(2);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        //openarecordinformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        //switchtoeditmode
        awaittestUtils.dom.click($('.o_control_panel.o_form_button_edit'));

        assert.hasClass(actionManager.$('.o_form_view'),'o_form_editable');
        //dosomeotheraction
        awaitactionManager.doAction(4);
        //gobacktoformview
        awaittestUtils.dom.clickLast($('.o_control_panel.breadcrumba'));
        awaittestUtils.nextTick();
        assert.hasClass(actionManager.$('.o_form_view'),'o_form_readonly');

        actionManager.destroy();
    });

    QUnit.test('honorgroup_byspecifiedinactionscontext',asyncfunction(assert){
        assert.expect(5);

        _.findWhere(this.actions,{id:3}).context="{'group_by':'bar'}";
        this.archs['partner,false,search']='<search>'+
            '<group>'+
                '<filtername="foo"string="foo"context="{\'group_by\':\'foo\'}"/>'+
            '</group>'+
        '</search>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(3);

        assert.containsOnce(actionManager,'.o_list_table_grouped',
            "shouldbegrouped");
        assert.containsN(actionManager,'.o_group_header',2,
            "shouldbegroupedby'bar'(twogroups)atfirstload");

        //groupby'bar'usingthesearchview
        awaittestUtils.dom.click($('.o_control_panel.o_cp_bottom_rightbutton:contains(GroupBy)'));
        awaittestUtils.dom.click($('.o_control_panel.o_group_by_menua:first'));

        assert.containsN(actionManager,'.o_group_header',5,
            "shouldbegroupedby'foo'(fivegroups)");

        //removethegroupbyinthesearchview
        awaittestUtils.dom.click($('.o_control_panel.o_searchview.o_facet_remove'));

        assert.containsOnce(actionManager,'.o_list_table_grouped',
            "shouldstillbegrouped");
        assert.containsN(actionManager,'.o_group_header',2,
            "shouldbegroupedby'bar'(twogroups)atreload");

        actionManager.destroy();
    });

    QUnit.test('switchrequesttounknownviewtype',asyncfunction(assert){
        assert.expect(7);

        this.actions.push({
            id:33,
            name:'Partners',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'list'],[1,'kanban']],//noformview
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(33);

        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");

        //trytoopenarecordinaformview
        testUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsOnce(actionManager,'.o_list_view',
            "shouldstilldisplaythelistview");
        assert.containsNone(actionManager,'.o_form_view',
            "shouldnotdisplaytheformview");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',
        ]);

        actionManager.destroy();
    });

    QUnit.test('savecurrentsearch',asyncfunction(assert){
        assert.expect(4);

        testUtils.mock.patch(ListController,{
            getOwnedQueryParams:function(){
                return{
                    context:{
                        shouldBeInFilterContext:true,
                    }
                };
            },
        });

        this.actions.push({
            id:33,
            context:{
                shouldNotBeInFilterContext:false,
            },
            name:'Partners',
            res_model:'partner',
            search_view_id:[1,'acustomsearchview'],
            type:'ir.actions.act_window',
            views:[[false,'list']],
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            env:{
                dataManager:{
                    create_filter:function(filter){
                        assert.strictEqual(filter.domain,`[("bar","=",1)]`,
                            "shouldsavethecorrectdomain");
                        constexpectedContext={
                            group_by:[],//defaultgroupbyisanemptylist
                            shouldBeInFilterContext:true,
                        };
                        assert.deepEqual(filter.context,expectedContext,
                            "shouldsavethecorrectcontext");
                    },
                }
            },
        });
        awaitactionManager.doAction(33);

        assert.containsN(actionManager,'.o_data_row',5,
            "shouldcontain5records");

        //filteronbar
        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"Bar");

        assert.containsN(actionManager,'.o_data_row',2);

        //savefilter
        awaitcpHelpers.toggleFavoriteMenu(actionManager);
        awaitcpHelpers.toggleSaveFavorite(actionManager);
        awaitcpHelpers.editFavoriteName(actionManager,"somename");
        awaitcpHelpers.saveFavorite(actionManager);

        testUtils.mock.unpatch(ListController);
        actionManager.destroy();
    });

    QUnit.test('listwithdefault_orderandfavoritefilterwithnoorderedBy',asyncfunction(assert){
        assert.expect(5);

        this.archs['partner,1,list']='<treedefault_order="foodesc"><fieldname="foo"/></tree>';

        this.actions.push({
            id:100,
            name:'Partners',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[1,'list'],[false,'form']],
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            favoriteFilters:[{
                user_id:[2,"MitchellAdmin"],
                name:'favoritefilter',
                id:5,
                context:{},
                sort:'[]',
                domain:'[("bar","=",1)]'
            }],
        });
        awaitactionManager.doAction(100);

        assert.strictEqual(actionManager.$('.o_list_viewtr.o_data_row.o_data_cell').text(),'zoupyopplopgnapblip',
            'recordshouldbeindescendingorderasdefault_orderapplies');

        awaitcpHelpers.toggleFavoriteMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"favoritefilter");

        assert.strictEqual(actionManager.$('.o_control_panel.o_facet_values').text().trim(),
            'favoritefilter','favoritefiltershouldbeapplied');
        assert.strictEqual(actionManager.$('.o_list_viewtr.o_data_row.o_data_cell').text(),'gnapblip',
            'recordshouldstillbeindescendingorderafterdefault_orderapplied');

        //gotoformviewandcomebacktolistview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        awaittestUtils.dom.click(actionManager.$('.o_control_panel.breadcrumba:eq(0)'));
        assert.strictEqual(actionManager.$('.o_list_viewtr.o_data_row.o_data_cell').text(),'gnapblip',
            'orderofrecordsshouldnotbechanged,whilecomingbackthroughbreadcrumb');

        //removefilter
        awaitcpHelpers.removeFacet(actionManager,0);
        assert.strictEqual(actionManager.$('.o_list_viewtr.o_data_row.o_data_cell').text(),
            'zoupyopplopgnapblip','orderofrecordsshouldnotbechanged,afterremovingcurrentfilter');

        actionManager.destroy();
    });

    QUnit.test("searchmenusarestillavailablewhenswitchingbetweenactions",asyncfunction(assert){
        assert.expect(3);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(1);
        assert.isVisible(actionManager.el.querySelector('.o_search_options.o_dropdown.o_filter_menu'),
            "thesearchoptionsshouldbeavailable");

        awaitactionManager.doAction(3);
        assert.isVisible(actionManager.el.querySelector('.o_search_options.o_dropdown.o_filter_menu'),
            "thesearchoptionsshouldbeavailable");

        //gobackusingthebreadcrumbs
        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:first'));
        assert.isVisible(actionManager.el.querySelector('.o_search_options.o_dropdown.o_filter_menu'),
            "thesearchoptionsshouldbeavailable");

        actionManager.destroy();
    });

    QUnit.test("currentact_windowactionisstoredinsession_storage",asyncfunction(assert){
        assert.expect(1);

        varexpectedAction=_.extend({},_.findWhere(this.actions,{id:3}),{
            context:{},
        });
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                session_storage:SessionStorageService.extend({
                    setItem:function(key,value){
                        assert.strictEqual(value,JSON.stringify(expectedAction),
                            "shouldstoretheexecutedactioninthesessionStorage");
                    },
                }),
            },
        });

        awaitactionManager.doAction(3);

        actionManager.destroy();
    });

    QUnit.test("storeevaluatedcontextofcurrentactioninsession_storage",asyncfunction(assert){
        //thistestensuresthatwedon'tstorestringifiedinstancesof
        //CompoundContextinthesession_storage,astheywouldbemeaningless
        //oncerestored
        assert.expect(1);

        varexpectedAction=_.extend({},_.findWhere(this.actions,{id:4}),{
            context:{
                active_model:'partner',
                active_id:1,
                active_ids:[1],
            },
        });
        varcheckSessionStorage=false;
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                session_storage:SessionStorageService.extend({
                    setItem:function(key,value){
                        if(checkSessionStorage){
                            assert.strictEqual(value,JSON.stringify(expectedAction),
                                "shouldcorrectlystoretheexecutedactioninthesessionStorage");
                        }
                    },
                }),
            },
        });

        //executeanactionandopenarecordinformview
        awaitactionManager.doAction(3);
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        //clickon'Executeaction'button(itexecutesanactionwithaCompoundContextascontext)
        checkSessionStorage=true;
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains(Executeaction)'));

        actionManager.destroy();
    });

    QUnit.test("destroyactionwithlazyloadedcontroller",asyncfunction(assert){
        assert.expect(6);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.loadState({
            action:3,
            id:2,
            view_type:'form',
        });
        assert.containsNone(actionManager,'.o_list_view');
        assert.containsOnce(actionManager,'.o_form_view');
        assert.strictEqual($('.o_control_panel.breadcrumb-item').length,2,
            "thereshouldbetwocontrollersinthebreadcrumbs");
        assert.strictEqual($('.o_control_panel.breadcrumb-item:last').text(),'Secondrecord',
            "breadcrumbsshouldcontainthedisplay_nameoftheopenedrecord");

        awaitactionManager.doAction(1,{clear_breadcrumbs:true});

        assert.containsNone(actionManager,'.o_form_view');
        assert.containsOnce(actionManager,'.o_kanban_view');

        actionManager.destroy();
    });

    QUnit.test('executeactionfromdirty,newrecord,andcomeback',asyncfunction(assert){
        assert.expect(17);

        this.data.partner.fields.bar.default=1;
        this.archs['partner,false,form']='<form>'+
                                                '<fieldname="foo"/>'+
                                                '<fieldname="bar"readonly="1"/>'+
                                            '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='get_formview_action'){
                    returnPromise.resolve({
                        res_id:1,
                        res_model:'partner',
                        type:'ir.actions.act_window',
                        views:[[false,'form']],
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                do_action:function(ev){
                    actionManager.doAction(ev.data.action,{});
                },
            },
        });

        //executeanactionandcreateanewrecord
        awaitactionManager.doAction(3);
        awaittestUtils.dom.click(actionManager.$('.o_list_button_add'));
        assert.containsOnce(actionManager,'.o_form_view.o_form_editable');
        assert.containsOnce(actionManager,'.o_form_uri:contains(Firstrecord)');
        assert.strictEqual(actionManager.$('.o_control_panel.breadcrumb-item').text(),
            "PartnersNew");

        //setformviewdirtyandopenm2orecord
        awaittestUtils.fields.editInput(actionManager.$('input[name=foo]'),'val');
        awaittestUtils.dom.click(actionManager.$('.o_form_uri:contains(Firstrecord)'));
        assert.containsOnce($('body'),'.modal');//confirmdiscarddialog

        //confirmdiscardchanges
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        assert.containsOnce(actionManager,'.o_form_view.o_form_readonly');
        assert.strictEqual(actionManager.$('.o_control_panel.breadcrumb-item').text(),
            "PartnersNewFirstrecord");

        //gobacktoNewusingthebreadcrumbs
        awaittestUtils.dom.click(actionManager.$('.o_control_panel.breadcrumb-item:nth(1)a'));
        assert.containsOnce(actionManager,'.o_form_view.o_form_editable');
        assert.strictEqual(actionManager.$('.o_control_panel.breadcrumb-item').text(),
            "PartnersNew");

        assert.verifySteps([
            '/web/action/load',//action3
            'load_views',//viewsofaction3
            '/web/dataset/search_read',//list
            'onchange',//form(create)
            'get_formview_action',//clickonm2o
            'load_views',//formviewofdynamicaction
            'read',//form
            'onchange',//form(create)
        ]);

        actionManager.destroy();
    });

    QUnit.test('executeacontextualactionfromaformview',asyncfunction(assert){
        assert.expect(4);

        constcontextualAction=this.actions.find(action=>action.id===8);
        contextualAction.context="{}";//needacontexttoevaluate

        constactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:asyncfunction(route,args){
                constres=awaitthis._super(...arguments);
                if(args.method==='load_views'&&args.model==='partner'){
                    assert.strictEqual(args.kwargs.options.toolbar,true,
                        "shouldaskfortoolbarinformation");
                    res.form.toolbar={
                        action:[contextualAction],
                        print:[],
                    };
                }
                returnres;
            },
            intercepts:{
                do_action:function(ev){
                    actionManager.doAction(ev.data.action,{});
                },
            },
        });

        //executeanactionandopenarecord
        awaitactionManager.doAction(3);
        assert.containsOnce(actionManager,'.o_list_view');
        awaittestUtils.dom.click(actionManager.$('.o_data_row:first'));
        assert.containsOnce(actionManager,'.o_form_view');

        //executethecustomactionfromtheactionmenu
        awaitcpHelpers.toggleActionMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,"FavoritePonies");
        assert.containsOnce(actionManager,'.o_list_view');

        actionManager.destroy();
    });

    QUnit.module('Actionsintarget="new"');

    QUnit.test('canexecuteact_windowactionsintarget="new"',asyncfunction(assert){
        assert.expect(7);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(5);

        assert.strictEqual($('.o_technical_modal.o_form_view').length,1,
            "shouldhaverenderedaformviewinamodal");
        assert.hasClass($('.o_technical_modal.modal-body'),'o_act_window',
            "dialogmainelementshouldhaveclassname'o_act_window'");
        assert.hasClass($('.o_technical_modal.o_form_view'),'o_form_editable',
            "formviewshouldbeineditmode");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            'onchange',
        ]);

        actionManager.destroy();
    });

    QUnit.test('chainedactionon_close',asyncfunction(assert){
        assert.expect(3);

        functionon_close(){
            assert.step('CloseAction');
        };

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(5,{on_close:on_close});

        //atarget=newactionshouldn'tactivatetheon_close
        awaitactionManager.doAction(5);
        assert.verifySteps([]);

        //Anact_window_closeshouldtriggertheon_close
        awaitactionManager.doAction(10);
        assert.verifySteps(['CloseAction']);

        actionManager.destroy();
    });

    QUnit.test('footerbuttonsaremovedtothedialogfooter',asyncfunction(assert){
        assert.expect(3);

        this.archs['partner,false,form']='<form>'+
                '<fieldname="display_name"/>'+
                '<footer>'+
                    '<buttonstring="Create"type="object"class="infooter"/>'+
                '</footer>'+
            '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(5);

        assert.containsNone($('.o_technical_modal.modal-body'),'button.infooter',
            "thebuttonshouldnotbeinthebody");
        assert.containsOnce($('.o_technical_modal.modal-footer'),'button.infooter',
            "thebuttonshouldbeinthefooter");
        assert.containsOnce($('.o_technical_modal.modal-footer'),'button',
            "themodalfootershouldonlycontainonebutton");

        actionManager.destroy();
    });

    QUnit.test("Buttonwith`close`attributeclosesdialog",asyncfunction(assert){
        assert.expect(2);
        constactions=[
            {
                id:4,
                name:"PartnersAction4",
                res_model:"partner",
                type:"ir.actions.act_window",
                views:[[false,"form"]],
            },
            {
                id:5,
                name:"CreateaPartner",
                res_model:"partner",
                target:"new",
                type:"ir.actions.act_window",
                views:[["view_ref","form"]],
            },
        ];

        constactionManager=awaitcreateActionManager({
            actions,
            archs:{
                "partner,false,form":`
                    <form>
                        <header>
                            <buttonstring="Opendialog"name="5"type="action"/>
                        </header>
                    </form>
                `,
                "partner,view_ref,form":`
                    <form>
                        <footer>
                            <buttonstring="Iclosethedialog"name="some_method"type="object"close="1"/>
                        </footer>
                    </form>
                `,
                "partner,false,search":"<search></search>",
            },
            data:this.data,
            mockRPC:asyncfunction(route,args){
                if(
                    route==="/web/dataset/call_button"&&
                    args.method==="some_method"
                ){
                    return{
                        tag:"display_notification",
                        type:"ir.actions.client"
                    };
                }
                returnthis._super(...arguments);
            },
        });

        awaitactionManager.doAction(4);
        awaittestUtils.dom.click(`button[name="5"]`);
        assert.strictEqual($(".modal").length,1,"Itshoulddisplayamodal");
        awaittestUtils.dom.click(`button[name="some_method"]`);
        assert.strictEqual($(".modal").length,0,"Itshouldhaveclosedthemodal");

        actionManager.destroy();
    });

    QUnit.test('canexecuteact_windowactionsintarget="new"',asyncfunction(assert){
        assert.expect(5);

        this.actions.push({
            id:999,
            name:'Awindowaction',
            res_model:'partner',
            target:'new',
            type:'ir.actions.act_window',
            views:[[999,'form']],
        });
        this.archs['partner,999,form']=`
            <form>
                <buttonname="method"string="Callmethod"type="object"confirm="Areyousure?"/>
            </form>`;
        this.archs['partner,1000,form']=`<form>Anotheraction</form>`;

        constactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='method'){
                    returnPromise.resolve({
                        id:1000,
                        name:'Anotherwindowaction',
                        res_model:'partner',
                        target:'new',
                        type:'ir.actions.act_window',
                        views:[[1000,'form']],
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(999);

        assert.containsOnce(document.body,'.modalbutton[name=method]');

        awaittestUtils.dom.click($('.modalbutton[name=method]'));

        assert.containsN(document.body,'.modal',2);
        assert.strictEqual($('.modal:last.modal-body').text(),'Areyousure?');

        awaittestUtils.dom.click($('.modal:last.modal-footer.btn-primary'));
        assert.containsOnce(document.body,'.modal');
        assert.strictEqual($('.modal:last.modal-body').text().trim(),'Anotheraction');

        actionManager.destroy();
    });

    QUnit.test('on_attach_callbackiscalledforactionsintarget="new"',asyncfunction(assert){
        assert.expect(4);

        varClientAction=AbstractAction.extend({
            on_attach_callback:function(){
                assert.step('on_attach_callback');
                assert.ok(actionManager.currentDialogController,
                    "thecurrentDialogControllershouldhavebeensetalready");
            },
            start:function(){
                this.$el.addClass('o_test');
            },
        });
        core.action_registry.add('test',ClientAction);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction({
            tag:'test',
            target:'new',
            type:'ir.actions.client',
        });

        assert.strictEqual($('.modal.o_test').length,1,
            "shouldhaverenderedtheclientactioninadialog");
        assert.verifySteps(['on_attach_callback']);

        actionManager.destroy();
        deletecore.action_registry.map.test;
    });

    QUnit.module('Actionsintarget="inline"');

    QUnit.test('formviewsforactionsintarget="inline"openineditmode',asyncfunction(assert){
        assert.expect(5);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(6);

        assert.containsOnce(actionManager,'.o_form_view.o_form_editable',
            "shouldhaverenderedaformviewineditmode");

        assert.verifySteps([
            '/web/action/load',
            'load_views',
            'read',
        ]);

        actionManager.destroy();
    });

    QUnit.module('Actionsintarget="fullscreen"');

    QUnit.test('correctlyexecuteact_windowactionsintarget="fullscreen"',asyncfunction(assert){
        assert.expect(7);

        this.actions[0].target='fullscreen';
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                toggle_fullscreen:function(){
                    assert.step('toggle_fullscreen');
                },
            },
        });
        awaitactionManager.doAction(1);

        assert.strictEqual($('.o_control_panel').length,1,
            "shouldhaverenderedacontrolpanel");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaverenderedakanbanview");
        assert.verifySteps([
            '/web/action/load',
            'load_views',
            '/web/dataset/search_read',
            'toggle_fullscreen',
        ]);

        actionManager.destroy();
    });

    QUnit.test('fullscreenonactionchange:backtoa"current"action',asyncfunction(assert){
        assert.expect(3);

        this.actions[0].target='fullscreen';
        this.archs['partner,false,form']='<form>'+
                                            '<buttonname="1"type="action"class="oe_stat_button"/>'+
                                        '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                toggle_fullscreen:function(ev){
                    varfullscreen=ev.data.fullscreen;

                    switch(toggleFullscreenCalls){
                        case0:
                            assert.strictEqual(fullscreen,false);
                            break;
                        case1:
                            assert.strictEqual(fullscreen,true);
                            break;
                        case2:
                            assert.strictEqual(fullscreen,false);
                            break;
                    }
                },
            },

        });

        vartoggleFullscreenCalls=0;
        awaitactionManager.doAction(6);

        toggleFullscreenCalls=1;
        awaittestUtils.dom.click(actionManager.$('button[name=1]'));

        toggleFullscreenCalls=2;
        awaittestUtils.dom.click(actionManager.$('.breadcrumblia:first'));

        actionManager.destroy();
    });

    QUnit.test('fullscreenonactionchange:all"fullscreen"actions',asyncfunction(assert){
        assert.expect(3);

        this.actions[5].target='fullscreen';
        this.archs['partner,false,form']='<form>'+
                                            '<buttonname="1"type="action"class="oe_stat_button"/>'+
                                        '</form>';

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                toggle_fullscreen:function(ev){
                    varfullscreen=ev.data.fullscreen;
                    assert.strictEqual(fullscreen,true);
                },
            },
        });

        awaitactionManager.doAction(6);

        awaittestUtils.dom.click(actionManager.$('button[name=1]'));

        awaittestUtils.dom.click(actionManager.$('.breadcrumblia:first'));

        actionManager.destroy();
    });

    QUnit.module('"ir.actions.act_window_close"actions');

    QUnit.test('closethecurrentlyopeneddialog',asyncfunction(assert){
        assert.expect(2);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        //executeanactionintarget="new"
        awaitactionManager.doAction(5);
        assert.strictEqual($('.o_technical_modal.o_form_view').length,1,
            "shouldhaverenderedaformviewinamodal");

        //executean'ir.actions.act_window_close'action
        awaitactionManager.doAction({
            type:'ir.actions.act_window_close',
        });
        assert.strictEqual($('.o_technical_modal').length,0,
            "shouldhaveclosedthemodal");

        actionManager.destroy();
    });

    QUnit.test('execute"on_close"onlyifthereisnodialogtoclose',asyncfunction(assert){
        assert.expect(3);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        //executeanactionintarget="new"
        awaitactionManager.doAction(5);

        varoptions={
            on_close:assert.step.bind(assert,'on_close'),
        };
        //executean'ir.actions.act_window_close'action
        //shouldnotcall'on_close'asthereisadialogtoclose
        awaitactionManager.doAction({type:'ir.actions.act_window_close'},options);

        assert.verifySteps([]);

        //executeagainan'ir.actions.act_window_close'action
        //shouldcall'on_close'asthereisnodialogtoclose
        awaitactionManager.doAction({type:'ir.actions.act_window_close'},options);

        assert.verifySteps(['on_close']);

        actionManager.destroy();
    });

    QUnit.test('doActionresolvedwithanaction',asyncfunction(assert){
        assert.expect(4);

        this.actions.push({
            id:21,
            name:'ACloseAction',
            type:'ir.actions.act_window_close',
        });

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(21).then(function(action){
            assert.ok(action,"doActionshouldberesolvedwithanaction");
            assert.strictEqual(action.id,21,
                "shouldberesolvedwithcorrectactionid");
            assert.strictEqual(action.name,'ACloseAction',
                "shouldberesolvedwithcorrectactionname");
            assert.strictEqual(action.type,'ir.actions.act_window_close',
                "shouldberesolvedwithcorrectactiontype");
            actionManager.destroy();
        });
    });

    QUnit.test('closeactionwithprovidedinfos',asyncfunction(assert){
        assert.expect(1);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        varoptions={
            on_close:function(infos){
                assert.strictEqual(infos,'justfortesting',
                    "shouldhavethecorrectcloseinfos");
            }
        };

        awaitactionManager.doAction({
            type:'ir.actions.act_window_close',
            infos:'justfortesting',
        },options);

        actionManager.destroy();
    });

    QUnit.test('historybackcallson_closehandlerofdialogaction',asyncfunction(assert){
        assert.expect(2);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        //openanewdialogform
        awaitactionManager.doAction(this.actions[4],{
            on_close:function(){
                assert.step('on_close');
            },
        });

        actionManager.trigger_up('history_back');
        assert.verifySteps(['on_close'],"shouldhavecalledtheon_closehandler");

        actionManager.destroy();
    });

    QUnit.test('properlydropclientactionsafternewactionisinitiated',asyncfunction(assert){
        assert.expect(1);

        varslowWillStartDef=testUtils.makeTestPromise();

        varClientAction=AbstractAction.extend({
            willStart:function(){
                returnslowWillStartDef;
            },
        });

        core.action_registry.add('slowAction',ClientAction);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        actionManager.doAction('slowAction');
        actionManager.doAction(4);
        slowWillStartDef.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(actionManager,'.o_kanban_view',
            'shouldhaveloadedakanbanview');

        actionManager.destroy();
        deletecore.action_registry.map.slowAction;
    });

    QUnit.test('abstractactiondoesnotcrashonnavigation_moves',asyncfunction(assert){
        assert.expect(1);
        varClientAction=AbstractAction.extend({
        });
        core.action_registry.add('ClientAction',ClientAction);
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction('ClientAction');
        actionManager.trigger_up('navigation_move',{direction:'down'});

        assert.ok(true);//noerrorsoit'sgood
        actionManager.destroy();
        deletecore.action_registry.ClientAction;
    });

    QUnit.test('fieldsinabstractactiondoesnotcrashonnavigation_moves',asyncfunction(assert){
        assert.expect(1);
        //createaclientactionwith2inputfield
        varinputWidget;
        varsecondInputWidget;
        varClientAction=AbstractAction.extend(StandaloneFieldManagerMixin,{
            init:function(){
                this._super.apply(this,arguments);
                StandaloneFieldManagerMixin.init.call(this);
            },
            start:function(){
                var_self=this;

                returnthis.model.makeRecord('partner',[{
                    name:'display_name',
                    type:'char',
                }]).then(function(recordID){
                    varrecord=_self.model.get(recordID);
                    inputWidget=newBasicFields.InputField(_self,'display_name',record,{mode:'edit',});
                    _self._registerWidget(recordID,'display_name',inputWidget);

                    secondInputWidget=newBasicFields.InputField(_self,'display_name',record,{mode:'edit',});
                    secondInputWidget.attrs={className:"secondField"};
                    _self._registerWidget(recordID,'display_name',secondInputWidget);

                    inputWidget.appendTo(_self.$el);
                    secondInputWidget.appendTo(_self.$el);
                });
            }
        });
        core.action_registry.add('ClientAction',ClientAction);
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction('ClientAction');
        inputWidget.$el[0].focus();
        varevent=$.Event('keydown',{
            which:$.ui.keyCode.TAB,
            keyCode:$.ui.keyCode.TAB,
        });
        $(inputWidget.$el[0]).trigger(event);

        assert.notOk(event.isDefaultPrevented(),
            "thekeyboardeventdefaultshouldnotbeprevented");//nocrashisgood
        actionManager.destroy();
        deletecore.action_registry.ClientAction;
    });

    QUnit.test('webclientisnotdeadlockedwhenaviewcrashes',asyncfunction(assert){
        assert.expect(3);

        varreadOnFirstRecordDef=testUtils.makeTestPromise();

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='read'&&args.args[0][0]===1){
                    returnreadOnFirstRecordDef;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        awaitactionManager.doAction(3);

        //openfirstrecordinformview.thiswillcrashandwillnot
        //displayaformview
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));

        readOnFirstRecordDef.reject("notworkingasintended");

        assert.containsOnce(actionManager,'.o_list_view',
            "thereshouldstillbealistviewindom");

        //openanotherrecord,thereadwillnotcrash
        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:eq(2)'));

        assert.containsNone(actionManager,'.o_list_view',
            "thereshouldnotbealistviewindom");

        assert.containsOnce(actionManager,'.o_form_view',
            "thereshouldbeaformviewindom");

        actionManager.destroy();
    });

    QUnit.test('data-mobileattributeonactionbutton,indesktop',asyncfunction(assert){
        assert.expect(2);

        testUtils.mock.patch(ActionManager,{
            doAction(action,options){
                assert.strictEqual(options.plop,undefined);
                returnthis._super(...arguments);
            },
        });

        this.archs['partner,75,kanban']=`
            <kanban>
                <templates>
                    <tt-name="kanban-box">
                        <divclass="oe_kanban_global_click">
                            <fieldname="display_name"/>
                            <button
                                name="1"
                                string="Executeaction"
                                type="action"
                                data-mobile='{"plop":28}'/>
                        </div>
                    </t>
                </templates>
            </kanban>`;

        this.actions.push({
            id:100,
            name:'action100',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[75,'kanban']],
        });

        constactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data
        });

        awaitactionManager.doAction(100,{});
        awaittestUtils.dom.click(actionManager.$('button[data-mobile]:first'));

        actionManager.destroy();
        testUtils.mock.unpatch(ActionManager);
    });

    QUnit.module('SearchViewAction');

    QUnit.test('searchviewshouldkeepfocusduringdo_search',asyncfunction(assert){
        assert.expect(5);

        /*Oneshouldbeabletotypesomethinginthesearchview,pressonenterto
         *makethefacetandtriggerthesearch,thendothisprocess
         *overandoveragainseamlessly.
         *Verifyingtheinput'svalueisalottrickierthanverifyingthesearch_read
         *becauseofhownativeeventsarehandledintests
         */

        varsearchPromise=testUtils.makeTestPromise();

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step('search_read'+args.domain);
                    if(_.isEqual(args.domain,[['foo','ilike','m']])){
                        returnsearchPromise.then(this._super.bind(this,route,args));
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(3);

        awaitcpHelpers.editSearch(actionManager,"m");
        awaitcpHelpers.validateSearch(actionManager);

        assert.verifySteps(["search_read","search_readfoo,ilike,m"]);

        //Triggeringthedo_searchabovewillkillthecurrentsearchviewInput
        awaitcpHelpers.editSearch(actionManager,"o");

        //Wehavesomethingintheinputofthesearchview.Makingthesearch_read
        //returnatthispointwilltriggertheredrawoftheview.
        //Howeverwewanttoholdontowhatwejusttyped
        searchPromise.resolve();
        awaitcpHelpers.validateSearch(actionManager);

        assert.verifySteps(["search_read|,foo,ilike,m,foo,ilike,o"]);

        actionManager.destroy();
    });

    QUnit.test('CalltwiceclearUncommittedChangesinarowdoesnotdisplaytwicethediscardwarning',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            intercepts:{
                clear_uncommitted_changes:function(){
                    actionManager.clearUncommittedChanges();
                },
            },
        });

        //executeanactionandeditexistingrecord
        awaitactionManager.doAction(3);

        awaittestUtils.dom.click(actionManager.$('.o_list_view.o_data_row:first'));
        assert.containsOnce(actionManager,'.o_form_view.o_form_readonly');

        awaittestUtils.dom.click($('.o_control_panel.o_form_button_edit'));
        assert.containsOnce(actionManager,'.o_form_view.o_form_editable');

        awaittestUtils.fields.editInput(actionManager.$('input[name=foo]'),'val');
        actionManager.trigger_up('clear_uncommitted_changes');
        awaittestUtils.nextTick();

        assert.containsOnce($('body'),'.modal');//confirmdiscarddialog
        //confirmdiscardchanges
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        actionManager.trigger_up('clear_uncommitted_changes');
        awaittestUtils.nextTick();

        assert.containsNone($('body'),'.modal');

        actionManager.destroy();
    });
});

});
