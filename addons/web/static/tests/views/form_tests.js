flectra.define('web.form_tests',function(require){
"usestrict";

constAbstractField=require("web.AbstractField");
varAbstractStorageService=require('web.AbstractStorageService');
varBasicModel=require('web.BasicModel');
varconcurrency=require('web.concurrency');
varcore=require('web.core');
varfieldRegistry=require('web.field_registry');
constfieldRegistryOwl=require('web.field_registry_owl');
constFormRenderer=require('web.FormRenderer');
varFormView=require('web.FormView');
varmixins=require('web.mixins');
varNotificationService=require('web.NotificationService');
varpyUtils=require('web.py_utils');
varRamStorage=require('web.RamStorage');
vartestUtils=require('web.test_utils');
varwidgetRegistry=require('web.widget_registry');
varWidget=require('web.Widget');

var_t=core._t;
constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;
varcreateActionManager=testUtils.createActionManager;

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    display_name:{string:"Displayedname",type:"char"},
                    foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
                    bar:{string:"Bar",type:"boolean"},
                    int_field:{string:"int_field",type:"integer",sortable:true},
                    qux:{string:"Qux",type:"float",digits:[16,1]},
                    p:{string:"one2manyfield",type:"one2many",relation:'partner'},
                    trululu:{string:"Trululu",type:"many2one",relation:'partner'},
                    timmy:{string:"pokemon",type:"many2many",relation:'partner_type'},
                    product_id:{string:"Product",type:"many2one",relation:'product'},
                    priority:{
                        string:"Priority",
                        type:"selection",
                        selection:[[1,"Low"],[2,"Medium"],[3,"High"]],
                        default:1,
                    },
                    state:{string:"State",type:"selection",selection:[["ab","AB"],["cd","CD"],["ef","EF"]]},
                    date:{string:"SomeDate",type:"date"},
                    datetime:{string:"DatetimeField",type:'datetime'},
                    product_ids:{string:"one2manyproduct",type:"one2many",relation:"product"},
                    reference:{string:"ReferenceField",type:'reference',selection:[["product","Product"],["partner_type","PartnerType"],["partner","Partner"]]},
                },
                records:[{
                    id:1,
                    display_name:"firstrecord",
                    bar:true,
                    foo:"yop",
                    int_field:10,
                    qux:0.44,
                    p:[],
                    timmy:[],
                    trululu:4,
                    state:"ab",
                    date:"2017-01-25",
                    datetime:"2016-12-1210:55:05",
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
                    state:"cd",
                },{
                    id:4,
                    display_name:"aaa",
                    state:"ef",
                },{
                    id:5,
                    display_name:"aaa",
                    foo:'',
                    bar:false,
                    state:"ef",
                }],
                onchanges:{},
            },
            product:{
                fields:{
                    display_name:{string:"ProductName",type:"char"},
                    name:{string:"ProductName",type:"char"},
                    partner_type_id:{string:"Partnertype",type:"many2one",relation:"partner_type"},
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
            "ir.translation":{
                fields:{
                    lang_code:{type:"char"},
                    value:{type:"char"},
                    res_id:{type:"integer"}
                },
                records:[{
                    id:99,
                    res_id:12,
                    value:'',
                    lang_code:'en_US'
                }]
            },
            user:{
                fields:{
                    name:{string:"Name",type:"char"},
                    partner_ids:{string:"one2manypartnersfield",type:"one2many",relation:'partner',relation_field:'user_id'},
                },
                records:[{
                    id:17,
                    name:"Aline",
                    partner_ids:[1],
                },{
                    id:19,
                    name:"Christine",
                }]
            },
            "res.company":{
                fields:{
                    name:{string:"Name",type:"char"},
                },
            },
        };
        this.actions=[{
            id:1,
            name:'PartnersAction1',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'kanban'],[false,'form']],
        }];
    },
},function(){

    QUnit.module('FormView');

    QUnit.test('simpleformrendering',asyncfunction(assert){
        assert.expect(12);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<divclass="test"style="opacity:0.5;">somehtml<span>aa</span></div>'+
                    '<sheet>'+
                        '<group>'+
                            '<groupstyle="background-color:red">'+
                                '<fieldname="foo"style="color:blue"/>'+
                                '<fieldname="bar"/>'+
                                '<fieldname="int_field"string="f3_description"/>'+
                                '<fieldname="qux"/>'+
                            '</group>'+
                            '<group>'+
                                '<divclass="hello"></div>'+
                            '</group>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="PartnerYo">'+
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
            res_id:2,
        });


        assert.containsOnce(form,'div.test');
        assert.strictEqual(form.$('div.test').css('opacity'),'0.5',
            "shouldkeeptheinlinestyleonhtmlelements");
        assert.containsOnce(form,'label:contains(Foo)');
        assert.containsOnce(form,'span:contains(blip)');
        assert.hasAttrValue(form.$('.o_group.o_group:first'),'style','background-color:red',
            "shouldapplystyleattributeongroups");
        assert.hasAttrValue(form.$('.o_field_widget[name=foo]'),'style','color:blue',
            "shouldapplystyleattributeonfields");
        assert.containsNone(form,'label:contains(something_id)');
        assert.containsOnce(form,'label:contains(f3_description)');
        assert.containsOnce(form,'div.o_field_one2manytable');
        assert.containsOnce(form,'tbodytd:not(.o_list_record_selector).custom-checkboxinput:checked');
        assert.containsOnce(form,'.o_control_panel.breadcrumb:contains(secondrecord)');
        assert.containsNone(form,'label.o_form_label_empty:contains(timmy)');

        form.destroy();
    });

    QUnit.test('duplicatefieldsrenderedproperly',asyncfunction(assert){
        assert.expect(6);
        this.data.partner.records.push({
            id:6,
            bar:true,
            foo:"blip",
            int_field:9,
        });
        varform=awaitcreateView({
            View:FormView,
            viewOptions:{mode:'edit'},
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<group>'+
                            '<fieldname="foo"attrs="{\'invisible\':[(\'bar\',\'=\',True)]}"/>'+
                            '<fieldname="foo"attrs="{\'invisible\':[(\'bar\',\'=\',False)]}"/>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="int_field"attrs="{\'readonly\':[(\'bar\',\'=\',False)]}"/>'+
                            '<fieldname="int_field"attrs="{\'readonly\':[(\'bar\',\'=\',True)]}"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</group>'+
                '</form>',
            res_id:6,
        });

        assert.hasClass(form.$('div.o_groupinput[name="foo"]:eq(0)'),'o_invisible_modifier','firstfoowidgetshouldbeinvisible');
        assert.containsOnce(form,'div.o_groupinput[name="foo"]:eq(1):not(.o_invisible_modifier)',"secondfoowidgetshouldbevisible");
        assert.containsOnce(form,'div.o_groupinput[name="foo"]:eq(2):not(.o_invisible_modifier)',"thirdfoowidgetshouldbevisible");
        awaittestUtils.fields.editInput(form.$('div.o_groupinput[name="foo"]:eq(2)'),"hello");
        assert.strictEqual(form.$('div.o_groupinput[name="foo"]:eq(1)').val(),"hello","secondfoowidgetshouldbe'hello'");
        assert.containsOnce(form,'div.o_groupinput[name="int_field"]:eq(0):not(.o_readonly_modifier)',"firstint_fieldwidgetshouldnotbereadonly");
        assert.hasClass(form.$('div.o_groupspan[name="int_field"]:eq(0)'),'o_readonly_modifier',"secondint_fieldwidgetshouldbereadonly");
        form.destroy();
    });

    QUnit.test('duplicatefieldsrenderedproperly(one2many)',asyncfunction(assert){
        assert.expect(7);
        this.data.partner.records.push({
            id:6,
            p:[1],
        });
        varform=awaitcreateView({
            View:FormView,
            viewOptions:{mode:'edit'},
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<notebook>'+
                        '<page>'+
                            '<fieldname="p">'+
                                '<treeeditable="True">'+
                                    '<fieldname="foo"/>'+
                                '</tree>'+
                                '<form/>'+
                            '</field>'+
                        '</page>'+
                        '<page>'+
                            '<fieldname="p"readonly="True">'+
                                '<treeeditable="True">'+
                                    '<fieldname="foo"/>'+
                                '</tree>'+
                                '<form/>'+
                            '</field>'+
                        '</page>'+
                    '</notebook>'+
                '</form>',
            res_id:6,
        });
        assert.containsOnce(form,'div.o_field_one2many:eq(0):not(.o_readonly_modifier)',"firstone2manywidgetshouldnotbereadonly");
        assert.hasClass(form.$('div.o_field_one2many:eq(1)'),'o_readonly_modifier',"secondone2manywidgetshouldbereadonly");
        awaittestUtils.dom.click(form.$('div.tab-contenttable.o_list_table:eq(0)tr.o_data_rowtd.o_data_cell:eq(0)'));
        assert.strictEqual(form.$('div.tab-contenttable.o_list_tabletr.o_selected_rowinput[name="foo"]').val(),"yop",
            "firstlineinone2manyoffirsttabcontainsyop");
        assert.strictEqual(form.$('div.tab-contenttable.o_list_table:eq(1)tr.o_data_rowtd.o_data_cell:eq(0)').text(),
            "yop","firstlineinone2manyofsecondtabcontainsyop");
        awaittestUtils.fields.editInput(form.$('div.tab-contenttable.o_list_tabletr.o_selected_rowinput[name="foo"]'),"hello");
        assert.strictEqual(form.$('div.tab-contenttable.o_list_table:eq(1)tr.o_data_rowtd.o_data_cell:eq(0)').text(),"hello",
            "firstlineinone2manyofsecondtabcontainshello");
        awaittestUtils.dom.click(form.$('div.tab-contenttable.o_list_table:eq(0)a:contains(Addaline)'));
        assert.strictEqual(form.$('div.tab-contenttable.o_list_tabletr.o_selected_rowinput[name="foo"]').val(),"MylittleFooValue",
            "secondlineinone2manyoffirsttabcontains'MylittleFooValue'");
        assert.strictEqual(form.$('div.tab-contenttable.o_list_table:eq(1)tr.o_data_row:eq(1)td.o_data_cell:eq(0)').text(),
            "MylittleFooValue","firstlineinone2manyofsecondtabcontainshello");
        form.destroy();
    });

    QUnit.test('attributesaretransferredonasyncwidgets',asyncfunction(assert){
        assert.expect(1);
        vardone =assert.async();

        vardef=testUtils.makeTestPromise();

        varFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            willStart:function(){
                returndef;
            },
        }));

        createView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group>'+
                        '<fieldname="foo"style="color:blue"widget="asyncwidget"/>'+
                    '</group>'+
                '</form>',
            res_id:2,
        }).then(function(form){
            assert.hasAttrValue(form.$('.o_field_widget[name=foo]'),'style','color:blue',
                "shouldapplystyleattributeonfields");
            form.destroy();
            deletefieldRegistry.map.asyncwidget;
            done();
        });
        def.resolve();
        awaittestUtils.nextTick();
    });

    QUnit.test('placeholderattributeoninput',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<inputplaceholder="chimay"/>'+
                '</form>',
            res_id:2,
        });

        assert.containsOnce(form,'input[placeholder="chimay"]');
        form.destroy();
    });

    QUnit.test('decorationworksonwidgets',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="display_name"decoration-danger="int_field&lt;5"/>'+
                    '<fieldname="foo"decoration-danger="int_field&gt;5"/>'+
                '</form>',
            res_id:2,
        });
        assert.doesNotHaveClass(form.$('span[name="display_name"]'),'text-danger');
        assert.hasClass(form.$('span[name="foo"]'),'text-danger');
        form.destroy();
    });

    QUnit.test('decorationonwidgetsarereevaluatedifnecessary',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="display_name"decoration-danger="int_field&lt;5"/>'+
                '</form>',
            res_id:2,
            viewOptions:{mode:'edit'},
        });
        assert.doesNotHaveClass(form.$('input[name="display_name"]'),'text-danger');
        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),3);
        assert.hasClass(form.$('input[name="display_name"]'),'text-danger');
        form.destroy();
    });

    QUnit.test('decorationonwidgetsworksonsamewidget',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="int_field"decoration-danger="int_field&lt;5"/>'+
                '</form>',
            res_id:2,
            viewOptions:{mode:'edit'},
        });
        assert.doesNotHaveClass(form.$('input[name="int_field"]'),'text-danger');
        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),3);
        assert.hasClass(form.$('input[name="int_field"]'),'text-danger');
        form.destroy();
    });

    QUnit.test('onlynecessaryfieldsarefetchedwithcorrectcontext',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                //NOTE:actually,thecurrentwebclientalwaysrequestthe__last_update
                //field,notsurewhy. Maybethistestshouldbemodified.
                assert.deepEqual(args.args[1],["foo","display_name"],
                    "shouldonlyfetchrequestedfields");
                assert.deepEqual(args.kwargs.context,{bin_size:true},
                    "bin_sizeshouldalwaysbeinthecontext");
                returnthis._super(route,args);
            }
        });
        form.destroy();
    });

    QUnit.test('grouprendering',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'table.o_inner_group');

        form.destroy();
    });

    QUnit.test('groupcontainingbothafieldandagroup',asyncfunction(assert){
        //Thepurposeofthistestistocheckthatclassnamesdefinedina
        //fieldwidgetandthoseaddedbytheformrendererarecorrectly
        //combined.Forinstance,therendereraddsclassName'o_group_col_x'
        //onoutergroup'schildren(anoutergroupbeingagroupthatcontains
        //atleastagroup).
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<group>'+
                            '<fieldname="int_field"/>'+
                        '</group>'+
                    '</group>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_group.o_field_widget[name=foo]');
        assert.containsOnce(form,'.o_group.o_inner_group.o_field_widget[name=int_field]');

        assert.hasClass(form.$('.o_field_widget[name=foo]'),'o_field_char');
        assert.hasClass(form.$('.o_field_widget[name=foo]'),'o_group_col_6');

        form.destroy();
    });

    QUnit.test('Formandsubviewwith_view_refcontexts',asyncfunction(assert){
        assert.expect(2);

        this.data.product.fields.partner_type_ids={string:"one2manyfield",type:"one2many",relation:"partner_type"},
        this.data.product.records=[{id:1,name:'Tromblon',partner_type_ids:[12,14]}];
        this.data.partner.records[0].product_id=1;

        varactionManager=awaitcreateActionManager({
            data:this.data,
            archs:{
                'product,false,form':'<form>'+
                                            '<fieldname="name"/>'+
                                            '<fieldname="partner_type_ids"context="{\'tree_view_ref\':\'some_other_tree_view\'}"/>'+
                                        '</form>',

                'partner_type,false,list':'<tree>'+
                                                '<fieldname="color"/>'+
                                            '</tree>',
                'product,false,search':'<search></search>',
            },
            mockRPC:function(route,args){
                if(args.method==='load_views'){
                    varcontext=args.kwargs.context;
                    if(args.model==='product'){
                        assert.deepEqual(context,{tree_view_ref:'some_tree_view'},
                            'Thecorrect_view_refshouldhavebeensenttotheserver,firsttime');
                    }
                    if(args.model==='partner_type'){
                        assert.deepEqual(context,{
                            base_model_name:'product',
                            tree_view_ref:'some_other_tree_view',
                        },'Thecorrect_view_refshouldhavebeensenttotheserverforthesubview');
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                     '<fieldname="name"/>'+
                     '<fieldname="product_id"context="{\'tree_view_ref\':\'some_tree_view\'}"/>'+
                  '</form>',
            res_id:1,

            mockRPC:function(route,args){
                if(args.method==='get_formview_action'){
                    returnPromise.resolve({
                        res_id:1,
                        type:'ir.actions.act_window',
                        target:'current',
                        res_model:args.model,
                        context:args.kwargs.context,
                        'view_mode':'form',
                        'views':[[false,'form']],
                    });
                }
                returnthis._super(route,args);
            },

            interceptsPropagate:{
                do_action:function(ev){
                    actionManager.doAction(ev.data.action);
                },
            },
        });
        awaittestUtils.dom.click(form.$('.o_field_widget[name="product_id"]'));
        form.destroy();
        actionManager.destroy();
    });

    QUnit.test('invisiblefieldsareproperlyhidden',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"invisible="1"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                        '<fieldname="qux"invisible="1"/>'+
                        //x2manyfieldwithoutinlineview:asitisalwaysinvisible,theview
                        //shouldnotbefetched.wedon'tspecifyanyviewinthistest,soifit
                        //evertriestofetchit,itwillcrash,indicatingthatthisiswrong.
                        '<fieldname="p"invisible="True"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsNone(form,'label:contains(Foo)');
        assert.containsNone(form,'.o_field_widget[name=foo]');
        assert.containsNone(form,'.o_field_widget[name=qux]');
        assert.containsNone(form,'.o_field_widget[name=p]');

        form.destroy();
    });

    QUnit.test('invisibleelementsareproperlyhidden',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<headerinvisible="1">'+
                        '<buttonname="myaction"string="coucou"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<groupstring="invgroup"invisible="1">'+
                                '<fieldname="foo"/>'+
                            '</group>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="visible"/>'+
                            '<pagestring="invisible"invisible="1"/>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        assert.containsOnce(form,'.o_form_statusbar.o_invisible_modifierbutton:contains(coucou)');
        assert.containsOnce(form,'.o_notebookli.o_invisible_modifiera:contains(invisible)');
        assert.containsOnce(form,'table.o_inner_group.o_invisible_modifiertd:contains(invgroup)');
        form.destroy();
    });

    QUnit.test('invisibleattrsonfieldsarere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(3);

        //wesetthevaluebartosimulateafalsybooleanvalue.
        this.data.partner.records[0].bar=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="timmy"invisible="1"/>'+
                        '<fieldname="foo"class="foo_field"attrs=\'{"invisible":[["product_id","=",false]]}\'/>'+
                        '<fieldname="bar"class="bar_field"attrs=\'{"invisible":[("bar","=",False),("timmy","=",[])]}\'/>'+
                    '</group></sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit'
            },
        });

        assert.hasClass(form.$('.foo_field'),'o_invisible_modifier');
        assert.hasClass(form.$('.bar_field'),'o_invisible_modifier');

        //setavalueonthem2o
        awaittestUtils.fields.many2one.searchAndClickItem('product_id');
        assert.doesNotHaveClass(form.$('.foo_field'),'o_invisible_modifier');

        form.destroy();
    });

    QUnit.test('asynchronousfieldscanbesetinvisible',asyncfunction(assert){
        assert.expect(1);
        vardone=assert.async();

        vardef=testUtils.makeTestPromise();

        //wechoosethiswidgetbecauseitisaquitesimplewidgetwithanon
        //emptyqwebtemplate
        varPercentPieWidget=fieldRegistry.get('percentpie');
        fieldRegistry.add('asyncwidget',PercentPieWidget.extend({
            willStart:function(){
                returndef;
            },
        }));

        createView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"invisible="1"widget="asyncwidget"/>'+
                    '</group></sheet>'+
                '</form>',
            res_id:1,
        }).then(function(form){
            assert.containsNone(form,'.o_field_widget[name="int_field"]');
            form.destroy();
            deletefieldRegistry.map.asyncwidget;
            done();
        });
        def.resolve();
    });

    QUnit.test('properlyhandlemodifiersandattributesonnotebooktags',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="product_id"/>'+
                        '<notebookclass="new_class"attrs=\'{"invisible":[["product_id","=",false]]}\'>'+
                            '<pagestring="Foo">'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.hasClass(form.$('.o_notebook'),'o_invisible_modifier');
        assert.hasClass(form.$('.o_notebook'),'new_class');
        form.destroy();
    });

    QUnit.test('emptynotebook',asyncfunction(assert){
        assert.expect(2);

        constform=awaitcreateView({
            arch:`
                <formstring="Partners">
                    <sheet>
                        <notebook/>
                    </sheet>
                </form>`,
            data:this.data,
            model:'partner',
            res_id:1,
            View:FormView,
        });

        //Doesnotchangewhenswitchingstate
        awaittestUtils.form.clickEdit(form);

        assert.containsNone(form,':scope.o_notebook.nav');

        //Doesnotchangewhencomingbacktoinitialstate
        awaittestUtils.form.clickSave(form);

        assert.containsNone(form,':scope.o_notebook.nav');

        form.destroy();
    });

    QUnit.test('novisiblepage',asyncfunction(assert){
        assert.expect(4);

        constform=awaitcreateView({
            arch:`
                <formstring="Partners">
                    <sheet>
                        <notebook>
                            <pagestring="Foo"invisible="1">
                                <fieldname="foo"/>
                            </page>
                            <pagestring="Bar"invisible="1">
                                <fieldname="bar"/>
                            </page>
                        </notebook>
                    </sheet>
                </form>`,
            data:this.data,
            model:'partner',
            res_id:1,
            View:FormView,
        });

        //Doesnotchangewhenswitchingstate
        awaittestUtils.form.clickEdit(form);

        for(constnavofform.el.querySelectorAll(':scope.o_notebook.nav')){
            assert.containsNone(nav,'.nav-link.active');
            assert.containsN(nav,'.nav-item.o_invisible_modifier',2);
        }

        //Doesnotchangewhencomingbacktoinitialstate
        awaittestUtils.form.clickSave(form);

        for(constnavofform.el.querySelectorAll(':scope.o_notebook.nav')){
            assert.containsNone(nav,'.nav-link.active');
            assert.containsN(nav,'.nav-item.o_invisible_modifier',2);
        }

        form.destroy();
    });

    QUnit.test('notebook:pageswithinvisiblemodifiers',asyncfunction(assert){
        assert.expect(10);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                    <sheet>
                        <fieldname="bar"/>
                        <notebook>
                            <pagestring="First"attrs='{"invisible":[["bar","=",false]]}'>
                                <fieldname="foo"/>
                            </page>
                            <pagestring="Second"attrs='{"invisible":[["bar","=",true]]}'>
                                <fieldname="int_field"/>
                            </page>
                            <pagestring="Third">
                                <fieldname="qux"/>
                            </page>
                        </notebook>
                    </sheet>
                </form>`,
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,".o_notebook.nav.nav-link.active",
            "Thereshouldbeonlyoneactivetab"
        );
        assert.isVisible(form.$(".o_notebook.nav.nav-item:first"));
        assert.hasClass(form.$(".o_notebook.nav.nav-link:first"),"active");

        assert.isNotVisible(form.$(".o_notebook.nav.nav-item:eq(1)"));
        assert.doesNotHaveClass(form.$(".o_notebook.nav.nav-link:eq(1)"),"active");

        awaittestUtils.dom.click(form.$(".o_field_widget[name=bar]input"));

        assert.containsOnce(form,".o_notebook.nav.nav-link.active",
            "Thereshouldbeonlyoneactivetab"
        );
        assert.isNotVisible(form.$(".o_notebook.nav.nav-item:first"));
        assert.doesNotHaveClass(form.$(".o_notebook.nav.nav-link:first"),"active");

        assert.isVisible(form.$(".o_notebook.nav.nav-item:eq(1)"));
        assert.hasClass(form.$(".o_notebook.nav.nav-link:eq(1)"),"active");

        form.destroy();
    });

    QUnit.test('invisibleattrsonfirstnotebookpage',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="product_id"/>'+
                        '<notebook>'+
                            '<pagestring="Foo"attrs=\'{"invisible":[["product_id","!=",false]]}\'>'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                            '<pagestring="Bar">'+
                                '<fieldname="bar"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.hasClass(form.$('.o_notebook.nav.nav-link:first()'),'active');
        assert.doesNotHaveClass(form.$('.o_notebook.nav.nav-item:first()'),'o_invisible_modifier');

        //setavalueonthem2o
        awaittestUtils.fields.many2one.searchAndClickItem('product_id');
        assert.doesNotHaveClass(form.$('.o_notebook.nav.nav-link:first()'),'active');
        assert.hasClass(form.$('.o_notebook.nav.nav-item:first()'),'o_invisible_modifier');
        assert.hasClass(form.$('.o_notebook.nav.nav-link:nth(1)'),'active');
        assert.hasClass(form.$('.o_notebook.tab-content.tab-pane:nth(1)'),'active');
        form.destroy();
    });

    QUnit.test('invisibleattrsonnotebookpagewhichhasonlyonepage',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="bar"/>'+
                        '<notebook>'+
                            '<pagestring="Foo"attrs=\'{"invisible":[["bar","!=",false]]}\'>'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.notOk(form.$('.o_notebook.nav.nav-link:first()').hasClass('active'),
            'firsttabshouldnotbeactive');
        assert.ok(form.$('.o_notebook.nav.nav-item:first()').hasClass('o_invisible_modifier'),
            'firsttabshouldbeinvisible');

        //enablecheckbox
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));
        assert.ok(form.$('.o_notebook.nav.nav-link:first()').hasClass('active'),
            'firsttabshouldbeactive');
        assert.notOk(form.$('.o_notebook.nav.nav-item:first()').hasClass('o_invisible_modifier'),
            'firsttabshouldbevisible');

        form.destroy();
    });

    QUnit.test('firstnotebookpageinvisible',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="product_id"/>'+
                        '<notebook>'+
                            '<pagestring="Foo"invisible="1">'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                            '<pagestring="Bar">'+
                                '<fieldname="bar"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.notOk(form.$('.o_notebook.nav.nav-item:first()').is(':visible'),
            'firsttabshouldbeinvisible');
        assert.hasClass(form.$('.o_notebook.nav.nav-link:nth(1)'),'active');

        form.destroy();
    });

    QUnit.test('autofocusonsecondnotebookpage',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="product_id"/>'+
                        '<notebook>'+
                            '<pagestring="Choucroute">'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                            '<pagestring="Cassoulet"autofocus="autofocus">'+
                                '<fieldname="bar"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.doesNotHaveClass(form.$('.o_notebook.nav.nav-link:first()'),'active');
        assert.hasClass(form.$('.o_notebook.nav.nav-link:nth(1)'),'active');

        form.destroy();
    });

    QUnit.test('invisibleattrsongrouparere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="bar"/>'+
                        '<groupattrs=\'{"invisible":[["bar","!=",true]]}\'>'+
                            '<group>'+
                                '<fieldname="foo"/>'+
                            '</group>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit'
            },
        });

        assert.containsOnce(form,'div.o_group:visible');
        awaittestUtils.dom.click('.o_field_booleaninput',form);
        assert.containsOnce(form,'div.o_group:hidden');
        form.destroy();
    });

    QUnit.test('invisibleattrswithzerovalueindomainandunsetvalueindata',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.int_field.type='monetary';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="foo"/>'+
                        '<groupattrs=\'{"invisible":[["int_field","=",0.0]]}\'>'+
                            '<divclass="hello">thisshouldbeinvisible</div>'+
                            '<fieldname="int_field"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });

        assert.isNotVisible(form.$('div.hello'));
        form.destroy();
    });

    QUnit.test('resetlocalstatewhenswitchingtoanotherview',asyncfunction(assert){
        assert.expect(3);

        constactionManager=awaitcreateActionManager({
            data:this.data,
            archs:{
                'partner,false,form':`<form>
                        <sheet>
                            <fieldname="product_id"/>
                            <notebook>
                                <pagestring="Foo">
                                    <fieldname="foo"/>
                                </page>
                                <pagestring="Bar">
                                    <fieldname="bar"/>
                                </page>
                            </notebook>
                        </sheet>
                    </form>`,
                'partner,false,list':'<tree><fieldname="foo"/></tree>',
                'partner,false,search':'<search></search>',
            },
            actions:[{
                id:1,
                name:'Partner',
                res_model:'partner',
                type:'ir.actions.act_window',
                views:[[false,'list'],[false,'form']],
            }],
        });

        awaitactionManager.doAction(1);

        awaittestUtils.dom.click(actionManager.$('.o_list_button_add'));
        assert.containsOnce(actionManager,'.o_form_view');

        //clickonsecondpagetab
        awaittestUtils.dom.click(actionManager.$('.o_notebook.nav-link:eq(1)'));

        awaittestUtils.dom.click('.o_control_panel.o_form_button_cancel');
        assert.containsNone(actionManager,'.o_form_view');

        awaittestUtils.dom.click(actionManager.$('.o_list_button_add'));
        //checknotebookactivepageis0thpage
        assert.hasClass(actionManager.$('.o_notebook.nav-link:eq(0)'),'active');

        actionManager.destroy();
    });

    QUnit.test('renderingstatbuttons',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<divname="button_box">'+
                            '<buttonclass="oe_stat_button">'+
                                '<fieldname="int_field"/>'+
                            '</button>'+
                            '<buttonclass="oe_stat_button"attrs=\'{"invisible":[["bar","=",true]]}\'>'+
                                '<fieldname="bar"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.containsN(form,'button.oe_stat_button',2);
        assert.containsOnce(form,'button.oe_stat_button.o_invisible_modifier');

        varcount=0;
        awaittestUtils.mock.intercept(form,"execute_action",function(){
            count++;
        });
        awaittestUtils.dom.click('.oe_stat_button');
        assert.strictEqual(count,1,"shouldhavetriggeredaexecuteaction");
        form.destroy();
    });

    QUnit.test('labelusesthestringattribute',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<labelfor="bar"string="customstring"/>'+
                            '<div><fieldname="bar"/></div>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.containsOnce(form,'label.o_form_label:contains(customstring)');
        form.destroy();
    });

    QUnit.test('inputidsformultipleoccurrencesoffieldsinformview',asyncfunction(assert){
        //Asamefieldcanoccurseveraltimesintheview,butitsidmustbe
        //uniquebyoccurrence,otherwisethereisawarningintheconsole(in
        //editmode)aswegetseveralinputswiththesame"id"attribute,and
        //severallabelsthesame"for"attribute.
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="foo"/>
                        <labelfor="qux"/>
                        <div><fieldname="qux"/></div>
                    </group>
                    <group>
                        <fieldname="foo"/>
                        <labelfor="qux2"/>
                        <div><fieldname="qux"id="qux2"/></div>
                    </group>
                </form>`,
        });

        constfieldIdAttrs=[...form.$('.o_field_widget')].map(n=>n.getAttribute('id'));
        constlabelForAttrs=[...form.$('.o_form_label')].map(n=>n.getAttribute('for'));

        assert.strictEqual([...newSet(fieldIdAttrs)].length,4,
            "shouldhavegeneratedauniqueidforeachfieldoccurrence");
        assert.deepEqual(fieldIdAttrs,labelForAttrs,
            "theforattributeoflabelsmustcoincidewithfieldids");

        form.destroy();
    });

    QUnit.test('inputidsformultipleoccurrencesoffieldsinsubformview(inline)',asyncfunction(assert){
        //Asamefieldcanoccurseveraltimesintheview,butitsidmustbe
        //uniquebyoccurrence,otherwisethereisawarningintheconsole(in
        //editmode)aswegetseveralinputswiththesame"id"attribute,and
        //severallabelsthesame"for"attribute.
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="p">
                        <tree><fieldname="foo"/></tree>
                        <form>
                            <group>
                                <fieldname="foo"/>
                                <labelfor="qux"/>
                                <div><fieldname="qux"/></div>
                            </group>
                            <group>
                                <fieldname="foo"/>
                                <labelfor="qux2"/>
                                <div><fieldname="qux"id="qux2"/></div>
                            </group>
                        </form>
                    </field>
                </form>`,
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

        assert.containsOnce(document.body,'.modal.o_form_view');

        constfieldIdAttrs=[...$('.modal.o_form_view.o_field_widget')].map(n=>n.getAttribute('id'));
        constlabelForAttrs=[...$('.modal.o_form_view.o_form_label')].map(n=>n.getAttribute('for'));

        assert.strictEqual([...newSet(fieldIdAttrs)].length,4,
            "shouldhavegeneratedauniqueidforeachfieldoccurrence");
        assert.deepEqual(fieldIdAttrs,labelForAttrs,
            "theforattributeoflabelsmustcoincidewithfieldids");

        form.destroy();
    });

    QUnit.test('inputidsformultipleoccurrencesoffieldsinsubformview(notinline)',asyncfunction(assert){
        //Asamefieldcanoccurseveraltimesintheview,butitsidmustbe
        //uniquebyoccurrence,otherwisethereisawarningintheconsole(in
        //editmode)aswegetseveralinputswiththesame"id"attribute,and
        //severallabelsthesame"for"attribute.
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="p"/></form>',
            archs:{
                'partner,false,list':'<tree><fieldname="foo"/></tree>',
                'partner,false,form':`
                    <form>
                        <group>
                            <fieldname="foo"/>
                            <labelfor="qux"/>
                            <div><fieldname="qux"/></div>
                        </group>
                        <group>
                            <fieldname="foo"/>
                            <labelfor="qux2"/>
                            <div><fieldname="qux"id="qux2"/></div>
                        </group>
                    </form>`
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

        assert.containsOnce(document.body,'.modal.o_form_view');

        constfieldIdAttrs=[...$('.modal.o_form_view.o_field_widget')].map(n=>n.getAttribute('id'));
        constlabelForAttrs=[...$('.modal.o_form_view.o_form_label')].map(n=>n.getAttribute('for'));

        assert.strictEqual([...newSet(fieldIdAttrs)].length,4,
            "shouldhavegeneratedauniqueidforeachfieldoccurrence");
        assert.deepEqual(fieldIdAttrs,labelForAttrs,
            "theforattributeoflabelsmustcoincidewithfieldids");

        form.destroy();
    });

    QUnit.test('twooccurrencesofinvalidfieldinformview',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.trululu.required=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="trululu"/>
                        <fieldname="trululu"/>
                    </group>
                </form>`,
        });

        awaittestUtils.form.clickSave(form);

        assert.containsN(form,'.o_form_label.o_field_invalid',2);
        assert.containsN(form,'.o_field_many2one.o_field_invalid',2);

        form.destroy();
    });

    QUnit.test('tooltipsonmultipleoccurrencesoffieldsandlabels',asyncfunction(assert){
        assert.expect(4);

        constinitialDebugMode=flectra.debug;
        flectra.debug=false;

        this.data.partner.fields.foo.help='footooltip';
        this.data.partner.fields.bar.help='bartooltip';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="foo"/>
                        <labelfor="bar"/>
                        <div><fieldname="bar"/></div>
                    </group>
                    <group>
                        <fieldname="foo"/>
                        <labelfor="bar2"/>
                        <div><fieldname="bar"id="bar2"/></div>
                    </group>
                </form>`,
        });

        const$fooLabel1=form.$('.o_form_label:nth(0)');
        $fooLabel1.tooltip('show',false);
        $fooLabel1.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),"footooltip");
        $fooLabel1.trigger($.Event('mouseleave'));

        const$fooLabel2=form.$('.o_form_label:nth(2)');
        $fooLabel2.tooltip('show',false);
        $fooLabel2.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),"footooltip");
        $fooLabel2.trigger($.Event('mouseleave'));

        const$barLabel1=form.$('.o_form_label:nth(1)');
        $barLabel1.tooltip('show',false);
        $barLabel1.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),"bartooltip");
        $barLabel1.trigger($.Event('mouseleave'));

        const$barLabel2=form.$('.o_form_label:nth(3)');
        $barLabel2.tooltip('show',false);
        $barLabel2.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),"bartooltip");
        $barLabel2.trigger($.Event('mouseleave'));

        flectra.debug=initialDebugMode;
        form.destroy();
    });

    QUnit.test('readonlyattrsonfieldsarere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"attrs="{\'readonly\':[[\'bar\',\'=\',True]]}"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'span[name="foo"]',
            "thefoofieldwidgetshouldbereadonly");
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));
        assert.containsOnce(form,'input[name="foo"]',
            "thefoofieldwidgetshouldhavebeenrerenderedtonowbeeditable");
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));
        assert.containsOnce(form,'span[name="foo"]',
            "thefoofieldwidgetshouldhavebeenrerenderedtonowbereadonlyagain");
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));
        assert.containsOnce(form,'input[name="foo"]',
            "thefoofieldwidgetshouldhavebeenrerenderedtonowbeeditableagain");

        form.destroy();
    });

    QUnit.test('readonlyattrsonlinesarere-evaluatedonfieldchange2',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].product_ids=[37];
        this.data.partner.records[0].trululu=false;
        this.data.partner.onchanges={
            trululu(record){
                //whentrululuchanges,pushanotherrecordinproduct_ids.
                //onlypushasecondrecordonce.
                if(record.product_ids.map(command=>command[1]).includes(41)){
                    return;
                }
                //copythelisttoforceitasdifferentfromtheoriginal
                record.product_ids=record.product_ids.slice();
                record.product_ids.push([4,41,false]);
            }
        };

        this.data.product.records[0].name='test';
        //Thisoneisnecessarytohaveavalid,renderedwidget
        this.data.product.fields.int_field={type:"integer",string:"intField"};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
            <form>
                <fieldname="trululu"/>
                <fieldname="product_ids"attrs="{'readonly':[['trululu','=',False]]}">
                    <treeeditable="top"><fieldname="int_field"widget="handle"/><fieldname="name"/></tree>
                </field>
            </form>
            `,
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        for(letvalueof[true,false,true,false]){
            if(value){
                awaittestUtils.fields.many2one.clickOpenDropdown('trululu')
                awaittestUtils.fields.many2one.clickHighlightedItem('trululu')
                assert.notOk($('.o_field_one2many[name="product_ids"]').hasClass("o_readonly_modifier"),'linesshouldnotbereadonly')
            }else{
                awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2one[name="trululu"]input'),'',['keyup'])
                assert.ok($('.o_field_one2many[name="product_ids"]').hasClass("o_readonly_modifier"),'linesshouldbereadonly')
            }
        }

        form.destroy();
    });

    QUnit.test('emptyfieldshaveo_form_emptyclassinreadonlymode',asyncfunction(assert){
        assert.expect(8);

        this.data.partner.fields.foo.default=false;//nodefaultvalueforthistest
        this.data.partner.records[1].foo=false; //1isrecordwithid=2
        this.data.partner.records[1].trululu=false; //1isrecordwithid=2
        this.data.partner.fields.int_field.readonly=true;
        this.data.partner.onchanges.foo=function(obj){
            if(obj.foo==="hello"){
                obj.int_field=false;
            }
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="trululu"attrs="{\'readonly\':[[\'foo\',\'=\',False]]}"/>'+
                            '<fieldname="int_field"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.containsN(form,'.o_field_widget.o_field_empty',2,
            "shouldhave2emptyfieldswithcorrectclass");
        assert.containsN(form,'.o_form_label_empty',2,
            "shouldhave2mutedlabels(fortheemptyfieds)inreadonly");

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'.o_field_empty',
            "ineditmode,onlyemptyreadonlyfieldsshouldhavetheo_field_emptyclass");
        assert.containsOnce(form,'.o_form_label_empty',
            "ineditmode,onlylabelsassociatedtoemptyreadonlyfieldsshouldhavetheo_form_label_emptyclass");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'test');

        assert.containsNone(form,'.o_field_empty',
            "afterreadonlymodifierchange,theo_field_emptyclassshouldhavebeenremoved");
        assert.containsNone(form,'.o_form_label_empty',
            "afterreadonlymodifierchange,theo_form_label_emptyclassshouldhavebeenremoved");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'hello');

        assert.containsOnce(form,'.o_field_empty',
            "aftervaluechangedtofalseforareadonlyfield,theo_field_emptyclassshouldhavebeenadded");
        assert.containsOnce(form,'.o_form_label_empty',
            "aftervaluechangedtofalseforareadonlyfield,theo_form_label_emptyclassshouldhavebeenadded");

        form.destroy();
    });

    QUnit.test('emptyfields\'labelsstillgettheemptyclassafterwidgetrerender',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.foo.default=false;//nodefaultvalueforthistest
        this.data.partner.records[1].foo=false; //1isrecordwithid=2
        this.data.partner.records[1].display_name=false; //1isrecordwithid=2

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="display_name"attrs="{\'readonly\':[[\'foo\',\'=\',\'readonly\']]}"/>'+
                    '</group>'+
                '</form>',
            res_id:2,
        });

        assert.containsN(form,'.o_field_widget.o_field_empty',2);
        assert.containsN(form,'.o_form_label_empty',2,
            "shouldhave1mutedlabel(fortheemptyfied)inreadonly");

        awaittestUtils.form.clickEdit(form);

        assert.containsNone(form,'.o_field_empty',
            "ineditmode,onlyemptyreadonlyfieldsshouldhavetheo_field_emptyclass");
        assert.containsNone(form,'.o_form_label_empty',
            "ineditmode,onlylabelsassociatedtoemptyreadonlyfieldsshouldhavetheo_form_label_emptyclass");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'readonly');
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'edit');
        awaittestUtils.fields.editInput(form.$('input[name=display_name]'),'somename');
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'readonly');

        assert.containsNone(form,'.o_field_empty',
            "therestillshouldnotbeanyemptyclassonfieldsasthereadonlyoneisnowset");
        assert.containsNone(form,'.o_form_label_empty',
            "therestillshouldnotbeanyemptyclassonlabelsastheassociatedreadonlyfieldisnowset");

        form.destroy();
    });

    QUnit.test('emptyinnerreadonlyfieldsdon\'thaveo_form_emptyclassin"create"mode',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.product_id.readonly=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<group>'+
                                '<fieldname="product_id"/>'+
                            '</group>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });
        assert.containsNone(form,'.o_form_label_empty',
                "noemptyclassonlabel");
        assert.containsNone(form,'.o_field_empty',
                "noemptyclassonfield");
        form.destroy();
    });

    QUnit.test('formviewcanswitchtoeditmode',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.mode,'readonly','formviewshouldbeinreadonlymode');
        assert.hasClass(form.$('.o_form_view'),'o_form_readonly');
        assert.isVisible(form.$buttons.find('.o_form_buttons_view'));
        assert.isNotVisible(form.$buttons.find('.o_form_buttons_edit'));

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.mode,'edit','formviewshouldbeineditmode');
        assert.hasClass(form.$('.o_form_view'),'o_form_editable');
        assert.doesNotHaveClass(form.$('.o_form_view'),'o_form_readonly');
        assert.isNotVisible(form.$buttons.find('.o_form_buttons_view'));
        assert.isVisible(form.$buttons.find('.o_form_buttons_edit'));
        form.destroy();
    });

    QUnit.test('requiredattrsonfieldsarere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"attrs="{\'required\':[[\'bar\',\'=\',True]]}"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'input[name="foo"].o_required_modifier',
            "thefoofieldwidgetshouldberequired");
        awaittestUtils.dom.click('.o_field_booleaninput');
        assert.containsOnce(form,'input[name="foo"]:not(.o_required_modifier)',
            "thefoofieldwidgetshouldnowhavebeenmarkedasnon-required");
        awaittestUtils.dom.click('.o_field_booleaninput');
        assert.containsOnce(form,'input[name="foo"].o_required_modifier',
            "thefoofieldwidgetshouldnowhavebeenmarkedasrequiredagain");

        form.destroy();
    });

    QUnit.test('requiredfieldsshouldhaveo_required_modifierinreadonlymode',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.foo.required=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'span.o_required_modifier',form);

        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'input.o_required_modifier',
                    "ineditmode,shouldhave1inputwitho_required_modifier");
        form.destroy();
    });

    QUnit.test('requiredfloatfieldsworksasexpected',asyncfunction(assert){
        assert.expect(10);

        this.data.partner.fields.qux.required=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="qux"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
        });

        assert.hasClass(form.$('input[name="qux"]'),'o_required_modifier');
        assert.strictEqual(form.$('input[name="qux"]').val(),"0.0",
            "quxinputis0bydefault(floatfield)");

        awaittestUtils.form.clickSave(form);

        assert.containsNone(form.$('input[name="qux"]'),"shouldhaveswitchedtoreadonly");

        awaittestUtils.form.clickEdit(form);

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'1');

        awaittestUtils.form.clickSave(form);

        awaittestUtils.form.clickEdit(form);

                assert.strictEqual(form.$('input[name="qux"]').val(),"1.0",
            "quxinputisproperlyformatted");

        assert.verifySteps(['onchange','create','read','write','read']);
        form.destroy();
    });

    QUnit.test('separators',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<separatorstring="Geolocation"/>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'div.o_horizontal_separator');
        form.destroy();
    });

    QUnit.test('invisibleattrsonseparators',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<separatorstring="Geolocation"attrs=\'{"invisible":[["bar","=",True]]}\'/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.hasClass(form.$('div.o_horizontal_separator'),'o_invisible_modifier');

        form.destroy();
    });

    QUnit.test('buttonsinformview',asyncfunction(assert){
        assert.expect(8);

        varrpcCount=0;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="state"invisible="1"/>'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"/>'+
                        '<buttonname="some_method"class="s"string="Doit"type="object"/>'+
                        '<buttonname="some_other_method"states="ab,ef"string="Donot"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<buttonstring="Geolocate"name="geo_localize"icon="fa-check"type="object"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            mockRPC:function(){
                rpcCount++;
                returnthis._super.apply(this,arguments);
            },
        });
        assert.containsOnce(form,'button.btni.fa.fa-check');
        assert.containsN(form,'.o_form_statusbarbutton',3);
        assert.containsOnce(form,'button.p[name="post"]:contains(Confirm)');
        assert.containsN(form,'.o_form_statusbarbutton:visible',2);

        awaittestUtils.mock.intercept(form,'execute_action',function(ev){
            assert.strictEqual(ev.data.action_data.name,'post',
                "shouldtriggerexecute_actionwithcorrectmethodname");
            assert.deepEqual(ev.data.env.currentID,2,"shouldhavecorrectidinevdata");
            ev.data.on_success();
            ev.data.on_closed();
        });
        rpcCount=0;
        awaittestUtils.dom.click('.o_form_statusbarbutton.p',form);

        assert.strictEqual(rpcCount,1,"shouldhavedone1rpcstoreload");

        awaittestUtils.mock.intercept(form,'execute_action',function(ev){
            ev.data.on_fail();
        });
        awaittestUtils.dom.click('.o_form_statusbarbutton.s',form);

        assert.strictEqual(rpcCount,1,
            "shouldhavedone1rpc,becausewedonotreloadanymoreiftheserveractionfails");

        form.destroy();
    });

    QUnit.test('buttonsclassesinformview',asyncfunction(assert){
        assert.expect(16);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="0"/>'+
                        '<buttonname="1"class="btn-primary"/>'+
                        '<buttonname="2"class="oe_highlight"/>'+
                        '<buttonname="3"class="btn-secondary"/>'+
                        '<buttonname="4"class="btn-link"/>'+
                        '<buttonname="5"class="oe_link"/>'+
                        '<buttonname="6"class="btn-success"/>'+
                        '<buttonname="7"class="o_this_is_a_button"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<buttonname="8"/>'+
                        '<buttonname="9"class="btn-primary"/>'+
                        '<buttonname="10"class="oe_highlight"/>'+
                        '<buttonname="11"class="btn-secondary"/>'+
                        '<buttonname="12"class="btn-link"/>'+
                        '<buttonname="13"class="oe_link"/>'+
                        '<buttonname="14"class="btn-success"/>'+
                        '<buttonname="15"class="o_this_is_a_button"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.hasAttrValue(form.$('button[name="0"]'),'class','btnbtn-secondary');
        assert.hasAttrValue(form.$('button[name="1"]'),'class','btnbtn-primary');
        assert.hasAttrValue(form.$('button[name="2"]'),'class','btnbtn-primary');
        assert.hasAttrValue(form.$('button[name="3"]'),'class','btnbtn-secondary');
        assert.hasAttrValue(form.$('button[name="4"]'),'class','btnbtn-link');
        assert.hasAttrValue(form.$('button[name="5"]'),'class','btnbtn-link');
        assert.hasAttrValue(form.$('button[name="6"]'),'class','btnbtn-success');
        assert.hasAttrValue(form.$('button[name="7"]'),'class','btno_this_is_a_buttonbtn-secondary');
        assert.hasAttrValue(form.$('button[name="8"]'),'class','btnbtn-secondary');
        assert.hasAttrValue(form.$('button[name="9"]'),'class','btnbtn-primary');
        assert.hasAttrValue(form.$('button[name="10"]'),'class','btnbtn-primary');
        assert.hasAttrValue(form.$('button[name="11"]'),'class','btnbtn-secondary');
        assert.hasAttrValue(form.$('button[name="12"]'),'class','btnbtn-link');
        assert.hasAttrValue(form.$('button[name="13"]'),'class','btnbtn-link');
        assert.hasAttrValue(form.$('button[name="14"]'),'class','btnbtn-success');
        assert.hasAttrValue(form.$('button[name="15"]'),'class','btno_this_is_a_button');

        form.destroy();
    });

    QUnit.test('buttoninformviewandlongwillStart',asyncfunction(assert){
        assert.expect(6);

        varrpcCount=0;

        varFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            willStart:function(){
                assert.step('load'+rpcCount);
                if(rpcCount===2){
                    return$.Deferred();
                }
                return$.Deferred().resolve();
            },
        }));

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="state"invisible="1"/>'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="asyncwidget"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            mockRPC:function(){
                rpcCount++;
                returnthis._super.apply(this,arguments);
            },
        });
        assert.verifySteps(['load1']);

        awaittestUtils.mock.intercept(form,'execute_action',function(ev){
            ev.data.on_success();
            ev.data.on_closed();
        });

        awaittestUtils.dom.click('.o_form_statusbarbutton.p',form);
        assert.verifySteps(['load2']);

        testUtils.mock.intercept(form,'execute_action',function(ev){
            ev.data.on_success();
            ev.data.on_closed();
        });

        awaittestUtils.dom.click('.o_form_statusbarbutton.p',form);
        assert.verifySteps(['load3']);

        form.destroy();
    });

    QUnit.test('buttonsinformview,newrecord',asyncfunction(assert){
        //thissimulatesasituationsimilartothesettingsforms.
        assert.expect(7);

        varresID;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"/>'+
                        '<buttonname="some_method"class="s"string="Doit"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<buttonstring="Geolocate"name="geo_localize"icon="fa-check"type="object"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                if(args.method==='create'){
                    returnthis._super.apply(this,arguments).then(function(result){
                        resID=result;
                        returnresID;
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.mock.intercept(form,'execute_action',function(event){
            assert.step('execute_action');
            assert.deepEqual(event.data.env.currentID,resID,
                "executeactionshouldbedoneoncorrectrecordid");
            event.data.on_success();
            event.data.on_closed();
        });
        awaittestUtils.dom.click('.o_form_statusbarbutton.p',form);

        assert.verifySteps(['onchange','create','read','execute_action','read']);
        form.destroy();
    });

    QUnit.test('buttonsinformview,newrecord,withfieldidinview',asyncfunction(assert){
        assert.expect(7);
        //buttonsinformviewareoneoftherareexampleofsituationwhenwe
        //savearecordwithoutreloadingitimmediately,becauseweonlycare
        //aboutitsidforthenextstep. Butatsomepoint,ifthefieldid
        //isintheview,itwasregisteredinthechanges,andcausedinvalid
        //valuesintherecord(data.idwassettonull)

        varresID;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="id"invisible="1"/>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                if(args.method==='create'){
                    returnthis._super.apply(this,arguments).then(function(result){
                        resID=result;
                        returnresID;
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.mock.intercept(form,'execute_action',function(event){
            assert.step('execute_action');
            assert.deepEqual(event.data.env.currentID,resID,
                "executeactionshouldbedoneoncorrectrecordid");
            event.data.on_success();
            event.data.on_closed();
        });
        awaittestUtils.dom.click('.o_form_statusbarbutton.p',form);

        assert.verifySteps(['onchange','create','read','execute_action','read']);
        form.destroy();
    });

    QUnit.test('changeandsavechar',asyncfunction(assert){
        assert.expect(6);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/></group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.ok(true,"shouldcallthe/writeroute");
                }
                returnthis._super(route,args);
            },
            res_id:2,
        });

        assert.strictEqual(form.mode,'readonly','formviewshouldbeinreadonlymode');
        assert.containsOnce(form,'span:contains(blip)',
                        "shouldcontainspanwithfieldvalue");

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.mode,'edit','formviewshouldbeineditmode');
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');
        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.mode,'readonly','formviewshouldbeinreadonlymode');
        assert.containsOnce(form,'span:contains(tralala)',
                        "shouldcontainspanwithfieldvalue");
        form.destroy();
    });

    QUnit.test('properlyreloaddatafromserver',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/></group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    args.args[1].foo="apple";
                }
                returnthis._super(route,args);
            },
            res_id:2,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'span:contains(apple)',
                        "shouldcontainspanwithfieldvalue");
        form.destroy();
    });

    QUnit.test('disablebuttonsuntilreloaddatafromserver',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/></group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    args.args[1].foo="apple";
                }elseif(args.method==='read'){
                    //Blockthe'read'call
                    varresult=this._super.apply(this,arguments);
                    returnPromise.resolve(def).then(result);
                }
                returnthis._super(route,args);
            },
            res_id:2,
        });

        vardef=testUtils.makeTestPromise();
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');
        awaittestUtils.form.clickSave(form);

        //Savebuttonshouldbedisabled
        assert.hasAttrValue(form.$buttons.find('.o_form_button_save'),'disabled','disabled');
        //Releasethe'read'call
        awaitdef.resolve();
        awaittestUtils.nextTick();

        //Editbuttonshouldbeenabledafterthereload
        assert.hasAttrValue(form.$buttons.find('.o_form_button_edit'),'disabled',undefined);

        form.destroy();
    });

    QUnit.test('properlyapplyonchangeinsimplecase',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.onchanges={
            foo:function(obj){
                obj.int_field=obj.foo.length+1000;
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
        });

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('input[name=int_field]').val(),"9",
                        "shouldcontaininputwithinitialvalue");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        assert.strictEqual(form.$('input[name=int_field]').val(),"1007",
                        "shouldcontaininputwithonchangeapplied");
        form.destroy();
    });

    QUnit.test('properlyapplyonchangewhenchangedfieldisactivefield',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.onchanges={
            int_field:function(obj){
                obj.int_field=14;
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
            viewOptions:{mode:'edit'},
        });


        assert.strictEqual(form.$('input[name=int_field]').val(),"9",
                        "shouldcontaininputwithinitialvalue");

        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),'666');

        assert.strictEqual(form.$('input[name=int_field]').val(),"14",
                "valueshouldhavebeensetto14byonchange");

        awaittestUtils.form.clickSave(form);

                assert.strictEqual(form.$('.o_field_widget[name=int_field]').text(),"14",
            "valueshouldstillbe14");

        form.destroy();
    });

    QUnit.test('onchangesendonlythepresentfieldstotheserver',asyncfunction(assert){
        assert.expect(1);
        this.data.partner.records[0].product_id=false;
        this.data.partner.onchanges.foo=function(obj){
            obj.foo=obj.foo+"alligator";
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="bar"/>'+
                            '<fieldname="product_id"/>'+
                        '</tree>'+
                    '</field>'+
                    '<fieldname="timmy"/>'+
                '</form>',
            archs:{
                "partner_type,false,list":'<tree><fieldname="name"/></tree>'
            },
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==="onchange"){
                    assert.deepEqual(args.args[3],
                        {"foo":"1","p":"","p.bar":"","p.product_id":"","timmy":"","timmy.name":""},
                        "shouldsendonlythefieldsusedintheviews");
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        form.destroy();
    });

    QUnit.test('onchangeonlysendpresentfieldsvalue',asyncfunction(assert){
        assert.expect(1);
        this.data.partner.onchanges.foo=function(obj){};

        letcheckOnchange=false;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                        '<treeeditable="top">'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="qux"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==="onchange"&&checkOnchange){
                    assert.deepEqual(args.args[1],{
                        display_name:"firstrecord",
                        foo:"tralala",
                        id:1,
                        p:[[0,args.args[1].p[0][1],{"display_name":"validline","qux":12.4}]]
                    },"shouldsendthevaluesforthepresentfields");
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickEdit(form);

        //addao2mrow
        awaittestUtils.dom.click('.o_field_x2many_list_row_adda');
        form.$('.o_field_one2manyinput:first').focus();
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput(form.$('.o_field_one2manyinput[name=display_name]'),'validline');
        form.$('.o_field_one2manyinput:last').focus();
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput(form.$('.o_field_one2manyinput[name=qux]'),'12.4');

        //triggeranonchangebymodifyingfoo
        checkOnchange=true;
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        form.destroy();
    });

    QUnit.test('evaluateinpythonfieldoptions',asyncfunction(assert){
        assert.expect(1);

        varisOk=false;
        vartmp=py.eval;
        py.eval=function(expr){
            if(expr==="{'horizontal':true}"){
                isOk=true;
            }
            returntmp.apply(tmp,arguments);
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"options="{\'horizontal\':true}"/>'+
                '</form>',
            res_id:2,
        });

        py.eval=tmp;

        assert.ok(isOk,"shouldhaveevaluatedthefieldoptions");
        form.destroy();
    });

    QUnit.test('cancreatearecordwithdefaultvalues',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                context:{active_field:2},
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.strictEqual(args.kwargs.context.active_field,2,
                        "shouldhavesendthecorrectcontext");
                }
                returnthis._super.apply(this,arguments);
            },
        });
        varn=this.data.partner.records.length;

        awaittestUtils.form.clickCreate(form);
        assert.strictEqual(form.mode,'edit','formviewshouldbeineditmode');

        assert.strictEqual(form.$('input:first').val(),"MylittleFooValue",
            "shouldhavecorrectdefault_getvalue");
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.mode,'readonly','formviewshouldbeinreadonlymode');
        assert.strictEqual(this.data.partner.records.length,n+1,"shouldhavecreatedarecord");
        form.destroy();
    });

    QUnit.test('defaultrecordwithaone2manyandanonchangeonsubfield',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.onchanges.foo=function(){};

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
                assert.step(args.method);
                if(args.method==='onchange'){
                    assert.deepEqual(args.args[3],{
                        p:'',
                        'p.foo':'1'
                    },"onchangeSpecshouldbecorrect(withsubfields)");
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.verifySteps(['onchange']);
        form.destroy();
    });

    QUnit.test('removedefaultvalueinsubviews',asyncfunction(assert){
        assert.expect(2);

        this.data.product.onchanges={}
        this.data.product.onchanges.name=function(){};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            viewOptions:{
                context:{default_state:"ab"}
            },
            arch:'<formstring="Partners">'+
                    '<fieldname="product_ids"context="{\'default_product_uom_qty\':68}">'+
                      '<treeeditable="top">'+
                        '<fieldname="name"/>'+
                      '</tree>'+
                    '</field>'+
                  '</form>',
            mockRPC:function(route,args){
                if(route==="/web/dataset/call_kw/partner/onchange"){
                    assert.deepEqual(args.kwargs.context,{
                        default_state:'ab',
                    })
                }
                elseif(route==="/web/dataset/call_kw/product/onchange"){
                    assert.deepEqual(args.kwargs.context,{
                        default_product_uom_qty:68,
                    })
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        form.destroy();
    });

    QUnit.test('referencefieldinone2manylist',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].reference='partner,2';

        varform=awaitcreateView({
            View:FormView,
            model:'user',
            data:this.data,
            arch:`<form>
                        <fieldname="name"/>
                        <fieldname="partner_ids">
                            <treeeditable="bottom">
                                <fieldname="display_name"/>
                                <fieldname="reference"/>
                            </tree>
                       </field>
                   </form>`,
            archs:{
                'partner,false,form':'<form><fieldname="display_name"/></form>',
            },
            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
            res_id:17,
        });
        //currentform
        awaittestUtils.form.clickEdit(form);

        //openthemodalformviewoftherecordpointedbythereferencefield
        awaittestUtils.dom.click(form.$('tabletd[title="firstrecord"]'));
        awaittestUtils.dom.click(form.$('tabletdbutton.o_external_button'));

        //edittherecordinthemodal
        awaittestUtils.fields.editInput($('.modal-bodyinput[name="display_name"]'),'Newname');
        awaittestUtils.dom.click($('.modal-dialogfooterbutton:first-child'));

        assert.containsOnce(form,'.o_field_cell[title="Newname"]','shouldnotcrashandvaluemustbeedited');

        form.destroy();
    });

    QUnit.test('toolbarishiddenwhenswitchingtoeditmode',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="foo"/>'+
                    '</sheet>'+
                '</form>',
            viewOptions:{hasActionMenus:true},
            res_id:1,
        });

        assert.containsOnce(form,'.o_cp_action_menus');

        awaittestUtils.form.clickEdit(form);

        assert.containsNone(form,'.o_cp_action_menus');

        awaittestUtils.form.clickDiscard(form);

        assert.containsOnce(form,'.o_cp_action_menus');

        form.destroy();
    });

    QUnit.test('basicdefaultrecord',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.foo.default="defaultfoovalue";

        varcount=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            mockRPC:function(route,args){
                count++;
                returnthis._super(route,args);
            },
        });

        assert.strictEqual(form.$('input[name=foo]').val(),"defaultfoovalue","shouldhavecorrectdefault");
        assert.strictEqual(count,1,"shoulddoonlyonerpc");
        form.destroy();
    });

    QUnit.test('makedefaultrecordwithnonemptyone2many',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.p.default=[
            [6,0,[]],                 //replacewithzeroids
            [0,0,{foo:"newfoo1",product_id:41,p:[]}],  //createanewvalue
            [0,0,{foo:"newfoo2",product_id:37,p:[]}],  //createanewvalue
        ];

        varnameGetCount=0;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="product_id"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='name_get'){
                    nameGetCount++;
                }
                returnthis._super(route,args);
            },
        });
        assert.containsOnce(form,'td:contains(newfoo1)',
            "shouldhavenewfoo1valueinone2many");
        assert.containsOnce(form,'td:contains(newfoo2)',
            "shouldhavenewfoo2valueinone2many");
        assert.containsOnce(form,'td:contains(xphone)',
            "shouldhaveacellwiththenamefield'product_id',settoxphone");
        assert.strictEqual(nameGetCount,0,"shouldhavedonenonameget");
        form.destroy();
    });

    QUnit.test('makedefaultrecordwithnonemptymany2one',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.trululu.default=4;

        varnameGetCount=0;

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="trululu"/></form>',
            mockRPC:function(route,args){
                if(args.method==='name_get'){
                    nameGetCount++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name=trululu]input').val(),'aaa',
            "defaultvalueshouldbecorrectlydisplayed");
        assert.strictEqual(nameGetCount,0,"shouldhavedonenoname_get");

        form.destroy();
    });

    QUnit.test('formviewproperlychangeitstitle',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),'firstrecord',
            "shouldhavethedisplaynameoftherecordas title");

        awaittestUtils.form.clickCreate(form);
        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),_t("New"),
            "shouldhavethedisplaynameoftherecordastitle");

        form.destroy();
    });

    QUnit.test('archive/unarchivearecord',asyncfunction(assert){
        assert.expect(10);

        //addactivefieldonpartnermodeltohavearchiveoption
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            res_id:1,
            viewOptions:{hasActionMenus:true},
            arch:'<form><fieldname="active"/><fieldname="foo"/></form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                if(args.method==='action_archive'){
                    this.data.partner.records[0].active=false;
                    returnPromise.resolve();
                }
                if(args.method==='action_unarchive'){
                    this.data.partner.records[0].active=true;
                    returnPromise.resolve();
                }
                returnthis._super(...arguments);
            },
        });

        awaitcpHelpers.toggleActionMenu(form);
        assert.containsOnce(form,'.o_cp_action_menusa:contains(Archive)');

        awaitcpHelpers.toggleMenuItem(form,"Archive");
        assert.containsOnce(document.body,'.modal');

        awaittestUtils.dom.click($('.modal-footer.btn-primary'));
        awaitcpHelpers.toggleActionMenu(form);
        assert.containsOnce(form,'.o_cp_action_menusa:contains(Unarchive)');

        awaitcpHelpers.toggleMenuItem(form,"Unarchive");
        awaitcpHelpers.toggleActionMenu(form);
        assert.containsOnce(form,'.o_cp_action_menusa:contains(Archive)');

        assert.verifySteps([
            'read',
            'action_archive',
            'read',
            'action_unarchive',
            'read',
        ]);

        form.destroy();
    });

    QUnit.test('archiveactionwithactivefieldnotinview',asyncfunction(assert){
        assert.expect(2);

        //addactivefieldonpartnermodel,butdonotputitintheview
        this.data.partner.fields.active={string:'Active',type:'char',default:true};

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            res_id:1,
            viewOptions:{hasActionMenus:true},
            arch:'<form><fieldname="foo"/></form>',
        });

        awaitcpHelpers.toggleActionMenu(form);
        assert.containsNone(form,'.o_cp_action_menusa:contains(Archive)');
        assert.containsNone(form,'.o_cp_action_menusa:contains(Unarchive)');

        form.destroy();
    });

    QUnit.test('canduplicatearecord',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
            viewOptions:{hasActionMenus:true},
        });

        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),'firstrecord',
            "shouldhavethedisplaynameoftherecordas title");

        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Duplicate");

        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),'firstrecord(copy)',
            "shouldhaveduplicatedtherecord");

        assert.strictEqual(form.mode,"edit",'shouldbeineditmode');
        form.destroy();
    });

    QUnit.test('duplicatingarecordpreservethecontext',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
            viewOptions:{hasActionMenus:true,context:{hey:'hoy'}},
            mockRPC:function(route,args){
                if(args.method==='read'){
                    //shouldhave2read,oneforinitialload,secondfor
                    //readafterduplicating
                    assert.strictEqual(args.kwargs.context.hey,'hoy',
                        "shouldhavesendthecorrectcontext");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Duplicate");

        form.destroy();
    });

    QUnit.test('cannotduplicatearecord',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"duplicate="false">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
            viewOptions:{hasActionMenus:true},
        });

        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),'firstrecord',
            "shouldhavethedisplaynameoftherecordas title");
        assert.containsNone(form,'.o_cp_action_menusa:contains(Duplicate)',
            "shouldnotcontainsa'Duplicate'action");
        form.destroy();
    });

    QUnit.test('clickingonstatbuttonsineditmode',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<divname="button_box">'+
                            '<buttonclass="oe_stat_button">'+
                                '<fieldname="bar"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].foo,"tralala","shouldhavesavedthechanges");
                }
                assert.step(args.method);
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickEdit(form);

        varcount=0;
        awaittestUtils.mock.intercept(form,"execute_action",function(event){
            event.stopPropagation();
            count++;
        });
        awaittestUtils.dom.click('.oe_stat_button');
        assert.strictEqual(count,1,"shouldhavetriggeredaexecuteaction");
        assert.strictEqual(form.mode,"edit","formviewshouldbeineditmode");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');
        awaittestUtils.dom.click('.oe_stat_button:first');

                assert.strictEqual(form.mode,"edit","formviewshouldbeineditmode");
        assert.strictEqual(count,2,"shouldhavetriggeredaexecuteaction");
        assert.verifySteps(['read','write','read']);
        form.destroy();
    });

    QUnit.test('clickingonstatbuttonssaveandreloadineditmode',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<divname="button_box">'+
                            '<buttonclass="oe_stat_button"type="action">'+
                                '<fieldname="int_field"widget="statinfo"string="Somenumber"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="name"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    //simulateanoverrideofthemodel...
                    args.args[1].display_name="GOLDORAK";
                    args.args[1].name="GOLDORAK";
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),'secondrecord',
            "shouldhavecorrectdisplay_name");
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=name]'),'someothername');

        awaittestUtils.dom.click('.oe_stat_button');
        assert.strictEqual(form.$('.o_control_panel.breadcrumb').text(),'GOLDORAK',
            "shouldhavecorrectdisplay_name");

        form.destroy();
    });

    QUnit.test('buttonswithattr"special"donottriggerasave',asyncfunction(assert){
        assert.expect(4);

        varexecuteActionCount=0;
        varwriteCount=0;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                        '<buttonstring="Dosomething"class="btn-primary"name="abc"type="object"/>'+
                        '<buttonstring="Ordiscard"class="btn-secondary"special="cancel"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    writeCount++;
                }
                returnthis._super(route,args);
            },
        });
        awaittestUtils.mock.intercept(form,"execute_action",function(){
            executeActionCount++;
        });

        awaittestUtils.form.clickEdit(form);

        //maketherecorddirty
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        awaittestUtils.dom.click(form.$('button:contains(Dosomething)'));
        //TODO:VSC:addanexttick?
        assert.strictEqual(writeCount,1,"shouldhavetriggeredawrite");
        assert.strictEqual(executeActionCount,1,"shouldhavetriggeredaexecuteaction");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'abcdef');

        awaittestUtils.dom.click(form.$('button:contains(Ordiscard)'));
        assert.strictEqual(writeCount,1,"shouldnothavetriggeredawrite");
        assert.strictEqual(executeActionCount,2,"shouldhavetriggeredaexecuteaction");

        form.destroy();
    });

    QUnit.test('buttonswithattr"special=save"save',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                        '<buttonstring="Save"class="btn-primary"special="save"/>'+
                '</form>',
            res_id:1,
            intercepts:{
                execute_action:function(){
                    assert.step('execute_action');
                },
            },
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super(route,args);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');
        awaittestUtils.dom.click(form.$('button[special="save"]'));
        assert.verifySteps(['read','write','read','execute_action']);

        form.destroy();
    });

    QUnit.test('missingwidgetsdonotcrash',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo.type='newfieldtypewithoutwidget';
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });
        assert.containsOnce(form,'.o_field_widget');
        form.destroy();
    });

    QUnit.test('nolabel',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<groupclass="firstgroup"><fieldname="foo"nolabel="1"/></group>'+
                            '<groupclass="secondgroup">'+
                                '<fieldname="product_id"/>'+
                                '<fieldname="int_field"nolabel="1"/><fieldname="qux"nolabel="1"/>'+
                            '</group>'+
                            '<group><fieldname="bar"/></group>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsN(form,"label.o_form_label",2);
        assert.strictEqual(form.$("label.o_form_label").first().text(),"Product",
            "oneshouldbetheonefortheproductfield");
        assert.strictEqual(form.$("label.o_form_label").eq(1).text(),"Bar",
            "oneshouldbetheoneforthebarfield");

        assert.hasAttrValue(form.$('.firstgrouptd').first(),'colspan',undefined,
            "footdshouldhaveadefaultcolspan(1)");
        assert.containsN(form,'.secondgrouptr',2,
            "int_fieldandquxshouldhavesametr");

        assert.containsN(form,'.secondgrouptr:firsttd',2,
            "product_idfieldshouldbeonitsowntr");
        form.destroy();
    });

    QUnit.test('many2oneinaone2many',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].p=[2];
        this.data.partner.records[1].product_id=37;

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
        });
        assert.containsOnce(form,'td:contains(xphone)',"shoulddisplaythenameofthemany2one");
        form.destroy();
    });

    QUnit.test('circularmany2many\'s',asyncfunction(assert){
        assert.expect(4);
        this.data.partner_type.fields.partner_ids={string:"partners",type:"many2many",relation:'partner'};
        this.data.partner.records[0].timmy=[12];
        this.data.partner_type.records[0].partner_ids=[1];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                        '<form>'+
                            '<fieldname="partner_ids">'+
                                '<tree>'+
                                    '<fieldname="display_name"/>'+
                                '</tree>'+
                                '<form>'+
                                    '<fieldname="display_name"/>'+
                                '</form>'+
                            '</field>'+
                        '</form>'+
                    '</field>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'td:contains(gold)',
            "shoulddisplaythenameofthemany2manyontheoriginalform");
        awaittestUtils.dom.click(form.$('td:contains(gold)'));

        assert.containsOnce(document.body,'.modal');
        assert.containsOnce($('.modal'),'td:contains(firstrecord)',
            "shoulddisplaythenameofthemany2manyonthemodalform");

        awaittestUtils.dom.click('.modaltd:contains(firstrecord)');
        assert.containsN(document.body,'.modal',2,
            "thereshouldbe2modals(partnerontopofpartner_type)opened");

        form.destroy();
    });

    QUnit.test('discardchangesonanondirtyformview',asyncfunction(assert){
        assert.expect(4);

        varnbWrite=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            res_id:1,
            mockRPC:function(route){
                if(route==='/web/dataset/call_kw/partner/write'){
                    nbWrite++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=foo]').val(),'yop',
            "inputshouldcontainyop");

        //clickondiscard
        awaittestUtils.form.clickDiscard(form);
        assert.containsNone(document.body,'.modal','noconfirmmodalshouldbedisplayed');
        assert.strictEqual(form.$('.o_field_widget').text(),'yop','fieldinreadonlyshoulddisplayyop');

        assert.strictEqual(nbWrite,0,"nowriteRPCshouldhavebeendone");
        form.destroy();
    });

    QUnit.test('discardchangesonadirtyformview',asyncfunction(assert){
        assert.expect(7);

        varnbWrite=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            res_id:1,
            mockRPC:function(route){
                if(route==='/web/dataset/call_kw/partner/write'){
                    nbWrite++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //switchtoeditmodeandeditthefoofield
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=foo]').val(),'yop',"inputshouldcontainyop");
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'newvalue');
        assert.strictEqual(form.$('input[name=foo]').val(),'newvalue',
            "inputshouldcontainnewvalue");

        //clickondiscardandcanceltheconfirmrequest
        awaittestUtils.form.clickDiscard(form);
        assert.containsOnce(document.body,'.modal',"aconfirmmodalshouldbedisplayed");
        awaittestUtils.dom.click('.modal-footer.btn-secondary');
        assert.strictEqual(form.$('input').val(),'newvalue','inputshouldstillcontainnewvalue');

        //clickondiscardandconfirm
        awaittestUtils.form.clickDiscard(form);
        assert.containsOnce(document.body,'.modal',"aconfirmmodalshouldbedisplayed");
        awaittestUtils.dom.click('.modal-footer.btn-primary');
        assert.strictEqual(form.$('.o_field_widget').text(),'yop','fieldinreadonlyshoulddisplayyop');

        assert.strictEqual(nbWrite,0,"nowriteRPCshouldhavebeendone");
        form.destroy();
    });

    QUnit.test('discardchangesonadirtyformview(fordatefield)',asyncfunction(assert){
        assert.expect(1);

        //thistestchecksthatthebasicmodelproperlyhandlesdateobject
        //whentheyarediscardedandsaved. Thismaybeanissuebecause
        //datesaresavedasmomentobject,andwereatonepointstringified,
        //thenparsedintostring,whichiswrong.

        this.data.partner.fields.date.default="2017-01-25";
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"></field></form>',
            intercepts:{
                history_back:function(){
                    form.update({},{reload:false});
                }
            },
        });

        //focusthebuttonsbeforeclickingonthemtopreciselyreproducewhat
        //reallyhappens(mostlybecausethedatepickerlibneedthatfocus
        //eventtoproperlyfocusouttheinput,otherwiseitcrasheslateron
        //whenthe'blur'eventistriggeredbythere-rendering)
        form.$buttons.find('.o_form_button_cancel').focus();
        awaittestUtils.dom.click('.o_form_button_cancel');
        form.$buttons.find('.o_form_button_save').focus();
        awaittestUtils.dom.click('.o_form_button_save');
        assert.containsOnce(form,'span:contains(2017)');

        form.destroy();
    });

    QUnit.test('discardchangesonrelationaldataonnewrecord',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><sheet><group>'+
                    '<fieldname="p">'+
                        '<treeeditable="top">'+
                            '<fieldname="product_id"/>'+
                        '</tree>'+
                    '</field>'+
                '</group></sheet></form>',
            intercepts:{
                history_back:function(){
                    assert.ok(true,"shouldhavesentcorrectevent");
                    //simulatetheresponsefromtheactionmanager,inthecase
                    //wherewehaveonlyoneactiveview(theform). Ifthere
                    //wasanotherview,wewouldhaveswitchedtothatview
                    //instead
                    form.update({},{reload:false});
                }
            },
        });

        //editthepfield
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

        assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'xphone',
            "inputshouldcontainxphone");

        //clickondiscardandconfirm
        awaittestUtils.form.clickDiscard(form);
        awaittestUtils.dom.click('.modal-footer.btn-primary');//clickonconfirm

        assert.notOk(form.$el.prop('outerHTML').match('xphone'),
            "thestringxphoneshouldnotbepresentafterdiscarding");
        form.destroy();
    });

    QUnit.test('discardchangesonanew(nondirty,exceptfordefaults)formview',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.fields.foo.default="ABC";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            intercepts:{
                history_back:function(){
                    assert.ok(true,"shouldhavesentcorrectevent");
                }
            }
        });

        //editthefoofield
        assert.strictEqual(form.$('input[name=foo]').val(),'ABC',
            "inputshouldcontainABC");

        awaittestUtils.form.clickDiscard(form);

        assert.containsNone(document.body,'.modal',
            "thereshouldnotbeaconfirmmodal");

        form.destroy();
    });

    QUnit.test('discardchangesonanew(dirty)formview',asyncfunction(assert){
        assert.expect(8);

        this.data.partner.fields.foo.default="ABC";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            intercepts:{
                history_back:function(){
                    assert.ok(true,"shouldhavesentcorrectevent");
                    //simulatetheresponsefromtheactionmanager,inthecase
                    //wherewehaveonlyoneactiveview(theform). Ifthere
                    //wasanotherview,wewouldhaveswitchedtothatview
                    //instead
                    form.update({},{reload:false});
                }
            },
        });

        //editthefoofield
        assert.strictEqual(form.$('input').val(),'ABC', 'inputshouldcontainABC');
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'DEF');

        //discardthechangesandcheckithasproperlybeendiscarded
        awaittestUtils.form.clickDiscard(form);
        assert.containsOnce(document.body,'.modal','thereshouldbeaconfirmmodal');
        assert.strictEqual(form.$('input').val(),'DEF','inputshouldbeDEF');
        awaittestUtils.dom.click('.modal-footer.btn-primary');//clickonconfirm
        assert.strictEqual(form.$('input').val(),'ABC','inputshouldnowbeABC');

        //redirtyanddiscardthefieldfoo(tomakesureinitialchangeshaven'tbeenlost)
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'GHI');
        awaittestUtils.form.clickDiscard(form);
        assert.strictEqual(form.$('input').val(),'GHI','inputshouldbeGHI');
        awaittestUtils.dom.click('.modal-footer.btn-primary');//clickonconfirm
        assert.strictEqual(form.$('input').val(),'ABC','inputshouldnowbeABC');

        form.destroy();
    });

    QUnit.test('discardchangesonaduplicatedrecord',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            res_id:1,
            viewOptions:{hasActionMenus:true},
        });
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');
        awaittestUtils.form.clickSave(form);

        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Duplicate");

        assert.strictEqual(form.$('input[name=foo]').val(),'tralala','inputshouldcontainABC');

        awaittestUtils.form.clickDiscard(form);

        assert.containsNone(document.body,'.modal',"thereshouldnotbeaconfirmmodal");

        form.destroy();
    });

    QUnit.test("switchingtoanotherrecordfromadirtyone",asyncfunction(assert){
        assert.expect(11);

        varnbWrite=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:1,
            mockRPC:function(route){
                if(route==='/web/dataset/call_kw/partner/write'){
                    nbWrite++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(cpHelpers.getPagerValue(form),'1',"pagervalueshouldbe1");
        assert.strictEqual(cpHelpers.getPagerSize(form),'2',"pagerlimitshouldbe2");

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=foo]').val(),'yop',"inputshouldcontainyop");

        //editthefoofield
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'newvalue');
        assert.strictEqual(form.$('input').val(),'newvalue','inputshouldcontainnewvalue');

        //clickonthepagertoswitchtothenextrecordandcanceltheconfirmrequest
        awaitcpHelpers.pagerNext(form);
        assert.containsOnce(document.body,'.modal',"aconfirmmodalshouldbedisplayed");
        awaittestUtils.dom.click('.modal-footer.btn-secondary');//clickoncancel
        assert.strictEqual(form.$('input[name=foo]').val(),'newvalue',
            "inputshouldstillcontainnewvalue");
        assert.strictEqual(cpHelpers.getPagerValue(form),'1',"pagervalueshouldstillbe1");

        //clickonthepagertoswitchtothenextrecordandconfirm
        awaitcpHelpers.pagerNext(form);
        assert.containsOnce(document.body,'.modal',"aconfirmmodalshouldbedisplayed");
        awaittestUtils.dom.click('.modal-footer.btn-primary');//clickonconfirm
        assert.strictEqual(form.$('input[name=foo]').val(),'blip',"inputshouldcontainblip");
        assert.strictEqual(cpHelpers.getPagerValue(form),'2',"pagervalueshouldbe2");

        assert.strictEqual(nbWrite,0,'nowriteRPCshouldhavebeendone');
        form.destroy();
    });

    QUnit.test('handlingdirtystate:switchingtoanotherrecord',asyncfunction(assert){
        assert.expect(12);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"></field>'+
                    '<fieldname="priority"widget="priority"></field>'+
                '</form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:1,
        });

        assert.strictEqual(cpHelpers.getPagerValue(form),'1',"pagervalueshouldbe1");

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=foo]').val(),'yop',"inputshouldcontainyop");

        //editthefoofield
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'newvalue');
        assert.strictEqual(form.$('input[name=foo]').val(),'newvalue',
            "inputshouldcontainnewvalue");

        awaittestUtils.form.clickSave(form);

        //clickonthepagertoswitchtothenextrecordandcanceltheconfirmrequest
        awaitcpHelpers.pagerNext(form);
        assert.containsNone(document.body,'.modal:visible',
            "noconfirmmodalshouldbedisplayed");
        assert.strictEqual(cpHelpers.getPagerValue(form),'2',"pagervalueshouldbe2");

        assert.containsN(form,'.o_priority.fa-star-o',2,
            'prioritywidgetshouldhavebeenrenderedwithcorrectvalue');

        //editthevalueinreadonly
        awaittestUtils.dom.click(form.$('.o_priority.fa-star-o:first'));//clickonthefirststar
        assert.containsOnce(form,'.o_priority.fa-star',
            'prioritywidgetshouldhavebeenupdated');

        awaitcpHelpers.pagerNext(form);
            assert.containsNone(document.body,'.modal:visible',
            "noconfirmmodalshouldbedisplayed");
        assert.strictEqual(cpHelpers.getPagerValue(form),'1',"pagervalueshouldbe1");

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=foo]').val(),'newvalue',
            "inputshouldcontainyop");

        //editthefoofield
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'wrongvalue');

        awaittestUtils.form.clickDiscard(form);
        assert.containsOnce(document.body,'.modal',"aconfirmmodalshouldbedisplayed");
        awaittestUtils.dom.click('.modal-footer.btn-primary');//clickonconfirm
        awaitcpHelpers.pagerNext(form);
        assert.strictEqual(cpHelpers.getPagerValue(form),'2',"pagervalueshouldbe2");
        form.destroy();
    });

    QUnit.test('restorelocalstatewhenswitchingtoanotherrecord',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<notebook>'+
                            '<pagestring="FirstPage"name="first">'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                            '<pagestring="Secondpage"name="second">'+
                                '<fieldname="bar"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:1,
        });

        //clickonsecondpagetab
        awaittestUtils.dom.click(form.$('.o_notebook.nav-link:eq(1)'));

        assert.doesNotHaveClass(form.$('.o_notebook.nav-link:eq(0)'),'active');
        assert.hasClass(form.$('.o_notebook.nav-link:eq(1)'),'active');

        //clickonthepagertoswitchtothenextrecord
        awaitcpHelpers.pagerNext(form);

        assert.doesNotHaveClass(form.$('.o_notebook.nav-link:eq(0)'),'active');
        assert.hasClass(form.$('.o_notebook.nav-link:eq(1)'),'active');
        form.destroy();
    });

    QUnit.test('pagerishiddenincreatemode',asyncfunction(assert){
        assert.expect(7);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                ids:[1,2],
                index:0,
            },
        });

        assert.containsOnce(form,'.o_pager');
        assert.strictEqual(cpHelpers.getPagerValue(form),"1",
            "currentpagervalueshouldbe1");
        assert.strictEqual(cpHelpers.getPagerSize(form),"2",
            "currentpagerlimitshouldbe1");

        awaittestUtils.form.clickCreate(form);

        assert.containsNone(form,'.o_pager');

        awaittestUtils.form.clickSave(form);

        assert.containsOnce(form,'.o_pager');
        assert.strictEqual(cpHelpers.getPagerValue(form),"3",
            "currentpagervalueshouldbe3");
        assert.strictEqual(cpHelpers.getPagerSize(form),"3",
            "currentpagerlimitshouldbe3");

        form.destroy();
    });

    QUnit.test('switchingtoanotherrecord,inreadonlymode',asyncfunction(assert){
        assert.expect(5);

        varpushStateCount=0;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:1,
            intercepts:{
                push_state:function(event){
                    pushStateCount++;
                }
            }
        });

        assert.strictEqual(form.mode,'readonly','formviewshouldbeinreadonlymode');
        assert.strictEqual(cpHelpers.getPagerValue(form),"1",'pagervalueshouldbe1');

        awaitcpHelpers.pagerNext(form);

        assert.strictEqual(cpHelpers.getPagerValue(form),"2",'pagervalueshouldbe2');
        assert.strictEqual(form.mode,'readonly','formviewshouldbeinreadonlymode');

        assert.strictEqual(pushStateCount,2,"shouldhavetriggered2push_state");
        form.destroy();
    });

    QUnit.test('modifiersarereevaluatedwhencreatingnewrecord',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<fieldname="foo"class="foo_field"attrs=\'{"invisible":[["bar","=",True]]}\'/>'+
                        '<fieldname="bar"/>'+
                    '</group></sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'span.foo_field');
        assert.isNotVisible(form.$('span.foo_field'));

        awaittestUtils.form.clickCreate(form);

        assert.containsOnce(form,'input.foo_field');
        assert.isVisible(form.$('input.foo_field'));

        form.destroy();
    });

    QUnit.test('emptyreadonlyfieldsarevisibleonnewrecords',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.foo.readonly=true;
        this.data.partner.fields.foo.default=undefined;
        this.data.partner.records[0].foo=undefined;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<fieldname="foo"/>'+
                    '</group></sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_field_empty');

        awaittestUtils.form.clickCreate(form);

        assert.containsNone(form,'.o_field_empty');
        form.destroy();
    });

    QUnit.test('allgroupchildrenhavecorrectlayoutclassname',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<groupclass="inner_group">'+
                            '<fieldname="name"/>'+
                        '</group>'+
                        '<divclass="inner_div">'+
                            '<fieldname="foo"/>'+
                        '</div>'+
                    '</group></sheet>'+
                '</form>',
            res_id:1,
        });

        assert.hasClass(form.$('.inner_group'),'o_group_col_6'),
        assert.hasClass(form.$('.inner_div'),'o_group_col_6'),
        form.destroy();
    });

    QUnit.test('deletingarecord',asyncfunction(assert){
        assert.expect(8);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            viewOptions:{
                ids:[1,2,4],
                index:0,
                hasActionMenus:true,
            },
            res_id:1,
        });

        assert.strictEqual(cpHelpers.getPagerValue(form),"1",'pagervalueshouldbe1');
        assert.strictEqual(cpHelpers.getPagerSize(form),"3",'pagerlimitshouldbe3');
        assert.strictEqual(form.$('span:contains(yop)').length,1,
            'shouldhaveafieldwithfoovalueforrecord1');
        assert.ok(!$('.modal:visible').length,'noconfirmmodalshouldbedisplayed');

        //openactionmenuanddelete
        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Delete");

        assert.ok($('.modal').length,'aconfirmmodalshouldbedisplayed');

        //confirmthedelete
        awaittestUtils.dom.click($('.modal-footerbutton.btn-primary'));

        assert.strictEqual(cpHelpers.getPagerValue(form),"1",'pagervalueshouldbe1');
        assert.strictEqual(cpHelpers.getPagerSize(form),"2",'pagerlimitshouldbe2');
        assert.strictEqual(form.$('span:contains(blip)').length,1,
            'shouldhaveafieldwithfoovalueforrecord2');
        form.destroy();
    });

    QUnit.test('deletingthelastrecord',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="foo"></field></form>',
            viewOptions:{
                ids:[1],
                index:0,
                hasActionMenus:true,
            },
            res_id:1,
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            }
        });

        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Delete");

        awaittestUtils.mock.intercept(form,'history_back',function(){
            assert.step('history_back');
        });
        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footerbutton.btn-primary'));
        assert.strictEqual($('.modal').length,0,'noconfirmmodalshouldbedisplayed');

        assert.verifySteps(['read','unlink','history_back']);
        form.destroy();
    });

    QUnit.test('emptyrequiredfieldscannotbesaved',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.foo.required=true;
        deletethis.data.partner.fields.foo.default;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<group><fieldname="foo"/></group>'+
                '</form>',
            services:{
                notification:NotificationService.extend({
                    notify:function(params){
                        if(params.type!=='danger'){
                            return;
                        }
                        assert.strictEqual(params.title,'Invalidfields:',
                            "shouldhaveawarningwithcorrecttitle");
                        assert.strictEqual(params.message,'<ul><li>Foo</li></ul>',
                            "shouldhaveawarningwithcorrectmessage");
                    }
                }),
            },
        });

        awaittestUtils.form.clickSave(form);
        assert.hasClass(form.$('label.o_form_label'),'o_field_invalid');
        assert.hasClass(form.$('input[name=foo]'),'o_field_invalid');

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        assert.containsNone(form,'.o_field_invalid');

        form.destroy();
    });

    QUnit.test('changesinareadonlyformviewaresaveddirectly',asyncfunction(assert){
        assert.expect(10);

        varnbWrite=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="priority"widget="priority"/>'+
                        '</group>'+
                '</form>',
            mockRPC:function(route){
                if(route==='/web/dataset/call_kw/partner/write'){
                    nbWrite++;
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
        });

        assert.containsN(form,'.o_priority.o_priority_star',2,
            'prioritywidgetshouldhavebeenrendered');
        assert.containsN(form,'.o_priority.fa-star-o',2,
            'prioritywidgetshouldhavebeenrenderedwithcorrectvalue');

        //editthevalueinreadonly
        awaittestUtils.dom.click(form.$('.o_priority.fa-star-o:first'));
        assert.strictEqual(nbWrite,1,'shouldhavesaveddirectly');
        assert.containsOnce(form,'.o_priority.fa-star',
            'prioritywidgetshouldhavebeenupdated');

        //switchtoeditmodeandeditthevalueagain
        awaittestUtils.form.clickEdit(form);
        assert.containsN(form,'.o_priority.o_priority_star',2,
            'prioritywidgetshouldhavebeencorrectlyrendered');
        assert.containsOnce(form,'.o_priority.fa-star',
            'prioritywidgetshouldhavecorrectvalue');
        awaittestUtils.dom.click(form.$('.o_priority.fa-star-o:first'));
        assert.strictEqual(nbWrite,1,'shouldnothavesaveddirectly');
        assert.containsN(form,'.o_priority.fa-star',2,
            'prioritywidgetshouldhavebeenupdated');

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(nbWrite,2,'shouldnothavesaveddirectly');
        assert.containsN(form,'.o_priority.fa-star',2,
            'prioritywidgetshouldhavecorrectvalue');
        form.destroy();
    });

    QUnit.test('displayadialogifonchangeresultisawarning',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.onchanges={foo:true};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{int_field:10},
                        warning:{
                            title:"Warning",
                            message:"Youmustfirstselectapartner",
                            type:'dialog',
                        }
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                warning:function(event){
                    assert.strictEqual(event.data.type,'dialog',
                        "shouldhavetriggeredaneventwiththecorrectdata");
                    assert.strictEqual(event.data.title,"Warning",
                        "shouldhavetriggeredaneventwiththecorrectdata");
                    assert.strictEqual(event.data.message,"Youmustfirstselectapartner",
                        "shouldhavetriggeredaneventwiththecorrectdata");
                },
            },
        });

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('input[name=int_field]').val(),'9');

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        assert.strictEqual(form.$('input[name=int_field]').val(),'10');

        form.destroy();
    });

    QUnit.test('displayanotificatonifonchangeresultisawarningwithtypenotification',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.onchanges={foo:true};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{int_field:10},
                        warning:{
                            title:"Warning",
                            message:"Youmustfirstselectapartner",
                            type:'notification',
                        }
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                warning:function(event){
                    assert.strictEqual(event.data.type,'notification',
                        "shouldhavetriggeredaneventwiththecorrectdata");
                    assert.strictEqual(event.data.title,"Warning",
                        "shouldhavetriggeredaneventwiththecorrectdata");
                    assert.strictEqual(event.data.message,"Youmustfirstselectapartner",
                        "shouldhavetriggeredaneventwiththecorrectdata");
                },
            },
        });

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('input[name=int_field]').val(),'9');

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        assert.strictEqual(form.$('input[name=int_field]').val(),'10');

        form.destroy();
    });

    QUnit.test('cancreaterecordevenifonchangereturnsawarning',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.onchanges={foo:true};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{int_field:10},
                        warning:{
                            title:"Warning",
                            message:"Youmustfirstselectapartner"
                        }
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                warning:function(event){
                    assert.ok(true,'shouldtriggerawarning');
                },
            },
        });
        assert.strictEqual(form.$('input[name="int_field"]').val(),"10",
            "recordshouldhavebeencreatedandrendered");

        form.destroy();
    });

    QUnit.test('donothingifaddalineinone2manyresultinaonchangewithawarning',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.onchanges={foo:true};

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
                        value:{},
                        warning:{
                            title:"Warning",
                            message:"Youmustfirstselectapartner",
                        }
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                warning:function(){
                    assert.step("shouldhavetriggeredawarning");
                },
            },
        });

        //gotoeditmode,clicktoaddarecordintheo2m
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.containsNone(form,'tr.o_data_row',
            "shouldnothaveaddedaline");
        assert.verifySteps(["shouldhavetriggeredawarning"]);
        form.destroy();
    });

    QUnit.test('buttonboxisrenderedincreatemode',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<divname="button_box"class="oe_button_box">'+
                        '<buttontype="object"class="oe_stat_button"icon="fa-check-square">'+
                            '<fieldname="bar"/>'+
                        '</button>'+
                    '</div>'+
                '</form>',
            res_id:2,
        });

        //readonlymode
        assert.containsOnce(form,'.oe_stat_button',
            "buttonboxshouldbedisplayedinreadonly");

        //editmode
        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'.oe_stat_button',
            "buttonboxshouldbedisplayedineditonanexistingrecord");

        //createmode(leaveeditionfirst!)
        awaittestUtils.form.clickDiscard(form);
        awaittestUtils.form.clickCreate(form);
        assert.containsOnce(form,'.oe_stat_button',
            "buttonboxshouldbedisplayedwhencreatinganewrecordaswell");

        form.destroy();
    });

    QUnit.test('properlyapplyonchangeonone2manyfields',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records[0].p=[4];
        this.data.partner.onchanges={
            foo:function(obj){
                obj.p=[
                    [5],
                    [1,4,{display_name:"updatedrecord"}],
                    [0,null,{display_name:"createdrecord"}],
                ];
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/></group>'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_field_one2many.o_data_row',
            "thereshouldbeoneone2manyrecordlinkedatfirst");
        assert.strictEqual(form.$('.o_field_one2many.o_data_rowtd:first').text(),'aaa',
            "the'display_name'oftheone2manyrecordshouldbecorrect");

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'letustriggeranonchange');
        var$o2m=form.$('.o_field_one2many');
        assert.strictEqual($o2m.find('.o_data_row').length,2,
            "thereshouldbetwolinkedrecord");
        assert.strictEqual($o2m.find('.o_data_row:firsttd:first').text(),'updatedrecord',
            "the'display_name'ofthefirstone2manyrecordshouldhavebeenupdated");
        assert.strictEqual($o2m.find('.o_data_row:nth(1)td:first').text(),'createdrecord',
            "the'display_name'ofthesecondone2manyrecordshouldbecorrect");

        form.destroy();
    });

    QUnit.test('properlyapplyonchangeonone2manyfieldsdirectclick',asyncfunction(assert){
        assert.expect(3);

        vardef=testUtils.makeTestPromise();

        this.data.partner.records[0].p=[2,4];
        this.data.partner.onchanges={
            int_field:function(obj){
                obj.p=[
                    [5],
                    [1,2,{display_name:"updatedrecord1",int_field:obj.int_field}],
                    [1,4,{display_name:"updatedrecord2",int_field:obj.int_field*2}],
                ];
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                    '</group>'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="int_field"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    varself=this;
                    varmy_args=arguments;
                    varmy_super=this._super;
                    returndef.then(()=>{
                        returnmy_super.apply(self,my_args)
                    });
                }
                returnthis._super.apply(this,arguments);
            },
            archs:{
                'partner,false,form':'<form><group><fieldname="display_name"/><fieldname="int_field"/></group></form>'
            },
            viewOptions:{
                mode:'edit',
            },
        });
        //Triggertheonchange
        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),'2');

        //Openfirstrecordinone2many
        awaittestUtils.dom.click(form.$('.o_data_row:first'));

        assert.containsNone(document.body,'.modal');

        def.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(document.body,'.modal');
        assert.strictEqual($('.modal').find('input[name=int_field]').val(),'2');

        form.destroy();
    });

    QUnit.test('updatemany2manyvalueinone2manyafteronchange',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[1].p=[4];
        this.data.partner.onchanges={
            foo:function(obj){
                obj.p=[
                    [5],
                    [1,4,{
                        display_name:"gold",
                        timmy:[[5]],
                    }],
                ];
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p">'+
                        '<treeeditable="top">'+
                            '<fieldname="display_name"attrs="{\'readonly\':[(\'timmy\',\'=\',false)]}"/>'+
                            '<fieldname="timmy"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:2,
        });
        assert.strictEqual($('div[name="p"].o_data_rowtd').text().trim(),"aaaNorecords",
            "shouldhaveproperinitialcontent");
        awaittestUtils.form.clickEdit(form);

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'tralala');

        assert.strictEqual($('div[name="p"].o_data_rowtd').text().trim(),"goldNorecords",
            "shouldhaveproperinitialcontent");
        form.destroy();
    });

    QUnit.test('deletealineinaone2manywhileeditinganotherlinetriggersawarning',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].p=[1,2];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="p">'+
                        '<treeeditable="bottom">'+
                            '<fieldname="display_name"required="True"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_data_cell').first());
        awaittestUtils.fields.editInput(form.$('input[name=display_name]'),'');
        awaittestUtils.dom.click(form.$('.fa-trash-o').eq(1));

        assert.strictEqual($('.modal').find('.modal-title').first().text(),"Warning",
            "Clickingoutofadirtylinewhileeditingshouldtriggerawarningmodal.");

        awaittestUtils.dom.click($('.modal').find('.btn-primary'));
        //useofowlCompatibilityNextTickbecausetherearetwosequentialupdatesofthe
        //controlpanel(whichiswritteninowl):eachofthemwaitsforthenextanimationframe
        //tocomplete
        awaittestUtils.owlCompatibilityNextTick();
        assert.strictEqual(form.$('.o_data_cell').first().text(),"firstrecord",
            "Valueshouldhavebeenresettowhatitwasbeforeeditingbegan.");
        assert.containsOnce(form,'.o_data_row',
            "Theotherlineshouldhavebeendeleted.");
        form.destroy();
    });

    QUnit.test('properlyapplyonchangeonmany2manyfields',asyncfunction(assert){
        assert.expect(14);

        this.data.partner.onchanges={
            foo:function(obj){
                obj.timmy=[
                    [5],
                    [4,12],
                    [4,14],
                ];
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/></group>'+
                    '<fieldname="timmy">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                if(args.method==='read'&&args.model==='partner_type'){
                    assert.deepEqual(args.args[0],[12,14],
                        "shouldreadbothm2mwithoneRPC");
                }
                if(args.method==='write'){
                    assert.deepEqual(args.args[1].timmy,[[6,false,[12,14]]],
                        "shouldcorrectlysavethechangedm2mvalues");

                }
                returnthis._super.apply(this,arguments);
            },
            res_id:2,
        });

        assert.containsNone(form,'.o_field_many2many.o_data_row',
            "thereshouldbenomany2manyrecordlinkedatfirst");

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'letustriggeranonchange');
        var$m2m=form.$('.o_field_many2many');
        assert.strictEqual($m2m.find('.o_data_row').length,2,
            "thereshouldbetwolinkedrecords");
        assert.strictEqual($m2m.find('.o_data_row:firsttd:first').text(),'gold',
            "the'display_name'ofthefirstm2mrecordshouldbecorrectlydisplayed");
        assert.strictEqual($m2m.find('.o_data_row:nth(1)td:first').text(),'silver',
            "the'display_name'ofthesecondm2mrecordshouldbecorrectlydisplayed");

        awaittestUtils.form.clickSave(form);

        assert.verifySteps(['read','onchange','read','write','read','read']);

        form.destroy();
    });

    QUnit.test('display_namenotsentforonchangesifnotinview',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].timmy=[12];
        this.data.partner.onchanges={
            foo:function(){},
        };
        this.data.partner_type.onchanges={
            name:function(){},
        };
        varreadInModal=false;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="timmy">'+
                            '<tree>'+
                                '<fieldname="name"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="name"/>'+
                                '<fieldname="color"/>'+
                            '</form>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='read'&&args.model==='partner'){
                    assert.deepEqual(args.args[1],['foo','timmy','display_name'],
                        "shouldreaddisplay_nameevenifnotintheview");
                }
                if(args.method==='read'&&args.model==='partner_type'){
                    if(!readInModal){
                        assert.deepEqual(args.args[1],['name'],
                            "shouldnotreaddisplay_nameforrecordsinthelist");
                    }else{
                        assert.deepEqual(args.args[1],['name','color','display_name'],
                            "shouldreaddisplay_namewhenopeningthesubrecord");
                    }
                }
                if(args.method==='onchange'&&args.model==='partner'){
                    assert.deepEqual(args.args[1],{
                        id:1,
                        foo:'coucou',
                        timmy:[[6,false,[12]]],
                    },"shouldonlysendthevalueoffieldsintheview(+id)");
                    assert.deepEqual(args.args[3],{
                        foo:'1',
                        timmy:'',
                        'timmy.name':'1',
                        'timmy.color':'',
                    },"onlythefieldsintheviewshouldbeintheonchangespec");
                }
                if(args.method==='onchange'&&args.model==='partner_type'){
                    assert.deepEqual(args.args[1],{
                        id:12,
                        name:'newname',
                        color:2,
                    },"shouldonlysendthevalueoffieldsintheview(+id)");
                    assert.deepEqual(args.args[3],{
                        name:'1',
                        color:'',
                    },"onlythefieldsintheviewshouldbeintheonchangespec");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        //triggertheonchange
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),"coucou");

        //openasubrecordandtriggeranonchange
        readInModal=true;
        awaittestUtils.dom.click(form.$('.o_data_row.o_data_cell:first'));
        awaittestUtils.fields.editInput($('.modal.o_field_widget[name=name]'),"newname");

        form.destroy();
    });

    QUnit.test('onchangesondate(time)fields',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.onchanges={
            foo:function(obj){
                obj.date='2021-12-12';
                obj.datetime='2021-12-1210:55:05';
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="date"/>'+
                        '<fieldname="datetime"/>'+
                    '</group>'+
                '</form>',
            res_id:1,
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name=date]').text(),
            '01/25/2017',"theinitialdateshouldbecorrect");
        assert.strictEqual(form.$('.o_field_widget[name=datetime]').text(),
            '12/12/201612:55:05',"theinitialdatetimeshouldbecorrect");

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_field_widget[name=date]input').val(),
            '01/25/2017',"theinitialdateshouldbecorrectinedit");
        assert.strictEqual(form.$('.o_field_widget[name=datetime]input').val(),
            '12/12/201612:55:05',"theinitialdatetimeshouldbecorrectinedit");

        //triggertheonchange
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name="foo"]'),"coucou");

        assert.strictEqual(form.$('.o_field_widget[name=date]input').val(),
            '12/12/2021',"theinitialdateshouldbecorrectinedit");
        assert.strictEqual(form.$('.o_field_widget[name=datetime]input').val(),
            '12/12/202112:55:05',"theinitialdatetimeshouldbecorrectinedit");

        form.destroy();
    });

    QUnit.test('onchangesarenotsentforeachkeystrokes',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(5);

        varonchangeNbr=0;

        this.data.partner.onchanges={
            foo:function(obj){
                obj.int_field=obj.foo.length+1000;
            },
        };
        vardef=testUtils.makeTestPromise();
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
            fieldDebounce:3,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    onchangeNbr++;
                    returnconcurrency.delay(3).then(function(){
                        def.resolve();
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        awaittestUtils.form.clickEdit(form);

        testUtils.fields.editInput(form.$('input[name=foo]'),'1');
        assert.strictEqual(onchangeNbr,0,"noonchangehasbeencalledyet");
        testUtils.fields.editInput(form.$('input[name=foo]'),'12');
        assert.strictEqual(onchangeNbr,0,"noonchangehasbeencalledyet");

        returnwaitForFinishedOnChange().then(asyncfunction(){
            assert.strictEqual(onchangeNbr,1,"oneonchangehasbeencalled");

            //addsomethingintheinput,thenfocusanotherinput
            awaittestUtils.fields.editAndTrigger(form.$('input[name=foo]'),'123',['change']);
            assert.strictEqual(onchangeNbr,2,"oneonchangehasbeencalledimmediately");

            returnwaitForFinishedOnChange();
        }).then(function(){
            assert.strictEqual(onchangeNbr,2,"noextraonchangeshouldhavebeencalled");

            form.destroy();
            done();
        });

        functionwaitForFinishedOnChange(){
            returndef.then(function(){
                def=testUtils.makeTestPromise();
                returnconcurrency.delay(0);
            });
        }
    });

    QUnit.test('onchangesarenotsentforinvalidvalues',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.onchanges={
            int_field:function(obj){
                obj.foo=String(obj.int_field);
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);

        //editint_field,andcheckthatanonchangehasbeenapplied
        awaittestUtils.fields.editInput(form.$('input[name="int_field"]'),"123");
        assert.strictEqual(form.$('input[name="foo"]').val(),"123",
            "theonchangehasbeenapplied");

        //enteraninvalidvalueinafloat,andcheckthatnoonchangehas
        //beenapplied
        awaittestUtils.fields.editInput(form.$('input[name="int_field"]'),"123a");
        assert.strictEqual(form.$('input[name="foo"]').val(),"123",
            "theonchangehasnotbeenapplied");

        //save,andcheckthattheint_fieldinputismarkedasinvalid
        awaittestUtils.form.clickSave(form);
        assert.hasClass(form.$('input[name="int_field"]'),'o_field_invalid',
            "inputint_fieldismarkedasinvalid");

        assert.verifySteps(['read','onchange']);
        form.destroy();
    });

    QUnit.test('rpccompleteafterdestroyingparent',asyncfunction(assert){
        //Wejusttestthatthereisnocrashinthissituation
        assert.expect(0);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<buttonname="update_module"type="object"class="o_form_button_update"/>'+
                '</form>',
            res_id:2,
            intercepts:{
                execute_action:function(event){
                    form.destroy();
                    event.data.on_success();
                }
            }
        });
        awaittestUtils.dom.click(form.$('.o_form_button_update'));
    });

    QUnit.test('onchangesthatcompleteafterdiscarding',asyncfunction(assert){
        assert.expect(5);

        vardef1=testUtils.makeTestPromise();

        this.data.partner.onchanges={
            foo:function(obj){
                obj.int_field=obj.foo.length+1000;
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group><fieldname="foo"/><fieldname="int_field"/></group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    assert.step('onchangeisdone');
                    returndef1.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        //gointoeditmode
        assert.strictEqual(form.$('span[name="foo"]').text(),"blip",
            "fieldfooshouldbedisplayedtoinitialvalue");
        awaittestUtils.form.clickEdit(form);

        //editavalue
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'1234');

        //discardchanges
        awaittestUtils.form.clickDiscard(form);
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));
        assert.strictEqual(form.$('span[name="foo"]').text(),"blip",
            "fieldfooshouldstillbedisplayedtoinitialvalue");

        //completetheonchange
        def1.resolve();
        awaittestUtils.nextTick();
        assert.strictEqual(form.$('span[name="foo"]').text(),"blip",
            "fieldfooshouldstillbedisplayedtoinitialvalue");
        assert.verifySteps(['onchangeisdone']);

        form.destroy();
    });

    QUnit.test('discardingbeforesavereturns',asyncfunction(assert){
        assert.expect(4);

        vardef=testUtils.makeTestPromise();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group><fieldname="foo"/></group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='write'){
                    returndef.then(_.constant(result));
                }
                returnresult;
            },
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'1234');

        //savethevalueanddiscarddirectly
        awaittestUtils.form.clickSave(form);
        form.discardChanges();//Simulateclickonbreadcrumb

        assert.strictEqual(form.$('.o_field_widget[name="foo"]').val(),"1234",
            "fieldfooshouldstillcontainnewvalue");
        assert.strictEqual($('.modal').length,0,
            "Confirmdialogshouldnotbedisplayed");

        //completethewrite
        def.resolve();
        awaittestUtils.nextTick();
        assert.strictEqual($('.modal').length,0,
            "Confirmdialogshouldnotbedisplayed");
        assert.strictEqual(form.$('.o_field_widget[name="foo"]').text(),"1234",
            "valueshouldhavebeensavedandrerenderedinreadonly");

        form.destroy();
    });

    QUnit.test('unchangedrelationaldataissentforonchanges',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[1].p=[4];
        this.data.partner.onchanges={
            foo:function(obj){
                obj.int_field=obj.foo.length+1000;
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="bar"/>'+
                            '</tree>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.deepEqual(args.args[1].p,[[4,4,false]],
                        "shouldsendacommandforfieldpevenifithasn'tchanged");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'triggeranonchange');

        form.destroy();
    });

    QUnit.test('onchangesonunknownfieldsofo2mareignored',asyncfunction(assert){
        //many2onefieldsneedtobepostprocessed(theonchangereturns[id,
        //display_name]),butifwedon'tknowthefield,wecan'tknowit'sa
        //many2one,soitisn'tignored,itsvalueisanarrayinsteadofa
        //dataPointid,whichmaycauseerrorslater(e.g.whensaving).
        assert.expect(2);

        this.data.partner.records[1].p=[4];
        this.data.partner.onchanges={
            foo:function(){},
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="bar"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="product_id"/>'+
                            '</form>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{
                            p:[
                                [5],
                                [1,4,{
                                    foo:'foochanged',
                                    product_id:[37,"xphone"],
                                }]
                            ],
                        },
                    });
                }
                if(args.method==='write'){
                    assert.deepEqual(args.args[1].p,[[1,4,{
                        foo:'foochanged',
                    }]],"shouldonlywritevalueofknownfields");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'triggeranonchange');
        awaittestUtils.owlCompatibilityNextTick();

        assert.strictEqual(form.$('.o_data_rowtd:first').text(),'foochanged',
            "onchangeshouldhavebeencorrectlyappliedonfieldino2mlist");

        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('onchangevaluearenotdiscardedono2medition',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[1].p=[4];
        this.data.partner.onchanges={
            foo:function(){},
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="bar"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="product_id"/>'+
                            '</form>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{
                            p:[[5],[1,4,{foo:'foochanged'}]],
                        },
                    });
                }
                if(args.method==='write'){
                    assert.deepEqual(args.args[1].p,[[1,4,{
                        foo:'foochanged',
                    }]],"shouldonlywritevalueofknownfields");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_data_rowtd:first').text(),'MylittleFooValue',
            "theinitialvalueshouldbethedefaultone");

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'triggeranonchange');
        awaittestUtils.owlCompatibilityNextTick();

        assert.strictEqual(form.$('.o_data_rowtd:first').text(),'foochanged',
            "onchangeshouldhavebeencorrectlyappliedonfieldino2mlist");

        awaittestUtils.dom.click(form.$('.o_data_row'));
        assert.strictEqual($('.modal.modal-title').text().trim(),'Open:one2manyfield',
            "thefieldstringisdisplayedinthemodaltitle");
        assert.strictEqual($('.modal.o_field_widget').val(),'foochanged',
            "theonchangevaluehasn'tbeendiscardedwhenopeningtheo2m");

        form.destroy();
    });

    QUnit.test('argsofonchangesino2mfieldsarecorrect(inlineedition)',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[1].p=[4];
        this.data.partner.fields.p.relation_field='rel_field';
        this.data.partner.fields.int_field.default=14;
        this.data.partner.onchanges={
            int_field:function(obj){
                obj.foo='['+obj.rel_field.foo+']'+obj.int_field;
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="p">'+
                            '<treeeditable="top">'+
                                '<fieldname="foo"/>'+
                                '<fieldname="int_field"/>'+
                            '</tree>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            res_id:2,
        });

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_data_rowtd:first').text(),'MylittleFooValue',
            "theinitialvalueshouldbethedefaultone");

        awaittestUtils.dom.click(form.$('.o_data_rowtd:nth(1)'));
        awaittestUtils.fields.editInput(form.$('.o_data_rowinput:nth(1)'),77);

        assert.strictEqual(form.$('.o_data_rowinput:first').val(),'[blip]77',
            "onchangeshouldhavebeencorrectlyapplied");

        //createanewo2mrecord
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.strictEqual(form.$('.o_data_rowinput:first').val(),'[blip]14',
            "onchangeshouldhavebeencorrectlyappliedafterdefaultget");

        form.destroy();
    });

    QUnit.test('argsofonchangesino2mfieldsarecorrect(dialogedition)',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records[1].p=[4];
        this.data.partner.fields.p.relation_field='rel_field';
        this.data.partner.fields.int_field.default=14;
        this.data.partner.onchanges={
            int_field:function(obj){
                obj.foo='['+obj.rel_field.foo+']'+obj.int_field;
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="p"string="customlabel">'+
                            '<tree>'+
                                '<fieldname="foo"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="foo"/>'+
                                '<fieldname="int_field"/>'+
                            '</form>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            res_id:2,
        });

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_data_rowtd:first').text(),'MylittleFooValue',
            "theinitialvalueshouldbethedefaultone");

        awaittestUtils.dom.click(form.$('.o_data_rowtd:first'));
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput($('.modalinput:nth(1)'),77);
        assert.strictEqual($('.modalinput:first').val(),'[blip]77',
            "onchangeshouldhavebeencorrectlyapplied");
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));
        assert.strictEqual(form.$('.o_data_rowtd:first').text(),'[blip]77',
            "onchangeshouldhavebeencorrectlyapplied");

        //createanewo2mrecord
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.strictEqual($('.modal.modal-title').text().trim(),'Createcustomlabel',
            "thecustomfieldlabelisappliedinthemodaltitle");
        assert.strictEqual($('.modalinput:first').val(),'[blip]14',
            "onchangeshouldhavebeencorrectlyappliedafterdefaultget");
        awaittestUtils.dom.clickFirst($('.modal-footer.btn-primary'));
        awaittestUtils.nextTick();
        assert.strictEqual(form.$('.o_data_row:nth(1)td:first').text(),'[blip]14',
            "onchangeshouldhavebeencorrectlyappliedafterdefaultget");

        form.destroy();
    });

    QUnit.test('contextofonchangescontainsthecontextofchangedfields',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.onchanges={
            foo:function(){},
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="foo"context="{\'test\':1}"/>'+
                        '<fieldname="int_field"context="{\'int_ctx\':1}"/>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.strictEqual(args.kwargs.context.test,1,
                        "thecontextofthefieldtriggeringtheonchangeshouldbegiven");
                    assert.strictEqual(args.kwargs.context.int_ctx,undefined,
                        "thecontextofotherfieldsshouldnotbegiven");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:2,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'coucou');

        form.destroy();
    });

    QUnit.test('navigationwithtabkeyinformview',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="email"/>'+
                            '<fieldname="bar"/>'+
                            '<fieldname="display_name"widget="url"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        //gotoeditmode
        awaittestUtils.form.clickEdit(form);

        //focusfirstinput,triggertab
        form.$('input[name="foo"]').focus();

        consttabKey={keyCode:$.ui.keyCode.TAB,which:$.ui.keyCode.TAB};
        awaittestUtils.dom.triggerEvent(form.$('input[name="foo"]'),'keydown',tabKey);
        assert.ok($.contains(form.$('div[name="bar"]')[0],document.activeElement),
            "barcheckboxshouldbefocused");

        awaittestUtils.dom.triggerEvent(document.activeElement,'keydown',tabKey);
        assert.strictEqual(form.$('input[name="display_name"]')[0],document.activeElement,
            "display_nameshouldbefocused");

        //simulateshift+tabonactiveelement
        constshiftTabKey=Object.assign({},tabKey,{shiftKey:true});
        awaittestUtils.dom.triggerEvent(document.activeElement,'keydown',shiftTabKey);
        awaittestUtils.dom.triggerEvent(document.activeElement,'keydown',shiftTabKey);
        assert.strictEqual(document.activeElement,form.$('input[name="foo"]')[0],
            "firstinputshouldbefocused");

        form.destroy();
    });

    QUnit.test('navigationwithtabkeyinreadonlyformview',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[1].product_id=37;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="trululu"/>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="product_id"/>'+
                            '<fieldname="foo"widget="phone"/>'+
                            '<fieldname="display_name"widget="url"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        //focusfirstfield,triggertab
        form.$('[name="trululu"]').focus();
        form.$('[name="trululu"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        form.$('[name="foo"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$('[name="product_id"]')[0],document.activeElement,
            "product_idshouldbefocused");
        form.$('[name="product_id"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        form.$('[name="foo"]:eq(1)').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$('[name="display_name"]')[0],document.activeElement,
            "display_nameshouldbefocused");

        //simulateshift+tabonactiveelement
        $(document.activeElement).trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        $(document.activeElement).trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        $(document.activeElement).trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        $(document.activeElement).trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        assert.strictEqual(document.activeElement,form.$('[name="trululu"]')[0],
            "firstmany2oneshouldbefocused");

        form.destroy();
    });

    QUnit.test('skipinvisiblefieldswhennavigatingwithTAB',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].bar=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="bar"invisible="1"/>'+
                        '<fieldname="product_id"attrs=\'{"invisible":[["bar","=",true]]}\'/>'+
                        '<fieldname="int_field"/>'+
                    '</group></sheet>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        form.$('input[name="foo"]').focus();
        form.$('input[name="foo"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$('input[name="int_field"]')[0],document.activeElement,
            "int_fieldshouldbefocused");

        form.destroy();
    });

    QUnit.test('navigationwithtabkeyselectsavalueinformview',asyncfunction(assert){
        assert.expect(5);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="display_name"/>
                    <fieldname="int_field"/>
                    <fieldname="qux"/>
                    <fieldname="trululu"/>
                    <fieldname="date"/>
                    <fieldname="datetime"/>
                </form>`,
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.dom.click(form.el.querySelector('input[name="display_name"]'));
        awaittestUtils.fields.triggerKeydown(document.activeElement,'tab');
        assert.strictEqual(document.getSelection().toString(),"10",
            "int_fieldvalueshouldbeselected");

        awaittestUtils.fields.triggerKeydown(document.activeElement,'tab');
        assert.strictEqual(document.getSelection().toString(),"0.4",
            "quxfieldvalueshouldbeselected");

        awaittestUtils.fields.triggerKeydown(document.activeElement,'tab');
        assert.strictEqual(document.getSelection().toString(),"aaa",
            "trululufieldvalueshouldbeselected");

        awaittestUtils.fields.triggerKeydown(document.activeElement,'tab');
        assert.strictEqual(document.getSelection().toString(),"01/25/2017",
            "datefieldvalueshouldbeselected");

        awaittestUtils.fields.triggerKeydown(document.activeElement,'tab');
        assert.strictEqual(document.getSelection().toString(),"12/12/201610:55:05",
            "datetimefieldvalueshouldbeselected");

        form.destroy();
    });

    QUnit.test('clickingonastatbuttonwithacontext',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<buttonclass="oe_stat_button"type="action"name="1"context="{\'test\':active_id}">'+
                                '<fieldname="qux"widget="statinfo"/>'+
                            '</button>'+
                        '</div>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            viewOptions:{
                context:{some_context:true},
            },
            intercepts:{
                execute_action:function(e){
                    assert.deepEqual(e.data.action_data.context,{
                        'test':2
                    },"buttoncontextshouldhavebeenevaluatedandgiventotheaction,withmagiccwithoutpreviouscontext");
                },
            },
        });

        awaittestUtils.dom.click(form.$('.oe_stat_button'));

        form.destroy();
    });

    QUnit.test('clickingonastatbuttonwithnocontext',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<buttonclass="oe_stat_button"type="action"name="1">'+
                                '<fieldname="qux"widget="statinfo"/>'+
                            '</button>'+
                        '</div>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            viewOptions:{
                context:{some_context:true},
            },
            intercepts:{
                execute_action:function(e){
                    assert.deepEqual(e.data.action_data.context,{
                    },"buttoncontextshouldhavebeenevaluatedandgiventotheaction,withmagickeysbutwithoutpreviouscontext");
                },
            },
        });

        awaittestUtils.dom.click(form.$('.oe_stat_button'));

        form.destroy();
    });

    QUnit.test('diplayastatbuttonoutsideabuttonbox',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<sheet>'+
                        '<buttonclass="oe_stat_button"type="action"name="1">'+
                            '<fieldname="int_field"widget="statinfo"/>'+
                        '</button>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.containsOnce(form,'button.o_field_widget',
            "afieldwidgetshouldbedisplayinsidethebutton");
        assert.strictEqual(form.$('button.o_field_widget').children().length,2,
            "thefieldwidgetshouldhave2children,thetextandthevalue");
        assert.strictEqual(parseInt(form.$('button.o_field_widget.o_stat_value').text()),9,
            "thevaluerenderedshouldbethesameasthefieldvalue");
        form.destroy();
    });

    QUnit.test('diplaysomethingelsethanabuttoninabuttonbox',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<divname="button_box"class="oe_button_box">'+
                        '<buttontype="object"class="oe_stat_button"icon="fa-check-square">'+
                            '<fieldname="bar"/>'+
                        '</button>'+
                        '<label/>'+
                    '</div>'+
                '</form>',
            res_id:2,
        });

        assert.strictEqual(form.$('.oe_button_box').children().length,2,
            "buttonboxshouldcontaintwochildren");
        assert.containsOnce(form,'.oe_button_box>.oe_stat_button',
            "buttonboxshouldonlycontainonebutton");
        assert.containsOnce(form,'.oe_button_box>label',
            "buttonboxshouldonlycontainonelabel");

        form.destroy();
    });

    QUnit.test('invisiblefieldsarenotconsideredasvisibleinabuttonbox',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                '<divname="button_box"class="oe_button_box">'+
                    '<fieldname="foo"invisible="1"/>'+
                    '<fieldname="bar"invisible="1"/>'+
                    '<fieldname="int_field"invisible="1"/>'+
                    '<fieldname="qux"invisible="1"/>'+
                    '<fieldname="display_name"invisible="1"/>'+
                    '<fieldname="state"invisible="1"/>'+
                    '<fieldname="date"invisible="1"/>'+
                    '<fieldname="datetime"invisible="1"/>'+
                    '<buttontype="object"class="oe_stat_button"icon="fa-check-square"/>'+
                '</div>'+
                '</form>',
            res_id:2,
        });

        assert.strictEqual(form.$('.oe_button_box').children().length,1,
            "buttonboxshouldcontainonlyonechild");
        assert.hasClass(form.$('.oe_button_box'),'o_not_full',
            "thebuttonboxshouldnotbefull");

        form.destroy();
    });

    QUnit.test('displaycorrectlybuttonbox,inlargesizeclass',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<divname="button_box"class="oe_button_box">'+
                        '<buttontype="object"class="oe_stat_button"icon="fa-check-square">'+
                            '<fieldname="bar"/>'+
                        '</button>'+
                        '<buttontype="object"class="oe_stat_button"icon="fa-check-square">'+
                            '<fieldname="foo"/>'+
                        '</button>'+
                    '</div>'+
                '</form>',
            res_id:2,
            config:{
                device:{size_class:5},
            },
        });

        assert.strictEqual(form.$('.oe_button_box').children().length,2,
            "buttonboxshouldcontaintwochildren");

        form.destroy();
    });

    QUnit.test('one2manydefaultvaluecreation',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].product_ids=[37];
        this.data.partner.fields.product_ids.default=[
            [0,0,{name:'xdroid',partner_type_id:12}]
        ];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_ids"nolabel="1">'+
                                '<treeeditable="top"create="0">'+
                                    '<fieldname="name"readonly="1"/>'+
                                '</tree>'+
                            '</field>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='create'){
                    varcommand=args.args[0].product_ids[0];
                    assert.strictEqual(command[2].partner_type_id,12,
                        "thedefaultpartner_type_idshouldbeequalto12");
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaittestUtils.form.clickSave(form);
        form.destroy();
    });

    QUnit.test('many2manysinsideone2manysaresavedcorrectly',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p">'+
                            '<treeeditable="top">'+
                                '<fieldname="timmy"widget="many2many_tags"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='create'){
                    varcommand=args.args[0].p;
                    assert.deepEqual(command,[[0,command[0][1],{
                        timmy:[[6,false,[12]]],
                    }]],"thedefaultpartner_type_idshouldbeequalto12");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //addao2msubrecordwitham2mtag
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');

        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('one2manys(listeditable)insideone2manysaresavedcorrectly',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="p"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            archs:{
                "partner,false,form":'<form>'+
                        '<fieldname="p">'+
                            '<treeeditable="top">'+
                                '<fieldname="display_name"/>'+
                            '</tree>'+
                        '</field>'+
                    '</form>'
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.deepEqual(args.args[0].p,
                        [[0,args.args[0].p[0][1],{
                            p:[[0,args.args[0].p[0][2].p[0][1],{display_name:"xtv"}]],
                        }]],
                        "createshouldbecalledwiththecorrectarguments");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //addao2msubrecord
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.dom.click($('.modal-body.o_field_one2many.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.editInput($('.modal-bodyinput'),'xtv');
        awaittestUtils.dom.click($('.modal-footerbutton:first'));
        assert.strictEqual($('.modal').length,0,
            "dialogshouldbeclosed");

        varrow=form.$('.o_field_one2many.o_list_view.o_data_row');
        assert.strictEqual(row.children()[0].textContent,'1record',
            "thecellshouldcontainsthenumberofrecord:1");

        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('oe_read_onlyandoe_edit_onlyclassNamesonfieldsinsidegroups',asyncfunction(assert){
        assert.expect(10);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="foo"class="oe_read_only"/>
                        <fieldname="bar"class="oe_edit_only"/>
                    </group>
                </form>`,
            res_id:1,
        });

        assert.hasClass(form.$('.o_form_view'),'o_form_readonly',
            'formshouldbeinreadonlymode');
        assert.isVisible(form.$('.o_field_widget[name=foo]'));
        assert.isVisible(form.$('label:contains(Foo)'));
        assert.isNotVisible(form.$('.o_field_widget[name=bar]'));
        assert.isNotVisible(form.$('label:contains(Bar)'));

        awaittestUtils.form.clickEdit(form);
        assert.hasClass(form.$('.o_form_view'),'o_form_editable',
            'formshouldbeinreadonlymode');
        assert.isNotVisible(form.$('.o_field_widget[name=foo]'));
        assert.isNotVisible(form.$('label:contains(Foo)'));
        assert.isVisible(form.$('.o_field_widget[name=bar]'));
        assert.isVisible(form.$('label:contains(Bar)'));

        form.destroy();
    });

    QUnit.test('oe_read_onlyclassNameishandledinlistviews',asyncfunction(assert){
        assert.expect(7);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p">'+
                            '<treeeditable="top">'+
                                '<fieldname="foo"/>'+
                                '<fieldname="display_name"class="oe_read_only"/>'+
                                '<fieldname="bar"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.hasClass(form.$('.o_form_view'),'o_form_readonly',
            'formshouldbeinreadonlymode');
        assert.isVisible(form.$('.o_field_one2many.o_list_viewtheadth[data-name="display_name"]'),
            'display_namecellshouldbevisibleinreadonlymode');

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.el.querySelector('th[data-name="foo"]').style.width,'100%',
            'Astheonlyvisiblecharfield,"foo"shouldtake100%oftheremainingspace');
        assert.strictEqual(form.el.querySelector('th.oe_read_only').style.width,'0px',
            '"oe_read_only"ineditmodeshouldhavea0pxwidth');

        assert.hasClass(form.$('.o_form_view'),'o_form_editable',
            'formshouldbeineditmode');
        assert.isNotVisible(form.$('.o_field_one2many.o_list_viewtheadth[data-name="display_name"]'),
            'display_namecellshouldnotbevisibleineditmode');

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.owlCompatibilityNextTick();
        assert.hasClass(form.$('.o_form_view.o_list_viewtbodytr:firstinput[name="display_name"]'),
            'oe_read_only','display_nameinputshouldhaveoe_read_onlyclass');

        form.destroy();
    });

    QUnit.test('oe_edit_onlyclassNameishandledinlistviews',asyncfunction(assert){
        assert.expect(5);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p">'+
                            '<treeeditable="top">'+
                                '<fieldname="foo"/>'+
                                '<fieldname="display_name"class="oe_edit_only"/>'+
                                '<fieldname="bar"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.hasClass(form.$('.o_form_view'),'o_form_readonly',
            'formshouldbeinreadonlymode');
        assert.isNotVisible(form.$('.o_field_one2many.o_list_viewtheadth[data-name="display_name"]'),
            'display_namecellshouldnotbevisibleinreadonlymode');

        awaittestUtils.form.clickEdit(form);
        assert.hasClass(form.$('.o_form_view'),'o_form_editable',
            'formshouldbeineditmode');
        assert.isVisible(form.$('.o_field_one2many.o_list_viewtheadth[data-name="display_name"]'),
            'display_namecellshouldbevisibleineditmode');

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.owlCompatibilityNextTick();
        assert.hasClass(form.$('.o_form_view.o_list_viewtbodytr:firstinput[name="display_name"]'),
            'oe_edit_only','display_nameinputshouldhaveoe_edit_onlyclass');

        form.destroy();
    });

    QUnit.test('*_view_refincontextarepassedcorrectly',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(3);

        createView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p"context="{\'tree_view_ref\':\'module.tree_view_ref\'}"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            intercepts:{
                load_views:function(event){
                    varcontext=event.data.context;
                    assert.strictEqual(context.tree_view_ref,'module.tree_view_ref',
                        "contextshouldcontaintree_view_ref");
                    event.data.on_success();
                }
            },
            viewOptions:{
                context:{some_context:false},
            },
            mockRPC:function(route,args){
                if(args.method==='read'){
                    assert.strictEqual('some_context'inargs.kwargs.context&&!args.kwargs.context.some_context,true,
                        "thecontextshouldhavebeenset");
                }
                returnthis._super.apply(this,arguments);
            },
        }).then(asyncfunction(form){
            //reloadtocheckthattherecord'scontexthasn'tbeenmodified
            awaitform.reload();
            form.destroy();
            done();
        });
    });

    QUnit.test('noninlinesubviewandcreate=0inactioncontext',asyncfunction(assert){
        //thecreate=0shouldapplyonthemainview(form),butnotonsubviews
        assert.expect(2);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="product_ids"mode="kanban"/></form>',
            archs:{
                "product,false,kanban":`<kanban>
                                            <templates><tt-name="kanban-box">
                                                <div><fieldname="name"/></div>
                                            </t></templates>
                                        </kanban>`,
            },
            res_id:1,
            viewOptions:{
                context:{create:false},
                mode:'edit',
            },
        });

        assert.containsNone(form,'.o_form_button_create');
        assert.containsOnce(form,'.o-kanban-button-new');

        form.destroy();
    });

    QUnit.test('readonlyfieldswithmodifiersmaybesaved',asyncfunction(assert){
        //thereadonlypropertyonthefielddescriptiononlyappliesonview,
        //thisisnotaDBconstraint.Itshouldbeseenasadefaultvalue,
        //thatmaybeoverriddeninviews,forexamplewithmodifiers.So
        //basically,afielddefinedasreadonlymaybeedited.
        assert.expect(3);

        this.data.partner.fields.foo.readonly=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="foo"attrs="{\'readonly\':[(\'bar\',\'=\',False)]}"/>'+
                        '<fieldname="bar"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{foo:'Newfoovalue'},
                        "thenewvalueshouldbesaved");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //barbeingsettotrue,fooshouldn'tbereadonlyandthusitsvalue
        //couldbesaved,evenifinitsfielddescriptionitisreadonly
        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'input[name="foo"]',
            "foofieldshouldbeeditable");
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),'Newfoovalue');

        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('.o_field_widget[name=foo]').text(),'Newfoovalue',
            "newvalueforfoofieldshouldhavebeensaved");

        form.destroy();
    });

    QUnit.test('readonlysetbymodifierdonotbreakmany2many_tags',asyncfunction(assert){
        assert.expect(0);

        this.data.partner.onchanges={
            bar:function(obj){
                obj.timmy=[[6,false,[12]]];
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                      '<sheet>'+
                          '<fieldname="bar"/>'+
                          '<fieldname="timmy"widget="many2many_tags"attrs="{\'readonly\':[(\'bar\',\'=\',True)]}"/>'+
                      '</sheet>'+
                  '</form>',
            res_id:5,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]input'));

        form.destroy();
    });

    QUnit.test('checkifidandactive_idaredefined',asyncfunction(assert){
        assert.expect(2);

        letcheckOnchange=false;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p"context="{\'default_trululu\':active_id,\'current_id\':id}">'+
                            '<tree>'+
                                '<fieldname="trululu"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            archs:{
                "partner,false,form":'<form><fieldname="trululu"/></form>'
            },
            mockRPC:function(route,args){
                if(args.method==='onchange'&&checkOnchange){
                    assert.strictEqual(args.kwargs.context.current_id,false,
                        "current_idshouldbefalse");
                    assert.strictEqual(args.kwargs.context.default_trululu,false,
                        "default_trululushouldbefalse");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        checkOnchange=true;
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        form.destroy();
    });

    QUnit.test('modifiersareconsideredonmultiple<footer/>tags',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="bar"/>'+
                    '<footerattrs="{\'invisible\':[(\'bar\',\'=\',False)]}">'+
                        '<button>Hello</button>'+
                        '<button>World</button>'+
                    '</footer>'+
                    '<footerattrs="{\'invisible\':[(\'bar\',\'!=\',False)]}">'+
                        '<button>Foo</button>'+
                    '</footer>'+
                '</form>',
            res_id:1,
            viewOptions:{
                footerToButtons:true,
                mode:'edit',
            },
        });

        assert.deepEqual(getVisibleButtonTexts(),["Hello","World"],
            "onlythefirstbuttonsectionshouldbevisible");

        awaittestUtils.dom.click(form.$(".o_field_booleaninput"));

        assert.deepEqual(getVisibleButtonTexts(),["Foo"],
            "onlythesecondbuttonsectionshouldbevisible");

        form.destroy();

        functiongetVisibleButtonTexts(){
            var$visibleButtons=form.$buttons.find('button:visible');
            return_.map($visibleButtons,function(el){
                returnel.innerHTML.trim();
            });
        }
    });

    QUnit.test('buttonsinfooteraremovedto$buttonsifnecessary',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                        '<footer>'+
                            '<buttonstring="Create"type="object"class="infooter"/>'+
                        '</footer>'+
                '</form>',
            res_id:1,
            viewOptions:{footerToButtons:true},
        });

        assert.containsOnce(form.$('.o_control_panel'),'button.infooter');
        assert.containsNone(form.$('.o_form_view'),'button.infooter');

        //checkthatthisstillworksafterareload
        awaittestUtils.form.reload(form);

        assert.containsOnce(form.$('.o_control_panel'),'button.infooter');
        assert.containsNone(form.$('.o_form_view'),'button.infooter');

        form.destroy();
    });

    QUnit.test('opennewrecordevenwithwarningmessage',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.onchanges={foo:true};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="foo"/></group>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        warning:{
                            title:"Warning",
                            message:"Anywarning."
                        }
                    });
                }
                returnthis._super.apply(this,arguments);
            },

        });
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input').val(),'blip','inputshouldcontainrecordvalue');
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"tralala");
        assert.strictEqual(form.$('input').val(),'tralala','inputshouldcontainnewvalue');

        awaitform.reload({currentId:false});
        assert.strictEqual(form.$('input').val(),'',
            'inputshouldhavenovalueafterreload');

        form.destroy();
    });

    QUnit.test('renderstatbuttonwithstringinline',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<formstring="ManufacturingOrders">'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<buttonstring="InventoryMoves"class="oe_stat_button"icon="fa-arrows-v"/>'+
                        '</div>'+
                    '</sheet>'+
                '</form>',
        });
        var$button=form.$('.o_form_view.o_form_sheet.oe_button_box.oe_stat_buttonspan');
        assert.strictEqual($button.text(),"InventoryMoves",
            "thestatbuttonshouldcontainaspanwiththestringattributevalue");
        form.destroy();
    });

    QUnit.test('rendererwaitsforasynchronousfieldsrendering',asyncfunction(assert){
        assert.expect(1);
        vardone=assert.async();

        testUtils.createView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="bar"/>'+
                    '<fieldname="foo"widget="ace"/>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            res_id:1,
        }).then(function(form){
            assert.containsOnce(form,'.ace_editor',
                "shouldhavewaitedforacetoloaditsdependencies");
            form.destroy();
            done();
        });
    });

    QUnit.test('openone2manyformcontainingone2many',asyncfunction(assert){
        assert.expect(9);

        this.data.partner.records[0].product_ids=[37];
        this.data.product.fields.partner_type_ids={
            string:"one2manypartner",type:"one2many",relation:"partner_type",
        };
        this.data.product.records[0].partner_type_ids=[12];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_ids">'+
                                '<treecreate="0">'+
                                    '<fieldname="display_name"/>'+
                                    '<fieldname="partner_type_ids"/>'+
                                '</tree>'+
                            '</field>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'product,false,form':
                    '<formstring="Products">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="partner_type_ids">'+
                                    '<treecreate="0">'+
                                        '<fieldname="display_name"/>'+
                                        '<fieldname="color"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
            },
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
        });
        varrow=form.$('.o_field_one2many.o_list_view.o_data_row');
        assert.strictEqual(row.children()[1].textContent,'1record',
            "thecellshouldcontainsthenumberofrecord:1");
        awaittestUtils.dom.click(row);
        varmodal_row=$('.modal-body.o_form_sheet.o_field_one2many.o_list_view.o_data_row');
        assert.strictEqual(modal_row.children().length,2,
            "therowshouldcontainsthe2fieldsdefinedintheformview");
        assert.strictEqual($(modal_row).text(),"gold2",
            "thevalueofthefieldsshouldbefetchedanddisplayed");
        assert.verifySteps(['read','read','load_views','read','read'],
            "thereshouldbe4readrpcs");
        form.destroy();
    });

    QUnit.test('ineditmode,firstfieldisfocused',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="bar"/>'+
                '</form>',
            res_id:1,
        });
        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(document.activeElement,form.$('input[name="foo"]')[0],
            "foofieldshouldhavefocus");
        assert.strictEqual(form.$('input[name="foo"]')[0].selectionStart,3,
            "cursorshouldbeattheend");

        form.destroy();
    });

    QUnit.test('autofocusfieldsarefocused',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="bar"/>'+
                        '<fieldname="foo"default_focus="1"/>'+
                '</form>',
            res_id:1,
        });
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(document.activeElement,form.$('input[name="foo"]')[0],
            "foofieldshouldhavefocus");

        form.destroy();
    });

    QUnit.test('correctamountofbuttons',asyncfunction(assert){
        assert.expect(7);

        varself=this;
        varbuttons=Array(8).join(
            '<buttontype="object"class="oe_stat_button"icon="fa-check-square">'+
                '<fieldname="bar"/>'+
            '</button>'
        );
        varstatButtonSelector='.oe_stat_button:not(.dropdown-item,.dropdown-toggle)';

        varcreateFormWithDeviceSizeClass=asyncfunction(size_class){
            returnawaitcreateView({
                View:FormView,
                model:'partner',
                data:self.data,
                arch:'<form>'+
                    '<divname="button_box"class="oe_button_box">'
                        +buttons+
                    '</div>'+
                '</form>',
                res_id:2,
                config:{
                    device:{size_class:size_class},
                },
            });
        };

        varassertFormContainsNButtonsWithSizeClass=asyncfunction(size_class,n){
            varform=awaitcreateFormWithDeviceSizeClass(size_class);
            assert.containsN(form,statButtonSelector,n,'Theformhastheexpectedamountofbuttons');
            form.destroy();
        };

        awaitassertFormContainsNButtonsWithSizeClass(0,2);
        awaitassertFormContainsNButtonsWithSizeClass(1,2);
        awaitassertFormContainsNButtonsWithSizeClass(2,2);
        awaitassertFormContainsNButtonsWithSizeClass(3,4);
        awaitassertFormContainsNButtonsWithSizeClass(4,7);
        awaitassertFormContainsNButtonsWithSizeClass(5,7);
        awaitassertFormContainsNButtonsWithSizeClass(6,7);
    });

    QUnit.test('cansetbin_sizetofalseincontext',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                  '</form>',
            res_id:1,
            context:{
                bin_size:false,
            },
            mockRPC:function(route,args){
                assert.strictEqual(args.kwargs.context.bin_size,false,
                    "bin_sizeshouldalwaysbeinthecontextandshouldbefalse");
                returnthis._super(route,args);
            }
        });
        form.destroy();
    });

    QUnit.test('nofocussetonformwhenclosingmany2onemodaliflastActivatedFieldIndexisnotset',asyncfunction(assert){
        assert.expect(8);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="p"/>'+
                    '<fieldname="timmy"/>'+
                    '<fieldname="product_ids"/>'+
                    '<fieldname="trululu"/>'+
                '</form>',
            res_id:2,
            archs:{
                'partner,false,list':'<tree><fieldname="display_name"/></tree>',
                'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                'partner,false,form':'<form><fieldname="trululu"/></form>',
                'product,false,list':'<tree><fieldname="name"/></tree>',
            },
            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
        });

        //setmax-heighttohavescrollforcefullysothatwecantestscrollpositionaftermodalclose
        $('.o_content').css({'overflow':'auto','max-height':'300px'});
        //Openmany2onemodal,lastActivatedFieldIndexwillnotsetaswedirectlyclickonexternalbutton
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual($(".o_content").scrollTop(),0,"scrollpositionshouldbe0");

        form.$(".o_field_many2one[name='trululu'].o_input").focus();
        assert.notStrictEqual($(".o_content").scrollTop(),0,"scrollpositionshouldnotbe0");

        awaittestUtils.dom.click(form.$('.o_external_button'));
        //Closemodal
        awaittestUtils.dom.click($('.modal').last().find('button[class="close"]'));
        assert.notStrictEqual($(".o_content").scrollTop(),0,
            "scrollpositionshouldnotbe0afterclosingmodal");
        assert.containsNone(document.body,'.modal','Thereshouldbenomodal');
        assert.doesNotHaveClass($('body'),'modal-open','Modalisnotsaidopened');
        assert.strictEqual(form.renderer.lastActivatedFieldIndex,-1,
            "lastActivatedFieldIndexis-1");
        assert.equal(document.activeElement,$('body')[0],
            'bodyisfocused,shouldnotsetfocusonformwidget');
        assert.notStrictEqual(document.activeElement,form.$('.o_field_many2one[name="trululu"].o_input'),
            'fieldwidgetshouldnotbefocusedwhenlastActivatedFieldIndexis-1');

        form.destroy();
    });

    QUnit.test('increatemode,autofocusfieldsarefocused',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="foo"default_focus="1"/>'+
                '</form>',
        });
        assert.strictEqual(document.activeElement,form.$('input[name="foo"]')[0],
            "foofieldshouldhavefocus");

        form.destroy();
    });

    QUnit.test('createwithfalsevalues',asyncfunction(assert){
        assert.expect(1);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="bar"/></group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.strictEqual(args.args[0].bar,false,
                        "thefalsevalueshouldbegivenasparameter");
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('autofocusfirstvisiblefield',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="int_field"invisible="1"/>'+
                        '<fieldname="foo"/>'+
                '</form>',
        });
        assert.strictEqual(document.activeElement,form.$('input[name="foo"]')[0],
            "foofieldshouldhavefocus");

        form.destroy();
    });

    QUnit.test('noautofocuswithdisable_autofocusoption[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="foo"/>'+
                '</form>',
            viewOptions:{
                disable_autofocus:true,
            },
        });
        assert.notStrictEqual(document.activeElement,form.$('input[name="int_field"]')[0],
            "int_fieldfieldshouldnothavefocus");

        awaitform.update({});

        assert.notStrictEqual(document.activeElement,form.$('input[name="int_field"]')[0],
            "int_fieldfieldshouldnothavefocus");

        form.destroy();
    });

    QUnit.test('openone2manyformcontainingmany2many_tags',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].product_ids=[37];
            this.data.product.fields.partner_type_ids={
                string:"many2manypartner_type",type:"many2many",relation:"partner_type",
            };
            this.data.product.records[0].partner_type_ids=[12,14];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                res_id:1,
                data:this.data,
                arch:'<formstring="Partners">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="product_ids">'+
                                    '<treecreate="0">'+
                                        '<fieldname="display_name"/>'+
                                        '<fieldname="partner_type_ids"widget="many2many_tags"/>'+
                                    '</tree>'+
                                    '<formstring="Products">'+
                                        '<sheet>'+
                                            '<group>'+
                                                '<labelfor="partner_type_ids"/>'+
                                                '<div>'+
                                                    '<fieldname="partner_type_ids"widget="many2many_tags"/>'+
                                                '</div>'+
                                            '</group>'+
                                        '</sheet>'+
                                    '</form>'+
                                '</field>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });
            varrow=form.$('.o_field_one2many.o_list_view.o_data_row');
            awaittestUtils.dom.click(row);
            assert.verifySteps(['read','read','read'],
                "thereshouldbe3readrpcs");
            form.destroy();
        });

    QUnit.test('onchangesareappliedbeforecheckingifitcanbesaved',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.onchanges.foo=function(obj){};
        this.data.partner.fields.foo.required=true;

        vardef=testUtils.makeTestPromise();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet><group>'+
                        '<fieldname="foo"/>'+
                    '</group></sheet>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                assert.step(args.method);
                if(args.method==='onchange'){
                    returndef.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
            services:{
                notification:NotificationService.extend({
                    notify:function(params){
                        assert.step(params.type);
                    }
                }),
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),'');
        awaittestUtils.form.clickSave(form);

        def.resolve();
        awaittestUtils.nextTick();

        assert.verifySteps(['read','onchange','danger']);
        form.destroy();
    });

    QUnit.test('displaytoolbar',asyncfunction(assert){
        assert.expect(8);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            res_id:1,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="bar"/></group>'+
                '</form>',
            toolbar:{
                action:[{
                    model_name:'partner',
                    name:'Actionpartner',
                    type:'ir.actions.server',
                    usage:'ir_actions_server',
                }],
                print:[],
            },
            viewOptions:{
                hasActionMenus:true,
            },
            mockRPC:function(route,args){
                if(route==='/web/action/load'){
                    assert.strictEqual(args.context.active_id,1,
                        "theactive_idshoudbe1.");
                    assert.deepEqual(args.context.active_ids,[1],
                        "theactive_idsshouldbeanarraywith1inside.");
                    returnPromise.resolve({});
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsNone(form,'.o_cp_action_menus.o_dropdown:contains(Print)');
        assert.containsOnce(form,'.o_cp_action_menus.o_dropdown:contains(Action)');

        awaitcpHelpers.toggleActionMenu(form);

        assert.containsN(form,'.o_cp_action_menus.dropdown-item',3,"thereshouldbe3actions");
        assert.strictEqual(form.$('.o_cp_action_menus.dropdown-item:last').text().trim(),'Actionpartner',
            "thecustomactionshouldhave'Actionpartner'asname");

        awaittestUtils.mock.intercept(form,'do_action',function(event){
            varcontext=event.data.action.context.__contexts[1];
            assert.strictEqual(context.active_id,1,
                "theactive_idshoudbe1.");
            assert.deepEqual(context.active_ids,[1],
                "theactive_idsshouldbeanarraywith1inside.");
        });
        awaitcpHelpers.toggleMenuItem(form,"Actionpartner");

        form.destroy();
    });

    QUnit.test('checkinteractionsbetweenmultipleFormViewDialogs',asyncfunction(assert){
        assert.expect(8);

        this.data.product.fields.product_ids={
            string:"one2manyproduct",type:"one2many",relation:"product",
        };

        this.data.partner.records[0].product_id=37;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_id"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'product,false,form':
                    '<formstring="Products">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="display_name"/>'+
                                '<fieldname="product_ids"/>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
                'product,false,list':'<tree><fieldname="display_name"/></tree>'
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/product/get_formview_id'){
                    returnPromise.resolve(false);
                }elseif(args.method==='write'){
                    assert.strictEqual(args.model,'product',
                        "shouldwriteonproductmodel");
                    assert.strictEqual(args.args[1].product_ids[0][2].display_name,'xtv',
                        "display_nameofthenewobjectshouldbextv");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);
        //Openfirstdialog
        awaittestUtils.dom.click(form.$('.o_external_button'));
        assert.strictEqual($('.modal').length,1,
            "OneFormViewDialogshouldbeopened");
        var$firstModal=$('.modal');
        assert.strictEqual($('.modal.modal-title').first().text().trim(),'Open:Product',
            "dialogtitleshoulddisplaythepythonfieldstringaslabel");
        assert.strictEqual($firstModal.find('input').val(),'xphone',
            "display_nameshouldbecorrectlydisplayed");

        //Openseconddialog
        awaittestUtils.dom.click($firstModal.find('.o_field_x2many_list_row_adda'));
        assert.strictEqual($('.modal').length,2,
            "twoFormViewDialogsshouldbeopened");
        var$secondModal=$('.modal:nth(1)');
        //Addnewvalue
        awaittestUtils.fields.editInput($secondModal.find('input'),'xtv');
        awaittestUtils.dom.click($secondModal.find('.modal-footerbutton:first'));
        assert.strictEqual($('.modal').length,1,
            "lastopeneddialogshouldbeclosed");

        //Checkthatdatainfirstdialogiscorrectlyupdated
        assert.strictEqual($firstModal.find('tr.o_data_rowtd').text(),'xtv',
            "shouldhaveaddedalinewithxtvasnewrecord");
        awaittestUtils.dom.click($firstModal.find('.modal-footerbutton:first'));
        form.destroy();
    });

    QUnit.test('fieldsandrecordcontextsarenotmixed',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="trululu"context="{\'test\':1}"/>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='name_search'){
                    assert.strictEqual(args.kwargs.context.test,1,
                        "field'scontextshouldbesent");
                    assert.notOk('mainContext'inargs.kwargs.context,
                        "record'scontextshouldnotbesent");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:2,
            viewOptions:{
                mode:'edit',
                context:{mainContext:3},
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));

        form.destroy();
    });

    QUnit.test('donotactivateanhiddentabwhenswitchingbetweenrecords',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<notebook>'+
                            '<pagestring="Foo"attrs=\'{"invisible":[["id","=",2]]}\'>'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                            '<pagestring="Bar">'+
                                '<fieldname="bar"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:1,
        });

        assert.strictEqual(form.$('.o_notebook.nav-item:not(.o_invisible_modifier)').length,2,
            "bothtabsshouldbevisible");
        assert.hasClass(form.$('.o_notebook.nav-link:first'),'active',
            "firsttabshouldbeactive");

        //clickonthepagertoswitchtothenextrecord
        awaitcpHelpers.pagerNext(form);

        assert.strictEqual(form.$('.o_notebook.nav-item:not(.o_invisible_modifier)').length,1,
            "onlythesecondtabshouldbevisible");
        assert.hasClass(form.$('.o_notebook.nav-item:not(.o_invisible_modifier).nav-link'),'active',
            "thevisibletabshouldbeactive");

        //clickonthepagertoswitchbacktothepreviousrecord
        awaitcpHelpers.pagerPrevious(form);

        assert.strictEqual(form.$('.o_notebook.nav-item:not(.o_invisible_modifier)').length,2,
            "bothtabsshouldbevisibleagain");
        assert.hasClass(form.$('.o_notebook.nav-link:nth(1)'),'active',
            "secondtabshouldbeactive");

        form.destroy();
    });

    QUnit.test('supportanchortagswithactiontype',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                            '<atype="action"name="42"><iclass="fafa-arrow-right"/>Clickme!</a>'+
                    '</form>',
            res_id:1,
            intercepts:{
                do_action:function(event){
                    assert.strictEqual(event.data.action,"42",
                        "shouldtriggerdo_actionwithcorrectactionparameter");
                }
            }
        });
        awaittestUtils.dom.click(form.$('a[type="action"]'));

        form.destroy();
    });

    QUnit.test('donotperformextraRPCtoreadinvisiblemany2onefields',asyncfunction(assert){
        //Thistestisn'treallymeaningfulanymore,sincedefault_getand(first)onchangerpcs
        //havebeenmergedinasingleonchangerpc,returningnamegetformany2onefields.Butit
        //isn'treallycostly,anditstillchecksrpcsdonewhencreatinganewrecordwitham2o.
        assert.expect(2);

        this.data.partner.fields.trululu.default=2;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="trululu"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
        });

        assert.verifySteps(['onchange'],"onlyoneRPCshouldhavebeendone");

        form.destroy();
    });

    QUnit.test('donotperformextraRPCtoreadinvisiblex2manyfields',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].p=[2];//one2many
        this.data.partner.records[0].product_ids=[37];//one2many
        this.data.partner.records[0].timmy=[12];//many2many

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p"invisible="1"/>'+//noinlineview
                        '<fieldname="product_ids"invisible="1">'+//inlineview
                            '<tree><fieldname="display_name"/></tree>'+
                        '</field>'+
                        '<fieldname="timmy"invisible="1"widget="many2many_tags"/>'+//noview
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
        });

        assert.verifySteps(['read'],"onlyonereadshouldhavebeendone");

        form.destroy();
    });

    QUnit.test('default_orderonx2manyembeddedview',asyncfunction(assert){
        assert.expect(11);

        this.data.partner.fields.display_name.sortable=true;
        this.data.partner.records[0].p=[1,4];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p">'+
                            '<treedefault_order="foodesc">'+
                                '<fieldname="display_name"/>'+
                                '<fieldname="foo"/>'+
                                '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner,false,form':
                    '<formstring="Partner">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="foo"/>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
            },
            res_id:1,
        });

        assert.ok(form.$('.o_field_one2manytbodytr:firsttd:contains(yop)').length,
            "record1shouldbefirst");
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.strictEqual($('.modal').length,1,
            "FormViewDialogshouldbeopened");
        awaittestUtils.fields.editInput($('.modalinput[name="foo"]'),'xop');
        awaittestUtils.dom.click($('.modal-footerbutton:eq(1)'));
        awaittestUtils.fields.editInput($('.modalinput[name="foo"]'),'zop');
        awaittestUtils.dom.click($('.modal-footerbutton:first'));

        //client-sidesort
        assert.ok(form.$('.o_field_one2manytbodytr:eq(0)td:contains(zop)').length,
            "recordzopshouldbefirst");
        assert.ok(form.$('.o_field_one2manytbodytr:eq(1)td:contains(yop)').length,
            "recordyopshouldbesecond");
        assert.ok(form.$('.o_field_one2manytbodytr:eq(2)td:contains(xop)').length,
            "recordxopshouldbethird");

        //server-sidesort
        awaittestUtils.form.clickSave(form);
        assert.ok(form.$('.o_field_one2manytbodytr:eq(0)td:contains(zop)').length,
            "recordzopshouldbefirst");
        assert.ok(form.$('.o_field_one2manytbodytr:eq(1)td:contains(yop)').length,
            "recordyopshouldbesecond");
        assert.ok(form.$('.o_field_one2manytbodytr:eq(2)td:contains(xop)').length,
            "recordxopshouldbethird");

        //client-sidesortonedit
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_one2manytbodytr:eq(1)td:contains(yop)'));
        awaittestUtils.fields.editInput($('.modalinput[name="foo"]'),'zzz');
        awaittestUtils.dom.click($('.modal-footerbutton:first'));
        assert.ok(form.$('.o_field_one2manytbodytr:eq(0)td:contains(zzz)').length,
            "recordzzzshouldbefirst");
        assert.ok(form.$('.o_field_one2manytbodytr:eq(1)td:contains(zop)').length,
            "recordzopshouldbesecond");
        assert.ok(form.$('.o_field_one2manytbodytr:eq(2)td:contains(xop)').length,
            "recordxopshouldbethird");

        form.destroy();
    });

    QUnit.test('actioncontextisusedwhenevaluatingdomains',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="trululu"domain="[(\'id\',\'in\',context.get(\'product_ids\',[]))]"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                context:{product_ids:[45,46,47]}
            },
            mockRPC:function(route,args){
                if(args.method==='name_search'){
                    assert.deepEqual(args.kwargs.args[0],['id','in',[45,46,47]],
                        "domainshouldbeproperlyevaluated");
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('div[name="trululu"]input'));

        form.destroy();
    });

    QUnit.test('formrenderingwithgroupswithcol/colspan',asyncfunction(assert){
        assert.expect(45);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<sheet>'+
                        '<groupcol="6"class="parent_group">'+
                            '<groupcol="4"colspan="3"class="group_4">'+
                                '<divcolspan="3"/>'+
                                '<divcolspan="2"/><div/>'+
                                '<divcolspan="4"/>'+
                            '</group>'+
                            '<groupcol="3"colspan="4"class="group_3">'+
                                '<groupcol="1"class="group_1">'+
                                    '<div/><div/><div/>'+
                                '</group>'+
                                '<div/>'+
                                '<groupcol="3"class="field_group">'+
                                    '<fieldname="foo"colspan="3"/>'+
                                    '<div/><fieldname="bar"nolabel="1"/>'+
                                    '<fieldname="qux"/>'+
                                    '<fieldname="int_field"colspan="3"nolabel="1"/>'+
                                    '<span/><fieldname="product_id"/>'+
                                '</group>'+
                            '</group>'+
                        '</group>'+
                        '<group>'+
                            '<fieldname="p">'+
                                '<tree>'+
                                    '<fieldname="display_name"/>'+
                                    '<fieldname="foo"/>'+
                                    '<fieldname="int_field"/>'+
                                '</tree>'+
                            '</field>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        var$parentGroup=form.$('.parent_group');
        var$group4=form.$('.group_4');
        var$group3=form.$('.group_3');
        var$group1=form.$('.group_1');
        var$fieldGroup=form.$('.field_group');

        //Verifyoutergroup/innergroup
        assert.strictEqual($parentGroup[0].tagName,'DIV',".parent_groupshouldbeanoutergroup");
        assert.strictEqual($group4[0].tagName,'TABLE',".group_4shouldbeaninnergroup");
        assert.strictEqual($group3[0].tagName,'DIV',".group_3shouldbeanoutergroup");
        assert.strictEqual($group1[0].tagName,'TABLE',".group_1shouldbeaninnergroup");
        assert.strictEqual($fieldGroup[0].tagName,'TABLE',".field_groupshouldbeaninnergroup");

        //Verify.parent_groupcontent
        var$parentGroupChildren=$parentGroup.children();
        assert.strictEqual($parentGroupChildren.length,2,"thereshouldbe2groupsin.parent_group");
        assert.ok($parentGroupChildren.eq(0).is('.o_group_col_6'),"first.parent_groupgroupshouldbe1/2parentwidth");
        assert.ok($parentGroupChildren.eq(1).is('.o_group_col_8'),"second.parent_groupgroupshouldbe2/3parentwidth");

        //Verify.group_4content
        var$group4rows=$group4.find('>tbody>tr');
        assert.strictEqual($group4rows.length,3,"thereshouldbe3rowsin.group_4");
        var$group4firstRowTd=$group4rows.eq(0).children('td');
        assert.strictEqual($group4firstRowTd.length,1,"thereshouldbe1tdinfirstrow");
        assert.hasAttrValue($group4firstRowTd,'colspan',"3","thefirsttdcolspanshouldbe3");
        assert.strictEqual($group4firstRowTd.attr('style').substr(0,9),"width:75","thefirsttdshouldbe75%width");
        assert.strictEqual($group4firstRowTd.children()[0].tagName,"DIV","thefirsttdshouldcontainadiv");
        var$group4secondRowTds=$group4rows.eq(1).children('td');
        assert.strictEqual($group4secondRowTds.length,2,"thereshouldbe2tdsinsecondrow");
        assert.hasAttrValue($group4secondRowTds.eq(0),'colspan',"2","thefirsttdcolspanshouldbe2");
        assert.strictEqual($group4secondRowTds.eq(0).attr('style').substr(0,9),"width:50","thefirsttdbe50%width");
        assert.hasAttrValue($group4secondRowTds.eq(1),'colspan',undefined,"thesecondtdcolspanshouldbedefaultone(1)");
        assert.strictEqual($group4secondRowTds.eq(1).attr('style').substr(0,9),"width:25","thesecondtdbe75%width");
        var$group4thirdRowTd=$group4rows.eq(2).children('td');
        assert.strictEqual($group4thirdRowTd.length,1,"thereshouldbe1tdinthirdrow");
        assert.hasAttrValue($group4thirdRowTd,'colspan',"4","thefirsttdcolspanshouldbe4");
        assert.strictEqual($group4thirdRowTd.attr('style').substr(0,10),"width:100","thefirsttdshouldbe100%width");

        //Verify.group_3content
        assert.strictEqual($group3.children().length,3,".group_3shouldhave3children");
        assert.strictEqual($group3.children('.o_group_col_4').length,3,".group_3shouldhave3childrenof1/3width");

        //Verify.group_1content
        assert.strictEqual($group1.find('>tbody>tr').length,3,"thereshouldbe3rowsin.group_1");

        //Verify.field_groupcontent
        var$fieldGroupRows=$fieldGroup.find('>tbody>tr');
        assert.strictEqual($fieldGroupRows.length,5,"thereshouldbe5rowsin.field_group");
        var$fieldGroupFirstRowTds=$fieldGroupRows.eq(0).children('td');
        assert.strictEqual($fieldGroupFirstRowTds.length,2,"thereshouldbe2tdsinfirstrow");
        assert.hasClass($fieldGroupFirstRowTds.eq(0),'o_td_label',"firsttdshouldbealabeltd");
        assert.hasAttrValue($fieldGroupFirstRowTds.eq(1),'colspan',"2","secondtdcolspanshouldbegivencolspan(3)-1(label)");
        assert.strictEqual($fieldGroupFirstRowTds.eq(1).attr('style').substr(0,10),"width:100","secondtdwidthshouldbe100%");
        var$fieldGroupSecondRowTds=$fieldGroupRows.eq(1).children('td');
        assert.strictEqual($fieldGroupSecondRowTds.length,2,"thereshouldbe2tdsinsecondrow");
        assert.hasAttrValue($fieldGroupSecondRowTds.eq(0),'colspan',undefined,"firsttdcolspanshouldbedefaultone(1)");
        assert.strictEqual($fieldGroupSecondRowTds.eq(0).attr('style').substr(0,9),"width:33","firsttdwidthshouldbe33.3333%");
        assert.hasAttrValue($fieldGroupSecondRowTds.eq(1),'colspan',undefined,"secondtdcolspanshouldbedefaultone(1)");
        assert.strictEqual($fieldGroupSecondRowTds.eq(1).attr('style').substr(0,9),"width:33","secondtdwidthshouldbe33.3333%");
        var$fieldGroupThirdRowTds=$fieldGroupRows.eq(2).children('td');//newrowaslabel/fieldpaircolspanisgreaterthanremainingspace
        assert.strictEqual($fieldGroupThirdRowTds.length,2,"thereshouldbe2tdsinthirdrow");
        assert.hasClass($fieldGroupThirdRowTds.eq(0),'o_td_label',"firsttdshouldbealabeltd");
        assert.hasAttrValue($fieldGroupThirdRowTds.eq(1),'colspan',undefined,"secondtdcolspanshouldbedefaultone(1)");
        assert.strictEqual($fieldGroupThirdRowTds.eq(1).attr('style').substr(0,9),"width:50","secondtdshouldbe50%width");
        var$fieldGroupFourthRowTds=$fieldGroupRows.eq(3).children('td');
        assert.strictEqual($fieldGroupFourthRowTds.length,1,"thereshouldbe1tdinfourthrow");
        assert.hasAttrValue($fieldGroupFourthRowTds,'colspan',"3","thetdshouldhaveacolspanequalto3");
        assert.strictEqual($fieldGroupFourthRowTds.attr('style').substr(0,10),"width:100","thetdshouldhave100%width");
        var$fieldGroupFifthRowTds=$fieldGroupRows.eq(4).children('td');//label/fieldpaircanbeputafterthe1-colspanspan
        assert.strictEqual($fieldGroupFifthRowTds.length,3,"thereshouldbe3tdsinfourthrow");
        assert.strictEqual($fieldGroupFifthRowTds.eq(0).attr('style').substr(0,9),"width:50","thefirsttdshould50%width");
        assert.hasClass($fieldGroupFifthRowTds.eq(1),'o_td_label',"thesecondtdshouldbealabeltd");
        assert.strictEqual($fieldGroupFifthRowTds.eq(2).attr('style').substr(0,9),"width:50","thethirdtdshould50%width");

        form.destroy();
    });

    QUnit.test('outerandinnergroupsstringattribute',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<groupstring="parentgroup"class="parent_group">'+
                            '<groupstring="childgroup1"class="group_1">'+
                                '<fieldname="bar"/>'+
                            '</group>'+
                            '<groupstring="childgroup2"class="group_2">'+
                                '<fieldname="bar"/>'+
                            '</group>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        var$parentGroup=form.$('.parent_group');
        var$group1=form.$('.group_1');
        var$group2=form.$('.group_2');

        assert.containsN(form,'table.o_inner_group',2,
            "shouldcontaintwoinnergroups");
        assert.strictEqual($group1.find('.o_horizontal_separator').length,1,
            "innergroupshouldcontainonestringseparator");
        assert.strictEqual($group1.find('.o_horizontal_separator:contains(childgroup1)').length,1,
            "firstinnergroupshouldcontain'childgroup1'string");
        assert.strictEqual($group2.find('.o_horizontal_separator:contains(childgroup2)').length,1,
            "secondinnergroupshouldcontain'childgroup2'string");
        assert.strictEqual($parentGroup.find('>div.o_horizontal_separator:contains(parentgroup)').length,1,
            "outergroupshouldcontain'parentgroup'string");

        form.destroy();
    });

    QUnit.test('formgroupwithnewlinetaginside',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<sheet>'+
                        '<groupcol="5"class="main_inner_group">'+
                            //col=5otherwisethetestisokevenwithoutthe
                            //newlinecodeasthiswillrendera<newline/>DOM
                            //elementinthethirdcolumn,leavingnoplacefor
                            //thenextfieldanditslabelonthesameline.
                            '<fieldname="foo"/>'+
                            '<newline/>'+
                            '<fieldname="bar"/>'+
                            '<fieldname="qux"/>'+
                        '</group>'+
                        '<groupcol="3">'+
                            //col=3otherwisethetestisokevenwithoutthe
                            //newlinecodeasthiswillrendera<newline/>DOM
                            //elementwiththeo_group_col_6class,leavingno
                            //placeforthenextgrouponthesameline.
                            '<groupclass="top_group">'+
                                '<divstyle="height:200px;"/>'+
                            '</group>'+
                            '<newline/>'+
                            '<groupclass="bottom_group">'+
                                '<div/>'+
                            '</group>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        //Innergroup
        assert.containsN(form,'.main_inner_group>tbody>tr',2,
            "thereshouldbe2rowsinthegroup");
        assert.containsOnce(form,'.main_inner_group>tbody>tr:first>.o_td_label',
            "thereshouldbeonlyonelabelinthefirstrow");
        assert.containsOnce(form,'.main_inner_group>tbody>tr:first.o_field_widget',
            "thereshouldbeonlyonewidgetinthefirstrow");
        assert.containsN(form,'.main_inner_group>tbody>tr:last>.o_td_label',2,
            "thereshouldbetwolabelsinthesecondrow");
        assert.containsN(form,'.main_inner_group>tbody>tr:last.o_field_widget',2,
            "thereshouldbetwowidgetsinthesecondrow");

        //Outergroup
        assert.ok((form.$('.bottom_group').position().top-form.$('.top_group').position().top)>=200,
            "outergroupchildrenshouldnotbeonthesameline");

        form.destroy();
    });

    QUnit.test('customopenrecorddialogtitle',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].p=[2];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p"widget="many2many"string="customlabel">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                        '<form>'+
                            '<fieldname="display_name"/>'+
                        '</form>'+
                    '</field>'+
                '</form>',
            session:{},
            res_id:1,
        });

        awaittestUtils.dom.click(form.$('.o_data_row:first'));
        assert.strictEqual($('.modal.modal-title').first().text().trim(),'Open:customlabel',
            "modalshouldusethepythonfieldstringastitle");

        form.destroy();
    });

    QUnit.test('displaytranslationalert',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.foo.translate=true;
        this.data.partner.fields.display_name.translate=true;

        varmulti_lang=_t.database.multi_lang;
        _t.database.multi_lang=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="display_name"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"test");
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.o_form_view.alert>div.oe_field_translate',
                            "shouldhavesingletranslationalert");

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name="display_name"]'),"test2");
        awaittestUtils.form.clickSave(form);
        assert.containsN(form,'.o_form_view.alert>div.oe_field_translate',2,
                         "shouldhavetwotranslatefieldsintranslationalert");

        form.destroy();

        _t.database.multi_lang=multi_lang;
    });

    QUnit.test('translationalertsarepreservedonpagerchange',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.foo.translate=true;

        varmulti_lang=_t.database.multi_lang;
        _t.database.multi_lang=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="foo"/>'+
                    '</sheet>'+
                '</form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"test");
        awaittestUtils.form.clickSave(form);

        assert.containsOnce(form,'.o_form_view.alert>div',"shouldhaveatranslationalert");

        //clickonthepagertoswitchtothenextrecord
        awaitcpHelpers.pagerNext(form);
        assert.containsNone(form,'.o_form_view.alert>div',"shouldnothaveatranslationalert");

        //clickonthepagertoswitchbacktothepreviousrecord
        awaitcpHelpers.pagerPrevious(form);
        assert.containsOnce(form,'.o_form_view.alert>div',"shouldhaveatranslationalert");

        //removetranslationalertbyclickXandcheckalertevenafterformreload
        awaittestUtils.dom.click(form.$('.o_form_view.alert>.close'));
        assert.containsNone(form,'.o_form_view.alert>div',"shouldnothaveatranslationalert");

        awaitform.reload();
        assert.containsNone(form,'.o_form_view.alert>div',"shouldnothaveatranslationalertafterreload");

        form.destroy();
        _t.database.multi_lang=multi_lang;
    });

    QUnit.test('translationalertspresevedonreversebreadcrumb',asyncfunction(assert){
        assert.expect(2);

        this.data['ir.translation']={
            fields:{
                name:{string:"name",type:"char"},
                source:{string:"Source",type:"char"},
                value:{string:"Value",type:"char"},
            },
            records:[],
        };

        this.data.partner.fields.foo.translate=true;

        varmulti_lang=_t.database.multi_lang;
        _t.database.multi_lang=true;

        vararchs={
            'partner,false,form':'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="foo"/>'+
                    '</sheet>'+
                '</form>',
            'partner,false,search':'<search></search>',
            'ir.translation,false,list':'<tree>'+
                        '<fieldname="name"/>'+
                        '<fieldname="source"/>'+
                        '<fieldname="value"/>'+
                    '</tree>',
            'ir.translation,false,search':'<search></search>',
        };

        varactions=[{
            id:1,
            name:'Partner',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'form']],
        },{
            id:2,
            name:'Translate',
            res_model:'ir.translation',
            type:'ir.actions.act_window',
            views:[[false,'list']],
            target:'current',
            flags:{'search_view':true,'action_buttons':true},
        }];

        varactionManager=awaitcreateActionManager({
            actions:actions,
            archs:archs,
            data:this.data,
        });

        awaitactionManager.doAction(1);
        actionManager.$('input[name="foo"]').val("test").trigger("input");
        awaittestUtils.dom.click(actionManager.$('.o_form_button_save'));

        assert.strictEqual(actionManager.$('.o_form_view.alert>div').length,1,
            "shouldhaveatranslationalert");

        varcurrentController=actionManager.getCurrentController().widget;
        awaitactionManager.doAction(2,{
            on_reverse_breadcrumb:function(){
                if(!_.isEmpty(currentController.renderer.alertFields)){
                    currentController.renderer.displayTranslationAlert();
                }
                returnfalse;
            },
        });

        awaittestUtils.dom.click($('.o_control_panel.breadcrumba:first'));
        assert.strictEqual(actionManager.$('.o_form_view.alert>div').length,1,
            "shouldhaveatranslationalert");

        actionManager.destroy();
        _t.database.multi_lang=multi_lang;
    });

    QUnit.test('translateeventcorrectlyhandledwithmultiplecontrollers',asyncfunction(assert){
        assert.expect(3);

        this.data.product.fields.name.translate=true;
        this.data.partner.records[0].product_id=37;
        varnbTranslateCalls=0;

        varmulti_lang=_t.database.multi_lang;
        _t.database.multi_lang=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_id"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'product,false,form':'<form>'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="name"/>'+
                                '<fieldname="partner_type_id"/>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
            },
            res_id:1,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/product/get_formview_id'){
                    returnPromise.resolve(false);
                }
                if(route==="/web/dataset/call_button"&&args.method==='translate_fields'){
                    assert.deepEqual(args.args,["product",37,"name"],'shouldcall"call_button"route');
                    nbTranslateCalls++;
                    returnPromise.resolve({
                        domain:[],
                        context:{search_default_name:'partnes,foo'},
                    });
                }
                if(route==="/web/dataset/call_kw/res.lang/get_installed"){
                    returnPromise.resolve([["en_US"],["fr_BE"]]);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('[name="product_id"].o_external_button'));
        assert.containsOnce($('.modal-body'),'span.o_field_translate',
            "thereshouldbeatranslatebuttoninthemodal");

        awaittestUtils.dom.click($('.modal-bodyspan.o_field_translate'));
        assert.strictEqual(nbTranslateCalls,1,"shouldcall_buttontranslateonce");

        form.destroy();
        _t.database.multi_lang=multi_lang;
    });

    QUnit.test('buttonsaredisableduntilstatusbaractionisresolved',asyncfunction(assert){
        assert.expect(9);

        vardef=testUtils.makeTestPromise();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"/>'+
                        '<buttonname="some_method"class="s"string="Doit"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<divname="button_box"class="oe_button_box">'+
                            '<buttonclass="oe_stat_button">'+
                                '<fieldname="bar"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            intercepts:{
                execute_action:function(event){
                    returndef.then(function(){
                        event.data.on_success();
                    });
                }
            },
        });

        assert.strictEqual(form.$buttons.find('button:not(:disabled)').length,4,
            "controlpanelbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.o_form_statusbarbutton:not(:disabled)').length,2,
            "statusbarbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.oe_button_boxbutton:not(:disabled)').length,1,
            "statbuttonsshouldbeenabled");

        awaittestUtils.dom.clickFirst(form.$('.o_form_statusbarbutton'));

        //Theunresolvedpromiseletsuscheckthestateofthebuttons
        assert.strictEqual(form.$buttons.find('button:disabled').length,4,
            "controlpanelbuttonsshouldbedisabled");
        assert.containsN(form,'.o_form_statusbarbutton:disabled',2,
            "statusbarbuttonsshouldbedisabled");
        assert.containsOnce(form,'.oe_button_boxbutton:disabled',
            "statbuttonsshouldbedisabled");

        def.resolve();
        awaittestUtils.nextTick();
        assert.strictEqual(form.$buttons.find('button:not(:disabled)').length,4,
            "controlpanelbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.o_form_statusbarbutton:not(:disabled)').length,2,
            "statusbarbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.oe_button_boxbutton:not(:disabled)').length,1,
            "statbuttonsshouldbeenabled");

        form.destroy();
    });

    QUnit.test('buttonsaredisableduntilbuttonboxactionisresolved',asyncfunction(assert){
        assert.expect(9);

        vardef=testUtils.makeTestPromise();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"/>'+
                        '<buttonname="some_method"class="s"string="Doit"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<divname="button_box"class="oe_button_box">'+
                            '<buttonclass="oe_stat_button">'+
                                '<fieldname="bar"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            intercepts:{
                execute_action:function(event){
                    returndef.then(function(){
                        event.data.on_success();
                    });
                }
            },
        });

        assert.strictEqual(form.$buttons.find('button:not(:disabled)').length,4,
            "controlpanelbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.o_form_statusbarbutton:not(:disabled)').length,2,
            "statusbarbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.oe_button_boxbutton:not(:disabled)').length,1,
            "statbuttonsshouldbeenabled");

        awaittestUtils.dom.click(form.$('.oe_button_boxbutton'));

        //Theunresolvedpromiseletsuscheckthestateofthebuttons
        assert.strictEqual(form.$buttons.find('button:disabled').length,4,
            "controlpanelbuttonsshouldbedisabled");
        assert.containsN(form,'.o_form_statusbarbutton:disabled',2,
            "statusbarbuttonsshouldbedisabled");
        assert.containsOnce(form,'.oe_button_boxbutton:disabled',
            "statbuttonsshouldbedisabled");

        def.resolve();
        awaittestUtils.nextTick();
        assert.strictEqual(form.$buttons.find('button:not(:disabled)').length,4,
            "controlpanelbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.o_form_statusbarbutton:not(:disabled)').length,2,
            "statusbarbuttonsshouldbeenabled");
        assert.strictEqual(form.$('.oe_button_boxbutton:not(:disabled)').length,1,
            "statbuttonsshouldbeenabled");

        form.destroy();
    });

    QUnit.test('buttonswith"confirm"attributesavebeforecallingthemethod',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="post"class="p"string="Confirm"type="object"'+
                            'confirm="Verydangerous.Usure?"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<fieldname="foo"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                execute_action:function(event){
                    assert.step('execute_action');
                    event.data.on_success();
                },
            },
        });

        //clickonbutton,andcancelinconfirmdialog
        awaittestUtils.dom.click(form.$('.o_statusbar_buttonsbutton'));
        assert.ok(form.$('.o_statusbar_buttonsbutton').prop('disabled'),
            'buttonshouldbedisabled');
        awaittestUtils.dom.click($('.modal-footerbutton.btn-secondary'));
        assert.ok(!form.$('.o_statusbar_buttonsbutton').prop('disabled'),
            'buttonshouldnolongerbedisabled');

        assert.verifySteps(['onchange']);

        //clickonbutton,andclickonokinconfirmdialog
        awaittestUtils.dom.click(form.$('.o_statusbar_buttonsbutton'));
        assert.verifySteps([]);
        awaittestUtils.dom.click($('.modal-footerbutton.btn-primary'));
        assert.verifySteps(['create','read','execute_action']);

        form.destroy();
    });

    QUnit.test('buttonswith"confirm"attribute:clicktwiceon"Ok"',asyncfunction(assert){
        assert.expect(7);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <header>
                        <buttonname="post"class="p"string="Confirm"type="object"confirm="Usure?"/>
                    </header>
                </form>`,
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                execute_action:function(event){
                    assert.step('execute_action');//shouldbecalledonlyonce
                    event.data.on_success();
                },
            },
        });

        assert.verifySteps(["onchange"]);

        awaittestUtils.dom.click(form.$('.o_statusbar_buttonsbutton'));
        assert.verifySteps([]);

        testUtils.dom.click($('.modal-footerbutton.btn-primary'));
        awaitPromise.resolve();
        awaittestUtils.dom.click($('.modal-footerbutton.btn-primary'));
        assert.verifySteps(['create','read','execute_action']);

        form.destroy();
    });

    QUnit.test('buttonsaredisableduntilactionisresolved(indialogs)',asyncfunction(assert){
        assert.expect(3);

        vardef=testUtils.makeTestPromise();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="trululu"/>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner,false,form':'<form>'+
                        '<sheet>'+
                            '<divname="button_box"class="oe_button_box">'+
                                '<buttonclass="oe_stat_button">'+
                                    '<fieldname="bar"/>'+
                                '</button>'+
                            '</div>'+
                            '<group>'+
                                '<fieldname="foo"/>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
            },
            res_id:1,
            intercepts:{
                execute_action:function(event){
                    returndef.then(function(){
                        event.data.on_success();
                    });
                }
            },
            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.dom.click(form.$('.o_external_button'));

        assert.notOk($('.modal.oe_button_boxbutton').attr('disabled'),
            "statbuttonsshouldbeenabled");

        awaittestUtils.dom.click($('.modal.oe_button_boxbutton'));

        assert.ok($('.modal.oe_button_boxbutton').attr('disabled'),
            "statbuttonsshouldbedisabled");

        def.resolve();
        awaittestUtils.nextTick();
        assert.notOk($('.modal.oe_button_boxbutton').attr('disabled'),
            "statbuttonsshouldbeenabled");

        form.destroy();
    });

    QUnit.test('multipleclicksonsaveshouldreloadonlyonce',asyncfunction(assert){
        assert.expect(5);

        vardef=testUtils.makeTestPromise();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                assert.step(args.method);
                if(args.method==="write"){
                    returndef.then(function(){
                        returnresult;
                    });
                }else{
                    returnresult;
                }
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"test");
        awaittestUtils.form.clickSave(form);
        assert.ok(form.$buttons.find('.o_form_button_save').get(0).disabled);

        def.resolve();
        awaittestUtils.nextTick();
        assert.verifySteps([
            'read',//initialreadtorendertheview
            'write',//writeonsave
            'read'//readonreload
        ]);

        form.destroy();
    });

    QUnit.test('formviewisnotbrokenifsaveoperationfails',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                assert.step(args.method);
                if(args.method==='write'&&args.args[1].foo==='incorrectvalue'){
                    returnPromise.reject();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"incorrectvalue");
        awaittestUtils.form.clickSave(form);

        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"correctvalue");

        awaittestUtils.form.clickSave(form);

        assert.verifySteps([
            'read',//initialreadtorendertheview
            'write',//writeonsave(itfails,doesnottriggeraread)
            'write',//writeonsave(itworks)
            'read'//readonreload
        ]);

        form.destroy();
    });

    QUnit.test('formviewisnotbrokenifsavefailedinreadonlymodeonfieldchanged',asyncfunction(assert){
        assert.expect(10);

        varfailFlag=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<header><fieldname="trululu"widget="statusbar"clickable="true"/></header>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.step('write');
                    if(failFlag){
                        returnPromise.reject();
                    }
                }elseif(args.method==='read'){
                    assert.step('read');
                }
                returnthis._super.apply(this,arguments);
            },
        });

        var$selectedState=form.$('.o_statusbar_statusbutton[data-value="4"]');
        assert.ok($selectedState.hasClass('btn-primary')&&$selectedState.hasClass('disabled'),
            "selectedstatusshouldbebtn-primaryanddisabled");

        failFlag=true;
        var$clickableState=form.$('.o_statusbar_statusbutton[data-value="1"]');
        awaittestUtils.dom.click($clickableState);

        var$lastActiveState=form.$('.o_statusbar_statusbutton[data-value="4"]');
        $selectedState=form.$('.o_statusbar_statusbutton.btn-primary');
        assert.strictEqual($selectedState[0],$lastActiveState[0],
            "selectedstatusisAAArecordaftersavefail");

        failFlag=false;
        $clickableState=form.$('.o_statusbar_statusbutton[data-value="1"]');
        awaittestUtils.dom.click($clickableState);

        var$lastClickedState=form.$('.o_statusbar_statusbutton[data-value="1"]');
        $selectedState=form.$('.o_statusbar_statusbutton.btn-primary');
        assert.strictEqual($selectedState[0],$lastClickedState[0],
            "lastclickedstatusshouldbeactive");

        assert.verifySteps([
            'read',
            'write',//fails
            'read',//mustreloadwhensavingfails
            'write',//works
            'read',//mustreloadwhensavingworks
            'read',//fixme:thisreadshouldnotbenecessary
        ]);

        form.destroy();
    });

    QUnit.test('supportpasswordattribute',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"password="True"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('span[name="foo"]').text(),'***',
            "passwordshouldbedisplayedwithstars");
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name="foo"]').val(),'yop',
            "inputvalueshouldbethepassword");
        assert.strictEqual(form.$('input[name="foo"]').prop('type'),'password',
            "inputshouldbeoftypepassword");
        form.destroy();
    });

    QUnit.test('supportautocompleteattribute',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="display_name"autocomplete="coucou"/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.hasAttrValue(form.$('input[name="display_name"]'),'autocomplete','coucou',
            "attributeautocompleteshouldbeset");
        form.destroy();
    });

    QUnit.test('inputautocompleteattributesettononebydefault',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="display_name"/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.hasAttrValue(form.$('input[name="display_name"]'),'autocomplete','off',
            "attributeautocompleteshouldbesettononebydefault");
        form.destroy();
    });

    QUnit.test('contextiscorrectlypassedaftersave&newinFormViewDialog',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:4,
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_ids"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'product,false,form':
                    '<formstring="Products">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="partner_type_id"'+
                                    'context="{\'color\':parent.id}"/>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
                'product,false,list':'<tree><fieldname="display_name"/></tree>'
            },
            mockRPC:function(route,args){
                if(args.method==='name_search'){
                    assert.strictEqual(args.kwargs.context.color,4,
                        "shouldusethecorrectcontext");
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.nextTick();
        assert.strictEqual($('.modal').length,1,
            "OneFormViewDialogshouldbeopened");
        //setavalueonthem2o
        awaittestUtils.fields.many2one.clickOpenDropdown('partner_type_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('partner_type_id');

        awaittestUtils.dom.click($('.modal-footerbutton:eq(1)'));
        awaittestUtils.nextTick();
        awaittestUtils.dom.click($('.modal.o_field_many2oneinput'));
        awaittestUtils.fields.many2one.clickHighlightedItem('partner_type_id');
        awaittestUtils.dom.click($('.modal-footerbutton:first'));
        awaittestUtils.nextTick();
        form.destroy();
    });

    QUnit.test('renderdomainfieldwidgetwithoutmodel',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.fields.model_name={string:"Modelname",type:"char"};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group>'+
                        '<fieldname="model_name"/>'+
                        '<fieldname="display_name"widget="domain"options="{\'model\':\'model_name\'}"/>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='search_count'){
                    assert.strictEqual(args.model,'test',
                        "shouldsearch_countontest");
                    if(!args.kwargs.domain){
                        returnPromise.reject({message:{
                            code:200,
                            data:{},
                            message:"MockServer._getRecords:givendomainhastobeanarray.",
                        },event:$.Event()});
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name="display_name"]').text(),"Selectamodeltoaddafilter.",
            "shouldcontainanerrormessagesayingthemodelismissing");
        awaittestUtils.fields.editInput(form.$('input[name="model_name"]'),"test");
        assert.notStrictEqual(form.$('.o_field_widget[name="display_name"]').text(),"Selectamodeltoaddafilter.",
            "shouldnotcontainanerrormessageanymore");
        form.destroy();
    });

    QUnit.test('readonlyfieldsarenotsentwhensaving',asyncfunction(assert){
        assert.expect(6);

        //defineanonchangeondisplay_nametocheckthatthevalueofreadonly
        //fieldsiscorrectlysentforonchanges
        this.data.partner.onchanges={
            display_name:function(){},
            p:function(){},
        };
        varcheckOnchange=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                        '<formstring="Partners">'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="foo"attrs="{\'readonly\':[[\'display_name\',\'=\',\'readonly\']]}"/>'+
                        '</form>'+
                    '</field>'+
                '</form>',
            mockRPC:function(route,args){
                if(checkOnchange&&args.method==='onchange'){
                    if(args.args[2]==='display_name'){//onchangeonfielddisplay_name
                        assert.strictEqual(args.args[1].foo,'foovalue',
                            "readonlyfieldsvalueshouldbesentforonchanges");
                    }else{//onchangeonfieldp
                        assert.deepEqual(args.args[1].p,[
                            [0,args.args[1].p[0][1],{display_name:'readonly',foo:'foovalue'}]
                        ],"readonlyfieldsvalueshouldbesentforonchanges");
                    }
                }
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{
                        p:[[0,args.args[0].p[0][1],{display_name:'readonly'}]]
                    },"shouldnothavesentthevalueofthereadonlyfield");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.nextTick();
        assert.strictEqual($('.modalinput.o_field_widget[name=foo]').length,1,
        'fooshouldbeeditable');
        checkOnchange=true;
        awaittestUtils.fields.editInput($('.modal.o_field_widget[name=foo]'),'foovalue');
        awaittestUtils.fields.editInput($('.modal.o_field_widget[name=display_name]'),'readonly');
        assert.strictEqual($('.modalspan.o_field_widget[name=foo]').length,1,
        'fooshouldbereadonly');
        awaittestUtils.dom.clickFirst($('.modal-footer.btn-primary'));
        awaittestUtils.nextTick();
        checkOnchange=false;

        awaittestUtils.dom.click(form.$('.o_data_row'));
        assert.strictEqual($('.modal.o_field_widget[name=foo]').text(),'foovalue',
        "theeditedvalueshouldhavebeenkept");
        awaittestUtils.dom.clickFirst($('.modal-footer.btn-primary'));
        awaittestUtils.nextTick();

        awaittestUtils.form.clickSave(form);//savetherecord
        form.destroy();
    });

    QUnit.test('idisFalseinevalContextfornewrecords',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="id"/>'+
                        '<fieldname="foo"attrs="{\'readonly\':[[\'id\',\'=\',False]]}"/>'+
                '</form>',
        });

        assert.hasClass(form.$('.o_field_widget[name=foo]'),'o_readonly_modifier',
            "fooshouldbereadonlyin'Create'mode");

        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);

        assert.doesNotHaveClass(form.$('.o_field_widget[name=foo]'),'o_readonly_modifier',
            "fooshouldnotbereadonlyanymore");

        form.destroy();
    });

    QUnit.test('deleteaduplicatedrecord',asyncfunction(assert){
        assert.expect(5);

        varnewRecordID;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="display_name"/>'+
                '</form>',
            res_id:1,
            viewOptions:{hasActionMenus:true},
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='copy'){
                    returnresult.then(function(id){
                        newRecordID=id;
                        returnid;
                    });
                }
                if(args.method==='unlink'){
                    assert.deepEqual(args.args[0],[newRecordID],
                        "shoulddeletethenewlycreatedrecord");
                }
                returnresult;
            },
        });

        //duplicaterecord1
        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Duplicate");

        assert.containsOnce(form,'.o_form_editable',
            "formshouldbeineditmode");
        assert.strictEqual(form.$('.o_field_widget').val(),'firstrecord(copy)',
            "duplicatedrecordshouldhavecorrectname");
        awaittestUtils.form.clickSave(form);//saveduplicatedrecord

        //deleteduplicatedrecord
        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Delete");

        assert.strictEqual($('.modal').length,1,"shouldhaveopenedaconfirmdialog");
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        assert.strictEqual(form.$('.o_field_widget').text(),'firstrecord',
            "shouldhavecomebacktopreviousrecord");

        form.destroy();
    });

    QUnit.test('displaytooltipsforbuttons',asyncfunction(assert){
        assert.expect(2);

        varinitialDebugMode=flectra.debug;
        flectra.debug=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="some_method"class="oe_highlight"string="Button"type="object"/>'+
                    '</header>'+
                    '<buttonname="other_method"class="oe_highlight"string="Button2"type="object"/>'+
                '</form>',
        });

        var$button=form.$('.o_form_statusbarbutton');
        $button.tooltip('show',false);
        $button.trigger($.Event('mouseenter'));

        assert.strictEqual($('.tooltip.oe_tooltip_string').length,1,
            "shouldhaverenderedatooltip");
        $button.trigger($.Event('mouseleave'));

        var$secondButton=form.$('button[name="other_method"]');
        $secondButton.tooltip('show',false);
        $secondButton.trigger($.Event('mouseenter'));

        assert.strictEqual($('.tooltip.oe_tooltip_string').length,1,
            "shouldhaverenderedatooltip");
        $secondButton.trigger($.Event('mouseleave'));

        flectra.debug=initialDebugMode;
        form.destroy();
    });

    QUnit.test('reloadeventishandledonlyonce',asyncfunction(assert){
        //Inthistest,severalformcontrollersarenested(twoofthemare
        //openedindialogs).Whentheusersclicksonsaveinthelast
        //openeddialog,a'reload'eventistriggereduptoreloadthe(direct)
        //parentview.Ifthiseventisn'tstopPropagatedbythefirstcontroller
        //catchingit,itwillcrashwhentheotheronewilltrytohandleit,
        //asthisonedoesn'tknowatallthedataPointIDtoreload.
        assert.expect(11);

        vararch='<form>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="trululu"/>'+
                    '</form>';
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:arch,
            archs:{
                'partner,false,form':arch,
            },
            res_id:2,
            mockRPC:function(route,args){
                assert.step(args.method);
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.dom.click(form.$('.o_external_button'));
        awaittestUtils.dom.click($('.modal.o_external_button'));

        awaittestUtils.fields.editInput($('.modal:nth(1).o_field_widget[name=display_name]'),'newname');
        awaittestUtils.dom.click($('.modal:nth(1)footer.btn-primary').first());

        assert.strictEqual($('.modal.o_field_widget[name=trululu]input').val(),'newname',
            "recordshouldhavebeenreloaded");
        assert.verifySteps([
            "read",//mainrecord
            "get_formview_id",//idoffirstformviewopenedinadialog
            "load_views",//archoffirstformviewopenedinadialog
            "read",//firstdialog
            "get_formview_id",//idofsecondformviewopenedinadialog
            "load_views",//archofsecondformviewopenedinadialog
            "read",//seconddialog
            "write",//saveseconddialog
            "read",//reloadfirstdialog
        ]);

        form.destroy();
    });

    QUnit.test('processthecontextforinlinesubview',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].p=[2];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="bar"invisible="context.get(\'hide_bar\',False)"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            viewOptions:{
                context:{hide_bar:true},
            },
        });
        assert.containsOnce(form,'.o_list_viewtheadtrth',
            "thereshouldbeonlyonecolumn");
        form.destroy();
    });

    QUnit.test('processthecontextforsubviewnotinline',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].p=[2];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p"/>'+
                '</form>',
            archs:{
                "partner,false,list":'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"invisible="context.get(\'hide_bar\',False)"/>'+
                '</tree>',
            },
            res_id:1,
            viewOptions:{
                context:{hide_bar:true},
            },
        });
        assert.containsOnce(form,'.o_list_viewtheadtrth',
            "thereshouldbeonlyonecolumn");
        form.destroy();
    });

    QUnit.test('cantogglecolumninx2manyinsubformview',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[2].p=[1,2];
        this.data.partner.fields.foo.sortable=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="trululu"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super.apply(this,arguments);
            },
            archs:{
                'partner,false,form':'<formstring="Partners">'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="foo"/>'+
                            '</tree>'+
                        '</field>'+
                    '</form>',
            },
            viewOptions:{mode:'edit'},
        });
        awaittestUtils.dom.click(form.$('.o_external_button'));
        assert.strictEqual($('.modal-body.o_form_view.o_list_view.o_data_cell').text(),"yopblip",
            "tablehassomeinitialorder");

        awaittestUtils.dom.click($('.modal-body.o_form_view.o_list_viewth.o_column_sortable'));
        assert.strictEqual($('.modal-body.o_form_view.o_list_view.o_data_cell').text(),"blipyop",
            "tableisnowsorted");
        form.destroy();
    });

    QUnit.test('rainbowmanattributescorrectlypassedonbuttonclick',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<buttonname="action_won"string="Won"type="object"effect="{\'message\':\'Congrats!\'}"/>'+
                    '</header>'+
                '</form>',
            intercepts:{
                execute_action:function(event){
                    vareffectDescription=pyUtils.py_eval(event.data.action_data.effect);
                    assert.deepEqual(effectDescription,{message:'Congrats!'},"shouldhavecorrecteffectdescription");
                }
            },
        });

        awaittestUtils.dom.click(form.$('.o_form_statusbar.btn-secondary'));
        form.destroy();
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

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<widgetname="test"/>'+
                '</form>',
        });

        assert.strictEqual(form.$('.o_widget').text(),'{"foo":"MylittleFooValue","bar":false}',
            "widgetshouldhavebeeninstantiated");

        form.destroy();
        deletewidgetRegistry.map.test;
    });

    QUnit.test('attachdocumentwidgetcallsactionwithattachmentids',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='my_action'){
                    assert.deepEqual(args.kwargs.attachment_ids,[5,2]);
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            arch:'<form>'+
                    '<widgetname="attach_document"action="my_action"/>'+
                '</form>',
        });

        varonFileLoadedEventName=form.$('.o_form_binary_form').attr('target');
        //trigger_onFileLoadedfunction
        $(window).trigger(onFileLoadedEventName,[{id:5},{id:2}]);

        form.destroy();
    });

    QUnit.test('supportheaderbuttonaswidgetsonformstatusbar',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header>'+
                        '<widgetname="attach_document"string="Attachdocument"/>'+
                    '</header>'+
                '</form>',
        });

        assert.containsOnce(form,'button.o_attachment_button',
            "shouldhave1attach_documentwidgetinthestatusbar");
        assert.strictEqual(form.$('span.o_attach_document').text().trim(),'Attachdocument',
            "widgetshouldhavebeeninstantiated");

        form.destroy();
    });

    QUnit.test('basicsupportforwidgets',asyncfunction(assert){
        assert.expect(1);

        varMyWidget=Widget.extend({
            init:function(parent,dataPoint){
                this.data=dataPoint.data;
            },
            start:function(){
                this.$el.text(this.data.foo+"!");
            },
            updateState:function(dataPoint){
                this.$el.text(dataPoint.data.foo+"!");
            },
        });
        widgetRegistry.add('test',MyWidget);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<widgetname="test"/>'+
                '</form>',
        });

        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"Iamalive");
        assert.strictEqual(form.$('.o_widget').text(),'Iamalive!',
            "widgetshouldhavebeenupdated");

        form.destroy();
        deletewidgetRegistry.map.test;
    });

    QUnit.test('bounceeditbuttoninreadonlymode',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<divclass="oe_title">'+
                        '<fieldname="display_name"/>'+
                    '</div>'+
                '</form>',
            res_id:1,
        });

        //inreadonly
        awaittestUtils.dom.click(form.$('[name="display_name"]'));
        assert.hasClass(form.$('.o_form_button_edit'),'o_catch_attention');

        //inedit
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('[name="display_name"]'));
        //awaittestUtils.nextTick();
        assert.containsNone(form,'button.o_catch_attention:visible');

        form.destroy();
    });

    QUnit.test('properstringificationindebugmodetooltip',asyncfunction(assert){
        assert.expect(6);

        varinitialDebugMode=flectra.debug;
        flectra.debug=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="product_id"context="{\'lang\':\'en_US\'}"'+
                            'attrs=\'{"invisible":[["product_id","=",33]]}\''+
                            'widget="many2one"/>'+
                    '</sheet>'+
                '</form>',
        });

        var$field=form.$('[name="product_id"]');
        $field.tooltip('show',true);
        $field.trigger($.Event('mouseenter'));
        assert.strictEqual($('.oe_tooltip_technical>li[data-item="context"]').length,
            1,'contextshouldbepresentforthisfield');
        assert.strictEqual($('.oe_tooltip_technical>li[data-item="context"]')[0].lastChild.wholeText.trim(),
            "{'lang':'en_US'}","contextshouldbeproperlystringified");

        assert.strictEqual($('.oe_tooltip_technical>li[data-item="modifiers"]').length,
            1,'modifiersshouldbepresentforthisfield');
        assert.strictEqual($('.oe_tooltip_technical>li[data-item="modifiers"]')[0].lastChild.wholeText.trim(),
            '{"invisible":[["product_id","=",33]]}',"modifiersshouldbeproperlystringified");

        assert.strictEqual($('.oe_tooltip_technical>li[data-item="widget"]').length,
            1,'widgetshouldbepresentforthisfield');
        assert.strictEqual($('.oe_tooltip_technical>li[data-item="widget"]')[0].lastChild.wholeText.trim(),
            'Many2one(many2one)',"widgetdescriptionshouldbecorrect");

        flectra.debug=initialDebugMode;
        form.destroy();
    });

    QUnit.test('autoresizeoftextfieldsisdonewhenswitchingtoeditmode',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.text_field={string:'Textfield',type:'text'};
        this.data.partner.fields.text_field.default="some\n\nmulti\n\nline\n\ntext\n";
        this.data.partner.records[0].text_field="a\nb\nc\nd\ne\nf";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="text_field"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        //switchtoeditmodetoensurethatautoresizeiscorrectlydone
        awaittestUtils.form.clickEdit(form);
        varheight=form.$('.o_field_widget[name=text_field]').height();
        //focusthefieldtomanuallytriggerautoresize
        form.$('.o_field_widget[name=text_field]').trigger('focus');
        assert.strictEqual(form.$('.o_field_widget[name=text_field]').height(),height,
            "autoresizeshouldhavebeendoneautomaticallyatrendering");
        //nextassertsimplytriestoensurethatthetextareaisn'tstuckedto
        //itsminimalsize,evenafterbeingfocused
        assert.ok(height>80,"textareashouldhaveanheightofatleast80px");

        //saveandcreateanewrecordtoensurethatautoresizeiscorrectlydone
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickCreate(form);
        height=form.$('.o_field_widget[name=text_field]').height();
        //focusthefieldtomanuallytriggerautoresize
        form.$('.o_field_widget[name=text_field]').trigger('focus');
        assert.strictEqual(form.$('.o_field_widget[name=text_field]').height(),height,
            "autoresizeshouldhavebeendoneautomaticallyatrendering");
        assert.ok(height>80,"textareashouldhaveanheightofatleast80px");

        form.destroy();
    });

    QUnit.test('autoresizeoftextfieldsisdoneonnotebookpageshow',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.text_field={string:'Textfield',type:'text'};
        this.data.partner.fields.text_field.default="some\n\nmulti\n\nline\n\ntext\n";
        this.data.partner.records[0].text_field="a\nb\nc\nd\ne\nf";
        this.data.partner.fields.text_field_empty={string:'Textfield',type:'text'};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<notebook>'+
                            '<pagestring="FirstPage">'+
                                '<fieldname="foo"/>'+
                            '</page>'+
                            '<pagestring="SecondPage">'+
                                '<fieldname="text_field"/>'+
                            '</page>'+
                            '<pagestring="ThirdPage">'+
                                '<fieldname="text_field_empty"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.hasClass(form.$('.o_notebook.nav.nav-link:first()'),'active');

        awaittestUtils.dom.click(form.$('.o_notebook.nav.nav-link:nth(1)'));
        assert.hasClass(form.$('.o_notebook.nav.nav-link:nth(1)'),'active');

        varheight=form.$('.o_field_widget[name=text_field]').height();
        assert.ok(height>80,"textareashouldhaveanheightofatleast80px");

        awaittestUtils.dom.click(form.$('.o_notebook.nav.nav-link:nth(2)'));
        assert.hasClass(form.$('.o_notebook.nav.nav-link:nth(2)'),'active');

        varheight=form.$('.o_field_widget[name=text_field_empty]').css('height');
        assert.strictEqual(height,'50px',"emptytextareashouldhaveheightof50px");

        form.destroy();
    });

    QUnit.test('checkiftheviewdestroysallwidgetsandinstances',asyncfunction(assert){
        assert.expect(2);

        varinstanceNumber=0;
        awaittestUtils.mock.patch(mixins.ParentedMixin,{
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
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="bar"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="qux"/>'+
                        '<fieldname="trululu"/>'+
                        '<fieldname="timmy"/>'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="priority"/>'+
                        '<fieldname="state"/>'+
                        '<fieldname="date"/>'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="product_ids"/>'+
                        '<fieldname="p">'+
                            '<treedefault_order="foodesc">'+
                                '<fieldname="display_name"/>'+
                                '<fieldname="foo"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner,false,form':
                    '<formstring="Partner">'+
                        '<sheet>'+
                            '<group>'+
                                '<fieldname="foo"/>'+
                            '</group>'+
                        '</sheet>'+
                    '</form>',
                "partner_type,false,list":'<tree><fieldname="name"/></tree>',
                'product,false,list':'<tree><fieldname="display_name"/></tree>',

            },
            res_id:1,
        };

        varform=awaitcreateView(params);
        assert.ok(instanceNumber>0);

        form.destroy();
        assert.strictEqual(instanceNumber,0);

        awaittestUtils.mock.unpatch(mixins.ParentedMixin);
    });

    QUnit.test('donotchangepagerwhendiscardingcurrentrecord',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            viewOptions:{
                ids:[1,2],
                index:0,
            },
            res_id:2,
        });

        assert.strictEqual(cpHelpers.getPagerValue(form),"2",
            'pagershouldindicatethatweareonsecondrecord');
        assert.strictEqual(cpHelpers.getPagerSize(form),"2",
            'pagershouldindicatethatweareonsecondrecord');

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.form.clickDiscard(form);

        assert.strictEqual(cpHelpers.getPagerValue(form),"2",
            'pagervalueshouldnothavechanged');
        assert.strictEqual(cpHelpers.getPagerSize(form),"2",
            'pagerlimitshouldnothavechanged');

        form.destroy();
    });

    QUnit.test('Formviewfromordered,groupedlistviewcorrectcontext',asyncfunction(assert){
        assert.expect(10);
        this.data.partner.records[0].timmy=[12];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="timmy"/>'+
                '</form>',
            archs:{
                'partner_type,false,list':
                    '<tree>'+
                        '<fieldname="name"/>'+
                    '</tree>',
            },
            viewOptions:{
                //Simulatescomingfromalistviewwithagroupbyandfilter
                context:{
                    orderedBy:[{name:'foo',asc:true}],
                    group_by:['foo'],
                }
            },
            res_id:1,
            mockRPC:function(route,args){
                assert.step(args.model+":"+args.method);
                if(args.method==='read'){
                    assert.ok(args.kwargs.context,'contextispresent');
                    assert.notOk('orderedBy'inargs.kwargs.context,
                        'orderedBynotincontext');
                    assert.notOk('group_by'inargs.kwargs.context,
                        'group_bynotincontext');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.verifySteps(['partner_type:load_views','partner:read','partner_type:read']);

        form.destroy();
    });

    QUnit.test('editioninformviewona"noCache"model',asyncfunction(assert){
        assert.expect(5);

        awaittestUtils.mock.patch(BasicModel,{
            noCacheModels:BasicModel.prototype.noCacheModels.concat(['partner']),
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="display_name"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.step('write');
                }
                returnthis._super.apply(this,arguments);
            },
        });
        core.bus.on('clear_cache',form,assert.step.bind(assert,'clear_cache'));

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'newvalue');
        awaittestUtils.form.clickSave(form);

        assert.verifySteps(['write','clear_cache']);

        form.destroy();
        awaittestUtils.mock.unpatch(BasicModel);

        assert.verifySteps(['clear_cache']);//triggeredbythetestenvironmentondestroy
    });

    QUnit.test('creationinformviewona"noCache"model',asyncfunction(assert){
        assert.expect(5);

        awaittestUtils.mock.patch(BasicModel,{
            noCacheModels:BasicModel.prototype.noCacheModels.concat(['partner']),
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="display_name"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.step('create');
                }
                returnthis._super.apply(this,arguments);
            },
        });
        core.bus.on('clear_cache',form,assert.step.bind(assert,'clear_cache'));

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'value');
        awaittestUtils.form.clickSave(form);

        assert.verifySteps(['create','clear_cache']);

        form.destroy();
        awaittestUtils.mock.unpatch(BasicModel);

        assert.verifySteps(['clear_cache']);//triggeredbythetestenvironmentondestroy
    });

    QUnit.test('deletioninformviewona"noCache"model',asyncfunction(assert){
        assert.expect(5);

        awaittestUtils.mock.patch(BasicModel,{
            noCacheModels:BasicModel.prototype.noCacheModels.concat(['partner']),
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="display_name"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='unlink'){
                    assert.step('unlink');
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            viewOptions:{
                hasActionMenus:true,
            },
        });
        core.bus.on('clear_cache',form,assert.step.bind(assert,'clear_cache'));

        awaitcpHelpers.toggleActionMenu(form);
        awaitcpHelpers.toggleMenuItem(form,"Delete");
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        assert.verifySteps(['unlink','clear_cache']);

        form.destroy();
        awaittestUtils.mock.unpatch(BasicModel);

        assert.verifySteps(['clear_cache']);//triggeredbythetestenvironmentondestroy
    });

    QUnit.test('reloadcurrencieswhenwritingonrecordsofmodelres.currency',asyncfunction(assert){
        assert.expect(5);

        this.data['res.currency']={
            fields:{},
            records:[{id:1,display_name:"somecurrency"}],
        };

        varform=awaitcreateView({
            View:FormView,
            model:'res.currency',
            data:this.data,
            arch:'<form><fieldname="display_name"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
            session:{
                reloadCurrencies:function(){
                    assert.step('reloadcurrencies');
                },
            },
        });

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'newvalue');
        awaittestUtils.form.clickSave(form);

        assert.verifySteps([
            'read',
            'write',
            'reloadcurrencies',
            'read',
        ]);

        form.destroy();
    });

    QUnit.test('keepeditingaftercall_buttonfail',asyncfunction(assert){
        assert.expect(4);

        varvalues;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<buttonname="post"class="p"string="RaiseError"type="object"/>'+
                    '<fieldname="p">'+
                        '<treeeditable="top">'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="product_id"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            intercepts:{
                execute_action:function(ev){
                    assert.ok(true,'theactioniscorrectlyexecuted');
                    ev.data.on_fail();
                },
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1].p[0][2],values);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        //addarowandpartiallyfillit
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.editInput(form.$('input[name=display_name]'),'abc');

        //clickbuttonwhichwilltrigger_up'execute_action'(thiswillsave)
        values={
            display_name:'abc',
            product_id:false,
        };
        awaittestUtils.dom.click(form.$('button.p'));
        //editthenewrowagainandsetamany2onevalue
        awaittestUtils.dom.clickLast(form.$('.o_form_view.o_field_one2many.o_data_row.o_data_cell'));
        awaittestUtils.nextTick();
        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

        assert.strictEqual(form.$('.o_field_many2oneinput').val(),'xphone',
            "valueofthem2oshouldhavebeencorrectlyupdated");

        values={
            product_id:37,
        };
        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('asynchronousrenderingofawidgettag',asyncfunction(assert){
        assert.expect(1);

        vardef1=testUtils.makeTestPromise();

        varMyWidget=Widget.extend({
            willStart:function(){
                returndef1;
            },
        });

        widgetRegistry.add('test',MyWidget);

        createView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                        '<widgetname="test"/>'+
                    '</form>',
        }).then(function(form){
            assert.containsOnce(form,'div.o_widget',
                "thereshouldbeadivwithwidgetclass");
            form.destroy();
            deletewidgetRegistry.map.test;
        });

        def1.resolve();
        awaittestUtils.nextTick();
    });

    QUnit.test('nodeadlockwhensavingwithuncommittedchanges',asyncfunction(assert){
        //Beforesavingarecord,allfieldwidgetsareaskedtocommittheirchanges(newvalues
        //thattheywouldn'thavesenttothemodelyet).Thistestisaddedalongsideabugfix
        //ensuringthatwedon'tendupinadeadlockwhenawidgetactuallyhassomechangesto
        //commitatthatmoment.Bychance,thissituationisn'treachedwhentheuserclickson
        //'Save'(whichisthenaturalwaytosavearecord),becausebyclickingoutsidethe
        //widget,the'change'event(thisismainlyforInputFields)istriggered,andthewidget
        //notifiesthemodelofitsnewvalueonitsowninitiative,beforebeingrequestedto.
        //Inthistest,wetrytoreproducethedeadlocksituationbyforcingthefieldwidgetto
        //commitchangesbeforethesave.Wethusmanuallycall'saveRecord',insteadofclicking
        //on'Save'.
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="foo"/></form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
                //wesetafieldDebouncetopreciselymockthebehaviorofthewebclient:changesare
                //notsenttothemodelatkeystrokes,butwhentheinputisleft
            fieldDebounce:5000,
        });

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'somefoovalue');
        //manuallysavetherecord,topreventthefieldwidgettonotifythemodelofitsnew
        //valuebeforebeingrequestedto
        form.saveRecord();

        awaittestUtils.nextTick();

        assert.containsOnce(form,'.o_form_readonly',"formviewshouldbeinreadonly");
        assert.strictEqual(form.$('.o_form_view').text().trim(),'somefoovalue',
            "foofieldshouldhavecorrectvalue");
        assert.verifySteps(['onchange','create','read']);

        form.destroy();
    });

    QUnit.test('saverecordwithonchangeonone2manywithrequiredfield',asyncfunction(assert){
        //inthistest,wehaveaone2manywitharequiredfield,whosevalueis
        //setbyanonchangeonanotherfield;wemanuallysetthevalueofthat
        //firstfield,anddirectlyclickonSave(beforetheonchangeRPCreturns
        //andsetsthevalueoftherequiredfield)
        assert.expect(6);

        this.data.partner.fields.foo.default=undefined;
        this.data.partner.onchanges={
            display_name:function(obj){
                obj.foo=obj.display_name?'foovalue':undefined;
            },
        };

        varonchangeDef;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="p">'+
                        '<treeeditable="top">'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="foo"required="1"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    returnPromise.resolve(onchangeDef).then(_.constant(result));
                }
                if(args.method==='create'){
                    assert.step('create');
                    assert.strictEqual(args.args[0].p[0][2].foo,'foovalue',
                        "shouldhavewaitfortheonchangetoreturnbeforesaving");
                }
                returnresult;
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

        assert.strictEqual(form.$('.o_field_widget[name=display_name]').val(),'',
            "display_nameshouldbetheemptystringbydefault");
        assert.strictEqual(form.$('.o_field_widget[name=foo]').val(),'',
            "fooshouldbetheemptystringbydefault");

        onchangeDef=testUtils.makeTestPromise();//delaytheonchange

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'somevalue');

        awaittestUtils.form.clickSave(form);

        assert.step('resolve');
        onchangeDef.resolve();
        awaittestUtils.nextTick();

        assert.verifySteps(['resolve','create']);

        form.destroy();
    });

    QUnit.test('callcanBeRemovedwhilesaving',asyncfunction(assert){
        assert.expect(10);

        this.data.partner.onchanges={
            foo:function(obj){
                obj.display_name=obj.foo==='triggeronchange'?'changed':'default';
            },
        };

        varonchangeDef;
        varcreateDef=testUtils.makeTestPromise();
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="display_name"/><fieldname="foo"/></form>',
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    returnPromise.resolve(onchangeDef).then(_.constant(result));
                }
                if(args.method==='create'){
                    returnPromise.resolve(createDef).then(_.constant(result));
                }
                returnresult;
            },
        });

        //editfoototriggeradelayedonchange
        onchangeDef=testUtils.makeTestPromise();
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'triggeronchange');

        assert.strictEqual(form.$('.o_field_widget[name=display_name]').val(),'default');

        //save(willwaitfortheonchangetoreturn),andwillbedelayedaswell
        awaittestUtils.dom.click(form.$buttons.find('.o_form_button_save'));

        assert.hasClass(form.$('.o_form_view'),'o_form_editable');
        assert.strictEqual(form.$('.o_field_widget[name=display_name]').val(),'default');

        //simulateaclickonthebreadcrumbstoleavetheformview
        form.canBeRemoved();
        awaittestUtils.nextTick();

        assert.hasClass(form.$('.o_form_view'),'o_form_editable');
        assert.strictEqual(form.$('.o_field_widget[name=display_name]').val(),'default');

        //unlocktheonchange
        onchangeDef.resolve();
        awaittestUtils.nextTick();
        assert.hasClass(form.$('.o_form_view'),'o_form_editable');
        assert.strictEqual(form.$('.o_field_widget[name=display_name]').val(),'changed');

        //unlockthecreate
        createDef.resolve();
        awaittestUtils.nextTick();

        assert.hasClass(form.$('.o_form_view'),'o_form_readonly');
        assert.strictEqual(form.$('.o_field_widget[name=display_name]').text(),'changed');
        assert.containsNone(document.body,'.modal',
            "shouldnotdisplaythe'Changeswillbediscarded'dialog");

        form.destroy();
    });

    QUnit.test('callcanBeRemovedtwice',asyncfunction(assert){
        assert.expect(4);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="display_name"/><fieldname="foo"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsOnce(form,'.o_form_editable');
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'somevalue');

        form.canBeRemoved();
        awaittestUtils.nextTick();
        assert.containsOnce(document.body,'.modal');

        form.canBeRemoved();
        awaittestUtils.nextTick();
        assert.containsOnce(document.body,'.modal');

        awaittestUtils.dom.click($('.modal.modal-footer.btn-secondary'));

        assert.containsNone(document.body,'.modal');

        form.destroy();
    });

    QUnit.test('domainreturnedbyonchangeisclearedondiscard',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.onchanges={
            foo:function(){},
        };

        vardomain=['id','=',1];
        varexpectedDomain=domain;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="foo"/><fieldname="trululu"/></form>',
            mockRPC:function(route,args){
                if(args.method==='onchange'&&args.args[0][0]===1){
                    //onchangereturnsadomainonlyonrecord1
                    returnPromise.resolve({
                        domain:{
                            trululu:domain,
                        },
                    });
                }
                if(args.method==='name_search'){
                    assert.deepEqual(args.kwargs.args,expectedDomain);
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            viewOptions:{
                ids:[1,2],
                mode:'edit',
            },
        });

        assert.strictEqual(form.$('input[name=foo]').val(),'yop',"shouldbeonrecord1");

        //changefoototriggertheonchange
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'newvalue');

        //openmany2onedropdowntocheckifthedomainisapplied
        awaittestUtils.fields.many2one.clickOpenDropdown('trululu');

        //switchtoanotherrecord(shouldasktodiscardchanges,andresetthedomain)
        awaitcpHelpers.pagerNext(form);

        //discardchangesbyclickingonconfirminthedialog
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));

        assert.strictEqual(form.$('input[name=foo]').val(),'blip',"shouldbeonrecord2");

        //openmany2onedropdowntocheckifthedomainisapplied
        expectedDomain=[];
        awaittestUtils.fields.many2one.clickOpenDropdown('trululu');

        form.destroy();
    });

    QUnit.test('discardafterafailedsave',asyncfunction(assert){
        assert.expect(2);

        varactionManager=awaitcreateActionManager({
            data:this.data,
            archs:{
                'partner,false,form':'<form>'+
                                        '<fieldname="date"required="true"/>'+
                                        '<fieldname="foo"required="true"/>'+
                                    '</form>',
                'partner,false,kanban':'<kanban><templates><tt-name="kanban-box">'+
                                        '</t></templates></kanban>',
                'partner,false,search':'<search></search>',
            },
            actions:this.actions,
        });

        awaitactionManager.doAction(1);

        awaittestUtils.dom.click('.o_control_panel.o-kanban-button-new');

        //cannotsavebecausethereisarequiredfield
        awaittestUtils.dom.click('.o_control_panel.o_form_button_save');
        awaittestUtils.dom.click('.o_control_panel.o_form_button_cancel');

        assert.containsNone(actionManager,'.o_form_view');
        assert.containsOnce(actionManager,'.o_kanban_view');

        actionManager.destroy();
    });

    QUnit.test("one2manycreaterecorddialogshouldn'thavea'remove'button",asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="p">'+
                        '<kanban>'+
                            '<templates>'+
                                '<tt-name="kanban-box">'+
                                    '<fieldname="foo"/>'+
                                '</t>'+
                            '</templates>'+
                        '</kanban>'+
                        '<form>'+
                            '<fieldname="foo"/>'+
                        '</form>'+
                    '</field>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickCreate(form);
        awaittestUtils.dom.click(form.$('.o-kanban-button-new'));

        assert.containsOnce(document.body,'.modal');
        assert.strictEqual($('.modal.modal-footer.o_btn_remove').length,0,
            "shouldn'thavea'remove'buttononnewrecords");

        form.destroy();
    });

    QUnit.test('editarecordinreadonlyandswitchtoeditbeforeitisactuallysaved',asyncfunction(assert){
        assert.expect(3);

        constprom=testUtils.makeTestPromise();
        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form>
                    <fieldname="foo"/>
                    <fieldname="bar"widget="toggle_button"/>
                </form>`,
            mockRPC:function(route,args){
                constresult=this._super.apply(this,arguments);
                if(args.method==='write'){//delaythewriteRPC
                    assert.deepEqual(args.args[1],{bar:false});
                    returnprom.then(_.constant(result));
                }
                returnresult;
            },
            res_id:1,
        });

        //edittherecord(inreadonly)withtoogle_buttonwidget(anddelaythewriteRPC)
        awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]'));

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);

        assert.hasClass(form.$('.o_form_view'),'o_form_readonly');//shouldwaitfortheRPCtoreturn

        //makewriteRPCreturn
        prom.resolve();
        awaittestUtils.nextTick();

        assert.hasClass(form.$('.o_form_view'),'o_form_editable');

        form.destroy();
    });

    QUnit.test('"bare"buttonsintemplateshouldnottriggerbuttonclick',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<buttonstring="Save"class="btn-primary"special="save"/>'+
                '<buttonclass="mybutton">westvleteren</button>'+
              '</form>',
            res_id:2,
            intercepts:{
                execute_action:function(){
                    assert.step('execute_action');
                },
            },
        });
        awaittestUtils.dom.click(form.$('.o_form_viewbutton.btn-primary'));
        assert.verifySteps(['execute_action']);
        awaittestUtils.dom.click(form.$('.o_form_viewbutton.mybutton'));
        assert.verifySteps([]);
        form.destroy();
    });

    QUnit.test('formviewwithinlinetreeviewwithoptionalfieldsandlocalstoragemock',asyncfunction(assert){
        assert.expect(12);

        varStorage=RamStorage.extend({
            getItem:function(key){
                assert.step('getItem'+key);
                returnthis._super.apply(this,arguments);
            },
            setItem:function(key,value){
                assert.step('setItem'+key+'to'+value);
                returnthis._super.apply(this,arguments);
            },
        });

        varRamStorageService=AbstractStorageService.extend({
            storage:newStorage(),
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="qux"/>'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="bar"optional="hide"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            services:{
                local_storage:RamStorageService,
            },
            view_id:27,
        });

        varlocalStorageKey='optional_fields,partner,form,27,p,list,undefined,bar,foo';

        assert.verifySteps(['getItem'+localStorageKey]);

        assert.containsN(form,'th',2,
            "shouldhave2th,1forselector,1forfoocolumn");

        assert.ok(form.$('th:contains(Foo)').is(':visible'),
            "shouldhaveavisiblefoofield");

        assert.notOk(form.$('th:contains(Bar)').is(':visible'),
            "shouldnothaveavisiblebarfield");

        //optionalfields
        awaittestUtils.dom.click(form.$('table.o_optional_columns_dropdown_toggle'));
        assert.containsN(form,'div.o_optional_columnsdiv.dropdown-item',1,
            "dropdownhave1optionalfield");

        //enableoptionalfield
        awaittestUtils.dom.click(form.$('div.o_optional_columnsdiv.dropdown-iteminput'));

        assert.verifySteps([
            'setItem'+localStorageKey+'to["bar"]',
            'getItem'+localStorageKey,
        ]);

        assert.containsN(form,'th',3,
            "shouldhave3th,1forselector,2forcolumns");

        assert.ok(form.$('th:contains(Foo)').is(':visible'),
            "shouldhaveavisiblefoofield");

        assert.ok(form.$('th:contains(Bar)').is(':visible'),
            "shouldhaveavisiblebarfield");

        form.destroy();
    });

    QUnit.test('formviewwithtree_view_refwithoptionalfieldsandlocalstoragemock',asyncfunction(assert){
        assert.expect(12);

        varStorage=RamStorage.extend({
            getItem:function(key){
                assert.step('getItem'+key);
                returnthis._super.apply(this,arguments);
            },
            setItem:function(key,value){
                assert.step('setItem'+key+'to'+value);
                returnthis._super.apply(this,arguments);
            },
        });

        varRamStorageService=AbstractStorageService.extend({
            storage:newStorage(),
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="qux"/>'+
                    '<fieldname="p"context="{\'tree_view_ref\':\'34\'}"/>'+
                '</form>',
            archs:{
                "partner,nope_not_this_one,list":'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '</tree>',
                "partner,34,list":'<tree>'+
                        '<fieldname="foo"optional="hide"/>'+
                        '<fieldname="bar"/>'+
                    '</tree>',
            },
            services:{
                local_storage:RamStorageService,
            },
            view_id:27,
        });

        varlocalStorageKey='optional_fields,partner,form,27,p,list,34,bar,foo';

        assert.verifySteps(['getItem'+localStorageKey]);

        assert.containsN(form,'th',2,
            "shouldhave2th,1forselector,1forfoocolumn");

        assert.notOk(form.$('th:contains(Foo)').is(':visible'),
            "shouldhaveavisiblefoofield");

        assert.ok(form.$('th:contains(Bar)').is(':visible'),
            "shouldnothaveavisiblebarfield");

        //optionalfields
        awaittestUtils.dom.click(form.$('table.o_optional_columns_dropdown_toggle'));
        assert.containsN(form,'div.o_optional_columnsdiv.dropdown-item',1,
            "dropdownhave1optionalfield");

        //enableoptionalfield
        awaittestUtils.dom.click(form.$('div.o_optional_columnsdiv.dropdown-iteminput'));

        assert.verifySteps([
            'setItem'+localStorageKey+'to["foo"]',
            'getItem'+localStorageKey,
        ]);

        assert.containsN(form,'th',3,
            "shouldhave3th,1forselector,2forcolumns");

        assert.ok(form.$('th:contains(Foo)').is(':visible'),
            "shouldhaveavisiblefoofield");

        assert.ok(form.$('th:contains(Bar)').is(':visible'),
            "shouldhaveavisiblebarfield");

        form.destroy();
    });

    QUnit.test('usingtabinanemptyrequiredstringfieldshouldnotmovetothenextfield',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="display_name"required="1"/>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });

        awaittestUtils.dom.click(form.$('input[name=display_name]'));
        assert.strictEqual(form.$('input[name="display_name"]')[0],document.activeElement,
            "display_nameshouldbefocused");
        form.$('input[name="display_name"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$('input[name="display_name"]')[0],document.activeElement,
            "display_nameshouldstillbefocusedbecauseitisemptyandrequired");
        assert.hasClass(form.$('input[name="display_name"]'),'o_field_invalid',
            "display_nameshouldhavetheo_field_invalidclass");
        form.destroy();
    });

    QUnit.test('usingtabinanemptyrequireddatefieldshouldnotmovetothenextfield',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="date"required="1"/>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });

        awaittestUtils.dom.click(form.$('input[name=date]'));
        assert.strictEqual(form.$('input[name="date"]')[0],document.activeElement,
            "display_nameshouldbefocused");
        form.$('input[name="date"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$('input[name="date"]')[0],document.activeElement,
            "dateshouldstillbefocusedbecauseitisemptyandrequired");

        form.destroy();
    });

    QUnit.test('EditbuttongetthefocuswhenpressingTABfromform',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<divclass="oe_title">'+
                        '<fieldname="display_name"/>'+
                    '</div>'+
                '</form>',
            res_id:1,
        });

        //inedit
        awaittestUtils.form.clickEdit(form);
        form.$('input[name="display_name"]').focus().trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$buttons.find('.btn-primary:visible')[0],document.activeElement,
            "thefirstprimarybutton(save)shouldbefocused");
        form.destroy();
    });

    QUnit.test('InEditionmode,afternavigatingtothelastfield,thedefaultbuttonwhenpressingTABisSAVE',asyncfunction(assert){
        assert.expect(1);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="state"invisible="1"/>'+
                    '<header>'+
                        '<buttonname="post"class="btn-primaryfirstButton"string="Confirm"type="object"/>'+
                        '<buttonname="post"class="btn-primarysecondButton"string="Confirm2"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<divclass="oe_title">'+
                                '<fieldname="display_name"/>'+
                            '</div>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            viewOptions:{
                mode:'edit',
            },
        });

        form.$('input[name="display_name"]').focus().trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$buttons.find('.o_form_button_save:visible')[0],document.activeElement,
            "thesaveshouldbefocused");
        form.destroy();
    });

    QUnit.test('InREADmode,thedefaultbuttonwithfocusisthefirstprimarybuttonoftheform',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="state"invisible="1"/>'+
                    '<header>'+
                        '<buttonname="post"class="btn-primaryfirstButton"string="Confirm"type="object"/>'+
                        '<buttonname="post"class="btn-primarysecondButton"string="Confirm2"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<divclass="oe_title">'+
                                '<fieldname="display_name"/>'+
                            '</div>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });
        assert.strictEqual(form.$('button.firstButton')[0],document.activeElement,
                        "bydefaultthefocusineditmodeshouldgotothefirstprimarybuttonoftheform(notedit)");
        form.destroy();
    });

    QUnit.test('InREADmode,thedefaultbuttonwhenpressingTABisEDITwhenthereisnoprimarybuttonontheform',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="state"invisible="1"/>'+
                    '<header>'+
                        '<buttonname="post"class="not-primary"string="Confirm"type="object"/>'+
                        '<buttonname="post"class="not-primary"string="Confirm2"type="object"/>'+
                    '</header>'+
                    '<sheet>'+
                        '<group>'+
                            '<divclass="oe_title">'+
                                '<fieldname="display_name"/>'+
                            '</div>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });
        assert.strictEqual(form.$buttons.find('.o_form_button_edit')[0],document.activeElement,
                        "inreadmode,whentherearenoprimarybuttonsontheform,thedefaultbuttonwiththefocusshouldbeedit");
        form.destroy();
    });

    QUnit.test('InEditionmode,whenanattributeisdynamicallyrequired(andnotrequired),TABshouldnavigatetothenextfield',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"attrs="{\'required\':[[\'bar\',\'=\',True]]}"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:5,
            viewOptions:{
                mode:'edit',
            },
        });

        form.$('input[name="foo"]').focus();
        $(document.activeElement).trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));

        assert.strictEqual(form.$('div[name="bar"]>input')[0],document.activeElement,"fooisnotrequired,sohittingTABonfooshouldhavemovedthefocustoBAR");
        form.destroy();
    });

    QUnit.test('InEditionmode,whenanattributeisdynamicallyrequired,TABshouldstoponthefieldifitisrequired',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"attrs="{\'required\':[[\'bar\',\'=\',True]]}"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:5,
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.dom.click(form.$('div[name="bar"]>input'));
        form.$('input[name="foo"]').focus();
        $(document.activeElement).trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));

        assert.strictEqual(form.$('input[name="foo"]')[0],document.activeElement,"fooisrequired,sohittingTABonfooshouldkeepthefocusonfoo");
        form.destroy();
    });

    QUnit.test('displaytooltipsforsaveanddiscardbuttons',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
        });

        form.$buttons.find('.o_form_buttons_edit').tooltip('show',false);
        assert.strictEqual($('.tooltip.oe_tooltip_string').length,1,
            "shouldhaverenderedatooltip");
            awaittestUtils.nextTick();
        form.destroy();
    });
    QUnit.test('ifthefocusisonthesavebutton,hittingENTERshouldsave',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.ok(true,"shouldcallthe/createroute");
                }
                returnthis._super(route,args);
            },
        });

        form.$buttons.find('.o_form_button_save')
                        .focus()
                        .trigger($.Event('keydown',{which:$.ui.keyCode.ENTER}));
        awaittestUtils.nextTick();
        form.destroy();
    });
    QUnit.test('ifthefocusisonthediscardbutton,hittingENTERshouldsave',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.ok(true,"shouldcallthe/createroute");
                }
                returnthis._super(route,args);
            },
        });

        form.$buttons.find('.o_form_button_cancel')
                        .focus()
                        .trigger($.Event('keydown',{which:$.ui.keyCode.ENTER}));
        awaittestUtils.nextTick();
        form.destroy();
    });
    QUnit.test('ifthefocusisonthesavebutton,hittingESCAPEshoulddiscard',asyncfunction(assert){
        assert.expect(0);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    thrownewError('Createshouldnotbecalled');
                }
                returnthis._super(route,args);
            },
        });

        form.$buttons.find('.o_form_button_save')
                        .focus()
                        .trigger($.Event('keydown',{which:$.ui.keyCode.ESCAPE}));
        awaittestUtils.nextTick();
        form.destroy();
    });

    QUnit.test('resequencelistlineswhendiscardablelinesarepresent',asyncfunction(assert){
        assert.expect(8);

        varonchangeNum=0;

        this.data.partner.onchanges={
            p:function(obj){
                onchangeNum++;
                obj.foo=obj.p?obj.p.length.toString():"0";
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="p"/>'+
                '</form>',
            archs:{
                'partner,false,list':
                    '<treeeditable="bottom">'+
                        '<fieldname="int_field"widget="handle"/>'+
                        '<fieldname="display_name"required="1"/>'+
                    '</tree>',
            },
        });

        assert.strictEqual(onchangeNum,1,"oneonchangehappenswhenformisopened");
        assert.strictEqual(form.$('[name="foo"]').val(),"0","onchangeworkedthereis0line");

        //Addoneline
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        form.$('.o_field_one2manyinput:first').focus();
        awaittestUtils.nextTick();
        form.$('.o_field_one2manyinput:first').val('firstline').trigger('input');
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(form.$('input[name="foo"]'));
        assert.strictEqual(onchangeNum,2,"oneonchangehappenswhenalineisadded");
        assert.strictEqual(form.$('[name="foo"]').val(),"1","onchangeworkedthereis1line");

        //Draganddropsecondlinebeforefirstone(with1draftandinvalidline)
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.dom.dragAndDrop(
            form.$('.ui-sortable-handle').eq(0),
            form.$('.o_data_row').last(),
            {position:'bottom'}
        );
        assert.strictEqual(onchangeNum,3,"oneonchangehappenswhenlinesareresequenced");
        assert.strictEqual(form.$('[name="foo"]').val(),"1","onchangeworkedthereis1line");

        //Addasecondline
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        form.$('.o_field_one2manyinput:first').focus();
        awaittestUtils.nextTick();
        form.$('.o_field_one2manyinput:first').val('secondline').trigger('input');
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(form.$('input[name="foo"]'));
        assert.strictEqual(onchangeNum,4,"oneonchangehappenswhenalineisadded");
        assert.strictEqual(form.$('[name="foo"]').val(),"2","onchangeworkedthereis2lines");

        form.destroy();
    });

    QUnit.test('ifthefocusisonthediscardbutton,hittingESCAPEshoulddiscard',asyncfunction(assert){
        assert.expect(0);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    thrownewError('Createshouldnotbecalled');
                }
                returnthis._super(route,args);
            },
        });

        form.$buttons.find('.o_form_button_cancel')
                        .focus()
                        .trigger($.Event('keydown',{which:$.ui.keyCode.ESCAPE}));
        awaittestUtils.nextTick();
        form.destroy();
    });

    QUnit.test('ifthefocusisonthesavebutton,hittingTABshouldnotmovetothenextbutton',asyncfunction(assert){
        assert.expect(1);
        /*
        thistesthasonlyonepurpose:tosaythatitisnormalthatthefocusstayswithinabuttonprimaryevenaftertheTABkeyhasbeenpressed.
        ItisnotpossibleheretoexecutethedefaultactionoftheTABonabutton:https://stackoverflow.com/questions/32428993/why-doesnt-simulating-a-tab-keypress-move-focus-to-the-next-input-field
        sowritingatestthatwillalwayssucceedisnotuseful.
            */
        assert.ok("Behaviorcan'tbetested");
    });

    QUnit.test('reloadcompanywhencreatingrecordsofmodelres.company',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'res.company',
            data:this.data,
            arch:'<form><fieldname="name"/></form>',
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                do_action:function(ev){
                    assert.step('reloadcompany');
                    assert.strictEqual(ev.data.action,"reload_context","companyviewreloaded");
                },
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name="name"]'),'TestCompany');
        awaittestUtils.form.clickSave(form);

        assert.verifySteps([
            'onchange',
            'create',
            'reloadcompany',
            'read',
        ]);

        form.destroy();
    });

    QUnit.test('reloadcompanywhenwritingonrecordsofmodelres.company',asyncfunction(assert){
        assert.expect(6);
        this.data['res.company'].records=[{
            id:1,name:"TestCompany"
        }];

        varform=awaitcreateView({
            View:FormView,
            model:'res.company',
            data:this.data,
            arch:'<form><fieldname="name"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                do_action:function(ev){
                    assert.step('reloadcompany');
                    assert.strictEqual(ev.data.action,"reload_context","companyviewreloaded");
                },
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name="name"]'),'TestCompany2');
        awaittestUtils.form.clickSave(form);

        assert.verifySteps([
            'read',
            'write',
            'reloadcompany',
            'read',
        ]);

        form.destroy();
    });

    QUnit.test('company_dependentfieldinformview,inmulticompanygroup',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.product_id.company_dependent=true;
        this.data.partner.fields.product_id.help='thisisatooltip';
        this.data.partner.fields.foo.company_dependent=true;

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="foo"/>
                        <fieldname="product_id"/>
                    </group>
                </form>`,
            session:{
                display_switch_company_menu:true,
            },
        });

        const$productLabel=form.$('.o_form_label:eq(1)');
        $productLabel.tooltip('show',false);
        $productLabel.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),
            "thisisatooltip\n\nValuessetherearecompany-specific.");
        $productLabel.trigger($.Event('mouseleave'));

        const$fooLabel=form.$('.o_form_label:first');
        $fooLabel.tooltip('show',false);
        $fooLabel.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),
            "Valuessetherearecompany-specific.");
        $fooLabel.trigger($.Event('mouseleave'));

        form.destroy();
    });

    QUnit.test('company_dependentfieldinformview,notinmulticompanygroup',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.product_id.company_dependent=true;
        this.data.partner.fields.product_id.help='thisisatooltip';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="product_id"/>
                    </group>
                </form>`,
            session:{
                display_switch_company_menu:false,
            },
        });

        const$productLabel=form.$('.o_form_label');

        $productLabel.tooltip('show',false);
        $productLabel.trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_help').text().trim(),"thisisatooltip");
        $productLabel.trigger($.Event('mouseleave'));

        form.destroy();
    });

    QUnit.test('reloadaformviewwithapiechartdoesnotcrash',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form>
                      <widgetname="pie_chart"title="quxbyproduct"attrs="{'measure\':'qux','groupby':'product_id'}"/>
                  </form>`,
        });

        assert.containsOnce(form,'.o_widget');
        constcanvasId1=form.el.querySelector('.o_widgetcanvas').id;

        awaitform.reload();
        awaittestUtils.nextTick();

        assert.containsOnce(form,'.o_widget');
        constcanvasId2=form.el.querySelector('.o_widgetcanvas').id;
        //Anewcanvasshouldbefoundinthedom
        assert.notStrictEqual(canvasId1,canvasId2);

        form.destroy();
        deletewidgetRegistry.map.test;
    });

    QUnit.test('donotcallmountedtwiceonchildren',asyncfunction(assert){
        assert.expect(3);

        classCustomFieldComponentextendsfieldRegistryOwl.get('boolean'){
            mounted(){
                super.mounted(...arguments);
                assert.step('mounted');
            }
            willUnmount(){
                super.willUnmount(...arguments);
                assert.step('willUnmount');
            }
        }
        fieldRegistryOwl.add('custom',CustomFieldComponent);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form><fieldname="bar"widget="custom"/></form>`,
        });

        form.destroy();
        deletefieldRegistryOwl.map.custom;

        assert.verifySteps(['mounted','willUnmount']);
    });

    QUnit.test("attachcallbackswithlongprocessingin__renderView",asyncfunction(assert){
        /**
         *Themainusecaseofthistestisdiscuss,inwhichtheFormRenderer
         *__renderViewmethodisoverriddentoperformasynchronoustasks(the
         *updateofthechatterComponent)resultinginadelaybetweenthe
         *appendingofthenewformcontentintoitselementandthe
         *"on_attach_callback"calls.Thisisthepurposeof"__renderView"
         *whichismeanttodoalltheasyncworkbeforethecontentisappended.
         */
        assert.expect(11);

        lettestPromise=Promise.resolve();

        constRenderer=FormRenderer.extend({
            on_attach_callback(){
                assert.step("form.on_attach_callback");
                this._super(...arguments);
            },
            async__renderView(){
                const_super=this._super.bind(this);
                awaittestPromise;
                return_super();
            },
        });

        //Setupcustomfieldwidget
        fieldRegistry.add("customwidget",AbstractField.extend({
            className:"custom-widget",
            on_attach_callback(){
                assert.step("widget.on_attach_callback");
            },
        }));

        constform=awaitcreateView({
            arch:`<form><fieldname="bar"widget="customwidget"/></form>`,
            data:this.data,
            model:'partner',
            res_id:1,
            View:FormView.extend({
                config:Object.assign({},FormView.prototype.config,{Renderer}),
            }),
        });

        assert.containsOnce(form,".custom-widget");
        assert.verifySteps([
            "form.on_attach_callback",//Formattached
            "widget.on_attach_callback",//Initialwidgetattached
        ]);

        constinitialWidget=form.$(".custom-widget")[0];
        testPromise=testUtils.makeTestPromise();

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,".custom-widget");
        assert.strictEqual(initialWidget,form.$(".custom-widget")[0],"Widgetshaveyettobereplaced");
        assert.verifySteps([]);

        testPromise.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(form,".custom-widget");
        assert.notStrictEqual(initialWidget,form.$(".custom-widget")[0],"Widgetshavebeenreplaced");
        assert.verifySteps([
            "widget.on_attach_callback",//Newwidgetattached
        ]);

        form.destroy();

        deletefieldRegistry.map.customwidget;
    });

    QUnit.test('field"length"withvalue0:canapplyonchange',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.length={string:'Length',type:'float',default:0};
        this.data.partner.fields.foo.default="foodefault";

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="foo"/><fieldname="length"/></form>',
        });

        assert.strictEqual(form.$('input[name=foo]').val(),"foodefault",
                        "shouldcontaininputwithinitialvalue");

        form.destroy();
    });

    QUnit.test('field"length"withvalue0:readonlyfieldsarenotsentwhensaving',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.fields.length={string:'Length',type:'float',default:0};
        this.data.partner.fields.foo.default="foodefault";

        //defineanonchangeondisplay_nametocheckthatthevalueofreadonly
        //fieldsiscorrectlysentforonchanges
        this.data.partner.onchanges={
            display_name:function(){},
            p:function(){},
        };

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                    <fieldname="p">
                        <tree>
                            <fieldname="display_name"/>
                        </tree>
                        <formstring="Partners">
                            <fieldname="length"/>
                            <fieldname="display_name"/>
                            <fieldname="foo"attrs="{\'readonly\':[[\'display_name\',\'=\',\'readonly\']]}"/>
                        </form>
                    </field>
                </form>`,
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{
                        p:[[0,args.args[0].p[0][1],{length:0,display_name:'readonly'}]]
                    },"shouldnothavesentthevalueofthereadonlyfield");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.containsOnce(document.body,'.modalinput.o_field_widget[name=foo]',
            'fooshouldbeeditable');
        awaittestUtils.fields.editInput($('.modal.o_field_widget[name=foo]'),'foovalue');
        awaittestUtils.fields.editInput($('.modal.o_field_widget[name=display_name]'),'readonly');
        assert.containsOnce(document.body,'.modalspan.o_field_widget[name=foo]',
            'fooshouldbereadonly');
        awaittestUtils.dom.clickFirst($('.modal-footer.btn-primary'));

        awaittestUtils.form.clickSave(form);//savetherecord
        form.destroy();
    });

});

});
