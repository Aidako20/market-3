flectra.define('web.kanban_tests',function(require){
"usestrict";

varAbstractField=require('web.AbstractField');
constDomain=require('web.Domain');
varfieldRegistry=require('web.field_registry');
constFormRenderer=require("web.FormRenderer");
varKanbanColumnProgressBar=require('web.KanbanColumnProgressBar');
varkanbanExamplesRegistry=require('web.kanban_examples_registry');
varKanbanRenderer=require('web.KanbanRenderer');
varKanbanView=require('web.KanbanView');
varmixins=require('web.mixins');
vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');
varwidgetRegistry=require('web.widget_registry');

varmakeTestPromise=testUtils.makeTestPromise;
varnextTick=testUtils.nextTick;
constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;

QUnit.module('Views',{
    before:function(){
        this._initialKanbanProgressBarAnimate=KanbanColumnProgressBar.prototype.ANIMATE;
        KanbanColumnProgressBar.prototype.ANIMATE=false;
    },
    after:function(){
        KanbanColumnProgressBar.prototype.ANIMATE=this._initialKanbanProgressBarAnimate;
    },
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    foo:{string:"Foo",type:"char"},
                    bar:{string:"Bar",type:"boolean"},
                    int_field:{string:"int_field",type:"integer",sortable:true},
                    qux:{string:"myfloat",type:"float"},
                    product_id:{string:"something_id",type:"many2one",relation:"product"},
                    category_ids:{string:"categories",type:"many2many",relation:'category'},
                    state:{string:"State",type:"selection",selection:[["abc","ABC"],["def","DEF"],["ghi","GHI"]]},
                    date:{string:"DateField",type:'date'},
                    datetime:{string:"DatetimeField",type:'datetime'},
                    image:{string:"Image",type:"binary"},
                    displayed_image_id:{string:"cover",type:"many2one",relation:"ir.attachment"},
                    currency_id:{string:"Currency",type:"many2one",relation:"currency",default:1},
                    salary:{string:"Monetaryfield",type:"monetary"},
                },
                records:[
                    {id:1,bar:true,foo:"yop",int_field:10,qux:0.4,product_id:3,state:"abc",category_ids:[],'image':'R0lGODlhAQABAAD/ACwAAAAAAQABAAACAA==',salary:1750,currency_id:1},
                    {id:2,bar:true,foo:"blip",int_field:9,qux:13,product_id:5,state:"def",category_ids:[6],salary:1500,currency_id:1},
                    {id:3,bar:true,foo:"gnap",int_field:17,qux:-3,product_id:3,state:"ghi",category_ids:[7],salary:2000,currency_id:2},
                    {id:4,bar:false,foo:"blip",int_field:-4,qux:9,product_id:5,state:"ghi",category_ids:[],salary:2222,currency_id:1},
                ]
            },
            product:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    name:{string:"DisplayName",type:"char"},
                },
                records:[
                    {id:3,name:"hello"},
                    {id:5,name:"xmo"},
                ]
            },
            category:{
                fields:{
                    name:{string:"CategoryName",type:"char"},
                    color:{string:"Colorindex",type:"integer"},
                },
                records:[
                    {id:6,name:"gold",color:2},
                    {id:7,name:"silver",color:5},
                ]
            },
            'ir.attachment':{
                fields:{
                    mimetype:{type:"char"},
                    name:{type:"char"},
                    res_model:{type:"char"},
                    res_id:{type:"integer"},
                },
                records:[
                    {id:1,name:"1.png",mimetype:'image/png',res_model:'partner',res_id:1},
                    {id:2,name:"2.png",mimetype:'image/png',res_model:'partner',res_id:2},
                ]
            },
            'currency':{
                fields:{
                    symbol:{string:"Symbol",type:"char"},
                    position:{
                        string:"Position",
                        type:"selection",
                        selection:[['after','A'],['before','B']],
                    },
                },
                records:[
                    {id:1,display_name:"USD",symbol:'$',position:'before'},
                    {id:2,display_name:"EUR",symbol:'€',position:'after'},
                ],
            },
        };
    },
},function(){

    QUnit.module('KanbanView');

    QUnit.test('basicungroupedrendering',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                    '<div>'+
                    '<tt-esc="record.foo.value"/>'+
                    '<fieldname="foo"/>'+
                    '</div>'+
                '</t></templates></kanban>',
            mockRPC:function(route,args){
                assert.ok(args.context.bin_size,
                    "shouldnotrequestdirectbinarypayload");
                returnthis._super(route,args);
            },
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_ungrouped');
        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_test');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);
        assert.containsN(kanban,'.o_kanban_ghost',6);
        assert.containsOnce(kanban,'.o_kanban_record:contains(gnap)');
        kanban.destroy();
    });

    QUnit.test('basicgroupedrendering',asyncfunction(assert){
        assert.expect(13);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    //thelazyoptionisimportant,sotheservercanfillin
                    //theemptygroups
                    assert.ok(args.kwargs.lazy,"shoulduselazyread_group");
                }
                returnthis._super(route,args);
            },
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_grouped');
        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_test');
        assert.containsN(kanban,'.o_kanban_group',2);
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',3);

        //checkavailableactionsinkanbanheader'sconfigdropdown
        assert.containsOnce(kanban,'.o_kanban_header:first.o_kanban_config.o_kanban_toggle_fold');
        assert.containsNone(kanban,'.o_kanban_header:first.o_kanban_config.o_column_edit');
        assert.containsNone(kanban,'.o_kanban_header:first.o_kanban_config.o_column_delete');
        assert.containsNone(kanban,'.o_kanban_header:first.o_kanban_config.o_column_archive_records');
        assert.containsNone(kanban,'.o_kanban_header:first.o_kanban_config.o_column_unarchive_records');

        //thenextlinemakessurethatreloadworksproperly. Itlooksuseless,
        //butitactuallytestthatagroupedlocalrecordcanbereloadedwithout
        //changingitsresult.
        awaitkanban.reload(kanban);
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',3);

        kanban.destroy();
    });

    QUnit.test('basicgroupedrenderingwithactivefield(archivablebydefault)',asyncfunction(assert){
        //vardone=assert.async();
        assert.expect(9);

        //addactivefieldonpartnermodelandmakeallrecordsactive
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        varenvIDs=[1,2,3,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="active"/>'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/action_archive'){
                    varpartnerIDS=args.args[0];
                    varrecords=this.data.partner.records
                    _.each(partnerIDS,function(partnerID){
                        _.find(records,function(record){
                            returnrecord.id===partnerID;
                        }).active=false;
                    })
                    this.data.partner.records[0].active;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //checkarchive/restoreallactionsinkanbanheader'sconfigdropdown
        assert.containsOnce(kanban,'.o_kanban_header:first.o_kanban_config.o_column_archive_records');
        assert.containsOnce(kanban,'.o_kanban_header:first.o_kanban_config.o_column_unarchive_records');
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //archivetherecordsofthefirstcolumn
        assert.containsN(kanban,'.o_kanban_group:last.o_kanban_record',3);

        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_archive_records'));
        assert.containsOnce(document.body,'.modal',"aconfirmmodalshouldbedisplayed");
        awaittestUtils.modal.clickButton('Cancel');
        assert.containsN(kanban,'.o_kanban_group:last.o_kanban_record',3,"stilllastcolumnshouldcontain3records");
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_archive_records'));
        assert.ok($('.modal').length,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.modal.clickButton('Ok');
        assert.containsNone(kanban,'.o_kanban_group:last.o_kanban_record',"lastcolumnshouldnotcontainanyrecords");
        envIDs=[4];
        assert.deepEqual(kanban.exportState().resIds,envIDs);
        kanban.destroy();
    });

    QUnit.test('basicgroupedrenderingwithactivefieldandarchiveenabled(archivabletrue)',asyncfunction(assert){
        assert.expect(7);

        //addactivefieldonpartnermodelandmakeallrecordsactive
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        varenvIDs=[1,2,3,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"archivable="true">'+
                        '<fieldname="active"/>'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/action_archive'){
                    varpartnerIDS=args.args[0];
                    varrecords=this.data.partner.records
                    _.each(partnerIDS,function(partnerID){
                        _.find(records,function(record){
                            returnrecord.id===partnerID;
                        }).active=false;
                    })
                    this.data.partner.records[0].active;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //checkarchive/restoreallactionsinkanbanheader'sconfigdropdown
        assert.ok(kanban.$('.o_kanban_header:first.o_kanban_config.o_column_archive_records').length,"shouldbeabletoarchivealltherecords");
        assert.ok(kanban.$('.o_kanban_header:first.o_kanban_config.o_column_unarchive_records').length,"shouldbeabletorestorealltherecords");

        //archivetherecordsofthefirstcolumn
        assert.containsN(kanban,'.o_kanban_group:last.o_kanban_record',3,
            "lastcolumnshouldcontain3records");
        envIDs=[4];
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_archive_records'));
        assert.ok($('.modal').length,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.modal.clickButton('Cancel');//Clickon'Cancel'
        assert.containsN(kanban,'.o_kanban_group:last.o_kanban_record',3,"stilllastcolumnshouldcontain3records");
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_archive_records'));
        assert.ok($('.modal').length,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.modal.clickButton('Ok');//Clickon'Ok'
        assert.containsNone(kanban,'.o_kanban_group:last.o_kanban_record',"lastcolumnshouldnotcontainanyrecords");
        kanban.destroy();
    });

    QUnit.test('basicgroupedrenderingwithactivefieldandhiddenarchivebuttons(archivablefalse)',asyncfunction(assert){
        assert.expect(2);

        //addactivefieldonpartnermodelandmakeallrecordsactive
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        varenvIDs=[1,2,3,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"archivable="false">'+
                        '<fieldname="active"/>'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        //checkarchive/restoreallactionsinkanbanheader'sconfigdropdown
        assert.strictEqual(
            kanban.$('.o_kanban_header:first.o_kanban_config.o_column_archive_records').length,0,
            "shouldnotbeabletoarchivealltherecords");
        assert.strictEqual(
            kanban.$('.o_kanban_header:first.o_kanban_config.o_column_unarchive_records').length,0,
            "shouldnotbeabletorestorealltherecords");
        kanban.destroy();
    });

    QUnit.test('contextcanbeusedinkanbantemplate',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                    '<templates>'+
                        '<tt-name="kanban-box">'+
                            '<div>'+
                                '<tt-if="context.some_key">'+
                                    '<fieldname="foo"/>'+
                                '</t>'+
                            '</div>'+
                        '</t>'+
                    '</templates>'+
                '</kanban>',
            context:{some_key:1},
            domain:[['id','=',1]],
        });

        assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,1,
            "thereshouldbeonerecord");
        assert.strictEqual(form.$('.o_kanban_recordspan:contains(yop)').length,1,
            "conditioninthekanbantemplateshouldhavebeencorrectlyevaluated");

        form.destroy();
    });

    QUnit.test('pagershouldbehiddeningroupedmode',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        assert.containsNone(kanban,'.o_pager');

        kanban.destroy();
    });

    QUnit.test('pager,ungrouped,withdefaultlimit',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            mockRPC:function(route,args){
                assert.strictEqual(args.limit,40,"defaultlimitshouldbe40inKanban");
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(kanban,'.o_pager');
        assert.strictEqual(cpHelpers.getPagerSize(kanban),"4","pager'ssizeshouldbe4");
        kanban.destroy();
    });

    QUnit.test('pager,ungrouped,withlimitgiveninoptions',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            mockRPC:function(route,args){
                assert.strictEqual(args.limit,2,"limitshouldbe2");
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                limit:2,
            },
        });

        assert.strictEqual(cpHelpers.getPagerValue(kanban),"1-2","pager'slimitshouldbe2");
        assert.strictEqual(cpHelpers.getPagerSize(kanban),"4","pager'ssizeshouldbe4");
        kanban.destroy();
    });

    QUnit.test('pager,ungrouped,withlimitsetonarchandgiveninoptions',asyncfunction(assert){
        assert.expect(3);

        //thelimitgiveninthearchshouldtakethepriorityovertheonegiveninoptions
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"limit="3">'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            mockRPC:function(route,args){
                assert.strictEqual(args.limit,3,"limitshouldbe3");
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                limit:2,
            },
        });

        assert.strictEqual(cpHelpers.getPagerValue(kanban),"1-3","pager'slimitshouldbe3");
        assert.strictEqual(cpHelpers.getPagerSize(kanban),"4","pager'ssizeshouldbe4");
        kanban.destroy();
    });

    QUnit.test('pager,ungrouped,deletingallrecordsfromlastpageshouldmovetopreviouspage',asyncfunction(assert){
        assert.expect(5);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                `<kanbanclass="o_kanban_test"limit="3">
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <div><arole="menuitem"type="delete"class="dropdown-item">Delete</a></div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
        });

        assert.strictEqual(cpHelpers.getPagerValue(kanban),"1-3",
            "shouldhave3recordsoncurrentpage");
        assert.strictEqual(cpHelpers.getPagerSize(kanban),"4",
            "shouldhave4records");

        //movetonextpage
        awaitcpHelpers.pagerNext(kanban);
        assert.strictEqual(cpHelpers.getPagerValue(kanban),"4-4",
            "shouldbeonsecondpage");

        //deletearecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_record:firsta:first'));
        awaittestUtils.dom.click($('.modal-footerbutton:first'));
        assert.strictEqual(cpHelpers.getPagerValue(kanban),"1-3",
            "shouldhave1pageonly");
        assert.strictEqual(cpHelpers.getPagerSize(kanban),"3",
            "shouldhave4records");

        kanban.destroy();
    });

    QUnit.test('createingroupedonm2o',asyncfunction(assert){
        assert.expect(5);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'ui-sortable',
            "columnsaresortablewhengroupedbyam2ofield");
        assert.hasClass(kanban.$buttons.find('.o-kanban-button-new'),'btn-primary',
            "'create'buttonshouldbebtn-primaryforgroupedkanbanwithatleastonecolumn");
        assert.hasClass(kanban.$('.o_kanban_view>div:last'),'o_column_quick_create',
            "columnquickcreateshouldbeenabledwhengroupedbyamany2onefield)");

        awaittestUtils.kanban.clickCreate(kanban);//Clickon'Create'
        assert.hasClass(kanban.$('.o_kanban_group:first()>div:nth(1)'),'o_kanban_quick_create',
            "clickingoncreateshouldopenthequick_createinthefirstcolumn");

        assert.ok(kanban.$('span.o_column_title:contains(hello)').length,
            "shouldhaveacolumntitlewithavaluefromthemany2one");
        kanban.destroy();
    });

    QUnit.test('createingroupedonchar',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['foo'],
        });

        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'ui-sortable',
            "columnsaren'tsortablewhennotgroupedbyam2ofield");
        assert.containsN(kanban,'.o_kanban_group',3,"shouldhave"+3+"columns");
        assert.strictEqual(kanban.$('.o_kanban_group:first().o_column_title').text(),"yop",
            "'yop'columnshouldbethefirstcolumn");
        assert.doesNotHaveClass(kanban.$('.o_kanban_view>div:last'),'o_column_quick_create',
            "columnquickcreateshouldbedisabledwhennotgroupedbyamany2onefield)");
        kanban.destroy();
    });

    QUnit.test('quickcreaterecordwithoutquick_create_view',asyncfunction(assert){
        assert.expect(16);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='name_create'){
                    assert.strictEqual(args.args[0],'newpartner',
                        "shouldsendthecorrectvalue");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clickon'Create'->shouldopenthequickcreateinthefirstcolumn
        awaittestUtils.kanban.clickCreate(kanban);
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');

        assert.strictEqual($quickCreate.length,1,
            "shouldhaveaquickcreateelementinthefirstcolumn");
        assert.strictEqual($quickCreate.find('.o_form_view.o_xxs_form_view').length,1,
            "shouldhaverenderedanXXSformview");
        assert.strictEqual($quickCreate.find('input').length,1,
            "shouldhaveonlyoneinput");
        assert.hasClass($quickCreate.find('input'),'o_required_modifier',
            "thefieldshouldberequired");
        assert.strictEqual($quickCreate.find('input[placeholder=Title]').length,1,
            "inputplaceholdershouldbe'Title'");

        //fillthequickcreateandvalidate
        awaittestUtils.fields.editInput($quickCreate.find('input'),'newpartner');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldcontaintworecords");

        assert.verifySteps([
            'web_read_group',//initialread_group
            '/web/dataset/search_read',//initialsearch_read(firstcolumn)
            '/web/dataset/search_read',//initialsearch_read(secondcolumn)
            'onchange',//quickcreate
            'name_create',//shouldperformaname_createtocreatetherecord
            'read',//readthecreatedrecord
            'onchange',//reopenthequickcreateautomatically
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordwithquick_create_view',asyncfunction(assert){
        assert.expect(19);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="state"widget="priority"/>'+
                '</form>',
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{
                        foo:'newpartner',
                        int_field:4,
                        state:'def',
                    },"shouldsendthecorrectvalues");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(kanban,'.o_control_panel','shouldhaveonecontrolpanel');
        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clickon'Create'->shouldopenthequickcreateinthefirstcolumn
        awaittestUtils.kanban.clickCreate(kanban);
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');

        assert.strictEqual($quickCreate.length,1,
            "shouldhaveaquickcreateelementinthefirstcolumn");
        assert.strictEqual($quickCreate.find('.o_form_view.o_xxs_form_view').length,1,
            "shouldhaverenderedanXXSformview");
        assert.containsOnce(kanban,'.o_control_panel','shouldnothaveinstantiatedanextracontrolpanel');
        assert.strictEqual($quickCreate.find('input').length,2,
            "shouldhavetwoinputs");
        assert.strictEqual($quickCreate.find('.o_field_widget').length,3,
            "shouldhaverenderedthreewidgets");

        //fillthequickcreateandvalidate
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=foo]'),'newpartner');
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=int_field]'),'4');
        awaittestUtils.dom.click($quickCreate.find('.o_field_widget[name=state].o_priority_star:first'));
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldcontaintworecords");

        assert.verifySteps([
            'web_read_group',//initialread_group
            '/web/dataset/search_read',//initialsearch_read(firstcolumn)
            '/web/dataset/search_read',//initialsearch_read(secondcolumn)
            'load_views',//formviewinquickcreate
            'onchange',//quickcreate
            'create',//shouldperformacreatetocreatetherecord
            'read',//readthecreatedrecord
            'load_views',//formviewinquickcreate(isactuallyincache)
            'onchange',//reopenthequickcreateautomatically
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedonm2o(noquick_create_view)',asyncfunction(assert){
        assert.expect(12);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='name_create'){
                    assert.strictEqual(args.args[0],'newpartner',
                        "shouldsendthecorrectvalue");
                    assert.deepEqual(args.kwargs.context,{
                        default_product_id:3,
                        default_qux:2.5,
                    },"shouldsendthecorrectcontext");
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                context:{default_qux:2.5},
            },
        });

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldcontaintworecords");

        //clickon'Create',fillthequickcreateandvalidate
        awaittestUtils.kanban.clickCreate(kanban);
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'newpartner');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',3,
            "firstcolumnshouldcontainthreerecords");

        assert.verifySteps([
            'web_read_group',//initialread_group
            '/web/dataset/search_read',//initialsearch_read(firstcolumn)
            '/web/dataset/search_read',//initialsearch_read(secondcolumn)
            'onchange',//quickcreate
            'name_create',//shouldperformaname_createtocreatetherecord
            'read',//readthecreatedrecord
            'onchange',//reopenthequickcreateautomatically
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedonm2o(withquick_create_view)',asyncfunction(assert){
        assert.expect(14);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="state"widget="priority"/>'+
                '</form>',
            },
            groupBy:['product_id'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{
                        foo:'newpartner',
                        int_field:4,
                        state:'def',
                    },"shouldsendthecorrectvalues");
                    assert.deepEqual(args.kwargs.context,{
                        default_product_id:3,
                        default_qux:2.5,
                    },"shouldsendthecorrectcontext");
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                context:{default_qux:2.5},
            },
        });

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldcontaintworecords");

        //clickon'Create',fillthequickcreateandvalidate
        awaittestUtils.kanban.clickCreate(kanban);
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=foo]'),'newpartner');
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=int_field]'),'4');
        awaittestUtils.dom.click($quickCreate.find('.o_field_widget[name=state].o_priority_star:first'));
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',3,
            "firstcolumnshouldcontainthreerecords");

        assert.verifySteps([
            'web_read_group',//initialread_group
            '/web/dataset/search_read',//initialsearch_read(firstcolumn)
            '/web/dataset/search_read',//initialsearch_read(secondcolumn)
            'load_views',//formviewinquickcreate
            'onchange',//quickcreate
            'create',//shouldperformacreatetocreatetherecord
            'read',//readthecreatedrecord
            'load_views',//formviewinquickcreate(isactuallyincache)
            'onchange',//reopenthequickcreateautomatically
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordwithdefaultvaluesandonchanges',asyncfunction(assert){
        assert.expect(10);

        this.data.partner.fields.int_field.default=4;
        this.data.partner.onchanges={
            foo:function(obj){
                if(obj.foo){
                    obj.int_field=8;
                }
            },
        };

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        //clickon'Create'->shouldopenthequickcreateinthefirstcolumn
        awaittestUtils.kanban.clickCreate(kanban);
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');

        assert.strictEqual($quickCreate.length,1,
            "shouldhaveaquickcreateelementinthefirstcolumn");
        assert.strictEqual($quickCreate.find('.o_field_widget[name=int_field]').val(),'4',
            "defaultvalueshouldbeset");

        //fillthe'foo'field->shouldtriggertheonchange
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=foo]'),'newpartner');

        assert.strictEqual($quickCreate.find('.o_field_widget[name=int_field]').val(),'8',
            "onchangeshouldhavebeentriggered");

        assert.verifySteps([
            'web_read_group',//initialread_group
            '/web/dataset/search_read',//initialsearch_read(firstcolumn)
            '/web/dataset/search_read',//initialsearch_read(secondcolumn)
            'load_views',//formviewinquickcreate
            'onchange',//quickcreate
            'onchange',//onchangedueto'foo'fieldchange
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordwithquick_create_view:modifiers',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanquick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"required="1"/>'+
                    '<fieldname="int_field"attrs=\'{"invisible":[["foo","=",false]]}\'/>'+
                '</form>',
            },
            groupBy:['bar'],
        });

        //createanewrecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:first.o_kanban_quick_add'));
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');

        assert.hasClass($quickCreate.find('.o_field_widget[name=foo]'),'o_required_modifier',
            "foofieldshouldberequired");
        assert.hasClass($quickCreate.find('.o_field_widget[name=int_field]'),'o_invisible_modifier',
            "int_fieldshouldbeinvisible");

        //fill'foo'field
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=foo]'),'newpartner');

        assert.doesNotHaveClass($quickCreate.find('.o_field_widget[name=int_field]'),'o_invisible_modifier',
            "int_fieldshouldnowbevisible");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordandchangestateingroupedmode',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.kanban_state={
            string:"KanbanState",
            type:"selection",
            selection:[["normal","Grey"],["done","Green"],["blocked","Red"]],
        };

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                        '<divclass="oe_kanban_bottom_right">'+
                        '<fieldname="kanban_state"widget="state_selection"/>'+
                        '</div>'+
                        '</t></templates>'+
                  '</kanban>',
            groupBy:['foo'],
        });

        //Quickcreatekanbanrecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        var$quickAdd=kanban.$('.o_kanban_quick_create');
        $quickAdd.find('.o_input').val('Test');
        awaittestUtils.dom.click($quickAdd.find('.o_kanban_add'));

        //Selectstateinkanban
        awaittestUtils.dom.click(kanban.$('.o_status').first());
        awaittestUtils.dom.click(kanban.$('.o_selection.dropdown-item:first'));
        assert.hasClass(kanban.$('.o_status').first(),'o_status_green',
            "Kanbanstateshouldbedone(Green)");
        kanban.destroy();
    });

    QUnit.test('windowresizeshouldnotchangequickcreateformsize',asyncfunction(assert){
        assert.expect(2);

        testUtils.mock.patch(FormRenderer,{
            start:function(){
                this._super.apply(this,arguments);
                window.addEventListener("resize",this._applyFormSizeClass.bind(this));
            },

        });
        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        //clicktoaddanelementandcancelthequickcreationbypressingESC
        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_header.o_kanban_quick_addi'));

        constquickCreate=kanban.el.querySelector('.o_kanban_quick_create');
        assert.hasClass(quickCreate.querySelector('.o_form_view'),"o_xxs_form_view");

        //triggerwindowresizeexplicitlytocall_applyFormSizeClass
        window.dispatchEvent(newEvent('resize'));
        assert.hasClass(quickCreate.querySelector('.o_form_view'),'o_xxs_form_view');

        kanban.destroy();
        testUtils.mock.unpatch(FormRenderer);
    });

    QUnit.test('quickcreaterecord:cancelandvalidatewithoutusingthebuttons',asyncfunction(assert){
        assert.expect(9);

        varnbRecords=4;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        assert.strictEqual(kanban.exportState().resIds.length,nbRecords);

        //clicktoaddanelementandcancelthequickcreationbypressingESC
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());

        var$quickCreate=kanban.$('.o_kanban_quick_create');
        assert.strictEqual($quickCreate.length,1,"shouldhaveaquickcreateelement");

        $quickCreate.find('input').trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ESCAPE,
            which:$.ui.keyCode.ESCAPE,
        }));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "shouldhavedestroyedthequickcreateelement");

        //clicktoaddandelementandclickoutside,shouldcancelthequickcreation
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        awaittestUtils.dom.click(kanban.$('.o_kanban_group.o_kanban_record:first'));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldbedestroyedwhentheuserclicksoutside");

        //clicktoinputanddragthemouseoutside,shouldnotcancelthequickcreation
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        $quickCreate=kanban.$('.o_kanban_quick_create');
        awaittestUtils.dom.triggerMouseEvent($quickCreate.find('input'),'mousedown');
        awaittestUtils.dom.click(kanban.$('.o_kanban_group.o_kanban_record:first').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldnothavebeendestroyedafterclickingoutside");

        //clicktoreallyaddanelement
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        $quickCreate=kanban.$('.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'newpartner');

        //clickingoutsideshouldnolongerdestroythequickcreateasitisdirty
        awaittestUtils.dom.click(kanban.$('.o_kanban_group.o_kanban_record:first'));
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldnothavebeendestroyed");

        //confirmbypressingENTER
        nbRecords=5;
        $quickCreate.find('input').trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ENTER,
            which:$.ui.keyCode.ENTER,
        }));

        awaitnextTick();
        assert.strictEqual(this.data.partner.records.length,5,
            "shouldhavecreatedapartner");
        assert.strictEqual(_.last(this.data.partner.records).name,"newpartner",
            "shouldhavecorrectname");
        assert.strictEqual(kanban.exportState().resIds.length,nbRecords);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:validatewithENTER',asyncfunction(assert){
        //inthistest,weaccuratelymockthebehaviorofthewebclientbyspecifyinga
        //fieldDebounce>0,meaningthatthechangesinanInputFieldaren'tnotifiedtothemodel
        //on'input'events,buttheywaitforthe'change'event(oracallto'commitChanges',
        //e.g.triggeredbyanavigationevent)
        //inthisscenario,thecallto'commitChanges'actuallydoessomething(i.e.itnotifies
        //thenewvalueofthecharfield),whereasitdoesnothingifthechangesarenotified
        //directly
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
            fieldDebounce:5000,
        });

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldhave4recordsatthebeginning");

        //addanelementandconfirmbypressingENTER
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        awaittestUtils.kanban.quickCreate(kanban,'newpartner','foo');
        //triggersanavigationevent,leadingtothe'commitChanges'andrecordcreation

        assert.containsN(kanban,'.o_kanban_record',5,
            "shouldhavecreatedanewrecord");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'',
            "quickcreateshouldnowbeempty");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:preventmultipleaddswithENTER',asyncfunction(assert){
        assert.expect(9);

        varprom=makeTestPromise();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
            //addafieldDebouncetoaccuratelysimulatewhathappensinthewebclient:thefield
            //doesn'tnotifytheBasicModelthatithaschangeddirectly,asitwaitsfortheuser
            //tofocusoutornavigate(e.g.bypressingENTER)
            fieldDebounce:5000,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='create'){
                    assert.step('create');
                    returnprom.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldhave4recordsatthebeginning");

        //addanelementandpressENTERtwice
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        varenterEvent={
            keyCode:$.ui.keyCode.ENTER,
            which:$.ui.keyCode.ENTER,
        };
        awaittestUtils.fields.editAndTrigger(
            kanban.$('.o_kanban_quick_create').find('input[name=foo]'),
            'newpartner',
            ['input',$.Event('keydown',enterEvent),$.Event('keydown',enterEvent)]
        );

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldnothavecreatedtherecordyet");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'newpartner',
            "quickcreateshouldnotbeemptyyet");
        assert.hasClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbedisabled");

        prom.resolve();
        awaitnextTick();

        assert.containsN(kanban,'.o_kanban_record',5,
            "shouldhavecreatedanewrecord");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'',
            "quickcreateshouldnowbeempty");
        assert.doesNotHaveClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbeenabled");

        assert.verifySteps(['create']);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:preventmultipleaddswithAddclicked',asyncfunction(assert){
        assert.expect(9);

        varprom=makeTestPromise();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='create'){
                    assert.step('create');
                    returnprom.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldhave4recordsatthebeginning");

        //addanelementandclick'Add'twice
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_create').find('input[name=foo]'),'newpartner');
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_create').find('.o_kanban_add'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_create').find('.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldnothavecreatedtherecordyet");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'newpartner',
            "quickcreateshouldnotbeemptyyet");
        assert.hasClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbedisabled");

        prom.resolve();

        awaitnextTick();
        assert.containsN(kanban,'.o_kanban_record',5,
            "shouldhavecreatedanewrecord");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'',
            "quickcreateshouldnowbeempty");
        assert.doesNotHaveClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbeenabled");

        assert.verifySteps(['create']);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:preventmultipleaddswithENTER,withonchange',asyncfunction(assert){
        assert.expect(13);

        this.data.partner.onchanges={
            foo:function(obj){
                obj.int_field+=(obj.foo?3:0);
            },
        };
        varshouldDelayOnchange=false;
        varprom=makeTestPromise();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    assert.step('onchange');
                    if(shouldDelayOnchange){
                        returnPromise.resolve(prom).then(function(){
                            returnresult;
                        });
                    }
                }
                if(args.method==='create'){
                    assert.step('create');
                    assert.deepEqual(_.pick(args.args[0],'foo','int_field'),{
                        foo:'newpartner',
                        int_field:3,
                    });
                }
                returnresult;
            },
            //addafieldDebouncetoaccuratelysimulatewhathappensinthewebclient:thefield
            //doesn'tnotifytheBasicModelthatithaschangeddirectly,asitwaitsfortheuser
            //tofocusoutornavigate(e.g.bypressingENTER)
            fieldDebounce:5000,
        });

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldhave4recordsatthebeginning");

        //addanelementandpressENTERtwice
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        shouldDelayOnchange=true;
        varenterEvent={
            keyCode:$.ui.keyCode.ENTER,
            which:$.ui.keyCode.ENTER,
        };

        awaittestUtils.fields.editAndTrigger(
            kanban.$('.o_kanban_quick_create').find('input[name=foo]'),
            'newpartner',
            ['input',$.Event('keydown',enterEvent),$.Event('keydown',enterEvent)]
        );

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldnothavecreatedtherecordyet");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'newpartner',
            "quickcreateshouldnotbeemptyyet");
        assert.hasClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbedisabled");

        prom.resolve();

        awaitnextTick();
        assert.containsN(kanban,'.o_kanban_record',5,
            "shouldhavecreatedanewrecord");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'',
            "quickcreateshouldnowbeempty");
        assert.doesNotHaveClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbeenabled");

        assert.verifySteps([
            'onchange',//default_get
            'onchange',//newpartner
            'create',
            'onchange',//default_get
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:clickAddtocreate,withdelayedonchange',asyncfunction(assert){
        assert.expect(13);

        this.data.partner.onchanges={
            foo:function(obj){
                obj.int_field+=(obj.foo?3:0);
            },
        };
        varshouldDelayOnchange=false;
        varprom=makeTestPromise();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/><fieldname="int_field"/></div>'+
                    '</t></templates></kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    assert.step('onchange');
                    if(shouldDelayOnchange){
                        returnPromise.resolve(prom).then(function(){
                            returnresult;
                        });
                    }
                }
                if(args.method==='create'){
                    assert.step('create');
                    assert.deepEqual(_.pick(args.args[0],'foo','int_field'),{
                        foo:'newpartner',
                        int_field:3,
                    });
                }
                returnresult;
            },
        });

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldhave4recordsatthebeginning");

        //addanelementandclick'add'
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        shouldDelayOnchange=true;
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_create').find('input[name=foo]'),'newpartner');
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_create').find('.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_record',4,
            "shouldnothavecreatedtherecordyet");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'newpartner',
            "quickcreateshouldnotbeemptyyet");
        assert.hasClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbedisabled");

        prom.resolve();//theonchangereturns

        awaitnextTick();
        assert.containsN(kanban,'.o_kanban_record',5,
            "shouldhavecreatedanewrecord");
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput[name=foo]').val(),'',
            "quickcreateshouldnowbeempty");
        assert.doesNotHaveClass(kanban.$('.o_kanban_quick_create'),'o_disabled',
            "quickcreateshouldbeenabled");

        assert.verifySteps([
            'onchange',//default_get
            'onchange',//newpartner
            'create',
            'onchange',//default_get
        ]);

        kanban.destroy();
    });

    QUnit.test('quickcreatewhenfirstcolumnisfolded',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        assert.doesNotHaveClass(kanban.$('.o_kanban_group:first'),'o_column_folded',
            "firstcolumnshouldnotbefolded");

        //foldthefirstcolumn
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:first'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:first.o_kanban_toggle_fold'));

        assert.hasClass(kanban.$('.o_kanban_group:first'),'o_column_folded',
            "firstcolumnshouldbefolded");

        //clickon'Create'toopenthequickcreateinthefirstcolumn
        awaittestUtils.kanban.clickCreate(kanban);

        assert.doesNotHaveClass(kanban.$('.o_kanban_group:first'),'o_column_folded',
            "firstcolumnshouldnolongerbefolded");
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');
        assert.strictEqual($quickCreate.length,1,
            "shouldhaveaddedaquickcreateelementinfirstcolumn");

        //foldagainthefirstcolumn
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:first'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:first.o_kanban_toggle_fold'));

        assert.hasClass(kanban.$('.o_kanban_group:first'),'o_column_folded',
            "firstcolumnshouldbefolded");
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "thereshouldbenomorequickcreate");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:cancelwhennotdirty',asyncfunction(assert){
        assert.expect(11);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clicktoaddanelement
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        //clickagaintoaddanelement->shouldhavekeptthequickcreateopen
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhavekeptthequickcreateopen");

        //clickoutside:shouldremovethequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_group.o_kanban_record:first'));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldnothavebeendestroyed");

        //clicktoreopenthequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        //pressESC:shouldremovethequickcreate
        kanban.$('.o_kanban_quick_createinput').trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ESCAPE,
            which:$.ui.keyCode.ESCAPE,
        }));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "quickcreatewidgetshouldhavebeenremoved");

        //clicktoreopenthequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        //clickon'Discard':shouldremovethequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        awaittestUtils.dom.click(kanban.$('.o_kanban_group.o_kanban_record:first'));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldbedestroyedwhentheuserclicksoutside");

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldstillcontainonerecord");

        //clicktoreopenthequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        //clickingonthequickcreateitselfshouldkeepitopen
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_create'));
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldnothavebeendestroyedwhenclickedonitself");


        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:cancelwhenmodalisopened',asyncfunction(assert){
        assert.expect(3);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                    '<templates><tt-name="kanban-box">'+
                    '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                  '</kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="product_id"/>'+
                '</form>',
            },
            groupBy:['bar'],
        });

        //clicktoaddanelement
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        kanban.$('.o_kanban_quick_createinput')
            .val('test')
            .trigger('keyup')
            .trigger('focusout');
        awaitnextTick();

        //Whenfocusingoutofthemany2one,amodaltoadda'product'willappear.
        //Thefollowingassertionsensuresthataclickonthebodyelementthathas'modal-open'
        //willNOTclosethequickcreate.
        //Thiscanhappenwhentheuserclicksoutoftheinputbecauseofaraceconditionbetween
        //thefocusoutofthem2oandtheglobal'click'handlerofthequickcreate.
        //Checkflectra/flectra#61981formoredetails.
        const$body=kanban.$el.closest('body');
        assert.hasClass($body,'modal-open',
            "modalshouldbeopeningafterm2ofocusout");
        awaittestUtils.dom.click($body);
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "quickcreateshouldstayopenwhilemodalisopening");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:cancelwhendirty',asyncfunction(assert){
        assert.expect(7);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clicktoaddanelementandeditit
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        var$quickCreate=kanban.$('.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'somevalue');

        //clickoutside:shouldnotremovethequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_group.o_kanban_record:first'));
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldnothavebeendestroyed");

        //pressESC:shouldremovethequickcreate
        $quickCreate.find('input').trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ESCAPE,
            which:$.ui.keyCode.ESCAPE,
        }));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "quickcreatewidgetshouldhavebeenremoved");

        //clicktoreopenquickcreateandeditit
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveopenthequickcreatewidget");

        $quickCreate=kanban.$('.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'somevalue');

        //clickon'Discard':shouldremovethequickcreate
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_create.o_kanban_cancel'));
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldbedestroyedwhentheuserclicksoutside");

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldstillcontainonerecord");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordandeditingroupedmode',asyncfunction(assert){
        assert.expect(6);

        varnewRecordID;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            mockRPC:function(route,args){
                vardef=this._super.apply(this,arguments);
                if(args.method==='name_create'){
                    def.then(function(result){
                        newRecordID=result[0];
                    });
                }
                returndef;
            },
            groupBy:['bar'],
            intercepts:{
                switch_view:function(event){
                    assert.strictEqual(event.data.mode,"edit",
                        "shouldtrigger'open_record'eventineditmode");
                    assert.strictEqual(event.data.res_id,newRecordID,
                        "shouldopenthecorrectrecord");
                },
            },
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clicktoaddandeditanelement
        var$quickCreate=kanban.$('.o_kanban_quick_create');
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
        $quickCreate=kanban.$('.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'newpartner');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_edit'));

        assert.strictEqual(this.data.partner.records.length,5,
            "shouldhavecreatedapartner");
        assert.strictEqual(_.last(this.data.partner.records).name,"newpartner",
            "shouldhavecorrectname");
        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldnowcontaintworecords");

        kanban.destroy();
    });

    QUnit.test('quickcreateseveralrecordsinarow',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clicktoaddanelement,filltheinputandpressENTER
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());

        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldbeopen");

        awaittestUtils.kanban.quickCreate(kanban,'newpartner1');

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldnowcontaintworecords");
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldstillbeopen");

        //createasecondelementinarow
        awaittestUtils.kanban.quickCreate(kanban,'newpartner2');

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',3,
            "firstcolumnshouldnowcontainthreerecords");
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldstillbeopen");

        kanban.destroy();
    });

    QUnit.test('quickcreateisdisableduntilrecordiscreatedandread',asyncfunction(assert){
        assert.expect(6);

        varprom=makeTestPromise();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read'){
                    returnprom.then(_.constant(result));
                }
                returnresult;
            },
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontainonerecord");

        //clicktoaddarecord,andaddtwoinarow(firstonewillbedelayed)
        awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());

        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "thequickcreateshouldbeopen");

        awaittestUtils.kanban.quickCreate(kanban,'newpartner1');

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldstillcontainonerecord");
        assert.containsOnce(kanban,'.o_kanban_quick_create.o_disabled',
            "quickcreateshouldbedisabled");

        prom.resolve();

        awaitnextTick();
        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldnowcontaintworecords");
        assert.strictEqual(kanban.$('.o_kanban_quick_create:not(.o_disabled)').length,1,
            "quickcreateshouldbeenabled");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordfailingroupedbymany2one',asyncfunction(assert){
        assert.expect(8);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                    '<fieldname="product_id"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                '</kanban>',
            archs:{
                'partner,false,form':'<formstring="Partner">'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="foo"/>'+
                    '</form>',
            },
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    returnPromise.reject({
                        message:{
                            code:200,
                            data:{},
                            message:"Flectraservererror",
                        },
                        event:$.Event()
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "thereshouldbe2recordsinfirstcolumn");

        awaittestUtils.kanban.clickCreate(kanban);//Clickon'Create'
        assert.hasClass(kanban.$('.o_kanban_group:first()>div:nth(1)'),'o_kanban_quick_create',
            "clickingoncreateshouldopenthequick_createinthefirstcolumn");

        awaittestUtils.kanban.quickCreate(kanban,'test');

        assert.strictEqual($('.modal.o_form_view.o_form_editable').length,1,
            "aformviewdialogshouldhavebeenopened(inedit)");
        assert.strictEqual($('.modal.o_field_many2oneinput').val(),'hello',
            "thecorrectproduct_idshouldalreadybeset");

        //specifyanameandsave
        awaittestUtils.fields.editInput($('.modalinput[name=foo]'),'test');
        awaittestUtils.modal.clickButton('Save');

        assert.strictEqual($('.modal').length,0,"themodalshouldbeclosed");
        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',3,
            "thereshouldbe3recordsinfirstcolumn");
        var$firstRecord=kanban.$('.o_kanban_group:first.o_kanban_record:first');
        assert.strictEqual($firstRecord.text(),'test',
            "thefirstrecordofthefirstcolumnshouldbethenewone");
        assert.strictEqual(kanban.$('.o_kanban_quick_create:not(.o_disabled)').length,1,
            "quickcreateshouldbeenabled");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordisre-enabledafterdiscardonfailure',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                    '<fieldname="product_id"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                '</kanban>',
            archs:{
                'partner,false,form':'<formstring="Partner">'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="foo"/>'+
                    '</form>',
            },
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    returnPromise.reject({
                        message:{
                            code:200,
                            data:{},
                            message:"Flectraservererror",
                        },
                        event:$.Event()
                    });
                }
                returnthis._super.apply(this,arguments);
            }
        });

        awaittestUtils.kanban.clickCreate(kanban);
        assert.containsOnce(kanban,'.o_kanban_quick_create',
            "shouldhaveaquickcreatewidget");

        awaittestUtils.kanban.quickCreate(kanban,'test');

        assert.strictEqual($('.modal.o_form_view.o_form_editable').length,1,
            "aformviewdialogshouldhavebeenopened(inedit)");

        awaittestUtils.modal.clickButton('Discard');

        assert.strictEqual($('.modal').length,0,"themodalshouldbeclosed");
        assert.strictEqual(kanban.$('.o_kanban_quick_create:not(.o_disabled)').length,1,
            "quickcreatewidgetshouldhavebeenre-enabled");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordfailsingroupedbychar',asyncfunction(assert){
        assert.expect(7);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                '</kanban>',
            archs:{
                'partner,false,form':'<form>'+
                        '<fieldname="foo"/>'+
                    '</form>',
            },
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    returnPromise.reject({
                        message:{
                            code:200,
                            data:{},
                            message:"Flectraservererror",
                        },
                        event:$.Event()
                    });
                }
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{foo:'yop'},
                        "shouldwritethecorrectvalueforfoo");
                    assert.deepEqual(args.kwargs.context,{default_foo:'yop',default_name:'test'},
                        "shouldsendthecorrectdefaultvalueforfoo");
                }
                returnthis._super.apply(this,arguments);
            },
            groupBy:['foo'],
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "thereshouldbe1recordinfirstcolumn");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:first.o_kanban_quick_addi'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'test');
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.strictEqual($('.modal.o_form_view.o_form_editable').length,1,
            "aformviewdialogshouldhavebeenopened(inedit)");
        assert.strictEqual($('.modal.o_field_widget[name=foo]').val(),'yop',
            "thecorrectdefaultvalueforfooshouldalreadybeset");
        awaittestUtils.modal.clickButton('Save');

        assert.strictEqual($('.modal').length,0,"themodalshouldbeclosed");
        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "thereshouldbe2recordsinfirstcolumn");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordfailsingroupedbyselection',asyncfunction(assert){
        assert.expect(7);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="state"/></div>'+
                    '</t></templates>'+
                '</kanban>',
            archs:{
                'partner,false,form':'<form>'+
                        '<fieldname="state"/>'+
                    '</form>',
            },
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    returnPromise.reject({
                        message:{
                            code:200,
                            data:{},
                            message:"Flectraservererror",
                        },
                        event:$.Event()
                    });
                }
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{state:'abc'},
                        "shouldwritethecorrectvalueforstate");
                    assert.deepEqual(args.kwargs.context,{default_state:'abc',default_name:'test'},
                        "shouldsendthecorrectdefaultvalueforstate");
                }
                returnthis._super.apply(this,arguments);
            },
            groupBy:['state'],
        });

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "thereshouldbe1recordinfirstcolumn");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:first.o_kanban_quick_addi'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'test');
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.strictEqual($('.modal.o_form_view.o_form_editable').length,1,
            "aformviewdialogshouldhavebeenopened(inedit)");
        assert.strictEqual($('.modal.o_field_widget[name=state]').val(),'"abc"',
            "thecorrectdefaultvalueforstateshouldalreadybeset");

        awaittestUtils.modal.clickButton('Save');

        assert.strictEqual($('.modal').length,0,"themodalshouldbeclosed");
        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "thereshouldbe2recordsinfirstcolumn");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordinemptygroupedkanban',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                    '<fieldname="product_id"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    varresult={
                        groups:[
                            {__domain:[['product_id','=',3]],product_id_count:0},
                            {__domain:[['product_id','=',5]],product_id_count:0},
                        ],
                        length:2,
                    };
                    returnPromise.resolve(result);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2,
            "thereshouldbe2columns");
        assert.containsNone(kanban,'.o_kanban_record',
            "bothcolumnsshouldbeempty");

        awaittestUtils.kanban.clickCreate(kanban);

        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_quick_create',
            "shouldhaveopenedthequickcreateinthefirstcolumn");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedondate(time)field',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="display_name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['date'],
            intercepts:{
                switch_view:function(ev){
                    assert.deepEqual(_.pick(ev.data,'res_id','view_type'),{
                        res_id:undefined,
                        view_type:'form',
                    },"shouldtriggeraneventtoopentheformview(twice)");
                },
            },
        });

        assert.containsNone(kanban,'.o_kanban_header.o_kanban_quick_addi',
            "quickcreateshouldbedisabledwhengroupedonadatefield");

        //clickingonCREATEincontrolpanelshouldnotopenaquickcreate
        awaittestUtils.kanban.clickCreate(kanban);
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "shouldnothaveopenedthequickcreatewidget");

        awaitkanban.reload({groupBy:['datetime']});

        assert.containsNone(kanban,'.o_kanban_header.o_kanban_quick_addi',
            "quickcreateshouldbedisabledwhengroupedonadatetimefield");

        //clickingonCREATEincontrolpanelshouldnotopenaquickcreate
        awaittestUtils.kanban.clickCreate(kanban);
        assert.containsNone(kanban,'.o_kanban_quick_create',
            "shouldnothaveopenedthequickcreatewidget");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordfeatureisproperlyenabled/disabledatreload',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="display_name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['foo'],
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',3,
            "quickcreateshouldbeenabledwhengroupedonacharfield");

        awaitkanban.reload({groupBy:['date']});

        assert.containsNone(kanban,'.o_kanban_header.o_kanban_quick_addi',
            "quickcreateshouldnowbedisabled(groupedondatefield)");

        awaitkanban.reload({groupBy:['bar']});

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',2,
            "quickcreateshouldbeenabledagain(groupedonbooleanfield)");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedbycharfield',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="display_name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['foo'],
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    assert.deepEqual(args.kwargs.context,{default_foo:'yop'},
                        "shouldsendthecorrectdefaultvalueforfoo");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',3,
            "quickcreateshouldbeenabledwhengroupedonacharfield");
        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontain1record");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:first.o_kanban_quick_addi'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'newrecord');
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldnowcontain2records");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedbybooleanfield',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="display_name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    assert.deepEqual(args.kwargs.context,{default_bar:true},
                        "shouldsendthecorrectdefaultvalueforbar");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',2,
            "quickcreateshouldbeenabledwhengroupedonabooleanfield");
        assert.strictEqual(kanban.$('.o_kanban_group:nth(1).o_kanban_record').length,3,
            "secondcolumn(true)shouldcontain3records");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:nth(1).o_kanban_quick_addi'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'newrecord');
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.strictEqual(kanban.$('.o_kanban_group:nth(1).o_kanban_record').length,4,
            "secondcolumn(true)shouldnowcontain4records");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedonselectionfield',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="display_name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    assert.deepEqual(args.kwargs.context,{default_state:'abc'},
                        "shouldsendthecorrectdefaultvalueforbar");
                }
                returnthis._super.apply(this,arguments);
            },
            groupBy:['state'],
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',3,
            "quickcreateshouldbeenabledwhengroupedonaselectionfield");
        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumn(abc)shouldcontain1record");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:first.o_kanban_quick_addi'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'newrecord');
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumn(abc)shouldcontain2records");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedbycharfield(withinquick_create_view)',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="foo"/>'+
                '</form>',
            },
            groupBy:['foo'],
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{foo:'yop'},
                        "shouldwritethecorrectvalueforfoo");
                    assert.deepEqual(args.kwargs.context,{default_foo:'yop'},
                        "shouldsendthecorrectdefaultvalueforfoo");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',3,
            "quickcreateshouldbeenabledwhengroupedonacharfield");
        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumnshouldcontain1record");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:first.o_kanban_quick_addi'));
        assert.strictEqual(kanban.$('.o_kanban_quick_createinput').val(),'yop',
            "shouldhavesetthecorrectfoovaluebydefault");
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumnshouldnowcontain2records");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedbybooleanfield(withinquick_create_view)',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="bar"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="bar"/>'+
                '</form>',
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{bar:true},
                        "shouldwritethecorrectvalueforbar");
                    assert.deepEqual(args.kwargs.context,{default_bar:true},
                        "shouldsendthecorrectdefaultvalueforbar");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',2,
            "quickcreateshouldbeenabledwhengroupedonabooleanfield");
        assert.strictEqual(kanban.$('.o_kanban_group:nth(1).o_kanban_record').length,3,
            "secondcolumn(true)shouldcontain3records");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:nth(1).o_kanban_quick_addi'));
        assert.ok(kanban.$('.o_kanban_quick_create.o_field_booleaninput').is(':checked'),
            "shouldhavesetthecorrectbarvaluebydefault");
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.strictEqual(kanban.$('.o_kanban_group:nth(1).o_kanban_record').length,4,
            "secondcolumn(true)shouldnowcontain4records");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordingroupedbyselectionfield(withinquick_create_view)',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="state"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="state"/>'+
                '</form>',
            },
            groupBy:['state'],
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{state:'abc'},
                        "shouldwritethecorrectvalueforstate");
                    assert.deepEqual(args.kwargs.context,{default_state:'abc'},
                        "shouldsendthecorrectdefaultvalueforstate");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_kanban_header.o_kanban_quick_addi',3,
            "quickcreateshouldbeenabledwhengroupedonaselectionfield");
        assert.containsOnce(kanban,'.o_kanban_group:first.o_kanban_record',
            "firstcolumn(abc)shouldcontain1record");

        awaittestUtils.dom.click(kanban.$('.o_kanban_header:first.o_kanban_quick_addi'));
        assert.strictEqual(kanban.$('.o_kanban_quick_createselect').val(),'"abc"',
            "shouldhavesetthecorrectstatevaluebydefault");
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2,
            "firstcolumn(abc)shouldnowcontain2records");

        kanban.destroy();
    });

    QUnit.test('quickcreaterecordwhileaddinganewcolumn',asyncfunction(assert){
        assert.expect(10);

        vardef=testUtils.makeTestPromise();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='name_create'&&args.model==='product'){
                    returndef.then(_.constant(result));
                }
                returnresult;
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2);
        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',2);

        //addanewcolumn
        assert.containsOnce(kanban,'.o_column_quick_create');
        assert.isNotVisible(kanban.$('.o_column_quick_createinput'));

        awaittestUtils.dom.click(kanban.$('.o_quick_create_folded'));

        assert.isVisible(kanban.$('.o_column_quick_createinput'));

        awaittestUtils.fields.editInput(kanban.$('.o_column_quick_createinput'),'newcolumn');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group',2);

        //clicktoaddanewrecord
        awaittestUtils.dom.click(kanban.$buttons.find('.o-kanban-button-new'));

        //shouldwaitforthecolumntobecreated(andviewtobere-rendered
        //beforeopeningthequickcreate
        assert.containsNone(kanban,'.o_kanban_quick_create');

        //unlockcolumncreation
        def.resolve();
        awaittestUtils.nextTick();
        assert.containsN(kanban,'.o_kanban_group',3);
        assert.containsOnce(kanban,'.o_kanban_quick_create');

        //quickcreaterecordinfirstcolumn
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'newrecord');
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_create.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group:first.o_kanban_record',3);

        kanban.destroy();
    });

    QUnit.test('closeacolumnwhilequickcreatingarecord',asyncfunction(assert){
        assert.expect(6);

        constdef=testUtils.makeTestPromise();
        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbanon_create="quick_create"quick_create_view="some_view_ref">
                    <templates><tt-name="kanban-box">
                        <div><fieldname="foo"/></div>
                    </t></templates>
                </kanban>`,
            archs:{
                'partner,some_view_ref,form':'<form><fieldname="int_field"/></form>',
            },
            groupBy:['product_id'],
            asyncmockRPC(route,args){
                constresult=this._super(...arguments);
                if(args.method==='load_views'){
                    awaitdef;
                }
                returnresult;
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2);
        assert.containsNone(kanban,'.o_column_folded');

        //clicktoquickcreateanewrecordinthefirstcolumn(thisoperationisdelayed)
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:first.o_kanban_quick_add'));

        assert.containsNone(kanban,'.o_form_view');

        //clicktofoldthefirstcolumn
        awaittestUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:first'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:first.o_kanban_toggle_fold'));

        assert.containsOnce(kanban,'.o_column_folded');

        def.resolve();
        awaittestUtils.nextTick();

        assert.containsNone(kanban,'.o_form_view');
        assert.containsOnce(kanban,'.o_column_folded');

        kanban.destroy();
    });

    QUnit.test('quickcreaterecord:openonacolumnwhileanothercolumnhasalreadyone',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        //Clickonquickcreateinfirstcolumn
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:nth-child(1).o_kanban_quick_add'));
        assert.containsOnce(kanban,'.o_kanban_quick_create');
        assert.containsOnce(kanban.$('.o_kanban_group:nth-child(1)'),'.o_kanban_quick_create');

        //Clickonquickcreateinsecondcolumn
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:nth-child(2).o_kanban_quick_add'));
        assert.containsOnce(kanban,'.o_kanban_quick_create');
        assert.containsOnce(kanban.$('.o_kanban_group:nth-child(2)'),'.o_kanban_quick_create');

        //Clickonquickcreateinfirstcolumnonceagain
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:nth-child(1).o_kanban_quick_add'));
        assert.containsOnce(kanban,'.o_kanban_quick_create');
        assert.containsOnce(kanban.$('.o_kanban_group:nth-child(1)'),'.o_kanban_quick_create');

        kanban.destroy();
    });

    QUnit.test('many2many_tagsinkanbanviews',asyncfunction(assert){
        assert.expect(12);

        this.data.partner.records[0].category_ids=[6,7];
        this.data.partner.records[1].category_ids=[7,8];
        this.data.category.records.push({
            id:8,
            name:"hello",
            color:0,
        });

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<templates><tt-name="kanban-box">'+
                            '<divclass="oe_kanban_global_click">'+
                                '<fieldname="category_ids"widget="many2many_tags"options="{\'color_field\':\'color\'}"/>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="state"widget="priority"/>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            mockRPC:function(route){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                switch_view:function(event){
                    assert.deepEqual(_.pick(event.data,'mode','model','res_id','view_type'),{
                        mode:'readonly',
                        model:'partner',
                        res_id:1,
                        view_type:'form',
                    },"shouldtriggeraneventtoopentheclickedrecordinaformview");
                },
            },
        });

        var$first_record=kanban.$('.o_kanban_record:first()');
        assert.strictEqual($first_record.find('.o_field_many2manytags.o_tag').length,2,
            'firstrecordshouldcontain2tags');
        assert.hasClass($first_record.find('.o_tag:first()'),'o_tag_color_2',
            'firsttagshouldhavecolor2');
        assert.verifySteps(['/web/dataset/search_read','/web/dataset/call_kw/category/read'],
            'twoRPCshouldhavebeendone(onesearchreadandonereadforthem2m)');

        //Checksthatsecondrecordshasonlyonetagasoneshouldbehidden(color0)
        assert.strictEqual(kanban.$('.o_kanban_record').eq(1).find('.o_tag').length,1,
            'thereshouldbeonlyonetaginsecondrecord');

        //Writeontherecordusingtheprioritywidgettotriggerare-renderinreadonly
        awaittestUtils.dom.click(kanban.$('.o_field_widget.o_prioritya.o_priority_star.fa-star-o').first());
        assert.verifySteps([
            '/web/dataset/call_kw/partner/write',
            '/web/dataset/call_kw/partner/read',
            '/web/dataset/call_kw/category/read'
        ],'fiveRPCsshouldhavebeendone(previous2,1write(triggersare-render),same2atre-render');
        assert.strictEqual(kanban.$('.o_kanban_record:first()').find('.o_field_many2manytags.o_tag').length,2,
            'firstrecordshouldstillcontainonly2tags');

        //clickonatag(shouldtriggerswitch_view)
        awaittestUtils.dom.click(kanban.$('.o_tag:contains(gold):first'));

        kanban.destroy();
    });

    QUnit.test('Donotopenrecordwhenclickingon`a`with`href`',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records=[
            {id:1,foo:'yop'},
        ];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<templates>'+
                            '<tt-name="kanban-box">'+
                                '<divclass="oe_kanban_global_click">'+
                                    '<fieldname="foo"/>'+
                                    '<div>'+
                                        '<aclass="o_test_link"href="#">testlink</a>'+
                                    '</div>'+
                                '</div>'+
                            '</t>'+
                        '</templates>'+
                    '</kanban>',
            intercepts:{
                //whenclickingonarecordinkanbanview,
                //itswitchestoformview.
                switch_view:function(){
                    thrownewError("shouldnotswitchview");
                },
            },
            doNotDisableAHref:true,
        });

        var$record=kanban.$('.o_kanban_record:not(.o_kanban_ghost)');
        assert.strictEqual($record.length,1,
            "shoulddisplayakanbanrecord");

        var$testLink=$record.find('a');
        assert.strictEqual($testLink.length,1,
            "shouldcontainalinkinthekanbanrecord");
        assert.ok(!!$testLink[0].href,
            "linkinsidekanbanrecordshouldhavenon-emptyhref");

        //Preventthebrowserdefaultbehaviourwhenclickingonanything.
        //Thisincludesclickingona`<a>`with`href`,sothatitdoesnot
        //changetheURLintheaddressbar.
        //Notethatweshouldnotspecifyaclicklisteneron'a',otherwise
        //itmayinfluencethekanbanrecordglobalclickhandlertonotopen
        //therecord.
        $(document.body).on('click.o_test',function(ev){
            assert.notOk(ev.isDefaultPrevented(),
                "shouldnotpreventedbrowserdefaultbehaviourbeforehand");
            assert.strictEqual(ev.target,$testLink[0],
                "shouldhaveclickedonthetestlinkinthekanbanrecord");
            ev.preventDefault();
        });

        awaittestUtils.dom.click($testLink);

        $(document.body).off('click.o_test');
        kanban.destroy();
    });

    QUnit.test('o2mloadedinonlyonebatch',asyncfunction(assert){
        assert.expect(9);

        this.data.subtask={
            fields:{
                name:{string:'Name',type:'char'}
            },
            records:[
                {id:1,name:"subtask#1"},
                {id:2,name:"subtask#2"},
            ]
        };
        this.data.partner.fields.subtask_ids={
            string:'Subtasks',
            type:'one2many',
            relation:'subtask'
        };
        this.data.partner.records[0].subtask_ids=[1];
        this.data.partner.records[1].subtask_ids=[2];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div>'+
                                '<fieldname="subtask_ids"widget="many2many_tags"/>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        awaitkanban.reload();
        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'read',
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'read',
        ]);
        kanban.destroy();
    });

    QUnit.test('m2mloadedinonlyonebatch',asyncfunction(assert){
        assert.expect(9);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div>'+
                                '<fieldname="category_ids"widget="many2many_tags"/>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        awaitkanban.reload(kanban);
        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'read',
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'read',
        ]);
        kanban.destroy();
    });

    QUnit.test('fetchreferenceinonlyonebatch',asyncfunction(assert){
        assert.expect(9);

        this.data.partner.records[0].ref_product='product,3';
        this.data.partner.records[1].ref_product='product,5';
        this.data.partner.fields.ref_product={
            string:"ReferenceField",
            type:'reference',
        };

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<divclass="oe_kanban_global_click">'+
                                '<fieldname="ref_product"/>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        awaitkanban.reload();
        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'name_get',
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'name_get',
        ]);
        kanban.destroy();
    });

    QUnit.test('waitx2manysbatchfetchestore-render',asyncfunction(assert){
        assert.expect(7);
        vardone=assert.async();

        vardef=Promise.resolve();
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div>'+
                                '<fieldname="category_ids"widget="many2many_tags"/>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                varresult=this._super(route,args);
                if(args.method==='read'){
                    returndef.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        def=testUtils.makeTestPromise();
        assert.containsN(kanban,'.o_tag',2);
        assert.containsN(kanban,'.o_kanban_group',2);
        kanban.update({groupBy:['state']});
        def.then(asyncfunction(){
            assert.containsN(kanban,'.o_kanban_group',2);
            awaittestUtils.nextTick();
            assert.containsN(kanban,'.o_kanban_group',3);

            assert.containsN(kanban,'.o_tag',2,
            'Shoulddisplay2tagsafterupdate');
            assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_tag').text(),
                'gold','Firstcategoryshouldbe\'gold\'');
            assert.strictEqual(kanban.$('.o_kanban_group:eq(2).o_tag').text(),
                'silver','Secondcategoryshouldbe\'silver\'');
            kanban.destroy();
            done();
        });
        awaittestUtils.nextTick();
        def.resolve();
    });

    QUnit.test('candraganddroparecordfromonecolumntothenext',asyncfunction(assert){
        assert.expect(9);

        //@todo:removethisresequenceDefwheneverthejqueryupgradebranch
        //ismerged. Thisiscurrentlynecessarytosimulatethereality:we
        //needtheclickhandlerstobeexecutedaftertheendofthedragand
        //dropoperation,notbefore.
        varresequenceDef=testUtils.makeTestPromise();

        varenvIDs=[1,3,2,4];//theidsthatshouldbeintheenvironmentduringthistest
        this.data.partner.fields.sequence={type:'number',string:"Sequence"};
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<divclass="oe_kanban_global_click"><fieldname="foo"/>'+
                                '<tt-if="widget.editable"><spanclass="thisiseditable">edit</span></t>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    assert.ok(true,"shouldcallresequence");
                    returnresequenceDef.then(_.constant(true));
                }
                returnthis._super(route,args);
            },
        });
        assert.containsN(kanban,'.o_kanban_group:nth-child(1).o_kanban_record',2);
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',2);
        assert.containsN(kanban,'.thisiseditable',4);
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        var$record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        var$group=kanban.$('.o_kanban_group:nth-child(2)');
        envIDs=[3,2,4,1];//firstrecordoffirstcolumnmovedtothebottomofsecondcolumn
        awaittestUtils.dom.dragAndDrop($record,$group,{withTrailingClick:true});

        resequenceDef.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',3);
        assert.containsN(kanban,'.thisiseditable',4);
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        resequenceDef.resolve();
        kanban.destroy();
    });

    QUnit.test('draganddroparecord,groupedbyselection',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<templates>'+
                            '<tt-name="kanban-box">'+
                                '<div><fieldname="state"/></div>'+
                            '</t>'+
                        '</templates>'+
                    '</kanban>',
            groupBy:['state'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    assert.ok(true,"shouldcallresequence");
                    returnPromise.resolve(true);
                }
                if(args.model==='partner'&&args.method==='write'){
                    assert.deepEqual(args.args[1],{state:'def'});
                }
                returnthis._super(route,args);
            },
        });
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(2).o_kanban_record');

        var$record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        var$group=kanban.$('.o_kanban_group:nth-child(2)');
        awaittestUtils.dom.dragAndDrop($record,$group);
        awaitnextTick(); //waitforresequenceafterdraganddrop

        assert.containsNone(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',2);
        kanban.destroy();
    });

    QUnit.test('preventdraganddropofrecordifgroupedbyreadonly',asyncfunction(assert){
        assert.expect(12);

        this.data.partner.fields.foo.readonly=true;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates>'+
                            '<tt-name="kanban-box"><div>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="state"readonly="1"/>'+
                            '</div></t>'+
                        '</templates>'+
                    '</kanban>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    returnPromise.resolve();
                }
                if(args.model==='partner'&&args.method==='write'){
                    thrownewError('shouldnotbedraggable');
                }
                returnthis._super(route,args);
            },
        });
        //simulateanupdatecomingfromthesearchview,withanothergroupbygiven
        awaitkanban.update({groupBy:['state']});
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(2).o_kanban_record');

        //drag&droparecordinanothercolumn
        var$record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        var$group=kanban.$('.o_kanban_group:nth-child(2)');
        awaittestUtils.dom.dragAndDrop($record,$group);
        awaitnextTick(); //waitforresequenceafterdraganddrop
        //shouldnotbedraggable
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(2).o_kanban_record');

        //simulateanupdatecomingfromthesearchview,withanothergroupbygiven
        awaitkanban.update({groupBy:['foo']});
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',2);

        //drag&droparecordinanothercolumn
        $record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        $group=kanban.$('.o_kanban_group:nth-child(2)');
        awaittestUtils.dom.dragAndDrop($record,$group);
        awaitnextTick(); //waitforresequenceafterdraganddrop
        //shouldnotbedraggable
        assert.containsOnce(kanban,'.o_kanban_group:nth-child(1).o_kanban_record');
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',2);

        //drag&droparecordinthesamecolumn
        var$record1=kanban.$('.o_kanban_group:nth-child(2).o_kanban_record:eq(0)');
        var$record2=kanban.$('.o_kanban_group:nth-child(2).o_kanban_record:eq(1)');
        assert.strictEqual($record1.text(),"blipDEF","firstrecordshouldbeDEF");
        assert.strictEqual($record2.text(),"blipGHI","secondrecordshouldbeGHI");
        awaittestUtils.dom.dragAndDrop($record2,$record1,{position:'top'});
        //shouldstillbeabletoresequence
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record:eq(0)').text(),"blipGHI",
            "recordsshouldhavebeenresequenced");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record:eq(1)').text(),"blipDEF",
            "recordsshouldhavebeenresequenced");

        kanban.destroy();
    });

    QUnit.test('preventdraganddropifgroupedbydate/datetimefield',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records[0].date='2017-01-08';
        this.data.partner.records[1].date='2017-01-09';
        this.data.partner.records[2].date='2017-02-08';
        this.data.partner.records[3].date='2017-02-10';

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['date:month'],
        });

        assert.strictEqual(kanban.$('.o_kanban_group').length,2,"shouldhave2columns");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(1).o_kanban_record').length,2,
                        "1stcolumnshouldcontain2recordsofJanuarymonth");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record').length,2,
                        "2ndcolumnshouldcontain2recordsofFebruarymonth");

        //drag&droparecordinanothercolumn
        var$record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        var$group=kanban.$('.o_kanban_group:nth-child(2)');
        awaittestUtils.dragAndDrop($record,$group);

        //shouldnotdrag&droprecord
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(1).o_kanban_record').length,2,
                        "Shouldremainsamerecordsinfirstcolumn(2records)");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record').length,2,
                        "Shouldremainsamerecordsin2ndcolumn(2record)");
        kanban.destroy();
    });

    QUnit.test('completelypreventdraganddropifrecords_draggablesettofalse',asyncfunction(assert){
        assert.expect(6);

        varenvIDs=[1,3,2,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"records_draggable="false">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['product_id'],
        });

        //testinginitialstate
        assert.containsN(kanban,'.o_kanban_group:nth-child(1).o_kanban_record',2);
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',2);
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //attempttodrag&droparecordinanothercolumn
        var$record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        var$group=kanban.$('.o_kanban_group:nth-child(2)');
        awaittestUtils.dom.dragAndDrop($record,$group,{withTrailingClick:true});

        //shouldnotdrag&droprecord
        assert.containsN(kanban,'.o_kanban_group:nth-child(1).o_kanban_record',2,
            "Firstcolumnshouldstillcontain2records");
        assert.containsN(kanban,'.o_kanban_group:nth-child(2).o_kanban_record',2,
            "Secondcolumnshouldstillcontain2records");
        assert.deepEqual(kanban.exportState().resIds,envIDs,"Recordsshouldnothavemoved");

        kanban.destroy();
    });

    QUnit.test('preventdraganddropofrecordifonchangefails',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.onchanges={
            product_id:function(obj){}
        };

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates>'+
                            '<tt-name="kanban-box"><div>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="product_id"/>'+
                            '</div></t>'+
                        '</templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/onchange'){
                    returnPromise.reject({});
                }
                returnthis._super(route,args);
            },
        });

        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(1).o_kanban_record').length,2,
                        "columnshouldcontain2records");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record').length,2,
                        "columnshouldcontain2records");
        //drag&droparecordinanothercolumn
        var$record=kanban.$('.o_kanban_group:nth-child(1).o_kanban_record:first');
        var$group=kanban.$('.o_kanban_group:nth-child(2)');
        awaittestUtils.dom.dragAndDrop($record,$group);
        //shouldnotbedropped,cardshouldresetbacktofirstcolumn
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(1).o_kanban_record').length,2,
                        "columnshouldnowcontain2records");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record').length,2,
                        "columnshouldcontain2records");

        kanban.destroy();
    });

    QUnit.test('kanbanviewwithdefault_group_by',asyncfunction(assert){
        assert.expect(7);
        this.data.partner.records.product_id=1;
        this.data.product.records.push({id:1,display_name:"thirdproduct"});

        varreadGroupCount=0;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"default_group_by="bar">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/web_read_group'){
                    readGroupCount++;
                    varcorrectGroupBy;
                    if(readGroupCount===2){
                        correctGroupBy=['product_id'];
                    }else{
                        correctGroupBy=['bar'];
                    }
                    //thisisdonethreetimes
                    assert.ok(_.isEqual(args.kwargs.groupby,correctGroupBy),
                        "groupbyargsshouldbecorrect");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_grouped');
        assert.containsN(kanban,'.o_kanban_group',2,"shouldhave"+2+"columns");

        //simulateanupdatecomingfromthesearchview,withanothergroupbygiven
        awaitkanban.update({groupBy:['product_id']});
        assert.containsN(kanban,'.o_kanban_group',2,"shouldnowhave"+3+"columns");

        //simulateanupdatecomingfromthesearchview,removingthepreviouslysetgroupby
        awaitkanban.update({groupBy:[]});
        assert.containsN(kanban,'.o_kanban_group',2,"shouldhave"+2+"columnsagain");
        kanban.destroy();
    });

    QUnit.test('kanbanviewnotgroupable',asyncfunction(assert){
        assert.expect(3);

        constsearchMenuTypesOriginal=KanbanView.prototype.searchMenuTypes;
        KanbanView.prototype.searchMenuTypes=['filter','favorite'];

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbanclass="o_kanban_test"default_group_by="bar">
                    <fieldname="bar"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="foo"/></div>
                        </t>
                    </templates>
                </kanban>
            `,
            archs:{
                'partner,false,search':`
                    <search>
                        <filterstring="candle"name="itsName"context="{'group_by':'foo'}"/>
                    </search>
                `,
            },
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    thrownewError("Shouldnotdoaread_groupRPC");
                }
                returnthis._super.apply(this,arguments);
            },
            context:{search_default_itsName:1,},
        });

        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'o_kanban_grouped');
        assert.containsNone(kanban,'.o_control_paneldiv.o_search_optionsdiv.o_group_by_menu');
        assert.deepEqual(cpHelpers.getFacetTexts(kanban),[]);

        kanban.destroy();
        KanbanView.prototype.searchMenuTypes=searchMenuTypesOriginal;
    });

    QUnit.test('kanbanviewwithcreate=False',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"create="0">'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
        });

        assert.ok(!kanban.$buttons||!kanban.$buttons.find('.o-kanban-button-new').length,
            "Createbuttonshouldn'tbethere");
        kanban.destroy();
    });

    QUnit.test('clickingonalinktriggerscorrectevent',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                    '<div><atype="edit">Edit</a></div>'+
                '</t></templates></kanban>',
        });

        testUtils.mock.intercept(kanban,'switch_view',function(event){
            assert.deepEqual(event.data,{
                view_type:'form',
                res_id:1,
                mode:'edit',
                model:'partner',
            });
        });
        awaittestUtils.dom.click(kanban.$('a').first());
        kanban.destroy();
    });

    QUnit.test('environmentisupdatedwhen(un)foldinggroups',asyncfunction(assert){
        assert.expect(3);

        varenvIDs=[1,3,2,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //foldthesecondgroupandcheckthattheres_idsitcontainsareno
        //longerintheenvironment
        envIDs=[1,3];
        awaittestUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_kanban_toggle_fold'));
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //re-openthesecondgroupandcheckthattheres_idsitcontainsare
        //backintheenvironment
        envIDs=[1,3,2,4];
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last'));
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        kanban.destroy();
    });

    QUnit.test('createacolumningroupedonm2o',asyncfunction(assert){
        assert.expect(14);

        varnbRPCs=0;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                nbRPCs++;
                if(args.method==='name_create'){
                    assert.ok(true,"shouldcallname_create");
                }
                //Createcolumnwillcallresequencetosetcolumnorder
                if(route==='/web/dataset/resequence'){
                    assert.ok(true,"shouldcallresequence");
                    returnPromise.resolve(true);
                }
                returnthis._super(route,args);
            },
        });
        assert.containsOnce(kanban,'.o_column_quick_create',"shouldhaveaquickcreatecolumn");
        assert.notOk(kanban.$('.o_column_quick_createinput').is(':visible'),
            "theinputshouldnotbevisible");

        awaittestUtils.dom.click(kanban.$('.o_quick_create_folded'));

        assert.ok(kanban.$('.o_column_quick_createinput').is(':visible'),
            "theinputshouldbevisible");

        //discardthecolumncreationandclickitagain
        awaitkanban.$('.o_column_quick_createinput').trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ESCAPE,
            which:$.ui.keyCode.ESCAPE,
        }));
        assert.notOk(kanban.$('.o_column_quick_createinput').is(':visible'),
            "theinputshouldnotbevisibleafterdiscard");

        awaittestUtils.dom.click(kanban.$('.o_quick_create_folded'));
        assert.ok(kanban.$('.o_column_quick_createinput').is(':visible'),
            "theinputshouldbevisible");

        awaitkanban.$('.o_column_quick_createinput').val('newvalue').trigger('input');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        assert.strictEqual(kanban.$('.o_kanban_group:lastspan:contains(newvalue)').length,1,
            "thelastcolumnshouldbethenewlycreatedone");
        assert.ok(_.isNumber(kanban.$('.o_kanban_group:last').data('id')),
            'thecreatedcolumnshouldhavethecorrectid');
        assert.doesNotHaveClass(kanban.$('.o_kanban_group:last'),'o_column_folded',
            'thecreatedcolumnshouldnotbefolded');

        //foldandunfoldthecreatedcolumn,andcheckthatnoRPCisdone(asthereisnorecord)
        nbRPCs=0;
        awaittestUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_kanban_toggle_fold'));
        assert.hasClass(kanban.$('.o_kanban_group:last'),'o_column_folded',
            'thecreatedcolumnshouldnowbefolded');
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last'));
        assert.doesNotHaveClass(kanban.$('.o_kanban_group:last'),'o_column_folded');
        assert.strictEqual(nbRPCs,0,'norpcshouldhavebeendonewhenfolding/unfolding');

        //quickcreatearecord
        awaittestUtils.kanban.clickCreate(kanban);
        assert.hasClass(kanban.$('.o_kanban_group:first()>div:nth(1)'),'o_kanban_quick_create',
            "clickingoncreateshouldopenthequick_createinthefirstcolumn");
        kanban.destroy();
    });

    QUnit.test('autofoldgroupwhenreachthelimit',asyncfunction(assert){
        assert.expect(9);

        vardata=this.data;
        for(vari=0;i<12;i++){
            data.product.records.push({
                id:(8+i),
                name:("column"),
            });
            data.partner.records.push({
                id:(20+i),
                foo:("dumbentry"),
                product_id:(8+i),
            });
        }

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    returnthis._super.apply(this,arguments).then(function(result){
                        result.groups[2].__fold=true;
                        result.groups[8].__fold=true;
                        returnresult;
                    });
                }
                returnthis._super(route,args);
            },
        });

        //welookifcolumnarefold/unfoldaccordingwhatisexpected
        assert.doesNotHaveClass(kanban.$('.o_kanban_group:nth-child(2)'),'o_column_folded');
        assert.doesNotHaveClass(kanban.$('.o_kanban_group:nth-child(4)'),'o_column_folded');
        assert.doesNotHaveClass(kanban.$('.o_kanban_group:nth-child(10)'),'o_column_folded');
        assert.hasClass(kanban.$('.o_kanban_group:nth-child(3)'),'o_column_folded');
        assert.hasClass(kanban.$('.o_kanban_group:nth-child(9)'),'o_column_folded');

        //welookifcolumnsareactuallyfoldafterwereachedthelimit
        assert.hasClass(kanban.$('.o_kanban_group:nth-child(13)'),'o_column_folded');
        assert.hasClass(kanban.$('.o_kanban_group:nth-child(14)'),'o_column_folded');

        //welookifwehavetherightcountoffolded/unfoldedcolumn
        assert.containsN(kanban,'.o_kanban_group:not(.o_column_folded)',10);
        assert.containsN(kanban,'.o_kanban_group.o_column_folded',4);

        kanban.destroy();
    });

    QUnit.test('hideanddisplayhelpmessage(ESC)inkanbanquickcreate',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        awaittestUtils.dom.click(kanban.$('.o_quick_create_folded'));
        assert.ok(kanban.$('.o_discard_msg').is(':visible'),
            'theESCtodiscardmessageisvisible');

        //clickoutsidethecolumn(tolosefocus)
        awaittestUtils.dom.clickFirst(kanban.$('.o_kanban_header'));
        assert.notOk(kanban.$('.o_discard_msg').is(':visible'),
            'theESCtodiscardmessageisnolongervisible');

        kanban.destroy();
    });

    QUnit.test('deleteacolumningroupedonm2o',asyncfunction(assert){
        assert.expect(37);

        testUtils.mock.patch(KanbanRenderer,{
            _renderGrouped:function(){
                this._super.apply(this,arguments);
                //setdelayandrevertanimationtimeto0sodummydraganddropworks
                if(this.$el.sortable('instance')){
                    this.$el.sortable('option',{delay:0,revert:0});
                }
            },
        });

        varresequencedIDs;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    resequencedIDs=args.ids;
                    assert.strictEqual(_.reject(args.ids,_.isNumber).length,0,
                        "columnresequencedshouldbeexistingrecordswithIDs");
                    returnPromise.resolve(true);
                }
                if(args.method){
                    assert.step(args.method);
                }
                returnthis._super(route,args);
            },
        });

        //checktheinitialrendering
        assert.containsN(kanban,'.o_kanban_group',2,"shouldhavetwocolumns");
        assert.strictEqual(kanban.$('.o_kanban_group:first').data('id'),3,
            'firstcolumnshouldbe[3,"hello"]');
        assert.strictEqual(kanban.$('.o_kanban_group:last').data('id'),5,
            'secondcolumnshouldbe[5,"xmo"]');
        assert.strictEqual(kanban.$('.o_kanban_group:last.o_column_title').text(),'xmo',
            'secondcolumnshouldhavecorrecttitle');
        assert.containsN(kanban,'.o_kanban_group:last.o_kanban_record',2,
            "secondcolumnshouldhavetworecords");

        //checkavailableactionsinkanbanheader'sconfigdropdown
        assert.ok(kanban.$('.o_kanban_group:first.o_kanban_toggle_fold').length,
                        "shouldbeabletofoldthecolumn");
        assert.ok(kanban.$('.o_kanban_group:first.o_column_edit').length,
                        "shouldbeabletoeditthecolumn");
        assert.ok(kanban.$('.o_kanban_group:first.o_column_delete').length,
                        "shouldbeabletodeletethecolumn");
        assert.ok(!kanban.$('.o_kanban_group:first.o_column_archive_records').length,"shouldnotbeabletoarchivealltherecords");
        assert.ok(!kanban.$('.o_kanban_group:first.o_column_unarchive_records').length,"shouldnotbeabletorestorealltherecords");

        //deletesecondcolumn(firstcanceltheconfirmrequest,thenconfirm)
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_delete'));
        assert.ok($('.modal').length,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.modal.clickButton('Cancel');//clickoncancel
        assert.strictEqual(kanban.$('.o_kanban_group:last').data('id'),5,
            'column[5,"xmo"]shouldstillbethere');
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_delete'));
        assert.ok($('.modal').length,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.modal.clickButton('Ok');//clickonconfirm
        assert.strictEqual(kanban.$('.o_kanban_group:last').data('id'),3,
            'lastcolumnshouldnowbe[3,"hello"]');
        assert.containsN(kanban,'.o_kanban_group',2,"shouldstillhavetwocolumns");
        assert.ok(!_.isNumber(kanban.$('.o_kanban_group:first').data('id')),
            'firstcolumnshouldhavenoid(Undefinedcolumn)');
        //checkavailableactionson'Undefined'column
        assert.ok(kanban.$('.o_kanban_group:first.o_kanban_toggle_fold').length,
                        "shouldbeabletofoldthecolumn");
        assert.ok(!kanban.$('.o_kanban_group:first.o_column_delete').length,
            'Undefinedcolumncouldnotbedeleted');
        assert.ok(!kanban.$('.o_kanban_group:first.o_column_edit').length,
            'Undefinedcolumncouldnotbeedited');
        assert.ok(!kanban.$('.o_kanban_group:first.o_column_archive_records').length,"Recordsofundefinedcolumncouldnotbearchived");
        assert.ok(!kanban.$('.o_kanban_group:first.o_column_unarchive_records').length,"Recordsofundefinedcolumncouldnotberestored");
        assert.verifySteps(['web_read_group','unlink','web_read_group']);
        assert.strictEqual(kanban.renderer.widgets.length,2,
            "theoldwidgetsshouldhavebeencorrectlydeleted");

        //testcolumndraganddrophavingan'Undefined'column
        awaittestUtils.dom.dragAndDrop(
            kanban.$('.o_column_title:first'),
            kanban.$('.o_column_title:last'),{position:'right'}
        );
        assert.strictEqual(resequencedIDs,undefined,
            "resequencingrequireatleast2notUndefinedcolumns");
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_quick_create_folded'));
        kanban.$('.o_column_quick_createinput').val('oncethirdcolumn');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));
        varnewColumnID=kanban.$('.o_kanban_group:last').data('id');
        awaittestUtils.dom.dragAndDrop(
            kanban.$('.o_column_title:first'),
            kanban.$('.o_column_title:last'),{position:'right'}
        );
        assert.deepEqual([3,newColumnID],resequencedIDs,
            "movingtheUndefinedcolumnshouldnotaffectorderofothercolumns");
        awaittestUtils.dom.dragAndDrop(
            kanban.$('.o_column_title:first'),
            kanban.$('.o_column_title:nth(1)'),{position:'right'}
        );
        awaitnextTick();//waitforresequenceafterdraganddrop
        assert.deepEqual([newColumnID,3],resequencedIDs,
            "movedcolumnshouldberesequencedaccordingly");
        assert.verifySteps(['name_create','read','read','read']);

        kanban.destroy();
        testUtils.mock.unpatch(KanbanRenderer);
    });

    QUnit.test('createacolumn,deleteitandcreateanotherone',asyncfunction(assert){
        assert.expect(5);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.containsN(kanban,'.o_kanban_group',2,"shouldhavetwocolumns");

        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_quick_create_folded'));
        kanban.$('.o_column_quick_createinput').val('newcolumn1');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group',3,"shouldhavetwocolumns");

        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:last'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:last.o_column_delete'));
        awaittestUtils.modal.clickButton('Ok');

        assert.containsN(kanban,'.o_kanban_group',2,"shouldhavetwoscolumns");

        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_quick_create_folded'));
        kanban.$('.o_column_quick_createinput').val('newcolumn2');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        assert.containsN(kanban,'.o_kanban_group',3,"shouldhavethreecolumns");
        assert.strictEqual(kanban.$('.o_kanban_group:lastspan:contains(newcolumn2)').length,1,
            "thelastcolumnshouldbethenewlycreatedone");
        kanban.destroy();
    });

    QUnit.test('editacolumningroupedonm2o',asyncfunction(assert){
        assert.expect(12);

        varnbRPCs=0;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            archs:{
                'product,false,form':'<formstring="Product"><fieldname="display_name"/></form>',
            },
            mockRPC:function(route,args){
                nbRPCs++;
                returnthis._super(route,args);
            },
        });
        assert.strictEqual(kanban.$('.o_kanban_group[data-id=5].o_column_title').text(),'xmo',
            'titleofthecolumnshouldbe"xmo"');

        //editthetitleofcolumn[5,'xmo']andclosewithoutsaving
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group[data-id=5]'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group[data-id=5].o_column_edit'));
        assert.containsOnce(document.body,'.modal.o_form_editable',
            "aformviewshouldbeopeninamodal");
        assert.strictEqual($('.modal.o_form_editableinput').val(),'xmo',
            'thenameshouldbe"xmo"');
        awaittestUtils.fields.editInput($('.modal.o_form_editableinput'),'ged');//changethevalue
        nbRPCs=0;
        awaittestUtils.dom.click($('.modal-header.close'));
        assert.containsNone(document.body,'.modal');
        assert.strictEqual(kanban.$('.o_kanban_group[data-id=5].o_column_title').text(),'xmo',
            'titleofthecolumnshouldstillbe"xmo"');
        assert.strictEqual(nbRPCs,0,'noRPCshouldhavebeendone');

        //editthetitleofcolumn[5,'xmo']anddiscard
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group[data-id=5]'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group[data-id=5].o_column_edit'));
        awaittestUtils.fields.editInput($('.modal.o_form_editableinput'),'ged');//changethevalue
        nbRPCs=0;
        awaittestUtils.modal.clickButton('Discard');
        assert.containsNone(document.body,'.modal');
        assert.strictEqual(kanban.$('.o_kanban_group[data-id=5].o_column_title').text(),'xmo',
            'titleofthecolumnshouldstillbe"xmo"');
        assert.strictEqual(nbRPCs,0,'noRPCshouldhavebeendone');

        //editthetitleofcolumn[5,'xmo']andsave
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group[data-id=5]'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group[data-id=5].o_column_edit'));
        awaittestUtils.fields.editInput($('.modal.o_form_editableinput'),'ged');//changethevalue
        nbRPCs=0;
        awaittestUtils.modal.clickButton('Save');//clickonsave
        assert.ok(!$('.modal').length,'themodalshouldbeclosed');
        assert.strictEqual(kanban.$('.o_kanban_group[data-id=5].o_column_title').text(),'ged',
            'titleofthecolumnshouldbe"ged"');
        assert.strictEqual(nbRPCs,4,'shouldhavedone1write,1read_groupand2search_read');
        kanban.destroy();
    });

    QUnit.test('editacolumnpropagatesrightcontext',asyncfunction(assert){
        assert.expect(4);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            archs:{
                'product,false,form':'<formstring="Product"><fieldname="display_name"/></form>',
            },
            session:{user_context:{lang:'brol'}},
            mockRPC:function(route,args){
                letcontext;
                if(route==='/web/dataset/search_read'&&args.model==='partner'){
                    context=args.context;
                    assert.strictEqual(context.lang,'brol',
                        'langispresentincontextforpartneroperations');
                }
                if(args.model==='product'){
                    context=args.kwargs.context;
                    assert.strictEqual(context.lang,'brol',
                        'langispresentincontextforproductoperations');
                }
                returnthis._super.apply(this,arguments);
            },
        });
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group[data-id=5]'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group[data-id=5].o_column_edit'));
        kanban.destroy();
    });

    QUnit.test('quickcreatecolumnshouldbeopenedifthereisnocolumn',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            domain:[['foo','=','norecord']],
        });

        assert.containsNone(kanban,'.o_kanban_group');
        assert.containsOnce(kanban,'.o_column_quick_create');
        assert.ok(kanban.$('.o_column_quick_createinput').is(':visible'),
            "thequickcreateshouldbeopened");

        kanban.destroy();
    });

    QUnit.test('quickcreateseveralcolumnsinarow',asyncfunction(assert){
        assert.expect(10);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.containsN(kanban,'.o_kanban_group',2,
            "shouldhavetwocolumns");
        assert.containsOnce(kanban,'.o_column_quick_create',
            "shouldhaveaColumnQuickCreatewidget");
        assert.containsOnce(kanban,'.o_column_quick_create.o_quick_create_folded:visible',
            "theColumnQuickCreateshouldbefolded");
        assert.containsNone(kanban,'.o_column_quick_create.o_quick_create_unfolded:visible',
            "theColumnQuickCreateshouldbefolded");

        //addanewcolumn
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_quick_create_folded'));
        assert.containsNone(kanban,'.o_column_quick_create.o_quick_create_folded:visible',
            "theColumnQuickCreateshouldbeunfolded");
        assert.containsOnce(kanban,'.o_column_quick_create.o_quick_create_unfolded:visible',
            "theColumnQuickCreateshouldbeunfolded");
        kanban.$('.o_column_quick_createinput').val('NewColumn1');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.btn-primary'));
        assert.containsN(kanban,'.o_kanban_group',3,
            "shouldnowhavethreecolumns");

        //addanothercolumn
        assert.containsNone(kanban,'.o_column_quick_create.o_quick_create_folded:visible',
            "theColumnQuickCreateshouldstillbeunfolded");
        assert.containsOnce(kanban,'.o_column_quick_create.o_quick_create_unfolded:visible',
            "theColumnQuickCreateshouldstillbeunfolded");
        kanban.$('.o_column_quick_createinput').val('NewColumn2');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.btn-primary'));
        assert.containsN(kanban,'.o_kanban_group',4,
            "shouldnowhavefourcolumns");

        kanban.destroy();
    });

    QUnit.test('quickcreatecolumnandexamples',asyncfunction(assert){
        assert.expect(12);

        kanbanExamplesRegistry.add('test',{
            examples:[{
                name:"Afirstexample",
                columns:["Column1","Column2","Column3"],
                description:"Somedescription",
            },{
                name:"Asecondexample",
                columns:["Col1","Col2"],
            }],
        });

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanexamples="test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.containsOnce(kanban,'.o_column_quick_create',
            "shouldhaveaColumnQuickCreatewidget");

        //openthequickcreate
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_quick_create_folded'));

        assert.containsOnce(kanban,'.o_column_quick_create.o_kanban_examples:visible',
            "shouldhavealinktoseeexamples");

        //clicktoseetheexamples
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_kanban_examples'));

        assert.strictEqual($('.modal.o_kanban_examples_dialog').length,1,
            "shouldhaveopentheexamplesdialog");
        assert.strictEqual($('.modal.o_kanban_examples_dialog_navli').length,2,
            "shouldhavetwoexamples(inthemenu)");
        assert.strictEqual($('.modal.o_kanban_examples_dialog_nava').text(),
            'Afirstexample Asecondexample',"examplenamesshouldbecorrect");
        assert.strictEqual($('.modal.o_kanban_examples_dialog_content.tab-pane').length,2,
            "shouldhavetwoexamples");

        var$firstPane=$('.modal.o_kanban_examples_dialog_content.tab-pane:first');
        assert.strictEqual($firstPane.find('.o_kanban_examples_group').length,3,
            "thereshouldbe3stagesinthefirstexample");
        assert.strictEqual($firstPane.find('h6').text(),'Column1Column2Column3',
            "columntitlesshouldbecorrect");
        assert.strictEqual($firstPane.find('.o_kanban_examples_description').text().trim(),
            "Somedescription","thecorrectdescriptionshouldbedisplayed");

        var$secondPane=$('.modal.o_kanban_examples_dialog_content.tab-pane:nth(1)');
        assert.strictEqual($secondPane.find('.o_kanban_examples_group').length,2,
            "thereshouldbe2stagesinthesecondexample");
        assert.strictEqual($secondPane.find('h6').text(),'Col1Col2',
            "columntitlesshouldbecorrect");
        assert.strictEqual($secondPane.find('.o_kanban_examples_description').text().trim(),
            "","thereshouldbenodescriptionforthesecondexample");

        kanban.destroy();
    });

    QUnit.test('quickcreatecolumnandexamplesbackgroundwithghostColumnstitles',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records=[];

        kanbanExamplesRegistry.add('test',{
            ghostColumns:["Ghost1","Ghost2","Ghost3","Ghost4"],
            examples:[{
                name:"Afirstexample",
                columns:["Column1","Column2","Column3"],
                description:"Somedescription",
            },{
                name:"Asecondexample",
                columns:["Col1","Col2"],
            }],
        });

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanexamples="test">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.containsOnce(kanban,'.o_kanban_example_background',
            "shouldhaveExamplesBackgroundwhennodata");
        assert.strictEqual(kanban.$('.o_kanban_examples_grouph6').text(),'Ghost1Ghost2Ghost3Ghost4',
            "ghosttitleshouldbecorrect");
        assert.containsOnce(kanban,'.o_column_quick_create',
            "shouldhaveaColumnQuickCreatewidget");
        assert.containsOnce(kanban,'.o_column_quick_create.o_kanban_examples:visible',
            "shouldnothavealinktoseeexamplesasthereisnoexamplesregistered");

        kanban.destroy();
    });

    QUnit.test('quickcreatecolumnandexamplesbackgroundwithoutghostColumnstitles',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.containsOnce(kanban,'.o_kanban_example_background',
            "shouldhaveExamplesBackgroundwhennodata");
        assert.strictEqual(kanban.$('.o_kanban_examples_grouph6').text(),'Column1Column2Column3Column4',
            "ghosttitleshouldbecorrect");
        assert.containsOnce(kanban,'.o_column_quick_create',
            "shouldhaveaColumnQuickCreatewidget");
        assert.containsNone(kanban,'.o_column_quick_create.o_kanban_examples:visible',
            "shouldnothavealinktoseeexamplesasthereisnoexamplesregistered");

        kanban.destroy();
    });

    QUnit.test('nocontenthelperafteraddingarecord(kanbanwithprogressbar)',asyncfunction(assert){
        assert.expect(3);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`<kanban>
                    <fieldname="product_id"/>
                    <progressbarfield="foo"colors='{"yop":"success","gnap":"warning","blip":"danger"}'sum_field="int_field"/>
                    <templates>
                      <tt-name="kanban-box">
                        <div><fieldname="foo"/></div>
                      </t>
                    </templates>
                </kanban>`,
            groupBy:['product_id'],
            domain:[['foo','=','abcd']],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    constresult={
                        groups:[
                            {__domain:[['product_id','=',3]],product_id_count:0,product_id:[3,'hello']},
                        ],
                    };
                    returnPromise.resolve(result);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsOnce(kanban,'.o_view_nocontent',"thenocontenthelperisdisplayed");

        //addarecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_create.o_input'),'twilightsparkle');
        awaittestUtils.dom.click(kanban.$('button.o_kanban_add'));

        assert.containsNone(kanban,'.o_view_nocontent',
            "thenocontenthelperisnotdisplayedafterquickcreate");

        //cancelquickcreate
        awaittestUtils.dom.click(kanban.$('button.o_kanban_cancel'));
        assert.containsNone(kanban,'.o_view_nocontent',
            "thenocontenthelperisnotdisplayedaftercancellingthequickcreate");

        kanban.destroy();
    });

    QUnit.test('ifviewwasnotgroupedatstart,itcanbegroupedandungrouped',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"on_create="quick_create">'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
        });

        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'o_kanban_grouped');
        awaitkanban.update({groupBy:['product_id']});
        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_grouped');
        awaitkanban.update({groupBy:[]});
        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'o_kanban_grouped');

        kanban.destroy();
    });

    QUnit.test('nocontenthelperwhenarchiveallrecordsinkanbangroup',asyncfunction(assert){
        assert.expect(3);

        //addactivefieldonpartnermodeltohavearchiveoption
        this.data.partner.fields.active={string:'Active',type:'boolean',default:true};
        //removelastrecordstohaveonlyonecolumn
        this.data.partner.records=this.data.partner.records.slice(0,3);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`<kanbanclass="o_kanban_test">
                        <fieldname="active"/>
                        <fieldname="bar"/>
                        <templates>
                            <tt-name="kanban-box">
                               <div><fieldname="foo"/></div>
                            </t>
                        </templates>
                    </kanban>`,
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                }
            },
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/action_archive'){
                    constpartnerIDS=args.args[0];
                    constrecords=this.data.partner.records;
                    _.each(partnerIDS,function(partnerID){
                        _.find(records,function(record){
                            returnrecord.id===partnerID;
                        }).active=false;
                    });
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //checkthatthe(unique)columncontains3records
        assert.containsN(kanban,'.o_kanban_group:last.o_kanban_record',3);

        //archivetherecordsofthelastcolumn
        testUtils.kanban.toggleGroupSettings($(kanban.el.querySelector('.o_kanban_group')));//weshouldchangethehelper
        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_group.o_column_archive_records'));
        assert.containsOnce(document.body,'.modal');
        awaittestUtils.modal.clickButton('Ok');
        //checknocontenthelperisexist
        assert.containsOnce(kanban,'.o_view_nocontent');
        kanban.destroy();
    });

    QUnit.test('nocontenthelperwhennodata',asyncfunction(assert){
        assert.expect(3);

        varrecords=this.data.partner.records;

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                    '<div>'+
                    '<tt-esc="record.foo.value"/>'+
                    '<fieldname="foo"/>'+
                    '</div>'+
                '</t></templates></kanban>',
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                }
            },
        });

        assert.containsOnce(kanban,'.o_view_nocontent',
            "shoulddisplaythenocontenthelper");

        assert.strictEqual(kanban.$('.o_view_nocontentp.hello:contains(addapartner)').length,1,
            "shouldhaverenderednocontenthelperfromaction");

        this.data.partner.records=records;
        awaitkanban.reload();

        assert.containsNone(kanban,'.o_view_nocontent',
            "shouldnotdisplaythenocontenthelper");
        kanban.destroy();
    });

    QUnit.test('nonocontenthelperforgroupedkanbanwithemptygroups',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    returnthis._super.apply(this,arguments).then(function(result){
                        _.each(result.groups,function(group){
                            group[args.kwargs.groupby[0]+'_count']=0;
                        });
                        returnresult;
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2,
            "thereshouldbetwocolumns");
        assert.containsNone(kanban,'.o_kanban_record',
            "thereshouldbenorecords");

        kanban.destroy();
    });

    QUnit.test('nonocontenthelperforgroupedkanbanwithnorecords',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsNone(kanban,'.o_kanban_group',
            "thereshouldbenocolumns");
        assert.containsNone(kanban,'.o_kanban_record',
            "thereshouldbenorecords");
        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldbenonocontenthelper(wearein'columncreationmode')");
        assert.containsOnce(kanban,'.o_column_quick_create',
            "thereshouldbeacolumnquickcreate");
        kanban.destroy();
    });

    QUnit.test('nonocontenthelperisshownwhennolongercreatingcolumn',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldbenonocontenthelper(wearein'columncreationmode')");

        //creatinganewcolumn
        kanban.$('.o_column_quick_create.o_input').val('applejack');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_create.o_kanban_add'));

        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldbenonocontenthelper(stillin'columncreationmode')");

        //leavingcolumncreationmode
        kanban.$('.o_column_quick_create.o_input').trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ESCAPE,
            which:$.ui.keyCode.ESCAPE,
        }));

        assert.containsOnce(kanban,'.o_view_nocontent',
            "thereshouldbeanocontenthelper");

        kanban.destroy();
    });

    QUnit.test('nonocontenthelperishiddenwhenquickcreatingacolumn',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    varresult={
                        groups:[
                            {__domain:[['product_id','=',3]],product_id_count:0,product_id:[3,'hello']},
                        ],
                        length:1,
                    };
                    returnPromise.resolve(result);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsOnce(kanban,'.o_view_nocontent',
            "thereshouldbeanocontenthelper");

        awaittestUtils.dom.click(kanban.$('.o_kanban_add_column'));

        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldbenonocontenthelper(wearein'columncreationmode')");

        kanban.destroy();
    });

    QUnit.test('removenocontenthelperafteraddingarecord',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    varresult={
                        groups:[
                            {__domain:[['product_id','=',3]],product_id_count:0,product_id:[3,'hello']},
                        ],
                        length:1,
                    };
                    returnPromise.resolve(result);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsOnce(kanban,'.o_view_nocontent',
            "thereshouldbeanocontenthelper");

        //addarecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_create.o_input'),'twilightsparkle');
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_createbutton.o_kanban_add'));

        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldbenonocontenthelper(thereisnowonerecord)");

        kanban.destroy();
    });

    QUnit.test('removenocontenthelperwhenaddingarecord',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    varresult={
                        groups:[
                            {__domain:[['product_id','=',3]],product_id_count:0,product_id:[3,'hello']},
                        ],
                        length:1,
                    };
                    returnPromise.resolve(result);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsOnce(kanban,'.o_view_nocontent',
            "thereshouldbeanocontenthelper");

        //addarecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_create.o_input'),'twilightsparkle');

        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldbenonocontenthelper(thereisnowonerecord)");

        kanban.destroy();
    });

    QUnit.test('nocontenthelperisdisplayedagainaftercancelingquickcreate',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="name"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    varresult={
                        groups:[
                            {__domain:[['product_id','=',3]],product_id_count:0,product_id:[3,'hello']},
                        ],
                        length:1,
                    };
                    returnPromise.resolve(result);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        //addarecord
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add'));

        awaittestUtils.dom.click(kanban.$('.o_kanban_view'));

        assert.containsOnce(kanban,'.o_view_nocontent',
            "thereshouldbeagainanocontenthelper");

        kanban.destroy();
    });

    QUnit.test('nocontenthelperforgroupedkanbanwithnorecordswithnogroup_create',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbangroup_create="false">'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsNone(kanban,'.o_kanban_group',
            "thereshouldbenocolumns");
        assert.containsNone(kanban,'.o_kanban_record',
            "thereshouldbenorecords");
        assert.containsNone(kanban,'.o_view_nocontent',
            "thereshouldnotbeanocontenthelper");
        assert.containsNone(kanban,'.o_column_quick_create',
            "thereshouldnotbeacolumnquickcreate");
        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledataandnocolumns',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records=[];

        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsNone(kanban,'.o_view_nocontent');
        assert.containsOnce(kanban,'.o_quick_create_unfolded');
        assert.containsOnce(kanban,'.o_kanban_example_background_container');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledataandclickquickcreate',asyncfunction(assert){
        assert.expect(11);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="foo"/></div>
                        </t>
                    </templates>
                </kanban>`,
            groupBy:['product_id'],
            asyncmockRPC(route,{kwargs,method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    result.groups.forEach(group=>{
                        group[`${kwargs.groupby[0]}_count`]=0;
                    });
                }
                returnresult;
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2,
            "thereshouldbetwocolumns");
        assert.hasClass(kanban.$el,'o_view_sample_data');
        assert.containsOnce(kanban,'.o_view_nocontent');
        assert.containsN(kanban,'.o_kanban_record',16,
            "thereshouldbe8samplerecordsbycolumn");

        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add:first'));
        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsNone(kanban,'.o_kanban_record');
        assert.containsNone(kanban,'.o_view_nocontent');
        assert.containsOnce(kanban.$('.o_kanban_group:first'),'.o_kanban_quick_create');

        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_create.o_input'),'twilightsparkle');
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_createbutton.o_kanban_add'));

        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsOnce(kanban.$('.o_kanban_group:first'),'.o_kanban_record');
        assert.containsNone(kanban,'.o_view_nocontent');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledataandcancelquickcreate',asyncfunction(assert){
        assert.expect(12);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="foo"/></div>
                        </t>
                    </templates>
                </kanban>`,
            groupBy:['product_id'],
            asyncmockRPC(route,{kwargs,method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    result.groups.forEach(group=>{
                        group[`${kwargs.groupby[0]}_count`]=0;
                    });
                }
                returnresult;
            },
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2,
            "thereshouldbetwocolumns");
        assert.hasClass(kanban.$el,'o_view_sample_data');
        assert.containsOnce(kanban,'.o_view_nocontent');
        assert.containsN(kanban,'.o_kanban_record',16,
            "thereshouldbe8samplerecordsbycolumn");

        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add:first'));
        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsNone(kanban,'.o_kanban_record');
        assert.containsNone(kanban,'.o_view_nocontent');
        assert.containsOnce(kanban.$('.o_kanban_group:first'),'.o_kanban_quick_create');

        awaittestUtils.dom.click(kanban.$('.o_kanban_view'));
        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsNone(kanban,'.o_kanban_quick_create');
        assert.containsNone(kanban,'.o_kanban_record');
        assert.containsOnce(kanban,'.o_view_nocontent');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledata:keyboardnavigation',asyncfunction(assert){
        assert.expect(5);

        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                            <fieldname="state"widget="priority"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            asyncmockRPC(route,{kwargs,method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    result.groups.forEach(g=>g.product_id_count=0);
                }
                returnresult;
            },
        });

        //Checkkeynavisdisabled
        assert.hasClass(
            kanban.el.querySelector('.o_kanban_record'),
            'o_sample_data_disabled'
        );
        assert.hasClass(
            kanban.el.querySelector('.o_kanban_toggle_fold'),
            'o_sample_data_disabled'
        );
        assert.containsNone(kanban.renderer,'[tabindex]:not([tabindex="-1"])');

        assert.hasClass(document.activeElement,'o_searchview_input');

        awaittestUtils.fields.triggerKeydown(document.activeElement,'down');

        assert.hasClass(document.activeElement,'o_searchview_input');

        kanban.destroy();
    });

    QUnit.test('emptykanbanwithsampledata',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records=[];

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="foo"/></div>
                        </t>
                    </templates>
                </kanban>`,
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.hasClass(kanban.$el,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',10,
            "thereshouldbe10samplerecords");
        assert.containsOnce(kanban,'.o_view_nocontent');

        awaitkanban.reload({domain:[['id','<',0]]});
        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsNone(kanban,'.o_kanban_record:not(.o_kanban_ghost)');
        assert.containsOnce(kanban,'.o_view_nocontent');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledataandmany2many_tags',asyncfunction(assert){
        assert.expect(6);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="int_field"/>
                                <fieldname="category_ids"widget="many2many_tags"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            groupBy:['product_id'],
            asyncmockRPC(route,{kwargs,method}){
                assert.step(method||route);
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    result.groups.forEach(group=>{
                        group[`${kwargs.groupby[0]}_count`]=0;
                    });
                }
                returnresult;
            },
        });

        assert.containsN(kanban,'.o_kanban_group',2,"thereshouldbe2'real'columns");
        assert.hasClass(kanban.$el,'o_view_sample_data');
        assert.ok(kanban.$('.o_kanban_record').length>=1,"thereshouldbesamplerecords");
        assert.ok(kanban.$('.o_field_many2manytags.o_tag').length>=1,"thereshouldbetags");

        assert.verifySteps(["web_read_group"],"shouldnotreadthetags");
        kanban.destroy();
    });

    QUnit.test('sampledatadoesnotchangeafterreloadwithsampledata',asyncfunction(assert){
        assert.expect(4);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="int_field"/></div>
                        </t>
                    </templates>
                </kanban>`,
            groupBy:['product_id'],
            asyncmockRPC(route,{kwargs,method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    result.groups.forEach(group=>{
                        group[`${kwargs.groupby[0]}_count`]=0;
                    });
                }
                returnresult;
            },
        });

        constcolumns=kanban.el.querySelectorAll('.o_kanban_group');

        assert.ok(columns.length>=1,"thereshouldbeatleast1samplecolumn");
        assert.hasClass(kanban.$el,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_record',16);

        constkanbanText=kanban.el.innerText;
        awaitkanban.reload();

        assert.strictEqual(kanbanText,kanban.el.innerText,
            "thecontentshouldbethesameafterreloadingtheview");

        kanban.destroy();
    });

    QUnit.test('nonemptykanbanwithsampledata',asyncfunction(assert){
        assert.expect(5);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="foo"/></div>
                        </t>
                    </templates>
                </kanban>`,
            viewOptions:{
                action:{
                    help:"Nocontenthelper",
                },
            },
        });

        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);
        assert.containsNone(kanban,'.o_view_nocontent');

        awaitkanban.reload({domain:[['id','<',0]]});
        assert.doesNotHaveClass(kanban.$el,'o_view_sample_data');
        assert.containsNone(kanban,'.o_kanban_record:not(.o_kanban_ghost)');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledata:addacolumn',asyncfunction(assert){
        assert.expect(6);

        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            asyncmockRPC(route,{method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    result.groups=this.data.product.records.map(r=>{
                        return{
                            product_id:[r.id,r.display_name],
                            product_id_count:0,
                            __domain:['product_id','=',r.id],
                        };
                    });
                    result.length=result.groups.length;
                }
                returnresult;
            },
        });

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_group',2);
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_add_column'));
        awaittestUtils.fields.editInput(kanban.el.querySelector('.o_kanban_headerinput'),"Yoohoo");
        awaittestUtils.dom.click(kanban.el.querySelector('.btn.o_kanban_add'));

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_group',3);
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledata:cannotfoldacolumn',asyncfunction(assert){
        //foldingacolumningroupedkanbanwithsampledataisdisabled,forthesakeofsimplicity
        assert.expect(5);

        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            asyncmockRPC(route,{kwargs,method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnasingle,emptygroup
                    result.groups=result.groups.slice(0,1);
                    result.groups[0][`${kwargs.groupby[0]}_count`]=0;
                    result.length=1;
                }
                returnresult;
            },
        });

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsOnce(kanban,'.o_kanban_group');
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_config>a'));

        assert.hasClass(kanban.el.querySelector('.o_kanban_config.o_kanban_toggle_fold'),'o_sample_data_disabled');
        assert.hasClass(kanban.el.querySelector('.o_kanban_config.o_kanban_toggle_fold'),'disabled');

        kanban.destroy();
    });

    QUnit.skip('emptygroupedkanbanwithsampledata:fold/unfoldacolumn',asyncfunction(assert){
        //folding/unfoldingofgroupedkanbanwithsampledataiscurrentlydisabled
        assert.expect(8);

        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            asyncmockRPC(route,{kwargs,method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnasingle,emptygroup
                    result.groups=result.groups.slice(0,1);
                    result.groups[0][`${kwargs.groupby[0]}_count`]=0;
                    result.length=1;
                }
                returnresult;
            },
        });

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsOnce(kanban,'.o_kanban_group');
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        //Foldthecolumn
        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_config>a'));
        awaittestUtils.dom.click(kanban.el.querySelector('.dropdown-item.o_kanban_toggle_fold'));

        assert.containsOnce(kanban,'.o_kanban_group');
        assert.hasClass(kanban.$('.o_kanban_group'),'o_column_folded');

        //Unfoldthecolumn
        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_group.o_column_folded'));

        assert.containsOnce(kanban,'.o_kanban_group');
        assert.doesNotHaveClass(kanban.$('.o_kanban_group'),'o_column_folded');
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledata:deleteacolumn',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records=[];

        letgroups=[{
            product_id:[1,'New'],
            product_id_count:0,
            __domain:[],
        }];
        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            asyncmockRPC(route,{method}){
                letresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    //overrideread_grouptoreturnasingle,emptygroup
                    return{
                        groups,
                        length:groups.length,
                    };
                }
                returnresult;
            },
        });

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsOnce(kanban,'.o_kanban_group');
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        //Deletethefirstcolumn
        groups=[];
        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_config>a'));
        awaittestUtils.dom.click(kanban.el.querySelector('.dropdown-item.o_column_delete'));
        awaittestUtils.dom.click(document.querySelector('.modal.btn-primary'));

        assert.containsNone(kanban,'.o_kanban_group');
        assert.containsOnce(kanban,'.o_column_quick_create.o_quick_create_unfolded');

        kanban.destroy();
    });

    QUnit.test('emptygroupedkanbanwithsampledata:addacolumnanddeleteitrightaway',asyncfunction(assert){
        assert.expect(9);

        constkanban=awaitcreateView({
            arch:`
                <kanbansample="1">
                    <fieldname="product_id"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:['product_id'],
            model:'partner',
            View:KanbanView,
            asyncmockRPC(route,{method}){
                constresult=awaitthis._super(...arguments);
                if(method==='web_read_group'){
                    result.groups=this.data.product.records.map(r=>{
                        return{
                            product_id:[r.id,r.display_name],
                            product_id_count:0,
                            __domain:['product_id','=',r.id],
                        };
                    });
                    result.length=result.groups.length;
                }
                returnresult;
            },
        });

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_group',2);
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        //addanewcolumn
        awaittestUtils.dom.click(kanban.el.querySelector('.o_kanban_add_column'));
        awaittestUtils.fields.editInput(kanban.el.querySelector('.o_kanban_headerinput'),"Yoohoo");
        awaittestUtils.dom.click(kanban.el.querySelector('.btn.o_kanban_add'));

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_group',3);
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        //deletethecolumnwejustcreated
        constnewColumn=kanban.el.querySelectorAll('.o_kanban_group')[2];
        awaittestUtils.dom.click(newColumn.querySelector('.o_kanban_config>a'));
        awaittestUtils.dom.click(newColumn.querySelector('.dropdown-item.o_column_delete'));
        awaittestUtils.dom.click(document.querySelector('.modal.btn-primary'));

        assert.hasClass(kanban,'o_view_sample_data');
        assert.containsN(kanban,'.o_kanban_group',2);
        assert.ok(kanban.$('.o_kanban_record').length>0,'shouldcontainsamplerecords');

        kanban.destroy();
    });

    QUnit.test('bouncecreatebuttonwhennodataandclickonemptyarea',asyncfunction(assert){
        assert.expect(2);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">
                    <div>
                        <tt-esc="record.foo.value"/>
                        <fieldname="foo"/>
                    </div>
                </t></templates></kanban>`,
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                }
            },
        });

        awaittestUtils.dom.click(kanban.$('.o_kanban_view'));
        assert.doesNotHaveClass(kanban.$('.o-kanban-button-new'),'o_catch_attention');

        awaitkanban.reload({domain:[['id','<',0]]});

        awaittestUtils.dom.click(kanban.$('.o_kanban_view'));
        assert.hasClass(kanban.$('.o-kanban-button-new'),'o_catch_attention');

        kanban.destroy();
    });

    QUnit.test('buttonswithmodifiers',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[1].bar=false;//sothattestismorecomplete

        varkanban=awaitcreateView({
            View:KanbanView,
            model:"partner",
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="state"/>'+
                    '<templates><divt-name="kanban-box">'+
                        '<buttonclass="o_btn_test_1"type="object"name="a1"'+
                            'attrs="{\'invisible\':[[\'foo\',\'!=\',\'yop\']]}"/>'+
                        '<buttonclass="o_btn_test_2"type="object"name="a2"'+
                            'attrs="{\'invisible\':[[\'bar\',\'=\',True]]}"'+
                            'states="abc,def"/>'+
                    '</div></templates>'+
                '</kanban>',
        });

        assert.containsOnce(kanban,".o_btn_test_1",
            "kanbanshouldhaveonebuttonsoftype1");
        assert.containsN(kanban,".o_btn_test_2",3,
            "kanbanshouldhavethreebuttonsoftype2");
        kanban.destroy();
    });

    QUnit.test('buttonexecutesactionandreloads',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:"partner",
            data:this.data,
            arch:
                '<kanban>'+
                    '<templates><divt-name="kanban-box">'+
                        '<fieldname="foo"/>'+
                        '<buttontype="object"name="a1"/>'+
                    '</div></templates>'+
                '</kanban>',
            mockRPC:function(route){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            },
        });

        assert.ok(kanban.$('button[data-name="a1"]').length,
            "kanbanshouldhaveatleastonebuttona1");

        varcount=0;
        testUtils.mock.intercept(kanban,'execute_action',function(event){
            count++;
            event.data.on_closed();
        });
        awaittestUtils.dom.click($('button[data-name="a1"]').first());
        assert.strictEqual(count,1,"shouldhavetriggeredaexecuteaction");

        awaittestUtils.dom.click($('button[data-name="a1"]').first());
        assert.strictEqual(count,1,"double-clickonkanbanactionsshouldbedebounced");

        assert.verifySteps([
            '/web/dataset/search_read',
            '/web/dataset/call_kw/partner/read'
        ],'areadshouldbedoneafterthecallbuttontoreloadtherecord');

        kanban.destroy();
    });

    QUnit.test('buttonexecutesactionandcheckdomain',asyncfunction(assert){
        assert.expect(2);

        vardata=this.data;
        data.partner.fields.active={string:"Active",type:"boolean",default:true};
        for(varkinthis.data.partner.records){
            data.partner.records[k].active=true;
        }

        varkanban=awaitcreateView({
            View:KanbanView,
            model:"partner",
            data:data,
            arch:
                '<kanban>'+
                    '<templates><divt-name="kanban-box">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="active"/>'+
                        '<buttontype="object"name="a1"/>'+
                        '<buttontype="object"name="toggle_active"/>'+
                    '</div></templates>'+
                '</kanban>',
        });

        testUtils.mock.intercept(kanban,'execute_action',function(event){
            data.partner.records[0].active=false;
            event.data.on_closed();
        });

        assert.strictEqual(kanban.$('.o_kanban_record:contains(yop)').length,1,"shoulddisplay'yop'record");
        awaittestUtils.dom.click(kanban.$('.o_kanban_record:contains(yop)button[data-name="toggle_active"]'));
        assert.strictEqual(kanban.$('.o_kanban_record:contains(yop)').length,0,"shouldremove'yop'recordfromtheview");

        kanban.destroy();
    });

    QUnit.test('buttonexecutesactionwithdomainfieldnotinview',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:"partner",
            data:this.data,
            domain:[['bar','=',true]],
            arch:
                '<kanban>'+
                    '<templates><divt-name="kanban-box">'+
                        '<fieldname="foo"/>'+
                        '<buttontype="object"name="a1"/>'+
                        '<buttontype="object"name="toggle_action"/>'+
                    '</div></templates>'+
                '</kanban>',
        });

        testUtils.mock.intercept(kanban,'execute_action',function(event){
            event.data.on_closed();
        });

        try{
            awaittestUtils.dom.click(kanban.$('.o_kanban_record:contains(yop)button[data-name="toggle_action"]'));
            assert.strictEqual(true,true,'Everythingwentfine');
        }catch(e){
            assert.strictEqual(true,false,'Errortriggeredatactionexecution');
        }
        kanban.destroy();
    });

    QUnit.test('renderingdateanddatetime',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].date="2017-01-25";
        this.data.partner.records[1].datetime="2016-12-1210:55:05";

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<fieldname="date"/>'+
                    '<fieldname="datetime"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                        '<tt-esc="record.date.raw_value"/>'+
                        '<tt-esc="record.datetime.raw_value"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
        });

        //FIXME:thistestislocaledependant.weneedtodoitright.
        assert.strictEqual(kanban.$('div.o_kanban_record:contains(WedJan25)').length,1,
            "shouldhaveformattedthedate");
        assert.strictEqual(kanban.$('div.o_kanban_record:contains(MonDec12)').length,1,
            "shouldhaveformattedthedatetime");
        kanban.destroy();
    });

    QUnit.test('evaluateconditionsonrelationalfields',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].product_id=false;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="category_ids"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                        '<buttont-if="!record.product_id.raw_value"class="btn_a">A</button>'+
                        '<buttont-if="!record.category_ids.raw_value.length"class="btn_b">B</button>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
        });

        assert.strictEqual($('.o_kanban_record:not(.o_kanban_ghost)').length,4,
            "thereshouldbe4records");
        assert.strictEqual($('.o_kanban_record:not(.o_kanban_ghost).btn_a').length,1,
            "only1ofthemshouldhavethe'Action'button");
        assert.strictEqual($('.o_kanban_record:not(.o_kanban_ghost).btn_b').length,2,
            "only2ofthemshouldhavethe'Action'button");

        kanban.destroy();
    });

    QUnit.test('resequencecolumnsingroupedbym2o',asyncfunction(assert){
        assert.expect(6);
        this.data.product.fields.sequence={string:"Sequence",type:"integer"};

        varenvIDs=[1,3,2,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<fieldname="product_id"/>'+
                        '<templates><tt-name="kanban-box">'+
                            '<div><fieldname="foo"/></div>'+
                        '</t></templates>'+
                    '</kanban>',
            groupBy:['product_id'],
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'ui-sortable',
            "columnsshouldbesortable");
        assert.containsN(kanban,'.o_kanban_group',2,
            "shouldhavetwocolumns");
        assert.strictEqual(kanban.$('.o_kanban_group:first').data('id'),3,
            "firstcolumnshouldbeid3beforeresequencing");
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //thereisa100msdelayonthed&dfeature(jquerysortable)for
        //kanbancolumns,makingithardtotest.Soweratherbypassthed&d
        //forthistest,anddirectlycalltheeventhandler
        envIDs=[2,4,1,3];//thecolumnswillbeinverted
        kanban._onResequenceColumn({data:{ids:[5,3]}});
        awaitnextTick(); //waitforresequencingbeforere-rendering
        awaitkanban.update({},{reload:false});//re-renderwithoutreloading

        assert.strictEqual(kanban.$('.o_kanban_group:first').data('id'),5,
            "firstcolumnshouldbeid5afterresequencing");
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        kanban.destroy();
    });

    QUnit.test('properlyevaluatemorecomplexdomains',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="category_ids"/>'+
                    '<templates>'+
                        '<tt-name="kanban-box">'+
                            '<div>'+
                                '<fieldname="foo"/>'+
                                '<buttontype="object"attrs="{\'invisible\':[\'|\',(\'bar\',\'=\',True),(\'category_ids\',\'!=\',[])]}"class="btnbtn-primaryfloat-right"name="channel_join_and_get_info">Join</button>'+
                            '</div>'+
                        '</t>'+
                    '</templates>'+
                '</kanban>',
        });

        assert.containsOnce(kanban,'button.oe_kanban_action_button',
            "onlyonebuttonshouldbevisible");
        kanban.destroy();
    });

    QUnit.test('editthekanbancolorwiththecolorpicker',asyncfunction(assert){
        assert.expect(5);

        varwriteOnColor;

        this.data.category.records[0].color=12;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'category',
            data:this.data,
            arch:'<kanban>'+
                    '<fieldname="color"/>'+
                    '<templates>'+
                        '<tt-name="kanban-box">'+
                            '<divcolor="color">'+
                                '<divclass="o_dropdown_kanbandropdown">'+
                                    '<aclass="dropdown-toggleo-no-caretbtn"data-toggle="dropdown"href="#">'+
                                            '<spanclass="fafa-barsfa-lg"/>'+
                                    '</a>'+
                                    '<ulclass="dropdown-menu"role="menu">'+
                                        '<li>'+
                                            '<ulclass="oe_kanban_colorpicker"/>'+
                                        '</li>'+
                                    '</ul>'+
                                '</div>'+
                                '<fieldname="name"/>'+
                            '</div>'+
                        '</t>'+
                    '</templates>'+
                '</kanban>',
            mockRPC:function(route,args){
                if(args.method==='write'&&'color'inargs.args[1]){
                    writeOnColor=true;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        var$firstRecord=kanban.$('.o_kanban_record:first()');

        assert.containsNone(kanban,'.o_kanban_record.oe_kanban_color_12',
            "norecordshouldhavethecolor12");
        assert.strictEqual($firstRecord.find('.oe_kanban_colorpicker').length,1,
            "thereshouldbeacolorpicker");
        assert.strictEqual($firstRecord.find('.oe_kanban_colorpicker').children().length,12,
            "thecolorpickershouldhave12children(thecolors)");

        //Setacolor
        testUtils.kanban.toggleRecordDropdown($firstRecord);
        awaittestUtils.dom.click($firstRecord.find('.oe_kanban_colorpickera.oe_kanban_color_9'));
        assert.ok(writeOnColor,"shouldwriteonthecolorfield");
        $firstRecord=kanban.$('.o_kanban_record:first()');//Firstrecordisreloadedhere
        assert.ok($firstRecord.is('.oe_kanban_color_9'),
            "thefirstrecordshouldhavethecolor9");

        kanban.destroy();
    });

    QUnit.test('loadmorerecordsincolumn',asyncfunction(assert){
        assert.expect(13);

        varenvIDs=[1,2,4];//theidsthatshouldbeintheenvironmentduringthistest
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                '<templates><tt-name="kanban-box">'+
                    '<div><fieldname="foo"/></div>'+
                '</t></templates>'+
            '</kanban>',
            groupBy:['bar'],
            viewOptions:{
                limit:2,
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(args.limit+'-'+ args.offset);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,2,
            "thereshouldbe2recordsinthecolumn");
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //loadmore
        envIDs=[1,2,3,4];//id3willbeloaded
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:eq(1)').find('.o_kanban_load_more'));

        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,3,
            "thereshouldnowbe3recordsinthecolumn");
        assert.verifySteps(['2-undefined','2-undefined','2-2'],
            "therecordsshouldbecorrectlyfetched");
        assert.deepEqual(kanban.exportState().resIds,envIDs);

        //reload
        awaitkanban.reload();
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,3,
            "thereshouldstillbe3recordsinthecolumnafterreload");
        assert.deepEqual(kanban.exportState().resIds,envIDs);
        assert.verifySteps(['4-undefined','2-undefined']);

        kanban.destroy();
    });

    QUnit.test('loadmorerecordsincolumnwithx2many',asyncfunction(assert){
        assert.expect(10);

        this.data.partner.records[0].category_ids=[7];
        this.data.partner.records[1].category_ids=[];
        this.data.partner.records[2].category_ids=[6];
        this.data.partner.records[3].category_ids=[];

        //record[2]willbeloadedafter

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                '<templates><tt-name="kanban-box">'+
                    '<div>'+
                        '<fieldname="category_ids"/>'+
                        '<fieldname="foo"/>'+
                    '</div>'+
                '</t></templates>'+
            '</kanban>',
            groupBy:['bar'],
            viewOptions:{
                limit:2,
            },
            mockRPC:function(route,args){
                if(args.model==='category'&&args.method==='read'){
                    assert.step(String(args.args[0]));
                }
                if(route==='/web/dataset/search_read'){
                    if(args.limit){
                        assert.strictEqual(args.limit,2,
                            "thelimitshouldbecorrectlyset");
                    }
                    if(args.offset){
                        assert.strictEqual(args.offset,2,
                            "theoffsetshouldbecorrectlysetatloadmore");
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,2,
            "thereshouldbe2recordsinthecolumn");

        assert.verifySteps(['7'],"onlytheappearingcategoryshouldbefetched");

        //loadmore
        awaittestUtils.dom.click(kanban.$('.o_kanban_group:eq(1)').find('.o_kanban_load_more'));

        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,3,
            "thereshouldnowbe3recordsinthecolumn");

        assert.verifySteps(['6'],"theothercategoriesshouldnotbefetched");

        kanban.destroy();
    });

    QUnit.test('updatebuttonsaftercolumncreation',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['product_id'],
        });

        assert.isNotVisible(kanban.$buttons.find('.o-kanban-button-new'),
            "Createbuttonshouldbehidden");

        awaittestUtils.dom.click(kanban.$('.o_column_quick_create'));
        kanban.$('.o_column_quick_createinput').val('newcolumn');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));
        assert.isVisible(kanban.$buttons.find('.o-kanban-button-new'),
            "Createbuttonshouldnowbevisible");
        kanban.destroy();
    });

    QUnit.test('group_by_tooltipoptionwhengroupingonamany2one',asyncfunction(assert){
        assert.expect(12);
        deletethis.data.partner.records[3].product_id;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbandefault_group_by="bar">'+
                    '<fieldname="bar"/>'+
                    '<fieldname="product_id"'+
                        'options=\'{"group_by_tooltip":{"name":"Kikou"}}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                    '<div><fieldname="foo"/></div>'+
                '</t></templates></kanban>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/product/read'){
                    assert.strictEqual(args.args[0].length,2,
                        "readontwogroups");
                    assert.deepEqual(args.args[1],['display_name','name'],
                        "shouldreadonspecifiedfieldsonthegroupbyrelation");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_grouped',
                        "shouldhaveclassname'o_kanban_grouped'");
        assert.containsN(kanban,'.o_kanban_group',2,"shouldhave"+2+"columns");

        //simulateanupdatecomingfromthesearchview,withanothergroupbygiven
        awaitkanban.update({groupBy:['product_id']});
        assert.containsN(kanban,'.o_kanban_group',3,"shouldhave"+3+"columns");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(1).o_kanban_record').length,1,
                        "columnshouldcontain1record(s)");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(2).o_kanban_record').length,2,
                        "columnshouldcontain2record(s)");
        assert.strictEqual(kanban.$('.o_kanban_group:nth-child(3).o_kanban_record').length,1,
                        "columnshouldcontain1record(s)");
        assert.ok(kanban.$('.o_kanban_group:firstspan.o_column_title:contains(Undefined)').length,
            "firstcolumnshouldhaveadefaulttitleforwhennovalueisprovided");
        assert.ok(!kanban.$('.o_kanban_group:first.o_kanban_header_title').data('original-title'),
            "tooltipoffirstcolumnshouldnotdefined,sincegroup_by_tooltiptitleandthemany2onefieldhasnovalue");
        assert.ok(kanban.$('.o_kanban_group:eq(1)span.o_column_title:contains(hello)').length,
            "secondcolumnshouldhaveatitlewithavaluefromthemany2one");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_header_title').data('original-title'),
            "<div>Kikou</br>hello</div>",
            "secondcolumnshouldhaveatooltipwiththegroup_by_tooltiptitleandmany2onefieldvalue");

        kanban.destroy();
    });

    QUnit.test('movearecordthenputitagaininthesamecolumn',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records=[];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                    '<fieldname="product_id"/>'+
                    '<templates><tt-name="kanban-box">'+
                    '<div><fieldname="display_name"/></div>'+
                '</t></templates></kanban>',
            groupBy:['product_id'],
        });

        awaittestUtils.dom.click(kanban.$('.o_column_quick_create'));
        kanban.$('.o_column_quick_createinput').val('column1');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        awaittestUtils.dom.click(kanban.$('.o_column_quick_create'));
        kanban.$('.o_column_quick_createinput').val('column2');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        awaittestUtils.dom.click(kanban.$('.o_kanban_group:eq(1).o_kanban_quick_addi'));
        var$quickCreate=kanban.$('.o_kanban_group:eq(1).o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'newpartner');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record').length,0,
                        "columnshouldcontain0record");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,1,
                        "columnshouldcontain1records");

        var$record=kanban.$('.o_kanban_group:eq(1).o_kanban_record:eq(0)');
        var$group=kanban.$('.o_kanban_group:eq(0)');
        awaittestUtils.dom.dragAndDrop($record,$group);
        awaitnextTick(); //waitforresequencingafterdraganddrop

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record').length,1,
                        "columnshouldcontain1records");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,0,
                        "columnshouldcontain0records");

        $record=kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)');
        $group=kanban.$('.o_kanban_group:eq(1)');

        awaittestUtils.dom.dragAndDrop($record,$group);
        awaitnextTick(); //waitforresequencingafterdraganddrop

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record').length,0,
                        "columnshouldcontain0records");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_record').length,1,
                        "columnshouldcontain1records");
        kanban.destroy();
    });

    QUnit.test('resequencearecordtwice',asyncfunction(assert){
        assert.expect(10);

        this.data.partner.records=[];

        varnbResequence=0;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                    '<fieldname="product_id"/>'+
                    '<templates><tt-name="kanban-box">'+
                    '<div><fieldname="display_name"/></div>'+
                '</t></templates></kanban>',
            groupBy:['product_id'],
            mockRPC:function(route){
                if(route==='/web/dataset/resequence'){
                    nbResequence++;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(kanban.$('.o_column_quick_create'));
        kanban.$('.o_column_quick_createinput').val('column1');
        awaittestUtils.dom.click(kanban.$('.o_column_quick_createbutton.o_kanban_add'));

        awaittestUtils.dom.click(kanban.$('.o_kanban_group:eq(0).o_kanban_quick_addi'));
        var$quickCreate=kanban.$('.o_kanban_group:eq(0).o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'record1');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        awaittestUtils.dom.click(kanban.$('.o_kanban_group:eq(0).o_kanban_quick_addi'));
        $quickCreate=kanban.$('.o_kanban_group:eq(0).o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('input'),'record2');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record').length,2,
                        "columnshouldcontain2records");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)').text(),"record2",
                        "recordsshouldbecorrectlyordered");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(1)').text(),"record1",
                        "recordsshouldbecorrectlyordered");

        var$record1=kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(1)');
        var$record2=kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)');
        awaittestUtils.dom.dragAndDrop($record1,$record2,{position:'top'});

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record').length,2,
                        "columnshouldcontain2records");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)').text(),"record1",
                        "recordsshouldbecorrectlyordered");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(1)').text(),"record2",
                        "recordsshouldbecorrectlyordered");

        awaittestUtils.dom.dragAndDrop($record2,$record1,{position:'top'});

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record').length,2,
                        "columnshouldcontain2records");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)').text(),"record2",
                        "recordsshouldbecorrectlyordered");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(1)').text(),"record1",
                        "recordsshouldbecorrectlyordered");
        assert.strictEqual(nbResequence,2,"shouldhaveresequencedtwice");
        kanban.destroy();
    });

    QUnit.test('basicsupportforwidgets',asyncfunction(assert){
        assert.expect(1);

        varMyWidget=Widget.extend({
            init:function(parent,dataPoint){
                this.data=dataPoint.data;
            },
            start:function(){
                this.$el.text(JSON.stringify(this.data));
            },
        });
        widgetRegistry.add('test',MyWidget);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                    '<div>'+
                    '<tt-esc="record.foo.value"/>'+
                    '<fieldname="foo"blip="1"/>'+
                    '<widgetname="test"/>'+
                    '</div>'+
                '</t></templates></kanban>',
        });

        assert.strictEqual(kanban.$('.o_widget:eq(2)').text(),'{"foo":"gnap","id":3}',
            "widgetshouldhavebeeninstantiated");

        kanban.destroy();
        deletewidgetRegistry.map.test;
    });

    QUnit.test('subwidgetswithon_attach_callbackwhenchangingrecordcolor',asyncfunction(assert){
        assert.expect(3);

        varcounter=0;
        varMyTestWidget=AbstractField.extend({
            on_attach_callback:function(){
                counter++;
            },
        });
        fieldRegistry.add('test_widget',MyTestWidget);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'category',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="color"/>'+
                        '<templates>'+
                            '<tt-name="kanban-box">'+
                                '<divcolor="color">'+
                                    '<divclass="o_dropdown_kanbandropdown">'+
                                        '<aclass="dropdown-toggleo-no-caretbtn"data-toggle="dropdown"href="#">'+
                                            '<spanclass="fafa-barsfa-lg"/>'+
                                        '</a>'+
                                        '<ulclass="dropdown-menu"role="menu">'+
                                            '<li>'+
                                                '<ulclass="oe_kanban_colorpicker"/>'+
                                            '</li>'+
                                        '</ul>'+
                                    '</div>'+
                                '<fieldname="name"widget="test_widget"/>'+
                                '</div>'+
                            '</t>'+
                        '</templates>'+
                    '</kanban>',
        });

        //countershouldbe2asthereare2records
        assert.strictEqual(counter,2,"on_attach_callbackshouldhavebeencalledtwice");

        //setacolortokanbanrecord
        var$firstRecord=kanban.$('.o_kanban_record:first()');
        testUtils.kanban.toggleRecordDropdown($firstRecord);
        awaittestUtils.dom.click($firstRecord.find('.oe_kanban_colorpickera.oe_kanban_color_9'));

        //firstrecordhasreplacedits$elwithanewone
        $firstRecord=kanban.$('.o_kanban_record:first()');
        assert.hasClass($firstRecord,'oe_kanban_color_9');
        assert.strictEqual(counter,3,"on_attach_callbackmethodshouldbecalled3times");

        deletefieldRegistry.map.test_widget;
        kanban.destroy();
    });

    QUnit.test('columnprogressbarsproperlywork',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
        });

        assert.containsN(kanban,'.o_kanban_counter',this.data.product.records.length,
            "kanbancountersshouldhavebeencreated");

        assert.strictEqual(parseInt(kanban.$('.o_kanban_counter_side').last().text()),36,
            "countershoulddisplaythesumofint_fieldvalues");
        kanban.destroy();
    });

    QUnit.test('columnprogressbars:"false"barisclickable',asyncfunction(assert){
        assert.expect(8);

        this.data.partner.records.push({id:5,bar:true,foo:false,product_id:5,state:"ghi"});
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
        });

        assert.containsN(kanban,'.o_kanban_group',2);
        assert.strictEqual(kanban.$('.o_kanban_counter:last.o_kanban_counter_side').text(),"4");
        assert.containsN(kanban,'.o_kanban_counter_progress:last.progress-bar',4);
        assert.containsOnce(kanban,'.o_kanban_counter_progress:last.progress-bar[data-filter="__false"]',
            "shouldhavefalsekanbancolor");
        assert.hasClass(kanban.$('.o_kanban_counter_progress:last.progress-bar[data-filter="__false"]'),'bg-muted-full');

        awaittestUtils.dom.click(kanban.$('.o_kanban_counter_progress:last.progress-bar[data-filter="__false"]'));

        assert.hasClass(kanban.$('.o_kanban_counter_progress:last.progress-bar[data-filter="__false"]'),'progress-bar-animated');
        assert.hasClass(kanban.$('.o_kanban_group:last'),'o_kanban_group_show_muted');
        assert.strictEqual(kanban.$('.o_kanban_counter:last.o_kanban_counter_side').text(),"1");

        kanban.destroy();
    });

    QUnit.test('columnprogressbars:"false"barwithsum_field',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records.push({id:5,bar:true,foo:false,int_field:15,product_id:5,state:"ghi"});
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="foo"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
        });

        assert.containsN(kanban,'.o_kanban_group',2);
        assert.strictEqual(kanban.$('.o_kanban_counter:last.o_kanban_counter_side').text(),"51");

        awaittestUtils.dom.click(kanban.$('.o_kanban_counter_progress:last.progress-bar[data-filter="__false"]'));

        assert.hasClass(kanban.$('.o_kanban_counter_progress:last.progress-bar[data-filter="__false"]'),'progress-bar-animated');
        assert.strictEqual(kanban.$('.o_kanban_counter:last.o_kanban_counter_side').text(),"15");

        kanban.destroy();
    });

    QUnit.test('columnprogressbarsshouldnotcrashinnongroupedviews',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            mockRPC:function(route,args){
                assert.step(route);
                returnthis._super(route,args);
            },
        });

        assert.strictEqual(kanban.$('.o_kanban_record').text(),'namenamenamename',
            "shouldhaverenderer4records");

        assert.verifySteps(['/web/dataset/search_read'],"noreadonprogressbardataisdone");
        kanban.destroy();
    });

    QUnit.test('columnprogressbars:creatinganewcolumnshouldcreateanewprogressbar',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="product_id"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['product_id'],
        });

        varnbProgressBars=kanban.$('.o_kanban_counter').length;

        //Createanewcolumn:thisshouldcreateanemptyprogressbar
        var$columnQuickCreate=kanban.$('.o_column_quick_create');
        awaittestUtils.dom.click($columnQuickCreate.find('.o_quick_create_folded'));
        $columnQuickCreate.find('input').val('test');
        awaittestUtils.dom.click($columnQuickCreate.find('.btn-primary'));

        assert.containsN(kanban,'.o_kanban_counter',nbProgressBars+1,
            "anewcolumnwithanewcolumnprogressbarshouldhavebeencreated");

        kanban.destroy();
    });

    QUnit.test('columnprogressbarsonquickcreateproperlyupdatecounter',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
        });

        varinitialCount=parseInt(kanban.$('.o_kanban_counter_side:first').text());
        awaittestUtils.dom.click(kanban.$('.o_kanban_quick_add:first'));
        awaittestUtils.fields.editInput(kanban.$('.o_kanban_quick_createinput'),'Test');
        awaittestUtils.dom.click(kanban.$('.o_kanban_add'));
        varlastCount=parseInt(kanban.$('.o_kanban_counter_side:first').text());
        awaitnextTick(); //awaitupdate
        awaitnextTick(); //awaitread
        assert.strictEqual(lastCount,initialCount+1,
            "kanbancountersshouldhaveupdatedonquickcreate");

        kanban.destroy();
    });

    QUnit.test('columnprogressbarsareworkingwithloadmore',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            domain:[['bar','=',true]],
            arch:
                '<kanbanlimit="1">'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="id"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
        });

        //wehave1recordshown,load2moreandcheckitworked
        awaittestUtils.dom.click(kanban.$('.o_kanban_group').find('.o_kanban_load_more'));
        awaittestUtils.dom.click(kanban.$('.o_kanban_group').find('.o_kanban_load_more'));
        varshownIDs=_.map(kanban.$('.o_kanban_record'),function(record){
            returnparseInt(record.innerText);
        });
        assert.deepEqual(shownIDs,[1,2,3],"intendedrecordsareloaded");

        kanban.destroy();
    });

    QUnit.test('columnprogressbarsonarchivingrecordsupdatecounter',asyncfunction(assert){
        assert.expect(4);

        //addactivefieldonpartnermodelandmakeallrecordsactive
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="active"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/action_archive'){
                    varpartnerIDS=args.args[0];
                    varrecords=this.data.partner.records;
                    _.each(partnerIDS,function(partnerID){
                        _.find(records,function(record){
                            returnrecord.id===partnerID;
                        }).active=false;
                    });
                    this.data.partner.records[0].active;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_counter_side').text(),"36",
            "countershouldcontainthecorrectvalue");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_counter_progress>.progress-bar:first').data('originalTitle'),"1yop",
            "thecounterprogressbarsshouldbecorrectlydisplayed");

        //archiveallrecordsofthesecondcolumns
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:eq(1)'));
        awaittestUtils.dom.click(kanban.$('.o_column_archive_records:visible'));
        awaittestUtils.dom.click($('.modal-footerbutton:first'));

        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_counter_side').text(),"0",
            "countershouldcontainthecorrectvalue");
        assert.strictEqual(kanban.$('.o_kanban_group:eq(1).o_kanban_counter_progress>.progress-bar:first').data('originalTitle'),"0yop",
            "thecounterprogressbarsshouldhavebeencorrectlyupdated");

        kanban.destroy();
    });

    QUnit.test('kanbanwithprogressbars:correctlyupdateenvwhenarchivingrecords',asyncfunction(assert){
        assert.expect(2);

        //addactivefieldonpartnermodelandmakeallrecordsactive
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="active"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/action_archive'){
                    varpartnerIDS=args.args[0];
                    varrecords=this.data.partner.records
                    _.each(partnerIDS,function(partnerID){
                        _.find(records,function(record){
                            returnrecord.id===partnerID;
                        }).active=false;
                    })
                    this.data.partner.records[0].active;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.deepEqual(kanban.exportState().resIds,[1,2,3,4]);

        //archiveallrecordsofthefirstcolumn
        testUtils.kanban.toggleGroupSettings(kanban.$('.o_kanban_group:first'));
        awaittestUtils.dom.click(kanban.$('.o_column_archive_records:visible'));
        awaittestUtils.dom.click($('.modal-footerbutton:first'));

        assert.deepEqual(kanban.exportState().resIds,[1,2,3]);

        kanban.destroy();
    });

    QUnit.test('RPCswhen(re)loadingkanbanviewprogressbars',asyncfunction(assert){
        assert.expect(9);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        awaitkanban.reload();

        assert.verifySteps([
            //initialload
            'web_read_group',
            'read_progress_bar',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            //reload
            'web_read_group',
            'read_progress_bar',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
        ]);

        kanban.destroy();
    });

    QUnit.test('drag&droprecordsgroupedbym2owithprogressbar',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].product_id=false;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="int_field"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['product_id'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    returnPromise.resolve(true);
                }
                returnthis._super(route,args);
            },
        });

        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_counter_side').text(),"1",
            "countershouldcontainthecorrectvalue");

        awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)'),kanban.$('.o_kanban_group:eq(1)'));
        awaitnextTick(); //waitforupdateresultingfromdraganddrop
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_counter_side').text(),"0",
            "countershouldcontainthecorrectvalue");

        awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_group:eq(1).o_kanban_record:eq(2)'),kanban.$('.o_kanban_group:eq(0)'));
        awaitnextTick(); //waitforupdateresultingfromdraganddrop
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_counter_side').text(),"1",
            "countershouldcontainthecorrectvalue");

        awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_group:eq(0).o_kanban_record:eq(0)'),kanban.$('.o_kanban_group:eq(1)'));
        awaitnextTick(); //waitforupdateresultingfromdraganddrop
        assert.strictEqual(kanban.$('.o_kanban_group:eq(0).o_kanban_counter_side').text(),"0",
            "countershouldcontainthecorrectvalue");

        kanban.destroy();
    });

    QUnit.test('progressbarsubgroupcountrecompute',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanban>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="foo"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['bar'],
        });

        var$secondGroup=kanban.$('.o_kanban_group:eq(1)');
        varinitialCount=parseInt($secondGroup.find('.o_kanban_counter_side').text());
        assert.strictEqual(initialCount,3,
            "InitialcountshouldbeThree");
        awaittestUtils.dom.click($secondGroup.find('.bg-success-full'));
        varlastCount=parseInt($secondGroup.find('.o_kanban_counter_side').text());
        assert.strictEqual(lastCount,1,
            "kanbancountersshouldvaryaccordingtowhatsubgroupisselected");

        kanban.destroy();
    });

    QUnit.test('columnprogressbarsonquickcreatewithquick_create_viewareupdated',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanon_create="quick_create"quick_create_view="some_view_ref">'+
                    '<fieldname="int_field"/>'+
                    '<progressbarfield="foo"colors=\'{"yop":"success","gnap":"warning","blip":"danger"}\'sum_field="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                            '<fieldname="name"/>'+
                        '</div>'+
                    '</t></templates>'+
                '</kanban>',
            archs:{
                'partner,some_view_ref,form':'<form>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            },
            groupBy:['bar'],
        });

        varinitialCount=parseInt(kanban.$('.o_kanban_counter_side:first').text());

        awaittestUtils.kanban.clickCreate(kanban);
        //fillthequickcreateandvalidate
        var$quickCreate=kanban.$('.o_kanban_group:first.o_kanban_quick_create');
        awaittestUtils.fields.editInput($quickCreate.find('.o_field_widget[name=int_field]'),'44');
        awaittestUtils.dom.click($quickCreate.find('button.o_kanban_add'));

        varlastCount=parseInt(kanban.$('.o_kanban_counter_side:first').text());
        assert.strictEqual(lastCount,initialCount+44,
            "kanbancountersshouldhavebeenupdatedonquickcreate");

        kanban.destroy();
    });

    QUnit.test('keepaddingquickcreateinfirstcolumnafterarecordfromthiscolumnwasmoved',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:
                '<kanbanon_create="quick_create">'+
                    '<fieldname="int_field"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                '</kanban>',
            groupBy:['foo'],
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    returnPromise.resolve(true);
                }
                returnthis._super(route,args);
            },
        });

        var$quickCreateGroup;
        var$groups;
        await_quickCreateAndTest();
        awaittestUtils.dom.dragAndDrop($groups.first().find('.o_kanban_record:first'),$groups.eq(1));
        await_quickCreateAndTest();
        kanban.destroy();

        asyncfunction_quickCreateAndTest(){
            awaittestUtils.kanban.clickCreate(kanban);
            $quickCreateGroup=kanban.$('.o_kanban_quick_create').closest('.o_kanban_group');
            $groups=kanban.$('.o_kanban_group');
            assert.strictEqual($quickCreateGroup[0],$groups[0],
                "quickcreateshouldhavebeenaddedinthefirstcolumn");
        }
    });

    QUnit.test('testdisplayingimage(URL,imagefieldnotset)',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                      '<fieldname="id"/>'+
                      '<templates><tt-name="kanban-box"><div>'+
                          '<imgt-att-src="kanban_image(\'partner\',\'image\',record.id.raw_value)"/>'+
                      '</div></t></templates>'+
                  '</kanban>',
        });

        //sincethefieldimageisnotset,kanban_imagewillgenerateanURL
        varimageOnRecord=kanban.$('img[data-src*="/web/image"][data-src*="&id=1"]');
        assert.strictEqual(imageOnRecord.length,1,"partnerwithimagedisplayimagebyurl");

        kanban.destroy();
    });

    QUnit.test('testdisplayingimage(binary&placeholder)',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                      '<fieldname="id"/>'+
                      '<fieldname="image"/>'+
                      '<templates><tt-name="kanban-box"><div>'+
                          '<imgt-att-src="kanban_image(\'partner\',\'image\',record.id.raw_value)"/>'+
                      '</div></t></templates>'+
                  '</kanban>',
            mockRPC:function(route,args){
                if(route==='data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACAA=='){
                    assert.ok("Theview'simageshouldhavebeenfetched.");
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });
        varimages=kanban.el.querySelectorAll('img');
        varplaceholders=[];
        for(var[index,img]ofimages.entries()){
            if(img.dataset.src.indexOf(this.data.partner.records[index].image)===-1){
                //Thenwedisplayaplaceholder
                placeholders.push(img);
            }
        }

        assert.strictEqual(placeholders.length,this.data.partner.records.length-1,
            "partnerwithnoimageshoulddisplaytheplaceholder");

        kanban.destroy();
    });

    QUnit.test('testdisplayingimage(foranotherrecord)',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                      '<fieldname="id"/>'+
                      '<fieldname="image"/>'+
                      '<templates><tt-name="kanban-box"><div>'+
                          '<imgt-att-src="kanban_image(\'partner\',\'image\',1)"/>'+
                      '</div></t></templates>'+
                  '</kanban>',
            mockRPC:function(route,args){
                if(route==='data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACAA=='){
                    assert.ok("Theview'simageshouldhavebeenfetched.");
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //thefieldimageisset,butwerequesttheimageforaspecificid
        //->fortherecordmatchingtheID,thebase64shouldbereturned
        //->foralltheotherrecords,theimageshouldbedisplayedbyurl
        varimageOnRecord=kanban.$('img[data-src*="/web/image"][data-src*="&id=1"]');
        assert.strictEqual(imageOnRecord.length,this.data.partner.records.length-1,
            "displayimagebyurlwhenrequestedforanotherrecord");

        kanban.destroy();
    });

    QUnit.test("testdisplayingimagefromm2ofield(m2ofieldnotset)",asyncfunction(assert){
        assert.expect(2);
        this.data.foo_partner={
            fields:{
                name:{string:"FooName",type:"char"},
                partner_id:{string:"Partner",type:"many2one",relation:"partner"},
            },
            records:[
                {id:1,name:'foo_with_partner_image',partner_id:1},
                {id:2,name:'foo_no_partner'},
            ]
        };

        constkanban=awaitcreateView({
            View:KanbanView,
            model:"foo_partner",
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="name"/>
                            <fieldname="partner_id"/>
                            <imgt-att-src="kanban_image('partner','image',record.partner_id.raw_value)"/>
                        </div>
                    </templates>
                </kanban>`,
        });

        assert.containsOnce(kanban,'img[data-src*="/web/image"][data-src$="&id=1"]',"imageurlshouldcontainidofsetpartner_id");
        assert.containsOnce(kanban,'img[data-src*="/web/image"][data-src$="&id="]',"imageurlshouldcontainanemptyidifpartner_idisnotset");

        kanban.destroy();
    });

    QUnit.test('checkiftheviewdestroysallwidgetsandinstances',asyncfunction(assert){
        assert.expect(2);

        varinstanceNumber=0;
        testUtils.mock.patch(mixins.ParentedMixin,{
            init:function(){
                instanceNumber++;
                returnthis._super.apply(this,arguments);
            },
            destroy:function(){
                if(!this.isDestroyed()){
                    instanceNumber--;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varparams={
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="qux"/>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="category_ids"/>'+
                    '<fieldname="state"/>'+
                    '<fieldname="date"/>'+
                    '<fieldname="datetime"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates>'+
                '</kanban>',
        };

        varkanban=awaitcreateView(params);
        assert.ok(instanceNumber>0);

        kanban.destroy();
        assert.strictEqual(instanceNumber,0);

        testUtils.mock.unpatch(mixins.ParentedMixin);
    });

    QUnit.test('groupedkanbanbecomesungroupedwhenclearingdomainthenclearinggroupby',asyncfunction(assert){
        //inthistest,wesimulatethatclearingthedomainisslow,sothat
        //clearingthegroupbydoesnotcorruptthedatahandledwhile
        //reloadingthekanbanview.
        assert.expect(4);

        varprom=makeTestPromise();

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            domain:[['foo','=','norecord']],
            groupBy:['bar'],
            mockRPC:function(route,args){
                varresult=this._super(route,args);
                if(args.method==='web_read_group'){
                    varisFirstUpdate=_.isEmpty(args.kwargs.domain)&&
                                        args.kwargs.groupby&&
                                        args.kwargs.groupby[0]==='bar';
                    if(isFirstUpdate){
                        returnprom.then(function(){
                            returnresult;
                        });
                    }
                }
                returnresult;
            },
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_grouped',
            "thekanbanviewshouldbegrouped");
        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'o_kanban_ungrouped',
            "thekanbanviewshouldnotbeungrouped");

        kanban.update({domain:[]});//1stupdateonkanbanview
        kanban.update({groupBy:false});//2nupdateonkanbanview
        prom.resolve();//simulateslow1stupdateofkanbanview

        awaitnextTick();
        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'o_kanban_grouped',
            "thekanbanviewshouldnotlongerbegrouped");
        assert.hasClass(kanban.$('.o_kanban_view'),'o_kanban_ungrouped',
            "thekanbanviewshouldhavebecomeungrouped");

        kanban.destroy();
    });

    QUnit.test('quick_createongroupedkanbanwithoutcolumn',asyncfunction(assert){
        assert.expect(1);
        this.data.partner.records=[];
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            //forcegroup_createtofalse,otherwisetheCREATEbuttonincontrolpanelishidden
            arch:'<kanbanclass="o_kanban_test"group_create="0"on_create="quick_create"><templates><tt-name="kanban-box">'+
                    '<div>'+
                    '<fieldname="name"/>'+
                    '</div>'+
                '</t></templates></kanban>',
            groupBy:['product_id'],

            intercepts:{
                switch_view:function(event){
                    assert.ok(true,"switch_viewwascalledinsteadofquick_create");
                },
            },
        });
        awaittestUtils.kanban.clickCreate(kanban);
        kanban.destroy();
    });

    QUnit.test('keyboardnavigationonkanbanbasicrendering',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                '<div>'+
                '<tt-esc="record.foo.value"/>'+
                '<fieldname="foo"/>'+
                '</div>'+
                '</t></templates></kanban>',
        });

        var$fisrtCard=kanban.$('.o_kanban_record:first');
        var$secondCard=kanban.$('.o_kanban_record:eq(1)');

        $fisrtCard.focus();
        assert.strictEqual(document.activeElement,$fisrtCard[0],"thekanbancardsarefocussable");

        $fisrtCard.trigger($.Event('keydown',{which:$.ui.keyCode.RIGHT,keyCode:$.ui.keyCode.RIGHT,}));
        assert.strictEqual(document.activeElement,$secondCard[0],"thesecondcardshouldbefocussed");

        $secondCard.trigger($.Event('keydown',{which:$.ui.keyCode.LEFT,keyCode:$.ui.keyCode.LEFT,}));
        assert.strictEqual(document.activeElement,$fisrtCard[0],"thefirstcardshouldbefocussed");
        kanban.destroy();
    });

    QUnit.test('keyboardnavigationonkanbangroupedrendering',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['bar'],
        });

        var$firstColumnFisrtCard=kanban.$('.o_kanban_record:first');
        var$secondColumnFirstCard=kanban.$('.o_kanban_group:eq(1).o_kanban_record:first');
        var$secondColumnSecondCard=kanban.$('.o_kanban_group:eq(1).o_kanban_record:eq(1)');

        $firstColumnFisrtCard.focus();

        //RIGHTshouldselectthenextcolumn
        $firstColumnFisrtCard.trigger($.Event('keydown',{which:$.ui.keyCode.RIGHT,keyCode:$.ui.keyCode.RIGHT,}));
        assert.strictEqual(document.activeElement,$secondColumnFirstCard[0],"RIGHTshouldselectthefirstcardofthenextcolumn");

        //DOWNshouldmoveuponecard
        $secondColumnFirstCard.trigger($.Event('keydown',{which:$.ui.keyCode.DOWN,keyCode:$.ui.keyCode.DOWN,}));
        assert.strictEqual(document.activeElement,$secondColumnSecondCard[0],"DOWNshouldselectthesecondcardofthecurrentcolumn");

        //LEFTshouldgobacktothefirstcolumn
        $secondColumnSecondCard.trigger($.Event('keydown',{which:$.ui.keyCode.LEFT,keyCode:$.ui.keyCode.LEFT,}));
        assert.strictEqual(document.activeElement,$firstColumnFisrtCard[0],"LEFTshouldselectthefirstcardofthefirstcolumn");

        kanban.destroy();
    });

    QUnit.test('keyboardnavigationonkanbangroupedrenderingwithemptycolumns',asyncfunction(assert){
        assert.expect(2);

        vardata=this.data;
        data.partner.records[1].state="abc";

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<fieldname="bar"/>'+
                        '<templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"/></div>'+
                    '</t></templates></kanban>',
            groupBy:['state'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    //overrideread_grouptoreturnemptygroups,asthisis
                    //thecaseforseveralmodels(e.g.project.taskgrouped
                    //bystage_id)
                    returnthis._super.apply(this,arguments).then(function(result){
                        //add2emptycolumnsinthemiddle
                        result.groups.splice(1,0,{state_count:0,state:'def',
                                           __domain:[["state","=","def"]]});
                        result.groups.splice(1,0,{state_count:0,state:'def',
                                           __domain:[["state","=","def"]]});

                        //add1emptycolumninthebeginningandtheend
                        result.groups.unshift({state_count:0,state:'def',
                                        __domain:[["state","=","def"]]});
                        result.groups.push({state_count:0,state:'def',
                                    __domain:[["state","=","def"]]});
                        returnresult;
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        /**
         *DEFcolumnsareempty
         *
         *   |DEF|ABC |DEF|DEF|GHI |DEF
         *   |-----|------|-----|-----|------|-----
         *   |    |yop |    |    |gnap|
         *   |    |blip|    |    |blip|
         */
        var$yop=kanban.$('.o_kanban_record:first');
        var$gnap=kanban.$('.o_kanban_group:eq(4).o_kanban_record:first');

        $yop.focus();

        //RIGHTshouldselectthenextcolumnthathasacard
        $yop.trigger($.Event('keydown',{which:$.ui.keyCode.RIGHT,
            keyCode:$.ui.keyCode.RIGHT,}));
        assert.strictEqual(document.activeElement,$gnap[0],
            "RIGHTshouldselectthefirstcardofthenextcolumnthathasacard");

        //LEFTshouldgobacktothefirstcolumnthathasacard
        $gnap.trigger($.Event('keydown',{which:$.ui.keyCode.LEFT,
            keyCode:$.ui.keyCode.LEFT,}));
        assert.strictEqual(document.activeElement,$yop[0],
            "LEFTshouldselectthefirstcardofthefirstcolumnthathasacard");

        kanban.destroy();
    });

    QUnit.test('keyboardnavigationonkanbanwhenthefocusisonalinkthat'+
     'hasanactionandthekanbanhasnooe_kanban_global_...class',asyncfunction(assert){
        assert.expect(1);
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                    '<div><atype="edit">Edit</a></div>'+
                '</t></templates></kanban>',
        });

        testUtils.mock.intercept(kanban,'switch_view',function(event){
            assert.deepEqual(event.data,{
                view_type:'form',
                res_id:1,
                mode:'edit',
                model:'partner',
            },'WhenselectingfocusingacardandhittingENTER,thefirstlinkorbuttonisclicked');
        });
        kanban.$('.o_kanban_record').first().focus().trigger($.Event('keydown',{
            keyCode:$.ui.keyCode.ENTER,
            which:$.ui.keyCode.ENTER,
        }));
        awaittestUtils.nextTick();

        kanban.destroy();
    });

    QUnit.test('asynchronousrenderingofafieldwidget(ungrouped)',asyncfunction(assert){
        assert.expect(4);

        varfooFieldProm=makeTestPromise();
        varFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            willStart:function(){
                returnfooFieldProm;
            },
            start:function(){
                this.$el.html('LOADED');
            },
        }));

        varkanbanController;
        testUtils.createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"widget="asyncwidget"/></div>'+
                '</t></templates></kanban>',
        }).then(function(kanban){
            kanbanController=kanban;
        });

        assert.strictEqual($('.o_kanban_record').length,0,"kanbanviewisnotreadyyet");

        fooFieldProm.resolve();
        awaitnextTick();
        assert.strictEqual($('.o_kanban_record').text(),"LOADEDLOADEDLOADEDLOADED");

        //reloadwithadomain
        fooFieldProm=makeTestPromise();
        kanbanController.reload({domain:[['id','=',1]]});
        awaitnextTick();

        assert.strictEqual($('.o_kanban_record').text(),"LOADEDLOADEDLOADEDLOADED");

        fooFieldProm.resolve();
        awaitnextTick();
        assert.strictEqual($('.o_kanban_record').text(),"LOADED");

        kanbanController.destroy();
        deletefieldRegistry.map.asyncWidget;
    });

    QUnit.test('asynchronousrenderingofafieldwidget(grouped)',asyncfunction(assert){
        assert.expect(4);

        varfooFieldProm=makeTestPromise();
        varFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            willStart:function(){
                returnfooFieldProm;
            },
            start:function(){
                this.$el.html('LOADED');
            },
        }));

        varkanbanController;
        testUtils.createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"widget="asyncwidget"/></div>'+
                '</t></templates></kanban>',
            groupBy:['foo'],
        }).then(function(kanban){
            kanbanController=kanban;
        });

        assert.strictEqual($('.o_kanban_record').length,0,"kanbanviewisnotreadyyet");

        fooFieldProm.resolve();
        awaitnextTick();
        assert.strictEqual($('.o_kanban_record').text(),"LOADEDLOADEDLOADEDLOADED");

        //reloadwithadomain
        fooFieldProm=makeTestPromise();
        kanbanController.reload({domain:[['id','=',1]]});
        awaitnextTick();

        assert.strictEqual($('.o_kanban_record').text(),"LOADEDLOADEDLOADEDLOADED");

        fooFieldProm.resolve();
        awaitnextTick();
        assert.strictEqual($('.o_kanban_record').text(),"LOADED");

        kanbanController.destroy();
        deletefieldRegistry.map.asyncWidget;
    });
    QUnit.test('asynchronousrenderingofafieldwidgetwithdisplayattr',asyncfunction(assert){
        assert.expect(3);

        varfooFieldDef=makeTestPromise();
        varFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            willStart:function(){
                returnfooFieldDef;
            },
            start:function(){
                this.$el.html('LOADED');
            },
        }));

        varkanbanController;
        testUtils.createAsyncView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"display="right"widget="asyncwidget"/></div>'+
                '</t></templates></kanban>',
        }).then(function(kanban){
            kanbanController=kanban;
        });

        assert.containsNone(document.body,'.o_kanban_record');

        fooFieldDef.resolve();
        awaitnextTick();
        assert.strictEqual(kanbanController.$('.o_kanban_record').text(),
            "LOADEDLOADEDLOADEDLOADED");
        assert.hasClass(kanbanController.$('.o_kanban_record:first.o_field_char'),'float-right');

        kanbanController.destroy();
        deletefieldRegistry.map.asyncWidget;
    });

    QUnit.test('asynchronousrenderingofawidget',asyncfunction(assert){
        assert.expect(2);

        varwidgetDef=makeTestPromise();
        widgetRegistry.add('asyncwidget',Widget.extend({
            willStart:function(){
                returnwidgetDef;
            },
            start:function(){
                this.$el.html('LOADED');
            },
        }));

        varkanbanController;
        testUtils.createAsyncView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                        '<div><widgetname="asyncwidget"/></div>'+
                '</t></templates></kanban>',
        }).then(function(kanban){
            kanbanController=kanban;
        });

        assert.containsNone(document.body,'.o_kanban_record');

        widgetDef.resolve();
        awaitnextTick();
        assert.strictEqual(kanbanController.$('.o_kanban_record.o_widget').text(),
            "LOADEDLOADEDLOADEDLOADED");

        kanbanController.destroy();
        deletewidgetRegistry.map.asyncWidget;
    });

    QUnit.test('updatekanbanwithasynchronousfieldwidget',asyncfunction(assert){
        assert.expect(3);

        varfooFieldDef=makeTestPromise();
        varFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            willStart:function(){
                returnfooFieldDef;
            },
            start:function(){
                this.$el.html('LOADED');
            },
        }));

        varkanban=awaittestUtils.createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test"><templates><tt-name="kanban-box">'+
                        '<div><fieldname="foo"widget="asyncwidget"/></div>'+
                '</t></templates></kanban>',
            domain:[['id','=','0']],//norecordmatchesthisdomain
        });

        assert.containsNone(kanban,'.o_kanban_record:not(.o_kanban_ghost)');

        kanban.update({domain:[]});//thisrenderingwillbeasync

        assert.containsNone(kanban,'.o_kanban_record:not(.o_kanban_ghost)');

        fooFieldDef.resolve();
        awaitnextTick();

        assert.strictEqual(kanban.$('.o_kanban_record').text(),
            "LOADEDLOADEDLOADEDLOADED");

        kanban.destroy();
        deletewidgetRegistry.map.asyncWidget;
    });

    QUnit.test('setcoverimage',asyncfunction(assert){
        assert.expect(6);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<templates>'+
                        '<tt-name="kanban-box">'+
                            '<div>'+
                                '<fieldname="name"/>'+
                                '<divclass="o_dropdown_kanbandropdown">'+
                                    '<aclass="dropdown-toggleo-no-caretbtn"data-toggle="dropdown"href="#">'+
                                        '<spanclass="fafa-barsfa-lg"/>'+
                                    '</a>'+
                                    '<divclass="dropdown-menu"role="menu">'+
                                        '<atype="set_cover"data-field="displayed_image_id"class="dropdown-item">SetCoverImage</a>'+
                                    '</div>'+
                                '</div>'+
                                '<div>'+
                                    '<fieldname="displayed_image_id"widget="attachment_image"/>'+
                                '</div>'+
                            '</div>'+
                        '</t>'+
                    '</templates>'+
                '</kanban>',
            mockRPC:function(route,args){
                if(args.model==='partner'&&args.method==='write'){
                    assert.step(String(args.args[0][0]));
                    returnthis._super(route,args);
                }
                returnthis._super(route,args);
            },
        });

        var$firstRecord=kanban.$('.o_kanban_record:first');
        testUtils.kanban.toggleRecordDropdown($firstRecord);
        awaittestUtils.dom.click($firstRecord.find('[data-type=set_cover]'));
        assert.containsNone($firstRecord,'img',"Initiallythereisnoimage.");

        awaittestUtils.dom.click($('.modal').find("img[data-id='1']"));
        awaittestUtils.modal.clickButton('Select');
        assert.containsOnce(kanban,'img[data-src*="/web/image/1"]');

        var$secondRecord=kanban.$('.o_kanban_record:nth(1)');
        testUtils.kanban.toggleRecordDropdown($secondRecord);
        awaittestUtils.dom.click($secondRecord.find('[data-type=set_cover]'));
        $('.modal').find("img[data-id='2']").dblclick();
        awaittestUtils.nextTick();
        assert.containsOnce(kanban,'img[data-src*="/web/image/2"]');
        assert.verifySteps(["1","2"],"shouldwritesonbothkanbanrecords");

        kanban.destroy();
    });

    QUnit.test('ungroupedkanbanwithhandlefield',asyncfunction(assert){
        assert.expect(4);

        varenvIDs=[1,2,3,4];//theidsthatshouldbeintheenvironmentduringthistest

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<templates><tt-name="kanban-box">'+
                    '<div>'+
                        '<fieldname="foo"/>'+
                    '</div>'+
                '</t></templates></kanban>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    assert.deepEqual(args.ids,envIDs,
                        "shouldwritethesequenceincorrectorder");
                    returnPromise.resolve(true);
                }
                returnthis._super(route,args);
            },
        });

        assert.hasClass(kanban.$('.o_kanban_view'),'ui-sortable');
        assert.strictEqual(kanban.$('.o_kanban_record:not(.o_kanban_ghost)').text(),
            'yopblipgnapblip');

        var$record=kanban.$('.o_kanban_view.o_kanban_record:first');
        var$to=kanban.$('.o_kanban_view.o_kanban_record:nth-child(4)');
        envIDs=[2,3,4,1];//firstrecordofmovedafterlastone
        awaittestUtils.dom.dragAndDrop($record,$to,{position:"bottom"});

        assert.strictEqual(kanban.$('.o_kanban_record:not(.o_kanban_ghost)').text(),
            'blipgnapblipyop');

        kanban.destroy();
    });

    QUnit.test('ungroupedkanbanwithouthandlefield',asyncfunction(assert){
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban>'+
                    '<templates><tt-name="kanban-box">'+
                    '<div>'+
                        '<fieldname="foo"/>'+
                    '</div>'+
                '</t></templates></kanban>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    assert.ok(false,"shouldnottriggeraresequencing");
                }
                returnthis._super(route,args);
            },
        });

        assert.doesNotHaveClass(kanban.$('.o_kanban_view'),'ui-sortable');
        assert.strictEqual(kanban.$('.o_kanban_record:not(.o_kanban_ghost)').text(),
            'yopblipgnapblip');

        var$draggedRecord=kanban.$('.o_kanban_view.o_kanban_record:first');
        var$to=kanban.$('.o_kanban_view.o_kanban_record:nth-child(4)');
        awaittestUtils.dom.dragAndDrop($draggedRecord,$to,{position:"bottom"});

        assert.strictEqual(kanban.$('.o_kanban_record:not(.o_kanban_ghost)').text(),
            'yopblipgnapblip');

        kanban.destroy();
    });

    QUnit.test('clickonimagefieldinkanbanwithoe_kanban_global_click',asyncfunction(assert){
        assert.expect(2);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                        '<templates><tt-name="kanban-box">'+
                            '<divclass="oe_kanban_global_click">'+
                                '<fieldname="image"widget="image"/>'+
                            '</div>'+
                        '</t></templates>'+
                    '</kanban>',
            mockRPC:function(route){
                if(route.startsWith('data:image')){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                switch_view:function(event){
                    assert.deepEqual(_.pick(event.data,'mode','model','res_id','view_type'),{
                        mode:'readonly',
                        model:'partner',
                        res_id:1,
                        view_type:'form',
                    },"shouldtriggeraneventtoopentheclickedrecordinaformview");
                },
            },
        });

        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);

        awaittestUtils.dom.click(kanban.$('.o_field_image').first());

        kanban.destroy();
    });

    QUnit.test('kanbanviewwithbooleanfield',asyncfunction(assert){
        assert.expect(2);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="bar"/></div>
                        </t>
                    </templates>
                </kanban>`,
        });

        assert.containsN(kanban,'.o_kanban_record:contains(True)',3);
        assert.containsOnce(kanban,'.o_kanban_record:contains(False)');

        kanban.destroy();
    });

    QUnit.test('kanbanviewwithbooleanwidget',asyncfunction(assert){
        assert.expect(1);

        constkanban=awaittestUtils.createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="bar"widget="boolean"/></div>
                        </t>
                    </templates>
                </kanban>
            `,
        });

        assert.containsOnce(kanban.el.querySelector('.o_kanban_record'),
            'div.custom-checkbox.o_field_boolean');
        kanban.destroy();
    });

    QUnit.test('kanbanviewwithmonetaryandcurrencyfieldswithoutwidget',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <fieldname="currency_id"/>
                    <templates><tt-name="kanban-box">
                        <div><fieldname="salary"/></div>
                    </t></templates>
                </kanban>`,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        constkanbanRecords=kanban.el.querySelectorAll('.o_kanban_record:not(.o_kanban_ghost)');
        assert.deepEqual([...kanbanRecords].map(r=>r.innerText),
            ['$1750.00','$1500.00','2000.00€','$2222.00']);

        kanban.destroy();
    });

    QUnit.test("quickcreate:keyboardnavigationtobuttons",asyncfunction(assert){
        assert.expect(2);

        constkanban=awaitcreateView({
            arch:`
                <kanbanon_create="quick_create">
                    <fieldname="bar"/>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="display_name"/>
                        </div>
                    </templates>
                </kanban>`,
            data:this.data,
            groupBy:["bar"],
            model:"partner",
            View:KanbanView,
        });

        //Openquickcreate
        awaittestUtils.kanban.clickCreate(kanban);

        assert.containsOnce(kanban,".o_kanban_group:first.o_kanban_quick_create");

        const$displayName=kanban.$(".o_kanban_quick_create.o_field_widget[name=display_name]");

        //Fillinmandatoryfield
        awaittestUtils.fields.editInput($displayName,"aaa");
        //Tab->goestofirstprimarybutton
        awaittestUtils.dom.triggerEvent($displayName,"keydown",{
            keyCode:$.ui.keyCode.TAB,
            which:$.ui.keyCode.TAB,
        });

        assert.hasClass(document.activeElement,"btnbtn-primaryo_kanban_add");

        kanban.destroy();
    });
});

});
