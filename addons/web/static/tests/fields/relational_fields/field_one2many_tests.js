flectra.define('web.field_one_to_many_tests',function(require){
"usestrict";

varAbstractField=require('web.AbstractField');
varAbstractStorageService=require('web.AbstractStorageService');
constControlPanel=require('web.ControlPanel');
constfieldRegistry=require('web.field_registry');
varFormView=require('web.FormView');
varKanbanRecord=require('web.KanbanRecord');
varListRenderer=require('web.ListRenderer');
varNotificationService=require('web.NotificationService');
varRamStorage=require('web.RamStorage');
varrelationalFields=require('web.relational_fields');
vartestUtils=require('web.test_utils');
varfieldUtils=require('web.field_utils');

constAbstractFieldOwl=require('web.AbstractFieldOwl');
constfieldRegistryOwl=require('web.field_registry_owl');

constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;
const{FieldOne2Many}=relationalFields;

QUnit.module('fields',{},function(){

    QUnit.module('relational_fields',{
        beforeEach:function(){
            this.data={
                partner:{
                    fields:{
                        display_name:{string:"Displayedname",type:"char"},
                        foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
                        bar:{string:"Bar",type:"boolean",default:true},
                        int_field:{string:"int_field",type:"integer",sortable:true},
                        qux:{string:"Qux",type:"float",digits:[16,1]},
                        p:{string:"one2manyfield",type:"one2many",relation:'partner',relation_field:'trululu'},
                        turtles:{string:"one2manyturtlefield",type:"one2many",relation:'turtle',relation_field:'turtle_trululu'},
                        trululu:{string:"Trululu",type:"many2one",relation:'partner'},
                        timmy:{string:"pokemon",type:"many2many",relation:'partner_type'},
                        product_id:{string:"Product",type:"many2one",relation:'product'},
                        color:{
                            type:"selection",
                            selection:[['red',"Red"],['black',"Black"]],
                            default:'red',
                            string:"Color",
                        },
                        date:{string:"SomeDate",type:"date"},
                        datetime:{string:"DatetimeField",type:'datetime'},
                        user_id:{string:"User",type:'many2one',relation:'user'},
                        reference:{
                            string:"ReferenceField",type:'reference',selection:[
                                ["product","Product"],["partner_type","PartnerType"],["partner","Partner"]]
                        },
                    },
                    records:[{
                        id:1,
                        display_name:"firstrecord",
                        bar:true,
                        foo:"yop",
                        int_field:10,
                        qux:0.44,
                        p:[],
                        turtles:[2],
                        timmy:[],
                        trululu:4,
                        user_id:17,
                        reference:'product,37',
                    },{
                        id:2,
                        display_name:"secondrecord",
                        bar:true,
                        foo:"blip",
                        int_field:9,
                        qux:13,
                        p:[],
                        timmy:[],
                        trululu:1,
                        product_id:37,
                        date:"2017-01-25",
                        datetime:"2016-12-1210:55:05",
                        user_id:17,
                    },{
                        id:4,
                        display_name:"aaa",
                        bar:false,
                    }],
                    onchanges:{},
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
                partner_type:{
                    fields:{
                        name:{string:"PartnerType",type:"char"},
                        color:{string:"Colorindex",type:"integer"},
                    },
                    records:[
                        {id:12,display_name:"gold",color:2},
                        {id:14,display_name:"silver",color:5},
                    ]
                },
                turtle:{
                    fields:{
                        display_name:{string:"Displayedname",type:"char"},
                        turtle_foo:{string:"Foo",type:"char"},
                        turtle_bar:{string:"Bar",type:"boolean",default:true},
                        turtle_int:{string:"int",type:"integer",sortable:true},
                        turtle_qux:{string:"Qux",type:"float",digits:[16,1],required:true,default:1.5},
                        turtle_description:{string:"Description",type:"text"},
                        turtle_trululu:{string:"Trululu",type:"many2one",relation:'partner'},
                        turtle_ref:{
                            string:"Reference",type:'reference',selection:[
                                ["product","Product"],["partner","Partner"]]
                        },
                        product_id:{string:"Product",type:"many2one",relation:'product',required:true},
                        partner_ids:{string:"Partner",type:"many2many",relation:'partner'},
                    },
                    records:[{
                        id:1,
                        display_name:"leonardo",
                        turtle_bar:true,
                        turtle_foo:"yop",
                        partner_ids:[],
                    },{
                        id:2,
                        display_name:"donatello",
                        turtle_bar:true,
                        turtle_foo:"blip",
                        turtle_int:9,
                        partner_ids:[2,4],
                    },{
                        id:3,
                        display_name:"raphael",
                        product_id:37,
                        turtle_bar:false,
                        turtle_foo:"kawa",
                        turtle_int:21,
                        turtle_qux:9.8,
                        partner_ids:[],
                        turtle_ref:'product,37',
                    }],
                    onchanges:{},
                },
                user:{
                    fields:{
                        name:{string:"Name",type:"char"},
                        partner_ids:{string:"one2manypartnersfield",type:"one2many",relation:'partner',relation_field:'user_id'},
                    },
                    records:[{
                        id:17,
                        name:"Aline",
                        partner_ids:[1,2],
                    },{
                        id:19,
                        name:"Christine",
                    }]
                },
            };
        }
    },function(){
        QUnit.module('FieldOne2Many');

        QUnit.test('Newrecordwithao2malsowith2newrecords,ordered,andresequenced',asyncfunction(assert){
            assert.expect(2);

            //Neededtohavetwonewrecordsinasinglestroke
            this.data.partner.onchanges={
                foo:function(obj){
                    obj.p=[
                        [5],
                        [0,0,{trululu:false}],
                        [0,0,{trululu:false}],
                    ];
                }
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom"default_order="int_field">'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                viewOptions:{
                    mode:'create',
                },
                mockRPC:function(route,args){
                    assert.step(args.method+''+args.model);
                    returnthis._super(route,args);
                },
            });

            //changetheint_fieldthroughdraganddrop
            //thatway,we'lltriggerthesortingandthename_get
            //ofthelinesof"p"
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(1),
                form.$('tbodytr').first(),
                {position:'top'}
            );

            assert.verifySteps(['onchangepartner']);

            form.destroy();
        });

        QUnit.test('O2MListwithpager,decorationanddefault_order:addandcanceladding',asyncfunction(assert){
            assert.expect(3);

            //Thedecorationonthelistimpliesthatitsconditionwillbeevaluated
            //againstthedataofthefield(actualrecords*displayed*)
            //Ifonedataiswronglyformed,itwillcrash
            //Thistestaddsthencancelsarecordinapaged,ordered,anddecoratedlist
            //Thatimpliesprefetchingofrecordsforsorting
            //andevaluationofthedecorationagainst*visiblerecords*

            this.data.partner.records[0].p=[2,4];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom"limit="1"decoration-muted="foo!=False"default_order="display_name">'+
                    '<fieldname="foo"invisible="1"/>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_field_x2many_list.o_data_row',2,
                'Thereshouldbe2rows');

            var$expectedSelectedRow=form.$('.o_field_x2many_list.o_data_row').eq(1);
            var$actualSelectedRow=form.$('.o_selected_row');
            assert.equal($actualSelectedRow[0],$expectedSelectedRow[0],
                'Theselectedrowshouldbethenewone');

            //CancelCreation
            awaittestUtils.fields.triggerKeydown($actualSelectedRow.find('input'),'escape');
            assert.containsOnce(form,'.o_field_x2many_list.o_data_row',
                'Thereshouldbe1row');

            form.destroy();
        });

        QUnit.test('O2Mwithparentedm2oanddomainonparent.m2o',asyncfunction(assert){
            assert.expect(4);

            /*recordsinano2mcanhaveam2opointingtothemselves
                *inthatcase,adomainevaluationonthatfieldfollowedbyname_search
                *shouldn'tsendvirtual_idstotheserver
                */

            this.data.turtle.fields.parent_id={string:"Parent",type:"many2one",relation:'turtle'};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="parent_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'turtle,false,form':'<form><fieldname="parent_id"domain="[(\'id\',\'in\',parent.turtles)]"/></form>',
                },
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/turtle/name_search'){
                        //Wearegoingtopasstwicehere
                        //Firsttime,wereallyhavenothing
                        //Secondtime,avirtual_idhasbeencreated
                        assert.deepEqual(args.kwargs.args,[['id','in',[]]]);
                    }
                    returnthis._super(route,args);
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list[name=turtles].o_field_x2many_list_row_adda'));

            awaittestUtils.fields.many2one.createAndEdit('parent_id');

            var$modal=$('.modal-content');

            awaittestUtils.dom.click($modal.eq(1).find('.modal-footer.btn-primary').eq(0));
            awaittestUtils.dom.click($modal.eq(0).find('.modal-footer.btn-primary').eq(1));

            assert.containsOnce(form,'.o_data_row',
                'Themainrecordshouldhavethenewrecordinitso2m');

            $modal=$('.modal-content');
            awaittestUtils.dom.click($modal.find('.o_field_many2oneinput'));

            form.destroy();
        });

        QUnit.test('one2manylisteditablewithcellreadonlymodifier',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2];
            this.data.partner.records[1].turtles=[1,2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtles"invisible="1"/>'+
                    '<fieldname="foo"attrs="{&quot;readonly&quot;:[(&quot;turtles&quot;,&quot;!=&quot;,[])]}"/>'+
                    '<fieldname="qux"attrs="{&quot;readonly&quot;:[(&quot;turtles&quot;,&quot;!=&quot;,[])]}"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        assert.deepEqual(args.args[1].p[1][2],{foo:'ff',qux:99},
                            'Therightvaluesshouldbewritten');
                    }
                    returnthis._super(route,args);
                }
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            var$targetInput=$('.o_selected_row.o_input[name=foo]');
            assert.equal($targetInput[0],document.activeElement,
                'Thefirstinputofthelineshouldhavethefocus');

            //Simulatinghittingthe'f'keytwice
            awaittestUtils.fields.editInput($targetInput,'f');
            awaittestUtils.fields.editInput($targetInput,$targetInput.val()+'f');

            assert.equal($targetInput[0],document.activeElement,
                'Thefirstinputofthelineshouldstillhavethefocus');

            //SimulatingaTABkey
            awaittestUtils.fields.triggerKeydown($targetInput,'tab');

            var$secondTarget=$('.o_selected_row.o_input[name=qux]');

            assert.equal($secondTarget[0],document.activeElement,
                'ThesecondinputofthelineshouldhavethefocusaftertheTABpress');


            awaittestUtils.fields.editInput($secondTarget,9);
            awaittestUtils.fields.editInput($secondTarget,$secondTarget.val()+9);

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('one2manybasicproperties',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Partnerpage">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                intercepts:{
                    load_filters:function(event){
                        thrownewError('Shouldnotloadfilters');
                    },
                },
            });


            assert.containsNone(form,'td.o_list_record_selector',
                "embeddedone2manyshouldnothaveaselector");
            assert.ok(!form.$('.o_field_x2many_list_row_add').length,
                "embeddedone2manyshouldnotbeeditable");
            assert.ok(!form.$('td.o_list_record_remove').length,
                "embeddedone2manyrecordsshouldnothavearemoveicon");

            awaittestUtils.form.clickEdit(form);

            assert.ok(form.$('.o_field_x2many_list_row_add').length,
                "embeddedone2manyshouldnowbeeditable");

            assert.hasAttrValue(form.$('.o_field_x2many_list_row_add'),'colspan',"2",
                "shouldhavecolspan2(oneforfieldfoo,oneforbeingbelowremoveicon)");

            assert.ok(form.$('td.o_list_record_remove').length,
                "embeddedone2manyrecordsshouldhavearemoveicon");
            form.destroy();
        });

        QUnit.test('transferringclassattributesinone2manysubfields',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"class="hey"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.containsOnce(form,'td.hey',
                'shouldhaveatdwiththedesiredclass');

            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'td.hey',
                'shouldhaveatdwiththedesiredclass');

            awaittestUtils.dom.click(form.$('td.o_data_cell'));

            assert.containsOnce(form,'input[name="turtle_foo"].hey',
                'shouldhaveaninputwiththedesiredclass');

            form.destroy();
        });

        QUnit.test('one2manywithdateanddatetime',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Partnerpage">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="date"/>'+
                    '<fieldname="datetime"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                session:{
                    getTZOffset:function(){
                        return120;
                    },
                },
            });
            assert.strictEqual(form.$('td:eq(0)').text(),"01/25/2017",
                "shouldhaveformattedthedate");
            assert.strictEqual(form.$('td:eq(1)').text(),"12/12/201612:55:05",
                "shouldhaveformattedthedatetime");
            form.destroy();
        });

        QUnit.test('renderingwithembeddedone2many',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            assert.strictEqual(form.$('th:contains(Foo)').length,1,
                "embeddedone2manyshouldhaveacolumntitledaccordingtofoo");
            assert.strictEqual(form.$('td:contains(blip)').length,1,
                "embeddedone2manyshouldhaveacellwithrelationalvalue");
            form.destroy();
        });

        QUnit.test('usethelimitattributeinarch(infieldo2minlinetreeview)',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[1,2,3];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="2">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.model==='turtle'){
                        assert.deepEqual(args.args[0],[1,2],
                            'shouldonlyloadfirst2records');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.containsN(form,'.o_data_row',2,
                'shoulddisplay2datarows');
            form.destroy();
        });

        QUnit.test('usethelimitattributeinarch(infieldo2mnoninlinetreeview)',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[1,2,3];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles"/>'+
                    '</form>',
                archs:{
                    'turtle,false,list':'<treelimit="2"><fieldname="turtle_foo"/></tree>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(args.model==='turtle'&&args.method==='read'){
                        assert.deepEqual(args.args[0],[1,2],
                            'shouldonlyloadfirst2records');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.containsN(form,'.o_data_row',2,
                'shoulddisplay2datarows');
            form.destroy();
        });

        QUnit.test('one2manywithdefault_orderonviewnotinline',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].turtles=[1,2,3];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Turtles">'+
                    '<fieldname="turtles"/>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'turtle,false,list':'<treedefault_order="turtle_foo">'+
                        '<fieldname="turtle_int"/>'+
                        '<fieldname="turtle_foo"/>'+
                        '</tree>',
                },
                res_id:1,
            });
            assert.strictEqual(form.$('.o_field_one2many.o_list_view.o_data_row').text(),"9blip21kawa0yop",
                "thedefaultordershouldbecorrectlyapplied");
            form.destroy();
        });

        QUnit.test('embeddedone2manywithwidget',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            assert.containsOnce(form,'span.o_row_handle',"shouldhave1handles");
            form.destroy();
        });

        QUnit.test('embeddedone2manywithhandlewidget',asyncfunction(assert){
            assert.expect(10);

            varnbConfirmChange=0;
            testUtils.mock.patch(ListRenderer,{
                confirmChange:function(){
                    nbConfirmChange++;
                    returnthis._super.apply(this,arguments);
                },
            });

            this.data.partner.records[0].turtles=[1,2,3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="turtles">'+
                    '<treedefault_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            testUtils.mock.intercept(form,"field_changed",function(event){
                assert.step(event.data.changes.turtles.data.turtle_int.toString());
            },true);

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"yopblipkawa",
                "shouldhavethe3rowsinthecorrectorder");

            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"yopblipkawa",
                "shouldstillhavethe3rowsinthecorrectorder");
            assert.strictEqual(nbConfirmChange,0,"shouldnothaveconfirmedanychangeyet");

            //Draganddropthesecondlineinfirstposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(1),
                form.$('tbodytr').first(),
                {position:'top'}
            );

            assert.strictEqual(nbConfirmChange,1,"shouldhaveconfirmedchangesonlyonce");
            assert.verifySteps(["0","1"],
                "sequencesvaluesshouldbeincrementalstartingfromthepreviousminimumone");

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"blipyopkawa",
                "shouldhavethe3rowsintheneworder");

            awaittestUtils.form.clickSave(form);

            assert.deepEqual(_.map(this.data.turtle.records,function(turtle){
                return_.pick(turtle,'id','turtle_foo','turtle_int');
            }),[
                    {id:1,turtle_foo:"yop",turtle_int:1},
                    {id:2,turtle_foo:"blip",turtle_int:0},
                    {id:3,turtle_foo:"kawa",turtle_int:21}
                ],"shouldhavesavethechangedsequence");

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"blipyopkawa",
                "shouldstillhavethe3rowsintheneworder");

            testUtils.mock.unpatch(ListRenderer);

            form.destroy();
        });

        QUnit.test('onchangeforembeddedone2manyinaone2manywithasecondpage',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.fields.partner_ids.type='one2many';
            this.data.turtle.records[0].partner_ids=[1];
            //weneedasecondpage,sowesettworecordsandonlydisplayoneperpage
            this.data.partner.records[0].turtles=[1,2];

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[
                        [5],
                        [1,1,{
                            turtle_foo:"hop",
                            partner_ids:[[5],[4,1]],
                        }],
                        [1,2,{
                            turtle_foo:"blip",
                            partner_ids:[[5],[4,2],[4,4]],
                        }],
                    ];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="1">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        varexpectedResultTurtles=[
                            [1,1,{
                                turtle_foo:"hop",
                            }],
                            [1,2,{
                                partner_ids:[[4,2,false],[4,4,false]],
                                turtle_foo:"blip",
                            }],
                        ];
                        assert.deepEqual(args.args[1].turtles,expectedResultTurtles,
                            "therightvaluesshouldbewritten");
                    }
                    returnthis._super.apply(this,arguments);
                }
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_data_cell').eq(1));
            var$cell=form.$('.o_selected_row.o_input[name=turtle_foo]');
            awaittestUtils.fields.editSelect($cell,"hop");
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('onchangeforembeddedone2manyinaone2manyupdatedbyserver',asyncfunction(assert){
            //herewetestthatafteranonchange,theembeddedone2manyfieldhas
            //beenupdatedbyanewlistofidsbytheserverresponse,tothisnew
            //listshouldbecorrectlysentbackatsavetime
            assert.expect(3);

            this.data.turtle.fields.partner_ids.type='one2many';
            this.data.partner.records[0].turtles=[2];
            this.data.turtle.records[1].partner_ids=[2];

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[
                        [5],
                        [1,2,{
                            turtle_foo:"hop",
                            partner_ids:[[5],[4,2],[4,4]],
                        }],
                    ];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        varexpectedResultTurtles=[
                            [1,2,{
                                partner_ids:[[4,2,false],[4,4,false]],
                                turtle_foo:"hop",
                            }],
                        ];
                        assert.deepEqual(args.args[1].turtles,expectedResultTurtles,
                            'Therightvaluesshouldbewritten');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.deepEqual(form.$('.o_data_cell.o_many2many_tags_cell').text().trim(),"secondrecord",
                "thepartner_idsshouldbeasspecifiedatinitialization");

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_data_cell').eq(1));
            var$cell=form.$('.o_selected_row.o_input[name=turtle_foo]');
            awaittestUtils.fields.editSelect($cell,"hop");
            awaittestUtils.form.clickSave(form);

            assert.deepEqual(form.$('.o_data_cell.o_many2many_tags_cell').text().trim().split(/\s+/),
                ["second","record","aaa"],
                'Thepartner_idsshouldhavebeenupdated');

            form.destroy();
        });

        QUnit.test('onchangeforembeddedone2manywithhandlewidget',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[1,2,3];
            varpartnerOnchange=0;
            this.data.partner.onchanges={
                turtles:function(){
                    partnerOnchange++;
                },
            };
            varturtleOnchange=0;
            this.data.turtle.onchanges={
                turtle_int:function(){
                    turtleOnchange++;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="turtles">'+
                    '<treedefault_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            //Draganddropthesecondlineinfirstposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(1),
                form.$('tbodytr').first(),
                {position:'top'}
            );

            assert.strictEqual(turtleOnchange,2,"shouldtriggeroneonchangeperlineupdated");
            assert.strictEqual(partnerOnchange,1,"shouldtriggeronlyoneonchangeontheparent");

            form.destroy();
        });

        QUnit.test('onchangeforembeddedone2manywithhandlewidgetusingsamesequence',asyncfunction(assert){
            assert.expect(4);

            this.data.turtle.records[0].turtle_int=1;
            this.data.turtle.records[1].turtle_int=1;
            this.data.turtle.records[2].turtle_int=1;
            this.data.partner.records[0].turtles=[1,2,3];
            varturtleOnchange=0;
            this.data.turtle.onchanges={
                turtle_int:function(){
                    turtleOnchange++;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="turtles">'+
                    '<treedefault_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].turtles,[[1,2,{"turtle_int":1}],[1,1,{"turtle_int":2}],[1,3,{"turtle_int":3}]],
                            "shouldchangealllinesthathavechanged(thefirstonedoesn'tchangebecauseithasthesamesequence)");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);


            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"yopblipkawa",
                "shouldhavethe3rowsinthecorrectorder");

            //Draganddropthesecondlineinfirstposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(1),
                form.$('tbodytr').first(),
                {position:'top'}
            );

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"blipyopkawa",
                "shouldstillhavethe3rowsinthecorrectorder");
            assert.strictEqual(turtleOnchange,3,"shouldupdatealllines");

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('onchange(withcommand5)forembeddedone2manywithhandlewidget',asyncfunction(assert){
            assert.expect(3);

            varids=[];
            for(vari=10;i<50;i++){
                varid=10+i;
                ids.push(id);
                this.data.turtle.records.push({
                    id:id,
                    turtle_int:0,
                    turtle_foo:"#"+id,
                });
            }
            ids.push(1,2,3);
            this.data.partner.records[0].turtles=ids;
            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[[5]].concat(obj.turtles);
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"default_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));
            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"yopblipkawa",
                "shouldhavethe3rowsinthecorrectorder");

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:firsttd:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:firstinput:first'),'blurp');

            //Draganddropthethirdlineinsecondposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(2),
                form.$('.o_field_one2manytbodytr').eq(1),
                {position:'top'}
            );

            assert.strictEqual(form.$('.o_data_cell').text(),"blurpkawablip","shoulddisplaytorecordin'turtle_int'order");

            awaittestUtils.form.clickSave(form);
            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));

            assert.strictEqual(form.$('.o_data_cell:not(.o_handle_cell)').text(),"blurpkawablip",
                "shoulddisplaytorecordin'turtle_int'order");

            form.destroy();
        });

        QUnit.test('onchangewithmodifiersforembeddedone2manyonthesecondpage',asyncfunction(assert){
            assert.expect(7);

            vardata=this.data;
            varids=[];
            for(vari=10;i<60;i++){
                varid=10+i;
                ids.push(id);
                data.turtle.records.push({
                    id:id,
                    turtle_int:0,
                    turtle_foo:"#"+id,
                });
            }
            ids.push(1,2,3);
            data.partner.records[0].turtles=ids;
            data.partner.onchanges={
                turtles:function(obj){
                    //TODO:makethistestmore'difficult'
                    //Fornow,theserveronlyreturnsUPDATEcommands(noLINKTO)
                    //eventhoughitshoulddoit(forperformancereasons)
                    //varturtles=obj.turtles.splice(0,20);

                    varturtles=[];
                    turtles.unshift([5]);
                    //createUPDATEcommandsforeachrecords(thisistheserver
                    //usualanswerforonchange)
                    for(varkinobj.turtles){
                        varchange=obj.turtles[k];
                        varrecord=_.findWhere(data.turtle.records,{id:change[1]});
                        if(change[0]===1){
                            _.extend(record,change[2]);
                        }
                        turtles.push([1,record.id,record]);
                    }
                    obj.turtles=turtles;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:data,
                arch:'<formstring="Partners">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="turtles">'+
                                    '<treeeditable="bottom"default_order="turtle_int"limit="10">'+
                                        '<fieldname="turtle_int"widget="handle"/>'+
                                        '<fieldname="turtle_foo"/>'+
                                        '<fieldname="turtle_qux"attrs="{\'readonly\':[(\'turtle_foo\',\'=\',False)]}"/>'+
                                   '</tree>'+
                                '</field>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"#20#21#22#23#24#25#26#27#28#29",
                "shoulddisplaytherecordsinorder");

            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:firsttd:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:firstinput:first'),'blurp');

            //thedomainfailifthewidgetdoesnotusetheallreadyloadeddata.
            awaittestUtils.form.clickDiscard(form);

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"blurp#21#22#23#24#25#26#27#28#29",
                "shoulddisplaytherecordsinorderwiththechanges");

            awaittestUtils.dom.click($('.modal.modal-footerbutton:first'));

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"#20#21#22#23#24#25#26#27#28#29",
                "shouldcancelchangesanddisplaytherecordsinorder");

            awaittestUtils.form.clickEdit(form);

            //Draganddropthethirdlineinsecondposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(2),
                form.$('.o_field_one2manytbodytr').eq(1),
                {position:'top'}
            );

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"#20#30#31#32#33#34#35#36#37#38",
                "shoulddisplaytherecordsinorderafterresequence(displayrecordwithturtle_int=0)");

            //Draganddropthethirdlineinsecondposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(2),
                form.$('.o_field_one2manytbodytr').eq(1),
                {position:'top'}
            );

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"#20#39#40#41#42#43#44#45#46#47",
                "shoulddisplaytherecordsinorderafterresequence(displayrecordwithturtle_int=0)");

            awaittestUtils.form.clickDiscard(form);

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"#20#39#40#41#42#43#44#45#46#47",
                "shoulddisplaytherecordsinorderafterresequence");

            awaittestUtils.dom.click($('.modal.modal-footerbutton:first'));

            assert.equal(form.$('.o_field_one2many.o_list_char').text(),"#20#21#22#23#24#25#26#27#28#29",
                "shouldcancelchangesanddisplaytherecordsinorder");

            form.destroy();
        });

        QUnit.test('onchangefollowedbyeditiononthesecondpage',asyncfunction(assert){
            assert.expect(12);

            varids=[];
            for(vari=1;i<85;i++){
                varid=10+i;
                ids.push(id);
                this.data.turtle.records.push({
                    id:id,
                    turtle_int:id/3|0,
                    turtle_foo:"#"+i,
                });
            }
            ids.splice(41,0,1,2,3);
            this.data.partner.records[0].turtles=ids;
            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[[5]].concat(obj.turtles);
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top"default_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));

            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:eq(1)td:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:eq(1)input:first'),'value1');
            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:eq(2)td:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:eq(2)input:first'),'value2');

            assert.containsN(form,'.o_data_row',40,"shoulddisplay40records");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#39))').index(),0,"shoulddisplay'#39'atthefirstline");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_data_row',40,"shoulddisplay39recordsandthecreateline");
            assert.containsOnce(form,'.o_data_row:first.o_field_char',"shoulddisplaythecreatelineinfirstposition");
            assert.strictEqual(form.$('.o_data_row:first.o_field_char').val(),"","shouldanemptyinput");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#39))').index(),1,"shoulddisplay'#39'atthesecondline");

            awaittestUtils.fields.editInput(form.$('.o_data_rowinput:first'),'value3');

            assert.containsOnce(form,'.o_data_row:first.o_field_char',"shoulddisplaythecreatelineinfirstpositionafteronchange");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#39))').index(),1,"shoulddisplay'#39'atthesecondlineafteronchange");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_data_row',40,"shoulddisplay39recordsandthecreateline");
            assert.containsOnce(form,'.o_data_row:first.o_field_char',"shoulddisplaythecreatelineinfirstposition");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(value3))').index(),1,"shoulddisplaythecreatedlineatthesecondposition");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#39))').index(),2,"shoulddisplay'#39'atthethirdline");

            form.destroy();
        });

        QUnit.test('onchangefollowedbyeditiononthesecondpage(part2)',asyncfunction(assert){
            assert.expect(8);

            varids=[];
            for(vari=1;i<85;i++){
                varid=10+i;
                ids.push(id);
                this.data.turtle.records.push({
                    id:id,
                    turtle_int:id/3|0,
                    turtle_foo:"#"+i,
                });
            }
            ids.splice(41,0,1,2,3);
            this.data.partner.records[0].turtles=ids;
            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[[5]].concat(obj.turtles);
                },
            };

            //bottomorder

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"default_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));

            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:eq(1)td:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:eq(1)input:first'),'value1');
            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:eq(2)td:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:eq(2)input:first'),'value2');

            assert.containsN(form,'.o_data_row',40,"shoulddisplay40records");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#77))').index(),39,"shoulddisplay'#77'atthelastline");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_data_row',41,"shoulddisplay41recordsandthecreateline");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#76))').index(),38,"shoulddisplay'#76'atthepenultimateline");
            assert.strictEqual(form.$('.o_data_row:has(.o_field_char)').index(),40,"shoulddisplaythecreatelineatthelastposition");

            awaittestUtils.fields.editInput(form.$('.o_data_rowinput:first'),'value3');
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_data_row',42,"shoulddisplay42recordsandthecreateline");
            assert.strictEqual(form.$('.o_data_row:has(.o_data_cell:contains(#76))').index(),38,"shoulddisplay'#76'atthepenultimateline");
            assert.strictEqual(form.$('.o_data_row:has(.o_field_char)').index(),41,"shoulddisplaythecreatelineatthelastposition");

            form.destroy();
        });

        QUnit.test('onchangereturningacommand6foranx2many',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.onchanges={
                foo:function(obj){
                    obj.turtles=[[6,false,[1,2,3]]];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "thereshouldbeonerecordintherelation");

            //changethevalueoffoototriggertheonchange
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'somevalue');

            assert.containsN(form,'.o_data_row',3,
                "thereshouldbethreerecordsintherelation");

            form.destroy();
        });

        QUnit.test('x2manyfieldsinsidex2manysarefetchedafteranonchange',asyncfunction(assert){
            assert.expect(6);

            this.data.turtle.records[0].partner_ids=[1];
            this.data.partner.onchanges={
                foo:function(obj){
                    obj.turtles=[[5],[4,1],[4,2],[4,3]];
                },
            };

            varcheckRPC=false;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(checkRPC&&args.method==='read'&&args.model==='partner'){
                        assert.deepEqual(args.args[1],['display_name'],
                            "shouldonlyreadthedisplay_nameforthem2mtags");
                        assert.deepEqual(args.args[0],[1],
                            "shouldonlyreadthedisplay_nameoftheunknownrecord");
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "thereshouldbeonerecordintherelation");
            assert.strictEqual(form.$('.o_data_row.o_field_widget[name=partner_ids]').text().replace(/\s/g,''),
                'secondrecordaaa',"many2many_tagsshouldbecorrectlydisplayed");

            //changethevalueoffoototriggertheonchange
            checkRPC=true;//enableflagtocheckreadRPCforthem2mfield
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'somevalue');

            assert.containsN(form,'.o_data_row',3,
                "thereshouldbethreerecordsintherelation");
            assert.strictEqual(form.$('.o_data_row:first.o_field_widget[name=partner_ids]').text().trim(),
                'firstrecord',"many2many_tagsshouldbecorrectlydisplayed");

            form.destroy();
        });

        QUnit.test('referencefieldsinsidex2manysarefetchedafteranonchange',asyncfunction(assert){
            assert.expect(5);

            this.data.turtle.records[1].turtle_ref='product,41';
            this.data.partner.onchanges={
                foo:function(obj){
                    obj.turtles=[[5],[4,1],[4,2],[4,3]];
                },
            };

            varcheckRPC=false;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_ref"class="ref_field"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(checkRPC&&args.method==='name_get'){
                        assert.deepEqual(args.args[0],[37],
                            "shouldonlyfetchthename_getoftheunknownrecord");
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "thereshouldbeonerecordintherelation");
            assert.strictEqual(form.$('.ref_field').text().trim(),'xpad',
                "referencefieldshouldbecorrectlydisplayed");

            //changethevalueoffoototriggertheonchange
            checkRPC=true;//enableflagtocheckreadRPCforreferencefield
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'somevalue');

            assert.containsN(form,'.o_data_row',3,
                "thereshouldbethreerecordsintherelation");
            assert.strictEqual(form.$('.ref_field').text().trim(),'xpadxphone',
                "referencefieldsshouldbecorrectlydisplayed");

            form.destroy();
        });

        QUnit.test('onchangeonone2manycontainingx2manyinformview',asyncfunction(assert){
            assert.expect(16);

            this.data.partner.onchanges={
                foo:function(obj){
                    obj.turtles=[[0,false,{turtle_foo:'newrecord'}]];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="partner_ids">'+
                    '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner,false,list':'<tree><fieldname="foo"/></tree>',
                    'partner,false,search':'<search></search>',
                },
            });


            assert.containsOnce(form,'.o_data_row',
                "theonchangeshouldhavecreatedonerecordintherelation");

            //openthecreatedo2mrecordinaformview,andaddam2msubrecord
            //initsrelation
            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.strictEqual($('.modal').length,1,"shouldhaveopenedadialog");
            assert.strictEqual($('.modal.o_data_row').length,0,
                "thereshouldbenorecordintheone2manyinthedialog");

            //addamany2manysubrecord
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));

            assert.strictEqual($('.modal').length,2,
                "shouldhaveopenedaseconddialog");

            //selectamany2manysubrecord
            awaittestUtils.dom.click($('.modal:nth(1).o_list_view.o_data_cell:first'));

            assert.strictEqual($('.modal').length,1,
                "seconddialogshouldbeclosed");
            assert.strictEqual($('.modal.o_data_row').length,1,
                "thereshouldbeonerecordintheone2manyinthedialog");
            assert.containsNone($('.modal'),'.o_x2m_control_panel.o_pager',
                'm2mpagershouldbehidden');

            //clickon'Save&Close'
            awaittestUtils.dom.click($('.modal-footer.btn-primary:first'));

            assert.strictEqual($('.modal').length,0,"dialogshouldbeclosed");

            //reopeno2mrecord,andanotherm2msubrecordinitsrelation,but
            //discardthechanges
            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.strictEqual($('.modal').length,1,"shouldhaveopenedadialog");
            assert.strictEqual($('.modal.o_data_row').length,1,
                "thereshouldbeonerecordintheone2manyinthedialog");

            //addanotherm2msubrecord
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));

            assert.strictEqual($('.modal').length,2,
                "shouldhaveopenedaseconddialog");

            awaittestUtils.dom.click($('.modal:nth(1).o_list_view.o_data_cell:first'));

            assert.strictEqual($('.modal').length,1,
                "seconddialogshouldbeclosed");
            assert.strictEqual($('.modal.o_data_row').length,2,
                "thereshouldbetworecordsintheone2manyinthedialog");

            //clickon'Discard'
            awaittestUtils.dom.click($('.modal-footer.btn-secondary'));

            assert.strictEqual($('.modal').length,0,"dialogshouldbeclosed");

            //reopeno2mrecordtocheckthatsecondchangeshaveproperlybeendiscarded
            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.strictEqual($('.modal').length,1,"shouldhaveopenedadialog");
            assert.strictEqual($('.modal.o_data_row').length,1,
                "thereshouldbeonerecordintheone2manyinthedialog");

            form.destroy();
        });

        QUnit.test('onchangeonone2manywithx2manyinlist(nowidget)andformview(list)',asyncfunction(assert){
            assert.expect(6);

            this.data.turtle.fields.turtle_foo.default="adefaultvalue";
            this.data.partner.onchanges={
                foo:function(obj){
                  obj.p=[[0,false,{turtles:[[0,false,{turtle_foo:'hello'}]]}]];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="foo"/>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="turtles"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="turtles">'+
                                    '<treeeditable="top">'+
                                        '<fieldname="turtle_foo"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</form>'+
                        '</field>'+
                    '</form>',
            });


            assert.containsOnce(form,'.o_data_row',
                "theonchangeshouldhavecreatedonerecordintherelation");

            //openthecreatedo2mrecordinaformview
            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal',"shouldhaveopenedadialog");
            assert.containsOnce(document.body,'.modal.o_data_row');
            assert.strictEqual($('.modal.o_data_row').text(),'hello');

            //addaone2manysubrecordandcheckifthedefaultvalueiscorrectlyapplied
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));

            assert.containsN(document.body,'.modal.o_data_row',2);
            assert.strictEqual($('.modal.o_data_row:first.o_field_widget[name=turtle_foo]').val(),
                'adefaultvalue');

            form.destroy();
        });

        QUnit.test('onchangeonone2manywithx2manyinlist(many2many_tags)andformview(list)',asyncfunction(assert){
            assert.expect(6);

            this.data.turtle.fields.turtle_foo.default="adefaultvalue";
            this.data.partner.onchanges={
                foo:function(obj){
                  obj.p=[[0,false,{turtles:[[0,false,{turtle_foo:'hello'}]]}]];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="foo"/>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="turtles"widget="many2many_tags"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="turtles">'+
                                    '<treeeditable="top">'+
                                        '<fieldname="turtle_foo"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</form>'+
                        '</field>'+
                    '</form>',
            });


            assert.containsOnce(form,'.o_data_row',
                "theonchangeshouldhavecreatedonerecordintherelation");

            //openthecreatedo2mrecordinaformview
            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal',"shouldhaveopenedadialog");
            assert.containsOnce(document.body,'.modal.o_data_row');
            assert.strictEqual($('.modal.o_data_row').text(),'hello');

            //addaone2manysubrecordandcheckifthedefaultvalueiscorrectlyapplied
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));

            assert.containsN(document.body,'.modal.o_data_row',2);
            assert.strictEqual($('.modal.o_data_row:first.o_field_widget[name=turtle_foo]').val(),
                'adefaultvalue');

            form.destroy();
        });

        QUnit.test('embeddedone2manywithhandlewidgetwithminimumsetValuecalls',asyncfunction(assert){
            vardone=assert.async();
            assert.expect(20);


            this.data.turtle.records[0].turtle_int=6;
            this.data.turtle.records.push({
                id:4,
                turtle_int:20,
                turtle_foo:"a1",
            },{
                    id:5,
                    turtle_int:9,
                    turtle_foo:"a2",
                },{
                    id:6,
                    turtle_int:2,
                    turtle_foo:"a3",
                },{
                    id:7,
                    turtle_int:11,
                    turtle_foo:"a4",
                });
            this.data.partner.records[0].turtles=[1,2,3,4,5,6,7];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="turtles">'+
                    '<treedefault_order="turtle_int">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            testUtils.mock.intercept(form,"field_changed",function(event){
                assert.step(String(form.model.get(event.data.changes.turtles.id).res_id));
            },true);

            awaittestUtils.form.clickEdit(form);

            varpositions=[
                [6,0,'top',['3','6','1','2','5','7','4']],//movethelasttothefirstline
                [5,1,'top',['7','6','1','2','5']],//movethepenultimatetothesecondline
                [2,5,'bottom',['1','2','5','6']],//movethethirdtothepenultimateline
            ];
            asyncfunctiondragAndDrop(){
                varpos=positions.shift();

                awaittestUtils.dom.dragAndDrop(
                    form.$('.ui-sortable-handle').eq(pos[0]),
                    form.$('tbodytr').eq(pos[1]),
                    {position:pos[2]}
                );

                assert.verifySteps(pos[3],
                    "sequencesvaluesshouldbeapplyfromthebeginindextothedropindex");

                if(positions.length){

                    setTimeout(dragAndDrop,10);

                }else{

                    assert.deepEqual(_.pluck(form.model.get(form.handle).data.turtles.data,'data'),[
                        {id:3,turtle_foo:"kawa",turtle_int:2},
                        {id:7,turtle_foo:"a4",turtle_int:3},
                        {id:1,turtle_foo:"yop",turtle_int:4},
                        {id:2,turtle_foo:"blip",turtle_int:5},
                        {id:5,turtle_foo:"a2",turtle_int:6},
                        {id:6,turtle_foo:"a3",turtle_int:7},
                        {id:4,turtle_foo:"a1",turtle_int:8}
                    ],"sequencesmustbeapplycorrectly");

                    form.destroy();
                    done();
                }
            }

            dragAndDrop();
        });

        QUnit.test('embeddedone2many(editablelist)withhandlewidget',asyncfunction(assert){
            assert.expect(8);

            this.data.partner.records[0].p=[1,2,4];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<notebook>'+
                    '<pagestring="Ppage">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            testUtils.mock.intercept(form,"field_changed",function(event){
                assert.step(event.data.changes.p.data.int_field.toString());
            },true);

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"MylittleFooValueblipyop",
                "shouldhavethe3rowsinthecorrectorder");

            awaittestUtils.form.clickEdit(form);
            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"MylittleFooValueblipyop",
                "shouldstillhavethe3rowsinthecorrectorder");

            //Draganddropthesecondlineinfirstposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(1),
                form.$('tbodytr').first(),
                {position:'top'}
            );

            assert.verifySteps(["0","1"],
                "sequencesvaluesshouldbeincrementalstartingfromthepreviousminimumone");

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"blipMylittleFooValueyop",
                "shouldhavethe3rowsintheneworder");

            awaittestUtils.dom.click(form.$('tbodytr:firsttd:first'));

            assert.strictEqual(form.$('tbodytr:firsttd.o_data_cell:not(.o_handle_cell)input').val(),"blip",
                "shouldeditthecorrectrow");

            awaittestUtils.form.clickSave(form);
            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"blipMylittleFooValueyop",
                "shouldstillhavethe3rowsintheneworder");

            form.destroy();
        });

        QUnit.test('one2manyfieldwhenusingthepager',asyncfunction(assert){
            assert.expect(13);

            varids=[];
            for(vari=0;i<45;i++){
                varid=10+i;
                ids.push(id);
                this.data.partner.records.push({
                    id:id,
                    display_name:"relationalrecord"+id,
                });
            }
            this.data.partner.records[0].p=ids.slice(0,42);
            this.data.partner.records[1].p=ids.slice(42);

            varcount=0;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<kanban>'+
                    '<fieldname="display_name"/>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<div><tt-esc="record.display_name"/></div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</form>',
                viewOptions:{
                    ids:[1,2],
                    index:0,
                },
                mockRPC:function(){
                    count++;
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
            });

            //weareonrecord1,whichhas90relatedrecord(first40shouldbe
            //displayed),2RPCs(read)shouldhavebeendone,oneonthemainrecord
            //andonefortheO2M
            assert.strictEqual(count,2,'twoRPCsshouldhavebeendone');
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'one2manykanbanshouldcontain40cardsforrecord1');

            //movetorecord2,whichhas3relatedrecords(andshouldn'tcontainthe
            //relatedrecordsofrecord1anymore).TwoadditionalRPCsshouldhave
            //beendone
            awaitcpHelpers.pagerNext(form);
            assert.strictEqual(count,4,'twoRPCsshouldhavebeendone');
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,3,
                'one2manykanbanshouldcontain3cardsforrecord2');

            //movebacktorecord1,whichshouldcontainagainitsfirst40related
            //records
            awaitcpHelpers.pagerPrevious(form);
            assert.strictEqual(count,6,'twoRPCsshouldhavebeendone');
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'one2manykanbanshouldcontain40cardsforrecord1');

            //movetothesecondpageoftheo2m:1RPCshouldhavebeendonetofetch
            //the2subrecordsofpage2,andthoserecordsshouldnowbedisplayed
            awaittestUtils.dom.click(form.$('.o_x2m_control_panel.o_pager_next'));
            assert.strictEqual(count,7,'oneRPCshouldhavebeendone');
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,2,
                'one2manykanbanshouldcontain2cardsforrecord1atpage2');

            //movetorecord2againandcheckthateverythingiscorrectlyupdated
            awaitcpHelpers.pagerNext(form);
            assert.strictEqual(count,9,'twoRPCsshouldhavebeendone');
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,3,
                'one2manykanbanshouldcontain3cardsforrecord2');

            //movebacktorecord1andmovetopage2again:alldatashouldhave
            //beencorrectlyreloaded
            awaitcpHelpers.pagerPrevious(form);
            assert.strictEqual(count,11,'twoRPCsshouldhavebeendone');
            awaittestUtils.dom.click(form.$('.o_x2m_control_panel.o_pager_next'));
            assert.strictEqual(count,12,'oneRPCshouldhavebeendone');
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,2,
                'one2manykanbanshouldcontain2cardsforrecord1atpage2');
            form.destroy();
        });

        QUnit.test('editionofone2manyfieldwithpager',asyncfunction(assert){
            assert.expect(31);

            varids=[];
            for(vari=0;i<45;i++){
                varid=10+i;
                ids.push(id);
                this.data.partner.records.push({
                    id:id,
                    display_name:"relationalrecord"+id,
                });
            }
            this.data.partner.records[0].p=ids;

            varsaveCount=0;
            varcheckRead=false;
            varreadIDs;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<kanban>'+
                    '<fieldname="display_name"/>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<divclass="oe_kanban_global_click">'+
                    '<at-if="!read_only_mode"type="delete"class="fafa-timesfloat-rightdelete_icon"/>'+
                    '<span><tt-esc="record.display_name.value"/></span>'+
                    '</div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<form><fieldname="display_name"/></form>',
                },
                mockRPC:function(route,args){
                    if(args.method==='read'&&checkRead){
                        readIDs=args.args[0];
                        checkRead=false;
                    }
                    if(args.method==='write'){
                        saveCount++;
                        varnbCommands=args.args[1].p.length;
                        varnbLinkCommands=_.filter(args.args[1].p,function(command){
                            returncommand[0]===4;
                        }).length;
                        switch(saveCount){
                            case1:
                                assert.strictEqual(nbCommands,46,
                                    "shouldsend46commands(oneforeachrecord)");
                                assert.strictEqual(nbLinkCommands,45,
                                    "shouldsendaLINK_TOcommandforeachexistingrecord");
                                assert.deepEqual(args.args[1].p[45],[0,args.args[1].p[45][1],{
                                    display_name:'newrecord',
                                }],"shouldsentaCREATEcommandforthenewrecord");
                                break;
                            case2:
                                assert.strictEqual(nbCommands,46,
                                    "shouldsend46commands");
                                assert.strictEqual(nbLinkCommands,45,
                                    "shouldsendaLINK_TOcommandforeachexistingrecord");
                                assert.deepEqual(args.args[1].p[45],[2,10,false],
                                    "shouldsentaDELETEcommandforthedeletedrecord");
                                break;
                            case3:
                                assert.strictEqual(nbCommands,47,
                                    "shouldsend47commands");
                                assert.strictEqual(nbLinkCommands,43,
                                    "shouldsendaLINK_TOcommandforeachexistingrecord");
                                assert.deepEqual(args.args[1].p[43],
                                    [0,args.args[1].p[43][1],{display_name:'newrecordpage1'}],
                                    "shouldsentcorrectCREATEcommand");
                                assert.deepEqual(args.args[1].p[44],
                                    [0,args.args[1].p[44][1],{display_name:'newrecordpage2'}],
                                    "shouldsentcorrectCREATEcommand");
                                assert.deepEqual(args.args[1].p[45],
                                    [2,11,false],
                                    "shouldsentcorrectDELETEcommand");
                                assert.deepEqual(args.args[1].p[46],
                                    [2,52,false],
                                    "shouldsentcorrectDELETEcommand");
                                break;
                        }
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
            });

            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'thereshouldbe40recordsonpage1');
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '1-40/45',"pagerrangeshouldbecorrect");

            //addarecordonpageone
            checkRead=true;
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            awaittestUtils.fields.editInput($('.modalinput'),'newrecord');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            //checks
            assert.strictEqual(readIDs,undefined,"shouldnothavereadanyrecord");
            assert.strictEqual(form.$('span:contains(newrecord)').length,0,
                "newrecordshouldbeonpage2");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'thereshouldbe40recordsonpage1');
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '1-40/46',"pagerrangeshouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_record:firstspan:contains(newrecord)').length,
                0,'newrecordshouldnotbeonpage1');
            //save
            awaittestUtils.form.clickSave(form);

            //deletearecordonpageone
            checkRead=true;
            awaittestUtils.form.clickEdit(form);
            assert.strictEqual(form.$('.o_kanban_record:firstspan:contains(relationalrecord10)').length,
                1,'firstrecordshouldbetheonewithid10(nextchecksrelyonthat)');
            awaittestUtils.dom.click(form.$('.delete_icon:first'));
            //checks
            assert.deepEqual(readIDs,[50],
                "shouldhavereadarecord(todisplay40recordsonpage1)");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'thereshouldbe40recordsonpage1');
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '1-40/45',"pagerrangeshouldbecorrect");
            //save
            awaittestUtils.form.clickSave(form);

            //addanddeleterecordsinbothpages
            awaittestUtils.form.clickEdit(form);
            checkRead=true;
            readIDs=undefined;
            //addanddeletearecordinpage1
            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            awaittestUtils.fields.editInput($('.modalinput'),'newrecordpage1');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            assert.strictEqual(form.$('.o_kanban_record:firstspan:contains(relationalrecord11)').length,
                1,'firstrecordshouldbetheonewithid11(nextchecksrelyonthat)');
            awaittestUtils.dom.click(form.$('.delete_icon:first'));
            assert.deepEqual(readIDs,[51],
                "shouldhavereadarecord(todisplay40recordsonpage1)");
            //addanddeletearecordinpage2
            awaittestUtils.dom.click(form.$('.o_x2m_control_panel.o_pager_next'));
            assert.strictEqual(form.$('.o_kanban_record:firstspan:contains(relationalrecord52)').length,
                1,'firstrecordshouldbetheonewithid52(nextchecksrelyonthat)');
            checkRead=true;
            readIDs=undefined;
            awaittestUtils.dom.click(form.$('.delete_icon:first'));
            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            awaittestUtils.fields.editInput($('.modalinput'),'newrecordpage2');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            assert.strictEqual(readIDs,undefined,"shouldnothavereadanyrecord");
            //checks
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,5,
                'thereshouldbe5recordsonpage2');
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '41-45/45',"pagerrangeshouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_recordspan:contains(newrecordpage1)').length,
                1,'newrecordsshouldbeonpage2');
            assert.strictEqual(form.$('.o_kanban_recordspan:contains(newrecordpage2)').length,
                1,'newrecordsshouldbeonpage2');
            //save
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('editionofone2manyfield,withonchangeandnotinlinesubview',asyncfunction(assert){
            assert.expect(2);

            this.data.turtle.onchanges.turtle_int=function(obj){
                obj.turtle_foo=String(obj.turtle_int);
            };
            this.data.partner.onchanges.turtles=function(){};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles"/>'+
                    '</form>',
                archs:{
                    'turtle,false,list':'<tree><fieldname="turtle_foo"/></tree>',
                    'turtle,false,form':'<form><group><fieldname="turtle_foo"/><fieldname="turtle_int"/></group></form>',
                },
                mockRPC:function(){
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput($('input[name="turtle_int"]'),'5');
            awaittestUtils.dom.click($('.modal-footerbutton.btn-primary').first());
            assert.strictEqual(form.$('tbodytr:eq(1)td.o_data_cell').text(),'5',
                'shoulddisplay5inthefoofield');
            awaittestUtils.dom.click(form.$('tbodytr:eq(1)td.o_data_cell'));

            awaittestUtils.fields.editInput($('input[name="turtle_int"]'),'3');
            awaittestUtils.dom.click($('.modal-footerbutton.btn-primary').first());
            assert.strictEqual(form.$('tbodytr:eq(1)td.o_data_cell').text(),'3',
                'shouldnowdisplay3inthefoofield');
            form.destroy();
        });

        QUnit.test('sortingone2manyfields',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.fields.foo.sortable=true;
            this.data.partner.records.push({id:23,foo:"abc"});
            this.data.partner.records.push({id:24,foo:"xyz"});
            this.data.partner.records.push({id:25,foo:"def"});
            this.data.partner.records[0].p=[23,24,25];

            varrpcCount=0;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(){
                    rpcCount++;
                    returnthis._super.apply(this,arguments);
                },
            });

            rpcCount=0;
            assert.ok(form.$('tabletbodytr:eq(2)td:contains(def)').length,
                "the3rdrecordistheonewith'def'value");
            form.renderer._render=function(){
                throw"shouldnotrenderthewholeform";
            };

            awaittestUtils.dom.click(form.$('tabletheadth:contains(Foo)'));
            assert.strictEqual(rpcCount,0,
                'sortshouldbeinmemory,noextraRPCsshouldhavebeendone');
            assert.ok(form.$('tabletbodytr:eq(2)td:contains(xyz)').length,
                "the3rdrecordistheonewith'xyz'value");

            awaittestUtils.dom.click(form.$('tabletheadth:contains(Foo)'));
            assert.ok(form.$('tabletbodytr:eq(2)td:contains(abc)').length,
                "the3rdrecordistheonewith'abc'value");

            form.destroy();
        });

        QUnit.test('one2manylistfieldedition',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.records.push({
                id:3,
                display_name:"relationalrecord1",
            });
            this.data.partner.records[1].p=[3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:2,
            });

            //editthefirstlineoftheo2m
            assert.strictEqual(form.$('.o_field_one2manytbodytd').first().text(),'relationalrecord1',
                "displaynameoffirstrecordino2mlistshouldbe'relationalrecord1'");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_one2manytbodytd').first());
            assert.hasClass(form.$('.o_field_one2manytbodytd').first().parent(),'o_selected_row',
                "firstrowofo2mshouldbeinedition");
            awaittestUtils.fields.editInput(form.$('.o_field_one2manytbodytd').first().find('input'),"newvalue");
            assert.hasClass(form.$('.o_field_one2manytbodytd').first().parent(),'o_selected_row',
                "firstrowofo2mshouldstillbeinedition");

            ////leaveo2medition
            awaittestUtils.dom.click(form.$el);
            assert.doesNotHaveClass(form.$('.o_field_one2manytbodytd').first().parent(),'o_selected_row',
                "firstrowofo2mshouldbereadonlyagain");

            //discardchanges
            awaittestUtils.form.clickDiscard(form);
            assert.strictEqual(form.$('.o_field_one2manytbodytd').first().text(),'newvalue',
                "changesshouldn'thavebeendiscardedyet,waitingforuserconfirmation");
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_field_one2manytbodytd').first().text(),'relationalrecord1',
                "displaynameoffirstrecordino2mlistshouldbe'relationalrecord1'");

            //editagainandsave
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_one2manytbodytd').first());
            awaittestUtils.fields.editInput(form.$('.o_field_one2manytbodytd').first().find('input'),"newvalue");
            awaittestUtils.dom.click(form.$el);
            awaittestUtils.form.clickSave(form);
            //FIXME:thisnexttestdoesn'tpassasthesaveofupdatesof
            //relationaldataistemporarilydisabled
            //assert.strictEqual(form.$('.o_field_one2manytbodytd').first().text(),'newvalue',
            //    "displaynameoffirstrecordino2mlistshouldbe'newvalue'");

            form.destroy();
        });

        QUnit.test('one2manylist:createactiondisabled',asyncfunction(assert){
            assert.expect(2);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treecreate="0">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.ok(!form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"linkshouldnotbeavailableinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.ok(!form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"linkshouldnotbeavailableinreadonly');
            form.destroy();
        });

        QUnit.test('one2manylist:conditionalcreate/deleteactions',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2,4];
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p"options="{'create':[('bar','=',True)],'delete':[('bar','=',True)]}">
                            <tree>
                                <fieldname="display_name"/>
                            </tree>
                        </field>
                    </form>`,
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //baristrue->createanddeleteactionareavailable
            assert.containsOnce(form,'.o_field_x2many_list_row_add',
                '"Addanitem"linkshouldbeavailable');
            assert.hasClass(form.$('td.o_list_record_removebutton').first(),'fafa-trash-o',
                "shouldhavetrashbinicons");

            //setbartofalse->createanddeleteactionarenolongeravailable
            awaittestUtils.dom.click(form.$('.o_field_widget[name="bar"]input').first());

            assert.containsNone(form,'.o_field_x2many_list_row_add',
                '"Addanitem"linkshouldnotbeavailableifbarfieldisFalse');
            assert.containsNone(form,'td.o_list_record_removebutton',
                "shouldnothavetrashbiniconsifbarfieldisFalse");

            form.destroy();
        });

        QUnit.test('one2manylist:unlinktworecords',asyncfunction(assert){
            assert.expect(8);
            this.data.partner.records[0].p=[1,2,4];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p"widget="many2many">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        varcommands=args.args[1].p;
                        assert.strictEqual(commands.length,3,
                            'shouldhavegeneratedthreecommands');
                        assert.ok(commands[0][0]===4&&commands[0][1]===2,
                            'shouldhavegeneratedthecommand4(LINK_TO)withid4');
                        assert.ok(commands[1][0]===4&&commands[1][1]===4,
                            'shouldhavegeneratedthecommand4(LINK_TO)withid4');
                        assert.ok(commands[2][0]===3&&commands[2][1]===1,
                            'shouldhavegeneratedthecommand3(UNLINK)withid1');
                    }
                    returnthis._super.apply(this,arguments);
                },
                archs:{
                    'partner,false,form':
                        '<formstring="Partner"><fieldname="display_name"/></form>',
                },
            });
            awaittestUtils.form.clickEdit(form);

            assert.containsN(form,'td.o_list_record_removebutton',3,
                "shouldhave3removebuttons");

            assert.hasClass(form.$('td.o_list_record_removebutton').first(),'fafa-times',
                "shouldhaveXiconstoremove(unlink)records");

            awaittestUtils.dom.click(form.$('td.o_list_record_removebutton').first());

            assert.containsN(form,'td.o_list_record_removebutton',2,
                "shouldhave2removebuttons(arecordissupposedtohavebeenunlinked)");

            awaittestUtils.dom.click(form.$('tr.o_data_row').first());
            assert.containsNone($('.modal.modal-footer.o_btn_remove'),
                'thereshouldnotbeamodalhavingRemoveButton');

            awaittestUtils.dom.click($('.modal.btn-secondary'))
            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manylist:deletingonerecords',asyncfunction(assert){
            assert.expect(7);
            this.data.partner.records[0].p=[1,2,4];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        varcommands=args.args[1].p;
                        assert.strictEqual(commands.length,3,
                            'shouldhavegeneratedthreecommands');
                        assert.ok(commands[0][0]===4&&commands[0][1]===2,
                            'shouldhavegeneratedthecommand4(LINK_TO)withid2');
                        assert.ok(commands[1][0]===4&&commands[1][1]===4,
                            'shouldhavegeneratedthecommand2(LINK_TO)withid1');
                        assert.ok(commands[2][0]===2&&commands[2][1]===1,
                            'shouldhavegeneratedthecommand2(DELETE)withid2');
                    }
                    returnthis._super.apply(this,arguments);
                },
                archs:{
                    'partner,false,form':
                        '<formstring="Partner"><fieldname="display_name"/></form>',
                },
            });
            awaittestUtils.form.clickEdit(form);

            assert.containsN(form,'td.o_list_record_removebutton',3,
                "shouldhave3removebuttons");

            assert.hasClass(form.$('td.o_list_record_removebutton').first(),'fafa-trash-o',
                "shouldhavetrashbiniconstoremove(delete)records");

            awaittestUtils.dom.click(form.$('td.o_list_record_removebutton').first());

            assert.containsN(form,'td.o_list_record_removebutton',2,
                "shouldhave2removebuttons");

            //saveandcheckthatthecorrectcommandhasbeengenerated
            awaittestUtils.form.clickSave(form);

            //FIXME:itwouldbenicetotestthattheviewisre-renderedcorrectly,
            //butastherelationaldataisn'tre-fetched,therenderingisokeven
            //ifthechangeshaven'tbeensaved
            form.destroy();
        });

        QUnit.test('one2manykanban:edition',asyncfunction(assert){
            assert.expect(23);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                        '<fieldname="p">'+
                            '<kanban>'+
                                //colorwillbeinthekanbanbutnotintheform
                                '<fieldname="color"/>'+
                                '<fieldname="display_name"/>'+
                                '<templates>'+
                                    '<tt-name="kanban-box">'+
                                        '<divclass="oe_kanban_global_click">'+
                                            '<at-if="!read_only_mode"type="delete"class="fafa-timesfloat-rightdelete_icon"/>'+
                                            '<span><tt-esc="record.display_name.value"/></span>'+
                                            '<span><tt-esc="record.color.value"/></span>'+
                                        '</div>'+
                                    '</t>'+
                                '</templates>'+
                            '</kanban>'+
                            '<formstring="Partners">'+
                                '<fieldname="display_name"/>'+
                                //foowillbeintheformbutnotinthekanban
                                '<fieldname="foo"/>'+
                            '</form>'+
                        '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        varcommands=args.args[1].p;
                        assert.strictEqual(commands.length,2,
                            'shouldhavegeneratedtwocommands');
                        assert.strictEqual(commands[0][0],0,
                            'generatedcommandshouldbeADDWITHVALUES');
                        assert.strictEqual(commands[0][2].display_name,"newsubrecord3",
                            'valueofnewlycreatedsubrecordshouldbe"newsubrecord3"');
                        assert.strictEqual(commands[1][0],2,
                            'generatedcommandshouldbeREMOVEANDDELETE');
                        assert.strictEqual(commands[1][1],2,
                            'deletedrecordidshouldbe2');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.ok(!form.$('.o_kanban_view.delete_icon').length,
                'deleteiconshouldnotbevisibleinreadonly');
            assert.ok(!form.$('.o_field_one2many.o-kanban-button-new').length,
                '"Create"buttonshouldnotbevisibleinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,1,
                'shouldcontain1record');
            assert.strictEqual(form.$('.o_kanban_recordspan:first').text(),'secondrecord',
                'display_nameofsubrecordshouldbetheoneinDB');
            assert.strictEqual(form.$('.o_kanban_recordspan:nth(1)').text(),'Red',
                'colorofsubrecordshouldbetheoneinDB');
            assert.ok(form.$('.o_kanban_view.delete_icon').length,
                'deleteiconshouldbevisibleinedit');
            assert.ok(form.$('.o_field_one2many.o-kanban-button-new').length,
                '"Create"buttonshouldbevisibleinedit');
            assert.hasClass(form.$('.o_field_one2many.o-kanban-button-new'),'btn-secondary',
                "'Create'buttonshouldhaveclassName'btn-secondary'");
            assert.strictEqual(form.$('.o_field_one2many.o-kanban-button-new').text().trim(),"Add",
                'Createbuttonshouldhave"Add"label');

            //editexistingsubrecord
            awaittestUtils.dom.click(form.$('.oe_kanban_global_click'));

            awaittestUtils.fields.editInput($('.modal.o_form_viewinput').first(),'newname');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_kanban_recordspan:first').text(),'newname',
                'valueofsubrecordshouldhavebeenupdated');

            //createanewsubrecord
            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            awaittestUtils.fields.editInput($('.modal.o_form_viewinput').first(),'newsubrecord1');
            awaittestUtils.dom.clickFirst($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,2,
                'shouldcontain2records');
            assert.strictEqual(form.$('.o_kanban_record:nth(1)span').text(),'newsubrecord1Red',
                'valueofnewlycreatedsubrecordshouldbe"newsubrecord1"');

            //createtwonewsubrecords
            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            awaittestUtils.fields.editInput($('.modal.o_form_viewinput').first(),'newsubrecord2');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:nth(1)'));
            awaittestUtils.fields.editInput($('.modal.o_form_viewinput').first(),'newsubrecord3');
            awaittestUtils.dom.clickFirst($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,4,
                'shouldcontain4records');

            //deletesubrecords
            awaittestUtils.dom.click(form.$('.oe_kanban_global_click').first());
            assert.strictEqual($('.modal.modal-footer.o_btn_remove').length,1,
                'ThereshouldbeamodalhavingRemoveButton');
            awaittestUtils.dom.click($('.modal.modal-footer.o_btn_remove'));
            assert.containsNone($('.o_modal'),"modalshouldhavebeenclosed");
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,3,
                'shouldcontain3records');
            awaittestUtils.dom.click(form.$('.o_kanban_view.delete_icon:first()'));
            awaittestUtils.dom.click(form.$('.o_kanban_view.delete_icon:first()'));
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,1,
                'shouldcontain1records');
            assert.strictEqual(form.$('.o_kanban_recordspan:first').text(),'newsubrecord3',
                'theremainingsubrecordshouldbe"newsubrecord3"');

            //saveandcheckthatthecorrectcommandhasbeengenerated
            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manykanban(editable):properlyhandlecreate_textnodeoption',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles"options="{\'create_text\':\'Addturtle\'}"mode="kanban">'+
                    '<kanban>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<divclass="oe_kanban_details">'+
                    '<fieldname="display_name"/>'+
                    '</div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);
            assert.strictEqual(form.$('.o_field_one2many[name="turtles"].o-kanban-button-new').text().trim(),
                "Addturtle","InO2MKanban,Addbuttonshouldhave'Addturtle'label");

            form.destroy();
        });

        QUnit.test('one2manykanban:createactiondisabled',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].p=[4];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<kanbancreate="0">'+
                    '<fieldname="display_name"/>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<divclass="oe_kanban_global_click">'+
                    '<at-if="!read_only_mode"type="delete"class="fafa-timesfloat-rightdelete_icon"/>'+
                    '<span><tt-esc="record.display_name.value"/></span>'+
                    '</div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.ok(!form.$('.o-kanban-button-new').length,
                '"Add"buttonshouldnotbeavailableinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.ok(!form.$('.o-kanban-button-new').length,
                '"Add"buttonshouldnotbeavailableinedit');
            assert.ok(form.$('.o_kanban_view.delete_icon').length,
                'deleteiconshouldbevisibleinedit');
            form.destroy();
        });

        QUnit.test('one2manykanban:conditionalcreate/deleteactions',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2,4];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p"options="{'create':[('bar','=',True)],'delete':[('bar','=',True)]}">
                            <kanban>
                                <fieldname="display_name"/>
                                <templates>
                                    <tt-name="kanban-box">
                                        <divclass="oe_kanban_global_click">
                                            <span><tt-esc="record.display_name.value"/></span>
                                        </div>
                                    </t>
                                </templates>
                            </kanban>
                            <form>
                                <fieldname="display_name"/>
                                <fieldname="foo"/>
                            </form>
                        </field>
                    </form>`,
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //barisinitiallytrue->createanddeleteactionsareavailable
            assert.containsOnce(form,'.o-kanban-button-new','"Add"buttonshouldbeavailable');

            awaittestUtils.dom.click(form.$('.oe_kanban_global_click').first());

            assert.containsOnce(document.body,'.modal.modal-footer.o_btn_remove',
                'ThereshouldbeaRemoveButtoninsidemodal');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setbarfalse->createanddeleteactionsarenolongeravailable
            awaittestUtils.dom.click(form.$('.o_field_widget[name="bar"]input').first());

            assert.containsNone(form,'.o-kanban-button-new',
                '"Add"buttonshouldnotbeavailableasbarisFalse');

            awaittestUtils.dom.click(form.$('.oe_kanban_global_click').first());

            assert.containsNone(document.body,'.modal.modal-footer.o_btn_remove',
                'ThereshouldnotbeaRemoveButtonasbarfieldisFalse');

            form.destroy();
        });

        QUnit.test('editableone2manylist,pagerisupdated',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.records.push({id:4,turtle_foo:'stephenhawking'});
            this.data.partner.records[0].turtles=[1,2,3,4];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //addarecord,thenclickinformviewtoconfirmit
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$el);

            assert.strictEqual(form.$('.o_field_widget[name=turtles].o_pager').text().trim(),'1-4/5',
                "pagershoulddisplaythecorrecttotal");
            form.destroy();
        });

        QUnit.test('one2manylist(noneditable):edition',asyncfunction(assert){
            assert.expect(12);

            varnbWrite=0;
            this.data.partner.records[0].p=[2,4];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="display_name"/><fieldname="qux"/>'+
                    '</tree>'+
                    '<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        nbWrite++;
                        assert.deepEqual(args.args[1],{
                            p:[[1,2,{display_name:'newname'}],[2,4,false]]
                        },"shouldhavesentthecorrectcommands");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.ok(!form.$('.o_list_record_remove').length,
                'removeiconshouldnotbevisibleinreadonly');
            assert.ok(!form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"shouldnotbevisibleinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2records');
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'secondrecord',
                'display_nameoffirstsubrecordshouldbetheoneinDB');
            assert.ok(form.$('.o_list_record_remove').length,
                'removeiconshouldbevisibleinedit');
            assert.ok(form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"shouldnotvisibleinedit');

            //editexistingsubrecord
            awaittestUtils.dom.click(form.$('.o_list_viewtbodytr:first()td:eq(1)'));

            awaittestUtils.fields.editInput($('.modal.o_form_viewinput'),'newname');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'newname',
                'valueofsubrecordshouldhavebeenupdated');
            assert.strictEqual(nbWrite,0,"shouldnothavewriteanythinginDB");

            //createnewsubrecords
            //TODOwhen'Addanitem'willbeimplemented

            //removesubrecords
            awaittestUtils.dom.click(form.$('.o_list_record_remove:nth(1)'));
            assert.containsOnce(form,'.o_list_viewtd.o_list_number',
                'shouldcontain1subrecord');
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'newname',
                'theremainingsubrecordshouldbe"newname"');

            awaittestUtils.form.clickSave(form);//savetherecord
            assert.strictEqual(nbWrite,1,"shouldhavewritethechangesinDB");

            form.destroy();
        });

        QUnit.test('one2manylist(editable):edition',asyncfunction(assert){
            assert.expect(7);

            this.data.partner.records[0].p=[2,4];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="display_name"/><fieldname="qux"/>'+
                    '</tree>'+
                    '<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.ok(!form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"linkshouldnotbeavailableinreadonly');

            awaittestUtils.dom.click(form.$('.o_list_viewtbodytd:first()'));
            assert.ok($('.modal.o_form_readonly').length,
                'inreadonly,clickingonasubrecordshouldopenitinreadonlyinadialog');
            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

            awaittestUtils.form.clickEdit(form);

            assert.ok(form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"linkshouldbeavailableinedit');

            //editexistingsubrecord
            awaittestUtils.dom.click(form.$('.o_list_viewtbodytd:first()'));
            assert.strictEqual($('.modal').length,0,
                'inedit,clickingonasubrecordshouldnotopenadialog');
            assert.hasClass(form.$('.o_list_viewtbodytr:first()'),'o_selected_row',
                'firstrowshouldbeinedition');
            awaittestUtils.fields.editInput(form.$('.o_list_viewinput:first()'),'newname');

            awaittestUtils.dom.click(form.$('.o_list_viewtbodytr:nth(1)td:first'));
            assert.doesNotHaveClass(form.$('.o_list_viewtbodytr:first'),'o_selected_row',
                'firstrowshouldnotbeineditionanymore');
            assert.strictEqual(form.$('.o_list_viewtbodytd:first').text(),'newname',
                'valueofsubrecordshouldhavebeenupdated');

            //createnewsubrecords
            //TODOwhen'Addanitem'willbeimplemented
            form.destroy();
        });

        QUnit.test('one2manylist(editable):edition,part2',asyncfunction(assert){
            assert.expect(8);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.strictEqual(args.args[1].p[0][0],0,
                            "shouldsenda0commandforfieldp");
                        assert.strictEqual(args.args[1].p[1][0],0,
                            "shouldsendasecond0commandforfieldp");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            //editmode,thenclickonAddanitemandenteravalue
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_selected_row>tdinput'),'kartoffel');

            //clickagainonAddanitem
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.strictEqual(form.$('td:contains(kartoffel)').length,1,
                "shouldhaveonetdwiththenewvalue");
            assert.containsOnce(form,'.o_selected_row>tdinput',
                "shouldhaveoneothernewtd");
            assert.containsN(form,'tr.o_data_row',2,"shouldhave2datarows");

            //enteranothervalueandsave
            awaittestUtils.fields.editInput(form.$('.o_selected_row>tdinput'),'gemuse');
            awaittestUtils.form.clickSave(form);
            assert.containsN(form,'tr.o_data_row',2,"shouldhave2datarows");
            assert.strictEqual(form.$('td:contains(kartoffel)').length,1,
                "shouldhaveonetdwiththenewvalue");
            assert.strictEqual(form.$('td:contains(gemuse)').length,1,
                "shouldhaveonetdwiththenewvalue");

            form.destroy();
        });

        QUnit.test('one2manylist(editable):edition,part3',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
            });

            //editmode,thenclickonAddanitem2times
            assert.containsOnce(form,'tr.o_data_row',
                "shouldhave1datarows");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsN(form,'tr.o_data_row',3,
                "shouldhave3datarows");

            //canceltheedition
            awaittestUtils.form.clickDiscard(form);
            awaittestUtils.dom.click($('.modal-footerbutton.btn-primary').first());
            assert.containsOnce(form,'tr.o_data_row',
                "shouldhave1datarows");

            form.destroy();
        });

        QUnit.test('one2manylist(editable):edition,part4',asyncfunction(assert){
            assert.expect(3);
            vari=0;

            this.data.turtle.onchanges={
                turtle_trululu:function(obj){
                    if(i){
                        obj.turtle_description="SomeDescription";
                    }
                    i++;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_trululu"/>'+
                    '<fieldname="turtle_description"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:2,
            });

            //editmode,thenclickonAddanitem
            assert.containsNone(form,'tr.o_data_row',
                "shouldhave0datarows");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.strictEqual(form.$('textarea').val(),"",
                "fieldturtle_descriptionshouldbeempty");

            //addavalueintheturtle_trululufieldtotriggeranonchange
            awaittestUtils.fields.many2one.clickOpenDropdown('turtle_trululu');
            awaittestUtils.fields.many2one.clickHighlightedItem('turtle_trululu');
            assert.strictEqual(form.$('textarea').val(),"SomeDescription",
                "fieldturtle_descriptionshouldbesettotheresultoftheonchange");
            form.destroy();
        });

        QUnit.test('one2manylist(editable):discardingrequiredemptydata',asyncfunction(assert){
            assert.expect(7);

            this.data.turtle.fields.turtle_foo.required=true;
            deletethis.data.turtle.fields.turtle_foo.default;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    if(args.method){
                        assert.step(args.method);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            //editmode,thenclickonAddanitem,thenclickelsewhere
            assert.containsNone(form,'tr.o_data_row',
                "shouldhave0datarows");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('label.o_form_label').first());
            assert.containsNone(form,'tr.o_data_row',
                "shouldstillhave0datarows");

            //clickonAddanitemagain,thenclickonsave
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.form.clickSave(form);
            assert.containsNone(form,'tr.o_data_row',
                "shouldstillhave0datarows");

            assert.verifySteps(['read','onchange','onchange']);
            form.destroy();
        });

        QUnit.test('editableone2manylist,addinglinewhenonlyonepage',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].turtles=[1,2,3];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //addarecord,toreachthepagesizelimit
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            //therecordcurrentlybeingaddedshouldnotcountinthepager
            assert.containsNone(form,'.o_field_widget[name=turtles].o_pager');

            //unselecttherow
            awaittestUtils.dom.click(form.$el);
            assert.containsNone(form,'.o_selected_row');
            assert.containsNone(form,'.o_field_widget[name=turtles].o_pager');

            awaittestUtils.form.clickSave(form);
            assert.containsOnce(form,'.o_field_widget[name=turtles].o_pager');
            assert.strictEqual(form.$('.o_field_widget[name=turtles].o_pager').text(),"1-3/4");

            form.destroy();
        });

        QUnit.test('editableone2manylist,addingline,thendiscarding',asyncfunction(assert){
            assert.expect(2);

            this.data.turtle.records.push({id:4,turtle_foo:'stephenhawking'});
            this.data.partner.records[0].turtles=[1,2,3,4];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //addarecord,thendiscard
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.form.clickDiscard(form);

            //confirmthediscardoperation
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

            assert.isVisible(form.$('.o_field_widget[name=turtles].o_pager'));
            assert.strictEqual(form.$('.o_field_widget[name=turtles].o_pager').text().trim(),'1-3/4',
                "pagershoulddisplaycorrectvalues");

            form.destroy();
        });

        QUnit.test('editableone2manylist,requiredfieldandpager',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.records.push({id:4,turtle_foo:'stephenhawking'});
            this.data.turtle.fields.turtle_foo.required=true;
            this.data.partner.records[0].turtles=[1,2,3,4];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //adda(empty)record
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            //goonnextpage.Thenewrecordisnotvalidandshouldbediscarded
            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));
            assert.containsOnce(form,'tr.o_data_row');

            form.destroy();
        });

        QUnit.test('editableone2manylist,requiredfield,pagerandconfirmdiscard',asyncfunction(assert){
            assert.expect(3);

            this.data.turtle.records.push({id:4,turtle_foo:'stephenhawking'});
            this.data.turtle.fields.turtle_foo.required=true;
            this.data.partner.records[0].turtles=[1,2,3,4];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //addarecordwithadirtystate,butnotvalid
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('input[name="turtle_int"]'),4321);

            //gotonextpage.Thenewrecordisnotvalid,butdirty.weshould
            //seeaconfirmdialog
            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));

            assert.strictEqual(form.$('.o_field_widget[name=turtles].o_pager').text().trim(),'1-4/5',
                "pagershouldstilldisplaythecorrecttotal");

            //clickoncancel
            awaittestUtils.dom.click($('.modal.modal-footer.btn-secondary'));

            assert.strictEqual(form.$('.o_field_widget[name=turtles].o_pager').text().trim(),'1-4/5',
                "pagershouldagaindisplaythecorrecttotal");
            assert.containsOnce(form,'.o_field_one2manyinput.o_field_invalid',
                "thereshouldbeaninvalidinputintheone2many");
            form.destroy();
        });

        QUnit.test('editableone2manylist,adding,discarding,andpager',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].turtles=[1];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //add4records(tohavemorerecordsthanthelimit)
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'tr.o_data_row',5);
            assert.containsNone(form,'.o_field_widget[name=turtles].o_pager');

            //discard
            awaittestUtils.form.clickDiscard(form);
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

            assert.containsOnce(form,'tr.o_data_row');
            assert.containsNone(form,'.o_field_widget[name=turtles].o_pager');

            form.destroy();
        });

        QUnit.test('unselectingalinewithmissingrequireddata',asyncfunction(assert){
            assert.expect(5);

            this.data.turtle.fields.turtle_foo.required=true;
            deletethis.data.turtle.fields.turtle_foo.default;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:2,
            });

            //editmode,thenclickonAddanitem,thenclickelsewhere
            assert.containsNone(form,'tr.o_data_row',
                "shouldhave0datarows");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsOnce(form,'tr.o_data_row',
                "shouldhave1datarows");

            //addingavalueinthenonrequiredfield,soitisdirty,butwith
            //amissingrequiredfield
            awaittestUtils.fields.editInput(form.$('input[name="turtle_int"]'),'12345');

            //clickelsewhere,
            awaittestUtils.dom.click(form.$('label.o_form_label'));
            assert.strictEqual($('.modal').length,1,
                'aconfirmationmodelshouldbeopened');

            //clickoncancel,thelineshouldstillbeselected
            awaittestUtils.dom.click($('.modal.modal-footerbutton.btn-secondary'));
            assert.containsOnce(form,'tr.o_data_row.o_selected_row',
                "shouldstillhave1selecteddatarow");

            //clickelsewhere,andclickonok(ontheconfirmationdialog)
            awaittestUtils.dom.click(form.$('label.o_form_label'));
            awaittestUtils.dom.click($('.modal.modal-footerbutton.btn-primary'));
            assert.containsNone(form,'tr.o_data_row',
                "shouldhave0datarows(invalidlinehasbeendiscarded");

            form.destroy();
        });

        QUnit.test('pressingenterinao2mwitharequiredemptyfield',asyncfunction(assert){
            assert.expect(4);

            this.data.turtle.fields.turtle_foo.required=true;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            //editmode,thenclickonAddanitem,thenpressenter
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.triggerKeydown(form.$('input[name="turtle_foo"]'),'enter');
            assert.hasClass(form.$('input[name="turtle_foo"]'),'o_field_invalid',
                "inputshouldbemarkedinvalid");
            assert.verifySteps(['read','onchange']);
            form.destroy();
        });

        QUnit.test('editingao2m,withrequiredfieldandonchange',asyncfunction(assert){
            assert.expect(11);

            this.data.turtle.fields.turtle_foo.required=true;
            deletethis.data.turtle.fields.turtle_foo.default;
            this.data.turtle.onchanges={
                turtle_foo:function(obj){
                    obj.turtle_int=obj.turtle_foo.length;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    if(args.method){
                        assert.step(args.method);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            //editmode,thenclickonAddanitem
            assert.containsNone(form,'tr.o_data_row',
                "shouldhave0datarows");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            //inputsometextinrequiredturtle_foofield
            awaittestUtils.fields.editInput(form.$('input[name="turtle_foo"]'),'aubergine');
            assert.strictEqual(form.$('input[name="turtle_int"]').val(),"9",
                "onchangeshouldhavebeentriggered");

            //saveandcheckeverythingisfine
            awaittestUtils.form.clickSave(form);
            assert.strictEqual(form.$('.o_data_rowtd:contains(aubergine)').length,1,
                "shouldhaveonerowwithturtle_foovalue");
            assert.strictEqual(form.$('.o_data_rowtd:contains(9)').length,1,
                "shouldhaveonerowwithturtle_intvalue");

            assert.verifySteps(['read','onchange','onchange','write','read','read']);
            form.destroy();
        });

        QUnit.test('editableo2m,pressingESCdiscardcurrentchanges',asyncfunction(assert){
            assert.expect(5);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsOnce(form,'tr.o_data_row',
                "thereshouldbeonedatarow");

            awaittestUtils.fields.triggerKeydown(form.$('input[name="turtle_foo"]'),'escape');
            assert.containsNone(form,'tr.o_data_row',
                "datarowshouldhavebeendiscarded");
            assert.verifySteps(['read','onchange']);
            form.destroy();
        });

        QUnit.test('editableo2mwithrequiredfield,pressingESCdiscardcurrentchanges',asyncfunction(assert){
            assert.expect(5);

            this.data.turtle.fields.turtle_foo.required=true;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsOnce(form,'tr.o_data_row',
                "thereshouldbeonedatarow");

            awaittestUtils.fields.triggerKeydown(form.$('input[name="turtle_foo"]'),'escape');
            assert.containsNone(form,'tr.o_data_row',
                "datarowshouldhavebeendiscarded");
            assert.verifySteps(['read','onchange']);
            form.destroy();
        });

        QUnit.test('pressingescapeineditableo2mlistindialog',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    "partner,false,form":'<form>'+
                        '<fieldname="p">'+
                        '<treeeditable="bottom">'+
                        '<fieldname="display_name"/>'+
                        '</tree>'+
                        '</field>'+
                        '</form>',
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));

            assert.strictEqual($('.modal.o_data_row.o_selected_row').length,1,
                "thereshouldbearowineditioninthedialog");

            awaittestUtils.fields.triggerKeydown($('.modal.o_data_cellinput'),'escape');

            assert.strictEqual($('.modal').length,1,
                "dialogshouldstillbeopen");
            assert.strictEqual($('.modal.o_data_row').length,0,
                "therowshouldhavebeenremoved");

            form.destroy();
        });

        QUnit.test('editableo2mwithonchangeandrequiredfield:deleteaninvalidline',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.onchanges={
                turtles:function(){},
            };
            this.data.partner.records[0].turtles=[1];
            this.data.turtle.records[0].product_id=37;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.dom.click(form.$('.o_data_cell:first'));
            form.$('.o_field_widget[name="product_id"]input').val('').trigger('keyup');
            assert.verifySteps(['read','read'],'noonchangeshouldbedoneaslineisinvalid');
            awaittestUtils.dom.click(form.$('.o_list_record_remove'));
            assert.verifySteps(['onchange'],'onchangeshouldhavebeendone');

            form.destroy();
        });

        QUnit.test('onchangeinaone2many',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records.push({
                id:3,
                foo:"relationalrecord1",
            });
            this.data.partner.records[1].p=[3];
            this.data.partner.onchanges={p:true};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({
                            value:{
                                p:[
                                    [5],                            //deleteall
                                    [0,0,{foo:"fromonchange"}], //createnew
                                ]
                            }
                        });
                    }
                    returnthis._super(route,args);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_one2manytbodytd').first());
            awaittestUtils.fields.editInput(form.$('.o_field_one2manytbodytd').first().find('input'),"newvalue");
            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('.o_field_one2manytbodytd').first().text(),'fromonchange',
                "displaynameoffirstrecordino2mlistshouldbe'newvalue'");
            form.destroy();
        });

        QUnit.test('one2many,default_getandonchange(basic)',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.p.default=[
                [6,0,[]],                 //replacewithzeroids
            ];
            this.data.partner.onchanges={p:true};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({
                            value:{
                                p:[
                                    [5],                            //deleteall
                                    [0,0,{foo:"fromonchange"}], //createnew
                                ]
                            }
                        });
                    }
                    returnthis._super(route,args);
                },
            });

            assert.ok(form.$('td:contains(fromonchange)').length,
                "shouldhave'fromonchange'valueinone2many");
            form.destroy();
        });

        QUnit.test('one2manyanddefault_get(withdate)',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.p.default=[
                [0,false,{date:'2017-10-08',p:[]}],
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="date"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            assert.strictEqual(form.$('.o_data_cell').text(),'10/08/2017',
                "shouldcorrectlydisplaythedate");

            form.destroy();
        });

        QUnit.test('one2manyandonchange(withinteger)',asyncfunction(assert){
            assert.expect(4);

            this.data.turtle.onchanges={
                turtle_int:function(){}
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('td:contains(9)'));
            awaittestUtils.fields.editInput(form.$('tdinput[name="turtle_int"]'),"3");

            //the'change'eventistriggeredontheinputwhenwefocussomewhere
            //else,forexamplebyclickinginthebody. However,ifwetryto
            //programmaticallyclickinthebody,itdoesnottriggerachange
            //event,sowesimplytriggeritdirectlyinstead.
            form.$('tdinput[name="turtle_int"]').trigger('change');

            assert.verifySteps(['read','read','onchange']);
            form.destroy();
        });

        QUnit.test('one2manyandonchange(withdate)',asyncfunction(assert){
            assert.expect(7);

            this.data.partner.onchanges={
                date:function(){}
            };
            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="date"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('td:contains(01/25/2017)'));
            awaittestUtils.dom.click(form.$('.o_datepicker_input'));
            awaittestUtils.nextTick();
            awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
            awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)'));
            awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.year:contains(2017)'));
            awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(1));
            awaittestUtils.dom.click($('.day:contains(22)'));
            awaittestUtils.form.clickSave(form);

            assert.verifySteps(['read','read','onchange','write','read','read']);
            form.destroy();
        });

        QUnit.test('one2manyandonchange(withcommandDELETE_ALL)',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.onchanges={
                foo:function(obj){
                    obj.p=[[5]];
                },
                p:function(){},//dummyonchangeontheo2mtoexecute_isX2ManyValid()
            };
            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(method,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].p,[
                            [0,args.args[1].p[0][1],{display_name:'z'}],
                            [2,2,false],
                        ],"correctcommandsshouldbesent");
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "o2mshouldcontainonerow");

            //emptyo2mbytriggeringtheonchange
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'triggeronchange');

            assert.containsNone(form,'.o_data_row',
                "rowsoftheo2mshouldhavebeendeleted");

            //addtwonewsubrecords
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'x');
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'y');

            assert.containsN(form,'.o_data_row',2,
                "o2mshouldcontaintworows");

            //emptyo2mbytriggeringtheonchange
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'triggeronchangeagain');

            assert.containsNone(form,'.o_data_row',
                "rowsoftheo2mshouldhavebeendeleted");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'z');

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manyandonchangeonlywritemodifiedfield',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[
                        [5],//deleteall
                        [1,3,{//theserverreturnsallfields
                            display_name:"coucou",
                            product_id:[37,"xphone"],
                            turtle_bar:false,
                            turtle_foo:"haschanged",
                            turtle_int:42,
                            turtle_qux:9.8,
                            partner_ids:[],
                            turtle_ref:'product,37',
                        }],
                    ];
                },
            };

            this.data.partner.records[0].turtles=[3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="turtle_bar"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="turtle_qux"/>'+
                    '<fieldname="turtle_ref"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(method,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].turtles,[
                            [1,3,{display_name:'coucou',turtle_foo:'haschanged',turtle_int:42}],
                        ],"correctcommandsshouldbesent(onlysendchangedvalues)");
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "o2mshouldcontainonerow");

            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:firsttd:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_one2many.o_list_viewtbodytr:firstinput:first'),'blurp');

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manywithCREATEonchangescorrectlyrefreshed',asyncfunction(assert){
            assert.expect(5);

            vardelta=0;
            testUtils.mock.patch(AbstractField,{
                init:function(){
                    delta++;
                    this._super.apply(this,arguments);
                },
                destroy:function(){
                    delta--;
                    this._super.apply(this,arguments);
                },
            });

            vardeactiveOnchange=true;

            this.data.partner.records[0].turtles=[];
            this.data.partner.onchanges={
                turtles:function(obj){
                    if(deactiveOnchange){return;}
                    //theonchangewilleither:
                    // -createasecondlineifthereisonlyoneline
                    // -editthesecondlineiftherearetwolines
                    if(obj.turtles.length===1){
                        obj.turtles=[
                            [5],//deleteall
                            [0,obj.turtles[0][1],{
                                display_name:"first",
                                turtle_int:obj.turtles[0][2].turtle_int,
                            }],
                            [0,0,{
                                display_name:"second",
                                turtle_int:-obj.turtles[0][2].turtle_int,
                            }],
                        ];
                    }elseif(obj.turtles.length===2){
                        obj.turtles=[
                            [5],//deleteall
                            [0,obj.turtles[0][1],{
                                display_name:"first",
                                turtle_int:obj.turtles[0][2].turtle_int,
                            }],
                            [0,obj.turtles[1][1],{
                                display_name:"second",
                                turtle_int:-obj.turtles[0][2].turtle_int,
                            }],
                        ];
                    }
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"widget="char"/>'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsNone(form,'.o_data_row',
                "o2mshouldn'tcontainanyrow");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            //triggerthefirstonchange
            deactiveOnchange=false;
            awaittestUtils.fields.editInput(form.$('input[name="turtle_int"]'),'10');
            //putthelistbackinnoneditmode
            awaittestUtils.dom.click(form.$('input[name="foo"]'));
            assert.strictEqual(form.$('.o_data_row').text(),"first10second-10",
                "shouldcorrectlyrefreshtherecords");

            //triggerthesecondonchange
            awaittestUtils.dom.click(form.$('.o_field_x2many_listtbodytr:firsttd:first'));
            awaittestUtils.fields.editInput(form.$('input[name="turtle_int"]'),'20');

            awaittestUtils.dom.click(form.$('input[name="foo"]'));
            assert.strictEqual(form.$('.o_data_row').text(),"first20second-20",
                "shouldcorrectlyrefreshtherecords");

            assert.containsN(form,'.o_field_widget',delta,
                "all(nonvisible)fieldwidgetsshouldhavebeendestroyed");

            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('.o_data_row').text(),"first20second-20",
                "shouldcorrectlyrefreshtherecordsaftersave");

            form.destroy();
            testUtils.mock.unpatch(AbstractField);
        });

        QUnit.test('editableone2manywithsubwidgetsarerenderedinreadonly',asyncfunction(assert){
            assert.expect(2);

            vareditableWidgets=0;
            testUtils.mock.patch(AbstractField,{
                init:function(){
                    this._super.apply(this,arguments);
                    if(this.mode==='edit'){
                        editableWidgets++;
                    }
                },
            });

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"widget="char"attrs="{\'readonly\':[(\'turtle_int\',\'==\',11111)]}"/>'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.strictEqual(editableWidgets,1,
                "o2misonlywidgetineditmode");
            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));

            assert.strictEqual(editableWidgets,3,
                "3widgetscurrentlyineditmode");

            form.destroy();
            testUtils.mock.unpatch(AbstractField);
        });

        QUnit.test('one2manyeditablelistwithonchangekeepstheorder',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].p=[1,2,4];
            this.data.partner.onchanges={
                p:function(){},
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.strictEqual(form.$('.o_data_cell').text(),'firstrecordsecondrecordaaa',
                "recordsshouldbedisplayinthecorrectorder");

            awaittestUtils.dom.click(form.$('.o_data_row:first.o_data_cell'));
            awaittestUtils.fields.editInput(form.$('.o_selected_row.o_field_widget[name=display_name]'),'new');
            awaittestUtils.dom.click(form.$el);

            assert.strictEqual(form.$('.o_data_cell').text(),'newsecondrecordaaa',
                "recordsshouldbedisplayinthecorrectorder");

            form.destroy();
        });

        QUnit.test('one2manylist(editable):readonlydomainisevaluated',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].p=[2,4];
            this.data.partner.records[1].product_id=false;
            this.data.partner.records[2].product_id=37;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="display_name"attrs=\'{"readonly":[["product_id","=",false]]}\'/>'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            assert.hasClass(form.$('.o_list_viewtbodytr:eq(0)td:first'),'o_readonly_modifier',
                "firstrecordshouldhavedisplay_nameinreadonlymode");

            assert.doesNotHaveClass(form.$('.o_list_viewtbodytr:eq(1)td:first'),'o_readonly_modifier',
                "secondrecordshouldnothavedisplay_nameinreadonlymode");
            form.destroy();
        });

        QUnit.test('pagerofone2manyfieldinnewrecord',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].p=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                        '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            assert.containsNone(form,'.o_x2m_control_panel.o_pager',
                'o2mpagershouldbehidden');

            //clicktocreateasubrecord
            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            assert.containsOnce(form,'tr.o_data_row');

            assert.containsNone(form,'.o_x2m_control_panel.o_pager',
                'o2mpagershouldbehidden');
            form.destroy();
        });

        QUnit.test('one2manylistwithamany2one',asyncfunction(assert){
            assert.expect(5);

            letcheckOnchange=false;
            this.data.partner.records[0].p=[2];
            this.data.partner.records[1].product_id=37;
            this.data.partner.onchanges.p=function(obj){
                obj.p=[
                    [5],//deleteall
                    [1,2,{product_id:[37,"xphone"]}],//updateexistingrecord
                    [0,0,{product_id:[41,"xpad"]}]
                ];
                //
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner,false,form':
                        '<formstring="Partner"><fieldname="product_id"/></form>',
                },
                mockRPC:function(route,args){
                    if(args.method==='onchange'&&checkOnchange){
                        assert.deepEqual(args.args[1].p,[[4,2,false],[0,args.args[1].p[1][1],{product_id:41}]],
                            "shouldtriggeronchangewithcorrectparameters");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.strictEqual(form.$('tbodytd:contains(xphone)').length,1,
                "shouldhaveproperlyfetchedthemany2onenameget");
            assert.strictEqual(form.$('tbodytd:contains(xpad)').length,0,
                "shouldnotdisplay'xpad'anywhere");

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));

            checkOnchange=true;
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            testUtils.fields.many2one.clickItem('product_id','xpad');

            awaittestUtils.dom.click($('.modal.modal-footerbutton:eq(0)'));

            assert.strictEqual(form.$('tbodytd:contains(xpad)').length,1,
                "shoulddisplay'xpad'onatd");
            assert.strictEqual(form.$('tbodytd:contains(xphone)').length,1,
                "shouldstilldisplayxphone");
            form.destroy();
        });

        QUnit.test('one2manylistwithinlineformview',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].p=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<formstring="Partner">'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="int_field"/>'+
                    '</form>'+
                    '<tree>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="foo"/>'+ //don'tremovethis,itis
                    //usefultomakesurethefoofieldwidget
                    //doesnotcrashbecausethefoofield
                    //isnotintheformview
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].p,[[0,args.args[1].p[0][1],{
                            foo:"MylittleFooValue",int_field:123,product_id:41,
                        }]]);
                    }
                    returnthis._super(route,args);
                },
            });

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));

            //writeinthemany2onefield,value=37(xphone)
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

            //writeintheintegerfield
            awaittestUtils.fields.editInput($('.modal.modal-bodyinput.o_field_widget'),'123');

            //saveandclose
            awaittestUtils.dom.click($('.modal.modal-footerbutton:eq(0)'));

            assert.strictEqual(form.$('tbodytd:contains(xphone)').length,1,
                "shoulddisplay'xphone'inatd");

            //reopentherecordinformview
            awaittestUtils.dom.click(form.$('tbodytd:contains(xphone)'));

            assert.strictEqual($('.modal.modal-bodyinput').val(),"xphone",
                "shoulddisplay'xphone'inaninput");

            awaittestUtils.fields.editInput($('.modal.modal-bodyinput.o_field_widget'),'456');

            //discard
            awaittestUtils.dom.click($('.modal.modal-footerspan:contains(Discard)'));

            //reopentherecordinformview
            awaittestUtils.dom.click(form.$('tbodytd:contains(xphone)'));

            assert.strictEqual($('.modal.modal-bodyinput.o_field_widget').val(),"123",
                "shoulddisplay123(previouschangehasbeendiscarded)");

            //writeinthemany2onefield,value=41(xpad)
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            testUtils.fields.many2one.clickItem('product_id','xpad');

            //saveandclose
            awaittestUtils.dom.click($('.modal.modal-footerbutton:eq(0)'));

            assert.strictEqual(form.$('tbodytd:contains(xpad)').length,1,
                "shoulddisplay'xpad'inatd");

            //savetherecord
            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manylistwithinlineformviewwithcontextwithparentkey',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].p=[2];
            this.data.partner.records[0].product_id=41;
            this.data.partner.records[1].product_id=37;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="p">'+
                    '<formstring="Partner">'+
                    '<fieldname="product_id"context="{\'partner_foo\':parent.foo,\'lalala\':parent.product_id}"/>'+
                    '</form>'+
                    '<tree>'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.strictEqual(args.kwargs.context.partner_foo,"yop",
                            "shouldhavecorrectlyevaluatedparentfoofield");
                        assert.strictEqual(args.kwargs.context.lalala,41,
                            "shouldhavecorrectlyevaluatedparentproduct_idfield");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            //openamodal
            awaittestUtils.dom.click(form.$('tr.o_data_row:eq(0)td:contains(xphone)'));

            //writeinthemany2onefield
            awaittestUtils.dom.click($('.modal.o_field_many2oneinput'));

            form.destroy();
        });

        QUnit.test('valueofinvisiblex2manyfieldsiscorrectlyevaluatedincontext',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].timmy=[12];
            this.data.partner.records[0].p=[2,3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<formstring="Partners">'+
                    '<fieldname="product_id"context="{\'p\':p,\'timmy\':timmy}"/>'+
                    '<fieldname="p"invisible="1"/>'+
                    '<fieldname="timmy"invisible="1"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.deepEqual(
                            args.kwargs.context,{
                                p:[[4,2,false],[4,3,false]],
                                timmy:[[6,false,[12]]],
                            },'valuesofx2manysshouldhavebeencorrectlyevaluatedincontext');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_widget[name=product_id]input'));

            form.destroy();
        });

        QUnit.test('one2manylist,editable,withmany2oneandwithcontextwithparentkey',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].p=[2];
            this.data.partner.records[1].product_id=37;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="product_id"context="{\'partner_foo\':parent.foo}"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.strictEqual(args.kwargs.context.partner_foo,"yop",
                            "shouldhavecorrectlyevaluatedparentfoofield");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('tr.o_data_row:eq(0)td:contains(xphone)'));

            //triggeranamesearch
            awaittestUtils.dom.click(form.$('tabletdinput'));

            form.destroy();
        });

        QUnit.test('one2manylist,editable,withadateinthecontext',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].p=[2];
            this.data.partner.records[1].product_id=37;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="date"/>'+
                    '<fieldname="p"context="{\'date\':date}">'+
                    '<treeeditable="top">'+
                    '<fieldname="date"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        assert.strictEqual(args.kwargs.context.date,'2017-01-25',
                            "shouldhaveproperlyevaluateddatekeyincontext");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            form.destroy();
        });

        QUnit.test('one2manyfieldwithcontext',asyncfunction(assert){
            assert.expect(2);

            varcounter=0;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles"context="{\'turtles\':turtles}">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        varexpected=counter===0?
                            [[4,2,false]]:
                            [[4,2,false],[0,args.kwargs.context.turtles[1][1],{turtle_foo:'hammer'}]];
                        assert.deepEqual(args.kwargs.context.turtles,expected,
                            "shouldhaveproperlyevaluatedturtleskeyincontext");
                        counter++;
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('input[name="turtle_foo"]'),'hammer');
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            form.destroy();
        });

        QUnit.test('one2manylistedition,somebasicfunctionality',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.fields.foo.default=false;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));

            assert.containsOnce(form,'tdinput.o_field_widget',
                "shouldhavecreatedarowineditmode");

            awaittestUtils.fields.editInput(form.$('tdinput.o_field_widget'),'a');

            assert.containsOnce(form,'tdinput.o_field_widget',
                "shouldnothaveunselectedtherowafteredition");

            awaittestUtils.fields.editInput(form.$('tdinput.o_field_widget'),'abc');
            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('td:contains(abc)').length,1,
                "shouldhavearowwiththecorrectvalue");
            form.destroy();
        });

        QUnit.test('one2manylist,thecontextisproperlyevaluatedandsent',asyncfunction(assert){
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="p"context="{\'hello\':\'world\',\'abc\':int_field}">'+
                    '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        varcontext=args.kwargs.context;
                        assert.strictEqual(context.hello,"world");
                        assert.strictEqual(context.abc,10);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            form.destroy();
        });

        QUnit.test('one2manywithmany2manywidget:create',asyncfunction(assert){
            assert.expect(10);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles"widget="many2many">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_qux"/>'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '<form>'+
                    '<group>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_bar"/>'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="product_id"/>'+
                    '</group>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'turtle,false,list':'<tree><fieldname="display_name"/><fieldname="turtle_foo"/><fieldname="turtle_bar"/><fieldname="product_id"/></tree>',
                    'turtle,false,search':'<search><fieldname="turtle_foo"/><fieldname="turtle_bar"/><fieldname="product_id"/></search>',
                },
                session:{},
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/turtle/create'){
                        assert.ok(args.args,"shouldwriteontheturtlerecord");
                    }
                    if(route==='/web/dataset/call_kw/partner/write'){
                        assert.strictEqual(args.args[0][0],1,"shouldwriteonthepartnerrecord1");
                        assert.strictEqual(args.args[1].turtles[0][0],6,"shouldsendonlya'replacewith'command");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.strictEqual($('.modal.o_data_row').length,2,
                "shouldhave2recordsintheselectview(thelastoneisnotdisplayedbecauseitisalreadyselected)");

            awaittestUtils.dom.click($('.modal.o_data_row:first.o_list_record_selectorinput'));
            awaittestUtils.dom.click($('.modal.o_select_button'));
            awaittestUtils.dom.click($('.o_form_button_save'));
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.strictEqual($('.modal.o_data_row').length,1,
                "shouldhave1recordintheselectview");

            awaittestUtils.dom.click($('.modal-footerbutton:eq(1)'));
            awaittestUtils.fields.editInput($('.modalinput.o_field_widget[name="turtle_foo"]'),'tototo');
            awaittestUtils.fields.editInput($('.modalinput.o_field_widget[name="turtle_int"]'),50);
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

            awaittestUtils.dom.click($('.modal-footerbutton:contains(&):first'));

            assert.strictEqual($('.modal').length,0,"shouldclosethemodals");

            assert.containsN(form,'.o_data_row',3,
                "shouldhave3recordsinone2manylist");
            assert.strictEqual(form.$('.o_data_row').text(),"blip1.59yop1.50tototo1.550xphone",
                "shoulddisplaytherecordvaluesinone2manylist");

            awaittestUtils.dom.click($('.o_form_button_save'));

            form.destroy();
        });

        QUnit.test('one2manywithmany2manywidget:edition',asyncfunction(assert){
            assert.expect(7);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles"widget="many2many">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_qux"/>'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '<form>'+
                    '<group>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_bar"/>'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="turtle_trululu"/>'+
                    '<fieldname="product_id"/>'+
                    '</group>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'turtle,false,list':'<tree><fieldname="display_name"/><fieldname="turtle_foo"/><fieldname="turtle_bar"/><fieldname="product_id"/></tree>',
                    'turtle,false,search':'<search><fieldname="turtle_foo"/><fieldname="turtle_bar"/><fieldname="product_id"/></search>',
                },
                session:{},
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/turtle/write'){
                        assert.strictEqual(args.args[0].length,1,"shouldwriteontheturtlerecord");
                        assert.deepEqual(args.args[1],{"product_id":37},"shouldwriteonlytheproduct_idontheturtlerecord");
                    }
                    if(route==='/web/dataset/call_kw/partner/write'){
                        assert.strictEqual(args.args[0][0],1,"shouldwriteonthepartnerrecord1");
                        assert.strictEqual(args.args[1].turtles[0][0],6,"shouldsendonlya'replacewith'command");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.dom.click(form.$('.o_data_row:first'));
            assert.strictEqual($('.modal.modal-title').first().text().trim(),'Open:one2manyturtlefield',
                "modalshouldusethepythonfieldstringastitle");
            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));
            awaittestUtils.form.clickEdit(form);

            //editthefirstone2manyrecord
            awaittestUtils.dom.click(form.$('.o_data_row:first'));
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickHighlightedItem('product_id');
            awaittestUtils.dom.click($('.modal-footerbutton:first'));

            awaittestUtils.dom.click($('.o_form_button_save'));

            //addaone2manyrecord
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click($('.modal.o_data_row:first.o_list_record_selectorinput'));
            awaittestUtils.dom.click($('.modal.o_select_button'));

            //editthesecondone2manyrecord
            awaittestUtils.dom.click(form.$('.o_data_row:eq(1)'));
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickHighlightedItem('product_id');
            awaittestUtils.dom.click($('.modal-footerbutton:first'));

            awaittestUtils.dom.click($('.o_form_button_save'));

            form.destroy();
        });

        QUnit.test('newrecord,thecontextisproperlyevaluatedandsent',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.fields.int_field.default=17;
            varn=0;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="p"context="{\'hello\':\'world\',\'abc\':int_field}">'+
                    '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        n++;
                        if(n===2){
                            varcontext=args.kwargs.context;
                            assert.strictEqual(context.hello,"world");
                            assert.strictEqual(context.abc,17);
                        }
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            form.destroy();
        });

        QUnit.test('parentdataisproperlysentonanonchangerpc',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.onchanges={bar:function(){}};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="top">'+
                    '<fieldname="bar"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        varfieldValues=args.args[1];
                        assert.strictEqual(fieldValues.trululu.foo,"yop",
                            "shouldhaveproperlysenttheparentfoovalue");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            //useofowlCompatibilityNextTickbecausewehaveanx2manyfieldwithabooleanfield
            //(writteninowl),sowhenweaddaline,wesequentiallyrenderthelistitself
            //(includingthebooleanfield),sowehavetowaitforthenextanimationframe,and
            //thenwerenderthecontrolpanel(alsoinowl),sowehavetowaitagainforthe
            //nextanimationframe
            awaittestUtils.owlCompatibilityNextTick();
            form.destroy();
        });

        QUnit.test('parentdataisproperlysentonanonchangerpc(existingx2manyrecord)',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.onchanges={
                display_name:function(){},
            };
            this.data.partner.records[0].p=[1];
            this.data.partner.records[0].turtles=[2];
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="foo"/>
                        <fieldname="p">
                            <treeeditable="top">
                                <fieldname="display_name"/>
                                <fieldname="turtles"widget="many2many_tags"/>
                            </tree>
                        </field>
                    </form>`,
                res_id:1,
                mockRPC(route,args){
                    if(args.method==='onchange'){
                        constfieldValues=args.args[1];
                        assert.strictEqual(fieldValues.trululu.foo,"yop");
                        //weonlysendfieldsthatchangedinsidethereversemany2one
                        assert.deepEqual(fieldValues.trululu.p,[
                            [1,1,{display_name:'newval'}],
                        ]);
                    }
                    returnthis._super(...arguments);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row');

            awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell:first'));

            assert.containsOnce(form,'.o_data_row.o_selected_row');
            awaittestUtils.fields.editInput(form.$('.o_selected_row.o_field_widget[name=display_name]'),"newval");

            form.destroy();
        });

        QUnit.test('parentdataisproperlysentonanonchangerpc,newrecord',asyncfunction(assert){
            assert.expect(4);

            this.data.turtle.onchanges={turtle_bar:function(){}};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_bar"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    assert.step(args.method);
                    if(args.method==='onchange'&&args.model==='turtle'){
                        varfieldValues=args.args[1];
                        assert.strictEqual(fieldValues.turtle_trululu.foo,"MylittleFooValue",
                            "shouldhaveproperlysenttheparentfoovalue");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            //useofowlCompatibilityNextTickbecausewehaveanx2manyfieldwithabooleanfield
            //(writteninowl),sowhenweaddaline,wesequentiallyrenderthelistitself
            //(includingthebooleanfield),sowehavetowaitforthenextanimationframe,and
            //thenwerenderthecontrolpanel(alsoinowl),sowehavetowaitagainforthe
            //nextanimationframe
            awaittestUtils.owlCompatibilityNextTick();
            assert.verifySteps(['onchange','onchange']);
            form.destroy();
        });

        QUnit.test('idinone2manyobtainedinonchangeisproperlyset',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.onchanges.turtles=function(obj){
                obj.turtles=[
                    [5],
                    [1,3,{turtle_foo:"kawa"}]
                ];
            };
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="id"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            assert.strictEqual(form.$('tr.o_data_row').text(),'3kawa',
                "shouldhaveproperlydisplayedidandfoofield");
            form.destroy();
        });

        QUnit.test('idfieldinone2manyinanewrecord',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="id"invisible="1"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        varvirtualID=args.args[0].turtles[0][1];
                        assert.deepEqual(args.args[0].turtles,
                            [[0,virtualID,{turtle_foo:"cat"}]],
                            'shouldsendpropercommands');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.dom.click(form.$('td.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('tdinput[name="turtle_foo"]'),'cat');
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('subformviewwitharequiredfield',asyncfunction(assert){
            assert.expect(2);
            this.data.partner.fields.foo.required=true;
            this.data.partner.fields.foo.default=null;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<formstring="Partner">'+
                    '<group><fieldname="foo"/></group>'+
                    '</form>'+
                    '<tree>'+
                    '<fieldname="foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click($('.modal-footerbutton.btn-primary').first());

            assert.strictEqual($('.modal').length,1,"shouldstillhaveanopenmodal");
            assert.strictEqual($('.modaltbodylabel.o_field_invalid').length,1,
                "shouldhavedisplayedinvalidfields");
            form.destroy();
        });

        QUnit.test('one2manylistwithactionbutton',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="foo"/>'+
                    '<buttonname="method_name"type="object"icon="fa-plus"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                intercepts:{
                    execute_action:function(event){
                        assert.deepEqual(event.data.env.currentID,2,
                            'shouldcallwithcorrectid');
                        assert.strictEqual(event.data.env.model,'partner',
                            'shouldcallwithcorrectmodel');
                        assert.strictEqual(event.data.action_data.name,'method_name',
                            "shouldcallcorrectmethod");
                        assert.strictEqual(event.data.action_data.type,'object',
                            'shouldhavecorrecttype');
                    },
                },
            });

            awaittestUtils.dom.click(form.$('.o_list_buttonbutton'));

            form.destroy();
        });

        QUnit.test('one2manykanbanwithactionbutton',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<kanban>'+
                    '<fieldname="foo"/>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<div>'+
                    '<span><tt-esc="record.foo.value"/></span>'+
                    '<buttonname="method_name"type="object"class="fafa-plus"/>'+
                    '</div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                intercepts:{
                    execute_action:function(event){
                        assert.deepEqual(event.data.env.currentID,2,
                            'shouldcallwithcorrectid');
                        assert.strictEqual(event.data.env.model,'partner',
                            'shouldcallwithcorrectmodel');
                        assert.strictEqual(event.data.action_data.name,'method_name',
                            "shouldcallcorrectmethod");
                        assert.strictEqual(event.data.action_data.type,'object',
                            'shouldhavecorrecttype');
                    },
                },
            });

            awaittestUtils.dom.click(form.$('.oe_kanban_action_button'));

            form.destroy();
        });

        QUnit.test('one2manykanbanwithedittypeactionanddomainwidget(widgetusingSpecialData)',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.fields.model_name={string:"DomainConditionModel",type:"char"};
            this.data.turtle.fields.condition={string:"DomainCondition",type:"char"};
            _.each(this.data.turtle.records,function(record){
                record.model_name='partner';
                record.condition='[]';
            });

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles"mode="kanban">'+
                    '<kanban>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<div><fieldname="display_name"/></div>'+
                    '<div><fieldname="turtle_foo"/></div>'+
                    //fieldwithoutWidgetinthelist
                    '<div><fieldname="condition"/></div>'+
                    '<div><atype="edit">Edit</a></div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '<form>'+
                    '<fieldname="product_id"widget="statusbar"/>'+
                    '<fieldname="model_name"/>'+
                    //fieldwithWidgetrequiringspecialDataintheform
                    '<fieldname="condition"widget="domain"options="{\'model\':\'model_name\'}"/>'+
                    '</form>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.dom.click(form.$('.oe_kanban_action:eq(0)'));
            assert.strictEqual($('.o_domain_selector').length,1,"shouldadddomainselectorwidget");
            form.destroy();
        });

        QUnit.test('one2manylistwithonchangeanddomainwidget(widgetusingSpecialData)',asyncfunction(assert){
            assert.expect(3);

            this.data.turtle.fields.model_name={string:"DomainConditionModel",type:"char"};
            this.data.turtle.fields.condition={string:"DomainCondition",type:"char"};
            _.each(this.data.turtle.records,function(record){
                record.model_name='partner';
                record.condition='[]';
            });
            this.data.partner.onchanges={
                turtles:function(obj){
                    varvirtualID=obj.turtles[1][1];
                    obj.turtles=[
                        [5],//deleteall
                        [0,virtualID,{
                            display_name:"coucou",
                            product_id:[37,"xphone"],
                            turtle_bar:false,
                            turtle_foo:"haschanged",
                            turtle_int:42,
                            turtle_qux:9.8,
                            partner_ids:[],
                            turtle_ref:'product,37',
                            model_name:'partner',
                            condition:'[]',
                        }],
                    ];
                },
            };
            varnbFetchSpecialDomain=0;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles"mode="tree">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="turtle_foo"/>'+
                    //fieldwithoutWidgetinthelist
                    '<fieldname="condition"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="model_name"/>'+
                    //fieldwithWidgetrequiringspecialDataintheform
                    '<fieldname="condition"widget="domain"options="{\'model\':\'model_name\'}"/>'+
                    '</form>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
                mockRPC:function(route){
                    if(route==='/web/dataset/call_kw/partner/search_count'){
                        nbFetchSpecialDomain++;
                    }
                    returnthis._super.apply(this,arguments);
                }
            });

            awaittestUtils.dom.click(form.$('.o_field_one2many.o_field_x2many_list_row_adda'));
            assert.strictEqual($('.modal').length,1,"formviewdialogshouldbeopened");
            awaittestUtils.fields.editInput($('.modal-bodyinput[name="model_name"]'),'partner');
            awaittestUtils.dom.click($('.modal-footerbutton:first'));

            assert.strictEqual(form.$('.o_field_one2manytbodytr:first').text(),"coucouhaschanged[]",
                "theonchangeshouldcreateonenewrecordandremovetheexisting");

            awaittestUtils.dom.click(form.$('.o_field_one2many.o_list_viewtbodytr:eq(0)td:first'));

            awaittestUtils.form.clickSave(form);
            assert.strictEqual(nbFetchSpecialDomain,1,
                "shouldonlyfetchspecialdomainonce");
            form.destroy();
        });

        QUnit.test('one2manywithoutinlinetreearch',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[2,3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="p"widget="many2many_tags"/>'+//checkiftheviewdonnotcallloadview(widgetwithoutuseSubview)
                    '<fieldname="turtles"/>'+
                    '<fieldname="timmy"invisible="1"/>'+//checkiftheviewdonnotcallloadviewininvisible
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    "turtle,false,list":'<treestring="Turtles"><fieldname="turtle_bar"/><fieldname="display_name"/><fieldname="partner_ids"/></tree>',
                }
            });

            assert.containsOnce(form,'.o_field_widget[name="turtles"].o_list_view',
                'shoulddisplayone2manylistviewinthemodal');

            assert.containsN(form,'.o_data_row',2,
                'shoulddisplaythe2turtles');

            form.destroy();
        });

        QUnit.test('many2oneandmany2manyinone2many',asyncfunction(assert){
            assert.expect(11);

            this.data.turtle.records[1].product_id=37;
            this.data.partner.records[0].turtles=[2,3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles">'+
                    '<formstring="Turtles">'+
                    '<group>'+
                    '<fieldname="product_id"/>'+
                    '</group>'+
                    '</form>'+
                    '<treeeditable="top">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        varcommands=args.args[1].turtles;
                        assert.strictEqual(commands.length,2,
                            "shouldhavegenerated2commands");
                        assert.deepEqual(commands[0],[1,2,{
                            partner_ids:[[6,false,[2,1]]],
                            product_id:41,
                        }],"generatedcommandsshouldbecorrect");
                        assert.deepEqual(commands[1],[4,3,false],
                            "generatedcommandsshouldbecorrect");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.containsN(form,'.o_data_row',2,
                'shoulddisplaythe2turtles');
            assert.strictEqual(form.$('.o_data_row:firsttd:nth(1)').text(),'xphone',
                "shouldcorrectlydisplaythem2o");
            assert.strictEqual(form.$('.o_data_row:firsttd:nth(2).badge').length,2,
                "m2mshouldcontaintwotags");
            assert.strictEqual(form.$('.o_data_row:firsttd:nth(2).badge:firstspan').text(),
                'secondrecord',"m2mvaluesshouldhavebeencorrectlyfetched");

            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.strictEqual($('.modal.o_field_widget').text(),"xphone",
                'shoulddisplaytheformviewdialogwiththemany2onevalue');
            awaittestUtils.dom.click($('.modal-footerbutton'));

            awaittestUtils.form.clickEdit(form);

            //editthem2moffirstrow
            awaittestUtils.dom.click(form.$('.o_list_viewtbodytd:first()'));
            //removeatag
            awaittestUtils.dom.click(form.$('.o_field_many2manytags.badge:contains(aaa).o_delete'));
            assert.strictEqual(form.$('.o_selected_row.o_field_many2manytags.o_badge_text:contains(aaa)').length,0,
                "tagshouldhavebeencorrectlyremoved");
            //addatag
            awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');
            awaittestUtils.fields.many2one.clickHighlightedItem('partner_ids');
            assert.strictEqual(form.$('.o_selected_row.o_field_many2manytags.o_badge_text:contains(firstrecord)').length,1,
                "tagshouldhavebeencorrectlyadded");

            //editthem2ooffirstrow
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickItem('product_id','xpad');
            assert.strictEqual(form.$('.o_selected_row.o_field_many2one:firstinput').val(),'xpad',
                "m2ovalueshouldhavebeenupdated");

            //save(shouldcorrectlygeneratethecommands)
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('many2manytaginone2many,onchange,somemodifiers,andmorethanonepage',asyncfunction(assert){
            assert.expect(9);

            this.data.partner.records[0].turtles=[1,2,3];

            this.data.partner.onchanges.turtles=function(){};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top"limit="2">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"attrs="{\'readonly\':[(\'turtle_foo\',\'=\',\'a\')]}"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{mode:'edit'},
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });
            assert.containsN(form,'.o_data_row',2,
                'thereshouldbeonly2rowsdisplayed');
            awaittestUtils.dom.clickFirst(form.$('.o_list_record_remove'));
            awaittestUtils.dom.clickFirst(form.$('.o_list_record_remove'));

            assert.containsOnce(form,'.o_data_row',
                'thereshouldbejustoneremainingrow');

            assert.verifySteps([
                "read", //initialreadonpartner
                "read", //initialreadonturtle
                "read", //batchedreadonpartner(fieldpartner_ids)
                "read", //afterfirstdelete,readonturtle(tofetch3rdrecord)
                "onchange", //afterfirstdelete,onchangeonfieldturtles
                "onchange"  //onchangeafterseconddelete
            ]);

            form.destroy();
        });

        QUnit.test('onchangemany2manyinone2manylisteditable',asyncfunction(assert){
            assert.expect(14);

            this.data.product.records.push({
                id:1,
                display_name:"xenomorphe",
            });

            this.data.turtle.onchanges={
                product_id:function(rec){
                    if(rec.product_id){
                        rec.partner_ids=[
                            [5],
                            [4,rec.product_id===41?1:2]
                        ];
                    }
                },
            };
            varpartnerOnchange=function(rec){
                if(!rec.int_field||!rec.turtles.length){
                    return;
                }
                rec.turtles=[
                    [5],
                    [0,0,{
                        display_name:'newline',
                        product_id:[37,'xphone'],
                        partner_ids:[
                            [5],
                            [4,1]
                        ]
                    }],
                    [0,rec.turtles[0][1],{
                        display_name:rec.turtles[0][2].display_name,
                        product_id:[1,'xenomorphe'],
                        partner_ids:[
                            [5],
                            [4,2]
                        ]
                    }],
                ];
            };

            this.data.partner.onchanges={
                int_field:partnerOnchange,
                turtles:partnerOnchange,
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
            });

            //addnewline(first,xpad)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('input[name="display_name"]'),'first');
            awaittestUtils.dom.click(form.$('div[name="product_id"]input'));
            //theonchangewon'tbegenerated
            awaittestUtils.dom.click($('li.ui-menu-itema:contains(xpad)').trigger('mouseenter'));

            assert.containsOnce(form,'.o_field_many2manytags.o_input',
                'shoulddisplaythelineineditablemode');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"xpad",
                'shoulddisplaytheproductxpad');
            assert.strictEqual(form.$('.o_field_many2manytags.o_input.o_badge_text').text(),"firstrecord",
                'shoulddisplaythetagfromtheonchange');

            awaittestUtils.dom.click(form.$('input.o_field_integer[name="int_field"]'));

            assert.strictEqual(form.$('.o_data_cell.o_required_modifier').text(),"xpad",
                'shoulddisplaytheproductxpad');
            assert.strictEqual(form.$('.o_field_many2manytags:not(.o_input).o_badge_text').text(),"firstrecord",
                'shoulddisplaythetaginreadonly');

            //enablethemany2manyonchangeandgenerateit
            awaittestUtils.fields.editInput(form.$('input.o_field_integer[name="int_field"]'),'10');

            assert.strictEqual(form.$('.o_data_cell.o_required_modifier').text(),"xenomorphexphone",
                'shoulddisplaytheproductxphoneandxenomorphe');
            assert.strictEqual(form.$('.o_data_row').text().replace(/\s+/g,''),"firstxenomorphesecondrecordnewlinexphonefirstrecord",
                'shoulddisplaythename,one2manyandmany2manyvalue');

            //disablethemany2manyonchange
            awaittestUtils.fields.editInput(form.$('input.o_field_integer[name="int_field"]'),'0');

            //removeandstartover
            awaittestUtils.dom.click(form.$('.o_list_record_remove:firstbutton'));
            awaittestUtils.dom.click(form.$('.o_list_record_remove:firstbutton'));

            //enablethemany2manyonchange
            awaittestUtils.fields.editInput(form.$('input.o_field_integer[name="int_field"]'),'10');

            //addnewline(first,xenomorphe)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('input[name="display_name"]'),'first');
            awaittestUtils.dom.click(form.$('div[name="product_id"]input'));
            //generatetheonchange
            awaittestUtils.dom.click($('li.ui-menu-itema:contains(xenomorphe)').trigger('mouseenter'));

            assert.containsOnce(form,'.o_field_many2manytags.o_input',
                'shoulddisplaythelineineditablemode');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"xenomorphe",
                'shoulddisplaytheproductxenomorphe');
            assert.strictEqual(form.$('.o_field_many2manytags.o_input.o_badge_text').text(),"secondrecord",
                'shoulddisplaythetagfromtheonchange');

            //putlistinreadonlymode
            awaittestUtils.dom.click(form.$('input.o_field_integer[name="int_field"]'));

            assert.strictEqual(form.$('.o_data_cell.o_required_modifier').text(),"xenomorphexphone",
                'shoulddisplaytheproductxphoneandxenomorphe');
            assert.strictEqual(form.$('.o_field_many2manytags:not(.o_input).o_badge_text').text(),"secondrecordfirstrecord",
                'shoulddisplaythetaginreadonly(firstrecordandsecondrecord)');

            awaittestUtils.fields.editInput(form.$('input.o_field_integer[name="int_field"]'),'10');

            assert.strictEqual(form.$('.o_data_row').text().replace(/\s+/g,''),"firstxenomorphesecondrecordnewlinexphonefirstrecord",
                'shoulddisplaythename,one2manyandmany2manyvalue');

            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('.o_data_row').text().replace(/\s+/g,''),"firstxenomorphesecondrecordnewlinexphonefirstrecord",
                'shoulddisplaythename,one2manyandmany2manyvalueaftersave');

            form.destroy();
        });

        QUnit.test('loadviewforx2manyinone2many',asyncfunction(assert){
            assert.expect(2);

            this.data.turtle.records[1].product_id=37;
            this.data.partner.records[0].turtles=[2,3];
            this.data.partner.records[2].turtles=[1,3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles">'+
                    '<formstring="Turtles">'+
                    '<group>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="partner_ids"/>'+
                    '</group>'+
                    '</form>'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    "partner,false,list":'<treestring="Partners"><fieldname="display_name"/></tree>',
                },
            });

            assert.containsN(form,'.o_data_row',2,
                'shoulddisplaythe2turtles');

            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.strictEqual($('.modal.o_field_widget[name="partner_ids"].o_list_view').length,1,
                'shoulddisplaymany2manylistviewinthemodal');

            form.destroy();
        });

        QUnit.test('one2many(whocontainsaone2many)withtreeviewandwithoutformview',asyncfunction(assert){
            assert.expect(1);

            //avoiderrorin_postprocess

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="partner_ids"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    "turtle,false,form":'<formstring="Turtles"><fieldname="turtle_foo"/></form>',
                },
            });

            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.strictEqual($('.modal.o_field_widget[name="turtle_foo"]').text(),'blip',
                'shouldopenthemodalanddisplaytheformfield');

            form.destroy();
        });

        QUnit.test('one2manywithx2manyinformview(butnotinlistview)',asyncfunction(assert){
            assert.expect(1);

            //avoiderrorwhensavingtheeditedrelatedrecord(becausethe
            //relatedx2mfieldisunknownintheinlinelistview)
            //alsoensurethatthechangesarecorrectlysaved

            this.data.turtle.fields.o2m={string:"o2m",type:"one2many",relation:'user'};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    "turtle,false,form":'<formstring="Turtles">'+
                        '<fieldname="partner_ids"widget="many2many_tags"/>'+
                        '</form>',
                },
                viewOptions:{
                    mode:'edit',
                },
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].turtles,[[1,2,{
                            partner_ids:[[6,false,[2,4,1]]],
                        }]]);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.dom.click(form.$('.o_data_row:first'));//editfirstrecord

            awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');
            awaittestUtils.fields.many2one.clickHighlightedItem('partner_ids');

            //addamany2manytagandsave
            awaittestUtils.dom.click($('.modal.o_field_many2manytagsinput'));
            awaittestUtils.fields.editInput($('.modal.o_field_many2manytagsinput'),'test');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));//save

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('many2manylistinaone2manyopenedbyamany2one',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.records[1].turtle_trululu=2;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                archs:{
                    "partner,false,form":'<formstring="P">'+
                        '<fieldname="timmy"/>'+
                        '</form>',
                    "partner_type,false,list":'<treeeditable="bottom">'+
                        '<fieldname="display_name"/>'+
                        '</tree>',
                    "partner_type,false,search":'<search>'+
                        '</search>',
                },
                viewOptions:{
                    mode:'edit',
                },
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/get_formview_id'){
                        returnPromise.resolve(false);
                    }
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].timmy,[[6,false,[12]]],
                            'shouldproperlywriteids');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            //editthefirstpartnerintheone2manypartnerformview
            awaittestUtils.dom.click(form.$('.o_data_row:firsttd.o_data_cell'));
            //openformviewformany2one
            awaittestUtils.dom.click(form.$('.o_external_button'));

            //clickonadd,toaddanewpartnerinthem2m
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));

            //selectthepartner_type'gold'(thisclosesthe2ndmodal)
            awaittestUtils.dom.click($('.modaltd:contains(gold)'));

            //confirmthechangesinthemodal
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('nestedx2manydefaultvalues',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.fields.turtles.default=[
                [0,0,{partner_ids:[[6,0,[4]]]}],
                [0,0,{partner_ids:[[6,0,[1]]]}],
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            assert.containsN(form,'.o_list_view.o_data_row',2,
                "one2manylistshouldcontain2rows");
            assert.containsN(form,'.o_list_view.o_field_many2manytags[name="partner_ids"].badge',2,
                "m2mtagsshouldcontaintwotags");
            assert.strictEqual(form.$('.o_list_view.o_field_many2manytags[name="partner_ids"].o_badge_text').text(),
                'aaafirstrecord',"tagnamesshouldhavebeencorrectlyloaded");

            form.destroy();
        });

        QUnit.test('nestedx2many(inlineformview)andonchanges',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.onchanges.bar=function(obj){
                if(!obj.bar){
                    obj.p=[[5],[0,0,{
                        turtles:[[0,0,{
                            turtle_foo:'newturtle',
                        }]],
                    }]];
                }
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<form>
                        <fieldname="bar"/>
                        <fieldname="p">
                            <tree>
                                <fieldname="turtles"/>
                            </tree>
                            <form>
                                <fieldname="turtles">
                                    <tree>
                                        <fieldname="turtle_foo"/>
                                    </tree>
                                </field>
                            </form>
                        </field>
                    </form>`,
            });

            assert.containsNone(form,'.o_data_row');

            awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]input'));
            assert.containsOnce(form,'.o_data_row');
            assert.strictEqual(form.$('.o_data_row').text(),'1record');

            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsOnce(document.body,'.modal.o_form_view.o_data_row');
            assert.strictEqual($('.modal.o_form_view.o_data_row').text(),'newturtle');

            form.destroy();
        });

        QUnit.test('nestedx2many(noninlineformview)andonchanges',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.onchanges.bar=function(obj){
                if(!obj.bar){
                    obj.p=[[5],[0,0,{
                        turtles:[[0,0,{
                            turtle_foo:'newturtle',
                        }]],
                    }]];
                }
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p">
                            <tree>
                                <fieldname="turtles"/>
                            </tree>
                        </field>
                    </form>`,
                archs:{
                    'partner,false,form':`
                        <form>
                            <fieldname="turtles">
                                <tree>
                                    <fieldname="turtle_foo"/>
                                </tree>
                            </field>
                        </form>`,
                },
            });

            assert.containsNone(form,'.o_data_row');

            awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]input'));
            assert.containsOnce(form,'.o_data_row');
            assert.strictEqual(form.$('.o_data_row').text(),'1record');

            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsOnce(document.body,'.modal.o_form_view.o_data_row');
            assert.strictEqual($('.modal.o_form_view.o_data_row').text(),'newturtle');

            form.destroy();
        });

        QUnit.test('nestedx2many(noninlineviewsandnowidgetoninnerx2manyinlist)',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].p=[1];
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="p"/></form>',
                archs:{
                    'partner,false,list':'<tree><fieldname="turtles"/></tree>',
                    'partner,false,form':'<form><fieldname="turtles"widget="many2many_tags"/></form>',
                },
                res_id:1,
            });

            assert.containsOnce(form,'.o_data_row');
            assert.strictEqual(form.$('.o_data_row').text(),'1record');

            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsOnce(document.body,'.modal.o_form_view.o_field_many2manytags.badge');
            assert.strictEqual($('.modal.o_field_many2manytags').text().trim(),'donatello');

            form.destroy();
        });

        QUnit.test('one2many(whocontainsdisplay_name)withtreeviewandwithoutformview',asyncfunction(assert){
            assert.expect(1);

            //avoiderrorin_fetchX2Manys

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    "turtle,false,form":'<formstring="Turtles"><fieldname="turtle_foo"/></form>',
                },
            });

            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.strictEqual($('.modal.o_field_widget[name="turtle_foo"]').text(),'blip',
                'shouldopenthemodalanddisplaytheformfield');

            form.destroy();
        });

        QUnit.test('one2manyfieldwithvirtualids',asyncfunction(assert){
            assert.expect(11);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<notebook>'+
                    '<page>'+
                    '<fieldname="p"mode="kanban">'+
                    '<kanban>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<divclass="oe_kanban_details">'+
                    '<divclass="o_test_id">'+
                    '<fieldname="id"/>'+
                    '</div>'+
                    '<divclass="o_test_foo">'+
                    '<fieldname="foo"/>'+
                    '</div>'+
                    '</div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<formstring="Associatedpartners">'+
                        '<fieldname="foo"/>'+
                        '</form>',
                },
                res_id:4,
            });

            assert.containsOnce(form,'.o_field_widget.o_kanban_view',
                "shouldhaveoneinnerkanbanviewfortheone2manyfield");
            assert.strictEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)').length,0,
                "shouldnothavekanbanrecordsyet");

            ////switchtoeditmodeandcreateanewkanbanrecord
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_widget.o-kanban-button-new'));

            //save&closethemodal
            assert.strictEqual($('.modal-contentinput.o_field_widget').val(),'MylittleFooValue',
                "shouldalreadyhavethedefaultvalueforfieldfoo");
            awaittestUtils.dom.click($('.modal-content.btn-primary').first());

            assert.containsOnce(form,'.o_field_widget.o_kanban_view',
                "shouldhaveoneinnerkanbanviewfortheone2manyfield");
            assert.strictEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)').length,1,
                "shouldnowhaveonekanbanrecord");
            assert.strictEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost).o_test_id').text(),
                '',"shouldnothaveavaluefortheidfield");
            assert.strictEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost).o_test_foo').text(),
                'MylittleFooValue',"shouldhaveavalueforthefoofield");

            //savetheviewtoforceacreateofthenewrecordintheone2many
            awaittestUtils.form.clickSave(form);
            assert.containsOnce(form,'.o_field_widget.o_kanban_view',
                "shouldhaveoneinnerkanbanviewfortheone2manyfield");
            assert.strictEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)').length,1,
                "shouldnowhaveonekanbanrecord");
            assert.notEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost).o_test_id').text(),
                '',"shouldnowhaveavaluefortheidfield");
            assert.strictEqual(form.$('.o_field_widget.o_kanban_view.o_kanban_record:not(.o_kanban_ghost).o_test_foo').text(),
                'MylittleFooValue',"shouldstillhaveavalueforthefoofield");

            form.destroy();
        });

        QUnit.test('one2manyfieldwithvirtualidswithkanbanbutton',asyncfunction(assert){
            assert.expect(25);

            testUtils.mock.patch(KanbanRecord,{
                init:function(){
                    this._super.apply(this,arguments);
                    this._onKanbanActionClicked=this.__proto__._onKanbanActionClicked;
                },
            });

            this.data.partner.records[0].p=[4];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="p"mode="kanban">'+
                    '<kanban>'+
                        '<templates>'+
                        '<fieldname="foo"/>'+
                        '<tt-name="kanban-box">'+
                            '<div>'+
                                '<span><tt-esc="record.foo.value"/></span>'+
                                '<buttontype="object"class="btnbtn-linkfafa-shopping-cart"name="button_warn"string="button_warn"warn="warn"/>'+
                                '<buttontype="object"class="btnbtn-linkfafa-shopping-cart"name="button_disabled"string="button_disabled"/>'+
                            '</div>'+
                        '</t>'+
                        '</templates>'+
                    '</kanban>'+
                    '</field>'+
                '</form>',
                archs:{
                    'partner,false,form':'<form><fieldname="foo"/></form>',
                },
                res_id:1,
                services:{
                    notification:NotificationService.extend({
                        notify:function(params){
                            assert.step(params.type);
                        }
                    }),
                },
                intercepts:{
                    execute_action:function(event){
                        assert.step(event.data.action_data.name+'_'+event.data.env.model+'_'+event.data.env.currentID);
                        event.data.on_success();
                    },
                },
            });

            //1.Defineallcssselector
            varoKanbanView='.o_field_widget.o_kanban_view';
            varoKanbanRecordActive=oKanbanView+'.o_kanban_record:not(.o_kanban_ghost)';
            varoAllKanbanButton=oKanbanRecordActive+'button[data-type="object"]';
            varbtn1=oKanbanRecordActive+':nth-child(1)button[data-type="object"]';
            varbtn2=oKanbanRecordActive+':nth-child(2)button[data-type="object"]';
            varbtn1Warn=btn1+'[data-name="button_warn"]';
            varbtn1Disabled=btn1+'[data-name="button_disabled"]';
            varbtn2Warn=btn2+'[data-name="button_warn"]';
            varbtn2Disabled=btn2+'[data-name="button_disabled"]';

            //checkifwealreadyhaveonekanbancard
            assert.containsOnce(form,oKanbanView,"shouldhaveoneinnerkanbanviewfortheone2manyfield");
            assert.containsOnce(form,oKanbanRecordActive,"shouldhaveonekanbanrecordsyet");

            //wehave2buttons
            assert.containsN(form,oAllKanbanButton,2,"shouldhave2buttonstypeobject");

            //disabled?
            assert.containsNone(form,oAllKanbanButton+'[disabled]',"shouldnothavebuttontypeobjectdisabled");

            //clickonthebutton
            awaittestUtils.dom.click(form.$(btn1Disabled));
            awaittestUtils.dom.click(form.$(btn1Warn));

            //switchtoeditmode
            awaittestUtils.form.clickEdit(form);

            //clickonexistingbuttons
            awaittestUtils.dom.click(form.$(btn1Disabled));
            awaittestUtils.dom.click(form.$(btn1Warn));

            //createnewkanban
            awaittestUtils.dom.click(form.$('.o_field_widget.o-kanban-button-new'));

            //save&closethemodal
            assert.strictEqual($('.modal-contentinput.o_field_widget').val(),'MylittleFooValue',
                "shouldalreadyhavethedefaultvalueforfieldfoo");
            awaittestUtils.dom.click($('.modal-content.btn-primary').first());

            //checknewitem
            assert.containsN(form,oAllKanbanButton,4,"shouldhave4buttonstypeobject");
            assert.containsN(form,btn1,2,"shouldhave2buttonstypeobjectinarea1");
            assert.containsN(form,btn2,2,"shouldhave2buttonstypeobjectinarea2");
            assert.containsOnce(form,oAllKanbanButton+'[disabled]', "shouldhave1buttontypeobjectdisabled");

            assert.strictEqual(form.$(btn2Disabled).attr('disabled'),'disabled','Shouldhaveabuttontypeobjectdisabledinarea2');
            assert.strictEqual(form.$(btn2Warn).attr('disabled'),undefined,'Shouldhaveabuttontypeobjectnotdisabledinarea2');
            assert.strictEqual(form.$(btn2Warn).attr('warn'),'warn','Shouldhaveabuttontypeobjectwithwarnattrinarea2');

            //clickallbuttons
            awaittestUtils.dom.click(form.$(btn1Disabled));
            awaittestUtils.dom.click(form.$(btn1Warn));
            awaittestUtils.dom.click(form.$(btn2Warn));

            //savetheform
            awaittestUtils.form.clickSave(form);

            assert.containsNone(form,oAllKanbanButton+'[disabled]',"shouldnothavebuttontypeobjectdisabledaftersave");

            //clickallbuttons
            awaittestUtils.dom.click(form.$(btn1Disabled));
            awaittestUtils.dom.click(form.$(btn1Warn));
            awaittestUtils.dom.click(form.$(btn2Disabled));
            awaittestUtils.dom.click(form.$(btn2Warn));

            assert.verifySteps([
                "button_disabled_partner_4",
                "button_warn_partner_4",

                "button_disabled_partner_4",
                "button_warn_partner_4",

                "button_disabled_partner_4",
                "button_warn_partner_4",
                "danger",//warnbtn8

                "button_disabled_partner_4",
                "button_warn_partner_4",
                "button_disabled_partner_5",
                "button_warn_partner_5"
            ],"shouldhavetriggeredtheses11clicksevent");

            testUtils.mock.unpatch(KanbanRecord);
            form.destroy();
        });

        QUnit.test('focusingfieldsinone2manylist',asyncfunction(assert){
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="turtle_int"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '<fieldname="foo"/>'+
                    '</form>',
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('.o_data_row:firsttd:first'));
            assert.strictEqual(form.$('input[name="turtle_foo"]')[0],document.activeElement,
                "turtlefoofieldshouldhavefocus");

            awaittestUtils.fields.triggerKeydown(form.$('input[name="turtle_foo"]'),'tab');
            assert.strictEqual(form.$('input[name="turtle_int"]')[0],document.activeElement,
                "turtleintfieldshouldhavefocus");
            form.destroy();
        });

        QUnit.test('one2manylisteditable=top',asyncfunction(assert){
            assert.expect(6);

            this.data.turtle.fields.turtle_foo.default="defaultfooturtle";
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        varcommands=args.args[1].turtles;
                        assert.strictEqual(commands[0][0],0,
                            "firstcommandisacreate");
                        assert.strictEqual(commands[1][0],4,
                            "secondcommandisalinkto");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'.o_data_row',
                "shouldstartwithonedatarow");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_data_row',2,
                "shouldhave2datarows");
            assert.strictEqual(form.$('tr.o_data_row:firstinput').val(),'defaultfooturtle',
                "firstrowshouldbethenewvalue");
            assert.hasClass(form.$('tr.o_data_row:first'),'o_selected_row',
                "firstrowshouldbeselected");

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manylisteditable=bottom',asyncfunction(assert){
            assert.expect(6);
            this.data.turtle.fields.turtle_foo.default="defaultfooturtle";

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        varcommands=args.args[1].turtles;
                        assert.strictEqual(commands[0][0],4,
                            "firstcommandisalinkto");
                        assert.strictEqual(commands[1][0],0,
                            "secondcommandisacreate");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'.o_data_row',
                "shouldstartwithonedatarow");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'.o_data_row',2,
                "shouldhave2datarows");
            assert.strictEqual(form.$('tr.o_data_row:eq(1)input').val(),'defaultfooturtle',
                "secondrowshouldbethenewvalue");
            assert.hasClass(form.$('tr.o_data_row:eq(1)'),'o_selected_row',
                "secondrowshouldbeselected");

            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('one2manylistedition,no"Remove"buttoninmodal',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.fields.foo.default=false;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="foo"/>'+
                            '</tree>'+
                            '<formstring="Partners">'+
                                '<fieldname="display_name"/>'+
                            '</form>'+
                        '</field>'+
                    '</form>',
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('tbodytd.o_field_x2many_list_row_adda'));
            assert.containsOnce($(document),$('.modal'),'thereshouldbeamodalopened');
            assert.containsNone($('.modal.modal-footer.o_btn_remove'),
            'modalshouldnotcontaina"Remove"button');

            //Discardamodal
            awaittestUtils.dom.click($('.modal-footer.btn-secondary'));

            awaittestUtils.form.clickDiscard(form);
            form.destroy();
        });

        QUnit.test('x2manyfieldsusetheir"mode"attribute',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldmode="kanban"name="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '<kanban>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<div>'+
                    '<fieldname="turtle_int"/>'+
                    '</div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
            });

            assert.containsOnce(form,'.o_field_one2many.o_kanban_view',
                "shouldhaverenderedakanbanview");

            form.destroy();
        });

        QUnit.test('one2manylisteditable,onchangeandrequiredfield',asyncfunction(assert){
            assert.expect(8);

            this.data.turtle.fields.turtle_foo.required=true;
            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.int_field=obj.turtles.length;
                },
            };
            this.data.partner.records[0].int_field=0;
            this.data.partner.records[0].turtles=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"0",
                "int_fieldshouldstartwithvalue0");
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"0",
                "int_fieldshouldstillbe0(noonchangeshouldhavebeendoneyet");

            assert.verifySteps(['read','onchange']);

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name="turtle_foo"]'),"sometext");
            assert.verifySteps(['onchange']);
            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"1",
                "int_fieldshouldnowbe1(theonchangeshouldhavebeendone");

            form.destroy();
        });

        QUnit.test('one2manylisteditable:triggeronchangewhenrowisvalid',asyncfunction(assert){
            //shouldomitrequirefieldsthataren'tintheviewasthey(obviously)
            //havenovalue,whencheckingthevalidityofrequiredfields
            //shouldn'tconsidernumericalfieldswithvalue0asunset
            assert.expect(13);

            this.data.turtle.fields.turtle_foo.required=true;
            this.data.turtle.fields.turtle_qux.required=true;//requiredfieldnotintheview
            this.data.turtle.fields.turtle_bar.required=true;//requiredbooleanfieldwithnodefault
            deletethis.data.turtle.fields.turtle_bar.default;
            this.data.turtle.fields.turtle_int.required=true;//requiredintfield(default0)
            this.data.turtle.fields.turtle_int.default=0;
            this.data.turtle.fields.partner_ids.required=true;//requiredmany2many
            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.int_field=obj.turtles.length;
                },
            };
            this.data.partner.records[0].int_field=0;
            this.data.partner.records[0].turtles=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles"/>'+
                    '</form>',
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
                archs:{
                    'turtle,false,list':'<treeeditable="top">'+
                        '<fieldname="turtle_qux"/>'+
                        '<fieldname="turtle_bar"/>'+
                        '<fieldname="turtle_int"/>'+
                        '<fieldname="turtle_foo"/>'+
                        '<fieldname="partner_ids"widget="many2many_tags"/>'+
                        '</tree>',
                },
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"0",
                "int_fieldshouldstartwithvalue0");

            //addanewrow(whichisinvalidatfirst)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.owlCompatibilityNextTick();
            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"0",
                "int_fieldshouldstillbe0(noonchangeshouldhavebeendoneyet)");
            assert.verifySteps(['load_views','read','onchange']);

            //fillturtle_foofield
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name="turtle_foo"]'),"sometext");
            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"0",
                "int_fieldshouldstillbe0(noonchangeshouldhavebeendoneyet)");
            assert.verifySteps([],"noonchangeshouldhavebeenapplied");

            //fillpartner_idsfieldwithatag(allrequiredfieldswillthenbeset)
            awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');
            awaittestUtils.fields.many2one.clickHighlightedItem('partner_ids');
            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"1",
                "int_fieldshouldnowbe1(theonchangeshouldhavebeendone");
            assert.verifySteps(['name_search','read','onchange']);

            form.destroy();
        });

        QUnit.test('one2manylisteditable:\'required\'modifiersisproperlyworking',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.int_field=obj.turtles.length;
                },
            };

            this.data.partner.records[0].turtles=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"10",
                "int_fieldshouldstartwithvalue10");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"10",
                "int_fieldshouldstillbe10(noonchange,becauselineisnotvalid)");

            //fillturtle_foofield
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name="turtle_foo"]'),"sometext");

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"1",
                "int_fieldshouldbe1(onchangetriggered,becauselineisnowvalid)");

            form.destroy();
        });

        QUnit.test('one2manylisteditable:\'required\'modifiersisproperlyworking,part2',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.int_field=obj.turtles.length;
                },
            };

            this.data.partner.records[0].turtles=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="turtle_foo"attrs=\'{"required":[["turtle_int","=",0]]}\'/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });
            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"10",
                "int_fieldshouldstartwithvalue10");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"10",
                "int_fieldshouldstillbe10(noonchange,becauselineisnotvalid)");

            //fillturtle_intfield
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name="turtle_int"]'),"1");

            assert.strictEqual(form.$('.o_field_widget[name="int_field"]').val(),"1",
                "int_fieldshouldbe1(onchangetriggered,becauselineisnowvalid)");

            form.destroy();
        });

        QUnit.test('one2manylisteditable:addnewlinebeforeonchangereturns',asyncfunction(assert){
            //Iftheuseraddsanewrow(witharequiredfieldwithonchange),selects
            //avalueforthatfield,thenaddsanotherrowbeforetheonchangereturns,
            //theeditablelistmustwaitfortheonchangetoreturnbeforetryingto
            //unselectthefirstrow,otherwiseitwillbedetectedasinvalid.
            assert.expect(7);

            this.data.turtle.onchanges={
                turtle_trululu:function(){},
            };

            varprom;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                        '<fieldname="turtles">'+
                            '<treeeditable="bottom">'+
                                '<fieldname="turtle_trululu"required="1"/>'+
                            '</tree>'+
                        '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnPromise.resolve(prom).then(_.constant(result));
                    }
                    returnresult;
                },
            });

            //addafirstlinebutholdtheonchangeback
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            prom=testUtils.makeTestPromise();
            assert.containsOnce(form,'.o_data_row',
                "shouldhavecreatedthefirstrowimmediately");
            awaittestUtils.fields.many2one.clickOpenDropdown('turtle_trululu');
            awaittestUtils.fields.many2one.clickHighlightedItem('turtle_trululu');

            //trytoaddasecondlineandcheckthatitiscorrectlywaiting
            //fortheonchangetoreturn
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.strictEqual($('.modal').length,0,"nomodalshouldbedisplayed");
            assert.strictEqual($('.o_field_invalid').length,0,
                "nofieldshouldbemarkedasinvalid");
            assert.containsOnce(form,'.o_data_row',
                "shouldwaitfortheonchangetocreatethesecondrow");
            assert.hasClass(form.$('.o_data_row'),'o_selected_row',
                "firstrowshouldstillbeinedition");

            //resolvetheonchangepromise
            prom.resolve();
            awaittestUtils.nextTick();
            assert.containsN(form,'.o_data_row',2,
                "secondrowshouldnowhavebeencreated");
            assert.doesNotHaveClass(form.$('.o_data_row:first'),'o_selected_row',
                "firstrowshouldnomorebeinedition");

            form.destroy();
        });

        QUnit.test('editablelist:multipleclicksonAddanitemdonotcreateinvalidrows',asyncfunction(assert){
            assert.expect(3);

            this.data.turtle.onchanges={
                turtle_trululu:function(){},
            };

            varprom;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnPromise.resolve(prom).then(_.constant(result));
                    }
                    returnresult;
                },
            });
            prom=testUtils.makeTestPromise();
            //clicktwicetoaddanewline
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsNone(form,'.o_data_row',
                "norowshouldhavebeencreatedyet(waitingfortheonchange)");

            //resolvetheonchangepromise
            prom.resolve();
            awaittestUtils.nextTick();
            assert.containsOnce(form,'.o_data_row',
                "onlyonerowshouldhavebeencreated");
            assert.hasClass(form.$('.o_data_row:first'),'o_selected_row',
                "thecreatedrowshouldbeinedition");

            form.destroy();
        });

        QUnit.test('editablelist:valueresetbyanonchange',asyncfunction(assert){
            //thistestreproducesasubtlebehaviorthatmayoccurinaformview:
            //theuseraddsarecordinaone2manyfield,anddirectlyclicksona
            //datetimefieldoftheformviewwhichhasanonchange,whichtotally
            //overridesthevalueoftheone2many(commands5and0).Thehandler
            //thatswitchestheeditedrowtoreadonlyisthencalledafterthe
            //newvalueoftheone2manyfieldisapplied(theonereturnedbythe
            //onchange),sotherowthatmustgotoreadonlydoesn'texistanymore.
            assert.expect(2);

            this.data.partner.onchanges={
                datetime:function(obj){
                    obj.turtles=[[5],[0,0,{display_name:'new'}]];
                },
            };

            varprom;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="datetime"/>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnPromise.resolve(prom).then(_.constant(result));
                    }
                    returnresult;
                },
            });

            //triggerthetwoonchanges
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_data_row.o_field_widget'),'aname');
            prom=testUtils.makeTestPromise();
            awaittestUtils.dom.click(form.$('.o_datepicker_input'));
            vardateTimeVal=fieldUtils.format.datetime(moment(),{timezone:false});
            awaittestUtils.fields.editSelect(form.$('.o_datepicker_input'),dateTimeVal);

            //resolvetheonchangepromise
            prom.resolve();
            awaittestUtils.nextTick();

            assert.containsOnce(form,'.o_data_row',
                "shouldhaveonerecordintheo2m");
            assert.strictEqual(form.$('.o_data_row.o_data_cell').text(),'new',
                "shouldbetherecordcreatedbytheonchange");

            form.destroy();
        });

        QUnit.test('editablelist:onchangethatreturnsawarning',asyncfunction(assert){
            assert.expect(5);

            this.data.turtle.onchanges={
                display_name:function(){},
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        assert.step(args.method);
                        returnPromise.resolve({
                            value:{},
                            warning:{
                                title:"Warning",
                                message:"Youmustfirstselectapartner"
                            },
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{
                    mode:'edit',
                },
                intercepts:{
                    warning:function(){
                        assert.step('warning');
                    },
                },
            });

            //addaline(thisshouldtriggeranonchangeandawarning)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            //checkif'Addanitem'stillworks(thisshouldtriggeranonchange
            //andawarningagain)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.verifySteps(['onchange','warning','onchange','warning']);

            form.destroy();
        });

        QUnit.test('editablelist:contextsarecorrectlysent',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].timmy=[12];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="timmy"context="{\'key\':parent.foo}">'+
                    '<treeeditable="top">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='read'&&args.model==='partner'){
                        assert.deepEqual(args.kwargs.context,{
                            active_field:2,
                            bin_size:true,
                            someKey:'somevalue',
                        },"sentcontextshouldbecorrect");
                    }
                    if(args.method==='read'&&args.model==='partner_type'){
                        assert.deepEqual(args.kwargs.context,{
                            key:'yop',
                            active_field:2,
                            someKey:'somevalue',
                        },"sentcontextshouldbecorrect");
                    }
                    if(args.method==='write'){
                        assert.deepEqual(args.kwargs.context,{
                            active_field:2,
                            someKey:'somevalue',
                        },"sentcontextshouldbecorrect");
                    }
                    returnthis._super.apply(this,arguments);
                },
                session:{
                    user_context:{someKey:'somevalue'},
                },
                viewOptions:{
                    mode:'edit',
                    context:{active_field:2},
                },
                res_id:1,
            });

            awaittestUtils.dom.click(form.$('.o_data_cell:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'abc');
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('resettinginvisibleone2manys',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].turtles=[];
            this.data.partner.onchanges.foo=function(obj){
                obj.turtles=[[5],[4,1]];
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="turtles"invisible="1"/>'+
                    '</form>',
                viewOptions:{
                    mode:'edit',
                },
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.fields.editInput(form.$('input[name="foo"]'),'abcd');
            assert.verifySteps(['read','onchange']);

            form.destroy();
        });

        QUnit.test('one2many:onchangethatreturnsunknownfieldinlist,butnotinform',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.onchanges={
                name:function(){},
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="name"/>'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({
                            value:{
                                p:[[5],[0,0,{display_name:'new',timmy:[[5],[4,12]]}]],
                            },
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "theone2manyshouldcontainonerow");
            assert.containsNone(form,'.o_field_widget[name="timmy"]',
                "timmyshouldnotbedisplayedinthelistview");

            awaittestUtils.dom.click(form.$('.o_data_rowtd:first'));

            assert.strictEqual($('.modal.o_field_many2manytags[name="timmy"]').length,1,
                "timmyshouldbedisplayedintheformview");
            assert.strictEqual($('.modal.o_field_many2manytags[name="timmy"].badge').length,1,
                "m2mtagsshouldcontainonetag");
            assert.strictEqual($('.modal.o_field_many2manytags[name="timmy"].o_badge_text').text(),
                'gold',"tagnameshouldhavebeencorrectlyloaded");

            form.destroy();
        });

        QUnit.test('multilevelofnestedx2manys,onchangeandrawChanges',asyncfunction(assert){
            assert.expect(8);

            this.data.partner.records[0].p=[1];
            this.data.partner.onchanges={
                name:function(){},
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="name"/>
                        <fieldname="p">
                            <tree><fieldname="display_name"/></tree>
                            <form>
                                <fieldname="display_name"/>
                                <fieldname="p">
                                    <tree><fieldname="display_name"/></tree>
                                    <form><fieldname="display_name"/></form>
                                </field>
                            </form>
                        </field>
                    </form>`,
                mockRPC(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].p[0][2],{
                            p:[[1,1,{display_name:'newname'}]],
                        });
                    }
                    returnthis._super(...arguments);
                },
                res_id:1,
            });

            assert.containsOnce(form,'.o_data_row',"theone2manyshouldcontainonerow");

            //opentheo2mrecordinreadonlyfirst
            awaittestUtils.dom.click(form.$('.o_data_rowtd:first'));
            assert.containsOnce(document.body,".modal.o_form_readonly");
            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //switchtoeditmodeandopenitagain
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_data_rowtd:first'));

            assert.containsOnce(document.body,".modal.o_form_editable");
            assert.containsOnce(document.body,'.modal.o_data_row',"theone2manyshouldcontainonerow");

            //opentheo2magain,inthedialog
            awaittestUtils.dom.click($('.modal.o_data_rowtd:first'));

            assert.containsN(document.body,".modal.o_form_editable",2);

            //editthenameandclicksavemodalthatisontop
            awaittestUtils.fields.editInput($('.modal:nth(1).o_field_widget[name=display_name]'),'newname');
            awaittestUtils.dom.click($('.modal:nth(1).modal-footer.btn-primary'));

            assert.containsOnce(document.body,".modal.o_form_editable");

            //clicksaveontheothermodal
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

            assert.containsNone(document.body,".modal");

            //savethemainrecord
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('onchangeandrequiredfieldswithoverrideinarch',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.onchanges={
                turtles:function(){}
            };
            this.data.turtle.fields.turtle_foo.required=true;
            this.data.partner.records[0].turtles=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="turtle_foo"required="0"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.form.clickEdit(form);

            //triggersanonchangeonpartner,becausethenewrecordisvalid
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.verifySteps(['read','onchange','onchange']);
            form.destroy();
        });

        QUnit.test('onchangeonaone2manycontainingaone2many',asyncfunction(assert){
            //thepurposeofthistestistoensurethattheonchangespecsare
            //correctlyandrecursivelycomputed
            assert.expect(1);

            this.data.partner.onchanges={
                p:function(){}
            };
            varcheckOnchange=false;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree><fieldname="display_name"/></tree>'+
                    '<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom"><fieldname="display_name"/></tree>'+
                    '</field>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='onchange'&&checkOnchange){
                        assert.strictEqual(args.args[3]['p.p.display_name'],'',
                            "onchangespecsshouldbecomputedrecursively");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput($('.modal.o_data_cellinput'),'newrecord');
            checkOnchange=true;
            awaittestUtils.dom.clickFirst($('.modal.modal-footer.btn-primary'));

            form.destroy();
        });

        QUnit.test('editingtabbedone2many(editable=bottom)',asyncfunction(assert){
            assert.expect(12);

            this.data.partner.records[0].turtles=[];
            for(vari=0;i<42;i++){
                varid=100+i;
                this.data.turtle.records.push({id:id,turtle_foo:'turtle'+(id-99)});
                this.data.partner.records[0].turtles.push(id);
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    if(args.method==='write'){
                        assert.strictEqual(args.args[1].turtles[40][0],0,'shouldsendacreatecommand');
                        assert.deepEqual(args.args[1].turtles[40][2],{turtle_foo:'rainbowdash'});
                    }
                    returnthis._super.apply(this,arguments);
                },
            });


            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'tr.o_data_row',41);
            assert.hasClass(form.$('tr.o_data_row').last(),'o_selected_row');

            awaittestUtils.fields.editInput(form.$('.o_data_rowinput[name="turtle_foo"]'),'rainbowdash');
            awaittestUtils.form.clickSave(form);

            assert.containsN(form,'tr.o_data_row',40);

            assert.verifySteps(['read','read','onchange','write','read','read']);
            form.destroy();
        });

        QUnit.test('editingtabbedone2many(editable=bottom),again...',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].turtles=[];
            for(vari=0;i<9;i++){
                varid=100+i;
                this.data.turtle.records.push({id:id,turtle_foo:'turtle'+(id-99)});
                this.data.partner.records[0].turtles.push(id);
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom"limit="3">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });


            awaittestUtils.form.clickEdit(form);
            //addanewrecordpage1(thisincreasesthelimitto4)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_data_rowinput[name="turtle_foo"]'),'rainbowdash');
            awaittestUtils.dom.click(form.$('.o_x2m_control_panel.o_pager_next'));//page2:4records
            awaittestUtils.dom.click(form.$('.o_x2m_control_panel.o_pager_next'));//page3:2records

            assert.containsN(form,'tr.o_data_row',2,
                "shouldhave2datarowsonthecurrentpage");
            form.destroy();
        });

        QUnit.test('editingtabbedone2many(editable=top)',asyncfunction(assert){
            assert.expect(15);

            this.data.partner.records[0].turtles=[];
            this.data.turtle.fields.turtle_foo.default="defaultfoo";
            for(vari=0;i<42;i++){
                varid=100+i;
                this.data.turtle.records.push({id:id,turtle_foo:'turtle'+(id-99)});
                this.data.partner.records[0].turtles.push(id);
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    if(args.method==='write'){
                        assert.strictEqual(args.args[1].turtles[40][0],0);
                        assert.deepEqual(args.args[1].turtles[40][2],{turtle_foo:'rainbowdash'});
                    }
                    returnthis._super.apply(this,arguments);
                },
            });


            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));

            assert.containsN(form,'tr.o_data_row',2);

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(form,'tr.o_data_row',3);

            assert.hasClass(form.$('tr.o_data_row').first(),'o_selected_row');

            assert.strictEqual(form.$('tr.o_data_rowinput').val(),'defaultfoo',
                "selectedinputshouldhavecorrectstring");

            awaittestUtils.fields.editInput(form.$('.o_data_rowinput[name="turtle_foo"]'),'rainbowdash');
            awaittestUtils.form.clickSave(form);

            assert.containsN(form,'tr.o_data_row',40);

            assert.verifySteps(['read','read','read','onchange','write','read','read']);
            form.destroy();
        });

        QUnit.test('one2manyfield:changevaluebeforependingonchangereturns',asyncfunction(assert){
            assert.expect(2);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            this.data.partner.onchanges={
                int_field:function(){}
            };
            varprom;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        //delaytheonchangeRPC
                        returnPromise.resolve(prom).then(_.constant(result));
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            prom=testUtils.makeTestPromise();
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),'44');

            var$dropdown=form.$('.o_field_many2oneinput').autocomplete('widget');
            //settrululubeforeonchange
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'first',['keydown','keyup']);
            //completetheonchange
            prom.resolve();
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),'first',
                'shouldhavekeptthenewvalue');
            awaittestUtils.nextTick();
            //checkname_searchresult
            assert.strictEqual($dropdown.find('li:not(.o_m2o_dropdown_option)').length,1,
                'autocompleteshouldcontains1suggestion');

            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('focusiscorrectlyresetafteranonchangeinanx2many',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.onchanges={
                int_field:function(){}
            };
            varprom;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="int_field"/>'+
                    '<buttonstring="hello"/>'+
                    '<fieldname="qux"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        //delaytheonchangeRPC
                        returnPromise.resolve(prom).then(_.constant(result));
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            prom=testUtils.makeTestPromise();
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_widget[name=int_field]'),'44',
                ['input',{type:'keydown',which:$.ui.keyCode.TAB}]);
            prom.resolve();
            awaittestUtils.nextTick();

            assert.strictEqual(document.activeElement,form.$('.o_field_widget[name=qux]')[0],
                "quxfieldshouldhavethefocus");

            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            awaittestUtils.fields.many2one.clickHighlightedItem('trululu');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),'firstrecord',
                "theone2manyfieldshouldhavetheexpectedvalue");

            form.destroy();
        });

        QUnit.test('checkboxinanx2manythattriggersanonchange',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.onchanges={
                bar:function(){}
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="bar"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            //useofowlCompatibilityNextTickbecausewehaveabooleanfield(owl)insidethe
            //x2many,soanupdateofthex2manyrequirestowaitfor2animationframes:one
            //forthelisttobere-rendered(withthebooleanfield)andoneforthecontrol
            //panel.
            awaittestUtils.owlCompatibilityNextTick();
            awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]input'));
            assert.notOk(form.$('.o_field_widget[name=bar]input').prop('checked'),
                "thecheckboxshouldbeunticked");

            form.destroy();
        });

        QUnit.test('one2manywithdefaultvalue:editlinetomakeitinvalid',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.fields.p.default=[
                [0,false,{foo:"coucou",int_field:5,p:[]}],
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            //editthelineandenteraninvalidvalueforint_field
            awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell:nth(1)'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),'e');
            awaittestUtils.dom.click(form.$el);

            assert.containsOnce(form,'.o_data_row.o_selected_row',
                "lineshouldnothavebeenremovedandshouldstillbeinedition");
            assert.strictEqual($('.modal').length,1,
                "aconfirmationdialogshouldbeopened");
            assert.hasClass(form.$('.o_field_widget[name=int_field]'),'o_field_invalid',
                "shouldindicatethatint_fieldisinvalid");

            form.destroy();
        });

        QUnit.test('defaultvaluefornestedone2manys(comingfromonchange)',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.onchanges.p=function(obj){
                obj.p=[
                    [5],
                    [0,0,{turtles:[[5],[4,1]]}],//linkrecord1bydefault
                ];
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<tree><fieldname="turtles"/></tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        assert.strictEqual(args.args[0].p[0][0],0,
                            "shouldsendacommand0(CREATE)forp");
                        assert.deepEqual(args.args[0].p[0][2],{turtles:[[4,1,false]]},
                            "shouldsendthecorrectvalues");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.strictEqual(form.$('.o_data_cell').text(),'1record',
                "shouldcorrectlydisplaythevalueoftheinnero2m");

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('displaycorrectvalueaftervalidationerror',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.onchanges.turtles=function(){};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        if(args.args[1].turtles[0][2].turtle_foo==='pinky'){
                            //wesimulateavalidationerror. Inthe'real'webclient,
                            //theservererrorwillbeusedbythesessiontodisplay
                            //anerrordialog. Fromthepointofviewofthebasic
                            //model,thepromiseisjustrejected.
                            returnPromise.reject();
                        }
                    }
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].turtles[0],[1,2,{turtle_foo:'foo'}],
                            'shouldsendthe"good"value');
                    }
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{mode:'edit'},
                res_id:1,
            });

            assert.strictEqual(form.$('.o_data_row.o_data_cell:nth(0)').text(),'blip',
                "initialtextshouldbecorrect");

            //clickandeditvalueto'foo',whichwilltriggeronchange
            awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell:nth(0)'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=turtle_foo]'),'foo');
            awaittestUtils.dom.click(form.$el);
            assert.strictEqual(form.$('.o_data_row.o_data_cell:nth(0)').text(),'foo',
                "fieldshouldhavebeenchangedtofoo");

            //clickandeditvalueto'pinky',whichtriggerafailedonchange
            awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell:nth(0)'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=turtle_foo]'),'pinky');
            awaittestUtils.dom.click(form.$el);

            assert.strictEqual(form.$('.o_data_row.o_data_cell:nth(0)').text(),'foo',
                "turtle_footextshouldnowbesetbacktofoo");

            //wemakesureherethatwhenwesave,thevaluesarethecurrent
            //valuesdisplayedinthefield.
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('propagatecontexttosubviewswithoutdefault_*keys',asyncfunction(assert){
            assert.expect(7);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    assert.strictEqual(args.kwargs.context.flutter,'shy',
                        'viewcontextkeyshouldbeusedforeveryrpcs');
                    if(args.method==='onchange'){
                        if(args.model==='partner'){
                            assert.strictEqual(args.kwargs.context.default_flutter,'why',
                                "shouldhavedefault_*valuesincontextforformviewRPCs");
                        }elseif(args.model==='turtle'){
                            assert.notOk(args.kwargs.context.default_flutter,
                                "shouldnothavedefault_*valuesincontextforsubviewRPCs");
                        }
                    }
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{
                    context:{
                        flutter:'shy',
                        default_flutter:'why',
                    },
                },
            });
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('input[name="turtle_foo"]'),'pinkypie');
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('nestedone2manyswithnowidgetinlistandasinvisiblelistinform',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.records[0].p=[1];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="p">
                            <tree><fieldname="turtles"/></tree>
                            <form><fieldname="turtles"invisible="1"/></form>
                        </field>
                    </form>`,
                res_id:1,
            });

            assert.containsOnce(form,'.o_data_row');
            assert.strictEqual(form.$('.o_data_row.o_data_cell').text(),'1record');

            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsNone(document.body,'.modal.o_form_view.o_field_one2many');

            //Testpossiblecachingissues
            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));
            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsNone(document.body,'.modal.o_form_view.o_field_one2many');

            form.destroy();
        });

        QUnit.test('onchangeonnestedone2manys',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.onchanges.display_name=function(obj){
                if(obj.display_name){
                    obj.p=[
                        [5],
                        [0,0,{
                            display_name:'test',
                            turtles:[[5],[0,0,{display_name:'testnested'}]],
                        }],
                    ];
                }
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="turtles">'+
                    '<tree><fieldname="display_name"/></tree>'+
                    '</field>'+
                    '</form>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        assert.strictEqual(args.args[0].p[0][0],0,
                            "shouldsendacommand0(CREATE)forp");
                        assert.strictEqual(args.args[0].p[0][2].display_name,'test',
                            "shouldsendthecorrectvalues");
                        assert.strictEqual(args.args[0].p[0][2].turtles[0][0],0,
                            "shouldsendacommand0(CREATE)forturtles");
                        assert.deepEqual(args.args[0].p[0][2].turtles[0][2],{display_name:'testnested'},
                            "shouldsendthecorrectvalues");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'triggeronchange');

            assert.strictEqual(form.$('.o_data_cell').text(),'test',
                "shouldhaveaddedthenewrowtotheone2many");

            //openthenewsubrecordtocheckthevalueofthenestedo2m,andto
            //ensurethatitwillbesaved
            awaittestUtils.dom.click(form.$('.o_data_cell:first'));
            assert.strictEqual($('.modal.o_data_cell').text(),'testnested',
                "shouldhaveaddedthenewrowtothenestedone2many");
            awaittestUtils.dom.clickFirst($('.modal.modal-footer.btn-primary'));

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('one2manywithmultiplepagesandsequencefield',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].turtles=[3,2,1];
            this.data.partner.onchanges.turtles=function(){};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="2">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="partner_ids"invisible="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({
                            value:{
                                turtles:[
                                    [5],
                                    [1,1,{turtle_foo:"fromonchange",partner_ids:[[5]]}],
                                ]
                            }
                        });
                    }
                    returnthis._super(route,args);
                },
                viewOptions:{
                    mode:'edit',
                },
            });
            awaittestUtils.dom.click(form.$('.o_list_record_remove:firstbutton'));
            assert.strictEqual(form.$('.o_data_row').text(),'fromonchange',
                'onchangehasbeenproperlyapplied');
            form.destroy();
        });

        QUnit.test('one2manywithmultiplepagesandsequencefield,part2',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].turtles=[3,2,1];
            this.data.partner.onchanges.turtles=function(){};

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="2">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="partner_ids"invisible="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({
                            value:{
                                turtles:[
                                    [5],
                                    [1,1,{turtle_foo:"fromonchangeid2",partner_ids:[[5]]}],
                                    [1,3,{turtle_foo:"fromonchangeid3",partner_ids:[[5]]}],
                                ]
                            }
                        });
                    }
                    returnthis._super(route,args);
                },
                viewOptions:{
                    mode:'edit',
                },
            });
            awaittestUtils.dom.click(form.$('.o_list_record_remove:firstbutton'));
            assert.strictEqual(form.$('.o_data_row').text(),'fromonchangeid2fromonchangeid3',
                'onchangehasbeenproperlyapplied');
            form.destroy();
        });

        QUnit.test('one2manywithsequencefield,overridedefault_get,bottomwheninline',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[3,2,1];

            this.data.turtle.fields.turtle_int.default=10;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //startingcondition
            assert.strictEqual($('.o_data_cell').text(),"blipyopkawa");

            //clickaddanewline
            //savetherecord
            //checklineisatthecorrectplace

            varinputText='ninja';
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_input[name="turtle_foo"]'),inputText);
            awaittestUtils.form.clickSave(form);

            assert.strictEqual($('.o_data_cell').text(),"blipyopkawa"+inputText);
            form.destroy();
        });

        QUnit.test('one2manywithsequencefield,overridedefault_get,topwheninline',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[3,2,1];

            this.data.turtle.fields.turtle_int.default=10;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //startingcondition
            assert.strictEqual($('.o_data_cell').text(),"blipyopkawa");

            //clickaddanewline
            //savetherecord
            //checklineisatthecorrectplace

            varinputText='ninja';
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_input[name="turtle_foo"]'),inputText);
            awaittestUtils.form.clickSave(form);

            assert.strictEqual($('.o_data_cell').text(),inputText+"blipyopkawa");
            form.destroy();
        });

        QUnit.test('one2manywithsequencefield,overridedefault_get,bottomwhenpopup',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].turtles=[3,2,1];

            this.data.turtle.fields.turtle_int.default=10;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '<form>'+
                    //NOTE:atsomepointwewanttofixthisintheframeworksothataninvisiblefieldisnotrequired.
                    '<fieldname="turtle_int"invisible="1"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //startingcondition
            assert.strictEqual($('.o_data_cell').text(),"blipyopkawa");

            //clickaddanewline
            //savetherecord
            //checklineisatthecorrectplace

            varinputText='ninja';
            awaittestUtils.dom.click($('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput($('.o_input[name="turtle_foo"]'),inputText);
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));

            assert.strictEqual($('.o_data_cell').text(),"blipyopkawa"+inputText);

            awaittestUtils.dom.click($('.o_form_button_save'));
            assert.strictEqual($('.o_data_cell').text(),"blipyopkawa"+inputText);
            form.destroy();
        });

        QUnit.test('one2manywithsequencefield,overridedefault_get,notlastpage',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].turtles=[3,2,1];

            this.data.turtle.fields.turtle_int.default=10;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="2">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="turtle_int"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //clickaddanewline
            //checkturtle_intfornewisthecurrentmaxofthepage
            awaittestUtils.dom.click($('.o_field_x2many_list_row_adda'));
            assert.strictEqual($('.modal.o_input[name="turtle_int"]').val(),'10');
            form.destroy();
        });

        QUnit.test('one2manywithsequencefield,overridedefault_get,lastpage',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].turtles=[3,2,1];

            this.data.turtle.fields.turtle_int.default=10;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="4">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="turtle_int"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //clickaddanewline
            //checkturtle_intfornewisthecurrentmaxofthepage+1
            awaittestUtils.dom.click($('.o_field_x2many_list_row_adda'));
            assert.strictEqual($('.modal.o_input[name="turtle_int"]').val(),'22');
            form.destroy();
        });

        QUnit.test('one2manywithsequencefield,fetchname_getfromemptylist,fieldtext',asyncfunction(assert){
            //TherewasabugwhereaRPCwouldfailbecausenoroutewasset.
            //Thescenariois:
            //-createanewparentmodel,whichhasaone2many
            //-addatleast2one2manylineswhichhave:
            //    -ahandlefield
            //    -amany2one,whichisnotrequired,andwewillleaveitempty
            //-reorderthelineswiththehandle
            //->Thiswillcallaresequence,whichcallsaname_get.
            //->Withthebugthatwouldfail,ifit'sokthetestwillpass.

            //Thistestwillalsomakesurelistswith
            //FieldText(turtle_description)canbereorderedwithahandle.
            //MorespecificallythiswilltriggeraresetonaFieldText
            //whilethefieldisnotineditablemode.
            assert.expect(4);

            this.data.turtle.fields.turtle_int.default=10;
            this.data.turtle.fields.product_id.default=37;
            this.data.turtle.fields.not_required_product_id={
                string:"Product",
                type:"many2one",
                relation:'product'
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_int"widget="handle"/>'+
                    '<fieldname="turtle_foo"/>'+
                    '<fieldname="not_required_product_id"/>'+
                    '<fieldname="turtle_description"widget="text"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                viewOptions:{
                    mode:'edit',
                },
            });

            //startingcondition
            assert.strictEqual($('.o_data_cell:nth-child(2)').text(),"");

            varinputText1='relax';
            varinputText2='max';
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_input[name="turtle_foo"]'),inputText1);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_input[name="turtle_foo"]'),inputText2);
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.strictEqual($('.o_data_cell:nth-child(2)').text(),inputText1+inputText2);

            var$handles=form.$('.ui-sortable-handle');

            assert.equal($handles.length,3,'Thereshouldbe3sequencehandlers');

            awaittestUtils.dom.dragAndDrop($handles.eq(1),
                form.$('tbodytr').first(),
                {position:'top'}
            );

            assert.strictEqual($('.o_data_cell:nth-child(2)').text(),inputText2+inputText1);

            form.destroy();
        });

        QUnit.skip('one2manywithseveralpages,onchangeanddefaultorder',asyncfunction(assert){
            //Thistestreproducesaspecificscenariowhereaone2manyisdisplayed
            //overseveralpages,andhasadefaultordersuchthatarecordthat
            //wouldnormallybeonpage1isactuallyonanotherpage.Moreover,
            //thereisanonchangeonthatone2manywhichconvertsallcommands4
            //(LINK_TO)intocommands1(UPDATE),whichisstandardintheORM.
            //Thistestensuresthattherecorddisplayedonpage2isneverfully
            //read.
            assert.expect(8);

            vardata=this.data;
            data.partner.records[0].turtles=[1,2,3];
            data.turtle.records[0].partner_ids=[1];
            data.partner.onchanges={
                turtles:function(obj){
                    varres=_.map(obj.turtles,function(command){
                        if(command[0]===1){//alreadyanUPDATEcommand:donothing
                            returncommand;
                        }
                        //convertLINK_TOcommandstoUPDATEcommands
                        varid=command[1];
                        varrecord=_.findWhere(data.turtle.records,{id:id});
                        return[1,id,_.pick(record,['turtle_int','turtle_foo','partner_ids'])];
                    });
                    obj.turtles=[[5]].concat(res);
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top"limit="2"default_order="turtle_foo">'+
                    '<fieldname="turtle_int"/>'+
                    '<fieldname="turtle_foo"class="foo"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varids=args.method==='read'?'['+args.args[0]+']':'';
                    assert.step(args.method+ids);
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.strictEqual(form.$('.o_data_cell.foo').text(),'blipkawa',
                "shoulddisplaytworecordsoutofthree,inthecorrectorder");

            //editturtle_intfieldoffirstrow
            awaittestUtils.dom.click(form.$('.o_data_cell:first'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=turtle_int]'),3);
            awaittestUtils.dom.click(form.$el);

            assert.strictEqual(form.$('.o_data_cell.foo').text(),'blipkawa',
                "shouldstilldisplaythesametworecords");

            assert.verifySteps([
                'read[1]',//mainrecord
                'read[1,2,3]',//one2many(turtle_foo,allrecords)
                'read[2,3]',//one2many(allfieldsinview,recordsoffirstpage)
                'read[2,4]',//many2manyinsideone2many(partner_ids),firstpageonly
                'onchange',
                'read[1]',//AABFIXME4(draftfixingtaskid-2323491):
                            //thistest'spurposeistoassertthatthisrpcisn't
                            //done,butyetitis.Actually,itwasn'tbeforebecausemockOnChange
                            //returned[1]ascommandlist,insteadof[[6,false,[1]]],sobasically
                            //thisvaluewasignored.NowthatmockOnChangeproperlyworks,thevalue
                            //istakenintoaccountbutthebasicmodeldoesn'tcareitconcernsa
                            //recordofthesecondpage,anddoestheread.Idon'tthinkwe
                            //introducedaregressionhere,thistestwassimplywrong...
            ]);

            form.destroy();
        });

        QUnit.test('newrecord,withone2manywithmoredefaultvaluesthanlimit',asyncfunction(assert){
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="2">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                context:{default_turtles:[1,2,3]},
                viewOptions:{
                    mode:'edit',
                },
            });
            assert.strictEqual(form.$('.o_data_row').text(),'yopblip',
                'datahasbeenproperlyloaded');
            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('.o_data_row').text(),'yopblip',
                'datahasbeenproperlysaved');
            form.destroy();
        });

        QUnit.test('addanewlineafterlimitisreachedshouldbehavenicely',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[1,2,3];

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[
                        [5],
                        [1,1,{turtle_foo:"yop"}],
                        [1,2,{turtle_foo:"blip"}],
                        [1,3,{turtle_foo:"kawa"}],
                        [0,obj.turtles[3][2],{turtle_foo:"abc"}],
                    ];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treelimit="3"editable="bottom">'+
                    '<fieldname="turtle_foo"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsN(form,'.o_data_row',4,'shouldhave4datarows');
            awaittestUtils.fields.editInput(form.$('.o_input[name="turtle_foo"]'),'a');
            assert.containsN(form,'.o_data_row',4,
                'shouldstillhave4datarows(thelimitisincreasedto4)');

            form.destroy();
        });

        QUnit.test('onchangeinaone2manywithnoninlineviewonanexistingrecord',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.fields.sequence={string:'Sequence',type:'integer'};
            this.data.partner.records[0].sequence=1;
            this.data.partner.records[1].sequence=2;
            this.data.partner.onchanges={sequence:function(){}};

            this.data.partner_type.fields.partner_ids={string:"Partner",type:"one2many",relation:'partner'};
            this.data.partner_type.records[0].partner_ids=[1,2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner_type',
                data:this.data,
                arch:'<form><fieldname="partner_ids"/></form>',
                archs:{
                    'partner,false,list':'<treestring="Vendors">'+
                        '<fieldname="sequence"widget="handle"/>'+
                        '<fieldname="display_name"/>'+
                        '</tree>',
                },
                res_id:12,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{mode:'edit'},
            });

            //swap2linesintheone2many
            awaittestUtils.dom.dragAndDrop(form.$('.ui-sortable-handle:eq(1)'),form.$('tbodytr').first(),
                {position:'top'});
            assert.verifySteps(['load_views','read','read','onchange','onchange']);
            form.destroy();
        });

        QUnit.test('onchangeinaone2manywithnoninlineviewonanewrecord',asyncfunction(assert){
            assert.expect(6);

            this.data.turtle.onchanges={
                display_name:function(obj){
                    if(obj.display_name){
                        obj.turtle_int=44;
                    }
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="turtles"/></form>',
                archs:{
                    'turtle,false,list':'<treeeditable="bottom">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="turtle_int"/>'+
                        '</tree>',
                },
                mockRPC:function(route,args){
                    assert.step(args.method||route);
                    returnthis._super.apply(this,arguments);
                },
            });

            //addarowandtriggertheonchange
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_data_row.o_field_widget[name=display_name]'),'aname');

            assert.strictEqual(form.$('.o_data_row.o_field_widget[name=turtle_int]').val(),"44",
                "shouldhavetriggeredtheonchange");

            assert.verifySteps([
                'load_views',//loadsublist
                'onchange',//mainrecord
                'onchange',//subrecord
                'onchange',//editionofdisplay_nameofsubrecord
            ]);

            form.destroy();
        });

        QUnit.test('addaline,edititand"Save&New"',asyncfunction(assert){
            assert.expect(5);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree><fieldname="display_name"/></tree>'+
                    '<form><fieldname="display_name"/></form>'+
                    '</field>'+
                    '</form>',
            });

            assert.containsNone(form,'.o_data_row',
                "thereshouldbenorecordintherelation");

            //addanewrecord
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput($('.modal.o_field_widget'),'newrecord');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));

            assert.strictEqual(form.$('.o_data_row.o_data_cell').text(),'newrecord',
                "shoulddisplaythenewrecord");

            //reopenfreshlyaddedrecordandeditit
            awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell'));
            awaittestUtils.fields.editInput($('.modal.o_field_widget'),'newrecordedited');

            //saveit,andchoosetodirectlycreateanotherrecord
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:nth(1)'));

            assert.strictEqual($('.modal').length,1,
                "themodelshouldstillbeopen");
            assert.strictEqual($('.modal.o_field_widget').text(),'',
                "shouldhaveclearedtheinput");

            awaittestUtils.fields.editInput($('.modal.o_field_widget'),'anothernewrecord');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));

            assert.strictEqual(form.$('.o_data_row.o_data_cell').text(),
                'newrecordeditedanothernewrecord',"shoulddisplaythetworecords");

            form.destroy();
        });

        QUnit.test('o2maddalinecustomcontrolcreateeditable',asyncfunction(assert){
            assert.expect(5);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<control>'+
                    '<createstring="Addfood"context=""/>'+
                    '<createstring="Addpizza"context="{\'default_display_name\':\'pizza\'}"/>'+
                    '</control>'+

                    '<control>'+
                    '<createstring="Addpasta"context="{\'default_display_name\':\'pasta\'}"/>'+
                    '</control>'+

                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="display_name"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
            });

            //newcontrolscorrectlyadded
            var$td=form.$('.o_field_x2many_list_row_add');
            assert.strictEqual($td.length,1);
            assert.strictEqual($td.closest('tr').find('td').length,1);
            assert.strictEqual($td.text(),"AddfoodAddpizzaAddpasta");

            //clickaddfood
            //checkit'sempty
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda:eq(0)'));
            assert.strictEqual($('.o_data_cell').text(),"");

            //clickaddpizza
            //savethemodal
            //checkit'spizza
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda:eq(1)'));
            //clickaddpasta
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda:eq(2)'));
            awaittestUtils.form.clickSave(form);
            assert.strictEqual($('.o_data_cell').text(),"pizzapasta");

            form.destroy();
        });

        QUnit.test('o2maddalinecustomcontrolcreatenon-editable',asyncfunction(assert){
            assert.expect(6);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<control>'+
                    '<createstring="Addfood"context=""/>'+
                    '<createstring="Addpizza"context="{\'default_display_name\':\'pizza\'}"/>'+
                    '</control>'+

                    '<control>'+
                    '<createstring="Addpasta"context="{\'default_display_name\':\'pasta\'}"/>'+
                    '</control>'+

                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '<form>'+
                    '<fieldname="display_name"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
            });

            //newcontrolscorrectlyadded
            var$td=form.$('.o_field_x2many_list_row_add');
            assert.strictEqual($td.length,1);
            assert.strictEqual($td.closest('tr').find('td').length,1);
            assert.strictEqual($td.text(),"AddfoodAddpizzaAddpasta");

            //clickaddfood
            //checkit'sempty
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda:eq(0)'));
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            assert.strictEqual($('.o_data_cell').text(),"");

            //clickaddpizza
            //savethemodal
            //checkit'spizza
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda:eq(1)'));
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            assert.strictEqual($('.o_data_cell').text(),"pizza");

            //clickaddpasta
            //savethewholerecord
            //checkit'spizzapasta
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda:eq(2)'));
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            assert.strictEqual($('.o_data_cell').text(),"pizzapasta");

            form.destroy();
        });

        QUnit.test('o2maddalinecustomcontrolcreatealignwithhandle',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            //controlscorrectlyadded,atonecolumnoffsetwhenhandleispresent
            var$tr=form.$('.o_field_x2many_list_row_add').closest('tr');
            assert.strictEqual($tr.find('td').length,2);
            assert.strictEqual($tr.find('td:eq(0)').text(),"");
            assert.strictEqual($tr.find('td:eq(1)').text(),"Addaline");

            form.destroy();
        });

        QUnit.test('one2manyformviewwithactionbutton',asyncfunction(assert){
            //oncetheactionbuttonisclicked,therecordisreloaded(viathe
            //on_closehandler,executedbecausethepythonmethoddoesnotreturn
            //anyaction,oranir.action.act_window_close);thistestensuresthat
            //itreloadsthefieldsoftheopenedview(i.e.theforminthiscase).
            //Seehttps://github.com/flectra/flectra/issues/24189
            assert.expect(7);

            vardata=this.data;
            data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:data,
                res_id:1,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree><fieldname="display_name"/></tree>'+
                    '<form>'+
                    '<buttontype="action"string="SetTimmy"/>'+
                    '<fieldname="timmy"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                },
                intercepts:{
                    execute_action:function(ev){
                        data.partner.records[1].display_name='newname';
                        data.partner.records[1].timmy=[12];
                        ev.data.on_closed();
                    },
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row',
                "thereshouldbeonerecordintheone2many");
            assert.strictEqual(form.$('.o_data_cell').text(),'secondrecord',
                "initialdisplay_nameofo2mrecordshouldbecorrect");

            //openone2manyrecordinformview
            awaittestUtils.dom.click(form.$('.o_data_cell:first'));
            assert.strictEqual($('.modal.o_form_view').length,1,
                "shouldhaveopenedtheformviewinadialog");
            assert.strictEqual($('.modal.o_form_view.o_data_row').length,0,
                "thereshouldbenorecordinthemany2many");

            //clickontheactionbutton
            awaittestUtils.dom.click($('.modal.o_form_viewbutton'));
            assert.strictEqual($('.modal.o_data_row').length,1,
                "fieldsintheo2mformviewshouldhavebeenread");
            assert.strictEqual($('.modal.o_data_cell').text(),'gold',
                "many2manysubrecordshouldhavebeenfetched");

            //savethedialog
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

            assert.strictEqual(form.$('.o_data_cell').text(),'newname',
                "fieldsintheo2mlistviewshouldhavebeenreadaswell");

            form.destroy();
        });

        QUnit.test('onchangeaffectinginlineunopenedlistview',asyncfunction(assert){
            //whenwegotonchangeresultforfieldsofrecordthatwerenot
            //alreadyavailablebecausetheywereinainlineviewnotalready
            //opened,inagivenconfigurationthechangewereappliedignoring
            //existingdata,thusalineofaone2manyfieldinsideaone2many
            //fieldcouldbeduplicatedunexplectedly
            assert.expect(5);

            varnumUserOnchange=0;

            this.data.user.onchanges={
                partner_ids:function(obj){
                    if(numUserOnchange===0){
                        //simulateproperserveronchangeaftersaveofmodalwithnewrecord
                        obj.partner_ids=[
                            [5],
                            [1,1,{
                                display_name:'firstrecord',
                                turtles:[
                                    [5],
                                    [1,2,{'display_name':'donatello'}],
                                ],
                            }],
                            [1,2,{
                                display_name:'secondrecord',
                                turtles:[
                                    [5],
                                    obj.partner_ids[1][2].turtles[0],
                                ],
                            }],
                        ];
                    }
                    numUserOnchange++;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'user',
                data:this.data,
                arch:'<form><sheet><group>'+
                    '<fieldname="partner_ids">'+
                    '<form>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group></sheet></form>',
                res_id:17,
            });

            //addaturtleonsecondpartner
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_data_row:eq(1)'));
            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));
            $('.modalinput[name="display_name"]').val('michelangelo').change();
            awaittestUtils.dom.click($('.modal.btn-primary'));
            //openfirstpartnersochangesfrompreviousactionareapplied
            awaittestUtils.dom.click(form.$('.o_data_row:eq(0)'));
            awaittestUtils.dom.click($('.modal.btn-primary'));
            awaittestUtils.form.clickSave(form);

            assert.strictEqual(numUserOnchange,2,
                'thereshould2andonly2onchangefromclosingthepartnermodal');

            awaittestUtils.dom.click(form.$('.o_data_row:eq(0)'));
            assert.strictEqual($('.modal.o_data_row').length,1,
                'only1turtleforfirstpartner');
            assert.strictEqual($('.modal.o_data_row').text(),'donatello',
                'firstpartnerturtleisdonatello');
            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

            awaittestUtils.dom.click(form.$('.o_data_row:eq(1)'));
            assert.strictEqual($('.modal.o_data_row').length,1,
                'only1turtleforsecondpartner');
            assert.strictEqual($('.modal.o_data_row').text(),'michelangelo',
                'secondpartnerturtleismichelangelo');
            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

            form.destroy();
        });

        QUnit.test('clickonURLshouldnotopentherecord',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].turtles=[1];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="display_name"widget="email"/>'+
                    '<fieldname="turtle_foo"widget="url"/>'+
                    '</tree>'+
                    '<form></form>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.dom.click(form.$('.o_email_cella'));
            assert.strictEqual($('.modal.o_form_view').length,0,
                'clickshouldnotopenthemodal');

            awaittestUtils.dom.click(form.$('.o_url_cella'));
            assert.strictEqual($('.modal.o_form_view').length,0,
                'clickshouldnotopenthemodal');
            form.destroy();
        });

        QUnit.test('createandeditonm2oino2m,andpressESCAPE',asyncfunction(assert){
            assert.expect(4);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="top">'+
                    '<fieldname="turtle_trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<form><fieldname="display_name"/></form>',
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsOnce(form,'.o_selected_row',
                "shouldhavecreateanewrowinedition");

            awaittestUtils.fields.many2one.createAndEdit('turtle_trululu',"ABC");

            assert.strictEqual($('.modal.o_form_view').length,1,
                "shouldhaveopenedaformviewinadialog");

            awaittestUtils.fields.triggerKeydown($('.modal.o_form_view.o_field_widget[name=display_name]'),'escape');

            assert.strictEqual($('.modal.o_form_view').length,0,
                "shouldhaveclosedthedialog");
            assert.containsOnce(form,'.o_selected_row',
                "newrowshouldstillbepresent");

            form.destroy();
        });

        QUnit.test('one2manyaddalineshouldnotcrashiforderedResIDsisnotset',asyncfunction(assert){
            //Thereisnoassertion,thecodewilljustcrashbeforethebugfix.
            assert.expect(0);

            this.data.partner.records[0].turtles=[];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<header>'+
                    '<buttonname="post"type="object"string="Validate"class="oe_highlight"/>'+
                    '</header>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                viewOptions:{
                    mode:'edit',
                },
                intercepts:{
                    execute_action:function(event){
                        event.data.on_fail();
                    },
                },
            });

            awaittestUtils.dom.click($('button[name="post"]'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            form.destroy();
        });

        QUnit.test('one2manyshortcuttabshouldnotcrashwhenthereisnoinputwidget',asyncfunction(assert){
            assert.expect(2);

            //createaone2manyviewwhichhasnoinput(only1textareainthiscase)
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"widget="text"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //addarow,fillit,thentriggerthetabshortcut
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_input[name="turtle_foo"]'),'ninja');
            awaittestUtils.fields.triggerKeydown(form.$('.o_input[name="turtle_foo"]'),'tab');

            assert.strictEqual(form.$('.o_field_text').text(),'blipninja',
                'currentlineshouldbesaved');
            assert.containsOnce(form,'textarea.o_field_text',
                'newlineshouldbecreated');

            form.destroy();
        });

        QUnit.test('one2manywithonchange,requiredfield,shortcutenter',asyncfunction(assert){
            assert.expect(5);

            this.data.turtle.onchanges={
                turtle_foo:function(){},
            };

            varprom;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnPromise.resolve(prom).then(_.constant(result));
                    }
                    returnresult;
                },
                //simulatewhathappensintheclient:
                //thenewvalueisn'tnotifieddirectlytothemodel
                fieldDebounce:5000,
            });

            varvalue="hello";

            //addanewline
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            //wewanttoaddadelaytosimulateanonchange
            prom=testUtils.makeTestPromise();

            //writesomethinginthefield
            var$input=form.$('input[name="turtle_foo"]');
            awaittestUtils.fields.editInput($input,value);
            awaittestUtils.fields.triggerKeydown($input,'enter');

            //checkthatnothingchangedbeforetheonchangefinished
            assert.strictEqual($input.val(),value,"inputcontentshouldn'tchange");
            assert.containsOnce(form,'.o_data_row',
                "shouldstillcontainonlyonerow");

            //unlockonchange
            prom.resolve();
            awaittestUtils.nextTick();

            //checkthecurrentlineisaddedwiththecorrectcontentandanewlineiseditable
            assert.strictEqual(form.$('td.o_data_cell').text(),value);
            assert.strictEqual(form.$('input[name="turtle_foo"]').val(),'');
            assert.containsN(form,'.o_data_row',2,
                "shouldnowcontaintworows");

            form.destroy();
        });

        QUnit.test('nodeadlockwhenleavingaone2manylinewithuncommittedchanges',asyncfunction(assert){
            //Beforeunselectingao2mline,fieldwidgetsareaskedtocommittheirchanges(newvalues
            //thattheywouldn'thavesenttothemodelyet).Thistestisaddedalongsideabugfix
            //ensuringthatwedon'tendupinadeadlockwhenawidgetactuallyhassomechangesto
            //commitatthatmoment.
            assert.expect(9);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
                //wesetafieldDebouncetopreciselymockthebehaviorofthewebclient:changesare
                //notsenttothemodelatkeystrokes,butwhentheinputisleft
                fieldDebounce:5000,
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=turtles]input'),'somefoovalue');

            //clicktoaddasecondrowtounselectthecurrentone,thensave
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.form.clickSave(form);

            assert.containsOnce(form,'.o_form_readonly',
                "formviewshouldbeinreadonly");
            assert.strictEqual(form.$('.o_data_row').text(),'somefoovalue',
                "foofieldshouldhavecorrectvalue");
            assert.verifySteps([
                'onchange',//mainrecord
                'onchange',//line1
                'onchange',//line2
                'create',
                'read',//mainrecord
                'read',//line1
            ]);

            form.destroy();
        });

        QUnit.test('one2manywithextrafieldfromservernotinform',asyncfunction(assert){
            assert.expect(6);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="datetime"/>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner,false,form':'<form>'+
                        '<fieldname="display_name"/>'+
                        '</form>'
                },
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        args.args[1].p[0][2].datetime='2018-04-0512:00:00';
                    }
                    returnthis._super.apply(this,arguments);
                }
            });

            awaittestUtils.form.clickEdit(form);

            varx2mList=form.$('.o_field_x2many_list[name=p]');

            //Addarecordinthelist
            awaittestUtils.dom.click(x2mList.find('.o_field_x2many_list_row_adda'));

            varmodal=$('.modal-lg');

            varnameInput=modal.find('input.o_input[name=display_name]');
            awaittestUtils.fields.editInput(nameInput,'michelangelo');

            //Savetherecordinthemodal(thoughitisstillvirtual)
            awaittestUtils.dom.click(modal.find('.btn-primary').first());

            assert.equal(x2mList.find('.o_data_row').length,1,
                'Thereshouldbe1recordsinthex2mlist');

            varnewlyAdded=x2mList.find('.o_data_row').eq(0);

            assert.equal(newlyAdded.find('.o_data_cell').first().text(),'',
                'Thecreate_datefieldshouldbeempty');
            assert.equal(newlyAdded.find('.o_data_cell').eq(1).text(),'michelangelo',
                'Thedisplaynamefieldshouldhavetherightvalue');

            //Savethewholething
            awaittestUtils.form.clickSave(form);

            x2mList=form.$('.o_field_x2many_list[name=p]');

            //RedoassertsinROmodeaftersaving
            assert.equal(x2mList.find('.o_data_row').length,1,
                'Thereshouldbe1recordsinthex2mlist');

            newlyAdded=x2mList.find('.o_data_row').eq(0);

            assert.equal(newlyAdded.find('.o_data_cell').first().text(),'04/05/201812:00:00',
                'Thecreate_datefieldshouldhavetherightvalue');
            assert.equal(newlyAdded.find('.o_data_cell').eq(1).text(),'michelangelo',
                'Thedisplaynamefieldshouldhavetherightvalue');

            form.destroy();
        });

        QUnit.test('one2manyinvisibledependsonparentfield',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="product_id"/>'+
                    '</group>'+
                    '<notebook>'+
                    '<pagestring="Partnerpage">'+
                    '<fieldname="bar"/>'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="foo"attrs="{\'column_invisible\':[(\'parent.product_id\',\'!=\',False)]}"/>'+
                    '<fieldname="bar"attrs="{\'column_invisible\':[(\'parent.bar\',\'=\',False)]}"/>'+
                    '</tree>'+
                    '</field>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });
            assert.containsN(form,'th',2,
                "shouldbe2columnsintheone2many");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_many2one[name="product_id"]input'));
            awaittestUtils.dom.click($('li.ui-menu-itema:contains(xpad)').trigger('mouseenter'));
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
                "shouldbe1columnwhentheproduct_idisset");
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2one[name="product_id"]input'),
                '','keyup');
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsN(form,'th:not(.o_list_record_remove_header)',2,
                "shouldbe2columnsintheone2manywhenproduct_idisnotset");
            awaittestUtils.dom.click(form.$('.o_field_boolean[name="bar"]input'));
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
                "shouldbe1columnafterthevaluechange");
            form.destroy();
        });

        QUnit.test('column_invisibleattrsonabuttoninaone2manylist',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.records[0].p=[2];
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="product_id"/>
                        <fieldname="p">
                            <tree>
                                <fieldname="foo"/>
                                <buttonname="abc"string="Doit"class="some_button"attrs="{'column_invisible':[('parent.product_id','=',False)]}"/>
                            </tree>
                        </field>
                    </form>`,
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'');
            assert.containsN(form,'.o_list_tableth',2);//foo+trashbin
            assert.containsNone(form,'.some_button');

            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'xphone');
            assert.containsN(form,'.o_list_tableth',3);//foo+button+trashbin
            assert.containsOnce(form,'.some_button');

            form.destroy();
        });

        QUnit.test('column_invisibleattrsonadjacentbuttons',asyncfunction(assert){
            assert.expect(14);

            this.data.partner.records[0].p=[2];
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="product_id"/>
                        <fieldname="trululu"/>
                        <fieldname="p">
                            <tree>
                                <buttonname="abc1"string="Doit1"class="some_button1"/>
                                <buttonname="abc2"string="Doit2"class="some_button2"attrs="{'column_invisible':[('parent.product_id','!=',False)]}"/>
                                <fieldname="foo"/>
                                <buttonname="abc3"string="Doit3"class="some_button3"attrs="{'column_invisible':[('parent.product_id','!=',False)]}"/>
                                <buttonname="abc4"string="Doit4"class="some_button4"attrs="{'column_invisible':[('parent.trululu','!=',False)]}"/>
                            </tree>
                        </field>
                    </form>`,
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'');
            assert.strictEqual(form.$('.o_field_widget[name=trululu]input').val(),'aaa');
            assert.containsN(form,'.o_list_tableth',4);//buttongroup1+foo+buttongroup2+trashbin
            assert.containsOnce(form,'.some_button1');
            assert.containsOnce(form,'.some_button2');
            assert.containsOnce(form,'.some_button3');
            assert.containsNone(form,'.some_button4');

            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'xphone');
            assert.strictEqual(form.$('.o_field_widget[name=trululu]input').val(),'aaa');
            assert.containsN(form,'.o_list_tableth',3);//buttongroup1+foo+trashbin
            assert.containsOnce(form,'.some_button1');
            assert.containsNone(form,'.some_button2');
            assert.containsNone(form,'.some_button3');
            assert.containsNone(form,'.some_button4');

            form.destroy();
        });

        QUnit.test('one2manycolumnvisiblitydependsononchangeofparentfield',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].p=[2];
            this.data.partner.records[0].bar=false;

            this.data.partner.onchanges.p=function(obj){
                //setbartotruewhenlineisadded
                if(obj.p.length>1&&obj.p[1][2].foo==='Newline'){
                    obj.bar=true;
                }
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"attrs="{\'column_invisible\':[(\'parent.bar\',\'=\',False)]}"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            //barisfalsesothereshouldbe1column
            assert.containsOnce(form,'th',
                "shouldbeonly1column('foo')intheone2many");
            assert.containsOnce(form,'.o_list_view.o_data_row',"shouldcontainonerow");

            awaittestUtils.form.clickEdit(form);

            //addanewo2mrecord
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            form.$('.o_field_one2manyinput:first').focus();
            awaittestUtils.fields.editInput(form.$('.o_field_one2manyinput:first'),'Newline');
            awaittestUtils.dom.click(form.$el);

            assert.containsN(form,'th:not(.o_list_record_remove_header)',2,"shouldbe2columns('foo'+'int_field')");

            form.destroy();
        });

        QUnit.test('one2manycolumn_invisibleonviewnotinline',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="product_id"/>'+
                    '</group>'+
                    '<notebook>'+
                    '<pagestring="Partnerpage">'+
                    '<fieldname="bar"/>'+
                    '<fieldname="p"/>'+
                    '</page>'+
                    '</notebook>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner,false,list':'<tree>'+
                        '<fieldname="foo"attrs="{\'column_invisible\':[(\'parent.product_id\',\'!=\',False)]}"/>'+
                        '<fieldname="bar"attrs="{\'column_invisible\':[(\'parent.bar\',\'=\',False)]}"/>'+
                        '</tree>',
                },
            });
            assert.containsN(form,'th',2,
                "shouldbe2columnsintheone2many");
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_field_many2one[name="product_id"]input'));
            awaittestUtils.dom.click($('li.ui-menu-itema:contains(xpad)').trigger('mouseenter'));
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
                "shouldbe1columnwhentheproduct_idisset");
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2one[name="product_id"]input'),
                '','keyup');
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsN(form,'th:not(.o_list_record_remove_header)',2,
                "shouldbe2columnsintheone2manywhenproduct_idisnotset");
            awaittestUtils.dom.click(form.$('.o_field_boolean[name="bar"]input'));
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
                "shouldbe1columnafterthevaluechange");
            form.destroy();
        });

        QUnit.test('fieldcontextiscorrectlypassedtox2msubviews',asyncfunction(assert){
            assert.expect(2);

             varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                        '<fieldname="turtles"context="{\'some_key\':1}">'+
                            '<kanban>'+
                                '<templates>'+
                                    '<tt-name="kanban-box">'+
                                        '<div>'+
                                            '<tt-if="context.some_key">'+
                                                '<fieldname="turtle_foo"/>'+
                                            '</t>'+
                                        '</div>'+
                                    '</t>'+
                                '</templates>'+
                            '</kanban>'+
                        '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,1,
                "shouldhavearecordintherelation");
            assert.strictEqual(form.$('.o_kanban_recordspan:contains(blip)').length,1,
                "conditioninthekanbantemplateshouldhavebeencorrectlyevaluated");

            form.destroy();
        });

        QUnit.test('one2manykanbanwithwidgethandle',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].turtles=[1,2,3];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                        '<fieldname="turtles">'+
                            '<kanban>'+
                                '<fieldname="turtle_int"widget="handle"/>'+
                                '<templates>'+
                                    '<tt-name="kanban-box">'+
                                        '<div><fieldname="turtle_foo"/></div>'+
                                    '</t>'+
                                '</templates>'+
                            '</kanban>'+
                        '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1],{
                            turtles:[
                                [1,2,{turtle_int:0}],
                                [1,3,{turtle_int:1}],
                                [1,1,{turtle_int:2}],
                            ],
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
            });

            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').text(),'yopblipkawa');
            assert.doesNotHaveClass(form.$('.o_field_one2many.o_kanban_view'),'ui-sortable');

            awaittestUtils.form.clickEdit(form);

            assert.hasClass(form.$('.o_field_one2many.o_kanban_view'),'ui-sortable');

            var$record=form.$('.o_field_one2many[name=turtles].o_kanban_view.o_kanban_record:first');
            var$to=form.$('.o_field_one2many[name=turtles].o_kanban_view.o_kanban_record:nth-child(3)');
            awaittestUtils.dom.dragAndDrop($record,$to,{position:"bottom"});

            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').text(),'blipkawayop');

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('one2manyeditablelist:editandclickonaddaline',asyncfunction(assert){
            assert.expect(9);

            this.data.turtle.onchanges={
                turtle_int:function(){},
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                        '<fieldname="turtles">'+
                            '<treeeditable="bottom"><fieldname="turtle_int"/></tree>'+
                        '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        assert.step('onchange');
                    }
                    returnthis._super.apply(this,arguments);
                },
                //inthistest,wewanttotoaccuratelymockwhatreallyhappens,thatis,input
                //fieldsonlytriggertheirchangeson'change'event,noton'input'
                fieldDebounce:100000,
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.containsOnce(form,'.o_data_row');

            //editfirstrow
            awaittestUtils.dom.click(form.$('.o_data_row:first.o_data_cell:first'));
            assert.hasClass(form.$('.o_data_row:first'),'o_selected_row');
            awaittestUtils.fields.editInput(form.$('.o_selected_rowinput[name=turtle_int]'),'44');

            assert.verifySteps([]);
            //simulatealongclickon'Addaline'(mousedown[delay]mouseupandclickevents)
            var$addLine=form.$('.o_field_x2many_list_row_adda');
            testUtils.dom.triggerEvents($addLine,'mousedown');
            //mousedownissupposedtotriggerthechangeeventontheeditedinput,butitdoesn't
            //inthetestenvironment,foranunknownreason,sowetriggeritmanuallytoreproduce
            //whatreallyhappens
            testUtils.dom.triggerEvents(form.$('.o_selected_rowinput[name=turtle_int]'),'change');
            awaittestUtils.nextTick();

            //releasetheclick
            awaittestUtils.dom.triggerEvents($addLine,['mouseup','click']);
            assert.verifySteps(['onchange','onchange']);

            assert.containsN(form,'.o_data_row',2);
            assert.strictEqual(form.$('.o_data_row:first').text(),'44');
            assert.hasClass(form.$('.o_data_row:nth(1)'),'o_selected_row');

            form.destroy();
        });

        QUnit.test('many2manysinsideaone2manyarefetchedinbatchafteronchange',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.onchanges={
                turtles:function(obj){
                    obj.turtles=[
                        [5],
                        [1,1,{
                            turtle_foo:"leonardo",
                            partner_ids:[[4,2]],
                        }],
                        [1,2,{
                            turtle_foo:"donatello",
                            partner_ids:[[4,2],[4,4]],
                        }],
                    ];
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                            '<fieldname="turtles">'+
                                '<treeeditable="bottom">'+
                                    '<fieldname="turtle_foo"/>'+
                                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                                '</tree>'+
                            '</field>'+
                        '</form>',
                enableBasicModelBachedRPCs:true,
                mockRPC:function(route,args){
                    assert.step(args.method||route);
                    if(args.method==='read'){
                        assert.deepEqual(args.args[0],[2,4],
                            'shouldreadthepartner_idsonce,batched');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.containsN(form,'.o_data_row',2);
            assert.strictEqual(form.$('.o_field_widget[name="partner_ids"]').text().replace(/\s/g,''),
                "secondrecordsecondrecordaaa");

            assert.verifySteps(['onchange','read']);

            form.destroy();
        });

        QUnit.test('twoone2manyfieldswithsamerelationandonchanges',asyncfunction(assert){
            //thistestsimulatesthepresenceoftwoone2manyfieldswithonchanges,suchthat
            //changestothefirsto2marerepercutedonthesecondone
            assert.expect(6);

            this.data.partner.fields.turtles2={
                string:"Turtles2",
                type:"one2many",
                relation:'turtle',
                relation_field:'turtle_trululu',
            };
            this.data.partner.onchanges={
                turtles:function(obj){
                    //whenweaddalinetoturtles,addsamelinetoturtles2
                    if(obj.turtles.length){
                        obj.turtles=[[5]].concat(obj.turtles);
                        obj.turtles2=obj.turtles;
                    }
                },
                turtles2:function(obj){
                    //simulateanonchangeonturtles2aswell
                    if(obj.turtles2.length){
                        obj.turtles2=[[5]].concat(obj.turtles2);
                    }
                }
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                        '<fieldname="turtles">'+
                            '<treeeditable="bottom"><fieldname="name"required="1"/></tree>'+
                        '</field>'+
                        '<fieldname="turtles2">'+
                            '<treeeditable="bottom"><fieldname="name"required="1"/></tree>'+
                        '</field>'+
                    '</form>',
            });

            //triggerfirstonchangebyaddingalineinturtlesfield(shouldaddalineinturtles2)
            awaittestUtils.dom.click(form.$('.o_field_widget[name="turtles"].o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name="turtles"].o_field_widget[name="name"]'),'ABC');

            assert.containsOnce(form,'.o_field_widget[name="turtles"].o_data_row',
                'lineoffirsto2mshouldhavebeencreated');
            assert.containsOnce(form,'.o_field_widget[name="turtles2"].o_data_row',
                'lineofsecondo2mshouldhavebeencreated');

            //addalineinturtles2
            awaittestUtils.dom.click(form.$('.o_field_widget[name="turtles2"].o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name="turtles2"].o_field_widget[name="name"]'),'DEF');

            assert.containsOnce(form,'.o_field_widget[name="turtles"].o_data_row',
                'weshouldstillhave1lineinturtles');
            assert.containsN(form,'.o_field_widget[name="turtles2"].o_data_row',2,
                'weshouldhave2linesinturtles2');
            assert.hasClass(form.$('.o_field_widget[name="turtles2"].o_data_row:nth(1)'),'o_selected_row',
                'secondrowshouldbeinedition');

            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('.o_field_widget[name="turtles2"].o_data_row').text(),'ABCDEF');

            form.destroy();
        });

        QUnit.test('columnwidthsarekeptwhenaddingfirstrecordino2m',asyncfunction(assert){
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                            '<fieldname="p">'+
                                '<treeeditable="top">'+
                                    '<fieldname="date"/>'+
                                    '<fieldname="foo"/>'+
                                '</tree>'+
                            '</field>'+
                        '</form>',
            });

            varwidth=form.$('th[data-name="date"]')[0].offsetWidth;

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsOnce(form,'.o_data_row');
            assert.strictEqual(form.$('th[data-name="date"]')[0].offsetWidth,width);

            form.destroy();
        });

        QUnit.test('columnwidthsarekeptwheneditingarecordino2m',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                            '<fieldname="p">'+
                                '<treeeditable="top">'+
                                    '<fieldname="date"/>'+
                                    '<fieldname="foo"/>'+
                                '</tree>'+
                            '</field>'+
                        '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            varwidth=form.$('th[data-name="date"]')[0].offsetWidth;

            awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell:first'));

            assert.strictEqual(form.$('th[data-name="date"]')[0].offsetWidth,width);

            varlongVal='Loremipsumdolorsitamet,consecteturadipiscingelit.Sedblandit,'+
                'justonectinciduntfeugiat,mijustosuscipitlibero,sitamettempusipsum'+
                'purusbibendumest.';
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),longVal);

            assert.strictEqual(form.$('th[data-name="date"]')[0].offsetWidth,width);

            form.destroy();
        });

        QUnit.test('columnwidthsarekeptwhenremovelastrecordino2m',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                            '<fieldname="p">'+
                                '<treeeditable="top">'+
                                    '<fieldname="date"/>'+
                                    '<fieldname="foo"/>'+
                                '</tree>'+
                            '</field>'+
                        '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            varwidth=form.$('th[data-name="date"]')[0].offsetWidth;

            awaittestUtils.dom.click(form.$('.o_data_row.o_list_record_remove'));

            assert.strictEqual(form.$('th[data-name="date"]')[0].offsetWidth,width);

            form.destroy();
        });

        QUnit.test('columnwidthsarecorrectaftertogglingoptionalfields',asyncfunction(assert){
            assert.expect(2);

            varRamStorageService=AbstractStorageService.extend({
                storage:newRamStorage(),
            });

            this.data.partner.records[0].p=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                            '<fieldname="p">'+
                                '<treeeditable="top">'+
                                    '<fieldname="date"required="1"/>'+//wewantthelisttoremainempty
                                    '<fieldname="foo"/>'+
                                    '<fieldname="int_field"optional="1"/>'+
                                '</tree>'+
                            '</field>'+
                        '</form>',
                services:{
                    local_storage:RamStorageService,
                },
            });

            //datefieldshaveanhardcodedwidth,whichapplywhenthereisno
            //record,andshouldbekeptafterwards
            letwidth=form.$('th[data-name="date"]')[0].offsetWidth;

            //createarecordtostorethecurrentwidths,butdiscarditdirectlytokeep
            //thelistempty(otherwise,thebrowserautomaticallycomputestheoptimalwidths)
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.strictEqual(form.$('th[data-name="date"]')[0].offsetWidth,width);

            awaittestUtils.dom.click(form.$('.o_optional_columns_dropdown_toggle'));
            awaittestUtils.dom.click(form.$('div.o_optional_columnsdiv.dropdown-iteminput'));

            assert.strictEqual(form.$('th[data-name="date"]')[0].offsetWidth,width);

            form.destroy();
        });

        QUnit.test('editableone2manylistwithoe_read_onlybutton',asyncfunction(assert){
            assert.expect(9);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<form>
                        <fieldname="turtles">
                            <treeeditable="bottom">
                                <fieldname="turtle_foo"/>
                                <buttonname="do_it"type="object"class="oe_read_only"/>
                            </tree>
                        </field>
                    </form>`,
                res_id:1,
            });

            assert.containsN(form,'.o_list_viewtheadth:visible',2);
            assert.containsN(form,'.o_list_viewtbody.o_data_rowtd:visible',2);
            assert.containsN(form,'.o_list_viewtfoottd:visible',2);
            assert.containsNone(form,'.o_list_record_remove_header');

            awaittestUtils.form.clickEdit(form);

            //shouldhavetwovisiblecolumnsinedit:foo+trash
            assert.hasClass(form.$('.o_form_view'),'o_form_editable');
            assert.containsN(form,'.o_list_viewtheadth:visible',2);
            assert.containsN(form,'.o_list_viewtbody.o_data_rowtd:visible',2);
            assert.containsN(form,'.o_list_viewtfoottd:visible',2);
            assert.containsOnce(form,'.o_list_record_remove_header');

            form.destroy();
        });

        QUnit.test('one2manyresetbyonchange(ofanotherfield)whilebeingedited',asyncfunction(assert){
            //Inthistest,wehaveamany2oneandaone2many.Themany2onehasanonchangethat
            //updatesthevalueoftheone2many.Wesetanewvaluetothemany2one(name_create)
            //suchthattheonchangeisdelayed.Duringthename_create,weclicktoaddanewrow
            //totheone2many.Afterawhile,weunlockthename_create,whichtriggerstheonchange
            //andresetstheone2many.Attheend,wewanttherowtobeinedition.
            assert.expect(3);

            constprom=testUtils.makeTestPromise();
            this.data.partner.onchanges={
                trululu:obj=>{
                    obj.p=[[5]].concat(obj.p);
                },
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="trululu"/>
                        <fieldname="p">
                            <treeeditable="top"><fieldname="product_id"required="1"/></tree>
                        </field>
                    </form>`,
                mockRPC:function(route,args){
                    constresult=this._super.apply(this,arguments);
                    if(args.method==='name_create'){
                        returnprom.then(()=>result);
                    }
                    returnresult;
                },
            });

            //setanewvaluefortrululu(willdelaytheonchange)
            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{search:'newvalue'});

            //addarowinp
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsNone(form,'.o_data_row');

            //resolvethename_createtotriggertheonchange,andtheresetofp
            prom.resolve();
            awaittestUtils.nextTick();
            //useofowlCompatibilityNextTickbecausewehavetwosequentialupdatesofthe
            //fieldX2Many:onebecauseoftheonchange,andonebecauseoftheclickonaddaline.
            //AsanupdaterequiresanupdateoftheControlPanel,whichisanOwlComponent,and
            //waitsforit,weneedtowaitfortwoanimationframesbeforeseeingthenewlinein
            //theDOM
            awaittestUtils.owlCompatibilityNextTick();
            assert.containsOnce(form,'.o_data_row');
            assert.hasClass(form.$('.o_data_row'),'o_selected_row');

            form.destroy();
        });

        QUnit.skip('one2manywithmany2many_tagsinlistandlistinformwithalimit',asyncfunction(assert){
            //Thistestisskippedfornow,asitdoesn'twork,anditcan'tbefixedinthecurrent
            //architecture(withoutlargechanges).However,thisisunlikelytohappenasthedefault
            //limitis80,anditwouldbeuselesstodisplaysomanyrecordswithamany2many_tags
            //widget.Soitwouldbeniceifwecouldmakeitworkinthefuture,butit'snobig
            //dealfornow.
            assert.expect(6);

            this.data.partner.records[0].p=[1];
            this.data.partner.records[0].turtles=[1,2,3];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p">
                            <tree>
                                <fieldname="turtles"widget="many2many_tags"/>
                            </tree>
                            <form>
                                <fieldname="turtles">
                                    <treelimit="2"><fieldname="display_name"/></tree>
                                </field>
                            </form>
                        </field>
                    </form>`,
                res_id:1,
            });

            assert.containsOnce(form,'.o_field_widget[name=p].o_data_row');
            assert.containsN(form,'.o_data_row.o_field_many2manytags.badge',3);

            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsN(document.body,'.modal.o_field_widget[name=turtles].o_data_row',2);
            assert.isVisible($('.modal.o_field_x2many_list.o_pager'));
            assert.strictEqual($(".modal.o_field_x2many_list.o_pager").text().trim(),'1-2/3');

            form.destroy();
        });

        QUnit.test('one2manywithmany2many_tagsinlistandlistinform,andonchange',asyncfunction(assert){
            assert.expect(8);

            this.data.partner.onchanges={
                bar:function(obj){
                    obj.p=[
                        [5],
                        [0,0,{
                            turtles:[
                                [5],
                                [0,0,{
                                    display_name:'newturtle',
                                }]
                            ],
                        }]
                    ];
                },
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p">
                            <tree>
                                <fieldname="turtles"widget="many2many_tags"/>
                            </tree>
                            <form>
                                <fieldname="turtles">
                                    <treeeditable="bottom"><fieldname="display_name"/></tree>
                                </field>
                            </form>
                        </field>
                    </form>`,
            });

            assert.containsOnce(form,'.o_field_widget[name=p].o_data_row');
            assert.containsOnce(form,'.o_data_row.o_field_many2manytags.badge');

            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.containsOnce(document.body,'.modal.o_field_widget[name=turtles].o_data_row');
            assert.strictEqual($('.modal.o_field_widget[name=turtles].o_data_row').text(),'newturtle');

            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));
            assert.containsN(document.body,'.modal.o_field_widget[name=turtles].o_data_row',2);
            assert.strictEqual($('.modal.o_field_widget[name=turtles].o_data_row:first').text(),'newturtle');
            assert.hasClass($('.modal.o_field_widget[name=turtles].o_data_row:nth(1)'),'o_selected_row');

            form.destroy();
        });

        QUnit.test('one2manywithmany2many_tagsinlistandlistinform,andonchange(2)',asyncfunction(assert){
            assert.expect(7);

            this.data.partner.onchanges={
                bar:function(obj){
                    obj.p=[
                        [5],
                        [0,0,{
                            turtles:[
                                [5],
                                [0,0,{
                                    display_name:'newturtle',
                                }]
                            ],
                        }]
                    ];
                },
            };
            this.data.turtle.onchanges={
                turtle_foo:function(obj){
                    obj.display_name=obj.turtle_foo;
                },
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p">
                            <tree>
                                <fieldname="turtles"widget="many2many_tags"/>
                            </tree>
                            <form>
                                <fieldname="turtles">
                                    <treeeditable="bottom">
                                        <fieldname="turtle_foo"required="1"/>
                                    </tree>
                                </field>
                            </form>
                        </field>
                    </form>`,
            });

            assert.containsOnce(form,'.o_field_widget[name=p].o_data_row');

            awaittestUtils.dom.click(form.$('.o_data_row'));

            assert.containsOnce(document.body,'.modal.o_form_view');

            awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));
            assert.containsN(document.body,'.modal.o_field_widget[name=turtles].o_data_row',2);

            awaittestUtils.fields.editInput($('.modal.o_selected_rowinput'),'anotherone');
            awaittestUtils.modal.clickButton('Save&Close');

            assert.containsNone(document.body,'.modal');

            assert.containsOnce(form,'.o_field_widget[name=p].o_data_row');
            assert.containsN(form,'.o_data_row.o_field_many2manytags.badge',2);
            assert.strictEqual(form.$('.o_data_row.o_field_many2manytags.o_badge_text').text(),
                'newturtleanotherone');

            form.destroy();
        });

        QUnit.test('one2manyvaluereturnedbyonchangewithunknownfields',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.onchanges={
                bar:function(obj){
                    obj.p=[
                        [5],
                        [0,0,{
                            bar:true,
                            display_name:"coucou",
                            trululu:[2,'secondrecord'],
                            turtles:[[5],[0,0,{turtle_int:4}]],
                        }]
                    ];
                },
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="bar"/>
                        <fieldname="p"widget="many2many_tags"/>
                    </form>`,
                mockRPC(route,args){
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0].p[0][2],{
                            bar:true,
                            display_name:"coucou",
                            trululu:2,
                            turtles:[[5],[0,0,{turtle_int:4}]],
                        });
                    }
                    returnthis._super(...arguments);
                },
            });

            assert.containsOnce(form,'.o_field_many2manytags.badge');
            assert.strictEqual(form.$('.o_field_many2manytags.o_badge_text').text(),'coucou');

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('mountediscalledonlyonceforx2manycontrolpanel',asyncfunction(assert){
            //Thistestcouldberemovedassoonasthefieldwidgetswillbeconvertedinowl.
            //Itcomeswithafixforabugthatoccurredbecauseinsomecirconstances,'mounted'
            //iscalledtwiceforthex2manycontrolpanel.
            //Specifically,thisoccurswhenthereis'pad'widgetintheformview,becausethis
            //widgetdoesa'setValue'inits'start',whichthusresetsthefieldx2many.
            assert.expect(5);

            constPadLikeWidget=fieldRegistry.get('char').extend({
                start(){
                    this._setValue("somevalue");
                }
            });
            fieldRegistry.add('pad_like',PadLikeWidget);

            letresolveCP;
            constprom=newPromise(r=>{
                resolveCP=r;
            });
            ControlPanel.patch('cp_patch_mock',T=>
                classextendsT{
                    constructor(){
                        super(...arguments);
                        owl.hooks.onMounted(()=>{
                            assert.step('mounted');
                        });
                        owl.hooks.onWillUnmount(()=>{
                            assert.step('willUnmount');
                        });
                    }
                    asyncupdate(){
                        //theissueisaracecondition,sowemanuallydelaytheupdatetoturnitdeterministic
                        awaitprom;
                        super.update(...arguments);
                    }
                }
            );

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="foo"widget="pad_like"/>
                        <fieldname="p">
                            <tree><fieldname="display_name"/></tree>
                        </field>
                    </form>`,
                viewOptions:{
                    withControlPanel:false,//s.t.thereisonlyoneCP:theoneofthex2many
                },
            });

            assert.verifySteps(['mounted']);

            resolveCP();
            awaittestUtils.nextTick();

            assert.verifySteps([]);

            ControlPanel.unpatch('cp_patch_mock');
            deletefieldRegistry.map.pad_like;
            form.destroy();

            assert.verifySteps(["willUnmount"]);
        });

        QUnit.test('one2many:internalstateisupdatedafteranotherfieldchanges',asyncfunction(assert){
            //TheFieldOne2Manyisconfiguredsuchthatitisresetatanyfieldchange.
            //TheMatrixProductConfiguratorfeaturereliesonthat,andrequiresthatits
            //internalstateiscorrectlyupdated.Thiswhite-boxtestartificiallychecksthat.
            assert.expect(2);

            leto2m;
            testUtils.patch(FieldOne2Many,{
                init(){
                    this._super(...arguments);
                    o2m=this;
                },
            });

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="display_name"/>
                        <fieldname="p">
                            <tree><fieldname="display_name"/></tree>
                        </field>
                    </form>`,
            });

            assert.strictEqual(o2m.recordData.display_name,false);

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'val');

            assert.strictEqual(o2m.recordData.display_name,"val");

            form.destroy();
            testUtils.unpatch(FieldOne2Many);
        });

        QUnit.test('nestedone2many,onchange,nocommandvalue',asyncfunction(assert){
            //Thistestensuresthatwealwayssendallvaluestoonchangerpcsfornested
            //one2manys,evenifsomefieldhasn'tchanged.Inthisparticulartestcase,
            //afirstonchangereturnsavaluefortheinnerone2many,andasecondonchange
            //removesit,thusrestoringthefieldtoitsinitialemptyvalue.Fromthispoint,
            //thenestedone2manyvaluemuststillbesenttoonchangerpcs(onthemainrecord),
            //asitmightbeusedtocomputeotherfields(sothefactthatthenestedo2misempty
            //mustbeexplicit).
            assert.expect(3);

            this.data.turtle.fields.o2m={
                string:"o2m",type:"one2many",relation:'partner',relation_field:'trululu',
            };
            this.data.turtle.fields.turtle_bar.default=true;
            this.data.partner.onchanges.turtles=function(obj){};
            this.data.turtle.onchanges.turtle_bar=function(obj){
                if(obj.turtle_bar){
                    obj.o2m=[[5],[0,false,{display_name:"default"}]];
                }else{
                    obj.o2m=[[5]];
                }
            };

            letstep=1;
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<form>
                        <fieldname="turtles">
                            <treeeditable="bottom">
                                <fieldname="o2m"/>
                                <fieldname="turtle_bar"/>
                            </tree>
                        </field>
                    </form>`,
                asyncmockRPC(route,args){
                    if(step===3&&args.method==='onchange'&&args.model==='partner'){
                        assert.deepEqual(args.args[1].turtles[0][2],{
                            turtle_bar:false,
                            o2m:[],//wemustsendavalueforthisfield
                        });
                    }
                    constresult=awaitthis._super(...arguments);
                    if(args.model==='turtle'){
                        //sanitychecks;thisiswhattheonchangesonturtlemustreturn
                        if(step===2){
                            assert.deepEqual(result.value,{
                                o2m:[[5],[0,false,{display_name:"default"}]],
                                turtle_bar:true,
                            });
                        }
                        if(step===3){
                            assert.deepEqual(result.value,{
                                o2m:[[5]],
                            });
                        }
                    }
                    returnresult;
                },
            });

            step=2;
            awaittestUtils.dom.click(form.$('.o_field_x2many_list.o_field_x2many_list_row_adda'));
            //useofowlCompatibilityNextTickbecausewehaveanx2manyfieldwithabooleanfield
            //(writteninowl),sowhenweaddaline,wesequentiallyrenderthelistitself
            //(includingthebooleanfield),sowehavetowaitforthenextanimationframe,and
            //thenwerenderthecontrolpanel(alsoinowl),sowehavetowaitagainforthe
            //nextanimationframe
            awaittestUtils.owlCompatibilityNextTick();
            step=3;
            awaittestUtils.dom.click(form.$('.o_data_row.o_field_booleaninput'));

            form.destroy();
        });

        QUnit.test('updateaone2manyfromacustomfieldwidget',asyncfunction(assert){
            //Inthistest,wedefineacustomfieldwidgettorender/updateaone2many
            //field.Fortheupdatepart,weensurethatupdatingprimitivefieldsofasub
            //recordworks.Thereisnoguaranteethatupdatingarelationalfieldonthesub
            //recordwouldwork.Deletingasubrecordworksaswell.However,creatingsub
            //recordsisn'tsupported.Thereareobviouslyalotoflimitations,butthecode
            //hasn'tbeendesignedtosupportallthis.Thistestsimplyencodeswhatcanbe
            //done,andthiscommentexplainswhatcan't(andwon'tbeimplementedinstable
            //versions).
            assert.expect(3);

            this.data.partner.records[0].p=[1,2];
            constMyRelationalField=AbstractField.extend({
                events:{
                    'click.update':'_onUpdate',
                    'click.delete':'_onDelete',
                },
                async_render(){
                    constrecords=awaitthis._rpc({
                        method:'read',
                        model:'partner',
                        args:[this.value.res_ids],
                    });
                    this.$el.text(records.map(r=>`${r.display_name}/${r.int_field}`).join(','));
                    this.$el.append($('<buttonclass="updatefafa-edit">'));
                    this.$el.append($('<buttonclass="deletefafa-trash">'));
                },
                _onUpdate(){
                    this._setValue({
                        operation:'UPDATE',
                        id:this.value.data[0].id,
                        data:{
                            display_name:'newname',
                            int_field:44,
                        },
                    });
                },
                _onDelete(){
                    this._setValue({
                        operation:'DELETE',
                        ids:[this.value.data[0].id],
                    });
                },
            });
            fieldRegistry.add('my_relational_field',MyRelationalField);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="p"widget="my_relational_field"/>
                    </form>`,
                res_id:1,
            });

            assert.strictEqual(form.$('.o_field_widget[name=p]').text(),'firstrecord/10,secondrecord/9');

            awaittestUtils.dom.click(form.$('button.update'));

            assert.strictEqual(form.$('.o_field_widget[name=p]').text(),'newname/44,secondrecord/9');

            awaittestUtils.dom.click(form.$('button.delete'));

            assert.strictEqual(form.$('.o_field_widget[name=p]').text(),'secondrecord/9');

            form.destroy();
            deletefieldRegistry.map.my_relational_field;
        });

        QUnit.test('reorderingembeddedone2manywithhandlewidgetstartingwithsamesequence',asyncfunction(assert){
            assert.expect(3);

            this.data.turtle={
                fields:{turtle_int:{string:"int",type:"integer",sortable:true}},
                records:[
                    {id:1,turtle_int:1},
                    {id:2,turtle_int:1},
                    {id:3,turtle_int:1},
                    {id:4,turtle_int:2},
                    {id:5,turtle_int:3},
                    {id:6,turtle_int:4},
                ],
            };
            this.data.partner.records[0].turtles=[1,2,3,4,5,6];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <formstring="Partners">
                        <sheet>
                            <notebook>
                                <pagestring="Ppage">
                                    <fieldname="turtles">
                                        <treedefault_order="turtle_int">
                                            <fieldname="turtle_int"widget="handle"/>
                                            <fieldname="id"/>
                                        </tree>
                                    </field>
                                </page>
                            </notebook>
                        </sheet>
                    </form>`,
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"123456","defaultshouldbesortedbyid");

            //Draganddropthefourthlineinfirstposition
            awaittestUtils.dom.dragAndDrop(
                form.$('.ui-sortable-handle').eq(3),
                form.$('tbodytr').first(),
                {position:'top'}
            );
            assert.strictEqual(form.$('td.o_data_cell:not(.o_handle_cell)').text(),"412356","shouldstillhavethe6rowsinthecorrectorder");

            awaittestUtils.form.clickSave(form);

            assert.deepEqual(_.map(this.data.turtle.records,function(turtle){
                return_.pick(turtle,'id','turtle_int');
            }),[
                {id:1,turtle_int:2},
                {id:2,turtle_int:3},
                {id:3,turtle_int:4},
                {id:4,turtle_int:1},
                {id:5,turtle_int:5},
                {id:6,turtle_int:6},
            ],"shouldhavesavedtheupdatedturtle_intsequence");

            form.destroy();
        });

        QUnit.test("add_recordinano2mwithanOWLfield:waitmountedbeforesuccess",asyncfunction(assert){
            assert.expect(7);

            lettestInst=0;
            classTestFieldextendsAbstractFieldOwl{
                setup(){
                    super.setup();
                    constID=testInst++;
                    owl.hooks.onMounted(()=>{
                        assert.step(`mounted${ID}`);
                    });

                    owl.hooks.onWillUnmount(()=>{
                        assert.step(`willUnmount${ID}`);
                    });
                }
                activate(){
                    returntrue;
                }
            }

            TestField.template=owl.tags.xml`<span>test</span>`;
            fieldRegistryOwl.add('test_field',TestField);

            constdef=testUtils.makeTestPromise();
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                debug:1,
                data:this.data,
                arch:`<form>
                        <fieldname="p">
                            <treeeditable="bottom">
                                <fieldname="name"widget="test_field"/>
                            </tree>
                        </field>
                    </form>`,
                viewOptions:{
                    mode:'edit',
                },
            });

            constlist=form.renderer.allFieldWidgets[form.handle][0];

            list.trigger_up('add_record',{
                context:[{
                    default_name:'thisisatest',
                }],
                allowWarning:true,
                forceEditable:'bottom',
                onSuccess:function(){
                    assert.step("onSuccess");
                    def.resolve();
                }
            });

            awaittestUtils.nextTick();
            awaitdef;
            assert.verifySteps(["mounted0","willUnmount0","mounted1","onSuccess"]);
            form.destroy();
            assert.verifySteps(["willUnmount1"]);
        });

        QUnit.test('nestedone2manys,multipage,onchange',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[2].int_field=5;
            this.data.partner.records[0].p=[2,4];//limit1->record4willbeonsecondpage
            this.data.partner.records[1].turtles=[1];
            this.data.partner.records[2].turtles=[2];
            this.data.turtle.records[0].turtle_int=1;
            this.data.turtle.records[1].turtle_int=2;

            this.data.partner.onchanges.int_field=function(obj){
               assert.step('onchange')
               obj.p=[[5]]
               obj.p.push([1,2,{turtles:[[5],[1,1,{turtle_int:obj.int_field}]]}]);
               obj.p.push([1,4,{turtles:[[5],[1,2,{turtle_int:obj.int_field}]]}]);
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partner">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom"limit="1"default_order="display_name">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="turtles">'+
                        '<treeeditable="bottom">'+
                            '<fieldname="turtle_int"/>'+
                        '</tree>'+
                        '</field>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.fields.editInput(form.$('[name="int_field"]'),'5');
            assert.verifySteps(['onchange'])

            awaittestUtils.form.clickSave(form);

            assert.strictEqual(this.data.partner.records[0].int_field,5,'Valueshouldhavebeenupdated')
            assert.strictEqual(this.data.turtle.records[1].turtle_int,5,'Showndatashouldhavebeenupdated');
            assert.strictEqual(this.data.turtle.records[0].turtle_int,5,'Hiddendatashouldhavebeenupdated');

            form.destroy();
        });
    });
});
});
